
## 🧠 Overview

**DeliverX** is a distributed, event-driven notification system designed to reliably deliver messages (email, SMS, push) at scale.

It is built to simulate real-world systems used by companies like Amazon, Uber, and fintech platforms where **millions of time-sensitive notifications** must be delivered with:

* high reliability
* low latency
* fault tolerance
* strong consistency guarantees (where needed)

Unlike simple notification services, DeliverX focuses on **distributed systems challenges** such as idempotency, retries, ordering, rate limiting, and eventual consistency.

---

## 🎯 Problem Statement

Modern applications need to send notifications for:

* OTPs and authentication
* payments and transactions
* order updates
* reminders and alerts
* marketing campaigns

These systems must ensure:

* notifications are **not lost**
* failures are **retried automatically**
* users are **not spammed with duplicates**
* high-priority messages are delivered **before low-priority ones**
* system scales under **high throughput**

DeliverX solves these challenges using a **decoupled, asynchronous architecture**.

---

## 🏗️ High-Level Architecture

### Core Flow

```text
Client → API → Database → Outbox → Queue → Workers → Providers → Status Update
```

---

## ⚙️ System Components

### 1. API Service

Responsible for:

* accepting notification requests
* validating input
* enforcing idempotency
* storing notification data
* publishing events to the queue (via outbox pattern)

**Key property:**
👉 Non-blocking — does NOT send notifications directly

---

### 2. Database (PostgreSQL)

Stores:

* notification metadata
* channel-level delivery state
* retry attempts
* failure reasons
* outbox events (for reliable publishing)

Ensures **durability and recovery capability**

---

### 3. Outbox Publisher

Implements **transactional outbox pattern**

Why this matters:

Without it:

* DB write succeeds but queue publish fails → data loss

With it:

* DB and event publishing are **eventually consistent and reliable**

---

### 4. Message Queue (Kafka)

Acts as a buffer between producers and consumers.

Responsibilities:

* decoupling API from workers
* handling high throughput
* enabling parallel processing
* supporting ordering via partitioning

---

### 5. Worker Services

Separate workers for each channel:

* email worker
* SMS worker
* push worker

Responsibilities:

* consume messages
* check idempotency
* call delivery provider
* update status
* trigger retries on failure

---

### 6. Retry Engine

Handles transient failures using:

* exponential backoff
* retry count tracking
* delayed re-processing

Ensures **at-least-once delivery**

---

### 7. Dead Letter Queue (DLQ)

Stores permanently failed messages.

Used for:

* debugging failures
* replaying messages
* auditing system behavior

---

### 8. Rate Limiter (Redis)

Prevents abuse and overload.

Supports:

* per-user limits
* per-channel limits
* global system throttling

---

## 🔁 End-to-End Flow

### Step 1: Request Submission

Client sends request:

```json
POST /notifications
```

System:

* validates input
* checks idempotency
* stores notification
* writes event to outbox

---

### Step 2: Event Publishing

Outbox publisher:

* reads pending events
* publishes to Kafka topic
* marks event as published

---

### Step 3: Queue Processing

Workers:

* consume messages from queue
* process based on priority
* ensure idempotency

---

### Step 4: Delivery Attempt

Worker:

* calls mock provider
* simulates success/failure
* updates status

---

### Step 5: Retry (if failure)

If transient failure:

* retry with backoff
* update attempt count

If max retries exceeded:

* move to DLQ

---

### Step 6: Status Tracking

Client can query:

```http
GET /notifications/{id}
```

Returns:

* overall status
* per-channel status
* retry information

---

## 🧠 Key System Design Concepts

### 1. Asynchronous Processing

Notifications are not sent during API call.

👉 Improves latency and scalability

---

### 2. Idempotency

Ensures:

* duplicate API calls don’t create duplicate notifications
* duplicate queue messages don’t cause duplicate sends

---

### 3. At-Least-Once Delivery

System guarantees delivery attempts, but duplicates are possible.

👉 handled via idempotency

---

### 4. Eventual Consistency

API returns:

```text
queued
```

Final state is updated asynchronously.

---

### 5. Partitioning for Ordering

Kafka partitions ensure:

```text
ordering per user_id
```

Tradeoff:

* ordering guaranteed per user
* not globally ordered

---

### 6. Fault Tolerance

Handles:

* worker crashes
* provider failures
* duplicate events
* partial delivery failures

---

### 7. Backpressure Handling

Queue absorbs traffic spikes.

Workers scale horizontally to handle load.

---

## 📊 Observability

### Logs

Structured logs include:

* notification_id
* request_id
* user_id
* channel
* attempt number
* error reason

---

### Metrics

* delivery success rate
* retry count
* DLQ size
* processing latency
* queue lag

---

## 📈 Scalability Strategy

System scales by:

* increasing API instances
* increasing worker instances
* increasing queue partitions
* using stateless workers

---

## 🧪 Failure Scenarios Handled

| Scenario             | Behavior                |
| -------------------- | ----------------------- |
| Worker crashes       | message reprocessed     |
| Duplicate message    | ignored via idempotency |
| Provider failure     | retried                 |
| Max retries exceeded | moved to DLQ            |
| DB failure           | retry / fail-safe       |
| Queue lag            | workers scale           |

---

## ⚖️ Tradeoffs

### At-least-once vs exactly-once

Chosen:

👉 **At-least-once**

Reason:

* simpler
* scalable
* industry standard

---

### Consistency vs Availability

Chosen:

👉 **Eventual consistency**

Reason:

* improves performance
* enables async architecture

---

### Kafka vs RabbitMQ

Chosen:

👉 Kafka

Reason:

* better for high throughput
* partition-based ordering
* durable log

---

## 🧪 Load Simulation

System tested with:

* 100k+ notification events
* multiple users
* mixed priorities
* simulated failures

---

## 🛠️ Tech Stack

* API Controller
* PostgreSQL (primary storage)
* Redis (rate limiting & caching)
* Kafka / Redpanda (event streaming)
* Docker (containerization)

---

## 🚀 What This Project Demonstrates

* real-world backend system design
* distributed system fundamentals
* handling failure at scale
* async architecture
* system reliability patterns

---

## 📌 Future Improvements

* multi-region deployment
* circuit breaker pattern
* batching for throughput
* real provider integrations
* UI dashboard for monitoring
* ML-based notification prioritization

---

## 💬 One-Line Summary

> Built a distributed notification delivery system with asynchronous processing, idempotent delivery, retry mechanisms, DLQ handling, and priority-based execution using FastAPI, Kafka, PostgreSQL, and Redis, simulating high-scale real-world backend systems.
