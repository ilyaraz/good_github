# Language servers and semantic code navigation tools

Research date: 2026-10-09.

This report selects 23 GitHub repositories implementing language servers, reusable semantic editor infrastructure, or symbol-aware code navigation indexes. It includes both interactive analysis of unfinished source and offline indexing of buildable projects. Monorepos count once, with the relevant subsystem identified. The selection emphasizes engineering mechanisms worth studying rather than popularity, feature completeness, or a ranking of current maintenance activity.

Criteria labels:

- **C1 — Difficult correctness:** semantic invariants, concurrent updates, malformed input, identity, cancellation, or failure recovery.
- **C2 — Reusable abstractions:** substantial analysis, protocol, query, or extension interfaces supporting multiple features and clients.
- **C3 — Performance and structure:** concrete latency, memory, recomputation, or indexing constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility work, testing, or deliberate complexity management.

Criterion assignments and recommendations are engineering judgments based on the cited primary material. They identify useful study areas; they do not establish that every component is exemplary. No candidate code was executed or benchmarked. The documentation and source links below are the recommended entry points as well as evidence for the associated claims.

## Compiler-backed and incremental semantic engines

### 1. [rust-lang/rust-analyzer](https://github.com/rust-lang/rust-analyzer)

**Rust — Rust language server and reusable IDE analysis engine.** A particularly useful study of designing a compiler front end around continuous editing, including incomplete programs, rather than invoking a batch compiler for every request.

