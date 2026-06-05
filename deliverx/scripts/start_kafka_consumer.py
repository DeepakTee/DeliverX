import asyncio

from deliverx.consumer.generic_kfk_consumer import GenericKafkaConsumer
from loguru import logger

# import sys

# from dotenv import load_dotenv

# load_dotenv()
# logger.remove()
# logger.add(sys.stderr, level="DEBUG", colorize=True)
# logger.add(
#     "app-logs/consumer.log", level="DEBUG", rotation="10 MB", retention="10 days"
# )

# logger.info("Logging setup done for CONSUMER!")


async def main() -> None:
    consumer = GenericKafkaConsumer()
    logger.info(f"{'*' * 10}  KAFKA CONSUMER STARTED  {'*' * 10}")
    await consumer.start_consumption()
    logger.info(f"{'*' * 10}  KAFKA CONSUMER STOPPED  {'*' * 10}")


if __name__ == "__main__":
    asyncio.run(main())
