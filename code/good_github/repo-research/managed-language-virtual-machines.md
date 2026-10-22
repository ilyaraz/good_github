# Managed language virtual machines

Research date: **2026-10-09**. This selection covers 23 GitHub repositories implementing managed execution for high-level languages: bytecode interpreters, tracing and method JITs, actor runtimes, embedded VMs, and native-code runtimes with managed heaps. It includes substantial VM-building frameworks and identifies the relevant subsystem within larger monorepos. Hardware virtualization, standalone garbage collectors, and runtimes whose primary purpose is executing WebAssembly are outside this report's scope.

The criteria below are engineering judgments grounded in the linked implementation material, not benchmark rankings or assertions that every component is exemplary. Repository pages and at least one additional primary source were opened for every entry.

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable machinery supporting different applications, languages, platforms, or execution modes.
- **C3 — Performance and structure:** concrete resource or execution constraints addressed through an understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate complexity management.

## JVM, CLR, and shared language infrastructure

### 1. [openjdk/jdk](https://github.com/openjdk/jdk)

**Language/role:** C++ and Java; HotSpot is the relevant VM subsystem in the JDK monorepo. A particularly useful study is how a large runtime brings heterogeneous thread states to a coordinated stopping point.

- **C1:** Safepoint synchronization distinguishes interpreted, compiled, native, blocked, and VM execution. The implementation explains why native transitions require memory ordering, arms a wait barrier before publishing the safepoint, and uses the thread-list lock to prevent thread creation or exit from violating the protocol.
- **C3:** The same implementation balances synchronization latency against CPU consumption through staged backoff and by retaining only threads still needing attention. Assertions, timeout diagnostics, tracing, and event recording make the protocol inspectable rather than hiding it behind a single global pause operation.

**Entry point:** HotSpot's [`safepoint.cpp`](https://github.com/openjdk/jdk/blob/master/src/hotspot/share/runtime/safepoint.cpp), especially synchronization, thread-state handling, and backoff. These claims concern that implementation, not a comparison of the JDK's different collectors.

### 2. [eclipse-openj9/openj9](https://github.com/eclipse-openj9/openj9)

**Language/role:** C/C++ and Java; an independent JVM implementation, integrated with OpenJDK libraries and Eclipse OMR. Its shared class infrastructure offers a different architectural perspective from HotSpot.

- **C1:** Shared class caches must validate classpath and timestamp information, distinguish incompatible cache generations, and respect object-reference compression modes. Reusing cached data safely is a compatibility protocol, not simply mapping a file into memory.
- **C3:** Caches share class data, ahead-of-time compiled code, and JIT profiling data across VM executions. Persistent mappings and layered caches address startup and memory costs, including duplication caused by container filesystem copy-on-write.
- **C2:** The documented helper interfaces extend caching to custom class loaders, making this a reusable runtime service rather than a special case for the bootstrap loader.

