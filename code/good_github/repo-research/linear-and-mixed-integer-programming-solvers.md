# Linear and mixed-integer programming solvers

Research date: 2026-10-09.

This guide selects 25 GitHub repositories containing substantial LP/MILP solving implementations or frameworks that implement the search and decomposition algorithms of specialized MILP solvers. It covers simplex, exact rational solving, interior-point methods, first-order GPU methods, parallel branch-and-bound, and decomposition. Modeling languages, bindings alone, commercial solver example collections, and general nonlinear/conic solvers are outside the selection. Repository identity and archive status were checked against GitHub; the sources below were read, including implementation material beyond repository introductions. Inclusion identifies useful engineering study material, not a correctness certification or a uniform recommendation for production use.

**Criteria legend**

- **C1 — Correctness:** difficult numerical semantics, invariants, concurrency, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and representations supporting multiple applications or algorithms.
- **C3 — Performance and structure:** concrete computational or memory constraints addressed through an understandable architecture.
- **C4 — Evolution:** documented development across years, together with compatibility work, testing, or complexity management.

The criterion assessments are grounded engineering judgments drawn from the linked primary evidence. Performance mechanisms are described without adopting unverified speedup claims. Unless stated otherwise, an unarchived repository is not being represented as having a particular maintenance cadence.

## General-purpose LP and MILP engines

### 1. [ERGO-Code/HiGHS](https://github.com/ERGO-Code/HiGHS)

**Language/role:** C++ with some C; sparse LP and MILP engine, also supporting convex QP. Study how a common model and solver interface accommodates revised simplex, interior-point solving, and a substantial MIP search implementation.

