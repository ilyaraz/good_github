# Persistent key-value storage engines

Research date: **2026-10-09**.

This selection covers 27 repositories implementing reusable, persistent key-value storage: local embedded engines, engine subsystems usable independently of a larger database, and a few clearly marked research or historical implementations. It spans LSM trees, copy-on-write trees, append-only hash stores, JVM collections, object storage, microcontroller flash, and persistent memory. Persistence does not imply identical commit, crash-recovery, or transaction guarantees; consequential differences are called out below. This is a guide to studying engineering decisions, not a certification of every component or a deployment recommendation.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, adversarial inputs, or failures. **C2** — substantial reusable abstractions supporting multiple applications. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — sustained evolution supported by compatibility, testing, or complexity-management evidence. Each entry explicitly justifies at least two criteria. Statements about what an engineer can learn are assessments grounded in the linked primary material.

## LSM trees and related merge-based engines

### 1. [google/leveldb](https://github.com/google/leveldb)

**C++; embedded ordered byte-string store.** A compact starting point for following a write from the log and memtable into immutable tables, then through compaction and recovery. The repository explicitly describes its maintenance as very limited.

- **C1:** Deletion markers must continue hiding older values until compaction can safely remove them. Recovery reconstructs the serving state from `CURRENT`, the manifest, and remaining logs; obsolete-file cleanup must preserve outputs of active compactions.
- **C2:** Comparators, iterators, snapshots, atomic write batches, and the `Env` interface separate application ordering and platform I/O from the engine.
- **C3:** The implementation guide explains non-overlapping ranges above level zero, compaction selection, and the tension between write bursts, memory, and accumulated level-zero files.

