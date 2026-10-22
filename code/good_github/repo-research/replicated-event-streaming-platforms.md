# Replicated event streaming platforms

Research date: **2026-10-09**.

This report selects 20 repositories implementing retained, replayable event streams with replicated storage, or purpose-built replicated-log foundations used to construct those platforms. It covers broker-local replication, separate log-storage services, and shared-object-storage designs. The last group explicitly delegates some durability to its storage backend. A replicated metadata service alone is insufficient for inclusion. Stream processors, client SDKs, connectors, and generic consensus libraries are outside scope.

The entries are engineering study recommendations, not deployment rankings or claims that every component is exemplary. Related layers are identified: for example, Pulsar and BookKeeper, and RabbitMQ and Osiris, expose different substantial implementations within the same ecosystem.

## Criteria legend

- **C1 — Correctness:** difficult invariants, concurrency, adversarial conditions, recovery, or failure semantics.
- **C2 — Abstractions:** substantial reusable interfaces or models serving multiple applications.
- **C3 — Performance and structure:** concrete performance constraints addressed through understandable architectural choices.
- **C4 — Evolution:** evidence across years of compatibility work, testing, or complexity management; age alone does not qualify.

## Partitioned brokers and streaming layers

### 1. [apache/kafka](https://github.com/apache/kafka)

**Language / role:** Java and Scala; partitioned event-log broker and surrounding platform. The relevant subsystem is the broker's storage, replication, and consumer coordination, rather than merely the Kafka Streams library in the same repository.

Study how an ordered partition log becomes a reusable ingestion and replay service while accommodating slow followers and independent consumers.

- **C1:** The replication design distinguishes a partition leader, its in-sync replicas, and the acknowledgement conditions under which records become durable. Replica catch-up, membership changes, and leader election connect directly to the committed-prefix invariant and availability tradeoffs.
- **C2:** Partition offsets, retained logs, consumer groups, and compaction provide several consumption and state-reconstruction models over the same storage machinery.
- **C3:** Shared batch formats, sequential I/O, page-cache use, and network transfer optimizations reduce copying and per-record overhead. The design also explains why TLS changes the zero-copy path.

