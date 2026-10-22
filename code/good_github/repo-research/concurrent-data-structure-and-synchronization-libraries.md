# Concurrent data structure and synchronization libraries

Research date: **2026-10-09**.

This report selects **24 GitHub repositories** for studying shared-memory concurrent containers, memory reclamation, synchronization primitives, inter-thread messaging, and composable atomic operations. It includes blocking and asynchronous coordination as well as nonblocking algorithms. General-purpose monorepos are included only for their named concurrency subsystems, and each repository counts once. Distributed locking services, consensus systems, application frameworks, and concurrency-testing tools without a substantial library implementation are outside this selection.

The criteria below are assessments grounded in the linked primary material, not independent proofs of correctness or reproduced performance results. Linked implementation files and guides are suggested reading entry points. All retained repositories were unarchived when checked through the GitHub API; that status alone does not establish active maintenance. Official mirrors and notable older activity snapshots are identified below.

## Criteria legend

- **C1 — Difficult correctness:** nontrivial invariants, memory ordering, lifetime safety, cancellation, concurrency semantics, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and implementation mechanisms useful across different applications or data structures.
- **C3 — Performance with structure:** concrete attention to contention, allocation, locality, throughput, or latency, with an architecture that can be studied.
- **C4 — Sustained evolution:** evidence of years of development together with compatibility management, testing, or explicit control of implementation complexity. Age and push activity alone do not qualify.

## Memory reclamation and native concurrency foundations

### [khizmax/libcds](https://github.com/khizmax/libcds)

**C++ · Concurrent containers and safe memory reclamation.** A useful comparative codebase for seeing how container algorithms, ordered-list implementations, traits, and reclamation policies fit together. The Michael hash map is especially instructive because its fixed bucket array and independently growing linked buckets make its capacity semantics explicit.

