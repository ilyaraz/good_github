# Rigid-body dynamics and collision detection engines

Research date: **2026-10-09**.

This selection covers 24 GitHub repositories implementing rigid-body simulation, articulated-body dynamics, or reusable collision/proximity algorithms. It spans 2D and 3D, interactive games and scientific robotics, CPU and GPU execution, and C, C++, C#, Rust, Java, JavaScript/TypeScript, Julia, and Python. A collision library need not integrate equations of motion to qualify; an articulated dynamics library need not implement a general collision engine. Those boundaries are identified below. Large repositories are counted once, with the relevant subsystem specified.

Criteria legend:

- **C1 — Correctness:** difficult numerical, geometric, state-lifetime, concurrency, or failure-mode requirements.
- **C2 — Abstractions:** substantial reusable interfaces and representations supporting different applications.
- **C3 — Performance and structure:** concrete performance mechanisms within an understandable architecture.
- **C4 — Evolution:** documented evolution over years together with compatibility, testing, or complexity management.

Criteria assignments and suggested study topics are engineering judgments grounded in the linked material. They are not assurances that every component is exemplary. Repository identities were checked through GitHub pages or the GitHub API; implementation and documentation entry points were separately read. Links generally follow development branches, so details can change. No candidate code was built or executed, and no comparative performance measurements were reproduced.

## General 3D and dimension-generic engines

### 1. [jrouwe/JoltPhysics](https://github.com/jrouwe/JoltPhysics)

**C++ — multithreaded rigid-body and collision engine.** Particularly useful for studying how a physics library participates in a larger concurrent game system, including scene streaming and queries outside the simulation step.

