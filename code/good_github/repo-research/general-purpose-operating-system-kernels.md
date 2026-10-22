# General-purpose operating system kernels

Research date: **2026-10-09**.

This guide selects 24 repositories containing kernels for general-purpose operating systems, or substantive research implementations of that role. It includes complete OS trees only once, identifying their kernel subsystem, and includes a bare microkernel where its use beneath a general-purpose OS is documented. Small-machine Unix systems belong here even when their resource budgets are radically different from contemporary desktops. Dedicated RTOSes, hypervisors without a general-purpose kernel role, application-specific unikernels, and introductory kernel exercises are outside scope.

The criteria below are assessments grounded in the linked implementations and documentation. They identify useful engineering material to study; they do not imply that every component is exemplary, that experimental systems are production-ready, or that a documented design goal has been proved.

- **C1 — Difficult correctness:** invariants, concurrency, adversarial inputs, resource lifetimes, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and mechanisms serving multiple subsystems or applications.
- **C3 — Performance with structure:** explicit resource or execution-cost constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** years of development accompanied by compatibility work, testing, or explicit complexity management. Age and recent pushes alone do not establish this criterion.

## Established Unix and Darwin kernels

### [torvalds/linux](https://github.com/torvalds/linux)

**Language/role:** Primarily C, with assembly and Rust; Linux mainline kernel. The repository is the kernel itself, rather than a distribution.

An experienced engineer can study how synchronization interfaces encode object-lifetime guarantees while supporting read-heavy workloads across many subsystems. The particularly useful starting point is the kernel's own [RCU explanation](https://github.com/torvalds/linux/blob/master/Documentation/RCU/whatisRCU.rst), which connects conceptual rules to APIs and implementations.

- **C1:** RCU separates removing an object from reclaiming it. Reclamation must wait for pre-existing readers; publication and dereference operations also carry memory-ordering requirements. The documentation explains why simply replacing a pointer is insufficient.
- **C2:** Read-side critical sections, grace-period waits, and deferred callbacks form a reusable lifetime-management interface, including use with reference counts and linked structures.
- **C3:** RCU deliberately shifts work away from readers to reduce atomic operations and cache-line communication. The same document discusses batching, delayed reclamation, and the need to bound asynchronous updates under resource pressure.

### [freebsd/freebsd-src](https://github.com/freebsd/freebsd-src)

**Language/role:** C and assembly kernel in `sys/`, within the FreeBSD base-system tree. **Official publish-only GitHub repository/mirror**, as identified by its repository description.

