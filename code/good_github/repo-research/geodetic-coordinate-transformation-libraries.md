# Geodetic coordinate transformation libraries

Research date: **2026-10-09**

This selection covers reusable implementations of coordinate reference system (CRS) transformations, datum and reference-frame changes, map projections, and conversions among geodetic, Earth-centered Earth-fixed (ECEF), and local coordinates. It includes both general transformation engines and smaller numerical libraries. A projection conversion on one ellipsoid is not necessarily a datum transformation; the entries distinguish these capabilities. The 23 repositories are selected for engineering study, not ranked by popularity or presented as uniformly exemplary.

Criteria legend:

- **C1 — Difficult correctness:** numerical stability, coordinate/frame invariants, units, epochs, concurrency, or explicit failure behavior.
- **C2 — Reusable abstractions:** substantial APIs or composable models supporting multiple applications.
- **C3 — Performance with structure:** identifiable design choices addressing repeated transformations, bulk data, or constrained execution.
- **C4 — Sustained evolution:** changes across years accompanied by compatibility work, testing, or complexity management. Age alone does not qualify.

The linked implementation files and documentation within each entry are the recommended reading entry points. Repository headings link to verified canonical GitHub locations. Unless a status is explicitly described, inclusion makes no claim about current maintenance capacity.

## General CRS engines and transformation frameworks

### 1. [OSGeo/PROJ](https://github.com/OSGeo/PROJ)

**C and C++ — general projection, datum, and spatiotemporal transformation engine.** Study how a projection library grew into an operation-composition system while accommodating earlier transformation semantics.

