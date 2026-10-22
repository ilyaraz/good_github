# Two-dimensional vector graphics and rasterization libraries

Research date: 2026-10-09.

This selection covers 25 GitHub repositories implementing reusable 2D drawing models, path tessellation, antialiased scan conversion, compositing, or SVG rendering. It spans CPU, GPU, hybrid, embedded, managed, and functional implementations. Geometry libraries are included when they directly support vector drawing; image codecs, thin bindings, complete editors, and primarily 3D engines are outside the selection. Each repository was opened, and additional primary implementation or architecture material was read. Linked source files and documents are the recommended study entry points.

The criteria identify worthwhile engineering problems, not a guarantee that every component is exemplary or every input is handled correctly. Architectural observations below are grounded in the linked material; the choice of what to study is an engineering judgment. Default-branch sources can describe work newer than a published release. Maintenance is not inferred from stars, repository age, or an isolated recent commit.

Criteria legend:

- **C1 — Difficult correctness:** numerical semantics, invariants, concurrency, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and representations serving multiple drawing use cases.
- **C3 — Performance with structure:** concrete optimization mechanisms within an understandable architecture.
- **C4 — Sustained evolution:** development across years accompanied by compatibility, testing, or complexity-management evidence.

## General-purpose rendering engines

### 1. [google/skia](https://github.com/google/skia)

**C++; comprehensive 2D graphics engine. Official GitHub mirror of Skia's Googlesource repository.** Focus on the CPU backend to make this large codebase tractable: follow a path draw from `SkCanvas` through device dispatch, coverage generation, and pixel blending.

