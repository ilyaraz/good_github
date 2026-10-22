# Compressed bitmap and succinct data structure libraries

Research date: **2026-10-09**.

This selection covers reusable compressed integer sets, rank/select indexes, compact integer sequences, dynamic succinct structures, and libraries that build wavelet or trie indexes from those primitives. “Succinct” is used in the ecosystem's practical sense: some implementations deliberately spend additional metadata space to reduce query latency rather than attaining a strict asymptotic bound. Bitmap image codecs, general-purpose compressors, ordinary unindexed bit arrays, and application databases are outside this report.

The 20 repositories below are selected for engineering study, not ranked by popularity. Criteria are judgments grounded in the linked implementations and documentation; they do not certify every component or establish production readiness. Repository pages were opened, and additional primary material was inspected for each entry. No candidate code was installed or executed. Current branches and published package documentation can describe different versions.

**Criteria legend**

- **C1 — Correctness:** difficult invariants, boundary semantics, concurrency, malformed input, or failure handling.
- **C2 — Abstraction:** substantial reusable interfaces or components serving multiple use cases.
- **C3 — Performance and structure:** concrete memory, CPU, locality, or I/O constraints addressed through understandable architecture.
- **C4 — Evolution:** evidence across years of compatibility work, testing, or complexity management, beyond repository age alone.

## Compressed bitmap sets and operations

### 1. [RoaringBitmap/CRoaring](https://github.com/RoaringBitmap/CRoaring)

**C, with C++ interfaces — hardware-oriented Roaring implementation.** Study how an adaptive representation becomes a portable systems library: integer space is partitioned into chunks whose contents use sorted arrays, bitsets, or runs. The C++ interfaces also illustrate ownership management over a C API.

- **C1:** The public header specifies allocation failure, ownership, and copy-on-write behavior. In particular, shared-container handling and interactions between bitmaps using different copy-on-write settings expose correctness obligations beyond Boolean set algebra.
- **C2:** Membership, ordered iteration, rank/select, serialization, and set operations share the same container architecture. The repository supplies both 32-bit and 64-bit interfaces.
- **C3:** The repository explains CPU feature dispatch and optimized versus scalar paths; the representation selects work according to local density rather than scanning the entire integer universe.

