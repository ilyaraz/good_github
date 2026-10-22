# Source-to-source compilers and transpilers

Research date: **2026-10-09**.

This report selects **22 GitHub repositories** that translate programming-language source into another source language, lower a language into an older dialect, or perform substantial source-preserving transformations. It includes general-purpose language compilers, scientific-computing translators, and SQL and shader translators. For mixed-purpose repositories, the relevant subsystem is identified. Binary-only compilation, decompilation, parser libraries without a substantive translation pipeline, and thin integration wrappers are outside the selection.

The criteria below are engineering-study judgments grounded in the linked implementation and documentation, not certifications of complete semantic equivalence or uniformly exemplary code. Each repository page and at least one additional primary source were opened and read. No candidate code was executed, and no performance numbers were independently reproduced.

## Criteria legend

- **C1 — Difficult correctness:** nontrivial semantic, representation, concurrency, numerical, invariant, or failure-handling obligations.
- **C2 — Reusable abstractions:** substantial intermediate representations, transformation interfaces, compiler services, or runtime abstractions serving multiple use cases.
- **C3 — Performance with structure:** concrete compiler-throughput, generated-code, memory, or execution constraints addressed through understandable architectural choices.
- **C4 — Sustained evolution:** dated evolution accompanied by compatibility, testing, or complexity-management evidence. Age or a recent commit alone does not qualify.

## JavaScript and TypeScript transformation pipelines

### 1. [babel/babel](https://github.com/babel/babel)

**Language/role:** JavaScript and TypeScript; JavaScript syntax lowering and a programmable transformation ecosystem.

Babel is useful for studying the boundary between a syntax rewrite and a semantics-preserving compiler pass. Its configurable assumptions make otherwise hidden obligations visible: getters may have effects, imported bindings can remain live, and iterators may need closing when execution exits abnormally.

