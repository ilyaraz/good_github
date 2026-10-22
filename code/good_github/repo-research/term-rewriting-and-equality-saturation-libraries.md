# Term rewriting and equality saturation libraries

Research date: **2026-10-09**. This selection covers reusable e-graph and equality-saturation engines, term matchers with replacement machinery, and strategic rewriting libraries. It also includes two language systems whose reusable rewriting runtimes are especially instructive, and one explicitly identified word-rewriting specialization. It excludes ordinary text replacement tools, application-specific optimizers that merely consume these libraries, and general symbolic systems without a separately justified rewriting focus.

The 18 repositories below are study candidates, not a ranking or a claim that every component is exemplary. Criterion assignments are engineering judgments grounded in the linked implementation material. In particular, handling difficult semantics does not prove that an implementation or a user's rewrite rules are sound.

**Criteria legend**

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure modes.
- **C2 — Abstractions:** substantial reusable interfaces supporting multiple languages, analyses, or applications.
- **C3 — Performance and structure:** concrete measures against computational or memory costs within an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or management of accumulated complexity.

## E-graphs and equality saturation

### 1. [egraphs-good/egg](https://github.com/egraphs-good/egg)

**Rust — extensible e-graph library.** A strong starting point for studying how congruence closure, user analyses, rewrite scheduling, and extraction fit together. Its API separates the expression language from analysis data and from search/application machinery.

