from aiogram import Router
from aiogram.types import Message

from module.chat.filter import ChatFilter
from module.chat.serv import ChatService

chat_router = Router(name=__name__)


@chat_router.message(ChatFilter.chat_activity_msg)
async def chat_activity_msg(message: Message):
    print(message.chat.id, message.from_user.id)

    await ChatService.chat_activity_msg(message=message)
