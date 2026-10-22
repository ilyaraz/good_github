# Locale, collation, and internationalization libraries

Research date: **2026-10-09**.

This report selects **26 GitHub repositories** for studying locale-sensitive ordering, CLDR data handling, language negotiation, grammatical messages, and translation runtimes. It includes independent algorithm implementations, broad internationalization engines, and reusable application libraries. ICU4C and ICU4J count together; other monorepos likewise count once. The selection concerns concrete engineering worth studying, not a claim that every component is exemplary or that each project is suitable for new production adoption.

Criteria legend:

- **C1 — Difficult correctness:** nontrivial invariants, concurrency, numerical or linguistic semantics, malformed inputs, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces and components supporting multiple applications and use cases.
- **C3 — Performance with structure:** explicit work on runtime cost, memory, loading, or compilation, with an understandable design.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility work, testing, or management of complexity. Age or a recent push alone does not qualify.

## Unicode engines and collation implementations

### 1. [unicode-org/icu](https://github.com/unicode-org/icu)

**C, C++, and Java — ICU4C/ICU4J internationalization engines.** Study the collation subsystem as a complete system: locale selection, tailoring rules, collation elements, comparison, and reusable sort keys.

- **C1:** Comparison must preserve ordering across primary, accent, and case levels; sort-key comparison must agree with direct comparison when collation settings agree. Locale fallback and normalization add further semantic constraints.
- **C2 / C3:** Collators expose both direct comparison and precomputed keys. The design explains compressed keys, partial keys, and the tradeoff between repeatedly comparing strings and storing their keys. These are useful designs for database indexes and search systems, not just UI sorting. See the [collation architecture guide](https://unicode-org.github.io/icu/userguide/collation/architecture.html).

The repository contains both language implementations and advertises exhaustive testing, fuzzing, and API comparison reports. Treat collation data/version compatibility as part of the application contract, rather than assuming persisted keys remain interchangeable indefinitely.

### 2. [unicode-org/icu4x](https://github.com/unicode-org/icu4x)

**Rust, with foreign-language interfaces — modular internationalization for constrained environments.** Study the boundary between algorithms and locale data rather than treating the entire CLDR dataset as an inseparable runtime dependency.

- **C2:** The data-provider design separates typed component data from its storage and delivery mechanism. Providers can compose, route requests, and support different data schemas.
- **C3:** The design explicitly moves pattern preprocessing out of runtime operations and discusses data slicing and configurable caching. The reasoning connects download size, I/O, and formatter construction cost. The [data-pipeline design](https://github.com/unicode-org/icu4x/blob/main/documents/design/data_pipeline.md) is an architectural entry point; its illustrative APIs should be read as design history, not assumed to be the current API verbatim.

The [documentation index](https://github.com/unicode-org/icu4x/tree/main/documents) also identifies benchmarking, data safety, locale fallback, and data-versioning material.

### 3. [boostorg/locale](https://github.com/boostorg/locale)

**C++ — locale facilities integrated with C++ abstractions and multiple backends.** Useful for understanding how to provide a coherent library over ICU, POSIX, Windows, and standard-library facilities with unequal capabilities.

- **C1:** Backends differ in supported calendars, encoding conversion, case handling, and collation levels. The documentation identifies concrete platform limitations and standard-library bugs that the adapter must accommodate.
- **C2:** A backend manager and locale generator allow selection by operation category, including mixing backends in one configuration. This is substantial portability architecture rather than a generated ICU binding. The [backend guide](https://www.boost.org/doc/libs/latest/libs/locale/doc/html/using_localization_backends.html) provides both the capability matrix and composition examples.

The same guide explains dependency-size and performance motivations, but its platform-specific observations should not be treated as fresh comparative benchmarks.

### 4. [golang/text](https://github.com/golang/text)

**Go — official GitHub mirror of Go's extended text libraries.** Relevant subsystems include `collate` and `language`; the repository also contains other text processing components.

- **C1:** The collator implements multi-level weights, reverse secondary traversal, variable-weight handling, and locale/options selection. The source makes the semantics visible instead of delegating the entire algorithm to a native library.
- **C3:** Reusable buffers, embedded iterator storage, and compact variable-length primary weights reduce allocation and key size. The key API explicitly documents the lifetime of returned slices. Start with [collate.go](https://raw.githubusercontent.com/golang/text/master/collate/collate.go).

**Limitation:** That source explicitly pins collation generation to CLDR 23/Unicode 6.2 and records incompatibility with later CLDR versions. Do not infer current collation coverage from the broader repository's activity. This is an official mirror, not an independent fork.

### 5. [twitter/twitter-cldr-rb](https://github.com/twitter/twitter-cldr-rb)

**Ruby — CLDR formatting, collation, normalization, and related locale services.** The collator provides an accessible implementation of fractional collation elements and locale tailoring.

- **C1:** Trie matching must recover contractions involving non-starters after canonical normalization, including blocking by combining class. Explicit and implicit collation elements are handled separately.
- **C2 / C3:** Comparison, sorting, and sort-key generation share a collator abstraction. Tailored tries are cached; sorting can compute keys once. The [collator implementation](https://raw.githubusercontent.com/twitter/twitter-cldr-rb/master/lib/twitter_cldr/collation/collator.rb) exposes these choices and candidly discusses normalization cost.

**Limitation:** The [README's collation section](https://github.com/twitter/twitter-cldr-rb/blob/master/README.md#sorting-collation) acknowledges failures in some Unicode collation tests. Its broader localization API should not be mistaken for an unconditional conformance guarantee.

### 6. [jtauber/pyuca](https://github.com/jtauber/pyuca)

**Python — compact, independent Unicode Collation Algorithm implementation.** A good smaller codebase for following an ordering algorithm end to end.

- **C1:** The implementation combines NFD normalization, longest-prefix trie lookup, non-starter handling, and implicit weights for code points absent from the table. It distinguishes Unicode-version-specific CJK ranges.
- **C2:** A shared collator core accepts alternative collation-element tables, produces reusable sort keys, and supports version-specific collators. See [collator.py](https://raw.githubusercontent.com/jtauber/pyuca/master/pyuca/collator.py).

**Scope limit:** The repository documents non-ignorable conformance tests through Unicode 10.0, not current Unicode coverage or comprehensive locale-tailoring selection. Its value here is a readable algorithm implementation; use the documented version limits when evaluating adoption.

### 7. [jgm/unicode-collation](https://github.com/jgm/unicode-collation)

**Haskell — pure Unicode collation with locale-specific tailoring.** This adds a functional implementation with a particularly clear relationship between laziness and comparison cost.

- **C1:** Collator options control variable weighting, reversed accents, normalization, and case ordering; language tags select tailorings with fallback. Study [Collator.hs](https://github.com/jgm/unicode-collation/blob/main/src/Text/Collate/Collator.hs).
- **C3:** The library implements lazy NFD decomposition so a comparison can stop before normalizing the entire input. It also specializes short combining-mark runs and handles Hangul decomposition algorithmically. See [Normalize.hs](https://github.com/jgm/unicode-collation/blob/main/src/Text/Collate/Normalize.hs).

**Limitations:** The README identifies Unicode 13 data, states that localized collations receive less extensive testing than root UCA conformance, and does not support collation reordering. Its workload-dependent performance discussion is useful; no benchmark ranking is inferred here.

## CLDR data, formatting, and parsing

### 8. [python-babel/babel](https://github.com/python-babel/babel)

**Python — locale data, date/number formatting, and message-catalog tooling.** Study how an application-facing locale API is backed by inherited, aliased data without depending on the process-wide C locale.

- **C1 / C2:** Locale loading combines recursive parent inheritance, exceptional parents, alias resolution, nested overrides, and a reentrant cache lock. `LocaleDataDict` provides a reusable mapping that resolves aliases in the appropriate locale context. See [localedata.py](https://raw.githubusercontent.com/python-babel/babel/master/babel/localedata.py).
- **C4:** The [changelog](https://github.com/python-babel/babel/blob/master/CHANGES.rst) documents evolution from 2013–2015 releases through 2026: Python compatibility, CLDR migrations, likely-subtag fixes, plural-format validation, and continuing test refactoring. This is concrete compatibility and correctness work over time, not just longevity.

### 9. [phensley/cldr-engine](https://github.com/phensley/cldr-engine)

**TypeScript — broad CLDR formatting engine; archived at the research date.** Retained as an architectural study candidate, especially for resource delivery to browser clients.

- **C2:** A typed schema separates access to calendar, number, unit, and other locale fields from the physical representation of resource packs.
- **C3:** The [resource-bundle design](https://phensley.github.io/cldr-engine/docs/en/doc-design-bundles) explains why nested CLDR JSON costs transfer bytes and heap space, then develops flattened data, deterministic field ordering, and typed accessors. The reasoning is substantially more informative than a bundle-size claim alone.

The [README](https://github.com/phensley/cldr-engine/blob/main/README.md) distinguishes public API compatibility from resource-pack schema compatibility and lists independently usable language-tag, decimal, plural, and message packages. Count the monorepo once. Archival status was checked through GitHub repository metadata.

### 10. [globalizejs/globalize](https://github.com/globalizejs/globalize)

**JavaScript — CLDR-driven formatting and parsing for browsers and Node.js.** Study an architecture where applications supply locale data separately from the library's algorithm modules.

- **C1:** Number parsing reverses localized digit/symbol mappings, recognizes sign affixes and infinities, requires complete grammar consumption, and applies percent/per-mille scaling. Invalid inputs produce `NaN`. See [number/parse.js](https://github.com/globalizejs/globalize/blob/master/src/number/parse.js).
- **C2 / C3:** Date, number, currency, plural, and message modules share externally loaded CLDR data. Per-value parsing accepts reduced, preprocessed locale properties. The [repository guide](https://github.com/globalizejs/globalize#why-globalize) describes this modular code/data separation and its compilation/runtime model.

This is useful to compare with libraries that delegate most formatting to native `Intl`; cross-environment consistency and data ownership are different design choices.

### 11. [dart-lang/i18n](https://github.com/dart-lang/i18n)

**Dart — internationalization monorepo; focus on `pkgs/intl`.** This is the current repository location for the traditional Dart `intl` package, alongside newer localization packages.

- **C1:** Number parsing must distinguish overlapping positive/negative affixes, localized digits, decimal and grouping symbols, special values, scaling, and unconsumed input. The state machine is visible in [number_parser_base.dart](https://github.com/dart-lang/i18n/blob/main/pkgs/intl/lib/src/intl/number_parser_base.dart).
- **C2:** The parser separates locale-sensitive normalization from the result representation through an abstract generic base. The concrete [number_parser.dart](https://raw.githubusercontent.com/dart-lang/i18n/main/pkgs/intl/lib/src/intl/number_parser.dart) supplies integer/double conversion and scaling. This sits within a broader package for messages, dates, numbers, and bidirectional text.

Study the state transitions as well as the public convenience APIs; inclusion does not certify every parsing edge case.

### 12. [elixir-localize/localize](https://github.com/elixir-localize/localize)

**Elixir — consolidated locale formatting, validation, collation, and message services.** The successor to the `ex_cldr_*` family replaces application-specific generated backend modules with runtime-loaded data.

- **C1 / C3:** A loader GenServer serializes first loads and rechecks cached data to avoid duplicate loading under concurrent requests; cache hits bypass the server. See [data_loader.ex](https://github.com/elixir-localize/localize/blob/main/lib/localize/data_loader.ex).
- **C2 / C3:** Compiled number/date patterns share a protected ETS cache. Writes go through its owner so eviction can enforce a size bound, while reads access ETS directly. The explicit rejection of full LRU bookkeeping is an instructive cost tradeoff. See [format_cache.ex](https://github.com/elixir-localize/localize/blob/main/lib/localize/format_cache.ex).

The repository describes a broad common locale API. These concurrency and storage mechanisms provide qualification without assuming that the newer project's history independently establishes C4.

## Language negotiation and grammatical message systems

### 13. [rspeer/langcodes](https://github.com/rspeer/langcodes)

**Python — language-tag normalization, equivalence, and matching.** Study why locale matching cannot be reduced to splitting a tag at its first hyphen.

- **C1:** Standardization accounts for deprecated aliases, redundant scripts, macrolanguages, and language/script/territory distinctions. The [repository documentation](https://github.com/rspeer/langcodes#standardizing-language-tags) supplies concrete examples such as replacing `sh` with `sr-Latn`.
- **C2 / C3:** A reusable language-distance layer separates matching from tag representation and caches comparisons of maximized triples. [language_distance.py](https://github.com/rspeer/langcodes/blob/master/langcodes/language_distance.py) shows language-conditioned script distances and region clusters rather than uniform edit distance.

**Limitation:** The inspected distance implementation explicitly hard-codes territory rules based on CLDR 36.1. Its scores are application-oriented matching heuristics, not measurements of linguistic similarity or a promise to track every later CLDR rule automatically.

### 14. [salesforce/grammaticus](https://github.com/salesforce/grammaticus)

**Java — grammatical labels with user-renamable nouns; an offline JavaScript engine is also present.** The motivating problem is changing “Account” to “Client” while retaining correct articles and inflected surrounding text.

- **C1:** Grammar depends on gender, number, case, possession, and initial/final sounds. [EnglishDeclension.java](https://github.com/salesforce/grammaticus/blob/main/src/main/java/com/force/i18n/grammar/impl/EnglishDeclension.java) demonstrates article-form selection and validation; the broader model supports substantially richer languages.
- **C2:** [LanguageDeclension.java](https://github.com/salesforce/grammaticus/blob/main/src/main/java/com/force/i18n/grammar/LanguageDeclension.java) defines reusable noun, article, and adjective forms, allowed/required grammatical dimensions, and language-specific behavior. This is an extensible grammar abstraction, not a bag of translated strings.

The README candidly identifies incomplete declensions, limitations around verbs and partitive articles, and beta offline JavaScript support. Engineers must supply appropriate grammatical metadata for renamed nouns.

### 15. [messageformat/messageformat](https://github.com/messageformat/messageformat)

**TypeScript/JavaScript — ICU MessageFormat 1 compilation and Unicode MessageFormat 2 parsing/runtime.** Count the MF1 and MF2 package families as one monorepo.

- **C1:** The MF1 compiler tracks plural context and offsets, checks required `other` branches, validates runtime identifiers, and prevents collisions between locale and formatter functions.
- **C2 / C3:** It recursively compiles locale-keyed message trees, supports custom formatters, and records the runtime dependencies required by emitted functions. Study [compiler.ts](https://github.com/messageformat/messageformat/blob/main/mf1/packages/core/src/compiler.ts).

The [repository package map](https://github.com/messageformat/messageformat#unicode-messageformat-2) distinguishes the newer MF2 runtime and format-conversion packages from the MF1 compiler. This is useful for studying coexistence of message-format generations without counting each package separately.

### 16. [projectfluent/fluent.js](https://github.com/projectfluent/fluent.js)

**JavaScript/TypeScript — Fluent messages, language negotiation, and UI integrations.** Study translation as a small executable language with recoverable failures.

- **C1:** The resolver distinguishes message/term references, argument scopes, exact numeric matches, plural categories, and default variants. It limits expanded placeables against explosive expansion and attempts to preserve useful output on errors.
- **C2 / C3:** Resolution operates through shared value and scope abstractions; custom functions and memoized `Intl` objects integrate formatting without baking every operation into syntax. See [resolver.ts](https://raw.githubusercontent.com/projectfluent/fluent.js/main/fluent-bundle/src/resolver.ts).

The repository separates syntax, bundles, negotiation, DOM, and React packages. Its implementation is independently substantive from the Rust implementation below.

### 17. [projectfluent/fluent-rs](https://github.com/projectfluent/fluent-rs)

**Rust — independent Fluent implementation with resource and fallback layers.** Especially useful for comparing ownership and allocation decisions with a garbage-collected implementation of the same language.

- **C1:** Resolution state tracks visited patterns to detect cycles, counts placeables for expansion protection, and accumulates errors while writing fallback representations.
- **C3:** The resolver lazily creates tracking state for complex references, allowing simple resolutions to take a shorter path; it uses small inline storage for the traversal stack. Inspect [resolver/scope.rs](https://raw.githubusercontent.com/projectfluent/fluent-rs/main/fluent-bundle/src/resolver/scope.rs).

**C2** is also supported by the repository's separation into syntax/AST, locale bundles, fallback lifecycle, resource management, pseudolocalization, and formatter memoization crates. This is a separate language implementation, not a fork counted twice.

## Browser and application message frameworks

### 18. [formatjs/formatjs](https://github.com/formatjs/formatjs)

**Primarily TypeScript/JavaScript, with additional native work — formatting, message parsing, `Intl` polyfills, and framework integration.** Focus on `packages/intl-messageformat` as a tractable slice of the larger monorepo.

- **C1:** [formatters.ts](https://github.com/formatjs/formatjs/blob/main/packages/intl-messageformat/formatters.ts) handles nested selects/plurals, exact numeric branches, offsets, rich-text callbacks, missing arguments, and prototype-sensitive option keys. It also exposes the differing numerical constraints of BigInt formatting and plural selection.
- **C2 / C3:** A common formatter interface supports injected implementations and structured output parts. [core.ts](https://github.com/formatjs/formatjs/blob/main/packages/intl-messageformat/core.ts) accepts strings or pre-parsed ASTs, memoizes number/date/plural formatter instances, and provides a simple-message fast path.

The older standalone `intl-messageformat` repository was migrated into this monorepo and is not counted separately.

### 19. [i18next/i18next](https://github.com/i18next/i18next)

**JavaScript/TypeScript interfaces — extensible application translation runtime.** The resource-loading machinery is a particularly useful study beyond the familiar translation function.

- **C1:** Concurrent requests for the same language/namespace share pending state. Completion processing consolidates results and errors and prevents repeated completion callbacks.
- **C2 / C3:** Backends can expose synchronous, callback, or promise-based reads. The connector limits parallel reads and retries transient failures with increasing delays, explicitly addressing socket/file-descriptor pressure. See [BackendConnector.js](https://raw.githubusercontent.com/i18next/i18next/master/src/BackendConnector.js).

These mechanisms explain how a reusable translation core can serve multiple frontend frameworks and loading strategies without making resource transport part of the translation API itself.

### 20. [lingui/js-lingui](https://github.com/lingui/js-lingui)

**TypeScript/JavaScript — extraction, compile-time macros, catalog compilation, and runtime translation.** Study the boundary between translator-friendly ICU messages and a smaller compiled runtime representation.

- **C1:** The runtime preserves plural offsets and `#` substitution semantics, handles nested choices and escapes, and checks own properties when selecting branches such as `constructor`. See [interpolate.ts](https://raw.githubusercontent.com/lingui/js-lingui/main/packages/core/src/interpolate.ts).
- **C2 / C3:** Shared compiled messages support a framework-independent core and multiple UI integrations. The [repository workflow](https://github.com/lingui/js-lingui#why-lingui) explains extraction into catalogs and ahead-of-time compilation so the MessageFormat parser need not ship in the runtime.

The study value is the compiler/runtime contract and rich-text handling, rather than the headline compressed-size number.

## Catalog runtimes and translation backends

### 21. [ruby-i18n/i18n](https://github.com/ruby-i18n/i18n)

**Ruby — translation/localization API with composable backends.** Study a small public API whose behavior must remain consistent across optional fallback, caching, pluralization, and storage extensions.

- **C1:** Fallback ordering interacts with symbols, strings, procs, explicit `nil`, and recursive resolution. The implementation carries the original locale through fallback resolution and avoids re-entering a fallback loop. See [backend/fallbacks.rb](https://github.com/ruby-i18n/i18n/blob/master/lib/i18n/backend/fallbacks.rb).
- **C2:** Features compose as backend modules rather than requiring an entirely different public API. The [test-suite explanation](https://github.com/ruby-i18n/i18n#tests) describes reusing the same API tests across combinations of backends and optimization modules, providing concrete evidence for the abstraction's contract.

### 22. [nicksnyder/go-i18n](https://github.com/nicksnyder/go-i18n)

**Go — application message bundles, preference-based localizers, and extraction/merge tools.** Study the separation between long-lived catalog data and a localizer for a particular set of language preferences.

- **C1:** Missing translations, incomplete plural forms, invalid plural operands, and mismatched message IDs have distinct behavior. Localization can return useful fallback text together with an error, preserving both availability and diagnostic information.
- **C2:** Bundles accept custom unmarshallers; localizers accept language preferences and `Accept-Language` values; template parsing is replaceable. [localizer.go](https://github.com/nicksnyder/go-i18n/blob/main/i18n/localizer.go) shows the lookup, template, and fallback boundaries.

The source also documents an order-sensitive language-matching caveat. The repository explains that plural code and tests are generated from CLDR, while its extraction/merge workflow maintains translation catalogs.

### 23. [leonelquinteros/gotext](https://github.com/leonelquinteros/gotext)

**Go — native GNU gettext PO/MO catalogs and plural-expression support.** Complementary to go-i18n: its core concern is interoperability with gettext catalog formats and contexts.

- **C1:** The MO parser detects byte order, validates revision and directory/string bounds using widened arithmetic, and checks all string spans before adding translations. Parsing acquires translation and plural locks. See [mo.go](https://github.com/leonelquinteros/gotext/blob/master/mo.go).
- **C2:** A shared domain abstraction supplies singular, plural, contextual, and combined lookups across catalog representations; MO objects support `fs.FS` loading and binary serialization. The same source shows delegation and compatibility-preserving public fields.

This is a useful study of binary parsing and concurrent catalog access. The inspected implementation silently returns on malformed data, which is an API behavior consumers should understand.

### 24. [elixir-gettext/gettext](https://github.com/elixir-gettext/gettext)

**Elixir — gettext extraction, PO compilation, and backend runtime.** Study how a familiar catalog format becomes generated BEAM code while preserving the gettext fallback contract.

- **C1:** Compile-time message validation supports extraction, while generated catch-all clauses route missing singular/plural translations to backend handlers. The compiler deliberately logs invalid domain separators instead of changing unknown-message behavior into an exception.
- **C2 / C3:** Backends configure domains, locales, interpolation, and missing-message behavior. The compiler tracks PO resources and generates lookup functions and recompilation checks, moving work from each lookup to compilation. See [compiler.ex](https://github.com/elixir-gettext/gettext/blob/main/lib/gettext/compiler.ex).

The repository's macro-based extraction and template-merging workflow provides the surrounding lifecycle; this is an Elixir implementation of gettext, not a wrapper around a native libintl call.

### 25. [symfony/translation](https://github.com/symfony/translation)

**PHP — official standalone component split from Symfony's monorepo.** Study message catalogs as mergeable resources with fallback graphs and metadata, usable independently of the full framework.

- **C1:** Catalog merging rejects incompatible locales. Fallback insertion checks for circular references and propagates resources through the parent chain; ICU-domain and ordinary-domain messages have explicit precedence. See [MessageCatalogue.php](https://github.com/symfony/translation/blob/8.2/MessageCatalogue.php).
- **C2:** Catalog interfaces separate lookup, resource tracking, message metadata, and catalog metadata. The repository's loader, dumper, extractor, formatter, and provider families build on that common model.

This is an official component distribution with development directed to the main Symfony repository, not an independent fork. The inspected `8.2` branch is a development snapshot; the entry does not imply that it is the currently recommended stable release.

### 26. [VitaliiTsilnyk/NGettext](https://github.com/VitaliiTsilnyk/NGettext)

**C# — managed gettext catalogs for .NET; historical study candidate.** GitHub metadata showed no archival flag but a last push in April 2022. Current maintenance is not assumed.

- **C1:** The [MO parser](https://github.com/VitaliiTsilnyk/NGettext/blob/master/src/NGettext/Loaders/MoFileParser.cs) handles byte-order detection, format revisions, string-offset tables, NUL-separated plural forms, and charset changes from catalog headers. It explicitly omits hash tables and system-dependent segments.
- **C2:** Catalog loading and plural-rule construction are replaceable. [MoAstPluralLoader.cs](https://github.com/VitaliiTsilnyk/NGettext/blob/master/src/NGettext/Loaders/MoAstPluralLoader.cs) composes a loader, parser, and AST plural-rule generator for file or stream input. The public catalog model supports multiple cultures and domains in one process.

Its value is the managed implementation and abstraction boundaries; inclusion does not assert comprehensive hardening against hostile catalog files or compatibility with every modern .NET target.

## Coverage, verification, and limitations

Discovery used more than six distinct live-search formulations: ICU/ICU4X/Boost/Go architecture; Python CLDR and UCA implementations; JavaScript Fluent/MessageFormat systems; Elixir CLDR/gettext; Ruby collation; independent Java engines; Dart internationalization; .NET/PHP gettext; Haskell/Perl collation; and OCaml/native C/C++ alternatives. Follow-up searches found the Haskell implementation and clarified successor projects. Later results increasingly repeated ICU and Boost or returned thin wrappers, demos, and integrations rather than distinct substantial engines.

Every selected canonical repository URL was checked through its GitHub page and/or GitHub repository API data. Each entry additionally has an opened implementation or architectural source beyond its root README. Repository metadata was checked for archival status and canonical names. No candidate code was executed, dependencies installed, or repositories cloned. Sources are branch snapshots inspected on the research date; they can change after this report.

Important selection decisions:

- **Monorepos and mirrors:** ICU4C/ICU4J, FormatJS packages, MF1/MF2 packages, and Dart packages are each counted once. Go's official mirror and Symfony's official component split are labeled. Fluent's JavaScript and Rust implementations have separate substantive runtimes and are retained separately.
- **Moved or superseded locations:** Old standalone FormatJS and Dart package repositories are excluded in favor of their current monorepos. For Elixir CLDR, this report selects Localize rather than double-counting its predecessor family. The predecessor organization states that `ex_cldr_*` receives bug-fix support through December 2027 and encourages migration; its generated-backend architecture differs from the successor's runtime data model. See the [official transition notice](https://github.com/elixir-cldr#future-support).
- **Boundary exclusions:** Translation-management applications, localization SaaS clients, data-only locale collections, generic Unicode utilities without a strong locale/i18n subsystem, generated bindings, tutorials, and awesome-lists were not included merely for matching keywords. GNU gettext and libunistring are relevant background, but no additional unofficial GitHub mirror was promoted as a canonical implementation.
- **Limits:** The search is broad but not exhaustive, particularly for Perl, OCaml, and smaller regional communities. Conformance and performance observations are attributed to inspected code or project documentation, not independently reproduced benchmarks. Explicit older-data limits, archival status, and historical maintenance status remain part of the selection. C1–C4 assignments and suggestions about what to study are engineering judgments grounded in those sources, not audits of the entire repositories.
