# Three-dimensional content creation and animation systems

Research date: **2026-10-09**.

This selection covers 24 GitHub repositories for modeling, sculpting, voxel editing, procedural scene construction, character authoring, and animation. It also includes libraries that implement substantial parts of those workflows: scene composition, animated geometry interchange, material authoring, subdivision, sparse volumes, and skeletal animation processing. Those infrastructure projects are identified as libraries rather than presented as complete artist applications. General game engines, CAD-only systems, renderers without a substantial authoring role, and 2D-only animation tools are outside this report's scope.

The criteria below are evidence-based selection judgments, not certification that every component is correct, secure, or exemplary. Descriptions of mechanisms come from the linked primary sources; explanations of their engineering value are grounded inference. Repository pages were opened to verify canonical URLs, and every entry has an additional inspected implementation or architecture source. No candidate code was executed.

**Criteria legend**

- **C1 — Difficult correctness:** topology and ownership invariants, concurrency, numerical semantics, malformed input, or consequential failure modes.
- **C2 — Reusable abstractions:** substantial models, interfaces, or frameworks supporting multiple operations and workflows.
- **C3 — Performance with structure:** concrete memory, latency, throughput, or parallelism constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** multi-year development evidenced together with compatibility work, testing, or deliberate complexity management.

## Complete modeling applications

### 1. [blender/blender](https://github.com/blender/blender)

**Language/role:** C/C++ and Python; integrated modeling, rigging, animation, simulation, and rendering suite. **Official GitHub mirror:** primary development is on Blender's own forge, as the repository explicitly states.

Study how a large authoring application evaluates interdependent scene operations while preserving responsive editing. The particularly useful subsystem here is the dependency graph, rather than the entire monorepo at once.

