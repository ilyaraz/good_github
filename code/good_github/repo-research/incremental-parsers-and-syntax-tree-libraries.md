# Incremental parsers and syntax tree libraries

Research date: **2026-10-09**.

This selection covers parsers that reuse work after source edits, reusable concrete/abstract syntax tree representations, and libraries for inspecting or transforming source while respecting syntax and source locations. It includes standalone libraries and clearly identified subsystems of larger repositories. A syntax tree library need not implement incremental parsing to qualify; streaming input alone is not treated as edit-incremental parsing. The 25 entries are study recommendations, not a claim that every component is uniformly exemplary or suitable for a new production dependency.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, language semantics, malformed input, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or representations supporting multiple applications.
- **C3 — Performance and structure:** concrete latency, allocation, memory, or throughput constraints addressed through an understandable design.
- **C4 — Evolution:** evidence spanning years of compatibility work, testing, or complexity management; repository age alone does not qualify.

## General incremental parsing engines

### 1. [tree-sitter/tree-sitter](https://github.com/tree-sitter/tree-sitter)

**Language/role:** C runtime and Rust tooling; generated parsers with incremental concrete syntax trees.

Study the boundary between a language-specific generated parser and a shared runtime, particularly how edits, reusable subtrees, and application-owned input interact. Its explicit edit protocol is useful material for anyone designing an editor integration.

- **C1:** An edit must update byte and point ranges before reparsing. Previously retained node handles require their own position updates. Concurrency also has a precise ownership rule: separate tree copies may be used across threads, but one tree instance is not itself thread-safe.
- **C2:** The runtime supports different generated languages and included source ranges, allowing applications to compose overlapping trees for embedded languages.
- **C3:** Reparsing accepts the previous tree and shares internal structure; copying a tree increments an atomic reference count rather than duplicating all nodes. These mechanisms directly address repeated editor updates.

