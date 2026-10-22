# Memory safety and data race detectors

Research date: **2026-10-09**.

This report selects **20 GitHub repositories** implementing memory-error or data-race detection, including compiler/runtime sanitizers, binary instrumentation, debugging allocators, interpreters, execution explorers, static analyses, and accelerator-specific tools. General verification frameworks appear only where their implementation directly checks races or invalid memory accesses. Large repositories are counted once and their relevant subsystems are identified. The engineering judgments below are grounded in the linked implementation and documentation; they are a selection guide, not a claim that every component is exemplary or every detector is complete.

Criteria legend:

- **C1 — Difficult correctness:** memory lifetime, bounds, aliasing, synchronization, weak memory, or other demanding invariants and failure cases.
- **C2 — Reusable abstractions:** substantial interfaces or components supporting multiple analyses, programs, runtimes, or integration contexts.
- **C3 — Performance with structure:** explicit management of instrumentation cost, metadata size, analysis complexity, or execution-state growth through understandable mechanisms.
- **C4 — Sustained evolution:** documented changes over multiple years accompanied by compatibility work, testing, or complexity management. Repository age or a recent push alone does not qualify.

## Compiler, kernel, and binary instrumentation

### 1. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language/role:** C++ and C; Clang instrumentation and the `compiler-rt` sanitizer runtimes, particularly AddressSanitizer and ThreadSanitizer. Other sanitizer directories in this monorepo are part of the same selection.