Study priority inversion and the relationship between scheduler state, lock ownership, and allocation cost through [the turnstile implementation](https://github.com/freebsd/freebsd-src/blob/main/sys/kern/subr_turnstile.c). Its extensive design comments make a difficult synchronization mechanism unusually approachable.

- **C1:** Priority lending follows chains of blocked lock owners. The code specifies lock order, detects inappropriate sleeping while holding non-sleepable locks, and accounts for a waiter already being awakened on another CPU.
- **C2:** Turnstiles provide shared infrastructure for non-sleepable locks, with separate shared/exclusive waiter queues and scheduler integration rather than bespoke waiting logic in each lock user.
- **C3:** Each thread contributes a turnstile when blocked; locks find them through a hash table. This avoids embedding a large queue structure or back-pointer in every lock. Profiling counters expose chain depth and contention-related behavior.

### [NetBSD/src](https://github.com/NetBSD/src)

**Language/role:** Primarily C and assembly; kernel in `sys/`, alongside the NetBSD base system. **Official automatic CVS conversion.** The repository warns that converted commit links can change, so this guide uses a branch-based source link.

The [UVM map implementation](https://github.com/NetBSD/src/blob/trunk/sys/uvm/uvm_map.c) is a strong study of virtual-address interval management and the bookkeeping behind efficient allocation.

- **C1:** Map insertion, removal, range clipping, and entry merging have explicit locking preconditions. Tree-order assertions, compatibility checks for merging mappings, and invalidation of lookup hints expose invariants that are easy to violate during unmapping or resizing.
- **C3:** An augmented red-black tree records the largest available gap in each subtree; cached subtree values avoid repeatedly searching all descendants. Entry pools, lookup hints, and event counters show how allocation overhead and search behavior are managed without hiding the underlying data structure.

This is a useful complement to studying architecture-specific page-table code: it exposes the reusable VM policy machinery above it.

### [openbsd/src](https://github.com/openbsd/src)

**Language/role:** C and assembly; OpenBSD kernel in `sys/`. **Official read-only conversion of the CVS source repository.**

Study the translation of application-declared restrictions into kernel enforcement through [the pledge implementation](https://github.com/openbsd/src/blob/master/sys/kern/kern_pledge.c). It makes the boundary between a convenient security API and detailed syscall semantics visible.

- **C1:** Enforcement is more involved than a syscall allowlist. The implementation distinguishes path access, socket address selection, descriptor passing, restricted `ioctl` operations, and calls required for process termination or error reporting.
- **C2:** Promise classes provide one reusable restriction vocabulary for otherwise unrelated applications. A central syscall-to-promise mapping cooperates with argument-specific checks, allowing broad application classes to share enforcement machinery.

The educational value is in tracing individual operations and exceptions through the implementation, rather than assuming that a small public API implies a small correctness surface.

### [DragonFlyBSD/DragonFlyBSD](https://github.com/DragonFlyBSD/DragonFlyBSD)

**Language/role:** C and assembly; kernel in `sys/`, within a complete BSD source tree. **Official read-only GitHub mirror.** This is a separately evolved BSD implementation, not a second copy of FreeBSD mainline.

The [LWKT token implementation](https://github.com/DragonFlyBSD/DragonFlyBSD/blob/master/sys/kern/lwkt_token.c) offers a distinctive comparison with ordinary mutexes: tokens serialize a thread while it runs, are released when it blocks, and are reacquired when execution resumes.

- **C1:** Recursive acquisition, reverse release order, shared/exclusive ownership, and scheduler-mediated reacquisition create nontrivial invariants. Callers must reason about changes that may occur across blocking points.
- **C2:** Tokens cover common subsystems such as VM, vnodes, device state, and terminal state through one synchronization facility.
- **C3:** Atomic acquisition, cache-aligned token pools, collision counters, exponential backoff, and shared-token timing windows expose explicit contention-management choices and their interaction with scheduling.

## Other large system families

### [illumos/illumos-gate](https://github.com/illumos/illumos-gate)

**Language/role:** Primarily C and assembly; Unix kernel under `usr/src/uts/` in the core illumos source tree. **Official read-only mirror** of the repository linked in its description.

Start with [kernel task queues](https://github.com/illumos/illumos-gate/blob/master/usr/src/uts/common/os/taskq.c). The source explains why deferred work is needed, then distinguishes ordinary worker queues from dynamic task pools.

- **C1:** The API documents dispatch failure under resource pressure, shutdown obligations, and deadlocks caused by queuing mutually dependent work or waiting on one's own task queue. Preallocated dispatch has separate lifetime rules.
- **C2:** A common task interface supports deferred operations, work that may block, and parallel execution across kernel subsystems. Callers can select different execution policies without redesigning their work items.
- **C3:** Dynamic pools address global contention and long-blocking tasks; thread limits, prepopulation, CPU-relative sizing, and backlog controls make the resource tradeoffs explicit.

### [apple-oss-distributions/xnu](https://github.com/apple-oss-distributions/xnu)

**Language/role:** C, C++, and assembly; Apple's **official published XNU source distribution**, not a complete macOS or iOS distribution or a public view of every internal development change.

The [repository architecture overview](https://github.com/apple-oss-distributions/xnu/blob/main/README.md) identifies the Mach-derived `osfmk`, BSD layer, platform code, and IOKit interfaces. A concrete implementation entry is [turnstile priority propagation](https://github.com/apple-oss-distributions/xnu/blob/main/osfmk/kern/turnstile.c).

- **C1:** Priority propagation must track changing wait relationships and object generations. The implementation includes distinct locking policies and debug machinery for chained boosting and unboosting.
- **C2:** One turnstile framework supports kernel mutexes, user locks, synchronous IPC, workqueues, and workloops, with policy tables separating these uses. This is useful for understanding how a hybrid kernel shares scheduling machinery across API families.
- **C3:** Configurable hash-table sizing, bounded propagation settings, and development statistics make the costs of this shared mechanism inspectable.

### [haiku/haiku](https://github.com/haiku/haiku)

**Language/role:** C++ and C, with assembly; personal-computing OS with its kernel in `src/system/kernel/`. **Project GitHub mirror**; the repository directs contributions to Haiku's review infrastructure.

Study the [VM cache implementation](https://github.com/haiku/haiku/blob/master/src/system/kernel/vm/VMCache.cpp), particularly resizing, moving pages between caches, and flushing cached pages. The project's [overview](https://github.com/haiku/haiku/blob/master/ReadMe.md) establishes its desktop OS scope.

- **C1:** Resizing can temporarily release the cache lock while waiting for busy pages. Shrinking must clear the unused tail of a partial page; flushing must distinguish dirty, busy, and still-mapped pages and restart traversal after waiting.
- **C2:** `VMCache` supplies common page ownership, backing-store, commitment, and I/O interfaces across anonymous, vnode-backed, device, and other cache types. It illustrates a substantial C++ abstraction at a kernel boundary rather than a wrapper around one special case.

### [reactos/reactos](https://github.com/reactos/reactos)

**Language/role:** Primarily C and C++, with assembly; Windows NT-compatible OS. The relevant kernel/executive is `ntoskrnl/`; the surrounding OS is counted only once.

The [object-handle implementation](https://github.com/reactos/reactos/blob/master/ntoskrnl/ob/obhandle.c) is a useful entry to an API family distinct from Unix. The repository describes compatibility with Windows applications and drivers as its purpose; this is an implementation target, not a claim of complete compatibility.

- **C1:** Handle-table access uses process rundown protection so teardown cannot invalidate an in-use table. The code differentiates user and kernel handles, handles pseudo-handles, and combines reference counting with critical regions and handle-entry locking.
- **C2:** A common object manager implements handle creation, duplication, destruction, attributes, and lifetime management. These operations serve many kernel object types rather than exposing separate ad hoc resource-management APIs.

Read the failure paths as well as the successful lookups: compatibility includes access-mode and error behavior, not only matching function names.

### [SerenityOS/serenity](https://github.com/SerenityOS/serenity)

**Language/role:** Primarily C++; graphical Unix-like OS for x86-64, Arm, and RISC-V, with the kernel in `Kernel/`. The complete system monorepo is one entry.

The [virtual filesystem implementation](https://github.com/SerenityOS/serenity/blob/master/Kernel/FileSystem/VirtualFileSystem.cpp) demonstrates how typed ownership and error handling interact with Unix path semantics. The [project overview](https://github.com/SerenityOS/serenity/blob/master/README.md) identifies preemptive threading, POSIX interfaces, and the broader OS role.

- **C1:** The implementation explicitly protects filesystem discovery and creation with a mutex to avoid a time-of-check/time-of-use race while disk access may occur. Mount validation and process-specific unveiled-path checks add adversarial-input constraints.
- **C2:** Filesystem, custody, open-file-description, mount, and root-context abstractions connect disk filesystems, pseudo-filesystems, and FUSE/Plan 9 interfaces. `ErrorOr` and reference-counted ownership are visible throughout the common code path.

## Rust kernels and language-oriented research

### [redox-os/kernel](https://github.com/redox-os/kernel)

**Language/role:** Rust and assembly; Redox microkernel. **Official substantive GitHub mirror** of the Redox GitLab repository identified in its description; other Redox components are outside this entry.

Study [userspace scheme mediation](https://github.com/redox-os/kernel/blob/master/src/scheme/user.rs): requests cross into userspace services, carry file descriptors or mapped-memory responsibilities, and return through typed completion states.

- **C1:** The implementation tracks waiting, cancellation, response, and mapping states with weak context references and locked request storage. Completion parsing rejects invalid operation and flag encodings, while ownership must survive process/service lifetime changes.
- **C2:** Schemes provide a common route for file-like operations implemented by userspace services; the protocol supports ordinary results, descriptor transfers, events, and memory mapping.
- **C3:** The source explains direct switching to a service context as an optimization and discusses its interaction with scheduler heuristics. This supplies a concrete tradeoff to study without treating the source's benchmark comments as independently validated measurements.

### [asterinas/asterinas](https://github.com/asterinas/asterinas)

**Language/role:** Rust; Linux-compatible general-purpose kernel and development framework. Relevant subsystems are the `kernel` services and the OSTD foundation. Its stated production-grade objective remains a goal, not an assurance of deployment readiness.

The [framekernel architecture document](https://asterinas.github.io/book/kernel/the-framekernel-architecture.html) explains a single-address-space design divided into a low-level framework and services written in safe Rust. The [repository overview](https://github.com/asterinas/asterinas/blob/main/README.md) describes Linux ABI goals and different support/testing tiers for x86-64, Arm64, RISC-V, and LoongArch.

- **C1:** Framework API soundness is the central obligation: arbitrary safe callers must not be able to trigger undefined behavior through its interfaces. Isolating unsafe code narrows the memory-safety review boundary; it does not prove all logical kernel behavior correct.
- **C2:** OSTD is intended to support memory management, drivers, and other kernel services through safe APIs and can underpin other framekernel designs.
- **C3:** Shared memory and function calls avoid mandatory process-boundary communication between services, while the architecture explicitly requires low-overhead framework abstractions.

### [DragonOS-Community/DragonOS](https://github.com/DragonOS-Community/DragonOS)

**Language/role:** Primarily Rust, with low-level C/assembly; independently implemented Linux-compatible kernel oriented toward cloud workloads. It remains a developing OS, and its compatibility ambitions should not be read as complete Linux equivalence.

The [address-space implementation](https://github.com/DragonOS-Community/DragonOS/blob/master/kernel/src/mm/ucontext/address_space.rs) is especially instructive because it documents interactions among page faults, unmapping, remote access, teardown, and TLB shootdowns.

- **C1:** The code distinguishes page-accounting changes from actual reclamation after TLB invalidation. Generation counters, active-CPU masks, explicit teardown state, and separate page-table edit locks encode cross-CPU lifetime rules. RISC-V instruction-cache comments explain why clearing a stale bit can lose a concurrent writer's update.
- **C2:** `AddressSpace` combines mappings, file-backed memory, shared memory, access checks, and lifecycle state for use by multiple process and memory operations.
- **C3:** A stable page-table physical address permits scheduler access without taking the main address-space lock; CPU masks limit shootdown targeting. The performance choices are tied directly to documented invariants.

### [theseus-os/Theseus](https://github.com/theseus-os/Theseus)

**Language/role:** Rust research OS; kernel components are individual crates under `kernel/`. **Quiet research tree:** GitHub metadata showed its last repository push in September 2024, so this guide does not repeat the README's unqualified active-development wording.

Study how language-level lifetimes can shape kernel interfaces through [memory management](https://github.com/theseus-os/Theseus/blob/theseus_main/kernel/memory/src/lib.rs) and [crate/module management](https://github.com/theseus-os/Theseus/blob/theseus_main/kernel/mod_mgmt/src/lib.rs).

- **C1:** `MappedPages` connects mapped-region lifetimes to Rust ownership; allocation helpers also document lock dependencies. Module management must preserve loaded sections and symbols while crates are shared, and explicitly discusses non-overlap requirements for thread-local storage.
- **C2:** `CrateNamespace` groups linked crates and their symbols, supports recursive dependencies, and can express application groups or OS personalities. Strong references keep crates alive across shared namespaces.

This is a substantive alternative OS-structure experiment, not a Linux-compatible replacement. The value lies in examining the tradeoffs of language-enforced ownership and dynamic composition.

## Microkernels and multiserver systems

### [HelenOS/helenos](https://github.com/HelenOS/helenos)

**Language/role:** Primarily C and assembly; portable microkernel and multiserver OS. Relevant code spans `kernel/` and userspace servers; the repository is counted once.

The [project overview](https://github.com/HelenOS/helenos/blob/master/README.md) describes filesystem, networking, driver, and GUI components communicating through messages, and explicitly favors its own design over cloning an existing API. Start implementation study at [kernel IPC](https://github.com/HelenOS/helenos/blob/master/kernel/generic/src/ipc/ipc.c).

- **C1:** An interrupted synchronous call can race with its reply. The IPC code distinguishes answering from forgetting a request, tracks object references through connection setup and destruction, and uses separate locks for several parts of call state.
- **C2:** Phones, answerboxes, call objects, and notifications constitute common communication machinery for many independently running system services. Synchronous helpers build on this shared mechanism rather than defining an unrelated channel model.

The architecture makes service boundaries and failure containment inspectable; it does not imply that every service failure is automatically recoverable.

### [Stichting-MINIX-Research-Foundation/minix](https://github.com/Stichting-MINIX-Research-Foundation/minix)

**Language/role:** C and assembly; MINIX 3 microkernel under `minix/kernel/`, with system servers under `minix/servers/`. **Official automatically replicated repository.** GitHub metadata showed its last repository push in March 2024; retain it as a substantial research/historical implementation without assuming current maintenance.

Read [kernel process/IPC machinery](https://github.com/Stichting-MINIX-Research-Foundation/minix/blob/master/minix/kernel/proc.c) together with [the reincarnation server](https://github.com/Stichting-MINIX-Research-Foundation/minix/blob/master/minix/servers/rs/main.c).

- **C1:** Kernel endpoints and privilege state must remain meaningful as processes change. Above that boundary, the reincarnation server distinguishes heartbeat notifications, clock events, administrative requests, and service-ready responses, with separate fresh-start, restart, and live-update initialization paths.
- **C2:** A shared service-management framework supports starting, stopping, monitoring, restarting, cloning, and updating services. Its use across system services illustrates how reliability mechanisms can be moved out of the kernel while relying on kernel IPC and protection.

### [managarm/managarm](https://github.com/managarm/managarm)

**Language/role:** Primarily C++; asynchronous microkernel OS. The Thor kernel lives under `kernel/thor/`, while drivers and servers provide the surrounding system.

The [project overview](https://github.com/managarm/managarm/blob/master/README.md) describes a separately implemented kernel with POSIX/Linux API support. The [Hel ABI definitions](https://github.com/managarm/managarm/blob/master/hel/include/hel.h) expose the actual descriptor, queue, memory, and thread contracts.

- **C1:** Shared submission/completion queues define which side writes each field, atomic notification-bit operations, progress markers, cancellation, and contract-violation reporting. Correctness depends on a coordinated protocol across the kernel/userspace boundary.
- **C2:** Descriptor rights and common asynchronous operations cover messages, clocks, events, memory changes, thread observation, and DMA-related operations. They support many servers and drivers without requiring a separate blocking protocol for each.
- **C3:** The design explicitly addresses microkernel communication costs through asynchronous APIs and shared queue structures. This provides a concrete performance-oriented architecture without asserting a universal advantage over monolithic kernels.

### [seL4/seL4](https://github.com/seL4/seL4)

**Language/role:** C and assembly; capability microkernel, **not a complete general-purpose OS**. Its inclusion is bounded: the official [2025 Sculpt/Genode presentation description](https://www.sel4.systems/Summit/2025/abstracts2025.html) documents an experimental general-purpose Sculpt system on seL4 and explains that this combination was not then officially supported by Sculpt.

Useful entry points are [capability semantics](https://docs.sel4.systems/Tutorials/capabilities.html) and [capability-space lookup](https://github.com/seL4/seL4/blob/master/src/kernel/cspace.c).

- **C1:** Capability lookup checks root object type, lookup depth, guard bits, and unresolved address bits, producing distinct failure information. These checks sit on an authority boundary, where a lookup mistake changes which kernel object a caller can control.
- **C2:** Capabilities give a uniform authority model for kernel objects; capability-space construction separates possession of authority from raw object addresses. The tutorial connects copying and manipulating capabilities to object access.

The repository participates in a formal-verification ecosystem, but this selection does not assert that every architecture, configuration, or surrounding userspace system is verified.

## Alternative namespaces and smaller complete systems

### [9front/9front](https://github.com/9front/9front)

**Language/role:** C and architecture-specific assembly; Plan 9-derived general-purpose OS, with kernel code under `sys/src/9/`. **Official project nightly-synchronized GitHub mirror**, pointing to its upstream Git service. It represents the separately evolved 9front system; no second Plan 9 copy is counted.

Read the [bind/mount interface](https://github.com/9front/9front/blob/front/sys/man/2/bind) alongside [channel and namespace implementation](https://github.com/9front/9front/blob/front/sys/src/9/port/chan.c).

- **C1:** Mount lists have several independent references. The implementation explains why mount-head reference counts and reader/writer locks must cooperate during unmount and namespace teardown; binding a union directory also requires careful creation and ordering semantics.
- **C2:** Per-process namespace groups, union directories, and file-server mounts provide a coherent way to compose resources. The mount interface translates file operations into 9P messages over a file descriptor, unifying local naming with remote services.

This is a useful alternative to assuming that global filesystem layout and conventional Unix process environments are inevitable kernel interfaces.

### [klange/toaruos](https://github.com/klange/toaruos)

**Language/role:** Primarily C and assembly; complete independent OS with the Misaka kernel in `kernel/`. Its desktop and userspace are context, not separate repository entries.

The [project overview](https://github.com/klange/toaruos/blob/master/README.md) describes the x86-64/ARMv8 scope and the 2020–2021 kernel rewrite. The [process implementation](https://github.com/klange/toaruos/blob/master/kernel/sys/process.c) explains the actual task model.

- **C1:** Nested kernel preemption requires preserving both kernel state and an outer interrupted context. Runnable, sleeping, and deferred-reaping queues have separate synchronization, and finished tasks must be handled correctly during dispatch.
- **C2:** Internally, a “process” is a schedulable thread; a POSIX process is a collection sharing paging, signal, and descriptor tables. Kernel tasklets reuse the scheduling machinery. This separation is useful for studying how a small implementation represents several public execution concepts.

The source is substantial yet compact enough to follow across scheduling and process lifecycle boundaries; the project's own overview acknowledges incomplete POSIX coverage.

### [minoca/os](https://github.com/minoca/os)

**Language/role:** Primarily C and assembly; independently written, POSIX-like general-purpose OS with the kernel in `kernel/`. **Historical official GitHub source tree:** the observed last repository push was December 2021. Current maintenance is not established.

The [repository overview](https://github.com/minoca/os/blob/master/README.md) explains its application and driver model. A concrete study target is [memory descriptor lists](https://github.com/minoca/os/blob/master/kernel/mm/mdl.c), shared between kernel and boot environments.

- **C1:** Descriptor insertion can override firmware-supplied regions. The implementation clips, splits, and replaces overlapping ranges while preserving address ordering, total/free-space accounting, and allocation-failure behavior.
- **C2:** One documented descriptor-list interface supports adding regions, finding constrained allocations, iterating, and destroying maps. It separates memory-range policy from individual boot or kernel consumers.
- **C3:** Red-black-tree indexing and free-size bins make the search/allocation strategy visible. The source is useful for studying a reusable range allocator under fragmentation and alignment constraints.

### [mikaku/Fiwix](https://github.com/mikaku/Fiwix)

**Language/role:** C and assembly; independent i386 Unix-like kernel. It targets mostly POSIX behavior and much of the Linux 2.0 i386 syscall ABI, not contemporary Linux compatibility in full. Although educational in intent, it implements a substantial kernel rather than a tutorial skeleton.

Study [page-fault handling](https://github.com/mikaku/Fiwix/blob/master/mm/fault.c) and the [versioned change history](https://github.com/mikaku/Fiwix/blob/master/Changes).

- **C1:** Fault handling distinguishes copy-on-write from genuine read-only violations, handles shared-page reference counts, invalidates TLB entries, and unwinds failed file-backed page population.
- **C3:** Demand paging, shared cached file pages, and avoiding unnecessary copies when a copy-on-write page becomes singly referenced expose performance mechanisms in a comparatively small implementation.
- **C4:** Dated releases from 2018 through 2025 document continuing syscall/filesystem additions, compatibility with newer compilers, and fixes to low-memory and resource-lifetime behavior. The top development section has an unfinished release date and is not treated here as a completed release.

## General-purpose Unix on constrained machines

### [EtchedPixels/FUZIX](https://github.com/EtchedPixels/FUZIX)

**Language/role:** C and substantial target-specific assembly; Unix-style kernel for small machines, including banked-memory 8-bit systems. **Archived repository**, retained explicitly as a substantive historical implementation. The README also warns about incomplete platform/toolchain work.

The [memory-management design](https://github.com/EtchedPixels/FUZIX/blob/master/docs/MemoryManagement.md) and [process/scheduling implementation](https://github.com/EtchedPixels/FUZIX/blob/master/Kernel/process.c) reveal constraints that conventional MMU-based kernels largely avoid.

- **C1:** Process sleep/wakeup transitions must keep runnable counts consistent while interrupts and signals intervene. The source includes checks for accounting errors and platform-specific context-switch boundaries.
- **C2:** A common allocation, resizing, release, and accounting contract hides banked or otherwise platform-specific memory layouts from the core kernel. Fixed-bank helpers also support swapping.
- **C3:** Scheduling explicitly avoids forcing immediate rescheduling on every wakeup because context switching is expensive on these targets. Reusing scarce disk-cache buffers for temporary storage and avoiding unnecessary switches show concrete memory and execution-cost tradeoffs.

### [ghaerr/elks](https://github.com/ghaerr/elks)

**Language/role:** C and 8086-family assembly; separately evolved early Linux derivative for IA16 machines. The kernel is in `elks/`, with userspace and tools alongside it. Despite its embedded name, its shell, filesystems, networking, and application environment also serve general-purpose retro PCs.

Start with [segment allocation](https://github.com/ghaerr/elks/blob/master/elks/arch/i86/mm/malloc.c) and the [platform porting guide](https://github.com/ghaerr/elks/blob/master/Documentation/text/porting-guide.txt).

- **C1:** Segment allocation must coordinate address/size accounting, splitting and merging, reference counts, and real-mode versus protected-mode representations. The source explicitly distinguishes a physical paragraph address from a selector and documents descriptor-allocation limits.
- **C2:** Allocation and platform interfaces support different hardware configurations, while the porting guide identifies shared console APIs and platform-specific interrupt, timer, disk, and serial implementations.
- **C3:** Best-fit free-segment search, local-memory descriptors, and segment-size constraints expose memory-fragmentation and access-cost decisions. Protected-mode support should not be mistaken for full user/kernel isolation: the inspected allocator comments explicitly describe ring-0 user code in that configuration.

## Coverage, search method, and limitations

Discovery used more than six distinct live-web search formulations: mainstream Linux/BSD kernel families; Rust general-purpose and Linux-compatible kernels; microkernel/multiserver systems; independent desktop and Windows-compatible OSes; RISC-V and cloud-oriented kernels; asynchronous C++ kernels; Plan 9 derivatives; 8-/16-bit Unix systems; and additional Ada, Zig, and managed-language searches. Focused follow-ups covered Managarm, ToaruOS, Minoca, ELKS, FUZIX, Fiwix, and seL4's general-purpose-system use. Later language-oriented searches produced mostly tutorial kernels, bibliographies, or out-of-scope systems, while further Plan 9 searches mainly overlapped the selected design family; those additions did not improve the selection sufficiently.

Every retained canonical repository URL was opened through its GitHub page or checked through the public GitHub API. Repository metadata established mirror/archive status and helped identify quiet trees. Each entry also rests on separately read implementation or architectural material, not merely a search snippet or a second copy of its README. Source files were fetched individually; no candidate repositories were cloned, built, or executed. Branch links describe the inspected source location and may evolve after the research date.

The selection spans C, C++, Rust, and assembly; monolithic, hybrid, microkernel, and language-oriented structures; and architectures ranging from banked 8-bit/IA16 machines to x86-64, Arm, RISC-V, and broader portable families. Coverage is intentionally stronger where substantive official GitHub source and implementation documentation could both be verified. No language quota was filled with weaker projects.

Excluded were Linux distributions and vendor forks without a distinct kernel design to justify duplication; framework-only projects as separate kernel entries; RTOSes and application-specific unikernels; tutorial kernels such as xv6-style teaching exercises; repository lists; and unofficial mirrors offered as substitutes for a verifiable official GitHub tree. GNU Hurd and Fuchsia were not retained because this search did not establish a suitable official substantive GitHub repository for the relevant current implementation. Genode informed the seL4 scope check but was not counted as another kernel. Additional Plan 9 descendants were not included merely to repeat shared ancestry.

Activity metadata is a snapshot, not a support guarantee. FUZIX is archived, and Theseus, MINIX, and Minoca are explicitly qualified as quiet or historical. The report makes no independently measured performance claims, does not infer full ABI compatibility from project ambitions, and does not treat language safety or formal verification as proof of an entire OS. Statements about what an engineer can learn are grounded interpretations of the cited code, rather than claims made by maintainers about uniform code quality.
