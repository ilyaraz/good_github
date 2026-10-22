# PDF and page description language interpreters

Research date: **2026-10-09**.

This report selects **18 GitHub repositories** that implement PDF content interpretation or execute related page-description languages: PostScript, PCL/PCL XL, XPS, DVI/XDV, and HPGL/2. It includes rasterizers, vector-output interpreters, and content interpreters that recover positioned text and graphics without rendering pixels. Pure document generators, object-container editors without substantial content interpretation, bindings, and viewer shells are outside the selection. Monorepos count once; their relevant subsystem is identified below.

The criteria are evidence-based selection judgments, not a certification of conformance, security, performance, or uniform code quality. Source and documentation links below are also suggested reading entry points. GitHub repository metadata was checked for canonical names and archive status; a recent push alone is not treated as evidence of maturity or ongoing maintenance.

- **C1 — Difficult correctness:** nontrivial language semantics, state invariants, numerical behavior, concurrency, malformed input, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces or components that serve multiple interpretation, rendering, or extraction use cases.
- **C3 — Performance with structure:** concrete techniques addressing memory, latency, or throughput, with identifiable architectural boundaries.
- **C4 — Sustained evolution:** dated, multi-year evidence of compatibility work, regression handling, testing, or complexity management.

## Native engines and browser rendering

### 1. [ArtifexSoftware/mupdf](https://github.com/ArtifexSoftware/mupdf)

**Language / role:** C; PDF and XPS interpretation, rendering, and conversion. **Official Artifex GitHub mirror.**

Study how an interpreter becomes an embeddable rendering framework through devices, reference-counted display lists, and explicit execution contexts. Its display-list boundary is particularly useful for understanding repeated rendering at different scales and separation of document access from rasterization.

