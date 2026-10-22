# Entity-component systems

Research date: **2026-10-09**.

This selection covers **25 GitHub repositories** implementing reusable entity-component systems: component storage, entity identity and lifetime, queries, reactive membership, and system execution. It includes standalone libraries and Bevy's independently usable ECS subsystem, counted once within its engine monorepo. The emphasis is on architectural study, across native, managed, scripting, and functional languages, rather than benchmark rankings or popularity. Each repository's canonical page and additional primary implementation or documentation material were opened. Links within entries are suggested reading entry points.

Criteria legend:

- **C1 — Correctness:** difficult invariants, aliasing, concurrency, mutation ordering, or failure modes.
- **C2 — Abstractions:** substantial reusable mechanisms applicable to different games, simulations, or applications.
- **C3 — Performance and structure:** concrete performance constraints addressed through understandable storage or execution architecture.
- **C4 — Evolution:** evidence spanning years together with compatibility, testing, or complexity-management work. Age or a recent commit alone does not qualify.

Criteria assignments are grounded engineering judgments about the cited material, not certifications of correctness. A repository's inclusion does not imply that every subsystem is exemplary or that it is currently maintained. Explicit lifecycle caveats appear where supported by the reviewed sources.

## Native C and C++ libraries

### 1. [skypjack/entt](https://github.com/skypjack/entt)

**Language/role:** C++; embeddable, header-only ECS and related utilities. Study an ECS designed as composable containers, with independent component pools and no prescribed application loop.

- **C1:** Entity identifiers carry versions; destroying or releasing an identifier advances its version, and the registry exposes validity checks. This makes entity recycling and stale handles explicit parts of the model.
- **C2:** Storage customization through static mixins, unconstrained component types, signals, views, and groups provides a substantial toolkit without requiring a system superclass or scheduler.
- **C3:** The sparse-set design separates component pools and makes additional query acceleration an explicit memory/performance choice. This is a useful counterpoint to libraries that always organize components into archetype tables.

