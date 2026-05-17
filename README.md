# DeliverX
---
# Distributed Notification & Delivery System — Requirements

## 1. Goal

Build a backend system that can reliably accept, process, and deliver notifications through multiple channels like email, SMS, and push.

The project should demonstrate:

* scalability
* async processing
* retries
* idempotency
* rate limiting
* ordering
* observability
* distributed system tradeoffs

---

# 2. Core Use Case

A client application sends a notification request:

```json
{
  "user_id": "user_123",
  "request_id": "req_abc_001",
  "channels": ["email", "sms"],
  "priority": "high",
  "template_id": "payment_success",
  "payload": {
    "amount": 1200,
    "merchant": "Amazon"
  }
}
```

The system should:

1. accept the request
2. validate it
3. store notification intent
4. publish it to a queue
5. process it asynchronously
6. send through selected channels
7. retry on failure
8. avoid duplicate sends
9. track delivery status
10. expose delivery status through API

---

# 3. Functional Requirements

## 3.1 Notification Submission API

Create an API to submit notification requests.

### Endpoint

```http
POST /notifications
```

### Requirements

The API should:

* accept notification requests
* validate required fields
* generate notification ID if not provided
* support client-provided `request_id` for idempotency
* store the request in database
* publish event to queue
* return immediately without sending the notification directly

### Response

```json
{
  "notification_id": "notif_123",
  "status": "queued"
}
```

---

## 3.2 Idempotency

The system must prevent duplicate notification creation and duplicate delivery.

### Requirements

* `request_id` should be unique per client/user
* if same `request_id` is submitted again, return original notification response
* workers should also check if a notification/channel has already been sent before sending again
* duplicate queue messages should not cause duplicate delivery

### Example

If this request is sent twice:

```json
{
  "request_id": "req_001",
  "user_id": "user_123"
}
```

Only one notification should be created and delivered.

---

## 3.3 Queue-Based Async Processing

Notification delivery must happen asynchronously.

### Requirements

* API service should publish messages to Kafka/Redpanda/RabbitMQ
* worker services should consume messages
* API should not block on actual email/SMS/push delivery
* workers should update notification status after processing

### Suggested Topics/Queues

```text
notifications.high
notifications.normal
notifications.low
notifications.dlq
```

---

## 3.4 Multi-Channel Delivery

Support multiple notification channels.

### Channels

* email
* SMS
* push

### Requirements

One notification request may create multiple delivery tasks.

Example:

```json
"channels": ["email", "sms"]
```

This should create:

```text
email delivery task
sms delivery task
```

Each channel should have independent status.

---

## 3.5 Delivery Status Tracking

Track status at both notification level and channel level.

### Notification statuses

```text
queued
processing
partially_delivered
delivered
failed
cancelled
```

### Channel statuses

```text
pending
processing
sent
failed
retrying
dead_lettered
```

### Endpoint

```http
GET /notifications/{notification_id}
```

### Response

```json
{
  "notification_id": "notif_123",
  "status": "partially_delivered",
  "channels": {
    "email": "sent",
    "sms": "retrying"
  }
}
```

---

## 3.6 Retry System

Failed deliveries should be retried automatically.

### Requirements

* retry failed channel delivery
* use exponential backoff
* max retry count should be configurable
* after max retries, move message to DLQ
* store retry count
* store last failure reason

### Example retry policy

```text
Attempt 1: immediate
Attempt 2: after 10 seconds
Attempt 3: after 30 seconds
Attempt 4: after 2 minutes
After that: move to DLQ
```

---

## 3.7 Dead Letter Queue

Messages that cannot be delivered after retries should go to DLQ.

### Requirements

* failed messages should be stored in DLQ topic/table
* admin should be able to inspect failed messages
* admin should be able to replay DLQ messages

### Endpoints

```http
GET /admin/dlq
POST /admin/dlq/{message_id}/replay
```

---

## 3.8 Rate Limiting

Prevent abuse and overload.

### Requirements

Apply rate limits on:

* per user
* per channel
* per notification type
* global system level

### Example limits

```text
OTP: 5 per user per 10 minutes
Marketing: 10 per user per day
Email provider: 100 requests per minute
SMS provider: 50 requests per minute
```

If limit is exceeded, system should either:

* reject the request
* delay processing
* queue for later

Document your chosen behavior.

---

## 3.9 Priority Handling

High-priority notifications should be processed before low-priority ones.

### Priority levels

```text
high
normal
low
```

### Examples

```text
OTP: high
Payment alert: high
Order update: normal
Marketing: low
```

### Requirements

* workers should prefer high-priority queues
* low-priority notifications should not block high-priority ones
* priority should be visible in stored records

---

## 3.10 Ordering Per User

Maintain ordering for notifications belonging to the same user where required.

### Requirement

For a given user, notifications marked as `ordering_required=true` should be processed in order.

### Example

Correct order:

```text
payment_initiated
payment_success
receipt_generated
```

Wrong order:

```text
receipt_generated
payment_initiated
payment_success
```

### Implementation expectation

Use partitioning strategy:

```text
partition key = user_id
```

Document the tradeoff:

* ordering per user
* not global ordering
* parallelism still possible across users

---

# 4. Non-Functional Requirements

## 4.1 Scalability

The system should support horizontal scaling.

### Requirements

* multiple API instances
* multiple worker instances
* multiple queue partitions
* Redis/Postgres should not become immediate bottleneck
* workers should be stateless where possible

