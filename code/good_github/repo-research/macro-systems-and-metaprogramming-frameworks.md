# Macro systems and metaprogramming frameworks

Research date: 2026-10-09.

This selection covers 24 GitHub repositories implementing macro expansion, reusable macro-authoring infrastructure, typed program transformation, staged code generation, and general-purpose compile-time metaprogramming. Language repositories are included only for their identified macro subsystem. The emphasis is on code an experienced engineer can study for binding semantics, composition, diagnostics, compiler integration, and compilation cost. This is a selection guide, not a claim that every component is uniformly exemplary or that every project is suitable for a new production dependency.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency restrictions, language semantics, malformed inputs, or failure handling.
- **C2 — Abstraction:** substantial, reusable machinery supporting multiple applications.
- **C3 — Performance and structure:** concrete performance constraints addressed through an understandable architecture.
- **C4 — Evolution:** evidence across years of compatibility work, testing, or complexity management; repository age alone does not qualify.

The criteria below are engineering judgments grounded in the linked primary material. GitHub repository metadata was checked for canonical names, default branches, forks, and archive flags. An unarchived flag is not treated as proof of active maintenance.

## Language-integrated expanders and language-building systems

### 1. [racket/racket](https://github.com/racket/racket)

**Language/role:** Racket; the `racket/src/expander` subsystem implements the reader, macro expander, binding representation, and module front end.

Study a production language front end whose expander can also bootstrap and run separately. The separation between syntax objects, scopes, namespaces, expansion, and compilation to linklets makes the implementation particularly instructive.

