import asyncio

from addons.decorator import TelegramDecorator
from addons.lexicon import OffersLexicon
from addons.markup import OffersMarkup

from tools.web import WebTools

from config import TelegramConfig

bot = TelegramConfig.BOT


class NotificationTools:
    @classmethod
    @TelegramDecorator.log_call()
    async def check_new_offers(cls):
        print("Checking new offers")

        offers: dict = await WebTools.get_offers(results=["SYNC"])
        update_results = []

        for offer in offers.get("offers", []):
            if "studentRes" in offer and "chatId" in offer["studentRes"]:

                await bot.send_message(
                    chat_id=offer["studentRes"]["chatId"],
                    text=OffersLexicon.OFFER_TO_STUDENT_MSG.format(
                        company_name=offer["recruiterRes"]["companyName"],
                        recruiter_name=offer["recruiterRes"]["fullName"],
                        speciality=offer["studentRes"]["speciality"]
                    ),
                    reply_markup=OffersMarkup.new_offer(offer["id"]),
                )

                update_results.append((offer["id"], "WAITING"))

            await asyncio.sleep(0.3)

        if update_results:
            await WebTools.batch_update(update_results)


    @classmethod
    @TelegramDecorator.log_call()
    async def check_failure_offers(cls):
        ...
