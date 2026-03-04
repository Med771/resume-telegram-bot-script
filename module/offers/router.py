from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from module.offers.filter import OffersFilter
from module.offers.serv import OffersService

offers_router = Router(name=__name__)


@offers_router.callback_query(OffersFilter.offers_btn)
async def offers_btn(callback: CallbackQuery, state: FSMContext):
    await OffersService.offers_btn(callback=callback, state=state)


@offers_router.callback_query(OffersFilter.offer_btn)
async def offer_btn(callback: CallbackQuery, state: FSMContext):
    await OffersService.offer_btn(callback=callback, state=state)


@offers_router.callback_query(OffersFilter.yes_new_offer_btn)
async def yes_new_offer_btn(callback: CallbackQuery, state: FSMContext):
    await OffersService.yes_new_offer_btn(callback=callback, state=state)


@offers_router.callback_query(OffersFilter.no_new_offer_btn)
async def no_new_offer_btn(callback: CallbackQuery, state: FSMContext):
    await OffersService.no_new_offer_btn(callback=callback, state=state)


@offers_router.callback_query(OffersFilter.failure_offer_btn)
async def failure_offer_btn(callback: CallbackQuery, state: FSMContext):
    await OffersService.failure_offer_btn(callback=callback, state=state)


@offers_router.message(OffersFilter.reject_offer_msg)
async def reject_offer_msg(message: Message, state: FSMContext):
    await OffersService.reject_offer_msg(message=message, state=state)


@offers_router.callback_query(OffersFilter.yes_offer_btn)
async def yes_offer_btn(callback: CallbackQuery, state: FSMContext):
    await OffersService.yes_offer_btn(callback=callback, state=state)


@offers_router.message(OffersFilter.chat_activity_msg)
async def chat_activity_msg(message: Message):
    await OffersService.chat_activity_msg(message=message)
