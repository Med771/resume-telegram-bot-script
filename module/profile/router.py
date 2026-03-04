from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from module.profile.filter import ProfileFilter
from module.profile.serv import ProfileService

profile_router = Router(name=__name__)


@profile_router.callback_query(ProfileFilter.profile_btn)
async def profile_btn(callback: CallbackQuery, state: FSMContext):
    await ProfileService.profile_btn(callback=callback, state=state)
