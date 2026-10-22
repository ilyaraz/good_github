# Full-system emulators

Research date: **2026-10-09**.

This report selects **24 GitHub repositories** that implement complete computers or embedded boards: processors together with memory, interrupts, buses, and enough devices to execute guest operating systems or unchanged firmware. It includes functional emulators, timing-oriented system simulators, and historical computer preservation projects. For mixed-purpose repositories, only the full-system subsystem is in scope. CPU-only libraries, userspace syscall emulators, hypervisor-only implementations, emulator frontends, and software collections are excluded. Dedicated console emulators are not exhaustively surveyed; the emphasis is general-purpose computers and embedded systems.

These are study recommendations grounded in inspected documentation and source, not assertions that every component is exemplary or every machine model is complete. Criterion judgments are engineering inferences from the specific evidence below. No performance benchmarks were run.

**Criteria legend**

- **C1 — Difficult correctness:** architectural invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and components that support multiple devices, machines, or integration scenarios.
- **C3 — Performance with structure:** concrete performance constraints addressed through understandable implementation boundaries.
- **C4 — Sustained evolution:** documented changes across years together with compatibility, testing, or complexity management. Age alone does not qualify.

## General frameworks and embedded boards

### 1. [qemu/qemu](https://github.com/qemu/qemu)

**Language/role:** Primarily C, with supporting languages; multi-architecture machine emulator. **Official GitHub mirror**; upstream development is hosted on GitLab. The relevant subsystem is system-mode emulation with TCG, rather than Linux/BSD userspace emulation or a hardware-virtualization-only configuration.