- **C1:** the [`EGraph` contract](https://docs.rs/egg/latest/egg/struct.EGraph.html) exposes the distinction between dirty and clean graphs: mutations invalidate reading assumptions, rebuilding restores them, and deserialization also requires rebuilding. This makes invariant restoration an explicit API obligation.
- **C2:** language, analysis, searcher, applier, cost-function, and scheduler interfaces permit domain-specific optimizers without replacing the graph engine; see the [API overview](https://docs.rs/egg/latest/egg/).
- **C4:** the [changelog](https://github.com/egraphs-good/egg/blob/main/CHANGELOG.md) documents releases from 2020 through 2025, including fixes for nonlinear matching and proof-size overflow, minimum-Rust-version changes, and removal of an explanation feature incompatible with analyses. This is evidence of complexity management, rather than age alone.

**Entry points:** the `EGraph` contract and changelog above; follow the API's source links into rebuilding and analysis propagation.

### 2. [egraphs-good/egglog](https://github.com/egraphs-good/egglog)

**Rust — equality saturation integrated with Datalog.** Study the alternative architecture in which rules, relational data, and equality reasoning share an execution engine. The repository contains the core engine and supporting relation, union-find, and concurrency components; these count as one project.

- **C1:** the [Rust API](https://egraphs-good.github.io/egglog/docs/egglog/) distinguishes pure, read, write, and full primitive contexts. In particular, write-context primitive bodies cannot depend on live database reads; capability-specific wrappers and typechecking constrain extensions that could violate incremental execution assumptions.
- **C2:** custom sorts, primitives, analyses expressed through rules, and user-defined commands provide extension points beyond a fixed expression simplifier.
- **C3:** the [repository documentation](https://github.com/egraphs-good/egglog) describes scoped thread pools per e-graph and benchmark comparisons in CI. It also explicitly says parallel support is relatively new and its CodSpeed measurements are single-threaded, an important limit on performance evidence.

**Entry points:** the Rust API above and the repository's `core-relations`, `union-find`, and `concurrency` component map.

### 3. [memoryleak47/slotted-egraphs](https://github.com/memoryleak47/slotted-egraphs)

**Rust — e-graphs for terms with variables and binders.** Particularly useful when ordinary first-order e-graphs force awkward encodings of lambda terms or quantified expressions. This is a specialized implementation, not simply a renamed copy of egg.

- **C1:** an [`AppliedId`](https://docs.rs/slotted-egraphs/latest/slotted_egraphs/struct.AppliedId.html) combines an e-class identifier with a slot mapping: referring to a class requires specifying how its parameters are instantiated. The [`Language` contract](https://docs.rs/slotted-egraphs/latest/slotted_egraphs/trait.Language.html) separately enumerates public and private slots, including the distinction between a variable occurrence and a lambda binder. Binding and renaming are therefore structural correctness concerns.
- **C2:** the [crate API](https://docs.rs/slotted-egraphs/latest/slotted_egraphs/) exposes language definitions, analyses, custom rewrite construction, extraction costs, and interchangeable substitution methods. Engineers can study how a richer term model propagates through an otherwise reusable saturation interface.

**Entry points:** `AppliedId` and `Language` documentation above. Treat this as research infrastructure; no long-term compatibility claim is inferred from its published crate version.

### 4. [jonathanvdc/foresight](https://github.com/jonathanvdc/foresight)

**Scala — customizable, parallel equality saturation.** Offers an unusually direct comparison between immutable and mutable graph designs under a common interface, with slotted terms and composable saturation strategies.

- **C1:** the architecture separates work over a graph snapshot from deferred updates, rather than allowing arbitrary concurrent mutation. Binding-aware metadata additionally has to remain consistent under class merges and slot renaming.
- **C2:** strategies compose iteration limits, timeouts, repeated saturation, analyses, and rebasing. Metadata and concurrency backends are explicit extension interfaces, described in the [repository guide](https://github.com/jonathanvdc/foresight).
- **C3:** the authors' [design paper](https://jonathanvdc.github.io/files/2026-cc-foresight.pdf) explains parallel matching, command generation and simplification, and deferred update application. This is concrete architectural evidence for addressing scalability; no cross-engine speedup is generalized here from the paper's workloads.

**Entry points:** the design paper and [implementation/test subtree](https://github.com/jonathanvdc/foresight/tree/main/foresight/src). The hosted Scaladoc endpoint could not be retrieved during this research; the paper supplied the additional architectural evidence.

### 5. [alt-romes/hegg](https://github.com/alt-romes/hegg)

**Haskell — generic equality saturation with algebraic expression languages.** Study how a base functor, its fixed point, type classes, and graph state express the same extension problems that other engines solve with mutable objects or Rust traits.

- **C1:** [`Data.Equality.Analysis`](https://github.com/alt-romes/hegg/blob/master/src/Data/Equality/Analysis.hs) specifies semilattice-based analysis data and an idempotence requirement for `modifyA`. Its paired-analysis instance explicitly discusses when two modifications commute and warns that arbitrary analyses cannot safely be composed. This is a particularly useful account of the limits of a reusable abstraction.
- **C2:** the [saturation API](https://hackage-content.haskell.org/package/hegg-0.6.0.0/docs/Data-Equality-Saturation.html) is parameterized over language, analysis, scheduler, and ordered cost type. Conditional rewrites inspect substitutions and graph information, while callers can use either a complete saturation/extraction operation or graph-level operations.

**Entry points:** the analysis implementation and saturation API above. The criterion assessment does not assume that the tutorial's arithmetic identities apply to every numerical interpretation.

### 6. [verse-lab/ego](https://github.com/verse-lab/ego)

**OCaml — equality saturation using modules and functors.** A compact alternative for studying how the module system can encode graph permissions and separate expression structure from recursive children.

- **C1:** the [analysis walkthrough](https://verse-lab.org/ego/ego/index.html) distinguishes `rw` and `ro` graph interfaces. Analysis construction receives read-only access where mutation would violate graph assumptions, while modification receives write access. This is a concrete design for controlling extension-induced invariant violations.
- **C2:** `Basic` supplies an S-expression interface; `Generic` parameterizes the engine over a language, analysis data, and analysis operations. A separate extractor functor accepts a cost module, and generic rules support conditions and dynamically generated patterns.

**Entry point:** the official [walkthrough and linked API](https://verse-lab.org/ego/ego/index.html), especially `LANGUAGE`, `GRAPH_API`, `ANALYSIS_OPS`, and `MakeExtractor`. The documentation's GitHub Pages address redirects to the lab's domain; the GitHub repository itself remains available. No sustained-maintenance claim is made.

### 7. [JuliaSymbolics/Metatheory.jl](https://github.com/JuliaSymbolics/Metatheory.jl)

**Julia — classical rewriting and equality saturation behind a shared rule language.** Useful for studying how host-language macros and multiple dispatch can support both ordinary tree rewriting and e-graph execution over user expression types.

- **C1:** [`egraph.jl`](https://github.com/JuliaSymbolics/Metatheory.jl/blob/master/src/EGraphs/egraph.jl) explicitly restores invariants through a dirty-class worklist, canonicalizes and deduplicates parents, and requeues parents when their analysis data changes. Analysis maintenance is interleaved with graph repair.
- **C2:** the [architecture document](https://github.com/JuliaSymbolics/Metatheory.jl/blob/master/ARCHITECTURE.md) separates shared patterns and rule types from classical matching, e-graph saturation, analyses, and schedulers. The repository describes interoperability through `TermInterface.jl`, rather than requiring every client to adopt one AST representation.

**Entry points:** the architecture document and e-graph implementation above. **Version caveat:** the README directs users to the in-development `ale/3.0` branch; these implementation entry points document the `master` layout. Do not assume those branch APIs or performance characteristics are interchangeable.

### 8. [riswords/quiche](https://github.com/riswords/quiche)

**Python — independent e-graph implementation with tree adapters.** Worth studying when readable control flow is more important than a highly optimized systems-language implementation. Its repository includes arithmetic, propositional, and Python-AST-oriented examples/tests.

- **C1:** [`egraph.py`](https://raw.githubusercontent.com/riswords/quiche/main/src/quiche/egraph.py) states the analysis least-upper-bound and modification fixed-point invariants. It implements parent-use tracking, union/find, a repair worklist, and propagation of analysis changes; rewrite application explicitly requires a subsequent rebuild.
- **C2:** [`QuicheTree`](https://github.com/riswords/quiche/blob/main/src/quiche/quiche_tree.py) abstracts node values, children, and pattern symbols, while searchers, rewriters, and analyses have separate interfaces in the engine. This supports multiple term representations rather than a single arithmetic grammar.

**Entry points:** the two implementation files above. Documentation is limited, and the README states Python 3.7–3.10 support; compatibility with newer Python releases was not established. This is a research implementation, not an inferred production-performance recommendation.

## Pattern matching and strategic term rewriting

### 9. [JuliaSymbolics/SymbolicUtils.jl](https://github.com/JuliaSymbolics/SymbolicUtils.jl)

**Julia — typed symbolic expressions, rewrite rules, and composable simplification.** Study the boundary between mathematical expression representation and a reusable transformation language, including the effects of automatic canonicalization on matching.

- **C1:** the [rewriting manual](https://docs.sciml.ai/SymbolicUtils/stable/manual/rewrite/) specifies equality requirements for repeated variables, predicates on individual and sequence captures, associative-commutative matching, and explicit failure via `nothing`. It also demonstrates that expressions may simplify before a user rule sees them; matching syntax cannot be reasoned about independently of representation semantics.
- **C2:** callable rules compose into chains, traversals, and fixed-point transformations. The [interfacing guide](https://docs.sciml.ai/SymbolicUtils/stable/manual/interface/) explains the expression protocol for using rewriting with other types, making the package useful below a complete computer-algebra system.

**Entry points:** the rewriting and interfacing guides. The selection concerns its rewriting infrastructure, not a blanket endorsement of every algebraic simplification for floating-point or domain-restricted values.

### 10. [HPAC/matchpy](https://github.com/HPAC/matchpy)

**Python — symbolic matching and many-rule replacement.** Especially instructive for the difficult case where operators are associative or commutative and patterns include sequence variables. It contains replacement machinery as well as matching, which establishes its fit here.

- **C1:** [`many_to_one.py`](https://github.com/HPAC/matchpy/blob/master/matchpy/matching/many_to_one.py) combines substitutions, constraints, associative matching, and commutative operand assignment. Its commutative matcher uses a bipartite graph and matching enumeration rather than treating operands as a simple ordered list.
- **C2:** patterns, expression operations, constraints, and replacement callbacks are reusable abstractions; `ManyToOneReplacer` accepts rules independently of a particular algebra.
- **C3:** the same implementation builds shared matching states for a set of patterns and maintains caches for commutative subjects. The [repository explanation](https://github.com/HPAC/matchpy) connects many-to-one matching to reuse of similarities among patterns, giving a clear reason for this architecture.

**Entry point:** the matching/replacement implementation above. No maintenance or comparative benchmark claim is inferred from repository popularity.

### 11. [inkytonik/kiama](https://github.com/inkytonik/kiama)

**Scala — language-processing library; relevant subsystem: strategic rewriting.** Study generic transformations over ordinary Scala data together with explicit success/failure and tree-shape policies.

- **C1:** [`Rewriter.scala`](https://github.com/inkytonik/kiama/blob/master/core/src/main/scala/org/bitbucket/inkytonik/kiama/rewriting/Rewriter.scala) distinguishes strategy failure from successful replacement. Its `rewriteTree` defaults to `EnsureTree`, explicitly addressing node sharing introduced by rewriting; this matters to clients that expect a tree rather than a shared graph.
- **C2:** rules, generic traversal, iteration, and choice are reusable strategies, described in the [rewriting guide](https://inkytonik.github.io/kiama/Rewriting). The wider library's parsers and attribution facilities are supporting context, not separate entries.
- **C4:** the [release documentation](https://inkytonik.github.io/kiama/Releases) records years of releases alongside tested Scala versions and ScalaCheck/ScalaTest dependencies.

**Entry points:** `Rewriter.scala` and release documentation. **Status:** the maintainer explicitly says active development has stopped and support time is limited. The overview rewriting guide describes 1.x and warns that 2.x differs; consult release-specific APIs.

### 12. [microsoft/Trieste](https://github.com/microsoft/Trieste)

**C++20 — header-only term rewriting for language construction.** A useful complement to mathematical term libraries: it connects AST parsing, rewrite passes, and well-formedness specifications in one framework.

- **C1:** the [project description](https://github.com/microsoft/Trieste) explains how well-formedness definitions check pass results and generate test inputs for fuzzing. In [`rewrite.h`](https://github.com/microsoft/Trieste/blob/main/include/trieste/rewrite.h), alternatives restore capture frames when backtracking, and negated patterns reject captures. Both are concrete correctness boundaries in the matcher.
- **C2:** its parsing, rewriting, and well-formedness DSLs serve different compiler phases, allowing a frontend to simplify, elaborate, or lower ASTs using the same node and pass infrastructure.

**Entry point:** `include/trieste/rewrite.h`, especially choice, optional, and negated patterns. The repository's sample languages provide context for the public driver interface. Inclusion concerns the reusable rewriting machinery, rather than treating every sample compiler as an independent project.

### 13. [noprompt/meander](https://github.com/noprompt/meander)

**Clojure/ClojureScript — declarative data transformation and strategic rewriting.** Useful for studying rewriting over heterogeneous host-language maps, sets, lists, and vectors instead of a dedicated algebraic expression class.

- **C1:** the [matching guide](https://github.com/noprompt/meander/blob/epsilon/doc/understanding.md) distinguishes first-result matching from multi-result search and substitution, including logic and memory variables. These semantics matter when patterns admit multiple decompositions. The [strategy guide](https://github.com/noprompt/meander/blob/epsilon/doc/strategies.md) makes failure a dedicated value and defines deterministic choice, short-circuiting composition, and traversal behavior around it.
- **C2:** pattern matching, substitution, syntax extensions, and strategy combinators can be combined without embedding traversal order into each rule. The same machinery supports nested data reshaping and symbolic normalization.

**Entry points:** the two guides above, both on the verified `epsilon` branch. Termination remains a property of the chosen rules and strategy; the strategy documentation explicitly discusses that responsibility.

### 14. [mschuene/stratege](https://github.com/mschuene/stratege)

**Clojure — historical strategic rewriting library using zippers and continuations.** A smaller but substantive implementation with a distinctive answer to deep traversal and access to surrounding term context.

- **C1:** [`core.clj`](https://github.com/mschuene/stratege/blob/master/src/stratege/core.clj) carries a binding map and zipper location through strategy execution; it runs continuation-based strategies through `trampoline`. The failure and scope combinators show how state and bindings are controlled across alternative paths.
- **C2:** zipper operations are configurable, and rules remain separate from composable top-down, bottom-up, innermost, and context-sensitive strategies.
- **C3:** [`cps.clj`](https://github.com/mschuene/stratege/blob/master/src/stratege/cps.clj) implements thunk-based continuation helpers to avoid consuming the call stack during strategy execution. The README also explains compiling a rule group into a shared `core.match` operation.

**Entry points:** `core.clj` and `cps.clj`. **Historical status:** the retrieved [default-branch commit feed](https://github.com/mschuene/stratege/commits/master.atom) ends in November 2016. Retained for its implementation choices; current ecosystem compatibility was not verified.

### 15. [joshrule/term-rewriting-rs](https://github.com/joshrule/term-rewriting-rs)

**Rust — first-order term-rewriting systems, including parsing and rewrite traces.** A useful alternative to equality saturation when the object of study is a rewrite system itself: terms, signatures, rules, substitutions, and alternative reductions.

- **C1:** the [`Rule` API](https://docs.rs/term_rewriting/latest/term_rewriting/struct.Rule.html) distinguishes matching, unification, and alpha-equivalence and documents variable freshness across separate parsing calls. Its examples explicitly check substitutions and failures, exposing easy-to-miss identity semantics rather than treating printed variable names as global identifiers.
- **C2:** the [crate API](https://docs.rs/term_rewriting/latest/term_rewriting/) models signatures, contexts with holes, rules with multiple right-hand sides, signature-merging strategies, and traces. These are reusable components for constructing and inspecting arbitrary first-order systems.

**Entry points:** the `Rule` documentation and crate module map above. The repository explicitly excludes lambda binding in rules; binding-aware equality saturation belongs with the slotted implementations instead.

## Completion and reusable language runtimes

### 16. [kalmarek/KnuthBendix.jl](https://github.com/kalmarek/KnuthBendix.jl)

**Julia — specialized word rewriting and Knuth–Bendix completion for groups and monoids.** This is the selection's word-rewriting specialization, not a general tree-pattern engine. It adds an important architecture family: constructing confluent rewrite systems and accelerating normalization with automata.

- **C1:** the [rewriting-system documentation](https://kalmarek.github.io/KnuthBendix.jl/dev/rewriting_system/) distinguishes reducedness from confluence. It explains that confluence checks expect a reduced system and describes critical-pair discovery using an index automaton and backtracking. A negative result from the convenience API must therefore be interpreted with its preconditions in mind.
- **C2:** words, alphabets, orderings, rules, and alternative rewriting implementations have explicit interfaces.
- **C3:** the [rewriting internals](https://kalmarek.github.io/KnuthBendix.jl/dev/rewriting/) explain two-buffer rewriting, reuse of allocated buffers during completion, and index/prefix automata that avoid repeatedly scanning all rule left-hand sides.

**Entry points:** the rewriting-system and rewriting-internals guides. No claim is made that arbitrary completion problems terminate.

### 17. [metaborg/strategoxt](https://github.com/metaborg/strategoxt)

**Stratego, Java, and C — strategic program-transformation language and runtime libraries.** Included for the reusable Stratego standard library and compiler infrastructure within this monorepo. It is a historical foundation for the strategy combinators seen in several smaller libraries above.

- **C2:** the [repository description](https://github.com/metaborg/strategoxt) separates conditional rewrite rules from control strategies and describes generic traversal, substitution, unification, and variable-renaming facilities. [`strategy/iteration.str`](https://github.com/metaborg/strategoxt/blob/master/strategoxt/stratego-libraries/lib/spec/strategy/iteration.str) shows iteration built compositionally from sequencing, choice, and failure.
- **C3:** the historical [release notes](https://github.com/metaborg/strategoxt/blob/master/NEWS) explain compiler passes including match/build fusion, innermost fusion, inlining, and variable analyses. They explicitly discuss the tradeoff between compilation cost and generated-program optimization, rather than asserting unqualified speed.

**Entry points:** the iteration module and [standard-library subtree](https://github.com/metaborg/strategoxt/tree/master/strategoxt/stratego-libraries/lib). **Historical scope:** the top-level README and NEWS contain legacy compiler/distribution descriptions; this entry does not claim they describe the current preferred Spoofax development workflow.

### 18. [maude-lang/Maude](https://github.com/maude-lang/Maude)

**C++ — equational and rewriting-logic engine.** This is a language-system implementation rather than a small drop-in library. It is retained for its reusable matching, rewriting, theory, and reflective runtime architecture; the relevant subsystem is the interpreter core, not merely a collection of Maude models.

- **C1:** [`ruleTable.cc`](https://github.com/maude-lang/Maude/blob/master/src/Core/ruleTable.cc) requires known sorts, invokes compiled left-hand-side matchers, solves deferred subproblems, checks conditions, and handles partial matches before constructing replacements. Correctness spans more than syntactic substitution.
- **C2:** the repository describes reflective manipulation and module composition; the source separates general rewriting machinery from specialized equational theories. These interfaces support executable semantics and multiple classes of symbolic systems.
- **C4:** [`NEWS`](https://github.com/maude-lang/Maude/blob/master/NEWS) records multi-year work on narrowing, module-instantiation correctness, platform builds, and memory-corruption fixes, through a 2026 development entry. This supports an evolution claim without treating every development entry as a stable release.

**Entry points:** `src/Core/ruleTable.cc` and `NEWS`.

## Coverage, exclusions, and limitations

Discovery used more than six meaningfully distinct live-search formulations: general equality-saturation engines; strategic rewriting and traversal combinators; Python symbolic matching; Julia rewriting and completion; OCaml/Haskell/Scala e-graphs; Rust first-order rewrite systems; Java/C++ rewriting runtimes; and follow-up searches for Go, C#, JavaScript/TypeScript, and C++ e-graph implementations. Searches also followed binding-aware and parallel-evaluation work. Later language-specific searches increasingly returned already identified engines, application-specific consumers, lightweight prototypes, or generic term-storage infrastructure rather than stronger distinct candidates.

The selection spans shared mutable e-graphs, immutable/deferred-update designs, relational equality reasoning, binder-aware graphs, many-to-one associative-commutative matching, zipper/CPS traversal, automaton-based word rewriting, and reflective rewriting runtimes. Smaller projects such as Ego, hegg, Quiche, and Stratege are included for specific implementation substance, not to match a quota.

Important exclusions were generic ATerm storage by itself, ordinary regex/text replacement, tutorial-sized e-graph implementations, awesome lists, and unchanged forks of egg. General computer-algebra applications and optimizer consumers were not included merely because they use rewriting. Searches for Tom and TermWare did not establish an appropriate canonical GitHub implementation with enough additional primary evidence, so no owner/repository paths were guessed. Bindings alone were not counted as separate engines; this is not a judgment that every binding project lacks substantive engineering.

Every retained GitHub repository page was opened, and each entry has additional primary implementation or documentation evidence beyond its README. Some browser retrievals failed or returned cache misses; public raw source and official documentation were read directly where needed. No candidate code was executed, no dependencies were installed, and no benchmarks were reproduced. C3 therefore evaluates documented mechanisms, not independently measured rankings. C4 is assigned only where release/compatibility history supports it. Maintenance is not inferred from stars, a visible repository, or a recent crawl; explicit historical and version limitations are identified above.

Final checks: **18 unique repository entries**, each with at least two justified criteria; no forks counted twice; no placeholders. Branch-based links are navigational entry points and may change after the research date.
