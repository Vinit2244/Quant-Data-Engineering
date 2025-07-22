## D. Future Improvements

While our current analysis helped surface duplicate events, retries, and overlaps, we now shift focus toward **how to prevent such issues in production**. We have outlined practical strategies that can improve the robustness and correctness of event processing pipelines in real-time systems.

### 1. Make Workers Idempotent

If a worker processes the same event more than once, the result should be the same every time. This property that is called **idempotency** is essential in distributed systems where retries and duplicates are common. We can ensure this by designing logic that either:
- Checks if the event has already been processed before updating state.
- Applies only non-destructive operations (e.g., overwriting instead of incrementing counters).

Reference: [AWS Whitepaper on Idempotency](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

#### 2. Use Kafka Keys for Deterministic Partitioning

When publishing events to Kafka (or similar systems), using a **consistent partition key** like `event_id` or `symbol` ensures that **related events go to the same partition**. This reduces the chances of different workers handling the same event simultaneously.

Reference: [Confluent Documentation – Kafka Consumer Groups & Partitioning](https://docs.confluent.io/platform/current/clients/consumer.html)


#### 3. Deduplicate Using Time Windows

Frameworks like Flink and Kafka Streams allow us to **deduplicate events based on time**, using techniques like TTL (time-to-live) windows or watermarking. This means the system can wait for a few seconds and discard late-arriving duplicates that match recent events.

Reference: [Apache Flink – Deduplication Patterns](https://nightlies.apache.org/flink/flink-docs-release-1.13/docs/dev/table/sql/queries/deduplication/)


### 4. Retry Intelligently

If something fails, we shouldn't just retry immediately. Implementing **exponential backoff** or **circuit breakers** (like in Netflix's Hystrix model) can help avoid system overload and repeated failures.