Study the boundary between translated CPU execution and shared machine state. The [multi-threaded TCG design](https://www.qemu.org/docs/master/devel/multi-thread-tcg.html) is an unusually concrete account of how a once-serial emulator becomes concurrent.

- **C1:** Translation-block invalidation must undo direct jump links, update lookup structures, and coordinate with other vCPUs. Cross-vCPU TLB flushes, guest memory ordering, and guest atomic operations introduce separate correctness obligations. The design documents both mechanisms and remaining limitations.
- **C3:** Per-vCPU translation contexts, atomic jump-cache updates, concurrent hash lookups, and a SoftMMU fast path reduce contention and exits from generated code. These optimizations are explained alongside the synchronization they require, rather than presented as an unsupported speed claim. Both criteria are supported by the linked design document.

### 2. [gem5/gem5](https://github.com/gem5/gem5)

**Language/role:** C++ and Python; computer architecture simulator with full-system and syscall-emulation modes. This entry concerns **full-system mode**, where guest firmware, kernels, and devices participate in the simulation.

Study how a research simulator separates configurable component composition from memory-transaction semantics. Its [memory-system documentation](https://www.gem5.org/documentation/general_docs/memory_system/) distinguishes requests, packets, ownership, and access modes; the [component guide](https://github.com/gem5/website/blob/stable/_pages/documentation/learning_gem5/part1/part1_3_more_complex_config.md) explains boards, processors, cache hierarchies, and memory systems.

- **C1:** Timing requests require backpressure and retry handling; functional accesses must reconcile with queued packets; packet lifetimes differ between timing and immediate accesses. Getting these wrong can change simulated results, not merely slow the simulator.
- **C2:** Parameterized C++ models are assembled through Python components and port connections. CPU models, interconnects, caches, and memory controllers can be recombined without bespoke interfaces between every pair. Some terminology in the older memory document predates current APIs, so use it for the protocol concepts and follow the current component guide for configuration.

### 3. [renode/renode](https://github.com/renode/renode)

**Language/role:** C# framework with C CPU translation components and scripting; embedded SoC, board, and multi-node network emulation. The repository assembles infrastructure submodules, platform descriptions, scripts, and tests; these are counted as one project.

Study reproducible virtual-time coordination and the interface between CPU memory accesses and peripheral models.

- **C1:** A time source grants execution quanta to sinks, waits for their completion, and processes inter-node communication at synchronization points when nodes are stopped. This explicitly addresses ordering across independently executing simulated machines. See the [time framework](https://renode.readthedocs.io/en/latest/advanced/time_framework.html).
- **C2:** Peripheral models implement access-width interfaces and register semantics behind a common system bus. The guide explains why translating one access into several smaller accesses can break read-to-clear registers and FIFOs. **C3:** Ordinary mapped-memory accesses stay in C, while peripheral accesses cross into C#, making the performance boundary visible. See the [peripheral modeling guide](https://renode.readthedocs.io/en/latest/advanced/writing-peripherals.html).

### 4. [mamedev/mame](https://github.com/mamedev/mame)

**Language/role:** C++; broad machine-preservation framework. The relevant subsystems include complete computer and workstation drivers, alongside the repository's arcade and console machines; this monorepo counts once.

Study how common device interfaces support many unrelated processors and buses without erasing hardware-specific behavior.

- **C1:** An interruptible CPU may have to suspend in the middle of an instruction, undo the cycle charge for an aborted memory access, and reissue exactly that access on resumption. The [CPU-device specification](https://docs.mamedev.org/techspecs/cpu_device.html) makes these obligations explicit and describes generated normal/restart execution paths.
- **C2:** Devices describe multiple address spaces, while machine configurations connect their address maps. Separate opcode spaces accommodate instruction decryption independently of data reads. See the [device memory interface](https://docs.mamedev.org/techspecs/device_memory_interface.html). Support and accuracy vary by individual machine driver.

### 5. [buserror/simavr](https://github.com/buserror/simavr)

**Language/role:** C; AVR microcontroller and board simulation, including timers, serial interfaces, GPIO, and external peripheral models. Its complete-board examples run the same firmware binaries as their physical counterparts; the inclusion is for board emulation, not merely instruction stepping.

Study a relatively small event and wiring framework that lets firmware drive a virtual circuit.

- **C1:** IRQ hooks have explicit initialization-order requirements and deliberately unspecified callback order. Cycle timers account for instructions that overshoot a scheduled deadline and may need repeated callbacks to catch up. See [IRQ contracts](https://github.com/buserror/simavr/blob/master/simavr/sim/sim_irq.h) and [cycle-timer contracts](https://github.com/buserror/simavr/blob/master/simavr/sim/sim_cycle_timers.h).
- **C2:** The same IRQ objects connect pins, peripheral notifications, and external board models; timer callbacks provide reusable periodic and one-shot behavior. This is a useful study of composing firmware-visible hardware without embedding every board into the CPU interpreter. The README distinguishes established support for smaller flash configurations from preliminary support for larger parts.

## PC emulators: accuracy, browsers, and managed runtimes

### 6. [bochs-emu/Bochs](https://github.com/bochs-emu/Bochs)

**Language/role:** C++; complete x86 PC emulation with CPU, BIOS, memory, and I/O devices, capable of running guest operating systems.

Study simulator lifecycle and state management across configurable PC hardware. The [emulator-object developer guide](https://bochs.sourceforge.io/doc/docbook/development/emulator-objects.html) explains the simulator interface, CPU objects, parameter tree, and device save/restore methods.

- **C1:** GUI/configuration interactions distinguish synchronous requests from queued asynchronous events. Restoring disk-image state requires format/coherency checks and reopening the underlying image; devices may need post-restore repair such as forcing a display refresh.
- **C2:** A typed parameter tree supports configuration, generated menus, validation, and shadow references for saved device state. The same simulator interface serves configuration frontends, debugging, event handling, and snapshots. The guide also candidly explains macro-based static-method optimizations, making this valuable for studying architectural tradeoffs rather than uniformly clean modern C++.

### 7. [86Box/86Box](https://github.com/86Box/86Box)

**Language/role:** Primarily C with C++ UI/platform code; low-level emulation of historical IBM PCs and compatibles, including numerous motherboard, chipset, and expansion-card combinations.

Study how an emulator manages a large hardware-compatibility matrix while retaining a distinct execution engine. This is a substantive PCem-derived project; PCem and close derivatives are not separately counted here.

- **C2:** The [device registry](https://github.com/86Box/86Box/blob/master/src/device.c) handles device descriptors, instances, private state, initialization, and configuration migration. It reserves an instance before chained device creation, preventing a child from selecting its parent's in-progress identifier.
- **C3:** The [new code generator's IR compiler](https://github.com/86Box/86Box/blob/master/src/codegen_new/codegen_ir.c) separates micro-operations, register allocation, backend emission, loop unrolling, and jump patching. Register renaming and dead-value handling coexist with explicit flush/invalidation barriers, providing concrete optimization code to examine.

### 8. [copy/v86](https://github.com/copy/v86)

**Language/role:** Rust and JavaScript/WebAssembly; browser-hosted x86 PC with storage, display, interrupts, and networking devices that boots guest operating systems.

Study full-system JIT compilation under WebAssembly's structured control flow and memory constraints. The [implementation overview](https://github.com/copy/v86/blob/master/docs/how-it-works.md) explains the interpreter, hot-page compilation, control-flow restructuring, and software TLB.

- **C1:** Memory access must distinguish page faults, read-only pages, MMIO, and writes to translated code. These cases route through a slow path that performs translation and invalidation while preserving guest semantics.
- **C3:** Hotness guides compilation; a two-pass generator discovers blocks before emitting code; a cached memory-access path avoids repeated page walks; lazy flags reduce arithmetic overhead. The document explains browser module-size and compilation constraints. The README explicitly lists missing x86 features and floating-point exceptions, so this is not a complete architectural reference implementation.

### 9. [dbalsom/martypc](https://github.com/dbalsom/martypc)

**Language/role:** Rust; IBM PC/XT and related early-PC machine emulation with detailed debugging and hardware-timing work.

Study the relationship between bus-visible CPU execution, peripheral timing, and observable debugging state.

- **C1:** The repository documents cycle-by-cycle comparison with a physical 8088, including prefetch-queue testing, and separate hardware investigations of timer and DMA behavior. This is stronger correctness evidence than merely booting a guest. See the repository's [accuracy discussion](https://github.com/dbalsom/martypc#accuracy); its device descriptions also disclose incomplete features.
- **C2:** The [machine implementation](https://github.com/dbalsom/martypc/blob/main/crates/lib/marty_core/src/machine.rs) owns the CPU/bus relationship and separates machine power, execution, debugger, and device-event state. CPU builders, video interfaces, machine descriptors, and shared device-state representations support multiple machine configurations and frontends.

### 10. [joncampbell123/dosbox-x](https://github.com/joncampbell123/dosbox-x)

**Language/role:** C/C++; DOSBox-derived PC emulator with broader hardware and operating-system compatibility. **Scope qualification:** inclusion rests on its bootable disk-image/guest-OS path, not on treating its built-in DOS environment as a complete historical machine.

Study the complications that appear when extending a DOS-oriented emulator to protected-mode operating systems. The official [Windows 98 installation guide](https://dosbox-x.com/wiki/Guide:Installing-Windows-98) verifies this full-system use case.

- **C1:** [Paging implementation](https://github.com/joncampbell123/dosbox-x/blob/master/src/cpu/paging.cpp) distinguishes privilege and write-protect combinations, page sizes, accessed/dirty state, and nested guest page faults. Fault execution preserves and restores lazy flags and the selected CPU decoder.
- **C2:** `PageHandler` abstracts read/write widths, checked operations, and optional direct host-memory access. Specialized handlers implement ordinary memory, permission enforcement, and fault behavior behind a shared interface. Comments expose unresolved CPU-core interactions, making the file useful for studying both design and accumulated compatibility complexity.

### 11. [ianopolous/JPC](https://github.com/ianopolous/JPC)

**Language/role:** Java; complete x86 PC emulator originating at Oxford, with guest OS booting and an integrated debugger. **Historical study candidate:** GitHub does not mark it archived; the API reported its last push in June 2024, which is not evidence of ongoing maintenance in 2026.

Study complete machine composition in a managed runtime, particularly how device references survive save/load cycles.

- **C1:** [LinearAddressSpace](https://github.com/ianopolous/JPC/blob/master/src/org/jpc/emulator/memory/LinearAddressSpace.java) models supervisor/user permissions, large pages, accessed bits, and global versus non-global TLB invalidation. Changing paging modes or directory bases has deliberately different cache effects.
- **C2:** [HardwareComponent](https://github.com/ianopolous/JPC/blob/master/src/org/jpc/emulator/HardwareComponent.java) defines initial wiring, reset without configuration loss, hibernation, and reconstruction of references after loading state. The lifecycle contract applies across PC devices rather than being embedded in a single machine bootstrap function.

## RISC-V and OpenRISC systems

### 12. [LekKit/RVVM](https://github.com/LekKit/RVVM)

**Language/role:** C; RISC-V machine emulator and embeddable library that runs firmware and operating systems. The full-machine API is relevant here; the separately described userspace work is not the basis for inclusion. The inspected default branch is `staging`.

Study an independent alternative to QEMU that exposes machine construction directly to embedding applications.

- **C2:** The [public machine API](https://github.com/LekKit/RVVM/blob/staging/include/rvvm/rvvm.h) separates machine creation, firmware/kernel loading, device-tree handling, MMIO callbacks, lifecycle, and ABI checks. It specifies handle invalidation on destruction and distinguishes paused from powered-off state.
- **C3:** The [retargetable JIT implementation](https://github.com/LekKit/RVVM/blob/staging/src/rvjit/rvjit.c) contains explicit host instruction-cache synchronization and executable-memory handling. **C1:** Host-specific barriers and cache flushes address the correctness of publishing generated code on machines without x86-style instruction-cache coherence. The project's comparative speed claims are not independently adopted here.

### 13. [sysprog21/semu](https://github.com/sysprog21/semu)

**Language/role:** C; compact RISC-V system emulator that boots Linux with an RV32 MMU, interrupt controller, UART, SBI services, and VirtIO devices.

Study event-driven execution at a scale where the central scheduling decisions remain easy to follow.

- **C1:** The [main execution loop](https://github.com/sysprog21/semu/blob/master/main.c) distinguishes stopped, started, WFI-idle, and UART-waiting harts when deciding whether host polling may block. Its boot-time timer handling explicitly prevents a deadlock when the kernel briefly puts all harts into WFI.
- **C3:** The same file explains why peripheral I/O is polled inline while coroutines are reserved for hart scheduling. This avoids making every peripheral wait for another round of coroutine scheduling and permits sleeping when guests are idle. The [coroutine interface](https://github.com/sysprog21/semu/blob/master/coro.h) exposes resume, yield, and suspended-state operations. The README documents limited interrupt-priority and device coverage.

### 14. [s-macke/jor1k](https://github.com/s-macke/jor1k)

**Language/role:** JavaScript, with alternative CPU engines; browser-based OpenRISC machine running Linux, plus a RISC-V system path.

Study the separation between a responsive browser frontend and worker-owned machine execution. It offers an older browser-emulation architecture worth comparing with v86's WebAssembly JIT, without assuming an equivalent maintenance cadence.

- **C1:** In the [system implementation](https://github.com/s-macke/jor1k/blob/master/js/worker/system.js), a hardware interrupt wakes a halted system, cancels the idle timeout, and advances guest time by a bounded amount before resuming execution. This coordinates guest sleep with asynchronous host events.
- **C2:** The worker system owns common memory, reset, timer, message, and filesystem machinery, then selects OpenRISC or RISC-V SoC initialization. Device reset and interrupt routing follow shared lifecycle interfaces. The repository's SMP demonstrations explicitly warn of instability as core count increases.

## Mainframes, minicomputers, and Alpha servers

### 15. [simh/simh](https://github.com/simh/simh)

**Language/role:** Primarily C; framework and collection of historical complete-computer simulators, including PDP, VAX, IBM, and other families. The monorepo counts once. This entry selects the `simh/simh` line; related SIMH forks are not independently counted.

Study how a common event and I/O substrate supports machines with very different instruction sets and peripheral conventions.

- **C1:** The [asynchronous-I/O design](https://github.com/simh/simh/blob/master/0readmeAsynchIO.txt) preserves minimum guest instruction delays and compatible save/restore state across asynchronous and synchronous builds. Device callbacks return to the instruction-executing thread, and a unit must not simultaneously remain on the event queue while asynchronous I/O is pending.
- **C2:** Disk, tape, Ethernet, console, and terminal-multiplexer libraries expose related callback-based services to many machine models. **C3:** The design replaces unproductive polling and overlaps host I/O with guest execution while keeping device-state mutation serialized. Study the mechanism; the old benchmark example in the document is not treated as a present-day performance estimate.

### 16. [SDL-Hercules-390/hyperion](https://github.com/SDL-Hercules-390/hyperion)

**Language/role:** C with assembly test programs; IBM System/370, ESA/390, and z/Architecture mainframe emulation. This is the substantive SDL Hyperion development line, not a separately counted copy of another Hercules repository.

Study extensibility and validation of a machine whose instruction, channel, and operating-system compatibility requirements extend beyond ordinary desktop emulation.

- **C1:** The [low-level testing guide](https://github.com/SDL-Hercules-390/hyperion/blob/master/tests/README.md) describes loading machine-state images, starting via a restart interrupt, waiting for CPUs to stop, and comparing storage/register results against known-good values. It explicitly discusses the difficulty of establishing a trustworthy oracle and validating against real hardware.
- **C2:** The [dynamic loader](https://github.com/SDL-Hercules-390/hyperion/blob/master/readme/README.HDL.md) supports adding commands, instructions, and functions without rebuilding the emulator. Dependency and symbol-resolution mechanisms support extension modules; the documented decision not to actually unmap unloaded code exposes a concrete concurrency/lifetime constraint.

### 17. [kej715/DtCyber](https://github.com/kej715/DtCyber)

**Language/role:** C core with JavaScript-based automation and terminal tooling; CDC 6000/70/170/180 computer simulation. **Substantive derivative:** the README identifies its Desktop CYBER 5.5.1 origin and separate additions, including peripherals, networking, and concurrent 170/180 operation.

Study channel-oriented I/O and peripheral processors, a markedly different system organization from a PC's CPU-centric device model.

- **C1:** The [channel implementation](https://github.com/kej715/DtCyber/blob/main/channel.c) distinguishes accepted, processed, and declined function codes, updates active/full state, and specifies behavior when no device claims a command. These transitions are guest-visible handshake semantics.
- **C2:** Attached devices implement function, activation, disconnect, and I/O callbacks through channel/device slots. This interface accommodates different tapes, disks, consoles, communications devices, and even physical channel interfaces. The surrounding OS setup material in the repository establishes that this is an operational complete-machine project rather than an isolated CDC instruction decoder.

### 18. [ES40-Emu/es40](https://github.com/ES40-Emu/es40)

**Language/role:** C++; revived AlphaServer ES40 emulator, including chipset and peripheral support. The repository documents guest operating-system work and a substantial 2026 JIT implementation. It is selected once for the ES40 family; AXPbox and older ES40 forks are not counted separately.

Study the interaction of Alpha address-space context, generated-code caching, and whole-machine persistence. This is an evolving revival with explicitly experimental graphics models, not a blanket recommendation of every device.

- **C1:** [SnapshotFile](https://github.com/ES40-Emu/es40/blob/main/src/SnapshotFile.h) creates an exclusive temporary file, checks write/flush/persistence/close failures, and replaces the previous snapshot only after completion. The README additionally documents snapshot-version and device/media compatibility restrictions.
- **C3:** The [JIT interface and cache structures](https://github.com/ES40-Emu/es40/blob/main/src/CPU/jit/jitengine.h) explain why virtual-PC-only caching thrashes across processes. Set-associative blocks incorporate address-space and PAL-shadow context; separate hot-trace and jump caches expose the optimization architecture. Numerical speedups in project updates are not independently verified here.

## Workstations and home computers

### 19. [dingusdev/dingusppc](https://github.com/dingusdev/dingusppc)

**Language/role:** C++; low-level PowerPC Macintosh emulation, particularly Old World machines, with CPU tests and a debugger. **Experimental:** the README explicitly describes incomplete machine support.

Study software MMU design where ordinary RAM, ROM, and memory-mapped devices share a guest address space.

- **C1:** The [MMU design document](https://github.com/dingusdev/dingusppc/blob/master/zdocs/developers/cpu/powerpc/mmuemu.md) explains block/page translation, permission exceptions, and delayed invalidation at context-synchronizing instructions. Changing a BAT mapping can shadow a cached page translation, requiring more than just clearing the BAT-derived entries.
- **C3:** A direct-mapped primary TLB handles common memory accesses; a secondary associative cache handles collisions and MMIO. Tracking populated translation slots moves invalidation work to synchronization points without adding a generation check to every hit. The document makes this tradeoff explicit; its instruction-count estimates are not repeated as measured results.

### 20. [hatari/hatari](https://github.com/hatari/hatari)

**Language/role:** C; Atari ST/STE/TT/Falcon computer emulator. **Official project GitHub mirror**; the repository points contributors to the main project and mailing-list workflow.

Study scheduling across hardware clock domains and the compatibility consequences of small timing errors.

- **C1:** [Cycle-interrupt scheduling](https://github.com/hatari/hatari/blob/main/src/cycInt.c) uses a common integer timebase for CPU and MFP clocks to avoid accumulating floating-point conversion errors. It also distinguishes absolute versus relative scheduling and compensates for interrupts delivered after a long instruction.
- **C3:** The execution loop tracks the next deadline instead of decrementing every event on every instruction, with ordered event links preserving scheduling structure.
- **C4:** The [release history](https://github.com/hatari/hatari/blob/main/doc/release-notes.txt) spans 2001 onward and records hardware compatibility fixes, deliberate API deprecations, configuration changes, and regressions such as reverted option behavior. This documents sustained compatibility management rather than merely repository age.

### 21. [tonioni/WinUAE](https://github.com/tonioni/WinUAE)

**Language/role:** C/C++; Amiga computer emulation, including Motorola CPU and custom-chip behavior. The source is especially valuable for examining the complexity of software that interacts with hardware while operations are in flight.

- **C1:** The [blitter implementation](https://github.com/tonioni/WinUAE/blob/master/blitter.cpp) maintains pipeline, channel, line/fill, delayed-register, and interrupt state. It explicitly forbids changing cycle-exact mode while a blit is running, illustrating an invariant that spans configuration and active hardware state.
- **C3:** The [event engine](https://github.com/tonioni/WinUAE/blob/master/events.cpp) provides normal and finer-grained cycle advancement, next-event scheduling, and host-vsync coordination. It preserves residual cycles and handles callbacks that schedule additional events at the current time. Study how timing modes and fast paths share a scheduler; do not assume all modes have identical fidelity.

### 22. [openMSX/openMSX](https://github.com/openMSX/openMSX)

**Language/role:** C++; MSX computer-family emulation with configurable machines and expansion hardware.

Study timestamped device interaction and the long-term refinement of memory mappers, video, sound, and flash devices.

- **C1:** The [current scheduler interface](https://github.com/openMSX/openMSX/blob/master/src/Scheduler.hh) requires synchronization points not to precede current CPU time and supports several pending points per device. Removing a single point does not promise to remove the earliest, an important caller-visible contract.
- **C2:** `Schedulable` devices share timestamped callbacks, removal, pending-query, and serialization machinery. A specialized queue supports removing entries away from the head while the normal scheduling path stays small.
- **C4:** The [release history](https://github.com/openMSX/openMSX/blob/master/doc/release-history.txt) records releases from 2003 through 2025, with concrete compatibility corrections: mapper registers, VDP I/O delays, a longstanding sound regression, and flash programming/erase semantics. An early internal design paper was also inspected but explicitly labels implementation details outdated; it is not the basis for claims about current APIs.

### 23. [TomHarte/CLK](https://github.com/TomHarte/CLK)

**Language/role:** C++ core with platform frontends; Clock Signal, a multi-machine emulator covering 6502, Z80, 68000, ARM, and other computer families as well as some consoles. The complete-computer implementations are the relevant subsystem.

Study machine-independent timing and output contracts alongside a signal-processing approach to video and sound. The README explains generating and decoding composite output and resampling source audio rather than relying solely on a finished framebuffer.

- **C1:** [TimedMachine](https://github.com/TomHarte/CLK/blob/master/Machines/TimedMachine.hpp) carries fractional clock-conversion error across calls instead of discarding it, and propagates speed changes into the audio producer's rate. This addresses numerical drift and cross-subsystem timing consistency.
- **C2:** The same interface translates host-duration requests into machine cycles and exposes output-flush and confidence hooks to many machine implementations. It sits alongside distinct audio, scan, input, and media interfaces. The README explicitly distinguishes its more rounded machines from less complete Amiga, Archimedes, and PC implementations.

### 24. [stardot/b-em](https://github.com/stardot/b-em)

**Language/role:** Primarily C; BBC Micro family emulation with multiple second-processor options.

Study heterogeneous processor cooperation through a narrow historical hardware interface rather than a modern shared-memory SMP model.

- **C1:** The [Tube ULA implementation](https://github.com/stardot/b-em/blob/master/src/tube.c) maintains FIFO/latch state, host and parasite status bits, and IRQ/NMI assertion transitions. Reading a register changes flow-control state and can change the interrupts seen by a different processor.
- **C2:** Common Tube execution, memory, save-state, and load-state hooks accommodate several second-processor architectures. Per-processor cycle multipliers and interrupt adapters preserve a shared host-side interface while allowing CPU-specific behavior. This makes the repository particularly useful for studying integration of multiple emulated CPUs in a complete microcomputer.

## Coverage, searches, and limitations

Discovery used live web searches followed by direct repository-page/API verification and reads of source files or project documentation. Search formulations covered, among others:

- `full system emulator GitHub QEMU Renode architecture` and embedded peripheral/time frameworks;
- `GitHub x86 full system emulator Rust JavaScript Bochs 86Box` and hardware-validated PC timing;
- `full system emulator RISC-V RVVM Linux JIT` and compact Linux-capable systems;
- OpenRISC/browser emulation, including `jor1k` and `or1ksim`;
- IBM mainframes, SIMH, CDC/DtCyber channels, and Alpha/ES40 revivals;
- PowerPC Macintosh, Atari, Amiga, MSX, BBC Micro, and multi-machine signal processing;
- MIPS/SPARC/GXemul and standalone workstation-emulator provenance;
- Java/JPC/Dioscuri, C#/Renode, Rust, and WebAssembly implementations.

Later architecture and language queries increasingly returned already-covered projects, userspace-only emulators, wrappers, unverified mirrors, or preliminary implementations. The final Java search still added the substantive historical JPC codebase. Selection stopped after these broader passes and primary-source verification, rather than at an initial familiar list.

**Important boundaries and exclusions:** userspace-focused FEX/felix86/libriscv-style projects, CPU-only ISA references, emulator launchers, and hardware RTL repositories are outside this report's scope. Educational RISC-V projects were considered but not added simply to increase count; semu was retained for its concrete Linux/device/scheduling implementation. Multiple PCem, SIMH, Hercules, and ES40 lineages were not indiscriminately counted as separate discoveries. AXPbox's own README points to ES40-Emu for current development, so the latter represents that family. GitHub copies without established project provenance were not used to fill standalone SPARC/MIPS coverage; those architectures remain represented through broader frameworks.

Every retained repository has a verified canonical GitHub location and at least one independently inspected implementation/design/test source beyond its root README. Raw URLs were used where GitHub's HTML obscured source text, not as a second copy of the README. Links target the verified branch/path as observed on the research date and can change later. QEMU and Hatari are explicitly identified as mirrors; JPC is explicitly treated as a historical study. No blanket active-maintenance claim is made for the remaining selection.

The report does not establish conformance, security, comparative speed, or guest compatibility by execution. ROM availability, guest licensing, and installation reproducibility were not tested. Architecture documents sometimes describe intended behavior; source-based recommendations remain an assessment of the inspected mechanisms, not proof of their correctness. The greatest depth is in software emulation of computers and boards; console-specific ecosystems and FPGA-assisted full-system simulation warrant separate searches.