- **C1:** The architecture explains sequence-numbered body IDs, failed locks after body removal, a hashed mutex array, and ordered multi-body locking to prevent deadlocks. It also specifies restrictions on callbacks and access during updates. These are concrete lifetime and concurrency contracts. [Architecture, especially multithreaded access](https://github.com/jrouwe/JoltPhysics/blob/master/Docs/Architecture.md).
- **C3:** Object layers map into broad-phase trees so expensive queries can avoid unrelated classes of bodies. The same document explains the cost of additional broad-phase layers and provides a workload-based example. This connects a public filtering abstraction directly to execution cost. [Collision filtering and broad-phase architecture](https://github.com/jrouwe/JoltPhysics/blob/master/Docs/Architecture.md).

### 2. [NVIDIA-Omniverse/PhysX](https://github.com/NVIDIA-Omniverse/PhysX)

**C++/CUDA — physics SDK; focus on the `physx` rigid-body and constraint-solver subsystem.** Study how a large SDK exposes simulation controls while documenting their numerical consequences.

- **C1:** Its rigid-body guide distinguishes position and velocity iterations, explaining why reported velocity can differ from the displacement divided by timestep. It also documents friction-patch limits and behavior when those limits are exceeded. [Rigid-body dynamics guide](https://nvidia-omniverse.github.io/PhysX/physx/5.4.1/docs/RigidBodyDynamics.html).
- **C2/C3:** PGS and TGS solvers share the scene abstraction but enforce constraints differently; solver selection is an immutable per-scene property, while per-body iteration counts interact with solver islands. This is useful evidence of configurable numerical policy and explicit accuracy/cost tradeoffs. The cited guide is **versioned 5.4.1 documentation**, not a claim about the latest release defaults. [Solver discussion](https://nvidia-omniverse.github.io/PhysX/physx/5.4.1/docs/RigidBodyDynamics.html#constraint-solver).

### 3. [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3)

**C++ — collision and multiphysics SDK; focus on `BulletDynamics` and `BulletCollision`.** The classic CPU rigid-body loop is an accessible entry into a much larger repository; Python bindings are not counted separately.

- **C1:** `btDiscreteDynamicsWorld` coordinates predictive contacts, discrete collision detection, constraint solving, transform integration, and activation updates. The ordering exposes dependencies between contact generation and physical state changes. [Dynamics-world implementation](https://github.com/bulletphysics/bullet3/blob/master/src/BulletDynamics/Dynamics/btDiscreteDynamicsWorld.cpp).
- **C3:** The same implementation bounds accumulated simulation substeps to prevent a frame-time backlog from growing without limit, partitions work into simulation islands, and includes stage profiling. Study the deliberate tradeoff between catching up simulated time and keeping an interactive application responsive. [Stepping and island orchestration](https://github.com/bulletphysics/bullet3/blob/master/src/BulletDynamics/Dynamics/btDiscreteDynamicsWorld.cpp).

### 4. [DanielChappuis/reactphysics3d](https://github.com/DanielChappuis/reactphysics3d)

**C++ — compact standalone 3D engine.** A useful intermediate-scale codebase for studying object ownership, collision shapes, and integration contracts without a surrounding game engine.

- **C1/C2:** `PhysicsCommon` centralizes allocation and acts as a factory for worlds and shapes. The manual specifies allocator alignment, engine-owned object destruction, and how collider changes require recomputation of mass, center of mass, and inertia. It distinguishes collision-only queries from full simulation. [User manual](https://reactphysics3d.com/documentation/).
- **C4:** The changelog spans 2013–2024 and documents more than new features: unit-test introduction, broad-phase rewrites, the 2020 world/API consolidation, and the 2024 change from shared mesh input data to copied data with explicit validation errors. These are concrete examples of compatibility and ownership complexity management. [Changelog](https://github.com/DanielChappuis/reactphysics3d/blob/master/CHANGELOG.md).

### 5. [JulioJerez/newton-dynamics](https://github.com/JulioJerez/newton-dynamics)

**C++ — Newton Dynamics; focus on the `newton-4.00` engine.** This is the current official repository identified by the [discontinued MADEAPPS repository](https://github.com/MADEAPPS/newton-dynamics), which is not a separate selection. It is distinct from Warp-based Newton below.

- **C1:** The dynamics update constructs Jacobians, iterates joint forces with bounds derived from normal forces and friction coefficients, accumulates residuals, and determines sleeping state through connected constraints. This provides a concrete route into constrained dynamics and coupled sleep decisions. [Dynamics update implementation](https://github.com/JulioJerez/newton-dynamics/blob/dliw/newton-dynamics/newton-4.00/sdk/dNewton/ndDynamicsUpdate.cpp).
- **C3:** The implementation separates island construction, unconstrained integration, force calculation, integration, and feedback. It uses packed vector operations and `ParallelExecute` batches rather than hiding the entire solve behind one opaque function. The linked branch name, `dliw/newton-dynamics`, was verified on the repository page.

### 6. [dimforge/rapier](https://github.com/dimforge/rapier)

**Rust — shared 2D/3D simulation engine with multiple scalar configurations.** Study separation of persistent world state from reusable timestep workspaces, alongside a shared implementation across dimensions.

- **C2:** The repository architecture describes how crate configurations select dimension and scalar precision while sharing engine sources, avoiding independent implementations for each combination. [Repository architecture](https://github.com/dimforge/rapier/blob/master/ARCHITECTURE.md).
- **C1/C3:** `PhysicsPipeline` owns reusable working buffers and coordinates broad phase, narrow phase, joints, islands, and solving. The inspected code explicitly joins deferred BVH optimization before the tree is reused and tracks whether a newly created pipeline has initialized its memoized joint selection. These are instructive examples of performance optimizations creating correctness obligations. [Pipeline implementation](https://github.com/dimforge/rapier/blob/master/src/pipeline/physics_pipeline/mod.rs).

### 7. [avianphysics/avian](https://github.com/avianphysics/avian)

**Rust — ECS-based 2D/3D physics for Bevy.** A substantive engine implementation, not merely a wrapper around another complete simulator. Study physics scheduling inside an entity-component system.

- **C2:** The solver is assembled from plugins with separate responsibilities for solver bodies, integration, constraints, CCD, islands, and sleeping. This creates useful replacement and extension boundaries. [Solver plugin group](https://github.com/avianphysics/avian/blob/main/src/dynamics/solver/mod.rs).
- **C1/C3:** The solver documentation lays out substeps, warm starting, biased constraint solving, velocity relaxation, restitution, and impulse persistence. It also explains why awake bodies receive a separate solver representation with better locality. The inspected source retains optional XPBD joint handling, so the implementation should not be summarized as one uniform solver for every constraint. [Solver implementation and schedule](https://github.com/avianphysics/avian/blob/main/src/dynamics/solver/plugin.rs).

## Managed-runtime engines

### 8. [bepu/bepuphysics2](https://github.com/bepu/bepuphysics2)

**C# — 3D rigid-body engine, a rewrite of BEPUphysics v1.** Especially valuable for studying performance-oriented design in a managed language and the obligations it places on callers.

- **C2/C3:** Body properties occupy separate buffers; active and sleeping bodies use different sets; constraints use an array-of-structures-of-arrays layout. Generic struct callbacks allow specialization without frequent virtual dispatch, and application-provided buffer pools make allocation explicit. [Getting started and internal representations](https://docs.bepuphysics.com/GettingStarted.html).
- **C1:** The CCD guide derives speculative contacts, explains false “ghost” collisions, and shows how sweep testing, speculative margins, and convergence tolerances interact. It candidly documents cases where secondary collisions can be missed. [Continuous collision detection](https://docs.bepuphysics.com/ContinuousCollisionDetection.html).

### 9. [notgiven688/jitterphysics2](https://github.com/notgiven688/jitterphysics2)

**C# — standalone 3D engine with configurable precision.** Study a smaller managed-runtime design with explicitly documented contact identity and broad-phase extension points.

- **C1/C2:** Arbiters belong to shape pairs, not body pairs. Canonically ordered IDs, handle lifetime restrictions, cached contact slots, and custom contact registration make the invariants visible. Contact replacement preserves accumulated impulses when appropriate and uses geometric spread when the cache is full. [Arbiter documentation](https://github.com/notgiven688/jitterphysics2/blob/main/docfx/docs/documentation/arbiters.md).
- **C3:** The dynamic tree uses velocity-expanded bounds to reduce update frequency and separates broad-phase candidates from exact ray, sweep, and nearest queries. Custom proxies must integrate with collision filtering. [Dynamic-tree documentation](https://github.com/notgiven688/jitterphysics2/blob/main/docfx/docs/documentation/dynamictree.md).

### 10. [dyn4j/dyn4j](https://github.com/dyn4j/dyn4j)

**Java — 2D collision and rigid-body dynamics library.** Useful for studying reusable geometry and collision layers behind an object-oriented simulation API.

- **C2:** Geometry, broad phase, narrow phase, manifold generation, and constrained dynamics have distinct responsibilities. The advanced guide explains that collision detection can be used independently, and that convex decomposition and hull utilities also serve applications directly. [Package architecture](https://dyn4j.org/pages/advanced.html#package-architecture).
- **C1:** The same guide addresses unit-dependent settings, floating-point comparisons, convexity requirements, continuous collision detection, and contact-constraint updates. These are concrete concerns when moving from geometric predicates to a stable timestep pipeline. Follow the guide's pipeline sections to study where application listeners interact with solver state. [Advanced usage and pipeline](https://dyn4j.org/pages/advanced.html).

## 2D native and browser engines

### 11. [erincatto/box2d](https://github.com/erincatto/box2d)

**C17 — current native 2D rigid-body engine.** Study how an established physics model is exposed through opaque handles and arranged for multithreading and SIMD.

- **C1:** The simulation guide defines handle validity and dependent-object destruction, then explains tunneling, time-of-impact sweeps, and the limits of bullet-body CCD. These are useful examples of precise API and numerical contracts. [Simulation guide](https://box2d.org/documentation/md_simulation.html).
- **C2/C3:** Opaque IDs decouple user references from internal storage, enabling data-oriented layout. Task callbacks connect the world to an application scheduler, while substep counts expose accuracy/cost control. The current repository is C; older C++ Box2D implementations should not be confused with this architecture. [IDs, world configuration, and stepping](https://box2d.org/documentation/md_simulation.html).

### 12. [slembcke/Chipmunk2D](https://github.com/slembcke/Chipmunk2D)

**C — lightweight 2D engine; official secondary GitHub hosting during a move to Codeberg.** The repository README states that the author is supporting both sites for now and intends eventually to leave GitHub. It is retained because substantive source and an explicit dual-hosting statement remain, not as an assertion that GitHub is the long-term upstream.

- **C1:** `cpSpaceStep` coordinates space locking, contact-graph rebuilding, sleeping components, arbiter retirement, and callback execution. Cached impulses are rescaled using the ratio of current and previous timesteps. [Simulation-step source](https://github.com/slembcke/Chipmunk2D/blob/master/src/cpSpaceStep.c).
- **C2/C3:** Position/velocity callbacks, spatial-index operations, and constraint method tables separate policy from the loop. Contact persistence and sleeping reduce repeated work while remaining visible in a comparatively compact implementation. The same source is the recommended entry point.

### 13. [liabru/matter-js](https://github.com/liabru/matter-js)

**JavaScript — browser-oriented 2D rigid-body engine.** Study simulation lifecycle and event semantics in a readable, renderer-independent stepping core.

- **C1/C2:** `Engine.update` coordinates composite membership changes, sleeping and wake-up, collision-pair lifetimes, two constraint passes, separate position/velocity resolution, and start/active/end collision events. The stage boundaries show how reusable modules cooperate without folding everything into rendering. [Engine implementation](https://github.com/liabru/matter-js/blob/master/src/core/Engine.js).
- **C4:** The changelog records development from 2014 through 2024, including behavior and memory comparison tests in 2021, and a fixed-timestep runner plus sleeping-pair event fixes in 2024. This is substantive regression and complexity-management evidence; it is not a claim of a newer release. [Changelog](https://github.com/liabru/matter-js/blob/master/CHANGELOG.md).

### 14. [piqnt/planck.js](https://github.com/piqnt/planck.js)

**TypeScript/JavaScript — independent-language rewrite of Box2D for the web.** Retained alongside native Box2D because it contains the algorithms themselves and a web-language API, rather than generated bindings. Its algorithmic ancestry is explicit.

- **C1:** The time-of-impact implementation alternates secant steps with bisection, preserves a root bracket, handles initial overlap, and returns explicit failure states when iteration limits are reached. It is a good focused study of robust iterative geometry. [Time-of-impact implementation](https://github.com/piqnt/planck.js/blob/master/src/collision/TimeOfImpact.ts).
- **C3:** The same code bounds several nested search loops, records iteration/timing statistics, and recycles a separation-function workspace. These mechanisms expose the tension between numerical convergence and bounded work in a browser simulation.

## Articulated systems, scientific simulation, and differentiable physics

### 15. [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco)

**C/C++, with Python and accelerator-related components — articulated-body simulator.** Focus on the core engine's contact model and computation pipeline; bundled interfaces and MJX are not separate entries.

- **C1:** The computation chapter explains its convex soft-contact model, including how dropping strict complementarity changes physical semantics. It distinguishes pyramidal and elliptic friction cones and describes the corresponding optimization problems. [Computation and constraint solver](https://mujoco.readthedocs.io/en/stable/computation/index.html).
- **C2/C3:** Recursive Newton–Euler and composite rigid-body calculations feed a structured pipeline. The inertia representation follows kinematic-tree sparsity, and factorization/back-substitution preserve that structure. Subtree-centered frames address floating-point accuracy. Study the connections among representation, solver mathematics, and execution cost in the same chapter.

### 16. [dartsim/dart](https://github.com/dartsim/dart)

**C++ with Python bindings — articulated-body dynamics and contact simulation.** Focus on dynamics, constraints, and interchangeable collision backends. It is more than an adapter around FCL or Bullet: those are collision backends within its dynamics system.

- **C2:** The documented DART 6.20 architecture preserves detector/group/object interfaces and factory keys across native, FCL, Bullet, and ODE implementations. This is a useful case study in backend substitution with downstream consumers. [Collision-backend architecture](https://github.com/dartsim/dart/blob/main/docs/design/dart6_collision_backends.md).
- **C1:** That document defines correctness through contact semantics, finite state, deterministic results, and scene tolerances. It identifies subclassing and contact-data contracts relied upon by Gazebo integrations and requires direct tests for contact caps and query behavior. These are explicit compatibility and correctness obligations, not evidence that every proposed future backend migration has already happened.

### 17. [projectchrono/chrono](https://github.com/projectchrono/chrono)

**C++ — multibody/multiphysics framework; focus on core rigid bodies, contacts, and collision systems.** A good study target for physical-model choices that cannot be reduced to a single “accuracy” setting.

- **C1:** Non-smooth contacts are modeled as constraints, while smooth contacts use penetration-dependent penalty forces. The manual explains the implications for stiffness, timestep selection, and compatible solvers. [Collision and contact-formulation manual](https://github.com/projectchrono/chrono/blob/main/doxygen/documentation/manuals/chrono/collisions.md).
- **C2/C3:** Collision models compose geometry and material objects, with documented sharing behavior. A system can select a customized Bullet backend or Chrono's multicore collision implementation. The manual discusses convex decomposition and simplified collision geometry as practical cost controls. These are distinct extension and optimization mechanisms within the same contact model hierarchy.

### 18. [JuliaRobotics/RigidBodyDynamics.jl](https://github.com/JuliaRobotics/RigidBodyDynamics.jl)

**Julia — articulated rigid-body dynamics algorithms, not a general-purpose scene collision engine.** Especially valuable for comparing generic numerical code with specialized fast paths.

- **C1:** `dynamics_solve!` derives the coupled acceleration/constraint system and explains why the reduced constraint matrix may be only positive semidefinite. Its BLAS path consequently uses a rank-revealing solve rather than assuming positive definiteness throughout. [Mechanism algorithms](https://github.com/JuliaRobotics/RigidBodyDynamics.jl/blob/master/src/mechanism_algorithms.jl).
- **C2/C3:** The API supports suitable generic scalar types, including symbolic and automatic-differentiation values, while specialized floating-point methods reuse workspaces and BLAS/LAPACK operations. The inspected implementation exposes both paths, making the abstraction/performance tradeoff unusually concrete. Its limited contact facilities should not be mistaken for full arbitrary-mesh collision coverage.

### 19. [dojo-sim/Dojo.jl](https://github.com/dojo-sim/Dojo.jl)

**Julia — differentiable rigid-body simulator for robotics; historical/research selection.** The README explicitly says active development stopped in April 2023 while contributions remain welcome. It is not GitHub-archived, but that does not imply active maintenance.

- **C1:** Each timestep solves a nonlinear complementarity problem with cone and quaternion variables. The solver documentation defines separate constraint and complementarity residuals and acceptance tolerances. [Interior-point algorithm](https://github.com/dojo-sim/Dojo.jl/blob/main/docs/src/background_solver/interior_point.md).
- **C3:** A custom primal-dual predictor-corrector method, continuation toward hard contact, and bounded backtracking address convergence and ill-conditioning explicitly. Study this implementation family to contrast optimization-based contact with the iterative impulse methods elsewhere in the report. No published speedup or typical iteration count is treated here as an independently verified benchmark.

### 20. [newton-physics/newton](https://github.com/newton-physics/newton)

**Python/Warp — GPU-oriented physics engine for robotics.** This is separate from Newton Dynamics. Focus on rigid-body solver interfaces and collision processing; inclusion does not imply that every solver supports the same physics or derivatives.

- **C2:** `ModelBuilder`, `Model`, `State`, `Control`, and `Contacts` have separate roles. The loop explicitly computes contacts and passes them with state/control into a selected solver. This supports studying multiple numerical backends behind shared simulation data. [Architecture overview](https://github.com/newton-physics/newton/blob/main/docs/guide/overview.rst).
- **C1/C3:** Collision documentation distinguishes convex support-map algorithms, live mesh-BVH queries, and precomputed SDF paths. It explains contact reduction, filtering, and selectable all-pairs, sweep-and-prune, or explicit-pair broad phases. These choices expose accuracy, geometry, and workload constraints rather than merely promising GPU acceleration. [Collision pipeline](https://github.com/newton-physics/newton/blob/main/docs/concepts/collisions.rst).

## Standalone collision and proximity libraries

### 21. [dimforge/parry](https://github.com/dimforge/parry)

**Rust — reusable 2D/3D geometric queries and collision detection.** It is a separate library from Rapier, with its own shape/query abstraction; it does not advance a rigid-body world.

- **C1/C2:** `QueryDispatcher` defines relative-coordinate conventions, `Send + Sync` requirements, and explicit unsupported-query results. Dispatchers can be chained so specialized shape-pair handling falls back to standard algorithms. [Query-dispatcher source and documentation](https://github.com/dimforge/parry/blob/master/src/query/query_dispatcher.rs).
- **C3:** Persistent query dispatch carries contact-manifold workspaces and exploits temporal coherence, rather than treating every query as stateless. The separate crate configurations share geometric implementation across dimensions and precisions. [Repository architecture](https://github.com/dimforge/parry/blob/master/ARCHITECTURE.md). Study the dispatcher first; the short architecture file supplies the packaging context.

### 22. [flexible-collision-library/fcl](https://github.com/flexible-collision-library/fcl)

**C++ — collision, distance, tolerance, and continuous proximity queries.** Useful for studying reusable collision services independent of a game timestep or dynamics solver.

- **C2:** The library separates collision geometry and posed objects from broad-phase managers and query callbacks. The dynamic-tree manager offers object-versus-world, self-collision, and distance operations, with specialized octree traversal where enabled. [Dynamic AABB-tree manager](https://github.com/flexible-collision-library/fcl/blob/master/include/fcl/broadphase/broadphase_dynamic_AABB_tree-inl.h).
- **C3:** The implementation distinguishes whole-tree refitting from single-object and batched incremental updates, then performs setup/rebalancing before queries. Collision and distance share hierarchy traversal infrastructure while carrying different callback and pruning state. This is a concrete study in scaling proximity queries without coupling them to physical response.

### 23. [coal-library/coal](https://github.com/coal-library/coal)

**C++ with Python bindings — proximity library formerly named HPP-FCL.** Counted separately from FCL because the project documents substantial rewriting after its 2015 fork, dedicated GJK/EPA implementations, and the 2024 rename. This is substantive separate evolution, not an unchanged mirror.

- **C1:** GJK exposes distinct convergence, early-separation, collision, and failure states. Its interface warns that early distance termination does not guarantee valid closest points; tolerances and iteration limits are explicit. [GJK implementation interface](https://github.com/coal-library/coal/blob/devel/include/coal/narrowphase/gjk.h).
- **C3:** The simplex reuses fixed storage for four vertices, and support hints and configurable early stopping make coherence and query intent visible. Study this alongside FCL's broader management layer. The project's numerical performance comparisons were not reproduced and are not used as selection evidence.

### 24. [danfis/libccd](https://github.com/danfis/libccd)

**C — convex-pair intersection and penetration algorithms, not a complete dynamics engine.** A focused library for studying GJK/EPA and MPR without scene-management machinery.

- **C1:** The GJK/EPA implementation separates simplex handling, conversion to polytopes of different ranks, and polytope expansion. The public API distinguishes non-intersection from allocation failure and exposes convergence tolerances. [GJK/EPA source](https://github.com/danfis/libccd/blob/master/src/ccd.c).
- **C2:** Caller-supplied support-map and center callbacks accept opaque objects, allowing application geometry to remain outside the library's data model. Intersection, separation, and penetration operations reuse this small contract. [Public interface](https://github.com/danfis/libccd/blob/master/src/ccd/ccd.h). The repository name should not be taken to mean that this library alone provides a complete swept-time collision pipeline.

## Search coverage, exclusions, and limitations

Discovery used more than six distinct live query families: mainstream 3D engines and architecture; standalone FCL/libccd proximity libraries; Rust dimension-generic and ECS engines; native 2D and Box2D-derived engines; C# and Java implementations; robotics/multibody contact solvers; Julia differentiable simulation; browser engines; GPU/Warp simulation; and less common Go, Zig, Fortran, and functional-language implementations. Later language-oriented searches mostly returned wrappers, small educational engines, or unrelated projects, producing diminishing returns. The selection therefore emphasizes substantive implementation diversity rather than a language quota.

Important scope decisions:

- **ODE:** The [official project wiki](https://ode.org/wiki/index.php/Main_Page) points to Bitbucket. An authoritative substantive GitHub mirror was not established during this search, so third-party GitHub copies were not promoted into the list.
- **Superseded Rust engines:** [nphysics](https://github.com/dimforge/nphysics) explicitly describes passive maintenance and replacement by Rapier. It was investigated but omitted to prioritize the successor and avoid redundant family coverage.
- **Ports, wrappers, and forks:** Planck is retained as an algorithm implementation in another language; Coal is retained for documented independent implementation work. Generated bindings and routine integrations around Bullet, Jolt, Rapier, and Box2D are excluded. Browser forks such as p2-es were discovered but did not add enough independent architectural coverage for this selection.
- **Hosting and status:** Chipmunk's official secondary GitHub copy and Dojo's development cessation are flagged in their entries. The discontinued MADEAPPS Newton repository supplies provenance only; the current official repository is the selection. An unarchived flag, recent push, or repository age was not treated as sufficient evidence of maintenance or C4.
- **Breadth limits:** This is not an exhaustive catalog of every robotics stack or game-engine monorepo containing physics. General renderers, asset-only projects, tutorials, and small learning exercises were excluded. RigidBodyDynamics.jl is intentionally included for dynamics algorithms, while FCL, Coal, Parry, and libccd are intentionally included for collision services without full simulation.

All retained repositories have at least two evidence-grounded criteria and a separately inspected implementation or design source beyond their repository README. GitHub API rate limiting interrupted further metadata requests late in the search; repository pages and direct primary-source reads completed the remaining checks. Claims are limited to the inspected material, with version-specific documentation identified where relevant. No ranking by stars, unsupported throughput comparison, or blanket maintenance recommendation is intended.
