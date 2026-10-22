# Probabilistic data structure and streaming sketch libraries

Research date: **2026-10-09**.

This report selects **24 GitHub repositories** implementing compact approximate sets, cardinality and similarity estimators, quantile and frequency summaries, sampling, and set-reconciliation sketches. It includes general libraries, specialized algorithm implementations, and two relevant subsystems in broader projects: Hash4j's distinct counters and sourmash's sketching library. PostgreSQL integration is included where the repository implements the sketch and its storage semantics itself. Native implementations in different languages count separately when they contain substantial engineering, rather than bindings alone.

The emphasis is on what an experienced engineer can learn from the implementation. These are reading recommendations, not a claim that every component has been audited, every probability bound holds under arbitrary inputs, or every repository is actively maintained. Canonical repository identities, default branches, archive status, and selected primary sources were checked through GitHub pages or the public GitHub API. No candidate code was executed.

Criteria used below:

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or important failure modes.
- **C2 — Reusable abstractions:** substantial interfaces or composition mechanisms supporting multiple use cases.
- **C3 — Performance with understandable structure:** concrete memory, throughput, latency, or bandwidth constraints reflected in the architecture.
- **C4 — Sustained evolution:** years of releases accompanied by compatibility work, testing, or complexity management; age alone does not qualify.

## General sketch libraries and aggregation frameworks

### 1. [apache/datasketches-java](https://github.com/apache/datasketches-java)

**Language / role:** Java; comprehensive streaming-sketch library for approximate analytics.

Study how a large algorithm family is organized around explicit statistical and storage contracts. The KLL subsystem is an especially useful entry: its common base separates item type from heap versus off-heap representation, while its comments spell out the level layout rather than leaving the compaction invariants implicit.

