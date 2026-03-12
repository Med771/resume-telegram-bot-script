from aiogram.types import Message

from addons.decorator import TelegramDecorator
from addons.lexicon import ChatLexicon

from config import TelegramConfig

from tools.logger import LoggerTools
from tools.web import WebTools

bot = TelegramConfig.BOT
logger = LoggerTools.get_logger(__name__, info=True, warn=True, error=True)


class ChatService:
    @staticmethod
    def _result(offer: dict) -> str:
        return offer.get("result", "") or offer.get("resultEnum", "")

    @staticmethod
    def _recruiter_chat_id(offer: dict) -> str:
        recruiter_res = offer.get("recruiterRes") or {}
        chat_id = recruiter_res.get("chatId", "") or offer.get("recruiterTelegramUserId", "")
        return str(chat_id).strip()

    @staticmethod
    def _student_chat_id(offer: dict) -> str:
        student_res = offer.get("studentRes") or {}
        chat_id = student_res.get("chatId", "") or offer.get("studentTelegramUserId", "")
        return str(chat_id).strip()

    @classmethod
    async def _resolve_actor_role(
        cls,
        sender_id: str,
        offer: dict,
        offer_id: int
    ) -> str:
        recruiter_chat_id = cls._recruiter_chat_id(offer=offer)
        student_chat_id = cls._student_chat_id(offer=offer)
        offer_student_id = str(offer.get("studentId", "")).strip()
        offer_recruiter_id = str(offer.get("recruiterId", "")).strip()

        if sender_id == recruiter_chat_id:
            return "recruiter"
        if sender_id == student_chat_id:
            return "student"

        sync_payload = await WebTools.get_sync(user_id=sender_id)
        sync_type = str(sync_payload.get("type", "")).strip()
        sync_profile_id = str(sync_payload.get("id", "")).strip()

        if sync_type == "re":
            if sync_profile_id and offer_recruiter_id and sync_profile_id == offer_recruiter_id:
                logger.warning(
                    f"chat_activity_msg role resolved by sync profile: offer_id={offer_id}, "
                    f"sender_id={sender_id}, role=recruiter"
                )
                return "recruiter"
            if not offer_recruiter_id:
                logger.warning(
                    f"chat_activity_msg role resolved by sync type fallback: offer_id={offer_id}, "
                    f"sender_id={sender_id}, role=recruiter"
                )
                return "recruiter"

        if sync_type == "st":
            if sync_profile_id and offer_student_id and sync_profile_id == offer_student_id:
                logger.warning(
                    f"chat_activity_msg role resolved by sync profile: offer_id={offer_id}, "
                    f"sender_id={sender_id}, role=student"
                )
                return "student"
            if not offer_student_id:
                logger.warning(
                    f"chat_activity_msg role resolved by sync type fallback: offer_id={offer_id}, "
                    f"sender_id={sender_id}, role=student"
                )
                return "student"

        return ""

    @classmethod
    async def send_chat_rules(cls, chat_id: str) -> bool:
        if not chat_id:
            return False
        try:
            await bot.send_message(chat_id=chat_id, text=ChatLexicon.CHAT_RULES_MSG)
            logger.info(f"chat rules sent: chat_id={chat_id}")
            return True
        except Exception as ex:
            logger.error(f"chat rules send failed: chat_id={chat_id}, error={ex}")
            return False

    @classmethod
    async def create_offer_chat(cls, offer_id: int) -> dict:
        payload = await WebTools.create_chat(_id=offer_id)
        if not isinstance(payload, dict):
            return {}

        chat_id = str(payload.get("chatId", "") or payload.get("chat_id", "")).strip()
        if chat_id:
            await cls.send_chat_rules(chat_id=chat_id)
        else:
            logger.warning(f"create_offer_chat created without chat_id: offer_id={offer_id}")
        return payload

    @classmethod
    @TelegramDecorator.log_call()
    async def chat_activity_msg(cls, message: Message):
        chat_id = str(message.chat.id)
        sender_id = str(message.from_user.id) if message.from_user else ""
        if not chat_id or not sender_id:
            logger.warning("chat_activity_msg skipped: empty chat_id or sender_id")
            return

        logger.info(
            f"chat_activity_msg received: chat_id={chat_id}, sender_id={sender_id}, "
            f"message_id={message.message_id}"
        )

        offer = await WebTools.get_offer_by_chat_id(chat_id=chat_id)
        if not offer:
            # Fallback for old offers where chatId was not persisted yet.
            sender_offers = await WebTools.get_offers_by_id(
                is_stud=True,
                chat_id=sender_id,
                results=["EXPECTATION", "STUDENT_CONFIRMED", "RECRUITER_CONFIRMED"]
            )
            sender_active_offers = sender_offers.get("offers", [])
            if len(sender_active_offers) == 1:
                offer = sender_active_offers[0]
                logger.warning(
                    f"chat_activity_msg fallback offer by sender: chat_id={chat_id}, sender_id={sender_id}, "
                    f"offer_id={offer.get('id')}"
                )
            else:
                logger.warning(
                    f"chat_activity_msg no active offer: chat_id={chat_id}, sender_id={sender_id}, "
                    f"sender_offers={len(sender_active_offers)}"
                )
                return

        enriched_offer = await WebTools.enrich_offer(offer=offer)
        if enriched_offer:
            offer = enriched_offer

        offer_id = offer.get("id")
        if offer_id is None:
            logger.error(f"chat_activity_msg invalid offer without id: chat_id={chat_id}")
            return

        current_result = cls._result(offer=offer) or "EXPECTATION"
        actor_role = await cls._resolve_actor_role(sender_id=sender_id, offer=offer, offer_id=offer_id)

        if actor_role == "recruiter":
            if offer.get("hasRecruiterMessage") is True:
                logger.info(f"chat_activity_msg recruiter flag already true: offer_id={offer_id}")
                return
            updated = await WebTools.set_status(
                _id=offer_id,
                status=current_result,
                has_recruiter_message=True,
                chat_id=chat_id
            )
            logger.info(
                f"chat_activity_msg recruiter update: offer_id={offer_id}, updated={updated}, "
                f"sender_id={sender_id}"
            )
            return

        if actor_role == "student":
            if offer.get("hasStudentMessage") is True:
                logger.info(f"chat_activity_msg student flag already true: offer_id={offer_id}")
                return
            updated = await WebTools.set_status(
                _id=offer_id,
                status=current_result,
                has_student_message=True,
                chat_id=chat_id
            )
            logger.info(
                f"chat_activity_msg student update: offer_id={offer_id}, updated={updated}, "
                f"sender_id={sender_id}"
            )
            return

        logger.warning(
            f"chat_activity_msg sender is not participant: offer_id={offer_id}, sender_id={sender_id}, "
            f"student_chat_id={cls._student_chat_id(offer=offer)}, recruiter_chat_id={cls._recruiter_chat_id(offer=offer)}, "
            f"offer_student_id={str(offer.get('studentId', '')).strip()}, offer_recruiter_id={str(offer.get('recruiterId', '')).strip()}"
        )