- **C1:** Its transformation documentation makes ordering and units concrete: geodetic coordinates become Cartesian before a Helmert transformation, time coordinates may require conversion before a dynamic transformation, and horizontal/vertical grid ordering depends on the interpolation CRS. These are semantic requirements that simple “convert EPSG A to B” interfaces can conceal.
- **C2:** A pipeline composes elementary operations, including Cartesian conversions, Helmert transformations, polynomial shifts, and unit conversions, into reusable transformations. The documentation also explains the transition from a WGS84 pivot to late-bound operations. Start with the [transformation architecture](https://proj.org/en/stable/usage/transformation.html).
- **C4:** The dated [historical ChangeLog](https://github.com/OSGeo/PROJ/blob/master/ChangeLog) records 2015 locale, threading, domain, and precision repairs; the [release notes](https://github.com/OSGeo/PROJ/blob/master/NEWS.md) document later API evolution, regression testing, and database compatibility repairs. This is evidence of sustained complexity management, not merely an old founding date.

### 2. [pyproj4/pyproj](https://github.com/pyproj4/pyproj)

**Python and Cython — a substantial Python interface to PROJ.** This is useful for studying the engineering above a native numerical engine: lifecycle management, operation discovery, array-friendly APIs, and Python concurrency.

- **C1:** `TransformerLocal` stores the native transformer separately for each thread. The inspected implementation distinguishes native versions when cloning an existing operation versus recreating it. `TransformerGroup` exposes unavailable operations caused by missing grids, rather than reducing every CRS pair to an unexplained result. See [transformer.py](https://github.com/pyproj4/pyproj/blob/main/pyproj/transformer.py).
- **C2:** `CRS`, reusable `Transformer` objects, operation groups, areas of interest, and explicit 2D/3D promotion provide reusable abstractions beyond generated bindings.
- **C3:** Transformer reuse and caching avoid repeated operation construction. The [advanced examples](https://pyproj4.github.io/pyproj/stable/advanced_examples.html) explain these costs, missing-grid inspection, dimensionality, and threading. Published timing examples are illustrative; no speed ratio was independently reproduced here.

### 3. [apache/sis](https://github.com/apache/sis)

**Java — Apache Spatial Information System; specifically its referencing and coordinate-operation subsystem.** Count this monorepo once. It is an **official GitHub mirror**, explicitly identified by the project's [source documentation](https://sis.apache.org/source.html).

- **C1:** The `MathTransforms` contracts specify dimension matching, monotonicity requirements for invertible interpolation, and constraints on specialized transforms within geographic subareas. Its tangent approximation has an explicit invariant at the chosen position. These contracts make numerical applicability and composition failures reviewable.
- **C2:** Concatenated, compound, pass-through, linear, interpolated, and geographically specialized transforms share a common interface. A compound transformation can process horizontal, vertical, and temporal components independently while preserving dimension rules. The [MathTransforms API](https://sis.apache.org/apidocs/org.apache.sis.referencing/org/apache/sis/referencing/operation/transform/MathTransforms.html) is a strong architectural entry point.

SIS is particularly useful for studying standards-oriented interfaces and the boundary between generic mathematical transforms and CRS metadata. Its source documentation also explains compatibility branches for released versus experimental GeoAPI interfaces.

### 4. [locationtech/proj4j](https://github.com/locationtech/proj4j)

**Java — native Java CRS reprojection and datum conversion.** Study a compact, explicit transformation strategy rather than assuming it implements every capability of contemporary PROJ.

- **C1:** `BasicCoordinateTransform` sequences axis normalization, inverse projection, prime-meridian adjustment, datum conversion, and destination projection. Its datum logic distinguishes grid shifts from geocentric transformations and adjusts ellipsoid handling around the WGS84 pivot.
- **C2:** CRS objects, coordinate-transform factories, datum objects, and projection implementations divide definition parsing from point transformation.
- **C3:** The constructor precomputes whether inverse projection, forward projection, and geocentric conversion are needed; repeated point calls reuse those decisions and converters. All three aspects are visible in [BasicCoordinateTransform.java](https://github.com/locationtech/proj4j/blob/master/core/src/main/java/org/locationtech/proj4j/BasicCoordinateTransform.java).

The repository also documents the separation of the core and EPSG artifacts. The primary study value is the interaction of a relatively small API with the many conditional paths required for a correct datum-aware transformation.

### 5. [orbisgis/cts](https://github.com/orbisgis/cts)

**Java — Coordinate Transformation Suite, an independent operation-oriented implementation.** A less prominent alternative worth studying for sequence algebra and explicit convergence control.

- **C1:** `IterativeTransformation` repeats an operation until selected coordinate components meet tolerances and raises `TooManyIterationsException` after its iteration limit. It specifically addresses transformations in which grid lookup coordinates depend on an approximate earlier result. See [IterativeTransformation.java](https://github.com/orbisgis/cts/blob/master/src/main/java/org/cts/op/IterativeTransformation.java).
- **C2:** `CoordinateOperationSequence` provides composition and constructs inverses by reversing the sequence and inverting its members; noninvertible operations propagate a specific exception.
- **C3:** Sequence construction removes identities and cancels adjacent inverse operations, including across nested sequence boundaries. This is a concrete optimization of reusable operation graphs, visible in [CoordinateOperationSequence.java](https://github.com/orbisgis/cts/blob/master/src/main/java/org/cts/op/CoordinateOperationSequence.java).

Its precision aggregation is a library-level estimate; it should not be mistaken for a complete statistical uncertainty model.

## Native implementations for web, Rust, PHP, and .NET

### 6. [proj4js/proj4js](https://github.com/proj4js/proj4js)

**JavaScript — browser and Node.js projection and datum transformations.** This is a substantive native implementation descended from PROJ-family code, not a remote conversion-service client.

- **C1:** The transformation implementation checks inputs, normalizes axes when requested, converts angular and linear units, adjusts prime meridians, routes applicable datum changes through WGS84, and preserves whether an input had a height component. It clones input point objects before transformation. See [transform.js](https://github.com/proj4js/proj4js/blob/main/lib/transform.js).
- **C2:** The public API accepts reusable projection definitions and exposes forward/inverse transformation objects. The repository documents PROJ strings, WKT and PROJJSON input, and separately registered grid data. This makes it useful for studying how flexible JavaScript data shapes meet a shared transformation engine.

An important reading question is which behavior belongs to CRS metadata, optional axis enforcement, or the coordinate object itself. Its lineage does not establish feature equivalence with current PROJ.

### 7. [3liz/proj4rs](https://github.com/3liz/proj4rs)

**Rust — native PROJ.4-style transformations for Rust and WebAssembly.** The repository explicitly positions the library as lightweight and documents exclusions for full 3D/4D/orthometric transformation functionality; native angular values are radians.

- **C1:** The transformation driver rejects missing forward/inverse implementations and orders axis, height-unit, projection, prime-meridian, and datum stages. Fallible coordinate closures expose transformation errors rather than hiding them.
- **C2:** The `Transform` trait makes the driver independent of coordinate storage. A caller can implement it for a single point or a collection and choose how per-coordinate failures affect collection processing. Study [transform.rs](https://github.com/3liz/proj4rs/blob/main/proj4rs/src/transform.rs).

This is a useful example of adapting an established numerical pipeline to Rust traits and error propagation. The presence of three-component inputs and internal geocentric steps should not be read as contradicting the project's narrower documented end-to-end scope.

### 8. [busstoptaktik/geodesy](https://github.com/busstoptaktik/geodesy)

**Rust — Rust Geodesy, a platform for geodetic operations and alternative data-flow designs.** Its scope includes reusable primitives and pipelines, with an explicit experimental-design emphasis.

- **C1:** The Helmert implementation handles static and dynamic parameters, validates position-vector versus coordinate-frame rotation conventions, and rejects a missing reference epoch when required. Forward and inverse paths share an implementation. See [helmert.rs](https://github.com/busstoptaktik/geodesy/blob/main/src/inner_op/helmert.rs), which also contains numerical tests.
- **C2:** The `Context` trait separates operation creation/application from access to grids, parameter resources, user-defined operators, and coordinate storage. Handles identify constructed operations, and `CoordinateSet` abstracts their operands. See [context/mod.rs](https://github.com/busstoptaktik/geodesy/blob/main/src/context/mod.rs).

The architectural distinction from a direct PROJ wrapper is material: applications can supply their own context and resource behavior while using the same operation vocabulary.

### 9. [NetTopologySuite/ProjNet4GeoAPI](https://github.com/NetTopologySuite/ProjNet4GeoAPI)

**C# — ProjNet spatial reference and projection engine.** The canonical repository name still includes GeoAPI, while the README distinguishes the older ProjNet4GeoAPI and newer ProjNet packages. **Status:** the README says the team lacks resources to support the project at present.

- **C1:** The geocentric conversion code addresses polar cases and selects height formulas according to latitude-related quantities. Its contract also explains prime-meridian and ellipsoid-unit prerequisites. See [GeocentricTransform.cs](https://github.com/NetTopologySuite/ProjNet4GeoAPI/blob/develop/src/ProjNet/CoordinateSystems/Transformations/GeocentricTransform.cs).
- **C2:** `CoordinateTransformationFactory` dispatches among projected, geographic, geocentric, and fitted coordinate systems and builds composed transformations, with explicit unsupported-path failures. See [CoordinateTransformationFactory.cs](https://github.com/NetTopologySuite/ProjNet4GeoAPI/blob/develop/src/ProjNet/CoordinateSystems/Transformations/CoordinateTransformationFactory.cs).

It remains a substantive study of coordinate-system object models and transformation construction; inclusion is not a recommendation to assume ongoing support.

### 10. [DotSpatial/DotSpatial](https://github.com/DotSpatial/DotSpatial)

**C# — specifically the reusable `DotSpatial.Projections` subsystem of the GIS monorepo.** Count the repository once, rather than treating the projection package and GIS application components as separate projects.

- **C1:** Reprojection handles geocentric/geodetic conversion, prime-meridian offsets, datum changes, and independent vertical-unit factors. Missing height arrays for geocentric transformations cause an explicit failure. The affine-image helper documents that its approximation degrades as geographic extent increases.
- **C2:** `ProjectionInfo` supplies the coordinate-system model, while an optional `IDatumTransform` lets callers replace the datum transformation stage without replacing the whole reprojection sequence.
- **C3:** The API transforms caller-provided coordinate arrays over a specified index/count region, supporting bulk GIS workloads without requiring a separate object per point. Study [Reproject.cs](https://github.com/DotSpatial/DotSpatial/blob/master/Source/Core/DotSpatial.Projections/Reproject.cs).

The affine helper and full point transformation are especially useful to compare because they expose a practical accuracy/performance tradeoff in the same module.

### 11. [proj4php/proj4php](https://github.com/proj4php/proj4php)

**PHP — native coordinate transformations derived from Proj4JS.** This is a substantive port with projection definitions, datum models, ellipsoids, and transformation logic, rather than a generated native-library binding.

- **C1:** The main driver orders axis changes, degree/radian and linear-unit conversion, prime-meridian offsets, and geocentric datum steps. Crucially, the inspected implementation **throws for grid-shift transformations because they are not implemented**. Its mutation and return-value semantics are also worth reviewing. See [Proj4php.php](https://github.com/proj4php/proj4php/blob/master/src/Proj4php.php).
- **C2:** `Proj` separates CRS definition parsing and projection-code initialization from coordinate transformation, with a registry of projection implementations and support for custom definitions. See [Proj.php](https://github.com/proj4php/proj4php/blob/master/src/Proj.php).

Study this library for the engineering consequences of moving a projection system into PHP. The unsupported-grid path and shared registry state are concrete limitations, not grounds for assuming every PROJ-style definition will work.

## Typed coordinate systems and Julia implementations

### 12. [JuliaGeo/Geodesy.jl](https://github.com/JuliaGeo/Geodesy.jl)

**Julia — typed world and local coordinates with composable transformations.** **Status:** the repository explicitly says it is in maintenance mode, with new features no longer being developed.

- **C1:** The ECEF-to-geodetic implementation validates ellipsoid parameters and treats spherical, polar/origin, and prolate cases separately. Coordinate types and explicit datum arguments help avoid silently interpreting an unlabelled numerical vector.
- **C2:** Transformations implement the `CoordinateTransformations` interface, allowing inversion and composition among LLA, ECEF, ENU, and projected representations. The repository documents why a datum-free `Base.convert` would require unsafe assumptions.
- **C3:** Transformation objects cache ellipsoid parameters and, for local frames, origin-related work so that many points can reuse the same setup. Study [transformations.jl](https://github.com/JuliaGeo/Geodesy.jl/blob/main/src/transformations.jl).

Its GeographicLib-derived numerical code and Julia-specific composition model make it an independent implementation worth comparing with both the C++ source and newer Julia designs.

### 13. [JuliaEarth/CoordRefSystems.jl](https://github.com/JuliaEarth/CoordRefSystems.jl)

**Julia — unit-aware CRS types and native coordinate/datum conversions.** Study how datum identity and coordinate types become dispatch parameters rather than incidental metadata.

- **C1:** Time-dependent Helmert transformations distinguish the source datum's epoch from the transformation reference epoch and apply separate annual rates to translation, rotation, and scale. The documented parameter units include meters, arc seconds, and parts per million. See [timedephelmert.jl](https://github.com/JuliaEarth/CoordRefSystems.jl/blob/main/src/transforms/timedephelmert.jl).
- **C2:** Macros generate forward and backward conversion methods for datum pairs and route spherical/cylindrical conversions through Cartesian coordinates. The [transformation definitions](https://github.com/JuliaEarth/CoordRefSystems.jl/blob/main/src/transforms.jl) combine identity, geocentric translation, Helmert, time-dependent Helmert, and sequential transformations, with parameter provenance links.

The README places offset-grid datum transformations in the separate CoordGridTransforms.jl package. Thus, the selected repository's typed conversion model should not be equated with an all-inclusive grid transformation engine. Its advertised benchmark rankings were not adopted as findings.

## Numerical kernels, local frames, and reference-frame libraries

### 14. [geographiclib/geographiclib](https://github.com/geographiclib/geographiclib)

**C++ — precision geodesy, including geocentric, local Cartesian, UTM/UPS, and grid-coordinate conversions.** The coordinate-conversion subsystem is the reason for inclusion; geodesic distance alone would not suffice.

- **C1:** `Geocentric::IntReverse` explicitly handles very large inputs to avoid overflow, the spherical limit, prolate ellipsoids, cancellation in algebraic expressions, and degeneracies that would otherwise produce division by zero. Comments explain why alternate formulas are used.
- **C2:** The same ellipsoid-parameterized class supplies forward/reverse conversions and optional rotation matrices linking local east/north/up directions to geocentric coordinates. It therefore supports both position and local-basis work through one reusable numerical model. Read [Geocentric.cpp](https://github.com/geographiclib/geographiclib/blob/main/src/Geocentric.cpp).

This is a particularly strong selection for engineers interested in the difference between translating a published formula and making it reliable throughout its input domain. No numerical error bound was independently measured in this research.

### 15. [geographiclib/geographiclib-octave](https://github.com/geographiclib/geographiclib-octave)

**Octave/MATLAB — native array-oriented GeographicLib implementations.** Retained separately from the C++ repository because it contains substantive `.m` implementations, including coordinate-conversion and triaxial functionality, rather than simply wrapping the C++ library.

- **C1:** The geocentric inverse checks compatible input shapes and handles spherical/prolate cases, poles, cancellation, and roundoff-sensitive intermediate expressions. Different numerical cases are selected with array masks. See [geocent_inv.m](https://github.com/geographiclib/geographiclib-octave/blob/main/inst/geocent_inv.m).
- **C2:** Its reusable functions cover geocentric and local Cartesian conversion, transverse Mercator, polar stereographic, UTM/UPS, and MGRS, with explicit ellipsoid and unit conventions. The [inst source tree](https://github.com/geographiclib/geographiclib-octave/tree/main/inst) is the module map.
- **C3:** Vectorized branches apply the same numerical cases to coordinate arrays, providing a useful comparison with scalar C++ control flow. This supports a structural performance observation, not the README's cross-language speed comparison.

### 16. [Stellacore/peridetic](https://github.com/Stellacore/peridetic)

**C++ — small header-only geodetic/ECEF conversion kernel.** A deliberately narrower alternative to a full CRS registry or projection engine, with an explicit interest in constrained devices.

- **C1:** The implementation normalizes the ellipsoid and input coordinates, solves for the nearby ellipsoid point using a bounded iterative update, derives the vertical direction from the surface gradient, and obtains signed altitude by projection onto that direction. Study [periDetail.h](https://github.com/Stellacore/peridetic/blob/main/include/periDetail.h), especially `EarthModel` and `sigmaNormFor`.
- **C3:** The fixed-size, inline implementation is paired with a benchmark harness that prepares coordinate sets and workspaces and measures per-operation costs. See [evalSpeed.cpp](https://github.com/Stellacore/peridetic/blob/main/eval/evalSpeed.cpp).

The README describes a preferred operational altitude range; the iteration limit is not proof of convergence for arbitrary inputs. This is a useful codebase for studying normalization and the balance between a specialized numerical kernel and a minimal integration footprint.

### 17. [chrisveness/geodesy](https://github.com/chrisveness/geodesy)

**JavaScript — ellipsoidal/spherical geodesy, grid conversions, historical datums, and modern reference frames.** Although it originated in explanatory examples, the repository contains a substantial reusable class and module family.

- **C1:** The reference-frame implementation carries epochs, converts millimeters/milliarcseconds/parts per billion into computational units, and applies time-dependent Helmert parameters. It supports direct, reversed, or intermediate-frame routes and preserves the observation epoch.
- **C2:** Reference-frame-aware latitude/longitude and Cartesian classes extend the underlying ellipsoidal coordinate classes; separate modules provide datum, UTM, MGRS, and national-grid functionality. Read [latlon-ellipsoidal-referenceframe.js](https://github.com/chrisveness/geodesy/blob/master/latlon-ellipsoidal-referenceframe.js).

This source is also explicit about its limits: it treats certain WGS84/ITRF changes as no-ops and uses a small intermediate-route search. The author characterizes the reference-frame support as suitable for less demanding requirements. These assumptions make it instructive, but not interchangeable with a full operation-selection engine.

### 18. [mrJean1/PyGeodesy](https://github.com/mrJean1/PyGeodesy)

**Python — multiple geodetic numerical methods and coordinate representations.** A substantial independent Python implementation drawing on both GeographicLib and Chris Veness, with additional algorithms and a broader Python class system.

- **C1:** Its ECEF module exposes different inverse solvers rather than pretending every method has identical numerical behavior. The documentation identifies algorithm provenance, discusses finite-input handling for the Karney method, and defines configurable longitude behavior at polar ECEF positions.
- **C2:** A common ECEF base supplies ellipsoid/datum handling and forward-conversion behavior, while concrete classes implement Karney, Fukushima, Sudano, Veness, You, and other approaches. The same package also supplies local-frame and projected-coordinate APIs. Read [ecef.py](https://github.com/mrJean1/PyGeodesy/blob/master/pygeodesy/ecef.py).

Its study value is comparative: engineers can inspect how several numerical approaches fit behind related interfaces. Accuracy claims attached to one algorithm should not be generalized to every solver or the entire package.

### 19. [geospace-code/pymap3d](https://github.com/geospace-code/pymap3d)

**Python — geodetic, ECEF, local-frame, and geospace coordinate conversions, with optional NumPy.** Especially useful for comparing a small scalar API with array-based scientific use.

- **C1:** The ECEF inverse distinguishes points inside the ellipsoid to assign altitude sign, handles polar/degenerate cases, and patches latitude and altitude calculations against float32 precision loss. It has separate NumPy and scalar paths. See [ecef.py](https://github.com/geospace-code/pymap3d/blob/main/src/pymap3d/ecef.py).
- **C2:** The module composes reusable geodetic, ECEF, ENU, and inertial-frame conversions with configurable ellipsoids and degree/radian conventions. The repository's API accepts scalars and, where mathematically consistent, arrays of arbitrary shape.
- **C3:** Array operations and the optional-dependency scalar path serve different deployment constraints without requiring a different public coordinate vocabulary.

The library converts coordinate representations and local/inertial frames; it should not be treated as a replacement for global CRS operation discovery and national datum-grid selection.

### 20. [pbrod/nvector](https://github.com/pbrod/nvector)

**Python/NumPy — ellipsoid-normal vectors, ECEF positions, and Earth/local/body reference frames.** This offers a different representation family from latitude/longitude-centric libraries.

- **C1:** Position-vector arithmetic and frame changes check that the participating Earth frames agree. `_check_frames` raises on mismatches. This is a concrete invariant guarding otherwise plausible but physically meaningless vector operations.
- **C2:** `GeoPoint`, `Nvector`, `ECEFvector`, `Pvector`, and the Earth, north/east/down, wander-azimuth, and body-frame classes share conversion operations. Local-frame changes use explicit rotation matrices, while vectorized positions retain frame metadata. Study [objects.py](https://github.com/pbrod/nvector/blob/master/src/nvector/objects.py).

The n-vector representation avoids latitude/longitude representation singularities for global positions, but that does not make local north/east directions uniquely defined at the poles. The repository's own examples distinguish that local-frame limitation. Its strongest fit is navigation and sensor geometry rather than an EPSG transformation database.

## National-agency transformations and surveying libraries

### 21. [GeoscienceAustralia/GeodePy](https://github.com/GeoscienceAustralia/GeodePy)

**Python — geodesy and surveying toolkit with Australian datum/reference-frame transformations.** The reusable transformation module is the focus, not the repository's standalone utilities.

- **C1:** `conform7` performs a Helmert transformation with explicit scale/rotation unit conversion and optional covariance propagation, including transformation-parameter uncertainty. `conform14` adds epoch-dependent parameters. This makes both coordinates and their uncertainty part of the numerical design.
- **C2:** Transformation objects, general conformal operations, plate-motion operations, MGA94/MGA2020 helpers, ATRF/GDA conversion, and an NTv2 interface share the same module and coordinate-conversion building blocks. Read [transform.py](https://github.com/GeoscienceAustralia/GeodePy/blob/master/geodepy/transform.py).

This is particularly useful for studying how a general transformation primitive becomes a practical surveying API. The seven-parameter function explicitly ignores time-dependent fields; choosing it versus the fourteen-parameter function is a meaningful semantic decision, not just an API naming preference.

### 22. [IGNF/circe](https://github.com/IGNF/circe)

**C++ — IGN France's Circé, specifically the reusable `circelib` subsystem.** The same repository includes GUI/CLI interfaces and territorial assets; count it once. Its documented “4D+1” scope includes spatial coordinates, epochs/velocity models, and vertical reference systems.

- **C1:** Compound-operation construction distinguishes missing geodetic/vertical transformations from other failures, checks whether a hub frame can connect the requested systems, and reconciles epochs. It clears inappropriate epochs on non-4D frames and can insert an epoch-change operation.
- **C2:** CRS, reference-frame, conversion, concatenated-operation, and compound-operation objects separate metadata from execution. The constructor chooses a direct operation or a sequence through a configured hub. Study [compoundoperation.cpp](https://github.com/IGNF/circe/blob/main/circelib/compoundoperation.cpp) and the [circelib module map](https://github.com/IGNF/circe/tree/main/circelib).

The README explicitly warns that bundled territorial assets may not be the latest public-service data. The source is valuable for operation selection and regional geodetic modeling; data currency must be assessed separately.

### 23. [noaa-ngs/ncat-lib](https://github.com/noaa-ngs/ncat-lib)

**Java — NOAA NGS's reusable transformation modules published for NCAT.** This provides national-grid and regional-datum architecture beyond the general PROJ ecosystem.

- **C1:** The grid transformer selects a region, traverses ordered regional datums, checks transformed points against bounds, distinguishes missing grids, and accumulates squared error contributions. Separate grid work is submitted to an executor and collected in a concurrent map. See [Transformer.java](https://github.com/noaa-ngs/ncat-lib/blob/main/src/gov/noaa/ngs/grid/Transformer.java).
- **C2:** `GridManager` abstracts grid-block access, interpolation, regional bounds, and transformation/error-grid parameters, with implementations selected for NADCON and VERTCON. See [GridManager.java](https://github.com/noaa-ngs/ncat-lib/blob/main/src/gov/noaa/ngs/grid/GridManager.java).

The per-transformation thread pool and polling for completion are instructive design tradeoffs, not evidence of an independently verified performance advantage. This report verifies the published library; it does not establish that its source and grid configuration exactly match today's hosted NCAT service.

## Search coverage, exclusions, and limitations

Discovery used live web search followed by opening repository pages and reading official documentation or implementation files. Distinct search formulations covered general C/C++ projection/datum engines; Java CRS frameworks; native Rust and WebAssembly; C# projection and grid shifts; JavaScript/PHP ports; Python ECEF, n-vector, and surveying libraries; Julia typed/unit-aware coordinates; national-agency 4D and vertical transformations; and Go/Fortran alternatives. Follow-up searches for independent kernels and less prominent transformation suites found Circé, NCAT, peridetic, and CTS. Later broad Go/Fortran and transformation-library searches increasingly returned already-covered engines, binding layers, geodesic-only code, or unrelated coordinate systems, so further expansion had diminishing value.

The list intentionally extends beyond the usual narrow-category range because it contains distinct numerical, representation, and architecture families. Native ports are retained when they contain substantive implementations and language-specific designs. GeographicLib's C++ and Octave repositories are distinguished explicitly; related ports are not presented as unrelated algorithmic inventions. pyproj is included for its substantial handwritten API, operation discovery, threading, and lifecycle layer. Generated bindings and repeated thin wrappers were not added merely to represent more languages.

Excluded areas include data-only repositories such as PROJ-data; geodesic-distance-only libraries, including language subsets of GeographicLib that do not provide the relevant conversions; map viewers and full GIS applications; tutorial snippets; duplicate forks; and generic Cartesian/robotics transforms without a substantive Earth-referenced coordinate model. Go/Fortran searches did not yield an additional retained candidate whose inspected scope improved this selection enough to justify expanding it further; that is a search limitation, not a claim that those ecosystems lack suitable work.

Every retained repository had its canonical GitHub page or API metadata checked and at least one distinct primary implementation or architecture source read. Unauthenticated GitHub API rate limits were encountered; public repository pages and raw source files supplied the remaining verification. Source links generally track development branches and may change. This was read-only source research: no candidate code was executed, no dependencies were installed, no benchmark was reproduced, and no numerical certification or national-grid currency audit was performed. Statements about what an engineer can study are grounded judgments from the cited code, not guarantees that all surrounding components share the same quality.
