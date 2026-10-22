# Text data format parsers and serializers

Research date: 2026-10-09. Category 210 of 347.

This selection covers 24 GitHub repositories implementing parsers, emitters, serializers, or editable document models for JSON, YAML, TOML, XML, CSV, HCL, HOCON, KDL, and EDN. It includes low-level engines, typed data binding, tabular ingestion, and preservation of human-written formatting. General parser generators, compiler front ends, binary-only codecs, specification-only repositories, and thin bindings are outside the selection. A parser need not also provide a serializer to qualify.

The criteria below identify specific engineering lessons, not a claim that every component is exemplary. The linked implementation files and documentation within each entry are recommended starting points. Repository URLs were opened, and additional primary material was read for every selection. Unless stated otherwise, the description concerns the inspected default branch or linked documentation, which may differ from a released package.

- **C1 — Difficult correctness:** invariants, numerical or Unicode semantics, adversarial input, concurrency, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or representations serving multiple workflows.
- **C3 — Performance with structure:** concrete allocation, throughput, latency, or memory constraints addressed through an understandable design.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate complexity management; age alone is insufficient.

## JSON engines and typed serialization

### 1. [simdjson/simdjson](https://github.com/simdjson/simdjson)

**C++ — SIMD-oriented JSON parsing with DOM and On-Demand interfaces.** Study how a common parsing algorithm is separated from processor-specific primitives, and how the representation changes when callers need only selected values.

