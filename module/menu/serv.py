from aiogram.types import Message

from addons.decorator import TelegramDecorator
from addons.lexicon import MenuLexicon

from tools.backend import BackendTools


class MenuService:
    @classmethod
    @TelegramDecorator.log_call()
    async def start_msg(cls, message: Message):
        args = message.text.split()[1]

        if args:
            res = await BackendTools.referral_link(_id=args, user_id=str(message.from_user.id))

            if res:
                await message.answer(text=MenuLexicon.SYNC_MSG)

        await message.answer(text=MenuLexicon.START_MSG)
