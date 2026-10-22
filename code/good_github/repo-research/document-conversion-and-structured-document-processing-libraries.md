# Document conversion and structured document processing libraries

Research date: 2026-10-09

This report selects 25 GitHub repositories with substantial implementations of document conversion, document object models, publishing pipelines, layout, or structured extraction. It covers semantic markup, Office/OpenDocument packages, scientific documents, ebooks, and PDF internals. Libraries embedded in larger applications are included only where an identifiable conversion subsystem is worth studying. Generic XML parsers, desktop editors as a whole, hosted conversion APIs, and thin command wrappers are outside the scope.

The criteria are selection judgments grounded in the linked primary material, not certifications that every component is exemplary. Each repository heading links to its verified GitHub location; the links within each entry provide one or two principal reading entry points, with occasional supplementary evidence.

- **C1 — Difficult correctness:** nontrivial invariants, concurrency, numerical or document semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial models, interfaces, or processing stages supporting multiple applications.
- **C3 — Performance with structure:** explicit resource or throughput constraints addressed through understandable architectural choices.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or management of implementation complexity. Age alone does not qualify.

## Semantic conversion and publishing pipelines

### 1. [jgm/pandoc](https://github.com/jgm/pandoc)

**Haskell; general document conversion library and CLI.** Study how a shared intermediate representation prevents a many-format converter from becoming a collection of pairwise translators. Its own documentation explicitly acknowledges that the model cannot preserve every feature of richer formats; this is a useful example of making conversion loss part of the contract.

