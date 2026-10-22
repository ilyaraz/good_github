# Combinatorial optimization and scheduling engines

Research date: **2026-10-09**

This report selects 25 GitHub repositories implementing reusable discrete optimization engines: mixed-integer and constraint programming, scheduling and timetabling, vehicle routing, dynamic programming, packing, metaheuristics, and Boolean optimization. The emphasis is on implementation decisions an experienced engineer can study, rather than modeling demonstrations or service wrappers. General solvers are included for their discrete optimization subsystems; each monorepo is counted once. Heuristic search engines are not presented as guaranteeing optimality.

Criteria legend:

- **C1 — Difficult correctness:** invariants, numerical semantics, concurrency, adversarial inputs, or failure handling materially shape the implementation.
- **C2 — Reusable abstractions:** substantial modeling, propagation, search, or extension interfaces support different problems.
- **C3 — Performance with structure:** concrete mechanisms address search, memory, or evaluation costs while exposing identifiable architectural boundaries.
- **C4 — Sustained evolution:** primary evidence connects years of development to testing, compatibility, or complexity management.

The criterion assessments are grounded engineering judgments from the linked material, not correctness proofs, benchmark results, or a claim that every component is exemplary. Links in each entry are recommended reading entry points as well as supporting evidence.

## General discrete optimization and constraint engines

### 1. [google/or-tools](https://github.com/google/or-tools)

**C++ core; Python, Java, and C# interfaces — optimization suite.** Focus on the CP-SAT scheduling subsystem and the separate routing/constraint solver rather than treating the entire suite as one algorithm. It is particularly useful for studying how reusable interval machinery supports multiple scheduling propagators.