- **C1:** KLL requires sorted levels above level zero, packed retained items, free capacity after compaction, and conservation of total sample weight. These invariants must survive updates and merges. The [KLL base implementation](https://github.com/apache/datasketches-java/blob/main/src/main/java/org/apache/datasketches/kll/KllSketch.java) documents them directly; the [serialized-memory validator](https://github.com/apache/datasketches-java/blob/main/src/main/java/org/apache/datasketches/kll/KllMemorySegmentValidate.java) distinguishes compact empty, single-item, full, and updatable forms.
- **C2:** The same KLL hierarchy supports primitive and generic items and multiple storage forms, providing a concrete example of sharing algorithm contracts without collapsing all representations into one class.
- **C4:** The [release history](https://github.com/apache/datasketches-java/releases) runs from the 2016 open-source releases through substantial platform migrations. Release 9.0.0 explicitly explains incompatible modernization and the replacement of the separate memory component with Java's Foreign Function & Memory facilities. This is evidence of managed evolution, not a promise of source compatibility across major versions.

### 2. [apache/datasketches-cpp](https://github.com/apache/datasketches-cpp)

**Language / role:** C++; native, header-only implementation of multiple sketch families.

This is a substantial parallel implementation, not a wrapper around the Java code. Read it for generic algorithms that must handle ownership, object movement, comparison, allocation, and serialization while retaining statistical meaning.

- **C1:** The [KLL compaction implementation](https://github.com/apache/datasketches-cpp/blob/master/kll/include/kll_helper_impl.hpp) explains how randomized halving, merging into the next level, and capacity calculations preserve sortedness and space constraints. It explicitly rejects invalid compaction conditions such as an odd input length for halving.
- **C2:** The [KLL public template](https://github.com/apache/datasketches-cpp/blob/master/kll/include/kll_sketch.hpp) exposes comparable item types, comparator and allocator parameters, merge, rank, quantile, and distribution queries. It also makes NaN handling and cross-language string-encoding responsibilities visible.
- **C3:** Compaction works over packed item buffers and uses moves rather than treating retained values as trivial scalars. The repository documents little-endian assumptions and testing on Linux, macOS, and Windows; cross-language serialization should be checked for the particular sketch and item type, not assumed universally.

### 3. [twitter/algebird](https://github.com/twitter/algebird)

**Language / role:** Scala; algebraic aggregation framework containing probabilistic summaries.

The relevant subsystem is `algebird-core`: HyperLogLog, count-min sketches, approximate collections, and their aggregation machinery. Its distinctive lesson is how sketches become composable building blocks for distributed reductions rather than isolated mutable counters.

- **C1:** The [HyperLogLog implementation](https://github.com/twitter/algebird/blob/develop/algebird-core/src/main/scala/com/twitter/algebird/HyperLogLog.scala) handles sparse and dense forms, reversible byte encoding, unions, and approximate intersection calculations. These operations expose representation and estimation issues behind apparently simple aggregation calls.
- **C2:** HyperLogLog is presented as a monoid, allowing the same aggregation model used for ordinary values to combine compact summaries. Sparse and dense implementations sit behind the common HLL abstraction.
- **C4:** [Releases](https://github.com/twitter/algebird/releases) document development from 2013 to 2023, including composable aggregators, Scala compatibility updates, testing dependencies, and binary-compatibility tooling. The [change log](https://github.com/twitter/algebird/blob/develop/CHANGES.md) records sketch optimizations and flaky-test repairs. The latest published release observed was from 2023; this report does not infer current support commitments from later pushes.

### 4. [addthis/stream-lib](https://github.com/addthis/stream-lib)

**Language / role:** Java; historical streaming cardinality, frequency, membership, and top-k library. **Archived.**

This remains useful for understanding an earlier generation of reusable JVM summaries and the practical implementation of HyperLogLog++. It should be approached as an architectural reference, with the archive status made explicit.

- **C1:** [HyperLogLogPlus](https://github.com/addthis/stream-lib/blob/master/src/main/java/com/clearspring/analytics/stream/cardinality/HyperLogLogPlus.java) combines sparse and normal representations, empirical bias-correction data, buffered sparse updates, and versioned serialization. Correctness includes deciding when to change representations and how to merge compatible states, not merely maintaining maximum register values.
- **C2:** The repository provides multiple summary families through reusable Java interfaces; HLL++ implements `ICardinality`, including merging and persistence, rather than existing only as a benchmark program.
- **C3:** Its sparse representation explicitly trades low-cardinality accuracy and compressed storage against the better scaling of normal registers. The temporary sparse collection amortizes work before consolidation. This is a good implementation to compare with newer HLL libraries that simplify or replace bias correction.

### 5. [tylertreat/BoomFilters](https://github.com/tylertreat/BoomFilters)

**Language / role:** Go; probabilistic structures for streams whose size may be unknown or unbounded.

The most instructive distinction is between stable, scalable, inverse, and conventional Bloom filters. Their error behavior differs materially; “Bloom filter” is not one interchangeable contract here.

- **C1:** The [stable filter](https://github.com/tylertreat/BoomFilters/blob/master/stable.go) ages information by decrementing cells before resetting the new item's cells to their maximum. Its stable-point and false-positive calculations accompany a deliberate possibility of false negatives. The [inverse filter](https://github.com/tylertreat/BoomFilters/blob/master/inverse.go) instead implements atomic replacement and comparison using a CAS loop, exposing concurrency and different error semantics.
- **C2:** The suite also includes scalable and counting filters, cuckoo filters, HyperLogLog, count-min, top-k, and MinHash. Its reusable constructors and operations let applications select a structure according to bounded memory, deletion, or stream-history requirements.
- **C3:** Packed cells, cached hash indices, bounded state, and atomic slot replacement make the resource tradeoffs inspectable in relatively small files. Thread safety of the inverse filter must not be generalized to every structure in the suite.

### 6. [Callidon/bloom-filters](https://github.com/Callidon/bloom-filters)

**Language / role:** TypeScript; JavaScript-facing probabilistic collection and sketch suite.

This project is useful for studying hashing, serialization compatibility, and probabilistic algorithms in a runtime with different number and byte-array conventions from C++ or Java. Its scope extends well beyond ordinary Bloom filters to similarity, frequency, cardinality, and invertible lookup tables.

- **C1:** The [IBLT implementation](https://github.com/Callidon/bloom-filters/blob/master/src/iblt/invertible-bloom-lookup-tables.ts) subtracts cell states and decodes differences through cells whose signed count and checksum indicate purity. Successful peeling and partial decoding are substantive failure-mode concerns. The repository also prominently warns that historical hashing/indexing fixes require rebuilding persisted filters.
- **C2:** A [common filter base](https://github.com/Callidon/bloom-filters/blob/master/src/base-filter.ts) centralizes seed, pseudorandom-generator, and hashing state, while individual structures expose their own operation sets. This offers a concrete study of shared infrastructure without assuming that all filters have identical merge or deletion behavior.

The migration warning is especially relevant: persisted bits have meaning only together with the original hash and indexing conventions.

### 7. [barrust/pyprobables](https://github.com/barrust/pyprobables)

**Language / role:** Python; reusable filters, count sketches, heavy hitters, and related summaries.

Read this implementation for the boundary between Python-level APIs and explicitly bounded numeric/storage formats. It covers both in-memory and persisted structures rather than only mathematical demonstrations.

- **C1:** The [count-sketch implementation](https://github.com/barrust/pyprobables/blob/master/probables/countminsketch/countminsketch.py) defines fixed-width counter limits, saturating merge behavior, dimension checks, and a hash-consistency probe. It also documents a format shared with a C implementation. These checks and saturation rules are more informative than a generic statement that sketches are mergeable; the probe itself is not a proof that arbitrary custom hash functions are equivalent.
- **C2:** Count-min, count-mean, count-mean-min, heavy-hitter, and threshold classes reuse substantial implementation and configuration machinery while presenting different query behavior.
- **C4:** The [release history](https://github.com/barrust/pyprobables/releases) spans 2017–2026. Its [change log](https://github.com/barrust/pyprobables/blob/master/CHANGELOG.md) records merge-count repairs, mmap portability fixes, added quotient-filter tests, Python-version transitions, and explicit breaking changes to mismatch handling.

### 8. [crepererum-oss/pdatastructs.rs](https://github.com/crepererum-oss/pdatastructs.rs)

**Language / role:** Rust; typed probabilistic collections, sketches, and stream sampling.

The canonical repository now uses the `crepererum-oss` owner. This is a useful smaller counterpart to the Apache suites, with Rust traits and detailed algorithm explanations close to the code.

- **C1:** The [filter trait](https://github.com/crepererum-oss/pdatastructs.rs/blob/main/src/filters/mod.rs) specifies fallible insertion and union, including the requirement that an unsuccessful insertion preserve user-visible state even if internal state changes. This is an unusually concrete contract to trace into cuckoo and quotient-filter implementations.
- **C2:** The same trait covers multiple approximate-membership implementations, while the library also provides count-min, HLL, t-digest, reservoir sampling, and top-k structures. Associated error types retain implementation-specific failure information.
- **C3:** [Reservoir sampling](https://github.com/crepererum-oss/pdatastructs.rs/blob/main/src/reservoirsampling.rs) separates initial filling, ordinary replacement, and a later skipping approximation. The implementation documents the transition and shows the floating-point/logarithmic calculation used to reduce per-element work. The word “approximation” matters when assessing its sampling guarantees.

### 9. [mattlorimor/ProbabilisticDataStructures](https://github.com/mattlorimor/ProbabilisticDataStructures)

**Language / role:** C#/.NET; broad probabilistic-structure suite with merge and persistence APIs.

This began as a BoomFilters port but now has a distinct implementation, additional algorithms, different hashing, and separate persistence semantics. The repository explicitly says it is not wire-compatible with the Go project; it is retained for that substantive independent evolution, not counted as a thin translation or binding.

- **C1:** [Merge tests](https://github.com/mattlorimor/ProbabilisticDataStructures/blob/master/TestProbabilisticDataStructures/TestMerge.cs) compare combined summaries and document a counterexample where merging bounded top-k heaps cannot recover an item absent from both local heaps. This is useful evidence of attention to a semantic limitation, rather than treating every `Merge` method as equivalent.
- **C2:** The [sliding-window abstraction](https://github.com/mattlorimor/ProbabilisticDataStructures/blob/master/ProbabilisticDataStructures/SlidingWindow.cs) composes user-supplied creation and merge operations over a ring of time buckets with an injectable clock. It documents bucket-granularity expiration and its requirement for exact merge semantics, and rejects the library's approximate top-k implementation.

The window's generic type parameter does not prove the supplied merge law; engineers should examine that caller obligation. The repository's extensive algorithm list and benchmark claims were not treated as blanket validation of every structure.

## Quantile estimation

### 10. [tdunning/t-digest](https://github.com/tdunning/t-digest)

**Language / role:** Java; reference t-digest implementation and accuracy/performance evaluation material.

This is a strong study of a numerically subtle, empirically evaluated summary. Centroid sizes, interpolation, repeated values, and ordering all matter to tail estimates; a compact centroid list alone is not the entire algorithm.

- **C1:** [MergingDigest](https://github.com/tdunning/t-digest/blob/main/core/src/main/java/com/tdunning/math/stats/MergingDigest.java) uses stable sorting, centroid weights, scale-dependent merging, and optional alternating merge direction. These are concrete responses to ordering and numerical behavior. The repository discusses invariant and size proofs separately from the stronger error guarantees of algorithms such as KLL.
- **C3:** The same source explains buffered insertion and amortized sort/merge cost, with parallel arrays for centroid means and weights. Two-level compression separates working precision from the compressed representation exposed later.
- **C2:** Digest APIs cover quantiles, cumulative distributions, merging, and serialization, and support more than one internal digest representation. [Release notes](https://github.com/tdunning/t-digest/blob/main/RELEASE-NOTES.md) provide historical context on serialization repairs and repeated-value bugs; their old known-issue text should not be read as a current exhaustive bug list.

### 11. [DataDog/sketches-go](https://github.com/DataDog/sketches-go)

**Language / role:** Go; native DDSketch implementation for mergeable quantile estimation.

DDSketch's relative error in the returned value is a different contract from an error in quantile rank. This implementation makes the mapping from numerical values to bins and the storage policy independently inspectable.

- **C1:** The [sketch core](https://github.com/DataDog/sketches-go/blob/master/ddsketch/ddsketch.go) separates positive values, negative values, and a zero region. It handles NaN and indexable-range failures and rejects merges with different index mappings.
- **C2:** `IndexMapping` and store abstractions let the same sketch use alternative numerical mappings and bin-storage policies. Protobuf and compact encoding support aggregation across process boundaries.
- **C3:** The [collapsing-lowest dense store](https://github.com/DataDog/sketches-go/blob/master/ddsketch/store/collapsing_lowest_dense_store.go) grows a contiguous bin array only as needed, then combines low-index bins to respect a size limit. That limit changes which quantiles retain the stated accuracy; bounded storage should not be described as preserving every original guarantee unconditionally.

## Cardinality estimation and database storage

### 12. [axiomhq/hyperloglog](https://github.com/axiomhq/hyperloglog)

**Language / role:** Go; focused HLL library with sparse storage and LogLog-Beta estimation.

This is a useful contrast with older HLL++ implementations: its current documentation describes byte-sized registers and the removal of the earlier TailCut approach, despite TailCut remaining in the repository description.

- **C1:** The [main implementation](https://github.com/axiomhq/hyperloglog/blob/main/hyperloglog.go) rejects precision-mismatched merges, handles zero-value sketches, and validates binary versions and representation markers during decoding. The [sparse encoding](https://github.com/axiomhq/hyperloglog/blob/main/sparse.go) has bit-level rules for recovering register indices and leading-zero counts, including validation against the allowed range.
- **C3:** A temporary sparse set, compressed sparse list, and dense register array represent different operating regimes. Conversion thresholds and sparse consolidation expose the practical tradeoff between cheap small sketches and predictable dense updates.
- **C2:** Precision selection, cloning, merging, and binary persistence make this a reusable cardinality component rather than an application-specific counter. Compatibility must include both precision and encoded representation, not just the nominal algorithm name.

### 13. [dynatrace-oss/hash4j](https://github.com/dynatrace-oss/hash4j)

**Language / role:** Java; relevant subsystem is `distinctcount`, especially UltraLogLog and HyperLogLog.

Count this repository once; its unrelated hashing facilities are not separate entries. The distinct-counting code is valuable for studying how an information-efficient sketch state supports several estimators and precision transformations.

- **C1:** [UltraLogLog](https://github.com/dynatrace-oss/hash4j/blob/main/src/main/java/com/dynatrace/hash4j/distinctcount/UltraLogLog.java) explains a register remapping that fits state into bytes, implements packing/unpacking during merges, and supplies both maximum-likelihood and FGRA estimators. Its numerical solver tolerance is related to estimator error rather than an unexplained constant.
- **C2:** The implementation exposes estimator selection, copying, downsizing, and merging. Static merging selects the smaller precision; in-place addition rejects a source with lower precision than the receiver. These are distinct contracts worth studying.
- **C3:** The [project's distinct-counting documentation](https://github.com/dynatrace-oss/hash4j#approximate-distinct-counting) explains allocation-free updates, byte versus packed-register layouts, and storage/error tradeoffs backed by linked simulation material. The report does not repeat benchmark percentages as universal performance claims.

### 14. [citusdata/postgresql-hll](https://github.com/citusdata/postgresql-hll)

**Language / role:** C and SQL; PostgreSQL extension implementing an HLL data type, aggregates, and persistent representation.

This repository is the canonical successor to the earlier Aggregate Knowledge location. It is particularly useful for studying sketch state as a database value that must survive upgrades and participate in SQL aggregation.

- **C1:** The [representation design](https://github.com/citusdata/postgresql-hll#motivation) describes promotion from empty to explicit sorted values, sparse registers, and a full register array. Unions and transitions must preserve the meaning of the set across those representations and their tuning parameters.
- **C2:** SQL construction, union, cardinality, and aggregate operations allow daily summaries to be recombined into larger intervals without revisiting original events. The database type is a reusable analytical building block, not merely a query example.
- **C4:** The [change log](https://github.com/citusdata/postgresql-hll/blob/master/CHANGELOG.md) documents PostgreSQL compatibility work across multiple years, parallel-aggregate support, upgrade fixes, and regression-test portability repairs. The [release procedure](https://github.com/citusdata/postgresql-hll/blob/master/DEVELOPER.md) explicitly couples version changes to SQL upgrade files and test expectations.

## Similarity sketches and domain-scale composition

### 15. [ekzhu/datasketch](https://github.com/ekzhu/datasketch)

**Language / role:** Python; MinHash, weighted MinHash, cardinality sketches, and sketch-based similarity indexes.

The relevant focus is compact set summaries and their LSH indexes, rather than the repository's separate HNSW implementation. This code connects estimator details to the retrieval behavior of a larger reusable index.

- **C1:** [MinHash](https://github.com/ekzhu/datasketch/blob/master/datasketch/minhash.py) checks permutation scheme, seed, and signature length before merging. Its explanation of newer affine permutation schemes distinguishes a bijection property from a proof of min-wise independence; it explicitly describes the resulting accuracy evidence as empirical. Version-2 sketches require attention to legacy compatibility.
- **C2:** The [LSH guide](https://github.com/ekzhu/datasketch/blob/master/docs/lsh.rst) explains banding, threshold optimization, and interchangeable in-memory, Redis, and Cassandra storage. Sketch construction and candidate retrieval are separate, reusable layers.
- **C3:** Batch sketch updates and LSH insertion sessions address computational and network overhead. The documentation warns that queries during an open insertion session can be inconsistent, making the performance tradeoff visible to callers.

### 16. [sourmash-bio/sourmash](https://github.com/sourmash-bio/sourmash)

**Language / role:** Rust core with Python APIs and CLI; MinHash/FracMinHash libraries for genomic sequence comparison.

The selected subsystem is the reusable sketch core and signature/index architecture. The surrounding biological application is valuable because it makes compatibility, abundance tracking, and large collections of sketches concrete requirements.

- **C1:** [KmerMinHash](https://github.com/sourmash-bio/sourmash/blob/latest/src/core/src/sketch/minhash.rs) carries hash-function, seed, k-mer, size/threshold, and optional abundance state. Merging checks compatibility; comparisons can downsample sketches to a common scale. Parallel sorted hash and abundance arrays must remain aligned through these operations.
- **C2:** The [internals guide](https://github.com/sourmash-bio/sourmash/blob/latest/doc/sourmash-internals.md) separates sketches, metadata-bearing signatures, collections, manifests, and indexes. The same summary can therefore be manipulated through library APIs and organized in several storage/search forms.
- **C3:** Threshold-based FracMinHash and sorted-hash merging connect accuracy choices to memory and comparison cost. This is especially useful for studying how a sketch library grows into a domain system without treating serialized metadata as incidental.

## Membership, counting, and range filters

### 17. [bits-and-blooms/bloom](https://github.com/bits-and-blooms/bloom)

**Language / role:** Go; focused Bloom-filter package.

This is a useful compact implementation to read before larger suites. Its study value lies in a small reusable API, efficient bit operations, and explicit compatibility checks rather than algorithmic breadth.

- **C1:** [The implementation](https://github.com/bits-and-blooms/bloom/blob/master/bloom.go) refuses merges when bit-array size or hash count differs and defines binary and JSON persistence. The [tests](https://github.com/bits-and-blooms/bloom/blob/master/bloom_test.go) cover merge mismatches and serialization round trips. The absence of false negatives assumes the filter is used according to its insertion and compatibility contracts.
- **C3:** Several probe positions are derived from a small set of base hash values; `TestAndAdd` shares hashing and traversal across membership checking and insertion. Bitset union performs compatible merges without replaying original keys.
- **C2:** Capacity/error-based construction, copying, set union, byte/string APIs, and stream persistence make it suitable as a reusable prefilter. A fused operation should not be mistaken for an atomic concurrent operation.

### 18. [FastFilter/xor_singleheader](https://github.com/FastFilter/xor_singleheader)

**Language / role:** C; header-only XOR and binary-fuse membership filters.

Read this for the different economics of immutable filters: construction can do substantial work to make later queries compact and simple. The public surface distinguishes allocation, population, querying, serialization, and release.

- **C1:** [Binary-fuse construction](https://github.com/FastFilter/xor_singleheader/blob/master/include/binaryfusefilter.h) handles a peeling order, seeded retries, duplicate-key cases, and allocation failure before assigning fingerprints. Build failure is part of the interface, not an impossible event hidden by the algorithm description.
- **C3:** Fingerprints and segment-based indexing reduce query state, while separate temporary construction arrays carry the expensive bookkeeping. This makes the build-memory versus query-memory distinction easy to inspect.
- **C2:** The small C API can be embedded without a framework and exposes multiple filter/fingerprint variants. [Unit tests](https://github.com/FastFilter/xor_singleheader/blob/master/tests/unit.c) exercise repeated keys, inserted-key membership, and serialization. These structures summarize a fixed set; they are not drop-in implementations of dynamically deletable filters.

### 19. [ayazhafiz/xorf](https://github.com/ayazhafiz/xorf)

**Language / role:** Rust; native XOR and binary-fuse filter implementations.

This is retained separately from FastFilter because it adds substantial Rust ownership, borrowing, serialization, and generic interface design around native implementations. A particularly useful aspect is the distinction between owned filters and views over external buffers.

- **C1:** [BinaryFuse8](https://github.com/ayazhafiz/xorf/blob/master/src/bfuse8.rs) exposes fallible construction, documents the distinct-key requirement, and contains tests for inserted-key membership, false positives, duplicates, and a small-input overflow regression. Its immutable construction contract differs from insertion into a mutable Bloom filter.
- **C2:** `Filter`, `FilterRef`, and `DmaSerializable` support owned fingerprints and borrowed references, allowing callers to use external storage without copying the fingerprint array.
- **C3:** The descriptor/fingerprint split and borrowed representation make memory layout a deliberate API concern. [Compatibility fixtures](https://github.com/ayazhafiz/xorf/blob/master/tests/serialization_compatibility.rs) pin JSON shape and descriptor bytes; they also expose native-endian fingerprint bytes, so the DMA representation should not be assumed universally endian-portable.

### 20. [efficient/cuckoofilter](https://github.com/efficient/cuckoofilter)

**Language / role:** C++; reference implementation of dynamic cuckoo filters.

This is a historical research implementation, useful for studying the algorithm and layout choices. The [repository metadata](https://api.github.com/repos/efficient/cuckoofilter) reports a last push in 2021; that is a status observation, not evidence of a current maintenance commitment.

- **C1:** [The filter core](https://github.com/efficient/cuckoofilter/blob/master/src/cuckoofilter.h) combines two candidate buckets, fingerprints, bounded relocation, and a victim cache. Insertion failure and later deletion interact with that extra cached item. Correct deletion depends on the caller removing an item actually inserted, rather than interpreting a probabilistic positive as proof.
- **C2:** Templates separate item type, fingerprint width, table representation, and hash family. This makes it possible to compare algorithm behavior without rewriting the public filter operations.
- **C3:** [PackedTable](https://github.com/efficient/cuckoofilter/blob/master/src/packedtable.h) uses permutation encoding and tightly packed buckets, including extra allocation for wide reads. It is a concrete example of space savings introducing nontrivial layout and access invariants.

### 21. [splatlab/cqf](https://github.com/splatlab/cqf)

**Language / role:** C; counting quotient filter with deletion, resizing, merging, and concurrency options.

CQF broadens the selection beyond fingerprint membership to compressed multiplicities and iteration. It is particularly interesting when counts are skewed, because counter representation and nearby run layout interact.

- **C1:** The [public API](https://github.com/splatlab/cqf/blob/master/include/gqf.h) exposes no-lock, try-once, and wait-for-lock modes and distinguishes lock acquisition failure, missing entries, and space-related outcomes. [The implementation](https://github.com/splatlab/cqf/blob/master/src/gqf.c) maintains occupied/run-end metadata and variable-length counter encodings while moving entries.
- **C2:** The API includes caller-managed memory, increment/decrement and set-count operations, merging, iteration, and count-vector operations such as inner products. It supports more use cases than a membership-only filter.
- **C3:** Packed slot metadata and counter encoding target locality and memory use; the repository also distinguishes hardware-assisted selection from an older-CPU fallback. GitHub reports its last push in 2023, so it is presented as a substantial research-library reference without an assertion of ongoing maintenance.

### 22. [Baqend/Orestes-Bloomfilter](https://github.com/Baqend/Orestes-Bloomfilter)

**Language / role:** Java; in-memory and Redis-backed Bloom and counting filters. **Archived.**

This is an unusually useful historical study of taking a compact local data structure across a process boundary. The Redis implementation makes transaction scope, network round trips, and shared counters part of the design.

- **C1:** [CountingBloomFilterRedis](https://github.com/Baqend/Orestes-Bloomfilter/blob/master/src/main/java/orestes/bloomfilter/redis/CountingBloomFilterRedis.java) updates membership bits and counts together, and uses watched transactional removal to handle concurrent changes. It also groups repeated hash positions before decrementing counts.
- **C2:** Common filter interfaces and builders configure local versus Redis-backed state, hashing, counter widths, and migration between supported implementations. The broader design demonstrates how one conceptual collection can have materially different storage mechanics.
- **C3:** Redis hashes and bit state are separated, with pipelining and connection pooling addressing network overhead. The [pool helper](https://github.com/Baqend/Orestes-Bloomfilter/blob/master/src/main/java/orestes/bloomfilter/redis/helper/RedisPool.java) makes transaction retries explicit, which is useful for understanding behavior under contention rather than assuming every operation has fixed latency.

### 23. [efficient/SuRF](https://github.com/efficient/SuRF)

**Language / role:** C++; succinct range filter for point filtering, range filtering, and approximate counts.

SuRF is included because it extends approximate filtering to ordered ranges. It is a historical research implementation; the [repository metadata](https://api.github.com/repos/efficient/SuRF) reports a last push in 2022. Construction requires sorted keys.

- **C1:** [The public implementation](https://github.com/efficient/SuRF/blob/master/include/surf.hpp) coordinates conservative prefix comparisons, inclusive/exclusive range endpoints, and iterators across dense and sparse portions of the trie. Range correctness cannot be reduced to the membership rule of an ordinary Bloom filter.
- **C3:** The design combines dense and sparse LOUDS representations, with configurable switching and suffix choices. [The dense component](https://github.com/efficient/SuRF/blob/master/include/louds_dense.hpp) exposes rank-based navigation and the state passed to the sparse component when a search continues below the dense levels.
- **C2:** Point lookup, ordered iteration, range existence, approximate counting, and serialization share the same compact index. It offers a useful comparison with immutable hash filters for applications that need ordering information.

## Set-reconciliation sketches

### 24. [bitcoin-core/minisketch](https://github.com/bitcoin-core/minisketch)

**Language / role:** C++ with a C API; BCH/PinSketch-based compact set reconciliation.

This is a boundary case worth retaining: its purpose is recovering set differences, not estimating a count or quantile. Within capacity it recovers the encoded set exactly; probabilistic failure considerations arise when capacity or protocol assumptions are exceeded. The canonical owner is `bitcoin-core`, not the older `sipa` URL.

- **C1:** The [mathematical design](https://github.com/bitcoin-core/minisketch/blob/master/doc/math.md) explains finite-field sketches, linear combination into symmetric differences, and polynomial recovery. The repository's implementation notes describe randomized root finding to resist adversarial worst-case decoding behavior.
- **C2:** A standalone C interface allows sketch construction, serialization, merging, and decoding independent of Bitcoin. The algebraic symmetric-difference operation supports general reconciliation protocols.
- **C3:** Finite-field specializations, hardware-assisted multiplication, and precomputation address decode cost. The [protocol guide](https://github.com/bitcoin-core/minisketch/blob/master/doc/protocoltips.md) connects that cost to bandwidth, capacity estimation, fallback transmission, incremental communication, and denial-of-service exposure. This is a useful example of a sketch library documenting the system-level consequences of its complexity.

## Search coverage, exclusions, and limitations

Discovery used more than six distinct live-search formulations. The main angles were general probabilistic/streaming suites; DDSketch, t-digest, and KLL quantiles; XOR/binary-fuse and cuckoo membership filters; counting quotient filters; UltraLogLog and HLL cardinality libraries; Scala algebraic aggregation; Python MinHash and LSH; Go unbounded-stream filtering; Rust typed collections and sampling; PostgreSQL-native sketch storage; succinct range filtering; BCH set reconciliation; and a final .NET/Haskell/Erlang ecosystem search. Follow-up searches checked canonical ownership and differentiated ports from wrappers. Later searches increasingly returned already-covered implementations, bindings, tutorials, or projects requiring another full validation pass; the final cross-language pass added the C# implementation rather than padding the list with similar bindings.

Every retained repository was checked through its repository page or GitHub API, and at least one additional primary implementation, design, test, or release source was read. The entries link the most useful inspected starting points. GitHub API tree listings were used to verify paths and default branches. Archive flags were checked directly: stream-lib and Orestes-Bloomfilter are archived. Other old repositories are labeled as historical references where appropriate; a push date is not treated as proof of sustained maintenance. C4 is claimed only where multi-year release or compatibility evidence was inspected.

Important exclusions and boundaries:

- Bindings alone, including Python wrappers around existing native filter/sketch implementations and Rust minisketch bindings, were not counted as independent implementations. Apache's Java and C++ cores are included because both contain substantial native algorithm code; additional Apache and Datadog language variants were not exhaustively catalogued.
- `probabilistic-collections-rs` was investigated through its documentation, but current primary project links led to GitLab; no substantive official GitHub mirror was established for this selection. It was therefore not included.
- `beorn7/perks` was investigated but not retained as an additional independent project: GitHub identifies it as a fork, and establishing the separate evolution needed for inclusion would require more historical comparison. This is not a judgment that its quantile implementation is unimportant.
- Tutorial notebooks, broad awesome-lists, generic stream-processing frameworks, probabilistic-programming systems, and database engines that merely consume sketches were excluded. Newer .NET, Elixir, Haskell, and Rust candidates outside the list remain an area for further research, not presumed inferior projects.
- The selection emphasizes inspectable implementations rather than benchmark rankings. No numerical speedup claims were independently reproduced. Test files and release notes establish engineering intent and observed practices, not a proof that all implementations satisfy their advertised statistical guarantees under every workload.

The study recommendations and criterion assignments are grounded engineering judgments drawn from those sources. Branch-based links describe the inspected repository state and can change; compare a pinned release before adopting serialization formats, platform requirements, or migration behavior in a production system.