Entry point: the official [ECS design and API guide](https://github.com/skypjack/entt/wiki/Entity-Component-System), especially design decisions, entity versions, storage, and views/groups.

### 2. [SanderMertens/flecs](https://github.com/SanderMertens/flecs)

**Language/role:** C core with a C++ API; archetype ECS with relationships, queries, and pipelines. Study the connection between structural mutation, command visibility, and parallel iteration.

- **C1:** During progression, structural operations become staged commands, preventing component-array relocation underneath iterators. Pipeline synchronization points make those commands visible to subsequent readers. The documentation explains why systems must declare otherwise invisible writes and why immediate systems retain mutation restrictions.
- **C2:** Queries, relationship-based modeling, phases, and pipelines offer reusable mechanisms for assembling simulations rather than a single fixed update loop.
- **C3:** Worker execution partitions table rows across threads; keeping entity ownership consistent until a synchronization point reduces synchronization needs. Thread-local command queues separate mutation recording from storage modification.

Entry point: [Systems.md](https://github.com/SanderMertens/flecs/blob/master/docs/Systems.md), particularly pipelines, staging, sync points, and threading.

### 3. [richardbiely/gaia-ecs](https://github.com/richardbiely/gaia-ecs)

**Language/role:** C++; archetype ECS with explicit chunk and component-layout machinery. Study the implementation beneath the query-facing API.

- **C1:** Chunk access has concrete invariants around column presence, valid row ranges, alignment, tag components, and component construction. Mutable access can update component versions; some low-level methods explicitly require the caller to satisfy preconditions to avoid undefined behavior.
- **C3:** Fixed-capacity chunks lay out component versions, identifiers, records, and data together. Cached pointers/offsets and separate handling of structure-of-arrays layouts expose how addressing overhead and memory layout are managed.

Entry point: [`include/gaia/ecs/chunk.h`](https://github.com/richardbiely/gaia-ecs/blob/main/include/gaia/ecs/chunk.h). Its layout comments, initialization, and view methods are more informative than headline speed claims.

## Rust: borrowing, scheduling, and alternative storage models

### 4. [bevyengine/bevy](https://github.com/bevyengine/bevy)

**Language/role:** Rust; the relevant subsystem is **`bevy_ecs`**, usable independently of the Bevy engine. Study how a general application execution model grows around an ECS.

- **C1:** System parameter types communicate data access to the scheduler. Parallel execution combines those access requirements with explicit system/set dependencies, making conflicting access and intended ordering architectural concerns.
- **C2:** Worlds, resources, bundles, schedules, change detection, messages, and observers support considerably more than component iteration. The distinction between scheduled message consumption and immediately triggered observers is particularly useful.
- **C3:** Components can use table or sparse-set storage. The documentation states the tradeoff directly: table storage favors iteration, while sparse sets favor adding and removing components.

Entry point: the [bevy_ecs crate documentation](https://docs.rs/bevy_ecs/latest/bevy_ecs/), including schedules, component storage, and observers. This entry evaluates that subsystem, not the entire renderer or game engine.

### 5. [Ralith/hecs](https://github.com/Ralith/hecs)

**Language/role:** Rust; a small archetype world/query library. Study the safety machinery of a storage library that leaves application scheduling to its caller.

- **C1:** Each archetype column has an atomic borrow state. Shared and unique accesses are checked, conflicting borrows panic, and column wrappers acquire and release their respective borrows. This makes the bridge between raw storage and safe references inspectable.
- **C2:** Typed queries, dynamic entity builders, command buffers, batch insertion, and prepared queries provide reusable storage operations without imposing a formal system abstraction.
- **C3:** Archetypes store entities with matching component sets and expose component columns; prepared queries can reuse query setup work.

Entry points: [archetype implementation](https://github.com/Ralith/hecs/blob/master/src/archetype.rs) and [API overview](https://docs.rs/hecs/latest/hecs/).

### 6. [leudz/shipyard](https://github.com/leudz/shipyard)

**Language/role:** Rust; sparse-set ECS with workloads and runtime borrowing. Study how independently written systems become composable scheduled workloads.

- **C1:** Workload construction documents scheduler/storage borrowing failures and duplicate-name errors. Barriers explicitly prohibit parallelism across a boundary, while fallible systems stop workload execution when an error occurs.
- **C2:** Workloads can be nested, appended, and merged while propagating run conditions and ordering requirements. This is a substantial composition layer above the component views.
- **C3:** Sparse-set storage is paired with parallel iterators and workload execution. Workloads execute compatible systems in parallel and preserve first-to-last evaluation where they cannot be parallelized.

Entry point: [Workload API and execution semantics](https://docs.rs/shipyard/latest/shipyard/struct.Workload.html); the repository introduction establishes the sparse-set storage lineage.

### 7. [amethyst/legion](https://github.com/amethyst/legion)

**Language/role:** Rust; archetype ECS with packing and automatic scheduling. Particularly useful as an architectural reference for fragmentation across many entity layouts.

- **C1:** A schedule promises the apparent ordering of system side effects while parallelizing compatible work. Its queries also distinguish read and mutable access, and change filters are explicitly described as conservative and coarse-grained.
- **C3:** Legion goes beyond contiguous arrays within each archetype: stable component slices can be packed across archetypes when a heuristic considers the move worthwhile. Declared component groups guide packing toward important query combinations.
- **C2:** Worlds, resources, query filters, schedules, and serialization separate storage and execution concerns into reusable pieces.

Entry points: [packed-archetype storage design](https://docs.rs/legion/latest/legion/storage/index.html) and [system/query documentation](https://docs.rs/legion/latest/legion/). The reviewed [release page](https://github.com/amethyst/legion/releases) identifies v0.4.0 as latest; current maintenance responsiveness was not established, so treat this as a design-study selection rather than an active-support recommendation.

### 8. [amethyst/specs](https://github.com/amethyst/specs)

**Language/role:** Rust; parallel ECS with selectable per-component storage. Study bitset-driven joins and the precise unsafe contracts needed to expose them safely.

- **C1:** The `Join` contract requires its membership mask to agree with storage and forbids repeated indices when that could produce aliased mutable references. Tuple joins intersect masks, and implementation comments explain why those intersections preserve safety.
- **C2:** Components choose storage implementations, including dense vectors, ordinary vectors, maps, flags, and tracked storage. Joining storage is separate from the optional dispatcher, allowing different execution arrangements.
- **C3:** Bitset membership intersections avoid inspecting unrelated components, and `ParJoin` supports parallel iteration subject to additional access guarantees.

Entry points: [`src/join/mod.rs`](https://github.com/amethyst/specs/blob/master/src/join/mod.rs) and [storage/execution overview](https://docs.rs/specs/latest/specs/).

### 9. [recatek/gecs](https://github.com/recatek/gecs)

**Language/role:** Rust; ECS worlds and queries generated from a compile-time archetype declaration. Study a deliberately closed-world alternative to dynamic archetype discovery.

- **C1:** Generated archetype traits encode component membership, while access APIs distinguish exclusive access that bypasses runtime borrow checks from shared-entry APIs that perform them and may panic. This is a concrete static/runtime safety tradeoff.
- **C3:** Precompiling the world/query structure removes the need for runtime query matching and query-cache construction; component slices expose dense archetype data directly.
- **C2:** Generated worlds still expose generic archetype, view, and component-access traits. The deliberate limitation is material: archetypes must be declared in advance, and components cannot presently be added or removed dynamically.

Entry point: [Archetype trait and borrowing APIs](https://docs.rs/gecs/latest/gecs/traits/trait.Archetype.html), read alongside the repository's explanation of generated queries. The project's absolute “zero-overhead” wording is not treated here as a measured guarantee.

## Managed runtimes: C#, Java, and Kotlin

### 10. [genaray/Arch](https://github.com/genaray/Arch)

**Language/role:** C#; archetype/chunk ECS. Study a relatively direct managed implementation of table-oriented storage.

- **C2:** Worlds and typed query descriptions separate component composition from application logic; the core is intended for use across different .NET game environments rather than one engine integration.
- **C3:** Archetypes group equal component compositions, and chunks provide the actual backing storage. Chunk allocation/trimming and configurable size/minimum-entity policies expose the tension between locality, memory consumption, and component size. The documented base size is a policy, not a universal cache-size guarantee.

Entry point: [Archetypes & Chunks](https://arch-ecs.gitbook.io/arch/documentation/archetypes-and-chunks), including the clarification that chunk sizes can grow with component composition.

### 11. [Doraku/DefaultEcs](https://github.com/Doraku/DefaultEcs)

**Language/role:** C#; per-type component pools with queries, reactive sets, systems, and serialization. Study shared component values and dense storage bookkeeping in a managed runtime.

- **C1:** A pool tracks entity-to-component mappings, links, and reference counts. Removing or relocating a shared component requires repairing all affected mappings; `SetSameAs` makes sharing a first-class operation rather than an accidental alias.
- **C2:** Query results can be used as sets, maps, or multimaps, with sequential/parallel systems and text/binary serialization layered above them.
- **C3:** Components occupy typed arrays with mappings into them. This keeps the dense iteration path separate from entity identity and lets multiple entities share one stored value. The documentation explicitly cautions that operations within one world should generally be treated as non-thread-safe.

Entry points: [component pool implementation](https://github.com/Doraku/DefaultEcs/blob/master/source/DefaultEcs/Internal/ComponentPool.cs) and the repository's detailed world/query/threading guide.

### 12. [friflo/Friflo.Engine.ECS](https://github.com/friflo/Friflo.Engine.ECS)

**Language/role:** C#; managed archetype ECS with query chunks and deferred mutation. Study how performance-oriented iteration can retain explicit misuse detection.

- **C1:** Structural changes inside query loops raise `StructuralChangeException`. Command buffers record those changes for later playback; documentation distinguishes recording on worker threads from playback on the main thread. It also explains an incremental migration escape hatch for pre-3.1 behavior.
- **C3:** Queries access component arrays through chunks and restrict work to matching archetypes, making the main iteration path an array traversal.
- **C2:** The same queries and command-buffer model work directly and inside query systems, alongside relations, hierarchy, events, and serialization described by the project.

Entry point: the [query and command-buffer guide](https://friflo.gitbook.io/friflo.engine.ecs/documentation/query), especially structural-change errors and their fixes.

### 13. [outfox/fennecs](https://github.com/outfox/fennecs)

**Language/role:** C#; archetype ECS with cached queries and stream views. Study the separation between selecting entities and choosing how to execute work over them.

- **C2:** A query represents a persistent world-specific selection, while stream views expose typed mutable data to `For` or `Job` execution. Bulk operations reuse the selection, and the wider API includes entity relations and links to objects.
- **C3:** Queries retain their matching archetypes and update as structure changes. Parallel jobs split work into chunks across cores. The documentation also exposes a real cost: many queries over fragmented archetypes increase update-notification overhead, so disposing unused queries matters.

Entry points: [query architecture and lifetime](https://fennecs.net/docs/Basic/Queries/index.html) and [parallel stream jobs](https://fennecs.net/docs/Basic/Streams/Stream.Job.html). The latter marks concurrency tuning as work in progress; it should not be read as a blanket automatic-safety guarantee.

### 14. [sschmid/Entitas](https://github.com/sschmid/Entitas)

**Language/role:** C#; context/group/reactive ECS, with optional code generation and Unity tooling. Study an event-driven membership model optimized around garbage-collected object lifetimes.

- **C1:** Automatic Entity Reference Counting prevents retained entities from returning to a pool prematurely. Entity destruction, event-handler cleanup, and explicit retain/release behavior expose the lifetime problems created by pooling.
- **C2:** Contexts, matchers, groups, collectors, and generated component accessors support reusable reactive logic. The framework can also be used in standalone C# applications.
- **C3:** Removed components return to indexed component pools; creation first tries to reuse an existing instance. This is a concrete mechanism for reducing allocation pressure.

Entry points: [Entity implementation](https://github.com/sschmid/Entitas/blob/main/src/Entitas/Entity/Entity.cs) and [entity/context documentation](https://github.com/sschmid/Entitas/wiki/Entities). The repository distinguishes the current GitHub project from its deprecated Unity Asset Store distribution.

### 15. [libgdx/ashley](https://github.com/libgdx/ashley)

**Language/role:** Java; compact ECS in the libGDX community, usable without adopting the whole game framework. Study the control flow around family membership and listeners.

- **C1:** Entity mutations are delayed when the engine is updating or family listeners are being notified. Reentrant `update` calls are rejected, and `finally` restores the updating flag, making callback and exception behavior visible in the core loop.
- **C2:** The engine composes entities, systems, families, and prioritized entity listeners; family selections are reusable outside a particular system subclass.
- **C3:** `getEntitiesFor` returns the same maintained family collection rather than reconstructing a query result for each call. Dedicated managers separate family membership, entity operations, and system ordering.

Entry point: [`Engine.java`](https://github.com/libgdx/ashley/blob/master/ashley/src/com/badlogic/ashley/core/Engine.java), especially mutation entry points and the update loop.

### 16. [junkdog/artemis-odb](https://github.com/junkdog/artemis-odb)

**Language/role:** Java; substantive continuation of Artemis, with aspect subscriptions, optional bytecode weaving, and serialization. Counted as one evolved implementation, not alongside its ancestor.

- **C1:** Aspect subscriptions are cached and synchronized with world changes. The implementation documents a subtle first-execution hazard: a subscription created during system processing can observe a different state from an already-existing subscription.
- **C3:** Changed/deleted entity bit vectors are converted into compact integer collections for updating subscriptions. Subscription reuse and component-composition identities keep membership processing distinct from gameplay logic.
- **C4:** The changelog documents releases across 2016–2019, deliberate breaking-change notices, dependency migration, JDK integration-test fixes, and later bytecode compatibility work. This establishes evolution and compatibility management, not merely repository age.

Entry points: [AspectSubscriptionManager](https://github.com/junkdog/artemis-odb/blob/develop/artemis-core/artemis/src/main/java/com/artemis/AspectSubscriptionManager.java) and [changelog](https://github.com/junkdog/artemis-odb/blob/develop/CHANGELOG.md). **Historical-study caveat:** the reviewed [GitHub release list](https://github.com/junkdog/artemis-odb/releases) still marks the 2019-era 2.3.0 release as latest; the README's “actively maintained” statement was not independently established.

### 17. [Quillraven/Fleks](https://github.com/Quillraven/Fleks)

**Language/role:** Kotlin Multiplatform; ECS with Kotlin configuration and family APIs. Study how an ECS can shed JVM reflection and retain a common cross-platform model.

- **C2:** Families express all/none component constraints, support sorting and iteration, and integrate hooks both directly and through iterating systems. Hook ordering is documented when multiple systems use the same family.
- **C3:** The project removed reflection when combining its JVM and multiplatform implementations. Its performance work explicitly exercises creation/removal, simple iteration, and repeated family-membership churn; the latter is more revealing than a position-update loop alone.

Entry points: [family semantics](https://github.com/Quillraven/Fleks/wiki/Family) and the repository's architecture/migration and benchmark descriptions. The [wiki](https://github.com/Quillraven/Fleks/wiki) clearly identifies the retained 1.x documentation as historical and directs fixes/features to 2.x; comparative benchmark ratios are not adopted here.

## JavaScript and TypeScript

### 18. [NateTheGreatt/bitECS](https://github.com/NateTheGreatt/bitECS)

**Language/role:** TypeScript/JavaScript; minimal entity membership and query toolkit with caller-owned component storage. Study the consequences of separating component identity from physical data representation.

- **C1:** The guide spells out immediate entity-ID recycling, deferred removal from query results, and optional versioned identifiers. It also explains a concrete failure mode: versioned IDs used directly as typed-array indices can exceed array bounds without JavaScript throwing.
- **C2:** Component stores may be arrays, structures of arrays, typed arrays, or other reference-identified objects. Worlds can share an entity index when sharing storage, while ordinary functions supply system logic.
- **C3:** Structure-of-arrays and typed-array layouts reduce object/allocation overhead; storage policy remains explicit instead of hidden behind a single representation.

Entry point: [Intro.md](https://github.com/NateTheGreatt/bitECS/blob/main/docs/Intro.md), particularly recycling, versioning, and cross-world storage ownership.

### 19. [LastOliveGames/becsy](https://github.com/LastOliveGames/becsy)

**Language/role:** TypeScript; schema-based ECS with reactive queries, access entitlements, and declarative system ordering. Study a higher-level alternative to caller-managed typed arrays.

- **C1:** Queries declare which components a system may read, write, create, or update; undeclared access produces an error. Query lists change between system executions, and added/removed/changed lists have explicit non-overlap and ephemeral-entity rules.
- **C2:** Schemas, reactive queries, coroutines, and entity references support complex workflows without turning every state change into an immediate callback.
- **C3:** Query maintenance follows component-shape changes instead of rescanning the entire entity population. Component schemas map fields to primitive array-buffer storage.

Entry points: [query semantics and entitlements](https://lastolivegames.github.io/becsy/guide/architecture/queries) and [component storage](https://lastolivegames.github.io/becsy/guide/architecture/components). **Material limitation:** despite the repository headline, the official [introduction](https://lastolivegames.github.io/becsy/guide/introduction) says multithreaded execution is not yet implemented and the API remains 0.x. This report does not credit implemented parallel execution.

### 20. [ecsyjs/ecsy](https://github.com/ecsyjs/ecsy)

**Language/role:** JavaScript; reactive, object-oriented ECS. **Archived on 2025-04-13**, as stated by GitHub; retained as a historical design reference, not a maintained dependency recommendation.

- **C1:** Entity/component deletion is deferred, removed component data is tracked separately, and system-state components can keep a logically dead entity around until cleanup finishes. These are useful lifecycle mechanisms to compare with immediate deletion and command buffers.
- **C2:** World-scoped systems, multiple queries, mutable component access, and reactive results form a reusable framework independent of any particular renderer.
- **C3:** Entity and component pools reduce object churn, while query membership is updated on component/entity changes. The core manager shows how pooling, notifications, and delayed release fit together.

Entry point: [`src/EntityManager.js`](https://github.com/ecsyjs/ecsy/blob/dev/src/EntityManager.js); the repository page supplies the archive status and framework scope.

## Go: archetype storage for games and simulations

### 21. [mlange-42/ark](https://github.com/mlange-42/ark)

**Language/role:** Go; archetype ECS with generic queries and entity relationships. Study a documented design suited to both games and agent-based simulation.

- **C1:** Recycled entity IDs carry generations, and invalid operations such as modifying a locked world deliberately panic. Extra debug checks improve error explanations without changing which operations are invalid.
- **C3:** An archetype graph caches transitions between component compositions. Relation targets subdivide archetypes into tables; empty tables for dead targets can be recycled while retaining allocated storage. This makes both iteration locality and relationship churn concrete design problems.
- **C2:** Queries, batch operations, relations, and resources can be used without adopting an internal system scheduler.

Entry points: [architecture](https://mlange-42.github.io/ark/architecture/) and [error-handling policy](https://mlange-42.github.io/ark/errors/). The architecture's machine-specific timing figures are not used as general performance claims.

### 22. [yohamta0/donburi-ecs](https://github.com/yohamta0/donburi-ecs)

**Language/role:** Go; archetype ECS associated with Ebitengine. The formerly common `yohamta/donburi` GitHub URL redirects to this canonical location; this is one project, not two entries.

- **C1:** World removal uses swap-removal, repairs the moved entity's location, and queues destroyed identifiers with incremented versions. Validity checks compare identity/readiness and the current archetype slot, exposing the invariants needed when rows and identifiers are reused.
- **C2:** Generic component handles, composable filters, ordered queries, and optional transform/hierarchy/event facilities make this useful beyond a minimal storage example.
- **C3:** Entity locations and component/archetype storage are separate structures. Component changes move entities between archetypes while preserving the lookup mapping.

Entry point: [`world.go`](https://github.com/yohamta0/donburi-ecs/blob/main/world.go), especially `Valid`, `Remove`, `removeAtLocation`, and archetype movement. The repository's older Go import examples should be distinguished from its redirected GitHub location.

## Lua, Python, and Haskell

### 23. [bakpakin/tiny-ecs](https://github.com/bakpakin/tiny-ecs)

**Language/role:** Lua; compact table-oriented ECS. Study how much lifecycle and query behavior can be expressed without a heavy type or object system.

- **C1:** Worlds queue entity changes/removals and reconcile system membership at update/refresh boundaries. Refresh has an explicit restriction against being called inside an update; membership lists and their reverse indices must remain consistent during removal.
- **C2:** Entities are ordinary Lua tables, filters are functions, and systems support processing, sorting, and lifecycle hooks. These abstractions coexist with other Lua object models.
- **C3:** Systems normally cache membership, but an experimental `nocache` option trades cached-list maintenance for filtering during traversal. Its limitations—no membership callbacks or sorting—make the tradeoff unusually explicit.

Entry point: [`tiny.lua`](https://github.com/bakpakin/tiny-ecs/blob/master/tiny.lua), including system options and entity management. **Low-churn status:** the maintainer's README says the project is largely finished and has seen few commits for years, while expressly rejecting the label “abandoned.”

### 24. [benmoran56/esper](https://github.com/benmoran56/esper)

**Language/role:** Python; entity/component database with processors and switchable world contexts. Study query-cache correctness in a dynamic language rather than native-memory layout alone.

- **C1:** Deferred deletion, component membership, cached query results, and context switching interact. The release notes record fixes for losing cached components across worlds and for incorrectly dropping a query filter when choosing the smallest membership set.
- **C2:** Plain Python component objects, prioritized processors, multiple contexts, and event dispatch support a broad range of small simulations and applications.
- **C3:** The implementation uses membership sets and query caches, with lazy invalidation. The 3.5 optimization work targets smallest-set traversal and repeated modification overhead, illustrating workload-aware improvements without changing language runtimes.

Entry points: [implementation](https://github.com/benmoran56/esper/blob/master/esper/__init__.py) and [release notes](https://github.com/benmoran56/esper/blob/master/RELEASE_NOTES). The 3.0 move from `World` objects to module-level context operations is an explicit API break.

### 25. [jonascarpay/apecs](https://github.com/jonascarpay/apecs)

**Language/role:** Haskell; type-driven ECS with replaceable storage backends and system combinators. This is the Haskell project, distinct from the unrelated Rust library with the same short name.

- **C2:** Map, unique, global, and read-only stores provide different component semantics behind common access classes. Cache wrappers compose around eligible stores, and boxed, unboxed, and storable vector variants expose representation choices.
- **C1:** The `Cachable` constraint excludes unique/global stores whose semantics do not behave like ordinary maps. Cache collisions write displaced values back to the underlying store, while membership enumeration must avoid reporting the same entity from both layers.
- **C3:** Cache capacity is a type-level parameter, rounded to a power of two for masked indexing. The source explicitly warns that iteration over a sparsely occupied cache can be slower, making locality and capacity tradeoffs part of the abstraction.

Entry point: [storage implementations](https://github.com/jonascarpay/apecs/blob/master/apecs/src/Apecs/Stores/Internal.hs). The [package definition](https://github.com/jonascarpay/apecs/blob/master/apecs/apecs.cabal) also exposes QuickCheck-based testing and Criterion benchmark targets; neither was executed for this report.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations, covering:

1. C/C++ sparse sets versus archetype storage, including EnTT, Flecs, and less prominent implementations.
2. Rust borrowing, parallel scheduling, and storage families: hecs, Shipyard, Legion, Specs, and Bevy.
3. C# archetype/chunk libraries, reactive groups, and managed component pools.
4. JavaScript/TypeScript typed arrays, shared-memory aspirations, reactive queries, and access declarations.
5. Go archetype libraries, scientific/agent simulation, and the Arche/Ark lineage.
6. Java, Kotlin Multiplatform, Lua, Python, and Haskell implementations.
7. Compile-time archetypes and constrained ECS designs, which added gecs.
8. Rollback-oriented ECS and Zig/Odin implementations, followed by broader cross-language storage searches.

Follow-up searches increasingly returned already-covered storage families, wrappers, examples, benchmark-only repositories, and newer candidates without enough additional verified evidence to improve this selection. The final list favors distinct engineering lessons; it is not an exhaustive ecosystem inventory. Smaller projects such as gaia-ecs, gecs, fennecs, Ark, and apecs were retained on implementation evidence, not star counts.

Bindings around Flecs, generated wrappers, awesome-lists, tutorials, and benchmark-only repositories were not counted as independent ECS implementations. Unity's public ECS samples were excluded because examples are not the underlying Entities implementation. Bevy is counted once, and Artemis-odb's substantive continuation is not duplicated by listing original Artemis. The Donburi redirect was resolved rather than counted as another project. Moved-host candidates were not retained without verifying an official substantive GitHub mirror; no unofficial mirror is presented as upstream.

The main coverage gaps are embedded/constrained runtimes, Zig/Odin, Luau-specific ecosystems, and rollback-specialized ECS. These were discovery angles, but no claim is made that every candidate in them received a full review. Source files and documentation were read; candidate code was not cloned, installed, or executed, and benchmark claims were not independently reproduced. Some GitHub pages and documentation URLs failed to render, and the unauthenticated API was rate-limited; successful repository pages, raw source reads, and official documentation supplied the evidence used above. Default-branch implementation links and released API documentation can describe different revisions, so readers should pin a version before applying an API example. C4 is used conservatively where dated evolution and compatibility/testing evidence were actually inspected.
