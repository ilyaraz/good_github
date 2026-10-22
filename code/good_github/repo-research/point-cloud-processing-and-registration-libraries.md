# Point cloud processing and registration libraries

Research date: **2026-10-09**.

This selection covers reusable libraries for point cloud storage, filtering, sampling, geometric estimation, LiDAR processing, and rigid or deformable registration. It includes broad frameworks, focused numerical libraries, and a few clearly identified historical implementations. General geometry monorepos are included only for their point cloud subsystems. The 23 entries are a guide to engineering ideas worth studying, not a claim that every component is equally reliable or appropriate for production.

Criteria legend:

- **C1 — Correctness:** difficult numerical semantics, geometric invariants, concurrency, invalid inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and data structures supporting multiple applications.
- **C3 — Performance:** meaningful memory or computation constraints addressed through understandable architecture.
- **C4 — Evolution:** sustained development with concrete compatibility, testing, or complexity-management evidence.

Canonical repository names, default branches, and archive flags were checked through the public GitHub API. None of the selected repositories was marked archived at the research date; that alone does not establish active maintenance. Sources below were opened and read, including implementation files or substantive architecture documentation for every entry.

## General-purpose processing and geometry

### 1. [PointCloudLibrary/pcl](https://github.com/PointCloudLibrary/pcl)

**C++; broad point cloud processing framework.** Study how an extensive collection of algorithms is organized around point types, search methods, correspondences, and transformation estimation. The registration subsystem is a particularly useful entry into the larger codebase.

