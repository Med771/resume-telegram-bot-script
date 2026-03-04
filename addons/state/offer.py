from aiogram.fsm.state import StatesGroup, State


class OfferState(StatesGroup):
    REJECT_OFFER_REASON_STATE = State(state="REJECT_OFFER_REASON_STATE")