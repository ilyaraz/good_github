# Ordinary differential equation and time integration libraries

Research date: **2026-10-09**.

This selection covers reusable numerical initial-value ODE solvers and time-integration infrastructure: stiff and nonstiff methods, differentiable solvers, geometric and oscillatory methods, and parallel integration of systems arising from spatially discretized PDEs. It includes substantial solver subsystems in broader numerical libraries, each counted once. The 21 repositories are study candidates, not a ranking or an assertion that every algorithm and component is equally reliable.

Criteria legend:

- **C1 — Difficult correctness:** numerical semantics, invariants, error control, concurrency, discontinuities, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and components supporting different equations, methods, data representations, or applications.
- **C3 — Performance with structure:** explicit treatment of computational or memory constraints through understandable architectural choices.
- **C4 — Sustained evolution:** years of development accompanied by evidence of compatibility management, testing, or controlled complexity; age and recent pushes alone do not qualify.

Criterion assignments below are engineering judgments grounded in the linked primary material. Canonical GitHub identities and archive status were checked through repository pages or the GitHub API. None of the selected repositories was marked archived at the research snapshot; that does not establish ongoing maintenance.

## General-purpose solver libraries

### 1. [llnl/sundials](https://github.com/llnl/sundials)

**Language/role:** Primarily C, with other language interfaces; CVODE/CVODES, ARKODE, and related DAE solvers.

Study how a production numerical suite separates time integration from vectors, matrices, nonlinear solves, linear solves, and preconditioners. ARKODE is an especially useful architectural entry point: its integration infrastructure handles stages, error estimation, step selection, and interpolation, while interchangeable solver objects handle subsidiary systems.

