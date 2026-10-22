# Code formatters and source rewriting tools

Research date: **2026-10-09**.

This report selects **26 GitHub repositories** implementing source formatters, reusable printing engines, lossless code transformation libraries, or structural and semantic rewriting systems. It covers whole-file normalization, preservation of untouched source, language migrations, semantic patches, and formatting of templated code. Compiler monorepos are included only for an identified formatting subsystem. The selection is intended to help experienced engineers choose codebases to study; it is not a ranking or a claim that every component is uniformly exemplary.

Criteria used below:

- **C1 — Correctness:** substantial invariants, semantic preservation, adversarial input handling, or difficult failure modes.
- **C2 — Abstractions:** substantial reusable representations and interfaces supporting multiple constructs, transformations, languages, or integration contexts.
- **C3 — Performance:** concrete measures addressing computational or resource constraints, within an understandable architecture.
- **C4 — Evolution:** documented development over years together with compatibility, testing, or complexity-management practices.

Canonical repository names, default branches, and archive flags were checked through the GitHub API. None of the retained repositories was marked archived at the time of research. This does not imply equal maintenance activity. Coccinelle is explicitly an official mirror; zprint's latest recorded release in the inspected changelog is from May 2025. Implementation observations below come from opened documentation and source files; statements about what an engineer can learn are grounded assessments of those materials.

## Reusable formatting engines

### 1. [prettier/prettier](https://github.com/prettier/prettier)

**Language / role:** JavaScript; a formatter and language-plugin platform for web languages and structured documents. Study the separation between syntax-specific printing and the common document-layout interpreter.

