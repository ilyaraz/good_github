# Reactive state management and incremental UI libraries

Research date: **2026-10-09**.

This selection covers libraries that maintain reactive application state, propagate derived values, or incrementally update user interfaces. It includes framework-independent engines, the relevant subsystems of UI-framework monorepos, functional reactive programming, and native/mobile state architectures. The 27 repositories are selected for engineering study, not ranked as adoption recommendations. Related projects are retained when their implementation layers or tradeoffs differ materially.

**Criteria legend:** **C1** = difficult correctness involving invariants, concurrency, adversarial inputs, or failure modes; **C2** = substantial reusable abstractions supporting multiple use cases; **C3** = concrete performance constraints addressed through understandable architecture; **C4** = sustained evolution accompanied by compatibility, testing, or complexity management. Criteria assignments below are grounded engineering judgments about the cited material, not proofs of correctness or benchmark results.

Canonical URLs, default branches, fork status, and archive status were checked through GitHub's repository API. All retained repositories were unarchived at the research date except the explicitly historical Incremental DOM entry. This does not establish a maintenance guarantee. Source links follow the inspected default branches and may change subsequently.

## JavaScript and TypeScript state engines

### 1. [mobxjs/mobx](https://github.com/mobxjs/mobx)

**Language/role:** TypeScript; observable state, computed values, and reactions, with UI integrations in the monorepo.

Study how a mutable programming interface can maintain a graph of derived values without making the application manually coordinate subscriptions. The useful distinction is between changing an input, recomputing a derivation, and actually notifying downstream observers.

