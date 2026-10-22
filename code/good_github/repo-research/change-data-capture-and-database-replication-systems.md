# Change data capture and database replication systems

Research date: **2026-10-09**.

This report selects **24 GitHub repositories** for studying how database changes are captured, ordered, transported, replayed, and recovered. It covers log readers, database-to-database replication, trigger-based synchronization, selective client replication, and SQLite page replication. Libraries are included when they implement substantial replication machinery. Larger monorepos are counted once and their relevant subsystems are identified. This is an engineering study guide, not a deployment recommendation or a claim that every component is exemplary.

Criteria used throughout:

- **C1 — Difficult correctness:** invariants, concurrency, data semantics, malformed inputs, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces or components supporting multiple applications, databases, or replication workflows.
- **C3 — Performance with structure:** explicit treatment of throughput, latency, memory, I/O, or source-database load within an understandable architecture.
- **C4 — Sustained evolution:** multiyear evidence of compatibility work, regression testing, or complexity management. Repository age and stars alone do not qualify.

The criteria assignments and suggested study topics are grounded engineering judgments. Statements about algorithms and behavior come from the linked primary material. Default-branch sources can describe development work; design proposals are identified as such rather than treated as released guarantees.

## CDC platforms and distributed replication workflows

### 1. [debezium/debezium](https://github.com/debezium/debezium)

**Language / role:** Java; database-specific CDC connectors and a shared capture framework.

Study the boundary between a common change-event model and the database-specific machinery needed to produce it. Debezium is especially useful for understanding why a connector needs historical schema information, durable source positions, and a careful transition between snapshots and live changes.