- **C1:** `SchedulingConstraintHelper` documents when cached bounds may be stale, requires synchronization when switching time direction, and distinguishes task presence from start/end/size bounds. Those rules expose the correctness burden behind incremental propagation.
- **C2 / C3:** The helper shares task orderings among propagators and can operate on transformed subsets of intervals, reducing repeated sorting while supporting different scheduling constraints. Read the [scheduling helper](https://github.com/google/or-tools/blob/stable/ortools/sat/scheduling_helpers.h); the [repository code map](https://github.com/google/or-tools#codemap) locates the distinct CP-SAT, routing, and graph optimization implementations.

### 2. [scipopt/scip](https://github.com/scipopt/scip)

**C with C++ extension interfaces — constraint integer programming and branch-cut-and-price.** **Official read-only GitHub mirror:** the repository identifies ZIB's GitLab instance as its origin. SCIP is a strong study of how a general search engine delegates domain-specific mathematics to plugins.

- **C1:** Constraint handlers must enforce and check their semantics; propagation and separation are distinct responsibilities. The cumulative handler implements resource-capacity reasoning and explicitly limits the time horizon to avoid integer overflow.
- **C2 / C3:** Handler callbacks separate feasibility, propagation, presolving, and cuts. Priorities, frequencies, and delayed execution let expensive routines coexist with cheaper inference. Start with the [constraint-handler development guide](https://www.scipopt.org/doc/html/CONS.php) and [cumulative constraint implementation](https://github.com/scipopt/scip/blob/master/src/scip/cons_cumulative.c).

### 3. [ERGO-Code/HiGHS](https://github.com/ERGO-Code/HiGHS)

**C++ — LP, QP, and mixed-integer optimization.** The relevant subsystem here is the MIP engine. Its search code gives a concrete view of numerical optimization and discrete branching meeting at the same state boundary.

- **C1:** Search explicitly checks integrality against feasibility tolerances, asserts finite solution values, and protects the domain-change stack from losing an infeasibility flag. Symmetry information is checked for validity in child nodes.
- **C3:** RINS and RENS neighborhoods restrict integer domains using incumbent and relaxation solutions; pseudocosts and selectable child rules are explicit search components. The [MIP search implementation](https://github.com/ERGO-Code/HiGHS/blob/master/highs/mip/HighsSearch.cpp) is a useful entry point for tracing these tradeoffs. These observations concern the implementation, not a claim about relative benchmark speed.

### 4. [coin-or/Cbc](https://github.com/coin-or/Cbc)

**C++ — callable branch-and-cut MILP solver.** Study the representation of suspended subproblems and the distinction between a stored search node and the currently active model.

- **C1:** `CbcModel` explains how ancestry reconstructs subproblems, how node deletion can recursively release ancestors, and how tight and loose cuts interact with the LP basis. Its integrality and stopping-gap parameters also make numerical semantics explicit.
- **C2:** The model is a reusable branch-and-cut controller with separate node, branching, heuristic, event, and solver-interface collaborators, rather than a solver hard-coded to one application. Begin with [CbcModel.hpp](https://github.com/coin-or/Cbc/blob/master/src/CbcModel.hpp).

The [release history](https://github.com/coin-or/Cbc#changelog) is additionally instructive: it records a reverted time-limit change that caused incorrect cleanup results, fixes to MIP-start handling after presolve, and build/test corrections. This is concrete maintenance evidence, without assuming every historical issue is solved uniformly.

### 5. [Gecode/gecode](https://github.com/Gecode/gecode)

**C++ — finite-domain constraint programming kernel and search engines.** A useful contrast to trail-centric solvers: inspect spaces, actors, propagators, branchers, and the contract for copying a search state.

- **C1:** Cloning requires a stable, nonfailed space. Branch choices must be committed in the order in which they were obtained, and older choices can become invalid after new choices are generated.
- **C2 / C3:** The kernel separates variable events, propagator costs, branching, and space management. Committing a choice deliberately does not propagate, enabling path recomputation; propagation queues are organized by cost. Read the [kernel contracts and implementation](https://github.com/Gecode/gecode/blob/main/gecode/kernel/core.hpp) and the [Modeling and Programming guide](https://www.gecode.org/doc-latest/MPG.pdf).

### 6. [chocoteam/choco-solver](https://github.com/chocoteam/choco-solver)

**Java — embeddable constraint programming solver.** Especially useful for understanding the contract that makes independently written propagators cooperate in a common engine.

- **C1:** The propagator abstraction documents idempotence, domain-wipeout failure, entailment, and internal references when a variable appears repeatedly. Passivated propagators must become active again when backtracking invalidates their entailment.
- **C2 / C3:** Generic propagators choose event subscriptions, incremental versus coarse filtering, and priorities. These controls avoid waking every constraint for every domain change. The [Propagator implementation](https://github.com/chocoteam/choco-solver/blob/master/solver/src/main/java/org/chocosolver/solver/constraints/Propagator.java) and [propagator design guide](https://choco-solver.org/docs/advanced-usages/propagator/) explain the extension contract and fixed-point implications.

### 7. [radsz/jacop](https://github.com/radsz/jacop)

**Java with a Scala modeling layer — constraint programming library.** JaCoP offers a different JVM implementation of global constraints, finite domains, and configurable search. Its store is a compact place to study the boundary between propagation and backtracking.

- **C1:** The store distinguishes notifications before and after a search level is removed, allowing stateful constraints to restore their internal structures. Auxiliary variables introduced by decompositions must also be grounded for a valid solution.
- **C2 / C3:** Constraints share a store with deduplicated reevaluation queues and specialized Boolean change histories; this infrastructure supports many constraint types without duplicating search-state management. Read [Store.java](https://github.com/radsz/jacop/blob/develop/src/main/java/org/jacop/core/Store.java).

The [changelog](https://github.com/radsz/jacop/blob/develop/CHANGELOG) records optional-task cumulative constraints, restart search, numerical-bound changes, and preservation of an older default search for compatibility. It is useful context for interpreting differences between releases.

### 8. [ConSol-Lab/Pumpkin](https://github.com/ConSol-Lab/Pumpkin)

**Rust — lazy-clause-generation constraint optimization solver.** Pumpkin is a research-oriented implementation with scheduling constraints and independent certificate checking described by the project. The cumulative subsystem is particularly well documented.

- **C1:** Its cumulative model precisely defines noninterruptible tasks and half-open execution intervals, so simultaneous resource use has an unambiguous meaning. Propagation options distinguish domain-hole removal from bound tightening and select explanations for conflicts and deductions.
- **C3:** The implementation exposes per-point versus interval time-tabling and incremental variants, including incremental backtracking. These are explicit alternatives for the cost of maintaining resource profiles. Read the [cumulative module](https://github.com/ConSol-Lab/Pumpkin/blob/main/pumpkin-crates/propagators/src/propagators/cumulative/mod.rs) and [propagation options](https://github.com/ConSol-Lab/Pumpkin/blob/main/pumpkin-crates/propagators/src/propagators/cumulative/options.rs). Certificate support is a project capability, not an independently performed verification in this report.

### 9. [plaans/aries](https://github.com/plaans/aries)

**Rust — constraint solver, scheduling, and automated planning workspace.** Counted once, with emphasis on `aries-solver` and scheduling. Its optional-variable representation makes it particularly relevant to tasks and actions whose existence is itself a decision.

- **C1:** Presence literals are separate from variable domains. The solver checks compatible presence scopes before introducing temporal edges and avoids passing optional constraints to an LP reasoner that cannot handle them.
- **C2 / C3:** Search coordinates multiple reasoners, including clauses and temporal reasoning. Redundant dynamic edges are explicitly used to detect cyclic propagation missed by independent linear constraints. Inspect [solver_impl.rs](https://github.com/plaans/aries/blob/master/solver/src/solver/solver_impl.rs) and the [workspace architecture/status description](https://github.com/plaans/aries#constraint-programming-solver).

The repository labels parts of its planning stack experimental or superseded; those labels should not be generalized to every crate.

### 10. [toulbar2/toulbar2](https://github.com/toulbar2/toulbar2)

**C++ with additional interfaces — exact optimization over cost-function networks.** This broadens the selection beyond ordinary hard-constraint CP: objectives and feasibility are represented by local cost functions, covering weighted CSPs and several discrete graphical-model problems.

- **C1:** The `WCSP` state distinguishes lower bounds, upper bounds, cost shifts, backtrackable data, and nonbacktrackable propagation queues. Reentrancy and restoration are visible design concerns.
- **C2 / C3:** Different consistency queues, global cost functions, separators, and variable-elimination bookkeeping share one weighted-problem abstraction. Bounded elimination stores enough information to reconstruct eliminated variables. Start with [tb2wcsp.hpp](https://github.com/toulbar2/toulbar2/blob/master/src/core/tb2wcsp.hpp); it connects the mathematical operations to their storage and lifecycle costs.

### 11. [pschaus/oscar](https://github.com/pschaus/oscar)

**Scala — OscaR-CP constraint programming and large-neighborhood search.** **Maintenance caveat:** the repository says development is no longer active and points to MaxiCP for ongoing development. It remains a substantive historical implementation, not merely an abandoned demonstration.

- **C1:** The store tracks whether it is inside fixed-point propagation, prevents inappropriate duplicate queueing, and resets each dequeued constraint's state when cleaning queues. Those details matter when failure interrupts propagation.
- **C2 / C3:** A Scala modeling layer sits over separate AC5-style event queues and AC3-style constraint queues with priorities and execution statistics. Compare the [CPStore implementation](https://github.com/pschaus/oscar/blob/main/src/main/scala/oscar/cp/core/CPStore.scala) with the [modeling and extension guide in the repository](https://github.com/pschaus/oscar#oscar-cp-tutorial). This entry is a study recommendation, not an active-maintenance recommendation.

## Planning, timetabling, and production scheduling

### 12. [TimefoldAI/timefold-solver](https://github.com/TimefoldAI/timefold-solver)

**Java; Java/Kotlin domain models — embeddable planning and local-search engine.** Study how domain-object updates, moves, score calculation, and derived variables are coordinated. The relevant code is the solver core, not the separately offered managed planning services.

- **C1:** The score director has explicit checks for score, undo, cloning, and shadow-variable corruption. Its value-range caches must not be shared between directors because they depend on the current working-solution clone.
- **C2 / C3:** Score directors and variable support provide reusable bookkeeping across planning models, while caches are created lazily to avoid expensive work in operations that do not perform moves. The [AbstractScoreDirector implementation](https://github.com/TimefoldAI/timefold-solver/blob/main/core/src/main/java/ai/timefold/solver/core/impl/score/director/AbstractScoreDirector.java) is the most useful starting point for these lifecycle contracts; the [official introduction](https://docs.timefold.ai/timefold-solver/latest/introduction) establishes its scheduling and routing roles.

### 13. [UniTime/cpsolver](https://github.com/UniTime/cpsolver)

**Java — reusable local-search library with course, examination, and student scheduling.** This entry covers the solver library used for UniTime's timetabling models.

- **C1:** Iterative forward search maintains feasible but potentially incomplete assignments. Assigning a value removes conflicting assignments, preserving hard constraints on the remaining assigned variables.
- **C2:** Neighbor selection, termination, and solution comparison are separate interfaces; the same search structure can support different timetabling models. The [Solver implementation and algorithm description](https://github.com/UniTime/cpsolver/blob/master/src/org/cpsolver/ifs/solver/Solver.java) explain the contract directly.
- **C4:** The [release history](https://github.com/UniTime/cpsolver/releases) documents 2023–2026 evolution: shorter locking around distance caches, fixes to best-solution serialization, configurable defaults preserving earlier behavior, and new constraints. These records show management of operational complexity, not just elapsed project age.

### 14. [frePPLe/frepple](https://github.com/frePPLe/frepple)

**C++ planning engine with Python/Django integration — production and supply-chain planning.** Focus on the open repository's heuristic planning engine. Its integration of demands, operations, capacity, and material availability is more application-oriented than a generic CP kernel.

- **C1:** Planning exposes commit/rollback behavior; the implementation catches failures during cluster planning and cleans affected planning state. The problem includes coordinating capacity with available materials and dependent operations.
- **C2 / C3:** Demands are grouped by planning cluster and dispatched through a shared solver interface. Parallelism is deliberately restricted in logging, non-autocommit, and certain unconstrained modes, including an explicit concern about thread overhead. Read [solverplan.cpp](https://github.com/frePPLe/frepple/blob/master/src/solver/solverplan.cpp) and the [production-planning description](https://github.com/frePPLe/frepple/blob/master/doc/features.rst). The broader product documentation includes commercial features; this entry does not assume all advertised functionality is in the open engine.

## Vehicle routing engines

### 15. [PyVRP/PyVRP](https://github.com/PyVRP/PyVRP)

**Python orchestration and C++ search — vehicle routing with operational constraints.** The inspected current documentation is labeled **1.0.0a0** and describes iterated local search. Older publications describe hybrid genetic search, so readers should match architectural claims to the version they study.

- **C2:** `Model`, `Solution`, `CostEvaluator`, `PenaltyManager`, stopping criteria, and configurable local-search operators are separate components. The implementation tutorial reconstructs the solve loop from them.
- **C3:** Search neighborhoods restrict which edges are evaluated, while local search and perturbation run in C++. Adaptive penalties balance exploration of feasible and infeasible routes. Start with [the implementation walkthrough](https://pyvrp.org/notebooks/pyvrp_implementation.html) and [the ILS architecture](https://pyvrp.org/dev/algorithm.html).

This entry concerns the public solver; the repository separately marks some features as Enterprise.

### 16. [VROOM-Project/vroom](https://github.com/VROOM-Project/vroom)

**C++ — rich vehicle-routing engine and library.** VROOM combines vehicle capacities, time windows, skills, shipments, and breaks with externally supplied travel costs. It is worth studying how the route representation supports repeated feasibility checks.

- **C1:** `TWRoute` tracks earliest and latest feasible times that may come from different windows. Job/break ordering also depends on current load, so temporal and capacity feasibility cannot be treated independently.
- **C2 / C3:** A time-window route extends the common raw-route representation and maintains forward/backward updates for timing and break-load margins. This gives neighborhood operators reusable state instead of requiring complete route recomputation. Read [tw_route.h](https://github.com/VROOM-Project/vroom/blob/master/src/structures/vroom/tw_route.h); the [repository's model description](https://github.com/VROOM-Project/vroom#how-it-works) explains jobs, shipments, vehicles, and routing-engine integration. No advertised latency figure is treated as a measured result here.

### 17. [graphhopper/jsprit](https://github.com/graphhopper/jsprit)

**Java — extensible toolkit for rich vehicle-routing problems.** Its state-management layer is especially useful when studying how custom operational constraints interact with ruin-and-recreate search.

- **C1:** Stateful constraints depend on problem, route, activity, and vehicle-specific state. The manager participates in ruin, insertion, and iteration events so those cached values can be updated at the right lifecycle points.
- **C2 / C3:** State identifiers and updater/visitor interfaces allow new constraints to use the same machinery. Indexed arrays coexist with route maps and vehicle-dependent state; the implementation also retains a deprecated-index fallback for compatibility. Read [StateManager.java](https://github.com/graphhopper/jsprit/blob/master/jsprit-core/src/main/java/com/graphhopper/jsprit/core/algorithm/state/StateManager.java) alongside the [insertion strategy interface](https://github.com/graphhopper/jsprit/blob/master/jsprit-core/src/main/java/com/graphhopper/jsprit/core/algorithm/recreate/InsertionStrategy.java).

### 18. [reinterpretcat/vrp](https://github.com/reinterpretcat/vrp)

**Rust — multiobjective vehicle-routing solver and reusable search infrastructure.** Count the `vrp-core` and `rosomaxa` components together. This is a useful alternative to both CP-based routing and a single fixed local-search trajectory.

- **C2:** The solver separates problem/goal models, insertion contexts, refinement contexts, population management, mutation/search operators, and termination. Objectives can involve fleet usage and unassigned jobs as well as travel cost.
- **C3:** Its evolutionary loop uses ruin-and-recreate mutation and population management to balance exploration and exploitation. The module describes selecting heuristics using both search quality and latency; omitting crossover also avoids constructing a feasibility-preserving VRP crossover. Read the substantial [solver module documentation and code](https://github.com/reinterpretcat/vrp/blob/master/vrp-core/src/solver/mod.rs). These are architectural observations, not guarantees of Pareto completeness or optimality.

## Dynamic programming, reusable search, and packing

### 19. [domain-independent-dp/didp-rs](https://github.com/domain-independent-dp/didp-rs)

**Rust with Python interface — domain-independent dynamic programming.** Relevant components are DyPDL models and generic heuristic-search engines, counted as one repository. This provides a different modeling route for routing, scheduling, and packing than MILP or CP.

- **C1:** The state registry separates signature variables from resource variables and combines model dominance with the direction of cost optimization. It warns about continuous variables in signatures and contains tests of dominance and replacement behavior.
- **C2 / C3:** Model-independent state storage and search interfaces support multiple algorithms. Dominated states are discarded; shared signatures and hash-based lookup reduce duplicate-state costs. Begin with the [state registry](https://github.com/domain-independent-dp/didp-rs/blob/main/dypdl-heuristic-search/src/search_algorithm/data_structure/state_registry.rs) and [search-library module map](https://github.com/domain-independent-dp/didp-rs/blob/main/dypdl-heuristic-search/src/lib.rs).

### 20. [xgillard/ddo](https://github.com/xgillard/ddo)

**Rust — decision-diagram-based combinatorial optimization framework.** DDO lets a problem author provide a dynamic-programming model and a relaxation, then reuse the optimization engine. Its explicit mathematical extension contract makes it particularly valuable for advanced study.

- **C1:** A merged decision-diagram node must overapproximate everything feasible from the original nodes. Violating this condition can invalidate the optimizer; the library documentation makes that responsibility explicit rather than hiding it in an interface signature.
- **C2 / C3:** `Problem` and `Relaxation` separate domain logic from diagram construction and search; the documented example also uses parallel solving. The [crate-level design documentation and complete example](https://github.com/xgillard/ddo/blob/master/ddo/src/lib.rs) connect state representation, transitions, objective contributions, and relaxation. The framework supplies machinery, but a client's relaxation still needs its own correctness argument.

### 21. [N-Wouda/ALNS](https://github.com/N-Wouda/ALNS)

**Python — adaptive large-neighborhood-search framework.** A smaller and more approachable engine than the general solvers, but substantive as a reusable implementation. It supports problem-specific destroy/repair operators while owning the adaptive search loop.

- **C2:** Solution state, destroy and repair operators, acceptance, operator selection, stopping rules, and outcome callbacks are separate protocols or callables.
- **C3:** Operator selection is updated from observed outcomes, and statistics record operator results and iteration timing. The framework makes time/quality tradeoffs inspectable rather than embedding them in one problem's code. Read [ALNS.py](https://github.com/N-Wouda/ALNS/blob/master/alns/ALNS.py) and [the algorithm explanation](https://github.com/N-Wouda/ALNS/blob/master/docs/source/setup/introduction_to_alns.rst).

One important extension contract is explicit: callbacks can mutate a candidate, but the engine does not reevaluate it afterward. Custom operators remain responsible for their problem's feasibility and state-copy semantics.

### 22. [optframe/optframe](https://github.com/optframe/optframe)

**Modern C++ — single- and multiobjective metaheuristic framework.** Study how solution representations and evaluations are paired with moves and search techniques, rather than starting with its long algorithm catalog.

- **C1 / C2:** A move distinguishes applicability, application, reverse moves, evaluation invalidation, and optional delta-cost evaluation. Applying and then undoing a move does not automatically make a cached evaluation valid again. These contracts make domain-specific neighborhoods reusable across searches. See [Move.hpp](https://github.com/optframe/optframe/blob/master/include/OptFrame/Core/Move.hpp).
- **C4:** The [project history](https://github.com/optframe/optframe/blob/master/HISTORY.md) traces development from 2007 through templates, automated runtime checking, and a later move to smart pointers and move semantics. This directly connects longevity to complexity management. The README also warns that major version changes left some tutorials needing updates, so examples should be matched to the checked-out version.

### 23. [fontanf/packingsolver](https://github.com/fontanf/packingsolver)

**C++ with Python and browser interfaces — geometric cutting and packing.** The repository covers one-dimensional items, rectangles, guillotine cutting, boxes, box stacks, and irregular shapes. Its rectangle optimizer is a useful entry point for studying an algorithm portfolio driven by problem structure.

- **C1:** Bounds account for whether an item can fit in any permitted orientation. The code also adjusts profit bounds for negative resource penalties so that optimistic bounds remain valid.
- **C2 / C3:** Shared objective and instance abstractions support bin packing, knapsack, and open-dimension variants. The optimizer combines cheap area bounds with stronger relaxations and column-generation options, disabling incompatible combinations where necessary. Read [rectangle/optimize.cpp](https://github.com/fontanf/packingsolver/blob/master/src/rectangle/optimize.cpp) and the [problem/objective inventory](https://github.com/fontanf/packingsolver#problem-types). Availability of bounds does not imply that every configured method proves optimality.

## MaxSAT and pseudo-Boolean optimization

### 24. [sat-group/open-wbo](https://github.com/sat-group/open-wbo)

**C++ — MaxSAT and pseudo-Boolean optimization framework.** **Historical reference:** the repository README presents version 2.1 from September 2018. It is included for its substantive solver architecture, without claiming a current release cadence. This represents Boolean optimization rather than general SAT decision solving.

- **C1:** The OLL algorithm tracks assumption-to-constraint mappings, finds minimum weights in unsatisfiable cores, increases a lower bound, and splits weighted soft clauses. Correctness depends on preserving costs while relaxing cores.
- **C2:** SAT backends, encodings, and optimization algorithms are separate areas of the framework; weighted and unweighted modes use different algorithm choices. Start with the [OLL implementation](https://github.com/sat-group/open-wbo/blob/master/algorithms/Alg_OLL.cc) and the [repository's algorithm/configuration description](https://github.com/sat-group/open-wbo#open-wbo-maxsat-solver). It offers a clear study of exact optimization built on repeated satisfiability queries.

### 25. [crillab/gophersat](https://github.com/crillab/gophersat)

**Go — native SAT, pseudo-Boolean, and MaxSAT solver.** Included specifically for its optimization core and weighted-constraint layer, not merely because it solves SAT. It brings a smaller Go codebase and a channel-based result API into a selection otherwise dominated by C++, JVM languages, and Rust.

- **C1:** Minimization saves the incumbent model before adding a stricter pseudo-Boolean bound. Hard infeasibility is distinguished from positive-cost feasible solutions, and the MaxSAT layer hides auxiliary blocking variables when reconstructing the user's model.
- **C2:** A reusable PB solver underlies named-variable hard/soft constraints and both direct minimization and streamed optimization results. Read [the core solver](https://github.com/crillab/gophersat/blob/master/solver/solver.go) and [the MaxSAT problem implementation](https://github.com/crillab/gophersat/blob/master/maxsat/problem.go).

The README limits supported PB integer sizes, and the MaxSAT constructor contains an explicit unresolved note about a soft-cardinality case. This is a useful implementation study with concrete scope limits, not a blanket endorsement of all encodings.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, including constraint propagation and scheduling engines; branch-and-cut/MIP; Java, Scala, and Rust CP implementations; rich vehicle routing; workforce and university timetabling; manufacturing planning; adaptive large-neighborhood search; decision diagrams and domain-independent DP; geometric packing; and Go/MaxSAT/pseudo-Boolean optimization. Follow-up searches for railway/project scheduling and alternative-language implementations mostly returned narrower modeling applications, wrappers, or already represented algorithm families; the Go search added Gophersat. The selection therefore stopped at diminishing architectural returns, rather than treating 25 as an exhaustive ecosystem count.

Every retained repository's GitHub page was opened, and at least one additional primary implementation or design source was read. Default branches were checked before constructing source links. GitHub API access encountered shared unauthenticated rate limiting; repository HTML and public raw source files supplied the verification instead. No repository code was run, dependencies installed, maintainers contacted, or performance benchmarks reproduced. Source links follow inspected branches rather than immutable commits, so future contents can change.

Excluded were awesome lists, portfolio schedulers, thin OR-Tools/CP-SAT service wrappers, solver-specific modeling demonstrations, general workflow/job-execution schedulers, road shortest-path engines without fleet optimization, and continuous-only optimizers. Proprietary engines without substantive public implementations do not belong in this GitHub selection. Related predecessors, bindings, and forks were not counted as extra entries; OR-Tools, Aries, and the Rust VRP workspace each appear once. SCIP's official mirror and the historical status of OscaR-CP and Open-WBO are identified explicitly.

Coverage is strongest in reusable exact search and routing. It is not exhaustive for specialized industrial schedulers, every CP research prototype, or every SAT/SMT optimizer. Current maintenance quality was not inferred from stars, creation dates, or a recent push. C4 is asserted only where the inspected history connects development across years to concrete maintenance decisions; the other selections qualify through implementation evidence under C1–C3.
