# Font parsing and rasterization libraries

Research date: 2026-10-09.

This report selects 25 GitHub repositories implementing font-file decoding, outline processing, hinting, glyph rasterization, or closely related font validation and reconstruction. It includes reusable font subsystems in larger repositories, counted once each. Parsing-only libraries qualify without producing pixels; GPU entries must implement meaningful glyph rendering or distance-field generation rather than merely display an existing atlas. Font discovery, application-level text layout, font collections, and thin bindings are outside the main scope.

The criteria below identify engineering material worth studying, not a security certification or a claim that every component is exemplary. Statements about implementation follow the linked primary sources; judgments about what an engineer can learn are grounded in those observations. Default-branch code may be newer than a packaged release.

- **C1 — Difficult correctness:** binary-format invariants, numerical behavior, concurrency contracts, adversarial input, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components serving multiple consumers and use cases.
- **C3 — Performance with structure:** concrete approaches to allocation, computation, caching, or throughput whose architecture can be studied.
- **C4 — Sustained evolution:** changes over multiple years accompanied by compatibility work, testing, or explicit complexity management.

## General engines and compact native rasterizers

### 1. [freetype/freetype](https://github.com/freetype/freetype)

**C — Font loading, hinting, and bitmap generation. Official GitHub mirror of FreeType's freedesktop.org repository.** A strong starting point for understanding the distinction between decoding outlines, grid fitting, and calculating pixel coverage.

