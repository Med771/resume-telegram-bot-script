import os

from dotenv import load_dotenv

from config.main import MainConfig


class WebConfig:
    load_dotenv(dotenv_path=MainConfig.MAIN_ENV_PATH)

    API_BASE_URL: str = os.getenv("API_BASE_URL", "").rstrip("/")
    CHAT_API_BASE_URL: str = os.getenv("CHAT_API_BASE_URL", "").rstrip("/")

    LOGIN_URL: str = os.getenv("LOGIN_URL", f"{API_BASE_URL}/auth/login" if API_BASE_URL else "")
    SYNC_SET_URL: str = os.getenv("SYNC_SET_URL", f"{API_BASE_URL}/sync/{{id}}" if API_BASE_URL else "")
    SYNC_GET_URL: str = os.getenv("SYNC_GET_URL", f"{API_BASE_URL}/sync/{{id}}" if API_BASE_URL else "")
    REQUEST_FILTER_URL: str = os.getenv("REQUEST_FILTER_URL", f"{API_BASE_URL}/request/filter" if API_BASE_URL else "")
    REQUEST_URL: str = os.getenv("REQUEST_URL", f"{API_BASE_URL}/request/{{id}}" if API_BASE_URL else "")
    TELEGRAM_UPDATE_URL: str = os.getenv("TELEGRAM_UPDATE_URL", f"{API_BASE_URL}/telegram/{{id}}" if API_BASE_URL else "")
    CREATE_CHAT_URL: str = os.getenv(
        "CREATE_CHAT_URL",
        f"{CHAT_API_BASE_URL}/create_chat" if CHAT_API_BASE_URL else ""
    )
    STUDENT_URL: str = os.getenv("STUDENT_URL", f"{API_BASE_URL}/student/{{id}}" if API_BASE_URL else "")
    RECRUITER_URL: str = os.getenv("RECRUITER_URL", f"{API_BASE_URL}/recruiter/{{id}}" if API_BASE_URL else "")

    REQUEST_PAGE: int = int(os.getenv("REQUEST_PAGE", "0"))
    REQUEST_SIZE: int = int(os.getenv("REQUEST_SIZE", "100"))

    USERNAME_LOGIN: str = os.getenv("USERNAME_LOGIN", "")
    PASSWORD: str = os.getenv("PASSWORD", "")

    ACCEPT: str = os.getenv("ACCEPT", "*/*")
    CONTENT_TYPE: str = os.getenv("CONTENT_TYPE", "application/json")

    if not API_BASE_URL and not LOGIN_URL:
        exit("API_BASE_URL or LOGIN_URL not set environment variable")
    if not SYNC_SET_URL:
        exit("SYNC_SET_URL not set environment variable")
    if not SYNC_GET_URL:
        exit("SYNC_GET_URL not set environment variable")
    if not REQUEST_FILTER_URL:
        exit("REQUEST_FILTER_URL not set environment variable")
    if not REQUEST_URL:
        exit("REQUEST_URL not set environment variable")
    if not TELEGRAM_UPDATE_URL:
        exit("TELEGRAM_UPDATE_URL not set environment variable")
    if not CREATE_CHAT_URL:
        exit("CREATE_CHAT_URL not set environment variable")
    if not STUDENT_URL:
        exit("STUDENT_URL not set environment variable")
    if not RECRUITER_URL:
        exit("RECRUITER_URL not set environment variable")

    if not USERNAME_LOGIN:
        exit("Username login not set environment variable")

    if not PASSWORD:
        exit("Password not set environment variable")

    HEADERS = {
        "accept": ACCEPT,
        "Content-Type": CONTENT_TYPE,
    }

    LOGIN_DATA: dict = {
        "username": USERNAME_LOGIN,
        "password": PASSWORD
    }

    COOKIE = None
