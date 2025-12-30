import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.main import MainConfig


class TelegramConfig:
    load_dotenv(dotenv_path=MainConfig.MAIN_ENV_PATH)

    TELEGRAM_BOT_API_TOKEN: str = os.getenv('TELEGRAM_BOT_API_TOKEN')
    OWNER_CHAT_ID: str = os.getenv('OWNER_CHAT_ID', "")
    ADMIN_CHAT_IDS: set = set(os.getenv('ADMIN_CHAT_IDS', "").split(","))

    if not TELEGRAM_BOT_API_TOKEN:
        exit("TELEGRAM_BOT_API_TOKEN environment variable not set")

    if not OWNER_CHAT_ID:
        exit("OWNER_CHAT_ID environment variable not set")

    try:
        BOT: Bot = Bot(token=TELEGRAM_BOT_API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        DISPATCHER: Dispatcher = Dispatcher()
    except Exception as e:
        exit(f"Telegram Bot Telegram API Error {e}")
