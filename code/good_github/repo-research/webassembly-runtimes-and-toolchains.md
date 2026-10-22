# WebAssembly runtimes and toolchains

Research date: **2026-10-09**

This report selects 25 GitHub repositories spanning WebAssembly execution engines, embedded interpreters, binary transformation and validation libraries, language compilers, linking, host bindings, and WASI support. The focus is code that implements execution semantics or reusable compilation and integration machinery. Large monorepos count once, with the relevant subsystem identified. These are study recommendations supported by primary documentation and implementation material, not an assertion that every component is equally exemplary or suitable for every deployment.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions supporting multiple uses. **C3** — real performance or resource constraints addressed through understandable architecture. **C4** — sustained evolution accompanied by evidence of compatibility, testing, or complexity management. Each entry gives at least two specific reasons; the absence of a criterion is not a negative judgment.

## Execution engines and interpreters

### 1. [bytecodealliance/wasmtime](https://github.com/bytecodealliance/wasmtime)

**Rust; standalone and embeddable runtime, including its Cranelift compiler subsystem.** Study how a safe embedding API sits above compiled-code interfaces, instance allocation, and low-level runtime state. The separation between an engine's shared compilation resources and a store's execution objects makes this particularly useful for understanding runtime ownership.

- **C1:** Store access rules prevent simultaneous mutable access to execution state. Below that boundary, instance handles and `VMContext` layouts carry allocation, lifetime, and generated-code invariants. The architecture documentation also identifies boundaries where unsafe abstractions remain difficult.
- **C2:** `Engine`, `Module`, and `Store` separate shared compilation, reusable compiled artifacts, and individual execution environments. This supports multiple embeddings without requiring each application to understand the lower-level instance machinery.

