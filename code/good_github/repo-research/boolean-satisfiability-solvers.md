# Boolean satisfiability solvers

Research date: 2026-10-09.

This is a selection of 25 substantive GitHub codebases for studying Boolean SAT implementation: complete CDCL engines, lookahead and cube-and-conquer, parallel and distributed solving, GPU inprocessing, formally verified solvers, and incomplete local search. Libraries and larger repositories are included only where they contain a substantial SAT implementation or SAT execution architecture; the relevant subsystem is identified. The breadth warrants more entries than a small solver shortlist. These are engineering study recommendations, not performance rankings or a claim that every component is exemplary.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and structures supporting different applications.
- **C3 — Performance:** concrete resource constraints addressed through an understandable implementation architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or complexity management; age alone does not qualify.

All repository identities and default branches were checked through GitHub repository pages or the GitHub API. None of the selected repositories was marked archived at the research date. Historical references are identified below; absence of an archive flag is not a maintenance guarantee. Criteria assessments and suggestions about what to study are grounded engineering judgments based on the linked primary sources. Source links use the inspected branches and may change subsequently.

## Sequential CDCL engines and their design lineages

### 1. [arminbiere/cadical](https://github.com/arminbiere/cadical)

**C++; embeddable incremental CDCL solver.** Particularly useful for studying the contract between an optimizing solver and its callers. The public header specifies legal states and transitions for clause addition, assumptions, solving, model access, and termination, rather than leaving these rules implicit.

