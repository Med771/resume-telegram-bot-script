from aiogram.fsm.state import StatesGroup, State


class OfferState(StatesGroup):
    NO_NEW_OFFER_STATE = State(state="NO_NEW_OFFER_STATE")