- **C1:** Parsing always produces a tree plus errors; the semantic model permits incomplete code. Mutable `AnalysisHost` updates are separated from immutable `Analysis` snapshots, and cancellation is handled across the analysis API boundary. These are concrete places to study consistency while edits and requests overlap.
- **C2:** The architecture separates syntax, database inputs, HIR semantics, editor-oriented APIs, and the LSP adapter. The semantic engine receives source and a crate graph without performing its own filesystem I/O.
- **C3:** Salsa-backed queries and body-independent item summaries constrain invalidation. The documented invariant that body changes should not invalidate global derived facts gives an unusually clear performance goal to follow through the implementation. See the [architecture guide](https://rust-analyzer.github.io/book/contributing/architecture.html).

### 2. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**C++ — clangd, in the `clang-tools-extra/clangd` subsystem.** Count the LLVM monorepo once; the separate clangd issue repository is not the implementation. Study how a language server safely schedules work around a compiler AST that is not thread-safe even for reads.

- **C1:** `TUScheduler` and per-file AST workers order operations, manage AST ownership, and discard cancelled or superseded work. The design distinguishes reusable immutable preambles from mutable ASTs and explains which document writes a read observes. [Threading design](https://clangd.llvm.org/design/threads).
- **C2, C3:** A common `SymbolIndex` interface permits dynamic, background, static, and remote indexes to be combined. The dynamic overlay accounts for unsaved edits, while background workers build persistent indexes from compilation commands. This exposes both the freshness problem and a structured way to move expensive project indexing off the request path. [Indexing design](https://clangd.llvm.org/design/indexing).

### 3. [golang/tools](https://github.com/golang/tools)

**Go — gopls, within the official GitHub mirror of Go Tools.** The relevant subsystem is `gopls`; this is explicitly a mirror, not an independently maintained fork. Study the relationship between editor overlays, Go package metadata, and persistent semantic indexes.

- **C1:** Position mapping bridges UTF-8, LSP UTF-16 positions, and Go token positions. Parsing repairs some malformed editor input, while file handles and snapshots provide content identities for concurrent analysis.
- **C2:** Sessions, folders, views, snapshots, metadata graphs, and package analysis have distinct responsibilities, allowing many editor features to share the same project model.
- **C3:** Serialized cross-reference, method-set, and related indexes let navigation avoid retaining every fully type-checked package. The implementation guide explains the cache redesign and the boundary between transient analysis and persistent data. [gopls implementation guide](https://go.dev/gopls/design/implementation). The guide identifies its own update date; treat it as architectural context, not a guarantee that every internal name remains unchanged.

### 4. [dotnet/roslyn](https://github.com/dotnet/roslyn)

**C# and Visual Basic — compiler semantic APIs, workspaces, editor features, and language-server infrastructure.** The relevant code spans the compiler, Workspaces, Features, and LanguageServer layers. Study how a semantic model becomes a reusable substrate for navigation, diagnostics, and transformations across hosts.

- **C1, C3:** Immutable syntax trees, compilations, and solution snapshots allow analyses to work against stable versions. Green/red syntax-tree organization and structural sharing support incremental editing. The engineering inference is that these boundaries make concurrent queries and edits easier to reason about; immutability alone does not prove every feature race-free. [Repository architecture description](https://github.com/dotnet/roslyn/blob/main/.github/memory/ARCHITECTURE.md).
- **C2:** Compiler semantics, workspace state, host-independent features, and host adapters occupy separate layers. Per-language services can be composed without placing editor-specific behavior in the compiler. [Layering diagram](https://github.com/dotnet/roslyn/blob/main/docs/Layering.md).

### 5. [microsoft/pyright](https://github.com/microsoft/pyright)

**TypeScript — Python type checker and language server.** Useful for studying a semantic engine that must support both complete diagnostics and selective, low-latency answers for the file being edited.

- **C1:** The binder establishes scopes and symbols, handles Python's `global` and `nonlocal` rules, and builds control-flow information consumed during type evaluation. These are semantic correctness problems beyond parsing or text matching.
- **C2:** Workspace services, the program dependency model, per-source-file analysis state, binding, type evaluation, and checking have explicit responsibilities. Multiple editor requests can share the same analysis machinery.
- **C3:** Type evaluation is lazy, while the checker drives the fuller evaluation needed for diagnostics. Program management prioritizes open files and relevant dependencies. This is a concrete architecture for controlling how much analysis each interaction requires. [Internal architecture](https://github.com/microsoft/pyright/blob/main/docs/internals.md).

### 6. [eclipse-jdtls/eclipse.jdt.ls](https://github.com/eclipse-jdtls/eclipse.jdt.ls)

**Java — Java language server built around Eclipse JDT.** The document lifecycle handlers are a good starting point for studying how a server keeps editor buffers, compiler working copies, and asynchronous diagnostics aligned.

- **C1:** The base handler tracks document versions, coordinates reconciliation, manages working-copy buffer changes, and detects content changes during operations. Cancellation and rescheduling of validation jobs expose the stale-result problem directly in implementation. [BaseDocumentLifeCycleHandler](https://github.com/eclipse-jdtls/eclipse.jdt.ls/blob/main/org.eclipse.jdt.ls.core/src/org/eclipse/jdt/ls/core/internal/handlers/BaseDocumentLifeCycleHandler.java).
- **C3:** Validation and diagnostic publication are debounced; timing measurements influence bounded delays, and the reconciliation queue prioritizes relevant files. This is more instructive than an undifferentiated background thread pool.
- **C2:** The concrete handler adds distinctions between managed projects and standalone files, including syntax-oriented treatment when a useful classpath is unavailable. Study that adaptation alongside the shared lifecycle machinery. [DocumentLifeCycleHandler](https://github.com/eclipse-jdtls/eclipse.jdt.ls/blob/main/org.eclipse.jdt.ls.core/src/org/eclipse/jdt/ls/core/internal/handlers/DocumentLifeCycleHandler.java).

### 7. [scalameta/metals](https://github.com/scalameta/metals)

**Scala, with Java interfaces — Scala language server.** Metals is valuable for studying the coexistence of build-produced semantic information, interactive compiler services, and cheaper syntax-based navigation.

- **C2:** Workspace services, Build Server Protocol integration, SemanticDB consumers, and version-specific presentation compilers have explicit boundaries. A Java interface helps bridge different Scala compiler versions.
- **C3:** Mtags supplies approximate syntax indexing when full semantic information is unavailable. Top-level scanners intentionally avoid indexing every nested definition, reducing work and memory. SemanticDB from builds and interactive analysis for otherwise uncovered sources provide different cost and precision points.
- **C1:** The distinction between approximate indexing and compiler-backed answers is itself important: engineers can study how a tool remains useful before a project compiles without treating every syntactic result as a fully resolved semantic fact. [Architecture and indexing guide](https://github.com/scalameta/metals/blob/main/architecture.md).

### 8. [haskell/haskell-language-server](https://github.com/haskell/haskell-language-server)

**Haskell — Haskell Language Server, including ghcide and feature plugins.** Count the integrated ghcide subsystem with HLS. Study the path from compiler sessions and dependency information to typed, extensible editor requests.

- **C2:** ghcide coordinates when and how to type-check; project setup is supplied through hie-bios, and plugins consume shared analysis. Compiler-version-specific server builds reflect the practical coupling to GHC APIs. [ghcide component documentation](https://haskell-language-server.readthedocs.io/en/latest/components/ghcide.html).
- **C1:** The explicit-imports plugin example obtains `TypeCheck` and `GhcSessionDeps` results, then uses compiler import-usage information and source locations to construct edits. This provides a concrete study of a semantic rewrite whose correctness depends on the resolved program and compiler session, not merely matching import text.
- **C2:** `PluginDescriptor`, typed handlers, commands, and shared rules make that implementation pattern reusable across features. The [plugin tutorial](https://haskell-language-server.readthedocs.io/en/latest/contributing/plugin-tutorial.html) contains compiled implementation examples; it is evidence about the substantive server, not a tutorial repository included as a candidate.

### 9. [ocaml/ocaml-lsp](https://github.com/ocaml/ocaml-lsp)

**OCaml — OCaml language server using Merlin and build-system integration.** Useful for studying how to isolate changing compiler representations while preserving reusable protocol infrastructure.

- **C2:** The repository separates `jsonrpc`, `jsonrpc-fiber`, `lsp`, `lsp-fiber`, and the concrete server. Its contribution guide explains why compiler-specific `Typedtree` logic should generally remain in Merlin: localizing that dependency reduces the scope of compiler-version migrations. [Component and contribution guide](https://github.com/ocaml/ocaml-lsp/blob/master/CONTRIBUTING.md).
- **C1:** The change history records concrete protocol and edit invariants: negotiated position encodings, document offsets after incremental edits, current document versions in multi-file renames, valid semantic-token ordering, and rejection of malformed requests. These provide focused failure cases to trace into code, rather than a blanket claim of correctness. [Change history](https://github.com/ocaml/ocaml-lsp/blob/master/CHANGES.md).

The repository also documents a practical boundary: Dune diagnostics depend on saved files and completed builds, so they can lag unsaved editor contents.

### 10. [WhatsApp/erlang-language-platform](https://github.com/WhatsApp/erlang-language-platform)

**Rust — Erlang analysis platform and language server.** ELP offers a useful comparison with rust-analyzer: it adopts an IDE-oriented architecture for a different language ecosystem rather than simply wrapping a batch compiler. Its Erlang front end and bundled analysis facilities form one repository entry.

- **C2:** The semantic engine is designed as a reusable library for editor features and other tooling, including linting and refactoring. The LSP service is one consumer of that infrastructure.
- **C3:** Tree-sitter supports incremental parsing and recovery during editing; Salsa caches derived analysis and tracks dependencies for recomputation. The project explains why an incremental engine matters for interactive use.
- **C1:** Working on unfinished, syntactically broken source is an explicit architectural requirement. Study where the implementation separates recoverable syntax from semantic answers rather than assuming compilation succeeds. [Architecture rationale and FAQ](https://github.com/WhatsApp/erlang-language-platform/blob/main/FAQ.md).

## Dynamic-language and scientific-language communities

### 11. [LuaLS/lua-language-server](https://github.com/LuaLS/lua-language-server)

**Lua, with native support code — Lua language server.** Besides its parser and semantic facilities, this repository provides an accessible example of cooperative task scheduling inside an interactive analysis service.

- **C1:** The coroutine scheduler checks task state before resuming or closing tasks, guards asynchronous completion against repeated resumption, and associates cleanup and cancellation with tasks. These are concrete lifecycle invariants worth tracing under cancellation and overlapping callbacks.
- **C3:** Delayed work, throttled scheduling, priority handling, and timing checks make the latency policy visible in a compact implementation. Study how yielding is exposed as an analysis-service primitive rather than hidden inside individual features. [Coroutine scheduler implementation](https://raw.githubusercontent.com/LuaLS/lua-language-server/master/script/await.lua).
- **C2:** The [script source tree](https://github.com/LuaLS/lua-language-server/tree/master/script) separates parser, semantic VM, core features, providers, and workspace responsibilities. This supplies context for following scheduler consumers; the correctness claim above concerns the inspected scheduler, not an audit of all Lua semantics.

### 12. [Shopify/ruby-lsp](https://github.com/Shopify/ruby-lsp)

**Ruby — Ruby language server and declaration indexer.** Study pragmatic semantic assistance for a dynamic language, especially the boundary between reusable syntax infrastructure and deliberately heuristic answers.

- **C2, C3:** Prism listeners and dispatchers let several features share tree traversal. The indexer, request implementations, and add-on interfaces provide reusable infrastructure instead of independent parsers per feature. Fixture tests exercise requests and expected responses. [Contribution and implementation guide](https://shopify.github.io/ruby-lsp/contributing.html).
- **C1:** Dependency identity matters: the design uses Bundler's project context to avoid navigating against the wrong gem versions. The same design discussion explains limits imposed by Ruby's dynamic behavior.
- **C3:** Resolving every constant for semantic highlighting on each keystroke illustrates an explicit accuracy-versus-work tradeoff. The server does not claim to supply a complete Ruby type system; that limitation is part of the study value. [Design and roadmap](https://shopify.github.io/ruby-lsp/design-and-roadmap.html).

### 13. [elixir-lsp/elixir-ls](https://github.com/elixir-lsp/elixir-ls)

**Elixir — Elixir language server, with a debugger in the same repository.** The language-server and incremental analysis portions are the focus. This is the community-maintained continuation of the original ElixirLS, with substantive subsequent development, not a duplicate listing of its predecessor.

- **C1:** The changelog describes document-update/parser races, UTF-16 boundary failures, concurrent analysis problems, and stale diagnostics during incremental checking. These are specific distributed-state and source-coordinate problems an engineer can follow into fixes.
- **C4:** Dated changes across 2024–2026 document incremental Dialyzer evolution, module-dependency tracking, storage changes, and repeated Elixir/OTP compatibility work. The 2026 entries include both newly supported runtime versions and retirement of older configurations; this is evidence of sustained compatibility management rather than age inferred from repository creation.

Start with the [detailed changelog](https://github.com/elixir-lsp/elixir-ls/blob/master/CHANGELOG.md), particularly the incremental Dialyzer and runtime-transition entries. The selection is based on documented mechanisms and failure history, not a claim that every supported runtime combination was tested in this research.

### 14. [clojure-lsp/clojure-lsp](https://github.com/clojure-lsp/clojure-lsp)

**Clojure — Clojure/ClojureScript language server and programmatic refactoring tools.** Study how analyzer output, a shared project database, and feature queries can support editor, command-line, and library consumers.

- **C2:** The development guide maps handlers to features and queries over a shared database, including clj-kondo analysis, classpath information, and dependency relationships. It distinguishes the reusable core from the CLI/LSP entry point. [Development architecture](https://clojure-lsp.io/development/).
- **C3:** Cached analysis is reused across startups subject to dependency/configuration changes. Completion explicitly offers a choice between using available, potentially stale analysis and waiting for current analysis. Lazy Java member analysis further exposes a memory-versus-eagerness decision. [Settings and analysis behavior](https://clojure-lsp.io/settings/).

The development guide also describes performance regression runs with latency percentiles and thresholds. That is useful complexity-management evidence; it is not an independently reproduced speed comparison with other servers.

### 15. [fortran-lang/fortls](https://github.com/fortran-lang/fortls)

**Python — Fortran language server.** A useful smaller-community implementation for studying semantic navigation across Fortran's scopes, interfaces, source forms, and import rules. It is a substantively evolved fork of the earlier Fortran server, counted here only once.

- **C1:** The documented internal model includes `USE` restrictions and renaming, procedure signatures, visibility, includes, and type/rank selection. Parsing utilities also address incomplete expressions and fixed/free-form distinctions. These are concrete sources of navigation errors beyond ordinary identifier lookup.
- **C2:** Scope, object, and signature representations form shared infrastructure for definition lookup, hover, completion, and related server operations. The [internal API reference](https://fortls.fortran-lang.org/fortls.html) exposes these data types and their operations, making the semantic model a practical starting point.

**Status and boundary:** The repository describes a maintenance-focused role while the community develops a compiler-backed successor using LFortran. It also documents semantic limitations; fortls should not be read as a complete Fortran compiler front end. Those notices make it a qualified study target rather than an unqualified recommendation for new feature investment.

### 16. [julia-vscode/LanguageServer.jl](https://github.com/julia-vscode/LanguageServer.jl)

**Julia — Julia language server integrating symbol and static-analysis services.** Study how asynchronous package-symbol discovery is integrated with live document analysis and protocol lifecycle handling.

- **C1:** Client messages and symbol-server results enter a combined queue. The implementation tracks open-file versions, wraps request/notification handling to enforce shutdown state, and rebuilds analysis environments when symbol information changes. Those transitions reveal where stale symbols and document state must be reconciled.
- **C2:** `LanguageServerInstance` connects JSON-RPC transport, documents, Julia workspace state, SymbolServer stores, and StaticLint environments through identifiable interfaces. The same state supports several navigation and diagnostic features.
- **C3:** Symbol information is cached, and relinting traverses document roots without repeatedly processing the same root. [Language-server instance implementation](https://raw.githubusercontent.com/julia-vscode/LanguageServer.jl/main/src/languageserverinstance.jl). The [source directory](https://github.com/julia-vscode/LanguageServer.jl/tree/main/src) provides the surrounding request and document modules.

## Reusable language frameworks and document-language servers

### 17. [eclipse-langium/langium](https://github.com/eclipse-langium/langium)

**TypeScript — language-engineering framework with LSP integration.** Langium belongs here as infrastructure for building semantic language services, particularly DSLs, rather than as one language-specific server.

- **C1:** Its document lifecycle distinguishes parsing, content indexing, scope computation, linking, reference indexing, and validation. The order is consequential: cross-references must not be resolved before the required descriptions and scopes exist.
- **C2:** Replaceable services such as scope computation/providers and extensible document-build phases allow languages to share a substantial pipeline while customizing semantics.
- **C3:** Reference indexes identify documents affected by changes, permitting targeted relinking. Symbol descriptions carry URIs and AST paths so discovery need not eagerly resolve every reference. These mechanisms connect correctness dependencies to incremental work. [Document lifecycle and service extension guide](https://langium.org/docs/reference/document-lifecycle/).

### 18. [tamasfe/taplo](https://github.com/tamasfe/taplo)

**Rust — TOML toolkit with an embeddable language server.** A compact contrast to compiler-heavy projects: configuration languages still require exact source preservation, semantic validation, and editor-friendly treatment of broken documents.

- **C1:** The parser builds a lossless Rowan syntax tree that retains whitespace, comments, and positions. Syntax errors and DOM-level semantic validation, such as duplicate definitions, are distinct; the DOM can still be useful after parsing incomplete input. [Taplo library architecture and API](https://docs.rs/taplo/latest/taplo/).
- **C2:** The syntax/DOM toolkit serves several consumers, while the language server is generic over its environment and can be embedded with the asynchronous LSP support layer. This is a concrete reusable boundary between language analysis and host facilities. [Language-server embedding guide](https://taplo.tamasfe.dev/lib/rust/taplo-lsp.html).

This entry is selected for its representation and embedding choices, not as a claim of universal TOML/schema completeness or current release cadence.

### 19. [Myriad-Dreamin/tinymist](https://github.com/Myriad-Dreamin/tinymist)

**Rust, with TypeScript frontend integration — Typst language service and related document tooling.** Useful for studying a server whose queries range from local syntax to expensive, version-sensitive compilation and rendering.

- **C1:** Actors own resources and communicate through messages. The design distinguishes source queries, semantic world queries, and queries requiring a specific compilation state, exposing which version and resource each answer depends on.
- **C3:** Queries request different levels of access according to their needs; source-local operations need not pay the cost of a full compiled world. Separate compile and render actors, including cached render state, make the concurrency and cost model explicit. [Architecture principles](https://myriad-dreamin.github.io/tinymist/principles.html).
- **C2:** AST matchers, lexical hierarchy, definition/use analysis, and type-related analysis supply common infrastructure for multiple editor capabilities. [Analysis overview](https://myriad-dreamin.github.io/tinymist/overview.html).

## Persistent indexes and cross-repository semantic navigation

### 20. [github/stack-graphs](https://github.com/github/stack-graphs)

**Rust — language-independent name-resolution graph library.** **Historical study target: GitHub's repository notice says it is no longer supported or updated.** Its distinct name-binding model remains worth studying; inclusion does not imply ongoing maintenance or a current product commitment.

- **C1:** Resolution paths manipulate symbol and scope stacks, enabling a binding problem to suspend one lookup while resolving another. Path validity, scope constraints, and cycle handling are central correctness concerns.
- **C2:** Language-specific front ends can produce graphs consumed by a shared resolution engine, rather than implementing an unrelated whole-program resolver for every language.
- **C3:** Per-file graph fragments and partial-path stitching support incremental construction without requiring every file's analysis to inspect the entire repository. The library exposes arenas, caches, and cancellation alongside the graph abstractions. [Library design and module reference](https://docs.rs/stack-graphs/latest/stack_graphs/).

### 21. [kythe/kythe](https://github.com/kythe/kythe)

**C++, Go, and Java — semantic indexing and cross-reference infrastructure.** Study the interfaces between build extraction, language-specific analysis, a common graph representation, and navigation-serving systems.

- **C2:** Extractors capture compilation inputs; indexers emit shared facts and edges; downstream tools consume the language-independent representation. This separates language semantics from the mechanics of cross-reference presentation. [System overview](https://kythe.io/docs/kythe-overview.html).
- **C1:** VNames distinguish entities through signature, corpus, root, path, and language. Ticket encoding and canonical identity rules matter when combining indexes from generated code, separate builds, or different languages.
- **C3:** The compact interchange/storage model is deliberately separated from denormalized serving tables. Consumers can construct query-oriented indexes without forcing extraction and analysis to use the same physical layout. [Storage model and identity rules](https://kythe.io/docs/kythe-storage.html).

Some overview material is historical. Use the repository for present subsystem availability; the cited design is evidence for the representation and pipeline, not a current deployment benchmark.

### 22. [sourcegraph/scip-clang](https://github.com/sourcegraph/scip-clang)

**C++ — Clang-based SCIP indexer for C, C++, and CUDA.** A strong complement to clangd: the focus is offline, cross-translation-unit navigation artifacts rather than live editor buffers.

- **C1:** The design discusses cross-translation-unit symbol identity, macro-generated entities, preprocessing-dependent header contents, and worker crashes or hangs. Process boundaries and recoverable jobs expose failure containment as part of indexing architecture.
- **C3:** Driver/worker queues, disk-backed job shards, and subsequent merging address throughput and memory pressure. Deduplicating suitable header output reduces repeated emission, while the documentation distinguishes that from eliminating repeated semantic parsing.

The [design document](https://github.com/sourcegraph/scip-clang/blob/main/docs/Design.md) is the main entry point. It also explains deliberately optimistic handling of some dependent template names: the navigation index is not a claim of exact resolution for every C++ construct. The document includes proposed extensions; this entry relies on its described indexing architecture, not on assuming every proposal shipped.

### 23. [facebookincubator/Glean](https://github.com/facebookincubator/Glean)

**Haskell and C++ — source-code fact database, with Glass navigation services and a generic LSP subsystem.** The category-relevant portions are language indexers, derived navigation facts, Glass, and LSP access; the monorepo counts once.

- **C2:** Typed schemas describe language-specific facts, while derived facts can provide language-neutral navigation concepts. Angle queries, Glass symbol APIs, and LSP access separate semantic storage from client presentation. This permits several languages and tools to share a substantial infrastructure layer.
- **C3:** Facts form an immutable, deduplicated graph stored using RocksDB. Selective fact retention and derived queries make storage size and serving requirements explicit design choices instead of requiring every consumer to keep a full compiler representation alive.
- **C1:** Typed fact references and immutable database structure provide concrete identity and consistency boundaries to examine when joining information from many source entities. [Architecture, fact model, and navigation overview](https://glean.software/docs/introduction/).

## Coverage, search process, and limitations

Discovery used more than six meaningfully different live search formulations. The main search angles were:

1. Incremental language-server architecture, snapshots, cancellation, and caches: Rust, C/C++, and Go.
2. Compiler API integration and build-system boundaries: Java, Scala, Haskell, OCaml, and .NET.
3. Dynamic-language analysis and scheduling: Python, Ruby, Lua, Elixir, and Clojure.
4. Scientific and less frequently covered language communities: Fortran and Julia, with additional discovery searches for R and Zig.
5. Reusable language-service frameworks and DSL infrastructure: Langium and related framework candidates.
6. Document/configuration-language tooling: Typst and TOML.
7. Erlang server alternatives and incremental semantic engines.
8. Cross-repository semantic indexing, name binding, SCIP, graph storage, Kythe, and Glean.
9. Hardware-description-language servers and additional indexing alternatives, used to test whether the selection was missing a distinct, well-supported architecture family.

Every retained repository's canonical GitHub page was opened, and at least one additional primary implementation or documentation source was read. Additional searches increasingly returned already-covered families, editor integrations, or candidates requiring more verification than their apparent incremental coverage justified. Hardware-description languages, COBOL, R, and Zig were not comprehensively verified; this is a diverse selection, not a census of all servers.

Editor clients, configuration collections, generated protocol wrappers without substantial semantic machinery, awesome lists, and ordinary lexical/tag search tools were excluded. “Semantic search” products based only on embeddings or natural-language retrieval were outside scope unless they also supplied the symbol-resolution infrastructure considered here. Compiler repositories were included only when a concrete language-service or navigation subsystem was identified.

The checked [erlang-ls/erlang_ls repository](https://github.com/erlang-ls/erlang_ls) explicitly reports that it is unmaintained and directs users toward ELP; it was not added as another entry. Evolved community continuations such as fortls and ElixirLS were counted once, without also listing their predecessors. Stack Graphs was retained despite its explicit support notice because its resolution architecture contributes a materially different study target. Go Tools is identified as an official mirror.

Sources include moving branches and versioned or “latest” documentation, sometimes with older architectural descriptions. Their presence does not establish current maintenance intensity, universal feature correctness, or measured comparative performance. Compatibility history was used for C4 only where the inspected material documented sustained changes and concrete compatibility management. All work was read-only internet research; no dependencies were installed, candidate repositories cloned, maintainers contacted, or external services modified.
