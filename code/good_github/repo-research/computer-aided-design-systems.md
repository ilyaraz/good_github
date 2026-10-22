# Computer-aided design systems

Research date: **2026-10-09**.

This selection covers 21 GitHub repositories for engineering design: interactive mechanical CAD, 2D drafting, programmable modeling, CAD kernels, architectural/BIM authoring, aircraft geometry, and schematic/PCB design. Libraries qualify when they implement substantial modeling or design-system infrastructure. General-purpose rendering engines, model collections, manufacturing machine controllers, and simulation-only software are outside this report's scope. Each retained repository's GitHub page was opened, and additional primary implementation or architecture material was read.

The criteria describe engineering substance, not a certification that every implementation choice is exemplary:

- **C1 — Difficult correctness:** geometric or numerical semantics, invariants, concurrency, adversarial inputs, or consequential failure modes.
- **C2 — Reusable abstractions:** substantial models, APIs, or frameworks supporting multiple operations and applications.
- **C3 — Performance with structure:** concrete techniques addressing real computational or interactive constraints within an understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or management of growing complexity. Age or a recent commit alone does not qualify.

## Interactive mechanical CAD and drafting

### [FreeCAD/FreeCAD](https://github.com/FreeCAD/FreeCAD)

**Language/role:** C++ and Python; an extensible parametric CAD application. Study the application document infrastructure behind the Part, PartDesign, Sketcher, and other workbenches, rather than treating this large repository as a single modeling algorithm.

