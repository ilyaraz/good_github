# Declarative configuration languages and evaluators

Research date: 2026-10-09.

This report selects 21 GitHub repositories implementing languages, runtimes, or structural evaluators for defining, composing, validating, and generating configuration. It includes general configuration languages, embedded configuration interpreters, and libraries with substantive interpolation or merge semantics. Serialization-only parsers, deployment controllers, and collections of configuration examples are outside the scope. Separate implementations of a language are retained when their execution architecture offers a distinct study opportunity; each monorepo is counted once.

The criteria below describe reasons to study particular mechanisms, not a claim that every component is exemplary or that the projects are interchangeable production choices.

- **C1 — Difficult correctness:** meaningful invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial language or library mechanisms supporting multiple applications.
- **C3 — Performance and structure:** concrete approaches to runtime, allocation, or scaling constraints within an understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or management of implementation complexity.

## Typed, constrained, and schema-oriented languages

### 1. [cue-lang/cue](https://github.com/cue-lang/cue)

**Language/role:** Go; CUE compiler, evaluator, validation APIs, and configuration tooling.

CUE is especially useful for studying a configuration system where partially specified data and schemas participate in the same constraint model. Its [implementation model](https://github.com/cue-lang/cue/blob/master/doc/ref/impl.md) explains typed feature structures, subsumption, and unification rather than treating validation as a separate pass over ordinary JSON.

- **C1:** Unification must preserve reference meaning, detect inconsistent constraints, and handle cyclic dependencies. The [ADT implementation documentation](https://github.com/cue-lang/cue/blob/master/internal/core/adt/doc.go) makes a particularly subtle rule explicit: references inside a substituted value must follow the substituted structure, while references outside it retain their original target.
- **C2:** The ADT separates resolvers, evaluators, yielders, and validators, supporting partial values and comprehensions as well as concrete data. The repository integrates this model with configuration validation and formats including JSON Schema, OpenAPI, and Protobuf.
- **C3:** The ADT documentation describes implementing substitution through environments and scope offsets instead of physically copying referenced values, with environments shared where possible.

**Entry points:** the implementation model and `internal/core/adt/doc.go` linked above.

### 2. [dhall-lang/dhall-haskell](https://github.com/dhall-lang/dhall-haskell)

**Language/role:** Haskell; Dhall implementation and a monorepo of conversion and editor tools. The relevant subsystem is the `dhall` package.

Study this implementation for the relationship between typed configuration, normalization, and host-language embedding. Its [evaluation machine](https://github.com/dhall-lang/dhall-haskell/blob/main/dhall/src/Dhall/Eval.hs) separates evaluation, conversion checking, closures, and quotation back into normal forms.

- **C1:** Alpha/beta equivalence, variable shifting, substitution, and shadowing must agree with type checking. The [normalization API](https://github.com/dhall-lang/dhall-haskell/blob/main/dhall/src/Dhall/Normalize.hs) explicitly documents that normalization assumes appropriately typed terms and that custom normalizers can change termination properties.
- **C2:** Normalization and custom typing contexts are reusable APIs; the surrounding packages convert the same language to JSON, YAML, TOML, CSV, and other targets.
- **C3:** `Dhall.Eval` documents selective argument forcing and accumulator handling: cheap types can be forced without turning lazy list construction into unnecessarily eager work. This is a concrete study in controlling thunk growth while preserving useful laziness.

**Entry points:** `Dhall/Eval.hs` and `Dhall/Normalize.hs`.

### 3. [nickel-lang/nickel](https://github.com/nickel-lang/nickel)

**Language/role:** Rust; gradually typed configuration language with contracts and record composition.

Nickel offers an unusually explicit implementation of the interaction between lazy functions, record merging, and validation. Its [abstract-machine documentation](https://github.com/nickel-lang/nickel/blob/master/core/src/eval/mod.rs) describes the current term, argument/continuation stack, environments, evaluation-cache updates, and diagnostic call stack.

- **C1:** The [merge implementation](https://github.com/nickel-lang/nickel/blob/master/core/src/eval/merge.rs) recursively combines common fields and their metadata, rejects incompatible values, and distinguishes ordinary merge from contract application. Contract-mode operand order matters; this is not a generic commutative dictionary union.
- **C2:** Functions, reusable records, field metadata, defaults, and contracts form a compositional configuration system. The same merge machinery supports both data construction and record contracts, exposing an instructive boundary between language semantics and runtime validation.

**Entry points:** `core/src/eval/mod.rs` for the machine and `core/src/eval/merge.rs` for composition semantics. The comments also acknowledge limitations of the current reference-counting approach; the implementation should not be read as a finished memory-management ideal.

### 4. [apple/pkl](https://github.com/apple/pkl)

**Language/role:** Java and Kotlin; Pkl runtime, configuration bindings, CLI, and tooling. Focus on `pkl-core`.

Pkl is a good study of prototype-based configuration reuse combined with typed data models. Its [language reference](https://github.com/apple/pkl/blob/main/docs/modules/language-reference/pages/index.adoc) explains amendments, late-bound properties, typed versus dynamic objects, and runtime type constraints.

- **C1:** Amending an object must preserve late binding: dependent properties change when their inputs are overridden. Conversion to an eager map explicitly resolves those dependencies, so converting back cannot restore the former dependency behavior. Type constraints introduce further obligations when values are forced.
- **C2:** Classes, modules, amendments, and reusable constraint functions support families of related configurations. The [evaluator implementation](https://github.com/apple/pkl/blob/main/pkl-core/src/main/java/org/pkl/core/EvaluatorImpl.java) separates module resolution, resource readers, package resolution, security policy, and output forms, making the language embeddable beyond its CLI.

**Entry points:** the language reference and `EvaluatorImpl.java`; the latter also shows how timeout handling and the GraalVM context are integrated into evaluation.

### 5. [kcl-lang/kcl](https://github.com/kcl-lang/kcl)

**Language/role:** Rust; constraint-based record language, evaluator, runtime, and APIs for configuration generation and validation.

KCL is particularly relevant to engineers interested in schema inheritance and composition of cloud configuration. The repository exposes these as language mechanisms rather than a collection of Kubernetes-specific templates.

- **C1:** The [schema evaluator](https://github.com/kcl-lang/kcl/blob/main/crates/evaluator/src/schema.rs) documents a concrete correctness hazard: lazy replay and eager schema-body execution can apply a mixin's augmented assignments twice. It tracks already-applied mixins using names qualified by namespace, because runtime frame identities can differ for protocol-decorated mixins.
- **C2:** The same subsystem represents parent schemas, mixins, optional fields, configuration metadata, and reusable schema contexts. Schema checking and configuration evaluation build on these shared abstractions rather than being implemented separately for each output resource.

**Entry point:** `crates/evaluator/src/schema.rs`, especially `SchemaEvalContext`, its snapshot operations, and the interaction with lazy scopes. This entry concerns the current Rust implementation; older descriptions of KCL's execution strategy should be checked against this source.

### 6. [ruuda/rcl](https://github.com/ruuda/rcl)

**Language/role:** Rust; gradually typed functional configuration generator and JSON query language, with Python integration.

**Repository status:** an official GitHub mirror alongside Codeberg, explicitly listed in the project's [development guide](https://github.com/ruuda/rcl/blob/master/docs/development.md). The project describes itself as pre-1.0.

- **C1:** RCL's [number model](https://github.com/ruuda/rcl/blob/master/docs/numbers.md) uses finite-range decimal arithmetic and preserves decimal-point information. Arithmetic fails when its result cannot be represented exactly; input parsing has a separately documented rounding policy. The [evaluator](https://github.com/ruuda/rcl/blob/master/src/eval.rs) also distinguishes stack-depth protection from an evaluation budget that tracks repeated source locations.
- **C2:** Functions, imports, comprehensions, and gradual annotations support reusable data generation and queries, with both a CLI and a native Python interface. The immutable standard library and cached built-in function types provide clear reusable runtime components.

**Entry points:** `docs/numbers.md` and `src/eval.rs`. The development guide additionally describes golden tests and fuzzing, without implying that those checks were run for this report.

## Lazy functional evaluation and the Jsonnet family

### 7. [NixOS/nix](https://github.com/NixOS/nix)

**Language/role:** C++; Nix expression evaluator inside the Nix package-manager monorepo. The relevant subsystem is `src/libexpr`, not the entire store/build daemon.

Nix is included for its configuration expression language and its coupling of evaluation to dependency provenance. Its [evaluation documentation](https://github.com/NixOS/nix/blob/master/doc/manual/source/language/evaluation.md) explains weak-head normal forms, call-by-need, closures, and where results are retained.

- **C1:** [String contexts](https://github.com/NixOS/nix/blob/master/doc/manual/source/language/string-context.md) carry store dependencies through string interpolation and concatenation. Discarding context changes dependency tracking, so ordinary string manipulation has correctness consequences beyond textual output.
- **C2:** Lazy bindings, functions, and structured values provide reusable configuration composition, while string contexts connect those abstractions to generated files and derivations. This is a useful comparison with languages whose final values contain only ordinary JSON-like data.
- **C3:** Call-by-need avoids evaluating unused portions and retains binding results. The documentation carefully distinguishes this from globally memoizing arbitrary function calls, an important architectural boundary for memory and cache behavior.

**Entry points:** the evaluation and string-context chapters.

### 8. [google/jsonnet](https://github.com/google/jsonnet)

**Language/role:** C++; original Jsonnet implementation, standard library, language documentation, and tests.

Study this alongside the independent implementations below to see how the same lazy configuration semantics map to different runtimes. The [design document](https://github.com/google/jsonnet/blob/master/doc/articles/design.html) grounds its modularity and variant-generation goals in JSON compatibility, functions, and object composition.

- **C1:** In the [VM](https://github.com/google/jsonnet/blob/master/core/vm.cpp), recursive local bindings are created before environments are captured, allowing cycles. The code explicitly preserves an allocation/binding ordering required by garbage collection. Cached thunks, object self bindings, and inherited-field offsets must remain consistent as evaluation proceeds.
- **C2:** A compact data-templating language supports reusable functions, imports, and derived object variants while preserving JSON as the data substrate.

**Entry points:** `doc/articles/design.html` and `core/vm.cpp`.

**Selection caveat:** the repository recommends `go-jsonnet` in preference to its C++ implementation and explicitly says the latter is not hardened for untrusted Jsonnet input. It remains valuable as an original implementation and semantic reference, not an automatic default for new embedding work.

### 9. [google/go-jsonnet](https://github.com/google/go-jsonnet)

**Language/role:** Go; independent Jsonnet evaluator and embedding library.

This implementation is particularly useful for studying the contract between lazy evaluation and application-controlled imports.

- **C1:** The [importer API](https://github.com/google/go-jsonnet/blob/master/imports.go) requires stable contents for repeated import locations and verifies content identity. Its distinct content, AST, and evaluated-value caches make those assumptions explicit. The [thunk implementation](https://github.com/google/go-jsonnet/blob/master/thunks.go) also separates ready values from deferred computations to avoid accidental over-evaluation.
- **C2:** The `Importer` abstraction lets applications define their own meaning of relative paths and content sources; it is more substantial than a fixed filesystem loader. Object-field evaluation separately carries self bindings and lexical bindings.
- **C3:** Cached thunks clear their environment after successful evaluation to reduce memory retention. Imports reuse buffers and cache parsed and evaluated forms, addressing repeated-module workloads without conflating all cache lifetimes.

**Entry points:** `imports.go` and `thunks.go`.

### 10. [databricks/sjsonnet](https://github.com/databricks/sjsonnet)

**Language/role:** Scala; independent Jsonnet implementation targeting the JVM and other Scala platforms.

Sjsonnet provides a particularly readable optimizing-interpreter architecture. Its [architecture overview](https://github.com/databricks/sjsonnet/blob/master/readme.md#architecture) distinguishes parsing, static rewriting/optimization, lazy runtime values, and final materialization.

- **C1:** Lazy object fields and array elements must defer errors until their values are needed. The overview explains the boundary between a deferred `Eval`, a cached `Lazy`, and an already-computed `Val`; this distinction carries through to JSON materialization.
- **C3:** The [evaluator](https://github.com/databricks/sjsonnet/blob/master/sjsonnet/src/sjsonnet/Evaluator.scala) separates import-result caching from external parse caching and contains explicit stack accounting, tail-call argument-buffer reuse, and hot/cold expression-dispatch paths. Comments explain the safety condition for reusing argument buffers.
- **C2:** The pipeline exposes reusable intermediate representations and an interpreter API, making it suitable for studying repeated evaluation in an embedding application.

**Entry points:** the architecture overview and `Evaluator.scala`. Published benchmark comparisons use particular workloads and runtime setups; no general speed ranking is asserted here.

### 11. [deltarocks/jrsonnet](https://github.com/deltarocks/jrsonnet)

**Language/role:** Rust; independent Jsonnet evaluator, CLI, parsers, and bindings. This is the verified canonical destination of the former `CertainLach/jrsonnet` URL.

Jrsonnet offers a different object-runtime design from the Go and Scala implementations. Its [object implementation](https://github.com/deltarocks/jrsonnet/blob/master/crates/jrsonnet-evaluator/src/obj/oop.rs) represents inherited objects as layers of object cores and separates member evaluation from field enumeration and visibility.

- **C1:** Correctness depends on retaining super-depth, field order/visibility, assertions, and the distinction between a final field result and a result requiring superclass addition. Object construction also initializes assertion and value-cache state explicitly.
- **C2:** `ObjectCore`, object builders, native methods, and deferred field values provide reusable embedding abstractions. The [repository overview](https://github.com/deltarocks/jrsonnet/blob/master/README.adoc) documents Rust, WebAssembly, Python, and C/C++ integration paths.

**Entry point:** `crates/jrsonnet-evaluator/src/obj/oop.rs`. The project also experiments with language extensions, so compatibility should be evaluated for the chosen dialect and release rather than inferred from the Jsonnet name. Its performance superlatives are not adopted here.

## Embeddable configuration-language toolkits

### 12. [hashicorp/hcl](https://github.com/hashicorp/hcl)

**Language/role:** Go; toolkit for defining application-specific configuration languages with native and JSON syntax.

HCL is a strong choice for studying separation of a configuration language's common syntax from the host application's domain model. The [language-design guide](https://github.com/hashicorp/hcl/blob/main/guide/language_design.rst) distinguishes rigid block structure from free-form object values and application-provided functions.

- **C1:** The [expression evaluator](https://github.com/hashicorp/hcl/blob/main/hclsyntax/expression.go) handles conditional type unification, nulls, unknown values, value marks, and refined numerical or collection ranges. Preserving marks across an unknown conditional is a concrete information-propagation invariant.
- **C2:** Blocks, attributes, expressions, schemas, and evaluation contexts let applications define distinct languages over the same information model; Terraform and Nomad are examples, not the limits of the abstraction.
- **C4:** The [dated changelog](https://github.com/hashicorp/hcl/blob/main/CHANGELOG.md) records continuing work across 2023–2025 on marked and unknown values, panic fixes, diagnostics, and compatibility-preserving optional hooks.

**Entry points:** the language-design guide and `hclsyntax/expression.go`.

### 13. [google/starlark-go](https://github.com/google/starlark-go)

**Language/role:** Go; embeddable Starlark interpreter for configuration and application-specific scripting.

Starlark permits procedural computation inside configuration generation, but its constrained state model and embedding contracts make it directly relevant to declarative configuration systems.

- **C1:** The [implementation document](https://github.com/google/starlark-go/blob/master/doc/impl.md) explains recursive freezing of values before concurrent sharing. Iterator bookkeeping temporarily prohibits collection mutation; host-defined values and host iteration code must respect these same rules.
- **C2:** The [embedding interface and examples](https://github.com/google/starlark-go/blob/master/README.md) support application-defined functions and types, execution threads, globals, and callable values, allowing many domain-specific configuration environments.
- **C3:** The implementation document explains ordered hash-table design rather than relying on Go maps, and mapping resolved local/free variables to compact indices. These choices follow from deterministic iteration and interpreter workload requirements.

**Entry points:** `doc/impl.md` and the embedding examples in the README. The resource-limit documentation explicitly distinguishes execution-step limits and cancellation from a memory sandbox. Some implementation prose is historical; its old evaluation-strategy discussion is not treated here as a current runtime description.

### 14. [facebook/starlark-rust](https://github.com/facebook/starlark-rust)

**Language/role:** Rust; Starlark runtime used by Buck2, with syntax, embedding, debugging, and language-server components.

The [repository overview](https://github.com/facebook/starlark-rust/blob/main/README.md) explicitly identifies this repository as canonical and distinguishes its current ownership from older copies.

- **C1:** Frozen values are shareable across Rust threads while mutable values are not. The [moving-GC design](https://github.com/facebook/starlark-rust/blob/main/docs/gc.md) explains how reservations and forwarding pointers preserve cyclic object graphs during copying, both for collection and freezing.
- **C2:** Syntax, value conversion, embedding macros, evaluator, debugger, and language-server support form reusable layers for applications that supply their own domain types and functions.
- **C3:** The collector traverses reachable live data instead of visiting discarded objects, and uses the same copying pattern for freezing. The worked cyclic-heap example makes the allocation and reachability tradeoffs unusually approachable.

**Entry points:** `docs/gc.md` and the component map in the README. The project explicitly does not promise API stability between releases; its documented SemVer practice should not be mistaken for an unchanging embedding API.

## Structural configuration generation and compilation

### 15. [carvel-dev/ytt](https://github.com/carvel-dev/ytt)

**Language/role:** Go with embedded Starlark; structured YAML templates, data values, validation, and overlays.

ytt is relevant because it evaluates configuration structures and declarative overlays, not merely strings containing YAML. Study how annotation semantics connect structural selection to an embedded language.

- **C1:** The [overlay match checker](https://github.com/carvel-dev/ytt/blob/develop/pkg/yttlibrary/overlay/match_annotation_expects_kwarg.go) enforces match cardinality, rejects incompatible combinations of `expects`, `missing_ok`, and `when`, and attaches matched source positions to failures. Selecting too many or too few nodes is treated as a semantic error rather than silently patching an unintended structure.
- **C2:** Match expectations can be exact counts, count ranges, alternatives, or Starlark callables. Combined with reusable templates and data values described in the repository, this supports application-specific configuration composition without hard-coding Kubernetes resource types into each operation.

**Entry point:** `pkg/yttlibrary/overlay/match_annotation_expects_kwarg.go`. Its small size makes it a useful first stop before following surrounding overlay operations and the template evaluator.

### 16. [json-e/json-e](https://github.com/json-e/json-e)

**Language/role:** JavaScript, Go, Python, and Rust; one monorepo defining and implementing a structural configuration-templating language.

JSON-e takes a template data structure plus a context data structure and produces another data structure. Taskcluster's task-definition generation is a documented use case. It is a useful study in maintaining one small language across different host runtimes.

- **C1:** The [Go renderer](https://github.com/json-e/json-e/blob/main/internal/jsone.go) validates contexts, separates operators from expression interpretation, tracks error locations, and rejects function values left in rendered output. The [executable specification](https://github.com/json-e/json-e/blob/main/specification.yml) includes interpolation escaping, invalid contexts, special object keys, and expected errors.
- **C2:** Structured operators and context functions enable reusable transformations without relying on textual substitution or the host language's unrestricted `eval`.
- **C4:** The [2021–2026 changelog](https://github.com/json-e/json-e/blob/main/CHANGELOG.md) records cross-implementation conformance work on Unicode indexing, numerical errors, lexical scope, exact error messages, and JavaScript dictionary semantics.

**Entry points:** `internal/jsone.go` and `specification.yml`. Host-provided functions remain part of the application's trust boundary; the language's restrictions do not constrain arbitrary behavior in those callbacks.

### 17. [quattor/pan](https://github.com/quattor/pan)

**Language/role:** Java and Clojure; Pan configuration compiler, documentation, and tools. Focus on the `panc` subsystem.

Pan brings an established infrastructure-management community into this selection. It combines configuration construction with schema and constraint validation and emits machine-readable profiles. The [compiler overview](https://www.quattor.org/development/panc-internals-overview.html) explains compile, build, two validation stages, and output as separate phases.

- **C1:** The [compiler coordinator](https://github.com/quattor/pan/blob/main/panc/src/main/java/org/quattor/pan/Compiler.java) tracks outstanding tasks atomically and consumes task futures through a queue. Its comments identify a specific deadlock risk: object dependencies can exhaust a rigidly fixed build pool, requiring the build-thread limit to grow.
- **C2:** Template construction, user-defined types, validation bindings, and format-specific output are reusable layers rather than machine-specific provisioning actions.
- **C3:** Phase-specific caches and executors reuse intermediate work and parallelize processing while retaining a clear staged architecture.

**Entry points:** the compiler overview and `panc/.../Compiler.java`. The overview uses some older source-layout references; the linked Java path was checked against the current tree.

## Configuration composition libraries and smaller language implementations

### 18. [lightbend/config](https://github.com/lightbend/config)

**Language/role:** Java; HOCON parser, substitution resolver, configuration merging, and JVM API.

HOCON is included for its nontrivial evaluation semantics, not just relaxed JSON syntax. The [specification](https://github.com/lightbend/config/blob/main/HOCON.md) defines substitutions, self references, includes, concatenation, and object merging.

- **C1:** [ResolveContext](https://github.com/lightbend/config/blob/main/config/src/main/java/com/typesafe/config/impl/ResolveContext.java) restricts resolution to the necessary child path to avoid creating spurious cycles through unrelated siblings. It combines identity-based cycle markers, memoized results, and a resolution stack for diagnostics.
- **C2:** Includes, fallback composition, substitutions, and a shared configuration API support reusable settings across JVM libraries and applications.
- **C4:** The [dated release notes](https://github.com/lightbend/config/blob/main/NEWS.md) span years of resolution and compatibility work, including 2020 context-handling changes and 2026 fixes for shadowed substitutions and nested delayed merges. These show continuing management of semantic edge cases rather than age alone.

**Entry points:** `HOCON.md` and `ResolveContext.java`.

### 19. [vstakhov/libucl](https://github.com/vstakhov/libucl)

**Language/role:** C; Universal Configuration Language library with macros, variable substitution, includes, object operations, and validation.

libucl offers a lower-level systems perspective on configuration evaluation. Its [API guide](https://github.com/vstakhov/libucl/blob/master/doc/api.md) connects parser options, object ownership, macro callbacks, variable registration, emission, and schema validation.

- **C1:** Zero-copy parsing creates an explicit lifetime obligation: input storage must outlive objects referring to it. Structural limits separately bound nesting, nodes, allocation, and string/key lengths because input byte size alone does not bound parse-tree cost. The [changelog](https://github.com/vstakhov/libucl/blob/master/ChangeLog.md) records fixes for use-after-free, buffer overflow, iterator leaks, and invalid emission.
- **C2:** A common object model supports parsing, programmatic generation, schema checks, and multiple output formats. Macro handlers and variables let applications extend configuration behavior without replacing the parser.
- **C3:** Zero-copy operation and explicit ownership expose the performance/lifetime tradeoff directly; they are architectural mechanisms, not merely a speed claim.

**Entry point:** `doc/api.md`. The repository explicitly characterizes full macro/include mode as suitable for trusted configuration; this is not a blanket recommendation for parsing hostile input.

### 20. [hydra-ecosystem/omegaconf](https://github.com/hydra-ecosystem/omegaconf)

**Language/role:** Python; hierarchical configuration system with typed nodes, merging, lazy interpolation, and custom resolvers. This is the verified canonical destination of `omry/omegaconf`.

OmegaConf sits at the library end of this category: its embedded interpolation language and typed configuration graph are the relevant components, rather than a standalone general programming language.

- **C1:** The [core node implementation](https://github.com/hydra-ecosystem/omegaconf/blob/main/omegaconf/base.py) resolves interpolation parse trees and then validates or converts their results against destination types. It distinguishes missing values, existing nodes, wrapped callback results, typed containers, and recursive resolver results that cannot safely be materialized.
- **C2:** The [resolver model](https://github.com/hydra-ecosystem/omegaconf/blob/main/website/docs/concepts/resolvers.md) allows nested interpolation arguments and named Python callbacks. This composes with a uniform API for configurations originating in YAML, dataclasses, and command-line arguments.

**Entry points:** `omegaconf/base.py`, particularly interpolation resolution and result validation, and the resolver-concepts guide. Resolver callbacks make evaluation extensible but also mean purity depends on the embedding application.

### 21. [rix0rrr/gcl](https://github.com/rix0rrr/gcl)

**Language/role:** Python; Generic Configuration Language with lazy tuples, composition, includes, and schemas.

**Repository status:** historical study candidate. GitHub metadata checked during research reported the last push as 2017-12-14 and did not mark the repository archived. Current maintenance is not implied.

GCL is smaller and less prominent than the major language implementations, but its design exposes configuration-specific scoping tradeoffs clearly.

- **C1:** The [scoping document](https://github.com/rix0rrr/gcl/blob/master/docs/source/scoping.md) explains why lexically invisible fields must remain invisible after tuple composition: adding a field to a distant base tuple must not silently capture a name. The [runtime](https://github.com/rix0rrr/gcl/blob/master/gcl/runtime.py) binds thunks to environments and validates/attaches schemas on member access before caching values.
- **C2:** Tuples serve as data records, parameterized components, and composable models. Empty declarations act as inputs; applying parameters to an included file supports partial application of a collection of related tuples.

**Entry points:** `docs/source/scoping.md` and `gcl/runtime.py`. Its age makes it a design and implementation reading candidate, with dependency and runtime suitability requiring separate assessment.

## Coverage, search method, and limitations

Discovery used more than six distinct live web-search formulations, including broad typed-language comparisons; Jsonnet implementation and performance searches; Starlark freezing and embedding searches; Python GCL and lazy tuple semantics; RCL and smaller configuration languages; Pan/Quattor compilation; UCL/HOCON libraries; ytt structural overlays; and JSON-e data-structure parameterization. Follow-up searches for newer language names and alternate YAML evaluators mostly returned already-covered families, wrappers, or less substantiated projects. JSON-e was retained from that later pass because it added both a different language model and multi-language conformance work.

Every retained repository's canonical identity was checked through its GitHub repository page or public API. Repository metadata and recursive source listings were inspected, followed by actual reads of implementation files, design documents, specifications, or changelogs. JSON-e's repository page supplied identity verification after the unauthenticated API quota was exhausted. No candidate code was executed, dependencies installed, repositories cloned, or benchmark results independently reproduced.

The selection spans Go, Rust, Haskell, C++, Java, Kotlin, Scala, Clojure, Python, C, and JavaScript; language ecosystems associated with CUE, Dhall, Nix, HashiCorp, Apple, Meta, Databricks, Carvel, Quattor, and independent maintainers are represented. The four Jsonnet implementations are separate substantive runtimes, not forks counted to inflate coverage. Likewise, the Starlark implementations expose materially different host-runtime and memory models. Monorepos such as Pkl, Dhall Haskell, Nix, Pan, and JSON-e each appear once.

Important exclusions are serialization-only JSON/YAML/TOML/KDL implementations, generic expression or policy engines without a primary configuration-language role, deployment tools whose evaluator is incidental to a much larger operational system, configuration bundles, and thin wrappers such as the discovered `rjsone` CLI. The specification-only Starlark and Dhall repositories informed discovery but were not counted separately from implementation projects. No unofficial mirrors or relocated projects lacking a substantive official GitHub presence were intentionally retained.

Criterion assignments are engineering judgments grounded in the cited mechanisms. Default-branch code may be newer than a published release, and older design documents can lag implementation; concrete current-code claims were preferred where that distinction mattered. GCL is explicitly historical, RCL is an official mirror and pre-1.0, and adoption/support conclusions should not be inferred from repository age, stars, an unarchived flag, or this selection alone.