- **C1:** The printer distinguishes flat and broken groups, conditional breaks, line suffixes, and suffix boundaries. Its fit calculation accounts for these states rather than merely counting characters, making interactions between trailing content and nested layouts a concrete correctness problem. Start with the [document printer](https://github.com/prettier/prettier/blob/main/src/document/printer/printer.js).
- **C2:** Parsers produce ASTs, language printers produce `Doc` values, and a shared renderer chooses the layout. The plugin interface also separates comment attachment, embedded-language formatting, preprocessing, and traversal. Prettier's built-in languages use that same interface, demonstrating substantial reuse rather than a nominal extension hook. See the [plugin architecture and printing process](https://prettier.io/docs/plugins).

### 2. [biomejs/biome](https://github.com/biomejs/biome)

**Language / role:** Rust; integrated web tooling, with `biome_formatter` and the language-specific formatter crates as the relevant subsystems. Study how a shared syntax infrastructure supports formatting while a user is editing incomplete code.

- **C1:** The parser preserves trivia in a concrete syntax tree and represents damaged syntax using missing fields and bogus nodes. Those distinctions prevent consumers from treating malformed syntax as ordinary valid nodes. The [architecture documentation](https://biomejs.dev/internals/architecture/) explains the red/green tree representation, trivia ownership, and recovery examples.
- **C2:** `FormatElement` is a common formatting IR; `Format`, `FormatRule`, and wrappers for externally owned types separate representation, reusable rules, and rendering. The [formatter crate](https://github.com/biomejs/biome/blob/main/crates/biome_formatter/src/lib.rs) is a useful entry into the trait design and builder macros. The architecture page's formatter section is unfinished, so the implementation is the stronger source for this claim.

### 3. [dprint/dprint](https://github.com/dprint/dprint)

**Language / role:** Rust; a formatting platform and reusable printing core serving independently developed language plugins. Study both plugin lifecycle boundaries and a layout engine with deferred decisions.

- **C1:** Plugin contracts distinguish ordinary formatting errors from critical failures that require recreating a plugin, expose cancellation, and cap traversal of potentially cyclic error-source chains. These are explicit failure-containment mechanisms in the [plugin handler interfaces](https://github.com/dprint/dprint/blob/main/crates/core/src/plugins/plugin_handler.rs).
- **C2:** The same contracts carry configuration and formatting requests across different plugins, while the core printer consumes shared print items rather than language syntax.
- **C3:** The [printer implementation](https://github.com/dprint/dprint/blob/main/crates/core/src/formatting/printer.rs) uses arena allocation, specialized lookup collections, saved writer states, and look-ahead resolution. It also integrates protection against infinite reevaluation. This offers a concrete study of the cost and termination of revisiting layout choices; no benchmark multiplier is assumed here.

## Python formatting: different correctness and layout strategies

### 4. [psf/black](https://github.com/psf/black)

**Language / role:** Python; opinionated source formatting. Study the engineering around detecting unsafe output and controlling changes to a widely shared style.

- **C1:** `assert_equivalent` compares normalized input and output ASTs; `assert_stable` checks whether another formatting pass changes the output. Their error paths preserve diagnostic material. The implementation also documents that the stability check is skipped for selected line ranges because range remapping has troublesome edge cases. See the [formatting and safety entry points](https://github.com/psf/black/blob/main/src/black/__init__.py).
- **C4:** The [changelog](https://github.com/psf/black/blob/main/CHANGES.md) records evolution from the first 2018 release through 2026, including syntax support and correctness regressions. The [stability policy](https://github.com/psf/black/blob/main/docs/the_black_code_style/index.md) separates same-calendar-year stable formatting from preview and unstable experimentation. These are compatibility mechanisms, not simply evidence that the repository is old.

### 5. [astral-sh/ruff](https://github.com/astral-sh/ruff)

**Language / role:** Rust; Python tooling monorepo, specifically `ruff_python_formatter` and its common formatting infrastructure. Study a Python-specific implementation built on a reusable document formatter, with explicit compatibility boundaries.

- **C1:** Node formatting divides comments into leading, dangling, and trailing categories; a debug assertion requires dangling comments to have been handled explicitly. Source positions are emitted for appropriate range-formatting targets, connecting printing to edit boundaries. See [the formatter entry points and `FormatNodeRule`](https://github.com/astral-sh/ruff/blob/main/crates/ruff_python_formatter/src/lib.rs).
- **C2:** Language-specific node rules use a shared context, formatting traits, builders, and printer. Parsing, AST formatting, and final printing have distinct interfaces and error types. The [formatter documentation](https://github.com/astral-sh/ruff/blob/main/docs/formatter.md) explains Black compatibility, preview changes, and interactions with lint fixes.

Ruff acknowledges Rome-derived printing infrastructure. It is retained alongside Biome because its Python AST, comments, style rules, and integration constitute a substantive separate implementation, rather than a redistributed fork.

### 6. [google/yapf](https://github.com/google/yapf)

**Language / role:** Python; configurable Python formatter using cost-based layout search. Study how formatting becomes a graph-search problem and where practical heuristics alter that search.

- **C1:** The project's [algorithm explanation](https://github.com/google/yapf#algorithm-design) describes logical lines and weighted split decisions. Its stated constraint against changing the token stream, including adding parentheses, exposes a meaningful tradeoff between prettier output and preserving Python behavior.
- **C3:** `_AnalyzeSolutionSpace` implements a Dijkstra-style search with a priority queue and visited states. It avoids repeated hashing in the common path and relaxes stack comparison after the search becomes large. If no solution is found, it declines that reformatting. Read the [reformatter](https://github.com/google/yapf/blob/main/yapf/yapflib/reformatter.py) to examine state equivalence, deterministic tie-breaking, and the practical limits of optimization. The README still describes the project as beta; inclusion is not a stability endorsement.

## Compiler-oriented and functional-language formatters

### 7. [rust-lang/rustfmt](https://github.com/rust-lang/rustfmt)

**Language / role:** Rust; Rust source formatting integrated with the compiler ecosystem. Study the mismatch between compiler ASTs and the information required to reproduce source faithfully.

- **C1:** Rustfmt works before macro expansion, so macro arguments remain tokens, and ordinary comments must often be recovered from gaps between spans. Its developer guide explains these limitations, fallback behavior, width underflow checks, source/target fixtures, and style-edition gating. See [the implementation guide](https://github.com/rust-lang/rustfmt/blob/main/Contributing.md).
- **C2:** `Rewrite` formats AST elements against a `Shape` and `RewriteContext`, with structured outcomes for skipped formatting, width limits, and macro failures. This is a reusable contract across many Rust constructs, not just one formatting function. Start with [the rewrite abstraction](https://github.com/rust-lang/rustfmt/blob/main/src/rewrite.rs), then follow the guide's discussion of shared list formatting.

### 8. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language / role:** C++; **clang-format**, principally `clang/lib/Format`, within the LLVM monorepo. The compiler and other LLVM tools are not separate entries here. Study token annotation, unwrapped lines, indentation state, and layout optimization.

- **C1:** The [unwrapped-line formatter](https://github.com/llvm/llvm-project/blob/main/clang/lib/Format/UnwrappedLineFormatter.cpp) tracks indentation through modified and unmodified lines, treats preprocessor and macro-body indentation separately, and refuses unsafe line merges involving trailing line comments. These details show why formatting C-family input is more complicated than printing an AST.
- **C3:** The same file implements a Dijkstra-style search over `LineState`, uses deterministic ordering for equal-cost states, and caches dry-run penalties keyed by a line collection and indentation. It makes a useful comparison with YAPF: related search ideas appear in a different language and a more extensive token-formatting pipeline.

### 9. [google/google-java-format](https://github.com/google/google-java-format)

**Language / role:** Java; Java source formatter built around javac parsing. Study a compact document algebra and the distinction between constructing formatting operations and resolving line breaks.

- **C2:** `JavaInputAstVisitor` emits operations through `OpsBuilder`; `DocBuilder` converts them into a tree of levels, tokens, spaces, and breaks. Unified breaks move together, while independent breaks can fill a level separately. The [document implementation](https://github.com/google/google-java-format/blob/master/core/src/main/java/com/google/googlejavaformat/Doc.java) describes the pipeline and implements its reusable representation.
- **C3:** Document width, flattened text, and token ranges are memoized. Break computation is a separate phase from writing the output, allowing expensive layout properties to be reused during nested decisions. These are inspectable performance mechanisms rather than an inferred benefit of the implementation language. The [repository documentation](https://github.com/google/google-java-format#using-the-formatter) also identifies the javac module boundary and library API.

### 10. [scalameta/scalafmt](https://github.com/scalameta/scalafmt)

**Language / role:** Scala; Scala formatter using best-first search. Study how to keep a combinatorial layout problem tractable while retaining explicit decision and state representations.

- **C2:** A `Router` precomputes possible `Split` values for tokens; `State`, ordering, policies, and a writer supply separate parts of the search machinery. The [best-first search implementation](https://github.com/scalameta/scalafmt/blob/main/scalafmt-core/shared/src/main/scala/org/scalafmt/internal/BestFirstSearch.scala) exposes the connections clearly.
- **C3:** The code identifies nested blocks inside wide argument clauses as a source of combinatorial growth, extracts suitable blocks as subproblems, memoizes results, and tracks explored states. Comments explain the conditions needed to keep memo lookups sound. It also uses primitive-key maps and avoids per-state tuple allocation. This is unusually useful material for studying both algorithmic pruning and allocation costs in one place. The [project overview](https://github.com/scalameta/scalafmt/blob/main/readme.md) establishes its CLI, library, and editor-facing context.

### 11. [ocaml-ppx/ocamlformat](https://github.com/ocaml-ppx/ocamlformat)

**Language / role:** OCaml; configurable OCaml formatter with library and RPC integration. Study formatting as a checked transformation that must reach a stable result.

- **C1:** The [translation-unit implementation](https://github.com/ocaml-ppx/ocamlformat/blob/main/lib/Translation_unit.ml) reparses generated output, detects AST changes, checks dropped or changed comments, handles misplaced documentation comments, and reports failure to stabilize after repeated formatting. These are separate error categories with diagnostic support.
- **C2:** The [translation-unit interface](https://github.com/ocaml-ppx/ocamlformat/blob/main/lib/Translation_unit.mli) accepts syntax kinds, named source, and configuration and returns structured success or failure. Internally it separates standard and extended AST views and parsing with comments; the repository also exposes an RPC service for other tools. The interesting abstraction is a common checked fragment-formatting pipeline, rather than a set of unrelated command-line style switches.

### 12. [tweag/ormolu](https://github.com/tweag/ormolu)

**Language / role:** Haskell; Haskell formatter using GHC parsing. Study how layout-sensitive syntax, operator fixities, and comment placement affect the validation boundary.

- **C1:** The [current implementation](https://github.com/tweag/ormolu/blob/master/src/Ormolu.hs) checks comment occurrence and order, reparses output for AST comparison, and can check idempotence. It explains why an AST comparison alone does not cover every comment invariant. These checks can be disabled or selected through configuration; they should not be described as an unconditional semantic proof.
- **C2:** The same module defines the stable library boundary for text, file, and stdin formatting, regions, Cabal information, fixity overrides, and module re-exports. The [repository documentation](https://github.com/tweag/ormolu#language-extensions-dependencies-and-fixities) explains how extensions and dependencies inform parsing and operator interpretation.

The inspected [design record](https://github.com/tweag/ormolu/blob/master/DESIGN.md) explicitly says it is an early, no-longer-updated document. Its linear-time aspirations and CPP discussion are historical context, not claims about the current implementation's guarantees.

### 13. [dart-lang/dart_style](https://github.com/dart-lang/dart_style)

**Language / role:** Dart; implementation behind `dart format`. Study a modern layout solver with a deliberately bounded search and compatibility across language-dependent formatting styles.

- **C2:** The [solver](https://github.com/dart-lang/dart_style/blob/main/lib/src/back_end/solver.dart) operates on trees of `Piece` objects and candidate `Solution` states. This separates language-specific piece construction from a reusable optimization backend.
- **C3:** It explores lower-cost solutions first, expands pieces associated with the first problematic line, solves sufficiently isolated subtrees separately, and caches those results. A fixed attempt limit prevents pathological search; the fallback is the best solution found, so global optimality is not promised for every input.

The [test-format documentation](https://github.com/dart-lang/dart_style/blob/main/test/README.md) is another valuable entry point: fixtures can specify different expected outputs and unsupported syntax ranges for different Dart language versions. This makes compatibility behavior inspectable instead of relying only on snapshots of the latest style.

## Specialist languages and configurable token pipelines

### 14. [JohnnyMorganz/StyLua](https://github.com/JohnnyMorganz/StyLua)

**Language / role:** Rust; Lua and Luau formatter. Study dialect ambiguity and optional verification within a reusable formatting library.

- **C1:** Lua label syntax and Luau type assertions can conflict when dialects are combined. The tool exposes explicit syntax selection. Its optional `--verify` reparses output and compares ASTs, while the [README](https://github.com/JohnnyMorganz/StyLua#--verify-verifying-formatting-output) candidly acknowledges possible false positives and negatives.
- **C2:** The [library implementation](https://github.com/JohnnyMorganz/StyLua/blob/main/src/lib.rs) accepts either source text or an existing AST, with a shared configuration, range, and verification contract. The same implementation has a WebAssembly entry point and supports a separate require-sorting phase. This is a useful example of sharing transformation machinery across a CLI, embedding API, and browser-oriented interface.

### 15. [mvdan/sh](https://github.com/mvdan/sh)

**Language / role:** Go; shell parser, formatter, and interpreter, with **shfmt and the `syntax` package** as the relevant subsystems. Study a reusable printer where quoting, line continuation, and here-documents have behavioral consequences.

- **C1:** The [printer](https://github.com/mvdan/sh/blob/master/syntax/printer.go) queues here-documents, handles tab-indented here-document bodies specially, flushes pending comments, and tracks required versus optional newlines. These states are necessary to retain shell meaning across layout changes.
- **C2:** A common syntax model and configurable `Printer` can print files, statements, commands, and words to an `io.Writer`. The [repository's caveats](https://github.com/mvdan/sh#caveats) explain deliberate parser tradeoffs, including rejecting an ambiguity whose backtracking would complicate streaming. They also discuss why partial-file formatting and additional interacting options are constrained. The interpreter is not the basis for this entry's qualification.

### 16. [kkinnear/zprint](https://github.com/kkinnear/zprint)

**Language / role:** Clojure/ClojureScript; formatter for Clojure source and runtime s-expressions. Study a formatter that shares machinery between parsed source and live data, with extensible treatment of language forms.

- **C2:** The [traversal abstraction](https://github.com/kkinnear/zprint/blob/main/src/zprint/zfns.cljc) supplies operations for either zippers or s-expressions. The [reference manual](https://github.com/kkinnear/zprint/blob/main/doc/reference.md) explains function classifications and per-form options, allowing user-defined forms and macros to receive appropriate layouts without rewriting the whole printer.
- **C4:** The [changelog](https://github.com/kkinnear/zprint/blob/main/CHANGELOG.md) spans 2016–2025 and explains compatibility-sensitive changes, including the tagged-literal rewrite, changed indentation interpretation, and the decision to accept a narrowly scoped behavior change instead of adding another configuration option. This is direct evidence of complexity management.

**Status:** the inspected changelog's latest release is 1.3.0, dated 2025-05-08; GitHub reported the repository as unarchived. No claim of recent active development is needed to justify studying it.

### 17. [uncrustify/uncrustify](https://github.com/uncrustify/uncrustify)

**Language / role:** C++; configurable formatter and source cleanup tool for C-family languages and several related syntaxes. Study an explicitly ordered token-processing pipeline with many interacting policies.

- **C1:** `uncrustify_start` first tokenizes, then normalizes token sequences, determines brace/parenthesis levels including preprocessor cases, and only afterward performs level-dependent classification. File processing also detects embedded zero values associated with decoding failures. The ordering requirements are documented in [the central implementation](https://github.com/uncrustify/uncrustify/blob/master/src/uncrustify.cpp).
- **C2:** Shared chunks and classification stages feed separate brace, parenthesis, newline, spacing, and cleanup passes. The same pipeline supports different language modes and configuration sets, including transformations beyond whitespace. The [developer sections of the README](https://github.com/uncrustify/uncrustify#contribute) describe configuration/input/expected-output fixtures and intermediate token dumps, useful for understanding how interactions are diagnosed.

### 18. [sqlfluff/sqlfluff](https://github.com/sqlfluff/sqlfluff)

**Language / role:** Python; SQL linting, formatting, and automatic fixes across dialects and template engines. Study edits that must be mapped between rendered SQL and the original template.

- **C1:** [Patch generation](https://github.com/sqlfluff/sqlfluff/blob/main/src/sqlfluff/core/linter/patch.py) retains both source and templated slices, treats literal regions differently from generated ones, and handles empty template placeholders specially to avoid spurious deletion. The implementation explicitly accounts for loops, insertions, and non-backward slice boundaries.
- **C2:** The [architecture document](https://github.com/sqlfluff/sqlfluff/blob/main/docsv/development/architecture.md) separates templating, lexing, grammar matching, and later lint/fix stages. Dialects inherit common grammar definitions and replace selected components; references resolve grammar elements at runtime. This is a strong contrast with formatters that assume a single ordinary source file directly corresponds to one parse tree.

## Lossless syntax transformations and migration frameworks

### 19. [benjamn/recast](https://github.com/benjamn/recast)

**Language / role:** TypeScript/JavaScript; nondestructive AST rewriting and source-map-aware printing. Study how to change selected syntax without normalizing an entire file.

- **C1:** Parsing makes a shadow AST whose `.original` links let the printer recognize unchanged subtrees and reuse their source. The [patcher](https://github.com/benjamn/recast/blob/master/lib/patcher.ts) orders source replacements, handles nested replacement ranges, and attempts local comment reprinting. Correctness involves source locations and untouched text as well as AST shape.
- **C2:** The [parser integration and source-map documentation](https://github.com/benjamn/recast#using-a-different-parser) explains pluggable parsers, shared typed node builders, and preserving the original-node relationship when another transform consumes the AST. Its map generation follows reused source through slicing and indentation. These abstractions support many codemods rather than a fixed catalog of migrations.

### 20. [Instagram/LibCST](https://github.com/Instagram/LibCST)

**Language / role:** Python and Rust; concrete syntax tree library and Python codemod framework. Study a representation designed specifically for modifying source while retaining formatting details.

- **C1:** The [design rationale](https://github.com/Instagram/LibCST/blob/main/docs/source/why_libcst.rst) explains explicit ownership of whitespace, comments, commas, and parentheses. Assigning these to semantically meaningful typed nodes avoids the ambiguity of deleting or moving nodes that carry undifferentiated prefix text. Exact reconstruction is a representation property, not a guarantee that an arbitrary transformation preserves program behavior.
- **C2:** The [codemod framework](https://github.com/Instagram/LibCST/blob/main/docs/source/codemods.rst) provides shared context, automatic metadata resolution, multiple passes, composition, structured skip/failure results, testing helpers, and parallel execution utilities. Import and annotation transforms build on those interfaces. This is a strong entry for studying the layer between a syntax library and repository-wide migration tooling.

### 21. [openrewrite/rewrite](https://github.com/openrewrite/rewrite)

**Language / role:** Primarily Java; OpenRewrite's transformation framework and language modules. Study type-aware migrations that preserve local formatting, with **`rewrite-core` and the Java transformation infrastructure** as the clearest starting scope.

- **C1:** [Lossless Semantic Trees](https://docs.openrewrite.org/concepts-and-explanations/lossless-semantic-trees) combine formatting information with type attribution. This allows matching a method's semantic owner instead of assuming identical method-name text refers to the same API. The documentation also makes the local execution limit explicit: the tree must fit in memory.
- **C2:** [TreeVisitor](https://github.com/openrewrite/rewrite/blob/main/rewrite-core/src/main/java/org/openrewrite/TreeVisitor.java) parameterizes tree and context types, tracks an ancestry cursor, and supports follow-up visits. Recipes can compose these reusable traversal and transformation operations.

**Scope caveat:** the current repository README distinguishes framework, parser, and recipe licensing, and separates local OpenRewrite from additional Moderne capabilities. This entry does not attribute the commercial platform's persistent, organization-wide execution system to this repository.

### 22. [rectorphp/rector-src](https://github.com/rectorphp/rector-src)

**Language / role:** PHP; Rector's **development source repository**, implementing automated PHP upgrades and refactorings. Its README directs installation and issue reporting to the separate distribution repository; only the development codebase is counted here.

- **C1:** A concrete example is [StrEndsWithRector](https://github.com/rectorphp/rector-src/blob/main/rules/Php80/Rector/Identical/StrEndsWithRector.php): it checks the recognized substring shape, compares expressions or literal lengths, rejects explicitly case-insensitive comparisons, and declares minimum PHP-version and polyfill requirements. This demonstrates the semantic and compatibility preconditions needed even for an apparently simple API substitution; it is not evidence of universal safety for all inputs.
- **C2:** [AbstractRector](https://github.com/rectorphp/rector-src/blob/main/src/Rector/AbstractRector.php) shares node factories, type/name resolution, comparison, traversal, and comment helpers. Individual rules declare the node types they handle and implement refactoring against that infrastructure. Study the relationship between reusable analysis services and narrowly scoped transformation rules.

## Structural rewriting and semantic patches

### 23. [coccinelle/coccinelle](https://github.com/coccinelle/coccinelle)

**Language / role:** OCaml; semantic patches for C source-to-source transformations. **Official substantive GitHub mirror:** the repository description identifies the main repository at Inria. The GitHub mirror contains the implementation, not merely a relocation notice.

- **C2:** The [CTL engine](https://github.com/coccinelle/coccinelle/blob/master/ctl/ctl_engine.ml) is parameterized by substitution, graph, and predicate modules. It implements a witness-tree model-checking engine for CTL with free-variable extensions, giving semantic matching a reusable computational foundation beyond text templates.
- **C3:** The same implementation contains label memoization, filtering by required environments and states, and incremental treatment of new information during fixed-point iteration. These address the cost of model checking without hiding the underlying algorithm behind an external service.

The [project introduction](https://github.com/coccinelle/coccinelle/blob/master/readme.txt) establishes the style-preserving C transformation use case. This is a particularly useful selection for engineers interested in the connection between program analysis and large families of source edits.

### 24. [comby-tools/comby](https://github.com/comby-tools/comby)

**Language / role:** OCaml; structural search and replacement across many languages. Study an intermediate point between regular expressions and full semantic AST analysis.

- **C1:** Comby's design accounts for nested delimiters, strings, and comments. Its [design/contribution notes](https://github.com/comby-tools/comby/blob/master/docs/CONTRIBUTING.md) explain why adding arbitrary matching syntax can interfere with balanced delimiter parsing, and why the meaning of delimiters varies by language. This is a concrete adversarial-input and language-boundary problem.
- **C2:** Match/rewrite templates are separated from optional constraint rules. This allows readable concrete-syntax templates to be reused with richer matching conditions, instead of encoding both concerns in one metasyntax. The [repository examples](https://github.com/comby-tools/comby#isnt-a-regex-approach-like-sed-good-enough) demonstrate the intended transformation model.

The design notes also describe performance-regression checks. Structural awareness should not be confused with type-aware refactoring or proof that a replacement preserves behavior.

### 25. [ast-grep/ast-grep](https://github.com/ast-grep/ast-grep)

**Language / role:** Rust; tree-sitter-based structural search, linting, and rewriting. Study reusable pattern matching paired with precise source-range replacement.

- **C1:** The [rewrite guide](https://ast-grep.github.io/guide/rewrite-code.html) addresses indentation-sensitive substitution and expanding a replacement to consume adjacent syntax such as commas. It also documents failure boundaries: unmatched replacement metavariables become empty text, and a syntactically matched rewrite can still produce invalid or nonsensical code.
- **C2:** The [pattern implementation](https://github.com/ast-grep/ast-grep/blob/main/crates/core/src/matcher/pattern.rs) separates language/document abstractions, contextual pattern selection, matching strictness, and metavariable environments. It rejects a list-capturing metavariable used as an invalid single-node pattern root. These mechanisms serve CLI rules and embedded APIs rather than one hard-coded transformation.

### 26. [uber/piranha](https://github.com/uber/piranha)

**Language / role:** Rust with Python bindings; Polyglot Piranha, a rule-driven rewriting framework with feature-flag cleanup as a major use case. Study transformations where one edit deliberately enables further cleanup.

- **C1:** The [rule-graph implementation](https://github.com/uber/piranha/blob/master/crates/core/src/models/rule_graph.rs) performs forward definite-assignment analysis of capture tags and reports tags used in predicates without being defined by the rule graph. This is a concrete correctness issue introduced by chaining rules, separate from whether an individual pattern parses.
- **C2:** The [Polyglot architecture and DSL guide](https://github.com/uber/piranha/blob/master/POLYGLOT_README.md) describes rules, graph edges, substitutions, and scoped propagation into built-in or custom cleanup rules. For example, replacing a flag check can trigger Boolean simplification and removal of obsolete surrounding constructs. The framework supports broader migrations, not only feature flags.

The repository distinguishes the current polyglot implementation from legacy language-specific versions available under an older tag. The older implementations are not counted as separate projects; current source paths above are preferred over historical paths embedded in parts of the guide.

## Coverage and search notes

Discovery used live web searches across more than six distinct formulations, followed by canonical-URL checks through GitHub's API and direct reading of primary documentation or source. Search angles included:

- Generic formatter architecture, document IRs, and plugin systems: Prettier, Biome, and dprint.
- Python AST stability and cost-based formatting: Black, Ruff, and YAPF.
- C/C++ token formatting and compiler infrastructure: clang-format and Uncrustify.
- Scala, OCaml, and Haskell layout algorithms and design records.
- Dart layout solving and language-versioned formatting behavior.
- Shell, Lua/Luau, Clojure, Ruby, and Swift formatter communities, extending discovery beyond the largest web/Python tools.
- Concrete syntax trees, nondestructive printing, and Java/PHP migration frameworks.
- C semantic patches, structural templates, tree-sitter rewrites, and rule-graph cleanup.
- SQL dialects and templating-aware automatic fixes, which added a distinct source-mapping problem late in the search.

Later queries increasingly returned integrations, wrappers, alternate frontends, or implementations sharing already represented approaches. The final list slightly exceeds the broad-category guide to retain templated SQL alongside both language-specialized formatters and semantic rewriting engines. It remains selective: Ruby and Swift discovery yielded plausible further candidates, but they were not taken through the same full evidence review and are not rated here. Editor adapters, formatting aggregators without a substantial engine, generated distribution copies, awesome-lists, tutorials, generic compiler IR rewriting, and analysis-only tools were excluded from the retained list.

Each retained repository was checked against an additional primary implementation or design source beyond its repository introduction. Default-branch links are readable entry points, not immutable revision pins. Some documentation URLs had moved or could not be opened; the report uses verified source-tree files where necessary. No candidate repository was cloned, built, installed, or executed, and no numerical speed comparison was independently benchmarked. Correctness mechanisms are reported with their limits: syntax-tree equality does not prove arbitrary semantic equivalence, and user-authored structural rewrites still require appropriate preconditions and validation.
