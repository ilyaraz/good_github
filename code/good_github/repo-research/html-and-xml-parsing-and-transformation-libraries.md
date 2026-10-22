# HTML and XML parsing and transformation libraries

Research date: **2026-10-09**.

This report selects 27 GitHub repositories implementing HTML/XML parsers, document models, streaming rewriters, and XPath/XSLT or functional transformation engines. It includes native implementations and substantial language integrations whose ownership and API layers provide independent engineering lessons. It excludes applications that merely consume markup, thin generated bindings, and duplicate forks. The emphasis is on what an experienced engineer can learn from a codebase, not on ranking packages for every production workload.

Criteria used below:

- **C1 — Difficult correctness:** structural invariants, language semantics, concurrency, adversarial input, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or models serving multiple applications.
- **C3 — Performance with structure:** concrete memory, latency, or throughput constraints addressed by identifiable architectural mechanisms.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility work, testing, or deliberate complexity management.

Criterion assignments are grounded engineering judgments about the cited material. They do not imply that every component is exemplary or that standards conformance and security have been independently certified.

## XML parsing engines and document models

### 1. [GNOME/libxml2](https://github.com/GNOME/libxml2)

**Language / role:** C; XML parsing, HTML parsing, document trees, validation, and XPath. **Official read-only GitHub mirror** of GNOME GitLab.

Study a large parser toolkit in which several access styles share document and parser-context infrastructure. Its value includes seeing how resource accounting is added to a complex existing implementation.

