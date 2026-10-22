# Time-series databases

Research date: 2026-10-09.

This selection covers 24 GitHub repositories implementing time-series databases or substantial time-series storage subsystems: SQL engines, monitoring stores, distributed databases built on other storage systems, fixed-retention files, and embedded flash databases. The emphasis is on code an experienced engineer can study for storage semantics, indexing, concurrency, recovery, compression, and query execution. Inclusion is an evidence-based study recommendation, not a claim that every component is exemplary or that every project is suitable for a new production deployment.

Criteria used below:

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, malformed input, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces, data models, or execution machinery supporting multiple use cases.
- **C3 — Performance with structure:** explicit resource constraints addressed through an understandable architecture.
- **C4 — Evolution and complexity management:** years of development accompanied by compatibility work, testing, or documented management of complexity.

Canonical repository names, default branches, archive flags, and push metadata were checked through the GitHub API. Each entry also uses an inspected README and/or an additional primary design, documentation, implementation, or test source. Unless stated otherwise, the entry concerns the public implementation; commercial features described alongside it are not assumed to be present.

## SQL, columnar, and distributed telemetry engines

### 1. [influxdata/influxdb](https://github.com/influxdata/influxdb)

**Language / role:** Rust on the current `main` branch; older Go implementations remain on version-specific branches. A time-series database with an Arrow/DataFusion query stack and Parquet persistence.