Entry point: the extensively documented [32-bit API and representation header](https://raw.githubusercontent.com/RoaringBitmap/CRoaring/master/include/roaring/roaring.h), especially its ownership and copy-on-write sections. The repository README supplies the platform and dispatch discussion.

### 2. [RoaringBitmap/RoaringBitmap](https://github.com/RoaringBitmap/RoaringBitmap)

**Java — Roaring containers and higher-level bitmap indexes.** A useful example of specialized algorithms behind a uniform object-oriented interface. Its scope includes ordinary and memory-mapped bitmaps, 64-bit variants, and range-oriented indexing; these are subsystems of one repository, not separate entries.

- **C1:** Container methods specify unsigned range interpretation, exclusive endpoints, mutating versus nonmutating behavior, and the possibility that an update returns a different container representation.
- **C2:** The abstract container interface dispatches operations among array, bitmap, and run containers while allowing callers to use one bitmap abstraction.
- **C3:** Cardinality-only operations avoid constructing intermediate sets. For example, XOR cardinality is derived from input cardinalities and intersection cardinality, while dispatch still selects the appropriate container-pair algorithm.

Entry point: [Container.java](https://raw.githubusercontent.com/RoaringBitmap/RoaringBitmap/master/roaringbitmap/src/main/java/org/roaringbitmap/Container.java), including the overload dispatch and cardinality methods. The repository README explains memory mapping and unsigned integer semantics.

### 3. [RoaringBitmap/roaring](https://github.com/RoaringBitmap/roaring)

**Go — native Roaring with parallel aggregation.** Study the boundary between compressed-container algorithms and a goroutine pipeline. This is a substantive Go implementation, not a binding to CRoaring.

- **C1:** Parallel aggregation labels results with their intended positions, reconstructs ordered keys despite worker completion order, handles empty outputs, and repairs deliberately deferred cardinalities before publishing containers.
- **C2:** The implementation exposes reusable bitmap operations and also contains `roaring64` and bit-slice indexing subsystems.
- **C3:** Its heap-based multiway union groups equal container keys, pools temporary slices, and uses lazy OR to reduce repeated cardinality work. These mechanisms are directly visible rather than hidden behind a general “parallel” claim.

Entry point: [parallel.go](https://raw.githubusercontent.com/RoaringBitmap/roaring/master/parallel.go), particularly `bitmapContainerHeap`, `repairAfterLazy`, `appenderRoutine`, and `ParHeapOr`.

### 4. [RoaringBitmap/roaring-rs](https://github.com/RoaringBitmap/roaring-rs)

**Rust — native Roaring bitmap and treemap implementation.** Useful for studying Rust collection APIs over adaptive compressed storage, including owned and borrowed set operations and interoperability with other languages.

- **C1:** The API distinguishes validated deserialization from a memory-safe unchecked variant that does not establish bitmap validity. Sorted construction and range operations introduce additional semantic invariants. The [API guide](https://docs.rs/roaring/latest/roaring/bitmap/struct.RoaringBitmap.html) explicitly documents these boundaries.
- **C2:** Standard collection traits, iterators, range queries, rank/select, and cardinality-only operations make the representation reusable without exposing container management to callers.
- **C3:** Container optimization and operations that return only result cardinalities address allocation and representation costs. The repository describes real-dataset benchmarking, while its [release notes](https://github.com/RoaringBitmap/roaring-rs/releases) expose iterator, overflow, and bitmap-corruption fixes worth tracing.

Entry points are the API guide and release notes above. The README labels the optional SIMD feature experimental and untested; it also allows patch releases to require newer stable Rust. Do not infer a conservative compiler-compatibility policy.

### 5. [lemire/javaewah](https://github.com/lemire/javaewah)

**Java — word-aligned run-length bitmap compression.** This offers a different design from Roaring: compressed words encode homogeneous runs and following literal words. Study streaming Boolean computation, packed metadata, and the abstraction of array-backed versus mapped storage.

- **C1:** A running-length word packs the run value, run length, and literal count into different bit fields. Its setters must preserve neighboring fields; count limits and unsigned shifts matter. See [RunningLengthWord.java](https://raw.githubusercontent.com/lemire/javaewah/master/src/main/java/com/googlecode/javaewah/RunningLengthWord.java).
- **C2:** The library provides both 32-bit and 64-bit compressed schemes, bitmap operations, and memory-mapped usage through a reusable set interface.
- **C4:** The [historical changelog](https://raw.githubusercontent.com/lemire/javaewah/master/CHANGELOG) records changes across 2013–2016 involving iterator fixes, literal-count overflow, better tests, refactoring, API deprecations, memory mapping, and backward JDK compatibility. This is evidence of sustained complexity management, not a claim that that changelog describes the latest release.

Entry points: the packed-word implementation and changelog above. Random membership access has different costs from streaming set operations, as the README explains.

### 6. [lemire/EWAHBoolArray](https://github.com/lemire/EWAHBoolArray)

**C++ — templated EWAH compressed bitmaps.** A compact counterpart to JavaEWAH, with distinct C++ storage, iterators, and contracts. Study how a word-size parameter changes the compression representation and how compressed scanning differs from random access.

- **C1:** `set` requires strictly increasing positions, including no duplicate insertion; the header also specifies result lengths for logical operations and why padding matters for logical negation. These contracts are easy to violate if the class is treated as an arbitrary mutable bitset.
- **C2:** Word-size templates, set operators, raw compressed iterators, and set-bit iteration provide several useful views of the same storage.
- **C3:** The implementation skips runs and locates literal words without expanding the bitmap. Its documentation distinguishes work proportional to compressed size from work proportional to the number of set bits.

Entry point: [ewah.h](https://github.com/lemire/EWAHBoolArray/blob/master/include/ewah/ewah.h). The README states that persistent storage does not correct endianness; do not assume its file format has Roaring's cross-language portability properties.

### 7. [tlk00/BitMagic](https://github.com/tlk00/BitMagic)

**C++ — compressed bit-vectors and searchable compact columns.** This is broader than a set implementation: integer and string vectors organize values into bit planes backed by compressed bit-vectors. It is particularly useful for studying the relationship between representation, predicate evaluation, and data movement.

- **C2:** `bm::bvector<>` underlies set operations, rank/select, scans, similarity calculations, and higher-level vectors. The same primitives support both explicit indexes and searches over the stored columns themselves.
- **C3:** The [compression design](https://bitmagic.io/design) describes fixed-depth block organization, bitmap versus delta-gap blocks, and a separate serialization stage using stronger codecs. Partial restoration returns data to a queryable compact representation rather than expanding every value.
- **C1:** Delta-gap blocks encode transition positions, and the two storage stages impose different access and update contracts. Studying these representation boundaries is more informative than treating all “compression” as one interchangeable operation.

Entry point: the compression design above, followed by the repository README's explanation of bit-plane predicate evaluation and progressive elimination of candidate blocks.

## Rank/select and general succinct toolkits

### 8. [xxsds/sdsl-lite](https://github.com/xxsds/sdsl-lite)

**C++ — SDSL v3, a substantial continuation/fork of SDSL v2.** Counted once here for the SDSL family. The repository documents a header-only organization, cereal serialization support, and newer language/compiler support relative to v2. Its value is the composition of basic compact structures into complete indexes.

- **C2:** The [source tree](https://github.com/xxsds/sdsl-lite/tree/master/include/sdsl) spans bitvectors, integer vectors, wavelet structures, balanced parentheses, suffix indexes, and compressed trees.
- **C1:** [csa_wt.hpp](https://raw.githubusercontent.com/xxsds/sdsl-lite/master/include/sdsl/csa_wt.hpp) constrains compatible wavelet-tree, alphabet, and sampling policies with compile-time checks. The resulting index must keep its wavelet representation and suffix-array sampling views consistent.
- **C3:** Separate suffix-array and inverse-suffix-array sampling densities, plus replaceable wavelet and alphabet representations, expose explicit space/access-time choices without duplicating the whole index implementation.

Entry points: the two links above. The original `simongog/sdsl-lite` is the historical v2 lineage, not an additional independent implementation in this count; no blanket assertion of source or binary compatibility between versions is made.

### 9. [vigna/sux](https://github.com/vigna/sux)

**C++ — broadword rank/select, compact Fenwick trees, and related succinct structures.** Particularly useful for understanding the small amount of carefully arranged metadata behind fast rank queries. Its dynamic structures also offer a contrast to B-tree-based bitvectors.

- **C1:** [Rank9.hpp](https://raw.githubusercontent.com/vigna/sux/master/sux/bits/Rank9.hpp) retains a reference to external bits, so later mutation invalidates the index. It also documents the extra accessible bit required for a query at the logical end. These ownership and endpoint assumptions deserve close attention.
- **C3:** Rank9 packs relative counts beside an absolute count and finishes with a masked population count. The README explains benchmark distributions that include a nearly empty half followed by a nearly full half, specifically to reveal behavior concealed by uniform random data.
- **C2:** The same repository supplies static indexing, Elias–Fano sequences, and bounded-leaf Fenwick-based dynamic rank/select as reusable templates.

Entry point: Rank9 above. This is the C++ implementation in the Sux family; the Java and Rust repositories below contain separate substantive implementations, not language-binding packages.

### 10. [vigna/sux-rs](https://github.com/vigna/sux-rs)

**Rust — composable succinct and compressed structures.** Study how storage backends and query capabilities are expressed in the type system. The useful contrast with SDSL is trait-based layering and explicit support for mapped or unaligned storage.

- **C2:** Rank/select structures delegate backend traits, allowing nested indexes. An Elias–Fano sequence can gain indexed access, predecessor/successor lookup, or both by adding the appropriate high-bit select structures.
- **C1:** The [EliasFano API](https://docs.rs/sux/latest/sux/dict/elias_fano/struct.EliasFano.html) distinguishes checked predecessor/successor queries from unchecked operations whose required neighbor must exist. Backend replacement and unaligned-access conversions must preserve compatibility.
- **C3:** Optional indexes avoid paying for unused operations; the repository also documents memory mapping and memory-layout inspection. The API explains how cached endpoints make checked neighbor queries inexpensive.

Entry point: EliasFano's type parameters, construction modes, and safety contracts above. The repository also contains static functions and filters, but the rank/select and sequence components are the category-relevant focus here.

### 11. [vigna/Sux4J](https://github.com/vigna/Sux4J)

**Java — succinct bit indexes, monotone lists, and static functions.** An instructive implementation of compressed sequence access within the constraints of Java arrays and collection interfaces.

- **C1:** Elias–Fano construction assumes nondecreasing natural numbers, a known size, and a suitable upper bound. The implementation documents bounds-check behavior and provides a capacity check because some representations cannot fit within Java's array limits.
- **C2:** Compact monotone data is exposed through big-list and iterator abstractions, with an alternative representation for larger instances and support for mapped data.
- **C3:** [EliasFanoMonotoneLongBigList.java](https://raw.githubusercontent.com/vigna/Sux4J/master/src/it/unimi/dsi/sux4j/util/EliasFanoMonotoneLongBigList.java) explains the high/low-bit split and selection over unary-coded high bits. Bulk extraction, direct delta access, and sequential iterators exploit access patterns that repeated random lookup cannot.

Entry point: the class's implementation notes and corresponding methods above. This is a native Java codebase in the Sux family, separately valuable from the C++ and Rust implementations.

### 12. [Cydhra/vers](https://github.com/Cydhra/vers)

**Rust — rank/select-based vectors, range queries, wavelet matrices, and succinct trees.** A useful study in making low-level indexing primitives serve a broad, documented collection API.

- **C1:** The [RsVec documentation](https://docs.rs/vers-vecs/latest/vers_vecs/bit_vec/fast_rs_vec/struct.RsVec.html) specifies rank/select inverse relationships and what happens when a requested rank is outside the represented set. Those conventions affect every higher-level structure built on it.
- **C2:** The [crate guide](https://docs.rs/vers-vecs/latest/vers_vecs/) distinguishes the mutable construction bitvector from static query structures and describes Elias–Fano, RMQ, wavelet-matrix, and balanced-parenthesis abstractions.
- **C3:** Select iterators exploit sequential access rather than repeating independent select queries. CPU intrinsics, optional pointer-using SIMD, and different balanced-parenthesis lookup-table sizes expose concrete speed/space and portability choices.

Entry points: RsVec and the crate guide above. Benchmark rankings in the README are workload-specific author measurements; they are not adopted as universal claims here.

### 13. [jltsiren/simple-sds](https://github.com/jltsiren/simple-sds)

**Rust — compact structures with an explicit interchange format.** Strong for studying an implementation that treats serialization, streaming construction, and memory mapping as core design concerns rather than afterthoughts.

- **C2:** Raw and packed integer vectors, optional rank/select supports, Elias–Fano sparse vectors, run-length bitvectors, and wavelet matrices form a layered library. Writer and mapper variants let applications choose different storage lifecycles.
- **C1:** The [serialization specification](https://github.com/jltsiren/simple-sds/blob/main/SERIALIZATION.md) defines little-endian words, alignment, padding, optional-index lengths, and zeroed unused bits. Sparse-vector encoding also constrains the number of unary buckets.
- **C3:** Run-length encoding packs complete runs into blocks and stores rank/position samples; optional supports avoid materializing indexes a particular consumer does not need. Wavelet-matrix levels can use different bitvector representations.

Entry point: the serialization specification above, which contains substantive encoding and navigation details. The README identifies 64-bit and little-endian assumptions and a Unix requirement for the optional mapping functionality.

### 14. [kampersanda/sucds](https://github.com/kampersanda/sucds)

**Rust — interchangeable succinct vector and sequence implementations.** Useful for studying a compact library organized around operation traits rather than one favored representation. The repository groups integer vectors, bitvectors, monotone sequences, and character sequences.

- **C2:** Shared `Access`, `Rank`, and `Select` interfaces make implementations within a category replaceable. The README demonstrates combining a rank/select bitvector with a separately compressed random-access integer vector.
- **C1:** Portability is specified at the serialization boundary: pointer-sized integers are stored as 64-bit little-endian values, and deserialization must fail when a value cannot fit the destination machine's `usize`. This separates persistent representation from host pointer width.

Entry points: the repository's portability and interface documentation, and the inspected [source organization](https://github.com/kampersanda/sucds/tree/main/src), which separates operation families, broadword/intrinsic helpers, errors, and serialization. This entry's evidence is narrower than those with fully inspected algorithm files: several deeper source and docs.rs pages failed to load. Optional `no_std` behavior was not independently verified.

### 15. [beling/bsuccinct-rs](https://github.com/beling/bsuccinct-rs)

**Rust monorepo — succinct primitives, compressed sequences, and evaluation tools.** Counted once; the relevant starting subsystem is `bitm`, with `cseq` and the sequence benchmarks providing neighboring context. This is useful for comparing representation policies while holding public query operations constant.

- **C2:** The [bitm API](https://docs.rs/bitm/latest/bitm/) separates bit access, rank, select, and select-zero traits from concrete storage and select strategies. Rank/select indexes can be layered over word arrays instead of requiring a wholly separate container ecosystem.
- **C3:** `RankSelect101111` offers binary search over ranks without another select index, or combined sampling with additional metadata. Constant and adaptive sampling policies make the tradeoff explicit. The documentation connects these implementations to the repository's `cseq_benchmark` tooling.
- **C1:** The API documents capacity limits for simpler rank structures and distinguishes unchecked low-level bit-reading functions, making representation and bounds assumptions visible to callers.

Entry point: bitm's strategy and trait documentation above. The repository also contains perfect-hashing and coding projects; those are not counted separately or used to inflate bitmap coverage.

### 16. [haskell-works/hw-rankselect](https://github.com/haskell-works/hw-rankselect)

**Haskell — Poppy-family indexes over large bitvectors.** Offers a functional-language perspective on an architecture otherwise represented mostly by C++ and Rust here. Study the transition from storable word vectors or mapped files to indexed rank/select queries.

- **C2:** `Poppy512` and `CsPoppy` support rank and select for both bit values, with construction from word vectors and mapped regions. The [published package](https://hackage.haskell.org/package/hw-rankselect) exposes separate internal modules for sampling, lookup, vector handling, and reference implementations.
- **C3:** The README distinguishes a broadword implementation from optional BMI2 support and specifies bit order and padding. It candidly says its combined-sampling implementation does not implement the full optimized cspoppy design.
- **C4:** Package metadata records the 2022 release and 2025 metadata revision, updated dependency bounds, and a declared tested-with range spanning multiple GHC generations. This supports compatibility work across years, without implying a recent algorithmic rewrite.

Entry points: the repository's construction/mapping discussion and package metadata above. Detailed module pages were unavailable during this search, so the assessment relies on the architectural README and independently inspected package metadata, not a source-level correctness audit.

## Dynamic succinct structures

### 17. [xxsds/DYNAMIC](https://github.com/xxsds/DYNAMIC)

**C++ — dynamic partial sums, bitvectors, strings, and compressed text indexes.** The main lesson is how a single mutable building block supports a hierarchy of more complicated structures. The repository retains references to its earlier `nicolaprezza` location; the linked heading is the verified current repository.

- **C1:** [spsi.hpp](https://raw.githubusercontent.com/xxsds/DYNAMIC/master/include/dynamic/internal/spsi.hpp) implements searchable partial sums in a B+-tree, with leaf/internal-node occupancy requirements, sums, positional searches, and insert/update operations. Mutations must preserve both tree organization and aggregate metadata.
- **C2:** Packed partial sums support gap bitvectors and succinct bitvectors, which in turn support strings and BWT/FM-index structures. [dynamic.hpp](https://raw.githubusercontent.com/xxsds/DYNAMIC/master/include/dynamic/dynamic.hpp) makes this composition explicit.
- **C3:** B+-tree locality, compressed leaves, and interchangeable gap/run representations address mutable-index space and traversal costs.

Entry points: the two headers above. The README documents deletion gaps for some higher-level structures and limitations of the allocator. Its broad “dynamic” description should not be read as a promise that every structure supports every edit.

### 18. [saskeli/bit_vector](https://github.com/saskeli/bit_vector)

**C++ — experimental dynamic bitvector library accompanying research.** Valuable as a smaller codebase focused on update buffering, leaves, internal nodes, and layout parameters. The README explicitly directs reproducible study of the published work to its DCC branch and warns that the main branch contains experimental code.

- **C1:** [bv.hpp](https://github.com/saskeli/bit_vector/blob/main/bit_vector/bv.hpp) specifies constraints on update-buffer size, leaf size/alignment, branching factor, and bookkeeping widths. These are structural preconditions rather than cosmetic tuning knobs.
- **C2:** Public aliases compose leaf, node, allocator, and root implementations; both smaller and larger bookkeeping variants support reusable dynamic-vector APIs.
- **C3:** Buffered leaf edits, optional AVX population counting, hybrid run-length options, and explicit cache-line-aware prefetching address update and traversal costs. The README also describes GoogleTest and coverage tooling, without this report claiming to have run them.

Entry point: the public composition header above. Treat this as research software with an explicit experimental-branch caveat, not as a maintenance or deployment recommendation.

## Succinct sequence and tree indexes

### 19. [rossanoventurini/qwt](https://github.com/rossanoventurini/qwt)

**Rust — quaternary wavelet matrices, including compressed variants.** A focused example of changing the representation to reduce dependent memory accesses. Despite the project name, the README explains that its implementation uses a wavelet-matrix layout.

- **C3:** Four-way levels reduce traversal depth relative to binary levels. Optional prediction metadata supports prefetching, and Huffman-shaped variants provide another space/query tradeoff. The README explains dependent-query benchmarking and why query-symbol distribution affects results.
- **C2:** The [QWaveletTree API](https://docs.rs/qwt/latest/qwt/quadwt/struct.QWaveletTree.html) parameterizes the underlying quaternary rank/select structure and prefetch support while exposing common access, rank, select, and iteration operations.
- **C1:** Construction consumes/reorders its input and has a documented size limit; alphabet size and out-of-range queries require careful conventions. The API explains its largest-symbol convention specifically to avoid overflow.

Entry point: QWaveletTree's construction and `rank_prefetch` documentation above. Published speedups are tied to the authors' experimental workloads; no universal multiplier is asserted here.

### 20. [s-yata/marisa-trie](https://github.com/s-yata/marisa-trie)

**C++ — static compressed trie dictionaries, with bindings and tools.** Included for its underlying succinct tree implementation, not merely because it compresses strings. Study how LOUDS navigation, terminal markers, and compressed paths produce a useful dictionary API.

- **C1:** [louds-trie.cc](https://raw.githubusercontent.com/s-yata/marisa-trie/master/lib/marisa/grimoire/trie/louds-trie.cc) translates dictionary IDs through terminal rank/select, follows LOUDS parent relationships, restores linked paths, and tracks resumable prefix/predictive-search state. Construction and loading use temporary objects followed by swap.
- **C2:** The same immutable dictionary supports lookup, reverse lookup, common-prefix search, and predictive search, rather than exposing only a one-purpose membership test.
- **C3:** Compact tree navigation and linked path restoration avoid ordinary per-node pointer structures; separate mapping and reading paths support different storage lifecycles.

Entry point: the LOUDS trie implementation above. This is a static structure: applications needing arbitrary updates should compare its construction lifecycle with the dynamic libraries rather than assume in-place insertion support.

## Search coverage and limitations

Discovery used more than six distinct query formulations, covering: Roaring implementations and interoperation; EWAH/WAH/CONCISE formats; BitMagic's bit-plane design; SDSL versions and compressed suffix indexes; Rust rank/select and Elias–Fano ecosystems; dynamic bitvectors and searchable partial sums; Java and Haskell succinct libraries; LOUDS/compressed tries; and quaternary wavelet trees. Follow-up searches and primary-source links led from broad format families to smaller projects such as DYNAMIC, `saskeli/bit_vector`, `hw-rankselect`, and QWT. Later broad queries mostly repeated already identified projects, wrappers, comparisons, or unrelated image/cryptographic uses of “bitmap” and “succinct.”

The final selection spans C, C++, Java, Go, Rust, and Haskell; native and managed implementations; scalar/broadword/SIMD techniques; immutable and mutable structures; in-memory and mapped storage; production-oriented libraries and explicitly experimental research code. Sux's three language repositories are separate implementations. SDSL v2/v3 are treated as one lineage, and monorepo subsystems are not counted as separate repositories.

Excluded are thin FFI wrappers, wrapper-only Python packages, generic bit-array libraries without the category's compression or indexing focus, application databases that merely consume these structures, and benchmark-only or tutorial repositories. WAH/CONCISE searches provided historical context but did not yield an additional candidate with sufficiently complete verification in this pass. `ot/succinct` and `kampersanda/xcdat` were discovered but their repository pages repeatedly failed to load, so they were not retained on snippets alone. Several deeper Sucds and Haskell module pages also failed; their entries explicitly state the narrower evidence available. Thus this is a substantial selection, not an exhaustive inventory.

No retained project is presented as an official mirror or as archived without evidence. Historical and experimental qualifications are stated where relevant; otherwise inclusion does not imply ongoing maintenance. C4 is assigned only where the inspected history or package metadata supports it. Performance explanations describe mechanisms visible in source or documentation, not independently reproduced benchmark results. The engineering lessons and criteria assignments are grounded in those mechanisms, while judgments about study value remain this report's interpretation.
