from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from module.menu.serv import MenuService

menu_router = Router(name=__name__)


@menu_router.message(Command(commands=["start"]))
async def start(message: Message, state: FSMContext):
    await MenuService.start_msg(message, state)
