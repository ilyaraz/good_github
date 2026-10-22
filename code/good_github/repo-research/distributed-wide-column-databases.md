# Distributed wide-column databases

Research date: 2026-10-09.

This selection covers distributed databases with Bigtable-style sparse, versioned cells or Cassandra-style partitioned, clustered rows. It includes eleven repositories: core engines, substantive integrations, and one explicitly identified alpha implementation of replicated wide-column storage. A multimodel repository is included only for its relevant subsystem. Analytical column stores, embedded engines that merely offer column families, clients, and applications built on these databases are outside the scope.

The criteria describe useful engineering study opportunities, not a certification of every component or a recommendation to deploy every project:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial inputs, or failure and recovery semantics.
- **C2 — Abstractions:** substantial reusable interfaces or components serving multiple use cases.
- **C3 — Performance:** concrete resource constraints addressed through understandable architecture.
- **C4 — Evolution:** years of change accompanied by compatibility, testing, or complexity management.

Repository identities, default branches, archival flags, and push timestamps were checked through the public GitHub API. A recent push is evidence of repository activity, not a support guarantee. Sources below were opened and read; paths refer to the inspected branches and can change.

## Core Cassandra and Bigtable families

### 1. [apache/cassandra](https://github.com/apache/cassandra)

**Language/role:** Java; partitioned wide-column database. Official Apache source repository, with October 2026 activity.

Study how a partitioned row abstraction interacts with independently writable replicas, placement across failure domains, and repair. The [Dynamo architecture chapter](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html) explicitly identifies the wide-column interface and explains the distinction between partition keys, clustering keys, and per-column mutation timestamps.

- **C1:** Timestamp reconciliation, quorum overlap, hinted handoff, and Merkle-tree repair address different parts of replica convergence. The chapter explains why best-effort read repair and hints do not replace anti-entropy repair, and how simultaneous range movements can violate consistency.
- **C2:** Replication strategies separate placement policy from the storage model; keyspaces configure replication while CQL exposes typed rows and collections. This is useful for studying how policy is made configurable without exposing the entire storage protocol to callers.
- **C3:** Virtual nodes improve incremental balancing but introduce more repair work and failure combinations. The documented tradeoff is more instructive than a generic scalability claim.

