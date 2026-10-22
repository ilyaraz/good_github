# Message brokers and durable message queues

Research date: **2026-10-09**.

This selection covers 25 repositories implementing message brokers, persistent work queues, replayable messaging logs, MQTT brokers, and embedded durable queues. It includes storage and delivery machinery inside larger projects, identified below, rather than counting their clients or dependencies separately. Durability has different boundaries here: disk persistence, replicated acceptance, consumer acknowledgement, and application transaction completion are not interchangeable. Historical projects are included explicitly for architectural study.

Criteria legend:

- **C1 — Correctness:** substantial invariants, concurrency, adversarial inputs, or failure and recovery semantics.
- **C2 — Abstractions:** reusable mechanisms supporting materially different messaging applications.
- **C3 — Performance and structure:** concrete resource or throughput constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development supported by compatibility work, testing, or deliberate complexity management.

The criteria below are evidence-based reasons to study each repository, not scores or claims that every component is exemplary. Linked repository headings identify the verified canonical GitHub locations; links within entries are additional primary-source reading entry points.

## General-purpose and transactional brokers

### 1. [rabbitmq/rabbitmq-server](https://github.com/rabbitmq/rabbitmq-server)

**Erlang; multiprotocol broker, particularly its quorum-queue subsystem.** Study how replicated queue state interacts with publisher confirmation, consumer acknowledgement, and dead-letter routing.

