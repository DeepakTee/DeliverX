from deliverx.constant.subscription import NotificationDeliveryMedium
from deliverx.model.kafka_message import KafkaMessage
from kafka.producer.kafka import KafkaProducer


class OutboxEvent:
    PREFIX = "notifications__"

    def __init__(self):
        self.kafka_producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            key_serializer=lambda k: str(k).encode("utf-8"),
            value_serializer=lambda v: v.model_dump_json().encode("utf-8"),
        )

    def send_message(self, /, message: KafkaMessage, type_: NotificationDeliveryMedium):
        self.kafka_producer.send(
            topic=self.PREFIX + type_.value,
            value=message,
            key=message.priority,
        )
