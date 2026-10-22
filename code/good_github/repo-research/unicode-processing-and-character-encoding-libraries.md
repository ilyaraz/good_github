# Unicode processing and character encoding libraries

Research date: 2026-10-09.

This report selects 25 GitHub repositories implementing Unicode algorithms, character conversion, text boundaries, display width, collation, encoding detection, or repair of encoding damage. It covers C, C++, Rust, Go, JavaScript, Python, Java, C#, OCaml, Haskell, and Zig, from small algorithm libraries to internationalization platforms. In larger repositories, only the relevant Unicode subsystems are assessed. The explanations identify useful engineering study material; they are not a certification of every component or a recommendation to adopt a dependency without further evaluation.

Criteria legend:

- **C1 — Correctness:** difficult invariants, malformed or adversarial input, state transitions, concurrency, or failure handling.
- **C2 — Abstraction:** substantial reusable interfaces or components serving multiple applications.
- **C3 — Performance:** concrete resource or throughput constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or explicit management of complexity.

Repository headings link to verified canonical GitHub pages. The implementation and documentation links near each criterion also serve as suggested entry points. References to source describe the inspected branch or published documentation, not a guarantee that every released version behaves identically. Maintenance is not inferred from stars or commit counts.

## Unicode platforms and shared infrastructure

### 1. [unicode-org/icu](https://github.com/unicode-org/icu)

**Language/role:** C/C++ and Java; ICU4C and ICU4J in one repository, counted once. Focus on normalization and the shared Unicode processing infrastructure.

Study how a large standards implementation replaces its internals while preserving older public interfaces. The normalization guide explains how the older normalization API delegates to `Normalizer2`, and how generated normalization data can serve both C++ and Java.

