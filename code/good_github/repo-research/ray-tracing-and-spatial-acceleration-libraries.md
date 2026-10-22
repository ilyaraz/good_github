# Ray tracing and spatial acceleration libraries

Research date: **2026-10-09**.

This report selects **24 GitHub repositories** implementing reusable ray-intersection kernels, bounding-volume hierarchies (BVHs), and spatial search structures. It covers CPU/GPU traversal, browser mesh queries, scientific geometry, k-d and ball trees, dynamic and packed R-trees, and orthotrees. Larger repositories are included only for named acceleration subsystems and are counted once. Full renderers, graphics API tutorials, thin language bindings, and high-dimensional vector databases are outside this selection.

The criteria are:

- **C1 — Difficult correctness:** numerical semantics, structural invariants, concurrency, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces that serve multiple geometries, queries, applications, or execution environments.
- **C3 — Performance with structure:** concrete work on memory layout, construction, traversal, parallelism, or allocation, with understandable architectural boundaries.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or complexity management, beyond repository age alone.

Criteria below are evidence-based engineering assessments, not certifications of uniformly exemplary code. Canonical repository identities were checked through GitHub pages or its API; implementation and documentation links were opened and read. Default-branch code may be newer than a released package. No candidate code was executed and no benchmark claims were independently reproduced.

## Ray-intersection engines and BVH libraries

### 1. [RenderKit/embree](https://github.com/RenderKit/embree)

**Language/role:** C++, ISPC, and SYCL; reusable ray-tracing kernels. The former `embree/embree` URL redirects to this canonical repository.

Study how an industrial intersection engine separates primitive intersectors from BVH traversal while specializing hot code for node width and numerical behavior.

