# Interval arithmetic and validated numerics libraries

Research date: **2026-10-09**

This selection covers 20 GitHub repositories implementing interval or ball arithmetic, exact-real computation through enclosures, and reusable algorithms for validated roots, linear algebra, function approximation, constraints, and differential equations. It includes both arithmetic kernels and substantial libraries built on those kernels. General range containers, ordinary approximate numerical solvers, bindings without substantial independent algorithms, and individual computer-assisted proof scripts are outside the selection.

Repository identities and archival flags were checked against GitHub repository pages or the public API. Implementation and documentation entry points below were read, rather than inferred from search snippets. “Study” recommendations are engineering judgments drawn from that evidence; they are not certifications of correctness or claims that every component is exemplary. No candidate code was built or executed.

Criteria legend:

- **C1 — Difficult correctness:** numerical semantics, enclosure invariants, exceptional inputs, or failure handling that require careful reasoning.
- **C2 — Reusable abstractions:** substantial interfaces or representations supporting multiple algorithms and applications.
- **C3 — Performance with structure:** concrete computational costs addressed through understandable representations, algorithms, or policies.
- **C4 — Sustained evolution:** documented changes across years together with compatibility work, testing, or management of implementation complexity.

## Arithmetic kernels and numerical representations

### 1. [flintlib/flint](https://github.com/flintlib/flint)

**C; arbitrary-precision ball arithmetic within the FLINT monorepo.** The relevant subsystem is Arb: `arf`, `mag`, `arb`, `acb`, and the associated polynomial and matrix modules. Study how a common enclosure representation supports a large numerical API without requiring every operation to use the same precision internally.

