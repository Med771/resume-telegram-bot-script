from logging import getLogger, Logger, FileHandler, Formatter, Filter, LogRecord
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

from config import LoggerConfig


class LevelFilter(Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record: LogRecord) -> bool:
        return record.levelno == self.level


def create_handler(level: int) -> FileHandler:
    handler: FileHandler = FileHandler(
        filename=LoggerConfig.LOG_LEVELS[level]["dir"],
        mode=LoggerConfig.LOG_LEVELS[level]["record_mode"],
        encoding=LoggerConfig.ENCODING)

    formatter: Formatter = Formatter(
        fmt=LoggerConfig.LOG_LEVELS[level]["format"]
    )

    handler.setFormatter(formatter)
    handler.addFilter(LevelFilter(level))

    return handler


info_handler = create_handler(INFO)
warning_handler = create_handler(WARNING)
error_handler = create_handler(ERROR)
critical_handler = create_handler(CRITICAL)

data_handler: FileHandler = FileHandler(
    filename=LoggerConfig.DATA_DIR,
    mode=LoggerConfig.RECORD_MODE_A,
    encoding=LoggerConfig.ENCODING)

data_handler.addFilter(LevelFilter(DEBUG))

data_formatter: Formatter = Formatter(
    fmt=LoggerConfig.LOG_LEVELS[INFO]["format"])


class LoggerTools:
    @staticmethod
    def get_logger(name: str,
                   info: bool = False,
                   warn: bool = False,
                   error: bool = False,
                   critical: bool = False,
                   ) -> Logger:
        logger: Logger = getLogger(name)
        logger.setLevel(DEBUG)

        if info:
            logger.addHandler(info_handler)
        if warn:
            logger.addHandler(warning_handler)
        if error:
            logger.addHandler(error_handler)
        if critical:
            logger.addHandler(critical_handler)

        return logger

    @staticmethod
    def get_data_logger(name: str) -> Logger:
        data_handler.setFormatter(data_formatter)

        logger: Logger = getLogger(name)
        logger.setLevel(DEBUG)

        logger.addHandler(data_handler)

        return logger
