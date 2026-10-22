# Foreign function interfaces and language binding generators

Research date: 2026-10-09

This report selects 29 GitHub repositories for studying reusable machinery that crosses language boundaries: machine-level calling conventions, dynamic foreign calls, generated wrappers, ownership-aware bridges, and WebAssembly bindings. It includes libraries and generators rather than individual generated API wrappers. The larger selection preserves coverage of Perl, Common Lisp, OCaml, Haskell, Fortran, R, Ruby, Dart, JVM, .NET, Python, JavaScript, Lua, and BEAM communities alongside Rust and C/C++.

The criteria below are evidence-based reasons to investigate a codebase, not a claim that every component is exemplary or that using it makes arbitrary native code safe. Descriptions of what an engineer can learn are grounded judgments from the cited implementation and documentation. Inclusion does not, by itself, assert an active maintenance commitment.

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstraction:** substantial reusable machinery serving multiple applications or interface shapes.
- **C3 — Performance:** concrete performance constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development with evidence of compatibility work, testing, or complexity management; age alone does not qualify.

## ABI machinery and dynamic foreign calls

### 1. [libffi/libffi](https://github.com/libffi/libffi)

**Language/role:** C and assembly; portable runtime invocation and callback machinery at the machine ABI layer.

Study how one call-interface description becomes architecture-specific register and stack operations. This is foundational machinery below language-specific object conversion, rather than a complete binding generator.

