# Relational database servers

Research date: **2026-10-09**.

This selection covers **24 GitHub repositories** implementing relational database servers or substantial distributed relational serving systems. It spans conventional transactional databases, distributed SQL, versioned data, analytical SQL databases, and streaming relational views. Analytical and streaming systems are labeled explicitly: their transaction, mutation, and constraint semantics should not be assumed equivalent to a general-purpose OLTP database. H2 and Derby qualify through their network-server implementations; Vitess qualifies through its substantial SQL-serving and database-clustering implementation over MySQL.

The aim is to identify codebases from which an experienced engineer can study difficult, reusable systems engineering. Criteria assignments are judgments grounded in the linked primary material, not certifications of correctness or claims that every subsystem is equally exemplary. Repository popularity was not used as evidence. Publicly readable source is the requirement here; this is not an exclusively OSI-licensed list, and notable source-available licensing is identified below.

## Criteria

- **C1 — Difficult correctness:** concurrency, consistency, recovery, invariants, SQL semantics, or adversarial failure cases.
- **C2 — Reusable abstractions:** substantial interfaces or representations supporting multiple operations, workloads, or deployment modes.
- **C3 — Performance with structure:** explicit treatment of CPU, memory, storage, network, or latency constraints within an understandable architecture.
- **C4 — Sustained evolution:** years of development with evidence of compatibility handling, testing, or deliberate complexity management.

## Conventional relational servers

### 1. [postgres/postgres](https://github.com/postgres/postgres)

**Language/role:** C; general-purpose object-relational server. **Repository status:** official PostgreSQL Git mirror; normal contribution review takes place outside GitHub.

An unusually rich starting point for understanding how a database reconciles extensible SQL semantics with concurrent storage. A productive reading path is a single index access method, followed by the SQL extension interfaces, rather than attempting the entire backend at once.

