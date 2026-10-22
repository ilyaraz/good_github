# Metrics storage and monitoring systems

Research date: **2026-10-09**.

This guide selects 24 repositories implementing metric storage, ingestion, querying, collection, or monitoring and alert evaluation. It spans embedded retention stores, distributed time-series databases, and complete monitoring systems. For broader observability monorepos, the relevant metrics subsystem is identified and the repository is counted once. The selection emphasizes implementation lessons for experienced engineers; it is not a deployment ranking or a claim that every component is uniformly exemplary.

Criteria used below:

- **C1 — Difficult correctness:** meaningful invariants, concurrency, numerical semantics, adversarial inputs, or recovery and failure behavior.
- **C2 — Reusable abstractions:** substantial interfaces or components supporting multiple use cases, protocols, or deployment forms.
- **C3 — Performance with structure:** concrete resource constraints addressed through understandable storage, execution, or distribution architecture.
- **C4 — Sustained evolution:** multi-year evidence of compatibility work, testing, or management of accumulated complexity. Repository age alone does not qualify.

Criterion assignments are engineering judgments grounded in the linked primary material. Repository headings link to verified GitHub pages; the accompanying documentation and source links are starting points for deeper reading.

## Prometheus and distributed metrics backends

### 1. [prometheus/prometheus](https://github.com/prometheus/prometheus)

**Go — monitoring server, PromQL engine, and local TSDB.** A useful starting point for studying how a mutable ingestion head becomes immutable indexed blocks, and how query semantics interact with storage changes.

- **C1:** The write-ahead log recovers the in-memory head; deletions use tombstones, and backfilling must respect the mutable head's time range. These are concrete persistence and overlap invariants. The [storage documentation](https://prometheus.io/docs/prometheus/latest/storage/) explains the layout and operational boundaries.
- **C3:** Chunk files, per-block indexes, memory mapping, and background compaction separate ingestion from historical scans while creating explicit disk-space and retention tradeoffs. The same storage guide explains these mechanisms without requiring a distributed deployment.
- **C4:** The [changelog](https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md) contains sustained compatibility and correctness work across 2020–2026, including WAL compression downgrade restrictions, PromQL numerical fixes, and restart/compaction fixes. This supports studying evolution as well as the current architecture.

### 2. [VictoriaMetrics/VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics)

**Go — single-node and clustered metrics database in one repository.** Study the relationship between series indexing, compressed time-series parts, and crash-safe publication of newly written or merged data.

