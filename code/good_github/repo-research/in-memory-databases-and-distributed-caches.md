# In-memory databases and distributed caches

Research date: 2026-10-09.

This selection covers 25 repositories implementing memory-resident databases, remote cache servers, distributed data grids, and substantive cache engines or coordination libraries. Hybrid systems are included where an actual in-memory mode or subsystem is identifiable. Embedded databases and CacheLib broaden the selection to transaction and memory-management machinery that engineers can reuse when building services. Client SDKs, deployment operators, benchmark-only projects, and ordinary local memoization libraries are outside the main scope.

The criteria below describe specific reasons to study a repository, not a guarantee that every component is exemplary or suitable for a particular production workload. Architectural conclusions are grounded in the linked primary material; the selection judgments are interpretive. Repository headings link to verified canonical GitHub pages. The documentation and source links within each entry are suggested reading entry points.

- **C1 — Correctness:** nontrivial invariants, concurrency, adversarial inputs, or failure semantics.
- **C2 — Reusable abstractions:** substantial interfaces or architectural components serving multiple use cases.
- **C3 — Performance with structure:** concrete latency, throughput, allocation, or capacity constraints addressed through an understandable design.
- **C4 — Sustained evolution:** years of changes accompanied by evidence of compatibility work, testing, or complexity management; age alone does not qualify.

## RESP-compatible memory engines

### [redis/redis](https://github.com/redis/redis)

**Language / role:** C core; networked in-memory data-structure database with persistence and replication. The focus here is the core server, rather than every module now collected in the repository. It is useful for studying how a broad command surface interacts with replication history and expiration.

- **C1:** Replication identifies a history with both a replication ID and an offset. After promotion, a replica needs a new history ID while retaining a bounded reference to its previous history. Expiration also has a replication invariant: the primary propagates deletions, while replicas must avoid independently diverging the dataset. The documentation explicitly explains why `WAIT` acknowledgments do not make the system strongly consistent. [Replication design](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/).
- **C3:** The same design separates backlog-based partial resynchronization from full snapshot transfer. This makes recovery cost, retained history, and memory consumption visible architectural choices rather than incidental optimizations. The linked guide is the best starting point before tracing replication code.

### [valkey-io/valkey](https://github.com/valkey-io/valkey)

**Language / role:** C; Redis-derived in-memory data-structure server. Retained separately because the inspected Valkey 8 design documents substantive evolution in network processing and memory access.

- **C1:** Its threading design preserves single-threaded command execution while coordinating concurrent I/O workers. One explicit invariant permits only one thread to poll a shared event mechanism at a time; connection affinity and ownership transitions determine where concurrent work is safe.
- **C3:** Parsing, socket reads and writes, polling, and some memory reclamation move off the command executor. Dynamic worker activation and key prefetching address both small workloads and memory stalls. This is a concrete study in moving the performance boundary without parallelizing the entire command engine. Both criteria are explained in the project's [Valkey 8 threading deep dive](https://valkey.io/blog/unlock-one-million-rps/); its benchmark headline is not used here as an independently verified performance claim.

### [Snapchat/KeyDB](https://github.com/Snapchat/KeyDB)

**Language / role:** C/C++; Redis-derived multithreaded database and cache. Its separate execution and versioning work makes it more than a duplicate listing of the upstream codebase.

