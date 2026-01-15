from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from addons.lexicon import OffersLexicon, QueryLexicon, MenuLexicon

BACK_BTN = InlineKeyboardButton(text=MenuLexicon.BACK_BTN_TXT, callback_data=MenuLexicon.BACK_BTN_CL)

OFFERS_BTN = InlineKeyboardButton(text=OffersLexicon.OFFERS_BTN_TXT, callback_data=OffersLexicon.OFFERS_BTN_CL)
QUERY_BTN = InlineKeyboardButton(text=QueryLexicon.QUERY_BTN_TXT, callback_data=QueryLexicon.QUERY_BTN_CL)


class MenuMarkup:
    back_markup = InlineKeyboardMarkup(inline_keyboard=[[BACK_BTN]])

    offers_markup = InlineKeyboardMarkup(inline_keyboard=[[OFFERS_BTN]])
    query_markup = ReplyKeyboardRemove() # InlineKeyboardMarkup(inline_keyboard=[[QUERY_BTN]])