- **C1:** The B-tree design explains concurrent splits, high keys and sibling links, backward scans, page deletion, and the interaction between VACUUM and tuple-ID reuse. These are concrete invariants whose violations can silently omit or duplicate query results. [B-tree implementation notes](https://raw.githubusercontent.com/postgres/postgres/master/src/backend/access/nbtree/README).
- **C2:** Types, functions, aggregates, operators, and index operator classes are explicit extension mechanisms. Their interaction with planner information and extension update scripts makes this useful for studying an extensible language runtime inside a server. [Extending SQL](https://www.postgresql.org/docs/current/extend.html).
- **C3:** The same B-tree notes explain shortening page-lock lifetimes, copying matching tuple IDs into backend-local memory, and the tradeoffs imposed by variable-sized keys. The performance reasoning is attached directly to the concurrency argument.

**Entry points:** the B-tree notes and SQL extension manual linked above.

### 2. [mysql/mysql-server](https://github.com/mysql/mysql-server)

**Language/role:** C and C++; transactional SQL server, including the InnoDB subsystem and other server components. Counted once, including the MySQL Cluster code in the same repository.

Study the boundary between SQL execution and storage-engine responsibilities, then follow a consistent read through undo history and secondary-index access. This is especially instructive when an optimization must remain valid across multiple physical representations of one logical row.

- **C1:** InnoDB reconstructs prior row versions from undo records. Insert and update undo have different retention rules, and secondary indexes require visibility checks against clustered records. Purging cannot discard history still needed by a reader. [InnoDB multi-versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html).
- **C3:** Buffer pools, log buffers, tablespaces, redo logs, and doublewrite storage form a concrete division between memory and disk work. Index-condition pushdown can avoid a clustered lookup, but the MVCC documentation explains when the lookup remains necessary. [InnoDB architecture](https://dev.mysql.com/doc/refman/8.4/en/innodb-architecture.html).

**Entry points:** the architecture diagram and multi-versioning chapter above; the relevant engine lives under the repository's `storage` subsystem.

### 3. [MariaDB/server](https://github.com/MariaDB/server)

**Language/role:** C and C++; general-purpose SQL server. **Lineage:** a substantive, independently evolved MySQL fork, retained separately because its engine ecosystem, SQL extensions, and replication integrations provide distinct study material.

The useful theme is preserving a common SQL surface while permitting tables to have different storage behavior. Its repository describes temporal tables, multiple replication modes, and MySQL/Oracle-oriented compatibility, making it a useful comparison with upstream MySQL rather than a duplicate entry.

- **C2:** Storage engines are plugins selected per table. The documented interface supports transactional, write-heavy, federated, sharded, and archival use cases; even a single query can span engines, subject to engine-specific restrictions. [Storage-engine overview](https://mariadb.com/docs/server/server-usage/storage-engines/storage-engines-storage-engines-overview).
- **C3:** Engine selection explicitly trades read/write mix, I/O reduction, temporary storage, and remote archival requirements. The abstraction has practical performance consequences, rather than merely providing interchangeable class names. The server tree also separates `sql`, `storage`, `plugin`, and `tpool`. [Server source and feature overview](https://github.com/MariaDB/server).

**Entry points:** the storage-engine overview above and the repository's `storage`/`sql` subsystems. ColumnStore is an ecosystem integration, not an additional repository counted here.

### 4. [FirebirdSQL/firebird](https://github.com/FirebirdSQL/firebird)

**Language/role:** C and C++; cross-platform relational server, client libraries, and tools.

Firebird is particularly useful for studying record-version visibility and the observable semantics of retrying work inside the database. Its transaction documentation connects concurrency behavior to stored procedures, triggers, autonomous transactions, and externally visible side effects.

- **C1:** Read-consistency mode uses statement snapshots and follows back-version chains. Conflict handling can restart a top-level statement while retaining acquired write locks; triggers may therefore run more than once, and statements that have already returned rows have different restart behavior. [Transaction control](https://www.firebirdsql.org/file/documentation/chunk/en/refdocs/fblangref50/fblangref50-transacs.html).
- **C2:** Snapshot sharing across database attachments supplies one consistent view to parallel readers. The same transaction machinery applies to direct SQL and nested procedural work, exposing reusable consistency mechanisms across backup, application, and stored-program workloads. The repository confirms the broader stored-procedure and trigger implementation. [Project README](https://raw.githubusercontent.com/FirebirdSQL/firebird/master/README.md).

**Entry points:** transaction control, especially shared snapshots and statement restart, followed by the server implementation in the repository.

### 5. [CUBRID/cubrid](https://github.com/CUBRID/cubrid)

**Language/role:** C and C++, with Java components; object-relational server and connection-broker system.

CUBRID offers a less commonly studied implementation with unusually concrete source-level examples of visibility classification and parallel recovery. The transaction subsystem is a manageable entry into a larger server.

- **C1:** Its MVCC record header separates insert/delete transaction IDs from the log address of the previous version. Snapshot checks distinguish visible, too-old, and too-new records; deletion and vacuum have their own result classifications. Those distinctions expose the invariants shared by readers, writers, and garbage collection. [MVCC declarations and explanatory comments](https://raw.githubusercontent.com/CUBRID/cubrid/develop/src/transaction/mvcc.h).
- **C3:** Parallel redo uses worker tasks, reusable job pools, synchronous exceptions, and tracking of the minimum unapplied log position. Comments explain lifetime ownership, synchronization, and why a recovery-specific termination mechanism is needed beyond the general worker pool. [Parallel redo infrastructure](https://raw.githubusercontent.com/CUBRID/cubrid/develop/src/transaction/log_recovery_redo_parallel.hpp).

**Entry points:** the two source files above. Both were read directly after the browser reader failed on their GitHub blob pages.

### 6. [h2database/h2database](https://github.com/h2database/h2database)

**Language/role:** Java; SQL database with both embedded and network-server modes.

H2 is useful when a smaller deployment footprint is desirable for learning, but the engineering question still involves a real SQL engine. Its documentation is candid about the behavior and limitations hidden behind familiar JDBC interfaces.

- **C1:** The advanced manual specifies dirty-read, repeatable-read, snapshot, and serializable behavior, including a limitation: its documented serializable mode does not ensure serial equivalence for concurrent write transactions. That is valuable material for studying the gap between isolation names and implemented guarantees. [Advanced transaction documentation](https://h2database.com/html/advanced.html#transaction_isolation).
- **C2:** The same engine supports embedded/server operation and persistent/in-memory databases, while linked tables adapt external JDBC databases into the local SQL interface. [Server and engine overview](https://github.com/h2database/h2database), [linked-table behavior](https://h2database.com/html/advanced.html#linked_tables).
- **C3:** Large result sets spill to disk and use external sorting; large objects are streamed, with explicit inline-versus-separate storage tradeoffs. These make concrete exercises in bounding memory under a general relational interface. [Advanced manual](https://h2database.com/html/advanced.html).

**Entry points:** the advanced manual and engine repository. The older architecture page contains historical storage-engine descriptions, so it was not used to describe current internals.

### 7. [apache/derby](https://github.com/apache/derby)

**Language/role:** Java; embedded relational engine plus a network database server. **Status:** historical/read-only project. Apache reports that development and bug fixing ended following the retirement vote on 2025-10-10.

Derby is retained as a study of standards-oriented Java server design and compatibility management over a long release history, not as a recommendation for a newly maintained deployment.

- **C2:** The engine, embedded JDBC driver, network server, and network JDBC client expose different deployment boundaries around relational functionality. The release documentation identifies these components explicitly. [10.17 release documentation](https://db.apache.org/derby/releases/release-10_17_1_0.cgi).
- **C4:** Apache's release history runs from the 2004 incubation release through 2023. Release 10.17 documents its Java 21/JDBC 4.2 requirements, incompatibilities with older Java runtimes, and bug-fix changes from the preceding release. This provides concrete evidence of managing compatibility as the host platform evolves. [History and retirement notice](https://db.apache.org/derby/), [release changes](https://db.apache.org/derby/releases/release-10_17_1_0.cgi).

**Entry points:** the release notes and the repository's Java engine/server/client implementation.

## Distributed transactional and clustered SQL systems

### 8. [cockroachdb/cockroach](https://github.com/cockroachdb/cockroach)

**Language/role:** primarily Go; distributed transactional SQL server using the PostgreSQL wire protocol. **License note:** the repository identifies modern releases as using the CockroachDB Software License; public source availability should not be confused with unrestricted open-source licensing.

An excellent study of making distributed transaction state explicit. Focus on how provisional writes, transaction records, locks, and cleanup interact when a coordinator is delayed or fails.

- **C1:** Transactions can cross ranges and tables. The transaction layer distinguishes pending, staging, committed, and aborted records; write intents reference these records, and later operations can resolve leftover intents. This is a concrete treatment of atomicity beyond one replica group. [Transaction-layer architecture](https://docs.cockroachlabs.com/docs/stable/architecture/transaction-layer).
- **C2:** Transaction coordination, concurrency management, lock tables, latches, timestamp handling, and the distribution layer have documented responsibilities rather than being folded into the SQL frontend.
- **C3:** Parallel Commits and asynchronous cleanup separate the work required to acknowledge a commit from later bookkeeping. Closed-timestamp reads provide another explicit latency/recency tradeoff. These optimizations are explained within the correctness model in the same architecture document.

**Entry point:** the transaction-layer document above; it is preferable to relying on the repository's explicitly historical original design document for current details.

### 9. [pingcap/tidb](https://github.com/pingcap/tidb)

**Language/role:** Go; MySQL-compatible distributed SQL frontend and supporting tools. **Scope:** TiDB's SQL-server repository; TiKV, TiFlash, and Placement Driver are cooperating components, not extra entries counted here.

The clearest learning opportunity is the separation between SQL semantics and a transactional distributed key-value substrate. It is useful for tracing one statement through protocol parsing, planning, execution, row encoding, and remote computation.

- **C1:** Distributed transactions and asynchronous schema operations require coordination beyond an individual server. The developer guide identifies an owner mechanism for work that only one TiDB instance may execute, and the repository describes its distributed transaction guarantees. [Development guide](https://pingcap.github.io/tidb-dev-guide/understand-tidb/introduction.html), [repository overview](https://github.com/pingcap/tidb).
- **C2:** `kv`, `table`, `tablecodec`, `distsql`, and storage-driver interfaces separate logical tables, encodings, transactions, and remote execution. This is substantive interface design with a readable package map.
- **C3:** The distributed-computation interface permits work to be pushed into storage. TiDB coordinates execution over row-oriented TiKV and column-oriented TiFlash, showing how a SQL layer can choose different physical execution paths.

**Entry point:** the development guide above, especially the KV API and package map; some explanatory text retains older package paths, so use its linked current packages when navigating.

### 10. [yugabyte/yugabyte-db](https://github.com/yugabyte/yugabyte-db)

**Language/role:** C++ distributed storage with PostgreSQL-derived C query code; distributed SQL database. **Monorepo focus:** YSQL and DocDB, not the management application also present in the repository.

Study how a reused, feature-rich relational query layer is adapted to a sharded storage system. This complements TiDB's independently implemented MySQL-compatible SQL layer.

- **C1:** Table shards, called tablets, have leaders and Raft-replicated followers. The repository describes distributed transactions and isolation levels, making the boundary between per-tablet replication and cross-tablet atomicity central to the code study. [Architecture](https://docs.yugabyte.com/stable/architecture/), [transaction overview in the repository](https://github.com/yugabyte/yugabyte-db).
- **C2:** The architecture separates query handling from storage, replication, and consistency. YSQL reuses PostgreSQL's query layer, while DocDB builds on RocksDB and is also used by another query API. This is a substantial example of storage reuse without making the APIs identical.
- **C4:** The repository documents the PostgreSQL 11-to-15 rebase, associated compatibility changes, and version-gated online upgrade/downgrade paths. That is concrete evidence of managing upstream evolution alongside distributed extensions.

**Entry points:** the architecture's query/storage layers and the repository's PostgreSQL compatibility and upgrade notes. The repository distinguishes the database's license from that of its management platform.

### 11. [oceanbase/oceanbase](https://github.com/oceanbase/oceanbase)

**Language/role:** C++; distributed relational database with a MySQL-compatible community implementation.

OceanBase adds a useful multi-tenant perspective: the engineering problem is not only spreading rows across machines, but also controlling which workloads own CPU, memory, disk, and fault-domain placement.

- **C1:** Multi-Paxos log streams maintain replica consistency across availability zones. Leaders accept modifications, while followers replicate them; tablets can move between log streams for resource balancing. [Developer architecture](https://oceanbase.github.io/oceanbase/architecture/).
- **C2:** The documentation separates observers, tablets, log streams, tenants, resource units, and resource pools. A tenant presents an independent database instance while drawing resources from a shared cluster.
- **C3:** Resource units partition CPU, memory, and disk, and routing uses cached partition information to direct requests to appropriate observers. This gives concrete mechanisms for locality and workload isolation, rather than only a scale-out claim.

**Entry point:** the developer architecture above. It discusses both MySQL and Oracle compatibility modes at product level; the entry does not assume every documented commercial capability is available in this repository's community build.

### 12. [vitessio/vitess](https://github.com/vitessio/vitess)

**Language/role:** Go; distributed SQL-serving and clustering system around MySQL. It is not an independent replacement for InnoDB's storage implementation.

Vitess is worthwhile for studying how a database fleet acquires a coherent application-facing query model. Its sharding abstractions and operational machinery are substantial enough to justify inclusion beyond ordinary database proxies.

- **C2:** VSchema maps a logical database view onto keyspaces and shards. Vindexes translate column values to keyspace IDs, while topology-distributed metadata lets VTGate plan and route queries. This supports resharding without exposing physical shard boundaries as application schema. [VSchema architecture](https://vitess.io/docs/25.0/reference/features/vschema/).
- **C3:** Connection pooling and query rewriting in VTTablet address concrete limits of existing MySQL servers. The architecture explains a progression from individual database efficiency to fleet-wide automation. [System architecture](https://vitess.io/docs/24.0/overview/architecture/).
- **C1:** Stable keyspace IDs across resharding and routing-rule distribution expose correctness obligations during topology change. This criterion is an inference from the documented routing model, rather than a claim that every distributed transaction mode has identical guarantees.

**Entry points:** system architecture and VSchema. The linked VSchema page is labeled development-version documentation.

### 13. [rqlite/rqlite](https://github.com/rqlite/rqlite)

**Language/role:** Go around SQLite; replicated relational database server with an HTTP API.

This is a focused way to study the additional machinery required to turn an embedded SQL engine into a fault-tolerant service. The SQL engine is reused, but consensus, request forwarding, cluster management, snapshots, and operational APIs are substantive server work.

- **C1:** Linearizable reads record a Raft commit index, confirm leadership with a quorum, and wait until the corresponding write is applied to SQLite. The final apply step is crucial: log commitment alone does not mean the SQL state machine has caught up. [Read-consistency specification](https://rqlite.io/docs/api/read-consistency/).
- **C3:** The same document contrasts local replica reads, leader reads, quorum-confirmed reads, and reads passed through the log. It explains the associated network, disk, and stale-read costs rather than hiding them behind a single consistency label.
- **C2:** SQLite remains the relational execution layer while the repository separates database access, store/consensus, snapshots, HTTP, and cluster communication. This supports a useful study of reuse at an engine/service boundary. [Repository layout and features](https://github.com/rqlite/rqlite).

**Entry point:** read consistency, followed by the repository's `store`, `db`, and `snapshot` components. Default reads should not be described as automatically linearizable.

### 14. [bloomberg/comdb2](https://github.com/bloomberg/comdb2)

**Language/role:** primarily C, with C++ and Java components; replicated relational database developed at Bloomberg.

Comdb2 is a valuable less-famous alternative to the usual Raft-based SQL examples. Its documented transaction lifecycle distributes query execution across replicas while centralizing the application of record changes at an elected leader.

- **C1:** A replica executes a statement and sends record changes to the leader; the leader validates and commits them, then distributes log records. Optimistic verification errors can trigger rollback and statement replay. The documentation discusses how retries can change what an application observes. [Transaction model](https://bloomberg.github.io/comdb2/transaction_model.html).
- **C3:** Replicas execute SQL with short-duration page read locks, while the replication path acquires its required locks before applying changes. The document explains deadlock-victim selection and the work that is deliberately kept off the leader until commit.
- **C2:** The repository identifies its SQLite-derived SQL VM and separate storage, client, and replication infrastructure. Reusing a query engine while replacing surrounding execution and transaction assumptions is a useful architectural comparison with rqlite. [Repository overview and component map](https://github.com/bloomberg/comdb2).

**Entry point:** the transaction model above. Its documented default replicated-read behavior should not be conflated with an unconditional linearizability guarantee.

## Versioned and cryptographically verifiable relational servers

### 15. [dolthub/dolt](https://github.com/dolthub/dolt)

**Language/role:** Go; MySQL-compatible SQL server with database branching, merging, and history.

Dolt is useful for exploring what changes when versions of entire relational datasets become first-class objects. Its SQL-server behavior distinguishes it from a file-format library or a version-control wrapper around exports.

- **C2:** A commit graph references immutable database roots built from table schema and data. The same representation supports branch, diff, merge, clone, and historical query operations. These capabilities are exposed through both CLI and SQL interfaces. [Storage-engine design](https://www.dolthub.com/blog/2024-02-29-storage-engine/), [SQL-server overview](https://github.com/dolthub/dolt).
- **C3:** Content-addressed Prolly Trees permit unchanged subtrees to share storage and allow comparisons to skip matching subtrees. This directly addresses the cost of keeping many versions and calculating relational diffs.
- **C1:** The repository illustrates relational constraints alongside version operations and explicitly distinguishes a SQL transaction commit from a Dolt history commit. Studying that boundary is a concrete exercise in composing transaction semantics with branch state.

**Entry points:** the storage-engine article and the repository's server/SQL version-control examples. The structural-sharing explanation is a design argument, not an independently reproduced performance benchmark.

### 16. [codenotary/immudb](https://github.com/codenotary/immudb)

**Language/role:** Go; server supporting relational SQL as well as key-value and document interfaces, with verifiable history.

The central study topic is the separation between a transaction ledger, its proof structure, and the mutable indexing machinery used for current queries. Restrict attention here to the SQL-serving path and its underlying storage contracts.

- **C1:** Transactions form entries in an immutable change log, with a parallel Merkle structure used for verification. The SQL layer requires an up-to-date index even though lower-level ledger operations may relax that dependency. [Layering and performance guide](https://immudb.io/docs/production/performance-guide/).
- **C2:** SQL rows and secondary indexes are translated into key-value entries over the same transaction substrate. This provides a concrete multi-model abstraction, with different requirements at each layer rather than one universal consistency/performance promise.
- **C3:** The guide explains asynchronous B-tree indexing, cache effects of key size and ordering, index write amplification, and remote-storage cache misses. These connect schema choices to physical costs.

**Entry points:** the performance guide and the repository's SQL/protocol implementation. Cryptographic verifiability should be read as a claim about detecting inconsistent history under the documented verification model, not immunity to every operational failure.

## Analytical relational servers

### 17. [MonetDB/MonetDB](https://github.com/MonetDB/MonetDB)

**Language/role:** primarily C; column-oriented relational database server. **Repository status:** official mirror of the project's Mercurial repository; contributions follow the upstream process.

MonetDB is a strong contrast to tuple-at-a-time transactional engines. The key learning path runs from SQL through an explicit intermediate language and optimizer pipeline to vectorized execution.

- **C2:** MonetDB Assembly Language, or MAL, separates the SQL frontend from the execution machinery. Its module interfaces allow custom extensions, and its optimization pipeline can be inspected independently of the SQL parser. [MonetDB internals](https://www.monetdb.org/documentation-Aug2024/dev-guide/monetdb-internals/).
- **C3:** The documented MAL virtual machine uses dynamic vectorized execution. The developer material includes optimizer and profiling entry points, making the connection between query transformations and execution costs visible.

**Entry point:** the versioned August 2024 internals documentation above. It is used for the documented architecture, not to assert the exact behavior of every later release.

### 18. [ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse)

**Language/role:** primarily C++; column-oriented analytical SQL database server.

ClickHouse is especially useful for studying how data representation, execution scheduling, and extensibility are made to cooperate. The architecture guide contains specific interfaces and the reasons behind them, rather than only a service diagram.

- **C2:** `IColumn`, data types, aggregate-function states, `IStorage`, and processor pipelines divide representation, serialization, table access, and execution. Table engines return pipelines that can be composed with further transformations. [Architecture guide](https://clickhouse.com/docs/development/architecture).
- **C3:** Functions operate on blocks for vectorized execution; storage can supply parallel readers or partially processed remote results. Aggregate states can be serialized for distributed execution or spilling, while MergeTree's sorted parts and sparse indexes reduce the data read.
- **C1:** Persisted aggregate states create compatibility obligations: the guide explicitly connects changes in serialized aggregate-state format to existing stored data. This is a concrete example of an internal optimization becoming a durable external contract.

**Entry point:** the architecture guide, especially tables, processors, aggregates, and MergeTree. Analytical SQL and primary-key indexing here do not imply conventional OLTP uniqueness or transaction semantics.

### 19. [apache/doris](https://github.com/apache/doris)

**Language/role:** C++ execution/storage backend and Java frontend; distributed analytical SQL database.

Doris is useful for comparing an integrated storage/compute deployment with a design that splits metadata, compute, and shared storage. Follow how the responsibilities of the same SQL frontend change as the physical deployment model changes.

- **C1:** Metadata changes require quorum confirmation. In the decoupled architecture, the Meta Service handles ingestion-transaction versioning, conflict detection, and rowset metadata used for recovery and garbage collection. [System architecture](https://doris.apache.org/docs/4.x/features-architecture/system-architecture/).
- **C2:** FE, BE, and Meta Service have distinct responsibilities; tablets and rowsets form explicit management units. The SQL-layer metadata/data-layer metadata distinction is particularly useful for understanding distributed catalog boundaries.
- **C3:** Columnar encoding, distributed query stages, vectorized execution, and pipeline scheduling address I/O, CPU parallelism, and thread-count constraints. Shared storage adds a cache/locality tradeoff that the documentation explains explicitly.

**Entry point:** the 4.x system-architecture document above. Vendor-provided speedup figures were not used as selection evidence.

### 20. [StarRocks/starrocks](https://github.com/StarRocks/starrocks)

**Language/role:** C++ execution/storage backend and Java frontend; MPP analytical database and query engine with native storage.

StarRocks is retained for its substantial independent implementation and development, even though its history and FE/BE vocabulary overlap the Doris family. The specific study focus is the relationship between native data organization and shared-data compute nodes.

- **C2:** Frontends plan and schedule queries; backends execute them and manage local data, while compute nodes serve the shared-data configuration. The documented shared-data mode reuses segment-file formats and indexing techniques from native tables. [Architecture](https://docs.starrocks.io/docs/introduction/Architecture/).
- **C3:** Local-storage execution avoids movement and copying. The shared-data configuration instead uses memory, local disk, and remote storage as a hierarchy, with caches and prefetching to reduce remote-read costs. This makes elasticity and locality tradeoffs concrete.
- **C1:** The frontend metadata replicas have distinct leader, follower, and observer responsibilities. Recovery and replication are architectural obligations rather than an assumption that stateless query workers alone provide availability.

**Entry points:** the architecture above and the repository's native SQL-engine overview. This entry does not repeat the project's comparative benchmark marketing as an independently established fact.

### 21. [apache/cloudberry](https://github.com/apache/cloudberry)

**Language/role:** primarily C with C++ components; PostgreSQL/Greenplum-derived MPP relational database. **Status/lineage:** Apache incubating project and substantive continuation of the Greenplum architecture, counted separately from PostgreSQL because distributed execution and transaction machinery materially change the server.

Cloudberry provides a direct route into the problem of extending local transaction IDs and snapshots into a distributed execution environment. The `src/backend/cdb` subsystem is the relevant scope within the larger PostgreSQL-derived tree.

- **C1:** Distributed snapshot checks map local transaction IDs to distributed IDs, consult distributed commit information, and distinguish local-only, unknown, in-progress, and visible cases. Recovery code resolves in-doubt prepared transactions and retries commit/abort notifications to segments. [Snapshot implementation](https://raw.githubusercontent.com/apache/cloudberry/main/src/backend/cdb/cdbdistributedsnapshot.c), [distributed recovery implementation](https://raw.githubusercontent.com/apache/cloudberry/main/src/backend/cdb/cdbdtxrecovery.c).
- **C3:** The snapshot implementation caches local/distributed mappings to avoid repeated distributed-log lookups and uses sorted in-progress IDs for early termination. These are specific optimizations embedded in visibility logic, making their safety assumptions inspectable.
- **C2:** The surrounding subsystem separates dispatch, data motion, transaction context, and recovery. [Distributed backend tree](https://github.com/apache/cloudberry/tree/main/src/backend/cdb).

**Entry points:** the snapshot and recovery source files. An older architecture-document URL returned 404, so source evidence was used instead.

### 22. [questdb/questdb](https://github.com/questdb/questdb)

**Language/role:** Java with C++ and Rust performance-sensitive components; time-series SQL database server.

QuestDB broadens the selection to relational serving where time order, ingestion concurrency, and late-arriving data dominate the physical design. It exposes SQL joins and time-series operators, but is a specialized analytical server rather than a general OLTP substitute.

- **C1:** Per-connection/table WAL streams permit concurrent ingestion. A sequencer assigns transaction numbers across them, while the table writer consolidates changes and handles out-of-order data and deduplication. [Storage-engine architecture](https://questdb.com/docs/architecture/storage-engine/).
- **C3:** The architecture separates a write path optimized for ingestion from columnar reads, uses time partitions, and supports native and Parquet representations. The repository further identifies memory-mapped data and SIMD/JIT-assisted execution. [Repository engine overview](https://github.com/questdb/questdb).
- **C2:** SQL spans different partition representations, keeping logical queries separate from physical storage choices.

**Entry point:** the storage-engine architecture above. The documentation includes enterprise-only remote-tier automation; it is not attributed to the open repository here. Performance numbers from the README were deliberately not adopted.

## Streaming relational servers

### 23. [risingwavelabs/risingwave](https://github.com/risingwavelabs/risingwave)

**Language/role:** Rust; distributed streaming relational system that maintains tables/materialized views and serves SQL through the PostgreSQL wire protocol.

RisingWave belongs here through its queryable relational state, rather than merely because it can parse SQL. It is useful for studying how continuous execution changes snapshot and recovery requirements.

- **C1:** The checkpoint design connects two obligations: recovering all stateful operators from one consistent point and serving tables/views from a consistent snapshot. Barriers fan out through dispatchers and align across the inputs of merge/join operators before checkpoint completion. [Checkpoint design](https://risingwavelabs.github.io/risingwave/design/checkpoint.html).
- **C2:** Sources, stateful operators, compute nodes, the metadata service, and shared storage have separate responsibilities. A local buffer exposes an operator's uncommitted updates to itself before globally committing the checkpoint.
- **C3:** Incrementally maintained results avoid recomputing entire relational queries for every read. The repository describes the distinct roles of its serving row store, object-backed state, and analytical storage integration. [System overview](https://github.com/risingwavelabs/risingwave).

**Entry points:** checkpoint design and the repository's streaming/storage subsystems. The design guide is architecture evidence; individual runtime defaults and newer optimizations should be checked against a chosen release.

### 24. [MaterializeInc/materialize](https://github.com/MaterializeInc/materialize)

**Language/role:** Rust; continuously maintained relational views and SQL serving, using PostgreSQL dialect/protocol. **License note:** the repository describes BSL 1.1 licensing for the standalone engine with later conversion to Apache 2.0.

Materialize is a strong study of turning incremental computation into a database contract. Its internal indexed state has to serve several changing queries while respecting logical time and bounded resource use.

- **C1:** The repository states that answers correspond to a consistent version of the data, including joins over multiple upstream sources. Its execution model represents updates using data, logical time, and multiplicity changes, making time and retractions part of query semantics. [Repository consistency overview](https://github.com/MaterializeInc/materialize), [arrangements](https://materialize.com/docs/fundamentals/concepts/arrangements/).
- **C2:** An arrangement is an indexed representation of a changing collection. Multiple queries can reuse it, rather than maintaining separate copies of equivalent intermediate indexes.
- **C3:** Shared arrangements and background compaction address repeated work and memory growth. The documentation also explains how index-key choice and implicit casts affect memory consumption, connecting SQL-level choices to internal state size.

**Entry point:** the arrangements document above, then the repository's developer documentation. This is a continuous-view serving design, not a claim of drop-in equivalence with every PostgreSQL application.

## Search coverage, boundaries, and limitations

Discovery used more than six meaningfully different query families: traditional C/C++ relational servers; distributed SQL and consensus; Java embedded/network engines; SQLite-based replicated servers; versioned and verifiable SQL; columnar/MPP analytics; Rust streaming databases; and less-famous systems such as CUBRID and Comdb2. Additional cross-check searches for other relational server families increasingly returned already-covered systems, client software, embedded engines, historical projects, or product integrations without sufficient implementation evidence for this selection.

Every retained canonical GitHub repository was opened. Each entry also uses opened official documentation, a source tree, release material, or directly read source files; discovery snippets alone were not treated as verification. Some GitHub blob pages and CUBRID manual pages failed in the browser reader. Direct public source reads supplied the missing CUBRID and Cloudberry evidence. The broken Cloudberry architecture URL is not offered as an entry point. No candidate code was executed, dependencies installed, or large repositories cloned.

SQLite and DuckDB themselves were excluded because their core role is embedded execution; rqlite is retained for the substantial server added around SQLite. Drivers, ORMs, management GUIs, thin proxies, and repository lists were excluded. Standalone query/federation engines without a comparable database storage/serving role were outside the principal scope. Proprietary database products without a substantive public GitHub server implementation were also excluded. This is a broad, evidence-backed selection, not a complete census of every qualifying server.

PostgreSQL and MonetDB are explicitly labeled official mirrors, Derby is explicitly retired, and source-available licensing is called out where material. Fork-derived entries are included for substantive architectural or evolutionary differences, not multiplied merely by repository ancestry. No blanket assertion of current maintenance is made for all entries. Documentation and default-branch links can change, and several sources are explicitly versioned or historical; the report establishes useful study directions as of the research date, not release-specific guarantees or comparative benchmark results.
