# Dynamic binary instrumentation frameworks

Research date: **2026-10-09**

This guide selects 18 GitHub codebases for studying instrumentation of executing machine code. It covers native dynamic translation, selective runtime rewriting and probes, GPU instrumentation, and emulators with substantial instrumentation APIs. These mechanisms have different transparency and deployment properties; an emulator or syscall rewriter is not interchangeable with an attachable native DBI engine. Purely static rewriters, managed-bytecode instrumentation, individual analysis clients, bindings alone, and binary-only engine distributions are outside this selection.

Each repository meets at least two of the following criteria based on the linked primary material. The guide identifies useful engineering problems and abstractions, rather than asserting that every component is exemplary or currently compatible with every advertised platform.

- **C1 — Difficult correctness:** maintaining semantics, invariants, concurrency, or well-defined behavior across difficult inputs and failure modes.
- **C2 — Reusable abstractions:** substantial interfaces and components that support multiple instrumentation or analysis use cases.
- **C3 — Performance with structure:** explicit treatment of runtime or translation costs through an understandable architecture.
- **C4 — Sustained evolution:** documented evolution accompanied by compatibility work, testing, or complexity management. Age or a recent commit alone does not qualify.

## Native translation and process instrumentation

### 1. [DynamoRIO/dynamorio](https://github.com/DynamoRIO/dynamorio)

**Language / role:** C and assembly; native runtime code manipulation and client instrumentation across several CPU and operating-system families.

DynamoRIO is especially useful for studying the boundary between a translated program and operating-system mechanisms that assume original instruction addresses. Its clients operate through instruction manipulation and instrumentation interfaces, while the runtime owns execution and preservation of application state.