- **C1:** `xmlParserEntityCheck` accounts for expanded entity data against consumed input, handles arithmetic saturation, and raises a resource-limit error; nearby expansion code detects recursive entities. These are concrete defenses around adversarial expansion, not merely syntax recognition. [Parser implementation](https://github.com/GNOME/libxml2/blob/master/parser.c).
- **C2:** The toolkit exposes push parsing, SAX, reader/writer interfaces, tree operations, XPath, and schema-related modules through separately configurable subsystems. The repository describes these interfaces and their build boundaries. [Repository documentation](https://github.com/GNOME/libxml2#readme).

Boundary: the current upstream README expressly discourages processing untrusted data. Inclusion recognizes architectural substance, not a blanket security recommendation.

### 2. [libexpat/libexpat](https://github.com/libexpat/libexpat)

**Language / role:** C; incremental, callback-driven XML parser.

Expat is a strong study in maintaining parser state across arbitrarily divided input while leaving document storage to the caller.

- **C1:** The API makes external-entity processing, parser suspension/resumption, entity-amplification protection, and reparse deferral explicit. These mechanisms expose the difficult boundary between incremental parsing and resource exhaustion. [API reference](https://libexpat.github.io/doc/api/latest/).
- **C2:** Independently registered handlers for elements, character data, namespaces, declarations, and entities let applications construct trees, extract records, or validate application rules without adopting a built-in DOM. The same reference explains the callback and buffer contracts.
- **C3:** Feeding input in pieces allows processing documents larger than available memory; callers can supply input buffers rather than first assembling an entire document. This is a structural memory advantage, not a cross-library speed claim.

The [change history](https://github.com/libexpat/libexpat/blob/master/expat/Changes) is a useful second entry point for allocation failures, integer-boundary checks, and encoding fixes.

### 3. [apache/xerces-c](https://github.com/apache/xerces-c)

**Language / role:** C++; validating XML parser with SAX and DOM interfaces.

Study grammar management as a reusable subsystem rather than treating validation as a one-shot parser option.

- **C2:** Xerces provides both SAX and DOM access and lets applications preparse grammars, retain them in a grammar pool, and use them in subsequent document parses. The guide demonstrates both parser styles. [Programming guide](https://xerces.apache.org/xerces-c/program-others-3.html).
- **C3:** Grammar caching avoids rebuilding schema/DTD structures for each document. The guide distinguishes loading a grammar explicitly from caching grammars encountered during parsing, and documents restrictions such as internal DTD subsets. This makes the performance mechanism and its semantic boundaries visible.

This selection concerns the C++ parser and validation library, not the separate Xerces Java implementation. Start with the guide's **Pre-parsing Grammar and Grammar Caching** section and follow its concrete parser calls.

### 4. [zeux/pugixml](https://github.com/zeux/pugixml)

**Language / role:** C++; mutable XML tree, parser, serializer, and XPath 1.0 engine.

Pugixml is especially instructive for the relationship between a convenient node API and a specialized allocator.

- **C2:** A mutable tree interface, traversal, serialization, Unicode conversion, and compiled XPath queries form a cohesive reusable library. Its manual explicitly separates structural tree integrity from XML validity. [Manual](https://pugixml.org/docs/manual.html).
- **C3:** Document objects are allocated within pages; parsing can retain names and values in the input buffer, and compact mode trades access efficiency for smaller structures. The manual explains reclamation limitations, while `xml_memory_page` and the allocator make the mechanism inspectable. [Implementation](https://github.com/zeux/pugixml/blob/master/src/pugixml.cpp).
- **C4:** The manual's dated changelog spans many release generations and records API adjustments, XPath correctness fixes, compiler compatibility, and allocator changes.

Boundary: it is an in-memory, non-validating parser; it is not a streaming or schema-validation substitute.

### 5. [leethomason/tinyxml2](https://github.com/leethomason/tinyxml2)

**Language / role:** C++; compact embeddable XML DOM parser and writer.

Study how a deliberately small implementation handles lifetime, allocation, and failure limits without growing into a full XML standards stack.

- **C1:** Nodes belong to an `XMLDocument`, visitor dispatch distinguishes node kinds, and a maximum element depth explicitly limits stack-exhaustion cases from deeply nested input. [Public types and internal contracts](https://github.com/leethomason/tinyxml2/blob/master/tinyxml2.h).
- **C3:** `MemPoolT` allocates fixed-size objects in blocks. `StrPair` can retain ranges in the source buffer and defer normalization/entity work until the string is read. Both mechanisms are documented beside their implementation in the same header.

The [project overview](https://github.com/leethomason/tinyxml2#readme) explains its integration goals and intentionally restricted feature scope. It is useful precisely because its smaller design can be followed end to end.

### 6. [FasterXML/woodstox](https://github.com/FasterXML/woodstox)

**Language / role:** Java; StAX XML pull parser/writer, also exposing SAX and StAX2 functionality.

Woodstox makes lazy parsing an observable API design problem: deferred work changes when errors can surface.

- **C1:** `BasicStreamReader` tracks token completeness, element nesting, attribute collection, and text-validation requirements. Its comments explain why deferred parsing interacts awkwardly with StAX methods that cannot throw checked stream exceptions. [Reader implementation](https://github.com/FasterXML/woodstox/blob/main/src/main/java/com/ctc/wstx/sr/BasicStreamReader.java).
- **C3:** Text coalescing, partial segments, lazy token completion, and whitespace interning are explicit mechanisms. Lazy parsing is disabled for the event-reader path because event creation already demands the complete data; validation can also force text completion.
- **C2:** Standard StAX/SAX interfaces plus StAX2 extensions allow reuse across Java XML pipelines, with factory properties controlling behavior. [Project and configuration overview](https://github.com/FasterXML/woodstox#readme).

### 7. [tafia/quick-xml](https://github.com/tafia/quick-xml)

**Language / role:** Rust; pull reader/writer with optional asynchronous I/O and Serde integration.

Study the API consequences of borrowing data from reusable buffers rather than allocating an owned object for every XML event.

- **C2:** The crate separates explicit `Reader`/`Writer` event processing from Serde mapping, with optional Tokio support. Readers and writers can be combined to implement stream transformations. [Crate architecture and API overview](https://github.com/tafia/quick-xml/blob/master/src/lib.rs).
- **C3:** Buffer allocation and clearing remain under caller control. Configuration documentation explains the additional allocation needed for matching end tags and expanding empty elements, including when the two settings can share that cost. [Reader and configuration](https://github.com/tafia/quick-xml/blob/master/src/reader/mod.rs).
- **C1:** End-name checking, unclosed-reference handling, and whitespace-related option interactions have explicit error and behavior contracts in the reader.

Boundary: callers of the event interface must track their application-level nesting and state; reading incrementally does not automatically build a DOM.

### 8. [RazrFalcon/roxmltree](https://github.com/RazrFalcon/roxmltree)

**Language / role:** Rust; read-only XML tree.

Roxmltree illustrates a different optimization point from both streaming parsers and fully mutable DOMs: retaining indexed navigation while avoiding mutation machinery.

- **C2:** `Document`, `Node`, node IDs, and traversal iterators provide reusable navigation. Nodes reference a containing document rather than independently owning child objects. [Tree representation](https://github.com/RazrFalcon/roxmltree/blob/master/src/lib.rs).
- **C3:** The document holds vectors of nodes and attributes together with borrowed input text. This gives a concrete layout to study when considering allocation overhead and source-position support; the API labels source-position calculation as expensive.
- **C1:** Parsing distinguishes invalid reserved namespace bindings, unknown prefixes, duplicate declarations, and mismatched closing tags. [Parser and error model](https://github.com/RazrFalcon/roxmltree/blob/master/src/parse.rs).

Boundary: its read-only model is intentional; document editing requires another representation.

### 9. [beevik/etree](https://github.com/beevik/etree)

**Language / role:** Go; mutable XML element trees built over `encoding/xml`.

Etree provides a useful middle-sized example of the nontrivial work above a standard-library tokenizer.

- **C1:** Child mutation maintains both parent pointers and sibling indices. Moving a child within its current parent adjusts the insertion index; removal repairs later indices and detaches the token. [Tree implementation](https://github.com/beevik/etree/blob/main/etree.go).
- **C2:** A common token interface covers elements, text, comments, directives, and processing instructions, with read/write settings controlling representation. A separate path system composes selectors and filters for navigation. [Path implementation and grammar](https://github.com/beevik/etree/blob/main/path.go).

Study the ownership invariants together with query evaluation, particularly after a tree mutation. Its path language is explicitly a restricted XPath-like language; the implementation should not be described as a complete XPath processor.

## HTML tree construction and streaming rewriting

### 10. [inikulin/parse5](https://github.com/inikulin/parse5)

**Language / role:** TypeScript; HTML parsing and serialization toolset for Node.js. Counted once as a monorepo.

The relevant subsystem is `packages/parse5`: a browser-style parser separated from the concrete representation of its output tree.

- **C1:** Parsing maintains insertion modes, open-element and formatting-element structures, fragment context, and template modes. These interacting states explain why malformed HTML cannot be modeled as ordinary balanced XML tags. [Parser](https://github.com/inikulin/parse5/blob/master/packages/parse5/lib/parser/index.ts).
- **C2:** `TreeAdapter` abstracts element creation, attribute adoption, detachment, and other tree operations through a typed node map. It is a minimal boundary for plugging in an AST representation, with documented limits on being a general manipulation API. [Adapter contract](https://github.com/inikulin/parse5/blob/master/packages/parse5/lib/tree-adapters/interface.ts).

Study the parser and adapter together to see how specification state can remain independent of a consumer's document classes.

### 11. [servo/html5ever](https://github.com/servo/html5ever)

**Language / role:** Rust; HTML tokenizer, tree builder, and serializer. The repository's `markup5ever` interface is part of this single selection.

Html5ever is a useful study in integrating a standards parser with a host-owned DOM.

- **C1:** The project describes tokenizer and tree-builder testing against `html5lib-tests` and explicitly acknowledges remaining browser-compatibility gaps. The sink contract additionally captures quirks mode, template content, adjacent text merging, and element identity requirements. [Project description](https://github.com/servo/html5ever#readme).
- **C2:** `TreeSink` uses associated handle and output types so the parser can manipulate different tree implementations. Cloning a handle must preserve identity, while the host supplies node creation and attachment behavior. [Tree-builder interface](https://github.com/servo/html5ever/blob/main/markup5ever/interface/tree_builder.rs).

Boundary: the core parser does not prescribe its own DOM representation, and correct XHTML parsing requires an XML parser.

### 12. [lexbor/lexbor](https://github.com/lexbor/lexbor)

**Language / role:** C; modular web-processing library. Relevant subsystems: HTML tokenizer/tree construction and DOM; broader rendering work is outside this selection.

Lexbor is notable for documenting how a literal implementation of specification stages can be reorganized for throughput.

- **C1:** The HTML module implements full-document and fragment parsing, chunked input, and tree-construction tests. These claims are explicitly made for the HTML subsystem, not for the unfinished browser engine as a whole. [Module overview](https://github.com/lexbor/lexbor#html-module).
- **C3:** The author's implementation article describes reusable token storage, numeric tag IDs, state-local scanning loops, and incoming-buffer bookkeeping that restores correctness when tags cross chunk boundaries. [HTML architecture article](https://github.com/lexbor/docs/blob/main/source/articles/part-1-html.md).
- **C2:** HTML and DOM are independently usable modules within a wider set of encoding, selector, and CSS facilities.

No numerical speed comparison is adopted from the project's benchmarks.

### 13. [cloudflare/lol-html](https://github.com/cloudflare/lol-html)

**Language / role:** Rust; streaming HTML parser/rewriter with selector-based mutation callbacks.

Study a design driven by output latency and constrained memory, particularly how it avoids constructing a complete DOM.

- **C3:** The engineering article describes a tag scanner that skips irrelevant content, a fuller lexer enabled when matching requires more information, and token outlines storing ranges for input split across chunks. [Architecture discussion](https://blog.cloudflare.com/html-parsing-2/).
- **C2:** Selectors scope rewrite callbacks, and a resumable matching machine connects selector evaluation to the parser. The same article explains shared selector prefixes and suspension when attributes are needed.
- **C1:** A shared macro-based state-machine definition reduces inconsistent behavior between the two parsing paths. This is a concrete complexity-management response to maintaining two views of one grammar.

The [library overview and example](https://github.com/cloudflare/lol-html#readme) show incremental writes and finalization. The architecture article is historical design evidence, not a fresh performance measurement.

### 14. [fb55/htmlparser2](https://github.com/fb55/htmlparser2)

**Language / role:** TypeScript/JavaScript; permissive HTML/XML tokenizer and callback parser.

This is a useful counterpart to browser-conformance-oriented implementations because its project documentation explicitly acknowledges parsing shortcuts.

- **C2:** Applications can consume callbacks directly, wrap the parser in a writable stream, or attach a DOM handler. XML mode changes entity, CDATA, case, and self-closing behavior. [API and ecosystem overview](https://github.com/fb55/htmlparser2#readme).
- **C3:** The tokenizer uses explicit states, buffer offsets, section boundaries, and specialized scanning. Pause/resume retains progress, while callbacks can consume input without constructing an entire tree. [Tokenizer](https://github.com/fb55/htmlparser2/blob/master/src/Tokenizer.ts).

Study where permissive behavior lives and how callback consumption affects allocation. The project itself directs users needing strict HTML specification behavior toward parse5; this selection does not claim the two have equivalent parsing semantics.

### 15. [jhy/jsoup](https://github.com/jhy/jsoup)

**Language / role:** Java; HTML/XML parsing, DOM editing, selection, and cleaning.

The especially interesting subsystem is `StreamParser`, which combines progressive input with a usable DOM rather than exposing only low-level SAX events.

- **C2:** Completed elements are available through an iterator or stream, while selection methods can suspend parsing at a match and resume later. This composes with the broader DOM manipulation API. [Stream parser](https://github.com/jhy/jsoup/blob/master/src/main/java/org/jsoup/parser/StreamParser.java).
- **C3:** Removing completed elements or children during parsing can reduce retained memory enough to process otherwise oversized inputs. Memory reduction is caller-controlled, not automatic.
- **C1:** The implementation documents the consequences of partial knowledge: selectors depending on future siblings require completion, input failures may emerge as unchecked I/O exceptions, and one parser must not process concurrent inputs.

The [project overview](https://github.com/jhy/jsoup#readme) situates this subsystem within the complete parser, query, and editing library.

### 16. [digitalfondue/jfiveparse](https://github.com/digitalfondue/jfiveparse)

**Language / role:** Java; compact HTML parser, serializer, and selector facilities.

Jfiveparse is a less prominent implementation with unusually useful documentation of intentional deviations and source-preservation options.

- **C1:** The README identifies WPT tree-construction and html5lib tokenizer tests, while also documenting template-element representation limitations and nonstandard parsing switches. This makes conformance scope inspectable rather than inferred from a tagline. [Behavior and tests overview](https://github.com/digitalfondue/jfiveparse#readme).
- **C3:** The tree constructor retains the previous text builder so the tokenizer can append characters directly and bypass repeated dispatch. Open elements, formatting elements, template modes, and pending table characters remain explicit state. [Tree constructor](https://github.com/digitalfondue/jfiveparse/blob/master/src/main/java/ch/digitalfondue/jfiveparse/TreeConstructor.java).
- **C2:** Selectors work with its own node types and W3C DOM nodes, with conversion between representations.

Boundary: input encoding must already be known; `Reader` input does not itself imply a bounded-memory output tree.

### 17. [html5lib/html5lib-python](https://github.com/html5lib/html5lib-python)

**Language / role:** Python; HTML parsing and serialization with pluggable tree representations.

Study the specification algorithms in a high-level implementation where data structures and recovery steps remain comparatively visible.

- **C1:** The base tree builder reconstructs active formatting elements and computes foster-parent insertion positions for misnested table content. Comments map portions of the implementation to specification steps. [Tree-builder implementation](https://github.com/html5lib/html5lib-python/blob/master/html5lib/treebuilders/base.py).
- **C2:** Tree-builder choices include ElementTree, minidom, and lxml. Strict error reporting, input-encoding hints, and separate tree walking/serialization make the implementation useful beyond a single DOM API. [Usage and testing documentation](https://github.com/html5lib/html5lib-python#readme).

The project documents its external parser test corpus. Some compatibility examples mention older Python versions; use this selection as an architectural study and check current packaging requirements separately. The repository was not archived when checked.

### 18. [AngleSharp/AngleSharp](https://github.com/AngleSharp/AngleSharp)

**Language / role:** C#; HTML parsing and DOM with browsing-context abstractions.

Study the boundary between parsing a document and hosting it in a reusable browser-like service model.

- **C1:** `HtmlDomBuilder` explicitly maintains open and formatting elements, template insertion modes, form and fragment context, and foster-parenting behavior. Its table-handling branches raise errors and route tokens through recovery paths. [DOM builder](https://github.com/AngleSharp/AngleSharp/blob/devel/src/AngleSharp/Html/Parser/HtmlDomBuilder.cs).
- **C2:** DOM interfaces, selectors, LINQ-compatible collections, configuration services, and `BrowsingContext` provide a reusable surface for parsing and document interaction. The generic builder also separates construction from concrete element/document types. [Project documentation](https://github.com/AngleSharp/AngleSharp#readme).

Boundary: full CSS, scripting, and XML-oriented facilities have companion repositories. This entry counts the core repository once and does not attribute all companion implementations to it.

## Substantial language integrations

### 19. [lxml/lxml](https://github.com/lxml/lxml)

**Language / role:** Python and Cython; Python document API over libxml2/libxslt.

Lxml is retained independently of its native dependencies because proxy identity, reference ownership, and Python execution semantics constitute substantial implementation work.

- **C1:** Element proxies are associated with native nodes to avoid duplicate Python identities. The inspected implementation includes special handling for preventing concurrent proxy disposal and resurrection under free-threaded Python, with a documented need for an external guard in one path. [Proxy implementation](https://github.com/lxml/lxml/blob/master/src/lxml/proxy.pxi).
- **C2:** XPath expressions, evaluator objects, XSLT stylesheets, result objects, extension behavior, and error handling form an application-oriented API above the C libraries. [XPath/XSLT guide](https://github.com/lxml/lxml/blob/master/doc/xpathxslt.txt).

Study the lifecycle layer alongside the query API; it is not a generated translation of C function signatures. The cited guide distinguishes its XPath 1.0/XSLT 1.0 facilities from later standards.

### 20. [sparklemotion/nokogiri](https://github.com/sparklemotion/nokogiri)

**Language / role:** Ruby with native C and Java integration; HTML/XML document querying, editing, validation, and transformation.

Nokogiri is particularly useful for studying how mutable native trees coexist with a moving garbage collector and language-level object identity.

- **C1:** The C node layer marks the containing document, updates references during Ruby GC compaction, pairs wrapper and native-node pointers, and relinks namespaces during reparenting. [Node implementation](https://github.com/sparklemotion/nokogiri/blob/main/ext/nokogiri/xml_node.c).
- **C2:** DOM, SAX, push parsing, XPath/CSS querying, a builder DSL, schema validation, and XSLT provide several reusable workflows across parser backends. The project explicitly discusses backend differences rather than promising to erase them. [Project overview](https://github.com/sparklemotion/nokogiri#readme).

Its independent engineering value lies in these ownership, mutation, and API layers. The parser engines it incorporates are not counted again as separate forks of Nokogiri.

## Query and transformation engines

### 21. [GNOME/libxslt](https://github.com/GNOME/libxslt)

**Language / role:** C; XSLT processor using libxml2. **Official read-only GitHub mirror** of GNOME GitLab.

Study the execution machinery of stylesheet-driven tree transformation: template application, local-variable lifetime, and dynamic XPath context.

- **C1:** The transformation implementation manages variable stacks by scope, tracks template depth, stops when limits are exceeded, and checks allocations while constructing contexts. These mechanisms address recursive transformations and partial initialization failures. [Transformation engine](https://github.com/GNOME/libxslt/blob/master/libxslt/transform.c).
- **C2:** Stylesheet processing is built around explicit transformation contexts and reusable XML trees, with template dispatch and XPath evaluation integrated into the execution path. The code distinguishes runtime state from the stylesheet structures it uses.

The [design notes](https://github.com/GNOME/libxslt/blob/master/NOTES) discuss pattern matching, template priority, recursion, and imports. They are historical questions and rationale; the current implementation, not every suggestion in those notes, is the basis for the criterion assignments.

### 22. [Saxonica/Saxon-HE](https://github.com/Saxonica/Saxon-HE)

**Language / role:** Primarily Java; XSLT, XQuery, and XPath processor. **Official release/source-distribution repository**, rather than an ordinary expanded Java source checkout.

Study separation between compilation, immutable compiled programs, and per-execution transformation state.

- **C1:** In the inspected 12.10 source, `XsltExecutable` is documented as immutable and thread-safe, while its loaded `XsltTransformer` is serially reusable within one thread. `XsltCompiler` also documents the error-reporting difficulties of concurrent compiler reuse.
- **C2:** The s9api pipeline distinguishes the processor, compiler/static context, compiled executable, and loaded transformer. One compiled stylesheet can therefore serve multiple independent executions without conflating their state.
- **C3:** Reusing a compiled executable avoids repeated stylesheet compilation while preserving per-run state boundaries.

Entry points: [repository overview](https://github.com/Saxonica/Saxon-HE#readme) and the [official 12.10 source archive](https://github.com/Saxonica/Saxon-HE/blob/main/12/source/saxon12-10source.zip), specifically `net/sf/saxon/s9api/XsltCompiler.java` and `XsltExecutable.java`. Commercial-edition facilities mentioned in shared source comments are not attributed to HE.

### 23. [apache/xalan-c](https://github.com/apache/xalan-c)

**Language / role:** C++; XSLT 1.0 and XPath 1.0 transformation library using Xerces-C++.

Xalan-C++ offers a useful view of configurable allocation and transformation lifetime in a substantial C++ engine.

- **C2:** Transformations accept multiple input/output forms, including streams and DOMs, and support C++ extension functions. Xerces supplies XML parsing while Xalan implements the stylesheet transformation layer. [Overview](https://github.com/apache/xalan-c/blob/master/docs/overview.md).
- **C3:** A pluggable `MemoryManager` can be supplied during global initialization and separately for transformer instances. Applications can choose allocation strategies or share a manager deliberately; the distinction is explained with concrete instance examples. [Programming guide](https://github.com/apache/xalan-c/blob/master/docs/programming.md).

Study these allocation boundaries together with transformer ownership. This is a selection for the XSLT 1.0 engine; it does not imply support for the later XSLT/XPath versions implemented by some other entries.

### 24. [FontoXML/fontoxpath](https://github.com/FontoXML/fontoxpath)

**Language / role:** TypeScript/JavaScript; XPath/XQuery evaluation and XQuery Update Facility support over XML nodes.

Study how an expression engine can remain independent of a concrete DOM and then apply a separately represented set of updates.

- **C2:** `IDomFacade` abstracts attributes, children, and other navigation relationships. Optional buckets let a host narrow candidate retrieval without exposing its underlying representation. [DOM facade interface](https://github.com/FontoXML/fontoxpath/blob/master/src/domFacade/IDomFacade.ts).
- **C1:** Tests for executing pending update lists cover deletion, replacement, and renaming in the presence of namespaced attributes. They verify resulting XML after evaluation and update application occur in separate steps. [Update execution tests](https://github.com/FontoXML/fontoxpath/blob/master/test/specs/parsing/xquery-updating/executePendingUpdateList.tests.ts).
- **C3:** Navigation buckets provide an explicit filtering hook at the abstraction boundary, avoiding a requirement that every host materialize all candidate nodes first.

Boundary: it operates over an existing node model; it is not itself an XML text parser, and its README identifies remaining language-feature gaps.

### 25. [sissaschool/elementpath](https://github.com/sissaschool/elementpath)

**Language / role:** Python; XPath parsers and selectors for ElementTree and lxml.

Elementpath is a useful study in growing a language family around a reusable expression parser and an explicit XPath data/context model.

- **C2:** Its Pratt parser represents operands through list-like tokens and supports per-symbol binding powers, patterns, and labels. Those mechanisms form reusable foundations for its XPath parser versions. [Pratt implementation](https://github.com/sissaschool/elementpath/blob/master/elementpath/tdop.py).
- **C1:** Static context belongs to the parser, while `XPathContext` explicitly handles dynamic position, variables, namespaces, node kinds, and document-versus-fragment treatment. These distinctions matter when an ElementTree element must be interpreted as an XPath document context. [Dynamic context](https://github.com/sissaschool/elementpath/blob/master/elementpath/xpath_context.py).

The repository's public API supports both immediate selection and reusable selector objects. Its category fit is query processing over XML trees, not a replacement tokenizer for XML input.

### 26. [Paligo/xee](https://github.com/Paligo/xee)

**Language / role:** Rust; XPath compiler/interpreter and partially implemented XSLT engine. Counted once across its workspace crates.

Xee supplies a particularly readable compiler architecture: lexer → XPath AST → specialized intermediate representation → bytecode → interpreter, with a related path for XSLT.

- **C2:** Separate compiler stages, a shared interpreter, and a Rust binding mechanism for standard functions provide reusable boundaries across XPath and XSLT. [Architecture and testing overview](https://github.com/Paligo/xee#architecture).
- **C1:** The project distinguishes dynamic type checking from unsupported static typing and schema integration. It describes XPath conformance testing and publishes specific feature gaps rather than presenting all language versions as complete. [Conformance notes](https://github.com/Paligo/xee/blob/main/conformance/README.md).

Boundary: XSLT support remains partial, and the inspected conformance notes say XSLT support in the generic test runner is still missing. Treat it as a substantive implementation to study, not a complete substitute for an established XSLT processor. No C4 claim is made.

### 27. [UweSchmidt/hxt](https://github.com/UweSchmidt/hxt)

**Language / role:** Haskell; XML/HTML parsing and transformation toolbox, with related XPath/XSLT and validation packages in one repository.

HXT adds a functional-programming perspective that the object-oriented DOM and event-parser entries do not cover.

- **C2:** `ArrowXml` builds XML predicates and transformations over arrow, list-arrow, and tree-arrow abstractions. This lets selection, construction, and traversal participate in compositional processing pipelines. [XML arrow interface](https://github.com/UweSchmidt/hxt/blob/master/hxt/src/Text/XML/HXT/Arrow/XmlArrow.hs).
- **C1:** Namespace processing threads the valid environment through elements and attributes, extends it at declarations, and provides cleanup that gathers prefix/URI pairs before renaming declarations and qualified names. These are nontrivial invariants for document transformations. [Namespace algorithms](https://github.com/UweSchmidt/hxt/blob/master/hxt/src/Text/XML/HXT/Arrow/Namespace.hs).

Status: an older, lower-activity codebase; the GitHub API reported its last push in July 2024 and no archival flag. The selection concerns enduring abstraction and transformation lessons, not an assertion of current compiler support.

## Coverage, search process, and limitations

Discovery used live web searches, followed by repository/API verification and direct reading of implementation files, official manuals, and tests. Search formulations covered general HTML/XML tokenizers and conformance; XML transformation/XPath/XSLT engines; C/C++ parsers; Rust and JavaScript streaming rewriters; Rust/Java pull readers; Python/Ruby/.NET integrations; official GNOME mirrors; Go tree/query libraries; Haskell arrow-based XML processing; and smaller-language or historical HTML parser alternatives. Follow-up searches increasingly returned alternative bindings, forks, or implementations of already-covered architectural families, so the list stopped at 27 rather than expanding every ecosystem mechanically.

The selection spans C, C++, Rust, Java, TypeScript/JavaScript, Python/Cython, Ruby, C#, Go, and Haskell. It includes callback, pull, mutable-tree, immutable-tree, browser tree-construction, streaming mutation, compiled transformation, and functional-combinator designs. HXT, jfiveparse, roxmltree, Xee, and elementpath help prevent the list from becoming only the most familiar packages.

Canonical URLs and default branches for every retained repository were checked through the GitHub API or an opened repository page. All retained repositories lacked an archival flag at the time checked; this is not evidence of active maintenance by itself. The two GNOME entries are official mirrors, and Saxon-HE is explicitly identified as a release/source archive. No retained forks are counted as independent projects merely for repackaging an upstream engine. Relevant monorepo subsystems are identified in their entries.

Important exclusions: whole browser engines and XML databases would broaden the category beyond reusable parsing/transformation libraries; application scrapers and sanitizers without a substantial parser or document engine are omitted. Thin wrappers around selected native engines, platform ports, tutorial parsers, and lists of libraries are excluded. Go query wrappers, additional JavaScript DOM facades, and smaller functional-language parsers surfaced in discovery but were not all promoted to full entries; this is not an exhaustive ecosystem census.

Primary-source inspection covered at least one implementation or architectural source beyond a tagline for each repository, plus repository identification/category evidence. Source files were read as text; the Saxon archive was inspected in memory. No candidate code was run, dependencies installed, large repositories cloned, or remote services modified. Published conformance claims and tests were inspected but not rerun; benchmarks were not reproduced, and no numerical speed rankings are asserted. Branch links are moving references, so the research date matters. Differences between upstream documentation, default-branch code, and released packages should be checked when choosing a production dependency.
