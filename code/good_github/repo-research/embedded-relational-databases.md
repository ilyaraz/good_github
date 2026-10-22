# Embedded relational databases

Research date: **2026-10-09**. This report selects **22 GitHub repositories** for studying databases that execute relational queries inside an application process. It covers transactional SQL, embedded analytics, browser runtimes, relational Datalog, and a small-device relational engine. An optional server mode does not disqualify an otherwise embeddable system. Datalog entries are included for their tuple/relation semantics and joins, rather than merely because their data can represent a graph.

This is a source-reading guide, not a production-readiness ranking. In particular, a database framework with a supplied in-memory backend, a substantive embedding layer, and a complete durable engine offer different lessons. Those distinctions are stated below. Each selection has at least two evidence-grounded criteria; the criteria describe worthwhile engineering problems and abstractions, not a claim that every implementation detail is exemplary.

## Criteria

- **C1 — Correctness:** difficult invariants, concurrency, numerical or query semantics, adversarial inputs, or recovery/failure behavior.
- **C2 — Abstractions:** substantial reusable interfaces or structures supporting multiple workloads or integrations.
- **C3 — Performance and structure:** concrete resource or throughput constraints addressed through an understandable architecture.
- **C4 — Evolution:** years of development accompanied by compatibility, testing, or explicit complexity management.

## Transactional engines and established implementations

### 1. [sqlite/sqlite](https://github.com/sqlite/sqlite)

**C; embedded transactional SQL engine. Official Git mirror:** the authoritative development repository uses Fossil. The repository explains that its source history extends back to May 2000 and that some testing and most documentation live separately.

Study the boundaries between SQL compilation, the VDBE bytecode interpreter, B-trees, page caching, and the operating-system interface. They expose the engineering beneath a small public API without pretending that the optimized implementation is simple.

