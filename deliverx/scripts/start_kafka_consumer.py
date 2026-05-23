import asyncio

from deliverx.consumer.generic_kfk_consumer import GenericKafkaConsumer
from loguru import logger


async def main() -> None:
    consumer = GenericKafkaConsumer()
    logger.info(f"{'*' * 10}  KAFKA CONSUMER STARTED  {'*' * 10}")
    await consumer.start_consumption()
    logger.info(f"{'*' * 10}  KAFKA CONSUMER STOPPED  {'*' * 10}")


if __name__ == "__main__":
    asyncio.run(main())
