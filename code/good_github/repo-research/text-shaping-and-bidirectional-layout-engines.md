# Text shaping and bidirectional layout engines

Research date: **2026-10-09**.

This selection covers **23 GitHub repositories** implementing glyph shaping, the Unicode Bidirectional Algorithm, or substantial paragraph-layout machinery that integrates them. It includes small libraries and explicitly identified subsystems of larger repositories. Shaping selects and positions glyphs within runs; bidi analysis resolves direction and visual ordering; paragraph engines coordinate those operations with fonts, wrapping, styles, and interaction. A library need not implement all three to belong here.

Canonical repository identities and archive/mirror metadata were checked through GitHub; linked implementation, documentation, and test material was read. Descriptions concern the inspected default branches, which can differ from published packages. Criteria are engineering-study judgments grounded in the cited evidence, not certifications of correctness or uniform code quality. No candidate code was executed and no performance claims were independently benchmarked.

**Criteria legend:** **C1** — difficult correctness involving invariants, input handling, concurrency, numerical semantics, or failure modes. **C2** — substantial reusable abstractions serving different callers or use cases. **C3** — concrete performance constraints addressed through understandable architecture. **C4** — sustained evolution accompanied by compatibility, testing, or complexity management.

## Glyph-shaping engines

### 1. [harfbuzz/harfbuzz](https://github.com/harfbuzz/harfbuzz)

**C++ with a C API — OpenType and Apple Advanced Typography shaping.** Study how a general shaping pipeline accommodates script-specific decisions and incompatible font conventions without exposing those details to every caller.