**Entry point:** [OpenJ9 shared classes documentation](https://eclipse.dev/openj9/docs/shrc/), covering cache structure, validation, layering, and loader integration.

### 3. [dotnet/runtime](https://github.com/dotnet/runtime)

**Language/role:** C++, C, and C#; a runtime monorepo containing CoreCLR and Mono, counted once. The evidence here focuses on CoreCLR's garbage collector.

- **C1:** Generational collection depends on JIT-emitted write barriers recording older-to-younger references. Relocation must update weak references as well as ordinary roots, while background collection requires explicit coordination with suspended and running execution engines.
- **C3:** Allocation budgets respond to survival rates, fragmentation, and memory pressure. Separate marking, planning, relocation, compaction, and sweeping phases expose the choices behind collection policy; workstation, server, and background configurations address different workloads.

An experienced engineer can study the boundary between compiler-generated barriers, allocator policy, and thread suspension without treating GC as an isolated library.

**Entry point:** The CoreCLR Book of the Runtime's [garbage collector design](https://github.com/dotnet/runtime/blob/main/docs/design/coreclr/botr/garbage-collection.md).

### 4. [oracle/graal](https://github.com/oracle/graal)

**Language/role:** Primarily Java; compiler and runtime infrastructure. The relevant subsystem is Truffle and its optimizing execution machinery, not every tool in the monorepo.

- **C2:** Truffle gives language implementers shared machinery for specializing guest-language interpreters. Interpreter structure, profiling, and specialization become inputs to compilation, allowing substantial execution infrastructure to be reused across language implementations.
- **C3:** The optimization guide connects partial evaluation, compilation boundaries, frame materialization, and deoptimization to concrete performance outcomes. It also shows how to inspect intermediate representations and compilation decisions, making optimization failures diagnosable.

This is a strong study of the contract between an interpreter author and a compiler: apparently harmless choices can prevent specialization or repeatedly invalidate compiled code.

**Entry point:** Truffle's [optimizing guide](https://github.com/oracle/graal/blob/master/truffle/docs/Optimizing.md), especially partial-evaluation diagnostics and deoptimization guidance. The repository is counted once rather than separately listing Truffle and its compiler.

### 5. [dart-lang/sdk](https://github.com/dart-lang/sdk)

**Language/role:** C++ and Dart; the Dart VM within the SDK monorepo. Its GC documentation closely connects object representation, native integration, and parallel execution.

- **C1:** A precise moving collector requires C++ handles instead of untracked object pointers across safepoints. Parallel evacuation uses atomic forwarding-pointer installation, including recovery when another worker wins the race. Concurrent marking imposes additional write-barrier invariants.
- **C3:** Tagged values and alignment choices reduce object-classification costs. The implementation combines generational and incremental barrier checks, while dividing work between young-generation copying and old-generation concurrent marking and sweeping or compaction.

The useful lesson is how low-level representation choices simplify hot paths while increasing the obligations imposed on runtime code.

**Entry point:** The VM's [garbage collection design](https://github.com/dart-lang/sdk/blob/main/runtime/docs/gc.md), including handles, safepoints, parallel scavenging, and barrier implementation.

## Actor and process-oriented virtual machines

### 6. [erlang/otp](https://github.com/erlang/otp)

**Language/role:** C and Erlang; the BEAM emulator and Erlang Runtime System (ERTS) within OTP. Study the interaction between immutable language semantics and process-local memory management.

- **C1:** The collector depends on the absence of pointers from old objects into the young generation. Erlang's immutable terms make this invariant practical. Copying must still preserve sharing and correctly interpret tagged immediate and boxed values.
- **C3:** Per-process heaps localize collection work. Allocation checks can be combined, while message heap fragments avoid unnecessary copying and alter which objects must be treated as roots. The documentation explains these tradeoffs rather than only presenting collector names.

The primary guide also documents changes introduced in OTP 19, giving historical context for message handling; this entry does not assume that all BEAM implementations share the same layout.

**Entry point:** ERTS's [garbage collection documentation](https://www.erlang.org/doc/apps/erts/garbagecollection.html), especially the generational invariant and heap-fragment sections.

### 7. [atomvm/AtomVM](https://github.com/atomvm/AtomVM)

**Language/role:** Primarily C; a separate implementation of a subset of BEAM for constrained systems, supporting Erlang and Elixir use cases. It is not full OTP compatibility in a smaller package.

- **C1:** Process operations cross scheduler boundaries through signals and mailboxes. The internals explain why a caller of a process-information operation can be trapped until the target runs and replies, and why another process's collection is requested rather than performed through unsynchronized direct manipulation.
- **C3:** Memory-constrained deployment shapes module representation and diagnostics. Module data can remain memory-mapped, while filename references and optional line information avoid or control extra allocations.
- **C2:** `GlobalContext`, per-process `Context`, module tables, and platform interfaces separate common VM behavior from individual embedded targets.

**Entry point:** [AtomVM internals](https://doc.atomvm.org/main/atomvm-internals.html), including contexts, signals, modules, and line information. These are development-branch documents; supported instructions and libraries should be checked against the chosen release.

## Dynamic-language implementations and specialization

### 8. [pypy/pypy](https://github.com/pypy/pypy)

**Language/role:** RPython/Python, translated to a lower-level implementation; Python VM plus reusable translation and JIT infrastructure.

- **C2:** The architecture separates bytecode compilation, evaluation, and the object space implementing operations on values. The RPython toolchain supplies memory management during translation rather than forcing the interpreter to hard-code a collector. This separation also supports language implementations beyond Python.
- **C3:** Meta-tracing specializes execution of the interpreter itself. The tracer, optimization stages, and machine-code backends are distinct components, with hints connecting interpreter semantics to compilation decisions.

This is a useful contrast with hand-built method JITs: the abstraction being optimized is an interpreter written in a restricted implementation language, not merely the guest bytecode stream.

**Entry point:** [PyPy architecture](https://doc.pypy.org/architecture.html), especially object spaces, the translation framework, and the JIT overview. The linked GitHub repository is the project's repository, not an unrelated historical mirror.

### 9. [RustPython/RustPython](https://github.com/RustPython/RustPython)

**Language/role:** Rust; a Python interpreter and embeddable VM. The repository describes ongoing compatibility work and an experimental optional JIT; it should not be read as a drop-in production replacement for every CPython workload.

- **C1:** Numerical helpers explicitly handle floating-point comparisons with arbitrarily large integers, infinities and NaNs, and Python-compatible division and remainder, including signed zero and rounding corrections. These are language-semantic obligations beyond using Rust's built-in arithmetic.
- **C2:** Compiler, VM, shared low-level helpers, native-module macros, and standard-library integration have separate responsibilities. The architecture guide also identifies the adapted CPython tests and known skipped cases, making compatibility gaps visible.

**Entry points:** [Architecture guide](https://github.com/RustPython/RustPython/blob/main/architecture/architecture.md) and [`float_ops.rs`](https://raw.githubusercontent.com/RustPython/RustPython/main/crates/common/src/float_ops.rs). Together they connect reusable VM structure to concrete semantic edge cases.

### 10. [ruby/ruby](https://github.com/ruby/ruby)

**Language/role:** C, Rust, and Ruby; CRuby's YARV interpreter and YJIT compiler, counted together. This GitHub repository is an official mirror of the Ruby source repository.

- **C3:** YJIT's lazy basic-block versioning specializes code incrementally. Compilation thresholds, executable-memory limits, cold-code controls, and optional code collection expose the tradeoff between speed, warmup, and memory consumption.
- **C4:** Ruby's [2021 release announcement](https://www.ruby-lang.org/en/news/2021/11/09/ruby-3-1-0-preview1-released/) records YJIT's initial integration. The versioned Ruby 3.4 guide documents subsequent configuration and code-GC behavior, including changes since 3.3, and how to run YJIT-specific and full Ruby tests. This is evidence of continued integration and complexity management across years, rather than age alone.

**Entry points:** The [Ruby 3.4 YJIT guide](https://docs.ruby-lang.org/en/3.4/yjit/yjit_md.html) and the linked introductory release announcement. The versioned guide is intentionally identified; it is not presented as documentation for every later release.

### 11. [MoarVM/MoarVM](https://github.com/MoarVM/MoarVM)

**Language/role:** Primarily C; a VM designed around the needs of Rakudo/Raku and a reusable object model.

- **C2:** Language-level metamodel behavior is separated from representations that determine storage layout. Inheritance, mixins, and type checks can therefore be defined above machinery for struct-like objects and arrays.
- **C1:** Precise moving GC is accompanied by stress techniques: collecting at every allocation and protecting previous copying spaces help expose stale pointers that ordinary workloads may conceal.
- **C3:** The specialization layer uses argument and type observations, with deoptimization, small-routine inlining, and on-stack replacement. These mechanisms provide an explicit path from generic execution to optimized code.

An engineer can study how a rich language object system is supported without baking every semantic decision into the lowest-level allocator and dispatch machinery.

**Entry point:** The official [VM architecture and features overview](https://www.moarvm.org/features.html), whose representation, collector, and specialization sections contain implementation explanations beyond a feature checklist.

### 12. [facebook/hhvm](https://github.com/facebook/hhvm)

**Language/role:** C++ and Hack; a managed runtime for Hack. Its historical association with PHP should not be mistaken for a claim of current PHP compatibility.

- **C1:** Request-local allocation, persistent data, reference counting, and tracing for cycles impose different lifetime rules. Roots span the native stack, VM stack, and request-data segment; shared persistent values cannot follow ordinary request-local reference-count updates.
- **C3:** The interpreter guide describes an intentional division of labor: performance-sensitive execution relies on the JIT, while the interpreter remains a semantic reference. Generated opcode wrappers reduce duplication, and JIT code can synchronize state and invoke an interpreter helper for an individual difficult instruction.

This is especially instructive for runtimes designed around short-lived requests but also maintaining concurrent shared state.

**Entry points:** [Memory management](https://github.com/facebook/hhvm/blob/master/hphp/doc/hackers-guide/memory-management.md) and [bytecode interpreter design](https://github.com/facebook/hhvm/blob/master/hphp/doc/hackers-guide/bytecode-interpreter.md).

## JavaScript engines

### 13. [v8/v8](https://github.com/v8/v8)

**Language/role:** Primarily C++; a JavaScript engine and embeddable managed runtime. GitHub is the official mirror of the V8 source hosted on Chromium's infrastructure.

- **C1:** Concurrent marking must preserve reachability while mutators allocate, change object layouts, and update references. The design explains the tri-color invariant, atomic coordination, and why apparently simple barrier checks can become races.
- **C3:** Segmented marking worklists allow cheap local operations and controlled publication for work stealing. The collector's barrier design explicitly considers the cost of memory ordering, illustrating how synchronization overhead constrains the architecture.

**Entry point:** The team's [concurrent marking design article](https://v8.dev/blog/concurrent-marking). This is a dated architectural account from 2018, useful for studying the reasoning behind a production collector; it is not evidence that every detail remains unchanged in the current tree. No historical benchmark result is treated as a present-day performance guarantee.

### 14. [facebook/hermes](https://github.com/facebook/hermes)

**Language/role:** Primarily C++; JavaScript execution infrastructure developed for application workloads including React Native. Its ahead-of-time optimization and bytecode pipeline offer a different starting point from browser-engine architecture.

- **C1:** The IR specifies correctness obligations for type annotations and side-effect classifications. Generator lowering must preserve suspended state and exception behavior, while closure environments and stack or heap variables must retain JavaScript semantics across transformations.
- **C3:** An infinite-register intermediate representation is lowered through register allocation, including phi handling and argument-placement constraints, toward compact executable bytecode. The architecture separates semantic lowering from the storage decisions required by the execution engine.

An engineer can follow how language constructs become explicit control flow and state before final code emission.

**Entry point:** Hermes's [IR design document](https://github.com/facebook/hermes/blob/static_h/doc/IR.md). This link targets the verified `static_h` branch; this report does not assume that all Hermes release lines expose identical internals.

### 15. [quickjs-ng/quickjs](https://github.com/quickjs-ng/quickjs)

**Language/role:** C; a compact JavaScript engine. QuickJS-NG is a substantively evolved fork of QuickJS, not an additional listing of an unchanged upstream mirror. Upstream QuickJS is not separately counted here.

- **C1:** Reference counting is supplemented by cycle removal. The regular-expression implementation uses its own backtracking stack and handles empty-term loops, illustrating correctness and failure cases beyond ordinary bytecode dispatch.
- **C3:** Direct bytecode generation, compile-time stack sizing, and shared object shapes keep the engine compact. The fork documents additional opcode fusion and polymorphic inline caches, making its independent implementation work concrete.
- **C2:** The engine exposes a reusable embedding core with distinct runtime and execution-context concepts; its internals are small enough to follow across parsing, execution, and reclamation.

**Entry points:** [Engine internals](https://quickjs-ng.github.io/quickjs/developer-guide/internals/) and [differences from upstream](https://quickjs-ng.github.io/quickjs/diff/). The latter also describes Test262 and sanitizer/build-configuration testing; performance claims here are qualitative, not benchmark comparisons.

## Compact and embedded managed runtimes

### 16. [LuaJIT/LuaJIT](https://github.com/LuaJIT/LuaJIT)

**Language/role:** C, assembly, and Lua; a tracing JIT runtime. This GitHub repository is an [official mirror](https://luajit.org/download.html).

- **C1:** Trace snapshots record enough VM state to recover execution when optimized assumptions fail. The snapshot implementation tracks stack slots, frame information, program positions, and live values, including interactions with open upvalues.
- **C3:** Snapshot storage is reduced by omitting unchanged or otherwise unnecessary slots and merging compatible snapshots. These optimizations sit in a dedicated implementation unit with explicit bounds and representation checks, making a central JIT space/time tradeoff inspectable.

Study this code to understand that speculative compilation needs a carefully engineered route back to ordinary language execution, not just a fast machine-code path.

**Entry point:** [`lj_snap.c` on the `v2.1` branch](https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/lj_snap.c). The branch-specific source and official distribution page establish both the mechanism and repository provenance.

### 17. [mruby/mruby](https://github.com/mruby/mruby)

**Language/role:** C and Ruby; an embeddable Ruby implementation with its own VM, compiler, and extension model.

- **C1:** References held only in native C locals are not sufficient to keep managed objects alive. The GC arena API requires deliberate save, restore, and protection operations; using it incorrectly can either collect a needed temporary or retain too many objects and exhaust arena capacity.
- **C2:** Embedding interfaces, compiled bytecode that can be packaged into C applications, and `mrbgems` support different host applications and native extensions. The root-handling contract applies consistently across these integrations.

This is a compact case study of the boundary between automatic lifetime management and a manually managed host language. The documented examples show why restoring an arena requires reasoning about which result must remain rooted.

**Entry point:** The [GC arena guide](https://mruby.org/docs/api/file.gc-arena-howto.html), alongside the repository's embedding and extension overview.

### 18. [micropython/micropython](https://github.com/micropython/micropython)

**Language/role:** Primarily C with Python; a Python implementation for microcontrollers and constrained environments, with a shared core and platform ports. Python compatibility is intentionally scoped to the implementation and target.

- **C1:** Collector roots include registered pointers and supported execution stacks, but arbitrary native globals, interior pointers, or unregistered RTOS stacks cannot be assumed safe. Soft reset introduces a further lifetime boundary for objects referenced by native code.
- **C3:** Tagged values avoid heap allocation for common immediate objects. A block-based heap and allocation bitmap make memory-management costs visible in a runtime intended for tight RAM budgets.

The valuable study is the explicit contract required of a platform port or native extension, especially when the surrounding operating system has its own tasks and memory lifetimes.

**Entry point:** [Memory management internals](https://docs.micropython.org/en/latest/develop/memorymgt.html), including root registration, object representation, and the collector. The linked `latest` documentation can describe development behavior.

### 19. [wren-lang/wren](https://github.com/wren-lang/wren)

**Language/role:** C; a compact, embeddable class-based scripting VM with fibers. Its modest implementation size makes complete control-flow and object-lifetime paths easier to follow than in industrial monorepos.

- **C1:** Capturing a local variable reuses an existing upvalue when appropriate, preserving sharing between closures. Collection must root modules, fibers, temporary values, handles, and compiler state; allocation and compilation can therefore interact in ways an embedding API must respect.
- **C2:** Configuration hooks cover allocation, module resolution and loading, foreign methods, and foreign classes. These form a reusable host interface instead of coupling the VM to one executable or filesystem arrangement.

**Entry point:** [`wren_vm.c`](https://raw.githubusercontent.com/wren-lang/wren/main/src/vm/wren_vm.c), especially configuration, root marking, and upvalue capture. Inclusion is based on the implementation's substance; it is not a claim about release frequency or a promise of a particular maintenance cadence.

## Reflective, stack-based, and research systems

### 20. [OpenSmalltalk/opensmalltalk-vm](https://github.com/OpenSmalltalk/opensmalltalk-vm)

**Language/role:** Smalltalk-derived C plus handwritten platform code; the Cog/Spur VM family. The repository contains generated core VM sources, real platform implementation, and build machinery; the editable Smalltalk VM definitions also live in the Smalltalk source infrastructure linked by the project.

- **C1:** Reflective object-identity operations require forwarding machinery, and weak/ephemeron handling imposes collector ordering requirements. Release notes include a concrete fix for unscanned ephemerons, demonstrating a subtle failure mode rather than merely asserting GC correctness.
- **C3:** Stack-mapped activations, the Cog JIT, and Spur's generational collection and segmented memory organization provide connected examples of execution and heap optimization.

**Entry points:** The repository's [VM architecture overview](https://github.com/OpenSmalltalk/opensmalltalk-vm#readme) and [release notes](https://github.com/OpenSmalltalk/opensmalltalk-vm/releases). The project states that Pharo and Newspeak support was dropped in August 2025; current coverage centers on Squeak and Cuis, with older variants available historically. This should not be treated as a current VM for every Smalltalk dialect.

### 21. [factor/factor](https://github.com/factor/factor)

**Language/role:** Factor and C++; an image-based, stack-oriented managed runtime, with a native VM and a self-hosted optimizing compiler.

- **C1:** Optimized stack updates can expose uninitialized slots when an allocation triggers GC. A dedicated dataflow analysis identifies these holes and inserts clearing operations, including cases involving unsafe stack reads; otherwise the collector could interpret garbage as references.
- **C3:** A fast, non-optimizing quotation compiler in the VM coexists with a higher-level compiler performing more expensive data and control-flow analysis. Saved images retain compiled work, exposing a practical compile-time versus execution-time tradeoff in an interactive system.

This is a useful example of compiler transformations having direct obligations to the collector, even when the source language abstracts away both stack addresses and allocation details.

**Entry points:** [Stack-location clearing](https://docs.factorcode.org/content/article-compiler.cfg.stacks.clearing.html) and [the two-compiler architecture](https://docs.factorcode.org/content/article-compiler.html).

### 22. [cisco/ChezScheme](https://github.com/cisco/ChezScheme)

**Language/role:** Scheme and C; a native-code managed runtime with an additional portable-bytecode VM. It belongs here because execution, object layout, collection, and compiler/runtime contracts are substantial parts of the repository.

- **C1:** Compiler-generated object-layout headers must agree with the C collector. Code objects retain relocation information so collection can update references involving moved code and heap objects. Captured mutable variables also require representation choices that preserve sharing across closures and continuations.
- **C2:** A portable instruction set provides a bootstrap path and execution option where a native backend or runtime code generation is unavailable. Its platform-neutral and platform-specific variants make word size, endianness, and foreign-interface constraints explicit.
- **C3:** Nanopass compiler stages and backend interfaces separate optimization from instruction selection and emission, while supporting guarded inline implementations of primitives.

**Entry point:** The extensive [implementation guide](https://github.com/cisco/ChezScheme/blob/main/IMPLEMENTATION.md), especially object layouts, linking, compiler structure, and portable bytecode.

### 23. [JikesRVM/JikesRVM](https://github.com/JikesRVM/JikesRVM)

**Language/role:** Primarily Java; a self-hosting research JVM. Treat it as a research and historical architecture study: the repository's documented class-library and build constraints are not equivalent to support for a current Java platform.

- **C2:** The adaptive system separates event organizers, a controller, compilation threads, optimization strategies, and cost models. These interfaces make experimentation with runtime policy an architectural feature.
- **C3:** Runtime sampling feeds cost/benefit decisions about recompilation and inlining. Yieldpoint placement and uninterruptible regions affect sampling accuracy, while queues and compiler threads decouple optimization work from the running application. Record/replay facilities help investigate decisions and failures.

The system is valuable for understanding how a VM decides whether optimization is worth its own CPU and compilation cost, rather than assuming that every hot method should receive maximal optimization.

**Entry point:** The [Adaptive Optimization System guide](https://www.jikesrvm.org/UserGuide/AdaptiveOptimizationSystem/index.html).

## Search coverage and limitations

Discovery used well over six distinct live-search formulations. The principal angles were JVM/CLR architectures and shared caches; BEAM/actor runtimes; RPython and dynamic-language specialization; JavaScript bytecode and GC designs; embedded Wren, mruby, and MicroPython implementations; Smalltalk and reflective object memories; Factor's stack/collector interaction; Scheme native and portable runtimes; and smaller research JVMs. Follow-up searches targeted safepoints, numerical semantics, JIT snapshots, rooting APIs, test practices, and release history. Later small-JVM and mirror searches produced diminishing returns, including inactive projects and unofficial staging mirrors rather than additional well-supported selections.

Canonical GitHub repository pages were opened for all 23 entries. Each retained project also has an opened, substantive primary implementation or design source beyond its repository README; release material supplements that evidence where used. Monorepos count once, and QuickJS-NG's independent evolution is explicit. Official GitHub mirrors are identified for Ruby, V8, and LuaJIT. OpenSmalltalk's generated-source workflow and JikesRVM's research-era compatibility constraints are called out separately.

The search did not retain tutorial VMs, wrapper-only projects, standalone GC toolkits, or hypervisors. Smaller JVM candidates such as Avian and search results for JamVM/CACAO did not yield enough additional, clearly canonical and applicable evidence to justify expanding this selection. Android runtime implementations were not included without completing the required official GitHub repository and additional-source verification; their absence is not a judgment about technical merit. Other substantive runtimes may also be missing: this is a diverse selection guide, not a complete ecosystem inventory.

No candidate repository was cloned, built, or benchmarked. Links include moving branches, development documentation, explicitly versioned guides, and dated design articles; documented mechanisms are distinguished from claims about current release behavior. Criteria assessments are grounded in those mechanisms, but are not independent correctness audits. Maintenance status is not inferred from stars, repository age, or a recent push, and historical design measurements are not repeated as current performance claims.
