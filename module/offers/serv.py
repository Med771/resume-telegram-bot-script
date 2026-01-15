from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from addons.lexicon import OffersLexicon
from addons.decorator import TelegramDecorator


class OffersService:
    @classmethod
    @TelegramDecorator.log_call()
    async def offers_btn(cls, message: Message, state: FSMContext):