- **C1:** An `arb_t` result must contain the exact operation on every choice of points in its input balls. The documentation specifies exact-result behavior, working-precision semantics, and special balls containing infinities or NaN. These are stronger contracts than merely computing extra digits. [Ball representation and semantics](https://github.com/flintlib/flint/blob/main/doc/source/arb.rst).
- **C2 / C3:** The architecture separates an arbitrary-precision midpoint from a small-precision magnitude bound, then builds complex balls, polynomials, power series, and matrices on top. This is a concrete representation-level cost decision, not a benchmark claim. [Subsystem architecture](https://github.com/flintlib/flint/blob/main/doc/source/overview.rst).

The former standalone Arb repository is archived following its 2023 merger into FLINT; it is not counted separately here.

### 2. [boostorg/interval](https://github.com/boostorg/interval)

**C++; header-only numeric interval library.** Study policy-based numerical programming where the rounding backend is part of the correctness contract, rather than an incidental implementation detail.

- **C1:** Rounding-policy constructors and destructors must establish and restore the floating-point rounding state; arithmetic and conversion operations separately provide upper and lower bounds. The documentation explicitly warns that using an “exact” policy with inexact floating-point types forfeits the inclusion guarantee.
- **C2 / C3:** Layered policies separate low-level rounding control, basic arithmetic, transcendental functions, and state protection. The `_opp` implementation reduces mode switching by keeping rounding upward and using sign transformations, with documented restrictions on mixing policies.

Both the extensibility contract and its performance tradeoffs are explained in the [rounding-policy guide](https://github.com/boostorg/interval/blob/develop/doc/rounding.htm). Compiler, floating-point environment, and policy choices therefore matter when assessing a particular use.

### 3. [JuliaIntervals/IntervalArithmetic.jl](https://github.com/JuliaIntervals/IntervalArithmetic.jl)

**Julia; interval arithmetic foundation for the JuliaIntervals ecosystem.** Study how interval semantics interact with a language's ordinary numeric conversions and promotion rules.

- **C1:** `Interval` carries both a decoration and an independent `isguaranteed` flag. Domain violations can degrade decorations, while implicit conversion from ordinary real values produces the `NG` marker. These mechanisms expose different reasons a downstream proof may be invalid. [Construction and decorations](https://github.com/JuliaIntervals/IntervalArithmetic.jl/blob/master/docs/src/manual/construction.md).
- **C2:** The separation between endpoint-only `BareInterval`, decorated `Interval`, and `ExactReal` gives generic numerical code distinct integration options. Explicit construction and exact-value annotations let functions participate in both ordinary and interval computations without silently treating all promoted values as trustworthy. [Guarantees and exact-number integration](https://github.com/JuliaIntervals/IntervalArithmetic.jl/blob/master/docs/src/manual/guarantee.md).

The repository states IEEE 1788-2015 compliance; this report does not independently establish standards conformance.

### 4. [unageek/inari](https://github.com/unageek/inari)

**Rust; machine-precision interval arithmetic with bare and decorated types.** This is a useful small-kernel study in making SIMD arithmetic readable enough to audit.

- **C1 / C3:** Arithmetic represents an interval through a negated lower endpoint and an upper endpoint. Addition uses upward-rounded vector operations; multiplication dispatches on sign and empty/zero classifications, with comments deriving the necessary lane shuffles and bounds. [Arithmetic implementation](https://github.com/unageek/inari/blob/main/src/arith.rs).
- **C4:** The 2020–2024 changelog records empty-interval deserialization fixes, malformed decimal handling, CPU-feature checks, minimum-Rust-version changes, and explicit breaking API migrations. This supplies evidence of numerical edge-case and compatibility management across years. [Changelog](https://github.com/unageek/inari/blob/main/CHANGELOG.md).

The documented target restrictions include Haswell-or-newer x86-64 and AArch64; some operations require GMP/MPFR. The checked repository last-push date was January 2025, so no claim of ongoing 2026 maintenance is made.

### 5. [nehmeier/libieeep1788](https://github.com/nehmeier/libieeep1788)

**C++; historical implementation of the preliminary IEEE P1788 standard.** Retained for its explicit standards-oriented architecture, not as evidence of current standards compliance or current toolchain support.

- **C1:** Representation validation handles empty intervals encoded with NaNs, illegal infinite endpoints, and combinations of interval contents with decorations. Invalid operands feed an explicit exception-signaling mechanism. [Validation implementation](https://github.com/nehmeier/libieeep1788/blob/master/p1788/flavor/infsup/setbased/mpfr_bin_ieee754_flavor_validation_func_impl.hpp).
- **C2:** `base_interval` separates the bound type, representation, concrete interval type, and a template `Flavor` that supplies semantics. It is a substantial example of making alternative interval semantics reusable through a common interface. [Base abstraction](https://github.com/nehmeier/libieeep1788/blob/master/p1788/infsup/base_interval.hpp).

The README emphasizes correctness over performance and describes the implementation as work in progress. GitHub metadata shows its last push in 2015.

### 6. [jinterval/jinterval](https://github.com/jinterval/jinterval)

**Java, with native test adapters; historical interval arithmetic and cross-library testing suite.** Counted once, including its rational arithmetic, interval implementations, and P1788 test launcher.

- **C1:** Tightest-enclosure contexts construct separate floor- and ceiling-rounded rational contexts. Exact, accurate-binary64, nearest, and plain contexts are distinct choices, so guarantees cannot be inferred from the interval type alone. [Context construction](https://github.com/jinterval/jinterval/blob/master/jinterval-interval-java/src/main/java/net/java/jinterval/interval/set/SetIntervalContexts.java).
- **C2:** The context interface also supports decoration adapters and evaluation of expression code lists. Separately, the test launcher adapts multiple native libraries and distinguishes containment failures from insufficient accuracy or tightness. This makes the repository useful for studying both arithmetic backends and numerical differential testing. [Launcher architecture and examples](https://github.com/jinterval/jinterval/blob/master/README.md).

The checked GitHub repository last changed by push in 2018; newer third-party package listings were not treated as evidence of newer repository development.

### 7. [mskashi/kv](https://github.com/mskashi/kv)

**C++; verified numerical computation with interval, affine, and power-series machinery.** Study how lightweight numeric templates compose into validated algorithms rather than stopping at scalar arithmetic.

- **C1 / C2:** The ODE routine operates on vectors of interval-valued power series, constructs candidate bounds, checks coefficient inclusion, and either accepts the step or follows restart/failure logic. The same function abstraction is evaluated through different series orders. [Validated ODE implementation](https://github.com/mskashi/kv/blob/master/kv/ode.hpp).
- **C3:** Affine arithmetic exposes a concrete cost-versus-enclosure choice: the source documents linear-cost multiplication and quadratic-cost alternatives intended to reduce the extra error term. Its coefficient-vector representation and configurable error-symbol treatment make the tradeoff inspectable. [Affine arithmetic implementation](https://github.com/mskashi/kv/blob/master/kv/affine.hpp).

The broader source tree contains multiple rounding backends; a reader should inspect the selected backend when porting the library to a new compiler or architecture.

### 8. [taschini/pyinterval](https://github.com/taschini/pyinterval)

**Python; historical arithmetic over finite unions of real intervals.** Its distinguishing abstraction is a possibly disconnected set, rather than one convex interval.

- **C1:** Arithmetic uses directed rounding for endpoint calculations, applies operations component by component, and canonicalizes the resulting union. This preserves useful disconnected results such as division across a denominator containing zero.
- **C2:** Immutable multi-interval values support ordinary arithmetic, scalar coercion, union, intersection, hulls, and component traversal through a common representation. The decorators implementing coercion and componentwise lifting are particularly useful architectural entry points.

These mechanisms and executable-style examples are in the [core interval implementation](https://github.com/taschini/pyinterval/blob/master/interval/__init__.py). The repository describes its finite-union model in the [project README](https://github.com/taschini/pyinterval/blob/master/README.rst). GitHub metadata shows a last push in 2017; modern Python compatibility was not tested.

## Exact-real computation through enclosures

### 9. [michalkonecny/aern2](https://github.com/michalkonecny/aern2)

**Haskell; a monorepo of interval and exact-real packages.** Focus on `aern2-mp` and `aern2-real`, rather than assuming every experimental package has equal readiness.

- **C1 / C2:** `MPBall` represents a variable-precision center with an error bound; exact reals are lazy converging sequences of balls. Comparisons can return a three-valued `Kleenean` instead of forcing an unjustified Boolean answer. The package documents algebraic property tests as set over-approximation properties for balls. [Arithmetic, backends, and testing](https://github.com/michalkonecny/aern2/blob/master/aern2-mp/README.md).
- **C4:** The 2017–2026 history records backend simplification, migration from MPFR to the CDAR-based implementation, GHC compatibility work, tests for valid balls, and changes to error propagation and comparison support. [Package changelog](https://github.com/michalkonecny/aern2/blob/master/aern2-mp/changelog.md).

The root README explicitly marks the univariate-function and function-representation benchmark components as broken on the main development branch and points to an older working branch.

### 10. [norbert-mueller/iRRAM](https://github.com/norbert-mueller/iRRAM)

**C++; historical exact-real arithmetic runtime.** Study how numerical uncertainty changes execution and control flow, not just the representation of numbers.

- **C1:** Converting an unresolved lazy Boolean to `bool` requests reiteration. The implementation caches resolved decisions outside limit computations, making repeated numerical execution and decision consistency explicit concerns. [Lazy Boolean implementation](https://github.com/norbert-mueller/iRRAM/blob/master/src/LAZY_BOOLEAN.cc).
- **C2:** The interface combines real, complex, rational, interval, matrix, and sparse-matrix abstractions with limit operators. It supports a dedicated computation entry point and library execution through `iRRAM_exec`, providing a reusable runtime boundary for exact-real calculations. [Interface and execution model](https://github.com/norbert-mueller/iRRAM/blob/master/doc/iRRAM.html).

The bundled manual calls itself an early version, and the checked repository last-push date is 2020. Treat it as an implementation study with historical documentation, not a promise of current build support.

## Validated roots, linear algebra, and function approximation

### 11. [JuliaIntervals/IntervalRootFinding.jl](https://github.com/JuliaIntervals/IntervalRootFinding.jl)

**Julia; rigorous root isolation by branch and bound.** A particularly clear example of keeping numerical search results separate from proof status.

- **C1:** A region is discarded only after proving absence of roots; existence and uniqueness produce `:unique`, while inconclusive small regions remain `:unknown`. A bisection-only contractor cannot prove existence or uniqueness. Decorations and the `NG` flag impose additional conditions on whether the result can be trusted. [Guarantee semantics](https://github.com/JuliaIntervals/IntervalRootFinding.jl/blob/master/docs/src/decorations.md).
- **C2 / C3:** `RootProblem` exposes iteration state and interchangeable Newton, Krawczyk, and bisection contractors. Breadth-first and depth-first traversal offer explicit memory and search-progress tradeoffs, including the risk of spending work near a singularity. [Search internals](https://github.com/JuliaIntervals/IntervalRootFinding.jl/blob/master/docs/src/internals.md).

This is worth studying for APIs that must return useful partial work without presenting unresolved numerical regions as established roots.

### 12. [JuliaIntervals/IntervalLinearAlgebra.jl](https://github.com/JuliaIntervals/IntervalLinearAlgebra.jl)

**Julia; interval linear systems and verified matrix computations.** Study the distinction between enclosing all solutions of uncertain systems and certifying a computation for a fixed floating-point system.

- **C1:** The epsilon-inflation interface returns an enclosure candidate together with a Boolean certificate. A false certificate explicitly means the returned candidate is not established as rigorous; it must not be accepted merely because a numerical vector was produced.
- **C2 / C3:** A common `solve(A, b, method, precondition)` interface separates direct and iterative methods from preconditioning. Alternatives include Gaussian elimination, Hansen–Bliek–Rohn, Krawczyk, and Gauss–Seidel, while Oettli–Präger methods address the shape of the solution set. Epsilon inflation is a specialized path for narrow or point data.

The [linear-systems tutorial](https://github.com/JuliaIntervals/IntervalLinearAlgebra.jl/blob/main/docs/src/tutorials/linear_systems.md) explains these interfaces and failure semantics. The [documentation overview](https://juliaintervals.github.io/IntervalLinearAlgebra.jl/stable/) identifies the related verified eigenvalue functionality. Documentation examples were not independently executed or mathematically audited.

### 13. [JuliaIntervals/TaylorModels.jl](https://github.com/JuliaIntervals/TaylorModels.jl)

**Julia; rigorous polynomial approximations with interval remainders.** Study representations that retain functional dependence beyond an ordinary interval evaluation.

- **C1:** Model constructors keep the polynomial, remainder, expansion point, and validity domain together. Checked constructors enforce domain inclusion and, for absolute models, a remainder containing zero. Absolute and relative remainders have explicitly different mathematical meanings. [Types and constructor invariants](https://github.com/JuliaIntervals/TaylorModels.jl/blob/master/src/constructors.jl).
- **C2:** Univariate and multivariate models compose through arithmetic and elementary functions. Range bounding can evaluate a model over subdivisions and combine their enclosures, providing reusable machinery for function inequalities and approximation bounds. [Range-bounding guide](https://github.com/JuliaIntervals/TaylorModels.jl/blob/master/docs/src/range_bounding.md).

The source also exposes unchecked constructors and mutable fields; constructor checks alone should not be mistaken for a universal invariant guarantee across every possible use.

### 14. [OlivierHnt/RadiiPolynomial.jl](https://github.com/OlivierHnt/RadiiPolynomial.jl)

**Julia; reusable infrastructure for a posteriori computer-assisted proofs.** Study the separation between finding a good approximation and verifying the mathematical hypotheses that make it meaningful.

- **C1:** The radii-polynomial method checks bounds on a fixed-point residual and derivative, then establishes existence and uniqueness only when a suitable radius satisfies the theorem's inequalities. The API reports whether validation succeeded. [Theorem and validation pipeline](https://github.com/OlivierHnt/RadiiPolynomial.jl/blob/main/docs/src/radii_polynomial_approach.md).
- **C2:** Sequence spaces, projections, linear operators, norms, and Taylor/Fourier/Chebyshev bases support more than finite-dimensional roots. The worked initial-value problem shows an approximate finite inverse combined with a tail operator and interval norm bounds. [Complete library-level example](https://github.com/OlivierHnt/RadiiPolynomial.jl/blob/main/README.md).

This is a library for assembling proof arguments; an application still has to formulate the correct space, operator, and bounds.

## Constraint processing and validated dynamics

### 15. [ibex-team/ibex-lib](https://github.com/ibex-team/ibex-lib)

**C++; interval constraint processing, system solving, and global optimization.** Study how a mathematical filtering invariant becomes an extensible solver architecture.

- **C1:** A contractor must shrink its input domain without removing feasible points. The documentation makes contraction and consistency explicit, and explains forward/backward expression evaluation rather than equating a smaller box with a correct box.
- **C2:** The central `Ctc::contract(IntervalVector&)` interface supports heterogeneous contractors. Composition, propagation, shaving, and constructive disjunction build more elaborate solvers from those components, avoiding a requirement that every contractor share one constraint representation.

The [contractor architecture guide](https://github.com/ibex-team/ibex-lib/blob/master/doc/contractor.rst) is the strongest entry point. The [repository overview](https://github.com/ibex-team/ibex-lib/blob/master/README.md) connects this architecture to guaranteed nonlinear-system enclosures and bounded global optimization.

### 16. [codac-team/codac](https://github.com/codac-team/codac)

**C++ with Python and MATLAB interfaces; interval domains, contractors, and uncertain trajectories.** This report examines the repository's `codac2` default branch. Study the extension of interval constraint programming from static boxes to time-dependent tubes.

- **C1:** `CtcLohner` first encloses trajectories throughout a time slice, then uses that enclosure to constrain the slice's endpoint gates. The documentation explicitly describes failure to establish a global enclosure and states that automatic step adjustment is not implemented for this contractor. [Lohner contractor](https://github.com/codac-team/codac/blob/codac2/doc/manual/manual/contractors/dynamic/ctclohner.rst).
- **C2:** A common catalog includes geometric, analytic, set, and dynamic contractors, together with separators for inner/outer set reasoning. This supports combining observations, nonlinear equations, and trajectory constraints rather than providing only a single robotics application. [Contractor and separator catalog](https://github.com/codac-team/codac/blob/codac2/doc/manual/manual/contractors/index.rst).

Examples or extensions written for Codac v1 should not be assumed to describe the reviewed branch.

### 17. [nasa/Kodiak](https://github.com/nasa/Kodiak)

**C++; rigorous nonlinear branch-and-bound library.** Study an extensible search engine whose problem-specific enclosure logic is separate from traversal and aggregation.

- **C1:** The library uses interval arithmetic through filib++ and Bernstein enclosures for polynomials and rational functions. Its documented applications include nonlinear feasibility, global optimization, and bifurcation sets, where a mistaken exclusion or bound changes the mathematical conclusion. [Project methods and scope](https://github.com/nasa/Kodiak/blob/master/README.md).
- **C2:** `BranchAndBoundDF<Expression, Answer, Environment>` separates evaluation, answer combination, variable selection, pruning, and local/global exits through hooks. It also supplies splitting, depth limits, instrumentation, and optional debug soundness checks. These are reusable algorithmic abstractions, not merely a collection of solved examples. [Branch-and-bound template](https://github.com/nasa/Kodiak/blob/master/src/BranchAndBoundDF.hpp).

The soundness hook is extensible and its base implementation is permissive; it is not an independent correctness verifier for arbitrary subclasses.

### 18. [CAPDGroup/CAPD](https://github.com/CAPDGroup/CAPD)

**C++; official CAPD::DynSys repository for computer-assisted dynamics.** The relevant subsystem is `capdDynSys`, together with its interval and linear-algebra foundations. Bundled third-party interval implementations are not counted as separate repositories.

- **C1:** `HighOrderEnclosure` computes Taylor-based enclosures for solutions and derivatives. It checks when remainder coefficients need recomputation, uses derivative information to distinguish monotone polynomial ranges, and carries integration context into solver exceptions. [Enclosure implementation](https://github.com/CAPDGroup/CAPD/blob/master/capdDynSys/include/capd/dynsys/HighOrderEnclosure.h).
- **C2 / C3:** That enclosure class is a policy for multiple rigorous solvers. The surrounding architecture separates maps and derivatives, ODE solvers, geometric set representations with Lohner methods, Poincaré maps, differential inclusions, and interval Newton tools. Reusable policies and specialized range evaluation expose both numerical structure and computational choices. [Module architecture](https://github.com/CAPDGroup/CAPD/blob/master/capdMake/docs/src/capdDynSys_package.dox).

CAPD contains both rigorous and nonrigorous solver variants; category fit does not make those variants interchangeable.

### 19. [robsontpm/capdDDEs](https://github.com/robsontpm/capdDDEs)

**C++; validated delay-differential-equation library built on CAPD.** Retained separately because it implements additional DDE solution representations and algorithms, not just bindings or a copied CAPD distribution.

- **C1:** `DDETaylorSolver` computes coefficient, Jacobian, and remainder enclosures over a time step. Its type selection deliberately requires the solution curve's set type to prevent use with the nonrigorous counterpart. The distinction between point jets and whole-step enclosures is documented in the interface.
- **C2 / C3:** A solver parameterized by a functional map works through associated curve, jet, matrix, time-point, and storage types. It collects reusable computation data and caps expansion order when the representation would otherwise become too expensive. [Solver interface and implementation](https://github.com/robsontpm/capdDDEs/blob/main/include/capd/ddes/DDETaylorSolver.h).

The [project overview](https://github.com/robsontpm/capdDDEs/blob/main/README.md) identifies the underlying DDE research and CAPD dependency, and labels its new 2026 CMake build system experimental.

### 20. [ariadne-cps/ariadne](https://github.com/ariadne-cps/ariadne)

**C++ with Python bindings; rigorous numerical framework and hybrid-system analysis.** Focus on its arithmetic, function-model, and validated-calculus layers, rather than treating the whole project only as a reachability application.

- **C1:** The function-model documentation distinguishes a uniform bound on function values from a bound on derivatives: a polynomial plus a uniform remainder alone cannot justify differentiation. It also distinguishes interval coefficients denoting fixed unknown values from coefficients denoting varying functions. [Function-model semantics](https://github.com/ariadne-cps/ariadne/blob/main/doc/function_models.dox).
- **C2:** Its type-system design separates effective, validated, approximate, upper, and lower information, with refinement and effort-controlled computation. This is a substantial architectural approach to making the quality and direction of numerical information part of reusable interfaces. [Type-system design](https://github.com/ariadne-cps/ariadne/blob/main/doc/type_system.dox).

Some cited material is conceptual design documentation rather than a promise that every sketched type signature is the current public API. The repository also contains concrete arithmetic, solver, and hybrid-system implementations.

## Search coverage and limitations

Discovery used more than six distinct query families: IEEE 1788 implementations in C++/Julia/Rust; arbitrary-precision ball arithmetic and Arb/FLINT; verified ODE and DDE libraries; interval contractors and robotics; Java interval contexts and conformance testing; Haskell and C++ exact-real arithmetic; Julia root isolation, linear algebra, and Taylor models; a posteriori radii-polynomial proofs; affine arithmetic; and legacy Fortran, OCaml, MATLAB, and MPFI-related searches. The later cross-language searches increasingly returned approximate solvers, applications, wrappers, package mirrors, or libraries hosted elsewhere. Affine arithmetic is represented substantively by kv rather than by adding every older affine package found.

Important boundaries and exclusions:

- **Arb consolidation:** The [standalone Arb repository](https://github.com/flintlib/arb) explicitly says it was merged into FLINT in 2023 and is archived. It is counted only through FLINT's relevant subsystem.
- **GitHub and provenance limits:** The [MPFI author's software page](https://perso.ens-lyon.fr/nathalie.revol/software.html) directs users to its development resources outside GitHub. This search did not establish an official substantive GitHub mirror for MPFI, C-XSC, GNU Octave's interval package, or INTLAB, so these important names were not padded into a GitHub-only list. Third-party copies and thin wrappers were not substitutes for verified provenance.
- **Historical status:** The API reported last pushes in 2015 for [libieeep1788](https://api.github.com/repos/nehmeier/libieeep1788), 2017 for [PyInterval](https://api.github.com/repos/taschini/pyinterval), 2018 for [JInterval](https://api.github.com/repos/jinterval/jinterval), 2020 for [iRRAM](https://api.github.com/repos/norbert-mueller/iRRAM), and January 2025 for [inari](https://api.github.com/repos/unageek/inari). None of these was marked archived at inspection. Push timestamps qualify activity statements; they do not establish correctness, sustained maintenance, or C4 by themselves.
- **Assurance limits:** Primary sources establish documented contracts and visible mechanisms. This was read-only research, not a standards-conformance campaign, build-compatibility test, numerical benchmark, or formal verification. In particular, backend selection, compiler rounding behavior, unresolved proof statuses, and unchecked APIs remain application-level review concerns.

The selection favors distinct numerical representations and reusable algorithmic designs. Shared dependencies are identified explicitly; the Julia algorithm packages and CAPD's DDE extension are retained because their independently implemented algorithms add substantial scope beyond the underlying arithmetic library.