- **C1:** Implicit stages, nonidentity mass matrices, local-error control, and interpolation must remain consistent. Problem state is held in an opaque instance rather than global data, supporting reentrant use.
- **C2:** `SUNLINSOL`, `SUNMATRIX`, and nonlinear-solver interfaces support direct, iterative, and matrix-free implementations without replacing the integrator.
- **C3:** Separate preconditioner setup/solve phases and serial, threaded, and distributed vector implementations expose where large-system costs are managed. These details are documented in the [ARKODE organization chapter](https://github.com/llnl/sundials/blob/main/doc/arkode/guide/source/Organization.rst).

**Entry points:** The organization chapter above; the [changelog](https://github.com/llnl/sundials/blob/main/CHANGELOG.md), which records concrete tolerance-scaling fixes, convergence-check fixes, and staged API deprecations.

### 2. [SciML/OrdinaryDiffEq.jl](https://github.com/SciML/OrdinaryDiffEq.jl)

**Language/role:** Julia; a broad native solver implementation within SciML, including explicit, implicit, multistep, exponential, and structure-preserving methods.

Study how many algorithms share an integration framework while retaining specialized numerical kernels. The developer recipe distinguishes algorithm dispatch types, mutable work caches, constant caches, initialization, and `perform_step!`; its worked example includes stage limiters and endpoint derivative reuse.

- **C1:** Adding an algorithm entails convergence checks and dense-output regression tests; endpoint derivatives must also support interpolation correctly.
- **C2:** Algorithm types and cache types separate method selection from reusable integration state and in-place versus out-of-place right-hand sides.
- **C3:** Mutable caches reuse work arrays, while exponential methods distinguish precomputed operators from Krylov approximations. The [algorithm-development guide](https://github.com/SciML/OrdinaryDiffEq.jl/blob/master/docs/src/devtools/contributing/adding_algorithms.md) explains these choices with code.

**Entry points:** That guide and the current [solver package tree](https://github.com/SciML/OrdinaryDiffEq.jl/tree/master/lib). Some developer examples describe an older file organization; use the current tree to locate implementations. The umbrella DifferentialEquations.jl repository is not counted separately.

### 3. [boostorg/odeint](https://github.com/boostorg/odeint)

**Language/role:** C++; generic ODE integration within Boost.

Study a library organized around stepper concepts rather than one mandatory solver class. Explicit, controlled, dense-output, symplectic, and multistep methods expose different contracts, including in-place and out-of-place stepping.

- **C1:** First-same-as-last (FSAL) methods retain derivatives between steps. The documentation explicitly explains why switching the system or state without handling that cache violates the stepping contract.
- **C2:** Stepper concepts accept user-supplied systems; Hamiltonian methods accept paired component functions, and controlled/dense-output steppers add distinct capabilities.
- **C3:** Passing or caching already computed derivatives avoids repeated right-hand-side evaluations. The [detailed stepper guide](https://www.boost.org/doc/libs/latest/libs/numeric/odeint/doc/html/boost_numeric_odeint/odeint_in_detail/steppers.html) connects this optimization to its correctness obligations.

**Entry point:** The stepper guide above. Its implicit-solver subsection is explicitly marked out of date, so it should not be treated as a complete current capability inventory.

### 4. [scipy/scipy](https://github.com/scipy/scipy)

**Language/role:** Python with compiled numerical components; relevant subsystem: `scipy.integrate`, particularly `solve_ivp` and its native solver classes.

Study the boundary between a uniform scientific API and implementations with different stiffness, interpolation, and Jacobian requirements. This entry concerns the solver subsystem, not the entire SciPy monorepo.

- **C1:** Error scaling, complex-domain restrictions, solver failure states, and event localization have explicit semantics. Event detection can miss multiple crossings inside a step, a useful example of a documented numerical limitation.
- **C2:** New `OdeSolver` subclasses implement `_step_impl` and `_dense_output_impl`; the base contract defines status transitions and evaluation accounting.
- **C3:** Sparse Jacobian structure and vectorized finite differences reduce some implicit-solver costs, while the API documents cases where vectorization is slower. See the [solver extension contract](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.OdeSolver.html) and [solve_ivp reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html).

**Entry points:** Those two references, each with links to implementation source. Native Runge–Kutta, Radau, and BDF implementations make this more than a wrapper-only selection.

### 5. [Hipparchus-Math/hipparchus](https://github.com/Hipparchus-Math/hipparchus)

**Language/role:** Java; relevant subsystem: `hipparchus-ode`.

Study event handling as a carefully specified part of numerical integration. Hipparchus [originated as an Apache Commons Math fork](https://www.hipparchus.org/); it is retained for substantive independent evolution, including a redesigned detector/handler API, rather than counted as another copy of Commons Math.

- **C1:** The event package defines bracketing versus root localization, backward-integration checks, at-most-once root reporting, chronological ordering, and visibility of state resets to subsequent events.
- **C2:** Detectors, handlers, switching functions, and generic field-valued counterparts can be composed independently. The 3.0 reorganization explicitly enabled reuse of predefined detectors with custom handlers.

**Entry points:** [Event semantics](https://www.hipparchus.org/hipparchus-ode/apidocs/org/hipparchus/ode/events/package-summary.html) and the [field event-handler API and migration explanation](https://www.hipparchus.org/hipparchus-ode/apidocs/org/hipparchus/ode/events/FieldODEEventHandler.html). These distinguish the codebase more usefully than its catalogue of Runge–Kutta methods.

### 6. [martinjrobins/diffsol](https://github.com/martinjrobins/diffsol)

**Language/role:** Rust; stiff/nonstiff ODE and mass-matrix DAE solving, with sensitivities and optional compiled equation definitions.

Study a trait-oriented design linking equations, solver state, linear algebra backends, and numerical methods. The API permits both high-level builders and custom equation/operator implementations.

- **C1:** Consistent initial states, singular mass matrices, sensitivity error control, and state resets require coordinated semantics. The documentation also exposes an unusually concrete failure mode: NaN propagation used to infer Jacobian sparsity can fail with input-dependent control flow, with explicit sparsity/matrix methods as alternatives.
- **C2:** Matrix/vector, equation, linear-solver, nonlinear-solver, and integration traits allow replacement of components without rewriting the full pipeline.
- **C3:** Sparse Jacobians and checkpoint-based reconstruction of trajectories address factorization and adjoint-memory costs. See the [crate's architectural/API guide](https://docs.rs/diffsol/latest/diffsol/).

**Entry points:** That guide and the [equation implementation tree](https://github.com/martinjrobins/diffsol/tree/main/crates/diffsol/src/ode_equations). The current repository is a workspace; older links referring simply to root-level `src` can be stale.

### 7. [srenevey/ode-solvers](https://github.com/srenevey/ode-solvers)

**Language/role:** Rust; a smaller nonstiff integration library with Dormand–Prince methods, RK4, and dense output.

Study an approachable implementation of adaptive integration with a separate proportional-integral step controller. It offers a narrower reading project than a stiff-solver framework while retaining meaningful numerical machinery.

- **C1:** The controller bounds step-size changes, preserves integration direction, and prevents immediate growth after a rejected step; acceptance also updates the remembered error used by subsequent control decisions.
- **C2:** A generic `System<T, V>` separates the differential equation from solvers and vector representations. Its mutable `solout` callback can stop after a successful step; this is a step callback, not continuous event-root localization.

**Entry points:** The [controller implementation](https://github.com/srenevey/ode-solvers/blob/main/src/controller.rs) and [System trait contract](https://docs.rs/ode_solvers/latest/ode_solvers/dop_shared/trait.System.html).

## Differentiable and probabilistic integration

### 8. [patrick-kidger/diffrax](https://github.com/patrick-kidger/diffrax)

**Language/role:** Python/JAX; differentiable ODE, SDE, and controlled-equation solvers.

Study how equation representation and gradient strategy can be orthogonal to the numerical method. Terms combine a vector field, a control increment, and their interaction; solvers declare the term structures they accept.

- **C1:** The adjoint documentation distinguishes differentiating the discretized solution from numerically solving continuous adjoint equations. These are different gradient computations, with different supported differentiation modes.
- **C2:** `ODETerm`, `ControlTerm`, `MultiTerm`, and PyTree combinations reuse the same abstractions across ordinary, controlled, stochastic, and partitioned systems.
- **C3:** The default recursive checkpoint adjoint uses online binomial checkpointing when the adaptive step count is unknown in advance. Specialized vector-field/product composition can also avoid unnecessary intermediate operations.

**Entry points:** [Term architecture](https://docs.kidger.site/diffrax/api/terms/) and [adjoint implementation choices](https://docs.kidger.site/diffrax/api/adjoints/).

### 9. [rtqichen/torchdiffeq](https://github.com/rtqichen/torchdiffeq)

**Language/role:** Python/PyTorch; differentiable tensor ODE solvers and event handling.

Study the interaction between adaptive stepping and automatic differentiation in a compact neural-ODE-oriented implementation. Direct differentiation through the solve and a backward adjoint solve share the public integration interface.

- **C1:** Adaptive rejection depends on scaled error norms; interpolation distinguishes requested output times from internal steps. Differentiable event termination additionally requires event parameters to be represented appropriately in the state.
- **C2:** Tensor-valued states and a callable right-hand side work across multiple fixed and adaptive methods, with separate direct and adjoint entry points.
- **C3:** The adjoint path trades saved internal-step history for additional backward integration. Its memory claim concerns the integration strategy, not elimination of all model or output storage.

**Entry points:** The [repository API and event explanation](https://github.com/rtqichen/torchdiffeq#differentiable-event-handling) and [implementation-oriented FAQ](https://github.com/rtqichen/torchdiffeq/blob/master/FAQ.md), which discusses norms, intermediate states, interpolation, and step-size underflow.

### 10. [martenlienen/torchode](https://github.com/martenlienen/torchode)

**Language/role:** Python/PyTorch; independently adaptive integration across batches of ODE problems.

Study how vectorization changes solver-state management. Batch elements have separate time ranges, step sizes, acceptance decisions, counters, and completion masks. This is a distinct implementation from torchdiffeq.

- **C1:** The solve loop updates time, solution, and method state only where `accept & running` holds. Initial-time output handling establishes an invariant that rejected steps do not cross pending evaluation points.
- **C2:** Initial-value problems, terms, single-step methods, step-size controllers, and adjoint strategies are separate components.
- **C3:** Tensor masking and a TorchScript-exported solve loop support batch execution without forcing every sample to use one common adaptive step size. Study the implementation rather than assuming a universal speed advantage.

**Entry point:** The [adjoint/solve-loop implementation](https://github.com/martenlienen/torchode/blob/main/torchode/adjoints.py), which makes the state transitions and compilation constraints explicit.

### 11. [pnkraemer/probdiffeq](https://github.com/pnkraemer/probdiffeq)

**Language/role:** Python/JAX; probabilistic numerical ODE solvers using state-space estimation.

Study integration that represents uncertainty in the numerical solution, with filtering/smoothing, Taylor-state representations, priors, and calibration. The project explicitly describes itself as research software with potentially sudden API changes.

- **C1:** Stability depends on linearization and covariance representation; calibration affects adaptive stepping, while DAE constraints can require a different error estimator from explicit ODE residuals.
- **C2:** Priors, estimation strategies, error estimators, and state-space representations provide composable choices across initial-value problems and parameter estimation.
- **C3:** Dense, block-diagonal, and isotropic models trade retained correlations against computational cost. The documentation explains the associated uncertainty and stability compromises instead of presenting them as equivalent implementations.

**Entry points:** The [project documentation](https://pnkraemer.github.io/probdiffeq/) and substantive [solver-design/selection guide](https://pnkraemer.github.io/probdiffeq/3_choose_the_right_solver/). Probabilistic uncertainty here should not be read as a universal rigorous error bound.

## Specialized numerical architectures

### 12. [bluescarni/heyoka](https://github.com/bluescarni/heyoka)

**Language/role:** C++; Taylor-method ODE integration with symbolic expressions, automatic differentiation, and LLVM JIT compilation.

Study an integrator generator: the expression system decomposes a vector field, differentiation rules generate high-order derivatives, and LLVM compiles the operations into a problem-specific time stepper.

- **C1:** Taylor order, adaptive step size, normalized derivatives, and polynomial propagation must agree numerically; the derivation is exposed in the [Taylor-method implementation tutorial](https://github.com/bluescarni/heyoka/blob/master/doc/tut_taylor_method.rst).
- **C3:** Generated code specializes evaluation to the equation. The [batch tutorial](https://github.com/bluescarni/heyoka/blob/master/doc/tut_batch_mode.rst) describes contiguous batch storage and reuse of outcome buffers to avoid per-step allocations.
- **C4:** The [dated changelog](https://github.com/bluescarni/heyoka/blob/master/doc/changelog.rst) spans the December 2020 initial release through 2026 and records LLVM compatibility changes, code-generation fixes, cache accounting, and changes to floating-point compilation flags.

**Entry points:** The Taylor-method tutorial and changelog above. This architecture requires an expressible symbolic vector field, a meaningful tradeoff compared with an arbitrary opaque right-hand-side callback.

### 13. [JuliaGNI/GeometricIntegrators.jl](https://github.com/JuliaGNI/GeometricIntegrators.jl)

**Language/role:** Julia; geometric, variational, partitioned, and projection-based integrators.

Study algorithms whose design is driven by dynamical structure and long-time behavior. The variational partitioned Runge–Kutta documentation develops stage equations from a discrete action and states the coefficient conditions for symplecticity.

- **C1:** Preserving geometric structure requires relationships among tableaux and projections. The documentation distinguishes regular from degenerate Lagrangians and explicitly marks unstable and experimental variants.
- **C2:** Problem types, Runge–Kutta methods, and projection choices combine through `GeometricIntegrator`; multiple projected variants reuse the underlying variational method.

**Entry point:** The substantial [variational partitioned Runge–Kutta chapter](https://github.com/JuliaGNI/GeometricIntegrators.jl/blob/main/docs/src/integrators/vprk.md). Its derivation and restrictions are more informative than a blanket claim of energy conservation; not every method is appropriate for every Hamiltonian or constrained system.

### 14. [fruzsinaagocs/oscode](https://github.com/fruzsinaagocs/oscode)

**Language/role:** C++ with a Python interface; specialized integration of oscillatory second-order linear ODEs.

Study a hybrid numerical method that evaluates both Runge–Kutta and WKB candidates, then chooses using predicted admissible step sizes. Frequency and damping data can come from interpolated input or functions.

- **C1:** The solve loop handles WKB truncation versus integration error, invalid WKB values, direction checks, and distinct dense-output paths after accepted RK or WKB steps.
- **C3:** WKB steps can traverse many oscillations when coefficients vary sufficiently slowly, with ordinary RK stepping covering other regimes. This is a problem-structure optimization, not a general-purpose speed claim.

**Entry point:** [The solution and method-switching implementation](https://github.com/fruzsinaagocs/oscode/blob/master/include/oscode/solver.hpp). The [repository explanation](https://github.com/fruzsinaagocs/oscode#about) states the restricted equation family and applicability condition; its changelog records dense-output and interface fixes.

## Smaller libraries with substantial solver machinery

### 15. [jacobwilliams/rklib](https://github.com/jacobwilliams/rklib)

**Language/role:** Modern Fortran; fixed and variable-step Runge–Kutta families.

Study object-oriented Fortran used to share integration policy across many method implementations. The main module separates a base integration class, fixed/variable-step subclasses, a step-size policy object, and method properties such as order, storage requirements, and FSAL behavior.

- **C1:** Explicit statuses cover malformed tolerance arrays, minimum step size, excessive step reductions, missing callbacks, and user cancellation. Event integration and adaptive policy add correctness obligations beyond the tableau arithmetic.
- **C2:** Deferred procedures specialize method steps while common classes handle equation callbacks, reporting, stopping, tolerances, and selectable real kinds.

**Entry point:** [The core module and type contracts](https://github.com/jacobwilliams/rklib/blob/master/src/rklib_module.F90). Its method-property descriptions expose low-storage and stability-preserving distinctions without requiring the reader to inspect every coefficient table first.

### 16. [princemahajan/FLINT](https://github.com/princemahajan/FLINT)

**Language/role:** Modern Fortran; adaptive explicit Runge–Kutta integration with dense output and multiple events.

Study the integration of error control, event actions, and interpolation in one solver engine. Equation systems and the `ERK_class` are separate, while initialization, stepping, integration, and interpolation occupy distinct source submodules.

- **C1:** Event actions may terminate or restart integration and modify state; interpolation coefficients must be recomputed when state or step length changes. After rejection, the controller prevents immediate step growth.
- **C2:** A common equation-system interface and ERK engine serve several methods, with event masks and event actions supporting hybrid dynamical applications.
- **C3:** The project separates hand-specialized DOP54/DOP853 steps from a generic tableau path and stores interpolation coefficients for repeated output queries. See the [project design description](https://github.com/princemahajan/FLINT) and [integration submodule](https://github.com/princemahajan/FLINT/blob/master/src/ERKIntegrate.f90).

**Entry point:** The integration submodule. **Maintenance qualification:** the [API snapshot](https://api.github.com/repos/princemahajan/FLINT) reported a last push in January 2024 and no archive flag; this entry does not imply current active maintenance.

### 17. [markmbaum/libode](https://github.com/markmbaum/libode)

**Language/role:** C++; dependency-light, class-based Runge–Kutta and related ODE methods.

Study a smaller inheritance-based solver design with visible adaptation and callback hooks. The adaptive base stores the prior solution, delegates method-specific error decisions, and commits or restores state depending on acceptance.

- **C1:** Rejected steps restore the solution without advancing time; the accepted-step path periodically checks solution integrity, and proposed steps are bounded by the integration endpoint and maximum step size.
- **C2:** The shared adaptive loop calls replaceable stepping, adaptation, rejection, and lifecycle hooks across many concrete methods.

**Entry point:** [The adaptive solver implementation](https://github.com/markmbaum/libode/blob/master/src/ode_adaptive.cc). The [repository scope](https://github.com/markmbaum/libode) explicitly excludes sparse matrices and dense output and notes incomplete adaptive support for some implicit methods. The [API snapshot](https://api.github.com/repos/markmbaum/libode) showed a June 2024 last push and no archive flag; use it as a bounded study project rather than infer a current support commitment.

## Large-system and parallel time-integration frameworks

### 18. [petsc/petsc](https://github.com/petsc/petsc)

**Language/role:** Primarily C; relevant subsystem: TS, PETSc's ODE/DAE time-stepping framework.

**Repository status:** Official substantive GitHub mirror of the project developed on GitLab, as identified by the repository itself.

Study integration of time stepping with distributed numerical data and nonlinear solves. The TS formulation separates an implicit residual from an explicit right-hand side, allowing method changes without rewriting the mathematical model.

- **C1:** Implicit Jacobians use the shifted combination `sigma * F_udot + F_u`; the manual derives why the shift depends on the integrator and step size. This avoids treating a residual Jacobian as merely the derivative of an explicit right-hand side.
- **C2:** Residual, right-hand-side, and Jacobian callbacks support explicit, implicit, and IMEX choices through the same TS interface.
- **C3:** The framework is built around MPI communicators and PETSc vector/matrix objects, with separate matrices available for the operator and preconditioner.

**Entry point:** The [TS manual chapter](https://petsc.org/release/manual/ts/), including its formulation, Jacobian derivation, and setup examples. The monorepo is counted once.

### 19. [trilinos/Trilinos](https://github.com/trilinos/Trilinos)

**Language/role:** C++; relevant subsystem: Tempus time integration and sensitivity analysis.

Study explicit ownership of integration state. An integrator drives the time loop; steppers attempt individual steps; `SolutionState` holds restartable state and metadata; `SolutionHistory` manages retained states; control strategies determine step size.

- **C1:** Failed-step recovery requires sufficient saved state, consistent initial conditions, and controlled retries. The documentation also warns that interpolated states need not preserve the governing conservation principles.
- **C2:** Steppers, observers, application actions, history policies, and control strategies are separate extension points. Applications can adopt the entire driver or compose selected pieces.
- **C3:** FSAL reuse reduces derivative evaluations, while history-retention policies support multistep methods and adjoint checkpointing without one universal storage policy.

**Entry point:** The [Tempus architecture reference](https://trilinos.github.io/docs/tempus/index.html). This report counts Trilinos once and focuses on Tempus, rather than presenting older and newer packages as separate repositories.

### 20. [Parallel-in-Time/pySDC](https://github.com/Parallel-in-Time/pySDC)

**Language/role:** Python; spectral deferred correction, multilevel SDC, and PFASST, with MPI and non-MPI configurations.

Study research infrastructure with reusable problem, level, sweeper, transfer, controller, and convergence-controller components. Although the project supports teaching and prototyping, its algorithm implementations and parallel orchestration go well beyond a tutorial repository.

- **C1:** Sweepers enforce triangular preconditioner structure and force a collocation update when the right endpoint is not a collocation node. The controller also explicitly rejects an obsolete MPI iteration-estimator mode whose broadcast pattern could deadlock.
- **C2:** Controllers assemble hooks and convergence policies independently from problem definitions and numerical sweepers.
- **C3:** Cached quadrature/preconditioner generators and explicit tracking of whether a sweeper is parallelizable connect mathematical choices to execution structure.

**Entry points:** [Sweeper implementation](https://github.com/Parallel-in-Time/pySDC/blob/master/pySDC/core/sweeper.py) and [controller implementation](https://github.com/Parallel-in-Time/pySDC/blob/master/pySDC/core/controller.py). These are stronger evidence than the presence of MPI alone.

### 21. [XBraid/xbraid](https://github.com/XBraid/xbraid)

**Language/role:** C/MPI with additional interfaces; multigrid reduction in time around existing time steppers.

Study how to add time parallelism without replacing an application's sequential stepping scheme. Applications supply state operations and a step callback; XBraid organizes a hierarchy in time and coordinates the iterative solution.

- **C1:** The callback contract specifies potentially aliased input/output vectors, optional forcing, refinement requests, and norms controlling global convergence. Packing buffers must satisfy size bounds for distributed communication.
- **C2:** User-defined application and vector types, stepping, cloning, freeing, summation, norms, and packing decouple the time solver from the spatial discretization and storage format.
- **C3:** Multigrid reduction targets the sequential dependency in time; temporal/spatial coarsening and relaxation are exposed as choices. The project itself qualifies applicability, noting that success has been strongest for problems with parabolic character.

**Entry points:** [Public callback and data contracts](https://github.com/XBraid/xbraid/blob/master/braid/braid.h) and the [project's algorithm/applicability explanation](https://github.com/XBraid/xbraid#about-xbraid). No universal parallel speedup is assumed.

## Coverage, search process, and limits

Live discovery used thirteen search formulations across these angles: general stiff/nonstiff C++ and Fortran ODE libraries; Julia/JAX/Rust integration; parallel-in-time SDC/PFASST/MGRIT; modern Fortran RK libraries; Java event-aware integration; probabilistic and geometric solvers; PyTorch batch adaptivity; Taylor/LLVM and oscillatory integration; PETSc/Trilinos transient frameworks; Rust solver traits; XBraid callback architecture; heyoka code generation; and less familiar stabilized/exponential/general ODE implementations. Later broad searches largely returned already covered engines, wrappers, adjacent applications, or small projects without stronger evidence of reusable numerical architecture.

The selection spans C, C++, Fortran, Java, Julia, Rust, and Python; scalar/small-system libraries, scientific Python interfaces, accelerator-oriented solvers, and distributed simulation infrastructure. Exponential, IMEX, multirate, and geometric families are represented within larger libraries rather than padded into separate entries. Established projects are balanced by smaller substantive implementations such as FLINT, libode, oscode, ode-solvers, and probdiffeq.

Excluded from separate counting were umbrella packages and language bindings around already selected engines, including DifferentialEquations.jl, Sundials.jl, and diffeqpy; generated wrappers; tutorial-only RK implementations; solver comparison/awesome lists; and application-specific simulations without a clearly reusable integration subsystem. Apache Commons Math was not added alongside its independently evolved Hipparchus descendant. This is principally an initial-value/time-integration survey, not a survey of symbolic ODE manipulation, boundary-value shooting software, or complete PDE discretization systems.

Every retained repository had its canonical GitHub identity checked and at least one additional primary implementation or substantive documentation source read. Some web-rendered pages were inaccessible; direct public source reads supplied the missing evidence. GitHub's unauthenticated API rate limit interrupted later tree browsing, which was completed with repository pages, raw files, and official documentation. A few developer-documentation stubs were inspected but not used as architectural evidence. No candidate code was executed, dependencies installed, or benchmarks reproduced.

Links generally follow current development branches or documentation rather than immutable commits, so details can evolve. Maintenance qualifications are based on the stated research snapshot, not a promise of support. Performance assessments identify concrete mechanisms and tradeoffs; numerical quality, stability, and speed still depend on the equation, tolerances, method, and hardware.
