from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from module.offers.filter import OffersFilter
from module.offers.serv import OffersService

offers_router = Router(name=__name__)


@offers_router.callback_query(OffersFilter.offers_btn)
async def offers_btn(callback: CallbackQuery, state: FSMContext):
    await OffersService.offers_btn(callback=callback, state=state)


@offers_router.callback_query(OffersFilter.offer_btn)
async def offers_btn(callback: CallbackQuery, state: FSMContext):
    await OffersService.offer_btn(callback=callback, state=state)
