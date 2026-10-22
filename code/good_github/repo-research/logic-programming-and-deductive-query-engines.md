# Logic programming and deductive query engines

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing logic languages, relational programming libraries, Datalog evaluation, answer-set and probabilistic logic, and deductive database subsystems. It emphasizes execution machinery: unification, constraint stores, tabling, fixed points, rule compilation, incremental maintenance, and query planning. Jena and Z3 are included only for their identified reasoning subsystems. These are engineering study recommendations, not claims that every component is exemplary or that every project is currently maintained.

Criteria used below:

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable mechanisms supporting multiple applications.
- **C3 — Performance and structure:** concrete performance constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or explicit complexity management. Repository age alone does not qualify.

The criterion judgments are grounded in the linked primary material. Performance discussions identify mechanisms, rather than treating benchmark claims as independently reproduced results. Repository headings link to verified canonical GitHub pages; the entry points are additional material opened during research.

## Prolog runtimes and compilers

### 1. [SWI-Prolog/swipl-devel](https://github.com/SWI-Prolog/swipl-devel)

**Language/role:** C and Prolog; general-purpose Prolog runtime, compiler, and libraries.

Study how a large Prolog implementation reconciles mutable predicates with memoized recursive evaluation. Its incremental tabling design connects answer tries and dynamic predicates through an incremental dependency graph; updates invalidate dependent tables, and later queries trigger ordered recomputation.

- **C1:** Correctness requires propagating invalidation through dependencies while preserving answers after assertions and retractions. The documented example distinguishes an invalidated table from one whose answers actually changed.
- **C3:** Reevaluation proceeds on demand and can stop propagating when a recomputed answer set is unchanged. This is a concrete strategy for avoiding unnecessary recursive work, with an explicitly documented table-level granularity limit.
- **C2:** Tabling is exposed through predicate declarations within the broader Prolog system, making the mechanism reusable across graph queries and other recursive programs.

