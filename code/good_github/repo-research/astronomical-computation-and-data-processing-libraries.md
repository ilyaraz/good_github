# Astronomical computation and data processing libraries

Research date: **2026-10-09**

This selection covers 25 GitHub repositories providing reusable astronomical calculations, scientific data models, storage, measurement, simulation, and large-data processing. It spans Python, C, C++, Fortran, Java, Rust, and Julia, from small numerical foundations to frameworks for survey catalogs and simulation outputs. Each repository's GitHub page and additional primary implementation or documentation material were opened and inspected. The engineering assessments below are grounded judgments about particular subsystems, not claims that every component is uniformly exemplary.

**Criteria legend:** **C1** — difficult correctness, including numerical semantics, invariants, concurrency, and failure handling. **C2** — substantial reusable abstractions serving multiple workflows. **C3** — explicit performance constraints addressed through understandable architecture. **C4** — documented evolution across years together with compatibility, testing, or complexity management. Every entry has at least two supported criteria; age, popularity, and recent commits alone are not qualifying evidence.

## Fundamental quantities, astrometry, and coordinate transformations

### 1. [astropy/astropy](https://github.com/astropy/astropy)

**Language/role:** Python with native components; the core astronomy framework. Study the separation between physical quantities and their external representations, especially in `astropy.time`.

