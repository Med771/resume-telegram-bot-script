import os

from dotenv import load_dotenv

from logging import INFO, WARNING, ERROR, CRITICAL

from config.main import MainConfig


class LoggerConfig:
    load_dotenv(dotenv_path=MainConfig.MAIN_ENV_PATH)

    LOGS_DIR = os.path.join(MainConfig.MAIN_PATH, "logs")

    os.makedirs(LOGS_DIR, exist_ok=True)

    INFO_DIR: str = os.path.join(LOGS_DIR, os.getenv('INFO_FILENAME', 'info.log'))
    WARN_DIR: str = os.path.join(LOGS_DIR, os.getenv('WARN_FILENAME', 'warn.log'))
    ERROR_DIR: str = os.path.join(LOGS_DIR, os.getenv('ERROR_FILENAME', 'error.log'))
    CRIT_DIR: str = os.path.join(LOGS_DIR, os.getenv('CRIT_FILENAME', 'crit.log'))
    DATA_DIR: str = os.path.join(LOGS_DIR, os.getenv('DATA_FILENAME', 'data.log'))

    RECORD_MODE_W: str = "w"
    RECORD_MODE_A: str = "a"

    ENCODING: str = os.getenv("ENCODING", "utf-8")

    INFO_FMT: str = '#%(levelname)-5s [%(asctime)s] - %(message)s'
    WARN_FMT: str = '[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(message)s'
    ERROR_FMT: str = '[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d %(funcName)s() - %(message)s'
    CRIT_FMT: str = '[%(asctime)s] #%(levelname)-8s  %(filename)s:%(lineno)d %(funcName)s() - %(message)s'

    LOG_LEVELS: dict[int, dict[str, str]] = {
        INFO: {
            "dir": INFO_DIR,
            "format": INFO_FMT,
            "record_mode": RECORD_MODE_A
        },
        WARNING: {
            "dir": WARN_DIR,
            "format": WARN_FMT,
            "record_mode": RECORD_MODE_A
        },
        ERROR: {
            "dir": ERROR_DIR,
            "format": ERROR_FMT,
            "record_mode": RECORD_MODE_A
        },
        CRITICAL: {
            "dir": CRIT_DIR,
            "format": CRIT_FMT,
            "record_mode": RECORD_MODE_A
        }
    }
