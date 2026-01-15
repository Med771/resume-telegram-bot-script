from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from addons.lexicon import OffersLexicon
from addons.decorator import TelegramDecorator
from addons.markup import OffersMarkup
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
