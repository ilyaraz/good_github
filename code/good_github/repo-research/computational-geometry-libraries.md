# Computational geometry libraries

Research date: 2026-10-09

This report selects 24 GitHub repositories implementing reusable geometric algorithms and data structures: numerical kernels, planar and spherical topology, clipping, hulls, triangulations, Voronoi cells, and mesh processing. It includes both broad toolkits and focused algorithm libraries. Native implementations descended from JTS are identified as related engineering lineages, not independent algorithm inventions. Monorepositories and multilingual implementations count once. The emphasis is what an experienced engineer can learn from implementation choices, contracts, and failure handling; inclusion does not certify every component or every input regime.

Criteria legend:

- **C1 — Difficult correctness:** geometric or topological invariants, numerical semantics, degeneracies, concurrency, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and representations supporting multiple algorithms or application domains.
- **C3 — Performance with structure:** concrete approaches to memory, indexing, computational cost, or parallelism with an understandable organization.
- **C4 — Sustained evolution:** documented development across years together with compatibility, testing, or complexity management. Age and stars alone do not qualify.

## General kernels and geometry toolkits

### 1. [CGAL/cgal](https://github.com/CGAL/cgal)

**Language/role:** C++; comprehensive computational geometry toolkit. Study the boundary between arithmetic, geometric predicates, constructions, and higher-level algorithms. Relevant subsystems include the kernels, triangulations, arrangements, Boolean operations, and mesh-processing packages; these are one repository, not separate selections.

