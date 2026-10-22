# Game engines and simulation frameworks

Research date: **2026-10-09**

This selection covers 25 publicly inspectable GitHub repositories: general game engines, 2D and browser runtimes, physical and robotics simulation, discrete-event infrastructure, and agent-based modeling. It emphasizes reusable runtime machinery rather than individual games, visual demos, or standalone rendering and physics libraries. Large repositories are represented by specific subsystems worth studying. Public source availability does not imply identical licensing terms.

Every repository heading links to a verified GitHub repository page. The linked documentation or implementation sources within each entry are additional, inspected primary evidence and suggested reading entry points. The criteria identify reasons to study a codebase; they are not a certification of every component's quality.

## Criteria

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and structures supporting different applications.
- **C3 — Performance and architecture:** concrete runtime constraints addressed through understandable architectural choices.
- **C4 — Evolution:** documented development across years with compatibility work, testing, or deliberate management of complexity.

## General, 3D, and networked game engines

### [godotengine/godot](https://github.com/godotengine/godot)

**Language and role:** C++ engine with GDScript and C# application interfaces; integrated 2D/3D runtime and editor. A useful study in separating an approachable scene API from lower-level rendering, physics, and platform machinery.

- **C2:** The architecture distinguishes the scene layer, subsystem servers, drivers, platform integration, and foundational object/type facilities. These boundaries let an engineer trace a high-level node operation into reusable services without treating the editor and runtime as an undifferentiated whole. Start with the [engine architecture diagram and layer descriptions](https://docs.godotengine.org/en/stable/engine_details/architecture/godot_architecture_diagram.html).
- **C3:** The [servers and RIDs design rationale](https://godotengine.org/article/why-does-godot-use-servers-and-rids/) explains how opaque resource handles and command-oriented interfaces allow subsystem work to be buffered and synchronized across threads. This is explicitly a **historical 2016 explanation**, useful for understanding the design tradeoff; it should not be read as an exact description of every current threading path.

### [bevyengine/bevy](https://github.com/bevyengine/bevy)

**Language and role:** Rust game engine organized around an entity-component system. The especially instructive subsystem is `bevy_ecs`, which is also usable independently of the rest of the engine.

- **C1:** Systems declare access through typed parameters; scheduling uses access information and explicit dependencies to determine which systems may execute concurrently. This connects Rust-level data access to runtime scheduling constraints.
- **C2:** Worlds, entities, components, resources, queries, systems, and schedules form a reusable application model rather than a collection of game-specific classes.
- **C3:** Table storage favors iteration locality, while sparse-set storage favors component insertion and removal. The documentation makes this workload-dependent tradeoff explicit. The [ECS crate documentation](https://docs.rs/bevy_ecs/latest/bevy_ecs/) is the entry point for all three observations, including runnable API examples and links into the implementation.

### [o3de/o3de](https://github.com/o3de/o3de)

**Language and role:** C++ engine and tools monorepo. Focus on **Atom's rendering pass system**, rather than trying to assess the whole engine at once.

- **C1:** Pass attachments distinguish inputs, outputs, and input/output access, including whether previous contents must survive. The pass lifecycle separates resetting, attachment construction, validation, frame setup, and frame completion. These are concrete resource-lifetime and dependency contracts to inspect.
- **C2:** Parent passes compose a hierarchy; render passes submit GPU work. C++ implementations combine with JSON templates and requests so the same rendering machinery can be configured into different pipelines. The [Atom pass-system guide](https://www.docs.o3de.org/docs/atom-guide/dev-guide/passes/pass-system/) explains both the hierarchy and lifecycle, including integration with frame-graph scopes.

This is a strong candidate for studying how a large engine exposes extensible rendering structure while retaining validation points around GPU resources.

### [stride3d/stride](https://github.com/stride3d/stride)

**Language and role:** C# game engine and editor. Study the entity manager and processor architecture as an alternative to both deeply inherited scene objects and query-oriented Rust ECS designs.

- **C2:** Entities aggregate components, while processors implement behavior over matching entities. Separate transform, model-transform, and lighting processors demonstrate how rendering responsibilities can be assembled without putting all behavior into an entity base class.
- **C3:** The manager maintains processor membership as entities and components change. Processing matching sets together avoids repeatedly discovering the same relationships during every update and is explicitly motivated by cache efficiency. Processor ordering also makes transform propagation precede dependent rendering work.

The [entity-management and processor guide](https://doc.stride3d.net/latest/en/manual/engine/entity-component-system/managing-entities.html) is the architectural entry point. It is marked under construction, so its conceptual account is more useful than assuming it exhaustively specifies every API detail.

### [FyroxEngine/Fyrox](https://github.com/FyroxEngine/Fyrox)

**Language and role:** Rust 2D/3D engine and editor. Its object-pool design is particularly valuable for studying mutable scene graphs without pervasive reference-counted object ownership.

- **C1:** Handles combine a slot index with a generation; recycling a slot invalidates older handles. Reserved slots and restoration tickets add a second lifetime problem: an object can temporarily leave the pool while retaining its identity. The documentation distinguishes checked borrowing, invalid handles, restoration, and permanently releasing a reserved slot.
- **C2:** The same pool/handle abstraction supports scene nodes, animations, and audio, making it a reusable engine primitive rather than a scene-only trick.
- **C3:** The design exposes the benefits and costs of array-based storage, vacancy reuse, fragmentation, and indirect access. Start with the [data-management chapter](https://fyrox-book.github.io/beginning/data_management.html), which explains the invariants and tradeoffs with concrete examples.

### [jMonkeyEngine/jmonkeyengine](https://github.com/jMonkeyEngine/jmonkeyengine)

**Language and role:** Java 3D engine with a scene graph and application-state/control abstractions. A practical case study in integrating asynchronous application work into a thread-confined game loop.

- **C1:** The documented rule confines scene-graph operations to the update thread. Background tasks must work with suitable independent data, then submit changes through `enqueue`; merely moving scene access into a worker does not make it safe.
- **C3:** Expensive work such as pathfinding can leave the frame loop and return results through tasks and futures. The architecture distinguishes computing a result from applying it to shared engine state, giving a clear boundary for investigating responsiveness and synchronization costs.

The [multithreading guide](https://wiki.jmonkeyengine.org/docs/3.9/core/app/multithreading.html) includes the update-thread contract and task-based examples. It is a better starting point for this topic than surveying the engine's feature list.

### [panda3d/panda3d](https://github.com/panda3d/panda3d)

**Language and role:** C++ scene-graph engine with Python and C++ application APIs. Particularly useful for understanding frame pipelining and the difference between rendering throughput and interaction latency.

- **C2:** Application updates, scene traversal/culling, and graphics submission have distinct responsibilities. The cull stage produces a sorted collection of objects and render state for the draw stage, an intermediate representation that separates scene organization from GPU submission.
- **C3:** The optional multithreaded pipeline overlaps App, Cull, and Draw work from different frames. Its documentation explains why an imbalanced stage limits the benefit and why increased throughput does not mean reduced latency.

Read the [multithreaded rendering-pipeline guide](https://docs.panda3d.org/1.10/python/programming/rendering-process/multithreaded-render-pipeline). The guide labels this facility experimental; the selection concerns the architectural lesson, not an unconditional recommendation to enable it.

### [luanti-org/luanti](https://github.com/luanti-org/luanti)

**Language and role:** C++ networked voxel engine with Lua game/mod APIs, formerly named Minetest. It belongs here as reusable game infrastructure, rather than as a single voxel game.

- **C1:** The [client-interface header](https://raw.githubusercontent.com/luanti-org/luanti/master/src/server/clientiface.h) contains an explicit connection state machine spanning initial handshake, authentication, initialization, definition transfer, active play, elevated access, and disconnection. State-qualified client lookup and sending interfaces make protocol readiness an inspectable invariant.
- **C2:** The [Lua API reference](https://raw.githubusercontent.com/luanti-org/luanti/master/doc/lua_api.md) provides registries and callbacks for nodes, tools, entities, crafting, metadata, and world-update behavior. This separates game content and rules from networking and world infrastructure.

An experienced engineer can study the boundary between an extensible content system and a server that must handle clients at different stages of readiness. The state-machine evidence is not a claim of comprehensive security verification.

## 2D and browser game frameworks

### [libgdx/libgdx](https://github.com/libgdx/libgdx)

**Language and role:** Java cross-platform game-development framework. Its 2D drawing layer offers a compact route into GPU batching and API-level resource management.

- **C2:** `TextureRegion`, `Sprite`, and `SpriteBatch` separate texture selection, object-level drawing state, and submission. The abstractions support many 2D renderers without prescribing a complete game architecture.
- **C3:** SpriteBatch accumulates geometry and flushes when texture changes or buffer limits require it. Texture atlases reduce otherwise unnecessary flushes; counters expose draw-call and buffer-usage behavior. Capacity selection therefore has an understandable memory-versus-submission tradeoff.

The [SpriteBatch, TextureRegions, and Sprites guide](https://libgdx.com/wiki/graphics/2d/spritebatch-textureregions-and-sprites) is a substantive entry point covering batching, drawing-state constraints, and performance tuning. It helps connect an apparently simple immediate drawing API to the retained work actually sent to the GPU.

### [defold/defold](https://github.com/defold/defold)

**Language and role:** C++ runtime with Lua scripting and a Clojure-based editor in the same repository. Defold is source-available; do not infer unrestricted licensing from its public GitHub hosting.

- **C2:** Render scripts define initialization, per-frame work, and message handling. Material-tag predicates select groups for drawing, and render targets and materials are resources that scripts can compose into custom pipelines.
- **C3:** The renderer can reject objects outside a supplied view-projection frustum before GPU submission. The documented interaction between cameras, projection matrices, predicates, and culling makes this optimization inspectable rather than an opaque engine toggle.

Start with the [rendering manual](https://defold.com/manuals/render/), especially the default script and custom rendering examples. It is useful for studying how a relatively small scripting surface controls ordering, blend/depth state, and resource use in a native runtime.

### [hajimehoshi/ebiten](https://github.com/hajimehoshi/ebiten)

**Language and role:** Go 2D game engine, branded **Ebitengine**. Study how a small image-oriented API hides a more involved command stream and graphics-resource lifecycle.

- **C1:** Graphics-context restoration depends on drawing history. Modifying an image after it has become another image's source, or creating cyclic drawing dependencies, complicates reconstruction. This is a concrete example of recovery requirements affecting otherwise ordinary drawing semantics.
- **C3:** Compatible successive draws can be combined, and an automatic texture atlas reduces texture switching. Render targets, blend settings, filters, and source-image placement affect batching; reading a pixel can force queued GPU work to resolve.

The [performance tips](https://ebitengine.org/en/documents/performancetips.html) explain both command coalescing and restoration constraints. These mechanisms are stronger selection evidence than claims about a particular frame rate or a small public API alone.

### [phaserjs/phaser](https://github.com/phaserjs/phaser)

**Language and role:** JavaScript browser game framework with TypeScript-facing APIs. The scene system is a useful bounded subsystem for studying runtime lifecycle design.

- **C1:** Scenes distinguish loading, creation, running, pausing, sleeping, shutdown, and destruction. Shutdown permits restart; destruction does not. The guide documents real restart failure modes, including retained references to destroyed game objects and event subscriptions that outlive their objects.
- **C2:** Each scene owns systems such as cameras, display/update lists, and plugins, while selected services and caches are global. This supports concurrently running scenes and different plugin configurations without duplicating the entire runtime.

The [scene concepts and lifecycle guide](https://docs.phaser.io/phaser/concepts/scenes) is the entry point for both criteria. Study its cleanup examples alongside the lifecycle state transitions; together they reveal why scene management is more than a screen-switching convenience.

### [playcanvas/engine](https://github.com/playcanvas/engine)

**Language and role:** JavaScript browser 3D engine with TypeScript definitions. This repository contains the runtime engine; it should not be conflated with the hosted editor product.

- **C2:** The repository's entity/component application API provides reusable scene, camera, light, and rendering facilities. Clustered lighting then supplies a shared spatial representation through which different lights, shadows, and cookies reach material evaluation.
- **C3:** Visible lights are assigned to cells of a world-space grid on the CPU. Fragment shaders consult the corresponding light lists, while atlases consolidate shadow and cookie resources. Grid resolution, light capacity per cell, and atlas allocation expose practical quality, memory, and shader-work tradeoffs.

The [clustered-lighting implementation guide](https://developer.playcanvas.com/user-manual/graphics/lighting/clustered-lighting/) explains this CPU/GPU division and its configuration limits. It is a concrete rendering-architecture study, without relying on unsupported comparisons against other engines.

## Physical, robotics, and multibody simulation

### [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco)

**Language and role:** C/C++ physics simulator with a C API and Python interfaces, widely oriented toward articulated mechanisms and control. Study the stepping API and the distinction between model configuration, integration state, and derived workspace.

- **C1:** Integration semantics affect when control may be computed: splitting a step into two calls does not preserve every integrator's behavior. Quaternion positions and velocity coordinates also have different dimensional semantics. Solver warm-start information matters when comparing restored simulation trajectories.
- **C2:** Separate model and data structures, exposed pipeline stages, and callbacks allow controllers and analysis tools to reuse the same dynamics machinery.
- **C3:** Preallocated runtime storage and the choice between copying derived data or recomputing it expose the cost of managing many simulation states.

The [simulation programming chapter](https://mujoco.readthedocs.io/en/stable/programming/simulation.html) explains these contracts. It is especially useful for avoiding the mistaken assumption that copying positions and velocities always reproduces a complete simulator state.

### [RobotLocomotion/drake](https://github.com/RobotLocomotion/drake)

**Language and role:** C++ robotics toolbox with Python bindings. The selected monorepo subsystems are the **systems framework and simulation/event machinery**, which integrate with multibody modeling and control.

- **C2:** A `System` exposes inputs, outputs, state, and parameters; `Diagram` composes systems into larger models. This accommodates plants, controllers, sensors, and mathematical primitives through a common structure. Start with the [systems-framework overview](https://drake.mit.edu/doxygen_cxx/group__systems.html).
- **C1:** Hybrid simulation distinguishes publish events, discrete updates, and unrestricted state updates. Update calculations operate against appropriate pre-update state, and the framework specifies ordering between update categories, event triggers, and failure/termination reporting. The [event semantics documentation](https://drake.mit.edu/doxygen_cxx/group__events__description.html) makes simultaneous events and continuous/discrete interaction concrete.

This is a strong choice for studying the semantic obligations of a compositional simulator, beyond merely invoking a numerical integrator.

### [projectchrono/chrono](https://github.com/projectchrono/chrono)

**Language and role:** C++ multiphysics and multibody simulation framework, with additional language interfaces. Contact and collision handling provide a focused entry into a broad codebase.

- **C1:** Nonsmooth contact treats contact through constraints, whereas smooth contact uses penetration-dependent forces. These choices have different solver and timestep implications; stiff penalty forces can require smaller steps. Collision envelopes and margins introduce further accuracy and robustness tradeoffs.
- **C2:** Collision models, contact surfaces, shared materials, and broad/narrow-phase callbacks separate object representation from contact processing. Multiple collision implementations fit into this structure rather than defining unrelated application APIs.
- **C3:** The documentation connects collision tolerances and implementation choices to problem size, fallback costs, and multicore execution.

Read the [collision and contact manual](https://api.projectchrono.org/collisions.html). Its explanation of numerical formulations and configurable collision machinery offers more substance than the repository's list of application domains.

### [sofa-framework/sofa](https://github.com/sofa-framework/sofa)

**Language and role:** C++ framework for interactive physical simulation, with strong deformable-object and biomechanical modeling coverage. The multi-model mapping architecture is the main reason to study it.

- **C2:** Different representations can serve mechanics, collision detection, and visualization, linked through mappings rather than forced into a single mesh. The [framework architecture description](https://www.sofa-framework.org/about-sofa/) explains this composition and the role of plugins and scene organization.
- **C1:** Mappings propagate positions and velocities forward, but forces backward through the Jacobian transpose. Nonlinear mappings can contribute geometric stiffness, whose symmetry properties affect compatible solvers. The [mapping documentation](https://sofa-framework.github.io/doc/simulation-principles/multi-model-representation/mapping/) derives these relationships and discusses their implementation implications.

The study opportunity is preserving mechanical consistency across representations. This selection makes no claim about clinical validity or the suitability of a particular model for a medical application.

### [gazebosim/gz-sim](https://github.com/gazebosim/gz-sim)

**Language and role:** C++ robotics simulator. Focus on the **simulation orchestration and system-plugin layer** in this repository; the broader Gazebo ecosystem contains separate rendering, physics, transport, and sensor projects.

- **C2:** Runtime-loaded systems attach behavior to entities through an entity-component manager. The same interface accommodates controllers, physics-related behavior, and sensing without making each a separate simulator.
- **C1:** Configure, PreUpdate, Update, PostUpdate, and Reset have distinct responsibilities. PostUpdate receives read-only state, whereas earlier update phases permit mutation. The documentation also specifies what simulation time means at a step boundary and how pausing affects it.

The [system-plugin guide](https://gazebosim.org/api/sim/9/createsystemplugins.html) shows these contracts in code. Its feedback example—observe after a step, apply commands before a later step—is a useful entry point into timing-sensitive robotics software. This entry refers to Gazebo Sim, not the historical Gazebo Classic repository.

## Discrete-event, network, and computer-system simulation

### [simgrid/simgrid](https://github.com/simgrid/simgrid)

**Language and role:** C++ simulation framework for distributed applications and computing platforms. **Official GitHub mirror:** the repository identifies Framagit as the primary development location; the GitHub copy contains substantive source.

- **C1:** Actors interact with the simulation kernel through simcalls. A central scheduling process resolves interactions and advances simulated time when activities require it; ordering and reproducibility are explicit design concerns.
- **C2:** Actors, activities, and resources separate application behavior from modeled computation, storage, and communication. The [design-goals document](https://simgrid.org/doc/latest/Design_goals.html) explains this decomposition and the resource-sharing models underneath it.
- **C4:** The [release history](https://simgrid.org/doc/latest/Release_Notes.html) documents a multi-year transition: MSG deprecation in 2017, later API restructuring, and removal in 2023 of a fragile, insufficiently tested liveness-checking implementation. This is evidence of managing compatibility and complexity, not simply of an old repository.

The history also cautions against assuming every capability mentioned in older architectural descriptions survives unchanged.

### [omnetpp/omnetpp](https://github.com/omnetpp/omnetpp)

**Language and role:** C++ discrete-event simulation infrastructure with the NED topology language and development tools. Its public source is distributed under the **Academic Public License**, so commercial-use terms require separate consideration.

- **C1:** Event ordering is specified by arrival time, scheduling priority, and then scheduling order. Simulation time uses a fixed-point representation with configurable resolution, making precision/range choices and equal-time behavior explicit parts of the model.
- **C2:** C++ simple modules compose into compound modules; gates and channels carry messages, and NED describes the hierarchy and connections. The kernel is separated from user interfaces and simulation models.

The [simulation manual](https://doc.omnetpp.org/omnetpp/manual/), particularly its architecture and discrete-event simulation sections, is the primary entry point. It supports studying how topology composition, message ownership, event ordering, and introspection fit into a reusable simulation environment.

### [nsnam/ns-3-dev-git](https://github.com/nsnam/ns-3-dev-git)

**Language and role:** C++ network simulator with Python bindings. **Official read-only GitHub mirror** of the project's GitLab development repository; the mirrored source remains substantive.

- **C1:** Equal-time events execute in FIFO order using monotonically increasing identifiers. Event handlers consume zero simulated time, so modeled processing delays require later events. Integer time representation introduces an explicit precision-versus-range tradeoff.
- **C2:** Simulator implementations and event schedulers are separate abstractions, allowing different execution backends and event-queue structures under the common simulation API.
- **C3:** Cancellation retains a queued event marked as cancelled, while removal deletes it from the queue; these choices trade memory against processing cost. Scheduler data structures provide another workload-dependent performance choice.

The [events chapter](https://www.nsnam.org/docs/manual/html/events.html) explains these mechanics. This entry emphasizes the reusable simulation kernel, while recognizing that the repository's application focus is network modeling.

### [sstsimulator/sst-core](https://github.com/sstsimulator/sst-core)

**Language and role:** C++ parallel discrete-event core for the Structural Simulation Toolkit, used for computer-system modeling. This entry counts the core once, rather than separately listing its associated element-model collection.

- **C2:** Components exchange events over links; SubComponents and ComponentExtensions share a common base API. Clocks, statistics, serialization, and lifecycle hooks provide reusable services around independently implemented models. The [component introduction](https://sst-simulator.org/sst-docs/docs/core/component/introduction) explains these boundaries.
- **C1:** Initialization is a distinct communication protocol: handlers are not yet active, links are polled using untimed operations, and messages sent in one round arrive in the next. Rounds continue until no messages remain to deliver. Components must explicitly propagate initialization to their subcomponents, making ordering a model-author responsibility. See the [initialization contract](https://sst-simulator.org/sst-docs/docs/core/component/lifecycle/init).

The repository's MPI-based execution context makes this a useful complement to single-process event-loop frameworks, without implying a universal parallel speedup.

## Agent-based simulation

### [mesa/mesa](https://github.com/mesa/mesa)

**Language and role:** Python agent-based modeling framework. The former `projectmesa/mesa` URL redirects to this canonical repository. Study agent collections and lifecycle behavior, not only the visualization examples.

- **C2:** Agent sets support selection, grouping, aggregation, and activation patterns; spaces, data collection, and batch execution support different model families. The [framework overview](https://mesa.readthedocs.io/stable/overview.html) describes this shared modeling vocabulary.
- **C1:** The [AgentSet implementation](https://mesa.readthedocs.io/stable/_modules/mesa/agentset.html) makes lifetime and ordering concerns explicit: weak-reference storage, checks for expired references, and shuffled activation using a supplied or model-derived random generator. Its warning about missing RNG context connects an API default to reproducibility risk.

The repository distinguishes stable Mesa 3 from Mesa 4 development. Documentation aliases can move, so match these implementation ideas to the intended release before relying on exact signatures or migration behavior. The evidence does not establish that all removal and activation patterns have identical semantics.

### [JuliaDynamics/Agents.jl](https://github.com/JuliaDynamics/Agents.jl)

**Language and role:** Julia agent-based modeling framework with discrete-step and continuous-time event-queue models. Particularly useful for examining how one interface can support multiple activation semantics.

- **C2:** Abstract model interfaces unify agents, spaces, scheduling, and random-number generation. Standard and event-queue models share a vocabulary while retaining different execution machinery.
- **C1:** Agent deletion affects iteration correctness; manual scheduling must account for agents that no longer exist. In event-queue models, event propensities, action selection, and timing are explicit, and an action that does nothing can still consume simulated time.
- **C3:** Container choice reflects workload: vectors suit cases without removal, dictionaries support removal, and specialized layouts offer other storage tradeoffs.

The [API and model-construction documentation](https://juliadynamics.github.io/Agents.jl/stable/api/) discusses these decisions. Shared interfaces do not mean identical feature coverage—for example, the documentation identifies limitations around checkpointing event-queue models.

### [FLAMEGPU/FLAMEGPU2](https://github.com/FLAMEGPU/FLAMEGPU2)

**Language and role:** CUDA C++ agent-based simulation framework with a Python interface. This adds a GPU-oriented execution model to the CPU-focused agent frameworks above.

- **C1:** Execution layers enforce constraints on agent-function combinations. Conflicting input/output states and producer/consumer use of a message type cannot simply be placed together; host functions and submodel execution have additional restrictions. These rules expose hazards that would otherwise become concurrency bugs.
- **C3:** Layers run sequentially, while compatible functions within a layer may execute concurrently. The model expresses enough dependency structure for GPU parallelism while preserving understandable synchronization boundaries.

The [execution-layer guide](https://docs.flamegpu.com/guide/defining-execution-order/layers.html) documents the rules and examples. It is a useful study of turning a model description into constrained parallel work. Hardware applicability is narrower than that of a generic CPU framework: this implementation is oriented toward NVIDIA CUDA.

## Coverage, search process, and limitations

Discovery used repeated live web searches, followed by opening canonical GitHub pages and substantive official documentation or source. Search formulations covered more than six distinct directions: scene-tree and ECS engine architecture; C#/Java 3D engines; Rust handles and storage; Go/Lua/Java 2D rendering; browser/WebGL engines; robotics and multibody contact solvers; deformable multi-model simulation; network and distributed-system discrete-event kernels; MPI computer-system simulation; and Python/Julia/CUDA agent-based modeling. Follow-up searches targeted pass graphs, threading contracts, scene lifecycles, event ordering, and release/deprecation history. A final broader pass through voxel engines, Haxe/Lua engines, and smaller simulation frameworks added Luanti; further candidates mostly repeated covered architectures or lacked comparably strong primary evidence within this review.

The selection spans both familiar projects and narrower communities, including Fyrox, SOFA, SST, Agents.jl, and FLAME GPU. It deliberately omits individual games, tutorial engines, generated wrappers, awesome-lists, and standalone ECS, renderer, or collision libraries whose larger framework role was not established. It does not count earlier names, mirrors, related model collections, or engine subsystems as additional repositories. Exclusion is not a finding of poor quality or abandonment.

All 25 retained repositories have a verified canonical GitHub page and at least one additional inspected primary source containing implementation or architectural detail. SimGrid and ns-3 are explicitly identified as official mirrors. Defold and OMNeT++ are not presented as having interchangeable licensing with permissively licensed projects. No blanket claim of active maintenance is made; C4 is assigned only where the reviewed history supports evolution and complexity management.

This was read-only research: no candidate repository was cloned, built, benchmarked, or subjected to a test suite. Many documentation links follow `stable`, `latest`, or a development branch; versioned links are used where inspected, and mutable links may change after the research date. Documented architecture is factual evidence; the judgment that it provides a worthwhile engineering study is an inference. Neither published design intent nor this selection establishes that every implementation path satisfies its intended invariants.