- **C1:** Normalization data generation enforces constraints on recursive mappings and canonical combining classes, while append operations must respect normalization boundaries. This is a concrete combination of data-validation and runtime semantic invariants.
- **C2:** Standard forms, custom mapping files, filtered normalizers, and composition/decomposition modes share the same service abstraction. The guide identifies IDNA mappings and combined normalization/case folding as applications.
- **C3:** `spanQuickCheckYes()` avoids reprocessing an already-normalized prefix; combined data files allow related transformations in one processing step. These mechanisms are explained in the [normalization implementation guide](https://unicode-org.github.io/icu/userguide/transforms/normalization/).

The repository also exposes exhaustive testing, fuzzing, and API-comparison infrastructure. Those are useful inspection leads, not a claim that the checks were run for this report.

### 2. [unicode-org/icu4x](https://github.com/unicode-org/icu4x)

**Language/role:** Rust with foreign-language interfaces; modular Unicode and internationalization components. The relevant subsystem here is `icu_normalizer`, together with its data-provider architecture.

Study the separation between Unicode algorithms, typed data, and data delivery. This offers a different architectural scale from ICU4C/J while still supporting reusable standards implementations.

- **C1:** The normalizer distinguishes valid Rust strings from potentially malformed UTF-8 and UTF-16 input. It also exposes normalizing character iterators and building blocks for UTS #46. Its normalization checks deliberately return definitive answers rather than a three-way quick-check result. See the [normalizer API](https://docs.rs/icu_normalizer/latest/icu_normalizer/).
- **C2:** Data providers separate the consumer’s typed data requirements from storage format and delivery mechanism.
- **C3:** The [data-pipeline design](https://github.com/unicode-org/icu4x/blob/main/documents/design/data_pipeline.md) explains preprocessing, selective data inclusion, and explicit caching to reduce runtime work and data footprint. The document explicitly warns that some detailed implementation choices have changed; use it for the high-level architecture, alongside current API documentation.

### 3. [golang/text](https://github.com/golang/text)

**Language/role:** Go; `golang.org/x/text`, including encoding conversion, normalization, casing, and collation. **Official GitHub mirror:** development is hosted at Go’s source service, as the repository explains.

Start with the shared transformation protocol rather than an individual codec. It demonstrates how many text algorithms can participate in the same streaming I/O machinery.

- **C1:** `Transformer.Transform` specifies consumed and produced byte counts, end-of-input semantics, short source and destination errors, and the obligation to process output before considering an error. Reader/writer adapters handle buffered leftovers and detect inconsistent progress.
- **C2:** The same interface underlies character conversion and normalization, with reusable reader/writer adapters and resettable state.
- **C3:** `SpanningTransformer` identifies unchanged input without copying it, and the reader/writer implementations reuse buffers. These contracts and mechanisms are visible together in [transform.go](https://raw.githubusercontent.com/golang/text/master/transform/transform.go).

The repository’s Unicode-version matching and optional ICU conformance tests are useful additional context; its data-generation notes also warn that arbitrary data-version changes are not automatically backward compatible.

### 4. [NightOwl888/ICU4N](https://github.com/NightOwl888/ICU4N)

**Language/role:** C#; a substantive .NET port of ICU4J, including normalization, Unicode sets, break iterators, collation, and transliteration. **Scope limitation:** the README identifies ICU4J 60.1 as its baseline and describes an incomplete port with no plan to add further features.

Study adaptation of an established algorithmic API to .NET memory and string conventions. This is a separate implementation port, not merely a generated binding to ICU.

- **C1:** `Normalizer2` defines context-independent normalization boundaries and the conditions under which a prefix can be preserved while a suffix is normalized and appended.
- **C2:** Immutable normalizer instances support standard and custom mapping data through a common interface, including composition, decomposition, and specialized modes.
- **C3:** The inspected implementation returns the original string when possible, otherwise uses a small stack buffer or a larger `ValueStringBuilder`. This makes allocation policy and semantic fast paths easy to study in [Normalizer2.cs](https://raw.githubusercontent.com/NightOwl888/ICU4N/main/src/ICU4N/Text/Normalizer2.cs).

## Compact algorithms, normalization, and Unicode data

### 5. [JuliaStrings/utf8proc](https://github.com/JuliaStrings/utf8proc)

**Language/role:** C; a compact UTF-8 processing library with normalization, case operations, properties, and grapheme boundaries.

Study how a relatively small implementation combines strict byte decoding with generated property data and stateful Unicode rules.

- **C1:** The decoder rejects invalid continuation bytes, overlong encodings, surrogate encodings, and values outside the Unicode range. Grapheme processing carries state for regional indicators, emoji joiners, and Indic conjunct behavior; a pair of code points alone is insufficient for these rules.
- **C3:** Two-stage property lookup tables and encoded sequence indexes separate compact generated data from the algorithms that consume it. The stateful boundary routine reuses that common property representation. The [core implementation](https://raw.githubusercontent.com/JuliaStrings/utf8proc/master/utf8proc.c) shows both mechanisms directly.

A useful compatibility caveat appears in the same file: the low-level character encoder deliberately retains permissive surrogate behavior. Do not generalize the decoder’s validation guarantee to every low-level function.

### 6. [uni-algo/uni-algo](https://github.com/uni-algo/uni-algo)

**Language/role:** C++ with C-oriented low-level algorithms; conversion, normalization, casing, properties, and segmentation.

Study the split between constrained algorithm implementations and convenient string/range interfaces. The repository explains both whole-string functions and composable views, including the tradeoff between specialized loops and combining multiple transformations in one pass.

- **C1:** Malformed UTF handling is an explicit design requirement. A separate checked-array/iterator layer and constexpr testing address memory access failures; the documentation also distinguishes these checks from tests of logical correctness.
- **C2:** Algorithms operate on supplied text rather than requiring a new owning string type. Standard-string functions and range views expose the same core functionality to different use cases.
- **C3:** Data modules can be excluded, while the [safe-layer design](https://github.com/uni-algo/uni-algo/blob/main/doc/SAFE_LAYER.md) explains the runtime cost of bounds checks and why some checks can be optimized away.

The safe-layer document explicitly says range views do not yet use every part of that protection. The library’s simple collation facility should also not be mistaken for a full Unicode Collation Algorithm implementation.

### 7. [unicode-rs/unicode-normalization](https://github.com/unicode-rs/unicode-normalization)

**Language/role:** Rust; Unicode normalization exposed through iterator adapters.

Study deferred output: a normalizer cannot emit every decoded character immediately because later combining characters can affect canonical ordering.

- **C1:** The decomposition iterator documents separate free, ready, and pending buffer regions. Stable sorting preserves order within a combining class, and the ready-range invariant prevents access to unavailable output. The underlying iterator is fused to make repeated exhaustion safe.
- **C2:** Canonical and compatibility decomposition wrap arbitrary character iterators instead of requiring a particular input container.
- **C3:** A small inline `TinyVec` buffer and a custom buffer-compaction path address the common small-segment case. Comments explain why the output-state invariant permits fewer branches. These details are unusually accessible in [decompose.rs](https://raw.githubusercontent.com/unicode-rs/unicode-normalization/master/src/decompose.rs).

This is a strong small-codebase choice for studying how Unicode semantics constrain streaming and allocation behavior.

### 8. [dbuenzli/uunf](https://github.com/dbuenzli/uunf)

**Language/role:** OCaml; streaming Unicode normalization. **Official GitHub mirror:** the [author’s project page](https://erratique.ch/software/uunf) explicitly identifies it as such.

Study a small stateful protocol that is independent of both I/O and the application’s text representation.

- **C1:** The `Uchar`/`Await`/`End` protocol requires the caller to drain available output before supplying more input. Invalid call sequences raise an error. The documentation candidly explains why a legal but very long combining-mark sequence can require large buffering.
- **C2:** The same normalizer can process files, streams, or application-specific character sources without requiring the full input in memory. Combining-class and decomposition properties are also exposed for other algorithms. Start with the [Uunf API and protocol explanation](https://erratique.ch/software/uunf/doc/Uunf/index.html).
- **C4:** The [change history](https://github.com/dbuenzli/uunf/blob/master/CHANGES.md) spans releases from 2012 onward and records composition and stream-flushing fixes, adoption of `Uchar.t`, compiler compatibility, and a deprecated compatibility library after an internal reorganization.

### 9. [jacobsandlund/uucode](https://github.com/jacobsandlund/uucode)

**Language/role:** Zig; configurable Unicode properties, UTF-8 iteration, grapheme processing, and width-related extensions.

Study Unicode data generation as part of library architecture. Applications declare the properties they need and can determine how those properties are grouped and stored.

- **C2:** The component model declares input fields and produced fields, allowing custom derived properties alongside built-in Unicode data. Generic property access and grapheme iterators serve multiple consumers.
- **C3:** Build-time selection omits unused fields; configurable two- or three-stage tables and packed or unpacked rows expose space/access tradeoffs. The [table generator](https://github.com/jacobsandlund/uucode/blob/main/src/generate.zig), also available as [raw source](https://raw.githubusercontent.com/jacobsandlund/uucode/main/src/generate.zig), recursively determines required fields and components before generating storage.

The repository’s configuration examples explain the intended tradeoffs without requiring acceptance of a benchmark headline. This entry is selected for its data architecture; no claim of long-term API stability is made.

## UTF validation and character conversion

### 10. [simdutf/simdutf](https://github.com/simdutf/simdutf)

**Language/role:** C++; SIMD implementations of UTF validation and transcoding. Its Base64 functionality is outside this report’s focus.

Study how architecture-specific implementations fit behind a common dispatch layer, including the initialization behavior of a library that may be called before `main()`.

- **C1:** Validation and conversion must distinguish malformed byte sequences and encoding boundaries. The dispatch implementation additionally explains the static-initialization-order failure mode and the synchronization tradeoff involved in constructing implementation singletons.
- **C2:** A common interface exposes validation, conversion, and error-reporting operations across multiple Unicode encodings and machine architectures.
- **C3:** Runtime instruction-set detection chooses a supported implementation; a single-implementation build can avoid dispatch overhead. See [implementation.cpp](https://raw.githubusercontent.com/simdutf/simdutf/master/src/implementation.cpp).

The same source labels encoding autodetection as a guess: BOM handling and a successful UTF validator do not establish the original encoding with certainty. No numerical throughput claim is adopted here.

### 11. [nemtrif/utfcpp](https://github.com/nemtrif/utfcpp)

**Language/role:** C++; portable UTF-8/UTF-16 iteration and conversion using generic iterators.

Study a focused API in which decoding, advancing, reverse traversal, and replacement share a common validation core.

- **C1:** Checked functions distinguish insufficient input, malformed UTF-8, invalid code points, and invalid UTF-16. Replacement processing consumes the relevant malformed sequence, while reverse traversal must stop safely at the supplied boundary.
- **C2:** Iterator templates support caller-owned containers and output iterators; string conveniences build on those primitives. See [checked.h](https://raw.githubusercontent.com/nemtrif/utfcpp/master/source/utf8/checked.h).

The [release notes](https://github.com/nemtrif/utfcpp/releases) are a useful second entry point: they record fixes to UTF-16 exception behavior, compiler-dependent decoding optimizations, and accommodations for C++98/03 builds. They also illustrate why users should check the behavior of their selected release rather than assuming every historical checked API was equivalent.

### 12. [hsivonen/encoding_rs](https://github.com/hsivonen/encoding_rs)

**Language/role:** Rust; WHATWG character encodings, conversion to/from UTF-8 and UTF-16, and operations on in-memory text.

Study a converter designed around browser streaming and foreign-function integration. The author’s design discussion connects memory safety, encoding semantics, binary size, and workload-specific optimization.

- **C1:** Borrowing and temporary stack objects tie buffer-space checks to reads and writes in legacy CJK converters, enforcing an at-most-once relationship. The public interface also distinguishes streaming conversion from whole-input convenience operations.
- **C2:** A common encoder/decoder architecture supports web-compatible legacy encodings and both Rust’s UTF-8 and Gecko’s UTF-16 use cases.
- **C3:** ASCII fast paths and SIMD coexist with a deliberate decode-speed versus legacy-encode-table-size tradeoff. Optional faster encoding tables illustrate that the correct optimization depends on workload. Start with the [implementation design essay](https://hsivonen.fi/encoding_rs/).

Its WHATWG/browser scope is deliberate; it is not an implementation of every historical character set.

### 13. [pillarjs/iconv-lite](https://github.com/pillarjs/iconv-lite)

**Language/role:** JavaScript; character conversion implemented without requiring native iconv bindings.

Study a table-driven multibyte codec capable of handling mappings that are more complex than one input byte to one Unicode character.

- **C1:** The DBCS codec deals with surrogate pairs, incomplete surrogate state, GB18030 ranges, and mappings between one encoded character and a Unicode sequence. It also detects conflicting mapping-table entries.
- **C2:** Encoding-specific tables feed a shared codec implementation, keeping the conversion machinery reusable across related encodings.
- **C3:** Tables load on demand. Decoding uses a trie of integer arrays, encoding uses sparse buckets, and sequence objects are stored separately from the common direct mappings. These decisions are documented inline in [dbcs-codec.js](https://raw.githubusercontent.com/pillarjs/iconv-lite/master/encodings/dbcs-codec.js).

The canonical repository is now under `pillarjs`; older links under the original author should not be counted as another project.

## Bidirectionality, boundaries, and display width

### 14. [fribidi/fribidi](https://github.com/fribidi/fribidi)

**Language/role:** C; GNU FriBidi, implementing the Unicode Bidirectional Algorithm and related text operations.

Study the interaction of direction runs, embedding levels, isolates, and paired brackets. The convenience API can also return logical-to-visual and visual-to-logical position mappings needed by interactive text applications.

- **C1:** Run compaction must preserve isolate links and bracket identity. The source explicitly documents a dangling-pointer edge case found through fuzzing. See [fribidi-bidi.c](https://raw.githubusercontent.com/fribidi/fribidi/master/lib/fribidi-bidi.c).
- **C3:** The implementation groups text into runs and collects bracket pairs in a growable array instead of allocating each pair separately; those choices are explained alongside the relevant algorithm.
- **C4:** The [NEWS history](https://raw.githubusercontent.com/fribidi/fribidi/master/NEWS) documents evolution from work in 2004–2005 through successive Unicode updates, API/ABI concerns, restoration of a deprecated symbol, isolate fixes, fuzzing fixes, and a correction to the conformance-test runner itself.

This makes it especially useful for studying the maintenance of an algorithm whose specification and test coverage evolve.

### 15. [Tehreer/SheenBidi](https://github.com/Tehreer/SheenBidi)

**Language/role:** C; a separate implementation of bidirectional processing, with script and mirror locators.

Study an object-based C API that separates source text, paragraphs, lines, and directional runs. Its organization offers a useful comparison with FriBidi’s run-processing implementation.

- **C1:** The API maps successive Unicode rules onto paragraph analysis and line reordering. Construction validates the code-point sequence, and paragraph operations normalize requested ranges before creating paragraph objects.
- **C2:** `SBCodepointSequence` handles multiple UTF representations; algorithm, paragraph, and line objects expose reusable levels and runs rather than binding the library to a particular renderer. Mirror and script locators support subsequent layout work.

The repository’s API overview explains this division, while [SBAlgorithm.c](https://raw.githubusercontent.com/Tehreer/SheenBidi/master/Source/API/SBAlgorithm.c) shows the underlying allocation, cached bidi types, normalized ranges, and retain/release integration. Its output is material for layout engines, not a complete glyph-shaping or rendering system.

### 16. [adah1972/libunibreak](https://github.com/adah1972/libunibreak)

**Language/role:** C; Unicode line, word, and grapheme breaking. The inspected subsystem is line breaking.

Study how a standards algorithm combines a pair-action table with contextual rules that cannot be reduced to a simple adjacent-character lookup.

- **C1:** The line-breaking implementation distinguishes combining-mark handling and explicitly documents adjustments for joiners, regional indicators, and newer line-break classes. Its comments connect the action table and special processing to specific UAX #14 rules.
- **C2:** The interface supports UTF-8, UTF-16, and UTF-32 and distinguishes mandatory, permitted, prohibited, unfinished-character, and indeterminate outcomes. Per-code-point variants help consumers whose indexing differs from code-unit indexing.

Read [linebreak.c](https://raw.githubusercontent.com/adah1972/libunibreak/master/src/linebreak.c) beside the [public header](https://raw.githubusercontent.com/adah1972/libunibreak/master/src/linebreak.h). The separation of boundary detection from actual layout makes the implementation relevant to renderers, editors, and wrapping tools.

### 17. [rivo/uniseg](https://github.com/rivo/uniseg)

**Language/role:** Go; grapheme, word, sentence, and line segmentation, together with width calculation.

Study a single traversal that reports several boundary types and grapheme width while returning slices of the original input.

- **C1:** Grapheme, word, sentence, and line algorithms carry separate state encoded into nonoverlapping fields. The API documents the state-reuse contract and the mandatory boundary at end of input, which callers may need to distinguish from an actual trailing newline.
- **C2:** The low-level `Step`/`StepString` interface combines several results for consumers such as wrapping and cursor movement, while the package also offers more convenient grapheme iteration.
- **C3:** The step API returns input subslices without allocating and caches state/property information between calls. [step.go](https://raw.githubusercontent.com/rivo/uniseg/master/step.go) places the bit layout, public contract, and traversal next to one another.

Width remains a model of monospace display behavior; it should not be confused with font measurement.

### 18. [unicode-rs/unicode-segmentation](https://github.com/unicode-rs/unicode-segmentation)

**Language/role:** Rust; grapheme, word, and sentence boundaries. Focus on the grapheme cursor and iterators.

Study segmentation over text that is not necessarily a single contiguous string. This is particularly relevant to editors using ropes or other chunked storage.

- **C1:** The grapheme cursor preserves context for regional-indicator parity, emoji joiners, and Indic conjunct rules. Boundary decisions can require information before the current chunk, represented explicitly in the cursor’s state.
- **C2:** Ordinary grapheme and byte-offset iterators are built around the lower-level cursor, which is documented as supporting ropes and incompletely available text. Forward and reverse traversal share this abstraction.

Start with [grapheme.rs](https://raw.githubusercontent.com/unicode-rs/unicode-segmentation/master/src/grapheme.rs), particularly `GraphemeState`, `GraphemeCursor`, and the double-ended iterator implementation. The reusable abstraction is more substantial than merely splitting a string on a table lookup: it represents requests for the context needed to make a correct decision.

### 19. [jquast/wcwidth](https://github.com/jquast/wcwidth)

**Language/role:** Python and C11; terminal cell-width processing. The inspected implementation is the Python width engine.

Study where Unicode properties meet application-specific display conventions. Counting code points is insufficient for combining marks, emoji sequences, and terminal rendering differences.

- **C1:** Width processing handles variation selectors, regional indicators, emoji modifiers, joiners, viramas, and control-character outcomes. These interactions require sequence state rather than independent per-character addition.
- **C2:** The project offers primitive width functions and higher-level clipping, wrapping, alignment, and terminal-specific corrections.
- **C3:** An ASCII fast path avoids the general state machine, while interval-table searches handle Unicode properties. See [_wcswidth.py](https://raw.githubusercontent.com/jquast/wcwidth/master/wcwidth/_wcswidth.py).

A current compatibility detail matters: the inspected source retains the `unicode_version` parameter but documents it as ignored because only the latest data is shipped. The former single-file import surface remains in a [compatibility module](https://raw.githubusercontent.com/jquast/wcwidth/master/wcwidth/wcwidth.py). Terminal width is not a universal font-independent truth.

## Collation

### 20. [jgm/unicode-collation](https://github.com/jgm/unicode-collation)

**Language/role:** Haskell; an implementation of the Unicode Collation Algorithm with locale tailoring.

Study collation as an interaction between normalization, longest-prefix matching, implicit weights, and reusable sort keys. This provides a functional implementation perspective outside the larger ICU systems.

- **C1:** The change history explains a correction to discontiguous matching caused by assumptions that the default collation table did not satisfy. It also describes tests guarding implicit ideograph-weight ranges against drift in the shipped data.
- **C2:** Configurable collators and `collateWithUnpacker` extend the implementation beyond one concrete text representation.
- **C3:** Incremental normalization avoids processing unused suffixes; computing each sort key once avoids repeated work during sorting. The [implementation-oriented changelog](https://github.com/jgm/unicode-collation/blob/main/CHANGELOG.md) also records a benchmark correction from evaluating only the first list constructor to forcing a complete sort.

Limitations are explicit in the README: Unicode 13 data, less extensive testing of localized collations, and no collation reordering. Its older benchmark figures should not be treated as a current universal comparison.

## Encoding detection and repair

### 21. [hsivonen/chardetng](https://github.com/hsivonen/chardetng)

**Language/role:** Rust; heuristic detection of legacy web encodings.

Study a detector that first eliminates implausible encodings and then scores the remaining candidates. The repository documents why ASCII pairs usually contribute no score, allowing much HTML syntax to be ignored without parsing HTML.

- **C1:** Decoder errors, control characters, character-pair statistics, and script-specific penalties constrain candidate selection. The documented special cases demonstrate how superficially reasonable rules can misidentify another language or encoding.
- **C3:** The [author’s design essay](https://hsivonen.fi/chardetng/) explains reuse of existing CJK decoders and an explicit binary-size versus detection-work tradeoff. The README discusses why optional parallel detection can improve elapsed time while consuming more total CPU.

This is deliberately web-scoped: UTF-16 belongs to a separate BOM layer, and short-input weaknesses are documented. The current roadmap says detection-result improvements are not planned; retention here reflects the implementation’s study value, not an assumption of continuing accuracy expansion.

### 22. [chardet/chardet](https://github.com/chardet/chardet)

**Language/role:** Python with optional compiled acceleration; character encoding detection.

**Evolution context:** the current repository describes chardet 7 as a rewrite. Do not describe its present implementation as merely the old Mozilla prober architecture translated into Python.

- **C1:** The feed/close interface distinguishes a truly complete buffer from input truncated at a byte limit. It rejects feeding a closed detector before reset, preserves explicit truncation state, and documents that an individual detector instance is not thread-safe.
- **C2:** Streaming-shaped and one-shot interfaces use the same detection pipeline, with candidate filters, configurable fallbacks, and compatibility naming. This centralizes behavior while retaining familiar entry points.

Study [detector.py](https://raw.githubusercontent.com/chardet/chardet/main/src/chardet/detector.py): `feed` buffers up to its limit, and `close` runs the pipeline. It is therefore important to distinguish API-level incremental feeding from continuous incremental statistical evaluation. The [usage guide](https://github.com/chardet/chardet/blob/main/docs/usage.rst) explains encoding filters and compatibility options. Project-reported accuracy and speed comparisons are not independently validated here.

### 23. [jawah/charset_normalizer](https://github.com/jawah/charset_normalizer)

**Language/role:** Python; candidate decoding evaluated through text coherence and “mess” heuristics.

Study a different detection architecture from byte-prober ensembles. Candidate decodings are assessed as text, with configurable sampling and language-related coherence checks.

- **C1:** The implementation separates decoding failures from heuristic rejection, handles signatures and declared encodings, and adapts sampling for small inputs. A declaration changes priority without automatically proving a candidate correct.
- **C2:** Candidate inclusion/exclusion, thresholds, explanatory logging, and ranked match objects expose controls useful to different ingestion pipelines.
- **C3:** The implementation orders multibyte candidates strategically, uses lazy decoding for large payloads, and limits the lifetime of scoring caches to the operation. These choices are explained in [api.py](https://raw.githubusercontent.com/jawah/charset_normalizer/master/src/charset_normalizer/api.py).

Detection is still heuristic. The repository’s comparative benchmark claims depend on its chosen dataset and are not used as evidence that this detector universally outperforms another one.

### 24. [albfernandez/juniversalchardet](https://github.com/albfernandez/juniversalchardet)

**Language/role:** Java; a separately developed Java port of Mozilla’s universal charset detector.

Study the classic prober-ensemble design in contrast to chardet’s current rewrite and charset-normalizer’s decoded-text approach.

- **C1:** `UniversalDetector` distinguishes plain ASCII, escape-bearing ASCII, and high-byte input, performs BOM recognition, and uses confidence thresholds rather than claiming every input is identifiable. Resetting the detector must reset its constituent probers as well.
- **C2:** Escape, single-byte, multibyte, and Latin-1 probers sit behind a common detector interface. Incremental feeding, result listeners, and file/stream convenience APIs allow reuse in multiple Java I/O contexts.

Start with [UniversalDetector.java](https://raw.githubusercontent.com/albfernandez/juniversalchardet/master/src/main/java/org/mozilla/universalchardet/UniversalDetector.java). The repository’s usage examples also explain `handleData`, `dataEnd`, and `reset`. This is a substantive language port, not a second entry for the same upstream source tree; its heuristic output still requires application-level judgment.

### 25. [rspeer/python-ftfy](https://github.com/rspeer/python-ftfy)

**Language/role:** Python; repairing mojibake and related problems in text that has already been decoded.

Study repair as an explainable transformation process. Its task differs from guessing the encoding of an untouched byte stream: input can contain multiple decoding mistakes and subsequent edits.

- **C1:** The [heuristics documentation](https://ftfy.readthedocs.io/en/latest/heuristic.html) explains suspicious character contexts, stopping conditions, partial UTF-8 recovery, and why careless partial matches could recursively produce arbitrary characters. Avoiding false repairs is a central design constraint.
- **C2:** Configurable fixers and explanation plans allow callers to inspect transformations and reapply a plan to similarly damaged text.
- **C3:** Text is processed in bounded segments to avoid unbounded slowdowns. The [repair and explanation API](https://ftfy.readthedocs.io/en/latest/explain.html) explains both this limit and the distinction between per-segment repair and a single explanation for an entire string.

The useful lesson is how to expose a heuristic repair system’s decisions, not a guarantee that lost original bytes can always be reconstructed.

## Coverage and search notes

Discovery used more than six distinct live-search formulations: C/C++ normalization and malformed UTF handling; Rust encoding and ICU4X architecture; JavaScript/Python conversion and detection; C bidirectional and line-break engines; Go segmentation; Haskell/OCaml normalization and collation; Java/.NET ports; SIMD UTF processing; official GNU conversion-library mirrors; IDNA/Punycode; and Zig/Swift/Nim Unicode libraries. Follow-up searches emphasized compact tables, streaming interfaces, and less prominent implementations. Later searches increasingly returned already-covered engines, bindings around them, distribution mirrors, or adjacent applications. The Zig search added `uucode` because it supplied a distinct, inspectable data-generation design.

Every retained repository’s canonical GitHub page was opened. At least one additional primary implementation or documentation source was opened and read for each entry; README copies fetched through another URL were not counted as independent evidence. The linked files and guides supplied the concrete architectural grounds for the criterion assignments. Official mirrors are labeled, ICU4C/ICU4J are counted once, and independent language ports are identified as ports. No candidate code was cloned, installed, or executed, and no numerical performance comparison was reproduced as an independently established result.

Important exclusions and limitations:

- GNU libiconv and libunistring are highly relevant, but this search did not establish an official substantive GitHub mirror; third-party and packaging mirrors were not substituted for canonical projects.
- Thin ICU/simdutf/iconv wrappers, duplicated single-include distributions, general font-shaping/rendering engines, NLP tokenizers, and whole language runtimes were outside the selected scope. IDNA was searched but is represented mainly through the relevant ICU-family building blocks rather than a separate domain-name-library survey.
- `composewell/unicode-transforms` was investigated, including its published API, but implementation-source fetches repeatedly failed during this run. It was omitted rather than assigning architectural criteria from its performance README alone.
- Browser retrieval can expose differently aged snapshots of a README, source file, and release document. The report consequently avoids asserting a single latest Unicode version across projects. Particularly material scope differences—ICU4N’s older partial port, the collation library’s stated data baseline, and detector limitations—are called out individually.
- Criterion assignments and suggested study value are grounded engineering judgments drawn from the cited mechanisms. Conformance statements remain project statements unless the report explicitly describes inspected test machinery; this was a source review, not an independent audit or benchmark exercise.
