# API and ABI compatibility checking tools

Research date: **2026-10-09**

This selection covers **22 GitHub repositories** that implement compatibility analysis: native library ABI/API comparison, language-specific library evolution, compiler-integrated checking, and compatibility of network API schemas. It includes both standalone tools and clearly identified subsystems of larger repositories. Source compatibility, binary compatibility, serialized-data compatibility, and API snapshot equality are different contracts; entries identify the contract they actually examine. Snapshot tools are included where their extraction and comparison machinery is substantial, with their classification limits made explicit.

The criteria below are engineering judgments grounded in the cited implementation and documentation, not certifications of correctness or claims that every component is exemplary. Repository pages and additional primary material were opened and read. No candidate code was executed, dependencies installed, or repositories cloned. Maintenance claims are limited to explicit upstream notices; an unarchived repository alone is not evidence of active maintenance.

## Criteria legend

- **C1 — Difficult correctness:** nontrivial language, layout, type-system, recursion, visibility, or failure-mode invariants.
- **C2 — Reusable abstractions:** substantial representations, analysis frameworks, or libraries supporting multiple kinds of compatibility checks and integrations.
- **C3 — Performance with structure:** concrete measures to control repeated work, memory, or analysis cost without obscuring the architecture.
- **C4 — Sustained evolution:** evidence spanning years of compatibility adaptation, regression handling, or complexity management; age and recent activity alone do not qualify.

## Native interfaces and compiler-integrated checking

### 1. [lvc/abi-compliance-checker](https://github.com/lvc/abi-compliance-checker)

**Language / role:** Perl; C/C++ source and binary compatibility checker.

Study the distinction between a header-level API and the interface emitted under a compiler ABI. ABICC accepts descriptions of headers and libraries or previously extracted ABI dumps, and produces separate assessments of changes such as calling conventions, virtual tables, and fields. Its repository documents use as the analysis core of ABI Tracker.

