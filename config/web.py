import os

from dotenv import load_dotenv

from config.main import MainConfig


class WebConfig:
    load_dotenv(dotenv_path=MainConfig.MAIN_ENV_PATH)

    LOGIN_URL: str = os.getenv("LOGIN_URL", "")

    SET_STUD_URL: str = os.getenv("SET_STUD_URL", "")
    SET_REC_URL: str = os.getenv("SET_REC_URL", "")

    GET_STUD_INFO_URL: str = os.getenv("GET_STUD_INFO_URL", "")
    GET_REC_INFO_URL: str = os.getenv("GET_REC_INFO_URL", "")

    GET_REQ_URL: str = os.getenv("GET_REQ_URL", "")
    GET_OFFER_URL: str = os.getenv("GET_OFFER_URL", "")

    SET_STATUS_URL: str = os.getenv("SET_STATUS_URL", "")

    OFFERS_URL: str = os.getenv("OFFERS_URL", "")
    BATCH_UPDATE_STATUS_URL: str = os.getenv("BATCH_UPDATE_STATUS_URL", "")

    CREATE_CHAT_URL: str = os.getenv("CREATE_CHAT_URL", "")

    USERNAME_LOGIN: str = os.getenv("USERNAME_LOGIN", "")
    PASSWORD: str = os.getenv("PASSWORD", "")

    ACCEPT: str = os.getenv("ACCEPT", "*/*")
    CONTENT_TYPE: str = os.getenv("CONTENT_TYPE", "application/json")

    if not LOGIN_URL:
        exit("Login URL not set environment variable")

    if not SET_STUD_URL:
        exit("Set STUD URL not set environment variable")

    if not SET_REC_URL:
        exit("Set REC URL not set environment variable")

    if not GET_STUD_INFO_URL:
        exit("Get STUD info URL not set environment variable")

    if not GET_REC_INFO_URL:
        exit("Get REC info URL not set environment variable")

    if not GET_REQ_URL:
        exit("Get REQ URL not set environment variable")

    if not GET_OFFER_URL:
        exit("Get OFFER URL not set environment variable")

    if not SET_STATUS_URL:
        exit("Set status URL not set environment variable")

    if not OFFERS_URL:
        exit("Offers URL not set environment variable")

    if not BATCH_UPDATE_STATUS_URL:
        exit("Batch update status URL not set environment variable")

    if not CREATE_CHAT_URL:
        exit("Create chat URL not set environment variable")

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
