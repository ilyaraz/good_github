# Standard library implementations

Research date: **2026-10-09**.

This report selects 27 GitHub repositories implementing language standard libraries, C/POSIX libraries, or substantial standard-library replacements and polyfills. Compiler/runtime monorepos count once; their relevant library subsystems are identified below. The selection spans desktop, embedded, GPU, WebAssembly, managed, functional, and numerical environments. It is a guide to worthwhile implementation studies, not a claim of complete standards conformance or uniformly exemplary code.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions supporting many use cases. **C3** — real performance or resource constraints addressed through understandable implementation structure. **C4** — sustained evolution evidenced by compatibility work, testing, or complexity management, rather than age alone.

## C++ implementations and specialized alternatives

### [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language/role:** C++ and C; the relevant subsystems are `libcxx` (C++ standard library) and `libc` (LLVM's C library), counted together. Study how a library separates fast common cases from expensive correctness work, and how public interfaces survive representation changes.

- **C1:** LLVM libc's logarithm design derives range-reduction bounds and uses a fast approximation followed by Ziv's test, with a more accurate phase when the result cannot yet be certified. The [logarithm algorithm document](https://libc.llvm.org/headers/math/log.html) exposes the numerical reasoning rather than merely presenting a polynomial.
- **C3:** That staged algorithm makes extra precision conditional on need. At the library boundary, the [libc++ ABI design](https://libcxx.llvm.org/DesignDocs/ABIVersioning.html) explains stable versus experimental ABI versions and individual feature macros, making the cost of changing internal representations visible.

### [microsoft/STL](https://github.com/microsoft/STL)

**Language/role:** C++; Microsoft's implementation of the C++ standard library. A particularly useful study of exception guarantees, iterator diagnostics, sanitizers, and allocator behavior interacting inside ordinary containers.

- **C1:** The [vector implementation](https://github.com/microsoft/STL/blob/main/stl/inc/vector) separates insertion with spare capacity from reallocation, uses destruction/deallocation guards, and integrates iterator invalidation and AddressSanitizer annotations. Correctness depends on which elements have actually been constructed when an operation throws.
- **C4:** The [release-linked changelog](https://github.com/microsoft/STL/wiki/Changelog) connects VS 2019, VS 2022, and later toolsets, including regression backports, standard defect resolutions, and removal of features after documented deprecation periods. This is concrete evidence of compatibility management across releases, alongside the repository's multiple conformance suites.

### [gcc-mirror/gcc](https://github.com/gcc-mirror/gcc)

**Language/role:** C++; `libstdc++-v3` within GCC. **GitHub public mirror:** GitHub identifies its upstream as GCC's `gcc.gnu.org` Git repository; this is not an independent library project. Study how representation choices satisfy standard container requirements while preserving deployed interfaces.

- **C1:** The [hashtable implementation notes](https://github.com/gcc-mirror/gcc/blob/master/libstdc++-v3/include/bits/hashtable.h) explain that buckets point to predecessor nodes, including a non-dereferenceable sentinel. Insertion and erasure must preserve that invariant.
- **C3:** The same notes connect optional cached hash codes and node-based iterators to bucket traversal and efficient iteration even with many empty buckets. Separately, the [dual ABI manual](https://gcc.gnu.org/onlinedocs/libstdc++/manual/using_dual_abi.html) shows how old and new string/list implementations coexist through inline namespaces without changing the shared-library soname.

### [NVIDIA/cccl](https://github.com/NVIDIA/cccl)

**Language/role:** C++/CUDA; retain specifically `libcudacxx`, the host/device C++ standard-library implementation. Thrust and CUB share the monorepo but are not counted separately. The [repository overview](https://github.com/NVIDIA/cccl/blob/main/README.md) distinguishes these components and their roles.

- **C1:** The [memory-model documentation](https://nvidia.github.io/cccl/unstable/libcudacxx/extended_api/memory_model.html) specifies the relationship among thread scopes, memory locations, atomicity, and data races. Its message-passing examples show why using an atomic operation at the wrong scope still permits a race.
- **C2:** Standard-like facilities coexist with CUDA-specific synchronization abstractions, allowing the same conceptual interfaces to serve host and device code.
- **C3:** Thread scopes explicitly reflect different synchronization costs within a block, across a device, and across a system. This is an architectural response to heterogeneous hardware, not a generic claim that GPU code is faster.

### [electronicarts/EASTL](https://github.com/electronicarts/EASTL)

**Language/role:** C++; an STL-style alternative tailored to game development, with deliberate allocation-interface differences rather than full drop-in conformance. Study allocator-controlled containers and the tradeoff between reusable implementations and predictable memory use.

- **C2:** The [design document](https://github.com/electronicarts/EASTL/blob/master/doc/Design.md) explains iterator-based algorithms and reuse of ordinary container machinery for fixed-storage variants.
- **C3:** [fixed_vector](https://github.com/electronicarts/EASTL/blob/master/include/EASTL/fixed_vector.h) embeds a fixed memory pool and makes heap overflow a template policy. Its source explicitly documents the failure behavior when overflow is disabled and capacity is exceeded.

Some design-document comparisons describe historical STL implementations; they are not evidence of current comparative speed. The repository was not archived when checked, but its API-reported last push was 2025-11-15; this report does not infer ongoing maintenance from its reputation.

## C libraries for constrained or different execution environments

### [picolibc/picolibc](https://github.com/picolibc/picolibc)

**Language/role:** C and assembly; embedded libc/libm with substantive evolution from Newlib and AVR Libc. Study how a general C API can be implemented with narrow platform hooks and selectable functionality under ROM/RAM limits.

- **C1:** The [locking design](https://github.com/picolibc/picolibc/blob/main/doc/locking.md) distinguishes shared global state, per-file locks, and atomics for reentrant operations. It also specifies the platform's retargetable locking obligations; enabling library locking does not itself supply a working OS mutex implementation.
- **C3:** The [printf/scanf design](https://github.com/picolibc/picolibc/blob/main/doc/printf.md) offers conversion variants selected through compiler/linker configuration. It explains code-size tradeoffs, why symbol aliases preserve compiler optimizations, and the limitation with link-time optimization.

### [avrdudes/avr-libc](https://github.com/avrdudes/avr-libc)

**Language/role:** C and AVR assembly; the AVR-GCC C library and startup support. The [official repository description](https://github.com/avrdudes/avr-libc/blob/main/README.md) explicitly identifies its ISO C subset, including the absence of `wchar_t` support. Study the consequences of very small address spaces and a heap sharing RAM with the stack.

- **C1:** The [allocator implementation guide](https://avrdudes.github.io/avr-libc/avr-libc-user-manual/malloc.html) explains stack/heap collision checks, interrupt-stack margins, block headers, and allocation failure. Its limits are explicit: checking the current stack does not prove that later calls or interrupts will fit.
- **C3:** The allocator stores free-list links inside freed blocks, splits suitable blocks, coalesces neighbors, and attempts in-place `realloc` growth. These choices balance metadata size, fragmentation, and copying on constrained devices.

### [managarm/mlibc](https://github.com/managarm/mlibc)

**Language/role:** C, C++, and assembly; a portable C/POSIX library intended for multiple operating systems. Study a libc whose porting boundary is an explicit design concern.

- **C2:** The [repository architecture](https://github.com/managarm/mlibc/blob/master/README.md) separates OS-independent `options`, one selected `sysdeps` backend, and ABI definitions. Feature groups allow a port to choose POSIX or Linux interfaces without embedding those choices throughout every function.
- **C1:** The [sysdeps implementation guide](https://docs.managarm.org/mlibc-book/porting/implementing_sysdeps_p2.html) specifies error-code returns versus `errno`, required operations, entry-stack layout, and zero-filled mapping expectations. These are concrete cross-layer failure modes, including allocation and startup bugs that a successful build would not detect.

The project recommends pinning versions for out-of-tree ports because internal backend interfaces can change; the abstraction boundary is not a promise of permanent backend ABI stability.

### [redox-os/relibc](https://github.com/redox-os/relibc)

**Language/role:** Primarily Rust, exposing C/POSIX interfaces. **Official Redox GitHub mirror** of development on Redox GitLab. Its [README](https://github.com/redox-os/relibc/blob/master/README.md) identifies Redox and Linux support and describes the library as under heavy development.

- **C1:** The [mutex implementation](https://github.com/redox-os/relibc/blob/master/src/sync/mutex.rs) uses distinct unlocked/locked/waiting states, acquire/release operations, futex wakeups, and guard-based unlocking. Manual FFI-oriented methods document the aliasing obligations their unsafe interfaces impose.
- **C2:** C header implementations and generated interfaces are separated from platform backends; `redox-rt` supplies process and signal machinery underneath the Redox backend. This is a useful study of implementing a foreign language's standard-library contract in Rust without assuming that Rust eliminates ABI or synchronization hazards.

### [WebAssembly/wasi-libc](https://github.com/WebAssembly/wasi-libc)

**Language/role:** C; libc for WebAssembly on WASI. Study how familiar filesystem interfaces are adapted to an environment with preopened directory capabilities. The [lower-half architecture](https://github.com/WebAssembly/wasi-libc/blob/main/libc-bottom-half/README.md) explains this adaptation and its relationship to higher-level libc functionality.

- **C1:** [preopens.c](https://github.com/WebAssembly/wasi-libc/blob/main/libc-bottom-half/sources/preopens.c) handles prefix selection, precedence among registered preopens, synchronization, missing-prefix errors, and conversion of an empty relative path to `.`. These details determine the meaning of an apparently ordinary pathname operation.
- **C2:** The split between reusable higher-level C-library code and WASI-facing implementations preserves a broad C/POSIX API over a different host interface. This is substantive adaptation of upstream components, not an independently counted musl mirror.

Thread support and failure behavior vary by target; the repository's current README documents those differences, so this entry does not imply uniform POSIX behavior across WASI configurations.

## Native language libraries: ownership, protocols, and generic algorithms

### [rust-lang/rust](https://github.com/rust-lang/rust)

**Language/role:** Rust; `library/core`, `library/alloc`, and `library/std` in the compiler monorepo. The [standard-library root](https://github.com/rust-lang/rust/blob/main/library/std/src/lib.rs) is an entry point to the public abstractions; the implementation often lives in the lower layers and is re-exported.

- **C1:** [Vec's implementation and safety contracts](https://github.com/rust-lang/rust/blob/main/library/alloc/src/vec/mod.rs) specify allocation provenance, alignment, initialized length versus capacity, zero-sized types, and the byte-size limit for pointer arithmetic. These invariants explain why a short unsafe operation may require extensive surrounding reasoning.
- **C2:** Allocation-backed collections integrate with slices, iterators, and allocator interfaces rather than forming isolated containers.
- **C3:** The same source documents amortized growth, zero-capacity allocation avoidance, and the pointer/capacity/length representation. Its guarantees also explicitly avoid promising a stable field layout.

### [golang/go](https://github.com/golang/go)

**Language/role:** Go; the standard-library packages under `src`. **Official GitHub mirror:** the [README](https://github.com/golang/go/blob/master/README.md) names `go.googlesource.com/go` as canonical. Study how small interfaces permit composition and optional optimization.

- **C1:** [io.go](https://github.com/golang/go/blob/master/src/io/io.go) defines partial-read, EOF, short-write, and buffer-retention contracts. Its copy loop must process bytes returned alongside an error and detect impossible write counts.
- **C2:** `Reader`, `Writer`, `Closer`, and composed interfaces support files, buffers, streams, and adapters without requiring a shared concrete class hierarchy.
- **C3:** `Copy` selects `WriterTo` or `ReaderFrom` when available before using a buffer. The optimization is expressed through optional capabilities, preserving the general interface while allowing implementations to avoid an extra allocation and copy.

### [swiftlang/swift](https://github.com/swiftlang/swift)

**Language/role:** Swift, with C++ runtime support; `stdlib/public/core` is the main library subsystem. The [official library architecture](https://www.swift.org/documentation/standard-library/) distinguishes core types, runtime machinery, platform overlays, and compiler-coupled tests.

- **C1:** The [Array implementation](https://github.com/swiftlang/swift/blob/main/stdlib/public/core/Array.swift) makes mutation conditional on uniquely owned storage and brackets mutation with explicit buffer operations. Bounds checks, native storage, and Objective-C bridging add distinct paths that must preserve value semantics.
- **C3:** Copy-on-write lets array copies share storage until mutation, while unique storage can be modified in place. The source explains where copying costs arise and exposes the checks that implement the optimization.

This is especially instructive for understanding how a high-level value type depends on compiler/runtime cooperation rather than on its public API alone.

### [dlang/phobos](https://github.com/dlang/phobos)

**Language/role:** D; Phobos, D's standard library. Study generic range programming with algorithm requirements made visible in template constraints and compile-time assertions.

- **C2:** [std.algorithm.sorting](https://github.com/dlang/phobos/blob/master/std/algorithm/sorting.d) implements sorting, partitioning, selection, and merging over ranges, with customizable predicates. `sort` returns a `SortedRange`, making established ordering useful to subsequent operations.
- **C3:** The same implementation documents and selects introsort for unstable sorting and Timsort for stable sorting. It distinguishes allocation behavior, partially ordered inputs, and predicate costs, while checking capabilities such as random access, slicing, and element assignment.

The [Phobos module documentation](https://dlang.org/phobos/index.html) provides the wider map of algorithms, containers, numerics, I/O, and concurrency facilities. The value here is composable algorithm design, not an unsupported cross-language speed comparison.

### [nim-lang/Nim](https://github.com/nim-lang/Nim)

**Language/role:** Nim; the `lib` standard-library tree, especially its pure Nim modules. The [repository layout](https://github.com/nim-lang/Nim/blob/devel/readme.md) separates these from foreign-library wrappers and identifies the shared test tree.

- **C2:** [tables.nim](https://github.com/nim-lang/Nim/blob/devel/lib/pure/collections/tables.nim) supplies ordinary, insertion-ordered, and counting tables, each with value and reference variants. Its examples make the aliasing consequences of those choices explicit.
- **C3:** Table growth rebuilds bucket placement using stored hash codes and moves keys and values where supported, with a separate JavaScript path. Shared insertion/deletion machinery supports multiple variants without reducing the design to a single inflexible container.

This is a useful bridge between API semantics and implementation mechanics: seemingly similar assignments can copy a table or alias it, and the implementation must also accommodate multiple compilation targets.

### [crystal-lang/crystal](https://github.com/crystal-lang/crystal)

**Language/role:** Crystal; library implementations under `src`, excluding the compiler subsystem. Study typed message passing implemented within the language's own library.

- **C1:** [Channel](https://github.com/crystal-lang/crystal/blob/master/src/channel.cr) coordinates sender/receiver queues, buffered delivery, close state, and select contexts. Closing prevents new sends but permits buffered values to drain; blocked participants must be awakened correctly.
- **C2:** A generic `Channel(T)` provides buffered and rendezvous communication, iteration, and selection as reusable operations rather than requiring applications to manipulate scheduler queues.

The [channel specifications](https://github.com/crystal-lang/crystal/blob/master/spec/std/channel_spec.cr) exercise closing during selection, awakening multiple waiters, and nilable payload types. They make good companions to the implementation because they expose lifecycle distinctions that a happy-path send/receive example misses.

## Managed runtimes and JavaScript compatibility

### [python/cpython](https://github.com/python/cpython)

**Language/role:** Python and C; standard-library code in `Lib`, with native implementations in `Modules`. The entry point here is `asyncio`, rather than the interpreter or compiler.

- **C1:** [asyncio's queues](https://github.com/python/cpython/blob/main/Lib/asyncio/queues.py) remove cancelled waiters and transfer wakeups when a resumed producer cannot proceed. Shutdown, unfinished-task accounting, and `join` introduce additional state invariants.
- **C2:** Queue, priority-queue, and LIFO variants share coordination machinery while overriding storage operations, separating scheduling concerns from ordering policy.

The [queue tests](https://github.com/python/cpython/blob/main/Lib/test/test_asyncio/test_queues.py) inspect empty and nonempty shutdown, pending producers/consumers, and completion behavior. This provides a compact study of asynchronous failure handling inside a much larger general-purpose library.

### [dotnet/runtime](https://github.com/dotnet/runtime)

**Language/role:** Primarily C# for the library; focus on `src/libraries`, especially `System.Private.CoreLib`. The [repository overview](https://github.com/dotnet/runtime/blob/main/README.md) distinguishes its runtime, libraries, and host responsibilities.

- **C1:** [ConcurrentDictionary](https://github.com/dotnet/runtime/blob/main/src/libraries/System.Private.CoreLib/src/System/Collections/Concurrent/ConcurrentDictionary.cs) retries an update if resizing changed the table after the relevant lock was acquired. It also accounts for a changed comparer when recomputing the hash.
- **C3:** Striped locks, a replaceable table object, growth budgets, and specialized comparer paths make contention, allocation, and dispatch costs explicit. Comments explain why a cached optimization for hashing cannot automatically be applied to equality semantics.

An experienced engineer can follow this one type from public concurrent operations through synchronization and representation changes without first understanding the entire CLR.

### [openjdk/jdk](https://github.com/openjdk/jdk)

**Language/role:** Java with native support; the standard Java modules, particularly `src/java.base`, within the JDK monorepo. Study the implementation of a general collection under concurrent mutation and collision-heavy inputs.

- **C1:** [ConcurrentHashMap's implementation overview](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/concurrent/ConcurrentHashMap.java) describes forwarding nodes during resize, reservation nodes during computation, tree bins, and validation after locking a bin's first node.
- **C3:** The design combines concurrent reads, CAS insertion into empty bins, and per-bin synchronization for other updates. It explains the choice to reuse nodes as lock objects and the space/contention tradeoffs, rather than hiding them behind an undifferentiated “thread safe” label.

The long in-source design commentary is itself the recommended entry point; concentrate on its invariants before reading individual public methods.

### [scala/scala](https://github.com/scala/scala)

**Language/role:** Scala; `src/library` on the `2.13.x` line. This entry concerns the standard library in the Scala 2 repository, not a separate count for the Scala 3 compiler.

- **C1:** The [immutable HashMap implementation](https://github.com/scala/scala/blob/2.13.x/src/library/scala/collection/immutable/HashMap.scala) uses a compressed hash-array mapped prefix tree. Its builder must copy aliased structure before further mutation, and publication includes release fences because nodes may have been mutated during construction.
- **C2:** The map participates in generic collection operations, factories, iterators, and key-set views rather than exposing only a standalone trie.
- **C3:** Persistent updates copy changed structure while retaining unchanged nodes; builders use controlled mutation to avoid paying that cost for every construction step. The code exposes the boundary between mutable construction and immutable results.

### [zloirock/core-js](https://github.com/zloirock/core-js)

**Language/role:** JavaScript; modular implementations/polyfills for ECMAScript library facilities. This is an intentional category extension to standard-library compatibility implementations, not a JavaScript engine or a wrapper-only package.

- **C1:** The [shared Map/Set implementation](https://github.com/zloirock/core-js/blob/master/packages/core-js/internals/collection-strong.js) maintains linked iteration order and removed-entry state so callbacks can delete or clear entries during traversal. It also normalizes zero keys and separates indexed lookup from iteration bookkeeping.
- **C2:** Shared internals support multiple collection APIs, while the package exposes modular features and a variant that avoids modifying global objects.
- **C4:** The [dated changelog](https://github.com/zloirock/core-js/blob/master/CHANGELOG.md) records years of engine-specific fixes, compatibility-data changes, and transitions from proposals into standardized features. Examples include older Symbol/multiple-copy fixes and continuing engine-support updates; this is stronger evidence than popularity.

## Functional libraries and process-oriented abstractions

### [ocaml/ocaml](https://github.com/ocaml/ocaml)

**Language/role:** OCaml; the `stdlib` subsystem of the compiler/runtime repository. Study persistent data structures implemented through modules and functors.

- **C1:** [map.ml](https://github.com/ocaml/ocaml/blob/trunk/stdlib/map.ml) records tree heights and performs single or double rotations when subtree heights diverge. Updates must preserve both ordering and balance while retaining existing structure where possible.
- **C2:** `Map.Make` accepts an ordered key module and supplies a full map API, including updates, folds, merging, and sequence conversion. The ordering contract is isolated from the balancing implementation.
- **C3:** Updates reuse unchanged subtrees and can return the original map when the inserted binding is already physically identical. The implementation makes the allocation consequences of persistence easy to inspect.

### [janestreet/base](https://github.com/janestreet/base)

**Language/role:** OCaml; a substantial replacement standard library. Its [README](https://github.com/janestreet/base/blob/master/README.org) explicitly defines replacement scope and excludes nonportable facilities such as I/O, which live in companion libraries.

- **C1:** The [comparator interface](https://github.com/janestreet/base/blob/master/src/comparator_intf.ml) gives comparison functions witness types: equal witnesses imply the same comparison behavior. This is a concrete way to encode ordering identity in types instead of relying on callers to keep compatible comparators together.
- **C2:** First-class comparator modules, functors, and derived comparators support many key and container types. The library also deliberately changes default comparison behavior rather than blindly re-exporting polymorphic structural comparison.

This is a useful comparison with OCaml's own library: both are substantive implementations, but they draw different boundaries around portability and error-prone generic operations. Development-branch interfaces include OxCaml-specific annotations, so they should not be mistaken for a frozen release API.

### [ghc/ghc](https://github.com/ghc/ghc)

**Language/role:** Haskell; `libraries/base` and its `ghc-internal` implementation, counted within the GHC monorepo. **Official project GitHub mirror** of GHC's GitLab repository. Study resource management in the presence of asynchronous exceptions and lazy evaluation.

- **C1:** [GHC.Internal.IO](https://github.com/ghc/ghc/blob/master/libraries/ghc-internal/src/GHC/Internal/IO.hs) implements `mask`, `bracket`, and `finally`. It preserves the enclosing masking state and explains why masked operations can still be interruptible when blocking.
- **C2:** The public [Control.Exception interface](https://github.com/ghc/ghc/blob/master/libraries/base/src/Control/Exception.hs) exposes reusable acquisition/use/release patterns and exception-handling combinators. These abstractions apply to arbitrary resources rather than only to files.

The distinction between evaluating a lazy value and executing an `IO` action is part of the correctness story; the implementation notes make it explicit instead of treating cleanup as an ordinary `try/finally` translation.

### [erlang/otp](https://github.com/erlang/otp)

**Language/role:** Erlang; the `lib/stdlib` application within OTP. Retain this for standard-library process abstractions, not as a general list of every networking or tooling application shipped with OTP.

- **C1:** [gen_server](https://github.com/erlang/otp/blob/master/lib/stdlib/src/gen_server.erl) defines callback-result handling, termination, system messages, timeouts, and exit-signal behavior. Its documentation explicitly distinguishes callback failures and warns that exit trapping is not automatic.
- **C2:** A single behavior supplies a reusable server lifecycle while application modules implement initialization, calls, casts, other messages, and code changes. Tracing and error reporting fit into that same structure.
- **C3:** Hibernation is exposed as a lifecycle choice with documented garbage-collection costs and suitability for idle servers. This connects resource management to workload behavior rather than assuming every server should use the same loop policy.

## Numerical and scientific language foundations

### [JuliaLang/julia](https://github.com/JuliaLang/julia)

**Language/role:** Julia; `base` and the in-tree `stdlib` packages. The [repository layout](https://github.com/JuliaLang/julia/blob/master/README.md) explicitly identifies `base` as part of the standard library. Externally maintained library repositories are not silently counted here.

- **C2:** [broadcast.jl](https://github.com/JuliaLang/julia/blob/master/base/broadcast.jl) uses `BroadcastStyle` traits and extensible `Broadcasted` representations to support custom containers, arrays, tuples, and scalars through one operation family.
- **C3:** Nested dotted operations can fuse into a single broadcast loop. The implementation separates expression construction, axis computation, allocation/materialization, and writing into an existing destination, exposing where intermediate work can be avoided.

This is a strong study of using multiple dispatch to make library-level optimizations extensible. The claims concern documented fusion and dispatch structure, not a benchmark against other numerical languages.

### [fortran-lang/stdlib](https://github.com/fortran-lang/stdlib)

**Language/role:** Fortran with Fypp metaprogramming; a community specification and reference implementation. Its [stated scope](https://github.com/fortran-lang/stdlib/blob/master/README.md) is a de facto standard library, not an ISO-mandated library that Fortran already requires.

- **C2:** The library brings together algorithms, containers, strings, testing support, and numerical facilities. The [sorting specification](https://github.com/fortran-lang/stdlib/blob/master/doc/specs/stdlib_sorting.md) shows overloaded interfaces spanning several intrinsic types, plus index and adjoint sorting for related arrays.
- **C3:** The specification explains different algorithms for partially ordered data, general data, and fixed-width values, together with optional caller-supplied workspace and memory costs. It also distinguishes stack scratch space from supplied work arrays.

The documented sorting interfaces include experimental status and explicit NaN limitations. Those qualifications matter: the study value is the visible specification/implementation tradeoff, not an assertion that every numerical edge case has a total ordering or a stable API.

## Coverage, verification, and limitations

Discovery used more than six distinct query families: C++ vendor implementations and ABI compatibility; embedded C libraries; portable libc and new-OS backends; WASI capability adaptation; Rust/Go/Swift libraries; D/Nim/Crystal generic facilities; managed-runtime concurrency; functional standard libraries and replacements; Julia/Fortran numerics; JavaScript polyfills; and game-oriented STL alternatives. Later searches largely returned already identified implementations, extensions rather than replacements, vendor forks, or projects outside the GitHub scope. The final additions cover genuinely different implementation constraints rather than enlarging one vendor family.

Every listed canonical repository URL was checked through its repository page or GitHub API. Each entry also uses opened documentation or source content beyond repository metadata; source excerpts were read through GitHub's content API when browser rendering obscured code. Repository archive status and available activity metadata were checked on the research date. None of the retained repositories was marked archived; that observation is not a guarantee of maintenance. Go, GHC, and relibc are explicitly identified as official mirrors, and GCC is identified as GitHub's public upstream mirror. Monorepos and shared ancestry are not counted twice.

Important boundaries and exclusions:

- [Zig's GitHub repository](https://github.com/ziglang/zig) explicitly says it moved to Codeberg and is not mirrored, so it is excluded. Unaffiliated replacement mirrors were not substituted.
- musl, glibc, Newlib, Bionic, and BSD libc families are important omissions from this selection. Searches encountered external canonical hosts and assorted GitHub copies; this report does not promote unverified copies as official implementations. Their absence is a coverage limitation, not a negative quality assessment.
- Ordinary library extensions, compiler-only projects, tutorial STLs, awesome-lists, wrapper-only bindings, and duplicate vendor forks were excluded. EASTL, Base, core-js, and Fortran stdlib are retained with explicit qualifications because they implement substantial alternative or compatibility library surfaces.
- Most links follow development branches or current documentation. A source inspection establishes the stated design at the time of research, not that it has shipped in every supported release. Some upstream overview prose is older than the implementation; specific code and concrete contracts take precedence over broad promotional claims.

No candidate code was executed, dependencies installed, repositories cloned, or benchmarks independently reproduced. Criterion judgments and suggested study value are grounded engineering inferences from the cited material; tests and release notes are evidence of engineering practice, not proof that the selected implementations are defect-free.
