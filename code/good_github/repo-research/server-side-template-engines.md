# Server-side template engines

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing engines that render HTML or other documents on a server. It includes runtime interpreters, compilers to host-language code or bytecode, statically typed template generators, markup-aware processors, and languages intended for user-authored templates. General document rendering is included where the engine also has a clear web/server role. Browser-capable engines qualify through their server implementation; frontend component frameworks and template integration wrappers are outside the focus. The Go repository is counted once, specifically for its standard-library template subsystem.

Criteria are evidence-based study recommendations, not ratings of every component:

- **C1 — Difficult correctness:** invariants, concurrency, language semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or language mechanisms supporting different applications.
- **C3 — Performance with structure:** concrete techniques addressing compilation, rendering, allocation, caching, or latency costs within an understandable design.
- **C4 — Sustained evolution:** years of change accompanied by compatibility management, testing, or explicit control of complexity.

The explanations below distinguish template-author trust from untrusted render data. Output escaping, object-access restrictions, and resource limits solve different problems. Architectural study value is an inference from the linked primary material; it is not a security certification or a comparative performance benchmark. Unless explicitly stated, inclusion makes no claim about current maintenance cadence.

## Python and Ruby

### 1. [pallets/jinja](https://github.com/pallets/jinja)

**Python — extensible, compiled template language.** A particularly useful study of how a template compiler cooperates with a configurable runtime, including the difficult boundary between convenient Python-like expressions and restricted execution.

