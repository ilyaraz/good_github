# Mesh generation, processing, and simplification libraries

Research date: **2026-10-09**

This report selects **26 GitHub repositories** for studying reusable mesh data structures, surface and volume generation, remeshing, subdivision, solid operations, and simplification. It includes general frameworks and focused algorithm implementations, spanning C++, C, Python, JavaScript, Rust, C#, Julia, Java, and Fortran. Mesh-specific subsystems of larger repositories are identified explicitly. Inclusion means that the inspected material supports at least two criteria; it does not mean that every component is equally robust, maintained, or suitable for every input.

**Criteria legend**

- **C1 — Difficult correctness:** topology and connectivity invariants, numerical predicates, degeneracies, concurrent mutation, or consequential failure modes.
- **C2 — Reusable abstractions:** substantial mesh representations, algorithm interfaces, properties, or policies supporting multiple uses.
- **C3 — Performance with structure:** explicit responses to memory, throughput, locality, parallelism, or repeated computation, with an architecture that can be studied.
- **C4 — Sustained evolution:** evidence across years together with compatibility work, testing, or deliberate complexity management. Repository age or a recent push alone does not qualify.

## Surface processing and mesh representations

### 1. [CGAL/cgal](https://github.com/CGAL/cgal)

**Language/role:** C++; computational geometry monorepo, represented here by `Surface_mesh_simplification` and its mesh concepts.

Study how a demanding mesh algorithm can be expressed through concepts and interchangeable policies without requiring one concrete mesh container. The simplifier accepts models of `MutableFaceGraph` and `HalfedgeListGraph`; its manual demonstrates several representations.

- **C1:** An edge selected by cost can still be rejected on geometric or topological grounds. The implementation targets oriented manifold surfaces and deliberately restricts contraction to edges; arbitrary vertex-pair contraction would violate its supported topology. The manual also explains singular quadric placement and boundary handling.
- **C2:** Cost, placement, placement filtering, stopping, and observation are separate customization points. This exposes algorithmic decisions without forcing clients to replace the collapse machinery.
- **C3:** The manual explains why per-edge costs are stored while placement is recomputed, and why expensive filters are delayed until an edge is selected: concrete memory-versus-computation tradeoffs.

