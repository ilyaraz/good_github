# Machine control and industrial automation runtimes

Research date: **2026-10-09**.

This selection covers 19 GitHub repositories that execute PLC programs, schedule control components, coordinate machine motion, or provide the runtime foundation for industrial and experimental plant control. It spans IEC scan and event models, native Rust controllers, CNC kernels, embedded motion firmware, and distributed control frameworks. The relevant runtime subsystem is identified where the repository also contains editors, compilers, or other tools. These are engineering study candidates; inclusion does not establish that every component is exemplary or suitable for a particular machine.

Criteria used below:

- **C1 — Difficult correctness:** meaningful invariants, concurrency, numerical semantics, input handling, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces and execution models supporting multiple machines or applications.
- **C3 — Performance with structure:** actual timing, memory, or throughput constraints addressed by an understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, tests, or deliberate complexity management. Age alone does not qualify.

## PLC execution, scan models, and compatibility

### 1. [beremiz/beremiz](https://github.com/beremiz/beremiz)

**Language / role:** Python, C, and C++; IEC 61131-3 development environment with native PLC execution runtimes. Study the boundary between generated control code, target-specific cyclic execution, and remote program management. Relevant subsystems are `runtime/`, `C_runtime/`, and the target support code.

- **C2:** The architecture connects IEC compilation through MatIEC to a native shared object, with located variables providing the I/O boundary. Python and C++ runtime implementations expose a common eRPC management interface. This is a concrete example of keeping a PLC program contract independent of its runtime host. The [architecture overview](https://beremiz.readthedocs.io/en/latest/overview.html) explains the compilation, loading, runtime, and extension layers.
- **C3:** The Python implementation separates management work from the native scan execution path; target code supplies platform-specific timing facilities. The same overview discusses the worker/process boundary and POSIX, Windows, and Xenomai targets. That separation is worth studying without interpreting the presence of Python as a hard real-time guarantee.

Scope caveat: the public C++ runtime and reference target are the basis for inclusion; privately offered target ports mentioned in the documentation are not counted as public implementation evidence.

### 2. [Autonomy-Logic/openplc-runtime](https://github.com/Autonomy-Logic/openplc-runtime)

**Language / role:** C/C++ runtime with a Python management API; OpenPLC v4. This is the newer runtime repository, counted once rather than alongside its predecessor. It offers a particularly explicit account of what happens when a downloaded PLC program overruns or fails to stop.

- **C1:** The [architecture document](https://github.com/Autonomy-Logic/openplc-runtime/blob/main/docs/ARCHITECTURE.md) describes program lifecycle states, task draining, watchdog escalation, output-zeroing with protection against subsequent plugin writes, and restart into a safe mode after a fatal runtime failure. These mechanisms expose the difficult interaction between program cancellation, shared I/O state, and recovery.
- **C2:** Compiled PLC shared objects, I/O plugins, and the management API meet at separate interfaces. The API runs in a different process and communicates with the core through Unix-domain sockets, allowing control programs and hardware integrations to vary independently.
- **C3:** The same document explains the dispatcher, periodic IEC tasks, priority ordering, and a separate watchdog. The useful study topic is how task periods and supervisory work are organized, rather than an unsupported claim about achieved jitter.

The evidence concerns v4's documented architecture; the older OpenPLC project's history is not used to award C4 to this implementation.

### 3. [eclipse-4diac/4diac-forte](https://github.com/eclipse-4diac/4diac-forte)

**Language / role:** C++; IEC 61499 function-block runtime. FORTE adds an event-driven execution model to a list otherwise rich in cyclic PLCs. The inspected branch is `release`, whose current core lives under `core/src`.

- **C1:** The [event-chain executor](https://raw.githubusercontent.com/eclipse-4diac/4diac-forte/release/core/src/ecet.cpp) makes event delivery and concurrency concrete: external events enter under a critical section, the execution thread drains work and suspends when idle, and queue exhaustion has explicit handling. Start, stop, and kill operations interact with queued events, making lifecycle and wakeup semantics central correctness questions.
- **C2:** The [core source tree](https://github.com/eclipse-4diac/4diac-forte/tree/release/core/src) separates function blocks, resources, event/data connections, timers, and execution machinery. These are reusable runtime concepts for composing control applications, rather than a scheduler embedded in one machine program.

An experienced engineer can trace an event from an external producer through execution to a block input, then compare that contract with the process-image semantics of scan-based PLCs. Queue behavior is implementation evidence, not a claim that arbitrary application graphs are bounded or deterministic.

### 4. [roboplc/roboplc](https://github.com/roboplc/roboplc)

**Language / role:** Rust; Linux controller framework for writing native control programs. It is useful for studying industrial runtime construction without an IEC-language interpreter.

- **C2:** The repository documents independently usable controller workers, supervision, typed in-process messaging, ring buffers, I/O facilities, and thread configuration. The message hub avoids a dedicated server thread and serialization between local workers. This gives applications a reusable coordination model instead of requiring a bespoke thread graph for each controller.
- **C3:** The [worker example and initialization sequence](https://info.bma.ai/en/actual/roboplc/quickstart_hello.html) explicitly configure CPU affinity, FIFO scheduling and priority, preallocate heap memory, start periodic workers, and register bounded shutdown handling. These are concrete mechanisms for managing scheduling and allocation costs; the example's chosen period is not a measured latency guarantee.
- **C1:** The repository distinguishes default locking from optional real-time locking modes, including a priority-inheritance option. Its message policies and bounded buffers also make overload behavior an application decision. Study those choices before assuming that the default synchronization configuration prevents priority inversion.

The older rPLC project is not counted separately; RoboPLC is the successor examined here.

### 5. [ProviewRDev/pwrdev](https://github.com/ProviewRDev/pwrdev)

**Language / role:** Primarily C/C++; ProviewR process-control system, including its runtime database, PLC execution, and I/O framework. The monorepo also contains engineering and operator tools; the runtime is the reason for inclusion.

- **C2:** The [database guide](https://www.proviewr.se/doc/en_us/qguide_database.html) explains typed objects, classes, mounted volumes, and reusable plant assemblies. A component can combine control behavior, I/O representation, and operator-facing information. This is a richer reuse boundary than a collection of register addresses or isolated function blocks.
- **C1:** The [I/O guide, especially the I/O framework discussion around printed pages 69–70](https://www.proviewr.se/doc/en_us/man_iog.pdf), explains how initialization constructs agent/rack/card/channel trees for a process or PLC thread. Cycles perform input reads, PLC execution, then writes; write traversal reverses read traversal. Process and thread ownership determine which methods participate. Those ordering and ownership rules are essential to interpreting a scan correctly.

Study how persistent engineering objects become runtime dispatch structures and how custom applications attach to the same plant database. The inclusion is grounded in those mechanisms, not in the age or size of the surrounding SCADA environment.

### 6. [mbuesch/awlsim](https://github.com/mbuesch/awlsim)

**Language / role:** Python with optional Cython acceleration; S7-compatible AWL/STL execution and simulation, including hardware interfaces. **Official GitHub mirror:** the README identifies a separate primary Git server while explicitly directing GitHub issues and pull requests to this repository.

- **C1:** The [compatibility document](https://github.com/mbuesch/awlsim/blob/master/COMPATIBILITY.md) discusses instruction and memory semantics rather than claiming perfect hardware equivalence. It explains differences in symbol resolution, temporary memory, CALL handling, and unsupported call variants. This makes the repository valuable for studying the precise boundary between a useful industrial-language runtime and faithful emulation of a particular PLC.
- **C2:** The runtime operates on an internal program representation rather than requiring Siemens machine-code execution, and exposes multiple hardware integration paths. The repository describes LinuxCNC, Raspberry Pi GPIO, PiXtend, and PROFIBUS interfaces alongside its interpreter and self-tests. Thus the execution engine can support both virtual testing and physical control integrations.

Read the compatibility guide before comparing behavior with an actual S7 CPU. Its candid semantic differences are a strength as study material, not evidence that every program can be transferred unchanged.

### 7. [ironplc/ironplc](https://github.com/ironplc/ironplc)

**Language / role:** Rust; a **prototype** IEC 61131-3 compiler and bytecode runtime. The relevant implementation is `compiler/vm`, with the command-line host in `compiler/vm-cli`; the repository is counted once.

- **C1:** The [scheduler implementation and its tests](https://raw.githubusercontent.com/ironplc/ironplc/main/compiler/vm/src/scheduler.rs) establish explicit ordering by task priority and identity, cyclic release times, disabled-task behavior, and overrun handling. Time is supplied by the caller, which makes scheduling decisions reproducible in tests without sleeping or reading an operating-system clock.
- **C2:** The scheduler consumes caller-supplied task state and ready-task storage, separating clock acquisition, scheduling, and VM execution. The [runtime execution design](https://github.com/ironplc/ironplc/blob/main/specs/design/runtime-execution-model.md) develops the broader program lifecycle and process-image contract. These are useful interfaces for exploring different runtime hosts.

Important limit: the design document includes intended behavior beyond what should be assumed implemented. In the inspected scheduler, event-task readiness is still explicitly unimplemented. This is included as a substantive, inspectable runtime under development, not as a production-ready replacement for the more established PLC systems above; C4 is not claimed.

## CNC kernels and machine execution

### 8. [LinuxCNC/linuxcnc](https://github.com/LinuxCNC/linuxcnc)

**Language / role:** C/C++ with Python tooling; CNC control system. Focus on the motion controller, trajectory planning, kinematics, homing, and hardware abstraction layer rather than treating every GUI and bundled component as a separate project.

- **C1:** The [code notes](https://linuxcnc.org/docs/scratch/html/code/code-notes.html) distinguish task interpretation, trajectory generation, kinematics, joint coordinates, and machine coordinates. Homing and mode transitions affect which coordinate relationships are meaningful. This is useful material for understanding why a motion controller's state model is more complicated than translating a G-code move into motor pulses.
- **C2:** The [HAL introduction](https://linuxcnc.org/docs/html/hal/intro.html) describes typed pins, signals, components, and functions that can be wired into different machine configurations. The abstraction supports both software control functions and hardware drivers.
- **C3:** HAL assigns ordered functions to periodic threads, allowing input acquisition, control computation, and output updates to run at appropriate rates. This complements the separation between user-space task work and timing-sensitive motion execution.

Documentation caveat: the code-notes page itself warns that some material is outdated. Use it as an architectural map and check the current source when relying on a particular implementation detail.

### 9. [machinekit/machinekit-hal](https://github.com/machinekit/machinekit-hal)

**Language / role:** C/C++ with supporting Python; reusable real-time HAL, drivers, and component infrastructure. This is the separately developed HAL repository, not the archived original Machinekit monorepo. Its README records the LinuxCNC lineage and the later HAL/CNC split.

- **C2:** The [HAL guide](https://www.machinekit.io/docs/hal/intro/) explains typed pins and signals, independently reusable components, and the distinction between a component's data interface and its executable functions. Machines are assembled by configuring those contracts. Separating the HAL package from CNC-specific interpretation gives this fork a substantive scope beyond mirroring LinuxCNC.
- **C3:** Functions are assigned to periodic threads in an explicit order. Fast pulse-generation work, slower servo work, and user-space interaction need not share one schedule. The guide's read/compute/write examples make timing structure inspectable rather than burying it inside callbacks.

The [current source tree](https://github.com/machinekit/machinekit-hal/tree/master/src) is organized into executables, libraries, and modules. Read it alongside the guide: some website material predates the repository split and discusses the broader Machinekit system. The historical multicore design proposals are not treated here as proof that all proposed mechanisms landed.

### 10. [grblHAL/core](https://github.com/grblHAL/core)

**Language / role:** C; hardware-independent CNC motion core with external MCU drivers and plugins. It descends from Grbl but has a substantive hardware and extension architecture of its own, so it is not counted as an unchanged fork.

- **C1:** The [planner implementation](https://raw.githubusercontent.com/grblHAL/core/master/planner.c) describes a ring of motion blocks and a reverse/forward lookahead calculation. Deceleration feasibility propagates backward; acceleration limits propagate forward. Feed holds and overrides can invalidate previously planned work, making queue state and numerical bounds tightly coupled.
- **C3:** The planner tracks how far useful replanning has progressed and avoids repeatedly processing an already optimal prefix. Its comments explain the tradeoff between finite lookahead, many short segments, computation, and buffer memory. This is concrete performance engineering with a readable algorithmic rationale.
- **C2:** The core delegates hardware operations to driver interfaces and supports extension hooks. The [changelog](https://github.com/grblHAL/core/blob/master/changelog.md) gives concrete examples of driver-interface changes, hooks, and motion-state fixes, showing where core/driver boundaries demand coordination.

Best study path: read the planner's introductory invariants, then follow a recent motion or driver-interface change into its affected subsystem. No particular pulse rate or latency is inferred from the architecture.

### 11. [bdring/FluidNC](https://github.com/bdring/FluidNC)

**Language / role:** C++; ESP32 CNC firmware and successor to Grbl_ESP32. FluidNC emphasizes runtime machine configuration and an object-oriented hardware model, giving it a distinct study role from grblHAL's portable C core.

- **C2:** The repository explains YAML machine configuration and configurable motors, spindles, and peripheral hardware. The same firmware can represent different machines through configuration rather than requiring every machine variation to become a separately compiled source fork.
- **C1:** The [planner source](https://raw.githubusercontent.com/bdring/FluidNC/main/FluidNC/src/Planner.cpp) keeps planner position separate from the interpreter's position, which matters for decomposed arcs and compensation. Its block queue and two-pass velocity calculation preserve acceleration and deceleration feasibility across adjacent moves.
- **C3:** The same source allocates the configured planner buffer during initialization, carries markers that limit recalculation, and uses squared speed quantities in the lookahead calculations. Engineers can examine how a familiar motion algorithm is integrated into a configurable MCU runtime with bounded planning storage.

The planner shares Grbl ancestry with other entries; the reason to study FluidNC separately is its machine configuration and hardware-object architecture, not to count the inherited planner as an entirely independent invention.

### 12. [synthetos/g2](https://github.com/synthetos/g2)

**Language / role:** C++; g2core motion firmware for CNC and related multi-axis machines. Its TinyG lineage and jerk-controlled planning offer a different embedded motion architecture from the Grbl family.

- **C1:** The [planner source](https://raw.githubusercontent.com/synthetos/g2/edge/g2core/planner.cpp) explicitly separates the canonical machine model, queued/planned blocks, and the runtime executing motion. Because planning runs ahead of physical movement, reading state from the wrong layer can use a future position. The source explains those ownership boundaries and includes structural assertions for planner buffers.
- **C3:** Planning is organized as nonblocking work with bounded queues and distinct planner/runtime contexts. The implementation explains why some singleton paths are non-reentrant. This makes continuation-style execution and finite-buffer behavior visible instead of hiding them behind an operating-system thread per activity.
- **C2:** The planner sits below canonical machine interpretation and above motor mapping and step generation, providing a reusable boundary for different machine geometries and command sources.

Branch caveat: the inspected `edge` branch is described by the repository as beta; its README directs users seeking the stable branch to `master`. Inclusion is an implementation-study recommendation, not a claim about current release cadence.

### 13. [epics-modules/ecmc](https://github.com/epics-modules/ecmc)

**Language / role:** C++; EtherCAT motion control and PLC functionality integrated with EPICS. The relevant code is `devEcmcSup`, especially its motion, PLC, EtherCAT, and plugin subsystems. This is a controller runtime, not merely a fieldbus packet library.

- **C1:** The [motion-monitor implementation](https://raw.githubusercontent.com/epics-modules/ecmc/master/devEcmcSup/motion/ecmcMonitor.cpp) covers hard and soft limits, following error, encoder disagreement, velocity, stall detection, and EtherCAT entry validity. Several checks use tolerances and counters rather than a single instantaneous comparison. Their interaction with startup conditions and interlocks is valuable material for studying failure handling in a real motion stack.
- **C2:** The repository combines axis abstractions, trajectory generation, a PLC expression layer, extension plugins, and EPICS-facing integration. The [runtime source tree](https://github.com/epics-modules/ecmc/tree/master/devEcmcSup) exposes the separation between those concerns, allowing the same motion machinery to serve multiple machine configurations and supervisory applications.

A useful reading exercise is to trace a bad bus value or persistent following error through monitor state into an axis interlock, then compare that with the normal trajectory path. The presence of these checks does not by itself establish a machine-level safety guarantee.

### 14. [scottalford75/Remora](https://github.com/scottalford75/Remora)

**Language / role:** C++ MCU firmware plus a C LinuxCNC HAL component; a programmable real-time coprocessor for LinuxCNC. This entry concentrates on the repository's SPI firmware and host integration.

- **C2:** The [Mbed OS6 firmware entry point](https://raw.githubusercontent.com/scottalford75/Remora/main/Firmware/FirmwareSource/Remora-OS6/main.cpp) loads JSON-selected modules into base and servo threads. Step generation, encoders, PWM, temperature, and digital I/O share that execution framework. It also exposes the setup/running/reset state machine and the communications boundary.
- **C3:** The firmware places time-sensitive module work in the MCU threads and uses DMA for communication, while LinuxCNC supplies the higher-level machine control. This is an accessible example of moving pulse and I/O deadlines away from a general-purpose host without replacing its entire control stack.
- **C1:** The [SPI HAL component](https://raw.githubusercontent.com/scottalford75/Remora/main/LinuxCNC/Components/Remora-spi/remora-spi.c) handles scale validation, frequency and acceleration limiting, feedback counters, and response-header checks. These show the numerical and protocol responsibilities on the host side of the boundary.

Documentation caveat: the README warns that documentation lags a release candidate. Shared Remora documentation also covers newer hardware and firmware repositories; their capabilities are not automatically attributed to this repository.

## Additive-manufacturing machine runtimes

### 15. [Klipper3d/klipper](https://github.com/Klipper3d/klipper)

**Language / role:** Python and C; host-plus-microcontroller machine-control runtime, primarily for 3D printers. Its split execution model makes it especially useful for studying how high-level language code can participate in a system with precise physical timing.

- **C3:** The [code overview](https://www.klipper3d.org/Code_Overview.html) follows movement from G-code through lookahead and kinematics to a C trajectory queue, iterative step-time calculation, compressed step commands, and MCU timer execution. The host performs expensive planning; the MCU consumes scheduled work close to the hardware.
- **C1:** The same overview documents execution contexts: the host reactor, background work, per-stepper calculation, MCU tasks, and timer interrupt callbacks. Shutdown handling and restrictions on interrupt-context work are part of the runtime contract. Correctness depends on ordered commands and timing across these boundaries, not just valid geometry.
- **C2:** Kinematics implementations, hardware wrappers, and configurable modules extend the same execution pipeline. The configuration lifecycle validates and connects objects before normal operation, providing a reusable machine model rather than a single printer-specific main loop.

The overview is a strong entry point because it connects algorithms and scheduling to the exact source subsystems responsible for them. No numerical timing claim is needed to justify inclusion.

### 16. [Duet3D/RepRapFirmware](https://github.com/Duet3D/RepRapFirmware)

**Language / role:** C++; embedded machine firmware for Duet hardware, including motion, G-code execution, and thermal/peripheral control. Study its RTOS integration and extensible kinematics rather than only its printer feature set.

- **C1:** The [FreeRTOS implementation notes](https://github.com/Duet3D/RepRapFirmware/wiki/Notes-on-using-FreeRTOS) explain why heap operations cannot be used indiscriminately while scheduling is suspended, how library reentrancy affects memory use, and when code needs a mutex, scheduler suspension, selective interrupt masking, or full interrupt exclusion. These distinctions expose practical deadlock and interrupt-race risks.
- **C2:** The [kinematics extension guide](https://github.com/Duet3D/RepRapFirmware/wiki/Adding-New-Kinematics) describes a class hierarchy and factory registration through `KinematicsTypeDescriptor`. It distinguishes the newer registration mechanism from older numeric registration, making the interface evolution explicit. Machine geometry can be added through an established subsystem rather than scattered conditionals throughout the interpreter.
- **C3:** The RTOS notes also explain custom numeric conversion and formatting choices motivated by heap use and reentrancy costs. The tradeoff is tied to identifiable library behavior, not an unsupported assertion that all firmware paths have bounded execution time.

Together, the two guides are useful examples of documenting constraints that extension authors must preserve.

## Reusable control and plant-runtime frameworks

### 17. [epics-base/epics-base](https://github.com/epics-base/epics-base)

**Language / role:** C/C++; EPICS Base, particularly the IOC database and record-processing runtime. This is included for execution of linked control records and device support in large experimental and industrial control systems, not merely for its network protocols.

- **C1:** The [locking, scanning, and processing guide](https://docs.epics-controls.org/en/latest/appdevguide/lockScanProcess.html) explains record lock sets, asynchronous completion, and the `PACT` processing guard that prevents recursive record-processing cycles. It also describes multi-record locking rules and why older links that bypassed locking were removed. A linked record graph creates concurrency obligations that are absent from a simple sequential scan.
- **C2:** Records can be activated by periodic scans, I/O events, explicit events, or passive links, while record and device support provide reusable extension boundaries. The same guide shows how these activation models compose into one IOC execution system.

The most useful study path is to trace a forward or input link across record processing and then add an asynchronous device completion. This reveals the distinction between dependency structure, lock ownership, and actual completion time. The monorepo is counted once; individual record types and protocol components are not separate entries.

### 18. [orocos-toolchain/rtt](https://github.com/orocos-toolchain/rtt)

**Language / role:** C++; Orocos Real-Time Toolkit, a component execution framework used in robotics and machine control. Its reusable control-runtime semantics, rather than general robot middleware alone, are the category fit.

- **C2:** The [component manual](https://orocos-toolchain.github.io/rtt/toolchain-2.9/xml/orocos-components-manual.html) defines `TaskContext`, operations, typed data ports, properties, execution activities, and type extensions. Periodic and event-driven components share the same composition model, supporting different control applications without embedding their behavior into one scheduler.
- **C1:** The manual distinguishes the thread-safety and real-time contracts of ports, properties, and operations. In particular, copying a port's data type must itself meet the required constraints; a generic transport interface cannot make arbitrary user types safe. Its lifecycle model also distinguishes runtime errors, exceptions, fatal errors, and recovery paths.
- **C3:** Components can select execution contexts and communicate through local data-port mechanisms without requiring all work to run in a single loop. The documented constraints make the cost model inspectable instead of treating “real-time” as an unconditional property of every component.

The linked manual is explicitly for Toolchain 2.9; it is not evidence that this is the newest release or that every transport has identical guarantees.

### 19. [eeros-project/eeros-framework](https://github.com/eeros-project/eeros-framework)

**Language / role:** C++; machine-control framework organized around control, safety, and sequencing subsystems. EEROS is a useful less-famous example of making control periods and machine-state handling first-class architectural concepts.

- **C1:** The [time-domain documentation](https://wiki.eeros.org/eeros_architecture/control_system/time_domains) specifies that blocks execute in insertion order, that signals carry timestamps, and that crossing between periods needs explicit transition behavior. It also describes faults that trigger safety events and stop affected execution. Engineers can study both numerical timing assumptions and the consequences of a wrongly ordered control graph.
- **C2:** Blocks are grouped into time domains with a common period; control logic, safety-state handling, and higher-level sequencing have separate roles. The framework can therefore express different machines without collapsing all timing and state logic into one application loop.
- **C4:** The [changelog](https://github.com/eeros-project/eeros-framework/blob/master/CHANGELOG.md) provides evidence across 2021–2026: block-interface deprecations, test changes, initialization and thread-safety fixes, numerical corrections, and language/toolchain adaptation. This supports a sustained-evolution claim more strongly than repository creation or push dates alone.

Read the timing guide together with relevant changelog entries: changes to block interfaces and initialization behavior can alter the assumptions of an otherwise unchanged control application.

## Coverage, search process, and limitations

Discovery used more than six distinct live-web query families, followed by direct reading of repository pages and primary material. Search angles included:

- IEC 61131-3 SoftPLC runtimes, Beremiz/OpenPLC, and compiler-to-runtime boundaries.
- IEC 61499 event-chain execution and FORTE's current core layout.
- Rust control runtimes, RoboPLC/rPLC, and IronPLC scheduling.
- S7 AWL compatibility, instruction semantics, and hardware-backed simulation.
- Linux CNC real-time motion, HAL component execution, and Machinekit's repository split.
- Embedded CNC planning across grblHAL, FluidNC, and the TinyG/g2 family.
- EtherCAT motion with EPICS, axis interlocks, and plant runtime databases.
- Host/MCU execution partitions in Klipper and Remora, plus RTOS-based RepRapFirmware.
- Reusable control frameworks including Orocos, EEROS, and MARTe2, and the hosting status of candidate projects.

The selection spans C, C++, Python, and Rust; MCU, Linux real-time, and distributed plant architectures; and PLC, manufacturing, robotics/control, and experimental-facility communities. Later searches primarily rediscovered these families or found smaller wrappers and adjacent tooling. Additional closely related printer firmware was not added merely to increase the count.

Each retained canonical GitHub repository page was opened, and at least one additional primary document or implementation source was read. Source files, architecture manuals, compatibility notes, and the cited changelog provide evidence beyond taglines. Criterion assignments and suggested study paths are judgments drawn from that evidence, not independent benchmark results. Branch links are browsing entry points and can change after the research date.

Important boundaries: compiler-only projects, HMI/G-code senders, general ROS packages, pure fieldbus libraries, tutorial controllers, and aggregate lists were excluded. Original Grbl and the archived original Machinekit repository were not added beside their substantively evolved descendants. Superseded OpenPLC and rPLC implementations were not double-counted. MARTe2 was investigated, but its GitHub mirror's official status was not established strongly enough for retention; its repository directs source development elsewhere. Moved hosting and uncertain mirror provenance therefore limit coverage of some otherwise relevant control frameworks.

The report flags the official Awlsim mirror, IronPLC's prototype status, g2's branch distinction, and documentation/version mismatches where observed. It does not infer active maintenance from an accessible repository or a recent push. No candidate code was built or run, no dependencies were installed, and no hardware behavior was tested. Timing bounds, complete compatibility, and deployment readiness remain application- and configuration-dependent questions outside this read-only research.
