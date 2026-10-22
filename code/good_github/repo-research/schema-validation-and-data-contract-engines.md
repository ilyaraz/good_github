# Schema validation and data contract engines

Research date: **2026-10-09**.

This selection covers 25 repositories that execute structural schemas, typed validation rules, configuration constraints, dataset contracts, or schema-compatibility decisions. It spans embedded libraries, language runtimes, distributed data checks, and registry services. Pure schema specifications, generators without a substantive validation engine, and general pipeline orchestration are outside the scope. Repository headings use the canonical GitHub locations observed during research; monorepos are counted once and the relevant subsystem is identified.

The criteria below are evidence-based selection judgments, not claims that every component is exemplary or that a library is appropriate for every deployment.

- **C1 — Correctness:** difficult invariants, semantic edge cases, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable models and interfaces that serve multiple use cases.
- **C3 — Performance architecture:** concrete performance constraints addressed through an understandable design.
- **C4 — Evolution:** sustained development accompanied by evidence of compatibility, testing, or complexity management.

## Standards-based JSON and XML validation

### 1. [ajv-validator/ajv](https://github.com/ajv-validator/ajv)

**Language/role:** TypeScript and JavaScript; compiling validator for JSON Schema and JSON Type Definition.

Ajv is especially useful for studying the boundary between declarative schemas and generated executable code. Its compiler has a typed code-construction layer rather than unrestricted template interpolation.

- **C1:** The code-generation design distinguishes generated names, code fragments, and quoted values through `Name`, `_Code`, and tagged templates. This directly addresses injection risks when schemas contain untrusted strings. The documentation also explains the boundary of that protection: its TypeScript checks do not automatically protect arbitrary JavaScript extensions.
- **C3:** Generated code is represented as a tree that supports unreachable-branch removal, unused-variable removal, and limited constant inlining. These are concrete compiler optimizations, with assumptions about side effects documented rather than hidden behind a speed claim.

