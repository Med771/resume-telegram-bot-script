import aiohttp

from addons.decorator import TelegramDecorator
from tools.logger import LoggerTools

from config import WebConfig

logger = LoggerTools.get_logger(__name__, info=True, warn=True, error=True)


class WebTools:
    @staticmethod
    def _paged_url(url: str, page: int | None = None, size: int | None = None) -> str:
        page_value = WebConfig.REQUEST_PAGE if page is None else page
        size_value = WebConfig.REQUEST_SIZE if size is None else size
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}page={page_value}&size={size_value}"

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
    def _pagination(payload: dict | None) -> tuple[int | None, int | None]:
        if not isinstance(payload, dict):
            return None, None
        page = payload.get("page")
        total_pages = payload.get("totalPages")
        if isinstance(page, int) and isinstance(total_pages, int):
            return page, total_pages
        return None, None

    @staticmethod
    def _cards_payload(payload: dict | list | None) -> dict:
        if isinstance(payload, dict) and isinstance(payload.get("data"), list):
            return {"students": payload["data"]}
        if isinstance(payload, list):
            return {"students": payload}
        return {"students": []}

    @classmethod
    async def _request_filter_collect(cls, payload: dict) -> dict:
        page = WebConfig.REQUEST_PAGE
        max_pages = 200
        offers: list[dict] = []

        async with aiohttp.ClientSession() as session:
            for _ in range(max_pages):
                async with session.post(
                    url=cls._paged_url(WebConfig.REQUEST_FILTER_URL, page=page),
                    headers=WebConfig.HEADERS,
                    cookies=WebConfig.COOKIE,
                    json=payload
                ) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        logger.error(
                            f"request_filter failed: page={page}, status={response.status}, "
                            f"payload={payload}, response={response_text}"
                        )
                        return {"offers": offers}

                    response_payload = await response.json()
                    page_offers = cls._offers_payload(response_payload).get("offers", [])
                    offers.extend(page_offers)

                    current_page, total_pages = cls._pagination(response_payload)
                    if current_page is None or total_pages is None:
                        break
                    if total_pages <= 0 or current_page + 1 >= total_pages:
                        break

                    page = current_page + 1

        return {"offers": offers}

    @classmethod
    async def _student_cards_filter_collect(cls, payload: dict) -> dict:
        page = WebConfig.REQUEST_PAGE
        max_pages = 200
        students: list[dict] = []

        async with aiohttp.ClientSession() as session:
            for _ in range(max_pages):
                async with session.post(
                    url=cls._paged_url(WebConfig.STUDENT_CARDS_FILTER_URL, page=page),
                    headers=WebConfig.HEADERS,
                    cookies=WebConfig.COOKIE,
                    json=payload
                ) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        logger.error(
                            f"student_cards_filter failed: page={page}, status={response.status}, "
                            f"payload={payload}, response={response_text}"
                        )
                        return {"students": students}

                    response_payload = await response.json()
                    page_students = cls._cards_payload(response_payload).get("students", [])
                    students.extend(page_students)

                    current_page, total_pages = cls._pagination(response_payload)
                    if current_page is None or total_pages is None:
                        break
                    if total_pages <= 0 or current_page + 1 >= total_pages:
                        break

                    page = current_page + 1

        return {"students": students}

    @staticmethod
    def _chat_name_from_offer(offer: dict) -> str:
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
    def _extract_chat_response(payload: dict) -> tuple[str, str]:
        if not isinstance(payload, dict):
            return "", ""

        chat_id = (
            payload.get("chat_id", "")
            or payload.get("chatId", "")
            or payload.get("id", "")
        )
        chat_url = (
            payload.get("invite_link", "")
            or payload.get("inviteLink", "")
            or payload.get("chatUrl", "")
            or payload.get("chat_url", "")
            or payload.get("url", "")
        )

        return str(chat_id).strip(), str(chat_url).strip()

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
                    logger.warning(f"referral_link conflict: profile_id={_id}, user_id={user_id}")
                    return 1

                logger.error(
                    f"referral_link failed: profile_id={_id}, user_id={user_id}, status={response.status}"
                )

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

                logger.warning(f"get_sync failed: user_id={user_id}, status={response.status}")

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

                logger.warning(f"get_student failed: student_id={student_id}, status={response.status}")

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

                logger.warning(f"get_recruiter failed: recruiter_id={recruiter_id}, status={response.status}")

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
            results = ["WAITING", "EXPECTATION", "STUDENT_CONFIRMED", "RECRUITER_CONFIRMED"]

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

            return await cls._request_filter_collect(payload=payload)

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
        chat_id: str = "",
    ) -> bool:
        _ = await cls.login()

        payload: dict[str, object] = {"result": status}
        if student_response_text:
            payload["studentResponseText"] = student_response_text
        if has_recruiter_message is not None:
            payload["hasRecruiterMessage"] = has_recruiter_message
        if has_student_message is not None:
            payload["hasStudentMessage"] = has_student_message
        if chat_id:
            payload["chatId"] = str(chat_id).strip()

        logger.info(
            f"set_status request: offer_id={_id}, status={status}, "
            f"hasRecruiterMessage={payload.get('hasRecruiterMessage')}, "
            f"hasStudentMessage={payload.get('hasStudentMessage')}"
        )

        async def _put(update_payload: dict[str, object], attempt: str) -> bool:
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    url=WebConfig.TELEGRAM_UPDATE_URL.format(id=_id),
                    headers=WebConfig.HEADERS,
                    cookies=WebConfig.COOKIE,
                    json=update_payload
                ) as response:
                    if response.status in (200, 204):
                        logger.info(
                            f"set_status success: offer_id={_id}, response_status={response.status}, attempt={attempt}"
                        )
                        return True

                    response_text = await response.text()
                    logger.error(
                        f"set_status failed: offer_id={_id}, response_status={response.status}, "
                        f"attempt={attempt}, payload={update_payload}, response={response_text}"
                    )
                    return False

        if await _put(update_payload=payload, attempt="primary"):
            return True

        # Backend fallback: some environments fail to update boolean flags
        # when full payload includes unchanged result field.
        fallback_payload = dict(payload)
        fallback_payload.pop("result", None)
        if (has_recruiter_message is not None or has_student_message is not None or chat_id) and fallback_payload:
            if await _put(update_payload=fallback_payload, attempt="flags_only"):
                return True

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

                logger.warning(f"get_offer failed: offer_id={_id}, status={response.status}")

        return {}

    @classmethod
    async def get_offers(cls, results=None) -> dict:
        if results is None:
            results = ["SYNC", "WAITING", "EXPECTATION", "STUDENT_CONFIRMED", "RECRUITER_CONFIRMED"]

        _ = await cls.login()
        return await cls._request_filter_collect(payload={"results": results})

    @classmethod
    @TelegramDecorator.log_call()
    async def get_offer_by_chat_id(cls, chat_id: str, results=None) -> dict:
        if not chat_id:
            logger.warning("get_offer_by_chat_id skipped: empty chat_id")
            return {}
        if results is None:
            results = ["EXPECTATION", "STUDENT_CONFIRMED", "RECRUITER_CONFIRMED"]

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
    @TelegramDecorator.log_call()
    async def get_student_cards(cls, filters: dict | None = None) -> dict:
        _ = await cls.login()
        payload = filters if isinstance(filters, dict) else {}
        return await cls._student_cards_filter_collect(payload=payload)

    @classmethod
    @TelegramDecorator.log_call()
    async def get_similar_students_by_offer(cls, offer: dict, limit: int = 5) -> list[dict]:
        if not isinstance(offer, dict):
            return []

        current_student_id = str(offer.get("studentId", "") or "").strip()
        if not current_student_id:
            return []

        current_student = await cls.get_student(student_id=current_student_id)
        if not current_student:
            return []

        speciality_id = current_student.get("specialityId")
        skills = current_student.get("skills", [])
        skill_ids: list[int] = []
        if isinstance(skills, list):
            for skill in skills:
                if isinstance(skill, dict) and isinstance(skill.get("id"), int):
                    skill_ids.append(skill["id"])

        filters_primary: dict = {}
        if isinstance(speciality_id, int):
            filters_primary["specialitiesIds"] = [speciality_id]
        if skill_ids:
            filters_primary["skillsIds"] = skill_ids[:10]

        candidates: list[dict] = []
        if filters_primary:
            cards_payload = await cls.get_student_cards(filters=filters_primary)
            candidates = cards_payload.get("students", [])

        if not candidates:
            speciality_text = str(current_student.get("speciality", "")).strip()
            if speciality_text:
                cards_payload = await cls.get_student_cards(filters={"findString": speciality_text})
                candidates = cards_payload.get("students", [])

        unique_students: list[dict] = []
        used_ids: set[str] = set()
        for student in candidates:
            student_id = str(student.get("id", "")).strip()
            if not student_id or student_id == current_student_id or student_id in used_ids:
                continue
            used_ids.add(student_id)
            unique_students.append(student)
            if len(unique_students) >= limit:
                break

        return unique_students

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
            "cookies": WebConfig.COOKIE,
            # Some chat services require this body regardless of URL format.
            "json": {"chat_name": cls._chat_name_from_offer(offer=source_offer)}
        }

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(**request_kwargs) as response:
                    if response.status in (200, 201):
                        try:
                            payload = await response.json()
                        except Exception:
                            response_text = await response.text()
                            logger.error(
                                f"create_chat invalid json: offer_id={_id}, status={response.status}, "
                                f"response={response_text}"
                            )
                            return {}

                        if isinstance(payload, dict):
                            chat_id, chat_url = cls._extract_chat_response(payload)
                            if chat_id or chat_url:
                                merged_offer = dict(source_offer)
                                if chat_url:
                                    merged_offer["chatUrl"] = chat_url
                                if chat_id:
                                    merged_offer["chatId"] = chat_id
                                return merged_offer
                            return payload

                    logger.error(f"create_chat failed: offer_id={_id}, status={response.status}")
                    try:
                        logger.error(f"create_chat response: offer_id={_id}, response={await response.text()}")
                    except Exception:
                        pass
        except aiohttp.ClientError as ex:
            logger.error(
                f"create_chat network error: offer_id={_id}, url={request_url}, error={type(ex).__name__}: {ex}"
            )
        except TimeoutError:
            logger.error(f"create_chat timeout: offer_id={_id}, url={request_url}")

        return {}
