from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from addons.decorator import TelegramDecorator


class ChatFilter:
    @classmethod
    @TelegramDecorator.log_call()
    async def chat_activity_msg(cls, message: Message, state: FSMContext = None):
        if message.chat.type not in {"group", "supergroup"}:
            return False
        if not message.from_user or message.from_user.is_bot:
            return False
        return True