- **C1:** MIP state explicitly distinguishes lower and upper bounds, incumbents, feasibility tolerances, domain propagation, and the transformation of integer solutions back through presolve. These are concrete boundaries at which an apparently good solution or bound can become invalid.
- **C2/C3:** The MIP orchestration separates LP relaxations, cut pools, conflict pools, domains, pseudocosts, node queues, heuristics, and workers. Per-worker collections and explicit parallel coordination expose how the solver combines reusable components with parallel search. Start with the verified [MIP solver state and orchestration interface](https://raw.githubusercontent.com/ERGO-Code/HiGHS/master/highs/mip/HighsMipSolverData.h).

### 2. [scipopt/scip](https://github.com/scipopt/scip)

**Language/role:** Primarily C; constraint integer programming framework and MILP/MINLP solver. **Official read-only GitHub mirror** of the ZIB-hosted repository, as stated in its introduction. Its distinctive study value is the contract between the solving engine and problem-specific plugins.

- **C1:** Constraint handlers must distinguish checking a solution, enforcing an LP or pseudo solution, separating cuts, and propagating domains. The callback documentation describes which results are legal and when presolve initialization/deinitialization still runs even if presolving is disabled.
- **C2:** Constraint-type data and handler data are opaque extension points, with lifecycle, copying, presolving, separation, and enforcement callbacks. This lets application-specific constraints participate in the same search machinery. Read the extensive contracts in [type_cons.h](https://raw.githubusercontent.com/scipopt/scip/master/src/scip/type_cons.h); they are more informative than a list of supported constraint types.

### 3. [coin-or/Cbc](https://github.com/coin-or/Cbc)

**Language/role:** C++; general MILP branch-and-cut solver, usable as a library or executable. Study the integration boundary among a search controller, LP solver, cut generators, and heuristics.

- **C1:** Integer tolerances, cutoff comparisons, integer presolve, and reconstruction of the original model are explicit concerns in [CbcModel.hpp](https://raw.githubusercontent.com/coin-or/Cbc/master/src/CbcModel.hpp). The repository's release history also records a particularly instructive failure: stopping Clp at a time limit caused later cleanup solves to stop prematurely and return wrong results.
- **C2:** `CbcModel` coordinates Osi solver interfaces, Cgl cut generators, branching objects, strategies, heuristics, and event handlers rather than embedding one application formulation. The [repository changelog](https://github.com/coin-or/Cbc#changelog) documents interface and build changes, plus fixes to cloning, MIP starts after presolve, and unit-test execution. This is useful evidence of complexity management, without treating unreleased “3.0” notes as a released version.

### 4. [coin-or/Clp](https://github.com/coin-or/Clp)

**Language/role:** C++; LP solver with primal/dual simplex and a barrier method. Particularly useful for studying an LP relaxation engine that other MILP solvers can repeatedly call.

- **C1:** The [ClpSimplex interface](https://raw.githubusercontent.com/coin-or/Clp/master/src/ClpSimplex.hpp) exposes primal/dual infeasibility cleanup, basis and factorization reuse, tolerances, and distinctions between initial solves and subsequent solves. Correct reuse requires more than retaining the previous variable values.
- **C2/C3:** Matrix storage and pivot selection are replaceable: the repository documents sparse, network, and 0–1 matrix representations, along with user-provided primal/dual pivot rules. The same interface provides options to retain work areas and factorization between solves. Read the [solver overview](https://github.com/coin-or/Clp#clp) alongside the interface to connect these extension points with reoptimization costs.

### 5. [scipopt/soplex](https://github.com/scipopt/soplex)

**Language/role:** C++; revised-simplex LP solver with floating-point, higher-precision, and exact rational facilities. **Official read-only GitHub mirror** of the ZIB repository. This is a strong entry point for studying the boundary between approximate optimization and exact answers.

- **C1/C2:** Separate real and rational model access, explicit synchronization, rational factorization, and templated arithmetic make numerical representation part of the architecture. Inspect [soplex.h](https://raw.githubusercontent.com/scipopt/soplex/master/src/soplex.h), including model synchronization and rational solution access.
- **C4:** The dated [CHANGELOG](https://github.com/scipopt/soplex/blob/master/CHANGELOG) connects evolution with numerical and compatibility work: 2024 introduced precision boosting, centralized tolerances, additional C-interface functions, and LP tests; 2026 fixes include treating rational singularity as an iterative-refinement failure to guarantee termination. This is stronger evidence than repository age alone.

### 6. [google/or-tools](https://github.com/google/or-tools)

**Language/role:** C++ core with multiple language interfaces; counted once for the **GLOP and PDLP LP solvers** and related integer-solving infrastructure. The repository also contains routing and constraint programming, which are outside this entry's focus. Its generic MIP interfaces can call external solvers; those wrappers are not the reason for inclusion.

- **C1:** GLOP documents basis/status consistency, error correction only after refactorization, precision-triggered refactorization, and the effects of objective scaling on termination. The detailed [revised_simplex.h](https://raw.githubusercontent.com/google/or-tools/stable/ortools/glop/revised_simplex.h) is an unusually readable numerical-state contract.
- **C2/C3:** That interface decomposes simplex into basis factorization, reduced costs, entering-variable selection, edge norms, and variable-value maintenance, with compact sparse storage and incremental-change detection. The [repository code map](https://github.com/google/or-tools#codemap) locates GLOP, PDLP, LP model data, and solver interfaces, allowing comparison of two genuinely different LP algorithms within one project.

### 7. [lp-solve/lp_solve](https://github.com/lp-solve/lp_solve)

**Language/role:** C solver core, with interfaces and other supporting languages; revised simplex plus branch-and-bound for linear, integer, semicontinuous, and SOS models. GitHub's aggregate language label is misleading for this repository because its distribution includes many ancillary files.

- **C1:** [lp_mipbb.c](https://github.com/lp-solve/lp_solve/blob/main/lp_mipbb.c) shows the coupled restoration of node bounds, basis state, active-variable counts, and semicontinuous markers when a branch is popped. These state transitions are useful examples of non-recursive search correctness.
- **C2/C3:** The [library header](https://github.com/lp-solve/lp_solve/blob/main/lp_lib.h) exposes numerical controls, anti-degeneracy strategies, pricing choices, and basis-factorization facilities. The branch-and-bound implementation records the use of packed/delta bound storage to reduce search memory. Study this as a compact procedural architecture with explicit performance tradeoffs, while distinguishing enabled code from sections labeled inactive or experimental.

### 8. [optimatika/ojAlgo](https://github.com/optimatika/ojAlgo)

**Language/role:** Java; mathematical library with native LP, QP, and MIP solvers. Focus on `org.ojalgo.optimisation`, especially its integer solver; the larger matrix library is not counted separately.

- **C1:** [IntegerSolver.java](https://github.com/optimatika/ojAlgo/blob/develop/src/main/java/org/ojalgo/optimisation/integer/IntegerSolver.java) tracks bounds for nodes checked out by workers, including a pessimistic placeholder during queue polling so another worker cannot prematurely prove optimality. It also documents a race avoided by initializing a lazily created objective constraint before workers start.
- **C2:** [IntegerStrategy.java](https://github.com/optimatika/ojAlgo/blob/develop/src/main/java/org/ojalgo/optimisation/integer/IntegerStrategy.java) separates model-specific strategies, search priorities, integrality/gap tolerances, and cut-quality settings. It provides a useful example of configurable parallel optimization on the JVM. The cited branch is `develop`; it should not be assumed identical to the latest packaged release.

## Decomposition and parallel integer-programming frameworks

### 9. [coin-or/SYMPHONY](https://github.com/coin-or/SYMPHONY)

**Language/role:** C with supporting C++; generic MILP solver and customizable framework for sequential, shared-memory, and distributed configurations. Its [overview](https://github.com/coin-or/SYMPHONY#symphony) also describes warm starts, multiobjective MILPs, and sensitivity analysis.

- **C1:** [Tree-manager communication](https://github.com/coin-or/SYMPHONY/blob/master/src/TreeManager/tm_proccomm.c) reconstructs node descriptions, merges inherited bound changes, transfers basis information, and handles nodes held for subsequent column-generation phases. Distributed search must preserve the meaning of this state across process boundaries.
- **C2/C3:** The same code supports an LP component compiled into the tree manager or dispatched through messages. Together with the documented callback framework, this offers a concrete study of sharing solving logic across deployment configurations rather than writing a separate parallel solver.

### 10. [scipopt/gcg](https://github.com/scipopt/gcg)

**Language/role:** C/C++; SCIP-based generic column generation and branch-price-and-cut, also supporting Benders decomposition. Study automatic recognition of structure and the contracts needed to exploit it safely.

- **C1:** The [pricing-solver extension guide](https://github.com/scipopt/gcg/blob/master/doc/resources/devs/howtoadd/own-pricing-solver.md) distinguishes heuristic pricing from solving to optimality and specifies lower-bound/status responsibilities. Finding no improving column heuristically is not the same as proving none exists.
- **C2/C3:** The [detection-process design](https://github.com/scipopt/gcg/blob/master/doc/resources/devs/detection/detection-process.md) describes a pool of partial decompositions, multiple detectors, scoring completed decompositions, and translating decompositions after presolve changes the model. This makes structural discovery reusable across different MIPs. The page identifies itself as incomplete, so it is an architectural entry point rather than a complete specification.

### 11. [atoptima/Coluna.jl](https://github.com/atoptima/Coluna.jl)

**Language/role:** Julia; branch-price-and-cut framework that reformulates annotated JuMP models and orchestrates external subproblem solvers. Its own decomposition and search algorithms make it substantially more than a solver wrapper.

- **C2:** The [algorithm guide](https://github.com/atoptima/Coluna.jl/blob/master/docs/src/man/algorithm.md) separates node-conquering algorithms, branching/division algorithms, and exploration strategies. Strong branching additionally composes phases, scoring methods, and candidate-selection rules.
- **C1:** The [storage API](https://github.com/atoptima/Coluna.jl/blob/master/docs/src/api/storage.md) gives explicit contracts for recording and restoring model/storage state, with a correspondence between storage-unit and record types. This is the machinery needed to keep mutations local when evaluating branches.

The repository labels different features stable, beta, alpha, or in development; in particular, not every Benders or basis-restoration facility has the same maturity. The upstream repository is selected instead of its publication snapshot.

### 12. [coin-or/Dip](https://github.com/coin-or/Dip)

**Language/role:** C++ with the DipPy Python interface; decomposition-based MILP solver framework. Study how one application definition can support different combinations of pricing, cutting, and relaxation.

- **C2:** [DecompAlgo.h](https://github.com/coin-or/Dip/blob/master/Dip/src/DecompAlgo.h) separates master construction, solution recomposition, node processing, phase updates, and bound updates. The abstractions expose algorithmic control rather than just model construction.
- **C1:** [DecompApp.h](https://github.com/coin-or/Dip/blob/master/Dip/src/DecompApp.h) explains why automatically checking explicit constraints cannot establish feasibility when some constraints are implicit and generated dynamically. Applications must supply the corresponding feasibility callback. The distinction between a user cutoff and an actual feasible incumbent is also explicit in the algorithm state.

### 13. [coin-or/Bcp](https://github.com/coin-or/Bcp)

**Language/role:** C++; framework for application-specific parallel branch-cut-and-price solvers. **Historical architecture study:** the README contains legacy toolchain guidance and says the framework is not an out-of-the-box general IP solver. It is not archived, but current platform support was not established here.

- **C1:** [BCP_lp_user.hpp](https://github.com/coin-or/Bcp/blob/master/Bcp/src/include/BCP_lp_user.hpp) distinguishes the restricted LP result from a valid subproblem lower bound, documents tolerance assumptions for feasibility helpers, and provides a separate feasibility-restoration path involving dual rays and new variables.
- **C2/C3:** The same interface supports problem-specific cut/column generation, branching, solver initialization, and message processing. The [parallelization overview](https://github.com/coin-or/Bcp#how-is-bcp-parallelized) describes tree-manager/worker message passing, including a serial message-passing implementation. This is useful for studying distributed framework design and its application obligations.

### 14. [coin-or/CHiPPS-BLIS](https://github.com/coin-or/CHiPPS-BLIS)

**Language/role:** C++; BiCePS Linear Integer Solver, implementing MILP branch-and-cut on the BiCePS layer of CHiPPS. It is distinct from the unrelated BLIS dense-linear-algebra project.

- **C2:** [BlisModel.h](https://github.com/coin-or/CHiPPS-BLIS/blob/master/src/BlisModel.h) exposes Osi LP solvers, Cgl cut generators, branching objects, and model setup hooks while distinguishing initialization performed by the master from setup required on every process.
- **C1/C3:** The model has separate pools and encode/decode operations for shared constraints, variables, and pseudocosts. This makes distributed exchange of search knowledge, its ownership, and its serialization concrete study topics. Read it with the [project overview](https://github.com/coin-or/CHiPPS-BLIS#blis). Its testing-status prose references older configurations; those statements are not treated as evidence of a freshly run test matrix.

### 15. [Argonne-National-Laboratory/DSP](https://github.com/Argonne-National-Laboratory/DSP)

**Language/role:** C++; structured and stochastic MILP decomposition, including serial/parallel Dantzig–Wolfe, dual decomposition, and Benders methods. The repository distinguishes global-solving methods from dual-bounding methods, an important limitation when interpreting results.

- **C2:** [DecModel.h](https://github.com/Argonne-National-Laboratory/DSP/blob/release/src/Model/DecModel.h) represents coupling rows, coupling columns, subproblem mappings, stochastic data, and distributionally robust extensions. Its comments explain why fixing coupling columns supports Benders while relaxing coupling rows supports Lagrangian decomposition.
- **C1/C3:** [DdMWAsync.h](https://github.com/Argonne-National-Laboratory/DSP/blob/release/src/Solver/DualDecomp/DdMWAsync.h) models asynchronous work using unique queue identifiers, assignment/evaluation states, per-subproblem indicators, and separate receipt of upper bounds and Benders cuts. This is a compact map of the coordination obligations behind asynchronous optimization. `release` is the verified default branch.

## Interior-point, first-order, and GPU-oriented LP solvers

### 16. [ds4dm/Tulip.jl](https://github.com/ds4dm/Tulip.jl)

**Language/role:** Julia; homogeneous primal-dual interior-point LP solver. Its main study value is separating optimization logic from linear algebra and numeric precision.

- **C1:** The homogeneous formulation handles infeasible and unbounded LPs; arithmetic is parameterized rather than fixed to machine doubles. The [KKT module](https://github.com/ds4dm/Tulip.jl/blob/master/src/KKT/KKT.jl) makes primal/dual regularization and the exact augmented system to be solved explicit.
- **C2/C3:** [KKT interface documentation](https://github.com/ds4dm/Tulip.jl/blob/master/docs/src/reference/KKT/kkt.md) separates system formulations, backends, and solver objects, with `setup`, `update!`, and `solve!` contracts. Implementations include dense, CHOLMOD, LDL-factorization, and Krylov approaches. This supports specialized structured linear algebra without duplicating the interior-point algorithm. The README cautions that the low-level API is less stable than the JuMP/MOI interface.

### 17. [NCKempke/PIPS-IPMpp](https://github.com/NCKempke/PIPS-IPMpp)

**Language/role:** C++ solver code with C/Fortran dependencies; MPI/OpenMP interior-point solver for doubly bordered block-diagonal LPs. It is a substantially modified derivative of Argonne's PIPS, not another mirror of the same implementation.

- **C1:** [DistributedRootLinearSystem.h](https://github.com/NCKempke/PIPS-IPMpp/blob/pipsipm/PIPS-IPM/Core/KKTFormulation/LinearSystems/DistributedRootLinearSystem.h) separates local KKT assembly, reductions, factorization, hierarchical solves, regularization data, and synchronization of distributed matrix entries. Numerical state and MPI ownership must agree throughout that sequence.
- **C2/C3:** Root/child linear systems, sparse versus dense Schur-complement paths, chunked matrix reductions, and specialized solver creation expose how block structure drives the implementation. The [repository guide](https://github.com/NCKempke/PIPS-IPMpp#what-is-pips-ipm) explains the required model structure and execution configuration. This is a specialist HPC codebase; the documented default workflow includes a GAMS interface and expert-level options, and is not a drop-in solver for arbitrary unstructured models.

### 18. [google-research/FirstOrderLp.jl](https://github.com/google-research/FirstOrderLp.jl)

**Language/role:** Julia; experimental first-order LP/QP implementations, including PDHG and Mirror Prox. **Archived on 2025-01-06.** The authors recommend OR-Tools PDLP for users and retain this repository for experiments and publications.

- **C1:** [termination.jl](https://github.com/google-research/FirstOrderLp.jl/blob/main/src/termination.jl) states absolute/relative primal and dual feasibility tests, objective-gap conditions, approximate infeasibility certificates, and distinct work/time-limit outcomes.
- **C2/C3:** [primal_dual_hybrid_gradient.jl](https://github.com/google-research/FirstOrderLp.jl/blob/main/src/primal_dual_hybrid_gradient.jl) separates solver state, iterate averaging, restart parameters, primal weights, and alternative step-size policies. It is valuable for connecting numerical analysis to implementable solver state, particularly how frequently expensive termination checks are performed. Its historical research role is different from the production C++ implementation in OR-Tools.

### 19. [COPT-Public/cuPDLP-C](https://github.com/COPT-Public/cuPDLP-C)

**Language/role:** C/CUDA; restarted PDHG LP solver with CPU and GPU paths. The inspected repository identifies its source packaging as prepared for COIN-OR onboarding review; that is not a claim of completed acceptance.

- **C1:** [cupdlp_solver.c](https://github.com/COPT-Public/cuPDLP-C/blob/main/cupdlp/cupdlp_solver.c) implements primal/dual residual calculations with explicit scaling and variable-bound treatment. The [checker-test guide](https://github.com/COPT-Public/cuPDLP-C/blob/main/tests/README.md) describes independently recomputing feasibility/objectives and rejecting missing, stale, nonfinite, or incorrect outputs.
- **C3:** The solver separates projection, restart, step, scaling, and linear-algebra routines; residual evaluation has CPU operations and specialized CUDA kernels. This exposes the translation of a first-order algorithm into device work and reusable buffers. The documented small tests establish a validation approach, not broad benchmark performance or validation of every optional interface.

### 20. [MIT-Lu-Lab/cuPDLPx](https://github.com/MIT-Lu-Lab/cuPDLPx)

**Language/role:** CUDA/C with language interfaces; LP solver using restarted Halpern PDHG. It is retained separately from cuPDLP-C because its algorithm and execution architecture have substantive differences: Halpern anchoring, reflection, adaptive restarts, and a controlled primal weight.

- **C1:** The [termination design](https://github.com/MIT-Lu-Lab/cuPDLPx/blob/main/docs/algorithm/termination.md) explains dual-slack recovery and unscaling of residuals, and distinguishes satisfying optimality tolerances from merely reaching an iteration/time limit.
- **C3:** The [CUDA Graphs design](https://github.com/MIT-Lu-Lab/cuPDLPx/blob/main/docs/implementation/cuda-graphs.md) describes graph capture between check intervals, an initial iteration outside the graph, device-resident state, and keeping buffer addresses stable so graphs survive restarts. It explicitly explains the tradeoff between fewer launches/synchronizations and delayed stopping checks. These are concrete mechanisms, not a speed ranking.

### 21. [PolyU-IOR/HPR-LP](https://github.com/PolyU-IOR/HPR-LP)

**Language/role:** Julia/CUDA; Halpern Peaceman–Rachford LP implementation, selected as the family's development/research implementation. C, Python, and MATLAB variants are not counted as additional selections.

- **C1:** The [presolve/postsolve architecture](https://github.com/PolyU-IOR/HPR-LP/blob/main/src/presolve/README.md) records reductions for later reconstruction of primal variables and multipliers. It distinguishes exact tape replay from rule-specific recovery and exposes isolated-rule validation helpers.
- **C2/C3:** That subsystem separates scheduling, reduction rules, and GPU primitives. The [solver implementation](https://github.com/PolyU-IOR/HPR-LP/blob/main/src/algorithm.jl) separates residuals, adaptive restarts, penalty updates, GPU workspaces, and scalar transfers; it also handles an underestimated spectral quantity used in the iteration. The repository advises using another solver to check potentially infeasible/unbounded inputs, so it should not be assumed to supply the same failure certificates as every general-purpose LP engine.

### 22. [NVIDIA/cuopt](https://github.com/NVIDIA/cuopt)

**Language/role:** C++/CUDA with C/Python/server interfaces; focus on the **LP and MIP numerical-optimization subsystems**, not routing. **MIP is labeled beta** in the inspected README, which specifically identifies proving optimality as continuing development.

- **C1:** [branch_and_bound.hpp](https://github.com/NVIDIA/cuopt/blob/main/cpp/src/branch_and_bound/branch_and_bound.hpp) exposes concurrent-root-solve coordination, atomic bounds, deterministic solution-event handling, incumbent repair, and separate numerical/limit/feasibility statuses.
- **C3:** The [release notes](https://github.com/NVIDIA/cuopt/blob/main/RELEASE-NOTES.md) document concrete architecture changes: worker-local heaps with node stealing, OpenMP task coordination, concurrent LP algorithms, and multi-GPU PDLP partitioning. They also record fixes to descriptor lifetimes, infeasible-solve hangs, and huge-bound propagation. The project is useful for studying CPU/GPU cooperation; no reported vendor speedup is independently endorsed here.

## Compact native implementations and browser-oriented solvers

### 23. [Specy/microlp](https://github.com/Specy/microlp)

**Language/role:** Rust; native LP/MILP solver usable in WebAssembly. **Substantive fork of `ztlpn/minilp`**, adding integer solving and substantial search/resume facilities; the ancestor is not counted separately.

- **C1:** The [MIP driver](https://github.com/Specy/microlp/blob/master/src/mip/mod.rs) distinguishes feasible incumbents from proven optima, validates tolerances, and makes interruption/resumption explicit. Branching mutates bounds on a single underlying solver, creating a meaningful state-restoration problem.
- **C2/C3:** Solve options, warm starts, node/time limits, and resumable outcomes are reusable library abstractions. The [correctness-suite design](https://github.com/Specy/microlp/blob/master/tests/suite/README.md) describes independent shadow-model checks, exact small combinatorial oracles, metamorphic cases, and incremental/resume comparisons. The README still warns of cycling or precision loss on difficult inputs; the test strategy should not be mistaken for a proof of universal reliability.

### 24. [IanManske/YALPS](https://github.com/IanManske/YALPS)

**Language/role:** TypeScript; browser-oriented LP/MILP solver intended for small problems, substantially rewritten from javascript-lp-solver. Useful for examining a solver whose bundle size and allocation behavior matter as well as arithmetic work.

- **C1:** [simplex.ts](https://github.com/IanManske/YALPS/blob/main/src/simplex.ts) maintains inverse variable-position mappings during pivots, implements two phases, and exposes tolerance, pivot-limit, unboundedness, and cycle-handling decisions.
- **C3:** [branchAndCut.ts](https://github.com/IanManske/YALPS/blob/main/src/branchAndCut.ts) uses typed arrays, a heap of branches, and two reusable tableau buffers swapped when an incumbent improves. This is an approachable example of controlling allocations during repeated LP solves.

Its limitations matter: the README excludes unrestricted variables, and the branch code skips branches whose LP solves cycle. That behavior deserves scrutiny before relying on optimality claims for difficult numerical cases; the entry is especially useful for studying those tradeoffs.

### 25. [daniel-sullivan/go-milp](https://github.com/daniel-sullivan/go-milp)

**Language/role:** Go; native bounded-variable revised-simplex and branch-and-bound MILP implementation. Treat it as an exploratory code-reading selection, without a C4 or production-maturity claim.

- **C1:** [presolve_test.go](https://github.com/daniel-sullivan/go-milp/blob/main/presolve_test.go) generates models with known feasible witnesses and checks that presolve preserves those witnesses; it also compares solves with presolve/cuts enabled and disabled. These are meaningful invariant tests beyond a handful of expected objectives.
- **C2/C3:** [basis_sparse.go](https://github.com/daniel-sullivan/go-milp/blob/main/basis_sparse.go) implements a sparse LU basis backend with row permutations, reusable work arrays, singular-pivot detection, and product-form eta updates behind a basis abstraction. It provides a compact alternative to studying a large C++ factorization subsystem.

Documentation drift is visible: the design note proposes a banded/border method, whereas the implementation uses general sparse LU; even the source's opening refactorization comment predates the eta-update fields. The assessment follows the inspected code and tests, not the repository's numerical speedup or “proven correctness” wording.

## Coverage, searches, and limitations

Discovery used more than six distinct live-web formulations, followed by GitHub repository/API verification and reading additional source files or technical documentation. Search angles included general open-source LP/MILP engines; exact rational simplex; branch-price-and-cut and automatic decomposition; distributed/shared-memory MILP; structured stochastic programming; Julia interior-point and first-order methods; GPU PDHG/Halpern/Peaceman–Rachford implementations; Rust and WebAssembly; JVM and TypeScript solvers; and native Go/C# implementations. Later searches increasingly returned already identified engines, interfaces, academic exercises, or ports, but also added DSP, HPR-LP, and the explicitly qualified Go implementation.

The selection spans large research/industrial codebases, specialist HPC solvers, application-building frameworks, and smaller native libraries. Shared foundations are stated: SCIP and GCG are different implementations with different responsibilities; Cbc and Clp are separate search and LP engines; PIPS-IPM++ and microlp have substantive derivative implementations; OR-Tools and cuOpt each count once despite containing several solvers. Historical FirstOrderLp.jl is included for its independently useful research implementation, not as a second copy of OR-Tools PDLP.

Important exclusions and limits:

- **GLPK:** its [official GNU page](https://www.gnu.org/software/glpk/) was found, but an official substantive GitHub mirror was not established. Unofficial source snapshots were not substituted merely to include a familiar name.
- **Modelers and bindings:** PuLP, JuMP, Pyomo, good_lp, Python-MIP, PySCIPOpt, and Go solver adapters were not counted as LP/MILP solver implementations. Likewise, commercial solver API/examples repositories do not expose the solver internals sought here.
- **Adjacent optimization:** MINLP-focused solvers and general conic/QP solvers were not added solely because LP is a special case. Presolve/cut libraries are valuable dependencies, but were not separately counted as complete solvers in this report.
- **Duplication and maturity:** publication snapshots, extra ports within the HPR-LP family, small educational simplex exercises, and additional forks without a needed distinct implementation were omitted. Legacy Bcp documentation, archived FirstOrderLp.jl, beta features, and visible documentation inconsistencies are called out where relevant.
- **Verification boundary:** this was read-only research. No candidate was cloned, built, installed, or benchmarked, and no tests were run. Source/test inspection supports the described mechanisms, not a claim that the current branch is bug-free or that published performance generalizes. Default-branch links can change after the research date.
