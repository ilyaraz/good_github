# Multi-pattern string matching and text indexing libraries

Research date: **2026-10-09**

This selection covers **24 GitHub repositories** implementing reusable multi-pattern scanners, compact string dictionaries, suffix-array construction, compressed full-text indexes, and embedded inverted indexes. Sequence-oriented libraries are included where the indexing implementation is reusable; their alphabet restrictions are stated. Search services, thin language bindings, application-specific aligners, and general-purpose containers without a substantial string-indexing role are outside the selection.

The criteria are judgments grounded in the linked implementation and documentation, not certifications of production readiness. Repository identity and archive status were checked through GitHub repository pages or API metadata. None of the selected repositories was marked archived at the time of research. Older activity is identified where relevant; an unarchived repository does not establish ongoing maintenance.

**Criteria legend**

- **C1 — Correctness:** difficult invariants, concurrency, numerical or character semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or composable structures supporting multiple use cases.
- **C3 — Performance architecture:** concrete memory, throughput, latency, or scaling constraints addressed through an understandable design.
- **C4 — Evolution:** documented development over years together with compatibility, testing, or complexity management. Age and recent pushes alone do not qualify.

## Multi-pattern automata and streaming scanners

### 1. [BurntSushi/aho-corasick](https://github.com/BurntSushi/aho-corasick)

**Rust — literal multi-pattern matching.** An especially useful study of how production match semantics change automaton construction. Standard, leftmost-first, and leftmost-longest matching are deliberately different behaviors, rather than post-processing options over an identical stream of results.

