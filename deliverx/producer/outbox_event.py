from deliverx.model.kafka_message import KafkaMessage
from deliverx.constant.subscription import priority_tier
from kafka.producer.kafka import KafkaProducer
from loguru import logger

class OutboxEvent:
    PREFIX = "notifications__"

    def __init__(self):
        self.kafka_producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            key_serializer=lambda k: str(k).encode("utf-8"),
            value_serializer=lambda v: v.model_dump_json().encode("utf-8"),
        )

    def send_message(self, /, message: KafkaMessage, priority: int):
        future = self.kafka_producer.send(
            topic=self.PREFIX + priority_tier(priority).value,
            value=message,
            key=priority_tier(priority).value,
        )
        future.get(timeout=10)