- **C2:** The architecture distinguishes drawing state (`SkCanvas`), geometry (`SkPath`), styling (`SkPaint`), storage ownership, and a lightweight pixel-memory view. Scan conversion produces coverage independently of color processing, allowing paints and effects to reuse the same geometry machinery.
- **C3:** `SkRasterPipeline` assembles precompiled stages for coverage, shading, blending, and storage rather than requiring a function for every combination. SIMD processes multiple pixels, while device tiling bounds intermediate memory. These mechanisms and their call flow are explained in the [CPU architecture guide](https://github.com/google/skia/blob/main/docs/architecture/CPU.md).

The most useful lesson is how a broad drawing API reaches specialized low-level execution without exposing that complexity to every caller.

### 2. [blend2d/blend2d](https://github.com/blend2d/blend2d)

**C++; CPU vector renderer with generated rendering pipelines.** Study the interaction of analytic coverage, curve-offset stroking, pipeline specialization, and asynchronous drawing.

- **C1:** Workers acquire exclusive scanline bands and process queued drawing commands for those bands. Pixel ownership avoids workers racing over the same destination pixels. The project also describes checking portable and JIT pipelines for pixel-identical results across instruction-set variants.
- **C3:** Pipeline selection is table driven, generated pipelines are cached, and band processing keeps destination pixels local across drawing commands. These are concrete architectural responses to dispatch overhead and memory locality, not merely benchmark claims.
- **C4:** The documented history connects the 2015 prototype, 2020 multithreaded context, 2023 dispatch redesign, and 2024 AArch64 abstraction and cross-pipeline testing. Read the [design and development history](https://blend2d.com/about.html), especially the stability and multithreading sections.

This is a particularly useful comparison with Skia's precompiled pipeline stages.

### 3. [thorvg/thorvg](https://github.com/thorvg/thorvg)

**C++; retained vector scenes, SVG/Lottie content, and CPU/GPU backends.** Study how scene updates, rendering resources, and optional parallel execution meet below the public drawing model.

- **C2:** Shared rendering structures describe surfaces, composition purposes, clipping regions, and update flags for geometry, paint, transforms, images, and children. They provide a common vocabulary across backends. Start with [tvgRender.h](https://github.com/thorvg/thorvg/blob/main/src/renderer/tvgRender.h).
- **C1:** The scheduler must coordinate queue access, condition-variable wakeups, task preparation, and shutdown before destroying worker resources. Its zero-worker configuration also provides synchronous execution.
- **C3:** Workers try other queues before blocking on their own; task submission likewise tries available queues before a blocking push. The compact [task scheduler implementation](https://github.com/thorvg/thorvg/blob/main/src/renderer/tvgTaskScheduler.cpp) makes the parallelism policy inspectable.

The relevant subsystems are `src/renderer`, including the CPU and GPU engines; this repository is counted once despite its multiple backends.

## GPU, hybrid rendering, and tessellation

### 4. [linebender/vello](https://github.com/linebender/vello)

**Rust and shader languages; CPU, hybrid GPU, and experimental compute renderers in one repository.** The current layout matters: `vello_cpu` and `vello_gpu` use Sparse Strips; the original compute-centric implementation lives under `research/`.

- **C2:** The Sparse Strips implementations share geometry, tiling, paint, image, and strip representations in `vello_common`, with shared glyph support and test scenes. The same intermediate representation feeds different execution targets.
- **C3:** CPU preprocessing flattens and bins paths, retaining boundary coverage while compactly representing fully covered regions. CPU execution uses SIMD and threading; the hybrid GPU path uploads scheduled strips for vertex/fragment rendering. The research implementation instead encodes scene buffers and uses prefix scans in compute shaders. Read the [architecture guide](https://github.com/linebender/vello/blob/main/ARCHITECTURE.md).

This is an unusually direct study of different hardware strategies within one project. The repository explicitly distinguishes maturity profiles; the compute renderer remains experimental.

### 5. [servo/pathfinder](https://github.com/servo/pathfinder)

**Rust; tiled GPU rasterization for paths and fonts.** Study the separation between geometric preparation and GPU coverage/shading. The README explicitly notes incomplete areas.

- **C1:** The documented CPU preparation converts strokes to fills and makes curves monotonic before cutting paths into tiles. Correct coverage, path order, and occlusion decisions must survive those transformations.
- **C3:** The [architecture document](https://github.com/servo/pathfinder/blob/main/doc/architecture.md) describes parallel path preparation, solid-tile detection, occlusion culling, packed batches, an alpha-coverage pass, and a shading pass. It provides a readable explanation of where work is removed or moved between processors.

That document describes the CPU-setup pipeline; the repository README additionally distinguishes compute-based and hardware-rasterization modes. Its “D3D9” and “D3D11” labels refer to capability levels, not implemented Direct3D backends. Treat the document's historical timings as context, not present-day performance evidence.

### 6. [memononen/nanovg](https://github.com/memononen/nanovg)

**C; immediate-mode antialiased vector drawing over OpenGL.** A relatively compact place to study conversion from a canvas-like command stream into fill and stroke geometry.

- **C1:** Path flattening normalizes winding, merges coincident closing points within a tolerance, and computes segment directions. Join construction handles inner bevels, miter limits, round joins, and device-dependent antialiasing fringes; these choices directly affect cracks and spikes.
- **C2:** The drawing context separates saved paint/transform state, path commands and caches, font resources, and renderer callbacks. Public drawing operations reuse this machinery instead of issuing unrelated backend operations.

Start with [nanovg.c](https://github.com/memononen/nanovg/blob/master/src/nanovg.c), particularly `nvg__flattenPaths`, `nvg__calculateJoins`, and `nvg__expandStroke`. Its value here is the inspectable implementation; no current maintenance guarantee is inferred.

### 7. [femtovg/femtovg](https://github.com/femtovg/femtovg)

**Rust; GPU vector drawing descended from NanoVG.** Retained separately because it is a native Rust implementation with substantial additional command, clipping, layer, filter, and backend machinery—not a generated binding.

- **C1:** Persistent stencil clipping must coexist with winding accumulation and clears. Commands track clip participation, and the code explicitly preserves the clip plane when clearing winding bits. Clip bounds also account for backend restrictions on empty scissors.
- **C2:** A `Renderer` trait and typed command variants separate canvas operations from OpenGL and optional wgpu execution. Convex fills, concave fills, stencil strokes, render targets, and filtered images share a command model.
- **C3:** Bounding draw work by clip reach reduces fragment processing, while filter metadata can fuse color-matrix work into existing passes. These mechanisms are visible in [renderer.rs](https://github.com/femtovg/femtovg/blob/master/src/renderer.rs).

Read the implementation when checking backend capabilities: its current module declarations are more specific than the older single-backend wording in the README.

### 8. [nical/lyon](https://github.com/nical/lyon)

**Rust; vector paths, geometry, and fill/stroke tessellation.** This produces triangle geometry for a renderer rather than a finished pixel image. It belongs here as a reusable vector-rendering stage.

- **C1:** The fill tessellator handles self-intersections, merged coincident vertices, winding state, and active-edge ordering. Its implementation clamps computed edge positions because floating-point error can otherwise make ordering inconsistent. The API explicitly does not accept NaN inputs.
- **C2:** Input can arrive through path events or indexed position/attribute stores, while `FillGeometryBuilder` controls output storage. Vertex provenance and lazily interpolated attributes let applications preserve their own colors or texture coordinates when tessellation creates new vertices.

The documentation and implementation in [fill.rs](https://github.com/nical/lyon/blob/main/crates/tessellation/src/fill.rs) are the main entry point. Study the active-edge structures first, then the custom-attribute explanation; it connects numerical topology to a useful extensibility contract.

## Software rasterizers and compact implementations

### 9. [linebender/tiny-skia](https://github.com/linebender/tiny-skia)

**Rust; CPU-only port of a selected Skia subset.** It is an independently implemented, reduced rendering library, not a wrapper around the C++ engine. The project describes itself as a research project rather than a Skia replacement.

- **C2:** A stage-based raster pipeline composes color generation, transforms, masks, sampling, blending, and storage. A shared context carries the state needed by different stages.
- **C3:** Pipeline construction chooses the low-precision implementation only when every required stage supports it; otherwise it selects high precision. Execution chains function pointers, and stage design minimizes branching in pixel-processing work. Read the rationale and implementation in [pipeline/mod.rs](https://github.com/linebender/tiny-skia/blob/main/src/pipeline/mod.rs).

It is useful for examining what survives when a broad engine is reduced to a small portable rasterizer. The repository covers fills, strokes, dashes, clipping, and image blending, while identifying text rendering as a missing feature.

### 10. [google/forma](https://github.com/google/forma)

**Rust; experimental parallel vector renderer. Archived on 2024-07-18.** Include it as a historical architecture study, not as a maintained dependency recommendation.

- **C3:** Its four-stage pipeline separates curve flattening, line rasterization, pixel-segment sorting, and painting. CPU work uses SIMD and Rayon; the repository also contains a GPU backend.
- **C1:** The CPU renderer's reuse of cached tiles requires tracking layer changes, previous clear color, and buffer dimensions. Changing dimensions clears the layer cache, while geometry identifiers must continue to map to valid composition ordering.

Start with the pipeline explanation on the repository page and then [cpu/renderer.rs](https://github.com/google/forma/blob/main/forma/src/cpu/renderer.rs). The latter shows cache invalidation, rendering-stage orchestration, and recycling of the segment buffer in one manageable implementation. It is a useful contrast with immediate-mode engines that rebuild all work for each draw.

### 11. [sammycage/plutovg](https://github.com/sammycage/plutovg)

**C; standalone canvas-style software vector library.** Study its span representation and the boundary between path geometry, outline stroking, and compositing. It also supplies rendering infrastructure used by LunaSVG, listed separately for its SVG semantics.

- **C1:** Geometry is transformed and converted into fixed-point outlines with explicit contour boundaries and closure flags. Clipping intersects ordered spans and multiplies their coverage values, so contour and coverage semantics remain central even in a small implementation.
- **C2:** Paths, surfaces, canvas state, and solid/gradient/texture paints support a reusable drawing API. Internally, span buffers provide common operations for rectangular initialization, copying, extents, hit testing, and clipping.

The substantive entry point is [plutovg-rasterize.c](https://github.com/sammycage/plutovg/blob/main/source/plutovg-rasterize.c). It makes the adaptation to the included FreeType-derived outline rasterizer/stroker visible; this should not be mistaken for an entirely unrelated rasterization algorithm.

### 12. [a-e-k/canvas_ity](https://github.com/a-e-k/canvas_ity)

**C++03-style single-header CPU renderer; official release mirror of the author's local Mercurial repository.** The project considers its feature set largely complete and does not accept outside code contributions.

- **C1:** The implementation combines signed trapezoidal coverage, linear-light premultiplied-alpha processing, bicubic resampling, and careful stroke expansion. It also documents concrete limits: coverage at subpixel self-intersections, mask-based clipping, and font parsing that is unsuitable for unsanitized fonts.
- **C2:** A canvas API integrates paths, paints, transforms, saved state, compositing, shadows, images, and basic text. An internal data-flow explanation follows poly-Béziers through flattening, dashing, stroking, sparse coverage, and painting.

Read [canvas_ity.hpp](https://github.com/a-e-k/canvas_ity/blob/main/src/canvas_ity.hpp) and the independent [test harness](https://github.com/a-e-k/canvas_ity/blob/main/test/test.cpp), which hashes rendered outputs and supports image inspection. The complete pipeline is small enough to study end to end; test coverage alone is not treated as proof of correctness or sustained evolution.

### 13. [micro-gl/micro-gl](https://github.com/micro-gl/micro-gl)

**C++ templates; CPU vector graphics for constrained systems, with additional 3D facilities.** The relevant scope is its 2D canvas, path rendering, sampling, and compositing; the repository is counted once.

- **C1:** Rasterizer options expose arithmetic choices directly: larger intermediates, division-based UV calculations, bit compression, and optional overflow detection that stops rendering. These are explicit numerical tradeoffs, particularly in 32-bit configurations.
- **C2:** Canvas templates compose bitmap/pixel coders, samplers, blend modes, and Porter–Duff operations. Number types can be selected for environments without a floating-point unit.
- **C3:** Compile-time policies and a separately positioned canvas window permit specialized rasterization and block rendering into buffers smaller than the logical canvas.

Start with [canvas.h](https://github.com/micro-gl/micro-gl/blob/master/include/microgl/canvas.h), especially the option definitions and bitmap/window interfaces. The source header carries a custom license notice; evaluate that separately when considering reuse.

## SVG document interpretation and rendering

### 14. [linebender/resvg](https://github.com/linebender/resvg)

**Rust; static SVG parsing, normalization, and rendering.** Count `usvg` and the renderer together as one repository. This adds document semantics above tiny-skia rather than duplicating its pixel engine.

- **C1:** The parser resolves CSS, inherited/default values, relative units, references, and text; it detects recursive elements and removes malformed or unsupported structures. The repository also describes recursion/loop protections and image regression tests.
- **C2:** `usvg` transforms SVG into a strongly typed tree whose shapes, path commands, coordinate systems, and references are already normalized. This deliberately lets downstream renderers work with a smaller semantic model.

Read the implementation-level crate documentation in [usvg/src/lib.rs](https://github.com/linebender/resvg/blob/main/crates/usvg/src/lib.rs). It spells out both the normalization contract and its limits, including static-only rendering and limited CSS. The study opportunity is the boundary between permissive document syntax and a renderer-friendly representation, not a claim of complete browser equivalence.

### 15. [GNOME/librsvg](https://github.com/GNOME/librsvg)

**Rust with a stable C-facing API; SVG rendering to Cairo surfaces. Official read-only GitHub mirror of GNOME GitLab.** A particularly strong case study in evolving an established graphics library without breaking its callers.

- **C2:** A C compatibility layer calls the public Rust API, which operates on parsed documents and rendering handles. Internally, specified CSS values become computed values after cascading. The [architecture guide](https://github.com/GNOME/librsvg/blob/main/devel-docs/architecture.rst) explains these boundaries.
- **C1:** Tests distinguish parser crashes, rendering crashes, semantic image differences, and resource-limit failures. Limits on elements and instanced objects address excessive memory and CPU use.
- **C4:** The architecture history traces the original 2001 library and the 2016–2021 C-to-Rust transition while preserving the C API/ABI. The [test-suite guide](https://github.com/GNOME/librsvg/blob/main/rsvg/tests/README.md) documents tests for deprecated functions and historical API behavior, alongside reference-image and error tests.

Use the official GitLab project for contribution activity; the GitHub mirror remains a substantive source tree.

### 16. [sammycage/lunasvg](https://github.com/sammycage/lunasvg)

**C++; SVG document rendering and manipulation over PlutoVG.** Its independent value is in document/style interpretation and group rendering, not a second copy of PlutoVG's rasterizer.

- **C1:** Rendering state checks ancestor references for cycles. Group opacity, clip paths, and masks require deciding whether direct drawing is valid or an intermediate canvas is needed; offscreen bounds are intersected with canvas extents.
- **C2:** Document loading, styling, hit testing, and rendering sit above a reusable group-state abstraction. A group either saves/restores the existing canvas or composites a separate canvas back into its parent.

The compact [svgrenderstate.cpp](https://github.com/sammycage/lunasvg/blob/master/source/svgrenderstate.cpp) is a good first read because it exposes these decisions without requiring an initial tour of the entire parser. The repository describes static SVG support and explicitly excludes animation, filters, and scripts; its broader feature claims are not treated here as verified conformance scores.

## Go drawing and rasterization components

### 17. [tdewolff/canvas](https://github.com/tdewolff/canvas)

**Go; vector drawing model with raster, SVG, PDF, EPS, and interactive output targets.** Study the combination of path geometry and reusable drawing output rather than viewing it as just an image-export helper.

- **C1:** Boolean path operations use a Bentley–Ottmann sweep with a snap-rounding tolerance to manage numerical inconsistencies. Settling a path must remove self-intersections, orient outer rings and holes, and preserve the selected filling behavior.
- **C2:** A common drawing target supports path operations, styled text, font handling, and multiple renderers. Boolean results can therefore be reused across output formats instead of being raster-only masks.

Start with [path_intersection.go](https://github.com/tdewolff/canvas/blob/master/path_intersection.go), which documents these geometric contracts and includes pooled sweep data structures. The repository candidly says its implementation is complex and test coverage remains incomplete; retain that caveat when judging suitability for production workloads.

### 18. [srwiley/rasterx](https://github.com/srwiley/rasterx)

**Go; path filling, stroking, and dashing with replaceable scan conversion.** Particularly valuable for studying stroke details that many smaller drawing libraries omit.

- **C1:** Arc joins depend on endpoint tangents, normals, and curvature radii. Miter/arc clipping, separate leading/trailing caps, explicit closure, and fixed-point approximations interact in the join logic. [stroke.go](https://github.com/srwiley/rasterx/blob/master/stroke.go) exposes these data and operations directly.
- **C2:** `Filler` and `Stroker` share a `Scanner` boundary, separating path-to-line geometry from the final antialiaser. Cap and gap callbacks also allow behavior to be extended without replacing the whole stroker.

Read the repository's Scanner-interface explanation alongside the source. Backend selection changes semantics as well as speed: the README identifies an even-odd winding limitation in the Go-vector-backed scanner. The library is therefore useful for studying how abstraction contracts can expose—or conceal—backend differences.

### 19. [golang/image](https://github.com/golang/image)

**Go; official mirror of supplementary image packages. Relevant subsystem: `vector`.** Count the monorepo once; codecs and unrelated packages are outside this entry's scope.

- **C1:** The rasterizer has fixed- and floating-point versions of the same area algorithm. Fixed-point computations can overflow at larger scales, so dimensions select the arithmetic path; the source explains the threshold's relationship to polygon-rendering tests.
- **C3:** The implementation reuses accumulation buffers, uses a one-time curve-flatness estimate to choose subdivisions, and specializes drawing for destinations such as alpha masks. The tradeoffs are documented beside the code rather than hidden behind a generic speed claim.

Start with [vector/vector.go](https://github.com/golang/image/blob/master/vector/vector.go). Its `Rasterizer.Draw` integration with Go's image interfaces is also a useful example of a small vector component fitting into a broader graphics ecosystem. Changes are managed through Go's Gerrit workflow, as identified on the repository page.

## Other language communities and drawing models

### 20. [treeform/pixie](https://github.com/treeform/pixie)

**Nim; CPU paths, images, text, paints, masking, and blending.** Study a full vector pipeline implemented within a smaller language ecosystem.

- **C1:** Path parsing handles SVG command arity and arc flags; rasterization implements nonzero and even-odd winding. Mask fills must clear pixels even when the path lies outside the image, and the source explicitly handles this case and detects a path-width overflow.
- **C3:** Segments are partitioned vertically, and two nonintersecting spanning edges enable special treatment. Pixel-aligned fills can avoid antialiasing work; coverage accumulation includes x86 and ARM SIMD paths.

The primary entry point is [paths.nim](https://github.com/treeform/pixie/blob/master/src/pixie/paths.nim), especially `partitionSegments`, `computeCoverage`, and `fillShapes`. These routines make correctness conditions for fast paths visible. The README's advertised image quality is not used as a substitute for independent conformance evidence.

### 21. [graphics32/graphics32](https://github.com/graphics32/graphics32)

**Object Pascal; Delphi/Lazarus graphics with vector polygon rasterization. Official GitHub continuation/fork of the original SourceForge project.** Focus on polygon coverage and renderer/filler abstractions rather than the entire component library.

- **C1:** [GR32_VPR.pas](https://github.com/graphics32/graphics32/blob/master/Source/GR32_VPR.pas) explains segment integration and cumulative coverage, including a limitation when oppositely oriented boundaries occupy the same pixel. It also contains explicit Free Pascal/64-bit indexing and rounding-related accommodations.
- **C2:** Span callbacks separate coverage generation from painting. [GR32_Polygons.pas](https://github.com/graphics32/graphics32/blob/master/Source/GR32_Polygons.pas) adds abstract polygon renderers, bitmap-oriented implementations, fill rules, transformations, and distinct polygon fillers.

The combination offers a useful study of numerical graphics code inside a component-oriented API. Historical copyright dates alone are not counted as C4 evidence; the entry qualifies on the implementation and abstraction criteria.

### 22. [SixLabors/ImageSharp.Drawing](https://github.com/SixLabors/ImageSharp.Drawing)

**C#; vector drawing and polygon operations integrated with ImageSharp.** Current main-branch material describes CPU and WebGPU targets behind `DrawingCanvas`; verify release availability separately if adopting those APIs.

- **C2:** The canvas records drawing intent, the batcher prepares commands, and backends create and execute retained scenes. Frame interfaces distinguish memory access from native-surface access without changing the drawing model.
- **C1:** Clip scopes must be balanced when a batch is sealed and reopened for subsequent commands. Image-processing operations are ordering barriers that must observe prior drawing, including isolated-layer contents.
- **C3:** Deferred batches amortize backend setup. Shared preparation performs dash and brush-coordinate normalization once, leaving scale-aware geometry processing to each backend.

Read the substantive [DrawingCanvas architecture document](https://github.com/SixLabors/ImageSharp.Drawing/blob/main/src/ImageSharp.Drawing/Processing/DRAWING_CANVAS.md). It explains why an immediate-looking API requires a deferred execution model and specifies the boundaries where ordering and state matter.

### 23. [Twinside/Rasterific](https://github.com/Twinside/Rasterific)

**Haskell; antialiased vector rendering on JuicyPixels, with PDF output.** The project identifies Nile/Gezira as design influences. It is useful for comparing a functional command language with the mutable contexts used elsewhere in this report.

- **C2:** [Command.hs](https://github.com/Twinside/Rasterific/blob/master/src/Graphics/Rasterific/Command.hs) records drawing using a Church-encoded free monad over `DrawCommand`. Textures, clipping, transforms, opacity, strokes, and nested drawings are values in that command language; pixel types remain parameterized.
- **C1:** [Rasterize.hs](https://github.com/Twinside/Rasterific/blob/master/src/Graphics/Rasterific/Rasterize.hs) decomposes primitives into edge samples, orders samples by position, accumulates signed coverage, and applies different mappings for winding and even-odd fills. Correct ordering and carry accumulation are essential to the resulting spans.

The same file locally uses mutable vector sorting inside `ST`, making the boundary between functional composition and controlled mutation especially clear. Current production support was not established by this research.

### 24. [bourgesl/marlin-renderer](https://github.com/bourgesl/marlin-renderer)

**Java; Java2D antialiasing rasterizer derived from OpenJDK Pisces, with substantial separate evolution and upstream integration.** Use the `jdk` branch; the repository explicitly says the older `use_Unsafe` branch has not been maintained since January 2024.

- **C1:** A thread-dedicated, reentrant renderer context owns stroking, dashing, clipping, and reusable working state. Exceptions mark it dirty and require cleanup before reuse. Read [RendererContext.java](https://github.com/bourgesl/marlin-renderer/blob/jdk/src/main/java/sun/java2d/marlin/RendererContext.java).
- **C3:** [Renderer.java](https://github.com/bourgesl/marlin-renderer/blob/jdk/src/main/java/sun/java2d/marlin/Renderer.java) exposes adaptive forward differencing, subpixel edge buckets, active-edge arrays, tile flags, and off-heap edge storage. These mechanisms address allocation and scan-conversion costs in a managed runtime.
- **C4:** The repository documents integration and backport milestones from 2015 through 2025, alongside build, unit, and integration-test workflows and distinct JDK compatibility branches.

This is an advanced implementation study: its use of JDK internals makes it a different integration proposition from a general canvas library.

### 25. [paperjs/paper.js](https://github.com/paperjs/paper.js)

**JavaScript; retained vector graphics and Bézier geometry over Canvas.** Included for its substantive geometry and scene model; pixel rasterization is supplied by browser Canvas or a Node canvas backend.

- **C1:** Boolean operations normalize paths, resolve self-crossings, split curves at intersections, propagate winding contributions, and reconstruct contours. They explicitly distinguish overlap and crossing cases. Start with [PathItem.Boolean.js](https://github.com/paperjs/paper.js/blob/develop/src/path/PathItem.Boolean.js).
- **C2:** [Item.js](https://github.com/paperjs/paper.js/blob/develop/src/item/Item.js) supplies shared hierarchy, transformation, style, event, and serialization behavior for paths, compound paths, groups, layers, and raster items. This is a reusable document model above the drawing surface.

The geometry implementation is a useful complement to rasterizer studies: an engineer can examine how operations on editable curves preserve document attributes and scene placement, while leaving final pixel generation to another layer.

## Search coverage and limitations

Discovery used twelve distinct query formulations across these angles: CPU/SIMD/JIT engines; GPU compute and hybrid rendering; SVG document engines; Go scanners and drawing targets; Nim/Pascal/C# implementations; compact C/C++ rasterizers; Rust tessellation and Skia subsets; official mirrors and historical renderers; Java/JavaScript geometry; Haskell/OCaml rendering; fixed-point embedded graphics; and a final general scanline/analytic-rasterization sweep. Later searches largely returned already covered engines, bindings, related ports, or implementations with overlapping scope. The language-focused pass added Rasterific, Marlin, and Paper.js rather than more implementations from the same CPU/GPU families.

Repository pages were opened to verify canonical locations and category fit. Additional files were retrieved through GitHub's read-only connector and read for implementation evidence; directory listings were used to locate actual files, not as substitutes for reading code. Source links use verified branches and paths. Searches sometimes surfaced obsolete owner names or layouts, so this report uses Linebender's current tiny-skia/resvg locations, ThorVG's current renderer layout, and Marlin's `jdk` sources.

Important boundaries and exclusions:

- **Cairo:** clearly relevant, but its [official source-download instructions](https://www.cairographics.org/download/) identify freedesktop-hosted source rather than a GitHub upstream. No official substantive GitHub mirror was established in this search, so an arbitrary downstream mirror is not substituted.
- **Related implementations:** Vello's renderer families and resvg's crates each count once. NanoVG/FemtoVG and Skia/tiny-skia are identified as related native implementations. LunaSVG/PlutoVG are included for different substantive layers, with the shared rasterizer dependency made explicit. Additional bindings and repetitive ports were excluded.
- **Adjacent areas:** general GPU APIs, primarily 3D rasterizers, image-processing-only libraries, application editors, and sprite/atlas layers without their own substantial vector subsystem were excluded. This is not an exhaustive inventory of GUI toolkit internals or font-only rasterizers.
- **Verification limits:** no candidate was cloned, built, benchmarked, or executed. Algorithmic mechanisms are grounded in source inspection, but correctness and performance were not independently measured. No numerical speed rankings or blanket active-maintenance claims are made. Forma's archive, official mirrors, canvas_ity's release-mirror status, and Marlin's obsolete branch are explicitly identified. C4 is used only where development history is accompanied by concrete compatibility/testing evidence.

The result is a selection guide to contrasting engineering approaches, with 25 unique repository entries, rather than a uniform endorsement of completeness, safety, licensing suitability, or maintenance capacity.