- **C1:** Linux restartable sequences are a concrete transparency problem: the kernel interprets instruction ranges and abort addresses belonging to application code, whereas the application executes from a code cache. The design discusses identifying sequences, control-flow redirection, instrumentation side effects, and a two-execution approach with explicit limitations and tests. See the [restartable-sequence design](https://dynamorio.org/page_rseq.html).
- **C2:** The repository exposes reusable client APIs, instruction representations, and extension libraries for building different analyses; clients do not each implement a complete translator. The [repository overview and source layout](https://github.com/DynamoRIO/dynamorio) identify these components.
- **C1, C3:** ARM exclusive-load/store sequences illustrate how inserted memory operations and dispatch machinery can disturb the exclusive monitor and cause retry loops. The [exclusive-access design](https://dynamorio.org/page_ldstex.html) compares implementation strategies and their execution costs.

The two design documents are particularly valuable entry points because they expose difficult compromises rather than just successful API examples.

### 2. [dyninst/dyninst](https://github.com/dyninst/dyninst)

**Language / role:** C++ and C; instrumentation APIs spanning running processes and binary editing. The relevant subsystem here is `dyninstAPI` and its runtime instrumentation machinery.

Study Dyninst for how a public instrumentation model accommodates code relocation, multiple insertion points, process control, and platform differences. Its API supports attaching instrumentation without making every tool manage rewritten machine code directly.

- **C2:** [`BPatch_addressSpace.h`](https://github.com/dyninst/dyninst/blob/master/dyninstAPI/h/BPatch_addressSpace.h) supplies a shared abstraction for process and binary-edit address spaces, snippet insertion and deletion, function replacement, allocation, and grouped insertion. Patch handles account for instances associated with relocated code.
- **C1:** The same API exposes ordering, insertion timing, thread catch-up, and atomicity requests, making synchronization and relocation semantics visible design concerns. These facilities are worth studying together with the repository's documented limitations, including exceptions in relocated code and incomplete support on some architectures.
- **C4:** The [changelog](https://github.com/dyninst/dyninst/blob/master/CHANGELOG.md) documents evolution from the 2018 release's parallel parsing and DWARF-library changes through 2024 work on thread-safe symbol parsing, newer compiler compatibility, full-system-library parsing tests, and downstream-project CI. This is concrete maintenance evidence beyond repository age.

### 3. [QBDI/QBDI](https://github.com/QBDI/QBDI)

**Language / role:** C++; embeddable DBI library with C/C++, Python, and Frida-facing interfaces.

QBDI makes a useful study of a compact virtual-machine abstraction embedded inside the instrumented process. Injection is deliberately separable from instrumentation, allowing different launch and integration mechanisms around the same engine.

- **C2:** The [repository overview](https://github.com/QBDI/QBDI) describes the VM library, bindings, preload helper, and Frida integration. The reusable core is the instruction and execution instrumentation interface, rather than a single analysis application.
- **C1:** The [architecture introduction](https://qbdi.readthedocs.io/en/stable/intro.html) explains that host callbacks and guest code share process resources. Calling a non-reentrant allocator from instrumentation can deadlock; the execution broker and excluded regions address important boundary cases. This is an instructive limitation of an apparently isolated VM API.
- **C3:** That introduction follows the engine through basic-block decoding, patching, instrumentation, executable caching, and dispatch. It provides a readable connection between transformation stages and amortizing translation cost.

The repository explicitly lists limitations around signals, new thread creation, and C++ exceptions. Treat supported-platform lists as qualified by those execution restrictions.

### 4. [frida/frida-gum](https://github.com/frida/frida-gum)

**Language / role:** Primarily C; Frida's reusable native instrumentation core, including Stalker, Interceptor, code writers, and relocators.

Gum is the substantive engine repository to study here; the Frida umbrella and language bindings are not counted as separate frameworks. Its combination of whole-thread tracing and targeted function interception supports very different client designs.

- **C2:** The [repository](https://github.com/frida/frida-gum) separates tracing, interception, relocation, memory monitoring, and introspection facilities behind native APIs, with GumJS providing a higher-level integration layer.
- **C1:** The [Stalker architecture guide](https://frida.re/docs/stalker/) discusses preserving ARM exclusive-access behavior and detecting changes to original code after translation. It also explains why cached translated calls complicate interaction with interception and call probes.
- **C3:** The same guide connects code-cache trust policy, block backpatching, event buffering, and call summaries to overhead. The configurable trust threshold is particularly instructive: validation work and assumptions about code mutability are an explicit policy choice.

Start with the Stalker guide, then follow the corresponding implementation from the Gum repository. Its architecture discussion makes the costs of seemingly simple tracing requests visible.

### 5. [googleprojectzero/TinyInst](https://github.com/googleprojectzero/TinyInst)

**Language / role:** C++; selective native instrumentation, frequently used for coverage and fuzzing infrastructure.

TinyInst is valuable for studying a smaller engine whose scope is selected modules. Its debugger-based execution control, module translation, and hook interfaces make the main mechanisms relatively accessible.

- **C1:** The [implementation explanation in the README](https://github.com/googleprojectzero/TinyInst#how-tinyinst-works) covers executable protection changes, relocated code, nearby allocation for relative addressing, indirect transfers, and optional unwind-information generation. These mechanisms expose the correctness obligations of relocating real application code.
- **C2:** The [hook guide](https://github.com/googleprojectzero/TinyInst/blob/master/hook.md) distinguishes replacement, entry, and entry/exit hooks, as well as debugger-side breakpoint handlers and code emitted into the target. The execution context distinction matters for memory access and callback ordering.
- **C3:** Selective module instrumentation keeps other code native. The README explains alternative indirect-target dispatch structures and the tradeoff between dispatch cost and preserving useful edge identity.

Its stated assumptions concern reasonably well-behaved programs; it should not be inferred to provide universal transparency for arbitrary hostile or self-modifying binaries.

### 6. [beehive-lab/mambo](https://github.com/beehive-lab/mambo)

**Language / role:** C and assembly; research DBI for ARM, AArch64, and RISC-V.

MAMBO broadens the selection beyond x86-centric engines. It is useful for following the interaction between per-architecture dispatch code, traces, and a shared instrumentation-plugin interface.

- **C2:** [`api/plugin_support.h`](https://github.com/beehive-lab/mambo/blob/master/api/plugin_support.h) defines callbacks around instructions, blocks, fragments, syscalls, threads, functions, and virtual-memory events. Plugin and thread data, scratch-register management, and source/generated-code positions support analyses with different state requirements.
- **C1:** [`dispatcher.c`](https://github.com/beehive-lab/mambo/blob/master/dispatcher.c) contains a concrete metadata invariant: source exit information must be saved before a lookup can scan a stub and overwrite that metadata. The dispatcher also avoids linking after a cache flush invalidates the relevant state.
- **C3:** The same dispatcher exposes code-cache lookup, block scanning, trace exits, and branch linking, letting readers connect the API's instrumentation events to the engine's mechanisms for reducing repeated dispatch.

This is research infrastructure, and the README explicitly disclaims use as a secure sandbox. Its public repository also notes development outside the public tree, so public commit frequency alone is a weak maintenance signal.

### 7. [aengelke/instrew](https://github.com/aengelke/instrew)

**Language / role:** C and C++; LLVM-based dynamic translation and instrumentation using Rellume for lifting.

Instrew offers a distinct architecture: a client executes guest code and manages its code cache, while a separate server lifts instructions, optimizes LLVM IR, and returns generated ELF objects for relocation. The [repository overview](https://github.com/aengelke/instrew) explains the split and its supported guest/host combinations.

- **C2:** This decomposition separates execution, lifting, optimization, code generation, and object loading. It gives researchers an instrumentation path through LLVM IR rather than requiring all transformations to operate directly on machine instructions.
- **C1:** [`server/rewriteserver.cc`](https://github.com/aengelke/instrew/blob/master/server/rewriteserver.cc) shows architecture-specific setup, calling-convention transformations, decoding failure handling, and object-cache keys that incorporate configuration and code content, including address information when required.
- **C3:** The server organizes lifting, optimization, and code generation into separately measured stages. It removes unused IR entities and supports caching, while the README describes calling-convention and call/return choices that trade translation work against execution cost.

Treat it as a research translation framework with explicit coverage limits; the README warns that system-call support can lag newer host libraries.

## Selective instrumentation and historical framework designs

### 8. [srg-imperial/SaBRe](https://github.com/srg-imperial/SaBRe)

**Language / role:** C and assembly; selective runtime binary rewriting for syscall, vDSO, and function interception.

SaBRe belongs at the selective-rewriting end of this category. Its loader and plugins support tracing and fault injection without requiring clients to request instrumentation at every machine instruction.

- **C2:** The [repository architecture discussion](https://github.com/srg-imperial/SaBRe) describes the plugin model and the change from an isolated plugin environment to sharing application libraries in version 2. That change exposes a useful design tradeoff between plugin isolation and access to ordinary allocation and library facilities.
- **C1:** [`plugin_api/recursion_protector.c`](https://github.com/srg-imperial/SaBRe/blob/master/plugin_api/recursion_protector.c) handles recursion through thread-local plugin state. Its initial-exec TLS choice avoids problematic dynamic TLS resolution during thread initialization, and a vDSO readiness guard handles initialization ordering. These are concrete runtime-integration hazards.
- **C3:** The selective interception scope provides an understandable way to limit instrumentation work, though it should not be read as a measured performance claim for every plugin.

The [plugin API notes](https://github.com/srg-imperial/SaBRe/blob/master/plugin_api/README.md) are a useful companion to the recursion implementation, including TLS requirements and integration guidance for non-C plugins.

### 9. [iu-parfunc/liteinst](https://github.com/iu-parfunc/liteinst)

**Language / role:** C++ and C; lightweight probe instrumentation and reusable concurrent code-patching libraries.

LiteInst is a historical research codebase; its public history inspected here ends in 2018. It remains distinctive because it exposes the patching protocols underneath instrumentation rather than hiding them inside a large translator.

- **C1:** [`libpointpatch/src/patcher.c`](https://github.com/iu-parfunc/liteinst/blob/master/libpointpatch/src/patcher.c) handles patches crossing cache-line boundaries and code that other CPUs may be executing. It contains breakpoint gating, a trap handler that completes pending work, compare-and-exchange installation, split writes, and alternative synchronization strategies.
- **C2:** The [repository README](https://github.com/iu-parfunc/liteinst/blob/master/README.md) separates probe providers from instrumentation providers and divides call patching, point patching, instrumentation, and profiling into libraries. Function entry/exit coordinates and selection rules support reusable probe placement.
- **C3:** The repository includes patching microbenchmarks and application-level experiments, while the implementation makes update-protocol alternatives inspectable.

Some compile-time variants deliberately relax synchronization. The existence of these experiments is not evidence that every configuration is safe. The implemented coordinate support is also narrower than the broader future instrumentation model described in the README.

### 10. [Samsung/ADBI](https://github.com/Samsung/ADBI)

**Language / role:** C, Python, and ARM assembly; Android native tracepoint injection with host-side control and an on-device server.

This is a historical Android research framework with sparse public release history, not evidence of broad present-day Android compatibility. Its implementation documents nevertheless give unusually concrete accounts of safe unloading and architecture-specific injected code.

- **C1:** The [stabilization design](https://github.com/Samsung/ADBI/blob/master/doc/STABILIZATION) addresses threads whose program counters remain inside code that must be modified or unloaded. It describes stopping threads, temporarily changing execute permissions, letting unstable threads reach an external fault boundary, and restoring state. It also handles the Linux `READ_IMPLIES_EXEC` interaction with permission changes.
- **C2:** The [ARM template design](https://github.com/Samsung/ADBI/blob/master/doc/ARM_TEMPLATES) describes reusable templates that save registers, invoke C handlers, execute relocated or emulated original instructions, and return to application code. Precompiled templates and symbolic field patching separate instruction mechanics from individual tracepoint handlers.

Study these documents together: generating a correct trampoline and establishing when it is safe to replace or remove it are separate framework responsibilities.

### 11. [Granary/granary](https://github.com/Granary/granary)

**Language / role:** C++ and assembly; historical dynamic translation and instrumentation of Linux kernel modules.

**Archived:** GitHub marks this repository archived. It is useful for kernel instrumentation design, not as an implied supported solution for current kernels. Its scope allows instrumented modules and uninstrumented kernel code to coexist.

- **C2:** The [repository overview](https://github.com/Granary/granary) explains policy-driven instrumentation and selective attachment. Policies can distinguish execution contexts such as critical sections, allowing clients to change instrumentation behavior as control moves between contexts.
- **C1:** [`granary/policy.h`](https://github.com/Granary/granary/blob/master/granary/policy.h) makes those contexts concrete: policy properties include host/application state, register-preservation requirements, user-data access, and transfer type. It distinguishes inherited properties from temporary properties and defines how calls and other transfers propagate state.
- **C3:** Keeping selected kernel code native while translating modules is an architectural way to restrict instrumentation cost and scope. The policy representation also connects contextual decisions to dispatch and code-cache identity.

The policy header is a useful entry point into the engine's invariants. Its presence should not be mistaken for proof that all kernel concurrency and interrupt cases are solved.

### 12. [Granary/granary2](https://github.com/Granary/granary2)

**Language / role:** C++ and assembly; a separate, redesigned x86-64 Linux userspace instrumentation framework.

**Archived:** This is not counted merely as a fork of the preceding repository. It has a distinct userspace design, JIT decoding model, virtual-register machinery, and tool pipeline. The README candidly discusses excessive design complexity and residual constraints from earlier kernel ambitions; its historical toolchain instructions should not be assumed current.

- **C2:** [`granary/tool.h`](https://github.com/Granary/granary2/blob/master/granary/tool.h) separates entry, control-flow, trace, and basic-block instrumentation stages. It defines tool ordering and bounded repeated materialization, while specifying when block instrumentation happens once per instrumentation session.
- **C1:** [`granary/code/register.cc`](https://github.com/Granary/granary2/blob/master/granary/code/register.cc) implements virtual-register allocation and register liveness. Handling partial-register writes requires distinguishing values that are killed from bytes preserved by an aliasing write; the file also exposes set operations and encoding constraints.

This is a valuable design-comparison companion to the original Granary, particularly for readers interested in whether powerful intermediate abstractions justify the complexity they introduce.

## GPU instrumentation

### 13. [matinraayai/Luthier](https://github.com/matinraayai/Luthier)

**Language / role:** C++, LLVM infrastructure, and HIP device code; an evolving AMD GPU instrumentation framework for the ROCm environment.

Luthier adds a substantially different execution architecture to the selection. Its source permits study of instrumentation inside GPU kernels, where register pressure, scratch space, and application-visible device state strongly constrain inserted code. The repository distinguishes implemented capabilities from aims; do not read every listed goal as a mature guarantee.

- **C2:** The [hook insertion design](https://github.com/matinraayai/Luthier/blob/main/docs/hook_insertion.md) connects HIP-written device hooks to LLVM IR embedded in HSA code objects, module loading and caching, and insertion into application code. This offers reusable instrumentation above raw instruction patching.
- **C1:** Hook insertion must preserve live physical registers and application stack behavior. The design explains how register liveness and stack-frame information guide allocation and spilling, and how external global declarations connect copied hook IR to runtime objects.
- **C3:** The same document motivates forced inlining and liveness-aware allocation: ordinary ABI call frames and unnecessary spills can be costly in a GPU kernel. These are architectural performance arguments, not independent benchmark claims.

This entry refers to the framework repository. Its [ISPASS artifact](https://github.com/NUCAR-DEV/luthier-ispass2025) contains a snapshot and experiments and is not counted again as an independent framework.

## Emulation-based instrumentation

These projects instrument translated execution within an emulator. They can offer architecture independence, controlled memory, or whole-system context, at the cost of a different deployment and fidelity model from native process attachment.

### 14. [qemu/qemu](https://github.com/qemu/qemu)

**Language / role:** Primarily C; the **TCG plugin subsystem** inside QEMU's broader emulator monorepo. This GitHub repository is an official substantive mirror; upstream development uses other infrastructure.

QEMU is counted once, specifically for instrumentation of TCG-translated execution. Its plugin interface provides a strong study of callback lifetimes and concurrency in both user-mode and system emulation.

- **C1:** The [TCG plugin documentation](https://www.qemu.org/docs/master/devel/tcg-plugins.html) distinguishes translation from execution and instruction entry from successful memory access. Query handles have callback-scoped lifetimes. Plugin uninstallation is asynchronous, requiring quiescence before callbacks are fully retired.
- **C2:** Plugins can inspect translated blocks and instructions, register execution or memory callbacks, and attach analysis state through an API rather than modifying the translator for each measurement.
- **C3:** The documentation's internals explain RCU-protected callback lists and registration locking. Per-vCPU scoreboards, inline operations, and conditional callbacks reduce shared-state contention and callback overhead.

Start with the lifecycle and internals sections of that guide. Their explicit semantics are essential when interpreting counters or assuming that an instruction observed during translation actually executed.

### 15. [panda-re/panda](https://github.com/panda-re/panda)

**Language / role:** C/C++ with Python interfaces; whole-system dynamic analysis built from QEMU, with record/replay and reusable analysis plugins.

PANDA is retained separately from QEMU because recording, deterministic replay, inter-plugin analysis, taint facilities, and operating-system introspection constitute substantial independent framework work. It is not simply another QEMU mirror.

- **C1:** The [manual's record/replay discussion](https://github.com/panda-re/panda/blob/dev/panda/docs/manual.md) locates nondeterminism at the CPU/RAM boundary, including interrupts and DMA effects. It also documents restrictions on returning to live execution and on scheduling state transitions at safe block boundaries.
- **C2:** The same manual describes callbacks around translation and execution, optional memory callbacks, and plugin infrastructure that supports composing analyses. The [repository overview](https://github.com/panda-re/panda) connects this machinery to taint analysis, introspection, and Python control.
- **C3:** Expensive analyses can operate on a replay rather than imposing all their work during the original interaction. The manual also explains when enabling analysis features requires translated-block cache invalidation, exposing a correctness cost behind apparently simple configuration changes.

Some manual passages describe older QEMU foundations. Use them for the documented design and inspect the relevant current code before drawing version-specific compatibility conclusions.

### 16. [unicorn-engine/unicorn](https://github.com/unicorn-engine/unicorn)

**Language / role:** C engine with multiple bindings; embeddable multi-architecture CPU emulation and instrumentation, derived from QEMU with its own API and evolution.

Unicorn provides CPU and memory execution primitives rather than a complete operating-system environment. It is a useful foundation for clients that supply their own loaders, stubs, execution bounds, and analysis state.

- **C2:** The [hook guide](https://github.com/unicorn-engine/unicorn/blob/master/docs/Hooks.md) describes instruction, block, and memory-related hooks, including address ranges and fault-related events. These abstractions support emulation clients with different observation and intervention needs.
- **C1:** [`tests/unit/test_ctl.c`](https://github.com/unicorn-engine/unicorn/blob/master/tests/unit/test_ctl.c) contains a targeted regression for deleting a hook after translated execution: subsequent runs must clear stale cached references and avoid invoking freed hook state. It also exercises cache controls, callback-directed execution changes, and TLB behavior.
- **C3:** The hook guide discusses the overhead of hook-list dispatch and the importance of appropriate hook granularity and filtering. The cache-control tests make the interaction between translated-code reuse and dynamic instrumentation changes inspectable.

The guide and control tests together are better study entry points than a bindings-only example: they expose both the public mechanism and a concrete failure mode beneath it.

### 17. [qilingframework/qiling](https://github.com/qilingframework/qiling)

**Language / role:** Python; binary-emulation and instrumentation framework providing loaders, operating-system behavior, and ABI services above Unicorn.

Qiling qualifies separately because its loaders, system-call and library emulation, calling-convention machinery, and analysis interfaces are substantial framework functionality. The relevant study is how a CPU emulator becomes a reusable environment for real binaries, rather than Python bindings alone.

- **C2:** [`qiling/core_hooks.py`](https://github.com/qilingframework/qiling/blob/master/qiling/core_hooks.py) multiplexes higher-level handlers over lower-level emulator hooks, with address filtering, handler chaining, and propagation control. This supports analyses without forcing each client to implement hook dispatch.
- **C1:** That implementation captures exceptions crossing Python callbacks, stops emulation, and preserves the failure for the surrounding runtime. It also makes unhandled memory, interrupt, and invalid-instruction events explicit rather than silently accepting them.
- **C1, C2:** [`qiling/os/fcall.py`](https://github.com/qilingframework/qiling/blob/master/qiling/os/fcall.py) abstracts argument access, calling-convention slots, return values, interception, and native-call staging. Variadic arguments and stack cleanup demonstrate why API emulation requires more than assigning a Python function to an address.

These two files are compact entry points into the framework's control-flow and ABI boundaries; individual operating-system models still need their own fidelity assessment.

### 18. [icicle-emu/icicle-emu](https://github.com/icicle-emu/icicle-emu)

**Language / role:** Rust; experimental emulator and fuzzing-oriented DBI framework using SLEIGH-derived p-code, an interpreter, and a JIT.

Icicle adds a distinct implementation language and intermediate representation. Its [repository examples](https://github.com/icicle-emu/icicle-emu) show instrumentation inserting operations into lifted blocks, while the monorepo also provides CPU, memory, environment, and fuzzing integration components.

- **C2:** [`icicle-vm/src/injector.rs`](https://github.com/icicle-emu/icicle-emu/blob/master/icicle-vm/src/injector.rs) defines the `CodeInjector` interface over block groups and p-code. Block and instruction hooks, address selection, and trace collection reuse the same lifted representation across target architectures.
- **C1:** The injector tracks modified blocks and temporary-variable state when changing code. The [instruction-test format](https://github.com/icicle-emu/icicle-emu/blob/master/icicle-test/README.md) pairs instruction bytes and base addresses with initial and expected registers and flags, making relative-address and instruction-semantics assumptions testable. Unspecified outputs are intentionally not checked, an important limit on what such a test establishes.
- **C3:** Inserting operations into the representation consumed by the JIT enables inline instrumentation, while the injector includes bounded trace-storage behavior. The architecture makes instrumentation placement and storage costs visible without requiring a particular speedup claim.

The project describes itself as experimental; the source is particularly suitable for studying an evolving design rather than assuming production-wide architecture coverage.

## Coverage, exclusions, and limitations

Discovery used more than six materially distinct live search angles: general native DBI and binary translation; ARM/AArch64 and RISC-V engines; kernel and kernel-module instrumentation; selective runtime patching and concurrent probes; LLVM lifting; Android injection; Rust and p-code instrumentation; whole-system replay and emulator plugins; and AMD, NVIDIA, and Intel GPU instrumentation. Additional searches excluded familiar engine names and looked for historical research systems, helping uncover LiteInst, Instrew, Granary, Samsung ADBI, and Icicle. Later queries predominantly returned previously found engines, analysis clients, bindings, static rewriters, or artifact snapshots, indicating diminishing returns rather than a reason to pad the list.

Every retained canonical GitHub repository was opened or checked through GitHub metadata. Each also had at least one independently read primary implementation, architecture, API, or test source beyond its repository overview. Source links above are the study entry points; search snippets and star counts were not used as quality evidence. Repository status and public history were checked to distinguish archived or historical material from a supported-platform claim. **C4 is applied only where the cited evidence establishes evolution together with maintenance practices.**

Important exclusions and distinctions:

- **Valgrind:** Its [official repository instructions](https://valgrind.org/downloads/repository.html) identify Sourceware as the development repository. No official substantive GitHub mirror was verified in this search, so unofficial copies were not substituted. This is a hosting-scope exclusion, not a judgment about engineering value.
- **NVIDIA NVBit:** The [official GitHub repository](https://github.com/NVlabs/NVBit) primarily supplies documentation, licensing, and release artifacts rather than the framework engine's tracked implementation. It is relevant to the category but less suitable for this source-code selection. This does not imply that its distribution lacks example-tool source.
- **Intel GTPin artifacts:** The inspected [ISPASS artifact](https://github.com/intel/GTPin-ispass2026) depends on an externally obtained GTPin kit and contains tool and experiment material. It was not treated as the engine implementation. No verified Intel Pin engine-source repository was retained either.
- **Duplication:** Frida's umbrella and bindings, standalone instrumentation clients, Luthier artifact snapshots, and architecture ports already represented in an engine were not counted separately. PANDA, Unicorn, and Qiling have distinct substantive framework layers despite their shared lineage; the two Granary repositories are explicitly separate historical designs.
- **Boundary choices:** Static-only rewriting, managed-bytecode tooling, generic debugger front ends, hardware-trace consumers, and small hook libraries without a substantial instrumentation framework were excluded. Selective rewriting and emulation were retained but separated so readers can choose an appropriate execution model.

This was read-only source research: no candidate code was executed, dependencies installed, performance numbers reproduced, or current-platform compatibility certified. The explanations distinguish documented behavior from architectural inference; in particular, identifying a design that reduces work is not a benchmark result. Branch-based source links may change after the research date, and historical projects may require significant porting before practical use.