- **C1:** The single-ray implementation handles empty hierarchies, validates ray intervals and motion time, and parameterizes robust traversal. Its closest-hit loop must keep the ray's shrinking far distance consistent with queued nodes and SIMD traversal state.
- **C3:** Node intersection produces child masks and distances; a separate traverser orders pending children, while primitive-specific precalculations and leaf intersectors remain outside that traversal policy. These boundaries are visible in [the single-ray traversal implementation](https://github.com/RenderKit/embree/blob/master/kernels/bvh/bvh_intersector1.cpp).

Also inspect the [changelog](https://github.com/RenderKit/embree/blob/master/CHANGELOG.md) for robust-mode boundary corrections, NaN fixes, and API/platform transitions. It is useful context for why the fast paths have accumulated complexity.

### 2. [GPUOpen-LibrariesAndSDKs/HIPRT](https://github.com/GPUOpen-LibrariesAndSDKs/HIPRT)

**Language/role:** C++/HIP; GPU ray-tracing library intended for integration into HIP applications.

The most instructive distinction is between the traversal operation and the memory policy used to retain its state.

- **C2:** Device traversal objects distinguish geometry from scenes, closest-hit from any-hit queries, and built-in triangles from custom primitives. Stack and instance-stack types are explicit reusable components of the [device API](https://github.com/GPUOpen-LibrariesAndSDKs/HIPRT/blob/main/hiprt/hiprt_device.h).
- **C3:** Private stacks use local memory; global and dynamically assigned alternatives combine shared memory with global-memory spill storage. This makes occupancy, stack capacity, and memory-access costs visible architectural choices rather than hidden implementation details.

The [implementation directory](https://github.com/GPUOpen-LibrariesAndSDKs/HIPRT/tree/main/hiprt/impl) separates construction, node representations, geometry, compilation, and device traversal. The repository README describes separate basic-feature, mesh-feature, and performance test groups; those tests were not run here.

### 3. [NVIDIA/OWL](https://github.com/NVIDIA/OWL)

**Language/role:** C++/CUDA; an OptiX productivity library with substantive resource and acceleration-structure management.

Although its name says “Wrappers,” OWL belongs here because it implements a scene/resource graph, shader-binding-table management, multi-device resources, and BVH lifecycle logic rather than merely forwarding generated bindings.

- **C1:** The triangle-group implementation rejects refitting an unbuilt acceleration structure or one lacking the required update flag. It distinguishes rebuilds, updates, temporary storage requirements, and optional compaction.
- **C2:** Geometry groups, instance groups, buffers, modules, and per-device state form reusable abstractions for different renderers and ray-query applications, as explained in the [project overview](https://github.com/NVIDIA/OWL/blob/main/README.md).
- **C3:** [Triangle acceleration construction](https://github.com/NVIDIA/OWL/blob/main/owl/TrianglesGeomGroup.cpp) explicitly computes scratch requirements, retrieves compacted sizes, replaces BVH buffers, and tracks device-memory consumption. It is a useful study of organizing a hardware API's multi-step protocol.

### 4. [jbikker/tinybvh](https://github.com/jbikker/tinybvh)

**Language/role:** C++; dependency-free BVH construction and traversal, with CPU and GPU-oriented layouts.

Study how different representations of the same hierarchy target different hardware and ray workloads.

- **C2:** The [repository documentation](https://github.com/jbikker/tinybvh/blob/main/README.md) describes binary and wide layouts, transformed BLAS instances beneath a TLAS, closest-hit and occlusion queries, and refitting. It explicitly limits refitting to unchanged primitive counts.
- **C3:** Binary, wide CPU, and compressed GPU layouts are separate choices. The [top-level implementation header](https://github.com/jbikker/tinybvh/blob/main/tiny_bvh.h) exposes traversal/build thresholds and separates platform-neutral code from x86 and ARM float/double kernels. It also shows the optional watertight triangle test rather than implying that every configuration uses it.

This is a compact comparison point for Embree's broader engine. Treat the README's comparative benchmark results as workload-specific author measurements; this report does not rank the libraries by those numbers.

### 5. [madmann91/bvh](https://github.com/madmann91/bvh)

**Language/role:** C++20, with a C-facing high-level interface; standalone generic BVH construction and traversal.

Study an intentionally small architecture in which builders, traversal, primitive tests, and optimization remain separable.

- **C1:** The traversal interface explicitly selects robust versus faster ray-box testing and any-hit versus closest-hit behavior. Robust traversal uses padded inverse directions; refitting recomputes internal bounds bottom-up. These choices are directly visible in [the BVH implementation](https://github.com/madmann91/bvh/blob/master/src/bvh/v2/bvh.h).
- **C2:** User-supplied leaf functions and node/scalar/dimension types allow the hierarchy to serve geometry beyond a fixed triangle representation.
- **C3:** The [project's builder overview](https://github.com/madmann91/bvh/blob/master/README.md) distinguishes sweeping SAH, binned SAH, multithreaded mini-tree construction, and reinsertion optimization, with a higher-level quality-selection interface. This makes build-time versus query-time tradeoffs especially easy to compare.

The current interface is version 2; the README points existing version-1 users to a separate branch.

### 6. [lighttransport/nanort](https://github.com/lighttransport/nanort)

**Language/role:** Portable C++; single-header ray-tracing kernel with custom primitive support.

Study a small kernel that preserves explicit numerical and geometry-extension boundaries while retaining compatibility with older C++ environments.

- **C1:** The [project documentation](https://github.com/lighttransport/nanort/blob/release/README.md) identifies robust ray-box traversal and watertight triangle intersection, supports double precision, and defines minimum/maximum ray distances. It also distinguishes optional parallel-build configurations and their testing caveats.
- **C2:** `BVHAccel` accepts primitive accessors and partition predicates; traversal accepts an intersector. Triangle meshes are a supplied implementation rather than the only geometry model.
- **C3:** The hierarchy uses a pointer-free linear representation, while the [implementation](https://github.com/lighttransport/nanort/blob/release/nanort.h) contains explicit build thresholds and small-buffer allocation machinery. These are useful examples of controlling allocation and representation without imposing a full scene engine.

The verified default branch is `release`; roadmap checkboxes in the README were not treated as implemented features.

### 7. [svenstaro/bvh](https://github.com/svenstaro/bvh)

**Language/role:** Rust; generic BVH, ray, and axis-aligned bounding-box library.

Study how a host-side hierarchy becomes a representation suitable for iterative shader traversal.

- **C2:** `Bounded` and `BHShape` adapt application-owned shapes, with generic scalar and dimensional types. The flattening API also accepts a custom node constructor, allowing a consumer-specific output layout.
- **C3:** [Flat BVH construction and traversal](https://github.com/svenstaro/bvh/blob/master/src/flat_bvh.rs) use entry and exit indices to traverse without a separate stack. The [README](https://github.com/svenstaro/bvh/blob/master/README.md) documents Rayon construction, explicit SIMD paths, and the limitations of local rotations when many shapes move.
- **C1:** Flat leaves use a sentinel entry index and have undefined bounding-box fields, so traversal must inspect the sentinel before accessing bounds. This is a concrete representation invariant worth following through the implementation.

The README's favorable asymptotic summary should not be read as a worst-case query guarantee for arbitrary geometry.

## Mesh queries, scientific geometry, and general BVHs

### 8. [gkjohnson/three-mesh-bvh](https://github.com/gkjohnson/three-mesh-bvh)

**Language/role:** JavaScript; acceleration and spatial queries for three.js geometry.

Study the boundary between an acceleration structure and a mutable graphics-engine mesh, including worker transfer and serialization.

- **C1:** [MeshBVH's implementation and API comments](https://github.com/gkjohnson/three-mesh-bvh/blob/master/src/core/MeshBVH.js) specify local-coordinate queries, index-buffer ownership, draw-range/group exclusions, and the consequences of modifying indices after construction. Deserialization also contains a conversion path for an older node-offset representation.
- **C2:** Triangle callbacks, shape casting, BVH-to-BVH queries, closest-point queries, and refitting support picking, collision queries, sculpting, and geometric processing beyond rendering.
- **C3:** The same source explains transfer or sharing of serialized node buffers across WebWorkers and optional copying of buffers. The [project examples and integration guide](https://github.com/gkjohnson/three-mesh-bvh/blob/master/README.md) show how these mechanisms fit browser workloads.

### 9. [dimforge/parry](https://github.com/dimforge/parry)

**Language/role:** Rust; collision and geometric-query library. Relevant subsystem: `src/partitioning/bvh`, counted once across its 2D/3D and precision variants.

Study acceleration-structure maintenance for changing geometry, where correctness involves more than the initial build.

- **C1:** [BVH validation](https://github.com/dimforge/parry/blob/master/src/partitioning/bvh/bvh_validation.rs) checks cycles, parent/child indices, leaf mappings, subtree counts, propagated change flags, and geometric containment. The checks make the invariants behind insertion, refitting, and optimization unusually concrete.
- **C3:** The [BVH types and construction interface](https://github.com/dimforge/parry/blob/master/src/partitioning/bvh/bvh_tree.rs) distinguish binned SAH and locally ordered clustering. A reusable workspace retains temporary buffers between operations to reduce allocations.

The inspected implementation explicitly says these construction strategies are currently sequential, including the one based on a parallel clustering paper. Its algorithm name should not be mistaken for an implemented parallel builder.

### 10. [CGAL/cgal](https://github.com/CGAL/cgal)

**Language/role:** C++; computational geometry monorepo. Relevant subsystem: **AABB Tree** for intersection and distance queries.

Study the separation of hierarchy mechanics from primitive identity, geometry access, predicates, and constructions.

- **C2:** The [AABB Tree manual](https://doc.cgal.org/latest/AABB_tree/index.html) demonstrates traits and primitive adapters over triangles, segments, and mesh faces, with intersection-existence, primitive-ID, constructed-intersection, and nearest-point interfaces.
- **C1:** The manual distinguishes an arbitrary encountered intersection from the first along a ray, demonstrates skipping a source face to avoid floating-point self-intersections, and states the failure risks of degenerate primitives with unsuitable traits. These are meaningful semantic constraints rather than a blanket promise of exactness.
- **C3:** Distance queries use an auxiliary search structure; incremental insertion into this static hierarchy triggers rebuilding rather than silently providing dynamic-tree update costs.

The [repository guide](https://github.com/CGAL/cgal/blob/main/README.md) explains the package-based source organization. This entry does not assess unrelated CGAL packages.

### 11. [kokkos/ArborX](https://github.com/kokkos/ArborX)

**Language/role:** C++/Kokkos; portable geometric search, including distributed search. The former `arborx/ArborX` URL redirects here.

Study how execution space, memory space, application data, bounding volumes, and query outputs become separate library parameters.

- **C2:** [The linear BVH interface](https://github.com/kokkos/ArborX/blob/master/src/spatial/ArborX_LinearBVH.hpp) accepts indexable getters, customizable bounding volumes and space-filling curves, and callback or compressed-row-style outputs. Kokkos views distinguish leaf storage from internal-node storage.
- **C3:** Morton ordering, batched queries, traversal policies, and execution-space-aware construction make accelerator portability an architectural concern. The source exposes a per-thread query path as well.
- **C4:** The [2020–2026 changelog](https://github.com/kokkos/ArborX/blob/master/CHANGELOG.md) documents stackless traversal, CUDA-aware MPI copy avoidance, callback/memory-access checks, deprecation and removal of old APIs, and fixes for ray-box division by zero and compiler-specific failures. This supports sustained complexity and compatibility management.

### 12. [attcs/Octree](https://github.com/attcs/Octree)

**Language/role:** C++20; OrthoTree, providing quadtrees, octrees, higher-dimensional trees, and a static BVH.

Study an acceleration library that separates indexing storage from geometry ownership and search operations.

- **C2:** Geometry adapters, entity identifiers, non-owning cores, and managed wrappers allow application containers and third-party geometry types to participate without adopting one mandatory scene representation.
- **C3:** The [architecture documentation](https://github.com/attcs/Octree/blob/master/docs/README.md) separates an immutable linear orthotree, a mutable hash-based orthotree, a binned-SAH static BVH, and a shared query layer. This gives a concrete comparison of locality versus mutation costs.
- **C1:** The same document distinguishes stable and shifting entity indices and declares a `noexcept` policy: allocation failure or throwing callbacks terminate execution. This is an explicit integration constraint, not recoverable-error handling.

The [README](https://github.com/attcs/Octree/blob/master/README.md) lists ray, range, nearest-neighbor, frustum, and collision queries and documents dimension/depth limits.

## Point and metric-space search

### 13. [jlblancoc/nanoflann](https://github.com/jlblancoc/nanoflann)

**Language/role:** C++; header-only k-d trees, especially for low-dimensional point clouds.

Study data adaptation without copying an entire application dataset into a library-owned matrix. It originated as a FLANN fork, but its documented template/CRTP redesign and independently developed index types make it a substantive separate implementation.

- **C2:** Dataset and distance adaptors support different containers and coordinate/metric types; the [README](https://github.com/jlblancoc/nanoflann/blob/master/README.md) explains the removal of virtual-dispatch-based interfaces and the direct-access model.
- **C1:** L2 queries use squared distances. The [implementation](https://github.com/jlblancoc/nanoflann/blob/master/include/nanoflann.hpp) also spells out the asynchronous incremental index's threading contract: concurrent readers are allowed under its stated conditions, writers are restricted, and backing element storage must stay stable during background rebuilding.
- **C3:** Pooled node allocation and background rebuild/replay machinery expose both throughput and foreground-latency concerns. These newer index types should be checked against the version actually deployed.

### 14. [sdd-org/kiddo](https://github.com/sdd-org/kiddo)

**Language/role:** Rust; low-dimensional k-d trees with configurable coordinate, storage, and traversal strategies.

Study how cache behavior can be exposed through reusable strategies rather than baked into every query implementation.

- **C2:** The [crate-level API documentation](https://github.com/sdd-org/kiddo/blob/master/src/lib.rs) describes mutable/immutable aliases, floating/fixed/integer coordinates, several result-selection modes, periodic boundaries, and explicit inclusive/exclusive radius behavior.
- **C3:** [The Eytzinger strategy](https://github.com/sdd-org/kiddo/blob/master/src/stem_strategy/eytzinger/mod.rs) uses breadth-first stem layout, compact deferred traversal state, and compile-time immediate/deeper prefetch policies. It supplies variants with prefetching disabled, making the optimization boundary inspectable.

The source documents that mutable trees do not continuously rebalance; some strategies can perform a safety rebuild, and callers may still need periodic rebuilds under growth or churn. The library is explicitly aimed at low-dimensional spatial workloads, not general embedding search.

### 15. [KristofferC/NearestNeighbors.jl](https://github.com/KristofferC/NearestNeighbors.jl)

**Language/role:** Julia; k-d, ball, brute-force, and periodic nearest-neighbor structures.

Study metric-driven algorithm selection and the ownership consequences of reusing storage in a language with ordinary array references.

- **C2:** The [README/API guide](https://github.com/KristofferC/NearestNeighbors.jl/blob/master/README.md) distinguishes axis-aligned metrics for k-d trees, broader metric support for ball trees, brute-force baselines, and periodic-domain wrapping behind related query interfaces.
- **C1:** [K-d tree construction](https://github.com/KristofferC/NearestNeighbors.jl/blob/master/src/kd_tree.jl) rejects NaNs, checks metric dimensionality, and invalidates an old tree when a mutating constructor takes over its storage. Aliasing the old internal dataset is explicitly disallowed.
- **C3:** Reordering improves query locality; parallel construction and buffer-reusing rebuilds address build cost and allocation. The source shares a construction core between fresh and recycled-storage paths.

These trees are static between rebuilds; periodic support does not make them dynamically insertable.

## R-trees and multidimensional indexes

### 16. [libspatialindex/libspatialindex](https://github.com/libspatialindex/libspatialindex)

**Language/role:** C++, with a C API; reusable spatial indexes including R*, multiversion, and time-parameterized trees.

Study a storage-aware indexing library with abstractions beyond an in-memory container.

- **C2:** [R-tree construction and querying](https://github.com/libspatialindex/libspatialindex/blob/main/src/rtree/RTree.cc) are mediated by `IStorageManager`, property sets, shapes, visitors, and nearest-neighbor comparators. Bulk loading and reopening an index share the same higher-level interfaces.
- **C1:** The implementation checks configuration constraints such as fill factors and dimensionality. It rejects non-finite insertion bounds before they can poison area comparisons and later splitting, and deliberately includes tied neighbors even when that produces more than the requested count.

The [repository's documentation pointer](https://github.com/libspatialindex/libspatialindex/blob/main/README.rst) leads to its full library manual. This entry is about the underlying implementation, not the Python or Julia bindings, and makes no blanket thread-safety claim.

### 17. [boostorg/geometry](https://github.com/boostorg/geometry)

**Language/role:** C++; Boost.Geometry. Relevant subsystem: `include/boost/geometry/index`, particularly `rtree`.

Study a spatial container whose customization model follows generic C++ library design rather than a fixed geometry class hierarchy.

- **C2:** [The R-tree interface and implementation](https://github.com/boostorg/geometry/blob/develop/include/boost/geometry/index/rtree.hpp) parameterize stored values, indexable extraction, equality, allocation, and tree parameters. Points, boxes, segments, and compound values can use the same container machinery.
- **C3:** Packing constructors and separate linear, quadratic, and R*-tree implementation families expose construction/quality tradeoffs. The documentation warns against repeatedly calculating an indexable during extraction, tying the abstraction's contract to its hot-path cost.

The [repository guide](https://github.com/boostorg/geometry/blob/develop/README.md) identifies dedicated spatial-index examples and regression tests. The inspected branch is `develop`.

### 18. [georust/rstar](https://github.com/georust/rstar)

**Language/role:** Rust; generic multidimensional R*-tree.

Study the contract between an application's exact geometry and its conservative search envelope.

- **C1:** [Object and distance traits](https://github.com/georust/rstar/blob/master/rstar/src/object.rs) prohibit changing an envelope after insertion and define squared-distance semantics. The default thresholded distance method first uses the envelope as a lower bound before evaluating the object itself.
- **C2:** `RTreeObject`, `PointDistance`, envelope types, geometry-with-data wrappers, and selection interfaces support application-defined spatial objects.
- **C3:** [The tree implementation's design notes](https://github.com/georust/rstar/blob/master/rstar/src/rtree.rs) discuss bulk loading and distinguish external iterators, which retain heap-allocated traversal state, from callback-based internal iteration that can use stack state. They also explicitly describe degeneration when indexed objects overlap heavily.

This is a useful companion to Boost.Geometry for comparing C++ customization with Rust traits and iterator APIs.

### 19. [mourner/rbush](https://github.com/mourner/rbush)

**Language/role:** JavaScript; dynamic 2D spatial index over points and rectangles.

Study a relatively compact R-tree whose entire insertion, bulk-load, split, search, and deletion flow can be followed in one implementation file.

- **C1:** [The implementation](https://github.com/mourner/rbush/blob/main/index.js) propagates bounding-box changes up insertion paths, splits overflowing nodes, and removes empty nodes while recomputing ancestor boxes during deletion. Bulk loading also handles merging trees of unequal height.
- **C3:** Bulk construction uses overlap-minimizing top-down partitioning with quickselect-based grouping. Search collects an entirely contained subtree without repeating intersection tests for each descendant; node capacity is a visible tuning parameter.
- **C2:** Bounding-box extraction, axis comparison, custom removal equality, serialization, and separate search/collision interfaces accommodate application objects, as shown in the [usage guide](https://github.com/mourner/rbush/blob/main/README.md).

Its dynamic object-oriented layout is especially instructive beside Flatbush's immutable packed representation.

### 20. [mourner/flatbush](https://github.com/mourner/flatbush)

**Language/role:** JavaScript; static packed Hilbert R-tree for 2D rectangles and points.

Study the architectural consequences of knowing the complete item count before construction.

- **C3:** [Construction and traversal](https://github.com/mourner/flatbush/blob/main/index.js) allocate the hierarchy up front, order items by Hilbert keys, and build parent levels bottom-up. A fully contained subtree can be collected as a contiguous leaf range rather than traversed node by node.
- **C1:** Loading checks buffer alignment, format magic, version, and coordinate-array type; construction requires the declared item count. These checks expose the binary representation's contract without establishing that it is a general-purpose hardened file parser.
- **C2:** The [API guide](https://github.com/mourner/flatbush/blob/main/README.md) provides rectangle and nearest-neighbor queries with filters, configurable coordinate storage, and transferable/shared buffers for workers.

The inability to insert or remove items after indexing is central to its design, not a missing dynamic-tree operation.

### 21. [tidwall/rtree.c](https://github.com/tidwall/rtree.c)

**Language/role:** C; compact configurable R-tree with copy-on-write cloning.

Study manual memory ownership in a spatial index that supports cheap structural sharing.

- **C1:** [The implementation](https://github.com/tidwall/rtree.c/blob/master/rtree.c) uses reference-counted nodes, copies shared nodes before mutation, and cleans up partially cloned leaf payloads when a user clone callback fails. Atomic reference counting is configurable; it does not by itself establish unrestricted concurrent mutation safety.
- **C2:** Custom allocators, item-clone/free hooks, dimension and numeric-type configuration, and callback-based search make the library reusable in C applications.
- **C3:** The [algorithm notes](https://github.com/tidwall/rtree.c/blob/master/README.md) explain a largest-axis split strategy intended to reduce sorting and overlap-comparison work. Comparing that choice with conventional R*-tree splitting is a useful engineering exercise.

The README's coverage percentage is an author claim, not a test result produced by this research.

### 22. [dhconnelly/rtreego](https://github.com/dhconnelly/rtreego)

**Language/role:** Go; N-dimensional dynamic R-tree with bounding-box and nearest-neighbor queries.

Study how a small language-level interface connects application objects to a mutable spatial index.

- **C2:** The [usage guide](https://github.com/dhconnelly/rtreego/blob/master/README.md) defines `Spatial`, custom deletion comparators, bulk loading, and filters that can reject a result or stop a search.
- **C1:** Moving an object requires deletion and reinsertion; mutating its bounds in place corrupts the index. The [implementation](https://github.com/dhconnelly/rtreego/blob/master/rtree.go) also addresses floating-point rounding in bulk-load height calculation and exposes tolerance for nearest-neighbor pruning calculations.
- **C3:** Overlap-minimizing top-down construction, reusable deletion buffers, and short-circuiting unchanged ancestor bounds address practical build and update costs.

The README correctly distinguishes balanced tree height from guaranteed query performance. The 3D-specialized fork is not counted as another project here.

### 23. [davidmoten/rtree](https://github.com/davidmoten/rtree)

**Language/role:** Java; immutable 2D R-tree/R*-tree with RxJava query results. This is the original reactive line; its README identifies `rtree2` as the next version with different API scope.

Study the interaction between persistent data structures and interruptible, backpressured queries.

- **C1:** The [architecture discussion](https://github.com/davidmoten/rtree/blob/master/README.md) describes retaining traversal position in an immutable stack for backpressure and avoiding recursive query traversal. Cancellation is part of the query contract.
- **C2:** Geometry interfaces and customizable selectors/splitters separate spatial semantics from balancing policy; reactive result streams support composition with consumer processing.
- **C3:** [Non-leaf update logic](https://github.com/davidmoten/rtree/blob/master/src/main/java/com/github/davidmoten/rtree/internal/NonLeafHelper.java) replaces only affected children and reconstructs the path while preserving other nodes. Deletion carries underfull-node entries upward for reinsertion, making both sharing and occupancy invariants visible.

It remains a substantive implementation to study even when selecting a different API line for new applications.

### 24. [tzaeschke/phtree](https://github.com/tzaeschke/phtree)

**Language/role:** Java; multidimensional PH-tree with bitwise spatial decomposition, point/box interfaces, and multiple internal implementations.

Study an alternative to geometric split heuristics and the evolution of its node representation.

- **C2:** [The core API](https://github.com/tzaeschke/phtree/blob/master/src/main/java/ch/ethz/globis/phtree/PhTree.java) supports window, nearest-neighbor, and distance queries, filtering, custom distances, and coordinate updates. Its single-value-per-key semantics are distinct from the separate multimap adapters.
- **C1:** Update failure when a destination key already exists, distance ties, and ownership of stored coordinate arrays are explicit semantic constraints.
- **C4:** The [2015–2025 changelog](https://github.com/tzaeschke/phtree/blob/master/CHANGELOG.md) records missed-result regressions, IEEE-conversion tests, Java compatibility fixes, and a substantial transition from AHC/LHC nodes to internal B+ trees. It documents the resulting memory tradeoff and the changed key-ownership contract, providing unusually concrete evidence of complexity management.

Only the Java project is counted; its related C++ implementations are not added as automatic duplicates.

## Coverage, search method, and limitations

Discovery used fourteen distinct live search formulations, including these angles:

- CPU ray-intersection kernels and standalone BVH builders: Embree, TinyBVH, NanoRT, and builder/traversal alternatives.
- HIP, OptiX, RadeonRays, and GPU traversal libraries, including explicit stack and acceleration-structure management.
- Rust ray-tracing BVHs and spatial indexes, including generic shapes, flattening, and update behavior.
- JavaScript mesh acceleration and the distinction between dynamic R-trees and packed static indexes.
- Scientific/HPC spatial search, Kokkos portability, distributed queries, and general geometry-library subsystems.
- C/C++ k-d trees, R-trees, Morton-ordered orthotrees, and allocator/layout choices.
- Java PH-trees and persistent/reactive R-trees, plus Go's spatial-object interfaces.
- Julia k-d/ball/periodic trees and C# ray/spatial searches as a further language-diversity check.

Repository pages/API metadata and additional source or documentation were inspected for every retained entry. Later broad ray-tracing queries increasingly returned the same kernels, tutorial renderers, benchmark consumers, or thin bindings; the Julia pass supplied a distinct metric-tree implementation. Selection stopped after that added coverage and diminishing returns elsewhere, rather than filling every possible language or tree family.

Excluded classes include standalone path tracers, “ray tracing in a weekend” projects, API sample collections, awesome lists, generated bindings, and spatial databases whose central subject is query/database infrastructure. Deprecated Julia `KDTrees.jl` was superseded in this selection by `NearestNeighbors.jl`; `LibSpatialIndex.jl` is a binding to an implementation already represented. Additional projects surfaced during discovery—such as blazeRT, TinSpin, geo-index, and Visionaray—were not all taken through full verification, so their omission is not a negative quality judgment.

All 24 retained repositories reported `archived: false` in the GitHub metadata checked. That is not a claim of uniform active maintenance or release cadence. No repository in this selection is presented as an official mirror; GitHub ownership redirects were resolved for Embree and ArborX. Historical/alternative-line context is called out for the reactive Java R-tree, and NanoRT's default branch and nanoflann's fork lineage are explicit.

Correctness assessments identify contracts, checks, and invariants present in the inspected material; they are not proof that all edge cases are handled. Performance assessments identify concrete mechanisms, not independently measured superiority. C4 is assigned only where multi-year change history supplies substantive compatibility, regression, or architectural evidence. Graphics kernels remain predominantly C++, while the broader index selection adds Rust, JavaScript, Java, Go, C, and Julia. This is a selection guide for comparative code study, not an exhaustive catalogue or a uniform endorsement of every component.
