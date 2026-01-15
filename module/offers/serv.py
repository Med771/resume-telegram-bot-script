from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from addons.lexicon import OffersLexicon
from addons.decorator import TelegramDecorator
from addons.markup import OffersMarkup
from tools.admin import AdminTools


class OffersService:
    @classmethod
    @TelegramDecorator.log_call()
    async def offers_btn(cls, callback: CallbackQuery, state: FSMContext):
        await AdminTools.delete_msg(message=callback.message)

        await callback.message.answer(
            text=OffersLexicon.OFFERS_MSG,
            reply_markup=OffersMarkup.markup_offers(offers=[])
        )
