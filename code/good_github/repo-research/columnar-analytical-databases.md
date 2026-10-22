# Columnar analytical databases

Research date: **2026-10-09**.

This selection covers databases that actually store analytical data by column, plus substantial columnar storage engines integrated into larger database systems. It includes embedded, distributed, GPU, hybrid transactional/analytical, and time-series implementations. A query engine that merely reads Parquet, a file format, a client, and a Bigtable-style column-family store do not qualify on that basis alone. The 19 repositories below are code-reading candidates, not a ranking or a claim that every component is exemplary.

Criteria: **C1** — difficult correctness, including invariants, concurrency, numerical semantics, or failure recovery; **C2** — substantial reusable abstractions; **C3** — real performance constraints addressed through an understandable architecture; **C4** — years of evolution supported by compatibility, testing, or complexity-management evidence. Each entry identifies at least two concrete criteria. Architectural descriptions are documented facts; judgments about what is valuable to study are the researcher's assessment.

## General-purpose analytical SQL engines

### 1. [ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse)

**Language / role:** Primarily C++; complete column-oriented analytical DBMS.

Study how an engine exposes column operations and storage interfaces while allowing specialized implementations to access concrete memory layouts. Its architecture guide is unusually candid about abstraction boundaries and performance trade-offs.

- **C2:** `IColumn`, `IDataType`, `IStorage`, processors, and aggregate-function states separate physical layout, serialization, table access, execution, and aggregation. The same pipeline mechanisms support reads, writes, and `INSERT SELECT`.
- **C3:** Vectorized operations reduce per-value dispatch; buffer abstractions compose compression and I/O; query CPU slots address oversubscription across concurrent queries.
- **C1:** Aggregate-state ownership and destruction, serialization compatibility, and the free/granted/acquired CPU-slot state machine expose concrete lifetime and concurrency invariants.