- **C2:** Readers and writers meet at a document AST; Lua and JSON filters add transformations independently of either endpoint. Block, inline, and metadata representations support transformations across otherwise unrelated formats. Start with the [filter architecture and worked transformations](https://pandoc.org/filters.html).
- **C1:** The same guide demonstrates why headings inside code/comments, alternative heading syntax, nested emphasis, and mathematical delimiters require structural parsing. The repository documents the resulting fidelity boundary, including complex tables and formatting details, rather than promising universal round trips. See the [conversion model and limitations](https://github.com/jgm/pandoc#pandoc).

### 2. [asciidoctor/asciidoctor](https://github.com/asciidoctor/asciidoctor)

**Ruby; AsciiDoc document processor and conversion framework.** An instructive codebase for extending a markup language while preserving the stages at which source text acquires meaning. The core supplies HTML, DocBook, and man-page conversion; additional output backends belong to its broader ecosystem.

- **C2:** The document model exposes sections, blocks, lists, and list items to registered processors. Extensions can inspect and replace structural nodes through a common API, as shown in the [tree processor guide](https://docs.asciidoctor.org/asciidoctor/latest/extensions/tree-processor/).
- **C1:** Tree processors run after block parsing but before inline interpretation. Replacing node text therefore changes material that will still be parsed. The documented sequencing and escaping in the worked processor make this a concrete study of phase-sensitive transformation correctness, not merely callback registration. The same [guide](https://docs.asciidoctor.org/asciidoctor/latest/extensions/tree-processor/) explains the boundary.

### 3. [unifiedjs/unified](https://github.com/unifiedjs/unified)

**JavaScript with TypeScript-facing types; syntax-tree processing framework.** This is the core processor behind the remark/rehype ecosystems, counted once rather than listing numerous small adapters. Study the lifecycle of a configurable processor that can cross Markdown, HTML, and other tree representations.

- **C2:** Parsing, transformation, and compilation are separate phases; plugins and presets configure processors, while a virtual file carries content and diagnostics. The [API and processing overview](https://github.com/unifiedjs/unified#overview) includes a Markdown-to-HTML pipeline and permits compilers to return non-text results.
- **C1:** Frozen processors prevent configuration changes from leaking into other module users. The implementation also checks that synchronous entry points actually finish synchronously and propagates errors through callback/promise execution. Read `freeze`, `process`, and `processSync` in the [processor implementation](https://github.com/unifiedjs/unified/blob/main/lib/index.js).

### 4. [dita-ot/dita-ot](https://github.com/dita-ot/dita-ot)

**Java, XSLT, and Ant; DITA publishing engine.** Particularly useful for studying transformations across a graph of reusable topics and maps, where copying XML is insufficient to preserve document meaning.

- **C2:** Shared preprocessing stages precede output-specific transformations, with stages represented as Ant targets. This provides reusable processing across deliverables rather than duplicating content-resolution logic in every writer. See the [preprocessing architecture](https://www.dita-ot.org/dev/reference/preprocessing).
- **C1:** Content-reference expansion changes IDs to keep them unique in the receiving topic and rewrites accompanying cross-references to preserve their targets. The [content-reference implementation guide](https://www.dita-ot.org/dev/reference/preprocess-conref.html) supplies concrete before/after XML and identifies the XSLT stage responsible. This is a strong example of identity and referential-integrity invariants during document reuse.

### 5. [brucemiller/LaTeXML](https://github.com/brucemiller/LaTeXML)

**Perl; TeX/LaTeX conversion to XML, HTML, MathML, EPUB, and related formats.** Study semantic conversion of an executable markup language, including how to preserve higher-level constructs instead of merely reproducing their rendered appearance.

- **C1:** Tokenization depends on current TeX category codes, macro expansion and primitive execution are distinct, and a state object implements TeX scoping. XML construction must also open or close elements according to the document model. The [architecture chapter](https://math.nist.gov/~BMiller/LaTeXML/manual/architecture/latexml/) explains these interacting semantics.
- **C2:** Replaceable bindings, constructors, document-model declarations, rewrite rules, and a separate math-parsing stage give users several levels of customization. The same [architecture chapter](https://math.nist.gov/~BMiller/LaTeXML/manual/architecture/latexml/) maps these concepts to `Mouth`, `Gullet`, `Stomach`, `Document`, and `Rewrite`, making it a useful route into the implementation.

### 6. [kovidgoyal/calibre](https://github.com/kovidgoyal/calibre)

**Primarily Python with native components; ebook conversion subsystem within a larger application.** The relevant subsystem is the input/output plugin and intermediate XHTML transformation pipeline, not the library-management GUI. Study how one intermediate form supports many ebook formats and reader-specific presentation constraints.

- **C2:** Input plugins produce XHTML, shared transforms process it, and output plugins package the target format. Metadata insertion, chapter detection, CSS changes, and font adjustment become reusable stages. The [conversion manual](https://manual.calibre-ebook.com/conversion.html) explains this architecture.
- **C1:** Structural detection and font-size normalization have explicit rules and can change document meaning or hierarchy when heuristics misfire. The pipeline exposes intermediate `input`, `parsed`, `structure`, and `processed` artifacts for locating conversion errors. The [same manual](https://manual.calibre-ebook.com/conversion.html) documents these inspection boundaries and format-dependent fidelity limitations.

## Office and OpenDocument object models

### 7. [dotnet/Open-XML-SDK](https://github.com/dotnet/Open-XML-SDK)

**C#; low-level OOXML package and markup SDK.** Study how a large standardized schema becomes a typed programming interface without concealing the underlying part/relationship structure. It is a document manipulation SDK, not a Word-compatible pagination engine.

- **C2:** OPC packages, typed schema objects, and LINQ-based traversal provide reusable access to Word, Excel, and PowerPoint document structures. Microsoft's [SDK architecture overview](https://learn.microsoft.com/en-us/office/open-xml/about-the-open-xml-sdk) connects package parts, relationships, and the object model.
- **C1:** Validation covers format variants, while Strict-format loading maps namespaces into the SDK representation. Relationships and content types must remain consistent as parts are manipulated. The [overview](https://learn.microsoft.com/en-us/office/open-xml/about-the-open-xml-sdk) describes these mechanisms; the [repository's known issues](https://github.com/dotnet/Open-XML-SDK#known-issues) also document ZIP-related memory limitations rather than implying uniformly streaming behavior.

### 8. [apache/poi](https://github.com/apache/poi)

**Java; Office document APIs. Official Apache GitBox mirror.** Counted once; the most relevant subsystems here are XWPF/HWPF for Word documents, OpenXML4J for OOXML packaging, and the shared compound-document infrastructure.

- **C2:** The package/part layer implements OPC independently of higher-level document objects. XWPF then presents bodies, paragraphs, runs, tables, and headers/footers. Read the [OpenXML4J overview](https://poi.apache.org/components/oxml4j/index.html) followed by the [XWPF guide](https://poi.apache.org/components/document/quick-guide-xwpf.html).
- **C1:** Text edits operate on runs, and tabs and carriage returns require explicit structural operations. First/even/odd headers are separate cases. These details expose correctness problems hidden by plain string replacement. The XWPF guide also candidly identifies incomplete high-level coverage and the need to descend into XMLBeans for some operations, and directs readers to unit tests for examples.

### 9. [plutext/docx4j](https://github.com/plutext/docx4j)

**Java; JAXB-based OOXML manipulation and conversion.** Useful for comparing a schema-oriented model with more convenience-oriented Office APIs. Concentrate on packaging, generated JAXB content, and cross-part document operations.

- **C2:** The maintainer's [architecture explanation](https://www.docx4java.org/forums/docx-java-f6/architecture-overview-t51.html) separates package/parts, JAXB content trees, and higher-level models such as numbering and headers/footers. This gives a concrete rule for placing functionality without editing generated schema classes.
- **C4:** That 2009 design account can be compared with the [current repository's migration notes](https://github.com/plutext/docx4j): Java/JAXB compatibility lines, migration from `javax` to `jakarta`, build-time schema generation, and consolidation of content-list APIs show sustained complexity management. The notes explicitly identify the Java 8 line as legacy and unsupported. PDF export involves alternative strategies and should not be mistaken for one uniform rendering path.

### 10. [python-openxml/python-docx](https://github.com/python-openxml/python-docx)

**Python; creation and modification of DOCX files.** A focused study of how friendly document APIs encode awkward WordprocessingML semantics. Its analysis documentation is particularly valuable because it derives behavior from concrete XML and Word examples.

- **C1:** Cell merges must be rectangular; a merge enclosing prior spans must include those spans completely. Content concatenation, dimension accumulation, and horizontal versus vertical continuation require distinct rules. See the [table-merge analysis](https://python-docx.readthedocs.io/en/latest/dev/analysis/features/table/cell-merge.html).
- **C2:** Table, row, column, and cell abstractions expose access through layout-grid coordinates, including positions inside merged spans. The [same analysis](https://python-docx.readthedocs.io/en/latest/dev/analysis/features/table/cell-merge.html) shows how these abstractions make a nonuniform XML table usable for construction and inspection. This is a manipulation library; no general DOCX-to-PDF fidelity claim is implied.

### 11. [mwilliamson/mammoth.js](https://github.com/mwilliamson/mammoth.js)

**JavaScript; semantic DOCX-to-HTML conversion.** Study an intentionally selective converter: Word styles become meaningful HTML structures, while visual fidelity is not its central contract.

- **C2:** Style maps, document-node converters, image callbacks, and HTML path composition allow the same conversion core to serve different web publishing conventions. The [repository's style-map/API guide](https://github.com/mwilliamson/mammoth.js#custom-style-map) explains the public model.
- **C1:** Conversion tracks notes/comments, builds their identifiers, resolves deferred nodes before serialization, and converts image failures into reported messages. The [document-to-HTML implementation](https://github.com/mwilliamson/mammoth.js/blob/master/lib/document-to-html.js) exposes this failure handling and ordering. The repository also explicitly says generated HTML is not sanitized, an essential boundary when assessing correctness for untrusted documents.

### 12. [PHPOffice/PHPWord](https://github.com/PHPOffice/PHPWord)

**PHP; word-processing document model, readers, writers, and template processing.** Study both construction from semantic elements and modification of existing OOXML templates, which have different implementation pressures.

- **C2:** Writer selection reuses a document model across Word2007, ODF text, RTF, and HTML. PDF output passes through HTML and an external renderer, with a callback at the intermediate stage. The [writer guide](https://phpoffice.github.io/PHPWord/usage/writers.html) makes these boundaries explicit.
- **C1:** `TemplateProcessor` handles document parts and their relationships separately, repairs macros broken across XML markup, processes headers and footers as well as the body, and controls encoding/escaping during substitutions. Read the [template processor source](https://github.com/PHPOffice/PHPWord/blob/master/src/PhpWord/TemplateProcessor.php). These are concrete examples of why document templating cannot safely be modeled as replacing bytes in one text file.

### 13. [eea/odfpy](https://github.com/eea/odfpy)

**Python; OpenDocument 1.2 manipulation library and utilities.** A smaller, schema-oriented counterpart to the OOXML projects. Study the reusable `odf` package; the same repository contains converters, metadata utilities, and linting tools.

- **C1:** Its element layer checks permitted child relationships against grammar tables, raises dedicated illegal-child/text exceptions, maintains parent/sibling links, and updates owner-document caches on mutation. Grammar checking can be explicitly disabled, so it is not an unconditional validity guarantee. Read the [element implementation](https://github.com/eea/odfpy/blob/master/odf/element.py).
- **C2:** The common node and element abstractions supply namespace-aware XML serialization and mutation for multiple ODF utilities. The [repository overview and source layout](https://github.com/eea/odfpy) identify these consumers and the shared library. Its [GitHub releases page](https://github.com/eea/odfpy/releases) has no published releases; inclusion is based on implementation substance, with no claim of a current release cadence.

## Paginated document rendering

### 14. [apache/xmlgraphics-fop](https://github.com/apache/xmlgraphics-fop)

**Java; embeddable XSL-FO formatter.** Study the transition from semantic formatting objects to physical pages and then to multiple output backends. The Apache project explicitly lists this as its [official Git repository](https://xmlgraphics.apache.org/repo.html).

- **C2:** Parsing, property refinement, layout, area trees, and renderers are distinct architectural layers. The [design overview](https://xmlgraphics.apache.org/fop/dev/design/) explains their contracts and which structural outputs bypass pagination.
- **C3:** Memory is an explicit design constraint for large documents and live document generation. The architecture permits stages to overlap rather than requiring every preceding representation to finish first, and discusses serialization and page-sequence boundaries. These are documented design responses, not benchmark claims. The same [design overview](https://xmlgraphics.apache.org/fop/dev/design/) is the best starting point; parts are historical design material, which the page itself cautions readers to interpret alongside current code.

### 15. [Kozea/WeasyPrint](https://github.com/Kozea/WeasyPrint)

**Python; HTML/CSS-to-PDF layout engine.** Study a renderer designed for static paged documents. It offers a contrasting approach to FOP, beginning with CSS cascade and formatting rules rather than XSL-FO.

- **C1:** The cascade resolves origin, importance, specificity, and source order; computed values must still distinguish percentages from absolute lengths. Layout and stacking then determine the page representation. The [source architecture guide](https://doc.courtbouillon.org/weasyprint/stable/going_further.html) explains these semantic dependencies.
- **C2:** HTML parsing, CSS validation/computation, formatting boxes, page layout, drawing, and PDF metadata form separate stages. The [same guide](https://doc.courtbouillon.org/weasyprint/stable/going_further.html) maps them to source modules. It explicitly prioritizes maintainability and specification fidelity over speed, so this selection does not assign C3 merely because it is a rendering engine.

## Detection, extraction, and document understanding

### 16. [apache/tika](https://github.com/apache/tika)

**Java; document detection and normalized content/metadata extraction.** Study the orchestration layer around heterogeneous parsers, particularly where application-level failure containment must supplement library APIs.

- **C2:** A parser consumes a stream and emits XHTML SAX events plus metadata; parse context injects strategies and delegates for embedded packages. Handlers adapt that event stream to different consumers, and auto-detection chooses an appropriate parser. See the [Parser API architecture](https://tika.apache.org/3.2.3/parser.html), a versioned description of the established interface.
- **C1:** The [security model](https://tika.apache.org/security-model.html) distinguishes untrusted files, callers, and configuration. It documents parser crashes/hangs and resource exhaustion, with process-isolation/time-limit mechanisms in the surrounding toolkit. Extraction output remains untrusted and is not sanitization. This explicit failure boundary is a major engineering study opportunity, not evidence that arbitrary parsing is intrinsically safe.

### 17. [docling-project/docling](https://github.com/docling-project/docling)

**Python; format conversion and document understanding pipelines.** Study the combination of deterministic backends, model-driven layout/OCR/table stages, and a common structured result.

- **C2:** `DoclingDocument` separates content items from hierarchy, records provenance and bounding boxes, and uses JSON pointers for parent/child references. Body order and separate furniture represent different semantic roles. Start with the [document representation guide](https://docling-project.github.io/docling/concepts/docling_document/).
- **C1 and C3:** The [standard PDF pipeline](https://github.com/docling-project/docling/blob/main/docling/pipeline/standard_pdf_pipeline.py) implements bounded queues, batch processing, per-run identifiers, timeout/failure records, queue closure, and a guard against models returning the wrong number of pages. These are concrete throughput and concurrency concerns. Its shutdown code also acknowledges that a stuck worker can outlive the join timeout, so the design should be studied together with its remaining failure limits.

### 18. [Unstructured-IO/unstructured](https://github.com/Unstructured-IO/unstructured)

**Python; document partitioning into typed elements and metadata.** The selection concerns the open-source library, not the separate hosted platform. Study how a common element interface coexists with format-specific extraction policies.

- **C2:** Automatic dispatch and explicit per-format functions produce elements such as titles, narrative text, and list items. File-type-specific options remain available where the general interface would erase useful distinctions. See the [partitioning API guide](https://docs.unstructured.io/open-source/core-functionality/partitioning).
- **C1 and C3:** PDF strategies distinguish native text extraction, layout inference, and OCR, with explicit fallbacks when text or dependencies are unavailable. The guide documents the tradeoff between speed and classification detail and acknowledges multi-column ordering limitations. Its [PDF strategy section](https://docs.unstructured.io/open-source/core-functionality/partitioning) is useful evidence of failure-aware routing rather than a claim that one model handles every input uniformly.

### 19. [grobidOrg/grobid](https://github.com/grobidOrg/grobid)

**Java with machine-learning components; scholarly document conversion to TEI XML.** The former `kermitt2/grobid` location redirects here. Study the core segmentation/extraction engine; current documentation emphasizes service operation and labels older Java-library usage instructions as deprecated.

- **C2:** A cascade of specialized sequence-labeling models separates document segmentation, headers, references, names, dates, and other structures. Models can vary in algorithm, tokenizer, and features while contributing to a shared TEI result. Read [How GROBID works](https://grobid.readthedocs.io/en/latest/Principles/).
- **C3:** Whole-document segmentation works at line level, while more expensive token-level models process smaller regions. The design explicitly balances runtime, memory, training-data requirements, and accuracy; separating models also reduces interference between common and rare labels. The [same architecture account](https://grobid.readthedocs.io/en/latest/Principles/) supports these choices without requiring a universal speed or accuracy claim.

## PDF structure, transformation, and extraction primitives

### 20. [pdfminer/pdfminer.six](https://github.com/pdfminer/pdfminer.six)

**Python; PDF interpretation and layout-based extraction.** A substantive community continuation of PDFMiner, counted once and not alongside its ancestor. Study how page-level graphical information is reconstructed into a reading hierarchy.

- **C1:** Character boxes are grouped into lines, lines into boxes, and boxes into a hierarchy using relative geometric thresholds. Word spacing and vertical text need explicit rules. The [layout-analysis explanation](https://pdfminersix.readthedocs.io/en/latest/topic/converting_pdf_to_text.html) exposes the assumptions and parameter interactions.
- **C2:** Configurable layout parameters and the resulting hierarchy of layout objects provide reusable access beyond flat text, as described in that guide.
- **C4:** The [changelog](https://github.com/pdfminer/pdfminer.six/blob/master/CHANGELOG.md) documents years of distinct evolution: a pytest/CI migration in 2022, fuzzing integration in 2024, and subsequent Python compatibility, malformed-input, and CMap-storage changes. These establish substantive continued development of the fork rather than merely a renamed copy.

### 21. [py-pdf/pypdf](https://github.com/py-pdf/pypdf)

**Python; PDF object and page manipulation.** Study graph-preserving document assembly, especially why a page is not an independently copyable blob.

- **C1:** Merging must manage form-field name collisions, named destinations, recursive indirect-object cloning, and page rotation. Cloning caches preserve object identity, while excluding selected dictionary keys can prevent copying unexpectedly large linked structures. The [merging and cloning guide](https://pypdf.readthedocs.io/en/stable/user/merging-pdfs.html) documents these cases.
- **C2:** Reader, writer, page, and generic PDF-object APIs support both high-level append/merge workflows and explicit cloning. The [same guide](https://pypdf.readthedocs.io/en/stable/user/merging-pdfs.html) shows shared mechanisms underneath those entry points. Its recursion-limit discussion also makes a practical failure mode visible without implying bounded-memory processing.

### 22. [apache/pdfbox](https://github.com/apache/pdfbox)

**Java; PDF document model, extraction, rendering, and manipulation. Official Apache mirror.** Study the PDFBox subsystem and its IO layer; the repository is counted once, including its related font and metadata components.

- **C2:** Random-access readers and stream-cache factories separate document operations from storage choices. Memory, buffered-file, memory-mapped, and scratch-file approaches are exposed through interfaces. The [3.0 migration guide](https://pdfbox.apache.org/3.0/migration.html) explains the refactoring and extension contracts.
- **C1 and C3:** On-demand parsing reduces initial loading, but later traversal can still load much of the document. Reader/cache implementations have thread-safety requirements; the guide also explains why saving over the source file can corrupt lazily read content and how Windows memory-map cleanup needs special treatment. These concrete lifecycle and memory constraints make the [migration guide](https://pdfbox.apache.org/3.0/migration.html) unusually useful architectural evidence.

### 23. [qpdf/qpdf](https://github.com/qpdf/qpdf)

**C++; content-preserving PDF transformation library and CLI.** Study the boundary between object-graph manipulation and byte-level bookkeeping. qpdf deliberately expects callers to understand PDF objects while hiding storage positions and encoding details.

- **C1:** Direct and indirect objects share a handle interface; indirect objects resolve when accessed. Reading damaged input involves explicit recovery policies, and the documentation warns that successful recovery is not proof of conformity. See [Design and Library Notes](https://qpdf.readthedocs.io/en/stable/design.html).
- **C2 and C3:** Shared object handles, separate document/writer responsibilities, and lazy object resolution support many transformations without requiring every caller to implement cross-reference management. The [same design notes](https://qpdf.readthedocs.io/en/stable/design.html) explain seekable input versus potentially nonseekable output, including linearized output. The document is an architectural roadmap and explicitly defers to implementation/tests where details differ.

### 24. [pdfcpu/pdfcpu](https://github.com/pdfcpu/pdfcpu)

**Go; PDF validation and document transformation library with CLI.** Study a broad operation API whose file-oriented commands share an integration layer based on Go IO interfaces.

- **C2:** File APIs delegate to `io.ReadSeeker`/`io.Writer` APIs; reading, validation, configuration, and writing are organized around a shared PDF context. The [API implementation](https://github.com/pdfcpu/pdfcpu/blob/master/pkg/api/api.go) documents this layering and implements cancellation checks and explicit missing-context errors.
- **C1:** [Validation documentation](https://pdfcpu.io/core/validate/) distinguishes strict rules, curated relaxed compatibility exceptions, and lower-level reader recovery. It explains structured divergence reports and explicitly limits PDF 2.0 coverage. This is a useful study of separating readable input, accepted compatibility deviations, and standards compliance without conflating them.

### 25. [J-F-Liu/lopdf](https://github.com/J-F-Liu/lopdf)

**Rust; low-level PDF document manipulation.** Study a typed object/stream model coupled to a parser that must survive cyclic and malformed reference graphs. The verified current source branch is `main`.

- **C1:** The [reader implementation](https://github.com/J-F-Liu/lopdf/blob/main/src/reader.rs) tracks already-seen references, bounds page-tree depth, checks offsets against buffer length, and detects repeated previous-cross-reference offsets. It distinguishes cycles from long acyclic chains, an important adversarial-input detail.
- **C2 and C3:** Document/object/stream APIs and configurable loading support multiple transformation workflows. The [crate API documentation](https://docs.rs/lopdf/latest/lopdf/) describes optional asynchronous loading and Rayon-based parallel object-stream/cross-reference parsing. The reader also preallocates from file size and offers a metadata-oriented path; these are specific resource choices, not a claim that the entire library streams input or uses constant memory.

## Coverage and search notes

Discovery used more than six distinct live search formulations. The main angles were universal converters and AST filters; DITA/DocBook publishing; Java and .NET Office package models; DOCX-to-HTML and ODF utilities; Rust/Go PDF internals; model-driven document extraction; PHP/RTF readers and writers; legacy C++/ebook conversion; and TeX/LaTeX semantic conversion. Follow-up queries targeted reference rewriting, lifecycle invariants, parser fallbacks, architecture documents, and migration history. Later broad queries increasingly returned already-covered projects, application wrappers, or unofficial mirrors, while the TeX query added a distinct architecture and language.

Repository pages were opened for every retained project, followed by separately opened implementation or documentation material; search snippets alone were not used as verification. The selection spans Haskell, Ruby, JavaScript, Perl, Python, Java, C#, PHP, C++, Go, Rust, and XSLT-based processing. Smaller projects such as odfpy and Mammoth are included for specific implementation lessons rather than popularity.

Important exclusions and limits:

- **Hosting eligibility:** DocBook xslTNG's [GitHub notice](https://github.com/docbook/xslTNG) says development moved to Codeberg and that no further releases will appear there; an ongoing official GitHub mirror was not established, so it was excluded. Docutils' [official repository documentation](https://docutils.sourceforge.io/docs/dev/repository.html) describes GitHub copies as third-party mirrors; it was also excluded. Search results for legacy C++ format importers frequently led to third-party mirrors, which were not treated as canonical projects.
- **Overlap:** Unified represents the shared processor framework instead of separately counting remark and numerous plugins. PDFMiner's ancestor, PDF conversion wrappers, generated bindings, and hosted service SDKs were not added as independent entries. Calibre is included specifically for its conversion subsystem.
- **Evidence boundaries:** No candidate code was executed, dependencies installed, repositories cloned, or benchmark results independently reproduced. Criteria describe observable design/implementation properties. A complex parser or a documented safety check is not proof that all malformed inputs are handled correctly.
- **Maintenance and versioning:** This is not a blanket endorsement of current maintenance. Odfpy's lack of GitHub releases is called out; historical architecture and migration documents are labeled where relevant. Some current documentation URLs and source branches are moving targets, and occasional fetch failures were resolved through accessible official pages or raw source. C4 is assigned only where the inspected material demonstrates evolution and compatibility/testing work across years.