- **C1:** The robustness manual explains how contradictory floating-point decisions can invalidate algorithm control flow, and distinguishes exact predicate results from constructed coordinates. This makes numerical contracts an architectural concern rather than an incidental epsilon choice.
- **C2:** Kernel primitives can serve as traits for algorithms and data structures, allowing higher layers to reuse geometry while changing the numerical representation.
- **C3:** Arithmetic filters, including interval arithmetic, handle reliable cases cheaply before more expensive exact computation is needed. These mechanisms and their assumptions are explained in the [robustness design manual](https://doc.cgal.org/latest/Manual/devman_robustness.html).

**Entry points:** the robustness manual above and the repository's package-layout explanation. Kernel selection remains application dependent; a robustness-oriented library does not make every kernel choice exact.

### 2. [boostorg/geometry](https://github.com/boostorg/geometry)

**Language/role:** C++; generic geometry algorithms and spatial indexing. Particularly useful for studying how to retrofit reusable algorithms onto application-owned data types.

- **C2:** Its [design rationale](https://www.boost.org/doc/libs/latest/libs/geometry/doc/html/geometry/design.html) develops traits for access, dimension, coordinate type, and coordinate system, then combines tag dispatch with replaceable strategies. The abstraction supports different representations and geometric operations without imposing a single point class.
- **C3:** The design connects compile-time dimension handling and comparable distances to avoiding unnecessary runtime work. The [R-tree implementation](https://github.com/boostorg/geometry/blob/develop/include/boost/geometry/index/rtree.hpp) exposes linear, quadratic, and R*-style balancing policies, runtime or compile-time parameters, and configurable value/indexable handling.

**Entry points:** the design rationale and `rtree.hpp`. Read the rationale as a design explanation, not a blanket accuracy guarantee for every geographic strategy.

### 3. [BrunoLevy/geogram](https://github.com/BrunoLevy/geogram)

**Language/role:** C++; geometric predicates, triangulations, mesh representations, reconstruction, and remeshing. Study how a research-oriented geometry toolkit shares numerical machinery across higher-level algorithms.

- **C1:** The [predicate interface](https://raw.githubusercontent.com/BrunoLevy/geogram/main/src/lib/geogram/numerics/predicates.h) documents arithmetic filters, expansion arithmetic, and simulation of simplicity. Its symbolic-perturbation modes distinguish fixed-address points from dynamically generated points ordered lexicographically—an unusually concrete example of storage assumptions affecting geometric correctness.
- **C2:** The same interface includes orientation, in-sphere, lifted-point, and bisector-side predicates, including predicates on implicitly defined intersections. These support the repository's triangulation and restricted-Voronoi machinery rather than a single demo.
- **C3:** Filtered exact predicates concentrate expensive arithmetic in uncertain cases while preserving explicit preconditions and sign conventions.

**Entry points:** `predicates.h` above and the [programmer's reference](https://brunolevy.github.io/geogram/).

### 4. [georust/geo](https://github.com/georust/geo)

**Language/role:** Rust; geometry primitives and algorithms for planar and geographic workloads. Study the `geo` algorithms and their relationship to the shared `geo-types` model in this repository.

- **C2:** The [API guide](https://docs.rs/geo/latest/geo/) separates primitive geometry types from algorithm traits and metric spaces. Euclidean, spherical, geodesic, and rhumb-line measurements have distinct semantics; the same model supports topology, simplification, measurements, and transformations.
- **C3:** Its [monotone-chain subsystem](https://docs.rs/geo/latest/geo/algorithm/monotone_chain/index.html) partitions linestring segments so segments within a chain need not be tested against each other. Endpoint envelopes permit binary subdivision when comparing chains, reducing unnecessary intersection tests while exposing prepared geometry types.

**Entry points:** the API guide and monotone-chain module. Some algorithms intentionally compose external engines, including iOverlay; this selection is for the broader Rust geometry architecture and native algorithms, not crediting dependencies as original implementations.

## Planar topology, polygon overlay, and curved contours

### 5. [locationtech/jts](https://github.com/locationtech/jts)

**Language/role:** Java; planar vector geometry and topology engine. Study the distinction between a geometry object model, noding, precision policy, and the semantics of Boolean results.

- **C1:** [OverlayNG](https://locationtech.github.io/jts/javadoc/org/locationtech/jts/operation/overlayng/OverlayNG.html) chooses snap-rounding noding for fixed precision and indexed noding for floating precision. It explicitly documents robustness limits, possible topology exceptions, and how strict mode excludes lower-dimensional remnants from collapses.
- **C2:** Overlay operation, precision model, and noder are independently selectable. The same machinery implements union, intersection, difference, and symmetric difference; custom noders allow specialized operations to reuse the overlay framework.
- **C3:** The documented custom-noder extension supports faster handling of special input classes such as coverages without redesigning the complete operation.

**Entry point:** the OverlayNG API/design documentation. The repository also contains a geometry test corpus and TestBuilder, making failure cases inspectable rather than hiding them behind a Boolean API.

### 6. [libgeos/geos](https://github.com/libgeos/geos)

**Language/role:** C++ implementation with a C API; a substantive native JTS descendant used as a geometry engine by other systems. Study the additional engineering needed to expose complex C++ geometry through a long-lived foreign-function boundary.

- **C1:** The [C API guide](https://libgeos.org/usage/c_api/) explains reentrant operations with per-thread contexts, error callbacks, and explicit ownership/destruction. Numerical geometry must coexist with correct lifetime and concurrency behavior.
- **C2:** Geometry, coordinate-sequence, prepared-geometry, and spatial-index interfaces support applications beyond a single GIS front end.
- **C4:** The repository promises stability for the C API while explicitly declining equivalent C++ API/ABI guarantees. Its [release history](https://raw.githubusercontent.com/libgeos/geos/main/NEWS.md), including 2024–2026 releases, records numerical repairs, prepared-predicate improvements, and changes to empty/invalid-input semantics. This supports sustained compatibility management, not merely longevity.

**Entry points:** C API programming guide and `NEWS.md`. Entries marked as future/unreleased in the changelog are not treated as released capabilities.

### 7. [NetTopologySuite/NetTopologySuite](https://github.com/NetTopologySuite/NetTopologySuite)

**Language/role:** C#/.NET; native geometry and topology implementation descended from JTS. It is useful for examining numerical algorithm translation and failure recovery in managed code, rather than as an independent origin of the overlay algorithm.

- **C1:** [OverlayNGRobust.cs](https://github.com/NetTopologySuite/NetTopologySuite/blob/develop/src/NetTopologySuite/Operation/OverlayNG/OverlayNGRobust.cs) first attempts floating-precision overlay with validation, then retries snapping strategies with increasing tolerances. Self-snapping can remove narrow artifacts; exhausted recovery preserves failure instead of silently returning an arbitrary geometry.
- **C2:** The implementation composes `Geometry`, `OverlayNG`, precision policies, and configurable noders. Self-snapping itself reuses union and strict-result semantics, illustrating reusable operations inside a recovery pipeline.

**Entry point:** `OverlayNGRobust.cs`, including its comments and helper methods. Increasing snap tolerance can change coordinates; robustness recovery is a defined tradeoff, not exact reconstruction of all original coordinates.

### 8. [peterstace/simplefeatures](https://github.com/peterstace/simplefeatures)

**Language/role:** Go; native Simple Features geometry model, algorithms, and R-tree. The repository also has optional CGO wrappers, but the selection concerns its native `geom` and `rtree` packages. Current overlay, buffer, relate, and prepared-geometry operations use a Go port of JTS.

- **C2:** Separate geometry, cartography, and indexing packages support reuse without requiring the optional C dependencies. The geometry API combines validation, topological relations, measurements, serialization, and constructive operations.
- **C3:** The [R-tree API and implementation documentation](https://pkg.go.dev/github.com/peterstace/simplefeatures/rtree) separates stored bounding boxes/record IDs from application records. Bulk loading minimizes node overlap; range and distance-prioritized searches support callbacks and early stopping.

**Entry points:** the native-package descriptions in the repository and the R-tree documentation. It offers a useful contrast between a Go-facing object model, a ported topology engine, and a small independently reusable spatial index.

### 9. [AngusJohnson/Clipper2](https://github.com/AngusJohnson/Clipper2)

**Language/role:** C++, C#, and Delphi; polygon clipping and offsetting, with parallel implementations counted once. Study explicit finite-precision policy across language implementations.

- **C1:** The [technical overview](https://www.angusj.com/clipper2/Docs/Overview.htm) explains that both integer and double-facing clipping classes use integer coordinates internally. Scaling, overflow headroom, deterioration at extreme coordinate magnitudes, and caller-owned range checks are documented rather than left implicit.
- **C2:** Paths, clipping classes, fill rules, open/closed-path handling, and offset operations form a reusable polygon toolkit. Output orientation and hole conventions give downstream consumers a concrete contract.

**Entry point:** the overview, especially coordinate ranges and clipping semantics. **Current limitation:** the repository README warns that its triangulation code is buggy. This entry is primarily for clipping/offsetting architecture and does not endorse the newly exposed triangulation subsystem.

### 10. [jbuckmccready/cavalier_contours](https://github.com/jbuckmccready/cavalier_contours)

**Language/role:** Rust; line-and-circular-arc polylines, offsets, intersections, and Boolean operations. The repository describes itself as the expanded Rust continuation of the author's C++ CavalierContours; the old implementation is not counted again.

- **C2:** The [polyline module](https://docs.rs/cavalier_contours/latest/cavalier_contours/polyline/index.html) separates read-only, mutable, and creatable polyline traits. Vertices encode arc bulge as well as position, while intersection types distinguish isolated crossings from overlapping spans.
- **C3:** `PlineView` borrows a portion of a source polyline without copying. The [PlineSource API](https://docs.rs/cavalier_contours/latest/cavalier_contours/polyline/trait.PlineSource.html) exposes precise and approximate AABB indexes alongside operations and configurable variants, making storage reuse and spatial acceleration visible in the design.

**Entry points:** those two API pages. Circular arcs are represented directly, but the repository documents limits such as supported bulge range and rounded offset joins; it is not an arbitrary spline kernel.

### 11. [iShape-Rust/iOverlay](https://github.com/iShape-Rust/iOverlay)

**Language/role:** Rust; polygon overlay, clipping, and related operations. Study an integer geometry engine with separate floating-point adapters and reusable preprocessing.

- **C1:** The repository's coordinate-limit documentation derives overflow headroom and distinguishes unchecked integer ranges from checked fixed-scale float conversions. It also specifies contour orientation and valid-polygon requirements for offsetting; support for self-intersecting overlay input does not imply unrestricted offset input.
- **C2:** The [Overlay API](https://docs.rs/i_overlay/latest/i_overlay/core/overlay/struct.Overlay.html) separates geometry ingestion, fill rules, Boolean rules, and an intermediate graph used to extract results.
- **C3:** `build_graph_view` exposes preprocessed input for graph-based operations, while the single-operation path constructs only necessary links. This is a concrete separation between reusable preprocessing and a cheaper one-shot execution path.

**Entry points:** the repository's numerical-limits sections and the Overlay API. Its use by `geo` is a dependency relationship, not an additional independent implementation of `geo`'s Boolean operations.

## Hulls, triangulation, tessellation, and Voronoi algorithms

### 12. [qhull/qhull](https://github.com/qhull/qhull)

**Language/role:** C with C++ interfaces; convex hulls, Delaunay/Voronoi structures, and halfspace intersections in multiple dimensions. Study a numerical architecture that accepts finite precision and exposes its consequences.

- **C1:** The [precision manual](https://github.com/qhull/qhull/blob/master/html/qh-impre.htm) explains merged facets, thick facets bounded by inner/outer planes, and randomly joggled input. It distinguishes cocircular/cospherical input and triangulated output, and discusses normalization and precision failures.
- **C2:** Related structures are built on a shared hull engine rather than independent one-off implementations. The repository includes reentrant C and C++ library interfaces in addition to command-line applications.

**Entry points:** the precision manual and repository layout/build documentation. The manual explicitly treats bounds and success rates empirically in relevant places; it should not be read as a universal exact-arithmetic guarantee. No claim of frequent current releases is made here.

### 13. [artem-ogre/CDT](https://github.com/artem-ogre/CDT)

**Language/role:** C++; constrained and conforming Delaunay triangulation. Study incremental triangulation with explicit handling of constraints, holes, insertion order, and refinement limits.

- **C1:** The repository documents robust orientation/in-circle predicates, points on edges, overlapping edges, and optional resolution of intersecting constraints. The [Triangulation API](https://artem-ogre.github.io/CDT/classCDT_1_1Triangulation.html) describes depth peeling through outer boundaries, holes, and nested islands, including overlapping boundaries.
- **C2:** Coordinate and near-point-locator template parameters, custom point/edge inputs, and separate finalization operations expose reusable algorithm components.
- **C3:** The implementation explanation connects a nearest-point kd-tree to triangle walking and uses spatially ordered initial insertion plus randomized subsequent insertion to avoid poor insertion sequences.

**Entry points:** the repository's algorithm explanation and `Triangulation` documentation. Refinement has insertion budgets and minimum-edge limits, and cannot repair an intrinsically sharp input corner by promising an impossible angle bound.

### 14. [Stoeoef/spade](https://github.com/Stoeoef/spade)

**Language/role:** Rust; dynamic Delaunay and constrained Delaunay triangulation, Voronoi extraction, and interpolation. Study how an adjacency-rich data structure is exposed under Rust borrowing rules.

- **C1:** The [crate documentation](https://docs.rs/spade/latest/spade/) specifies exact predicate evaluation, coordinate validation, and underflow mitigation. Robust predicates have an input domain; they do not remove the need to validate magnitudes.
- **C2:** The [handle design](https://docs.rs/spade/latest/spade/handles/index.html) separates immutable reference handles from fixed index handles used around mutations. Vertices, faces, and directed/undirected edges support traversal and attached application data.
- **C3:** Vector-backed fixed handles and pluggable location hints make memory layout and point-location acceleration explicit. The docs warn that removal can invalidate fixed handles, including changing the element an index identifies.

**Entry points:** crate overview and handle module.

### 15. [mapbox/delaunator](https://github.com/mapbox/delaunator)

**Language/role:** JavaScript; compact planar Delaunay triangulation. Useful for studying a focused library whose output representation is itself the main reusable abstraction.

- **C2:** The [data-structure guide](https://mapbox.github.io/delaunator/) explains paired triangle and halfedge arrays, opposite-edge links, hull sentinels, and traversal. These support adjacency queries and derivation of Voronoi cells without demanding a heavyweight mesh object hierarchy.
- **C3:** The repository API uses typed arrays and supports updating a triangulation while reusing allocated storage. The guide explicitly distinguishes allocation-heavy explanatory code from more efficient flat-array use.
- **C1:** Hull edges have no opposite halfedge; the guide develops boundary-aware traversal and discusses ghost-edge alternatives instead of assuming every vertex has a closed fan.

**Entry points:** the guide and repository API documentation. This is a point-set triangulator, not a constrained polygon meshing engine.

### 16. [mapbox/earcut](https://github.com/mapbox/earcut)

**Language/role:** JavaScript; polygon triangulation for rendering workloads. Study how a compact implementation combines a simple algorithm with targeted spatial acceleration and fallback stages.

- **C1:** The [implementation](https://raw.githubusercontent.com/mapbox/earcut/main/src/earcut.js) maintains circular ring links, removes collinear/coincident points, retries stalled clipping, repairs local intersections, and finally attempts polygon splitting. These are substantive degeneracy and termination concerns.
- **C3:** Z-order indexing narrows candidate point tests for larger polygons; the source also contains a convex-ring fast path and localized filtering around changes. The acceleration remains traceable to separate helpers and explicit ring state.

**Entry point:** `src/earcut.js`. **Contract limitation:** the repository explicitly declines correctness on arbitrary invalid polygons and notes that output can contain T-junctions. It is a valuable performance/correctness tradeoff study, not a guaranteed conforming mesh generator for FEM or navigation.

### 17. [memononen/libtess2](https://github.com/memononen/libtess2)

**Language/role:** C; a substantive refactoring of the GLU tessellator for games and tools. **Maintenance status:** the repository explicitly says it is minimally maintained.

- **C1:** Its [algorithm outline](https://raw.githubusercontent.com/memononen/libtess2/master/alg_outline.md) enumerates edge-dictionary, processed-mesh, and sweep invariants. Numerical intersection errors are handled through topological repairs that restore those invariants; monotone regions are triangulated after the sweep completes.
- **C3:** The repository explains replacement of many small allocations with a bucket allocator, user-supplied allocator support, and operation within a predefined memory region. Its array-oriented API exposes contours, polygons, and connected polygons.

**Entry points:** `alg_outline.md` and the repository's allocator/API explanation. Its distinct memory and interface redesign justifies treating it as more than an unmodified copy of historical GLU code. No benchmark multiplier is adopted as a general performance claim.

### 18. [JuliaGeometry/DelaunayTriangulation.jl](https://github.com/JuliaGeometry/DelaunayTriangulation.jl)

**Language/role:** Julia; planar constrained/weighted triangulations, mesh refinement, and Voronoi/power diagrams. Study a native scientific geometry implementation with unusually extensive mathematical and internal documentation.

- **C1:** The [predicate-kernel manual](https://juliageometry.github.io/DelaunayTriangulation.jl/stable/manual/predicate_kernels/) distinguishes fast, adaptive, and exact kernels, explains collinear/cocircular cases, and provides a validity-checking discussion. Kernel choice and combinatorial correctness are exposed explicitly.
- **C2:** The [manual and API index](https://juliageometry.github.io/DelaunayTriangulation.jl/stable/) covers customizable primitives, boundary representations, ghost vertices, dynamic insertion/deletion, curve-bounded domains, refinement, and dual tessellations on a common triangulation model.

**Entry points:** predicate kernels and the manual's representation/algorithm-internals sections. This is an implementation rather than a wrapper around Qhull or Triangle; its scope is planar triangulation, not unrestricted higher-dimensional meshing.

### 19. [chr1shr/voro](https://github.com/chr1shr/voro)

**Language/role:** C++; Voro++, a three-dimensional cell-based Voronoi library. Study the alternative to computing an entire global Delaunay/Voronoi graph: construct each particle's cell independently.

- **C1:** The [implementation manual](https://math.lbl.gov/voro%2B%2B/doc/refman/) describes a convex-polyhedron graph updated by plane cuts, reciprocal edge relations, and support for higher-order vertices. It explains why an earlier degree-three-only representation failed under floating-point errors and crystalline arrangements.
- **C2:** Cell, particle-container, wall, loop, and `voro_compute` components separate local geometry from boundary conditions, periodicity, and traversal. Cell volume, centroid, surface area, and neighbor information serve particle-analysis workflows.
- **C3:** Cutting exploits convexity for early exits, while the computation layer uses spatial blocks and candidate-processing structures to avoid indiscriminate particle comparisons.

**Entry point:** the class/implementation manual, particularly cell representation and the computation template. The distinctive lesson is local cell construction and topology maintenance, not a generic triangulation API.

## Spherical geometry

### 20. [google/s2geometry](https://github.com/google/s2geometry)

**Language/role:** C++; geometry and spatial indexing on a sphere. Study the interaction between mathematical region semantics, numerical guarantees, and a hierarchical spatial decomposition.

- **C1:** The [architecture overview](https://s2geometry.io/about/overview) explains conservative error bounds, exact predicates, and snap rounding. It also makes boundary inclusion and degeneracy handling explicit, including topology and distance-tolerance contracts for relevant operations.
- **C2:** `S2Shape` allows application-specific storage; shape indexes, queries, regions, and cell coverings form a layered toolkit rather than one fixed geographic feature representation.
- **C3:** Internal unit vectors avoid repeated trigonometry for geodesic edges, and query objects can preserve work across calls. The cell hierarchy supports spatial indexing and approximations of regions.

**Entry point:** the architecture overview. The repository currently states that its 0.x releases do not guarantee API/ABI stability. Spherical modeling is an intentional design choice and should not be mistaken for ellipsoidal geodesy.

## Surface meshes and solid geometry

### 21. [libigl/libigl](https://github.com/libigl/libigl)

**Language/role:** C++; geometry processing on surface meshes. Study the algorithm core—differential operators, parameterization, deformation, distances, and remeshing—rather than the optional viewer.

- **C2:** The [design and tutorial](https://libigl.github.io/tutorial/) uses vertex/face matrices and encapsulated functions instead of imposing a large persistent mesh class. This representation supports composition with Eigen and multiple geometry-processing workflows.
- **C3:** Indexed matrices make connectivity compact and cache-friendly; dense/sparse linear algebra supplies a common execution model. The tutorial explains reusable precomputation in numerical methods and offers a static-library option when header-only compilation is costly.

**Entry point:** the tutorial, starting with design principles and mesh representation, then numerical operators. Some optional functions wrap external libraries, but the repository has substantial original geometry-processing implementations; inclusion does not treat all optional backends as libigl inventions.

### 22. [nmwsharp/geometry-central](https://github.com/nmwsharp/geometry-central)

**Language/role:** C++; surface-mesh data structures and geometric algorithms. Especially valuable for understanding mutable topology, mesh-associated data, and the cost of apparently convenient handles.

- **C1:** The [halfedge internals guide](https://geometry-central.net/surface/surface_mesh/internals/) specifies boundary invariants, connectivity validation, deleted-element markers, and how iterators avoid invalid entries. It explains why an earlier pointer-based design produced invalidation and copying hazards.
- **C2:** Typed element wrappers and mesh-data containers share a mesh representation; registered callbacks keep associated data synchronized during resize and compression.
- **C3:** Contiguous arrays, implicit twin relationships, lazy reallocation, and holes left by deletion support efficient traversal and amortized constant-time updates. Compression is an explicit operation rather than an invisible global reindexing cost.

**Entry point:** the internals guide. It also distinguishes the simpler manifold representation from extra structures needed for general surface meshes.

### 23. [elalish/manifold](https://github.com/elalish/manifold)

**Language/role:** C++; triangle-mesh solid modeling and Boolean operations, with language bindings. Study the separation between exact connectivity and approximate coordinates.

- **C1:** The [algorithm design document](https://github.com/elalish/manifold/wiki/Manifold-Library) defines manifoldness topologically and explains symbolic perturbation, consistent reuse of geometric decisions, and removal of degenerate features. Its manifold-output guarantee is conditional on manifold input; it does not promise arbitrary self-overlap repair or exact geometric coordinates.
- **C2:** Mesh properties, provenance, and import/export representations preserve relationships through Boolean operations. The documented merge information allows duplicated rendering vertices to retain underlying topological identity.
- **C3:** A bounding-volume broad phase reduces candidate triangle pairs before Boolean processing; the project explicitly targets parallel execution. Treat backend details in the older design write-up as historical where they differ from the current build.

**Entry points:** the algorithm design document and current repository overview/build configuration. This is a strong study in defining a useful guarantee precisely enough to implement it.

### 24. [JuliaGeometry/Meshes.jl](https://github.com/JuliaGeometry/Meshes.jl)

**Language/role:** Julia; geometric domains, meshes, topologies, and algorithms shared across scientific applications. Study how geometry, coordinate systems, and connectivity remain separate but composable.

- **C2:** The [mesh documentation](https://juliageometry.github.io/MeshesDocs/stable/domains/meshes/) parameterizes meshes by manifold, coordinate reference system, and topology. Structured grids, general connectivity lists, and boundary/coboundary/adjacency relations share interfaces used by mesh algorithms and sparse operators.
- **C1:** `HalfEdgeTopology` targets orientable two-manifolds and documents orientation handling. `SimpleTopology` intentionally lacks neighborhood relations, making a consequential capability difference explicit instead of silently approximating it.
- **C3:** The halfedge representation uses indexed storage and lookup dictionaries for incidence relations. Consistently oriented input can bypass sorting, while construction accepts an element-count hint to manage allocation.

**Entry points:** mesh/topology documentation and the [general guide](https://juliageometry.github.io/MeshesDocs/stable/). A polygon soup is suitable for some IO/visualization tasks but cannot automatically substitute for a topology supporting neighborhood-dependent algorithms.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations, followed by repository opens and targeted documentation/source reads. Search angles included general robust-predicate kernels; polygon clipping and triangulation; Rust/Go Delaunay and Voronoi libraries; Java/.NET/Go topology engines; C++ surface processing and mesh Booleans; Julia scientific meshing; higher-dimensional hulls and cell-based Voronoi construction; sweep-line tessellators; and less common functional-language implementations. Follow-up searches increasingly returned the same engines, language ports, wrapper packages, and narrow demonstrations. The final selection spans C, C++, C#, Delphi, Rust, Go, JavaScript, Java, and Julia, with substantially different data structures and numerical policies.

Every retained repository's canonical GitHub page was opened, and at least one additional primary document or source file was read. The cited sources include substantive implementation or architecture material, not just search snippets. Evidence supports the specific criteria stated; recommendations about what to study are this report's engineering judgments. Current branch documentation and released API documentation can differ, so this is a research snapshot rather than a version-pinned implementation audit.

Important selection boundaries:

- JTS, GEOS, NetTopologySuite, and the JTS-derived parts of Simple Features share an algorithmic lineage. They are retained for substantive native implementations and different runtime/API engineering, not counted as unrelated geometric discoveries.
- Thin bindings, repeated ports without an additional architectural reason, tutorial collections, awesome-lists, and rendering/CAD applications whose main purpose is not a reusable geometry library were not added. Neither a wrapper's language nor its star count was treated as independent quality evidence.
- HGeometry was discovered and its repository inspected, but additional source/changelog retrieval failed in this session; it was not retained on README evidence alone. Tinfour and other triangulators appeared during discovery; this report is a curated selection, not an exhaustive inventory.
- No moved-away project is represented through an unverified unofficial mirror. The older C++ CavalierContours is subsumed by the verified Rust continuation. libtess2 is explicitly marked minimally maintained. Other entries do not imply a particular maintenance cadence merely because their repository pages are accessible.
- Numerical caveats are material: filtering, snapping, integer scaling, perturbation, approximate construction, and topology preservation establish different contracts. Earcut's rendering-oriented limitations, Clipper2's current triangulation warning, and S2's current API-stability policy are stated where relevant.
- No candidate code was executed, dependencies installed, large repositories cloned, or benchmark results independently reproduced. Performance criteria rely on inspected mechanisms, not unverified throughput rankings. Some web fetches failed or returned incomplete GitHub views; retained entries were supported through accessible official documentation or source alternatives.