**Entry point:** [Architecture overview](https://clickhouse.com/docs/resources/develop-contribute/introduction/architecture), including columns, aggregate states, pipelines, and concurrency control. The repository identifies the project as a column-oriented DBMS; it is not merely the ClickHouse client or an integration package.

### 2. [duckdb/duckdb](https://github.com/duckdb/duckdb)

**Language / role:** C++; embedded analytical SQL database with its own storage and execution engine.

Study how one compact execution representation serves SQL operators, storage decompression, and nested data types in an in-process database.

- **C2:** `Vector` and `DataChunk` provide common execution containers. `UnifiedVectorFormat` exposes a generic view across flat, constant, dictionary, and sequence representations, avoiding a separate implementation for every combination.
- **C3:** Dictionary and constant vectors can preserve compression during execution. Short strings are stored inline, while prefixes permit early comparison rejection before pointer chasing.
- **C1:** Nested lists, structs, maps, unions, and their child-vector layouts create precise representation invariants that generic operators must preserve.

**Entry point:** [Execution format](https://duckdb.org/docs/current/internals/vector). The [repository README](https://github.com/duckdb/duckdb) also identifies SQL semantics, embedding options, and unit/benchmark workflows. DuckDB itself is retained once; language bindings and DuckDB-based products are not counted separately.

### 3. [MonetDB/MonetDB](https://github.com/MonetDB/MonetDB)

**Language / role:** Primarily C; analytical relational database. **Official GitHub mirror of the Mercurial repository**, explicitly identified as such by the project; GitHub is not its pull-request contribution channel.

Study a different execution philosophy: fully materialized column vectors and a low-level algebra virtual machine rather than only short vector batches.

- **C2:** Binary Association Tables (BATs), the MonetDB Assembly Language (MAL), and composable optimizer passes separate storage, algebra, and language-specific planning.
- **C1:** BAT properties such as uniqueness, sortedness, null presence, and sequence offsets must remain valid through updates and intermediate creation. Delta storage supports snapshot isolation.
- **C3:** Memory-mapped column arrays and tight bulk-operation loops target data locality; optimizer modules can defer algorithm choices until argument properties are known.

**Entry points:** [Design overview](https://www.monetdb.org/documentation-Dec2025/dev-guide/monetdb-internals/design-overview/) and [MAL/components overview](https://www.monetdb.org/documentation-Dec2025/dev-guide/monetdb-internals/). These describe the actual column-store kernel, not just SQL connectors.

### 4. [heavyai/heavydb](https://github.com/heavyai/heavydb)

**Language / role:** Primarily C++ with GPU/native components; columnar SQL database, formerly MapD/OmniSciDB. The repository now contains a wider platform; this entry concerns the HeavyDB database and query engine.

Study resource admission across heterogeneous CPUs and GPUs, where memory capacity and concurrent execution directly constrain query scheduling.

- **C2:** `ExecutorResourceMgr`, resource pools, request descriptions, and resource handles form a reusable allocation layer across executor requests and device/resource types.
- **C1:** Resource handles return grants on destruction; timed-out requests, queue shutdown, and pausing until outstanding allocations finish require explicit lifetime and synchronization rules.
- **C3:** The manager accounts separately for CPU slots, GPUs, result memory, and CPU/GPU buffer pools, scheduling requests when their resource needs can be satisfied.

**Entry points:** [QueryEngine source tree](https://github.com/heavyai/heavydb/tree/master/QueryEngine) and [documented resource-manager interface](https://raw.githubusercontent.com/heavyai/heavydb/master/QueryEngine/ExecutorResourceMgr/ExecutorResourceMgr.h). The [repository](https://github.com/heavyai/heavydb) explicitly identifies an in-memory column-store SQL engine designed for GPUs.

### 5. [cswinter/LocustDB](https://github.com/cswinter/LocustDB)

**Language / role:** Rust; experimental embedded/standalone analytical database. Treat it as a smaller engineering study, not a production-equivalence claim.

The author's implementation account provides a particularly clear study of making compression part of query execution. Its historical design should be read alongside the current code, rather than assuming every 2018 implementation detail is unchanged.

- **C2:** The described `Column`/`Codec` representation expresses decoding as a small stack-machine program, allowing multiple compression schemes to share serialization and query optimization machinery.
- **C3:** Queries can operate on dictionary indices and decode only the final result. Partitioned column storage and different disk-read scheduling strategies expose the relationship between compression, sequential I/O, and worker parallelism.

**Entry points:** [Author's storage and compression design](https://clemenswinter.com/2018/08/13/how-read-100s-of-millions-of-records-per-second-from-a-single-disk/) and [changelog](https://github.com/cswinter/LocustDB/blob/master/CHANGELOG.md). The README explicitly calls the database experimental and lists consistency/durability and SQL limitations; distributed scaling statements in its “Goals” section are not treated here as implemented capabilities.

## Distributed warehouses and real-time OLAP databases

### 6. [apache/doris](https://github.com/apache/doris)

**Language / role:** C++ backends and Java frontends; distributed analytical SQL database with native columnar tablets.

Study the boundary between query planning, replica management, execution, and shared-storage metadata. The same database documents both integrated and separated storage/compute deployments.

- **C1:** Metadata quorum confirmation, tablet replication and repair, and ingestion version/conflict management are concrete distributed correctness problems.
- **C2:** Frontends handle SQL and cluster metadata; backends execute plans and manage tablets; the separated deployment adds a metadata service responsible for rowsets, versions, and ingestion transactions.
- **C3:** Column encoding, zone-style min/max filtering, runtime filters, distributed shuffle joins, and bounded pipeline execution address both I/O and thread-explosion costs.

**Entry point:** [System architecture](https://doris.apache.org/docs/dev/features-architecture/system-architecture/). The document identifies native columnar storage, data models, execution components, and failure handling; no vendor benchmark multiplier is relied upon here.

### 7. [StarRocks/starrocks](https://github.com/StarRocks/starrocks)

**Language / role:** C++ execution/storage and Java frontend; analytical SQL database supporting shared-nothing and shared-data deployments.

Study an updatable column store combined with an optimizer for multi-table analytics. It is a substantive implementation with its own vectorized execution, optimizer, primary-key update design, and storage/compute architecture, not counted merely as another distribution of Doris.

- **C1:** Ingestion transactions must remain atomic and isolated while the delete-and-insert update path maintains primary-key visibility.
- **C2:** Logical fragments map to physical fragment instances; the cascades-style optimizer performs reusable transformations such as join reordering and subquery rewriting.
- **C3:** Encoded-string execution avoids unnecessary decoding, MPP distributes join/aggregation work, and shared-data compute nodes use local caches over remote storage.

**Entry points:** [Database features and engine mechanisms](https://docs.starrocks.io/docs/introduction/Features/) and [architecture](https://docs.starrocks.io/docs/introduction/Architecture/). These explicitly distinguish native storage from its additional ability to query external lakehouse data.

### 8. [databendlabs/databend](https://github.com/databendlabs/databend)

**Language / role:** Rust; analytical SQL warehouse with the native Fuse table engine over object storage. The repository identifies both Apache-2.0 and Elastic-2.0 licensing; inspect the relevant component's license.

Study the database machinery layered above Parquet: table snapshots, maintenance policies, index choices, and distributed write organization.

- **C2:** Fuse supplies a versioned table abstraction with snapshot locations, history access, change tracking, and independently configurable block/segment organization. A snapshot location also enables sharing without copying table data.
- **C3:** Partition pruning, clustering, compression choices, and filter indexes reduce scan cost. Hash-distributing partitioned writes trades a network shuffle for less small-block fragmentation.
- **C1:** Snapshot retention and automatic vacuum interact with historical reads; schema evolution must correctly fill missing historical values and distinguish new index formats from existing ones.

**Entry points:** [Fuse engine documentation](https://docs.databend.com/sql/sql-reference/table-engines/fuse) and [Fuse source subtree](https://github.com/databendlabs/databend/tree/main/src/query/storages/fuse). Inclusion is for the database and its native table engine, not for Parquet itself.

### 9. [apache/druid](https://github.com/apache/druid)

**Language / role:** Primarily Java; distributed real-time analytical database with time-partitioned columnar segments.

Study how a segment becomes both a physical storage unit and a unit of versioning, availability, and query planning.

- **C1:** Segment replacement provides MVCC-like visibility with atomicity limited to an interval. Shard completeness rules, missing-column semantics, and null bitmaps make correctness boundaries explicit.
- **C2:** Column descriptors and polymorphic serialization allow storage representations to evolve without rewriting all query logic.
- **C3:** Dictionary-encoded dimensions, compressed bitmaps, selective column access, and “smoosh” file consolidation address filtering, bandwidth, and file-descriptor limits together.

**Entry point:** [Segment design](https://druid.apache.org/docs/latest/design/segments/). It includes physical layouts and precise limitations of segment updates; the report does not infer whole-database transactional atomicity from the presence of versioned segments.

### 10. [apache/pinot](https://github.com/apache/pinot)

**Language / role:** Primarily Java; distributed real-time OLAP database with columnar storage and batch/stream ingestion.

Study indexing as a modular part of the database, particularly the differences between mutable consuming segments and completed immutable segments.

- **C2:** The repository exposes segment and planner SPIs and pluggable indexing. The documented index families support different access patterns: inverted, range, text, JSON, geospatial, and star-tree aggregation.
- **C3:** Bloom filters prune segments, inverted indexes narrow selective predicates, and star trees accelerate repeated grouping workloads. The design makes workload-specific indexing decisions concrete.
- **C1:** Indexes supported during live ingestion must remain synchronized with consumed rows; other indexes become available only after segments complete. Configuration overrides distinguish these states.

**Entry point:** [Indexing guide](https://docs.pinot.apache.org/build-with-pinot/indexing). The [repository README](https://github.com/apache/pinot) explicitly confirms column orientation and compression; clients and connectors within the monorepo are not separate entries.

### 11. [ByConity/ByConity](https://github.com/ByConity/ByConity)

**Language / role:** Primarily C++; cloud data warehouse derived from ClickHouse 21.8. **Historical: archived on August 3, 2026**, with active maintenance discontinued in the repository's end-of-life notice.

Retained because its separate implementation adds substantial warehouse architecture: independent compute groups, resource scheduling, distributed metadata, and transaction machinery.

- **C1:** Catalog transactions and the timestamp oracle support consistency across separated metadata and data services, while compaction and garbage collection run as background work.
- **C2:** Catalog and virtual-filesystem APIs abstract metadata and storage backends; plan segments express distributed computation and shuffle dependencies.
- **C3:** Compute groups isolate tenant resources, and scheduling can favor workers with useful cached data while managing queries, writes, and background tasks.

**Entry points:** [Architecture and interaction principles](https://byconity.github.io/docs/introduction/main-principle-concepts) and [repository end-of-life notice](https://github.com/ByConity/ByConity). The archived documentation is useful for study but is no longer an actively maintained deployment reference.

## Columnar engines inside broader database systems

### 12. [mariadb-corporation/mariadb-columnstore-engine](https://github.com/mariadb-corporation/mariadb-columnstore-engine)

**Language / role:** Primarily C++; MariaDB ColumnStore's storage and distributed execution engine, including UM/PM process code. This is the engine repository, not the MariaDB SQL client.

Study a columnar analytical engine integrated behind an established relational server, especially the interaction between physical block addressing, range metadata, and transactional versions.

- **C1:** The documented version buffer preserves modified blocks for rollback and statement snapshots identified by system change numbers; in-flight modifications are tracked by logical block identifier.
- **C2:** Columns, extents, segment files, and the extent map give storage and execution a shared organization for locating and interpreting data.
- **C3:** Min/max metadata permits extent elimination before unnecessary reads, and compression is chosen with decompression and I/O costs in mind.

**Entry point:** [ColumnStore storage architecture](https://mariadb.com/docs/analytics/mariadb-columnstore/architecture/columnstore-storage-architecture). This documentation is framed around Enterprise ColumnStore; use it for the described core mechanisms, and verify edition/version availability before assuming an operational feature exists in a particular community build.

### 13. [citusdata/citus](https://github.com/citusdata/citus)

**Language / role:** Primarily C; PostgreSQL extension. The relevant subsystem is **columnar table storage**, usable for regular and distributed tables; Citus as a whole is not exclusively columnar.

Study how a new physical table organization fits into PostgreSQL's existing SQL, transaction, and partitioning environment.

- **C2:** The same columnar storage capability works with ordinary tables, distributed tables, and mixed row/column partitions, exposing a reusable storage choice inside a general database extension.
- **C3:** Inserts form compressed stripes bounded by transaction size and a row threshold. Projection reduces reads, while small transactions create inefficient tiny stripes—a useful example of ingestion shape changing analytical performance.
- **C1:** The guide explicitly describes rolled-back storage, unsupported tuple locks/serializable isolation, and update restrictions on mixed partitions, exposing the boundary between PostgreSQL behavior and the columnar implementation.

**Entry point:** [Columnar storage and limitations](https://docs.citusdata.com/en/stable/admin_guide/table_management.html#columnar-storage). The inspected guide is labeled Citus 13.0; its restrictions should be interpreted for that documented version, not assumed to describe every newer release.

### 14. [apache/cloudberry](https://github.com/apache/cloudberry)

**Language / role:** Primarily C/C++; PostgreSQL/Greenplum-derived MPP database. The relevant subsystem is **append-optimized column-oriented tables** alongside row-oriented storage. The repository identifies the project as Apache Cloudberry (Incubating).

Study columnar storage inside a database that retains PostgreSQL semantics and distributed table placement. The repository documents separate evolution from Greenplum through a newer PostgreSQL kernel and additional capabilities.

- **C2:** A table can select heap, append-optimized row, or append-optimized column storage while retaining SQL and distribution-policy concepts.
- **C1:** Append-optimized tables have documented transaction-isolation restrictions; distribution changes require coordinated data redistribution while preserving table attributes.
- **C3:** Bulk-load-oriented layouts remove per-row visibility overhead, while column compression and selective column reads target large fact tables. The documentation explains the compression/random-access trade-off.

**Entry point:** [Table storage models](https://cloudberry.apache.org/docs/1.x/table-storage-models/), a versioned 1.x guide. Greenplum is not counted again as a duplicate lineage entry here.

### 15. [pingcap/tiflash](https://github.com/pingcap/tiflash)

**Language / role:** Primarily C++ with a Rust proxy component; TiDB's columnar analytical engine. It requires the TiDB/TiKV ecosystem for writes and is not an independent general-purpose SQL server.

Study strongly consistent analytical replicas without forcing transactional writes through the analytical execution path. Its Raft/MVCC integration constitutes substantial separate engineering despite reuse of ClickHouse execution components.

- **C1:** Asynchronously replicated Raft learners validate replication progress against a read timestamp and use MVCC to provide snapshot-isolated reads. Region splitting/merging must track the transactional replica topology.
- **C2:** The storage/proxy boundary separates columnar storage and computation from Multi-Raft communication; TiDB can choose row, column, or mixed access paths.
- **C3:** Compute pushdown and vectorized column scans accelerate analytics, while separate analytical nodes isolate workloads from transactional storage.

**Entry point:** [TiFlash architecture and consistency](https://docs.pingcap.com/tidb/stable/tiflash-overview/). The documentation explicitly states that direct writes to TiFlash are not supported; that dependency is part of its category fit.

### 16. [apache/kudu](https://github.com/apache/kudu)

**Language / role:** Primarily C++; distributed mutable columnar data store/storage engine. **Official Apache GitHub mirror**, as identified by the repository. SQL is supplied through integrations such as Impala.

Study a service that combines efficient analytical column scans with row-level mutation and replicated tablets. Unlike HBase-style column families, Kudu explicitly stores strongly typed columns in a physically columnar layout.

- **C1:** Both masters and tablets use Raft; acknowledged writes require persistence to a majority. Fault detection and re-replication must preserve availability and consistency as replicas disappear.
- **C2:** Schema-bearing tables, ordered primary keys, tablets, and metadata APIs provide reusable units for partitioning and database integration.
- **C3:** Predicate pushdown and parallel tablet scans reduce transfer costs. Logical replication lets replicas compact independently without transmitting compaction output or synchronizing their physical layouts.

**Entry point:** [Architecture, concepts, and integration mechanisms](https://kudu.apache.org/docs/). Kudu is retained as a real storage service; the report does not mistake its Impala client integration for a self-contained SQL engine.

## Time-series and observability databases with columnar engines

### 17. [questdb/questdb](https://github.com/questdb/questdb)

**Language / role:** Primarily Java with native C++/Rust components; SQL time-series database with native columnar partitions and Parquet support.

Study how an append-heavy time-series database handles out-of-order arrivals and parallel writers while preserving a columnar read path.

- **C1:** Per-connection/table WAL streams are consolidated through a sequencer assigning transaction numbers. The table writer resolves out-of-order data and deduplication; durability depends on the documented commit mode.
- **C2:** A common table/partition abstraction supports both native column files and Parquet partitions through the same query interface.
- **C3:** The row-oriented ingestion path feeds column-oriented storage; column files, vectorized page-frame execution, and time partitioning reduce scan and CPU costs.

**Entry points:** [Storage engine](https://questdb.com/docs/architecture/storage-engine/) and [architecture overview](https://questdb.com/docs/architecture/questdb-architecture/). Automatic cold-storage tiering is documented as Enterprise functionality; it is not attributed here to the open-source engine. The storage guide distinguishes default OS-level durability from synchronous commits.

### 18. [GreptimeTeam/greptimedb](https://github.com/GreptimeTeam/greptimedb)

**Language / role:** Rust; distributed observability/time-series database. The relevant columnar storage subsystem is **Mito**, which persists Parquet SST files.

Study how LSM techniques and columnar analytics fit together in an engine designed around series keys and timestamps.

- **C1:** Internal primary-key, sequence, and operation columns support correct merging, deduplication, and deletion across memtables and SSTs. Freezing/flushing memtables and WAL persistence create additional recovery boundaries.
- **C2:** Regions define isolated schema-bearing storage units; the `Log Store` API permits local or remote WAL implementations independently of the engine's write logic.
- **C3:** Key/time ordering improves series locality and compression; time-range pruning, row-group statistics, and selective indexes progressively avoid reads. Time-window compaction cooperates with retention policies.

**Entry point:** [Mito storage-engine design](https://docs.greptime.com/contributor-guide/datanode/storage-engine/). The source repository's columnar-engine description and this implementation guide establish database fit; the presence of SSTs does not make it a Bigtable-style column-family entry.

### 19. [influxdata/influxdb](https://github.com/influxdata/influxdb)

**Language / role:** Rust for the **InfluxDB 3 Core** subsystem considered here; time-series/real-time analytics database built with Arrow and DataFusion and storing Parquet. Older InfluxDB generations use different designs and are not conflated with this entry.

Study the transition from accepted writes to durable WAL, queryable buffers, and persistent columnar files in an actual database built around reusable execution components.

- **C1:** The durability guide distinguishes acknowledgment before persistence with `no_sync=true` from the default WAL-persisted acknowledgment. Query visibility and Parquet persistence occur at distinct stages.
- **C2:** Write validation, WAL, query buffers, persistent files, and caches form explicit stages around SQL/InfluxQL interfaces and the reusable Arrow/DataFusion stack.
- **C3:** Buffered writes amortize object-store I/O; recent data remains queryable in memory; caching newly persisted Parquet avoids immediate remote reads. Persistence also consumes the configured execution memory pool.

**Entry points:** [Storage-engine scope](https://docs.influxdata.com/influxdb3/core/reference/internals/storage-engine/) and [write-path durability](https://docs.influxdata.com/influxdb3/core/reference/internals/durability/). The Core documentation explicitly separates its Parquet engine from an upgraded Enterprise-only storage engine.

## Coverage, search method, and limitations

Discovery used more than six distinct live-search formulations: general columnar analytical DBMSs; distributed cloud warehouses; C/C++ and GPU engines; Rust implementations; real-time OLAP databases; PostgreSQL columnar storage; lesser-known embedded engines; and mutable/HTAP storage. Follow-up searches targeted snapshot-based object storage, compression, physical layout, and project status. Every retained canonical GitHub repository was opened, followed by at least one additional relevant primary document or source page. Later discovery queries increasingly returned already-covered engines, wrappers, formats, or early experimental projects.

The resulting selection spans C, C++, Java, and Rust; embedded and cluster scales; academic, Apache, independent-developer, and commercial project communities. It includes substantial related implementations only where their separate architecture is meaningful: ByConity, TiFlash, StarRocks, and Cloudberry are not presented as unrelated lineages. MonetDB and Kudu mirrors, ByConity's archive, LocustDB's experimental status, and relevant monorepo subsystems are called out explicitly.

Excluded by scope are Parquet/ORC/Arrow as formats or libraries, DataFusion/Velox as execution building blocks without a database service of their own, database clients and connectors, and Cassandra/HBase-style column-family systems. DuckDB wrappers are not additional engines. Proprietary-only warehouses were not used to fill the list. Additional time-series and early beta projects surfaced, but were not all pursued to equivalent depth; this is a substantial selection rather than an exhaustive catalog.

This was read-only repository/documentation research, not a benchmark, operational audit, or full source review. No candidate code was executed. Documentation can cover commercial editions or lag a default branch; version/edition distinctions are noted where material. Historical descriptions are labeled, numerical marketing comparisons are omitted, and absence of an archive label is not offered as proof of active maintenance. C4 is not awarded merely for a large commit count or an old copyright date.
