import os

from pathlib import Path

from dotenv import load_dotenv


class MainConfig:
    MAIN_PATH = Path(__file__).parent.parent
    MAIN_ENV_PATH = MAIN_PATH / ".env"

    load_dotenv(dotenv_path=MAIN_ENV_PATH)

    ENCODING = os.getenv("ENCODING", "utf-8")

    if not ENCODING:
        exit("Encoding environment variable not set")
