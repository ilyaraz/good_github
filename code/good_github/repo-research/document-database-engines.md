# Document database engines

Research date: 2026-10-09.

This selection covers 24 substantive implementations that store and query documents: JSON/BSON servers, embedded engines, browser and peer-to-peer databases, and native XML or temporal tree stores. Multi-model projects are included where the document subsystem is a first-class implementation. Engines built over another storage system qualify when they implement substantial document semantics, indexing, query execution, or replication themselves. This is a guide for studying engineering decisions, not a production-readiness ranking or a claim that every component is exemplary.

Criteria used below:

- **C1 — Correctness:** difficult invariants, concurrency, data semantics, adversarial inputs, or failure recovery.
- **C2 — Abstractions:** substantial reusable interfaces and mechanisms supporting multiple use cases.
- **C3 — Performance:** concrete resource constraints addressed through an understandable architecture.
- **C4 — Evolution:** years of development with compatibility, testing, or complexity-management evidence.

## Server and multi-model document engines

### 1. [mongodb/mongo](https://github.com/mongodb/mongo)

**C++; BSON document server and sharding router.** Study how a large document engine separates collections, indexes, storage transactions, and replication recovery. The particularly useful entry point is its unusually detailed storage contract.

- **C1:** `RecoveryUnit` defines snapshot visibility, atomicity across documents and their indexes, write-conflict retries, and the distinction between a committed and durable transaction. Startup recovery also reconciles the database catalog with storage-engine objects. These are explicit invariants rather than an undifferentiated “ACID” claim. [Storage Engine API](https://github.com/mongodb/mongo/blob/master/src/mongo/db/storage/README.md).
- **C2:** `RecordStore`, `SortedDataInterface`, `KVEngine`, and `RecoveryUnit` isolate reusable storage responsibilities from document operations. The same document/index consistency contract must survive different implementations. [Storage Engine API](https://github.com/mongodb/mongo/blob/master/src/mongo/db/storage/README.md).

### 2. [apache/couchdb](https://github.com/apache/couchdb)

**Erlang, with JavaScript query components; replicated JSON document server.** A strong study of designing persistence, derived views, and disconnected replication around the same revision model.

- **C1:** Optimistic document updates reject stale revisions; replicated conflicts retain losing revisions while deterministically selecting a winner. Append-only index updates and the documented commit sequence address interrupted writes. [Technical overview](https://docs.couchdb.org/en/stable/intro/overview.html).
- **C3:** Sequence IDs drive incremental replication and view maintenance. View construction processes changed documents in storage order, and online compaction reclaims space while readers continue using the old file. These mechanisms expose the I/O tradeoffs directly. [Technical overview](https://docs.couchdb.org/en/stable/intro/overview.html).

### 3. [ravendb/ravendb](https://github.com/ravendb/ravendb)

**C#; document server with the in-repository Voron storage engine.** Study the interaction between a managed runtime, memory-mapped storage, and a deliberately restricted write-concurrency model.

- **C1:** Voron combines a write-ahead journal with MVCC scratch files and page translation tables. Journals provide recovery, while readers retain their transaction snapshots. [Voron design](https://docs.ravendb.net/7.1/server/storage/storage-engine/).
- **C3:** A single write transaction simplifies storage concurrency; RavenDB adds transaction merging above it to handle load. Variable-size and fixed-size B+trees, raw-data sections, and tables serve different access patterns. Start with the design and then the [Voron source tree](https://github.com/ravendb/ravendb/tree/v7.1/src/Voron). That source link deliberately selects the documented 7.1 branch.

### 4. [rethinkdb/rethinkdb](https://github.com/rethinkdb/rethinkdb)

**C++; distributed JSON database with ReQL and changefeeds.** Useful for understanding how declarative cluster configuration becomes concrete shard and replica placement.

- **C2:** The clustering architecture separates distributed primitives, automatic planning of placement/split decisions, and the administrative interface. This allows the same machinery to support simple table configuration and explicit server-tag placement. [Architecture FAQ](https://rethinkdb.com/docs/architecture/).
- **C3:** Primary-key range sharding uses table statistics to choose split points and supports efficient range queries. The documentation explains the cost and control tradeoff: existing split points are not automatically adjusted as the key distribution changes. [Architecture FAQ](https://rethinkdb.com/docs/architecture/).

### 5. [arangodb/arangodb](https://github.com/arangodb/arangodb)

**C++ and JavaScript; document, graph, and key-value server.** Focus on document collections, AQL execution, and the transaction layer above RocksDB, rather than treating the graph API as the whole project.

- **C1:** Concurrent modifications of a document or unique-index entry can produce write conflicts. Collection declaration, lazy collection discovery, deadlock detection, and per-DB-server snapshots make the isolation boundary explicit; the documentation also distinguishes failed operations from automatic abortion of an entire stream transaction. [Locking and isolation](https://docs.arango.ai/arangodb/3.12/develop/transactions/locking-and-isolation/).
- **C2:** JSON documents, collection identity/revisions, and a shared query language support ordinary document work and graph traversal in one engine. This is a substantive model integration, with concurrency consequences when traversal discovers collections dynamically. [Document model](https://docs.arango.ai/arangodb/3.12/concepts/data-structure/documents/).

### 6. [orientechnologies/orientdb](https://github.com/orientechnologies/orientdb)

**Java; document/graph database with paginated local storage.** Study stable record identities and the boundary between logical records, physical pages, caching, and recovery.

- **C1:** The PLocal design separates record positions from physical locations, retains tombstones, checks page integrity, and logs changes before applying them. It explicitly discusses index recovery modes and durability tradeoffs. [Paginated local storage](https://orientdb.dev/docs/3.2.x/internals/Paginated-Local-Storage.html).
- **C3:** Separate read and write caches distinguish repeatedly accessed pages from short-lived pages and group dirty-page writes by disk position. The documented durable-page abstraction records changes while allowing low-level off-heap access. [Paginated local storage](https://orientdb.dev/docs/3.2.x/internals/Paginated-Local-Storage.html). Treat this as a versioned internals guide, not a promise that every default remains unchanged.

### 7. [documentdb/documentdb](https://github.com/documentdb/documentdb)

**C, SQL, and Rust components; PostgreSQL-based BSON document engine and MongoDB-protocol gateway.** This is a useful counterexample to engines that implement their own physical storage.

- **C2:** The repository separates BSON types/operators (`pg_documentdb_core`), document CRUD/query APIs (`pg_documentdb`), and protocol translation (`pg_documentdb_gw`). This keeps document semantics reusable through PostgreSQL as well as the gateway. [Repository component overview](https://github.com/documentdb/documentdb).
- **C1 / C3:** The development changelog documents concrete work on UTF-8 boundaries, collation, compound-index sort/group correctness, concurrent RUM-tree splits during vacuum, and planner selectivity for `$lookup`. These show semantic compatibility and query/storage optimization interacting. Several entries are explicitly **unreleased**; they are implementation-study evidence, not released-feature promises. [Changelog](https://github.com/documentdb/documentdb/blob/main/CHANGELOG.md).

### 8. [SequoiaDB/SequoiaDB](https://github.com/SequoiaDB/SequoiaDB)

**C++; distributed document database with BSON and an extensive operational toolset.** Adds a substantial Chinese database community and a different server decomposition to the selection.

- **C1:** The transaction subsystem includes an explicit dependency graph for deadlock detection. Its implementation traverses waiter/holder relationships and detects cycles, providing a concrete path from locking policy to graph algorithms. [Deadlock detector](https://github.com/SequoiaDB/SequoiaDB/blob/master/SequoiaDB/engine/dps/dpsDeadlockDetector.cpp).
- **C2:** The source separates coordination, catalog management, data storage, indexes, query optimization, and transaction/log processing. The repository also exposes cluster management, inspection, import/export, and restore tools, making it useful for studying an engine and its operational interfaces together. [Engine tree](https://github.com/SequoiaDB/SequoiaDB/tree/master/SequoiaDB/engine). Some top-level build guidance names old tool versions; it is not used here as maintenance evidence.

### 9. [surrealdb/surrealdb](https://github.com/surrealdb/surrealdb)

**Rust; document/graph engine usable as a server or embedded library.** Focus on the document processor and query layer above transactional key-value backends.

- **C1:** The documented transaction model uses snapshot isolation and commit-time conflict detection. Document changes, graph-edge records, and index updates share a transaction boundary, so model integration creates real consistency obligations. [Architecture](https://surrealdb.com/docs/learn/data-models/architecture).
- **C2:** A key/range transaction interface separates storage from parsing, execution, permissions, and document processing. Different storage backends and deployment forms reuse that query layer. [Architecture](https://surrealdb.com/docs/learn/data-models/architecture). The documentation includes commercial deployment capabilities; this entry does not imply that every described distributed backend is contained in the public repository.

### 10. [terminusdb/terminusdb](https://github.com/terminusdb/terminusdb)

**Prolog and Rust; versioned JSON/JSON-LD document graph database.** Study document semantics implemented over graph storage, with a logic engine and revision control as core features.

- **C1:** Immutable delta layers let readers retain an existing branch state while writers build new layers and publish a new head. Concurrent writes to one branch require optimistic conflict handling; separate branch heads isolate independent histories. [Immutability and concurrency](https://terminusdb.org/docs/immutability-and-concurrency/).
- **C2:** The architecture assigns storage and document/GraphQL facilities to Rust and logic queries, schema validation, revision operations, and replication to Prolog. The same representation supports documents, graph reasoning, and branch/diff workflows. [Developer architecture overview](https://github.com/terminusdb/terminusdb/blob/main/GETTING_STARTED.md).

## Embedded and mobile engines

### 11. [couchbase/couchbase-lite-core](https://github.com/couchbase/couchbase-lite-core)

**C++; shared document engine beneath Couchbase Lite platform bindings.** Study actual CRUD, query, revision, and synchronization machinery rather than a language SDK.

- **C1:** Replication uses actors to serialize each component's work while coordinating network I/O and database access. A reconnecting API object creates fresh internal replicators instead of trying to reset all connection state in place. [Replicator overview](https://github.com/couchbase/couchbase-lite-core/blob/master/docs/overview/Replicator.md).
- **C2 / C3:** `DataFile`/`KeyStore` abstract storage; collection notifications are coalesced, and replication uses connection pooling and batching. The class map explains how these pieces serve multiple platform bindings. [Class overview](https://github.com/couchbase/couchbase-lite-core/blob/master/docs/overview/Classes.md).

The repository warns that direct LiteCore use is unsupported and its API unstable; enterprise components are partly private. The overview documents also identify their historical context.

### 12. [litedb-org/LiteDB](https://github.com/litedb-org/LiteDB)

**C#; embedded BSON document database for .NET.** A comparatively approachable engine for studying schema-free indexing and typed application APIs.

- **C1:** Mixed BSON values need a defined comparison order. The index documentation specifies numeric normalization, array/document comparison, multikey behavior, and uniqueness of index names, exposing semantics that affect both query results and index validity. [Indexes](https://www.litedb.org/docs/indexes/).
- **C3:** Skip-list indexes avoid deserializing every document during a full scan. Expressions and array values can generate index keys, but a query uses only one index; remaining predicates still require filtering. These limitations make planner and representation tradeoffs visible. [Indexes](https://www.litedb.org/docs/indexes/).

### 13. [nitrite/nitrite-java](https://github.com/nitrite/nitrite-java)

**Java with Kotlin support; embedded document collections and object repositories.** Study how a common document layer works across storage modules and transaction-scoped collection wrappers.

- **C1:** `NitriteTransaction` models active, partially committed, failed, committed, and aborted states. Commit processes collection journals under write locks, records undo commands, and rollback executes undo entries in reverse order. This is useful failure-path code to read critically; it is not evidence of unrestricted distributed ACID guarantees. [Transaction implementation](https://github.com/nitrite/nitrite-java/blob/main/nitrite/src/main/java/org/dizitart/no2/transaction/NitriteTransaction.java).
- **C2:** In-memory storage, MVStore, and RocksDB modules sit beneath collections and mapped object repositories, with a documented extension point for custom stores. [Storage modules](https://nitrite.dizitart.com/java-sdk/modules/store-modules/index.html).

### 14. [Softmotions/ejdb](https://github.com/Softmotions/ejdb)

**C11; embedded JSON engine with JQL and optional HTTP/WebSocket interfaces.** Study a compact query engine built over IOWOW, including the separation of JSON values, query objects, and execution callbacks.

- **C2:** The C interface separates database operations, JSON management, and query construction. Reusable query objects accept bound parameters and visitor-based result processing. [C API guide](https://github.com/Softmotions/ejdb/blob/master/CAPI.md).
- **C3:** Typed path indexes, heuristic index selection, explain output, and index-backed ordering expose the query planner's decisions. The documentation states limitations such as one selected index and unsupported top-level predicate shapes. [JQL indexes and performance](https://github.com/Softmotions/ejdb#jql-indexes-and-performance-tips).

The README says the issue tracker is disabled while contributions through pull requests are accepted; no stronger support commitment is inferred.

### 15. [symisc/unqlite](https://github.com/symisc/unqlite)

**C; embedded transactional key-value engine with a Jx9-powered document layer.** The document subsystem is the reason for inclusion; the raw key-value API alone would belong elsewhere.

- **C1:** The pager owns page caching, file locking, rollback, and atomic commit. Storage implementations request pages and report modifications instead of independently implementing those failure-sensitive operations. [Architecture](https://unqlite.symisc.net/arch.html).
- **C2:** The document/Jx9 layer, interchangeable key-value engines, pager, and virtual filesystem form explicit boundaries. This supports scripting, raw records, persistent or in-memory stores, and operating-system portability in one embedded library. [Architecture](https://unqlite.symisc.net/arch.html). The split `src` tree is preferable to the amalgamation for extended reading.

### 16. [PoloDB/PoloDB](https://github.com/PoloDB/PoloDB)

**Rust; embedded BSON engine with a MongoDB-like API and partial wire-protocol server.** The canonical repository redirects from the older `vincentdchan/PoloDB` URL.

- **C1:** Recent changelog entries tackle duplicate `_id` rejection, unique-index-preserving updates, upsert conditions, dotted update paths, and scalar/array/regex matching. These are specific examples of the difficulty of reproducing document-query semantics. [Changelog](https://github.com/PoloDB/PoloDB/blob/master/CHANGELOG.md).
- **C2:** Typed Serde collections, explicit and automatic transactions, and the standalone server share the Rust core above RocksDB. This is a useful embedded/server reuse boundary. [Current README](https://github.com/PoloDB/PoloDB/blob/master/README.md).

The current README explicitly limits MongoDB compatibility and identifies evolving features. Version 5 uses a RocksDB directory, so older single-file descriptions should not be carried forward.

### 17. [khonsulabs/bonsaidb](https://github.com/khonsulabs/bonsaidb)

**Rust; typed document database with embedded and networked access.** Particularly useful for its explicit architecture guide and persistent map/reduce-view bookkeeping.

- **C2:** Common connection, schema, document, key, and transaction traits live in `bonsaidb-core`; local storage, server, and client crates build outward from those interfaces. [Architecture](https://github.com/khonsulabs/bonsaidb/blob/main/ARCHITECTURE.md).
- **C1 / C3:** View maintenance tracks invalidated document IDs and a reverse document-to-emitted-keys map. That allows incremental reindexing while removing stale view entries after a document's emitted keys change. Collections and view structures sit over Nebari's transactional trees. [Architecture](https://github.com/khonsulabs/bonsaidb/blob/main/ARCHITECTURE.md).

The README labels the project **alpha** and discloses an earlier benchmarking error and transactional-write performance problem. Inclusion is for study, not a maturity endorsement or an assertion of current development cadence.

## JavaScript, local-first, and peer-to-peer engines

### 18. [apache/pouchdb](https://github.com/apache/pouchdb)

**JavaScript; local document database implementing CouchDB replication semantics.** The former `pouchdb/pouchdb` URL now redirects here. Study what must remain consistent when the same document API runs locally and synchronizes across disconnected peers.

- **C1:** Immediate stale-revision conflicts and eventual replication conflicts are separate cases. A deterministic winning revision does not erase the competing revisions, which remain available for application resolution. [Conflict guide](https://pouchdb.com/guides/conflicts.html).
- **C2:** CouchDB-compatible document/revision behavior is reused by a portable local database and its synchronization interface, letting offline and networked applications share an API model. The conflict guide explains the shared replication algorithm rather than merely claiming protocol resemblance. [Repository](https://github.com/apache/pouchdb) and [conflict guide](https://pouchdb.com/guides/conflicts.html).

### 19. [pubkey/rxdb](https://github.com/pubkey/rxdb)

**TypeScript; reactive local document database with storage and replication plugins.** Retained for its substantive synchronization/query layer; its persistence backends are separate mechanisms.

- **C1:** Push requests carry both the assumed server state and new local state, making conflicting updates explicit. Deterministic checkpoint ordering, deletion tombstones, and resynchronization after missed events are documented protocol requirements. [Replication engine](https://rxdb.info/replication.html).
- **C2 / C3:** A common pull/push/stream contract supports different backends. Batched transfers and switching between checkpoint catch-up and live event observation address synchronization cost without changing the document model. [Replication engine](https://rxdb.info/replication.html). Commercial plugins are outside the implied scope of the public repository.

### 20. [techfort/LokiJS](https://github.com/techfort/LokiJS)

**JavaScript; in-memory document database with persistence adapters.** Useful for studying indexing and live views without immediately entering a server or disk-page architecture.

- **C2:** Collections, chained result sets, named transforms, map/reduce functions, dynamic views, and persistence adapters provide reusable mechanisms beyond a simple JSON-file wrapper. [Wiki overview and examples](https://github.com/techfort/LokiJS/wiki).
- **C3:** Binary/unique indexes and maintained dynamic views reduce repeated scans of in-memory objects. The update API's responsibility for synchronizing indexes is an instructive consequence of exposing JavaScript objects directly. [Repository overview](https://github.com/techfort/LokiJS) and [wiki](https://github.com/techfort/LokiJS/wiki).

The wiki documents older API context. Its rollback option should not be confused with crash-durable multi-process transactions; no current-maintenance or published-throughput claim is made here.

### 21. [orbitdb/orbitdb](https://github.com/orbitdb/orbitdb)

**JavaScript; peer-to-peer database framework, specifically its documents store.** Study a document view reconstructed from a cryptographically verifiable operation log rather than from a central server's mutable records.

- **C1:** The shared operation log supplies Merkle-CRDT replication semantics. The document iterator must suppress superseded values and honor deletion operations when reconstructing visible state. [Repository architecture](https://github.com/orbitdb/orbitdb) and [documents implementation](https://github.com/orbitdb/orbitdb/blob/main/src/databases/documents.js).
- **C2:** Documents, events, and key-value models share the database/log machinery, while the documents layer supplies configurable identity fields, put/delete operations, iteration, and predicates. [Documents implementation](https://github.com/orbitdb/orbitdb/blob/main/src/databases/documents.js).

The inspected document implementation scans log-derived state for lookups and predicates; this entry is not a claim of sophisticated secondary-index planning.

## Native XML and temporal tree engines

### 22. [BaseXdb/basex](https://github.com/BaseXdb/basex)

**Java; native XML database and XQuery processor.** A valuable comparison with JSON engines because its optimizer understands document paths and node structure.

- **C1:** Pending update lists make a query's update operations an atomic unit at the query level. Preclaiming two-phase locking supports concurrent readers and serialized writes, with compiler analysis determining which databases need locks. The documentation explicitly warns about cross-JVM locking and possible inconsistency after a power failure. [Transaction management](https://docs.basex.org/main/Transaction_Management).
- **C3:** Name and path indexes support query elimination, descendant-to-child rewrites, and precomputed statistics; value indexes support content access. Updates can invalidate statistics, making the boundary between data correctness and optimizer metadata visible. [Indexes](https://docs.basex.org/main/Indexes).

### 23. [eXist-db/exist](https://github.com/eXist-db/exist)

**Java; native XML document database and application platform.** Study node-oriented persistence, XML indexing, pooled database access, and an explicit recovery implementation.

- **C1:** Recovery identifies the last valid checkpoint, replays journal entries, tracks transaction starts/commits/aborts, and reverse-scans to undo unfinished transactions. It aborts recovery on problematic entries rather than proceeding blindly. [RecoveryManager](https://github.com/eXist-db/exist/blob/develop/exist-core/src/main/java/org/exist/storage/recovery/RecoveryManager.java).
- **C2:** `DBBroker` defines backend operations for document storage/removal and index access while exposing transaction, lock, subject, and serializer relationships. This is a reusable interface between the XML/application layer and storage implementations. [DBBroker](https://github.com/eXist-db/exist/blob/develop/exist-core/src/main/java/org/exist/storage/DBBroker.java).

### 24. [sirixdb/sirix](https://github.com/sirixdb/sirix)

**Java with Kotlin components; versioned JSON/XML node store.** Included as a document engine whose physical unit is a tree node, enabling fine-grained history and subtree access.

- **C1:** Read transactions bind to immutable revisions; one write transaction per resource builds a new revision. Copy-on-write pages and transaction-local modifications must preserve old reader snapshots and expose a revision only after its pages are written. [Architecture specification](https://github.com/sirixdb/sirix/blob/main/docs/ARCHITECTURE.md).
- **C3:** Structural sharing and bounded page-fragment reconstruction address the storage/read-cost tension of retaining history. Node navigation and secondary indexes permit partial materialization instead of loading an entire resource. [Architecture specification](https://github.com/sirixdb/sirix/blob/main/docs/ARCHITECTURE.md).

The repository contains both implementation documentation and design plans. The selection relies on documented architectural mechanisms, not the document's broad comparative speed claims or an independent verification of its formal-proof claims.

## Search coverage and limitations

Discovery used substantially more than six distinct query formulations: established document-server architecture; distributed BSON/JSON engines; embedded C/C#/Java implementations; Rust and Go document engines; browser/offline replication; native XML engines; PostgreSQL-backed document implementations; and immutable document/graph databases. Follow-up searches targeted storage contracts, transactions, indexing, recovery, and replication. Candidate discovery continued into smaller implementations and alternative communities; later queries increasingly returned already-covered engines, wrappers, very new projects, or adjacent database categories.

Every retained repository's canonical page was opened, and at least one additional primary document, source file, or source-tree endpoint was read. GitHub's public API and raw source endpoints supplied evidence when rendered source pages failed. The report preserves the PoloDB and PouchDB owner changes and counts each monorepo once. Versioned architecture pages and older overviews are identified where relevant. No repository is described as actively maintained solely because its README says so.

The boundary excludes drivers, ODMs, tutorials, lists, hosted services without a substantive public engine, and raw key-value engines without their own document layer. MongoDB compatibility gateways alone are not counted separately from substantive engines. MongoDB-derived forks are not added simply to increase the count. SQL systems with JSON columns and search engines that happen to index documents are outside the primary scope. The Go-oriented search found candidates such as tiedot and newer engines, but this selection prioritizes the better-substantiated implementations above; it is not exhaustive for that language. Sedna was discovered in the XML search, but was not retained without completing equivalent canonical GitHub/source verification.

This was read-only research: no candidate was cloned, built, benchmarked, or exercised under failure injection. Performance judgments concern observable mechanisms, not measured rankings. The C1–C4 assignments are grounded engineering assessments, not audits of correctness, license suitability, support availability, or production reliability. Public code may cover only part of a commercial product, and documentation can describe newer or older behavior than a particular release.
