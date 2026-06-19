from concurrent.futures import ThreadPoolExecutor
from deliverx.configuration.application import MAX_ATTEMPTS
from datetime import datetime
from deliverx.constant.notification import NotificationChannelStatus
from deliverx.configuration.database import AsyncPostgresSession
from deliverx.database.notification_channels import NotificationChannels
import random
from time import sleep
from deliverx.model.kafka_message import KafkaMessage
from loguru import logger
from deliverx.constant.subscription import NotificationDeliveryMedium
from aiokafka import AIOKafkaConsumer
import os
import time

failure_pct_threshold = os.getenv("FAILURE_PCT_IN_CONSUMERS", 0.8)


class GenericKafkaConsumer:

    def __init__(self):
        self.kfk_consumer = AIOKafkaConsumer(
            NotificationDeliveryMedium.EMAIL.as_topic_name,
            NotificationDeliveryMedium.SMS.as_topic_name,
            NotificationDeliveryMedium.WHATSAPP.as_topic_name,
            NotificationDeliveryMedium.IN_APP.as_topic_name,
            bootstrap_servers="localhost:9092",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="notifications__consumer-group",
            key_deserializer=lambda k: str(k),
            value_deserializer=lambda v: KafkaMessage.model_validate_json(
                v.decode('utf-8')
            ),
        )
        self.thread_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="kfk-consmr-thread-")

    async def start_consumption(self):
        logger.info(f"Starting consumer: {self.kfk_consumer}")
        await self.kfk_consumer.start()

        try:
            total_processed_messages = 0
            async with AsyncPostgresSession() as session:
                async for record in self.kfk_consumer:
                    await self._process_message(record, session)
                    total_processed_messages += 1    
            logger.info(f"Total messages processed: {total_processed_messages}.")
        finally:
            await self.kfk_consumer.stop()

    async def _process_message(self, record, session):
        start = time.time()
        logger.debug("Got a message!")
        message: KafkaMessage = record.value
        channel: NotificationChannels | None = await session.get(
            NotificationChannels, message.id_
        )
        if channel is None:
            logger.warning(f"No channel found for id={message.id_}")
            return

        channel.attempt_count += 1
        failure_message = None

        try:
            was_run_successfull = await self.send_notification(message)
        except Exception as e:
            logger.exception(e)
            was_run_successfull = False
            failure_message = str(e)

        if was_run_successfull:
            channel.status = NotificationChannelStatus.DELIVERED
            channel.updated_at = datetime.now()
            channel.sent_at = datetime.now()
        else:
            channel.status = NotificationChannelStatus.FAILED
            channel.updated_at = datetime.now()
            channel.last_error = (
                failure_message
                or f"Threshold {failure_pct_threshold * 100}% was not in favour. Better luck next time."
            )
            if channel.attempt_count >= MAX_ATTEMPTS:
                self.move_to_dlq(message)
        await session.commit()
        logger.debug(f"Completed a message in: {time.time()-start}s")


    async def send_notification(self, message: KafkaMessage) -> bool:
        result = None
        match message.type_:
            case NotificationDeliveryMedium.EMAIL.value:
                result = await self.send_email(message)
            case NotificationDeliveryMedium.SMS.value:
                result = await self.send_sms(message)
            case NotificationDeliveryMedium.WHATSAPP.value:
                result = await self.send_whatsapp(message)
            case NotificationDeliveryMedium.IN_APP.value:
                result = await self.send_in_app(message)
            case _:
                raise RuntimeError(
                    f"Wrong type provided: {message.type_}. Message process is failed as no matching impl was found."
                )
        return result

    async def send_email(self, message: KafkaMessage) -> bool:
        time_to_exec = random.randint(3, 6)
        # Below we are mocking the time taken to send an email
        sleep(time_to_exec)
        is_sent_success = random.randint(0, 1) > failure_pct_threshold
        return not is_sent_success

    async def send_sms(self, message: KafkaMessage) -> bool:
        time_to_exec = random.randint(3, 6)
        # Below we are mocking the time taken to send an email
        sleep(time_to_exec)
        is_sent_success = random.randint(0, 1) > failure_pct_threshold
        return not is_sent_success

    async def send_whatsapp(self, message: KafkaMessage) -> bool:
        time_to_exec = random.randint(3, 6)
        # Below we are mocking the time taken to send an email
        sleep(time_to_exec)
        is_sent_success = random.randint(0, 1) > failure_pct_threshold
        return not is_sent_success

    async def send_in_app(self, message: KafkaMessage) -> bool:
        time_to_exec = random.randint(3, 6)
        # Below we are mocking the time taken to send an email
        sleep(time_to_exec)
        is_sent_success = random.randint(0, 1) > failure_pct_threshold
        return not is_sent_success
