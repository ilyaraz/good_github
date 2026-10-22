# Declarative UI frameworks and rendering runtimes

Research date: **2026-10-09**

This selection covers 25 repositories that turn declarative component trees, templates, reactive values, or UI descriptions into browser or native interfaces. It emphasizes the machinery underneath application APIs: reconciliation, dependency tracking, composition, layout, scheduling, hydration, and rendering boundaries. It includes large frameworks, smaller language-community implementations, official mirrors, and one explicitly archived historical project. Each repository is counted once; relevant monorepo subsystems are identified below.

Criteria are judgments grounded in the linked primary material, not claims that every component of a selected repository is exemplary:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial input handling, or failure and lifecycle semantics.
- **C2 — Abstractions:** substantial reusable mechanisms supporting different applications, components, or rendering targets.
- **C3 — Performance and structure:** concrete reductions in rendering, allocation, scheduling, or layout work, organized around understandable architectural boundaries.
- **C4 — Evolution:** dated evidence of sustained development together with compatibility work, testing, or complexity management.

## Browser component frameworks and compiler-assisted runtimes

### 1. [react/react](https://github.com/react/react)

**Language/role:** JavaScript with Flow; component runtime, reconciler, DOM/server renderers, and scheduling infrastructure. The live GitHub API resolves the former `facebook/react` repository to this canonical owner.

