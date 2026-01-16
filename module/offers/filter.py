from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from addons.lexicon import OffersLexicon
from addons.decorator import TelegramDecorator


class OffersFilter:
    @classmethod
    @TelegramDecorator.log_call()
    async def back_btn(cls, callback: CallbackQuery, state: FSMContext):
        is_btn = callback.data == OffersLexicon.BACK_TO_OFFERS_BTN_TXT
        state_data = await state.get_data()

        return is_btn and state_data.get("u", 0) == 1

    @classmethod
    @TelegramDecorator.log_call()
    async def offers_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        is_btn = callback.data == OffersLexicon.OFFERS_BTN_CL
        state_data = await state.get_data()

        return is_btn and state_data.get("u", 0) == 1

    @classmethod
    @TelegramDecorator.log_call()
    async def offer_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        is_btn = callback.data.startswith(OffersLexicon.OFFER_BTN_CL)
        state_data = await state.get_data()

        return is_btn and state_data.get("u", 0) == 1

    @classmethod
    @TelegramDecorator.log_call()
    async def yes_new_offer_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        is_btn = callback.data.startswith(OffersLexicon.NEW_OFFERS_YES_BTN_CL)
        state_data = await state.get_data()

        return is_btn and state_data.get("u", 0) == 1

