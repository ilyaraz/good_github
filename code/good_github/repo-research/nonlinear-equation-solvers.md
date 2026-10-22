# Nonlinear equation solvers

Research date: **2026-10-09**

This selection covers software for finding zeros of nonlinear scalar functions and systems, including Newton and quasi-Newton methods, accelerated fixed-point iteration, validated interval isolation, and polynomial homotopy continuation. It includes dedicated libraries and substantive solver subsystems within larger numerical libraries. Optimization and least-squares packages qualify here only when their inspected implementation directly supports nonlinear equation solving. Each monorepo appears once; the relevant subsystem is identified.

The 23 repositories below are a selection guide for experienced engineers studying numerical software architecture. The criteria are evidence-based judgments about particular subsystems, not a claim that every component is exemplary or appropriate for every problem.

## Criteria legend

- **C1 — Difficult correctness:** numerical semantics, invariants, convergence and failure distinctions, concurrency, or difficult inputs.
- **C2 — Reusable abstractions:** substantial interfaces and components that support multiple problems, algorithms, or execution models.
- **C3 — Performance with structure:** concrete treatment of evaluation, memory, factorization, or parallel-execution costs within an understandable design.
- **C4 — Sustained evolution:** documented evolution accompanied by compatibility work, testing, or management of accumulated complexity. Age alone does not qualify.

## Large-scale simulation infrastructure

### [petsc/petsc](https://github.com/petsc/petsc)

**Language/role:** C with language bindings; the **SNES** nonlinear solver subsystem. **Repository status:** this is the official substantive GitHub mirror; the repository identifies GitLab as the development home.

Study how a nonlinear iteration delegates linear systems and preconditioning to KSP and PC without prescribing the application's matrix representation. This is particularly useful for PDE applications where evaluating a residual, assembling a Jacobian, and constructing a preconditioner have very different costs.

- **C1:** The SNES manual explains inexact Newton tolerances, finite-difference perturbations relative to residual-evaluation noise, and convergence control. These expose numerical assumptions that a simple Newton loop hides.
- **C2:** Residual/Jacobian callbacks, nonlinear preconditioning, and the SNES/KSP/PC composition let applications replace numerical layers independently.
- **C3:** Matrix-free Jacobian products, separately assembled preconditioning matrices, and colored finite differences explicitly trade storage and residual evaluations against linear-solve quality.

