# Color management and color science libraries

Research date: **2026-10-09**.

This report selects **24 GitHub repositories** implementing reusable color-management engines, spectral and perceptual color science, color-space abstractions, and gamut/interpolation algorithms. It includes production frameworks, compact libraries, and reference implementations. It excludes general image editors, palette collections, and thin bindings whose substantive implementation lives elsewhere. Repository pages and additional primary implementation or architectural material were read for every selection. These are engineering study recommendations, not certifications of numerical accuracy or uniform code quality.

Criteria used throughout:

- **C1 — Difficult correctness:** numerical semantics, invariants, malformed inputs, concurrency, or meaningful failure modes.
- **C2 — Reusable abstractions:** substantial interfaces or models supporting multiple applications and workflows.
- **C3 — Performance with structure:** explicit computational, memory, or throughput constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** evidence of years of development together with compatibility work, testing, or complexity management.

Criteria judgments are grounded interpretations of the linked material. Maintenance is not inferred from stars, repository age, or the mere presence of CI; historical and mirror qualifications are stated where relevant.

## ICC engines and production color pipelines

### 1. [mm2/Little-CMS](https://github.com/mm2/Little-CMS)

**Language / role:** C; ICC color-management engine supporting profile transforms, including device-link, abstract, and named-color profiles.

Study how a conventional C library represents a transform as composable processing stages while preserving channel counts and managing partial allocation failures. The implementation is particularly useful for understanding the boundary between profile semantics and numerical execution.

