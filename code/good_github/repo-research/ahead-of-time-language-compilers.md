# Ahead-of-time language compilers

Research date: **2026-10-09**.

This selection covers 25 substantive repositories that compile a programming language to native executables, native libraries, or native extension modules before execution. It includes compilers that emit C as an intermediate step, verified compilers, embedded and parallel-language compilers, and AOT subsystems inside larger runtimes. A project can also provide an interpreter or JIT; the entry identifies its relevant AOT path. Monorepos count once. GitHub repository locations and the linked implementation material were opened during research.

The criteria identify worthwhile engineering study, rather than certify that every component is exemplary:

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable representations, interfaces, or components serving multiple use cases.
- **C3 — Performance:** real execution, memory, code-size, or compilation-cost constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by evidence of compatibility work, regression testing, or complexity management. Repository age alone does not qualify.

## Mainstream native toolchains

### 1. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language/role:** Primarily C++; the relevant subsystems are Clang's language frontend and LLVM's optimizer and machine-code backends. This monorepo is counted once.

Study how a production language frontend shares infrastructure with tooling, and why apparently simple optimizer rewrites require precise semantics.

- **C1:** LLVM distinguishes immediate undefined behavior, deferred poison, and `undef`. Its examples explain why speculating division can introduce invalid behavior, why hardware shift semantics differ, and why replacing a `select` with a Boolean operation can wrongly propagate poison. The [undefined-behavior manual](https://llvm.org/docs/UndefinedBehavior.html) is a substantive introduction to optimization correctness.
- **C2:** Clang separates diagnostic IDs, arguments, source locations, and presentation, and supports partially formed syntax during error recovery. These are reusable frontend services rather than functionality tied to one compilation command. Start with the [Clang internals manual](https://clang.llvm.org/docs/InternalsManual.html).

### 2. [rust-lang/rust](https://github.com/rust-lang/rust)

**Language/role:** Primarily Rust; `rustc` compiles Rust through several intermediate representations to native code.

Study how ownership checks, generic programming, incremental computation, and machine-code generation coexist without requiring one representation to serve every purpose.

- **C1:** MIR supports borrow checking, initialization analysis, and constant evaluation. Its control-flow-oriented representation makes lifetime and initialization obligations explicit before machine lowering.
- **C2:** HIR, THIR, MIR, and backend representations divide semantic responsibilities; the query system provides common dependency tracking and cached computation across compiler services.
- **C3:** MIR optimization can happen before monomorphization, sharing work across later generic instantiations. The architecture also explicitly addresses compilation cost through incremental queries and memory-management choices. These stages and their purposes are documented in the [compiler overview](https://rustc-dev-guide.rust-lang.org/overview.html).

### 3. [gcc-mirror/gcc](https://github.com/gcc-mirror/gcc)

**Language/role:** Primarily C and C++; the GNU Compiler Collection's native language frontends, shared optimization pipeline, and target backends. **Unofficial GitHub mirror:** upstream explicitly identifies this repository in its [mirror-policy commit](https://gcc.gnu.org/pipermail/gcc-cvs/2023-November/392054.html). It supplies inspectable GCC source, but GitHub is not the upstream contribution venue.

Study how several language frontends share native-code compilation without requiring every frontend to implement the same lowering machinery.

- **C1:** Language-specific lowering callbacks must make progress toward valid GIMPLE, distinguish completed transformations from expressions needing another pass, and propagate semantic errors. These are explicit correctness contracts in the [gimplification design](https://gcc.gnu.org/onlinedocs/gccint/Gimplification-pass.html), with implementation entry points in `gimplify.cc`.
- **C2:** Frontends can emit GIMPLE directly or use GENERIC plus extensions and a shared lowering implementation. The [pass manager](https://gcc.gnu.org/onlinedocs/gccint/Pass-manager.html) centralizes ordering and bookkeeping through pass descriptors while exposing required representations and auxiliary analyses. It validates prerequisites but does not automatically reconstruct missing analyses, leaving a consequential boundary between framework services and pass-author responsibilities.

### 4. [golang/go](https://github.com/golang/go)

**Language/role:** Primarily Go; the native compiler is `cmd/compile`. **Official GitHub mirror** of the Go repository hosted at `go.googlesource.com`.

Study a relatively direct pipeline that connects language semantics, garbage-collector requirements, and architecture-specific instruction selection.

- **C1:** The walk phase preserves evaluation order while lowering constructs. Later code generation must provide correct live-pointer information at GC safe points, linking frontend transformations to runtime correctness.
- **C2:** Unified IR handles import/export and generic instantiation, while the SSA representation supports shared optimizations before target-specific lowering.
- **C3:** Inlining, devirtualization, escape analysis, generic SSA passes, register allocation, and architecture lowering occupy identifiable phases. The [compiler's internal README](https://go.dev/src/cmd/compile/README) explains both the pipeline and its source-package boundaries.

### 5. [swiftlang/swift](https://github.com/swiftlang/swift)

**Language/role:** C++ and Swift; Swift frontend, SIL optimizer, and LLVM-based native compilation.

Study an intermediate representation designed to retain information that would be lost by immediately lowering a high-level language into LLVM IR.

- **C1:** Optimizer analyses have explicit invalidation requirements. For example, cached dominator information becomes invalid when a transformation changes branches; the pass infrastructure coordinates these dependencies.
- **C2:** Function and module passes use common analysis interfaces and invalidation machinery, allowing new optimizations to reuse compiler knowledge.
- **C3:** SIL exposes reference-counting operations, dispatch, arrays, and generic specialization to optimizers before low-level lowering. The [optimizer design document](https://github.com/swiftlang/swift/blob/main/docs/OptimizerDesign.md) explains this information-preservation argument and the pass architecture. Sections explicitly labeled as future work should be read as proposals, not implemented guarantees.

### 6. [ldc-developers/ldc](https://github.com/ldc-developers/ldc)

**Language/role:** D and C++; an LLVM-based native D compiler that reuses the DMD frontend.

Study the boundary between a shared language frontend and target-dependent ABI rules, including cases where LLVM's natural aggregate representation is insufficient.

- **C1:** Argument and return-value rewriting must preserve hidden structure-return parameters, by-value rules, variadic representations, and agreement with the D runtime. These obligations are explicit in the [target ABI interface](https://github.com/ldc-developers/ldc/blob/master/gen/abi/abi.h).
- **C2:** `TargetABI` and `ABIRewrite` provide common interfaces for different calling conventions and target-specific coercions.
- **C4:** The [changelog](https://github.com/ldc-developers/ldc/blob/master/CHANGELOG.md) connects 2020-era constructor-order and testsuite work with 2026 frontend/runtime synchronization and LLVM compatibility changes. It records breaking ABI changes and fixes, providing evidence of sustained compatibility management rather than merely longevity.

## Alternative systems languages and embedded compilation

### 7. [nim-lang/Nim](https://github.com/nim-lang/Nim)

**Language/role:** Primarily Nim; native compilation commonly proceeds through generated C and an external C compiler/linker.

Study self-hosting, compile-time execution, and the interaction between high-level closures and an existing systems-language backend.

- **C1:** Semantic checking changes AST shape, while potentially cyclic types and symbols have separate representations. Closure lowering must preserve nested captured environments and the distinction between procedure pointers and GC-managed references.
- **C2:** The compiler shares AST infrastructure among semantic passes, generic instantiation, compile-time evaluation, rendering, and C generation. Separate modules coordinate the external compiler and linker.
- **C3:** The closure design makes the cost of ordinary-procedure/closure interoperability explicit: a procedure/environment pair supports both, with a conditional call path. The [compiler internals guide](https://nim-lang.org/docs/intern.html) maps modules and explains these tradeoffs. It also candidly documents historical implementation baggage; this is a study opportunity, not a claim of uniform stylistic quality.

### 8. [crystal-lang/crystal](https://github.com/crystal-lang/crystal)

**Language/role:** Primarily Crystal; self-hosted, statically checked native compilation using LLVM.

Study the sequencing constraints in a compiler that combines extensive type inference, macros, object-oriented declarations, and native data layouts.

- **C1:** Semantic passes establish declarations, synthesize constructors, validate abstract methods and initializers, analyze the program, and finally reject recursively embedded structs that cannot be represented. Non-nilable class variables without initializers receive explicit checks.
- **C2:** The same semantic driver exposes a partial top-level analysis for documentation and hierarchy tools, distinct from full program inference and cleanup. This is a concrete reuse boundary between compilation and developer tooling. The ordered passes and their rationale are directly visible in [semantic.cr](https://github.com/crystal-lang/crystal/blob/master/src/compiler/crystal/semantic.cr).

### 9. [ponylang/ponyc](https://github.com/ponylang/ponyc)

**Language/role:** C/C++ compiler with Pony libraries; native compilation for an actor language with reference capabilities.

Study how a language-level concurrency discipline becomes a sequence of compiler checks and lowering passes.

- **C1:** Reference capabilities distinguish isolated ownership, shared immutable values, and actor-local mutable access. Their aliasing rules constrain which references may cross actor boundaries; the [capability tutorial](https://tutorial.ponylang.io/reference-capabilities/reference-capabilities.html) explains the safety obligations with concrete access combinations.
- **C2:** The [pass driver](https://github.com/ponylang/ponyc/blob/main/src/libponyc/pass/pass.c) organizes common AST traversal around named stages for scope, type aliases, traits, expressions, completeness, verification, reachability, and code generation. It includes failure propagation and optional tree checking, making it useful for studying how many analyses share traversal machinery.

The repository describes a pre-1.0 language with possible breaking changes; inclusion does not imply a stable language-compatibility contract.

### 10. [odin-lang/Odin](https://github.com/odin-lang/Odin)

**Language/role:** Primarily C++; Odin's native compiler and LLVM backend.

Study the distinction between a source-language value, its memory layout, and the representation a platform ABI requires at a call boundary.

- **C1:** The [LLVM ABI implementation](https://github.com/odin-lang/Odin/blob/master/src/llvm_abi.cpp) tracks direct, indirect, and ignored arguments, alignments, and coercion offsets. Its RISC-V aggregate example explains why flattening a padded structure can change field offsets and make a naive bitcast incorrect.
- **C3:** Odin's immutable parameter semantics let the compiler choose value passing or an immutable pointer. The [FAQ](https://odin-lang.org/docs/faq/) explains the performance motivation, while the ABI code shows how such choices become concrete calling-convention machinery. This is a useful connection between language design and backend freedom, without relying on benchmark claims.

### 11. [c3lang/c3c](https://github.com/c3lang/c3c)

**Language/role:** Primarily C; native C3 compiler with LLVM integration and C interoperability.

Study a smaller systems compiler where semantic state management and compilation scheduling are accessible in ordinary source files.

- **C1:** Expression resolution explicitly transitions through not-started, running, and completed states. Re-entering a running expression produces a recursive-resolution diagnostic and poisons the expression, avoiding uncontrolled recursion or falsely successful analysis. See [sema_expr.c](https://github.com/c3lang/c3c/blob/master/src/compiler/sema_expr.c).
- **C3:** The [compiler driver](https://github.com/c3lang/c3c/blob/master/src/compiler/compiler.c) creates per-output code-generation tasks, bounds worker count by available tasks and configuration, gathers object files, and then links. Separate timing points expose parse, semantic, IR, code-generation, and link costs. This makes the architecture for compilation throughput visible rather than presenting parallelism as an unexplained feature.

### 12. [tinygo-org/tinygo](https://github.com/tinygo-org/tinygo)

**Language/role:** Primarily Go with LLVM integration; Go compilation for microcontrollers, WebAssembly, and other small targets.

Study how a familiar frontend is adapted to environments where startup work, memory, and binary size are central constraints.

- **C1:** Lowering interfaces and goroutines must preserve their runtime semantics. The documented AVR backend also performs late corrections for distinct flash and RAM address spaces, a hardware correctness issue absent from conventional flat-address-space targets.
- **C3:** The pipeline interprets global initialization during compilation to reduce generated startup code, applies escape and string optimizations, and delays some interface lowering so optimization can still use higher-level information. The [compiler pipeline guide](https://tinygo.org/docs/concepts/compiler-internals/pipeline/) provides the stage map and implementation rationale.

This guide describes architecture, not a promise that every Go package or runtime feature works on every TinyGo target.

## Functional languages and verified compilation

### 13. [ocaml/ocaml](https://github.com/ocaml/ocaml)

**Language/role:** OCaml and C; the relevant AOT compiler is `ocamlopt`, alongside the bytecode compiler and runtime in the same repository.

Study how two execution backends share language lowering while native compilation carries additional optimization information across module boundaries.

- **C2:** Lambda IR removes high-level module and object constructs before backend divergence. Native and bytecode compilation share interface information, while native `.cmx` files carry optimization information. See the [compiler backend guide](https://ocaml.org/docs/compiler-backend).
- **C3:** Pattern matching becomes lower-level decision structures, and native compilation supports representation optimizations and cross-module inlining; the guide connects those decisions to the staged backend.
- **C4:** The [Changes file](https://github.com/ocaml/ocaml/blob/trunk/Changes) documents 2022 releases and later 5.x work with marked breaking changes, regression repairs, and tests. Examples include GADT/type-checking regressions, diagnostic stack overflows, and GC/domain fixes, demonstrating continued management of semantic and runtime complexity.

### 14. [ghc/ghc](https://github.com/ghc/ghc)

**Language/role:** Primarily Haskell with C runtime components; Glasgow Haskell Compiler. **Official substantive GitHub mirror**; development is hosted on GHC's GitLab.

Study how a compact, explicitly typed intermediate language supports aggressive optimization of a high-level lazy language.

- **C1:** [Core.hs](https://github.com/ghc/ghc/blob/master/compiler/GHC/Core.hs) explains invariants around explicit types/coercions and case alternatives. Recording a case expression's result type prevents existentially bound type variables from escaping scope; Core Lint checks relevant well-formedness conditions.
- **C2:** Core supplies a shared expression language, binder abstraction, constructors, and helper operations across compiler passes. The extensive implementation notes make those contracts unusually inspectable.
- **C3:** The [code-generator guide](https://downloads.haskell.org/ghc/latest/docs/users_guide/codegens.html) describes native assembly and LLVM paths and their compilation-cost tradeoffs. Both establish category fit beyond GHC's interactive execution facilities.

### 15. [MLton/mlton](https://github.com/MLton/mlton)

**Language/role:** Primarily Standard ML with runtime support in C; a whole-program native compiler for Standard ML.

Study an alternative to preserving modules, polymorphism, and closures deep into a general-purpose backend.

- **C2:** The [compiler overview](https://github.com/MLton/mlton/blob/master/doc/guide/src/CompilerOverview.adoc) maps distinct intermediate languages from CoreML through XML, SXML, SSA, RSSA, and machine representation. Translation passes and optimization passes are distinguished, with a central compilation functor controlling the pipeline.
- **C3:** Defunctorization, monomorphization, and closure conversion progressively remove high-level machinery before machine lowering. Together with the repository's documented unboxed/untagged representations and whole-program approach, this provides a concrete architecture for reducing abstraction costs. The engineering lesson is the interaction between specialization and representation, rather than a claim that whole-program compilation is always preferable.

### 16. [CakeML/cakeml](https://github.com/CakeML/cakeml)

**Language/role:** Standard ML/HOL4 proof development; a verified ML compiler with native machine-code backends and a bootstrapped compiler implementation.

Study compilation as a chain of semantic arguments, including the connection between a proved compiler function and an executable tool.

- **C1:** The [compiler overview](https://github.com/CakeML/cakeml/blob/master/compiler/README.md) connects parsing, frontend compilation, encoding, errors, and machine-code output with proof components. The repository's verification claim has a defined formal scope, rather than implying that every surrounding tool and hardware component is proved correct.
- **C2:** The [backend overview](https://github.com/CakeML/cakeml/blob/master/compiler/backend/README.md) explains successive languages and their transformations, making proof and optimization boundaries explicit.
- **C3:** Those stages include known-closure specialization, inlining, live-variable annotations, and splitting very large expressions to control allocator work. Correctness-oriented development still exposes practical code-quality and compiler-resource tradeoffs.

### 17. [AbsInt/CompCert](https://github.com/AbsInt/CompCert)

**Language/role:** Primarily Rocq/Coq with OCaml and supporting code; a formally verified optimizing C compiler targeting several native architectures.

Study how to assemble a compiler from individually justified transformations while keeping failed passes explicit.

- **C1:** The [compiler driver and composition proofs](https://github.com/AbsInt/CompCert/blob/master/driver/Compiler.v) import transformation correctness results and compose semantic preservation across C, Clight, Cminor, RTL, LTL, Mach, and assembly-level representations. Partial passes use an explicit result type. The guarantee must be interpreted within the formal semantics and toolchain trust boundary.
- **C2:** The same driver composes total and partial passes and exposes compilation from multiple intermediate-language entry points. This is a substantial abstraction for connecting independently specified transformations and their proofs.

**License distinction:** The repository is source-available under CompCert's stated noncommercial evaluation, research, education, and personal-use terms; commercial use requires the applicable separate license. Do not treat it as interchangeable with permissively licensed compiler infrastructure.

## Numerical, vector, and distributed-language compilers

### 18. [diku-dk/futhark](https://github.com/diku-dk/futhark)

**Language/role:** Primarily Haskell; an optimizing compiler for a functional array language, including a native CPU path through generated C and GPU-oriented backends.

Study how one language is progressively transformed into explicit parallel work, memory allocation, and imperative execution.

- **C1:** The development workflow type-checks intermediate programs after passes and can dump the failing representation, localizing broken transformation invariants. See [HACKING.md](https://github.com/diku-dk/futhark/blob/master/HACKING.md).
- **C2:** The architecture separates parametric core representations, optimization pipelines, memory-explicit forms, and extensible imperative code. Shared C generation supports backend variants.
- **C3:** Fusion, inlining, segmented parallel operations, and explicit allocation occupy named stages. The unusually informative [Futhark.hs architecture overview](https://github.com/diku-dk/futhark/blob/master/src/Futhark.hs) explains why those representations exist. Inclusion relies on its AOT native path; generated GPU kernels may also involve device compilation at runtime.

### 19. [ispc/ispc](https://github.com/ispc/ispc)

**Language/role:** Primarily C++; LLVM-based compiler for a C-like SPMD language that produces native vectorized code callable from host programs.

Study the semantic boundary between a single scalar value, per-lane values, and execution masks.

- **C1:** `uniform` and `varying` values have different assignment and control-flow rules. Divergent branches execute with masked side effects, while uniform assignments are not simply subject to the same lane mask. The language also specifies ordering and races within an execution gang.
- **C3:** Uniform control flow can avoid divergent execution and mask-handling work; the type distinction therefore carries optimization-relevant information into lowering. The [language and compiler manual](https://github.com/ispc/ispc/blob/main/docs/ispc.rst), especially its uniform-data and control-flow sections, explains both the correctness model and the resulting performance choices without requiring numerical speedup claims.

### 20. [lfortran/lfortran](https://github.com/lfortran/lfortran)

**Language/role:** Primarily C++; Fortran compiler with native object/executable output as well as interactive and JIT facilities.

Study a frontend designed around a reusable semantic representation rather than making compilation the only consumer of language analysis.

- **C1:** ASR represents semantically valid programs with resolved symbols and constrained node structure. The design describes validity checks and the obligations of transformations that produce ASR; these are engineering invariants, not a formal proof of full Fortran correctness.
- **C2:** AST and ASR are designed as independently usable modules, with conversions supporting parsing, semantic analysis, source regeneration, optimization, and code generation. The [design document](https://docs.lfortran.org/en/design/) explains the AST/ASR distinction and the path from ASR through LLVM to native output.

Language support is evolving. The presence of a native output path should not be read as complete support for every Fortran program or standard feature.

### 21. [chapel-lang/chapel](https://github.com/chapel-lang/chapel)

**Language/role:** C++ compiler, C runtime, and Chapel libraries; native compilation for parallel and distributed programs.

Study how a language's distributed-memory model is made concrete in pointers, assignments, runtime calls, and optimization decisions.

- **C1:** [insertWideReferences.cpp](https://github.com/chapel-lang/chapel/blob/main/compiler/passes/insertWideReferences.cpp) explains wide references carrying a locale identifier and a local pointer. The pass propagates possible remoteness through assignments and fields, repairs the AST, and handles local blocks with narrowed temporaries and runtime checks.
- **C3:** The same pass avoids unnecessary wide references and remote-access machinery where analysis permits. Its discussion of array-instance fields shows how representation decisions affect ordinary indexing performance.

The [compilation guide](https://github.com/chapel-lang/chapel/blob/main/doc/rst/usingchapel/compiling.rst) connects this compiler machinery to executable generation and compiler/runtime checking options.

## Python and managed-runtime AOT subsystems

### 22. [Nuitka/Nuitka](https://github.com/Nuitka/Nuitka)

**Language/role:** Primarily Python with C runtime/code-generation support; compiles Python through C and links with Python runtime support.

Study how static optimization operates when Python's dynamic object behavior and exception semantics must remain observable.

- **C1:** Shape information predicts operation results and whether operations raise exceptions. Specialized generated operations need less-specific fallbacks when the available knowledge is insufficient; this is a concrete correctness boundary for speculative simplification.
- **C2:** Tree construction, optimization, finalization, and code generation are separate stages, with node information feeding generated C snippets.
- **C3:** Type/value knowledge allows specialized operations while retaining generic behavior where required. The [developer manual](https://nuitka.net/doc/developer-manual.html) describes that architecture and also distinguishes work in progress from existing support. Compilation here does not mean that Python runtime semantics or runtime dependencies disappear.

### 23. [python/mypy](https://github.com/python/mypy)

**Language/role:** Primarily Python with a C runtime; the relevant subsystem is **mypyc**, which turns typed Python modules into native extension modules. The mypy monorepo is counted once.

Study how a static type checker can supply the frontend for compilation, and how restricted dynamic behavior makes efficient representations possible.

- **C1:** After typed IR construction, dedicated passes handle uninitialized values, exceptions, and explicit reference-count increments/decrements. These passes connect control flow to Python object ownership.
- **C2:** mypyc reuses mypy's analyzed AST and type information rather than implementing a separate language frontend.
- **C3:** Early binding, direct C calls, fixed extension-class fields, virtual tables, and unboxed primitives reduce dynamic dispatch and representation costs. The [mypyc developer introduction](https://github.com/python/mypy/blob/master/mypyc/doc/dev-intro.md) explains the pipeline and its restrictions, including limits on monkey-patching compiled definitions. This entry concerns extension compilation, not a general standalone Python executable compiler.

### 24. [dotnet/runtime](https://github.com/dotnet/runtime)

**Language/role:** C# and C/C++; the relevant subsystems are **NativeAOT/ILCompiler**, under `src/coreclr/tools/aot` and `src/coreclr/nativeaot`.

Study whole-program native compilation of managed IL together with the runtime data structures required to execute it.

- **C1:** Reachability must include more than method bodies: generic virtual dispatch, GC layouts, exception information, and reflection-related data introduce dependencies. The [ILC architecture document](https://github.com/dotnet/runtime/blob/main/docs/design/coreclr/botr/ilc-architecture.md) explains static, conditional, and dynamically discovered graph dependencies.
- **C2:** Dependency nodes, root providers, and compilation groups separate graph machinery from decisions about what belongs in a compilation. This supports reuse across compilation policies and related toolchains.

The [NativeAOT developer workflow](https://github.com/dotnet/runtime/blob/main/docs/workflow/building/coreclr/nativeaot.md) explains generation of native object files, linkage with a specialized runtime, and shared infrastructure with crossgen2. Its separately compiled testing mode is explicitly not a shipping configuration; historical architecture possibilities should not be mistaken for supported deployment modes.

### 25. [oracle/graal](https://github.com/oracle/graal)

**Language/role:** Primarily Java with native support; the relevant subsystem is **Native Image**, including Substrate VM. Other Graal JIT and language-runtime components are not counted separately.

Study the practical consequences of making a managed-language application closed-world before execution.

- **C1:** Static reachability alone cannot recover every reflective lookup, dynamic class operation, JNI use, or proxy construction. Native Image's [reference overview](https://github.com/oracle/graal/blob/master/docs/reference-manual/native-image/README.md) explains the closed-world assumption and the metadata required for dynamic features.
- **C3:** Points-to analysis determines reachable methods and runtime data before parsing, inlining, machine compilation, and image layout. Reflection registration and image-heap contents affect both build work and executable footprint. The [build-output guide](https://github.com/oracle/graal/blob/master/docs/reference-manual/native-image/BuildOutput.md) exposes these phases and measurements, providing a useful bridge from architecture to performance diagnosis.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, including general AOT architecture; functional whole-program compilation; verified C/ML compilation; scientific Fortran and array languages; SIMD/SPMD and distributed compilation; embedded Go; self-hosted systems languages; Python AOT; and managed NativeAOT/Native Image. Follow-up queries sought design documents, ABI implementations, semantic passes, tests and changelogs, and migration/mirror status. Later distinct queries increasingly returned already-covered compiler families or small demonstration projects. Follow-up review verified GCC's mirror provenance and added its shared lowering and pass machinery, bringing the selection to 25 substantial codebases.

Each retained repository's exact GitHub root was opened, and at least one additional primary document or implementation file was read. The entries emphasize concrete code or design contracts; the judgement that these make good study projects is an inference from that evidence. C4 is claimed only where the inspected history supplies compatibility or regression-management evidence across years. Other entries do not imply a checked maintenance cadence or uniform production readiness.

Important exclusions and boundaries:

- **Zig:** The [former GitHub repository](https://github.com/ziglang/zig) points to Codeberg. A suitable current GitHub mirror was not verified in this research pass, so replacement mirrors were not substituted.
- **Mirror provenance:** GCC is included through a substantive unofficial mirror identified by upstream; Go and GHC use official mirrors. Hosting status is disclosed separately from the engineering criteria, and a mirror is not counted as another implementation of its upstream project.
- **Duplicate homes and subsystems:** mypyc is represented by the implementation in `python/mypy`, and NativeAOT by `dotnet/runtime`; documentation-only pointer repositories and historical predecessor repositories were not counted as additional compilers. LLVM's monorepo is likewise one entry.
- **Category boundaries:** Bytecode-only and JIT-only systems, backend libraries without an identified language compiler, tutorials, generated wrappers, and compiler lists were excluded. Native extension compilation and C-mediated native compilation are included explicitly. Mixed CPU/GPU pipelines do not imply that every device compilation step happens ahead of time.

This is a source-reading selection guide, not a build audit, benchmark, exhaustive ecosystem census, or comparative ranking. No candidate repository was cloned or executed, and the research did not assess every target, language feature, or historical release. Branch-based documentation links can change after the research date.