- **C1:** The grayscale scan converter distinguishes exact coverage for straight segments from approximate coverage for flattened Bézier curves. Its comments explain subdivision error and integer arithmetic rather than treating antialiasing as an opaque operation.
- **C2/C3:** The same converter can operate independently of the rest of FreeType and emit spans through callbacks. Its cell representation avoids an intermediate bitmap and permits direct composition into a consumer's surface. These are concrete reuse and memory-design choices. [Grayscale rasterizer implementation](https://github.com/freetype/freetype/blob/master/src/smooth/ftgrays.c).
- **C4:** The change history documents years of format expansion, malformed-input fixes, rendering compatibility, and build transitions—for example, 2021 signedness/COLR work and 2025–2026 hinting and rendering changes. It also distinguishes released versions from development changes. [Change history](https://github.com/freetype/freetype/blob/master/docs/CHANGES).

### 2. [harfbuzz/harfbuzz](https://github.com/harfbuzz/harfbuzz)

**C++ with C APIs — Font tables, outline/paint interfaces, and experimental rasterization.** The relevant subsystem is now larger than shaping: the repository explicitly identifies `libharfbuzz-raster` and `libharfbuzz-gpu` as experimental libraries. The latter encodes outlines for Slug-style GPU rendering. Hinting remains absent; the README directs hinted rendering to FreeType or Skrifa. [Component and stability map](https://github.com/harfbuzz/harfbuzz/blob/main/README.md).

- **C1:** The CPU rasterizer uses fixed-point edges, explicit winding, bounded outline/flattening work, and a shared paint-session budget. This is useful material on controlling geometric complexity as well as numerical coverage.
- **C2/C3:** Rasterization consumes the existing draw/paint abstractions, while its implementation retains scratch arrays and recycles output images. Architecture-specific SIMD paths coexist with explicit edge buckets and active-edge storage. [Rasterizer implementation](https://github.com/harfbuzz/harfbuzz/blob/main/src/hb-raster-draw.cc).

The longstanding core API's compatibility policy should not be mistaken for equal maturity of these newer experimental renderers.

### 3. [nothings/stb](https://github.com/nothings/stb)

**C/C++ — The `stb_truetype.h` subsystem of the stb collection.** Study a compact implementation that exposes file parsing, metrics, outline extraction, bitmap rasterization, atlas packing, and signed-distance glyph images in one distributable header.

- **C2:** The API separates codepoint/glyph lookup, outline access, caller-provided versus allocated bitmap storage, and batch atlas packing. Consumers can choose how much of the pipeline to use.
- **C3:** The implementation documents the coverage rasterizer replacement and its overlapping-contour tradeoff, while retaining a selectable older rasterizer. Oversampling and packing are explicit parts of the rendering interface.
- **C4:** The in-file history records substantive evolution from 2009 through 2021, including CFF/OpenType support, GPOS kerning, allocation failures, and rasterization fixes. [Implementation, API, and version history](https://github.com/nothings/stb/blob/master/stb_truetype.h).

Its own header explicitly rules out use with untrusted fonts because offsets are not range-checked. This is a study of compact integration and rendering tradeoffs, not a hardened parser recommendation.

## Rust parsing and CPU rendering architectures

### 4. [googlefonts/fontations](https://github.com/googlefonts/fontations)

**Rust — `read-fonts`, `write-fonts`, `font-types`, and Skrifa in one monorepo.** Especially useful for studying how related read-only and editable font representations can share a schema without forcing the same ownership model.

- **C1:** The design explains big-endian scalar types, offsets of different widths, versioned structures, and tables such as `loca` whose interpretation depends on other tables. `FontRead` validates a structure without recursively chasing every offset.
- **C2/C3:** Borrowed table views support allocation-free, copy-free access; owned writing types support modification and serialization. Generated table code is combined with substantial handwritten primitives and outline machinery. [Detailed code-generation and representation tour](https://github.com/googlefonts/fontations/blob/main/docs/codegen-tour.md).

The repository also documents fuzz targets and the Fauntlet comparison of Skrifa with FreeType. Those are useful validation entry points, rather than evidence that all outputs are identical. [Crate architecture and fuzzing workflow](https://github.com/googlefonts/fontations/blob/main/README.md).

### 5. [harfbuzz/ttf-parser](https://github.com/harfbuzz/ttf-parser)

**Rust with a C interface — Borrowed TrueType/OpenType/AAT parser. Maintenance mode: bug fixes only.** Its README explicitly recommends Fontations for new projects. It remains valuable for studying a small, stateless parser design. [Scope, safety contract, and maintenance policy](https://github.com/harfbuzz/ttf-parser/blob/main/README.md).

- **C1:** The documented contract addresses panics, checked arithmetic, recursive depth, and total work for graph-shaped font data. The parser primitives show why bounds must be checked before addition on 32-bit targets, and why array lengths require checked multiplication.
- **C2/C3:** `FromData`, typed offsets, streams, and lazy arrays supply common building blocks for many table parsers. Lazy arrays decode elements on access instead of materializing an owned object graph. [Binary parsing primitives](https://github.com/harfbuzz/ttf-parser/blob/main/src/parser.rs).

It does not rasterize glyphs itself; its category fit is font parsing, including use beneath several renderers in this report.

### 6. [dfrg/swash](https://github.com/dfrg/swash)

**Rust — Font introspection, shaping, scaling, hinting, and glyph images.** The interesting boundary is between immutable borrowed font data and mutable processing contexts, with layout and final application composition deliberately left to consumers. [Architecture and scope](https://github.com/dfrg/swash/blob/main/README.md).

- **C2:** A scaler can return raw or hinted outlines, embedded bitmap strikes, and layered color outlines; source-selection policies determine which representation to render. Applications can consume outlines independently of Swash's image generation.
- **C3:** `ScaleContext` owns LRU caches and scratch buffers, with one context per rasterizing thread recommended. The `_into` operations reuse caller-held results, and normalized variation coordinates can be reused from shaping and incorporated into glyph cache keys. [Scaling module and API discussion](https://github.com/dfrg/swash/blob/main/src/scale/mod.rs).

Study this when allocation ownership and integration into a larger renderer matter as much as font-format coverage.

### 7. [mooman219/fontdue](https://github.com/mooman219/fontdue)

**Rust — `no_std` font rasterization and basic layout.** Parsing is delegated to `ttf-parser`; Fontdue supplies its own rendering implementation. The README describes a ground-up rewrite following its initial `font-rs` ancestry, so this is more than another copy of that project. It also discloses limited solo-maintainer time and excludes complex shaping from its intended role. [Scope and provenance](https://github.com/mooman219/fontdue/blob/master/README.md).

- **C1:** The raster source explicitly warns that unchecked writes rely on upstream sanitization and nuanced internal invariants. Following the contract between prepared glyph geometry and the raster is a useful unsafe-code case study.
- **C3:** Separate vertical/general line paths operate on prepared geometry using vector-like numeric operations and a coverage accumulation buffer. Bitmap conversion is a separate platform operation. [Raster implementation and invariant warning](https://github.com/mooman219/fontdue/blob/master/src/raster.rs).

The repository's speed superlative is not adopted here; no comparative benchmark was independently reproduced.

### 8. [alexheretic/ab-glyph](https://github.com/alexheretic/ab-glyph)

**Rust — Glyph APIs and the separable `ab_glyph_rasterizer` crate.** Useful for comparing a focused rendering interface with larger text engines. Its documented history identifies an API rewrite of RustType, and the raster source credits earlier `font-rs` and stb algorithms.

- **C2:** Font loading, glyph scaling/positioning, and callback-based coverage delivery form a reusable interface; the coverage rasterizer independently accepts lines, quadratic curves, and cubic curves. [Glyph API guide](https://github.com/alexheretic/ab-glyph/blob/main/glyph/README.md).
- **C3:** Raster buffers can be cleared or resized while retaining allocation capacity. One-time CPU feature detection selects target-feature implementations while preserving a scalar path.
- **C1:** The same source exposes clipping, near-horizontal edges, curve subdivision, and synchronization of the selected function pointer, making numerical and concurrency assumptions inspectable. [Coverage rasterizer](https://github.com/alexheretic/ab-glyph/blob/main/rasterizer/src/raster.rs).

### 9. [yeslogic/allsorts](https://github.com/yeslogic/allsorts)

**Rust — Font parser, variable-font instancer, shaper, and subsetter extracted from Prince.** Its font parsing and serialization are independently substantial; a separate library performs final rasterization.

- **C1:** Its binary layer makes a clear safety boundary: generic reads check available bytes before using an unchecked fixed-size reader. Scoped offsets, parse errors, borrowed arrays, and owned alternatives are explicit. [Binary reader architecture](https://github.com/yeslogic/allsorts/blob/master/src/binary/read.rs).
- **C2:** Subsetting has PDF, minimal-font, and custom table profiles, plus explicit character-map targets. The code enforces glyph-selection requirements and reconstructs table order/checksums through builder types. This supports distinct output contexts rather than a single hard-coded conversion. [Subset API and builders](https://github.com/yeslogic/allsorts/blob/master/src/subset.rs).

The project README identifies reference shaping tests and the Adobe annotated-specification suite, while candidly listing missing Unicode normalization. Do not infer a complete text stack from its substantial font engine.

## Validation, reconstruction, and font engineering

### 10. [fonttools/fonttools](https://github.com/fonttools/fonttools)

**Python — Font parsing, editing, compilation, and TTX conversion.** Particularly valuable for studying tooling-oriented representations that must survive modification and serialization, not merely answer rendering queries.

- **C2/C3:** `TTFont` presents a table-oriented interface, lazy decompilation, XML round trips, selectable checksum checking, and optional bounding-box recalculation. It can preserve binary data when a table cannot be decompiled. [Core `TTFont` implementation and API](https://github.com/fonttools/fonttools/blob/main/Lib/fontTools/ttLib/ttFont.py).
- **C1/C4:** The release history connects long-term compatibility work to concrete format failures: the 2019 Python transition and empty-glyph fixes, and 2026 corrections for character-map offsets, stale CFF2 variation stores, and excessive character-map expansion. [Release notes](https://github.com/fonttools/fonttools/blob/main/NEWS.rst).

The study value lies in round-trip semantics, table dependencies, and incremental format evolution. It is not primarily a pixel rasterizer.

### 11. [khaledhosny/ots](https://github.com/khaledhosny/ots)

**C++ — OpenType Sanitizer.** A validation-and-reserialization library for OTF, TTF, WOFF, and WOFF2, with browser integration documented by the project. The build deliberately favors source integration rather than providing a shared library. [Purpose and integration model](https://github.com/khaledhosny/ots/blob/main/README.md).

- **C1:** The glyph validator checks repeated flags, coordinate byte lengths, reserved bits, and cross-table information. Its handling of incorrect bounding boxes distinguishes fonts whose hinting depends on historical quirks from fonts that can be repaired.
- **C2:** Parsing, diagnostics, repair, and output serialization are organized around font tables. The `glyf` implementation constructs output slices and replacement data, showing how a reusable sanitizer can retain acceptable data while rewriting particular fields. [Glyph validation and repair](https://github.com/khaledhosny/ots/blob/main/src/glyf.cc).

This is a particularly relevant complement to permissive readers: rejection and repair policies are visible engineering decisions.

### 12. [google/woff2](https://github.com/google/woff2)

**C++ — WOFF2 reference compression and reconstruction library.** Its substantive font work is reversing transformed font tables and rebuilding SFNT structures, beyond simply invoking Brotli.

- **C1:** The decoder handles variable-length point encodings, checked coordinate accumulation, output bounds, table checksums, and collection metadata. Shared tables and reconstructed glyph-location data introduce inter-table invariants. [WOFF2 decoder](https://github.com/google/woff2/blob/master/src/woff2_dec.cc).
- **C2:** `WOFF2Out` supports both appending and writing at earlier offsets, allowing table headers and checksums to be patched after reconstruction. Fixed-memory and expanding-string implementations let consumers control output storage and size limits. [Output abstraction](https://github.com/google/woff2/blob/master/include/woff2/output.h).

The README contains old provisional-format wording; the inspected decoder and public output API provide the stronger evidence for its implemented behavior.

## JavaScript font engines

### 13. [opentypejs/opentype.js](https://github.com/opentypejs/opentype.js)

**JavaScript — Browser/Node font parsing, writing, outlines, and hinting.** A useful comparison with native engines because JavaScript's numeric model directly affects its implementation choices.

- **C1:** The TrueType interpreter documents its use of floating-point arithmetic instead of exactly reproducing all 26.6 fixed-point operations. It separately limits instructions, call depth, and loops; cached font/preparation state and error states govern recovery. [Hinting interpreter](https://github.com/opentypejs/opentype.js/blob/master/src/hintingtt.mjs).
- **C2:** The public model supports loading existing fonts, creating glyph paths and fonts, and writing them back. Those abstractions serve inspection, editing, and drawing applications. WOFF2 decompression is explicitly a separate prerequisite. [Usage and font-construction guide](https://github.com/opentypejs/opentype.js/blob/master/README.md).

The interpreter itself lists incomplete instructions and transform limitations; numerical equivalence with FreeType should not be assumed.

### 14. [foliojs/fontkit](https://github.com/foliojs/fontkit)

**JavaScript — Multi-format font engine used by PDFKit.** Study how one font object coordinates table access, glyph classes, variation processing, layout, and subsets.

- **C2:** The public API supports font collections, vector glyph paths, color glyphs, layout runs, and subset creation. This makes the same parser useful for document production and graphical applications. [Font and subset APIs](https://github.com/foliojs/fontkit/blob/master/README.md).
- **C3:** `TTFFont` installs lazy property accessors for available tables, caches decoded tables and glyphs, and dispatches to separate outline/color glyph implementations. The architecture localizes expensive decoding while keeping a uniform higher-level model. [SFNT font implementation](https://github.com/foliojs/fontkit/blob/master/src/TTFFont.js).

Its table-decode error handling is also worth examining: failures can be logged and represented by a missing result rather than immediately terminating every operation.

### 15. [photopea/Typr.js](https://github.com/photopea/Typr.js)

**JavaScript — Procedural parser and outline utilities used by Photopea.** This offers a contrasting architecture to Fontkit: plain table-shaped objects and static functions, with parser and utility files separated. [Architecture and API guide](https://github.com/photopea/Typr.js/blob/gh-pages/README.md).

- **C1:** Its glyph decoder handles repeated flags, delta-encoded coordinates, composite glyph references, and alternative component transforms. These are meaningful format semantics even though the code is not presented as a hardened validator.
- **C2/C3:** The table-dispatch structure is easy to trace, and the `glyf` table initially creates empty slots so individual glyph data can be decoded later. The parser/utility split permits consumers to extract outlines without adopting every rendering utility. [Table and glyph parsing implementation](https://github.com/photopea/Typr.js/blob/gh-pages/src/Typr.js).

Activity note: [GitHub metadata](https://api.github.com/repos/photopea/Typr.js) reported its latest repository push in August 2025 at research time. The README's comparative speed and size claims were not independently verified and are not selection evidence here.

## Go libraries

### 16. [golang/image](https://github.com/golang/image)

**Go — `font/sfnt`, `font/opentype`, and their vector-rasterizer integration. Official mirror of Go's supplementary image repository.** Counted only once; the relevant code is the font pipeline rather than unrelated image codecs.

- **C1:** `sfnt.Font` retains access to its input and documents immutability/lifetime requirements. Concurrent calls require separate scratch buffers. The implementation also bounds compound-glyph depth, stack size, table sizes, and subroutine counts. [SFNT decoder and contracts](https://github.com/golang/image/blob/master/font/sfnt/sfnt.go).
- **C2/C3:** The low-level outline decoder feeds an `opentype.Face` implementing the common `font.Face` interface. Each face owns reusable rasterizer, mask, and buffer state; careful call ordering prevents reused buffers from invalidating outlines prematurely. [Rasterizing face implementation](https://github.com/golang/image/blob/master/font/opentype/opentype.go).

Both packages explicitly state that they are not hardened against malicious inputs. The mutable `Face` is not safe for concurrent use.

### 17. [go-text/typesetting](https://github.com/go-text/typesetting)

**Go — The `font` and `font/opentype` parsing subsystems within a typesetting stack.** A substantive parser selection, not an entry based only on its shaping or line layout. [Font subsystem boundaries](https://github.com/go-text/typesetting/blob/main/font/README.md).

- **C1:** `NewFont` treats invalid mandatory tables differently from optional tables, documenting its tolerance policy. Immutable `Font` objects are safe for concurrent access, while mutable `Face` objects are not.
- **C2/C3:** Low-level table access feeds a higher-level font model used by renderers and shapers. A face caches character mapping, glyph extents, and advances; changing variation coordinates invalidates affected caches, and changing pixel size invalidates extents. [Font loading, face state, and cache invalidation](https://github.com/go-text/typesetting/blob/main/font/font.go).

This is useful for studying both the cost of repeated font queries and the correctness obligations introduced by variable-font caches. The project documents an evolving pre-1.0 API rather than promising frozen interfaces.

### 18. [seehuhn/go-sfnt](https://github.com/seehuhn/go-sfnt)

**Go — TrueType/OpenType reading, writing, variation handling, and subsetting.** A less prominent but substantial alternative oriented toward editable font data.

- **C1:** Parsing accepts an explicit memory budget and passes it to table readers. The main reader distinguishes absent and malformed tables and reconciles information from multiple tables. [Reader and budget plumbing](https://github.com/seehuhn/go-sfnt/blob/main/read.go).
- **C2:** Per-table packages and the read/write/subset model support conversion and font production as well as inspection. The inspected subset tests encode and re-read GSUB/GPOS data, comparing representations after glyph remapping—a concrete example of protecting the interface between editing and serialization. [Subset round-trip tests](https://github.com/seehuhn/go-sfnt/blob/main/subset_roundtrip_test.go).

The budget mechanism is evidence of resource-control design, not a claim that every allocation path has been independently audited.

## Managed and functional-language implementations

### 19. [SixLabors/Fonts](https://github.com/SixLabors/Fonts)

**C#/.NET — Font loading, outline/metrics access, hinting, and text layout.** Included for its own font machinery; final image rendering can be supplied by a consumer such as ImageSharp.Drawing. The repository uses the Six Labors Split License, which should not be conflated with the permissive licenses of several other entries.

- **C1:** The TrueType interpreter explicitly models preparation state, per-glyph working CVT data, copy-on-write storage, and different hinting modes. Its comments connect mode selection and preparation caching to FreeType v40/v35 compatibility behavior. [Interpreter state and compatibility semantics](https://github.com/SixLabors/Fonts/blob/main/src/SixLabors.Fonts/Tables/TrueType/Hinting/TrueTypeInterpreter.cs).
- **C2/C3:** `FontReader` separates table headers, format-specific WOFF/WOFF2 handling, table loaders, and a cache keyed by table type. Owned decompression streams have explicit disposal handling. [Reader implementation](https://github.com/SixLabors/Fonts/blob/main/src/SixLabors.Fonts/FontReader.cs).

The compatibility statements describe the project's intended semantics; this research did not run differential rendering tests.

### 20. [LayoutFarm/Typography](https://github.com/LayoutFarm/Typography)

**C# — `Typography.OpenFont` parser with separately organized glyph-layout and rendering integration. Historical/low-activity selection.** [GitHub metadata](https://api.github.com/repos/LayoutFarm/Typography) reported the latest repository push as September 2023; the code is retained for architectural study without implying current maintenance.

- **C1:** The TrueType glyph loader uses the location table to distinguish empty and nonempty glyphs, decodes simple glyphs first, and defers composite resolution. Following component transforms and shared outline data exposes the format's nonlocal dependencies. [Glyph loader](https://github.com/LayoutFarm/Typography/blob/master/Typography.OpenFont/Tables.TrueType/Glyf.cs).
- **C2:** The README explains why the independent OpenFont core, higher-level GlyphLayout module, and PixelFarm rendering integration are separate. It explicitly states that the first two do not themselves rasterize. [Module architecture and limitations](https://github.com/LayoutFarm/Typography/blob/master/README.md).

This is a substantial C# implementation with acknowledged code ancestry, not a wrapper around a native font engine.

### 21. [apache/pdfbox](https://github.com/apache/pdfbox)

**Java — The FontBox subproject. Official Apache PDFBox GitHub mirror.** Counted once for its reusable font library, not for the PDF renderer as a whole. [FontBox subsystem description](https://github.com/apache/pdfbox/blob/trunk/fontbox/README.txt).

- **C1:** `TTFParser` distinguishes embedded PDF fonts from standalone fonts when deciding which tables are mandatory. It checks table extents against available data and can skip an invalid optional table, while rejecting missing required structures. This illustrates compatibility-driven parsing rather than one universal strictness policy.
- **C2/C3:** Table objects and random-access streams support full font parsing and a separate header-only path. The latter reads selected naming/metadata information instead of requiring every glyph-related operation. [TrueType parser](https://github.com/apache/pdfbox/blob/trunk/fontbox/src/main/java/org/apache/fontbox/ttf/TTFParser.java).

The FontBox README's old build requirements are not treated as current instructions; the parser source is the technical entry point.

### 22. [gfngfn/otfed](https://github.com/gfngfn/otfed)

**OCaml — OpenType encoder, decoder, and subsetter.** A useful functional-language counterpoint, developed as a reformulation of Otfm rather than a generated binding.

- **C1:** The decoding core threads position/source state through result-returning operations. Offset, length, and end-of-input errors are represented explicitly; multi-byte integers and timestamps are reconstructed with dedicated numeric handling. [Decoding primitives](https://github.com/gfngfn/otfed/blob/master/src/decodeOperationCore.ml).
- **C2:** The public interface separates font values from encoding/decoding operations and exposes glyph IDs, mappings, bounding boxes, and quadratic/cubic paths. It even documents rounding loss when converting curve representations. [Public font model and interfaces](https://github.com/gfngfn/otfed/blob/master/src/otfed.mli).

The repository's development-status matrix differentiates supported, automatically tested, lightly tested, and unsupported table operations. Coverage is selective; this should not be read as a fully interchangeable replacement for a general font engine.

## Distance fields and GPU glyph rendering

### 23. [Chlumsky/msdfgen](https://github.com/Chlumsky/msdfgen)

**C++ — Multi-channel signed-distance-field generation for glyphs and vector shapes.** FreeType supplies font loading in the extensions; the substantive independent implementation is geometric distance-field generation, not parsing.

- **C1:** Edge types handle line, quadratic, and cubic geometry, distance minimization, endpoint directions, and degenerate curves. These numerical details explain why a font distance field is more complex than sampling an ordinary bitmap. [Edge geometry implementation](https://github.com/Chlumsky/msdfgen/blob/master/core/edge-segments.cpp).
- **C2:** A dependency-light geometry core is separate from font/SVG/image I/O, allowing callers to supply shapes directly as well as load glyphs.
- **C4:** The changelog records multiple years of precision and error-correction changes, compatibility-preserving coordinate-scaling options, and retained old option names. These show active management of rendering semantics and API evolution. [Change history](https://github.com/Chlumsky/msdfgen/blob/master/CHANGELOG.md).

### 24. [nyyManni/msdfgl](https://github.com/nyyManni/msdfgl)

**C and GLSL — GPU implementation of multi-channel distance-field generation. Historical/low-activity selection.** The project states that this was written from scratch, adapting the algorithm to constant shader workspace and eliminating pointer-based structures; it is therefore distinct from an msdfgen wrapper. [Architecture and limitations](https://github.com/nyyManni/msdfgl/blob/master/README.md).

- **C1:** The fragment shader implements signed distances, contour winding, channel selection, and handling of degenerate contours. Its fixed workspace makes the representation constraints visible. [Generation shader](https://github.com/nyyManni/msdfgl/blob/master/src/msdf_fragment.glsl).
- **C3:** The CPU/GPU split moves per-pixel work into shaders. Separate atlas and index textures grow as glyphs are introduced, while batch generation amortizes uploads and binding changes.

Important limits are explicit: cubic segments are unsupported, and the README lists remaining winding/edge-coloring work. [GitHub metadata](https://api.github.com/repos/nyyManni/msdfgl) reported the latest repository push in October 2024. Its old benchmark setup is not evidence of present-day hardware performance.

### 25. [hypernewbie/VEFontCache](https://github.com/hypernewbie/VEFontCache)

**C++ and shader examples — Runtime glyph rasterization and caching for game engines.** Font parsing relies on stb, but the repository adds its own substantive GPU rendering, atlas management, and draw-command architecture.

- **C2:** The library returns draw lists with vertices, indices, and rendering passes, leaving execution to the graphics backend. The header gives a concrete integration contract and includes optional HarfBuzz shaping and FreeType rasterization paths. [Header, data structures, and integration contract](https://github.com/hypernewbie/VEFontCache/blob/main/ve_fontcache.h).
- **C3:** The documented GPU path tessellates curves, uses XOR blending and supersampling, then downsamples into a regioned atlas. Fixed-size cache slots trade packing density for straightforward LRU replacement; batched glyph updates are explicit data structures. [Rendering and cache design](https://github.com/hypernewbie/VEFontCache/blob/main/README.md).

This is useful for studying the whole cost of dynamic text in an engine, including cache misses and render-pass coordination, rather than only the glyph-generation algorithm.

## Coverage and search notes

Discovery used more than twenty live search formulations: native TrueType rasterizers; Rust zero-allocation parsers and scalers; JavaScript OpenType/WOFF engines; Java and C# font implementations; Go SFNT readers and typesetting cores; sanitizers and WOFF2 reconstruction; GPU coverage/MSDF rendering; and OCaml, Haskell, embedded, BDF, and PCF alternatives. Later comparison queries increasingly returned the same engines, bindings, small experiments, and forks. The final selection balances architecture and implementation depth rather than attempting to enumerate every font-related repository.

Every selected canonical GitHub URL was verified through repository metadata or an opened repository page. Primary README/API material and at least one separate implementation or design source were inspected for every entry. None of the selected repositories was marked archived by GitHub at research time. FreeType, Go image, and PDFBox are explicitly identified as mirrors; low-activity projects and `ttf-parser`'s maintenance-only status are identified individually. Push dates are activity observations, not evidence for C4.

Thin FreeType/stb bindings, font catalogs, font discovery libraries, bitmap-only display helpers, application text-layout stacks without a substantial relevant subsystem, and tutorial-sized parsers were excluded. Additional JavaScript ports and `font-rs`/RustType descendants were not counted merely to repeat shared implementations; Fontdue, ab-glyph, and MSDFGL were retained for their documented separate implementations or significant redesigns. General vector renderers such as Pathfinder were not needed to establish GPU coverage, given the more directly font-focused selections. The bitmap/embedded and Haskell searches did not receive the same implementation depth as the retained OpenType-oriented projects; those ecosystems are not claimed to be exhaustively represented.

No candidate code was executed, dependencies installed, benchmarks reproduced, or repositories cloned. Test and fuzzing claims describe inspected project material, not successful test runs in this research session. Default-branch source, documentation, and repository metadata establish the evidence; inclusion remains a selection judgment rather than an assurance of complete format support, safety, or uniform code quality.
