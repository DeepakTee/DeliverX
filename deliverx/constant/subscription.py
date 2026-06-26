from enum import Enum


class NotificationDeliveryMedium(Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_APP = "in-app"

    @property
    def as_topic_name(self):
        return "notifications__" + self.value


class NotificationPriorityTier(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def as_topic_name(self) -> str:
        return f"notifications__{self.value}"


def priority_tier(priority: int) -> NotificationPriorityTier:
    if priority <= 3:
        return NotificationPriorityTier.HIGH
    if priority <= 7:
        return NotificationPriorityTier.MEDIUM
    return NotificationPriorityTier.LOW