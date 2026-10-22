# Garbage collectors

Research date: **2026-10-09**.

This report selects **24 GitHub repositories** implementing automatic memory reclamation: reusable collectors, collector construction frameworks, cycle collectors, and substantial collector subsystems inside language runtimes. It includes conservative and precise tracing, copying and nonmoving heaps, generational and concurrent collection, actor-local collection, and reference counting with cycle detection. Each monorepo appears once; its relevant subsystem is identified. This is a source-reading selection guide, not a benchmark ranking or a claim that every component is uniformly exemplary.

The criteria assessments below are engineering judgments grounded in the linked primary material:

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial conditions, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or components supporting multiple applications or collector designs.
- **C3 — Performance and structure:** concrete latency, throughput, memory, or locality constraints addressed through an understandable architecture.
- **C4 — Evolution:** documented development across years together with compatibility work, testing, or complexity management.

Repository identities, default branches, and archive flags were checked through GitHub pages or its API. None of the selected repositories was marked archived. Official mirrors and notable historical or experimental selections are labeled below. Links to development branches describe the inspected code, which may differ from released versions; repository activity alone is not treated as evidence for C4 or a maintenance guarantee.

## Reusable collectors and construction frameworks

### [bdwgc/bdwgc](https://github.com/bdwgc/bdwgc)

**Language/role:** C, with C++ integration; Boehm–Demers–Weiser conservative collector. The former `ivmai/bdwgc` URL redirects here.

Study how a collector works with ordinary C object layouts, ambiguous pointers, interior pointers, native stacks, and platform-dependent root discovery. Its architecture exposes the practical consequences of collecting an environment that does not precisely identify every reference.

- **C1:** The marker recovers from mark-stack overflow by returning to an invalid-mark state and rescanning while preserving forward progress. Pointer recognition and blacklisting address false pointer candidates rather than assuming perfect heap metadata.
- **C3:** Size-and-kind free lists, allocation-triggered lazy sweeping, and thread-local allocation reduce page touches and allocation-lock traffic. The design explicitly separates fast allocation paths from initialization and collection work.

**Entry point:** Boehm's [algorithm and data-structure overview](https://www.hboehm.info/gc/gcdescr.html) connects these mechanisms to implementation names. Its platform discussion contains historical details, so use the [current repository](https://github.com/bdwgc/bdwgc) for contemporary support boundaries.

### [Ravenbrook/mps](https://github.com/Ravenbrook/mps)

**Language/role:** C; Memory Pool System, combining automatic and manual memory-management policies.

Study how arenas, pools, object formats, roots, and protection barriers make multiple memory-management strategies coexist. This is especially useful for understanding the contract between an embedding runtime and a collector.

