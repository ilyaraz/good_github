# Symbolic execution engines

Research date: **2026-10-09**.

This guide selects **25 GitHub repositories** that implement substantive symbolic execution machinery: path-oriented interpreters, concolic instrumentation, symbolic virtual machines, and reusable execution cores. It includes the execution subsystem of a bounded model checker, but excludes standalone SMT solvers, thin integrations, and projects that merely invoke another engine. The emphasis is on what an experienced engineer can learn from the implementation, not on stars or a ranking of verification power. Criteria are evidence-based selection judgments, not assurances that every supported language feature is modeled soundly.

**Criteria legend:** **C1** — difficult correctness involving semantics, invariants, adversarial inputs, concurrency, or failure modes. **C2** — substantial reusable abstractions supporting multiple analyses or applications. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — sustained evolution demonstrated by compatibility work, testing, or complexity management, rather than repository age alone.

## LLVM, bounded execution, and concolic instrumentation

### [klee/klee](https://github.com/klee/klee)

**C++ — LLVM symbolic virtual machine with POSIX environment models.** Study the relationship between execution states, allocation objects, symbolic expressions, and search policies. This is a particularly useful reference for implementing memory semantics without copying an entire heap at every branch.

**C1:** Allocation identity is separated from per-path object contents; symbolic addresses must be resolved against possible objects, and stack objects become inaccessible when their frames disappear. **C3:** Immutable address-space trees, copy-on-write object states, shared update lists, and expression folding address the cost of branching and byte-level memory operations. These mechanisms are explained in the [implementation overview](https://github.com/klee/klee/blob/master/docs/overview). **C4:** The dated [NEWS](https://github.com/klee/klee/blob/master/NEWS) records several years of LLVM compatibility changes, allocator evolution, CI work, and correctness fixes, including restrictions on incorrectly handled oversized symbolic objects. Those two files are useful starting points; the overview is historical in places, so use NEWS to understand subsequent changes.

### [diffblue/cbmc](https://github.com/diffblue/cbmc)

**C++ — bounded model checker; the relevant subsystem is `goto-symex`.** Count this monorepo once. Its symbolic executor is worth studying even when the desired product is not a model checker: it translates execution into an explicit system of SSA equations, assumptions, and assertions.

**C1:** Pointer candidate sets, variable renaming across calls and threads, and assertions about exhausted unwind bounds expose difficult semantic and completeness obligations. The documentation also candidly describes the aliasing limitation of failed-object fallbacks. **C2:** `symex_targett` separates execution from equation construction, and the engine supports both merged execution and individual-path exploration. **C3:** Memory-heavy state is created on demand and released promptly. The detailed [goto-symex architecture documentation](https://diffblue.github.io/cbmc/group__goto-symex.html) explains these mechanisms; the [repository README](https://github.com/diffblue/cbmc/blob/develop/README.md) supplies language scope and distinguishes tested releases from development builds.

### [PLSysSec/haybale](https://github.com/PLSysSec/haybale)

**Rust — embeddable LLVM IR symbolic executor.** A smaller alternative for studying a library interface in which an `ExecutionManager` exposes successive paths and clients inspect or constrain their states.

**C1:** The backend explicitly distinguishes cloning a solver reference from duplicating its state; bitvectors and arrays must be matched to the correct duplicate, with documented lifetime restrictions. **C2:** Related `Backend`, `BV`, `Memory`, and `SolverRef` traits separate execution from representation, while hooks and configuration support custom analyses. **C3:** Solver model generation is enabled only when needed, with the implementation explaining the cost for frequent incremental checks. Start with [backend.rs](https://github.com/PLSysSec/haybale/blob/main/src/backend.rs) and the [API-oriented README](https://github.com/PLSysSec/haybale/blob/main/README.md). **Historical compatibility caveat:** GitHub metadata showed the latest push in October 2023; the README supports LLVM 9–14. Do not assume compatibility with current LLVM.

### [eurecom-s3/symcc](https://github.com/eurecom-s3/symcc)

**C++ with Rust tooling — compiler-assisted concolic execution.** Study how an LLVM pass adds symbolic computation to a program while preserving ordinary native execution and delegating expression construction to a runtime.

**C1:** Instrumentation must preserve SSA relationships, including symbolic PHI nodes; finalization replaces unnecessary nodes and invalidates expression mappings that would otherwise retain stale references. **C3:** The compiler emits a concrete fast path that skips symbolic expression construction when all operands are concrete, and a slow path that constructs missing expressions. These mechanisms are visible in [Symbolizer.cpp](https://github.com/eurecom-s3/symcc/blob/master/compiler/Symbolizer.cpp). The [README](https://github.com/eurecom-s3/symcc/blob/master/README.md) explains the compiler/runtime boundary and the hybrid-fuzzing workflow. **Maintenance and semantic caveats:** the maintainers explicitly describe best-effort maintenance; the QSYM backend deliberately prunes paths, and unsupported library interactions can lose symbolic information.

### [eurecom-s3/symqemu](https://github.com/eurecom-s3/symqemu)

**C — binary-only concolic execution through modified QEMU translation.** This is a substantive QEMU-derived implementation, not merely a launcher for SymCC. It adds a distinct instrumentation frontend while sharing the symbolic runtime.

**C1:** Runtime helpers reconcile concrete operands with symbolic operands, enforce expression widths, and distinguish signed and unsigned arithmetic. Returning no expression for an unimplemented helper concretizes that operation, an important boundary to inspect. **C3:** Instrumented translation emits helper calls, and fully concrete operations return immediately without constructing symbolic expressions. Start with [tcg-runtime-sym.c](https://github.com/eurecom-s3/symqemu/blob/master/accel/tcg/tcg-runtime-sym.c). The [README](https://github.com/eurecom-s3/symqemu/blob/master/README.md) maps the modified translation files, documents the QEMU 4-to-8 transition, and distinguishes instrumentation unit tests from binary integration tests. Its stated architecture limitations should be treated as part of the design, not incidental setup details.

### [sslab-gatech/qsym](https://github.com/sslab-gatech/qsym)

**C++ and Python — native concolic execution designed for hybrid fuzzing. Archived.** Retain this as a historical implementation of the engineering tradeoff between exhaustive symbolic reasoning and generating useful inputs quickly.

**C1:** Native branch outcomes must be reconciled with bitvector constraints; the solver layer handles timeout exceptions as unknown results and tracks constraints associated with observed values. **C3:** It checks whether branches are interesting before negating them, uses range-based reasoning, and includes an optimistic fallback that drops context when a full query does not produce a solution. These choices are inspectable in [solver.cpp](https://github.com/sslab-gatech/qsym/blob/master/qsym/pintool/solver.cpp), rather than supported only by a speed claim. The [README](https://github.com/sslab-gatech/qsym/blob/master/README.md) describes AFL integration, tests, and old Pin/kernel dependencies. Its approximations and archived status make it an architectural study target, not an assumed current verification platform.

## Binary and whole-system engines

### [angr/angr](https://github.com/angr/angr)

**Python with native dependencies — multi-architecture binary analysis and symbolic execution.** Study the separation of machine state, successor generation, exploration policy, environment modeling, and concrete execution.

**C1:** Symbolic branches produce separate states with complementary path constraints; registers, memory, and input streams must retain compatible bitvector semantics. The [machine-state guide](https://docs.angr.io/en/latest/core-concepts/states.html) explains the mechanism and initialization choices. **C2:** Simulation managers, exploration hooks, engine mixins, and procedure summaries make the executor useful for many analyses. **C3:** The [execution-pipeline guide](https://docs.angr.io/en/latest/advanced-topics/pipeline.html) explains when concrete execution is handed to Unicorn, how symbolic accesses bring execution back, and why cooldowns prevent expensive switching back and forth. These two guides provide an unusually clear route from public APIs to the engine's internal dispatch structure.

### [JonathanSalwan/Triton](https://github.com/JonathanSalwan/Triton)

**C++ with Python bindings — instruction-level dynamic symbolic execution library.** This is the binary-analysis Triton, not the unrelated GPU programming project. It is useful for studying symbolic CPU semantics and constructing custom analysis tools around an explicit context.

**C1:** The symbolic engine maintains parent-register state, byte-addressed memory expressions, and optional symbolic-array memory; concretization must also invalidate overlapping aligned-memory representations. **C2:** Architecture state, AST construction, path management, simplification, callbacks, and solver interfaces are separate components exposed through C++ and Python APIs. Start with [symbolicEngine.cpp](https://github.com/JonathanSalwan/Triton/blob/master/src/libtriton/engines/symbolic/symbolicEngine.cpp) and the [repository API example](https://github.com/JonathanSalwan/Triton#readme). The library intentionally supplies building blocks rather than an entire modeled operating system. The README describes it as a part-time project, so feature support should be checked for the particular ISA and analysis.

### [S2E/s2e](https://github.com/S2E/s2e)

**C++ — selective symbolic execution integrated with a virtualized system.** The relevant implementation is `libs2ecore` and its executor; this repository supplies the library loaded into QEMU. Study the boundary between symbolic program state and a real system's concrete execution state.

**C1:** State switches coordinate CPU registers, shared concrete memory, device state, timers, disk requests, and translation-cache behavior. The order matters: device restoration can itself write memory. **C3:** Selective execution, symbolic-aware native helpers, and lazy forking on symbolic addresses expose explicit speed/precision tradeoffs. [S2EExecutor.cpp](https://github.com/S2E/s2e/blob/master/libs2ecore/src/S2EExecutor.cpp), especially `doStateSwitch` and its configuration options, makes both obligations concrete. The [repository overview](https://github.com/S2E/s2e#readme) identifies the QEMU integration. This is a distinct whole-system architecture despite its KLEE ancestry; KLEE-derived components are not counted separately here.

### [binsec/binsec](https://github.com/binsec/binsec)

**OCaml — binary analysis platform with static symbolic execution.** Focus on the SSE engine and plugin interfaces. It is particularly instructive for extending an executor without embedding every analysis and search policy into the core.

**C2:** Plugins receive typed engine/path abstractions, can instrument newly decoded control-flow graphs, add path fields, and install callbacks. The [shadow-stack plugin walkthrough](https://github.com/binsec/binsec/blob/master/doc/sse/plugins_1.md) explains this interface through an actual security property. **C3:** The [quick-path-merging design](https://github.com/binsec/binsec/blob/master/doc/sse/quick_merge.md) implements opportunistic joining of sibling paths at small branch diamonds. It also handles the difficult lifecycle case where one sibling dies or branches again, so the other must be resumed. The document discusses both saved work and harder merged constraints. These are substantive extension and scheduling designs, not merely a command-line feature list.

### [cea-sec/miasm](https://github.com/cea-sec/miasm)

**Python with C support — binary lifting, IR analysis, emulation, and symbolic execution.** The relevant subsystem is the common IR symbolic evaluator. Study how instruction semantics can be reused across execution and reverse-engineering analyses.

**C1:** Symbolic memory is organized by base expressions and offsets, with slicing of stored expressions and bounded address arithmetic; state merging retains only expressions that agree. **C2:** State, memory, expression simplification, and block lifting have explicit interfaces rather than being tied to one instruction set. These mechanisms are documented directly in [symbexec.py](https://github.com/cea-sec/miasm/blob/master/miasm/ir/symbexec.py). **C4:** The [changelog](https://github.com/cea-sec/miasm/blob/master/CHANGELOG.md) records the 2018 memory-management rewrite, subsequent DSE fixes, expression regression tests, Python migrations, and architecture-semantic corrections through dated later releases. The common evaluator is an analysis component; its conservative merge operation should not be mistaken for retaining every path predicate.

### [trailofbits/manticore](https://github.com/trailofbits/manticore)

**Python — symbolic execution framework for native binaries, EVM, and WebAssembly. Archived.** This remains useful for studying how multiple platforms share state exploration, instrumentation, and a public analysis API.

**C1:** Forking, termination, abandonment, serialization, and several concretization policies are explicit state transitions; Boolean forking adds constraints without necessarily replacing the symbolic expression with a concrete value. **C2:** A common `StateBase` connects constraints and platform state, while solver events and instruction hooks allow independent detectors and custom analyses. Read [core/state.py](https://github.com/trailofbits/manticore/blob/master/manticore/core/state.py) alongside the [platform API examples and archive notice](https://github.com/trailofbits/manticore/blob/master/README.md). The README now explicitly says internal development and maintenance have ended. Its documented EVM opcode gaps and platform restrictions are material when interpreting historical examples.

## Reusable symbolic virtual machines and language frameworks

### [GaloisInc/crucible](https://github.com/GaloisInc/crucible)

**Haskell — language-independent symbolic simulator with LLVM, JVM, and Rust MIR frontends.** Count Crucible, Crux, and the frontends in this monorepo once. Study the boundary between a program representation, a language-specific memory model, symbolic execution, and the What4 expression/solver layer.

**C2:** Programs become control-flow graphs, while new primitives and data types can extend the simulator; the [repository architecture overview](https://github.com/GaloisInc/crucible/blob/master/README.md) explains the package boundaries. **C1:** Crux-LLVM exposes distinct floating-point interpretations and explicit arithmetic/pointer relaxations, making semantic choices visible. **C3:** It supports merging at postdominators or exploring paths independently, separate path-feasibility and goal solvers, and symbolic/solver profiling. The [Crux-LLVM guide](https://github.com/GaloisInc/crucible/blob/master/crux-llvm/README.md) explains these controls and counterexample limitations. Different floating-point modes and resource bounds must not be treated as interchangeable proofs.

### [GillianPlatform/Gillian](https://github.com/GillianPlatform/Gillian)

**OCaml — compositional symbolic execution parameterized by language memory semantics.** The monorepo includes the core and C, JavaScript, and small-language instantiations. It is a strong study target for building a language family around one symbolic executor.

**C2:** An instantiation supplies a memory model and a compiler into GIL, as the [current introduction](https://gillianplatform.github.io/intro.html) explains. **C1:** The [paper-to-implementation comparison](https://gillianplatform.github.io/publications/gillian1/impl_diffs.html) makes difficult details explicit: error returns versus normal returns, fresh-symbol allocation, mutable memory copying, and path conditions split between formulas and type information. It also shows how the abstraction becomes executable OCaml interfaces. That second document explicitly describes the PLDI 2020 version, so it is historical architectural evidence rather than a promise that every interface remains unchanged. The distinction itself is useful when studying how formal designs become maintainable implementations.

### [emina/rosette](https://github.com/emina/rosette)

**Racket — solver-aided host language with an embedded symbolic virtual machine.** Include the SVM, not just the surface synthesis language. This is a different architecture from interpreting LLVM or machine code: client languages can express their semantics using lifted host-language operations.

**C1:** Guarded evaluation captures both store mutations and verification conditions, then merges results. Its implementation states the required exclusivity and coverage conditions on guards and specifies restoration of the caller's store and verification condition. **C2:** The host supports verification, synthesis, and domain-specific languages through the same symbolic evaluator. Start with [eval.rkt](https://github.com/emina/rosette/blob/master/rosette/base/core/eval.rkt). The [release notes](https://github.com/emina/rosette/blob/master/NOTES.md) are another useful entry point: they document changes in numerical semantics, verification-condition tracking, solver interfaces, and profiling. The repository distinguishes symbolically safe constructs from unrestricted Racket; arbitrary host operations are not automatically sound symbolic models.

### [OCamlPro/owi](https://github.com/OCamlPro/owi)

**OCaml — WebAssembly symbolic execution and analysis of languages compiled to Wasm.** Study how one interpreter can support concrete and symbolic execution while also accommodating host functions and multiple source languages.

**C1:** The interpreter distinguishes trapping and nontrapping branches, checks memory access bounds with attention to arithmetic overflow, and carries structured block/return state. **C2:** An OCaml functor parameterizes values, choice operations, memory, tables, external functions, and environments; concrete and symbolic instances share instruction semantics. These are visible in [interpret.ml](https://github.com/OCamlPro/owi/blob/main/src/interpret/interpret.ml). The [development guide](https://github.com/OCamlPro/owi/blob/main/HACKING.md) describes executable documentation tests, Cram tests, fuzzing, and profiling. The README's cross-language scope comes from compilation to Wasm, not independent native semantics for each source language; the newer abstract-interpretation verification direction is explicitly experimental.

## Managed and dynamic language engines

### [SymbolicPathFinder/jpf-symbc](https://github.com/SymbolicPathFinder/jpf-symbc)

**Java — symbolic bytecode execution extending Java PathFinder.** Study how a symbolic interpreter can reuse an existing VM's operand metadata, choice generators, and search/backtracking infrastructure.

**C1:** A symbolic branch must preserve concrete operand-stack effects while installing the appropriate equality or inequality constraint; infeasible choices are marked ignored. The concrete-driven mode must select the choice corresponding to the branch actually taken. [IF_ICMPEQ.java](https://github.com/SymbolicPathFinder/jpf-symbc/blob/master/src/main/gov/nasa/jpf/symbc/bytecode/IF_ICMPEQ.java) provides a compact, substantive example. **C2:** The extension applies the same machinery to methods with primitive, string, array, and user-defined inputs, rather than providing only a single test generator. The [README](https://github.com/SymbolicPathFinder/jpf-symbc/blob/master/README.md) defines that scope. **Compatibility caveat:** its documented setup requires Java 8 and specific JPF-core versions; this is not evidence of compatibility with arbitrary modern JVMs.

### [pietrobraione/jbse](https://github.com/pietrobraione/jbse)

**Java — symbolic JVM exposed as an analysis library.** Study a clean separation between instruction stepping, tree traversal, symbolic expression rewriting, and decision procedures.

**C1:** Symbolic references force case splits that include null dereferences as well as value-producing accesses; the engine stores alternatives and backtracks to them. **C2:** A low-level `Engine` is driven by a higher-level `Runner`, with callbacks for execution events and configurable calculators and rewriting rules. The [usage/architecture manual](https://jbse-manual.readthedocs.io/en/latest/text/using.html) explains these interfaces and their dependencies. The [README](https://github.com/pietrobraione/jbse/blob/master/README.md) explains reference semantics, regression tests, packaging, and dependency isolation. **Compatibility caveat:** the build/runtime requirements are unusually specific—Java 8 for JBSE and a newer Java runtime for its Gradle version—and the project says formal releases await greater stability.

### [UnitTestBot/usvm](https://github.com/UnitTestBot/usvm)

**Kotlin — reusable symbolic core with a JVM instantiation and experimental Python support.** Focus on `usvm-core` and how `usvm-jvm` assembles it into a language engine. This is useful for studying analysis-specific targeting and observability.

**C2:** Shared memory, container, type-constraint, solver, and path-selection facilities let a language interpreter reuse more than an SMT wrapper. The [README](https://github.com/UnitTestBot/usvm/blob/main/README.md) connects these facilities to test generation, custom checkers, and confirmation of reported paths. **C3:** [JcMachine.kt](https://github.com/UnitTestBot/usvm/blob/main/usvm-jvm/src/main/kotlin/org/usvm/machine/JcMachine.kt) explicitly composes path selectors with coverage, call-graph information, loop tracking, state collectors, and time/step stopping strategies. Those mechanisms make the performance design inspectable. The advertised precision and speed are not accepted here as measured comparative results; the retained evidence is the reusable core and its concrete scheduling architecture.

### [VSharp-team/VSharp](https://github.com/VSharp-team/VSharp)

**F# symbolic core, C# APIs/tests, and C++ runtime support — symbolic execution of .NET assemblies.** A valuable counterweight to JVM-heavy coverage. Study how symbolic heap semantics interact with reflection, managed references, arrays, and generated executable tests.

**C1:** The memory implementation distinguishes heap references, pointers and offsets, guarded alternatives, stack reads, and multidimensional array indexing. **C2:** Typed region/key abstractions support different memory locations, while the public API and runner analyze methods or classes from arbitrary assemblies. Start with [Memory.fs](https://github.com/VSharp-team/VSharp/blob/master/VSharp.SILI.Core/Memory.fs) and the [API/runner walkthrough](https://github.com/VSharp-team/VSharp#readme). The walkthrough demonstrates an integer-minimum failure and generation of object inputs. **Status caveat:** the README describes an unreleased research implementation; its statement about active development is not treated here as independent evidence of a current maintenance cadence.

### [pschanely/CrossHair](https://github.com/pschanely/CrossHair)

**Python — symbolic execution through proxy values passed to ordinary Python functions.** Study an engine that uses the host interpreter rather than implementing a separate full bytecode interpreter.

**C1:** Symbolic proxies must reconcile Python and solver semantics for types, conversions, truthiness, exceptions, mutation, and aliasing. In particular, `SymbolicBool.__bool__` chooses a feasible concrete branch and adds the corresponding constraint while exploration remembers alternative decisions. The [implementation explanation](https://crosshair.readthedocs.io/en/latest/how_does_it_work.html) describes this mechanism and its difficult boundaries. **C2:** The same execution machinery supports contract checking, input/test generation, behavioral comparison, custom classes, and library integrations, as documented in the [README](https://github.com/pschanely/CrossHair/blob/main/README.md). The architecture is attractive for incremental adoption, but unsupported host behavior and concretization boundaries remain part of interpreting its results.

### [ExpoSEJS/ExpoSE](https://github.com/ExpoSEJS/ExpoSE)

**JavaScript — Jalangi-based dynamic symbolic execution for Node.js, with limited browser support.** Study the separation between instrumented execution of one input and distributed scheduling of newly discovered alternatives.

**C1:** [SymbolicState.js](https://github.com/ExpoSEJS/ExpoSE/blob/master/Analyser/src/SymbolicState.js) models coercions and truthiness, tracks path conditions, builds string constraints, and negates branches while preserving the earlier path prefix. Its explicit modeling limitations are as instructive as the successful cases. **C3:** [Center.js](https://github.com/ExpoSEJS/ExpoSE/blob/master/Distributor/src/Center.js) bounds concurrent workers, times out test processes, aggregates coverage, and feeds alternative inputs back into a scheduling strategy. **Status/compatibility caveat:** GitHub metadata showed the latest push in January 2025, and the README names Node 21.7.2 as the tested version. Do not read the general JavaScript-support description as full current-language or browser conformance.

## EVM and smart-contract symbolic execution

### [argotorg/hevm](https://github.com/argotorg/hevm)

**Haskell — concrete and symbolic EVM execution, equivalence checking, and symbolic unit testing.** This is the current canonical repository reached from the former `ethereum/hevm` URL. Its README traces the separate implementation's origin to dapptools; the old location is not counted again.

**C1:** Symbolic calldata, callers, storage initialization, and assertion/revert interpretation make the execution environment part of the verification problem. **C3:** The engine normally explores before asking the solver about violating leaves, but begins feasibility checks after a configurable number of loop iterations to avoid unrestricted eager expansion. The [symbolic-execution guide](https://hevm.dev/symbolic.html) explains that tradeoff and the default exclusion of arithmetic-overflow panics. The [repository overview](https://github.com/argotorg/hevm#readme) documents equivalence testing, Forge integration, and Ethereum standard-test execution. These are useful entry points into both search strategy and reusable testing interfaces.

### [a16z/halmos](https://github.com/a16z/halmos)

**Python — symbolic EVM testing with a Solidity/Foundry-oriented frontend.** Study the bridge between familiar property tests and a dedicated symbolic VM, especially its handling of paths that the solver cannot immediately decide.

**C1:** The branch implementation distinguishes unsatisfiable results from unknown results, validates jump destinations, and copies persistent/transient storage and execution context when forking. **C3:** Loop bounds apply to symbolic branches while proven concrete branch behavior can continue; branch creation deliberately shares stable data and copies mutable state. These choices are explicit in [sevm.py](https://github.com/a16z/halmos/blob/main/src/halmos/sevm.py). The [symbolic-test guide](https://github.com/a16z/halmos/blob/main/docs/getting-started.md) explains reusable symbolic setup and assumptions, as well as its crucial assertion policy: ordinary revert cases, including overflow reverts, are not reported like `Panic(1)` assertion failures. A passing symbolic test must therefore be interpreted with its bounds and modeled failure policy.

### [ConsenSysDiligence/mythril](https://github.com/ConsenSysDiligence/mythril)

**Python — EVM security analysis built around the LASER symbolic engine.** This is the canonical repository reached from the older `Consensys/mythril` URL. The relevant subsystem is `mythril/laser`, not merely the vulnerability-reporting CLI.

**C1:** The executor distinguishes global machine state from world state carried across transactions and explicitly handles nested transaction starts/ends and VM exceptions. **C2:** Search strategies, world-state hooks, transaction hooks, and per-instruction pre/post hooks let detectors remain separate from execution semantics. **C3:** Depth, execution-time, transaction-count, and optional state-space recording controls make resource costs explicit. Start with [svm.py](https://github.com/ConsenSysDiligence/mythril/blob/develop/mythril/laser/ethereum/svm.py) and the [usage README](https://github.com/ConsenSysDiligence/mythril/blob/develop/README.md). The documented bounded transaction exploration is not a claim of unrestricted contract verification; current EVM-fork and dependency compatibility should be checked for a concrete deployment.

## Coverage and search notes

Discovery used more than six distinct live search formulations, including LLVM interpreters/compiler instrumentation; binary lifting and native concolic engines; selective whole-system execution; JVM and .NET engines; Python and JavaScript execution; Wasm and Rust-oriented engines; language-independent Haskell/OCaml/Racket frameworks; and EVM symbolic testing. Follow-up searches targeted memory models, path merging, symbolic state, architecture documents, and exact source-tree locations. Later searches mainly returned already-covered families, thin integrations, forks, tutorials, or unrelated projects with colliding names. The final selection favors distinct implementations and architectural lessons rather than exhaustive enumeration.

Every retained canonical URL was opened as a repository page or checked through GitHub's public repository API. Each entry also has an independently read implementation or documentation source beyond the root README; a raw copy of a README was not counted as a second source. Exact source paths were checked before citation. GitHub API rate limits interrupted recursive tree enumeration after repository verification, so direct source reads and rendered project documentation supplied the remaining evidence. No candidate repository was cloned, installed, or executed, and no benchmark results were reproduced.

SMT backends such as Z3 and What4 were excluded as independent engines; wrapper-oriented integrations and example repositories were not counted. Crucible's frontends and Crux count once, as do the engine subsystems inside CBMC and Mythril. SymQEMU is retained separately because its QEMU translation instrumentation is substantive, despite sharing SymCC's runtime. [WASP explicitly points to Owi as its successor](https://github.com/formalsec/wasp), so it was not added as another comparable current choice. Manticore and QSYM are explicitly archived; older activity and pinned dependencies are flagged where material. No project is labeled an official mirror, and the hevm/Mythril ownership redirects are represented only by their current canonical repositories.

The report establishes category fit and concrete reasons to study the code. It does not establish uniform soundness, completeness, contemporary toolchain compatibility, or production readiness. In particular, C1 identifies difficult correctness work in the implementation; it does not certify that all such problems have been solved.
