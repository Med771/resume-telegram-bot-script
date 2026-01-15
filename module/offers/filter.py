from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from addons.lexicon import OffersLexicon
from addons.decorator import TelegramDecorator


class OffersFilter:
    @classmethod
    @TelegramDecorator.log_call()
    async def offers_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        is_btn = callback.data == OffersLexicon.OFFERS_BTN_CL
        is_state_data = await state.get_data()

        return is_btn and is_state_data.get("u", 0) == 1