- **C1:** The Shield separates collector access from mutator access using memory protection and thread control. Nested expose/cover operations and special handling for unprotectable roots make the access invariants explicit in the [Shield design](https://memory-pool-system.readthedocs.io/en/latest/design/shield.html).
- **C2:** Pool classes and client-defined object formats provide reusable policy and representation boundaries rather than imposing one language's object model.
- **C4:** The repository documents development since 1994; its [release notes](https://github.com/Ravenbrook/mps/blob/master/NEWS) record successive API deprecations, platform changes, thread initialization fixes, and signal/fork behavior corrections.

**Status:** Established implementation with extensive design material; GitHub's API reported its last push in November 2024. That observation does not establish the status of commercial support.

### [mmtk/mmtk-core](https://github.com/mmtk/mmtk-core)

**Language/role:** Rust; language-independent Memory Management Toolkit.

Study the separation of a collector algorithm from heap-space policies, allocation semantics, mutator barriers, and scheduled collection work. It is a strong starting point for comparing algorithms without changing the entire surrounding runtime.

- **C2:** A plan combines spaces and page accounting with a mutator definition, allocator mappings, constraints, and `GCWork` tasks. The [plan module](https://github.com/mmtk/mmtk-core/blob/master/src/plan/mod.rs) documents these extension boundaries and exposes copying, Immix, mark-sweep, and other families.
- **C4:** The [2020–2026 changelog](https://github.com/mmtk/mmtk-core/blob/master/CHANGELOG.md) records binding API changes, metadata refactoring, sanity checks, VM integration tests, and multiple collector additions. This supports sustained complexity management, without implying a permanently stable API.
- **C1:** The same history gives concrete correctness examples: forwarding and stack-scanning races, out-of-memory callback loops, atomic barrier state, and pinning support for concurrent collection.

### [eclipse-omr/omr](https://github.com/eclipse-omr/omr)

**Language/role:** C/C++; reusable runtime components, specifically the `gc` subsystem.

Study how industrial collector machinery is factored away from a particular language. The repository also contains compiler and portability components, but this selection concerns managed-heap collection.

- **C2:** The marking implementation obtains object scanners through a delegate while retaining common mark maps, per-worker environments, and work-packet management. This provides a concrete reusable boundary between object semantics and traversal infrastructure.
- **C1:** `completeScan` is a joining scan: workers must collectively exhaust work, including overflow recovery, before completion. Heap range changes also have to update marking metadata consistently.
- **C3:** Worker-local stacks and statistics feed shared work-packet processing, making parallel traversal and its coordination costs visible.

**Entry points:** [GC subsystem tree](https://github.com/eclipse-omr/omr/tree/master/gc) and [MarkingScheme.cpp](https://github.com/eclipse-omr/omr/blob/master/gc/base/MarkingScheme.cpp). OMR is counted once; its consumers are not counted as copies of this implementation.

### [wingo/whippet](https://github.com/wingo/whippet)

**Language/role:** C; an embeddable collector family initially targeting Guile. **Work in progress**, as explicitly described by the repository.

Study the common allocation interface across collector implementations, and the separation of heap-sizing policy from collection mechanics. Whippet is designed to be incorporated into a host's source tree.

- **C2:** Its abstract C API supports multiple implementations and embedding choices including precise or conservative roots, object pinning, finalization, and ephemerons, with implementation-specific limitations documented in the repository.
- **C3:** The [adaptive heap sizer](https://github.com/wingo/whippet/blob/main/src/adaptive-heap-sizer.h) implements a MemBalancer-derived policy using smoothed allocation rate, pause duration, and live bytes. Minimum free space and bounded growth multipliers make the space-versus-collection-cost policy explicit.
- **C1:** The sizer also exposes numerical and synchronization details: NaN handling, bounded multipliers, lock-protected shared estimates, and retry behavior when allocation-counter sampling fails.

This is valuable experimental implementation material, not evidence of a production-readiness guarantee.

### [fredericbonnet/colibri](https://github.com/fredericbonnet/colibri)

**Language/role:** C; a datatype library containing its own precise generational collector and cell allocator.

Study a collector designed together with ropes, lists, maps, custom object types, and explicit roots. It provides a smaller embedding-oriented counterpoint to whole-language runtimes.

- **C1:** Allocations must occur inside GC-protected sections. The collector marks both explicit roots and modified parent pages from uncollected generations; promotion order must preserve pool relationships. These obligations are visible in [colGc.c](https://github.com/fredericbonnet/colibri/blob/master/src/colGc.c).
- **C2:** Custom words supply child enumeration and cleanup behavior, while thread groups define independent managed-memory domains. The [library architecture](https://github.com/fredericbonnet/colibri/blob/master/README.md) explains the single-threaded, asynchronous, and shared models and their restrictions.
- **C3:** Per-thread Eden pools, less frequent older-generation collection, whole-page promotion, and optional compaction on promotion expose locality and fragmentation tradeoffs.

Do not read the README's broad safety language as a proof: correct rooting, custom tracing, and group boundaries remain client obligations.

## Rust libraries: rooting, lifetimes, and cycles

### [kyren/gc-arena](https://github.com/kyren/gc-arena)

**Language/role:** Rust; incremental, exact, nonmoving mark-and-sweep arenas.

Study how generative lifetimes and controlled mutation can express GC integration constraints through an otherwise safe API. The repository describes use in Ruffle and a game scripting VM.

- **C1:** Arena-branded lifetimes prevent pointers escaping into the wrong arena, and collection runs separately from mutation callbacks. The [`Collect` contract](https://raw.githubusercontent.com/kyren/gc-arena/master/src/collect.rs) further requires tracing every managed pointer, forbids dereferencing managed fields during destruction, and requires barriers for interior mutation.
- **C2:** Derivable tracing, managed pointers, weak pointers, and barrier-aware interior-mutability wrappers support user-defined object graphs and dynamically sized types.
- **C3:** Copyable pointers avoid bookkeeping on every pointer copy; allocation debt meters incremental collection work. The [repository design explanation](https://github.com/kyren/gc-arena) also states the corresponding limits: single-threaded arenas, no compaction, and no collection during an ongoing mutation callback.

### [Manishearth/rust-gc](https://github.com/Manishearth/rust-gc)

**Language/role:** Rust; thread-local tracing collector with `Gc`, `GcCell`, and derive support.

Study the interaction between explicit root counts, tracing, interior mutability, and finalization in a compact library. The main implementation is not the experimental concurrent branch.

- **C1:** The [collector implementation](https://github.com/Manishearth/rust-gc/blob/master/gc/src/gc.rs) guards root-count overflow, prevents managed-pointer dereferencing during sweeping, and performs another marking pass after finalizers because finalization may restore reachability. Thread-local teardown also deliberately avoids freeing objects still possibly referenced by other thread-local variables.
- **C2:** `Trace` and `Finalize`, derive macros, and `GcCell` expose reusable integration points for application types. The [repository's usage and restrictions](https://github.com/Manishearth/rust-gc) explain why ordinary `RefCell` and arbitrary destructors cannot simply substitute for these abstractions.

The code is particularly useful for studying the safety boundary around destruction; the presence of an ergonomic pointer API does not remove the unsafe obligations of manual tracing implementations.

### [claytonwramsey/dumpster](https://github.com/claytonwramsey/dumpster)

**Language/role:** Rust; reference counting extended with cycle detection, offering `sync` and `unsync` collectors.

Study an alternative to root-based tracing that retains an `Rc`/`Arc`-like interface. The two collector implementations share tracing concepts but have materially different concurrency requirements.

- **C1:** The [thread-safe pointer implementation](https://github.com/claytonwramsey/dumpster/blob/master/dumpster/src/sync/mod.rs) separates strong ownership from collector-held weak references and tracks mutation through atomic tags and generations. Managed pointers can be marked dead during cycle destruction; fallible access operations address destructor-time access without permitting use-after-free.
- **C2:** Generic tracing and derive support cover user-defined cyclic structures, unsized data, and both thread-local and shared ownership. Collection-trigger callbacks expose policy independently of pointer operations.
- **C3:** The default trigger compares dropped-pointer activity with the number of existing pointers, making collection scheduling explicit. The API carefully avoids promising that one concurrent `collect()` call immediately reclaims every unreachable object.

## Shared-heap production runtime implementations

### [openjdk/jdk](https://github.com/openjdk/jdk)

**Language/role:** Primarily C++ for HotSpot GC; Java tests and runtime interfaces. Relevant subsystem: `src/hotspot/share/gc`.

Study several collector families within a shared VM, then narrow to one correctness boundary. G1, Serial, Parallel, Shenandoah, and ZGC are represented in the [collector source tree](https://github.com/openjdk/jdk/tree/master/src/hotspot/share/gc); they are not separate repository entries.

- **C1:** ZGC's [barrier interface and design comments](https://github.com/openjdk/jdk/blob/master/src/hotspot/share/gc/z/zBarrier.hpp) distinguish load, store, marking, relocation, and weak/phantom-reference handling. Pointer metadata must prevent an unsafe address from being exposed across changing collection phases.
- **C3:** The shift-based compiled load barrier combines a metadata check with pointer decoding. Its comments explain restrictions on valid bit patterns and why the slow path must reload a pointer damaged by the speculative shift.

This is a particularly concrete study of how machine-level fast paths constrain collector design; no claim is made that one HotSpot algorithm is best for all workloads.

### [dotnet/runtime](https://github.com/dotnet/runtime)

**Language/role:** C++ collector with C# APIs and tests; focus on CoreCLR GC.

Study the boundary between the execution engine, thread allocation contexts, generational policy, and the decision to compact or sweep.

- **C1:** The [CoreCLR GC design](https://github.com/dotnet/runtime/blob/main/docs/design/coreclr/botr/garbage-collection.md) explains why allocation must keep the heap crawlable, why older-to-younger references require cards, and why relocation must update references beyond the strongly live set, including weak references.
- **C3:** Thread-owned allocation contexts avoid common-path locking. Separate treatment of large objects and a planning phase that estimates whether compaction is productive make allocation cost, copying cost, and fragmentation tradeoffs explicit.

**Additional entry point:** The [GC testing requirements](https://github.com/dotnet/runtime/blob/main/docs/project/garbage-collector-guidelines.md) distinguish core-heap stress testing, functional API tests, and performance checks. Those documented requirements are evidence of the engineering process, not a claim that this research executed the tests. The older design overview should be read as an architectural introduction rather than a complete description of every current configuration.

### [golang/go](https://github.com/golang/go)

**Language/role:** Go with low-level runtime support; **official GitHub mirror**. Relevant subsystem: `src/runtime`.

Study a precise, concurrent, non-generational mark-and-sweep collector integrated with goroutine scheduling and allocation assists.

- **C1:** [`mgc.go`](https://github.com/golang/go/blob/master/src/runtime/mgc.go) documents the ordering between stopping mutators, enabling write barriers, scanning roots, detecting distributed marking termination, and sweeping. Operations on unswept spans are explicitly prohibited because they can corrupt marking metadata.
- **C3:** Allocation assists share collection work with mutators; background sweeping and demand sweeping reclaim spans without requiring a monolithic sweep pause. Large-object scans are divided into smaller jobs to limit scanning delays and expose parallel work.

The same file connects the phase machine to per-processor allocation areas and collection pacing. It is unusually useful as a source-level architectural overview. The [repository README](https://github.com/golang/go) identifies the canonical upstream as `go.googlesource.com/go`; the GitHub mirror contains substantive implementation history and source.

### [v8/v8](https://github.com/v8/v8)

**Language/role:** C++; JavaScript/WebAssembly runtime heap collectors. **Official GitHub mirror**.

Study a generational heap where nursery strategy, concurrent marking, and selective old-space evacuation share a compiler-generated barrier system.

- **C1:** The [GC architecture document](https://github.com/v8/v8/blob/main/docs/heap/garbage-collection.md) distinguishes three barrier obligations: preserving old-to-young edges, maintaining marking invariants under mutation, and recording old-to-old slots that need updating after evacuation.
- **C3:** The same document contrasts nursery copying with minor mark-sweep and page promotion, then explains concurrent marking/sweeping and selective compaction. It also states when barriers can be eliminated, such as certain initializing stores before another possible GC point.

This is a useful study of the compiler–collector contract and of multiple strategies coexisting within one heap architecture. Default flags and enabled algorithms can change; the linked development document describes the inspected source rather than every Chrome or Node.js release.

## Functional, scientific, and actor runtimes

### [ocaml/ocaml](https://github.com/ocaml/ocaml)

**Language/role:** C runtime within an OCaml compiler repository; focus on the multicore major collector.

Study how concurrent collection handles domains entering and leaving the runtime, rather than assuming a fixed set of mutators.

- **C1:** [`runtime/major_gc.c`](https://github.com/ocaml/ocaml/blob/trunk/runtime/major_gc.c) documents separate completion counters for sweeping, marking, ephemerons, and finalizers. Some counters only decrease, while others may increase as domains create work. Finalizer orphaning and adoption constrain permissible phase transitions.
- **C3:** Collection work is accounted across slices, and a prefetch buffer separates discovery from scanning. The source explains why read-prefetching object headers and nearby fields can help traversal while write-prefetching may introduce contention.

The comments also identify contexts that cannot safely inspect global GC phase state, including domain termination and opportunistic collection around barriers. These details make the implementation valuable for studying lifecycle races and work pacing in a mostly concurrent runtime collector.

### [JuliaLang/julia](https://github.com/JuliaLang/julia)

**Language/role:** C/C++ runtime with Julia APIs and tests; focus on the stock collector rather than its optional MMTk integration.

Study a nonmoving, generational collector designed around precise object metadata, native integration, and parallel heap traversal.

- **C1:** The [developer GC documentation](https://docs.julialang.org/en/v1/devdocs/gc/) explains how sticky mark bits encode generational state and why old-to-young writes must enter per-thread remembered sets. Page ownership also has to remain consistent between mutators and a background sweeper.
- **C3:** Small allocations use per-thread size-class pools; marking and parts of sweeping are parallelized. A tiered page-reuse policy lets allocation claim empty pages before the background thread releases their physical memory, avoiding some fresh-page faults.

The same source explains why pacing based only on live-object size misses fragmentation, and why heap-size decisions incorporate pages, allocation rate, and collector progress. This provides a practical connection between allocator metadata and process-wide memory policy.

### [ghc/ghc](https://github.com/ghc/ghc)

**Language/role:** C runtime within the Haskell compiler repository; **official mirror**, with development hosted on GHC GitLab. Focus: the nonmoving oldest-generation collector.

Study how a concurrent mark-and-sweep old generation coexists with younger moving generations and Haskell-specific roots and weak references.

- **C1:** [`rts/sm/NonMoving.c`](https://github.com/ghc/ghc/blob/master/rts/sm/NonMoving.c) states the snapshot invariant, separates stop-the-world preparation/final synchronization from concurrent work, and explains why a particular atomic segment-list discipline avoids ABA. Allocation snapshots determine which blocks existed at cycle start.
- **C3:** Size-specific allocators keep per-capability current segments and shared active/filled segment lists. This layout supports low-latency old-generation collection without forcing every allocation through a shared lock or moving the entire old heap.

The source's named design notes link weak-pointer processing, stack dirtiness, remembered sets, and promotion behavior into the central collector model. These are useful navigation aids for a codebase whose correctness spans multiple runtime modules.

### [erlang/otp](https://github.com/erlang/otp)

**Language/role:** C collector in BEAM, with Erlang runtime interfaces and tests.

Study process-local generational copying, where immutable terms simplify the intergenerational reference problem and isolate collection work between processes.

- **C1:** The [collector design document](https://github.com/erlang/otp/blob/master/erts/emulator/internal_doc/GarbageCollection.md) explains forwarding markers that preserve sharing, root scanning, and the invariant that old-heap terms cannot reference young-heap terms. Heap fragments and message payloads add roots beyond a single contiguous nursery.
- **C3:** Most collections traverse only the young heap; a high-water mark identifies survivors for promotion. [`erl_gc.c`](https://github.com/erlang/otp/blob/master/erts/emulator/beam/erl_gc.c) makes heap-size growth and scheduler reduction accounting explicit, linking memory reclamation to execution fairness.

The architecture is useful for understanding how language immutability changes the collector's obligations. The design document retains some illustrative links to older OTP source versions; the second entry point is the inspected current implementation.

### [ponylang/ponyc](https://github.com/ponylang/ponyc)

**Language/role:** C runtime and Pony compiler; actor-local object collection plus actor-cycle collection.

Study a collector whose correctness depends on the language's reference capabilities and message-passing protocol, including objects shared across actor boundaries.

- **C1:** [`src/libponyrt/gc/gc.c`](https://github.com/ponylang/ponyc/blob/main/src/libponyrt/gc/gc.c) tracks local and foreign object ownership, reference-count transfers, and tracing on send/receive. Its immutable-transition path keeps tracing until the owner has received the required acquisition information.
- **C3:** Per-actor collection avoids a global stop-the-world step. The [runtime explanation](https://tutorial.ponylang.io/runtime-basics/garbage-collection.html) states that object collection runs between behaviors, allowing other actors to continue, but also explains why a long allocating behavior can exhaust memory before yielding an opportunity to collect.

The repository therefore offers both a concurrency protocol study and an explicit latency-versus-progress tradeoff. Object collection and detecting dead cycles of actors are distinct parts of the design.

### [sbcl/sbcl](https://github.com/sbcl/sbcl)

**Language/role:** C collector with Common Lisp runtime/compiler integration; **official repository mirror**. Focus: the generational conservative collector in `src/runtime/gencgc.c`.

Study how a moving generational collector accommodates conservative stack references, pinned objects, Lisp code objects, and saved heap images.

- **C1:** [`gencgc.c`](https://github.com/sbcl/sbcl/blob/master/src/runtime/gencgc.c) documents page-table and pinning invariants, locking needed to prevent overlapping allocations, and the distinction between properties established when an allocation region opens and usage recorded when it closes. Scavenging cannot treat an open region as fully described.
- **C3:** Inline allocation uses region free pointers; boxed and unboxed page classes avoid scanning and write-protecting pages that cannot contain references. Generation selection limits repeated work on long-lived data.

The same implementation exposes a special nonconservative mode used before saving a core image. Collector details vary by target and build configuration; this entry specifically concerns the inspected generational implementation.

## Dynamic-language and cycle-collector integration

### [python/cpython](https://github.com/python/cpython)

**Language/role:** C runtime; cyclic collection supplementing reference counting. Focus here: the free-threaded collector in `Python/gc_free_threading.c`.

Study how a cycle detector adapts when reference counts may be deferred or distributed across threads and finalizers can resurrect objects.

- **C1:** The [free-threaded implementation](https://github.com/python/cpython/blob/main/Python/gc_free_threading.c) merges counts only under a stopped-world invariant, handles frame references that were previously deferred, and avoids collecting deferred-reference objects when an active frame lacks a valid stack pointer. It restores object metadata after temporarily repurposing it for collection.
- **C3:** Allocation counts are buffered per thread to reduce global-counter traffic. Temporary work lists reuse an object-header field, and heap visitors use allocator knowledge to locate tracked objects instead of requiring every allocation to enter one global tracking list.

This is a focused study of the collector–reference-counting boundary. The free-threaded and GIL-enabled builds have different implementations, so their algorithmic details should not be conflated.

### [ruby/ruby](https://github.com/ruby/ruby)

**Language/role:** C collector with Ruby APIs and tests; focus on `gc/default/default.c` and the Modular GC boundary.

Study how a default mark-sweep-compact collector is separated from the runtime while retaining generational barriers, object metadata, and allocation policy.

- **C1:** The [default collector](https://github.com/ruby/ruby/blob/master/gc/default/default.c) contains distinct generational and incremental write-barrier paths, remembered and pinned metadata, consistency checks, and explicit synchronization assumptions around remembered-bit updates.
- **C2:** The [GC subsystem documentation](https://github.com/ruby/ruby/blob/master/gc/README.md) defines the implementation API and host-side API used by interchangeable collectors. It clearly distinguishes the default implementation from the experimental MMTk integration.
- **C3:** Size-specific heap pools, incremental marking work, lazy sweeping, and growth thresholds expose the separation of allocation policy from graph traversal.

The Modular GC API is explicitly experimental and subject to change. This entry counts the Ruby repository once and does not treat its synchronized MMTk integration as another independent collector implementation.

### [lua/lua](https://github.com/lua/lua)

**Language/role:** C; compact embeddable runtime with incremental and generational collection. **Official development copy, mirrored irregularly**, according to the repository description.

Study a small collector that still has demanding semantics: weak tables, finalizers, open upvalues, and transitions between object ages and marking colors.

- **C1:** [`lgc.c`](https://github.com/lua/lua/blob/master/lgc.c) explains forward and backward barriers, including why an object reached from an old object cannot immediately become fully old while it still references young objects. Weak-table key cleanup must also preserve hash-chain traversal structure.
- **C3:** Sweeping is divided into bounded batches to balance fixed overhead against incremental step size. Closed upvalues and simple objects can be marked directly, while other objects enter explicit gray lists for later traversal.

The relatively compact source makes the state-machine and data-structure interactions approachable without reducing the collector to a tutorial example. The mirror is development material and should not be assumed to exactly match a released Lua tarball.

### [nim-lang/Nim](https://github.com/nim-lang/Nim)

**Language/role:** Nim; runtime ORC cycle collection alongside compiler-managed reference counting. Focus: `lib/system/orc.nim` on `devel`.

Study trial-deletion cycle detection and its integration with compiler-generated tracing and destructors.

- **C1:** [`orc.nim`](https://github.com/nim-lang/Nim/blob/devel/lib/system/orc.nim) implements gray marking by temporarily discounting internal references, restores reachable subgraphs through black scanning, and separates objects to free from those still externally reachable. Its comments explain the reference-count and color-state invariants.
- **C3:** Explicit traversal stacks avoid depending solely on recursive graph walks. The inspected development code also implements generational pruning: repeatedly surviving subgraphs can be skipped within an epoch, while new epochs and full collection restore exhaustive tracing.

The pruning rule deliberately permits some cyclic garbage to survive until a later epoch in exchange for less repeated work. This is development-branch behavior; it is not a claim about every released Nim version or every memory-management mode.

## Historical research infrastructure

### [JikesRVM/JikesRVM](https://github.com/JikesRVM/JikesRVM)

**Language/role:** Java, with VM-specific low-level support; self-hosted research VM containing the original Java MMTk implementation.

Study collector construction in a managed-language VM, particularly global plans, thread-local contexts, space policies, and collector bootstrapping. This is a separate Java implementation with substantial research history, not a duplicate Rust MMTk binding.

- **C2:** [`MMTk/.../Plan.java`](https://github.com/JikesRVM/JikesRVM/blob/master/MMTk/src/org/mmtk/plan/Plan.java) supplies common space management, allocation categories, collector constraints, statistics, and sanity-checking infrastructure for multiple plans.
- **C1:** The same source distinguishes synchronized global state from thread-local state and lays out a boot sequence that enables allocation before collection. Collector-thread counts must remain consistent with the active plan's constraints.
- **C3:** Local contexts keep frequent allocation operations unsynchronized while global resources are coordinated separately.

**Status:** Historical research selection. GitHub's API reported the last repository push in November 2022, and the [README](https://github.com/JikesRVM/JikesRVM) specifies older JDK/Ant requirements. Do not assume compatibility with a current Java toolchain.

## Coverage, search process, and limitations

Live discovery used more than six distinct query formulations, followed by repository-page/API verification and additional primary-source reading for every retained repository. Search angles included:

- Conservative C libraries and reusable memory-management toolkits: Boehm, MPS, and MMTk.
- Rust rooting, arena lifetimes, cycle tracking, and concurrent shared-pointer collectors.
- Immix-family and embedding-oriented implementations, including Whippet.
- Language-independent runtime components and original Java MMTk research infrastructure.
- Shared-heap runtimes: JVM, .NET, Go, and JavaScript engines.
- Functional/scientific runtimes and multicore collector design: OCaml, GHC, and Julia.
- Actor ownership, per-process heaps, and message-passing collection: Pony and Erlang.
- Reference counting with cycle detection, small embedded runtimes, and native extension boundaries.
- Common Lisp and precise C datatype libraries; this follow-up added SBCL and Colibri.
- Real-time/embedded C collector searches, which increasingly returned already-covered projects, small demonstration collectors, wrappers, and GC log-analysis tools.

The selection deliberately excludes allocator-only projects, epoch/hazard-pointer reclamation libraries, GC log parsers, awesome-lists, generated bindings, and small teaching collectors. Rust experiments such as Shifgrethor and zerogc were discovery leads but were not retained without the same depth of implementation and present-status review. MMTk bindings and runtime forks were not multiplied into separate entries. Tiny C collectors and newer C++ smart-pointer collectors remain possible follow-up areas; omission is not a finding that they are unsound or insubstantial.

Primary evidence came from repository content, developer documentation, implementation comments, and release notes. Some public documentation URLs could not be retrieved, so the report uses verified repository sources instead. The search was broad but not exhaustive: it does not cover every Scheme, Smalltalk, D, JavaScript, or research collector, and it makes no hard real-time guarantees or cross-project numerical performance claims. No candidate code was installed, built, or executed. The report assesses architectural study value, not a completed correctness audit or an adoption recommendation.