- **C1:** The MySQL connector reconstructs the schema applicable at a historical binlog position from its schema-history stream. Its initial snapshot records a consistent source position before subsequent streaming; using the current schema for old events would be incorrect. [MySQL connector internals](https://debezium.io/documentation/reference/stable/connectors/mysql.html).
- **C2:** Connectors can run through Kafka Connect, Debezium Server, or an embedded engine, separating database capture from deployment and delivery choices. [Architecture](https://github.com/debezium/debezium/blob/main/documentation/modules/ROOT/pages/architecture.adoc).
- **C3:** Incremental snapshots bound work into chunks and resolve collisions between snapshot rows and concurrent log events using a snapshot window and primary-key matching. This is a concrete memory/concurrency tradeoff, not simply a bulk export. [Incremental snapshot algorithm](https://github.com/debezium/debezium/blob/main/documentation/modules/ROOT/partials/modules/all-connectors/con-connector-incremental-snapshot.adoc).

### 2. [apache/flink-cdc](https://github.com/apache/flink-cdc)

**Language / role:** Java; distributed CDC sources and declarative replication pipelines on Flink.

Study the source enumerator/reader boundary and the interaction between parallel snapshot work and checkpoint recovery. The repository exposes YAML pipelines, SQL sources, and a DataStream API, while retaining database-specific implementations beneath them.

- **C1:** `MySqlHybridSplitAssigner` waits for snapshot assignment to finish before assigning the binlog split to avoid conflicting row order. Its metadata-release logic waits for checkpoint completion and uses assignment generations to reject stale reader events. [Hybrid split assigner](https://github.com/apache/flink-cdc/blob/master/flink-cdc-connect/flink-cdc-source-connectors/flink-connector-mysql-cdc/src/main/java/org/apache/flink/cdc/connectors/mysql/source/assigners/MySqlHybridSplitAssigner.java).
- **C2:** The three public API layers share a connector ecosystem while supporting different integration styles; pipeline routing, transformation, and schema evolution are first-class concerns. [API layers and compatibility matrix](https://github.com/apache/flink-cdc#api-layers).
- **C3:** Snapshot splits permit parallel initial loading, while the assigner explicitly manages the memory cost and recovery lifetime of completed-split metadata. The source above provides a focused entry point into that coordination.

### 3. [pingcap/ticdc](https://github.com/pingcap/ticdc)

**Language / role:** Go; distributed capture of TiDB changes into databases, messaging systems, and object storage.

This is the redesigned TiCDC repository, used beginning with v8.5.4 according to its README. Older TiCDC code remains in TiFlow; it is not counted as a second implementation here. Study the separation between upstream log acquisition and downstream dispatch, plus the safety boundaries around distributed writers.

- **C1:** The capture write-lease design addresses a partitioned old capture that can still reach a sink. It combines etcd identity evidence with coordinator leases and checks admission at actual sink mutation boundaries, including already queued asynchronous work. It also describes mixed-version rollout behavior. [Write-lease design overview](https://github.com/pingcap/ticdc/blob/master/docs/design/capture-write-lease-overview.md).
- **C3:** The flow-control design divides acquisition into LogPuller/EventStore/EventService and delivery into EventCollector/Dispatcher/Sink. It specifies per-dispatcher and per-changefeed memory controls, with stream reset after emergency queue discards. [Flow-control design](https://github.com/pingcap/ticdc/blob/master/docs/design/2024-12-20-ticdc-flow-control.md).

These documents are design evidence; individual mechanisms should be checked against the intended release before operational use.

### 4. [vitessio/vitess](https://github.com/vitessio/vitess)

**Language / role:** Go; the **VReplication and VStream subsystems** of the Vitess monorepo.

Study replication as a reusable engine for online database operations. VReplication supplies filtered streams between shards and underlies table migration, resharding, materialization, and online schema changes; VStream also exposes changes to external consumers.

- **C1:** Interrupted copying must resume consistently with the stream position. Cutovers journal source positions, and VDiff compares consistent source/target snapshots. The copy task implementation places row insertion, copy-state insertion, and commit into an explicit lifecycle. [VReplication overview](https://vitess.io/docs/25.0/reference/vreplication/vreplication/), [copy implementation](https://github.com/vitessio/vitess/blob/main/go/vt/vttablet/tabletmanager/vreplication/vcopier.go).
- **C2:** A stream combines table selection, filtering, and supported transformations, allowing the same machinery to serve several migration and materialization workflows.
- **C3:** The documented engine batches replay when the destination falls behind and throttles overloaded sources or targets. The implementation separates copy tasks, a bounded work queue, and workers.

The linked v25 documentation is marked development; the study target is the subsystem, not a promise about every released version.

### 5. [PeerDB-io/peerdb](https://github.com/PeerDB-io/peerdb)

**Language / role:** Go and Rust, with a TypeScript UI; CDC and initial-load orchestration for analytical destinations.

Study the division between durable workflow orchestration and database-specific data movement. The Go flow workers are the main replication entry point; the Rust Nexus service supplies a PostgreSQL-compatible control interface.

- **C1:** Temporal workflows coordinate setup, snapshot, CDC, normalization, retries, and flow-state changes. Catalog state records batch progress and schema mappings, making restart behavior a cross-component concern rather than a simple reconnect loop. [Architecture and CDC workflow](https://github.com/PeerDB-io/peerdb/blob/main/docs/peerdb-architecture.md).
- **C2:** Connector capabilities are separated into pull, sync, normalize, schema, and query-replication interfaces. This makes differences among source databases and destination write models explicit.
- **C3:** Initial snapshots use parallel partitions and dedicated snapshot workers, so long initial loads do not consume the same work queue as ongoing CDC. The design also exposes staging and destination-specific bulk ingestion. [Detailed design](https://github.com/PeerDB-io/peerdb/blob/main/docs/deep-dive-design-document.md).

## MySQL binlog systems and reusable readers

### 6. [alibaba/canal](https://github.com/alibaba/canal)

**Language / role:** Java; MySQL binlog subscription server, clients, and downstream adapters.

Canal impersonates a MySQL replication client, parses binlog bytes, and exposes changes through its own client/server protocol. Study the distinction between reading events, acknowledging consumption, and retaining enough state to replay a failed batch.

- **C1:** The streaming client API records a cursor mark for each fetch, requires acknowledgements in order, and resets outstanding marks on rollback to resume from the last acknowledged cursor. This is a concrete consumption invariant. [Client API and acknowledgement protocol](https://github.com/alibaba/canal/wiki/ClientAPI).
- **C2:** The protobuf-based boundary permits consumers in different languages; the server’s capture work is reusable across indexing, cache refresh, messaging, and database synchronization. [Replication architecture](https://github.com/alibaba/canal/wiki/Introduction).
- **C3:** Fetch and acknowledgement can proceed asynchronously, reducing round-trip overhead while permitting concurrent downstream work. Correct acknowledgement order is the cost of that throughput-oriented design.

Some wiki pages are older than current code; use them to understand the protocol, then inspect the version being studied.

### 7. [zendesk/maxwell](https://github.com/zendesk/maxwell)

**Language / role:** Java; a MySQL-binlog-to-JSON daemon for streaming destinations.

Study a comparatively focused CDC application with a substantial schema-history subsystem. Maxwell stores an initial schema plus changes associated with binlog positions, server IDs, and heartbeat information, rather than assuming that the current database schema describes every event.

- **C1:** Schema reconstruction follows the applicable delta chain. For primary failover, heartbeat events establish a correspondence between positions in two servers’ binlogs, allowing a schema-history merge point. [Schema storage and failover internals](https://github.com/zendesk/maxwell/blob/master/docs/docs/schemas.md).
- **C4:** The changelog documents multiyear parser and compatibility work: MySQL 8.4 support and test updates, MariaDB GTID fixes, a stale-schema selection fix involving binlog filename ordering, and compressed-binlog support. These are substantive examples of maintaining protocol correctness as upstream systems change. [Changelog](https://github.com/zendesk/maxwell/blob/master/CHANGELOG.md).

The study value lies in the interaction of schema history, source identity, and recovery, not in the small JSON envelope alone.

### 8. [go-mysql-org/go-mysql](https://github.com/go-mysql-org/go-mysql)

**Language / role:** Go; reusable MySQL/MariaDB protocol, binlog parsing, and replication components.

Focus on the `replication` package and its use by the higher-level canal package. This is a library for constructing replication systems, rather than a complete managed pipeline.

- **C1:** `BinlogSyncer` resets parser state on reconnect and distinguishes GTID-based restart from file/position restart. Its options also expose semantic choices for decimals, timestamps, checksums, and MySQL JSON representations—details that can change downstream values if handled casually. [Replication client implementation](https://github.com/go-mysql-org/go-mysql/blob/master/replication/binlogsyncer.go).
- **C2:** The same protocol foundation supports live event streaming, binlog-file parsing, incremental dumping, clients, and server-side protocol implementations.
- **C4:** The changelog spans 2020–2026 and includes compressed-transaction checkpoint fixes, protocol frame bounds, compatibility changes, and explicit breaking-change sections. [Changelog](https://github.com/go-mysql-org/go-mysql/blob/master/CHANGELOG.md).

Use the canonical organization above; historical `siddontang/go-mysql` references should not be counted separately.

### 9. [julien-duponchelle/python-mysql-replication](https://github.com/julien-duponchelle/python-mysql-replication)

**Language / role:** Python; MySQL/MariaDB replication-protocol reader built on PyMySQL.

Study the lower-level event-stream machinery behind Python CDC applications. The code makes replication positions, metadata lookup, event selection, and stream reconnection visible without the infrastructure of a distributed connector platform.

- **C1:** `BinLogStreamReader` retains format-description, table-map, and rotation events even when user filters exclude other events, because later decoding depends on them. It separates the streaming and metadata connections and handles both position and GTID configuration. [Stream reader](https://github.com/julien-duponchelle/python-mysql-replication/blob/main/pymysqlreplication/binlogstream.py).
- **C2:** Consumers receive typed events through a configurable iterator with table/schema/event filters, heartbeat support, and alternative connection wrappers, making the reader reusable across different destinations.
- **C3:** The implementation exposes schema freezing and column-name caching as explicit tradeoffs; these avoid work but carry compatibility or schema-change implications. [Documented limitations](https://github.com/julien-duponchelle/python-mysql-replication/blob/main/docs/limitations.rst) are useful alongside the implementation.

The canonical owner differs from older `noplay` links found in documentation and downstream projects.

### 10. [the4thdoctor/pg_chameleon](https://github.com/the4thdoctor/pg_chameleon)

**Language / role:** Python and PL/pgSQL; MySQL-to-PostgreSQL replication and migration.

This is a substantive consumer of the Python binlog library, with its own durable intermediate representation and replay machinery. Row images are stored as PostgreSQL JSONB; database-side logic transforms them into changes on the destination.

- **C1:** Initial loading captures source coordinates and establishes a high-water mark before declaring consistency. Incremental batches track source log positions and processed state; tables without suitable keys cannot participate in ongoing replication. [MySQL capture and initialization](https://github.com/the4thdoctor/pg_chameleon/blob/main/pg_chameleon/lib/mysql_lib.py).
- **C2:** Schema mappings, type overrides, refresh operations, and database-side replay support ongoing replicas, aggregation from multiple MySQL sources, and migration cutover. [Replication catalog and replay SQL](https://github.com/the4thdoctor/pg_chameleon/blob/main/pg_chameleon/sql/create_schema.sql).
- **C3:** Separate reader and replay processes decouple binlog intake from destination application, while initial copying uses bounded slices.

Its README explicitly limits DDL handling and describes conservative exclusion of failing tables; study those policies as part of the design, not as transparent cross-engine equivalence.

## PostgreSQL logical decoding, migration, and delivery engines

### 11. [2ndQuadrant/pglogical](https://github.com/2ndQuadrant/pglogical)

**Language / role:** C and SQL; a PostgreSQL logical replication extension with providers, subscribers, and replication sets.

Study the protocol and apply-side engineering behind selective replication and cross-version migration. The repository documents continued maintenance while directing new feature development toward the separate Postgres Distributed product; those products should not be conflated.

- **C1:** The design explains why source and destination column attribute numbers can differ even when visible schemas look identical. Relation metadata must therefore identify columns correctly. Protocol capabilities must also be negotiated before new message formats are enabled. [Design decisions](https://github.com/2ndQuadrant/pglogical/blob/REL2_x_STABLE/internals-doc/DESIGN.md).
- **C2:** Replication sets, row/column filtering, multiple origins, and pluggable output hooks support different topologies and consumers. [Extension guide](https://github.com/2ndQuadrant/pglogical/blob/REL2_x_STABLE/docs/README.md).
- **C3:** Its binary protocol avoids repeated JSON encoding/decoding and supports metadata reuse; the design explains the tradeoffs rather than presenting a throughput claim.

The internals document contains historical and planned elements. Its reasoning is valuable, but planned cache controls or transaction-streaming extensions should not be read as current feature guarantees.

### 12. [eulerto/wal2json](https://github.com/eulerto/wal2json)

**Language / role:** C; PostgreSQL logical-decoding output plugin.

Study how database-native values and transaction boundaries become an external CDC format. This is an output component rather than a complete replication service, and its consumer remains responsible for transport progress and destination behavior.

- **C1:** The implementation deals explicitly with PostgreSQL type output, TOAST values, replica identity, and JSON-incompatible numeric values. NaN and infinities have a defined null/string policy depending on configuration; blindly serializing database values would lose or misrepresent semantics. [Output implementation](https://github.com/eulerto/wal2json/blob/master/wal2json.c).
- **C2:** Transaction-oriented and tuple-oriented output formats, selectable metadata, and filtering let different consumers use the same decoding plugin through PostgreSQL’s streaming or SQL interfaces.
- **C1, additional testing evidence:** The TOAST regression scenario covers large compressed and uncompressed values, changes to other columns, deletion, and both output formats. [TOAST test](https://github.com/eulerto/wal2json/blob/master/sql/toast.sql).

This compact codebase is particularly useful for studying correctness at a serialization boundary.

### 13. [dimitri/pgcopydb](https://github.com/dimitri/pgcopydb)

**Language / role:** C; PostgreSQL base-copy and CDC tooling for online migration.

Study the mechanics of getting a bulk copy and ongoing logical changes to meet at a controlled cutover point. The current implementation supports `pgoutput`, `test_decoding`, and `wal2json`, with structured local SQLite storage for intermediate changes.

- **C1:** The logical-decoding internals distinguish received, transformed, and replayed progress; replication feedback must correspond to safe durable boundaries. Target-side restart uses PostgreSQL replication-origin progress, and an operator’s requested stopping position can fall inside a transaction. [Logical decoding and restart semantics](https://github.com/dimitri/pgcopydb/blob/main/docs/logical-decoding.rst).
- **C3:** Data copying uses multiple streaming processes, while index creation is scheduled separately and concurrently. This avoids requiring a complete directory-format dump before restore can begin. [Base copy and CDC architecture](https://github.com/dimitri/pgcopydb#base-copy-and-change-data-capture).

Its role is migration-oriented replication. The interesting architecture includes local spooling, progress accounting, and controlled completion, not just invoking `pg_dump`.

### 14. [supabase/etl](https://github.com/supabase/etl)

**Language / role:** Rust; embeddable PostgreSQL replication engine and standalone replicator.

Study a typed library design for initial table synchronization and ongoing WAL application. This is the canonical repository associated with earlier `pg_replicate` references; forks of that earlier code are not separate entries here. The README explicitly identifies the project as under active development before its first stable release.

- **C1:** Table-sync workers copy consistent snapshots and catch up before handing responsibility to an apply worker. The architecture explicitly promises at-least-once delivery and explains the failure window between destination commit and checkpoint persistence. Parallel catch-up does not imply global transaction-boundary delivery. [Architecture and table states](https://github.com/supabase/etl/blob/main/site/content/docs/explanation/architecture.mdx).
- **C2:** `Destination`, state, schema, and lifecycle store traits separate data delivery from durable recovery state; destinations distinguish accepted work from durable completion.
- **C3:** Parallel initial-copy workers and batched ongoing events address throughput without hiding the ordering contract. Stable `commit_lsn`/`tx_ordinal` sequence keys help consumers implement ordered, idempotent replay. [Event semantics](https://github.com/supabase/etl/blob/main/site/content/docs/explanation/events.mdx).

### 15. [sequinstream/sequin](https://github.com/sequinstream/sequin)

**Language / role:** Elixir; PostgreSQL CDC delivery to queues, streams, search indexes, and HTTP consumers.

Study replication through OTP processes, supervision, and demand-driven stages. The distinctive material is the relationship between WAL intake, per-consumer buffers, acknowledgement, and persistent retry handling.

- **C1:** The slot message store documents consumer-crash detection and replay after an ephemeral buffer fails. Failed deliveries are handled separately through persistent storage and redelivery, making durability boundaries explicit. [Message-store lifecycle](https://github.com/sequinstream/sequin/blob/main/lib/sequin/runtime/slot_message_store.ex).
- **C2:** The replication producer emits a common message structure with commit position, within-transaction index, relation information, and batch markers, allowing downstream stages and sinks to share the capture machinery. [GenStage slot producer](https://github.com/sequinstream/sequin/blob/main/lib/sequin/runtime/slot_producer/slot_producer.ex).
- **C3:** Demand-driven WAL emission and buffer-limit backpressure connect downstream consumption to source intake instead of allowing unbounded buffering.

GitHub metadata showed its latest repository push in February 2026 and no archive flag. This report makes no stronger claim about current maintenance cadence.

## Trigger-based and heterogeneous replication

### 16. [jumpmindinc/symmetric-ds](https://github.com/jumpmindinc/symmetric-ds)

**Language / role:** Java and database-specific SQL; heterogeneous, bidirectional database synchronization.

Study durable replication across intermittently connected nodes. SymmetricDS separates capture, routing, batching, transport, and loading; the public core and commercial Pro capabilities should be distinguished.

- **C1:** Trigger capture records change data and transaction identity. Batch state exists on both source and destination. Its conflict resolver also handles database-specific timestamp representations and type conversion, showing that conflict resolution depends on value semantics as well as policy. [Capture-to-delivery architecture](https://symmetricds.org/docs/how-to/how-symmetricds-works/), [conflict resolver](https://github.com/jumpmindinc/symmetric-ds/blob/release/3.18/symmetric-io/src/main/java/org/jumpmind/symmetric/io/data/writer/DefaultDatabaseWriterConflictResolver.java).
- **C2:** Node groups, push/pull links, configurable routers, and database-platform abstractions support hub-and-spoke networks, filtered replicas, and heterogeneous targets.
- **C3:** Routing groups changes into destination batches; transactional batching can exceed the nominal size to preserve a transaction grouping. This makes the throughput/correctness interaction visible.

The canonical GitHub owner is `jumpmindinc`, despite older `JumpMind/symmetric-ds` links elsewhere.

### 17. [bucardo/bucardo](https://github.com/bucardo/bucardo)

**Language / role:** Perl, PL/Perl, and SQL; trigger-based PostgreSQL multimaster and source-to-target replication.

Study a long-lived alternative to WAL decoding: change-tracking tables and triggers, configurable synchronization groups, and explicit conflict policies. The replication catalog and trigger construction are substantial parts of the implementation. [Schema and trigger machinery](https://github.com/bucardo/bucardo/blob/master/bucardo.schema).

- **C1:** The conflict tests build three writable sources and a fourth target, create simultaneous conflicting rows, and verify convergence under configured source-priority strategies. This is unusually concrete material for studying multiwriter semantics. [Conflict regression test](https://github.com/bucardo/bucardo/blob/master/t/40-conflict.t).
- **C4:** The changelog documents years of PostgreSQL compatibility changes, reload races, process-restart fixes, quoting fixes, and conflict-test improvements. [Changes](https://github.com/bucardo/bucardo/blob/master/Changes).

Treat it as a mature historical study target with limited recent activity: the changelog’s latest named release is 5.6.0 from February 2020, and GitHub metadata showed a May 2025 push. It was not archived when checked; that does not establish current-version database support.

## Specialized Oracle and MongoDB capture

### 18. [bersler/OpenLogReplicator](https://github.com/bersler/OpenLogReplicator)

**Language / role:** C++; Oracle CDC through direct binary redo-log parsing.

Study the reconstruction of transactions from a database’s physical log representation. It emits committed changes to outputs such as Kafka and JSON/Protobuf streams; it does not perform an initial application-data load.

- **C1:** Redo contains interleaved, uncommitted, and rolled-back work. The parser reconstructs transactions, emits them in commit-SCN order, and restarts from the low-water mark needed to rebuild open transactions. Checkpoints do not contain complete transaction bodies, so log retention is part of recoverability. [Architecture and transaction processing](https://github.com/bersler/OpenLogReplicator/blob/master/documentation/user-manual/2.architecture-and-components.adoc).
- **C3:** Reader, parser, writer, and checkpoint threads have different responsibilities. A bounded pool and transaction-data spilling address memory pressure, while the manual explicitly distinguishes heap-allocated metadata and LOBs from pool-controlled memory.

Version caveat: the README identifies 1.9 as stable and 2.0 as development; the linked manual describes 2.0. It also says release validation uses a private test suite. Those private-test claims were not independently inspected and do not support a C4 assignment here.

### 19. [rwynn/monstache](https://github.com/rwynn/monstache)

**Language / role:** Go; MongoDB change-stream/oplog synchronization into Elasticsearch.

Study a specialized database-to-search replica with direct initial reads, incremental updates, document transformation, and restart metadata. The `rel6` branch uses the official MongoDB Go driver and defaults to change streams.

- **C1:** Resume positions can be timestamps or per-stream tokens. The implementation coordinates bulk flushing with saving those positions and tracks completed direct-read namespaces, exposing the recovery boundary between ingestion and indexing. [Indexing and resume implementation](https://github.com/rwynn/monstache/blob/rel6/monstache.go).
- **C2:** Namespace selection, mappings, transformation hooks, direct reads, and selectable resume strategies allow the same daemon to support different search projections. [Configuration reference](https://rwynn.github.io/monstache-site/config/).
- **C3:** Bulk processing and separate processing/indexing channels make batching and concurrency explicit rather than issuing one synchronous destination request per source change.

The README targets MongoDB 3.6+ and Elasticsearch 7.0+; do not infer support for every newer major version. GitHub metadata showed an August 2025 push and no archive flag.

## Selective replication toward applications and clients

### 20. [electric-sql/electric](https://github.com/electric-sql/electric)

**Language / role:** Elixir replication service within a broader TypeScript-heavy monorepo; selective PostgreSQL-to-client synchronization.

The relevant subsystem is **`packages/sync-service`**, not the repository’s newer agent-platform components. It consumes PostgreSQL logical replication and serves subsets called Shapes through HTTP. [Sync-service overview](https://github.com/electric-sql/electric/blob/main/packages/sync-service/README.md).

- **C2:** Shapes express selected tables, rows, and columns; multiple clients can consume the same shape, and shapes can overlap. This supplies a reusable partial-replication model for applications, caches, and local databases. [Shape model](https://github.com/electric-sql/electric/blob/main/website/docs/sync/guides/shapes.md).
- **C1:** The snapshotter coordinates publication membership, consumer state, persisted snapshot availability, and error notification. Restored storage is checked after startup because cleanup or format changes can alter whether a snapshot remains available. [Snapshotter implementation](https://github.com/electric-sql/electric/blob/main/packages/sync-service/lib/electric/shapes/consumer/snapshotter.ex).
- **C3:** It distinguishes waiting for a database connection from waiting for the first result, allowing slow queries to time out without charging connection-pool queueing time against the query’s first-data budget.

### 21. [powersync-ja/powersync-service](https://github.com/powersync-ja/powersync-service)

**Language / role:** TypeScript; backend CDC and selective synchronization service for client-side SQLite databases.

Study the bridge from database-native replication positions to the checkpointed bucket history served to clients. The monorepo contains source modules, storage modules, shared service logic, and sync-rule processing; it is counted once.

- **C1:** Source resume position and client-visible checkpoint ID are distinct. A completed source commit may remain invisible while initial snapshots or catch-up boundaries are unresolved. Dynamic parameter lookups must be evaluated at the same checkpoint as bucket data. [Checkpoint semantics](https://github.com/powersync-ja/powersync-service/blob/main/docs/replication/06-checkpoints.md).
- **C2:** Source connectors and storage writers share lifecycle contracts while retaining database-specific snapshot/stream handoff strategies. [Snapshots and streaming](https://github.com/powersync-ja/powersync-service/blob/main/docs/replication/05-snapshots-and-streaming.md).
- **C3:** Checkpoint-change tracking and bucket checksums reduce the work and data transferred to clients. The documentation explicitly treats change hints as an optimization that may return false positives, keeping correctness independent of that optimization.

## SQLite page replication and recovery

### 22. [benbjohnson/litestream](https://github.com/benbjohnson/litestream)

**Language / role:** Go; continuous SQLite replication to external storage for recovery.

Study replication below the SQL row level and the interaction between SQLite WAL lifecycle and remote durability. The current source uses LTX files and a storage-client abstraction; older descriptions focused only on copying WAL segments do not fully describe this version.

- **C1:** The database component coordinates WAL observation, long-lived read transactions, synchronization state, and checkpointing. It also exposes filesystem error injection for staging files, including disk-full failures. [Database and checkpoint implementation](https://github.com/benbjohnson/litestream/blob/main/db.go).
- **C2:** `ReplicaClient` abstracts initialization, LTX enumeration, ranged reads, writes, and retention across different storage backends. [Storage interface](https://github.com/benbjohnson/litestream/blob/main/replica_client.go).
- **C3:** The checkpoint path attempts passive progress before a blocking truncation and avoids unnecessary LTX work for bookkeeping-only changes. The storage interface distinguishes fast listing timestamps from metadata needed for timestamp-based restore.

Its primary role here is recoverable external replication; it should not be mistaken for a consensus-based writable database cluster.

### 23. [superfly/litefs](https://github.com/superfly/litefs)

**Language / role:** Go; FUSE-based live SQLite replication across machines.

Study the interception of filesystem operations to identify database transaction boundaries without replacing the application’s SQLite API. The architecture separates the FUSE layer, leader-election leases, and an HTTP replication service.

- **C1:** Replicas exchange both transaction IDs and rolling database checksums. Equal transaction IDs with different contents signal divergence; a replica then resnapshots instead of applying incompatible history. The design explicitly acknowledges that asynchronous failover can discard transactions. [Architecture and split-brain behavior](https://github.com/superfly/litefs/blob/main/docs/ARCHITECTURE.md).
- **C3:** LTX files package changed pages for replication and compaction. The rolling checksum removes the old page contribution and adds the new one, avoiding a complete database checksum scan on every transaction.
- **C2:** Separating transaction capture from lease management and HTTP transfer makes the system applicable to ordinary SQLite-backed applications across different deployment environments.

The architecture’s planned features should not be treated as implemented. GitHub metadata showed a May 2026 push and no archive flag; no stronger maintenance commitment is inferred.

### 24. [canonical/dqlite](https://github.com/canonical/dqlite)

**Language / role:** C; embeddable SQLite-based replicated SQL engine using Raft.

Study the connection between local SQLite execution and replicated state-machine progress. The relevant material includes its custom VFS, leader execution state machine, and Raft integration; Go bindings are not counted as an independent engine.

- **C1:** Leader execution has explicit states for barriers, queueing, running, and waiting for Raft application. It checks whether replicated state has caught up before proceeding and rechecks after queued work has waited. [Leader state machine](https://github.com/canonical/dqlite/blob/main/src/leader.c).
- **C2:** The engine is an embeddable C library with a wire protocol and reusable database/network components, rather than an application-specific replication script.
- **C3:** Its VFS implements SQLite page/WAL mechanics directly, including checksum and memory-map alignment handling; the surrounding asynchronous architecture makes storage and replication scheduling visible. [VFS implementation](https://github.com/canonical/dqlite/blob/main/src/vfs.c).

Unlike asynchronous replica/back-up tools, this study target couples database progress to consensus. Its platform requirements should be read before extrapolating the design to other operating systems.

## Search coverage and limitations

Discovery used more than six distinct live-web search formulations, including broad CDC platforms; MySQL binlog clients in Java, Go, and Python; PostgreSQL logical extensions and migration clients; trigger-based heterogeneous replication; SQLite page/WAL replication; Oracle redo parsing; MongoDB-to-search replication; TiCDC distributed flow control; Vitess VReplication; and Rust/Elixir CDC engines. Later searches for older Databus/Brooklin/Otter-style systems and general alternatives mostly overlapped the established architecture families or returned comparison pages with weaker evidence. Those secondary pages were not used to substantiate entries.

Every retained canonical URL was verified through the GitHub repository API, including the default branch and archive flag. Repository material was then read alongside additional design documents, implementation files, or tests. Source-tree paths were checked through GitHub tree listings, and raw files were read without executing candidate code. No retained repository was marked archived at the time of the check. That observation is not a maintenance guarantee; sparse activity, old release lines, historical documentation, and explicit development status are called out where material.

The selection excludes tutorials, awesome-lists, thin connector wrappers, failover-only managers, and general ETL engines whose CDC implementation was not the clearest study target. It also avoids listing full database engines merely because they contain replication. Vitess, Electric, and PowerSync are included only for identified, substantial replication subsystems. TiFlow’s older TiCDC implementation, old owner URLs, client bindings, and forks of the same implementation are not counted again. All selected entries point to substantive GitHub source repositories; none is presented as an official mirror of a project hosted elsewhere.

Coverage is strongest for PostgreSQL/MySQL and includes distinct Oracle, MongoDB, heterogeneous-trigger, and SQLite approaches. SQL Server and Db2 appear through multiproduct connector platforms rather than dedicated entries. This is not an exhaustive inventory of commercial replication products or every historical implementation. No software was installed, run, benchmarked, or subjected to a correctness audit. Numerical marketing claims were intentionally not used as quality evidence, and private tests were not treated as inspected evidence. Delivery guarantees remain conditional on the documented configuration, source retention, destination semantics, and release being studied.
