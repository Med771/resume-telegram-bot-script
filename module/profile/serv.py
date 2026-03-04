from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from addons.decorator import TelegramDecorator
from addons.lexicon import ProfileLexicon
from addons.markup import MenuMarkup
from tools.admin import AdminTools
from tools.web import WebTools


class ProfileService:
    @staticmethod
    def _full_name(data: dict) -> str:
        if data.get("fullName"):
            full_name = str(data.get("fullName", "")).strip()
            if full_name:
                return full_name

        first_name = data.get("firstName", "") or ""
        last_name = data.get("lastName", "") or ""
        full_name = f"{first_name} {last_name}".strip()
        return full_name or "Не указано"

    @staticmethod
    def _val(data: dict, key: str, default: str = "Не указано") -> str:
        value = data.get(key)
        if value is None:
            return default
        value_str = str(value).strip()
        return value_str if value_str else default

    @classmethod
    @TelegramDecorator.log_call()
    async def profile_btn(cls, callback: CallbackQuery, state: FSMContext):
        await AdminTools.delete_msg(message=callback.message)

        profile_payload = await WebTools.get_profile_by_chat_id(chat_id=str(callback.message.chat.id))
        if not profile_payload:
            await callback.message.answer(
                text=ProfileLexicon.PROFILE_EMPTY_MSG,
                reply_markup=MenuMarkup.back_markup
            )
            return

        profile_type = profile_payload.get("type", "")
        profile_data = profile_payload.get("data", {}) or {}

        if profile_type == "st":
            await callback.message.answer(
                text=ProfileLexicon.PROFILE_STUDENT_MSG.format(
                    full_name=cls._full_name(profile_data),
                    speciality=cls._val(profile_data, "speciality"),
                    course=cls._val(profile_data, "course"),
                    busyness=cls._val(profile_data, "busyness"),
                    city=cls._val(profile_data, "city"),
                    email=cls._val(profile_data, "email"),
                    phone=cls._val(profile_data, "phoneNumber"),
                ),
                reply_markup=MenuMarkup.back_markup
            )
            return

        if profile_type == "re":
            await callback.message.answer(
                text=ProfileLexicon.PROFILE_RECRUITER_MSG.format(
                    company_name=cls._val(profile_data, "companyName"),
                    full_name=cls._full_name(profile_data),
                    email=cls._val(profile_data, "email"),
                    phone=cls._val(profile_data, "phoneNumber"),
                ),
                reply_markup=MenuMarkup.back_markup
            )
            return

        await callback.message.answer(
            text=ProfileLexicon.PROFILE_EMPTY_MSG,
            reply_markup=MenuMarkup.back_markup
        )