- **C1:** The design separates structural indexing and UTF-8 validation from number/string interpretation and DOM tape construction. This makes the division of validation responsibilities explicit, rather than treating token discovery as complete parsing. The engineering guide also identifies fuzzing and its CI integration. [Design and source map](https://github.com/simdjson/simdjson/blob/master/HACKING.md).
- **C3:** Generic parsing code is compiled against architecture-specific implementations; runtime CPU selection allows one binary to select an appropriate implementation. The documentation explains why indiscriminate architecture compiler flags can undermine that dispatch. [Implementation selection](https://github.com/simdjson/simdjson/blob/master/doc/implementation-selection.md).

### 2. [ibireme/yyjson](https://github.com/ibireme/yyjson)

**C — JSON reader/writer with separate immutable and mutable document representations.** A useful study in choosing data layout for the operation being optimized, while keeping ownership comprehensible.

- **C2:** Parsed documents, mutable documents, values, and conversion operations form a reusable document API. Values share their owning document's lifetime and cannot be freed independently, giving a clear ownership boundary. [Data structures and ownership](https://ibireme.github.io/yyjson/doc/doxygen/html/data-structures.html).
- **C3:** Immutable documents place values and strings in contiguous regions; mutable arrays and objects use circular linked lists whose parent retains the tail, enabling constant-time append, prepend, and removal of the first child. These are concrete read-versus-edit tradeoffs, not merely a speed claim. [Representation details](https://ibireme.github.io/yyjson/doc/doxygen/html/data-structures.html).

### 3. [Tencent/rapidjson](https://github.com/Tencent/rapidjson)

**C++ — JSON parser and generator with SAX and DOM APIs.** Study an event protocol that lets parsing, tree construction, traversal, and output compose without requiring each component to know the others.

- **C2:** `Reader` publishes events to a `Handler`; `Writer` and `Document` implement that same concept, while `Value::Accept` publishes events from an existing tree. Allocator, encoding, and stream concepts provide additional independent extension points. [Architecture](https://rapidjson.org/md_doc_internals.html).
- **C3:** The internals document explains tagged value storage, inline short strings, pooled allocation, and specialized parsing/generation paths. It connects memory layout to cache behavior and describes optimization hazards such as SIMD access near page boundaries. [Internals](https://rapidjson.org/md_doc_internals.html).

### 4. [serde-rs/json](https://github.com/serde-rs/json)

**Rust — JSON parsing and serialization integrated with Serde's typed data model.** Study how a format implementation supports both generic values and application types while exploiting input ownership information.

- **C1:** Deserialization distinguishes strings borrowed from the original input from strings copied into scratch storage. Escape expansion and UTF-8 validation interact with those lifetimes; stream input cannot offer the same borrowing guarantees as a retained input slice. [Deserializer lifetime guide](https://serde.rs/lifetimes.html).
- **C2/C3:** The JSON implementation specializes its sealed input abstraction for I/O, byte slices, and UTF-8 strings. Slice input can return unescaped strings without copying; string input can exploit its existing UTF-8 guarantee, and line/column calculation is deferred on the slice path until errors occur. [Input implementation](https://raw.githubusercontent.com/serde-rs/json/master/src/read.rs).

### 5. [FasterXML/jackson-core](https://github.com/FasterXML/jackson-core)

**Java — Jackson's streaming parser/generator foundation and JSON implementation.** This entry is the core repository, not the separate databind repository. Study the boundary between a token engine and higher-level object mapping.

- **C2:** Parser, generator, and factory abstractions underpin Jackson data binding and other format implementations. The repository explains which abstractions are format-independent and which packages implement JSON. Its reusable factory is thread-safe once configured. [Core architecture and API overview](https://github.com/FasterXML/jackson-core).
- **C1:** `StreamReadConstraints` centralizes limits on nesting, token lengths, document length, and token count, with factory-specific configuration. The source also guards expensive decimal-to-integer conversion. These address resource exhaustion; they are not a substitute for semantic validation. [Constraint implementation](https://raw.githubusercontent.com/FasterXML/jackson-core/3.x/src/main/java/tools/jackson/core/StreamReadConstraints.java).

The inspected default branch is `3.x`; the repository explicitly distinguishes its package names and Java baseline from the 2.x line.

### 6. [JamesNK/Newtonsoft.Json](https://github.com/JamesNK/Newtonsoft.Json)

**C# — Json.NET object serialization, deserialization, and JSON object-model tooling.** Study the mismatch between a runtime object graph and JSON's smaller tree-shaped data model.

- **C2:** The serializer defines different contracts for collections, dictionaries, ordinary objects, dynamic objects, and custom converters. Opt-in and opt-out member selection allow one engine to serve different application models. [Serialization guide](https://www.newtonsoft.com/json/help/html/SerializationGuide.htm).
- **C1:** Circular references, object reuse versus replacement, reference metadata, and polymorphic type names require explicit policy. The settings documentation explains default loop errors and the need to validate incoming type names when enabling type-name handling. [Serialization policies and failure modes](https://www.newtonsoft.com/json/help/html/SerializationSettings.htm).

### 7. [haskell/aeson](https://github.com/haskell/aeson)

**Haskell — JSON values, typed decoding, generic derivation, and encoding.** Study how type classes support convenient defaults while allowing a more efficient representation-specific path.

- **C2/C3:** `FromJSON` and `ToJSON` support application types and generic JSON values. `toEncoding` can build output directly without allocating an intermediate `Value`; its default still delegates through `toJSON` to preserve compatibility with older instances. [API and direct-encoding design](https://raw.githubusercontent.com/haskell/aeson/master/src/Data/Aeson.hs).
- **C1:** The changelog records large-number denial-of-service fixes and a compatibility backport, control-character validation fixes, and removal of an unsound rewrite rule. It also documents the tokenizer/parser replacement and movement of the older Attoparsec implementation into a separate package. This is a concrete opportunity to study numerical failure modes and implementation migration. [Changelog](https://raw.githubusercontent.com/haskell/aeson/master/changelog.md).

### 8. [nlohmann/json](https://github.com/nlohmann/json)

**C++ — General-purpose JSON value API, parsing, and serialization.** Study the implementation beneath a familiar container-style interface, particularly the shared event boundary between parsing and tree construction.

- **C2:** The SAX interface separates signed integers, unsigned integers, floating-point values with their original token, strings, and structural events. Handlers can stop parsing, and parse errors carry a position, token, and exception. This supports consumers beyond building a complete DOM. [SAX interface and DOM handlers](https://raw.githubusercontent.com/nlohmann/json/develop/include/nlohmann/detail/input/json_sax.hpp).
- **C1:** The repository documents deliberate Unicode and numeric acceptance choices and its JSONTestSuite coverage. It also distinguishes strict whole-document `parse()` from stream extraction, which consumes one value and leaves subsequent input unread—a consequential API invariant for validation callers. [Conformance and encoding notes](https://github.com/nlohmann/json).

## YAML event streams, composition, and document editing

### 9. [yaml/libyaml](https://github.com/yaml/libyaml)

**C — YAML parser and emitter with an event-level API.** Study a low-level engine whose event grammar can be used independently of an application's native object types.

- **C1:** The parser spells out the grammar and implements explicit state dispatch for block/flow collections, mappings, directives, and document boundaries. Its end/error states prevent further event production. [Parser state machine](https://raw.githubusercontent.com/yaml/libyaml/master/src/parser.c).
- **C2:** Parsing produces events and emission consumes them, with a documented equivalence contract and explicit scalar/tag/style attributes. Input can come from strings, files, or a caller-supplied reader. [Event model and API](https://pyyaml.org/wiki/LibYAML).
- **C4:** The history records streaming fixes in 2009, pointer-overflow fixes in 2012, and later emitter and test-suite work through the listed 2020 release. [Changes](https://raw.githubusercontent.com/yaml/libyaml/master/Changes).

Release-cadence caveat: the official download page still identifies 0.2.5, dated 2020-06-01; this entry does not imply a recent packaged release.

### 10. [eemeli/yaml](https://github.com/eemeli/yaml)

**TypeScript/JavaScript — YAML parsing, serialization, and editable document models.** Particularly useful for studying why tooling needs both concrete syntax and semantic document representations.

- **C2:** The lexer, CST parser, and document composer are separate public stages. Callers can obtain native values, editable documents with comments, or lower-level tokens carrying source offsets and formatting. [Parsing architecture](https://github.com/eemeli/yaml/blob/main/docs/07_parsing_yaml.md).
- **C1:** The CST parser deliberately preserves a best-effort structure for malformed input; validation occurs during composition, with errors linked back to source offsets. CST stringification merely joins retained source pieces and performs no validation. That distinction is crucial for editors that must represent incomplete documents without misrepresenting them as valid YAML. [Error and CST contracts](https://github.com/eemeli/yaml/blob/main/docs/07_parsing_yaml.md).

### 11. [yaml/pyyaml](https://github.com/yaml/pyyaml)

**Python, with Cython integration — YAML parsing, object construction, and emission.** This is a substantive Python implementation, not merely a LibYAML wrapper. Study the boundary between event composition and native-object construction.

- **C1:** The composer maintains a per-document anchor table, rejects undefined aliases and duplicate anchors, and registers collection nodes before recursively composing their contents. That ordering permits references to already registered nodes while preserving identity. It also distinguishes one-document loading from a multi-document stream. [Composer implementation](https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/composer.py).
- **C4:** The 2019–2024 change history documents loader compatibility repairs, moving arbitrary Python tags to `UnsafeLoader`, requiring an explicit loader for `yaml.load`, YAML-type tests, and Python/Cython compatibility work. This is useful evidence of evolving safety boundaries in a widely reused API. [Change history](https://raw.githubusercontent.com/yaml/pyyaml/main/CHANGES).

## TOML and preservation of human-written configuration

### 12. [toml-rs/toml](https://github.com/toml-rs/toml)

**Rust — TOML workspace; the main study target here is `crates/toml_edit`.** Counted once despite its multiple crates. Study the separation of a value's meaning, textual spelling, and surrounding formatting.

- **C2:** `Formatted`, `Repr`, and `Decor` keep a scalar's logical value, original representation, and prefix/suffix whitespace or comments separate. Source spans and conversion from span-backed text support both document inspection and mutation. [Representation implementation](https://raw.githubusercontent.com/toml-rs/toml/main/crates/toml_edit/src/repr.rs).
- **C1/C4:** The changelog spans the 2022 parser rewrite through 2026, explicitly treating the rewrite as a breaking release. It records recursion limits, dotted-key/table conflicts, numeric overflow checks, formatting fixes, and compatibility changes for TOML 1.1. [toml_edit changelog](https://github.com/toml-rs/toml/blob/main/crates/toml_edit/CHANGELOG.md).

The API documentation explicitly lists dotted-key ordering as a preservation limitation; “format preserving” should not be read as an unconditional identity guarantee. [Document API and limitations](https://raw.githubusercontent.com/toml-rs/toml/main/crates/toml_edit/src/lib.rs).

### 13. [python-poetry/tomlkit](https://github.com/python-poetry/tomlkit)

**Python — TOML parser, serializer, and style-preserving mapping API.** Study how a dictionary-like interface can coexist with an ordered syntax body and tables represented in multiple separated fragments.

- **C1/C2:** `Container` stores both a body sequence and a key-to-body index, including tuple indices for out-of-order table fragments. Dotted-key handling and table placement must prevent an edit from silently moving subsequent values into a different table's scope. [Container implementation](https://raw.githubusercontent.com/python-poetry/tomlkit/master/tomlkit/container.py).
- **C3:** The implementation caches validation of appended table fragments and invalidates that cache after incompatible mutation or failed validation. The changelog explains this and other reductions in repeated copying/scanning, alongside round-trip and deeply nested-input fixes. [Performance and correctness changes](https://raw.githubusercontent.com/python-poetry/tomlkit/master/CHANGELOG.md).

## XML: callbacks, trees, and borrowed events

### 14. [libexpat/libexpat](https://github.com/libexpat/libexpat)

**C — Streaming XML parser.** Study a callback engine that must remain correct when document structure and tokens cross arbitrary input boundaries.

- **C2:** Registered handlers receive parsing events as buffers arrive; parser creation, external-entity handling, suspension/resumption, and input-buffer APIs provide control over integration without requiring a DOM. [Expat API manual](https://libexpat.github.io/doc/api/latest/).
- **C1/C3:** The manual explains entity-amplification defenses and reparse deferral: repeatedly retrying a large incomplete token on every small input chunk can cause quadratic work, so reparsing waits for a significant amount of new input. This connects adversarial-input handling directly to the incremental parser architecture. [Attack protection and reparse behavior](https://libexpat.github.io/doc/api/latest/).

### 15. [zeux/pugixml](https://github.com/zeux/pugixml)

**C++ — XML DOM parsing, modification, serialization, and XPath.** Study an intentionally compact tree implementation and the lifetime costs of fast allocation.

- **C2:** A DOM-like traversal/editing interface and XPath queries let the same document representation support inspection, transformation, and output. [Repository and documentation overview](https://github.com/zeux/pugixml).
- **C1/C3:** The manual documents page-based allocation of many small nodes, separate document text storage, in-place loading, and configurable allocation functions. It also explains hazards: changing allocators with live objects is invalid, and deleting some nodes may reclaim no pages. These explicit tradeoffs make the memory architecture particularly instructive. [Memory-management internals](https://pugixml.org/docs/manual.html).

### 16. [tafia/quick-xml](https://github.com/tafia/quick-xml)

**Rust — Pull-based XML reader and writer, with higher-level serialization integration.** Study how lifetimes and parser configuration interact with event-stream performance.

- **C1:** Reader configuration distinguishes unmatched end tags, mismatched names, dangling references, and comment validation. The documentation notes that literal start/end names must match even when namespace prefixes would resolve to the same namespace. Some validation, including comment checking, is optional. [Reader configuration](https://raw.githubusercontent.com/tafia/quick-xml/master/src/reader/mod.rs).
- **C2/C3:** The internal `XmlSource` abstraction covers buffered input whose events borrow from a caller-provided buffer and slice input whose events borrow directly from the source. Parser state survives input refills, while the public pull API lets callers reuse buffers and choose what to retain. [Reader and input abstraction](https://raw.githubusercontent.com/tafia/quick-xml/master/src/reader/mod.rs).

## CSV and delimited text ingestion

### 17. [BurntSushi/rust-csv](https://github.com/BurntSushi/rust-csv)

**Rust — CSV reading/writing and Serde integration; study `csv-core` within the repository.** A particularly clear example of retaining a readable reference mechanism alongside a faster execution mechanism.

- **C1:** The core contains both an explicit NFA implementation and a DFA implementation, tested together so their behavior remains aligned. This supplies a concrete strategy for checking an optimized state machine against something easier to debug. [Core reader design](https://raw.githubusercontent.com/BurntSushi/rust-csv/master/csv-core/src/reader.rs).
- **C3:** The parser does not allocate. It generates a transition table from the configured NFA by enumerating states and inputs; this moves dialect-dependent choices out of the hot parsing path. The comments explain the resulting stack/table-size constraints and non-obvious dependencies. [Implementation commentary](https://raw.githubusercontent.com/BurntSushi/rust-csv/master/csv-core/src/reader.rs).

### 18. [uniVocity/univocity-parsers](https://github.com/uniVocity/univocity-parsers)

**Java — Delimited and fixed-width parsers/writers built on a shared processing framework.** Study the division between format-specific token rules and common input, row-processing, and cleanup behavior.

- **C2:** `AbstractParser` owns buffered input, output accumulation, configuration, row processors, stopping, and resource cleanup; subclasses implement `parseRecord`. The documented control cycle makes the framework's extension boundary inspectable. [AbstractParser](https://raw.githubusercontent.com/uniVocity/univocity-parsers/master/src/main/java/com/univocity/parsers/common/AbstractParser.java).
- **C1:** `CsvParser` handles quoted/unquoted fields, empty-versus-null values, embedded line endings, multiple-character delimiters, and selectable unescaped-quote policies. The code explicitly handles EOF after delimiters and bounds column lengths. [CSV implementation](https://raw.githubusercontent.com/uniVocity/univocity-parsers/master/src/main/java/com/univocity/parsers/csv/CsvParser.java).

Maintenance limitation: the inspected tag listing ends at v2.9.1, dated January 2021. Retained as an implementation study, without an assurance of current release activity. [Tags](https://github.com/uniVocity/univocity-parsers/tags).

### 19. [adaltas/node-csv](https://github.com/adaltas/node-csv)

**JavaScript — CSV monorepo; relevant packages include `csv-parse` and `csv-stringify`.** Counted once. Study how one incremental implementation supports different consumption styles.

- **C1:** The parser retains incomplete buffer tails and computes how much lookahead is needed for delimiters, escaped quotes, and closing quotes. BOM discovery can change encoding and trigger option normalization. These are substantive chunk-boundary correctness concerns. [Parsing core](https://raw.githubusercontent.com/adaltas/node-csv/master/packages/csv-parse/lib/api/index.js).
- **C2/C3:** Stream, async-iterator, synchronous, and callback APIs share an implementation. The documentation explains that callback/synchronous consumption buffers the dataset, while streaming interfaces support scalable consumption. [API architecture and memory tradeoffs](https://csv.js.org/parse/api/).

### 20. [JuliaData/CSV.jl](https://github.com/JuliaData/CSV.jl)

**Julia — Typed delimited-text reading/writing integrated with Tables.jl.** Study the bridge from a textual record format to column-oriented computation, with eager, lazy, row-wise, and chunked access.

- **C2:** The inspected main-branch API separates indexing/value parsing, Tables.jl integration, public reader APIs, and writing. `CSV.read` passes ownership-aware columns to compatible sinks, and `CSV.write` accepts the common table interface. [Module and public contracts](https://github.com/JuliaData/CSV.jl/blob/main/src/CSV.jl).
- **C1/C3:** The reading guide documents parallel parsing with stable row order, structural chunks, reference versus vectorized scanning, and bounded diagnostics. It distinguishes owned eager columns from lazy views that retain source bytes. Lazy/row access should not be mistaken for an unbounded streaming-input parser. [Reading architecture and memory behavior](https://raw.githubusercontent.com/JuliaData/CSV.jl/main/docs/src/reading.md).

These details concern the inspected main branch; older released APIs and cached documentation differ.

## Structured configuration and extensible data notation

### 21. [hashicorp/hcl](https://github.com/hashicorp/hcl)

**Go — HCL configuration-language toolkit with native and JSON syntaxes.** The relevant subsystems are parsing, structural decoding, diagnostics, and document writing; this is not an entry for Terraform itself.

- **C2:** Applications define expected attributes and nested block types while HCL supplies syntax parsing, structural checks, and expressions parameterized by application-provided variables/functions. Native and JSON forms feed the toolkit's higher-level model. [Architecture overview](https://github.com/hashicorp/hcl).
- **C1:** The native parser accumulates source-ranged diagnostics, detects duplicate attributes, and attempts recovery. It explicitly suppresses cascading bad-token errors after recovery has made the current position uncertain. This is useful for studying partial results and comprehensible errors, rather than just accepting or rejecting input. [Native parser](https://raw.githubusercontent.com/hashicorp/hcl/main/hclsyntax/parser.go).

### 22. [lightbend/config](https://github.com/lightbend/config)

**Java — HOCON parsing, resolution, and configuration composition; Scala is used in tests.** Study a text format whose meaning cannot be settled solely by tokenizing and building a tree.

- **C1:** Substitutions are resolved after merging, can refer forward, and interact with missing values and includes. `ResolveContext` uses identity-based cycle markers, memoization, and path-restricted resolution to avoid both repeated work and unnecessary cycles through unrelated siblings. [Resolution implementation](https://raw.githubusercontent.com/lightbend/config/main/config/src/main/java/com/typesafe/config/impl/ResolveContext.java).
- **C2:** Immutable configuration objects support layering defaults, application values, and overrides. The format specification carefully defines merge and substitution semantics, allowing applications to share a predictable composition model. [HOCON specification](https://raw.githubusercontent.com/lightbend/config/main/HOCON.md).

The maintainers explicitly describe the library as feature complete, with future JVM compatibility as the main maintenance focus and other changes expected to be rare. [Maintenance statement](https://github.com/lightbend/config).

### 23. [kdl-org/kdl-rs](https://github.com/kdl-org/kdl-rs)

**Rust — KDL document parser and formatting-preserving editing/serialization API.** Study a node-oriented data model with ordered arguments, properties, child documents, and retained textual formatting.

- **C1:** Duplicate properties are preserved for round trips while lookup returns the last value. Numeric text can be retained independently of the interpreted `i128`/`f64` value, and automatic formatting discards that original spelling. These distinct notions of textual and semantic identity are documented explicitly. [Document API and semantic quirks](https://raw.githubusercontent.com/kdl-org/kdl-rs/main/src/lib.rs).
- **C2:** Nodes expose entries and child documents independently from formatting and source spans. Equality/hash omit location spans, and mutation may invalidate their original locations. This offers a useful, concrete model for tools that edit data without discarding comments. [Node implementation](https://raw.githubusercontent.com/kdl-org/kdl-rs/main/src/node.rs).

The API also documents optional KDL v1 parsing/fallback alongside v2; version fallback and formatting preservation are separate contracts.

### 24. [borkdude/edamame](https://github.com/borkdude/edamame)

**Clojure/ClojureScript and additional runtime targets — Configurable EDN/Clojure reader with source metadata.** Included for its EDN data-reading capability; evaluation is outside this entry's scope. Study how reader extensibility can be exposed without requiring a separate intermediate syntax tree for every value.

- **C1:** The parser tracks opening/expected delimiters and reports their locations, detects duplicate set entries, and handles conditional-reader branches with suppression of unselected forms. Those concerns go beyond splitting Lisp-like tokens. [Parser implementation](https://raw.githubusercontent.com/borkdude/edamame/master/src/edamame/impl/parser.cljc).
- **C2:** The API offers single-form, all-form, and incremental reader entry points; configurable tagged readers; feature-selective or preserved conditionals; custom collection construction; and postprocessing for values that cannot carry metadata themselves. [API contracts](https://raw.githubusercontent.com/borkdude/edamame/master/API.md).

## Coverage, search process, and limitations

Discovery used 16 distinct live search formulations, followed by repository-page verification and primary-source inspection. Search angles included SIMD JSON and numeric/Unicode validation; YAML event APIs and CSTs; lossless TOML editing; XML streaming/DOM/pull interfaces; CSV quoting and buffering across Rust, Java, Node.js, and Julia; Haskell typed encoding; Jackson resource limits; EDN, KDL, HCL, and HOCON; and wider INI, S-expression, Perl, OCaml, and D ecosystem searches. Follow-up queries increasingly returned already-covered architectures, wrappers, small examples, or adjacent language tools, so the selection stopped at 24 rather than adding marginally different implementations.

The selection spans C, C++, Rust, Java, C#, Python, TypeScript/JavaScript, Haskell, Julia, Go, and Clojure communities. It deliberately includes smaller specialist projects such as Edamame, KDL's Rust implementation, and TOMLKit alongside widely deployed engines. Multiple JSON projects remain because their study targets differ: SIMD indexing, mutable/immutable layout, event composition, borrowing, streaming factories, runtime object contracts, functional encoding, and container-style DOM/SAX integration.

Important boundaries and limitations:

- General-purpose parsing libraries such as Attoparsec and Tree-sitter were discovery leads but excluded as broader parsing infrastructure. Specification repositories such as `edn-format/edn` and `kdl-org/kdl` are not counted as implementations. Binary codecs, HTML/Markdown processors, query engines, and thin bindings are likewise excluded.
- `toml-rs/toml`, `adaltas/node-csv`, and other multi-component repositories are each counted once. LibYAML and PyYAML remain separate because the inspected PyYAML code supplies substantive composition and native-object semantics, rather than only forwarding to C.
- No retained entry is presented as an independent fork or unofficial mirror. No inspected repository page displayed an archive or relocation banner. This is not an assurance of active maintenance: the concrete release-cadence limitations for LibYAML and uniVocity, and Lightbend Config's stated maintenance policy, are recorded above.
- Some hosted documentation pages were unavailable through the research browser; repository source or documentation files supplied the evidence instead. Browser caches also exposed different ages of CSV.jl material; the entry uses the newer GitHub module view and matching main-branch reading guide, rather than combining their behavior with older source snapshots.
- Architectural study recommendations and C1–C4 judgments are grounded in the cited sources but remain evaluative inferences. No candidate code was executed, dependencies installed, benchmarks reproduced, or complete security audit performed. There are no comparative throughput rankings or quality claims based on stars.

Final checks: 24 distinct canonical repository URLs; every entry has at least two justified criteria and an inspected implementation or architectural source beyond its repository landing page. This report is a selection guide, not an exhaustive census or a guarantee of uniform code quality.