Study the contract between inserted checks and runtime metadata, then compare addressability checking with concurrency history tracking. The [AddressSanitizer guide](https://clang.llvm.org/docs/AddressSanitizer.html) explains allocation errors, stack lifetime checks, container annotations, and the compiler/runtime split.

- **C1:** ASan's address translation must keep application memory, shadow memory, and unmapped gaps consistent across platform address layouts. The mapping definitions explicitly document these cases rather than hiding them behind a single platform assumption.
- **C3:** TSan encodes common memory accesses with compressed addresses and program-counter deltas, falling back to extended events when necessary. This is a concrete example of reducing diagnostic-history cost while preserving an explicit event format. ASan also exposes an inline-versus-outlined instrumentation tradeoff in its guide.

Entry points: [ASan mapping implementation](https://github.com/llvm/llvm-project/blob/main/compiler-rt/lib/asan/asan_mapping.h); [TSan access and trace implementation](https://github.com/llvm/llvm-project/blob/main/compiler-rt/lib/tsan/rtl/tsan_rtl_access.cpp).

### 2. [torvalds/linux](https://github.com/torvalds/linux)

**Language/role:** C; the KASAN memory-safety and KCSAN data-race detector subsystems in the Linux kernel's official GitHub tree.

This is the selection for studying detectors inside a kernel, where interrupts, memory barriers, allocator behavior, and hardware capabilities change the design constraints. KASAN offers generic, software-tag, and hardware-tag modes; KCSAN combines compiler instrumentation with sampled software watchpoints.

- **C1:** KCSAN interprets marked accesses and a subset of Linux memory-model ordering guarantees. Its documentation explicitly identifies missing-ordering cases it cannot detect. KASAN separately describes which kernel memory types each mode can check.
- **C3:** KCSAN's per-CPU skip counts and different task/interrupt stall durations expose the detection-probability versus latency tradeoff. KASAN's tag modes, allocation sampling, and inline/outline choices show how overhead changes deployment possibilities.

Entry points: [KCSAN design, semantics, and tuning](https://github.com/torvalds/linux/blob/master/Documentation/dev-tools/kcsan.rst); [KASAN modes and implementation details](https://github.com/torvalds/linux/blob/master/Documentation/dev-tools/kasan.rst).

### 3. [DynamoRIO/drmemory](https://github.com/DynamoRIO/drmemory)

**Language/role:** Primarily C; Dr. Memory, a memory debugger operating on unmodified application binaries through DynamoRIO.

Study how a binary-level tool tracks both addressability and initialization without compiler cooperation. The repository describes detection of invalid accesses, uninitialized reads, use-after-free, double frees, and leaks; its reusable shadow-memory framework is also a useful systems component in its own right.

- **C1:** The shadow implementation distinguishes defined, undefined, inaccessible, and bit-level states. Its cached mapping interface documents stale-cache and partial-byte concurrency hazards, exposing the correctness obligations of the detector itself.
- **C2:** Umbra separates mapping creation, region iteration, shadow reads/writes, and instrumentation from the client analysis.
- **C3:** Packed shadow state, shared default blocks, lazy allocation, and direct cached access are explicit techniques for controlling metadata and lookup cost.

Entry points: [shadow-state implementation](https://github.com/DynamoRIO/drmemory/blob/master/drmemory/shadow.c); [Umbra mapping and instrumentation API](https://drmemory.org/page_umbra.html).

### 4. [golang/go](https://github.com/golang/go)

**Language/role:** Go, assembly, and an imported native detector runtime; the Go compiler/runtime integration behind `-race`. This is an **official mirror**: the [repository README](https://github.com/golang/go/blob/master/README.md) identifies `go.googlesource.com/go` as canonical.

The distinct study subject is Go's language-runtime integration, not a second independent implementation of TSan. The [race runtime manifest](https://github.com/golang/go/blob/master/src/runtime/race/README) explicitly identifies its LLVM ThreadSanitizer foundation and records the native runtime revisions.

- **C1:** `RaceAcquire`, `RaceRelease`, and `RaceReleaseMerge` convey happens-before relationships between goroutines. The runtime carefully distinguishes scalar accesses from accesses to composite objects, where a conflicting write may affect a subobject.
- **C2:** Public and internal race hooks let runtime and library synchronization participate in one detector, while the Go command exposes it consistently through test, build, run, and install workflows.

Entry points: [runtime race interface and integration](https://github.com/golang/go/blob/master/src/runtime/race.go); [official race-detector guide](https://go.dev/doc/articles/race_detector). The guide states that detection depends on executing the relevant code paths.

## Debugging allocators and alternative memory metadata

### 5. [johnsonjh/duma](https://github.com/johnsonjh/duma)

**Language/role:** C and C++; DUMA, an Electric Fence-derived debugging allocator using inaccessible pages around allocations and after deallocation.

This is a compact alternative to per-access instrumentation. Study the allocation interposition and page-protection strategy, including alignment and allocator-compatibility consequences. It detects reads as well as writes when they touch protected memory; it is not complete bounds checking.

- **C1:** The allocator must maintain protected regions across allocation, freeing, and C/C++ allocation semantics. The source explains why faults occur at the offending instruction, while the change history records fixes involving thread safety, zero-sized allocation, and operators.
- **C4:** The changelog documents compatibility and correctness work across releases from the 2000s through 2020–2021, including multithreaded test fixes and later build-system/platform updates. This supports historical evolution, not an inference of release frequency today.

Entry points: [allocator implementation and design commentary](https://github.com/johnsonjh/duma/blob/master/src/duma.c); [version history](https://github.com/johnsonjh/duma/blob/master/CHANGELOG.md). Guard pages have substantial memory and allocation overhead, which the implementation explicitly acknowledges.

### 6. [j256/dmalloc](https://github.com/j256/dmalloc)

**Language/role:** C with C++ allocation support; a configurable replacement allocator for fence-post corruption, invalid allocation operations, and leak diagnostics.

Where DUMA relies on page faults, dmalloc provides allocator bookkeeping and configurable checking. Study how a debugging allocator maintains its own administrative structures without recursively allocating through itself.

- **C1:** Fence regions, delayed reuse of freed blocks, pointer validation, and memory-operation argument checks require consistent allocation state. The changelog includes concrete fixes for double-free reporting, overlapping `memcpy`, and pointer arithmetic.
- **C3:** `chunk.c` separates address-ordered and size-ordered skip lists, free-entry pools, and delayed-free queues. These structures make allocation lookup and metadata costs visible rather than relying on an undifferentiated heap scan.
- **C4:** The release history connects 2004 and 2007 allocator/test changes with 2020 cross-compilation, pointer-size, recursion, and library-build fixes.

Entry points: [chunk allocator and metadata structures](https://github.com/j256/dmalloc/blob/master/chunk.c); [release changelog](https://github.com/j256/dmalloc/blob/master/ChangeLog.txt). The README advertises release 5.6.5 from 2020; that is not presented as evidence of a recent release.

### 7. [GJDuck/EffectiveSan](https://github.com/GJDuck/EffectiveSan)

**Language/role:** C/C++; a research compiler and runtime adding dynamic type and subobject-bounds checks. This is a substantive implementation built into a vendored LLVM 4.0.1 tree, not a general-purpose LLVM fork counted for its inherited compiler code.

Study how high-level C/C++ type information survives lowering and becomes runtime metadata. The [design explanation](https://github.com/GJDuck/EffectiveSan/blob/master/README.md) connects front-end metadata, an instrumentation pass, low-fat allocation metadata, type checks, and bounds narrowing.

- **C1:** Checks distinguish allocation bounds from subobject bounds and handle effective types, array offsets, flexible-array members, coercions, and freed-object type state.
- **C3:** The runtime separates a common matching-type/zero-offset fast path from hashed layout lookup, limits lookup probing through compiler-generated metadata, and uses vector operations for bounds intersection.

Entry points: [architecture and examples](https://github.com/GJDuck/EffectiveSan/blob/master/README.md); [type-check and bounds runtime](https://github.com/GJDuck/EffectiveSan/blob/master/llvm-4.0.1.src/projects/compiler-rt/lib/effective/effective.c). Treat this as a historical research implementation with an old compiler dependency; its handling of non-fat pointers deliberately weakens checking.

### 8. [santoshn/softboundcets-34](https://github.com/santoshn/softboundcets-34)

**Language/role:** C++ compiler transformations and C runtime; the historical LLVM/Clang 3.4 SoftBound+CETS implementation.

This code illustrates pointer-associated metadata rather than allocation redzones alone. It is retained for the substantial spatial/temporal checking design; repository metadata showed the last push in 2014, and no present-day compiler compatibility is implied.

- **C1:** Spatial checks compare accesses against base/bound pairs; temporal checks compare a pointer's key with its allocation lock value. Bulk-memory operations need both kinds of validation, not merely a valid starting address.
- **C2:** The runtime exposes a consistent metadata load/store and checking interface, with spatial-only, temporal-only, and combined modes. Its trie-backed metadata accessors separate metadata representation from the instrumented program's ordinary pointers.

Entry points: [version-specific compiler integration and example](https://github.com/santoshn/softboundcets-34/blob/master/README.md); [runtime metadata and check implementation](https://github.com/santoshn/softboundcets-34/blob/master/softboundcets-lib/softboundcets.h). Other versioned copies of SoftBound+CETS are not counted separately.

## Interpreters and execution exploration with direct safety checks

### 9. [rust-lang/miri](https://github.com/rust-lang/miri)

**Language/role:** Rust; a MIR interpreter that detects undefined behavior in Rust programs and test suites, including invalid memory accesses and data races.

Study the combination of language-level checks with modeled allocations, threads, and atomics. The repository documentation explains aliasing checks, initialization and alignment failures, and the limits of interpreting platform APIs.

- **C1:** Its race detector treats allocation/deallocation as writes, models fences and read-modify-write operations, and explicitly accommodates C++20 release-sequence changes used by its concurrency model.
- **C3:** Vector-clock indices are reused only after all live threads have advanced beyond a joined thread's relevant history. The source gives the safety argument for this metadata-space optimization and explains when timestamp increments can be omitted.

Entry points: [supported checks and limitations](https://github.com/rust-lang/miri/blob/master/README.md); [data-race implementation and invariants](https://github.com/rust-lang/miri/blob/master/src/concurrency/data_race.rs). A passing interpreted execution is not a proof of soundness; the documented weak-memory exploration is incomplete.

### 10. [tokio-rs/loom](https://github.com/tokio-rs/loom)

**Language/role:** Rust; concurrency execution exploration with modeled synchronization and checked memory cells.

Its category fit goes beyond testing arbitrary race conditions: the runtime directly detects conflicting accesses to its modeled `UnsafeCell`. Study how replacement concurrency primitives connect a user's test to causality tracking and repeated execution.

- **C1:** The cell implementation tracks read/write lifetimes, the accumulated causal history of reads, and the last write. It checks both overlapping access guards and happens-before violations, retaining locations for diagnostics.
- **C2:** Replacement threads, atomics, shared ownership, synchronization primitives, and cells form a reusable testing interface for many concurrent data structures.
- **C3:** The execution explorer uses state-reduction techniques to limit redundant permutations, as described in the README.

Entry points: [integration and memory-model limitations](https://github.com/tokio-rs/loom/blob/master/README.md); [checked-cell runtime](https://github.com/tokio-rs/loom/blob/master/src/rt/cell.rs). The README identifies incomplete C11 coverage, including treatment of sequentially consistent accesses and missed load-buffering executions.

### 11. [dvyukov/relacy](https://github.com/dvyukov/relacy)

**Language/role:** C++; Relacy Race Detector, a header-based test and simulation framework for synchronization algorithms under relaxed memory models.

Study the explicit boundary between ordinary test code and instrumented variables, atomics, and threads. This is especially useful for understanding how a library-based detector preserves source-level diagnostics without a compiler pass.

- **C1:** `var<T>` routes loads/stores through detector state, checks initialization and object signatures, and reports data races through the execution context. Invariant checking receives deliberately different treatment from program accesses.
- **C2:** Generic variable proxies, replacement atomics/threads, test suites, and an optional standard-header interception layer allow the same engine to exercise many algorithms. The README also documents a consumable CMake package and the compatibility caveat of intercepting standard types.

Entry points: [integration and tested toolchain matrix](https://github.com/dvyukov/relacy/blob/master/README.md); [instrumented ordinary-variable implementation](https://github.com/dvyukov/relacy/blob/master/relacy/var.hpp). Unlike several historical selections here, its README records compiler/standard combinations tested in January 2026.

### 12. [MPI-SWS/genmc](https://github.com/MPI-SWS/genmc)

**Language/role:** C++; stateless model checking of concurrent C/C++ and experimental Rust inputs. The README explicitly identifies this GitHub repository as a **periodically updated official mirror of an internal repository**.

Retained for direct detection of non-atomic races, invalid dynamic-memory accesses, use-after-free, and double free. Study how errors depend on the selected memory model and how execution reduction interacts with program semantics.

- **C1:** The manual distinguishes source-language RC11 interpretation from the assumptions needed for IMM inputs, and demonstrates why causally dependent operations need not be ordered by happens-before.
- **C3:** Barrier-aware checking, symmetry reduction, and bounded exploration reduce state growth. Their preconditions matter: the manual warns that its barrier optimization cannot be used when a barrier's return value is significant.
- **C4:** The 2020–2026 changelog records LLVM compatibility changes, correctness fixes, new checking capabilities, internal refactoring, and the evolving library/frontend interface.

Entry points: [memory models, race checks, and reduction mechanisms](https://github.com/MPI-SWS/genmc/blob/master/doc/manual/features.md); [versioned evolution](https://github.com/MPI-SWS/genmc/blob/master/CHANGELOG.md).

## Dynamic and predictive race analysis

### 13. [stephenfreund/RoadRunner](https://github.com/stephenfreund/RoadRunner)

**Language/role:** Java; bytecode instrumentation and an event-analysis framework containing FastTrack race detectors. A historical codebase: the checked repository metadata showed its last push in 2017, and its compatibility notes concern Java 7/8.

Study both an analysis framework and the detailed engineering of a detector whose own metadata is accessed concurrently. FastTrack's source is unusually explicit about why particular state transitions and synchronization schemes were simplified.

- **C1:** The implementation documents thread-clock ownership, the invariant relating a thread's epoch to its vector clock, lock/volatile metadata synchronization, class initialization, and thread-ID reuse.
- **C2:** Tools consume a common event API and attach analysis-specific state to threads, locks, variables, and volatile fields; bytecode instrumentation is separated from those analyses.
- **C3:** Fast paths and epochs avoid full vector-clock work in common cases. Comments explain the removal of an optimistic synchronization scheme that increased correctness complexity without retaining a performance benefit.

Entry points: [framework structure and revision notes](https://github.com/stephenfreund/RoadRunner/blob/master/README.txt); [FastTrack implementation](https://github.com/stephenfreund/RoadRunner/blob/master/src/tools/fasttrack/FastTrackTool.java).

### 14. [focs-lab/rapid](https://github.com/focs-lab/rapid)

**Language/role:** Java; reusable offline analysis of execution traces, with multiple happens-before and predictive race-detection algorithms.

RAPID is particularly useful for comparing algorithms under a shared event representation. Its README explicitly says that instrumentation/logging comes from external tools and that performance optimality has not been its primary architectural goal.

- **C1:** The weak-causally-precedes implementation maintains separate ordering information, critical-section read/write sets, nested lock stacks, and special handling of reentrant acquisition. These are concrete correctness differences from a simple lockset checker.
- **C2:** A common `Engine` abstraction and parsers for STD, RoadRunner, RV-Predict, and CSV traces support distinct detection algorithms without duplicating trace ingestion. The repository also contains epoch-optimized and alternative predictive engines.

Entry points: [trace formats and analysis architecture](https://github.com/focs-lab/rapid/blob/master/README.md); [WCP event semantics](https://github.com/focs-lab/rapid/blob/master/src/engine/racedetectionengine/wcp/WCPEvent.java). It is not presented as a standalone instrumenter or as the fastest implementation of every included algorithm.

### 15. [runtimeverification/rv-predict](https://github.com/runtimeverification/rv-predict)

**Language/role:** Java analysis, C/C++ instrumentation/runtime components, and supporting OCaml tooling; predictive race analysis, including the RV-Predict/C path for threads and Unix signal handlers.

This historical implementation adds a different concurrency setting: signal handlers can interrupt threads and one another. Its [manual](https://github.com/runtimeverification/rv-predict/blob/master/doc/manual.md) explains trace production, separate offline analysis, and nested signal context in reports. Repository metadata showed the last push in 2022; the developer guide targets an older Clang/Java stack.

- **C1:** Predicting whether conflicting accesses can coexist requires feasible ordering constraints across threads and signals. The SMT interface distinguishes window-wide constraints from per-race assertions and separately represents fast and sound constraint sets.
- **C3:** A common solver interface supports single-threaded and parallel checking, with an explicit completion contract for asynchronous result callbacks. The developer guide also explains event-ring buffering and why signal-context producers spin instead of sleeping.

Entry points: [SMT race-checking interface](https://github.com/runtimeverification/rv-predict/blob/master/java/src/main/java/com/runtimeverification/rvpredict/smt/RaceSolver.java); [developer guide and trace-runtime buffering](https://github.com/runtimeverification/rv-predict/blob/master/doc/DEVELOPER.md). The manual's soundness/maximality claims are not generalized here into a guarantee for arbitrary configurations or unobserved traces.

## Static analysis of races and memory errors

### 16. [goblint/analyzer](https://github.com/goblint/analyzer)

**Language/role:** OCaml; a C static-analysis framework with a substantial data-race analysis and additional memory analyses.

Study race detection after points-to resolution, especially when an access might refer to a whole structure, a field, or an unknown pointer of a known type. The race implementation contains an extensive account of the memory-location relationships it must compare.

- **C1:** A write to `s` may conflict with an access to `s.f`; type-based locations introduce additional overlapping paths. The implementation explicitly combines prefix and type-suffix relationships so these cases are not treated as independent locations.
- **C2:** Lattice/domain combinators and a transfer-function interface let analyses reuse the framework's state and fixpoint machinery. The developer guide demonstrates composing variable maps with different abstract domains.
- **C3:** Lattice-enriched tries and lazy distribution of accesses avoid repeating comparisons already performed at an ancestor location, while retaining precise report locations.

Entry points: [race analysis and its location model](https://github.com/goblint/analyzer/blob/master/src/analyses/raceAnalysis.ml); [domain and analysis extension guide](https://github.com/goblint/analyzer/blob/master/docs/developer-guide/firstanalysis.md).

### 17. [facebook/infer](https://github.com/facebook/infer)

**Language/role:** Primarily OCaml; the Pulse memory-safety analysis and RacerD static race analysis within Infer. The repository is counted once.

Study how a detector uses procedure summaries to reason across calls without requiring an executable test. Pulse explains the distinction between latent memory errors and errors made manifest by a caller; RacerD explains ownership and thread-confinement information in its race summaries.

- **C1:** Pulse propagates conditions on invalid memory use across procedure boundaries. RacerD must distinguish accesses to owned objects from shared state and reason about cross-method synchronization contexts.
- **C2:** Compositional summaries allow findings inside a callee to participate in caller analysis, including across files and classes.
- **C3:** RacerD deliberately uses restricted abstractions to make analysis practical on changing codebases. Its documentation specifies the resulting blind spots: aliasing, different locks collapsed into a boolean lock abstraction, escaping objects, and weak-memory behavior.

Entry points: [Pulse semantics and unknown-call limitations](https://fbinfer.com/docs/checker-pulse/); [RacerD summaries, annotations, and limitations](https://fbinfer.com/docs/checker-racerd/). These are bug-finding analyses, not comprehensive proofs of memory or concurrency safety.

## GPU and AI-accelerator detectors

### 18. [mc-imperial/gpuverify](https://github.com/mc-imperial/gpuverify)

**Language/role:** C# and Python, with an LLVM/Boogie/SMT toolchain; static race- and barrier-divergence analysis for CUDA and OpenCL kernels.

Study how GPU execution concepts become verification conditions instead of a runtime access log. This is a historical research toolchain: the checked repository metadata showed its last push in 2022, and its developer guide depends on LLVM 6.0 and older solver tooling.

- **C1:** Race instrumentation distinguishes group-shared arrays from global accesses and introduces contracts/invariants reflecting whether modeled threads belong to the same workgroup. It also treats barrier effects and selected benign writes specially.
- **C2:** `IRaceInstrumenter` and the abstract `RaceInstrumenter` organize alternative instrumentation strategies around a shared verifier, access representation, and loop-invariant machinery. The surrounding pipeline separates translation, verification-condition generation, and solving.

Entry points: [race instrumentation and invariant generation](https://github.com/mc-imperial/gpuverify/blob/master/GPUVerifyVCGen/RaceInstrumenter.cs); [toolchain structure and dependencies](https://github.com/mc-imperial/gpuverify/blob/master/Documentation/developer_guide.rst). Its documented benign-race policy should be considered when interpreting a successful check.

### 19. [tudasc/cusan](https://github.com/tudasc/cusan)

**Language/role:** C/C++; CuSan, LLVM-based analysis and runtime modeling of races between asynchronous CUDA operations and host accesses, with CUDA-aware MPI integration.

This is not a second copy of TSan: its substantive contribution is exposing accelerator operations and synchronization to TSan. The README explains the compile-time device-kernel analysis, host instrumentation, and runtime event translation.

- **C1:** CUDA streams are represented through TSan fibers, including default-stream ordering and the distinction between blocking and nonblocking streams. Allocation records distinguish device, pinned, and managed memory.
- **C2:** The design separates kernel access information, LLVM instrumentation, runtime stream/allocation models, and the TSan interface. This supports ordinary CUDA applications and combinations with MPI semantics.

Entry points: [integration model, examples, and constraints](https://github.com/tudasc/cusan/blob/main/README.md); [stream and allocation runtime](https://github.com/tudasc/cusan/blob/main/lib/runtime/CusanRuntime.cpp). Its documented scope is host/asynchronous-operation races; the README also requires serialized compilation to keep shared kernel-analysis metadata consistent.

### 20. [Ascend/mssanitizer](https://github.com/Ascend/mssanitizer)

**Language/role:** Primarily C++; MindStudio Sanitizer for Ascend AI-processor operators, covering invalid memory access, uninitialized memory, pipeline/core races, and synchronization errors.

This is an **official GitHub source copy with project issue and release links directed to GitCode**. The English README dates full open-sourcing to December 31, 2025; no C4 claim is made from that short public history. Study the adaptation of sanitization to explicit accelerator memory spaces and instruction pipelines.

- **C1:** The architecture models different device memory regions, per-byte initialization/addressability, allocation lifetime, and shared-memory mappings across devices. Synchronization checking pairs pipeline events by source, destination, and event ID.
- **C2:** Runtime hooks and instrumentation feed normalized records to a checker that constructs analyses through `SanitizerFactory`/`SanitizerBase`; memory, race, and synchronization checking share this record-processing infrastructure.
- **C3:** Each enabled tool type has an independent consumer queue and thread, making parallel analysis an explicit architectural choice rather than an opaque performance claim.

Entry points: [scope, provenance, and project links](https://github.com/Ascend/mssanitizer/blob/master/README_EN.md); [architecture, shadow state, and processing design](https://github.com/Ascend/mssanitizer/blob/master/docs/en/development_guide/architecture.md).

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, including native sanitizers and binary instrumentation; happens-before detection in C++, Java, and Go; Rust unsafe-code interpreters and concurrency exploration; SoftBound/EffectiveSan-style pointer metadata; guarded/debugging allocators and embedded use; static C/OpenMP analysis; GPU/CUDA race and memory checking; and Ascend-specific checking. Follow-up searches targeted exact project names, design documents, source files, and repository provenance. Later searches mostly returned already covered families, general allocators/hardening tools, benchmarks, and broader concurrency testers; they did not justify expanding the list with weaker category matches.

Every retained canonical GitHub URL was checked through the GitHub API or an opened repository page. Each selection also has an opened implementation or substantive design source beyond repository identity, and the report distinguishes runtime libraries, language integrations, and research extensions sharing infrastructure. Repository metadata was inspected for archive status, branch identity, and maintenance context; no C4 rating is based solely on metadata. The few stated last-push dates describe the checked snapshot, not a definitive abandonment judgment.

Important exclusions and consolidation:

- **Valgrind/Memcheck/Helgrind/DRD:** central to this field, but the [official repository instructions](https://valgrind.org/downloads/repository.html) identify Sourceware. This search did not establish an official substantive GitHub mirror, so unofficial mirrors were not substituted.
- **`google/sanitizers`:** its [README describes the repository as archived documentation/helper code](https://github.com/google/sanitizers/blob/master/README.md) and points to LLVM for the core implementation. It is not counted separately, regardless of the GitHub API archive flag.
- **Standalone Archer:** the [project README](https://github.com/PRUNERS/archer/blob/master/README.md) says development moved into LLVM and marks the standalone project deprecated. It is consolidated with the LLVM selection rather than counted as another current detector.
- **OpenRace:** its published GitHub location, `coderrect-inc/OpenRace`, returned 404 during verification. **LLOV:** the [inspected repository](https://github.com/utpalbora/LLOV) says its source will be released later and provides a binary-oriented layout. Neither satisfied this report's source-inspection requirement.
- General heap profilers, allocator hardening without a substantial detector focus, benchmark-only suites, wrappers around closed detector engines, and concurrency testers without established direct memory/race checking were not used to fill the list. Other versioned SoftBound copies and inherited LLVM code were not counted again.

This was read-only source/documentation research: no candidate was cloned, built, installed, or executed. Platform support and reproducibility are therefore documented claims, not locally validated outcomes. Historical compiler dependencies, incomplete execution coverage, finite exploration bounds, and deliberate static-analysis approximations materially affect what each tool can detect; the linked limitations are part of the selection, not incidental deployment details.
