from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from addons.lexicon import MenuLexicon
from addons.decorator import TelegramDecorator


class MenuFilter:
    @classmethod
    @TelegramDecorator.log_call()
    async def back_btn(cls, callback: CallbackQuery, state: FSMContext):
        is_btn = callback.data == MenuLexicon.BACK_BTN_CL

        return is_btn