- **C1:** Hazard-pointer management exposes per-thread protection records, retirement capacity constraints, initialization, and thread-lifetime requirements. These are concrete prerequisites for safely reclaiming removed nodes, rather than incidental allocator details. Start with [the hazard-pointer implementation and API](https://github.com/khizmax/libcds/blob/master/cds/gc/hp.h).
- **C2:** The [MichaelHashMap implementation](https://github.com/khizmax/libcds/blob/master/cds/container/michael_map.h) composes an ordered bucket list, a compatible garbage collector, and hashing/comparison traits. It provides a clear example of reusing one container structure with different synchronization and lifetime mechanisms.

Activity caveat: the repository is not archived, but its [GitHub metadata](https://api.github.com/repos/khizmax/libcds) reported its last push as 2023-10-17. Treat it as a study resource without assuming a current support cadence.

### [mpoeter/xenium](https://github.com/mpoeter/xenium)

**C++ · Policy-based concurrent structures and interchangeable reclaimers.** Particularly valuable when the engineering question is how to compare reclamation strategies without rewriting the container algorithm.

- **C1:** The [Michael–Scott queue](https://github.com/mpoeter/xenium/blob/main/xenium/michael_scott_queue.hpp) explicitly pairs acquire loads with release CAS operations, helps advance a lagging tail, and retires the old dummy node only after unlinking it. The comments make the synchronization argument traceable through the implementation.
- **C2:** The same implementation obtains its concurrent-pointer and guard types from a reclaimer policy and accepts a separate backoff policy. The [project overview](https://github.com/mpoeter/xenium#readme) describes hazard pointers, hazard eras, epoch variants, and other alternatives behind this common approach. This is substantive policy-based reuse, with explicit type and allocation constraints.

### [concurrencykit/ck](https://github.com/concurrencykit/ck)

**C · Low-level synchronization, reclamation, and concurrent structures.** A strong entry point for engineers who want to follow a memory-model argument into portable C and architecture-sensitive primitives.

- **C1:** [Epoch reclamation](https://github.com/concurrencykit/ck/blob/master/src/ck_epoch.c) explains which epochs active readers may occupy, when logically deleted objects become reclaimable, and why applying modulo arithmetic to the global epoch can cause livelock under bursty workloads. The explanation precedes the implementation.
- **C3:** The [ring-buffer implementation](https://github.com/concurrencykit/ck/blob/master/include/ck_ring.h) separates producer and consumer state with cache-line padding and specializes operations for different producer/consumer configurations. Together with the epoch module, it exposes the relationship between fast access and deferred destruction without hiding either mechanism behind a large runtime.

### [urcu/userspace-rcu](https://github.com/urcu/userspace-rcu)

**C · Userspace read-copy-update and RCU-compatible containers; official GitHub mirror.** The repository identifies the LTTng-hosted Git repository as upstream. This remains a substantive source mirror, not a relocation notice or unofficial fork.

- **C1:** The [RCU API guide](https://github.com/urcu/userspace-rcu/blob/master/doc/rcu-api.md) distinguishes waiting for pre-existing read-side critical sections from acquiring a reader-writer lock. Thread registration, grace periods, and deferred callbacks make lifetime obligations explicit.
- **C2/C3:** The [resizable hash-table implementation](https://github.com/urcu/userspace-rcu/blob/master/src/rculfhash.c) combines split-ordered lists, marked-node removal, helping, and alternative bucket-memory backends. It documents which operations are lock-free and that resize operations themselves use a mutex. Study this for integrating reclamation with concurrent traversal and growth, rather than assuming an entire library has one progress guarantee.

## Native containers and synchronization subsystems

### [cameron314/concurrentqueue](https://github.com/cameron314/concurrentqueue)

**C++ · Generic multi-producer/multi-consumer queue.** A detailed example of optimizing a queue by choosing an explicit ordering contract and organizing storage around producers.

- **C1:** The [design and semantics discussion](https://github.com/cameron314/concurrentqueue#readme) explicitly says the queue is not globally linearizable or sequentially consistent. Producer-local order, external producer coordination, token ownership, and exception behavior therefore deserve close attention when integrating it.
- **C3:** Contiguous blocks, producer subqueues, reusable tokens, and bulk operations address allocation and synchronization overhead. In [the implementation](https://github.com/cameron314/concurrentqueue/blob/master/concurrentqueue.h), the free list uses reference accounting to keep a candidate node's next pointer stable during removal. This provides a useful path from the high-level partitioning decision into memory-reuse correctness.

### [efficient/libcuckoo](https://github.com/efficient/libcuckoo)

**C++ · Concurrent cuckoo hash table.** Study how a compact hash-table algorithm accommodates concurrent displacement, resizing, and an interface for temporarily locking the whole table.

- **C1:** [The main implementation](https://github.com/efficient/libcuckoo/blob/master/libcuckoo/cuckoohash_map.hh) documents ordered acquisition of bucket locks to avoid deadlock, validation of a cuckoo path after its unlocked search, and the required ordering of resize-counter and hashpower loads. These are distinct correctness problems with local explanations.
- **C3:** The same file separates normal operation with bucket locks and lazy rehashing from `locked_table` operation, where all locks are already held and rehashing must be complete. This organization makes the cost of concurrent point operations versus bulk traversal visible. The [project overview](https://github.com/efficient/libcuckoo#readme) also explains that the implementation evolved beyond its original papers, so the source is the definitive algorithm reference.

### [uxlfoundation/oneTBB](https://github.com/uxlfoundation/oneTBB)

**C++ · Concurrent-container subsystem within a broader parallelism library.** The selected subsystem is the concurrent containers, especially `concurrent_hash_map`, rather than the entire scheduler and algorithm collection.

- **C1:** The [hash-map guide](https://github.com/uxlfoundation/oneTBB/blob/master/doc/main/tbb_userguide/concurrent_hash_map.rst) defines read and write accessors whose lifetimes govern access to an element. Erasure waits for outstanding access, and long-lived accessors can block other threads. This is useful material for designing safe access to mutable values, beyond merely making table lookup thread-safe.
- **C2:** Hash/comparison policy, generic key/value types, and scoped element access form a reusable container API. The [implementation](https://github.com/uxlfoundation/oneTBB/blob/master/include/oneapi/tbb/concurrent_hash_map.h) separates node-level and bucket-level synchronization, providing concrete machinery behind those public semantics.

### [facebook/folly](https://github.com/facebook/folly)

**C++ · The `folly/synchronization` subsystem and its lifetime-protection documentation.** This entry is specifically about hazard pointers, RCU, and mutex machinery, not a blanket assessment of the monorepo.

- **C1:** The [RCU and hazard-pointer guide](https://github.com/facebook/folly/blob/main/folly/docs/Hazptr.md) starts with the use-after-free problem caused by returning a raw pointer after releasing a read lock, then develops protected observation and retirement. It is an unusually useful bridge between API lifetime design and concurrent reclamation.
- **C3:** [DistributedMutex](https://github.com/facebook/folly/blob/main/folly/synchronization/DistributedMutex.h) explains thread-local waiting nodes, contention chains, spin/sleep decisions, fairness, and combining critical sections. It also states restrictions on combined work, including dependence on thread-local state. Study these tradeoffs qualitatively; the implementation's embedded benchmark claims are not independently validated here.

### [google/nsync](https://github.com/google/nsync)

**C · Portable locks and conditional waiting.** Particularly useful for studying conditional critical sections, where a predicate is associated with a mutex and wakeup decisions are handled by the library.

- **C1:** The [mutex slow path](https://github.com/google/nsync/blob/master/internal/mu.c) coordinates queue insertion, designated wakers, atomic state changes, and a long-wait mechanism intended to prevent starvation. Its comments explain why releasing the internal spinlock cannot simply overwrite the state word.
- **C2:** The [conditional-wait API](https://github.com/google/nsync/blob/master/public/nsync_mu_wait.h) supports predicates, equivalent-condition grouping, deadlines, and cancellation while returning with the mutex held. It specifies which protected state predicates may inspect. This abstraction serves many state-machine and resource-coordination use cases and makes caller obligations unusually concrete.

### [abseil/abseil-cpp](https://github.com/abseil/abseil-cpp)

**C++ · The `absl/synchronization` subsystem.** A substantial implementation of mutexes with intrinsic predicates, shared access, debug facilities, and RAII wrappers; unrelated Abseil collections are outside this entry.

- **C1:** [The mutex implementation](https://github.com/abseil/abseil-cpp/blob/master/absl/synchronization/mutex.cc) names a designated-waker invariant: a runnable former waiter must either acquire the mutex or restore the necessary wakeup state. It also encodes waiting writers to prevent new readers from indefinitely bypassing them.
- **C2:** [The public mutex header](https://github.com/abseil/abseil-cpp/blob/master/absl/synchronization/mutex.h) distinguishes ownership, non-reentrancy, reader/writer modes, predicate waiting, condition variables, and scoped locking. It is a useful case study in carrying implementation constraints into a broadly reusable synchronization API.

## Rust: ownership, guards, and alternative consistency models

### [crossbeam-rs/crossbeam](https://github.com/crossbeam-rs/crossbeam)

**Rust · A workspace of channels, queues, deques, synchronization tools, and epoch reclamation.** Counted once. The channel and epoch crates provide complementary views of message ownership and shared-node lifetime management.

- **C1:** [The bounded channel](https://github.com/crossbeam-rs/crossbeam/blob/main/crossbeam-channel/src/flavors/array.rs) encodes slot generations, buffer laps, and disconnection in atomic state. Reserving a slot, initializing its message, publishing its stamp, and waking a receiver are distinct steps that must compose correctly.
- **C2:** [The epoch API and implementation overview](https://github.com/crossbeam-rs/crossbeam/blob/main/crossbeam-epoch/src/lib.rs) supplies atomic/shared pointer types, pinned participants, deferred destruction, and custom collectors. These are reusable building blocks for containers beyond Crossbeam's own collection types. The code shows how a safe-facing interface concentrates the unsafe lifetime argument.

### [Amanieu/parking_lot](https://github.com/Amanieu/parking_lot)

**Rust · Compact locks, a parking core, and reusable lock interfaces.** Study the separation between the state stored inside a lock and the external machinery that queues and suspends contending threads.

- **C1:** [RawMutex](https://github.com/Amanieu/parking_lot/blob/master/src/raw_mutex.rs) documents all combinations of its locked and parked bits. Clearing the parked bit requires a bucket lock so that sleeping threads cannot become invisible and remain unwoken; timeout cleanup and direct ownership handoff extend that state machine.
- **C2/C3:** [The parking core](https://github.com/Amanieu/parking_lot/blob/master/core/src/parking_lot.rs) hashes wait keys into shared buckets and exposes validation, pre-sleep, timeout, and wakeup hooks. This allows multiple synchronization primitives to share queue management while retaining small uncontended state and a separate spinning path.

### [vorner/arc-swap](https://github.com/vorner/arc-swap)

**Rust · Atomic replacement of reference-counted shared values.** A focused, substantive alternative for read-mostly configuration or snapshot publication.

- **C1:** [The internal design](https://github.com/vorner/arc-swap/blob/master/src/docs/internal.rs) explains why loading a raw pointer and then incrementing its reference count is unsafe. Its hybrid protection scheme records reference-count debts and lets writers help readers, with explicit discussion of ABA and memory ordering.
- **C3:** Thread-local debt slots avoid a shared reference-count update on the common read path, while a more expensive fallback handles exhausted slots or interfering writes. The [limitations guide](https://github.com/vorner/arc-swap/blob/master/src/docs/limitations.rs) makes the performance consequences of retaining too many guards explicit, including the recommendation against carrying ordinary guards across async yield points.

### [xacrimon/dashmap](https://github.com/xacrimon/dashmap)

**Rust · Concurrent hash map using sharded reader-writer locks.** Included as a structurally different design from reclamation-based maps. Its source makes both the attraction and integration hazards of returning guarded references easy to inspect.

- **C1:** [The public methods and implementation](https://github.com/xacrimon/dashmap/blob/master/src/lib.rs) explicitly warn that operations such as insertion and removal can deadlock when the caller already holds a reference into the map. A safe Rust reference does not eliminate synchronization-level misuse.
- **C2/C3:** The same source implements a familiar generic map API through shared references, backed by cache-padded shards with independently allocated hash tables and locks. Shard-count constraints and capacity distribution are visible. Study it for the interaction between API familiarity, contention partitioning, memory overhead, and guard lifetime.

### [ibraheemdev/papaya](https://github.com/ibraheemdev/papaya)

**Rust · Concurrent map and set designed around read-heavy workloads and guarded references.** Useful for comparing pointer-protected access with shard-lock ownership.

- **C1:** [The raw table](https://github.com/ibraheemdev/papaya/blob/master/src/raw/mod.rs) distinguishes entries being copied, already copied, and borrowed from an earlier table. Those states affect where operations continue and when reclamation is safe. Resize state also includes allocation locking and coordination, so “lock-free” should not be indiscriminately applied to every internal step.
- **C3:** The implementation supports blocking or incremental resize modes and separates claimed copying work from completed work. The [API guide](https://github.com/ibraheemdev/papaya/blob/master/src/lib.rs) explains the cost/lifetime balance of guards, delayed collection, and owned guards for async use. These are explicit latency and memory-retention tradeoffs, not just a throughput claim.

### [jonhoo/evmap](https://github.com/jonhoo/evmap)

**Rust · Eventually consistent concurrent multi-value map.** A useful study of intentionally weakening immediate visibility in exchange for inexpensive reads and batched publication. It uses the separate `left-right` primitive but contains substantial map-specific operation replay and lifetime handling.

- **C1:** [The write implementation](https://github.com/jonhoo/evmap/blob/main/src/write.rs) applies operations in two passes, first suppressing destruction and later allowing the remaining alias to be dropped. Its unsafe retention API requires deterministic predicate behavior across both passes. These are concrete invariants introduced by maintaining two logical copies.
- **C3:** [The crate guide](https://github.com/jonhoo/evmap/blob/main/src/lib.rs) describes separate read/write handles and delayed visibility. Current examples and the implementation use `publish`; some explanatory text retains older terminology. Publication may wait for readers, so the valuable guarantee is the cheap read path and explicit synchronization boundary, not universal nonblocking progress.

## JVM queues and messaging structures

### [JCTools/JCTools](https://github.com/JCTools/JCTools)

**Java · Specialized queues and message-passing interfaces.** A good comparative collection for different producer/consumer cardinalities and for distinguishing strict queue semantics from deliberately relaxed operations.

- **C1:** [MpmcArrayQueue](https://github.com/JCTools/JCTools/blob/master/jctools-core/src/main/java/org/jctools/queues/MpmcArrayQueue.java) maintains per-slot sequence state and includes extra producer/consumer-index checks so strict `offer` and `poll` results reflect full/empty conditions rather than temporary publication gaps.
- **C3:** The same implementation explicitly discusses padding, separate element and sequence arrays, and power-of-two capacity as memory/performance tradeoffs. The [repository overview](https://github.com/JCTools/JCTools#readme) explains relaxed operations, batch drain/fill, linked-array queues, and XADD-based producer coordination. This makes it useful for understanding why one queue algorithm does not fit every workload.

### [LMAX-Exchange/disruptor](https://github.com/LMAX-Exchange/disruptor)

**Java · Sequenced ring-buffer messaging with consumer dependency graphs.** Study multicast processing and coordinated pipelines as well as ordinary producer/consumer transfer.

- **C1/C3:** The [current user guide](https://github.com/LMAX-Exchange/disruptor/blob/master/src/docs/asciidoc/en/user-guide/10_using_the_disruptor.adoc) separates storage, sequencers, sequence barriers, and wait strategies. Gating prevents producers from overwriting unread entries and prevents dependent consumers from outrunning prerequisite processing; preallocation and wait-policy selection expose the allocation/CPU/latency tradeoff.
- **C4:** The [changelog](https://github.com/LMAX-Exchange/disruptor/blob/master/src/docs/asciidoc/en/changelog.adoc) includes dated 2013–2014 releases, subsequent race fixes and test restructuring, deprecations, and the 4.0 Java-baseline and API changes. This is concrete evidence of managing an evolving concurrency API, rather than inferring maturity from repository age. The original design paper remains useful historically, but its examples should not be mistaken for current API guidance.

### [aeron-io/agrona](https://github.com/aeron-io/agrona)

**Java · The `org.agrona.concurrent` buffers, queues, and ring-buffer subsystem.** The canonical repository now belongs to `aeron-io`; the previous `real-logic/agrona` address redirects here. Ordinary collections elsewhere in Agrona are not being described as concurrent.

- **C1:** [ManyToOneRingBuffer](https://github.com/aeron-io/agrona/blob/master/agrona/src/main/java/org/agrona/concurrent/ringbuffer/ManyToOneRingBuffer.java) separates capacity claims from publication. Negative record lengths mark incomplete writes; release operations publish completed records, while explicit commit and abort paths handle claimed regions.
- **C3:** The same implementation uses an atomic buffer, aligned records, cached consumer position, and wraparound padding. These mechanisms make it a useful study of variable-length message transport in a bounded buffer, including the relationship between data layout and producer coordination. The [project overview](https://github.com/aeron-io/agrona#readme) places these primitives within its on/off-heap buffer abstractions.

## Go and .NET coordination libraries

### [puzpuzpuz/xsync](https://github.com/puzpuzpuz/xsync)

**Go · Concurrent maps, counters, queues, and synchronization primitives.** The map provides a particularly concrete example of adapting cache-conscious container design to Go's atomics, garbage collector, and allocator.

- **C1:** [The map implementation](https://github.com/puzpuzpuz/xsync/blob/main/map.go) coordinates old/new table pointers, resize sequence state, helper counts, and transfer progress. Concurrent rehashing is therefore an explicit protocol rather than an opaque stop-and-copy operation.
- **C3:** Cache-oriented buckets, immutable key/value entries, metadata-assisted lookup, and striped counters address different contention costs. The [bucket-alignment investigation](https://github.com/puzpuzpuz/xsync/blob/main/bucket-alignment-fix.md) explains how allocator headers defeated the intended layout and how moving frequently written lock fields reduced cross-bucket interference. Its stated race-test and layout checks are project-reported evidence; no benchmark was rerun for this report.

### [golang/sync](https://github.com/golang/sync)

**Go · `golang.org/x/sync`; official GitHub mirror of the Go subrepository.** A compact selection with meaningful failure handling: weighted semaphores, duplicate-call suppression, and related coordination interfaces.

- **C1:** [The weighted semaphore](https://github.com/golang/sync/blob/master/semaphore/semaphore.go) handles cancellation racing with acquisition by returning acquired tokens when necessary. Its waiter policy deliberately declines to bypass a large request with smaller requests, documenting the resulting starvation-versus-utilization tradeoff.
- **C2:** [Singleflight](https://github.com/golang/sync/blob/master/singleflight/singleflight.go) provides reusable per-key suppression of duplicate in-flight work. Its cleanup distinguishes a normal return, panic, and `runtime.Goexit`, illustrating why a seemingly small coordination abstraction needs a substantial failure protocol. Together these modules support resource budgeting and shared expensive work across many services.

### [StephenCleary/AsyncEx](https://github.com/StephenCleary/AsyncEx)

**C# · The `Nito.AsyncEx.Coordination` subsystem.** Useful for studying synchronization whose ownership lasts across `await`, with tasks representing queued waiters rather than blocked operating-system threads.

- **C1:** [AsyncLock](https://github.com/StephenCleary/AsyncEx/blob/master/src/Nito.AsyncEx.Coordination/AsyncLock.cs) coordinates lock state, a cancellable wait queue, and disposable release keys. It documents non-reentrancy and the semantics of an already-cancelled token, and keeps the lock taken when handing ownership to a queued waiter.
- **C2:** The [design guidelines](https://github.com/StephenCleary/AsyncEx/blob/master/doc/design.md) require consistent asynchronous coordination APIs, cancellation-token support, and avoidance of public state queries that encourage races. These guidelines explain how a family of locks, events, and coordination types can remain coherent rather than becoming unrelated task wrappers.

Activity caveat: the repository is not archived, but its [GitHub metadata](https://api.github.com/repos/StephenCleary/AsyncEx) reported its last push as 2024-01-01. This entry does not imply current feature development or support for every newer .NET environment.

## OCaml: domain-safe structures and transactional composition

### [ocaml-multicore/saturn](https://github.com/ocaml-multicore/saturn)

**OCaml · Concurrent structures for multicore domains.** A useful complement to unmanaged-language implementations: garbage collection simplifies some lifetime concerns, but owner/stealer roles, atomic ordering, and algorithmic progress still require careful reasoning.

- **C1:** The [testing guide](https://github.com/ocaml-multicore/saturn/blob/main/test/README.md) describes sequential-model/linearizability testing and `dscheck` exploration of atomic interleavings. It explicitly limits the conclusions to paths explored by the tests. This is valuable evidence of a concrete concurrency-validation method without claiming a proof of the entire library.
- **C3:** [The work-stealing deque](https://github.com/ocaml-multicore/saturn/blob/main/src/ws_deque.ml) separates owner and thief state, caches the top index, pads contended fields, and comments on when a fenceless access is justified. Growth and CAS-based stealing expose a compact but nontrivial architecture suitable for close study.

### [ocaml-multicore/kcas](https://github.com/ocaml-multicore/kcas)

**OCaml · Software transactional memory and composable concurrent structures.** The repository includes both the multi-word compare-and-set foundation and `Kcas_data`; they count as one project.

- **C1:** The [algorithm design document](https://github.com/ocaml-multicore/kcas/blob/main/doc/gkmz-with-read-only-cmp-ops.md) develops descriptor-based multi-word CAS, helping, and the role of fresh descriptors in avoiding ABA. It explains why asserting an unchanged value with CAS can still create interference, motivating separate read-only comparisons.
- **C2/C3:** The [public interface](https://github.com/ocaml-multicore/kcas/blob/main/src/kcas/kcas.mli) exposes locations, composable transactions, retries, timeouts, and waiting for changes across multiple locations. The distinction between read-only comparison and writes provides a concrete performance rationale for the abstraction. Study it for composing atomic operations across data structures, where independent thread-safe method calls are insufficient.

## Coverage, search process, and limitations

Discovery used live web searches across more than six distinct formulations, including C++ lock-free containers and reclamation; C synchronization, Concurrency Kit, and userspace RCU; concurrent cuckoo tables and queues; Rust maps and guarded publication; Java queue families and the Disruptor/Agrona community; Go concurrent maps and synchronization; .NET async coordination; and OCaml/Scala transactional memory. Follow-up searches for C lock-free libraries, STM implementations, and asynchronous synchronization increasingly repeated covered families or returned tutorials, wrappers, distributed systems, and broader runtimes. This is a bounded selection, not an exhaustive census of those ecosystems.

For every retained repository, the exact canonical URL, default branch, archive flag, and repository identity were checked through the public GitHub API. At least one additional primary implementation or architectural document was fetched and read; most entries have two complementary entry points. Source-tree paths were checked against repository file listings. Agrona's owner redirect was resolved, and Userspace RCU and Go's sync repository are explicitly marked as official mirrors. Links to default branches are verified reading paths, not immutable version pins.

Important exclusions include [SCC's former GitHub repository](https://github.com/wvwwvwwv/scalable-concurrent-containers), whose inspected README says development moved to Codeberg and that the GitHub repository will no longer be maintained; it is not counted as a current official mirror. Xenium's earlier `emr` predecessor was not counted separately. Flurry and additional Rust concurrent maps were considered during discovery, but the selected sharded, guarded, and eventual-publication designs already provide contrasting study paths. Single-algorithm examples, awesome-lists, unofficial forks, generated wrappers, and benchmark-only repositories were not used to fill the list. Scala STM and other functional-language implementations were discovery leads, not verified entries in this report.

No candidate was cloned or executed, no dependencies were installed, and no performance or correctness tests were independently run. C3 judgments concern visible engineering mechanisms rather than cross-project benchmark rankings. C4 is asserted only where inspected release history supports evolution and complexity management. Sparse push activity, published tests, and sophisticated algorithms each provide limited evidence on their own; this guide identifies worthwhile subsystems to inspect, not repositories whose every component is uniformly exemplary.