**Entry point:** the [architecture guide](https://docs.wasmtime.dev/contributing-architecture.html), especially the embedding API and runtime sections. Cranelift, Winch, and other in-repository execution components are not counted separately.

### 2. [wasmerio/wasmer](https://github.com/wasmerio/wasmer)

**Rust; embeddable runtime with interchangeable compilation and execution facilities.** Useful for studying a runtime API that accommodates multiple backends while retaining common module, instance, memory, and host-function concepts.

- **C2:** Engines and compilers are separate abstractions; imports, exports, and typed or dynamically typed host functions give applications reusable interfaces independent of a particular compiler configuration.
- **C3:** Compiled-module serialization and headless execution move compilation outside the deployed runtime. The architecture exposes a concrete choice between compilation cost, generated-code behavior, and the footprint of shipping compiler machinery.

**Entry point:** the [Rust API guide](https://wasmerio.github.io/wasmer/crates/doc/wasmer/), including engines, compilers, caching, and headless operation. Its architectural mechanisms are the evidence here; marketing benchmark comparisons are not used.

### 3. [WasmEdge/WasmEdge](https://github.com/WasmEdge/WasmEdge)

**C++; embeddable runtime with interpreter/AOT support and host extensions.** Its C embedding interface provides an unusually explicit view of a module's progression through loading, validation, linking, and execution.

- **C1:** The API distinguishes AST modules, validated code, runtime instances, and stores. Stores reference module instances without taking ownership, so deletion and unlinking rules matter; each processing stage also exposes explicit failure results.
- **C2:** Loader, validator, executor, store, and host-module contexts can be assembled separately. The same embedding structure handles ordinary Wasm and compiled Wasm inputs and connects reusable host implementations to module imports.

**Entry point:** the [C API reference](https://wasmedge.org/docs/embed/c/reference/latest/), particularly Loader, Validator, Executor, Store, and module-instance ownership. This recommendation does not imply that arbitrary concurrent use of its contexts is safe.

### 4. [wasm-micro-runtime/wasm-micro-runtime](https://github.com/wasm-micro-runtime/wasm-micro-runtime)

**C, with C++ compiler components; WAMR, an embedded and general-purpose runtime.** The repository now lives under the `wasm-micro-runtime` organization; the former Bytecode Alliance location is not a second project. Its interpreter, AOT, and JIT modes expose different deployment choices within one runtime.

- **C2:** Runtime allocation can use a supplied memory pool, application allocators, or system allocation. Execution modes and platform adaptation make the same core usable across host applications and constrained devices.
- **C3:** Memory tuning separates the runtime heap, Wasm operand stack, linear memory, auxiliary stack, and application/libc heaps. The documentation explains their different controls and ownership instead of treating memory consumption as one undifferentiated limit.
- **C1:** Early release of bytecode storage requires checking whether the runtime still depends on it, and can remove access to custom sections. This is a concrete embedding lifetime constraint.

**Entry point:** [memory tuning and bytecode-buffer lifetime](https://github.com/wasm-micro-runtime/wasm-micro-runtime/blob/main/doc/memory_tune.md).

### 5. [wasm3/wasm3](https://github.com/wasm3/wasm3)

**C; compact interpreter using an internal operation representation.** The repository explicitly describes itself as being in a **minimal-maintenance phase**. It remains a substantive architecture study, particularly where generating native executable code is undesirable.

- **C3:** Wasm instructions become internal operations implemented as C functions with a common calling convention. Tail-call dispatch, fused operations, and virtual registers reduce repeated decoding and stack traffic without a conventional native-code JIT.
- **C1:** Trap propagation and control flow must cooperate with the native call stack. The interpreter design explains why loops need stack unwinding and why flattened control transfers complicate exception-handler bookkeeping.

**Entry point:** [interpreter implementation notes](https://github.com/wasm3/wasm3/blob/main/docs/Interpreter.md). Read this alongside the maintenance notice on the repository page when considering adoption.

### 6. [wasmi-labs/wasmi](https://github.com/wasmi-labs/wasmi)

**Rust; embeddable interpreter with fuel accounting and resumable execution.** Use the current `wasmi-labs` repository, rather than treating its former organization as a separate implementation. The engine is a useful study in controlling execution while maintaining Rust-facing ownership boundaries.

- **C1:** Engine-associated identities, resumable host traps, and out-of-fuel states make execution continuation an explicit part of the design. Official WAST tests and differential fuzzing against other engines supplement translation tests.
- **C3:** The engine reuses validation and translation allocations and supports lazy function preparation. Its development guide distinguishes translation, execution, instantiation, and fueled/lazy benchmarks, making the relevant cost centers visible.

**Entry points:** [engine implementation](https://github.com/wasmi-labs/wasmi/blob/main/crates/wasmi/src/engine/mod.rs) and the [development/testing guide](https://github.com/wasmi-labs/wasmi/blob/main/docs/developement.md). The spelling of the latter filename is intentional.

### 7. [wazero/wazero](https://github.com/wazero/wazero)

**Go; runtime with an interpreter and native compilation, without requiring CGO.** The canonical GitHub repository is now under `wazero`; older `tetratelabs` references and the established Go import path should not be counted as another project.

- **C3:** The `wazevo` compiler separates Wasm frontend processing, SSA representation, and machine-code backend work. Compiled-code caching and reusable trampolines address compilation and repeated host/runtime transition costs.
- **C1:** The engine implementation combines synchronized compiled-module maps, executable-address lookup, and reference counts. Shared trampolines handle memory growth, stack growth, and atomic waits/notifications, exposing the lifetime and transition machinery behind the public API.

**Entry points:** the [wazevo compiler directory](https://github.com/wazero/wazero/tree/main/internal/engine/wazevo) and its [engine implementation](https://github.com/wazero/wazero/blob/main/internal/engine/wazevo/engine.go). These internals are especially useful for studying native compilation implemented in Go.

### 8. [dylibso/chicory](https://github.com/dylibso/chicory)

**Java; JVM-native Wasm execution through interpretation and compilation to JVM bytecode.** This provides a different implementation family from engines that allocate native machine code or require a JNI runtime.

- **C1:** A valid Wasm function can exceed the JVM's method-size limit after translation. Chicory makes interpreter fallback configurable, including warning, silent fallback, and failure modes, rather than assuming every valid function can become one JVM method.
- **C3:** Eager runtime compilation trades initialization cost for later execution speed; build-time compilation moves that work earlier. A machine factory lets compiled and interpreted execution fit the same instance construction model.

**Entry point:** the [runtime compiler guide](https://chicory.dev/docs/usage/runtime-compiler/), including compilation timing, method-size fallback, and test coverage. The compiler has its own dependencies, so the runtime's portability should not be confused with every configuration being dependency-free.

### 9. [yamt/toywasm](https://github.com/yamt/toywasm)

**C11; direct bytecode interpreter with carefully documented implementation tradeoffs.** Despite the name, this is a substantive execution-engine study. Its documentation explicitly makes stable API/ABI compatibility a non-goal; version numbers should not be interpreted as a semantic-versioning promise.

- **C3:** Validation-time annotations supply jump destinations, local offsets, and information otherwise expensive to recover during execution. The design compares additional metadata against repeated decoding while keeping the original Wasm bytes read-only.
- **C1:** Interrupt checks and restartable errors allow execution to unwind to the embedder and resume later. Host I/O, long waits, sibling-thread exit, and nested invocation make this substantially more difficult than periodically decrementing a counter.

**Entry points:** [execution annotations](https://github.com/yamt/toywasm/blob/master/doc/annotations.md) and [interrupt/restart design](https://github.com/yamt/toywasm/blob/master/doc/check_interrupt.md).

### 10. [WAVM/WAVM](https://github.com/WAVM/WAVM)

**C++; LLVM-based JIT runtime and supporting libraries.** Study the boundaries between Wasm representation, compilation, runtime objects, operating-system facilities, and host interfaces. This is a host-oriented implementation with architectural assumptions such as a 64-bit address space.

- **C2:** Separate libraries cover IR and validation, binary/text formats, LLVM compilation, runtime services, WASI, virtual filesystems, and object caching. The organization guide makes these dependencies discoverable.
- **C3:** Virtual-memory facilities and fault handling participate in memory-access enforcement, while an object cache avoids repeated compilation. These connect performance decisions to identifiable runtime/platform components.
- **C1:** The test organization includes specification tests, fuzzing, and proposal-specific cases such as threading and memory variants, reflecting the semantic surface those components must preserve.

**Entry point:** [code organization and testing layout](https://github.com/WAVM/WAVM/blob/master/Doc/CodeOrganization.md), read with the repository's platform and security limitations. No current maintenance cadence is inferred here.

### 11. [v8/v8](https://github.com/v8/v8)

**C++; WebAssembly subsystem inside the V8 JavaScript/Wasm engine.** This is the project's **official GitHub mirror**; upstream development also uses Chromium infrastructure. The selected subject is Wasm compilation and execution, not the whole JavaScript engine.

- **C3:** The documented pipeline uses a low-latency baseline tier and background optimization of hot functions. Streaming, lazy compilation, and compiled-code caching address different parts of startup and steady-state cost.
- **C1:** Tier transitions must account for already-running calls and debugging. The guide explains that new calls can use optimized code while an existing invocation finishes in its original tier, and that debugging can require tier-down behavior.

**Entry point:** the [WebAssembly compilation pipeline guide](https://v8.dev/docs/wasm-compilation-pipeline). This describes architectural mechanisms; compiler names, flags, and Chrome-specific caching policies are version-sensitive and should be checked against the revision being studied.

## Binary processing, optimization, and interface generation

### 12. [WebAssembly/binaryen](https://github.com/WebAssembly/binaryen)

**C++; optimization and code-generation infrastructure, including `wasm-opt`.** Its tree-oriented intermediate representation is deliberately different from the binary format's stack machine, making it a useful example of choosing an IR for transformations.

- **C2:** A shared IR, pass framework, and C/JavaScript interfaces support compiler backends and post-link optimization. Explicit handling of unreachable expressions and other IR properties lets passes work above byte-level encoding details.
- **C1:** Fuzzing constructs valid modules from arbitrary input, varies transformations, and compares execution before and after optimization. Reduction then seeks a smaller input preserving the observed failure, providing a practical workflow for semantic miscompilations.

**Entry points:** the repository's [IR and infrastructure documentation](https://github.com/WebAssembly/binaryen#binaryen-ir) and [fuzzing guide](https://github.com/WebAssembly/binaryen/wiki/Fuzzing). The latter explains testing mechanisms rather than relying on benchmark reputation.

### 13. [WebAssembly/wabt](https://github.com/WebAssembly/wabt)

**C++; parsing, validation, text/binary conversion, interpretation, and Wasm-to-C tools.** WABT emphasizes faithful representation of Wasm rather than serving as a broad optimizing IR. Its `wasm2c` subsystem is particularly instructive.

- **C2:** Related command-line tools share infrastructure for reading, validating, displaying, and translating modules. This supports language implementers, debugging tools, and test harnesses around the same format semantics.
- **C1:** Translating Wasm to C requires preserving traps, function-reference types, memory behavior, and floating-point details despite C compiler assumptions. The `wasm2c` documentation calls out compiler options affecting NaNs and recursion/stack-overflow behavior and explains generated instance and runtime interfaces.

**Entry point:** the [wasm2c implementation and runtime guide](https://github.com/WebAssembly/wabt/blob/main/wasm2c/README.md). `wasm2c` is counted within WABT, not as a separate repository.

### 14. [bytecodealliance/wasm-tools](https://github.com/bytecodealliance/wasm-tools)

**Rust; a monorepo of reusable Wasm and component-model libraries plus command-line tools.** Its parser, encoder, text tooling, WIT/component utilities, and fuzzing-related crates form infrastructure used by other toolchains.

- **C1:** Incremental parsing distinguishes incomplete input from malformed input at EOF, reports consumed bytes, and lends payloads backed by the caller's buffer. Nested components/modules require parser-stack handling. Parsing a section header does not mean its contents have been fully validated.
- **C2:** Parsing, validation, encoding, printing, component processing, and test-input construction are exposed as libraries as well as CLI operations. Applications can assemble only the stages they need.

**Entry point:** the [`wasmparser::Parser` API and examples](https://docs.rs/wasmparser/latest/wasmparser/struct.Parser.html), especially incremental input and nested parsing. All in-repository crates count as one project here.

### 15. [wasm-bindgen/walrus](https://github.com/wasm-bindgen/walrus)

**Rust; structured Wasm transformation library.** The current canonical repository is under `wasm-bindgen`, replacing older `rustwasm` references. It is useful for engineers building instrumentation, rewriting, or other module-to-module tooling.

- **C2:** Module and function builders, instruction structures, and transformation-oriented APIs let clients operate on a module model instead of manually rewriting binary offsets and section indexes.
- **C1:** Internal entity identities must be mapped back to emitted Wasm indexes. Recursive GC type groups introduce forward references and subtype relationships; the API provides group construction that allocates identities before all referenced definitions are available.

**Entry point:** the [library API](https://docs.rs/walrus/latest/walrus/), particularly `ModuleTypes`, recursive groups, instruction builders, and identity/index mapping. These are concrete graph-rewriting concerns, rather than evidence that every possible transformation preserves semantics automatically.

### 16. [wasm-bindgen/wasm-bindgen](https://github.com/wasm-bindgen/wasm-bindgen)

**Rust and JavaScript/TypeScript; interoperation generator and Wasm post-processing toolchain.** Study how source-level annotations, compiler-produced metadata, generated JavaScript, and binary transformation cooperate to expose richer interfaces than Wasm's basic value types.

- **C2:** The design separates a Rust macro frontend, runtime support, Wasm processing, and JavaScript glue generation. This reusable pipeline handles strings, objects, and application-defined interfaces instead of requiring hand-maintained wrappers for each function.
- **C1:** Its documented JavaScript-object handle design distinguishes temporary borrows from owned values. Stack cleanup, slab entries, Rust `Drop`, and suppressed destruction for borrowed handles must agree across a language boundary.

**Entry points:** [overall design](https://wasm-bindgen.github.io/wasm-bindgen/contributing/design/index.html) and [JavaScript objects in Rust](https://wasm-bindgen.github.io/wasm-bindgen/contributing/design/js-objects-in-rust.html). The latter documents the object-handle/polyfill design; it should not be read as claiming that every modern configuration uses that exact representation.

### 17. [bytecodealliance/wit-bindgen](https://github.com/bytecodealliance/wit-bindgen)

**Rust implementation; multi-language bindings generator for WIT and the Component Model.** This is the generator and ABI adaptation machinery, not merely a repository of generated wrappers.

- **C2:** WIT worlds, interfaces, and structured types become guest-language APIs through shared generation infrastructure. The C backend illustrates how a reusable interface description produces declarations, implementation glue, and component type information.
- **C1:** Lists, strings, nested allocations, and resource handles need direction-dependent ownership rules. Imported and exported functions differ in who allocates and frees arguments/results; generated post-return cleanup and owned versus borrowed resources make those rules executable.

**Entry point:** the [C generator's ABI and memory-management guide](https://github.com/bytecodealliance/wit-bindgen/blob/main/crates/c/README.md). The ownership examples are particularly valuable for understanding what convenient component interfaces hide from application code.

### 18. [turbolent/w2c2](https://github.com/turbolent/w2c2)

**C; portable Wasm-to-C translation, including older compilers and unusual targets.** The project describes inspiration from WABT's `wasm2c`, but has its own implementation and portability approach. It provides a distinct example of AOT deployment through a widely available C compiler.

- **C3:** Streaming translation and splitting generated code into multiple files address translator memory use and downstream compilation cost. This architecture is relevant where modern JIT infrastructure or large compilation processes are impractical.
- **C1:** Wasm's fixed-width, little-endian value model must survive host variation. The runtime support header explicitly detects endianness, selects byte-swapping implementations, and accommodates differing compiler/type facilities, including older toolchains.

**Entry points:** the [translator source directory](https://github.com/turbolent/w2c2/tree/main/w2c2) and [portable runtime support header](https://github.com/turbolent/w2c2/blob/main/w2c2/w2c2_base.h). Portability mechanisms are the evidence; no uniform performance claim across those targets is implied.

## Language toolchains, linking, and system interfaces

### 19. [emscripten-core/emscripten](https://github.com/emscripten-core/emscripten)

**Python, JavaScript, and C/C++; C/C++-to-WebAssembly toolchain and browser-facing runtime support.** Particularly useful for studying how existing native programming models are adapted to an asynchronous browser environment.

- **C1:** POSIX-style thread behavior collides with browser constraints: blocking the main thread can deadlock work proxied from a worker, and worker creation is asynchronous. The pthread guide explains proxying and pre-created pools as concrete responses.
- **C2:** The compiler driver and reusable runtime facilities package browser, libc, filesystem, and threading integration for many native applications.
- **C4:** The changelog records multi-year backend migrations, ABI changes, deprecations, regression fixes, and test-gated release tags. Its explicit lack of a general ABI guarantee and cache/rebuild rules are evidence of managing compatibility boundaries, not evidence that compatibility never breaks.

**Entry points:** [pthreads and browser concurrency](https://emscripten.org/docs/porting/pthreads.html) and the [changelog](https://github.com/emscripten-core/emscripten/blob/main/ChangeLog.md), including the 2020 backend transition and later release policies.

### 20. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**C++; WebAssembly code-generation backend and LLD's WebAssembly linker within the LLVM monorepo.** The selected subsystem demonstrates why linking Wasm is more than reproducing an ELF linker with a different file encoder.

- **C1:** Wasm's function-type requirements expose mismatches that native linking may tolerate. LLD documents errors or trapping stubs for incompatible signatures, constraints on undefined imports, and relocation behavior needed to produce valid modules.
- **C3:** Section garbage collection follows reachability from exported and entry symbols. Compressing padded LEB relocations can reduce output, but changes code offsets and conflicts with debug-information expectations. The linker makes that size/debugging tradeoff explicit.
- **C2:** The backend and linker are reusable stages for multiple source-language frontends and build systems.

**Entry point:** [LLD's WebAssembly linker design and options](https://lld.llvm.org/WebAssembly.html). LLVM and LLD are counted once, rather than inflating the list with monorepo subprojects.

### 21. [AssemblyScript/assemblyscript](https://github.com/AssemblyScript/assemblyscript)

**TypeScript/AssemblyScript; compiler and managed runtime for a TypeScript-like language targeting Wasm.** Its runtime makes the tradeoffs behind managed objects in linear memory accessible without requiring a full browser-engine codebase.

- **C1:** Object headers, runtime type identities, and host-held references form an explicit memory contract. Objects referenced outside Wasm may require pinning across allocations; pin/unpin discipline is necessary for the collector to distinguish live objects from unreachable ones.
- **C3:** Runtime variants choose between an incremental collector with allocator support, a smaller explicitly collected configuration, and a stub allocator that never frees. These are different application-lifetime and footprint tradeoffs, not interchangeable defaults.

**Entry point:** [runtime variants, object layout, and memory interface](https://www.assemblyscript.org/runtime.html). AssemblyScript is not presented here as a compiler for arbitrary existing TypeScript programs.

### 22. [tinygo-org/tinygo](https://github.com/tinygo-org/tinygo)

**Go, with LLVM integration; compiler and runtime targeting Wasm/WASI and embedded systems.** The relevant subject is its Wasm-capable compilation pipeline and supporting runtime, viewed in the context of a compiler that also targets constrained native devices.

- **C2:** Parsing and type checking feed Go SSA, followed by LLVM lowering and runtime support for language features such as interfaces and goroutines. That layered organization supports different host and target environments without a separate language frontend for each.
- **C3:** Compile-time interpretation of global initialization, escape/string analysis, and staged interface lowering reduce runtime work or generated code while preserving higher-level Go constructs. The pipeline guide identifies where these transformations belong.

**Entry points:** [compiler pipeline](https://tinygo.org/docs/concepts/compiler-internals/pipeline/) and [WASI compilation guide](https://tinygo.org/docs/guides/webassembly/wasi/). The latter verifies the category fit; the former supplies the implementation substance.

### 23. [WebAssembly/wasi-libc](https://github.com/WebAssembly/wasi-libc)

**C; libc implementation and sysroot support for Wasm programs using WASI.** This is a system-interface/toolchain component rather than an execution engine. It is valuable for understanding where familiar C APIs meet capability-oriented host interfaces.

- **C2:** The library separates higher-level libc functionality from a lower layer implementing operations through WASI. That boundary lets reusable C interfaces sit above host-specific system-call adaptation.
- **C1:** Filesystem paths must resolve through preopened directory capabilities and relative operations. Thread support also depends on the target: the repository documents failure or trap behavior where ordinary blocking/thread-creation semantics cannot be supplied, instead of silently treating all WASI environments as POSIX.

**Entry points:** [bottom-half implementation and preopen handling](https://github.com/WebAssembly/wasi-libc/tree/main/libc-bottom-half) and the repository's [target and threading documentation](https://github.com/WebAssembly/wasi-libc#readme). Proposal and target support should be checked for the exact sysroot version being deployed.

### 24. [bytecodealliance/javy](https://github.com/bytecodealliance/javy)

**Rust, with the QuickJS C engine; JavaScript-to-Wasm packaging and execution toolchain.** Javy combines a JavaScript runtime with generated Wasm modules; it should not be confused with an optimizing compiler that translates all JavaScript operations directly into Wasm instructions.

- **C2:** The architecture separates the CLI, code generator, configurable JavaScript runtime, plugin API, and plugin implementation. Embedders can customize runtime behavior while reusing the surrounding generation and invocation machinery.
- **C3:** Static embedding and dynamic plugin linking expose different artifact-size and deployment tradeoffs. Runtime feature gates also affect produced module size; plugin processing and initialization make those choices part of an identifiable pipeline.

**Entry point:** [architecture and crate relationships](https://github.com/bytecodealliance/javy/blob/main/docs/docs-contributing-architecture.md). This is especially useful for studying language-runtime packaging and extension contracts rather than native-code optimization.

## Executable specification and conformance infrastructure

### 25. [WebAssembly/spec](https://github.com/WebAssembly/spec)

**OCaml, specification sources, and WAST tests; reference interpreter and language specification.** The reference interpreter intentionally favors clarity over production execution speed. That makes it complementary to the resource-constrained and optimizing engines above.

- **C1:** Syntax, validation, runtime structures, and evaluation are separated to correspond to the specification. Malformed modules, type validity, and execution traps are distinct semantic concerns rather than one generic loading failure.
- **C2:** Text/binary processing and a script runner support execution, assertions, and test conversion. This supplies reusable conformance infrastructure for engine and toolchain implementers, alongside an executable explanation of the language.

**Entry point:** the [reference interpreter directory and implementation guide](https://github.com/WebAssembly/spec/tree/main/interpreter), especially its implementation organization and script commands. It is retained for semantic and testing architecture, not as a performance-oriented deployment runtime.

## Search coverage, exclusions, and limits

Discovery used more than six distinct live-web query formulations. Search angles included standalone JIT/AOT architecture; embedded and small interpreters; pure-Go and JVM implementations; C#/Swift/OCaml alternatives; binary validators and optimizer fuzzing; Wasm-to-C translation and older targets; language compilers for Go, JavaScript, and AssemblyScript; component/WIT binding generation; WASI libraries; and historical runtimes. Follow-up searches targeted compiler pipelines, memory management, interrupt handling, ownership, and release/change documentation. Additional queries increasingly returned already-covered families, application frameworks, wrappers, or projects for which equally substantive primary evidence was not established.

Every retained repository's canonical GitHub page was opened, and at least one additional primary implementation or documentation source was read. Reading the root README again through a raw URL was not counted as additional evidence. Several ownership moves were resolved to current canonical repositories. V8 is explicitly labeled an official mirror. The entries identify reusable subsystems inside monorepos instead of counting their constituent tools or crates separately.

The selection includes less prominent architecture studies such as toywasm and w2c2, alongside widely deployed infrastructure. Application platforms, browser applications, generated bindings alone, tutorials, awesome-lists, and thin runtime wrappers were excluded from scope. [Lucet](https://github.com/bytecodealliance/lucet) was inspected but excluded from the main list because its official repository declares end of life and directs users to Wasmtime. wasm3 is retained with its explicit minimal-maintenance warning because its interpreter architecture remains a distinct study subject. No fork is counted solely for sharing an upstream implementation.

This is not an exhaustive survey of browser engines or every .NET, Swift, Zig, and research runtime. Inclusion indicates that the cited material supports the stated criteria; conclusions about what an engineer can learn are grounded assessments, not an independent correctness or security audit. Maintenance status is stated only where checked explicitly, and C4 is assigned only where longitudinal change-management evidence was inspected. No candidate code was cloned, installed, built, or executed; there are no independently measured performance claims. Documentation and default-branch source links can evolve, so implementation and proposal details should be rechecked against a chosen release.
