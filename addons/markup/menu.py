from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from addons.lexicon import OffersLexicon, MenuLexicon

BACK_BTN = InlineKeyboardButton(text=MenuLexicon.BACK_BTN_TXT, callback_data=MenuLexicon.BACK_BTN_CL)

OFFERS_BTN = InlineKeyboardButton(text=OffersLexicon.OFFERS_BTN_TXT, callback_data=OffersLexicon.OFFERS_BTN_CL)
PROFILE_BTN = InlineKeyboardButton(text=MenuLexicon.PROFILE_BTN_TXT, callback_data=MenuLexicon.PROFILE_BTN_CL)
MAIN_MENU_MARKUP = InlineKeyboardMarkup(inline_keyboard=[[OFFERS_BTN], [PROFILE_BTN]])

class MenuMarkup:
    back_markup = InlineKeyboardMarkup(inline_keyboard=[[BACK_BTN]])

    student_markup = MAIN_MENU_MARKUP
    employer_markup = MAIN_MENU_MARKUP