**Entry point:** [Incremental tabling implementation and worked example](https://www.swi-prolog.org/pldoc/man?section=tabling-incremental).

### 2. [mthom/scryer-prolog](https://github.com/mthom/scryer-prolog)

**Language/role:** Rust and Prolog; Warren Abstract Machine implementation.

Scryer is useful for studying a WAM implemented in a higher-level systems language. Its repository describes first-argument indexing, last-call optimization, attributed variables, and ISO conformance work. The machine implementation separates code, indexes, heap/stack state, streams, loading, and unification.

- **C1:** Choice-point creation and cleanup must restore registers, trail positions, heap boundaries, and attributed-variable queues consistently. The machine source makes these coupled invariants visible, including allocation-failure paths and synthetic choice points used by embedded calls.
- **C2:** A reusable machine object and separate loading, indexing, and attribute-verification machinery support both ordinary execution and host integration.
- **C3:** Clause applicability scans and specialized indexing instructions show how avoiding failed alternatives interacts with execution state, rather than hiding optimization in an opaque interpreter loop.

**Entry points:** [Machine implementation](https://raw.githubusercontent.com/mthom/scryer-prolog/master/src/machine/mod.rs), [source organization](https://github.com/mthom/scryer-prolog/tree/master/src).

### 3. [trealla-prolog/trealla-prolog](https://github.com/trealla-prolog/trealla-prolog)

**Language/role:** C, with Prolog libraries; compact embeddable Prolog interpreter.

The older `trealla-prolog/trealla` repository URL redirects here. The README describes the project as feature-complete, with bug fixes and incremental improvements remaining; this is a maintenance-position statement from the project, not an assumption of rapid feature development.

- **C1:** The query implementation explicitly manages trails, choice points, frames, and variable slots. Allocation failures set query error state, while backtracking requires preserving the relationships between these structures. The repository also documents sanitizer-based testing.
- **C3:** Dynamic growth and memory-pressure reduction for interpreter structures expose the costs of a portable C runtime. This is a useful contrast with Scryer’s Rust WAM and implementations relying more heavily on host garbage collection.
- **C2:** The interpreter offers a C embedding API, foreign predicates, attributed variables, and constraint libraries rather than serving only as a command-line language.

**Entry point:** [Query execution and memory management source](https://raw.githubusercontent.com/trealla-prolog/trealla/main/src/query.c). This verified raw source remains served under the legacy repository name; it should not be interpreted as a second project or as a pinned snapshot of the renamed repository.

### 4. [didoudiaz/gprolog](https://github.com/didoudiaz/gprolog)

**Language/role:** C and Prolog; GNU Prolog native compiler and finite-domain constraint solver.

Study the separation between Prolog-to-WAM compilation, WAM-to-mini-assembly translation, target assembly generation, and the finite-domain runtime. The source tree exposes these as `Pl2Wam`, `Wam2Ma`, `Ma2Asm`, `EnginePl`, and `EngineFD`.

- **C1:** Release notes document substantive correctness problems and fixes: cut inside conditionals, integer overflow under optimization, rounding semantics, clause reclamation, and finite-domain propagation. These are useful concrete examples of language semantics crossing compiler and runtime boundaries.
- **C2:** Native compilation, interpreted execution, a bidirectional C interface, and user-definable constraints provide reusable execution and solver facilities.
- **C4:** The opened NEWS history spans releases from the 2000s through 2026 and records architecture ports, compatibility changes, regression fixes, and the addition of interpreted checks. This supports sustained evolution rather than merely longevity.

**Entry points:** [Compiler/runtime source layout](https://github.com/didoudiaz/gprolog/tree/master/src), [NEWS](https://raw.githubusercontent.com/didoudiaz/gprolog/master/NEWS).

### 5. [ciao-lang/ciao](https://github.com/ciao-lang/ciao)

**Language/role:** Prolog and C; extensible Prolog-family compiler, runtime, and standard libraries.

Ciao is a study in building language features around a small logic kernel. This repository contains the compiler, libraries, and build system; the separately maintained CiaoPP analysis system is not counted here.

- **C2:** Packages and modules let programs select language facilities, including higher-order constructs and constraint extensions. The changelog documents changes to the default module environment and explicit packages for dynamic predicates, higher-order calls, and other facilities.
- **C1:** The implementation history discusses variable-sharing semantics in predicate abstractions, cyclic terms, thread-safe exceptions, floating-point round trips, and missing garbage-collection roots. These provide specific correctness boundaries to investigate.
- **C4:** Releases documented for 2018, 2020, and 2024 include compatibility migrations, ISO behavior corrections, runtime checks, and regression-test improvements. The 1.25 entry is explicitly marked draft, so it is not treated as a completed release.

**Entry point:** [Detailed changelog, including compiler and engine changes](https://github.com/ciao-lang/ciao/blob/master/CHANGELOG.md).

### 6. [ichiban/prolog](https://github.com/ichiban/prolog)

**Language/role:** Go; embeddable ISO Prolog interpreter.

This is a particularly approachable comparison point for WAM-based systems. The architecture document describes a VM derived from ZIP, with adaptations for Go’s memory model and missing nondeterministic control facilities.

- **C1:** The interpreter must implement variable environments, continuations, and cut boundaries explicitly. Its architecture identifies an `env` register for bindings and `cutParent` for control scope, making the relevant correctness state inspectable.
- **C2:** The high-level API follows Go’s `database/sql` style, while custom predicates and custom terms expose reusable host-language integration points. An interpreter can be constructed without built-ins for controlled embedding.
- **C3:** Splitting head/body instructions permits slice-based execution; direct Go pointers replace the original VM’s constant table. These are concrete representation choices with a concise architectural explanation.

**Entry point:** [ARCHITECTURE.md](https://github.com/ichiban/prolog/blob/main/ARCHITECTURE.md).

## Reusable relational and higher-order logic languages

### 7. [LogtalkDotOrg/logtalk3](https://github.com/LogtalkDotOrg/logtalk3)

**Language/role:** Logtalk and Prolog; portable logic-language compiler and development environment.

Logtalk adds a substantial organization layer to Prolog: objects, protocols, reusable categories, and a compiler targeting different Prolog implementations. Study how language-level reuse and diagnostics are maintained across heterogeneous backends.

- **C2:** Protocols, categories, and object mechanisms are reusable abstractions for organizing large logic programs. The compiler exposes checks for unknown calls, predicate declarations, portability, variable aliasing around cuts, and other language-level hazards.
- **C4:** Release notes document years of backend adaptation and testing. For example, the 2021 entries add Unicode and permission-error tests and update Ciao, Scryer, and Trealla compatibility; later entries continue adapter and compiler corrections.
- **C1:** Compile-time checks distinguish undeclared calls, declared-but-undefined predicates, conflicting directives, and potential non-steadfastness. Their documented limits also make this useful material for studying conservative diagnostics.

**Entry points:** [Compilation and application manual](https://logtalk.org/manuals/userman/programming.html), [release notes](https://logtalk.org/releasenotes.html).

### 8. [LPCIC/elpi](https://github.com/LPCIC/elpi)

**Language/role:** OCaml; embeddable λProlog interpreter with Constraint Handling Rules.

Elpi adds a distinct family to the selection: logic programming over syntax containing binders and unification variables. It is especially relevant to language tooling and proof-assistant extensions.

- **C1:** Higher-order unification must respect the scope introduced by alternating universal and existential quantifiers and avoid variable capture. The authors’ implementation paper explains the interaction between variable representations, reduction, and delayed unification problems.
- **C2:** The public API separates setup, parsing, compilation, and execution and supports host-defined built-ins, quotations, and data representations. These are substantive embedding abstractions, not merely a subprocess wrapper.
- **C3:** The implementation paper studies how term representation and reduction choices affect the cost of unification and binder traversal. Read it as design evidence for the interpreter’s lineage, rather than as a benchmark of today’s default branch.

**Entry points:** [OCaml embedding API](https://raw.githubusercontent.com/LPCIC/elpi/master/src/API.mli), [authors’ implementation paper](https://cs.unibo.it/~sacerdot/PAPERS/elpi.pdf).

### 9. [clojure/core.logic](https://github.com/clojure/core.logic)

**Language/role:** Clojure and ClojureScript; miniKanren-derived relational and constraint programming library.

Study how persistent substitutions, variable metadata, domain constraints, and search protocols compose inside a host language. The implementation goes well beyond a minimal unification demonstration.

- **C1:** The substitution implementation follows variable roots, merges domains, tracks related variables, and queues constraints without repeatedly adding the same constraint. Binding a variable can trigger constraint execution, so substitution and constraint-store updates must agree.
- **C2:** Relational, finite-domain, and nominal programming share an extensible core. The repository explicitly describes extension beyond the supplied logic styles and also provides unification facilities that need not depend on the whole engine.

The source comments discuss difficult interactions between nominal programs and finite-domain constraints, including remaining redundant computation. That candor is useful when studying the limits of an abstraction, not just its successful examples.

**Entry point:** [Substitutions, constraint propagation, and search implementation](https://raw.githubusercontent.com/clojure/core.logic/master/src/main/clojure/clojure/core/logic.clj).

### 10. [webyrd/faster-miniKanren](https://github.com/webyrd/faster-miniKanren)

**Language/role:** Scheme and Racket; relational search with symbolic constraints.

This compact but substantive implementation supports equality, disequality, type constraints, and `absento`, with relational interpreters and synthesis examples. It is an evolution of the author’s earlier symbolic-constraint implementation, which is not counted separately.

- **C1:** The core implements occurs checks, substitution extension, and interleaving search streams. Its comments explicitly describe representation invariants separating a single answer from a suspended stream or multiple answers.
- **C3:** The project replaces association-list substitutions with persistent maps, using an immutable hash implementation on Racket and a bit-oriented trie on other Scheme systems. Constraint-heavy search is the motivation; the source makes suspension and unnecessary-search avoidance inspectable.
- **C2:** The search and constraint kernel supports reusable relational arithmetic, pattern matching, and interpreters rather than one hard-coded puzzle.

**Entry point:** [Core unification and search implementation](https://raw.githubusercontent.com/webyrd/faster-miniKanren/master/mk.scm). The repository README explains the representation choices; its numerical speedup claim is not reproduced here.

## Datalog compilers and fixed-point engines

### 11. [souffle-lang/souffle](https://github.com/souffle-lang/souffle)

**Language/role:** C++; Datalog compiler and interpreter for analysis workloads.

Soufflé is a strong choice for following declarative rules through an explicit compiler pipeline into parallel native code. The source tree separates the AST, AST-to-RAM translation, relational intermediate representation, interpreter, and C++ synthesizer.

- **C2:** Typed relations, records, algebraic data types, components, and foreign functors support many analyses without requiring engine modifications.
- **C3:** Native parallel synthesis, specialized relation structures, and index selection address large fact sets. The implementation documentation explains an additional concrete space/layout choice: relations store ordinal identifiers for symbols and records, with separate intern tables; ADTs are encoded through tagged records.
- **C1:** This representation introduces consistency obligations between relation values, symbol/record identity, and ADT tags. Those invariants are a useful implementation-study target, alongside language-level typing and recursion semantics.

**Entry points:** [Compiler source organization](https://github.com/souffle-lang/souffle/tree/master/src), [symbol, record, and ADT representation](https://souffle-lang.github.io/implementation).

### 12. [knowsys/nemo](https://github.com/knowsys/nemo)

**Language/role:** Rust; in-memory Datalog and existential-rule materialization engine.

Nemo connects deductive database evaluation with RDF-shaped data and existential rules. The authors’ system description provides unusually concrete storage and query-execution details.

- **C1:** Its language includes stratified negation and aggregation plus existential rules evaluated with the restricted chase. Fresh witnesses and negative dependencies make semantics more demanding than positive, function-free Datalog alone.
- **C3:** The engine combines semi-naive evaluation, sorted column storage, compression, dictionary-encoded variable-size values, and leapfrog trie joins. The paper also explains the boundary of that design: projection and resorting require row-oriented temporary tables.
- **C2:** The same reasoning machinery is exposed through command-line, Rust/Python, and WebAssembly interfaces and can return proof traces for derived facts.

**Entry point:** [Authors’ 2024 system description, especially System Overview](https://iccl.inf.tu-dresden.de/w/images/6/61/Ivliev-Datalog20-2024.pdf). Its benchmark results are historical, not independently verified current performance.

### 13. [vmware-archive/differential-datalog](https://github.com/vmware-archive/differential-datalog)

**Language/role:** Haskell compiler and Rust runtime; incremental Datalog over differential dataflow.

**Status:** GitHub marks the repository archived on July 13, 2026. Retained as a substantial historical implementation and design reference.

- **C1:** DDlog handles insertions, deletions, primary keys, and both set and multiset semantics. Its tutorial explains why deleting one of several contributing occurrences must not remove a still-supported value, and how signed multiplicities differ from ordinary set updates.
- **C2:** Typed rules compile into Rust libraries with host-language integration, separating declarative programs from update ingestion and application code.
- **C3:** Differential dataflow supplies incremental execution. The tutorial identifies a specific cost boundary: internal multisets require an additional `distinct` operation when set semantics are requested.

Study the generated-program boundary and the semantics of externally visible deltas, not just the surface rule syntax.

**Entry points:** [Tutorial, including compilation and multiset semantics](https://github.com/vmware-archive/differential-datalog/blob/master/doc/tutorial/tutorial.md), [language reference](https://github.com/vmware-archive/differential-datalog/blob/master/doc/language_reference/language_reference.md).

### 14. [s-arash/ascent](https://github.com/s-arash/ascent)

**Language/role:** Rust; Datalog-like language embedded through procedural macros.

Ascent is useful for studying a logic language that deliberately exposes host-language types and replaceable relation representations. Its lattice relations combine alternative values through joins rather than storing every alternative independently.

- **C2:** User-defined lattices and “Bring Your Own Data Structures” relation backends allow domain-specific reasoning and storage strategies without replacing the front-end language.
- **C3:** Parallel macros use Rayon, while custom relations can change the underlying algorithmic cost—for example, representing an appropriate transitive relation through union-find. The internal API separates index reading, writing, merging, and freezing.
- **C1:** Lattice combination must obey the intended order laws, and parallel relations impose `Send + Sync` requirements. These are explicit obligations at the boundary between generated execution and user-supplied types; the types alone are not a proof of semantic correctness.

**Entry points:** [Relation/index extension interfaces](https://docs.rs/ascent/latest/ascent/internal/index.html), [Lattice trait](https://docs.rs/ascent/latest/ascent/lattice/trait.Lattice.html).

### 15. [ekzhang/crepe](https://github.com/ekzhang/crepe)

**Language/role:** Rust; procedural-macro Datalog compiler.

Crepe offers a smaller compiler to read end to end. Its macro transforms typed relation declarations and rules into an ordinary Rust runtime with relation sets and generated indexes.

- **C1:** The compiler checks duplicate declarations, undefined relations, arities, input-relation misuse, and invalid output lifetimes. It builds relation dependencies and rejects negation within a recursive stratum, providing a concrete implementation of stratified-negation safety.
- **C3:** Generated code uses semi-naive updates and indexes determined by bound/free positions. The source includes an illustrative generated transitive-closure loop, making the transformation from rules to imperative execution understandable.
- **C2:** Rust functions, borrowed inputs, relation types, and generated initialization APIs make the compiler reusable inside ordinary programs.

**Entry point:** [Macro compiler, validation, index construction, and generated-loop explanation](https://raw.githubusercontent.com/ekzhang/crepe/master/src/lib.rs).

### 16. [rust-lang/datafrog](https://github.com/rust-lang/datafrog)

**Language/role:** Rust; embedded fixed-point evaluation library.

Datafrog deliberately leaves rule scheduling in the caller’s Rust code. This makes it a good study of the minimal reusable machinery beneath a Datalog compiler, rather than another standalone language.

- **C1:** The variable implementation documents a three-stage tuple lifecycle: pending, recent, and stable. Every inserted tuple must become recent and eventually stable. If duplicate elimination is disabled for performance, every derivation cycle must still contain a deduplicating variable to support termination.
- **C2:** Relations, variables, iteration contexts, joins, and extension/filter interfaces form a reusable toolkit over typed tuples.
- **C3:** Sorted vector-backed relations and the separation of fixed inputs from changing variables avoid repeating work. The join API explicitly explains why joining two unchanging relations inside the iteration is the wrong execution placement.

**Entry points:** [Library design and exported abstractions](https://raw.githubusercontent.com/rust-lang/datafrog/master/src/lib.rs), [variable lifecycle and operators](https://raw.githubusercontent.com/rust-lang/datafrog/master/src/variable.rs).

### 17. [egraphs-good/egglog](https://github.com/egraphs-good/egglog)

**Language/role:** Rust; Datalog-style fixed-point reasoning combined with equality saturation.

Egglog is relevant where ordinary tuple identity is insufficient: rules need to reason modulo an evolving equivalence relation while also propagating analysis results.

- **C1:** Canonicalization can make previously distinct function inputs equal, creating conflicting outputs. Rebuilding resolves these through merge operations, which can create further equalities and require more rebuilding. The authors’ paper explains this interdependence explicitly.
- **C2:** The combination of rules, functions with merge behavior, equality, and analysis values supports both program rewriting and composable deductive analyses.
- **C3:** The design combines incremental rule execution with congruence maintenance and extraction. It is useful to study how these mechanisms share one engine instead of building a separate ad hoc equality layer around a Datalog program.

**Entry points:** [Authors’ design and implementation paper](https://effect.systems/doc/pldi-2023-egglog/paper.pdf), [equality-saturation tutorial](https://egraphs-good.github.io/egglog-tutorial/01-basics.html). The paper describes the original architecture; the current repository has evolved further, including parallel execution support.

## Answer sets, probabilistic logic, and constrained Horn clauses

### 18. [potassco/clingo](https://github.com/potassco/clingo)

**Language/role:** C++ with C/Python interfaces; grounder and answer-set solver.

Clingo belongs to the broader logic-programming category through answer-set semantics, rather than ordinary least-fixed-point Datalog. Study its separation of grounding, solver control, external atoms, and repeated solving.

- **C1:** External-atom lifetimes and cleanup affect later grounding: cleanup may remove an atom, and a subsequent definition introduces a fresh atom. Asynchronous callbacks and interruption have documented thread-safety and GIL constraints, giving concrete examples of correctness at a solver API boundary.
- **C2:** The control interface permits applications to add program parts, ground selected instances, observe models, supply assumptions, and extend solving with propagators.
- **C3:** Multi-shot execution reuses a control instance across grounding/solving steps; cleanup incorporates solver information into the grounding domain. This connects API structure to managing repeated search costs.

**Entry points:** [Control implementation and detailed lifecycle documentation](https://raw.githubusercontent.com/potassco/clingo/master/libpyclingo/clingo/control.py), [versioned Python API](https://docs.potassco.org/clingo/python-api/5.8/clingo/).

### 19. [ML-KULeuven/problog](https://github.com/ML-KULeuven/problog)

**Language/role:** Python; probabilistic logic programming and inference toolbox.

ProbLog turns logic programs, queries, and evidence into weighted Boolean formulas. This makes it a useful bridge between deductive execution, grounding, and knowledge compilation.

- **C1:** Probability inference must preserve shared logical dependencies and evidence; simply adding probabilities of overlapping proofs would be wrong. The project’s formula-based reduction and explicit grounding boundary are the mechanisms to study for this obligation.
- **C2:** A generic grounding-engine interface separates program preparation, direct querying, and formula construction. Host-language predicates can be deterministic, nondeterministic, or mode-sensitive, and data can come from database-backed relations.
- **C3:** Reducing inference to weighted model counting permits alternative compiled representations and inference algorithms instead of enumerating possible worlds directly in every application.

**Entry points:** [Grounding engine and transformation interface](https://raw.githubusercontent.com/ML-KULeuven/problog/master/problog/engine.py), [foreign predicates and database integration](https://problog.readthedocs.io/en/latest/modeling_advanced.html).

### 20. [scallop-lang/scallop](https://github.com/scallop-lang/scallop)

**Language/role:** Rust with Python integration; Datalog-based probabilistic and differentiable reasoning.

Scallop is a study in parameterizing a deductive engine by the meaning of derived facts. Facts carry tags, and a provenance algebra determines how those tags propagate through rules.

- **C1:** The provenance documentation works through disjunction of uncertain facts and the resulting probability. The correctness problem is preserving the chosen logical/probabilistic interpretation through derivation, rather than treating tags as arbitrary numeric annotations.
- **C2:** The generalized provenance-semiring framework supports ordinary, probabilistic, and differentiable reasoning through a common rule language. Python/PyTorch integration connects that engine to learned inputs without requiring each application to implement its own logical evaluator.

Study the distinction between relation membership and the information attached to a derivation. Different provenance choices have different semantics; the entry is not a claim that every configuration gives exact probabilistic inference.

**Entry points:** [Tags and provenance semantics](https://www.scallop-lang.org/doc/probabilistic/provenance.html), [Scallop book and integration examples](https://www.scallop-lang.org/doc/).

### 21. [Z3Prover/z3](https://github.com/Z3Prover/z3)

**Language/role:** Primarily C++; **μZ fixed-point and constrained-Horn-clause subsystem** within the Z3 monorepo.

The relevant code is `src/muz`, not the entire SMT solver. Its organization separates shared rule infrastructure and transformations from relational Datalog, tabulation, bounded-model-checking, and SPACER-related engines.

- **C1:** The fixed-point guide distinguishes finite-domain Datalog with stratified negation from constrained Horn clauses used for symbolic model checking. Maintaining the intended semantics across these different problem classes and engine choices is the principal correctness study target.
- **C2:** Shared contexts, rule transformations, and exported fixed-point routines support multiple reasoning engines and applications through common infrastructure.
- **C3:** The [basic Datalog engine](https://microsoft.github.io/z3guide/docs/fixedpoints/basicdatalog/) uses finite relation tables, while the broader subsystem exposes alternative symbolic techniques. This is useful material for comparing when explicit relation materialization is appropriate and when a different representation is needed.

**Entry points:** [μZ source layout and subsystem description](https://github.com/Z3Prover/z3/tree/master/src/muz), [fixed-point guide](https://microsoft.github.io/z3guide/docs/fixedpoints/intro/).

## Deductive query engines inside databases and graph frameworks

### 22. [tonsky/datascript](https://github.com/tonsky/datascript)

**Language/role:** Clojure and ClojureScript; immutable database and Datalog query engine.

DataScript is useful for studying deductive queries over application-local immutable data, including browser applications. Its query implementation makes relation algebra and variable-binding checks visible in one navigable module.

- **C1:** Disjunction branches must expose compatible variables; `or-join` and `not-join` restrict the binding context, and unsafe negation raises insufficient-binding errors. These checks are necessary to preserve query meaning as clauses are composed.
- **C2:** Query contexts separate relations, sources, and rules; the same engine works with host-language tuples and database datoms. This is a reusable query abstraction rather than a fixed graph traversal API.
- **C3:** Hash joins, relation collapsing, a bounded query cache, and empty-relation short circuits expose concrete execution optimizations in otherwise ordinary host-language code.

**Entry point:** [Query algebra, joins, and clause resolution](https://raw.githubusercontent.com/tonsky/datascript/master/src/datascript/query.cljc).

### 23. [datalevin/datalevin](https://github.com/datalevin/datalevin)

**Language/role:** Clojure/Java with native storage integration; persistent Datalog database.

Although it shares DataScript-style APIs and lineage, Datalevin is retained for substantive independent storage and rule-engine evolution. Its current rule design includes semi-naive evaluation, magic-set rewriting, and specialized demand-driven graph evaluation.

- **C1:** The rule documentation distinguishes transitive from reflexive-transitive closure: a start node is returned only if a nonempty cycle reaches it. Optimizations also distinguish committed data from pending transaction overlays, where stored cardinalities may be insufficient to prove completion.
- **C3:** EAV/AVE access paths support both indexed probes and range/cardinality information. Specialized traversal can change from point probes to an adjacency representation as observed work grows; general rule shapes retain the semi-naive evaluator.
- **C2:** The database exposes Datalog, pull, and direct index APIs over the same fact storage.

**Entry points:** [Rule-engine design and optimization preconditions](https://github.com/datalevin/datalevin/blob/master/doc/rules.md), [index architecture](https://datalevin.org/docs/15-index-architecture).

### 24. [cozodb/cozo](https://github.com/cozodb/cozo)

**Language/role:** Rust; transactional database with a Datalog query engine.

Cozo is especially useful for understanding an intentionally explainable evaluation pipeline. Its repository separates language/environment wrappers, the query engine, and pluggable key-value storage backends.

- **C1:** Rules are normalized to disjunctive normal form before safety checking; an apparently bound variable can become unsafe after splitting a disjunction. Strongly connected components are checked for forbidden stratifying edges before recursive evaluation.
- **C2:** A storage trait decouples rule execution and transactions from several storage implementations, while wrappers expose the engine to host languages.
- **C3:** Magic-set rewriting limits irrelevant derivations; semi-naive evaluation drives recursion; early filters and key-prefix scans control join costs. The documentation explains both efficient and expensive access patterns and exposes execution through `::explain`.

**Entry point:** [Query execution, safety, stratification, and access-path behavior](https://docs.cozodb.org/en/latest/execution.html). The repository README supplies the complementary storage/query/wrapper architecture.

### 25. [apache/jena](https://github.com/apache/jena)

**Language/role:** Java; **generic rule reasoner and inference subsystem** within the Apache Jena framework.

The relevant subsystem is the generic rule engine, not SPARQL or RDF storage in general. It offers forward RETE evaluation, a backward tabled Datalog engine, and a hybrid configuration in which forward processing primes backward query answering.

- **C2:** `GenericRuleReasoner` presents these execution modes through one configurable abstraction, with extensible procedural built-ins and integration into inference models.
- **C3:** Forward evaluation handles incremental fact changes; backward evaluation can table selected goals and consult the underlying graph’s indexes. The hybrid architecture is a concrete tradeoff between precomputing consequences and deriving answers on demand.
- **C1:** Model changes, cached deductions, tabling, and rebinding must remain consistent. The documentation explicitly explains that changing underlying data outside the inference API requires rebinding and describes limitations of the supplied ontology reasoners.

**Entry point:** [Inference architecture, rule engines, and update semantics](https://jena.apache.org/documentation/inference/). The ontology rule sets are not claimed to implement complete OWL reasoning.

## Coverage, search process, and limitations

Discovery used 19 live search queries, followed by repository-page verification and targeted reading of source, manuals, papers, and change histories. Search formulations covered:

- Compiled Datalog and analysis engines, including “Datalog deductive query engines GitHub Souffle architecture.”
- ISO Prolog implementations, native compilers, and embeddable Go runtimes.
- Rust procedural macros, differential dataflow, incremental updates, and lattice-valued relations.
- miniKanren, symbolic constraints, Clojure relational programming, and Scheme search representations.
- Existential rules, RDF-compatible materialization, and columnar query execution.
- Answer-set solving, probabilistic logic, differentiable reasoning, and equality saturation.
- Datalog databases and storage/index architecture across Clojure and Rust communities.
- Higher-order λProlog, OCaml embedding, and additional Java/Erlang/Lua engine searches.

Later general embedded-engine and language-diversity searches mostly revisited these families or found smaller alternatives; Elpi was added because binder-aware higher-order unification contributed a distinct architecture. The result balances large runtimes with smaller substantive libraries such as Datafrog, Crepe, faster-miniKanren, and ichiban/prolog. It is not an exhaustive census, and coverage of Lua/Erlang implementations and older systems hosted primarily outside GitHub remains limited.

Tutorial-only interpreters, lists of projects, bindings without an independent engine, and generic databases without a demonstrated deductive subsystem were excluded. Differential dataflow is discussed as DDlog’s substrate rather than counted again as a logic engine. DataScript and Datalevin are retained separately because the inspected Datalevin material demonstrates substantial distinct execution and storage design. Broad monorepos are counted once.

All 25 canonical repository pages were opened, and each retained project has additional primary evidence beyond its repository README; at least one inspected source per entry contains implementation or architectural substance. Some GitHub file views and documentation URLs failed to load, so working raw sources or official manuals were used instead. Trealla’s source retrieval through its legacy raw URL is called out in its entry. Papers describe the architectures at publication time and do not certify every current implementation detail. No candidate code was run, no dependencies were installed, and no benchmark claims were independently reproduced. Only explicit project statements and opened history are used for maintenance or evolution claims; availability on GitHub is not treated as proof of active maintenance.