- **C1:** The regression machinery constructs old/new C and C++ libraries with deliberately changed declarations. Cases include const qualification, visibility, removed overloads, and changed inline signatures, making compiler-dependent compatibility rules inspectable through concrete fixtures. Start with [the regression generator](https://github.com/lvc/abi-compliance-checker/blob/master/modules/Internals/RegTests.pm).
- **C2:** The dump/compare boundary permits extraction and comparison to be separate operations, including consumption of dumps from ABI Dumper. Library descriptors and public-header filtering make the same engine applicable to different libraries and release pipelines. The [repository usage and test documentation](https://github.com/lvc/abi-compliance-checker#usage) explains that boundary.

This review establishes a substantive implementation and test corpus, without making a claim about current release cadence.

### 2. [abicheck/abicheck](https://github.com/abicheck/abicheck)

**Language / role:** Python; C/C++ compatibility analysis combining binary metadata, debug information, and header AST evidence.

Study how a checker represents missing evidence and combines findings from different information sources. This is an alternative implementation with explicit architectural migration debt; its published cross-tool benchmark rankings are not treated here as independently verified results.

- **C1:** The [virtual-table reconstruction implementation](https://github.com/abicheck/abicheck/blob/main/abicheck/diff_vtable_layout.py) detects effects of a base becoming polymorphic on a derived class's secondary vtable groups, and virtual-base reorderings. Its tri-state reasoning avoids concluding that a base is non-polymorphic merely because its type information is absent.
- **C2:** Shared snapshots and detector registration support multiple evidence levels. The [architecture contract](https://github.com/abicheck/abicheck/blob/main/architecture/README.md) separates responsibility packages, allowed dependency directions, public compatibility surfaces, and temporary migration debt, with machine-checkable enforcement. This is useful material for studying how a growing analysis engine manages its internal boundaries.

No C4 claim is made for this project.

### 3. [swiftlang/swift](https://github.com/swiftlang/swift)

**Language / role:** C++ implementation with Swift fixtures; the **API Digester** subsystem of the Swift compiler repository.

Study a compiler-integrated checker that extracts declaration trees into JSON baselines and then matches and diagnoses differences. Only API Digester is the subject of this entry; the whole compiler is counted once.

- **C1:** The [digester implementation](https://github.com/swiftlang/swift/blob/main/lib/DriverTool/swift_api_digester_main.cpp) uses declaration identity and structural matching, and distinguishes API from ABI mode. For example, adding a declaration with fixed binary order to a non-resilient type can be an ABI break. It also handles client-emitted declarations specially when checking ABI removal.
- **C2:** Extraction, serialized baselines, matching, and diagnostics are separate stages over SDK-node representations. That lets the tool compare stored module surfaces and serve compiler regression workflows. The [module-dump test](https://github.com/swiftlang/swift/blob/main/test/api-digester/dump-module.swift) exercises API/ABI dumps, comparison, and serialization round trips.

### 4. [dotnet/sdk](https://github.com/dotnet/sdk)

**Language / role:** C#; **ApiCompat and package validation** under `src/Compatibility/ApiCompat`.

Study compatibility checking across assemblies, previous package versions, and target frameworks. The [official overview](https://learn.microsoft.com/en-us/dotnet/fundamentals/apicompat/overview) distinguishes ordinary compatibility checks from strict equality checks and describes CLI and MSBuild integration.

- **C1:** [Generic-constraint checking](https://github.com/dotnet/sdk/blob/main/src/Compatibility/ApiCompat/Microsoft.DotNet.ApiCompatibility/Rules/CannotChangeGenericConstraints.cs) distinguishes sealed types and non-virtual methods, where some constraint removals are permitted, from extensible types and virtual methods. Strict mode changes those rules. This is a concrete example of compatibility depending on whether downstream code can implement or override an API.
- **C2:** [ApiComparer](https://github.com/dotnet/sdk/blob/main/src/Compatibility/ApiCompat/Microsoft.DotNet.ApiCompatibility/ApiComparer.cs) operates on Roslyn symbols through mapper and difference-visitor factories, with comparisons against multiple right-hand assemblies or assembly sets. The engine is reusable beneath command-line, build-task, and package-validation entry points.

The repository is included for this subsystem, not for unrelated SDK functionality.

## JVM libraries: bytecode, source signatures, and Scala metadata

### 5. [siom79/japicmp](https://github.com/siom79/japicmp)

**Language / role:** Java; comparison of JAR APIs and binary compatibility.

Study direct classfile analysis using Javassist rather than loading the examined application through reflection. The project distinguishes binary and source changes and exposes the comparison result as a Java model, alongside CLI and build integrations.

- **C1:** [CompatibilityChanges](https://github.com/siom79/japicmp/blob/master/japicmp/src/main/java/japicmp/compat/CompatibilityChanges.java) handles inherited members, members moved to superclasses, access changes, generic signatures, and covariant returns. The latter requires considering generated bridge methods rather than treating every return-type change identically.
- **C2:** The [documented library interface](https://github.com/siom79/japicmp#readme) separates `JarArchiveComparator` and comparison options from reports and Maven/Ant integration. Consumers can inspect structured `JApiClass` results instead of scraping command output, and apply visibility or annotation-based selection.

The README contains a timing example, but this report makes no numerical performance claim from it.

### 6. [revapi/revapi](https://github.com/revapi/revapi)

**Language / role:** Java; extensible API-analysis framework, with Java, JSON, and YAML analyzers in the repository.

Study how to build compatibility checking as an analysis framework rather than bind every layer to one artifact format. Its Java implementation is particularly useful for understanding language-model-based comparisons.

- **C1:** The [formal type-parameter check](https://github.com/revapi/revapi/blob/main/revapi-java/src/main/java/org/revapi/java/checks/generics/FormalTypeParametersChanged.java) checks accessible classes and methods, aligns parameter lists, compares their unique type representations, and distinguishes added, removed, and changed parameters. Compatibility analysis must account for these generic contracts as well as ordinary member presence.
- **C2:** [ApiAnalyzer](https://github.com/revapi/revapi/blob/main/revapi/src/main/java/org/revapi/ApiAnalyzer.java) defines a reusable boundary between archive extraction, element forests, correspondence ordering, and pairwise difference analysis. That interface explains how analyzers for non-Java API artifacts participate in the same framework.

### 7. [scala-garden/mima](https://github.com/scala-garden/mima)

**Language / role:** Scala; MiMa, a binary compatibility checker for Scala libraries.

Study the consequences of Scala compilation strategies at the JVM linkage boundary. MiMa compares classfiles to identify changes capable of causing linkage errors. Its documented scope excludes behavioral equivalence and does not equate binary compatibility with source compatibility.

- **C1:** The [problem model](https://github.com/scala-garden/mima/blob/main/core/src/main/scala/com/typesafe/tools/mima/core/Problems.scala) includes incompatible member descriptors, cyclic type references, inherited abstract methods, and mixin-forwarder changes. These represent failures that a simple public-method-name diff would miss.
- **C2:** The same model supplies structured problem families, matching signatures, descriptions, and filter instructions. The [usage and filtering guide](https://github.com/scala-garden/mima#filtering-binary-incompatibilities) shows how this representation supports a standalone CLI, sbt checks, and project-specific exclusions.

The canonical URL verified during research is `scala-garden/mima`; older owner paths should not be counted as separate projects.

### 8. [scalacenter/tasty-mima](https://github.com/scalacenter/tasty-mima)

**Language / role:** Scala with a Java-facing interface; Scala 3 TASTy compatibility checking.

Study a compatibility dimension that bytecode comparison misses: retypechecking previously compiled TASTy during inline or macro expansion. The repository explains why changing a sequence parameter to varargs can remain binary compatible yet invalidate downstream inline expansion.

- **C1:** [Analyzer](https://github.com/scalacenter/tasty-mima/blob/main/tasty-mima/src/main/scala/tastymima/Analyzer.scala) compares old/new type-query contexts, translates parent types, checks subtype relationships and self types, and considers openness and newly abstract members. This is type-system compatibility reasoning, not a textual signature comparison.
- **C2:** The analyzer separates configuration, problem matchers, artifact-private package boundaries, and old/new contexts. The [repository's integration and motivation documentation](https://github.com/scalacenter/tasty-mima#readme) describes the core/build-plugin boundary and explains why TASTy-MiMa complements MiMa.

### 9. [Kotlin/binary-compatibility-validator](https://github.com/Kotlin/binary-compatibility-validator)

**Language / role:** Kotlin; Gradle plugin and library for public binary API dumps and comparison.

Study extraction of the effective Kotlin API from JVM classfiles. **Upstream explicitly places this plugin in maintenance mode**, retaining critical fixes and Kotlin-version support while directing new features toward Kotlin Gradle plugin validation. Its `apiCheck` task compares against a checked-in golden API, so differences still require review; this is not a claim that every changed line is necessarily breaking.

- **C1:** [KotlinSignaturesLoading](https://github.com/Kotlin/binary-compatibility-validator/blob/master/src/main/kotlin/api/KotlinSignaturesLoading.kt) combines ASM class information with Kotlin visibility metadata. It treats companion fields, synthetic default implementations, and property annotations specially so JVM-public implementation artifacts do not automatically become public Kotlin API.
- **C2:** The extraction code exposes signature-loading and filtering operations separately from Gradle tasks, uses stable ordering for dumps, and supports package/class/annotation selection. The [task and configuration documentation](https://github.com/Kotlin/binary-compatibility-validator#tasks) shows reuse across projects and multiple JVM targets.

### 10. [openjdk/sigtest](https://github.com/openjdk/sigtest)

**Language / role:** Java; signature-based API conformance and compatibility tools.

Study the TCK-oriented problem of comparing different implementations of an API against a common signature specification, as well as comparing successive versions. This is a useful historical reference implementation. The bundled release notes are dated May 2014 and should not be mistaken for a present-day Java support matrix.

- **C1:** [SignatureTest](https://github.com/openjdk/sigtest/blob/master/src/classes/com/sun/tdk/signaturetest/SignatureTest.java) describes and implements checking of inherited public/protected members, class modifiers, method descriptors, declared exceptions, and optional constant values. Its conformance goal can be stricter than one-way binary compatibility because implementations may need the same API surface in both directions.
- **C2:** Signature files serve as an intermediate representation shared by signature testing, API checking, and coverage analysis. The [release documentation](https://github.com/openjdk/sigtest/blob/master/ReleaseNotes.html) explains these tools and their differing dependency requirements, making the repository valuable for studying reusable test-specification formats.

### 11. [lvc/japi-compliance-checker](https://github.com/lvc/japi-compliance-checker)

**Language / role:** Perl with JDK tooling; Java source and binary compatibility analysis.

Study a different architecture from the Java-native engines: extraction through JDK tools, persistent API dumps, and separately maintained binary/source rule databases. The repository documents JAR and JMOD inputs and Scala support; that does not establish complete support for all later Java language features.

- **C1:** The [binary rules](https://github.com/lvc/japi-compliance-checker/blob/master/modules/RulesBin.xml) distinguish changes to staticness, return descriptors, finality, access, and default methods, with severity and client-effect descriptions. The distinction between a removed default implementation and a harmless addition is particularly useful to inspect.
- **C2:** The [main implementation](https://github.com/lvc/japi-compliance-checker/blob/master/japi-compliance-checker.pl) separates binary/source rule paths, manages extracted method/type information, and resolves inherited/default implementations. Saved dumps let extraction and comparison be reused by release-tracking workflows.

## Rust, Go, and Elm library evolution

### 12. [obi1kenobi/cargo-semver-checks](https://github.com/obi1kenobi/cargo-semver-checks)

**Language / role:** Rust; semantic-versioning checks over crate APIs extracted through rustdoc JSON.

Study a compatibility engine whose lints are declarative queries. The project documents the consequences of rustdoc's unstable JSON format and the need to align checker and toolchain versions; a successful scan is bounded by the selected build configuration and implemented lints.

- **C1:** Losing an auto trait such as `Send` or `Sync` has different downstream implications and explanatory needs from losing a derived or ordinary trait implementation. The [design discussion](https://github.com/obi1kenobi/cargo-semver-checks/blob/main/CONTRIBUTING.md#design-goals) uses these cases to explain why precise rule-specific diagnostics matter.
- **C2:** Lints are strongly typed Trustfall queries over shared API data, decoupling individual rules from extraction and query execution. The [contributor guide](https://github.com/obi1kenobi/cargo-semver-checks/blob/main/CONTRIBUTING.md#adding-a-new-lint) describes extending that system and testing it with crate fixtures and snapshots.
- **C3:** The same design document explains lazy query evaluation without cloning the rustdoc data and shared optimizations that benefit multiple lints. This is architectural performance evidence, not a benchmark claim.

### 13. [cargo-public-api/cargo-public-api](https://github.com/cargo-public-api/cargo-public-api)

**Language / role:** Rust; public API extraction, reviewable diffs, and snapshot-based CI checks.

Study normalization and stable presentation of a language's exposed surface. This tool is especially relevant when humans want to review the whole API delta. Its own diff model acknowledges that textual changes can have compatibility exceptions, so it should not be treated as a complete semantic breakage classifier.

- **C1:** [PublicApiDiff](https://github.com/cargo-public-api/cargo-public-api/blob/main/public-api/src/diff.rs) deliberately uses a multiset rather than a set so identical rendered items are not silently lost. It pairs additions/removals by public-item path and sorts the result deterministically.
- **C2:** The workspace separates the CLI, `public-api` library, rustdoc JSON production, and toolchain support; the repository demonstrates composing these libraries into API snapshot tests.
- **C4:** The [changelog](https://github.com/cargo-public-api/cargo-public-api/blob/main/CHANGELOG.md) records adaptations to dated 2023–2025 rustdoc toolchains, generic/lifetime rendering corrections, deterministic output improvements, API deprecations, and a memory-growth fix. These are concrete evolution and complexity-management evidence.

The verified canonical owner is `cargo-public-api`, following the documented move from `Enselic`.

### 14. [rust-lang/rust-semverver](https://github.com/rust-lang/rust-semverver)

**Language / role:** Rust; historical compiler-driven semantic-versioning checker. **Archived and explicitly deprecated upstream.**

Study the alternative of using compiler-internal type information directly. Both crate versions are compiled as dependencies of a dummy crate, then analyzed within one custom compiler-driver invocation. The README pins an old nightly and points readers to newer alternatives; this entry is for architectural study, not an assertion of suitability for modern Rust builds.

- **C1:** The [implementation notes](https://github.com/rust-lang/rust-semverver/blob/master/doc/impl_notes.md) describe matching public items, opportunistically matching hidden types exposed through public signatures, translating types between versions, and checking trait bounds and implementations in the appropriate directions.
- **C2:** Separate mapping, translation, mismatch, and traversal passes reuse item correspondence across different checks. The same document explains why this shared compiler context was chosen and the resulting metadata and compilation-cost tradeoffs.

The linked implementation notes are an additional primary source beyond the repository README.

### 15. [golang/exp](https://github.com/golang/exp)

**Language / role:** Go; the **`apidiff`** library and related commands in the Go project's official GitHub mirror.

Study compatibility through `go/types` package and module representations. This is an experimental repository, and its README explicitly excludes its packages from the Go 1 compatibility promise. The entry concerns `apidiff`, not every package in `exp`.

- **C1:** The [compatibility design document](https://github.com/golang/exp/blob/master/apidiff/README.md) carefully defines what the tool promises and deliberately ignores, including unkeyed struct literals, embedding/shadowing corner cases, and `unsafe`-dependent layout observations. This makes its approximation inspectable instead of implying that an API check proves arbitrary client compatibility.
- **C2:** [The implementation](https://github.com/golang/exp/blob/master/apidiff/apidiff.go) exposes package-level and module-level comparison, returns structured compatible/incompatible changes, and maintains correspondences between named types. Module comparison aligns packages relative to their module roots, permitting reuse beyond identical import paths.

### 16. [elm/compiler](https://github.com/elm/compiler)

**Language / role:** Haskell; the **package API diff and version-bump** subsystem of the Elm toolchain.

Study compatibility policy integrated with a language's package workflow. The relevant code compares generated module documentation/type descriptions, classifies API changes, and supplies version-bump advice. This is a structural API contract, not analysis of function-body behavior.

- **C1:** [Deps.Diff](https://github.com/elm/compiler/blob/main/builder/src/Deps/Diff.hs) compares unions, aliases, values, and operators. Type comparison handles type-variable renaming, extensible records, tuples, and constructor structure; operator associativity and precedence also matter to equivalence.
- **C2:** Package/module change records and magnitude calculation form a reusable analysis layer. The [Bump command](https://github.com/elm/compiler/blob/main/terminal/src/Bump.hs) obtains old API documentation, generates the new public surface, and consumes that layer to recommend a version change, showing the boundary between pure comparison and package I/O.

## Dynamic-language API contracts

### 17. [mkdocstrings/griffe](https://github.com/mkdocstrings/griffe)

**Language / role:** Python; API object-model extraction and breaking-change detection, also used for documentation.

Study how one representation can serve API documentation and compatibility analysis. Griffe exposes package loading and `find_breaking_changes`, with CLI workflows for comparing package revisions. Its remit is exposed Python structure and signatures, not all dynamic runtime behavior.

- **C1:** The [diff engine](https://github.com/mkdocstrings/griffe/blob/main/packages/griffelib/src/griffe/_internal/diff.py) distinguishes positional-only, keyword-only, and variadic parameters. A removed parameter can remain callable if the appropriate new `*args`/`**kwargs` absorbs it; changing an optional parameter to required, or moving positional parameters, needs different treatment. Recursive traversal tracks seen paths.
- **C2:** The same engine operates on shared module/class/function/alias objects and emits typed breakages with old/new values and explanation styles. The [documented Python API](https://github.com/mkdocstrings/griffe#load-and-navigate-data-with-python) demonstrates reusing extraction and comparison without the CLI.

### 18. [Roave/BackwardCompatibilityCheck](https://github.com/Roave/BackwardCompatibilityCheck)

**Language / role:** PHP; library API compatibility checks between Git revisions.

Study structural reflection and variance-sensitive change detection in a dynamic-language ecosystem. The command integrates with Composer autoload information and chooses a tagged baseline, while the engine accepts reflectors for old and new sources and their dependencies.

- **C1:** [TypeIsCovariant](https://github.com/Roave/BackwardCompatibilityCheck/blob/8.24.x/src/DetectChanges/Variance/TypeIsCovariant.php) recursively treats union and intersection types differently and handles `mixed`, `never`, iterable/array relations, interfaces, and class inheritance. Its comment candidly identifies this as a simplified type-relation implementation rather than a full formal model.
- **C2:** [CompareClasses](https://github.com/Roave/BackwardCompatibilityCheck/blob/8.24.x/src/CompareClasses.php) receives separate class/interface/trait comparison strategies, filters anonymous and explicitly internal classes, and emits a shared `Changes` stream. This makes the source/dependency locators and rule families separable from command execution.

The verified default branch at research time was `8.24.x`; source entry points intentionally use that branch.

## Network API and serialized-schema compatibility

### 19. [oasdiff/oasdiff](https://github.com/oasdiff/oasdiff)

**Language / role:** Go; OpenAPI semantic diff, changelog, and breaking-change detection.

Study the difference between a changed specification and a changed client contract. The checker reasons about the declared contract, including validators and generated clients, rather than assuming that a lenient server makes a restriction harmless.

- **C1:** The [breaking-change semantics](https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md) explain why adding a required request property breaks compatibility even if it has a default. They also describe uncertainty around composed schemas and how request/response direction, including read-only/write-only properties, changes a finding's significance.
- **C2:** Breaking checks and changelogs run over a shared diff engine, with independently configurable severity levels, endpoint matching, normalization, and report formats. The same document explains those layers and the customization boundary; the [repository overview](https://github.com/oasdiff/oasdiff#readme) maps them to commands and integrations.

The verified canonical repository is under `oasdiff`, rather than its older `Tufin` owner path.

### 20. [OpenAPITools/openapi-diff](https://github.com/OpenAPITools/openapi-diff)

**Language / role:** Java; OpenAPI comparison library with CLI and Maven integration.

Study recursive schema comparison and structured compatibility results in the Java OpenAPI ecosystem. The tool can distinguish any change from an incompatible change, allowing different CI failure policies.

- **C1:** [SchemaDiff](https://github.com/OpenAPITools/openapi-diff/blob/master/core/src/main/java/org/openapitools/openapidiff/core/compare/SchemaDiff.java) resolves references and composed schemas while tracking visited references. It dispatches ordinary, array, and composed schemas through distinct result implementations and carries comparison context into the result.
- **C2:** Schema-specific comparison, deferred results, and the enclosing OpenAPI comparison engine are reusable beneath multiple frontends. The [repository API and usage documentation](https://github.com/OpenAPITools/openapi-diff#readme) describes the core artifact separately from the CLI and Maven plugin.
- **C3:** `SchemaDiff` keys its deferred schema cache by both schema references and comparison context. That structure addresses repeated/recursive schema work while preserving context-sensitive results; no throughput claim is inferred.

### 21. [graphql-hive/graphql-inspector](https://github.com/graphql-hive/graphql-inspector)

**Language / role:** TypeScript; GraphQL schema compatibility, operation validation, and change reporting.

Study a typed change model with breaking, non-breaking, and dangerous classifications. The repository contains the core engine and integrations; the separate hosted Hive product is not counted here.

- **C1:** The [field-change implementation](https://github.com/graphql-hive/graphql-inspector/blob/master/packages/core/src/diff/changes/field.ts) treats removal of even a deprecated field as breaking, checks whether output-type changes are safe, and recognizes that a newly added non-null argument is breaking only when no default makes omission valid.
- **C2:** The [core diff entry point](https://github.com/graphql-hive/graphql-inspector/blob/master/packages/core/src/diff/index.ts) separates initial schema comparison from an ordered asynchronous rule pipeline. Typed changes and rule configuration can therefore be reused from CLI, action, or programmatic integrations without duplicating the schema walk.

The canonical owner verified during research is `graphql-hive`; older organization paths are not additional projects.

### 22. [bufbuild/buf](https://github.com/bufbuild/buf)

**Language / role:** Go; **`buf breaking` and the `bufcheck` subsystem** of the Protobuf toolchain.

Study compatibility as several distinct guarantees over the same descriptors: generated-code compatibility at file or package scope, JSON compatibility, and binary wire compatibility. A schema change can be safe at one level and unsafe at another.

- **C1:** The [rules reference](https://buf.build/docs/breaking/rules/) explains why removing an enum value can preserve wire encoding while breaking generated source. Its categories also distinguish JSON names from field numbers and language-specific file/package effects, making the chosen compatibility policy explicit.
- **C2:** [bufcheck's interfaces](https://github.com/bufbuild/buf/blob/main/private/bufpkg/bufcheck/bufcheck.go) compare current and baseline images under a breaking configuration and expose common rule/category abstractions, plugins, and structured annotations. The implementation explicitly requires retaining import information until the appropriate filtering option is applied, a useful boundary between descriptor loading and rule execution.

The repository is included once for this subsystem; its compiler, registry client, and code-generation functionality do not create extra entries.

## Search coverage, exclusions, and limits

Discovery used more than six distinct live-web search formulations, followed by direct reads of official repository pages, raw implementation files, source directories, and project documentation. Search angles included C/C++ ABI and DWARF tools; Java JAR/signature checkers; Scala binary and TASTy compatibility; Kotlin API validation; Rust semver and public-API extraction; Go package/module comparison; .NET assembly validation; Swift API Digester; Python and PHP signatures; OpenAPI; GraphQL and Protobuf; Elm/Haskell package policies; TypeScript exported-type checking; and concurrency/atomics ABI research. Later distinct queries increasingly returned already-covered engines, thin integrations, or candidates whose GitHub provenance and implementation depth could not both be established.

The selection intentionally preserves several implementation families: declarative rule databases, bytecode readers, compiler type models, query-based lints, normalized snapshots, recursive schema graphs, and reusable analyzer frameworks. Established tools are accompanied by smaller specialized implementations such as TASTy-MiMa and abicheck. The three larger language/SDK repositories and the Go mirror identify their relevant subsystem rather than receiving blanket endorsements.

- **Non-GitHub upstreams:** [Libabigail's official source instructions](https://sourceware.org/libabigail/) point to Sourceware, and [STG's upstream](https://android.googlesource.com/platform/external/stg/) is Android Git. Both are important ABI tools. This search did not establish an officially endorsed substantive GitHub mirror for inclusion, so personal copies and forks were not substituted. This is a provenance limitation of the report, not a quality judgment on those projects.
- **Wrappers and adjacent tools:** ABI Dumper alone extracts data rather than deciding compatibility; action-only wrappers, tracker frontends, generic version-number utilities, migration guides, and awesome lists were not counted as separate checking engines. Historical moved .NET implementations were not duplicated alongside the SDK subsystem.
- **Behavioral scope:** Most retained tools analyze declared structure or metadata. Snapshot equality may flag compatible additions; a successful structural check does not establish equivalence of runtime behavior. Rust-semverver is explicitly historical, Kotlin's standalone validator is explicitly in maintenance mode, and SigTest's dated bundled documentation is identified as such.
- **Evidence limits:** This was source and documentation research, not comparative execution or a full audit. No star counts, self-published accuracy rankings, or unverified numerical performance claims determined inclusion. C1–C4 assignments are grounded in the cited mechanisms; uncertain current support or maintenance was not promoted into fact.

Repository identities were deduplicated, including organization moves. Every selected repository has at least two explicitly justified criteria and an inspected implementation or architecture source in addition to its repository page.
