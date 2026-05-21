from enum import Enum


class NotificationStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    PARTIALLY_DELIVERED = "partially_delivered"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationChannelStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    RETRYING = "retrying"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