- **C2:** Observable models and derived values can live outside a UI framework; the repository demonstrates adapting that model to React through `observer`. This makes the dependency engine reusable independently of a component hierarchy. [Repository introduction](https://github.com/mobxjs/mobx#introduction).
- **C3:** Computeds cache their output, evaluate lazily, suspend when unobserved, and suppress downstream work when the derived result is unchanged. The documentation also explains why forcing a computed to stay alive changes resource retention. [Computed-value design and examples](https://mobx.js.org/computeds.html).

### 2. [preactjs/signals](https://github.com/preactjs/signals)

**Language/role:** TypeScript; a framework-independent signal core with Preact and React integrations.

This is an unusually accessible study of the data structures behind reactivity. The implementation article explains dependency edges, allocation costs, notification scheduling, and cache invalidation as related design decisions.

- **C1:** Dynamic dependencies must be replaced when a conditional computation changes branches. Computeds also subscribe to upstream notifications only when needed downstream, avoiding references that would otherwise retain unreachable computations. [Dependency tracking and subscription lifetime](https://preactjs.com/blog/signal-boosting/).
- **C3:** The documented design reuses doubly linked dependency nodes, embeds scheduling links in effects, deduplicates notifications, and checks dependency/global versions before recomputation. These are concrete reductions in allocation and redundant work, rather than an unsupported speed ranking. [Implementation discussion](https://preactjs.com/blog/signal-boosting/).

The article describes the 2022 design evolution; use it as an architectural entry point alongside the current repository, not as a claim that every detail is unchanged.

### 3. [stackblitz/alien-signals](https://github.com/stackblitz/alien-signals)

**Language/role:** TypeScript; a compact, reusable push-pull signal algorithm and public signal API.

Study the separation between graph mechanics and the surface API. Unlike a thin framework adapter, this repository implements the dependency graph itself and exposes `createReactiveSystem` for other APIs.

- **C1:** Dependency edges belong to both subscriber and dependency lists; unlinking must update both directions and detect the last subscriber. Propagation distinguishes pending, dirty, and recursive-update states, including writes made during propagation. [Graph implementation](https://github.com/stackblitz/alien-signals/blob/master/src/system.ts).
- **C2:** The engine accepts update, notification, and unwatched callbacks, allowing different signal interfaces to share its algorithms. [Custom surface API documentation](https://github.com/stackblitz/alien-signals#creating-your-own-surface-api).
- **C3:** The core deliberately uses iterative traversal and linked graph structures instead of recursive function calls and Array/Set/Map-based graph bookkeeping. The README explains those constraints and provides simpler recursive equivalents for understanding the algorithm. [Algorithm rationale](https://github.com/stackblitz/alien-signals#about-propagate-and-checkdirty-functions).

### 4. [pmndrs/jotai](https://github.com/pmndrs/jotai)

**Language/role:** TypeScript; composable atoms with a vanilla store and React bindings.

Study how atom definitions remain separate from per-store state and how derived atoms form a dynamically maintained graph. The official internals tutorial is explicitly simplified; the production implementation provides the more instructive lifetime and asynchronous-state bookkeeping.

- **C2:** Primitive, read-only, write-only, and read-write atoms share a compositional interface. Read functions establish dependencies while write functions can coordinate updates across atoms. [Core internals guide](https://github.com/pmndrs/jotai/blob/main/docs/guides/core-internals.mdx).
- **C1:** Production state distinguishes mounted dependencies, listeners, atom errors, pending promise dependents, and unmount cleanup. The source even records a retention tradeoff for continuing promises, making the limits visible rather than implying effortless garbage collection. [Vanilla store internals](https://github.com/pmndrs/jotai/blob/main/src/vanilla/internals.ts).
- **C3:** Dependency epochs and store validation epochs support detecting whether cached atom state needs validation or recomputation. The same internals file is the entry point for following those mechanisms.

### 5. [pmndrs/valtio](https://github.com/pmndrs/valtio)

**Language/role:** TypeScript; mutable proxy state with immutable snapshots and React read tracking.

Valtio offers a useful contrast to atom APIs: application code mutates objects, while rendering consumes snapshots. Its two kinds of proxy have different jobs—tracking writes and tracking which snapshot properties a render actually reads.

- **C1:** Mutable source objects and immutable snapshots must remain semantically distinct. Snapshot methods evaluate against the frozen snapshot, and object prototypes are preserved; this exposes subtle identity and `this` behavior. [Snapshot semantics](https://github.com/pmndrs/valtio/blob/main/docs/api/advanced/snapshot.mdx).
- **C3:** Unchanged snapshots retain their identity, and updated snapshots reuse unchanged nested objects. Read tracking then limits rendering work to accessed state. [Copy-on-write explanation](https://github.com/pmndrs/valtio/blob/main/docs/api/advanced/snapshot.mdx) and [two-proxy architecture](https://github.com/pmndrs/valtio#react-via-usesnapshot).

The inspected snapshot guide contains older promise-handling descriptions; the repository's current React guidance discusses React's `use` API. The selection relies on the snapshot identity and sharing design, not on treating those async descriptions as interchangeable.

### 6. [nanostores/nanostores](https://github.com/nanostores/nanostores)

**Language/role:** JavaScript/TypeScript; small atomic and derived stores usable across UI frameworks.

Study a small implementation that still has meaningful scheduling and lifecycle choices. Stores activate resource-owning logic when observed and can deactivate it after listeners disappear.

- **C2:** Atoms, maps, computed stores, effects, and lifecycle hooks form reusable building blocks for application logic, with integrations spanning React, Vue, Svelte, Solid, and plain JavaScript. [Store and lifecycle guide](https://github.com/nanostores/nanostores#guide).
- **C3:** The computed implementation uses an epoch fast path, compares dependency arguments before calling the derivation, and offers end-of-tick batching. Upstream listeners are attached through `onMount` and removed on cleanup. [Computed implementation](https://github.com/nanostores/nanostores/blob/main/computed/index.js).

The inspected implementation also guards against stale promise resolutions, but explicitly deprecates that particular promise mechanism in favor of a separate async package; it is a useful compatibility detail, not a recommended new API.

### 7. [LegendApp/legend-state](https://github.com/LegendApp/legend-state)

**Language/role:** TypeScript; fine-grained observable state with persistence and synchronization facilities.

Study how path-level change records connect local mutation, batched notifications, previous values, and persistence/sync provenance. The batching layer is more revealing than the project's headline benchmark claims.

- **C1:** Batches must account for a value changing and then reverting, parent replacement superseding child changes, and an unmatched batch boundary after an exception. The code explicitly handles these cases and distinguishes immediate listeners from batched listeners. [Batching implementation](https://github.com/LegendApp/legend-state/blob/main/src/batching.ts).
- **C3:** Previous state is reconstructed lazily because cloning is expensive; notification records consolidate changes and avoid notifying for reverted values. This gives a concrete example of paying for historical state only when a consumer asks for it. [Same implementation](https://github.com/LegendApp/legend-state/blob/main/src/batching.ts).
- **C2:** The observable layer also supports computed state and local/remote synchronization adapters. [State and persistence overview](https://github.com/LegendApp/legend-state).

### 8. [effector/effector](https://github.com/effector/effector)

**Language/role:** TypeScript; event-driven stores and effects, with framework bindings in the monorepo.

Study how explicit dataflow operations become scheduled graph work. Effector is useful for comparing a graph built from events and stores with graphs inferred from property reads.

- **C1:** Its execution kernel distinguishes child, pure, read, barrier, sampler, and effect priorities. Ordering combined state, sampled state, and side effects is a correctness problem made explicit in the scheduler. [Kernel and priority ordering](https://github.com/effector/effector/blob/master/src/effector/kernel.ts).
- **C3:** The kernel uses linked queues for ordinary priority buckets and a skew heap for barrier/sampler work, with ordering also based on node IDs. The data structures expose the cost and scheduling model directly. [Queue implementation](https://github.com/effector/effector/blob/master/src/effector/kernel.ts).
- **C2:** The library's combinable stores and view-independent logic serve several frontend frameworks and Node.js. [Design principles](https://github.com/effector/effector#introduction).

## Browser frameworks with substantial reactive runtimes

### 9. [solidjs/solid](https://github.com/solidjs/solid)

**Language/role:** TypeScript; fine-grained UI rendering, especially `packages/solid/src/reactive` and the store primitives.

Study the relationship between signal dependencies, computation ownership, and rendering. Solid's educational material reconstructs a small reactive system, while the production runtime makes ownership and computation state explicit.

- **C2:** Signals and observers underpin stores, memoized derivations, resources, and render effects. These are related abstractions for mutable data, derived data, asynchronous results, and external side effects. [Fine-grained reactivity guide](https://docs.solidjs.com/advanced-concepts/fine-grained-reactivity).
- **C3:** Fine-grained subscriptions target the affected output, while memos cache derived computations. The runtime separately represents signal observers, source slots, ownership/cleanup, and update/effect queues. [Signal runtime](https://github.com/solidjs/solid/blob/main/packages/solid/src/reactive/signal.ts).

This entry concerns Solid's reactive/UI core, not the separate SolidStart application framework.

### 10. [vuejs/core](https://github.com/vuejs/core)

**Language/role:** TypeScript; Vue's core monorepo, particularly `packages/reactivity` and its integration with rendering.

Study how a widely used object/ref API hides dependency tracking while still exposing important identity and tracking boundaries. The explanatory documentation intentionally uses simplified pseudocode; the current computed implementation is a useful corrective to reading that pseudocode as literal internals.

- **C2:** Reactive objects, refs, computed refs, and effects provide reusable state abstractions, including read-only and writable computed values. [Reactivity in depth](https://vuejs.org/guide/extras/reactivity-in-depth.html).
- **C1:** The computed implementation avoids notifying itself recursively, distinguishes read-only from writable values, and synchronizes dependency versions after evaluation. [Computed implementation](https://github.com/vuejs/core/blob/main/packages/reactivity/src/computed.ts).
- **C3:** Dirty/notified flags, dependency links, batched notification, and refresh-on-read make invalidation and evaluation separate operations. The inspected source exposes these mechanisms without requiring a tour of the entire framework.

### 11. [sveltejs/svelte](https://github.com/sveltejs/svelte)

**Language/role:** JavaScript/TypeScript; compiler and reactive runtime in `packages/svelte`, including rune-based derived state.

Study the boundary between compile-time transformation and runtime dependency tracking. This is particularly useful when comparing Svelte's ordinary-looking source syntax with libraries whose signals are explicit function or object calls.

- **C1:** Derived expressions disallow state mutation, and dependency tracking has documented synchronous and transformed-`await` boundaries. These constraints prevent some feedback problems while explaining which reads remain reactive. [Derived-state semantics](https://svelte.dev/docs/svelte/$derived).
- **C3:** State writes push invalidation through dependencies, but derived values are pulled only when read; unchanged derived results suppress downstream updates. This complements the repository's compiler-based DOM-update strategy. [Update propagation](https://svelte.dev/docs/svelte/$derived#Update-propagation) and [compiler overview](https://github.com/sveltejs/svelte#what-is-svelte).

The inspected documentation also identifies a version boundary for writable derived values, illustrating why examples from different Svelte generations require care.

## Rust reactive state and UI ownership

### 12. [leptos-rs/leptos](https://github.com/leptos-rs/leptos)

**Language/role:** Rust; especially the reusable `reactive_graph` subsystem, alongside UI rendering and reactive stores.

Study a runtime designed around expensive effects rather than merely maximizing raw graph-update throughput. Its current crate documentation is more appropriate for this entry than older architecture prose referring to previous crate names.

- **C2:** Signals, synchronous/asynchronous computations, and effects are independent of the DOM. Effects use an executor abstraction that can work with browser, Tokio, or GTK environments. [Reactive graph design](https://github.com/leptos-rs/leptos/blob/main/reactive_graph/src/lib.rs).
- **C3:** Dependencies are rediscovered dynamically, inactive conditional branches stop causing recomputation, and effects run asynchronously on a subsequent runtime tick. The documentation explicitly states the tradeoff of spending more on graph propagation to avoid unnecessary external effects. [Design principles](https://github.com/leptos-rs/leptos/blob/main/reactive_graph/src/lib.rs).
- **C1:** Scoped async work distinguishes preserving reactive ownership from actually cancelling work when the owner is cleaned up; separate helpers implement those different contracts in the same source file.

### 13. [DioxusLabs/dioxus](https://github.com/DioxusLabs/dioxus)

**Language/role:** Rust; the monorepo's `packages/signals` subsystem and its component-runtime integration.

Study how convenient `Copy` signal handles coexist with runtime ownership, borrowing, and cross-thread storage. Dioxus is retained separately from direct-DOM signal frameworks because its signal state participates in a broader component/renderer architecture.

- **C1:** Signals are owned by component scopes, with APIs for explicit owner selection. The source documents how repeatedly allocating outside a hook retains values until that owner is dropped. It also distinguishes synchronized and unsynchronized storage and maintains subscribers behind shared synchronization. [Signal ownership and storage](https://github.com/DioxusLabs/dioxus/blob/main/packages/signals/src/signal.rs).
- **C2:** The subsystem provides local signals, per-application global signals, global memos, selectors, and separate read/write abstractions; these support multiple state-lifetime and derived-state needs. [Signal API](https://github.com/DioxusLabs/dioxus/blob/main/packages/signals/src/signal.rs) and [module organization](https://github.com/DioxusLabs/dioxus/blob/main/packages/signals/src/lib.rs).

### 14. [sycamore-rs/sycamore](https://github.com/sycamore-rs/sycamore)

**Language/role:** Rust; reactive web UI, particularly `packages/sycamore-reactive`.

Study a relatively contained arena-backed reactive graph. The central `Root` explicitly owns graph nodes, dependency tracking, a pending-update queue, and batch depth.

- **C1:** Before reading a dirty node, dependencies must be brought up to date. Updating a node removes old dependency links, disposes children created by its previous execution, and reconstructs the current dependencies. Nested batches wait for the outermost boundary. [Root and update implementation](https://github.com/sycamore-rs/sycamore/blob/main/packages/sycamore-reactive/src/root.rs).
- **C3:** The root reuses a sorting buffer to avoid allocating a new vector on each propagation and separates clean/dirty state from graph ownership. This offers concrete memory and recomputation tradeoffs in a smaller code surface. [Same implementation](https://github.com/sycamore-rs/sycamore/blob/main/packages/sycamore-reactive/src/root.rs).

The source candidly documents that the app-lifetime root itself may be leaked while its managed resources are disposable; this is an intentional lifetime convention, not a general leak-freedom claim.

## ClojureScript and distributed reactive UI

### 15. [day8/re-frame](https://github.com/day8/re-frame)

**Language/role:** ClojureScript; application state and event architecture above Reagent/React.

Study how a single application database feeds a demand-built subscription graph. This differs from treating the component tree as the primary owner of all state and computation.

- **C2:** Registered subscriptions describe reusable query/derivation nodes; view demand instantiates the required graph, and nodes disappear when no remaining view needs them. Pure subscription functions compose through other subscriptions. [Subscription architecture](https://github.com/day8/re-frame/blob/master/docs/subscriptions.md).
- **C3:** The documentation separates cheap extractors from expensive materialized views. Every root-state change can rerun extractors, but equality-based propagation pruning stops unchanged fragments from triggering downstream calculations and rendering. [Four layers and propagation pruning](https://github.com/day8/re-frame/blob/master/docs/subscriptions.md).

This explicit account of where work still occurs makes re-frame useful for studying incremental computation without assuming that every root update is free.

### 16. [reagent-project/reagent](https://github.com/reagent-project/reagent)

**Language/role:** ClojureScript; React integration with reactive atoms, reactions, and batching.

Study the boundary where ClojureScript dereference tracking meets React's rendering lifecycle. It is a distinct implementation layer from re-frame, which builds application-level event and subscription conventions above it.

- **C1:** Reactions capture dereferenced atoms and update their watched dependencies. React StrictMode's mount/unmount/remount sequence required explicit fixes to prevent permanently lost atom watches. [Ratom implementation](https://github.com/reagent-project/reagent/blob/master/src/reagent/ratom.cljs) and [2.0.1 regression explanation](https://github.com/reagent-project/reagent/blob/master/CHANGELOG.md).
- **C3:** The source avoids rebuilding watch relationships when dereferences occur in the same order, caches watch arrays for notification, and queues reactions for batched processing. [Ratom implementation](https://github.com/reagent-project/reagent/blob/master/src/reagent/ratom.cljs).
- **C4:** The inspected changelog documents 2021 dependency changes, 2023 React 18 integration, and 2025 React 19/concurrent-mode testing while retaining tests for an older React integration. This is concrete compatibility work across years. [Changelog](https://github.com/reagent-project/reagent/blob/master/CHANGELOG.md).

### 17. [hyperfiddle/electric](https://github.com/hyperfiddle/electric)

**Language/role:** Clojure/ClojureScript; compiler and runtime for reactive client/server UI programs. **The inspected README advertises a v3 alpha snapshot.**

Study a more ambitious architecture in which client and server expressions share a reactive program and the compiler analyzes their network boundary. This is a research-rich implementation, but its alpha designation matters when considering adoption.

- **C1:** The compiler must preserve evaluation/effect order and references through graph rewrites. Its walkthrough explains separate stable identities, ordered graph entities, and explicit effect-order passes. [Compiler walkthrough](https://github.com/hyperfiddle/electric/blob/master/src/hyperfiddle/electric/impl/lang_3_walkthrough.md).
- **C2:** Reactive functions, control flow, and client/server composition form a reusable programming model for networked interfaces. [Architecture and maturity statement](https://github.com/hyperfiddle/electric).
- **C3:** Compiler passes eliminate unused constructors, reroute aliases, inline locals, and collapse pure operations. These concrete transformations make the compiler's performance strategy inspectable. [Compiler passes](https://github.com/hyperfiddle/electric/blob/master/src/hyperfiddle/electric/impl/lang_3_walkthrough.md).

## Scala.js transactional FRP and DOM binding

### 18. [raquo/Airstream](https://github.com/raquo/Airstream)

**Language/role:** Scala/Scala.js; event streams, signals, variables, and owned subscriptions.

Study precisely scoped glitch-avoidance guarantees. Airstream explains why synchronous propagation, feedback loops, asynchronous operations, and observable startup cannot all be treated as the same transaction.

- **C1:** A transaction permits at most one emission per observable; pending observables are processed by topological rank. Async sources and potentially cyclic operations use new transactions. The implementation also limits nested transaction depth to prevent runaway feedback from freezing the UI. [Transaction implementation](https://github.com/raquo/Airstream/blob/master/src/main/scala/com/raquo/airstream/core/Transaction.scala).
- **C2:** Streams, signals, `Var`, event buses, combinators, and mandatory ownership support both application state and external event sources. [API and glitch model](https://github.com/raquo/Airstream#frp-glitches).
- **C3:** The current transaction source lazily creates a priority queue only when pending work exists; its ordering invariant explains both correctness and execution structure.

### 19. [raquo/Laminar](https://github.com/raquo/Laminar)

**Language/role:** Scala/Scala.js; direct DOM composition and bindings built on Airstream.

Study how observable ownership becomes a DOM lifecycle policy. Laminar separates creating a node from mounting it, and makes subscriptions follow actual mounting rather than object construction.

- **C1:** A fresh owner is activated on each mount and killed on unmount. Dynamic subscriptions can then restart when the element is remounted, addressing both never-mounted resource retention and dead bindings after reuse. [Ownership walkthrough](https://laminar.dev/documentation#ownership).
- **C2:** Typed modifiers, binders, and inserters compose attributes, events, individual children, and lists through a common element-building API. [Documentation](https://laminar.dev/documentation).
- **C4:** The [2020 lifecycle overhaul](https://github.com/raquo/Laminar/blob/master/CHANGELOG.md) explains migration and ordering changes; [the 2024 release discussion](https://github.com/raquo/Laminar/blob/master/website/blog/2024-05-14-laminar-v17.0.0.md) documents further API changes and migration helpers motivated by observable semantics. These show sustained complexity management, not just repository age.

## OCaml and Haskell incremental computation for interfaces

### 20. [janestreet/incremental](https://github.com/janestreet/incremental)

**Language/role:** OCaml; general incremental computation, explicitly including efficiently updated GUI views.

Study a rigorous account of dynamic DAG maintenance, observation, and stabilization. The interface documentation is itself a substantial architecture document with explicit failure contracts.

- **C1:** Node heights must increase along dependency edges, and `bind` introduces extra constraints for dynamically created subgraphs. Generative functors keep separate graph instances type-distinct. Exceptions during stabilization make the instance unusable, a significant failure mode documented rather than hidden. [Interface and invariants](https://github.com/janestreet/incremental/blob/master/src/incremental_intf.ml).
- **C3:** Stabilization visits necessary nodes through a recomputation heap and uses configurable cutoffs to stop propagation. The documentation discusses the heap's dependence on graph height and the consequences of increasing the height limit. [Stabilization design](https://github.com/janestreet/incremental/blob/master/src/incremental_intf.ml).

The [README](https://github.com/janestreet/incremental/blob/master/README.org) establishes the UI connection; this entry is an enabling reactive engine, not a DOM framework.

### 21. [janestreet/bonsai](https://github.com/janestreet/bonsai)

**Language/role:** OCaml; incremental, composable state machines underlying browser and terminal UI libraries.

Study a design that composes state and incrementality separately from rendering. The repository explains that the Bonsai core is more general than its web-oriented description; browser integration lives in Bonsai_web.

- **C2:** Time-varying values, state machines, mapped computations, and model reset behavior compose through the core API. The same core supports different UI frontends. [Repository architecture](https://github.com/janestreet/bonsai) and [core interface](https://github.com/janestreet/bonsai/blob/master/src/cont.mli).
- **C1:** The graph-building phase has an explicit graph parameter, while runtime operation forbids structural graph modification through that construction API. The type/interface design makes this phase boundary visible. [Graph contract](https://github.com/janestreet/bonsai/blob/master/src/cont.mli).
- **C3:** Lazy constants, custom equality cutoffs, and equality-aware state storage control recomputation and memory use. These are exposed policies that an engineer can trace from API contracts into the runtime.

### 22. [reflex-frp/reflex](https://github.com/reflex-frp/reflex)

**Language/role:** Haskell; deterministic higher-order FRP, used beneath Reflex-DOM interfaces.

Study a typed distinction between a sampled time-varying value, event occurrences, and a value paired with change notifications. This provides a useful semantic counterpoint to libraries that call all three concepts “signals.”

- **C1:** `Dynamic` requires its behavior to change exactly when its update event fires. Timelines identify independent reactive contexts, and event combinators specify simultaneous occurrences and switching semantics. [Core FRP class](https://github.com/reflex-frp/reflex/blob/develop/src/Reflex/Class.hs).
- **C2:** `Behavior`, `Event`, `Dynamic`, and `Incremental`, together with push/pull computation interfaces, support compositional interactive programs; the README identifies the Reflex-DOM integration. [Repository overview](https://github.com/reflex-frp/reflex) and [semantic interface](https://github.com/reflex-frp/reflex/blob/develop/src/Reflex/Class.hs).
- **C3:** `Incremental` supports patches to large values rather than full replacement, and “cheap” combinators deliberately trade caching for repeat computation. The interface documents those performance contracts explicitly.

## Mobile, multiplatform, and native state architectures

### 23. [rrousselGit/riverpod](https://github.com/rrousselGit/riverpod)

**Language/role:** Dart; reactive caching and data binding, including the core package and Flutter integrations.

Study provider state as a resource with dependency-driven recomputation and a listener-dependent lifetime. The disposal documentation is especially useful for asynchronous data, where caching policy and cleanup correctness interact.

- **C1:** Recomputing a provider destroys its previous state; becoming unobserved invokes a different lifecycle sequence involving cancellation, a grace period, and disposal. Cleanup callbacks must avoid mutations that create unintended provider side effects. [Automatic disposal contract](https://riverpod.dev/docs/concepts2/auto_dispose).
- **C2:** Providers expose synchronous and asynchronous state independently of widget implementation, while Flutter consumers react to loading, error, and data states. [Core/framework package overview](https://github.com/rrousselGit/riverpod).
- **C3:** `keepAlive` can retain successful fetch results without retaining failed requests, and timed retention can be built from lifecycle hooks. [Selective cache retention](https://riverpod.dev/docs/concepts2/auto_dispose#fine-tuned-disposal-with-refkeepalive).

### 24. [pointfreeco/swift-composable-architecture](https://github.com/pointfreeco/swift-composable-architecture)

**Language/role:** Swift; observable application state, reducers, effects, stores, and an exhaustive testing runtime.

Study how reactive UI state and asynchronous effects can be organized into features whose behavior is testable as an action sequence. The interesting code is not only the production store: `TestStore` embodies the architecture's expectations about unfinished work and state transitions.

- **C2:** State, actions, reducers, effects, and stores compose smaller feature domains into larger applications, with SwiftUI and UIKit integration. [Architectural model](https://github.com/pointfreeco/swift-composable-architecture#basic-usage).
- **C1:** Exhaustive tests assert state changes, effect-emitted actions, and completion of in-flight effects. The source demonstrates debouncing with a controlled clock and cancellation of superseded requests, making temporal behavior reproducible. [TestStore contracts and implementation](https://github.com/pointfreeco/swift-composable-architecture/blob/main/Sources/ComposableArchitecture/TestStore.swift).

This is evidence of a reusable correctness mechanism, not a claim that application tests constitute a formal proof.

### 25. [cashapp/molecule](https://github.com/cashapp/molecule)

**Language/role:** Kotlin; Compose-runtime state computation exposed as coroutine `Flow`/`StateFlow`, without a UI node tree.

Study how a UI-oriented recomposition runtime can serve as a headless presenter engine. This is retained for its explicit scheduling implementation, not merely because it adapts one API to another.

- **C2:** Model-producing composable functions can serve different display layers, and `StateFlow` exposes an initial model synchronously. The README demonstrates separating presentation state from display code. [Architecture and presenter example](https://github.com/cashapp/molecule).
- **C1:** The runtime bridges coroutine scope, frame-clock scheduling, and emission. Immediate mode gates a frame clock around a bounded output channel, whereas context-clock mode follows the supplied clock; these differences affect when values become observable. [Flow and clock implementation](https://github.com/cashapp/molecule/blob/trunk/molecule-runtime/src/commonMain/kotlin/app/cash/molecule/molecule.kt).
- **C3:** Gating recomposition around downstream consumption makes scheduling/backpressure an explicit mechanism. The same file also preserves hidden overloads for binary compatibility, although that fact alone is not assigned C4.

### 26. [arximboldi/lager](https://github.com/arximboldi/lager)

**Language/role:** C++; value-oriented application state and unidirectional dataflow for interactive programs.

Study how immutable-style reducers and reactive accessors can fit C++ GUI/event-loop environments. The architecture separates state transition logic from event injection, effects, and rendering, while cursors compose read/write access to state.

- **C1:** The documented store offers thread-safe dispatch but executes reducers through an event-loop integration. This separates concurrent event arrival from state-transition execution; it should not be generalized into a claim that every cursor operation is thread-safe. [Store and event-loop architecture](https://sinusoid.es/lager/architecture.html).
- **C2:** Reducers, stores, event-loop hooks, readers, writers, cursors, lenses, and transformations support different UI backends and state projections. The cursor code shows composition through reader/writer/watchable layers rather than a framework-specific widget type. [Cursor implementation](https://github.com/arximboldi/lager/blob/master/lager/cursor.hpp).

## Historical incremental rendering implementation

### 27. [google/incremental-dom](https://github.com/google/incremental-dom)

**Language/role:** TypeScript; in-place DOM patching and a compilation target for template languages. **Archived on 2025-06-20; read-only historical study.**

Study incremental rendering without constructing an intermediate virtual tree. This is a different layer from state propagation: callers determine when to patch, while the library reconciles a stream of element/text operations against existing DOM nodes.

- **C2:** Separate element-open, element-close, text, and patch operations form a reusable target for template compilers, including templates whose opening and closing tags occur in different functions. [Compilation-target rationale](https://github.com/google/incremental-dom#overview).
- **C3:** The API is designed to reduce intermediate allocation and garbage-collection pressure. The core walks existing siblings, matches identity/name/key, and removes unvisited nodes rather than materializing a fresh UI tree. [Patch core](https://github.com/google/incremental-dom/blob/master/src/core.ts).
- **C1:** The implementation exposes patch-context state and structural assertions, and gives nested patch calls separate argument buffers. These make reentrancy and structural consistency concrete study topics. [Same core source](https://github.com/google/incremental-dom/blob/master/src/core.ts).

## Search coverage and limitations

Discovery used more than six meaningfully different live search formulations: JavaScript signal graphs and state stores; Rust signal/UI libraries; Scala.js transactions and glitches; ClojureScript subscription and distributed UI systems; OCaml self-adjusting computation and Bonsai; Haskell FRP; Dart reactive providers; Swift observable state and effects; Kotlin headless Compose/multiplatform state; C++ value-oriented interactive systems; and historical incremental DOM rendering. Follow-up queries inspected small signal engines, alternative Kotlin architectures, and older DOM-binding families. Later searches increasingly returned adapters, ports, starters, and implementations overlapping already represented designs; Alien Signals and Incremental DOM were retained because they added substantive architectural contrasts.

Every retained repository has canonical GitHub verification and an opened primary source beyond its repository README. Architecture evidence comes from actual source files, documented invariants, lifecycle explanations, or design walkthroughs. Repository stars and unverified comparative benchmark claims were not used as quality criteria. Repositories were not cloned, installed, executed, or tested during this read-only research.

Generic reactive-stream libraries, incremental databases, and build systems were outside scope unless primary material established a direct UI/state role. Knockout, Ractive, Decompose, and related projects appeared in discovery but were not exhaustively reviewed; omission is not a negative quality judgment. The selection favors distinct mechanisms over including every established JavaScript state manager. Core and frontend projects such as Airstream/Laminar and Incremental/Bonsai are separate substantive implementations, while each monorepo is counted once.

Some documentation is conceptual, historical, or behind current development. In particular, Jotai and Vue label their instructional internals as simplified; the Preact article records a particular design evolution; Valtio has async wording spanning different APIs; and Electric advertises an alpha snapshot. A Laminar v18 draft contained unfinished release prose, so historical evolution claims instead use completed 2020 and 2024 material. These limits are material to interpretation. The report identifies worthwhile places to study, not uniformly exemplary components or a guarantee of current release readiness.