- **C1:** The shaping planner decides whether glyph classes, substitutions, positioning, and kerning come from OpenType tables, AAT tables, or fallbacks. Its comments document exceptions such as avoiding mark-position adjustments for particular AAT emoji behavior. These are concrete compatibility constraints, not simply a character-to-glyph lookup. [Shaping planner and pipeline](https://github.com/harfbuzz/harfbuzz/blob/main/src/hb-ot-shape.cc).
- **C2:** Reusable plans, feature maps, font objects, and text buffers separate font-dependent preparation from per-buffer substitution and positioning. The same pipeline selects script-specific shapers and horizontal or vertical features. [Implementation](https://github.com/harfbuzz/harfbuzz/blob/main/src/hb-ot-shape.cc).
- **C4:** The release history documents changes from 2020 through 2026 involving USE specifications, matching platform shaping behavior, work limits, malformed-font handling, fuzzing, and numerical overflow fixes. It is particularly useful for studying how preserving output behavior interacts with robustness improvements. [NEWS](https://github.com/harfbuzz/harfbuzz/blob/main/NEWS).

### 2. [harfbuzz/harfrust](https://github.com/harfbuzz/harfrust)

**Rust — a substantive Rust implementation of HarfBuzz shaping.** This began as a RustyBuzz fork but replaced the font-parsing backend with `read-fonts` and evolved separately. RustyBuzz is therefore not counted as an additional entry. The repository documents the lineage and the division of work with Fontations.

- **C1:** Explicit cluster policies distinguish preserving grapheme groups from preserving monotonic source order. Buffer flags also express boundary context and whether concatenating shaped output is safe; the library forbids unsafe Rust in its own implementation. [Public types and contracts](https://github.com/harfbuzz/harfrust/blob/main/harfrust/src/lib.rs).
- **C2:** `Font`, `ShaperFont`, `ShapePlan`, `Buffer`, and shaping options expose separate font, planning, and mutable-output responsibilities, making the port useful independently of a renderer. [API implementation](https://github.com/harfbuzz/harfrust/blob/main/harfrust/src/lib.rs).

The project documents a reproducible comparison with HarfBuzz using the same shaping tests and benchmark inputs. It also records known Arabic fallback differences, rather than claiming universal equivalence. [Correctness and performance comparison guide](https://github.com/harfbuzz/harfrust/blob/main/HARFBUZZ.md).

### 3. [yeslogic/allsorts](https://github.com/yeslogic/allsorts)

**Rust — font parsing, OpenType shaping, and subsetting, extracted from Prince.** An independent design worth comparing with the HarfBuzz family, especially for document production and preserving application metadata through substitutions.

- **C1:** GSUB processing accounts for mark filtering, contextual and reverse-context substitutions, variation-dependent features, recursion limits, and limits on glyph expansion. Ligature formation preserves contributing Unicode characters and updates component positions needed by subsequent processing. [GSUB implementation](https://github.com/yeslogic/allsorts/blob/master/src/gsub.rs).
- **C2:** `RawGlyph<T>` carries caller data through shaping, and `GlyphData::merge` defines what happens to that data when multiple glyphs become a ligature. This is a useful abstraction for retaining source and styling information while the glyph sequence changes. [Generic glyph representation](https://github.com/yeslogic/allsorts/blob/master/src/gsub.rs).

The repository explains its shaping-specification work and use of HarfBuzz output and Adobe's test suite. Its documented limits include no Unicode normalization and no font lookup/matching; applications must supply those layers. [Scope, tests, and limitations](https://github.com/yeslogic/allsorts#readme).

### 4. [dfrg/swash](https://github.com/dfrg/swash)

**Rust — font inspection, complex shaping, and glyph rendering.** Particularly instructive for separating borrowed font data from caches and for designing the handoff between a shaper and a higher-level layout engine.

- **C1:** The shaping documentation states a crucial ordering contract: output remains in logical order, and RTL reordering must reverse clusters while preserving glyph order inside each cluster for mark positioning. Character clusters retain composed/decomposed alternatives for font selection. [Shaping module](https://github.com/dfrg/swash/blob/main/src/shape/mod.rs).
- **C2:** Callers may feed strings or individual clusters with source ranges, user data, and boundary analysis. This permits custom font fallback and styled-text storage without requiring Swash to own the application's text model. [Cluster input/output guide](https://github.com/dfrg/swash/blob/main/src/shape/mod.rs).
- **C3:** `ShapeContext` owns LRU caches and scratch buffers. The documentation recommends persistent contexts, one per layout thread, to amortize allocations and reduce heap contention. The architecture makes the performance policy visible to callers. [Context design](https://github.com/dfrg/swash/blob/main/src/shape/mod.rs).

Itemization and full paragraph bidi layout remain outside this shaper's contract.

### 5. [silnrsi/graphite](https://github.com/silnrsi/graphite)

**C++ with a C API — Graphite smart-font execution engine.** This provides a different architectural family: fonts carry compiled rules for complex writing-system behavior, including minority-language conventions, instead of relying only on a fixed set of script shapers.

- **C1:** Pass loading validates table lengths, state counts, context bounds, rule references, bytecode status, and constraint immutability. An engineer can trace how externally supplied font programs become executable shaping rules. [Pass parser and executor](https://github.com/silnrsi/graphite/blob/master/src/Pass.cpp).
- **C2:** Faces, segments, passes, finite-state tables, constraints, and actions form a reusable rule-execution model. The pass implementation connects that model to collision and kerning behavior. [Implementation](https://github.com/silnrsi/graphite/blob/master/src/Pass.cpp).
- **C3:** Rule code is allocated in pools, and finite-state transitions organize rule selection; the changelog also records memory-footprint work and the removal of the old segment-cache design. [Pass storage](https://github.com/silnrsi/graphite/blob/master/src/Pass.cpp), [ChangeLog](https://github.com/silnrsi/graphite/blob/master/ChangeLog).

**Boundary:** the changelog says full bidi processing was removed in 1.3.2; segments are assumed to have one direction. Retain this for shaping and font-program execution, not as a complete paragraph bidi engine.

### 6. [Tehreer/SheenFigure](https://github.com/Tehreer/SheenFigure)

**C — a compact OpenType shaping implementation with Arabic-specific support.** A focused, lower-activity study candidate: GitHub metadata showed its last push in November 2023, and it was not marked archived. The README explicitly limits script coverage to Arabic and a subset of OpenType layout facilities.

- **C1:** Arabic joining is implemented with feature masks for isolated, initial, medial, and final forms while skipping transparent characters. Feature scheduling applies `rclt` and `calt` together to avoid duplicate lookup application, an unusually concrete compatibility detail. [Arabic engine](https://github.com/Tehreer/SheenFigure/blob/master/Source/ArabicEngine.c).
- **C2:** Script knowledge consists of ordered substitution and positioning feature descriptions, while a shared text processor performs glyph discovery, substitution, positioning, and finalization. This makes the script-policy/lookup-mechanism split easy to study. [Engine implementation](https://github.com/Tehreer/SheenFigure/blob/master/Source/ArabicEngine.c), [source organization](https://github.com/Tehreer/SheenFigure/tree/master/Source).

The narrow coverage is an explicit limit, not evidence that it can replace a general-purpose shaper.

### 7. [foliojs/fontkit](https://github.com/foliojs/fontkit)

**JavaScript — font engine for Node and browsers with its own OpenType/AAT layout machinery.** Useful for studying shaping integrated with font inspection and PDF-oriented glyph access, without reducing the project to a native-library binding.

- **C1:** The layout engine selects AAT or OpenType processing, then handles Unicode mark-position fallback, legacy kerning only when needed, and default-ignorable characters with zero advances. Correctness depends on composing these fallbacks without applying an adjustment twice. [LayoutEngine.js](https://github.com/foliojs/fontkit/blob/master/src/layout/LayoutEngine.js).
- **C2:** A `GlyphRun` carries glyphs, feature settings, script, language, direction, and positions through interchangeable layout engines. The same interface accepts text or an existing glyph sequence and supports feature queries. [Pipeline implementation](https://github.com/foliojs/fontkit/blob/master/src/layout/LayoutEngine.js).

The [repository API guide](https://github.com/foliojs/fontkit#readme) connects shaping to metrics, outlines, and subsetting. This entry concerns font/run shaping; a run direction parameter alone should not be read as a complete mixed-direction paragraph-layout API.

### 8. [LayoutFarm/Typography](https://github.com/LayoutFarm/Typography)

**C# — managed font reader and glyph-layout engine.** The relevant subsystems are `Typography.OpenFont` and `Typography.GlyphLayout`, counted together. This is a historical/low-activity comparison point: the checked repository was not archived, but its last push was in September 2023, and its README calls the glyph-layout engine unstable.

- **C2:** The project separates font parsing and OpenType lookup machinery from a convenient glyph-layout facade and from rendering. `UnscaledGlyphPlan`, plan sequences, and an output-list interface expose glyph IDs, source offsets, advances, and placement without choosing a graphics backend. [GlyphLayout.cs](https://github.com/LayoutFarm/Typography/blob/master/Typography.GlyphLayout/GlyphLayout.cs), [module roles](https://github.com/LayoutFarm/Typography#readme).
- **C3:** Layout preparation caches GSUB/GPOS plan contexts using typeface and script/language information; input glyph and positioning buffers are reused. The code makes the lifetime of reusable work visible and offers a concrete comparison with Rust and native shaper caches. [Plan collection and layout state](https://github.com/LayoutFarm/Typography/blob/master/Typography.GlyphLayout/GlyphLayout.cs).

These are study-worthy design choices, not a claim that its caching or script coverage has been independently validated.

## Bidirectional algorithm libraries

### 9. [fribidi/fribidi](https://github.com/fribidi/fribidi)

**C — GNU FriBidi, a standalone Unicode bidi implementation.** A useful native baseline for tracing UAX #9 through run-based data structures and then integrating its results with another shaper.

- **C1:** The implementation maintains run links, isolate links, levels, and bracket-pair relationships while merging compatible runs. Comments identify a dangling-pointer edge case discovered by fuzzing and explain why bracket runs must not be merged indiscriminately. [Bidi implementation](https://github.com/fribidi/fribidi/blob/master/lib/fribidi-bidi.c).
- **C2:** The API separates type classification, paragraph embedding levels, and line reordering. Its convenience function can return both logical-to-visual and visual-to-logical maps and embedding levels, with unwanted outputs omitted. [API description](https://github.com/fribidi/fribidi#readme).
- **C3:** Bracket pairs use a growable flat array instead of individually allocated list nodes; runs are pool-owned, and isolate links shortcut adjacent-run searches. Those choices are explained beside their implementation. [Storage and traversal](https://github.com/fribidi/fribidi/blob/master/lib/fribidi-bidi.c).

Its core representation is UTF-32; encoding conversion is a separate concern.

### 10. [Tehreer/SheenBidi](https://github.com/Tehreer/SheenBidi)

**C, with C++ tests — object-oriented bidi processing through a C API.** Study the explicit hierarchy from encoded text to algorithms, paragraphs, lines, visual runs, and mirror/script locators.

- **C1:** Isolating-run processing temporarily reconnects level-run links, resolves weak and neutral types, and restores the original topology. That exposes the state invariants behind UAX #9's isolating sequences. [IsolatingRun.c](https://github.com/Tehreer/SheenBidi/blob/master/Source/UBA/IsolatingRun.c).
- **C2:** The [API overview](https://github.com/Tehreer/SheenBidi#readme) separates paragraph resolution from line reordering and returns runs rather than only a transformed string. UTF-8, UTF-16, and UTF-32 support and separate mirror/script locators make it useful to different layout stacks.

The [algorithm tests](https://github.com/Tehreer/SheenBidi/blob/master/Tests/AlgorithmTests.cpp) load Unicode bidi and mirroring data and check paragraph levels, run bounds, visual order, and mirrors. This is a strong entry point for studying how a run-based API is checked against character-based expected results; test presence is not a claim that this research ran them.

### 11. [servo/unicode-bidi](https://github.com/servo/unicode-bidi)

**Rust — standalone bidi analysis with UTF-8 and UTF-16 interfaces.** Especially useful for studying how one algorithm supports different code-unit index spaces without confusing byte offsets, characters, and visual runs.

- **C1:** The implementation documents code-unit indexing and surrogate handling. Its conformance tests assert an internal invariant between `visual_runs` and `reorder_visual`, and verify that UTF-8 and UTF-16 APIs produce the same per-character levels. [Implementation/API](https://github.com/servo/unicode-bidi/blob/main/src/lib.rs), [conformance tests](https://github.com/servo/unicode-bidi/blob/main/tests/conformance_tests.rs).
- **C2:** Paragraph information, resolved levels, visual runs, and reordering maps are independently useful outputs. A `BidiDataSource` abstraction permits custom Unicode property data, and feature selection supports `no_std` plus allocation. [Public architecture](https://github.com/servo/unicode-bidi/blob/main/src/lib.rs).

The line API deliberately sits after application wrapping. Its documented visual-run operation does not itself perform every glyph-level responsibility, such as mirroring and combining-mark treatment; the caller still needs a shaping/layout strategy.

### 12. [lojjic/bidi-js](https://github.com/lojjic/bidi-js)

**JavaScript — dependency-free UBA implementation targeting Unicode 13.0.0.** A relatively small, substantive algorithm implementation for browser and Node environments; the declared Unicode version is a material limit.

- **C1:** Explicit-level processing tracks separate isolate and embedding overflow counters and an explicit depth bound. Later phases resolve brackets and directional types. The test harness compares expected levels and reordered indices, rather than only rendered strings. [Embedding-level implementation](https://github.com/lojjic/bidi-js/blob/main/src/embeddingLevels.js), [character conformance harness](https://github.com/lojjic/bidi-js/blob/main/test/BidiCharacterTest.js).
- **C2:** The API exposes embedding levels, paragraph boundaries, reversal segments, and mirrored-character mappings independently. Per-line ranges support integration with an application's wrapping. The self-contained factory is intentionally usable in worker-based environments. [API rationale](https://github.com/lojjic/bidi-js#readme).

The project reports conformance to its stated version; this report does not extrapolate that claim to newer Unicode data or independently certify it.

### 13. [unicode-org/icu](https://github.com/unicode-org/icu)

**C/C++ and Java — ICU's bidi subsystem, counted once within the monorepo.** The inspected entry points are ICU4C's `ubidi` implementation and C API. This belongs for its actual bidi engine, not for ICU's unrelated internationalization facilities.

- **C1:** Implementation notes explain how surrogate halves receive intermediate directional properties, why naively assigning the same property to both halves breaks weak-type resolution, and how final levels are repaired. They also discuss retaining boundary-neutral characters while virtually ignoring them. [ubidi.cpp](https://github.com/unicode-org/icu/blob/main/icu4c/source/common/ubidi.cpp).
- **C2:** Paragraph/line objects, run access, maps, and explicit error propagation support renderers and storage-layout applications. The API's worked example intersects style runs with direction runs while keeping input text logical. [ubidi.h](https://github.com/unicode-org/icu/blob/main/icu4c/source/common/unicode/ubidi.h).
- **C3:** Directional-property bitmasks skip unnecessary phases for common paragraphs; weak-type, neutral, and implicit-level work is combined in a documented loop. [Optimization rationale](https://github.com/unicode-org/icu/blob/main/icu4c/source/common/ubidi.cpp).

ICU bidi and Arabic character shaping should not be confused with a general OpenType glyph shaper.

### 14. [MeirKriheli/python-bidi](https://github.com/MeirKriheli/python-bidi)

**Python with a Rust extension — independent historical Python bidi engine plus a modern Rust-backed path.** Retained specifically for the Python implementation and the compatibility boundary; its Rust wrapper is not counted as another independent algorithm.

- **C1:** The Python code decomposes processing into base-level detection, explicit embeddings/overrides, weak and neutral resolution, implicit levels, reordering, and mirroring. Mutable per-character records preserve original types while later phases update resolved types and levels. [algorithm.py](https://github.com/MeirKriheli/python-bidi/blob/master/bidi/algorithm.py).
- **C2:** A common display-conversion interface accommodates text or encoded bytes, base-direction overrides, and debugging. The project preserves a distinct import path for the older Python engine while exposing the Rust implementation separately. Its changelog records restoring old imports/behavior after the backend transition and adding free-threaded concurrency tests. [Compatibility history](https://github.com/MeirKriheli/python-bidi/blob/master/CHANGELOG.rst).

**Boundary:** the [README](https://github.com/MeirKriheli/python-bidi#readme) labels the Python engine as version 5 of the algorithm and distinguishes it from the Rust path. Study it as an inspectable older implementation, not as evidence of current UBA coverage.

## Paragraph layout and shaping integration

### 15. [HOST-Oman/libraqm](https://github.com/HOST-Oman/libraqm)

**C — Raqm, a compact integration layer for complex text layout.** It combines HarfBuzz, FreeType, and either FriBidi or SheenBidi. Its own itemization, state management, and index conversion make it more substantive than a generated binding.

- **C1:** The implementation translates glyph clusters back from internal UTF-32 positions to UTF-8 or UTF-16 input indices, retains the supplying font per glyph, checks missing font assignments, and rejects input containing paragraph separators. [raqm.c](https://github.com/HOST-Oman/libraqm/blob/main/src/raqm.c).
- **C2:** A single state object collects text, direction, language, font ranges, and features, then exposes positioned glyphs through a renderer-independent API. Script itemization and bidi handling are coordinated before shaping, sparing each consumer from reconstructing that pipeline. [API and implementation](https://github.com/HOST-Oman/libraqm/blob/main/src/raqm.c), [component boundaries](https://github.com/HOST-Oman/libraqm#readme).

The inspected implementation is a single-paragraph shaping/layout layer, not a general multi-line document formatter. It is a useful starting point for understanding the minimum integration work above a glyph shaper.

### 16. [GNOME/pango](https://github.com/GNOME/pango)

**C — internationalized text layout; official read-only GitHub mirror of GNOME GitLab.** Study the `PangoLayout` subsystem and its relationship to itemization, shaping, font backends, and application-facing text interaction.

- **C2:** `PangoLayout` turns UTF-8 text and attributes into paragraph lines with wrapping, justification, alignment, ellipsization, and logical-position/physical-position conversion. It sits above lower-level itemization and shaping APIs and supports multiple font/rendering backends. [Layout implementation and API documentation](https://github.com/GNOME/pango/blob/main/pango/pango-layout.c).
- **C3:** Extents caching explicitly records when line/run structures have escaped to a caller who could mutate them; caching is disabled in that case. This is an instructive interaction between an established public API and performance correctness. [Cache-state explanation](https://github.com/GNOME/pango/blob/main/pango/pango-layout.c).
- **C4:** The 2022–2026 history includes mixed-direction ligature-caret fixes, RTL paragraph navigation, thread-safety fixes, font-lifetime changes, platform updates, and deliberate deprecations. [NEWS](https://github.com/GNOME/pango/blob/main/NEWS).

The GitHub repository is a substantive source mirror; upstream development is hosted at the GitLab URL identified on its repository page.

### 17. [pop-os/cosmic-text](https://github.com/pop-os/cosmic-text)

**Rust — multi-line text handling, editing, custom bidi-aware layout, and font fallback.** The current README identifies HarfRust for shaping and Swash for rendering. The study target is COSMIC Text's own buffer and layout architecture.

- **C1:** `BufferLine` couples text ranges, attributes, and line endings. Append/split operations must move style spans and paragraph endings consistently; changes to shaping inputs invalidate both shape and layout state, whereas alignment changes invalidate layout alone. [buffer_line.rs](https://github.com/pop-os/cosmic-text/blob/main/src/buffer_line.rs).
- **C2:** Per-paragraph buffers hold text, styles, shaping choice, alignment, and cached results, supporting both display and editing on top of the lower-level font stack. [Buffer abstraction](https://github.com/pop-os/cosmic-text/blob/main/src/buffer_line.rs).
- **C3:** Shape and layout caches are separate, and resetting a line can retain allocations for reuse. This gives a concrete example of making incremental editing affordable while preserving invalidation rules. [Cache lifecycle](https://github.com/pop-os/cosmic-text/blob/main/src/buffer_line.rs).

The [README](https://github.com/pop-os/cosmic-text#readme) also describes a multilingual editing test that simulates insertion and deletion and compares the final buffer with the source corpus.

### 18. [linebender/parley](https://github.com/linebender/parley)

**Rust — reusable rich-text layout stack.** Count the monorepo once, including its Fontique integration. The current stack names HarfRust, Skrifa, Fontique, and ICU4X; the older design document still describes an earlier Swash-based plan.

- **C2:** Ranged, tree, and style-run builders accept different representations of styled text and produce a common `Layout`, including inline boxes. Font resources, layout scratch space, style resolution, and resulting glyph runs have distinct responsibilities. [Current crate architecture](https://github.com/linebender/parley/blob/main/parley/src/lib.rs).
- **C3:** `LayoutContext` reuses scratch allocations, while a built layout can be broken into lines and aligned repeatedly for different widths. Text or style changes require rebuilding, making the reuse boundary explicit. [Lifecycle contract](https://github.com/linebender/parley/blob/main/parley/src/lib.rs).

For the underlying sequencing problem, the [historical design document](https://github.com/linebender/parley/blob/main/doc/design.md) explains bidi analysis, itemization, font fallback, shaping, and per-line reordering, including why selection needs affinity. Read it for rationale while using current code and the repository README for present dependencies and APIs.

### 19. [go-text/typesetting](https://github.com/go-text/typesetting)

**Go — pure-Go font/shaping and wrapping stack shared by GUI-toolkit communities.** The relevant subsystems include `harfbuzz`, `bidi`, `segmenter`, and the higher-level `shaping` package. It is an implementation stack, not merely a CGo binding.

- **C1:** Shaped runs carry both rune and glyph cluster counts; wrapping must convert between these spaces differently for forward and reverse directions. The shaper also explicitly scales fixed-point coordinates to retain fractional precision. [Shaping and numerical handling](https://github.com/go-text/typesetting/blob/main/shaping/shaping.go), [cluster-aware wrapping](https://github.com/go-text/typesetting/blob/main/shaping/wrapping.go).
- **C2:** `Shaper`, `Input`, and `Output` separate shaping from consumers, while the wrapping layer operates on reusable shaped runs rather than a particular renderer. [Shaper interface](https://github.com/go-text/typesetting/blob/main/shaping/shaping.go).
- **C3:** A reusable shaping buffer, configurable font LRU, retained feature storage, and an option to skip expensive glyph-extents work show concrete performance choices. Wrapping uses different cluster lookup strategies for individual versus bulk queries. [Shaper](https://github.com/go-text/typesetting/blob/main/shaping/shaping.go), [wrapping](https://github.com/go-text/typesetting/blob/main/shaping/wrapping.go).

The repository documents evolving `v0` APIs; adoption does not imply interface stability.

### 20. [SixLabors/Fonts](https://github.com/SixLabors/Fonts)

**C# — managed OpenType shaping, bidi analysis, measurement, and layout.** This independently implements shaping rather than calling HarfBuzz or platform text APIs. It is useful for studying shared shaping results across custom rendering and text interaction.

- **C1:** The pipeline resolves overlapping/gapped style runs, retains grapheme/source indices, performs bidi analysis before substitution, applies mirrored forms, and manages fallback glyphs before final positioning. [Shaping architecture guide](https://github.com/SixLabors/docs/blob/main/articles/fonts/shaping.md).
- **C2:** Measurement, public shaping, and layout consume a shared pipeline; line composition remains separate from glyph selection. The guide explains how font identity, source indices, levels, advances, and bounds support carets, selection, and rendering. [Architecture guide](https://github.com/SixLabors/docs/blob/main/articles/fonts/shaping.md).
- **C3:** The implementation pools scratch state with exclusive ownership and explicit result-lifetime boundaries. It separates fallback-font construction so calls without fallbacks avoid that work. [TextShaper.Pipeline.cs](https://github.com/SixLabors/Fonts/blob/main/src/SixLabors.Fonts/TextShaper.Pipeline.cs).

The repository uses the Six Labors Split License; evaluate its terms for intended reuse. This entry describes inspected source, not a promise that every default-branch API is in the latest package.

### 21. [toptensoftware/RichTextKit](https://github.com/toptensoftware/RichTextKit)

**C# — rich-text layout and interaction for SkiaSharp, with HarfBuzzSharp shaping and its own bidi machinery.** This original repository is retained rather than similarly named forks.

- **C1:** Its bidi processor maintains isolate pairs, explicit-level stacks, an X9 removal map, isolated-run mappings, and whitespace-level cleanup. These structures make the relationship between retained source indices and algorithmically removed controls inspectable. [Bidi.cs](https://github.com/toptensoftware/RichTextKit/blob/main/Topten.RichTextKit/BidiAlgorithm/Bidi.cs).
- **C2:** `TextBlock` coordinates formatted text, base direction, wrapping width, line/height limits, truncation, and invalidation. The public layer includes caret and hit-testing facilities rather than only painted output. [TextBlock.cs](https://github.com/toptensoftware/RichTextKit/blob/main/Topten.RichTextKit/TextBlock.cs).
- **C3:** The bidi implementation deliberately reuses work buffers and keeps a per-thread processor to reduce garbage-collector pressure. [Buffer-lifetime rationale](https://github.com/toptensoftware/RichTextKit/blob/main/Topten.RichTextKit/BidiAlgorithm/Bidi.cs).

The current README states that it is under development and has been tested on Windows but not other platforms; the selection does not extend that platform assurance.

### 22. [google/skia](https://github.com/google/skia)

**C++ — SkParagraph and its shaping/Unicode integration within Skia; official GitHub mirror of the Googlesource repository.** Count Skia once and focus on `modules/skparagraph`, not the rest of this graphics monorepo.

- **C2:** Paragraph layout organizes immutable text, styled ranges, placeholders, fonts, Unicode analysis, shaped runs, and final lines. Its state progression separates indexing, shaping, line breaking, and formatting so applications can request geometry as well as paint. [ParagraphImpl.cpp](https://github.com/google/skia/blob/main/modules/skparagraph/src/ParagraphImpl.cpp).
- **C3:** A changed width can retain shaping while redoing later layout phases. The paragraph LRU stores runs, clusters, code-unit mappings, words, and bidi regions; its keys account for text, styles, and placeholders. This exposes the cost and correctness obligations of reusing a paragraph's expensive intermediate state. [Layout state transitions](https://github.com/google/skia/blob/main/modules/skparagraph/src/ParagraphImpl.cpp), [ParagraphCache.cpp](https://github.com/google/skia/blob/main/modules/skparagraph/src/ParagraphCache.cpp).

The cache also explicitly handles floating-point equality and compatibility rounding. Those are valuable code-review topics, not grounds for claiming the subsystem has simple numerical semantics.

### 23. [chearon/dropflow](https://github.com/chearon/dropflow)

**TypeScript with native components compiled to WebAssembly — CSS inline/text layout for browser and server rendering.** The relevant subsystem is its own itemization and inline text layout around HarfBuzz and SheenBidi, not the general CSS box model alone.

- **C1:** Itemization coordinates UTF-16 source offsets, bidi paragraph levels, script and emoji segmentation, surrogate pairs, and WebAssembly memory views that must be refreshed after memory growth. [text-itemize.ts](https://github.com/chearon/dropflow/blob/master/src/text-itemize.ts).
- **C2:** Shaped items, inline runs, font fallback, whitespace handling, grapheme boundaries, and line layout form a reusable layer above the native algorithms, supporting different paint backends. [layout-text.ts](https://github.com/chearon/dropflow/blob/master/src/layout-text.ts).
- **C3:** The text layout code reuses a shaping buffer and implements a word cache alongside an uncached shaping path. It documents a kerning-around-spaces tradeoff in the cache path, making it useful for studying where optimization can change text semantics. [Caching implementation and caveat](https://github.com/chearon/dropflow/blob/master/src/layout-text.ts).

The README still marks the CSS `unicode-bidi` property as planned. Bidi text support therefore must not be confused with complete CSS bidi behavior.

## Coverage and search notes

Discovery used more than a dozen formulations, including native OpenType shapers; Rust ports and independent Rust engines; standalone Unicode bidi implementations; Go GUI typesetting; managed C# shaping and rich text; JavaScript font engines; Graphite smart fonts and minority-language support; compact Arabic engines; desktop paragraph libraries; browser/canvas/WebAssembly layout; embedded shaping; and functional-language bidi searches. Follow-up searches for conformance-test implementations and broad text-shaping engines increasingly returned the same core projects, wrappers, application renderers, or additional candidates requiring a separate audit. Primary repository metadata, READMEs, source files, conformance harnesses, architecture documents, and release histories were used to vet the retained selection.

The list spans C, C++, Rust, Go, C#, JavaScript, TypeScript, and Python, with ICU's Java implementation acknowledged within its single monorepo entry. It includes independent algorithms, substantial language ports, and integrations with their own layout/state machinery. HarfRust's RustyBuzz ancestry and the Python package's reuse of `unicode-bidi` are explicit; neither relationship is treated as two unrelated algorithms. Pango and Skia are identified as official mirrors. No retained repository was marked archived in the metadata checked; SheenFigure and Typography are explicitly treated as older, lower-activity study targets.

Excluded from the retained list were pure bindings and generated wrappers, font rasterizers/parsers without a substantial shaping or bidi role, font collections, tutorial/demo repositories, and generic editors that delegate all relevant work. RustyBuzz was not separately counted alongside HarfRust. The merged `go-text/shaping` repository was not counted alongside `go-text/typesetting`. Small canvas word-wrapping utilities and Unicode normalization libraries did not provide the required category fit. Searches for less common implementation languages often led to ICU bindings or unrelated bidirectional type-checking work. Android/other non-GitHub implementations were not added through unverified personal mirrors.

This is a selection guide rather than an exhaustive implementation census. Conformance and test statements distinguish inspected test mechanisms or project-reported results from tests performed here. Newer search-discovered engines were not promoted merely on broad feature or performance claims. Default-branch source and older design documents can disagree; Parley's historical design and current implementation are deliberately distinguished. C4 is assigned only where inspected release history establishes continuing compatibility or robustness work across years, rather than inferred from repository age or push recency.
