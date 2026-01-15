from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from addons.decorator import TelegramDecorator
from addons.lexicon import MenuLexicon, SyncLexicon
from addons.markup import MenuMarkup

from tools.web import WebTools


class MenuService:
    @classmethod
    @TelegramDecorator.log_call()
    async def start_msg(cls, message: Message, state: FSMContext):
        await state.clear()

        _arr = message.text.split()

        if len(_arr) == 2:
            args = message.text.split()[1]
            is_stud, _id = args.split("_")

            res = await WebTools.referral_link(is_stud=int(is_stud) < 5000, _id=_id, user_id=str(message.from_user.id))

            markup = MenuMarkup.offers_markup if int(is_stud) < 5000 else MenuMarkup.query_markup

            await state.update_data(u=1 if int(is_stud) < 5000 else 2)

            if res == 2:
                await message.answer(text=SyncLexicon.SYNC_SUCCESS_MSG)
            elif res == 1:
                await message.answer(text=SyncLexicon.SYNC_EXISTS_MSG)
            else:
                await message.answer(text=SyncLexicon.SYNC_FAILURE_MSG)

                markup = ReplyKeyboardRemove()
        else:
            if await WebTools.get_stud_by_id(user_id=str(message.from_user.id)):
                markup = MenuMarkup.offers_markup

                await state.update_data(u=1)
            elif await WebTools.get_rec_by_id(user_id=str(message.from_user.id)):
                markup = MenuMarkup.query_markup

                await state.update_data(u=2)
            else:
                await message.answer(text=SyncLexicon.SYNC_FAILURE_MSG)

                markup = ReplyKeyboardRemove()

        await message.answer(text=MenuLexicon.START_MSG, reply_markup=markup)
