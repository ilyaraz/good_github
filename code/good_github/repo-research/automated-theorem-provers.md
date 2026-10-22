# Automated theorem provers

Research date: **2026-10-09**

This selection covers 20 GitHub repositories implementing automated proof search: first-order saturation, connection and tableau calculi, higher-order reasoning, SMT refutation, and proof-producing automation inside a proof assistant. SMT solvers belong here because unsatisfiability of a negated conjecture establishes validity in the supported theory. General proof assistants are not included merely because they check proofs; the entries below identify the actual automation under study. GAPT is counted once for its built-in provers and supporting proof infrastructure.

The criteria are engineering judgments grounded in the linked implementations and documentation, not certifications of soundness or claims that every component is exemplary. No candidate code was executed. Repository availability does not imply current maintenance, and no maintenance claim is inferred from stars or a recent push.

**Criteria legend**

- **C1 — Difficult correctness:** logical invariants, concurrency, numerical semantics, malformed inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial representations, interfaces, and algorithms serving multiple reasoning tasks.
- **C3 — Performance with structure:** concrete search, memory, or computational constraints addressed through inspectable architectural mechanisms.
- **C4 — Sustained evolution:** years of documented changes together with compatibility, testing, or complexity management.

## Saturation, higher-order, and connection provers

### 1. [eprover/eprover](https://github.com/eprover/eprover)

**Language / role:** C; equational saturation prover with first-order and higher-order support.

Study how a prover connects compact term representations, proof production, strategy selection, and explicit resource limits. E is particularly useful for examining the boundary between logically complete search and practical axiom selection.

