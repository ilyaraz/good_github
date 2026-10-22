# Interactive theorem provers and proof kernels

Research date: 2026-10-09.

This selection covers 25 GitHub repositories implementing interactive proof assistants, logical frameworks, reusable proof kernels, and checkers for their proof artifacts. It includes large prover environments, compact kernels, experimental type theories, and verification of the provers themselves. Mathematical libraries, editor integrations, and automated proof-search wrappers are not counted as prover implementations. CakeML is included specifically for its Candle subsystem and counts once.

The emphasis is on code an experienced engineer can study: representation invariants, trust boundaries, binding and substitution, proof-state management, extensibility, and scalable checking. Criterion assessments are grounded engineering judgments from the linked primary sources, not certifications of soundness or endorsements of every component. No candidate was built or benchmarked. Maintenance activity is not inferred from stars, creation dates, or the mere availability of a repository.

**Criteria legend**

- **C1 — Difficult correctness:** nontrivial invariants, logical or numerical semantics, concurrency, malformed input, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or representations that support multiple theories, developments, tools, or applications.
- **C3 — Performance with structure:** concrete scaling constraints addressed through understandable algorithms or architecture.
- **C4 — Sustained evolution:** evidence across years accompanied by compatibility work, testing, or deliberate complexity management.

## Dependent types and cubical proof assistants

### 1. [leanprover/lean4](https://github.com/leanprover/lean4)

**Language / role:** Lean and C++; integrated programming language and interactive theorem prover, with a C++ kernel.

Study how a rich elaboration environment terminates in a comparatively explicit checking interface. The kernel's distinction between inference-only operations and checking is particularly useful for understanding the preconditions behind apparently harmless optimizations.

