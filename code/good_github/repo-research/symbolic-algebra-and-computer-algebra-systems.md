# Symbolic algebra and computer algebra systems

Research date: **2026-10-09**.

This selection covers **26 GitHub repositories** implementing general computer algebra systems, symbolic expression engines, exact polynomial and discrete algebra, tensor manipulation, and reusable symbolic libraries. It includes both interactive systems and the mathematical kernels that make them possible. Numerical-only libraries, thin language bindings, interfaces to proprietary CAS products, and symbolic-regression applications are outside the main scope.

Each repository page and at least one additional substantive primary source were opened and read. The criteria below are engineering judgments grounded in the linked material, not certifications of mathematical correctness or claims that every subsystem is exemplary. Source links generally follow the inspected development or stable branch and can change after this date. Maintenance is not inferred from stars or a recent push; historical and licensing qualifications appear where relevant.

## Criteria legend

- **C1 — Difficult correctness:** mathematical invariants, exact/numerical semantics, concurrency, difficult inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial representations, interfaces, or algorithms supporting multiple mathematical domains or applications.
- **C3 — Performance with structure:** concrete strategies for computational cost, memory use, or parallelism, with an architecture that can be studied.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate management of implementation complexity.

## General-purpose systems and evaluation languages

### 1. [sympy/sympy](https://github.com/sympy/sympy)

**Language / role:** Python; general-purpose symbolic mathematics library and CAS.

Study how a large mathematical library builds transformations on a common expression protocol while preserving uncertainty about mathematical properties. The most instructive starting point is the relationship between expression structure and assumptions, rather than any single integration algorithm.

