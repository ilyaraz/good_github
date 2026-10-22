# Static analysis and abstract interpretation frameworks

Research date: **2026-10-09**.

This guide selects **27 GitHub repositories** whose reusable static-analysis machinery is worth studying: abstract domains, fixpoint engines, interprocedural dataflow, pointer analysis, semantic models, and analysis composition. It includes standalone libraries, substantial analyzer frameworks, and explicitly identified subsystems of larger projects. Research prototypes and historical implementations are included when they expose a distinctive architecture. Inclusion is an engineering assessment grounded in the linked material, not a claim that every component is exemplary or that every configuration is sound.

Criteria used throughout:

- **C1 — Difficult correctness:** invariants, concurrency, numerical or language semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components that support multiple analyses, domains, languages, or clients.
- **C3 — Performance with structure:** concrete approaches to time or memory constraints, with an understandable architectural explanation.
- **C4 — Sustained evolution:** years of documented changes together with compatibility work, testing, or complexity management. Age alone does not qualify.

## Abstract domains and reusable fixpoint engines

### 1. [antoinemine/apron](https://github.com/antoinemine/apron)

**Language / role:** C, with OCaml, Java, and C++ interfaces; numerical abstract-domain library.

Study how a common numerical interface accommodates intervals, octagons, polyhedra, and other domains while retaining domain-specific implementations. The two API levels distinguish low-level numerical dimensions from named-variable environments and expression handling.

- **C1:** Resource failures are part of the semantic contract: timeouts, overflow, or allocation limits must still yield a sound approximation, potentially the top element. Exact and floating-point scalar representations also have explicit interfaces.
- **C2:** Managers select domain implementations behind common operations; level 1 supplies shared environment and expression services above level 0. Cartesian and reduced products provide composition mechanisms.
- **C3:** Functional and destructive operations let clients manage copying and allocation deliberately.