- **C1:** `cmslut.c` checks adjacent stages' input/output channel compatibility, guards multidimensional table-size calculations, and uses double-precision accumulation for matrix stages. Its reverse evaluator explicitly handles convergence and matrix-solver failure. [Pipeline implementation](https://github.com/mm2/Little-CMS/blob/master/src/cmslut.c).
- **C2:** Curves, matrices, lookup tables, and conversion stages share evaluation, duplication, and destruction interfaces; pipelines can be copied and concatenated through a common API. [Same implementation](https://github.com/mm2/Little-CMS/blob/master/src/cmslut.c).
- **C4:** The repository documents an initial 1998 release, while its detailed release history records context-race fixes, restored raw-tag behavior needed by consumers, broader platform testing, and fuzzing infrastructure. This is compatibility and failure-management evidence beyond longevity alone. [ChangeLog](https://github.com/mm2/Little-CMS/blob/master/ChangeLog).

### 2. [AcademySoftwareFoundation/OpenColorIO](https://github.com/AcademySoftwareFoundation/OpenColorIO)

**Language / role:** C++ with Python bindings; configurable color management for visual effects and animation.

Study the separation between a pipeline configuration, an abstract processor, and optimized CPU/GPU execution. This is a substantial example of keeping production color policy outside application code while sharing transform definitions across renderers.

- **C2:** `Config` produces `Processor` objects; CPU and GPU processors expose execution-specific interfaces, while transform metadata and cache identifiers remain accessible at the processor level. [Public architecture and API](https://github.com/AcademySoftwareFoundation/OpenColorIO/blob/main/include/OpenColorIO/OpenColorIO.h).
- **C3:** The API distinguishes bit-depth-specific CPU optimization, GPU optimization, and a reusable optimization pass when both backends are needed. It also documents the fidelity tradeoff of the legacy GPU path that bakes operations into a single 3D LUT. [Processor API](https://github.com/AcademySoftwareFoundation/OpenColorIO/blob/main/include/OpenColorIO/OpenColorIO.h).
- **C4:** Dated releases from 2012–2019 record matrix-precision improvements, concurrent file-cache work, Python compatibility, and cross-platform CI; the current API retains an explicit legacy execution path. [Historical changelog](https://github.com/AcademySoftwareFoundation/OpenColorIO/blob/main/CHANGELOG.md). That file explicitly redirects readers elsewhere for version 2 release notes.

### 3. [InternationalColorConsortium/iccDEV](https://github.com/InternationalColorConsortium/iccDEV)

**Language / role:** C++; ICC and iccMAX profile libraries plus developer tools. This is the project formerly called DemoIccMAX, counted once under its current name.

Study `IccProfLib`, particularly the division between a transform's persistent definition and per-application working state. The code handles substantially more than RGB matrices: profile chains, named colors, multidimensional LUTs, and spectral connection paths.

- **C1:** The CMM API distinguishes invalid profiles, unsupported profile classes, bad space links, and PCS-adjustment failures. Its processing-step contract requires invariant state to be initialized before concurrent `Apply()` calls, explicitly avoiding lazy-initialization data races. [CMM interfaces and concurrency contract](https://github.com/InternationalColorConsortium/iccDEV/blob/master/IccProfLib/IccCmm.h).
- **C2:** `CIccCmm` builds ordered profile chains; transform subclasses and separate `CIccApplyXform`/`CIccApplyPcsStep` objects allow different transform families to share execution machinery while retaining application-time data. [CMM architecture](https://github.com/InternationalColorConsortium/iccDEV/blob/master/IccProfLib/IccCmm.h).

### 4. [FirefoxGraphics/qcms](https://github.com/FirefoxGraphics/qcms)

**Language / role:** Rust with a C-facing API; Firefox's ICC image transformation library, originally C and subsequently converted and refactored.

Study a constrained, browser-oriented profile engine and the practical consequences of carrying a systems implementation across languages. The repository describes its Rust implementation as mostly safe, rather than claiming the entire library avoids unsafe code.

- **C1:** The parser bounds curve sizes, uses checked exponentiation for CLUT dimensions, rejects empty or excessive tables, and rejects parametric curves that divide by zero. [ICC reader](https://github.com/FirefoxGraphics/qcms/blob/main/src/iccread.rs).
- **C3:** Output lookup tables are shared through `Arc` instead of duplicated per transform. The transform layer separates pixel layouts and imports AVX, SSE2, and optional NEON kernels; comments explain the lookup-table precision/startup-memory tradeoff. [Transform construction and dispatch](https://github.com/FirefoxGraphics/qcms/blob/main/src/transform.rs).

### 5. [awxkee/moxcms](https://github.com/awxkee/moxcms)

**Language / role:** Rust; native ICC parsing and color transformation, with reusable color mathematics.

Study how an engine makes precision and interpolation policy explicit instead of hiding every choice behind a single conversion function. It offers a useful comparison with qcms and Little CMS without requiring a claim that their profile coverage is identical.

- **C1:** Transform contracts require matching source/destination sample counts. Interpolation policy distinguishes gamma-encoded RGB from Lab, XYZ, and scene-linear RGB, for which linear multidimensional interpolation remains enforced. [Transform contracts and options](https://github.com/awxkee/moxcms/blob/master/src/transform.rs).
- **C2:** Separate executor traits support different sample types and in-place or staged processing; profile, curve, matrix, and perceptual-space types are exposed independently. [Public module surface](https://github.com/awxkee/moxcms/blob/master/src/lib.rs).
- **C3:** Options expose fixed-point processing, barycentric-weight precision, and optional analytic transfer-curve handling for extended ranges. These are concrete speed/precision choices, not independently measured speedup claims. [Transform options](https://github.com/awxkee/moxcms/blob/master/src/transform.rs).

### 6. [google/skcms](https://github.com/google/skcms)

**Language / role:** C++ implementation with a C API; ICC/profile and pixel-format conversion. **Official read-only GitHub mirror:** the repository explicitly points upstream to Skia's source server; substantive source is on the `mirror` branch, while `main` contains mirror infrastructure.

Study a compact transform API backed by shared scalar/vector kernels. This is a useful example of fitting color management into low-level graphics processing without exposing a large object hierarchy.

- **C1:** The API defines buffer-aliasing conditions, alpha representations, profile-buffer lifetimes, and fallible destination-profile approximation. It separates parsed transfer curves, matrices, and A2B/B2A tables through explicit availability fields. [Public contracts](https://github.com/google/skcms/blob/mirror/src/skcms_public.h).
- **C3:** The same transform implementation is instantiated with different SIMD widths and architecture-specific capabilities, including vectorized pixel conversion and explicit IEEE half-float handling. [Shared transform kernels](https://github.com/google/skcms/blob/mirror/src/Transform_inl.h).

### 7. [aces-aswf/aces-core](https://github.com/aces-aswf/aces-core)

**Language / role:** CTL, the Color Transformation Language; core ACES rendering and color-science reference library. The repository preserves the history of the earlier `aces-dev` project; old names and component repositories are not counted separately here.

Study the actual rendering mathematics beneath an ACES implementation, especially the split between parameter initialization and forward/inverse transform evaluation. This is reference transform code rather than a general-purpose ICC engine.

- **C1:** The tone-scale implementation makes scene-referred values, display luminance, peak-dependent parameters, and inverse-domain limits explicit. The output-transform implementation includes circular hue indexing, padded hue tables, and separate numerical search tolerances. [Tone scale](https://github.com/aces-aswf/aces-core/blob/main/lib/Lib.Academy.Tonescale.ctl); [output transform](https://github.com/aces-aswf/aces-core/blob/main/lib/Lib.Academy.OutputTransform.ctl).
- **C2:** `TSParams`, `JMhParams`, and `ODTParams` collect reusable parameters for tone scale, appearance-space conversion, chroma compression, and gamut compression across output configurations. [Output-transform architecture](https://github.com/aces-aswf/aces-core/blob/main/lib/Lib.Academy.OutputTransform.ctl).

## Spectral science, appearance models, and conversion graphs

### 8. [colour-science/colour](https://github.com/colour-science/colour)

**Language / role:** Python; broad scientific library covering spectral colorimetry, appearance models, chromatic adaptation, color differences, and related datasets.

Study how scientific algorithms share spectral representations without concealing normalization, observer, or sampling assumptions. The tristimulus implementation is a particularly informative entry into the larger package.

- **C1:** Spectral-to-XYZ conversion checks array lengths against wavelength shapes, aligns illuminants and color-matching functions, distinguishes absolute versus relative normalization, and implements dedicated ASTM E308 handling for measurement intervals. [Tristimulus implementation](https://github.com/colour-science/colour/blob/develop/colour/colorimetry/tristimulus_values.py).
- **C2:** The same routines accept spectral-distribution objects, multispectral distributions, and explicitly shaped arrays. Shared spectral argument handling and weighting-factor functions support both ordinary integration and standards-based methods. [Same implementation](https://github.com/colour-science/colour/blob/develop/colour/colorimetry/tristimulus_values.py).
- **C3:** The array path performs batched matrix multiplication after alignment and weighting setup, exposing a clear boundary between spectral preparation and bulk numerical work. [Array execution path](https://github.com/colour-science/colour/blob/develop/colour/colorimetry/tristimulus_values.py).

### 9. [ksmet1977/luxpy](https://github.com/ksmet1977/luxpy)

**Language / role:** Python; lighting and color-science toolkit, including spectral calculations, color rendering, appearance models, and correlated color temperature.

Study an application-oriented scientific toolkit where multiple published numerical methods coexist behind related interfaces. Its CCT implementation makes a good comparison with a library that exposes only one approximation.

- **C1:** The CCT source documents observer-dependent validity limits, distinguishes CCT from distance to the Planckian locus, and warns when changing observer data would make a fitted approximation inconsistent. It implements multiple methods with different assumptions. [CCT algorithms and contracts](https://github.com/ksmet1977/luxpy/blob/master/luxpy/color/cct/cct.py).
- **C2:** CCT calculations can receive a named color space, forward/backward conversion functions, or a mapping describing those transforms; observer and wavelength parameters are carried through the interface. This supports comparing numerical methods under different colorimetric configurations. [CCT implementation](https://github.com/ksmet1977/luxpy/blob/master/luxpy/color/cct/cct.py).

### 10. [njsmith/colorspacious](https://github.com/njsmith/colorspacious)

**Language / role:** Python/NumPy; color-space conversion, CIECAM02 appearance modeling, and color-vision-deficiency simulation. **Historical release caution:** the inspected repository lists [v1.1.2 from April 2018](https://github.com/njsmith/colorspacious/releases) as its latest release; this entry does not imply current release maintenance.

Study the parameterized conversion graph: a color space is more than a string because viewing conditions and other attributes constrain which paths are valid.

- **C1:** CIECAM02 explicitly handles inputs with a negative achromatic signal through either an exception or NaN propagation, and validates vectorized input shape. [Appearance model](https://github.com/njsmith/colorspacious/blob/master/colorspacious/ciecam02.py).
- **C2:** `TransformGraph` precomputes paths and matches concrete endpoint parameters against placeholder-constrained nodes before composing transforms. The graph source includes invariant checks and tests for its matching machinery. [Conversion graph](https://github.com/njsmith/colorspacious/blob/master/colorspacious/transform_graph.py).

### 11. [facelessuser/coloraide](https://github.com/facelessuser/coloraide)

**Language / role:** Python; extensible color-space conversion and color manipulation library.

Study a conversion architecture built around each space's relationship to a base space. The readable conversion module exposes the mechanics behind a broad user-facing color API.

- **C1:** Conversion paths explicitly mark where white-point adaptation is necessary, resolve NaN coordinates before numerical conversion, and enforce a maximum traversal count to detect pathological conversion chains. [Conversion implementation](https://github.com/facelessuser/coloraide/blob/main/coloraide/convert.py).
- **C2:** Registered spaces provide `BASE`, `to_base`, and `from_base` relationships; the engine constructs a path through shared ancestors and separates path construction from execution. Cached chains can then be reused for subsequent conversions. [Conversion graph and execution](https://github.com/facelessuser/coloraide/blob/main/coloraide/convert.py).

### 12. [harbik/colorimetry](https://github.com/harbik/colorimetry)

**Language / role:** Rust with WebAssembly support; spectral colorimetry for illuminants, filters, observers, and color-quality calculations.

Study a less prominent library whose central objects represent physical light and materials rather than only RGB triples. The inspected implementation fixes its spectral domain to 380–780 nm at 1 nm spacing; that design boundary matters when comparing results with wider-domain datasets.

- **C1:** Illuminant code documents physical units and truncation of standard daylight spectra. Observer computations normalize filtered stimuli against the unfiltered source and retain both stimulus and reference-white values for subsequent appearance calculations. [Illuminants](https://github.com/harbik/colorimetry/blob/main/src/illuminant.rs); [observer calculations](https://github.com/harbik/colorimetry/blob/main/src/observer.rs).
- **C2:** `Light` and `Filter` interfaces combine with selectable observers, allowing the same computation to work with standard illuminants, synthesized spectra, and material/filter spectra. [Observer API and implementation](https://github.com/harbik/colorimetry/blob/main/src/observer.rs).

## Typed color APIs and numerical language ecosystems

### 13. [Ogeon/palette](https://github.com/Ogeon/palette)

**Language / role:** Rust; typed linear-light calculations, color conversion, blending, and color manipulation.

Study how a type system can express distinctions that are often implicit in image-processing code. The library's conceptual documentation lives alongside its public module structure and explains the tradeoffs behind its abstractions.

- **C1:** Component type, reference white, and RGB encoding/standard are represented through type parameters; `Srgb` and `LinSrgb` are distinct variants. This makes accidental mixing of incompatible encodings harder. [Library architecture](https://github.com/Ogeon/palette/blob/master/palette/src/lib.rs).
- **C2:** Conversion traits operate across spaces, while generic `Alpha` and `PreAlpha` composition avoid defining a separate transparent implementation for every color model. Buffer casting, optional allocation, and `no_std` support extend those abstractions beyond desktop applications. [Public module documentation](https://github.com/Ogeon/palette/blob/master/palette/src/lib.rs).

### 14. [JuliaGraphics/Colors.jl](https://github.com/JuliaGraphics/Colors.jl)

**Language / role:** Julia; color conversion, perceptual differences, color-vision simulation, and graphics-oriented color operations.

Study multiple dispatch over color and difference-metric types. The repository deliberately builds on separate ColorTypes and ColorVectorSpace packages; those dependencies are not additional entries in this report.

- **C1:** Difference functions explicitly distinguish asymmetric CIE94/CMC comparisons from symmetric expectations. CIEDE2000 processing converts inputs to Lab, chooses working precision, and handles circular hue calculations as part of the metric. [Difference algorithms](https://github.com/JuliaGraphics/Colors.jl/blob/master/src/differences.jl).
- **C2:** Metric objects carry weighting factors or white points, and generic color inputs dispatch into the appropriate representation and algorithm. Users can choose perceptual models without duplicating conversion logic. [Metric hierarchy and dispatch](https://github.com/JuliaGraphics/Colors.jl/blob/master/src/differences.jl).
- **C3:** The same file provides specialized Float32 polynomial paths for parts of CIEDE2000 alongside the general formulation, making numerical optimization inspectable rather than opaque. [Specialized implementations](https://github.com/JuliaGraphics/Colors.jl/blob/master/src/differences.jl).

### 15. [lehins/Color](https://github.com/lehins/Color)

**Language / role:** Haskell; color models, color spaces, pixels, and chromatic adaptation. Source modules label their stability as experimental.

Study the distinction between a color model, an actual color space, and an alternative representation, enforced through types. This provides a different perspective from Rust's encoding types or dynamically registered conversion graphs.

- **C1:** `convertColor` requires the source and destination to share the same illuminant type parameter; changing illuminants requires the separate adaptation API. It also chooses an explicit Double intermediate, with a separate Float variant. [Conversion implementation and signatures](https://github.com/lehins/Color/blob/master/Color/src/Graphics/Color/Space.hs).
- **C2:** A shared `ColorSpace` interface composes conversions through XYZ while preserving the destination type. The repository's examples show the same abstraction across encoded RGB, Lab, different component precisions, and adaptation workflows. [Typed conversion core](https://github.com/lehins/Color/blob/master/Color/src/Graphics/Color/Space.hs); [repository examples](https://github.com/lehins/Color#example).

### 16. [tompazourek/Colourful](https://github.com/tompazourek/Colourful)

**Language / role:** C#/.NET; color-space conversion, chromatic adaptation, color differences, and color-temperature utilities.

Study an API that forces conversion metadata to be configured before a reusable converter is constructed. It is a concrete example of turning color-science assumptions into application-level contracts.

- **C1:** Conversions requiring an unspecified white point fail with `MissingConversionMetadataException`. The documentation explains when adaptation is inserted and why out-of-range target values are preserved instead of automatically clamped. [Conversion contracts](https://github.com/tompazourek/Colourful/blob/master/docs/topic-conversion.md).
- **C2:** A staged `ConverterBuilder` produces `IColorConverter<TSource,TTarget>` objects intended for reuse. RGB working spaces and source/target white points are parameters, while Lab and Hunter Lab conversions share XYZ routing with different formulas and reference-white expectations. [Builder architecture](https://github.com/tompazourek/Colourful/blob/master/docs/topic-conversion.md); [Lab conversion strategy](https://github.com/tompazourek/Colourful/blob/master/docs/spaces-lab.md).

### 17. [ajalt/colormath](https://github.com/ajalt/colormath)

**Language / role:** Kotlin Multiplatform; conversion, chromatic adaptation, perceptual differences, and configurable gradients.

Study how a multiplatform library combines typed color-space objects with a gradient-building API while documenting unusual numerical values as meaningful state.

- **C1:** Grayscale hue is represented as NaN rather than assigned an arbitrary angle. The usage guide explains alpha premultiplication, hue/component adjustment before interpolation, and the different effects of interpolation geometry and easing. [Numerical semantics and interpolation](https://github.com/ajalt/colormath/blob/master/docs/usage.md).
- **C2:** Users can define color spaces with custom illuminants, reuse RGB-to-RGB converters, and configure interpolation methods, per-component easing, and per-stop behavior through the same builder. [Usage and architecture](https://github.com/ajalt/colormath/blob/master/docs/usage.md).

### 18. [lucasb-eyer/go-colorful](https://github.com/lucasb-eyer/go-colorful)

**Language / role:** Go; color conversions, perceptual distances, blending, and palette-oriented operations.

Study a comparatively compact implementation that bridges Go's image interfaces and color-science operations. Its concentration of conversion and distance algorithms in one source file makes it approachable for following numerical edge cases end to end.

- **C1:** Conversion from `image/color.Color` reverses premultiplied alpha and handles fully transparent input. CIEDE2000 implements zero-chroma and hue-wrap branches; HCL blending treats nearly achromatic endpoints specially. [Numerical implementation](https://github.com/lucasb-eyer/go-colorful/blob/master/colors.go).
- **C2:** The `Color` value implements Go's standard color interface while exposing multiple perceptual spaces, configurable reference-white conversions, distance measures, and blending operations. This supports image tooling and visualization without requiring a bespoke image container. [Color abstraction and algorithms](https://github.com/lucasb-eyer/go-colorful/blob/master/colors.go).

### 19. [thomasp85/farver](https://github.com/thomasp85/farver)

**Language / role:** R and C++; vectorized color conversion, comparison, string encoding/decoding, and channel manipulation. Its native implementation incorporates a modified ColorSpace library, rather than merely forwarding calls to an installed external engine.

Study the boundary between a high-level matrix API and specialized native loops. The design makes both R-specific semantics and runtime-to-template dispatch visible.

- **C1:** Native color objects track validity for nonfinite values and R integer missing values; conversion code checks dimensional compatibility and applies space-specific range handling. [Color representations](https://github.com/thomasp85/farver/blob/main/src/ColorSpace.cpp); [conversion dispatch](https://github.com/thomasp85/farver/blob/main/src/farver.cpp).
- **C3:** Runtime source/destination choices dispatch into C++ template instantiations. Each batch allocates an output matrix once and processes column-major input directly, with separate integer and floating-point access. [Native batch implementation](https://github.com/thomasp85/farver/blob/main/src/farver.cpp).

## Web color science, gamut mapping, and perceptual palettes

### 20. [color-js/color.js](https://github.com/color-js/color.js)

**Language / role:** JavaScript; color-space conversion and manipulation with strong CSS color integration.

Study a space-independent API whose gamut mapping exposes perceptual choices and numerical stopping rules. The project is particularly relevant when a color library must operate beyond the gamut of the final display or serialization format.

- **C1:** Gamut mapping distinguishes clipping, CSS mapping, ray tracing, and coordinate-reduction strategies. The reduction path uses a selected color-difference method and just-noticeable-difference target, with an epsilon floor to prevent nonterminating searches. [Gamut implementation](https://github.com/color-js/color.js/blob/main/src/toGamut.js).
- **C2:** The same mapping machinery resolves target spaces and coordinates through `ColorSpace`, and can reduce a selected coordinate in another space before returning to the original representation. The repository also exposes object-oriented and procedural use of its color-space modules. [Gamut architecture](https://github.com/color-js/color.js/blob/main/src/toGamut.js); [repository API overview](https://github.com/color-js/color.js#features).

### 21. [Evercoder/culori](https://github.com/Evercoder/culori)

**Language / role:** JavaScript; functional color conversion, interpolation, and manipulation.

Study how color-space definitions drive a generic interpolation engine. This is a useful alternative to building an independent gradient implementation for every color model.

- **C1:** Interpolation normalizes stop positions, applies channel fixups before interpolation, handles missing/NaN channel values, and offers an explicit premultiplied-alpha interpolation path. [Interpolation implementation](https://github.com/Evercoder/culori/blob/main/src/interpolate/interpolate.js).
- **C2:** Mode definitions supply channels and default interpolation functions; callers can override individual channels, global methods, and local easing. `interpolateWith` composes pre- and post-mapping around the common engine. [Generic interpolation architecture](https://github.com/Evercoder/culori/blob/main/src/interpolate/interpolate.js).

### 22. [gka/chroma.js](https://github.com/gka/chroma.js)

**Language / role:** JavaScript; color manipulation and perceptual color scales for visualization.

Study the scale generator rather than only string-to-color helpers. It combines data-domain mapping, class breaks, interpolation, missing-data behavior, and optional lightness correction in a reusable callable object.

- **C1:** Lightness correction uses a bounded iterative search against Lab lightness; missing values and degenerate domains receive explicit handling. [Scale implementation](https://github.com/gka/chroma.js/blob/main/src/generator/scale.js).
- **C2:** A scale can change domains, interpolation modes, padding, gamma, output formats, and class boundaries while retaining a consistent interface. Its sampled-color cache and reset points also expose the costs of this mutable abstraction. [Scale architecture](https://github.com/gka/chroma.js/blob/main/src/generator/scale.js).

The [changelog](https://github.com/gka/chroma.js/blob/main/CHANGELOG.md) is an additional useful reading path for the CoffeeScript-to-ES6 transition, modularization, and fixes involving hue-less colors and CSS parsing; no unverified maintenance cadence is implied.

### 23. [texel-org/color](https://github.com/texel-org/color)

**Language / role:** JavaScript; low-level color conversion and gamut mapping for image processing and creative coding.

Study a smaller implementation that makes its approximation strategy and temporary-storage choices visible. Its distinct value here is its numerical kernel design, not the comparative speed multipliers advertised in its README.

- **C1:** Gamut calculations require normalized hue coordinates and select coefficient sets according to which RGB channel reaches the boundary. Polynomial saturation estimates are refined with Halley's method, with source comments acknowledging difficult blue-hue behavior. [Gamut algorithms](https://github.com/texel-org/color/blob/main/src/gamut.js).
- **C3:** Shared scratch vectors, precomputed coefficient/matrix inputs, and a short refinement step address repeated gamut calculations. Separate mapping functions choose different lightness targets without replacing the underlying boundary calculation. [Kernel structure](https://github.com/texel-org/color/blob/main/src/gamut.js).

### 24. [material-foundation/material-color-utilities](https://github.com/material-foundation/material-color-utilities)

**Language / role:** Multi-language monorepo: TypeScript, C++, Dart, Java, Kotlin, and Swift implementations of Material color algorithms. Counted once; the HCT/CAM16, quantization, and palette subsystems establish category fit beyond UI theming helpers.

Study the inverse problem of producing an in-gamut sRGB color with requested perceptual hue, chroma, and tone. The TypeScript solver is an accessible entry into algorithms shared across the library's platform implementations.

- **C1:** `HctSolver` first attempts a bounded solution in appearance-model lightness, then falls back to gamut-boundary bisection. Achromatic and extreme-tone inputs receive separate handling, and unattainable chroma is treated as a constrained solution. [HCT solver](https://github.com/material-foundation/material-color-utilities/blob/main/typescript/hct/hct_solver.ts).
- **C2:** The repository separates appearance modeling, blending, contrast, quantization, palettes, scoring, and dynamic schemes so consumers can reuse subsets. The solver itself reuses viewing conditions and color/math utilities. [Component architecture](https://github.com/material-foundation/material-color-utilities#capabilities-overview); [solver implementation](https://github.com/material-foundation/material-color-utilities/blob/main/typescript/hct/hct_solver.ts).
- **C3:** The solver hoists hue- and viewing-condition-dependent calculations outside its iteration loop and inlines selected CAM16 operations to avoid recomputation. [Solver's `findResultByJ`](https://github.com/material-foundation/material-color-utilities/blob/main/typescript/hct/hct_solver.ts).

## Search coverage and limitations

Discovery used more than six distinct live web-search formulations, including ICC/CMM architecture; spectral color science and appearance models; Rust ICC and typed color libraries; JavaScript/CSS gamut mapping; Julia and R numerical libraries; C#/.NET and Kotlin conversion APIs; Haskell color-space types; Material HCT algorithms; ACES reference transforms; and operating-system/printing color management. Searches were followed by repository-page opens and direct reads of source files, API contracts, or documentation. Later searches increasingly returned already selected libraries, language ports, wrappers, GUI applications, and narrow utilities. ACES core was retained from the later reference-implementation search because it adds a distinct architectural family.

Selection boundaries and limitations:

- **GitHub provenance matters.** Google's skcms mirror is explicitly identified and its substantive branch verified. [Oyranos](https://github.com/oyranos-cms/oyranos) was investigated, but its README directs source and support to GitLab; a continuing GitHub mirror arrangement was not established, so it was omitted. ArgyllCMS search results included third-party forks; none was treated as the canonical upstream or as an independently justified implementation.
- **No duplicate ecosystems disguised as separate projects.** DemoIccMAX/iccDEV and aces-dev/aces-core are each counted once. Material's language implementations are one monorepo entry; straightforward external ports and thin Little CMS bindings were excluded. Julia's separate type/arithmetic dependencies are discussed only as context for Colors.jl.
- **Scope stays on reusable implementations.** Color pickers, terminal ANSI-color packages, palette/data-only collections, general editors, and configuration-only repositories were not included. Less prominent selections such as moxcms, colorimetry, lehins/Color, go-colorful, and texel/color add distinct implementations rather than filling a popularity quota.
- **Evidence is selective.** The linked code demonstrates the stated engineering concerns; this research did not build libraries, execute candidate code, run their tests, reproduce benchmarks, or independently validate conformance to every cited color standard. Performance criteria refer to inspectable implementation strategies, not measured superiority. C4 is used selectively where historical compatibility/testing evidence was actually read.
- **Status is a research-date snapshot.** Source links generally target the inspected default branch, except the explicit skcms mirror. They can evolve. Colorspacious is retained as a substantive historical study, and experimental stability labels are preserved for the Haskell library. The list is not a maintenance ranking or an assertion that every repository suits a new production dependency.