**Entry point:** the [SNES manual](https://petsc.org/release/manual/snes/) develops these algorithms and interfaces together, including matrix-free operation and preconditioning.

### [trilinos/Trilinos](https://github.com/trilinos/Trilinos)

**Language/role:** C++; **NOX** nonlinear solves and **LOCA** continuation within the Trilinos monorepo.

Study the boundary between solver algorithms and application-owned linear algebra. NOX's abstract Group and Vector interfaces are also a useful example of extending a solver framework into continuation without requiring a completely separate application model.

- **C1:** Globalized Newton methods use line searches or trust regions; LOCA introduces augmented equations for continuation and bifurcation analysis, where singularity and parameterization become central correctness concerns.
- **C2:** NOX separates the nonlinear algorithm from concrete vector and operator implementations. LOCA extends those abstractions with parameter derivatives, predictors, and continuation step control.
- **C3:** The documented interfaces include colored finite differences and Jacobian-free Newton–Krylov operation. LOCA's bordered/augmented systems exploit structure rather than treating every continuation step as an unrelated dense solve.

**Entry point:** the official [NOX and LOCA architecture overview](https://trilinos.github.io/nox_and_loca.html). Some examples describe legacy Epetra interfaces; use it to understand the architecture, not as a guarantee that every historical integration is the current preferred API.

### [llnl/sundials](https://github.com/llnl/sundials)

**Language/role:** C with interfaces to other languages; **KINSOL**, the nonlinear-system solver within SUNDIALS.

KINSOL is an especially instructive implementation of scaled Newton iteration and the policy surrounding expensive Jacobian/preconditioner refreshes. Its mathematical documentation makes unsuccessful termination cases unusually explicit.

- **C1:** Solution and residual scaling are distinct. A sufficiently small residual can establish success, whereas a small step can indicate stalled iteration. The documentation also specifies line-search conditions and when failures trigger refreshed linearization data.
- **C2:** Vector, matrix, and linear-solver modules separate nonlinear iteration from storage and linear algebra, including user-provided implementations.
- **C3:** Modified and inexact Newton methods reuse Jacobians or preconditioners where appropriate. Matrix-free products, grouped banded differences, and forcing terms control the cost of approximate linear solves.

**Entry point:** [KINSOL mathematical considerations](https://sundials.readthedocs.io/en/latest/kinsol/Mathematics_link.html), including convergence tests, scaling, Jacobian updates, and linear-solver coupling.

## General frameworks and language ecosystems

### [SciML/NonlinearSolve.jl](https://github.com/SciML/NonlinearSolve.jl)

**Language/role:** Julia; a solver framework with native algorithms and integrations. Its component packages are counted together as one monorepo.

Study how a common problem description accommodates small static systems and large sparse systems while keeping algorithm choice, differentiation, and linear algebra replaceable.

- **C2:** The problem/algorithm interface separates the residual definition from nonlinear and linear solver selection. The [package documentation](https://docs.sciml.ai/NonlinearSolve/stable/) describes the shared interface across its solver families.
- **C3:** The [large-system tutorial](https://docs.sciml.ai/NonlinearSolve/stable/tutorials/large_systems/) works through sparse Jacobians, automatic differentiation, Krylov methods, and preconditioning. It explains when a Jacobian can remain implicit and when an explicitly formed matrix is useful for the preconditioner.

**Entry points:** the two guides above. The performance lesson is the arrangement of differentiation and linear algebra, not a universal speed ranking. One preconditioner example in the inspected tutorial is explicitly marked as skipped because of a Julia-version compatibility issue; its displayed results should not be treated as a fresh validation of that configuration.

### [scipy/scipy](https://github.com/scipy/scipy)

**Language/role:** Python with compiled numerical backends; **scipy.optimize.root** and the native nonlinear-iteration machinery in **_nonlin.py**.

This subsystem shows how a widely used public API accommodates MINPACK methods alongside native Broyden, Anderson, and Krylov implementations. It is included for that implementation and adaptation layer, rather than counted as another MINPACK wrapper alone.

- **C1:** The implementation separates residual and step tolerances, exposes nonconvergence, and handles line-search outcomes explicitly. These details determine what a returned iterate actually means.
- **C2:** A Jacobian protocol supports solving, updating, multiplying, and adapting an approximation as a preconditioner. Algorithms can share the nonlinear iteration without sharing one matrix representation.
- **C3:** Krylov and limited-information Jacobian approximations avoid requiring a dense Jacobian for every system.

**Entry points:** the [root API and method descriptions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.root.html) and [native nonlinear solver implementation](https://github.com/scipy/scipy/blob/main/scipy/optimize/_nonlin.py). The API includes least-squares-based methods; their termination semantics deserve attention when an actual zero is required.

### [JuliaNLSolvers/NLsolve.jl](https://github.com/JuliaNLSolvers/NLsolve.jl)

**Language/role:** Julia; nonlinear systems, fixed points, and mixed complementarity problems.

NLsolve is a relatively direct codebase for studying how trust-region and Newton algorithms share residual/Jacobian infrastructure. Its trust-region implementation is small enough to follow while still confronting singular linearizations and scaling.

- **C1:** The dogleg implementation checks the scaled trust-region geometry and catches singular Jacobian solves. It can compute a Moore–Penrose step through an SVD when the direct solve fails, rather than assuming every Newton system is invertible.
- **C2:** The repository exposes analytic, finite-difference, and automatic-differentiation paths behind shared problem machinery, with several nonlinear algorithms and complementarity support.
- **C3:** The trust-region solver maintains work buffers in a cache, making allocation decisions visible alongside the mathematical steps.

**Entry points:** [trust-region implementation](https://github.com/JuliaNLSolvers/NLsolve.jl/blob/master/src/solvers/trust_region.jl) and the [solver source directory](https://github.com/JuliaNLSolvers/NLsolve.jl/tree/master/src/solvers). The singular-Jacobian fallback is a mechanism to inspect, not a guarantee of convergence for singular problems.

### [patrick-kidger/optimistix](https://github.com/patrick-kidger/optimistix)

**Language/role:** Python/JAX; differentiable root finding, fixed-point solving, least squares, and optimization.

Study solver state as an explicit protocol in an array-programming ecosystem. The root-finding interface accepts structured PyTrees and separates the iterative solve from the adjoint used to differentiate its result.

- **C1:** The root API distinguishes thrown failures from returned result codes and documents implicit differentiation through a solve. Iteration termination and derivative semantics both matter when embedding roots inside a larger differentiable model.
- **C2:** Initialization, stepping, termination, and postprocessing are solver operations. The same interface accommodates different state structures and adaptation to least-squares or minimization algorithms.
- **C3:** Jacobian-structure tags can inform the associated Lineax linear solve, preserving information beyond an undifferentiated dense array.

**Entry point:** the detailed [root_find and solver-protocol reference](https://docs.kidger.site/optimistix/api/root_find/). When using an optimization-based adaptation, an optimizer's stopping condition alone should not be interpreted as proof that the original residual is zero; this is an engineering inference from the documented conversion.

### [datamole-ai/gomez](https://github.com/datamole-ai/gomez)

**Language/role:** Rust; native nonlinear-system and optimization algorithms.

Gomez is useful for studying a solver architecture expressed through Rust traits rather than a single application-specific numerical loop. Its driver layer lets callers retain control over progress and stopping decisions.

- **C1:** Its trust-region implementation documents a Powell dogleg approach and a Levenberg–Marquardt variant for cases where the Newton direction is unavailable. That fallback is a concrete response to problematic local linear models.
- **C2:** Problem, Domain, System, and Solver traits distinguish the mathematical problem, admissible inputs, algorithm, and execution driver. Callers can supply algorithms and custom stopping closures without replacing the entire problem representation.

**Entry points:** the [crate API and trait architecture](https://docs.rs/gomez/latest/gomez/) and [trust-region algorithm documentation](https://docs.rs/gomez/latest/gomez/algo/trust_region/index.html). The inspected API uses nalgebra abstractions; proposals for other linear-algebra backends are not treated as implemented features.

### [mathnet/mathnet-numerics](https://github.com/mathnet/mathnet-numerics)

**Language/role:** C#/.NET; the **RootFinding** subsystem, including multidimensional Broyden and scalar algorithms.

The Broyden source offers a compact, practical study of approximate-Jacobian iteration integrated with a general matrix library. Its dense linear algebra makes it more suitable as an architectural reference for modest systems than as a sparse large-scale solver.

- **C1:** The implementation scales finite-difference perturbations with the current variable, retries an unfavorable step with damping, and applies a rank-one Jacobian correction. It distinguishes failure-returning and exception-throwing public calls.
- **C2:** Function delegates and array inputs separate the user's equations from vector/matrix operations and factorization. The surrounding RootFinding API supplies alternative scalar strategies under the same numerical-library umbrella.

**Entry points:** the [Broyden API](https://numerics.mathdotnet.com/api/MathNet.Numerics.RootFinding/Broyden.htm) and [Broyden implementation](https://github.com/mathnet/mathnet-numerics/blob/master/src/Numerics/RootFinding/Broyden.cs). Inspect the actual residual test and failure paths when choosing tolerances; the presence of damping is not a global convergence guarantee.

### [cpmech/gosl](https://github.com/cpmech/gosl)

**Language/role:** Go with native numerical dependencies; the **num** package's nonlinear-system and scalar-solving facilities.

Study an application-oriented solver configuration that exposes sparse/dense Jacobian choices and linear-solver settings directly. Gosl is broader than root finding; only this subsystem is being evaluated here.

- **C1:** The nonlinear API exposes residual and step-related controls, iteration limits, and a Jacobian checker that compares derivatives and reports conditioning information. These are concrete aids for diagnosing user-supplied equations.
- **C2:** Residual and Jacobian callbacks, numerical differentiation, solver configuration, and output callbacks permit reuse across different models and monitoring needs.
- **C3:** The API distinguishes sparse and dense paths and supports retaining a constant Jacobian for modified Newton iteration. Its documentation explicitly describes the dense inverse-based path as inefficient and intended for small systems—a useful, candid representation tradeoff.

**Entry point:** the [num package reference](https://pkg.go.dev/github.com/cpmech/gosl/num), especially NlSolver, NlSolverConfig, and CheckJ. The larger library's C/Fortran dependencies matter when evaluating deployment; this is not presented as a dependency-free pure-Go stack.

## Dense, batched, and Fortran/R solver kernels

### [llnl/SNLS](https://github.com/llnl/SNLS)

**Language/role:** C++; small dense nonlinear systems, including batched execution on accelerator-oriented infrastructure.

SNLS addresses a different scale from PETSc: many small solves whose overhead, storage layout, and per-system convergence state matter. The batched dense dogleg implementation is a useful point of comparison with one-system-at-a-time APIs.

- **C2:** A templated residual/Jacobian contract and compile-time problem dimension separate the model from the solver. Static checks make the required interface explicit.
- **C3:** The batched implementation allocates working arrays during initialization, then uses RAJA views and CHAI-managed storage for repeated work. Residual norms, trust radii, evaluation counts, and statuses are maintained per system, exposing the structure needed to manage a batch rather than hiding it in a generic callback loop.

**Entry points:** the [solver source directory](https://github.com/llnl/SNLS/tree/develop/src) and the inspected [batched dense dogleg implementation](https://raw.githubusercontent.com/LLNL/SNLS/develop/src/SNLS_TrDLDenseG_Batch.h). These are architectural observations, not a measured CPU/GPU speed comparison.

### [fortran-lang/minpack](https://github.com/fortran-lang/minpack)

**Language/role:** modern Fortran; modernization of the historical MINPACK nonlinear-equation and nonlinear-least-squares library.

This is a strong study of preserving established numerical algorithms while modernizing their packaging and interfaces. The hybrid solver combines finite-difference Jacobians, QR-related updates, and trust-region dogleg steps.

- **C1:** HYBRD exposes variable scaling, finite-difference bandwidths, evaluation budgets, and distinct termination codes. Its implementation makes the relationship between Jacobian approximation, step acceptance, and lack of progress inspectable.
- **C2:** Analytic/numerical Jacobian variants and simplified/full-control entry points serve different caller requirements while retaining a common numerical core.
- **C4:** The repository documents the original 1980 library, later GitHub maintenance, and the 2021 modernization to free-form Fortran, with CI-oriented tests and a C API. This is evidence of managed evolution, not a claim that the GitHub repository itself dates to 1980.

**Entry point:** the [HYBRD API and included source](https://fortran-lang.github.io/minpack/proc/hybrd.html); the repository's history section explains the modernization and testing work.

### [devernay/cminpack](https://github.com/devernay/cminpack)

**Language/role:** C/C++; a substantive C-oriented reworking of MINPACK. It shares mathematical lineage with the preceding project and is not an independent algorithm family.

Study what numerical-library portability entails beyond translating arithmetic: calling conventions, callback context, precision choices, reentrancy, and comparisons with a reference implementation.

- **C1:** The rewrite removes mutable static working state and introduces callback user data. This supports reentrant use, while leaving synchronization of shared user data to the caller. Reference comparisons explicitly account for numerical differences in iteration histories and final digits.
- **C2:** Conventional C arguments, context-bearing callbacks, and precision variants make the algorithms reusable beyond the original Fortran calling model.
- **C4:** The project history explains successive translation/rewrite stages and testing against reference outputs, including CTest integration and comparisons with the Fortran implementation.

**Entry point:** the author's [CMinpack implementation, interface, history, and testing notes](https://devernay.github.io/cminpack/). The selection is justified by distinct engineering evolution; it should not be counted as extra evidence that the underlying MINPACK algorithms are unrelated implementations.

### [jacobwilliams/nlesolver-fortran](https://github.com/jacobwilliams/nlesolver-fortran)

**Language/role:** modern Fortran; object-oriented nonlinear solves with dense and sparse linear algebra, including rectangular systems.

This project exposes the integration work often concealed behind a Newton-method label: how dimensions, bounds, norms, Jacobian storage, and linear solvers change the actual iteration.

- **C1:** The API makes bound-handling modes, line-search behavior, and norm selection explicit. Square and rectangular linearized systems require different linear-algebra paths, rather than assuming every Jacobian is an invertible square matrix.
- **C2:** The solver type accepts residual, dense or sparse Jacobian, norm, and custom sparse-linear-solver callbacks. The sparse callback contract specifies coordinate indices, values, and status reporting, providing a concrete extension boundary.
- **C3:** Dense LAPACK and sparse solver choices let the implementation reflect matrix shape and storage costs rather than always constructing one dense representation.

**Entry point:** the generated [nlesolver_module interface and implementation documentation](https://jacobwilliams.github.io/nlesolver-fortran/module/nlesolver_module.html), especially nlesolver_type and the Jacobian/linear-solver callback interfaces.

### [bertcarnell/nleqslv](https://github.com/bertcarnell/nleqslv)

**Language/role:** R with a Fortran numerical core; Newton and Broyden methods for nonlinear systems.

Nleqslv is particularly useful for studying a user-facing contract around difficult termination and globalization choices. Its documentation is candid about cases in which a numerical workaround can produce misleading convergence.

- **C1:** Nonfinite function values, invalid Jacobians, ill-conditioning, small steps, and small residuals receive different treatment. The optional singular-Jacobian workaround is documented as potentially causing spurious convergence, rather than presented as universally safe.
- **C2:** Users can choose Newton/Broyden, several line searches and trust-region strategies, scaling, and analytic or numerical Jacobians through one result model.
- **C3:** Broyden updates reuse Jacobian information through QR-related work; banded numerical Jacobians reduce the required function evaluations for suitable systems.

**Entry point:** the detailed [nleqslv reference](https://bertcarnell.github.io/nleqslv/reference/nleqslv.html). Also inspect its documented nonrecursive restriction before using a nonlinear solve inside the residual callback of another solve.

## Scalar root finding

### [JuliaMath/Roots.jl](https://github.com/JuliaMath/Roots.jl)

**Language/role:** Julia; scalar bracketing, derivative-based, and derivative-free root methods.

Roots is valuable for studying the gap between textbook scalar iteration and floating-point stopping semantics. It also shows how a focused package can offer many methods without requiring a different problem definition for each one.

- **C1:** Separate tolerances govern changes in the independent variable and the residual. The reference explains strict versus relaxed acceptance and different failure behavior between interfaces. Finding several roots heuristically is not represented as validated isolation of every root.
- **C2:** Algorithm objects work with function-only or derivative-bearing inputs. ZeroProblem/CommonSolve integration and iteration facilities separate the mathematical problem, method, and execution pattern.

**Entry point:** the [Roots reference manual](https://juliamath.github.io/Roots.jl/dev/reference/), especially find_zero, ZeroProblem, tolerances, and bracketing methods. This is the development documentation inspected during research, so API details should be matched to a chosen package release.

### [boostorg/math](https://github.com/boostorg/math)

**Language/role:** generic C++; the **Boost.Math root-finding tools**, not the entirety of Boost.Math.

Study safeguarded Newton, Halley, and Schröder iteration through a generic numeric interface. The documentation discusses concrete failures—zero derivatives, bounds, and nearly infinite derivatives—instead of treating high-order convergence as sufficient engineering justification.

- **C1:** Derivative methods fall back to safer steps when derivatives or proposed iterates are unsuitable. The guide explains how inaccurate derivatives and tiny steps can affect termination, and why bounding intervals matter.
- **C2:** Callable objects return the required function/derivative values, while templated numeric types and requested precision make the same algorithms usable across different arithmetic types.

**Entry points:** the [derivative-based root-finding guide](https://www.boost.org/doc/libs/latest/libs/math/doc/html/math_toolkit/roots_deriv.html) and [roots.hpp](https://github.com/boostorg/math/blob/develop/include/boost/math/tools/roots.hpp). The guide's advice on choosing precision is especially useful when higher-order iterations cost more function or derivative work.

### [Hipparchus-Math/hipparchus](https://github.com/Hipparchus-Math/hipparchus)

**Language/role:** Java; **hipparchus-core analysis.solvers**, including bracketed and derivative-based scalar methods.

This is a useful object-oriented counterpart to the template- and multiple-dispatch-based libraries above. Its result-side policy illustrates an API detail that becomes important when repeatedly finding nearby events or roots.

- **C1:** Bracketed solvers can require an answer on a particular side of a root, helping callers avoid rediscovering the same crossing. The guide also explains stagnation in false-position methods and how Illinois/Pegasus updates address it. Evaluation limits and numerical tolerances are explicit.
- **C2:** Separate function and solver interfaces accommodate ordinary, differentiable, and polynomial functions. Algorithm selection and allowed-solution policies can change without embedding those choices into the function implementation.

**Entry point:** the official [analysis and root-solving guide](https://www.hipparchus.org/hipparchus-core/analysis.html), including solver interfaces, bracketed solvers, and convergence controls. The repository is counted once for its own substantial library implementation, not alongside a second entry for its Commons Math ancestry.

## Validated roots and polynomial systems

### [JuliaIntervals/IntervalRootFinding.jl](https://github.com/JuliaIntervals/IntervalRootFinding.jl)

**Language/role:** Julia; interval-based root isolation for scalar and multidimensional functions.

Study a solver whose result includes a logical classification of regions, rather than only a floating-point candidate. It is particularly useful for understanding why certification, search completeness, and numerical approximation are separate concerns.

- **C1:** Boxes are classified as empty, uniquely containing a root, or unresolved. Multiple roots and boundary cases can remain unknown; plain bisection does not itself certify existence. Guarantees rely on appropriate interval evaluation and the documented contractor conditions.
- **C2:** RootProblem and its search state separate branch-and-bound traversal from Newton, Krawczyk, or bisection contractors. The search can be iterated and its traversal strategy varied without rewriting interval contraction.

**Entry points:** the [search and contractor internals](https://juliaintervals.github.io/IntervalRootFinding.jl/stable/internals/) and [root-finding reference](https://juliaintervals.github.io/IntervalRootFinding.jl/stable/roots/). The statuses are part of the result contract; an unknown box should not be silently promoted to a certified solution.

### [ibex-team/ibex-lib](https://github.com/ibex-team/ibex-lib)

**Language/role:** C++; interval constraint programming, specifically **IbexSolve** and the generic equation-solving framework.

Ibex connects nonlinear equations with inequalities and underdetermined solution sets. Its solver architecture is worth studying when root finding means covering a feasible region rather than converging from one starting point.

- **C1:** Output distinguishes solution, boundary, unknown, and pending boxes. Singular regions or exhausted precision can remain unresolved; a time limit can leave pending regions. Those categories preserve information that a single success flag would lose. See the [current repository's solver documentation](https://github.com/ibex-team/ibex-lib/blob/master/doc/solver.rst).
- **C2:** The generic solver composes a contractor, bisector, and cell buffer. This separates mathematical pruning from subdivision and search order; the [programmer guide](https://ibex-lib.readthedocs.io/en/latest/solver.html) demonstrates composition with interval Newton and other contractors.

**Entry points:** the two guides above. The inspected hosted programmer guide identifies itself as an older documentation version and includes thread-safety caveats. Validated search can be expensive, and the current solver guide does not promise a bounded completion time.

### [JuliaHomotopyContinuation/HomotopyContinuation.jl](https://github.com/JuliaHomotopyContinuation/HomotopyContinuation.jl)

**Language/role:** Julia; numerical solution of polynomial systems by homotopy continuation, with separate certification facilities.

Study the machinery needed when Newton correction is one component of a path-tracking algorithm. Following paths toward singular endpoints or infinity raises different issues from solving once near a regular root.

- **C1:** Endgame tracking handles difficult endpoints through Cauchy endgames and monitors divergence using valuation-related information. Separately, interval Krawczyk certification can verify appropriate nonsingular candidate solutions and distinguish duplicates; path-tracking output and certification are different stages.
- **C2:** System/homotopy descriptions, ordinary trackers, endgame trackers, path results, and certification interfaces form reusable layers. This supports inspecting or replacing parts of the computation without reducing everything to one opaque solve call.

**Entry points:** [endgame tracker architecture](https://www.juliahomotopycontinuation.org/HomotopyContinuation.jl/stable/endgame_tracker/) and [certification semantics](https://www.juliahomotopycontinuation.org/HomotopyContinuation.jl/stable/certification/). The documented certification scope includes affine square polynomial systems; certifying supplied candidates is not, by itself, proof that an arbitrary system has no other roots.

### [janverschelde/PHCpack](https://github.com/janverschelde/PHCpack)

**Language/role:** Ada numerical core with C/C++, Python, and accelerator-related components; polynomial homotopy continuation.

PHCpack offers a different implementation tradition and a broader historical view of polynomial-system solving. It includes work on isolated roots, singularities, and positive-dimensional solution sets, rather than only a single Newton corrector.

- **C1:** Deflation addresses singular solutions, while higher-precision arithmetic supports difficult path tracking. These mechanisms make conditioning and multiplicity explicit parts of the implementation.
- **C3:** The documentation discusses parallel path tracking and higher precision together: independent paths offer parallel work, while extra precision increases computational cost.
- **C4:** The development history records successive additions such as polyhedral methods, cascades, monodromy, deflation, and precision/parallel work. It also describes per-directory Ada test programs and evolution of the build tooling, providing evidence beyond repository age.

**Entry point:** the source-controlled [implementation, testing, and development-history guide](https://github.com/janverschelde/PHCpack/blob/master/src/doc/source/welcome.rst). Historical published algorithm versions are part of its lineage; this entry refers to the substantive GitHub codebase, not merely the old publication artifact.

## Algorithm-focused reference implementation

### [ctkelley/SIAMFANLEquations.jl](https://github.com/ctkelley/SIAMFANLEquations.jl)

**Language/role:** Julia; standalone implementations accompanying Kelley's nonlinear-equations book. **Status:** the repository describes the package as feature-frozen, retaining bug/typo fixes and a stable public API.

This is included despite its educational role because it contains substantive Newton–Krylov, Anderson, and related implementations, with explicit workspaces and production-relevant numerical controls. It favors inspectable algorithms over a growing general framework.

- **C1:** The Newton–Krylov solver documents forcing-term control, Armijo globalization, finite-difference Jacobian-vector products, and the distinction between inner linear-solve trouble and failure of the outer nonlinear solve.
- **C3:** Preallocated Krylov storage, optional lower-precision basis storage, user-provided Jacobian/preconditioner products, and reusable solver data expose real memory and evaluation costs. Documentation also explains when a returned solution aliases reusable storage and needs copying.

**Entry point:** the [nsoli implementation and extensive interface documentation](https://github.com/ctkelley/SIAMFANLEquations.jl/blob/master/src/Solvers/nsoli.jl). It is a substantial algorithmic reference with a deliberately limited evolution policy, not an actively expanding solver framework.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, followed by direct reading of canonical GitHub pages and implementation or documentation sources for every retained repository. Representative search angles included:

- Nonlinear-system libraries using Newton, trust-region, and quasi-Newton methods.
- PETSc SNES, SUNDIALS KINSOL, and Trilinos NOX/LOCA simulation infrastructure.
- Modern MINPACK, Fortran nonlinear solvers, and R's nleqslv ecosystem.
- Julia solver frameworks and Rust trait-based nonlinear-solving libraries.
- JAX root finding, implicit differentiation, and solver-state abstractions.
- Go, Java, and .NET root-finding implementations.
- Interval Newton, Krawczyk operators, certified root isolation, and constraint contractors.
- Polynomial homotopy continuation, singular endgames, and multiprecision path tracking.
- Anderson acceleration, Newton–Krylov, and continuation libraries outside the best-known numerical stacks.

Later queries increasingly rediscovered these families or produced smaller application-specific codes, tutorials, wrappers, and optimization-only projects. This is a representative selection rather than an exhaustive census. Ceres/Ipopt-style optimization-first libraries, standalone trust-region subproblem solvers, applications merely calling another solver, and wrapper-only packages were excluded. Candidates without a verified substantive GitHub home, or whose additional primary implementation evidence could not be retrieved, were not retained. Star counts were not selection evidence.

Canonical repository pages and the linked additional sources were opened, not accepted solely from search snippets. PETSc's mirror status, the shared MINPACK lineage, larger-library subsystem boundaries, and the book package's feature freeze are called out explicitly. No retained repository was classified as archived from the inspected pages; this is not a systematic maintenance-health audit. C4 is used selectively where development history and testing or compatibility work were actually documented.

No candidate code was executed and no benchmarks were reproduced. Performance assessments concern documented mechanisms—sparsity, reuse, matrix-free products, storage, and parallel paths—not comparative speed claims. Hosted documentation can describe a different release from a repository's default branch; identified version caveats are stated where they affect interpretation. The suggestions about what an engineer can learn, and the mapping to C1–C4, are grounded editorial judgments rather than project-authored endorsements.
