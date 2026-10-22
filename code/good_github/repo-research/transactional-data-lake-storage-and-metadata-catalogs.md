# Transactional data lake storage and metadata catalogs

Research date: **2026-10-09**.

This selection covers 24 repositories implementing transactional lake tables, independent native implementations of their protocols, commit catalogs and versioned object namespaces, table maintenance, and metadata discovery. The final subgroup concerns discovery and governance catalogs; those systems do not, merely by cataloging a dataset, become its transaction coordinator. The focus is on code an experienced engineer can study for concrete storage and metadata design decisions, rather than a product ranking.

Criteria used below:

- **C1 — Correctness:** difficult invariants, concurrency, failure recovery, semantic edge cases, or adversarial inputs.
- **C2 — Abstractions:** substantial reusable interfaces or models supporting multiple workloads, engines, storage systems, or metadata types.
- **C3 — Performance:** real resource or latency constraints addressed through understandable architecture.
- **C4 — Evolution:** evidence spanning years, together with compatibility, testing, or deliberate complexity management. Repository age alone does not qualify.

Every repository heading links to a verified canonical GitHub location. Linked specifications, implementation files, and architecture guides provide reading entry points and support the criteria. Criteria are judgments grounded in the cited material, not claims that every component is uniformly exemplary.

## Transactional table formats and storage implementations

### [apache/iceberg](https://github.com/apache/iceberg)

**Language/role:** Java reference implementation, format specifications, and engine integrations. Study how an immutable metadata hierarchy lets a table evolve independently of its physical files and query engine.

