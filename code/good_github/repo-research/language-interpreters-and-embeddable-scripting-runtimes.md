# Language interpreters and embeddable scripting runtimes

Research date: **2026-10-09**

This selection covers 25 implementations of language interpreters and runtimes intended for embedding, including compact native VMs, ECMAScript engines, Python and Ruby implementations, Scheme systems, and interpreters integrated with Rust, Go, Java, and C++. Compiler components are included where they explain execution or embedding; standalone compiler frameworks, bindings around other engines, and application shells are outside the main scope. Each linked repository was opened, and each entry also draws on separately inspected implementation material or technical documentation. The criteria are evidence-based judgments about useful engineering study targets, not a claim that every component is exemplary or suitable for hostile code.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or components serving multiple embedding and language use cases.
- **C3 — Performance:** concrete execution or memory constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or explicit complexity management.

## Compact native runtimes and the Lua family

### [lua/lua](https://github.com/lua/lua)

**Language/role:** C; the Lua interpreter and embedding library. This repository is the official development mirror, updated irregularly; it should not be mistaken for the release-distribution workflow. Study how a small runtime exposes language mechanisms through a consistent C stack interface.

- **C1:** Integer overflow, equality between integer and floating-point table keys, finalizer resurrection, and weak-key ephemerons create interacting semantic and collector invariants. These are specified explicitly in the [Lua 5.4 reference manual](https://www.lua.org/manual/5.4/manual.html), particularly §§2.5 and 3.4.
- **C2:** Userdata, metatables, protected calls, coroutine operations, and stack-based argument/result exchange form a reusable embedding protocol rather than a collection of application-specific hooks. The same manual's C API documents ownership and error behavior at that boundary.

**Entry point:** [Lua 5.4 manual, language semantics and C API](https://www.lua.org/manual/5.4/manual.html). The version is intentional: these claims concern documented 5.4 behavior, not every development-tree change.

### [LuaJIT/LuaJIT](https://github.com/LuaJIT/LuaJIT)

**Language/role:** C and architecture-specific assembly; an independent Lua runtime with a tracing JIT and C FFI. The GitHub repository identifies itself as an official mirror. Its value as a study target is the connection between optimized execution and recoverable interpreter state.

- **C1:** Trace exits reconstruct values from constants, registers, and spill slots, including allocations eliminated inside a trace. Assertions and architecture-dependent cases make the reconstruction obligations visible in [snapshot implementation code](https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/lj_snap.c).
- **C3:** Snapshot construction omits unnecessary restoration work, while allocation sinking requires objects to be materialized again on exit. This is a concrete optimization/correctness tradeoff within a recognizable trace subsystem.
- **C2:** The [FFI semantics](https://luajit.org/ext_ffi_semantics.html) explain reusable native interoperation and its boundaries: pointers do not keep their pointees alive, and callbacks impose lifetime and reentry restrictions.

**Entry points:** `src/lj_snap.c` and the FFI semantics document linked above.

### [luau-lang/luau](https://github.com/luau-lang/luau)

**Language/role:** C++; a substantially evolved Lua-derived language implementation with compiler, VM, and gradual type analysis. Count the monorepo once; the relevant study area here is the compiler/VM and host isolation design.

- **C1:** Read-only shared builtins, per-script global environments, removal of dangerous library facilities, and the requirement to trust compiler-produced bytecode establish specific isolation invariants. The [sandbox documentation](https://luau.org/sandbox/) also describes fuzzing and the limits of its guarantees.
- **C3:** The [performance architecture](https://luau.org/performance/) connects an optimizing bytecode compiler with inline caches, specialized builtin calls, upvalue optimizations, and garbage-collector pacing. Optional native compilation provides another execution tier without making the portable interpreter incidental.

An engineer can study how language restrictions enable optimizations and make shared runtime state easier to reason about. This is a separate implementation trajectory, not merely another packaging of Lua.

**Entry points:** The sandbox and performance design pages linked above.

### [wren-lang/wren](https://github.com/wren-lang/wren)

**Language/role:** C; a compact object-oriented scripting VM with a C embedding API. Study the division between temporary call arguments and persistent references owned by the embedding application.

- **C1:** Executing Wren code invalidates the temporary slot array. A host cannot retain a slot as an enduring object reference; handles instead keep their referenced objects alive across garbage collection and must eventually be released. These lifetime rules are developed in [Slots and Handles](https://wren.io/embedding/slots-and-handles.html).
- **C2:** Slots provide one protocol for transferring arguments and results across the language boundary, while opaque handles represent values of arbitrary Wren types. That combination supports many host interfaces without exposing the VM's internal object layout.

The documentation is especially useful for comparing an explicit handle API with conservative stack scanning or raw reference-counted values.

**Entry point:** [Embedding: slots, handles, and retention](https://wren.io/embedding/slots-and-handles.html).

### [albertodemichelis/squirrel](https://github.com/albertodemichelis/squirrel)

**Language/role:** C++; an embeddable scripting language and VM. Its hybrid memory-management policy makes it a useful comparison with Lua's tracing collector and Wren's rooted handles.

- **C1:** Reference counting reclaims acyclic structures, but reference cycles require a separate mark-and-sweep pass. The embedding documentation explicitly assigns invocation of that pass to the host application, so reclamation is partly an integration invariant rather than an automatic VM guarantee. See [memory management](https://raw.githubusercontent.com/albertodemichelis/squirrel/master/doc/source/reference/embedding/memory_management.rst).
- **C3:** The optional `NO_GARBAGE_COLLECTOR` configuration removes collector bookkeeping while leaving cycle management to the application. The source documentation explains the per-object storage tradeoff instead of merely advertising a small footprint.

Study how a runtime makes collection timing controllable for a host with its own scheduling constraints, and what correctness obligations that control transfers to the embedder.

**Entry point:** The in-tree embedding memory-management chapter linked above.

## Lisp, Scheme, and Tcl embedding

### [janet-lang/janet](https://github.com/janet-lang/janet)

**Language/role:** C and Janet; a Lisp-family language implemented by an embeddable bytecode VM. Study the interaction between native extensions, reentrant evaluation, fibers, and nonlocal error handling.

- **C1:** Native code must distinguish calls that may trigger collection from calls that suppress it. Even a call that suppresses collection can invalidate an argument pointer when a stack grows. The [C API memory model](https://janet-lang.org/capi/memory-model.html) explains these distinct failure modes and explicit rooting requirements.
- **C2:** Root-management operations and scratch allocation form reusable native-extension mechanisms. Scratch storage is reclaimed across panic/nonlocal-exit paths, allowing extension authors to manage temporary memory without inventing an application-specific unwinding scheme.

The most instructive feature is the precision of the boundary contract: preserving an object and preserving an address into a resizable VM stack are different obligations.

**Entry point:** [C API memory model](https://janet-lang.org/capi/memory-model.html), including reentrant calls and scratch memory.

### [ashinn/chibi-scheme](https://github.com/ashinn/chibi-scheme)

**Language/role:** C and Scheme; a compact R7RS Scheme implementation designed as an extension language. Its [maintainer's manual](https://synthcode.com/scheme/chibi/) describes a deliberately layered system: VM opcodes, C primitives, language, module system, and standard modules.

- **C1:** The default precise collector requires native temporaries to be explicitly preserved and released. Separately, independent VM heaps support execution in different OS threads; communicating across managed heaps requires explicit lifetime care. The manual provides the relevant preservation APIs and examples.
- **C2:** Embedders can select or replace layers, evaluate in chosen environments, register primitives, and generate wrappers with the C FFI. This architecture supports more than a fixed command-line Scheme executable.

Study both the small extension surface and its consequences: a minimal API leaves substantial responsibility with the host. Optional language features and collector configurations should be evaluated against the particular build.

**Entry point:** [Manual: embedding, contexts, garbage collection, and C FFI](https://synthcode.com/scheme/chibi/).

### [gambit/gambit](https://github.com/gambit/gambit)

**Language/role:** Scheme and C; an interpreter, compiler, and shared runtime. The selected subsystem is the runtime and its foreign interface, rather than code generation alone.

- **C1:** Scheme continuations are maintained separately from the C stack. Escaping from nested Scheme/C calls can retain C frames, while thread switches can invalidate another thread's nested call frames. The [4.9.7 manual, C-interface chapter](https://gambitscheme.org/4.9.7/manual/) documents these failure modes and restrictions in §16.7.
- **C2:** `c-lambda`, `c-define`, and `c-define-type` describe both directions of interoperation, including generated conversion, custom foreign types, release functions, and cleanup during unwinding. The same chapter distinguishes pointer ownership from copied C structures.

This is a strong study target for the difficult meeting point between first-class continuations and conventional native call stacks. The cited manual is versioned; its restrictions should not be silently generalized to all later builds.

**Entry point:** [Gambit 4.9.7 manual, chapter 16](https://gambitscheme.org/4.9.7/manual/).

### [tcltk/tcl](https://github.com/tcltk/tcl)

**Language/role:** C and Tcl; the Tcl interpreter and extension library. This is the official GitHub mirror of the Tcl core repository. Focus on the value model and bytecode runtime, not Tk or a surrounding application.

- **C1:** A `Tcl_Obj` can cache both a string and a typed internal representation. Mutations must invalidate stale representations, and modifying a shared value requires copying it first. The [Tcl 9.0 object API](https://www.tcl-lang.org/man/tcl9.0/TclLib/Object.html) traces these invariants through concrete value lifetimes.
- **C3:** Lazy conversion avoids repeated parsing, while reference-counted sharing allows argument passing and assignment without copying large values. The performance mechanism follows directly from the representation and ownership rules.
- **C2:** Extension-defined `Tcl_ObjType` implementations let the same protocol support additional host data types.

**Entry point:** [Tcl_Obj: representation, conversion, reference counts, and copy-on-write](https://www.tcl-lang.org/man/tcl9.0/TclLib/Object.html).

## Embeddable ECMAScript engines

### [bellard/quickjs](https://github.com/bellard/quickjs)

**Language/role:** C; a compact JavaScript interpreter and embedding library. Study how a relatively small engine separates heaps, language realms, bytecode, and native object ownership.

- **C1:** `JSValue` duplication/freeing, exception sentinels, finalizers, and cycle-marking callbacks are explicit host obligations. Runtime heaps cannot exchange objects, while contexts within a runtime can share objects. These distinctions are documented in the [C API and internals manual](https://bellard.org/quickjs/quickjs.html).
- **C2:** Runtime/context separation, host-defined classes with opaque data, and module loading supply reusable embedding abstractions.
- **C3:** Direct bytecode generation, compile-time calculation of maximum stack use, shared object shapes, and reference counting with cycle removal explain the execution and storage design.

The manual also makes a consequential trust boundary explicit: serialized bytecode is not a validated format for accepting hostile input.

**Entry point:** [QuickJS manual, C API and internals sections](https://bellard.org/quickjs/quickjs.html).

### [svaarala/duktape](https://github.com/svaarala/duktape)

**Language/role:** C; an embeddable JavaScript engine. The repository distinguishes the incompatible Duktape 3 development line from `v2-maintenance`; choose a branch deliberately when studying or integrating it.

- **C1:** Bytecode serialization cannot simply preserve arbitrary live closures: lexical environments and function instances differ from reusable function templates. The [bytecode design document](https://github.com/svaarala/duktape/blob/master/doc/bytecode.rst) explains those semantics and warns that loading untrusted bytecode is unsafe.
- **C3:** Dump/load allows compilation work to be reused, while the serialized format deals explicitly with endianness and alignment. This trades startup work for version coupling and a stricter trust boundary rather than providing a universally portable program format.

An experienced engineer can study why serializing executable state is more demanding than writing opcodes to a buffer, particularly when environments and closures are involved.

**Entry point:** [In-tree bytecode format and loading design](https://github.com/svaarala/duktape/blob/master/doc/bytecode.rst).

### [jerryscript-project/jerryscript](https://github.com/jerryscript-project/jerryscript)

**Language/role:** C; a JavaScript engine oriented toward constrained devices. The [internals guide](https://jerryscript.net/internals/) exposes the parser, VM, and ECMAScript support layers as separately understandable subsystems.

- **C1:** Tagged values and explicit ownership conventions govern when values must be retained or released. Garbage collection, object references, and property lookup caches must remain consistent with the authoritative object representation.
- **C3:** The parser emits compact bytecode directly; variable-length and combined instructions, compressed pointers, and snapshot execution address different sources of memory and execution overhead. The guide explains the mechanisms without requiring acceptance of a benchmark comparison.

Study how footprint constraints propagate through the whole engine: instruction encoding, heap addressing, parser intermediates, and deployment format all matter. These are more informative than an isolated claim about executable size.

**Entry point:** [JerryScript internals](https://jerryscript.net/internals/), especially bytecode, values, and memory management.

### [boa-dev/boa](https://github.com/boa-dev/boa)

**Language/role:** Rust; an embeddable JavaScript engine with parser, execution engine, and collector components. Count the monorepo once and focus on scope analysis and execution in the engine.

- **C1:** JavaScript locals cannot all become simple machine-like registers: captured bindings, mapped `arguments`, and dynamic evaluation impose observable aliasing and lookup semantics. The project explains these constraints in its [local-variable implementation article](https://boajs.dev/blog/2025/03/05/local-variables/).
- **C3:** The same article follows the move from chained hash-map lookups to indexed environments and register allocation for eligible locals. It is an unusually concrete account of how semantic analysis removes runtime work while preserving closure behavior.

This is a useful smaller-engine counterpart to mature browser engines: the optimization story is inspectable through one well-defined language feature rather than an entire optimizing compiler pipeline.

**Entry point:** [Local variables: scope analysis and indexed/register storage](https://boajs.dev/blog/2025/03/05/local-variables/).

### [sebastienros/jint](https://github.com/sebastienros/jint)

**Language/role:** C#; a managed JavaScript interpreter for .NET. The relevant subsystem is the interpreter and embedding configuration under `Jint/`.

- **C1:** Child-engine configuration must inherit restrictions without automatically inheriting host capability grants. The inspected [Options.cs implementation](https://github.com/sebastienros/jint/blob/main/Jint/Options.cs) classifies those settings and recreates stateful constraints for each engine. Its comments identify reflective tests guarding the classification of new options.
- **C2:** Host interoperability, configurable constraints, and reusable prepared scripts/modules provide several integration modes. The [repository documentation](https://github.com/sebastienros/jint) distinguishes shareable prepared code from values tied to an engine or realm.

Study policy propagation and ownership in an interpreter that relies on the host's managed runtime. Resource constraints are cooperative: the documentation explicitly notes that they do not preempt an arbitrary blocking host callback.

**Entry points:** `Jint/Options.cs` and the repository's embedding/constraint documentation linked above.

## Python and Ruby runtime implementations

### [python/cpython](https://github.com/python/cpython)

**Language/role:** C and Python; Python's reference interpreter. The selected study area is the evaluation loop, generated instruction definitions, frames, and C API migration, rather than the whole standard library.

- **C1:** Instruction families must preserve cache-layout and stack invariants as execution specializes and falls back. The [interpreter internals](https://raw.githubusercontent.com/python/cpython/main/InternalDocs/interpreter.md) explain these constraints and the use of generated interpreter cases.
- **C3:** Guarded specialization, inline caches, and inlined Python calls reduce repeated dispatch and C-call overhead while retaining generic behavior when assumptions fail.
- **C4:** The [Python 3.11 release and porting notes](https://docs.python.org/3.11/whatsnew/3.11.html) date that release to 2022, document frame-layout changes and compatibility adapters for older Python versions, and can be compared with the current generated-instruction architecture. This is concrete evidence of managing runtime evolution across years and extension interfaces.

**Entry points:** The current interpreter internals and versioned release/porting notes linked above.

### [micropython/micropython](https://github.com/micropython/micropython)

**Language/role:** C and Python; a Python implementation for microcontrollers and other constrained hosts. Study the core object/collector design and the responsibilities it imposes on each platform port.

- **C1:** Collector roots must include the correct stacks and global state. Unregistered RTOS stacks, interior pointers, and native references surviving a soft reset are documented sources of invalid lifetimes. See the [memory-management guide](https://docs.micropython.org/en/latest/develop/memorymgt.html).
- **C3:** Tagged immediate values avoid heap allocations for common objects, while heap blocks and a compact allocation/mark bitmap support collection with constrained storage. The guide connects those representations to the collector rather than treating memory usage as an unexplained property.

This provides a different engineering perspective from CPython: root discovery and reset behavior are inseparable from board integration. Python-language familiarity should not be interpreted as complete CPython compatibility.

**Entry point:** [Development guide: memory management](https://docs.micropython.org/en/latest/develop/memorymgt.html).

### [mruby/mruby](https://github.com/mruby/mruby)

**Language/role:** C and Ruby; an embeddable Ruby implementation. Its native-extension GC arena offers a focused study in portable object rooting.

- **C1:** C local variables cannot be assumed visible to the collector. Newly created objects enter a GC arena, and native code must preserve surviving results when restoring an earlier arena boundary. The [arena guide](https://mruby.org/docs/api/file.gc-arena-howto.html) demonstrates this with actual extension patterns, including `Array#inspect`.
- **C3:** Save/restore operations release temporary roots promptly, preventing repeated native calls from retaining unnecessary objects. The performance concern is live memory and retention, balanced against a portable collector interface rather than automatic scanning of arbitrary C frames.

Study why correct rooting can still cause excessive memory retention, and how an API can make both correctness and temporary-object lifetime visible to extension authors.

**Entry point:** [GC arena how-to](https://mruby.org/docs/api/file.gc-arena-howto.html).

### [RustPython/RustPython](https://github.com/RustPython/RustPython)

**Language/role:** Rust and Python; an independent, embeddable Python implementation. The [architecture document](https://raw.githubusercontent.com/RustPython/RustPython/main/architecture/architecture.md) separates parsing, compilation, stack VM, native libraries, and Python library code.

- **C1:** The [floating-point implementation and tests](https://raw.githubusercontent.com/RustPython/RustPython/main/crates/common/src/float_ops.rs) handle signed zero, overflow, hexadecimal conversion, and decimal rounding compatible with Python behavior. Its discussion of `round(2.675, 2)` shows why straightforward scaling and rounding can be wrong.
- **C2:** A separate VM crate, native module/class support, and reusable common numeric operations give hosts and library implementers defined integration boundaries.

The architecture document also candidly describes skipped, failing, and crash-prone cases in the imported CPython test suite. These tests are valuable compatibility infrastructure, but their presence is not evidence that RustPython is a drop-in replacement for every CPython application.

**Entry points:** The architecture document and `crates/common/src/float_ops.rs` linked above.

## Runtimes integrated with Rust, Go, C++, and Java

### [rhaiscript/rhai](https://github.com/rhaiscript/rhai)

**Language/role:** Rust; an embedded scripting engine with a configurable host-facing type and function API. Study the combination of type erasure, host registration, and bounded evaluation.

- **C1:** Operation accounting has explicit limits: native calls count as operations without bounding the work performed inside them, limits are unlimited by default, and unchecked configurations disable protection. The [operation-limit documentation](https://rhai.rs/book/safety/max-operations.html) makes this distinction clear.
- **C2:** Host-defined types are exposed through reusable registration mechanisms for methods, properties, indexers, and iterators. The [custom-types guide](https://rhai.rs/book/rust/custom-types.html) explains cloning/type erasure and the additional `Send`/`Sync` requirements under synchronized configurations.

Rhai is useful for studying a scripting API that adapts ordinary Rust types to a dynamic language. Resource budgets are an embedding mechanism, not a guarantee that arbitrary native functions are interruptible.

**Entry points:** The operation-limit and custom-type guides linked above.

### [rune-rs/rune](https://github.com/rune-rs/rune)

**Language/role:** Rust; a dynamic language and embeddable VM supporting asynchronous execution. Study how execution frames and resource accounting interact with resumable computations.

- **C1:** The [call-frame design](https://rune-rs.github.io/book/call_frames.html) constrains instructions to a frame's stack slice and checks cleanup on return. These checks detect compiler/VM disagreements; the document does not claim perfect protection against malicious instructions.
- **C2:** The [sandboxing APIs](https://rune-rs.github.io/book/sandboxing.html) provide budget wrappers for functions and futures, including budgets that travel with suspended execution. This makes the same control mechanism usable in synchronous and asynchronous hosts.
- **C3:** Memory accounting is integrated with Rune's allocation-aware collections rather than pretending to measure every allocation made by arbitrary Rust code. This exposes the practical scope of resource control and its architectural boundary.

**Entry points:** The call-frame walkthrough and sandboxing chapter linked above. Native integrations must cooperate with the relevant budget mechanisms.

### [google/starlark-go](https://github.com/google/starlark-go)

**Language/role:** Go; a Starlark interpreter for embedding deterministic configuration and extension logic. Study the value protocol and the transition from mutable evaluation state to safely shared module values.

- **C1:** Transitive freezing covers contained values and function-associated state. Active iteration restricts mutation, and iterator cleanup is part of the protocol. These invariants enable frozen modules to be reused across concurrent evaluations, as described in the [implementation guide](https://raw.githubusercontent.com/google/starlark-go/master/doc/impl.md).
- **C2:** Host-defined values implement interfaces for language operations and freezing, allowing application objects to participate in the same semantics as builtin values. The interpreter's reusable value layer therefore carries behavioral obligations, not just conversion helpers.

The design document is marked as work in progress, so it is best used as a map into the implementation rather than a versioned specification of every current optimization.

**Entry point:** [Implementation guide: values, freezing, iteration, and execution](https://raw.githubusercontent.com/google/starlark-go/master/doc/impl.md).

### [d5/tengo](https://github.com/d5/tengo)

**Language/role:** Go; an embeddable scripting language compiled to VM bytecode. Study how compiled programs, their mutable globals, and host-defined objects are separated.

- **C1:** Allocation limits count allocations cumulatively rather than measuring live bytes, and process-wide string/byte limits should not change during execution. Concurrent runs require appropriate state separation; the documentation demonstrates cloning compiled programs. See [interoperability](https://raw.githubusercontent.com/d5/tengo/master/docs/interoperability.md).
- **C2:** The `Object` and `ModuleGetter` interfaces admit native objects, builtin modules, and source modules. Compiled programs expose controlled variable exchange and can be prepared once for repeated evaluation.

Its explicit distinction between compiled code and execution state makes Tengo useful for service-side expression or script evaluation. Modules and filesystem imports are not enabled implicitly, which is a concrete host-integration choice rather than a general security certification.

**Entry point:** [Interoperability: compiled scripts, objects, modules, and limits](https://raw.githubusercontent.com/d5/tengo/master/docs/interoperability.md).

### [traefik/yaegi](https://github.com/traefik/yaegi)

**Language/role:** Go; a Go interpreter embedded in Go applications. The maintainer's [internals article](https://marc.vertes.org/yaegi-internals/) explains a distinctive execution design using the Go runtime itself.

- **C2:** Generated closures operate on values represented through Go reflection; the host runtime supplies garbage collection, channels, and goroutines. Exported host symbols and interpreter evaluation therefore fit into an existing Go application without introducing a separate native engine.
- **C3:** Semantic passes annotate an AST with type information, control-flow successors, and frame allocation information before execution. Action nodes then produce executable closures, moving repeated decisions out of the execution path while retaining a portable implementation.

Study the tradeoff between implementing a separate bytecode machine and reusing host closures and reflection. The repository documents unsupported areas including C interoperability and assembly; it should not be treated as an unrestricted replacement for the Go toolchain.

**Entry point:** [Yaegi internals: analysis, control-flow construction, and closure execution](https://marc.vertes.org/yaegi-internals/).

### [ChaiScript/ChaiScript](https://github.com/ChaiScript/ChaiScript)

**Language/role:** C++; an embedded scripting implementation integrated directly with C++ types and callable objects. Study the conversion/dispatch layer rather than only the surface language.

- **C1:** Const qualification, pointer versus reference access, polymorphic downcasts, and unsupported static conversions require distinct behavior. The inspected [type-conversion implementation](https://raw.githubusercontent.com/ChaiScript/ChaiScript/develop/include/chaiscript/dispatchkit/type_conversions.hpp) makes those branches and error cases explicit.
- **C2:** `Boxed_Value`, type metadata, and extensible conversion objects provide a common basis for registering host functions and moving C++ objects through dynamic dispatch. They support application-specific types without replacing the interpreter's value protocol.

This codebase is especially relevant to engineers designing dynamic interfaces over a statically typed host: apparently simple scripting calls inherit C++'s constness, inheritance, ownership, and overload concerns.

**Entry point:** [`dispatchkit/type_conversions.hpp`](https://raw.githubusercontent.com/ChaiScript/ChaiScript/develop/include/chaiscript/dispatchkit/type_conversions.hpp) on the inspected `develop` branch.

### [beanshell/beanshell](https://github.com/beanshell/beanshell)

**Language/role:** Java; a Java-syntax interpreter with dynamic scripting extensions running inside the JVM. The repository currently lists BeanShell 3.0.0b1 as a beta and 2.1.1 as legacy; development-tree behavior should not be conflated with either release.

- **C1:** Namespace lookup spans variables, methods, imports, and parent scopes. The [NameSpace implementation](https://raw.githubusercontent.com/beanshell/beanshell/master/src/main/java/bsh/NameSpace.java) also documents a shared reentrant lock for nested command loading to avoid deadlocks across namespace chains.
- **C2:** Namespaces combined with an interpreter and a scripted `This` object provide reusable live objects and scopes for Java-hosted scripting.

The [changelog](https://raw.githubusercontent.com/beanshell/beanshell/master/CHANGES.md) gives a concrete compatibility caution: ongoing 3.0 work restores noncoercive Java/2.x behavior in typed contexts after beta changes. This makes the project useful for studying tension between dynamic convenience and host-language expectations, without assuming the beta is behaviorally interchangeable with legacy versions.

**Entry points:** `NameSpace.java` and the changelog linked above.

## Coverage, search process, and limitations

Discovery used more than six distinct query families: C/C++ embeddable VMs and game scripting; Lua implementations and sandbox design; compact JavaScript engines and bytecode internals; Rust scripting engines and resource budgets; Go configuration/scripting interpreters; Python/Ruby embedding and collector roots; Scheme continuations and native interfaces; and Java/.NET host integration. Follow-up searches targeted numeric regression tests, architecture documents, source-level dispatch and snapshot recovery, compatibility notes, and official mirror status. A late search for alternatives such as PocketPy, Gravity, AngelScript, and small Tcl implementations added candidates but increasingly repeated architectural concerns already represented; the retained set emphasizes independently inspected implementation evidence rather than attempting an ecosystem census.

The selection spans stack and register-oriented execution, tracing optimization, adaptive specialization, host-closure execution, precise and conservative root discovery, reference counting with cycle handling, and managed-host integration. These comparisons are grounded in the linked documents; the judgment that a subsystem is worth studying is the researcher's inference. No benchmark results were independently reproduced, and no candidate code was executed or dependencies installed.

Important exclusions include tutorial interpreters, thin language bindings, generated wrappers, repository lists, expression-only utilities, and general compiler infrastructure without a central interpreter/embedding role. Browser-scale engine monorepos and additional implementations of already-covered language families are not comprehensively surveyed. QuickJS derivatives and alternate Lua bindings were not counted as extra projects merely for sharing an ecosystem. Luau and LuaJIT are retained because their separate runtime and optimization architectures are substantive. Every monorepo is counted once.

GitHub repository pages and at least one additional substantive primary source were opened for every retained entry. Some hosted documentation was inaccessible, notably Squirrel's rendered reference, so the corresponding in-repository documentation was read instead. Lua, LuaJIT, and Tcl are explicitly identified as official mirrors. Release cadence was not comprehensively audited: inclusion does not assert active maintenance or production readiness. Versioned manuals, moving development branches, BeanShell's beta status, Duktape's branch split, and RustPython's incomplete compatibility evidence are identified where they affect interpretation. Before using a project in production, the relevant release and configuration would need their own evaluation.