**Entry points:** [replication and partitioning architecture](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html); [main source tree](https://github.com/apache/cassandra/tree/trunk/src), linked from the verified repository root. The architecture chapter is versioned documentation; it should not be read as a complete description of every newer transaction feature on `trunk`.

### 2. [scylladb/scylladb](https://github.com/scylladb/scylladb)

**Language/role:** C++; independent Cassandra-compatible engine built on Seastar. Public source with October 2026 activity; the repository carries a [ScyllaDB source-available license](https://github.com/scylladb/scylladb/blob/master/LICENSE-ScyllaDB-Source-Available.md).

Study a wide-column engine whose read admission, memory management, and asynchronous execution are explicit architectural concerns.

- **C1:** The [Raft integration design](https://github.com/scylladb/scylladb/blob/master/docs/dev/raft-in-scylla.md) explains why a committed log alone does not make schema updates safe: concurrent proposals and uncertain outcomes need state identifiers, read barriers, and idempotent application. This document includes historical implementation stages, rather than a guarantee that all data replication uses Raft.
- **C2:** That design separates persistence, RPC, and client state-machine interfaces, allowing the consensus library to be instantiated for different purposes.
- **C3:** The [reader concurrency semaphore](https://github.com/scylladb/scylladb/blob/master/docs/dev/reader-concurrency-semaphore.md) balances CPU/I/O utilization against transient memory and cancellable queued work. Inactive-reader eviction also prevents deadlock when operations need permits on multiple shards.

**Entry points:** the two design documents above; follow their named interfaces into the implementation. The semaphore's admission states and diagnostics provide a particularly concrete route into overload behavior.

### 3. [apache/hbase](https://github.com/apache/hbase)

**Language/role:** Java; distributed Bigtable-style database with column families, mutable qualifiers, and timestamped cells. Official Apache source repository, with October 2026 activity.

The [data-model documentation](https://hbase.apache.org/docs/datamodel/) makes its category fit precise: rows are lexicographically ordered, qualifiers can differ between rows, and storage settings are attached to column families. Study how these semantics survive compaction and distributed administration.

- **C1:** Version and deletion behavior is subtle: the documentation discusses timestamp collisions, delete markers, and an alternate version-accounting mode intended to keep major compaction from changing results. These are observable database semantics rather than implementation trivia.
- **C2:** The [Procedure Framework](https://hbase.apache.org/docs/pv2/) turns operations on tables and regions into persisted state machines, with subprocedures, suspension, retries, and rollback. Its executor/store separation is reusable across administrative operations.
- **C1, additionally:** Procedure steps may run repeatedly after failure; the guide requires idempotence and describes restoring executor state from the procedure store. It also candidly identifies framework complexity and incomplete hardening.

**Entry points:** [data model and deletion semantics](https://hbase.apache.org/docs/datamodel/); [Procedure Framework implementation guide](https://hbase.apache.org/docs/pv2/). These current multipage guides supersede the site's explicitly marked legacy single-page manual.

### 4. [apache/accumulo](https://github.com/apache/accumulo)

**Language/role:** Java; Bigtable-inspired sorted distributed store with column families, qualifiers, timestamps, and cell visibility labels. Official Apache source repository, with October 2026 activity.

Study the combination of extensible server-side computation and access control over sorted cells. The [design guide](https://accumulo.apache.org/docs/2.x/getting-started/design) explains tablet ownership, WAL replay, merged reads from memory and RFiles, and locality groups.

- **C1:** [Visibility expressions](https://accumulo.apache.org/docs/2.x/security/authorizations) attach authorization conditions to individual values. Scanner authorizations must be a subset of the user's permissions, while values failing the expression are suppressed. This makes filtering correctness part of the confidentiality boundary.
- **C2:** [SortedKeyValueIterator](https://accumulo.apache.org/docs/2.x/development/iterators) is more than a forward iterator: seek ranges, deep copies, composition, and execution context support custom filters and computation during scans or compaction.
- **C1, additionally:** Iterator contracts expose real pitfalls: emitting outside the supplied range can duplicate results across tablets, and retaining reused key/value objects can silently corrupt an iterator's logic.

**Entry points:** [iterator development guide](https://accumulo.apache.org/docs/2.x/development/iterators); [authorization semantics](https://accumulo.apache.org/docs/2.x/security/authorizations). These are the documented 2.x contracts; the repository's main branch also contains newer development.

## Additional independent implementations

### 5. [baidu/tera](https://github.com/baidu/tera)

**Language/role:** C++; Bigtable-inspired sparse multidimensional tables, with an enhanced LevelDB engine and pluggable distributed filesystems. **Historical study candidate:** not archived, but the API reported its latest push as June 2024.

The repository's architecture separates SDK, master, and tablet servers. It is especially useful for studying multi-locality-group row semantics and caching over remote storage, rather than treating LevelDB as an opaque dependency.

- **C1:** The [read/write consistency design](https://github.com/baidu/tera/blob/master/doc/read_write_consistency.md) explains atomic updates across a row's locality groups using a shared WAL. Temporary snapshots keep readers from observing a partially updated row and keep old versions alive during reads.
- **C3:** The [persistent-cache design](https://github.com/baidu/tera/blob/master/doc/persistent_cache.md) addresses finite SSD capacity, file-level LRU eviction, heterogeneous disks, invalid cached blocks, and reference-aware deferred deletion. It connects capacity accounting to concrete cache interfaces and placement policy.
- **C2:** The same cache design separates the cache interface, metadata, individual disk implementation, and sharded cache, making the abstraction boundaries inspectable.

**Entry points:** the two design documents above. Much of the most valuable internal documentation is in Chinese; the repository also supplies English SDK material.

### 6. [kashirin-alex/swc-db](https://github.com/kashirin-alex/swc-db)

**Language/role:** C++; independent distributed wide-column engine with variable-length composite cell keys. Repository activity was observed in August 2026.

Its [technical introduction](https://github.com/kashirin-alex/swc-db/blob/master/docs/README.md) describes a different modeling choice: columns and tagged column selection replace conventional tables/namespaces, while keys consist of ordered “fractions” plus versions. It explicitly documents how ordinary wide-column row/family/qualifier structures map into this model.

- **C2:** Configurable key sequences, comparators, scan intervals, and a filesystem base interface support different ordering and storage needs without requiring a separate engine per model.
- **C3:** Master/meta/data range hierarchies and range metadata narrow scans before reaching data ranges. CellStores and commit-log fragments separate compacted storage from recent updates.
- **C1:** Ranger reassignment, stale cached locations, and single-cell versus multicell atomicity are explicit documented concerns. The [changelog](https://github.com/kashirin-alex/swc-db/blob/master/CHANGELOG.md) records concrete fixes for Ranger state synchronization, initialization order, and a BlockLoader use-after-free risk.

**Entry points:** [technical introduction](https://github.com/kashirin-alex/swc-db/blob/master/docs/README.md); [changelog](https://github.com/kashirin-alex/swc-db/blob/master/CHANGELOG.md). Replication depends on the selected filesystem, and the documentation does not promise atomic multicell writes. Its very large capacity and performance claims were not independently validated and are not used as selection evidence.

### 7. [hypertable/hypertable](https://github.com/hypertable/hypertable)

**Language/role:** C++; distributed Bigtable-style database with RangeServers, versioned sparse cells, access groups, and a filesystem broker. **Historical:** latest reported push December 2018. GitHub marks this project repository as a fork of `nuggetwheat/hypertable`; it is counted once, as the project distribution identified by its own README.

The [2012 architecture white paper](https://hypertable.com/collateral/whitepaper-hypertable-architecture.pdf) provides a readable route from the data model to the implementation.

- **C1:** The documented write path orders log synchronization, insertion into the CellCache, and acknowledgment. The [CommitLog interface](https://github.com/hypertable/hypertable/blob/master/src/cc/Hypertable/Lib/CommitLog.h) exposes log linking, rolling, and purging by revision plus safe-removal sets—useful recovery and retention invariants to trace.
- **C3:** Access groups colocate selected columns to reduce I/O; merge scanners combine memory and disk runs; memory allocation shifts between write buffers and read caches according to workload. These mechanisms are explained in the architecture paper.
- **C4:** The [release history](https://github.com/hypertable/hypertable/blob/master/CHANGES) documents subsequent evolution through 2016, including log compatibility repairs, recovery bugs, encoding changes, and migration to C++11 concurrency primitives.

**Entry points:** [architecture paper](https://hypertable.com/collateral/whitepaper-hypertable-architecture.pdf); [CommitLog header](https://github.com/hypertable/hypertable/blob/master/src/cc/Hypertable/Lib/CommitLog.h). The paper describes its contemporary implementation; later code and release notes take precedence for details.

### 8. [gruter/cloudata](https://github.com/gruter/cloudata)

**Language/role:** Java; historical independent Bigtable-style distributed store. **Archived on 2024-02-29**, with latest reported push in March 2011. The checked-in [data-model document](https://github.com/gruter/cloudata/blob/master/doc/datamodel.html) defines sparse tables, ordered row and cell keys, and multiple timestamped cell versions.

Study a compact historical cluster implementation that separates master, tablet service, and commit-log service. Its [components document](https://github.com/gruter/cloudata/blob/master/doc/components.html) explains tablet assignment and reassignment while keeping ordinary data service separate from master availability.

- **C1:** The [commit-log failure tests](https://github.com/gruter/cloudata/blob/master/src/unit_test/org/cloudata/core/commitlog/TestCommitLogServerFailure.java) start separate server processes, stop a server, inject connection death/delay faults, and assert expected failures and written lengths. They expose the system's failure assumptions directly.
- **C2:** Tablets provide the unit of distribution and balancing, while separately addressed column/cell/version structures provide a reusable ordered-data API. These boundaries can be followed from the component and data-model documents into client and tablet-server packages.

**Entry points:** [component architecture](https://github.com/gruter/cloudata/blob/master/doc/components.html); [failure-injection test source](https://github.com/gruter/cloudata/blob/master/src/unit_test/org/cloudata/core/commitlog/TestCommitLogServerFailure.java). Some test methods are empty or explicitly unfinished; the presence of fault injection does not establish comprehensive coverage or present-day readiness.

## Substantial integrations and another replication model

### 9. [strapdata/elassandra](https://github.com/strapdata/elassandra)

**Language/role:** Java; Cassandra distribution integrating Elasticsearch as a secondary-index engine. This is a substantive integration, not an independent replacement storage engine. Repository activity was observed in May 2026; the inspected default branch is `v6.8.4-strapdata`.

Study how a distributed wide-column database supplies durability, placement, and metadata coordination to a search engine. The [branch's architecture document](https://github.com/strapdata/elassandra/blob/v6.8.4-strapdata/docs/elassandra/source/architecture.rst) maps search indices/types to Cassandra keyspaces/tables and describes indexing on each replica.

- **C1:** Cassandra commit-log replay reconstructs unflushed search-index updates, permitting the integration to disable Elasticsearch's separate translog. Concurrent mapping changes use Paxos-backed metadata versioning and batched schema changes. Both require correctness across component boundaries.
- **C2:** A secondary-index bridge and field-to-CQL mappings expose search and wide-column access to the same stored data, including nested documents represented with Cassandra types.
- **C3:** Search uses token-range filtering to avoid duplicate replica results; a per-Lucene-segment bitset cache reduces repeated filtering work, and an alternate routing strategy selects nodes covering the ring.

**Entry points:** [architecture](https://github.com/strapdata/elassandra/blob/v6.8.4-strapdata/docs/elassandra/source/architecture.rst); the [repository README](https://github.com/strapdata/elassandra) for branch-specific upgrade cautions. Findings apply to the inspected Elasticsearch-based line, not automatically to separately surfaced OpenSearch-port documentation.

### 10. [yugabyte/yugabyte-db](https://github.com/yugabyte/yugabyte-db)

**Language/role:** C/C++ with Java components/tests; a multimodel distributed database, included specifically for **YCQL and its DocDB integration**. The repository also contains the PostgreSQL-compatible YSQL system, which is not the reason for inclusion. October 2026 repository activity was verified.

The [YCQL feature guide](https://docs.yugabyte.com/stable/explore/ycql-language/) identifies its Cassandra Query Language roots and the shared distributed storage layer. It is a useful counterpoint to Cassandra: a similar application-facing family of tables and operations is implemented over different replication semantics.

- **C1:** The guide documents Raft-backed strong replica consistency, distributed transactions, and immediately consistent secondary indexes. Study how those guarantees are attached to a CQL-derived interface rather than assuming Cassandra's consistency model transfers unchanged.
- **C2:** YCQL translates keyspaces, tables, typed values, expressions, and JSONB operations onto DocDB. The query-layer/server split makes API compatibility and reusable distributed storage separate engineering concerns.

**Entry points:** [YCQL feature and compatibility guide](https://docs.yugabyte.com/stable/explore/ycql-language/); [CQL query-layer source](https://github.com/yugabyte/yugabyte-db/tree/master/src/yb/yql/cql/ql). This is a subsystem selection within one monorepo, not an additional independent repository for each API.

### 11. [ankur-anand/unisondb](https://github.com/ankur-anand/unisondb)

**Language/role:** Go; multimodel storage engine with replicated wide-column rows and edge readers. **Alpha**, as marked in the inspected README; latest reported push September 2026. Included for a distinct WAL-streaming/B+Tree design, not as evidence of maturity comparable to the long-established engines above.

The [current README](https://github.com/ankur-anand/unisondb/blob/main/README.md) describes dynamic columns, partial column-family updates, and replication of changed columns. Writes originate at a write server, while replicas/relayers consume the log using gRPC or object storage.

- **C1:** [Replication regression tests](https://github.com/ankur-anand/unisondb/blob/main/pkg/replicator/replicator_regression_test.go) verify that resuming at the log tail does not resend the resume record, a new append wakes the waiting replica, and racing cancellation against delivery never publishes released/nil records.
- **C3:** Column-level replication avoids retransmitting unchanged row contents. Immutable WAL publication to object storage changes fan-out costs, while B+Tree backends and the WAL/memtable layer separate read storage from update propagation.
- **C2:** The README documents interchangeable BoltDB and LMDB backends and a shared engine serving key/value, wide-column, and large-object operations.

**Entry points:** [architecture sections in the README](https://github.com/ankur-anand/unisondb/blob/main/README.md); [replication regression tests](https://github.com/ankur-anand/unisondb/blob/main/pkg/replicator/replicator_regression_test.go). Search-indexed text mentioned optional Raft writers, but the directly fetched current README did not; this report therefore makes no Raft-writer or multi-writer guarantee.

## Search coverage and limitations

Discovery used more than six distinct live query formulations, including the following angles:

- Broad distributed wide-column families and Cassandra/HBase/Accumulo alternatives.
- Independent Bigtable implementations, including Tera, Hypertable, and Cloudata.
- C++ range-server/storage-engine architecture and historical distributed stores.
- Cassandra/search integration and Elassandra's distinct evolution.
- Exclusion queries removing the famous projects to surface SWC-DB and smaller implementations.
- Go/Rust implementations and replicated edge storage, followed by UnisonDB source and regression-test inspection.
- CQL-compatible multimodel systems, with YCQL checked as an identified subsystem.

The later broad queries mostly returned clients, educational projects, embedded engines, and analytical databases. RocksDB, Fjall, and FrostDB were not included merely because of column-family or wide-column terminology: that alone does not establish a distributed wide-column database. ClickHouse, Kudu, and similar analytical column-oriented systems were not used to expand this category. Google Bigtable and hosted Cassandra-compatible services were not substituted with their client libraries because their server implementations are not available as comparable public GitHub repositories. New multimodel candidates whose search material only advertised a wide-column endpoint were not promoted without adequate subsystem evidence.

The result spans Java, C++, C/C++, and Go; master/tablet systems, independently writable replica systems, consensus-backed CQL storage, search integration, and streaming replica trees. Eleven entries are sufficient for this narrow category without treating storage clients or every Cassandra fork as separate engines. The historical projects are deliberately retained for contrasting architecture, with their age and archival status made explicit. Some older hosted documentation failed to load; checked-in documentation/source and Hypertable's accessible official PDF supplied the evidence instead. No repositories were cloned, built, or benchmarked, and documented performance mechanisms are distinguished from unverified scale claims.
