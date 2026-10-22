# Real-time operating systems

Research date: **2026-10-09**.

This selection covers 25 substantive GitHub codebases implementing real-time kernels or complete embedded operating systems: small microcontroller executives, connected-device platforms, SMP kernels, partitioned systems, and C++/Rust approaches. The relevant kernel subsystem is identified for larger repositories. Historical and experimental systems are included where they offer distinctive engineering material. This is a source-reading guide, not a certification, benchmark ranking, or claim that every component is exemplary.

**Criteria legend:** **C1** — difficult correctness involving concurrency, invariants, timing semantics, adversarial inputs, or failure handling. **C2** — substantial reusable abstractions serving multiple applications or hardware targets. **C3** — concrete performance or resource constraints addressed through understandable architecture. **C4** — sustained evolution with evidence of compatibility, testing, or complexity management. The criterion assessments are engineering judgments grounded in the linked primary material; they are not assertions of defect-free implementation.

## General-purpose embedded kernels and platforms

### [FreeRTOS/FreeRTOS-Kernel](https://github.com/FreeRTOS/FreeRTOS-Kernel)

**Language/role:** C and assembly; portable real-time kernel and architecture ports. The study target is the shared kernel implementation and its architecture ports. Study how a compact common implementation accommodates ISR calls, synchronization objects, allocation policies, and many ports.