- **C1:** The API makes asynchronous termination and state-dependent operations explicit. Its test documentation describes API tests, CNF tests that check models and proofs, trace replay, and model-based testing with `mobical`. [API contract](https://github.com/arminbiere/cadical/blob/master/src/cadical.hpp), [testing guide](https://github.com/arminbiere/cadical/blob/master/test/README.md).
- **C2:** IPASIR-compatible incremental operations, failed assumptions, and external propagators support integration into larger reasoning systems. The [change history](https://github.com/arminbiere/cadical/blob/master/NEWS.md) explains the particularly instructive problem of keeping user variables distinct from internally introduced extension variables and the resulting API migration.

Start with the API header and testing guide above. This is a good choice for learning how aggressive internal transformations affect public semantics.

### 2. [arminbiere/kissat](https://github.com/arminbiere/kissat)

**C; performance-focused CDCL and inprocessing engine.** A substantive reimplementation of CaDiCaL in C, not a packaging fork. Study how compact representations and simplification scheduling interact.

- **C1:** Watch records distinguish binary literals, blocking literals, and references to large clauses. Iterators depend on whether the solver is currently watching or connecting clauses, with assertions enforcing the representation mode. [Watch implementation](https://github.com/arminbiere/kissat/blob/master/src/watch.h).
- **C3:** The same implementation packs tagged watches into unsigned-sized records. The [engineering history](https://github.com/arminbiere/kissat/blob/master/NEWS.md) documents removal of a quadratic gate-extraction issue, delayed bounded variable addition for large formulas, and the deliberate removal of marginal features in the `sc2022-light` version to reduce complexity.

Start with `src/watch.h` and `NEWS.md`. The latter is unusually useful for understanding why an optimized solver sometimes becomes smaller before acquiring new techniques.

### 3. [niklasso/minisat](https://github.com/niklasso/minisat)

**C++; compact, foundational CDCL implementation.** A historical reference whose value is the visibility of the complete solving loop and its invariants, rather than a claim of current competitive leadership.

- **C1:** `analyze` documents the asserting literal and backtrack-level postconditions; clause deletion protects locked reason clauses; relocation updates watchers and assignment reasons. These are concrete examples of logical correctness depending on memory-management correctness. [Solver implementation](https://github.com/niklasso/minisat/blob/master/minisat/core/Solver.cc).
- **C3:** Blocking literals avoid unnecessary clause inspection, clause references support arena allocation, and learned-clause reduction controls memory growth. These mechanisms sit in the same readable implementation, making their interactions easy to trace.

Start with [the core solver](https://github.com/niklasso/minisat/blob/master/minisat/core/Solver.cc). Read propagation, conflict analysis, database reduction, and relocation together; studying only the search loop misses much of the engineering.

### 4. [audemard/glucose](https://github.com/audemard/glucose)

**C++; MiniSat-derived sequential and parallel solver.** Retained separately because its learned-clause quality measures, restart policy, and parallel evolution constitute substantive solver design.

- **C1:** Database reduction preserves binary and locked clauses and temporarily protects selected clauses from deletion. These rules maintain usable reasons while pruning the search database. [Core implementation](https://github.com/audemard/glucose/blob/main/core/Solver.cc).
- **C3:** LBD-based ordering, clause activity, moving averages, and reactive reduction thresholds provide a concrete study of selecting useful learned information under memory and propagation costs. The implementation exposes these policies rather than hiding them behind an opaque backend.

Start with `core/Solver.cc`, especially `reduceDB`, and the [project description](https://github.com/audemard/glucose/blob/main/README.md). The README flags discrepancies with the `-rcheck` preprocessing option and distinguishes sequential certification/incrementality from parallel capabilities; those combinations should not be assumed interchangeable.

### 5. [msoos/cryptominisat](https://github.com/msoos/cryptominisat)

**C++, with language interfaces; incremental SAT with native XOR reasoning.** A strong reference for combining ordinary clausal search with algebraic reasoning over parity constraints.

- **C1:** The Gaussian subsystem maintains mappings between solver variables and matrix columns, coordinates with replaced variables and assumptions, and participates in proof logging. Correctness spans both Boolean propagation and matrix transformations. [Gaussian implementation](https://github.com/msoos/cryptominisat/blob/master/src/gaussian.cpp).
- **C2:** The repository provides command-line, C++, and Python use with assumptions and repeated solving, allowing the same XOR-capable engine to serve multiple applications. Its [verification guide](https://github.com/msoos/cryptominisat/blob/master/README_VERIFIER.md) describes FRAT-to-XLRUP elaboration, independent checking, and how to trace a rejected proof step back to the responsible solver function.

Start with the Gaussian subsystem and verification guide. The distinctive lesson is the interface between specialized inference and independently checkable evidence, not merely another CDCL heuristic collection.

### 6. [arminbiere/lingeling](https://github.com/arminbiere/lingeling)

**C; historical inprocessing solver family.** The repository contains Lingeling, its parallel form Plingeling, and the Treengeling/Ilingeling cube-and-conquer variants. Treat these as one codebase, as the [repository documentation](https://github.com/arminbiere/lingeling/blob/master/README) does.

- **C1:** The API explains why eliminated or unfrozen variables cannot simply be reused in later incremental calls. Its clone/fork/join contracts also distinguish copying a solver from changing variable namespaces and reconstructing a parent model. [Library contract](https://github.com/arminbiere/lingeling/blob/master/lglib.h).
- **C2:** Custom memory management, cloning, lookahead, termination callbacks, and clause/unit exchange callbacks form a reusable integration layer for multiple execution strategies. The contracts expose important limitations, including restrictions between fork and join.

Start with `lglib.h`, then inspect the substantial [solver implementation](https://github.com/arminbiere/lingeling/blob/master/lglib.c). This is a denser historical design than CaDiCaL, useful for understanding why later solvers pursued simpler internals.

## Parallel, distributed, GPU, and partitioned solving

### 7. [arminbiere/gimsatul](https://github.com/arminbiere/gimsatul)

**C; shared-memory portfolio SAT solver.** Its key architectural choice is physically sharing immutable large clauses while keeping each thread's watchers separate.

- **C1:** Atomic reference counts govern shared-clause lifetime and final proof deletion. Global simplification requires synchronization, while some inprocessing remains local to solver threads. [Architecture description](https://github.com/arminbiere/gimsatul/blob/master/README.md), [clause lifetime implementation](https://github.com/arminbiere/gimsatul/blob/master/clause.c).
- **C3:** Physical sharing reduces duplication of large clauses and proof entries. Binary clauses have a separate representation, and exchange prioritizes low-glue learned clauses. These choices make memory traffic, sharing policy, and proof size visible architectural concerns.

Start with the README's sharing/proof sections and `clause.c`. It is especially valuable for comparing shared immutable data with the copy-and-exchange architecture of other portfolios.

### 8. [domschrei/mallob](https://github.com/domschrei/mallob)

**C++ and MPI; distributed reasoning platform, specifically MallobSat.** Counted once despite additional MaxSAT and SMT engines. The SAT subsystem combines solver portfolios with decentralized scheduling and incremental jobs. [Project overview](https://github.com/domschrei/mallob/blob/master/README.md).

- **C1:** Its development guide explicitly confines MPI communication to each process's main thread; solver callbacks must enqueue requests instead. It also documents failures involving unresponsive nodes, assertions, logging, and the interaction of threads and processes. [Development architecture](https://github.com/domschrei/mallob/blob/master/docs/develop.md).
- **C2:** `PortfolioSolverInterface` separates sequential solver adapters from the execution engine, while application interfaces separate job management from the reasoning task. This supports a study of extending a SAT service without entangling solver internals with scheduling.

Start with the overview and development guide. The guide candidly notes that safe logging is not yet implemented uniformly, making this a useful distributed-systems study rather than a blanket reliability endorsement.

### 9. [lip6/painless](https://github.com/lip6/painless)

**C++ and MPI; framework for parallel and distributed SAT portfolios.** The reusable implementation is in solver interfaces, workers, clause containers, and sharing strategies; bundled sequential solvers are not counted again as new projects.

- **C1:** Clause exchange crosses smart-pointer and raw-pointer boundaries. The documentation explains reference ownership on successful and failed queue pushes, atomic size tracking, and multi-producer/multi-consumer operation. [Clause-management design](https://github.com/lip6/painless/blob/master/docs/source/ClauseManagement.md).
- **C3:** Flexible-sized clause allocation, intrusive reference counts, lock-free queues, and bounded insertion address allocation and sharing pressure directly. The [project structure](https://github.com/lip6/painless) separates these mechanisms from portfolio composition and preprocessing.

Start with `ClauseManagement.md` and the [experiment guide](https://github.com/lip6/painless/blob/master/docs/source/TACAS25.md), which exposes the sharing configurations and acknowledges crashed instances in the evaluation setup.

### 10. [muhos/ParaFROST](https://github.com/muhos/ParaFROST)

**C++/CUDA; CDCL with GPU-accelerated pre- and inprocessing.** This is a solver implementation with its own search engine, not simply a GPU wrapper around a CPU executable.

- **C1:** The simplification controller coordinates propagation state, variable elimination, host/device clause transfer, CUDA stream synchronization, proof buffers, and allocation-failure recovery. [GPU simplification implementation](https://github.com/muhos/ParaFROST/blob/master/src/gpu/simplify.cu).
- **C3:** Clause extraction and reflection use separate streams, and GPU simplification is organized into explicit reduction phases. The current [README](https://github.com/muhos/ParaFROST/blob/master/README.md) explains a cuArena pool with stable and dynamic regions to reduce repeated driver allocation overhead; cuArena is currently required for the GPU build.

Start with the README's memory-backend discussion and `src/gpu/simplify.cu`. This is a particularly different performance architecture from CPU-only portfolios; no numerical speedup is inferred here.

### 11. [marijnheule/CnC](https://github.com/marijnheule/CnC)

**C/C++ and shell; March lookahead plus incremental conquer solvers.** A historical research implementation of cube-and-conquer. Its bundled Glucose and Lingeling versions are older, explicitly named versions, not current upstream engines. [Project description](https://github.com/marijnheule/CnC/blob/master/README.md).

- **C1:** The cube representation records a decision tree, closes a node when both children are refuted, and emits assumption paths. Correct decomposition and branch accounting are central to obtaining a valid global answer. [Cube implementation](https://github.com/marijnheule/CnC/blob/master/march_cu/cube.c).
- **C3:** Lookahead has separate propagation paths for 3-SAT/general clauses and optional equivalence handling; cutoff depth, remaining variables, and cube count control the partitioning cost. [Lookahead implementation](https://github.com/marijnheule/CnC/blob/master/march_cu/lookahead.c).

Start with `cube.c` and `lookahead.c`. The independent contribution is March and the decomposition/conquer protocol, not the vendored solver copies.

## Native implementations and reusable solver libraries

### 12. [jix/varisat](https://github.com/jix/varisat)

**Rust; incremental CDCL solver and proof infrastructure.** A historical reference: repository metadata showed the last push in 2022, so current maintenance is not assumed.

- **C1:** The solver distinguishes interruption, unrecoverable errors, unconditional UNSAT, and UNSAT under assumptions. Proof handling maps solver variables to global names and supports checking during solving, including incremental clause additions. [Solver API implementation](https://github.com/jix/varisat/blob/master/varisat/src/solver.rs), [proof subsystem](https://github.com/jix/varisat/blob/master/varisat/src/proof.rs).
- **C2:** Formula extension, assumptions, failed cores, selectable proof formats, and proof processors make the library reusable beyond a single DIMACS command. The proof subsystem explicitly separates generation, checking, mapping, and output buffering.

Start with these two files. The failed-core API explicitly does not promise a minimal core; this is an example of a useful semantic limitation being documented at the interface.

### 13. [shnarazk/splr](https://github.com/shnarazk/splr)

**Rust; deterministic CDCL with substantial preprocessing and heuristic experimentation.** Offers a different Rust design from Varisat: assignment state, clause database, and global state are composed through explicit interfaces.

- **C1:** The search engine checks clause-database capacity, distinguishes out-of-memory errors from UNSAT, and records certificates for transformations. Comments explain ordering constraints such as constructing occurrence information before assigning phases. [Search implementation](https://github.com/shnarazk/splr/blob/main/src/solver/search.rs).
- **C3:** The solver combines vivification, elimination, trail saving, branching-policy changes, and staged restarts. Their scheduling is visible in the search engine, with the [README](https://github.com/shnarazk/splr/blob/main/README.md) describing model and DRAT validation of benchmark results.

Start with the search implementation and README. A material API limitation: the README says incremental mode was removed as of version 0.18.0; older descriptions should not be used to infer current support.

### 14. [c-cube/batsat](https://github.com/c-cube/batsat)

**Rust; MiniSat-lineage solver parameterized by a theory.** Derived from Ratsat, but retained for substantial separate evolution: theory callbacks, proof output, assumption cores, and embedding interfaces. [Project goals and implementation status](https://github.com/c-cube/batsat/blob/main/README.md).

- **C1:** The `Theory` contract requires a final model check to produce a valid conflict lemma when a candidate is invalid. It distinguishes optional partial checking from mandatory final checking and requires explanations for theory propagation. [Theory interface](https://github.com/c-cube/batsat/blob/main/src/batsat/src/theory.rs).
- **C2:** Explicit level creation/popping and a trivial empty theory let the same SAT core support ordinary propositional solving or domain-specific reasoning. This is a useful example of a solver extension point whose correctness obligations remain visible.

Start with `theory.rs` and the README. The README still lists testing of its IPASIR interface as unfinished; implemented interfaces and validated interfaces should not be conflated.

### 15. [go-air/gini](https://github.com/go-air/gini)

**Go; SAT solver with circuit modeling and asynchronous execution.** A historical integration reference: GitHub metadata showed its last push in 2021. Downstream forks were not counted separately.

- **C1:** Copying deliberately excludes execution-control mechanisms, and assumptions, test scopes, result access, and cancellation have distinct contracts. The manual restricts solve-time copying to a paused solver. [Public implementation](https://github.com/go-air/gini/blob/master/gini.go), [manual](https://github.com/go-air/gini/blob/master/docs/manual.md).
- **C2:** And-inverter graphs, sequential-circuit unrolling, sorting-network cardinality constraints, assumption exchange, and the CRISP client/server protocol provide substantial abstractions around the native SAT core.

Start with `gini.go` and the manual's concurrency section. Proposed future protocol extensions or clause sharing in the manual are not treated as implemented features.

### 16. [crillab/gophersat](https://github.com/crillab/gophersat)

**Go; native SAT and pseudo-Boolean solver.** Worth studying for how one solver library supports ordinary clauses, cardinality constraints, and weighted constraints without a foreign-language backend.

- **C1:** Watch registration has distinct cases for propositional, binary, cardinality, and pseudo-Boolean constraints. Weighted watching maintains a threshold derived from constraint weights, making generalization of the usual two-watch invariant concrete. [Watcher implementation](https://github.com/crillab/gophersat/blob/master/solver/watcher.go).
- **C2:** The [project documentation](https://github.com/crillab/gophersat) describes decision/optimization APIs, model delivery through channels, incremental solving, and separate explanation facilities. It explicitly limits current UNSAT certification/MUS facilities to pure SAT rather than all supported constraint types.

Start with the watcher implementation and [solver source tree](https://github.com/crillab/gophersat/tree/master/solver), which includes dedicated clause, cardinality, pseudo-Boolean, and optimization tests.

### 17. [Gbury/mSAT](https://github.com/Gbury/mSAT)

**OCaml; modular SAT core with theory extensions and proof output.** The ready-to-use `Msat_sat` subsystem establishes direct SAT category fit; the theory machinery is an extension of that implementation. [Usage and architecture](https://github.com/Gbury/mSAT/blob/master/README.md).

- **C1:** Propagation reasons carry a specific invariant: their antecedents must be true on the current trail. Deferred explanations must remain safe under conservative trail extensions; the interface explains when eager explanation is preferable. [Solver interface](https://github.com/Gbury/mSAT/blob/master/src/core/Solver_intf.ml).
- **C2:** Functorized formula/theory representations, SAT/UNSAT result structures, persistent proofs, assumption cores, and a separate Tseitin formula layer support multiple embeddings. Generative modules address mutable solver-state separation explicitly.

Start with `Solver_intf.ml` and the README's SAT example. The most instructive abstraction is the boundary between inexpensive lazy explanations and the state needed to justify them.

### 18. [imandra-ai/minisat-ml](https://github.com/imandra-ai/minisat-ml)

**OCaml; historical native reimplementation and performance study.** Retained as a substantive language/runtime port, not a binding or another copy of MiniSat. Repository metadata showed the last push in 2023.

- **C1:** The implementation study shows how MiniSat's trail traversal and conflict analysis are translated into OCaml's control flow and private integer-based types. Preserving decision/trail relationships while changing representation is the central correctness problem.
- **C3:** The report explains a structure-of-arrays watch representation to avoid many small allocations, word-sized integer costs, functorized heaps, and inlining choices. It also states benchmark methodology and its historical compiler configuration. [Technical report](https://github.com/imandra-ai/minisat-ml/blob/master/docs/tech_report.md).

Start with the technical report and the [implementation tree](https://github.com/imandra-ai/minisat-ml/tree/master/src). Its old benchmark results should be read as evidence for design tradeoffs, not a prediction about present-day language performance.

### 19. [msakai/toysolver](https://github.com/msakai/toysolver)

**Haskell; specifically the `toysat` and `ToySolver.SAT` subsystems.** Despite the sandbox name, this contains a substantial native CDCL engine, not a tutorial or merely a launcher for another solver. The broader arithmetic/SMT components are outside this entry's scope. [Repository overview](https://github.com/msakai/toysolver/blob/master/README.md).

- **C2:** The CDCL API supports clauses, cardinality, pseudo-Boolean and XOR constraints, assumptions, failed assumptions, theory integration, budgets, cancellation, and callbacks. These are reusable solver abstractions rather than a fixed demonstration problem.
- **C3:** Packed literals, mutable unboxed arrays, strict evaluation, indexed priority queues, and selectable extra bounds checking expose how a Haskell solver manages allocation and hot-loop costs. [CDCL implementation](https://github.com/msakai/toysolver/blob/master/src/ToySolver/SAT/Solver/CDCL.hs).

Start with the CDCL implementation and [SAT source tree](https://github.com/msakai/toysolver/tree/master/src/ToySolver/SAT). The module itself labels portability and stability limitations, so native implementation should not be mistaken for portability across all Haskell systems.

## Formal verification as an implementation method

### 20. [IsaFoL/IsaFoL](https://github.com/IsaFoL/IsaFoL)

**Isabelle/HOL with LLVM-oriented refinement; specifically `Weidenbach_Book/IsaSAT`.** This monorepo is counted once and only its SAT development is recommended here. The [author's project page](https://m-fleury.github.io/isasat/) describes synthesizing the solver through the Isabelle Refinement Framework.

- **C1:** Propagation refinements carry explicit assertions about valid arena clause indices, trail state, and bounded machine-word representations. The proof source connects executable operations to their abstract specifications. [Inner-propagation refinement](https://github.com/IsaFoL/IsaFoL/blob/master/Weidenbach_Book/IsaSAT/IsaSAT_Inner_Propagation_LLVM.thy).
- **C3:** The implementation refines arenas, watched literals, saved search positions, and word-level operations instead of stopping at an abstract DPLL proof. The [IsaSAT source tree](https://github.com/IsaFoL/IsaFoL/tree/master/Weidenbach_Book/IsaSAT) separates logical definitions, proofs, and LLVM-oriented implementations for the solver components.

Start with that tree and the propagation refinement. This is a study of making optimized representations provable, with a substantially steeper prerequisite burden than the conventional C/C++ entries.

### 21. [sarsko/CreuSAT](https://github.com/sarsko/CreuSAT)

**Rust and Creusot specifications; specifically the `CreuSAT` solver.** A complementary route to IsaSAT: contracts are attached to imperative Rust rather than beginning with Isabelle refinement.

- **C1:** The solver specifies formula/trail/watch invariants, equisatisfiable clause extensions, index bounds, and preservation conditions across learned-clause insertion and backtracking. [Annotated solver](https://github.com/sarsko/CreuSAT/blob/master/CreuSAT/src/solver.rs).
- **C3:** Its [documented implementation](https://github.com/sarsko/CreuSAT/blob/master/README.md) includes blocking watched literals, circular search, VMTF, phase saving, EMA restarts, and clause deletion, making it useful for studying verification obligations around practical optimizations.

Start with the annotated solver and README. Limitations matter: the source has optional trusted configurations, the README marks the Cargo Make proof workflow broken, and clause deletion is documented without garbage collection. This report does not independently certify the current tree or every build configuration.

## Stochastic local search

These entries search for satisfying assignments. Failure to find one within a budget is not a general proof of UNSAT; they serve a different role from complete CDCL solvers.

### 22. [arminbiere/yalsat](https://github.com/arminbiere/yalsat)

**C; local-search library and sequential/parallel executables.** Useful for seeing how a stochastic algorithm becomes an embeddable solver with resource control. The [README](https://github.com/arminbiere/yalsat/blob/master/README.md) identifies the library, `yalsat`, and multithreaded `palsat`.

- **C1:** The implementation updates satisfaction counts, critical literals, and weighted break scores together; a debug global-invariant checker recomputes clause satisfaction to catch divergence. [Local-search engine](https://github.com/arminbiere/yalsat/blob/master/yals.c).
- **C3:** It selects compact counter widths, caches assignments for restarts, and maintains specialized unsatisfied-clause structures. Its [API](https://github.com/arminbiere/yalsat/blob/master/yals.h) exposes flip/memory-operation budgets, custom allocators, termination, and message-lock callbacks.

Start with `yals.c` and `yals.h`. It is a useful contrast to clause-learning engines because performance depends on efficient incremental score maintenance after each flip.

### 23. [adrianopolus/probSAT](https://github.com/adrianopolus/probSAT)

**C; historical stochastic local-search reference implementation.** A compact but substantive algorithm implementation associated with the authors' probability-distribution research; it intentionally uses break values without tracking make values. [Project description](https://github.com/adrianopolus/probSAT/blob/master/README.md). Repository metadata showed the last push in 2022.

- **C1:** A flip must consistently update true-literal counts, the unsatisfied-clause list, its inverse index, and cached break information. A separate assignment checker verifies a candidate against the clauses. [Implementation](https://github.com/adrianopolus/probSAT/blob/master/probSAT.c).
- **C3:** Cached and noncached flip implementations make a concrete time/space tradeoff visible, while probability lookup tables avoid recomputing scoring functions in the inner loop.

Start with `probSAT.c`, particularly `pickAndFlipNC`, `pickAndFlip`, and `checkAssignment`. Its global-state design and fixed maximum clause-length constant make it more appropriate as an algorithm study than a general-purpose embedding recommendation.

## SAT engines within broader Boolean reasoning libraries

### 24. [potassco/clasp](https://github.com/potassco/clasp)

**C++; conflict-driven nogood learning engine with direct SAT support.** Although developed for answer-set solving, clasp explicitly accepts DIMACS and functions as a SAT/PB solver and C++ library. This entry concerns that engine, not an assertion that ASP and SAT have identical semantics. [Project scope](https://github.com/potassco/clasp/blob/master/README.md).

- **C1:** The solver separates the root level for assumptions from the backtrack level for enumeration; the latter constrains backjumping to avoid repeated solutions. [Solver contract](https://github.com/potassco/clasp/blob/master/clasp/solver.h).
- **C2:** The same engine exposes incremental search, enumeration, optimization, strategies, and shared-context integration.
- **C4:** The dated [change history](https://github.com/potassco/clasp/blob/master/CHANGES) spans multiple years of compiler compatibility, tests with threading disabled, overflow handling, incremental solving fixes, and a work-splitting race correction. This is concrete sustained complexity management, not an inference from repository age.

Start with `clasp/solver.h` and `CHANGES` to connect public search semantics with the failure modes discovered over time.

### 25. [logic-ng/LogicNG](https://github.com/logic-ng/LogicNG)

**Java; Boolean reasoning library containing native SAT engines.** The relevant subsystem is `org.logicng.solvers`, including Java implementations of MiniSat/Glucose-style solving. Formula factories and transformations make it more substantial than a solver binding. [Repository description](https://github.com/logic-ng/LogicNG/blob/master/README.md).

- **C1:** The wrapper invalidates cached results and transformation state when restoring solver state. The native engine also disables a clause simplification when proof generation would make it invalid. [Solver state management](https://github.com/logic-ng/LogicNG/blob/master/src/main/java/org/logicng/solvers/MiniSat.java), [native engine](https://github.com/logic-ng/LogicNG/blob/master/src/main/java/org/logicng/solvers/sat/MiniSat2Solver.java).
- **C2:** Formula factories, cardinality encoders, solver functions, and state snapshots create a reusable application-facing layer over actual solver implementations.
- **C4:** The dated [changelog](https://github.com/logic-ng/LogicNG/blob/master/CHANGELOG.md) documents the 2024 split of parser artifacts to manage Java/ANTLR compatibility, followed by 2026 proof-edge-case fixes and a map change whose ordering consequences are explicitly described.

Start with `MiniSat.java` and `MiniSat2Solver.java`. Study the boundary between user-visible formula/state objects and the lower-level engine, where apparently harmless caching decisions can affect solver semantics.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations. The searches covered established CDCL and XOR solvers; parallel clause sharing and MPI portfolios; Rust-native solvers; Go and Java libraries; Isabelle/Creusot verification; stochastic local search; OCaml and Haskell implementations; GPU acceleration; lookahead/cube-and-conquer; and Scala/.NET alternatives. Follow-up searches increasingly returned the already-inspected lineages, wrappers, teaching projects, or broader SMT tools. Later useful discoveries—ParaFROST, ToySolver, and the official March/CnC code—were inspected rather than excluded merely because a target count had been reached.

For every retained repository, the canonical GitHub identity was checked and at least one additional primary implementation or architectural source was opened. Metadata, README files, source files, API contracts, testing guides, and changelogs were read; search snippets were used for discovery, not as sole verification. The report counts each monorepo once and does not double-count vendored solver copies. MiniSat-derived projects are retained only for explained implementation differences, native-language reimplementation, or substantial separate architecture.

Important exclusions and boundaries:

- **SAT4J:** its [official site](https://www.sat4j.org/) links source development to OW2 GitLab. No official substantive GitHub mirror was established, so unofficial copies were not substituted.
- **Bindings/toolkits:** PySAT, RustSAT, and language wrappers were not added merely for exposing external engines. They can be valuable infrastructure, but the selection emphasizes solver implementations and execution architectures.
- **Adjacent domains:** general SMT solvers, MaxSAT-only optimizers, model counters, proof-checker-only repositories, benchmark collections, and neural predictors without a sufficiently established solver implementation were outside the main selection. Clasp, LogicNG, mSAT, and ToySolver were included only because direct native SAT subsystems were verified.
- **Research snapshots:** competition bundles and minor heuristic forks were generally omitted when their independent contribution or architecture was harder to establish than the selected alternatives. Educational implementations and incomplete GPU experiments were not used to pad language or hardware coverage.
- **Verification limits:** this was read-only source research. No candidate code was installed, compiled, benchmarked, or formally reverified. A project's documented tests or proofs are evidence of its engineering approach, not a test result produced by this research. Recent pushes are not used to award C4, and historical benchmarks are not treated as current performance comparisons.