**Entry point:** The [code-generation design](https://ajv.js.org/codegen.html) explains both the safety model and optimization passes. The repository supplies the broader schema dialect and extension context.

### 2. [python-jsonschema/jsonschema](https://github.com/python-jsonschema/jsonschema)

**Language/role:** Python; extensible JSON Schema validator with explicit reference-resolution machinery.

This is a strong study in keeping schema interpretation separate from resource acquisition and Python's own type system.

- **C1:** Reference resources carry a schema specification, so dialect-sensitive semantics remain explicit; the referencing guide illustrates why a value such as `2.0` can require different treatment across drafts. The newer registry API also makes remote retrieval an explicit application choice.
- **C2:** Validator protocols, immutable type-checker mappings, format checkers, and retrieval callbacks provide separate extension seams. Customizing what counts as a number does not require replacing reference resolution or the whole validator.

**Entry points:** [JSON Schema referencing](https://python-jsonschema.readthedocs.io/en/stable/referencing/) describes `Registry`, `Resource`, and retrieval policies; the [validation API](https://python-jsonschema.readthedocs.io/en/stable/validate/) documents validator evolution, lazy errors, and type-checker extension. Its explanation of concrete `int`/`dict` checks also exposes a deliberate extensibility-versus-performance tradeoff.

### 3. [Stranger6667/jsonschema](https://github.com/Stranger6667/jsonschema)

**Language/role:** Rust; reusable compiled JSON Schema validators, with related bindings in the repository.

Study how construction-time work is separated from repeated validation, and how the engine exposes potentially expensive or semantically sensitive dependencies.

- **C1:** Regex configuration exposes a real tradeoff between richer expression features and bounded-backtracking behavior. Reference retrieval and draft selection are explicit parts of validator construction rather than incidental string processing.
- **C2:** The `Keyword` interface and keyword factories, retrieval customization, and multiple output modes provide reusable extension points around the same validation engine.
- **C3:** Validators are built for reuse. Blocking or asynchronous reference acquisition occurs during construction; subsequent validation operates synchronously on the prepared in-memory representation.

**Entry point:** The substantive [crate documentation](https://docs.rs/jsonschema/latest/jsonschema/) covers validator construction, custom keywords, reference retrieval, and regex engines. Avoid extrapolating its benchmark results to other languages or workloads without measurement.

### 4. [santhosh-tekuri/jsonschema](https://github.com/santhosh-tekuri/jsonschema)

**Language/role:** Go; JSON Schema compiler and validation library.

This comparatively compact engine offers useful material on dialect-aware compilation, schema loading, and structured diagnostics.

- **C1:** The repository documents detection of infinite schema/validation cycles and support for mixed-draft resources. The API makes format assertions draft-dependent: a format annotation is not automatically an assertion in every dialect. It also recommends choosing a default draft explicitly to avoid behavior changes when defaults evolve.
- **C2:** A `Compiler` produces reusable `Schema` objects while allowing applications to supply resources, loaders, formats, media-type handlers, and vocabularies. Hierarchical validation errors preserve more information than a boolean result.

**Entry point:** The [v6 package reference](https://pkg.go.dev/github.com/santhosh-tekuri/jsonschema/v6) documents `Compiler`, `Schema`, `AssertFormat`, and extension interfaces. Read it alongside the canonical repository's conformance and cycle-handling description; similarly named forks are not separate selections here.

### 5. [networknt/json-schema-validator](https://github.com/networknt/json-schema-validator)

**Language/role:** Java; Jackson-based JSON Schema engine with configurable dialects and evaluation output.

Its architectural interest is the relationship among keyword evaluation, annotations, and diagnostics—not merely Java object validation.

- **C1:** The repository explains that annotations needed by `unevaluatedProperties` and `unevaluatedItems` must still be collected when general annotation reporting is disabled. It also distinguishes evaluation paths, schema locations, and instance locations, which become different under references and composition.
- **C2:** Dialects, vocabularies, keyword factories, per-keyword validators, and execution contexts form an explicit extension model. Required unknown vocabularies can invalidate a meta-schema, while handling of unknown keywords is configurable.
- **C3:** Annotation reporting, fail-fast output, and source line/column tracking are separate options with different costs; the engine does not force maximal diagnostics onto every call.

**Entry point:** The [custom-dialect implementation guide](https://github.com/networknt/json-schema-validator/blob/master/doc/custom-dialect.md) explains the extension layers. The repository README supplies the evaluation-output and annotation-cost details.

### 6. [sourcemeta/blaze](https://github.com/sourcemeta/blaze)

**Language/role:** C++; JSON Schema compiler and instruction evaluator.

Blaze supplies a different compilation strategy from JavaScript source generation: schemas become a low-level intermediate representation consumed by a schema-agnostic evaluator.

- **C1:** The compiler frames resources, resolves reference targets, builds dynamic-anchor labels, and rejects invalid reference destinations. These stages expose the complexity of reference scope and recursive evaluation directly.
- **C3:** Compilation detects whether dynamic-scope tracking is needed and whether annotations or unevaluated-keyword bookkeeping must be retained. Fast-validation postprocessing specializes the resulting instruction program rather than repeatedly interpreting the original schema structure.

**Entry points:** Read the [compiler implementation](https://github.com/sourcemeta/blaze/blob/main/src/compiler/compile.cc), especially reference analysis and final postprocessing, and the [project documentation](https://blaze.sourcemeta.com/). The architectural observations are supported by the code; this report does not reproduce the project's numerical performance comparisons.

### 7. [opis/json-schema](https://github.com/opis/json-schema)

**Language/role:** PHP; JSON Schema validation with both standards-focused and extended validation interfaces.

Opis is a useful contrast to engines embedded in statically typed host languages, particularly around PHP's representation of JSON objects and arrays.

- **C1:** Its API documentation treats `stdClass` objects and indexed arrays differently and warns about ambiguous empty associative arrays. It distinguishes validation failures from schema-resolution problems such as duplicate normalized identifiers or unresolved references.
- **C2:** The general validator exposes extensions such as filters and slots, while `CompliantValidator` excludes those extensions. Schema loading and network retrieval can be configured independently of the validation call.
- **C3:** Parsed schemas are cached, making reuse of a validator an explicit architectural recommendation. Per-keyword error limits and stopping at the first error are separate controls.

**Entry point:** The [PHP validator guide](https://opis.io/json-schema/2.x/php-validator.html) explains object representation, result handling, loader configuration, caching, and the compliant-versus-extended API boundary.

### 8. [json-everything/json-everything](https://github.com/json-everything/json-everything)

**Language/role:** C#/.NET monorepo; the relevant subsystem is **JsonSchema.Net**.

Study a schema object model that connects construction, reference resolution, evaluation, and output formatting without collapsing them into a single validation function.

- **C1:** Schema building checks schema structure and resolves references, including schemas embedded in larger documents. Meta-schema and reference handling are therefore part of construction correctness, not just instance traversal.
- **C2:** `IJsonSchemaKeyword`, typed builder extensions, schema registries, and `IBaseDocument` let callers extend keywords or locate schemas inside documents such as OpenAPI descriptions. Evaluation results can expose different output structures and annotations.
- **C3:** The documented build/evaluate lifecycle moves reusable work into schema construction; reference resolution is performed during building and, where needed, the first evaluation rather than on every validation.

**Entry point:** The [JsonSchema.Net basics and architecture guide](https://docs.json-everything.net/schema/basics/) covers builders, registries, embedded documents, and evaluation results. Other JSON utilities in the monorepo are not counted separately.

### 9. [sissaschool/xmlschema](https://github.com/sissaschool/xmlschema)

**Language/role:** Python; XML Schema 1.0/1.1 validation and conversion between XML and application data.

This broadens the report beyond JSON and supplies concrete material on schema-loading policy, namespace behavior, and hostile-input constraints.

- **C1:** The documentation distinguishes XSD 1.0 and 1.1 semantics, including complex-type extension differences. It also describes entity restrictions, external-resource access policies, and processing limits for depth, elements, and schema sources.
- **C2:** Validation modes, schema loaders, immutable settings, and converter interfaces are separate abstractions. They support strict validation, error-tolerant processing, and XML-to-data conversion without requiring separate engines.

**Entry point:** The [features and processing architecture](https://xmlschema.readthedocs.io/en/latest/features.html) explains schema-loading alternatives, resource controls, converters, and validation modes. These controls are study material, not a claim that every possible configuration is safe for untrusted XML.

## Typed application schemas and rule engines

### 10. [pydantic/pydantic](https://github.com/pydantic/pydantic)

**Language/role:** Python and Rust; typed model validation and serialization.

The most useful study boundary is between Python's model/type customization and the Rust engine that executes the resulting schema.

- **C2:** Model construction gathers fields, configuration, and validators into a core-schema representation. The same representation feeds `SchemaValidator` and `SchemaSerializer`, while wrapper hooks let user types participate in schema generation and JSON Schema production.
- **C3:** The architecture places model-definition work in Python and repeated validation/serialization in `pydantic-core`. This is a concrete division of setup cost and instance-processing cost, with a documented constraint: core-schema node kinds must be understood by the Rust implementation.

**Entry point:** The [architecture documentation](https://pydantic.dev/docs/validation/latest/internals/architecture/) follows metaclass processing, `GenerateSchema`, core-schema dictionaries, and execution. Count the model layer and its core integration as one selection here, rather than inflating the list with implementation components.

### 11. [msgspec/msgspec](https://github.com/msgspec/msgspec)

**Language/role:** C and Python; typed decoding, validation, and serialization.

msgspec is valuable for studying validation integrated into decoding and the compatibility consequences of choosing a wire representation.

- **C1:** Its schema-evolution rules distinguish map-like structures from positional `array_like` structures. New fields need defaults; positional fields must be appended without reordering, and field types and MessagePack extension codes require compatibility discipline.
- **C3:** The performance guide explains reuse of typed decoders, skipping unneeded fields, native `Struct` layouts, and reducing field-name overhead with positional encoding. These choices connect the validation model to allocation and decoding work.

**Entry points:** Read [schema evolution](https://github.com/msgspec/msgspec/blob/main/docs/schema-evolution.rst) together with [performance tips](https://github.com/msgspec/msgspec/blob/main/docs/perf-tips.rst). The engineering lesson is the relationship among schema rules, omitted/defaulted fields, and work avoided during decoding—not an unsupported universal speed ranking.

### 12. [colinhacks/zod](https://github.com/colinhacks/zod)

**Language/role:** TypeScript; runtime schemas with inferred input and output types.

Zod is interesting both as a parser library and as a case study in controlling the cost of a public TypeScript API.

- **C2:** The core package separates `$ZodType`, schema definitions, parsing, checks, and errors. Its shared internals support the classic API and Zod Mini, and permit tooling to traverse schemas through explicit definition objects.
- **C3:** The v4 design addresses TypeScript generic-instantiation growth in chains such as `.extend()` and `.omit()`, alongside runtime/package concerns. Compiler workload is treated as an engineering constraint of the library's abstractions.
- **C4:** The v4 account explicitly traces the v3 line back to 2021 and explains which accumulated design constraints motivated the redesign, supported by a TypeScript benchmark playground and migration-oriented documentation.

**Entry points:** [Zod Core](https://zod.dev/packages/core) explains the reusable implementation model; the [v4 design and release account](https://zod.dev/v4) explains the evolution. Reported benchmark multipliers are not independently endorsed here.

### 13. [open-circle/valibot](https://github.com/open-circle/valibot)

**Language/role:** TypeScript; composable runtime schemas designed around modular imports.

Valibot is a useful counterpoint to method-heavy schema APIs: validators and transformations are independently imported functions composed into pipelines.

- **C2:** Schema objects describe inputs, while pipe actions separately express validation, transformation, and metadata. The same composition model supports constraints, output transformation, branding, and readonly types.
- **C3:** The independent-function architecture allows bundlers to remove unused validation functionality. This connects an understandable API organization to browser delivery constraints, without requiring a particular bundle-size claim to establish merit.

**Entry points:** The [mental model](https://valibot.dev/guides/mental-model/) explains schemas and action pipelines; the [introduction](https://valibot.dev/guides/introduction/) explains the relationship between modular functions, tree shaking, and implementation organization. The heading uses the current canonical GitHub owner observed during research.

### 14. [metosin/malli](https://github.com/metosin/malli)

**Language/role:** Clojure and ClojureScript; schemas represented as data, with validation and transformation machinery.

Malli is particularly useful for comparing schema reuse through direct values, named references, and registries in a dynamic language.

- **C2:** Reusable schemas can live in ordinary vars, global composite registries, or local reference maps. The documentation makes lookup and dereferencing behavior explicit, exposing the tradeoff between local reasoning and dynamically replaceable definitions.
- **C3:** The changelog documents compilation and reuse of recursive functions and reference transformers, showing attention to repeated work in recursive schemas.
- **C4:** Dated entries across 2023–2026 document compatibility changes, parsing migration helpers, generator invariant fixes, and regressions such as startup cost and recursive-schema memory failures. This is stronger evolution evidence than repository age alone.

**Entry points:** [Reusable schemas](https://github.com/metosin/malli/blob/master/docs/reusable-schemas.md) explains registry choices; the [changelog](https://github.com/metosin/malli/blob/master/CHANGELOG.md) records the compatibility and implementation work.

### 15. [dry-rb/dry-schema](https://github.com/dry-rb/dry-schema)

**Language/role:** Ruby; declarative schemas compiled into coercion and validation processing steps.

Study the implementation of the DSL, particularly how apparently simple field declarations become ordered processing stages.

- **C1:** The DSL distinguishes optional absent keys from values that must actually be checked. Its processing assembly makes key validation, key coercion, value coercion, filtering, and rule application separate concerns whose order affects outcomes.
- **C2:** Parent schemas contribute rules, types, and processing configuration. Macros, processor selection, and before/after hooks allow reuse and customization without copying the entire validator.

**Entry point:** The [DSL implementation](https://github.com/dry-rb/dry-schema/blob/main/lib/dry/schema/dsl.rb) exposes `call`, rule/type construction, inherited steps, and coercer assembly. Reading this file after the repository's usage examples gives an experienced engineer a concrete route from the public DSL to its execution pipeline.

### 16. [FluentValidation/FluentValidation](https://github.com/FluentValidation/FluentValidation)

**Language/role:** C#/.NET; typed object-validation rules, including asynchronous conditions and checks.

This engine is useful for studying reusable business-validation rules and the correctness boundary between synchronous frameworks and asynchronous validators.

- **C1:** `ValidateAsync` handles both synchronous and asynchronous rules, while calling synchronous validation on a validator with asynchronous rules throws. The documentation explicitly describes version-dependent behavior in ASP.NET's synchronous automatic-validation pipeline, making a subtle integration failure mode visible.
- **C2:** `IRuleBuilder<T,TProperty>`, generic extension methods, predicate validators, `ValidationContext`, and custom property validators provide progressively deeper reuse mechanisms. Custom errors can retain context rather than being reduced to a single boolean.

**Entry points:** [Asynchronous validation](https://docs.fluentvalidation.net/en/latest/async.html) explains execution constraints; [custom validators](https://docs.fluentvalidation.net/en/latest/custom-validators.html) shows how reusable rules build on the same interfaces as built-in validators.

## Constraint languages used as schema engines

### 17. [cue-lang/cue](https://github.com/cue-lang/cue)

**Language/role:** Go; CUE implementation for configuration, schemas, constraints, and data validation.

CUE belongs here because constraints and concrete values participate in the same evaluation model, allowing schemas to be composed and checked rather than merely parsed as a separate document format.

- **C1:** The language specification defines unification as a greatest lower bound and requires associative, commutative, and idempotent behavior. Defaults, disjunctions, bottom values, required/optional fields, and closed records introduce precise semantic obligations for the evaluator.
- **C2:** Values and types inhabit the same lattice. Partial configurations, reusable definitions, and validation against concrete data can therefore use the same underlying constraint operations.

**Entry point:** The [language specification in the source tree](https://github.com/cue-lang/cue/blob/master/doc/ref/spec.md), particularly unification, defaults, and struct closedness, is substantive semantic guidance for reading the implementation. The selection concerns CUE's constraint engine; it does not imply that every language/tooling subsystem is a schema validator.

### 18. [nickel-lang/nickel](https://github.com/nickel-lang/nickel)

**Language/role:** Rust; configuration language with runtime contracts.

Nickel adds a useful architectural family: contracts can constrain both data structures and higher-order values in a lazily evaluated configuration language.

- **C1:** Function contracts check arguments and results and assign blame to callers or callees; nested function contracts make that polarity nontrivial. Delayed contract enforcement must also remain coherent with laziness and record merging.
- **C2:** Primitive, record, function, and user-defined contracts share compositional mechanisms. Open versus closed records and custom predicate contracts let the same engine express structural and semantic constraints.

**Entry point:** The [contracts manual](https://nickel-lang.org/user-manual/contracts/) explains enforcement, custom contracts, record behavior, function wrappers, and blame. This is a study of contract semantics and their implementation consequences, not merely an alternative syntax for JSON Schema.

## Dataset validation and executable data contracts

### 19. [unionai-oss/pandera](https://github.com/unionai-oss/pandera)

**Language/role:** Python; dataframe schemas, type checks, and data-quality predicates.

Pandera is useful for understanding how structural validation interacts with vectorized data, coercion, missing values, and aggregated diagnostics.

- **C1:** Column nullability and dtype coercion are independent constraints: allowing nulls does not make a non-nullable integer representation capable of holding `NaN`. Lazy validation also separates missing/unexpected columns, coercion problems, and failed data checks into structured error collections.
- **C2:** `DataFrameSchema` composes columns, indexes, dtype policies, and `Check` objects. Checks can use application predicates or groups defined by another column, supporting contracts beyond record-by-record type validation.

**Entry points:** [DataFrame schemas](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html) explains composition and coercion semantics; [lazy validation](https://pandera.readthedocs.io/en/stable/lazy_validation.html) explains accumulated failures. These examples substantiate the dataframe contract engine without assuming identical behavior across every supported backend.

### 20. [fivetran/great_expectations](https://github.com/fivetran/great_expectations)

**Language/role:** Python; expectation-based data validation. The relevant subsystem is execution engines and metric resolution.

The canonical GitHub page observed during research is under `fivetran`; older `great-expectations/great_expectations` links redirect there. Study how user-facing expectations are lowered into reusable backend computations.

- **C2:** Expectations depend on metric configurations rather than directly owning every backend operation. Execution engines separate compute domains and accessors from the native dataframe or query representation.
- **C3:** The implementation distinguishes directly resolvable metrics from bundled computations, consumes previously computed metrics, and can group work over the same compute domain into a backend operation. This addresses query/scan cost through an explicit metric-dependency architecture.

**Entry points:** The current [execution-engine source](https://github.com/fivetran/great_expectations/blob/develop/great_expectations/execution_engine/execution_engine.py) is the implementation reference. The [historical execution-engine design](https://legacy.017.docs.greatexpectations.io/docs/0.14.13/reference/execution_engine/) explains the dependency-graph motivation; it is versioned legacy documentation, not a current API guide.

### 21. [sodadata/soda-core](https://github.com/sodadata/soda-core)

**Language/role:** Python monorepo; Soda Core v4 contract verification with data-source packages.

The current contract/session architecture is the relevant target; older SodaCL-era descriptions alone do not establish how the present engine works.

- **C1:** Verification results distinguish failed checks from execution errors. In the inspected API, `is_passed` concerns check outcomes and can ignore execution-log errors; aggregate `is_ok` addresses the complete result. Check states also include warnings, exclusion, and non-evaluation. These distinctions matter when turning validation into a pipeline gate.
- **C2:** Sessions accept multiple contracts and data sources, while structured contract/check results and metadata-only validation support different execution contexts. The contract language separates dataset checks, column checks, type precision, extra-column policy, and ordering policy.

**Entry points:** The [contract verification API implementation](https://github.com/sodadata/soda-core/blob/main/soda-core/src/soda_core/contracts/contract_verification.py) exposes session and result semantics; the [contract-language reference](https://docs.soda.io/reference/contract-language-reference) defines the declarative input. Source packages within this monorepo are counted once.

### 22. [awslabs/deequ](https://github.com/awslabs/deequ)

**Language/role:** Scala and Apache Spark; distributed data-quality constraints and metric computation.

Deequ provides a clear route into scalable contract execution: assertions sit above analyzers, metrics, reusable intermediate states, and persistence interfaces.

- **C2:** An `Analyzer` computes a `Metric`; intermediate `State` can be loaded or persisted separately. A metrics repository associates results with timestamps/tags and analyzer contexts, supporting repeated validation and comparison workflows.
- **C3:** The engine identifies required analyzers and combines compatible work to reduce passes over data. The design distinguishes scan-shareable analyzers from grouping-based computation, and reusable states support work across changing datasets.

**Entry point:** The [key-concepts architecture document](https://github.com/awslabs/deequ/blob/master/docs/key-concepts.md) connects analyzers, states, constraints, shared scans, and metric repositories. This is a particularly useful companion to embedded validators because its dominant costs are distributed scans and aggregations.

### 23. [datacontract/datacontract-cli](https://github.com/datacontract/datacontract-cli)

**Language/role:** Python; executable data contracts, schema checks, and quality checks across data sources.

Despite its CLI name, this is substantive engine work rather than merely a wrapper. The June 2026 v1 transition replaced Soda-based execution with an Ibis-based engine, making old architectural descriptions misleading.

- **C1:** The changelog records count-versus-percentage thresholds, severity handling, structured measured/expected diagnostics, and SQL-dialect differences such as unsupported regex handling. The test command also distinguishes metadata-only checks from row-level execution and excludes schema/custom-SQL checks from generic row-filter application.
- **C2:** Contract-defined checks are translated through a shared execution layer to backend expressions. Categories, dimensions, identifiers, and tags select subsets of a contract without requiring a separate checker for each workflow.

**Entry points:** The [test-command implementation](https://github.com/datacontract/datacontract-cli/blob/main/datacontract/command_test.py) shows selection and execution boundaries; the [changelog](https://github.com/datacontract/datacontract-cli/blob/main/CHANGELOG.md) documents the engine replacement and semantic fixes. Migration caveat: old custom SodaCL checks are not automatically equivalent to current engine checks.

## Message contracts and schema evolution

### 24. [bufbuild/protovalidate-go](https://github.com/bufbuild/protovalidate-go)

**Language/role:** Go; Protocol Buffers validation runtime using field annotations and CEL expressions.

This selects a concrete runtime implementation rather than counting the shared annotation specification and each language binding as independent engines.

- **C1:** Cache construction checks that rules are appropriate for field types and reports compilation problems for invalid rule extensions. The repository's conformance workflow exercises native-rule execution and CEL execution to check their agreement.
- **C2:** Protobuf descriptors, standard validation annotations, and custom CEL rules provide a reusable contract layer over generated messages rather than application-specific hand-written validation.
- **C3:** A build-through cache stores compiled rule ASTs by field descriptor. The implementation attempts compilation in existing environments before extending them, and specializes expressions using rule values, exposing concrete strategies for avoiding repeated compilation work.

**Entry point:** The [cache implementation](https://github.com/bufbuild/protovalidate-go/blob/main/cache.go) is a compact route into compilation, specialization, and descriptor-level reuse. The repository's native/CEL conformance instructions complement that implementation evidence.

### 25. [confluentinc/schema-registry](https://github.com/confluentinc/schema-registry)

**Language/role:** Java monorepo; schema registry and compatibility engine. Focus on schema providers, especially `json-schema-provider`.

The selection concerns persistent data-contract evolution as well as validation of individual messages. Compatibility is a relation between versions, with semantics that differ by schema format.

- **C1:** Backward compatibility with the immediately preceding version differs from backward-transitive compatibility with the full history. Avro, Protobuf, and JSON Schema also impose different compatibility rules; treating them as a single structural diff would be incorrect.
- **C2:** The JSON Schema implementation participates in a `ParsedSchema` abstraction while carrying references, resolved references, metadata, rules, and canonical representations. This supports a shared registry interface without erasing format-specific behavior.

**Entry points:** The [schema-evolution documentation](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html) defines compatibility modes and format differences; [JsonSchema.java](https://github.com/confluentinc/schema-registry/blob/master/json-schema-provider/src/main/java/io/confluent/kafka/schemaregistry/json/JsonSchema.java) exposes the provider representation. Other registry components are not separately counted or uniformly assessed here.

## Coverage, search process, and limitations

Discovery used meaningfully different live-web query families: compiled JSON Schema engines in Rust/Go/C++/Java; Python reference and type systems; TypeScript parser/schema composition; PHP, Ruby, Clojure, and .NET validator implementations; XML/XSD engines and resource handling; CUE/Nickel-style configuration contracts; dataframe validation and warehouse data contracts; Spark metric/analyzer execution; and Protobuf/CEL validation plus registry compatibility. Follow-up searches targeted source files, extension APIs, design documents, migration guides, conformance descriptions, and changelogs. Additional language/ecosystem searches increasingly returned already-covered families, generators, thin integrations, or specification-only projects.

Every retained GitHub repository page was opened to verify its location and category fit, and at least one separate primary implementation or substantive documentation source was opened and read. The entry-point links identify the material supporting the criteria. Stars were not used as evidence. Transfers were resolved to the observed canonical owners, including Great Expectations, Valibot, msgspec, and Pandera. Forks and repeated language bindings were not used to inflate coverage; monorepos appear once.

Excluded classes include awesome lists, tutorials, schema-only standards repositories, code generators without a substantial validation runtime, and general policy/query engines lacking a focused schema or data-contract role in this selection. The list includes larger ecosystems and less prominent independent implementations, but is not an exhaustive inventory of every validator or a ranking of correctness. C4 is claimed selectively where dated evolution and compatibility/complexity evidence were inspected; inclusion alone does not assert current maintenance status.

Research was read-only. No candidate code, tests, benchmarks, or dependencies were executed, so performance judgments concern documented mechanisms rather than verified throughput. Sources generally follow mutable branches or current documentation and can change after the research date. The Great Expectations legacy design source is explicitly historical, and the Soda Core and Data Contract CLI entries identify major architecture changes. Study-value judgments are grounded in the cited designs but remain engineering assessments, not independent security or conformance audits.