Entry point and evidence: [advanced parsing: edits, included ranges, and concurrency](https://tree-sitter.github.io/tree-sitter/using-parsers/3-advanced-parsing.html).

### 2. [ohmjs/ohm](https://github.com/ohmjs/ohm)

**Language/role:** JavaScript; PEG toolkit with incremental matchers and separately defined semantics.

Ohm is a useful comparison with tree-oriented APIs: clients inspect successful parses through semantic operations and attributes, while grammars remain separate from those interpretations.

- **C1:** `Matcher.replaceInputRange` validates edit bounds, relocates memo-table entries, and invalidates obsolete results before the edit. The implementation also rejects incremental use when a grammar cannot support it; cached recognition results are not unconditionally reusable.
- **C2:** Grammar extension, independent semantics instances, visitor-like operations, and memoized attributes support interpreters, analyses, and custom languages without embedding actions in grammar productions.
- **C3:** A persistent matcher reuses partial results across edits. Its relatively direct memo-table maintenance offers an instructive comparison with GPeg's more elaborate indexing.

Entry points: [matcher and semantics API](https://ohmjs.org/docs/api-reference); [Matcher implementation](https://raw.githubusercontent.com/ohmjs/ohm/main/packages/ohm-js/src/Matcher.js).

### 3. [zyedidia/gpeg](https://github.com/zyedidia/gpeg)

**Language/role:** Go; dynamically compiled PEG parsing virtual machine and incremental memoization engine. The associated paper presents it as a research prototype.

Study how the choice of memo-table data structure changes the cost of processing edits. This is a substantive implementation with a published explanation of its design, rather than a thin interface to another parser.

- **C1:** Invalidation must track characters *examined*, including lookahead, rather than only characters consumed. Captured parse results must remain relocatable when edits shift their positions.
- **C2:** Runtime grammar compilation, AST captures, pattern matching, and an input reader abstraction serve both language grammars and regex-like workloads.
- **C3:** The design uses an augmented interval tree, lazy position shifts, and tree-shaped memoization of repetitions to avoid scanning flat memo tables after ordinary edits. The paper also explains memory tradeoffs and the possibility of whole-input work after disruptive edits; no universal speedup is assumed here.

Entry point: [authors' implementation paper, especially sections 3–5](https://zyedidia.github.io/papers/gpeg_sle21.pdf).

### 4. [Eliah-Lakhin/papa-carlo](https://github.com/Eliah-Lakhin/papa-carlo)

**Language/role:** Scala; incremental PEG/Pratt parser construction library. **Historical/beta study target:** the README still describes a beta release, and [public repository metadata](https://api.github.com/repos/Eliah-Lakhin/papa-carlo) records its last push in December 2020.

Its distinctive idea is to let language authors specify contextual fragments separately from lexical and syntactic rules. Follow the pipeline from changed text to token replacements, fragment updates, and AST branch replacement.

- **C1:** Cached fragments require a semantic boundary invariant: the applicable syntax rule must remain independent of the fragment's contents. Error recovery and token-boundary choices make that contract more demanding than simply splitting on delimiters.
- **C2:** Separate tokenizer, contextualizer, syntax rules, and stage signals form a reusable language-definition toolkit, including Pratt expression primitives.
- **C3:** Caching operates on small contextual fragments. The documentation explicitly acknowledges the startup overhead of caching and recovery, making the edit-latency versus batch-throughput tradeoff visible.

Entry point: [author's architecture and fragment-definition guide](https://lakhin.com/projects/papa-carlo/).

### 5. [softdevteam/eco](https://github.com/softdevteam/eco)

**Language/role:** Python; language-composition editor containing an incremental LR parser and versioned syntax trees. **Historical research prototype:** upstream explicitly says it is incomplete and not intended for production; [repository metadata](https://api.github.com/repos/softdevteam/eco) records a December 2022 last push.

The relevant subsystem is `lib/eco/incparser`, not the graphical editor. It exposes complications that simpler incremental-parser examples omit: subtree retention during recovery, undoable deletion, and nested language contexts.

- **C1:** Reuse is guarded by change, error, and context checks. Recovery must repair parent/sibling relationships, retain eligible subtrees, and restore previous versions. Deleted nodes are kept for undo rather than immediately discarded.
- **C3:** Unchanged nonterminals can be shifted as whole subtrees; unsuitable nodes are broken down. Out-of-context parsing attempts to limit reanalysis while checking the expected parser state and surrounding context.

Entry point: [incremental parser, recovery integration, and retention logic](https://raw.githubusercontent.com/softdevteam/eco/master/lib/eco/incparser/incparser.py).

## Reusable tree representations

### 6. [rust-analyzer/rowan](https://github.com/rust-analyzer/rowan)

**Language/role:** Rust; language-independent lossless syntax tree library, not a parser generator.

Study the separation between immutable, position-independent green data; navigable syntax-node views; and an application-defined typed AST. This is a compact foundation whose design can be understood independently of rust-analyzer's language server.

- **C2:** The `Language` abstraction maps application syntax kinds into the generic tree. Builders and traversal APIs support different grammars; the worked example layers typed AST wrappers over the same underlying nodes and preserves erroneous input.
- **C3:** The design discusses packed node allocation, tagged child pointers, and interning of immutable nodes/tokens. Position-independent storage allows structural sharing while navigation views supply offsets and parents.

Entry points: [worked parser and AST example](https://raw.githubusercontent.com/rust-analyzer/rowan/master/examples/s_expressions.rs); [tree design and allocation discussion](https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/syntax.md). The latter explicitly dates its architectural snapshot to 2020, so treat its fine implementation details as historical context.

### 7. [domenicquirl/cstree](https://github.com/domenicquirl/cstree)

**Language/role:** Rust; lossless CST library. **Substantively evolved Rowan fork**, retained because its ownership, interning, and traversal design differs materially.

Compare its persistent red layer with Rowan's navigation model. The repository explains the tradeoff: keeping realized red nodes allocated can improve repeated traversal but retains more state.

- **C1:** Red nodes can be shared across threads through whole-tree atomic reference counting. The design gives up in-place CST mutation; updates produce replacement trees. Resolver-bearing types make availability of interned token text explicit.
- **C2:** Generic syntax kinds, optional custom node data, interchangeable string interning, and resolved/unresolved node forms support compiler and tooling integrations.
- **C3:** Interned token text, cached green nodes, precomputed subtree hashes, and borrowed traversal results address allocation and reference-count overhead. These are concrete departures from its parent project, not merely a renamed API.

Entry points: [repository's comparison with Rowan](https://github.com/domenicquirl/cstree#readme); [red-tree API and representation](https://docs.rs/cstree/latest/cstree/syntax/index.html).

### 8. [udoprog/syntree](https://github.com/udoprog/syntree)

**Language/role:** Rust; contiguous syntax tree storage with streaming construction.

Study an alternative to reference-counted green trees: nodes reside in contiguous storage, and the caller manages source text separately. `Copy` payloads can represent synthetic macro-generated content as well as source references.

- **C1:** Builder operations expose failures such as identifier overflow, unclosed nodes, and invalid checkpoint relationships. `close_at` requires a sibling checkpoint; the documentation candidly explains that mixing checkpoints from different trees is not well-defined.
- **C2:** Configurable index/storage “flavors,” arbitrary copyable payloads, optional span storage, and checkpoint wrapping support different parser and generated-syntax designs.
- **C3:** A contiguous slab and externally managed source strings make memory layout an explicit architectural choice. Upstream describes its comparative performance observations as preliminary, so this report makes no superiority claim.

Entry points: [layout and payload rationale](https://github.com/udoprog/syntree#readme); [Builder contracts and checkpoint examples](https://docs.rs/syntree/latest/syntree/struct.Builder.html).

### 9. [s-expressionists/Concrete-Syntax-Tree](https://github.com/s-expressionists/Concrete-Syntax-Tree)

**Language/role:** Common Lisp; source-associated s-expression trees and reconstruction after macro expansion.

This library addresses a different notion of concrete syntax: preserving source provenance alongside Lisp objects, including when conventional macros operate on raw s-expressions. It is not a byte-for-byte whitespace-preserving editor CST.

- **C1:** Reconstruction must handle shared cons cells, cycles, deep recursion, and ambiguous atom provenance. The implementation uses identity tables and bounded recursion; its comments explicitly distinguish reliable cons identity from heuristic attribution for atoms.
- **C2:** The CST/raw-expression boundary lets existing macroexpanders remain usable while a reconstruction protocol recovers source-associated trees. The repository also supplies destructuring and lambda-list facilities around the representation.
- **C3:** Memoized identity correspondence avoids revisiting cycles and reuses existing CSTs for retained subexpressions; an explicit worklist limits recursive traversal depth.

Entry point: [reconstruction algorithm and its documented precision limits](https://raw.githubusercontent.com/s-expressionists/Concrete-Syntax-Tree/master/reconstruct.lisp).

## Parser and tree subsystems in language toolchains

### 10. [dotnet/roslyn](https://github.com/dotnet/roslyn)

**Language/role:** C# and Visual Basic compiler platform; focus on C# syntax trees and `src/Compilers/CSharp/Portable/Parser`.

Study how a handwritten recursive-descent parser consumes a mixture of old nodes, old tokens, and newly lexed tokens. The “blender” makes reuse decisions a visible layer rather than spreading them throughout every grammar production.

- **C1:** Reuse requires synchronized positions, safe edit boundaries, and matching parser context. The design explains why ambiguous expression parsing is conservatively repeated: lookahead beyond an expression can invalidate an otherwise unchanged subtree.
- **C2:** Public syntax trees underpin analysis and transformation APIs while internal green nodes and parser machinery serve compilation and IDE workloads.
- **C3:** Whole statements and members can be reused; intersecting nodes are lazily broken into smaller pieces. The design documents limits such as giant expressions and pervasive syntax errors, where reuse provides less benefit.

Entry point: [incremental parser design, implementation links, and caveats](https://github.com/dotnet/roslyn/blob/main/docs/compilers/Design/Incremental%20Parser.md).

### 11. [swiftlang/swift-syntax](https://github.com/swiftlang/swift-syntax)

**Language/role:** Swift; SwiftSyntax, SwiftParser, and related source construction/transformation libraries. Counted once as a package collection.

Study the combination of persistent full-fidelity trees and an incremental parser that tracks what it looked ahead at, not merely the text attached to each node.

- **C1:** Trees explicitly represent missing and unexpected syntax, retaining malformed source. Incremental parsing records lookahead lengths to determine reuse eligibility, while immutable trees support independent transformations across threads.
- **C2:** Typed syntax protocols, visitors, rewriters, and builders serve macros, formatters, generators, and source analyses.
- **C3:** Reused subtrees retain their originating allocation arenas. The current transition implementation deliberately performs an occasional full reparse to compact accumulated arenas, exposing a concrete memory-versus-edit-latency tradeoff.

Entry points: [tree model and transformation guide](https://raw.githubusercontent.com/swiftlang/swift-syntax/main/Sources/SwiftSyntax/Documentation.docc/Working%20with%20SwiftSyntax.md); [incremental transition and arena compaction](https://raw.githubusercontent.com/swiftlang/swift-syntax/main/Sources/SwiftParser/IncrementalParseTransition.swift).

### 12. [rust-lang/rust-analyzer](https://github.com/rust-lang/rust-analyzer)

**Language/role:** Rust; focus on the `parser` and `syntax` crates, including incremental reparsing. The monorepo is counted once; Rowan is separately listed for its independent, language-neutral implementation.

Study a deliberately restricted reparse strategy integrated with a larger analysis system: first attempt a token replacement, then a surrounding brace-delimited block.

- **C1:** Token reuse checks lexical kind, contextual keywords, removed newlines, and whether an edited identifier could join the following character into a larger token. Block reparsing verifies delimiter balance and merges relocated diagnostics.
- **C2:** The architecture separates parsing, lossless syntax, typed AST views, and later analysis. This makes the Rust-specific parser/tree boundary useful independently of the editor protocol.
- **C3:** Fast paths replace a token or bounded subtree; unsupported edits fall back rather than requiring an elaborate universally incremental grammar.

Entry points: [current reparsing implementation](https://raw.githubusercontent.com/rust-lang/rust-analyzer/master/crates/syntax/src/parsing/reparsing.rs); [library architecture](https://rust-analyzer.github.io/book/contributing/architecture.html).

### 13. [microsoft/TypeScript](https://github.com/microsoft/TypeScript)

**Language/role:** TypeScript compiler and syntax APIs; this study target is the **verified historical `v5.9.3` TypeScript implementation**. Current `main` also contains the Go compiler under `tsc`; its JSDoc reparser is not being presented here as the same edit-incremental implementation.

The historical parser is especially instructive as a mutable alternative to persistent green trees.

- **C1:** Incremental updates mutate positions and parents in reused nodes, so the old `SourceFile` becomes unusable. The implementation expands the affected range for lookahead and restricts reuse by parsing context, documenting speculative-parsing hazards.
- **C3:** A syntax cursor permits reuse of eligible statements, class/type members, and other selected list elements. The parser also explains reuse of scanner/parser state to reduce per-file setup costs.

Entry points: [`v5.9.3` parser and IncrementalParser implementation](https://raw.githubusercontent.com/microsoft/TypeScript/v5.9.3/src/compiler/parser.ts); [current parser subtree inventory](https://api.github.com/repos/microsoft/TypeScript/contents/tsc/internal/parser). The version pin is intentional and should not be read as a claim about the current native parser's behavior.

### 14. [typst/typst](https://github.com/typst/typst)

**Language/role:** Rust; focus on `crates/typst-syntax`, especially incremental reparsing of a mixed markup/code language.

Study conservative region expansion in a grammar where delimiters, indentation, and newline state all affect how far an edit propagates.

- **C1:** A local reparse succeeds only when delimiter nesting and relevant parser state remain compatible. Tests compare the incrementally updated tree against a fresh parse and check which source range was reparsed.
- **C3:** The algorithm descends to a surrounding block or expands a markup region, with a whole-text fallback. Its comments explain that more aggressive reparsing inside lists/headings was removed because of correctness bugs without a meaningful performance loss.
- **C2:** A dedicated source object combines text, line mappings, and syntax, providing an edit interface usable by tooling outside the typesetting stages.

Entry points: [reparser, rationale, and differential tests](https://raw.githubusercontent.com/typst/typst/main/crates/typst-syntax/src/reparser.rs); [Source representation and edit integration](https://docs.rs/typst-syntax/latest/src/typst_syntax/source.rs.html). The inspected implementation does not locally reparse math expressions.

### 15. [JuliaLang/julia](https://github.com/JuliaLang/julia)

**Language/role:** Julia; specifically the **`JuliaSyntax/` subsystem**, not the entire compiler/runtime.

JuliaSyntax's [former standalone repository](https://github.com/JuliaLang/JuliaSyntax.jl) directs development for version 2 onward into this monorepo and retains older-version backports. It is therefore counted here, once, at its current implementation home.

- **C1:** `ParseStream` output must cover the input and maintain nested spans, source-ordered siblings, and child-before-parent emission. Recovery distinguishes missing syntax from unexpected tokens retained under error nodes, enabling deterministic tree construction from malformed input.
- **C2:** Parsing emits an intermediate stream rather than committing to one tree representation. Builders can produce lossless green trees, source-linked `SyntaxNode` trees, or Julia's conventional `Expr` for compatibility.

Entry points: [current subsystem](https://github.com/JuliaLang/julia/tree/master/JuliaSyntax); [current design document](https://raw.githubusercontent.com/JuliaLang/julia/master/JuliaSyntax/docs/src/design.md). This is a syntax-tree architecture selection; it does not imply implemented edit-incremental parsing.

### 16. [julia-vscode/CSTParser.jl](https://github.com/julia-vscode/CSTParser.jl)

**Language/role:** Julia; mutable concrete syntax trees designed to retain more source information than `Base.Expr`.

Study a compatibility-oriented tree model that keeps conventional expression arguments while separately retaining punctuation and keyword trivia. It offers a different design from JuliaSyntax's layered parse stream.

- **C1:** `span` excludes trailing whitespace while `fullspan` includes it; arguments and trivia have distinct ordering contracts. The specification handles cases where source order and the conventional AST differ, such as `global const` declarations.
- **C2:** `EXPR` uniformly represents terminals and composite expressions, with parent links, token text, and metadata. That combination supports source-aware navigation while keeping a recognizable relationship to Julia expressions.

Entry points: [representation specification and syntax mappings](https://github.com/julia-vscode/CSTParser.jl/blob/main/specification.md); [specification regression cases](https://raw.githubusercontent.com/julia-vscode/CSTParser.jl/main/test/test_spec.jl). These tests also expose version-sensitive expectations rather than assuming the host parser never changes.

## Source analysis and transformation libraries

### 17. [davidhalter/parso](https://github.com/davidhalter/parso)

**Language/role:** Python; error-recovering, round-trip parser with a diff-based incremental path.

Study the costs of retrofitting incrementality onto mutable Python trees. Its implementation comments are unusually candid about why avoiding node copies improves performance while making state management difficult.

- **C1:** The diff parser checks parent/child consistency, token positions, prefixes, and equivalence with ordinary parsing; its documentation points maintainers to a dedicated fuzzer.
- **C2:** Version-selectable grammars, round-trip tree APIs, and multi-error reporting support refactoring and editor analysis.
- **C3:** It computes changed regions with `difflib` and reuses mutable nodes. The [API documentation](https://parso.readthedocs.io/en/latest/docs/usage.html) labels `diff_cache` experimental and warns that cached modules can change underneath their holders.
- **C4:** The changelog spans 2017–2026 and records diff-parser fuzzing/fixes, grammar changes, new Python syntax, and explicit removal of older-version support.

Implementation/history entry points: [diff parser](https://raw.githubusercontent.com/davidhalter/parso/master/parso/python/diff.py); [changelog](https://raw.githubusercontent.com/davidhalter/parso/master/CHANGELOG.rst).

### 18. [Instagram/LibCST](https://github.com/Instagram/LibCST)

**Language/role:** Python API with a Rust native parser; typed, lossless Python CST and transformation infrastructure.

Study how a tree can remain convenient for semantic transformations while assigning precise ownership to commas, parentheses, whitespace, and comments. Its category fit is source-preserving syntax trees, not edit-incremental reparsing.

- **C1:** Whitespace ownership is part of the representation, avoiding the ambiguity of attaching arbitrary prefixes to grammar leaves. Immutable nodes and separate metadata help prevent analyses from silently changing source structure.
- **C2:** Typed nodes, visitors, transformers, and declarative metadata providers support codemods and linters. Metadata dependencies are resolved through a wrapper; position, scope, and qualified-name information can be computed without adding mutable fields to syntax nodes.

Entry points: [representation tradeoffs and whitespace ownership](https://libcst.readthedocs.io/en/latest/why_libcst.html); [metadata architecture](https://raw.githubusercontent.com/Instagram/LibCST/main/docs/source/metadata.rst). Full fidelity entails extra parsing work; the documentation does not promise ordinary-AST costs.

### 19. [benjamn/recast](https://github.com/benjamn/recast)

**Language/role:** TypeScript/JavaScript; AST transformation, conservative reprinting, and source maps.

Study an approach that preserves original text through provenance rather than requiring every formatting detail to become a dedicated AST node. Parsing creates a shadow tree with `.original` links used to identify changed regions.

- **C1:** Reprinting must handle overlapping replacements, comments, indentation, and parentheses while preserving valid token boundaries. The patcher treats nested replacement ranges explicitly and falls back when a local reprint cannot preserve surrounding comments.
- **C2:** Parser substitution supports different JavaScript-family syntaxes, while the same transformation/printing interface tracks original source across files and produces source maps.

Entry points: [original-node contract and parser integration](https://github.com/benjamn/recast#readme); [patcher implementation](https://raw.githubusercontent.com/benjamn/recast/master/lib/patcher.ts). Original-node links must survive downstream transformations for conservative printing to work.

### 20. [javaparser/javaparser](https://github.com/javaparser/javaparser)

**Language/role:** Java; parser, mutable AST, analysis infrastructure, and lexical-preserving printing.

Study the observer bridge between semantic-looking AST mutations and a token-oriented printable representation. The lexical-preservation subsystem is a particularly concrete entry into the larger project.

- **C1:** Node replacement must find the actual token owner, preserve comments, and update text consistently. The printer documents a reentrancy invariant: calling `toString()` during initial text construction can recursively observe an empty representation and lose token content.
- **C2:** The parser's AST supports inspection and mutation; lexical preservation registers observers throughout a subtree so ordinary property/list changes can drive text updates. A concrete syntax model supplies printable structure for newly constructed nodes.

Entry point: [LexicalPreservingPrinter setup, observers, and invariants](https://raw.githubusercontent.com/javaparser/javaparser/master/javaparser-core/src/main/java/com/github/javaparser/printer/lexicalpreservation/LexicalPreservingPrinter.java). This is AST-to-source synchronization, not a claim that every source edit is incrementally parsed.

### 21. [INRIA/spoon](https://github.com/INRIA/spoon)

**Language/role:** Java; Java metamodel, source analysis/transformation, and multiple printing strategies.

Study how model changes and original source fragments are reconciled by the Sniper printer. Spoon is included for its substantial tree/metamodel infrastructure, not simply because it wraps a Java parser.

- **C1:** Source-preserving output depends on installing change collection before model construction. The implementation rejects a missing collector and mismatching compilation units, and coordinates comment, indentation, and source-fragment context.
- **C2:** Model elements, visitors, change observation, configurable token writers, and printing strategies allow analyses and transformations to share a common Java representation.

Entry points: [printing modes and import handling](https://spoon.gforge.inria.fr/custom-pretty-printing.html); [Sniper implementation](https://raw.githubusercontent.com/INRIA/spoon/master/src/main/java/spoon/support/sniper/SniperJavaPrettyPrinter.java). The inspected Sniper class carries an `Experimental` annotation.

### 22. [scalameta/scalameta](https://github.com/scalameta/scalameta)

**Language/role:** Scala; parser, syntax trees, dialects, quasiquotes, and traversal/transformation APIs.

Study the interaction between a changing language grammar and a public tree API. Versioned extractors are a useful mechanism for accommodating node-field evolution without assuming all consumers migrate at once.

- **C1:** The parser handles dialect-dependent conditional syntax, indentation/outdent state, and ambiguous forms such as named versus anonymous givens. These affect tree shape and recovery boundaries, not just token recognition.
- **C2:** Typed trees, dialect selection, quasiquotes, custom traversers, and transformers support source analysis and generation across Scala environments. The guide explains reference equality versus structural comparison and version-specific pattern extractors.

Entry points: [tree guide and transformation limitations](https://scalameta.org/docs/trees/guide.html); [ScalametaParser implementation](https://raw.githubusercontent.com/scalameta/scalameta/main/scalameta/parsers/shared/src/main/scala/scala/meta/internal/parsers/ScalametaParser.scala). Parsed trees retain source detail, but the guide explicitly warns that transformed trees do not preserve all comments and formatting when pretty-printed.

### 23. [dtolnay/syn](https://github.com/dtolnay/syn)

**Language/role:** Rust; Rust token-stream parser and typed AST library, especially for procedural macros.

Study reusable syntax components with carefully chosen parsing contracts. Unlike a lossless editor CST, Syn works primarily at the token/typed-syntax level and is not being described as an incremental text parser.

- **C1:** Context-sensitive forms deliberately lack a single default `Parse` implementation: inner versus outer attributes and punctuation lists with different trailing-token rules require an explicit parser choice. Lookahead diagnostics retain the location of the unexpected token.
- **C2:** Most syntax nodes compose through `ParseStream -> Result<T>` functions; consumers can combine Rust syntax types with custom macro syntax. Typed delimiter and punctuation structures preserve details that a loosely structured AST would leave to callers.

Entry point: [parsing architecture, contextual parser selection, and examples](https://docs.rs/syn/latest/syn/parse/index.html). The repository's configurable feature surface also lets consumers select the syntax functionality they need.

### 24. [clj-commons/rewrite-clj](https://github.com/clj-commons/rewrite-clj)

**Language/role:** Clojure/ClojureScript; source-preserving nodes, parsing, zippers, and structural editing for Clojure and EDN.

Study how editing operations distinguish source syntax from the values produced by reading that syntax. Its zipper API manages whitespace while allowing callers to inspect the underlying nodes when necessary.

- **C1:** Namespaced maps, auto-resolved symbols, reader macros, duplicate values, and host-specific numeric representations complicate conversion to s-expressions. The guide documents these distinctions and makes namespace resolution configurable rather than silently depending on the execution namespace.
- **C2:** Parser, node, zipper, and paredit APIs support both low-level tree operations and higher-level source editing across two host platforms.
- **C4:** The guide records the project's evolution from 2013, the later ClojureScript implementation, their consolidation, compatibility choices, and a multi-version test policy. This is evidence of managed evolution beyond simple age.

Entry point: [user guide: representation, migration history, APIs, and semantic caveats](https://github.com/clj-commons/rewrite-clj/blob/main/doc/01-user-guide.adoc). Whitespace preservation has a documented exception: newline variants normalize to `\n`.

### 25. [doorgan/sourceror](https://github.com/doorgan/sourceror)

**Language/role:** Elixir; source manipulation through annotated Elixir ASTs, zippers, and comments.

Study a practical alternative to replacing a language's native AST: attach comments to node metadata and supply navigation/editing abstractions that preserve their association with code.

- **C1:** Structural removal has language-specific rules. Removing a reserved block's body substitutes an empty block to keep the AST valid; removing a root without a parent raises an error. Comment association and traversal boundaries are explicit concerns.
- **C2:** The zipper separates the focused node, sibling/parent path, and optional enclosing subtree. Subtree, supertree, and `within` operations support composable local transformations that reconnect to the surrounding tree.

Entry points: [zipper API and removal contracts](https://sourceror.hexdocs.pm/Sourceror.Zipper.html); [zipper representation and subtree implementation](https://raw.githubusercontent.com/doorgan/sourceror/main/lib/sourceror/zipper.ex). Upstream also documents compatibility via vendored parser/formatter modules for older Elixir versions; that does not make this merely a generated binding.

## Coverage, search process, and limitations

Discovery used substantially more than six distinct live search formulations, including:

- General incremental engines and subtree reuse: `incremental parser syntax tree library GitHub tree sitter lezer rowan architecture`.
- Native and JVM implementations: `incremental parsing library GitHub syntax tree reuse C++ Rust Java`.
- Green/red and lossless representations: `site:github.com rowan cstree lossless syntax tree green`.
- PEG and packrat approaches: `site:github.com incremental PEG parsing gpeg ohm`, followed by project-specific primary-source searches.
- Python source preservation: `site:github.com lossless concrete syntax tree library Python LibCST parso`.
- Language composition and recovery: searches for Eco's incremental parser and source implementation.
- Less prominent communities: syntax-tree searches spanning Julia, Elixir, Clojure, Common Lisp, Haskell, OCaml, and Scala.
- Typed transformations and metamodels: JavaParser lexical preservation, Spoon source fragments, Swift tree immutability, and Scala tree/dialect APIs.
- Final alternative searches for edit-incremental libraries and persistent syntax trees, which mostly returned already covered systems, small/new implementations, bindings, or adjacent parser tooling.

Every retained canonical GitHub URL was opened or checked against the public GitHub API. Each entry also has an independently read primary implementation, design, API, or test source beyond the repository README. Source files were read without running candidate code, installing dependencies, or cloning repositories. Public metadata was checked for archive status; none of the 25 selected repositories was marked archived at research time. That observation does not establish active maintenance. Eco and Papa Carlo are explicitly historical study targets, GPeg has research-prototype provenance, and TypeScript's studied implementation is explicitly version-pinned.

Important exclusions and boundaries:

- **Lezer:** the [official GitHub LR repository](https://github.com/lezer-parser/lr) was archived on April 15, 2026 and directs development to another host. A maintained official GitHub mirror was not established, so it is excluded under the requested hosting rule despite its strong technical relevance.
- **Relocations and related implementations:** JuliaSyntax is represented at its current Julia monorepo home, not counted again as a standalone project. Cstree is explicitly identified as a materially different Rowan fork. Individual Tree-sitter grammars and thin language bindings are not separate entries.
- **Adjacent categories:** generic parser combinators/generators, token-streaming libraries, NLP constituency parsers, syntax-tree format specifications without a substantial implementation, and tools merely consuming Tree-sitter were not included on those grounds alone. Small tutorial parsers were also excluded.
- **Search limits:** this is a broad selection rather than an exhaustive census. C/C++, OCaml, and Haskell discovery did not yield equally strong additional selections within the chosen edit-incremental/source-tree scope and verification depth; this is a coverage limitation, not a claim that those communities lack relevant work.
- **Evidence versus judgment:** implementation behavior and documented contracts are sourced facts; criterion assignments and suggestions about what an engineer can learn are grounded editorial judgments. No independent benchmark or full code audit was performed. Design documents can lag implementations, mutable branch links can change, and C4 is assigned only where the inspected material actually establishes sustained evolution and complexity management.
