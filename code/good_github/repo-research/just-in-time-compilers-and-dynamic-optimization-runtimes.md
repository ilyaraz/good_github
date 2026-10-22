# Just-in-time compilers and dynamic optimization runtimes

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing runtime native-code generation, speculative specialization, reusable JIT infrastructure, or dynamic binary translation. It includes both integrated language VMs and smaller components that expose the machinery more directly. Monorepos are counted once, with the relevant subsystem named. Runtime compilation at module load is included even when a project calls that mode “AOT”; ordinary offline compilers, application wrappers, and optimization unrelated to executing program code are outside the scope.

The criteria below are evidence-based reasons to study particular subsystems, not a claim that every component is exemplary. Repository pages and the linked implementation/design material were inspected. Documentation can describe an earlier architecture; dated accounts and experimental limitations are identified where relevant. Inclusion does not assert a particular maintenance cadence or deployment readiness.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions serving multiple use cases. **C3** — concrete performance constraints addressed through understandable architectural choices. **C4** — sustained evolution accompanied by compatibility, testing, or complexity-management evidence. Every entry meets at least two; C4 is used sparingly rather than inferred from repository age.

## Reusable code generation and compiler infrastructure

### 1. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language/role:** C++; ORC JIT, JIT linking, and runtime support within the LLVM monorepo.

Study runtime compilation as a linking and resource-management problem. ORC models independently named libraries, symbol lookup, materialization, and compilation layers instead of assuming that every client simply compiles one LLVM module.

- **C1:** Concurrent lookup and compilation require dependencies to become ready before executable addresses are released. The design also addresses duplicate definitions, symbol visibility, lazy-compilation failures, and removable code.
- **C2:** Custom `MaterializationUnit` implementations admit representations other than LLVM IR; compilation and linking layers support in-process and remote execution, debuggers, REPLs, and other language VMs.
- **C3:** Eager versus lazy materialization and configurable compilation dispatch make startup cost and concurrency explicit architectural choices.

