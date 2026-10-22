# Type checkers and type inference engines

Research date: **2026-10-09**.

This guide selects 25 GitHub repositories containing substantive static type checkers, inference engines, or reusable checking frameworks. It includes standalone tools and explicitly identified compiler/IDE subsystems, spanning gradual typing, abstract interpretation, structural subtyping, refinement types, trait solving, and dependent types. A compiler monorepo appears only once. The criteria are engineering judgments grounded in the linked primary material, not claims of complete soundness or uniformly exemplary code.

**Criteria legend:** **C1** — difficult correctness involving invariants, recursion, control flow, adversarial inputs, or failure handling. **C2** — substantial reusable abstractions supporting multiple analyses, language constructs, or consumers. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — sustained evolution accompanied by compatibility work, testing, or complexity management. Each entry justifies at least two criteria.

## Python: contrasting inference architectures

### 1. [python/mypy](https://github.com/python/mypy)

**Language / role:** Python; optional static checker and local type inference engine.

Study how a checker coordinates semantic analysis, import dependencies, and expression inference without requiring a new Python runtime.

- **C1:** The build manager processes cyclic imports as strongly connected components; semantic analysis revisits unresolved forward references, and checking can require further passes. These are concrete dependency and convergence problems, explained in the [implementation overview](https://github.com/python/mypy/wiki/Implementation-Overview).
- **C3:** The same overview describes retaining ASTs in a daemon for incremental runs and using smaller standard-library fixtures to keep unit tests inexpensive. It exposes the boundaries between build scheduling, semantic analysis, and checking, rather than treating performance as an opaque optimization.

The overview is the main entry point; its linked checker, expression checker, and build-manager modules provide focused reading paths.

### 2. [microsoft/pyright](https://github.com/microsoft/pyright)

**Language / role:** TypeScript; Python checker and language-service analysis engine.

Study demand-driven type evaluation in an interactive editor, where source files may be incomplete and only some need full diagnostics.

- **C1:** Binding constructs a reverse control-flow graph so evaluation can recover the type of a symbol from its antecedents. Scopes, binding consistency, imports, and type evaluation have distinct responsibilities in the [internals guide](https://github.com/microsoft/pyright/blob/main/docs/internals.md).
- **C3:** The program prioritizes open files and their dependencies, retains per-file analysis state, and skips full checking for imported files that do not need diagnostic output. The [architecture comparison](https://github.com/microsoft/pyright/blob/main/docs/mypy-comparison.md) explains its lazy evaluator and the need to answer queries on erroneous or incomplete code. This is architectural evidence, not an endorsement of the document's comparative speed claims.

### 3. [facebook/pyrefly](https://github.com/facebook/pyrefly)

**Language / role:** Rust; Python checker and language server.

This is a useful counterpoint to both repeated AST passes and identifier-at-a-time evaluation. Its [architecture document](https://github.com/facebook/pyrefly/blob/main/ARCHITECTURE.md) explains exports, per-module bindings, and cross-module solving.

- **C1:** Recursive bindings introduce temporary `Type::Var` placeholders. The worked loop example shows how a self-dependent union is solved using its reachable bound; import-star exports also require transitive resolution.
- **C3:** The design deliberately chooses module-level incrementality and parallelism, anticipating large cyclic module components. Separate graph/cache utilities and type representations make the tradeoff between granularity and overhead inspectable. The document states performance goals; no measured speedup is assumed here.

### 4. [google/pytype](https://github.com/google/pytype)

**Language / role:** Python and C++; bytecode-based abstract interpretation and type inference. **Archived historical project:** the repository says Python 3.12 is its final supported Python version.

Study the benefits and maintenance costs of modeling Python execution at the bytecode level. The [main-loop guide](https://github.com/google/pytype/blob/main/docs/developers/main_loop.md) explains opcode dispatch and the second pass needed to analyze otherwise unvisited function bodies.

- **C1:** The [typegraph design](https://github.com/google/pytype/blob/main/docs/developers/typegraph.md) represents bindings, origins, source sets, and path conditions. It also explains cross-language ownership and reference-counting hazards when C++ bindings retain Python objects.
- **C3:** The hot typegraph is implemented in C++, with reachability solving, caching, and deliberate ownership boundaries. The archive notice supplies an unusually candid account of how bytecode changes complicated compatibility and new typing features.

## Ruby, JavaScript, and PHP

### 5. [sorbet/sorbet](https://github.com/sorbet/sorbet)

**Language / role:** C++, with Ruby support code; gradual Ruby checker.

Study how a checker reduces Ruby's large syntax and metaprogramming surface into a smaller inference problem. The [internals document](https://github.com/sorbet/sorbet/blob/master/docs/internals.md) follows desugaring, DSL rewriting, name resolution, CFG construction, and inference.

- **C1:** CFG-based inference must accommodate Ruby blocks, exceptional control flow, and cycles. The documentation explicitly describes approximations for rescue blocks and restrictions on changing variable types inside loops; these are useful examples of exposed semantic tradeoffs.
- **C3:** Each binding gets a single inference decision, and method bodies can be checked independently. Compact references into global state and precomputed ancestor relationships address lookup cost. The architecture explains the inference power sacrificed to make that approach practical.

### 6. [soutaro/steep](https://github.com/soutaro/steep)

**Language / role:** Ruby; checker using RBS declarations and annotations.

Study a Ruby-native implementation that treats method lookup and narrowing as explicit abstractions.

- **C1:** The [narrowing implementation](https://github.com/soutaro/steep/blob/master/doc/narrowing.md) introduces logical types and truthy/falsy environments for methods such as `nil?`, `is_a?`, and `===`. It explains why `case` conditions require synthetic locals and how pure-call facts propagate.
- **C2:** [Shapes](https://github.com/soutaro/steep/blob/master/doc/shape.md) provide a common method-set representation for interfaces, classes, tuples, records, and procs, including receiver-sensitive `self` behavior.
- **C3:** Shape entries calculate method types lazily, avoiding computation for methods a call never uses. The design document also records limitations in union/self handling, making it valuable for studying unfinished edges rather than assuming perfection.

### 7. [microsoft/TypeScript](https://github.com/microsoft/TypeScript)

**Language / role:** Go in the current `main` checker tree; TypeScript/JavaScript compiler and type checker. The language here reflects the inspected source, not the historical implementation.

Study the checker subsystem at [tsc/internal/checker/checker.go](https://github.com/microsoft/TypeScript/blob/main/tsc/internal/checker/checker.go).

- **C1:** Inference contexts distinguish covariant and contravariant candidates, priorities, fixed inferences, and contextual versus inferential checking. The code explicitly marks contextual types as non-cacheable, illustrating how a seemingly simple cache can violate inference semantics.
- **C3:** Dedicated keys and caches cover narrowed types, instantiated signatures, unions, indexed access, and reverse-mapped types. These structures make repeated structural operations and their identity assumptions visible. Read the checking-mode and inference-context definitions before attempting the larger checking routines.

This entry counts the repository once; it does not count historical or native-port lineages as separate projects.

### 8. [facebook/flow](https://github.com/facebook/flow)

**Language / role:** Rust in the inspected `main` tree; static JavaScript checker.

Study the [subtyping engine](https://github.com/facebook/flow/blob/main/rust_port/crates/flow_typing_flow_js/src/flow_js.rs), whose module commentary explains constraint propagation through lower and upper bounds.

- **C1:** A new subtype relation is decomposed into simpler flows; connections between concrete types and variables induce additional constraints until a fixed point. Correctness depends on preserving those bounds and their interactions rather than only checking an AST node in isolation.
- **C2:** The [Rust crate layout](https://github.com/facebook/flow/tree/main/rust_port/crates) separates type representations, contexts, environment construction, inference services, and specialized checking operations. The core engine exposes common flow operations consumed by those layers, making it a substantial reusable constraint substrate.

Older OCaml-oriented descriptions should not be assumed to describe these current paths.

### 9. [kaleidawave/ezno](https://github.com/kaleidawave/ezno)

**Language / role:** Rust; experimental JavaScript/TypeScript checker and compiler. **Scope warning:** the repository says it does not yet support enough features to check existing projects generally.

Study an effects-aware alternative to conventional expression-only typing.

- **C1:** The [events design](https://github.com/kaleidawave/ezno/blob/main/checker/documentation/events.md) records property updates, calls, and throws during function synthesis, attaches them to function types, and replays them in the caller's state. This creates a concrete correctness problem around the ordering and context of effects.
- **C2:** The [checker crate guide](https://github.com/kaleidawave/ezno/blob/main/checker/README.md) explains the separation between AST-independent checking logic and optional parser synthesis bindings, allowing another toolchain to integrate its own AST.

Its experimental status is part of the selection: useful architecture research, not a claim of TypeScript compatibility or proven safety.

### 10. [vimeo/psalm](https://github.com/vimeo/psalm)

**Language / role:** PHP; static analysis with a substantial type inference and reconciliation engine.

The [implementation guide](https://github.com/vimeo/psalm/blob/master/docs/contributing/how_psalm_works.md) makes the scanning/analysis split particularly approachable.

- **C1:** Function analysis carries a context of variable and property types, clones it at branches, and reconciles the results afterward. Assertions such as non-nullness refine unions, while inferred returns are checked against declared returns. The guide identifies the storage, context, and reconciliation layers involved.
- **C3:** Dependencies and signatures are collected before parallel analysis. Shallow scans extract interfaces from dependencies; deep scans inspect bodies when required. This is a concrete way to limit vendor-code work while retaining information needed for inheritance and calls.

Focus on the type-analysis path described by the guide; Psalm's broader security-analysis capabilities are not the reason for inclusion.

## Lua, Erlang, and Clojure

### 11. [luau-lang/luau](https://github.com/luau-lang/luau)

**Language / role:** C++; gradual checking and inference in the `Analysis` subsystem of a Lua-derived language.

- **C1:** [ConstraintSolver.cpp](https://github.com/luau-lang/luau/blob/master/Analysis/src/ConstraintSolver.cpp) contains ownership assertions for blocked types and type packs, saturation of generic arguments, and defaults that can depend on preceding arguments. Those details expose the invariants behind deferred solving.
- **C2:** The implemented [user-defined type-function design](https://github.com/luau-lang/rfcs/blob/master/docs/user-defined-type-functions.md) adds a reusable type-manipulation API: types are represented as VM userdata, transformed by ordinary Luau functions during analysis, and converted back into the solver's representation.

Study the interaction between the constraint engine and this type runtime, including failure propagation. The RFC is supporting documentation, not a second repository counted in the list.

### 12. [teal-language/tl](https://github.com/teal-language/tl)

**Language / role:** Teal and Lua; compiler/checker for a typed Lua dialect.

Study a smaller self-hosted checker with explicit flow facts, especially [teal/facts.tl](https://github.com/teal-language/tl/blob/main/teal/facts.tl).

- **C1:** The fact algebra distinguishes type tests from value equality: negating equality must not subtract an entire type. Conjunction, disjunction, union intersection, and widening are implemented explicitly, including special treatment of type variables and implicit nil.
- **C4:** The [changelog](https://github.com/teal-language/tl/blob/main/CHANGELOG.md) documents releases from 2020 through 2025, inference regressions and fixes, Lua-target compatibility fixes, richer type-reporting APIs, and the move toward splitting the large implementation into modules. This establishes sustained complexity management, not merely repository age.

The current modular source is a better implementation entry point than assuming the older single-file layout remains authoritative.

### 13. [josefs/Gradualizer](https://github.com/josefs/Gradualizer)

**Language / role:** Erlang; gradual checker using existing Erlang type specifications. The repository describes its status as close to beta and acknowledges unsupported cases.

- **C1:** [typechecker.erl](https://github.com/josefs/Gradualizer/blob/master/src/typechecker.erl) explains why recursive subtype comparisons need a set of previously compared type pairs. It also enforces normalized source annotations and accumulates upper/lower constraints for type variables.
- **C3:** The same source caches subtype results with the module in the key and imposes a per-form checking timeout. This makes both repeated-work avoidance and pathological-input handling directly inspectable.

The [design notes](https://github.com/josefs/Gradualizer/blob/master/Notes.md) provide historical rationale, including the boundary around process communication. Treat their unchecked plans as historical notes; the current checker is the source for implemented behavior.

### 14. [typedclojure/typedclojure](https://github.com/typedclojure/typedclojure)

**Language / role:** Clojure; optional typing library with separate checker, analyzer, runtime, and integration modules.

Study how types model variadic core functions and heterogeneous map-shaped data in a dynamic Lisp.

- **C1:** The historical [inference design note](https://github.com/typedclojure/typedclojure/blob/main/doc/infer-detail.md) works through repeated argument sequences and the underdetermined constraints produced by `assoc` and heterogeneous maps. It is concrete evidence of the inference problem, not a claim that its historical limitations remain unresolved today.
- **C2:** The [Malli integration guide](https://github.com/typedclojure/typedclojure/blob/main/typed/malli/README.md) shows the type representation reused for validators and parsers, with validation facts refining checked code and parsing producing typed tagged results. The repository's module split also separates development-time checking from runtime dependencies.

## Pluggable and refinement checking

### 15. [typetools/checker-framework](https://github.com/typetools/checker-framework)

**Language / role:** Java; framework for pluggable Java type checking and reusable dataflow analysis.

Study the mechanisms for implementing families of checkers, not just one fixed type system.

- **C2:** [AbstractAnalysis](https://github.com/typetools/checker-framework/blob/master/dataflow/src/main/java/org/checkerframework/dataflow/analysis/AbstractAnalysis.java) parameterizes abstract values, stores, and transfer functions, sharing machinery across forward and backward analyses.
- **C1:** [ForwardAnalysisImpl](https://github.com/typetools/checker-framework/blob/master/dataflow/src/main/java/org/checkerframework/dataflow/analysis/ForwardAnalysisImpl.java) keeps separate then/else stores, handles exceptional CFG blocks, and guards analysis-state invariants even when analysis crashes.
- **C3:** The same implementation uses a worklist for fixed-point iteration and configurable widening after repeated visits. This exposes how termination and precision are balanced within a reusable framework.

### 16. [ucsd-progsys/liquidhaskell](https://github.com/ucsd-progsys/liquidhaskell)

**Language / role:** Haskell; refinement-type checker integrated with GHC.

Study how a rich verification front end connects source specifications, compiler IR, modular interfaces, and generated constraints.

- **C1:** The repository's [plugin architecture guide](https://github.com/ucsd-progsys/liquidhaskell#ghc-plugin-development-guide) explains why checking needs unoptimized Core even when the user's compilation uses optimizations. It describes dependency assumptions, constraint generation, and checking via liquid-fixpoint; its detailed commentary identifies the version to which it refers.
- **C2:** [Types/Specs.hs](https://github.com/ucsd-progsys/liquidhaskell/blob/develop/liquidhaskell-boot/src/Language/Haskell/Liquid/Types/Specs.hs) documents separate `BareSpec`, `TargetSpec`, and serializable `LiftedSpec` stages. Exported specifications deliberately omit local details and termination obligations, giving downstream modules a reusable verification interface.

The specification lifecycle is the most focused reading path; compiler-version coupling is a real part of this architecture.

### 17. [nickel-lang/nickel](https://github.com/nickel-lang/nickel)

**Language / role:** Rust; gradual type checker for a configuration language, in `core/src/typecheck`.

The [typechecking module](https://github.com/nickel-lang/nickel/blob/master/core/src/typecheck/mod.rs) contains unusually useful implementation documentation.

- **C1:** It distinguishes dynamic traversal from enforced static checking, then separates checking and inference within the static mode. Type annotations and contracts change those modes. The documented refusal to implicitly generalize inferred let bindings makes an important inference boundary explicit.
- **C3:** Unification metadata tracks upper bounds and pending updates to variable levels, allowing costly traversals to be deferred and combined. The implementation also bounds shallow standard-library record inference. These optimizations are described alongside the invariants they must preserve.

This is a compact study of gradual boundaries, row representations, bidirectional checking, and unification in one subsystem.

## Compiler and IDE inference subsystems

### 18. [ocaml/ocaml](https://github.com/ocaml/ocaml)

**Language / role:** OCaml; the compiler's `typing` subsystem.

Study how ML inference scales to objects, polymorphic variants, classes, and GADTs. Start with [ctype.mli](https://github.com/ocaml/ocaml/blob/trunk/typing/ctype.mli), then follow expression and pattern checking in [typecore.ml](https://github.com/ocaml/ocaml/blob/trunk/typing/typecore.ml).

- **C1:** The core type interface documents exception-safe restoration of generalization levels, scope-escape checks, lowering of contravariant variables, and interactions between object rows and GADT equations. These are explicit correctness obligations on mutable type state.
- **C2:** A shared API provides instantiation, generalization, row operations, class-signature handling, and pattern environments. The expression checker consumes those operations rather than giving each syntax form an unrelated unifier.

The selection concerns these typing modules, not an assessment of the runtime or compiler backends.

### 19. [ghc/ghc](https://github.com/ghc/ghc)

**Language / role:** Haskell; GHC's `compiler/GHC/Tc` subsystem. **Official substantive GitHub mirror:** development and contribution tracking are hosted on GHC's GitLab, as the repository explicitly states.

Study the boundary between constraint generation, solving, and evidence production through [GHC/Tc/Solver.hs](https://github.com/ghc/ghc/blob/master/compiler/GHC/Tc/Solver.hs).

- **C1:** The source explains preserving insoluble constraints when exceptions propagate, solving equalities under typechecking levels, and wrapping failures so constraints do not escape their scope. It ties these behaviors to concrete failure cases.
- **C2:** The solver exposes common operations for inference, ambiguity checking, interactive checking, normalization, top-level solving, and plugin consumers. Dedicated modules handle defaulting, dictionaries, rewriting, and the inert set, giving a shared solving architecture for many language features.

The mirror retains implementation code and is included under the GitHub-source requirement; it is not presented as the upstream collaboration venue.

### 20. [purescript/purescript](https://github.com/purescript/purescript)

**Language / role:** Haskell; PureScript compiler typechecker, especially subsumption and row typing.

Study the small but substantial [TypeChecker/Subsumption.hs](https://github.com/purescript/purescript/blob/master/src/Language/PureScript/TypeChecker/Subsumption.hs) module.

- **C1:** Subsumption instantiates quantified types, skolemizes expected polymorphism, reverses function-argument comparison, and checks missing or excess record fields before unifying row tails. The cases show why ordinary equality unification is insufficient.
- **C2:** The implementation indexes its elaboration mode and return evidence through `ModeSing` and the `Coercion` type family. The same recursive checker either constructs dictionary-inserting expression transformations or checks in a mode where such insertion is impossible, such as underneath record fields.

This is a useful focused example of using the implementation language's types to constrain the checker itself.

### 21. [rust-lang/chalk](https://github.com/rust-lang/chalk)

**Language / role:** Rust; logic-based trait solver library. **Sunset historical project:** the repository directs readers to the newer Rust trait-solver work; it is not presented as rustc's current production solver.

- **C1:** The [canonical-query chapter](https://github.com/rust-lang/chalk/blob/master/book/src/canonical_queries.md) distinguishes no solution, ambiguity, and proved results, including substitutions and lifetime constraints. Its examples show why a checker must defer an ambiguous obligation rather than select an arbitrary valid answer.
- **C2:** The [engine overview](https://github.com/rust-lang/chalk/blob/master/book/src/engine.md) identifies a general logic engine separated from Rust-specific types and rules, supporting negation and coinductive solving. This is a reusable solver abstraction rather than only a language-specific AST visitor.

Read its book as documentation of this implementation and its design lineage, not as a guarantee about today's rustc query API.

### 22. [rust-lang/rust-analyzer](https://github.com/rust-lang/rust-analyzer)

**Language / role:** Rust; IDE compiler front end, with type inference in `crates/hir-ty`.

Study inference as a queryable semantic service. The [inference entry point](https://github.com/rust-lang/rust-analyzer/blob/master/crates/hir-ty/src/infer.rs) operates on a function body and separates expression, pattern, coercion, closure, and unification concerns.

- **C1:** The [architecture guide](https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md) states invariants for incomplete syntax, crate-specific semantic representations, and the mapping from syntax to semantic entities.
- **C3:** Incremental queries compute derived state lazily; the documented invariant is that editing a function body should not invalidate unrelated global facts. The guide explains the input database and stable item summaries supporting that behavior.
- **C2:** The `hir` and IDE facades expose the semantic model to multiple editor operations while isolating LSP serialization. Some guide passages retain older solver references; use the current source for the actual solver integration.

## Dependent types, elaboration, and checking kernels

### 23. [agda/agda](https://github.com/agda/agda)

**Language / role:** Haskell; dependently typed language and proof assistant, particularly `Agda.TypeChecking`.

Study type-directed equality in [Conversion.hs](https://github.com/agda/agda/blob/master/src/full/Agda/TypeChecking/Conversion.hs).

- **C1:** Conversion attempts can create metavariables, generate constraints, fail, and restore state. The implementation carefully limits shortcuts around blocked types, subtyping, sized types, and cubical operations; comments identify cases where an apparently natural shortcut is unsound or loops.
- **C3:** Pointer and syntactic-equality checks avoid expensive reduction, while direct metavariable assignment can avoid unfolding. The source records why repeatedly traversing whole terms became infeasible and includes profiling hooks for the alternatives.

This is particularly useful for engineers studying the interaction between optimization, speculative mutation, and definitional equality.

### 24. [idris-lang/Idris2](https://github.com/idris-lang/Idris2)

**Language / role:** Idris; quantitative dependent typing and elaboration.

The [implementation overview](https://github.com/idris-lang/Idris2/blob/main/docs/source/implementation/overview.rst) connects high-level Idris, implicit `TTImp`, and the core `TT` language. It cautions that some notes may lag the code.

- **C1:** Core terms are indexed by names in scope, and local variables carry erased proofs of valid indices. Unification preserves these scope relationships; a separate linearity pass handles multiplicities after elaboration.
- **C2:** The same core term, environment, normalization, and unification interfaces serve implicit argument inference, elaboration, and proof search.
- **C3:** Constraints record the metavariables blocking them so retries can be selective. Glued term/normal-form representations and lazy decoding of checked definitions avoid work until it is needed. These are documented mechanisms, without relying on the guide's numerical performance comparisons.

### 25. [leanprover/lean4](https://github.com/leanprover/lean4)

**Language / role:** Lean and C++; elaboration and kernel type checking in a programming language/proof assistant.

Study both [kernel/type_checker.cpp](https://github.com/leanprover/lean4/blob/master/src/kernel/type_checker.cpp) and [TermElabM.lean](https://github.com/leanprover/lean4/blob/master/src/Lean/Elab/Term/TermElabM.lean).

- **C1:** The kernel checks universe parameters, rejects unknown free variables and invalid safety dependencies, and extends local contexts only after checking binder domains. It also checks projection-index bounds to prevent truncation from changing the selected field.
- **C2:** The elaborator represents pending work through synthetic metavariable kinds for typeclass resolution, coercions, tactics, and postponed terms, with saved contexts and backtrackable state. A shared representation supports multiple forms of elaboration without conflating them with final core checking.
- **C3:** The kernel explicitly bounds numeral-reduction resources and uses normalization/reduction paths that avoid unnecessary work. Its comments explain the failure modes those limits address.

## Coverage, search method, and limitations

Discovery used **22 distinct live search formulations**, followed by reads of official GitHub pages, GitHub API metadata, project documentation, and individual source files. Search angles included Python incremental versus bytecode inference; Ruby/RBS gradual checking; JavaScript structural and effects-aware typing; Lua type solvers; Erlang and Clojure optional typing; pluggable Java analysis; refinement verification; ML unification and subsumption; Rust trait and IDE solvers; dependent-type elaboration; PHP inference; and reusable/algebraic-subtyping research engines. Final broad searches mostly added small demonstrations, adjacent inference meanings, and overlapping implementations rather than compelling new architectural coverage.

Canonical repository URLs were checked by opening GitHub or reading repository API metadata. Every retained repository has additional primary implementation or design evidence beyond its project description. Source links use the branches inspected during research and can move; they are not frozen audit artifacts. Current source inspection was important for TypeScript, Flow, and Teal, whose layouts differ from older descriptions.

Excluded from the selection were annotation-only collections, editor/package wrappers, runtime-only validators, tutorial-sized Hindley–Milner demonstrations, awesome lists, and unrelated machine-learning inference engines. Closely related forks were not counted separately. The search also surfaced Inferno and small algebraic-subtyping implementations, but they were not expanded into entries without the same combination of verified GitHub provenance and implementation coverage. Omissions are not negative quality judgments; this is a selection guide rather than an exhaustive language census.

Status qualifications are explicit for archived Pytype, sunset Chalk, experimental Ezno, pre-beta Gradualizer, and the official GHC mirror. Other entries are not blanket claims of active maintenance. C4 is used only where dated evolution and concrete maintenance work were inspected; old copyright dates, stars, and recent pushes were not treated as sufficient evidence. No candidate code was executed, dependencies installed, large repositories cloned, or comparative benchmarks independently reproduced.
