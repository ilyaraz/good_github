# Generic container and algorithm libraries

Research date: **2026-10-09**.

This selection covers reusable in-memory collections and algorithms over arbitrary element types: owning and intrusive containers, fixed-capacity storage, hash tables, balanced trees, persistent collections, and composable iteration. The 25 repositories span C, C++, Rust, Java, Swift, Go, Haskell, C#, JavaScript, Python, Julia, and OCaml. Broader utility repositories are included only for identified collection subsystems. These are study recommendations grounded in the cited material, not certifications of every component or benchmark claims.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions serving many use cases. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — sustained evolution with evidence of compatibility work, testing, or complexity management. Each entry justifies at least two criteria; absence of a criterion is not a negative assessment.

## C++: storage policy, invariants, and generic algorithms

### 1. [boostorg/container](https://github.com/boostorg/container)

**Language / role:** C++; owning STL-like containers and alternative sequence layouts.

Study how storage layout changes an otherwise familiar interface. The documentation contrasts a `flat_map` stored as one sorted sequence of key/value pairs with a `devector` that keeps contiguous storage while supporting growth at both ends.

- **C1:** `devector` exposes unusually instructive capacity and exception-safety contracts: internal relocation affects reference validity, insertion lacks a strong exception guarantee in documented cases, and ordinary vector assumptions about `size()` versus `capacity()` do not transfer unchanged.
- **C2:** Generic containers, sequence customization, and ordered-range operations serve many element types and workloads.
- **C3:** The design explains binary-search lookup versus linear insertion for flat containers and when `devector` relocates existing elements instead of allocating another buffer. These are explicit layout and amortization tradeoffs. [Non-standard container design guide](https://www.boost.org/doc/libs/latest/doc/html/container/non_standard_containers.html).

**Entry point:** the linked design guide, especially `flat_map` and `devector`. This is the official Boost.Container module repository, counted separately from the different intrusive implementation below.

### 2. [boostorg/intrusive](https://github.com/boostorg/intrusive)

**Language / role:** C++; intrusive collection building blocks with STL-like interfaces.

Study the separation between an object's lifetime and its membership in a data structure. Hooks put linkage in user objects, making membership state part of an explicit contract rather than hiding it inside an owning container.

- **C1:** Safe-link hooks initialize a recognizable unlinked state, check it before insertion and destruction, and restore it on erasure. This makes double insertion and destruction of linked objects concrete invariant violations with configurable assertions.
- **C2:** The hook/container interface supports reusable intrusive structures and higher-level uses such as allocation machinery and composite indexes, identified in the repository overview. [Safe-hook design](https://www.boost.org/doc/libs/latest/doc/html/intrusive/safe_hook.html).

**Entry point:** the safe-hook documentation. Its assertions detect misuse; they do not transfer lifetime ownership to the container.

### 3. [abseil/abseil-cpp](https://github.com/abseil/abseil-cpp)

**Language / role:** C++; the `absl::container` subsystem of a larger foundational library.

Study how a collection library deliberately changes contracts to enable different layouts. The relevant families are flat and node Swiss tables plus ordered B-tree containers, not Abseil's unrelated utilities.

- **C1:** The guide specifies rehash invalidation and address stability separately for flat and node tables. It also explains how changed iteration order can expose order-dependent floating-point accumulation bugs.
- **C2:** Maps, sets, multi-containers, and heterogeneous lookup provide a broad reusable interface.
- **C3:** Inline key/value slots versus separately allocated nodes make memory locality and stable addresses competing choices. Heterogeneous lookup avoids temporary key construction; the erase interface is chosen to support constant-time erasure. [Container guide](https://abseil.io/docs/cpp/guides/container).

**Entry point:** the container guide. Abseil explicitly cautions that these containers are not universal drop-in replacements for their standard-library counterparts.

### 4. [electronicarts/EASTL](https://github.com/electronicarts/EASTL)

**Language / role:** C++; a general template collection and algorithm library shaped by game-development requirements.

Study allocation as a first-class container policy. The design explains instance-accessible allocators, fixed pools, container validation, and specialization of algorithms by element and iterator traits.

- **C2:** A consistent container interface and iterator-based algorithms allow reuse across containers and ordinary arrays.
- **C3:** Fixed containers reuse regular container implementations through allocators pointing into their own storage. The design explicitly weighs small object overhead against implementation duplication and code size. Empty containers avoid initial allocation, and validation can be invoked explicitly because exhaustive checking has a runtime cost. [Design document](https://github.com/electronicarts/EASTL/blob/master/doc/Design.md).

**Entry point:** the allocator, fixed-container, and algorithm sections of the design document. Treat its comparisons with other STL implementations as historical motivation, not independently reproduced performance results; its stated policy permits usage restrictions in pursuit of efficiency.

### 5. [ETLCPP/etl](https://github.com/ETLCPP/etl)

**Language / role:** C++; Embedded Template Library, focusing here on containers and their generic algorithms.

Study reusable APIs under fixed memory budgets. ETL's container model places storage inside fixed-capacity objects rather than relying on heap growth.

- **C2:** The `icontainer<T>` layer lets a function accept containers of the same element type but different capacities; users do not need to template every consumer on the storage size.
- **C3:** The three-layer architecture separates type-and-size-independent code, type-dependent code, and the small portion dependent on both type and capacity. This addresses generated code size as well as predictable storage requirements. [Container architecture tutorial](https://www.etlcpp.com/docs/tutorials/containers-tutorial/).

**Entry point:** the tutorial's `container_base` → `icontainer<T>` → `container<T, N>` design. The selection concerns this concrete embedded collection architecture, not every messaging or device-oriented module in the repository.

### 6. [ericniebler/range-v3](https://github.com/ericniebler/range-v3)

**Language / role:** C++; range algorithms, lazy views, eager actions, and iterator construction machinery.

Study how algorithms become composable without prescribing a storage container. The manual explains range overloads, view state machines, `view_facade`, and `view_adaptor`.

- **C1:** A view may carry mutable iteration state even when it reads constant elements. The manual distinguishes view constness from element constness and explains that underlying mutation can invalidate a view, including some mutations that affect filtering.
- **C2:** Reusable views, actions, iterator concepts, and range algorithms work across independent collection implementations.
- **C3:** Lazy pipelines defer work until iteration; keeping state in the view can keep its iterators small. [User manual](https://ericniebler.github.io/range-v3/).

**Entry point:** the manual's view semantics and custom-view sections. Its development-status statement does not promise general long-term backward compatibility, with a narrower exception for `ranges::cpp20`.

## C: genericity without language templates

### 7. [stclib/STC](https://github.com/stclib/STC)

**Language / role:** C99/C11; typed container templates and general collection algorithms.

Study preprocessor specialization coupled to explicit value lifecycle operations. The hash-map implementation instantiates a shared map/set design and supplies cloning, dropping, raw-key conversion, lookup, and allocation-failure paths.

- **C1:** The implementation must preserve ownership of nontrivial keys and values while maintaining Robin Hood probing metadata. The source separates key/value clone and drop operations and returns an unsuccessful insertion result when reservation fails.
- **C2:** A common template mechanism supports maps, sets, sequences, strings, spans, and algorithms over user-defined types.
- **C3:** `hmap` packs a hash fragment and probe distance into metadata and specializes operations through macros. [Hash-map implementation](https://raw.githubusercontent.com/stclib/STC/main/include/stc/hmap.h).

**Entry point:** `include/stc/hmap.h`. The reviewed repository announces a version 6 release candidate and documents breaking changes; do not infer a settled API from the breadth of its container family. This is the upstream repository, not the STC forks also returned by search.

### 8. [JacksonAllan/CC](https://github.com/JacksonAllan/CC)

**Language / role:** C, also usable from C++; a single-header generic container library.

Study a different solution to C genericity: the API deduces element-specific behavior without requiring a new container type declaration for every combination of types.

- **C1:** Allocation success is not assumed, and custom destructors, hashing, and comparison introduce lifecycle and semantic obligations that the API must preserve across its collection families.
- **C2:** A unified typed interface covers vectors, lists, unordered and ordered associative containers, and strings.
- **C3:** The author's implementation article explains extendible `_Generic` dispatch, selecting hash/comparison/destructor functions at compile time instead of storing function pointers in each container. [Generic-dispatch design article](https://github.com/JacksonAllan/CC/blob/main/articles/Better_C_Generics_Part_1_The_Extendible_Generic.md).

**Entry point:** the design article, read alongside the repository's allocation-failure examples. It offers a useful comparison with STC's template-instantiation approach.

## Rust: compact storage, ownership, and persistent values

### 9. [rust-lang/hashbrown](https://github.com/rust-lang/hashbrown)

**Language / role:** Rust; SwissTable-derived generic hash maps and sets.

Study the boundary between safe collection APIs and an unsafe storage engine. The current raw implementation explains probing, allocation layout, control groups, capacity arithmetic, and zero-sized element handling.

- **C1:** The probe sequence must cover the table, missing-key lookup must terminate, and capacity calculations must avoid overflow. The source explicitly reserves empty space for termination and separates fallible allocation from aborting/panicking paths.
- **C3:** Group-based probing and compact control metadata are integrated with platform alignment and small-table allocation choices. [Raw table implementation](https://raw.githubusercontent.com/rust-lang/hashbrown/main/src/raw.rs).

**Entry point:** `src/raw.rs`. This is a substantive Rust implementation, not a wrapper around Abseil. The repository also distinguishes its default hasher's HashDoS resistance from the standard library's choice; table layout and adversarial hashing policy are separate decisions.

### 10. [indexmap-rs/indexmap](https://github.com/indexmap-rs/indexmap)

**Language / role:** Rust; maps and sets supporting deterministic sequence order and numeric indexing.

Study the synchronization of two representations: a hash table containing indices and a dense vector containing key/value pairs. The repository explains the locality advantage for iteration and the extra indirection during lookup.

- **C1:** Removal semantics are explicit: swapping an entry out can alter order, whereas shifting removal preserves relative order. Both representations must stay consistent through reordering and mutation.
- **C3:** Dense iteration, compact index storage, and different deletion strategies expose useful time/locality tradeoffs. [Architecture discussion in the repository](https://github.com/indexmap-rs/indexmap#performance).
- **C4:** Dated releases from 2024–2026 document minimum-Rust-version changes, hashbrown migrations, internal simplification, bounds-check consolidation, and macro-hygiene fixes. [Release history](https://github.com/indexmap-rs/indexmap/blob/main/RELEASES.md).

**Entry points:** the architecture discussion and release history. IndexMap adds a substantial storage/ordering layer over hashbrown, so the two are not duplicate entries.

### 11. [rust-itertools/itertools](https://github.com/rust-itertools/itertools)

**Language / role:** Rust; generic iterator adaptors and collection-processing algorithms.

Study algorithms packaged as iterator state machines. A particularly readable starting point is the merge of multiple sorted input iterators: each live input contributes a head element and a remaining iterator.

- **C1:** The merge implementation handles empty inputs, exhaustion, ordering predicates, and aggregate size hints while preserving its heap invariant.
- **C2:** Iterator and comparator parameters make the algorithm reusable across unrelated storage types and element orderings.
- **C3:** A heap of live heads avoids collecting and sorting the full combined input; the sift-down implementation comments on branch behavior and handles the final single-child case explicitly. [Multiway-merge implementation](https://raw.githubusercontent.com/rust-itertools/itertools/master/src/kmerge_impl.rs).

**Entry point:** `src/kmerge_impl.rs`, including `HeadTail`, `heapify`, and `KMergeBy::next`. Its sorted-output guarantee assumes appropriately sorted inputs and a suitable ordering predicate.

### 12. [orium/rpds](https://github.com/orium/rpds)

**Language / role:** Rust; persistent lists, vectors, queues, hash tries, and red-black collections.

Study structural sharing with a configurable reference-counting pointer kind. The repository explains why thread-sharing capability is opt-in and how `Rc`-like versus `Arc`-like pointer choices fit the same collection abstraction.

- **C1:** The hash-trie implementation documents branching by hash segments, terminal full-hash collisions, and structural invariants. Updates must preserve earlier versions while maintaining those invariants.
- **C2:** Several collection families expose persistent operations and optional mutable operations through reusable generic types.
- **C3:** Shared nodes make cheap version creation possible; parameterizing pointer ownership makes synchronization overhead a deliberate choice. [Hash-trie implementation and invariant commentary](https://raw.githubusercontent.com/orium/rpds/main/src/map/hash_trie_map/mod.rs).

**Entry point:** `src/map/hash_trie_map/mod.rs`. Thread sharing is a type-level option, not a claim that every configuration is interchangeable across threads.

## Java and C#: broad collection frameworks

### 13. [eclipse-collections/eclipse-collections](https://github.com/eclipse-collections/eclipse-collections)

**Language / role:** Java; object and primitive collections, iteration protocols, and collection factories.

Study how a wide API family coexists with specialized representations. The relevant monorepo components are the collection API, implementations, primitive-generation machinery, and their dedicated tests.

- **C2:** Readable, mutable, immutable, eager, lazy, and parallel collection interfaces support common use cases while preserving interoperability with Java collection types.
- **C3:** `UnifiedMap` stores alternating keys and values in one array. Collisions use secondary arrays rather than an allocated entry object per mapping; the implementation describes the locality rationale directly. [UnifiedMap implementation](https://raw.githubusercontent.com/eclipse-collections/eclipse-collections/master/eclipse-collections/src/main/java/org/eclipse/collections/impl/map/mutable/UnifiedMap.java).

**Entry point:** `UnifiedMap.java`. Its sentinel objects and collision paths also provide useful correctness study material. The presence of parallel APIs does not make this particular mutable map safe for unsynchronized concurrent mutation.

### 14. [vigna/fastutil](https://github.com/vigna/fastutil)

**Language / role:** Java with preprocessor driver sources; type-specific collections and large-index storage.

Study the maintainable source of a large specialized API rather than only its generated classes. The driver files implement actual algorithms and generate primitive/object combinations; this is not a generated-wrapper project.

- **C2:** Maps, sets, lists, queues, custom hashing strategies, and large-index collections extend familiar Java interfaces while permitting primitive specialization.
- **C1:** The open-hash-map driver explains why shrinking is suppressed during iterator removal and how linked variants preserve insertion order using a parallel array of links.
- **C3:** Load thresholds govern growth and shrinkage, while specialized storage avoids requiring boxed values throughout the implementation. [Open-hash-map driver](https://raw.githubusercontent.com/vigna/fastutil/master/drv/OpenHashMap.drv).

**Entry point:** `drv/OpenHashMap.drv`. The linked variant deliberately has limitations relative to the full `SortedMap` contract, documented in its source comments.

### 15. [vavr-io/vavr](https://github.com/vavr-io/vavr)

**Language / role:** Java; the persistent collection subsystem of a functional programming library.

Study how APIs change when updates return a new value. The guide connects immutable linked lists, a queue built from front/rear lists, and path-copying balanced trees to their public operations.

- **C1:** Old collection versions must survive updates. The queue must reverse and transfer its rear list at the right boundary, while sorted sets maintain ordering and red-black balance. Empty dequeue is offered with both throwing and optional-result semantics.
- **C2:** A shared persistent collection model spans sequences, sets, and maps, with `Iterable` integration rather than pretending that Java's mutating collection interface has the same semantics.
- **C3:** Structural sharing and path reconstruction avoid copying an entire collection for each update. [User guide, functional data structures](https://docs.vavr.io/#_functional_data_structures).

**Entry point:** guide sections 1.3–1.5. The reviewed guide identifies itself as version 0.11.0; the repository advertises a later release, so use the guide for architecture rather than an exhaustive current API reference.

### 16. [sestoft/C5](https://github.com/sestoft/C5)

**Language / role:** C#/.NET; a comprehensive generic collection framework with a long historical lineage.

Study interface organization and framework evolution together. The authors describe separate collection capabilities, updatable views, hash-indexed lists, persistent trees, and priority queues with item handles. [Official research overview](https://vipwww.itu.dk/research/c5/).

- **C2:** The interface hierarchy supports coding against collection capabilities across multiple implementations, including directed enumeration, indexed and sorted collections, dictionaries, and priority queues.
- **C4:** The release notes trace concrete changes from 2004 through 2024: .NET interface integration, fixes to view updates and range indexing, framework-target migrations, replacing custom tuple-like abstractions, and removal of serialization attributes. The repository documents its NUnit test suite. [Release notes](https://github.com/sestoft/C5/blob/master/RELEASE-NOTES.md).

**Entry points:** the research overview and detailed release notes. The research website is historical and last updated in 2016; the repository's release notes are the better source for later .NET changes. No claim of a current rapid release cadence is made.

## Swift and Go: collection protocols and concrete data structures

### 17. [apple/swift-collections](https://github.com/apple/swift-collections)

**Language / role:** Swift; generic collection implementations including deques, ordered collections, heaps, and persistent hash trees.

Study how value semantics and collection protocols constrain representation. `OrderedDictionary` is especially useful because ordered traversal, unique keys, and key-based subscripting must coexist.

- **C1:** Ordered equality depends on entry order. Key uniqueness prevents unrestricted mutable-collection conformance, and a separate `elements` view avoids ambiguity between integer keys and positional indices.
- **C2:** Protocol-based generic collections support different ordering, ownership, and access requirements within one package.
- **C3:** The ordered-dictionary design combines hashing with efficient positional traversal; the repository also identifies ring-buffer deques with copy-on-write value semantics. [OrderedDictionary design/API guide](https://github.com/apple/swift-collections/blob/main/Documentation/OrderedDictionary.md).

**Entry point:** `Documentation/OrderedDictionary.md`. The repository distinguishes stable modules from explicitly unstable experimental features; do not apply stable-API expectations to every advertised type.

### 18. [apple/swift-algorithms](https://github.com/apple/swift-algorithms)

**Language / role:** Swift; generic sequence and collection algorithms with design proposals.

Study algorithms expressed in terms of collection capabilities rather than integer-indexed arrays. The rotation guide is a concise example of API shape, mutation semantics, and performance being designed together.

- **C2:** Rotation operates on `MutableCollection`; the broader package supplies chunking, combinations, permutations, sampling, and other reusable sequence operations.
- **C3:** The guide provides subrange overloads to avoid copy-on-write problems from slice mutation in divide-and-conquer algorithms. It also explains why bidirectional collections admit a rotation implementation requiring fewer swaps than the general case. [Rotation design guide](https://github.com/apple/swift-algorithms/blob/main/Guides/Rotate.md).

**Entry point:** `Guides/Rotate.md`, which links its implementation and tests. The repository documents public-API semantic versioning separately from the policy for increasing the required Swift toolchain.

### 19. [zyedidia/generic](https://github.com/zyedidia/generic)

**Language / role:** Go; reusable generic trees, maps, ropes, heaps, and other collections.

Study a smaller, modular collection library with unusual sequence structures. Its persistent rope stores arbitrary elements, distinguishing it from text-only rope packages.

- **C1:** Persistent updates copy changed paths and share unaffected nodes. The source explicitly warns that the constructor retains the caller's slice, so later external mutation can violate the expected persistence contract.
- **C2:** Independent packages offer AVL and interval trees, heaps, bidirectional maps, ordinary and persistent ropes, and more.
- **C3:** The rope exposes leaf split/join thresholds and explains the space benefit of sharing versions. Rebalancing can allocate substantially and is a separate operation worth inspecting. [Persistent-rope implementation](https://raw.githubusercontent.com/zyedidia/generic/master/prope/prope.go).

**Entry point:** `prope/prope.go`. Its documented complexity statements depend on structural balance; this selection does not independently establish worst-case bounds for arbitrary operation sequences.

### 20. [tidwall/btree](https://github.com/tidwall/btree)

**Language / role:** Go; generic ordered maps, sets, and comparator-based B-trees.

Study a specialized container engine rather than a broad framework. The public API includes ordered scans, positional operations, bulk loading, and copy-on-write copies.

- **C2:** Ordered map/set wrappers and a comparator-based tree let one storage engine serve different key and value models.
- **C3:** Path hints retain the traversal positions from earlier operations, exploiting locality among nearby keys. The design explains how an incorrect hint is corrected instead of being treated as authoritative. [Path-hint design](https://github.com/tidwall/btree/blob/master/PATH_HINT.md).

**Entry point:** `PATH_HINT.md`. The hint itself is mutated, and the author recommends separate hints for separate threads. Thread-safety claims in the repository apply to specified tree types, not automatically to every wrapper or shared hint. No numerical speedup is adopted here.

## Functional and dynamic-language collection ecosystems

### 21. [haskell/containers](https://github.com/haskell/containers)

**Language / role:** Haskell; persistent maps, sets, sequences, and related foundational containers.

Study balancing algorithms alongside evaluation semantics and compiler specialization. `Data.Map.Internal` explains both the mathematical tree family and code-generation choices that are easy to miss in a purely abstract presentation.

- **C1:** The map representation uses size-balanced binary trees, while its lazy internal interface is strict in keys and lazy in values. Correct updates must preserve balancing, ordering, and the intended evaluation behavior.
- **C2:** Polymorphic container interfaces support user-defined key orderings and reusable whole-collection operations.
- **C3:** Implementation notes distinguish `INLINABLE` specialization from selective `INLINE`, leaving rebalancing out of some inlined paths to control code growth. [Map implementation and design notes](https://raw.githubusercontent.com/haskell/containers/master/containers/src/Data/Map/Internal.hs).

**Entry point:** `containers/src/Data/Map/Internal.hs`. This is a study entry point: the file explicitly excludes its internal API from the package's normal versioning guarantees.

### 22. [immutable-js/immutable-js](https://github.com/immutable-js/immutable-js)

**Language / role:** JavaScript, with TypeScript declarations; persistent collections and lazy sequences.

Study the coexistence of immutable public values and controlled internal mutation. Hash and vector tries share unchanged structure; temporary ownership allows batches of updates to avoid repeatedly copying paths.

- **C1:** The map distinguishes owned mutable state from persistent state through owner identifiers. Clearing and updating must preserve prior versions, invalidate cached hashes where needed, and maintain size and alteration bookkeeping.
- **C2:** Maps, lists, sets, ordered variants, records, and lazy sequences form a reusable collection-processing API.
- **C3:** Structural sharing and `withMutations` address repeated-update allocation costs. [Map implementation](https://raw.githubusercontent.com/immutable-js/immutable-js/main/src/Map.js).

**Entry point:** `src/Map.js`, particularly construction, `clear`, and `__ensureOwner`. Persistent collection structure does not imply deep immutability of arbitrary JavaScript objects stored inside it.

### 23. [grantjenks/python-sortedcontainers](https://github.com/grantjenks/python-sortedcontainers)

**Language / role:** Python; sorted list, dictionary, and set implementations.

Study a practical alternative to pointer-heavy balanced trees. The design divides a sorted list into sublists and maintains both per-block maxima and a positional index of block lengths.

- **C1:** Search and positional indexing depend on agreement among `_lists`, `_maxes`, and the pairwise-sum `_index`. Splitting and merging blocks must update these related structures coherently.
- **C2:** Sorted sequences and associative collections provide reusable ordered lookup, range access, and positional operations.
- **C3:** The implementation deliberately exploits optimized Python list movement and dense references, with load-factor-based block sizing to limit typical insert/delete movement. [Implementation details](https://grantjenks.com/docs/sortedcontainers/implementation.html).

**Entry point:** the implementation guide. Its own discussion acknowledges different asymptotic tradeoffs from balanced trees; this report does not generalize its benchmark claims to every workload or Python runtime.

### 24. [JuliaCollections/DataStructures.jl](https://github.com/JuliaCollections/DataStructures.jl)

**Language / role:** Julia; generic containers including priority queues, heaps, disjoint sets, and sorted collections.

Study Julia-specific representation and dispatch choices using sorted containers as the entry point. They share a 2–3 tree representation whose key/data pairs and tree structure live in separate vectors.

- **C1:** Key ordering/equality and token validity are explicit contracts. Before-start and past-end tokens have restricted operations, and mutable keys can undermine ordering assumptions.
- **C2:** `SortedDict`, `SortedMultiDict`, and `SortedSet` parameterize key type and ordering; the package adds many other reusable structures.
- **C3:** Tokens permit direct item access, while smaller semitokens can avoid allocations associated with carrying the container reference. The documentation explains this representation and the operation costs. [Sorted-container design and API](https://juliacollections.github.io/DataStructures.jl/stable/sorted_containers/).

**Entry point:** the sorted-container guide, especially representation, tokens, and ordering. This is one package entry, not separate entries for each data structure.

### 25. [c-cube/ocaml-containers](https://github.com/c-cube/ocaml-containers)

**Language / role:** OCaml; modular standard-library collection extensions, combinators, and additional data structures.

Study the engineering of generic collection operations as the host compiler and standard library evolve. The relevant scope is the collection/combinator core and persistent-vector work, rather than unrelated codecs or process utilities.

- **C1:** Release notes document a `CCList.flat_map` bug tied to unspecified evaluation order and subsequent changes using standard-library `concat_map` on newer OCaml versions. They also record persistent-vector test expansion and a test-size explosion discovered in CI.
- **C2:** Independent prefixed modules and an optional `Containers` overlay offer reusable list, array, map, iterator, and vector operations without requiring one monolithic application framework. [Repository architecture overview](https://github.com/c-cube/ocaml-containers#quick-summary).
- **C3:** The release history records implementation choices for list operations, including version-dependent tail-modulo-cons support and faster `take_drop`, exposing the relationship between generic APIs and compiler behavior. [Detailed releases](https://github.com/c-cube/ocaml-containers/releases).

**Entry points:** the architecture overview and implementation-oriented release notes, especially versions 3.13.1 and 3.17–3.18. The repository explicitly describes `containers-data` as less thoroughly maintained; do not assume identical maturity across subpackages.

## Coverage, search process, and limitations

Discovery used more than six distinct live-web search formulations, including C++ allocator/intrusive designs; C type-safe generics; Rust hash tables and persistence; JVM primitive and persistent collections; Swift collection protocols; Go generic trees and ropes; Haskell persistent maps; Python sorted structures; Julia collections; C# frameworks; OCaml combinators; and embedded fixed-capacity containers. Follow-up searches broadened toward less familiar implementations, then returned many already-covered families, forks, comparison lists, and educational collections. The selection stops at 25 substantial examples rather than counting every alternative within each family.

Every retained canonical GitHub repository page was opened, and additional primary documentation, implementation source, or detailed release material was read for each. Raw source links above identify implementation files, not duplicate copies of a README. C5 and OCaml-containers rely more heavily on official architectural overviews and implementation-oriented release notes because several direct source-page retrievals failed; these are useful study entries but have less direct source inspection in this pass. Some other GitHub rendering failures were resolved through raw implementation files. Linked default-branch documentation can change after the research date.

The report deliberately excludes tutorial/exercise collections, awesome lists, non-substantive wrappers, and duplicate STC forks. Language compiler/runtime monorepos were not added merely to count their standard libraries; standalone collection libraries provide a more bounded reading scope. Dedicated graph, numerical, distributed-storage, and concurrency frameworks fall outside this selection's center of gravity. Broad ecosystems such as Scala and Kotlin therefore remain underrepresented, and this is not an exhaustive catalog.

Repository identity and category fit are verified facts; the criteria and suggested study paths are engineering judgments based on the linked evidence. No candidate code was executed, dependencies installed, or reported benchmark results reproduced. A repository's inclusion does not establish current maintenance responsiveness. Historical documentation is labeled where relevant, and no fork, archived project, or unofficial mirror is intentionally presented as an independent current upstream.