- **C1:** Parts become visible through an atomically updated `parts.json` after files are written and synchronized. Incomplete parts are discarded, and merge publication preserves the old parts until replacement is complete. This is a concrete crash-consistency protocol; it does not mean that buffered, unflushed data is already durable. See the [storage internals](https://docs.victoriametrics.com/victoriametrics/#storage).
- **C3:** Blocks organize compressed timestamps and values by series and time, while global and per-day inverted indexes address label lookup costs. Merges also account for available disk space. The [IndexDB description](https://docs.victoriametrics.com/victoriametrics/#indexdb) connects indexing choices to query and retention costs.

### 3. [thanos-io/thanos](https://github.com/thanos-io/thanos)

**Go — federated querying and long-term storage around Prometheus.** Particularly useful for studying how an existing local database can become part of a larger storage system through explicit interfaces.

- **C2:** A common gRPC Store API represents both live Prometheus sidecars and gateways serving blocks from object storage. Query components can combine these sources through the same abstraction. The [design document](https://thanos.io/tip/thanos/design.md/) explains this component boundary.
- **C3:** Immutable blocks, cached index information, metadata-based pruning, and object-store range reads address expensive remote requests and unnecessary data transfer. These mechanisms make the storage/query decomposition concrete rather than merely describing horizontal scaling.

The linked document contains original design history as well as architectural motivation. Its early deployment restrictions should not be treated as a complete statement of current capabilities.

### 4. [cortexproject/cortex](https://github.com/cortexproject/cortex)

**Go — multi-tenant, distributed Prometheus-compatible storage.** Study distributed ingestion together with the scheduling and fairness problems that arise when many tenants share a query service.

- **C1:** Distributor validation, replication quorums, ingester ring states, WAL recovery, and HA replica selection coordinate which samples are accepted and where they survive failures. The [architecture documentation](https://cortexmetrics.io/docs/architecture/) describes the responsibilities of each component.
- **C3:** Per-tenant TSDB blocks and batched writes reduce storage overhead; query frontends split long queries, cache results, and schedule work through tenant-aware queues. These give concrete examples of balancing throughput against contention and fairness.

The architecture page is a useful reading route from distributor and ingester behavior into the query frontend and storage gateway, rather than treating the repository as one undifferentiated distributed database.

### 5. [grafana/mimir](https://github.com/grafana/mimir)

**Go — distributed metrics backend with a Kafka-based ingestion architecture.** Mimir is explicitly a [Cortex fork](https://grafana.com/blog/qa-with-our-ceo-about-grafana-mimir/); it is retained separately because its subsequent storage and execution architecture provides substantive additional material.

- **C1:** In the documented ingest-storage architecture, write acknowledgment follows Kafka persistence, consumers recover using stored offsets, and strong reads propagate offsets so the read path can wait for ingestion. This makes asynchronous ingestion and read-after-write guarantees an explicit protocol. See the [ingest-storage design](https://grafana.com/docs/mimir/latest/get-started/about-grafana-mimir-architecture/about-ingest-storage-architecture/).
- **C3:** Kafka separates write acceptance from ingester consumption, while partitioned ingestion and query splitting allow different parts of the workload to scale independently. The same design explains the resulting buffering and consistency tradeoffs.

This entry concerns the open repository's metrics backend, with attention to the architecture preferred since Mimir 3.0.

### 6. [m3db/m3](https://github.com/m3db/m3)

**Go — M3DB, aggregation, and query components in one monorepo.** Counted once; the strongest entry point here is M3DB's engine and its hierarchy of storage responsibilities.

- **C2:** The database decomposes into namespaces, shards, series, and buffers/blocks. Namespace options carry policies such as retention and block size, while encoding supports both floating-point series and protobuf data. These abstractions separate placement and lifecycle policy from individual series representation. See the [engine design](https://github.com/m3db/m3/blob/master/site/content/architecture/m3db/engine.md).
- **C3:** M3TSZ adapts Gorilla-style compression, while buffers accept recent writes and bootstrapped data before block flushing. The design makes memory residency, compression, and disk organization visible in a compact hierarchy.

This is a useful comparison with Prometheus's head/block model and with storage engines that make an LSM tree their central abstraction.

## Specialized time-series storage engines

### 7. [influxdata/influxdb](https://github.com/influxdata/influxdb)

**Rust — InfluxDB 3 Core; older Go generations remain in separate branches.** This entry focuses on the current repository's v3 Core write path, avoiding conflation with older TSM internals or commercial-edition features.

- **C1:** Write validation, the write buffer, object-store WAL persistence, and query visibility have distinct stages. Normal acknowledgment follows WAL persistence, whereas `no_sync=true` permits an earlier acknowledgment with a different durability contract. The [Core durability documentation](https://docs.influxdata.com/influxdb3/core/reference/internals/durability/) explains these boundaries.
- **C3:** WAL batches eventually become Parquet files, with memory caching serving a different role from durable object storage. Engineers can study how batching and columnar persistence coexist with queries over recent writes, rather than assuming that all queryable data has the same physical representation.

The repository heading and durability guide together establish both the implementation generation and the subsystem being assessed.

### 8. [GreptimeTeam/greptimedb](https://github.com/GreptimeTeam/greptimedb)

**Rust — distributed observability database; focus on the Mito time-series storage engine.** Study how a columnar LSM design represents metric series, versions, deletions, and time-based retention.

- **C1:** Regions use a WAL, mutable and immutable memtables, SST files, and manifests. Internal primary-key, sequence, and operation-type columns supply the information needed for deduplication and deletion semantics. The [storage-engine guide](https://docs.greptime.com/contributor-guide/datanode/storage-engine/) exposes these mechanisms.
- **C3:** Sorting by tags and time, Parquet SST storage, file/row-group statistics, and time-window compaction connect physical layout to metric scans and TTL expiration. This is a concrete example of adapting an LSM architecture to analytical time-series access.

The assessment concerns the documented open storage engine. It does not assume that every feature advertised across the broader product family belongs to the open edition.

### 9. [OpenTSDB/opentsdb](https://github.com/OpenTSDB/opentsdb)

**Java — metrics storage and querying over HBase.** Useful for studying how a specialized time-series data model is encoded onto a general distributed key/value substrate.

- **C1:** UID assignment, sorted tag identifiers, timestamp offsets, and value-type flags must agree across writers and readers. The documented standard and append schemas are not interchangeable. The [HBase schema guide](https://opentsdb.net/docs/build/html/user_guide/backends/hbase.html) details these encoding and compatibility constraints.
- **C3:** Salted row keys distribute load; time-bucketed rows group nearby samples; OpenTSDB's own compaction combines points into fewer columns. The guide distinguishes this process from HBase compaction, which is an important separation of responsibilities.

The additional source is the project's 2.4 documentation. It supports studying that storage generation, without establishing a claim about current release cadence.

### 10. [kairosdb/kairosdb](https://github.com/kairosdb/kairosdb)

**Java — metrics database backed by Cassandra.** A useful contrast to OpenTSDB: follow how metric, time, and tag indexes lead to the underlying data-point rows.

- **C1:** Row width and time units are persisted as schema choices; the documentation warns that changing them after creation can cause data loss. Data-point implementations also control value serialization. These are concrete storage-format invariants. See the [Cassandra schema](https://kairosdb.github.io/docs/CassandraSchema.html).
- **C3:** Separate metric/time/tag indexing structures and an optional high-cardinality tag index trade write and index overhead for more selective reads. The schema documentation makes those access paths inspectable.

The [project documentation homepage](https://kairosdb.github.io/) also introduces plugin extension points for stores, protocol handling, and data-point listeners. The schema material is versioned documentation, not evidence by itself of present maintenance activity.

### 11. [akumuli/Akumuli](https://github.com/akumuli/Akumuli)

**C++ — specialized time-series database and embeddable engine.** Retained principally as a historical storage-design study; current maintenance was not established during this research.

- **C1:** The Numeric B+tree design depends on ordered timestamp insertion, page boundaries, and the structure of successively larger extents. These invariants determine which append and merge operations are valid. The [2017 engine article](https://akumuli.org/akumuli/2017/04/29/nbplustree/) explains the design.
- **C3:** Separate series trees share physical files, while reference-based merging avoids repeatedly rewriting all accumulated data. The design explicitly addresses read amplification, write amplification, and the memory cost of partially filled leaves.

The [changelog](https://github.com/akumuli/Akumuli/blob/master/CHANGELOG.md) adds concrete failure cases to inspect, including WAL race and buffer-overflow fixes, parser integer overflow, and backward-query result corrections. These are useful study leads, not a claim that the implementation is uniformly correct.

### 12. [facebookarchive/beringei](https://github.com/facebookarchive/beringei)

**C++ — compressed in-memory time-series storage with persistence and a reference service. Archived on January 13, 2022.** Its narrower encoding implementation makes a useful companion to larger storage systems.

- **C1:** Timestamp order checks and minimum deltas interact with bucket resets, while floating-point values are encoded through their bit representations. These require exact boundary and state-transition behavior. Read [`TimeSeriesStream.cpp`](https://github.com/facebookarchive/beringei/blob/master/beringei/lib/TimeSeriesStream.cpp).
- **C3:** Delta-of-delta timestamp coding and XOR-based value coding reuse previous-value state and leading/trailing-zero information to reduce storage per sample. The same source exposes both the compression mechanism and the state that readers and writers must preserve.

This is explicitly a historical implementation reference. The archived repository should not be mistaken for an actively maintained deployment recommendation.

## Graphite ingestion and bounded-retention storage

### 13. [graphite-project/whisper](https://github.com/graphite-project/whisper)

**Python — fixed-size, multi-resolution time-series storage library.** An unusually approachable codebase for examining retention and aggregation semantics at the file-format level.

- **C1:** Archive resolutions must have compatible divisibility, stored timestamps distinguish valid samples from stale ring slots, and a query selects an archive capable of covering its range. These rules affect the meaning of missing and downsampled data. The [Whisper design documentation](https://graphite.readthedocs.io/en/latest/whisper.html) explains the constraints.
- **C3:** Preallocated archives bound disk usage and permit contiguous reads and writes. Overlapping archives exchange detailed recent data for cheaper long-term history, exposing the space, precision, and I/O tradeoff directly.

Whisper is counted independently from Carbon because it implements the reusable storage format and operations, whereas Carbon implements ingestion and routing daemons.

### 14. [graphite-project/carbon](https://github.com/graphite-project/carbon)

**Python/Twisted — Graphite metric ingestion, routing, aggregation, and persistence daemons.** Study a small set of independently deployable components with distinct positions in the metric pipeline.

- **C2:** `carbon-cache`, `carbon-relay`, and `carbon-aggregator` separate hot-data caching/persistence, forwarding, and interval aggregation. They can be composed into different deployments using shared metric protocols. The [daemon architecture guide](https://graphite.readthedocs.io/en/latest/carbon-daemons.html) describes their responsibilities.
- **C3:** The cache batches writes to Whisper and answers requests for recent cached data; relays distribute or replicate traffic, including through consistent hashing; aggregation reduces the number of downstream points. Each component addresses a concrete bottleneck rather than relying on a single scaling mechanism.

This repository is useful for comparing asynchronous ingestion pipelines with databases whose buffering and persistence are internal to one server.

### 15. [go-graphite/go-carbon](https://github.com/go-graphite/go-carbon)

**Go — substantive reimplementation of the Graphite/Carbon server.** Retained separately from Python Carbon for its own concurrency, persistence, and metric-index implementation.

- **C1:** The documented pipeline uses metric-based worker assignment and file locking for persistence, and includes a cache dump/restart procedure. These expose coordination across in-memory queues, filesystem updates, and process lifecycle. See the repository's [architecture and configuration](https://github.com/go-graphite/go-carbon#readme).
- **C3:** Parallel persister workers distribute storage work, while a prefix-sharing trie supports metric lookup and glob matching. The architecture makes the relationship between ingestion parallelism and query indexing clear.

The [changelog](https://github.com/go-graphite/go-carbon/blob/master/CHANGELOG.md) is a second reading entry point for implementation changes, including cache-size representation and sharding behavior. This entry assesses the independent server implementation rather than counting compatibility with Graphite as originality by itself.

### 16. [oetiker/rrdtool-1.x](https://github.com/oetiker/rrdtool-1.x)

**C — reusable round-robin metric storage, consolidation, and graphing.** Study the numerical model underlying bounded time-series archives rather than viewing it only as a graph-generation tool.

- **C1:** Data-source types normalize incoming values into evenly spaced primary data points, then consolidation functions form archive points at coarser intervals. The definitions in [`rrd_format.h`](https://github.com/oetiker/rrdtool-1.x/blob/master/src/rrd_format.h) make timing and consolidation semantics explicit. The [creation guide](https://oss.oetiker.ch/rrdtool/doc/rrdcreate.en.html) also explains limitations of prefilling/resampling existing data.
- **C2:** Data sources, source types, consolidation functions, and round-robin archives are separate abstractions. Multiple archives with different resolutions and functions reuse the same representation, providing a general model for counters, gauges, and retention policies rather than a single monitoring application's schema.

The format header is especially useful for connecting user-facing retention configuration to actual stored structures.

## Monitoring systems, collection, and alert evaluation

### 17. [netdata/netdata](https://github.com/netdata/netdata)

**C/C++ and Go — monitoring agent with collection, querying, and local tiered storage.** The selected subsystem is DBENGINE, rather than the entire surrounding product surface.

- **C1:** Pages assume a uniform collection interval, so an interval change requires a new page; gaps and aggregate samples have explicit representations. Tiered aggregates preserve quantities such as sum, count, minimum, and maximum. The [database-engine documentation](https://learn.netdata.cloud/docs/developer-and-contributor-corner/database-engine) describes these data semantics.
- **C3:** Implicit timestamps within uniform pages reduce repeated metadata, compressed extents group pages for I/O, and hot/dirty/clean page states separate ingestion from persistence and caching. These are inspectable mechanisms for serving recent and historical metrics within agent resource limits.

This provides a useful middle ground between a small fixed-retention library and a separately operated distributed metrics service.

### 18. [zabbix/zabbix](https://github.com/zabbix/zabbix)

**C, PHP, and Go — full monitoring server/proxy/agent system. Official GitHub mirror.** The project documents its primary repository and the [GitHub mirror of master and supported releases](https://www.zabbix.com/documentation/current/en/manual/installation/getting_zabbix). The selected study area is server-side preprocessing and history ingestion.

- **C1:** Some preprocessing operations require sequential task execution, including change-based calculations and throttling. Dependent-item execution and value normalization introduce further ordering and error-propagation rules. The [Zabbix 7.0 preprocessing internals](https://www.zabbix.com/documentation/7.0/en/manual/config/items/preprocessing/preprocessing_details) explain these distinctions.
- **C3:** Asynchronous IPC, preprocessing workers, history caches, and history syncers divide the pipeline. Parsed Prometheus or JSONPath data can be reused across dependent items, reducing repeated parsing work.

These details make Zabbix useful for studying a monitoring system's internal dataflow, not just its inventory of integrations. The cited internals describe the 7.0 generation.

### 19. [Icinga/icinga2](https://github.com/Icinga/icinga2)

**C++ — distributed check execution, notifications, and monitoring configuration.** Study how a common object lifecycle controls which endpoint is responsible for work.

- **C1:** Object authority is calculated from object or host identity and connected endpoints, then drives pause/resume transitions. Database IDO writers additionally use endpoint and timestamp information to limit duplicate writes during partition/failover scenarios. The [technical-concepts guide](https://icinga.com/docs/icinga-2/latest/doc/19-technical-concepts/) explains both mechanisms and their distinct responsibilities.
- **C2:** The shared configuration-object and authority machinery is reused by checking, notification, and database-writing features. This is a substantial lifecycle abstraction spanning multiple kinds of monitoring work, not merely a list of plugins.

The guide is particularly useful for comparing ordinary distributed ownership with the additional safeguards needed when an external database is the destination.

### 20. [netxms/netxms](https://github.com/netxms/netxms)

**C++ core and Java clients — network and infrastructure monitoring.** A less frequently cited large system with reusable platform libraries and explicit metric-export machinery.

- **C2:** The [C++ developer guide](https://github.com/netxms/netxms/blob/master/doc/CPP_DEVELOPER_GUIDE.md) separates cross-platform utilities, database access, and scripting into libraries. It also documents thread-pool primitives, including serialization by key, that support different server workloads.
- **C3:** The [advanced administration source](https://github.com/netxms/netxms-doc/blob/master/admin/advanced.rst) describes per-data-item distribution to ClickHouse sender queues, independent workers, binary batches, and flush/queue limits. Queue overflow can drop data: the documentation exposes the resource-versus-delivery tradeoff instead of implying unlimited buffering.

Together these entry points connect a broad monitoring application's internal abstractions with a concrete ingestion/export bottleneck. The documentation repository is evidence for NetXMS, not an additional counted project.

### 21. [collectd/collectd](https://github.com/collectd/collectd)

**C — plugin-driven metric collection and routing daemon.** Included as substantive monitoring infrastructure; it is not itself a durable historical database.

- **C2:** Input and output plugins communicate through typed values and a shared dispatch path. The [exec-plugin manual](https://collectd.org/documentation/manpages/collectd-exec.html) demonstrates the abstraction through external long-lived collectors and notification handling, without requiring each collector to implement every destination protocol.
- **C3:** Configurable read intervals, flush behavior, bounded write queues, and backoff after read failures address slow destinations and failing collectors. The [configuration manual](https://collectd.org/documentation/manpages/collectd.conf.html) documents these resource controls, including dropping behavior when queues become overloaded.

This is useful for studying the boundary between extension APIs and operational behavior: a plugin contract alone is insufficient unless the daemon also controls scheduling and accumulated work.

### 22. [riemann/riemann](https://github.com/riemann/riemann)

**Clojure — monitoring event streams, state indexing, and alerting.** Its focus is event processing and current state rather than durable metric history.

- **C2:** Immutable event maps flow through composable stream functions; an index represents the latest host/service state, and TTL expiration is fed back as an event. The [concepts guide](https://riemann.io/concepts.html) shows how grouping, state changes, and rollups are assembled from reusable operations.
- **C4:** The [changelog](https://github.com/riemann/riemann/blob/main/CHANGELOG.md) provides multi-year evidence across 2020–2025: runtime and dependency updates, JDK compatibility work, CI/test improvements, and transport-recovery fixes. This supports studying the maintenance of an extensible long-running service across platform changes.

Riemann is a useful contrast to rule engines centered on periodic database queries: its primary abstraction is the processing of incoming events and their lifecycle.

### 23. [ccfos/nightingale](https://github.com/ccfos/nightingale)

**Go — monitoring and alert evaluation over external data sources.** The repository's role is the monitoring/alert layer; it should not be mistaken for a new metrics-storage engine. Study the lifecycle of a scheduled rule worker.

- **C1:** `AlertRuleWorker` restores current alert state, configures cron execution to skip overlapping runs, and coordinates scheduler shutdown. These choices directly affect duplicate work and state continuity. Read [`alert/eval/eval.go`](https://github.com/ccfos/nightingale/blob/main/alert/eval/eval.go).
- **C2:** Workers bind rule and data-source identity to shared processing, using Prometheus clients or other data-source paths to produce common anomaly inputs. This lets query-specific logic participate in a common alert lifecycle rather than duplicating the whole engine.

The [evaluation source directory](https://github.com/ccfos/nightingale/tree/main/alert/eval) provides a useful next step into neighboring evaluators. The criteria here are grounded in the implementation, not just the project's integration list.

### 24. [apache/hertzbeat](https://github.com/apache/hertzbeat)

**Java and TypeScript — agentless monitoring, collection scheduling, alerting, and storage integration.** Study how protocol-specific collection is organized into a shared execution pipeline.

- **C2:** Monitoring templates and collector strategies support different protocols under the same scheduling/result-handling framework. Collection can run within the manager or through separate collectors. The project's [metrics-collection architecture article](https://hertzbeat.apache.org/blog/2025/03/30/how-does-metrics-collection-work/) explains this composition.
- **C3:** Consistent hashing assigns jobs to collectors; timer dispatch, worker execution, result queues, alert handling, and storage have separate responsibilities. This provides concrete material for studying distributed assignment and queue-based concurrency.

The linked article describes the architecture in March 2025. It is a substantive design entry point, while exact module names and paths should be checked against the version being studied.

## Search coverage, exclusions, and limits

Discovery used more than twelve live search formulations, followed by repository and primary-document inspection. Distinct angles included Prometheus-compatible distributed storage; Cassandra/HBase time-series schemas; Graphite routing and retention stores; C/C++ agents and embedded storage; Rust columnar engines; Gorilla-style compression and lesser-known time-series databases; network-monitoring systems; Clojure event processing; and Java/template-driven monitoring. Follow-up searches targeted WAL recovery, object-store architectures, indexing, preprocessing queues, alert-worker lifecycle, changelogs, and mirror status. Later broad queries mainly repeated already represented families, providing diminishing returns.

Every selected repository's GitHub page was opened, and at least one additional primary document or implementation file was read. Search-result snippets alone were not used to qualify a repository. Canonical repositories are counted once; M3 and other monorepos identify their relevant subsystems. Whisper and Carbon have different implementation responsibilities, and go-carbon is a substantive alternative implementation. Mimir's Cortex lineage is explicit rather than concealed as an unrelated project.

Dashboard-only applications, instrumentation SDKs, thin exporters, awesome lists, tutorials, and generic databases without a sufficiently direct metrics/monitoring focus were outside this selection. Leads including SiriDB, Blueflood, DalmatinerDB, and CnosDB were considered but not retained with the same completed depth of primary-source verification; their omission is not a negative quality assessment. This is a broad curated guide, not an exhaustive census, and the largest distributed family represented is the Go/Prometheus ecosystem.

Maintenance is not inferred from popularity, repository age, or a recent push. Beringei is explicitly archived; Akumuli is presented as a historical design study with current maintenance unestablished; Zabbix is an official substantive GitHub mirror. Versioned and historical sources are labeled where their age materially affects interpretation. Only entries with inspected multi-year compatibility/testing evidence receive C4. No numerical performance promises are made, and no candidate code was executed or benchmarked. Links to moving branches and current documentation may change after the research date.