- **C1:** Leftmost matching retains only suitable failure transitions and continues after an initial match until termination is justified. That changes which overlapping and streaming operations are supported. The design explains these semantic restrictions and the buffering required for stream replacement. [Design](https://github.com/BurntSushi/aho-corasick/blob/master/DESIGN.md)
- **C2/C3:** A common API fronts noncontiguous NFA, contiguous NFA, and DFA representations. Alphabet equivalence classes, premultiplied state identifiers, SIMD prefilters, and packed matching expose concrete construction-time, memory, and search-speed tradeoffs. The public examples include searching and replacing through `Read`/`Write` streams. [API and usage](https://github.com/BurntSushi/aho-corasick/blob/master/README.md)

### 2. [daac-tools/daachorse](https://github.com/daac-tools/daachorse)

**Rust — double-array Aho–Corasick.** Study a compact automaton representation and the consequences of choosing byte transitions versus Unicode code-point transitions.

- **C1:** Matching policy distinguishes overlapping, standard, and leftmost variants; the character-oriented implementation still reports byte offsets. Serialization offers checked and unchecked loading paths and explicitly warns that major versions may change the format. [Public types and contracts](https://github.com/daac-tools/daachorse/blob/main/src/lib.rs)
- **C2/C3:** Pattern-associated values, iterator interfaces, and separate bytewise/characterwise implementations support more than boolean detection. Compact double-array traversal, corpus-guided layout, and an optional two-gram prefilter show how layout and filtering affect memory and scanning costs. [Crate documentation](https://docs.rs/daachorse/latest/daachorse/)

### 3. [WojciechMula/pyahocorasick](https://github.com/WojciechMula/pyahocorasick)

**C with a Python API — native trie and Aho–Corasick implementation.** This is an implementation in its own right, rather than a thin binding to another selected matcher. It is useful for studying the interaction between a mutable dictionary, a finalized automaton, and CPython ownership rules.

- **C1:** The implementation tracks empty/trie/automaton states and mutation versions, constructs failure links with a queue, handles allocation failures, and manages Python reference counts when values are replaced or removed. [Automaton implementation](https://github.com/WojciechMula/pyahocorasick/blob/master/src/Automaton.c)
- **C2:** One abstraction supports dictionary operations, prefix lookup, associated Python objects or compact integer values, finalization for multi-pattern scans, and persistence. The API documents build-dependent Unicode/bytes behavior and iterator usage. [API guide](https://pyahocorasick.readthedocs.io/en/latest/)

### 4. [hankcs/AhoCorasickDoubleArrayTrie](https://github.com/hankcs/AhoCorasickDoubleArrayTrie)

**Java — double-array dictionary matching.** A compact study of separating an object-based construction phase from array-based traversal. Treat it as an older implementation: GitHub metadata recorded its last repository push in 2021, so ongoing maintenance is not assumed.

- **C1/C3:** `base` and `check` encode transitions, while separate failure and output arrays preserve suffix matches. Breadth-first failure construction propagates emitted patterns; scan loops then access these arrays directly. The empty-dictionary construction path explicitly prevents transitions. [Implementation](https://github.com/hankcs/AhoCorasickDoubleArrayTrie/blob/master/src/main/java/com/hankcs/algorithm/AhoCorasickDoubleArrayTrie.java)
- **C2:** Generic values, collected results, callbacks, cancellable callbacks, exact lookup, and save/load support several integration styles. The project documents concurrent use after construction; callers should distinguish read-only scanning from mutation. [Usage and lifecycle](https://github.com/hankcs/AhoCorasickDoubleArrayTrie/blob/master/README.md)

### 5. [VectorCamp/vectorscan](https://github.com/VectorCamp/vectorscan)

**C/C++ — simultaneous regular-expression scanning.** A substantive Hyperscan fork, selected once for this lineage. Its independent work includes Arm and Power SIMD support, SIMD abstraction, build refactoring, and regression fixes; it is not merely a repackaging.

- **C1/C2:** Block, vectored, and streaming APIs distinguish temporary scratch space from persistent stream state. Scratch cannot be shared by simultaneous or nested scans; stopping a stream through a callback still requires cleanup. Zero-width assertions can defer matches until another block or stream closure. [Runtime contracts](https://github.com/VectorCamp/vectorscan/blob/develop/doc/dev-reference/runtime.rst)
- **C3/C4:** The 2022–2026 changelog records SuperVector refactoring, platform CI, compatibility decisions, and fixes for vector tails, out-of-bounds accesses, and matches crossing stream chunks. This provides concrete evidence of performance work coupled to portability and correctness management. [Vectorscan changelog](https://github.com/VectorCamp/vectorscan/blob/develop/CHANGELOG-vectorscan.md)

## Compact dictionaries and prefix indexes

### 6. [s-yata/marisa-trie](https://github.com/s-yata/marisa-trie)

**C++ — static compressed trie dictionaries.** Study how a compact representation supports both directions of dictionary encoding and resumable prefix enumeration.

- **C1/C3:** The LOUDS implementation combines topology bitvectors, terminal flags, links, and stored tails. Lookup obtains key IDs through terminal-bit ranks; reverse lookup uses select operations. Predictive search maintains explicit traversal history, so rank/select navigation and search-state invariants are central. [LOUDS implementation](https://github.com/s-yata/marisa-trie/blob/master/lib/marisa/grimoire/trie/louds-trie.cc)
- **C2:** Exact lookup, reverse lookup, common-prefix search, and predictive search share the same static dictionary. This makes the code useful for autocomplete, lexicons, and key-to-ID storage, with command-line tools exposing the library's construction and query lifecycle. [Library overview](https://github.com/s-yata/marisa-trie/blob/master/README.md)

### 7. [Tessil/hat-trie](https://github.com/Tessil/hat-trie)

**C++ — mutable string maps and sets using a HAT-trie.** A useful contrast with static compressed dictionaries: trie prefixes lead to array-hash leaves, which can burst into further trie structure.

- **C1:** The implementation documents that hash nodes are leaves and that a trie node must have a child or stored value. Mutation must preserve that structure; the public contract also states iterator invalidation and value-type requirements. [Core node and container implementation](https://github.com/Tessil/hat-trie/blob/master/include/tsl/htrie_hash.h)
- **C2/C3:** Map/set interfaces offer prefix ranges, prefix deletion, longest-prefix lookup, and serialization. Burst threshold and hash load factor expose distinct tuning choices for exact lookup, prefix enumeration, and memory consumption. Keys are not lexicographically ordered, an important consequence of the hash leaves. [API overview and tuning](https://github.com/Tessil/hat-trie/blob/master/README.md)

### 8. [BurntSushi/fst](https://github.com/BurntSushi/fst)

**Rust — immutable finite-state string sets and maps.** Study compression through shared prefixes and suffixes, plus query execution over compressed storage. The metadata's last recorded push was in 2024; no current release cadence is inferred.

- **C1/C2:** The raw layer separates immutable transducers, nodes, builders, range streams, and set-operation streams. Map values are reconstructed by accumulating transition outputs, while serialized transducers carry a checked format version. [Representation and raw API](https://github.com/BurntSushi/fst/blob/master/src/raw/mod.rs)
- **C3:** Construction can stream to a writer, and the resulting byte representation can be memory-mapped for lookup. Automaton queries and unions/intersections of result streams avoid materializing every key. The documentation candidly identifies the optional Levenshtein automaton builder as memory-heavy. [Memory and query architecture](https://github.com/BurntSushi/fst/blob/master/src/lib.rs)

### 9. [kampersanda/xcdat](https://github.com/kampersanda/xcdat)

**C++17 — compressed double-array string dictionaries.** A less widely known implementation that connects succinct encoding with a practical dictionary API.

- **C1/C2:** Construction expects sorted, unique keys. Binary-key handling switches from null termination to bit flags; lookup/decode and prefix/predictive iterators share the representation. Iterator-returned string views have explicit lifetime caveats. [Trie implementation and contracts](https://github.com/kampersanda/xcdat/blob/master/include/xcdat/trie.hpp)
- **C3:** Compressed base/check vectors reduce double-array storage, while minimal-prefix tries move redundant paths into tail strings to improve locality. Multiple vector encodings and memory-mapped loading make the speed/space design inspectable. [Architecture and encoding alternatives](https://github.com/kampersanda/xcdat/blob/master/README.md)

## Suffix-array construction libraries

### 10. [IlyaGrebnov/libsais](https://github.com/IlyaGrebnov/libsais)

**C — suffix arrays, generalized suffix arrays, LCP/PLCP, and BWT construction.** An indexing foundation, rather than a complete query engine. Study how a theoretically linear algorithm is organized around actual memory traffic.

- **C1/C3:** The architecture describes S/L/LMS classification, recursive problem reduction, and directional induced-sorting passes. Reusing array space, prefetching, and optional OpenMP address memory limits and bandwidth; larger-index and wider-symbol variants make integer-width constraints explicit. [Algorithm and API](https://github.com/IlyaGrebnov/libsais/blob/master/README.md)
- **C4:** The 2021–2025 changelog documents large-input bounds fixes, strict-aliasing and undefined-behavior corrections, integer-input restoration, wider input support, and compiler/build integration. These are evidence of sustained correctness and portability work, not merely elapsed age. [Change history](https://github.com/IlyaGrebnov/libsais/blob/master/CHANGES)

### 11. [y-256/libdivsufsort](https://github.com/y-256/libdivsufsort)

**C — lightweight suffix sorting and BWT.** A historical but substantive construction library, with its last repository push recorded in 2020. It offers a useful algorithmic comparison with SA-IS implementations.

- **C1/C3:** Construction classifies A/B/B* suffixes, sorts B* substrings, derives ranks, and induces the remaining suffix order. Assertions explain ordering and bucket-position requirements, while temporary regions reuse suffix-array storage. The source separates substring sorting, rank sorting, suffix-array construction, and direct BWT construction. [Core algorithm](https://github.com/y-256/libdivsufsort/blob/master/lib/divsufsort.c)
- **C2:** A small C API exposes suffix-array and BWT construction with explicit buffers, lengths, return codes, and permitted buffer aliasing. This makes it an inspectable building block for downstream compressed indexes rather than an application-bound implementation. [Public interface](https://github.com/y-256/libdivsufsort/blob/master/README.md)

## Compressed full-text and sequence indexes

### 12. [simongog/sdsl-lite](https://github.com/simongog/sdsl-lite)

**C++ — succinct data structures, especially compressed suffix arrays and trees.** The selected subsystem is its text-indexing stack. This is the historical SDSL 2 repository; its last recorded push was in 2023. Other SDSL forks are not counted as separate entries.

- **C1/C2:** `csa_wt` composes wavelet trees, suffix/inverse-suffix sampling policies, and alphabet representations through templates with explicit constraints. Copying must also reconnect sampling support structures to the copied storage. [Compressed suffix-array implementation](https://github.com/simongog/sdsl-lite/blob/master/include/sdsl/csa_wt.hpp)
- **C3:** Sampling density and representation choices expose memory/query tradeoffs. Shared construction, serialization, memory accounting, and succinct rank/select components let an engineer compare index configurations within one framework; the project also documents its unit-testing approach. [Library architecture and examples](https://github.com/simongog/sdsl-lite/blob/master/README.md)

### 13. [dynatrace-oss/index4j](https://github.com/dynatrace-oss/index4j)

**Java — FM indexing for arbitrary substrings, including logs.** Study a compressed text index that can recover surrounding records without storing a second uncompressed corpus.

- **C1/C2:** Count, locate, bounded extraction, and extraction-to-delimiter share an index containing cumulative counts, sampled positions, RRR bitvectors, and a wavelet representation. The API spells out Java character-unit limits and makes extraction support optional. [FM-index implementation](https://github.com/dynatrace-oss/index4j/blob/main/indices/src/main/java/com/dynatrace/fm/FmIndex.java)
- **C3:** Fixed-block-boosted wavelet storage and configurable sampling trade compressed size against locate/extract work. The guide demonstrates caller-supplied output buffers and extracting complete log records around matches. Independent bitvector and wavelet structures are also reusable. [Usage and data-structure details](https://github.com/dynatrace-oss/index4j/blob/main/README.md)

### 14. [TravisWheelerLab/AvxWindowFmIndex](https://github.com/TravisWheelerLab/AvxWindowFmIndex)

**C — SIMD FM index for nucleotide and amino-acid sequences.** This is deliberately restricted to biological alphabets and is unsuitable for general text. Study specialization of rank/occurrence queries and batch execution.

- **C1/C3:** Occurrence routines encode symbols across bit planes and combine SIMD masks to identify positions. Nucleotide, ambiguity, and sentinel encodings are distinguished; sentinel symbols are excluded from searchable cases. [Occurrence implementation](https://github.com/TravisWheelerLab/AvxWindowFmIndex/blob/master/src/AwFmOccurrence.c)
- **C2/C3:** The library exposes index creation/loading, configurable suffix-array sampling, seed lookup tables, optional disk-resident suffix samples, and parallel batches of queries. These provide meaningful latency/memory choices. [API and configuration](https://github.com/TravisWheelerLab/AvxWindowFmIndex/blob/master/README.md)

Its repository design document declares itself outdated; it was not used as the authority for current layout details. Last repository push recorded: 2024.

### 15. [SGSSGene/fmindex-collection](https://github.com/SGSSGene/fmindex-collection)

**C++20 — interchangeable FM-index structures and approximate-search algorithms.** A useful research-oriented framework for comparing occurrence representations and bidirectional search rather than committing to one fixed index layout.

- **C1:** The bidirectional implementation maintains forward/reverse BWT consistency, cumulative counts, and sparse position annotations. Collection construction maps samples back to sequence IDs and positions; locating accounts for steps between samples. Delimiter and reverse-storage policies are explicit template choices. [Bidirectional index](https://github.com/SGSSGene/fmindex-collection/blob/main/src/fmindex-collection/fmindex/BiFMIndex.h)
- **C2/C3:** A string concept defines symbol access, rank, prefix-rank, and combined rank operations, allowing different compressed representations to serve the same index algorithms. This is a concrete abstraction boundary for comparing storage layouts and batched rank work. [Rank-support concept](https://github.com/SGSSGene/fmindex-collection/blob/main/src/fmindex-collection/string/concepts.h)

Some published documentation uses older type signatures; consult the linked source for current interfaces.

### 16. [seqan/seqan3](https://github.com/seqan/seqan3)

**C++ — the FM-index and search subsystem of the larger sequence-analysis library.** Counted once as a repository. Its value here is the typed index/cursor layer and the handling of text collections, not the unrelated alignment or file-format modules.

- **C1:** Input validators enforce alphabet and range constraints. Sentinel remapping reserves high byte ranks, with an additional delimiter restriction for collections. Copy/move behavior must preserve internal support structures. The source also warns that a changing default index type can affect persistent formats. [FM-index implementation](https://github.com/seqan/seqan3/blob/main/include/seqan3/search/fm_index/fm_index.hpp)
- **C2:** Typed alphabets, single-text/collection layouts, configurable underlying SDSL indexes, and cursor-based traversal separate storage from search usage. The changelog records fixes involving one-text collections, null terminators, and cursor/interface changes, making those abstractions' edge cases traceable. [Subsystem evolution](https://github.com/seqan/seqan3/blob/main/CHANGELOG.md)

### 17. [xxsds/DYNAMIC](https://github.com/xxsds/DYNAMIC)

**C++ — dynamic succinct structures and incrementally extended FM indexes.** The current canonical repository is `xxsds/DYNAMIC`; the README retains an older `nicolaprezza/dynamic` clone URL. The important limitation is that its BWT/FM-index supports **left extension**, not arbitrary text editing or deletion.

- **C1:** Extending the indexed text updates the BWT, sampled-position bitvector, and suffix samples together. Text positions are measured from the end, and a reserved alphabet value represents the terminator. Locate walks to a marked sample and adds the traversal distance. [Dynamic FM-index](https://github.com/xxsds/DYNAMIC/blob/master/include/dynamic/internal/fm_index.hpp)
- **C2/C3:** Cache-oriented B-tree partial sums underpin dynamic bitvectors, wavelet strings, run-length strings, BWTs, and indexes. Entropy and run-length representations can be composed; the documentation candidly identifies incomplete deletion support and allocator fragmentation. [Structure hierarchy and limitations](https://github.com/xxsds/DYNAMIC/blob/master/README.md)

### 18. [nicolaprezza/r-index](https://github.com/nicolaprezza/r-index)

**C++ — run-length BWT index for repetitive text.** A historical research-library implementation, with its last repository push recorded in 2023. Study the reusable `ri::r_index` class; the supplied command-line programs are benchmark drivers, not end-user search applications.

- **C1:** Construction ties run-boundary suffix samples to a predecessor structure. `Phi` navigation requires careful circular-predecessor, run-number, sentinel, and modular-position invariants, expressed through assertions. Reserved input bytes and inclusive search intervals are explicit. [Index and navigation implementation](https://github.com/nicolaprezza/r-index/blob/master/internal/r_index.hpp)
- **C3:** Storage and locating are organized around BWT runs rather than uniform dense sampling. The README explains the revised strategy of finding one suffix-array position and navigating neighboring occurrences with `Phi`. [Design and research context](https://github.com/nicolaprezza/r-index/blob/master/README.md)

Integration requires care: invalid reserved input can terminate the process, and locating materializes a result vector. These are useful study limitations, not endorsements of a hardened library interface.

## Embedded inverted-index and document-search libraries

### 19. [apache/lucene](https://github.com/apache/lucene)

**Java — core text indexing, postings, and index lifecycle.** The selected subsystem is `lucene/core`; this is the embedded library rather than a separately deployed search service.

- **C1:** A single thread-safe writer coexists with point-in-time readers. Segment cores, live-document changes, atomic document replacement, merges, and reassigned document IDs create substantial visibility and identity invariants. The package documentation explains why document IDs must remain internal. [Index architecture](https://github.com/apache/lucene/blob/main/lucene/core/src/java/org/apache/lucene/index/package-info.java)
- **C2/C3:** Term enumeration supports ordered traversal, exact/ceiling seeks, optional postings detail, iterator reuse, and saved term state. Two-phase exact seeks allow prefetching across terms while imposing explicit sequencing and thread constraints. This is a concrete example of an extensible traversal API exposing performance opportunities without hiding its invariants. [Term and postings interface](https://github.com/apache/lucene/blob/main/lucene/core/src/java/org/apache/lucene/index/TermsEnum.java)

### 20. [quickwit-oss/tantivy](https://github.com/quickwit-oss/tantivy)

**Rust — embedded full-text indexing and search.** Study how compact immutable segments coexist with continuous ingestion, deletion, and background merging.

- **C1:** The index writer manages worker lifecycles, a shared ingestion queue, directory locking, and ordered operations. Delete processing checks operation stamps so that a deletion affects documents inserted before it, not later replacements. [Writer and deletion implementation](https://github.com/quickwit-oss/tantivy/blob/main/src/indexer/index_writer.rs)
- **C2/C3:** A `Directory` abstraction and memory-mapped storage support access to compact on-disk structures. RAM buffers become independently searchable segments, and background merging limits accumulation of small segments. Memory budgets and queue backpressure connect the architecture to resource limits. [Index anatomy](https://github.com/quickwit-oss/tantivy/blob/main/doc/src/basis.md)

### 21. [blevesearch/bleve](https://github.com/blevesearch/bleve)

**Go — document indexing; focus on the Scorch text-index backend.** Study snapshot-based search and segment lifecycle underneath the higher-level mapping and query API.

- **C1:** Scorch separates immutable segment contents from per-snapshot deletion sets. Readers retain their snapshot while updates produce another view. Current source uses explicit reference counting and synchronization to delay segment reclamation and protect shared reader caches. [Snapshot implementation](https://github.com/blevesearch/bleve/blob/master/index/scorch/snapshot_index.go)
- **C2/C3:** The design maps batches, documents, fields, dictionaries, postings, and positional data onto the existing indexing API. Segment dictionary access can run concurrently, and the implementation merges dictionary cursors with a heap. [Scorch design](https://github.com/blevesearch/bleve/blob/master/index/scorch/README.md)

The design document includes proposal-era sketches; the linked implementation was checked to distinguish the current snapshot machinery from those sketches.

### 22. [xapian/xapian](https://github.com/xapian/xapian)

**C++ with language bindings — embedded probabilistic text search.** This is the project's substantive GitHub **mirror**. The selected subsystem is `xapian-core`, not the Omega application or unrelated auxiliary modules.

- **C1:** The database API documents commit failures, locking, transaction cancellation on close, format-version errors, and the distinction between single-shard atomicity and the absence of cross-shard atomicity. Its explicit contracts make failure semantics a productive study area. [Database API contracts](https://github.com/xapian/xapian/blob/main/xapian-core/include/xapian/database.h)
- **C2/C3:** Reference-counted implementation objects give inexpensive API copies and retain dependencies. Queries combine boolean structure with ranking; database backends sit behind a common interface. Buffered updates and explicit commits expose the tradeoff between publication frequency and indexing throughput. [API design overview](https://github.com/xapian/xapian/blob/main/xapian-core/docs/overview.rst)

### 23. [nextapps-de/flexsearch](https://github.com/nextapps-de/flexsearch)

**JavaScript — browser and Node.js text indexing.** Useful for studying client-side indexing choices where memory expansion and main-thread responsiveness matter.

- **C1/C3:** Token insertion handles duplicate suppression, score buckets, forward/reverse/full token expansion, and contextual indexing. The code explicitly avoids dropping duplicates when that would break a context chain. Comparing the tokenizer branches reveals why substring indexing can consume much more work and storage than exact-token indexing. [Index construction](https://github.com/nextapps-de/flexsearch/blob/master/src/index/add.js)
- **C2/C3:** Worker indexes retain an asynchronous search/index interface, while document workers partition work by field. The guide explains promises, bulk operations, and external configuration for custom functions that cannot simply cross worker boundaries. [Worker architecture](https://github.com/nextapps-de/flexsearch/blob/master/doc/worker.md)

No headline benchmark multiplier from the project is adopted as a general performance claim.

### 24. [olivernn/lunr.js](https://github.com/olivernn/lunr.js)

**JavaScript — compact browser full-text search.** A smaller architectural comparison with FlexSearch and server-oriented indexing libraries. The last repository push recorded was in 2024; current maintenance is not assumed.

- **C1/C3:** The token vocabulary and incoming queries are represented as finite-state automata and intersected before postings lookup. Sharing prefixes and suffixes reduces vocabulary storage; wildcard and edit operations complicate intersection semantics. The code documents the rapid cost growth of larger edit distances. [Token-set implementation](https://github.com/olivernn/lunr.js/blob/master/lib/token_set.js)
- **C2:** The builder separates field configuration, document references, tokenization, indexing/search pipelines, scoring parameters, and metadata retention. It documents configuration-order constraints and how field/document boosts affect indexing. [Index builder](https://github.com/olivernn/lunr.js/blob/master/lib/builder.js)

## Coverage, search process, and limits

Discovery used more than six distinct live-search formulations, including general multi-pattern/Aho–Corasick libraries across languages; SIMD multi-regex engines; double-array and compressed tries; suffix-array construction; FM-index libraries for text and sequences; embedded Go/Rust/JavaScript search; dynamic compressed indexing; run-length/repetitive-text indexing; .NET/SQL CLR matching; and GPU failureless, Wu–Manber, and Commentz–Walter implementations. Follow-up inspection used official repositories, GitHub API directory listings and file contents, project documentation, and changelogs. Each retained repository has a verified canonical GitHub identity and separately inspected implementation or documentation beyond its repository description.

Later searches expanded coverage with DYNAMIC and the r-index, then increasingly returned existing candidates, ports, small experiments, and wrappers. This is a representative selection, not an exhaustive inventory. GPU matching and .NET implementations were explored but are not represented in the retained set; no claim is made that those ecosystems lack strong codebases.

Thin wrappers such as `ahocorasick_rs`, R bindings to SDSL, and Python bindings to suffix-sorting libraries were not counted separately from the underlying implementations. Hyperscan was researched, but Vectorscan represents that lineage here because its independent portability and maintenance work was inspected. SDSL variants likewise were not multiplied into separate entries. Search servers and complete aligner applications were excluded to keep the focus on libraries. Smaller Java matchers were considered, with the retained double-array implementation offering a clearer fit for this selection's construction-versus-runtime comparison.

All investigation was read-only: no candidate repository was cloned, built, installed, or executed. Performance discussion describes source-backed mechanisms and documented tradeoffs, not independently reproduced measurements. C4 is awarded only where multi-year changes and compatibility/correctness work were inspected. Historical and research-oriented entries remain worthwhile study candidates, but their APIs, tests, and failure handling should not be presumed uniformly exemplary. Source links target the inspected default branches and may evolve after the research date.
