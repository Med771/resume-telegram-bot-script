from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from addons.lexicon import OffersLexicon
from addons.decorator import TelegramDecorator
from addons.state.offer import OfferState
from tools.admin import AdminTools


class OffersFilter:
    @classmethod
    @TelegramDecorator.log_call()
    async def back_btn(cls, callback: CallbackQuery, state: FSMContext):
        is_btn = callback.data == OffersLexicon.BACK_TO_OFFERS_BTN_TXT
        # state_data = await state.get_data()

        return is_btn

    @classmethod
    @TelegramDecorator.log_call()
    async def offers_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        is_btn = callback.data == OffersLexicon.OFFERS_BTN_CL
        # state_data = await state.get_data()

        return is_btn

    @classmethod
    @TelegramDecorator.log_call()
    async def offer_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        is_btn = callback.data.startswith(OffersLexicon.OFFER_BTN_CL)
        # state_data = await state.get_data()

        return is_btn

    @classmethod
    @TelegramDecorator.log_call()
    async def yes_new_offer_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        is_btn = callback.data.startswith(OffersLexicon.NEW_OFFERS_YES_BTN_CL)
        # state_data = await state.get_data()

        return is_btn

    @classmethod
    @TelegramDecorator.log_call()
    async def no_new_offer_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        is_btn = callback.data.startswith(OffersLexicon.NEW_OFFERS_NO_BTN_CL)

        return is_btn


    @classmethod
    @TelegramDecorator.log_call()
    async def no_new_offer_msg(cls, message: Message, state: FSMContext = None):
        is_state = await AdminTools.get_state(state) == OfferState.NO_NEW_OFFER_STATE

        return is_state

    @classmethod
    @TelegramDecorator.log_call()
    async def yes_offer_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        is_btn = callback.data.startswith(OffersLexicon.OFFERS_SUCCESS_BTN_CL)

        return is_btn
