from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from addons.lexicon import OffersLexicon, ErrorLexicon
from addons.decorator import TelegramDecorator
from addons.markup import OffersMarkup
from addons.state.offer import OfferState

from tools.admin import AdminTools
from tools.logger import LoggerTools
from tools.web import WebTools

from config import TelegramConfig

bot = TelegramConfig.BOT
logger = LoggerTools.get_logger(__name__, info=True, warn=True, error=True)


class OffersService:
    @staticmethod
    def _result(offer: dict) -> str:
        return offer.get("result", "") or offer.get("resultEnum", "")

    @staticmethod
    def _company_name(offer: dict) -> str:
        return (
            offer.get("recruiterRes", {}).get("companyName", "")
            or offer.get("companyName", "")
            or offer.get("recruiterCompanyName", "")
        )

    @staticmethod
    def _recruiter_name(offer: dict) -> str:
        return (
            offer.get("recruiterRes", {}).get("fullName", "")
            or offer.get("recruiterName", "")
            or "Работодатель"
        )

    @staticmethod
    def _speciality(offer: dict) -> str:
        return (
            offer.get("studentRes", {}).get("speciality", "")
            or offer.get("studentSpeciality", "")
            or "Не указано"
        )

    @staticmethod
    def _recruiter_chat_id(offer: dict) -> str:
        return (
            offer.get("recruiterRes", {}).get("chatId", "")
            or offer.get("recruiterTelegramUserId", "")
        )

    @staticmethod
    def _student_chat_id(offer: dict) -> str:
        return (
            offer.get("studentRes", {}).get("chatId", "")
            or offer.get("studentTelegramUserId", "")
        )

    @staticmethod
    def _student_full_name(offer: dict) -> str:
        return (
            offer.get("studentRes", {}).get("fullName", "")
            or offer.get("studentFullName", "")
            or "Студент"
        )

    @staticmethod
    def _chat_url(offer: dict) -> str:
        return offer.get("chatUrl", "") or offer.get("chat_url", "")

    @classmethod
    @TelegramDecorator.log_call()
    async def chat_activity_msg(cls, message: Message):
        chat_id = str(message.chat.id)
        sender_id = str(message.from_user.id) if message.from_user else ""
        if not chat_id or not sender_id:
            logger.warning("chat_activity_msg skipped: empty chat_id or sender_id")
            return

        logger.info(
            f"chat_activity_msg received: chat_id={chat_id}, sender_id={sender_id}, "
            f"message_id={message.message_id}"
        )

        offer = await WebTools.get_offer_by_chat_id(chat_id=chat_id, results=["EXPECTATION"])
        if not offer:
            logger.warning(f"chat_activity_msg no active offer: chat_id={chat_id}")
            return

        enriched_offer = await WebTools.enrich_offer(offer=offer)
        if enriched_offer:
            offer = enriched_offer

        offer_id = offer.get("id")
        if offer_id is None:
            logger.error(f"chat_activity_msg invalid offer without id: chat_id={chat_id}")
            return

        recruiter_chat_id = cls._recruiter_chat_id(offer=offer)
        student_chat_id = cls._student_chat_id(offer=offer)
        current_result = cls._result(offer=offer) or "EXPECTATION"

        if sender_id == recruiter_chat_id:
            if offer.get("hasRecruiterMessage"):
                logger.info(f"chat_activity_msg recruiter flag already true: offer_id={offer_id}")
                return
            updated = await WebTools.set_status(
                _id=offer_id,
                status=current_result,
                has_recruiter_message=True
            )
            logger.info(
                f"chat_activity_msg recruiter update: offer_id={offer_id}, updated={updated}, "
                f"sender_id={sender_id}"
            )
            return

        if sender_id == student_chat_id:
            if offer.get("hasStudentMessage"):
                logger.info(f"chat_activity_msg student flag already true: offer_id={offer_id}")
                return
            updated = await WebTools.set_status(
                _id=offer_id,
                status=current_result,
                has_student_message=True
            )
            logger.info(
                f"chat_activity_msg student update: offer_id={offer_id}, updated={updated}, "
                f"sender_id={sender_id}"
            )
            return

        logger.warning(
            f"chat_activity_msg sender is not participant: offer_id={offer_id}, sender_id={sender_id}, "
            f"student_chat_id={student_chat_id}, recruiter_chat_id={recruiter_chat_id}"
        )

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
        await AdminTools.delete_msg(message=callback.message)

        call_data = callback.data.split("_")
        _id = int(call_data[-1])
        chat_id = str(callback.message.chat.id)
        is_stud = await cls._is_student_user(state=state, chat_id=chat_id)

        offer = await WebTools.get_offer(_id=_id)
        enriched_offer = await WebTools.enrich_offer(offer=offer)
        if enriched_offer:
            offer = enriched_offer

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
            if result == "EXPECTATION":
                await callback.message.answer(
                    text=OffersLexicon.OFFER_CHAT_ACTIVE_MSG.format(
                        company_name=company_name,
                        recruiter_name=recruiter_name,
                        speciality=speciality
                    ),
                    reply_markup=OffersMarkup.active_offer(_id=_id, can_reject=True)
                )
                return
        else:
            student_full_name = cls._student_full_name(offer=offer)
            if result == "WAITING":
                await callback.message.answer(
                    text=OffersLexicon.OFFER_TO_RECRUITER_WAITING_MSG.format(
                        student_full_name=student_full_name,
                        student_speciality=speciality,
                        company_name=company_name
                    ),
                    reply_markup=OffersMarkup.back_markup
                )
                return
            if result == "EXPECTATION":
                await callback.message.answer(
                    text=OffersLexicon.OFFER_TO_RECRUITER_ACTIVE_MSG.format(
                        student_full_name=student_full_name,
                        student_speciality=speciality,
                        company_name=company_name
                    ),
                    reply_markup=OffersMarkup.active_offer(_id=_id, can_reject=False)
                )
                return

        await callback.message.answer(
            text=ErrorLexicon.ERROR_RETURN_MENU_MSG,
            reply_markup=OffersMarkup.back_markup
        )

    @classmethod
    @TelegramDecorator.log_call()
    async def yes_new_offer_btn(cls, callback: CallbackQuery, state: FSMContext):
        chat_id = str(callback.message.chat.id)
        is_stud = await cls._is_student_user(state=state, chat_id=chat_id)
        if not is_stud:
            await callback.message.answer(
                text=OffersLexicon.OFFER_RECRUITER_READONLY_MSG,
                reply_markup=OffersMarkup.back_markup
            )
            return

        await AdminTools.edit_reply(message=callback.message)

        call_data = callback.data.split("_")
        _id = int(call_data[-1])

        _res = await WebTools.create_chat(_id=_id)

        if not _res:
            await callback.message.answer(
                text=ErrorLexicon.CHAT_CREATE_ERROR_MSG,
                reply_markup=OffersMarkup.back_markup
            )

            return

        await WebTools.set_status(
            _id=_id,
            status="EXPECTATION",
            has_recruiter_message=False,
            has_student_message=False
        )

        offer = _res if isinstance(_res, dict) else {}

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
            reply_markup=OffersMarkup.chat_offer(url=url)
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
        chat_id = str(callback.message.chat.id)
        is_stud = await cls._is_student_user(state=state, chat_id=chat_id)
        if not is_stud:
            await callback.message.answer(
                text=OffersLexicon.OFFER_RECRUITER_READONLY_MSG,
                reply_markup=OffersMarkup.back_markup
            )
            return

        call_data = callback.data.split("_")
        _id = int(call_data[-1])

        await callback.message.answer(
            text=OffersLexicon.OFFER_REJECT_REASON_MSG,
            reply_markup=OffersMarkup.back_markup
        )

        await state.set_state(OfferState.REJECT_OFFER_REASON_STATE)
        await state.update_data(id=_id)

    @classmethod
    @TelegramDecorator.log_call()
    async def failure_offer_btn(cls, callback: CallbackQuery, state: FSMContext):
        chat_id = str(callback.message.chat.id)
        is_stud = await cls._is_student_user(state=state, chat_id=chat_id)
        if not is_stud:
            await callback.message.answer(
                text=OffersLexicon.OFFER_RECRUITER_READONLY_MSG,
                reply_markup=OffersMarkup.back_markup
            )
            return

        call_data = callback.data.split("_")
        _id = int(call_data[-1])

        await callback.message.answer(
            text=OffersLexicon.OFFER_REJECT_REASON_MSG,
            reply_markup=OffersMarkup.back_markup
        )

        await state.set_state(OfferState.REJECT_OFFER_REASON_STATE)
        await state.update_data(id=_id)

    @classmethod
    @TelegramDecorator.log_call()
    async def reject_offer_msg(cls, message: Message, state: FSMContext):
        data = await state.get_data()
        _id = data.get("id", 0)

        await state.clear()

        offer = await WebTools.get_offer(_id=_id)
        enriched_offer = await WebTools.enrich_offer(offer=offer)
        if enriched_offer:
            offer = enriched_offer

        recruiter_chat_id = cls._recruiter_chat_id(offer=offer)
        student_full_name = cls._student_full_name(offer=offer)
        student_speciality = cls._speciality(offer=offer)
        reject_reason = message.text or ""

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
                    reject_reason=reject_reason,
                ),
            )

    @classmethod
    @TelegramDecorator.log_call()
    async def yes_offer_btn(cls, callback: CallbackQuery, state: FSMContext):
        await AdminTools.edit_reply(message=callback.message)

        call_data = callback.data.split("_")
        _id = int(call_data[-1])
        chat_id = str(callback.message.chat.id)
        is_stud = await cls._is_student_user(state=state, chat_id=chat_id)

        offer = await WebTools.get_offer(_id=_id)
        enriched_offer = await WebTools.enrich_offer(offer=offer)
        if enriched_offer:
            offer = enriched_offer

        recruiter_company_name = cls._company_name(offer=offer)
        recruiter_chat_id = cls._recruiter_chat_id(offer=offer)
        student_chat_id = cls._student_chat_id(offer=offer)

        student_full_name = cls._student_full_name(offer=offer)
        student_speciality = cls._speciality(offer=offer)

        await WebTools.set_status(_id=_id, status="SUCCESS")

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
