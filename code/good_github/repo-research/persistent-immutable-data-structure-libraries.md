# Persistent immutable data structure libraries

Research date: **2026-10-09**.

This selection covers 27 GitHub repositories implementing reusable collections whose previous versions remain usable after updates, usually through structural sharing. It includes general collection libraries, language-library subsystems, and specialized persistent trees and union-find structures. “Persistent” here concerns versions in memory, rather than durability on disk. Mutable builders, transients, reference counting, and copy-on-write internals belong in scope when they preserve the public snapshot contract. Immutability of a container does not automatically make its stored objects immutable or make every builder safe for concurrent use.

The entries are a guide to architectural study, not a ranking or a claim that every component is uniformly exemplary. Repository pages and additional primary implementation or design material were opened for every selection. Criteria identify what the inspected evidence supports; absence of a criterion is not a negative assessment.

## Criteria legend

- **C1 — Difficult correctness:** structural invariants, ownership, concurrency, equality, adversarial inputs, or failure handling require substantial care.
- **C2 — Reusable abstractions:** collection interfaces, configurable policies, or composition mechanisms support multiple applications.
- **C3 — Performance with understandable structure:** allocation, locality, copying, parallelism, or asymptotic costs are addressed through identifiable architectural choices.
- **C4 — Sustained evolution:** dated history shows years of compatibility work, testing improvements, or management of implementation complexity. Repository age alone is insufficient.

## C and C++: ownership, allocation, and parallel trees

### [arximboldi/immer](https://github.com/arximboldi/immer)

**Language / role:** C++; persistent vectors, maps, and related collections with configurable memory management.

