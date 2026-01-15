from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from module.offers.filter import OffersFilter
from module.offers.serv import OffersService

offers_router = Router(name=__name__)


@offers_router.message(OffersFilter.offers_btn)
async def offers_btn(message: Message, state: FSMContext):
    await OffersService.offers_btn(message=message, state=state)
