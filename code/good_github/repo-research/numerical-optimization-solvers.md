# Numerical optimization solvers

Research date: **2026-10-09**.

This selection covers implementations of continuous numerical optimization: nonlinear programming, nonlinear least squares, linear and quadratic programming, conic and semidefinite optimization, derivative-free search, and parallel optimization. It includes solver libraries and substantial solver subsystems in larger repositories. Mixed-integer capabilities are mentioned where they accompany a relevant numerical core; modeling layers and thin bindings are not treated as independent solvers. The 26 repositories are grouped by the engineering questions they help answer, not ranked by speed or popularity.

**Criteria legend:** **C1** — difficult correctness involving numerical semantics, invariants, concurrency, adversarial inputs, or failure recovery. **C2** — substantial reusable abstractions supporting multiple problems or algorithms. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — years of evolution accompanied by compatibility work, testing, or complexity management. Criteria judgments below are grounded engineering assessments of the cited material, not certifications of every component.

## General nonlinear optimization and reusable solver libraries

### 1. [coin-or/Ipopt](https://github.com/coin-or/Ipopt)

**Language/role:** C++; large sparse nonlinear programming with an interior-point solver.

Study the boundary between application-provided derivatives, sparse matrix representations, numerical stopping conditions, and a configurable solver implementation.

- **C1:** The changelog records a substantive correction for square systems: dual feasibility and complementarity must not be bypassed when declaring optimality. It also documents failures involving derivative callbacks and warm-start dual values. These expose correctness obligations beyond merely reducing the objective.
- **C2:** The `TNLP` interface accepts sparse derivative triplets with explicit indexing conventions; the implementation documents duplicate-entry accumulation and reference-counted object ownership.
- **C4:** Dated 2022–2024 entries document continuing fixes to metadata mappings, linear-solver interfaces, runtime library loading, and numerical behavior.