Start with the substantive [ORC design and implementation guide](https://llvm.org/docs/ORCv2.html), especially `ExecutionSession`, `JITDylib`, materialization, and dependency tracking.

### 2. [asmjit/asmjit](https://github.com/asmjit/asmjit)

**Language/role:** C++; low-latency machine-code generation library, including assembler, builder, compiler, and JIT runtime abstractions.

Useful for understanding what an embeddable code generator needs below a language-specific optimizer: ownership of code buffers, labels, sections, relocations, register allocation, and executable-code installation.

- **C1:** `CodeHolder` distinguishes relocation entries from unresolved-label and cross-section fixups. Instruction validation is configurable, with distinct validation points before encoding and before creating intermediate nodes.
- **C2:** The emitter hierarchy lets clients choose direct assembly or an editable instruction representation and compiler-level services while sharing code storage and runtime facilities.
- **C3:** The documentation explains the cost of extra validation and exposes size-oriented encodings and optimized alignment rather than hiding these choices behind a generic “fast” label.

Read the [core API and implementation examples](https://asmjit.com/doc/group__asmjit__core.html), particularly explicit relocation, emitter types, and diagnostic options.

### 3. [zherczeg/sljit](https://github.com/zherczeg/sljit)

**Language/role:** C; portable low-level JIT compiler.

Study a compact portability layer that retains explicit control over registers and calling conventions. It is especially useful when a bytecode implementation wants native code without adopting a large optimizing compiler.

- **C1:** The public header specifies overlapping scratch/saved register sets and the permitted register context. Its protected executable allocator uses separate writable and executable mappings; dynamic patching must account for their address offset.
- **C2:** The same instruction API covers multiple processor families while exposing integer, floating-point, vector, stack, and CPU-feature facilities. Platform ABI handling is part of the abstraction.

The [annotated public interface](https://github.com/zherczeg/sljit/blob/master/sljit_src/sljitLir.h) is a substantive design document. The [first-program walkthrough](https://github.com/zherczeg/sljit/blob/master/docs/tutorial/02-your-first-program.md) explains the register and function-entry model.

### 4. [vnmakarov/mir](https://github.com/vnmakarov/mir)

**Language/role:** C; lightweight MIR-based JIT, interpreter, and C frontend.

Study a middle-sized compiler whose module/linking model is small enough to follow without losing real runtime concerns. MIR here means this project's Medium Internal Representation, not LLVM's machine IR.

- **C2:** A context owns modules, functions, imports, exports, and typed operations. External-symbol resolution allows generated programs to call native functions; textual and programmatic construction share the same representation.
- **C3:** The linking API selects interpretation, eager native compilation, lazy function compilation, or lazy basic-block compilation. These are concrete alternatives for balancing compilation work against executed code coverage.

Begin with the [MIR specification and API](https://github.com/vnmakarov/mir/blob/master/MIR.md), particularly module loading, `MIR_link`, execution interfaces, and interpreter-assisted data initialization. The repository overview supplies the optimizer and source-organization context without requiring its benchmark comparisons to be accepted.

### 5. [dstogov/ir](https://github.com/dstogov/ir)

**Language/role:** C; lightweight optimizing JIT framework using a sea-of-nodes representation.

This is a useful study in fitting a recognizable optimizing compiler pipeline into an embeddable framework. The repository explicitly warns that it does not provide a stable library interface and recommends source embedding.

- **C2:** The IR construction API, typed constants, function prototypes, loaders, and emission facilities separate frontend needs from optimization and target code generation.
- **C3:** The public interface exposes sparse conditional constant propagation, global code motion, scheduling, liveness, coalescing, register allocation, and instruction selection as separate stages. Graph dumps, disassembly, GDB registration, and `perf` integration make their effects inspectable.

Read the [public compiler interface](https://raw.githubusercontent.com/dstogov/ir/master/ir.h) alongside the repository's worked IR-building example. The interface also exposes verification and code-patching operations, useful follow-on areas for correctness study.

## Meta-JITs and generated execution engines

### 6. [oracle/graal](https://github.com/oracle/graal)

**Language/role:** Primarily Java; Graal compiler and Truffle language-implementation framework. This entry concerns `compiler/` and `truffle/`, not merely Native Image.

Study how language interpreters expose specialization information to a shared compiler, and how optimized code remains tied to assumptions about mutable language state.

- **C1:** Truffle's `Assumption` is a one-way validity abstraction. Invalidation cannot be undone; failed checks can trigger node replacement. Its placement in final fields matters to compiler treatment, making the optimization contract explicit.
- **C2:** The monorepo separates the compiler, language framework, instrumentation tools, and language implementations. The same assumption and node mechanisms are available to different guest languages rather than being hardwired to JavaScript or Python.

Start with the [Assumption API contract](https://www.graalvm.org/truffle/javadoc/com/oracle/truffle/api/Assumption.html). The [RootNode API](https://www.graalvm.org/truffle/javadoc/com/oracle/truffle/api/nodes/RootNode.html) is a complementary entry into compilation, partial evaluation, and runtime scheduling.

### 7. [pypy/pypy](https://github.com/pypy/pypy)

**Language/role:** RPython/Python, with generated native runtime code; Python implementation and reusable meta-tracing machinery.

Study the distinction between tracing a user's bytecode and tracing an interpreter executing that bytecode. The relevant subsystem is `rpython/jit`, with code writing, the meta-interpreter, optimization, and machine backends separated.

- **C1:** Traces record one observed path and insert guards to check assumptions on subsequent execution. Returning to interpretation and preserving the meaning of virtual or escaping objects are central correctness concerns.
- **C2:** Interpreter hints and the distinction between loop-identifying “green” variables and varying “red” variables connect different interpreters to the same JIT generator.
- **C3:** Trace flattening removes interpreter dispatch, while virtual objects allow allocations and field accesses to disappear when escape behavior permits it.

The [PyJitPl5 implementation overview](https://rpython.readthedocs.io/en/latest/jit/pyjitpl5.html) explains these mechanisms and points to their source directories. Some examples use historical Python bytecodes; treat them as architectural explanations rather than a current opcode reference.

### 8. [ykjit/yk](https://github.com/ykjit/yk)

**Language/role:** Rust runtime with an LLVM/C integration toolchain; meta-tracing for existing C interpreters.

Study a different route to interpreter reuse: instrument a C interpreter at build time, retain an AOT representation, and reconstruct specialized JIT traces while it runs. This is a research-oriented selection; the documentation labels example interpreter integrations pre-alpha.

- **C2:** The architecture separates `ykllvm`, which embeds the information needed for tracing, from the Rust runtime. AOT IR, recorded interpreter paths, JIT IR, and executable traces have distinct roles.
- **C3:** Hot-loop and side-trace thresholds, compilation worker counts, and separate tracing/compiling/deoptimizing timing statistics expose the costs that determine whether tracing pays off.

The [yk book](https://ykjit.github.io/yk/print.html) covers the architecture, runtime controls, and debugging of generated code. Its documented platform/toolchain requirements are a limitation to check before treating it as a general deployment option; the LLVM fork is not counted separately.

### 9. [luajit-remake/luajit-remake](https://github.com/luajit-remake/luajit-remake)

**Language/role:** C++ and LLVM tooling; Deegen-generated Lua execution engines and a separately engineered Lua runtime.

This is a distinct implementation, not a second listing of LuaJIT's source. Study generating an interpreter and baseline JIT from shared bytecode semantics. The repository identifies the larger multi-tier project as work in progress and far from production-ready.

- **C1:** The author's baseline-JIT design explains a subtle copy-and-patch hazard: treating runtime constants as external-symbol addresses can let LLVM incorrectly eliminate zero checks. It discusses systematic handling of those symbol-range assumptions.
- **C2:** Shared semantic definitions and APIs for bytecode operations, calls, and inline caches reduce duplicated interpreter/JIT implementation work.
- **C3:** Stencil preparation happens at build time; runtime generation copies machine-code fragments and patches runtime values. This targets baseline compilation latency through an explicit division of work.

Read [Building a baseline JIT for Lua automatically](https://sillycross.github.io/2023/05/12/2023-05-12/), a primary design account linked by the repository. Its implemented baseline should not be confused with completion of all planned optimizing tiers.

## Dynamic language VMs

### 10. [v8/v8](https://github.com/v8/v8)

**Language/role:** C++; JavaScript/WebAssembly VM. **Official GitHub mirror** of the Chromium-hosted V8 repository.

Maglev is a particularly approachable subsystem for studying how an industrial VM balances compilation latency, speculative optimization, and GC integration.

- **C1:** Deoptimization metadata maps optimized values back to interpreter state. Object-shape dependencies, changes to globals, numeric representations, and GC-visible stack slots constrain optimization.
- **C3:** The Maglev design uses a small SSA pipeline, a bytecode prepass, early specialization during graph construction, and simple allocation rules to occupy a useful point between baseline code generation and more expensive optimization.
- **C4:** The dated design account describes the 2021 addition of Sparkplug and the 2023 addition of Maglev, including reuse of the established deoptimizer and its testing rather than creating an independent recovery mechanism.

Read the [Maglev architecture account](https://v8.dev/blog/maglev). It describes the 2023 tiering design; its benchmark results and rollout statements are historical, not current performance guarantees.

### 11. [WebKit/WebKit](https://github.com/WebKit/WebKit)

**Language/role:** C++; JavaScriptCore's baseline, DFG, and FTL execution machinery within the WebKit monorepo.

Study speculative optimization as a contract between shared bytecode semantics, profiling tiers, optimizing IRs, watchpoints, and on-stack replacement.

- **C1:** OSR exits must reconstruct live baseline state without repeating observable side effects or exposing partially updated bytecode state. The design identifies points where exiting is illegal and explains how invalidation interacts with speculation.
- **C3:** DFG's compressed representation of exit-state updates avoids eagerly materializing large stackmaps. Tier control and profiling make expensive optimization conditional on execution behavior.

The primary [Speculation in JavaScriptCore](https://webkit.org/blog/10308/speculation-in-javascriptcore/) article is unusually detailed, including machine-level exit behavior and IR semantics. It is a 2020 design account and should be read alongside the current JavaScriptCore subsystem when tracking implementation changes.

### 12. [LuaJIT/LuaJIT](https://github.com/LuaJIT/LuaJIT)

**Language/role:** C and architecture-specific assembly; Lua tracing JIT. **Project GitHub mirror**, as identified by its repository page.

Study a compact tracing runtime with explicit snapshot restoration and representation-aware exits. This is a strong comparison with both PyPy's meta-tracing and method-based VMs.

- **C1:** Snapshot recovery restores constants, registers, spills, numeric representations, and GC references. The implementation also reconstructs allocations and stores that optimization had removed, including FFI data and architecture-dependent layouts.
- **C3:** Allocation sinking makes the successful trace cheaper but moves work into uncommon recovery paths. The source makes that performance/correctness tradeoff visible rather than presenting escape analysis in isolation.

Start with the [snapshot implementation](https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/lj_snap.c). The project's [DynASM explanation](https://luajit.org/dynasm.html) provides complementary context for its runtime code-generation tooling.

### 13. [ruby/ruby](https://github.com/ruby/ruby)

**Language/role:** C runtime with Rust JIT implementation; focus on YJIT within CRuby.

Study lazy basic-block versioning inside a highly dynamic existing runtime. This entry counts Ruby once and focuses on YJIT rather than treating each Ruby JIT subsystem as a separate repository.

- **C1:** The code generator records dependencies on method lookup, basic-operator definitions, constant paths, singleton-class assumptions, and single-Ractor execution. Invalidatable blocks need an entry exit before those assumptions can be relied upon.
- **C3:** Lazy compilation, call/cold thresholds, and executable-memory limits make warmup and code-size costs explicit. The structure is useful for comparing local block specialization with whole-method optimization.
- **C4:** The [2021 Ruby 3.1 release](https://www.ruby-lang.org/en/news/2021/12/25/ruby-3-1-0-released/) documents YJIT's integration; the later Ruby 3.4 manual documents the Rust implementation and both bootstrap and full-suite testing.

Entry points: the versioned [YJIT manual](https://docs.ruby-lang.org/en/3.4/yjit/yjit_md.html) and current [code-generation implementation](https://raw.githubusercontent.com/ruby/ruby/master/yjit/src/codegen.rs). Version-specific defaults in the manual are not asserted to be current defaults.

### 14. [erlang/otp](https://github.com/erlang/otp)

**Language/role:** Erlang, C, and C++; BeamAsm load-time JIT in the ERTS emulator.

Study a JIT that deliberately preserves much of its interpreter's execution model. BeamAsm converts BEAM instructions to native code while retaining register-array conventions and the surrounding scheduling runtime.

- **C1:** Native return addresses change exception and garbage-collection requirements. The design specifies stack reservations, valid frame-pointer chains, transitions to the C stack, and code updates through writable/executable mappings.
- **C3:** Shared global code fragments avoid repeating context-switch and error-handling sequences in every compiled module. Eliminating dispatch while limiting cross-instruction optimization is an explicit load-time and code-size tradeoff.

The [BeamAsm internal design document](https://github.com/erlang/otp/blob/master/erts/emulator/internal_doc/BeamAsm.md) includes these invariants and a file-by-file guide to `erts/emulator/beam/jit`.

### 15. [python/cpython](https://github.com/python/cpython)

**Language/role:** C runtime and Python build tooling; adaptive interpreter, trace optimizer, and experimental copy-and-patch JIT.

Study incremental JIT integration into an existing interpreter, including how one bytecode definition feeds several execution forms. The relevant subsystem is the JIT described in `InternalDocs/jit.md`, not the entire standard library.

- **C1:** Trace recording must see current specialization data. Executors track invalidation dependencies; side exits and deoptimizing exits have different rules for whether another trace is recorded.
- **C3:** Cross-instruction optimization operates on micro-ops, while LLVM-generated stencils are prepared at build time and completed with runtime values during native-code construction. A micro-op interpreter provides a simpler execution path for debugging the optimizer.

Read the [internal JIT design](https://github.com/python/cpython/blob/main/InternalDocs/jit.md). It explicitly describes experimental build modes, so inclusion does not imply that native JIT execution is universally enabled or beneficial for every Python workload.

## Managed bytecode runtimes

### 16. [openjdk/jdk](https://github.com/openjdk/jdk)

**Language/role:** C++ HotSpot runtime and Java tests/libraries; C1/C2 compilation and tier-management machinery.

Study the runtime policy around an optimizing compiler: selecting a compilation level, deciding when enough profiling exists, managing compiler load, and replacing executing code.

- **C1:** The policy handles methods that cannot be compiled by a particular compiler, separate OSR compilability, invalidation of existing OSR code, and immediate deoptimization when returning a method to interpretation for profiling. Locking and safepoint restrictions appear directly in these paths.
- **C3:** Invocation/backedge thresholds are scaled using compiler-queue feedback. The code distinguishes interpretation, simple compilation, limited profiling, full profiling, and full optimization rather than using a single hotness threshold.

The current [compilation policy implementation](https://raw.githubusercontent.com/openjdk/jdk/master/src/hotspot/share/compiler/compilationPolicy.cpp) is the main reading entry point; its transition comments connect policy decisions to the concrete implementation.

### 17. [dotnet/runtime](https://github.com/dotnet/runtime)

**Language/role:** C++ runtime/compiler with C# libraries and tests; CoreCLR RyuJIT subsystem.

Study a production compiler pipeline that starts with managed IL and ends with machine code plus the metadata needed by the VM. Focus on RyuJIT rather than counting Mono and other runtime components separately.

- **C1:** The distinction between tree-form HIR and linear LIR includes execution-order invariants. Final generation must produce exception-handling, GC, and debugging information as well as instructions; register allocation and frame layout must agree with those outputs.
- **C3:** The documented pipeline separates importation, SSA/value numbering, range analysis, loop optimization, rationalization, lowering, allocation, and emission. It shows exactly where checks can be eliminated and where representation changes prepare code for the backend.

Read the [RyuJIT overview](https://github.com/dotnet/runtime/blob/main/docs/design/coreclr/jit/ryujit-overview.md), especially IR forms and the phase table. The document flags some older diagrams itself; its explicit phase invariants are the more dependable study guide.

### 18. [eclipse-omr/omr](https://github.com/eclipse-omr/omr)

**Language/role:** C/C++; reusable runtime components, optimizing compiler, and JitBuilder.

Study extracting compiler and runtime infrastructure from a language-specific VM. This is the shared OMR implementation, not a duplicate listing of an OpenJ9 downstream tree.

- **C2:** The repository separates compiler technology, JitBuilder, GC, threading, portability, and per-interpreter/per-thread contexts. Its language-independent test framework allows components to be exercised outside a complete guest-language runtime.
- **C3:** The compiler's documented recompilation strategy spends progressively more optimization effort on frequently executed methods. Fixed optimization levels, method-limit files, and phase traces make the cost and behavior observable.
- **C1:** The troubleshooting guide recognizes that changing compilation thresholds can alter concurrency ordering and mask a failure. It provides methods for isolating incorrect-result and crash-producing compilations rather than assuming interpreter/compiler equivalence.

Start with [compiler problem determination](https://github.com/eclipse-omr/omr/blob/master/doc/compiler/ProblemDetermination.md), which explains actual optimization modes and IR diagnostics as well as debugging procedures.

## WebAssembly and numerical specialization

### 19. [bytecodealliance/wasmtime](https://github.com/bytecodealliance/wasmtime)

**Language/role:** Rust; WebAssembly runtime and the in-repository Cranelift code generator. Counted once for both.

Study the boundary between compilation artifacts, executable memory, shared compiled modules, and instance-local state.

- **C1:** Module parsing and validation precede use of untrusted input. Compilation artifacts carry trap and unwind information; executable memory transitions from writable to executable. Indirect calls require compatible function types across independently compiled modules.
- **C2:** `Engine`, `Module`, and `Store` separate shared compilation resources, compiled code, and execution state. Generated code obtains instance-specific information through `VMContext`, allowing one compiled module to serve multiple instantiations.
- **C3:** Independent function compilation and code sharing address compilation work and per-instance memory costs directly.

The [architecture guide](https://docs.wasmtime.dev/contributing-architecture.html) provides the detailed contracts. Some crate names and statements about available engines lag the repository, which also contains Winch and Pulley; this entry relies on the shared-code and runtime-boundary design, not those historical exclusivity claims.

### 20. [wazero/wazero](https://github.com/wazero/wazero)

**Language/role:** Go and assembly; embedded WebAssembly runtime with native compiler and interpreter engines.

Study generating and calling native code from a Go implementation without a CGO compiler dependency. Wazero calls compilation during `Runtime.CompileModule` AOT; it belongs here as native compilation inside the host runtime, not as profile-guided recompilation.

- **C1:** The rationale explains why generated code entered through assembly trampolines is not asynchronously preempted as ordinary Go code. Cancellation checks return to Go so other goroutines can run and set the cancellation state; merely polling from native code could defeat cancellation.
- **C2:** The engine exposes WebAssembly execution to Go embedders while separating frontend translation, SSA, target backends, and call machinery. Interpreter and compiler implementations share the user-facing runtime model.

Read the [design rationale](https://github.com/wazero/wazero/blob/main/RATIONALE.md), especially compiler execution and cancellation, then inspect the [wazevo source tree](https://github.com/wazero/wazero/tree/main/internal/engine/wazevo). The rationale also describes concurrency hammer tests.

### 21. [numba/numba](https://github.com/numba/numba)

**Language/role:** Primarily Python with native support; type-specializing compiler for Python/NumPy functions using LLVM.

Study where a numerical JIT should perform optimizations that depend on array semantics, before lowering erases that information.

- **C2:** The compiler stages distinguish bytecode translation, untyped IR rewriting, type inference, typed rewriting, lowering, and execution. Explicit signatures and observed argument types both feed specialization.
- **C3:** Typed array rewrites fuse producer/consumer loops and eliminate intermediate arrays. The architecture explains why recovering the same opportunity after lowering each array operation into LLVM loops is difficult.

The [Numba architecture guide](https://numba.readthedocs.io/en/stable/developer/architecture.html) includes worked IR transformations and links to the implementing stages. Read its version qualification on object-mode fallback carefully; this selection does not imply support for arbitrary Python programs.

### 22. [JuliaLang/julia](https://github.com/JuliaLang/julia)

**Language/role:** Julia plus C/C++; specializing language runtime with a custom LLVM ORC-based JIT.

Study what a language runtime adds above a generic JIT library: code-instance lookup, a language-specific optimization pipeline, runtime intrinsics, object linking, and publication of compiled methods.

- **C1:** Object allocation, garbage collection, and exception behavior are represented through custom intrinsics that must be lowered at appropriate stages. The design also explains why linker restrictions can serialize an otherwise concurrency-oriented optimize/compile/link pipeline.
- **C3:** The optimization pipeline deliberately orders inexpensive simplification before more costly loop/scalar transformations, vectorization, and target code generation. This is a concrete account of both optimizing numerical kernels and controlling compiler work.

Read [JIT Design and Implementation](https://docs.julialang.org/en/v1/devdocs/jit/), which identifies `src/jitlayers.cpp` and `src/pipeline.cpp`. Its RuntimeDyld concurrency restriction is documented platform-dependent design context, not a claim that every current platform uses the same linker.

## Dynamic binary translation and instrumentation

### 23. [qemu/qemu](https://github.com/qemu/qemu)

**Language/role:** Primarily C; Tiny Code Generator and dynamic translation inside the emulator. **Official GitHub mirror**; contribution hosting is elsewhere.

Study runtime compilation of an existing instruction set, where CPU state and interrupt behavior constrain the optimizations.

- **C1:** Translation blocks specialize on CPU state and may only be reused when that state matches. State changes that can unmask interrupts require exiting through the main execution loop; bypassing it would change observable guest behavior.
- **C3:** Direct block chaining and lookup-and-jump mechanisms avoid repeated dispatcher trips. The design distinguishes the faster paths from the required slow path and explains when each is valid.

The [translator internals guide](https://www.qemu.org/docs/master/devel/tcg.html) is the main entry point, covering state specialization, block chaining, self-modifying code, and exception support. This entry concerns TCG, not hardware-assisted virtualization alone.

### 24. [DynamoRIO/dynamorio](https://github.com/DynamoRIO/dynamorio)

**Language/role:** C/C++ and assembly; runtime code manipulation, dynamic instrumentation, and code-cache execution.

Study how to transform a running native program while preserving its machine state. This is also a reusable substrate for profiling and dynamic analysis rather than a JIT tied to one source language.

- **C1:** Clean calls must switch stacks and preserve application registers/state. Floating-point/SIMD preservation is an explicit choice; spill-slot lifetimes and restoration barriers impose further contracts on instrumentation.
- **C2:** The code-manipulation API provides instruction representations, insertion hooks, state-preservation mechanisms, and thread-local facilities for different clients.
- **C3:** Clean-call analysis can reduce saved state or inline simple callees, connecting instrumentation convenience to its execution overhead.

Read the [Code Manipulation API](https://dynamorio.org/API_BT.html). Its separate [JIT optimization design note](https://dynamorio.org/page_jitopt.html) is historical and partly experimental; do not assume every optimization described on that branch is in the main implementation.

### 25. [FEX-Emu/FEX](https://github.com/FEX-Emu/FEX)

**Language/role:** C++ and assembly; user-mode x86/x86-64 translation for Arm64 Linux, centered on FEXCore.

Study an emulator-specific SSA representation rather than a general language compiler IR. The representation keeps guest CPU state, guest memory, scalar/vector operations, and explicit machine interfaces distinguishable.

- **C1:** IR ordering must preserve SSA dominance; block boundaries and invalid nodes have explicit conventions. Integer/floating interpretation and operand sizes matter to reproducing guest instruction semantics. The IR documentation explicitly does not promise a hostile-code sandbox.
- **C3:** Compact node offsets allow IR storage to move without pointer fixups. Explicit CPUID/syscall operations enable specialization, while separation of decoding, IR optimization, and backends gives the performance work a tractable structure.

The [FEXCore IR design](https://github.com/FEX-Emu/FEX/blob/main/FEXCore/docs/IR.md) explains representation, allocation, and traversal, including traps for readers modifying IR. Treat this as a guide to the relevant subsystem rather than a compatibility guarantee for all x86 software.

## Coverage and search notes

Discovery used more than six distinct live-web formulations, including tracing/meta-tracing; portable JIT libraries and register allocation; JVM/CLR and reusable runtime components; Ruby/BEAM integration; numerical Python/Julia specialization; WebAssembly/Go compiler engines; dynamic binary translation; Smalltalk/Cog; and broad deoptimization/testing queries. Searches surfaced established projects and smaller implementations such as MIR, SLJIT, `dstogov/ir`, yk, and Deegen. Later broad passes added relatively little to the selected architectural coverage and increasingly returned immature candidates, adjacent optimization systems, or duplicate families. This is diminishing return for this selection, not a claim that the ecosystem has no other substantive projects.

Each retained canonical repository URL was opened, and at least one separate implementation or documentation source was opened and read. Re-reading a README through a raw URL was not counted as independent evidence. No repository was cloned, built, or benchmarked, and stars were not used as quality evidence. The specific study recommendations and criterion assignments are the researcher's inferences from the cited mechanisms; performance ratios have deliberately not been reproduced.

The selection favors inspectable runtime/compiler architecture over exhaustive language coverage. It does not separately list downstream LLVM forks, Cranelift outside its current Wasmtime monorepo, Ruby's individual JITs, or OpenJ9's OMR-derived components. AI workflow “JIT” tools and mathematical dynamic-optimization packages were excluded as category mismatches. Domain-specific SQL, regular-expression, tensor/GPU, and eBPF JITs were not systematically surveyed here. The inspected [OpenSmalltalk VM distribution](https://github.com/OpenSmalltalk/opensmalltalk-vm) was not retained: it has substantive generated VM code and platform support, but its editable Smalltalk core lives in a separate source system, making it a less direct GitHub study entry for this report. This is a selection decision, not a judgment that generated VM code is a mere wrapper.

Official mirrors are flagged for V8, LuaJIT, and QEMU. Experimental limitations are retained for yk, Deegen, and CPython's JIT, and `dstogov/ir`'s unstable integration surface is explicit. Some official design pages lag source changes; those discrepancies are called out rather than silently treating historical documents as complete descriptions of today's default runtime. The evidence supports study value, not a security audit, benchmark ranking, or blanket maintenance endorsement.
