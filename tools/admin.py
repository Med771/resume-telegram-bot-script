from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import TelegramConfig

from addons.decorator import TelegramDecorator


class AdminTools:
    @classmethod
    @TelegramDecorator.log_del()
    async def delete_msg(cls, message: Message):
        await message.delete()

    @classmethod
    @TelegramDecorator.log_del()
    async def delete_msg_by_id(cls, chat_id: str | int, message_id: int):
        await TelegramConfig.BOT.delete_message(chat_id=chat_id, message_id=message_id)

    @classmethod
    @TelegramDecorator.log_call()
    async def edit_reply(cls, message: Message):
        await message.edit_reply_markup(reply_markup=None)

    @staticmethod
    def is_admin(chat_id: int | str) -> bool:
        is_admin_id = str(chat_id) in TelegramConfig.ADMIN_CHAT_IDS
        is_owner_id = str(chat_id) == TelegramConfig.OWNER_CHAT_ID

        return is_admin_id or is_owner_id

    @classmethod
    @TelegramDecorator.log_call()
    async def get_state(cls, state: FSMContext):
        try:
            return await state.get_state()

        except BaseException:
            return ""
