# Typesetting and page layout engines

Research date: **2026-10-09**.

This selection covers 24 repositories that implement substantive paragraph, document, or page layout: standalone typesetting languages, HTML/CSS and XSL-FO pagination, composable document libraries, and interactive editors with their own layout subsystems. Libraries qualify through their layout implementation, rather than merely their ability to write PDF files. Monorepos are counted once, with the relevant subsystem identified. The list deliberately includes smaller research and specialist systems alongside established projects.

The criteria below are engineering judgments grounded in the linked implementation and documentation, not audits or claims that every component is exemplary. Repository identities and status were checked against GitHub pages or API metadata. Links to moving branches describe the material inspected on the research date; a recent push alone is not treated as evidence of sustained maintenance.

- **C1 — Difficult correctness:** nontrivial invariants, numerical semantics, interacting layout constraints, adversarial inputs, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces or models that support multiple document structures, applications, or rendering arrangements.
- **C3 — Performance with structure:** concrete measures addressing work, allocation, memory, or interactive latency within an understandable architecture.
- **C4 — Sustained evolution:** a multiyear record accompanied by compatibility work, testing, or deliberate management of complexity.

## Standalone typesetters and programmable publishing systems

### 1. [typst/typst](https://github.com/typst/typst)

**Language / role:** Rust; a programmable document compiler with its own typesetting and layout implementation. Study how a modern incremental compiler connects a document language to paragraph, mathematical, grid, and page layout.

