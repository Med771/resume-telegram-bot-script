from addons.decorator import TelegramDecorator


class NotificationTools:
    @classmethod
    @TelegramDecorator.log_call()
    async def check_new_offers(cls):
        ...

    @classmethod
    @TelegramDecorator.log_call()
    async def check_failure_offers(cls):
        ...