- **C1:** Queue locking permits ISR data operations while deferring modifications to blocked-task lists. Mutex waits also require priority disinheritance when a waiter times out. These interacting states are documented directly in [queue.c](https://github.com/FreeRTOS/FreeRTOS-Kernel/blob/main/queue.c).
- **C2:** The same queue machinery implements queues, semaphores, and mutexes, with distinct storage and ownership semantics and static/dynamic allocation options.
- **C4:** The [release history](https://github.com/FreeRTOS/FreeRTOS-Kernel/blob/main/History.txt) spans many release generations and records compatibility defaults, generalized thread-local storage, SMP integration, compiler-port fixes, and corrections to object-lifetime and overflow handling. This is stronger evolution evidence than repository age alone.

### [zephyrproject-rtos/zephyr](https://github.com/zephyrproject-rtos/zephyr)

**Language/role:** Primarily C, with assembly and Python tooling; full embedded RTOS platform. Focus on the kernel and its configuration boundary before exploring the driver and networking subsystems.

- **C1:** The scheduler combines static priorities, optional deadline ordering within a priority, cooperative/preemptive execution, and SMP behavior. The documentation explicitly distinguishes timeslice limits from equitable CPU allocation, a useful example of precise scheduling semantics.
- **C2/C3:** Ready queues can use a simple list, red-black tree, or per-priority multiqueue, with documented memory, scaling, and feature tradeoffs. IPC wait queues reuse related backend choices. Read the [scheduling design](https://github.com/zephyrproject-rtos/zephyr/blob/main/doc/kernel/services/scheduling/index.rst) alongside [sched.c](https://github.com/zephyrproject-rtos/zephyr/blob/main/kernel/sched.c). The interesting abstraction is policy and data-structure selection without replacing the surrounding kernel API.

### [eclipse-threadx/threadx](https://github.com/eclipse-threadx/threadx)

**Language/role:** C and assembly; ThreadX embedded kernel, including architecture-specific ports. Study the interaction between ordinary priorities, preemption thresholds, and synchronization.

- **C1/C3:** Changing a thread's preemption threshold can make another thread immediately eligible to run. The implementation validates the threshold, updates preempted-thread bookkeeping, and performs the necessary preemption check. This exposes the correctness costs of controlling scheduling overhead more selectively than disabling all preemption. Entry point: [tx_thread_preemption_change.c](https://github.com/eclipse-threadx/threadx/blob/master/common/src/tx_thread_preemption_change.c).
- **C2:** Mutexes provide recursive ownership, configurable waiting, optional priority inheritance, and performance instrumentation through portable kernel code. [tx_mutex_get.c](https://github.com/eclipse-threadx/threadx/blob/master/common/src/tx_mutex_get.c) connects the reusable object API to owned-mutex lists, suspension cleanup, and scheduler services.

### [apache/nuttx](https://github.com/apache/nuttx)

**Language/role:** Primarily C; RTOS with POSIX-oriented interfaces and configurable embedded services. The relevant subsystem here is task/thread lifecycle management, rather than the entire collection of boards and drivers.

- **C1:** Last-member exit must release task-group resources in a safe order; shared kernel-thread groups require different treatment to avoid freeing resources still in use. [group_leave.c](https://github.com/apache/nuttx/blob/master/sched/group/group_leave.c) makes this distinction explicit and coordinates file descriptors, pending signals, pthread state, environment storage, mappings, and loaded binaries.
- **C2:** Task groups supply a reusable process-like ownership boundary for those services, letting POSIX-style applications share resources without equating each thread with an independent process.
- **C1/C2:** The [SMP port interface](https://github.com/apache/nuttx/blob/master/Documentation/reference/os/smp.rst) documents secondary-CPU startup and coordinated changes to another CPU's assigned-task state. Read it as the documented port contract, with current implementations checked for a chosen target.

### [RTEMS/rtems](https://github.com/RTEMS/rtems)

**Language/role:** C and assembly; real-time executive with multiple scheduler implementations and embedded services. **Official GitHub mirror:** development is hosted at the RTEMS GitLab, as the repository explicitly states.

- **C1:** SMP scheduling must reconcile processor affinity, pinning, readiness, and processor addition/removal. The documented EDF scheduler constrains affinity to one-to-one or one-to-all, including a specific rule for affinity sets that omit online processors.
- **C2/C3:** RTEMS exposes alternative scheduler implementations with different ready-queue structures: red-black trees, per-priority chains, and sorted chains. Its documentation also acknowledges the higher worst-case cost of arbitrary-affinity scheduling. Start with the [SMP scheduler guide](https://docs.rtems.org/docs/6.2/c-user/scheduling-concepts/smp-schedulers.html) and [EDF SMP implementation](https://github.com/RTEMS/rtems/blob/main/cpukit/score/src/scheduleredfsmp.c). This is particularly useful for studying the boundary between a scheduling interface and the algorithms behind it.

### [RT-Thread/rt-thread](https://github.com/RT-Thread/rt-thread)

**Language/role:** Primarily C; RTOS kernel within a larger device and application platform. Focus on the SMP scheduler in `src`.

- **C1:** [scheduler_mp.c](https://github.com/RT-Thread/rt-thread/blob/master/src/scheduler_mp.c) separates local interrupt masking, the scheduler spinlock, per-thread critical nesting, and deferred switching. Ready insertion checks whether a thread is already ready or still executing on a CPU, rather than blindly enqueueing it.
- **C3:** Global and per-CPU priority queues use bitmaps to select candidates; CPU binding affects placement and interprocessor scheduling notifications. These optimizations remain visible in named helper functions and explicit state transitions.
- **C4:** The same file's dated change log records evolution from the original scheduler through per-CPU queues, the uniprocessor/SMP split, spinlock changes, and race fixes. This gives concrete evidence of long-term complexity management, rather than merely an old copyright date.

### [ARM-software/CMSIS-RTX](https://github.com/ARM-software/CMSIS-RTX)

**Language/role:** C and assembly; RTX5 kernel implementing CMSIS-RTOS2 for Arm Cortex systems. This is the kernel spun out of CMSIS_5, not an additional independent implementation of that older copy.

- **C1:** Robust mutex owner termination, ownership transfer, recursive-lock limits, and restoration of inherited priorities are handled explicitly in [rtx_mutex.c](https://github.com/ARM-software/CMSIS-RTX/blob/main/Source/rtx_mutex.c).
- **C2/C3:** RTX supports global dynamic memory, object-specific pools, and application-supplied object storage, alongside a standard RTOS API. The [theory of operation](https://arm-software.github.io/CMSIS-RTX/latest/theory_of_operation.html) explains exception-based scheduling, interrupt-context calls, stack accounting, and tickless suspend/resume. Study how the Cortex exception model constrains kernel structure and how memory policy changes predictability; do not generalize architecture-specific interrupt behavior to every supported core.

### [weston-embedded/uC-OS3](https://github.com/weston-embedded/uC-OS3)

**Language/role:** C and assembly; µC/OS-III portable preemptive kernel. The former SiliconLabs URL redirects to this canonical repository. Its default branch is `develop`.

- **C1:** Mutex deletion distinguishes refusal when tasks are waiting from forced deletion that wakes waiters with a deletion result. Creation can reject ISR context and, under configuration, runtime creation after a safety-critical start boundary. [os_mutex.c](https://github.com/weston-embedded/uC-OS3/blob/develop/Source/os_mutex.c) documents these failure semantics alongside implementation.
- **C2:** The [public kernel header](https://github.com/weston-embedded/uC-OS3/blob/develop/Source/os.h) defines shared task/object types, synchronization services, timers, memory services, and detailed error states. Caller-owned control blocks and configurable checks are useful material for studying reusable APIs whose allocation and lifecycle policies remain explicit. The presence of safety-related options is not itself evidence that this checkout is certified.

### [tron-forum/mtkernel_3](https://github.com/tron-forum/mtkernel_3)

**Language/role:** C and assembly; TRON Forum's µT-Kernel 3.0 for small embedded systems and IoT edge nodes. It adds a standards-oriented Japanese RTOS lineage to the selection.

- **C1:** [mutex.c](https://github.com/tron-forum/mtkernel_3/blob/master/kernel/tkernel/mutex.c) handles priority inheritance and ceiling protocols, adjusts priorities after release, constrains priority changes while locks are held, and transfers owned mutexes when a task terminates.
- **C2:** The [kernel object modules](https://github.com/tron-forum/mtkernel_3/tree/master/kernel/tkernel) separate tasks, event flags, rendezvous, message buffers, mailboxes, fixed/variable memory pools, timers, and device I/O. Configurable control-block tables and a common waiting machinery support multiple object families. An engineer can compare this API/object model with POSIX-influenced and CMSIS-influenced kernels without treating the interface vocabulary as interchangeable.

## Connected devices and compact C kernels

### [ChibiOS/ChibiOS](https://github.com/ChibiOS/ChibiOS)

**Language/role:** C and assembly; RT and smaller NIL kernels, shared support libraries, and HAL. **Official read-only GitHub mirror** of the SourceForge SVN repository. The monorepo counts once; the main study target here is ChibiOS/RT.

- **C1:** [chmtx.c](https://github.com/ChibiOS/ChibiOS/blob/master/os/rt/src/chmtx.c) propagates inherited priority through chains of blocked mutex owners and reorders affected wait/ready queues. Disposal checks also make object-lifetime assumptions explicit.
- **C3:** The mutex API requires reverse-order unlocking, a deliberate restriction used to simplify and improve the inheritance implementation. The source documents a worst-case cost proportional to nesting depth. This is valuable for studying the performance consequences of API restrictions; reverse-order unlocking should not be mistaken for a universal proof that arbitrary application lock acquisition cannot deadlock.
- **C2:** The repository's structure separates RT/NIL kernels from reusable ports, OS libraries, and HAL adaptation, allowing those components to serve different footprint requirements.

### [RIOT-OS/RIOT](https://github.com/RIOT-OS/RIOT)

**Language/role:** Primarily C; microcontroller RTOS for networked and low-power devices, covering 8-, 16-, and 32-bit targets. Study the compact scheduler before following calls into the networking and driver layers.

- **C1:** [sched.c](https://github.com/RIOT-OS/RIOT/blob/master/core/sched.c) maintains the invariant between thread state, per-priority run queues, and a readiness bitmap. Context changes also interact with optional stack checks, TLS, and MPU stack guards.
- **C3:** Bitmap orientation changes according to availability of a count-leading-zeros instruction, showing a small, understandable optimization across CPU families. Inlining decisions are explained in terms of removing unused priority-changing code.
- **C2:** The repository documents a uniform hardware-facing API, partial POSIX support, modular networking, and a native host port. Those abstractions make it more than a board-specific scheduler; the retained subsystem is the actual RIOT kernel, not its tutorials or application examples.

### [apache/mynewt-core](https://github.com/apache/mynewt-core)

**Language/role:** Primarily C; Mynewt's preemptive RTOS kernel, HAL/BSP infrastructure, and system packages. NimBLE now has a separate repository and is not counted as part of this kernel entry.

- **C1:** The [callout implementation](https://github.com/apache/mynewt-core/blob/master/kernel/os/src/os_callout.c) coordinates timer-list membership with event-queue membership, rejects out-of-range delays, uses tick-comparison macros, and removes pending events when stopping a callout. Reset, expiration, and cancellation therefore involve more than a callback pointer and a timestamp.
- **C2:** Callouts reuse event queues to deliver timed work, letting services share an asynchronous execution mechanism. At a larger scale, the [kernel package](https://github.com/apache/mynewt-core/tree/master/kernel/os) sits within a system assembled through Newt packages and hardware abstractions. Study how a reusable timer/event layer connects a small kernel to independently selected services.

### [kelvinlawson/atomthreads](https://github.com/kelvinlawson/atomthreads)

**Language/role:** C and assembly; small portable scheduler and RTOS primitives, with AVR/STM8-oriented study value. **Historical:** GitHub metadata shows its last repository push in February 2021; current maintenance is not inferred.

- **C1:** [atomqueue.c](https://github.com/kelvinlawson/atomthreads/blob/master/kernel/atomqueue.c) specifies ISR-safe nonblocking use, priority-ordered wakeups with FIFO ties, timeout handling, and waking every blocked caller with a deletion result when a queue is destroyed.
- **C2/C3:** The queue API accepts caller-provided storage and configurable fixed-size messages. This keeps memory ownership explicit while reusing the same communication primitive across applications. The project intentionally limits itself to a scheduler and primitives, with architecture-specific ports separated from the core, making it a useful compact comparison to full connected-device platforms rather than a tutorial-only kernel.

## C++ kernel designs

### [DISTORTEC/distortos](https://github.com/DISTORTEC/distortos)

**Language/role:** C++; object-oriented RTOS for microcontrollers. Study how familiar C++ interfaces are adapted to embedded timing and interrupt-context constraints.

- **C1:** The [Mutex interface and implementation-facing contract](https://github.com/DISTORTEC/distortos/blob/master/include/distortos/Mutex.hpp) distinguish recursive-count exhaustion, erroneous relocking, ceiling violations, and timeout. It states that an immediately available mutex must not fail merely because a timeout has elapsed and explicitly restricts interrupt-context use.
- **C2:** Configurable mutex types/protocols, `constexpr` construction, and `std::chrono` duration overloads provide reusable abstractions rather than a C API with cosmetic wrappers. The class builds on a dedicated internal control block.
- **C4:** The [changelog](https://github.com/DISTORTEC/distortos/blob/master/CHANGELOG.md) includes dated releases across 2016–2019, semantic-versioning policy, later board test configurations, and detailed compatibility/limitation notes for standard-library and filesystem integration. Tagged-release cadence should be evaluated separately from ongoing source changes.

### [fedetft/miosix-kernel](https://github.com/fedetft/miosix-kernel)

**Language/role:** C++ and assembly; microcontroller RTOS supporting C/C++ runtime services, configurable scheduling, and protected or kernel-space applications. The README identifies `master` as the stable branch and other branches as development branches.

- **C2/C3:** [scheduler.h](https://github.com/fedetft/miosix-kernel/blob/master/miosix/kernel/scheduler/scheduler.h) uses a template-based common interface for priority, EDF, and control-based policies. Selection happens at compile time, avoiding virtual dispatch while preserving a shared kernel-facing contract.
- **C1/C3:** The same layer coordinates the next sleep wakeup and preemption deadline, including a designated wakeup-handling core under SMP. It documents locking assumptions, thread-lifetime rules, and why an older internal scheduling entry point was removed. This is a strong study target for policy separation that still exposes hardware timer costs and multicore ownership, rather than hiding them behind a generic scheduler class.

### [scmrtos/scmrtos](https://github.com/scmrtos/scmrtos)

**Language/role:** C++ and assembly; compact preemptive RTOS for single-chip microcontrollers, including AVR, MSP430, STM8, Cortex-M, and Blackfin targets.

- **C2/C3:** [os_kernel.h](https://github.com/scmrtos/scmrtos/blob/master/core/os_kernel.h) represents processes with templates parameterized by priority and stack size, including variants for architectures with separate return stacks. Fixed process tables and readiness bitmaps make resource layout visible at compile time.
- **C1:** The common service layer must distinguish an actual synchronization wakeup from timeout or forced wakeup before changing waiter maps. [os_services.h](https://github.com/scmrtos/scmrtos/blob/master/core/os_services.h) shows the shared suspend/resume machinery and separate ISR paths. It is useful for studying reusable C++ services over a deliberately constrained process model, without relying on the project's headline latency figures.

## Static configuration, partitioning, and microkernels

### [TrampolineRTOS/trampoline](https://github.com/TrampolineRTOS/trampoline)

**Language/role:** C and assembly, with configuration-generator tooling; static RTOS aligned with OSEK/VDX and AUTOSAR OS APIs. Its targets include automotive-relevant Cortex-R/RH850 as well as PowerPC, RISC-V, and smaller MCUs.

- **C1:** [resource management](https://github.com/TrampolineRTOS/trampoline/blob/master/os/tpl_os_resource_kernel.c) checks calling context, resource identity, access rights, ceiling relationships, ownership, and release order. It also handles releasing a terminated process's resources without ordinary rescheduling.
- **C2:** Static resource tables and a standards-shaped task/resource API separate application configuration from machine-specific code. The repository contains the `goil` configuration tool alongside `os`, `autosar`, and `machines`; the [manual source tree](https://github.com/TrampolineRTOS/trampoline/tree/master/documentation/manual) is the next navigation point. Study generated configuration as part of the kernel's correctness boundary, not just as build plumbing. The API alignment is not a blanket compliance or certification claim.

### [pok-kernel/pok](https://github.com/pok-kernel/pok)

**Language/role:** C and assembly; partitioned microkernel aimed at safety-critical embedded systems, with ARINC 653-oriented interfaces. Study temporal partitioning rather than treating it as another ordinary priority scheduler.

- **C1:** [sched.c](https://github.com/pok-kernel/pok/blob/main/kernel/core/sched.c) validates that partition slot durations sum to the major frame, advances partition deadlines, and tracks periodic thread activation and remaining execution capacity.
- **C2/C3:** Scheduling is split between partition selection and thread selection within a partition. Configured slot allocation and selectable communication-port flushing points expose the coupling between temporal isolation and interpartition communication.

The [project description](https://pok-kernel.github.io/) establishes category fit, but its old security notice is stale: the corresponding [isolation vulnerability issue](https://github.com/pok-kernel/pok/issues/9) records a merged fix and closure. Treat certification language as project intent, not as demonstrated assurance of the current tree.

### [phoenix-rtos/phoenix-rtos-kernel](https://github.com/phoenix-rtos/phoenix-rtos-kernel)

**Language/role:** C and assembly; Phoenix-RTOS microkernel, spanning MCU and MMU-equipped targets including Arm, RISC-V, x86, and SPARC/LEON. This entry covers the kernel, not the separate project-image assembly repository.

- **C1/C2:** [message passing](https://github.com/phoenix-rtos/phoenix-rtos-kernel/blob/master/proc/msg.c) separates request/reply states and buffer mappings. It handles partial-page copying, full-page mappings, and cleanup of temporary resources. This is concrete material for studying IPC across address spaces; inspecting it does not establish that all user-pointer validation is complete.
- **C1/C3:** [threads.c](https://github.com/phoenix-rtos/phoenix-rtos-kernel/blob/master/proc/threads.c) combines priority readiness bitmaps, a red-black tree of sleepers, timer programming, and scheduling-wait instrumentation. Assertions check list membership and time monotonicity, while comments expose platform-specific optimization constraints. The juxtaposition of IPC and scheduling makes this a useful small-process-system comparison to single-address-space RTOSes.

### [seL4/seL4](https://github.com/seL4/seL4)

**Language/role:** C and assembly; capability microkernel. Included specifically for its **Mixed-Criticality System (MCS) scheduling subsystem**, a foundation for real-time systems rather than a complete MCU middleware distribution.

- **C1:** Scheduling contexts track budget and period, enforce execution limits through sporadic-server replenishments, and follow donation chains through RPC. Correctness includes returning donated contexts and handling budget exhaustion.
- **C2/C3:** CPU-time authority is a reusable capability-managed object. Passive servers can execute on client budgets; the number of replenishment records trades memory and scheduling overhead against budget fragmentation. The [MCS design tutorial](https://docs.sel4.systems/Tutorials/mcs.html) provides substantive semantics and examples, including timeout faults. Its verification caveat must be respected: seL4's general reputation for proofs is not evidence that every MCS configuration or platform is covered by the same proof results.

### [echronos/echronos](https://github.com/echronos/echronos)

**Language/role:** C/assembly with Python configuration and testing tools; configurable RTOS family for constrained systems without virtual memory. **Historical:** the checked repository metadata reports a December 2019 last push.

- **C2/C3:** The repository's software-model documentation describes two stages of specialization: compose feature components into RTOS variants, then specialize a variant for an application's statically declared resources. Component source is merged before compilation, deliberately exposing more optimization opportunities and limiting included features.
- **C1:** [test_sched.py](https://github.com/echronos/echronos/blob/master/unit_tests/test_sched.py) compares compiled C scheduler behavior and resulting state with Python models across generated states for round-robin, priority, and priority-inheritance variants. The [model implementation](https://github.com/echronos/echronos/blob/master/unit_tests/sched.py) is a useful paired entry point. This supports studying executable-model checking, without claiming that the tests constitute a complete formal proof or that current toolchains remain supported.

## Rust approaches to real-time execution and fault handling

### [oxidecomputer/hubris](https://github.com/oxidecomputer/hubris)

**Language/role:** Rust with low-level architecture code; statically configured, memory-protected, message-passing embedded OS. Focus on `sys/kern` and the task model rather than counting its many firmware applications separately.

- **C1:** Task restart increments a generation number and wakes tasks interacting with the previous generation with an identifiable error. Fault policy belongs to a supervisor task, while initialization and reinitialization share a kernel path.
- **C2/C3:** Tasks are separately compiled and declared at build time; they run unprivileged and communicate through kernel interfaces. Strict priority preemption coexists with cooperative execution among equal-priority tasks. The [task design document](https://github.com/oxidecomputer/hubris/blob/master/doc/tasks.adoc) explains both the memory-accounting benefits and flash duplication costs of this structure. Study the explicit exchange between dynamic flexibility, fault containment, and predictable resource usage.

### [r3-os/r3](https://github.com/r3-os/r3)

**Language/role:** Rust; experimental statically configured preemptive RTOS. **Archived:** GitHub reports the repository archived, with its last push in April 2023. The default branch is literally `🦆`; the source link below preserves that verified branch name.

- **C2/C3:** Const evaluation constructs kernel objects and memory configuration, while traits decouple the kernel API from concrete kernel and architecture implementations. This is substantive compile-time composition rather than a Rust binding to a C RTOS.
- **C1:** [timeout.rs](https://github.com/r3-os/r3/blob/%F0%9F%A6%86/src/r3_kernel/src/timeout.rs) explains system time versus event time, wrapping counters, overdue interrupts, and permitted clock adjustments. A frontier invariant limits backward adjustment without inspecting every outstanding timeout. The explicit remaining application obligation—preventing timeouts from passing the critical point—is especially useful for studying where arithmetic guarantees stop. Treat this as design research requiring its historical compiler context.

### [hopter-project/hopter](https://github.com/hopter-project/hopter)

**Language/role:** Rust with assembly and a customized compiler; research embedded OS with priority scheduling, panic recovery, and segmented-stack experiments. The checked repository's last push was April 2025; production support is not inferred.

- **C1:** [soft_lock.rs](https://github.com/hopter-project/hopter/blob/main/src/sync/soft_lock.rs) grants either full access or a restricted ability to pend an operation. Its correctness assumption is explicit: an interrupting execution finishes before returning to the interrupted execution; this does not apply to arbitrary task switching.
- **C3:** The [scheduler](https://github.com/hopter-project/hopter/blob/main/src/schedule/scheduler.rs) uses a bounded lock-free insertion buffer when the ready list is contended, then drains deferred insertions and requests preemption. This supplies inspectable architectural evidence for reducing interrupt masking, without adopting an unqualified numerical or physical “zero latency” claim. The compiler dependency is a meaningful integration limitation and part of the design being studied.

### [n7space/aerugo](https://github.com/n7space/aerugo)

**Language/role:** Rust; safety-oriented RTOS developed in an ESA Rust evaluation activity for SAMV71/Cortex-M7. It deliberately uses **cooperative tasklets without preemption**, a distinct model from the other Rust entries.

- **C1:** [executor.rs](https://github.com/n7space/aerugo/blob/main/src/executor.rs) documents why its unsafe `Sync` implementation depends on static tasklet allocation and exclusion from IRQ access. Scheduling uses explicit Sleeping/Waiting/Working transitions; embedded tests reference system requirements and check those transitions.
- **C2/C3:** A fixed-capacity heap schedules reusable tasklets, rescheduling them when input remains. The separate [execution monitor](https://github.com/n7space/aerugo/blob/main/src/execution_monitor.rs) records timing statistics and emits an event after a configured execution-duration limit is exceeded. Monitoring is not preemptive enforcement: real-time behavior still depends on each tasklet completing its bounded processing step. The source offers a useful contrast between measurable execution and enforced CPU budgets.

## Coverage, search method, and limitations

Discovery used live web searches followed by repository/API checks and direct reading of source or primary documentation. Search formulations included conventional RTOS kernel/scheduler searches; C++ RTOSes and configurable scheduling; Rust RTOSes and isolation; OSEK/AUTOSAR/TRON lineages; safety-oriented microkernels; RISC-V/SMP kernels; 8-bit AVR/STM8 systems; partitioned RTOS alternatives; and hard-real-time kernels with priority ceilings and tests. Later searches increasingly returned already-covered families, wrappers, tutorial kernels, or closely related experimental alternatives. Aerugo was retained from that later pass because its cooperative tasklet model and requirement-linked tests added a distinct design.

The selection spans Arm Cortex-M/A/R, RISC-V, AVR, MSP430, STM8, PowerPC, SPARC/LEON, Blackfin, x86, and host-simulation approaches. Hardware support varies by project and branch; this report does not imply every listed kernel supports every architecture. C dominates the ecosystem, with substantive C++ and Rust implementations included intentionally. Repository canonical names, default branches, archive flags, and push metadata were checked through GitHub; a recent push was not treated as proof of maintenance quality or as C4 evidence.

Important exclusions and boundaries:

- **TencentOS Tiny/TobudOS:** the old GitHub URL redirects to [OpenAtomFoundation/TobudOS](https://github.com/OpenAtomFoundation/TobudOS), whose current default tree is a migration notice pointing to AtomGit. It was excluded because a substantive current official GitHub source mirror was not present there. Forks were not substituted.
- **Duplicate distributions and ports:** FreeRTOS vendor copies, CMSIS_5's older RTX copy, and board-only forks were not counted as independent kernels. RTEMS and ChibiOS remain because their official GitHub mirrors contain substantial implementations.
- **Adjacent categories:** general-purpose Linux/PREEMPT_RT, Linux co-kernels, hypervisors without a retained RTOS kernel, async frameworks alone, and generic embedded SDKs were outside this report's principal scope. Closed-source commercial RTOSes and repositories consisting mainly of wrappers, examples, or lists were excluded.
- **Experimental and historical coverage:** R3, eChronos, Atomthreads, and Hopter carry explicit status limitations. Other discovered experiments, including SCARS, were not needed to repeat the same scheduling families. This is a diverse selection rather than an exhaustive directory.

No candidate code was executed, repositories were not cloned, and hardware timing, test results, proof coverage, and certification were not independently reproduced. Some project documentation is older than its source tree; the POK notice is a concrete example where the issue history was checked to resolve that discrepancy. Performance assessments concern documented mechanisms and tradeoffs, not unsupported throughput or latency comparisons.