- **C1:** Paragraph processing explicitly separates collection, preparation, line breaking, and frame construction. Collecting the paragraph before bidirectional analysis, then coordinating shaping and candidate line breaks, exposes the correctness dependencies between logical text and visual placement. [Paragraph implementation](https://raw.githubusercontent.com/typst/typst/main/crates/typst-layout/src/inline/mod.rs).
- **C3:** The paragraph implementation uses dependency-tracked memoization, with tracked world and introspection inputs. This is concrete infrastructure for reusing expensive layout results while retaining the dependencies needed to invalidate them; it is not a claimed benchmark advantage. The surrounding crate separates inline, flow, grid, mathematical, and page algorithms. [Layout crate entry point](https://github.com/typst/typst/blob/main/crates/typst-layout/src/lib.rs).

### 2. [sile-typesetter/sile](https://github.com/sile-typesetter/sile)

**Language / role:** Primarily Lua, with native components; an extensible typesetter built around frames, nodes, classes, packages, shapers, and outputters. Particularly useful for studying unusual page designs and synchronized multilingual text.

- **C1:** The manual explains the horizontal node queue, vertical output queue, and transitions that turn shaped text into lines and pages. Its parallel-text example maintains separate typesetter states and coordinates column and page flushing, making state ownership and ordering visible. [Developer sections of the manual](https://sile-typesetter.org/manual/sile-0.15.6.pdf).
- **C2:** Frames and replaceable Lua typesetting components let extensions change document behavior below the surface syntax. The manual describes both the node model and custom typesetter use, rather than only end-user commands.
- **C4:** The changelog records development across 2014–2025, including compatibility controls for changed spacing behavior, language-specific hyphenation handling, and adaptations to native-library APIs. [Changelog](https://github.com/sile-typesetter/sile/blob/master/CHANGELOG.md).

### 3. [TeX-Live/texlive-source](https://github.com/TeX-Live/texlive-source)

**Language / role:** WEB/Pascal, C, C++, and Lua; the relevant subsystem is the family of engines under texk/web2c. **Official mirror of the upstream Subversion source repository**, not a complete installed TeX distribution. Count the engine collection once.

- **C1:** TeX's literate source makes numerical behavior unusually explicit: fixed-point dimensions, decimal conversion and rounding, overflow avoidance, and validation of font metrics are part of the layout contract. It is a strong study in obtaining reproducible typography across machines. [TeX implementation, tex.web](https://raw.githubusercontent.com/TeX-Live/texlive-source/trunk/texk/web2c/tex.web).
- **C4:** The same source documents portability and TRIP conformance requirements, while the repository changelog supplies a multiyear record of build, platform, and test maintenance. This pairs an unusually stable engine contract with continued integration work, rather than inferring quality from TeX's age. [Repository changelog](https://github.com/TeX-Live/texlive-source/blob/trunk/ChangeLog).

### 4. [tectonic-typesetting/tectonic](https://github.com/tectonic-typesetting/tectonic)

**Language / role:** Rust with C/C++ components; a substantially evolved XeTeX-derived system with an embeddable processing driver and managed resource access. Its value alongside TeX Live is the architecture around the engine and the ongoing implementation transition.

- **C1:** ProcessingSession coordinates engine invocations and reruns when auxiliary outputs change. This exposes a document-build correctness problem beyond individual line breaks: deciding when references and other generated state have converged. [Driver API](https://docs.rs/tectonic/latest/tectonic/driver/index.html).
- **C2:** The session/builder API separates document processing from the command-line interface, making the typesetter usable as an application component rather than only an executable.
- **C4:** Release history spans 2017–2026 and records concrete compatibility and migration work, including continued support for older resource-bundle formats, Rust migration of XeTeX layout code, and fixes for unsafe/native-boundary failures. [Release-branch changelog](https://github.com/tectonic-typesetting/tectonic/blob/release/CHANGELOG.md).

### 5. [gfngfn/SATySFi](https://github.com/gfngfn/SATySFi)

**Language / role:** OCaml; a typesetting system with a statically typed functional programming language. Study how typed document construction meets a concrete box and line-breaking implementation.

- **C1:** The line breaker represents discretionary breaks and natural, stretchable, and shrinkable widths, then searches a graph for a break sequence. It explicitly handles the case where a feasible path cannot be found and distinguishes alphabetic and ideographic text behavior. [Line-breaking implementation](https://github.com/gfngfn/SATySFi/blob/master/src/backend/lineBreak.ml).
- **C2:** The backend's algebraic box model accommodates text, mathematics, graphics, frames, and tabular content rather than hard-coding a single report format. Separate modules handle page breaking, fonts, and tables, providing an informative companion to the language's typed extension model. [Backend source tree](https://github.com/gfngfn/SATySFi/tree/master/src/backend).

### 6. [patoline/patoline](https://github.com/patoline/patoline)

**Language / role:** OCaml; a research-oriented programmable typesetter. **Historical/dormant in the inspected GitHub record:** not archived, but the last recorded push was in May 2022, and the README targets older OCaml versions. Treat it as an architectural study, without assuming a current toolchain experience.

- **C1:** Its breaking interface exposes figure placement state, line and page parameters, badness, and explicit failures such as no solution, overfull/underfull output, widows, and orphans. This makes interactions among layout constraints visible to callers instead of reducing everything to a successful list of coordinates. [Breaking interface](https://github.com/patoline/patoline/blob/master/typography/Break.mli).
- **C2:** The breaker is an OCaml functor parameterized by line types, with callbacks for line completion, page creation, parameters, and cost evaluation. It is a useful example of an extensible optimization boundary. The changelog gives context for the project's module and build-system evolution, but does not establish present maintenance. [Changes](https://github.com/patoline/patoline/blob/master/CHANGES.md).

### 7. [aligrudi/neatroff](https://github.com/aligrudi/neatroff)

**Language / role:** C; a compact troff-family formatter. A useful smaller codebase for studying layout state machines and the relationship between a formatting language, font/device support, and paragraph adjustment.

- **C1:** The formatter has a precise buffering protocol: failure to enqueue another word requires draining completed lines and retrying. Changes to line length and indentation are delayed until a partially constructed line has been emitted. Integer distribution of gap widths also makes rounding decisions explicit. [Formatter implementation](https://github.com/aligrudi/neatroff/blob/master/fmt.c).
- **C2:** The word/line formatter is separated from the roff command language and surrounding device, font, preprocessor, and postprocessor tools. That boundary supports macro-driven document composition and different output workflows while keeping the core formatting mechanics inspectable. [Project and companion-tool overview](https://github.com/aligrudi/neatroff/blob/master/README).

### 8. [speedata/publisher](https://github.com/speedata/publisher)

**Language / role:** Lua and Go, with native integration; an XML-driven publishing system built on LuaTeX. Its own contribution is document orchestration, grids, tables, and page construction; it reuses LuaTeX's lower-level typesetting machinery.

- **C1:** Grid allocation, multipage table splitting, and repeated table heads/feet introduce document-level constraints above paragraph composition. The architecture identifies dedicated modules for these responsibilities and explains how they construct LuaTeX node lists directly. [Architecture guide](https://github.com/speedata/publisher/blob/develop/ARCHITECTURE.md).
- **C2:** The guide traces the Go launcher, Lua command dispatch, XML/data access, page/grid/table modules, and the C/Go bridge. This is a substantial reusable publishing layer, with business-document behavior separated from the underlying engine.
- **C3:** Resource lookup uses an index/cache, and the guide identifies frequently executed dispatch, page, and node paths. It also describes rendered-PDF image comparison for checking changes. These are concrete design and validation choices, without implying any particular throughput.

## HTML/CSS and XSL-FO pagination

### 9. [Kozea/WeasyPrint](https://github.com/Kozea/WeasyPrint)

**Language / role:** Python; an HTML/CSS-to-PDF engine with its own paged layout implementation. Particularly readable for studying how CSS concepts become a formatting tree and then page fragments.

- **C1:** The implementation guide distinguishes specified, computed, and used values; explains when percentages and automatic sizes become concrete; and documents formatting-tree invariants and box splitting across pages. Correctness depends on preserving these distinctions through successive phases. [Architecture and implementation guide](https://doc.courtbouillon.org/weasyprint/stable/going_further.html).
- **C2:** HTML/CSS parsing, cascade, box construction, layout, stacking, and drawing are separate stages. The guide explains that drawing consumes layout results rather than recalculating geometry, making it a useful model for separating semantic layout from PDF output. Its stated emphasis on maintainability also makes C2 more appropriate here than an unsupported speed claim.

### 10. [vivliostyle/vivliostyle.js](https://github.com/vivliostyle/vivliostyle.js)

**Language / role:** TypeScript; a browser-based paged-media engine and viewer. The relevant subsystem is Vivliostyle Core; the monorepo is counted once.

- **C1:** Its module map separates cascade and styling, view-tree generation, page masters, page floats, and region/column breaking. Their coordination is the central engineering challenge: a selected page master constrains regions while floats and breaks change the content that can be placed. [Development guide and source map](https://github.com/vivliostyle/vivliostyle.js/wiki/Development).
- **C2:** Core exposes an API to the viewer instead of embedding all document behavior in viewer UI code. Separate task scheduling, view-tree, CSS-page, and layout modules make this a substantive pagination system layered on browser primitives. The guide provides named source entry points for following those boundaries and describes the test/development workflow.

### 11. [pagedjs/pagedjs](https://github.com/pagedjs/pagedjs)

**Language / role:** JavaScript; a paged-media layer that uses browser layout while implementing document fragmentation and CSS processing itself. It is useful for studying the unstable geometry and asynchronous resources involved in browser-assisted pagination.

- **C1:** Layout resumes from break tokens, measures overflow, waits for images, and handles forced breaks and footnote-related bounds. It explicitly rejects a repeated break token that would make pagination fail to advance, exposing a practical termination invariant. [Chunker layout implementation](https://github.com/pagedjs/pagedjs/blob/main/src/chunker/layout.js).
- **C2:** The repository separates chunking from CSS polishing and exposes hooks around layout, overflow, and break handling. Those hooks allow extensions to participate in page construction while the shared engine owns the continuation protocol; this goes beyond invoking a browser's print command.

### 12. [apache/xmlgraphics-fop](https://github.com/apache/xmlgraphics-fop)

**Language / role:** Java; an XSL-FO formatter with layout managers, an area tree, and output backends. Study how a document formatting vocabulary is translated into reusable break optimization and renderer-independent areas.

- **C1:** BreakingAlgorithm tracks feasible break candidates, cumulative widths, stretch/shrink, fitness classes, and penalties. It includes bounded recovery for cases that cannot satisfy the normal fit conditions. The same abstraction can interpret the target measure as line width or column height. [BreakingAlgorithm](https://github.com/apache/xmlgraphics-fop/blob/main/fop-core/src/main/java/org/apache/fop/layoutmgr/BreakingAlgorithm.java).
- **C2:** Layout managers mediate between formatting objects and the area tree; child managers produce areas while retaining break-related state. The design discussion also explains why forward references complicate page lifetime and memory reclamation. [Layout design](https://xmlgraphics.apache.org/fop/dev/design/layout.html). Some design discussion is historical; the linked implementation is the stronger evidence for the current breaker.

### 13. [flyingsaucerproject/flyingsaucer](https://github.com/flyingsaucerproject/flyingsaucer)

**Language / role:** Java; a CSS/XHTML layout engine with Swing, PDF, and image-oriented integrations. The selected implementation is flying-saucer-core, rather than optional browser-based alternatives.

- **C1:** BoxBuilder converts DOM structure into valid formatting structure: it normalizes whitespace, inserts anonymous boxes, handles generated content, and treats table columns and out-of-flow elements specially. These transformations preserve CSS box-tree invariants that are not present directly in the input DOM. [BoxBuilder](https://github.com/flyingsaucerproject/flyingsaucer/blob/main/flying-saucer-core/src/main/java/org/xhtmlrenderer/layout/BoxBuilder.java).
- **C2:** Inline/block/table construction lives in the common rendering core, which can feed different display/output integrations. It is a good entry point for studying why parsing a document, constructing its layout representation, and painting it are separate responsibilities even in a comparatively focused renderer.

### 14. [openhtmltopdf/openhtmltopdf](https://github.com/openhtmltopdf/openhtmltopdf)

**Language / role:** Java; an HTML/CSS-to-PDF engine with a PDFBox backend. **Substantive community continuation** of danfickle/openhtmltopdf, itself derived from Flying Saucer. Only the continuation is counted here; its own evolution and PDF-focused behavior justify examining it separately from Flying Saucer.

- **C1:** Block layout saves and restores state when retrying content under page-break avoidance rules, then can drop an unsatisfiable rule. This is an explicit recovery policy for competing pagination constraints. [BlockBoxing](https://github.com/openhtmltopdf/openhtmltopdf/blob/main/openhtmltopdf-core/src/main/java/com/openhtmltopdf/layout/BlockBoxing.java).
- **C3:** Retry permissions limit nested reflow attempts, addressing the work explosion that naive recursive retries could cause. This is an identifiable performance constraint embedded in understandable control flow.

The project's own history records the community continuation, PDFBox 3 migration, selector-performance work, and JVM testing across multiple versions. Its PDF accessibility and conformance work are additional reasons it is more than a renamed fork. [Continuation and release history](https://github.com/openhtmltopdf/openhtmltopdf/blob/main/README.md).

### 15. [dompdf/dompdf](https://github.com/dompdf/dompdf)

**Language / role:** PHP; an HTML/CSS-to-PDF renderer implementing layout in PHP. A useful counterpoint to browser engines and native renderers, especially for inspecting how CSS constraints are organized in an application-library setting.

- **C1:** Block reflow resolves automatic widths and margins, shrink-to-fit sizing, minimum/maximum intrinsic widths, and overconstrained combinations. Distinct cases for normal blocks, floats, and inline blocks show why apparently simple width arithmetic is a semantic algorithm. [Block reflower](https://github.com/dompdf/dompdf/blob/master/src/FrameReflower/Block.php).
- **C2:** DOM nodes acquire frames and styles; display-specific decorators add behavior; positioner and reflower strategies handle geometry; output adapters handle rendering. The main class documents constraints flowing downward and resolved sizes upward, including the special multipass treatment of tables. [Architecture in Dompdf.php](https://github.com/dompdf/dompdf/blob/master/src/Dompdf.php).

Its repository documents layout limitations, including table rows that must fit on a page. Inclusion is not a claim of complete browser CSS compatibility.

## Composable document and PDF layout libraries

### 16. [brechtm/rinohtype](https://github.com/brechtm/rinohtype)

**Language / role:** Python; structured-document typesetting to PDF, including Sphinx integration, templates, and stylesheets. Study continuation-oriented page composition rather than HTML compatibility.

- **C1:** Layout uses explicit continuation state when a flowable reaches the end of a container, and a separate reflow signal for changes such as float placement. Placement and fit decisions are distinct, so partially attempted layout has state that must be carried or discarded correctly. [Container and flow implementation](https://github.com/brechtm/rinohtype/blob/master/src/rinoh/layout.py).
- **C2:** Containers, expanding containers, virtual containers, and chains provide reusable ways to arrange content independently of particular document templates. The relationship between these objects and flowables is useful for studying page filling across multiple regions.

The project describes itself as beta. Its requested future work includes widow/orphan control and Knuth–Plass line breaking; those are not counted as implemented capabilities in this selection.

### 17. [prawnpdf/prawn](https://github.com/prawnpdf/prawn)

**Language / role:** Ruby; a programmable PDF library with substantive text wrapping and bounded text layout. It is a lower-level composition toolkit, rather than a complete declarative publishing system.

- **C1:** Formatted text boxes support measuring without drawing, return unplaced text, track whether content fits, and offer different overflow policies. Font changes, fallback fonts, direction, and wrapping decisions must remain consistent between measurement and actual rendering. [Formatted text box implementation](https://github.com/prawnpdf/prawn/blob/master/lib/prawn/text/formatted/box.rb).
- **C2:** Formatted boxes and wrapping behavior can be composed with the library's bounding regions, grids, and page operations. The box API exposes enough fit information for callers to build their own continuation and overflow policies, making it more reusable than a fixed report renderer.

This is a particularly approachable study of the API contract between a text layout component and a higher-level document composer.

### 18. [gettalong/hexapdf](https://github.com/gettalong/hexapdf)

**Language / role:** Ruby; a broad PDF toolkit, selected specifically for HexaPDF::Layout and its document-composition facilities. Its object-level PDF editing features are outside this category's selection rationale.

- **C1:** Layout distinguishes fitting, splitting, and drawing. Frames maintain available geometric space, including regions left after earlier placements, so a successful fit must consume the right area while preserving valid space for later boxes. [Frame implementation](https://github.com/gettalong/hexapdf/blob/master/lib/hexapdf/layout/frame.rb).
- **C2:** Boxes, styles, frames, and box fitters are separate abstractions; fitters can distribute content across frames, and custom boxes participate in the same protocol. The architecture postpones drawing until placement is settled, permitting measurement and splitting without committing output. [Document layout guide](https://hexapdf.gettalong.org/documentation/document-creation/document-layout.html).

It is a good comparison with Prawn when studying how a higher-level flow engine can sit above PDF drawing primitives.

### 19. [bpampuch/pdfmake](https://github.com/bpampuch/pdfmake)

**Language / role:** JavaScript; a declarative document-definition engine layered on PDF output facilities. Its own measuring, table processing, and pagination logic make it more than a thin PDF-writing wrapper.

- **C1:** The layout builder can rerun pagination after a page-break callback considers neighboring nodes and page positions. It resets coordinates and records break decisions, illustrating the state-management problems introduced when user policies depend on an earlier layout result. [LayoutBuilder](https://github.com/bpampuch/pdfmake/blob/master/src/LayoutBuilder.js).
- **C2:** Document preprocessing, measurement, document context, page-element writing, and table processing have distinct roles. Nested stacks/columns and tables enter a shared pipeline instead of requiring callers to compute all page coordinates themselves. The builder is a useful entry point for following how declarative content acquires dimensions and continuation behavior.

The study focus is this layout pipeline, not the underlying PDF syntax emitter.

### 20. [diegomura/react-pdf](https://github.com/diegomura/react-pdf)

**Language / role:** TypeScript/JavaScript; a React-based PDF document renderer with its own layout pipeline. This is the document-creation project, not the similarly named PDF viewer.

- **C1:** Pagination distinguishes text and view splitting, duplicates fixed elements across pages, handles oversized nonwrapping content, and uses a small geometric tolerance to avoid spurious splits from decimal error. Dynamic content and page-count-dependent rendering require additional layout passes. [Pagination step](https://github.com/diegomura/react-pdf/blob/master/packages/layout/src/steps/resolvePagination.ts).
- **C2:** The pagination step consumes an already structured and measured document tree, keeping React-facing construction, dimensional layout, pagination, and output concerns separable. Its split/relayout helpers make the interaction between flex-style geometry and multipage flow particularly instructive.

An experienced engineer can study the boundary where a general box-layout model needs document-specific continuation, fixed-content, and page-number semantics.

### 21. [QuestPDF/QuestPDF](https://github.com/QuestPDF/QuestPDF)

**Language / role:** C#; a fluent, compositional document-generation engine. Study explicit layout outcomes and resumable element state in the current library subtree.

- **C1:** Column measurement returns distinct empty, wrap, complete, and partial outcomes. Drawing advances the stored child index only for fully rendered children, while negative-space checks and geometric tolerances handle boundary cases. This makes continuation semantics visible rather than implicit in exceptions. [Column implementation](https://github.com/QuestPDF/QuestPDF/blob/main/src/dotnet/library/QuestPDF/Elements/Column.cs).
- **C2:** Column participates in common element and state protocols, so the same measure/draw vocabulary can support other compositional containers.
- **C3:** Layout commands use reusable pooled lists; the implementation explicitly preserves concrete list enumeration to avoid allocations. These are localized performance choices that remain connected to the element's control flow. The surrounding tree separates library code from layout, unit, visual, and other validation projects. [Library subtree](https://github.com/QuestPDF/QuestPDF/tree/main/src/dotnet/library).

### 22. [empira/PDFsharp](https://github.com/empira/PDFsharp)

**Language / role:** C#; the selected subsystem is **MigraDoc**, the higher-level document model and formatter in the PDFsharp monorepo. PDFsharp's lower-level drawing API alone is not the basis for inclusion.

- **C1:** TopDownFormatter carries split format information across areas, handles page-start spacing differently from ordinary flow, collapses margins, and revisits placement when keep constraints interact with area endings. These are concrete pagination semantics that cannot be reduced to a single vertical cursor. [TopDownFormatter](https://github.com/empira/PDFsharp/blob/master/src/foundation/src/MigraDoc/src/MigraDoc.Rendering/Rendering/TopDownFormatter.cs).
- **C2:** An area-provider interface supplies places to lay out content, while document-object renderers handle individual elements and return formatting information. The separation allows a sequence of document objects to flow through different available regions without embedding every object-specific rule in the area provider.

This is a useful study of a document object model, renderer factory, and multipage formatting state working together.

## Interactive document systems with substantial layout engines

### 23. [texmacs/texmacs](https://github.com/texmacs/texmacs)

**Language / role:** C++ and Scheme; an interactive scientific document editor with its own typesetting engine. **Official Subversion mirror**; inspected sources use the svn_mirror branch. It is not merely a graphical front end to TeX.

- **C1:** The page breaker coordinates body text, footnotes, floats, forced breaks, and multicolumn material. Its space model distinguishes minimum, preferred, and maximum heights, exposing constraints that interact when content migrates between regions. [Page-breaker implementation](https://github.com/texmacs/texmacs/blob/svn_mirror/src/Typeset/Page/new_breaker.cpp).
- **C3:** The breaker maintains cumulative height information and caches for uniform/column breaking, alongside predecessor and penalty data for selecting solutions. These data structures make repeated range evaluation and break search inspectable. [Page-breaker state and interface](https://github.com/texmacs/texmacs/blob/svn_mirror/src/Typeset/Page/new_breaker.hpp).

The inspected source also records unresolved cases, including splitting long insertions. Its value is the substantial coupled layout machinery, not a claim that every combination is complete.

### 24. [LibreOffice/core](https://github.com/LibreOffice/core)

**Language / role:** Primarily C++; the selected subsystem is **Writer**, under sw. **Official read-only GitHub mirror**, with development centered on upstream infrastructure. Count the office-suite monorepo once.

- **C1:** Writer distinguishes the document model from layout state, manages nested inline attributes as nonoverlapping portions, and has fields whose values depend on the current pagination. The module guide exposes why editing, formatting, and layout-dependent values must remain synchronized. [Writer architecture and source guide](https://github.com/LibreOffice/core/blob/master/sw/README.md).
- **C3:** Layout actions check for pending input so work can yield to interaction. Painting is limited using changed regions and exclusions for floating frames, linking responsiveness to explicit scheduling and geometry rather than a blanket redraw. [Layout-action implementation](https://github.com/LibreOffice/core/blob/master/sw/source/core/layout/layact.cxx).

This is the largest integration study in the selection: useful for understanding incremental interactive layout and compatibility-driven document complexity, but less suitable as a first small engine to read.

## Coverage, search method, and limitations

Discovery used live web search and then opened repository pages/API metadata plus implementation or design material. The searches were independent of other category reports. More than six distinct discovery formulations were used; representative angles included:

1. Standalone typesetting engines and architecture, including Typst, SILE, and Tectonic.
2. HTML/CSS paged media, including WeasyPrint, Paged.js, and Vivliostyle.
3. Knuth–Plass and document/page-layout libraries in Java and C++.
4. OCaml and functional typesetters, including SATySFi, Patoline, and ANT-related searches.
5. XSL-FO, data-driven XML publishing, and LuaTeX-based systems.
6. Troff-family, Neatroff, and Lout-related systems.
7. Ruby PDF composition, including Prawn and HexaPDF.
8. C# document layout, including QuestPDF and MigraDoc/PDFsharp.
9. JavaScript declarative document renderers and React-based pagination.
10. PHP HTML-to-PDF engines and interactive publishing/editor engines, including Scribus and TeXmacs.

Later queries increasingly returned these same engines, PDF wrappers, tutorials, and generic document converters, so the selection stopped at 24 rather than padding it. The retained projects span Rust, C/C++, WEB/Pascal, Lua, Go, OCaml, Python, Java, JavaScript/TypeScript, Ruby, PHP, C#, and Scheme integrations, and range from compact formatters to large office-suite subsystems.

**Important boundaries and exclusions:** General-purpose browser engines and standalone glyph-shaping/font-rasterization libraries were left outside this document/page-engine focus. Conversion tools, templates, and wrappers without substantial layout machinery were not retained. Scribus was investigated but excluded because the inspected [scribusproject/scribus repository](https://github.com/scribusproject/scribus) explicitly identifies itself as an unsupported, manually updated community mirror; an official substantive GitHub mirror was not verified. Searches for ANT and Lout did not establish a suitable official GitHub source with enough independently inspected implementation evidence, so no repository identity is guessed. The original danfickle OpenHTMLtoPDF repository is not separately counted alongside its community continuation. TeX Live, TeXmacs, and LibreOffice are clearly marked as official mirrors; Patoline is marked historical rather than presented as currently maintained.

Every retained repository had its exact GitHub identity checked and at least one additional primary implementation/design source opened beyond the repository overview. Source APIs and design descriptions support the architectural claims; criterion assignments and recommendations about what to study are grounded inferences. No repositories were cloned, candidate code executed, dependencies installed, or benchmark comparisons performed. Status observations and moving-branch links can change after the research date. The report is a selection guide, not an exhaustive inventory, maintenance guarantee, or judgment that all components in any repository have equal quality.