Entry points: [implementation and recovery guide](https://github.com/google/leveldb/blob/main/doc/impl.md); [repository API map and maintenance policy](https://github.com/google/leveldb#repository-contents).

### 2. [facebook/rocksdb](https://github.com/facebook/rocksdb)

**C++; configurable persistent engine descended from LevelDB.** Retained separately because its column families, transaction modes, compaction policies, and operational machinery represent substantial independent evolution. Study how an engine manages several competing forms of amplification without abandoning a common storage model.

- **C1:** Atomic batches can span column families. Snapshots constrain which versions compaction may discard, while iterators retain underlying files; these are different lifetime mechanisms. Recovery guarantees depend on WAL or atomic-flush configuration.
- **C3:** Leveled, universal, and FIFO compaction make explicit space/write/read tradeoffs, alongside parallel compaction and batched log synchronization.
- **C4:** The [2014–2026 changelog](https://github.com/facebook/rocksdb/blob/main/HISTORY.md) records public-API changes, compatibility work, and correctness fixes rather than merely release dates. The [architecture overview](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview) also states compatibility goals and explains the mechanisms above.

Entry points: the architecture overview and changelog linked above.

### 3. [cockroachdb/pebble](https://github.com/cockroachdb/pebble)

**Go; independently implemented LSM engine shaped by CockroachDB workloads.** Especially useful for studying how internal representations and concurrency protocols affect CPU costs while retaining familiar storage formats.

- **C1:** Its commit pipeline must preserve both WAL sequence order and read-visibility order even when batches are applied concurrently. Indexed-batch iteration also has to compose correctly with merges and range deletions.
- **C3:** Structured internal keys avoid repeated encoding and allocation. Indexed batches reuse the merging machinery, and large batches can become flushable structures rather than being copied through an ordinary memtable.
- **C2:** Snapshots, merge operators, range operations, iterators, and an I/O abstraction form reusable engine interfaces. The repository explicitly limits RocksDB compatibility; unsupported RocksDB features are not safe to assume interchangeable.

Entry points: [implementation differences and commit invariants](https://github.com/cockroachdb/pebble/blob/master/docs/rocksdb.md); [supported features and compatibility boundaries](https://github.com/cockroachdb/pebble#readme).

### 4. [dgraph-io/badger](https://github.com/dgraph-io/badger)

**Go; transactional LSM engine with a separate value log.** Study the interaction between value separation, version retention, and transaction conflict detection rather than treating this as simply a Go translation of RocksDB.

- **C1:** The transaction oracle checks read keys against later committed write sets, coordinates commit timestamps with write-channel order, and tracks reader watermarks before discarding versions. These mechanisms are visible in [`txn.go`](https://github.com/dgraph-io/badger/blob/main/txn.go).
- **C3:** The [design discussion](https://github.com/dgraph-io/badger#design) explains its WiscKey-inspired separation of values from the LSM index, targeting the cost of repeatedly moving large values through compaction.
- **C2:** Transactions, iterators over versions, configurable retention, and managed timestamps expose more than a simple point-lookup API. The repository also documents race-enabled transactional testing and filesystem-anomaly testing; these are project-reported practices, not independently rerun here.

Entry points: transaction implementation and design discussion linked above.

### 5. [fjall-rs/fjall](https://github.com/fjall-rs/fjall)

**Rust; embedded engine coordinating multiple LSM keyspaces.** Study how a reusable lower-level tree library is integrated with journaling, transactional APIs, and shared resource management. The separately packaged backing tree is not counted again.

- **C1:** Cross-keyspace atomic operations and optional optimistic or single-writer transactions have distinct guarantees. The README explicitly distinguishes repeatable snapshots from serializable read-modify-write transactions and distinguishes OS-buffer flushing from disk synchronization.
- **C3:** The [3.0 design discussion](https://fjall-rs.github.io/post/fjall-3/) explains partitioned indexes and filters, per-level compression, and cache pressure rather than only publishing benchmark results.
- **C4:** That same account traces the 2024 first and second major releases through 3.0, documents a migration tool, and explains configuration simplification and database locking. This is concrete evolution and compatibility work.

Entry points: [durability and transactional modes](https://github.com/fjall-rs/fjall#readme); the 3.0 design and migration account above.

### 6. [surrealdb/surrealkv](https://github.com/surrealdb/surrealkv)

**Rust; versioned embedded engine developed for SurrealDB and exposed independently.** Useful for following the boundary between transaction coordination, the LSM, and value-log garbage collection. Its architecture document is explicitly marked work in progress, so it should be read alongside the current implementation.

- **C1:** The [architecture document](https://github.com/surrealdb/surrealkv/blob/main/docs/ARCHITECTURE.md) describes a conflict oracle, ordered commit pipeline, snapshot visibility, and compaction that respects live versions. Value-log reclamation must agree with the surviving LSM references.
- **C3:** Large values may live in a separate log, while memtables, immutable SSTs, background flushing, and compaction have distinct responsibilities. This makes the costs of value movement and foreground commit coordination inspectable.
- **C2:** Buffered transactions, snapshots, checkpoints, and restore operations provide reusable interfaces beyond the parent database's query layer.

Entry points: architecture document above; [repository and current API overview](https://github.com/surrealdb/surrealkv#readme). Published performance ratios are deliberately not reproduced here.

### 7. [pmwkaa/sophia](https://github.com/pmwkaa/sophia)

**C; historical transactional key-value/row library.** The maintainer explicitly says the project is no longer developed. It remains a useful study of a merge-based architecture organized around independently maintained node files rather than only global LSM levels.

- **C1:** [Transactions](https://github.com/pmwkaa/sophia/blob/master/documentation/crud/transactions.md) can span databases and write their changes to the log as one batch. Commit distinguishes success, rollback, waiting for a concurrent transaction, and errors; error handling does not automatically imply rollback.
- **C3:** The [repository's architecture explanation](https://github.com/pmwkaa/sophia#version-12-latest-design) describes node-local key indexes, appended sorted branches, and a scheduler balancing memory limits, branch counts, and compaction. It explains why the original two-level design changed.
- **C2:** A small object-oriented C API supports documents, cursors, databases, and transactions while keeping the embedding surface compact.

Entry points: transaction guide and architectural history above. Broad asymptotic marketing claims in the README are not adopted as general performance guarantees.

### 8. [slatedb/slatedb](https://github.com/slatedb/slatedb)

**Rust; embedded LSM engine whose durable backing is object storage.** This changes the storage contract: network latency, request charges, and ownership of a remote manifest replace assumptions about a local disk and process lock.

- **C1:** The accepted [manifest RFC](https://github.com/slatedb/slatedb/blob/main/rfcs/0001-manifest.md) develops compare-and-swap updates, writer epochs, zombie-writer fencing, and snapshots that prevent premature object deletion. It is design history, not a claim that every early RFC detail still matches current code.
- **C3:** The [current overview](https://github.com/slatedb/slatedb#introduction) explains batching writes to reduce object-store requests and using caches, compression, and filters on reads. It explicitly separates receiving a write handle from waiting for durability.
- **C2:** Object-store interfaces and an embedded key/range API permit use across storage providers and application types.

Entry points: manifest RFC and current overview above. The repository promises adjacent-version storage compatibility while reserving API-breaking changes.

## Copy-on-write trees, page engines, and hybrid indexes

### 9. [LMDB/lmdb](https://github.com/LMDB/lmdb)

**C; official read-only GitHub mirror of the OpenLDAP-hosted LMDB repository.** The mirror contains substantive source; it is not the upstream issue tracker. Study a design that delegates caching to the operating system and makes transaction lifetime central to page reclamation.

- **C1:** Copy-on-write pages, serialized writers, and a reader table let readers retain consistent versions without blocking writers. Long-lived or stale readers can prevent page reuse, and process/thread rules matter.
- **C3:** Memory-mapped reads return data directly rather than copying through a private page cache. Reusing free pages avoids relying on periodic whole-store log compaction.
- **C2:** Environments, transactions, named databases, cursors, and duplicate-key handling form a small general-purpose interface.

Entry point: [`lmdb.h`, including architecture, caveats, and API contracts](https://github.com/LMDB/lmdb/blob/mdb.master3/libraries/liblmdb/lmdb.h). This is the inspected default branch, not a statement that it is the release to deploy. Mirror status is stated on the repository page.

### 10. [Mithril-mine/libmdbx](https://github.com/Mithril-mine/libmdbx)

**C/C++; official GitHub mirror of a substantially evolved LMDB descendant.** The previously common `erthink/libmdbx` URL redirects here. The README identifies SourceCraft as the origin and GitHub as a mirror. The available source is amalgamated and excludes most internal tests.

- **C1:** Serialized writers and copy-on-write snapshots coexist with cross-process readers; reader lifetime controls when retired pages can be reclaimed. The API carefully distinguishes synchronization modes, writable mappings, and nested-transaction restrictions.
- **C2:** Named maps, multimaps, cursors, C and C++ APIs, and database inspection/copy tools make this a reusable engine rather than a language binding.
- **C3:** Its memory-mapping and shadow-paging design exposes real tradeoffs between copying, synchronization cost, and page reuse, including why long readers can cause database growth.

Entry points: [mirror, distribution, and design notes](https://github.com/Mithril-mine/libmdbx#readme); [documented C API and operating modes](https://github.com/Mithril-mine/libmdbx/blob/master/mdbx.h). Inclusion does not endorse the README's comparative superiority claims.

### 11. [etcd-io/bbolt](https://github.com/etcd-io/bbolt)

**Go; single-file transactional B+tree and substantive continuation of Bolt.** The original Bolt repository is not counted separately. Study a deliberately small API backed by explicit page ownership and commit sequencing.

- **C1:** Read transactions pin pages; a writer cannot reclaim them until readers finish. [`Tx.Commit`](https://github.com/etcd-io/bbolt/blob/main/tx.go) makes node rebalancing, spilling, freelist replacement, data writes, and metadata publication inspectable.
- **C2:** Buckets, nested buckets, ordered cursors, read-only transactions, and update callbacks cover a broad set of embedded applications.
- **C3:** Batching combines concurrent update requests to amortize disk commits, but callbacks may be retried and must tolerate that behavior. The [README](https://github.com/etcd-io/bbolt#readme) also explains mapping-related deadlocks and the cost of long-lived transactions.

Entry points: transaction implementation and README source-reading guide above.

### 12. [cberner/redb](https://github.com/cberner/redb)

**Rust; typed transactional store built from copy-on-write B+trees.** Particularly instructive for the relationship among file-format design, Rust value lifetimes, checksums, and crash-safe publication of a new root.

- **C1:** The [design document](https://github.com/cberner/redb/blob/master/docs/design.md) specifies alternating commit slots, checksum validation, recovery from partial commits, and restrictions on reclaiming pages during non-durable commits. It states underlying filesystem assumptions explicitly.
- **C2:** Typed table definitions, multiversion readers, write transactions, savepoints, and storage backends separate application data representation from persistence machinery.
- **C3:** The document compares single-sync checksum-backed commits with other commit strategies and specifies compact layouts for fixed-width keys and values.

Entry points: design document; [API examples and project status](https://github.com/cberner/redb#readme). The repository describes the project as stable and maintained, but experimental features should still be distinguished from the stable API.

### 13. [wiredtiger/wiredtiger](https://github.com/wiredtiger/wiredtiger)

**C; reusable storage engine, including row-oriented key-value B-trees.** Although widely associated with MongoDB, the repository exposes the underlying engine. Its page cache, update chains, visibility rules, and checkpoint boundaries are valuable study targets.

- **C1:** In-memory update chains retain versions selected by transaction visibility and timestamps. Eviction and checkpointing must avoid persisting invisible operations; the documentation also discusses subtle timestamp and range-truncation exceptions.
- **C2:** Connections, sessions, cursors, transactions, and multiple data-source representations provide reusable boundaries independent of a document query layer.
- **C3:** Pages are loaded through reference structures, and fast range truncation can mark whole pages deleted without reading every record. The interaction with visibility rules makes the optimization particularly instructive.

Entry points: [B-tree architecture](https://github.com/wiredtiger/wiredtiger/blob/develop/src/docs/arch-btree.dox); [transaction architecture](https://github.com/wiredtiger/wiredtiger/blob/develop/src/docs/arch-transaction.dox).

### 14. [couchbase/forestdb](https://github.com/couchbase/forestdb)

**C++; HB+-trie engine with an append-only storage layer.** A useful alternative to ordinary B+tree and LSM indexing. **Branch caveat:** the README says `master` is untouched and unsupported; Couchbase production work uses the separately evolved `cb-master` lineage. The source entry below is for studying `master`, not selecting a production branch.

- **C2:** Binary keys, custom comparators, lookup by key/sequence number/disk offset, snapshots, rollback, and range iteration offer multiple access patterns through one engine.
- **C3:** The HB+-trie divides keys into chunks and combines trie traversal with B-tree nodes. Its implementation exposes key reforming, prefix metadata, comparator selection, and format-version handling. A WAL and in-memory index reduce immediate main-index update work.

Entry points: [HB+-trie implementation](https://github.com/couchbase/forestdb/blob/master/src/hbtrie.cc); [features and branch-history explanation](https://github.com/couchbase/forestdb#readme). Do not equate the repository's existence with support for its default branch.

### 15. [spacejam/sled](https://github.com/spacejam/sled)

**Rust; embedded tree engine with a major in-progress rewrite.** The README warns that it is out of sync with `main`. This entry specifically studies the checked-in **1.0 architecture**, avoiding a mixture of older 0.34 behavior and the new design.

- **C1:** The new write path persists leaf objects before atomically recording their locations. It then defers reuse of old slab slots through epoch-based reclamation. Recovery treats incomplete metadata batches as uncommitted.
- **C3:** A lock-free in-memory index identifies leaves, individually locked leaves constrain contention, a scan-resistant cache controls residency, and slab size classes address fragmentation. The design explicitly contrasts its memory pressure with the earlier implementation.
- **C2:** The documented durability boundary is `flush`, with atomic write batches providing a reusable persistence contract for applications.

Entry points: [1.0 architecture and write ordering](https://github.com/spacejam/sled/blob/main/ARCHITECTURE.md); [rewrite warning](https://github.com/spacejam/sled#readme). Treat this as evolving implementation research, not a claim of a released 1.0 guarantee.

## Append-only logs, value separation, hash stores, and DBM interfaces

### 16. [basho/bitcask](https://github.com/basho/bitcask)

**Erlang with C native components; log-structured hash-table engine.** The original Basho implementation is more instructive than the many small Bitcask tutorial clones. Study how a compact core becomes complicated when merges, expiration, iterators, and concurrent readers overlap.

- **C1:** `get` retries when a merge removes a file between key-directory lookup and file access. Expiration removal checks timestamps and locations to avoid deleting a concurrently updated key. Merge code also tracks tombstones and partial/full merge coverage.
- **C3:** A key directory maps keys to file positions, separating lookup from append-oriented storage. Rotating files and merging obsolete records expose the cost of reclaiming space while reads continue.
- **C2:** The engine supports point operations, folds, iterators, explicit synchronization, and configurable merging. PULSE/EUnit/QuickCheck hooks in the source expose concurrency-testing concerns without requiring a distributed Riak installation.

Entry point: [core engine, read races, and merge implementation](https://github.com/basho/bitcask/blob/develop/src/bitcask.erl). No current maintenance commitment is inferred from the historical Basho name.

### 17. [martinsumner/leveled](https://github.com/martinsumner/leveled)

**Erlang; actor-based engine separating an object journal from a metadata ledger.** Designed especially for Riak-style workloads with substantial values and frequent metadata-only operations.

- **C1:** The [design](https://github.com/martinsumner/leveled/blob/develop-3.4/docs/DESIGN.md) separates the durable journal from the ledger that can be rebuilt by replay. Compaction marks old files for deletion but waits until no snapshot clone needs them.
- **C3:** Keys and metadata move through an LSM ledger while full objects remain in CDB-style journal files. This limits value-related write amplification and reduces cache disturbance for `HEAD` and metadata scans.
- **C2:** Object-type tags and application-defined metadata extraction support differing object semantics. Bookie, Inker, Penciller, and file-clerk actors define comprehensible ownership boundaries; clones enable scans without copying the files.

Entry points: design document; [public role and workload assumptions](https://github.com/martinsumner/leveled#readme). The inspected branch is `develop-3.4`.

### 18. [nutsdb/nutsdb](https://github.com/nutsdb/nutsdb)

**Go; persistent transactional store with several collection types.** Useful for studying how an append-oriented engine exposes richer application data structures and how compaction publication survives interruption.

- **C1:** [`merge_recovery.go`](https://github.com/nutsdb/nutsdb/blob/master/merge_recovery.go) treats a merge in the writing state differently from a committed merge: it discards stale outputs in one case and completes deletion of replaced data/hint files in the other. Unknown manifest states are errors.
- **C2:** Transaction-scoped key/value operations, lists, sets, and sorted sets give the engine broader reuse than a dictionary alone.
- **C3:** The [Merge V2 and HintFile explanation](https://github.com/nutsdb/nutsdb#readme) separates rewrite, commit, and cleanup phases and uses hint files to reduce restart work. It also documents a segment-size compatibility pitfall across older versions.

Entry points: merge recovery implementation and repository architecture/merge notes. The README's numerical improvement claims were not independently measured.

### 19. [estraier/tkrzw](https://github.com/estraier/tkrzw)

**C++; a family of DBM implementations behind common interfaces.** Scope here is the persistent HashDBM, TreeDBM, and SkipDBM implementations; volatile engines are not independent selections.

- **C2:** Common record processors, iterators, polymorphic/sharded adapters, and file abstractions let an application change storage algorithms without replacing its entire access layer.
- **C1:** The manual distinguishes atomic operations across threads from durability across crashes, explains crash detection and restoration, and offers multi-record processing and compare-exchange operations with explicit semantics.
- **C3:** Hash-record offset width and alignment trade maximum addressable size against footprint. Append versus in-place updates, hash-table rebuilding, and direct versus cached I/O expose concrete space, recovery, and performance decisions.

Entry point: [full manual, including file formats, transactions, and tuning](https://github.com/estraier/tkrzw/blob/master/doc/index.xhtml). The manual contains substantive storage layouts, not merely an API feature list.

### 20. [symisc/unqlite](https://github.com/symisc/unqlite)

**C; single-file embedded engine with both raw key/value and document APIs.** Only the underlying key-value, pager, and file-system layers are in scope; the Jx9 document-language implementation is not the reason for inclusion.

- **C1:** The pager owns page caching, database-file locking, rollback, and atomic commit. This boundary makes it possible to study how an index implementation requests mutations without owning all crash-consistency details.
- **C2:** Runtime storage-engine interfaces and the virtual file system separate indexing from platform I/O. The default persistent implementation uses virtual linear hashing; raw binary records can be used directly without the document layer.
- **C3:** Fixed-size cached pages and a dedicated hash engine make page access and lookup organization explicit within a small embedding surface.

Entry points: [official architecture guide](https://unqlite.symisc.net/arch.html); [repository layout and amalgamation guidance](https://github.com/symisc/unqlite#readme). Additional index families mentioned as possible extensions are not treated as implemented features.

### 21. [microsoft/FASTER](https://github.com/microsoft/FASTER)

**C# and C++; hybrid-log key-value engine and persistent-log library.** **Historical status:** the repository says it is no longer actively maintained and points to Garnet/Tsavorite. This entry studies FASTER KV; it does not count the log library as a second repository.

- **C1:** Larger-than-memory storage and recoverability are separate: the [guide](https://github.com/microsoft/FASTER/blob/main/docs/_docs/20-fasterkv-basics.md) requires checkpoints for recovery and contrasts fold-over with snapshot checkpoints. Pending disk reads also require correct session completion handling.
- **C3:** A memory-resident hash index points into a hybrid log whose mutable head supports updates while older pages spill to storage. Compaction copies live records, with different scan and lookup strategies.
- **C2:** User-defined key/value types, callbacks, serializers, and `IDevice` storage implementations support diverse workloads and backing devices.

Entry points: FasterKV guide above; [maintenance notice](https://github.com/microsoft/FASTER#readme).

## JVM engines and independently usable subsystems

### 22. [JetBrains/xodus](https://github.com/JetBrains/xodus)

**Java/Kotlin; transactional environment beneath higher-level entity storage.** **Sunset status:** the README announces migration toward YouTrackDB. The selection is specifically the `environment`/`openAPI` key-value layer, not a separate count for the entity store.

- **C1:** Transactions hold snapshots and can fail to flush or commit because of version mismatch. The [environment guide](https://github.com/JetBrains/xodus/wiki/Environments) documents retry/revert behavior and states that durable writes must be enabled explicitly.
- **C2:** An environment contains multiple named stores, supports maps or multimaps, and allows one transaction across stores. Byte iterables and cursors keep the raw storage API independent of the entity layer.
- **C3:** Prefixing stores use Patricia tries while non-prefixing stores use B+tree variants, exposing a documented random-access versus ordered-scan tradeoff.

Entry points: environment guide above; [sunset notice and subsystem overview](https://github.com/JetBrains/xodus#readme).

### 23. [jankotek/mapdb](https://github.com/jankotek/mapdb)

**Java/Kotlin; persistent collections and reusable storage primitives.** Study what happens when familiar Java collection contracts must coexist with serialization, disk storage, and concurrent structural changes.

- **C1:** The [BTreeMap implementation](https://github.com/jankotek/mapdb/blob/release-3.1/src/main/java/org/mapdb/BTreeMap.kt) spells out weakly consistent iteration, non-atomic bulk operations, and a B-linked-tree protocol with lock-free reads and narrowly locked updates.
- **C2:** Map interfaces, serializers, and the underlying `Store` abstraction separate application collection semantics from record storage. Persistent and off-heap modes serve different application needs.
- **C3:** Node-local synchronization targets concurrency, while the source candidly explains that deletion does not collapse nodes and can leave a performance cost. This makes it a useful example of a documented structural tradeoff, not an unqualified performance endorsement.

Entry points: BTreeMap source above; [repository usage and test-suite explanation](https://github.com/jankotek/mapdb#readme). The inspected branch is `release-3.1`.

### 24. [h2database/h2database](https://github.com/h2database/h2database)

**Java; specifically the independently usable MVStore subsystem.** H2 is counted once. MVStore belongs here because it can be embedded directly as a persistent key-value store without SQL or JDBC.

- **C1:** Copy-on-write versions retain old roots for readers; concurrent persistence writes a snapshot. File layout, chunk reuse, and online-backup rules show why durable storage requires more than a thread-safe map.
- **C2:** Named maps, pluggable serializers and map implementations, large-object storage, a file-system abstraction, and a transaction utility support applications beyond H2's relational engine.
- **C3:** Counted B+trees support rank-style access; changed pages are collected into sequential chunks, while page caching and compaction manage reads and obsolete space.

Entry point: [official MVStore architecture, file format, and API guide](https://h2database.com/html/mvstore.html). Individual durability and transaction behaviors must be read at this subsystem's level rather than inferred from H2's SQL guarantees.

## Specialized media and research architectures

### 25. [armink/FlashDB](https://github.com/armink/FlashDB)

**C; embedded flash database, specifically its KVDB subsystem.** The time-series subsystem is outside this entry's scope. This is an important scale contrast to server engines: flash erase behavior, write granularity, and small memory budgets shape the design.

- **C1:** [`fdb_kvdb.c`](https://github.com/armink/FlashDB/blob/master/src/fdb_kvdb.c) implements explicit record/sector states, CRC validation, aligned writes, and recovery checks for incomplete records. It reserves empty-sector capacity for garbage collection.
- **C3:** Sector recycling, optional small caches, and write-granularity-dependent layouts respond to flash endurance and resource constraints rather than assuming a filesystem and abundant RAM.
- **C2:** Multiple database instances, string/blob values, flash abstraction, and incremental default-key upgrades serve configuration and parameter-storage use cases across devices.

Entry points: KVDB implementation above; [scope, portability, and features](https://github.com/armink/FlashDB#readme). No RAM-footprint or throughput headline is adopted without its platform-specific context.

### 26. [pmem/pmemkv](https://github.com/pmem/pmemkv)

**C/C++; persistent-memory key-value framework. Archived and discontinued by Intel.** Scope is its persistent engines, especially `cmap`; the volatile engines and separate language bindings are not counted as additional stores.

- **C1:** The [engine manual](https://github.com/pmem/pmemkv/blob/master/doc/libpmemkv.7.md) explains persistent concurrent maps, crash consistency, and the restriction against calling engine operations inside external libpmemobj transactions. Thread-safety guarantees vary by operation and engine.
- **C2:** Runtime-selected engines share a C API and C++ interface while exposing differences in ordering, persistence, and concurrency through configuration. This is useful for studying which guarantees belong in a common interface and which must remain implementation-specific.
- **C3:** DAX-backed persistent pools, persistent strings, and a persistent concurrent hash map target memory-addressable storage rather than forcing a disk-oriented WAL/LSM architecture onto it.

Entry points: engine manual above; [archive/discontinuation notice and engine matrix](https://github.com/pmem/pmemkv#readme). Persistent primitives supplied by PMDK/libpmemobj-cpp are dependencies, not claimed as original implementations in this repository.

### 27. [vmware/splinterdb](https://github.com/vmware/splinterdb)

**C; research-oriented embedded store for fast NVMe devices.** Included for a distinct buffered-tree architecture. **Major limitation:** its [limitations document](https://github.com/vmware/splinterdb/blob/main/docs/limitations.md) says recovery is not implemented, the public API and disk format are unstable, and there is no public force-durability operation. Persistence across orderly close/reopen should not be confused with production crash durability.

- **C3:** The authors' [USENIX paper overview](https://www.usenix.org/conference/atc20/presentation/conway) explains the size-tiered Bε-tree, combining LSM and buffered-tree ideas to reduce compaction work and expose I/O/CPU concurrency. Concurrent cache and memtable design accompany the data structure.
- **C2:** The [usage guide](https://github.com/vmware/splinterdb/blob/main/docs/usage.md) exposes point/range operations and configurable message semantics: applications can express an increment or append as a blind update instead of performing a read-modify-write cycle.

Entry points: usage guide and research overview above. This entry qualifies through reusable abstractions and performance architecture, not through a claim of complete crash recovery.

## Coverage, search method, and limitations

Discovery used **19 distinct live web-search formulations**, followed by direct reads of public repository pages, source files, manuals, and design documents. Search angles included mainstream LSM engines; copy-on-write B-trees; Erlang/Bitcask append-only stores; Java/Kotlin collections and transactional environments; newer Rust engines; object-store manifests; microcontroller flash; persistent-memory engines; NVMe/Bε-tree research; and DBM/legacy engine lineages. Follow-up searches increasingly returned already covered families, language bindings, and small experimental implementations, alongside a few additional candidates. The selection extends beyond 25 because flash, persistent memory, and buffered-tree research add materially different engineering constraints.

Canonical GitHub identities were checked by opening repository pages; redirects were followed, including libmdbx's owner change. For each retained repository, an additional primary document or source file was opened and relevant implementation material read. The GitHub API was rate-limited, so verification used public repository HTML and raw source rather than API metadata. The report's source links reflect branches available on the research date; they are not immutable release pins. No candidate code was run and no benchmark, test-suite result, or durability guarantee was independently reproduced.

The scope excludes distributed databases whose main subject is replication or serving infrastructure, such as Redis, etcd, and TiKV; language-only bindings; tutorial Bitcask/LSM clones; caches without persistent-engine substance; and unrelated filesystem or document-query implementations. H2, Xodus, and FlashDB are included only for the named key-value subsystems. RocksDB, bbolt, and libmdbx have enough distinct implementation or evolution to justify their lineage relationships, while thin forks are not separate entries. LMDB and libmdbx are explicitly marked official mirrors. Sophia, FASTER, Xodus, sled, ForestDB, pmemkv, and SplinterDB carry the specific status or completeness limitations observed in their primary material.

This is not an exhaustive ecosystem inventory: additional candidates such as Jungle, upscaledb, and gkvlite surfaced but were not given the same full verification pass and are not ranked or rejected on quality here. C4 is used selectively where historical changes and compatibility management were actually inspected; an old copyright date or a recent commit alone was not treated as evidence. Architectural study value is a grounded judgment, and the report does not imply that every code path in a selected project is uniformly exemplary.
