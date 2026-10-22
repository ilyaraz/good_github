# Satisfiability modulo theories solvers

Research date: **2026-10-09**

This report selects **18 GitHub repositories** implementing SMT solvers, substantive theory-solving extensions, or reusable solver construction machinery. Coverage includes general-purpose engines, machine arithmetic, interpolation, quantified formulas, nonlinear real arithmetic, and strings. Solver bindings, verification applications, SAT-only engines, and benchmark collections are outside the selection. Delta-complete solvers are included with their different answer semantics identified explicitly.

Every repository's canonical URL was checked through its repository page and GitHub API, and each entry has additional primary implementation or architectural evidence. The criteria are judgments grounded in those sources, not independent proofs of correctness or comparative benchmarks. This is a guide to worthwhile engineering study; it does not imply that every component is uniformly exemplary. Unless specifically discussed, an entry makes no claim about maintenance cadence.

Criteria legend:

- **C1 — Difficult correctness:** invariants, numerical semantics, incremental state, proof obligations, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and components supporting multiple theories, integrations, or solving workflows.
- **C3 — Performance with structure:** concrete measures to control time or memory while preserving understandable architectural boundaries.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, refactoring, or complexity management; repository age alone does not qualify.

## General-purpose and extensible verification engines

### 1. [Z3Prover/z3](https://github.com/Z3Prover/z3)

**C++ · General-purpose SMT engine with multiple solver cores and language APIs.**

Study how a large reasoning engine keeps equality reasoning, theory solvers, preprocessing, and specialized search procedures connected without making them a single algorithm. The especially useful reading path is from the CDCL(T) invariants to the equality graph, then to tactics and result conversion.

- **C1:** Equality merges carry justifications; undo trails must restore congruence classes and their hash-table representation during backtracking. The documented invariants expose why an apparently local data-structure change can affect soundness.
- **C2:** Tactics compose transformations and solvers, while model, proof, and unsatisfiable-core converters relate answers back to the original problem. These are substantive reusable interfaces for building different solving pipelines.
- **C3:** The congruence-closure implementation uses smaller-class merging, parent tracking, and selective interaction with Boolean propagation to control repeated work.

