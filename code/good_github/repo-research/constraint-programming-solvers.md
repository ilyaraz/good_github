# Constraint programming solvers

Research date: **2026-10-09**.

This selection covers 20 GitHub repositories containing substantial solver implementations: finite-domain propagation, CP/SAT hybrids, proof logging, weighted constraints, real-interval constraints, constraint logic programming, and constraint-based local search. It includes reusable libraries and research systems with distinctive internals. Modeling-only packages, generated bindings, solver catalogs, and single-problem demonstrations are outside the scope. OR-Tools and SWI-Prolog are counted once each, with the relevant subsystem identified below. Local-search entries are heuristic systems and should not be read as promises of infeasibility or optimality proofs.

Criteria legend:

- **C1 — Difficult correctness:** preserving propagation, backtracking, numerical, explanation, concurrency, or failure-handling invariants.
- **C2 — Reusable abstractions:** substantial interfaces and representations supporting different constraints, searches, and applications.
- **C3 — Performance with structure:** concrete mechanisms to reduce search, propagation work, allocations, or other real costs within an understandable architecture.
- **C4 — Sustained evolution:** multi-year development supported by compatibility work, testing, or deliberate complexity management. Age and recent pushes alone do not establish this criterion.

The criteria assessments are engineering judgments grounded in the linked material, not claims that every component is exemplary. Sources were read; candidate code was not built or executed. No comparative benchmark claims are made.

## Finite-domain engines and extensible propagation

### 1. [Gecode/gecode](https://github.com/Gecode/gecode)

**Language/role:** C++; general-purpose constraint-programming toolkit.

Gecode is particularly useful for studying the contract between a solver kernel and user-defined propagators. Its implementation manual distinguishes variables from the views through which propagators inspect and narrow domains, then develops event subscriptions, subsumption, cloning, and disposal. The result is a concrete account of what a reusable propagation component owes its host engine.

