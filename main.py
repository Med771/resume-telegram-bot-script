import asyncio

from config import TelegramConfig

from module import routers

from tools.logger import LoggerTools

BOT = TelegramConfig.BOT
DISPATCHER = TelegramConfig.DISPATCHER


logger = LoggerTools.get_logger(name=__name__, info=True, error=True, critical=True)


async def main():
    try:
        print("COMPILING")

        DISPATCHER.include_routers(*routers)

        logger.info("SESSION OPEN")
        print("SESSION OPEN")

        await DISPATCHER.start_polling(BOT, polling_timeout=30)
    except asyncio.CancelledError:
        logger.info("Polling cancelled")
    except Exception as ex:
        logger.critical(f"Unexpected error: {ex}", exc_info=True)
    finally:
        logger.info("SESSION CLOSE")
        print("SESSION CLOSE")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("PROGRAM INTERRUPTED")
    except SystemExit:
        logger.info("SYSTEM EXIT")
    except Exception as e:
        logger.critical(f"EXTREMAL ERROR: {e}", exc_info=True)
