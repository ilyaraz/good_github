# Distributed transactional databases

Research date: **2026-10-09**. This selection covers **27 GitHub repositories** implementing distributed transactions: sharded SQL and key-value engines, transaction middleware, document and graph databases, replicated embedded databases, and substantial research implementations. The scope includes replication across machines as well as transactions across shards. Entries identify which case applies; these are different engineering problems.

The emphasis is on code an experienced engineer can study for transaction ordering, concurrency control, recovery, storage boundaries, and performance tradeoffs. Inclusion does not imply that all projects provide the same isolation, that every component is exemplary, or that every repository is suitable for deployment. Some repositories are source available under restrictive licenses; this is not an open-source license audit.

Criteria used below:

- **C1 — Difficult correctness:** concrete invariants, concurrent execution, failure recovery, or other demanding semantics.
- **C2 — Reusable abstractions:** substantial interfaces or architectural components supporting multiple uses.
- **C3 — Performance with structure:** identifiable performance constraints addressed through understandable design.
- **C4 — Sustained evolution:** documented years of development together with compatibility, testing, or complexity management.

Criterion assignments are research judgments grounded in the linked primary material. Every entry meets at least two criteria.

## Distributed SQL engines

### 1. [cockroachdb/cockroach](https://github.com/cockroachdb/cockroach)

**Language / role:** Go; distributed SQL over a replicated transactional key-value layer. Current releases use the CockroachDB Software License.

Study how an SQL transaction becomes MVCC reads, write intents, conflict checks, and a durable transaction record. The distinction between pending, staging, and committed transactions exposes why client-visible completion and background intent cleanup need not happen together.

- **C1:** The transaction layer explains lock tables, timestamp caches, read refreshing, and resolution of abandoned intents. These mechanisms connect concurrent execution and crash recovery rather than treating commit as a single Boolean operation.
- **C3:** Parallel Commits and transaction pipelining reduce coordination on the commit path while preserving evidence that writes were replicated. Follower reads introduce another explicit interaction between timestamps and replica visibility.