- **C1:** the pager owns rollback, atomic commit, and locking; WAL behavior is separated from the B-tree layer. The testing program injects allocation failures, I/O failures, malformed databases, and simulated crashes, including compound failures. [Architecture](https://sqlite.org/arch.html), [testing](https://sqlite.org/testing.html).
- **C2:** prepared statements, function callbacks, and the VFS interface isolate execution, extension, and platform concerns. The architecture document maps these abstractions to source files.
- **C4:** the long source history is accompanied by retained regression cases and multiple independently developed testing approaches. The testing document distinguishes public tests from proprietary harnesses, so the GitHub mirror should not be mistaken for the entire verification infrastructure.

### 2. [h2database/h2database](https://github.com/h2database/h2database)

**Java; embeddable RDBMS with an independently reusable storage subsystem.** H2 is especially useful for following the relationship between a JDBC/SQL database and its lower-level MVStore, rather than studying either in isolation.

- **C1:** MVStore maintains copy-on-write versions while its transaction layer manages concurrent transactions, savepoints, and two-phase commit. Snapshot retention, chunk reuse, and background persistence create concrete consistency and lifecycle problems. [MVStore documentation](https://www.h2database.com/html/mvstore.html).
- **C2:** maps, serializers, data types, map implementations, storage targets, and filesystems have extension points. The same subsystem supports ordinary B-tree maps, spatial R-tree maps, BLOB handling, and SQL storage.
- **C3:** counted B-trees support indexed positional access, a page-level LIRS cache addresses scans, and buffered changes become sequential chunk writes. The documentation discusses memory, caching, compaction, and concurrency alongside these mechanisms rather than presenting performance as a single benchmark number.

### 3. [apache/derby](https://github.com/apache/derby)

**Java; embedded JDBC relational engine. Historical, official Apache mirror.** Derby was retired on **2025-10-10**: its project states that development, bug fixes, and further releases have ended. A later repository push or an unset GitHub archive flag does not override that retirement notice. [Project status](https://db.apache.org/derby/).

Study a mature modular database through its JDBC, SQL, store, and service layers. Its architecture paper is explicitly historical, dating to 2004, and is best read as an explanation of the design lineage.

- **C1:** the access store handles isolation and locking policies, while the raw store owns pages, transaction logging, and transaction management. This split makes the responsibilities behind transactional behavior unusually explicit. [Engine architecture](https://db.apache.org/derby/papers/derby_arch.html).
- **C2:** modules expose Java interfaces; a monitor chooses implementations for their environment. A shared cache abstraction serves pages, compiled plans, file descriptors, and metadata, demonstrating reuse inside a complex engine.
- **C4:** the official project history spans releases across many Java generations, while the architecture explains how implementation selection and interface boundaries managed that variation. Retain it as a study target, not as an actively supported deployment recommendation.

### 4. [FirebirdSQL/firebird](https://github.com/FirebirdSQL/firebird)

**C/C++; full relational engine with an embedded provider as well as server deployments.** The relevant subsystem is the database engine and its provider boundary, not merely the client libraries or the embedded-SQL preprocessor. Firebird's quick-start guide identifies the engine provider that opens database files directly inside the application. [Deployment and provider guide](https://firebirdsql.org/file/documentation/html/en/firebirddocs/qsg5/firebird-5-quickstartguide.html).

- **C1:** snapshot isolation, read-committed variants, update conflicts, wait/no-wait behavior, and lock timeouts interact in explicitly documented ways. Sharing a snapshot between attachments adds another useful consistency case. [Transaction reference](https://firebirdsql.org/file/documentation/chunk/en/refdocs/fblangref50/fblangref50-transacs.html).
- **C2:** provider selection and per-database configuration allow embedded and networked access to reuse the relational engine. This is a substantial example of embedding a system that also has operationally different server modes.
- **C3:** the guide contrasts per-connection page caches with a shared cache and explains which modes permit other processes to open the same database. Study the resource model together with the concurrency constraints.

## SQLite extensions, alternative implementation, and replication

### 5. [sqlcipher/sqlcipher](https://github.com/sqlcipher/sqlcipher)

**C; a substantive SQLite fork adding encrypted storage.** This is included separately because its pager integration, cryptographic provider boundary, and upstream-merge obligations are distinct engineering work, not a language binding.

- **C1:** encryption operates page by page; authentication covers ciphertext and initialization vectors; keys have derivation and separation rules; and journal/WAL handling must preserve the security boundary during transactions. The design also addresses temporary storage and memory cleanup. [SQLCipher design](https://www.zetetic.net/sqlcipher/design/).
- **C2:** applications retain SQLite's SQL/API model while cryptographic implementations can vary by platform. The same document explains why an ordinary loadable extension cannot supply the required internal access. The separate source tree deliberately limits upstream modifications, but SQLite merges still require inspection and testing because the codec uses internal APIs. This makes the abstraction boundary a concrete compatibility-management problem.

### 6. [tursodatabase/libsql](https://github.com/tursodatabase/libsql)

**C and Rust; SQLite fork with embedded replicas, remote access, and additional engine interfaces.** The repository explicitly distinguishes libSQL from the separate Rust implementation, Turso. It describes libSQL as maintained while directing new feature development toward Turso; it also notes the inherited single-writer model.

- **C1:** exposing an alternative WAL implementation introduces a precise ownership problem: methods are globally registered and must remain stateless, while per-connection state is passed separately. Study this alongside the consistency boundary of embedded replicas. [Engine extensions and virtual WAL contract](https://github.com/tursodatabase/libsql/blob/main/libsql-sqlite3/doc/libsql_extensions.md).
- **C2:** virtual WAL methods extend the familiar VFS style of customization to logging. The repository provides both a libSQL API and a compatibility-oriented SQLite C API, supporting applications that need different levels of access to the extensions.

Its independent value here is the WAL/replication integration and compatibility work. It is not counted as a wholly independent implementation of SQLite's inherited parser, VM, or B-tree algorithms.

### 7. [tursodatabase/turso](https://github.com/tursodatabase/turso)

**Rust; independent in-process SQL engine targeting SQLite compatibility.** This is a rewrite, not another SQLite fork. Its bytecode VM and concurrent-write support make it useful to compare with SQLite and libSQL. Compatibility is feature-specific and should be read from the project's matrix rather than inferred from the project description. [Compatibility reference](https://github.com/tursodatabase/turso/blob/main/COMPAT.md).

- **C1:** the deterministic concurrent simulator exercises overlapping writes, old reader snapshots, savepoints, checkpoints, cancellation, recovery copies, and index consistency. Its full-text profiles compare indexed results with table scans in the same view. [Concurrent simulator](https://github.com/tursodatabase/turso/blob/main/testing/concurrent-simulator/README.md).
- **C2:** the engine separates SQL frontends from a shared VM and offers multiple language integrations. The compatibility document separates SQL syntax, C APIs, opcodes, and journaling behavior, making the integration surface reviewable.
- **C3:** MVCC and asynchronous I/O address write concurrency and blocking costs. The simulator documentation is also candid about what its recovery copies do not model, including partially written pages and power-loss write reordering.

### 8. [canonical/dqlite](https://github.com/canonical/dqlite)

**C; embeddable replicated SQL engine built around SQLite.** Dqlite runs a server thread within an application and connects application nodes into a cluster. Its contribution is substantial replication and I/O machinery around SQLite, rather than an independent SQL compiler.

- **C1:** modified pages are withheld from the visible WAL image while the corresponding Raft entry is replicated. The write lock remains effectively held until quorum commit, preventing readers and later writers from observing an uncommitted distributed state. [Replication design](https://canonical.com/dqlite/docs/explanation/replication).
- **C2:** a custom VFS, gateway, replicated state machine, and wire protocol separate database execution from consensus and application communication.
- **C3:** an asynchronous libuv event loop and in-memory SQLite file images avoid blocking the server thread and avoid persisting the same change independently in both SQLite files and the Raft log. The design discusses checkpoints and leadership failures as part of that architecture.

This belongs at the distributed edge of the category: embedding does not mean that every query is a local, network-free operation.

## Embedded analytics

### 9. [duckdb/duckdb](https://github.com/duckdb/duckdb)

**C++; in-process analytical SQL database.** DuckDB is a particularly strong counterpoint to row-oriented transactional engines. Study how the engine turns a rich SQL query into a typed, optimized pipeline of columnar operations.

- **C2:** the parser, binder, logical planner, optimizer, physical planner, and execution engine have distinct intermediate representations. Binding resolves catalog names and types before later stages transform the plan. [Internals overview](https://duckdb.org/docs/current/internals/overview).
- **C3:** expression rewriting, filter pushdown, join-order optimization, common-subexpression extraction, and push-based vectorized execution reduce work at different stages. DataChunks provide the execution boundary between physical operators.
- **C1:** type resolution, aggregate/window extraction, and semantics-preserving plan rewrites are concrete correctness obligations across those representations. The value of the codebase is the interaction of these obligations with the performance architecture, not merely the presence of many optimizations.

The documentation is versioned; its current 1.5 documentation and the repository's development default branch need not describe identical release states.

### 10. [MonetDB/MonetDB](https://github.com/MonetDB/MonetDB)

**C; analytical database monorepo, specifically the MonetDBe subsystem. Official Mercurial mirror.** MonetDBe packages the SQL engine as a directly linked library. Count the repository once, rather than separately counting its server, embedded library, and language clients.

- **C2:** a small C API exposes the SQL engine while reusing the server implementation. Its documentation explicitly identifies avoiding separate code paths as a design objective. [MonetDBe introduction](https://github.com/MonetDB/MonetDB/blob/master/documentation/monetdbe/introduction.rst).
- **C3:** embedding eliminates the client/server exchange and intermediate serialization, while retaining the column-store and parallel execution machinery. The documentation discusses in-memory resource limits and persistent local storage as different operating modes.
- **C1:** the embedded API has storage-access and lifecycle restrictions; the introduction calls out exclusive persistent access and serving one database at a time. These are essential boundaries to study when converting a server into a library.

The checked introduction still contains alpha-era wording and prospective features. Treat it as architecture evidence, not a definitive statement of current release readiness or every supported combination.

### 11. [chdb-io/chdb](https://github.com/chdb-io/chdb)

**Primarily Python in this repository; in-process ClickHouse integration, DataStore query planning, and durability control.** The native engine is supplied through chdb-core; this repository should not be presented as the entire ClickHouse engine source. Its integration work is nevertheless much more substantial than a generated wrapper.

- **C2:** DataStore records a lazy operation chain, plans execution segments, and routes them to chDB or pandas. It gives two API styles a common execution model and documents compatibility boundaries. [DataStore architecture](https://github.com/chdb-io/chdb/blob/main/dev-docs/ARCHITECTURE.md).
- **C3:** SQL compilation and delayed materialization reduce intermediate DataFrames; segment and result caching support repeated exploratory work.
- **C1:** the Durable layer defines explicit flush/checkpoint boundaries, immutable recovery objects, conditional head updates, single-writer fencing, and an ambiguous-commit outcome. A successful local mutation is not automatically durable in object storage. [Durability design](https://github.com/chdb-io/chdb/blob/main/docs/durable/index.mdx).

Study the local engine/embedding/control-plane boundary, rather than assuming server-style durability or transaction guarantees from the ClickHouse name alone.

## Browser and JavaScript relational systems

### 12. [electric-sql/pglite](https://github.com/electric-sql/pglite)

**TypeScript plus PostgreSQL/WebAssembly integration; embeddable PostgreSQL.** PGlite adapts PostgreSQL's single-user mode to a JavaScript-accessible I/O pathway. Its own repository documents a single-user/connection limitation. This is a substantive runtime adaptation, not a new independent relational optimizer.

- **C1:** persistence adapters expose different durability boundaries. IndexedDB flushes changed files, while relaxed durability returns results before the asynchronous flush. These semantics matter when translating a synchronous native engine into a browser environment. [Filesystem design](https://pglite.dev/docs/filesystems).
- **C2:** one database interface supports memory, host filesystem, IndexedDB, and OPFS-backed operation across multiple JavaScript runtimes.
- **C3:** OPFS access-handle pooling bridges PostgreSQL's synchronous calls and the browser's asynchronous file-opening APIs without relying on Asyncify for every operation. Study its directory mapping and pool maintenance alongside the single-process execution constraint.

### 13. [AlaSQL/alasql](https://github.com/AlaSQL/alasql)

**JavaScript; in-process relational SQL and data transformation for browsers and Node.js.** Its distinctive lesson is query compilation in a dynamic language with many input/output adapters. SQL tables and queries over arrays coexist within the same library.

- **C2:** the query object and source adapters let relational operations work over tables, JavaScript objects, and external formats. The source tree separates these integrations from the core SELECT implementation. [Source layout](https://github.com/AlaSQL/alasql/tree/develop/src).
- **C3:** SELECT compilation is staged into FROM/JOIN, predicate handling, grouping, projection, ordering, and set operations; it specifically has a WHERE/JOIN optimization stage before execution. [SELECT compiler](https://github.com/AlaSQL/alasql/blob/develop/src/40select.js).
- **C1:** grouping, correlated subqueries, set operations, and JavaScript value behavior meet within this compilation path, making it a useful study of SQL semantics outside a conventional native engine.

This selection is for its relational compiler and integration abstractions. It does not assert that its persistence adapters provide SQLite-equivalent transactional guarantees.

### 14. [google/lovefield](https://github.com/google/lovefield)

**JavaScript; browser relational database. Archived on 2023-01-10.** Lovefield remains a useful historical example of a typed query-builder interface, browser storage, and explicit transaction scheduling.

- **C1:** transactions have documented states, scope acquisition, shared/reserved locks, commit and rollback paths, and an in-memory journal. The design explicitly assumes that the underlying datastore's final write is atomic. [Transaction design](https://github.com/google/lovefield/blob/master/docs/dd/05_transaction.md).
- **C2:** query builders, tasks, a runner, journals, and observer registration separate user-facing queries from scheduling and persistence. Observed SELECTs reuse transaction scope information to decide when to rerun.
- **C3:** the runner schedules compatible read scopes concurrently; transaction batching and observer priority have explicit performance consequences.

The [design-document index](https://github.com/google/lovefield/blob/master/docs/dd_index.md) links the surrounding schema, storage, query-engine, and index designs. These are design documents for an archived system, not a claim of current browser compatibility or support.

## Go, Rust, and resource-constrained alternatives

### 15. [dolthub/go-mysql-server](https://github.com/dolthub/go-mysql-server)

**Go; embeddable MySQL-compatible relational engine and storage interfaces.** Its included in-memory database makes it usable in-process, while durable storage is supplied by an implementation such as Dolt. The network server is an optional layer, not the whole project.

- **C2:** `Node`, `Expression`, catalog, row, and backend interfaces allow the query engine to operate over multiple storage implementations. The root engine coordinates these components independently of the wire server. [Architecture](https://github.com/dolthub/go-mysql-server/blob/main/ARCHITECTURE.md).
- **C1:** the analyzer applies ordered and sometimes repeated rules to resolve and transform plans. Its engine-test harness is reusable by backend implementers, so the same semantic expectations can be tested against the supplied memory store and other implementations.
- **C3:** analysis rules separate resolution from optimizations and make ordering dependencies visible, illustrating how a reusable engine manages complexity while improving plans.

Read this as an embedded relational-engine framework with a concrete memory backend, not as a complete durable database shipped by this repository alone.

### 16. [chaisql/chai](https://github.com/chaisql/chai)

**Go; embedded SQL database built on Pebble. Experimental:** its README says it is not production-ready and that joins and many advanced features are not yet implemented. Those omissions substantially limit its relational coverage.

- **C1:** transaction code coordinates session commit, writer exclusion, commit/rollback hooks, and publication of a cloned catalog. This is useful for studying how schema changes participate in a storage transaction rather than mutating shared metadata prematurely. [Transaction implementation](https://github.com/chaisql/chai/blob/main/internal/database/transaction.go).
- **C2:** the transaction object composes engine/session abstractions with a database catalog and a separate catalog writer, giving a relatively compact example of the boundary between SQL metadata and a key-value storage substrate.

The [concurrent transaction regression test](https://github.com/chaisql/chai/blob/main/internal/database/database_test.go) stages a second transaction while a first transaction finishes. Its focused source and test are more useful evidence than treating planned SQL features as implemented. GitHub metadata showed a January 2026 last push at research time; no stronger maintenance claim is made.

### 17. [stoolap/stoolap](https://github.com/stoolap/stoolap)

**Rust; embedded SQL engine combining transactional row storage with columnar persistent segments.** Treat it as a newer implementation to inspect critically, especially at the boundary between hot data, cold data, indexes, and transaction visibility.

- **C1:** its MVCC design uses immutable version chains, creation/deletion transaction IDs, monotonic begin/commit sequences, and optimistic conflict detection. The documentation distinguishes read-committed and snapshot visibility. [MVCC design](https://github.com/stoolap/stoolap/blob/main/docs/_docs/architecture/mvcc-implementation.md).
- **C3:** hot rows and sealed columnar volumes have different access paths: cold data uses zone maps, Bloom filters, dictionaries, and aggregate pushdown, while hot data has mutable indexes. Queries must merge these paths without exposing inconsistent versions. [Storage design](https://github.com/stoolap/stoolap/blob/main/docs/_docs/architecture/storage-engine.md).
- **C2:** the source separates transaction registry, version store, scanner, persistence, and WAL modules, providing identifiable places to trace these responsibilities.

The evidence establishes a substantial architecture to study; it is not an independent validation of the project's correctness or performance claims.

### 18. [ubco-db/EmbedDB](https://github.com/ubco-db/EmbedDB)

**C/C++; embedded-device and time-series research engine with relational operators.** Unlike most entries, this targets machines that may lack an operating system. Its relational query subsystem sits above a specialized key-value/time-series storage and indexing layer.

- **C2:** operators use schemas, record buffers, and an `init`/`next`/`close` lifecycle. Table scan, projection, selection, aggregation, and key equijoin can be composed, and users can supply custom operators. [Query interface](https://github.com/ubco-db/EmbedDB/blob/main/docs/advancedQueries.md).
- **C3:** explicit page/erase geometry, caller-configured buffers, learned indexing, and flash-oriented data indexing address constrained memory and storage. The query guide also describes adaptive sorting choices appropriate to those constraints.
- **C1:** even the small operator API has ownership and ordering invariants: schemas carry signedness and layout, projection indices must increase, and cleanup differs for chains with multiple inputs.

This is not a full general-purpose SQL server. The separate SQL converter supports only some query forms; the primary study target is the operator and storage implementation in this repository.

## Relational Datalog and databases as values

### 19. [cozodb/cozo](https://github.com/cozodb/cozo)

**Rust; embeddable transactional relational database queried with Datalog.** Cozo explicitly models data as relations even when queries involve graphs or vectors. Its layered design separates environment bindings, query execution, and storage backends.

- **C1:** rule safety and stratification constrain legal recursion, negation, and aggregation. Strongly connected components containing prohibited dependency edges are rejected before evaluation. [Query execution](https://docs.cozodb.org/en/latest/execution.html).
- **C2:** a storage trait supports different backends beneath one relational query layer; Rust users can supply another backend. The project README explains the memcomparable row/key representation and the wrapper boundary.
- **C3:** magic-set rewriting, semi-naïve evaluation, early filter placement, key-prefix scans, and streaming joins address recursive-query work and intermediate results.

Maintenance caveat: the repository was not archived, but GitHub's metadata reported its last push as **2024-12-04** when checked. It is retained for architecture, without implying ongoing upstream development. [Repository metadata](https://api.github.com/repos/cozodb/cozo).

### 20. [tonsky/datascript](https://github.com/tonsky/datascript)

**Clojure/ClojureScript; immutable embedded database and Datalog query engine, including JavaScript use.** DataScript treats the database as an application value and originally emphasizes ephemeral in-memory state. This changes the concurrency and lifecycle questions compared with a durable server.

- **C1:** transactions resolve temporary IDs and structured updates into datoms and a transaction report; immutable before/after values make the state transition explicit. The author's internals article explains uniqueness of facts and the relation-merging invariants of the query engine. [Internals walkthrough](https://tonsky.me/blog/datascript-internals/).
- **C2:** database search/index protocols, entity access, filtered databases, and a relational query engine compose over the same fact representation. Queries can operate over databases and collections.
- **C3:** differently ordered indexes support different access patterns; the walkthrough explains the motivation for persistent B-tree structures and hash joins.

The walkthrough describes an older version and includes historical module names. Use it for design rationale, then follow the current repository for implementation details; “persistent data structure” should not be confused with automatic durable disk storage.

### 21. [datalevin/datalevin](https://github.com/datalevin/datalevin)

**Clojure/Java with native LMDB-family storage; durable, embeddable Datalog database.** The former `juji-io` URL redirects to this canonical repository. It supports embedded library operation as well as server deployment; the embedded query/storage path is the relevant subject here.

- **C2:** relational Datalog is implemented over indexed facts while the same library exposes lower-level storage and other data access capabilities. The query engine is more than an API veneer over LMDB: it plans and compiles multi-pattern queries.
- **C3:** nested triple storage uses sorted duplicate values to avoid repeating index prefixes and to obtain counts useful for planning. Predicates become index ranges where valid; costed lookups choose between indexed probes and scans. [Query-engine design](https://github.com/datalevin/datalevin/blob/master/doc/query.md).
- **C1:** the same document states preconditions for rewrites and preserves multiplicity, bound-variable behavior, and later uses of eliminated variables. Conservative fallback is part of the design, making this a useful study of optimization correctness.

No comparative benchmark number from the project is treated here as an independently established result.

### 22. [replikativ/datahike](https://github.com/replikativ/datahike)

**Clojure/ClojureScript; durable Datalog database built around immutable snapshots.** The local file-backed library is the embedded case. Distributed readers, remote writers, browser storage, and native bindings extend the model; several non-JVM bindings are explicitly beta in the README.

- **C1:** commits write new copy-on-write index nodes and then publish a root. The ownership model distinguishes exclusive writers from shared writers with conditional/fenced publication; the documentation explains why an exclusive declaration is not itself enforced exclusivity. [Architecture and writer coordination](https://github.com/replikativ/datahike/blob/main/doc/distributed.md).
- **C2:** snapshots are queryable values, and storage backends are separated from the relational API. Local files and other storage implementations can support the same index/query model.
- **C3:** structural sharing lets readers reuse most existing index structure and read snapshots without coordinating every query with a writer. Study the dependency between this efficiency, root publication, and safe garbage collection rather than assuming immutability eliminates all coordination.

Datahike's distributed options do not change the category fit of its in-process, file-backed deployment.

## Search coverage, exclusions, and limitations

Discovery used more than fifteen distinct live search formulations, followed by repository, documentation, source, test, and GitHub API inspection. Search angles included Java embedded SQL; C/C++ transactional engines; SQLite forks and replicated libraries; in-process analytical column stores; browser and WebAssembly databases; pure-Go and Rust alternatives; Datalog and immutable database values; and microcontroller/flash-oriented relational engines. Follow-up searches checked official mirrors, migrations, archived projects, and less familiar implementations. Later broad searches increasingly returned already-covered families, small prototypes, wrappers, or graph/document systems; EmbedDB was a useful additional result from the constrained-device search.

Important boundaries and exclusions:

- **QL and Metakit:** QL's GitHub repository announces its move to `modernc.org/ql`; Metakit's project page announces a move to a personal Gitea server. Neither was retained without establishing a current official substantive GitHub mirror. [QL notice](https://github.com/cznic/ql), [Metakit notice](https://www.equi4.com/metakit.html).
- **HSQLDB:** a substantial category fit, but this search found the `ryenus/hsqldb` mirror without establishing project authorization of that GitHub mirror. It is omitted rather than mislabeling it as an official repository. This is a verification limitation, not a judgment about HyperSQL's engineering quality.
- **Key-value, object, and document stores:** RocksDB, LMDB, sled, redb, Badger, Realm, PoloDB, and similar systems were not counted merely because applications can build relational features above them. In contrast, EmbedDB has an inspected relational operator layer, and the selected Datalog engines implement relation queries themselves.
- **Wrappers, ORMs, and duplicate engines:** ordinary SQLite drivers, generated ports, ORM libraries, and separate language bindings are not additional databases here. PGlite, chDB, SQLCipher, libSQL, and dqlite are retained because the inspected runtime adaptation, compiler/control layer, cryptographic integration, or replication machinery is substantive; their inherited engines are clearly identified.
- **Server-only and tutorial projects:** a server speaking SQL, an embedded-SQL preprocessor, or a small “build a database” exercise is not sufficient. Several newly discovered Rust/Go/C# prototypes were not retained because this survey did not establish equally useful, verified architecture and source evidence beyond their feature claims.

All 22 canonical repository identities were checked by opening the repository or reading GitHub repository metadata. Every entry has an additional opened primary document, source file, or test beyond its root page. Public GitHub API/raw-source reads supplemented browser fetches that timed out or returned truncated navigation. No candidate code was executed and no benchmark was reproduced. Branch links are readable entry points, not immutable snapshots; newer repositories and default branches can change rapidly. Historical architecture documents and experimental features are called out where material.

The classifications and proposed study lessons are grounded engineering judgments from those sources. The report is deliberately broader than “SQLite alternatives” and deliberately narrower than all software that stores data inside an application.