### Load test target

For local simulation:

```text
100k notification requests
1k–5k requests/minute
multiple workers running in parallel
```

---

## 4.2 Reliability

System should handle failures gracefully.

### Failure cases to support

* worker crashes after consuming message
* queue temporarily unavailable
* provider API fails
* database write fails
* duplicate messages arrive
* Redis unavailable
* partial channel failure

For each case, document:

```text
What happens?
How does system recover?
Is duplicate delivery possible?
Is data loss possible?
```

---

## 4.3 Consistency

The system should use eventual consistency.

### Requirement

API may return:

```text
queued
```

even though delivery happens later.

### Expected behavior

* notification request is stored first
* event is published after/with durable storage
* worker updates final state later
* status API reflects latest known state

### Important design decision

Use either:

1. transactional outbox pattern, or
2. careful DB-write-then-publish with recovery job

Preferred: **transactional outbox pattern**.

---

## 4.4 Observability

Add logs, metrics, and tracing-friendly structure.

### Logs should include

* notification_id
* request_id
* user_id
* channel
* attempt number
* status
* failure reason

### Metrics to expose

```text
notifications_received_total
notifications_delivered_total
notifications_failed_total
notification_retry_total
dlq_messages_total
delivery_latency_ms
queue_lag
worker_processing_time_ms
```

---

## 4.5 Performance

### Requirements

* API response should be fast because delivery is async
* target API latency: under 100–200 ms locally
* delivery latency should be measured
* queue lag should be observable
* workers should support batch consumption if possible

---

# 5. Data Model

## 5.1 notifications table

```text
id
request_id
user_id
template_id
priority
status
ordering_required
created_at
updated_at
```

## 5.2 notification_channels table

```text
id
notification_id
channel
status
attempt_count
last_error
sent_at
created_at
updated_at
```

## 5.3 outbox_events table

```text
id
aggregate_id
event_type
payload
status
created_at
published_at
```

## 5.4 dlq_messages table

```text
id
notification_id
channel
payload
failure_reason
attempt_count
created_at
replayed_at
```

## 5.5 rate_limits table/cache

Can be Redis-based.

```text
key
count
expiry
```

---

# 6. APIs

## Public APIs

```http
POST /notifications
GET /notifications/{notification_id}
GET /users/{user_id}/notifications
```

## Admin APIs

```http
GET /admin/dlq
POST /admin/dlq/{message_id}/replay
GET /admin/metrics
GET /admin/health
```

---

# 7. Worker Requirements

Create separate workers or logical processors for:

```text
email_worker
sms_worker
push_worker
retry_worker
outbox_publisher
dlq_replay_worker
```

Each worker should:

* consume messages
* validate idempotency
* call mock provider
* update status
* retry on failure
* log structured events

---

# 8. Mock Providers

Do not integrate real SMS/email initially.

Create mock providers that simulate:

* success
* temporary failure
* permanent failure
* timeout
* slow response

Example:

```text
90% success
5% temporary failure
3% timeout
2% permanent failure
```

This makes the system easier to test.

---

# 9. Testing Requirements

## Unit Tests

Test:

* request validation
* idempotency logic
* retry policy
* rate limiting
* status transitions

## Integration Tests

Test:

* API → DB → queue → worker → status update
* duplicate request handling
* provider failure and retry
* DLQ movement
* DLQ replay

## Load Tests

Simulate:

```text
10k requests
100k requests
multiple users
multiple channels
mixed priority
```

Measure:

* throughput
* latency
* retry count
* failure rate
* queue lag

---

# 10. Documentation Requirements

Your README should include:

1. project overview
2. architecture diagram
3. system components
4. API examples
5. data model
6. queue design
7. retry design
8. idempotency design
9. consistency model
10. failure scenarios
11. scaling strategy
12. tradeoffs
13. local setup
14. load test results
15. future improvements

---

# 11. Recommended Tech Stack

Since your background is backend/Python/FastAPI:

```text
API: FastAPI
Workers: Python workers / Celery optional
Queue: Kafka or Redpanda
DB: PostgreSQL
Cache/rate limit: Redis
Containerization: Docker Compose
Load testing: k6 or Locust
Observability: Prometheus + Grafana optional
```

Use **Redpanda** if you want Kafka-like behavior with easier local setup.

---

# 12. MVP Scope

Build this first:

```text
POST /notifications
GET /notifications/{id}
Postgres persistence
queue publishing
one email worker
mock email provider
idempotency by request_id
retry 3 times
DLQ table
basic logs
Docker Compose setup
```

Then expand to:

```text
SMS/push
priority queues
rate limiting
ordering
outbox pattern
metrics
load testing
DLQ replay
```

---

# 13. Success Criteria

Project is complete when you can demonstrate:

* submit 100k notifications locally
* workers process asynchronously
* failed messages retry automatically
* permanently failed messages move to DLQ
* duplicate requests do not create duplicate sends
* high-priority messages process before low-priority ones
* status API shows accurate delivery state
* README explains tradeoffs clearly

---

# 14. Resume Positioning

Once complete, you can describe it like this:

> Built a distributed notification delivery system using FastAPI, Kafka/Redpanda, PostgreSQL, and Redis, supporting asynchronous processing, idempotent delivery, retries, DLQ replay, priority queues, per-user ordering, and rate limiting. Simulated 100k+ notification events with horizontally scalable workers and documented consistency, reliability, and scaling tradeoffs.