- **C1:** Time arithmetic uses a pair of 64-bit floating-point values, with compensated floating-point algorithms, rather than treating a displayed Julian date as the full internal state. Changing a time's *format* preserves the instant; changing its *scale* can change the represented numeric values. This is a concrete example of numerical precision and domain semantics shaping an API. See the [time implementation and usage guide](https://docs.astropy.org/en/stable/time/index.html).
- **C2:** The same `Time` abstraction handles scalar and array inputs, multiple astronomical time scales, and interchangeable formats. Its format-class extension mechanism supports specialized representations without rewriting arithmetic. The same [guide](https://docs.astropy.org/en/stable/time/index.html) is the recommended entry point into this subsystem of the larger repository.

### 2. [liberfa/erfa](https://github.com/liberfa/erfa)

**Language/role:** C; Essential Routines for Fundamental Astronomy. This is a SOFA-derived library with its own licensing, integration features, and documented upstream tracking, not a second independent invention of the SOFA algorithms.

- **C1:** [`src/dat.c`](https://github.com/liberfa/erfa/blob/master/src/dat.c) distinguishes invalid calendar inputs from a merely dubious year, explains the impossibility of predicting future leap seconds, and defines behavior on either side of a leap-second boundary. Its extensive contracts are useful models for small numerical APIs whose edge cases carry scientific meaning.
- **C4:** The [repository's SOFA comparison history](https://github.com/liberfa/erfa#differences-from-sofa) documents releases corresponding to upstream versions from 2015 through 2023, numerical fixes, the explicit-header compatibility change, version-query functions, and runtime leap-second-table extensions. This supports sustained compatibility management rather than an inference from repository age.

### 3. [skyfielders/python-skyfield](https://github.com/skyfielders/python-skyfield)

**Language/role:** Python; celestial positions and observational astronomy. Study how types expose stages of a scientific calculation instead of collapsing every position into an unqualified vector.

- **C1:** The [positions guide](https://rhodesmill.org/skyfield/positions.html) separates barycentric, astrometric, and apparent positions. `observe()` accounts for light travel time; `apparent()` adds aberration and gravitational deflection. The guide also distinguishes catalog coordinates from coordinates appropriate for pointing a telescope.
- **C2:** Position objects share Cartesian representations, units, observation times, and explicit center/target identities across planets, stars, satellites, and other bodies. Array-valued dates propagate through position and velocity calculations. The [position model](https://rhodesmill.org/skyfield/positions.html) provides a readable entry point into this reusable object system.

### 4. [spacetelescope/gwcs](https://github.com/spacetelescope/gwcs)

**Language/role:** Python; generalized world coordinate systems. Study composable detector-to-world transformations and their intermediate coordinate frames.

- **C1:** Bounding-box ordering is a real semantic trap: a tuple applied to an underlying model can mean something different from the same tuple applied to a GWCS object. The [WCS guide](https://gwcs.readthedocs.io/en/latest/gwcs/using_wcs.html) documents ordering conversion and warnings. It also distinguishes analytical and numerical inverses, explaining that numerical inversion's default quiet mode can suppress divergence warnings; callers can request `NoConvergence` exceptions.
- **C2:** A WCS is a pipeline whose frame-to-frame transforms can be retrieved, replaced, or extended. This makes instrument distortion and coordinate conversion stages independently reusable. The [pipeline manipulation examples](https://gwcs.readthedocs.io/en/latest/gwcs/using_wcs.html) are a useful bridge from model composition to implementation.

## Astronomical storage and interferometry data models

### 5. [heasarc/cfitsio](https://github.com/HEASARC/cfitsio)

**Language/role:** C with Fortran interfaces; FITS image and table I/O. Study how a scientific binary-format library exposes its buffering and concurrency rules.

- **C1:** The [multithreading contract](https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node15.html) requires a reentrant build, independent opens for concurrent readers of the same file, and locking when sharing a file pointer. It explicitly disallows different threads writing the same FITS file. These are precise ownership rules, not a blanket thread-safety claim.
- **C3:** The [I/O optimization guide](https://heasarc.gsfc.nasa.gov/docs/software/fitsio/user_f/node35.html) explains large contiguous transfers bypassing intermediate buffers, row-block processing across table columns, and the costs of conversion and scaling. It also identifies fast raw-byte operations that bypass normal validation, making the correctness/performance boundary visible.

### 6. [nom-tam-fits/nom-tam-fits](https://github.com/nom-tam-fits/nom-tam-fits)

**Language/role:** Java; an independent FITS implementation. Study binary-table descriptors, variable-length array heaps, and deferred I/O in a managed runtime.

- **C1:** [`BinaryTable`](https://nom-tam-fits.github.io/nom-tam-fits/apidocs/nom/tam/fits/BinaryTable.html) distinguishes row-major and column-major construction, ordinary values from heap pointers, and copying a full binary table from copying a generic column table. These distinctions prevent plausible-looking but semantically wrong reconstructions.
- **C3:** The same [API documentation](https://nom-tam-fits.github.io/nom-tam-fits/apidocs/nom/tam/fits/BinaryTable.html) describes deferred entry access, operations that force materialization, and heap defragmentation. The architecture exposes when file-backed access becomes an in-memory operation.
- **C4:** The [changelog](https://nom-tam-fits.github.io/nom-tam-fits/CHANGELOG.html) records multi-year table and compression evolution, compatibility restoration, synchronization fixes, explicit deprecations, and migration of the test suite to JUnit 5. It is particularly useful for studying standards compliance without silently breaking existing readers.

### 7. [casacore/casacore](https://github.com/casacore/casacore)

**Language/role:** C++; radio astronomy libraries. The relevant subsystems are the Table Data System, MeasurementSet storage, and image/lattice infrastructure; this suite counts as one repository.

- **C1:** The [table-locking design note](https://casacore.github.io/casacore-notes/256.html) describes one-writer/multiple-reader exclusion, flushing on unlock, refreshing on lock, and metadata used to refresh only changed storage managers. No-read-lock modes require explicit synchronization; the note also acknowledges schema-change limitations.
- **C2:** Tables support scalar and array columns, subtables, keywords, and array-aware queries. MeasurementSets and images reuse these mechanisms rather than defining unrelated storage stacks. See the [Table Data System design note](https://casacore.github.io/casacore-notes/255.html).
- **C3:** Incremental and tiled storage managers separate physical layout from the logical table. The same design note explains how tile shape affects access along different axes and candidly discusses overheads.

### 8. [RadioAstronomySoftwareGroup/pyuvdata](https://github.com/RadioAstronomySoftwareGroup/pyuvdata)

**Language/role:** Python; interoperable radio interferometry data models. Study a common in-memory representation that must retain enough information to survive conversions among visibility formats.

- **C1:** The [UVData API](https://pyuvdata.readthedocs.io/en/latest/uvdata.html) defines dependent array shapes, a coherent metadata-only state, and consistency checks. Writer contracts include restrictions on frequencies, polarization layouts, phasing, and time systems; autocorrelation checks can detect imaginary values that should not mathematically exist.
- **C2:** `UVData` separates visibility data, flags, sample weights, telescope information, and phase-center metadata while exposing readers and writers for multiple formats. The same [API guide](https://pyuvdata.readthedocs.io/en/latest/uvdata.html) shows how selection, metadata inspection, and serialization reuse the representation. This is more substantial than a file-format wrapper.

## Image measurement, resampling, and simulation

### 9. [astropy/photutils](https://github.com/astropy/photutils)

**Language/role:** Python with numerical extensions; source detection and photometry. Study aperture geometry and measurement contracts as one entry into a broader image-analysis package.

- **C1:** The [aperture-photometry implementation](https://photutils.readthedocs.io/en/stable/_modules/photutils/aperture/photometry.html) handles masks, compatible data/error units, and weighted pixel overlaps. It explicitly states that summing an aperture does not convert surface brightness to flux, and documents approximation limits for aperture shapes.
- **C2:** Aperture objects and sky apertures feed a shared measurement routine that accepts arrays, quantities, and `NDData`; the latter carries its own uncertainty, mask, and WCS. The [source](https://photutils.readthedocs.io/en/stable/_modules/photutils/aperture/photometry.html) shows how these input models are normalized while retaining metadata, a useful pattern for scientific library interoperability.

### 10. [sep-developers/sep](https://github.com/sep-developers/sep)

**Language/role:** C and Python/Cython; source extraction and photometry on in-memory images. This is the documented successor home of SEP; earlier `kbarbary/sep` and `sep-pjw` repositories are not counted separately.

- **C1:** The [documented C interface](https://github.com/sep-developers/sep/blob/main/src/sep.h) exposes masked/truncated aperture flags, noise representations, and relative versus absolute thresholds. The [repository's design explanation](https://github.com/sep-developers/sep#faq) describes replacing executable-style termination with cleanup and error returns.
- **C2:** Source Extractor algorithms were reorganized into independent functions operating on caller-provided arrays. `sep_image`, background objects, and catalog structures make data, noise, masks, and results explicit; options are passed to functions rather than inherited from one global executable configuration. This is a particularly useful study of turning a scientific application into an embeddable library.

### 11. [astropy/reproject](https://github.com/astropy/reproject)

**Language/role:** Python with compiled numerical components; astronomical image reprojection. Study algorithm choice as an explicit scientific and computational contract.

- **C1:** The [algorithm explanation](https://reproject.readthedocs.io/en/latest/explanation/algorithms.html) separates interpolation, adaptive antialiased resampling, and spherical-polygon overlap. It carefully distinguishes preserving surface-brightness units from preserving integrated flux and from photometric accuracy; these are not interchangeable guarantees.
- **C3:** The [performance guide](https://reproject.readthedocs.io/en/stable/performance.html) explains output chunking, parallel execution, temporary memory-mapped inputs, and reusing coordinate transformations for multiple images. It also explains why chunking output does not generally partition the input: an output region may depend on pixels anywhere in the source image.

### 12. [GalSim-developers/GalSim](https://github.com/GalSim-developers/GalSim)

**Language/role:** C++ numerical engine with Python interfaces; realistic astronomical image simulation. Study composition of galaxy and point-spread-function profiles and rendering with controlled approximations.

- **C2:** The [`GSObject` interface](https://galsim-developers.github.io/GalSim/_build/html/gsobject.html) supports profile transformations, sums, convolutions, and drawing through common abstractions. Profiles and combinations remain manipulable objects before rendering, supporting many observing and simulation configurations.
- **C1:** The same guide distinguishes flux-preserving dilation from surface-brightness-preserving transformations, and documents photon-shooting normalization and FFT wraparound artifacts.
- **C3:** `GSParams` centralizes accuracy/speed controls such as Fourier sampling, folding thresholds, and FFT size. The [rendering documentation](https://galsim-developers.github.io/GalSim/_build/html/gsobject.html) explains memory consequences and which parameters can be changed on a compound object versus its components.

## Spectra, time series, and observational analysis frameworks

### 13. [astropy/specutils](https://github.com/astropy/specutils)

**Language/role:** Python; shared spectral representations and analysis operations. Study consistent interfaces for manipulating spectra while exposing the statistical limits of each operation.

- **C1:** The [manipulation guide](https://specutils.readthedocs.io/en/stable/manipulation.html) distinguishes integrated-flux-conserving resampling from linear and spline interpolation. It documents extrapolation policies and the important limitation that the latter two resamplers ignore input uncertainty; smoothing's ordinary error propagation does not account for covariance between samples.
- **C2:** Resamplers accept a `Spectrum` and a target dispersion grid and return another `Spectrum`. Shared units and uncertainty representations let smoothing, resampling, splicing, and uncertainty estimation form larger workflows. The [same guide](https://specutils.readthedocs.io/en/stable/manipulation.html) is a concrete entry point into these composable operations.

### 14. [radio-astro-tools/spectral-cube](https://github.com/radio-astro-tools/spectral-cube)

**Language/role:** Python; astrophysical spectral-data cubes. Study extension APIs that preserve masks while supporting datasets larger than memory.

- **C3:** The [developer guide](https://spectral-cube.readthedocs.io/en/stable/developing_with_spectralcube.html) explains memory mapping, minimizing copies, subset-based reductions, lazy masks, and Dask-backed execution. It describes scheduling, rechunking, and persistence as architectural choices rather than promising universal parallel speedups.
- **C2:** Both ordinary and Dask-backed cube classes expose spatial and spectral function-application methods. Custom algorithms receive data and masks, allowing per-spectrum fitting or per-plane processing through a common abstraction. The [extension discussion](https://spectral-cube.readthedocs.io/en/stable/developing_with_spectralcube.html) warns that accessing the underlying Dask array directly bypasses mask-aware checks.

### 15. [StingraySoftware/stingray](https://github.com/StingraySoftware/stingray)

**Language/role:** Python; astronomical spectral timing. Study how event lists, light curves, and averaged Fourier products share calculation machinery.

- **C1:** The [`powerspectrum` implementation](https://docs.stingray.science/en/stable/_modules/stingray/powerspectrum.html) makes good-time intervals, normalization, measurement-error assumptions, and segment means explicit. Using a mean per segment instead of a common mean changes the result, so this is represented as a scientific option rather than an invisible optimization.
- **C2:** Constructors support event lists, light curves, general time series, and iterable collections of light curves, dispatching to common calculation functions and rebuilding consistent result objects. The [source module](https://docs.stingray.science/en/stable/_modules/stingray/powerspectrum.html) is readable evidence of a reusable analysis layer rather than a collection of instrument-specific scripts.

### 16. [gammapy/gammapy](https://github.com/gammapy/gammapy)

**Language/role:** Python; gamma-ray data analysis. Study the boundary between observed counts, instrument response, and source models.

- **C1:** The [dataset guide](https://docs.gammapy.org/dev/tutorials/details/datasets.html) requires counts and background maps to share reconstructed-energy geometry while permitting response maps to use different spatial grids and true-energy axes. Keeping these spaces distinct is essential to meaningful model prediction.
- **C2:** `MapDataset` packages counts, exposure, background, masks, and response functions. Source and background models attach to this representation; methods compute total or component predicted counts and extract region-based datasets. The [guide](https://docs.gammapy.org/dev/tutorials/details/datasets.html) offers an end-to-end entry point for studying this separation of data, geometry, and model responsibilities.

### 17. [sunpy/sunpy](https://github.com/sunpy/sunpy)

**Language/role:** Python; solar data analysis. Focus on the coordinate and map subsystems, which are counted together within the core repository.

- **C1:** Helioprojective and heliocentric coordinates depend on observer location, and calculating a solar-system observer's position also requires observation time. The [coordinate guide](https://docs.sunpy.org/en/latest/tutorial/coordinates.html) explains these dependencies and shows transformations between observers rather than treating solar-image angles as globally comparable coordinates.
- **C2:** Solar frames integrate with `SkyCoord`; maps construct their coordinate frames from observation headers and expose them for coordinate-aware analysis. The [coordinates-and-maps discussion](https://docs.sunpy.org/en/latest/tutorial/coordinates.html) shows how geometry can be reused across different images and observers instead of being embedded separately in each instrument workflow.

### 18. [yt-project/yt](https://github.com/yt-project/yt)

**Language/role:** Python with compiled numerical components; analysis of astrophysical simulation data. Focus on simulation frontends, field definitions, indexing, and I/O rather than visualization alone.

- **C2:** The [frontend architecture guide](https://yt-project.org/doc/developing/creating_frontend.html) separates data meaning, data localization, and data reading. `Dataset`, field containers, index classes, and I/O handlers allow multiple simulation formats to feed the same analysis layer, including through externally packaged frontends.
- **C3:** Patch-based and octree indexes describe where physically selected regions reside on disk, while I/O handlers read selected chunks. The [guide](https://yt-project.org/doc/developing/creating_frontend.html) explains how different simulation layouts map onto these structures. This gives engineers a concrete example of separating a physical query from the storage work needed to answer it.

## Spherical indexing and survey-scale catalogs

### 19. [cds-astro/cds-healpix-rust](https://github.com/cds-astro/cds-healpix-rust)

**Language/role:** Rust; the Strasbourg astronomical Data Centre's HEALPix implementation. Study hierarchical sky coverage with explicit approximation semantics; language bindings are not counted as separate projects.

- **C1:** The [`Layer` documentation](https://docs.rs/cdshealpix/latest/cdshealpix/nested/struct.Layer.html) states that approximate cone coverage can include false-positive cells, while cells marked fully covered really are fully covered. Deeper calculations refine the approximation, subject to a maximum-depth contract. Polygon coverage also documents an approximation to HEALPix cell-edge geometry.
- **C2:** Per-depth `Layer` objects collect constants and operations; hierarchical coverage objects retain partial/full coverage information and can expose flat iterators. The [nested-module documentation](https://docs.rs/cdshealpix/latest/cdshealpix/nested/) connects these abstractions to neighbors, boundaries, coordinate hashing, and several region-query shapes.

### 20. [JuliaAstro/Healpix.jl](https://github.com/JuliaAstro/Healpix.jl)

**Language/role:** Julia; HEALPix algorithms and sky-map operations, with a native Julia pixelization implementation. Study how a compact configuration type captures mathematical invariants and reusable precomputation.

- **C1:** The [resolution guide](https://juliaastro.org/Healpix/stable/resolutions/) makes `NSIDE`, pixel count, and hierarchy order relationships explicit. Validation rejects invalid sizes; supported limits depend on the machine integer representation. These checks matter because invalid hierarchy sizes or overflow would corrupt sky indexing.
- **C3:** `Resolution` precomputes coefficients used across repeated pixel calculations, avoiding repeated setup while keeping the state in a small understandable type. The [same guide](https://juliaastro.org/Healpix/stable/resolutions/) names the stored fields and shows how resolution is passed into operations. This offers a useful comparison with the Rust library's per-depth `Layer` abstraction.

### 21. [astronomy-commons/lsdb](https://github.com/astronomy-commons/lsdb)

**Language/role:** Python/Dask; distributed analysis and crossmatching of astronomical catalogs partitioned with HATS. Study correctness at partition boundaries and extension of partition-local algorithms.

- **C1:** The [margin-cache explanation](https://docs.lsdb.io/en/latest/tutorials/margins.html) shows why partition-local matching misses boundary neighbors. Keeping catalog and margin task graphs separate, and using the right catalog's margin during matching, avoids duplicating left-side results. The [crossmatch API](https://docs.lsdb.io/en/stable/reference/api/lsdb.catalog.Catalog.crossmatch.html) offers an explicit missing-margin check; completeness is not unconditional.
- **C3:** Spatial partitions and bounded margin caches avoid loading entire neighboring partitions. Margin graphs remain unevaluated when unnecessary, reducing both I/O and memory demand. This design addresses larger-than-memory processing without hiding boundary behavior.
- **C2:** Custom crossmatch algorithms plug into a documented interface over aligned partition pairs and return matched indices plus typed extra columns, reusing the surrounding catalog infrastructure.

## Orbital dynamics and cosmological calculations

### 22. [hannorein/rebound](https://github.com/hannorein/rebound)

**Language/role:** C with Python interfaces; gravitational N-body integration. Study the interaction between an integrator's internal state and the public particle representation.

- **C1:** The [WHFast documentation](https://rebound.hanno-rein.de/integrators/whfast/) explains that disabling safe mode changes synchronization obligations: users must synchronize before output or particle modification. Correct integration is therefore partly an API-state invariant, not merely choosing a small timestep.
- **C3:** WHFast exposes a deliberate speed/accuracy tradeoff through synchronization policy and correctors, within a clear integrator-specific configuration. The [integrator documentation](https://rebound.hanno-rein.de/integrators/) places it alongside alternative numerical methods. Engineers can study how one simulation framework supports specialized methods without pretending they have identical operational contracts.

### 23. [jobovy/galpy](https://github.com/jobovy/galpy)

**Language/role:** Python and C; galactic dynamics and orbit calculations. Study composition of gravitational fields and selection of compatible numerical integrators.

- **C1:** The [orbit tutorial](https://docs.galpy.org/en/v1.12.0/tutorials/orbits/integration_and_plotting.html) demonstrates rejecting symplectic integration for dissipative forces and falling back to an appropriate non-symplectic method. This is a concrete safeguard against using an algorithm outside its mathematical assumptions.
- **C2:** The [`Orbit.integrate` contract](https://docs.galpy.org/en/latest/reference/orbitint.html) accepts potentials, dissipative forces, and additive combinations through one interface, together with tolerances and unit-aware times.
- **C3:** The same API separates Python and C integrators and describes multiprocessing controls and fixed-step divisibility constraints. The architecture supports accelerated numerical kernels without eliminating the higher-level field abstractions.

### 24. [cmbant/CAMB](https://github.com/cmbant/CAMB)

**Language/role:** Fortran and Python; cosmological perturbation and observable calculations. Study extensible physics models across a language boundary, rather than treating the Python interface as the whole implementation.

- **C1:** The [code-modification guide](https://camb.readthedocs.io/en/stable/modifying_code.html) requires matching field order across Python and Fortran types and explains pointer/type mapping, version agreement checks, and pitfalls of directly constructing wrapper subcomponents. It also calls for testing stability as numerical accuracy settings increase.
- **C2:** Dark energy, initial power, reionization, recombination, and nonlinear corrections have extension points based on inherited model classes; some changes can instead be supplied as interpolation tables. The [guide](https://camb.readthedocs.io/en/stable/modifying_code.html) gives a worked paired Python/Fortran class example.
- **C3:** The guide explains why adjusting specific numerical tolerances can be more efficient than globally increasing every accuracy setting.

### 25. [LSSTDESC/CCL](https://github.com/LSSTDESC/CCL)

**Language/role:** C and Python; the DESC Core Cosmology Library. Study orchestration of cosmological parameters, derived quantities, and alternative prediction backends.

- **C1:** [`pyccl/cosmology.py`](https://github.com/LSSTDESC/CCL/blob/master/pyccl/cosmology.py) documents mutually exclusive amplitude normalizations and their physical interpretation. Its configuration builder rejects using CAMB nonlinear power with an incompatible transfer-function backend, making a cross-component numerical constraint explicit.
- **C2:** `Cosmology` centralizes parameters and derived data, while enumerated transfer-function and matter-power choices organize interchangeable calculators. The [implementation](https://github.com/LSSTDESC/CCL/blob/master/pyccl/cosmology.py) also shows attaching cosmology-taking functions as methods and managing C-backed state during serialization. This is a useful study in building a coherent scientific interface over several computational models.

## Search coverage, exclusions, and limitations

Discovery used substantially more than six distinct formulations, including: core astronomy coordinates/time/units; C/C++ FITS and radio storage; image photometry and reprojection; interferometric visibility data; spectral cubes and timing; celestial mechanics and N-body integration; cosmological prediction libraries; Rust spherical indexing; native Julia astronomy; Java FITS; distributed catalogs and pulsar timing; and broader Go/Rust/R astronomical processing searches. Follow-up searches targeted primary design notes, source modules, numerical contracts, performance explanations, and changelogs. Later broad searches increasingly returned alternative implementations in already-covered families, application suites, or wrappers rather than new architectural families for this selection.

The list deliberately includes both shared infrastructure and smaller specialist implementations. Astropy, casacore, SunPy, and yt each count once despite containing multiple subsystems. SEP's former homes are not additional entries. ERFA's SOFA derivation is disclosed; SOFA itself and generated bindings are not counted to inflate coverage. Rust and Julia HEALPix entries represent distinct implementations and contrasting interfaces, rather than two wrappers around one C core.

Desktop viewers, telescope-control applications, small demonstrations, awesome-lists, and thin service/FFI wrappers were outside the chosen scope. Pulsar-specific timing, gravitational-wave pipelines, exoplanet inference, and full observatory reduction systems are not comprehensively represented. Unselected candidates are not thereby judged poor quality. The scope is a diverse engineering selection, not an exhaustive inventory of astronomy software.

All retained repository roots and the cited substantive entry points were verified through live web access. Some documentation is versioned, while `stable`, `latest`, `dev`, and default-branch links can evolve; those labels do not establish a current release or maintenance promise. C4 is used only where inspected history supports it. No performance benchmarks were run, no dependencies were installed, and no candidate code was executed. Quantitative speed rankings and blanket claims of scientific correctness or active maintenance are intentionally absent.