- **C1:** Propagators must preserve solutions, detect violations on complete assignments, and meet contraction and kernel lifecycle obligations. The manual explicitly distinguishes these requirements rather than treating successful example solutions as sufficient correctness evidence.
- **C2:** Views and propagator patterns let implementations be reused across variable transformations and constraints.
- **C3:** Propagation conditions suppress irrelevant executions; subsumption eliminates work once a constraint is entailed. These mechanisms are explained alongside their correctness obligations in the [propagator implementation chapter](https://www.gecode.dev/doc/latest/modeling/propagators/started/).

**Entry point:** [Implementing propagators, including obligations and permitted exceptions](https://www.gecode.dev/doc/latest/modeling/propagators/started/).

### 2. [chocoteam/choco-solver](https://github.com/chocoteam/choco-solver)

**Language/role:** Java; embeddable CP solver with multiple variable families and search strategies.

Study how a broad modeling API is backed by explicit propagation and entailment interfaces. The developer guide contrasts complete recomputation with incremental filtering and explains when a propagator can become passive and how backtracking reactivates it.

- **C1:** Three-valued entailment supports reification, while event masks and idempotency rules determine whether incremental propagation is sound. The [propagator guide](https://choco-solver.org/docs/advanced-usages/propagator/) makes those obligations concrete.
- **C2:** Custom `Constraint`/`Propagator` implementations share the same engine as built-in constraints; priorities and variable-event subscriptions are reusable extension mechanisms.
- **C4:** The [changelog](https://github.com/chocoteam/choco-solver/blob/master/CHANGES.md) records releases across 2022–2026, API deprecations, numerical and explanation fixes, and the Java 17/TestNG/build migration in version 6.0.0. This is evidence of managing compatibility and testing through substantial change.

**Entry points:** [Propagator extension guide](https://choco-solver.org/docs/advanced-usages/propagator/); [release and migration history](https://github.com/chocoteam/choco-solver/blob/master/CHANGES.md). The older guide is best read alongside the current changelog.

### 3. [radsz/jacop](https://github.com/radsz/jacop)

**Language/role:** Java; finite-domain and set-constraint solver with configurable search.

JaCoP's `Store` is an informative, centralized account of solver bookkeeping. It brings together propagation queues, search levels, mutable state, timestamps, and notifications for constraints whose internal structures need restoration.

- **C1:** The store distinguishes notifications before and after a search level is removed, records changed Boolean variables, and prevents consistency evaluation from proceeding normally after an unresolved failure. It also documents that auxiliary variables introduced by decomposition must be grounded for a valid solution.
- **C2:** Constraints, stateful objects, level-removal listeners, and interchangeable backtracking management form explicit extension boundaries.
- **C3:** Deduplicated priority queues, compact histories for Boolean changes, and timestamped state avoid repeatedly copying or reevaluating everything. These are directly visible in [Store.java](https://github.com/radsz/jacop/blob/develop/src/main/java/org/jacop/core/Store.java).

**Entry points:** [Store implementation](https://github.com/radsz/jacop/blob/develop/src/main/java/org/jacop/core/Store.java); [changelog, including MiniZinc compatibility decisions](https://github.com/radsz/jacop/blob/develop/CHANGELOG).

### 4. [minion/minion](https://github.com/minion/minion)

**Language/role:** C++ solver; Rust testing and library-interface infrastructure.

Minion offers both specialized propagation code and unusually concrete descriptions of how that code is challenged. Its short-table implementation is a good route into reversible sparse structures and support maintenance; its test documentation explains how independent formulations expose solver mistakes.

- **C1:** The test harness compares constraint solutions with explicit table encodings, compares equivalent propagators, and checks agreement across search options and parallel modes. This is stronger evidence than a collection of puzzle examples. Coverage limitations are also documented in [TESTING.md](https://github.com/minion/minion/blob/main/TESTING.md).
- **C2:** The templated STR implementation shares machinery between ordinary and short tuples while adapting variable-array types.
- **C3:** A reversible active-tuple boundary, deletion-only array sets, and domain-change triggers support incremental table filtering without rebuilding all state. See [constraint_shortstr2.h](https://github.com/minion/minion/blob/main/minion/constraints/constraint_shortstr2.h).

**Entry points:** [ShortSTR2/STR2 implementation](https://github.com/minion/minion/blob/main/minion/constraints/constraint_shortstr2.h); [testing architecture](https://github.com/minion/minion/blob/main/TESTING.md).

### 5. [xcsp3team/ACE](https://github.com/xcsp3team/ACE)

**Language/role:** Java; XCSP3-oriented CSP and optimization solver.

ACE is a useful implementation study for propagation scheduling, nogood reasoning, and the interaction between filtering statistics and search heuristics. Its repository identifies support for ordinary, starred, and hybrid tables alongside global constraints.

- **C1:** The propagation layer coordinates watched nogoods, domain wipeouts, entailed constraints, and postponed work. Inconsistent propagation clears pending work rather than treating a partially processed queue as a fixpoint.
- **C2:** A common `Propagation` base supports alternative consistency algorithms and solver-selected implementations.
- **C3:** Variable/constraint timestamps avoid useless filtering calls, while postponed constraints and sparse sets separate expensive work from the main queue. These mechanisms are exposed in [Propagation.java](https://github.com/xcsp3team/ACE/blob/main/src/main/java/propagation/Propagation.java).

**Entry point:** [Propagation implementation](https://github.com/xcsp3team/ACE/blob/main/src/main/java/propagation/Propagation.java). **Limitation:** the repository README explicitly says unit tests are no longer included in the main repository; no test-suite completeness claim is made here.

### 6. [concrete-cp/concrete](https://github.com/concrete-cp/concrete)

**Language/role:** Scala; CSP solver using persistent and semi-persistent state.

Concrete provides a valuable comparison with mutable trailing engines. Its README describes persistent domain structures combined with sparse sets, residues, and watched literals where persistence would be unnecessary or costly. `ProblemState` makes successful states and contradictions separate outcomes.

- **C1:** Domain updates assert that new domains are nonempty subsets of the previous domains; empty results become contradictions. The outcome API prevents ordinary domain operations from silently continuing with a failed state.
- **C2:** `Outcome`, `ProblemState`, typed constraint-state access, and composable state transformations provide reusable interfaces for different propagators.
- **C3:** Persistent maps share state, unchanged updates return the existing state, and the solver chooses domain representations according to density. See the [state implementation](https://github.com/concrete-cp/concrete/blob/master/src/main/scala/concrete/ProblemState.scala) and repository architecture discussion.

**Entry point:** [ProblemState.scala](https://github.com/concrete-cp/concrete/blob/master/src/main/scala/concrete/ProblemState.scala). **Limitation:** the README warns about 32-bit arithmetic overflow and large-domain memory use; this is a design study, not an assertion that arbitrary integer inputs are safe.

### 7. [aia-uclouvain/maxicp](https://github.com/aia-uclouvain/maxicp)

**Language/role:** Java; CP library emphasizing scheduling, routing, and symbolic modeling.

MaxiCP explicitly extends MiniCP, but is retained as a substantive separate implementation: optional interval variables, sequence variables, delta propagation, and symbolic models materially expand its scope beyond the teaching solver. Study the boundary between immutable model construction and mutable solving.

- **C1:** Backtracking state is isolated in a state-management package; concrete variables and the propagation queue live in the engine layer.
- **C2:** The symbolic API represents a model as immutable linked nodes, while a bridge concretizes those nodes into engine objects. Integer, interval, and sequence variables support distinct problem families.
- **C3:** The architecture supports model transformations, large-neighborhood search expressed as model branches, and independent parallel search. The [architecture guide](https://maxicp.org/learning_maxicp/architecture.html) identifies the responsible packages and search classes.

**Entry point:** [Architecture and the two modeling layers](https://maxicp.org/learning_maxicp/architecture.html).

## Clause learning, hybrid solving, and proof logging

### 8. [google/or-tools](https://github.com/google/or-tools)

**Language/role:** C++ with language bindings; the relevant subsystem is **CP-SAT under `ortools/sat`**, with a separate traditional CP engine under `ortools/constraint_solver` in the same repository.

For this category, begin with CP-SAT's integer encoding layer. It explains how finite-domain facts become Boolean literals that the SAT solver can decide on and learn about, rather than requiring readers to start with the entire optimization suite.

- **C1:** Integer literals must be canonicalized across domain holes, and equality/bound encodings must agree. The source documents restrictions on when full encodings can be created and the validity of returned references.
- **C2:** `IntegerEncoder`, integer trails, and the shared model interface connect reusable integer propagators to the SAT engine.
- **C3:** Lazy versus full encodings, reuse of literals for extreme values and negated variables, and batched implication construction explicitly trade memory and setup work against propagation needs. See [integer.h](https://github.com/google/or-tools/blob/stable/ortools/sat/integer.h).

**Entry points:** [Integer encoding and propagation interfaces](https://github.com/google/or-tools/blob/stable/ortools/sat/integer.h); [CP-SAT documentation index](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/README.md).

### 9. [chuffed/chuffed](https://github.com/chuffed/chuffed)

**Language/role:** C++; tightly integrated lazy-clause-generation CP solver.

Chuffed is useful for understanding a compact finite-domain engine whose propagation steps produce SAT explanations. Its repository describes native channeling between integer domains and Boolean encodings, with eager encoding for small domains and lazy creation for larger ones.

- **C1:** The [propagator interface](https://github.com/chuffed/chuffed/blob/develop/chuffed/core/propagator.h) explicitly calls out complete-assignment checking, safe subsumption, trailing persistent state, clearing temporary state, overflow, and idempotency.
- **C2:** Propagators implement a shared lifecycle of event wakeup, propagation, explanation, and cleanup; globals and FlatZinc models use the same machinery.
- **C3:** Queue deduplication and selective wakeups reduce repeated filtering, while learned nogoods and conflict-directed search reduce redundant exploration. The [repository's architectural description](https://github.com/chuffed/chuffed#description) explains the CP/SAT connection without requiring an unsupported speed claim.

**Entry point:** [Propagator lifecycle and explanation interface](https://github.com/chuffed/chuffed/blob/develop/chuffed/core/propagator.h).

### 10. [ConSol-Lab/Pumpkin](https://github.com/ConSol-Lab/Pumpkin)

**Language/role:** Rust; lazy-clause-generation solver and proof-logging research platform.

Pumpkin is especially interesting for the separation between a simple reference propagator and its optimized incremental implementation. Its public API documents when the solver invokes each and what information is available when an explanation is reconstructed later.

- **C1:** With debug checks enabled, `propagate_from_scratch` double-checks reported propagations and failure reasons. Lazy explanations must account for the state at the original trail position, while backtrack notifications have explicitly documented delivery limits.
- **C2:** The propagator trait provides independent hooks for notification, propagation, synchronization, priorities, inconsistency detection, and lazy explanations.
- **C3:** Cheap event handling is separated from expensive propagation; incremental state and deferred explanations can reduce work while retaining a simpler checking implementation. These contracts are in the [Propagator API](https://docs.rs/pumpkin-solver/latest/pumpkin_solver/core/propagation/trait.Propagator.html).

**Entry point:** [Propagator contract and checking behavior](https://docs.rs/pumpkin-solver/latest/pumpkin_solver/core/propagation/trait.Propagator.html). The repository also identifies its proof-format and proof-processing components; this report does not independently validate its certificates.

### 11. [huub-solver/huub](https://github.com/huub-solver/huub)

**Language/role:** Rust; extensible CP/SAT solver framework.

Huub separates modeling, lowering, reasoning contexts, and solver execution. It is a good study of how types can expose different operations during construction, propagation, explanation, and branching instead of handing every extension unrestricted access to solver state.

- **C1:** Propagation contexts define conflict and reason-sink types; deferred reasons are restricted to the propagator context that can later explain them. Trailed handles support state restoration.
- **C2:** Phase-specific action traits, custom propagators and branchers, variable views, and replaceable SAT backends support reuse across applications and experiments.
- **C3:** Deferred reason construction avoids building explanations before they are needed, while the model/lowering boundary provides a place for simplification. See [actions.rs](https://github.com/huub-solver/huub/blob/develop/crates/huub/src/actions.rs) and the [library architecture/API](https://docs.rs/huub/latest/huub/).

**Entry points:** [Action and reasoning-context interfaces](https://github.com/huub-solver/huub/blob/develop/crates/huub/src/actions.rs); [model-to-solver API](https://docs.rs/huub/latest/huub/). Published API documentation and the development branch can represent different revisions.

### 12. [ciaranm/glasgow-constraint-solver](https://github.com/ciaranm/glasgow-constraint-solver)

**Language/role:** C++; finite-domain solver designed around checkable pseudo-Boolean proof logs.

Glasgow makes the relationship between a high-level constraint, its low-level encoding, and its propagation proof particularly explicit. It is useful for studying assurance architecture, including the distinction between checking a proof and checking that the encoded model means the intended thing.

- **C1:** Constraints have separate preparation, proof-model definition, and propagator-installation phases. The proof checker validates the emitted pseudo-Boolean reasoning; correctness of the high-level encoding remains a separate obligation, explicitly acknowledged in the README.
- **C2:** Callable propagators, common inference/justification APIs, and shared encoding helpers let different global constraints use the proof infrastructure.
- **C3:** Consistency choices expose their cost model: the developer guide distinguishes a genuine GAC algorithm from obtaining the same consistency by table enumeration. See [Implementing a constraint](https://github.com/ciaranm/glasgow-constraint-solver/blob/main/dev_docs/constraints.md).

**Entry point:** [Constraint, encoding, propagation, and testing architecture](https://github.com/ciaranm/glasgow-constraint-solver/blob/main/dev_docs/constraints.md). **Status:** the README calls the solver a work in progress with no stable API or design.

## Weighted, continuous, and logic-programming constraints

### 13. [toulbar2/toulbar2](https://github.com/toulbar2/toulbar2)

**Language/role:** C++; exact optimization of weighted constraint networks and discrete cost-function networks.

toulbar2 broadens the category beyond hard satisfaction: local functions contribute costs, and forbidden assignments are represented relative to a bound. Its `WCSP` class shows how lower bounds, upper bounds, local consistency, and variable elimination fit together.

- **C1:** Bound increases can immediately raise contradictions; alternative search nodes must enforce the current upper bound. Propagation distinguishes backtrackable bounds and separator state from queues that must be reset after failure.
- **C2:** `WeightedCSP`/`WCSP`, variable abstractions, and ordinary/global cost functions provide reusable modeling and reasoning machinery.
- **C3:** Separate queues for node, arc, directed, and existential consistency, plus bounded-degree variable elimination, organize several ways to strengthen bounds without treating all propagation as one undifferentiated pass. The [WCSP header](https://github.com/toulbar2/toulbar2/blob/master/src/core/tb2wcsp.hpp) documents these responsibilities and exposes fixpoint verification.

**Entry point:** [Weighted-CSP state, bounds, and local-reasoning interface](https://github.com/toulbar2/toulbar2/blob/master/src/core/tb2wcsp.hpp).

### 14. [ibex-team/ibex-lib](https://github.com/ibex-team/ibex-lib)

**Language/role:** C++; interval constraint processing and global optimization over real numbers.

IBEX is the main continuous-domain counterpoint in this selection. Rather than centering every algorithm on a global mutable constraint store, it exposes contractors that narrow interval boxes and can themselves be combined into more powerful contractors.

- **C1:** Contractor semantics require contraction without losing solutions; the library's interval arithmetic accounts for rounding. The documentation also distinguishes stopping by a fixpoint ratio from having a bound on the distance to the mathematical fixpoint.
- **C2:** A small `Ctc::contract` interface supports composition, union, fixpoint, propagation, shaving, and constructive disjunction.
- **C3:** Input/output dependency bitsets drive an agenda that reschedules only affected contractors. The [contractor chapter](https://ibex-team.github.io/ibex-lib/contractor.html) explains both the abstraction and the dependency-based scheduling algorithm.

**Entry point:** [Contractor semantics, composition, and propagation](https://ibex-team.github.io/ibex-lib/contractor.html).

### 15. [mpelleau/AbSolute](https://github.com/mpelleau/AbSolute)

**Language/role:** OCaml; research solver using abstract domains from abstract interpretation.

AbSolute is retained for a distinct architecture, not for production maturity. The solver is parameterized by an abstract domain, enabling experiments with representations beyond the usual independent finite domains or interval boxes.

- **C1:** The library formalizes filtering as producing a subset that retains every satisfying point. Domain implementations must supply consistency, splitting, and precision operations, so their soundness and termination-related behavior are explicit integration concerns.
- **C2:** The solver is an OCaml functor; domain registration and combination, constraint syntax, filtering order, and arithmetic modules are separated. See the [Libabsolute module overview](https://mpelleau.github.io/AbSolute/libabsolute/Libabsolute/index.html) and [domain signatures](https://mpelleau.github.io/AbSolute/libabsolute/Libabsolute/Signature/index.html).

**Entry points:** [Library architecture](https://mpelleau.github.io/AbSolute/libabsolute/Libabsolute/index.html); [abstract-domain interface](https://mpelleau.github.io/AbSolute/libabsolute/Libabsolute/Signature/index.html). **Status:** the README explicitly describes incomplete testing; this is a research implementation, not an established reliability claim.

### 16. [SWI-Prolog/swipl-devel](https://github.com/SWI-Prolog/swipl-devel)

**Language/role:** Prolog solver inside a C/Prolog runtime repository; specifically **`library/clp/clpfd.pl`**.

The bundled CLP(FD) implementation shows how domain propagation integrates with unification and relational programming. Study attributed variables, propagation queues, reification, residual constraints, and the separation of a logical relation from the labeling strategy used to search it.

- **C1:** The manual explains monotonic mode, including the requirement to distinguish variables in arithmetic expressions so adding constraints cannot create new solutions. Domain narrowing and unification must remain consistent with these relational semantics.
- **C2:** Arithmetic, global constraints, reification, reflection, labeling, and custom propagators share the same library and host-language mechanisms.
- **C3:** Goal expansion substitutes cheaper ordinary arithmetic when instantiation permits it; the source also maintains separate fast/slow propagation queues. See the [CLP(FD) manual](https://www.swi-prolog.org/pldoc/man?section=clpfd) and [implementation](https://github.com/SWI-Prolog/swipl-devel/blob/master/library/clp/clpfd.pl).

**Entry points:** [CLP(FD) implementation](https://github.com/SWI-Prolog/swipl-devel/blob/master/library/clp/clpfd.pl); [semantics and extension guide](https://www.swi-prolog.org/pldoc/man?section=clpfd). **Historical qualification:** the manual says the original author's library development moved to SICStus. This entry concerns the substantive implementation still distributed in the official SWI-Prolog repository, not a claim that its original development continues there.

## Julia implementations and learned search

### 17. [Wikunia/ConstraintSolver.jl](https://github.com/Wikunia/ConstraintSolver.jl)

**Language/role:** Julia; native finite-domain solver integrated with JuMP/MathOptInterface.

Although the project has a teaching goal, it contains substantive solver machinery rather than just modeling examples. Its all-different implementation is a useful path into combining graph-based domain filtering with bounds passed to an optional LP model.

- **C1:** Matching and strongly connected component state support all-different filtering; numeric bounds must remain compatible with the distinctness condition and any LP-side auxiliary constraints.
- **C2:** The same implementation participates in the MathOptInterface constraint lifecycle and accepts models through JuMP. The repository also identifies table, linear, reified, and Boolean constraints.
- **C3:** The [all-different source](https://github.com/Wikunia/ConstraintSolver.jl/blob/master/src/constraints/all_different.jl) initializes reusable matching/SCC work arrays and derives distinct-value sum bounds for LP integration. This makes the tradeoff between stronger bounds and extra machinery directly inspectable.

**Entry point:** [All-different implementation and LP-bound integration](https://github.com/Wikunia/ConstraintSolver.jl/blob/master/src/constraints/all_different.jl). **Scope limit:** the documented solver supports bounded discrete variables; the JuMP interface does not imply arbitrary continuous/nonlinear support.

### 18. [corail-research/SeaPearl.jl](https://github.com/corail-research/SeaPearl.jl)

**Language/role:** Julia; CP research solver with reinforcement-learning value-selection heuristics.

SeaPearl makes solver state available to learning components while retaining ordinary CP search. Its research API separates variable selection, learned value selection, state representations, rewards, problem generators, and evaluation, making it useful for studying how learned heuristics connect to a solver.

- **C1:** Reversible `StateObject` values record previous contents in a trailer; restoration must undo changes in the proper order. The [trailer documentation](https://corail-research.github.io/SeaPearl.jl/dev/CP/trailer/) explicitly limits restoration to ancestors rather than arbitrary saved states.
- **C2:** The model and learning abstractions allow different problems, graph representations, and policies to reuse the same search machinery. The [internals guide](https://corail-research.github.io/SeaPearl.jl/dev/CP/internals/) documents model state, resource limits, statistics, and objective tightening.

**Entry points:** [Trailer and reversible-state contract](https://corail-research.github.io/SeaPearl.jl/dev/CP/trailer/); [model/search internals](https://corail-research.github.io/SeaPearl.jl/dev/CP/internals/). **Qualification:** these generated guides are dated August 2023; no claim about current dependency compatibility or learned-heuristic superiority is inferred from them.

## Constraint-based local search

### 19. [informarte/yuck](https://github.com/informarte/yuck)

**Language/role:** Scala; local-search constraint solver with a FlatZinc interface.

Yuck is useful for studying violation semantics and structured neighborhoods, rather than only search-tree pruning. Its all-different implementation supports exception values, computes a violation measure, and can construct a specialized neighborhood from a bipartite matching.

- **C1:** Violation counting must handle repeated and excepted values correctly. The annealing engine preserves the best proposal on interruption, reconstructs its state, and checks that its cost agrees with the recorded best cost.
- **C2:** Generic constraint/value/domain types, neighborhoods, objectives, and annealing schedules support many models, including soft constraints and hierarchical objectives.
- **C3:** Constraint-specific neighborhoods and value-frequency tracking exploit problem structure instead of repeatedly treating every move as a fresh whole-model evaluation. See [AllDifferent.scala](https://github.com/informarte/yuck/blob/master/src/main/yuck/constraints/AllDifferent.scala) and [SimulatedAnnealing.scala](https://github.com/informarte/yuck/blob/master/src/main/yuck/annealing/SimulatedAnnealing.scala).

**Entry points:** [All-different violation and neighborhood implementation](https://github.com/informarte/yuck/blob/master/src/main/yuck/constraints/AllDifferent.scala); [annealing lifecycle and interruption handling](https://github.com/informarte/yuck/blob/master/src/main/yuck/annealing/SimulatedAnnealing.scala).

### 20. [cetic/oscar-cbls](https://github.com/cetic/oscar-cbls)

**Language/role:** Scala; library for building constraint-based local-search solvers.

This is the CBLS project, not the unrelated OSCAR computer-algebra system. It represents dependencies between variables and incrementally maintained invariants, with neighborhoods layered over those computations. The propagation implementation explains how update order controls both correctness and evaluation cost.

- **C1:** Propagation elements are ordered from inputs through dependencies, and debug modes invoke `checkInternals` after updates. Partial propagation must include the dependencies of its selected target.
- **C2:** Variables, invariants, propagation elements, and neighborhoods are separate reusable abstractions; the repository includes integer, set, sequence, and routing facilities.
- **C3:** Precomputed layers and an aggregated heap organize a single update wave; target-specific dependency tracks permit partial propagation instead of recomputing the full graph. See [PropagationStructure.scala](https://github.com/cetic/oscar-cbls/blob/master/src/main/scala/oscar/cbls/core/propagation/PropagationStructure.scala).

**Entry point:** [Propagation ordering, partial evaluation, and checking](https://github.com/cetic/oscar-cbls/blob/master/src/main/scala/oscar/cbls/core/propagation/PropagationStructure.scala). **Qualification:** the README warns that its linked user manual is not yet updated for the substantial version-6 refactor, so this entry relies on the current source.

## Coverage and search notes

Discovery used more than six distinct live-search formulations, followed by repository, documentation, and source inspection. Search angles included:

- Established propagation engines: “constraint programming solver GitHub propagation Gecode Choco” and searches for Minion, JaCoP, and ACE.
- Rust and lazy clause generation: Pumpkin, Huub, replaceable SAT backends, and propagator traits.
- Proof-producing CP: Glasgow, explanations, and proof logging.
- JVM and functional state designs: Scala/Concrete, OscaR, and MaxiCP architecture.
- Weighted and real-valued constraints: toulbar2, IBEX, and abstract-domain/OCaml solvers.
- Julia and learned search: ConstraintSolver.jl and SeaPearl.
- Local search and language breadth: Yuck, CBLS, and additional Go, Python, and OCaml searches.

Later language-focused searches increasingly returned bindings, modeling packages, elementary AC-3/backtracking implementations, or already represented solver families. Those results did not justify padding the list. Pure SAT/SMT systems and general LP/MIP solvers were excluded unless a retained repository contained a direct CP implementation. MiniZinc, CPMpy, and JuMP are important neighboring modeling projects but are not extra solver entries here. MiniCP derivatives are not counted automatically: MaxiCP and SeaPearl are retained for their substantive additional architectures, while elementary teaching implementations are omitted. Geas and other externally hosted systems were not promoted into entries without a verified substantive official GitHub repository.

Every heading URL was opened as a repository page or checked through GitHub's API. Each retained repository has additional non-README primary evidence, including implementation material. Some browser fetches failed and the public GitHub API reached its shared unauthenticated rate limit; direct read-only retrieval of public source and documentation supplied the missing evidence. No retained entry depends solely on a search snippet. No archived banner was observed on the retained repository pages; this is not a maintenance endorsement. Prototype, older-documentation, and relocated-development qualifications are called out where relevant. Default branches and documentation can change after this research date.

Final validation found 20 distinct repository heading URLs, at least two explicit criteria per entry, no unfinished placeholders, and successful HTTP responses for all 50 distinct cited links.
