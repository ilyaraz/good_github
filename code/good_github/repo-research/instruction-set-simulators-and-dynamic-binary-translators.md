# Instruction set simulators and dynamic binary translators

Research date: **2026-10-09**.

This selection covers software that executes machine or virtual-ISA instructions through interpretation, dynamic translation, or an executable architectural model. It includes full-system emulators, embeddable CPU engines, application translators, same-ISA instrumentation runtimes, and verification-oriented simulators. Timing simulators qualify where an inspected subsystem also executes instruction semantics. The 27 repositories span desktop, server, microcontroller, historical, and GPU architectures. Each repository heading links to its verified canonical GitHub location; the links beside the criteria are the recommended implementation or documentation entry points.

Criteria used below:

- **C1 — Difficult correctness:** architectural state, numerical semantics, memory ordering, interrupts, exceptions, concurrency, or other demanding failure cases.
- **C2 — Reusable abstractions:** substantial interfaces or models that support different machines, architectures, analyses, or embedding applications.
- **C3 — Performance with structure:** identifiable execution, compilation, scheduling, or caching mechanisms that address real costs.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate complexity management. Age or recent activity alone does not qualify.

The criteria identify useful things to study, not a claim that every component is exemplary or that a simulator implements every corner of its advertised ISA. Maintenance is not inferred from popularity. Explicit archival, mirror, and historical qualifications appear where relevant.

## Full-system execution and architectural simulation

### 1. [qemu/qemu](https://github.com/qemu/qemu)

**Language / role:** Primarily C; multi-architecture system emulation and user-mode binary translation. **Official GitHub mirror:** the repository directs development to QEMU's GitLab infrastructure.

Study the boundary between the Tiny Code Generator (TCG), architectural CPU state, translated blocks, and the software MMU. QEMU makes especially instructive tradeoffs between keeping guest state in host registers and recovering precise state when execution exits unexpectedly.

