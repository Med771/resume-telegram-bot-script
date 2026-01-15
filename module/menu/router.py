from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from module.menu.filter import MenuFilter
from module.menu.serv import MenuService

menu_router = Router(name=__name__)


@menu_router.message(Command(commands=["start"]))
async def start(message: Message, state: FSMContext):
    await MenuService.start_msg(message, state)

@menu_router.callback_query(MenuFilter.back_btn)
async def back_btn(callback: CallbackQuery, state: FSMContext):
    await MenuService.back_btn(callback, state)