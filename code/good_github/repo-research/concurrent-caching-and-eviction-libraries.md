# Concurrent caching and eviction libraries

Research date: **2026-10-09**.

This report selects 26 GitHub repositories implementing reusable caches, eviction policies, or substantial coordination of concurrent cache loads. The emphasis is on bounded application caches: maintaining an index alongside replacement metadata, controlling contention, preserving entry lifetimes, coordinating expiration and loading, and managing memory or storage costs. Embedded peer-aware and disk-backed libraries are included; standalone cache servers, CPU-cache research, cache simulators, and thin backend adapters are outside the main scope. Guava and oneTBB are counted once each, specifically for their cache subsystems.

Canonical repository identities, default branches, and archive flags were checked through the GitHub API. None of the selected repositories was marked archived at inspection. That is not a claim of active maintenance: relevant development limitations and older activity are identified below. Source links generally follow the verified default branch and can change after this research date. Architectural descriptions are grounded in opened primary sources; judgments about what an engineer can learn are the researcher's synthesis, not independent correctness or benchmark certifications.

**Criteria legend**

- **C1:** Difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes.
- **C2:** Substantial reusable abstractions supporting multiple use cases.
- **C3:** Real performance constraints addressed through an understandable architecture.
- **C4:** Sustained evolution with concrete compatibility, testing, or complexity-management evidence; age alone does not qualify.

## JVM: replacement metadata, loading, and storage tiers

### [ben-manes/caffeine](https://github.com/ben-manes/caffeine)

**Java — concurrent in-memory loading and eviction library.** A strong starting point for studying how a concurrent map and an eviction policy can have different synchronization requirements. Its design separates immediate map operations from buffered policy maintenance and combines recency with frequency-based admission.

- **C1:** Entries pass through alive, retired, and dead states to tolerate reordered maintenance events. The design distinguishes lossy access observations from write events that must be retained, and discusses defending frequency estimates against collision-driven admission starvation.
- **C3:** Striped read buffers, a bounded write queue, batched maintenance, a hierarchical timer wheel, and adaptive Window TinyLFU explain where throughput and memory savings come from. These are concrete tradeoffs rather than a blanket lock-free claim.

