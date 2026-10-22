# Geometric modeling kernels and boundary representation libraries

Research date: 2026-10-09.

This selection covers 17 repositories implementing geometric modeling machinery: trimmed-surface boundary representations (B-reps), reusable spline geometry, polyhedral solid operations, and one explicitly identified implicit-modeling alternative. Spline toolkits and mesh kernels are distinguished from complete analytic-surface CAD kernels. Application monorepos appear only where their own modeling implementation is worth studying. The criteria assess engineering substance, not production readiness or uniform code quality.

## Criteria legend

- **C1 — Correctness:** difficult geometric/topological invariants, numerical semantics, concurrency, degenerate inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable representations and algorithms supporting multiple modeling tasks.
- **C3 — Performance:** concrete computational or memory constraints addressed through an understandable architecture.
- **C4 — Evolution:** evidence across years of compatibility management, testing, or deliberate control of complexity. Repository age alone does not qualify.

## Trimmed-surface B-rep kernels and representations

### 1. [Open-Cascade-SAS/OCCT](https://github.com/Open-Cascade-SAS/OCCT)

**Language/role:** C++; general-purpose surface and solid modeling platform.

Study how an industrial-scale kernel shares intersection computation across several modeling operations. Its Boolean architecture separates an intersection phase, a shared intermediate data structure, and a result-building phase. General Fuse supplies the foundation for Boolean, splitter, and section operations, including history information for downstream naming. The [Boolean operations specification](https://occt3d.com/dev/doc/overview/html/specification__boolean_operations.html) explains the implementation rather than merely listing API functions.

- **C1:** The specification explains how near-coincident entities, imported tolerances, gaps, and narrow residual faces affect validity. Fuzzy operations explicitly add a user-selected tolerance; this is a numerical modeling decision, not an unconditional robustness guarantee.
- **C2:** Reusing the intersection phase while changing the construction phase supports multiple operators over the same shape abstractions.
- **C3:** The documented gluing optimization skips expensive intersection classes when inputs satisfy coincidence preconditions. The documentation also states that those preconditions are the caller's responsibility.

**Entry point:** the specification above, especially “Parts of algorithms,” “Fuzzy Boolean Operation,” and “Gluing Operation.”

### 2. [sandialabs/sgm](https://github.com/sandialabs/sgm)

**Language/role:** C++; reduced-topology B-rep kernel for engineering geometry. **Archived on 2026-08-03**, as indicated by the repository banner.

SGM is a useful smaller counterpart to OCCT: its repository separates bodies, volumes, faces, edges, curves, surfaces, interrogation, faceting, and file handling. It exposes modeling and query operations without requiring the Qt viewer. The particularly instructive component is its [entity checker](https://raw.githubusercontent.com/sandialabs/sgm/master/Source/Checker.cpp), which makes otherwise implicit consistency requirements visible.

- **C1:** Checks verify reciprocal owner/child relationships, body-to-volume back references, out-of-range mesh indices, and degenerate segments and triangles. Diagnostic strings identify the affected entities.
- **C2:** A common entity hierarchy supports both analytic/NURBS geometry and operations such as closest-point queries, intersections, Booleans, and faceting; see the [source organization](https://github.com/sandialabs/sgm/tree/master/Source).

**Entry points:** `Source/Checker.cpp` and the `Source` tree above. Retain it as an architectural and historical study target; archival status precludes an active-maintenance claim.

### 3. [solvespace/solvespace](https://github.com/solvespace/solvespace)

**Language/role:** C++; native rational-surface modeling subsystem inside the SolveSpace CAD application. Counted once for that subsystem, not for the GUI or constraint solver.

The [surface Boolean implementation](https://raw.githubusercontent.com/solvespace/solvespace/master/src/srf/boolean.cpp) is unusually informative about the practical interaction between exact curves, piecewise-linear approximations, trim curves, and classification. Engineers can follow how shell intersections become split curves and how the resulting regions are retained for union, difference, or intersection.

- **C1:** Comments and implementation distinguish actual trim endpoints from endpoints of extended intersection curves, because splitting at the latter can create T-junctions and naked edges. Refinement avoids singular three-surface systems and removes duplicate split points that would create zero-length edges.
- **C3:** Curve splitting runs in an OpenMP parallel loop, with a critical section around shared result insertion and identifier assignment. Bounding checks reject irrelevant vertex/curve candidates before projection.

**Entry point:** `src/srf/boolean.cpp`, particularly `FindVertsOnCurve`, `MakeCopySplitAgainst`, `CopyCurvesSplitAgainst`, and `KeepRegion`. The subsystem remains coupled to application settings; it is not presented as a drop-in standalone SDK.

### 4. [FriendsOfCADability/CADability](https://github.com/FriendsOfCADability/CADability)

**Language/role:** C#/.NET; independently implemented CAD geometry library with a separable Windows Forms application layer.

This provides a substantial managed-language alternative to the C++ and Rust implementations. The repository describes the division between the geometry/algorithm library, platform UI library, and thin application. Its [edge implementation](https://raw.githubusercontent.com/FriendsOfCADability/CADability/master/CADability/Edge.cs) is a concrete starting point for studying how a B-rep reconciles model-space geometry with surface parameter space.

- **C1:** An edge carries a 3D curve, references to adjoining faces, and corresponding 2D curves. STEP import descriptors handle seams and splitting a single imported edge across periodic surfaces, while sharing the list of derived edges across descriptor copies.
- **C2:** The [geometry source tree](https://github.com/FriendsOfCADability/CADability/tree/master/CADability) includes curve and surface interfaces, analytic and NURBS implementations, faces/shells/solids, intersection code, and modeling operations. These belong to the reusable library rather than exclusively to UI actions.

**Entry points:** `CADability/Edge.cs` and the geometry source tree. Some implementation commentary is in German.

### 5. [ricosjp/truck](https://github.com/ricosjp/truck)

**Language/role:** Rust; modular CAD kernel with geometry, topology, meshing, shape operations, and STEP support.

Truck is particularly useful for studying the difference between geometric equality and topological identity. Its [topology implementation and module documentation](https://raw.githubusercontent.com/ricosjp/truck/master/truck-topology/src/lib.rs) define vertices, edges, wires, faces, shells, and solids parameterized over geometry types. Topology can even be constructed with empty geometry payloads.

- **C1:** Distinct construction creates distinct entity identities even when coordinates or endpoints match. Reversing an edge or face changes orientation while retaining the underlying identity. Face boundaries and solid shells have explicit closure/orientation requirements, with checked and unchecked construction paths.
- **C2:** Generic topology and separate geometric traits permit replacement of geometry implementations without replacing the object graph. The repository's crate decomposition separates modeling, tessellation, rendering, and exchange.

**Entry points:** `truck-topology/src/lib.rs` above and the [published topology API](https://docs.rs/truck-topology/latest/truck_topology/). Read versioned API documentation alongside the source: published crates and the default branch can differ.

### 6. [hannobraun/fornjot](https://github.com/hannobraun/fornjot)

**Language/role:** Rust; experimental B-rep kernel. **Shut down and archived on 2026-06-19**; the README explicitly says its goals were not reached.

Fornjot merits inclusion as a substantive design experiment, not as a production recommendation. The [core design documentation](https://docs.rs/fj-core/latest/fj_core/) discusses why inferring incidence from epsilon comparisons is problematic and instead requires geometric relationships to be expressed explicitly.

- **C1:** Shared vertices and incidence with curves or surfaces are semantic relationships that the kernel seeks to validate, rather than coincidences inferred solely from coordinates. The documentation explicitly acknowledges incomplete validation and explains the remaining role of tolerances.
- **C2:** The core separates objects, geometry, loosely coupled layers, queries, operations, validation, and append-only storage. Other crates handle mathematical primitives, interoperability, export, and viewing.

**Entry points:** the `fj-core` documentation above and the [mainline crates](https://github.com/hannobraun/fornjot/tree/main/crates). The repository distinguishes this mainline from later experiments; the published 0.49.0 design documentation should not be mistaken for a description of every experiment.

### 7. [andymai/brepkit](https://github.com/andymai/brepkit)

**Language/role:** Rust, with WebAssembly/TypeScript integration; developing analytic/NURBS B-rep kernel.

This newer project provides a contrasting ownership design: entities live in arenas and are referenced by typed IDs. Its [topology module](https://raw.githubusercontent.com/andymai/brepkit/main/crates/topology/src/lib.rs) explains the separation of topology from geometry and the consequences for borrowing, traversal, analytic surface variants, and cavity shells.

- **C1:** The [math module](https://raw.githubusercontent.com/andymai/brepkit/main/crates/math/src/lib.rs) distinguishes tolerance-based measurements from filtered orientation predicates. Topology documentation separately warns that traversing only a solid's outer shell silently omits cavity faces and corrupts measurements.
- **C2:** Geometry, topology, Boolean construction, healing, checks, higher-level operations, and exchange occupy distinct workspace layers. Analytic curves/surfaces remain distinct variants instead of immediately becoming generic splines.
- **C3:** Arena handles avoid reference-counting overhead and analytic intersections provide specialized computational paths.

**Entry points:** the two module sources above. The README documents mesh fallback for difficult Booleans, with no watertightness guarantee on that fallback, and experimental IGES support. Its feature ratings and performance comparisons are project claims, not independently validated here; no C4 claim is made.

### 8. [mcneel/opennurbs](https://github.com/mcneel/opennurbs)

**Language/role:** C++; geometric representations and 3DM interchange, including rich B-rep data structures. This is not a claim that Rhino's complete modeling engine is open source.

The [B-rep header](https://github.com/mcneel/opennurbs/blob/8.x/opennurbs_brep.h) is a detailed representation specification. It exposes the relationship between underlying geometry and topological uses, including trim curves whose orientation or parameter domain differs from the referenced curve.

- **C1:** Trim types distinguish boundaries, mated trims, seams, and singular situations. Validation is staged: topology must be valid before geometry checks, and both must pass before tolerance/flag checks. These ordering requirements are documented API preconditions.
- **C2:** Curve proxies and the vertex/edge/trim/loop/face structure support shared geometry with different topological roles, rather than flattening each face into an independent surface patch. The same representation serves interchange and geometry inspection.

**Entry point:** `opennurbs_brep.h`, especially `ON_BrepTrim` and `ON_Brep` validation methods. It is valuable for representation and interchange engineering even when a separate kernel must perform advanced modeling operations.

## Spline and composite-surface modeling foundations

### 9. [SINTEF-Geometry/GoTools](https://github.com/SINTEF-Geometry/GoTools)

**Language/role:** C++; modular geometry toolkit, including spline geometry, intersections, trimmed/composite surfaces, topology, and volumetric modeling.

GoTools is a strong study target for the transition from mathematical surfaces to connected surface models. The [SurfaceModel interface](https://raw.githubusercontent.com/SINTEF-Geometry/GoTools/master/compositemodel/include/GoTools/compositemodel/SurfaceModel.h) represents a shell or surface set with topology and makes several distinct tolerances explicit.

- **C1:** Approximation error, positional gap, adjacency distance, small normal-angle discontinuities, and intentional sharp bends are separate inputs. This avoids treating all continuity and connection questions as a single epsilon test.
- **C2:** `SurfaceModel` builds on `CompositeModel`, connects face and parametric-surface abstractions, and offers geometry evaluation and topology-aware access. The surrounding modules extend the same foundation toward quality analysis, parameterization, intersections, and trivariate models.

**Entry points:** `SurfaceModel.h` above and the [installation/testing guide](https://github.com/SINTEF-Geometry/GoTools/blob/master/INSTALL), which documents separately selectable modules and unit, integration, and acceptance test labels. SISL is also included as a submodule, but GoTools' composite-model implementation is distinct from SISL's numerical routines.

### 10. [SINTEF-Geometry/SISL](https://github.com/SINTEF-Geometry/SISL)

**Language/role:** C; reusable B-spline/NURBS curve and surface algorithms, rather than a complete solid-topology kernel.

SISL exposes the low-level numerical layer that larger modelers need. The [surface/surface intersection routine `s1859`](https://github.com/SINTEF-Geometry/SISL/blob/master/src/s1859.c) describes subdivision followed by iteration, separates computational and geometric resolution, and explains the representation returned to callers.

- **C1:** Results distinguish isolated intersection points from intersection curves in both parameter domains. Degenerate inputs can cause a point-like result to be represented as a curve, and status codes distinguish errors, warnings, and success. Understanding these contracts matters when turning numerical intersections into topology.
- **C2:** Curve/surface data and intersection result structures form a reusable procedural interface. The [closest-points example](https://github.com/SINTEF-Geometry/SISL/blob/master/examples/example08.cpp) demonstrates construction, closest-point queries, evaluation, tolerance selection, status handling, and explicit ownership cleanup.

**Entry points:** `src/s1859.c` and `examples/example08.cpp`. The historical routine comments are informative, but are not used alone to claim present maintenance or C4.

### 11. [pboyer/verb](https://github.com/pboyer/verb)

**Language/role:** Haxe, targeting JavaScript and other platforms; reusable NURBS geometry library.

Verb separates user-facing immutable curve objects from lower-level evaluation data and algorithms. [NurbsCurve](https://github.com/pboyer/verb/blob/master/src/verb/geom/NurbsCurve.hx) exposes evaluation, derivatives, closest points, lengths, transformations, and asynchronous counterparts that dispatch work through a shared execution layer.

- **C1:** The [validation module](https://raw.githubusercontent.com/pboyer/verb/master/src/verb/eval/Check.hx) checks relationships between degree, control-point count, and knot-vector length, as well as knot ordering and endpoint multiplicities. It explicitly warns that low-level evaluators assume callers have validated their data.
- **C2:** Immutable geometry objects, serializable data, and separate evaluation/analysis/modification modules support several modeling operations without one monolithic object implementation.
- **C3:** Validation is separated from performance-sensitive evaluation, while asynchronous methods provide a route to background computation.

**Entry points:** `NurbsCurve.hx` and `Check.hx`. This is a curve/surface foundation; it should not be inferred to provide a complete manifold B-rep Boolean engine.

### 12. [orbingol/NURBS-Python](https://github.com/orbingol/NURBS-Python)

**Language/role:** Python; the `geomdl` B-spline/NURBS modeling library, implemented in Python rather than generated bindings to another kernel.

The [evaluator implementation](https://raw.githubusercontent.com/orbingol/NURBS-Python/5.x/geomdl/evaluators.py) is approachable without being a toy: abstract evaluators consume geometry data, concrete curve/surface/volume evaluators implement algorithms, and rational variants build on homogeneous-coordinate evaluation.

- **C1:** Rational evaluation includes the extra homogeneous dimension and weight division; derivative computation must respect spline degree and requested derivative order. The source identifies the corresponding algorithms from *The NURBS Book*, making numerical behavior traceable.
- **C2:** Evaluator strategies and injected knot-span search functions separate mathematical geometry from algorithm selection. This is useful for studying how to make a numerical modeling API extensible without requiring each shape class to own every algorithm.

**Entry point:** `geomdl/evaluators.py`, beginning with `AbstractEvaluator`, `CurveEvaluator`, and `CurveEvaluatorRational`. Its scope is spline geometry and associated modeling operations, not full solid B-rep topology or general solid Booleans.

## Polyhedral boundary representations and solid modeling

### 13. [CGAL/cgal](https://github.com/CGAL/cgal)

**Language/role:** C++; computational geometry monorepo. Included specifically for the `Nef_3` B-rep solid-modeling subsystem, not indiscriminately for every CGAL package.

The [3D Nef polyhedra manual](https://doc.cgal.org/latest/Nef_3/index.html) explains a representation that supports configurations beyond orientable manifold surface meshes. It combines local spherical maps around vertices with global edges, facets, and volumes.

- **C1:** Ordinary manifold B-reps are not closed under every Boolean operation. Nef polyhedra explicitly model non-manifold and lower-dimensional results, open/closed set membership, and distinctions between ordinary and regularized operations.
- **C2:** The representation supports union, intersection, difference, complement, boundary, interior, closure, point location, transformations, and connectivity inspection. Local-neighborhood information and global connectivity are separate but coordinated abstractions.

**Entry point:** the `Nef_3` manual, particularly its representation discussion and definitions. This is polyhedral geometry; it does not supply OCCT-style trimmed NURBS faces. It is especially useful when the meaning of the represented set is as important as a triangulated surface.

### 14. [elalish/manifold](https://github.com/elalish/manifold)

**Language/role:** C++; solid modeling with manifold triangle meshes, with language bindings and a 2D cross-section subsystem.

Study the explicit topology contract and the relationship between reliable construction and efficient candidate generation. The [library documentation](https://manifoldcad.org/docs/html/index.html) states that imported meshes must satisfy manifoldness requirements and explains error status, vertex properties, face provenance, and optional parallel execution.

- **C1:** Manifoldness is an input/output contract rather than a consequence of visually plausible triangles. The [Boolean2 design](https://raw.githubusercontent.com/elalish/manifold/master/docs/Boolean2.md) gives a concrete robustness case study: independent local crossing decisions can disagree in dense near-concurrent arrangements, motivating coordinated sweep order and winding classification.
- **C2:** The solid and cross-section APIs combine Boolean construction with property preservation, refinement, and shape creation.
- **C3:** TBB parallel paths coexist with serial execution for small workloads. Boolean2 separates broad-phase candidate generation, incidence splitting, sweep processing, and output construction, with BVH use for larger inputs.

**Entry points:** the library documentation and `docs/Boolean2.md`. The latter describes the 2D subsystem specifically; it is not presented as the implementation of the 3D Boolean algorithm.

### 15. [nicklockwood/Euclid](https://github.com/nicklockwood/Euclid)

**Language/role:** Swift; reusable polygonal solid modeling through paths, extrusion, lofting, and CSG.

Euclid supplies a substantial implementation in a language less commonly associated with geometry kernels. Its [BSP source](https://raw.githubusercontent.com/nicklockwood/Euclid/main/Sources/BSP.swift) exposes polygon classification, explicit traversal state, convex-path specialization, deterministic polygon shuffling, and cancellation checks.

- **C1:** Plane-side classification, polygon splitting, winding, and watertightness interact across operations. The changelog records concrete failures involving self-intersections, compound paths, non-planar boundaries, and degenerate inputs.
- **C3:** Deterministic shuffling reduces unfavorable splitting behavior, convex input has a specialized construction path, and long operations poll for cancellation.
- **C4:** The [changelog](https://raw.githubusercontent.com/nicklockwood/Euclid/main/CHANGELOG.md) documents evolution from at least 2022 through 2026: compatibility tests, `Sendable` adoption, concurrency changes, deprecation/removal cycles, and regression fixes. These establish more than simple repository age.

**Entry points:** `Sources/BSP.swift` and `CHANGELOG.md`. Its surfaces are polygonal; it is not an analytic-surface B-rep kernel.

### 16. [jscad/OpenJSCAD.org](https://github.com/jscad/OpenJSCAD.org)

**Language/role:** JavaScript, with TypeScript declarations; monorepo included specifically for the `packages/modeling` geometry library.

The most interesting study target is the interaction between BSP clipping and a separate hierarchy that remembers polygon splits. [PolygonTreeNode](https://raw.githubusercontent.com/JSCAD/OpenJSCAD.org/master/packages/modeling/src/operations/booleans/trees/PolygonTreeNode.js) can return the original polygon when all of its fragments survive, but invalidates ancestors when a fragment is removed.

- **C1:** The split hierarchy preserves the distinction between a complete original polygon and its surviving fragments. Root-only insertion, ancestor invalidation, and front/back coplanar handling enforce structural assumptions during Boolean operations.
- **C2:** `packages/modeling` separates geometry representations, mathematical primitives, measurements, primitive construction, and operations from browser and command-line front ends.
- **C3:** [Union implementation](https://raw.githubusercontent.com/JSCAD/OpenJSCAD.org/master/packages/modeling/src/operations/booleans/unionGeom3Sub.js) bypasses clipping for non-overlapping inputs. Polygon splitting uses a bounding-sphere rejection, while deferred removal avoids repeated array splicing.

**Entry points:** `PolygonTreeNode.js` and `unionGeom3Sub.js`. These are actual modeling implementations, not an adapter around OCCT or Manifold.

## A contrasting implicit modeling kernel

### 17. [libfive/libfive](https://github.com/libfive/libfive)

**Language/role:** C++ with a C API and Scheme/Python interfaces; functional-representation solid modeling. Included under geometric modeling kernels, explicitly **not** as a stored trimmed-surface B-rep library.

Libfive represents a solid with a scalar function and derives a boundary mesh for output. It is useful for comparing the architecture of numerical expression evaluation with explicit face/edge topology. The [interval evaluator](https://raw.githubusercontent.com/libfive/libfive/master/libfive/include/libfive/eval/eval_interval.hpp) and [evaluation tape](https://raw.githubusercontent.com/libfive/libfive/master/libfive/include/libfive/eval/tape.hpp) reveal the optimization mechanism.

- **C1:** A specialized tape is valid only for its associated region. `getBase` walks back to a suitable parent when evaluation moves outside that region, including dual-contouring points outside their originating cells. This is a concrete correctness constraint on optimization reuse.
- **C2:** Expression trees, evaluator variants, tape storage, and external oracle contexts are separate abstractions; the repository also separates the core kernel, shape library, bindings, and Studio UI.
- **C3:** Interval evaluation can shorten the tape, discard inactive branches, and recognize terminal tapes with no remaining selective clauses, reducing repeated evaluation work.

**Entry points:** `eval_interval.hpp` and `tape.hpp`. The inclusion supplies a useful alternative modeling architecture without implying analytic B-rep interoperability.

## Search coverage and limitations

Discovery used more than six distinct formulations, including “boundary representation geometric modeling kernel open source,” Rust CAD kernels, C++ NURBS/B-rep libraries, SGM/sgCore, EGADS/Engineering Sketch Pad, SINTEF spline toolkits, JavaScript solid Booleans, C# CADability, Swift CSG, and implicit solid-modeling kernels. Follow-up queries increasingly returned the same established projects, wrappers, and recent small prototypes. Verification opened repository pages and additional primary API documentation, design documents, source files, or changelogs. Direct public source reads supplemented GitHub pages whose HTML did not expose their code.

The selection spans C, C++, Rust, C#, Python, Haxe/JavaScript, JavaScript, and Swift; commercial CAD, scientific geometry, independent library, browser, and code-driven modeling communities; and several representation/ownership strategies. Study recommendations and criterion assignments are judgments grounded in the cited implementation contracts, not measurements of correctness or performance. No candidate code was run, no dependencies were installed, and no benchmark or complete regression suite was independently reproduced. Except for explicitly documented historical status and dated evolution evidence, no blanket active-maintenance claim is made.

Important exclusions and boundaries:

- Proprietary kernels such as Parasolid and ACIS, and sgCore search results without a verified substantive public implementation, were outside the GitHub-source requirement.
- OCCT bindings, generated wrappers, CAD front ends, B-rep machine-learning datasets/models, and tutorial kernels were not added merely for breadth. JSketcher's current README says solid Booleans use OCCT; that frontend was not counted as another independent Boolean kernel.
- The inspected Carve repository identified itself as a fork of the former Google Code project. Its status as a canonical or independently evolved implementation was not established sufficiently for this selection. EGADS/ESP search results included third-party distributions and reorganizations; no additional entry was made without establishing the appropriate official GitHub source or mirror.
- BRL-CAD's `libnmg` is substantively relevant: its [official topology documentation](https://brlcad.org/docs/api/d2/d9d/group__nmg__topology.html) describes entity/use separation and non-manifold boundary topology. However, canonical-root and direct-source fetches repeatedly failed during this pass despite accessible indexed repository-tree material. It was excluded from the retained count rather than treating that inconsistent access as fully successful verification.
- SGM and Fornjot are deliberately retained as substantive historical codebases and clearly labeled. Newer brepkit is included for inspectable architecture, with its documented unsupported/fallback behavior stated, and without attributing years of evolution to it.

This is a selection guide to specific engineering lessons. Inclusion does not mean every operation is reliable on arbitrary input, that the APIs are interchangeable, or that every component is exemplary.