Immer is especially useful for studying how a persistent API can exploit C++ ownership information. Its design distinguishes ordinary functional updates, temporary transient mutation, and operations on rvalues that may reuse uniquely owned storage. **C1:** these optimizations must preserve all surviving versions while obeying reference-count and lifetime rules; the documentation also distinguishes immutable objects from mutable variables holding them. **C3:** move-aware updates and transients reduce repeated allocation during update sequences, with a clear account of when copying remains necessary. [Design entry point](https://sinusoid.es/immer/design.html).

**C2:** memory policies separate collection algorithms from heaps, reference counting, locking, and transience. This makes the library relevant to both ordinary applications and environments with different allocation or reclamation requirements. **C3:** the memory documentation describes thread-local and shared free-list layers, and the tradeoffs of tracing garbage collection versus reference counting. [Memory-policy entry point](https://sinusoid.es/immer/memory.html).

### [mkirchner/hamt](https://github.com/mkirchner/hamt)

**Language / role:** C99; a compact HAMT library exposing both destructive and persistent update operations.

This is a focused entry point for understanding what a garbage-collected language normally hides. **C1:** the implementation combines tagged pointers, bitmap-indexed compact tables, hash-fragment traversal, and a mechanism for obtaining another hash when the current hash has been consumed. Correctness depends on those representation rules and on the caller's hashing and allocation contracts. **C3:** bitmap/popcount addressing avoids allocating a full child array at each sparse trie node; persistent updates copy the affected path. [Implementation entry point](https://github.com/mkirchner/hamt/blob/main/src/hamt.c).

**C2:** hashing, comparison, and allocation are supplied through interfaces, allowing reuse with different key types and memory systems. The repository documentation explicitly distinguishes `hamt_set`/`hamt_remove` from `hamt_pset`/`hamt_premove` and explains the reclamation problem created by shared persistent nodes. Ordinary allocation alone does not solve that problem. The README has unfinished sections, so this is a useful implementation study with an incomplete guide, rather than evidence of polished documentation. Its relatively quiet activity is noted below.

### [cmuparlay/PAM](https://github.com/cmuparlay/PAM)

**Language / role:** C++; parallel augmented ordered maps, sets, and sequences.

PAM makes balancing and augmentation into reusable building blocks. **C2:** a map can maintain an aggregate over each subtree, supporting applications such as range queries, interval search, and inverted indexes. The central `join` abstraction lets higher-level operations be expressed separately from the balancing scheme. **C3:** that separation also exposes parallel set algebra and batch operations, rather than treating persistence as a sequence of isolated insertions. [Architecture and application entry point](https://cmuparlay.github.io/PAMWeb/index.html).

**C1:** path copying, subtree augmentation, balancing, and reference-counted reclamation must agree while versions share nodes. The project documentation discusses concurrent access through persistent snapshots and explicitly distinguishes that capability from automatically providing serializable transactions. An engineer can study both the compositional tree algorithms and the boundary between a concurrent data structure and an application-level update protocol. This is a research-oriented library; the published applications establish intended uses, not universal production guarantees.

### [ParAlg/CPAM](https://github.com/ParAlg/CPAM)

**Language / role:** C++; compressed parallel augmented maps, distributed as a research library and artifact.

CPAM is retained separately from PAM because its PaC-tree representation adds substantive implementation work: balanced trees have blocked leaves stored in compressed arrays. **C3:** this changes the tradeoff between pointer overhead, compression, and the work required to update a block while retaining persistent versions. **C2:** the architecture supports generic augmented maps and parallel operations including union, intersection, filtering, reduction, and range queries. [Authors' architecture paper](https://www.cs.umd.edu/~laxman/papers/cpam.pdf).

**C1:** encoding must preserve ordered keys, values, and augmentation consistently across compression and decompression. The implementation's difference encoder separates encoded key differences from values and incorporates augmentation through callbacks, making these obligations visible in code. [Compression entry point](https://github.com/ParAlg/CPAM/blob/main/include/cpam/compression.h). This is a good companion to PAM for examining how representation changes affect the same abstract operations. The report does not reproduce the paper's benchmark results or infer production maturity from the artifact.

## Rust: pointer policies and collection families

### [orium/rpds](https://github.com/orium/rpds)

**Language / role:** Rust; persistent lists, vectors, queues, stacks, hash tries, and ordered collections.

RPDS exposes a useful connection between data structure design and the cost of shared ownership. **C2:** its collection family is parameterized by a shared-pointer abstraction, allowing related APIs to use reference counting appropriate to their threading requirements. **C3:** this keeps single-threaded users from necessarily paying for atomic reference counts, while shared-node updates use copy-on-write mechanisms.

**C1:** the hash-trie map source documents concrete shape rules: only the root can be an empty branch, non-root branches have minimum occupancy requirements, and collision nodes occur at the end of available hash depth. Insertions and removals must preserve these distinctions while sharing unaffected nodes. Collision buckets and sparse arrays are explicit types, rather than incidental cases hidden in one large routine. [Hash-trie implementation and invariant entry point](https://github.com/orium/rpds/blob/main/src/map/hash_trie_map/mod.rs). Study the pointer-policy boundary alongside branch contraction and collision handling; thread-safe variants remain subject to Rust's bounds on their contents.

### [jneem/imbl](https://github.com/jneem/imbl)

**Language / role:** Rust; a continuing implementation of the `im` family of persistent collections.

This is the selected continuation of `im`, rather than a second entry for substantially the same ancestor. **C1:** the vector implementation must keep inline, single-chunk, and full RRB-tree representations consistent, including size and boundary conditions during splits and updates. **C3:** small-value representations, head/tail chunks, and shared-pointer parameters expose explicit allocation and locality choices. The source includes invariant-checking machinery that helps make the transitions reviewable. [Vector entry point](https://github.com/jneem/imbl/blob/main/src/vector/mod.rs).

**C4:** the changelog documents development across 2021–2026, including a B+tree rewrite of ordered collections, shared-pointer generalization, aliasing-related fixes, and corrections to differences across shared nodes. It also records API and dependency changes rather than presenting all releases as interchangeable. This is evidence of substantive evolution beyond a renamed fork. **C2:** the shared collection APIs cover sequences, hash collections, and ordered maps/sets. [Evolution entry point](https://github.com/jneem/imbl/blob/main/CHANGELOG.md).

## JavaScript, TypeScript, Python, and Ruby

### [immutable-js/immutable-js](https://github.com/immutable-js/immutable-js)

**Language / role:** JavaScript with TypeScript-facing APIs; general persistent collections and lazy sequence operations.

The library combines persistent maps and vectors with ordered collections, records, nested updates, and sequence transformations. **C2:** those common operations allow application state and derived views to use a consistent collection vocabulary, rather than requiring separate APIs for each representation.

**C1:** the map source makes the temporary-mutation boundary concrete through owner identities. A node can be edited in place only under the appropriate owner; otherwise updates construct a new root or path. No-op updates can return the existing collection. **C3:** bitmap-indexed trie nodes compact sparse branches, while `withMutations` batches edits so that each intermediate logical update need not allocate an independent persistent path. [Map and mutation entry point](https://github.com/immutable-js/immutable-js/blob/main/src/Map.js). An experienced engineer can follow a public update down to node ownership and then compare it with lazy `Seq` processing, which addresses a different source of intermediate allocation.

### [funkia/list](https://github.com/funkia/list)

**Language / role:** TypeScript; an RRB-tree persistent sequence library.

This narrower project is valuable for studying efficient concatenation and slicing rather than another general hash-map API. **C1:** relaxed nodes need cumulative size information and correct offset calculations because child subtrees need not all have equal capacity. The implementation distinguishes regular and relaxed navigation and copies affected paths during updates. **C3:** the RRB representation permits reuse of subtrees across sequence operations while retaining indexed access. [Representation and indexing entry point](https://github.com/funkia/list/blob/master/src/index.ts).

**C2:** the repository exposes a substantial sequence interface with functional, curried, and method-oriented usage, plus iteration and conversion facilities. That makes the tree reusable in application pipelines rather than only a standalone algorithm demonstration. The code is a useful contrast with ordinary persistent vectors, whose concatenation is less central to their design. Repository activity is relatively quiet; inclusion is for the implementation and abstraction, not a claim of current maintenance intensity.

### [tobgu/pyrsistent](https://github.com/tobgu/pyrsistent)

**Language / role:** Python with a C vector implementation; collections, immutable records/classes, and checked containers.

Pyrsistent connects structural persistence to application-level validation. **C2:** vectors, maps, sets, records, classes, and nested transformations support both generic containers and structured domain objects. **C1:** checked types and record invariants introduce correctness requirements beyond tree shape, while evolvers must allow temporary editing without changing the original persistent value. These facilities are described in the repository's API-oriented README.

**C3:** the Python vector implementation exposes a branching trie and tail together with dirty-node and leaf tracking for evolvers, so repeated edits can reuse work before producing the next persistent value. It also makes tradeoffs visible: some slice paths materialize ordinary Python lists instead of preserving every possible subtree. The project supplies Python and C vector implementations behind compatible APIs. [Python vector and evolver entry point](https://github.com/tobgu/pyrsistent/blob/master/pyrsistent/_pvector.py). This is particularly useful for comparing understandable reference code with an accelerated implementation without assuming that every operation has the same cost model.

### [MagicStack/immutables](https://github.com/MagicStack/immutables)

**Language / role:** Python/C; a persistent hashable mapping with batch mutation support.

The implementation is a focused study of HAMTs under Python's object and error-handling rules. **C1:** equal hash values require explicit collision nodes, while lookup and removal have distinct success, absence, empty-node, and error outcomes. Reference management and propagation of Python-level failures accompany the trie invariants. **C3:** bitmap nodes pack sparse children; dense array nodes avoid repeated sparse indexing at higher occupancy; updates share unchanged paths. The large implementation comment explains these representations before the algorithms. [HAMT implementation and architecture entry point](https://github.com/MagicStack/immutables/blob/master/immutables/_map.c).

**C2:** the public `Map` presents familiar mapping behavior, equality, hashing, and serialization support, making it useful outside one framework. Its mutation context and finalization API provide a reusable mechanism for constructing the next snapshot efficiently. The combination of a small public abstraction and substantial internal machinery makes this a good contrast with Pyrsistent's broader family of validated data types.

### [immutable-ruby/immutable-ruby](https://github.com/immutable-ruby/immutable-ruby)

**Language / role:** Ruby; persistent hashes, vectors, sets, sorted sets, lists, and deques.

This is the continuation fork selected in place of also listing its Hamster ancestor; the repository describes fixes and optimizations while retaining the earlier API under a different module name. That lineage statement is not a claim of recent activity. **C2:** the collection family works with Ruby's enumeration conventions and includes lazy-list operations, providing substantial integration with ordinary Ruby programs.

**C1:** the trie implementation protects a subtle key invariant by duplicating and freezing mutable string keys; structural persistence alone would not prevent a key's hash from changing. Updates preserve existing versions by replacing only affected entries and children. **C3:** bulk insertion delays copying backing arrays until an actual change requires it, and identity-preserving no-op paths avoid unnecessary new versions. [Trie and bulk-update entry point](https://github.com/immutable-ruby/immutable-ruby/blob/master/lib/immutable/trie.rb). Stored objects are not universally deep-frozen, so the snapshot guarantee should not be extended to arbitrary mutable payloads. Activity is relatively quiet, as noted below.

## JVM collection ecosystems

### [hrldcpr/pcollections](https://github.com/hrldcpr/pcollections)

**Language / role:** Java; persistent collections integrated with standard Java collection interfaces.

PCollections offers a different starting point from the usual HAMT tutorial. **C1:** its integer tree stores keys relative to parent nodes, balances by subtree size, and uses wider arithmetic for key differences. Shifting a range of logical indices must preserve ordering and avoid overflow, making it instructive for persistent indexed sequences. **C3:** relative keys allow operations to adjust whole regions without individually rewriting every key. [Integer-tree entry point](https://github.com/hrldcpr/pcollections/blob/master/src/main/java/org/pcollections/IntTree.java).

**C2:** persistent producer methods coexist with Java collection interfaces across lists, maps, sets, stacks, and bags. **C4:** the dated changelog documents 2018–2025 work on iterator contracts, serialization, null handling, stack-overflow bugs, navigable collections, and supported Java versions. These are concrete examples of preserving usable behavior as the implementation and platform evolve. [Compatibility and maintenance entry point](https://github.com/hrldcpr/pcollections/blob/master/CHANGELOG.md).

### [usethesource/capsule](https://github.com/usethesource/capsule)

**Language / role:** Java; persistent sets and maps using compact hash-array mapped tries, or CHAMP.

Capsule is a strong representation-focused study because its design aims for a compact, canonical layout rather than treating all HAMTs as equivalent. **C3:** separate occupancy information for data and child nodes supports packed storage and efficient traversal/equality behavior. **C1:** cached collection size and hash information must remain consistent with the trie, and temporary mutation must preserve published persistent values. The map source includes internal checking that recomputes aggregates through iteration. [Persistent map entry point](https://github.com/usethesource/capsule/blob/main/src/main/java/io/usethesource/capsule/core/PersistentTrieMap.java).

**C2:** the immutable and transient interfaces provide reusable collection components intended for uses such as language runtimes and analysis tools. The repository connects the implementation to the CHAMP design and related research, making it useful for tracing a memory-layout argument into code. The project describes itself as an incubating library; inclusion therefore reflects the implementation's substance rather than an assumption that its API has the stability of a platform standard library.

### [lacuna/bifurcan](https://github.com/lacuna/bifurcan)

**Language / role:** Java; persistent collection interfaces spanning maps, lists, sets, ropes, and graphs.

Bifurcan explores how one collection vocabulary can support both ordinary functional use and efficient temporary linear use. **C2:** custom hashing/equality, common collection interfaces, splitting and merging, and graph/string structures extend its usefulness beyond a replacement for `java.util.Map`.

**C1:** map nodes combine separate data/child bitmaps, collision handling, subtree sizes, and an editor identity controlling whether mutation is permitted. Correct subtree sizes also support positional lookup operations. **C3:** the implementation deliberately leaves unused buffer capacity in editable nodes to amortize future writes, while structural bulk operations can reuse persistent subtrees. [Map-node entry point](https://github.com/lacuna/bifurcan/blob/master/src/io/lacuna/bifurcan/nodes/MapNodes.java). Study how the linear/forked API maps to those edit identities, and how a representation optimized for repeated local edits can still serve immutable snapshots. The broader repository is worth exploring for abstractions, but the inspected map core is the principal evidence here.

### [Kotlin/kotlinx.collections.immutable](https://github.com/Kotlin/kotlinx.collections.immutable)

**Language / role:** Kotlin Multiplatform; immutable and persistent collection interfaces with builders.

The design explicitly separates read-only interfaces from immutable values and persistent update APIs. **C2:** collection interfaces and builders carry that distinction across Kotlin targets and familiar collection operations. **C1:** covariance and builder behavior must remain sound while builders offer mutation-like methods; building or editing a derived value must not modify its source collection. [API and representation design entry point](https://github.com/Kotlin/kotlinx.collections.immutable/blob/master/docs/proposal.md).

**C3:** the design discusses trie-backed lists with tails, compact small collections, and different costs for ordered and unordered maps/sets. Those choices make the overhead of preserving iteration order explicit. The proposal is design evidence, not a promise that every implementation detail remains frozen. The repository currently labels the library experimental, so engineers should study both the interface distinctions and the associated compatibility caveat rather than treating it as a permanently fixed standard-library contract.

### [clojure/clojure](https://github.com/clojure/clojure)

**Language / role:** Java/Clojure; the persistent collection subsystem of the Clojure runtime. The monorepo counts once.

The runtime is a foundational example of persistent collections forming the default language data model. **C2:** maps, vectors, and sets participate in common protocols, equality, metadata, and sequence operations, making the abstractions reusable throughout programs. **C1:** the hash-map implementation has explicit collision nodes, null-key handling, and hashing/equality semantics that must agree with the rest of the runtime. **C3:** path copying and specialized node representations keep unchanged portions shared. [Persistent hash-map entry point](https://github.com/clojure/clojure/blob/master/src/jvm/clojure/lang/PersistentHashMap.java).

The transient API adds another important correctness boundary. **C1:** transient use requires isolation, and finalizing a transient invalidates its further use; aliases must obey that lifecycle. **C3:** temporary editing avoids constructing a full succession of persistent paths during bulk construction. The documentation carefully distinguishes the isolation requirement from historical thread-affinity enforcement. [Transient contract entry point](https://clojure.org/reference/transients). The selection concerns these collections, not an assessment of the compiler or every runtime subsystem.

### [clojure/core.rrb-vector](https://github.com/clojure/core.rrb-vector)

**Language / role:** Clojure/ClojureScript; RRB vectors compatible with native vector operations.

This project adds structural concatenation and slicing to a familiar persistent-vector model. **C2:** compatibility with ordinary vector operations, including relevant primitive and transient paths, lets applications adopt the representation without adopting an unrelated sequence API. **C3:** concatenation and non-view slicing reuse appropriate subtrees; slicing need not retain an entire original vector merely because a small region remains in use. The repository README explains the RRB motivation and interface.

**C1:** the change history exposes difficult failure modes rather than just successful examples: overly tall sparse trees, fullness checks, primitive association, pop bounds, and a hashing race. It also records debug-checking helpers and reorganized tests for concatenation and slicing. [Correctness-history entry point](https://github.com/clojure/core.rrb-vector/blob/master/CHANGES.md). These details make it especially valuable for studying why relaxed vector algorithms require more than adapting ordinary indexed trie lookup. No independent performance reproduction was performed for this report.

### [scala/scala](https://github.com/scala/scala)

**Language / role:** Scala; immutable collections in the Scala 2.13 standard library. The language monorepo counts once.

The relevant subsystem combines persistent representations with a large generic collections API. **C2:** immutable maps integrate with collection factories, transformations, views, and specialized traversal interfaces. This is useful for studying the constraints imposed when persistence must fit a broadly used language library rather than a small standalone package.

**C1:** the immutable hash-map source includes an explicit publication fence because construction can mutate intermediate state before the completed value becomes visible. It also connects map nodes to collection-wide hashing and equality behavior. **C3:** CHAMP nodes provide a compact representation, and primitive-specialized steppers address traversal overhead; unchanged roots can be reused by no-op operations. [Scala 2.13 immutable HashMap entry point](https://github.com/scala/scala/blob/2.13.x/src/library/scala/collection/immutable/HashMap.scala). The selection is specifically the Scala 2 collection implementation at the verified branch, not a claim that this repository contains the Scala 3 compiler.

## Functional-language libraries and specialized persistence

### [haskell/containers](https://github.com/haskell/containers)

**Language / role:** Haskell; ordered maps/sets, integer collections, and persistent sequences.

Containers offers multiple persistent tree families in one widely reusable package. **C1:** the map implementation combines size-balanced trees with explicit strictness rules: keys and the tree structure have different evaluation behavior from values. **C3:** its implementation notes discuss specialization, inlining, allocation, and code-size tradeoffs, connecting the abstract algorithm to compiled performance. [Map implementation entry point](https://github.com/haskell/containers/blob/master/containers/src/Data/Map/Internal.hs).

**C2:** `Map`, `Set`, integer-key collections, and `Seq` serve different ordering and access requirements under coherent functional APIs. **C1/C3:** `Seq` uses size-annotated 2–3 finger trees, where cached measures support indexing and splitting while the representation supports operations at both ends and concatenation. [Sequence implementation entry point](https://github.com/haskell/containers/blob/master/containers/src/Data/Sequence/Internal.hs). These internal modules are study locations, not recommendations to depend on their unstable implementation interfaces. Comparing the two trees is more informative than treating “persistent collection” as one uniform cost model.

### [haskell-unordered-containers/unordered-containers](https://github.com/haskell-unordered-containers/unordered-containers)

**Language / role:** Haskell; persistent hash maps and hash sets.

This library provides a useful counterpoint to ordered `containers`. **C2:** it supplies general hash-based map/set abstractions, allowing clients to choose hashing rather than ordering as the key contract. **C1:** the developer guide distinguishes empty, bitmap-indexed, full, leaf, and collision nodes and explains the collision and hashing obligations. It also discusses adversarial inputs and historical hash-function tradeoffs, so the code should not be assumed resistant to every hash-flooding workload merely because it is immutable.

**C3:** the same guide connects bitmap/popcount addressing, dense-node transitions, and fanout to copying and memory costs. Its discussion of strictness and compiler annotations explains why a source-level allocation pattern may matter in a lazy language. [Architecture and optimization entry point](https://github.com/haskell-unordered-containers/unordered-containers/blob/master/docs/developer-guide.md). Historical implementation anecdotes in that guide are treated as design context, not as a guarantee about the exact hash algorithm selected by every current dependency configuration.

### [slburson/fset](https://github.com/slburson/fset)

**Language / role:** Common Lisp; functional sets, maps, bags, sequences, and additional collection abstractions.

FSet stands out for supporting nested collection values and for taking ordering semantics seriously. **C2:** collection algebra and arbitrary nesting allow applications to use sets and maps as values and keys rather than treating persistence as a thin wrapper around mutable tables.

**C1:** the weight-balanced tree implementation handles objects that compare as order-equivalent without necessarily being equal. Explicit equivalence nodes and a richer comparison result complicate ordinary search-tree invariants in a useful, documented way. **C3:** small vectors replace the lowest tree levels to reduce node overhead, and the code explains how comparison counts and modified balance conditions interact with that representation. [Weight-balanced tree entry point](https://github.com/slburson/fset/blob/master/Code/wb-trees.lisp). This is a substantial alternative to the more frequently discussed HAMT lineage: an engineer can study equality/order separation, leaf blocking, and functional collection algebra together.

### [codex-semantics-library/union-find-lattice](https://github.com/codex-semantics-library/union-find-lattice)

**Language / role:** OCaml; persistent union-find structures with lattice operations, intended for program-analysis-style uses.

This recent research-oriented repository broadens the selection beyond containers. **C2:** classic, labeled, and valued variants expose reusable functor interfaces; operations include combining and comparing equivalence relations, rather than only answering connectivity queries. [Classic interface entry point](https://github.com/codex-semantics-library/union-find-lattice/blob/main/union-find-lattice/Classic.mli).

**C1:** the Patricia-tree implementation maintains representative and rank information, including explicit representation of nontrivial roots needed by relation-level operations. **C3:** operations can traverse differences between persistent maps instead of blindly processing every shared binding. [Implementation entry point, particularly `PatriciaTree`](https://github.com/codex-semantics-library/union-find-lattice/blob/main/union-find-lattice/Classic.ml).

There is an important qualification from reading the code: `PatriciaTree` supports optional lazy path compression through a mutable field. Select the configuration with path compression set to `None` when studying strictly immutable internals; externally persistent behavior does not by itself establish concurrent-read safety for every configuration. Rerooted persistent-array implementations have different mutation concerns, and the mutable `ArrayWithCopy` baseline is outside this entry's category fit. No C4 maturity claim is made for this recent project.

## Go, .NET, F#, and Swift

### [benbjohnson/immutable](https://github.com/benbjohnson/immutable)

**Language / role:** Go; generic persistent lists, maps, sorted maps, and sets.

The library combines a deliberately familiar Go API with several persistent representations. **C2:** hash maps accept custom hashing/equality, sorted maps use comparers, and list/map builders offer a common bulk-construction pattern. The README identifies HAMT maps and B+tree sorted maps, giving useful contrasts within one package.

**C1:** persistent list updates shallow-copy the outer value and replace the relevant tree path; builders have a separate mutation lifecycle and are invalid after producing the finished collection. Bounds and ownership boundaries remain part of the contract even though garbage collection handles reclamation. **C3:** a root, origin, and size describe the list, and builder-specific mutable updates reduce repeated path copying during construction. [Collection implementation entry point](https://github.com/benbjohnson/immutable/blob/master/immutable.go). The repository describes a deliberately conservative feature policy. Its relatively quiet activity should be evaluated in that context, without interpreting either the policy or a last-push date as proof of ongoing support.

### [hashicorp/go-immutable-radix](https://github.com/hashicorp/go-immutable-radix)

**Language / role:** Go; persistent radix trees with transactions and mutation notifications.

This is a specialized alternative to hash tries when prefix and ordered-key operations matter. **C2:** longest-prefix lookup, ordered traversal, and snapshot-based updates make the abstraction useful for indexes and configuration or routing-like state. **C1:** transaction cloning must stop subsequent writes from affecting a clone; the implementation resets its writable-node cache to maintain that boundary. Change-notification channels introduce another obligation: updates must notify the right observers even when bookkeeping limits are reached. [Tree and transaction entry point](https://github.com/hashicorp/go-immutable-radix/blob/master/iradix.go).

**C3:** transactions reuse writable nodes for batches, with bounded caches controlling auxiliary memory. Overflow handling trades more work for bounded tracking space. The source explicitly says transactions themselves are not thread-safe; safe sharing of completed tree snapshots must not be generalized to concurrent use of a mutable transaction. The interaction between persistence, watches, and bounded caching is the main architectural reason to study this implementation.

### [dotnet/runtime](https://github.com/dotnet/runtime)

**Language / role:** C#; the `System.Collections.Immutable` subsystem. The runtime monorepo counts once.

The relevant library exposes reusable immutable list, map, set, queue, and related interfaces and builders. **C2:** those APIs integrate persistent values with .NET collection conventions and packaging. [Subsystem entry point](https://github.com/dotnet/runtime/blob/main/src/libraries/System.Collections.Immutable/README.md). The category fit rests on the structurally shared collections, not on assuming that every immutable array operation shares a tree.

**C1:** `ImmutableList<T>` uses AVL nodes with cached height and subtree count. Nodes must be frozen before a wrapping immutable collection exposes them, and a frozen parent requires frozen children. **C3:** mutation helpers create replacements for frozen nodes but update unfrozen nodes in place; freezing is therefore the concrete boundary enabling both efficient construction and safe sharing. Rotations must preserve height, count, and the freeze contract. [Immutable-list node entry point](https://github.com/dotnet/runtime/blob/main/src/libraries/System.Collections.Immutable/src/System/Collections/Immutable/ImmutableList_1.Node.cs). This is a clear example of logically immutable public values built using controlled internal mutation.

### [fsprojects/FSharpx.Collections](https://github.com/fsprojects/FSharpx.Collections)

**Language / role:** F# with .NET and Fable considerations; the persistent collection subset of a broader collection library.

The selection concerns persistent vectors, hash maps, queues, deques, and related functional structures, rather than mutable helpers elsewhere in the repository. **C2:** these structures provide reusable alternatives suited to different access patterns and interoperability requirements.

**C1:** the persistent-vector implementation exposes root growth, tail transitions, and editable-node checks. Its transient path tracks edit ownership, with platform-specific handling for .NET and Fable, illustrating why an algorithm port also needs to account for the target runtime. [Persistent-vector entry point](https://github.com/fsprojects/FSharpx.Collections/blob/master/src/FSharpx.Collections/PersistentVector.fs).

**C4:** the release notes document work across 2015–2022 on collection edge cases, a CHAMP implementation, threading-related comparison fixes, Fable support, FSharp.Core references, target frameworks, and tests against newer .NET versions. This is concrete compatibility and complexity-management evidence rather than an age-based inference. [Release-history entry point](https://github.com/fsprojects/FSharpx.Collections/blob/master/RELEASE_NOTES.md). Those documented years do not establish that every module receives equally frequent current changes.

### [apple/swift-collections](https://github.com/apple/swift-collections)

**Language / role:** Swift; specifically `HashTreeCollections` and its `TreeDictionary`/`TreeSet`. The repository counts once.

These collections use persistent CHAMP trees under Swift value semantics. **C2:** dictionary/set-style interfaces let applications retain many related values while continuing to use familiar generic collection operations. Mutation syntax on a variable does not negate the preservation of other value copies.

**C1:** the dictionary source tracks index invalidation through version state and specifies key-identity behavior when replacing an equal key's value. Such observable semantics must survive internal sharing and updates. **C3:** unchanged branches are shared, and structural comparison can skip identical subtrees. The documentation also acknowledges the pointer indirection and allocation costs relative to flat storage, making this an unusually useful source for understanding when persistent trees help and when they impose overhead. [TreeDictionary implementation and design entry point](https://github.com/apple/swift-collections/blob/main/Sources/HashTreeCollections/TreeDictionary/TreeDictionary.swift). The selection applies to this subsystem, not to an assertion that all collections in the package are persistent trees.

## Search coverage, exclusions, and limitations

Discovery used live web searches with substantially more than six distinct formulations. Search angles included:

- General persistent/immutable libraries combined with HAMT, CHAMP, RRB, and structural-sharing terminology.
- C/C++ ownership and allocation, parallel augmented maps, and compressed persistent trees.
- Rust collection families, shared-pointer choices, and the `im`/`imbl` lineage.
- Python persistent records and C-extension maps; JavaScript/TypeScript sequence and hash-trie implementations.
- Java/Kotlin CHAMP implementations, Clojure transients and RRB vectors, and Scala immutable collections.
- Haskell balanced trees and finger trees, Common Lisp functional collections, and OCaml persistent union-find/lattice structures.
- Go immutable radix trees and generic collections; F# Okasaki-style collections, .NET immutable internals, and Swift hash trees.
- Additional targeted searches for persistent deques/finger trees, smaller CHAMP projects, and Dart immutable collections. These later searches increasingly repeated selected lineages or returned wrappers and small demonstrations, rather than adding a comparably distinct implementation.

All 27 canonical repository URLs were checked against repository pages or the GitHub API, and every retained repository had an additional primary design, implementation, interface, or history source opened. None was marked archived in the metadata checked on the research date. No moved-away project without a substantive GitHub implementation, or official mirror needing separate attribution, was retained. The source links above use verified branches, but remain moving references rather than a frozen reproducibility bundle.

Activity varies. GitHub metadata reported the latest repository pushes in August 2023 for [benbjohnson/immutable](https://api.github.com/repos/benbjohnson/immutable), January 2024 for [funkia/list](https://api.github.com/repos/funkia/list), February 2024 for [mkirchner/hamt](https://api.github.com/repos/mkirchner/hamt), and April 2024 for [immutable-ruby/immutable-ruby](https://api.github.com/repos/immutable-ruby/immutable-ruby). These are quiet code-study candidates; push timestamps do not prove either abandonment or support. CPAM is identified as a research artifact, and the recent union-find project is included for distinct architecture without a claim of long-term maturity. C4 is used only where substantive dated history was read.

Excluded scope includes disk-persistence engines, read-only wrappers around mutable collections, generated bindings counted separately from their implementation, tutorial-only repositories, and list-of-links repositories. The predecessor `im` and Hamster repositories were not double-counted alongside their selected continuations. CPAM remains separate from PAM because its compressed PaC-tree implementation is a substantive architectural extension, not merely a repackaged fork. Other plausible collections were left out where they would add less architectural coverage; this is not a claim that all alternatives were exhaustively audited.

The criteria assessments are reasoned judgments grounded in the linked primary material. Descriptions of invariants, representations, and documented compatibility work are factual observations; suitability as an engineering study target is an inference. No candidate code was executed, dependencies installed, or benchmarks independently reproduced. Numerical performance comparisons from project marketing and papers were deliberately not adopted. Source inspection also does not establish that all advertised invariants are bug-free or that mutable payloads, transients, or every configuration are safe for concurrent use.