- **C1:** The [multithreaded example](https://github.com/ArtifexSoftware/mupdf/blob/master/docs/examples/multi-threaded.c) confines document access to one thread, clones contexts for rendering threads, supplies shared lock callbacks, and handles cleanup through MuPDF's exception machinery. These are concrete ownership and concurrency constraints, not a blanket thread-safety promise.
- **C2, C3:** The [display-list interface](https://github.com/ArtifexSoftware/mupdf/blob/master/include/mupdf/fitz/display-list.h) records device commands for repeated playback without reinterpreting page content. Playback accepts a transform, clipping region, and progress/abort cookie. The same abstraction supports caching, output devices, and moving rendering work between threads.

### 2. [ArtifexSoftware/ghostpdl](https://github.com/ArtifexSoftware/ghostpdl)

**Language / role:** Mainly C and PostScript; Ghostscript, GhostPDF, GhostPCL, and GhostXPS. **Official mirror of Artifex's canonical GhostPDL repository; counted once.**

This is the broadest language-family selection: PostScript/PDF, PCL5/PCL XL, and XPS interpreters share graphics and output infrastructure. Study the tension between standards, compatibility with existing documents, printer devices, and constrained-memory rendering.

- **C1:** The current C PDF interpreter's [numeric parsing implementation](https://github.com/ArtifexSoftware/ghostpdl/blob/master/pdf/pdf_int.c) explicitly reproduces some Acrobat number-overflow behavior while separately guarding fractional accumulation and reporting invalid integer formats. Correctness here includes compatibility decisions that differ from simply calling a standard numeric parser.
- **C2, C3:** The [developer architecture guide](https://ghostscript.readthedocs.io/en/latest/Develop.html) explains stream and memory substrates, graphics-state machinery, virtual device procedures, and selecting banded versus full-page rendering according to available memory. Some sections retain historical descriptions, including the former PostScript-based PDF interpreter; use the current `pdf/` source for today's PDF execution path.

### 3. [chromium/pdfium](https://github.com/chromium/pdfium)

**Language / role:** C++; Chromium's embeddable PDF engine. **Archived official GitHub repository**, verified through GitHub metadata. The retained source is substantial; the repository's instructions identify [Googlesource as upstream](https://pdfium.googlesource.com/pdfium/). Do not mistake this GitHub snapshot for the current development venue.

Study resumable rendering as an explicit state machine rather than a single blocking page-render call.

- **C1:** [CPDF_ProgressiveRenderer](https://github.com/chromium/pdfium/blob/main/core/fpdfapi/render/cpdf_progressiverenderer.cpp) tracks readiness, continuation, failure, current layers, and the last rendered object. It pairs device save/restore operations and coordinates incomplete parsing with paused rendering.
- **C3:** The same implementation bounds work between pause checks, skips objects outside the clip rectangle, and requests image-cache optimization when configured. Forms and shadings affect its work budget, showing how responsiveness and memory limits influence the rendering control flow.

### 4. [mozilla/pdf.js](https://github.com/mozilla/pdf.js)

**Language / role:** JavaScript; independent PDF interpretation and browser rendering.

Study the boundary between asynchronous document interpretation and transferable drawing commands. The important code is the engine beneath the familiar viewer, especially cancellation and streaming work across the worker interface.

- **C1, C2:** The [worker implementation](https://github.com/mozilla/pdf.js/blob/master/src/core/worker.js) gives document operations a message-based interface, tracks worker tasks and termination, checks API/worker version agreement, and retries document initialization in a recovery mode for cross-reference failures. Its task lifecycle exposes the failure modes of asynchronous interpretation.
- **C3:** [OperatorList](https://github.com/mozilla/pdf.js/blob/master/src/core/operator_list.js) optimizes queued operations, streams bounded chunks, selects useful flush boundaries such as restore/end-text operations, and transfers image buffers. It also distinguishes compositing cases that require isolation, making rendering cost and graphics semantics meet at a visible intermediate representation.

### 5. [SerenityOS/serenity](https://github.com/SerenityOS/serenity)

**Language / role:** C++; the **LibPDF** subsystem inside the SerenityOS monorepo. The operating system is not itself the subject of this entry.

Study a comparatively approachable PDF renderer integrated with an independently developed graphics library. This is useful for tracing operators directly into rendering state and examining incomplete-feature/error handling without starting with an industrial-scale engine.

- **C1:** [Renderer.cpp](https://github.com/SerenityOS/serenity/blob/master/Userland/Libraries/LibPDF/Renderer.cpp) uses a scoped state-restoration object specifically to unwind nested `q` pushes when an error prevents the corresponding `Q` operations from executing. It also shows clip-mask compositing and accumulation of rendering errors.
- **C2, C3:** [Document.h](https://github.com/SerenityOS/serenity/blob/master/Userland/Libraries/LibPDF/Document.h) separates indirect-object resolution, page access, strict/permissive parsing, and metadata from the renderer. Its comments explain deferred page loading and candidly identify further page-tree laziness as unfinished optimization. This is architectural evidence, not a claim of complete PDF compatibility.

## JVM and .NET implementations

### 6. [apache/pdfbox](https://github.com/apache/pdfbox)

**Language / role:** Java; PDF content interpretation, rendering, text processing, and document tooling. **Official Apache GitHub mirror.**

Study a reusable stream-execution framework with specialized operator handlers and higher-level rendering. Particularly instructive are the places where nested content must inherit resources while preserving the surrounding graphics state.

- **C1, C2:** [PDFStreamEngine](https://github.com/apache/pdfbox/blob/trunk/pdfbox/src/main/java/org/apache/pdfbox/contentstream/PDFStreamEngine.java) saves and restores graphics stacks and resource scopes in `finally` blocks for forms, transparency groups, and Type 3 glyph programs. It contains recursion-depth checks and an explicitly documented resource-inheritance compatibility exception for real PDFs.
- **C3:** [PDFRenderer](https://github.com/apache/pdfbox/blob/trunk/pdfbox/src/main/java/org/apache/pdfbox/rendering/PDFRenderer.java) exposes image subsampling and downscaling-quality controls, and checks raster dimensions before allocating a buffered image. Its documentation makes the speed/memory versus image-quality tradeoff explicit.

### 7. [pcorless/icepdf](https://github.com/pcorless/icepdf)

**Language / role:** Java; community ICEpdf rendering engine and viewing API.

Study an interpreter that produces a collection of drawing commands for subsequent Java2D replay, with separate concerns for parsing, optional content, image reuse, and painting.

- **C1, C2:** [Shapes](https://github.com/pcorless/icepdf/blob/main/core/core-awt/src/main/java/org/icepdf/core/pobjects/graphics/Shapes.java) stores `DrawCmd` objects and replays them into a graphics context. Its implementation explains why nested shapes must keep paint-specific state local: mutating shared cached commands would interfere with concurrent paints. Optional-content state is also created per paint.
- **C3:** [ContentParser](https://github.com/pcorless/icepdf/blob/main/core/core-awt/src/main/java/org/icepdf/core/util/parser/content/ContentParser.java) caches repeated inline images with soft references and explains why weak keys would defeat reuse during garbage collection. Parsing and painting both check interruption periodically, exposing the balance between cancellation responsiveness and per-operation overhead.

### 8. [LibrePDF/OpenPDF](https://github.com/LibrePDF/OpenPDF)

**Language / role:** Java; specifically **`openpdf-renderer` and its `openpdf-core` integration**, not merely the PDF-generation API. Counted once.

Study the consolidation of a renderer's parsing responsibilities into a shared document engine. The renderer has legacy `com.sun.pdfview` ancestry and a distinct current core-driven implementation; those paths should not be conflated.

- **C2:** The [renderer module guide](https://github.com/LibrePDF/OpenPDF/blob/master/openpdf-renderer/README.md) documents the migration to the core parser, including content-operator walking, a new bridge API, and temporarily retained deprecated entry points. This provides a concrete example of reducing duplicate parsing logic while managing caller compatibility.
- **C1, C3:** [OpenPdfCorePageRenderer](https://github.com/LibrePDF/OpenPDF/blob/master/openpdf-renderer/src/main/java/org/openpdf/renderer/core/OpenPdfCorePageRenderer.java) handles graphics/clip stacks, device-pixel hairline semantics, and inline-image preprocessing to keep binary image data out of ordinary token parsing. Font-program caching avoids repeated parsing for text operations. Coverage is explicitly a subset; the module guide distinguishes it from the legacy renderer's coverage.

### 9. [DrJohnMelville/Pdf](https://github.com/DrJohnMelville/Pdf)

**Language / role:** C#; Melville.Pdf's managed PDF interpreter and rendering framework, with WPF and SkiaSharp targets.

Study how a document interpreter can remain independent of display technology while treating indirect objects as potentially asynchronous I/O. This is a substantive engine, even though some image decoders have external ancestry and output targets depend on other graphics systems.

- **C2:** The [assembly architecture](https://github.com/DrJohnMelville/Pdf/blob/main/Docs/Architecture/AssemblySummaries.md) identifies `IDrawTarget`, `IRenderTarget`, and `IGraphicsState`, alongside low-level document objects, independently packaged decoders, image/text extraction targets, and a PostScript interpreter used in embedded PDF constructs. It also describes generated reference PDFs and rendering comparisons.
- **C3:** The [async design explanation](https://github.com/DrJohnMelville/Pdf/blob/main/Docs/Architecture/Async.md) shows lazy cross-reference resolution behind dictionary/array access, caching resolved objects, and using `ValueTask` because most accesses do not actually require I/O. This gives a clear account of the architectural cost and intended performance benefit. The project documents incomplete rendering features; inclusion is not a full-conformance claim.

### 10. [UglyToad/PdfPig](https://github.com/UglyToad/PdfPig)

**Language / role:** C#; PDF content interpretation for extraction and analysis, originally a PDFBox port with its own implementation and evolution. **Not a general pixel renderer.**

Study the conversion of a page's graphics program into positioned letters, paths, images, and marked content. This is an example of executing drawing semantics to produce analytical data rather than a bitmap.

- **C1:** [BaseStreamProcessor](https://github.com/UglyToad/PdfPig/blob/master/src/UglyToad.PdfPig/Graphics/BaseStreamProcessor.cs) preserves a nonempty graphics-state stack, distinguishes strict from lenient handling of an invalid pop, clones graphics state, and applies font decoding and coordinate transforms. These details determine whether extracted positions mean what the page actually drew.
- **C2:** Its generic `BaseStreamProcessor<TPageContent>` executes graphics-state operations against an operation context. The [concrete ContentStreamProcessor](https://github.com/UglyToad/PdfPig/blob/master/src/UglyToad.PdfPig/Graphics/ContentStreamProcessor.cs) specializes glyph/path/image handling and returns structured page content, separating execution machinery from its extraction result.

## Rust and dynamic-language content engines

### 11. [LaurenzV/hayro](https://github.com/LaurenzV/hayro)

**Language / role:** Rust; independent PDF interpreter with bitmap and SVG output.

Study a modern separation between PDF syntax, interpretation, devices, and image/font-related support crates. The project explicitly calls itself experimental and documents unsupported cases, including knockout groups and nonembedded CID fonts. Its README also says performance has not yet been its main focus, so C3 is deliberately not awarded here.

- **C1:** The [test-suite guide](https://github.com/LaurenzV/hayro/blob/main/hayro-tests/README.md) distinguishes crash/load tests, rendering snapshots, and SVG-output tests. It draws on PDFBox, PDF.js, issue-tracker files, and a larger document corpus. These are concrete mechanisms for managing malformed inputs and rendering regressions; the external corpus and generated baselines are not all committed to GitHub.
- **C2:** The [Device trait](https://github.com/LaurenzV/hayro/blob/main/hayro-interpret/src/device.rs) receives positioned glyph runs, paths, images, clip operations, transparency groups, and marked-content events. Output consumers can share interpretation while choosing different drawing or analysis behavior.

### 12. [pdfminer/pdfminer.six](https://github.com/pdfminer/pdfminer.six)

**Language / role:** Python; community continuation of PDFMiner, focused on interpreted text/layout and content extraction. **Not a general rasterizer; the original PDFMiner is not counted separately.**

Study the separation between executing page content, managing resources, and collecting output through a device. This is especially useful when glyph placement and resource scope matter more than pixel output.

- **C1, C2:** [PDFPageInterpreter](https://github.com/pdfminer/pdfminer.six/blob/master/pdfminer/pdfinterp.py) takes a resource manager and device, manages graphics/text state, and recursively interprets Form XObjects. It tracks active stream IDs across parent interpreters to avoid circular content execution. The explicit device boundary permits extraction behaviors without replacing the interpreter.
- **C4:** The [changelog](https://github.com/pdfminer/pdfminer.six/blob/master/CHANGELOG.md) records multi-year work: 2021–2022 encryption/CMap support and malformed-input fixes, followed by 2025–2026 content-stream recursion handling, split-token corrections, CMap storage changes, and Python compatibility updates. This demonstrates substantive continued development beyond the original project.

### 13. [yob/pdf-reader](https://github.com/yob/pdf-reader)

**Language / role:** Ruby; PDF content-stream walking and stateful text extraction. **No built-in page rasterization.**

Study a compact callback-oriented interpreter API that makes a PDF page's operator sequence accessible to multiple consumers. The useful boundary is between operator delivery and receivers that implement stateful semantics.

- **C2:** [Page#walk](https://github.com/yob/pdf-reader/blob/main/lib/pdf/reader/page.rb) sends sequential content-stream operations to receiver objects, supplies page resources, and underlies higher-level text/run extraction. The implementation also validates receiver calls and detects loops in page ancestry.
- **C1, C3:** [PageState](https://github.com/yob/pdf-reader/blob/main/lib/pdf/reader/page_state.rb) implements graphics-state copying, text matrices, font/resource scopes, and the distinction between glyph spacing and `TJ` displacement. It memoizes text-rendering matrices and special-cases common displacement calculations to reduce allocations. The same source explicitly leaves vertical displacement support unfinished, a useful limit when studying or adopting it.

## PostScript, XPS, DVI, and plotter-language specialists

### 14. [luser-dr00g/xpost](https://github.com/luser-dr00g/xpost)

**Language / role:** C and PostScript; embeddable PostScript interpreter with limited graphics support.

Study the language runtime itself: composite objects, relocatable virtual memory, save/restore, name interning, stacks, and device dispatch. Its repository describes rudimentary graphics and platform limitations; this is a runtime-design selection rather than a claim that it substitutes for Ghostscript's rendering coverage.

- **C1:** The [internals document](https://github.com/luser-dr00g/xpost/blob/master/doc/NEWINTERNALS) explains why global allocations cannot contain local objects, how save levels interact with collection, and why pointers into movable memory must not survive allocation. These are specific invariants whose violation would create dangling references.
- **C2, C3:** The same document describes relative-addressed memory files, cheaply represented array/string intervals, segmented stacks, and device dictionaries whose PostScript procedures can be replaced by C operators. Its raster-device interface can return control at `showpage` and later resume interpretation, making the library useful beyond its command-line application.

### 15. [AndyCappDev/postforge](https://github.com/AndyCappDev/postforge)

**Language / role:** Python, with optional Cython acceleration; PostScript execution and raster/vector output.

Study a readable high-level implementation of the execution stack, VM lifetime, and a page display list. The project advertises Level 3 coverage, but this research did not independently establish full standards conformance or long-term maturity; C4 is not claimed.

- **C1:** The [architecture guide](https://github.com/AndyCappDev/postforge/blob/master/docs/developer/architecture-overview.md) explains local/global VM, copy-on-write save/restore, and job encapsulation. It also explains why successful job-control tests must run outside the ordinary assertion framework: resetting VM destroys that framework's state.
- **C2:** The documented pipeline separates tokenizer, execution loop, display-list builder, and output device. Paths are transformed when constructed; display-list elements preserve painting and clipping operations. Cairo-backed raster/SVG devices and the PDF device consume the same page representation, while `showpage` and `copypage` deliberately differ in state retention.

### 16. [GNOME/libgxps](https://github.com/GNOME/libgxps)

**Language / role:** C, GObject, and Cairo; XPS document interpretation and rendering. **Official read-only GNOME mirror of its GitLab repository.**

Study an XML/ZIP-based page description rather than a PDF or PostScript token stream. The small library exposes document/page objects while translating nested XPS resources, transforms, glyphs, paths, and opacity into Cairo operations.

- **C1, C2:** [gxps-page.c](https://github.com/GNOME/libgxps/blob/master/libgxps/gxps-page.c) separates fixed-page parsing from rendering parsers, manages nested parser contexts, validates numeric attributes, and uses Cairo state and groups for transforms and opacity masks. Rendering into a caller-provided Cairo context keeps interpretation separate from the eventual output surface.
- **C4:** [NEWS](https://github.com/GNOME/libgxps/blob/master/NEWS) documents work across 2012–2021 on failed-parse cleanup, interleaved ZIPs, OpenXPS schemas, malformed files, integer overflow, and font scaling. Its newest listed release is from 2021; that historical evidence does not establish a frequent present-day release cadence.

### 17. [mgieseki/dvisvgm](https://github.com/mgieseki/dvisvgm)

**Language / role:** C++; native DVI/XDV interpretation to SVG, with EPS/PDF and PostScript-special integration.

Study a page-description machine with explicit position registers, a state stack, virtual fonts, and extensible conversion actions. Its native DVI interpreter is the reason for inclusion; PostScript and PDF paths also rely on external engines, so it is not counted as another independent general PDF renderer.

- **C1, C2:** [DVIReader.cpp](https://github.com/mgieseki/dvisvgm/blob/master/src/DVIReader.cpp) checks zero measurement denominators, stack underflow and nonempty end-of-page stacks, and drawing outside page boundaries. It interprets virtual-font programs and invokes specialized action hooks after decoded commands, separating DVI execution from conversion behavior.
- **C4:** [NEWS](https://github.com/mgieseki/dvisvgm/blob/master/NEWS) shows compatibility and regression work across multiple years: adapting to Ghostscript changes, correcting clipping/optimizer behavior, deterministic font output, malformed-DVI fixes, and C++ toolchain compatibility. This is stronger maturity evidence than the repository's age alone.

### 18. [mozman/ezdxf](https://github.com/mozman/ezdxf)

**Language / role:** Python; specifically the **`ezdxf.addons.hpgl2` interpreter and virtual plotter**, inside the larger DXF library. Counted once.

Study a deliberately bounded interpreter for HPGL/2 plot files, with the virtual plotter reducing language commands to polylines and filled polygons. The [official add-on documentation](https://ezdxf.readthedocs.io/en/stable/addons/hpgl2.html) describes conversion to DXF/SVG/PDF and explicitly limits support to common command subsets. PDF export uses PyMuPDF; the HPGL interpretation itself is implemented here.

- **C1:** The [virtual plotter](https://github.com/mozman/ezdxf/blob/master/src/ezdxf/addons/hpgl2/plotter.py) tracks pen position separately in user and page coordinates, absolute/relative movement, pen-up/down state, and polygon mode. Entering polygon mode redirects drawing into a buffer; leaving it restores the output backend. Correct interpretation depends on these interacting state transitions and coordinate conversions.
- **C2:** The interpreter → plotter → backend separation permits the same interpreted geometry to reach different outputs. Explicit fill rules and buffered polygon replay keep output choices separate from command semantics. Font rendering and the full HPGL/2 command set are outside its stated coverage.

## Search coverage and limitations

Discovery used more than six distinct live-web query families: general PDF renderer architecture; PostScript/PCL/XPS implementations; pure-Rust interpreters; Java renderers; C# engines and content processors; Python/Ruby extraction interpreters; embedded OS PDF libraries; DVI/XDV conversion; HPGL/2 plotters; Go PDF interpretation; and official-mirror status for Poppler/Xpdf. Targeted searches then located implementation files, architecture notes, and regression/release evidence. Later broad and exclusion-filtered queries increasingly returned the same engines, bindings, viewer shells, and unverified new implementations, providing diminishing returns for this selection.

Every retained canonical repository was opened or checked through the GitHub API, and additional primary implementation or architecture material was read. Raw source reads were of actual implementation/design files, not a second copy of the README presented as independent evidence. The archive check identified PDFium's GitHub snapshot as archived. Mirrors are marked individually. No candidate code was executed, no dependencies were installed, and no repositories were cloned.

Important boundaries and exclusions:

- **Poppler and Xpdf remain major coverage gaps imposed by the GitHub requirement.** [Poppler's official site](https://poppler.freedesktop.org/) directs development to freedesktop GitLab and labels its linked external CI arrangements unofficial. This search did not establish a qualifying official substantive GitHub mirror for either project; third-party copies were not substituted.
- MuPDF/PDFium bindings and ordinary viewer frontends were excluded to avoid recounting the underlying interpreter. PDF-generation libraries and structural editors were also excluded unless a substantive content interpreter was verified. GhostPDL's constituent interpreters and the selected monorepo subsystems each count only once.
- The three extraction-oriented selections—PdfPig, PDFMiner.six, and PDF::Reader—belong here because their code executes content-stream state and operators. They are explicitly distinguished from pixel renderers. Similarly, dvisvgm qualifies through native DVI interpretation and ezdxf through native HPGL/2 interpretation.
- Smaller engines and partial implementations are included for concrete design substance, not parity with established renderers. Unsupported-feature and completeness claims were kept qualified. Performance criteria describe inspected mechanisms; no comparative benchmark or numerical speed claim was independently validated.
- This is read-only source research at the stated date. Links generally follow default branches and can evolve; no comprehensive conformance, fuzzing, or maintenance audit was performed. The engineering lessons are grounded interpretations of the cited implementation and documentation, not assurances that every component is exemplary.
