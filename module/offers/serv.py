from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from addons.lexicon import OffersLexicon, MenuLexicon
from addons.decorator import TelegramDecorator
from addons.markup import OffersMarkup, MenuMarkup
from tools.admin import AdminTools
from tools.web import WebTools


class OffersService:
    @classmethod
    @TelegramDecorator.log_call()
    async def offers_btn(cls, callback: CallbackQuery, state: FSMContext):
        await AdminTools.delete_msg(message=callback.message)

        data = await WebTools.get_offers(is_stud=True, chat_id=str(callback.message.chat.id))

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

        if offer.get("result", "") == "SYNC":
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
                text=MenuLexicon.NO_SYNC_START_MSG,
                reply_markup=MenuMarkup.back_markup
            )

    # @classmethod
    # @TelegramDecorator.log_call()
    # async def yes_new_offer_btn(cls, callback: CallbackQuery, state: FSMContext):
    #     await AdminTools.delete_msg(message=callback.message)
    #
    #     call_data = callback.data.split("_")
    #     _id = int(call_data[-1])
    #
    #     await callback.message.answer(
    #         text=OffersLexicon.
    #     )
