# Append-only event stores

Research date: **2026-10-09**.

This report selects 20 GitHub repositories whose central purpose, or a substantial identifiable subsystem, is storing and replaying appended events. It covers dedicated databases, relational implementations, embedded libraries, cloud-blob storage, and replicated event logs. “Append-only” describes the event-writing model: it does not imply that administrators cannot delete data, that retention is unlimited, or that every physical storage page is immutable. Framework repositories qualify here because they contain event-store implementations, not merely clients for another product. The final subgroup explicitly distinguishes durable log engines from aggregate-oriented event stores.

This is a code-reading selection guide, not a production certification or a claim that every component is exemplary. Criteria are judgments grounded in the linked implementation and documentation. Performance mechanisms are discussed without treating project benchmarks as independently reproduced results.

## Criteria legend

- **C1 — Correctness:** substantial invariants, concurrency control, ordering, adversarial-input handling, or recovery and failure semantics.
- **C2 — Reusable abstractions:** meaningful storage, stream, transaction, serialization, or subscription abstractions usable across applications.
- **C3 — Performance and architecture:** concrete responses to latency, throughput, contention, memory, or storage constraints within an understandable design.
- **C4 — Sustained evolution:** evidence spanning years together with compatibility work, testing, migrations, or other complexity management. Repository age and recent pushes alone do not establish this criterion.

## Dedicated event databases

### 1. [kurrent-io/KurrentDB](https://github.com/kurrent-io/KurrentDB)

**Language / role:** C#; dedicated event database, formerly EventStoreDB. The repository documents the rename; the former and current names count as one project.

Study the boundary between event-stream semantics, durable replication, and the index that makes a shared transaction log usable as many logical streams.

