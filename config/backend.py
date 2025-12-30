import os

from dotenv import load_dotenv

from config.main import MainConfig


class BackendConfig:
    load_dotenv(dotenv_path=MainConfig.MAIN_ENV_PATH)

    LOGIN_URL: str = "https://api.singularity-resume.ru/auth/login"
    SET_URL: str = "https://api.singularity-resume.ru/telegram/student/{id}/setUserId"

    HEADERS = {
        "accept": "*/*",
        "Content-Type": "application/json"
    }

    LOGIN_DATA: dict = {
        "username": "Resume",
        "password": "Resume!01156"
    }

    COOKIE = None
