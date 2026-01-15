import aiohttp

from addons.decorator import TelegramDecorator

from config import WebConfig


class WebTools:
    @classmethod
    @TelegramDecorator.log_call()
    async def login(cls):
        async with aiohttp.ClientSession() as session:
            async with session.post(WebConfig.LOGIN_URL, json=WebConfig.LOGIN_DATA, headers=WebConfig.HEADERS) as response:
                print("Login status:", response.status)

                WebConfig.COOKIE = response.cookies

    @classmethod
    @TelegramDecorator.log_call()
    async def referral_link(cls, is_stud: bool, _id: str, user_id: str) -> int:
        _ = await cls.login()

        async with (aiohttp.ClientSession() as session):
            async with session.post(
                    url=WebConfig.SET_STUD_URL.format(id=_id) if is_stud else WebConfig.SET_REC_URL.format(id=_id),
                    headers=WebConfig.HEADERS,
                    json={"telegramUserId": user_id},
                    cookies=WebConfig.COOKIE
            ) as response:
                print(WebConfig.SET_STUD_URL.format(id=_id) if is_stud else WebConfig.SET_REC_URL.format(id=_id))

                if response.status == 200:
                    return 2
                if response.status == 400:
                    print(await response.text())

                    return 1

                print("Referral status:", response.status)

        return 0

    @classmethod
    @TelegramDecorator.log_call()
    async def get_stud_by_id(cls, user_id: str) -> bool:
        _ = await cls.login()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=WebConfig.GET_STUD_INFO_URL.format(id=user_id),
                cookies=WebConfig.COOKIE
            ) as response:

                print(WebConfig.GET_STUD_INFO_URL.format(id=user_id))
                print(await response.text())

                if response.status == 200:
                    return True

                print("Get stud info URL status:", response.status)

        return False

    @classmethod
    @TelegramDecorator.log_call()
    async def get_rec_by_id(cls, user_id: str) -> bool:
        _ = await cls.login()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=WebConfig.GET_REC_INFO_URL.format(id=user_id),
                cookies=WebConfig.COOKIE
            ) as response:

                if response.status == 200:
                    return True

                print("Get rec info URL status:", response.status)

        return False