Study how interruptible rendering can coexist with a consistent committed interface. **C1:** the work loop checks external-store consistency after concurrent rendering and retries synchronously when an interleaved mutation invalidates the result. **C3:** separate synchronous and cooperative work loops make yielding, work units, and scheduling policy explicit. These are concrete entry points into the reconciler rather than a small application-level rendering example. See [ReactFiberWorkLoop.js](https://github.com/react/react/blob/main/packages/react-reconciler/src/ReactFiberWorkLoop.js).

**C4:** the [changelog](https://github.com/react/react/blob/main/CHANGELOG.md) spans dated releases from 2013 through 2026 and records continuing fixes to hidden-tree updates, Suspense propagation, StrictMode behavior, and browser compatibility. Its value is the record of preserving semantics through architectural changes, not merely the project's age.

### 2. [vuejs/core](https://github.com/vuejs/core)

**Language/role:** TypeScript; Vue's reactivity, template compiler, virtual DOM, and renderer packages.

Study the contract between static template analysis and a general-purpose runtime. **C2:** templates compile to render functions, while applications can also author render functions directly; both feed the same mounting and patching model. **C3:** cached static nodes, compiler-generated patch flags, and flattened lists of dynamic descendants allow the renderer to skip known-static work. The architecture also explains how these hints affect hydration. The [rendering mechanism guide](https://vuejs.org/guide/extras/rendering-mechanism.html) is a particularly clear entry point for comparing compiler-assisted virtual DOMs with purely runtime reconciliation.

### 3. [sveltejs/svelte](https://github.com/sveltejs/svelte)

**Language/role:** JavaScript/TypeScript; declarative component compiler and reactive browser runtime.

Study the runtime bookkeeping that remains necessary even when components are compiled into direct DOM operations. **C1:** reaction execution preserves and restores nested reactive context, handles writes that invalidate the currently running effect, and commits dependencies discovered before an exception so that later changes can retrigger the reaction. **C3:** it reuses unchanged dependency prefixes and updates subscriptions when dependencies change, rather than rebuilding all bookkeeping on every evaluation. These mechanisms are visible in [client/runtime.js](https://github.com/sveltejs/svelte/blob/main/packages/svelte/src/internal/client/runtime.js), especially `update_reaction` and `update_dependencies`. The compiler/runtime combination is the relevant subsystem; SvelteKit is a separate project and is not counted here.

### 4. [solidjs/solid](https://github.com/solidjs/solid)

**Language/role:** TypeScript/JavaScript; fine-grained reactive UI runtime with compiled DOM templates.

Study how dependency discovery replaces repeated execution of whole component trees. **C2:** signals, memos, effects, stores, and asynchronous resources form reusable primitives with distinct responsibilities. **C1:** dependencies can disappear when a conditional branch stops reading a signal; nested effects must restore the previous subscriber, and asynchronous callbacks cannot assume the original tracking context still exists. **C3:** cached computations and targeted updates reduce unnecessary recalculation and DOM work. The official [fine-grained reactivity explanation](https://docs.solidjs.com/advanced-concepts/fine-grained-reactivity) walks through these mechanisms and their limitations, making this a useful entry point into dependency-graph semantics.

### 5. [preactjs/preact](https://github.com/preactjs/preact)

**Language/role:** JavaScript; compact component and virtual-DOM implementation with React-oriented compatibility APIs.

Study a comparatively concentrated renderer where DOM position, component identity, and fragment handling meet. **C1:** child reconciliation explicitly handles references detached by Suspense and clears stale positional DOM pointers after moving matched nodes, preventing later nested diffs from inserting elements in the wrong place. **C2:** the same child-diff machinery accepts component output, fragments, namespaces, hydration state, and commit/ref queues. **C3:** matching and in-place movement reuse existing nodes instead of reconstructing an entire subtree. Start with [src/diff/children.js](https://github.com/preactjs/preact/blob/main/src/diff/children.js); its explanatory comments expose the correctness cost of an apparently simple diff loop.

### 6. [lit/lit](https://github.com/lit/lit)

**Language/role:** TypeScript; declarative templates and reactive Web Components. Relevant monorepo layers are `lit-html`, `reactive-element`, and `lit-element`.

Study how a framework composes with browser-defined custom-element lifecycles. **C1:** values assigned before element upgrade must survive initialization, external listeners need cleanup on disconnection, and update completion has explicit asynchronous semantics. **C2:** a low-level reactive element base and a separate template renderer support reusable components without requiring a whole-application framework. **C3:** property changes are batched into microtask updates before the next paint. The [lifecycle guide](https://lit.dev/docs/components/lifecycle/) explains the ordering between attribute reflection, rendering, and `updateComplete`, a useful boundary for studying subtle integration failures.

### 7. [QwikDev/qwik](https://github.com/QwikDev/qwik)

**Language/role:** TypeScript, with optimizer infrastructure including Rust; resumable component runtime and compilation tools. The relevant subsystem is Qwik core, rather than its routing adapters.

Study a server-to-browser handoff that preserves framework state in addition to application data. **C1:** serialization must preserve object-graph relationships and supported non-JSON values while respecting limits on classes, streams, and captured closures. **C3:** serialized listener locations, component boundaries, and subscriptions permit code to load when needed instead of reconstructing all of that information by executing every component at startup. The [resumability design explanation](https://next.qwik.dev/docs/concepts/resumable/) describes the loader and serialization mechanisms. Treat the document's absolute startup-speed language as project positioning; this selection relies on the architecture, not an independently established latency claim.

### 8. [marko-js/marko](https://github.com/marko-js/marko)

**Language/role:** JavaScript/TypeScript; HTML-oriented declarative language, compiler, and browser/server runtimes.

Study compilation as a coordinated server-and-browser build contract. **C2:** the compiler supports source, migrated-source, HTML, and DOM outputs, with pluggable translators and virtual dependencies for generated styles and modules. **C3:** shared analysis caches avoid repeatedly analyzing templates used by several others; dependency metadata determines when cached results must be invalidated. **C1:** server and browser builds must agree on template identifiers and relevant configuration, and the API distinguishes blocking assets from deferred ones. The current [compiler API reference](https://markojs.com/docs/reference/compiler) explains these constraints. Older Marko 5 compiler documentation remains in the repository; it should not be mistaken for the current API.

## Native and cross-platform composition and rendering

### 9. [flutter/flutter](https://github.com/flutter/flutter)

**Language/role:** Dart and C++; cross-platform widget framework and rendering/engine monorepo. The study target here is the widget, element, and render-object pipeline.

Study why immutable widget descriptions, persistent elements, and geometry-bearing render objects are separate structures. **C1:** layout relies on constrained information flow: constraints travel downward, geometry upward, and child layout does not depend on a position assigned later by its parent. Global-key reparenting must preserve state and subtree identity. **C2:** separate protocols support highly composed widgets and specialized render objects. **C3:** dirty-element processing, constraint-based early exits, and child-list reconciliation avoid unnecessary tree walks. [Inside Flutter](https://docs.flutter.dev/resources/inside-flutter) connects these invariants directly to the algorithms, including viewport-aware construction of scrolling content.

### 10. [react/react-native](https://github.com/react/react-native)

**Language/role:** C++, JavaScript/TypeScript, Kotlin/Java, and Objective-C/Objective-C++; React's native platform renderer. The former `facebook/react-native` URL redirects to this canonical repository.

Study the Fabric render/commit/mount pipeline, especially the boundary between immutable shadow trees and mutable host views. **C1:** tree promotion and native-state updates require consistency across threads; conflicting C++ state commits retry against the latest committed tree. **C3:** structural sharing reduces copying, while view flattening removes unnecessary host-view nodes before mounting mutations. These mechanisms are explained in [Render, Commit, and Mount](https://reactnative.dev/architecture/render-pipeline). This is independently substantive platform-rendering code, not a second count of React's shared reconciler.

### 11. [androidx/androidx](https://github.com/androidx/androidx)

**Language/role:** Kotlin/Java; AndroidX monorepo, specifically Compose runtime and UI. **Official synchronized GitHub mirror/development surface:** primary development is on Android's AOSP infrastructure, as the repository describes.

Study compiler-generated composition calls and positional memoization. **C1:** the composition design specifies restrictions on slot-group shape and exclusive writer versus concurrent reader access; conditional composition must retain the correct identity of remembered values. **C3:** parameter-change checks and skipping avoid reevaluating unchanged composition regions, with compact slot storage designed to reduce overhead. [How Composition Works](https://github.com/androidx/androidx/blob/androidx-main/compose/runtime/design/how-compose-works.md) explains the compiler/runtime contract with transformed-code examples. It explicitly warns that some slot-table implementation details may describe an older implementation, so use it as a design entry point rather than a frozen description of every current data structure.

### 12. [qt/qtdeclarative](https://github.com/qt/qtdeclarative)

**Language/role:** C++ and QML; QML runtime, Qt Quick scene graph, controls, and associated modules. **Official GitHub mirror**, identified by the [Qt organization](https://github.com/qt); contribution review occurs through Qt's Gerrit infrastructure.

Study the synchronization boundary between declarative QML items and rendering nodes. **C1:** in the threaded render loop, the GUI thread is blocked while changed items synchronize into the scene graph; application graphics hooks have specific thread and ordering constraints. **C3:** rendering then proceeds separately while the GUI can handle events and animation work, and the architecture supports different graphics backends. The [Qt Quick scene-graph guide](https://doc.qt.io/qt-6/qtquick-visualcanvas-scenegraph.html) describes these phases and the basic/threaded loop alternatives. This is a substantive maintained mirror of the implementation, not a third-party port.

### 13. [facebook/litho](https://github.com/facebook/litho)

**Language/role:** Kotlin/Java; declarative Android component and layout framework.

Study how immutable component inputs make layout computation movable off the UI thread. **C1:** the layout model requires immutable props and state, and its synchronous/asynchronous root-setting APIs promise that the resulting layout represents the last root supplied. That is an ordering guarantee worth tracing through the runtime. **C3:** background measurement reduces main-thread work; pooling and generated code address allocation costs introduced by immutable descriptions. The [asynchronous-layout explanation](https://fblitho.com/docs/asynchronous-layout/) also explains when synchronous work is necessary because visible content cannot wait. Its annotations and examples describe the documented API generation, rather than every newer Kotlin-facing convenience API.

### 14. [facebook/componentkit](https://github.com/facebook/componentkit)

**Language/role:** Objective-C++/C++; declarative iOS component framework, particularly for complex collection/list content.

Study the separation between component descriptions, computed layout, and acquired UIKit views. **C1:** mounting and unmounting assert main-thread execution, coordinate controller callbacks, and track whether a component currently owns mount information. [CKComponent.mm](https://github.com/facebook/componentkit/blob/main/ComponentKit/Core/CKComponent.mm) makes these lifecycle boundaries concrete. **C3:** background layout and declarative view configuration enable view recycling without making application code manually reset every reused view; the [uses guide](https://componentkit.org/docs/uses/) explains this focus and notes that non-list interfaces are a less natural fit. The older guide is useful historical design context; its platform-interoperability commentary should not be generalized to current language capabilities.

### 15. [AvaloniaUI/Avalonia](https://github.com/AvaloniaUI/Avalonia)

**Language/role:** C# and XAML; declarative cross-platform UI framework and composition renderer.

Study the bridge from a XAML-defined control hierarchy to a separately managed rendering engine. **C2:** the [composition explanation](https://github.com/AvaloniaUI/avalonia-docs/blob/main/docs/fundamentals/ui-composition.md) distinguishes reusable user/custom/template controls and logical versus visual trees. **C1:** the compositor checks dispatcher access, coordinates pending batches under a lock, and schedules render-thread disposal through serialized batches. **C3:** queued changes, deduplicated serialization, and pooled transport buffers concentrate cross-thread work rather than sending each property mutation independently. The implementation entry point is [Compositor.cs](https://github.com/AvaloniaUI/Avalonia/blob/main/src/Avalonia.Base/Rendering/Composition/Compositor.cs).

## Rust ownership, typed views, and reusable rendering cores

### 16. [slint-ui/slint](https://github.com/slint-ui/slint)

**Language/role:** Rust with a declarative UI language and C++, JavaScript, and Python integrations; native and embedded GUI compiler/runtime.

Study the dependency engine underneath property bindings. **C1:** pinned allocations and external raw pointers require careful address stability and unlinking; the implementation documents ownership rules, validates dependency links, and drops long lists iteratively to avoid stack overflow. See [internal/core/properties.rs](https://github.com/slint-ui/slint/blob/master/internal/core/properties.rs). **C2:** the repository's architecture separates declarative UI compilation, language-facing application APIs, reactive runtime properties, and selectable rendering backends. This makes Slint useful for studying how one UI model spans embedded and desktop constraints. The presence of unsafe implementation code is a source of invariants to investigate, not evidence by itself that those invariants are universally satisfied.

### 17. [DioxusLabs/dioxus](https://github.com/DioxusLabs/dioxus)

**Language/role:** Rust; declarative component framework with a shared virtual-DOM core and multiple renderer integrations.

Study the interface between asynchronous work and a renderer-independent stream of mutations. **C2:** the core exposes virtual-DOM construction, event delivery, renderer mutation writers, and Suspense-aware progress independently of a particular display target. **C1:** `wait_for_work` documents cancellation safety, and rendering drains newly queued dirty marks after each work item so that cancellation or rerunning a child does not leave its Suspense boundary stale. **C3:** dirty-scope scheduling and idle polling avoid continuously rebuilding the whole UI. [virtual_dom.rs](https://github.com/DioxusLabs/dioxus/blob/main/packages/core/src/virtual_dom.rs) includes both the integration protocol and its implementation. The repository labels its native WGPU renderer experimental; the core's inclusion does not imply equal maturity across targets.

### 18. [leptos-rs/leptos](https://github.com/leptos-rs/leptos)

**Language/role:** Rust; fine-grained declarative web framework with browser, server-rendering, and hydration support. Relevant subsystem: `reactive_graph` ownership and the UI layers using it.

Study how a reactive lifetime can differ from Rust's lexical lifetime. **C1:** rerunning an owned reactive computation must cancel effects, run cleanup functions, and dispose arena-stored values created during the previous run; weak owner references prevent ownership cycles from keeping resources alive. **C2:** the same owner abstraction provides effect lifecycle management, context lookup, and arena-backed handles for signals and memos. The current [reactive_graph/src/owner.rs](https://github.com/leptos-rs/leptos/blob/main/reactive_graph/src/owner.rs) explains these responsibilities and implements them. This is a better current entry point than assuming older architectural descriptions of `leptos_reactive` still match the crate layout.

### 19. [linebender/xilem](https://github.com/linebender/xilem)

**Language/role:** Rust; **experimental** typed reactive UI architecture, with web and Masonry-backed native implementations.

Study the distinction between short-lived typed view descriptions and retained backend elements. **C2:** `xilem_core` supplies shared view and sequence abstractions, while `xilem_web` and `xilem_masonry` adapt them to different retained trees. **C3:** statically typed comparisons and selective memoization provide explicit ways to reduce regeneration and rebuilding of view subtrees. The [Xilem architecture document](https://github.com/linebender/xilem/blob/main/xilem/ARCHITECTURE.md) explains this design and its backend separation. Its final usage section is marked as needing revision, so the architecture is the study target; its illustrative API signatures should not be treated as a current compatibility guarantee.

### 20. [iced-rs/iced](https://github.com/iced-rs/iced)

**Language/role:** Rust; Elm-inspired declarative native GUI, with a renderer-independent runtime. The repository describes the project as **experimental software**.

Study how an application can regenerate declarative widget descriptions while retaining interaction state and cached work. **C2:** [iced_runtime](https://github.com/iced-rs/iced/blob/master/runtime/src/lib.rs) separates event-loop actions, tasks, widgets, windows, and renderer integration. **C3:** [UserInterface](https://github.com/iced-rs/iced/blob/master/runtime/src/user_interface.rs) accepts a previous cache, diffs widget state, and tracks layout/overlay invalidation and redraw requests. **C1:** rebuilding overlays during event processing requires respecting invalidation before continuing to use layout and widget state. This makes the repository useful for studying the integration surface between declarative application logic and an externally driven native event loop.

## Functional-language runtimes and alternative component models

### 21. [elm/virtual-dom](https://github.com/elm/virtual-dom)

**Language/role:** Elm and JavaScript kernel code; rendering foundation underneath Elm's HTML and SVG libraries.

Study a focused implementation of immutable node descriptions, lazy nodes, keyed children, and patch application. **C1:** the kernel handles duplicate keys during insertion/removal and implements explicit checks against script tags, event-like attributes, and obfuscated JavaScript/HTML URL vectors. **C3:** lazy nodes and keyed reconciliation provide concrete mechanisms for reusing work and DOM nodes. Start with [VirtualDom.js](https://github.com/elm/virtual-dom/blob/master/src/Elm/Kernel/VirtualDom.js), which keeps diffing, patching, and defensive input handling close enough to follow together. The security checks are evidence of adversarial-input complexity, not a claim that arbitrary user HTML becomes safe.

### 22. [purescript-halogen/purescript-halogen](https://github.com/purescript-halogen/purescript-halogen)

**Language/role:** PureScript; declarative components with typed queries, outputs, child slots, and an asynchronous runtime.

Study component composition that preserves strong types while hiding each child's internal state. **C2:** `RenderSpec` abstracts driver-specific rendering and persistent render state, allowing alternate drivers to reuse lifecycle and component machinery; its quantified types prevent internal component parameters from escaping. **C1:** disposal is guarded against repetition, subscriptions are removed, forked fibers are killed, and duplicate child-slot addresses produce a diagnostic. [Halogen/Aff/Driver.purs](https://github.com/purescript-halogen/purescript-halogen/blob/master/src/Halogen/Aff/Driver.purs) is a substantial implementation entry point for both mechanisms, especially `runUI`, child rendering, and finalization.

### 23. [reflex-frp/reflex-dom](https://github.com/reflex-frp/reflex-dom)

**Language/role:** Haskell; functional reactive DOM construction, dynamic widgets, server rendering, and hydration.

Study a declarative UI expressed through typed events and timelines rather than repeated virtual-tree construction. **C2:** [Builder/Class.hs](https://github.com/reflex-frp/reflex-dom/blob/develop/reflex-dom-core/src/Reflex/Dom/Builder/Class.hs) separates `DomSpace`, `DomBuilder`, node configuration, and adjustable construction, allowing the interface to work through different monad stacks and builder implementations. **C1:** the [immediate/hydration builder](https://github.com/reflex-frp/reflex-dom/blob/develop/reflex-dom-core/src/Reflex/Dom/Builder/Immediate.hs) must match existing DOM at switchover and reconcile programmatic input updates with user edits that happened before hydration completed. It explicitly orders those events and reads back browser-normalized values. These are concrete browser-state correctness problems beyond the abstract FRP API.

### 24. [reagent-project/reagent](https://github.com/reagent-project/reagent)

**Language/role:** ClojureScript; declarative React integration with its own reactive atoms, reactions, dependency capture, and update coordination.

Study the substantive runtime behind the integration, rather than counting a generated binding as a separate renderer. **C1:** reactions update their watched dependency sets as reads change and dispose subscriptions when no longer observed. **C3:** ordered dependency comparison avoids rebuilding identical watch sets, while dirty-state tracking suppresses redundant queued work. See [ratom.cljs](https://github.com/reagent-project/reagent/blob/master/src/reagent/ratom.cljs).

**C4:** the [changelog](https://github.com/reagent-project/reagent/blob/master/CHANGELOG.md) records dated releases across 2020–2025, migration to React 19, testing against both React 18 and 19 APIs, and a specific StrictMode mount/unmount/remount fix that otherwise lost reactive subscriptions. This is unusually useful evidence of compatibility management at a framework boundary.

### 25. [TokamakUI/Tokamak](https://github.com/TokamakUI/Tokamak)

**Language/role:** Swift; SwiftUI-compatible declarative API with independent reconciliation and renderer implementations. **Archived; historical study target.** The checked repository page also says it is looking for active maintainers.

Study how declarative Swift view values become persistent mounted elements without Apple's proprietary renderer. **C2:** the [renderer guide](https://github.com/TokamakUI/Tokamak/blob/main/docs/RenderersGuide.md) separates platform targets, mounting, updating, unmounting, and platform-specific primitive bodies. **C3:** [StackReconciler.swift](https://github.com/TokamakUI/Tokamak/blob/main/Sources/TokamakCore/StackReconciler.swift) defers updates through a platform scheduler and deduplicates queued rerenders. Its comments explicitly acknowledge that the deduplication benefit was not benchmark-proven. The value is an inspectable scheduling and renderer abstraction, not a claim of current maintenance or measured superiority.

## Coverage and search notes

Discovery used live web searches across more than six distinct formulations: browser reconciliation architectures; Rust reactive/native UI; native Flutter/Compose/Litho/ComponentKit runtimes; PureScript/Haskell functional components; Swift renderer protocols; Qt/QML official mirrors and scene graphs; resumable and compiler-driven Qwik/Marko frameworks; C#/XAML composition; and smaller Rust alternatives such as Sycamore, Ribir, and Sauron. Follow-up queries targeted asynchronous layout, hydration, renderer internals, and mirror provenance. Later searches chiefly added alternatives to already represented architectural families, so the selection stopped at 25 rather than accumulating near-duplicate examples.

Canonical repository URLs were checked through the live GitHub API or by opening repository pages and following redirects. Public source files and official documentation were then opened and read; a second rendering of the same README was not counted as additional evidence. An unauthenticated API rate limit interrupted metadata collection, so the remaining repositories were verified through their public GitHub pages. React and React Native's current canonical owner differs from older search results. Archive indicators were checked; absence of an archive banner is not used as proof of ongoing maintenance.

The boundaries are deliberate: no component collections, application starters, generated wrappers, awesome lists, pure graphics APIs, or immediate-mode-only toolkits are included. Proprietary SwiftUI itself has no inspectable GitHub implementation meeting this brief; Tokamak supplies a clearly labeled historical alternative. React Native contributes a substantive native renderer beyond React's reconciler. Reagent contributes its own reactive runtime beyond its React bindings. AndroidX, Flutter, Lit, and other monorepos each receive one entry; Compose distribution forks and separate copies of the same engine are not counted again. Other credible web frameworks and Rust libraries are omitted to keep this a diverse selection guide rather than an exhaustive ecosystem census.

Performance discussion identifies mechanisms and constraints, not independently reproduced benchmarks. No candidate code was executed, dependencies installed, or large repositories cloned. C4 is awarded only where dated compatibility or testing evidence was actually inspected. Older design pages and experimental or archived implementations are labeled where that affects how an engineer should use the entry point.