- **C1:** The implementation distinguishes signature symbols, ordinary variables, fresh premise variables, and de Bruijn variables. Its higher-order representation uses flat application spines. These conventions expose concrete variable-renaming and binding invariants rather than hiding them behind a generic expression class. See the [implementation notes](https://github.com/eprover/eprover/blob/master/DOC/implementation_notes.org).
- **C3:** The [repository documentation](https://github.com/eprover/eprover#readme) describes timed strategy schedules, multicore scheduling, memory limits, and separate `auto`/`satauto` modes. It explicitly warns that heuristic axiom pruning can lose completeness; this is an instructive documented performance tradeoff.

**Entry points:** [term implementation notes](https://github.com/eprover/eprover/blob/master/DOC/implementation_notes.org); [documentation directory](https://github.com/eprover/eprover/tree/master/DOC). The README also identifies limits of its proof-checking utilities; proof output should not be confused with universal independent checking.

### 2. [vprover/vampire](https://github.com/vprover/vampire)

**Language / role:** C++; general automated reasoning and saturation prover.

Study a substantial search engine whose interfaces make clause lifecycle, inference generation, simplification, and indexing visible. The central saturation class is a useful map before exploring individual calculi.

- **C1:** Clause reduction, parenthood, activation, and removal have explicit hooks. The implementation even handles cases in which equality can arise after preprocessing despite being absent initially. These are correctness-sensitive interactions between preprocessing and later inference.
- **C2:** The same framework composes generating and simplifying inference engines, literal selection, term ordering, splitting, and index management through distinct interfaces.
- **C3:** Active/passive/unprocessed containers, separate generating and simplifying indices, postponed removals, and resource-estimation hooks expose how the engine controls a growing search space. These mechanisms are visible in [SaturationAlgorithm.hpp](https://github.com/vprover/vampire/blob/master/Saturation/SaturationAlgorithm.hpp).

**Entry point:** [saturation engine interface](https://github.com/vprover/vampire/blob/master/Saturation/SaturationAlgorithm.hpp). This is the main project repository, not an independently counted fork.

### 3. [sneeuwballen/zipperposition](https://github.com/sneeuwballen/zipperposition)

**Language / role:** OCaml; typed higher-order superposition prover and bundled Logtk reasoning library.

Study how to make a calculus extensible without erasing the distinctions between inference, rewriting, redundancy, and proof-state manipulation. The project explicitly emphasizes experimentation and modularity; it should not be selected solely for production-throughput expectations.

- **C1:** The environment contract distinguishes unchanged from rewritten clauses, constrains backward simplification to the active set, and carries proof parents with term and literal rewrites. It also documents when finite inference extraction requires terminating unification.
- **C2:** OCaml module relationships connect clauses, contexts, proof states, streams, and stream queues. Registered unary/binary inference rules, conversion hooks, simplifiers, and signals support multiple calculi within one engine. These contracts are concrete in [env_intf.ml](https://github.com/sneeuwballen/zipperposition/blob/master/src/prover/env_intf.ml).

**Entry points:** [environment interface](https://github.com/sneeuwballen/zipperposition/blob/master/src/prover/env_intf.ml); [published API index](https://sneeuwballen.github.io/zipperposition/2.0/libzipperposition/Libzipperposition/index.html). The published API is versioned 2.0; current source can differ.

### 4. [leoprover/Leo-III](https://github.com/leoprover/Leo-III)

**Language / role:** Scala; higher-order paramodulation prover with external-prover cooperation and non-classical logic embeddings.

Study the interaction between native higher-order search and translation to other reasoning engines. The project covers polymorphic higher-order logic and uses ordering-constrained paramodulation, as described in its repository introduction.

- **C1:** The [usage guide](https://github.com/leoprover/Leo-III/blob/master/USAGE.md) distinguishes unification depth and number-of-unifier limits, type errors, exhausted search, and timeouts. Its modal encoding distinguishes domain semantics and local/global assumptions; these choices change the theorem being proved.
- **C2:** A shared proving pipeline supports several TPTP dialects, configurable external ATP cooperation, and semantic embeddings of modal and other non-classical logics. The guide includes an actual refutation trace with normalization, ordered paramodulation, and unification steps.

**Entry point:** [usage, proof traces, and embedding semantics](https://github.com/leoprover/Leo-III/blob/master/USAGE.md). Its internal timeout is documented as best effort, and bounded search failure is not a countermodel.

### 5. [GoelandProver/Goeland](https://github.com/GoelandProver/Goeland)

**Language / role:** Go; concurrent first-order tableau prover.

Study concurrency where branches cannot simply return independent Boolean answers: closing substitutions must agree, respect metavariable scope, and support backtracking.

- **C1:** [Child management](https://github.com/GoelandProver/Goeland/blob/master/src/Search/child_management.go) merges branch substitutions, removes metavariables unknown to a parent, updates proof state, and handles incompatible or exhausted branches. It contains explicit checks for impossible substitution states.
- **C3:** Concurrent search is organized around parent/child communication, selection of substitutions to try, and retained alternatives for backtracking. This provides an inspectable approach to parallel proof search rather than only a command-line parallelism flag.

**Entry points:** [branch coordination](https://github.com/GoelandProver/Goeland/blob/master/src/Search/child_management.go); [testing and error-management policy](https://github.com/GoelandProver/Goeland/blob/master/CONTRIBUTING.md). The latter requires unit tests, countertheorem checks, and regression problems for fixes. The README cautions that nondeterminism complicates debugging and that its proof-export implementation lags the cited deskolemization paper.

### 6. [01mf02/cop-rs](https://github.com/01mf02/cop-rs)

**Language / role:** Rust; connection-prover library and meanCoP reference prover, supporting clausal and nonclausal search.

This smaller codebase is valuable for studying the explicit state machinery that replaces Prolog's implicit substitution and backtracking behavior.

- **C1:** The library provides a substitution map that can be restored to earlier states and a `Rewind` abstraction for mutable data structures. Correct rollback is central to exploring alternative connections without leaking bindings between branches.
- **C2:** Separate `lean` and `nano` modules share formulas, terms, clauses, matrices, contraposition databases, and TPTP handling. The [author-maintained crate documentation](https://docs.rs/cop/latest/cop/) explicitly presents these as foundations for custom connection provers.
- **C3:** Offset terms/clauses, shared symbols, and restorable substitutions target repeated copying, equality checks, and backtracking costs; these are named data-structure choices in the API documentation.

**Entry point:** [cop API and module documentation](https://docs.rs/cop/latest/cop/). The inspected published documentation identifies version 0.2.0; no claim of ongoing release activity is made.

### 7. [gilith/metis](https://github.com/gilith/metis)

**Language / role:** Standard ML; first-order theorem prover with equality and a small logical kernel.

Study the separation between a search procedure and a compact theorem-construction interface. The [project site](https://www.gilith.com/metis/) identifies ordered paramodulation and documents integrations into Isabelle and HOL4.

- **C1:** The [kernel signature](https://www.gilith.com/software/metis/logical-kernel.txt) exposes an abstract theorem type and six primitive inference forms. Resolution requires complementary literals in the premises; equality replacement identifies a term occurrence by a path. These side conditions make the trust boundary tangible.
- **C2:** The same inference engine has been embedded in proof-assistant tactics and adapted as the core of MetiTarski. Its theorem abstraction provides a reusable basis for reconstruction rather than tying proof search to one user interface.

**Entry points:** [logical kernel](https://www.gilith.com/software/metis/logical-kernel.txt); [project documentation and integration references](https://www.gilith.com/metis/). The repository documents test builds for multiple SML implementations; this report does not infer a release cadence from that alone.

### 8. [gapt/gapt](https://github.com/gapt/gapt)

**Language / role:** Scala; proof-theory framework containing Escargot and other automated provers. Relevant subsystem: built-in proving and proof conversion, not merely external-prover wrappers.

Study search that produces structured proofs reusable by transformation algorithms. Escargot provides a particularly readable bridge between a saturation engine and sequent-calculus proofs.

- **C1:** [Escargot's implementation](https://github.com/gapt/gapt/blob/master/core/src/main/scala/gapt/provers/escargot/escargot.scala) chooses equality-sensitive inference rules, avoids existing names when creating symbols, and converts resolution results into atomic LK proofs.
- **C2:** Common contexts, clauses, term orderings, and proof representations serve native search, imported proofs, expansion proofs, and proof transformations.
- **C4:** [Release notes spanning 2016–2026](https://github.com/gapt/gapt/blob/master/RELEASE-NOTES.md) document prover-interface compatibility updates, removal of obsolete calculi, CI introduction, Scala migrations, and newer-JDK fixes. This is substantive evolution evidence beyond repository age.

**Entry points:** [Escargot setup and entry points](https://github.com/gapt/gapt/blob/master/core/src/main/scala/gapt/provers/escargot/escargot.scala); [release history](https://github.com/gapt/gapt/blob/master/RELEASE-NOTES.md). The monorepo is counted once.

## SMT and theory-specific automated reasoning

### 9. [Z3Prover/z3](https://github.com/Z3Prover/z3)

**Language / role:** C++ core with several language APIs; general SMT theorem prover.

Study how one system exposes a common expression and solver interface while hosting different engines for SMT, polynomial arithmetic, Horn clauses, and quantified reasoning.

- **C1:** The authors' [Programming Z3 tutorial, section 6](https://theory.stanford.edu/~nikolaj/programmingz3.html) explains consistency across theories, equality exchange, quantifier instantiation, and why a propositional assignment alone is insufficient.
- **C2:** Incremental solvers, assumptions, models, cores, tactics, and solver/tactic composition support many verification and symbolic-computation applications.
- **C3:** The tutorial explains learned conflict clauses and theory propagation during search, showing how pruning is integrated into the SAT/theory boundary. The [release notes](https://github.com/Z3Prover/z3/blob/master/RELEASE_NOTES.md) provide concrete further examples of memory, arithmetic, and rewriting changes alongside soundness fixes.

**Entry points:** [authors' implementation tutorial](https://theory.stanford.edu/~nikolaj/programmingz3.html); [release notes](https://github.com/Z3Prover/z3/blob/master/RELEASE_NOTES.md). The tutorial's overview diagram describes an older version; use current source for exact module boundaries.

### 10. [cvc5/cvc5](https://github.com/cvc5/cvc5)

**Language / role:** C++; extensible SMT engine and library with proof production.

Study proof infrastructure that must represent reasoning performed by numerous cooperating solver components while permitting deferred proof construction.

- **C1:** [ProofNode](https://github.com/cvc5/cvc5/blob/main/src/proof/proof_node.h) documents a partially mutable proof DAG whose proven conclusion must remain invariant. It distinguishes stored Skolem forms from witness forms used for checking, and records whether a conclusion was checked or trusted.
- **C2:** A shared proof-node representation contains rules, premises, arguments, and conclusions. The [proof-production documentation](https://github.com/cvc5/cvc5/blob/main/docs/proofs/proofs.rst) describes proof objects available through several APIs and conversion to CPC, Alethe, and visualization formats. This supports downstream checking and tooling across the solver's theories.

**Entry points:** [proof-node invariants](https://github.com/cvc5/cvc5/blob/main/src/proof/proof_node.h); [proof API and formats](https://github.com/cvc5/cvc5/blob/main/docs/proofs/proofs.rst). Proof production does not mean every configuration uses an independently checked external proof.

### 11. [SRI-CSL/yices2](https://github.com/SRI-CSL/yices2)

**Language / role:** C; SMT solver with native and SMT-LIB inputs and a library API.

Study explicit C interfaces for cooperation between Boolean search, congruence closure, and specialized theory solvers.

- **C1:** The [architecture document](https://github.com/SRI-CSL/yices2/blob/master/doc/smt_architecture.txt) states the obligations of conflict clauses and theory-propagation explanations. It also explains the dual representation of a term in the e-graph and a satellite theory and the consistency bookkeeping this requires.
- **C2:** Control, SMT, e-graph, and internalization interfaces separate backtracking, assertion, explanation, and term construction. Function-pointer records make the component contracts accessible without C++ inheritance.
- **C3:** Compact integer representations, lazy expansion of explanations, and dynamically generated theory lemmas address memory and search costs within that interface structure.

**Entry point:** [solver architecture](https://github.com/SRI-CSL/yices2/blob/master/doc/smt_architecture.txt). It is a design document for the SMT-core/e-graph architecture, not a claim to describe every newer solving mode exhaustively.

### 12. [OCamlPro/alt-ergo](https://github.com/OCamlPro/alt-ergo)

**Language / role:** OCaml; automated SMT reasoning oriented toward program-verification obligations.

Study how a functional-language solver exposes theory composition, quantified-fact selection, incremental assertions, and failures as explicit contracts.

- **C1:** The [solver signature](https://github.com/OCamlPro/alt-ergo/blob/next/src/lib/reasoners/sat_solver_sig.mli) explains guard-based `push`/`pop`, dependencies for unsatisfiable cores, and distinct reasons for unknown results, including incompleteness, memory exhaustion, step limits, and timeouts during different phases.
- **C2:** The `SatContainer.Make` functor accepts a `Theory.S` implementation and returns a common solver interface. This supports alternative reasoning components while preserving assumptions, models, objectives, and incremental-control operations.

**Entry points:** [solver interface](https://github.com/OCamlPro/alt-ergo/blob/next/src/lib/reasoners/sat_solver_sig.mli); [reasoner modules](https://github.com/OCamlPro/alt-ergo/tree/next/src/lib/reasoners). The inspected `next` source carries non-commercial licensing terms with a stated exception; check the intended version's license before reuse.

### 13. [usi-verification-and-security/opensmt](https://github.com/usi-verification-and-security/opensmt)

**Language / role:** C++; SMT solver with interpolation and library integration.

Study the top-level ownership and state model of an incremental solver. `MainSolver` connects logic, term mapping, theory handling, simplification, models, unsatisfiable cores, and interpolation.

- **C1:** [MainSolver.h](https://github.com/usi-verification-and-security/opensmt/blob/master/src/api/MainSolver.h) distinguishes current assertions from assertions already popped, requires a satisfiable state for model retrieval, and an unsatisfiable state for proofs and interpolation. Its assertion frames and status API expose correctness-sensitive lifecycle rules.
- **C2:** Constructors support supplied theory and solver components; separate result objects serve models, cores, and interpolation. This offers reusable machinery for clients that need more than a one-shot SAT/UNSAT answer.
- **C3:** Preprocessing skips assertion levels already simplified, preserving work across incremental queries rather than rebuilding the entire problem.

**Entry points:** [main solver API](https://github.com/usi-verification-and-security/opensmt/blob/master/src/api/MainSolver.h); [source subsystem layout](https://github.com/usi-verification-and-security/opensmt/tree/master/src).

### 14. [uuverifiers/princess](https://github.com/uuverifiers/princess)

**Language / role:** Scala; theorem prover for Presburger arithmetic with uninterpreted predicates and additional theory modules.

Study a prover whose API supports both satisfiability and validity workflows, generated constraints, and proof-derived interpolation. The repository explicitly supports arbitrary quantification over its core arithmetic/predicate language.

- **C1:** [SimpleAPI](https://github.com/uuverifiers/princess/blob/master/src/main/scala/ap/api/SimpleAPI.scala) checks status and certificate prerequisites before interpolation, distinguishes model-search and exhaustive-prover paths, and preserves/restores state around additional model-consistency queries.
- **C2:** The API provides theory and datatype construction, formula/term representations, scoped solver use, partial models, constraints on existential constants, and sequences of interpolants. These facilities support reusable verification components beyond command-line proving.

**Entry points:** [SimpleAPI implementation and contracts](https://github.com/uuverifiers/princess/blob/master/src/main/scala/ap/api/SimpleAPI.scala); [core source layout](https://github.com/uuverifiers/princess/tree/master/src/main/scala/ap). Debug validation is not an unconditional independent guarantee: the inspected interpolation assertion helper explicitly warns when its checking timeout prevents full verification.

### 15. [ultimate-pa/smtinterpol](https://github.com/ultimate-pa/smtinterpol)

**Language / role:** Java; SMT solver specializing in Craig interpolation.

Study the extra obligations introduced when a solver must explain inconsistency through formulas restricted to the appropriate shared vocabulary. Only SMTInterpol is counted here; Ultimate clients and embedded copies are not additional entries.

- **C1:** [InterpolantChecker](https://github.com/ultimate-pa/smtinterpol/blob/master/SMTInterpol/src/de/uni_freiburg/informatik/ultimate/smtinterpol/interpolate/InterpolantChecker.java) handles purification variables, auxiliary functions, partition membership, inductivity checks, and final symbol occurrence checks. These are substantive invariants beyond ordinary satisfiability.
- **C2:** A common `Script`/`Term` interface lets checking issue scoped queries, while theory-specific interpolation modules share the surrounding framework. The [official site](https://ultimate.informatik.uni-freiburg.de/smtinterpol/) documents supported theory combinations and their distinct quantifier/interpolation limitations.

**Entry points:** [interpolant checking implementation](https://github.com/ultimate-pa/smtinterpol/blob/master/SMTInterpol/src/de/uni_freiburg/informatik/ultimate/smtinterpol/interpolate/InterpolantChecker.java); [interpolation subsystem](https://github.com/ultimate-pa/smtinterpol/tree/master/SMTInterpol/src/de/uni_freiburg/informatik/ultimate/smtinterpol/interpolate). Do not assume every supported theory has identical interpolation support.

### 16. [bitwuzla/bitwuzla](https://github.com/bitwuzla/bitwuzla)

**Language / role:** C++; SMT solver for bit-vectors, floating-point arithmetic, arrays, uninterpreted functions, and combinations.

Study precise machine-value reasoning through a solver engine that keeps theory modules and incremental state explicit.

- **C1:** [SolverEngine](https://github.com/bitwuzla/bitwuzla/blob/main/src/solver/solver_engine.h) synchronizes backtracking scopes and records assertion levels for registered terms. Lemma terms must be encoded at their dependencies' levels; getting that wrong could retain or discard information across a `pop` incorrectly.
- **C2:** Bit-vector, floating-point, function, array, and quantifier solver objects communicate through shared nodes, solver state, lemma submission, and model-value requests.
- **C3:** Backtrackable registration and lemma caches avoid repeated work, while model-value caching and separate timing statistics make costs visible within the architecture.

**Entry points:** [solver engine interface](https://github.com/bitwuzla/bitwuzla/blob/main/src/solver/solver_engine.h); [solver modules](https://github.com/bitwuzla/bitwuzla/tree/main/src/solver). Its specialization complements general first-order ATPs rather than replacing their unrestricted search.

### 17. [dreal/dreal4](https://github.com/dreal/dreal4)

**Language / role:** C++ with Python bindings; automated reasoning over nonlinear real functions using δ-complete decision procedures.

Study numerical proof search through interval boxes, contractors, formula evaluators, and branching. This offers a different correctness challenge from symbolic equality saturation.

- **C1:** The [official semantics](https://dreal.github.io/) distinguishes exact `unsat` from `δ-sat`, which concerns a perturbed formula. The [sequential ICP loop](https://github.com/dreal/dreal4/blob/master/dreal/solver/icp_seq.cc) makes pruning, feasibility evaluation, precision, and branching decisions visible. A `δ-sat` answer must not be described as exact satisfiability of the original formula.
- **C3:** The loop first prunes boxes, discards infeasible ones, then branches only where needed. Configurable branching, alternating stack order, and separate pruning/evaluation/branching timers expose performance decisions within a compact implementation.

**Entry points:** [interval search loop](https://github.com/dreal/dreal4/blob/master/dreal/solver/icp_seq.cc); [δ-decision semantics](https://dreal.github.io/). The website includes older examples; this entry does not infer that every historical proof-checking command applies unchanged to dReal 4.

## Inductive and proof-assistant-integrated automation

### 18. [acl2/acl2](https://github.com/acl2/acl2)

**Language / role:** Common Lisp; automated inductive theorem-proving environment and community libraries.

Study automation driven by rewriting, simplification, generalization, and induction, with users steering difficult proofs through lemmas and hints. This entry concerns the prover and reusable books together, counted once.

- **C1:** [Theorem admission and rewrite-rule processing](https://github.com/acl2/acl2/blob/master/defthm.lisp) validate how proved statements become executable rewrite rules, rejecting problematic rule forms such as a term rewriting to itself. The [waterfall reference](https://www.cs.utexas.edu/~moore/acl2/v6-1/HINTS-AND-THE-WATERFALL.html) explains subtle goal, hint, and induction-state propagation.
- **C2:** The repository combines the theorem-proving system with the canonical Community Books collection. Lemmas, rule classes, and hints provide reusable automation over different formal models rather than requiring a new search engine for each application.

**Entry points:** [rule processing](https://github.com/acl2/acl2/blob/master/defthm.lisp); [waterfall architecture reference](https://www.cs.utexas.edu/~moore/acl2/v6-1/HINTS-AND-THE-WATERFALL.html). The latter is explicitly historical version 6.1 documentation. The current README identifies this as the development repository and `acl2-devel/acl2-devel` as the stable-release distribution fork; that fork is not counted separately.

### 19. [leanprover-community/aesop](https://github.com/leanprover-community/aesop)

**Language / role:** Lean; extensible automatic proof-search tactic for Lean 4.

Study an automated search engine that builds proof terms while allowing domain-specific rule sets. The repository documents its use for both general goals and specialized automation such as continuity and measurability.

- **C1:** [Search/Main.lean](https://github.com/leanprover-community/aesop/blob/master/Aesop/Search/Main.lean) checks that extracted proofs contain no unresolved expression metavariables. It distinguishes search limits from exhaustive failure and explains why safe-prefix expansion is necessary to keep failure output from depending on incidental search priorities.
- **C2:** Rules may be arbitrary tactics; normalization, safe rules, unsafe rules, and local/global rule sets provide reusable search machinery for different proof domains.
- **C3:** Best-first exploration, eager non-backtracked safe rules, rule indexing, and configurable goal/application limits address search explosion while preserving separate queue, tree, and proof-extraction layers.

**Entry point:** [search loop and proof finalization](https://github.com/leanprover-community/aesop/blob/master/Aesop/Search/Main.lean). The README distinguishes successful proof search from its less reliable optional tactic-script generation.

### 20. [leanprover-community/duper](https://github.com/leanprover-community/duper)

**Language / role:** Lean; automatic proof-producing theorem prover integrated into Lean 4.

Study the reconstruction boundary between a clause-based search and a dependent-type-theory proof term. This is a substantive prover implementation, not a wrapper around an external ATP.

- **C1:** [ProofReconstruction.lean](https://github.com/leanprover-community/duper/blob/main/Duper/ProofReconstruction.lean) tracks universe-level requests, instantiates parent clauses, reconstructs Skolem definitions, and updates local/metavariable contexts. These details are necessary to turn an abstract refutation into a correctly scoped Lean expression.
- **C3:** Reconstruction walks only ancestors of the empty clause, deduplicates collected clauses, and caches constructed clauses by identifier and universe levels. Shared derived facts and Skolem terms are reused rather than expanded repeatedly.

**Entry points:** [proof reconstruction](https://github.com/leanprover-community/duper/blob/main/Duper/ProofReconstruction.lean); [prover subsystem layout](https://github.com/leanprover-community/duper/tree/main/Duper). The README explicitly requires compatible Lean and Batteries versions, so integration should follow the selected revision's toolchain.

## Coverage and search notes

Discovery used more than six distinct live web-search formulations, including:

1. “automated theorem prover superposition saturation github E Vampire iProver”;
2. “higher order automated theorem prover github Leo III zipperposition Satallax”;
3. “SMT solver github cvc5 z3 veriT architecture”;
4. “automated theorem prover connection calculus tableau github leanCoP nanoCoP” and a focused “cop-rs” query;
5. “automated theorem prover Rust Haskell OCaml github”;
6. “automated theorem prover intuitionistic modal logic github Goeland”;
7. “equational theorem prover Twee Haskell” and focused Lash/Satallax and Connect++ searches;
8. searches for Princess/OpenSMT/Alt-Ergo/Yices, followed by induction, sequent-calculus, and ACL2 waterfall searches.

These searches covered saturation versus goal-directed search, classical versus higher-order/non-classical reasoning, exact symbolic versus numerical semantics, standalone engines versus embedded proof-producing tactics, and C/C++/OCaml/Scala/Go/Rust/SML/Lisp/Lean/Java implementations. Later searches increasingly returned the same engines, external-hosted systems, educational projects, and LLM orchestration wrappers. Repository pages were opened for all 20 retained entries; additional primary implementation or documentation material was opened and read for each. GitHub source retrieval was used when the web reader could not load a source page.

**Exclusions and limits:** [Twee's GitHub repository](https://github.com/nick8325/twee) explicitly reports its move to Codeberg and is archived; no maintained official GitHub mirror was established, so it is excluded despite its relevance. Other discovery candidates were not retained where canonical GitHub implementation evidence was insufficient. Pure SAT solvers, benchmark collections, general proof libraries, duplicate forks, and LLM-only proving wrappers were outside the chosen scope. The survey does not exhaust non-GitHub ATPs or certify contemporary performance rankings. GAPT's release history supports the explicit C4 assessment; C4 is not assigned to other entries merely because they are old or have extensive commit histories. Architecture and study-value assessments are reasoned inferences from the cited material, with no claim of a full code audit.