- **C1:** The sandbox directs the compiler to generate checked operations. Attribute access, calls, mutation, and selected operators have different interception rules; ordinary operators are emitted directly unless interception is requested. The documentation also explains why this does not itself bound CPU or output growth. [Sandbox architecture](https://jinja.palletsprojects.com/en/stable/sandbox/).
- **C4:** The changelog documents several years of concrete complexity management: a bytecode-cache race fix in 2022, async-generator cleanup and indirect string-format checks in 2024, and prevention of an attribute-filter sandbox bypass in 2025. It also records removals of previously deprecated APIs and compiled-template compatibility consequences. [Changelog](https://raw.githubusercontent.com/pallets/jinja/main/CHANGES.rst).

### 2. [sqlalchemy/mako](https://github.com/sqlalchemy/mako)

**Python — templates compiled into Python modules.** Study a design that deliberately preserves host-language calling and scoping behavior, rather than introducing a restricted expression language.

- **C1:** The runtime differentiates missing values from explicit `None`, offers immediate strict-undefined errors, and copies contexts across definitions and inheritance chains. Mutating one context does not reliably update the others; this is a concrete scope invariant, not merely a dictionary API.
- **C2:** A central `Context` combines variables with a stack of output buffers. Definitions, inheritance, filtering, and capture can share that interface while directing writes to the current buffer. The runtime guide explains the generated `render_body` and `render_*` functions and their context lookups. [Runtime and generated-function model](https://docs.makotemplates.org/en/latest/runtime.html).

The repository describes an embedded-Python model; this is an engine for trusted template code, not an isolated language for arbitrary authors.

### 3. [malthe/chameleon](https://github.com/malthe/chameleon)

**Python — HTML/XML page templates using TAL, METAL, and translation attributes.** Its document-oriented syntax offers a useful contrast to engines that regard surrounding markup as opaque text.

- **C2:** TAL controls document structure, METAL supplies macro slots, and the translation layer supports named interpolation and translated attributes. These mechanisms compose: translated content can contain named dynamic pieces, and slots can participate in loops. [Language reference](https://chameleon.readthedocs.io/en/latest/reference.html).
- **C3:** Templates are translated into Python bytecode, and extension authors can supply expression compilers that return Python AST nodes. The library separates string/file template constructors and loaders, and documents the performance cost of automatic reloading. This makes the compilation boundary directly inspectable. [Library and expression-compiler documentation](https://chameleon.readthedocs.io/en/latest/library.html).

The documentation contains older environment examples; no claim about current Python-version support or benchmark ratios is made here.

### 4. [Shopify/liquid](https://github.com/Shopify/liquid)

**Ruby — constrained, customer-facing template language.** Study the separation of parse/compile work from rendering, together with application-specific language environments.

- **C1:** Resource accounting distinguishes output length, render work, and assignment/capture work. The implementation restores capture state with `ensure`, and supports cumulative counters as well as per-render counters. The README explicitly notes that limiting output alone does not bound empty-body iteration. [Resource-limit implementation](https://github.com/Shopify/liquid/blob/main/lib/liquid/resource_limits.rb).
- **C2:** Scoped environments register tags and filters without globally replacing another application's behavior. Strict parsing, missing-variable handling, and missing-filter handling are independently configurable, allowing an editor and a production renderer to adopt different policies. [Environment and error-mode guide in the repository](https://github.com/Shopify/liquid#concept-of-environments).

## PHP

### 5. [twigphp/Twig](https://github.com/twigphp/Twig)

**PHP — extensible compiler-based template engine.** The lexer → token stream → AST → PHP class pipeline is unusually easy to follow through the official internals guide.

- **C2:** Nodes, token parsers, extensions, and the compiler provide explicit places to add language constructs without patching unrelated rendering code. The guide shows both intermediate representations and generated PHP. [Compiler internals](https://twig.symfony.com/doc/3.x/internals.html).
- **C1:** Sandbox policy governs tags, filters, functions, tests, methods, and properties, with checks at different execution stages. The documentation explains partial-output failures, trusted extension code, and the absence of resource limits. These are valuable examples of how a language boundary depends on its embedding application. [Sandbox design and limitations](https://twig.symfony.com/doc/3.x/sandbox.html).

The sandbox documentation follows the evolving 3.x line; consult the installed version before copying its API examples.

### 6. [nette/latte](https://github.com/nette/latte)

**PHP — markup-aware compiler with contextual escaping.** Study how understanding HTML structure changes the compiler's responsibilities.

- **C1:** Latte distinguishes text, attributes, URLs, JavaScript, and nested contexts. Its guide demonstrates why escaping a JavaScript value inside an HTML attribute requires more than a generic HTML substitution, and describes URL-scheme checks. [Context-aware escaping](https://latte.nette.org/en/safety-first).
- **C2:** `Engine` exposes distinct parse, compiler-pass, and generation phases. Extensions contribute tags and ordered AST passes, while loaders and runtime functions remain separate interfaces. The source also shows how generated class/cache identities depend on configuration. [Engine implementation](https://github.com/nette/latte/blob/master/src/Latte/Engine.php).

The useful evidence is the context handling and compiler structure, not the documentation's comparative marketing claims.

### 7. [smarty-php/smarty](https://github.com/smarty-php/smarty)

**PHP — template engine with compiled templates and rendered-output caching.** Especially useful for studying caches whose dependencies cross template boundaries.

- **C1:** One cached result can depend on included or inherited templates and configuration files. Compile checking invalidates the result when those dependencies change; current-lifetime and saved-lifetime modes intentionally have different expiration semantics.
- **C3:** Output caching avoids repeated rendering, `isCached()` lets the application avoid expensive data preparation, and `nocache` regions retain dynamic content within an otherwise cached page. These are distinct optimizations with explicit correctness tradeoffs, rather than a single undifferentiated cache. [Caching architecture and examples](https://smarty-php.github.io/smarty/stable/api/caching/basics/).

## JVM engines

### 8. [apache/freemarker](https://github.com/apache/freemarker)

**Java — embeddable FTL interpreter and object-model adapter.** This is an **official substantive GitHub mirror**, which Apache also permits linked contributors to write to. [Official repository locations](https://freemarker.apache.org/sourcecode.html).

- **C1:** Shared `Configuration`, `Template`, and data-model objects are to be treated as immutable after setup; a separate environment holds each processing invocation's runtime state. The guide explains how this avoids expensive synchronization and why changing a cached template's configuration is unsafe. [Multithreading contract](https://freemarker.apache.org/docs/pgui_misc_multithreading.html).
- **C2:** `ObjectWrapper` maps Java objects into a family of `TemplateModel` interfaces. Container adapters recursively wrap child values, while pre-wrapped models can bypass conversion. This is a substantial reusable boundary between a host object graph and an interpreted language. [Object-wrapper architecture](https://freemarker.apache.org/docs/pgui_datamodel_objectWrapper.html).

### 9. [thymeleaf/thymeleaf](https://github.com/thymeleaf/thymeleaf)

**Java — event-based server renderer for natural HTML/XML templates and textual modes.** Study the extension system as a structured processing engine rather than a string-substitution library.

- **C2:** Dialects supply processors, expression-object factories, execution attributes, and pre/post-processors. Different processor interfaces handle individual tags or whole element models, supporting both local transformations and body-aware operations.
- **C1:** Processor precedence determines ordering. Tag events are immutable; processors request mutations through a structure handler instead of editing shared input directly. The separation between context-visible expression objects and internal execution attributes is another explicit boundary. [Extension architecture and processor contracts](https://www.thymeleaf.org/doc/tutorials/3.1/extendingthymeleaf.html).

The [main tutorial](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html) establishes the server-rendering role and explains the distinct HTML, XML, text, JavaScript, CSS, and raw modes.

### 10. [PebbleTemplates/pebble](https://github.com/PebbleTemplates/pebble)

**Java — Twig-inspired engine with inheritance and optional parallel rendering.** Particularly relevant when expensive template sections or slow data access affect response latency.

- **C1:** Compiled templates can be reused across threads only when their backing data is also thread-safe. Parallel sections are explicitly activated through an executor and the `parallel` tag, making the concurrency contract visible.
- **C3:** The engine supports parallel sections and incremental output through `flush`. Its guide explains a subtle limitation: a block rendered through the `block` function uses an internal `StringWriter`, so flushing it does not flush the application's writer. [Concurrency, streaming, and buffering](https://pebbletemplates.io/wiki/guide/high-performance/).

The repository also records loader and Spring-integration breaking changes, useful context when comparing versions; no throughput ranking is inferred.

### 11. [casid/jte](https://github.com/casid/jte)

**Java/Kotlin — typed templates compiled into JVM classes.** Study the trade between development-time recompilation and a production runtime that loads generated classes.

- **C1:** HTML mode applies different escaping operations to tag bodies, attributes, and JavaScript contexts. Boolean attributes require boolean expressions and disappear when false, showing how HTML semantics affect generated code. [HTML rendering rules](https://jte.gg/html-rendering/).
- **C3:** The build can either generate template source before application compilation or compile template classes afterward. Production can load those classes from a directory or application JAR, eliminating template compilation on the server. [Precompilation architecture](https://jte.gg/pre-compiling/).

These are trusted Java/Kotlin templates; contextual output escaping does not restrict their host-language execution.

### 12. [playframework/twirl](https://github.com/playframework/twirl)

**Scala — Play's template compiler, also packaged as its own project.** Study how templates become ordinary typed functions rather than an independently interpreted runtime language.

- **C1:** A template's parameter declaration becomes a typed Scala call interface. Dynamic output is escaped according to the output format, while an explicit content wrapper such as `Html` changes that treatment. Option and collection values have documented unwrapping behavior, so rendering semantics extend beyond calling `toString` on everything.
- **C2:** Templates compile to classes with callable `apply` methods, and reusable blocks, imports, and scoped values compose through normal Scala mechanisms. HTML, XML, and other textual outputs use the same underlying model. [Compilation, composition, and escaping guide](https://www.playframework.com/documentation/3.0.x/ScalaTemplates).

## JavaScript engines with server runtimes

### 13. [mozilla/nunjucks](https://github.com/mozilla/nunjucks)

**JavaScript — Jinja-inspired engine with synchronous and asynchronous rendering.** A useful compiler/runtime study when filters, tags, or template loading may perform asynchronous work.

- **C1:** Async loaders require the async rendering API; asynchronous filters and extensions must be known at compilation time. The API guide explains how evaluation pauses for callbacks and why mixing assumptions from the synchronous path produces failures.
- **C2:** Environments assemble loaders, filters, globals, and extensions; precompilation can consume the same environment configuration used for rendering. This is a reusable bridge between language customization and generated JavaScript. [API and asynchronous compilation contracts](https://mozilla.github.io/nunjucks/api.html).

The same guide explicitly says Nunjucks does **not** sandbox user-authored templates. Async support is an integration capability, not evidence that rendering is inherently faster.

### 14. [pugjs/pug](https://github.com/pugjs/pug)

**JavaScript — indentation-based HTML compiler for Node.js and browsers.** Counted once despite its several compiler packages.

- **C2:** The coordinator connects lexing/parsing, dependency loading, filter processing, linking, and code generation. Plugins can intervene at named phases or replace resolution, reading, and code generation. Dependency tracking is returned with the generated function. [Compiler coordinator](https://raw.githubusercontent.com/pugjs/pug/master/packages/pug/lib/index.js).
- **C3:** Templates compile to reusable JavaScript functions, and rendering can cache those functions by filename. Options expose meaningful tradeoffs: shared versus inlined runtime helpers, namespace-based local access, and generated debugging instrumentation. [Compiler and rendering API](https://pugjs.org/api/reference.html).

Study the package boundaries and generated output together; the template language permits JavaScript and is not an untrusted-author sandbox.

### 15. [handlebars-lang/handlebars.js](https://github.com/handlebars-lang/handlebars.js)

**JavaScript — helper/partial-based engine usable in Node.js and browsers.** Study the interaction between a relatively constrained template syntax and JavaScript's dynamic object model.

- **C1:** Runtime options govern prototype property and method access, with special handling for dangerous names. The documentation explains why enabling permissive compatibility options can expose code execution, and separates per-render helpers and partials from global registrations. [Runtime access controls](https://handlebarsjs.com/api-reference/runtime-options.html).
- **C3:** Compilation can specialize for known helpers and omit selected checks when stronger input assumptions are supplied. Precompilation separates compiler work from the execution runtime, while source-map options preserve debuggability. [Compilation and specialization options](https://handlebarsjs.com/api-reference/compilation.html).

The access controls are useful correctness material, not a blanket guarantee that arbitrary templates and helper sets are safe.

## Go

### 16. [golang/go](https://github.com/golang/go)

**Go — specifically `html/template` and its `text/template` foundation.** This language monorepo is counted once. GitHub is the **official source mirror**, as stated by the [canonical Go repository](https://go.googlesource.com/go.git/).

- **C1:** `html/template` analyzes HTML, JavaScript, CSS, and URI contexts and inserts escaping stages into action pipelines. Its documentation describes structure-preservation and code-effect invariants, rejects unsafe contexts, and explains trusted-content types that deliberately bypass ordinary treatment.
- **C2:** It wraps the `text/template` interface rather than introducing a separate application API. Named templates, associated template sets, function maps, cloning, and execution to writers remain reusable across applications. [Package contracts and contextual-rewriting examples](https://pkg.go.dev/html/template).

The documented trust model assumes trusted template authors and potentially hostile input data. The recommended study target is the template subsystem, not the entire Go toolchain.

### 17. [a-h/templ](https://github.com/a-h/templ)

**Go — typed HTML component/template generator for server rendering.** Study generated Go functions and their interoperability with hand-written components.

- **C2:** Generated functions return a small `Component` interface whose `Render` method accepts a context and `io.Writer`. Ordinary Go code can implement the same interface, and components can be distributed through Go modules. [Component contract](https://templ.guide/core-concepts/components/).
- **C1:** The contract explicitly allows partial output before an error and recommends buffering when atomic output is required. Separately, typed URL/script mechanisms and context-specific restrictions control injection surfaces; hand-written components remain responsible for their own escaping. [Injection rules](https://templ.guide/security/injection-attacks/).

This combines a useful failure contract with typed composition. The security guide is version-sensitive and should be read alongside the generator version in use.

### 18. [CloudyKit/jet](https://github.com/CloudyKit/jet)

**Go — dynamic template interpreter with inheritance and composition.** A smaller codebase worth comparing with both `html/template` and generated-Go approaches.

- **C2:** `Set` owns loading, parsing, caches, global variables, delimiters, and escaping policy through separate interfaces and options. Relative template resolution is centralized there. [Set implementation](https://raw.githubusercontent.com/CloudyKit/jet/master/set.go).
- **C3:** The default parsed-template cache is concurrency-safe; development mode bypasses it. Rendering obtains runtime state from a pool and follows the inheritance chain before executing the root, exposing concrete allocation and reuse choices in a compact execution path. [Execution entry point](https://raw.githubusercontent.com/CloudyKit/jet/master/exec.go).

The repository warns that parts of its wiki are out of date; this entry relies on the source rather than the wiki's older version and speed comparisons.

## Rust

### 19. [mitsuhiko/minijinja](https://github.com/mitsuhiko/minijinja)

**Primarily Rust — embedded Jinja-compatible runtime; repository also contains other language surfaces.** Counted once, with the Rust engine as the study target.

- **C1:** Optional fuel accounting charges VM instructions per render, and recursion limits and undefined-value policies are separately configurable. This makes execution work and language failure behavior explicit rather than relying only on an output-size limit.
- **C2:** `Environment` owns configuration and loaded templates, with both borrowed and owned template-source APIs, custom loaders, filters, functions, and formatter callbacks. Source lifetimes and `Send`/`Sync` callback bounds are meaningful parts of the embedding contract. [Environment API and execution controls](https://docs.rs/minijinja/latest/minijinja/struct.Environment.html).

The repository establishes dynamic web-template use as well as other embedding roles; Jinja compatibility should be treated as a documented subset, not identity with Python Jinja.

### 20. [Keats/tera](https://github.com/Keats/tera)

**Rust — Jinja/Django-inspired runtime engine; inspected material covers the v2 rewrite.** Useful for studying deliberate language evolution rather than assuming all engines with similar delimiters share semantics.

- **C1:** The migration guide specifies short-circuit evaluation and precise undefined-value behavior, including when chained access must fail. Template compilation now checks the presence of registered filters, functions, tests, and components. [v1-to-v2 semantic changes](https://raw.githubusercontent.com/Keats/tera/master/MIGRATION.md).
- **C2:** Custom callable traits use typed arguments, keyword extraction, and render state; the API handles type mismatches and missing arguments. Components replace the earlier macro model, while dependency-heavy builtins move to the companion crate in the same repository. [Current API and language guide](https://keats.github.io/tera/).

The guide explicitly says escaping is not context-sensitive. Old v1 API examples and assumptions should not be silently applied to v2.

### 21. [askama-rs/askama](https://github.com/askama-rs/askama)

**Rust — compile-time template generator driven by a typed context struct.** Study how a procedural macro turns a template into inspectable trait implementations.

- **C1:** Context fields and template expressions participate in Rust's compilation model, while filename/content-type hints select escaping behavior. The derive options distinguish inline sources, paths, and explicitly chosen escape modes, exposing important configuration invariants.
- **C2:** Generated template traits, reusable inheritance, and block-specific rendering support full documents and fragments. The derive can generate named block views without moving each fragment into another file; debug options print the AST or generated code for inspection. [Template creation and derive architecture](https://askama.rs/en/stable/creating_templates.html).

The [introduction](https://askama.rs/en/stable/) explains the compile-time boundary and typed context model. This is the current `askama-rs` repository, not a separately counted historical fork or old owner URL.

## .NET

### 22. [scriban/scriban](https://github.com/scriban/scriban)

**C# — embeddable scripting/template engine with a Liquid parsing mode.** Study the object model, AST-backed execution, and the practical limits of an embedded-language safety policy.

- **C1:** `TemplateContext` has separate controls for iteration, recursion, string conversion, output growth, and regex work. The documentation carefully distinguishes these controls from a process sandbox and describes the danger of exposing powerful .NET object graphs. [Runtime controls and boundaries](https://scriban.github.io/docs/runtime/safe-runtime/).
- **C2:** `ScriptObject`/`ScriptArray` provide explicit template data, while member-renaming and filtering delegates adapt reflected .NET models. Dictionary entries and reflected members follow different rules, an important abstraction boundary for application embedding and Native AOT usage. [Member adaptation contracts](https://scriban.github.io/docs/runtime/member-renamer/).

In particular, a member filter is documented as an exposure convenience, not a complete security boundary.

### 23. [sebastienros/fluid](https://github.com/sebastienros/fluid)

**C# — Liquid implementation with ASP.NET view-engine integrations.** A strong study of shared compiled artifacts versus render-local state.

- **C1:** The documented contract allows shared parsers and compiled templates, but requires a fresh non-thread-safe context per render. The context implementation checks cancellation and configured resource limits, and enforces reverse-order scope release. [TemplateContext implementation](https://raw.githubusercontent.com/sebastienros/fluid/main/Fluid/TemplateContext.cs).
- **C2:** Local, write-through, and isolated scopes encode different lookup and assignment behavior for loops, includes, and the `render` tag. Immutable options and custom model-access mappings separate application configuration from per-render values. [Thread safety and scope contracts](https://github.com/sebastienros/fluid#thread-safety).

The current README treats the reachable model object graph as readable template data. This report does not assume that older allowlist-oriented descriptions accurately describe every current access path.

## Perl and Erlang

### 24. [cpan-authors/Template2](https://github.com/cpan-authors/Template2)

**Perl — Template Toolkit.** The former `abw/Template2` URL redirects here; this is one project, not two entries. Its explicit runtime architecture makes it useful beyond its original web ecosystem.

- **C2:** The frontend delegates to a service, which schedules processing through a context. Providers supply compiled documents, a parser produces Perl subroutines, and a stash owns variable access. Those interfaces let applications change storage, embedding, and variable behavior independently.
- **C1:** The service centralizes missing-template, parsing, plugin, and execution failures, while its error-recovery mechanism and pre/post-processing stages impose an execution protocol. Compiled documents call back into the context for runtime resources instead of reimplementing them. [Architecture and execution walkthrough](https://template-toolkit.org/docs/manual/Internals.html).

The repository's API documentation also demonstrates Apache/mod_perl output integration, establishing the server-rendering role. The internals guide is useful architectural evidence, not proof that every legacy integration remains supported.

### 25. [erlydtl/erlydtl](https://github.com/erlydtl/erlydtl)

**Erlang — Django-template-language compiler to Erlang bytecode. Historical/maintenance-limited selection:** the repository explicitly contains a call for maintainers and targets Django 1.6-era semantics. Inclusion is for implementation study, not an assertion of contemporary Django compatibility.

- **C2:** Compiler context separates readers, scanners, tag/filter libraries, translations, record metadata, and extension hooks. The public API compiles strings, files, or directories, making the engine adaptable to multiple server-loading arrangements. [Compiler/context implementation](https://raw.githubusercontent.com/erlydtl/erlydtl/master/src/erlydtl_compiler.erl).
- **C3:** Compilation produces reusable BEAM code; documented options replace selected variables with constants and avoid recompilation when source checksums have not changed. Binary-versus-list strings, emitted debug source, and returned compiler diagnostics expose the tradeoffs around the generated artifact. [Compilation options and maintenance statement](https://github.com/erlydtl/erlydtl#template-compilation).

## Coverage and search notes

Discovery used live web searches with more than six distinct formulations. The search angles included Python sandbox/bytecode engines; PHP contextual escaping and caches; Java inheritance, compilation, and concurrency; JavaScript asynchronous loaders and compiler packages; Go runtime versus generated templates; Rust runtime versus derive-based engines; .NET Liquid implementations and object exposure; and Perl, Scala, Erlang, C++, Haskell, and Elixir communities. Later searches increasingly returned additional Jinja/Liquid variants, integration packages, and examples; the selection stops after covering the major contrasting architectures rather than collecting every port.

Every retained canonical GitHub repository was opened, including the Template Toolkit redirect. Each entry also uses at least one opened, distinct primary document or implementation source; rereading a README through a raw URL was not counted as independent evidence. Source trees and current documentation resolved several stale assumptions: Tera now documents a v2 rewrite, Fluid's current model-access contract differs from older summaries, Jet's wiki is versioned behind its main source, and the FreeMarker and Go GitHub repositories are official mirrors.

Exclusions include frontend-only renderers, framework adapters without their own engine, tutorial implementations, awesome lists, and duplicate language bindings/forks. Framework-owned engines such as Blade, Razor, Django templates, and EEx were not comprehensively audited in this report; the emphasis is independently inspectable engines, with the standard-library Go subsystem as a deliberate exception. C++ and Haskell candidates surfaced in the broader discovery pass but were not retained without completing the same implementation review. LLM-chat-specific template implementations were outside the web/document-server focus.

This was a read-only documentation and source review: no candidate repositories were cloned, dependencies installed, or code executed. Some guessed documentation routes returned errors; retained citations use successfully opened alternatives. Moving branch and versionless documentation links can change after the research date. No numerical speed comparisons, star-based quality rankings, or unsupported maintenance claims are used.