Entry points: [C API architectural choices](https://antoinemine.github.io/Apron/doc/api/c/General-choices.html), which documents these contracts, and the [documentation hub](https://antoinemine.github.io/Apron/doc/).

### 2. [eth-sri/ELINA](https://github.com/eth-sri/ELINA)

**Language / role:** Primarily C; optimized numerical abstract domains, with bindings and neural-network analysis components.

ELINA is useful for studying how mathematical domain operations are reorganized around hardware and representation costs. Its repository includes polyhedra, octagons, zones, and neural-network domains; these are different components, not separate repositories in this guide.

- **C2:** Domain-specific manager constructors expose implementations through APRON-compatible interfaces, enabling existing analyzers to change domain implementations without rebuilding their whole analysis architecture.
- **C3:** The project explains online decomposition, vectorization, locality improvements, and scalar replacement. Optional AVX paths for octagons and zones give concrete implementation choices to inspect rather than a bare claim of speed.

Entry point: the [official architecture, interfaces, and testing overview](https://elina.ethz.ch/). It also identifies transformer tests and language bindings. The site's dated news is not used as evidence of current maintenance, and no benchmark ratio is asserted here.

### 3. [seahorn/crab](https://github.com/seahorn/crab)

**Language / role:** C++; abstract interpretation library with its own intermediate representation.

Crab exposes the boundary between an analysis language, domain implementations, and convergence machinery particularly clearly. Its architecture describes numerical, array, and memory domains, domain products, forward and backward analyses, and several interprocedural strategies.

- **C1:** Weak topological ordering identifies widening points; threshold and lookahead widening address convergence and precision. Recursive interprocedural analysis adds another layer of fixpoint reasoning.
- **C2:** CrabIR and separate domain, CFG, call-graph, and fixpoint components allow analyses to reuse machinery across abstract domains.
- **C3:** Memoized top-down interprocedural analysis and alternative bottom-up/top-down strategies expose where repeated analysis work can be avoided. These mechanisms are described in the [repository overview](https://github.com/seahorn/crab).

Entry points: [library headers](https://github.com/seahorn/crab/tree/master/include/crab) and [tests and domain-test integration instructions](https://github.com/seahorn/crab/tree/master/tests). The latter distinguishes integer and rational domain instantiations and maintains domain-specific expected outputs.

### 4. [facebook/SPARTA](https://github.com/facebook/SPARTA)

**Language / role:** C++ analysis library; this entry focuses on its generic abstract interpretation and fixpoint interfaces.

The fixpoint iterator is a compact place to study how a library makes solver assumptions visible in its API. It accepts a graph interface rather than assuming that every client uses the same CFG representation.

- **C1:** The implementation specifies monotonic node and edge transformers and checks the abstract-domain type relationship. Correctness depends on these explicit client obligations.
- **C2:** Graph entry, predecessor, successor, source, and target operations are parameterized; the abstraction also accommodates call and dependency graphs.
- **C3:** Node analysis updates states in place to avoid copying expensive domain values repeatedly across instructions.

Entry points: [FixpointIterator.h](https://github.com/facebook/SPARTA/blob/main/include/sparta/FixpointIterator.h), containing these contracts and implementation choices, and the [domain and solver header collection](https://github.com/facebook/SPARTA/tree/main/include/sparta).

### 5. [NASA-SW-VnV/ikos](https://github.com/NASA-SW-VnV/ikos)

**Language / role:** C++; reusable abstract interpretation core plus LLVM-based C/C++ analysis.

The independently usable core makes IKOS valuable beyond its command-line analyzer. Study how numerical reasoning is connected to pointer, memory, lifetime, and initialization abstractions without embedding every concern into a single domain.

- **C1:** The core distinguishes machine-integer domains from mathematical numerical domains and provides separate abstractions for memory, nullity, lifetime, exceptions, and uninitialized values. These distinctions expose semantic obligations that a single interval abstraction cannot handle.
- **C2:** Its header-only core provides CFG traits, fixpoint iterators, abstract domains, number representations, and supporting data structures independently of the analyzer frontend.

Entry point: the [core source tree and separate core architecture README](https://github.com/NASA-SW-VnV/ikos/tree/master/core). It also documents the unit-test organization and Patricia-tree data structures; those tests alone are not treated as proof of soundness or C4.

### 6. [lisa-analyzer/lisa](https://github.com/lisa-analyzer/lisa)

**Language / role:** Java; framework for constructing analyses for multiple source languages.

LiSA is an instructive example of normalizing language-specific constructs before abstract evaluation. For example, a frontend can resolve overloaded addition into numerical addition or string concatenation and pass an appropriate symbolic expression to the analysis.

- **C1:** Whole-program analysis coordinates interprocedural fixpoints, CFG fixpoints, and call-target resolution; semantic checks consume the converged results. Its state architecture separates memory, type, and value reasoning.
- **C2:** The SDK, analysis implementations, program constructs, and demonstration language occupy separate projects. Language-neutral symbolic expressions let different frontends reuse domains.

Entry point: [architecture and developer documentation](https://lisa-analyzer.github.io/documentation/), especially the project organization, symbolic expressions, and analysis workflow. The [project site](https://lisa-analyzer.github.io/) describes an evolving research framework and warns that APIs can change; this entry does not imply a stable compatibility contract.

## C/C++, LLVM, and configurable verification platforms

### 7. [goblint/analyzer](https://github.com/goblint/analyzer)

**Language / role:** OCaml; composable, thread-modular analysis of C programs.

Goblint is especially useful for studying collaboration between analyses. Components communicate through queries and events, while analysis lifters add concerns such as context control and widening policy.

- **C1:** The implementation includes must/may lock information, locksets, thread identities and joins, and may-happen-in-parallel reasoning. These interact with value analysis and shared-memory interference.
- **C2:** Analysis specifications are dynamically combined into a constraint system. Query results from participating analyses are combined, and lifters wrap existing analyses instead of duplicating their transfer logic.
- **C3:** The architecture includes incremental comparison of program representations and reuse of previous analysis work, making invalidation boundaries part of the design.

Entry point: the [official module-level implementation reference](https://goblint.github.io/analyzer/goblint/Goblint_lib/index.html), particularly the analysis composition, lifters, thread domains, incremental machinery, and QCheck property-testing modules.

### 8. [facebook/infer](https://github.com/facebook/infer)

**Language / role:** Primarily OCaml; analysis platform with a reusable abstract interpretation framework.

The `Absint` framework provides a concrete progression from a lattice and transfer functions to a registered checker. Its liveness and initialization-order examples show how analysis authors connect an abstract interpreter to reporting and interprocedural summaries.

- **C1:** CFG choices include forward, backward, and exceptional control flow; the interpreter maintains pre/post invariants at program points. Picking the correct CFG and transfer semantics is an explicit correctness concern.
- **C2:** OCaml modules and functors separate abstract domains, transfer functions, CFG interfaces, and interpreter construction.
- **C3:** Dependency analysis computes procedure summaries on demand, allowing callers to reuse summarized effects instead of repeatedly traversing bodies.

Entry point: [the official Absint framework guide](https://fbinfer.com/docs/absint-framework/). Its documented interprocedural model is modular: the guide explicitly says this interface does not express arbitrary global interprocedural analyses. This entry evaluates that subsystem, not every Infer checker.

### 9. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language / role:** C++; specifically the **Clang Static Analyzer** subsystem in `clang/lib/StaticAnalyzer`.

Study the expression-level engine's integration of program states, memory regions, constraints, checker callbacks, and an exploded graph. The LLVM monorepo is counted once; compiler optimization infrastructure is outside this entry's scope.

- **C1:** The engine models path-dependent C++ construction state, stack frames, and object lifetimes. These semantics are visible in the [ExprEngine implementation](https://clang.llvm.org/doxygen/ExprEngine_8cpp_source.html), not merely in a checker feature list.
- **C2:** `ExprEngine` builds expression semantics over `CoreEngine`, with separate constraint, state, region, and checker managers.
- **C3:** Inlining decisions, loop handling, and constraint-solver budgets make resource limits explicit. The [analyzer configuration reference](https://clang.llvm.org/docs/analyzer/user-docs/Options.html) also explains how eager state splitting increases path counts.

Entry points are the two sources above. Configuration choices can suppress paths or reports; this is not a blanket claim of exhaustive verification.

### 10. [SVF-tools/SVF](https://github.com/SVF-tools/SVF)

**Language / role:** C++; LLVM-based pointer and static value-flow analysis framework.

SVF is a useful bridge from alias analysis to reusable sparse representations of memory effects. Study how points-to information supports side-effect analysis and memory SSA rather than treating pointer analysis as a terminal report.

- **C1:** Indirect reads and writes require alias-dependent use/definition sets. The Mod/Ref and memory-SSA construction expose the difficulty of preserving these effects across procedures.
- **C2:** Its design separates **Graph**, **Rules**, and **Solver**, allowing analysis relations and algorithms to operate over shared representations.
- **C3:** Memory-region partitioning controls both precision and the size of the resulting value-flow representation; this makes scalability an architectural choice.

Entry point: the [official SVF design guide](https://github.com/svf-tools/SVF/wiki/SVF-Design), especially its memory SSA and framework architecture sections. The repository's LLVM-version history is useful context, but no compatibility claim is inferred solely from that history.

### 11. [secure-software-engineering/phasar](https://github.com/secure-software-engineering/phasar)

**Language / role:** C++; LLVM interprocedural dataflow analysis framework.

PhASAR makes IFDS analysis construction tangible: clients provide a fact domain and different flow functions for ordinary instructions, calls, returns, call-to-return edges, and summaries. The framework supplies the surrounding interprocedural infrastructure.

- **C1:** The distinct flow-function categories encode call/return behavior, while the distinguished zero fact supports facts generated independently of incoming facts. Incorrect choices here change the analysis semantics.
- **C2:** `IFDSTabulationProblem` and its analysis-domain types parameterize program nodes and facts; custom abstract-memory representations and summaries can be plugged in.
- **C3:** Flow functions are cached after construction for reached instructions, reducing repeated setup during tabulation.

Entry point: [Writing an IFDS Analysis](https://github.com/secure-software-engineering/phasar/wiki/Writing-an-IFDS-Analysis), an implementation-oriented guide with API definitions and examples. The repository also contains other solver families; this assessment centers on the inspected IFDS extension architecture.

### 12. [sosy-lab/cpachecker](https://github.com/sosy-lab/cpachecker)

**Language / role:** Java; configurable software-verification framework. **Official read-only GitHub mirror** of development hosted elsewhere, as identified by the repository.

CPAchecker offers a particularly explicit decomposition of an analysis into operators. Study how the framework can vary state representation, exploration precision, merging, and coverage without conflating them.

- **C1:** The analysis interface requires an abstract domain, transfer relation, merge operator, stop operator, and precision adjustment. Coverage is decided against reached states under a supplied precision; these are essential semantic decisions rather than generic collection operations.
- **C2:** The `ConfigurableProgramAnalysis` contract exposes these operators separately, along with initial-state and initial-precision construction, so components can be assembled into different verification configurations.

Entry points: the [ConfigurableProgramAnalysis interface](https://raw.githubusercontent.com/sosy-lab/cpachecker/main/src/org/sosy_lab/cpachecker/core/interfaces/ConfigurableProgramAnalysis.java) and [StopOperator interface](https://raw.githubusercontent.com/sosy-lab/cpachecker/main/src/org/sosy_lab/cpachecker/core/interfaces/StopOperator.java). The mirror is retained because it contains the substantive implementation, not merely relocation instructions.

## JVM, declarative analysis, and pluggable type systems

### 13. [soot-oss/soot](https://github.com/soot-oss/soot)

**Language / role:** Java; established Java/Android analysis and transformation framework.

Soot's multiple intermediate representations support different analysis needs. Its generic flow-analysis implementation is especially instructive for the interaction between graph traversal, object sharing, and convergence.

- **C1:** Backward analysis must handle loops with no exit. The solver discusses selecting representatives from closed strongly connected components and preserving necessary merge nodes to prevent nonterminating iteration.
- **C2:** Generic forward/backward flow analysis is separated from client flow facts and from the framework's Baf, Jimple, Shimple, and Grimp representations.
- **C3:** The solver shares flow objects where safe to reduce memory consumption; the same code documents where sharing and merge elimination would break the algorithm.

Entry point: [FlowAnalysis.java](https://raw.githubusercontent.com/soot-oss/soot/develop/src/main/java/soot/toolkits/scalar/FlowAnalysis.java). Soot and SootUp are separate entries because SootUp is a new implementation; the original project's README also explains remaining feature differences.

### 14. [soot-oss/SootUp](https://github.com/soot-oss/SootUp)

**Language / role:** Java; redesigned static-analysis framework and successor implementation to Soot.

SootUp is useful for studying the replacement of global framework state with explicit program views and immutable intermediate representations. Its documentation identifies it as a new implementation rather than a drop-in update.

- **C1:** Immutable IR objects and controlled construction of interned identifiers reduce accidental mutation and identity inconsistencies across analyses.
- **C2:** Separate core, frontend, Java support, call-graph, and analysis components support library use. Views allow multiple program representations without a single global `Scene`.
- **C3:** Lazy loading and hash-consed identifiers reduce unnecessary construction and allow efficient identity comparisons under documented factory invariants.

Entry points: [architectural changes from Soot](https://soot-oss.github.io/SootUp/latest/whatsnew/) and the [documentation overview](https://soot-oss.github.io/SootUp/latest/). These differences justify retaining both projects without counting a routine fork twice.

### 15. [wala/WALA](https://github.com/wala/WALA)

**Language / role:** Primarily Java; program-analysis libraries with Java, JavaScript, and other language support.

WALA is a strong study target for separating heap abstraction from calling-context policy. Its pointer-analysis documentation explains what allocation instances and pointer keys represent and how call-graph construction interacts with points-to information.

- **C1:** Entry modeling through a synthetic root, reflection, heap locations, and call contexts all affect which behaviors the analysis covers.
- **C2:** `HeapModel`, `InstanceKey`, `PointerKey`, and `ContextSelector` form distinct extension points; clients can change heap and context policies independently.
- **C3:** Selective merging of strings, exceptions, or large groups of allocation sites provides concrete ways to control analysis size.

Entry point: [the official pointer-analysis design guide](https://github.com/wala/WALA/wiki/Pointer-Analysis). It also identifies settings whose reflection assumptions sacrifice soundness. Some examples use older Java environments; use the guide for architecture rather than as a current installation recipe.

### 16. [soot-oss/heros](https://github.com/soot-oss/heros)

**Language / role:** Java; reusable IFDS/IDE interprocedural dataflow solver.

Heros is narrower than a complete frontend framework, making it useful for studying solver mechanics without simultaneously learning a parser or IR. Its interfaces parameterize nodes, methods, facts, values, and the interprocedural control-flow graph.

- **C1:** The IDE solver coordinates incoming edges, end summaries, and jump functions across worker threads. Synchronization requirements are visible in the implementation and annotations.
- **C2:** The generic solver consumes an ICFG and client flow/edge functions, allowing frontends and fact domains to vary independently.
- **C3:** Flow-function and edge-function caches, a worker executor, and ordered sets used to stabilize iteration during benchmarking expose concrete costs and engineering choices.

Entry point: [IDESolver.java](https://raw.githubusercontent.com/soot-oss/heros/master/src/heros/solver/IDESolver.java). Ordered iteration is not presented as a guarantee that every parallel execution is deterministic.

### 17. [pascal-lab/Tai-e](https://github.com/pascal-lab/Tai-e)

**Language / role:** Java; static-analysis framework centered on extensible pointer analysis.

Tai-e's plugin protocol is a clear example of extending an analysis while it is running. Plugins receive newly discovered points-to sets and call edges and can feed additional facts or edges back into the solver.

- **C1:** Reflection, implicit JVM entry points, exceptions, and framework entry models affect program coverage. The documentation explicitly warns that disabling implicit entries can make results unsound.
- **C2:** Solver/plugin callbacks support features such as taint analysis and library or framework modeling without replacing the pointer-analysis engine.
- **C3:** Configurable context sensitivity, selective string distinctions, and object merging expose targeted precision-versus-cost choices.

Entry point: [the pointer-analysis framework reference](https://tai-e.pascal-lab.net/docs/0.5.4/reference/en/pointer-analysis-framework.html). This is a versioned guide, so API names and options should be checked against the revision chosen for actual development.

### 18. [opalj/opal](https://github.com/opalj/opal)

**Language / role:** Scala; JVM bytecode analysis framework with abstract interpretation, TAC, and property computation.

OPAL is useful for tracing how multiple program representations share analysis infrastructure. The repository distinguishes generic static-analysis facilities, bytecode abstract interpretation, and three-address code with control-flow and def-use information.

- **C2:** The `OPAL/si`, `OPAL/ai`, and `OPAL/tac` layers provide reusable lattice/property facilities, an abstract interpreter, and analysis-friendly IR. Their separation supports multiple analysis styles within one framework.
- **C4:** The [change history](https://github.com/opalj/opal/blob/develop/Changes.md) documents releases from 2017 through 2025, Java-version and Scala migrations, property-framework testing, parallel property-store work, and fixes involving exception flow and strongly connected components. This is concrete evidence of evolution and complexity management, beyond project age.

Entry points: the [repository's module architecture](https://github.com/opalj/opal) and [Changes.md](https://github.com/opalj/opal/blob/develop/Changes.md). This entry counts the monorepo once.

### 19. [plast-lab/doop](https://github.com/plast-lab/doop)

**Language / role:** Datalog, Java, and Groovy; declarative pointer-analysis framework and orchestration infrastructure.

Doop is valuable for comparing declarative analysis logic with imperative solver frameworks. The developer guide separates analysis configuration and execution from the logic being evaluated, and exposes the mechanics of caching generated facts.

- **C2:** Core analysis construction, validation, and execution are separate from command-line handling and individual declarative analyses. This supports embedded clients as well as command-line experiments.
- **C3:** Analysis options indicate whether they alter facts, preprocessor settings, or cache identities. That makes cache reuse depend on explicit semantic inputs rather than only an output-directory convention.

Entry point: [the developer architecture and option-model guide](https://raw.githubusercontent.com/plast-lab/doop/master/docs/documentation.md). Some examples are historical. The [repository overview](https://github.com/plast-lab/doop) distinguishes the maintained Soufflé implementation from legacy, unmaintained LogicBlox support; these backends are not treated as equally current.

### 20. [typetools/checker-framework](https://github.com/typetools/checker-framework)

**Language / role:** Java; pluggable type checkers and reusable flow-analysis infrastructure.

The relevant subsystem is the generic dataflow engine underlying type refinement. Study how a framework exposes abstract values, stores, transfer functions, and per-node results while supporting many qualifier systems.

- **C1:** The API distinguishes regular and exceptional exit stores, results before and after nodes, and unreachable exits. Consumers must also respect whether analysis has finished before retrieving complete results.
- **C2:** `Analysis<V,S,T>` separates the abstract value, store, and transfer function and supports forward and backward analyses. The surrounding framework applies these abstractions across checkers rather than hard-coding one nullness lattice.

Entry point: [the Analysis API and its implementation relationships](https://checkerframework.org/api/org/checkerframework/dataflow/analysis/Analysis.html). The selection concerns reusable semantic analysis, not merely the presence of annotation syntax or a collection of style checks.

## Dynamic languages, Rust, and modular research frameworks

### 21. [cs-au-dk/TAJS](https://github.com/cs-au-dk/TAJS)

**Language / role:** Java; JavaScript type/value analysis by abstract interpretation. **Historical: archived on 2025-02-11 and identified as no longer maintained.**

TAJS remains useful for studying how an analyzer models a dynamic language and its host environment. Its special modeling functions expose abstract values and joins, coercions, context selection, asynchronous callbacks, and model-limit failures.

- **C1:** JavaScript host and conversion behavior requires semantic models. Explicit unsupported-model exceptions and assertions about abstract values make limitations and model validation inspectable.
- **C2:** The modeling API lets library models construct and combine abstract values and register behavior, providing reusable mechanisms beyond a fixed list of warnings.
- **C3:** Per-function context-sensitivity controls, including parameter- and caller-dependent choices, allow precision to be concentrated where it matters.

Entry point: [TAJS modeling functions](https://github.com/cs-au-dk/TAJS/blob/master/TAJS-functions.md). The repository describes primarily ECMAScript 3/5 support with partial accommodation of later language features; it should not be mistaken for complete contemporary JavaScript coverage.

### 22. [endorlabs/MIRAI](https://github.com/endorlabs/MIRAI)

**Language / role:** Rust; abstract interpretation of Rust MIR with contracts and procedure summaries.

MIRAI is instructive for combining symbolic expressions with numerical reasoning and bounded computation. Its architecture describes a path-to-value environment, alias-sensitive updates, on-demand numerical abstractions, and summary specialization.

- **C1:** Flattened field paths, aliasing, preconditions, postconditions, and side effects must retain their meaning when a summary is applied at a call.
- **C2:** Summaries separate reusable procedure effects from caller context; abstract values combine symbolic expressions, interval reasoning, tags, and SMT-backed checks.
- **C3:** Expression simplification, widening, cached summaries, and depth/size/time bounds address state explosion explicitly.

Entry point: [the architecture overview](https://raw.githubusercontent.com/endorlabs/MIRAI/main/documentation/Overview.md). A material limitation in that document is that incomplete calls can be treated as unreachable under default diagnostics, an unsound assumption; `--diag=verify` reports reachable incompleteness. Compiler-version compatibility is also a concern, and no current-toolchain build was attempted.

### 23. [softwarelanguageslab/maf](https://github.com/softwarelanguageslab/maf)

**Language / role:** Scala; modular abstract interpretation research framework for higher-order and concurrent languages.

MAF is useful for exploring analysis composition through traits and mixins. Its incremental machinery provides a substantive example of how reuse must be checked against whole-program recomputation.

- **C1:** The incremental-analysis documentation describes comparisons against fresh analysis, restart invariance, and checks against concrete execution; concurrent variants use multiple concrete runs. These are distinct checks on reuse and semantic coverage, not merely parser tests.
- **C2:** Semantics, abstract domains, sensitivity, and incremental behavior can be assembled as separate mixins. Documented configurations include big-step Scheme ModF and concurrent small-step ModConc.

Entry point: [incremental analysis architecture and tests](https://github.com/softwarelanguageslab/maf/blob/master/code/shared/src/main/scala/maf/modular/incremental/incrementalAnalysis.md). The document marks some worklist-order tests as disabled. The repository also warns that timeout results may not be sound until analysis finishes. Monarch, below, is the separately implemented successor identified by that project's documentation.

### 24. [softwarelanguageslab/monarch](https://github.com/softwarelanguageslab/monarch)

**Language / role:** Haskell; modular abstract definitional interpreters, succeeding MAF with a different implementation architecture.

Monarch treats domains, effects, and fixpoint strategies as composable components. Its monorepo separates domain, syntax, and analysis libraries; Scheme analysis is demonstrated, while the README describes more limited Python-facing command-line functionality.

- **C1:** Effect ordering changes semantics: composing failure and state in different orders determines whether state survives failure. The architecture makes this locality choice explicit rather than hiding it in one interpreter implementation.
- **C2:** Type classes specify semantic requirements, domain combinators assemble values, and `MonadLayer` supports effect composition. Different fixpoint strategies can drive the same intra-component analysis.
- **C3:** `MonadCache` derives cache keys and results from relevant effects, connecting memoization to the semantics of the chosen transformer stack.

Entry point: the [authors' architecture and implementation paper](https://soft.vub.ac.be/Publications/2025/vub-tr-soft-25-09.pdf), especially sections on effect layering, caching, and fixpoint construction. This is a research framework; no stable-API or production-readiness claim is made.

### 25. [cuplv/dai](https://github.com/cuplv/dai)

**Language / role:** OCaml; demand-driven, incremental abstract interpretation research implementation. **The README states that it is not actively maintained.**

DAI makes analysis computations explicit as a dependency graph so that edits and queries can share previous work. It is a useful smaller counterpart to broad industrial frameworks when studying incremental correctness.

- **C1:** Loop analysis preserves an acyclic dependency-graph invariant by representing abstract iterations explicitly. The authors give conditions for termination and agreement with from-scratch analysis; these are properties of the formalized method, not a blanket verification of repository code.
- **C2:** The implementation is parameterized by an abstract-domain interface; the paper demonstrates interval, octagon, and shape domains.
- **C3:** Eager invalidation combined with lazy recomputation avoids both unnecessary whole-program work and reuse of stale results; Adapton supplies auxiliary memoization.

Entry point: [the design and implementation paper](https://arxiv.org/html/2104.01270v2), sections 2, 5–7. The paper's prototype has restricted interprocedural semantics, and the README documents dependency drift and patched pins. No published latency figure is generalized to other workloads.

## Static analysis of binaries

### 26. [angr/angr](https://github.com/angr/angr)

**Language / role:** Python with native dependencies; binary-analysis framework. This entry concerns its **static CFG recovery and shared analysis representations**.

Angr is useful for studying analysis when source-level control flow is unavailable. CFG recovery must distinguish discovered facts from assumptions and revise the graph as more information becomes available.

- **C1:** Indirect jumps and uncertain returns complicate reconstruction. Provisional `FakeRet` edges are removed when analysis determines that a callee does not return, illustrating revision of earlier control-flow assumptions.
- **C2:** CFG nodes, function information, and graph representations are exposed to downstream analyses through the shared function manager and graph APIs.
- **C3:** `CFGFast` lifts blocks and explores statically determined successors, while `CFGEmulated` uses a more expensive state-based approach. The documentation explains their different costs and environment-model limitations.

Entry point: [the official CFG analysis guide](https://docs.angr.io/en/latest/analyses/cfg.html). The broader symbolic-execution and reverse-engineering platform is not being counted as uniformly static analysis.

### 27. [BinaryAnalysisPlatform/bap](https://github.com/BinaryAnalysisPlatform/bap)

**Language / role:** OCaml; binary-analysis framework with extensible machine semantics and analysis infrastructure.

BAP's Core Theory is valuable for studying how instruction lifters and analyses can share semantics without requiring every consumer to understand every machine operation. It exposes typed terms, effects, and different interpretations of the same semantic structure.

- **C1:** Bitvector widths, memory operations, floating-point sorts, and rounding modes carry correctness obligations that disappear in untyped instruction summaries. Core Theory distinguishes values from effects explicitly.
- **C2:** Extensible sublanguages and alternative interpretations let lifters and analyses target the semantic operations they need. This separates machine description from downstream analysis implementation.

Entry points: [Core Theory's architecture and API](https://binaryanalysisplatform.github.io/bap/api/master/bap-core-theory/Bap_core_theory/index.html) and the [framework API index](https://binaryanalysisplatform.github.io/bap/api/master/index.html). This selection highlights the static semantic framework; it does not claim that all plugins provide conservative or complete analyses.

## Coverage, search method, and limitations

Discovery used more than six distinct live-search formulations, including numerical domains and APRON alternatives; generic fixpoint libraries; LLVM pointer/value-flow and IFDS/IDE engines; JVM, Android, and declarative pointer analysis; JavaScript abstract interpretation; Rust MIR analysis; OCaml concurrency and incremental analysis; Scala/Haskell higher-order and definitional interpreters; Python-oriented framework searches; and static binary analysis. Follow-up searches targeted architecture documents, source interfaces, solver implementations, tests, and change histories. The final cross-language and demand-driven searches added Monarch and DAI; subsequent results increasingly overlapped these architectural families or led to more specialized alternatives. This is a curated selection, not an exhaustive inventory.

Every listed canonical GitHub repository page was opened, and at least one additional primary document, API reference, implementation file, test guide, or author design paper was read for each entry. Source entry points are supplied beside the corresponding claims. Repository stars were not used as quality evidence. C1–C4 assignments and suggested study value are grounded engineering judgments; the described interfaces and mechanisms are source-supported facts. C4 is used sparingly because testing or an old creation date alone does not establish sustained evolution.

Tutorials, awesome-lists, thin wrappers, routine forks, and tools centered solely on execution were excluded. Soot/SootUp and MAF/Monarch are deliberately separate because their primary documentation identifies substantial new implementations. LLVM and other monorepos count once. [Mopsa's official project](https://gitlab.com/mopsa/mopsa-analyzer) is hosted on GitLab; this search did not establish a qualifying official substantive GitHub mirror, so it was not retained. The same GitHub-verification requirement limited coverage of other non-GitHub ecosystems. C/C++ and JVM infrastructure is more heavily represented than Python-specific frameworks.

TAJS is explicitly historical, DAI reports that it is not actively maintained, and CPAchecker is explicitly a mirror. Other entries are not blanket assertions of active maintenance. Some useful design guides are older or versioned, particularly WALA, Doop, and Tai-e; links to moving branches may change. Several attempted source URLs could not be fetched and were replaced by accessible primary sources. No repositories were cloned, dependencies installed, candidate code executed, or performance measurements reproduced. Soundness depends on frontend coverage, semantic models, client analyses, configuration, and successful convergence; the per-project limitations above are part of the selection guidance.