- **C1:** Quorum queues use Raft, and publisher confirmation depends on quorum acceptance. The at-least-once dead-letter path retains source messages until an internal consumer receives confirmation from the destination; unavailable destinations therefore create storage and backpressure consequences. This is a concrete distributed ownership-transfer problem. [Quorum-queue design and guarantees](https://www.rabbitmq.com/docs/quorum-queues).
- **C2:** Queue delivery, exchange-based routing, acknowledgement, redelivery, and configurable dead-letter handling compose into reusable application workflows. The same guide distinguishes normal queue consumption from replay-oriented streams and explains which queue policies alter the guarantees. [Queue behavior and configuration](https://www.rabbitmq.com/docs/quorum-queues).

### 2. [nats-io/nats-server](https://github.com/nats-io/nats-server)

**Go; subject-based broker with the embedded JetStream persistence subsystem.** Study the transition from ephemeral messaging to replicated streams without replacing the subject-routing model.

- **C1:** JetStream adds replicated stream state, Raft-based recovery, acknowledged publication, optional deduplication, and consumer acknowledgement/redelivery. These are distinct mechanisms; their combination should not be mistaken for automatically exactly-once application side effects. [Server architecture](https://github.com/nats-io/nats-general/blob/main/architecture/ARCHITECTURE.md).
- **C2:** Streams capture subjects, while durable consumers maintain independent delivery state and offer filtering and replay. Key-value and object-store facilities build on that messaging foundation, illustrating reuse above the storage layer. [JetStream concepts](https://docs.nats.io/concepts/jetstream).

### 3. [apache/artemis](https://github.com/apache/artemis)

**Java; Apache Artemis messaging broker.** This is the canonical repository verified during research. Its persistence implementation is particularly useful for studying where an API operation becomes a durable fact.

- **C1:** The persistence guide distinguishes synchronization at transaction prepare/commit from synchronization of nontransactional sends and acknowledgements. It also separates process-crash recovery from power-failure protection through journal synchronization settings. [Persistence implementation guide](https://github.com/apache/artemis/blob/main/docs/user-manual/persistence.adoc).
- **C3:** Separate bindings and message journals, precreated journal files, NIO/AIO/memory-mapped alternatives, timed buffering, and bounded I/O submission expose concrete latency-throughput tradeoffs. Large messages and paging take separate paths rather than forcing every workload through one journal representation. [Journal structure and tuning](https://github.com/apache/artemis/blob/main/docs/user-manual/persistence.adoc).

### 4. [apache/activemq](https://github.com/apache/activemq)

**Java; ActiveMQ Classic, a distinct implementation from Artemis.** Study KahaDB and the interaction between message retention, acknowledgement records, and destination isolation.

- **C1:** KahaDB supports journal checksums and corruption checking. Transactions spanning multiple KahaDB stores require a two-phase completion mechanism and a durable commit decision, making multi-destination atomicity an explicit storage concern. [KahaDB persistence documentation](https://activemq.apache.org/components/classic/documentation/kahadb).
- **C3:** Acknowledgement compaction addresses journal files kept alive by scattered acknowledgement dependencies. Multiple destination stores, preallocation, write batching, and configurable synchronization policies show how storage layout and crash guarantees constrain throughput. [KahaDB configuration and compaction](https://activemq.apache.org/components/classic/documentation/kahadb).

### 5. [apache/qpid-broker-j](https://github.com/apache/qpid-broker-j)

**Java; AMQP broker, in an official Apache GitHub mirror.** Study its managed-object architecture: broker configuration is a structured lifecycle with persistence and concurrency rules, not just a collection of settings.

- **C1:** Configuration mutations run through a single configuration executor associated with the relevant broker or virtual host. Creation, recovery, validation, and publication to observer threads impose lifecycle and safe-publication requirements. [High-level architecture](https://cwiki.apache.org/confluence/display/qpid/High%2BLevel%2BArchitecture).
- **C2:** The `ConfiguredObject` hierarchy separates system configuration, broker, virtual-host nodes, virtual hosts, and queues. Pluggable message stores, authentication, protocol handling, and embedded or standalone operation supply reusable extension boundaries. [Object model and extension architecture](https://cwiki.apache.org/confluence/display/qpid/High%2BLevel%2BArchitecture).

The architecture document is dated 2018; use it as a conceptual map and check current interfaces in the mirrored source.

### 6. [cloudamqp/lavinmq](https://github.com/cloudamqp/lavinmq)

**Crystal; AMQP broker with a disk-oriented queue engine.** Study how a relatively compact implementation combines Crystal fibers with a sequential storage model.

- **C1:** Message segments and acknowledgement positions are stored separately. Recovery skips acknowledged positions, and segment reclamation waits until its messages are acknowledged. Requeue tracking and replay therefore have explicit state-management consequences. [Implementation details in the contributor guide](https://github.com/cloudamqp/lavinmq/blob/main/CONTRIBUTING.md).
- **C3:** Memory-mapped segments rely on the operating system's page cache, sequential consumption favors disk access patterns, and consumer delivery loops run as fibers. The guide traces publication through client, channel, virtual host, routing, and queue, making the hot path inspectable. [Storage and execution architecture](https://github.com/cloudamqp/lavinmq/blob/main/CONTRIBUTING.md).

### 7. [bloomberg/blazingmq](https://github.com/bloomberg/blazingmq)

**C++; clustered broker with replicated disk-backed queues.** Study the separation between message acceptance, consumer completion, queue leadership, and cluster metadata leadership.

- **C1:** Producer `ACK` and consumer `CONFIRM` represent different milestones. Out-of-order confirmations support concurrent processing, while failover can cause duplicates; the architecture explicitly differentiates normal at-least-once delivery from broadcast's weaker guarantee. [Architecture overview](https://bloomberg.github.io/blazingmq/docs/introduction/architecture_overview/).
- **C2:** Domains group queue policy, quotas, consistency, and lifetime settings. Priority, fanout, and broadcast modes reuse the queue machinery, while connections to nonprimary nodes can be forwarded to the queue's primary. This is a useful model of separating deployment topology from application-facing destinations. [Domains, queues, and routing](https://bloomberg.github.io/blazingmq/docs/introduction/architecture_overview/).

### 8. [endurox-dev/endurox](https://github.com/endurox-dev/endurox)

**C; transaction-processing middleware, specifically the TMQ persistent-message-queue subsystem.** Counted once as a monorepo. Study messaging integrated with XA transaction coordination and service invocation.

- **C1:** Enqueue initially writes and locks a message in the active area; XA commit makes it visible in committed storage. Dequeue uses locking and a deletion command finalized at commit. The documented restriction on enqueueing and dequeueing the same message within one transaction exposes the actual visibility model. [Persistent queue implementation overview](https://github.com/endurox-dev/endurox/blob/master/doc/persistent_message_queues_overview.adoc).
- **C2:** Queue spaces support explicit `tpenqueue`/`tpdequeue` operations and automatic forwarding to services, with retry, reply, and failure queues. The same transactional storage primitive therefore serves both pull-based work and service-driven workflows. [Manual and automatic queue operation](https://github.com/endurox-dev/endurox/blob/master/doc/persistent_message_queues_overview.adoc).

## Replicated logs and replayable messaging

### 9. [apache/kafka](https://github.com/apache/kafka)

**Java and Scala; partitioned, durable event broker.** The focus is the broker's log and replication machinery, not the surrounding stream-processing ecosystem.

- **C1:** The design explains in-sync replicas, committed offsets, leader failure, and how acknowledgement and minimum-replica policies affect accepted writes. This is useful for separating the log's committed prefix from data merely present on a replica. [Kafka 4.1 design documentation](https://kafka.apache.org/41/design/design/).
- **C3:** Sequential append, operating-system page caching, message batching, compression, and efficient transfer address disk, memory-copy, and network constraints together. Partition logs provide a clear architectural unit for reasoning about those optimizations and their ordering scope. [Persistence and efficiency design](https://kafka.apache.org/41/design/design/).

### 10. [apache/pulsar](https://github.com/apache/pulsar)

**Java; broker and managed-ledger subsystems of the Pulsar monorepo.** Study the separation of broker ownership from durable storage; BookKeeper is a dependency here, not a second counted repository.

- **C1:** BookKeeper ledgers have a single writer and become read-only after closure or recovery. Managed ledgers track persistent subscription cursors, and old ledger data can be reclaimed only after the relevant cursors pass it. Crash recovery and slow consumers therefore meet at explicit storage boundaries. [Pulsar 4.0 architecture](https://pulsar.apache.org/docs/4.0.x/concepts-architecture-overview/).
- **C2:** A managed ledger turns multiple storage ledgers into one topic stream with independent cursors. Brokers, bookies, and metadata services have separate responsibilities, supporting multiple subscription behaviors and independent storage expansion. [Brokers, storage, and managed ledgers](https://pulsar.apache.org/docs/4.0.x/concepts-architecture-overview/).

### 11. [apache/rocketmq](https://github.com/apache/rocketmq)

**Java; distributed messaging broker with transactional publication.** Study its transaction-message protocol and the distinction between local business transactions and downstream consumption.

- **C1:** A prepared half-message remains invisible until the producer reports its local transaction outcome. When that report is missing, the broker checks the producer's transaction state and eventually commits or rolls back publication. This coordinates eventual publication with a local transaction; it does not make consumer side effects part of that transaction. [Transaction-message protocol](https://rocketmq.apache.org/docs/featureBehavior/04transactionmessage/).
- **C2:** Topics contain message queues, while consumer groups carry subscription, filtering, retry, and consumption-progress configuration. Independent groups receive independent views of a topic, and group members share work. [Domain model](https://rocketmq.apache.org/docs/domainModel/01main/).

### 12. [redpanda-data/redpanda](https://github.com/redpanda-data/redpanda)

**C++; Kafka-compatible broker built on Seastar.** Study how partition replication and explicit CPU ownership fit together in one server. Inclusion concerns inspectable implementation, not a claim about uniform licensing across these projects.

- **C1:** Partition data is replicated through Raft groups, and cluster metadata has its own controller group. Producer acknowledgement policy and quorum behavior determine which failure cases an accepted write survives. [Redpanda architecture](https://docs.redpanda.com/streaming/current/get-started/architecture/).
- **C3:** A thread-per-core execution model uses asynchronous communication between shards to reduce shared-memory locking and scheduling overhead. Tiered storage introduces a separate distinction between recent local data and remotely stored log data, with metadata and caching implications. [Execution and storage architecture](https://docs.redpanda.com/streaming/current/get-started/architecture/).

### 13. [apache/iggy](https://github.com/apache/iggy)

**Rust; persistent streaming broker.** Study a newer implementation whose recent replication and storage changes make design tradeoffs unusually visible; do not assume pre-0.9 descriptions apply unchanged.

- **C1:** Version 0.9 uses Viewstamped Replication with separate metadata and partition groups. Its `replicated` acknowledgement policy waits for quorum commit without an additional stable-storage barrier; `persisted` requires recoverable stable-storage copies at quorum. Message and consumer-offset durability are configured independently. The release also describes deterministic fault simulation and crash tests. [0.9.0 architecture and release notes](https://iggy.apache.org/blogs/2026/09/21/release-0.9.0/).
- **C3:** The thread-per-core and `io_uring` migration discusses shard ownership, batching, asynchronous borrow hazards, and the difference between I/O submission and completion ordering. These are concrete costs and correctness obligations behind its performance design. [Execution-engine migration](https://iggy.apache.org/blogs/2026/02/27/thread-per-core-io_uring/).

### 14. [liftbridge-io/liftbridge](https://github.com/liftbridge-io/liftbridge)

**Go; durable, partitioned streams layered over NATS.** Study a smaller replicated-log implementation and the boundary between messaging transport and storage consensus.

- **C1:** Metadata uses Raft, while stream replication tracks in-sync replicas and leader epochs. Follower recovery uses epoch history to decide truncation, avoiding the ambiguity of recovering from a high-water mark alone. Consumers receive committed data. [Replication protocol](https://liftbridge.io/docs/replication-protocol.html).
- **C2:** Streams and partitions add retention and replay over NATS subjects, while consumer groups distribute processing. This makes a useful comparison with JetStream's integration inside the NATS server. [System overview](https://liftbridge.io/docs/overview.html).

The inspected overview and replication documents carry 2022 and 2021 update dates respectively; they are architectural evidence, not verification that every described interface is current.

## Work queues and historical designs

### 15. [nsqio/nsq](https://github.com/nsqio/nsq)

**Go; decentralized topic/channel work-distribution system.** Study flow control and failure semantics without assuming the cluster is a replicated storage system.

- **C1:** Consumers finish or requeue messages, and processing timeouts return outstanding work. The design explicitly acknowledges possible loss of in-memory or unflushed messages after an unclean `nsqd` shutdown and does not provide built-in replication between nodes. These boundaries are central to understanding the guarantees. [NSQ design](https://nsq.io/overview/design.html).
- **C3:** Client `RDY` counts provide credit-based flow control; bounded in-memory buffering spills backlog to disk. Topic fanout and channel-level work sharing make it possible to trace where independent backlogs and slow consumers consume resources. [Buffering, discovery, and delivery architecture](https://nsq.io/overview/design.html).

### 16. [beanstalkd/beanstalkd](https://github.com/beanstalkd/beanstalkd)

**C; compact job-queue server with optional persistent binlogging.** Study an unusually explicit work-item state machine and a small protocol with meaningful edge cases.

- **C1:** Jobs transition among ready, reserved, delayed, and buried states. Reservation deadlines, timeout-driven release, and `DEADLINE_SOON` prevent a worker from indefinitely blocking while its existing reservation expires. [Protocol specification](https://github.com/beanstalkd/beanstalkd/blob/master/doc/protocol.txt).
- **C2:** Named tubes, watch lists, priorities, delayed availability, and opaque payloads support multiple worker and scheduling patterns. Persistence is opt-in, and binlog synchronization can be periodic or disabled; durable deployment behavior therefore depends on configuration. [Server manual and binlog controls](https://github.com/beanstalkd/beanstalkd/blob/master/doc/beanstalkd.ronn).

### 17. [antirez/disque](https://github.com/antirez/disque)

**C; historical experimental distributed work queue.** The repository describes a beta experiment; the latest commit returned by the GitHub API during research was [dated 2016-04-29](https://github.com/antirez/disque/commit/0192ba7e1cda157024229962b7bee1c6e86d771b). Include it for study, not as an implication of current maintenance.

- **C1:** Acknowledgement triggers distributed garbage collection rather than immediate unilateral deletion. The implementation tracks confirmations from replicas, handles acknowledgements for jobs unknown locally, and retries coordination with backoff and jitter. This is a concrete study of avoiding job resurrection while eventually releasing replicated state. [Acknowledgement and garbage-collection implementation](https://github.com/antirez/disque/blob/master/src/ack.c).
- **C2:** Per-job replication, retry, lifetime, and queue controls separate scheduling and availability policy from payload handling. Its availability-oriented design deliberately does not offer strict global FIFO, and optional disk persistence is distinct from replication. [Project design and protocol description](https://github.com/antirez/disque).

### 18. [twitter-archive/kestrel](https://github.com/twitter-archive/kestrel)

**Scala; archived, inactive persistent queue server.** Study a historical design where simple independent servers place distribution responsibilities on clients.

- **C1:** Reliable reads provisionally remove items and require a later close/confirmation; abort or disconnect restores the item. A sequential journal supports recovery of queue operations. These mechanisms expose the boundary between delivery and completed processing. [Kestrel guide](https://github.com/twitter-archive/kestrel/blob/master/docs/guide.md).
- **C3:** Read-behind limits resident backlog while journals retain queued data, and checkpointing/compaction bounds replay and disk accumulation. Servers do not coordinate a global queue order: client distribution across independent nodes trades away global FIFO rather than hiding that cost. [Journal, memory, and deployment design](https://github.com/twitter-archive/kestrel/blob/master/docs/guide.md).

## MQTT brokers and persistent sessions

### 19. [eclipse-mosquitto/mosquitto](https://github.com/eclipse-mosquitto/mosquitto)

**C; MQTT broker.** Study persistent sessions, protocol handshakes, and resource limits in a comparatively compact server.

- **C1:** Persistence settings govern saving and restoring connection, subscription, and message state; periodic saves are not equivalent to making every acceptance immediately power-failure durable. In-flight QoS handshakes, queued-message limits, and session expiration interact with ordering and resource exhaustion. [Broker configuration manual](https://mosquitto.org/man/mosquitto-conf-5.html).
- **C3:** In-flight and queued-message bounds constrain memory and backpressure. The manual also explains the cost of eliminating duplicate deliveries from overlapping subscriptions, tying a protocol feature to runtime work. [Resource and delivery controls](https://mosquitto.org/man/mosquitto-conf-5.html).
- **C4:** The changelog documents releases across 2020–2026, specific regression fixes, and staged deprecation of configuration mechanisms in favor of plugins. The persistence documentation describes reading older database formats while writing the current format: concrete compatibility work beyond repository age. [Changelog](https://github.com/eclipse-mosquitto/mosquitto/blob/master/ChangeLog.txt).

### 20. [emqx/emqx](https://github.com/emqx/emqx)

**Erlang; clustered MQTT broker, especially durable storage and sessions.** The repository states that releases from 5.9 use BSL 1.1 and that multi-node clustering requires a license file; this is a source-access selection, not an open-source-license classification.

- **C1:** Durable storage distinguishes local RocksDB storage from replicated Raft-backed shards. Its atomicity and consistency boundaries are expressed in terms of slabs, identified by shard and generation, rather than an unspecified global transaction. [Durable-storage design](https://docs.emqx.com/en/emqx/latest/develop/design/durable-storage.html).
- **C2:** A common storage model separates databases, shards, generations, slabs, streams, and topic/timestamp/value records. Backend independence and wildcard-oriented batched replay allow message and session machinery to reuse a storage interface while maintaining different logical state. [Storage abstractions and replay](https://docs.emqx.com/en/emqx/latest/develop/design/durable-storage.html).

### 21. [vernemq/vernemq](https://github.com/vernemq/vernemq)

**Erlang; clustered MQTT broker.** Study the explicit difference between converging cluster metadata and protecting queued message bodies.

- **C1:** Subscription and retained-message metadata are eventually consistent. The partition guide identifies an uncertainty window in which new remote subscriptions may be missed or duplicate clients may exist, and describes configurable refusal of operations after partition detection. [Network-partition semantics](https://docs.vernemq.com/vernemq-clustering/netsplits).
- **C2:** Cluster membership, client sessions, queue migration, and node-independent connection placement provide a reusable model for operating stateful MQTT services. Graceful node departure can migrate queues; removing a dead node cannot recover its locally stored messages, which are not replicated by default. This is an important limit of the abstraction. [Cluster membership and queue migration](https://docs.vernemq.com/vernemq-clustering/introduction).

### 22. [nanomq/nanomq](https://github.com/nanomq/nanomq)

**C; edge-oriented MQTT broker.** The canonical repository is now under `nanomq`. Study the NNG-based asynchronous execution model and the mechanics of retransmission under load.

- **C1:** The batch-resend design coordinates cached pending messages with acknowledgements, timers, message expiry, duplicate flags, and a busy transport pipe. These state transitions determine whether a retry is still valid and when another send can safely begin. [Batch-resend design](https://github.com/nanomq/nanomq/blob/master/docs/en_US/batch_resend.md).
- **C3:** The broker uses asynchronous message passing and scheduling; batched resend trades additional cached work for fewer per-message resend triggers and lookups. The design document exposes the memory/work tradeoff instead of relying solely on benchmark claims. [Resend implementation rationale](https://github.com/nanomq/nanomq/blob/master/docs/en_US/batch_resend.md).

Included as a substantive message broker; this entry does not claim replicated durable storage.

### 23. [moscajs/aedes](https://github.com/moscajs/aedes)

**JavaScript; embeddable MQTT broker.** Study broker composition and backpressure inside a host application. Default persistence is in memory; restart durability depends on the selected persistence backend.

- **C1:** A frozen subscriber socket can occupy concurrency slots and stall delivery; `drainTimeout` provides a disconnection boundary. Limits on pending inbound QoS 2 messages and topic structure address retained handshake state and hostile inputs. [Aedes API and flow-control documentation](https://github.com/moscajs/aedes/blob/main/docs/Aedes.md).
- **C2:** The message emitter handles dispatch while persistence stores subscriptions, retained messages, wills, and QoS-related state. Authentication hooks and stream-oriented integration allow the same broker engine to be embedded with different transports and storage choices. [Broker interfaces and extension points](https://github.com/moscajs/aedes/blob/main/docs/Aedes.md).

## Embedded durable queues

### 24. [peter-wangxu/persist-queue](https://github.com/peter-wangxu/persist-queue)

**Python; local persistent queue library with file and SQLite implementations.** Study the smaller-scale version of acknowledgement and recovery problems without a network server.

- **C1:** The file queue uses a mutex and condition variables for concurrent access, persists head/tail metadata through an atomic replacement, and truncates a recovered chunk to its committed position. Same-filesystem checks protect the metadata replacement assumption. Flushes and explicit synchronization occur at different points, so process-restart persistence should not be generalized to unconditional power-loss safety. [File-queue implementation](https://github.com/peter-wangxu/persist-queue/blob/master/persistqueue/queue.py).
- **C2:** Queue-like operations, configurable serialization, and file/SQLite variants support ordinary FIFO use, acknowledgement-oriented consumption, and other ordering/deduplication policies. The file implementation provides its own chunk and metadata machinery, rather than merely wrapping a remote broker. [API and implementation families](https://github.com/peter-wangxu/persist-queue).

### 25. [i-e-b/DiskQueue](https://github.com/i-e-b/DiskQueue)

**C#; embedded transactional disk queue for .NET.** Derived substantially from Rhino Queues, but retained as a separately evolved implementation with its own session machinery and failure tests; its ancestor is not counted separately.

- **C1:** A session accumulates enqueue/dequeue operations, waits for outstanding writes, flushes data, and commits the operation transaction. Disposal restores uncommitted operations. Failure propagation is material: the test suite injects a write-failing filesystem and verifies that dequeues remain possible while enqueue/flush fails. [Session implementation](https://github.com/i-e-b/DiskQueue/blob/master/src/DiskQueue/Implementation/PersistentQueueSession.cs), [write-failure tests](https://github.com/i-e-b/DiskQueue/blob/master/src/DiskQueue.Tests/WriteFailureTests.cs).
- **C3:** The session buffers small enqueues into contiguous writes and switches to asynchronous writing above a size threshold. Explicit flush boundaries amortize I/O while preserving an inspectable commit sequence; pending write failures and timeouts are collected before commit. [Buffering and commit path](https://github.com/i-e-b/DiskQueue/blob/master/src/DiskQueue/Implementation/PersistentQueueSession.cs).

## Coverage, search method, and limitations

Discovery used live web searches across more than six distinct angles: general distributed brokers; durable work queues and acknowledgement protocols; JMS/AMQP stores and transaction journals; replayable logs and replication; Rust and C++ storage engines; Crystal and smaller broker communities; MQTT clustering and durable sessions; XA-integrated queues; historical distributed queues; and embedded Python/.NET persistence. Later language-specific and alternative-broker searches increasingly repeated retained projects or produced candidates outside the chosen scope. The list spans eleven implementation languages and both large foundations and smaller project communities; it is deliberately selective rather than exhaustive.

Every retained canonical GitHub repository was opened or checked through GitHub, and at least one additional primary architecture document, manual, implementation file, or test was read for each. Search snippets and star counts were not treated as evidence. Canonical-location checks resolved Artemis to `apache/artemis` and NanoMQ to `nanomq/nanomq`; Qpid Broker-J is explicitly an official mirror. A monorepo appears only once, with the relevant subsystem identified.

Excluded families include client SDKs, protocol transports such as ZeroMQ/NNG alone, job frameworks whose broker is another product, managed services without a substantive GitHub implementation, tutorial queues, lists of links, and duplicate forks. Embedded libraries were retained only where they implement meaningful storage/recovery machinery. BookKeeper is discussed through Pulsar's storage boundary rather than counted as a standalone broker. Disque and Kestrel are marked as historical; inclusion elsewhere is not an assertion of current maintenance or deployment suitability.

Versioned and older design material is labeled where it matters, especially Kafka, Pulsar, Qpid, and Liftbridge. Default-branch links may change after the research date. No candidate code was executed, dependencies installed, or performance measurements reproduced. Durability and delivery claims remain conditional on the documented configuration and failure model. Statements about what an engineer can learn are grounded interpretation of the cited mechanisms, not an independent correctness audit or comparative benchmark.
