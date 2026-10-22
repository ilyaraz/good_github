# Module bundlers and tree-shaking optimizers

Research date: **2026-10-09**

This report selects **23 GitHub repositories** implementing module bundling, dependency-graph partitioning, or the semantic dead-code elimination that makes tree shaking effective. It covers general web bundlers, incremental and development bundlers, CommonJS/AMD systems, whole-program JavaScript optimizers, and a Lua/Luau implementation. Compressor toolkits are identified separately: removing unused declarations within an already assembled program is not the same operation as resolving and bundling an import graph. Monorepos count once, with the relevant subsystem identified.

The selection is a guide to code worth studying, not a claim that every component is exemplary or that every project is suitable for new deployments. Criteria are engineering judgments grounded in the linked primary material. Archived projects are explicitly marked; an unarchived repository is not, by itself, evidence of ongoing maintenance. Source links follow the inspected branches and may evolve.

## Criteria legend

- **C1 — Correctness:** difficult invariants, concurrency, language or numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and representations supporting multiple use cases.
- **C3 — Performance and structure:** concrete performance constraints addressed through an understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or complexity management; age alone does not qualify.

## General-purpose bundlers and tree shakers

### 1. [webpack/webpack](https://github.com/webpack/webpack)

**Language/role:** JavaScript; extensible module and asset bundler.