- **C1:** The x86-64 implementation classifies argument chunks, merges integer/SSE/x87 classes, and decides when values require memory passing. These rules make aggregate layout and mixed numeric arguments particularly instructive. Start with [the x86-64 implementation](https://github.com/libffi/libffi/blob/master/src/x86/ffi64.c).
- **C2:** The common call-interface abstraction supports runtime-selected signatures across many ABIs, allowing interpreters and other binding systems to reuse the same low-level engine. The [repository overview](https://github.com/libffi/libffi#what-is-libffi) explicitly distinguishes this layer from higher-level conversions.
- **C4:** The [documented release history](https://github.com/libffi/libffi#history) spans 2014–2026 with concrete compatibility fixes for struct returns, stack alignment, floating-point formats, closures, and new architectures; it also documents platform testing and DejaGNU checks.

### 2. [python-cffi/cffi](https://github.com/python-cffi/cffi)

**Language/role:** Python and C; C declarations, foreign objects, and calls exposed to Python.

Study the distinction between a Python object that owns native storage and a Python object that merely points into it. The repository is the project's verified GitHub source home; older references to other hosting should not be used to identify the current repository.

- **C1:** The [usage guide](https://cffi.readthedocs.io/en/latest/using.html) explains dangling allocations, nested `ffi.new` mistakes, pointer/struct co-ownership, and why storing a pointer does not automatically retain its allocation. These are precise cross-GC/native-lifetime failure modes.
- **C2:** The same `cdata` model supports pointers, arrays, structs, unions, casts, and foreign function arguments, giving many C APIs a common representation. The guide's allocation and conversion examples are useful entry points; [the repository](https://github.com/python-cffi/cffi) also identifies separate C-backend and Python-level test suites.

### 3. [java-native-access/jna](https://github.com/java-native-access/jna)

**Language/role:** Java and C; dynamic access to native shared libraries through Java interface declarations.

Study how a reusable JNI dispatch layer removes the need for application-specific JNI glue, while still exposing the lifetime obligations that Java's collector cannot infer.

- **C1:** The [callback documentation](https://github.com/java-native-access/jna/blob/master/www/CallbacksAndClosures.md) describes native calls into collected Java callbacks, platform-specific callback calling conventions, and automatic proxies for function pointers inside native structs. Callback reachability is a real crash boundary.
- **C2:** Java interfaces describe native functions and structures, while a small shared JNI stub performs invocation. The [repository's architecture overview](https://github.com/java-native-access/jna#java-native-access-jna) explains this reusable split. It expressly prioritizes correctness and ease of use over performance, so no universal speed claim is implied here.

### 4. [jnr/jnr-ffi](https://github.com/jnr/jnr-ffi)

**Language/role:** Java; native-library interfaces backed by generated JVM classes and JFFI calls.

Study runtime code generation as an alternative to a single generic reflective invocation path. The implementation separates interface scanning, type mapping, calling conventions, and method generators.

- **C1:** [AsmLibraryLoader](https://github.com/jnr/jnr-ffi/blob/master/src/main/java/jnr/ffi/provider/jffi/AsmLibraryLoader.java) handles recursive class-loader use, variadic invocation, error preservation, symbol lookup failures, and mapped parameter/result types. Its failure stubs and cleanup paths are concrete study targets.
- **C2:** Function mappers, signature type mappers, native variables, and generated interface implementations support different native APIs through shared machinery in that loader.
- **C3:** The loader selects a compatible method generator and emits JVM bytecode for the binding. This is inspectable specialization of the call path, not evidence for an unqualified benchmark ranking.

### 5. [ffi/ffi](https://github.com/ffi/ffi)

**Language/role:** Ruby and C; Ruby foreign-function declarations, memory access, and callbacks.

Study a dynamic-language interface whose hard problems include entering Ruby from native threads, not just translating arguments.

- **C1:** The [callback architecture notes](https://github.com/ffi/ffi/wiki/Callbacks) distinguish callbacks when the caller already holds the GVL, callbacks from Ruby-owned threads without the lock, and callbacks from foreign threads. They spell out the different acquisition and dispatch paths.
- **C2:** `FFI::Library`, attached functions, function pointers, and Ruby `Proc` callbacks form a reusable bidirectional interface rather than a wrapper for one library. The same notes show both native and Ruby callback representations.
- **C3:** The documented `blocking: true` path releases the GVL around a native call and reacquires it for conversion, allowing other Ruby threads to progress during expensive or blocking foreign work. This is a concrete concurrency/performance tradeoff.

### 6. [cffi/cffi](https://github.com/cffi/cffi)

**Language/role:** Common Lisp; portable foreign interfaces across Lisp implementations. This is distinct from Python CFFI above.

Study a portability boundary with implementation-specific backends and a declarative frontend, plus extensible conversion protocols.

- **C1:** [Foreign type translators](https://cffi.common-lisp.dev/manual/html_node/Foreign-Type-Translators.html) pair allocation with `free-translated-object`, document the leak when cleanup is omitted, and show validation of non-null pointer arguments.
- **C2:** The [repository's architecture description](https://github.com/cffi/cffi#how) separates `CFFI-SYS` from portable `CFFI`, while specialized generic functions implement conversion policy. Struct-by-value support and header-derived bindings fit around this shared frontend rather than replacing it.

### 7. [yallop/ocaml-ctypes](https://github.com/yallop/ocaml-ctypes)

**Language/role:** OCaml and C; typed C interfaces usable through dynamic calls or generated stubs.

Study how one typed binding description can support different execution and concurrency strategies.

- **C1:** [The foreign-call interface](https://github.com/yallop/ocaml-ctypes/blob/HEAD/src/ctypes-foreign/foreign.mli) documents restrictions on heap access and callbacks when releasing the runtime lock, callback collection, and explicit function-pointer lifetimes. It also notes that successful C functions may change `errno`, preventing a simplistic error interpretation.
- **C2:** [The stub-generation interface](https://github.com/yallop/ocaml-ctypes/blob/HEAD/src/cstubs/cstubs.mli) abstracts bindings as functors and exposes reusable errno and concurrency policies, including sequential calls, unlocked calls, and Lwt integration. The policies can change the generated OCaml result type in a systematic way.

### 8. [PerlFFI/FFI-Platypus](https://github.com/PerlFFI/FFI-Platypus)

**Language/role:** Perl and native extension code; libffi-based calls and callbacks without application-specific XS bindings.

Study how a language-facing API adds type policy, symbol lookup, and closure retention above a general ABI engine.

- **C1:** [Closure.pm](https://github.com/PerlFFI/FFI-Platypus/blob/HEAD/lib/FFI/Platypus/Closure.pm) explains that a callback must remain reachable while compiled code may call it, and implements explicit sticky/unstick lifetime control. Letting the closure disappear is documented as a native crash risk.
- **C2:** [The repository's API documentation](https://github.com/PerlFFI/FFI-Platypus) provides per-instance type definitions, dynamically callable functions, attached Perl subs, and language plugins. Its selectable API levels also show a compatibility mechanism for changing null-pointer and array-argument behavior without silently changing legacy callers.

## Header-driven and interface-definition generators

### 9. [swig/swig](https://github.com/swig/swig)

**Language/role:** C/C++ generator and language-specific support code; C/C++ interfaces exposed to many target languages.

Study a generator where marshalling is a programmable subsystem. The interesting architecture is the interaction between a C++ type model, target-language modules, and reusable conversion rules.

- **C1:** [The typemap manual](https://www.swig.org/Doc4.3/Typemaps.html) covers input validation, overload type checks, temporary-argument cleanup, returned-object cleanup, and exceptions. Correct generation requires these stages to agree, especially for multi-argument conversions such as pointer/length pairs.
- **C2:** Typemap matching follows underlying types through typedefs and namespaces; `%apply` reuses families of rules. The same manual provides substantive implementation-level examples of code insertion and special-variable expansion, making it a useful starting point for extending a generator backend.

### 10. [mono/CppSharp](https://github.com/mono/CppSharp)

**Language/role:** C# and C++; Clang-based generation of managed bindings for native C/C++ APIs.

Study a compiler-style pipeline with an AST, transformation passes, type maps, and multiple output backends.

- **C1:** [The user manual](https://github.com/mono/CppSharp/blob/main/docs/UsersManual.md) addresses platform-dependent integer widths, signedness, `wchar_t` encoding, delegates for function pointers, and native/managed allocation differences. These details make faithful .NET bindings more difficult than renaming declarations.
- **C2:** The [repository architecture](https://github.com/mono/CppSharp#libraries) separates the Clang parser, managed AST, and generator. The manual connects specific transformations to passes such as `DelegatesPass` and explains configurable mappings; these are reusable extension points for different native APIs.

### 11. [Snapchat/djinni](https://github.com/Snapchat/djinni)

**Language/role:** Scala generator with C++/JNI and Objective-C++ support; shared interface definitions for mobile/native components.

This is the documented successor to Dropbox's implementation. Its [repository history and modifications](https://github.com/Snapchat/djinni#modifications) describe substantive changes, including removal of proxy finalizers, move support, and additional data-passing types. Dropbox's archived repository is not counted separately.

- **C1:** [JNI support types](https://github.com/Snapchat/djinni/blob/HEAD/support-lib/jni/djinni_support.hpp) implement distinct `GlobalRef` and `LocalRef` ownership wrappers using custom deleters. They also restrict conversion of temporary local-reference wrappers, exposing the importance of reference lifetime in generated bridges.
- **C2:** [The inherited interface guide](https://github.com/Snapchat/djinni/blob/main/README.dropbox.md) explains how enums, records, and bidirectional interfaces map across C++, Java, and Objective-C. This is useful for studying a deliberately constrained common object model rather than arbitrary C++ parsing.

### 12. [llnl/shroud](https://github.com/llnl/shroud)

**Language/role:** Python generator; C and C++ APIs wrapped for Fortran, Python, and C.

Study a scientific-computing generator that asks users for semantic annotations absent from declarations. YAML input combines the API with generation policy, producing readable wrapper code without a separate Shroud runtime library.

- **C1:** [The type-conversion documentation](https://shroud.readthedocs.io/en/develop/types.html) explains conversion between Fortran `logical` and `logical(C_BOOL)`, when a result requires an extra wrapper, numeric-kind casts, and explicit string lengths. These language-representation mismatches are concrete correctness problems.
- **C2:** Type maps and pre/post-call statement templates share conversion machinery across generated C, Fortran, and Python layers. The same guide shows how declarative fields select interface types, local variables, and generated conversion code; the [repository example](https://github.com/llnl/shroud#example) demonstrates retaining a C++ object's methods in both target languages.

### 13. [haskell/c2hs](https://github.com/haskell/c2hs)

**Language/role:** Haskell; C-header analysis and hooks embedded in Haskell binding templates.

Study a generator that combines discovered C signatures with explicit Haskell marshalling choices, instead of attempting to infer every high-level semantic decision.

- **C1:** [The user-guide source](https://github.com/haskell/c2hs/blob/HEAD/doc/c2hs.xml) describes pointer hooks, distinct pointer `newtype`s, `ForeignPtr`/`StablePtr` mappings, and generated `withObject` marshalling. Keeping pointer types distinct helps detect swapped or incompatible pointer arguments.
- **C2:** Function, pointer, type, and import hooks provide reusable binding construction. [The import-handling design note](https://github.com/haskell/c2hs/blob/master/import-handling.md) explains generated qualified imports, why implementation changes previously broke clients, and regression checks against real downstream packages. This is particularly useful for studying compatibility-sensitive code generation.

### 14. [dart-lang/native](https://github.com/dart-lang/native)

**Language/role:** Dart-centric monorepo; this entry focuses on **`pkgs/ffigen`**, with adjacent JNI and Objective-C support packages counted only as context.

Study how libclang parsing, a generator AST, dependency analysis, and user visitors cooperate. The former standalone `dart-archive/ffigen` repository points here and is not a second entry.

- **C1:** [The opaque-compound visitor](https://github.com/dart-lang/native/blob/HEAD/pkgs/ffigen/lib/src/visitor/opaque_compounds.dart) distinguishes compounds required by value from those referenced only through pointers. It makes dependencies opaque only under explicit conditions, preserving the information needed for by-value representation.
- **C2:** [The parser pipeline](https://github.com/dart-lang/native/blob/HEAD/pkgs/ffigen/lib/src/header_parser/parser.dart) separates translation-unit parsing from binding transformations, including transitive dependencies, scopes, imports, method overrides, and variadic expansion. It also exposes source-diagnostic handling rather than silently treating erroneous headers as reliable input. This entry concerns the generator subsystem, not a blanket assessment of the monorepo.

## Rust-facing native bridges

### 15. [rust-lang/rust-bindgen](https://github.com/rust-lang/rust-bindgen)

**Language/role:** Rust using libclang; generation of Rust declarations and layouts from C and supported C++ headers.

Study a genuine compiler pipeline: Clang AST to an internal graph, fixed-point analyses, and Rust code generation.

- **C1:** [The contributor guide](https://github.com/rust-lang/rust-bindgen/blob/main/CONTRIBUTING.md) describes generated struct-layout tests, cross-language integration assertions, Csmith fuzzing, and property tests. It explicitly distinguishes comparing generated text from compiling and testing those bindings.
- **C2:** Its IR separates items, types, functions, layouts, and typed graph edges; analyses allocate bitfields and determine type properties before code generation. The guide's **Code Overview** is the best architectural entry point. These are low-level declarations; [the C++ guide](https://rust-lang.github.io/rust-bindgen/cpp.html) explains that constructors, destructors, and higher-level ergonomics can still require manual work.

### 16. [mozilla/cbindgen](https://github.com/mozilla/cbindgen)

**Language/role:** Rust; generation of C/C++ headers for Rust libraries exporting a C-compatible API.

Study the reverse direction from bindgen: discovering exported Rust items and the transitive types required to describe their ABI.

- **C1:** [The detailed guide](https://github.com/mozilla/cbindgen/blob/main/docs.md) distinguishes guaranteed layouts from opaque forward declarations, explains supported `repr` forms and tagged unions, and documents why wide pointers and anonymous tuples cannot simply become portable C declarations.
- **C2:** The traversal and shared type model support different output strategies: C monomorphization/mangling versus C++ templates, with CLI and library integration. The same guide candidly documents incomplete Rust namespace resolution and generic limitations, which are valuable boundaries to understand before extending or adopting the generator.

### 17. [dtolnay/cxx](https://github.com/dtolnay/cxx)

**Language/role:** Rust and C++; paired generators for an explicitly declared bidirectional boundary.

Study how restricting the supported boundary allows more static checking and direct use of native ownership types.

- **C1:** [The extern-C++ design](https://github.com/dtolnay/cxx/blob/HEAD/book/src/extern-c++.md) requires pinned mutable references for opaque C++ objects, avoids assuming `Send`/`Sync`, and separates signature verification from the programmer's safety claims about C++ behavior.
- **C2:** [The architecture overview](https://github.com/dtolnay/cxx#overview) describes coordinated Rust/C++ generation and static assertions, with reusable bindings for strings, vectors, boxes, and smart pointers.
- **C3:** The documented design avoids a general serialization layer at the boundary. The direct representation strategy is worth studying; it does not remove the need to audit unsafe C++ implementations.

### 18. [mozilla/uniffi-rs](https://github.com/mozilla/uniffi-rs)

**Language/role:** Rust generator/runtime with foreign-language backends; export of Rust component APIs through an object model.

Study a different tradeoff from CXX: a common C-style transfer layer mediates rich language-native values.

- **C1:** [RustBuffer's implementation](https://github.com/mozilla/uniffi-rs/blob/main/uniffi_core/src/ffi/rustbuffer.rs) specifies allocation provenance, `len <= capacity`, explicit destruction, empty-buffer handling, and why foreign-owned memory must not masquerade as a Rust allocation.
- **C2:** [Lifting, lowering, and serialization](https://github.com/mozilla/uniffi-rs/blob/main/docs/manual/src/internals/lifting_and_lowering.md) follows arguments and results through generated foreign code and Rust scaffolding. Primitive casts and serialized compound values form reusable conversion rules across multiple target-language backends. This also exposes where copying and serialization enter the architecture, without implying a universal performance ranking.

### 19. [rust-diplomat/diplomat](https://github.com/rust-diplomat/diplomat)

**Language/role:** Rust; annotated Rust APIs translated into C and higher-level language bindings.

Study how the same Rust lifetime information can produce different safeguards depending on the destination language.

- **C1:** [The lifetime guide](https://github.com/rust-diplomat/diplomat/blob/HEAD/book/src/lifetimes.md) explains an iterator that borrows its originating collection. JavaScript bindings retain the collection through additional references; C++ bindings document the lifetime requirement. These are deliberately different guarantees, not universal enforcement of Rust borrowing.
- **C2:** The [repository architecture and testing notes](https://github.com/rust-diplomat/diplomat#architecture) describe target-language plugins and snapshot testing of macro/code generation. Opaque and non-opaque types can share lifetime relationships, making the model reusable beyond one iterator example.

## Runtime-specific binding frameworks

### 20. [pybind/pybind11](https://github.com/pybind/pybind11)

**Language/role:** C++; template-based C++/Python binding library.

Study compile-time type discovery coupled to explicit policies for runtime ownership and conversion.

- **C1:** [Return-value and call policies](https://pybind11.readthedocs.io/en/stable/advanced/functions.html) distinguish copying, moving, ownership transfer, borrowed references, and `reference_internal`. The guide shows how a wrong policy can delete static storage or leave a dangling object, and explains how `keep_alive` ties related lifetimes together.
- **C2:** The [type-conversion overview](https://github.com/pybind/pybind11/blob/master/docs/advanced/cast/overview.rst) separates wrapped native C++ objects, C++ wrappers around Python objects, and converted values. Combined with reusable class/function binding machinery, this is a strong study of type-directed interoperation rather than a single extension module.

### 21. [wjakob/nanobind](https://github.com/wjakob/nanobind)

**Language/role:** C++; C++/Python bindings with a compiled support library and intentionally constrained scope.

Study how representation and build architecture affect binding overhead. This is a separate implementation with a documented redesign, not a duplicate pybind11 wrapper.

- **C1:** [The ownership guide](https://nanobind.readthedocs.io/en/latest/ownership.html) works through return-value policies, explicit unique ownership, shared ownership, and premature destruction across the language boundary.
- **C3:** [The design rationale](https://nanobind.readthedocs.io/en/latest/why.html) describes co-locating wrapper metadata, Python vector calls, a dispatch loop without heap allocation, and moving common implementation into `libnanobind` to avoid redundant compilation. These concrete mechanisms justify performance study without repeating numerical benchmark claims.
- **C2:** The ownership and binding abstractions apply to user classes, functions, and smart pointers; the documented scope restrictions are part of the design worth assessing.

### 22. [PyO3/pyo3](https://github.com/PyO3/pyo3)

**Language/role:** Rust; Python extension modules and embedding Python in Rust programs.

Study how Rust's type system represents Python object ownership and attachment to the interpreter.

- **C1:** [The object-type guide](https://pyo3.rs/main/types.html) distinguishes `Py<T>`, `Bound<'py, T>`, and borrowed references. It explains reference-count ownership, tying APIs to an interpreter lifetime, and why returned objects sometimes require explicit lifetime relationships.
- **C2:** These smart-pointer abstractions support both exported extension functions and Rust code interacting with Python objects, as demonstrated by [the repository's two integration directions](https://github.com/PyO3/pyo3#usage).
- **C3:** The guide identifies a specific tradeoff: lifetime-bound objects carry interpreter-attachment evidence, whereas unbound objects require runtime checks for some operations. This links API design to a concrete cost rather than a general claim that Rust bindings are faster.

### 23. [wlav/CPyCppyy](https://github.com/wlav/CPyCppyy)

**Language/role:** C++; CPython-facing runtime within cppyy's runtime-generated C++ binding system.

Study the actual conversion layer rather than counting cppyy's Python frontend and several dependent repositories as separate recommendations. Cling/JIT compilation lives elsewhere in the system; [the official package architecture](https://cppyy.readthedocs.io/en/latest/packages.html) explains that division.

- **C1:** [Converters.cxx](https://github.com/wlav/CPyCppyy/blob/HEAD/src/Converters.cxx) establishes Python reference “lifelines” for memory exposed to C++, including string and ctypes conversions. It makes the challenge of retaining backing objects visible in implementation code.
- **C2:** The same converter machinery handles parameter passing and memory reads/writes across Python and C++ representations, while the interpreter-specific layer is separated from the shared C++ backend. This is useful for studying a reusable dynamic binder with a different architecture from handwritten static template bindings.

### 24. [RcppCore/Rcpp](https://github.com/RcppCore/Rcpp)

**Language/role:** C++ and R; typed C++ access to R objects and reusable conversion/extension facilities.

Study how C++ object wrappers coexist with R's garbage collector, and how the wrapper model extends from vectors to functions and environments.

- **C1:** [PreserveStorage](https://github.com/RcppCore/Rcpp/blob/HEAD/inst/include/Rcpp/storage/PreserveStorage.h) manages preservation tokens through assignment, invalidation, copying, and destruction. It provides a compact example of coordinating RAII with a foreign collector instead of assuming a raw `SEXP` pointer is sufficient.
- **C2:** [The repository's architecture overview](https://github.com/RcppCore/Rcpp#synopsis) maps R's object variants to C++ classes and identifies extensible `wrap`/`as` conversions and modules. The generic storage policy and type-conversion layer serve many R packages rather than one numerical algorithm.

### 25. [ThePhD/sol2](https://github.com/ThePhD/sol2)

**Language/role:** C++; template-based C++/Lua binding and embedding library, including LuaJIT support.

Study the interaction between a stack-based VM API, C++ callable/type adaptation, and configurable checking.

- **C1:** [The safety configuration guide](https://sol2.readthedocs.io/en/latest/safety.html) covers argument checking, protected calls, numeric representability, float/integer overload distinction, and stack-position restrictions. Several safeguards require explicit configuration, which is essential context for interpreting its abstractions.
- **C2:** [The repository examples and overview](https://github.com/ThePhD/sol2) show reusable state, function, usertype, and member-binding interfaces. The safety guide explains how policy changes propagate through shared `stack::get`, call, and function abstractions rather than requiring application-specific conversions everywhere.

### 26. [rusterlium/rustler](https://github.com/rusterlium/rustler)

**Language/role:** Rust and Elixir integration; Rust implementations of Erlang NIFs for the BEAM.

Study a boundary where invalid native behavior can damage an entire VM, and where terms belong to particular environments.

- **C1:** [Env's implementation](https://github.com/rusterlium/rustler/blob/HEAD/rustler/src/env.rs) uses invariant lifetime markers to prevent automatic conversion between environments and documents VM-thread restrictions on message sending. The send path checks environment kind before invoking the native operation.
- **C2:** [The project overview](https://github.com/rusterlium/rustler#rustler) describes reusable term encoders/decoders, derived conversions, resource objects, and panic containment before unwinding into C. These mechanisms are the study target; the project's safety goal should not be read as proof that arbitrary unsafe NIF code cannot crash the VM.

### 27. [napi-rs/napi-rs](https://github.com/napi-rs/napi-rs)

**Language/role:** Rust and TypeScript tooling; generation and runtime support for Rust Node-API add-ons.

Study how a native binding framework connects Rust ownership and threads to JavaScript's runtime-affine values.

- **C1:** [ThreadsafeFunction documentation](https://napi.rs/docs/concepts/threadsafe-function) explains why native environment/value/reference handles cannot simply be accessed from another thread. Its ownership-based wrapper moves callback work through Node-API's thread-safe function mechanism, with explicit call modes and error behavior.
- **C2:** The same API supports typed payloads and callback results while integrating with `#[napi]` exports and generated TypeScript declarations. [The repository](https://github.com/napi-rs/napi-rs) supplies the surrounding reusable framework and build tooling; it is not merely a collection of generated declarations.

## WebAssembly language boundaries

### 28. [wasm-bindgen/wasm-bindgen](https://github.com/wasm-bindgen/wasm-bindgen)

**Language/role:** Rust and JavaScript; generated glue between Rust WebAssembly modules and JavaScript APIs.

Study coordinated macro expansion, Rust shims, and JavaScript wrappers. The verified canonical repository is under the `wasm-bindgen` organization.

- **C1:** [The exported-struct design](https://github.com/wasm-bindgen/wasm-bindgen/blob/HEAD/guide/src/contributing/design/exporting-rust-struct.md) shows pointer invalidation after freeing, null checks, and `WasmRefCell` borrow checks around methods and destruction. These protect Rust invariants when JavaScript initiates calls.
- **C2:** The same generated boundary model supports functions, objects, constructors, and methods rather than one application API.
- **C3:** [The reference-types explanation](https://github.com/wasm-bindgen/wasm-bindgen/blob/HEAD/guide/src/reference/reference-types.md) contrasts a JavaScript handle-table fallback with direct `externref` passing that removes glue. Its old browser-version notes should not be treated as current compatibility advice; the architectural comparison is the relevant evidence.

### 29. [bytecodealliance/wit-bindgen](https://github.com/bytecodealliance/wit-bindgen)

**Language/role:** Rust generator suite; guest-language bindings for WIT interfaces and the WebAssembly Component Model.

Study a language-independent lowering model shared by multiple code-generation backends. The repository focuses on guest bindings, not a general host runtime.

- **C1:** [The ABI instruction implementation](https://github.com/bytecodealliance/wit-bindgen/blob/HEAD/crates/core/src/abi.rs) specifies boolean validation, scalar loads/stores, list/string pointer-length conversion, ownership transfer, allocation, and responsibility for temporary cleanup. These are substantive canonical-ABI correctness obligations.
- **C2:** The same source represents conversion steps as instructions with explicit operand/result counts, allowing language backends to reuse the lowering model. [The repository guide](https://github.com/bytecodealliance/wit-bindgen#wit-as-an-idl) explains how WIT worlds and interfaces compose imports, exports, records, and other types. Its CLI stability caveat is part of the project's documented scope.

## Coverage, search method, and limitations

Discovery used more than six distinct formulations, including portable ABI/callback libraries; C/C++ header generators; Rust ownership-aware bridges; Python static versus runtime bindings; Java and Ruby dynamic FFIs; OCaml/Haskell/Common Lisp interfaces; BEAM and Node native extensions; WebAssembly component bindings; Fortran generators; Perl closures; and Dart/Swift/Zig interop. Representative live queries included `foreign function interface library GitHub libffi dyncall portable callbacks ABI`, `foreign function interface OCaml Haskell Common Lisp ctypes cffi GitHub`, `CppSharp C++ C# bindings generator GitHub architecture`, `site:github.com Rustler NAPI Rcpp sol2 foreign function interface`, `site:github.com Fortran C C++ Python binding generator shroud`, and `site:github.com Perl FFI Platypus closure native library`.

Later searches for ownership/callback mechanisms and generator alternatives increasingly returned already covered systems, individual library wrappers, or overlapping/newer generator families. The final Perl, Fortran, and Dart additions materially broadened the selection, which explains exceeding the approximate 15–25 guide. This is a bounded selection, not an exhaustive census: compiler-integrated FFIs, library sandboxing, and the full range of language-specific generators remain outside the detailed coverage.

Every retained repository's canonical URL was checked by opening its GitHub page or reading public GitHub repository metadata. Each also has independently opened implementation or detailed documentation evidence beyond its repository landing page. Some rendered pages failed, so the corresponding public raw source files were read instead. A later GitHub API quota limit affected redundant metadata checks; repository-page verification and raw-source reading remained available. Links using `HEAD` intentionally follow the repository's default revision and are not immutable snapshots.

Important exclusions and counting decisions:

- The discovered LWJGL copy of dyncall was not promoted to an independent upstream recommendation because an official substantive GitHub-mirror relationship was not established in this search.
- [Dropbox's Djinni repository](https://github.com/dropbox/djinni) is archived; only the substantively evolved Snapchat successor is counted. Other Djinni descendants are not counted again.
- [The archived standalone Dart ffigen repository](https://github.com/dart-archive/ffigen) moved into `dart-lang/native`; that monorepo appears once, with `pkgs/ffigen` identified explicitly.
- cppyy's split packages are not inflated into several entries: CPyCppyy is the selected implementation repository, with its external backend relationship stated.
- Tutorials, awesome-lists, benchmark-only comparisons, and generated wrappers for one library were not retained. Whole language/compiler repositories were generally excluded to keep the guide centered on reusable FFI and generator machinery.

No candidate code was run, dependencies installed, or repositories cloned. Test and performance descriptions report documented mechanisms, not independent execution results. Maintenance commitments and universal performance rankings were not inferred from stars, creation dates, or recent pushes.