- **C1:** Registration explicitly separates correspondence generation from rejection, including reciprocal matching, RANSAC, trimming, and handling one-to-many matches. These choices determine whether the numerical transformation estimate has meaningful input.
- **C2:** Keypoints, descriptors, correspondence estimators, rejection stages, and motion estimators can be assembled into different pipelines. Both points and feature descriptors can drive matching. See the [registration architecture guide](https://pointclouds.org/documentation/tutorials/registration_api.html).
- **C4:** The [changelog](https://github.com/PointCloudLibrary/pcl/blob/master/CHANGES.md) documents evolution across many years: the 2020 smart-pointer migration used previously introduced aliases, while later releases distinguish deprecations, removals, behavior changes, and ABI changes. This is concrete compatibility management, not merely longevity.

### 2. [isl-org/Open3D](https://github.com/isl-org/Open3D)

**C++ and Python, with accelerator backends; integrated 3D processing.** Focus on the tensor geometry and registration pipeline, where device placement, convergence policy, and geometric operations meet.

- **C1:** The [tensor ICP guide](https://www.open3d.org/docs/release/tutorial/t_pipelines/t_icp_registration.html) explains initialization sensitivity, robust losses, correspondence thresholds, and the failure case where both fitness and inlier RMSE are zero because there are no correspondences. A small RMSE alone is therefore insufficient evidence of alignment.
- **C2:** Transformation estimators, robust kernels, convergence criteria, and iteration callbacks are explicit API objects rather than a single fixed registration procedure.
- **C3:** The same guide describes coarse-to-fine ICP with separate voxel sizes, distance thresholds, and iteration budgets at each scale, and execution on the device holding the point clouds. Study how the API exposes performance controls without hiding their numerical consequences.

### 3. [CGAL/cgal](https://github.com/CGAL/cgal)

**C++; the `Point_set_processing_3` subsystem of a geometry monorepo.** This entry concerns point set processing, not CGAL's entire collection. It is valuable for studying generic algorithms over caller-owned data.

- **C2:** The [point set processing manual](https://doc.cgal.org/latest/Point_set_processing_3/index.html) uses ranges, named parameters, and property maps so points and normals can live in tuples, custom objects, or separate containers. The same abstractions support simplification, smoothing, normal estimation, and other operations.
- **C1:** The [bilateral smoothing implementation](https://github.com/CGAL/cgal/blob/main/Point_set_processing_3/include/CGAL/bilateral_smooth_point_set.h) specifies neighborhood and input preconditions, handles cancellation, and documents that parallel callbacks must not mutate algorithm inputs.
- **C3:** That implementation separates neighbor discovery from calculation of updated points and normals, uses concurrency tags, and stages output before writing it back. This makes both the parallel work and its memory cost visible.

### 4. [CloudCompare/CCCoreLib](https://github.com/CloudCompare/CCCoreLib)

**C++; standalone computational core extracted from CloudCompare.** Study point cloud comparison and registration infrastructure independently of the desktop application's GUI. The repository explicitly explains its extraction from the former CCLib subsystem.

- **C1:** The [distance computation API](https://github.com/CloudCompare/CCCoreLib/blob/master/include/DistanceComputationTools.h) states that reused cloud octrees must share the same cubical bounding box. It also distinguishes squared unsigned point-to-triangle distances from signed distances and documents incompatible acceleration options.
- **C2:** Algorithms accept abstract indexed clouds, parameter structures, and progress callbacks, making them usable with different storage implementations and applications.
- **C3:** Octree level, maximum search distance, reusable spatial indexes, and approximate distance transforms expose explicit accuracy–memory–runtime tradeoffs. The same header is an unusually concrete map of those contracts.

### 5. [kzampog/cilantro](https://github.com/kzampog/cilantro)

**C++; templated processing and registration library.** A useful smaller counterpart to PCL for studying how rigid, affine, and deformable registration can share an extensible structure.

- **C2:** The [ICP base](https://github.com/kzampog/cilantro/blob/master/include/cilantro/registration/icp_base.hpp) separates the transform type, correspondence search engine, residual representation, and derived algorithm. Its CRTP loop delegates correspondence and estimate updates while retaining iteration and convergence bookkeeping.
- **C1:** The [transform estimators](https://github.com/kzampog/cilantro/blob/master/include/cilantro/registration/transform_estimation.hpp) distinguish isometric and affine problems, reject empty or mismatched point sets, and correct an SVD reflection before constructing a rigid transform.
- **C3:** The affine estimator exposes optional parallel normal-equation accumulation under an explicitly named nondeterministic-parallelism switch. This is a useful place to examine the tension between reduction order and throughput.

### 6. [fwilliams/point-cloud-utils](https://github.com/fwilliams/point-cloud-utils)

**Python API with C++ implementations; sampling and geometry utilities.** Study a collection of composable NumPy-oriented operations covering cloud downsampling, normals, distances, and cloud–mesh interactions. Although it integrates other geometry libraries, it also contains substantive implementation logic of its own.

- **C1:** The [point sampling implementation](https://github.com/fwilliams/point-cloud-utils/blob/master/src/sample_point_cloud.cpp) handles radius-based and target-count sampling separately, validates tolerance parameters, and explicitly bounds part of the search for an appropriate sampling radius. Target counts are approximate, not an exact cardinality guarantee.
- **C3:** Blue-noise downsampling uses spatial cells, sorted point coordinates, hash maps, active samples, and squared-radius comparisons instead of treating all point pairs uniformly.
- **C2:** The same file preserves selected point indices and supports voxel aggregation with attributes, useful building blocks for larger processing pipelines. The [repository overview](https://github.com/fwilliams/point-cloud-utils) connects these operations to the wider distance, normal, and mesh APIs.

## Composable local registration

### 7. [norlab-ulaval/libpointmatcher](https://github.com/norlab-ulaval/libpointmatcher)

**C++ with Python bindings; configurable 2D/3D ICP.** Particularly useful for studying a registration algorithm as a sequence of replaceable policies.

- **C2:** The [configuration guide](https://github.com/norlab-ulaval/libpointmatcher/blob/master/doc/Configuration.md) separates reading and reference filters, matcher, outlier filters, error minimizer, transformation checkers, inspector, and logger. YAML and in-memory configuration expose the same conceptual pipeline.
- **C1:** Filter order is semantically significant: a filter requiring descriptors must follow the filter that generates them. Transformation checkers and outlier policies make stopping and rejection explicit rather than incidental details of the loop.
- **C2, further evidence:** The [cloud representation guide](https://github.com/norlab-ulaval/libpointmatcher/blob/master/doc/PointClouds.md) describes homogeneous feature matrices and separately labeled descriptor matrices, parameterized by scalar type. This supports sensor-specific attributes while preserving the registration interfaces.

### 8. [koide3/small_gicp](https://github.com/koide3/small_gicp)

**Header-only C++ with Python bindings; parallel local registration.** A rewrite of the author's earlier fast_gicp, with different integration boundaries. It is especially instructive for policy-based numerical code and parallel accumulation.

- **C1:** The [registration template](https://github.com/koide3/small_gicp/blob/master/include/small_gicp/registration/registration.hpp) re-orthonormalizes the initial rotation to prevent accumulated composition drift from being carried through rigid increments. Its contract excludes scale and reflection in the initial guess.
- **C2:** Point factors, reduction strategy, general factors, correspondence rejection, and optimizer are independently parameterized; cloud and search types enter through traits.
- **C3:** The [OpenMP reduction](https://github.com/koide3/small_gicp/blob/master/include/small_gicp/registration/reduction_omp.hpp) accumulates Hessians, gradients, and errors per thread before combining them. It provides a compact, readable example of parallelizing the expensive numerical kernel. This repository does not include GPU registration implementations.

### 9. [MOLAorg/mp2p_icp](https://github.com/MOLAorg/mp2p_icp)

**C++; multi-primitive registration and cloud-processing libraries.** Study its reusable registration core rather than treating the repository as a complete SLAM system. Named map layers can hold clouds alongside extracted planes and lines.

- **C2:** The [data model documentation](https://github.com/MOLAorg/mp2p_icp/blob/develop/docs/source/mp2p_icp_basics.rst) explains layered metric maps. The [ICP implementation](https://github.com/MOLAorg/mp2p_icp/blob/develop/mp2p_icp_core/mp2p_icp/src/ICP.cpp) composes matchers, solvers, and quality evaluators, including a solver sequence that can try another solver after failure.
- **C1:** Termination distinguishes absent pairings, solver failure, stalled progress, quality-checkpoint failure, and iteration exhaustion. Pose increments are measured through the SE(3) logarithm, and final transform covariance is computed from pairings.
- **C3:** Profiling scopes identify individual stages; optional pairing reuse and intermediate quality checkpoints address avoidable work. The introductory documentation has unfinished algorithm sections, so the implementation is the stronger entry point.

### 10. [seqsense/pcgol](https://github.com/seqsense/pcgol)

**Go; independent point cloud processing library.** A less prominent implementation spanning binary cloud access, spatial storage, filtering, segmentation, and registration. The project explicitly says it is not a PCL port.

- **C2:** The [ICP loop](https://github.com/seqsense/pcgol/blob/master/pc/registration/icp/icp.go) accepts a spatial-search interface, random-access point interface, evaluator, and updater factory. Storage, correspondence evaluation, and optimization can vary independently.
- **C1:** The [point-to-point evaluator](https://github.com/seqsense/pcgol/blob/master/pc/registration/icp/evaluator.go) includes the small-angle rotation derivative, checks minimum correspondence counts, and limits rotation gradients because the approximation can become misleading when alignment is poor. The loop propagates evaluation errors with its current transform and statistics.

These files offer a manageable study of numerical behavior in Go without a large foreign-function layer; they do not imply that all registration variants found in larger frameworks are implemented.

## GPU and accelerator-oriented implementations

### 11. [koide3/fast_gicp](https://github.com/koide3/fast_gicp)

**C++/CUDA; GICP, voxelized GICP, and NDT implementations.** The repository points users toward small_gicp for a newer CPU design. It remains a distinct selection because of its CUDA implementations and PCL-compatible registration interface.

- **C2:** Its [overview](https://github.com/koide3/fast_gicp) describes interchangeable PCL registration implementations with different parallelization strategies.
- **C3:** The [CUDA VGICP core](https://github.com/koide3/fast_gicp/blob/master/src/fast_gicp/cuda/fast_vgicp_cuda.cu) separates device-resident point and covariance storage, neighborhood discovery, Gaussian voxel map construction, correspondence updates, and derivative calculation. Neighbor search can use different voxel-offset patterns.
- **C1:** Covariance estimation and regularization are explicit preprocessing steps before the registration objective is evaluated. Study how float device representations and double-facing transformation/Hessian interfaces meet.

No headline frame-rate claims are adopted here; hardware, preprocessing, and data reuse materially affect such comparisons.

### 12. [neka-nat/cupoch](https://github.com/neka-nat/cupoch)

**C++/CUDA with Python bindings; GPU robotics geometry.** The project is derived from Open3D, but its substantive device-memory algorithms justify a separate entry. Registration, filtering, features, and other geometry operations are implemented around GPU data.

- **C3:** The [registration implementation](https://github.com/neka-nat/cupoch/blob/main/src/cupoch/registration/registration.cu) builds correspondences with device vectors, removes invalid entries on the device, and computes error through a Thrust reduction. Host/device transfers are explicit in the result accessors.
- **C1:** ICP validates the correspondence distance and required normals; evaluation defines behavior for an empty correspondence set. Fitness and RMSE are calculated separately, exposing why one statistic cannot stand in for the other.
- **C2:** Transformation estimation and convergence criteria remain separate API concepts despite the accelerator-specific execution. The [repository overview](https://github.com/neka-nat/cupoch) documents its broader GPU processing scope and Open3D lineage.

## Robust, global, probabilistic, and multi-cloud registration

### 13. [MIT-SPARK/TEASER-plusplus](https://github.com/MIT-SPARK/TEASER-plusplus)

**C++ with Python/MATLAB bindings; robust registration from correspondences.** Study the decomposition of a heavily contaminated correspondence problem into scale, rotation, translation, and inlier-selection subproblems.

- **C1:** The [solver interfaces and parameters](https://github.com/MIT-SPARK/TEASER-plusplus/blob/master/teaser/include/teaser/registration.h) make the measurement noise bound, truncated least-squares estimators, rotation convergence rules, and inlier-selection modes explicit. Exact and heuristic clique selection are distinct options.
- **C2:** Abstract scale, rotation, and translation solvers allow algorithm substitutions; the composite solver manages their configuration and resets intermediate inlier state.
- **C3:** Chain versus complete translation-invariant measurement graphs, clique time limits, thread counts, and optional scale estimation expose major computational choices.

The repository's “certifiable” framing should be read with the selected algorithm and assumptions in mind; it is not a guarantee that arbitrary correspondences and every heuristic configuration recover the desired alignment.

### 14. [STORM-IRIT/OpenGR](https://github.com/STORM-IRIT/OpenGR)

**C++; global registration through congruent-set exploration.** This is an author-led fork/evolution of Super4PCS, which is not counted separately here.

- **C1:** The [congruent-set base](https://github.com/STORM-IRIT/OpenGR/blob/master/src/gr/algorithms/congruentSetExplorationBase.h) connects overlap estimates to sampling trials, restricts base diameter to improve the chance of inlier bases, and defines a directional largest-common-point score. “Global registration” here does not mean the same optimality guarantee as exhaustive branch-and-bound.
- **C2:** Point types, traits, pair-filtering functors, samplers, and transform visitors are independent customization points.
- **C2, evolution evidence:** The [changelog](https://github.com/STORM-IRIT/OpenGR/blob/master/CHANGELOG) records conversion to header-only libraries, a point-type abstraction layer, functor-based algorithms, interoperability work, and numerical fixes. These changes establish substantive evolution beyond a duplicate fork.

### 15. [yangjiaolong/Go-ICP](https://github.com/yangjiaolong/Go-ICP)

**C++; historical global-registration reference implementation.** Useful primarily for studying bounded search and its assumptions. GitHub metadata reports a last push in 2019; it is not archived, but this report does not present it as a currently maintained general framework.

- **C1:** The [branch-and-bound implementation](https://github.com/yangjiaolong/Go-ICP/blob/master/jly_goicp.cpp) nests translation search inside rotation search, maintains lower and upper bounds, and prunes subcubes against the best known objective. Trimming changes the inlier count and the conversion from an MSE threshold to an SSE threshold.
- **C3:** A precomputed distance transform accelerates repeated closest-distance evaluation; ICP supplies improved candidate solutions, and partial selection avoids fully sorting all distances for trimming.

The [usage and numerical notes](https://github.com/yangjiaolong/Go-ICP) require normalization, bounded search configuration, and appropriate trimming. Distance-transform resolution trades memory and construction time against distance accuracy, limiting how mathematical optimality claims should be interpreted for a concrete run.

### 16. [neka-nat/probreg](https://github.com/neka-nat/probreg)

**Python with native components; probabilistic rigid and deformable registration.** The collection includes CPD, GMM-based methods, FilterReg, and Bayesian CPD. It is useful for comparing probability-based correspondence models within one package.

- **C2:** The [FilterReg implementation](https://github.com/neka-nat/probreg/blob/master/probreg/filterreg.py) separates expectation and maximization steps, transformation classes, feature functions, and callbacks; rigid and deformable variants share the iteration structure.
- **C1:** It clamps the variance to a minimum, handles vanishing correspondence mass, distinguishes point-to-point from point-to-plane objectives, and stops based on objective change. These are substantive numerical contracts of the EM-like loop.
- **C3:** The expectation step uses permutohedral Gaussian filtering, with a lattice-size-dependent choice, to address the cost of probabilistic interactions. This provides an implementation-level performance lesson beyond merely exposing a faster backend.

### 17. [gadomski/cpd](https://github.com/gadomski/cpd)

**C++; coherent point drift library.** A focused alternative to a broad registration framework, useful for studying how shared probability calculations support different transform models.

- **C2:** The [generic transform implementation](https://github.com/gadomski/cpd/blob/main/include/cpd/transform.hpp) centralizes normalization, iteration control, callbacks, probability calculation, and result handling while derived transforms supply initialization and per-iteration estimation.
- **C1:** It makes outlier weight, variance initialization, normalization/denormalization, and the small-variance stopping condition visible. Optional correspondence extraction is a separate operation rather than an assumed byproduct of every run.
- **C3:** The [fast Gauss transform backend](https://github.com/gadomski/cpd/blob/main/src/gauss_transform_fgt.cpp) supports tree-based direct evaluation, improved fast Gauss transforms, and a bandwidth-dependent switch. This is a concrete strategy for reducing CPD's expensive Gaussian summations.

### 18. [pglira/Point_cloud_tools_for_Matlab](https://github.com/pglira/Point_cloud_tools_for_Matlab)

**MATLAB; cloud manipulation and simultaneous multi-cloud ICP.** An older toolbox with a `pointCloud` class and a `globalICP` class. Its repository recommends simpleICP for simpler two-cloud cases while retaining this toolbox for more flexible multi-cloud work. The last API-reported push was in 2023; current maintenance is not assumed.

- **C1:** The [method description](https://www.geo.tuwien.ac.at/pg/pctools/globalICPGeneralDescription.html) explains rejection by distance, roughness, and normal angle, correspondence weighting, and robust least-squares adjustment of point-to-plane residuals.
- **C2:** Cloud manipulation and registration are separate classes, and registration handles multiple clouds with configurable transformation models. Approximate initial alignment is required: “globalICP” refers to the multi-cloud adjustment, not initialization-free global optimization.
- **C3:** [Advanced selection strategies](https://www.geo.tuwien.ac.at/pg/pctools/globalICPAdvancedSelection.html) use normal-space or maximum-leverage sampling to retain geometrically informative constraints while reducing the number of points processed.

## Large LiDAR datasets, memory models, and processing pipelines

### 19. [PDAL/PDAL](https://github.com/PDAL/PDAL)

**C++; point data processing and format-independent pipelines.** Study how a processing framework reconciles dynamically described point attributes with reusable readers, filters, writers, and bounded-memory execution.

- **C2:** The [architecture overview](https://pdal.io/en/latest/development/overview.html) distinguishes `PointLayout`, `PointTable`, `PointView`, and `PointRef`. Views refer to shared points rather than implicitly copying them, and attribute dimensions carry explicit storage types.
- **C1:** Dimension type promotion must accommodate values requested by multiple stages; view IDs are local references, so appending an existing point to another view does not create an independent point. Those semantics matter when stages mutate attributes.
- **C3:** `FixedPointTable` and `StreamPointTable` support bounded point storage, while streaming stages operate through `processOne()`. A pipeline containing an incompatible stage fails instead of silently claiming to stream. This is a strong example of making memory behavior part of the stage contract.

### 20. [igd-geo/pasture](https://github.com/igd-geo/pasture)

**Rust; point cloud memory abstractions, I/O, and processing.** Especially useful for studying dynamic point schemas without forcing one physical layout or ownership model.

- **C2:** The [buffer architecture](https://github.com/igd-geo/pasture/blob/main/pasture-core/src/containers/mod.rs) separates memory ownership from memory layout. Owned, borrowed, and mutably borrowed buffers can expose interleaved or columnar data; slices preserve layout capabilities.
- **C1:** Runtime `PointLayout` information supports typed views over byte storage. The [buffer contracts](https://github.com/igd-geo/pasture/blob/main/pasture-core/src/containers/point_buffer.rs) document bounds, attribute type, size, and alignment requirements, with unchecked operations explicitly marked unsafe.
- **C3:** Layout-specific borrows permit direct point or attribute access, while external-memory buffers avoid requiring all callers to adopt an owning container. The project describes itself as early-stage; these abstractions are a study target, not evidence of a frozen API.

### 21. [r-lidar/lidR](https://github.com/r-lidar/lidR)

**R and C++; LiDAR analysis, particularly forestry and terrain workflows.** The catalog engine is a strong example of making spatial partitioning correctness part of an extension API.

- **C1:** The [catalog engine implementation and contracts](https://github.com/r-lidar/lidR/blob/master/R/catalog_apply.R) address overlapping buffers, duplicate output, empty chunks, and raster alignment. Neighborhood operations need data beyond tile boundaries, but results from those buffers must be cropped consistently.
- **C2:** User functions can operate through the flexible `catalog_apply()` contract or the simpler `catalog_map()` interface, which handles routine reading, empty-input checks, and cropping.
- **C4:** The [2022–2026 release history](https://github.com/r-lidar/lidR/blob/master/NEWS.md) records spatial-package interoperability changes, on-disk raster support, simplified catalog interfaces, and fixes for triangulation and grid-partition accuracy. It demonstrates sustained compatibility and numerical-complexity management.

### 22. [r-lidar/lasR](https://github.com/r-lidar/lasR)

**C++ core with R and Python APIs; large-scale LiDAR pipelines.** A separate implementation from lidR, with internal C++ cloud storage and stage pipelines. Its concurrency model is the main reason to study it alongside lidR.

- **C2:** The [stage interface](https://github.com/r-lidar/lasR/blob/main/src/LASRcore/Stage.h) describes lifecycle order, processing at point/cloud/header levels, streamability, buffer requirements, dependencies, and resource cleanup.
- **C1:** Parallel file processing requires cloning stages, updating inter-stage pointers, merging output, and optionally restoring order. The [parallel-processing documentation](https://github.com/r-lidar/lasR/blob/main/vignettes/multithreading.Rmd) also explains why stages calling the R C API cannot safely execute through concurrent-file processing.
- **C3:** Sequential, concurrent-point, concurrent-file, and nested strategies have distinct CPU, disk, and memory consequences. This is a useful example of exposing parallelism according to the workload's actual bottleneck.

### 23. [efpl-columbia/PointClouds.jl](https://github.com/efpl-columbia/PointClouds.jl)

**Julia; LiDAR acquisition and processing primitives.** A smaller, newer library that brings Julia-specific type and array considerations into point cloud processing. Its README explicitly allows frequent breaking changes.

- **C2:** The [processing guide](https://github.com/efpl-columbia/PointClouds.jl/blob/main/docs/src/point-processing.md) describes tabular point attributes, neighborhood-aware operations, CRS transformations, and rasterized views that can be mapped with user functions.
- **C3:** The guide explains function barriers for dynamically typed attribute containers and multithreaded `apply`. The [rasterization implementation](https://github.com/efpl-columbia/PointClouds.jl/blob/main/src/rasterization.jl) groups point indices using offsets and prefix sums, then exposes views into attribute arrays rather than copying each cell's attributes.
- **C1:** CRS is an immutable cloud property; assigning a CRS where none exists does not itself transform coordinates. Rasterization also checks dimensional and index invariants. The inspected rasterization implementation supports 2D grids; its generic-looking structures should not be mistaken for complete 3D voxel support.

## Search coverage and limitations

Discovery used more than six distinct query families: general PCL/Open3D-style frameworks; robust and global registration; probabilistic/nonrigid point-set registration; CUDA/SYCL processing; Rust memory and streaming libraries; native Go processing; R/Julia LiDAR analysis; MATLAB and Java/C# alternatives; and modular multi-primitive ICP. Follow-up searches found both smaller projects and lineage relationships. The final broad registration and language searches increasingly returned already-covered libraries, paper collections, application-specific code, and bindings rather than additional broadly reusable implementations.

Primary verification combined repository pages, GitHub metadata and source-tree APIs, individual source files, official manuals, and changelogs. No candidate repository was cloned, built, installed, or executed. Performance observations above describe mechanisms inspected in code or documentation; no cross-project speed ranking is claimed. Criteria assignments and suggested engineering lessons are grounded interpretations of those mechanisms, not results of an independent correctness audit.

Thin bindings such as GeoRust's PDAL wrapper were not counted as independent algorithm implementations. Super4PCS was represented by its author-led OpenGR evolution; CloudCompare's GUI was represented by CCCoreLib. Cupoch is explicitly identified as Open3D-derived, and the two Koide libraries are distinguished by their rewritten CPU architecture versus GPU code. General nearest-neighbor packages, file-format-only readers, viewers, complete SLAM applications, and deep-learning paper repositories were outside the main selection. Pure NumPy CPD implementations and additional research solvers were considered but not added merely to multiply similar registration examples.

Coverage is strongest in C++ and scientific/robotics ecosystems, with substantive Rust, Go, Julia, R, Python, and MATLAB perspectives. Java/C# discovery did not yield a retained project with stronger independently verified fit than this selection; this is a search limitation, not a claim that such projects do not exist. Historical Go-ICP and the older MATLAB toolbox are included for their numerical designs. Archive status and a recent push are not treated as C4 evidence or a maintenance guarantee.
