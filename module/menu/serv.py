from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from addons.decorator import TelegramDecorator
from addons.lexicon import MenuLexicon, SyncLexicon
from addons.markup import MenuMarkup
from tools.admin import AdminTools

from tools.web import WebTools

async def menu(message: Message, state: FSMContext):
    if await WebTools.get_stud_by_id(user_id=str(message.chat.id)):
        await state.update_data(u=1)

        await message.answer(text=MenuLexicon.STUDENT_START_MSG, reply_markup=MenuMarkup.offers_markup)
    elif await WebTools.get_rec_by_id(user_id=str(message.chat.id)):
        await state.update_data(u=2)

        await message.answer(text=MenuLexicon.EMPLOYER_START_MSG, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(text=MenuLexicon.NO_SYNC_START_MSG, reply_markup=ReplyKeyboardRemove())


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

            if res:
                if res == 2:
                    await message.answer(text=SyncLexicon.SYNC_SUCCESS_MSG)
                else:
                    await message.answer(text=SyncLexicon.SYNC_EXISTS_MSG)

                if int(is_stud) < 5000:
                    await state.update_data(u=1)

                    await message.answer(text=MenuLexicon.STUDENT_START_MSG, reply_markup=MenuMarkup.offers_markup)
                else:
                    await state.update_data(u=2)

                    await message.answer(text=MenuLexicon.EMPLOYER_START_MSG, reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer(text=MenuLexicon.NO_SYNC_START_MSG, reply_markup=ReplyKeyboardRemove())
        else:
            await menu(message, state)

    @classmethod
    @TelegramDecorator.log_call()
    async def back_btn(cls, callback: CallbackQuery, state: FSMContext):
        await AdminTools.delete_msg(message=callback.message)

        await menu(message=callback.message, state=state)