**Entry point:** [Kafka 4.1 design documentation](https://kafka.apache.org/41/design/design/) supplies the replication, log, consumer, and I/O explanations supporting these criteria.

### 2. [apache/pulsar](https://github.com/apache/pulsar)

**Language / role:** Java; broker, managed-ledger, and subscription platform using BookKeeper for replicated persistence.

The useful study boundary is between topic ownership in a broker and durable topic history in bookies. This provides a concrete alternative to keeping a partition's full history on its serving broker.

- **C1:** A managed ledger composes successive single-writer ledgers. Recovery closes a failed writer's ledger and resumes through a new one, while subscription cursors maintain separate consumption positions.
- **C2:** The managed-ledger abstraction combines an append-only history with multiple persistent cursors, supporting independent subscriptions without duplicating each subscription's payload history.
- **C3:** Brokers cache the recent tail and fetch older backlog from BookKeeper; broker and storage capacity can be scaled separately. Geo-replication adds another useful layer: local records are read and republished to remote clusters.

**Entry point:** [Architecture overview](https://pulsar.apache.org/docs/next/concepts-architecture-overview/), especially managed ledgers, persistent storage, and replication. This is the project's **Next** documentation, not a release-pinned compatibility promise.

### 3. [redpanda-data/redpanda](https://github.com/redpanda-data/redpanda)

**Language / role:** C++; Kafka-compatible streaming broker built on Seastar.

Study how partition-level consensus is integrated with a runtime organized around CPU cores. The interest lies in coordinating ownership, replication, and resource scheduling inside one broker.

- **C1:** Each partition is a Raft group. Leader terms, majority acknowledgement for `acks=all`, and rejection of stale leadership define the write/failover contract; a separate controller partition handles cluster metadata.
- **C3:** The architecture assigns work to cores and exchanges messages between them, with explicit memory and I/O management. This exposes the tradeoffs between avoiding shared-memory contention and paying for cross-core communication.

**Entry point:** [Redpanda architecture](https://docs.redpanda.com/streaming/current/get-started/architecture/), covering Raft, the controller, and the thread-per-core runtime. Performance mechanisms are the evidence here; vendor benchmark ratios are not used.

### 4. [apache/rocketmq](https://github.com/apache/rocketmq)

**Language / role:** Java; retained-message broker with logical queues over a physical commit log. This entry concerns the main broker/store and controller-based failover, not the separate stream-processing integrations.

Study the separation between physical append storage, logical consumption indexes, and the controller's knowledge of safe replicas.

- **C1:** Controller-mode replication maintains a `SyncStateSet`, excludes learners from election, tracks epochs, and offers acknowledgement/minimum-in-sync-replica controls. The documented option to elect outside the safe set makes the availability-versus-data-loss tradeoff explicit. See [automatic failover](https://rocketmq.apache.org/docs/deploymentOperations/03autofailover/).
- **C2:** A physical commit log and lightweight logical queue indexes support ordered consumption and offset-based replay. Retention is independent of consumption, and disk-pressure cleanup complicates the apparent retention contract. See [message storage and cleanup](https://rocketmq.apache.org/docs/featureBehavior/11messagestorepolicy/).

**Entry points:** The two documents above connect the replication protocol to the storage model. The storage page mixes local-broker and cloud-service discussion; this assessment uses its explicitly described local-file behavior.

### 5. [nats-io/nats-server](https://github.com/nats-io/nats-server)

**Language / role:** Go; NATS server, specifically its **JetStream** persistent-streaming subsystem. NATS Core by itself is not the retained replicated log considered here.

Study the consequences of placing stream contents, consumer progress, and administrative metadata in distinct consensus groups.

- **C1:** JetStream uses separate Raft groups for metadata, individual streams, and replicated consumer state. Preserving a stream does not automatically preserve every consumer's acknowledgement position: replication settings for those objects matter independently.
- **C2:** Streams represent retained messages, while consumers represent delivery and acknowledgement state over those messages. Their separate placement and lifecycles support multiple consumption arrangements without making the stream synonymous with one queue consumer.

**Entry point:** [JetStream clustering](https://docs.nats.io/learn/topologies/jetstream-in-a-cluster). It also documents an important configuration boundary: a clustered installation can still contain a stream with only one replica; cluster membership alone does not establish payload redundancy.

### 6. [rabbitmq/rabbitmq-server](https://github.com/rabbitmq/rabbitmq-server)

**Language / role:** Erlang; messaging-server monorepo, specifically **Streams and Super Streams**. Classic queues and quorum queues are not counted as separate repositories or interchangeable streaming implementations.

Study how retained logs coexist with established broker routing and management facilities, and how stream membership differs from the data path.

- **C1:** Streams have a leader and replicas, with majority availability requirements. Replica management has its own constraints: adding a replica can be blocked while an existing replica is out of sync because membership information is coordinated separately from the stream log.
- **C2:** Nondestructive consumption, replay positions, and partitioned Super Streams support independent readers and larger logical streams.
- **C3:** The implementation is deliberately disk- and page-cache-oriented. Consumer offset tracking adds non-message records to the stream, illustrating how a seemingly small API feature affects storage accounting and throughput.

**Entry point:** [RabbitMQ Streams documentation](https://www.rabbitmq.com/docs/streams), including replication, replica management, retention, and offset tracking. Osiris, listed below, is the separately reusable log engine beneath this platform.

### 7. [fluvio-community/fluvio](https://github.com/fluvio-community/fluvio)

**Language / role:** Rust; partitioned streaming platform with separate control and data services.

The formerly used `infinyon/fluvio` URL redirects to this canonical repository. Its README describes the transition to community-hosted builds and releases; this report counts the project once under its current owner.

- **C1:** Streaming Processing Units hold leader/follower copies of partitions. Ordered immutable records, follower replication, and replacement of failed leaders make replica progress and log ownership central study topics.
- **C3:** The controller manages topology while SPUs handle data and replication. The storage design combines a single writer with concurrent readers, segmented retention, and zero-copy disk-to-network transfer, making the interaction of retention and concurrent delivery especially useful to inspect.

**Entry point:** [Fluvio architecture overview](https://www.fluvio.io/docs/fluvio/concepts/architecture/overview/). This supports the SC/SPU split, replication model, and I/O mechanisms; replication must actually be configured above one copy to provide redundant event storage.

### 8. [apache/iggy](https://github.com/apache/iggy)

**Language / role:** Rust; streaming server with Viewstamped Replication and a thread-per-core runtime.

**Status:** The inspected documentation explicitly says the system has not reached a 1.0 production release. VSR is now integrated into the standard server rather than merely a proposed clustering feature, but clustering is disabled by default and protocol/configuration changes remain possible.

- **C1:** Metadata has one consensus group and each partition has its own group for messages and consumer offsets. View changes, persistent WAL recovery, journal repair, session fencing, and duplicate detection are accompanied by deterministic simulation and cross-SDK behavioral tests.
- **C3:** The repository describes a shared-nothing, thread-per-core design using `io_uring`/Compio. It is useful for studying how explicit shard ownership and asynchronous disk/network operations interact with a replicated state machine.

**Entry points:** [VSR architecture and implementation status](https://iggy.apache.org/docs/clustering/vsr/) and the [consensus source subtree](https://github.com/apache/iggy/tree/master/core/consensus). Treat mainline capabilities separately from older released wire protocols.

### 9. [liftbridge-io/liftbridge](https://github.com/liftbridge-io/liftbridge)

**Language / role:** Go; durable replicated streams associated with NATS subjects.

Study how durable stream state can be layered onto an existing messaging namespace. The author's [architecture introduction](https://bravenewgeek.com/introducing-liftbridge-lightweight-fault-tolerant-message-streams/) explains independent stream replicas and distinguishes Raft coordination from the data log's in-sync-replica approach.

- **C1:** The changelog exposes concrete recovery hazards: corrupt index reconstruction, partial segment deletion, snapshot restoration before server initialization, and a snapshot containing a leader outside the ISR. Named regression tests and recovery changes make these useful invariants to investigate rather than abstract fault-tolerance claims.
- **C3:** Reverse readers, backward index/segment scanners, and reverse cursor lookup avoid scanning an entire stream to find recent state. Timer-based batching is another explicit throughput mechanism.

**Entry points:** The author's architecture article above and the [changelog](https://github.com/liftbridge-io/liftbridge/blob/master/CHANGELOG.md). Its January 2026 release records a Basekick Labs maintainer transition and dependency/CI updates; describing this repository as simply abandoned would miss that evidence.

## Shared storage and stream-native data systems

### 10. [AutoMQ/automq](https://github.com/AutoMQ/automq)

**Language / role:** Java and Scala; a substantive Kafka fork with the **S3 storage adapter and S3Stream** as the relevant new subsystems.

**Replication boundary:** This is a shared-storage variant. Event durability depends on the object-storage service's redundancy and guarantees; the broker does not reproduce Kafka's usual arrangement of local payload copies on peer brokers. Public-repository behavior should also be distinguished from advertised enterprise storage/latency options.

- **C2:** The adapter replaces Kafka log abstractions, while S3Stream exposes stream IDs, offsets, asynchronous append/fetch, and trim operations. This separates the storage interface from the Kafka-facing broker and is substantial independent implementation work, not a renamed upstream fork.
- **C3:** Its WAL, batching, log cache, and block cache address object-store operation costs and read latency. Shared history also changes the data movement required when assigning partitions to brokers.

**Entry points:** The repository's architecture section and the [S3Stream subtree/API description](https://github.com/AutoMQ/automq/tree/main/s3stream). These support the architectural assessment without relying on numerical cost or latency marketing claims.

### 11. [pravega/pravega](https://github.com/pravega/pravega)

**Language / role:** Java; elastic event-stream storage with controllers, segment stores, and replicated durable logs.

Study how stream topology changes interact with transactions. A stream is assembled from segments that can be sealed, split, and merged rather than being permanently tied to a fixed partition set.

- **C1:** Transaction segments must merge idempotently, commit/abort decisions require guarded metadata transitions, and transaction ordering must remain coherent across scaling. The durable-log layer uses BookKeeper and fencing to prevent an obsolete segment-container owner from continuing writes.
- **C2:** Controllers manage stream and transaction lifecycles, while segment stores implement the byte/event storage path. This division makes the stream/segment abstraction reusable across different scaling and reader behaviors.
- **C3:** A synchronous durable-log tier protects the recent tail while asynchronous long-term storage holds history, separating write acknowledgement from bulk retention work.

**Entry point:** [Pravega internals](https://pravega.io/blog/2018/10/17/pravega-internals/). This is a substantive **2018 architectural explanation**, useful for the underlying design; it is not evidence that every implementation detail or default is unchanged today.

### 12. [hstreamdb/hstream](https://github.com/hstreamdb/hstream)

**Language / role:** Haskell server and associated C++/LogDevice-based storage integration; streaming database/platform with durable streams and subscriptions.

This entry concerns HStream's server/storage integration and stream APIs. It is broader than a standalone SQL processor, and it is not counted as an independent reimplementation of every LogDevice mechanism.

- **C1:** The HStore design describes a Flexible-Paxos-based replication layer, nondeterministic data placement, and online replication-group reconfiguration. These expose correctness questions around safe placement changes and continued ordered reads.
- **C2:** HStore separates streaming APIs, replication, local RocksDB storage, and long-term offloading behind a unified stream interface. HServer separately implements access, SQL planning, dataflow operators, and execution management.
- **C3:** Batch append/read operations and separation of recent local data from historical object/HDFS storage address different access patterns without requiring the client to use two storage APIs.

**Entry points:** [HStore architecture](https://docs.hstream.io/reference/architecture/hstore) and [HServer architecture](https://docs.hstream.io/reference/architecture/hserver). These are architecture evidence, not an assertion of a current support commitment or release cadence.

### 13. [apache/fluss](https://github.com/apache/fluss)

**Language / role:** Java; streaming storage for append logs and primary-key tables. The relevant subsystem is the replicated **LogTablet** and its relationship to **KvTablet** state.

Study a system where a replayable changelog and a materialized key-value view must agree about what has become visible.

- **C1:** Tablet leaders and followers maintain in-sync replicas and a high watermark. For primary-key tables, log progress must be coordinated with key-value application. A new owner restores a completed remote snapshot and replays subsequent log records, exposing the snapshot/log consistency boundary.
- **C2:** Tables divide into buckets that act as ordering and replication units. Log scans, snapshot access, and primary-key lookups offer distinct read models over related storage state.
- **C3:** Coordinator metadata is separated from tablet data serving, while remote history and snapshots reduce the amount of state tied to one serving process.

**Entry point:** [Fluss architecture](https://fluss.apache.org/docs/next/concepts/architecture/). This is **Next** documentation; it describes the development architecture rather than guaranteeing every capability in every released version.

### 14. [kurrent-io/KurrentDB](https://github.com/kurrent-io/KurrentDB)

**Language / role:** C#; replicated event database, formerly EventStoreDB. The rename is one repository lineage, not an extra entry.

Study an event database's acknowledgement and subscription contract alongside the operational compatibility required to evolve a long-lived cluster.

- **C1:** The inspected cluster documentation distinguishes voting replicas from asynchronous read-only replicas. Successful writes involve leader persistence, replication to a majority, and indexing before acknowledgement. Read-only replicas can serve catch-up subscriptions without participating in elections or the write quorum. See [v26.1 cluster configuration](https://docs.kurrent.io/server/v26.1/configuration/cluster).
- **C4:** The upgrade guide covers online rolling upgrades from releases spanning 22.10 through 25.x, follower-first ordering, renamed configuration/directories, and removal of obsolete options. Preserving old-directory fallbacks during the EventStoreDB-to-KurrentDB transition is concrete compatibility work, not merely an old repository date.

**Entry points:** The versioned cluster guide above and the [v26.0 upgrade guide](https://docs.kurrent.io/server/v26.0/quick-start/upgrade-guide). These claims are intentionally tied to the documented versions rather than generalized to every newer clustering option.

### 15. [gazette/core](https://github.com/gazette/core)

**Language / role:** Go; distributed journal broker and consumer/recovery infrastructure.

Gazette is particularly useful for studying what changes when the broker sequences **bytes** rather than understanding records. Clients choose framing and serialization; immutable offset ranges are the common currency.

- **C2:** Journals and label selectors avoid baking topic schemas or record formats into the broker. Consumer recovery logs record database file operations, allowing embedded databases and hot standbys to reuse the same journal substrate.
- **C3:** Brokers serve and replicate recent content while historical fragments live in blob storage. New assignments do not require downloading the full history, although reads can wait for recent content to become visible in the backing store. This makes startup speed versus read availability an explicit tradeoff.

**Entry point:** [Architecture goals and non-goals](https://github.com/gazette/core/blob/master/docs/architecture-design-goals-and-nongoals.rst). It also explains how etcd leases gate membership changes. Its failure-availability goals are design intent; this review does not treat them as independently demonstrated guarantees.

## Replicated-log foundations and historical implementations

### 16. [apache/bookkeeper](https://github.com/apache/bookkeeper)

**Language / role:** Java; replicated append-only ledger storage underlying streaming platforms. The ledger client, bookie server, and recovery protocol are the principal study targets.

Study how a writer can spread a log over storage nodes without electing a storage-node leader for every ledger. This is a reusable foundation rather than a complete Kafka-style broker API.

- **C1:** Ensemble, write-quorum, and acknowledgement-quorum sizes determine which failures can be tolerated. Fencing must intersect potential write quorums so an old writer can no longer acknowledge new entries; recovery also reconciles the last confirmed entry and ledger closure.
- **C2:** Single-writer ledgers, ensemble changes, and ledger-to-log composition separate durable ordering from application-specific topic or subscription machinery. The protocol explains the extra fencing needed when composing ledgers into a continuing log.
- **C3:** Striping writes across ensembles separates placement and quorum choices from the logical append sequence.

**Entry point:** [BookKeeper protocol](https://bookkeeper.apache.org/docs/development/protocol/). DistributedLog is not counted separately: its [old repository](https://github.com/apache/distributedlog) says core development moved into BookKeeper after becoming a subproject.

### 17. [rabbitmq/osiris](https://github.com/rabbitmq/osiris)

**Language / role:** Erlang; independently reusable replicated append-only log used by RabbitMQ Streams. Its role is storage and replication machinery, while `rabbitmq-server` supplies the surrounding broker platform.

Study the exact point where received replica progress becomes an externally visible committed offset.

- **C1:** The writer derives committed progress from replica offsets, rejects acknowledgements from unknown replicas and backwards progress, and distinguishes duplicate producer sequences from records that are safe to acknowledge. Recovery of tracking state and the ordering of reader/writer notifications make the failure semantics inspectable.
- **C3:** The writer uses a batch-processing server and combines payload and tracking work. Release changes include offset/timestamp index search improvements and conditional `sendfile` use, connecting concrete hot paths with platform constraints.
- **C4:** The repository records use in RabbitMQ since 2021; subsequent release notes document compatibility-sensitive changes, replica-reader crash fixes, retention work, and platform-specific transfer behavior.

**Entry points:** [Writer implementation](https://github.com/rabbitmq/osiris/blob/main/src/osiris_writer.erl) and [release history](https://github.com/rabbitmq/osiris/releases). The source was read directly as well as through its GitHub page.

### 18. [facebookarchive/LogDevice](https://github.com/facebookarchive/LogDevice)

**Language / role:** C++; distributed log-storage service with separate sequencing and storage responsibilities.

**Status:** Official archived repository; GitHub marks it archived on **2022-01-07**, and its README says it is no longer supported. It remains a substantive historical implementation, not a current deployment recommendation.

- **C1:** Concurrent appenders and readers must agree on log-sequence-number order despite failures. Replica placement spans failure domains, and the read model explicitly accounts for gaps or lost ranges rather than pretending every historical record must always be recoverable.
- **C3:** Records can use different storage-node subsets, and placement can avoid slow or failed nodes. This separates sequencing from capacity and load distribution, in contrast to assigning an entire partition to one fixed replica set.
- **C2:** The distributed-log API is designed as a foundation for multiple event and state-replication applications, while local RocksDB storage multiplexes many logs.

**Entry point:** [LogDevice concepts and architecture](https://logdevice.io/docs/Concepts.html). The archive heading links the verified canonical GitHub location; the old Facebook owner is not counted separately.

### 19. [wepay/waltz](https://github.com/wepay/waltz)

**Language / role:** Java; distributed transaction/write-ahead log, with ordering servers separated from storage replicas.

**Status:** Included as a historical design study. The inspected GitHub page did not establish an archival banner, but this review did not establish a current maintenance or support commitment either.

- **C1:** Monotonic session IDs obtained through ZooKeeper fence obsolete servers. A new session must recover storage before serving, and an unavailable storage node cannot simply rejoin without that recovery process. Majority writes, truncation, and session transitions make the append contract unusually explicit. See [server/storage communication](https://wepay.github.io/waltz/docs/server-storage-communication).
- **C3:** Optimistic conflict detection uses application-provided lock identifiers mapped into a fixed-size table of high-water marks. This provides a concrete case study in bounding conflict-tracking memory and understanding the concurrency consequences of hashing. See [optimistic locking](https://wepay.github.io/waltz/docs/concurrency-control-optimistic-locking).

**Entry points:** The two design documents above. The repository also describes a failure-injection smoke test with random process termination and transaction/checksum validation; this review read that description but did not run the test.

### 20. [nats-io/nats-streaming-server](https://github.com/nats-io/nats-streaming-server)

**Language / role:** Go; the former NATS Streaming/STAN durable-stream server, a separate implementation from JetStream.

**Status:** Archived and deprecated. Its repository states that critical/security support ended in **June 2023** and directs users to JetStream. It is retained only for comparative implementation study.

- **C1:** Cluster recovery must reconcile Raft snapshots with separately stored message history, including retained-message expiry and channel incarnations. The clustering code serializes snapshot/application interactions and checks channel identifiers so old state is not applied to a recreated channel.
- **C3:** Batched publish application, message-store flushes, and pooled NATS transport connections reveal how consensus integration creates extra copying, persistence, and contention costs. The implementation makes those costs and coordination boundaries concrete.

**Entry point:** [Clustering implementation](https://raw.githubusercontent.com/nats-io/nats-streaming-server/main/server/clustering.go). This is actual implementation source, independent of the repository README, and is useful for comparison with JetStream's per-stream and per-consumer groups.

## Search coverage and limitations

Discovery used more than six distinct live-web search angles, followed by repository and documentation/source inspection. Representative query formulations included:

1. Distributed replicated event-streaming platforms and Kafka alternatives using Raft.
2. Distributed commit logs and lesser-known systems such as Liftbridge, Gazette, and Waltz.
3. Rust and Haskell streaming platforms, including Fluvio, Iggy, and HStream.
4. Erlang replicated streams and the RabbitMQ/Osiris implementation boundary.
5. Separate replicated-log storage: BookKeeper, LogDevice, and Pravega.
6. Kafka-compatible object-storage architectures and AutoMQ/S3Stream.
7. Replicated streaming tables and event databases, leading to Fluss and KurrentDB.
8. Additional Go, Java, Rust, and C++ durable-log/broker searches for smaller projects, followed by targeted searches for replication protocols, recovery code, and release history.

Later broad queries increasingly repeated these families or surfaced prototypes, wrappers, and systems whose inspected descriptions did not sufficiently establish replicated payload storage. The selection spans Java/Scala, Go, Rust, C++, Erlang, Haskell, and C#; quorum/ISR brokers, Raft and VSR groups, ledger ensembles, flexible replica placement, and storage-backed designs are all represented.

Each retained canonical GitHub page was opened, and at least one additional primary architecture, implementation, protocol, or evolution source was read. A differently hosted copy of the same root README was not counted as independent evidence. Canonical-owner changes were resolved for Fluvio and LogDevice. No moved-away repository is presented as an independently maintained project; DistributedLog is explicitly folded into BookKeeper. Apache repository hosting is not treated as a separate implementation from its upstream project.

Important exclusions and boundaries:

- **NSQ:** Its [official design](https://nsq.io/overview/design.html) describes independent `nsqd` instances and suggests producer-fed redundant pairs as an application topology. That is materially different from a platform-managed replicated event log, so it was excluded from this category.
- **Processors and consensus libraries:** Flink-style computation engines, generic Raft libraries, connectors, and client-only repositories do not qualify solely because they interact with replicated streams.
- **Related layers:** BookKeeper and Osiris are included because their reusable log machinery is itself substantial; they are not claimed to be full broker substitutes. HStream is evaluated for its own platform integration, not as a second independent invention of LogDevice's storage protocol. AutoMQ's distinct storage engine justifies including a Kafka-derived implementation.
- **Maintenance and release boundaries:** LogDevice and STAN are explicitly historical; Waltz's current maintenance was not established. Iggy's prerelease status, Fluvio's community transition, historical Pravega documentation, and development-version Pulsar/Fluss pages are flagged. An unarchived repository or recent update alone was not taken as proof of sustained maintenance.
- **Evidence limits:** The criteria are reasoned assessments grounded in the cited primary material. Documentation claims and test descriptions were not independently validated by running clusters, benchmarks, or failure tests. Shared storage only supplies the redundancy its configured backend actually guarantees. Links to moving branches and unversioned documentation can change after the research date.

No repository stars, unsupported benchmark numbers, or creation dates were used as quality evidence.