- **C1:** The [kernel type checker](https://github.com/leanprover/lean4/blob/master/src/kernel/type_checker.cpp) checks universe parameters, rejects metavariables and loose bound variables, validates projection structure and indices, and extends local contexts only after checking their contents. Its comments explain soundness-sensitive interactions between normalized universe levels and elimination from propositions.
- **C3:** The same implementation separates weak-head reduction, unfolding, inference, and definitional equality; it caches intermediate results and includes recursion/interruption checks and bounds on evaluated numerals. These are concrete responses to large terms and expensive conversion, without requiring a throughput claim.

### 2. [rocq-prover/rocq](https://github.com/rocq-prover/rocq)

**Language / role:** Primarily OCaml; the Rocq prover, from the Coq lineage.

A useful study in maintaining a common term representation across a large proof environment while keeping the rules for accepting terms explicit. The separation between representation and typing makes this a strong comparison with Lean's implementation.

- **C1:** [Kernel typing operations](https://github.com/rocq-prover/rocq/blob/master/kernel/typeops.ml) check universe constraints, relevance annotations, canonical constant identities, and dependent applications. Context instantiation must simultaneously preserve substitutions, binder relevance, and parameter counts.
- **C2:** [The kernel term interface](https://github.com/rocq-prover/rocq/blob/master/kernel/constr.mli) provides abstract terms, constructors, traversal/manipulation operations, universe-instantiated constants, inductives, and machine primitives. Its documented case-expression invariants are useful examples of sharing a rich representation without leaving its assumptions implicit.

### 3. [agda/agda](https://github.com/agda/agda)

**Language / role:** Haskell; dependently typed programming language and interactive proof assistant.

Study the engineering consequences of supporting several related type theories in one implementation. Agda is especially instructive for understanding why feature combinations and transitive module settings belong in a proof assistant's correctness model.

- **C1:** The [Safe Agda specification](https://agda.readthedocs.io/en/latest/language/safe-agda.html) documents restrictions on postulates, incomplete matches, termination and positivity bypasses, universe options, and combinations known to cause inconsistency. Safety propagates through imports; it is not just a local parser switch.
- **C2:** The [cubical implementation documentation](https://agda.readthedocs.io/en/latest/language/cubical.html) explains reusable primitives for paths, partial elements, transport, composition, and higher inductive types. The decomposition of composition into homogeneous composition and generalized transport is a substantive implementation choice supporting many formal developments.

### 4. [JetBrains/Arend](https://github.com/JetBrains/Arend)

**Language / role:** Java, with Kotlin build configuration; proof assistant based on homotopy type theory.

A valuable JVM example for engineers interested in embeddable typechecking and extension APIs. Read the project layout alongside the core-expression checker to see how language tooling and logical checks are organized.

- **C1:** [CoreExpressionChecker](https://github.com/JetBrains/Arend/blob/master/base/src/main/java/org/arend/typechecking/doubleChecker/CoreExpressionChecker.java) checks dependent argument substitutions, universe levels, expected versus actual types, and representation conditions such as boxed property arguments. It makes several conditions on already elaborated expressions concrete.
- **C2:** The [architecture document](https://github.com/JetBrains/Arend/blob/master/ARCHITECTURE.md) separates the extension API, typechecker, generated parser, serialization classes, and CLI. The parser-generator dependency is deliberately isolated from consumers that need only generated parsing code; JUnit tests exercise the assembled frontend.

### 5. [RedPRL/cooltt](https://github.com/RedPRL/cooltt)

**Language / role:** OCaml; experimental Cartesian cubical proof assistant and normalization-by-evaluation implementation.

The [project's own description](https://redprl.org/) explicitly calls cooltt a prototype. It is retained for its substantial cubical implementation, not treated as a production-stability reference. Its ancestry in blott and reuse of redtt code are disclosed by the repository; those predecessors are not separately counted here.

- **C1:** [Conversion.ml](https://github.com/RedPRL/cooltt/blob/main/src/core/Conversion.ml) compares types and terms under cofibration assumptions, handles split types by restricting the context, and checks boundaries of extension types. Its invariants explicitly distinguish inputs that may still require weak-head normalization.
- **C2:** The [core source tree](https://github.com/RedPRL/cooltt/tree/main/src/core) separates syntax, semantic domains, evaluation, conversion, quotation, refinement state, and tactics. These layers provide a substantial reference for building cubical elaborators and experimenting with equality algorithms, beyond the included examples.

## Higher-order logic and LCF-style systems

### 6. [isabelle-prover/mirror-isabelle](https://github.com/isabelle-prover/mirror-isabelle)

**Language / role:** Standard ML, Scala, and Isabelle theories; generic proof assistant. **Project GitHub mirror:** the [repository page](https://github.com/isabelle-prover/mirror-isabelle/tree/master) identifies the upstream Isabelle repository it mirrors.

Study how certified logical objects remain attached to theories and proof contexts while a larger environment supports continuous checking. This is particularly useful for engineers designing APIs around context-dependent validity.

- **C1:** [Pure/thm.ML](https://github.com/isabelle-prover/mirror-isabelle/blob/master/src/Pure/thm.ML) exposes abstract certified types, certified terms, and theorems. It includes context-transfer operations, inference rules, proof dependencies, and explicit oracle interfaces, making the boundary between certified manipulation and additional trust visible.
- **C2:** The same module provides reusable matching, instantiation, resolution, conversion, and theorem-context operations for the generic Pure layer. The repository describes PIDE's versioned theory-source model, illustrating how that logical foundation participates in a larger interactive architecture.

### 7. [HOL-Theorem-Prover/HOL](https://github.com/HOL-Theorem-Prover/HOL)

**Language / role:** Standard ML; canonical HOL4 implementation.

Study the relationship among an abstract theorem type, derived automation, persistent theories, and a regression-controlled development process. The repository explains that development is merged forward to master after regression tests pass.

- **C1:** The [official guidebook](https://github.com/HOL-Theorem-Prover/hol-guidebook/blob/master/guidebook.smd) explains theorem construction through the trusted `Thm` structure and propagation of tags recording axioms or oracle use. This makes assumptions in derived results inspectable.
- **C2:** The guide also describes theory ancestry, qualified constants and types, theorem databases, and derived rules. These provide reusable organization for developments and automation rather than a single fixed proof task.
- **C4:** [Release notes](https://github.com/HOL-Theorem-Prover/HOL/releases) span, among others, Kananaskis-12 in 2018 and Trindemossen-2 in 2025. They document parallel builds, changed theory storage, kernel/compute evolution, and explicit incompatibilities and migration guidance.

### 8. [jrh13/hol-light](https://github.com/jrh13/hol-light)

**Language / role:** OCaml; HOL Light theorem prover.

An unusually direct place to study a compact logical foundation inside a much larger mathematics environment. Read the kernel signature before its implementation; it shows exactly which constructors and operations are exposed.

- **C1:** [fusion.ml](https://github.com/jrh13/hol-light/blob/master/fusion.ml) keeps `thm` abstract and implements primitive inference, substitution, alpha-equivalence, and type instantiation. The capture-avoidance and variable-clash handling demonstrate why even a small kernel requires careful invariants.
- **C2:** The same kernel supplies generic polymorphic terms and types, theorem substitution, equality rules, and definitional extension. These operations form a reusable substrate for derived proof procedures and theories. The explicit `new_axiom` interface also makes clear that a theorem's meaning depends on its admitted assumptions.

### 9. [gilith/opentheory](https://github.com/gilith/opentheory)

**Language / role:** Standard ML; checker and tooling for portable higher-order-logic theory packages.

Study proof interchange as a first-class systems problem: exported theory packages need a logical checker, dependency accounting, and tooling independent of the originating interactive prover. The repository identifies itself as the development distribution and documents regression theories and several supported ML compilers.

- **C1:** [Thm.sml](https://github.com/gilith/opentheory/blob/master/src/Thm.sml) represents a theorem using both its sequent and its axiom set. Inference combines those dependencies; abstraction checks that the bound variable is not free in hypotheses, and assumptions must be Boolean.
- **C2:** Its abstract theorem interface and alpha-aware term/sequent operations support reusable HOL theory packages. This is a different architectural target from an IDE-centric prover: it provides a common checking and packaging layer for exchanging developments.

## Specification and set-theoretic proving environments

### 10. [acl2/acl2](https://github.com/acl2/acl2)

**Language / role:** Common Lisp; ACL2 system and Community Books in one repository.

Study a prover whose automation is organized around interacting simplification and induction machinery. Count the system and its books once; the separate stable-release distribution is not another implementation.

- **C1:** [simplify.lisp](https://github.com/acl2/acl2/blob/master/simplify.lisp) documents the obligations involved in clause rewriting, assumption tracking, justification trees, and avoiding circular simplification dependencies. Comments explain why changes to dependency tracking forced earlier helper operations to be reconsidered.
- **C2:** The same source separates top-level expansion decisions, clause-wide reasoning, and literal rewriting. Type-set reasoning and linear arithmetic feed a common simplification pipeline, while the repository's Community Books provide reusable developments above the system. This is useful architecture to study when independently sensible reasoning procedures must cooperate.

### 11. [SRI-CSL/PVS](https://github.com/SRI-CSL/PVS)

**Language / role:** Primarily Common Lisp; specification language, typechecker, and interactive prover.

PVS is useful for understanding a design in which typechecking itself generates proof obligations. Its own README describes it as an evolving research prototype; this report does not equate that description with a small or trivial implementation.

- **C1:** The [language reference, especially subtype and TCC sections](https://pvs.csl.sri.com/doc/pvs-language-reference.pdf), explains context-dependent obligations such as proving a denominator nonzero. [typecheck.lisp](https://github.com/SRI-CSL/PVS/blob/master/src/typecheck.lisp) explicitly permits regenerating obligations for already checked expressions used in different prover contexts.
- **C2:** Parameterized theories, predicate subtypes, and dependent function/record/tuple types support reusable specifications. The typechecker manages theory instances, imported declarations, contextual typing state, and caches, making the interaction between modular specifications and proof obligations concrete. The linked manual is version 7.1 and warns that newer features may be missing.

### 12. [epfl-lara/lisa](https://github.com/epfl-lara/lisa)

**Language / role:** Scala 3; proof assistant based on sequent calculus and set theory.

A useful contrast to dependent-type kernels: proof steps are explicit data checked against sequent rules, while a Scala DSL and tactics live above the kernel.

- **C1:** [SCProofChecker.scala](https://github.com/epfl-lara/lisa/blob/main/lisa-kernel/src/main/scala/lisa/kernel/proof/SCProofChecker.scala) rejects forward references and references outside imported premises, validates expression sorts, and checks the parameters and conclusions of individual inference steps. Its formula-equivalence operations are part of the checking boundary.
- **C2:** [SequentCalculus.scala](https://github.com/epfl-lara/lisa/blob/main/lisa-kernel/src/main/scala/lisa/kernel/proof/SequentCalculus.scala) defines reusable sequent and proof-step representations, including substitution and subproof operations. The repository explains the separation between `lisa-kernel` and utilities for parsing, unification, syntax, and user tactics.

## Logical frameworks and mechanized metatheory

### 13. [Deducteam/Dedukti](https://github.com/Deducteam/Dedukti)

**Language / role:** OCaml; typechecker for the lambda-Pi calculus modulo rewriting.

Study what changes when user rewrite rules participate in definitional equality. The checker is also useful as a common target for encodings of different logics, rather than an assistant tied to one mathematical foundation.

- **C1:** [kernel/typing.ml](https://github.com/Deducteam/Dedukti/blob/master/kernel/typing.ml) combines dependent typing with subject-reduction constraints, conversion, partially typed rule contexts, and specific errors for escaping variables or circular constraints. These are substantial correctness obligations beyond ordinary AST traversal.
- **C2:** The typing implementation is a functor over a reduction interface and works with explicit signatures and typed contexts. The repository's manual explains modules exporting constants and rewrite rules and optional external confluence checking. It also explicitly says termination is not checked: accepting a useful encoding still requires respecting the framework's metatheoretic conditions.

### 14. [Deducteam/lambdapi](https://github.com/Deducteam/lambdapi)

**Language / role:** OCaml, with editor tooling; interactive assistant for the lambda-Pi calculus modulo rewriting.

A substantive implementation alongside Dedukti, adding an interactive elaboration and proof environment. Study how rewriting, constraint generation, mutable signatures, proof state, and editor rollback are separated.

- **C1:** The [architecture map](https://lambdapi.readthedocs.io/en/latest/structure.html) identifies distinct scoping, constraint-generating typing, unification, subject-reduction, and local-confluence components, plus tests expected to succeed and tests expected to fail.
- **C2:** The same map separates compiled signatures from signatures under construction and exposes a rollback-oriented interface for the language server. Exports to other proof/rule formats and multiple input syntaxes make this a reusable proof-processing environment.
- **C3:** [Decision-tree documentation](https://lambdapi.readthedocs.io/en/latest/dtrees.html) explains compilation of rewrite matching into symbol-attached trees with stack operations, saved terms, convertibility tests, and free-variable conditions. The trees can be visualized for debugging, making optimized evaluation inspectable.

### 15. [Beluga-lang/Beluga](https://github.com/Beluga-lang/Beluga)

**Language / role:** OCaml; contextual type theory and mechanized metatheory, including the Harpoon interactive prover.

Study contexts and object-language binding as explicit abstractions, and the less obvious correctness requirements of an interactive session manager. Beluga's repository documents higher-order abstract syntax and first-class contexts.

- **C1:** [Harpoon's prover structure](https://beluga-lang.readthedocs.io/en/latest/harpoon/prover-structure.html) explains how switching sessions changes theorem scope to prevent circular references among unfinished proofs. Mutual induction is organized within a session, not obtained accidentally through globally visible incomplete theorems.
- **C2:** The same document separates sessions, mutually inductive theorems, subgoals, metacontexts, and computational contexts. Those abstractions support reusable tactics and structured proof scripts for many object languages. The [Harpoon overview](https://beluga-lang.readthedocs.io/en/latest/harpoon/index.html) connects its tactics to inversion, lemma application, and induction.

### 16. [abella-prover/abella](https://github.com/abella-prover/abella)

**Language / role:** OCaml; interactive prover based on lambda-tree syntax.

An instructive alternative to encoding every object-language context manually. The project is specifically designed for reasoning about systems with binding, including programming-language metatheory.

- **C1:** The [official subject-reduction walkthrough](https://abella-prover.org/walkthrough.html) explains how binding, capture-avoiding substitution, and context assumptions participate in a preservation proof. It provides a concrete account of what the prover must preserve, rather than just a feature inventory.
- **C2:** The same walkthrough documents the two-level architecture: an executable specification logic describes inference rules, while a reasoning logic proves properties of their derivations. That reusable separation supports different operational semantics and logical systems while sharing the binding machinery and proof environment.

### 17. [standardml/twelf](https://github.com/standardml/twelf)

**Language / role:** Standard ML; LF implementation, logic-programming environment, and metatheorem-checking machinery.

**Historical design reference:** the repository retains earlier design material, calls its bundled user guide outdated, and describes its meta-theorem prover as preliminary. No present release cadence is asserted here. The source remains substantive, with separately organized coverage, termination, world, mode, and type checking.

- **C1:** [cover.fun](https://github.com/standardml/twelf/blob/main/src/cover/cover.fun) states contextual invariants for weakening and existential-variable creation, distinguishes input from output coverage, and requires a unifier with trailing. It is useful for studying completeness obligations and reversible unification state.
- **C2:** The [source organization](https://github.com/standardml/twelf/tree/main/src) and coverage functor show reusable interfaces for normalization, conversion, indexing, modes, subordination, worlds, and constraints. These components support checking many LF signatures and metatheoretic encodings rather than a single language semantics.

### 18. [Andromedans/andromeda](https://github.com/Andromedans/andromeda)

**Language / role:** OCaml; Andromeda 2, a proof checker for user-defined dependent type theories.

Study a trust boundary designed around judgments instead of a fixed universal conversion algorithm. It applies the LCF approach to a family of object type theories, with a separate metalanguage for constructing derivations.

- **C1:** The [object-type-theory documentation](https://www.andromeda-prover.org/type-theory.html) defines four judgment forms and says that judgments, boundaries, and derivations originate in the trusted nucleus. Contexts are combined when rules are applied; the soundness guarantee is explicitly relative to user-postulated and built-in structural rules.
- **C2:** Boundaries classify goals, while derivations act as parameterized proof builders. User declarations select the object theory, and the same nucleus and metalanguage infrastructure handle its judgments, abstraction, and instantiation. This is a substantive reusable framework, not a collection of hard-coded theorem tactics.

## Metamath and certificate-oriented verification

### 19. [metamath/metamath-exe](https://github.com/metamath/metamath-exe)

**Language / role:** C; Metamath executable with verification and proof-assistant facilities.

Study a logic-agnostic verifier implemented with explicit stacks and substitutions. Its simplicity at the language level does not eliminate hard engineering problems around incomplete proofs, storage ownership, or variable conditions.

- **C1:** [mmveri.c](https://github.com/metamath/metamath-exe/blob/master/src/mmveri.c) distinguishes valid, incomplete, and erroneous proofs; implements RPN proof evaluation; and checks disjoint-variable requirements after substitutions. Comments identify shared strings that must not be deallocated with temporary proof storage.
- **C2:** The verifier processes generic assertions, hypotheses, substitutions, and variable restrictions rather than embedding one mathematical logic. The same engine can therefore check different axiom databases and supply information about individual proof steps to interactive tooling.
- **C3:** The disjointness-checking code explains pointer/length reuse and how scans skip irrelevant portions of required and optional variable-pair lists. These local optimizations are directly readable beside the semantic checks they must preserve.

### 20. [digama0/mmj2](https://github.com/digama0/mmj2)

**Language / role:** Java; GUI proof assistant, verifier, and grammar analysis for Metamath.

Study the interaction among incomplete worksheets, syntax trees, hypothesis matching, and proof reconstruction. The repository explicitly identifies this implementation as a continuation of Mel O'Cat's original work.

- **C1:** The historical [Step Unifier design document](https://github.com/digama0/mmj2/blob/master/doc/StepUnifier.html) details occurs checks, consistent work-variable substitutions, backtracking, and rollback of partial matches. It is labeled a proposed design and should be read as design history, not assumed to name current implementation files.
- **C3:** The [change log](https://github.com/digama0/mmj2/blob/master/CHGLOG.TXT) records an alternative LR parser, the startup-versus-repeated-parsing tradeoff, and persistent caching of expensive parse tables.
- **C4:** Entries across 2014 and 2016 document Java compatibility changes, a macro layer keeping database-specific behavior out of the generic core, and support for forward worksheet references only when dependency cycles are absent. This is concrete evolution and complexity management, not a claim about current maintenance frequency.

### 21. [metamath/metamath-knife](https://github.com/metamath/metamath-knife)

**Language / role:** Rust; parallel and incremental Metamath processing and verification.

This is a disclosed, substantive fork of smetamath-rs, with expanded proof-format support and its own evolution. The original is not counted separately. Read the library's architecture comments before examining individual checking passes.

- **C1:** [database.rs](https://github.com/metamath/metamath-knife/blob/main/metamath-rs/src/database.rs) explains segment ordering, reuse of segment identifiers, scope boundaries, and versioned dependency tracking. Incorrect reuse would invalidate the meaning of cached verification results.
- **C2:** A `Database` API provides parsing and on-demand analyses, with readers recording exactly which results later passes used.
- **C3:** Segments are units of incremental recomputation and parallel work; an executor returns promises and schedules jobs using estimated cost. The same source candidly documents limitations, including grouping/header restrictions in file splitting that do not fully match the Metamath specification. Its design should be studied together with those constraints.

### 22. [digama0/mm0](https://github.com/digama0/mm0)

**Language / role:** Rust and C, with additional implementations/formalization code; Metamath Zero specification language and proof-checking ecosystem.

Study the separation between a human-auditable specification and an untrusted producer's proof certificate. The Rust elaborator/server and C verifier belong to one repository and count once.

- **C1:** The [MM0 specification](https://github.com/digama0/mm0/blob/master/mm0.md) defines the acceptance obligation: the checker must validate theorem claims against the supplied specification even when the proof producer is untrusted. It distinguishes syntax, sorts, binding restrictions, definitions, and proof input, and explicitly warns that the specification has not stabilized.
- **C2:** The repository describes independent specification and proof files, with an MM1 elaboration/metaprogramming layer generating material for the verifier. Users supply the axiom system, allowing the checking substrate to support different logics. The stated goal of verification down to machine instructions is a project objective; this report does not claim it has been completed.

## Kernels as libraries and verification targets

### 23. [CakeML/cakeml](https://github.com/CakeML/cakeml)

**Language / role:** Standard ML/HOL4 and CakeML; included specifically for **Candle**, its HOL theorem-prover implementation and verification.

Study how a kernel correctness argument is connected to the semantics of its implementation language. The broader compiler is relevant infrastructure, but it is not the reason this monorepo belongs in this category.

- **C1:** The [Candle prover map](https://github.com/CakeML/cakeml/blob/master/candle/prover/README.md) identifies definitions of runtime-value invariants, preservation proofs for kernel functions and prover evaluation, and a top-level soundness theorem. This exposes multiple proof obligations between abstract inference and executable behavior.
- **C2:** The [Candle subsystem](https://github.com/CakeML/cakeml/tree/master/candle) separates deeply embedded HOL syntax, standard HOL inference and semantics, ad-hoc overloading, and set-theoretic foundations. The prover directory also identifies a verified compute primitive. This decomposition supports reusable logical infrastructure and extensions rather than one fixed certificate check.

### 24. [digama0/lean4lean](https://github.com/digama0/lean4lean)

**Language / role:** Lean; Lean 4 kernel implementation, external checking tool, and metatheory/implementation-verification project.

The repository explicitly says it derives from Lean's C++ kernel and can share implementation bugs. Treat it as a port and verification/audit effort; independence of implementation and completion of all formal proofs are not assumed.

- **C1:** The [divergence record](https://github.com/digama0/lean4lean/blob/master/divergences.md) makes trust assumptions concrete: native reduction is unsupported, primitives receive additional checks, and universe and projection behavior differ in documented ways. It is a useful example of tracking the semantic meaning of differences between checkers.
- **C2:** The repository separates the library environment interface, standalone checker, abstract theory, and proofs relating implementation to theory. Those are reusable components for checking environments and studying the kernel's metatheory.
- **C3:** Its documented interface supports multithreaded module checking and comparison against the C++ kernel on slow declarations. This establishes a performance-validation mechanism; no benchmark ranking is inferred from it.

### 25. [latte-central/latte-kernel](https://github.com/latte-central/latte-kernel)

**Language / role:** Clojure/ClojureScript; reusable trusted kernel of the LaTTe proof assistant.

A compact, literate implementation with enough structure to study beyond a tutorial. The repository explicitly prioritizes readability and warns about fragile support in one build path; it is not selected as a throughput or deployment-maturity exemplar.

- **C1:** The [literate typechecker](https://github.com/latte-central/latte-kernel/blob/master/src/latte_kernel/typing.cljc.md) checks dependent applications using substitution, compares inferred and expected types by reduction, and rejects references to theorems without proofs. Error results preserve contextual diagnostic information.
- **C2:** The [proof elaborator/checker](https://github.com/latte-central/latte-kernel/blob/master/src/latte_kernel/proof.cljc.md) defines declarative proof steps for declarations, local facts, discharge, and final proof terms. It tracks local definitions and their dependencies when abstracting variables, providing reusable machinery above normalization and typing. The kernel is expressly packaged as a basis for constructing assistants.

## Coverage, search process, and limits

Discovery used more than six distinct live-search formulations, including: mainstream prover/kernel architecture; LCF and HOL source repositories; cubical and homotopy type theories; Metamath verifier implementations; logical frameworks and rewriting; contextual LF and binding-aware metatheory; verified kernels and external checkers; Scala and Clojure proof assistants; and historical/independent checking systems. Follow-up queries targeted source layouts, release histories, and specific implementation mechanisms. Later broad searches increasingly returned already covered systems, proof libraries, wrappers, educational tools, or new compatibility claims requiring a separate audit. A final language-diversity pass added LaTTe's substantive kernel.

Every retained repository was opened on GitHub, including Isabelle's repository tree when its root page timed out. Each also has an opened, distinct primary implementation or documentation source beyond the repository README; GitHub content retrieval was used when browser retrieval failed. Branches and cited source paths were checked rather than inferred from familiar project names. Some documentation is intentionally historical, notably Twelf's design material, mmj2's unifier proposal/change log, and the PVS 7.1 manual. These are identified where used. Links to moving branches are entry points, not immutable audit snapshots.

The selection spans OCaml, Standard ML, Haskell, Common Lisp, Java, Scala, C/C++, Rust, Lean, and Clojure, and covers several distinct trust models. It does not imply that these systems have identical kernels, identical soundness assumptions, or interchangeable proof formats. C4 is claimed only where the inspected material shows evolution together with compatibility or complexity management; other entries qualify through different criteria.

Important exclusions: mathlib, set.mm, and the Cubical Agda library are developments atop provers, so they are not separate implementations here. AI proof-search agents, MCP/editor wrappers, awesome lists, and general SAT/SMT search engines fall outside this selection. Related redtt/RedPRL predecessors were not separately counted alongside cooltt; original smetamath-rs was not duplicated alongside metamath-knife. Moved projects without a verified substantive GitHub home were not included. Additional newer kernels and research prototypes exist; this report is a supported selection guide, not an exhaustive census or a fresh soundness audit.
