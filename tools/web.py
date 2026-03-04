import aiohttp

from addons.decorator import TelegramDecorator
from tools.logger import LoggerTools

from config import WebConfig

logger = LoggerTools.get_logger(__name__, info=True, warn=True, error=True)


class WebTools:
    @staticmethod
    def _paged_url(url: str) -> str:
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}page={WebConfig.REQUEST_PAGE}&size={WebConfig.REQUEST_SIZE}"

    @staticmethod
    def _offers_payload(payload: dict | list | None) -> dict:
        if isinstance(payload, dict):
            if isinstance(payload.get("offers"), list):
                return {"offers": payload["offers"]}
            if isinstance(payload.get("data"), list):
                return {"offers": payload["data"]}
            if isinstance(payload.get("requests"), list):
                return {"offers": payload["requests"]}
        if isinstance(payload, list):
            return {"offers": payload}
        return {"offers": []}

    @staticmethod
    def _chat_name_from_offer(offer: dict, offer_id: int) -> str:
        company_name = (
            offer.get("recruiterRes", {}).get("companyName", "")
            or offer.get("companyName", "")
            or "Не указано"
        )
        student_name = (
            offer.get("studentRes", {}).get("fullName", "")
            or offer.get("studentFullName", "")
            or "Не указано"
        )
        return f"Оффер | Студент: {student_name} | Компания: {company_name}"

    @staticmethod
    def _full_name(first_name: str, last_name: str) -> str:
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        return full_name

    @classmethod
    def _normalize_student(cls, payload: dict) -> dict:
        speciality = payload.get("speciality", "")
        if isinstance(speciality, dict):
            speciality = speciality.get("name", "") or speciality.get("title", "")

        skills = payload.get("skills", [])
        skill_names: list[str] = []
        if isinstance(skills, list):
            for skill in skills:
                if isinstance(skill, dict):
                    skill_name = str(skill.get("name", "")).strip()
                    if skill_name:
                        skill_names.append(skill_name)
                elif isinstance(skill, str):
                    skill_name = skill.strip()
                    if skill_name:
                        skill_names.append(skill_name)

        normalized = dict(payload)
        normalized["fullName"] = cls._full_name(
            str(payload.get("firstName", "")).strip(),
            str(payload.get("lastName", "")).strip()
        )
        normalized["speciality"] = str(speciality or "").strip()
        normalized["skillsNames"] = skill_names
        normalized["skillsText"] = ", ".join(skill_names)
        return normalized

    @classmethod
    def _normalize_recruiter(cls, payload: dict) -> dict:
        normalized = dict(payload)
        normalized["fullName"] = cls._full_name(
            str(payload.get("firstName", "")).strip(),
            str(payload.get("lastName", "")).strip()
        )
        normalized["companyName"] = str(payload.get("companyName", "")).strip()
        normalized["email"] = str(payload.get("email", "")).strip()
        normalized["phoneNumber"] = str(payload.get("phoneNumber", "")).strip()
        return normalized

    @classmethod
    def _merge_offer_with_entities(cls, offer: dict, student: dict, recruiter: dict) -> dict:
        merged = dict(offer)
        student_res = dict(offer.get("studentRes", {}))
        recruiter_res = dict(offer.get("recruiterRes", {}))

        if student:
            if not student_res.get("fullName"):
                student_res["fullName"] = student.get("fullName", "")
            if not student_res.get("speciality"):
                student_res["speciality"] = student.get("speciality", "")

        if recruiter:
            if not recruiter_res.get("fullName"):
                recruiter_res["fullName"] = recruiter.get("fullName", "")
            if not recruiter_res.get("companyName"):
                recruiter_res["companyName"] = recruiter.get("companyName", "")
            if not recruiter_res.get("chatId"):
                recruiter_res["chatId"] = recruiter.get("telegramUserId", "")

        if offer.get("studentTelegramUserId"):
            if not student_res.get("chatId"):
                student_res["chatId"] = offer.get("studentTelegramUserId", "")
        if offer.get("recruiterTelegramUserId"):
            if not recruiter_res.get("chatId"):
                recruiter_res["chatId"] = offer.get("recruiterTelegramUserId", "")

        merged["studentRes"] = student_res
        merged["recruiterRes"] = recruiter_res
        return merged

    @classmethod
    @TelegramDecorator.log_call()
    async def login(cls):
        async with aiohttp.ClientSession() as session:
            async with session.post(WebConfig.LOGIN_URL, json=WebConfig.LOGIN_DATA, headers=WebConfig.HEADERS) as response:
                WebConfig.COOKIE = response.cookies

    @classmethod
    @TelegramDecorator.log_call()
    async def referral_link(cls, is_stud: bool, _id: str, user_id: str) -> int:
        _ = await cls.login()

        req_type = "st" if is_stud else "re"
        payload = {"userId": user_id, "type": req_type}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=WebConfig.SYNC_SET_URL.format(id=_id),
                headers=WebConfig.HEADERS,
                json=payload,
                cookies=WebConfig.COOKIE
            ) as response:
                if response.status in (200, 204):
                    return 2
                if response.status == 400:
                    print(await response.text())
                    return 1

                print("Referral status:", response.status)

        return 0

    @classmethod
    @TelegramDecorator.log_call()
    async def get_sync(cls, user_id: str) -> dict:
        _ = await cls.login()

        if not WebConfig.SYNC_GET_URL:
            return {}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=WebConfig.SYNC_GET_URL.format(id=user_id),
                headers=WebConfig.HEADERS,
                cookies=WebConfig.COOKIE
            ) as response:
                if response.status == 200:
                    payload = await response.json()
                    if isinstance(payload, dict):
                        return payload

                print("Get sync URL status:", response.status)

        return {}

    @classmethod
    @TelegramDecorator.log_call()
    async def get_student(cls, student_id: str) -> dict:
        _ = await cls.login()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=WebConfig.STUDENT_URL.format(id=student_id),
                headers=WebConfig.HEADERS,
                cookies=WebConfig.COOKIE
            ) as response:
                if response.status == 200:
                    payload = await response.json()
                    if isinstance(payload, dict):
                        return cls._normalize_student(payload)

                print("Get student URL status:", response.status)

        return {}

    @classmethod
    @TelegramDecorator.log_call()
    async def get_recruiter(cls, recruiter_id: str) -> dict:
        _ = await cls.login()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=WebConfig.RECRUITER_URL.format(id=recruiter_id),
                headers=WebConfig.HEADERS,
                cookies=WebConfig.COOKIE
            ) as response:
                if response.status == 200:
                    payload = await response.json()
                    if isinstance(payload, dict):
                        return cls._normalize_recruiter(payload)

                print("Get recruiter URL status:", response.status)

        return {}

    @classmethod
    @TelegramDecorator.log_call()
    async def get_profile_by_chat_id(cls, chat_id: str) -> dict:
        sync_payload = await cls.get_sync(user_id=chat_id)
        if not sync_payload:
            return {}

        profile_type = sync_payload.get("type", "")
        profile_id = sync_payload.get("id", "")

        if not profile_id:
            return {}

        if profile_type == "st":
            return {"type": "st", "data": await cls.get_student(student_id=profile_id)}
        if profile_type == "re":
            return {"type": "re", "data": await cls.get_recruiter(recruiter_id=profile_id)}

        return {}

    @classmethod
    @TelegramDecorator.log_call()
    async def enrich_offer(cls, offer: dict) -> dict:
        if not isinstance(offer, dict):
            return {}

        student_id = str(offer.get("studentId", "") or "").strip()
        recruiter_id = str(offer.get("recruiterId", "") or "").strip()

        student = await cls.get_student(student_id=student_id) if student_id else {}
        recruiter = await cls.get_recruiter(recruiter_id=recruiter_id) if recruiter_id else {}

        return cls._merge_offer_with_entities(offer=offer, student=student, recruiter=recruiter)

    @classmethod
    @TelegramDecorator.log_call()
    async def get_stud_by_id(cls, user_id: str) -> bool:
        sync_payload = await cls.get_sync(user_id=user_id)
        return sync_payload.get("type") == "st" if sync_payload else False

    @classmethod
    @TelegramDecorator.log_call()
    async def get_rec_by_id(cls, user_id: str) -> bool:
        sync_payload = await cls.get_sync(user_id=user_id)
        return sync_payload.get("type") == "re" if sync_payload else False

    @classmethod
    @TelegramDecorator.log_call()
    async def get_offers_by_id(cls, is_stud: bool, chat_id: str, results=None) -> dict:
        if results is None:
            results = ["WAITING", "EXPECTATION"]

        _ = await cls.login()

        sync_payload = await cls.get_sync(user_id=chat_id)

        if sync_payload.get("id"):
            payload = {"results": results}
            if sync_payload.get("type") == "st":
                payload["studentId"] = sync_payload["id"]
            elif sync_payload.get("type") == "re":
                payload["recruiterId"] = sync_payload["id"]
            else:
                return {"offers": []}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=cls._paged_url(WebConfig.REQUEST_FILTER_URL),
                    headers=WebConfig.HEADERS,
                    cookies=WebConfig.COOKIE,
                    json=payload
                ) as response:
                    if response.status == 200:
                        return cls._offers_payload(await response.json())

                    print("Request filter URL status:", response.status)
                    return {"offers": []}

        return {"offers": []}


    @classmethod
    @TelegramDecorator.log_call()
    async def set_status(
        cls,
        _id: int,
        status: str,
        student_response_text: str = "",
        has_recruiter_message: bool | None = None,
        has_student_message: bool | None = None,
    ) -> bool:
        _ = await cls.login()

        payload: dict[str, object] = {"result": status}
        if student_response_text:
            payload["studentResponseText"] = student_response_text
        if has_recruiter_message is not None:
            payload["hasRecruiterMessage"] = has_recruiter_message
        if has_student_message is not None:
            payload["hasStudentMessage"] = has_student_message

        logger.info(
            f"set_status request: offer_id={_id}, status={status}, "
            f"hasRecruiterMessage={payload.get('hasRecruiterMessage')}, "
            f"hasStudentMessage={payload.get('hasStudentMessage')}"
        )

        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=WebConfig.TELEGRAM_UPDATE_URL.format(id=_id),
                headers=WebConfig.HEADERS,
                cookies=WebConfig.COOKIE,
                json=payload
            ) as response:

                if response.status in (200, 204):
                    logger.info(f"set_status success: offer_id={_id}, response_status={response.status}")
                    return True

                print("Update telegram request URL status:", response.status)
                response_text = await response.text()
                logger.error(
                    f"set_status failed: offer_id={_id}, response_status={response.status}, "
                    f"payload={payload}, response={response_text}"
                )

        return False

    @classmethod
    @TelegramDecorator.log_call()
    async def get_offer(cls, _id: int) -> dict:
        _ = await cls.login()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=WebConfig.REQUEST_URL.format(id=_id),
                headers=WebConfig.HEADERS,
                cookies=WebConfig.COOKIE,
            ) as response:

                if response.status == 200:
                    return await response.json()

                print("Get request URL status:", response.status)

        return {}

    @classmethod
    async def get_offers(cls, results=None) -> dict:
        if results is None:
            results = ["SYNC", "WAITING", "EXPECTATION"]

        _ = await cls.login()

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=cls._paged_url(WebConfig.REQUEST_FILTER_URL),
                headers=WebConfig.HEADERS,
                cookies=WebConfig.COOKIE,
                json={"results": results}) as response:

                if response.status == 200:
                    return cls._offers_payload(await response.json())

                print("Get offers URL status:", response.status)

        return {"offers": []}

    @classmethod
    @TelegramDecorator.log_call()
    async def get_offer_by_chat_id(cls, chat_id: str, results=None) -> dict:
        if not chat_id:
            logger.warning("get_offer_by_chat_id skipped: empty chat_id")
            return {}
        if results is None:
            results = ["EXPECTATION"]

        offers_payload = await cls.get_offers(results=results)
        offers = offers_payload.get("offers", [])
        logger.info(
            f"get_offer_by_chat_id lookup: chat_id={chat_id}, results={results}, offers_count={len(offers)}"
        )
        for offer in offers:
            offer_chat_id = str(offer.get("chatId", "") or offer.get("chat_id", "")).strip()
            if offer_chat_id == str(chat_id).strip():
                logger.info(
                    f"get_offer_by_chat_id found: chat_id={chat_id}, offer_id={offer.get('id')}, "
                    f"result={offer.get('result')}"
                )
                return offer

        logger.warning(f"get_offer_by_chat_id not found: chat_id={chat_id}, results={results}")
        return {}

    @classmethod
    async def batch_update(cls, results: list[tuple[int, str]]):
        updated = 0

        for _id, status in results:
            if await cls.set_status(_id=_id, status=status):
                updated += 1

        return {"updated": updated}

    @classmethod
    async def create_chat(cls, _id: int) -> dict:
        _ = await cls.login()
        offer = await cls.get_offer(_id=_id)
        enriched_offer = await cls.enrich_offer(offer=offer)
        source_offer = enriched_offer if enriched_offer else offer
        create_chat_url = WebConfig.CREATE_CHAT_URL
        request_url = create_chat_url.format(id=_id) if "{id}" in create_chat_url else create_chat_url

        request_kwargs: dict = {
            "url": request_url,
            "headers": WebConfig.HEADERS,
            "cookies": WebConfig.COOKIE
        }
        if "{id}" not in create_chat_url:
            request_kwargs["json"] = {"chat_name": cls._chat_name_from_offer(offer=source_offer, offer_id=_id)}

        async with aiohttp.ClientSession() as session:
            async with session.post(**request_kwargs) as response:

                if response.status == 200:
                    payload = await response.json()
                    if isinstance(payload, dict) and payload.get("invite_link"):
                        merged_offer = dict(source_offer)
                        merged_offer["chatUrl"] = payload.get("invite_link", "")
                        merged_offer["chatId"] = payload.get("chat_id", "")
                        return merged_offer
                    if isinstance(payload, dict):
                        return payload

                print("Create chat URL status:", response.status)
                try:
                    print("Create chat response:", await response.text())
                except Exception:
                    pass

        return {}