- **C1:** Commits atomically replace the current metadata pointer. Retry validation checks the operation's assumptions: a compaction cannot commit after another operation has removed one of its input files. Readers retain consistent snapshots without holding writer locks. The [reliability guide](https://iceberg.apache.org/docs/latest/reliability/) explains the distinction between retrying publication and revalidating the operation.
- **C2:** Field IDs, partition specifications, snapshots, manifests, and delete files form a reusable logical table model rather than a directory convention. The [table specification](https://iceberg.apache.org/spec/) is a useful map from engine-independent semantics to implementation responsibilities.
- **C3:** Reusing manifests across retries avoids repeating expensive preparation; manifest lists and partition summaries support pruning before opening data files. These mechanisms connect metadata layout directly to planning and commit costs in the same sources.

### [delta-io/delta](https://github.com/delta-io/delta)

**Language/role:** Scala and Java, with Python APIs; Delta transaction protocol, Spark integration, and Java Kernel in one monorepo. Study the boundary between durable log actions, protocol feature negotiation, and engine behavior.

- **C1:** The protocol defines snapshot reconstruction from file additions/removals, reader/writer feature requirements, and application transaction identifiers used for idempotent writes. These are precise obligations for independently implemented clients. Start with [PROTOCOL.md](https://github.com/delta-io/delta/blob/master/PROTOCOL.md).
- **C3:** Checkpoints and log-compaction files reduce the amount of history readers must replay; their format and reconstruction rules make the optimization inspectable rather than an opaque cache.
- **C4:** The [1.0.0 release, May 2021](https://github.com/delta-io/delta/releases/tag/v1.0.0), documents a stabilized custom LogStore API, public conflict exceptions, and schema-evolution fixes. The [4.0.0 release, June 2025](https://github.com/delta-io/delta/releases/tag/v4.0.0), adds explicit reader-version requirements, feature-removal compatibility mechanisms, and further invariant fixes. Together these show sustained compatibility work.

The 4.0 notes place Delta Standalone and its dependent Flink/Hive connectors in maintenance mode. They are not counted as separate current implementations here; Java Kernel is part of this same repository.

### [apache/hudi](https://github.com/apache/hudi)

**Language/role:** Java and Scala; mutable lake tables, incremental ingestion, and background table services. Particularly useful for studying interactions between ingestion, compaction, cleaning, and incremental readers.

- **C1:** File-level optimistic concurrency permits independent file changes while rejecting overlapping changes. Multiwriter cleaning requires a lazy failed-write policy and heartbeats so one writer does not remove another writer's unfinished work. Incremental consumption must also account for inflight commits, not just the largest visible timestamp.
- **C3:** Asynchronous table services separate maintenance from ingestion. The design narrows coordination to critical metadata operations instead of holding a table lock throughout file generation; deployment mode and writer configuration determine which combinations are supported.

The [concurrency-control guide](https://hudi.apache.org/docs/concurrency_control/) explains these protocols, lock-provider choices, and the differing assumptions of single-writer, optimistic, and nonblocking modes. This is a stronger reading target than treating all advertised concurrency modes as interchangeable.

### [apache/paimon](https://github.com/apache/paimon)

**Language/role:** Java; streaming lake storage with append and primary-key tables, including an LSM-based layout. Study why a successful snapshot-number retry does not necessarily make a stale compaction safe.

- **C1:** Publication races can retry against a later snapshot, whereas removing already-replaced input files is a semantic conflict. Primary-key LSM tables also reject overlapping key ranges within a partition, bucket, and level above level zero. The atomic-publication contract depends on the actual catalog/filesystem implementation; a shared lock is required where the storage primitive cannot provide it.
- **C3:** Dedicated compaction allows ingestion writers to avoid independently rewriting the same files. The architecture makes the tradeoff explicit: this reduces compaction contention but does not eliminate snapshot races or all incompatible writes.

The [concurrency-control design](https://paimon.apache.org/docs/master/concepts/concurrency-control/) gives the commit sequence, conflict classes, storage assumptions, and operational consequences. This link is to the development documentation; feature availability should be checked against a chosen release.

### [duckdb/ducklake](https://github.com/duckdb/ducklake)

**Language/role:** C++; DuckDB implementation of the DuckLake format, combining SQL metadata storage with lake data files. Study how a relational catalog can carry the commit serialization point.

- **C1:** Concurrent writers attempt to insert the next snapshot ID into a metadata table whose primary key permits only one winner. The loser examines recorded snapshot changes to distinguish a retryable publication conflict from a logical conflict involving schemas, tables, deletions, or compaction.
- **C3:** Compatible transactions retry their metadata work without rewriting the data files they already produced. The conflict model can allow deletions affecting disjoint files, avoiding unnecessary whole-table serialization.

The [conflict-resolution guide](https://ducklake.select/docs/stable/duckdb/advanced_features/conflict_resolution) names the metadata tables and walks through the protocol. This repository is a concrete implementation to compare with Iceberg's metadata-pointer publication and Delta's log-based approach, rather than a generic DuckDB query-engine entry.

### [lance-format/lance](https://github.com/lance-format/lance)

**Language/role:** Rust with Python interfaces; columnar storage and transactional versioning for multimodal datasets. Included for its table/manifest layer, distinct from the LanceDB database product.

- **C1:** Immutable version manifests are published using conditional creation or rename-if-absent. Serialized transaction descriptions let the implementation compare concurrent operations and distinguish a rebase from an operation that must be recomputed. Unknown future transaction operations must conservatively conflict, while optional inline transaction decoding must not make an otherwise readable manifest unreadable.
- **C3:** The second manifest naming scheme reverses the numeric version ordering so lexicographic object listing can discover the newest version efficiently. Persisting transaction descriptions also avoids discarding all preparation when compatible operations can rebase.

The [transaction specification](https://lance.org/format/table/transaction/) connects storage primitives, manifest naming, conflict examples, and external-manifest-store recovery. The canonical repository is now under `lance-format`; unresolved proposals are not treated as implemented capabilities.

### [lakesoul-io/LakeSoul](https://github.com/lakesoul-io/LakeSoul)

**Language/role:** Rust storage/I/O core with Java and Scala engine components; mutable lake tables coordinated through an external metadata database. Offers a useful alternative to metadata logs stored entirely in object storage.

- **C1:** The architecture places transactional metadata in PostgreSQL and describes a two-stage commit process for concurrent updates, including updates targeting the same partition. This makes the relationship between durable data files and catalog publication an explicit design problem.
- **C2:** A shared native Arrow-oriented I/O layer underlies integrations with Spark, Flink, and Python, rather than requiring each engine to own an unrelated storage implementation.
- **C3:** Primary-key updates, range/hash partitioning, delta files, and LSM-style merging are coordinated with indexed metadata lookup. These choices address frequent ingestion and mutable-table workloads without relying on repeated directory enumeration.

Start with the project's [architecture introduction](https://lakesoul-io.github.io/docs/intro). Its benchmark claims are not used here; the selection rests on the metadata/data split and reusable implementation layers.

## Independent native protocol libraries

These repositories implement meaningful protocol and storage behavior themselves. They are not counted merely for exposing generated bindings, and their supported feature sets should not be assumed identical to the Java/Scala implementations.

### [delta-io/delta-rs](https://github.com/delta-io/delta-rs)

**Language/role:** Rust with Python bindings; native Delta Lake reading, writing, and table operations. A useful study in bringing transactional lake operations into applications that do not embed Spark.

- **C1:** Writers can produce Parquet files before they validate and publish a log commit. A losing transaction may therefore leave unreferenced files, and safe publication depends on an atomic no-overwrite primitive. The implementation must distinguish data-file existence from committed visibility and preserve cleanup safety after conflicts.
- **C2:** The repository provides native Rust table/storage APIs and higher-level operations exposed to Python. The shared protocol implementation lets application workloads reuse transaction semantics independently of a JVM engine.

The versioned [ACID transaction guide](https://delta-io.github.io/delta-rs/1.5.1/how-delta-lake-works/delta-lake-acid-transactions/) walks through conflicting deletes, speculative files, and storage requirements. Read its guarantees as applying to that documented implementation/version, rather than extrapolating them to every Delta client or later protocol extension.

### [delta-io/delta-kernel-rs](https://github.com/delta-io/delta-kernel-rs)

**Language/role:** Rust and C ABI; a protocol kernel intended for integration into different query engines. Distinct from delta-rs's application-facing table-operation library.

- **C2:** An `Engine` interface delegates storage access, JSON/Parquet handling, and expression evaluation, while opaque `EngineData` keeps engine-native batches outside the kernel's concrete representation. A separate `Committer` boundary accommodates filesystem and catalog-mediated publication.
- **C1:** The scan path coordinates log replay, deletion vectors, and physical-to-logical transformations. The write path binds writer state to a transaction and distinguishes committed, conflicted, and retryable commit outcomes; these distinctions are essential when publication is delegated.
- **C3:** Batch visitors and selection vectors avoid requiring the kernel to deserialize every action into individual native structs. Data skipping is part of the scan pipeline rather than an unrelated add-on.

The repository's [architecture guide](https://github.com/delta-io/delta-kernel-rs/blob/main/CLAUDE/architecture.md) maps these interfaces to implementation modules. The repository labels its Rust API and write surface as evolving/experimental; this entry does not claim complete feature parity with other Delta writers.

### [apache/iceberg-rust](https://github.com/apache/iceberg-rust)

**Language/role:** Rust; independent Iceberg implementation with catalog, table, I/O, and transaction abstractions. Particularly useful for studying a typed transaction builder with testable retry policy.

- **C1:** A transaction reloads current table metadata, applies its actions to construct updates and requirements, and submits the resulting commit through the catalog. Retryable failures use bounded exponential backoff; nonretryable errors stop immediately. Tests in the same module exercise eventual success, exhausted retries, nonretryable failure, metadata versions, and row-lineage behavior.
- **C2:** `TransactionAction` separates construction of an operation from `Catalog` publication. This allows multiple kinds of table update to reuse orchestration while preserving their own preconditions and state transitions.

Start with the implementation and embedded tests in [transaction/mod.rs](https://github.com/apache/iceberg-rust/blob/main/crates/iceberg/src/transaction/mod.rs). These provide concrete evidence beyond a compatibility checklist; support for a particular catalog or table feature still needs checking in the chosen release.

### [apache/iceberg-python](https://github.com/apache/iceberg-python)

**Language/role:** Python; PyIceberg's native metadata, catalog, transaction, and Arrow integration. Study how transactional semantics interact with a dynamic-language API and single-use data streams.

- **C1:** Transactions stage requirements and updates, validate expected snapshot references, and prevent reuse after failure. Arrow append paths check schema compatibility, including timestamp precision. A streaming `RecordBatchReader` is consumed once, so retrying the surrounding operation is not equivalent to replaying an in-memory table; failures can also leave uncommitted files.
- **C2:** Builders for schema, sort-order, snapshot, and table updates share a transaction/catalog boundary. This is a substantial reusable metadata implementation, not simply a Python client generated from a REST schema.

The [`pyiceberg.table` implementation](https://github.com/apache/iceberg-python/blob/main/pyiceberg/table/__init__.py) is the entry point: follow `Transaction`, the update builders, and Arrow append handling. The streaming restrictions described in its current code should not be generalized into unrestricted support for all partitioned write paths.

## Commit catalogs, versioned namespaces, and table control planes

### [projectnessie/nessie](https://github.com/projectnessie/nessie)

**Language/role:** Java; a versioned catalog with branches, commits, and transactional changes across content keys. Study catalog-level transaction semantics rather than copying Git terminology at the API surface.

- **C1:** `expectedHash` enables conflict checking against the caller's base state while allowing unrelated keys to advance. Explicit `Unmodified` operations express read dependencies, preventing a transaction from silently ignoring changes to content it relied on. A commit cannot independently modify the same key multiple times.
- **C2:** Stable content IDs are separated from names and branch references. Renaming can be expressed as a delete plus a put retaining the content identity, while the content model supports different catalog objects and multi-key commits.

The [Nessie specification](https://projectnessie.org/develop/spec/) explains keys, identities, commit operations, and conflict semantics in enough detail to guide code reading. Its development-version status matters: experimental content types should not be assumed to have the same stability as the core commit model.

### [treeverse/lakeFS](https://github.com/treeverse/lakeFS)

**Language/role:** Go; versioned object namespaces with branches, commits, diffs, and merges. Its abstraction operates below table formats and can version collections of arbitrary lake objects.

- **C1:** The accepted metadata/KV design examines races between staging writes and branch advancement, using staging tokens, conditional updates, retries, and idempotent operations to preserve acknowledged writes. Read it as an [accepted design record](https://github.com/treeverse/lakeFS/blob/master/design/accepted/metadata_kv/index.md), including its discussion of shortcomings at the time it was written, rather than a blanket guarantee about every current operation.
- **C2:** Current [Graveler interfaces](https://github.com/treeverse/lakeFS/blob/master/pkg/graveler/graveler.go) separate committed ranges, staging state, references, garbage collection, and conflict resolution. Iterator-based diff/merge and content-addressed metaranges make the versioning model reusable independently of a particular table schema.
- **C3:** Immutable ranges/metaranges and mutable staging metadata separate large committed state from frequent small updates; the design also discusses amortizing metadata lookups through caching.

### [apache/polaris](https://github.com/apache/polaris)

**Language/role:** Java; interoperable Iceberg REST catalog. Study the catalog as both a metadata authority and a broker of scoped storage access.

- **C1:** Its [security threat model](https://github.com/apache/polaris/blob/main/SECURITY-THREAT-MODEL.md) traces authentication, role/privilege evaluation, metadata persistence, and credential vending across trust boundaries. User-provided storage locations and credentials with excessive scope are correctness/security concerns distinct from merely accepting valid REST requests.
- **C2:** The repository separates core catalog/entity logic, API definitions, runtime assembly, persistence, federation, and authorization extensions. That structure supports adapting storage backends and external policy systems without replacing the catalog's entire object model; the root documentation maps these modules and the reusable integration-test suite.

The threat model is an especially useful starting point for evaluating how metadata identifiers become authority over physical data. Its documented assumptions and mitigations are study material, not evidence that every deployment configuration enforces every desired policy.

### [lakekeeper/lakekeeper](https://github.com/lakekeeper/lakekeeper)

**Language/role:** Rust; Iceberg REST catalog with a separate management API and PostgreSQL persistence. Useful for studying multi-engine interoperability and storage-credential boundaries together.

- **C1:** Names are case-insensitive but case-preserving, with PostgreSQL ICU collation enforcing uniqueness across case variants. Table/view locations must lie within the warehouse storage profile, must not be parent/child locations of other tables, and must be empty on creation. These checks prevent ambiguous identifiers and leakage through vended credentials.
- **C2:** Catalog requests and management operations have separate APIs. The architecture distinguishes the persistence backend, warehouse storage, secret store, identity provider, authorizer, change-event destination, and optional contract checks, providing concrete extension boundaries.

The [concepts and architecture guide](https://docs.lakekeeper.io/docs/latest/concepts/) explains both the entity hierarchy and these invariants. PostgreSQL is the documented persistence implementation; planned alternatives and separately branded commercial features are not counted as implemented open-source capabilities here.

### [apache/gravitino](https://github.com/apache/gravitino)

**Language/role:** Java; federated metadata management, including a substantive Iceberg REST service. Study the difference between a shared metadata platform and the narrower table-catalog protocol it exposes.

- **C2:** The REST service supports multiple catalog backends and can run as an auxiliary service within Gravitino or separately. This offers a reusable boundary between engine clients, catalog persistence, credential vending, and the broader connector-based metadata platform.
- **C1:** The documented asynchronous purge path removes catalog visibility first but rejects recreation of the same name until file cleanup finishes. Durable cleanup jobs, heartbeat reclamation, and bounded attempts address the failure window between logical deletion and physical deletion.

The [Iceberg REST service guide in the source tree](https://github.com/apache/gravitino/blob/main/docs/iceberg-rest-service.md) documents those mechanics and their configuration. It also makes material boundaries explicit: asynchronous purge is an auxiliary-mode feature, standalone mode does not supply the same access-control integration, and the documented service does not support multi-table transactions. This is a development-branch guide, so release support must be checked separately.

### [unitycatalog/unitycatalog](https://github.com/unitycatalog/unitycatalog)

**Language/role:** Java server with TypeScript/Python components; open-source catalog for tables and other data/AI assets. The entry concerns this implementation, not assumed parity with a managed commercial service.

- **C1:** External identity verification and local catalog authorization are separate steps; a valid identity-provider token alone does not establish catalog permissions. The [authentication/authorization guide](https://docs.unitycatalog.io/server/auth/) explains provisioning and permission behavior. Current persistence code also distinguishes staging-table IDs from regular table IDs when looking up storage for temporary credentials, so a staging-only endpoint cannot silently accept an ordinary table.
- **C2:** The shared catalog/schema asset model supports different asset kinds. Within table persistence, transactional helpers and explicit detached state records let metadata reads, credential lookup, and format-specific commits share infrastructure without requiring the caller to hydrate every association.

Read [TableRepository.java](https://github.com/unitycatalog/unitycatalog/blob/main/server/src/main/java/io/unitycatalog/server/persist/TableRepository.java) for those implementation boundaries, repeatable-read loading, and replay-aware commit handling. Main-branch additions should not be mistaken for guarantees of an older packaged server.

### [apache/hive](https://github.com/apache/hive)

**Language/role:** Java monorepo; selected specifically for the standalone metastore, ACID transaction management, and compactor, rather than for its entire SQL engine.

- **C1:** Transaction/lock state lives in a metastore database; heartbeats allow abandoned work to be aborted. Readers reconcile base and delta files according to transaction visibility. Cleanup must retain obsolete files until readers that still need them have finished, tying garbage collection directly to isolation.
- **C3:** Initiator, worker, and cleaner responsibilities separate compaction planning, rewrite execution, and safe reclamation. Minor and major compaction reduce delta accumulation while supporting concurrent reads and writes under their documented rules.

The [Hive transactions guide](https://hive.apache.org/docs/latest/user/hive-transactions/) explains this architecture and records version-specific changes and upgrade requirements. It contains historical restrictions alongside newer behavior; its early-release limitations should not be read as a uniform description of today's Hive. The metastore/transaction subsystem is the code-reading target, and this monorepo is counted only once.

### [linkedin/openhouse](https://github.com/linkedin/openhouse)

**Language/role:** Java; table control plane with catalog, internal metadata persistence, and scheduled data services. A less ubiquitous but substantive example of separating declarative table management from query engines.

- **C1:** The catalog service writes format-specific metadata and publishes its location through an atomic compare-version-and-swap operation in the House Table Service. This makes the commit precondition and metadata pointer update explicit across service boundaries.
- **C2:** The House Table Service exposes a reusable internal key/value API with pluggable relational persistence. Separate scheduler and jobs services implement retention, snapshot expiration, orphan-file deletion, and staged-file cleanup; job submission and bookkeeping are distinct from catalog requests.

The [architecture guide](https://github.com/linkedin/openhouse/blob/main/ARCHITECTURE.md) follows these service boundaries and the Iceberg integration. It labels some other format/engine integrations as proofs of concept or work in progress. The reusable architecture is the reason for inclusion; an aspirational integration matrix is not treated as production support.

## Table maintenance and format interoperability

### [apache/amoro](https://github.com/apache/amoro)

**Language/role:** Primarily Java, with engine integrations and a web UI; lakehouse management and background optimization. The repository identifies the project as Apache incubating.

- **C2:** AMS detects and plans maintenance work, schedules it to resident optimizers, and submits the results. Optimizer groups provide physical isolation, with table-level quotas and alternative scheduling policies. This is reusable maintenance orchestration across tables rather than a one-off compaction script.
- **C3:** The optimizer distinguishes small fragments from larger segments. Frequent minor optimization compacts fragments and can convert equality deletes to position deletes; less frequent major optimization removes accumulated redundancy. The design explicitly balances read amplification against rewrite cost and competition for CPU, memory, and I/O.

The versioned [0.8.1 self-optimizing guide](https://amoro.apache.org/docs/0.8.1/self-optimizing/) is the entry point for the coordinator/worker architecture, file transformations, and quota versus balanced scheduling. Format-specific behavior should be checked rather than assuming every optimization applies to every supported format.

### [apache/incubator-xtable](https://github.com/apache/incubator-xtable)

**Language/role:** Java; metadata conversion and catalog synchronization across lakehouse table formats. Apache incubating; the canonical repository retains the `incubator-xtable` name.

- **C2:** Table-format synchronization and catalog synchronization are separate operations. Common file, schema, partition, and statistics models connect source and target implementations, allowing interoperability without making a new physical data format. The [features and limitations guide](https://xtable.apache.org/docs/features-and-limitations/) describes the supported semantic boundary, including restrictions around merge-on-read/log and delete representations.
- **C3:** Synchronization writes target metadata alongside existing data files rather than rewriting those files. The [Spark runtime guide](https://xtable.apache.org/docs/how-to-spark-runtime/) explains incremental synchronization with a stored watermark and fallback to a full snapshot when incremental conversion is unsafe.

This is a useful codebase for studying the cost and limits of format interoperability. Shared Parquet data alone does not establish equivalent transactional behavior across formats; unsupported conversion cases are part of the selection's scope, not evidence of complete interchangeability.

## Discovery, lineage, and governance catalogs

These systems belong to the metadata-catalog half of the category. Their modeled entities, ingestion pipelines, and searchable graphs complement transactional storage. The entries below do not infer table-level ACID guarantees from the presence of a catalog or a relational backend.

### [datahub-project/datahub](https://github.com/datahub-project/datahub)

**Language/role:** Java metadata services, Python ingestion, and TypeScript UI; metadata graph, discovery, and lineage platform. Study schema-first modeling and materialization of metadata into different serving systems.

- **C2:** Stable entity URNs and independently modeled aspects separate identity from evolving metadata. Ingestion sources and transformations emit a common model, and schemas drive service/event interfaces. The [component guide](https://github.com/datahub-project/datahub/blob/master/docs/components.md) maps this model to ingestion and storage responsibilities.
- **C3:** Metadata change streams allow graph/search processing to be separated from metadata services. The architecture also describes federated services feeding centralized discovery, giving a concrete way to reason about scaling and asynchronous projections rather than forcing every workload through one query shape.

The [architecture overview](https://github.com/datahub-project/datahub/blob/master/docs/architecture/architecture.md) connects the schema model, APIs, event stream, and federation. Search freshness and projection consistency need their own investigation; no strict synchronous consistency guarantee is inferred here.

### [open-metadata/OpenMetadata](https://github.com/open-metadata/OpenMetadata)

**Language/role:** Java backend, Python ingestion, and TypeScript UI; metadata catalog, lineage, and related governance services. Study one shared entity contract across ingestion, persistence, and presentation.

- **C2:** JSON schemas generate models for Java, Python, and TypeScript. Connector `ServiceSpec` definitions and producer/processor topologies feed the same REST API used by other clients. Resources, entity repositories, and DAOs provide identifiable paths from an API operation to persisted metadata.
- **C3:** SQL persistence is separated from Elasticsearch/OpenSearch serving. Writes emit change events and asynchronous index updates; dedicated reindexing rebuilds search projections. The architecture gives concrete paths for investigating stale search results versus persistence bugs.

The source-tree [architecture map](https://github.com/open-metadata/OpenMetadata/blob/main/ARCHITECTURE.md) explains these mechanisms and also documents limitations, including package cycles and migration-checksum enforcement gaps. Those admissions make it useful complexity-management study material, but they do not justify describing the whole codebase as cleanly layered or all migration invariants as enforced.

### [apache/atlas](https://github.com/apache/atlas)

**Language/role:** Java; typed metadata graph and governance infrastructure, including hooks for Hadoop ecosystem assets. Study how extensible types and entity relationships become graph operations and authorization checks.

- **C2:** The type system separates reusable definitions from entity instances; graph persistence, indexes, REST interfaces, and messaging hooks let different asset kinds participate in one metadata model. The [historical 1.0 architecture guide](https://atlas.apache.org/1.0.0/Architecture.html) provides the architectural orientation and is explicitly a historical source.
- **C1:** Current [AtlasEntityStoreV2.java](https://github.com/apache/atlas/blob/master/repository/src/main/java/org/apache/atlas/repository/store/graph/v2/AtlasEntityStoreV2.java) adds concrete implementation evidence: graph-transaction boundaries, registered-type validation, authorization during entity retrieval, and permission-aware handling of bulk operations. These are meaningful failure and adversarial-input concerns in a shared metadata graph.

Use the historical guide for the model and the current implementation for operational details; do not infer present dependency versions or complete current feature coverage from the 1.0 page.

## Coverage, search process, and limitations

Discovery used distinct live-web search formulations for open transactional table formats; streaming/CDC and LSM lake storage; Iceberg REST catalogs; native Rust/Python implementations and C++ lake storage; Git-like data/catalog versioning; federated metadata and governance graphs; table compaction/maintenance; and cross-format metadata synchronization. Follow-up searches targeted commit protocols, atomic object-store operations, architecture documents, retry tests, credential vending, and release compatibility. This covered Apache projects, independent Rust/Go communities, database-extension authors, and company-origin open-source systems, including OpenHouse, LakeSoul, Lakekeeper, and Amoro alongside the established formats. Later queries largely rediscovered these implementations or surfaced narrower wrappers and examples.

All 24 canonical repository locations were checked against GitHub pages and/or repository API responses, and each retained repository had an additional primary source opened and read. The final API check showed none of these repositories marked archived; that observation is not a claim about maintenance staffing, release cadence, or support. Amoro and XTable's incubation status, Delta Standalone's maintenance status, development documentation, and historical architecture sources are identified where relevant. The native libraries are distinct implementations, not forks counted as separate projects. Each monorepo appears once, with its relevant subsystem stated.

Excluded from this selection were general SQL engines without a focused storage/catalog reason, standalone columnar file formats without transactional metadata, proprietary hosted catalogs without a substantive public implementation, tutorials, generated client wrappers, awesome lists, and redundant forks. Additional language ports and adjacent storage servers were not exhaustively enumerated. Discovery/governance systems are kept in their own subgroup to make the category boundary visible.

This was read-only source and documentation research: no candidate code was executed, no dependencies installed, and no performance or failure-injection experiments performed. Branch and `latest` documentation can describe work ahead of a packaged release; feature completeness, benchmark results, and deployment readiness are not independently certified. C4 is assigned only where inspected dated releases and compatibility work provide direct support, rather than inferred from creation dates or recent pushes.
