
from deliverx.constant.subscription import NotificationDeliveryMedium
from kafka.admin import KafkaAdminClient, NewTopic


admin_client = KafkaAdminClient(
    bootstrap_servers="localhost:9092", client_id="producer-1"
)

expected_topic_names = [
    f"notification__{v.value}"
    for v in NotificationDeliveryMedium
]

actual_topic_names = admin_client.list_topics()

topics_needed = [topic_name for topic_name in expected_topic_names if topic_name not in actual_topic_names]

topics = [
    NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
    for topic_name in topics_needed
]

print(admin_client.create_topics(topics))
