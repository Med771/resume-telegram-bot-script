from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from addons.lexicon import MenuLexicon, OffersLexicon, QueryLexicon

BACK_BTN = KeyboardButton(text=MenuLexicon.BACK_BTN_TXT)
OFFERS_BTN = KeyboardButton(text=OffersLexicon.OFFERS_BTN_TXT)
QUERY_BTN = KeyboardButton(text=QueryLexicon.QUERY_BTN_TXT)


class MenuMarkup:
    back_markup = ReplyKeyboardMarkup(keyboard=[[BACK_BTN]], resize_keyboard=True)

    offers_markup = ReplyKeyboardMarkup(keyboard=[[OFFERS_BTN]], resize_keyboard=True)
    query_markup = ReplyKeyboardMarkup(keyboard=[[QUERY_BTN]], resize_keyboard=True)
