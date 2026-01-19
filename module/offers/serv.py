from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from addons.lexicon import OffersLexicon, ErrorLexicon
from addons.decorator import TelegramDecorator
from addons.markup import OffersMarkup
from addons.state.offer import OfferState

from tools.admin import AdminTools
from tools.web import WebTools

from config import TelegramConfig

bot = TelegramConfig.BOT


class OffersService:
    @classmethod
    @TelegramDecorator.log_call()
    async def offers_btn(cls, callback: CallbackQuery, state: FSMContext):
        await AdminTools.delete_msg(message=callback.message)

        data = await WebTools.get_offers_by_id(is_stud=True, chat_id=str(callback.message.chat.id))

        offers = []

        for offer in data.get("offers", []):
            offers.append((offer.get("id"), offer.get("recruiterRes", {}).get("companyName", "")))

        await callback.message.answer(
            text=OffersLexicon.OFFERS_MSG,
            reply_markup=OffersMarkup.markup_offers(offers=offers)
        )

    @classmethod
    @TelegramDecorator.log_call()
    async def offer_btn(cls, callback: CallbackQuery, state: FSMContext):
        await AdminTools.delete_msg(message=callback.message)

        call_data = callback.data.split("_")
        _id = int(call_data[-1])

        offer = await WebTools.get_offer(_id=_id)

        company_name = offer.get("recruiterRes", {}).get("companyName", "")
        recruiter_name = offer.get("recruiterRes", {}).get("fullName", "")
        speciality = offer.get("studentRes", {}).get("speciality", "")

        if offer.get("result", "") == "WAITING":
            await callback.message.answer(
                text=OffersLexicon.OFFER_TO_STUDENT_MSG.format(
                    company_name=company_name,
                    recruiter_name=recruiter_name,
                    speciality=speciality
                ),
                reply_markup=OffersMarkup.new_offer(_id=_id)
            )
        elif offer.get("result", "") == "EXPECTATION":
            await callback.message.answer(
                text=OffersLexicon.OFFER_CHAT_ACTIVE_MSG.format(
                    company_name=company_name,
                    recruiter_name=recruiter_name,
                    speciality=speciality
                ),
                reply_markup=OffersMarkup.active_offer(_id=_id)
            )
        else:
            await callback.message.answer(
                text=ErrorLexicon.ERROR_RETURN_MENU_MSG,
                reply_markup=OffersMarkup.back_markup
            )

    @classmethod
    @TelegramDecorator.log_call()
    async def yes_new_offer_btn(cls, callback: CallbackQuery, state: FSMContext):
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

        company_name = _res.get("recruiterRes", {}).get("companyName", "")
        recruiter_name = _res.get("recruiterRes", {}).get("fullName", "")
        recruiter_chat_id = _res.get("recruiterRes", {}).get("chatId", "")

        student_full_name = _res.get("studentRes", {}).get("fullName", "")
        student_speciality = _res.get("studentRes", {}).get("speciality", "")

        url = _res.get("chatUrl", "")

        await callback.message.answer(
            text=OffersLexicon.OFFER_STUDENT_READY_MSG.format(
                company_name=company_name,
                recruiter_name=recruiter_name,
                chat_url=url),
            reply_markup=OffersMarkup.chat_offer(url=url)
        )

        await bot.send_message(
            chat_id=recruiter_chat_id,
            text=OffersLexicon.OFFER_RECRUITER_READY_MSG.format(
                student_full_name=student_full_name,
                student_speciality=student_speciality,
                chat_url=url
            ),
            reply_markup=OffersMarkup.chat_offer(url=url)
        )

        await WebTools.set_status(_id=_id, status="EXPECTATION")

    @classmethod
    @TelegramDecorator.log_call()
    async def no_new_offer_btn(cls, callback: CallbackQuery, state: FSMContext):
        call_data = callback.data.split("_")
        _id = int(call_data[-1])

        await callback.message.answer(
            text=OffersLexicon.OFFER_REJECT_REASON_MSG,
            reply_markup=OffersMarkup.back_markup
        )

        await state.set_state(OfferState.NO_NEW_OFFER_STATE)
        await state.update_data(id=_id)

    @classmethod
    @TelegramDecorator.log_call()
    async def no_new_offer_msg(cls, message: Message, state: FSMContext):
        data = await state.get_data()
        _id = data.get("id", 0)

        offer = await WebTools.get_offer(_id=_id)

        await state.clear()

        await WebTools.set_status(_id=_id, status="REFUSAL")

        recruiter_chat_id = offer.get("recruiterRes", {}).get("chatId", "")

        student_full_name = offer.get("studentRes", {}).get("fullName", "")
        student_speciality = offer.get("studentRes", {}).get("speciality", "")

        await message.answer(
            text=OffersLexicon.OFFER_REJECT_SUCCESS_STUDENT_MSG,
            reply_markup=OffersMarkup.back_markup
        )

        await bot.send_message(
            chat_id=recruiter_chat_id,
            text=OffersLexicon.OFFER_REJECT_RECRUITER_MSG.format(
                student_full_name=student_full_name,
                student_speciality=student_speciality,
                reject_reason=message.text
            )
        )

    @classmethod
    @TelegramDecorator.log_call()
    async def yes_offer_btn(cls, callback: CallbackQuery, state: FSMContext):
        await AdminTools.edit_reply(message=callback.message)

        call_data = callback.data.split("_")
        _id = int(call_data[-1])

        offer = await WebTools.get_offer(_id=_id)

        recruiter_company_name = offer.get("recruiterRes", {}).get("companyName", "")
        recruiter_chat_id = offer.get("recruiterRes", {}).get("chatId", "")

        student_full_name = offer.get("studentRes", {}).get("fullName", "")
        student_speciality = offer.get("studentRes", {}).get("speciality", "")

        await WebTools.set_status(_id=_id, status="SUCCESS")

        await callback.message.answer(
            text=OffersLexicon.OFFER_SUCCESS_STUDENT_MSG.format(
                student_full_name=student_full_name,
                company_name=recruiter_company_name,
                student_speciality=student_speciality,
            ),
            reply_markup=OffersMarkup.back_markup
        )

        await bot.send_message(
            chat_id=recruiter_chat_id,
            text=OffersLexicon.OFFER_SUCCESS_RECRUITER_MSG.format(
                student_full_name=student_full_name,
                student_speciality=student_speciality,
            )
        )
