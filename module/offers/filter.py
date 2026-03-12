from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from addons.lexicon import OffersLexicon
from addons.decorator import TelegramDecorator
from addons.state.offer import OfferState
from tools.admin import AdminTools


class OffersFilter:
    @staticmethod
    def _eq(value: str | None, expected: str) -> bool:
        return (value or "") == expected

    @staticmethod
    def _starts(value: str | None, prefix: str) -> bool:
        return (value or "").startswith(prefix)

    @classmethod
    @TelegramDecorator.log_call()
    async def back_btn(cls, callback: CallbackQuery, state: FSMContext):
        return cls._eq(callback.data, OffersLexicon.BACK_TO_OFFERS_BTN_CL)

    @classmethod
    @TelegramDecorator.log_call()
    async def offers_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        return cls._eq(callback.data, OffersLexicon.OFFERS_BTN_CL)

    @classmethod
    @TelegramDecorator.log_call()
    async def offer_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        return cls._starts(callback.data, OffersLexicon.OFFER_BTN_CL)

    @classmethod
    @TelegramDecorator.log_call()
    async def yes_new_offer_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        return cls._starts(callback.data, OffersLexicon.NEW_OFFERS_YES_BTN_CL)

    @classmethod
    @TelegramDecorator.log_call()
    async def no_new_offer_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        return cls._starts(callback.data, OffersLexicon.NEW_OFFERS_NO_BTN_CL)

    @classmethod
    @TelegramDecorator.log_call()
    async def failure_offer_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        return cls._starts(callback.data, OffersLexicon.OFFERS_FAILURE_BTN_CL)

    @classmethod
    @TelegramDecorator.log_call()
    async def reject_offer_msg(cls, message: Message, state: FSMContext = None):
        is_state = await AdminTools.get_state(state) == OfferState.REJECT_OFFER_REASON_STATE

        return is_state

    @classmethod
    @TelegramDecorator.log_call()
    async def yes_offer_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        return cls._starts(callback.data, OffersLexicon.OFFERS_SUCCESS_BTN_CL)
