from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from addons.lexicon import OffersLexicon, MenuLexicon

MENU_BTN = InlineKeyboardButton(text=MenuLexicon.BACK_BTN_TXT, callback_data=MenuLexicon.BACK_BTN_CL)
BACK_BTN = InlineKeyboardButton(text=OffersLexicon.BACK_TO_OFFERS_BTN_TXT, callback_data=OffersLexicon.BACK_TO_OFFERS_BTN_CL)


class OffersMarkup:
    @classmethod
    def markup_offers(cls, offers: list[tuple[int, str]]) -> InlineKeyboardMarkup:
        keyboard = []

        for _id, name in offers:
            keyboard.append([InlineKeyboardButton(text=name, callback_data=OffersLexicon.OFFER_BTN_CL + str(_id))])

        keyboard.append([MENU_BTN])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def new_offer(cls, _id: int) -> InlineKeyboardMarkup:
        keyboard = []

        NEW_OFFER_YES_BTN = InlineKeyboardButton(text=OffersLexicon.NEW_OFFERS_YES_BTN_TXT, callback_data=OffersLexicon.NEW_OFFERS_YES_BTN_CL + str(_id))
        NEW_OFFER_NO_BTN = InlineKeyboardButton(text=OffersLexicon.NEW_OFFERS_NO_BTN_TXT, callback_data=OffersLexicon.NEW_OFFERS_NO_BTN_CL + str(_id))

        keyboard.append([NEW_OFFER_YES_BTN])
        keyboard.append([NEW_OFFER_NO_BTN])
        # keyboard.append([BACK_BTN])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def active_offer(cls, _id: int) -> InlineKeyboardMarkup:
        keyboard = []

        OFFER_SUCCESS_BTN = InlineKeyboardButton(text=OffersLexicon.OFFERS_SUCCESS_BTN_TXT, callback_data=OffersLexicon.OFFERS_SUCCESS_BTN_CL)
        OFFER_FAILURE_BTN = InlineKeyboardButton(text=OffersLexicon.OFFERS_FAILURE_BTN_TXT, callback_data=OffersLexicon.OFFERS_FAILURE_BTN_CL)

        keyboard.append([OFFER_SUCCESS_BTN])
        keyboard.append([OFFER_FAILURE_BTN])
        keyboard.append([BACK_BTN])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)
