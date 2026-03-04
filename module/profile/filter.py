from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from addons.decorator import TelegramDecorator
from addons.lexicon import MenuLexicon


class ProfileFilter:
    @classmethod
    @TelegramDecorator.log_call()
    async def profile_btn(cls, callback: CallbackQuery, state: FSMContext = None):
        return callback.data == MenuLexicon.PROFILE_BTN_CL