Entry point and evidence: the [design guide](https://github.com/ben-manes/caffeine/wiki/Design), especially buffering, entry states, and eviction. The [repository overview](https://github.com/ben-manes/caffeine#cache) establishes the loading, expiration, reference-strength, and integration surface.

### [cache2k/cache2k](https://github.com/cache2k/cache2k)

**Java — loading cache with a CLOCK-Pro-derived replacement engine.** Particularly useful for comparing a clock-based implementation with the more common TinyLFU family.

- **C1:** `ClockProPlusEviction` maintains hot and cold cyclic lists plus a separate ghost index. Its integrity checks reconcile list lengths, ghost counts, and linked-list structure, making the representation invariants explicit.
- **C3:** Ghosts store hashes instead of key references, ghost storage is capped, and scanning ages hit counters rather than requiring exact recency maintenance on every access. Source comments explain changes across several algorithm versions.
- **C2:** A separate API module and the deliberate distinction between loading `get` and non-loading `peek` show how public semantics are kept independent of the engine.

Entry points: [ClockProPlusEviction](https://github.com/cache2k/cache2k/blob/master/cache2k-core/src/main/java/org/cache2k/core/eviction/ClockProPlusEviction.java) and [design rationale](https://github.com/cache2k/cache2k/blob/master/src/site/markdown/design.md). [API metadata](https://api.github.com/repos/cache2k/cache2k) reported its last push in July 2025; this selection does not assert a current release cadence.

### [ehcache/ehcache3](https://github.com/ehcache/ehcache3)

**Java — tiered caching library with heap, off-heap, disk, and clustered configurations.** Study the distinction between an authoritative store and faster caching tiers, including the costs introduced by serialization.

- **C1:** Writes reach the authoritative tier and invalidate higher tiers. The documentation explains why disk and clustered persistence cannot be combined, why a persistence directory belongs to one cache manager, and why an unclean shutdown causes disk contents to be discarded rather than trusted.
- **C2:** Typed cache configuration and resource-pool abstractions support multiple storage combinations through one API.
- **C3:** Disk segmentation trades concurrency against open resources; off-heap storage trades serialization work against garbage-collection pressure. Tier capacities and object-size accounting have explicit operational consequences.

Entry point and evidence: [tiering options and operation flows](https://www.ehcache.org/documentation/3.11/tiering.html). Persistence here is a cache lifecycle feature, not a general crash-durable database guarantee.

### [google/guava](https://github.com/google/guava)

**Java — the `com.google.common.cache` subsystem of the Guava monorepo.** Useful as a comparison with Caffeine: the cache incorporates its own segmented hash-table machinery instead of merely decorating a modern concurrent map.

- **C1:** `LocalCache` documents concurrent reads, segment-serialized writes, reference strengths, expiration, and the weaker synchronization of replacement bookkeeping. Bounding is best effort per segment, so it should not be interpreted as globally exact LRU.
- **C2:** `Cache`, `LoadingCache`, loaders, weighers, removal listeners, and map views expose reusable behaviors with carefully different population semantics.
- **C3:** Read observations are queued and applied in batches; eviction operates within segments to limit contention and implementation complexity.

Entry points: [LocalCache's architectural comments and implementation](https://github.com/google/guava/blob/master/guava/src/com/google/common/cache/LocalCache.java) and [CachesExplained](https://github.com/google/guava/wiki/CachesExplained). Only this subsystem is being evaluated, not every Guava utility.

## Go: admission policies, allocation costs, and expiration

### [dgraph-io/ristretto](https://github.com/dgraph-io/ristretto)

**Go — concurrent, cost-bounded cache using TinyLFU admission and sampled LFU eviction.** Study the API consequences of decoupling writes and policy work through queues.

- **C1:** `Set` reports whether an insertion reached its buffer, but an accepted new insertion can still be rejected by admission. `Wait` drains preceding buffered work; updates change the stored value and expiration immediately while policy accounting can lag. These distinctions matter for tests and callers expecting read-after-write behavior.
- **C3:** Access batching, buffered writes, sampled victim selection, and custom entry costs address contention and the economics of retaining differently sized values.
- **C2:** Generic keys and values, configurable cost calculation, TTL, and separate rejection/eviction/exit callbacks support more than a simple entry-count map.

Entry points: [cache.go](https://github.com/dgraph-io/ristretto/blob/main/cache.go) and the [documented admission and buffering tradeoffs](https://github.com/dgraph-io/ristretto#faq). The outcaste fork is not counted separately.

### [maypok86/otter](https://github.com/maypok86/otter)

**Go — concurrent cache with loading, expiration, and adaptive Window TinyLFU.** Its current design is useful for studying how Caffeine-like ideas translate into goroutines and Go synchronization; older descriptions of its eviction policy may describe a different version.

- **C1:** Entry state transitions reconcile map changes with eventual policy updates. Writes must survive buffering, while read observations may be dropped. Producers can assist maintenance when an executor cannot make progress, addressing a real liveness problem.
- **C3:** The design combines a concurrent hash table, dynamically striped read buffers, chunked write buffering, timer-wheel expiration, and adaptive admission. It also explains generated entry layouts and the memory-versus-binary-size tradeoff.

Entry point and evidence: [current design documentation](https://github.com/maypok86/otter/blob/main/docs/performance/design.md). The [repository overview](https://github.com/maypok86/otter/blob/main/README.md) describes the configurable loading and refresh API. Do not infer strict policy ordering from thread-safe map operations.

### [allegro/bigcache](https://github.com/allegro/bigcache)

**Go — sharded byte-oriented cache designed to reduce garbage-collector scanning.** A useful study in changing data representation, not just changing an eviction algorithm.

- **C1:** A shard keeps its hash index and byte queue synchronized under a read/write lock. Deletion rechecks state after switching from a read lock to a write lock; expiration logic guards against unsigned subtraction when the clock moves backwards. Lookups verify the stored key after hashing.
- **C3:** Pointer-free hash indexes and packed byte storage reduce the object graph visible to GC. The queue can reclaim old entries when space is exhausted, while optional size limits and preallocation expose practical memory choices.

Entry points: [shard.go](https://github.com/allegro/bigcache/blob/main/shard.go) and [representation and collision notes](https://github.com/allegro/bigcache#how-it-works). Hash collisions can overwrite prior entries; ordinary `Get` and expiration reporting/cleanup must not be assumed to provide identical freshness semantics. The README's precise index type can lag the source.

### [coocood/freecache](https://github.com/coocood/freecache)

**Go — preallocated segmented byte cache with approximate LRU and expiration.** Compare its custom index and fixed storage with BigCache's growable byte-queue approach.

- **C1:** Packed entry headers, ring-buffer offsets, slot indexes, and relocation must stay consistent during eviction. `segment.set` explicitly repeats an index lookup when evacuation changes the slot, and handles value growth and oversized-entry rejection.
- **C3:** Per-segment locking limits contention, while byte buffers and index slices avoid one heap object per entry. Approximate recency and second-resolution expiration reduce bookkeeping at the cost of exactness and timing precision.

Entry points: [segment.go](https://github.com/coocood/freecache/blob/master/segment.go) and [memory layout and expiration caveats](https://github.com/coocood/freecache#how-it-is-done). Treat the README's “zero GC overhead” wording as motivation for its representation, not a measured universal guarantee for an application.

### [Yiling-J/theine-go](https://github.com/Yiling-J/theine-go)

**Go — adaptive admission cache with loading and an experimental secondary-cache interface.** Especially instructive where buffered policy events intersect with object reuse.

- **C1:** The README documents the risk of applying an asynchronous policy event to a pooled entry that has already been reused. Entry pooling became opt-in. The store has distinct shard and policy locks, and separate duplicate-load suppression for source loading and secondary-cache reads.
- **C2:** Simple/loading caches, weighers, removal listeners, persistence, and the secondary-cache interface provide substantial customization. The secondary tier receives memory evictions; it is not automatically the authoritative remote tier.
- **C3:** Sharding, buffered policy work, a frequency sketch, and a timer wheel divide the fast path from replacement and expiration work.

Entry points: [store implementation](https://github.com/Yiling-J/theine-go/blob/main/internal/store.go) and [entry pooling, persistence, and secondary-cache documentation](https://github.com/Yiling-J/theine-go/blob/main/README.md). Persistence compatibility across library upgrades is explicitly not guaranteed. [API metadata](https://api.github.com/repos/Yiling-J/theine-go) last showed a September 2025 push; current maintenance frequency is not established here.

### [hashicorp/golang-lru](https://github.com/hashicorp/golang-lru)

**Go — generic fixed-size LRU cache and related variants.** A smaller, readable reference for the costs and guarantees of exact recency maintenance.

- **C1:** A hit requires an exclusive lock because it changes recency, whereas `Peek` and `Contains` can use read locks. Compound `ContainsOrAdd` and `PeekOrAdd` operations avoid check-then-act races. Eviction callbacks are buffered during mutation and invoked after releasing the outer lock.
- **C2:** Generic keys/values, eviction hooks, resizing, non-promoting reads, and an expirable variant provide a reusable package rather than a demonstration of a linked list.

Entry points: [synchronized lru.go wrapper](https://github.com/hashicorp/golang-lru/blob/main/lru.go) and [package examples](https://github.com/hashicorp/golang-lru#golang-lru). The code acknowledges Groupcache ancestry, but its independently developed generic public library is distinct from Groupcache's distributed loading system; this is not a second listing of an unmodified fork.

### [jellydator/ttlcache](https://github.com/jellydator/ttlcache)

**Go — synchronized cache organized around per-item expiration, LRU capacity, and optional cost limits.** A good contrast with timing-wheel caches.

- **C1:** Each item participates in the map, recency list, and expiration heap. Heap swaps update item indexes; updates can change the earliest deadline and notify the cleaner through a carefully drained buffered channel. The code explains the race being avoided when sending timer updates.
- **C2:** Loader interfaces, a duplicate-suppressing loader wrapper, touch controls, event subscriptions, and explicit cleaner lifecycle give applications control over loading and expiry.
- **C3:** An indexed expiration heap supports updating/removing individual deadlines, while a separate LRU list supports capacity eviction without scanning all entries for each decision.

Entry points: [cache coordination and loader implementation](https://github.com/jellydator/ttlcache/blob/v3/cache.go) and [expiration_queue.go](https://github.com/jellydator/ttlcache/blob/v3/expiration_queue.go). The verified default branch is `v3`. Automatic cleanup must be started explicitly.

### [golang/groupcache](https://github.com/golang/groupcache)

**Go — embedded peer-aware loading cache with local LRU storage.** Retained as an older reference implementation for distributed miss coordination, not as a mutable general-purpose cache server.

- **C1:** Singleflight suppresses concurrent loads; peer failures fall back to local loading. The API deliberately requires a key to identify an unchanging value, eliminating an entire invalidation problem. It attempts, but does not guarantee, one load across the whole peer set.
- **C3:** Separate main and hot caches allow popular remote-owned values to be replicated locally, reducing network hotspots. Local synchronized LRU wrappers track key/value bytes and evict to a shared budget.

Entry points: [loading protocol and immutability restriction](https://github.com/golang/groupcache#loading-process) and [groupcache.go](https://github.com/golang/groupcache/blob/master/groupcache.go). Capacity eviction exists internally despite the absence of an explicit public eviction API or TTL. [API metadata](https://api.github.com/repos/golang/groupcache) showed a November 2024 last push; no active-maintenance claim is made.

## Rust: ownership, guards, and concurrent policy maintenance

### [moka-rs/moka](https://github.com/moka-rs/moka)

**Rust — synchronous and asynchronous concurrent caches with weighted eviction and expiration.** Study the relationship between Rust ownership and a cache whose values may disappear concurrently.

- **C1:** Retrieval returns a cloned value rather than a borrowed reference, because another thread can replace or remove the entry. The changelog documents a concrete map/policy race that left orphaned LRU nodes, as well as timer-wheel and expiration fixes: useful examples of the invariants such a design must preserve.
- **C2:** Sync and future-aware APIs, atomic initialization, configurable weights, expiration policies, and eviction listeners cover varied application patterns.
- **C3:** A concurrent hash table is bounded on a best-effort basis. The migration guide explains the removal of background threads and the resulting maintenance and async API changes.

Entry points: [sync Cache implementation and API rationale](https://github.com/moka-rs/moka/blob/main/src/sync/cache.rs) and [migration guide](https://github.com/moka-rs/moka/blob/main/MIGRATION-GUIDE.md). The specific correctness history is recorded in the [changelog](https://github.com/moka-rs/moka/blob/main/CHANGELOG.md).

### [arthurprs/quick-cache](https://github.com/arthurprs/quick-cache)

**Rust — sharded concurrent cache using S3-FIFO, with synchronous and asynchronous loading guards.** The main study value is a relatively compact design that still confronts cancellation and waiter lifetimes.

- **C1:** A missing value can be represented by a shared placeholder. Waiter registration must hold the shard lock to avoid joining an orphaned placeholder; unsafe waiter pointers are justified by stack/pinned-future lifetime and removal rules.
- **C2:** Weighting, lifecycle hooks, pinning, atomic entry operations, and non-blocking methods let callers choose loading and contention behavior.
- **C3:** Independently locked shards and no background thread reduce coordination overhead. The capacity tradeoff is explicit: each shard has its own weight allowance, which can produce uneven utilization.

Entry points: [sync cache and shard-capacity contract](https://github.com/arthurprs/quick-cache/blob/master/src/sync.rs) and [placeholder/guard machinery](https://github.com/arthurprs/quick-cache/blob/master/src/sync_placeholder.rs). The [README](https://github.com/arthurprs/quick-cache#quick-cache) identifies S3-FIFO and the intentionally limited expiration feature set.

### [foyer-rs/foyer](https://github.com/foyer-rs/foyer)

**Rust — concurrent memory cache and hybrid memory/disk cache framework.** Useful for studying a cache as a set of replaceable policies and storage components, with reference-counted entries crossing those boundaries.

- **C1:** The eviction abstraction specifies membership-flag and ownership obligations for push, pop, and removal. The raw cache reconciles eviction and index membership, checks record identity, and tracks in-flight fetches and notifications.
- **C2:** Eviction algorithms, weights, admission filters, entry properties, storage engines, and I/O configuration form substantive extension points. The same project supports a memory-only cache and serialized disk-backed operation.
- **C3:** Shards and zero-copy memory entry handles address contention and copying costs; disk throttling and admission controls expose different resource constraints.

Entry points: [eviction contract](https://github.com/foyer-rs/foyer/blob/main/foyer-memory/src/eviction/mod.rs) and [raw cache implementation](https://github.com/foyer-rs/foyer/blob/main/foyer-memory/src/raw.rs). The [README](https://github.com/foyer-rs/foyer#development-state--roadmap) explicitly describes heavy ongoing development; this is not a claim of a settled API.

## Native systems libraries: memory ownership and specialization

### [facebook/CacheLib](https://github.com/facebook/CacheLib)

**C++ — embeddable DRAM and SSD caching engine, including CacheAllocator and Navy.** An unusually rich study of how allocation classes and cache policy interact at larger memory scales.

- **C1:** Hybrid transitions use optimistic coordination rather than holding a global key lock over I/O. Put tokens, deletion tombstones, and lookup contexts prevent stale SSD reads or concurrent evictions from resurrecting removed data. Handles coordinate asynchronous availability and item lifetime.
- **C2:** Access containers, eviction containers, allocation pools, admission policies, and storage engines have separable responsibilities.
- **C3:** Slabs and allocation classes reduce fragmentation; compressed pointers reduce index overhead. SSD admission and clean-item tracking reduce unnecessary writes and account for flash endurance.

Entry points: [architecture overview](https://github.com/facebook/CacheLib/blob/main/website/docs/Cache_Library_Architecture_Guide/Overview_A_random_walk_down_the_Cache_Library.md) and [hybrid-cache concurrency design](https://github.com/facebook/CacheLib/blob/main/website/docs/Cache_Library_Architecture_Guide/Hybrid_Cache.md). Restart preservation is not equivalent to durable storage after power loss. This repository is counted once despite its several cache implementations.

### [uxlfoundation/oneTBB](https://github.com/uxlfoundation/oneTBB)

**C++ — specifically the preview `concurrent_lru_cache` container in the oneTBB monorepo.** A useful counterexample to caches that bound every retained object: this one bounds unused history while handles keep in-use items alive.

- **C1:** Reference counts determine when an item enters the eviction history. Aggregated operations serialize structural changes, and readiness publication coordinates readers with the thread constructing a missing value. Assertions distinguish live references from evictable entries.
- **C2:** A generic key/value container, user-supplied value factory, and movable RAII handle provide a reusable lifetime-aware memoization abstraction.
- **C3:** An operation aggregator batches access to the map and history structures, illustrating an alternative to independent per-operation locking.

Entry points: [container specification](https://github.com/uxlfoundation/oneTBB/blob/master/doc/main/reference/source/containers/concurrent_lru_cache.rst) and [implementation](https://github.com/uxlfoundation/oneTBB/blob/master/include/oneapi/tbb/concurrent_lru_cache.h). **Preview status is explicit**: enabling the feature requires `TBB_PREVIEW_CONCURRENT_LRU_CACHE`; outstanding handles can make total storage exceed the unused-history limit.

### [jaxron/zigache](https://github.com/jaxron/zigache)

**Zig — configurable sharded cache with several replacement algorithms.** A less prominent implementation worth reading for the boundary between compile-time specialization and runtime policy selection.

- **C2:** A generic cache interface selects FIFO, LRU, TinyLFU, SIEVE, or S3-FIFO through a tagged union. Policy parameters, allocator choice, node pooling, TTL, and sharding are explicit configuration dimensions.
- **C3:** Compile-time options remove unused TTL metadata/checks or synchronization, while per-shard mutexes, preallocated nodes, and hash-map load-factor controls make overhead tradeoffs visible in one implementation.

Entry points: [cache types and policy dispatch](https://github.com/jaxron/zigache/blob/main/src/zigache.zig) and [project configuration/status](https://github.com/jaxron/zigache/blob/main/README.md). **Maintenance limitation:** the README says it is not in active development and targets Zig 0.14.0. It is included as a substantive source study, without assuming compatibility with later Zig releases.

## .NET: eviction primitives and resilient load coordination

### [bitfaster/BitFaster.Caching](https://github.com/bitfaster/BitFaster.Caching)

**C# — concurrent LRU/LFU primitives with optional loading and lifetime behavior.** Particularly helpful for comparing multiple concurrency strategies inside a single library.

- **C3:** `ConcurrentLru` approximates recency with hot, warm, and cold FIFO queues. Hits mark entries without immediately reordering them; maintenance occurs during writes. `ConcurrentLfu` instead buffers and asynchronously replays observations for Window TinyLFU. These choices expose CPU, memory, maintenance, and hit-rate tradeoffs.
- **C2:** Builders compose atomic value factories, time-based eviction, metrics, and wrappers for disposable/scoped values. The library therefore addresses both retention policy and the use of values after lookup.

Entry points: [ConcurrentLru design and limitations](https://github.com/bitfaster/BitFaster.Caching/wiki/ConcurrentLru) and [library overview/API composition](https://github.com/bitfaster/BitFaster.Caching/blob/main/README.md). Pseudo-LRU order is intentional; the design guide includes scan patterns where its behavior differs substantially from exact LRU.

### [ZiggyCreatures/FusionCache](https://github.com/ZiggyCreatures/FusionCache)

**C# — hybrid caching and resilience library coordinating memory, optional distributed storage, and refresh work.** Its contribution is substantial concurrency orchestration above cache stores, rather than a novel linked-list replacement policy.

- **C1:** Per-key factory coordination limits duplicate loads, while optional distributed locking extends coordination beyond one process. Logical expiration can be separated from physical retention so failures or timeouts can temporarily fall back to an older value, with explicit maximum retention and retry throttling.
- **C2:** Memory/distributed locker interfaces, optional second-level storage, backplanes, serializers, and per-entry options support different deployment and failure models.

Entry points: [stampede protection and locker architecture](https://github.com/ZiggyCreatures/FusionCache/blob/main/docs/CacheStampede.md) and [fail-safe state/expiration behavior](https://github.com/ZiggyCreatures/FusionCache/blob/main/docs/FailSafe.md). A distributed cache alone does not imply distributed mutual exclusion; the latter needs a configured distributed locker.

## Python: process sharing, synchronization boundaries, and reusable policies

### [grantjenks/python-diskcache](https://github.com/grantjenks/python-diskcache)

**Python — thread/process-safe disk-backed cache built on SQLite and files.** Study what changes when an apparently familiar mapping API must coordinate database transactions and eviction writes.

- **C1:** Atomic operations can be shared between processes. The distinction between `Cache` and `FanoutCache` timeout behavior is consequential: FanoutCache catches database timeouts and can abort writes without raising, while mapping operators retry.
- **C3:** FanoutCache shards databases to reduce writer contention. The default least-recently-stored policy avoids writes on every read; LRU and LFU instead update database metadata during lookup. Sharding also divides the size budget between independent caches.
- **C2:** Mapping, memoization, tags, custom serialization, and file-like values support varied local workloads.

Entry point and evidence: [tutorial sections on concurrency, FanoutCache, and eviction](https://github.com/grantjenks/python-diskcache/blob/master/docs/tutorial.rst). [API metadata](https://api.github.com/repos/grantjenks/python-diskcache) showed a last push in August 2024; the report does not repeat the documentation's undated active-development claim.

### [tkem/cachetools](https://github.com/tkem/cachetools)

**Python — eviction collections plus explicitly synchronized memoization decorators.** **The cache containers themselves are not thread-safe.** Category fit rests on the library's lock/condition-aware decorator machinery combined with its reusable eviction policies.

- **C1:** Condition-based wrappers maintain a pending-key set, release the lock while executing user code, and clear pending state and notify waiters in `finally`. Lock-only wrappers instead permit duplicate computation and reconcile competing insertions. These are distinct guarantees.
- **C2:** Replaceable mappings, key functions, weight calculation, timers, TTL/TLRU, and eviction classes make the synchronization layer reusable across policy choices. Mutable-value sizing and delayed expiration reclamation are documented limitations.

Entry points: [thread-safety and policy contracts](https://github.com/tkem/cachetools/blob/master/docs/index.rst) and [decorator synchronization implementation](https://github.com/tkem/cachetools/blob/master/src/cachetools/_cached.py). This is included to teach explicit synchronization composition, not to label every exported cache concurrent.

### [Yiling-J/theine](https://github.com/Yiling-J/theine)

**Python with a separate Rust policy core — sharded object cache and memoization implementation.** Distinct from the Go project: this repository contains substantial Python-side storage, buffering, loading, and maintenance logic, rather than merely forwarding a foreign API.

- **C1:** Python objects remain in sharded dictionaries, while hashed identities connect them to the policy core. Each shard tracks both keys and hash-to-key mappings. The implementation also coordinates loading results and exceptions, expiration, and locking for free-threaded Python.
- **C3:** The Rust policy core is deliberately serialized under a mutex; Python storage is sharded separately. A shared maintenance thread services expiration across cache instances. This division makes the cost of crossing the language boundary a concrete design consideration.
- **C2:** Typed synchronous/asynchronous memoization and a Django adapter expose the engine to multiple usage patterns.

Entry points: [architecture and v2 migration rationale](https://github.com/Yiling-J/theine#design) and [Python implementation](https://github.com/Yiling-J/theine/blob/main/theine/theine.py). The Rust-core dependency is not counted as another repository. No compatibility claim beyond the documented configuration is inferred.

### [dgilland/cacheout](https://github.com/dgilland/cacheout)

**Python — thread-safe cache-policy family using ordered mappings and explicit expiration metadata.** A comparatively approachable implementation for studying reuse, callback boundaries, and the limits of coarse synchronization.

- **C1:** Public operations use a reentrant lock while internal helpers coordinate the ordered mapping and expiration table. Expiration sweeps use one time sample and a copy of the expiry map. A default-value callable can execute while the cache lock is held, an important contention boundary visible in the source.
- **C2:** FIFO/LIFO/LRU/MRU/LFU/random policies, filtered bulk operations, callbacks, memoization, and a cache manager share a common foundation.
- **C4:** The 2018–2026 changelog records thread-safety repairs, Python-version support changes, an LFU capacity fix, mutation-during-iteration fixes, and corrections to bulk policy hooks and memoization keys.

Entry points: [cache implementation](https://github.com/dgilland/cacheout/blob/master/src/cacheout/cache.py) and [dated changelog](https://github.com/dgilland/cacheout/blob/master/CHANGELOG.rst). The selection does not claim that every workload scales well under its per-cache lock.

## BEAM: process coordination and dependency invalidation

### [whitfin/cachex](https://github.com/whitfin/cachex)

**Elixir — ETS-backed caching library with row locking, loading, expiration, and configurable pruning.** Useful for studying where Erlang runtime primitives replace conventional object-level mutex designs.

- **C1:** The Locksmith service uses a shared ETS lock table, namespaces locks by cache, and atomically attempts multi-key lock acquisition. Transactional work and queued writes require coordination beyond the atomicity of individual ETS operations.
- **C2:** Hooks let applications select scheduled or event-driven pruning and extend least-recently-written behavior with access tracking for LRU-like behavior.
- **C3:** Scheduled cleanup reduces per-operation overhead; event hooks improve responsiveness at additional CPU/memory cost. Reclaiming extra entries creates headroom to avoid pruning on every subsequent write.

Entry points: [Locksmith implementation](https://github.com/whitfin/cachex/blob/main/lib/cachex/services/locksmith.ex) and [limiting-cache policy guide](https://github.com/whitfin/cachex/blob/main/docs/management/limiting-caches.md). Lifecycle pruning is asynchronous, so configured limits are not instant hard bounds.

### [zotonic/depcache](https://github.com/zotonic/depcache)

**Erlang — in-process cache service with dependency invalidation, expiration, and memoized loading.** A distinct design for applications where one cached result depends on several other keys.

- **C1:** Separate data, metadata, and dependency tables use serial numbers to determine whether dependencies remain valid. Waiting loaders are tracked; monitored writer-process exits notify waiters of premature failure so memoization can retry.
- **C3:** Concurrent reads use ETS, optional process-local memoization reduces repeated lookup work, and background cleanup falls back to random eviction under memory pressure to avoid maintaining a global recency list.
- **C2:** Dependency lists, subkey retrieval, memoization functions, expiry, and memory limits support structured application caches beyond isolated key/value entries.

Entry points: [depcache.erl](https://github.com/zotonic/depcache/blob/master/src/depcache.erl) and [property tests](https://github.com/zotonic/depcache/blob/master/test/prop_depcache.erl). This is an embeddable Erlang service, not a separate network-cache deployment. [API metadata](https://api.github.com/repos/zotonic/depcache) last showed a January 2025 push; sustained current maintenance is not asserted.

## Coverage, search process, and limitations

Discovery used **20 search formulations** across JVM TinyLFU/loading caches; Go concurrent eviction and GC-oriented caches; Rust sync/async and hybrid caches; C++ embeddable engines and lifetime-aware LRU; .NET eviction and stampede protection; Python thread/process synchronization; BEAM dependency/ETS caches; Zig specialization; and policy-specific ARC/2Q/SIEVE/S3-FIFO searches. Follow-up searches and source-tree inspection explored less prominent projects rather than ranking by stars. Later queries largely repeated established designs or introduced narrower alternatives with less additional coverage; the final broadening added Zigache and depcache.

For every retained repository, the canonical GitHub identity was verified with the repository API, and at least one additional primary implementation or architectural source was opened and read. Repository trees supplied exact paths and default branches. Important semantic differences were checked against code, including Ristretto's admission outcomes, BigCache's lookup/expiry behavior, Groupcache's internal capacity eviction, oneTBB's unused-entry bound, and cachetools' synchronization boundary. No candidate code was executed, no dependencies were installed, and no performance numbers were independently reproduced.

The selection excludes standalone Redis/Memcached-style servers, generic concurrent maps without eviction, generated or thin cache-store wrappers, tutorials/gists, and eviction simulators such as libCacheSim. It avoids counting the outcaste Ristretto fork, Moka language bindings, or repeated CacheLib subsystems as independent designs. Mini Moka, additional Go LRU/TTL packages, and other related policy implementations were discovered but not exhaustively inspected or retained when the selected projects already covered their principal study angle. This is an evidence-supported selection, not an exhaustive catalog or a judgment that omitted projects are poor.

Coverage is strongest in Go, Java, Rust, Python, and C++; Ruby and C discovery did not produce an additional retained candidate with a sufficiently distinct, verified library contribution within this search. Some repositories intentionally expose approximate bounds, lossy observations, deferred reclamation, or fallible admission. These are part of their contracts, not automatically defects. Conversely, historical bug fixes and tests establish interesting engineering challenges without proving every current component correct. Maintenance flags and last-push observations are snapshots, not support guarantees.