- **C1:** The [dependency-graph evaluator](https://github.com/blender/blender/blob/main/source/blender/depsgraph/intern/eval/deg_eval.cc) separates copy-on-evaluation, visibility, threaded evaluation, and a single-threaded fallback. Its comments explain dependency-cycle handling and races caused by simulation modifiers that directly update other objects during subframes.
- **C3:** The same implementation tracks pending parents, schedules child tasks, and skips operations that do not need updating. The stage boundaries make the concurrency exceptions and incremental-work strategy inspectable, including cases where parallel execution is deliberately disabled.

### 2. [dgud/wings](https://github.com/dgud/wings)

**Language/role:** Erlang, with native support code; subdivision and polygon modeling application.

Wings3D offers an unusual functional-language perspective on an interactive geometry editor. Study its central winged-edge representation and the relationship between topology-changing commands and derived lookup tables.

- **C1:** [wings_we.erl](https://github.com/dgud/wings/blob/master/src/wings_we.erl) explicitly distinguishes a full rebuild, which removes unused vertices and updates identifier bounds, from a faster rebuild that omits those operations. Face consistency, hole visibility, mirror validation, and identifier allocation expose the invariants editing commands must preserve.
- **C2:** The same module supplies a common mesh-operation vocabulary—construction, merging, separation, renumbering, transforms, normals, and geometric measurements—over one representation. This is a substantive shared abstraction for many modeling operations, rather than a collection of independent shape generators.

### 3. [ArtOfIllusion/ArtOfIllusion](https://github.com/ArtOfIllusion/ArtOfIllusion)

**Language/role:** Java; desktop modeling, animation, and rendering suite with plugins and scripting.

Study a comparatively approachable object-oriented authoring system, especially how animation tracks relate to scene objects and skeletal hierarchies.

- **C1:** [Skeleton.java](https://github.com/ArtOfIllusion/ArtOfIllusion/blob/master/ArtOfIllusion/src/artofillusion/animation/Skeleton.java) reconstructs parent/child references when duplicating skeletons and recursively deletes dependent joints. These are concrete graph-identity and ownership problems that become visible during copy, delete, and undo workflows.
- **C2:** [Track.java](https://github.com/ArtOfIllusion/ArtOfIllusion/blob/master/ArtOfIllusion/src/artofillusion/animation/Track.java) unifies procedural and keyframe-driven changes through time application, editing, serialization, subtracks, dependencies, and reference remapping when objects move between scenes. The abstraction connects the timeline, scene evaluation, and persistence layers.

### 4. [K-3D/k3d](https://github.com/K-3D/k3d)

**Language/role:** C++; procedural 3D modeling, animation, and rendering application. **Historical selection:** the inspected [default-branch commit history](https://github.com/K-3D/k3d/commits/master) ends in March 2019; this is not presented as currently maintained software.

Study an older application architecture that makes property dependencies and undoable graph edits explicit.

- **C1:** [pipeline.cpp](https://github.com/K-3D/k3d/blob/master/k3dsdk/pipeline.cpp) records old and new dependency states, disconnects signal handlers when links change, cleans up deleted properties, and uses loop-safe notification slots. Undo must restore both graph relationships and their notification behavior.
- **C2:** [pipeline.h](https://github.com/K-3D/k3d/blob/master/k3dsdk/pipeline.h) exposes arbitrary connections between properties through an `ipipeline` implementation with optional state recording. The mechanism can serve many procedural nodes without hard-coding individual modeling operations.

### 5. [huxingyi/dust3d](https://github.com/huxingyi/dust3d)

**Language/role:** C++/Qt; modeling application with rigging, procedural animation, UV generation, and asset export.

Study the conversion of editable parts and components into a generated mesh while retaining the information needed for appearance and deformation.

- **C1:** [mesh_generator.cc](https://github.com/huxingyi/dust3d/blob/master/dust3d/mesh/mesh_generator.cc) reconstructs quads using directed triangle-edge relationships and tracks which faces have already been combined. Geometry generation must also preserve correspondence with the editable model, not merely output triangles.
- **C3:** [mesh_generator.h](https://github.com/huxingyi/dust3d/blob/master/dust3d/mesh/mesh_generator.h) separates generated parts, components, previews, and cache context, with dirty component/part sets and cached mesh combinations. Its UV, node-weight, and vertex-attribute maps show why incremental generation requires richer cache state than a single mesh buffer.

## Surface, low-poly, and voxel editors

### 6. [JannisX11/blockbench](https://github.com/JannisX11/blockbench)

**Language/role:** JavaScript/TypeScript; browser and Electron model, texture, and animation editor, including specialized game asset formats.

Study how one editor accommodates differing geometry and animation semantics without duplicating its whole interface for each format.

- **C1:** [undo.js](https://github.com/JannisX11/blockbench/blob/master/js/undo.js) coordinates before/after snapshots, selection changes, redo-history truncation, cancellation, group tracking, and edit-session notifications. It is a useful study of maintaining coherent document state across several editing modes.
- **C2:** [format.ts](https://github.com/JannisX11/blockbench/blob/master/js/io/format.ts) models format capabilities such as rig types, texture assignment, coordinate and rotation restrictions, animation-loop wrapping, and quaternion interpolation. These capabilities govern shared editor behavior instead of being merely export-format labels.

### 7. [stephomi/sculptgl](https://github.com/stephomi/sculptgl)

**Language/role:** JavaScript/WebGL; browser sculpting application. **Archived; development stopped:** the repository points to the author's subsequent work on Nomad Sculpt.

Despite its historical status, this is a substantial implementation of interactive mesh editing with particularly readable local-topology code.

- **C1:** [Decimation.js](https://github.com/stephomi/sculptgl/blob/master/src/mesh/dynamic/Decimation.js) updates vertex/face adjacency, spatial-leaf membership, index references, and undo records when compacting arrays after deletions. Correctness requires all those representations to continue describing the same mesh.
- **C3:** [MeshDynamic.js](https://github.com/stephomi/sculptgl/blob/master/src/mesh/dynamic/MeshDynamic.js) exposes partial topology/render updates and typed-array capacity management for interactive sculpting. It also documents tradeoffs: dynamic topology is triangle-only, strips UVs, and has a deliberately simple wireframe implementation. Those limitations help explain the design rather than conceal it.

### 8. [guillaumechereau/goxel](https://github.com/guillaumechereau/goxel)

**Language/role:** C; voxel art editor with layers, undo, procedural operations, and mesh export.

Study a compact example of designing editable document storage around cheap snapshots. The [internals document](https://github.com/guillaumechereau/goxel/blob/master/INTERNALS.md) is an unusually direct entry point.

- **C1:** Voxel blocks and volumes use reference-counted copy-on-write, while image history stores layer snapshots. Preserving old edits therefore depends on detaching shared storage correctly before mutation—an ownership invariant central to undo correctness.
- **C3:** Block-level sharing avoids duplicating all voxel data for each history entry. A common painter-driven volume operation and deferred rendering queue separate mutation, storage, and draw submission, making the memory-saving strategy understandable without studying the entire UI first.

### 9. [vengi-voxel/vengi](https://github.com/vengi-voxel/vengi)

**Language/role:** C++; voxel editor and command-line asset tools with animation support. Counted once, including its VoxEdit and shared scene-graph subsystems.

Study how voxel volumes, palettes, scene hierarchy, and animation coexist in a reusable internal asset representation.

- **C1:** [SceneGraphTransform.h](https://github.com/vengi-voxel/vengi/blob/master/src/modules/scenegraph/SceneGraphTransform.h) states that local and world transforms cannot be modified simultaneously and that setters require a subsequent update. Dirty flags, parent changes, frame-dependent updates, and validation make transform-consistency obligations explicit.
- **C2:** [SceneGraph.h](https://github.com/vengi-voxel/vengi/blob/master/src/modules/scenegraph/SceneGraph.h) provides hierarchy, animation management, palette merging, identity lookup, and common save/load representation. Palette handling even accounts for formats that reserve a color index for empty space, illustrating the abstraction's role across import/export and editing workflows.

## Procedural construction and motion graphics

### 10. [GafferHQ/gaffer](https://github.com/GafferHQ/gaffer)

**Language/role:** C++ and Python; node-based look development, lighting, scene assembly, and production automation application/framework.

Study demand-driven evaluation where the same scene graph is queried in different contexts, such as different frames or scene locations.

- **C1:** [ComputeNode.h](https://github.com/GafferHQ/gaffer/blob/main/include/Gaffer/ComputeNode.h) permits concurrent value requests with different contexts. Implementations must hash every input and context value used by computation; an omitted dependency can therefore yield an incorrect cached result even when the computation itself is correct.
- **C3:** The interface separates hashing from computation, permits pass-through nodes to share cache entries, and requires task-compatible cache policies for computations that spawn TBB tasks. This is concrete guidance for coordinating reusable caching with nested parallel work.

### 11. [nortikin/sverchok](https://github.com/nortikin/sverchok)

**Language/role:** Python; Blender extension for parametric geometry and visual programming, including meshes, curves, surfaces, fields, and solids.

Study a substantial authoring system embedded in another application's event loop and data model.

- **C1:** [update_system.py](https://github.com/nortikin/sverchok/blob/master/core/update_system.py) treats animation-frame events differently from timer-driven scene updates because a new frame can arrive before a timer task finishes. It also handles stale graph state after undo and resets cached state when files change.
- **C2:** The [Node API](https://github.com/nortikin/sverchok/blob/master/docs/contributing/node_api.rst) defines common node classes, property updates, sockets, and draft-mode substitutions. Its discussion of keeping dynamic enum data alive also exposes a concrete lifetime hazard at the Python/Blender boundary.

### 12. [JacquesLucke/animation_nodes](https://github.com/JacquesLucke/animation_nodes)

**Language/role:** Python and Cython; Blender motion-graphics visual scripting system.

Study the translation from an artist-authored graph into executable code, including the handling of mutable values passed through sockets.

- **C1:** [code_generator.py](https://github.com/JacquesLucke/animation_nodes/blob/master/animation_nodes/execution/code_generator.py) generates input conversions and copies, distinguishes execution/monitoring/baking modes, and can report missing computed outputs. Graph wiring must preserve data semantics when nodes mutate their inputs.
- **C2:** [units.py](https://github.com/JacquesLucke/animation_nodes/blob/master/animation_nodes/execution/units.py) separates main networks, groups, loops, and script subprograms behind execution units with setup and finish phases. That supports reusable procedural structures beyond a flat list of node callbacks.

### 13. [zenustech/zeno](https://github.com/zenustech/zeno)

**Language/role:** C++ with Qt and optional CUDA components; node-based procedural 3D, simulation, and rendering environment.

Study how numerical simulation kernels become artist-facing nodes. The selected subsystem is the node interface plus the position-based dynamics implementation; the repository contains many additional projects that were not audited here.

- **C1:** [PBDSolveVolumeConstraint.cpp](https://github.com/zenustech/zeno/blob/master/projects/PBD/PBDSolveVolumeConstraint.cpp) computes tetrahedral volume constraints using gradients, inverse masses, timestep, and compliance. It explicitly identifies its Gauss–Seidel approach as difficult to parallelize. The numerical assumptions and update ordering are useful study material, not evidence of unconditional stability for arbitrary inputs.
- **C2:** [INode.h](https://github.com/zenustech/zeno/blob/master/zeno/include/zeno/core/INode.h) supplies a shared node lifecycle, named inputs/outputs, checked typed access, graph/session access, keyframes, and formulas. This turns simulation and geometry operations into composable authoring components.

### 14. [tixl3d/tixl](https://github.com/tixl3d/tixl)

**Language/role:** C# and shader code; TiXL, formerly Tooll3, combines procedural motion graphics, real-time rendering, and timeline animation. The relevant scope is its operator graph and animation machinery.

Study the interaction between live graph edits, cached output values, and keyframed parameters.

- **C1:** [Slot.cs](https://github.com/tixl3d/tixl/blob/main/Core/Operator/Slots/Slot.cs) explains why bypassing a node must preserve its original value and update action, and why ordinary invalidation can miss a UI change arriving after the frame's invalidation pass. These are concrete stale-state and identity hazards.
- **C2:** Generic slots expose values, connections, dirty state, animation actions, and time-clip remapping through a common operator interface. [EvaluationContext.cs](https://github.com/tixl3d/tixl/blob/main/Core/Operator/EvaluationContext.cs) carries object/world/camera matrices, materials, lights, and local playback time through graph evaluation, grounding the abstraction in reusable 3D scene and animation operations.

## Character creation and animation processing

### 15. [makehumancommunity/makehuman](https://github.com/makehumancommunity/makehuman)

**Language/role:** Python with NumPy and Qt; parameter-driven human character creation application.

Study how many user-facing shape controls map to weighted deformation targets and dependent model parameters. [humanmodifier.py](https://github.com/makehumancommunity/makehuman/blob/master/makehuman/apps/humanmodifier.py) is the main entry point.

- **C1:** Modifier actions account for symmetry and for resets that change multiple modifiers. Undo must restore the dependent values and reapply targets, rather than merely put one slider back at its previous position.
- **C2:** A shared `Modifier` abstraction manages target sets, weights, bounds, macro variables, and macro dependencies. It supports an extensive family of shape controls through the same update machinery.
- **C3:** The implementation distinguishes dependency groups updated during slider dragging from the full dependency update on release. This makes the responsiveness/completeness tradeoff explicit. The repository's own status prose is not treated as proof of a recent release.

### 16. [hkrn/nanoem](https://github.com/hkrn/nanoem)

**Language/role:** C/C++, with platform-specific frontends; MikuMikuDance-compatible animation application with model editing.

Study compatibility-oriented authoring architecture from the MMD community. The detailed [architecture document](https://github.com/hkrn/nanoem/blob/main/docs/architecture.rst), written in Japanese, separates the data library, application core, and platform UI layers.

- **C1:** The document specifies mutation ownership, opaque objects, status-based errors, string conversion across Shift-JIS/UTF encodings, and ordering of motion application before and after physics. These obligations span file interoperability, object lifetime, and animation evaluation.
- **C2:** The C library unifies model and motion data behind opaque APIs, while the C++ `emapp` layer implements shared application behavior. Platform frontends can reuse that core. The [application test tree](https://github.com/hkrn/nanoem/tree/main/emapp/test) provides further entry points organized by models, motion, cameras, projects, and other authoring concepts.

### 17. [Mesh2Motion/mesh2motion-app](https://github.com/Mesh2Motion/mesh2motion-app)

**Language/role:** TypeScript/Three.js; browser workflow for fitting skeletons, generating skin weights, previewing animations, retargeting, and exporting GLB/glTF assets.

Study a smaller authoring application in which difficult rigging behavior is exposed through focused services and processing stages. This entry makes no multi-year maturity claim.

- **C1:** [AnimationRetargetService.ts](https://github.com/Mesh2Motion/mesh2motion-app/blob/main/src/retarget/AnimationRetargetService.ts) captures rest transforms when a model is loaded, before animation overwrites them. Its comments explain why reconstructing them from inverse bind matrices can reintroduce import scale, and it separates human swing/twist retargeting from simple bone mapping.
- **C2:** [SkinningAlgorithm.ts](https://github.com/Mesh2Motion/mesh2motion-app/blob/main/src/lib/solvers/SkinningAlgorithm.ts) orchestrates distinct weight calculation, anatomical correction, smoothing, normalization, and optional head-correction components. This is an inspectable multi-stage implementation serving different skeleton configurations, rather than just a wrapper around model loading.

### 18. [guillaumeblanc/ozz-animation](https://github.com/guillaumeblanc/ozz-animation)

**Language/role:** C++; skeletal animation library and offline conversion toolset. A processing component for animation pipelines, not a modeling editor.

Study the separation between editable offline data and immutable runtime representations. The [runtime architecture guide](https://guillaumeblanc.github.io/ozz-animation/documentation/animation_runtime/) connects storage decisions directly to sampling and blending algorithms.

- **C1:** Quaternion reconstruction, required endpoint keys, hierarchy ordering, and overflow handling for previous-key offsets impose numerical and representational constraints. The guide describes insertion of additional keys when an offset cannot be represented.
- **C3:** Keyframe ordering, decompressed structure-of-arrays caches, and intermediate seek snapshots address sequential playback, backward playback, and random seeking. The discussion of version 0.15's changes is particularly useful for understanding why optimizing only forward playback was insufficient.
- **C2:** Sampling, blending, local-to-model conversion, and track-event processing are separate jobs with explicit caller-provided inputs and outputs, enabling engine-independent integration.

### 19. [nfrechette/acl](https://github.com/nfrechette/acl)

**Language/role:** C++; Animation Compression Library for offline compression and runtime playback of skeletal animation tracks.

Study the connection between perceptual animation quality, transform mathematics, and compressed memory layout.

- **C1:** The [error-metric documentation](https://github.com/nfrechette/acl/blob/develop/docs/error_metrics.md) explains why the metric must match the host engine's transform composition. It distinguishes vector/quaternion scale handling from matrix handling of shear, while identifying numerical error accumulation with extreme scales and translations.
- **C3:** The [uniformly sampled algorithm](https://github.com/nfrechette/acl/blob/develop/docs/algorithm_uniformly_sampled.md) compacts constant/default tracks, reduces sample precision, and groups samples by time and track for locality. It makes the layout's relationship to forward, reverse, and arbitrary-time sampling explicit without requiring unsupported benchmark claims.

## Scene, material, and geometry infrastructure

### 20. [PixarAnimationStudios/OpenUSD](https://github.com/PixarAnimationStudios/OpenUSD)

**Language/role:** C++ and Python; scene-description, composition, authoring, and imaging framework. Relevant monorepo subsystems include layers, stages, schemas, and composition; this is not only a file parser.

Study how independently authored assets and edits combine into a consistent scene.

- **C1:** The [threading contract](https://openusd.org/release/api/_usd__page__multi_threading.html) permits multiple readers or a single writer. Loading/unloading counts as mutation, and two distinct stages can still conflict if they share a layer. That subtle shared-dependency rule matters when building concurrent authoring tools.
- **C2:** The [technical introduction](https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/docs/intro.rst) describes layers, composition arcs, schemas, references, and overrides as a common model for assembling and editing geometry, materials, and time-varying scene data. These abstractions support cooperation among modeling, animation, lighting, and rendering applications.

### 21. [alembic/alembic](https://github.com/alembic/alembic)

**Language/role:** C++, with Python bindings and DCC integrations; animated scene-data interchange framework.

Study a focused boundary between time-sampled asset data and the tools that produce or consume it. This complements scene authoring systems without itself supplying a complete animation UI.

- **C1:** [TimeSampling.h](https://github.com/alembic/alembic/blob/master/lib/Alembic/AbcCoreAbstract/TimeSampling.h) unifies uniform, cyclic, and acyclic sample timing. Floor, ceiling, and nearest-sample queries have explicit boundary and nonempty-sample preconditions, making temporal lookup semantics visible to readers and writers.
- **C2:** [ISchemaObject.h](https://github.com/alembic/alembic/blob/master/lib/Alembic/Abc/ISchemaObject.h) layers schema-aware objects over generic archive objects, with metadata-based matching and configurable interpretation policies. It illustrates reusable typed scene access without baking every geometry type into the low-level storage abstraction.

### 22. [AcademySoftwareFoundation/MaterialX](https://github.com/AcademySoftwareFoundation/MaterialX)

**Language/role:** C++ with Python/JavaScript bindings and shader libraries; material/look-development representation, shader generation, viewer, and graph editor.

Study how an authored material graph remains independent of the shading language and renderer that eventually execute it.

- **C2:** The [shader-generation guide](https://github.com/AcademySoftwareFoundation/MaterialX/blob/main/documents/DeveloperGuide/ShaderGeneration.md) separates the common generator from language/target-specific generators and syntax classes. Typed node definitions can be implemented by inline expressions, target-language functions, node graphs, or C++ emitters. The output is shader source requiring a downstream compiler, an important architectural boundary.
- **C4:** The [changelog](https://github.com/AcademySoftwareFoundation/MaterialX/blob/main/CHANGELOG.md) contains dated releases from 2017 through 2026 and concrete evolution work: deprecated interfaces, retained legacy color-space names, GLSL/Vulkan and renderer compatibility fixes, and additional core/ESSL generation tests. This supports maturity more directly than the project's age alone.

### 23. [PixarAnimationStudios/OpenSubdiv](https://github.com/PixarAnimationStudios/OpenSubdiv)

**Language/role:** C++ and GPU backend code; subdivision-surface evaluation for deforming meshes in authoring and animation systems.

Study how expensive topology analysis is separated from the per-frame evaluation of changing vertex positions.

- **C2:** The [API architecture](https://github.com/PixarAnimationStudios/OpenSubdiv/blob/dev/documentation/api_overview.rst) separates subdivision rules (`Sdc`), internal topology (`Vtr`), client-facing refinement (`Far`), face evaluation (`Bfr`), and platform evaluation/drawing (`Osd`). Applications can adopt selected layers rather than a complete rendering stack.
- **C3:** The same guide describes stencil-table precomputation for unchanged topology, amortizing work across deforming frames. It also explains the flexibility/efficiency tradeoff between CPU face evaluation and the parallel evaluation path, making backend choices explicit rather than treating GPU use as sufficient evidence of performance quality.

### 24. [AcademySoftwareFoundation/openvdb](https://github.com/AcademySoftwareFoundation/openvdb)

**Language/role:** C++; sparse-volume manipulation for film/VFX content, with DCC integrations and related components in one monorepo. This entry focuses on core OpenVDB's editable volumetric representation; NanoVDB and AX are not separate entries.

Study the distinction between volume storage and its interpretation in physical space. The [architecture overview](https://github.com/AcademySoftwareFoundation/openvdb/blob/master/doc/doc.txt) is the main entry point.

- **C2:** `Tree`, `Transform`, and `Grid` separate sparse values, coordinate mapping, and metadata. Multiple grids can share the same tree while positioning it differently, supporting instancing and multiple tool workflows.
- **C3:** The tree represents unique voxels, uniform tiles, and background values differently, while sparsity-aware traversal avoids unnecessary dense work. These decisions support content operations such as filtering, CSG, compositing, and voxelization under significant memory pressure. The repository warns that its development branch is less tested than production releases; a branch snapshot is not a release-quality guarantee.

## Search coverage and limitations

Discovery used more than six distinct live web-search formulations, followed by direct reads of public GitHub repository pages, source files, architecture guides, and changelogs. Search angles included:

- Complete 3D modeling/animation suites, including Erlang and Java implementations.
- Procedural/node-based modeling, lighting, simulation, and C# motion graphics.
- Browser sculpting, low-poly asset editing, and voxel creation/animation tools.
- Character generation, rigging, retargeting, and MMD-compatible authoring.
- Skeletal runtime data structures and animation compression.
- Scene composition/interchange, material graphs, subdivision, and sparse-volume infrastructure.
- Additional searches for less-known authoring tools and SDF/node editors; these increasingly returned overlapping projects, small prototypes, 2D systems, and adjacent rendering/game-engine projects. The later pass added nanoem and Mesh2Motion because they contributed distinct implementations and communities.

Search results were discovery aids only. Retained entries were checked against primary implementation material; stars and promotional performance claims were not used as quality evidence. Where the web reader could not retrieve a page, public GitHub/raw-source reads supplied the evidence. No repositories were cloned and no dependencies were installed.

The report deliberately does not duplicate Blender forks with substantially shared cores, count asset-only companion repositories, or list wrappers and tutorial demonstrations as independent systems. Proprietary products without substantive public implementations, including commercial authoring applications, are excluded. CAD and reconstruction-heavy tools were left to their more specific categories. Supporting libraries are included only where their relationship to authoring or animation is direct and explained above.

Maintenance and validation vary. Blender is an official mirror, SculptGL is archived, and K-3D is a historical code-study selection. Other entries are not blanket claims of active maintenance, stable APIs, or comprehensive testing. C4 is awarded only where the inspected chronology and compatibility/testing evidence support it. This was a source-guided selection exercise, not a full code audit, benchmark reproduction, or review of every subsystem; links to development branches can change after the research date.
