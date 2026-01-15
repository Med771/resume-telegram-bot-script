from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from addons.lexicon import OffersLexicon, MenuLexicon

BACK_BTN = InlineKeyboardButton(text=MenuLexicon.BACK_BTN_TXT, callback_data=MenuLexicon.BACK_BTN_CL)


class OffersMarkup:
    @classmethod
    def markup_offers(cls, offers: list[tuple[int, str]]) -> InlineKeyboardMarkup:
        keyboard = [[]]

        for _id, name in offers:
            keyboard.append([InlineKeyboardButton(text=name, callback_data=OffersLexicon.OFFER_BTN_CL + str(_id))])

        keyboard.append([BACK_BTN])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)
