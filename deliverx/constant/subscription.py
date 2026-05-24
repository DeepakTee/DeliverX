from enum import Enum


class NotificationDeliveryMedium(Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_APP = "in-app"

    @property
    def as_topic_name(self):
        return "notifications__" + self.value