- **C1:** Scope identity, phase shifting, and serialization must preserve bindings. The implementation checks that serialized scopes are reachable and coordinates binding tables with reachability analysis. These are concrete invariants beyond textual substitution. **C3:** Bindings are attached to the most recently allocated scope to improve lookup and garbage collection. Both decisions are explained in [the scope implementation](https://github.com/racket/racket/blob/master/racket/src/expander/syntax/scope.rkt).
- **C2:** The same front end supports module loading, expansion, compilation, and evaluation. Its [implementation roadmap](https://github.com/racket/racket/blob/master/racket/src/expander/README.txt) explains these boundaries, embedding and bootstrapping, cache behavior, and performance instrumentation. It also documents the requirement that the extracted expander not retain dependencies on its host's syntax objects.

### 2. [michaelballantyne/syntax-spec](https://github.com/michaelballantyne/syntax-spec)

**Language/role:** Racket; a metalanguage for defining extensible embedded DSLs with explicit binding rules.

Study how a language-building framework moves binding checks out of individual macro implementations and into declarative grammar specifications.

- **C1:** Binding classes reject references resolving to the wrong kind of binder. Binding spaces add scopes to definitions and references, while separate nonterminal forms describe simultaneous, sequential, and exported bindings. The [language-specification reference](https://github.com/michaelballantyne/syntax-spec/blob/main/scribblings/reference/specifying.scrbl) explains the operational consequences.
- **C2:** Extension classes allow DSL-specific macros to expand into a core language before compilation. The [repository overview](https://github.com/michaelballantyne/syntax-spec/blob/main/README.md) identifies uses in Qi and hosted miniKanren and includes PEG, command-line, class, and hardware-language examples.

**Status:** The project explicitly calls itself a prototype, warns of incomplete documentation and future breaking changes, and uses versioned package names for breaking releases.

### 3. [sweet-js/sweet-core](https://github.com/sweet-js/sweet-core)

**Language/role:** JavaScript with Flow annotations; the historical Sweet.js core macro expander.

Study the interaction between JavaScript grammar recognition and hygienic syntax transformation. **This repository is archived**; it is retained as an implementation study, not a current dependency recommendation.

- **C1:** Syntax objects carry bindings and both shared and phase-specific scope sets. Identifier resolution filters candidate bindings by scope inclusion and follows aliases; scope addition and removal recursively handle delimiters. See [syntax.js](https://github.com/sweet-js/sweet-core/blob/master/src/syntax.js). The source also exposes unfinished areas, so the selection is not a claim of complete semantic coverage.
- **C2:** Macro authors receive a reusable context with iteration, saved positions, delimiter contexts, and expansion of specific grammar categories such as expressions and statements. [macro-context.js](https://github.com/sweet-js/sweet-core/blob/master/src/macro-context.js) shows how this interface delegates to the enforester instead of requiring each macro to implement a parser.

### 4. [Technologicat/mcpyrate](https://github.com/Technologicat/mcpyrate)

**Language/role:** Python; an AST macro expander, dialect framework, and multiphase compiler.

Study how macros can be integrated with an existing language's import system, including the difficult case of defining and using a macro in the same module.

- **C1:** The compiler extracts phases in descending order, temporarily reifies higher phases under the module's name in `sys.modules`, and restores the original module entry before handing compiled code back to Python. The [compiler manual](https://github.com/Technologicat/mcpyrate/blob/master/doc/compiler.md) specifies ordering, invalid placements of phase declarations, and the limitation on phases introduced by dialect transformations.
- **C2:** The same documented pipeline separates source transformations, AST transformations, macro expansion, and AST postprocessing. Its runtime `expand`, `compile`, `run`, and module-creation interfaces allow applications beyond import-time macros. The compiler manual is the main entry point for this reusable architecture.

### 5. [hylang/hy](https://github.com/hylang/hy)

**Language/role:** Python and Hy; a Lisp embedded in Python, with compile-time and reader macros.

Study an explicitly pragmatic macro model where authors must understand name capture, phase ordering, and Python interoperability.

- **C1:** The [macro manual](https://github.com/hylang/hy/blob/master/docs/macros.rst) develops concrete failures from accidental shadowing, evaluating an argument twice, and referencing a helper that exists only at runtime. It explains `gensym`, one-shot imports, and `eval-and-compile`; these are author responsibilities, not a claim that Hy automatically guarantees hygiene.
- **C2:** Regular macros transform parsed models, while reader macros extend parsing through the reader object. This supports both control-flow abstractions and new literal syntax using the same language implementation.
- **C4:** The [release history](https://github.com/hylang/hy/blob/master/NEWS.rst) records, for example, reader-macro and Python compatibility changes in 2023 and import, scoping, and compilation fixes in 2026. It explicitly distinguishes removals, breaking changes, and bug fixes.

### 6. [nim-lang/Nim](https://github.com/nim-lang/Nim)

**Language/role:** Nim; specifically the compiler-backed `lib/core/macros.nim` API.

Study a compiled language's direct interface between user metaprograms and compiler AST nodes, types, and resolved symbols. The whole compiler repository counts once.

- **C1:** `bindSym` distinguishes closed and open overload choices, while `genSym` creates unique symbols that must appear in a declaration context. Node-kind and child-count checks report errors against the offending AST. These semantics and their implementation are in [macros.nim](https://github.com/nim-lang/Nim/blob/devel/lib/core/macros.nim).
- **C2:** The same module exposes constructors, structural inspection, source locations, symbol binding, type information, and macro expansion access. It is a reusable compiler interface for language extensions rather than a collection of unrelated code generators. The compiler-magic annotations also provide a concrete route from the public API into compiler implementation.

### 7. [elixir-lang/elixir](https://github.com/elixir-lang/elixir)

**Language/role:** Elixir and Erlang; the `Macro` API and Erlang quotation implementation within the language monorepo.

Study how a compact AST representation supports a rich macro interface while retaining the metadata necessary for hygiene and useful diagnostics.

- **C1:** Variables are distinguished using names together with context or hygiene counters. The quotation engine tracks nested quote/unquote levels, alias/import hygiene, and propagation of call-site metadata. [elixir_quote.erl](https://github.com/elixir-lang/elixir/blob/main/lib/elixir/src/elixir_quote.erl) makes these mechanisms inspectable.
- **C2:** [Macro's implementation and API documentation](https://github.com/elixir-lang/elixir/blob/main/lib/elixir/lib/macro.ex) define macro input/output representations and provide traversal, querying, and transformation operations. The distinction between building AST and evaluating code is explicit, making this a useful example of a language-level metaprogramming API boundary.

### 8. [terralang/terra](https://github.com/terralang/terra)

**Language/role:** Lua, Terra, and C++; a low-level staged language generated and controlled from Lua.

Study staging where a dynamic host constructs typed low-level programs, rather than only rewriting its own syntax.

- **C1:** Quotations retain lexical variable identity when moved into other code. Explicit symbol objects allow definitions and uses to be connected across quotations. The [language guide](https://github.com/terralang/terra/blob/master/docs/getting-started.md) explains these binding rules and demonstrates the separate danger of a macro evaluating an argument twice.
- **C2:** Quotes, escapes, symbols, and macros compose into general code-generation facilities; Lua can generate families of specialized Terra functions. The same guide covers C interoperability, embedding, and generated object files, connecting metaprogramming abstractions to practical systems-programming outputs.

## Rust procedural-macro infrastructure

These four repositories occupy different layers: parsing, token generation, compiler-independent token representation, and declarative input validation. They are independent implementations, not forks or duplicate listings of a monorepo.

### 9. [dtolnay/syn](https://github.com/dtolnay/syn)

**Language/role:** Rust; token-stream parsing and syntax-tree infrastructure for procedural macros.

Study how ergonomic parser combinators can expose precise errors while maintaining low-level cursor and lifetime invariants.

- **C1:** `ParseBuffer` and `StepCursor` document the covariance/invariance conditions behind internal lifetime conversions. Parser entry points reject leftover tokens; context-sensitive choices such as outer versus inner attributes and optional trailing punctuation are deliberately not hidden behind an ambiguous default parser. See [parse.rs](https://github.com/dtolnay/syn/blob/master/src/parse.rs).
- **C2:** `Parse`, `Parser`, `ParseStream`, and token-level stepping support both ordinary Rust syntax and custom macro grammars.
- **C3:** The same source explains cheap cursor copies and bounded speculative parsing, warning against parsing an unbounded expression twice through a fork. This connects performance advice directly to the parser architecture.

### 10. [dtolnay/quote](https://github.com/dtolnay/quote)

**Language/role:** Rust; reusable quasiquotation and token generation.

Study the machinery behind interpolating syntax fragments and repetitions while keeping source spans meaningful.

- **C1:** Interpolated tokens preserve their existing spans, whereas tokens written inside the quotation use call-site spans unless overridden. [The public implementation and documentation](https://github.com/dtolnay/quote/blob/master/src/lib.rs) specify this distinction. [runtime.rs](https://github.com/dtolnay/quote/blob/master/src/runtime.rs) additionally checks that repetitions contain an iterable value and separates extension traits to avoid ambiguity.
- **C2:** `ToTokens` lets custom data types participate in quotation, and generated token streams can themselves be interpolated into larger quotations. This supports composable code generators both inside procedural macros and in ordinary Rust programs.

### 11. [dtolnay/proc-macro2](https://github.com/dtolnay/proc-macro2)

**Language/role:** Rust; compiler-backed and fallback token APIs for metaprogramming libraries.

Study an abstraction that makes compiler-bound functionality available to tests and ordinary programs without pretending every compiler property is portable.

- **C1:** [The API documentation](https://github.com/dtolnay/proc-macro2/blob/master/src/lib.rs) exposes thread-local restrictions and distinguishes stable functionality from explicitly semver-exempt compiler APIs. [wrapper.rs](https://github.com/dtolnay/proc-macro2/blob/master/src/wrapper.rs) handles compiler/fallback mismatches and a compiler lexer panic case.
- **C2:** The compiler and fallback implementations share token-stream abstractions, enabling libraries such as Syn and Quote to work in procedural macros, unit tests, and build scripts.
- **C3:** `DeferredTokenStream` batches appended tokens before invoking the compiler's extension operation, with the motivating compiler issue recorded beside the implementation.

### 12. [TedDriggs/darling](https://github.com/TedDriggs/darling)

**Language/role:** Rust; declarative attribute parsing and validation for procedural-macro authors.

Study diagnostics as part of framework design, particularly how to preserve multiple independent failures instead of forcing repeated compiler runs.

- **C1:** Errors form a nonempty, potentially hierarchical collection with spans, field locations, and suggestions. The [error subsystem](https://github.com/TedDriggs/darling/blob/master/core/src/error/mod.rs) explains why validation should accumulate errors and how conversion to poorer error types can lose information.
- **C2:** [The trait and derive interface](https://github.com/TedDriggs/darling/blob/master/README.md) covers metadata, complete derive inputs, fields, variants, and general attributes. Defaults, forwarding, and shape validation let many independent macro crates share a parsing model while supplying their own semantic checks.

## Typed AST transformation, derivation, and compiler extension frameworks

### 13. [ocaml-ppx/ppxlib](https://github.com/ocaml-ppx/ppxlib)

**Language/role:** OCaml; infrastructure for PPX AST rewriters and derived code.

Study a shared transformation driver that addresses both composition between plugins and changes in the host compiler's AST.

- **C1:** The [driver design](https://github.com/ocaml-ppx/ppxlib/blob/main/doc/driver.mld) distinguishes local, context-free transformations from global rewrites and gives the former defined composition semantics. It also rejects multiple transformations registered for its exclusive preprocessing phase.
- **C2:** Derivers, extension-node expanders, linting, instrumentation, and standalone or compiler-driven execution share the driver. The [compatibility design](https://github.com/ocaml-ppx/ppxlib/blob/main/doc/compatibility.mld) converts compiler ASTs into a chosen Ppxlib AST and back, limiting the version-specific surface exposed to plugin authors.
- **C3:** Context-free transformations share a traversal phase, avoiding the repeated whole-tree work of independent global rewriters. This is a specific architectural performance mechanism, not a numerical speed claim.

### 14. [glguy/th-abstraction](https://github.com/glguy/th-abstraction)

**Language/role:** Haskell; normalization and compatibility infrastructure over Template Haskell's reified datatype information.

Study the subtle boundary between a compiler's syntactic representation of a type declaration and the semantic information needed by generic deriving libraries.

- **C1:** GADT constructors are normalized into existential variables and equality constraints. Bound datatype variables are distinguished from applied datatype arguments, including polykinded and data-family cases. [Datatype.hs](https://github.com/glguy/th-abstraction/blob/master/src/Language/Haskell/TH/Datatype.hs) documents the representation and implements normalization, substitution, and related utilities.
- **C2:** A common `DatatypeInfo`/`ConstructorInfo` model lets downstream generators handle ordinary datatypes, newtypes, and more complex declarations without repeating compiler-specific inspection logic.
- **C4:** The [changelog](https://github.com/glguy/th-abstraction/blob/master/ChangeLog.md) records GHC 9.8 binder adaptation in 2023, return-kind and GADT fixes in 2024, and GHC 9.14 support in 2026, including concrete migration guidance.

### 15. [scalameta/scalameta](https://github.com/scalameta/scalameta)

**Language/role:** Scala; syntax trees, quasiquotes, and program-transformation infrastructure. The relevant subsystem is `scalameta` trees and quasiquotes, not the entire SemanticDB toolchain.

Study a metaprogramming library that represents source programs and their syntax dialects explicitly. This entry concerns its current transformation API, not an assertion that it remains the original proposed Scala macro system.

- **C1:** Parsing depends on both the expected tree category and the selected dialect; an expression is not automatically a valid source file, and script-like top-level statements require the appropriate dialect. The [tree guide](https://github.com/scalameta/scalameta/blob/main/docs/trees/guide.md) demonstrates these distinctions, source-positioned errors, and lossless source representation.
- **C2:** Parsing, construction, matching, traversal, and transformation share the tree model. The [quasiquote specification](https://github.com/scalameta/scalameta/blob/main/docs/trees/quasiquotes.md) maps expression, type, declaration, and pattern constructs into reusable construction/extraction syntax, with explicit dialect restrictions and unsupported cases.

### 16. [milessabin/shapeless](https://github.com/milessabin/shapeless)

**Language/role:** Scala; the Scala 2 Shapeless generic-programming and macro-derivation implementation.

Study how compiler macros and dependent types turn products and sums into reusable generic representations.

- **C1:** The [Generic implementation](https://github.com/milessabin/shapeless/blob/main/core/shared/src/main/scala/shapeless/generic.scala) handles subtype discovery and rejects inaccessible subtypes, unstable prefixes, and unsupported product/sum shapes. Its `Aux` encoding preserves the crucial relationship between an input type and its representation during implicit search.
- **C2:** `Generic` converts case-class-like products into heterogeneous lists and sealed sums into coproducts, allowing generic operations to share one representation. The [project overview](https://github.com/milessabin/shapeless/blob/main/README.md) provides the broader type-class/dependent-type context and links feature and migration documentation.

This entry is specifically the implementation in this repository, not a duplicate entry for a differently implemented later-generation Shapeless project.

### 17. [manifold-systems/manifold](https://github.com/manifold-systems/manifold)

**Language/role:** Java; compiler plugins and type-provider infrastructure. Relevant subsystems are Manifold Core and Java Extensions, counted together as one monorepo.

Study metaprogramming integrated with type resolution: schemas and other resources can supply Java types as the compiler requests them.

- **C2:** [The core architecture](https://github.com/manifold-systems/manifold/blob/master/manifold-core-parent/manifold/README.md) defines an SPI with primary, partial, and supplementary type contributors. Resource-backed type definitions and extensions can therefore cooperate in producing a type. [The extension framework](https://github.com/manifold-systems/manifold/blob/master/manifold-deps-parent/manifold-ext/README.md) demonstrates applications including extension methods and structural interfaces.
- **C3:** Type generation follows a demand-driven compiler-resolution path and supports incremental operation, rather than requiring every resource to be regenerated up front. The core document explains the pull model and common integration surface for compiler and IDE tooling. Its architectural mechanism is useful to study; the report does not adopt the document's unmeasured claims of optimal build times.

## Julia macro-authoring and pattern-compilation libraries

### 18. [FluxML/MacroTools.jl](https://github.com/FluxML/MacroTools.jl)

**Language/role:** Julia; reusable expression matching, traversal, quotation, and normalization tools.

Study a compact infrastructure library that concentrates difficult AST details so downstream macros can be expressed as recognizable transformations.

- **C1:** [The utilities implementation](https://github.com/FluxML/MacroTools.jl/blob/master/src/utils.jl) distinguishes quotation-site line numbers from interpolated-expression locations and preserves the positional structure required by macro calls when removing line metadata. These details affect diagnostics and AST validity.
- **C2:** [Pattern matching and expression walking](https://github.com/FluxML/MacroTools.jl/blob/master/docs/src/pattern-matching.md) combine captures, sequence captures, alternatives, and preorder/postorder transformations. The documentation explains normalization of quoted symbols and the possibility of nontermination when a preorder rewrite repeatedly reintroduces its own input pattern.

### 19. [thautwarm/MLStyle.jl](https://github.com/thautwarm/MLStyle.jl)

**Language/role:** Julia; extensible pattern matching and metaprogramming facilities that compile patterns into code.

Study the boundary between a user-extensible pattern language and the generated Julia program that implements it.

- **C1:** The [pattern semantics](https://github.com/thautwarm/MLStyle.jl/blob/main/docs/syntax/pattern.md) specify first-match ordering, failure for nonexhaustive matches, literal-equality distinctions, captures, guards, and alternatives. These are observable semantics a pattern compiler must preserve.
- **C2:** [MatchImpl.jl](https://github.com/thautwarm/MLStyle.jl/blob/main/src/MatchImpl.jl) exposes extension hooks such as `pattern_uncall`, `pattern_unref`, and `pattern_unmacrocall`, translates quoted expressions, and binds pattern interpretation to a module. Custom patterns can reuse the matching infrastructure instead of each providing a separate matcher.

## C and C++ compile-time metaprogramming

### 20. [boostorg/hana](https://github.com/boostorg/hana)

**Language/role:** C++14; heterogeneous and compile-time programming over both types and values.

Study the tradeoff between a broad value-oriented generic interface and the compiler work required to implement it.

- **C2:** [The implementation-oriented manual](https://github.com/boostorg/hana/blob/master/doc/tutorial.hpp) explains representing types as objects and the tag-dispatch architecture: `tag_of` selects a family, public algorithms dispatch through that tag, and specialized implementation templates supply behavior. This lets different container families participate in common algorithms.
- **C3:** The manual discusses compile-time and runtime performance separately, including the cost of supporting runtime values and reducing preprocessor dependencies. The [repository's benchmark organization](https://github.com/boostorg/hana/blob/master/README.md) describes generating C++ benchmark programs and collecting compilation and execution measurements. No comparative speed ratio is assumed here.

The project states that releases now follow the Boost release process; an old standalone GitHub release date should not by itself be read as an abandonment signal.

### 21. [boostorg/mp11](https://github.com/boostorg/mp11)

**Language/role:** C++11 and later; general type-list metaprogramming through alias templates and parameter packs.

Study how a small uniform representation can replace elaborate dedicated sequence protocols.

- **C2:** [The design overview](https://github.com/boostorg/mp11/blob/develop/doc/mp11/overview.adoc) treats algorithms as `F<T...>` and lists as `L<T...>`, permitting existing templates such as tuples and variants to participate without requiring a special container base class.
- **C1:** That abstraction has real shape constraints: fixed-arity templates cannot accept operations that resize them. The [revision history](https://github.com/boostorg/mp11/blob/develop/doc/mp11/changelog.adoc) documents fixed-size-list corrections and a regression involving non-integral sequence values, making these boundaries concrete.
- **C3:** The same history records targeted compilation improvements for large `mp_with_index<N>` instantiations and improvements to multiple algorithms. These are evidence that compilation cost is addressed, without asserting a benchmark result for a particular workload.

### 22. [kvasir-io/mpl](https://github.com/kvasir-io/mpl)

**Language/role:** C++; continuation-style template metaprogramming, distinct from the broader Kvasir embedded-hardware repository.

Study how changing a metaprogramming library's calling convention influences algorithm composition and compiler workload.

- **C2:** [The design overview](https://github.com/kvasir-io/mpl/blob/development/README.md) establishes continuations as the public interface and describes composing algorithms and lambdas without forcing an intermediate list representation at every boundary.
- **C3:** Compilation speed is an explicit design constraint. [The sorting implementation](https://github.com/kvasir-io/mpl/blob/development/src/kvasir/mpl/algorithm/sort.hpp) exposes specialized small sorts, chunked merge operations, and implementation/public-interface separation. Interpreting these specializations as attempts to control instantiation workload is an engineering inference supported by the stated design goal; no current cross-library speed ranking is claimed.

### 23. [boostorg/preprocessor](https://github.com/boostorg/preprocessor)

**Language/role:** C/C++ preprocessor macros; reusable repetition, control-flow, and data-manipulation infrastructure.

Study how a constrained token-expansion machine can support nested reusable operations despite forbidding ordinary recursive macro expansion.

- **C1:** The [reentrancy design](https://github.com/boostorg/preprocessor/blob/develop/doc/topics/reentrancy.html) walks through a nested concatenation failure and explains why expansion-state tracking is necessary. Equivalent macro families and state parameters provide controlled reentry into `WHILE`, `FOR`, and `REPEAT` operations.
- **C2:** The same design turns those low-level mechanisms into reusable control structures, permitting higher-level operations to compose without every client inventing its own recursion simulation. This is an unusually direct example of abstraction design constrained by the host language's expansion rules.

Here “reentrancy” means nested preprocessor expansion, not runtime multithreading.

### 24. [hirrolot/metalang99](https://github.com/hirrolot/metalang99)

**Language/role:** C99 preprocessor; an interpreted functional metalanguage implemented with macros.

Study a deliberately layered interpreter built on top of a very limited host execution model.

- **C2:** The [architecture document](https://github.com/hirrolot/metalang99/blob/master/ARCHITECTURE.md) separates a continuation-passing evaluator, the underlying macro-recursion engine, and a standard library implemented in the metalanguage. This supports reusable metaprograms rather than only isolated preprocessor tricks.
- **C3:** [The optimization guide](https://github.com/hirrolot/metalang99/blob/master/optimization_tips.md) relates preprocessing cost to reduction steps and gives concrete alternatives: unevaluated calls, simpler tuple/variadic representations, and specialized library operations.
- **C1:** That guide also explains why bypassing the evaluator can break expansion correctness through disabled recursive expansion, unexpected commas, or stringification/token-pasting behavior. The optimization boundary is therefore explicitly tied to semantic constraints.

## Coverage, search process, and limitations

Live discovery used more than six distinct formulations, including hygienic Racket expanders; JavaScript macro parsing; Rust procedural-macro layers; Python import-time macros; C++ Hana/Mp11/Metal/Kvasir-style libraries; C preprocessor interpreters; Scala quasiquotes and derivation; OCaml PPX infrastructure; Haskell datatype reification; Julia AST tooling and extensible patterns; Nim and Elixir compiler macros; Lua-hosted staging; Scheme/Common Lisp/Fennel macros; MetaOCaml-style staging; and Java compiler extensions. Later searches mostly repeated established candidates or produced narrower applications, educational experiments, or projects outside this category; Java type providers supplied the last distinct retained architecture.

Every retained canonical repository URL was checked using GitHub repository metadata. The report also opens and reads additional primary documentation or source for every entry; directory listings and search snippets were used to locate material, not as substitutes for implementation evidence. Source links use verified default branches and may evolve after the research date. The search did not clone repositories, install dependencies, execute candidate code, contact maintainers, or inspect private data.

Important selection boundaries:

- General parsers, ordinary application code that merely uses macros, awesome-lists, tutorials, and one-off macro exercises were excluded. Scalameta and Syn are included specifically because of their reusable metaprogramming interfaces.
- Several additional C++ libraries, including Metal, older MPL variants, and Fatal, surfaced in discovery. They were not needed to duplicate the selected representation families; their omission is not a negative quality judgment.
- MetaOCaml-related searches surfaced a bibliography, experiments, and specialized staged libraries. This report does not substitute an unofficial compiler fork for a verified canonical GitHub implementation. Typed staging is represented by Terra, with other forms of staged compilation represented by mcpyrate.
- [Fennel's README](https://github.com/bakpakin/Fennel/blob/main/README.md) directs source cloning to SourceHut and issue reporting to other services. It was not retained because continuing official-mirror status was not established in this pass. No retained repository is presented as an unofficial mirror.
- Common Lisp-specific infrastructure is less represented than Scheme/Racket, Rust, and C++; the selection does not claim ecosystem completeness. Runtime object-model reflection and bytecode instrumentation are outside the chosen compile-time emphasis.
- Sweet.js is explicitly archived, syntax-spec is explicitly a prototype, and Shapeless is scoped to the Scala 2 implementation examined. Other entries receive no blanket promise of current maintenance. C4 is claimed only where dated compatibility and correction history was actually inspected.
- Performance observations identify mechanisms and documented engineering priorities. Benchmarks were not rerun, and correctness criteria indicate worthwhile invariants to study rather than independently proven correctness.
