from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from addons.lexicon import OffersLexicon, QueryLexicon

OFFERS_BTN = InlineKeyboardButton(text=OffersLexicon.OFFERS_BTN_TXT, callback_data=OffersLexicon.OFFERS_BTN_CL)
QUERY_BTN = InlineKeyboardButton(text=QueryLexicon.QUERY_BTN_TXT, callback_data=QueryLexicon.QUERY_BTN_CL)


class MenuMarkup:
    offers_markup = InlineKeyboardMarkup(inline_keyboard=[[OFFERS_BTN]])
    query_markup = ReplyKeyboardRemove() # InlineKeyboardMarkup(inline_keyboard=[[QUERY_BTN]])