Entry point: [Z3 Internals](https://z3prover.github.io/papers/z3internals.html), particularly equality/congruence closure, core interaction, and tactics. This document is explicitly a draft; it explains design principles rather than guaranteeing that every detail matches today's default solver configuration.

### 2. [cvc5/cvc5](https://github.com/cvc5/cvc5)

**C++ · Broad SMT solver, with synthesis and other reasoning services built around its SMT core.**

This is a strong study in sharing infrastructure across many theories while making proof production a cross-cutting concern. The [architecture paper](https://cvc5.github.io/papers/2022/BarbosaBBKLMMMN-TACAS22.pdf) distinguishes term rewriting, whole-formula preprocessing, propositional reasoning, theory combination, node management, and context-dependent state.

- **C1:** Theory combination, backtrackable state, and proof-producing transformations create interacting correctness obligations. Recent release notes give concrete examples: signed/unsigned extension mistakes in bit-vector rewriting and wrongly typed candidate values affecting array theory combination.
- **C2:** The SMT core underlies additional solvers for synthesis, abduction, interpolation, and quantifier elimination; shared node and proof infrastructure keeps these from becoming unrelated implementations.
- **C4:** The 2022 architecture account explains its evolution from CVC4, while the current [release history](https://github.com/cvc5/cvc5/blob/main/NEWS.md) records API representation changes, proof-format retirement, memory-lifetime fixes, and backend changes. This is evidence of managing compatibility and complexity over time.

### 3. [SRI-CSL/yices2](https://github.com/SRI-CSL/yices2)

**C · Configurable SMT engine offering both DPLL(T) and MCSat.**

Yices is particularly instructive for designing a solver API whose capabilities and cost depend on explicit configuration. Its contexts combine selected theory solvers with an operating mode, rather than exposing one undifferentiated solver object.

- **C1:** The API specifies legal theory combinations and state transitions. Interactive mode saves a recoverable state before search; other modes impose stronger restrictions on adding or retracting assertions. Correct cancellation and incremental use therefore have explicit contracts.
- **C2:** Independently configured contexts expose assertions, models, assumptions, and model-based checking through a common interface, while accommodating the materially different DPLL(T) and MCSat engines.
- **C3:** One-shot and multi-check modes permit more aggressive simplification; specialized difference-logic solvers can be selected instead of general simplex. These tradeoffs are documented, rather than hidden behind a generic claim of speed.

Entry point: [Context operations and configuration](https://yices.csl.sri.com/doc/context-operations.html), including solver selection, operating modes, invalid configurations, and model interpolation.

### 4. [usi-verification-and-security/opensmt](https://github.com/usi-verification-and-security/opensmt)

**C++ · Incremental SMT solving for combinations of arrays, uninterpreted functions, and linear arithmetic.**

Study the boundary between the public solver, logical term representation, theory handling, and propositional engine. The repository documents a restriction worth preserving in integrations: it supports integer or real arithmetic, but not their mixed combination.

- **C1:** Assertion frames retain their own unsatisfiability state, and popped assertions must disappear from the current view. Model retrieval and proof/interpolation retrieval have different required result states. These are concrete lifecycle invariants, not just mathematical theory concerns.
- **C2:** `MainSolver` accepts separate `Theory`, `TermMapper`, `THandler`, and `SimpSMTSolver` components, and exposes models, unsatisfiable cores, and interpolation contexts through dedicated types.
- **C3:** Its preprocessing interface skips assertion levels already simplified, demonstrating how incremental structure can avoid repeating work.

Entry point: [`src/api/MainSolver.h`](https://github.com/usi-verification-and-security/opensmt/blob/master/src/api/MainSolver.h), especially the component constructor, assertion stack, preprocessing, and result APIs. Use this official repository rather than the personal OpenSMT2 forks returned by some searches.

### 5. [OCamlPro/alt-ergo](https://github.com/OCamlPro/alt-ergo)

**OCaml · SMT solver oriented toward program-verification obligations.**

Alt-Ergo offers a different implementation culture from the predominantly C++ engines. Its documented evolution is unusually useful for understanding the interaction of quantifier instantiation, theory domains, model construction, and a changing SMT-LIB frontend.

- **C1:** The changelog records fixes involving accidental name capture in models, integer-constraint soundness, bit-vector normalization, floating-point reasoning, and completion of cross-propagation. These identify concrete semantic boundaries to inspect.
- **C3:** Word-level bit-vector propagators, interval domains, storage of domains in union-find, and removal of irrelevant CDCL decisions show performance work expressed through identifiable components.
- **C4:** Changes spanning 2017–2026 include replacing frontends, restructuring expression representations, retiring legacy solver variants, OCaml compatibility checks, assertion-enabled tests, and push/pop regression coverage.

Entry point: [`CHANGES.md`](https://github.com/OCamlPro/alt-ergo/blob/next/CHANGES.md). It contains implementation-level descriptions as well as compatibility history; follow the named modules and linked changes when choosing a subsystem to study. The repository's development branch is `next`.

### 6. [ultimate-pa/smtinterpol](https://github.com/ultimate-pa/smtinterpol)

**Java · Proof-producing, interpolating SMT solver.**

SMTInterpol is a particularly useful codebase for studying how explanations and partition information survive solving and are turned into interpolants. The standalone solver repository is counted here, rather than also counting the larger Ultimate framework.

- **C1:** The [clausifier](https://github.com/ultimate-pa/smtinterpol/blob/master/SMTInterpol/src/de/uni_freiburg/informatik/ultimate/smtinterpol/convert/Clausifier.java) connects rewriting to a proof tracker and maintains scoped mappings for literals, congruence-closure terms, and arithmetic shared terms. Its comments explicitly identify terms that must be unshared on pop.
- **C2:** SMT-LIB term infrastructure, DPLL reasoning, theory modules, proof tracking, and interpolation are separate components with substantial shared representations.
- **C3:** The [interpolator](https://github.com/ultimate-pa/smtinterpol/blob/master/SMTInterpol/src/de/uni_freiburg/informatik/ultimate/smtinterpol/interpolate/Interpolator.java) traverses proof structure with nonrecursive walkers and caches previously computed interpolants. Its postorder representation of interpolation trees makes both the invariants and reuse strategy visible.

### 7. [uuverifiers/princess](https://github.com/uuverifiers/princess)

**Scala · Presburger-arithmetic-centered SMT and first-order reasoning engine.**

Princess is valuable for comparing an arithmetic-oriented prover with SAT-centered designs. It supports quantified arithmetic and additional theories, and also acts as infrastructure for specialized solvers such as OSTRICH.

- **C1:** Theory integration includes translating axioms and functions into the internal representation while extending term order and tracking dependent theories. The implementation asserts ordering properties after constructing theory axioms.
- **C2:** The [`Theory` interface and utilities](https://github.com/uuverifiers/princess/blob/master/src/main/scala/ap/theories/Theory.scala) provide dependency handling and preprocessing/postprocessing hooks. Postprocessing applies to outputs such as interpolants and quantifier-elimination results, making the abstraction broader than satisfiability alone.

Entry points: the theory implementation above and the [official project/API guide](https://philipp.ruemmer.org/princess.shtml), which identifies `ap.SimpleAPI`, formula construction, Java integration, and proof/interpolation capabilities. Scope and completeness depend on the theory and quantifier fragment; the presence of a theory module is not a blanket decision guarantee.

## Bit-vectors, floating point, and quantified machine arithmetic

### 8. [bitwuzla/bitwuzla](https://github.com/bitwuzla/bitwuzla)

**C++ · SMT solver for bit-vectors, floating point, arrays, and uninterpreted functions.**

Study a redesign motivated by the limitations of an earlier successful solver. The authors' [2023 architecture paper](https://cs.stanford.edu/~niemetz/publications/2023/NiemetzP-CAV23.pdf) explains that the released C++ implementation was written afresh after an earlier Boolector-derived version, justifying its separate inclusion.

- **C1:** Incremental preprocessing must preserve assertion-level dependencies and restore state on pop. Rewriting must preserve semantics while avoiding cycles, and candidate models must pass the other theories' consistency checks.
- **C2:** Term/node management is separated from solving contexts, while the central engine coordinates dedicated theory solvers through a lemmas-on-demand refinement loop.
- **C3:** The architecture combines bit-blasting with propagation-based local search and uses shared expression DAGs, rewrite caches, and backtrackable data structures to manage repeated solving costs.

Entry point: the architecture paper, especially Sections 2–3. It is a dated design account, not a claim that all contemporary implementation defaults remain those of the first release.

### 9. [Boolector/boolector](https://github.com/Boolector/boolector)

**C · Historical bit-vector, array, and uninterpreted-function solver; archived.**

The repository explicitly states that development and maintenance have stopped and points to Bitwuzla as its successor. It remains a substantive study of expression ownership and specialized SMT engineering, rather than a recommendation for a new maintained dependency.

- **C1:** The API explains overflow-sensitive bit-vector encodings, assumptions invalidated after a satisfiability call, and reference-count ownership. Asserting a node gives the solver its own reference, a subtle but important distinction from the caller retaining a handle.
- **C2:** A rich public operator vocabulary is reduced to a smaller internal operator set over an expression DAG; the same representation supports construction, assertions, model queries, and incremental assumptions.
- **C3:** Configurable rewriting and preprocessing simplify both newly constructed expressions and the accumulated DAG.

Entry point: [C API documentation](https://boolector.github.io/docs/cboolector.html), particularly Quickstart, Internals, and Rewriting and Preprocessing. This contains substantive implementation material in addition to API signatures.

### 10. [stp/stp](https://github.com/stp/stp)

**C++ · SMT solver rooted in bit-vector and array reasoning, with additional theories in the current tree.**

STP provides a clear route from symbolic expressions to Boolean solving. Its current documentation maps the implementation into node factories, simplification, abstraction refinement, array extensionality, floating-point lowering, and SAT adapters.

- **C1:** Array extensionality, bit-level lowering, and floating-point encodings require semantic preservation across representations. The [testing guide](https://stp.github.io/stp/testing.html) describes query regressions, internal/API tests, memory checking, and undefined-behavior checks that target distinct failure classes.
- **C2:** A common `SATSolver` interface accommodates several backends, while separate node factories control construction-time simplification. The compatibility layer exposes the older C interface over the newer API.
- **C3:** The [source layout guide](https://stp.github.io/stp/code-guide.html) identifies constant-bit propagation, AST-to-SAT conversion, and ABC-based AIG/CNF processing as discrete optimization stages.

These two guides are the best entry points: they connect architectural boundaries to the test infrastructure that exercises them.

### 11. [martinjonas/Q3B](https://github.com/martinjonas/Q3B)

**C++ · BDD-based solver for quantified bit-vector formulas; research-oriented implementation.**

Q3B adds an algorithmic family missing from a list containing only CDCL(T) and bit-blasting engines. Although it uses Z3 for term representation and some simplification, its [system description](https://smt-comp.github.io/2023/system-descriptions/Q3B.pdf) explicitly says it does not use Z3's SAT/SMT-solving functionality.

- **C1:** Quantified bit-vector approximations must preserve the direction of the satisfiability conclusion. The [release notes](https://github.com/martinjonas/Q3B/blob/master/NEWS.md) record polarity-related unsoundness fixes, Boolean-equality abstraction fixes, and correction of DAG counting in simplification.
- **C3:** Variable-width approximation and partial computation of expensive operations address BDD growth; the implementation also coordinates parallel approximation attempts and termination during BDD operations.
- **C4:** The 2023 account documents fixes and ANTLR/Z3 compatibility updates after the 2019 tool release. It also states that active algorithm development had stopped after 2019. Later repository activity should not be mistaken for evidence that this historical development status has reversed.

## Arithmetic strategies and numerical semantics

### 12. [ths-rwth/smtrat](https://github.com/ths-rwth/smtrat)

**C++ · Modular SMT toolbox with a strong emphasis on arithmetic procedures and solver strategies.**

SMT-RAT is a particularly direct study of building a solver from reusable decision procedures. Its [architecture documentation](https://ths-rwth.github.io/smtrat/dc/da6/architecture.html) describes modules, strategies, managers, and a frontend for satisfiability, optimization, and quantifier elimination.

- **C1:** Each module distinguishes received from passed formulas and records the reasons for passing them onward. Those dependencies support incremental retraction across a composed strategy. Parallel backends must stop in a consistent state when another backend answers.
- **C2:** A strategy graph composes modules using conditions on formula properties. The same module protocol supports procedures that solve directly, simplify, or call additional backends.
- **C3:** Conditional dispatch, prioritized tasks, sequential/parallel execution, and preservation of incremental work make the performance policy explicit and inspectable.

Entry point: the architecture document above, especially Module, Manager, and Infeasible Subsets and Lemmas. Its generated documentation includes unfinished portions, so it should be paired with the named implementation classes when studying a specific strategy.

### 13. [dreal/dreal4](https://github.com/dreal/dreal4)

**C++ · Delta-complete SMT solving for nonlinear real constraints.**

dReal is useful for studying the junction of symbolic reasoning and interval numerical methods. A `delta-SAT` answer has a tolerance-based meaning and must not be interpreted as an exact satisfying assignment to the original constraints.

- **C1:** The [`Icp` interface and `EvaluateBox` contract](https://github.com/dreal/dreal4/blob/master/dreal/solver/icp.h) distinguish an inconsistent box, an accepted delta-satisfiable box, and a box requiring further branching. The contract also records which constraint explains an inconsistency.
- **C2:** Contractors, formula evaluators, boxes, and interval-constraint-propagation implementations are separate abstractions. They divide pruning, stopping conditions, branch selection, and model representation into reusable components.
- **C3:** The [`TheorySolver` interface](https://github.com/dreal/dreal4/blob/master/dreal/solver/theory_solver.h) contains separate contractor and formula-evaluator caches, linking repeated SMT theory checks to reusable numerical work.

These two headers provide a compact starting point before following the contractor and solver implementations.

### 14. [TendTo/dlinear](https://github.com/TendTo/dlinear)

**C++ · Delta-complete linear-real solver, derived from dLinear4 and dReal4.**

This is a deliberately identified derivative with a substantive linear-programming theory layer, not an independent-from-scratch lineage. It is included separately from dReal because its LP interfaces and bound preprocessing present a different numerical architecture; the older `martinjos/dlinear4` repository is not also counted.

- **C1:** The [`TheorySolver` contract](https://github.com/TendTo/dlinear/blob/main/dlinear/solver/TheorySolver.h) explains how Boolean assignments enable theory constraints, how inverted bounds produce conflict explanations, and how shared predicate abstraction keeps SAT and arithmetic literals aligned.
- **C2:** The abstract theory interface separates literal management, variable/row mapping, bound preprocessing, and concrete LP backends. Fixed literals have a distinct preprocessing path so their bounds can be retained across iterations.
- **C3:** Early detection of bound conflicts and preprocessing of fixed constraints reduce repeated LP work while remaining visible components.

Second entry point: [`DeltaSoplexTheorySolver.h`](https://github.com/TendTo/dlinear/blob/main/dlinear/solver/DeltaSoplexTheorySolver.h). Its comments explicitly describe relaxation of strict inequalities and treatment of disequalities for positive delta; study that contract before interpreting results as exact linear feasibility. The repository documents Linux-only native support.

### 15. [d3sformal/yaga](https://github.com/d3sformal/yaga)

**C++ · Smaller MCSat solver, developed as a research platform for alternatives to CDCL(T).**

Yaga is a useful, less famous comparison to Yices' MCSat engine. Its [author-written system description](https://smt-comp.github.io/2023/system-descriptions/Yaga.pdf) explains Boolean and rational-variable plugins for quantifier-free linear real arithmetic; this is a statement of the documented 2023 configuration, not an assertion about every later extension.

- **C1:** Rational bound stacks must remain valid under backtracking. Obsolete bounds are removed lazily while lower-level bounds are retained, making decision-level ownership an explicit correctness concern.
- **C2:** Boolean and rational reasoning use separate plugins around the model-constructing calculus, giving a focused example of theory integration at a smaller scale.
- **C3:** Watched variables, cached scan positions, rational-value caching, generalized VSIDS ordering, and LBD-based restarts are concrete measures for avoiding repeated search work.

Entry point: the two-page system description above. No claim of broad theory coverage or industrial maturity is needed for the codebase to satisfy these criteria.

## Solver construction and specialized string reasoning

### 16. [c-cube/sidekick](https://github.com/c-cube/sidekick)

**OCaml · Reusable CDCL(T) solver library with an SMT-LIB executable.**

Sidekick is a substantive descendant of Alt-Ergo Zero and mSAT, with its own extensible term representation and solver components. It is included for studying how to expose solver internals safely enough to implement new theories, rather than as a feature-equivalent substitute for the large general-purpose solvers.

- **C1:** Theory extensions can propagate literals, report conflicts, and participate in congruence closure. The [implementation guide](https://github.com/c-cube/sidekick/blob/main/doc/guide.md) also demonstrates the distinction between permanent assertions and assumptions when extracting an unsatisfiable core.
- **C2:** Theory registration, preprocessing hooks, simplification hooks, and custom constants make domain-specific extension a first-class operation. The project separates core machinery, concrete term/arithmetic representations, and the executable frontend.

Entry point: the guide's arithmetic, congruence-closure, and extension sections. Both the repository and guide describe unfinished documentation/proof work; parts of the guide discuss an older functorized interface, so consult current interfaces before copying its examples. This caveat matters when studying API evolution.

### 17. [uuverifiers/ostrich](https://github.com/uuverifiers/ostrich)

**Scala · Automata-based string SMT solver built on Princess.**

OSTRICH is a substantive string-theory implementation, not merely a frontend to Princess. It is worth studying for the treatment of replace operations, transducers, regular expressions, and the interaction between string structure and arithmetic constraints.

- **C1:** Backward propagation computes preimages of regular constraints through string operations. The [system description](https://smt-comp.github.io/2023/system-descriptions/OSTRICH.pdf) carefully distinguishes completeness for straight-line fragments from procedures applied outside those fragments without the same guarantees.
- **C2:** New string operations can be integrated through preimage implementations. The documented architecture combines automata reasoning with Princess' arithmetic and datatype facilities.
- **C3:** The described portfolio includes backward propagation, an ADT-based representation, and cost-enriched automata. The latter encode lengths and integer-valued operations without necessarily unfolding counting constraints into much larger expressions.

Entry point: the system description above for algorithms and extension contracts. The current repository additionally documents client/server execution to avoid repeated JVM startup and options for propagation, minimization, and portfolio selection.

### 18. [VeriFIT/z3-noodler](https://github.com/VeriFIT/z3-noodler)

**C++ · Substantive Z3 fork replacing the string solver with automata-based decision procedures.**

This fork warrants its own entry because it replaces a major theory implementation and has a separate string-solving research trajectory. The repository identifies equation stabilization as its principal approach and uses the Mata automata library. Count the Noodler subsystem here; the inherited Z3 engine is already covered above.

- **C1:** The [`AbstractDecisionProcedure` interface](https://github.com/VeriFIT/z3-noodler/blob/devel/src/smt/theory_str_noodler/decision_procedure.h) distinguishes candidate string solutions from satisfaction of their length constraints, and explicitly records whether length information is precise or an approximation. Model construction must reconcile the arithmetic model with strings.
- **C2:** Preprocessing, initialization, solution enumeration, length constraints, and model extraction form a common interface for multiple decision procedures.
- **C3:** Separate worklists prioritize candidate completed states; preprocessing and length checks can remove infeasible states before further automata processing.

Entry points: the interface above and the [Noodler source subtree](https://github.com/VeriFIT/z3-noodler/tree/devel/src/smt/theory_str_noodler). The verified development branch is `devel`; using `master` would lead a reader into inherited Z3 material instead.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, including general SMT architecture; bit-vector/floating-point specialists; OpenSMT and modular arithmetic strategies; OCaml and Rust implementations; Java/Scala interpolation engines; delta-complete nonlinear and linear solvers; string and transducer solvers; MCSat research implementations; quantified BDD-based bit-vectors; and finite-field SMT. Follow-up searches and official project links were used to resolve owners and locate architecture papers, API contracts, implementation files, and release histories. Later Rust and finite-field searches increasingly returned bindings, early implementations requiring more validation, or subsystems of already selected solvers, rather than clearly stronger additions.

The selection spans C, C++, OCaml, Java, and Scala, and ranges from broad solver platforms to focused research engines. The absence of a Rust or Python implementation is a selection outcome, not a claim that no such solvers exist. Stars and repository creation dates were not used as quality criteria.

Important boundaries and exclusions:

- pySMT, JavaSMT, SMT-Switch, and language bindings provide valuable integration abstractions but were excluded because this report concentrates on solver implementations. Model checkers, Horn-solving applications, proof checkers, fuzzers, and SAT-only engines were likewise not used to enlarge the count.
- CVC4, older dReal versions, the earlier dLinear4 repository, and mSAT were not separately counted to limit overlapping lineages. Bitwuzla's documented rewrite and Noodler's replacement theory implementation justify their separate treatment. Boolector is retained explicitly as an archived historical study.
- veriT is an important omission from a GitHub-only list: its [official download page](https://www.verit-solver.org/download/) offers substantive source releases, but this search did not verify an official substantive GitHub repository. MathSAT/OptiMathSAT were also not included because an appropriate official GitHub implementation was not verified. These omissions say nothing about solver quality.
- Repository metadata and archive flags were checked on the research date. A recent push was not treated as proof of sustained maintenance. Dated papers describe specific designs or configurations, and entries flag material historical limitations instead of silently presenting them as current feature guarantees.

All retained entries were checked against a repository page/API and at least one additional primary source containing technical substance. Some web-reader requests failed, so the affected public source files and documentation were read directly over HTTPS. No candidate code was executed, no dependencies were installed, and no repositories were cloned. No performance ranking or independent correctness validation was attempted.