- **C1:** Assumption queries distinguish true, false, and unknown. The documentation shows why an unconstrained symbol does not justify reducing `sqrt(x**2)` to `x`, and why equivalent expressions can yield different amounts of inferred information. Consumers must preserve the unknown case. [Assumptions guide](https://docs.sympy.org/latest/guides/assumptions.html).
- **C2:** `Basic` supplies shared expression arguments, structural comparison, hashing, substitution, matching, and traversal machinery. These are reusable contracts beneath many different mathematical objects, not a collection of unrelated formula handlers. [Core implementation](https://github.com/sympy/sympy/blob/master/sympy/core/basic.py).

### 2. [sagemath/sage](https://github.com/sagemath/sage)

**Language / role:** Python and Cython, with native dependencies; integrated mathematical software system. Relevant subsystem: Sage's own parent, element, and coercion infrastructure.

Sage is especially valuable for studying interoperability that has mathematical meaning. Combining an integer polynomial and a rational number requires selecting an appropriate result domain, not merely converting both values to a convenient machine type.

- **C1:** The coercion model distinguishes canonical coercions from explicit, potentially partial conversions. Its contract requires compatible coercions to form a commuting diagram, subject to documented rounding qualifications, and raises `TypeError` when binary-operation resolution fails.
- **C2:** Parents describe algebraic domains; elements, coercion maps, and actions support arithmetic across those domains. The same mechanism also handles scalar actions, such as multiplying a point on an elliptic curve by an integer.
- **C3:** Discovered coercions and actions are cached. This connects the high-level mathematical interface to a concrete strategy for reducing repeated dispatch work.

All three are explained with executable examples in the [coercion implementation and its extensive module documentation](https://github.com/sagemath/sage/blob/develop/src/sage/structure/coerce.pyx).

### 3. [fricas/fricas](https://github.com/fricas/fricas)

**Language / role:** SPAD, Boot, and Lisp; general-purpose CAS with a strongly typed algebra library. FriCAS is a substantively evolved Axiom fork, not a duplicate mirror.

Study a design in which mathematical domains and their interfaces are themselves programmable objects. This is an unusually direct connection between abstract algebra and a language's type organization.

- **C1:** Available operations depend on the coefficient domain: the documented example gives a sparse univariate polynomial domain Euclidean-domain capabilities when its coefficients form a field, but not automatically over the integers.
- **C2:** Parameterized domains and categories compose polynomial rings, complex domains, modules, and vector spaces. User-defined constructors participate in the same library mechanism as supplied constructors. [Type-system walkthrough](https://fricas.github.io/fricas-notebooks/FriCAS-Types.html).
- **C4:** The changelog records compiler restructuring and crash fixes in 2015, portability and interpreter fixes in 2020, and cache recycling, bootstrap changes, and SBCL compatibility fixes in 2026. This supports sustained complexity management rather than age alone. [ChangeLog](https://github.com/fricas/fricas/blob/master/ChangeLog).

### 4. [reduce-algebra/reduce-algebra](https://github.com/reduce-algebra/reduce-algebra)

**Language / role:** Standard Lisp and RLISP, with Lisp runtimes in the distribution; general-purpose CAS. **Officially linked GitHub mirror:** development is mirrored from SourceForge Subversion, as confirmed by the [REDUCE project's own site](https://reduce-algebra.sourceforge.io/projects.php).

The algebra simplifier is a useful study of extensible symbolic evaluation in a Lisp system. Count the algebra packages and bundled runtimes as one repository.

- **C1:** The simplifier converts prefix expressions into canonical algebraic forms, handles cancellation and rationalization, preserves and restores evaluation state, and explicitly revisits GCD checking when leading-term cancellation requires it. Noncommutative declarations also affect simplification state.
- **C2:** Operator properties such as `simpfn`, matching rules, and type-specific element handlers dispatch into specialized simplifiers. This supports a broad package ecosystem through a shared evaluation mechanism.

The main implementation entry point is [`packages/alg/simp.red`](https://github.com/reduce-algebra/reduce-algebra/blob/master/packages/alg/simp.red). Its global-state conventions are also a useful boundary to examine when considering embedding or concurrent use.

### 5. [Mathics3/mathics-core](https://github.com/Mathics3/mathics-core)

**Language / role:** Python; symbolic language kernel implementing Mathematica/Wolfram-language-style evaluation. This is the evaluator and built-in implementation, not merely a notebook frontend.

Study the interaction between symbolic language semantics, mutable definitions, and evaluation caching. Using SymPy for some mathematical operations does not eliminate Mathics' substantial independent evaluator.

- **C1:** Expression evaluation must respect holding, flattening, sequence, and ordering attributes. Its metadata cache tracks symbols and definition timestamps so a previously evaluated expression can be reconsidered when definitions change.
- **C2:** Expressions share head-and-elements representation, conversion, structural comparison, and rewriting machinery across built-ins and user definitions.
- **C3:** `ExpressionCache` avoids unnecessary reevaluation using dependency metadata; the implementation also uses iterative structural equality to reduce Python recursion pressure.

Start with [`mathics/core/expression.py`](https://github.com/Mathics3/mathics-core/blob/master/mathics/core/expression.py), then the surrounding [core modules](https://github.com/Mathics3/mathics-core/tree/master/mathics/core), including definitions, rules, and evaluation.

### 6. [axkr/symja_android_library](https://github.com/axkr/symja_android_library)

**Language / role:** Java; Symja/Matheclipse symbolic language and mathematical library. Relevant monorepo subsystem: `symja_android_library/matheclipse-core`, not just the Android examples suggested by the repository name.

Study a stateful evaluator that combines symbolic rewrites, configurable numerical precision, user definitions, and resource limits behind an embeddable Java API.

- **C1:** `EvalEngine` is explicitly marked `NotThreadSafe`; the supplied current-engine access uses thread-local instances. Evaluation distinguishes held arguments and numerical modes and provides recursion, iteration, and timeout handling. These are real embedding and concurrency constraints.
- **C2:** A shared `IExpr`/`IAST` representation and function-evaluator interfaces let built-ins and rewrite rules participate in one engine rather than requiring separate evaluators for algebra, calculus, and numerical functions.

The detailed class documentation and implementation in [`EvalEngine.java`](https://github.com/axkr/symja_android_library/blob/master/symja_android_library/matheclipse-core/src/main/java/org/matheclipse/core/eval/EvalEngine.java) provide a substantive entry point, including evaluation-state restoration and cached fixed-point information.

## Native symbolic and exact-arithmetic kernels

### 7. [symengine/symengine](https://github.com/symengine/symengine)

**Language / role:** C++; standalone symbolic manipulation kernel with language bindings maintained separately.

SymEngine is a particularly clear case study in using strong internal invariants to make mathematical operations cheaper. Its design discussion exposes the tradeoff between convenient general constructors and specialized operations that already know their inputs are canonical.

- **C1:** `Add`, `Mul`, and `Pow` have representation restrictions checked by `is_canonical()` when assertions are enabled. Examples include coefficient restrictions and representing integral rationals as integers.
- **C3:** Algorithms can construct an already-canonical representation without repeating general simplification; debug checks and optimized builds serve different purposes. The design also discusses reference-count traffic and checked pointer access rather than treating allocation costs as invisible.
- **C2:** General `add`, `mul`, `pow`, and rational-construction functions provide a reusable boundary for callers that cannot establish the stronger internal preconditions.

Read the [design document](https://symengine.org/design/design.html) alongside the repository's build/testing description. Some design sections discuss historical proposals; the canonical-construction contract is the specific material highlighted here.

### 8. [flintlib/flint](https://github.com/flintlib/flint)

**Language / role:** C; exact arithmetic, polynomial, and algebraic computation kernel. Relevant subsystem: multivariate polynomial arithmetic, rather than every numerical facility in FLINT.

Study the explicit representation and memory contracts that a high-level CAS can hide. FLINT 3 incorporated formerly separate Arb, Antic, Calcium, and Generic-Rings libraries; they are not counted again as independent projects here.

- **C1:** Integer multivariate polynomials have a documented canonical form: nonzero coefficients and descending term order. Low-level construction can temporarily violate this, so canonicality checks and term-combination operations matter.
- **C2:** A context object carries the parent ring's variable count and monomial ordering, separating domain information from individual polynomial storage.
- **C3:** The API exposes heap-based, array-based, dense, and threaded multiplication strategies, including explicit failure returns for attempted strategies and controls over coefficient/exponent allocation.

The inspected [`fmpz_mpoly` reference](https://github.com/flintlib/flint/blob/main/doc/source/fmpz_mpoly.rst) is both an API entry point and a substantial guide to internal invariants and algorithm selection. No relative benchmark claim is needed to establish these engineering constraints.

### 9. [symbolica-dev/symbolica](https://github.com/symbolica-dev/symbolica)

**Language / role:** Rust with Python bindings; symbolic expression and polynomial computation library. **Source-available, not an unrestricted open-source reuse option:** the inspected [license](https://github.com/symbolica-dev/symbolica/blob/main/License.md) imposes substantial use and redistribution conditions.

Study the interface between owned symbolic expressions, borrowed views, and extensible mathematical behavior. This entry is useful for architectural inspection; licensing is a material distinction from most other entries.

- **C1:** Custom function behavior has explicit contracts, including normalized results from derivative callbacks. Function attributes and expression normalization affect mathematical identity, so extensions cannot be treated as arbitrary display hooks.
- **C2:** A common atom model covers coefficients, symbols, functions, sums, products, and powers, with shared transformation and conversion facilities.
- **C3:** `AtomView` supplies immutable borrowed variants alongside owned expressions. This gives a concrete place to study avoiding unnecessary expression copies; the performance implication is an architectural inference, not a measured speed claim.

The implementation entry point is [`src/atom.rs`](https://github.com/symbolica-dev/symbolica/blob/main/src/atom.rs), including its examples and callback documentation.

## Computational algebra and polynomial systems

### 10. [gap-system/gap](https://github.com/gap-system/gap)

**Language / role:** GAP language and C/C++; computational discrete algebra, especially groups and their representations.

GAP broadens the category beyond elementary expression simplification. Study how mathematical knowledge about objects controls algorithm dispatch and how a large algebra system manages correctness defects across releases.

- **C2:** Operations bundle methods selected by argument types and filters. Attributes and properties participate in the same mechanism, with stored values providing specialized retrieval methods. Constructors have deliberately different filter-matching and ranking rules. [Method-selection documentation](https://github.com/gap-system/gap/blob/master/doc/ref/methsel.xml).
- **C1:** The release history distinguishes wrong mathematical answers from crashes: examples include invalid group series, leaked randomized stabilizer-chain options producing wrong orders, and incorrect finiteness classification.
- **C4:** Changes across 2019, 2022, and 2026 document library embedding/GC fixes, kernel-extension compatibility, package transitions, and mathematical corrections. [Detailed change history](https://github.com/gap-system/gap/blob/master/CHANGES.md).

### 11. [Singular/Singular](https://github.com/Singular/Singular)

**Language / role:** C/C++ and Singular's language; polynomial computation, commutative and noncommutative algebra, algebraic geometry, and singularity theory.

Study the polynomial kernel beneath higher-level Gröbner-basis computations. The inspected default branch is named `spielwiese`; links use that verified branch rather than assuming `main` or `master`.

- **C1:** The polynomial interface documents divisibility over coefficient rings that may have zero divisors, coefficient ownership, destructive versus constant arguments, and specialized preconditions for reconstruction operations. Ordinary field arithmetic assumptions cannot simply be carried into every supported ring.
- **C2:** Operations accept explicit ring information and build on separate coefficient, monomial, ordering, and polynomial facilities. The header explicitly identifies routines independent of the ambient `currRing`, a useful design boundary within a system with historical global context.

Start at [`libpolys/polys/monomials/p_polys.h`](https://github.com/Singular/Singular/blob/spielwiese/libpolys/polys/monomials/p_polys.h). Its contracts make ownership and algebraic assumptions visible before following the implementations.

### 12. [Macaulay2/M2](https://github.com/Macaulay2/M2)

**Language / role:** Macaulay2 language, C++, and implementation-language infrastructure; commutative algebra and algebraic geometry. Relevant subsystem: the native algebra engine under `M2/Macaulay2/e`.

Study how a research-oriented language exposes rings, graded modules, matrices, resolutions, and Gröbner computations through a common engine. The monorepo and its contributed packages count once.

- **C1:** The ring abstraction records whether field status is declared, unknown, or disproved by finding a nonzero nonunit; it retains the offending element. This is a concrete example of managing mathematical assumptions that later computation can invalidate.
- **C2:** The common interface accommodates quotient rings, fraction rings, graded rings, Weyl algebras, and skew-commutative multiplication. [Ring interface](https://github.com/Macaulay2/M2/blob/stable/M2/Macaulay2/e/rings/ring.hpp).

The [engine directory](https://github.com/Macaulay2/M2/tree/stable/M2/Macaulay2/e) is the second entry point, separating rings, monomials, computations, interfaces, and unit tests. Its older engine notes contain work-in-progress plans; those plans are not treated as proof that every proposed refactoring was completed.

### 13. [cocoa-official/CoCoALib](https://github.com/cocoa-official/CoCoALib)

**Language / role:** C++; commutative-algebra library and the mathematical kernel of the included CoCoA-5 interactive system.

CoCoALib is a less prominent but substantial example of representing mathematical domains explicitly in a C++ API. It is useful for studying the difference between a scalar's apparent value and the ring that gives it meaning.

- **C1:** Constructing a ring element from a rational may fail if the denominator becomes a zero divisor. The documented behavior throws a specific division-by-zero error rather than silently importing field semantics into an unsuitable ring.
- **C2:** `RingElem` stores both a ring and a value. Ring objects, canonical homomorphisms, and element operations let the same user-facing abstraction serve many coefficient domains; even zero elements from different rings remain distinct objects.

The [RingElem documentation](https://github.com/cocoa-official/CoCoALib/blob/main/doc/txt/RingElem.txt) explains construction, coercion, arithmetic, and implementation considerations in detail. The repository contains the actual library and interactive system, not simply bindings to another CAS.

### 14. [algebraic-solving/msolve](https://github.com/algebraic-solving/msolve)

**Language / role:** C; Gröbner bases and multivariate polynomial-system solving over rational and prime-field coefficients.

Study the pipeline between sparse polynomial representations, symbolic preprocessing, matrix reduction, and modular computation. Its narrow mathematical purpose permits more specialized implementation choices than a general expression engine.

- **C1:** The F4 implementation checks a reused trace against both the number and leading monomials of newly produced elements, identifying bad-prime cases instead of assuming every modular run behaves identically.
- **C3:** Exponent hashes are mapped to matrix columns, rows are ordered for reduction, and resulting sparse rows are converted back to basis elements. Separate finite-field coefficient-width and rational linear-algebra implementations expose the performance architecture. [F4 implementation](https://github.com/algebraic-solving/msolve/blob/master/src/neogb/f4.c) and [neogb source directory](https://github.com/algebraic-solving/msolve/tree/master/src/neogb).

**Input limitation:** the repository documentation requires each monomial to occur only once within an input polynomial and says repeated occurrences give undefined parser behavior. This is an explicit integration constraint, not a claim of robust handling of arbitrary algebraic text.

### 15. [PoslavskySV/rings](https://github.com/PoslavskySV/rings)

**Language / role:** Java with a Scala DSL; polynomial rings, GCDs, factorization, ideals, and Gröbner bases on the JVM.

Study how generic algebra and specialized machine arithmetic can coexist without making every application choose between separate libraries. The Java/Scala API distinction also makes mutation semantics visible.

- **C1:** Polynomial objects are generally mutable, while ring-level arithmetic and Scala operators provide nonmutating behavior. The guide gives examples showing when an apparently ordinary addition changes an operand.
- **C2:** A typed hierarchy of coefficient rings, polynomials, field extensions, and fractions supports nested algebraic constructions and generic algorithms.
- **C3:** Specialized machine-coefficient polynomial types coexist with generic coefficient types. Multivariate representations use ordered sparse maps from degree vectors to monomials, and shared generic base classes let algorithms cover both representations.

The extensive [implementation-aware user guide](https://github.com/PoslavskySV/rings/blob/develop/doc/guide.rst) covers these contracts. Project benchmark superlatives are not adopted here, and this entry does not assert a current maintenance cadence.

### 16. [kredel/java-algebra-system](https://github.com/kredel/java-algebra-system)

**Language / role:** Java; JAS, a generic algebra library with sequential and parallel polynomial algorithms.

JAS offers unusually concrete material on concurrency inside exact algebra. The parallel Gröbner-basis engine is a better starting point than the broad feature catalog.

- **C1:** The inspected implementation rejects coefficient domains that are not fields for this algorithm, coordinates workers with a termination protocol, synchronizes modifications to the shared basis, and checks interruption before final minimization. Mathematical completion and worker termination must agree.
- **C2:** The engine is parameterized by coefficient elements and accepts replaceable reduction engines, pair-selection strategies, and executor services.
- **C3:** Reduction workers run in a thread pool, with a separate parallel phase for obtaining a minimal basis. This makes parallel scheduling and algebraic strategy independently inspectable.

The primary entry point is [`GroebnerBaseParallel.java`](https://github.com/kredel/java-algebra-system/blob/master/src/edu/jas/gb/GroebnerBaseParallel.java), including its worker classes and constructor contracts.

### 17. [oscar-system/Oscar.jl](https://github.com/oscar-system/Oscar.jl)

**Language / role:** Julia; integrated CAS for algebra, geometry, and number theory, combining and extending several cornerstone systems.

OSCAR is retained for its own mathematical interfaces and integration architecture, not counted as another copy of GAP or Singular. Study how a high-level language can unify several engines without losing domain information.

- **C1:** Its design document requires mathematical context to be explicit. For example, being a unit in a number field differs from being a unit in its ring of integers; type and parent information must distinguish these questions.
- **C2:** Shared infrastructure covers matrices, polynomials, groups, number fields, and geometric objects, with consistent conventions above lower-level systems.
- **C3:** The design explains why putting every modulus in a Julia type would trigger excessive recompilation in modular algorithms. Parent objects preserve runtime domain information, including for empty matrices where entries cannot carry it.

The [design-decisions document](https://github.com/oscar-system/Oscar.jl/blob/master/docs/src/DeveloperDocumentation/design_decisions.md) is a particularly useful architectural entry point, including explicit priorities among correctness, interoperability, readability, and speed.

### 18. [Nemocas/AbstractAlgebra.jl](https://github.com/Nemocas/AbstractAlgebra.jl)

**Language / role:** Julia; generic computational algebra implementations and interfaces, without C dependencies.

This is a substantial implementation layer used by Nemo and related systems, not a generated wrapper. Study the contracts needed to make generic algorithms valid across rings with different capabilities and identity rules.

- **C1:** Parent-object caches can make separately constructed rings compatible, but the documentation explains why identical defining polynomials do not always justify identifying number fields with distinct embeddings. The interface also requires a way to bypass caching.
- **C2:** Standardized parent and element types, required ring operations, and optional capabilities allow generic polynomial, matrix, fraction, residue-ring, and series algorithms to serve independently implemented domains.
- **C3:** Optional operations permit more efficient algorithm choices while preserving the generic fallback interface.

The [ring interface specification](https://github.com/Nemocas/AbstractAlgebra.jl/blob/master/docs/src/ring_interface.md) is a detailed entry point for representation, cache, dispatch, and extension contracts.

## Symbolic representations and numerical code generation in Julia

### 19. [JuliaSymbolics/Symbolics.jl](https://github.com/JuliaSymbolics/Symbolics.jl)

**Language / role:** Julia; CAS and symbolic-to-numerical compilation layer.

Study how symbolic expressions become reusable numerical programs. This repository adds differentiation, equation solving, arrays, and function construction above the separate SymbolicUtils representation and rewriting layer.

- **C2:** `build_function` accepts symbolic operations or arrays of operations and exposes a target abstraction for Julia, C, Stan, and MATLAB output. The documentation carefully distinguishes returned source from an actual callable function.
- **C3:** Generated Julia functions can specialize on static arrays and sparse matrices and support automatic parallelization. The important engineering question is how the symbolic IR supplies structure that numerical solvers can exploit, not a universal claim that symbolic generation is faster.

The [function-building and compilation guide](https://github.com/JuliaSymbolics/Symbolics.jl/blob/master/docs/src/manual/build_function.md) is the verified architectural entry point. Its explicit target limitations are useful when deciding whether a backend is a code printer or a complete compilation path.

### 20. [JuliaSymbolics/SymbolicUtils.jl](https://github.com/JuliaSymbolics/SymbolicUtils.jl)

**Language / role:** Julia; symbolic representations, rewriting, simplification, and extension infrastructure.

Study an evolving symbolic intermediate representation whose invariants differ from Julia's ordinary object mutability and type conventions. It warrants a separate entry because it is a reusable foundation for custom symbolic systems.

- **C1:** The representation is semantically immutable even when Julia reports a mutable implementation type. Its documented variants distinguish ordinary simplification, safer division without cancellation, and uninterpreted expression trees; operands must use a consistent algebra tag.
- **C2:** Symbolic types and array shapes are represented explicitly, with known-shape, known-rank, and unknown-rank cases governing how much validation is possible.
- **C3:** The v4 design moves represented mathematical types from Julia type parameters into fields to improve type stability; recursive-operation caching is exposed separately.

Read the [variant and representation design](https://github.com/JuliaSymbolics/SymbolicUtils.jl/blob/master/docs/src/manual/variants.md) and [caching guide](https://github.com/JuliaSymbolics/SymbolicUtils.jl/blob/master/docs/src/manual/caching.md). These describe the inspected branch, not every installed older release.

## Large expressions and tensor algebra

### 21. [form-dev/form](https://github.com/form-dev/form)

**Language / role:** C/C++ with the FORM language; symbolic manipulation particularly associated with large high-energy-physics computations. The older `vermaseren/form` URL redirects to this canonical repository.

FORM is distinctive because expression size need not be bounded by available RAM. Study its compilation and term-processing pipeline rather than expecting the architecture of an in-memory expression-tree library.

- **C3:** The developer walkthrough explains encoded expressions, delayed subexpression insertion, and a scratch-buffer system spanning memory buffers and files. Delaying expansion can allow cancellations before large intermediate expressions are materialized.
- **C2:** Preprocessing, algebra compilation, generation, and storage utilities form separable stages; callers can write to the scratch system without deciding where each expression is physically stored. [Annotated execution walkthrough](https://github.com/form-dev/form/blob/master/doc/devref/formrun.tex).
- **C1:** Dummy-index renaming interacts with powers and hidden bracket contents. The developer notes discuss specific cases where renaming would change meaning, exposing correctness/performance tradeoffs and known limitations. [In-depth developer notes](https://github.com/form-dev/form/blob/master/doc/devref/indepth.tex).

### 22. [kpeeters/cadabra2](https://github.com/kpeeters/cadabra2)

**Language / role:** C++ and Python; tensor and field-theory CAS, including index symmetries, fermions, and noncommuting objects. This is the 2.x implementation, which supersedes the separate 1.x repository.

Study the boundary between a generic expression tree and algorithms that need tensor-specific property information. The common algorithm base class makes extension obligations unusually explicit.

- **C1:** An algorithm may not invalidate the iterator supplied to its application method. If a node disappears, the documented protocol marks it with a zero multiplier so outer traversal can clean up; replacement requires updating the iterator. Index classification adds mathematical correctness obligations to these structural ones.
- **C2:** Algorithms implement common applicability and application methods, while the base machinery supplies traversal, repeated application, property-aware helpers, and progress reporting.

The [Algorithm interface](https://github.com/kpeeters/cadabra2/blob/master/core/Algorithm.hh) is the principal implementation entry point. It explains how tensor algorithms compose without each reimplementing safe tree traversal.

## Embedded, functional, and browser-oriented systems

### 23. [asc-community/AngouriMath](https://github.com/asc-community/AngouriMath)

**Language / role:** C# with F# and other interfaces; embeddable symbolic algebra library.

Study the gap between plausible algebraic rewrites and valid transformations over complex domains. The inspected documentation is candid about defects and incomplete extensibility; those limitations are part of its value as engineering material.

- **C1:** The simplification contract distinguishes expression domains, codomains, ambient interpretation, and attached conditions. It explains branch-cut failures and the need to preserve a condition when reducing `x/x`. Passing sampled regression checks alone is explicitly insufficient. [Simplification contract](https://github.com/asc-community/AngouriMath/blob/master/Sources/AngouriMath/Docs/Contributing/SimplificationContract.md).
- **C2:** The `Entity` node hierarchy connects child traversal, simplification, printing, domain conditions, and inversion. The node-contract audit documents which members a node must implement and why external assemblies cannot simply introduce arbitrary new node kinds. [Node contract](https://github.com/asc-community/AngouriMath/blob/master/Sources/AngouriMath/Docs/Contributing/NodeContract.md).

This supports studying a reusable internal abstraction, not claiming that its public extension surface is complete or all rewrite rules are unconditionally sound.

### 24. [mathnet/mathnet-symbolics](https://github.com/mathnet/mathnet-symbolics)

**Language / role:** F#; compact symbolic algebra library for .NET, explicitly narrower than a full CAS.

Study a functional representation with visible exact, approximate, infinite, and undefined cases. Its smaller scope makes it practical to trace a transformation across the representation and arithmetic layers.

- **C1:** The expression discriminated union distinguishes exact rationals, approximations, signed and complex infinity, and undefined results. Pattern matching and value operations make handling these cases explicit.
- **C2:** Shared expressions support algebraic, polynomial, rational, trigonometric, calculus, evaluation, and compilation modules. [Expression implementation](https://github.com/mathnet/mathnet-symbolics/blob/master/src/Symbolics/Expression.fs).
- **C4:** Release notes from 2016–2023 record infinity and complex-power corrections, separation of unary and n-ary functions, parsing changes, API breaks, and .NET target upgrades. [Release notes](https://github.com/mathnet/mathnet-symbolics/blob/master/RELEASENOTES.md).

**Maintenance qualification:** the inspected notes end with a December 2023 effort to revive the project. This report does not imply a regular current release cadence.

### 25. [davidedc/Algebrite](https://github.com/davidedc/Algebrite)

**Language / role:** TypeScript/JavaScript; embeddable and browser-capable CAS derived from EigenMath, with its own translated implementation and tests.

Study a comparatively compact symbolic runtime where Lisp-style expression construction remains visible in TypeScript. It is a substantive adaptation, not an interface that forwards calculations to an external CAS.

- **C2:** A common atom hierarchy includes cons cells, exact rational numbers, floating-point values, symbols, and tensors. The runtime explicitly diagrams how arithmetic expressions are represented. [Runtime definitions](https://github.com/davidedc/Algebrite/blob/master/runtime/defs.ts).
- **C1:** Addition must handle second-order simplification: combining two terms can change a radical coefficient and make another combination possible. The implementation orders and combines terms repeatedly, bounds the repetition, handles tensor compatibility, and checks cancellation requests. [Symbolic addition implementation](https://github.com/davidedc/Algebrite/blob/master/sources/add.ts).

Shared mutable runtime settings and module-level working state are also visible in these entry points; selection does not imply isolated concurrent evaluation contexts.

### 26. [mentat-collective/emmy](https://github.com/mentat-collective/emmy)

**Language / role:** Clojure and ClojureScript; CAS for mathematics and mechanics, implementing the scmutils tradition in a different language/runtime ecosystem.

Study how ordinary higher-order programs can operate on numerical or symbolic objects through the same extensible arithmetic. Its symbolic simplification and mechanics facilities establish category fit beyond automatic differentiation alone.

- **C1:** The dual-number implementation explains perturbation confusion in nested differentiation and uses distinct tags to preserve the identity of derivative levels. This is a concrete semantic failure mode that naïve dual arithmetic misses. [Dual-number implementation and derivation](https://github.com/mentat-collective/emmy/blob/main/src/emmy/dual.cljc).
- **C2:** Generic unary and binary operations extend across mathematical types, while higher-arity operations reduce through those primitives. Identity predicates distinguish scalar one from a matrix identity whose meaning depends on shape. [Generic arithmetic implementation](https://github.com/mentat-collective/emmy/blob/main/src/emmy/generic.cljc).

The source combines explanatory derivations with implementation, making it useful for following the reasoning behind the abstractions.

## Coverage, search process, and limitations

Discovery used more than six distinct formulations, including general CAS architecture; C++ polynomial and Gröbner libraries; Julia rewriting; Java/Rust/JavaScript symbolic libraries; Lisp CAS lineage and official mirrors; tensor and field-theory manipulation; .NET/F# symbolic mathematics; multivariate system solving; and Clojure/Haskell functional algebra. Follow-up searches targeted canonical repositories, coercion models, type systems, exact arithmetic, and official source-hosting information. Later searches increasingly returned already covered systems, thin integrations, or newer candidates whose implementation depth was not verified to the same level. Emmy added a distinct functional-programming community late in the search. The list was extended slightly beyond 25 to preserve that coverage.

Primary verification used live repository pages, project documentation, and individual raw source files. A shared GitHub API rate limit prevented metadata retrieval through that API; repository pages and HTTP redirects supplied canonical-URL verification instead. Failed URLs and unread search snippets were not used as implementation evidence. No candidate repository was cloned, installed, or executed, and no independent performance measurements were made.

Important selection boundaries:

- **Hosting:** GiNaC's [official download page](https://www.ginac.de/Download.html) points to Codeberg. Maxima's [official installation/source page](https://maxima.sourceforge.io/download.html) points readers to its own distribution infrastructure. Neither was retained because this search did not establish a substantive official GitHub mirror meeting the requested verification bar. This is a hosting/evidence exclusion, not a judgment of their engineering quality. REDUCE's officially linked mirror was retained and labeled.
- **Deduplication:** No separate entries were made for language bindings, notebook interfaces, old Cadabra releases, FORM's redirected owner path, or FLINT's absorbed component repositories. Sage, OSCAR, AbstractAlgebra, and their underlying engines are retained only for distinct implementation responsibilities identified in their entries.
- **Scope:** General compiler equality-saturation frameworks, symbolic regression, optimization modeling packages, and numerical-only libraries were excluded unless the inspected project itself supplied substantial computer-algebra functionality. Other discovered CAS projects, including Nerdamer and newer Rust/Haskell systems, remain outside this representative selection; their omission is not a claim that they fail the criteria.
- **Evidence limits:** C4 is assigned only where multi-year maintenance material was actually inspected. Repository availability does not establish active maintenance. The report does not exhaustively audit tests, prove algorithms, validate advertised benchmark rankings, or guarantee uniform code quality. Symbolica's restrictive source-available licensing and the documented correctness/input limitations above are material to choosing what to study or reuse.