- **C1:** The MVCC design gives readers a version appropriate to their snapshot while writers create newer versions. Visibility and reclamation of no-longer-needed snapshots are central correctness concerns; a shared key/value API hides substantial version-lifetime machinery.
- **C3:** Versioned reads allow work to proceed during operations that would otherwise block readers. Studying the interaction between multithreading and snapshots is more informative than merely comparing command throughput. The [MVCC explanation](https://docs.keydb.dev/docs/mvcc/) provides the substantive starting point for both criteria. This entry credits the documented mechanism, without assuming that every command or operational mode has identical isolation behavior or making a current maintenance claim.

### [dragonflydb/dragonfly](https://github.com/dragonflydb/dragonfly)

**Language / role:** C++; independently implemented memory store exposing Redis and memcached protocols. Particularly useful for studying shard ownership, fibers, and operations spanning multiple shards.

- **C1:** A database shard is accessed by its owning thread; cross-thread work uses messages. That simple local ownership rule must coexist with coordinated multi-key commands, Lua execution, and transactions. The design describes a coordinator responsible for preserving atomic behavior across shards.
- **C3:** Connections and background activities use fibers, so waiting on fiber-aware synchronization or I/O need not stall every activity on the worker. Shared-nothing shard execution reduces shared-memory contention while leaving cross-shard coordination explicit. Read the repository's [shared-nothing architecture document](https://github.com/dragonflydb/dragonfly/blob/main/docs/df-share-nothing.md). It offers a useful map of the implementation, rather than evidence that all Redis edge cases are interchangeable.

### [microsoft/garnet](https://github.com/microsoft/garnet)

**Language / role:** C# / .NET; remote RESP cache and storage engine, including the Tsavorite storage subsystem. The most distinctive study target is global maintenance work in a concurrent store.

- **C1:** Checkpointing and index growth advance through global phases and versions. Epoch barriers govern when workers have moved beyond an old phase, and compare-and-exchange protects global transitions. Getting these boundaries wrong can invalidate a checkpoint or expose an incompletely resized index.
- **C2:** `IStateMachine`, `IStateMachineTask`, and the state-machine driver separate the phase graph from reusable work performed during transitions. This supports multiple maintenance operations through the same coordination machinery. The [Tsavorite state-machine guide](https://microsoft.github.io/garnet/docs/dev/tsavorite/state-machine) explains both the synchronization invariant and the compositional interface; it is a more revealing entry point than the server's headline protocol compatibility.

## Dedicated cache servers and service frameworks

### [memcached/memcached](https://github.com/memcached/memcached)

**Language / role:** C; bounded-memory network cache daemon. Distribution is commonly supplied by clients or proxies; the core daemon should not be mistaken for a replicated transactional data grid.

- **C1:** The protocol exposes compare-and-swap tokens and distinguishes stale-version conflicts from missing keys. The meta protocol also provides winner/loser signals for cache filling and explicit stale-value handling. These are reusable building blocks for avoiding lost updates and controlling stampedes. Read the actual [protocol specification](https://github.com/memcached/memcached/blob/master/doc/protocol.txt).
- **C3:** Slab classes partition memory pressure: a server can evict from one class even when aggregate memory statistics seem comfortable. Slab reassignment, per-class eviction metrics, and the distinction between expiration and capacity eviction make allocator policy operationally visible. The [maintenance guide](https://docs.memcached.org/serverguide/maintenance/) connects those structures to diagnosis and tuning.

### [pelikan-io/pelikan](https://github.com/pelikan-io/pelikan)

**Language / role:** Rust; framework for cache servers and proxies. This entry concerns the current Rust repository, not the separately maintained historical C implementation.

- **C2:** The architecture separates foundational crates, protocol implementations, a storage facade, runtime machinery, and thin server products. Protocol and storage interfaces permit different products to reuse the same runtime. The documented Segcache engine dependency is external; this report does not attribute that entire engine's implementation to this repository.
- **C3:** A listener hands connections to workers that perform parsing, execution, and response writing on the worker thread. Administrative signaling has a separate control path, while proxy frontends and backends have explicit queues. These boundaries make queueing and allocation costs inspectable. The detailed [architecture document](https://github.com/pelikan-io/pelikan/blob/main/docs/ARCHITECTURE.md) also explains checks intended to keep its dependency diagrams aligned with the code.

## Distributed data grids

### [oracle/coherence](https://github.com/oracle/coherence)

**Language / role:** Java; Coherence Community Edition, a distributed in-memory data grid. Study the interaction between partition ownership, backup synchronization, and application-controlled data placement.

- **C1:** With synchronous backups, modifications wait for backup acknowledgments; failover promotes backup partitions. Partition movement and recovery temporarily block affected data to preserve integrity. These are concrete availability and ownership boundaries, rather than an unconditional promise that every failure is transparent. Read the [14.1.2 cache architecture](https://docs.oracle.com/en/middleware/fusion-middleware/coherence/14.1.2/develop-applications/introduction-coherence-caches.html) and [partition lifecycle guide](https://docs.oracle.com/en/middleware/fusion-middleware/coherence/14.1.2/develop-applications/working-partitions.html).
- **C2, C3:** Map-style access supports local, distributed, and near-cache arrangements. `KeyAssociation` and `KeyAssociator` colocate related entries so processing and synchronization can stay on one owner; overly broad affinity creates uneven load. The partition guide also exposes a replaceable `PartitionAssignmentStrategy`, making placement policy a reusable interface with measurable transfer and locality costs.

The repository explicitly separates Community Edition from commercial features. Elastic Data, WAN federation, and the separate Transaction Framework are excluded from the public edition; do not infer their implementation from the broader product manuals. The repository also permits asynchronous redundancy, whose acknowledgment guarantees differ from the synchronous mode described above.

### [hazelcast/hazelcast](https://github.com/hazelcast/hazelcast)

**Language / role:** Java; distributed in-memory maps and related data-grid machinery within a broader processing platform. Focus on partition ownership, backups, and migration.

- **C1:** Backup ordering and anti-entropy address missed or reordered replication. A particularly valuable documented failure case is an operation that executes on a primary but loses its acknowledgment: retrying after a failure can repeat it. The ordinary partitioned map should not be conflated with the separate CP subsystem.
- **C3:** Serialized-key hashing determines stable partition IDs, while a partition table maps those IDs to members. Changing cluster membership can therefore migrate ownership without changing the basic key-to-partition function. The [data-partitioning architecture guide](https://docs.hazelcast.com/hazelcast/5.2/architecture/data-partitioning) explains locality, backups, migration, and indeterminate operation outcomes together. This is a deliberately versioned 5.2 architectural reference, not a claim that 5.2 is the latest release.

### [infinispan/infinispan](https://github.com/infinispan/infinispan)

**Language / role:** Java; embedded and remote data grid supporting local, replicated, distributed, and invalidation cache modes.

- **C1:** Rebalancing distinguishes read ownership from write ownership while state moves. In the documented nontransactional triangle algorithm, primary owners assign per-segment sequence numbers and backup acknowledgments go to the originator; completion must account for the required acknowledgments without losing ordering.
- **C2:** Cache managers, commands, and interceptor chains separate transaction handling, locking, persistence, and distribution. These are substantial extension boundaries across multiple cache modes, rather than a single hard-coded deployment topology.

The [architecture guide](https://infinispan.org/docs/stable/titles/architecture/architecture.html) covers both criteria and also explains state-transfer backpressure. It is a strong entry point for engineers interested in how reusable middleware abstractions coexist with an optimized replication path.

### [apache/ignite](https://github.com/apache/ignite)

**Language / role:** Primarily Java, with other language APIs; Ignite 2 distributed caches and in-memory computing. This entry is specifically scoped to the Ignite 2 generation documented below.

- **C2:** The repository combines reusable distributed cache, SQL, and compute interfaces over a common storage platform. It is useful for following how several user-facing abstractions share data placement and memory-management services. [Repository overview](https://github.com/apache/ignite).
- **C3:** The page-memory architecture stores data outside the Java heap and uses the same binary representation in memory and on disk. Page indirection and compaction manage variable-length records and fragmentation. Optional native persistence changes the capacity model: disk may hold a superset of the resident pages. Read the [Ignite 2 memory architecture](https://ignite.apache.org/docs/ignite2/latest/memory-architecture).

Consequently, this is an in-memory architecture study with an optional persistent mode, not a claim that all Ignite deployments keep their full dataset in RAM.

### [apache/geode](https://github.com/apache/geode)

**Language / role:** Java; region-based distributed in-memory data grid. Its bucket replication and operational recovery controls offer a useful comparison with hash-partitioned key/value servers.

- **C1:** When a primary bucket holder fails, a redundant copy can be promoted and redundancy rebuilt. Recovery delays and redundancy zones address different failure assumptions; multiple correlated failures can still lose data. [Partitioned-region availability design](https://geode.apache.org/docs/guide/20/developing/partitioned_regions/how_pr_ha_works.html).
- **C3:** Writes pass through a primary and synchronously reach redundant copies, whereas reads can use any available copy and favor a local one. This makes the read-locality/write-coordination tradeoff concrete in the same design document.

An additional entry point is the [testing guide](https://github.com/apache/geode/blob/develop/TESTING.md), which distinguishes distributed, integration, acceptance, and upgrade tests. It is useful evidence of how the project exercises behavior spanning processes and versions, without treating the existence of tests as proof that every recovery case is correct.

### [Alachisoft/NCache](https://github.com/Alachisoft/NCache)

**Language / role:** C# / .NET; distributed cache with application and session integrations. The scope is the published repository and documented APIs available to its open-source SDK, rather than every commercial product feature.

- **C1:** Item versions support optimistic concurrency: an update or removal can fail if another writer changed the cached item. `GetIfNewer` also separates version checking from transferring unchanged data. The guide discusses failure handling, including state-transfer and timeout errors. [Cache-item versioning guide](https://www.alachisoft.com/resources/docs/ncache/prog-guide/using-cache-item-versioning.html).
- **C2:** The [source tree](https://github.com/Alachisoft/NCache/tree/master/Src) separates cache logic, clustering, storage, runtime APIs, serialization, and socket serving, alongside application integration components. This makes the repository useful for tracing how a distributed cache API reaches transport and storage layers, and how the same cache is adapted to session and application workloads.

## Distributed maps, cache ownership, and cache filling

### [olric-data/olric](https://github.com/olric-data/olric)

**Language / role:** Go; distributed maps usable as an embedded library or a standalone RESP-speaking service. This is the canonical repository, formerly under `buraksezer/olric`.

- **C1:** The architecture combines membership, partition ownership, replication, and configurable quorum behavior, with last-write-wins/read-repair semantics. Its documented best-effort partition behavior should not be read as a consensus-backed linearizability guarantee. [Architecture and consistency discussion](https://github.com/olric-data/olric#architecture).
- **C2:** The DMap abstraction serves both embedded and remote use, exposing expiration, eviction, iteration, and coordination operations. The [integration tests](https://github.com/olric-data/olric/blob/master/integration_test.go) show those abstractions under node joins and departures, client metadata refresh, TTL and idle expiration, and bounded-cache policies.

Study it to connect an approachable Go API to membership-driven routing and realistic cache lifecycle tests. The test suite supplies concrete scenarios, not a proof of all behavior during network partitions.

### [Tencent/DCache](https://github.com/Tencent/DCache)

**Language / role:** C++; Tars-based distributed cache supporting key/value and richer collection structures, with routing and database integration components. This is Tencent's cache system, unrelated to the similarly named scientific file-storage project.

- **C1:** The proxy API exposes version conflicts, stale routing, migration-time write restrictions, and partial batch failures. Dirty data also affects deletion semantics: an erase operation can reject dirty entries, distinguishing memory removal from deletion involving backing storage. The [proxy API guide](https://github.com/Tencent/DCache/blob/master/docs/proxy_api_guide.md) makes these boundaries unusually explicit.
- **C2:** Proxy, routing, cache-server, configuration, and database-access roles separate placement from application-facing operations. Key/value and multi-key collection APIs reuse that infrastructure. The [repository architecture overview](https://github.com/Tencent/DCache) provides the component map.

This is a useful study in write-back cache semantics and migration-visible errors. The detailed API source is in Chinese; no unsupported current-maintenance claim is made.

### [alibaba/tair](https://github.com/alibaba/tair)

**Language / role:** C++; historical distributed storage/cache system. The relevant in-memory subsystem is MDB; LDB is a persistent alternative. This entry refers to the published original codebase, not the contemporary managed cloud product sharing its name.

- **C3:** MDB allocates memory in pages, reserves regions for metadata and hash buckets, and uses the remaining pages for slab allocation. The layout exposes how addressing, allocation classes, and namespace metadata fit into a fixed memory budget. Start with the source's [MDB memory-format document](https://github.com/alibaba/tair/blob/master/src/storage/mdb/format.txt).
- **C4:** The [dated ChangeLog](https://github.com/alibaba/tair/blob/master/ChangeLog) records work from 2010 through 2014, including expiration behavior, configuration validation, namespace controls, hash-distribution fixes, and quota/clearing behavior. Those concrete changes establish sustained historical evolution and complexity management; they do not establish present-day maintenance.

The ConfigServer/DataServer/client split described on the repository page adds distributed placement and migration context to the allocator study.

### [golang/groupcache](https://github.com/golang/groupcache)

**Language / role:** Go; original distributed read-through cache library. It assumes a key identifies an immutable value, so TTL and mutable-value invalidation are deliberately outside its model.

- **C1:** Concurrent fills are coalesced with singleflight. The implementation performs a second cache check inside the fill callback: sequential callbacks can otherwise repeat an already completed load and corrupt cache-byte accounting. This is a small but substantive example of concurrency correctness affecting capacity bookkeeping.
- **C3:** Consistent-hash ownership is combined with local caching of popular remotely owned values. Separate main and hot caches share a bounded byte budget; peer failure may fall back to local loading. These mechanisms are visible in [groupcache.go](https://github.com/golang/groupcache/blob/master/groupcache.go), alongside the `Group`, loader, sink, and peer abstractions.

Study this reference implementation for coordinated loading and ownership-aware caching; its semantics are intentionally narrower than a general distributed mutable database.

### [elixir-nebulex/nebulex_distributed](https://github.com/elixir-nebulex/nebulex_distributed)

**Language / role:** Elixir; distributed cache topology and coordination adapters, including partitioned and replicated arrangements. It implements distribution logic over interchangeable storage adapters, rather than merely wrapping a remote cache client.

- **C1:** The partitioned adapter uses process-group membership, a hash ring, and a ring monitor. Periodic rejoining addresses membership events that can be missed during concurrent startup. Its documentation also states that RPC timeout does not ensure the remote operation was canceled, and that this adapter supplies no replica failover.
- **C2:** Local storage adapters, routing, supervised processes, and distributed API behavior are separate components. Applications can change the storage implementation without replacing the ownership mechanism. The [partitioned adapter documentation](https://hexdocs.pm/nebulex_distributed/Nebulex.Adapters.Partitioned.html) explains the topology, supervision, and failure boundaries in detail.

This is especially useful for examining how BEAM processes and supervision support a cache whose routing state changes over time.

## Memory-resident databases and transactional stores

### [tarantool/tarantool](https://github.com/tarantool/tarantool)

**Language / role:** C/C++ with Lua; database and application runtime. The relevant subsystem is the in-memory `memtx` engine, rather than the disk-oriented Vinyl engine.

- **C1:** The optional MVCC transaction mode allows transactions to yield while version and conflict managers preserve the permitted serialization order. A detected conflict affects further operations until rollback; read views and transaction isolation are therefore part of application-visible behavior, not merely storage internals.
- **C2:** Indexed tuple spaces, Lua application logic, and interactive transactions over protocol streams make the engine usable beyond a simple GET/SET cache. The [memtx MVCC guide](https://www.tarantool.io/docs/tarantool/en/3_x/platform/atomic/txn_mode_mvcc) connects transaction semantics to cooperative execution and the client API.

This is a strong study target for engineers interested in combining an application runtime with a memory database. The existence of MVCC mode should not be taken to mean it is enabled by default in every deployment.

### [skytable/skytable](https://github.com/skytable/skytable)

**Language / role:** Rust; structured in-memory database with its own query language and durable storage machinery. The public repository inspected documents the 0.8 implementation; its notice about privately developed 0.9 clustering is not credited as public-source functionality.

- **C1:** The architecture distinguishes durability semantics by operation class: schema/control operations are described as durable, while ordinary data mutations use delayed, batched persistence. That distinction is valuable for studying what a successful response guarantees after a crash.
- **C3:** Asynchronous multithreaded networking and the SDSS append-oriented storage design connect latency to batching and persistence scheduling. Structured models and typed data add query-processing work beyond raw byte lookup. Read the [architecture guide](https://docs.skytable.io/architecture/) together with the public repository's version-scope notice.

Its value here is the inspectable memory/query/persistence design. This report makes no claim that the public code implements the newer advertised high-availability or clustering features.

### [Restream/reindexer](https://github.com/Restream/reindexer)

**Language / role:** C++ core with Go integration; indexed in-memory document database usable embedded or as a service. It adds query planning, joins, and aggregation to the memory-store category.

- **C1:** The [replication design](https://github.com/Restream/reindexer/blob/master/replication.md) describes synchronous clustering with a Raft-like algorithm and distinct asynchronous replication modes. Configuration constraints determine which namespaces may participate and how asynchronous replicas follow a synchronous cluster. These are concrete ownership and failure-management concerns; the description is not a formal consensus proof.
- **C3:** The [repository's memory-management discussion](https://github.com/Restream/reindexer) explains packed C++ representations, string deduplication, pooling, and caching of decoded Go objects. Keeping the main dataset outside Go's object graph changes both allocation and garbage-collection costs.

Study the boundary between a native indexed engine and a managed-language API, then follow how the same namespaces participate in replication.

### [erlang/otp](https://github.com/erlang/otp)

**Language / role:** Erlang; only the **Mnesia** distributed database subsystem is selected from this much larger monorepo. Memory-resident tables and transactional access make it directly relevant; OTP as a whole is not being classified as a cache.

- **C1:** Mnesia's transaction manager uses distributed locking, including read access to one replica and write locks involving replicas. Sticky locks optimize particular access patterns but introduce different ownership behavior. Dirty operations bypass transaction protections, making the chosen access context semantically important.
- **C2:** Transactional, synchronous transactional, dirty, and direct ETS access contexts let callers select different coordination and performance behavior over the database abstraction. The guide also explicitly distinguishes the durability limits of pure-memory operation. Read [transactions and other access contexts](https://www.erlang.org/doc/apps/mnesia/mnesia_chap4.html).

The verified [lib/mnesia subtree](https://github.com/erlang/otp/tree/master/lib/mnesia) is the source entry point, including the subsystem's implementation and tests. Count this monorepo once.

### [hashicorp/go-memdb](https://github.com/hashicorp/go-memdb)

**Language / role:** Go; embedded transactional in-memory database built around immutable radix-tree indexing. It supplies neither a network service nor durable storage.

- **C1:** A commit publishes the new database root atomically before notifying watchers. That ordering ensures awakened observers can see the state that triggered the notification. Snapshot safety also depends on callers respecting object immutability: mutating an already inserted object in place bypasses the database's versioning model.
- **C2:** Schema-defined tables and indexes, transactions, and watches provide reusable foundations for control-plane and application state. A single writer can coexist with readers of immutable snapshots, keeping the concurrency model understandable.

Read the transaction implementation, especially commit and insertion behavior, in [txn.go](https://github.com/hashicorp/go-memdb/blob/main/txn.go?plain=1). The small public API is valuable precisely because publication, index updates, notifications, and caller-owned object lifetimes still require careful coordination.

### [aerospike/aerospike-server](https://github.com/aerospike/aerospike-server)

**Language / role:** C; distributed record database with selectable memory and hybrid storage configurations. Category fit is the configuration placing both records and indexes in DRAM, rather than a claim that the default hybrid configuration is wholly memory-resident.

- **C1:** Cluster membership changes drive partition ownership and migration. Requests using temporarily stale client routing may be proxied, while recovery must resolve duplicate record versions. The [architecture overview](https://aerospike.com/docs/database/learn/architecture/) connects client awareness, distribution, and transaction processing.
- **C3:** Per-namespace storage selection, contiguous record representation, copy-on-write updates, and background reclamation expose explicit capacity and locality tradeoffs. The [storage architecture](https://aerospike.com/docs/database/learn/architecture/hybrid-storage/) also distinguishes Community Edition's volatile process memory from Enterprise Edition's shared-memory behavior.

That edition distinction matters when reading broader product documentation: this entry does not attribute enterprise-only restart or storage capabilities to the public server implementation.

## Reusable cache-engine machinery

### [facebook/CacheLib](https://github.com/facebook/CacheLib)

**Language / role:** C++; in-process caching engine for applications and cache services, with memory and hybrid-cache machinery. It is included as an implementation building block, not as a standalone distributed service.

- **C1:** Item reference counts and an exclusive state bit coordinate access, eviction, and slab rebalancing. Chained items add parent/child lifetime constraints and separate modification locks. Moving memory safely while clients retain handles is the central invariant, not simply choosing an eviction policy.
- **C3:** Slab movement and rebalancing recover usable cache capacity without invalidating live references. The design spells out the race cases and synchronization paths that constrain this work. Read [synchronization in eviction and slab rebalancing](https://cachelib.org/docs/Cache_Library_Architecture_Guide/synchronization_in_eviction_and_slab_rebalancing/).

The repository also contains CacheBench tooling for exercising cache behavior. The source is especially useful for engineers implementing bounded-memory services where allocation, replacement policy, and concurrent object ownership cannot be designed independently.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, followed by opening canonical repository pages and independent primary documents or source files for every retained entry. The main search angles were:

- Redis/RESP engines, multithreading, MVCC, and shared-nothing implementations.
- Memcached-compatible servers, cache frameworks, slab allocation, and cache-engine libraries.
- Java data grids, backup ordering, partition migration, off-heap memory, and upgrade testing.
- Go distributed maps, consistent hashing, read-through loading, and embedded transactions.
- Rust memory databases, typed query models, and asynchronous durability.
- Erlang/Elixir memory tables, distributed locking, supervision, and topology adapters.
- C++ systems from Tencent and Alibaba, including Chinese API documentation and historical changelogs.
- .NET distributed caches and storage engines, plus databases offering explicit all-memory and hybrid modes.

Later queries increasingly returned already inspected projects, small local cache libraries, tutorials, protocol clients, or duplicate derivatives. The list therefore stops at 25 substantive repositories rather than filling a larger quota. Follow-up verification resolved temporary repository-loading failures for Oracle Coherence and added its partition ownership and data-affinity design. Valkey and KeyDB are explicitly identified as Redis-derived projects and retained for separately documented architectural evolution. Monorepos are counted once, and embedded subsystems are named. No star counts or unverified numerical speed claims support selection.

Ordinary LRU/memoization libraries such as Caffeine and Ristretto were left outside this report's main distributed/database scope; CacheLib is the explicit service-engine exception. Disk-first systems without a clear memory-resident database role, wrappers, operators, awesome-lists, and the unrelated dCache file-storage system were excluded.

Tair is intentionally a historical study. Groupcache is presented with its original, narrow immutable-key model. Skytable's publicly inspectable implementation is distinguished from its newer private development. Versioned Hazelcast and Ignite references identify the generation studied; moving branch links and unversioned documentation can change after this research date. Product documentation can span commercial and community editions, so the NCache and Aerospike entries restrict their claims accordingly. No blanket claim of present maintenance is made for this collection, and no repository code was installed, cloned, or executed. This is a source-backed selection guide, not an independent correctness audit or benchmark.