**Start here:** [Transaction-layer architecture](https://docs.cockroachlabs.com/docs/stable/architecture/transaction-layer), especially write intents, transaction records, and Parallel Commits. Timestamp and real-time guarantees should be read with the documented clock assumptions.

### 2. [yugabyte/yugabyte-db](https://github.com/yugabyte/yugabyte-db)

**Language / role:** C++ and C; distributed database with a PostgreSQL-derived SQL layer and the shared DocDB storage engine.

The useful study boundary is between query execution, tablet-level Raft replication, and distributed transaction visibility. A PostgreSQL-compatible interface does not remove the need to establish a safe read time across independently replicated tablets.

- **C1:** Hybrid logical clocks, safe hybrid times, and MVCC snapshots must remain valid across Raft leader changes. The transaction overview explains why a replica cannot answer a read merely because its local clock has advanced.
- **C2:** DocDB supports multiple query interfaces while centralizing distributed storage and transaction mechanisms. This makes the repository useful for studying which semantics belong in storage and which belong in a language frontend.

**Start here:** [Distributed transaction overview](https://docs.yugabyte.com/stable/architecture/transactions/transactions-overview/) for clock propagation, safe times, and consistent reads; the repository README for the query-layer/DocDB division.

### 3. [pingcap/tidb](https://github.com/pingcap/tidb)

**Language / role:** Go; distributed SQL execution and transaction coordination, typically over TiKV. TiKV appears separately because it is an independently reusable storage engine.

Study the translation of familiar SQL locking behavior into distributed prewrite and commit operations. The documentation makes differences from MySQL explicit instead of implying that wire compatibility guarantees identical concurrency semantics.

- **C1:** Pessimistic transactions distinguish snapshot reads from current reads, acquire distributed locks, detect deadlocks, and still use the two-phase commit machinery. Lock timeouts, DDL interaction, and retries create concrete correctness boundaries.
- **C3:** Pipelined and in-memory pessimistic locking reduce latency, but change how locks survive failures. This is an unusually clear example of an optimization that must be understood alongside its recovery semantics.

**Start here:** [Pessimistic transaction design and behavior](https://github.com/pingcap/docs/blob/master/pessimistic-transaction.md), including implementation details and compatibility differences. This primary documentation source was inspected directly because some rendered documentation requests timed out.

### 4. [oceanbase/oceanbase](https://github.com/oceanbase/oceanbase)

**Language / role:** C++; distributed relational database with tenant isolation and replicated partitions.

OceanBase offers a substantial example of coordinating transactions inside a system that also schedules tenant resources and chooses local, remote, or distributed SQL execution plans.

- **C1:** The architecture describes two-phase commit, transaction participant information recorded in logs, and recovery that can complete or abort transactions after coordinator failure. MVCC and tenant timestamp services connect commit decisions to snapshot visibility.
- **C2:** Storage, replication, transaction, and SQL layers sit beneath tenant-level resource isolation. These boundaries support multiple tenants and different query execution shapes without making every concern part of the transaction coordinator.
- **C3:** Locality-aware plan selection, parallel subplans, and plan caching make distribution costs visible in the design.

**Start here:** [Official architecture overview](https://en.oceanbase.com/docs/common-oceanbase-database-10000000000829641). The inspected page documents version 4.0.0; use it as a versioned architectural guide, not proof that every detail matches the current branch.

### 5. [ydb-platform/ydb](https://github.com/ydb-platform/ydb)

**Language / role:** C++; distributed SQL database built around actors, tablets, and coordinated transaction planning.

The contributor documentation goes beyond a high-level ACID claim: it explains proposers, coordinators, mediators, participants, plan steps, and persistent messages between shards.

- **C1:** Distributed execution requires consistent planning and recovery of participant communication. Persistent ReadSets use at-least-once delivery; transaction ordering can change only where the reordering is unobservable.
- **C2:** The proposer/participant framework covers data manipulation, schema operations, and TTL processing. It is a substantial reusable coordination mechanism rather than one SQL-specific commit routine.
- **C3:** Single-shard paths and volatile transactions remove coordination or persistent writes from selected critical paths. The documentation also explains the resulting restart and abort behavior.

**Start here:** [DataShard distributed transaction internals](https://ydb.tech/docs/en/contributor/datashard-distributed-txs). The Calvin influence is useful context, but YDB's implementation should not be treated as an unchanged implementation of Calvin.

### 6. [dingodb/dingo](https://github.com/dingodb/dingo)

**Language / role:** Java; distributed SQL and multimodal execution layer using the separately implemented DingoStore storage service.

Dingo adds a less familiar implementation and a useful execution-engine perspective. Its documentation describes optimistic and pessimistic distributed transactions; the strongest inspected implementation evidence concerns the SQL task and operator framework.

- **C2:** Physical execution is decomposed into jobs, distributed tasks, operators, and connected input pins. Meta and storage APIs separate planning and execution from distributed storage implementation.
- **C3:** Send/Receive operators batch network traffic and manage queues and backpressure. Push execution, early termination for limits, and task reuse expose concrete choices about wasted work and communication cost.

**Start here:** [Project documentation and feature scope](https://dingodb.readthedocs.io/en/latest/) and [distributed executor architecture](https://dingodb.readthedocs.io/en/latest/architecture/executor.html). This entry counts the Java repository once; DingoStore is a dependency, not a second counted entry.

### 7. [apache/ignite-3](https://github.com/apache/ignite-3)

**Language / role:** Java; Ignite 3 distributed SQL and table database. This entry concerns Ignite 3 specifically, not the older Ignite 2 implementation.

Study how one transaction abstraction serves SQL and table operations while read-write and read-only transactions take different execution paths.

- **C1:** Read-write transactions use locks and wait-die deadlock prevention. Coordinator and primary-replica failures interact with transaction abort and retry; retryable transaction closures must avoid unsafe repeated side effects.
- **C2:** The same explicit transaction can govern table and SQL operations, with synchronous and asynchronous interfaces. This provides a useful API boundary above partition routing and replication.
- **C3:** Read-only transactions use MVCC snapshots and can read suitable non-primary replicas without acquiring the read-write transaction's locks. Snapshot retention and low-watermark management bound the cost.

**Start here:** [Ignite 3 transaction guide](https://ignite.apache.org/docs/ignite3/latest/developers-guide/transactions), including isolation, replica routing, and retry rules.

## Transactional key-value stores

### 8. [apple/foundationdb](https://github.com/apple/foundationdb)

**Language / role:** C++ with the Flow runtime; ordered transactional key-value database designed to support higher-level data models.

FoundationDB is especially useful for studying how a compact transaction interface can sit above a decomposed distributed system. Read-version proxies, commit proxies, resolvers, transaction logs, and storage servers have distinct responsibilities.

- **C1:** Clients submit conflict ranges and buffered writes; resolvers validate conflicts, and transaction logs establish durability before storage servers finish applying changes. Understanding these boundaries is central to recovery and serializable execution.
- **C2:** The ordered key-value and transaction interface supports separately implemented layers instead of embedding every data model in the database core.
- **C3:** Role separation and Ratekeeper make bottleneck management and backpressure explicit. They allow commit processing and storage work to scale and be controlled differently.

**Start here:** [Architecture](https://apple.github.io/foundationdb/architecture.html); the repository README also describes simulation testing and supported release branches. Some architecture-page storage-engine/version references are historical and were not treated as current product claims.

### 9. [tikv/tikv](https://github.com/tikv/tikv)

**Language / role:** Rust; independently usable transactional key-value engine with region-based Raft replication.

Study the separation between consensus within a region and transactions spanning regions. Raft agreement alone does not determine whether a multi-key transaction has committed everywhere.

- **C1:** The Percolator-style protocol uses primary and secondary locks, prewrite and commit phases, timestamps, and MVCC. The primary transaction outcome lets readers and recovery operations resolve secondary locks after interrupted execution.
- **C2:** Transactional and raw key-value APIs, together with storage-side processing interfaces, make TiKV reusable beyond TiDB's SQL frontend.
- **C3:** Region sharding and independent Raft groups divide replication and storage work; this adds a useful study of the interaction between data placement and transaction coordination.

**Start here:** [Percolator transaction deep dive](https://tikv.org/deep-dive/distributed-transaction/percolator/) and the repository's architecture overview. Read the documented isolation properties directly rather than equating all timestamp-based protocols with serializability.

### 10. [AntidoteDB/antidote](https://github.com/AntidoteDB/antidote)

**Language / role:** Erlang; geo-replicated transactional store built around CRDTs and causal consistency.

Antidote broadens the category beyond globally coordinated serializable databases. Its transaction semantics combine causal snapshots and conflict-free data types; certification and durability settings matter.

- **C1:** Snapshot timestamps, causal dependencies, certification, and CRDT convergence address different correctness obligations. The configuration documentation says certification operates within a data center; it does not establish global serializability across data centers.
- **C2:** Typed counters, sets, maps, registers, and other CRDT objects share interactive and static transaction interfaces. Applications can atomically update multiple objects without each implementing replication and merge logic.

**Start here:** [Configuration and protocol choices](https://antidotedb.gitbook.io/documentation/architecture/configuration) and [native transaction API](https://antidotedb.gitbook.io/documentation/api/native). Pay attention to transaction certification and synchronous-log options when interpreting guarantees.

## Extensions and transaction middleware

### 11. [citusdata/citus](https://github.com/citusdata/citus)

**Language / role:** C; PostgreSQL extension implementing distributed tables, planning, execution, and transactions.

This is a strong codebase for studying how to build distribution around an existing database's hooks, connections, transaction callbacks, and prepared transactions.

- **C1:** Multi-worker writes use PostgreSQL two-phase commit, with recovery of prepared transactions and distributed deadlock handling. Connection ownership and local transaction callbacks must align with remote outcomes.
- **C2:** Ordinary PostgreSQL tables become shards, while coordinator and worker components preserve substantial reuse of PostgreSQL itself.
- **C3:** Colocation, adaptive execution, and connection caching control network, connection-setup, and distributed execution costs.

**Start here:** [Distributed subsystem developer README](https://github.com/citusdata/citus/blob/main/src/backend/distributed/README.md), particularly transactions and connection management; its [raw rendering](https://raw.githubusercontent.com/citusdata/citus/main/src/backend/distributed/README.md) was read directly. The document explicitly states that Citus does **not** provide full distributed snapshot isolation: cross-node reads may observe a partially committed distributed transaction.

### 12. [vitessio/vitess](https://github.com/vitessio/vitess)

**Language / role:** Go; sharding and transaction middleware for MySQL.

Vitess makes transaction policy an explicit part of a routing system. Its Single, Multi, and TwoPC modes are valuable precisely because their guarantees differ.

- **C1:** TwoPC requires durable transaction state, prepare and commit transitions, recovery, and observability through distributed transaction identifiers. Partial failure is part of the normal protocol design.
- **C2:** VTGate routing and tablet-side execution separate application-facing transaction policy from the MySQL servers that store data.
- **C3:** The documentation connects cross-shard coordination overhead to schema and routing choices, encouraging transactions to remain within a shard where possible.

**Start here:** [Vitess 23 distributed transactions](https://vitess.io/docs/23.0/reference/features/distributed-transaction/). Multi mode does not guarantee atomic cross-shard commit. TwoPC provides atomicity but still allows fractured reads across shards; it should not be described as full cross-shard isolation.

### 13. [mysql/mysql-server](https://github.com/mysql/mysql-server)

**Language / role:** C++; Oracle's official MySQL source repository, with this entry scoped to the **NDB Cluster subsystem** rather than single-server InnoDB.

NDB provides a distinctive message-driven transaction implementation inside a large established database repository. Start with coordinator and local-query-handler responsibilities rather than attempting to read all of MySQL.

- **C1:** DBTC tracks transaction and operation state, takeover information, and coordination with local handlers. Prepare, commit, and completion messages must leave primary and backup row copies consistent and release locks correctly.
- **C2:** Kernel blocks, API connection records, transaction connection records, and shared pools structure a reusable asynchronous protocol supporting multiple concurrent operations and access paths.

**Start here:** [DBTC kernel-block internals](https://dev.mysql.com/doc/ndb-internals/en/ndb-internals-kernel-blocks-dbtc.html) and [Oracle's illustrated NDB two-phase commit walkthrough](https://dev.mysql.com/blog-archive/2-phase-commit-in-ndbcluster/). The latter is a historical explanation of the simplest single-row case, not a complete description of every present-day optimization.

### 14. [scalar-labs/scalardb](https://github.com/scalar-labs/scalardb)

**Language / role:** Java; transaction middleware over multiple underlying database implementations, rather than a standalone storage engine.

ScalarDB is useful for studying how a transaction protocol can be implemented above storage systems that expose the required conditional, linearizable operations.

- **C1:** Consensus Commit separates record preparation and validation from the authoritative coordinator-table outcome and subsequent record cleanup. Incomplete records can be recovered by consulting that outcome rather than assuming physical updates finish simultaneously.
- **C2:** A common transaction interface and storage adapters reuse the protocol across heterogeneous backends. The abstraction has meaningful prerequisites: the underlying operations must supply the semantics the protocol assumes.

**Start here:** [Consensus Commit design, version 3.17](https://scalardb.scalar-labs.com/docs/3.17/consensus-commit/). Read isolation and validation settings carefully: default behavior is not interchangeable with a globally consistent snapshot, and serializable behavior requires the documented validation mechanisms and constraints.

## Document, graph, and platform transaction engines

### 15. [mongodb/mongo](https://github.com/mongodb/mongo)

**Language / role:** C++; document database supporting multi-document transactions across sharded clusters.

MongoDB is especially instructive where transaction processing meets cluster administration. Moving chunks and changing shard membership cannot be treated as unrelated background activity.

- **C1:** Transactions interact with chunk migration, locks, commit decisions, and replica-set durability. Migration races can cause transaction aborts, and the supported shard configuration constrains execution.
- **C2:** Document operations retain an application-facing transaction interface while routers, shard participants, and replica sets divide distributed execution and durability responsibilities.

**Start here:** [Transactions in sharded clusters](https://www.mongodb.com/docs/manual/core/transactions-sharded-clusters/). The documentation distinguishes read concerns: a synchronized snapshot across shards requires the appropriate snapshot read concern; other transaction configurations must not be assumed to provide it. This entry studies the source repository without making an open-source licensing claim about its SSPL-covered components.

### 16. [dgraph-io/dgraph](https://github.com/dgraph-io/dgraph)

**Language / role:** Go; distributed graph database with transactional mutations and reads.

The interesting complexity is preserving a graph-facing transaction abstraction over partitioned predicates, indexes, facets, and replicated storage groups.

- **C1:** MVCC snapshots, timestamp allocation, write-conflict detection, and group replication must agree on transaction visibility. Graph and index changes need compatible commit behavior rather than independent best-effort updates.
- **C2:** The transaction interface spans the graph's data and indexing structures, separating graph operations from timestamp and replication machinery.
- **C3:** Snapshot reads avoid taking ordinary write locks, while storage buffering and the underlying LSM organization address write and read costs.

**Start here:** [Consistency model](https://docs.dgraph.io/design-concepts/consistency-model/). The documented snapshot-isolation behavior is the relevant guarantee here; this report does not infer full serializability from the presence of timestamps or real-time ordering language.

### 17. [ravendb/ravendb](https://github.com/ravendb/ravendb)

**Language / role:** C#; document database, with this entry focused on explicit **cluster-wide transactions**.

RavenDB's cluster transaction path is a useful contrast to its ordinary database replication. Consensus acceptance of a command and application of the resulting document changes are separate stages.

- **C1:** Raft orders cluster-wide commands and checks compare-exchange conditions. Local document application then follows that order; an application failure can block later cluster transactions until resolved. This makes the acceptance-versus-application boundary concrete.
- **C2:** Sessions combine document operations with compare-exchange and atomic guards to express constraints such as uniqueness through a reusable transaction API.

**Start here:** [Cluster-wide transaction architecture, version 7.1](https://docs.ravendb.net/7.1/server/clustering/cluster-transactions). These guarantees belong to the explicitly selected cluster-wide mode and its supported operations; they should not be attributed to every RavenDB operation or replication mode.

### 18. [SequoiaDB/SequoiaDB](https://github.com/SequoiaDB/SequoiaDB)

**Language / role:** C++; distributed document database with coordinators and replicated data groups.

SequoiaDB adds a substantive implementation and primary documentation outside the usual English-language database shortlist. The transaction material enumerates failure cases rather than stopping at a two-phase commit diagram.

- **C1:** Participants move through doing, wait-commit, committed, and rolled-back states. Coordinator failure, participant failure, network interruption, and primary changes require recovery rules that reconstruct the transaction outcome.
- **C2:** Coordinators operate over replicated groups whose primaries act as transaction participants. The separation provides reusable transaction coordination above group-local replication and leadership changes.

**Start here:** [Official Chinese-language distributed transaction documentation](https://doc.sequoiadb.com/cn/sequoiadb_back-cat_id-1600139301-edition_id-304), covering two-phase commit and failures. The accessible source was edition 3.4; newer documentation requests failed, so these are versioned architectural observations rather than verified current-branch behavior.

### 19. [ytsaurus/ytsaurus](https://github.com/ytsaurus/ytsaurus)

**Language / role:** Primarily C++; data-platform monorepo, scoped here to **dynamic tables and tablet transactions**.

YTsaurus is worth studying for how transactional row storage coexists with a much larger data platform. Master transactions for metadata and tablet transactions for dynamic table data are distinct concepts.

- **C1:** Timestamp allocation, MVCC, and two-phase commit establish atomic tablet transactions. Atomicity modes and read semantics are explicit: the documented transaction model does not provide read-your-own-uncommitted-writes behavior, and snapshot isolation is not full serializability.
- **C3:** Clients buffer writes, batch work, and obtain timestamps through batching infrastructure. These choices reduce coordination cost while making memory, commit timing, and visibility boundaries observable in the API.

**Start here:** [Dynamic-table transactions](https://ytsaurus.tech/docs/en/user-guide/dynamic-tables/transactions). The default full-atomicity path and the weaker non-atomic mode should be studied separately. The entire monorepo is counted once, not as a separate repository for each platform service.

### 20. [kronotop/kronotop](https://github.com/kronotop/kronotop)

**Language / role:** Java; document and ordered key-value layer over FoundationDB. **Developer preview**, with interfaces and formats subject to change.

Kronotop belongs as a substantial database layer, not as an independent consensus implementation. It adds document storage, query execution, session state, and commit hooks around FoundationDB's transaction primitive.

- **C1:** Sessions own transaction handles, rollback behavior, and post-commit actions. Snapshot-read mode changes conflict tracking, making the difference between an ordinary transactional read and a weaker read operationally visible.
- **C2:** Bucket/document operations and ordered ZMap operations can share an explicit transaction across namespaces. This is a useful example of exposing multiple data models through one underlying transaction system.

**Start here:** [Transaction architecture and commands](https://kronotop.com/docs/transactions/) and the repository's storage overview. Transaction limits are inherited from FoundationDB. The README explicitly excludes the vector graph index from transactional guarantees; post-commit index work must not be described as part of the same atomic commit.

## Replicated SQL and embedded transaction systems

### 21. [rqlite/rqlite](https://github.com/rqlite/rqlite)

**Language / role:** Go; Raft-replicated SQLite database. Replication provides a distributed service; this is not a horizontally write-sharded SQL engine.

The core study topic is how to combine an embedded database with a replicated log without paying for or depending on two unrelated durability mechanisms.

- **C1:** Raft log replay, snapshots, recovery, and SQLite state must remain consistent. SQL execution belongs to a replicated state machine rather than a collection of independently writable SQLite files.
- **C3:** The design uses the Raft log as the durability authority and manages SQLite synchronization and snapshots accordingly. Request batching can amortize consensus and transaction overhead.

**Start here:** [System design](https://rqlite.io/docs/design/) and [HTTP API transaction rules](https://rqlite.io/docs/api/api/). Atomic transactions are expressed through request batches with the transaction option. Manually issuing SQL BEGIN/COMMIT across requests is unsupported and is not a substitute for that API.

### 22. [canonical/dqlite](https://github.com/canonical/dqlite)

**Language / role:** C; embeddable replicated SQLite database library and server protocol.

Dqlite contrasts well with rqlite: the replication design works at SQLite's WAL-page boundary through a custom virtual filesystem, rather than treating replicated SQL text as the central abstraction.

- **C1:** Pending pages remain outside the visible WAL until replication succeeds, and write-lock handling prevents readers from observing changes before the required quorum durability. Failure handling must preserve both SQLite and Raft invariants.
- **C2:** The custom VFS, embedded server, and wire protocol form reusable boundaries around SQLite. The documented move away from a patched SQLite illustrates how to reduce coupling to upstream implementation details.
- **C3:** Replicating page changes avoids requiring followers to reproduce SQL execution deterministically. Batching and SQLite's single-writer behavior make the throughput tradeoffs understandable.

**Start here:** [Replication design](https://canonical.com/dqlite/docs/explanation/replication) and [architecture](https://canonical.com/dqlite/docs/explanation/architecture). This is replicated embedded storage, not cross-shard distributed SQL.

### 23. [bloomberg/comdb2](https://github.com/bloomberg/comdb2)

**Language / role:** C and C++; clustered relational database with replicated storage and client libraries.

Comdb2 gives a distinctive execution/commit split: replicas can execute queries and collect logical row changes, while the master applies changes through a shorter locked transaction and distributes physical logs.

- **C1:** Generation identifiers support optimistic verification, while coherent-replica leases and durable LSN rules constrain which data may be exposed. Retry handling must avoid changing results or duplicating completed operations.
- **C3:** Moving query work to replicas and keeping the master's commit interval short addresses contention at the serialization point.
- **C4:** The project's [history](https://bloomberg.github.io/comdb2/overview_home.html) documents many years of development and an original requirement for wire compatibility with an older internal system, providing concrete compatibility motivation rather than an age-only maturity claim.

**Start here:** [Transaction model](https://bloomberg.github.io/comdb2/transaction_model.html) and [durability and coherent replicas](https://bloomberg.github.io/comdb2/durable.html). This is a replicated cluster design, not a claim of arbitrary cross-shard transactions.

### 24. [erlang/otp](https://github.com/erlang/otp)

**Language / role:** Erlang; the **Mnesia subsystem** in the OTP monorepo implements a distributed database embedded in Erlang applications.

Mnesia is valuable because its transaction abstraction is a retryable function rather than a remote SQL session. That choice exposes a different set of integration and side-effect hazards.

- **C1:** Two-phase locking and wait-die deadlock handling can cause a transaction function to run again. Read locks generally involve one replica, while write locks involve active replicas, requiring coordination across nodes.
- **C2:** Transaction functions, nested transactions, and multiple activity/access contexts provide substantial reusable database interfaces inside the runtime ecosystem.
- **C3:** Sticky locks retain ownership to reduce future messages, making locality and contention tradeoffs explicit. Dirty operations provide separate, weaker access semantics rather than silently inheriting transactional guarantees.

**Start here:** [Mnesia source and tests](https://github.com/erlang/otp/tree/master/lib/mnesia) and [transactions and locking guide](https://www.erlang.org/doc/apps/mnesia/mnesia_chap4.html). Durability depends on table copy/storage configuration; not every Mnesia deployment has identical persistence guarantees.

## Historical and experimental transaction designs

### 25. [apavlo/h-store](https://github.com/apavlo/h-store)

**Language / role:** Java and C++; experimental shared-nothing, main-memory OLTP system. **Archived on 2025-08-10.**

H-Store is retained as a substantial research implementation, not a maintained deployment recommendation. Its code exposes interactions between partition ownership, stored procedures, transaction prediction, and speculative work.

- **C1:** Incorrect partition predictions can require rollback and re-execution as multi-partition transactions. Speculative work while another transaction awaits distributed execution creates explicit undo and recovery obligations.
- **C3:** Scheduling single-partition work during otherwise idle distributed-transaction intervals is a concrete attempt to reduce the cost of coordination. The configuration code documents the switches and assumptions behind these strategies.

**Start here:** [HStoreConf implementation and option documentation](https://github.com/apavlo/h-store/blob/master/src/frontend/edu/brown/hstore/conf/HStoreConf.java), particularly speculative execution, transaction estimation, and undo logging; use the repository README to locate its benchmark and stored-procedure workflow. Expect historical build and environment assumptions.

### 26. [yaledb/calvin](https://github.com/yaledb/calvin)

**Language / role:** C++; historical deterministic transaction research code, including experimental variants and conventional comparison implementations.

Calvin changes the ordering problem: transactions are ordered before execution, allowing replicas and partitions to follow a predetermined serial order. Study both the benefits and the work required when access sets are not known in advance.

- **C1:** Deterministic scheduling and locking must make concurrent execution equivalent to the chosen order. Replica agreement depends on handling nondeterminism and abort behavior consistently.
- **C3:** The authors compare deterministic execution with conventional two-phase locking and commit, examining contention, partitioning, and access discovery. The repository's variant directories are experimental artifacts rather than a polished modern framework.

**Start here:** [Authors' experimental evaluation](https://www.cs.umd.edu/~abadi/papers/determinism-eval.pdf) and the [official project page](https://dslam.cs.umd.edu/calvin/index.html), which links this repository. The code and experimental assumptions are historical; no claim of current maintenance or present-day build compatibility is made.

### 27. [umd-dslam/SLOG](https://github.com/umd-dslam/SLOG)

**Language / role:** C++; experimental geo-replicated deterministic transaction system. The repository says it is **not production ready** and is a rewrite of the paper implementation.

SLOG adds geographic locality to deterministic execution. Data has a home region; single-home and multi-home transactions require different coordination paths.

- **C1:** Ordering must reconcile local and geographically distributed transactions while preserving the system's intended strict serializability. Home ownership, replication, and multi-home execution are interdependent protocol concerns.
- **C3:** The design moves coordination outside contentious execution intervals and exploits home-region locality. This addresses WAN latency and contention together, rather than treating throughput as only a storage-engine problem.

**Start here:** [SLOG paper](https://www.cs.umd.edu/~abadi/papers/1154-Abadi.pdf) and the repository's architecture/demo instructions. The paper explains the design rationale; its benchmark results are not assumed to describe the rewritten repository without a separate evaluation.

## Search coverage, boundaries, and limitations

Discovery used more than twenty distinct live query formulations, followed by direct inspection of canonical GitHub pages and additional primary sources for every retained repository. Search angles included distributed SQL and NewSQL; Percolator and transactional key-value stores; PostgreSQL extensions and MySQL transaction middleware; NDB kernel internals; Erlang/CRDT databases; document and graph transactions; SQLite/Raft replication; heterogeneous-storage transaction layers; Chinese-language SequoiaDB and Dingo documentation; transactional data platforms; FoundationDB data-model layers; and deterministic and geo-distributed research systems. Later searches increasingly returned already examined projects; Calvin and SLOG were retained because they added distinct, well-documented architectures. The final list extends the rough 15–25 guide for that reason.

Selection deliberately preserves different guarantees. Antidote's causal/CRDT model, Citus's lack of full distributed snapshots, Vitess's fractured-read possibility, and snapshot-isolated designs are not collapsed into one “fully ACID” label. Replicated SQLite, Comdb2, and Mnesia also address different distribution patterns from a sharded SQL engine. TiDB and TiKV are counted separately because they expose substantially different, independently useful layers; subsystems inside MySQL, OTP, and YTsaurus are counted only once per repository.

Important exclusions and limits:

- **ArangoDB** was investigated, but its [documented cluster ACID restrictions](https://docs.arango.ai/arangodb/3.12/features/list/) center on single-shard and OneShard configurations. The final selection prioritizes richer distributed coordination examples; this is a scope choice, not a claim that ArangoDB lacks transactions.
- An attempted official VoltDB repository lookup did not yield an inspectable current public repository. H-Store is included under its own historical identity, not presented as current VoltDB source. Proprietary services without a verified public engine repository were not substituted with SDKs.
- Bare consensus libraries, saga frameworks, connector-only projects, tutorials, generated wrappers, and curated link lists were excluded. Repository popularity was not used as evidence for the criteria.
- Some rendered documentation and GitHub source requests failed or timed out. Successful primary alternatives included PingCAP's documentation repository and Citus's raw developer document. SequoiaDB's accessible architecture source was an older official Chinese edition; OceanBase and several other entries also cite explicitly versioned documentation. Documentation and a moving main branch may diverge.
- H-Store's archive status, Calvin's historical research role, SLOG's experimental rewrite, and Kronotop's developer-preview status are explicit. No general active-maintenance claim is made for the remaining repositories merely because their pages were reachable.
- This was read-only source and documentation research. No candidate code was cloned, installed, built, benchmarked, or executed. Criterion assessments are therefore evidence-based study recommendations, not independent proofs of correctness, performance, security, or operational readiness.