**Entry point:** [Simplification design and user manual](https://doc.cgal.org/latest/Surface_mesh_simplification/index.html), including policy interfaces, algorithm stages, and worked examples. These claims concern this subsystem, not all of CGAL.

### 2. [libigl/libigl](https://github.com/libigl/libigl)

**Language/role:** C++; mesh processing algorithms using Eigen matrices and auxiliary topology arrays.

A useful contrast to container-centered libraries: study decimation as a composition of matrix operations, edge-flap connectivity, callbacks, and a priority queue. The algorithm returns mappings back to the original mesh, making downstream attribute handling part of the interface.

- **C1:** The decimator rejects non-edge-manifold inputs and treats boundaries through an augmented representation. The collapse validator checks the intersection of endpoint neighborhoods and explicitly rejects collapse of a lone tetrahedral surface. See [collapse validity](https://github.com/libigl/libigl/blob/main/include/igl/edge_collapse_is_valid.cpp).
- **C2:** Cost/placement, stopping, and pre/post-collapse callbacks are independent of the matrix-based geometry. The same driver can therefore host different simplification strategies.
- **C3:** Initial cost evaluation is separated from queue insertion to permit parallel evaluation; the source comments acknowledge the serial overhead of this choice. See the [decimation driver](https://github.com/libigl/libigl/blob/main/include/igl/decimate.cpp).

### 3. [nmwsharp/geometry-central](https://github.com/nmwsharp/geometry-central)

**Language/role:** C++; mutable surface meshes, intrinsic triangulations, and discrete geometry algorithms.

Especially valuable for understanding the relationship between topology mutation and data attached to mesh elements. Its design documentation explains both the representation and why an earlier pointer-based implementation was replaced.

- **C1:** Boundary halfedges have explicit indexing invariants, `validateConnectivity()` checks them, and deleted elements must remain unreachable from valid topology. Index-based handles avoid the invalidation problems caused by relocating pointer-based storage.
- **C2:** Typed element handles and `MeshData` containers separate connectivity from attached quantities. Resize and compression callbacks keep properties synchronized with mesh changes.
- **C3:** Contiguous buffers, implicit twin relationships, lazy deletion, and explicit compression reconcile traversal locality with inexpensive updates.

**Entry point:** [Halfedge mesh internals](https://geometry-central.net/surface/surface_mesh/internals/). Its distinctions between `SurfaceMesh` and `ManifoldSurfaceMesh` matter: the more general representation requires additional adjacency information.

### 4. [pmp-library/pmp-library](https://github.com/pmp-library/pmp-library)

**Language/role:** C++; polygon surface processing with an indexed half-edge core.

Study a relatively compact processing framework in which algorithms attach temporary properties to a shared mesh. The core supports manifold surfaces with boundary; this is a meaningful input restriction.

- **C1:** Decimation combines connectivity legality with checks for flipped normals, texture seams, valence, aspect ratio, and optional approximation limits. It temporarily evaluates proposed positions and restores them when a candidate fails.
- **C2:** The decimator stores quadrics, normals, selections, and seam information through the mesh property mechanism, illustrating how algorithms can share a container without permanently expanding every vertex record. See [decimation implementation](https://github.com/pmp-library/pmp-library/blob/main/src/pmp/algorithms/decimation.cpp).
- **C4:** The [changelog](https://github.com/pmp-library/pmp-library/blob/main/CHANGELOG.md) documents multiple years of API redesign, renderer separation, compiler/build corrections, texture-seam support, and file-parser fixes. It explicitly records breaking changes rather than implying perpetual source compatibility.

### 5. [cnr-isti-vclab/vcglib](https://github.com/cnr-isti-vclab/vcglib)

**Language/role:** C++; templated triangle-mesh processing library underlying much of MeshLab.

Study compile-time composition of vertex and face capabilities, and how local optimization algorithms operate over those user-defined types. The selection counts VCGlib once; MeshLab and its language bindings are not additional entries.

- **C1:** Quadric collapse exposes topology, boundary, normal, area, and triangle-quality controls. When topology preservation is enabled, feasibility uses link conditions. These are configurable controls, not unconditional guarantees; several preservation options default to false. See [quadric collapse](https://github.com/cnr-isti-vclab/vcglib/blob/main/vcg/complex/algorithms/local_optimization/tri_edge_collapse_quadric.h).
- **C2:** Mesh, vertex-pair, derived optimizer, and quadric-access helper types parameterize the algorithm. The [tridecimator example](https://github.com/cnr-isti-vclab/vcglib/blob/main/apps/tridecimator/tridecimator.cpp) demonstrates composing coordinate, adjacency, quality, and flag components, then adapting the optimizer to that mesh.

### 6. [mikedh/trimesh](https://github.com/mikedh/trimesh)

**Language/role:** Python; triangle-mesh manipulation, analysis, repair, and interchange.

Study the engineering required to make mutable NumPy geometry behave like a convenient object API. Although some optional operations call other libraries, its repair and caching implementations are substantive code of their own.

- **C1:** Repair must distinguish consistent winding from outward orientation. The implementation traverses face-adjacency components, and its inversion logic recognizes that volume-based decisions can be inappropriate for non-watertight meshes. See [repair operations](https://github.com/mikedh/trimesh/blob/main/trimesh/repair.py).
- **C2:** A common mesh object supports construction, geometric queries, repair, and numerous import/export paths, while optional dependencies supply additional capabilities without becoming mandatory for basic use.
- **C3:** `TrackedArray` marks potentially modifying operations, while hash-based cache verification invalidates dependent results. This is a concrete strategy for avoiding repeated geometric computation without serving stale data. See [caching implementation](https://github.com/mikedh/trimesh/blob/main/trimesh/caching.py).

The repository explicitly does not guarantee API stability; deployments should not infer it from the breadth of the interface.

### 7. [BrunoLevy/geogram](https://github.com/BrunoLevy/geogram)

**Language/role:** C++; geometric algorithms and unified surface/volume mesh storage.

Study a mesh representation organized into indexed element stores, then follow how it supports a numerical remeshing pipeline. It is particularly useful alongside half-edge libraries because its facets, corners, cells, and attributes expose different storage tradeoffs.

- **C2:** The [mesh representation](https://github.com/BrunoLevy/geogram/blob/main/src/lib/geogram/mesh/mesh.h) accommodates polygonal facets and several volumetric cell types, with attribute managers on element stores and special handling for simplicial layouts.
- **C3:** [Smooth remeshing](https://github.com/BrunoLevy/geogram/blob/main/src/lib/geogram/mesh/mesh_remesh.cpp) explicitly stages initial sampling, Lloyd iterations, optional Newton iterations, and surface extraction. It releases per-thread restricted-Voronoi storage before extracting the output because that intermediate storage consumes memory needed by the next stage.

The performance criterion rests on this observable staging and storage design, not on an unverified speed comparison.

### 8. [mlivesu/cinolib](https://github.com/mlivesu/cinolib)

**Language/role:** C++; header-oriented processing of polygonal and polyhedral meshes.

Study how much surface and volume functionality can share one abstraction. Unlike libraries centered exclusively on triangles or tetrahedra, CinoLib explicitly accommodates general polygons and polyhedra.

- **C1:** Tetrahedral edge collapse separates topological link conditions from geometric admissibility. Boundary checks account for an implicit vertex at infinity; geometric checks reject inverted or collapsed tetrahedra. See [tetrahedral mesh operations](https://github.com/mlivesu/cinolib/blob/master/include/cinolib/meshes/tetmesh.cpp).
- **C2:** [AbstractMesh](https://github.com/mlivesu/cinolib/blob/master/include/cinolib/meshes/abstract_mesh.h) factors common adjacency, attribute, labeling, and geometric interfaces out of the concrete mesh families. Template parameters carry mesh and element attributes.

The repository candidly describes the cost of this generality: variable-size element connectivity requires dynamic storage and precludes some specialized memory optimizations. It is a useful abstraction-design study, not evidence that generic representations are always faster.

### 9. [cgogn/CGoGN_3](https://github.com/cgogn/CGoGN_3)

**Language/role:** C++; combinatorial-map mesh representations with processing and modeling algorithms.

This adds a distinct topology family: cells are represented through orbits of darts and relations, rather than independent lists of every adjacency. The repository includes surface remeshing and decimation as well as volume modeling and hex generation.

- **C1:** Sewing and unsewing must preserve paired relations. `phi3_sew` asserts that both darts are available, then updates the relation symmetrically. Cutting an edge across incident volumes also requires preserving cell indices and boundary distinctions. See [three-dimensional map operations](https://github.com/cgogn/CGoGN_3/blob/master/cgogn/core/types/maps/cmap/cmap3.cpp).
- **C2:** [CMap3 and its traits](https://github.com/cgogn/CGoGN_3/blob/master/cgogn/core/types/maps/cmap/cmap3.h) define vertices, edges, faces, volumes, and connected components by different relation orbits, while reusing lower-dimensional structure and a common attribute mechanism.

Only this generation is counted; earlier CGoGN repositories are not additional entries. Repository metadata showed a September 2025 last push at the research date, so ongoing maintenance is not assumed.

### 10. [OpenVolumeMesh/OpenVolumeMesh](https://github.com/OpenVolumeMesh/OpenVolumeMesh)

**Language/role:** C++; arbitrary polyhedral topology and properties, with tetrahedral and hexahedral specializations. **Official GitHub mirror**, identified as such in repository metadata.

Study the extension from half-edges to oriented half-faces, plus the choice between inherent top-down incidence and optionally maintained bottom-up incidence.

- **C1:** Cell creation can check necessary closed-cell conditions, including use of opposing half-edges. Topology checking is optional, and the public interface warns that disconnected half-faces without checking have undefined behavior. This exposes the distinction between representational flexibility and validated construction. See [TopologyKernel implementation](https://github.com/OpenVolumeMesh/OpenVolumeMesh/blob/master/src/OpenVolumeMesh/Core/TopologyKernel.cc).
- **C2:** A generic topology kernel and element property system support multiple volumetric cell families without coupling all algorithms to one fixed tetrahedron layout.
- **C4:** The [changelog](https://github.com/OpenVolumeMesh/OpenVolumeMesh/blob/master/CHANGELOG) records dated evolution across years: API deprecation and restoration, attribute tests, endian fixes, iterator corrections, and a genus bug caused by counting deleted entities.

## Solid operations, simplification, and subdivision

### 11. [elalish/manifold](https://github.com/elalish/manifold)

**Language/role:** C++; solid triangle-mesh Booleans, construction, and refinement, with multiple language interfaces.

Study a deliberate separation between exact topological connectivity and inexact geometric coordinates. The most instructive material explains why ordinary floating-point geometric reasoning can give mutually inconsistent answers.

- **C1:** Its Boolean design uses consistent geometric decisions and symbolic perturbation to preserve manifold connectivity, then addresses difficult triangulation and degenerate-removal cases. The stated manifold-output guarantee requires manifold input; the design note distinguishes that guarantee from geometric validity on self-overlapping input.
- **C2:** Vertex property channels, provenance, and merge information preserve rendering attributes across solid operations instead of treating duplicated property vertices as disconnected topology.
- **C3:** A bounding-volume broad phase reduces unnecessary intersection work. The current repository README documents optional TBB execution and serial fallback for small jobs.

**Entry point:** [Algorithm and representation notes](https://github.com/elalish/manifold/wiki/Manifold-Library). Some backend discussion there is historical; the current README, rather than its older CUDA discussion, supports the present TBB statement.

### 12. [MeshInspector/MeshLib](https://github.com/MeshInspector/MeshLib)

**Language/role:** C++; geometry SDK. The relevant subsystem is `source/MRMesh`, particularly topology and decimation.

Study how a large mesh-processing API makes region selection, error control, callbacks, cancellation, and parallel execution coexist. The surrounding viewer is not the basis for inclusion.

- **C1:** Decimation has explicit boundary-movement controls and callback contracts. Collapse-cost adjustment may execute concurrently and must be thread-safe; user-supplied subdivision regions must not overlap, and some settings are incompatible. See [decimation interface](https://github.com/MeshInspector/MeshLib/blob/master/source/MRMesh/MRMeshDecimate.h).
- **C2:** The [mesh structure guide](https://github.com/MeshInspector/MeshLib/blob/master/doxygen/general_pages/MeshStructureOverview.md) separates point positions, half-edge topology, and cached spatial search. Typed IDs and navigation operations provide a common basis for multiple algorithms.
- **C3:** The decimator can process mesh partitions in parallel and optionally simplify across their boundaries afterward. Its API documents the importance of packing the mesh before that path.

### 13. [zeux/meshoptimizer](https://github.com/zeux/meshoptimizer)

**Language/role:** C++ with C-compatible interfaces; mesh simplification, GPU-oriented ordering, meshlets, and compression.

Study simplification as one stage of a rendering asset pipeline, with explicit treatment of attribute seams and vertex/index storage. The core library, `gltfpack`, and clustered-LOD companion code are counted together.

- **C1:** The [simplifier](https://github.com/zeux/meshoptimizer/blob/master/src/simplifier.cpp) classifies manifold, border, seam, complex, fringe, and locked vertices, then restricts which kinds may collapse into each other. Attribute discontinuities and protected vertices are therefore part of the algorithm's topology handling.
- **C3:** Flat adjacency/remap structures and buffer-oriented interfaces target real GPU and asset-processing costs. Sparse simplification supports subsets without treating the whole vertex buffer as equally relevant; the README explains the associated error-scale semantics.

**Additional entry point:** [Simplification fuzz target](https://github.com/zeux/meshoptimizer/blob/master/tools/simplifyfuzz.cpp), which exercises multiple options and attribute-aware paths on generated geometry. The README separately documents stable versus experimental APIs; that policy does not promise identical output meshes across versions.

### 14. [PixarAnimationStudios/OpenSubdiv](https://github.com/PixarAnimationStudios/OpenSubdiv)

**Language/role:** C++; subdivision surface refinement and evaluation on CPU/GPU backends.

Study decomposition of a numerical geometry pipeline into topology analysis, interpolation weights, and execution backends. This concerns reusable subdivision libraries rather than a complete modeling application.

- **C2:** The [API overview](https://github.com/PixarAnimationStudios/OpenSubdiv/blob/dev/documentation/api_overview.rst) explains the `Sdc`, `Vtr`, `Far`, `Bfr`, and `Osd` layers. Clients can use the topology/refinement layer without depending on the parallel drawing layer.
- **C3:** The [Far design](https://github.com/PixarAnimationStudios/OpenSubdiv/blob/dev/documentation/far_overview.rst) separates topology refinement from primitive-variable interpolation. Stencil tables amortize work across many attributes or animation frames when topology remains fixed, while feature-adaptive refinement concentrates work around extraordinary features.

This is an especially clear example of moving expensive structural work out of a repeated evaluation loop.

### 15. [sp4cerat/Fast-Quadric-Mesh-Simplification](https://github.com/sp4cerat/Fast-Quadric-Mesh-Simplification)

**Language/role:** C++; compact, reusable quadric mesh simplifier with example executables.

A focused comparison point for the larger frameworks: study what is gained and lost by replacing a globally ordered collapse queue with increasing error thresholds. Repository metadata showed a July 2024 last push; treat this as an older algorithm implementation, not evidence of current support.

- **C1:** Its [single-header implementation](https://github.com/sp4cerat/Fast-Quadric-Mesh-Simplification/blob/master/src.cmd/Simplify.h) handles singular quadric systems by testing endpoints and midpoint, rejects problematic normal changes, and distinguishes boundary vertices during collapse.
- **C3:** The same file exposes the threshold loop, compact adjacency references, dirty/deleted flags, and final compaction. The README explicitly describes avoiding sorting as a speed/quality tradeoff.

The author limits its recommended use to watertight volumes without thin sections. That caveat and the heuristic numerical checks make it valuable as a bounded engineering case study; its advertised cross-project speed ratio is not adopted here.

## Volume generation and adaptive remeshing

### 16. [NGSolve/netgen](https://github.com/NGSolve/netgen)

**Language/role:** C++; tetrahedral mesh generator and reusable meshing library, with Python scripting.

Study an advancing-front engine connected to reusable geometry and mesh APIs. Netgen accepts several geometry representations and includes optimization and hierarchical refinement.

- **C1:** The [three-dimensional meshing loop](https://github.com/NGSolve/netgen/blob/master/libsrc/meshing/meshing3.cpp) evaluates local rules in transformed coordinates, rejects candidates conflicting with local sizing and neighborhood limits, stages candidate changes, and distinguishes completion from an unclosed front. This is substantial geometric state management rather than a direct point-to-tetrahedron conversion.
- **C2:** The [nglib interface](https://github.com/NGSolve/netgen/blob/master/nglib/nglib.h) provides mesh construction, volume generation, geometry-specific operations, and refinement, with shared meshing parameters and explicit surface/volume failure codes.

The source is useful for following how candidate generation and front mutation interact; the API is useful for seeing where the engine exposes that complexity to callers.

### 17. [wildmeshing/fTetWild](https://github.com/wildmeshing/fTetWild)

**Language/role:** C++; tetrahedral meshing library and command-line research implementation for triangle soups.

Study robustness obtained through the ordering of construction and optimization, including preservation of a valid floating-point tetrahedral mesh. This is a substantive successor algorithm to TetWild, not a wrapper around it; TetWild is not counted separately.

- **C1:** The authors explain interleaving triangle insertion with mesh optimization to keep floating-point output valid. They also explicitly give up a guarantee that every input triangle is inserted. See the [method description](https://arxiv.org/abs/1908.03581).
- **C3:** The implementation combines spatial envelope queries with local operations and optional parallel quality recomputation rather than performing every geometric check globally. See [triangle insertion](https://github.com/wildmeshing/fTetWild/blob/master/src/TriangleInsertion.cpp) and its staged update logic.

The inspected build defines a real `FloatTetwild` library target. The README warns that input face orientation matters and difficult inputs can require substantial memory; robustness should not be read as immunity to resource exhaustion.

### 18. [dengwirda/jigsaw](https://github.com/dengwirda/jigsaw)

**Language/role:** C++; restricted-Delaunay mesh generation and optimization, with a C-format API.

Study a generator whose domain geometry, mesh-spacing field, refinement strategy, and storage are separate template parameters. It covers planar, surface, and volumetric domains; scripting bindings are not counted separately.

- **C2:** The [three-dimensional refinement driver](https://github.com/dengwirda/jigsaw/blob/master/src/libcpp/rdel_mesh/rdel_mesh_3.hpp) parameterizes mesh storage, predicates, geometry, spacing, initialization, and allocation. A new domain or spacing policy need not entail rewriting the entire refinement loop.
- **C3:** Separate priority structures track nodes, edges, faces, cells, and protective balls, while cavity lists support incremental work. The source describes refining bad simplices to convergence instead of repeatedly reconstructing the complete tessellation.

The repository's documented CLI/C API and unit/example layout provide integration context. Metadata showed an August 2025 last push; no stronger maintenance claim is inferred from that date.

### 19. [MmgTools/mmg](https://github.com/MmgTools/mmg)

**Language/role:** C; 2D, surface, and 3D remeshing libraries and tools. The inspected implementation centers on `mmg3d`.

Study metric-driven adaptation as a pipeline with validation, scaling, analysis, remeshing, and synchronized compaction of mesh and solution data.

- **C1:** [The library driver](https://github.com/MmgTools/mmg/blob/master/src/mmg3d/libmmg3d.c) validates scalar/tensor metric shape and option combinations, distinguishes failure levels, and packs connectivity and associated solutions together. Assertions check that packed metric and mesh vertex counts agree.
- **C2:** The [public API](https://github.com/MmgTools/mmg/blob/master/src/mmg3d/libmmg3d.h) exposes required entities, local parameters, isotropic/anisotropic sizing, level-set modes, and boundary controls through reusable mesh/solution structures. C and Fortran interfaces make this usable inside simulation workflows.

The distinction between a metric, a level-set field, and a displacement field is architectural: their shared storage does not make their modes interchangeable.

### 20. [lanl/LaGriT](https://github.com/lanl/LaGriT)

**Language/role:** Primarily Fortran with C/C++ and Python interfaces; mesh generation, optimization, and dynamic maintenance, particularly for geoscience.

Study a command-driven library where geometry, material information, and fields are carried in named mesh objects. This provides a different integration model from modern C++ templates or Python mesh objects.

- **C1:** [Refinement semantics](https://github.com/lanl/LaGriT/blob/master/docs/pages/docs/commands/REFINE.md) describe recursive longest-edge refinement and interface-specific splitting. Neighbor propagation matters for mesh consistency; interface refinement creates interior freedom for later smoothing when tetrahedra are constrained by material surfaces.
- **C2:** [Current Mesh Objects](https://github.com/lanl/LaGriT/blob/master/docs/pages/docs/commands/CMO2.md) support multiple named meshes, built-in and user attributes, configurable attribute types, and mesh operations across different element families. Refinement also specifies field interpolation rather than silently discarding associated data.

Its documentation explicitly marks some refinement methods unavailable or untested. The entry concerns the documented working mechanisms, not blanket coverage of every historical command.

## Planar triangulation and quality mesh refinement

### 21. [mapbox/earcut](https://github.com/mapbox/earcut)

**Language/role:** JavaScript; polygon triangulation for rendering and mapping pipelines.

Study a small algorithm with unusually visible practical compromises. It converts polygon rings and holes into triangle indices and is suitable for tracing the entire control flow.

- **C1:** The [implementation](https://github.com/mapbox/earcut/blob/main/src/earcut.js) contains hole elimination, collinear-point filtering, local self-intersection repair, and polygon splitting when ordinary ear clipping stalls. These are meaningful adversarial-input paths.
- **C3:** Z-order indexing and spatially restricted ear tests reduce candidate checks, with simpler handling for small polygons and a convex-ring shortcut in the inspected source. Those choices are visible alongside the core linked-ring algorithm.

The README explicitly says that handling twisted polygons, degeneracies, and self-intersections does **not** guarantee a correct triangulation. C1 here means that the implementation engages seriously with difficult cases, not that it supplies exact-arithmetic guarantees.

### 22. [mapbox/delaunator](https://github.com/mapbox/delaunator)

**Language/role:** JavaScript; unconstrained Delaunay triangulation of planar points.

Study a compact indexed triangulator whose output exposes triangles, halfedges, and the convex hull directly. It complements Earcut: the input and invariants are those of a point-set triangulation, not polygon-with-holes filling.

- **C1:** The [source](https://github.com/mapbox/delaunator/blob/main/index.js) uses robust orientation predicates, explicitly handles collinear input, skips duplicate/near-duplicate points, and legalizes edges while maintaining reciprocal halfedge links. This is not a claim that every predicate in the implementation uses exact arithmetic.
- **C3:** Typed arrays store connectivity and temporary work; an angular hash accelerates finding a visible hull edge. `update()` reuses the allocated structures when coordinates change, supporting repeated relaxation-like workloads.

Its narrow scope is a strength for study, but it does not replace a constrained or quality-refining mesher.

### 23. [Stoeoef/spade](https://github.com/Stoeoef/spade)

**Language/role:** Rust; Delaunay/constrained Delaunay triangulation, refinement, and interpolation.

Study how Rust traits and typed handles expose mutable geometric topology without requiring application data to adopt one fixed vertex struct.

- **C1:** [Refinement implementation and documentation](https://github.com/Stoeoef/spade/blob/master/src/delaunay_core/refinement.rs) explain when angle demands can cause runaway refinement, cap added vertices, and report incomplete refinement. Constraint splitting preserves the represented boundary but may change its segmentation.
- **C2:** The [Triangulation trait](https://github.com/Stoeoef/spade/blob/master/src/triangulation.rs) shares operations across constrained and unconstrained meshes, with associated vertex, directed-edge, undirected-edge, face, and location-hint types.
- **C3:** Incremental insertion and bulk loading are distinct paths, while hint generators make point-location strategy replaceable. The interface documents degenerate-input behavior instead of presenting one universal complexity claim.

### 24. [wo80/Triangle.NET](https://github.com/wo80/Triangle.NET)

**Language/role:** C#; a substantive .NET implementation derived from Shewchuk's Triangle, supporting constrained triangulation and quality meshing.

Study the translation of numerically careful triangulation into a managed-language library with interchangeable initial triangulators and separate constraint/quality stages.

- **C1:** [RobustPredicates](https://github.com/wo80/Triangle.NET/blob/master/src/Triangle/RobustPredicates.cs) uses error-bound checks and adaptive arithmetic for orientation and in-circle decisions. Circumcenter/off-center code also addresses small-angle refinement behavior.
- **C2:** [GenericMesher](https://github.com/wo80/Triangle.NET/blob/master/src/Triangle/Meshing/GenericMesher.cs) composes an `ITriangulator` and configuration, accepts point sets or polygons, and exposes constraint, quality, and cancellation options. The implementation is more than a binding to the original C executable.

**Material limitation:** The repository README explicitly flags uncertainty around the inherited Triangle licensing, advises against commercial use, and explains the absence of an official NuGet release. This is the maintainer's stated limitation, not an independent legal conclusion.

### 25. [JuliaGeometry/DelaunayTriangulation.jl](https://github.com/JuliaGeometry/DelaunayTriangulation.jl)

**Language/role:** Julia; planar triangulation, curve-bounded mesh refinement, weighted triangulation, and Voronoi constructions.

Study an implementation that makes numerical predicate policy visible through Julia dispatch, while supporting dynamic insertion/deletion and several domain representations.

- **C1:** The [predicate design](https://github.com/JuliaGeometry/DelaunayTriangulation.jl/blob/main/docs/src/manual/predicates.md) distinguishes fast, adaptive, and exact kernels. Predicates return multi-outcome certificates rather than ambiguous booleans; the documentation connects unreliable predicate decisions to failures such as infinite loops.
- **C2:** The [internal data-structure guide](https://github.com/JuliaGeometry/DelaunayTriangulation.jl/blob/main/docs/src/extended/data_structures.md) explains shared adjacency maps, polygon hierarchies, queues, and refinement priorities. Polygon hierarchy represents disconnected and nested domain boundaries, while shared primitives support both triangulations and tessellations.

The documentation also labels unfinished mechanisms; for example, the presence of a balanced search tree is not evidence that automatic intersecting-segment handling has been completed.

### 26. [gwlucastrig/Tinfour](https://github.com/gwlucastrig/Tinfour)

**Language/role:** Java; Delaunay and constrained triangulated irregular networks, with terrain and interpolation utilities.

Study a mesh library shaped by large terrain datasets and the allocation costs of managed-language object graphs. Its core is separable from GIS-oriented extensions.

- **C1:** [GeometricOperations](https://github.com/gwlucastrig/Tinfour/blob/master/core/src/main/java/org/tinfour/common/GeometricOperations.java) uses ordinary floating-point evaluation and threshold-triggered extended precision for delicate geometric decisions. Reusable arithmetic objects and diagnostic counts make the numerical fallback explicit.
- **C3:** [SemiVirtualEdge](https://github.com/gwlucastrig/Tinfour/blob/master/core/src/main/java/org/tinfour/semivirtual/SemiVirtualEdge.java) implements quad-edge navigation through integer-array links and pooled pages instead of a persistent object for every relationship. The common edge interface keeps traversal recognizable despite the altered storage.

The repository's advertised throughput is not reproduced here; the selection rests on the inspected numerical and storage mechanisms.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations. The main angles were:

- Half-edge surface libraries, matrix-based processing, and general mesh abstractions.
- Quadric simplification, rendering-oriented optimization, and compact threshold-based decimators.
- Tetrahedral generation from difficult triangle soups and geometry-driven advancing fronts.
- Anisotropic adaptation, restricted Delaunay meshing, and geoscience mesh maintenance.
- Rust, C#, Java, JavaScript, and Julia triangulation/refinement ecosystems.
- General polyhedral storage, combinatorial maps, and quad/hex generation.
- Solid Booleans, topology guarantees, and subdivision backends.

Follow-up searches on anisotropic remeshing and progressive/quadric simplification increasingly returned already covered frameworks, ports, wrappers, and narrow algorithm demonstrations. They also surfaced further candidates such as Pragmatic, Tucanos, Trinity, and HOHQMesh; these were not fully inspected and are not presented as qualified entries. The resulting selection extends slightly beyond 25 because the additional topology families and language communities contribute materially different study paths.

Canonical repository URLs and default branches were checked through the public GitHub API or opened repository pages. Each retained project has an independently read implementation file or substantive design/API document beyond its README. GitHub source paths were checked against repository trees; linked branch paths are moving references rather than pinned reproducibility snapshots. OpenVolumeMesh is explicitly marked as an official mirror. Older activity is noted where material, and C4 is used only where dated evolution accompanies concrete compatibility or complexity-management evidence.

The scope excludes thin language bindings, tutorial-only implementations, generated wrappers, lists of links, and standalone viewers. MeshLab is represented by its underlying VCGlib rather than counted again. General rendering and point-cloud frameworks were not expanded into separate entries merely because they contain a mesh filter. Gmsh's [official site](https://gmsh.info/) directs development to its own GitLab service; this search did not establish an official substantive GitHub mirror and therefore did not include an arbitrary GitHub copy. The inspected [current automesh meshing module](https://github.com/autotwin/automesh/blob/main/src/mesh/mod.rs) delegates core geometry operations to another crate, so it was not added as a separate algorithm-library entry.

This was source and documentation research: no candidate code was executed, dependencies installed, benchmarks reproduced, or repositories cloned. Descriptions of what an engineer can learn are grounded editorial judgments. Correctness mechanisms and documented guarantees should be distinguished from an independent correctness audit, and no ranking by stars or unsupported numerical speed claim is used.
