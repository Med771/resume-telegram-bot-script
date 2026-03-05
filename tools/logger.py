from logging import getLogger, Logger, FileHandler, StreamHandler, Formatter, Filter, LogRecord
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

console_handler: StreamHandler = StreamHandler()
console_handler.setLevel(DEBUG)
console_handler.setFormatter(Formatter(fmt=LoggerConfig.LOG_LEVELS[INFO]["format"]))


def _add_handler_once(logger: Logger, handler) -> None:
    if handler not in logger.handlers:
        logger.addHandler(handler)


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
        logger.propagate = False

        if info:
            _add_handler_once(logger, info_handler)
        if warn:
            _add_handler_once(logger, warning_handler)
        if error:
            _add_handler_once(logger, error_handler)
        if critical:
            _add_handler_once(logger, critical_handler)

        if info or warn or error or critical:
            _add_handler_once(logger, console_handler)

        return logger

    @staticmethod
    def get_data_logger(name: str) -> Logger:
        data_handler.setFormatter(data_formatter)

        logger: Logger = getLogger(name)
        logger.setLevel(DEBUG)
        logger.propagate = False

        _add_handler_once(logger, data_handler)
        _add_handler_once(logger, console_handler)

        return logger
