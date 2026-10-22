# Compiler infrastructures and optimization frameworks

Research date: **2026-10-09**

This report selects **25 GitHub repositories** for studying reusable intermediate representations, compiler passes, code generation, scheduling, equality saturation, and optimization correctness. It includes general-purpose infrastructure, domain-specific compiler frameworks, and supporting verification engines. Large monorepos count once, with the relevant subsystem identified. Selection reflects the engineering evidence below, not a claim that every component is exemplary or suitable for immediate adoption.

**Criteria legend**

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or consequential failure modes.
- **C2 — Reusable abstractions:** substantial representations, interfaces, or algorithms supporting multiple consumers and use cases.
- **C3 — Performance with structure:** concrete execution or compilation costs addressed through understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or complexity management; age alone does not qualify.

Criteria assignments are grounded engineering judgments based on the linked primary material. Maintenance is not assumed from repository visibility, stars, or a recent crawl. Explicit archival, mirror, and successor information appears where relevant.

## General-purpose IRs, optimizers, and native backends

### 1. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language / role:** Primarily C++; LLVM optimizer and code generator, MLIR infrastructure, and related toolchain components. LLVM, MLIR, and Polly are counted together here.

Study how transformations at different granularities share analyses without accidentally reusing stale results. **C1:** LLVM's analysis managers explicitly distinguish preserved, invalidated, cached, and immutable outer analyses; the documentation explains how unrestricted access could introduce invalid results or future concurrency nondeterminism. **C2:** module, call-graph SCC, function, and loop pass managers compose through adaptors, while extension callbacks let frontends and backends customize pipelines. **C3:** grouping passes improves locality, and restricting nested access avoids quadratic analysis work. Start with the [new pass manager design and usage](https://llvm.org/docs/NewPassManager.html), then compare MLIR's operation-scoped passes and scheduling constraints in its [pass infrastructure documentation](https://mlir.llvm.org/docs/PassManagement/).

### 2. [gcc-mirror/gcc](https://github.com/gcc-mirror/gcc)

**Language / role:** Primarily C and C++; GCC's shared optimization and target infrastructure. **Unofficial GitHub mirror:** the repository identifies its upstream as `gcc.gnu.org`, and upstream explicitly identifies this mirror as unofficial in its [repository-policy commit](https://gcc.gnu.org/pipermail/gcc-cvs/2023-November/392054.html). Development and contribution procedures belong to the upstream project.

Study a compiler whose pass framework explicitly records the IR form and auxiliary structures required by each transformation. **C1:** the pass manager validates constraints and orders transformations, but its documentation candidly says it does not automatically regenerate analyses or lower IR to satisfy the next pass. This exposes the correctness responsibilities left to pipeline authors. **C2:** pass descriptors centralize execution and bookkeeping across a multi-language compiler collection. The [pass manager internals](https://gcc.gnu.org/onlinedocs/gccint/Pass-manager.html) identify `passes.cc`, `tree-pass.h`, and `passes.def`; the [upstream Git guide](https://gcc.gnu.org/git.html) explains source history, generated-file handling, and why timestamps complicate reproducible developer workflows.

### 3. [bytecodealliance/wasmtime](https://github.com/bytecodealliance/wasmtime)

**Language / role:** Rust; the relevant subsystem is **Cranelift**, an independently usable native-code compiler backend inside the Wasmtime monorepo.

Study a function-oriented compiler with explicit block arguments and a small collection of libraries around code generation. **C1:** its IR specifies SSA dominance, typed basic-block parameters, explicit terminators, traps, and floating-point behavior. **C2:** separate codegen, frontend, module, object, and JIT crates allow consumers to construct IR, compile related functions, and choose file or memory output. Begin with the [Cranelift component map](https://github.com/bytecodealliance/wasmtime/blob/main/cranelift/docs/index.md) and the [IR reference](https://raw.githubusercontent.com/bytecodealliance/wasmtime/main/cranelift/docs/ir.md). The latter explicitly warns that portions may lag implementation; use its linked instruction API when relying on precise current instruction support.

### 4. [libfirm/libfirm](https://github.com/libfirm/libfirm)

**Language / role:** C; graph-based optimizing compiler middle end and backend.

Study an alternative to instruction-list IRs: Firm represents programs with type graphs, per-function graphs, and a symbol table, retaining SSA as a central organizing principle. **C2:** the representation is independent of the source language and target and supports reusable analysis, transformation, and code generation. **C1:** the documentation distinguishes freely chosen unknown values from undefined behavior, showing when apparently simple substitutions become invalid because multiple uses preserve relationships. Read the [IR introduction](https://libfirm.github.io/Introduction.html) and [unknown/undefined-value semantics](https://libfirm.github.io/Unknown_and_Undefined.html). The latter also documents known invalid-graph problems when `Bad` is used for undefined behavior. That caveat makes this a useful correctness study, not a blanket endorsement of every transformation.

### 5. [vnmakarov/mir](https://github.com/vnmakarov/mir)

**Language / role:** C; lightweight MIR-based interpreter and JIT infrastructure, with a C frontend.

Study the boundary between an embeddable compiler API, target calling conventions, and runtime ownership. **C2:** MIR exposes contexts, modules, functions, imports/exports, prototypes, and textual/binary representations through a coherent C API. **C1:** context separation defines when independent threads may operate without synchronization; the type system also makes target-dependent pointer sizes, long-double representations, and aggregate argument ABI cases explicit. The [MIR specification and API](https://github.com/vnmakarov/mir/blob/master/MIR.md) is a substantive entry point into these contracts. This is especially useful for engineers who want to understand a smaller native backend rather than begin inside an industrial-scale toolchain. Cross-target numerical equivalence should not be inferred for the documented target-dependent types.

### 6. [AnyDSL/thorin](https://github.com/AnyDSL/thorin)

**Language / role:** C++; higher-order intermediate representation used by AnyDSL.

Study how continuation-passing style represents control flow within a graph of values, and how a compiler API constructs SSA on behalf of frontends. **C2:** a common `Def` hierarchy covers primitive operations, lambdas, and parameters; `World` owns the representation, while cleanup removes dead definitions and unused types. **C1:** the programming guide explains that changing lambda parameters after construction can break existing users, and that jumps assert type agreement with their destination. These are concrete examples of mutation rules needed to preserve a graph IR. Start with the [Thorin overview](https://anydsl.github.io/Thorin.html) and [programming guide](https://anydsl.github.io/Programming-Guide.html). This entry concerns the substantive Thorin implementation, not the separate AnyDSL build-script repository or newer related IR projects.

## Runtime compilation and bytecode transformation

### 7. [eclipse-omr/omr](https://github.com/eclipse-omr/omr)

**Language / role:** C and C++; reusable runtime components, especially `compiler` and `jitbuilder`.

Study how compiler technology can be consumed by different language runtimes, and how a JIT exposes enough control to diagnose optimization failures. **C2:** OMR separates compiler, high-level JIT construction, platform, threading, and testing components; the repository identifies OpenJ9 and other language-runtime consumers. **C3:** its compiler documentation distinguishes recompilation of increasingly hot methods from a fixed optimization level, explicitly balancing compilation expense against execution benefit. The [compiler problem-determination guide](https://github.com/eclipse-omr/omr/blob/master/doc/compiler/ProblemDetermination.md) explains how optimization levels and compilation logs help isolate faulty phases. Read it as an architectural tour of adaptive compilation and observability, not merely as troubleshooting instructions.

### 8. [oracle/graal](https://github.com/oracle/graal)

**Language / role:** Primarily Java; relevant components are the Graal compiler and Truffle language-implementation framework, counted together.

Study compiler/runtime cooperation where interpreter structure, aliasing, register allocation, and calling conventions all affect generated code. **C2:** Truffle and the Graal compiler provide infrastructure for language implementations rather than a single source-language frontend. **C3:** the [one-compilation-per-bytecode-handler design](https://github.com/oracle/graal/blob/master/truffle/docs/OneCompilationPerBytecodeHandler.md) explains why one large dispatch loop causes register pressure, while ordinary outlining loses opportunities to retain interpreter state in registers. Its solution combines parameter expansion, specialized calling conventions, and tail-call threading. **C1:** parameter expansion must preserve aliasing relationships between interpreter data structures. This narrow design document is a more informative entry point than broad native-image performance claims.

### 9. [soot-oss/soot](https://github.com/soot-oss/soot)

**Language / role:** Java; Java bytecode analysis, optimization, and instrumentation framework.

Study the interaction between multiple IRs and reusable dataflow solvers. **C2:** Baf, Jimple, Shimple, and Grimp expose different levels of bytecode structure; analysis clients specialize common forward/backward flow machinery. **C1:** the [FlowAnalysis implementation](https://raw.githubusercontent.com/soot-oss/soot/develop/src/main/java/soot/toolkits/scalar/FlowAnalysis.java) handles strongly connected components and backward analyses of methods with potentially infinite loops and no return. These cases challenge naive worklist initialization. The [phase and option reference](https://soot-oss.github.io/soot/docs/4.5.0/options/soot_options.html) shows how analyses and transformations are assembled; it is explicitly versioned documentation. **Successor caveat:** the repository recommends SootUp for new analysis projects, while stating that classic Soot remains maintained for capabilities including instrumentation and robust Android support that the successor does not yet fully replace.

### 10. [WebAssembly/binaryen](https://github.com/WebAssembly/binaryen)

**Language / role:** C++; WebAssembly compiler and optimization library, including `wasm-opt`.

Study why a compiler's internal representation may deliberately differ from its serialization format: Binaryen uses structured tree IR, with additional machinery for stack-oriented code. **C2:** a pass registry and runner support reusable transformations behind both tools and embedding APIs. **C1:** optimization options encode semantic assumptions about trapping, imported memory, escaping references, and floating-point algebra. **C3:** inlining limits address code growth and startup costs, rather than optimizing call overhead in isolation. The [pass interface and option implementation](https://raw.githubusercontent.com/WebAssembly/binaryen/main/src/pass.h) explains these choices with examples, including why trap assumptions must not erase opaque imported calls. Pair it with the repository's IR and design discussion.

### 11. [KhronosGroup/SPIRV-Tools](https://github.com/KhronosGroup/SPIRV-Tools)

**Language / role:** C++; SPIR-V validation, optimization, assembly, reduction, and related library infrastructure.

Study the maintenance of derived facts while an optimizer mutates a binary-oriented IR. **C1:** `IRContext` explicitly requires changes to preserve or invalidate def-use, control-flow, dominance, type, and other analyses; deletion documents pointer/iterator validity, and ID allocation handles overflow. **C2:** the shared context and managers support many passes, while the repository separates core tooling from the optimizer library. The [IRContext implementation](https://raw.githubusercontent.com/KhronosGroup/SPIRV-Tools/main/source/opt/ir_context.h) is an unusually direct entry point into these invariants. The repository also describes validator and metamorphic-fuzzing tools, but explicitly calls validation incomplete. Its current release guidance points to tested Vulkan SDK releases and says GitHub releases are deprecated; those two facts should not be confused with project abandonment.

## Extensible dialects and domain-specific compiler stacks

### 12. [xdslproject/xdsl](https://github.com/xdslproject/xdsl)

**Language / role:** Python; extensible SSA compiler toolkit interoperating with MLIR.

Study a compiler framework whose IR construction, rewriting, and dialect definitions are accessible directly in Python. **C2:** shared regions, blocks, and SSA values support generic analyses and transformations across custom IRs. **C1:** the [pattern rewriter API and embedded source](https://docs.xdsl.dev/reference/pattern_rewriter/) tracks operation replacement/removal, updates uses, notifies listeners, and distinguishes safe erasure from replacing remaining uses with erased values. This is valuable for understanding why a rewrite API must do more than edit lists of nodes. The repository's compatibility note says validation is against a specific MLIR version, not arbitrary versions; consult the version actually checked out rather than assuming interchange is universally stable.

### 13. [llvm/circt](https://github.com/llvm/circt)

**Language / role:** C++ and MLIR/TableGen definitions; compiler infrastructure for hardware representations and transformations. This is a separate repository from `llvm/llvm-project`.

Study what changes when compiler IR describes communicating hardware processes rather than sequential machine instructions. **C2:** CIRCT builds reusable hardware dialects, transformations, and tools on MLIR; its stated motivation is a common library-based platform for hardware tooling. **C1:** the [Handshake dialect rationale and operation definitions](https://circt.llvm.org/docs/Dialects/Handshake/RationaleHandshake/) describe independent processes communicating through FIFO channels, with explicit forks, merges, buffers, and control tokens. Correctness therefore includes synchronization and stream behavior, not just arithmetic equivalence. This document is a good entry point for comparing software SSA values with hardware dataflow channels. The repository describes the overall effort as experimental, so maturity should be evaluated per dialect and tool.

### 14. [apache/tvm](https://github.com/apache/tvm)

**Language / role:** C++ and Python; machine-learning compiler framework with graph-level Relax and tensor-level IR/scheduling infrastructure.

Study how one module can retain both graph and loop-level information while transformations progressively lower it. **C2:** `IRModule`, high-level functions, low-level tensor functions, runtime modules, and target interfaces establish explicit boundaries between optimization, code generation, and deployment. **C3:** tensor schedules control tiling, locality, threading, and vector/tensor operations, while lower-level work such as register allocation is delegated to downstream compilers. **C1:** GPU thread bindings are required for valid generated programs, not merely optional tuning. Start with the [architecture guide](https://tvm.apache.org/docs/arch/index.html) and [TensorIR documentation](https://tvm.apache.org/docs/deep_dive/tensor_ir/index.html). The current documentation splits core tensor IR and schedulable infrastructure into `tirx` and `s_tir`; older tutorials may use previous organization.

### 15. [iree-org/iree](https://github.com/iree-org/iree)

**Language / role:** C++ compiler and C runtime; MLIR-based compilation and execution across heterogeneous devices.

Study how a compiler makes asynchronous execution and buffer lifetimes explicit before handing work to a runtime. **C2:** Flow, Stream, and HAL divide dispatch formation, scheduling/resource representation, and hardware execution responsibilities. **C1:** Stream timepoints define when produced data becomes available; using resources before their timepoints is undefined behavior. **C3:** explicit lifetime and scheduling information enables concurrent execution and resource aliasing without losing dependency information. The [Stream dialect design](https://iree.dev/reference/mlir-dialects/Stream/) describes tensor-to-resource lowering, target affinity, resource sizes, and lifetime classes. It provides a concrete bridge between compiler transformations and runtime memory planning, beyond simply listing accelerator backends.

### 16. [openxla/xla](https://github.com/openxla/xla)

**Language / role:** Primarily C++; optimizing compiler for tensor programs from multiple machine-learning frameworks.

Study how graph semantics, physical tensor layout, distributed execution, and device code generation interact in a single pipeline. **C2:** XLA accepts a shared high-level operation vocabulary from multiple frameworks and lowers toward multiple backends. **C3:** the [GPU architecture guide](https://openxla.org/xla/gpu_architecture) explains HLO transformations, SPMD partitioning, layout assignment, and the division between native and Triton-based emitters. In particular, logical shape is separated from physical layout, and partitioning aims to overlap communication with computation. These are concrete, reusable abstractions for optimizing data movement. The guide includes older example APIs; use it for architecture rather than assuming every sample command matches a current frontend release.

### 17. [halide/Halide](https://github.com/halide/Halide)

**Language / role:** C++ with Python bindings; compiler and embedded language for image and array pipelines.

Study the separation of algorithm definitions from scheduling decisions, especially the distinction between when storage is allocated and when a producer is computed. **C2:** `Func`, variables, and schedules represent pipelines independently of particular loop nests and target code. **C3:** the [multistage scheduling source tutorial](https://raw.githubusercontent.com/halide/Halide/main/tutorial/lesson_08_scheduling_2.cpp) contrasts inlining, root computation, and computation at a consumer loop level in terms of repeated work, temporary storage, and locality. It also shows how separate storage/computation placement enables reuse across scanlines. This is substantive API and generated-code material inside a full compiler repository, not a standalone tutorial project. The repository confirms both ahead-of-time and in-process JIT compilation roles.

### 18. [spcl/dace](https://github.com/spcl/dace)

**Language / role:** Primarily Python; data-centric compiler framework targeting CPUs, GPUs, and FPGAs.

Study optimization through explicit data movement rather than only expression trees or instruction order. **C2:** Stateful DataFlow multiGraphs separate source programs from reusable, extensible graph transformations. **C1:** transformations first match a pattern and then check applicability; their contract specifies whether changed edges carry suitable memlet annotations or require propagation. **C3:** device-copy and double-buffering transformations expose storage placement and transfer behavior as compiler operations. The [dataflow transformation API](https://spcldace.readthedocs.io/en/latest/source/dace.transformation.dataflow.html) concretely documents `expressions`, `can_be_applied`, `apply`, and `annotates_memlets`, including the creation of arrays and copies around a nested graph. This is a useful contrast to compilers where data movement remains implicit until late lowering.

### 19. [Tiramisu-Compiler/tiramisu](https://github.com/Tiramisu-Compiler/tiramisu)

**Language / role:** Primarily C++; polyhedral framework for scheduling data-parallel computations.

Study a staged representation that separates algorithm meaning, execution order/processor mapping, storage mapping, and communication. **C2:** its C++ API expresses computations and schedules across several numerical domains, rather than hard-coding one kernel family. **C3:** the [authors' architecture paper, especially sections IV–V](https://arxiv.org/pdf/1804.10694), explains affine-map composition for loop transformations, separate data-layout relations, and explicit communication/synchronization lowering. This structure makes tiling, GPU placement, and distributed communication understandable as transformations of different layers. The paper documents the original architecture, while the repository verifies the continuing source location and implementation scope; it is not evidence that all historical backend configurations work with today's dependencies. No comparative speedup claim is needed for selection.

## Equality saturation and programmable rewriting

### 20. [egraphs-good/egg](https://github.com/egraphs-good/egg)

**Language / role:** Rust; generic e-graph and equality-saturation library for building optimizers.

Study a representation that retains equivalent alternatives instead of committing to one rewrite order. **C2:** `EGraph` and `EClass` are generic over a user-defined language and associated analysis data, allowing the same engine to support different expression systems. **C1:** the [EGraph API](https://docs.rs/egg/latest/egg/struct.EGraph.html) makes the clean/rebuild protocol explicit: mutations dirty the graph, reading requires restored invariants, and deserialization requires rebuilding. That protocol is an instructive boundary between cheap updates and correct queries. The repository's tests span propositional logic, arithmetic, and lambda-calculus partial evaluation, providing concrete examples of reuse. Users still must justify their rewrite rules for their own numerical and language semantics.

### 21. [egraphs-good/egglog](https://github.com/egraphs-good/egglog)

**Language / role:** Rust engine with a declarative language; combines equality saturation and Datalog-style reasoning.

Study how analyses and rewrites can participate in the same rule-driven optimizer without forcing one global saturation policy. **C2:** user-defined expression datatypes, relations, functions with merge behavior, and reusable rulesets represent both optimization knowledge and analysis facts. **C3:** the [scheduling guide](https://egraphs-good.github.io/egglog-tutorial/04-scheduling.html) shows why separating analysis rules from expression-expanding optimization rules helps control work; schedules combine bounded execution and saturation. Start with the [equality-saturation introduction](https://egraphs-good.github.io/egglog-tutorial/01-basics.html) for the rule semantics. This is a separate engine from `egg`, not a renamed fork counted twice. The current repository documents parallel execution as relatively new, so no mature-scaling claim is inferred from the presence of a thread-count flag.

### 22. [jonathanvdc/foresight](https://github.com/jonathanvdc/foresight)

**Language / role:** Scala; equality-saturation library with programmable strategies and mutable/immutable graph implementations.

Study the saturation loop itself as a reusable compiler abstraction. **C2:** strategies can sequence, repeat, bound, instrument, and combine rewriting with analyses, rather than requiring consumers to edit the engine's main loop. **C1:** deferred rewriting separates parallel matching from graph mutation and metadata updates. **C3:** matching produces commands that can be simplified, deduplicated, and applied in batches; the two graph implementations offer different concurrency and sequential-latency tradeoffs. The [author's technical design account](https://jonathanvdc.github.io/compiler-work/foresight/) explains these boundaries and links the 2026 paper. This is a newer research library, included for concrete abstraction and concurrency design; no C4 or production-maturity claim is made.

## Optimization validation and verified compiler foundations

### 23. [AliveToolkit/alive2](https://github.com/AliveToolkit/alive2)

**Language / role:** C++; LLVM transformation validation, symbolic execution, and SMT-based refinement checking.

Study the machinery required to determine whether an optimization preserves the behavior allowed by its source IR. **C1:** the [authors' implementation paper](https://web.ist.utl.pt/nuno.lopes/pubs/alive2-pldi21.pdf) explains undefined behavior and memory encodings, including block identities, offsets, allocation properties, and poison. **C2:** the repository separates Alive2 IR, symbolic execution, LLVM conversion, refinement checking, and SMT abstraction, supporting standalone validation, compiler integration, and interpretation. Resource-bounded loop handling is an explicit limitation: a successful bounded check is not an unrestricted proof for arbitrary executions. The current README additionally warns that interprocedural transformations are unsupported and can produce spurious counterexamples. The paper is historical implementation evidence, not a claim that every feature restriction it describes remains current.

### 24. [google/souper](https://github.com/google/souper)

**Language / role:** C++; LLVM-oriented synthesizing superoptimizer. **Historical / archived:** GitHub reports archival on **2025-10-30** and read-only status.

Study the separation between extracting optimization opportunities and verifying candidate replacements. **C1:** the [Inst representation reference](https://github.com/google/souper/blob/main/docs/InstRef.md) encodes bit-vector operations, undefined signed overflow, and path conditions derived from control flow, including conditions attached to incoming block edges. **C2:** a common textual representation can be produced by the instruction harvester or written by hand, allowing synthesis and checking to operate on the same candidate language. The repository describes SMT-assisted identification of missing peephole optimizations and test infrastructure. Its archival status makes it a historical design reference; it should not be treated as a maintained integration for current LLVM without further work.

### 25. [AbsInt/CompCert](https://github.com/AbsInt/CompCert)

**Language / role:** Rocq/Coq and OCaml; formally verified C compiler and reusable semantics/proof infrastructure.

Study how executable optimization algorithms are accompanied by explicit semantic obligations. **C1:** the [Kildall module](https://compcert.org/doc/html/compcert.backend.Kildall.html) specifies dataflow inequations and states the theorem required of a returned solution. **C2:** its generic forward/backward solvers work over semilattices; a separate extended-basic-block solver trades precision for simpler or cheaper joins. **C4:** the [changelog](https://raw.githubusercontent.com/AbsInt/CompCert/master/Changelog.md) records years of compiler/proof-system compatibility and correctness work, from 2018 Coq support and conservative value analysis to 2026 alignment, ABI, memory-semantics, Rocq, and OCaml changes. This is evidence of continuing complexity management, not just age. The repository explicitly restricts this distribution to noncommercial uses; public GitHub availability does not imply an unrestricted open-source license.

## Coverage, search process, and limitations

Discovery used more than six distinct formulations, including general compiler backends and IR libraries; Python/MLIR extensibility; JVM and runtime JIT components; WebAssembly and SPIR-V optimization; polyhedral and data-centric scheduling; tensor compiler architecture; CPS/higher-order representations; equality saturation; verified compilation and translation validation; and small alternative native backends. Follow-up searches targeted pass managers, rewrite APIs, scheduling designs, transformation preconditions, and source-level correctness contracts. Late alternative-backend and saturation searches mostly returned already represented approaches, small demonstrations, or uncertain mirrors, but did add Foresight's distinct Scala and deferred-update design.

Every retained repository's GitHub page was opened, and each entry also has an independently read primary documentation, implementation, or author-paper source. Failed documentation URLs were replaced with working official sources or source files. The inspected material was treated as evidence only. No repositories were cloned, candidate code executed, dependencies installed, or external services modified.

The selection deliberately excludes awesome-lists, generated bindings without substantive compiler logic, tutorial-only optimizers such as optir, and ordinary language frontends whose reusable infrastructure was not the focus of this search. QBE appeared through third-party GitHub locations, but this research did not establish an official substantive GitHub mirror, so it is not included. LLVM subprojects are not separate entries, and Cranelift is attributed to Wasmtime rather than an obsolete standalone location. Related frontends, runtime-only repositories, and alternative experimental implementations are not counted simply to expand the list.

This is a source-guided selection, not a benchmark or comprehensive maintenance audit. Architectural papers describe the implementations they studied; moving documentation and default branches can differ from released versions. C4 is awarded only where sustained compatibility and correctness work was actually inspected. Most entries qualify through C1–C3 without an unsupported maturity claim. The report emphasizes C/C++, Rust, Python, Java, Scala, and proof-oriented infrastructure; it does not claim complete coverage of every compiler ecosystem or hardware backend.
