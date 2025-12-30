import aiohttp

from addons.decorator import TelegramDecorator

from config import BackendConfig


class BackendTools:
    @classmethod
    @TelegramDecorator.log_call()
    async def login(cls):
        async with aiohttp.ClientSession() as session:
            async with session.post(BackendConfig.LOGIN_URL, json=BackendConfig.LOGIN_DATA, headers=BackendConfig.HEADERS) as response:
                print("Login status:", response.status)

                BackendConfig.COOKIE = response.cookies

    @classmethod
    @TelegramDecorator.log_call()
    async def referral_link(cls, _id: str, user_id: str) -> bool:
        _ = await cls.login()

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    BackendConfig.SET_URL.format(id=_id),
                    headers=BackendConfig.HEADERS,
                    json={"telegramUserId": user_id},
                    cookies=BackendConfig.COOKIE) as response:
                try:
                    if response.status == 200:
                        return True
                except Exception:
                    print("Set status:", response.status)

        return False