- **C1:** Document recomputation crosses dependency ordering, undo/rollback, Python execution, and GUI-thread boundaries. The implementation guards recursive recomputation and transaction re-entry, and explains how retaining the Python GIL during recomputation preserves existing Python-backed feature behavior while signal hops must avoid deadlocks. These are concrete correctness obligations in an extensible CAD application. See [`src/App/Document.cpp`](https://github.com/FreeCAD/FreeCAD/blob/main/src/App/Document.cpp).
- **C2:** The document's object dependency and transaction machinery supports heterogeneous features through a shared lifecycle. Combined with the repository's documented workbench and Python model, this provides a useful study of how a general application framework accommodates mechanical design, drawings, and architecture. Start with the same [document implementation](https://github.com/FreeCAD/FreeCAD/blob/main/src/App/Document.cpp) and the [source tree](https://github.com/FreeCAD/FreeCAD/tree/main/src).

### [solvespace/solvespace](https://github.com/solvespace/solvespace)

**Language/role:** C++; constraint-based 2D/3D CAD with a reusable solver. An especially focused entry point for understanding what happens between a sketch constraint and an interactive numerical solution.

- **C1:** [`src/system.cpp`](https://github.com/solvespace/solvespace/blob/master/src/system.cpp) builds and evaluates a symbolic Jacobian, calculates rank and degrees of freedom, distinguishes redundancy from non-convergence, and identifies offending constraints. Its least-squares implementation explicitly discusses how normal equations square the condition number and can falsely make large sketches appear unsolvable.
- **C3:** The same implementation uses sparse QR, substitution of simple equations, separate solution of single-parameter equations, and time limits on constraint-removal diagnostics. Performance decisions are visible beside the numerical tradeoffs, including weighting dragged parameters and optional expensive freedom analysis. The [solver source](https://github.com/solvespace/solvespace/blob/master/src/system.cpp) is the principal reading entry point.

### [dune3d/dune3d](https://github.com/dune3d/dune3d)

**Language/role:** C++; parametric 3D CAD combining Open CASCADE, a modified SolveSpace solver, and its own interactive document/editor infrastructure. It is a separate application, although its [architecture discussion](https://github.com/dune3d/dune3d/blob/main/README.md) explicitly credits substantial reuse from SolveSpace and Horizon EDA.

- **C1:** The document loader handles failures per entity, constraint, and group; removes invalid constraints; and applies version-specific semantic upgrades. For example, a file-version migration reverses certain aligned-distance constraint values before regeneration. See [`document.cpp`](https://github.com/dune3d/dune3d/blob/main/src/document/document.cpp).
- **C2:** Entities, constraints, and ordered groups are separate document concepts, while group generation, constraint solving, and solid-model updates have distinct phases. Pending-update markers allow those phases to restart from different positions in the feature history. This is a useful implementation of recomputation orchestration above reused numerical kernels, visible in the same [document source](https://github.com/dune3d/dune3d/blob/main/src/document/document.cpp).

### [NoteCAD/NoteCAD](https://github.com/NoteCAD/NoteCAD)

**Language/role:** C#; Unity-based parametric CAD and sketching with its own expression and constraint-solving code. This smaller project provides a different implementation language and application environment from the C++ desktop systems.

- **C1:** [`EquationSystem.cs`](https://github.com/NoteCAD/NoteCAD/blob/master/Assets/Code/Solver/EquationSystem.cs) contains Jacobian generation, rank/degree-of-freedom calculations, iterative least-squares updates, distinct drag iterations, jump detection, and restoration of old parameter values after failed solves. These are substantive interactive solver failure modes.
- **C2:** [`Expression.cs`](https://github.com/NoteCAD/NoteCAD/blob/master/Assets/Code/Solver/Expression.cs) represents parameters and symbolic operations separately from sketch entities, with evaluation and differentiation interfaces for custom functions. The equation-system API accepts individual or vector equations and parameter collections, making the solver architecture useful beyond one geometric constraint.

Read critically: the inspected residual evaluator replaces a NaN residual with zero. That policy deserves scrutiny when studying solver correctness; inclusion here does not establish numerical robustness.

### [LibreCAD/LibreCAD](https://github.com/LibreCAD/LibreCAD)

**Language/role:** C++/Qt; 2D engineering drafting. LibreCAD originated from QCAD Community Edition, but its separate entity/math implementation and substantial independent development justify retaining it alongside modern QCAD.

- **C1:** [`lc_quadratic.cpp`](https://github.com/LibreCAD/LibreCAD/blob/master/librecad/src/lib/math/lc_quadratic.cpp) handles line/conic and conic/conic geometry with explicit degeneracy checks. Intersection handling changes coordinate orientation or rotates a problem when coefficients approach problematic values; construction also rejects zero-length and nearly degenerate cases. This makes numerical geometry directly traceable to drafting operations.
- **C2:** The [`RS_Entity` interface](https://github.com/LibreCAD/LibreCAD/blob/master/librecad/src/lib/engine/document/entities/rs_entity.h) combines drawable and undoable behavior with common cloning, identity, snapping, reference-point, and transformation operations. Lines, arcs, circles, and composite entities participate in the same editing contracts; even clone identity and transient flags are documented.

### [qcad/qcad](https://github.com/qcad/qcad)

**Language/role:** C++ and ECMAScript; scriptable 2D CAD. The repository covers the open-source system; its description distinguishes optional DWG functionality supplied through a proprietary plugin.

- **C2:** [`RDocument.h`](https://github.com/qcad/qcad/blob/master/src/core/RDocument.h) separates the graphics document from its `RStorage`, `RSpatialIndex`, and `RTransactionStack`. Entities, layers, blocks, coordinate systems, variables, and undo groups share this document abstraction. Study how drafting commands can operate against common storage and transaction interfaces.
- **C3:** The same interface exposes spatially indexed entity lookups, block-specific indices, nearest-object queries, and bounding-box-only versus more detailed intersection searches. This is a concrete architectural response to interactive selection and snapping in large drawings, rather than an unsupported claim about application speed. The [document header](https://github.com/qcad/qcad/blob/master/src/core/RDocument.h) is the main entry point.

### [xibyte/jsketcher](https://github.com/xibyte/jsketcher)

**Language/role:** JavaScript and TypeScript, with Open CASCADE WebAssembly integration; browser-based parametric 2D/3D CAD. Study its own sketch solver and history/workbench layer, not the wrapped geometry kernel as if it were independently implemented here.

- **C1:** [`AlgNumSystem.ts`](https://github.com/xibyte/jsketcher/blob/main/web/app/sketcher/constr/AlgNumSystem.ts) tracks conflicting and redundant constraints, snapshots parameter values, rolls back unsuccessful constraint additions, and reduces polynomials before numerical solving. It also distinguishes parameters owned by the current stage from external ones.
- **C2:** The [workbench developer guide](https://github.com/xibyte/jsketcher/blob/main/dev-guide/index.md) defines feature operations through a shared schema for dialog inputs and stored history parameters, execution code, and created/consumed geometry. Automatic geometry IDs and standard selection widgets connect UI extensions to a replayable part history.

## Programmable CAD and fabrication-oriented modeling

### [openscad/openscad](https://github.com/openscad/openscad)

**Language/role:** C++; a CAD language, evaluator, and solid-modeling application. Useful for studying a geometry compiler whose intermediate objects must serve both rendering and solid operations.

- **C1:** [`GeometryEvaluator.cc`](https://github.com/openscad/openscad/blob/master/src/geometry/GeometryEvaluator.cc) validates dimensional compatibility, dispatches between 2D and 3D operations, and handles conversion from engine-specific geometry to polygon sets. Its comments explain why indeterminate convexity and non-planar faces require careful tessellation decisions.
- **C3:** Evaluation traverses the modeling tree only after cache lookup fails. Raw geometry is cached separately from requested polygon conversions because caching a converted representation could change the behavior of a later request. This exposes a useful connection between representation semantics and performance in the [evaluator implementation](https://github.com/openscad/openscad/blob/master/src/geometry/GeometryEvaluator.cc). The [testing guide](https://github.com/openscad/openscad/blob/master/doc/testing.md) additionally distinguishes normal, heavy, example, known-bug, unit, and GUI tests; it warns that parts of the guide may be outdated.

### [CadQuery/cadquery](https://github.com/CadQuery/cadquery)

**Language/role:** Python; programmable parametric B-rep modeling and assemblies over OCCT. This is a substantial modeling API and solver integration, not merely a generated binding layer.

- **C2:** The [concepts and API-layer guide](https://github.com/CadQuery/cadquery/blob/master/doc/primer.rst) distinguishes fluent workplanes/sketches/assemblies, free shape functions, geometric coordinate abstractions, and the underlying OCCT API. Study how selection and workplane operations hide kernel bookkeeping while retaining lower-level access.
- **C1:** [`occ_impl/solver.py`](https://github.com/CadQuery/cadquery/blob/master/cadquery/occ_impl/solver.py) defines assembly constraint invariants for arity, geometric marker types, parameter types, and angle conversions. It also turns compound plane constraints into simpler constraints and builds a scaled optimization objective over translations and rotations. The code makes validation and numerical conventions explicit at the API/kernel boundary.

### [gumyr/build123d](https://github.com/gumyr/build123d)

**Language/role:** Python; a parametric B-rep CAD framework with builder and algebra APIs. The repository identifies its CadQuery-derived portions and extensive restructuring; its separate composition model makes it a substantive independent study.

- **C2:** The [builder concepts](https://github.com/gumyr/build123d/blob/dev/docs/key_concepts_builder.rst) explain a construction context that accumulates geometry through add, subtract, intersect, replace, and private modes, then finalizes its output on context exit. Separate line, sketch, and part builders provide dimensional structure rather than one undifferentiated shape API.
- **C3:** The [algebra performance guide](https://github.com/gumyr/build123d/blob/dev/docs/algebra_performance.rst) traces growing cost to repeated `fuse` and `clean` calls inside loops, and shows collection-based operations that perform these steps once. This is a concrete interaction between API design and expensive kernel calls. Its machine-specific timings are not generalized here.

### [jscad/OpenJSCAD.org](https://github.com/jscad/OpenJSCAD.org)

**Language/role:** JavaScript with TypeScript declarations; a monorepo of programmable 2D/3D modeling, browser, and command-line tools. Counted once, with the `packages/modeling` subsystem as the main engineering target.

- **C1:** The [3D union implementation](https://github.com/jscad/OpenJSCAD.org/blob/master/packages/modeling/src/operations/booleans/unionGeom3Sub.js) combines polygon-tree clipping and inversion, with a separate nonintersecting path guarded by an overlap test. The distinction matters: concatenating polygons is valid only when the solids cannot overlap.
- **C3:** [`unionGeom3.js`](https://github.com/jscad/OpenJSCAD.org/blob/master/packages/modeling/src/operations/booleans/unionGeom3.js) combines multiple inputs in a balanced binary-tree pattern and retessellates the result afterward. Together with the nonoverlap shortcut, this provides a compact study of scheduling expensive CSG operations without obscuring their geometry semantics.

### [microsoft/maker.js](https://github.com/microsoft/maker.js)

**Language/role:** TypeScript/JavaScript; programmable 2D path and model construction for CNC and laser-cut designs. Its role is geometric drawing and fabrication outlines, rather than machine control.

- **C1:** [`combine.ts`](https://github.com/microsoft/maker.js/blob/master/packages/maker.js/src/core/combine.ts) breaks paths at foreign intersections, distinguishes duplicate and overlapping segments, rejects effectively zero-length fragments, and carries model offsets through intersection calculations. These details are essential to usable Boolean outlines with lines, arcs, and circles.
- **C2:** The [core source tree](https://github.com/microsoft/maker.js/tree/master/packages/maker.js/src/core) exposes complementary path/model, chain, intersection, fillet, expansion, measurement, unit, and export abstractions. The combination algorithm consumes those common walking and path contracts, illustrating how a small geometric object model can support many fabrication operations and output formats.

## Modeling kernels and geometric infrastructure

### [Open-Cascade-SAS/OCCT](https://github.com/Open-Cascade-SAS/OCCT)

**Language/role:** C++; surface/solid modeling, CAD exchange, visualization, and application infrastructure. Many other entries build on this kernel, so reading it answers different questions from reading their higher-level APIs.

- **C1:** The [modeling-algorithms manual](https://github.com/Open-Cascade-SAS/OCCT/blob/master/dox/user_guides/modeling_algos/modeling_algos.md) describes tolerance-bearing intersection algorithms and distinguishes isolated intersection points from tangential overlap segments. It exposes geometric algorithms beneath topological modeling operations, making their numerical assumptions inspectable.
- **C2:** The [OCAF manual](https://github.com/Open-Cascade-SAS/OCCT/blob/master/dox/user_guides/ocaf/ocaf.md) addresses document data organization, display synchronization, persistence, undo/redo, and integration with modeling libraries. This broadens the study from a shape kernel to reusable infrastructure for domain-specific CAD applications.

### [ricosjp/truck](https://github.com/ricosjp/truck)

**Language/role:** Rust; a modular B-rep/NURBS CAD kernel. Particularly useful for examining a native Rust design rather than a binding to an existing C++ kernel.

- **C1:** [`truck-topology/src/lib.rs`](https://github.com/ricosjp/truck/blob/master/truck-topology/src/lib.rs) specifies simple, closed face boundaries and closed, oriented solid boundaries. Geometric coincidence does not imply topological identity: separately constructed vertices, edges, and faces have distinct identities. Orientation and shared `Arc<Mutex<...>>` geometry make the aliasing model explicit.
- **C2:** The same source parameterizes topology over point, curve, and surface types, even demonstrating topology with empty geometry. The [crate structure](https://github.com/ricosjp/truck/tree/master) separates geometry traits, topology, modeling, tessellation, shape operations, STEP I/O, and rendering, allowing engineers to study those layers independently.

### [elalish/manifold](https://github.com/elalish/manifold)

**Language/role:** C++; solid triangle-mesh operations and 2D cross-sections, with language bindings. Its repository explicitly places mesh Boolean operations at the foundation of a CAD kernel; this is not merely a graphics mesh viewer.

- **C1:** The [Boolean2 architecture document](https://github.com/elalish/manifold/blob/master/docs/Boolean2.md) details epsilon-based vertex merging, collapsed-edge removal, incidence splitting, near-concurrent sweep events, winding classification, and cleanup of residual crossings. It connects topological balance requirements to rounded arithmetic and specifies deterministic regression and fuzz testing of cross-section operations and solid round trips.
- **C3:** That document separates broad-phase candidate generation, arrangement coordination, sweep-line processing, geometric predicates, and diagnostics. Interval sweeps and BVH queries reduce candidate intersection work before detailed geometry processing. The [Boolean2 design](https://github.com/elalish/manifold/blob/master/docs/Boolean2.md) is a concrete entry point into robustness and performance together; no universal benchmark or absolute robustness claim is inferred here.

### [libfive/libfive](https://github.com/libfive/libfive)

**Language/role:** C++, with Scheme-facing modeling tools; an implicit-function CAD kernel. It provides a useful alternative to both exact-surface B-rep modeling and polygonal CSG.

- **C1:** [`interval.hpp`](https://github.com/libfive/libfive/blob/master/libfive/include/libfive/eval/interval.hpp) augments numeric intervals with possible-NaN state, makes ambiguous domains explicit, and documents the asymmetric NaN behavior of `std::min`/`std::max`. Even narrowing conversions are handled with interval safety in mind.
- **C3:** [`eval_interval.cpp`](https://github.com/libfive/libfive/blob/master/libfive/src/eval/eval_interval.cpp) evaluates an expression tape over spatial regions and prunes a minimum/maximum branch only when the interval bounds establish that one branch dominates. Study how a numerical enclosure becomes a safe optimization of repeated implicit-geometry evaluation.

## Architectural and domain-specific CAD

### [IfcOpenShell/IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell)

**Language/role:** C++ and Python; IFC geometry/data infrastructure and the Bonsai BIM authoring application. This monorepo is counted once. The relevant subsystems are `src/ifcgeom`, the Python IFC APIs, and `src/bonsai`, rather than every utility shipped in the repository.

- **C2:** The [Bonsai development architecture](https://github.com/IfcOpenShell/IfcOpenShell/blob/v0.8.0/src/bonsai/docs/guides/development/hello_world.rst) makes IFC the in-memory source of truth and uses Blender as an interface. Modules follow divisions in BIM data; UI operators, core behavior, tool implementations, and tests are separated. This is a substantive design-authoring system, not just a format converter.
- **C3:** The [geometry iterator documentation](https://docs.ifcopenshell.org/ifcopenshell/geometry_iterator.html) explains multicore processing, caching, and geometry reuse, with filtering and either triangulated or OCCT B-rep output. Study how large building models are processed through a reusable traversal interface instead of independently reconstructing every shape.

### [OpenVSP/OpenVSP](https://github.com/OpenVSP/OpenVSP)

**Language/role:** Primarily C/C++, with scripting interfaces; parametric aircraft geometry and associated engineering analysis. The selection focuses on `src/geom_core`, not the aerodynamic solver as a separate project.

- **C1:** [`Parm.cpp`](https://github.com/OpenVSP/OpenVSP/blob/main/src/geom_core/Parm.cpp) centralizes parameter limits and distinguishes changes made by links from those made through user devices. It coordinates container notifications, link propagation, undo recording, and initial-value restoration. Its warning that changing an ID updates only some references is a concrete example of an important API precondition.
- **C2:** The shared parameter/container mechanism underlies different geometry types and both interactive and programmatic operations, making aircraft-specific modeling behavior reusable above one common state-management layer. Follow the [parameter implementation](https://github.com/OpenVSP/OpenVSP/blob/main/src/geom_core/Parm.cpp) into the geometry components.
- **C4:** The [changelog](https://github.com/OpenVSP/OpenVSP/blob/main/CHANGELOG.md) documents evolution across 2020–2026, including regressions from faster update processing, dependency/build changes, file consistency fixes, and clone behavior that attempts to preserve parameter IDs. This supports sustained complexity management, while also showing that optimization and compatibility work introduced real bugs.

## Electronic CAD and PCB layout

### [KiCad/kicad-source-mirror](https://github.com/KiCad/kicad-source-mirror)

**Language/role:** Primarily C++; schematic capture, PCB layout, routing, and related electronic-design tools. **Official substantive GitHub mirror:** its repository description identifies GitLab as the development home and says the mirror updates on pushes; GitHub pull requests are not watched. Counted once, with `pcbnew/router` as the principal subsystem here.

- **C1:** [`pns_node.h`](https://github.com/KiCad/kicad-source-mirror/blob/master/pcbnew/router/pns_node.h) models clearance, differential-pair, length, width, hole, and layer constraints. Its branched router world documents parent-lifetime requirements and commit behavior that destroys child branches, connecting geometric correctness to ownership and speculative editing.
- **C3:** The same router world uses spatial indexing and lightweight branching for recursive optimization and shove springback, and exposes deferred index construction for bulk additions. Study the [node abstraction](https://github.com/KiCad/kicad-source-mirror/blob/master/pcbnew/router/pns_node.h) alongside the [router source tree](https://github.com/KiCad/kicad-source-mirror/tree/master/pcbnew/router) to follow these responsibilities into placement, shove, walkaround, and optimization algorithms.

### [LibrePCB/LibrePCB](https://github.com/LibrePCB/LibrePCB)

**Language/role:** C++/Qt; integrated electronic CAD with schematic, board, and component-library infrastructure. Particularly useful for studying exact quantities and recoverable multi-file projects.

- **C1:** [`length.h`](https://github.com/LibrePCB/LibrePCB/blob/master/libs/librepcb/core/types/length.h) standardizes lengths as signed 64-bit integer nanometers across symbols, footprints, schematics, and layouts. It distinguishes potentially lossy floating conversions from exact textual persistence. These are explicit numeric semantics at every geometric boundary.
- **C2:** [`transactionalfilesystem.h`](https://github.com/LibrePCB/LibrePCB/blob/master/libs/librepcb/core/fileio/transactionalfilesystem.h) provides a shared filesystem abstraction for projects and library elements, with in-memory modifications, directory locking, autosave recovery, save operations, and ZIP export. Its thread-safety contract explicitly separates safe method calls from logically consistent multi-operation content, also providing additional **C1** evidence.

### [horizon-eda/horizon](https://github.com/horizon-eda/horizon)

**Language/role:** C++; electronic CAD with a structured component pool, schematic editor, and board editor. Its part-library model offers a distinct study from KiCad's routing algorithms and LibrePCB's persistence/type infrastructure.

- **C2:** [`part.hpp`](https://github.com/horizon-eda/horizon/blob/master/src/pool/part.hpp) separates logical entities, physical packages, gate/pin mappings, manufacturer attributes, 3D models, and orderable part numbers. Base-part inheritance and tri-state flags support families of real components without duplicating every library record.
- **C1:** [`part.cpp`](https://github.com/horizon-eda/horizon/blob/master/src/pool/part.cpp) reconstructs these relationships from JSON using UUIDs, checks that referenced package pads, gates, and pins exist, excludes mechanical pads from electrical mappings, and checks file versions. Study referential consistency between schematic meaning and physical footprint connectivity, including the behavior when referenced records are missing.

## Coverage, search process, and limitations

Discovery used more than six distinct live search formulations, including: parametric mechanical CAD and constraint solvers; Rust B-rep kernels; 2D drafting; Python/JavaScript CAD-as-code; implicit-function CAD; Boolean/mesh kernels; browser workbench/history systems; aircraft geometry; PCB/EDA architectures; BIM geometry iteration; C# solvers; and NURBS/historical CAD projects. Follow-up queries increasingly returned projects already represented, thin integrations over those kernels, recent prototypes, or adjacent simulation/rendering tools. The final selection favors distinct implementation families and substantive code over additional names.

Repository pages established canonical owner/repository paths and category fit. Source files, architecture/API guides, and selected release history supplied the implementation evidence. Primary GitHub content was also read through the GitHub connector; no repositories were cloned, no candidate code was run, and no dependencies were installed. Source links use the branches actually inspected, including `dev` for build123d and `v0.8.0` for Bonsai; they are reading entry points, not frozen reproducibility snapshots. The separately hosted IfcOpenShell iterator documentation identifies itself as 0.9.0.

Important boundaries and exclusions:

- **BRL-CAD is a material verification gap.** Live search located its official repository and release material, but repeated repository-page opens failed and the GitHub content API returned 404 through the available connector. It was not retained because the required direct repository verification could not be completed. This is an access limitation of this research, not a judgment that the project lacks engineering substance.
- **No separate counts for bindings or closely related forks.** OCCT wrappers, CadQuery editors, JSketcher UI forks, and Truck-derived forks were not added merely to increase coverage. build123d and LibreCAD were retained because the inspected implementations provide substantively separate abstractions/evolution; Dune 3D explicitly identifies the reused components within its own application architecture.
- **Historical/unfinished candidates were considered but not padded into the list.** Fornjot's [official repository](https://github.com/hannobraun/fornjot) was archived on June 19, 2026 and states that the project shut down before reaching its goals; it was not selected as a current CAD-system alternative. General mesh viewers, AI prompting layers around existing kernels, model datasets, pure solvers for simulation, and hardware-design files were excluded.
- **Electronic CAD is scoped to direct schematic/board design.** Semiconductor synthesis/place-and-route systems and manufacturing controllers could support separate deep reports; they are not exhaustively represented here. BIM is represented through Bonsai/IfcOpenShell rather than treating every BIM utility as a separate CAD system.

Statements about what an engineer can learn and the C1–C4 assignments are grounded assessments of the inspected material. No cross-project speed comparison, complete numerical validation, or uniform maintenance/production-readiness claim is made. C4 is used selectively where multi-year change-management evidence was actually read; a test directory or an old repository alone was not treated as sufficient.
