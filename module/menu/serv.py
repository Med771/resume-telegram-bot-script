from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from addons.decorator import TelegramDecorator
from addons.lexicon import MenuLexicon, SyncLexicon
from addons.markup import MenuMarkup
from tools.admin import AdminTools

from tools.web import WebTools


def parse_sync_args(raw_args: str) -> tuple[bool, str] | None:
    if "_" not in raw_args:
        return None

    role_part, user_id = raw_args.split("_", 1)

    if role_part in {"st", "student"}:
        return True, user_id
    if role_part in {"re", "recruiter"}:
        return False, user_id

    if role_part.isdigit():
        return int(role_part) < 5000, user_id

    return None


async def menu(message: Message, state: FSMContext):
    if await WebTools.get_stud_by_id(user_id=str(message.chat.id)):
        await state.update_data(u=1)

        await message.answer(text=MenuLexicon.STUDENT_START_MSG, reply_markup=MenuMarkup.student_markup)
    elif await WebTools.get_rec_by_id(user_id=str(message.chat.id)):
        await state.update_data(u=2)

        await message.answer(text=MenuLexicon.EMPLOYER_START_MSG, reply_markup=MenuMarkup.employer_markup)
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
            parsed = parse_sync_args(raw_args=args)
            if not parsed:
                await message.answer(text=MenuLexicon.NO_SYNC_START_MSG, reply_markup=ReplyKeyboardRemove())
                return

            is_stud, _id = parsed

            res = await WebTools.referral_link(is_stud=is_stud, _id=_id, user_id=str(message.from_user.id))

            if res:
                if res == 2:
                    await message.answer(text=SyncLexicon.SYNC_SUCCESS_MSG)
                else:
                    await message.answer(text=SyncLexicon.SYNC_EXISTS_MSG)

                if is_stud:
                    await state.update_data(u=1)

                    await message.answer(text=MenuLexicon.STUDENT_START_MSG, reply_markup=MenuMarkup.student_markup)
                else:
                    await state.update_data(u=2)

                    await message.answer(text=MenuLexicon.EMPLOYER_START_MSG, reply_markup=MenuMarkup.employer_markup)
            else:
                await message.answer(text=MenuLexicon.NO_SYNC_START_MSG, reply_markup=ReplyKeyboardRemove())
        else:
            await menu(message, state)

    @classmethod
    @TelegramDecorator.log_call()
    async def back_btn(cls, callback: CallbackQuery, state: FSMContext):
        await AdminTools.delete_msg(message=callback.message)

        data = await state.get_data()

        await state.clear()

        if "u" in data:
            await state.update_data(u=data["u"])

        await menu(message=callback.message, state=state)