Entry points and evidence: [implementation details](https://coin-or.github.io/Ipopt/IMPL.html); [changelog](https://raw.githubusercontent.com/coin-or/Ipopt/master/ChangeLog.md).

### 2. [cvanaret/Uno](https://github.com/cvanaret/Uno)

**Language/role:** C++17; composable sequential quadratic programming and barrier methods for nonlinear constraints.

Uno is particularly useful for studying how to express a family of optimization algorithms without duplicating their common machinery.

- **C2:** Abstract classes separate globalization mechanisms, constraint relaxation, Hessian models, and subproblem construction. A reformulated problem, primal-dual iterate, curvature model, and inertia strategy jointly define a subproblem rather than being hardwired into one monolithic iteration.
- **C1:** The architecture distinguishes feasible KKT points, feasible Fritz John points, and infeasible stationary points. It also specifies when inertia correction applies and warns that arbitrary strategy combinations need not converge; some combinations are explicitly prohibited.

Entry points and evidence: [architecture, termination, and error handling](https://unosolver.readthedocs.io/en/latest/architecture/); [implemented strategies and presets](https://unosolver.readthedocs.io/en/latest/).

### 3. [stevengj/nlopt](https://github.com/stevengj/nlopt)

**Language/role:** C/C++; a library containing local, global, derivative-based, and derivative-free algorithms.

Study how independently developed numerical methods are adapted to a common contract while preserving their differing assumptions and cost models.

- **C1:** The algorithm documentation describes concrete SLSQP repairs: correcting roundoff excursions outside bounds, fixing uninitialized data when equality constraints fill the problem dimension, and handling infinite bounds. It also explains why identical function tolerances are not equivalent across algorithms.
- **C2:** Algorithm selection is systematic, and composite methods such as MLSL and augmented Lagrangian optimization accept a subsidiary optimizer. This supports meaningful algorithm composition rather than merely a collection of unrelated entry points.
- **C3:** The documentation identifies dense SLSQP's storage and computational limitations, helping readers connect implementation choices to problem scale.

Entry point and evidence: [algorithm implementations, adaptations, and composition](https://nlopt.readthedocs.io/en/latest/NLopt_Algorithms/).

### 4. [ralna/GALAHAD](https://github.com/ralna/GALAHAD)

**Language/role:** Modern Fortran, with several language interfaces; a suite of optimization methods and numerical subproblem solvers.

The GLTR subsystem offers an especially clear study of a solver that delegates large vector operations to its caller.

- **C1:** Its trust-region algorithm must distinguish interior solutions, boundary solutions, and behavior with indefinite curvature. The documentation explains why stopping at the first boundary crossing can give a poor answer for significantly indefinite Hessians.
- **C2:** Reverse communication exposes requests for Hessian-vector products and preconditioner applications through a state protocol; applications can supply their own representations without changing GLTR.
- **C3:** Lanczos reduction produces a tridiagonal subproblem. The implementation strategy avoids retaining the complete Krylov basis and reconstructs the solution with a controlled second pass, making memory and recomputation tradeoffs explicit.

Entry point and evidence: [GLTR algorithm and reverse-communication API](https://ralna.github.io/galahad_docs/html/C/gltr.html). The repository is counted once, not separately for each GALAHAD package.

### 5. [scipy/scipy](https://github.com/scipy/scipy)

**Language/role:** Python for the selected implementation; study **`scipy.optimize._trustregion_constr`** within the larger scientific-computing monorepo.

This is a substantial native solver subsystem, independently worth studying beyond SciPy's interfaces to external solvers.

- **C1:** `BarrierSubproblem` protects objective evaluation from strict-bound and enforced-constraint violations, manages slack positivity, and separates barrier stopping conditions from the outer termination logic.
- **C2:** Objective, gradient, constraint, Jacobian, and Lagrangian-Hessian callbacks feed a barrier problem that reuses equality-constrained SQP machinery.
- **C3:** The public solver offers sparse normal-equation or augmented-system factorizations and dense QR/SVD alternatives. Its documented SVD fallback handles deficient row rank but can require densification, exposing a consequential robustness-versus-memory tradeoff.

Entry points and evidence: [barrier implementation](https://raw.githubusercontent.com/scipy/scipy/main/scipy/optimize/_trustregion_constr/tr_interior_point.py); [trust-constr reference](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustconstr.html).

### 6. [JuliaNLSolvers/Optim.jl](https://github.com/JuliaNLSolvers/Optim.jl)

**Language/role:** Julia; univariate and multivariate optimization with several local and global methods.

Study composition at the user-facing algorithm boundary and the way derivative evaluation participates in performance design.

- **C2:** `Fminbox` wraps a selected inner optimizer, while line-search selection and preconditioning remain configurable. Outer barrier iterations and inner optimization iterations have distinct controls. Analytical derivatives, finite differences, and automatic differentiation fit into the same optimization interface.
- **C3:** In-place gradient and Hessian callbacks reuse storage over iterations, avoiding repeated allocation. The documentation connects box-constrained optimization to diagonal preconditioning and explains which inner methods use it.

Entry point and evidence: [minimization tutorial, derivative storage, and Fminbox implementation model](https://julianlsolvers.github.io/Optim.jl/stable/user/minimization/). This is the algorithm library, not a generic wrapper around another solver.

### 7. [argmin-rs/argmin](https://github.com/argmin-rs/argmin)

**Language/role:** Rust; numerical optimization algorithms and a generic execution framework.

Study how traits separate objective capabilities, iteration state, mathematical operations, and execution services.

- **C2:** `Solver<O, I>` connects algorithms to an `Executor` through initialization, iteration, and termination hooks. State and algebra types are generic; serialization enables checkpointing, and iteration metadata supports observers.
- **C1:** The More–Thuente line search encodes strong Wolfe conditions, validates the relationship between decrease and curvature constants, and controls step bounds and interval-width termination. This is a useful place to examine the contract between a line search and its enclosing optimizer.

Entry points and evidence: [Solver trait](https://docs.rs/argmin/latest/argmin/core/trait.Solver.html); [More–Thuente implementation documentation](https://docs.rs/argmin/latest/argmin/solver/linesearch/struct.MoreThuenteLineSearch.html). The latter explicitly notes missing stopping criteria, so inclusion should not be read as a blanket numerical-completeness claim.

### 8. [ceres-solver/ceres-solver](https://github.com/ceres-solver/ceres-solver)

**Language/role:** C++; nonlinear least squares, including large bundle-adjustment problems.

Study the interaction between nonlinear step acceptance and linear algebra specialized to the problem's block structure.

- **C1:** The solver guide develops trust-region acceptance from predicted versus actual improvement, and distinguishes exact and inexact Levenberg–Marquardt steps. Bounds introduce additional line-search handling.
- **C3:** Schur methods eliminate point variables before solving the reduced camera system. Dense, sparse, and iterative Schur alternatives expose different memory and factorization costs rather than hiding them behind one generic matrix solve.
- **C2:** The same nonlinear solver can select different trust-region strategies, linear solvers, and preconditioners, making it useful for studying interchangeable numerical components.

Entry points and evidence: [nonlinear least-squares solver guide in the source tree](https://raw.githubusercontent.com/ceres-solver/ceres-solver/master/docs/source/nnls_solving.rst); [version history and compatibility changes](https://raw.githubusercontent.com/ceres-solver/ceres-solver/master/docs/source/version_history.rst). The history separates unreleased changes from released features.

## Linear, quadratic, conic, and semidefinite solvers

### 9. [ERGO-Code/HiGHS](https://github.com/ERGO-Code/HiGHS)

**Language/role:** Primarily C++; sparse LP, convex QP, and mixed-integer linear optimization.

Study how several numerical engines share a solver product while retaining different notions of useful output and restart state.

- **C1:** The documentation distinguishes an optimal point from a basic solution, explains crossover after interior-point optimization, and describes cases where optimality cannot be claimed. It also candidly documents incomplete detection of nonconvex QP Hessians.
- **C2:** Simplex, interior-point, and first-order LP paths coexist with QP methods under explicit solver-selection rules. Simplex can reuse a basis after model changes.
- **C3:** The interior-point implementations illustrate preconditioned iterative solves versus direct factorization, including matrix-system and fill-reducing-ordering choices. These are concrete architecture choices for sparse problems, not a universal speed claim.

Entry point and evidence: [solver architecture, crossover, and numerical limitations](https://ergo-code.github.io/HiGHS/stable/solvers/).

### 10. [osqp/osqp](https://github.com/osqp/osqp)

**Language/role:** C; convex quadratic programming through operator splitting.

Study an ADMM solver whose numerical contract is defined by residuals, certificates, and linear-system structure.

- **C1:** Primal and dual infeasibility certificates have explicit tests; convergence uses scaled primal and dual residual thresholds. Polishing guesses active constraints and falls back to the ADMM result if that guess does not succeed.
- **C2:** The core supports interchangeable linear-system solvers. Direct methods solve a quasi-definite saddle-point system; indirect methods solve a positive-definite reduced system.
- **C3:** Adaptive step-size updates consider both residual balance and the relationship between iteration and setup time. The documentation also makes the extra factorization cost of polishing explicit.

Entry point and evidence: [algorithm, linear systems, certificates, and polishing](https://osqp.org/docs/solver/index.html).

### 11. [cvxgrp/scs](https://github.com/cvxgrp/scs)

**Language/role:** C; large convex cone programs using splitting and a homogeneous embedding.

Study the separation of cone projection, linear-system solution, and termination logic in a first-order solver.

- **C1:** Optimality requires primal residual, dual residual, and duality-gap checks. The documented infeasibility tests account for data scaling and require consecutive qualifying residual checks to guard against transient iterates.
- **C2:** A linear-solver backend implements an explicit workspace and lifecycle contract, including initialization, solves, diagonal updates, and cleanup.
- **C3:** The indirect backend uses matrix-vector products and warm-started conjugate gradients with controlled solve accuracy; direct and GPU backends offer alternative costs and hardware placement.

Entry points and evidence: [algorithm and termination](https://www.cvxgrp.org/scs/algorithm/index.html); [linear-system backend contract](https://www.cvxgrp.org/scs/linear_solver/index.html).

### 12. [oxfordcontrol/Clarabel.rs](https://github.com/oxfordcontrol/Clarabel.rs)

**Language/role:** Rust; interior-point optimization with quadratic objectives and multiple convex cone types.

Study the numerical safeguards around a conic interior-point implementation and its treatment of sparse semidefinite structure. The Rust implementation is counted once; its Julia sibling is not a duplicate entry.

- **C1:** Solver settings expose full and reduced accuracy thresholds, static and dynamic KKT regularization, iterative-refinement stopping rules, and distinct step handling for symmetric and asymmetric cones. The documentation warns that default tolerances assume 64-bit floating point.
- **C3:** Chordal decomposition and clique merging can replace a suitably structured large positive-semidefinite constraint with smaller cone constraints. The benefit depends on structure, and the settings expose choices such as compact assembly and dual completion.

Entry points and evidence: [numerical solver settings](https://clarabel.org/stable/api_settings/); [chordal decomposition](https://clarabel.org/stable/user_guide_chordal/).

### 13. [embotech/ecos](https://github.com/embotech/ecos)

**Language/role:** C; an embedded conic solver, particularly for second-order cone programs.

Study a relatively compact KKT implementation where ordering, regularization, work buffers, and numerical refinement remain visible.

- **C1:** The KKT module checks factorization success, applies dynamic regularization, and computes residuals for iterative refinement. If a refinement step increases the error, it explicitly undoes the correction and stops refining.
- **C3:** Matrix updating, LDL factorization, and triangular solves share a dedicated KKT structure and reusable work arrays. Permutation and unpermutation are explicit, making the connection between sparse storage and search directions inspectable.

Entry point and evidence: [KKT factorization and refinement implementation](https://raw.githubusercontent.com/embotech/ecos/develop/src/kkt.c). This entry concerns the continuous conic core; the repository's branch-and-bound extension is not counted independently.

### 14. [jump-dev/Hypatia.jl](https://github.com/jump-dev/Hypatia.jl)

**Language/role:** Julia; generic conic interior-point optimization, including cones beyond the usual small standard set.

Study what a solver needs from a cone, rather than treating cone support as a closed enumeration.

- **C2:** New cones implement a common interface with initialization, feasibility, and barrier-derivative oracles. The same abstraction supports dual-cone treatment and optional specialized oracles; cones also integrate with MathOptInterface.
- **C1:** The oracle contract requires an interior starting point and derivatives of an appropriate logarithmically homogeneous self-concordant barrier. Those mathematical obligations are part of the extension boundary, not incidental details hidden inside a solver loop.

Entry points and evidence: [generic cone interface](https://jump.dev/Hypatia.jl/stable/cones/); [native interface and project caveats](https://jump.dev/Hypatia.jl/stable/). The project explicitly calls itself experimental and cautions about default tuning and older Julia versions.

### 15. [Kim-ChuanToh/SDPT3](https://github.com/Kim-ChuanToh/SDPT3)

**Language/role:** MATLAB with MEX components; semidefinite, second-order, and linear cone programming. **Historical distribution in the author's repository**: its README dates the last major software update to February 2009 and lists later compatibility fixes; present activity is not assumed.

Study the block-oriented representation of mixed conic problems and an older numerical software design that exposes primal-dual diagnostics directly.

- **C1:** `sqlp` validates and converts problem data, returns optimality diagnostics or infeasibility certificates, and records primal/dual infeasibility and gap histories.
- **C2:** A block descriptor supports different cone structures; options include custom Schur-complement functions, initial primal-dual iterates, and predictor-corrector controls.
- **C4:** The README documents MATLAB MEX compatibility fixes in 2016 and 2017 following the earlier solver development, rather than merely supplying an old creation date.

Entry point and evidence: [SQLP implementation](https://raw.githubusercontent.com/Kim-ChuanToh/SDPT3/master/Solver/sqlp.m); history and distribution status are documented in the linked repository README.

## Embedded and repeatedly solved quadratic programs

### 16. [Simple-Robotics/proxsuite](https://github.com/Simple-Robotics/proxsuite)

**Language/role:** C++ with Python bindings; study the **ProxQP** dense and sparse quadratic-programming solvers.

This is useful for understanding how repeated optimization becomes an object-lifecycle and cache-invalidation problem.

- **C2:** Dense and sparse implementations share `init`, `solve`, and `update` operations while separating model data, settings, results, and workspace. Sparse initialization can use the matrices' sparsity masks.
- **C1:** Updating matrices or proximal parameters must invalidate affected factorizations; the documentation describes automatic refactorization to preserve consistency.
- **C3:** Warm starts can preserve primal-dual values, proximal parameters, and the factorization workspace. A distinct cold-start-with-previous-result mode retains values while resetting numerical machinery, making reuse policy explicit.

Entry point and evidence: [ProxQP API, workspace semantics, and warm-start modes](https://simple-robotics.github.io/proxsuite/md_doc_22-ProxQP__api.html).

### 17. [coin-or/qpOASES](https://github.com/coin-or/qpOASES)

**Language/role:** C++; online active-set quadratic programming for sequences of related problems.

Study how a solver exposes neighboring-problem state and bounded computational effort to an application.

- **C2:** `QProblem` accepts guessed primal/dual solutions and working sets, optional precomputed Cholesky factors, and a user-provided constraint-product operation. Initialization and hot starts use a common problem object.
- **C1:** The interface distinguishes failures in Cholesky/TQ initialization, homotopy steps, step directions, infeasibility, unboundedness, and working-set limits. These are separate outcomes rather than one generic failure flag.
- **C3:** Hot starts solve a neighboring QP with updated costs and bounds; the API supports limits on working-set recalculations and CPU time, with actual consumption returned to the caller.

Entry point and evidence: [QProblem interface and internal solve contracts](https://raw.githubusercontent.com/coin-or/qpOASES/master/include/qpOASES/QProblem.hpp).

### 18. [giaf/hpipm](https://github.com/giaf/hpipm)

**Language/role:** C; interior-point QP/QCQP solvers for dense, optimal-control, and tree-structured problems.

Study a solver that preserves application structure through its data representation instead of immediately flattening everything into a generic sparse problem.

- **C2:** The documented optimal-control API separates dimensions from QP data and permits stage-specific setters. States, controls, bounds, general constraints, and softened constraints have explicit representations.
- **C3:** The repository explains its reliance on BLASFEO and structure-exploiting algorithms for embedded and model-predictive-control workloads. The API has explicit memory-size queries and constructors that accept caller-supplied memory, making allocation part of the design.

Entry point and evidence: [OCP data and memory API guide](https://raw.githubusercontent.com/giaf/hpipm/master/doc/guide.tex); the repository README explains the solver families and BLASFEO dependency. The guide is terse, so this is a better selection for readers comfortable following C interfaces.

### 19. [darnstrom/daqp](https://github.com/darnstrom/daqp)

**Language/role:** C; a dependency-free dual active-set convex QP solver, with additional mixed-integer capabilities.

Study an embedded-oriented alternative to both primal active-set and interior-point implementations.

- **C1:** The main loop repairs singular working sets, checks primal and dual feasibility, handles near-singular factors with refinement, and has explicit cycling detection. It preserves additional ordering constraints when branch-and-bound is using the workspace.
- **C3:** Separate routines incrementally add and remove constraints from an LDL factorization. Packed factor storage and reused workspace expose how active-set changes avoid rebuilding all linear algebra from scratch.

Entry points and evidence: [solver loop and safeguards](https://raw.githubusercontent.com/darnstrom/daqp/master/src/daqp.c); [incremental factorization implementation](https://raw.githubusercontent.com/darnstrom/daqp/master/src/factorization.c). This selection is based on the continuous numerical core, not the mere presence of an integer extension.

## Derivative-free, black-box, and population-based optimization

### 20. [libprima/prima](https://github.com/libprima/prima)

**Language/role:** Modern Fortran core with additional interfaces and implementations; reference implementations of Powell's derivative-free methods.

Study the modernization of subtle numerical algorithms while preserving readable reasoning about their internal state.

- **C1:** The COBYLA implementation documents simplex geometry, merit-parameter updates, rounding failures, abnormal initialization, and return-point selection. Debug assertions check evaluation budgets, finite values, history consistency, and whether the returned point is dominated by a recorded point. It even explains an integer-overflow hazard in an iteration bound.
- **C2:** Initialization, geometry changes, trust-region subproblem solution, exit handling, and history management are separated into named routines. The wider project applies structured implementations across COBYLA, UOBYQA, NEWUOA, BOBYQA, and LINCOA.

Entry points and evidence: [COBYLA core and invariants](https://raw.githubusercontent.com/libprima/prima/main/fortran/cobyla/cobylb.f90); [automated testing organization](https://github.com/libprima/prima/blob/main/tests.md). Test infrastructure is evidence of verification effort, not independent confirmation of advertised test-hour totals.

### 21. [numericalalgorithmsgroup/dfols](https://github.com/numericalalgorithmsgroup/dfols)

**Language/role:** Python; derivative-free nonlinear least squares, particularly for expensive or noisy residual evaluations.

Study numerical recovery policy and the coordination of interpolation models with trust-region steps.

- **C1:** The controller distinguishes evaluation errors, singular linear algebra, exhausted budgets, slow progress, and misleading successful steps. Its restart policy permits recovery from some failures while refusing to restart after invalid input or an exhausted evaluation budget.
- **C2:** A controller coordinates separate model, trust-region, and utility components. Projection callbacks, regularization/proximal callbacks, sampling counts, and scaling information allow the same machinery to address different constrained least-squares problems.

Entry point and evidence: [controller, exit semantics, and initialization](https://raw.githubusercontent.com/numericalalgorithmsgroup/dfols/master/dfols/controller.py). The repository documents pytest-based installation checks and identifies DFO-LS as a more flexible successor to DFO-GN; DFO-GN is not counted separately.

### 22. [bbopt/nomad](https://github.com/bbopt/nomad)

**Language/role:** C++; NOMAD 4 implements Mesh Adaptive Direct Search for constrained black-box optimization.

Study how expensive evaluations are scheduled and how surrogate models participate in a solver without replacing the real objective.

- **C2:** Search and poll phases can use dynamically constructed quadratic models, SGTELIB models, or a user-provided static surrogate. Evaluator types and custom trial-point ordering form reusable extension boundaries.
- **C3:** Opportunistic evaluation stops a trial list after improvement; with block evaluation, that decision occurs after the block. The guide exposes block sizes and surrogate-based ordering, while the repository describes OpenMP evaluation parallelism.

Entry point and evidence: [advanced evaluation, surrogate, and search behavior](https://nomad-4-user-guide.readthedocs.io/en/latest/AdvancedFunctionalities.html). The repository explicitly identifies NOMAD 4 as a redesigned architecture; it is not the older NOMAD 3 codebase.

### 23. [esa/pagmo2](https://github.com/esa/pagmo2)

**Language/role:** C++; global and multiobjective optimization algorithms organized around asynchronous islands.

Study concurrency in optimization when algorithms and populations continue evolving while their owner remains responsive.

- **C1:** The island contract spells out concurrent access requirements, destruction and move behavior, and the distinction between waiting and checking asynchronous errors. The default island choice considers the thread-safety guarantees of the algorithm and problem.
- **C2:** An island combines an algorithm, population, execution implementation, and migration selection/replacement policies. User-defined islands can change where evolution runs without changing the population or algorithm interfaces.
- **C3:** Threads, processes, and potentially remote execution support asynchronous optimization; the architecture avoids prescribing one execution model for every numerical method.

Entry point and evidence: [island abstraction, lifecycle, and thread-safety rules](https://esa.github.io/pagmo2/docs/cpp/island.html). This repository includes its own optimization algorithms as well as integrations, so it is not retained merely as a solver wrapper.

## GPU and distributed nonlinear optimization

### 24. [madsuite-org/MadNLP.jl](https://github.com/madsuite-org/MadNLP.jl)

**Language/role:** Julia; nonlinear programming with CPU and GPU linear-solver extensions. The former `MadNLP/MadNLP.jl` URL redirects to this canonical organization.

Study how KKT systems become first-class numerical objects rather than matrices assembled ad hoc inside an iteration.

- **C2:** `AbstractKKTSystem` separates derivative storage, system assembly, algebraic manipulation, and factorization. Callback objects and KKT vector types support different representations and linear solvers.
- **C1:** The documentation derives the primal-dual system, regularization terms, and elimination that relates unreduced and reduced systems. It demonstrates checking a computed solution by multiplying with the KKT operator.
- **C3:** Reduced systems eliminate variable blocks before factorization, and the repository supplies GPU, HSL, and Pardiso extensions. This exposes the boundary between optimization logic and hardware-specific linear algebra.

Entry point and evidence: [KKT-system architecture and worked solve](https://madsuite.org/MadNLP.jl/stable/man/kkt/); extension availability is documented in the linked repository.

### 25. [llnl/hiop](https://github.com/llnl/hiop)

**Language/role:** C++; high-performance nonlinear optimization with MPI and GPU support.

Study an optimizer designed to cooperate with an application's existing data distribution and memory placement.

- **C2:** A common interface supports sparse, mixed dense-sparse, and dense-constraint problem forms. The calling application supplies distribution information instead of surrendering all representation choices to the solver.
- **C1:** Interface contracts distinguish invalid parallelization, invalid numerical values, user-evaluation failures, acceptable solutions, and feasible-but-not-optimal outcomes. Device-facing pointers must obey the selected memory-space contract.
- **C3:** Distributed vectors and specialized matrix forms support data-parallel iterations; the repository documents MPI, GPU, RAJA/Umpire support, and correctness tests that include optimization problems with known solutions.

Entry point and evidence: [problem interfaces, status codes, and memory-space obligations](https://raw.githubusercontent.com/LLNL/hiop/develop/src/Interface/hiopInterface.hpp). Build and test scope are documented in the repository README; no reported speedup is adopted here as an independent benchmark.

### 26. [petsc/petsc](https://github.com/petsc/petsc)

**Language/role:** Primarily C; study the **TAO optimization subsystem** of PETSc. **Official-project GitHub mirror** of the GitLab repository, explicitly labeled as a mirror on its repository page.

Study how reusable scientific-computing objects support optimization across distributed applications.

- **C2:** TAO uses objective/gradient/Hessian callbacks, solver contexts, PETSc vectors and matrices, and independently selectable linear solvers and preconditioners. Runtime options can change the optimization method without rewriting the application callbacks.
- **C3:** A solver is created with an MPI communicator; distributed vector layout is part of efficient scaling, reductions, and function evaluation. The same framework supplies unconstrained, bound-constrained, least-squares, and more general optimization methods.
- **C1:** Callback contracts specify nonzero error returns when evaluation is undefined or fails, and matrix/preconditioner responsibilities are explicit. These interfaces are useful for studying failure propagation across application and solver code.

Entry point and evidence: [TAO manual, callback contracts, and parallel workflow](https://petsc.org/main/manual/tao/). PETSc is counted once; its unrelated differential-equation subsystems are outside this report's selection.

## Coverage, search process, and limitations

Live discovery used eleven distinct search formulations, plus targeted searches for primary architecture documentation. The discovery angles included general nonlinear interior-point/SQP solvers; Rust/Julia conic and quadratic solvers; derivative-free least squares; sparse LP/simplex implementations; distributed and GPU optimization; Powell-method modernization and MADS; Julia/Rust/MATLAB solver communities; embedded active-set QP solvers; Go/Java/C# numerical libraries; Fortran reverse-communication trust-region methods; and a final cross-family conic/nonlinear search. Later searches mostly revisited covered families, interfaces, or projects with less-established evidence; the embedded search added DAQP because its dual active-set core supplied a distinct implementation to inspect.

Every retained repository page was opened, redirects were resolved, and at least one additional primary implementation or documentation source was read. Detailed source reading was used when documentation pages failed to load, notably for Ceres, DFO-LS, and qpOASES. Repository stars did not determine selection. No candidate code was run, dependencies installed, or large repositories cloned.

Important boundaries and exclusions:

- Thin language bindings, solver dispatch packages, modeling systems, tutorials, and lists were excluded as independent entries. Clarabel's language implementations are represented once; DFO-GN was not added alongside DFO-LS. SciPy and PETSc are included for named substantive solver subsystems, not their full monorepos.
- The unofficial `sqlp/sdpt3` distribution was examined but replaced in the selection by the author's `Kim-ChuanToh/SDPT3` repository. Its community packaging work is not attributed to the author's repository. PETSc's substantive GitHub mirror is explicitly identified.
- Mixed-integer-only, SAT/constraint-programming, symbolic optimization, Bayesian hyperparameter search, and neural-network training optimizers were outside the main scope. Additional implementations found during discovery, including PDFO, OptimLib, qpSWIFT, and newer conic projects, were not exhaustively audited; omission is not a negative quality judgment.

This is a source-based selection guide, not a benchmark or comprehensive numerical audit. Search coverage is strongest in C/C++, Fortran, Julia, Python, and Rust, with historical MATLAB coverage. Java, Go, and .NET were searched but are not represented in the final selection. Historical and experimental caveats are stated where primary sources establish them; otherwise inclusion makes no assertion about current release cadence. Documentation and default branches can change, and some documentation reflects development code rather than a released package. C4 is asserted only where dated evolution and concrete compatibility work were inspected.