Study the boundary between accepting writes, making them queryable, and producing durable columnar files. The [durability description](https://docs.influxdata.com/influxdb3/core/reference/internals/durability/) separates validation, write buffering, WAL persistence, query buffering, Parquet creation, and caching.

- **C1:** Acknowledgment semantics depend on `no_sync`: the default waits for WAL persistence, while asynchronous acknowledgment can precede it. The stages make crash exposure and visibility guarantees concrete subjects for review.
- **C3:** Queryable recent buffers and cached persisted Parquet reduce object-storage reads; persistence frequency trades I/O and memory against the amount of data retained in the WAL path.
- **C4:** The [repository README](https://github.com/influxdata/influxdb/blob/main/README.md) explicitly distinguishes v1, v2, and v3 branches and identifies older write/query APIs supported by v3. This makes compatibility across substantial engine changes a useful study angle.

Start with the durability guide and version map above. Do not read descriptions of the older TSM engine as descriptions of current `main`.

### 2. [timescale/timescaledb](https://github.com/timescale/timescaledb)

**Language / role:** C; a PostgreSQL extension adding time-partitioned hypertables, columnar storage, time-series operations, and incremental continuous aggregates.

Study how a specialized engine extends an existing optimizer and relational semantics instead of replacing the database. The [README](https://github.com/timescale/timescaledb/blob/main/README.md) explains hypertables, chunk pruning, columnstore operations, and continuous aggregates.

- **C2:** Hypertables preserve a SQL table interface while managing chunks underneath; continuous aggregates provide a reusable mechanism for incrementally maintained time-based summaries.
- **C1:** The [changelog](https://github.com/timescale/timescaledb/blob/main/CHANGELOG.md) documents subtle interactions among compressed chunks, multiple uniqueness constraints, `NULL`, collations, and parallel execution. These are concrete relational-correctness problems, not merely ingestion plumbing.
- **C3:** The same changelog explains deferred chunk expansion for `LIMIT` queries and chunk exclusion for DML, connecting optimizer structure to planning cost and lock contention.

Start with those two documents, then follow the relevant custom scan or compression changes. The repository contains differently licensed components; GitHub availability should not be treated as a uniform feature license.

### 3. [questdb/questdb](https://github.com/questdb/questdb)

**Language / role:** Primarily Java, with C++ and Rust on performance-sensitive paths; a native SQL time-series database.

Study explicit memory management in a JVM application and the path from parallel ingestion to ordered columnar partitions. The [architecture guide](https://questdb.com/docs/architecture/questdb-architecture/) describes the WAL, storage engine, memory mapping, query compilation, and vectorized execution.

- **C1:** Ordering and deduplication must coexist with out-of-order arrival, concurrent queries, and streaming schema changes; the [README](https://github.com/questdb/questdb/blob/master/README.md) identifies these engine responsibilities.
- **C3:** Memory-mapped columns, time partitioning, page-frame execution, SIMD, and JIT filters expose several interacting optimization layers with identifiable boundaries.
- **C2:** Time-aware SQL operations such as `ASOF JOIN`, `SAMPLE BY`, and latest-value queries package common temporal analysis patterns into reusable operators.

Start with the architecture guide and README. Automatic cold-data tiering and replication described in the broader documentation include Enterprise features; manual Parquet conversion in the public engine is a distinct capability.

### 4. [apache/iotdb](https://github.com/apache/iotdb)

**Language / role:** Java; a distributed database for industrial and device time series, using the separately maintained Apache TsFile format.

Study a device-oriented schema, temporal query execution, and the integration of storage, synchronization, and cluster management. The [README](https://github.com/apache/iotdb/blob/master/README.md) demonstrates typed measurements, per-series encoding choices, and the dependency on columnar TsFile storage.

- **C2:** Hierarchical device/measurement organization and the newer table model support different access patterns within a substantial database/query framework. The [release notes](https://github.com/apache/iotdb/blob/master/RELEASE_NOTES.md) document table functions, temporal joins, window functions, and tree-to-table views.
- **C1:** Those notes describe fixes for oversized requests hanging the WAL queue, concurrent metadata operations deadlocking startup, and failed-write/deletion interactions. These are useful entry points into real failure and concurrency behavior.
- **C3:** Time-series encodings and columnar storage address ingestion volume and scan cost while remaining distinct from the query and cluster layers.

Start with the README and release notes; the database repository is counted once, and its external TsFile dependency is not separately counted here.

### 5. [taosdata/TDengine](https://github.com/taosdata/TDengine)

**Language / role:** Primarily C; an industrial time-series database with distributed storage, SQL, and stream processing.

Study the distinction between physical servers and logical storage, metadata, query, and stream-processing roles. The [architecture guide](https://docs.tdengine.com/internals/arch/) describes dnodes, vnodes, vgroups, mnodes, qnodes, and snodes.

- **C1:** Metadata groups and replicated vnode groups use Raft; leader routing, membership, and replica behavior make distributed correctness visible in the architecture.
- **C3:** Virtual nodes split data and resource ownership; separate query nodes allow query capacity to grow independently of storage. Driver-side metadata caching and routing introduce another explicit performance boundary.
- **C2:** The [README](https://github.com/taosdata/TDengine/blob/main/README.md) describes supertables and built-in subscription/stream processing, which provide reusable structures for fleets of similar sensors rather than requiring one custom pipeline per device type.

Start with the architecture guide and README. No vendor throughput or compression rankings are adopted here.

### 6. [GreptimeTeam/greptimedb](https://github.com/GreptimeTeam/greptimedb)

**Language / role:** Rust; a time-series and observability database whose columnar engine serves metrics, logs, and traces over local or object storage.

Study how one implementation is assembled as either a standalone process or a distributed deployment. The [architecture document](https://docs.greptime.com/user-guide/concepts/architecture/) separates Frontend, Metasrv, Datanode, and optional Flownode responsibilities.

- **C2:** Region routing, database functions, and storage providers are reused across deployment modes. SQL, PromQL, and multiple ingestion protocols share a table model, as described in the [README](https://github.com/GreptimeTeam/greptimedb/blob/main/README.md).
- **C3:** Frontends split work by region; datanodes combine memory, persistent files, pruning, indexes, and caches. Shared object storage separates persistent capacity from compute scaling.
- **C1:** The architecture explicitly states that availability depends on WAL mode, metadata service deployment, region placement, and available datanodes; durable object files alone do not establish a failover guarantee.

Start with the architecture document and README. Public cluster support is distinct from the automated repartitioning and other features identified as Enterprise-only.

### 7. [cnosdb/cnosdb](https://github.com/cnosdb/cnosdb)

**Language / role:** Rust; a distributed SQL time-series database integrating Arrow and DataFusion with its own time-series storage machinery.

Study the interaction between schema evolution, duplicate timestamps, and columnar output. The inspected [series-data implementation](https://github.com/cnosdb/cnosdb/blob/main/tskv/src/mem_cache/series_data.rs) contains `SeriesDedupMergeSortIterator`, schema-versioned row groups, column-ID alignment, and conversion into column pages.

- **C1:** The iterator merges equal timestamps across groups while resolving fields against the aligned schema; column addition/removal and missing fields make a naive timestamp merge insufficient.
- **C2:** The [README](https://github.com/cnosdb/cnosdb/blob/main/README.md) identifies reusable Arrow/DataFusion integration, SQL access, schemaless ingestion, and multi-tenant operation rather than a single-purpose metric file format.
- **C3:** Schema-grouped memory data is transformed into column pages, exposing the cost and layout changes between ingestion and analytical execution.

Start with the series-data file and README. GitHub reported the last push in September 2025; this entry does not imply a currently busy maintenance cadence. Some local exploratory tests in the inspected file are explicitly ignored.

### 8. [openGemini/openGemini](https://github.com/openGemini/openGemini)

**Language / role:** Go; a distributed telemetry database with MPP query processing and specialized storage choices.

Study a concrete response to the memory cost of indexing many distinct series. The [high-cardinality engine guide](https://docs.opengemini.org/guide/features/high_series_cardinality.html) documents explicit columnstore selection, separate shard/primary/sort keys, and Arrow Flight ingestion.

- **C3:** The design addresses index growth and sorting/flushing concurrency directly; configurable sort keys and column ingestion connect physical layout to write and query cost.
- **C2:** The [README](https://github.com/openGemini/openGemini/blob/main/README.md) describes an MPP database with LSM-based storage, while the engine guide presents a common query surface over different engines and an explicit compatibility matrix.

Start with those two documents. The high-cardinality engine has documented limitations in functions and integrations; features advertised for the default engine must not automatically be attributed to it. The useful engineering lesson is the tradeoff between specialized layout and uniform behavior.

## Monitoring, dimensional, and layered distributed stores

### 9. [prometheus/prometheus](https://github.com/prometheus/prometheus)

**Language / role:** Go; a monitoring server containing a substantial local TSDB and query engine. The relevant subsystem is its local time-series storage, not just scraping and alerting.

Study the lifecycle from a mutable head through WAL replay, immutable blocks, indexing, and compaction. The [storage documentation](https://prometheus.io/docs/prometheus/latest/storage/) describes those transitions, tombstones, retention, and backfilling.

- **C1:** Deletion records are separate from chunk data; WAL replay reconstructs recent state; backfills can overlap a still-mutating head. These are concrete consistency and recovery boundaries.
- **C3:** Time-windowed blocks, compressed chunks, label indexes, and background compaction balance ingestion, indexed reads, and retention work.
- **C2:** Local storage and remote read/write interfaces offer explicit extension boundaries, while PromQL remains a separate expression engine over series data.

Start with the storage guide and [repository README](https://github.com/prometheus/prometheus/blob/main/README.md). Local TSDB storage is not itself a clustered or replicated database; the documentation states this limitation.

### 10. [VictoriaMetrics/VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics)

**Language / role:** Go; a time-series database and monitoring monorepo, with both single-node and cluster implementations.

Study a distributed database that makes availability choices visible to callers. The [cluster guide](https://docs.victoriametrics.com/victoriametrics/cluster-victoriametrics/) separates `vminsert`, `vmstorage`, and `vmselect`.

- **C1:** When storage nodes are unavailable, ingestion can reroute and queries can be marked partial. Callers can reject partial responses, and replication settings affect when complete results are assumed. These semantics are part of the API contract.
- **C3:** Consistent hashing distributes series, while storage, ingestion, and query services scale independently. Storage nodes do not exchange state directly, keeping the distributed execution structure understandable.
- **C2:** The [README](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/master/README.md) documents multiple ingestion protocols and PromQL/MetricsQL query support over the storage system.

Start with the cluster guide and README. This counts the monorepo once, not each executable as a separate database.

### 11. [m3db/m3](https://github.com/m3db/m3)

**Language / role:** Go; a monorepo containing M3DB, aggregation, and query components for distributed metric storage.

Study the interaction of compressed in-memory streams, persistent filesets, commit logs, peer recovery, and virtual-shard placement. The [M3DB architecture index](https://m3db.io/docs/architecture/m3db/) provides substantive summaries and links to each mechanism.

- **C1:** Read/write consistency levels are enforced by clients; crash recovery can use a commit log or another replica. Peer bootstrap compares metadata before fetching blocks, introducing correctness questions beyond simple log replay.
- **C3:** M3TSZ/protobuf encoding, shard-and-time-window filesets, and configurable caching policies target memory and disk cost while separating encoding, persistence, and distribution.
- **C2:** M3DB, query, and aggregation components are distinct reusable parts; the [README](https://github.com/m3db/m3/blob/master/README.md) also identifies Prometheus and Graphite integration.

Start with the architecture index and README. Count the monorepo once; the service components are not independent repository selections.

### 12. [Netflix/atlas](https://github.com/Netflix/atlas)

**Language / role:** Scala; an in-memory dimensional time-series database and expression/query system.

Study the relationship between a mutable series store and a periodically rebuilt tag index. [MemoryDatabase.scala](https://github.com/Netflix/atlas/blob/main/atlas-core/src/main/scala/com/netflix/atlas/core/db/MemoryDatabase.scala) uses a concurrent data map, batched index rebuilding, caching, and a Roaring tag index.

- **C1:** Its cleanup/rebuild logic derives index membership from surviving data entries to prevent removed series lingering in the index. Time-window expiry and concurrent updates make this a useful lifecycle invariant.
- **C3:** The [project overview](https://netflix.github.io/atlas-docs/overview/) explains why dimensional aggregation pushed storage toward memory and why historical rollups reduce the dimensions that cause series churn.
- **C2:** A composable query layer and stack language combine filtering, grouping, consolidation, and math; the overview explicitly discusses preserving missing-data/NaN behavior.

Start with the implementation and overview. Netflix's historical deployment description is architectural context, not evidence that every surrounding production service is included in this repository.

### 13. [OpenTSDB/opentsdb](https://github.com/OpenTSDB/opentsdb)

**Language / role:** Java; a distributed time-series service layered over HBase.

Study how physical key encoding determines both query locality and region distribution. The [HBase schema guide](https://opentsdb.net/docs/build/html/user_guide/backends/hbase.html) specifies salted keys, metric/tag UIDs, hourly rows, timestamp offsets, numeric encodings, and compaction formats.

- **C1:** Mixed second/millisecond encodings, integer/float flags, atomic UID allocation, and compare-and-set-sensitive metadata give the storage schema exact invariants that readers and writers must preserve.
- **C3:** Hour buckets prevent oversized rows, salting distributes writes, and post-write compaction reduces per-point overhead. The append alternative explicitly trades less rewrite traffic for server-side read/modify/write work.

Start with the schema guide and repository. The guide describes OpenTSDB 2.4; GitHub reported the last push in December 2024. This is a substantial established implementation, without a claim of current release activity.

### 14. [kairosdb/kairosdb](https://github.com/kairosdb/kairosdb)

**Language / role:** Java; a Cassandra-backed distributed time-series database.

Study how queryable metric/tag metadata is separated from timestamped datapoints. The [Cassandra schema documentation](https://kairosdb.github.io/docs/CassandraSchema.html) describes data rows, time indexes, row-key indexes, optional high-cardinality tag indexes, and internal schema settings.

- **C1:** Row width and timestamp granularity become persisted schema invariants. The documentation explicitly warns that changing them after creation can lose data; legacy and current column encodings must also be distinguished.
- **C3:** Time-index lookup, tag filtering, and batched row reads avoid indiscriminate scans. Optional tag indexes specialize the access path for high-cardinality predicates.
- **C4:** The schema guide records the transition from a legacy index and the introduction of configurable granularity in version 1.3, showing how a long-lived layout evolves while retaining older data interpretation.

Start with the schema guide and [README](https://github.com/kairosdb/kairosdb/blob/develop/README.md). The inspected schema documentation is versioned 1.3.0 and is not assumed to describe every later change.

### 15. [rax-maas/blueflood](https://github.com/rax-maas/blueflood)

**Language / role:** Java; a distributed metric ingestion and rollup system using Cassandra, with Elasticsearch needed for its complete feature set. The older `rackerlabs/blueflood` URL redirects here.

Study asynchronous rollup scheduling and the resource dependencies between locating series, reading inputs, and writing summaries. [RollupService.java](https://github.com/rax-maas/blueflood/blob/master/blueflood-core/src/main/java/com/rackspacecloud/blueflood/service/RollupService.java) makes these stages and their queues explicit.

- **C1:** Rejected locator work must be removed from the running-slot queue; saturation therefore affects scheduler state, not merely throughput. Shard ownership and delayed rollup execution are additional coordination boundaries.
- **C3:** Separate locator-fetch, read, and write executors expose concurrency tuning and queue coupling; gauges track in-flight, queued, and scheduled work. The source also openly uses unbounded queues in later stages, a tradeoff worth examining rather than overlooking.

Start with the rollup service and [README](https://github.com/rax-maas/blueflood/blob/master/README.md). GitHub reported the last push in August 2024; ongoing maintenance is not assumed.

### 16. [senx/warp10-platform](https://github.com/senx/warp10-platform)

**Language / role:** Java; a time-series storage and analytics platform with a richer measurement model that can include location and elevation.

Study the data representation as well as the server. [GTSEncoder.java](https://github.com/senx/warp10-platform/blob/master/warp10/src/main/java/io/warp10/continuum/gts/GTSEncoder.java) maintains independent timestamp, position, elevation, and typed-value encoding state.

- **C1:** Delta/identical encodings require valid prior state. The constructor that accepts existing encoded content disables those modes when previous values are unknown, and mutation respects a read-only state.
- **C3:** Flag-driven delta encodings and synchronized buffer reuse connect compression efficiency with state management and allocation cost.
- **C2:** The [README](https://github.com/senx/warp10-platform/blob/master/README.md) separates storage, history files, and the WarpScript analytics environment and describes multiple storage deployments. The abstractions support analysis independent of a single backing store.

Start with the encoder and README. The focus is the database/encoding/analysis core, not every dashboard or ecosystem integration mentioned in the project material.

### 17. [SiriDB/siridb-server](https://github.com/SiriDB/siridb-server)

**Language / role:** C; a distributed time-series server with its own query language and online expansion machinery.

Study what happens to queries and arriving points while series move between pools. The [reindex implementation](https://github.com/SiriDB/siridb-server/blob/master/src/siri/db/reindex.c) documents altered query behavior during migration and implements persistent progress, asynchronous callbacks, retries, and replica coordination.

- **C1:** Unknown-series errors are treated differently during reindexing because ownership can be in either pool. The drop/commit path explains how points received by a replica during migration are forwarded onward rather than stranded at the old owner.
- **C2:** The [README](https://github.com/SiriDB/siridb-server/blob/master/README.md) describes expanding existing databases and multiple client access methods; reindexing is a reusable server capability rather than a one-off offline conversion.
- **C4:** GitHub metadata places the repository's creation in 2016, and the README describes both unit and containerized integration-test workflows. The inspected migration code shows complexity handled explicitly through state and callback lifecycles.

Start with `reindex.c` and the README, especially the comments describing temporary semantic differences during expansion.

## Fixed-retention files, embedded databases, and historical engines

### 18. [graphite-project/whisper](https://github.com/graphite-project/whisper)

**Language / role:** Python; Graphite's file-based, fixed-size time-series database library.

Study a compact implementation where retention policy is part of the physical file layout. [whisper.py](https://github.com/graphite-project/whisper/blob/master/whisper.py) defines archive metadata, point encoding, archive validation, aggregation, and optional locking/flushing behavior.

- **C1:** Archive precisions must divide correctly, lower-resolution archives must retain more history, and each archive needs enough points to feed the next. `xFilesFactor` determines when missing inputs permit a propagated value.
- **C3:** Predefined archives bound storage and progressively reduce resolution, avoiding indefinite growth while making the accuracy/retention tradeoff explicit.
- **C2:** The [README](https://github.com/graphite-project/whisper/blob/master/README.md) describes a reusable database library and tools for creation, resizing, updating, fetching, and comparing files.

Start with the main implementation and README. This entry is the storage library, not a duplicate listing of the entire Graphite application.

### 19. [oetiker/rrdtool-1.x](https://github.com/oetiker/rrdtool-1.x)

**Language / role:** C; a round-robin time-series database with aggregation and graphing tools.

Study temporal normalization and numerical semantics in a deliberately bounded storage model. The [rrdcreate manual source](https://github.com/oetiker/rrdtool-1.x/blob/master/doc/rrdcreate.pod) defines data-source types, heartbeats, unknown values, consolidation functions, and archive parameters.

- **C1:** Counters, counter resets, 32/64-bit wraparound, derivatives, and missing intervals have different meanings. The manual explains why a reset can be mistaken for a wrap and how heartbeat and consolidation thresholds affect unknown results.
- **C2:** Data-source and archive definitions form a configurable model for gauges, counters, computed values, and multiple consolidation policies, reusable across many monitoring domains.
- **C3:** Round-robin archives give fixed storage requirements while retaining progressively summarized history.

Start with the manual and [README](https://github.com/oetiker/rrdtool-1.x/blob/master/README.md). The value for study extends well beyond the graphing front end.

### 20. [nakabonne/tstorage](https://github.com/nakabonne/tstorage)

**Language / role:** Go; an embedded time-series storage library with memory and local-disk modes.

Study a smaller complete engine whose [README](https://github.com/nakabonne/tstorage/blob/main/README.md) explains time partitions, WAL-before-memory insertion, compressed disk partitions, mmap reads, and late-arriving points.

- **C1:** Multiple writable partitions and temporary out-of-order buffers handle arrivals that cross partition boundaries. [Storage tests](https://github.com/nakabonne/tstorage/blob/main/storage_test.go) exercise selection spanning several partitions, providing an entry point into range-boundary behavior.
- **C3:** Old partitions become read-only compressed files, leaving metadata in the heap; per-metric offsets permit targeted access. Time partitions make the ingestion-to-persistence transition understandable without a large distributed service.
- **C2:** A small `Storage` API supports labeled metrics, configurable timestamp precision, and either memory-only or persistent operation.

Start with the implementation explanation in the README and the storage tests. This is useful as an embedded engine study, not evidence of distributed durability or unlimited late-data support.

### 21. [ubco-db/EmbedDB](https://github.com/ubco-db/EmbedDB)

**Language / role:** C/C++; an embedded database for time-series key/value and relational data on constrained devices and flash storage.

Study how database indexing and execution change when an operating system and abundant RAM cannot be assumed. The [README](https://github.com/ubco-db/EmbedDB/blob/main/README.md) describes learned timestamp indexing, configurable data indexing, and support for raw flash and SD storage.

- **C3:** Index and page choices explicitly target small memory budgets and flash access costs; storage configuration exposes page size and erase-block geometry.
- **C2:** The [advanced-query documentation](https://github.com/ubco-db/EmbedDB/blob/main/docs/advancedQueries.md) defines composable scan, selection, projection, sorting, aggregation, and join operators, including custom operator/aggregate lifecycles.
- **C1:** The same guide specifies ordering constraints on projections, unsigned key requirements, schema/buffer ownership, and different cleanup requirements for operators with multiple inputs.

Start with the README and query-operator guide. This selection counts the embedded repository; the separately linked desktop variant and SQL converter are not additional database entries.

### 22. [armink/FlashDB](https://github.com/armink/FlashDB)

**Language / role:** C; an embedded flash database with key/value and time-series modes. The relevant subsystem here is TSDB/time-series logging.

Study persistence on flash where write granularity, partially completed records, sector rollover, and clock behavior are explicit. The [TSDB implementation](https://github.com/armink/FlashDB/blob/master/src/fdb_tsdb.c) records sector and log-node status transitions and aligns metadata to flash write granularity.

- **C1:** Records enter a pre-write state before data completion; timestamp append checks reject times not greater than the last saved timestamp. The implementation also distinguishes a full database from one allowed to roll over, exposing important loss/retention semantics.
- **C3:** Sector-oriented allocation, fixed-blob options, and compact index records address bounded memory and flash I/O. The [README](https://github.com/armink/FlashDB/blob/master/README.md) identifies wear balancing, multiple instances, and power-off protection as design goals.
- **C2:** Configurable storage instances and per-record status support sensor logs and other firmware records beyond one particular metric schema.

Start with `fdb_tsdb.c` and the README. Power-loss handling is a study topic, not an assertion that all device/driver failure modes have been proved safe.

### 23. [akumuli/Akumuli](https://github.com/akumuli/Akumuli)

**Language / role:** C++; an archived time-series database supporting server and embedded-library use. GitHub marks the repository archived; the last reported push was August 2022.

Study a historical alternative to conventional LSM organization. The [README](https://github.com/akumuli/Akumuli/blob/master/README.md) describes a hybrid LSM/B+tree structure with MVCC, compressed recent data, lazy query production, and aggregation without preconfigured rollups.

- **C3:** Column-oriented compression and aggregation paths that can avoid decompression address both memory use and analytical work; lazy result production connects query execution to consumer progress.
- **C1:** The inspected [WAL recovery test](https://github.com/akumuli/Akumuli/blob/master/functests/test_wal_recovery.py) writes both sparse and denser series, terminates the server, restarts it, and checks backward selections and expected timestamps. This is direct recovery evidence rather than a general reliability claim.
- **C2:** The same core can be embedded or exposed as a network service.

Start with the README and recovery test. The README's feature matrix lists in-order insertion for the implemented version; do not reinterpret its future out-of-order column as a shipped guarantee.

### 24. [facebookarchive/beringei](https://github.com/facebookarchive/beringei)

**Language / role:** C++; an archived in-memory time-series storage engine implementing ideas from Facebook's Gorilla work. GitHub reports the last push in July 2018.

Study the exact bit-level codec, not just the often-repeated Gorilla compression description. [TimeSeriesStream.cpp](https://github.com/facebookarchive/beringei/blob/master/beringei/lib/TimeSeriesStream.cpp) implements timestamp delta-of-delta encoding and XOR-based floating-point encoding.

- **C1:** Timestamp admission checks persist across bucket resets; signed delta transformations and reuse of prior leading/trailing-zero windows create precise encoder/decoder invariants.
- **C3:** The codec selects bit representations according to timestamp regularity and value similarity, and avoids resending a bit-window description when reuse is cheaper.
- **C2:** The [README](https://github.com/facebookarchive/beringei/blob/master/README.md) describes embedded-library use as well as a reference sharded service and client, separating core storage from a deployment wrapper.

Start with the codec and README. This is a historical implementation for study, with old build dependencies; the repository's original performance numbers are not treated as current comparative evidence.

## Search coverage and limitations

Discovery used more than six distinct live search formulations, including Rust/Go WAL-backed engines; Cassandra/HBase time-series services; embedded C/C++ and fixed-size storage; distributed SQL/IoT column stores; Gorilla-derived and other historical engines; geospatial time-series systems; flash/learned-index databases; and Erlang/Scala alternatives. Follow-up searches targeted IoTDB consensus and TDengine logical-node architecture. The later searches mostly rediscovered covered architectural families, while flash-oriented queries added a materially different constrained-device implementation.

The selection spans Rust, Go, Java, Scala, C, C++, and Python; server, embedded, and firmware deployments; memory-resident, columnar, object-storage, wide-column-backed, and round-robin storage. Less prominent projects are retained where inspected code supplies concrete study value, not merely because they advertise a TSDB.

Important exclusions and boundaries:

- DalmatinerDB's GitHub repository points to GitLab. It was excluded because an official substantive current GitHub mirror was not established during this research.
- Apache HoraeDB was inspected but not retained: GitHub marks it archived, and its `main` README describes an unstable replacement engine while directing users to a separate legacy branch. That branch split would require deeper version-specific assessment before adding another Rust engine to this guide.
- Prototype-only candidates such as Catena and newer lightly evidenced projects were not used to fill the list. Generic relational/analytical databases, clients, connectors, dashboards, and benchmark suites were excluded unless their own substantial time-series storage subsystem was the focus.
- Prometheus-derived long-term storage systems such as Thanos, Cortex, and Mimir are an adjacent family not exhaustively covered here. General OLAP systems such as Druid and Pinot are also outside this selection's main storage-engine scope. Their omission does not imply low quality.
- Archived projects and older push dates are labeled. A recent push is not proof of active feature maintenance, and archive status is not a judgment about historical engineering value.
- Primary documentation sometimes mixes open and commercial editions or lags the default branch. The notes identify observed boundaries and versioned documentation where material. No repositories were built, benchmarked, or subjected to an independent correctness audit; criteria express grounded engineering interpretation of inspected primary material, not verification of all runtime claims.
