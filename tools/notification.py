import asyncio

from addons.decorator import TelegramDecorator
from addons.lexicon import OffersLexicon
from addons.markup import OffersMarkup

from tools.logger import LoggerTools
from tools.web import WebTools

from config import TelegramConfig

bot = TelegramConfig.BOT
logger = LoggerTools.get_logger(__name__, info=True, warn=True, error=True)


class NotificationTools:
    @staticmethod
    def _student_chat_id(offer: dict) -> str:
        return offer.get("studentRes", {}).get("chatId", "") or offer.get("studentTelegramUserId", "")

    @staticmethod
    def _company_name(offer: dict) -> str:
        return offer.get("recruiterRes", {}).get("companyName", "") or offer.get("companyName", "")

    @staticmethod
    def _recruiter_name(offer: dict) -> str:
        return offer.get("recruiterRes", {}).get("fullName", "") or offer.get("recruiterName", "") or "Работодатель"

    @staticmethod
    def _speciality(offer: dict) -> str:
        return offer.get("studentRes", {}).get("speciality", "") or offer.get("studentSpeciality", "") or "Не указано"

    @classmethod
    @TelegramDecorator.log_call()
    async def check_new_offers(cls):
        logger.info("notifications.check_new_offers started")

        offers: dict = await WebTools.get_offers(results=["SYNC"])
        update_results = []
        sent_count = 0
        skipped_count = 0

        for offer in offers.get("offers", []):
            detailed_offer = await WebTools.enrich_offer(offer=offer)
            if not detailed_offer:
                detailed_offer = offer

            chat_id = cls._student_chat_id(offer=detailed_offer)
            offer_id = offer.get("id")
            if not chat_id or offer_id is None:
                skipped_count += 1
                logger.warning(
                    f"notifications.check_new_offers skipped offer: offer_id={offer_id}, "
                    f"student_chat_id={chat_id}"
                )
                await asyncio.sleep(0.3)
                continue

            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=OffersLexicon.OFFER_TO_STUDENT_MSG.format(
                        company_name=cls._company_name(offer=detailed_offer),
                        recruiter_name=cls._recruiter_name(offer=detailed_offer),
                        speciality=cls._speciality(offer=detailed_offer)
                    ),
                    reply_markup=OffersMarkup.new_offer(offer_id),
                )
            except Exception as ex:
                logger.error(
                    f"notifications.check_new_offers send failed: offer_id={offer_id}, "
                    f"chat_id={chat_id}, error={ex}"
                )
                await asyncio.sleep(0.3)
                continue

            sent_count += 1
            logger.info(f"notifications.check_new_offers sent: offer_id={offer_id}, chat_id={chat_id}")
            update_results.append((offer_id, "WAITING"))

            await asyncio.sleep(0.3)

        if update_results:
            batch_result = await WebTools.batch_update(update_results)
            logger.info(
                f"notifications.check_new_offers status update: requested={len(update_results)}, "
                f"updated={batch_result.get('updated', 0)}"
            )

        logger.info(
            f"notifications.check_new_offers finished: total={len(offers.get('offers', []))}, "
            f"sent={sent_count}, skipped={skipped_count}"
        )


    @classmethod
    @TelegramDecorator.log_call()
    async def check_failure_offers(cls):
        logger.info("notifications.audit_statuses started")

        waiting_offers = await WebTools.get_offers(results=["WAITING"])
        expectation_offers = await WebTools.get_offers(results=["EXPECTATION"])
        refusal_offers = await WebTools.get_offers(results=["REFUSAL"])

        waiting_no_response = 0
        waiting_total = 0
        for offer in waiting_offers.get("offers", []):
            waiting_total += 1
            if not offer.get("studentResponseText"):
                waiting_no_response += 1

        expectation_total = 0
        expectation_silent = 0
        for offer in expectation_offers.get("offers", []):
            expectation_total += 1
            has_recruiter_message = bool(offer.get("hasRecruiterMessage"))
            has_student_message = bool(offer.get("hasStudentMessage"))
            if not has_recruiter_message and not has_student_message:
                expectation_silent += 1

        refusal_total = len(refusal_offers.get("offers", []))

        logger.info(
            f"notifications.audit_statuses summary: waiting_total={waiting_total}, "
            f"waiting_no_response={waiting_no_response}, expectation_total={expectation_total}, "
            f"expectation_silent={expectation_silent}, refusal_total={refusal_total}"
        )