Study how package metadata and static analysis cooperate with dependency-graph rewrites. The inspected [SideEffectsFlagPlugin implementation](https://github.com/webpack/webpack/blob/main/lib/optimize/SideEffectsFlagPlugin.js) does substantially more than read a boolean: it resolves the package that owns a `sideEffects` declaration, rebases glob patterns, records filesystem dependencies, and protects deferred-import behavior.

- **C1:** Skipping a re-exporting module can change namespace identity or evaluation timing. The plugin explicitly guards deferred imports and distinguishes missing manifests from unreadable manifests before inheriting metadata.
- **C2:** Loaders, compiler hooks, dependency objects, and optimization plugins allow the same engine to process multiple module formats and asset kinds. This optimization is itself implemented through compiler and parser hooks.
- **C3:** Caching the metadata walk avoids repeated filesystem work while replaying dependency information needed for invalidation. The [test-suite guide](https://github.com/webpack/webpack/blob/main/TESTING_DOCS.md) also distinguishes build/rebuild benchmarks from execution benchmarks of emitted bundles, making the two performance costs independently inspectable.

### 2. [rollup/rollup](https://github.com/rollup/rollup)

**Language/role:** TypeScript/JavaScript with Rust parsing support; ES-module bundler and tree shaker.

The [architecture guide](https://github.com/rollup/rollup/blob/master/ARCHITECTURE.md) is an unusually useful starting point for understanding statement inclusion. Modules are loaded and transformed into a graph, ordered for execution, and repeatedly visited until inclusion stops discovering additional necessary nodes. Output generation then assigns chunks, resolves names, renders wrappers, and finalizes hashes.

- **C1:** Inclusion depends on side-effect analysis rather than syntactic reachability alone. Repeated passes account for newly discovered dependencies, while execution order and deconfliction preserve observable behavior.
- **C2:** The build/generate separation allows one analyzed bundle to produce multiple output formats. Plugin hooks span loading, transformation, and output generation; browser and native interfaces share the underlying model.
- **C4:** The [changelog](https://github.com/rollup/rollup/blob/master/CHANGELOG.md) spans the October 2023 native-parser transition through October 2026 fixes for incorrectly removed CoreJS helpers and pathological nested-call performance. It documents API migrations and semantic regressions, not merely release numbers.

### 3. [evanw/esbuild](https://github.com/evanw/esbuild)

**Language/role:** Go; integrated parser, linker, bundler, and minifier.

Start with the [architecture document](https://github.com/evanw/esbuild/blob/main/docs/architecture.md). It connects a parallel scanning worklist to linking and printing, and explains tree shaking using top-level statement “parts.” Edges represent symbol references and dependencies on effectful parts; entry-point reachability also drives code splitting.

- **C1:** Shared data surviving incremental builds must remain immutable. Linking also distinguishes CommonJS execution wrappers from statically bound ES-module scopes and handles mixed syntax.
- **C3:** The implementation minimizes full AST passes and avoids serializing code between independent transformation tools. Parallel module scanning and shared representations have explicit structural explanations rather than relying on a language-choice claim.
- **C4:** The [2020 changelog](https://github.com/evanw/esbuild/blob/main/CHANGELOG-2020.md) records TypeScript import-preservation compatibility work; the [current changelog](https://github.com/evanw/esbuild/blob/main/CHANGELOG.md) continues that work with import-alias tree-shaking fixes and a pending safeguard against merging stateful chunks with identical contents. These provide concrete evidence of long-running semantic refinement.

### 4. [parcel-bundler/parcel](https://github.com/parcel-bundler/parcel)

**Language/role:** JavaScript/Flow with Rust components; multi-language asset bundler. Relevant subsystem: Parcel v2 core and its bundler/packager plugins.

Parcel is useful for studying an asset model that is broader than JavaScript modules. Its [plugin-system architecture](https://parceljs.org/plugin-system/overview/) distinguishes assets, dependency requests, and bundles, then transforms an asset graph into a bundle graph. A transformer can emit multiple assets from one input.

- **C2:** Resolvers, transformers, bundlers, namers, runtimes, packagers, optimizers, and compressors have separate responsibilities. This supports HTML, CSS, JavaScript, and generated assets without forcing every stage into one transform API.
- **C3:** Resolving and transformation run in parallel; packaging, optimization, and compression parallelize over bundles. Shared and asynchronous bundles explicitly address initial-load and duplicate-download costs.
- **C1:** The [scope-hoisting guide](https://parceljs.org/features/scope-hoisting/) explains why static exports, side effects, and CommonJS patterns affect which code can be concatenated or removed. This gives the reader a concrete semantic boundary to compare with the graph abstractions.

### 5. [web-infra-dev/rspack](https://github.com/web-infra-dev/rspack)

**Language/role:** Rust with TypeScript bindings; webpack-compatible bundler.

Study how a graph optimization can be parallelized without treating every update as independent. The [export-usage plugin](https://github.com/web-infra-dev/rspack/blob/main/crates/rspack_plugin_javascript/src/plugin/flag_dependency_usage_plugin.rs) propagates referenced exports with runtime information and work queues. It batches graph reads and separates updates that can be processed independently from nested or redirected export relationships.

- **C1:** Export usage is runtime-sensitive, and nested references can mutate related export records. The implementation explicitly limits parallel mutation and preserves distinct ownership when temporarily moving export data out of its storage.
- **C3:** Rayon batches, graph-cache freezing, and avoiding large export-map clones address identifiable analysis costs while retaining named stages and data types.
- **C2:** Compatibility with webpack's loader/plugin model is the integration boundary documented by the repository. The [JavaScript plugin tree](https://github.com/web-infra-dev/rspack/tree/main/crates/rspack_plugin_javascript/src/plugin) separates export discovery, usage, side effects, module concatenation, and asynchronous-module inference.

### 6. [rolldown/rolldown](https://github.com/rolldown/rolldown)

**Language/role:** Rust with TypeScript interfaces; bundler exposing Rollup-compatible APIs.

The [module-execution-order design](https://github.com/rolldown/rolldown/blob/main/internal-docs/linking/module-execution-order/implementation.md) makes the invariants behind linking unusually explicit: runtime helpers precede user code, declared entry order is preserved, and cycles prevent a simplistic claim of global topological ordering. The [link-stage source tree](https://github.com/rolldown/rolldown/tree/main/crates/rolldown/src/stages/link_stage) shows where sorting interacts with export binding, wrapping, top-level await, and tree shaking.

- **C1:** The design distinguishes back edges from completed cross edges and explains how dynamic imports enter ordering differently when code splitting is disabled. These choices propagate into cross-chunk imports and rendering.
- **C3:** An explicit-stack postorder traversal avoids stack overflow on deep graphs. Its documented work is proportional to vertices plus edges, with repeated incoming edges skipped through membership checks.
- **C2:** The repository supplies a reusable bundler and Rollup-compatible plugin surface; its staged linker offers a useful decomposition for studying ordering independently from statement inclusion and chunk generation.

### 7. [farm-fe/farm](https://github.com/farm-fe/farm)

**Language/role:** Rust and TypeScript; web bundler with persistent caching and partial bundling.

Farm contributes a different partitioning perspective. Its [core-architecture RFC](https://github.com/farm-fe/rfcs/blob/main/rfcs/001-core-architecture/rfc.md) separates modules, module groups, resource pots, and emitted resources, while specifying serial, first-result, and parallel plugin hooks. The [partial-bundling RFC](https://github.com/farm-fe/rfcs/blob/main/rfcs/003-partial-bundling/rfc.md) explains how modules are grouped according to sharing and mutability before output resources are formed.

- **C2:** The module/resource distinction accommodates JavaScript, CSS, HTML, and virtual modules. Rust and JavaScript extension interfaces share compilation concepts instead of reducing every asset to JavaScript text.
- **C3:** Partitioning explicitly trades off request count, resource size, and cache reuse. Keeping mutable application code separate from immutable package code limits the output affected by small edits.
- **C1:** The hook model states which operations must be isolated for parallel execution, while compilation context and graph access make shared-state coordination visible.

The RFCs are design documents, not proof that every detail of the latest implementation matches the original proposal; the repository confirms that partial bundling and the plugin model are implemented features.

## Incremental, mobile, and runtime-integrated bundlers

### 8. [react/metro](https://github.com/react/metro)

**Language/role:** JavaScript/Flow; React Native bundler. This is the verified canonical destination of the former `facebook/metro` URL.

The strongest entry point is [DeltaBundler/Graph.js](https://github.com/react/metro/blob/main/packages/metro/src/DeltaBundler/Graph.js). It treats rebuilding as a graph update with added, touched, and deleted modules, and documents a cycle-collection algorithm adapted to dependency references.

- **C1:** A failed transform or resolution can occur during an incremental update. The implementation snapshots affected state, performs subtractive and additive commits separately, and rolls back on failure, with an invariant checking that rollback leaves no unexplained additions or deletions.
- **C3:** Traversal follows changed paths and their affected dependencies instead of rebuilding the complete graph. Cycle collection releases unreachable cyclic groups that ordinary reference counting would retain.
- **C2:** The graph is parameterized over module output and receives resolution and transformation functions, separating graph maintenance from language transformation. The neighboring [DeltaBundler source tree](https://github.com/react/metro/tree/main/packages/metro/src/DeltaBundler) provides the broader integration context.

### 9. [vercel/next.js](https://github.com/vercel/next.js)

**Language/role:** Rust plus TypeScript/JavaScript; included specifically for **Turbopack and Turbo Tasks**, not the entire Next.js framework.

Study bundling as incremental computation over memoized functions. The [Turbo Tasks design](https://github.com/vercel/next.js/blob/canary/turbopack/crates/turbo-tasks/README.md) defines functions, values, traits, value cells, and emitted collectibles. Awaiting a value cell records a dependency; changing it invalidates dependent work.

- **C2:** Typed value cells and tasks form a reusable computation abstraction underneath bundler-specific operations. The distinction between a cell's identity and a read-only snapshot is especially useful to examine.
- **C3:** Functions execute through Tokio tasks and recomputation follows invalidated dependencies. The [official Turbopack guide](https://nextjs.org/docs/app/api-reference/turbopack) connects this to lazy compilation, disk-persisted results, and a unified graph spanning client and server outputs.
- **C1:** Dependency tracking and invalidation must agree for cached results to remain valid. This is an engineering inference from the documented execution model, not a claim that all cache invalidation cases have been independently audited.

### 10. [oven-sh/bun](https://github.com/oven-sh/bun)

**Language/role:** Rust in the inspected bundler, with C++ runtime integration and TypeScript tests; included for the **Bun bundler/linker**. Older descriptions of this subsystem as Zig should not be applied to the inspected branch.

Start at [src/bundler](https://github.com/oven-sh/bun/tree/main/src/bundler) and [LinkerContext.rs](https://github.com/oven-sh/bun/blob/main/src/bundler/LinkerContext.rs). The linker coordinates parse and link graphs, runtime helpers, cross-chunk names, source maps, and parallel output work.

- **C1:** The inspected source documents lifetime and disjoint-write requirements behind its unsafe `Send`/`Sync` implementations. Names shared by importing and exporting chunks must agree, while helper initialization and moved chunk effects need explicit bookkeeping.
- **C3:** Parallel chunk generation, dedicated parse tasks, arenas, and shared graph representations address build throughput and allocation costs within identifiable modules.
- **C2:** Loader, target, format, and output structures support multiple bundling modes, including JavaScript, CSS, and HTML processing. Restricting study to this subsystem avoids confusing bundler architecture with Bun's package manager and runtime implementations.

## CommonJS, AMD, and smaller specialized bundlers

### 11. [browserify/browserify](https://github.com/browserify/browserify)

**Language/role:** JavaScript; CommonJS-to-browser bundler.

Browserify offers a compact contrast to compiler-centric bundlers. Its [implementation entry point](https://github.com/browserify/browserify/blob/master/index.js) constructs a labeled object-stream pipeline: dependency discovery, JSON conversion, syntax validation, sorting, deduplication, labeling, source maps, and packing are separately addressable stages. The [official handbook](https://github.com/browserify/browserify-handbook) explains the static `require()` traversal and plugin model.

- **C2:** Named stream stages, transforms, plugins, and external-bundle integration form reusable composition boundaries. Engineers can replace a stage without reimplementing the entire traversal.
- **C1:** Exposed names, ignored modules, external modules, browser replacements, and entry order have distinct semantics. Pending asynchronous work is coordinated before a bundle is ready, including when another Browserify instance supplies external-module labels.
- **C3:** Dependency sorting/deduplication and a syntax cache are concrete size and repeated-work optimizations.

This is a bundler selection, not a claim that core Browserify performs modern export-level tree shaking. Its treatment of dynamic, nonliteral `require()` is an important limitation to study.

### 12. [requirejs/r.js](https://github.com/requirejs/r.js)

**Language/role:** JavaScript; RequireJS's AMD optimizer and command-line host. A legacy module-system implementation, not a modern ESM-first bundler.

Study how reusing a loader during optimization preserves behaviors that simple concatenation misses. The [repository overview](https://github.com/requirejs/r.js#readme) explains anonymous-module naming, loader-plugin inlining, and Node/Rhino/Nashorn/xpcshell integration. The [loader patch](https://github.com/requirejs/r.js/blob/master/build/jslib/requirePatch.js) exposes the build-time adaptation in detail.

- **C1:** Anonymous definitions need stable names after concatenation, and plugin execution must remain compatible with its host environment. The patch isolates Node's `module`/`exports`, resets caches across top-level optimizations, and rejects unsupported network/dynamic URLs from normal tracing.
- **C2:** Environment adapters and AMD loader plugins allow the optimizer to handle multiple execution hosts and non-script resources. The [optimizer source tree](https://github.com/requirejs/r.js/tree/master/build/jslib) makes these boundaries navigable.

The project's own README also documents CommonJS conversion cases where conditional imports or execution-order-sensitive cycles do not work; compatibility is qualified rather than universal.

### 13. [lasso-js/lasso](https://github.com/lasso-js/lasso)

**Language/role:** JavaScript; page-oriented CommonJS bundler and asset pipeline originating in the eBay ecosystem. Historical/low-recent-activity selection: inspected repository metadata reports its latest push in April 2024.

Lasso is useful for studying deployment-oriented bundling: page dependencies, application-wide shared bundles, CSS slots, and asynchronous resources. The [bundling guide](https://github.com/lasso-js/lasso/blob/master/docs/bundling.md) defines application versus page precedence and several scopes for recursive dependency inclusion.

- **C2:** Dependency types and bundle mappings support both module dependencies and other resources, with explicit policies for how far transitive inclusion should extend into directories and nested packages.
- **C1:** The [bundling-strategy implementation](https://github.com/lasso-js/lasso/blob/master/src/bundling-strategies.js) handles a dependency moving from an async-only assignment into synchronous page loading. It also prevents generating a separate asynchronous assignment when the page already loads that bundle synchronously.
- **C3:** The default and lean strategies expose a concrete tradeoff between stable shared bundles and page-specific content, making cache reuse and unnecessary payload inspectable policy decisions.

### 14. [dumberjs/dumber](https://github.com/dumberjs/dumber)

**Language/role:** JavaScript; small standalone bundling engine intended for Gulp pipelines and an AMD runtime. Latest inspected changelog entry: December 2024; current active maintenance is not assumed.

Study an intentionally narrower architecture with real package-compatibility work. [lib/trace.js](https://github.com/dumberjs/dumber/blob/master/lib/trace.js) composes format conversion, aliases, shims, data loaders, and optional dependency discovery. Its cache key includes source contents, source maps, environment, module/package identity, and shim configuration.

- **C2:** Transformation units and the optional dependency-finder interface let surrounding tools supply transpilation and asset processing. Bundling remains a reusable pipeline stage rather than owning the entire development workflow.
- **C3:** Traced units and transformed results are reused; the explicit cache inputs make the repeated-work optimization understandable.
- **C4:** The [dated changelog](https://github.com/dumberjs/dumber/blob/master/CHANGELOG.md) documents compatibility fixes from at least 2020 through 2024: UMD handling, source-map behavior, browser tests, Node-version transitions, and the shape of package `exports` conditions.

The [official overview](https://dumber.js.org/bundler-overview) also documents deliberate limitations, including how package-version conflicts are resolved; compactness should not be mistaken for complete Node compatibility.

### 15. [stealjs/steal-tools](https://github.com/stealjs/steal-tools)

**Language/role:** JavaScript; StealJS build-time graph processing, bundling, and output optimization. Included as a legacy ecosystem study without a claim of current active maintenance.

The distinctive implementation is [bundle/flatten.js](https://github.com/stealjs/steal-tools/blob/master/lib/bundle/flatten.js): it merges shared bundles to meet a requested depth while evaluating the additional bytes each application would have to load. It preserves lower-dependency contents first when merging.

- **C3:** This is an explicit optimization objective over network-load structure and wasted payload. The calculation is small enough to study directly, including its heuristics and limitations.
- **C2:** The [bundle API documentation](https://github.com/stealjs/steal-tools/blob/master/doc/bundle.md) separates configuration from bundle construction and supports filtered dependency/development bundles. The engine sits alongside graph, transformation, minification, and writing stages.
- **C1:** Dependency order constrains legal merges, while development bundles containing loader configuration become stale when that configuration changes. The docs make the resulting invalidation responsibility visible.

This is a useful heuristic implementation to review, not an assertion that its partitioning is globally optimal.

### 16. [PepsRyuu/nollup](https://github.com/PepsRyuu/nollup)

**Language/role:** JavaScript; independent Rollup-compatible development bundler, deliberately omitting production tree shaking and scope hoisting.

Nollup makes semantic/performance tradeoffs inspectable. Its [live-binding design](https://github.com/PepsRyuu/nollup/blob/master/docs/live-bindings.md) compares rewriting imported references to getter-backed objects with an experimental `with`-scope approach. The [live-binding resolver](https://github.com/PepsRyuu/nollup/blob/master/lib/impl/NollupLiveBindingsResolver.js) distinguishes actual imported-variable uses from shadowed names, property names, declarations, and export aliases.

- **C1:** Imported values must remain live after the exporting module changes them. AST context and lexical shadowing are central to the rewrite; the documentation also candidly limits circular-dependency support.
- **C3:** Module wrappers and invalidation favor rebuild latency. The [compiler API](https://github.com/PepsRyuu/nollup/blob/master/docs/compiler.md) specifies reuse of unchanged modules and in-memory output. Live bindings are disabled by default, and the alternatives have debugging, strict-mode, and runtime-cost consequences.
- **C2:** Rollup-style configuration and hooks support reuse of plugins and custom middleware without wrapping Rollup's production compiler.

### 17. [systemjs/builder](https://github.com/systemjs/builder)

**Language/role:** JavaScript; **archived and deprecated** mixed-format SystemJS bundler. Its README limits continued relevance to legacy SystemJS builds and directs new work toward Rollup.

Study the difficult transition between declarative ES-module linkage and CommonJS/AMD execution. The [self-executing bundle runtime](https://github.com/systemjs/builder/blob/master/templates/sfx-core.js) separates instantiation from evaluation, maintains importer setters, and locks export propagation to stop cycles.

- **C1:** Circular references, mutable exports, CommonJS `module.exports` replacement, and namespace wrapping interact. The runtime gives concrete code for the different ordering rules and cycle-stop conditions.
- **C2:** The [bundle-expression implementation](https://github.com/systemjs/builder/blob/master/lib/arithmetic.js) supports union, subtraction, and intersection over traced module trees, plus operations on single modules. Canonicalization and glob expansion connect that algebra to loader resolution.

This is a historical implementation of module-system interoperability. It is retained for those mechanisms, not presented as a maintained successor to current SystemJS or as an independent copy of Rollup's optional optimization pass.

### 18. [fuse-box/fuse-box](https://github.com/fuse-box/fuse-box)

**Language/role:** TypeScript/JavaScript; **archived** bundler with its own module runtime and production pipeline.

The [code-splitting phase](https://github.com/fuse-box/fuse-box/blob/master/src/production/phases/CodeSplittingPhase.ts) is a focused study of identifying modules that belong in a lazy subtree. It examines reverse dependants, records split entries, traces ownership back to an entry, and tracks visited/circular relationships.

- **C1:** A module referenced by both eager and lazy code cannot simply be moved into the lazy bundle. The implementation tests isolation and handles cycles explicitly instead of assuming the dependency graph is a tree.
- **C3:** Lazy-entry partitioning addresses initial payload and loading costs. The source also exposes the policy tradeoff for dependencies shared by split entries, making its decisions reviewable rather than presenting an unexplained size result.
- **C2:** The [production engine](https://github.com/fuse-box/fuse-box/blob/master/src/production/engine.ts) runs explicit warmup, splitting, and bundling phases over production context and can accept another phase sequence.

Retain the archive status when comparing it with current tools; this selection does not imply its old dependency stack is suitable for a new application.

## Dead-code elimination and optimizer toolkits

### 19. [google/closure-compiler](https://github.com/google/closure-compiler)

**Language/role:** Java; whole-program JavaScript optimizer, checker, and chunk-producing compiler.

Study an optimizer that can use stronger assumptions than a general-purpose bundler. [RemoveUnusedCode.java](https://github.com/google/closure-compiler/blob/master/src/com/google/javascript/jscomp/RemoveUnusedCode.java) explains a mark-and-sweep-style traversal whose deferred continuations represent conditional dependency edges. Assignments need not count as uses unless they affect observable state.

- **C1:** Removing variables, properties, and polyfills requires side-effect reasoning and care around implicit property uses. The source documents a further invariant: removing an enclosing subtree must not cause later double-removal or invalid scope-change notifications.
- **C2:** Compiler passes, coding conventions, scope creation, and configurable removal categories separate analysis mechanisms from policy. Deferred worklists let the pass express more than simple global-name reachability.
- **C3:** Traversing a deferred initializer only when its value becomes relevant avoids unnecessary work while retaining a documented algorithm.

The [project's input restrictions](https://github.com/google/closure-compiler#important-caveats) are material: `ADVANCED` assumes knowledge of the whole program, hidden property accesses can break output, and the best-supported module conventions remain Closure's own. This is not a transparent optimizer for arbitrary npm code.

### 20. [terser/terser](https://github.com/terser/terser)

**Language/role:** JavaScript; ES6+ compressor and mangler used downstream of bundling. Terser evolved from the Uglify family and is retained for its separate optimizer implementation and subsequent evolution.

Start with [drop-unused.js](https://github.com/terser/terser/blob/master/lib/compress/drop-unused.js). It first identifies direct uses, then follows initializer dependencies, and finally rewrites unused declarations. The handling of classes, exported declarations, destructuring, `arguments`, and pinned scopes is more informative than a simple dead-branch example.

- **C1:** Eliminating an unused binding must retain effectful initialization and preserve JavaScript calling and scope semantics. Class evaluation and non-strict `arguments` aliasing receive explicit treatment.
- **C2:** Compression, mangling, AST input, source maps, retained names, and persistent name caches are independently configurable through the repository's API documentation, supporting integration into many build pipelines.
- **C3:** The [changelog](https://github.com/terser/terser/blob/master/CHANGELOG.md) records concrete cost controls, including fixes for extremely slow expression evaluation and decisions not to inline functions into loops for performance reasons.

Terser is not a module resolver. Its documented compiler assumptions and unsafe options matter when assessing semantic equivalence.

### 21. [mishoo/UglifyJS](https://github.com/mishoo/UglifyJS)

**Language/role:** JavaScript; independent continuing UglifyJS compressor/parser/mangler toolkit, related to but not duplicated by Terser's codebase.

The [compressor](https://github.com/mishoo/UglifyJS/blob/master/lib/compress.js) exposes a dense AST-rewriting design: scope analysis, optimization flags, unused-variable removal, variable merging, and bounded repeated passes. It also documents why transforming children at the wrong time corrupts the traversal stack.

- **C1:** Tree mutation must preserve the walker's view of the AST as well as program behavior. The [fuzzer](https://github.com/mishoo/UglifyJS/blob/master/test/ufuzz/index.js) generates programs, runs original/transformed variants in a sandbox, compares outcomes, and connects failures to reduction machinery. That is substantive semantic validation evidence, not just test-count evidence.
- **C3:** Repeated compression measures AST node count and stops after progress stalls, exposing the tradeoff between additional optimization and compile cost.
- **C2:** The public toolkit can combine input files in a shared scope and coordinate mangled names across separate invocations through a persistent name cache.

The current README supports many ECMAScript features; describing this repository as strictly ES5-only would be misleading. As with Terser, minification assumptions constrain the equivalence claim.

### 22. [swc-project/swc](https://github.com/swc-project/swc)

**Language/role:** Rust; included for the **`swc_ecma_minifier` and optimization infrastructure**, not merely its transpiler or parser.

The [minifier entry point](https://github.com/swc-project/swc/blob/main/crates/swc_ecma_minifier/src/lib.rs) shows dead-code elimination before and after compression, repeated DCE until stability, metadata marking, name/property mangling, and export merging. The [architecture guide](https://github.com/swc-project/swc/blob/main/ARCHITECTURE.md) explains identifier resolution, hygiene, and final AST fixing.

- **C1:** Scope identity must survive transformations before textual names are made unique. The optimizer preserves effectful imports during DCE, and its source explicitly states assumptions about temporal-dead-zone violations and side-effectful global getters.
- **C2:** Separate AST, visitor, scope/hygiene, usage-analysis, and optimization crates allow downstream tools to reuse machinery at different levels rather than embedding an entire command-line compiler.
- **C3:** String interning and dedicated analysis/pass stages expose allocation and traversal choices. The architecture guide also describes Test262-based parser checks and golden code-generation fixtures, useful boundaries when studying the wider infrastructure supporting the optimizer.

These tests are not asserted to prove every minifier transformation correct; the documented assumptions remain material.

## A different source-language ecosystem

### 23. [seaofvoices/darklua](https://github.com/seaofvoices/darklua)

**Language/role:** Rust; Lua 5.1/Luau bundler and configurable AST transformation system.

Darklua adds more than a JavaScript-tool port. The [unused-variable pass](https://github.com/seaofvoices/darklua/blob/main/src/rules/remove_unused_variable.rs) preserves effectful expressions and reasons about Lua's multiple-return-value assignments, including trailing variables without corresponding expressions. The [bundler rule](https://github.com/seaofvoices/darklua/blob/main/src/rules/bundle/mod.rs) connects require modes, exclusion patterns, loaders, and processing context.

- **C1:** Removing one variable from a Lua assignment can change how several return values bind to the remaining variables. The pass explicitly distinguishes expressions that can return multiple values and retains necessary nil assignments and side effects.
- **C2:** Reusable rules, scope visitors, evaluators, require modes, and content loaders support transformation and bundling across Lua/Luau conventions and embedded data modules.

The [official bundling documentation](https://darklua.com/docs/bundle/) imposes an important limit: modules should not have require-time side effects because bundling may change their order. The project therefore qualifies through substantial mechanisms and explicit correctness boundaries, not a claim of unrestricted semantic preservation.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations. Angles included mainstream ESM tree shakers; Rust replacements and compatibility layers; Go/Zig/native implementations; mobile and incremental graph maintenance; CommonJS/AMD and loader-based bundling; JavaScript whole-program DCE and compressor internals; small independent development bundlers; and Lua/Luau bundling. Later queries increasingly returned the same engines, wrappers, generic lists, and tutorial projects. Nollup and Darklua were retained because follow-up primary-source inspection added distinct architectural coverage.

Each retained repository's canonical identity was checked through an opened GitHub repository page or the public GitHub API. Each entry also has independently opened implementation/design material beyond its root README; raw-file retrieval was used to read source directly where GitHub's rendered view was cumbersome. Repository status checks identified the SystemJS Builder and FuseBox archives. API metadata also helped distinguish a fork from an original repository; API rate limiting was handled by reading public repository pages and raw files instead. No candidate code was executed, no dependencies were installed, and no repositories were cloned.

Important exclusions and boundaries:

- **Thin integrations and duplicate engines:** Vite, Rsbuild/Rslib, tsup/tsdown, and ncc were not added simply to count another interface around an included engine. This is a scope decision, not a judgment that those projects lack engineering value.
- **Mako's changed identity:** the old [`umijs/mako`](https://github.com/umijs/mako) URL now redirects to [`utooland/utoo`](https://github.com/utooland/utoo), whose inspected default branch describes a Turbopack-based toolchain. [`ant-design/mako`](https://github.com/ant-design/mako) is a fork. Neither is counted as a separate current implementation of the original Mako engine.
- **Monorepos and shared ancestry:** Next.js, Bun, and SWC each count once, only for named subsystems. Terser and UglifyJS share ancestry but have separately inspected implementations, APIs, and testing/evolution evidence. Other forks were not used to inflate coverage.
- **Adjacent tools:** package managers named “bundler,” generic task runners, runtime-only module loaders, bundle visualizers, and ordinary transpilers were outside scope. General native-linker and WebAssembly DCE ecosystems were not expanded into this primarily source-module-focused report.
- **Historical value versus adoption:** archived and older low-activity projects are included where they contribute a distinct mechanism. None is recommended for a new deployment merely because it appears here. Unarchived status and a recent push were not used as substitutes for C4.
- **Evidence limits:** this was source-and-document research, not an exhaustive code audit or benchmark reproduction. Performance criteria refer to concrete architecture and optimization objectives, not unsupported comparative speed claims. RFCs describe intended designs; correctness and reuse judgments drawn from those designs are identified as such. Search results and retrieved repository text were treated as evidence, never as instructions.