- **C1:** The assumptions documentation explains when transformations can change observable behavior, including iterator closing, superclass stability, and private-field representation. This is concrete evidence of correctness work and of deliberately restricted optimization contracts. [Compiler assumptions](https://babeljs.io/docs/assumptions).
- **C2:** The traversal API exposes visitor callbacks and node paths for inspecting and updating an AST, allowing transformations to share traversal machinery rather than each implementing a parser and tree walker. [Traversal API](https://babeljs.io/docs/babel-traverse).

**Entry points:** The two guides above provide a practical route from a semantic obligation to the visitor-based implementation model. Treat an enabled assumption as an application promise, not an unconditional equivalence guarantee.

### 2. [swc-project/swc](https://github.com/swc-project/swc)

**Language/role:** Rust; JavaScript/TypeScript parsing, transformation, and source emission.

SWC offers a particularly explicit account of what must happen between parsing and printing. Its resolver, hygiene pass, and fixer solve different problems that are easy to conflate in a smaller transpiler.

- **C1:** Resolution assigns identifiers context-sensitive identities; hygiene prevents conflicting names after transformations; the fixer repairs syntactic requirements such as parentheses and precedence. The architecture document also describes parser validation against Test262 and code-generation fixtures. [Architecture](https://github.com/swc-project/swc/blob/main/ARCHITECTURE.md).
- **C2:** Interned atoms, spans and diagnostics, ECMAScript ASTs, parsing, code generation, and visitor/folder interfaces are separated into crates. This supports independently reusable passes while retaining a shared representation. [Architecture and crate map](https://github.com/swc-project/swc/blob/main/ARCHITECTURE.md).

**Entry point:** Follow the architecture document's resolver → transform → hygiene/fixer sequence before exploring individual syntax transforms. The useful lesson is the ordering of invariants across passes, beyond Rust implementation technique.

### 3. [evanw/esbuild](https://github.com/evanw/esbuild)

**Language/role:** Go; JavaScript/TypeScript lowering, optimization, source emission, and bundling. The lowering and compiler pipeline are the relevant subsystem.

The architecture document connects compiler speed to data ownership and pass organization, while explaining semantic constraints imposed by modules and code splitting.

- **C1:** Shared ASTs must remain immutable across incremental builds; mutable symbol information is handled separately. Code splitting must also respect assignment/export relationships because imported bindings cannot simply be reassigned in another chunk. These are concrete cross-pass and cross-file invariants. [Architecture](https://github.com/evanw/esbuild/blob/main/docs/architecture.md).
- **C3:** Parallel scanning, a small number of AST passes, symbol indirection, and choices intended to improve locality are described with their tradeoffs. Performance is connected to identifiable structures rather than only benchmark claims. [Passes, symbols, and parallelism](https://github.com/evanw/esbuild/blob/main/docs/architecture.md).

**Entry point:** Read the architecture document's parsing, linking, and code-splitting sections together. They show how an implementation optimized for build latency keeps semantic responsibilities explicit.

### 4. [microsoft/TypeScript](https://github.com/microsoft/TypeScript)

**Language/role:** TypeScript; the TypeScript implementation of the compiler, including JavaScript, declaration-file, and source-map emission.

Study how a source compiler becomes a reusable program-analysis service. The official compiler notes trace source files through binding, program construction, type checking, and emission; their authors explicitly describe the notes as contributor guidance rather than an exhaustive API specification.

- **C1:** Several declarations can denote one symbol, including a class and namespace with the same name. Binding and program-wide merging must preserve scope and identity across files before type relationships can be answered correctly. [Compiler pipeline notes](https://github.com/microsoft/TypeScript-Compiler-Notes/blob/main/README.md).
- **C2:** `SourceFile`, `Program`, `TypeChecker`, and the emitter expose different levels of compiler service. The query-driven checker resolves the information needed for a question, supporting uses beyond one-shot transpilation. [Compiler services and lazy checking](https://github.com/microsoft/TypeScript-Compiler-Notes/blob/main/README.md).

**Entry point:** The linked Microsoft compiler-notes repository documents this implementation; it is supporting evidence, not a second selected project. This entry does not assume that all newer TypeScript compiler implementations reside here.

### 5. [google/closure-compiler](https://github.com/google/closure-compiler)

**Language/role:** Java; JavaScript source optimization and language lowering.

Closure Compiler is a strong study target for coordinating many interacting transformations. Its phase scheduler is substantial enough to expose the engineering behind repeatedly optimizing an AST without losing control of execution cost or correctness checks.

- **C1:** `PhaseOptimizer` groups repeatable passes into fixed-point loops, tracks reported changes, supports change-verification and validity checks, and limits iteration. Correct change reporting becomes part of the pass contract. [PhaseOptimizer implementation](https://github.com/google/closure-compiler/blob/master/src/com/google/javascript/jscomp/PhaseOptimizer.java).
- **C3:** Scheduling distinguishes passes that changed the program from those that did not, while iteration and size heuristics bound optimization work. Pass instances are created for execution rather than retained with all their temporary state. [Scheduling implementation](https://github.com/google/closure-compiler/blob/master/src/com/google/javascript/jscomp/PhaseOptimizer.java).

**Entry point:** `PhaseOptimizer.java` is a compact route into the larger optimizer: follow `PassFactory`, `CompilerPass`, and change-tracking interactions from this file.

## Bridging language and runtime semantics

### 6. [HaxeFoundation/haxe](https://github.com/HaxeFoundation/haxe)

**Language/role:** OCaml compiler with a Haxe standard library; Haxe compilation to source targets including JavaScript, C++, Python, Lua, and PHP.

Haxe is useful for studying a language designed around multiple targets and compiler-time extension. Its macro stages and dead-code elimination expose how extensibility interacts with the compiler's knowledge of a program.

- **C2:** Initialization, build, and expression macros operate at different points relative to typing, using structured compiler representations. This supplies reusable extension mechanisms for generating types and expressions across applications. [Macro architecture](https://haxe.org/manual/macro.html).
- **C1:** Reachability-based elimination cannot discover every reflective or dynamically accessed member. The documented `@:keep`, `@:keepSub`, and related metadata establish explicit preservation obligations; the DCE account also explains why an earlier approach interacted badly with eager interface typing. [Dead-code elimination](https://haxe.org/manual/cr-dce.html).

**Entry points:** The macro-stage guide and DCE guide are complementary: one explains how code enters the typed program, the other how apparently unused code leaves it. Only Haxe's source-output targets are in scope here.

### 7. [fable-compiler/Fable](https://github.com/fable-compiler/Fable)

**Language/role:** F#; F# translation to JavaScript and other source-language backends.

Fable illustrates the choice between preserving source-language abstractions through a runtime library and mapping them directly onto a target's native types.

- **C1:** The JavaScript compatibility guide details representations for numbers, 64-bit integers, numeric arrays, and collections. Structural equality can require custom map/set implementations, while other cases use native JavaScript collections. These choices affect observable behavior, not just syntax. [JavaScript compatibility](https://fable.io/docs/javascript/compatibility.html).
- **C2:** The documented Erlang backend pipeline passes through `FSharp2Fable`, the Fable AST, shared transformations, a target AST, and a printer. This is a concrete example of separating common translation from backend representation. [Backend pipeline](https://fable.io/docs/beam/build-and-run.html).

**Entry points:** Start with the compatibility guide, then the backend pipeline. The Erlang documentation describes a newer target; this selection does not imply identical maturity or library coverage across all Fable targets, or complete .NET compatibility.

### 8. [gopherjs/gopherjs](https://github.com/gopherjs/gopherjs)

**Language/role:** Go with a JavaScript runtime; Go source to JavaScript.

GopherJS is valuable for studying concurrency translation and the recurring cost of matching an upstream language and standard library.

- **C1:** Its architecture explains how potentially blocking goroutine execution unwinds and later restores execution state and local variables. Interoperation with externally invoked JavaScript callbacks introduces restrictions on blocking behavior. Integer representation also requires explicit emulation choices. [Architecture in the repository guide](https://github.com/gopherjs/gopherjs#architecture).
- **C4:** The repository's dated history records Go-version support from 2021 through 2026, including modules and generics. The compatibility document explains the separate language, standard-library, and tooling layers and the need to align supported Go versions. [Release chronology](https://github.com/gopherjs/gopherjs#whats-new), [compatibility document](https://github.com/gopherjs/gopherjs/blob/master/doc/compatibility.md).

**Entry points:** Architecture and compatibility are the best pair. Some compatibility text lags newer repository announcements—for example, older module limitations—so use the dated release information when resolving version-specific claims. Cgo is outside the supported translation surface described by the repository.

### 9. [google/j2cl](https://github.com/google/j2cl)

**Language/role:** Java; Java-to-Closure-JavaScript transpiler and supporting runtime. The JavaScript path is the relevant subsystem.

J2CL's data-representation documentation makes the tension between Java semantics and JavaScript execution especially concrete.

- **C1:** Java's numeric and boxed types do not map uniformly to JavaScript primitives. The semantics guide explains integer emulation, special handling of `long`, and why boxed `Integer` needs a distinct representation to preserve type distinctions such as `instanceof`. [Data types and semantics](https://github.com/google/j2cl/blob/master/docs/semantics.md).
- **C3:** Selected boxed values, such as `Double` and `Boolean`, use native JavaScript representations, while other types retain wrappers. This selectively avoids representation overhead where the documented semantic mapping permits it. [Representation decisions](https://github.com/google/j2cl/blob/master/docs/semantics.md).

**Entry point:** Read `docs/semantics.md` before following the transpiler and runtime implementation. The repository itself cautions that open-source workflows and tooling are not all finalized; its existence and internal production use should not be read as a turnkey compatibility promise.

### 10. [google/j2objc](https://github.com/google/j2objc)

**Language/role:** Java and Objective-C; translation of Java application logic into Objective-C for Apple platforms.

J2ObjC is a useful counterpoint to Java-to-JavaScript systems because object ownership and synchronization become central translation concerns. Its stated application is sharing non-UI Java logic, with supporting runtime emulation.

- **C1:** The memory-model guide documents differences between garbage collection and reference counting, retention cycles, synchronization, and volatile fields. It distinguishes primitive atomic access from object-field locking and explains limitations relative to Java's memory model. [Memory-model guide](https://developers.google.com/j2objc/guides/j2objc-memory-model).
- **C3:** The documented reference-counting strategy avoids retaining local-variable assignments while treating field stores differently. The threading design similarly distinguishes where atomic or mutex operations are needed. These are inspectable ownership and synchronization cost decisions. [Ownership and concurrency implementation model](https://developers.google.com/j2objc/guides/j2objc-memory-model).

**Entry point:** The memory-model guide is the strongest starting point. Treat its described strategy as the documentation's model, and check translation options when investigating a particular generated program; it is not a claim that Java and Objective-C have identical lifetime or threading behavior.

### 11. [TypeScriptToLua/TypeScriptToLua](https://github.com/TypeScriptToLua/TypeScriptToLua)

**Language/role:** TypeScript and Lua; TypeScript-to-Lua compiler with runtime helpers and plugin APIs.

This project is particularly useful for studying a target whose basic value semantics differ from JavaScript, while retaining TypeScript tooling and type information.

- **C1:** The caveats document covers `null`/`undefined` collapsing into Lua `nil`, different truthiness rules, array holes and length, and target-version differences. It also explains why types can affect emitted code, making type correctness relevant to translation behavior. [Semantic caveats](https://typescripttolua.github.io/docs/caveats/).
- **C2:** Plugins can transform TypeScript AST nodes into Lua AST nodes, delegate to existing visitors through the transformation context, replace printing, and participate in compilation hooks. These are reusable compiler extension points rather than text substitution. [Plugin API](https://typescripttolua.github.io/docs/api/plugins/).

**Entry points:** Read caveats before implementing a visitor through the plugin API. Successful compilation alone does not establish JavaScript-equivalent behavior, particularly for truthiness and sparse arrays.

## Python source translators and numerical compilation

### 12. [cython/cython](https://github.com/cython/cython)

**Language/role:** Python/Cython with C runtime support; Python-like source to C or C++ extension code.

Cython is a substantial example of combining Python object semantics with progressively more explicit native types and operations. Its internal guide explains details that are often hidden behind a simple “AST passes” diagram.

- **C1:** Declaration analysis, expression analysis, and generic visitors use different traversal mechanisms. Child ordering and bespoke analysis order matter; a new node must integrate with each applicable mechanism rather than merely print valid C. [Compiler internals](https://docs.cython.org/en/latest/src/devguide/cython_internals.html).
- **C2:** Statement and expression nodes, transforms, type analysis, and shared `UtilityCode` helpers separate translation logic from reusable runtime support. The guide describes utility-code handling for common C support, cached objects, and module-level state. [Nodes, transforms, and utility code](https://docs.cython.org/en/latest/src/devguide/cython_internals.html).

**Entry point:** The internals guide links the conceptual stages to their implementation files. It is especially useful when comparing a language-extension compiler with translators that accept a narrower subset of ordinary Python.

### 13. [serge-sans-paille/pythran](https://github.com/serge-sans-paille/pythran)

**Language/role:** Python frontend and C++ support library; ahead-of-time translation of a numerical Python subset into C++.

Pythran exposes how source normalization and effect analysis support optimization without requiring every later pass to handle the full surface language.

- **C1:** Alias analysis distinguishes possible references, while argument and global-effect analyses account for mutation and purity across calls. Such facts determine whether an optimization may safely reorder, remove, or specialize work. [Developer tutorial: analyses](https://pythran.readthedocs.io/en/latest/TUTORIAL.html).
- **C2:** A pass manager provides interfaces for applying transformations, gathering analyses, and invoking backends. Normalizations, such as simplifying tuple unpacking, reduce the forms that subsequent stages must understand; both C++ and Python-oriented output are described. [Pass manager and normalization](https://pythran.readthedocs.io/en/latest/TUTORIAL.html).

**Entry point:** The developer tutorial is a route into the analysis/transform/backend organization, distinct from installation-oriented examples. The selection concerns the supported numerical subset, not unrestricted CPython programs or all dynamic Python behavior.

### 14. [pyccel/pyccel](https://github.com/pyccel/pyccel)

**Language/role:** Python; scientific Python translation to languages including C and Fortran, plus extension-generation support.

Pyccel is useful for studying array semantics and the point where a high-level operation must become explicit allocation, indexing, and cleanup.

- **C1:** Semantic annotation records precision, rank, shape, and memory order. Scope-aware allocation and pointer tracking address object lifetime, while semantic errors can prevent code generation. The printer guide explains why even an integer literal's precision must be preserved. [Semantic stage](https://pyccel.github.io/pyccel/developer_docs/semantic_stage.html), [code generation](https://pyccel.github.io/pyccel/developer_docs/codegen_stage.html).
- **C2:** A shared typed AST feeds language-specific `CodePrinter` subclasses. Common loop-expansion machinery lowers vector expressions as required by each target; C and Fortran printers handle different array capabilities through that framework. [Printer and loop-expansion architecture](https://pyccel.github.io/pyccel/developer_docs/codegen_stage.html).

**Entry points:** The semantic and code-generation guides should be read together. The latter candidly discusses imperfect separation between common semantics and backend-specific changes, making it useful for studying architectural tradeoffs as well as abstractions.

### 15. [TranscryptOrg/Transcrypt](https://github.com/TranscryptOrg/Transcrypt)

**Language/role:** Python compiler and JavaScript runtime; a Python subset to JavaScript for browser and JavaScript-library integration.

Transcrypt emphasizes readable, lightweight output and lets users localize some expensive Python facilities. The canonical repository is under `TranscryptOrg`; older references to a different owner should not be counted separately.

- **C2:** Module handling accommodates Python and JavaScript modules, while identifier aliasing and compiler pragmas support reusable interoperability patterns with native JavaScript APIs. [Special facilities and module handling](https://www.transcrypt.org/docs/html/special_facilities.html).
- **C3:** Operator-overload support can be enabled locally to avoid pervasive dispatch overhead. The documented fast-call mechanism binds and caches methods on instances, trading larger objects for avoiding repeated prototype-chain searches. [Pragmas and fast-call design](https://www.transcrypt.org/docs/html/special_facilities.html).

**Entry point:** The special-facilities chapter exposes the concrete code-generation tradeoffs. These facilities should be evaluated against the supported Python subset and application needs; the report does not repeat the documentation's broad speed comparisons as measured facts.

### 16. [shedskin/shedskin](https://github.com/shedskin/shedskin)

**Language/role:** Python and C++; implicitly statically typed Python-subset translation into C++ programs or extension modules.

Shed Skin provides an unusually focused entry into whole-program type inference and specialization. The inference source includes an explanatory overview of its algorithms and their resource constraints.

- **C1:** Types propagate through a constraint graph, with function specialization and container-allocation distinctions used to recover precision when different flows merge. The implementation combines Cartesian Product Algorithm and Iterative Flow Analysis ideas rather than assuming local annotations suffice. [Inference implementation](https://github.com/shedskin/shedskin/blob/main/shedskin/infer.py).
- **C3:** Incremental analysis and limits on specialization address combinatorial growth and memory consumption. The algorithm makes the precision-versus-resource tradeoff visible in a central implementation file. [Inference scheduling and limits](https://github.com/shedskin/shedskin/blob/main/shedskin/infer.py).

**Entry point:** Start with `shedskin/infer.py` and its introductory explanation. The restricted, statically inferable input subset is an essential part of the design, not evidence that arbitrary Python can be translated with the same behavior.

## C-family migration and scientific source transformation

### 17. [immunant/c2rust](https://github.com/immunant/c2rust)

**Language/role:** Rust and C++; C-to-Rust translation infrastructure, initially producing Rust that can retain unsafe operations.

C2Rust is valuable for separating faithful migration from later safety and idiom improvements. Its translation boundary includes a real C frontend, an explicit serialized AST, and control-flow restructuring.

- **C1:** The source walkthrough explains typed C AST identities and a Relooper-based stage that restructures `goto` and `switch` control flow for Rust. Preserving control flow and C representation semantics is the core difficulty; producing Rust does not itself establish memory safety. [Source walkthrough](https://github.com/immunant/c2rust/blob/master/docs/source_walkthrough.md).
- **C2:** Clang AST export, CBOR transfer, typed AST consumption, and a Rust AST builder are separated. The builder provides reusable construction machinery shared with translation/refactoring work. [Subsystem boundaries](https://github.com/immunant/c2rust/blob/master/docs/source_walkthrough.md).

**Entry point:** Use the in-tree walkthrough. The repository warns that its older public manual is outdated; the walkthrough also labels some historical infrastructure, including removed cross-checking components. Those components are not claimed here as current validation capabilities.

### 18. [llnl/rose](https://github.com/llnl/rose)

**Language/role:** C++; a source-analysis and transformation framework for languages including C, C++, and Fortran. Source translation, rather than its binary-analysis subsystem, is in scope.

ROSE is useful for studying the substantial metadata needed to reconstruct compilable source after changing a rich AST.

- **C1:** Its FAQ explains why defining and non-defining declarations must remain distinct, why an AST parent can differ from lexical scope, and how source-file information controls whether transformed nodes are emitted. These details prevent incorrect declaration ordering and unintended header emission. [AST and translation FAQ](https://github.com/llnl/rose/wiki/FAQ).
- **C2:** Traversal facilities, `SageBuilder`, and `SageInterface` provide reusable analysis and construction operations. The FAQ's cloning example combines tree modification, symbol handling, invariant checks, and regeneration. [Transformation examples](https://github.com/llnl/rose/wiki/FAQ).

**Entry point:** Start with the FAQ's AST and Translation sections. Some examples describe older configurations; the FAQ explicitly says identity translation is not byte-for-byte preservation. Its discussion of the EDG frontend also makes clear that not every frontend component is available as source in this repository.

### 19. [ecmwf-ifs/loki](https://github.com/ecmwf-ifs/loki)

**Language/role:** Python; programmable Fortran source transformation, particularly for scientific kernels. The repository labels the project **incubating**.

Loki offers a smaller, domain-focused alternative to broad compiler frameworks. Its intermediate representation explains how transformations can retain Fortran structure while manipulating expressions and declarations.

- **C2:** Containers, control-flow nodes, expression trees, and type/scope information form separate layers. Expression mapping builds on Pymbolic while adding Fortran-specific comparison, grouping, and metadata behavior. [Internal representation](https://sites.ecmwf.int/docs/loki/main/internal_representation.html).
- **C1:** Scoped symbols share attributes through hierarchical symbol tables, keeping uses tied to declarations. The documentation also identifies an important invariant hazard: removing an array shape does not automatically repair every array-expression node or subscript. Transform authors must explicitly restore consistency. [Types, scopes, and mutation caveats](https://sites.ecmwf.int/docs/loki/main/internal_representation.html).

**Entry point:** The internal-representation guide is both an architecture overview and a guide to transformation responsibilities. C1 reflects the real invariants exposed by this design, not a claim that arbitrary user-written transformations are automatically verified.

### 20. [stfc/PSyclone](https://github.com/stfc/PSyclone)

**Language/role:** Python; Fortran-to-Fortran optimization, parallelization, and instrumentation, including scientific DSL support.

PSyclone connects compiler transformation interfaces to HPC concerns such as loop dependencies, halo exchanges, privatization, and synchronization.

- **C1:** Dependency information propagates from accesses and kernels to enclosing schedule nodes, preventing invalid movement across dependencies. Parallel-loop transformation code rejects problematic calls and dependencies, checks whether privatized values escape, and can insert barriers before dependent statements for asynchronous execution. [Dependency analysis](https://psyclone.readthedocs.io/en/latest/developer_guide/dependency.html), [parallel-loop implementation](https://psyclone.readthedocs.io/en/latest/_modules/psyclone/psyir/transformations/parallel_loop_trans.html).
- **C2:** Shared PSyIR access analysis and an abstract parallel-loop transformation separate general legality checks from subclasses that construct particular directives. The same infrastructure supports multiple transformation scripts and scientific domains. [Transformation abstraction](https://psyclone.readthedocs.io/en/latest/_modules/psyclone/psyir/transformations/parallel_loop_trans.html).

**Entry points:** Read dependency analysis alongside `ParallelLoopTrans`. Options that force transformations or ignore selected dependencies transfer obligations to the caller; the presence of validation machinery does not make those overrides semantically safe by default.

## Domain languages: SQL and shaders

### 21. [tobymao/sqlglot](https://github.com/tobymao/sqlglot)

**Language/role:** Python; SQL parsing, dialect-to-dialect source translation, and AST transformations.

SQLGlot broadens the category beyond general-purpose languages. It is useful for studying a shared semantic representation across dialects whose syntax, identifiers, functions, and type rules differ.

- **C2:** Tokenizer, parser, and generator form the core translation pipeline. Dialects extend common behavior with flags and overrides, reducing duplication while retaining dialect-specific parsing and emission. [Contributor architecture guide](https://github.com/tobymao/sqlglot/blob/main/posts/onboarding.md).
- **C1:** Qualification and type annotation supply context needed for meaningful transformations. The guide also describes an explicit failure boundary: an unparsed statement can become an `exp.Command` and be returned unchanged, so its dialect-specific content has not been translated. [Schema, optimizer, and command fallback](https://github.com/tobymao/sqlglot/blob/main/posts/onboarding.md).

**Entry point:** The onboarding guide explains the AST pipeline and its limits. An unchanged fallback is not proof of portability. Some historical implementation details in that guide lag the main repository, so this entry does not rely on its older tokenizer-acceleration description.

### 22. [gfx-rs/wgpu](https://github.com/gfx-rs/wgpu) — Naga subsystem

**Language/role:** Rust; Naga's shader parsing, validation, and translation, including WGSL/GLSL source input and GLSL, HLSL, Metal, and WGSL source output.

Only **Naga**, within the wgpu monorepo, is selected here. This is one repository entry; the former standalone Naga location is not counted separately. Binary SPIR-V paths are adjacent capabilities rather than the basis for category fit.

- **C2:** A frontend produces a shared `Module`; validation produces `ModuleInfo`; a backend writer consumes both with target, pipeline, and bounds-check options. Feature-selected frontends and backends reuse this boundary. [Library pipeline example](https://github.com/gfx-rs/wgpu/blob/trunk/naga/src/lib.rs).
- **C1:** The pipeline includes explicit validation and bounds-check policies. Development documentation supplements snapshots with checks using target-platform validators such as Metal, GLSL, and HLSL tools. These checks address generated-language validity, though they are not a proof of behavioral equivalence. [Naga support matrix and validation workflow](https://github.com/gfx-rs/wgpu/blob/trunk/naga/README.md).

**Entry points:** `naga/src/lib.rs` and `naga/README.md`. Consult the support matrix: frontend/backend support levels and accepted shader dialects are not uniform.

## Coverage, search process, and limitations

Live discovery used more than six distinct query families, followed by direct inspection of repository pages, official manuals, design notes, and implementation files. Search angles included:

- JavaScript and TypeScript lowering, hygiene, compiler passes, and source emission.
- C/C++ source-transformation frameworks and C-to-Rust migration.
- Python-to-C/C++/Fortran numerical compilation, type inference, and runtime specialization.
- F#, Go, and Java translation to JavaScript, and Java translation to Objective-C.
- Multi-target languages, macro systems, and TypeScript-to-Lua embedding.
- Fortran HPC transformation, dependency analysis, and automatic parallelization.
- SQL dialect ASTs and source translation.
- Shader-language frontends, validation, and source backends.
- Additional language communities, including OCaml/JavaScript, Nim, PureScript, and Ruby/JavaScript, as a check against stopping at the most familiar compiler projects.

Later discovery increasingly returned already-covered projects, thin wrappers, or adjacent compiler categories. The final set balances large ecosystems with smaller substantive implementations such as Loki, Pyccel, Shed Skin, and TypeScriptToLua. It is selective rather than exhaustive; omission is not a negative quality judgment.

Excluded were awesome-lists, tutorials, generated API wrappers, loader plugins around another compiler, generic parser-only libraries, learned-translation demos without comparable compiler infrastructure, and systems whose relevant input/output path is exclusively bytecode or machine code. Monorepos are counted once. Repositories that only point to a replacement were not retained as separate projects, and no unofficial fork is presented as an independent implementation.

Documentation can lag source and released capabilities. Specific discrepancies or caveats are noted for GopherJS, C2Rust, ROSE, SQLGlot, and newer Fable targets; Loki's incubating status is explicit. No blanket active-maintenance claim is made, and C4 is assigned only where dated evolution and compatibility evidence were inspected. C1–C3 judgments identify worthwhile mechanisms and engineering obligations; they do not assert that every component satisfies them equally or that translations preserve every behavior of unrestricted source programs.