- **C1:** Translation blocks depend on recorded CPU state; self-modifying code requires page-based invalidation and removal of block chains. Exception handling reconstructs guest state from the faulting host instruction. The [TCG implementation document](https://www.qemu.org/docs/master/devel/tcg.html) explains these invariants alongside direct chaining and memory translation.
- **C2, C3:** The multi-threaded execution design separates per-vCPU translation contexts from shared code and memory structures. Atomic patching, synchronized TLB maintenance, and guest-to-host memory-order mappings expose the cost and correctness boundaries of scalable emulation. See [multi-threaded TCG](https://www.qemu.org/docs/master/devel/multi-thread-tcg.html).

### 2. [renode/renode](https://github.com/renode/renode)

**Language / role:** C# framework with native CPU execution components and Python/Robot testing infrastructure; simulation of embedded systems and networks of machines.

Renode is useful for studying how instruction execution participates in a larger deterministic device model. Its reusable unit is not merely a CPU: firmware, peripherals, buses, and communicating machines share explicit simulated-time relationships. Some implementation components are brought in through submodules.

- **C1:** Time sources grant quanta to time sinks and wait for their completion. Nested time domains constrain how far machines can diverge before synchronizing, and the documentation distinguishes halting a CPU from pausing simulated time. These are concrete consistency rules for multi-machine execution. See the [time framework](https://renode.readthedocs.io/en/latest/advanced/time_framework.html).
- **C2, C3:** Hierarchical time sources compose CPUs, peripherals, and machine groups while allowing different synchronization granularities. The same framework supports the architecture and board families described in the [repository overview](https://github.com/renode/renode/blob/master/README.md). Configured MIPS and time quanta are simulation controls, not a claim of cycle-accurate microarchitecture modeling.

### 3. [gem5/gem5](https://github.com/gem5/gem5)

**Language / role:** C++, Python, and ISA-description machinery; execution-driven computer architecture simulation.

The relevant subsystem is gem5's CPU execution model and its interface to ISA semantics. It provides a particularly clear comparison between an architectural instruction and the dynamic instances of that instruction moving through a speculative processor.

- **C1:** `DynInst` carries runtime state such as renamed registers and speculation information. Externally changing a thread's architectural state can require flushing an out-of-order pipeline; split memory operations must preserve instruction semantics across execution stages.
- **C2, C3:** `StaticInst` holds decoded, reusable instruction behavior, while `ExecContext` supplies the particular CPU's execution environment. This lets different CPU models reuse an ISA implementation. Caching decoded static instructions also avoids repeated decoding. The [execution basics guide](https://www.gem5.org/documentation/general_docs/cpu_models/execution_basics) develops all three interfaces and their performance consequences.

### 4. [open-simh/simh](https://github.com/open-simh/simh)

**Language / role:** C; a collection and common framework for historical computer simulators, including PDP and VAX families.

This is the Open SIMH project line, whose [repository overview](https://github.com/open-simh/simh/blob/master/README.md) explains its separate governance since 2022. Only this SIMH lineage is counted here. Its value is the architecture shared by many individual machine simulators, rather than a single modern JIT.

- **C1:** A simulator's instruction loop decrements the event interval and processes scheduled device activity at defined boundaries. Interrupt delivery, canceled events, breakpoints, and stopped execution must remain consistent with that model.
- **C2, C3:** The common `DEVICE`, `UNIT`, and `REG` structures separate machine-specific behavior from simulator control, event queues, inspection, and device services. The framework also exposes when idle-time advancement is permissible. The [SIMH implementation manual](https://opensimh.org/simdocs/simh.html) is the substantive entry point for these interfaces and scheduling rules.

### 5. [bochs-emu/Bochs](https://github.com/bochs-emu/Bochs)

**Language / role:** C++; portable x86 PC emulation through software instruction execution.

Bochs offers a contrasting study to cross-ISA JITs: a detailed interpreter must still organize fast instruction dispatch around precise architectural stops, debugger behavior, and virtualization-related exceptions.

- **C1:** The [CPU execution loop](https://github.com/bochs-emu/Bochs/blob/master/bochs/cpu/cpu.cc) handles asynchronous events, architectural instruction-pointer commitments, exception recovery, and debugger boundaries. Its instruction-handler chaining must yield at the right points for single stepping and event processing.
- **C4:** The [change history](https://github.com/bochs-emu/Bochs/blob/master/bochs/CHANGES) documents work across the 2020, 2021, and 2026 release periods on VMX/SVM behavior, CPU capabilities, decoder/disassembler consolidation, save/restore, and instruction-level fixes. This is evidence of sustained compatibility and complexity management, rather than age alone.

### 6. [SDL-Hercules-390/hyperion](https://github.com/SDL-Hercules-390/hyperion)

**Language / role:** C; the SDL Hercules branch emulating IBM System/370, ESA/390, and z/Architecture systems.

Study how related architectural generations share a CPU implementation while retaining incompatible details of program status words, addressing modes, and interruption behavior. The mainframe workload makes privileged state transitions as interesting as ordinary instruction arithmetic.

- **C1:** The architecture-dependent PSW load path validates reserved bits and mode combinations, selects address masks, and returns specification exceptions for invalid state. It also invalidates cached instruction-address information. These details are visible in [cpu.c](https://github.com/SDL-Hercules-390/hyperion/blob/master/cpu.c).
- **C2:** Architecture-parameterized CPU routines and the reusable test runner support more than one machine generation. Tests combine assembly programs, emulator scripts, reusable subtests, and automated output verification. The [test framework guide](https://github.com/SDL-Hercules-390/hyperion/blob/master/tests/README.md) explains how to isolate and reproduce architectural behaviors.

### 7. [gpgpu-sim/gpgpu-sim_distribution](https://github.com/gpgpu-sim/gpgpu-sim_distribution)

**Language / role:** C++; GPU architectural simulation with a functional PTX instruction-execution subsystem.

The category fit is specifically the PTX virtual-ISA executor in `src/cuda-sim`, coupled to GPU timing models. This is distinct from treating every SASS trace-driven mode in the surrounding ecosystem as an instruction emulator. The [repository overview](https://github.com/gpgpu-sim/gpgpu-sim_distribution/blob/dev/README.md) describes that ecosystem and execution modes.

- **C1:** PTX execution checks correspondence between functional and timing PCs, applies active masks and predicates, and coordinates barriers and SIMT reconvergence. Warp-wide operations require special handling to prevent an operation being applied independently by every lane.
- **C2, C3:** The functional core, instruction dispatch, warp state, and timing-facing instruction information are separated. In particular, warp-wide operations can execute once for the warp, while functional warp scheduling explicitly manages runnable and barrier-blocked work. Study `ptx_thread_info::ptx_exec_inst`, `functionalCoreSim::execute`, and `executeWarp` in [cuda-sim.cc](https://github.com/gpgpu-sim/gpgpu-sim_distribution/blob/dev/src/cuda-sim/cuda-sim.cc).

## Application translators, portable execution, and JIT libraries

### 8. [FEX-Emu/FEX](https://github.com/FEX-Emu/FEX)

**Language / role:** C++; x86 and x86-64 application translation for AArch64 Linux systems.

FEX is a useful study of the interaction between a compiler-like translation pipeline and the operating-system behaviors expected by real binaries. Native library thunks, guest signals, and CPU translation are related but separately organized concerns.

- **C2, C3:** The [source outline](https://github.com/FEX-Emu/FEX/blob/main/docs/SourceOutline.md) connects decoding, IR construction, optimization passes, register allocation, AArch64 emission, and library thunks. Flag elimination and the division between guest front end and host back end make performance work navigable.
- **C1:** A signal arriving while the translator holds an internal lock can reenter code that needs the same lock. The [deferred-signals design](https://github.com/FEX-Emu/FEX/blob/main/docs/DeferredSignals.md) explains nested deferral regions and a protected-page mechanism, including asynchronous/synchronous distinctions and limits involving recursion and nonlocal control flow. It is valuable precisely because the correctness assumptions are explicit.

### 9. [ptitSeb/box64](https://github.com/ptitSeb/box64)

**Language / role:** C; x86-64 Linux application emulation, including dynamic recompilers for ARM64, RISC-V, and LoongArch hosts.

Study how a practical translator manages x86's implicit flags and instruction boundaries within a shared native-translation framework. The project also integrates native-library wrapping, but the strongest inspected evidence here is in the recompilation machinery.

- **C1:** Partial, pending, and live x86 flags require backward propagation through control-flow predecessors; barriers and native flag state constrain which computations may disappear. Generated instructions must also become visible to the host instruction cache. These mechanisms appear in [dynarec_native.c](https://github.com/ptitSeb/box64/blob/main/src/dynarec/dynarec_native.c).
- **C3:** The same file builds branch relationships and computes flag requirements before emission, reducing work for values that successors do not need. The [dynarec source tree](https://github.com/ptitSeb/box64/tree/main/src/dynarec) shows how shared analysis coexists with host-specific emitters, making it useful for comparing translation decisions across host ISAs.

### 10. [jart/blink](https://github.com/jart/blink)

**Language / role:** C11; x86-64 Linux binary execution on POSIX systems, with interpreter and JIT execution paths and a terminal debugger.

Blink is a relatively compact place to study the executable-memory infrastructure beneath a translator. Its low-level JIT builder composes native sequences and helper calls while accommodating different host executable-memory policies.

- **C1:** Code publication involves instruction-cache synchronization, staged hooks where immediate executable publication is unavailable, and generation counters for detecting concurrent updates. Completing or abandoning a JIT block also has to handle allocation and competing-compilation cases. See [jit.c](https://github.com/jart/blink/blob/master/blink/jit.c).
- **C3:** The same module manages reusable code blocks, generated call sequences, hooks, and jump splicing rather than paying a full interpreter dispatch cost for every guest instruction. The [README](https://github.com/jart/blink/blob/master/README.md) explains interpreter/JIT availability and portable test workflows. Its documented x87 precision and Linux-API limitations matter when choosing compatibility workloads; benchmark superlatives are not used as evidence here.

### 11. [copy/v86](https://github.com/copy/v86)

**Language / role:** Rust CPU core and JavaScript integration/device code; browser-capable x86 emulation through WebAssembly translation.

The main lesson is how an unstructured guest instruction stream becomes structured WebAssembly under browser compilation and module-management constraints. The project describes a 32-bit x86 machine; it should not be selected as a general x86-64 or multicore emulator.

- **C1:** A software TLB distinguishes ordinary memory access from MMIO, protection faults, and writes to translated code. Lazy arithmetic flags must be materialized when an instruction needs them. These mechanisms preserve semantic boundaries despite aggressive caching.
- **C3:** The [implementation guide](https://github.com/copy/v86/blob/master/docs/how-it-works.md) explains interpreter hotness tracking, page-oriented compilation, two-pass block discovery, and a stackifier that turns control-flow graphs into structured Wasm. It also discusses the tradeoff between compilation granularity and module overhead. Consult the [repository](https://github.com/copy/v86) for explicit CPU and floating-point compatibility limits.

### 12. [lioncash/dynarmic](https://github.com/lioncash/dynarmic)

**Language / role:** C++20; embeddable A32/A64 dynamic recompilation, with x86-64 and AArch64 host support described by the repository. **Archived on 2024-03-12.**

Dynarmic remains a substantive historical study of an emulator-oriented JIT library. The design document is older than some of the repository's eventual architecture coverage, so its introductory scope should not be mistaken for a complete final feature matrix.

- **C1:** The IR makes flag results explicit and distinguishes guest semantics that do not map directly to host operations. ARM shift-count behavior versus x86 masking is one concrete example. Basic-block terminal forms make control-flow and guest-PC transitions explicit.
- **C2, C3:** Typed SSA instructions, optimization stages, host back ends, and user callbacks separate translation from the embedding application's memory system. The [design document](https://github.com/lioncash/dynarmic/blob/master/docs/Design.md) is the main study entry point; the [repository page](https://github.com/lioncash/dynarmic) supplies archival status and library scope. It is not presented as a currently maintained dependency recommendation.

### 13. [michalsc/Emu68](https://github.com/michalsc/Emu68)

**Language / role:** Primarily C; bare-metal Motorola 68k dynamic translation for ARM hardware, notably PiStorm integrations.

Emu68 exposes unusually concrete controls over translation-cache policy and legacy-software compatibility. Its instruction behavior should not be confused with exact reproduction of one physical 68040 microarchitecture.

- **C1:** A soft cache flush marks translation units for later checksum verification; changes to source instructions decide whether code can be reused. Condition-code lookahead can conflict with self-modifying software, so the implementation exposes a way to disable that optimization. These assumptions and controls are described in [the internal control-register documentation](https://michalsc.github.io/Emu68/internals/ControlRegisters.html).
- **C3:** Translation-unit size, branch/loop inlining, soft-to-full-flush thresholds, and deliberate slowdown for old timing loops expose actual speed-versus-compatibility choices. The [configuration reference](https://michalsc.github.io/Emu68/Options.html) connects those mechanisms to deployed firmware settings. This is especially useful alongside portable desktop translators because bare-metal integration changes the execution and compatibility constraints.

## Reusable execution and dynamic-analysis engines

### 14. [unicorn-engine/unicorn](https://github.com/unicorn-engine/unicorn)

**Language / role:** C execution core with multiple language bindings; embeddable, multi-architecture CPU emulation derived from QEMU.

Unicorn qualifies separately from QEMU because its CPU-only API, hooks, memory management, and execution-control contract form a substantial independent interface. It does not supply an operating system merely by executing that operating system's ISA.

- **C1:** An unmapped-memory hook must actually repair the mapping before requesting continued execution. Host-side changes to translated code require appropriate cache removal and execution-state handling; guest self-modification follows a different path. MMU configurations also distinguish physical mappings from virtual execution addresses.
- **C2, C3:** Embedders can compose instruction or block hooks, guest memory, CPU state, and controlled execution without adopting a complete machine emulator. The [FAQ](https://github.com/unicorn-engine/unicorn/blob/master/docs/FAQ.md) explains these contracts, program-counter visibility, and why instruction-level instrumentation costs more than block-level instrumentation. Its version-qualified behavior should be checked when embedding a particular release.

### 15. [DynamoRIO/dynamorio](https://github.com/DynamoRIO/dynamorio)

**Language / role:** C/C++; dynamic binary instrumentation and same-ISA translation runtime.

This entry broadens the category beyond cross-architecture emulation. DynamoRIO translates and controls an application's instruction stream so that clients can instrument execution without recompiling the application.

- **C2:** The client interface exposes instruction-stream manipulation and runtime events while the core owns code-cache construction and application control transfer. That separation supports profiling, tracing, analysis, and transformation tools.
- **C3:** Basic blocks are copied into code caches, linked directly where possible, and combined into hot traces. Indirect branches require lookup machinery, and system-mediated control transfers need separate handling. The [architecture and API introduction](https://github.com/DynamoRIO/dynamorio/blob/master/api/docs/intro.dox) ties these optimizations to runtime structure, making it a good entry point for understanding the overhead of transparent instrumentation.

### 16. [icicle-emu/icicle-emu](https://github.com/icicle-emu/icicle-emu)

**Language / role:** Rust; multi-architecture emulation using SLEIGH-derived p-code, an interpreter, and a Cranelift JIT, with fuzzing-oriented instrumentation.

Icicle is valuable for studying a semantic intermediate representation that supports both execution and inserted analyses. Its decomposition into CPU, memory, VM, JIT, and fuzzing components is materially different from adding a few hooks to a fixed-ISA interpreter.

- **C2:** Instrumentation can inject p-code into translated blocks, so analyses operate above individual host instruction encodings. The [repository guide](https://github.com/icicle-emu/icicle-emu/blob/master/README.md) shows this interface and the component boundaries.
- **C1, C3:** The [JIT implementation](https://github.com/icicle-emu/icicle-emu/blob/master/icicle-jit/src/lib.rs) maintains compiled groups and fast entry-point caches. Invalidating a group removes its dependent mappings; reset explicitly invalidates previously obtained native function pointers. These lifetime rules make a concrete case study in keeping fast dispatch consistent with changing translated code.

### 17. [cea-sec/miasm](https://github.com/cea-sec/miasm)

**Language / role:** Python and C; binary analysis framework with executable instruction semantics and JIT execution in `miasm/jitter`.

The relevant subsystem is the Jitter engine, not merely Miasm's disassembler. The same architecture descriptions and intermediate representations participate in lifting, execution, and other analyses, allowing an engineer to study where semantics can be shared and where execution needs additional machinery.

- **C2:** The common machine abstraction connects disassembly, lifting, and execution across supported architectures. The [README and worked examples](https://github.com/cea-sec/miasm/blob/master/README.md) show these relationships rather than treating each analysis as an unrelated front end.
- **C1, C3:** [jitcore.py](https://github.com/cea-sec/miasm/blob/master/miasm/jitter/jitcore.py) manages a bounded translation cache and address-interval metadata. Invalidating code must remove compiled blocks and associated lifted-IR mappings; memory writes and block boundaries therefore affect more than one representation. This is a readable study of self-modifying-code consistency in an analysis-oriented executor.

### 18. [panda-re/panda](https://github.com/panda-re/panda)

**Language / role:** C/C++ with Python interfaces; QEMU-derived whole-system execution, deterministic record/replay, and dynamic analysis.

PANDA is retained separately for its substantial replay and analysis architecture. The reusable object is an execution recording on which different analyses can run, often at a cost that would be impractical during live interaction.

- **C1:** Replay records nondeterministic influences crossing the CPU/RAM boundary, including interrupts and DMA-related effects, rather than simply recording high-level device inputs. The [record/replay design](https://github.com/panda-re/panda/blob/dev/panda/docs/manual.md#recordreplay-details) also explains why replay does not reconstruct all device state needed to resume ordinary live execution.
- **C2, C3:** Plugins compose instruction, memory, and OS-level analyses; plugin-to-plugin events address cases where ordinary callback ordering is insufficient. Replaying a recording decouples expensive analysis from the original interaction's timing. See the [plugin architecture](https://github.com/panda-re/panda/blob/dev/panda/docs/manual.md#plugin-architecture). The manual contains historical version details, so its architecture discussion is not treated as a current all-ISA support guarantee.

## RISC-V and OpenRISC execution, reference models, and co-simulation

### 19. [riscv-software-src/riscv-isa-sim](https://github.com/riscv-software-src/riscv-isa-sim)

**Language / role:** Primarily C++; Spike, a functional RISC-V ISA simulator and reference implementation.

Spike is particularly useful for following architectural instruction execution through traps, debugging, and retirement. It is a functional reference rather than a model of a particular processor's pipeline timing.

- **C1:** The execution loop distinguishes instruction completion, serialization requests, triggers, interrupts, and traps. Logging partially completed vector memory operations requires care around exceptions. See [riscv/execute.cc](https://github.com/riscv-software-src/riscv-isa-sim/blob/master/riscv/execute.cc).
- **C3:** The same implementation separates a cached fast dispatch path from a slower path needed for tracing and debugging. The [repository guide](https://github.com/riscv-software-src/riscv-isa-sim/blob/master/README.md) explains extension implementation and scope: sequentially consistent execution is compatible with the architectural memory models but does not enumerate every weak-memory behavior, and the C++ interface is not promised as a stable public API.

### 20. [riscv/sail-riscv](https://github.com/riscv/sail-riscv)

**Language / role:** Sail specification with generated compiled simulator infrastructure; executable RISC-V architectural semantics.

This is a different design point from a hand-optimized interpreter: a shared semantic model produces executable artifacts and material for formal reasoning. The generated simulator establishes category fit; the model itself is the central engineering artifact.

- **C2:** The [project architecture and build guide](https://github.com/riscv/sail-riscv/blob/master/README.md) describes a common model used for a compiled emulator, configuration/schema generation, documentation, and formal tooling. This is a substantive example of reusing instruction semantics across execution and specification work.
- **C1:** The [test guide](https://github.com/riscv/sail-riscv/blob/master/test/README.md) distinguishes first-party regressions, architectural tests, hypervisor tests, and vector configurations with different VLEN/ELEN combinations. Those dimensions expose privileged and numerical corner cases that a single fixed machine configuration could miss. Passing such tests is evidence of a verification strategy, not a proof that every modeled behavior is correct.

### 21. [chipsalliance/dromajo](https://github.com/chipsalliance/dromajo)

**Language / role:** C/C++; RV64 functional model used for RTL co-simulation, with substantial development from TinyEMU ancestry.

Dromajo's distinctive purpose is comparing a hardware implementation's architectural behavior with a software model while supporting boot and checkpoint workflows. The GitHub metadata inspected showed its last push in November 2024; it is included for study value without a claim of ongoing maintenance.

- **C1:** The [co-simulation implementation](https://github.com/chipsalliance/dromajo/blob/master/src/dromajo_cosim.cpp) handles interrupt/exception alignment and known nondeterministic results, including MMIO, counters, and store-conditional outcomes. Some values are deliberately supplied by the device under test, so those paths are not independent oracle checks.
- **C2:** The [integration overview](https://github.com/chipsalliance/dromajo/blob/master/README.md) describes a library interface and checkpoint-based workflows that let RTL environments reuse the architectural model. Together with the comparison loop, this is useful for understanding both the power and the blind spots of differential verification.

### 22. [sysprog21/rv32emu](https://github.com/sysprog21/rv32emu)

**Language / role:** C; RV32 emulation with interpreter, template-based native translation, and an LLVM optimization tier.

Despite its educational accessibility, this is a substantial implementation with real tiering and architectural test integration. Study how it decides when extra compilation is worthwhile and how native execution returns safely to shared emulator state.

- **C3:** The [code-generation design](https://github.com/sysprog21/rv32emu/blob/master/docs/codegen.md) explains tail-call interpreter dispatch, first-tier emission, hot-region LLVM compilation, and register promotion. Tiering gives cold code a cheaper path while allowing frequently executed regions more optimization.
- **C1:** Register spill/refill around callbacks and bounded translated regions preserve state and interrupt opportunities. The design explains why some target-prediction behavior is disabled in system mode. The [RISCOF testing guide](https://github.com/sysprog21/rv32emu/blob/master/docs/riscof.md) documents signature comparison against Sail-derived reference results across instruction-extension configurations, while explicitly warning that architectural tests do not replace full verification.

### 23. [libriscv/libriscv](https://github.com/libriscv/libriscv)

**Language / role:** C++; RISC-V execution library for embedding guest programs and callable guest functions in host applications.

This project is useful for studying the boundary between an instruction engine and a language-runtime-like embedding API. Calls across that boundary must reconcile host objects, guest addresses, register conventions, and memory lifetime.

- **C1, C2:** The [VM-call guide](https://github.com/libriscv/libriscv/blob/master/docs/VMCALL.md) explains argument placement, floating-point registers, structures copied to the guest stack, split RV32 values, and return-value limitations. It also describes guest-address and object-lifetime pitfalls. These are concrete contracts for reusable host/guest calls.
- **C3:** The [integration guide](https://github.com/libriscv/libriscv/blob/master/docs/INTEGRATION.md) exposes choices among memory arenas, page traps, dispatch approaches, and translation support. Floating-point configuration and experimental execution options affect semantics and suitability. This entry does not infer a blanket hostile-code isolation guarantee from the project's sandbox terminology.

### 24. [larkmjc/rv8](https://github.com/larkmjc/rv8)

**Language / role:** C++; RISC-V interpreter and RISC-V-to-x86-64 dynamic translator. **Historical implementation:** the inspected GitHub metadata showed a last push in February 2022, and the documentation references an older privileged-ISA revision.

Use the verified canonical repository above rather than assuming older owner names in articles are current. rv8 is retained for its compiler and metadata architecture, not as a current RISC-V conformance recommendation.

- **C2:** The [repository design overview](https://github.com/larkmjc/rv8/blob/master/README.md) describes instruction metadata reused to generate decoding, interpretation, disassembly, and documentation. This provides a useful contrast with executable specifications such as Sail.
- **C3:** The translator combines hot traces and cached native entry points with interpreter fallbacks for parts of the ISA. The parameterized processor/tracer/emitter arrangement, trace caches, load/store helpers, and branch fixups can be followed in [jit-runloop.h](https://github.com/larkmjc/rv8/blob/master/src/jit/jit-runloop.h). Its historical value is the organization of a hybrid engine, not an unsupported modern performance claim.

### 25. [openrisc/or1ksim](https://github.com/openrisc/or1ksim)

**Language / role:** C; OpenRISC 1000 instruction-set and full-system simulation. The inspected default branch is `or1k-master`.

or1ksim adds an architecture family and an integration style that are easy to miss in searches dominated by x86 and RISC-V. Its library interface connects instruction execution to external memory models and SystemC-style simulation environments.

- **C1, C2:** The embeddable run loop accounts for cycles and memory cycles, lets an external upcall shorten a run to synchronize with its parent environment, and stages external interrupt changes. These interfaces and timing constraints are concrete in [libtoplevel.c](https://github.com/openrisc/or1ksim/blob/or1k-master/libtoplevel.c).
- **C1:** The [NEWS history](https://github.com/openrisc/or1ksim/blob/or1k-master/NEWS) documents SoftFloat integration, exception and arithmetic corrections, instruction-cache/breakpoint interactions, and DejaGNU test integration. It helps identify correctness-sensitive subsystems to read next; it is not used alone to claim current maintenance or complete architectural accuracy.

## Microcontroller and classic CPU cores

### 26. [buserror/simavr](https://github.com/buserror/simavr)

**Language / role:** C; AVR microcontroller execution with peripheral models, firmware loading, debugging, and waveform-oriented inspection.

simavr is a useful smaller-scale counterpoint to desktop emulators: faithfully executing firmware requires interrupts, timers, sleep states, and peripherals to agree on more than opcode results.

- **C1:** The interrupt subsystem distinguishes a raised flag from an enabled interrupt, avoids duplicate pending entries, wakes sleeping CPUs under the appropriate conditions, and manages pending/running state and return-from-interrupt behavior. Study [sim_interrupts.c](https://github.com/buserror/simavr/blob/master/simavr/sim/sim_interrupts.c).
- **C2:** Reusable peripheral and IRQ interfaces support board models, while ELF metadata describes firmware settings and VCD tracing exposes interactions over simulated time. The [repository guide](https://github.com/buserror/simavr/blob/master/README.md) explains the relationship between firmware, cores, external components, tracing, and debugging. These facilities make it useful beyond a standalone instruction-loop example.

### 27. [kstenerud/Musashi](https://github.com/kstenerud/Musashi)

**Language / role:** C; embeddable Motorola 680x0 CPU emulation.

Musashi isolates the classic problem of implementing a reusable CPU inside someone else's memory map, interrupt controller, and machine timing loop. Its historical change log is also a compact record of how seemingly local instruction fixes affect exception frames and CPU-generation differences.

- **C1, C2:** The [public CPU interface](https://github.com/kstenerud/Musashi/blob/master/m68k.h) separates CPU selection, execution, and host callbacks. Interrupt acknowledgement distinguishes autovectors from spurious interrupts, and level-7 interrupt handling has edge-sensitive semantics. These contracts give embedders flexibility while leaving explicit responsibilities at the host boundary.
- **C4:** The [history](https://github.com/kstenerud/Musashi/blob/master/history.txt) records evolution across 1998–2002 involving generated instruction code, signed arithmetic, timing, exception PCs, and 68020 stack frames, followed by later licensing history. This supports a sustained historical compatibility criterion; it does not by itself establish the present maintenance level or uniform accuracy across every supported CPU.

## Coverage, search process, and limitations

Discovery used live web searches followed by opened GitHub repository pages or GitHub API responses and additional primary-source reading. Search formulations covered more than six independent angles: multi-architecture full-system execution and TCG internals; x86-on-ARM/RISC-V application translators; embeddable CPU and ARM JIT libraries; Rust/SLEIGH engines for firmware fuzzing; RISC-V reference, formal, and RTL co-simulation models; browser/WebAssembly recompilation; AVR and 680x0 CPU cores; PDP/VAX and IBM mainframe simulation; OpenRISC library integration; and GPU PTX functional execution. Follow-up searches for lesser-known translators and alternative ISA families increasingly returned already represented designs, small teaching implementations, or candidates without sufficiently strong inspected primary evidence.

The list extends modestly beyond 25 because bare-metal 68k translation, OpenRISC, GPU instruction execution, executable formal models, and same-ISA instrumentation add distinct execution architectures. QEMU, Unicorn, and PANDA share ancestry but are retained for separately substantial translator, embedding, and replay/analysis designs. Dromajo's co-simulation layer likewise provides distinct study value beyond its TinyEMU ancestry. SIMH lineages are counted only once, and each larger repository is counted once even when it contains several CPU models or execution subsystems.

Excluded classes include proprietary-only translators and simulators, hardware-virtualization-only projects, disassemblers or lifters without an inspected execution subsystem, trace-only timing models, thin bindings, generated wrappers, repository lists, and tutorial-scale duplicates. Projects hosted elsewhere were not added merely because unofficial GitHub copies exist. This report does not attempt a separate survey of every console emulator or every historical CPU core.

Every retained repository has an inspected canonical GitHub location and at least one additional primary source beyond its landing page; architectural evidence comes from implementation files or substantive design/API documents. Linked documentation and branch URLs are mutable snapshots, and several projects explicitly carry old design or compatibility notes. Archive status and the two stated last-push dates were checked, but a full maintainer-responsiveness audit was outside scope. No repositories were built, benchmarked, cloned, or executed. Statements about code mechanisms are documentary findings; recommendations about what an engineer can learn are grounded interpretations of those findings. No numerical speed claim or comprehensive conformance claim is made.
