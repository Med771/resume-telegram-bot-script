from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from addons.lexicon import OffersLexicon, ErrorLexicon
from addons.decorator import TelegramDecorator
from addons.markup import OffersMarkup
from addons.state.offer import OfferState

from module.chat.serv import ChatService

from tools.admin import AdminTools
from tools.web import WebTools

from config import TelegramConfig

bot = TelegramConfig.BOT


class OffersService:
    SUCCESS_INTERMEDIATE_STATUSES = {"STUDENT_CONFIRMED", "RECRUITER_CONFIRMED"}
    STUDENT_RESUME_URL_TEMPLATE = "https://singularity-resume.ru/studentsResume/{student_id}"

    @staticmethod
    def _result(offer: dict) -> str:
        return offer.get("result", "") or offer.get("resultEnum", "")

    @staticmethod
    def _company_name(offer: dict) -> str:
        recruiter_res = offer.get("recruiterRes") or {}
        return (
            recruiter_res.get("companyName", "")
            or offer.get("companyName", "")
            or offer.get("recruiterCompanyName", "")
        )

    @staticmethod
    def _recruiter_name(offer: dict) -> str:
        recruiter_res = offer.get("recruiterRes") or {}
        return (
            recruiter_res.get("fullName", "")
            or offer.get("recruiterName", "")
            or "Работодатель"
        )

    @staticmethod
    def _speciality(offer: dict) -> str:
        student_res = offer.get("studentRes") or {}
        return (
            student_res.get("speciality", "")
            or offer.get("studentSpeciality", "")
            or "Не указано"
        )

    @staticmethod
    def _recruiter_chat_id(offer: dict) -> str:
        recruiter_res = offer.get("recruiterRes") or {}
        chat_id = (
            recruiter_res.get("chatId", "")
            or offer.get("recruiterTelegramUserId", "")
        )
        return str(chat_id).strip()

    @staticmethod
    def _student_chat_id(offer: dict) -> str:
        student_res = offer.get("studentRes") or {}
        chat_id = (
            student_res.get("chatId", "")
            or offer.get("studentTelegramUserId", "")
        )
        return str(chat_id).strip()

    @staticmethod
    def _student_full_name(offer: dict) -> str:
        student_res = offer.get("studentRes") or {}
        return (
            student_res.get("fullName", "")
            or offer.get("studentFullName", "")
            or "Студент"
        )

    @staticmethod
    def _chat_url(offer: dict) -> str:
        return offer.get("chatUrl", "") or offer.get("chat_url", "")

    @classmethod
    def _student_resume_link(cls, student_id: str) -> str:
        return cls.STUDENT_RESUME_URL_TEMPLATE.format(student_id=student_id)

    @classmethod
    def _format_similar_students_links(cls, students: list[dict]) -> str:
        lines: list[str] = []
        for student in students:
            student_id = str(student.get("id", "")).strip()
            if not student_id:
                continue
            full_name = (
                f"{str(student.get('firstName', '')).strip()} {str(student.get('lastName', '')).strip()}".strip()
                or "Студент"
            )
            lines.append(f"• {full_name}: {cls._student_resume_link(student_id=student_id)}")
        return "\n".join(lines)

    @classmethod
    def _next_success_status(cls, current_result: str, is_student_actor: bool) -> str:
        if is_student_actor:
            if current_result == "RECRUITER_CONFIRMED":
                return "SUCCESS"
            return "STUDENT_CONFIRMED"
        if current_result == "STUDENT_CONFIRMED":
            return "SUCCESS"
        return "RECRUITER_CONFIRMED"

    @classmethod
    def _already_confirmed_by_actor(cls, current_result: str, is_student_actor: bool) -> bool:
        return (is_student_actor and current_result == "STUDENT_CONFIRMED") or (
            (not is_student_actor) and current_result == "RECRUITER_CONFIRMED"
        )

    @classmethod
    async def _ack_callback(cls, callback: CallbackQuery) -> None:
        try:
            await callback.answer()
        except Exception:
            pass

    @classmethod
    def _offer_id_from_callback(cls, callback: CallbackQuery) -> int | None:
        try:
            return int((callback.data or "").rsplit("_", 1)[-1])
        except (TypeError, ValueError):
            return None

    @classmethod
    async def _load_offer_with_entities(cls, offer_id: int) -> dict:
        offer = await WebTools.get_offer(_id=offer_id)
        enriched_offer = await WebTools.enrich_offer(offer=offer)
        return enriched_offer if enriched_offer else offer

    @classmethod
    def _wait_other_side_msg(cls, is_stud: bool) -> str:
        return (
            OffersLexicon.OFFER_SUCCESS_WAIT_OTHER_SIDE_MSG
            if is_stud
            else OffersLexicon.OFFER_SUCCESS_WAIT_OTHER_SIDE_RECRUITER_MSG
        )

    @classmethod
    async def _ensure_student_actor(cls, callback: CallbackQuery, state: FSMContext) -> bool:
        chat_id = str(callback.message.chat.id)
        is_stud = await cls._is_student_user(state=state, chat_id=chat_id)
        if is_stud:
            return True
        await callback.message.answer(
            text=OffersLexicon.OFFER_RECRUITER_READONLY_MSG,
            reply_markup=OffersMarkup.back_markup
        )
        return False

    @classmethod
    async def _request_reject_reason(cls, callback: CallbackQuery, state: FSMContext, offer_id: int) -> None:
        await callback.message.answer(
            text=OffersLexicon.OFFER_REJECT_REASON_MSG,
            reply_markup=OffersMarkup.back_markup
        )
        await state.set_state(OfferState.REJECT_OFFER_REASON_STATE)
        await state.update_data(id=offer_id)

    @classmethod
    async def _is_student_user(cls, state: FSMContext, chat_id: str) -> bool:
        state_data = await state.get_data()
        if state_data.get("u") == 1:
            return True
        if state_data.get("u") == 2:
            return False

        sync_payload = await WebTools.get_sync(user_id=chat_id)
        return sync_payload.get("type") == "st" if sync_payload else True

    @classmethod
    @TelegramDecorator.log_call()
    async def offers_btn(cls, callback: CallbackQuery, state: FSMContext):
        await cls._ack_callback(callback=callback)
        await AdminTools.delete_msg(message=callback.message)

        chat_id = str(callback.message.chat.id)
        is_stud = await cls._is_student_user(state=state, chat_id=chat_id)
        data = await WebTools.get_offers_by_id(is_stud=is_stud, chat_id=chat_id)

        offers = []

        for offer in data.get("offers", []):
            offer_id = offer.get("id")
            if offer_id is None:
                continue

            detailed_offer = await WebTools.enrich_offer(offer=offer)
            if not detailed_offer:
                detailed_offer = offer

            if is_stud:
                title = cls._company_name(offer=detailed_offer) or "Компания не указана"
            else:
                title = cls._student_full_name(offer=detailed_offer)

            offers.append((offer_id, title))

        await callback.message.answer(
            text=OffersLexicon.OFFERS_MSG if is_stud else OffersLexicon.OFFERS_RECRUITER_MSG,
            reply_markup=OffersMarkup.markup_offers(offers=offers)
        )

    @classmethod
    @TelegramDecorator.log_call()
    async def offer_btn(cls, callback: CallbackQuery, state: FSMContext):
        await cls._ack_callback(callback=callback)
        await AdminTools.delete_msg(message=callback.message)

        _id = cls._offer_id_from_callback(callback=callback)
        if _id is None:
            await callback.message.answer(
                text=ErrorLexicon.ERROR_RETURN_MENU_MSG,
                reply_markup=OffersMarkup.back_markup
            )
            return
        chat_id = str(callback.message.chat.id)
        is_stud = await cls._is_student_user(state=state, chat_id=chat_id)

        offer = await cls._load_offer_with_entities(offer_id=_id)

        company_name = cls._company_name(offer=offer)
        recruiter_name = cls._recruiter_name(offer=offer)
        speciality = cls._speciality(offer=offer)
        result = cls._result(offer=offer)

        if is_stud:
            if result == "WAITING":
                await callback.message.answer(
                    text=OffersLexicon.OFFER_TO_STUDENT_MSG.format(
                        company_name=company_name,
                        recruiter_name=recruiter_name,
                        speciality=speciality
                    ),
                    reply_markup=OffersMarkup.new_offer(_id=_id, can_reject=True)
                )
                return
            if result in {"EXPECTATION", "RECRUITER_CONFIRMED"}:
                await callback.message.answer(
                    text=(
                        OffersLexicon.OFFER_CHAT_ACTIVE_MSG.format(
                            company_name=company_name,
                            recruiter_name=recruiter_name,
                            speciality=speciality
                        )
                        if result == "EXPECTATION"
                        else OffersLexicon.OFFER_SUCCESS_OTHER_SIDE_CONFIRMED_MSG
                    ),
                    reply_markup=OffersMarkup.active_offer(_id=_id, can_reject=True)
                )
                return
            if result == "STUDENT_CONFIRMED":
                await callback.message.answer(
                    text=OffersLexicon.OFFER_SUCCESS_WAIT_OTHER_SIDE_MSG,
                    reply_markup=OffersMarkup.back_markup
                )
                return
        else:
            student_full_name = cls._student_full_name(offer=offer)
            if result == "WAITING":
                await callback.message.answer(
                    text=OffersLexicon.OFFER_TO_RECRUITER_WAITING_MSG.format(
                        student_full_name=student_full_name,
                        student_speciality=speciality,
                        company_name=company_name,
                    ),
                    reply_markup=OffersMarkup.back_markup
                )
                return
            if result in {"EXPECTATION", "STUDENT_CONFIRMED"}:
                await callback.message.answer(
                    text=(
                        OffersLexicon.OFFER_TO_RECRUITER_ACTIVE_MSG.format(
                            student_full_name=student_full_name,
                            student_speciality=speciality,
                            company_name=company_name
                        )
                        if result == "EXPECTATION"
                        else OffersLexicon.OFFER_SUCCESS_OTHER_SIDE_CONFIRMED_RECRUITER_MSG
                    ),
                    reply_markup=OffersMarkup.active_offer(_id=_id, can_reject=False)
                )
                return
            if result == "RECRUITER_CONFIRMED":
                await callback.message.answer(
                    text=OffersLexicon.OFFER_SUCCESS_WAIT_OTHER_SIDE_RECRUITER_MSG,
                    reply_markup=OffersMarkup.back_markup
                )
                return

        if result == "SUCCESS":
            student_full_name = cls._student_full_name(offer=offer)
            await callback.message.answer(
                text=OffersLexicon.OFFER_SUCCESS_RECRUITER_CONFIRM_MSG.format(
                        student_full_name=student_full_name,
                        student_speciality=speciality,
                        company_name=company_name
                    ),
                reply_markup=OffersMarkup.back_markup
            )
            return

        await callback.message.answer(
            text=ErrorLexicon.ERROR_RETURN_MENU_MSG,
            reply_markup=OffersMarkup.back_markup
        )

    @classmethod
    @TelegramDecorator.log_call()
    async def yes_new_offer_btn(cls, callback: CallbackQuery, state: FSMContext):
        await cls._ack_callback(callback=callback)
        if not await cls._ensure_student_actor(callback=callback, state=state):
            return

        await AdminTools.edit_reply(message=callback.message)

        _id = cls._offer_id_from_callback(callback=callback)
        if _id is None:
            await callback.message.answer(
                text=ErrorLexicon.ERROR_RETURN_MENU_MSG,
                reply_markup=OffersMarkup.back_markup
            )
            return

        _res = await ChatService.create_offer_chat(offer_id=_id)

        if not _res:
            await callback.message.answer(
                text=ErrorLexicon.CHAT_CREATE_ERROR_MSG,
                reply_markup=OffersMarkup.back_markup
            )

            return

        offer = _res if isinstance(_res, dict) else {}
        offer_chat_id = str(offer.get("chatId", "")).strip()

        await WebTools.set_status(
            _id=_id,
            status="EXPECTATION",
            has_recruiter_message=False,
            has_student_message=False,
            chat_id=offer_chat_id
        )

        company_name = cls._company_name(offer=offer)
        recruiter_name = cls._recruiter_name(offer=offer)
        recruiter_chat_id = cls._recruiter_chat_id(offer=offer)

        student_full_name = cls._student_full_name(offer=offer)
        student_speciality = cls._speciality(offer=offer)

        url = cls._chat_url(offer=offer)

        await callback.message.answer(
            text=OffersLexicon.OFFER_STUDENT_READY_MSG.format(
                company_name=company_name,
                recruiter_name=recruiter_name,
                student_full_name=student_full_name,
                student_speciality=student_speciality,
                chat_url=url),
            reply_markup=OffersMarkup.chat_offer(url=url, is_stud=True)
        )

        if recruiter_chat_id:
            await bot.send_message(
                chat_id=recruiter_chat_id,
                text=OffersLexicon.OFFER_RECRUITER_READY_MSG.format(
                    company_name=company_name,
                    recruiter_name=recruiter_name,
                    student_full_name=student_full_name,
                    student_speciality=student_speciality,
                    chat_url=url
                ),
                reply_markup=OffersMarkup.chat_offer(url=url)
            )

    @classmethod
    @TelegramDecorator.log_call()
    async def no_new_offer_btn(cls, callback: CallbackQuery, state: FSMContext):
        await cls._ack_callback(callback=callback)
        if not await cls._ensure_student_actor(callback=callback, state=state):
            return

        offer_id = cls._offer_id_from_callback(callback=callback)
        if offer_id is None:
            await callback.message.answer(
                text=ErrorLexicon.ERROR_RETURN_MENU_MSG,
                reply_markup=OffersMarkup.back_markup
            )
            return

        await cls._request_reject_reason(
            callback=callback,
            state=state,
            offer_id=offer_id
        )

    @classmethod
    @TelegramDecorator.log_call()
    async def failure_offer_btn(cls, callback: CallbackQuery, state: FSMContext):
        await cls._ack_callback(callback=callback)
        if not await cls._ensure_student_actor(callback=callback, state=state):
            return

        offer_id = cls._offer_id_from_callback(callback=callback)
        if offer_id is None:
            await callback.message.answer(
                text=ErrorLexicon.ERROR_RETURN_MENU_MSG,
                reply_markup=OffersMarkup.back_markup
            )
            return

        await cls._request_reject_reason(
            callback=callback,
            state=state,
            offer_id=offer_id
        )

    @classmethod
    @TelegramDecorator.log_call()
    async def reject_offer_msg(cls, message: Message, state: FSMContext):
        data = await state.get_data()
        _id = data.get("id", 0)

        await state.clear()

        offer = await cls._load_offer_with_entities(offer_id=_id)

        recruiter_chat_id = cls._recruiter_chat_id(offer=offer)
        student_full_name = cls._student_full_name(offer=offer)
        student_speciality = cls._speciality(offer=offer)

        await WebTools.set_status(_id=_id, status="REFUSAL", student_response_text=message.text)

        await message.answer(
            text=OffersLexicon.OFFER_REJECT_SUCCESS_STUDENT_MSG,
            reply_markup=OffersMarkup.back_markup
        )

        if recruiter_chat_id:
            await bot.send_message(
                chat_id=recruiter_chat_id,
                text=OffersLexicon.OFFER_REJECT_RECRUITER_MSG.format(
                    student_full_name=student_full_name,
                    student_speciality=student_speciality,
                ),
            )
            similar_students = await WebTools.get_similar_students_by_offer(offer=offer, limit=10)
            if similar_students:
                await bot.send_message(
                    chat_id=recruiter_chat_id,
                    text=OffersLexicon.OFFER_SIMILAR_STUDENTS_MSG.format(
                        students_links=cls._format_similar_students_links(similar_students)
                    )
                )
            else:
                await bot.send_message(
                    chat_id=recruiter_chat_id,
                    text=OffersLexicon.OFFER_SIMILAR_STUDENTS_EMPTY_MSG
                )

    @classmethod
    @TelegramDecorator.log_call()
    async def yes_offer_btn(cls, callback: CallbackQuery, state: FSMContext):
        await cls._ack_callback(callback=callback)
        await AdminTools.edit_reply(message=callback.message)

        _id = cls._offer_id_from_callback(callback=callback)
        if _id is None:
            await callback.message.answer(
                text=ErrorLexicon.ERROR_RETURN_MENU_MSG,
                reply_markup=OffersMarkup.back_markup
            )
            return
        chat_id = str(callback.message.chat.id)
        is_stud = await cls._is_student_user(state=state, chat_id=chat_id)

        offer = await cls._load_offer_with_entities(offer_id=_id)

        recruiter_company_name = cls._company_name(offer=offer)
        recruiter_chat_id = cls._recruiter_chat_id(offer=offer)
        student_chat_id = cls._student_chat_id(offer=offer)

        student_full_name = cls._student_full_name(offer=offer)
        student_speciality = cls._speciality(offer=offer)
        current_result = cls._result(offer=offer)

        if current_result not in {"EXPECTATION", "STUDENT_CONFIRMED", "RECRUITER_CONFIRMED"}:
            await callback.message.answer(
                text=ErrorLexicon.ERROR_RETURN_MENU_MSG,
                reply_markup=OffersMarkup.back_markup
            )
            return

        if cls._already_confirmed_by_actor(current_result=current_result, is_student_actor=is_stud):
            await callback.message.answer(
                text=cls._wait_other_side_msg(is_stud=is_stud),
                reply_markup=OffersMarkup.back_markup
            )
            return

        next_result = cls._next_success_status(current_result=current_result, is_student_actor=is_stud)

        await WebTools.set_status(_id=_id, status=next_result)

        if next_result != "SUCCESS":
            await callback.message.answer(
                text=cls._wait_other_side_msg(is_stud=is_stud),
                reply_markup=OffersMarkup.back_markup
            )

            if is_stud and recruiter_chat_id:
                await bot.send_message(
                    chat_id=recruiter_chat_id,
                    text=OffersLexicon.OFFER_SUCCESS_OTHER_SIDE_CONFIRMED_RECRUITER_MSG,
                    reply_markup=OffersMarkup.active_offer(_id=_id, can_reject=False)
                )
            if (not is_stud) and student_chat_id:
                await bot.send_message(
                    chat_id=student_chat_id,
                    text=OffersLexicon.OFFER_SUCCESS_OTHER_SIDE_CONFIRMED_MSG,
                    reply_markup=OffersMarkup.active_offer(_id=_id, can_reject=True)
                )
            return

        if is_stud:
            await callback.message.answer(
                text=OffersLexicon.OFFER_SUCCESS_STUDENT_MSG.format(
                    student_full_name=student_full_name,
                    company_name=recruiter_company_name,
                    student_speciality=student_speciality,
                ),
                reply_markup=OffersMarkup.back_markup
            )
            if recruiter_chat_id:
                await bot.send_message(
                    chat_id=recruiter_chat_id,
                    text=OffersLexicon.OFFER_SUCCESS_RECRUITER_MSG.format(
                        student_full_name=student_full_name,
                        student_speciality=student_speciality,
                    )
                )
            return

        await callback.message.answer(
            text=OffersLexicon.OFFER_SUCCESS_RECRUITER_CONFIRM_MSG.format(
                student_full_name=student_full_name,
                student_speciality=student_speciality,
                company_name=recruiter_company_name,
            ),
            reply_markup=OffersMarkup.back_markup
        )

        if student_chat_id:
            await bot.send_message(
                chat_id=student_chat_id,
                text=OffersLexicon.OFFER_SUCCESS_STUDENT_MSG.format(
                    student_full_name=student_full_name,
                    company_name=recruiter_company_name,
                    student_speciality=student_speciality,
                )
            )