- **C1:** Expected stream revisions detect conflicting appends. Cluster documentation specifies that the leader acknowledges after local persistence, majority replication, and local indexing; this makes acknowledgment and read visibility concrete rather than treating replication as a checkbox. See the [append API](https://docs.kurrent.io/clients/node/v1.1/appending-events) and [cluster design and configuration](https://github.com/kurrent-io/KurrentDB/blob/master/docs/server/configuration/cluster.md).
- **C3:** The [default-index design](https://github.com/kurrent-io/KurrentDB/blob/master/docs/server/features/indexes/default.md) explains stream-hash/event-number lookups, in-memory tables, persisted tables, Bloom filters, merge levels, checksums, and checkpoints. It is a useful entry point for understanding indexing costs and recovery together.
- **C4:** The [2020–2024 changelog](https://github.com/kurrent-io/KurrentDB/blob/master/CHANGELOG.md) records protocol deprecations, runtime migration, chunk-read fixes, and compatibility-sensitive changes. It explicitly directs newer release history elsewhere; it is not evidence that development stopped in 2024.

**Reading entry points:** the default-index document and cluster document above.

### 2. [sierra-db/sierradb](https://github.com/sierra-db/sierradb)

**Language / role:** Rust; dedicated distributed event store with a Redis-compatible protocol and an embeddable core.

The interesting separation is between writing an event locally, obtaining replica confirmations, and exposing a contiguous confirmed prefix to readers. Storage is divided into buckets, partitions, and segment files; ordering is local to the relevant partition rather than a universal total order.

- **C1:** The [watermark design](https://github.com/sierra-db/sierradb/blob/main/docs/Watermarks.md) describes independently confirmed events and a watermark that cannot advance across confirmation gaps. The [confirmation implementation](https://github.com/sierra-db/sierradb/blob/main/crates/sierradb-cluster/src/write/confirm.rs) validates transaction membership, event identities, and partition sequences before updating confirmation state.
- **C2:** The repository exposes both a network service and a Rust database interface, with event transactions, stream versions, historical scans, and subscriptions sharing the underlying storage model.
- **C3:** Partitioned sequential writes and local confirmation tracking address parallelism and the cost of distributed read quorums; these are identifiable mechanisms, not a verified throughput claim.

**Reading entry points:** the watermark document and confirmation implementation above. **Limitation:** the inspected confirmation-error branch leaves degraded-replica marking and recovery scheduling commented out. Some design documents retain the earlier “Eventus” name. Treat this as a developing design to examine critically, not proof that every recovery claim is implemented.

### 3. [umadb-io/umadb](https://github.com/umadb-io/umadb)

**Language / role:** Rust; specialist event database implementing dynamic consistency boundaries, with server and client components in one repository.

Study how a logical append-only event sequence can use a copy-on-write paged engine with reusable physical pages. Its consistency boundary is a query over relevant events and tags rather than necessarily one aggregate stream.

- **C1:** The [architecture document](https://umadb.io/architecture.html) describes conditional appends, snapshot transaction sequence numbers, two header pages, data synchronization before publishing a new header, and page reclamation constrained by active readers. It also explicitly states that writers serialize through one writer path; “non-blocking” should not be read as unrestricted parallel writing.
- **C3:** Separate B+ trees index events, tags, and free pages. Popular tags acquire their own subtrees, large event payloads use overflow pages, and batching amortizes writes. These mechanisms connect query behavior and storage efficiency.
- **C2:** The [core subsystem](https://github.com/umadb-io/umadb/tree/main/umadb-core) implements the event-store traits used by the higher-level server, keeping database mechanics distinct from gRPC transport.

**Reading entry points:** the architecture document and `umadb-core` above. No C4 claim is made for this comparatively recent implementation.

## Relational event-store implementations

### 4. [commanded/eventstore](https://github.com/commanded/eventstore)

**Language / role:** Elixir and SQL; PostgreSQL event store, independently usable alongside the Commanded ecosystem.

This is a compact study of how BEAM supervision interacts with database-owned coordination. The [architecture guide](https://github.com/commanded/eventstore/blob/master/guides/Architecture.md) distinguishes pooled queries, a notification connection, and a separate advisory-lock connection.

- **C1:** Subscription exclusivity depends on connection-scoped PostgreSQL locks. The guide explains why connection failure must terminate and restart monitored processes so locks can be reacquired. The [appender](https://github.com/commanded/eventstore/blob/master/lib/event_store/storage/appender.ex) separately maps duplicate-event, duplicate-stream, and wrong-version failures.
- **C2:** Named streams, linked events, all-stream reads, serialization, snapshots, and persistent subscriptions form a reusable storage service rather than an application-specific aggregate repository.
- **C3:** The appender splits large requests into bounded SQL batches within the transaction to respect PostgreSQL parameter limits. This is an explicit example of preserving transaction semantics while changing the physical write shape.

**Reading entry points:** the architecture guide and appender above. The [changelog](https://github.com/commanded/eventstore/blob/master/CHANGELOG.md) also records subscription catch-up fixes, gap handling, and runtime/test-matrix changes.

### 5. [message-db/message-db](https://github.com/message-db/message-db)

**Language / role:** PostgreSQL SQL/PLpgSQL, with shell and Ruby packaging; a language-neutral message and event store.

Most of the useful abstraction lives in database functions. This makes it a particularly direct comparison with libraries that implement stream semantics in application code.

- **C1:** [`write-message.sql`](https://github.com/message-db/message-db/blob/master/database/functions/write-message.sql) acquires a stream lock, reads the current version, rejects an incorrect expected version, and inserts the next position. The order of these operations is the important invariant.
- **C2:** Streams, categories, metadata, and consumer groups are exposed through SQL functions callable from different languages. [`get-category-messages.sql`](https://github.com/message-db/message-db/blob/master/database/functions/get-category-messages.sql) implements ordered category reads, validates consumer-group arguments, and partitions consumption using a hash of the stream's cardinal identity.
- **C3:** Bounded reads and database-side consumer partitioning avoid requiring every consumer to load and filter the entire event history.

**Reading entry points:** the write and category-read functions above. **Maintenance observation:** the [repository API](https://api.github.com/repos/message-db/message-db) reported an unarchived repository and a latest push in April 2024; this report does not infer current support from the README.

### 6. [JasperFx/marten](https://github.com/JasperFx/marten)

**Language / role:** C# and PostgreSQL; the event-store subsystem of a document-database/event-store monorepo.

Study the interaction between event appends, document sessions, and inline projections. The relevant subsystem is Marten's event storage and projection machinery, not every document-database feature.

- **C1:** The [append guide](https://github.com/JasperFx/marten/blob/master/docs/events/appending.md) distinguishes optimistic checks, exclusive stream locks, new-stream collisions, and tenant-partition behavior. It warns that some version-based append APIs have mode-specific restrictions, making API compatibility part of the concurrency story.
- **C2:** Event streams, typed events, metadata, projection documents, and transactional sessions support multiple application styles. The [storage-schema guide](https://github.com/JasperFx/marten/blob/master/docs/events/storage.md) shows how stream-local versions differ from the global event sequence.
- **C3:** Rich and Quick append modes trade early availability of sequence/version metadata for reduced work during appends. The consequences for inline projections and pre-commit listeners are documented explicitly; the optimization changes what information is available at each stage.

**Reading entry points:** the append guide and storage-schema guide above. Default-branch documentation describes evolving versions; check the release used before copying an API example.

### 7. [SQLStreamStore/SQLStreamStore](https://github.com/SQLStreamStore/SQLStreamStore)

**Language / role:** C# and SQL; relational stream-store library. **Archived and explicitly no longer actively maintained.**

This remains a substantial historical reference for specifying one stream API across SQL engines, particularly the interactions among expected versions, retries, and message identities.

- **C1:** The PostgreSQL [`AppendToStream.sql`](https://github.com/SQLStreamStore/SQLStreamStore/blob/master/src/SqlStreamStore.Postgres/PgSqlScripts/AppendToStream.sql) distinguishes Any, Empty, NoStream, and explicit-version cases, and invokes idempotency checks when inserts conflict. Treating all duplicate inserts as successful would not preserve these semantics.
- **C2:** SQL Server, PostgreSQL, and MySQL implementations share the stream-store contract; the in-memory implementation supports behavioral testing. This is reusable persistence infrastructure rather than a domain framework.
- **C1, testing evidence:** The [append acceptance tests](https://github.com/SQLStreamStore/SQLStreamStore/blob/master/tests/SqlStreamStore.AcceptanceTests/AcceptanceTests.AppendStream.cs) distinguish identical retries, additional or differing messages, incorrect versions, and empty-stream behavior. They make the intended contract easier to assess across backends.

**Reading entry points:** the PostgreSQL append function and shared acceptance tests above. Retention/deletion support means append-only event writing is not a promise of permanent retention.

### 8. [prooph/pdo-event-store](https://github.com/prooph/pdo-event-store)

**Language / role:** PHP and SQL; concrete PDO persistence for Prooph Event Store across PostgreSQL, MySQL, and MariaDB.

The useful comparison is among persistence strategies: table layout and aggregate semantics are explicit objects, separate from the store API. This report counts the concrete implementation repository, not a second entry for its interface package.

- **C1:** The [PostgreSQL aggregate-stream strategy](https://github.com/prooph/pdo-event-store/blob/master/src/PersistenceStrategy/PostgresAggregateStreamStrategy.php) requires aggregate-version metadata and creates uniqueness constraints for event IDs and aggregate versions. The [PostgreSQL store](https://github.com/prooph/pdo-event-store/blob/master/src/PostgresEventStore.php) translates constraint failures into concurrency errors and implements transaction rollback on exceptions.
- **C2:** Persistence strategies, metadata matchers, stream iterators, transaction control, and projection support let applications reuse the store while choosing different SQL layouts and access patterns.
- **C3:** `appendTo()` prepares a multi-row insert from the strategy's columns and encoded data, making batching and schema strategy visible in the implementation rather than hiding them behind a generic ORM call.

**Reading entry points:** the aggregate-stream strategy and PostgreSQL store above. Database-specific requirements and migration advice appear in the repository README; they should not be assumed identical across backends.

### 9. [zilverline/sequent](https://github.com/zilverline/sequent)

**Language / role:** Ruby and PLpgSQL; event-store subsystem within a CQRS/event-sourcing framework.

Study the split between the Ruby orchestration layer and PostgreSQL procedures, including command provenance, event ordering, aggregate uniqueness, snapshots, and replay.

- **C1:** The inspected [`store_events` procedure](https://github.com/zilverline/sequent/blob/master/db/migrate/sequent/store_events_v05.sql) orders aggregate processing, locks aggregate rows, checks the starting sequence number, and rejects sequence gaps before insertion. Its comments explain why uniqueness constraints alone do not catch every incorrect concurrent sequence.
- **C2:** The [Ruby event store](https://github.com/zilverline/sequent/blob/master/lib/sequent/core/event_store.rb) connects storage, event publication, snapshot-aware loading, and replay behind a reusable framework boundary.
- **C3:** Cursor-based replay processes batches instead of materializing the complete history. The same code makes replay progress reporting and configurable batch size explicit.

**Reading entry points:** `store_events_v05.sql` and `event_store.rb` above. The [changelog](https://github.com/zilverline/sequent/blob/master/CHANGELOG.md) documents versioned snapshots and projector activation for rolling upgrades. Older conceptual documentation describes earlier table layouts, so the current procedures are the stronger source for storage details.

## Reusable libraries with substantive event-store subsystems

### 10. [NEventStore/NEventStore](https://github.com/NEventStore/NEventStore)

**Language / role:** C#; persistence-independent event-stream and commit library, with core storage contracts and acceptance infrastructure.

Study the distinction between an event's stream revision, a commit sequence, and a commit identifier. Storage adapters are separate projects; the retained repository provides substantial semantics above that boundary.

- **C1:** [`OptimisticEventStream`](https://github.com/NEventStore/NEventStore/blob/develop/src/NEventStore/OptimisticEventStream.cs) prevents committing through a partially loaded stream, refreshes after concurrency errors, and explains why duplicate commit IDs must be enforced at the persistence boundary rather than against the currently loaded slice.
- **C2:** Stream, commit, snapshot, serializer, and polling interfaces separate domain-event handling from persistence engines. Snapshot loading and bounded stream reads reuse the same commit model.
- **C3:** The source explains its allocation-conscious event collections, while the [changelog](https://github.com/NEventStore/NEventStore/blob/develop/Changelog.md) records indexed in-memory reads, stream-write benchmarks, and serializer compatibility checks accompanying optimization work.

**Reading entry points:** `OptimisticEventStream.cs` and the changelog above. The inspected default branch is `develop`; its changes should not be assumed released merely because they are documented there.

### 11. [RailsEventStore/rails_event_store](https://github.com/RailsEventStore/rails_event_store)

**Language / role:** Ruby; a monorepo containing Ruby Event Store, Active Record persistence, Rails integration, and related gems. Counted once.

This is an unusually useful source for studying a precise concurrency contract at the application API boundary, together with independently reusable publishing and persistence components.

- **C1:** The [expected-version guide](https://github.com/RailsEventStore/rails_event_store/blob/master/railseventstore.org/docs/core-concepts/expected-version.md) differentiates `:any`, explicit versions, and `:auto`. It explains the read/write race in `:auto` and warns against mixing concurrency modes within a stream.
- **C2:** Event records and stream membership are separate concepts. The [Active Record repository](https://github.com/RailsEventStore/rails_event_store/blob/master/ruby_event_store-active_record/lib/ruby_event_store/active_record/event_repository.rb) supports appending records and linking existing events to streams, with serialized event insertion and stream entries enclosed in a transaction.
- **C3:** Batched record insertion uses `insert_all!`, while stream-position resolution remains a separate step whose concurrency semantics must be understood.

**Reading entry points:** the expected-version guide and Active Record repository above. The repository also has event-update operations, so its event-sourcing append path should not be mistaken for an enforced write-once security boundary.

### 12. [pyeventsourcing/eventsourcing](https://github.com/pyeventsourcing/eventsourcing)

**Language / role:** Python; event-sourcing library with concrete SQLite, PostgreSQL, and in-memory persistence modules.

The persistence layer is worth studying independently of the higher-level aggregate API. It defines storage requirements first, then separates mapping, serialization, database recording, and notification tracking.

- **C1:** The [persistence design](https://github.com/pyeventsourcing/eventsourcing/blob/9.5/docs/topics/persistence.rst) requires unique aggregate positions, atomic recording into aggregate and application sequences, consistent insertion/commit ordering, and atomic tracking of consumed notifications with resulting state changes. These requirements directly address dual-write and skipped-event failure modes.
- **C2:** `Mapper`, `Recorder`, `EventStore`, and infrastructure factories make serialization/compression/encryption and database selection independent concerns rather than one inheritance-heavy storage implementation.
- **C1, testing evidence:** The [noninterleaving notification tests](https://github.com/pyeventsourcing/eventsourcing/blob/9.5/tests/persistence_tests/test_noninterleaving_notification_ids.py) apply shared ordering tests to in-memory, SQLite, and PostgreSQL recorders.

**Reading entry points:** the persistence design and notification-order tests above. The atomic-processing guarantee concerns recorded state changes; it does not make unrelated external effects exactly-once.

### 13. [disintegrate-es/disintegrate](https://github.com/disintegrate-es/disintegrate)

**Language / role:** Rust; event-sourcing library with a PostgreSQL event store and query-defined consistency boundaries.

Study a design where the events needed to make a decision need not be the same set used to invalidate that decision. This is materially different from always locking or version-checking one predefined aggregate.

- **C1:** The [PostgreSQL store](https://github.com/disintegrate-es/disintegrate/blob/main/disintegrate-postgres/src/event_store.rs) uses serializable transactions for validated appends and an epoch mechanism to prevent readers skipping events when concurrent writers commit out of sequence order.
- **C2:** Typed state queries, validation queries, serialization, event-store traits, and PostgreSQL persistence support composition of state across domain identifiers. The [concurrency guide](https://github.com/disintegrate-es/disintegrate/blob/main/docs/docs/developer_journey/handle_concurrency_conflicts.md) demonstrates selectively excluding event types from validation and explains the resulting business tradeoff, such as permitting overbooking.
- **C3:** The implementation streams filtered results rather than requiring a complete aggregate history in memory; the SQL builder performs batched inserts and returns assigned event IDs.

**Reading entry points:** the PostgreSQL store and concurrency guide above. Relaxing a validation query deliberately relaxes the corresponding business invariant.

### 14. [hallgren/eventsourcing](https://github.com/hallgren/eventsourcing)

**Language / role:** Go; small event-sourcing toolkit with substantive bbolt and SQL stores.

**Provenance:** GitHub marks this as a fork of `jen20/go-event-sourcing-sample`, and its README acknowledges that origin. It is retained for its separately developed reusable modules, concrete persistence engines, iterators, projections, and common store test suite—not as another copy of the original sample. The parent is not separately listed.

- **C1:** The [bbolt store](https://github.com/hallgren/eventsourcing/blob/master/eventstore/bbolt/bbolt.go) checks the next aggregate version within a write transaction, assigns per-aggregate and global sequences, and commits the corresponding records together.
- **C2:** A small `EventStore`/iterator contract supports memory, SQL, bbolt, and external-store integrations. The [shared test suite](https://github.com/hallgren/eventsourcing/blob/master/core/testsuite/eventstoresuite.go) exercises storage-order and concurrency expectations across implementations.
- **C3:** The bbolt implementation uses ordered binary keys and cursor-based reads, making seek behavior and transaction lifetime visible without a large server architecture.

**Reading entry points:** the bbolt implementation and shared store tests above. The global-order bucket currently stores event values; do not infer that it contains only pointers from the older source comment.

### 15. [looplab/eventhorizon](https://github.com/looplab/eventhorizon)

**Language / role:** Go; CQRS toolkit, specifically its `eventstore/mongodb_v2` subsystem.

This offers a concrete study of a global event-position counter becoming a contention point even when writers touch different aggregates.

- **C1:** The [global-position strategy document](https://github.com/looplab/eventhorizon/blob/main/eventstore/mongodb_v2/STRATEGY.md) distinguishes an in-transaction counter, with strict commit ordering, from an outside-transaction counter that can leave gaps and reorder commits across aggregates. It explains which scanning consumers depend on the stronger mode.
- **C3:** Moving position reservation outside the save transaction removes the shared counter lock from the transaction's full duration. The same document describes a concurrency/pool-size benchmark matrix and the corresponding correctness test, connecting optimization with an explicit semantic cost.
- **C2:** The [MongoDB v2 store](https://github.com/looplab/eventhorizon/blob/main/eventstore/mongodb_v2/eventstore.go) implements the common store contract with codecs, transaction handlers, and aggregate-version control. It uses event documents separately from stream state, avoiding the first MongoDB adapter's ever-growing event array.

**Reading entry points:** `STRATEGY.md` and the MongoDB v2 store above. This entry concerns event persistence, not the toolkit's broker adapters.

### 16. [thenativeweb/node-eventstore](https://github.com/thenativeweb/node-eventstore)

**Language / role:** JavaScript; callback-based event-store library with several concrete database adapters. This is the canonical home of the former `adrai/node-eventstore`; the README explains the maintainer handover.

Study the older commit-batch model: events carry a commit ID, position within a commit, stream revision, and dispatch state. Its value is understanding the boundary among persistence, retry bookkeeping, snapshots, and publication.

- **C1:** The [core commit implementation](https://github.com/thenativeweb/node-eventstore/blob/master/lib/eventstore.js) preserves failed batches as uncommitted events and only queues dispatch after storage succeeds. Snapshot loading resumes from the following revision. These are important failure-sensitive transitions, not proof of cross-backend atomicity.
- **C2:** Stream and snapshot objects sit over interchangeable concrete adapters. The [MongoDB adapter](https://github.com/thenativeweb/node-eventstore/blob/master/lib/databases/mongodb.js) records multi-event transaction documents before inserting event documents, exposing adapter-specific recovery bookkeeping for inspection.

**Reading entry points:** the core store and MongoDB adapter above. **Limitation:** the inspected adapter does not establish the same expected-version or modern database-transaction guarantees as the dedicated stores above. Its transaction documents are application bookkeeping, not evidence of a MongoDB multi-document transaction. No active-maintenance claim is made from its historical README.

## Event streams over cloud object storage

### 17. [Lokad/AzureEventStore](https://github.com/Lokad/AzureEventStore)

**Language / role:** C#; event streams over Azure Append Blobs, with projections, snapshots, and local storage/cache abstractions.

This is a useful smaller-scale counterpoint to operating a database cluster. Study the mechanics of implementing a stream across multiple remote append-only objects while preserving conditional-write behavior.

- **C1:** The [storage design](https://github.com/Lokad/AzureEventStore/blob/master/Lokad.AzureEventStore/Drivers/AzureAppendBlob.md) explains rejecting writes based on a stale position, handling concurrent blob creation, and preserving that property across blob rollover. It also specifies an event format with size fields and checksums.
- **C2:** Storage drivers, event serializers, projection state, and projection snapshots are separated, so the application can retain event contracts and projections while changing persistence details.
- **C3:** Global offsets are translated into individual blobs using stored starting positions and binary search. Snapshots bound the amount of event replay required to rebuild projections.

**Reading entry points:** the storage design and [transaction tests](https://github.com/Lokad/AzureEventStore/blob/master/Lokad.AzureEventStore.Test/wrapper/transaction.cs). The README positions this for relatively modest write rates and in-memory materialized views; it is not presented as a substitute for every distributed event database.

## Replicated and embedded durable event logs

### 18. [pravega/pravega](https://github.com/pravega/pravega)

**Language / role:** Java; distributed stream storage. The relevant subsystem is the Segment Store and event/transaction APIs, rather than aggregate expected-version semantics.

Study how durable acknowledgment can be separated from migration into longer-term storage without making the cache authoritative.

- **C1:** The [Segment Store design](https://github.com/pravega/pravega/blob/master/documentation/src/docs/segment-store-service.md) defines length/truncation invariants, durable-log acknowledgment, recovery epochs, checkpoints, and the relationship between durable and long-term storage. Concurrent appends do not interleave their contents.
- **C3:** A fast durable log accepts small appends; background writers coalesce them for long-term storage. A read index resolves data from the cache and storage tiers. The architecture explains why the layers exist and when log truncation becomes safe.
- **C2:** The [transaction guide](https://github.com/pravega/pravega/blob/master/documentation/src/docs/transactions.md) exposes batches of events that remain invisible until committed, with transaction leases to handle failed clients.

**Reading entry points:** the Segment Store design and transaction guide above. **Maintenance observation:** the [repository API](https://api.github.com/repos/pravega/pravega) reported an unarchived repository with its latest push in March 2025. The reviewed design material uses Tier 1/Tier 2 terminology; this is not a claim of current operational support.

### 19. [RBMHTechnology/eventuate](https://github.com/RBMHTechnology/eventuate)

**Language / role:** Scala; replicated event logs and event-sourced components with Cassandra and LevelDB backends. **Archived on 2021-06-01**, despite the older description saying “maintenance mode.” This is the Red Bull Media House project, not the unrelated Eventuate-branded Java ecosystem.

Study the deliberate distinction between a total order within one local log and causal ordering across independently writable locations.

- **C1:** The [architecture](https://rbmhtechnology.github.io/eventuate/architecture.html) explains vector timestamps, asynchronous replication, deterministic local replay, and continued local writes during partitions. Concurrent events may have different orders at different locations. It also documents a limitation involving filtered replication cycles.
- **C2:** Local log providers, replication endpoints, event-sourced actors, views, writers, and processors compose into reusable event-driven systems. The [overview](https://rbmhtechnology.github.io/eventuate/overview.html) identifies the concrete backend plugins and distinguishes within-location durability from cross-location replication.
- **C3:** The architecture connects replication-network density to read load and bandwidth, making topology a tangible performance and availability tradeoff.

**Reading entry points:** the architecture's event-log section and the overview's storage/consistency sections above. The historical status matters when evaluating dependencies or considering adoption.

### 20. [OpenHFT/Chronicle-Queue](https://github.com/OpenHFT/Chronicle-Queue)

**Language / role:** Java; embedded persistent append/tail log used for replayable messaging and event processing. This is a storage primitive, not an aggregate-oriented event-sourcing database.

Study memory-mapped storage, document publication, writer coordination, rolling files, and independent readers. Its inclusion is specifically for its normal append-and-replay path.

- **C1:** [`StoreAppender`](https://github.com/OpenHFT/Chronicle-Queue/blob/ea/src/main/java/net/openhft/chronicle/queue/impl/single/StoreAppender.java) coordinates write locks, incomplete document headers, rollback-on-close, cycle transitions, and end-of-file markers. These are concrete concurrency and interrupted-write concerns.
- **C3:** The [low-level design](https://chronicle.software/tech-hub/technical-information/chronicle-queue/advanced) connects sequential access and memory mapping to reduced object allocation, operating-system paging, and off-heap atomic metadata operations. No numerical latency claim is adopted here.
- **C2:** Appenders, tailers, indexed seeks, and rolling policies make the log reusable for IPC, audit/replay, and event pipelines.

**Reading entry points:** `StoreAppender.java` and the low-level design above. **Scope limitation:** the design documentation also describes fixed-size in-place updates; Chronicle is therefore an append-oriented event-log engine, not an enforcement mechanism for immutable records. Replication and encryption discussed in the [user guide](https://github.com/OpenHFT/Chronicle-Queue/blob/ea/docs/antora/modules/introduction/pages/introduction.adoc) include enterprise features and should not be attributed wholesale to this public implementation.

## Search coverage and limitations

Discovery used live web searches and then primary-source reading. Search formulations covered: general append-only event databases; PostgreSQL stores and optimistic concurrency; .NET stream stores; Ruby and PHP persistence; Go and Node.js adapters; Rust embedded/distributed stores; dynamic consistency boundaries; Java persistent logs; Scala replicated journals; cloud append blobs; and expected-version/idempotency/snapshot behavior. Later searches increasingly returned already-seen projects, integration packages, tutorials, or adjacent temporal databases. They also exposed UmaDB and Eventuate, which were inspected and retained because they added distinct storage and consistency designs.

Canonical GitHub identities were checked through repository pages or the public GitHub API. Every selected repository has additional opened documentation or source beyond its root README; implementation details were read directly from verified source paths where useful. Default-branch links are a research-date view and can evolve. API requests eventually encountered an unauthenticated rate limit; browser and raw-file reads supplied the remaining evidence. No candidate code was run, no dependencies were installed, and no performance or fault-tolerance result was independently reproduced.

The list intentionally excludes small JSON-line demonstrations, tutorial application templates, awesome lists, generated wrappers, and SDK-only repositories. The PHP DCB interface and language bindings were not counted separately from storage implementations. Thalo's repository explicitly describes it as unmaintained; the retained Rust projects provide more distinct current implementation material for this selection. General-purpose brokers, databases whose append-only file is only an internal write-ahead log, and primarily temporal-document databases were not expanded into a second survey. Pravega and Chronicle are explicitly marked boundary cases because their reusable event-log storage is the material being studied.

Repository status is not inferred from stars. SQLStreamStore and Eventuate are clearly marked archived; Message DB and Pravega have dated activity observations rather than maintenance promises. The evolved Hallgren fork is identified as such, and no parent/fork pair or renamed repository is counted twice. The main limitation is selection, not a shortage of candidates: the ecosystem contains many more adapters, and this report prioritizes distinctive inspectable implementations over exhaustiveness.
