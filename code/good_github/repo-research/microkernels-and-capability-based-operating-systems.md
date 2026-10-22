# Microkernels and capability-based operating systems

Research date: 2026-10-09.

This guide selects 23 substantive GitHub repositories spanning capability kernels, multiserver operating systems, persistent and distributed capability systems, and embedded isolation runtimes. It includes system-construction frameworks when their abstractions are central to building a microkernel OS. Microkernel organization and capability security are separate properties; inclusion does not imply that every project implements both. The discussion identifies particular engineering mechanisms worth studying, not uniform correctness or production readiness.

Canonical repository pages or GitHub API records and additional primary documentation or implementation files were inspected. Historical projects, frozen archives, and official mirrors are identified below. Recent repository activity was checked, but is not treated as evidence of release support, security assurance, or C4 by itself.

## Criteria legend

- **C1 — Difficult correctness:** authority, ownership, concurrency, adversarial inputs, recovery, or other demanding invariants.
- **C2 — Reusable abstractions:** substantial interfaces or mechanisms that support multiple services, applications, or system configurations.
- **C3 — Structured performance engineering:** concrete latency, throughput, memory, or hardware constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** evidence of years of development accompanied by compatibility work, testing, or explicit complexity management.

## Capability kernels and system-construction frameworks

### [seL4/seL4](https://github.com/seL4/seL4)

**Language / role:** C and assembly; capability microkernel.

Study how a small kernel exposes authority over threads, interrupts, and memory without making object identity equivalent to permission. The [capability documentation](https://docs.sel4.systems/Tutorials/capabilities.html) explains CSpaces, CNodes, capability slots, and multiple capabilities with different rights to the same object.

**C1:** The [CNode implementation](https://github.com/seL4/seL4/blob/master/src/object/cnode.c) validates invocation lengths, source lookup depth, destination emptiness, and capability derivation before committing changes. Copy and mint operations mask rights; invalid derivations fail explicitly. These are concrete authority-preservation and hostile-input invariants.

**C2:** The same capability machinery controls kernel objects, abstract resources such as interrupt authority, and untyped memory used for allocation. Engineers can study a general resource-management substrate rather than a permission mechanism attached to one service. The documentation and CNode source are complementary entry points into the public model and its enforcement.

### [seL4/microkit](https://github.com/seL4/microkit)

**Language / role:** Rust tooling and C runtime; system-construction framework above seL4.

Microkit is useful for understanding how a general capability kernel becomes a tractable application architecture. Its [manual](https://github.com/seL4/microkit/blob/main/docs/manual.md) specifies protection domains, channels, memory regions, scheduling parameters, fault relationships, and virtual machines through a system description.

**C1:** Protected calls follow increasing priorities, constraining the call graph; notifications can coalesce and therefore require careful event semantics. Scheduling budgets and periods make execution resources explicit. The manual also distinguishes required bounded execution from what the runtime actually enforces, a valuable specification boundary.

**C2:** Protection domains, shared regions, notifications, protected procedures, and VM management form reusable building blocks for drivers and services. The declarative description ties authority and memory placement to deployment. This is a separate system layer from the seL4 kernel, not another kernel implementation, and application correctness does not follow automatically from the underlying kernel's assurances.

### [kernkonzept/fiasco](https://github.com/kernkonzept/fiasco)

**Language / role:** C++ and assembly; the Fiasco microkernel underlying L4Re.

The [thread IPC implementation](https://github.com/kernkonzept/fiasco/blob/master/src/kern/thread-ipc.cpp) is a substantial study of the interaction between scheduling, synchronous communication, timeouts, and multiple CPUs.

**C1:** Sender queues, receiver readiness, timeout setup, cross-CPU activation, and reply-capability cleanup interact with thread state transitions. In particular, timeout handling must avoid leaving reply references pointing at invalid state. The code exposes the locking and cleanup conditions rather than hiding them behind a generic messaging API.

**C3:** Direct context switches are guarded by conditions including CPU locality, willingness to donate execution time, pending senders, and receive-timeout status. This makes the optimization's eligibility and fallback behavior inspectable. It is a useful example of retaining a short IPC path while preserving the slower cases needed for cancellation, scheduling, and contention.

### [kernkonzept/l4re-core](https://github.com/kernkonzept/l4re-core)

**Language / role:** C and C++; capability-oriented userspace runtime and services for L4Re.

Study the separation between physical backing resources and virtual-address-space policy. [Dataspaces and region maps](https://l4re.org/doc/l4re_concepts_ds_rm.html) explain how dataspaces represent memory-like objects while region mappers attach them to address ranges and handle page faults.

**C1:** User-level paging must preserve mapping permissions and correctly resolve faults. The [naming and capability model](https://l4re.org/doc/l4re_concepts_naming.html) further separates per-task capability names from global names; initial capabilities determine the environment in which a task can operate.

**C2:** Dataspaces cover resources such as RAM, executable contents, and device memory. Region maps, namespace objects, and capability transfer let many kinds of servers use a common resource model. This repository is retained for its userspace abstractions; the Fiasco entry covers the underlying kernel's IPC and scheduling machinery.

### [genodelabs/genode](https://github.com/genodelabs/genode)

**Language / role:** Primarily C++; component OS framework and capability-based service infrastructure.

**Status:** Official, substantive frozen GitHub archive. The repository was archived in May 2026 and announces migration to Codeberg; it is not a current updating GitHub mirror. Its retained source tree remains useful for historical study.

**C1:** The [generic root component](https://github.com/genodelabs/genode/blob/master/repos/base/include/root/component.h) handles session-creation policy, allocation failures, error conversion, and cleanup when construction fails. Session shutdown removes the RPC object from its entrypoint before destruction. These paths show how resource and object-lifetime invariants survive partial failure.

**C2:** The [session-object abstraction](https://github.com/genodelabs/genode/blob/master/repos/base/include/base/session_object.h) combines typed RPC interfaces with client-supplied RAM and capability quotas. The root component supports creation, upgrades, and closure across service types. Study how a reusable service framework makes the cost of serving clients explicit, rather than treating server-side allocation as unaccounted ambient authority.

### [udosteinberg/NOVA](https://github.com/udosteinberg/NOVA)

**Language / role:** C++ and assembly; capability microhypervisor.

NOVA separates a small privileged substrate from userspace applications and virtualization services. Its repository describes an experimental system, so it should not be read as a turnkey virtualization product.

**C1:** The [object-space implementation](https://github.com/udosteinberg/NOVA/blob/release/src/space_obj.cpp) connects capability installation with successful object-reference acquisition. Sparse table construction uses compare-and-exchange and frees a newly allocated table when another CPU wins the installation race. Capability updates, concurrent allocation, and lifetime management are tightly coupled.

**C2:** Object spaces and selectors supply a common authority mechanism for the execution and communication resources needed by applications and virtual machines.

**C3:** The same source shows lazy construction of a multilevel capability table: backing storage is allocated as needed rather than for every possible selector. It provides a compact entry point into the relationship between memory footprint, lookup structure, and concurrent mutation.

### [cyberus-technology/hedron](https://github.com/cyberus-technology/hedron)

**Language / role:** C++ and assembly; capability microhypervisor derived from NOVA.

**Status:** Official mirror of internally developed code; the public repository's last push observed in GitHub metadata was October 2023. Its README describes substantial divergence from NOVA beginning in 2015, so it is included as a separate implementation lineage, without assuming that the public snapshot tracks current internal work.

**C1:** The [implementation notes](https://github.com/cyberus-technology/hedron/blob/master/docs/implementation.md) explain multicore boot serialization and an object-lifetime scheme combining reference counts with RCU grace periods. Pre-free and final reclamation are distinct phases.

**C3:** Deferring reclamation until CPUs pass suitable quiescent states avoids requiring atomic reference operations for every transient kernel reference. The notes connect that optimization to its lifetime assumptions.

The [versioned changelog](https://github.com/cyberus-technology/hedron/blob/master/CHANGELOG.md) is also an important entry point: API revisions remove or change facilities including scheduling and IOMMU support. Do not project the feature set of another NOVA descendant onto this snapshot.

## Persistent, distributed, and heterogeneous capability systems

### [capros-os/capros](https://github.com/capros-os/capros)

**Language / role:** Primarily C; persistent object-capability operating system descended from EROS.

**Status:** Historical research system; the public repository's last push observed was July 2022. The [official project site](https://www.capros.org/) identifies the GitHub repository and its persistent capability model.

**C1:** The [checkpoint design](https://www.capros.org/design-notes/Checkpoint.html) addresses crash consistency through generation boundaries, reservation of log space before objects become dirty, ordering of object and directory writes, and alternating checkpoint headers. The interaction with migration and reserved space exposes failure modes beyond ordinary filesystem serialization.

**C2:** The [address-space design](https://www.capros.org/devel/ObRef/concepts/AddressSpaces.html) builds mappings from capability-linked nodes and pages, with permissions and keepers participating in fault handling. Persistent objects and programmable address spaces are reusable foundations for services whose state outlives processes.

The documentation retains historical terminology and some design discussion. Its value is the explicit reasoning about persistence and authority, not a claim that every proposed mechanism is complete.

### [BarrelfishOS/barrelfish](https://github.com/BarrelfishOS/barrelfish)

**Language / role:** Primarily C; research multikernel with distributed capability management.

**Status:** Official historical GitHub mirror. The [project documentation page](https://barrelfish.org/documentation.html) states that Barrelfish is no longer actively developed.

The central study opportunity is how a machine with multiple kernel instances maintains authority over shared physical resources.

**C1:** The [capability-management technical note](https://barrelfish.org/publications/TN-013-CapabilityManagement.pdf) discusses retyping memory into objects, overlap and ancestry constraints, and the complications of copying and revoking capabilities across cores. Local metadata is insufficient when descendants and copies exist elsewhere.

**C3:** The note makes the tradeoff between bounded kernel execution and more involved monitor-level operations explicit, and describes the mapping database used to track capability relationships.

This is a multikernel rather than a conventional single microkernel. The technical note includes limitations and design alternatives; those sections should not be mistaken for implemented guarantees. It is particularly useful for studying the point at which local capability invariants become distributed protocols.

### [Barkhausen-Institut/M3](https://github.com/Barkhausen-Institut/M3)

**Language / role:** Primarily Rust; hardware/OS co-design for heterogeneous tiles.

This is the current official M³ repository. The older TUD-OS repository is archived and points to it; the two are counted once.

**C1:** The [kernel capability-table code](https://github.com/Barkhausen-Institut/M3/blob/master/src/kernel/src/cap/caps.rs) handles selector ranges, capability inheritance, activity state, and kernel-memory quotas. Checks for occupied selectors, dead activities, and exhausted quotas make authorization inseparable from lifecycle and resource accounting.

**C2:** Activities represent both ordinary programs and accelerator work. The [architecture description](https://github.com/Barkhausen-Institut/M3/blob/master/README.md) explains a common trusted communication unit, or TCU, at each tile, so heterogeneous compute units can access message-passing and shared-memory services through the same model.

**C3:** The kernel configures TCU endpoints; subsequent permitted communication proceeds directly through the TCU without kernel involvement. Study the separation of authority setup from the data path. These mechanisms assume the project's hardware model or its simulation, not an arbitrary stock processor.

## Multiserver operating systems and OS personalities

### [HelenOS/helenos](https://github.com/HelenOS/helenos)

**Language / role:** Primarily C; complete microkernel-based multiserver OS.

HelenOS offers a broad view of the consequences of moving system services into separate processes: filesystems, networking, drivers, and the graphical environment use the system's IPC facilities.

**C1:** The [IPC architecture documentation](https://www.helenos.org/index.fcgi/wiki/IPC) describes routing replies and incoming calls through an asynchronous framework while connection-handling fibrils suspend and resume. Shared-memory and data-transfer operations use negotiated protocols rather than unchecked pointers across protection boundaries.

**C2:** The same framework turns low-level phones and answerboxes into reusable connections and request-handling patterns. Engineers can study how user-level fibrils let server code retain a sequential style while multiple requests remain in flight.

This is a useful complement to kernel-only repositories: its most instructive abstraction is the bridge from kernel messages to manageable concurrent service implementations. The IPC documentation is the recommended architectural entry point.

### [managarm/managarm](https://github.com/managarm/managarm)

**Language / role:** Primarily C++; asynchronous microkernel OS with userspace services and a POSIX compatibility layer.

The relevant monorepo subsystems are the kernel, Hel interface, service protocols, drivers, and POSIX server; they are counted as one repository.

**C1:** The [Hel API header](https://github.com/managarm/managarm/blob/master/hel/include/hel.h) exposes object-specific access rights, asynchronous completion semantics, cancellation, and error cases such as remote faults. Correct use requires coordinating descriptor authority with operation and completion lifetimes.

**C2:** Lanes, queues, memory objects, address spaces, interrupts, and threads use a common descriptor-oriented interface. The same vocabulary supports higher-level servers instead of requiring each subsystem to invent its own kernel interaction model.

Study the API header as a contract between the kernel and asynchronous userspace code. The project's POSIX/Linux compatibility aims should be distinguished from complete behavioral compatibility with every Linux application.

### [Stichting-MINIX-Research-Foundation/minix](https://github.com/Stichting-MINIX-Research-Foundation/minix)

**Language / role:** Primarily C; MINIX 3 microkernel and multiserver OS, within a larger source tree.

**Status:** Official GitHub replica of the project's Gerrit repository. The last public push observed was March 2024; this entry does not imply a currently supported distribution release.

Focus on the MINIX kernel and service framework rather than treating all imported userspace code as microkernel-specific.

**C1:** The [reincarnation server](https://github.com/Stichting-MINIX-Research-Foundation/minix/blob/master/minix/servers/rs/main.c) coordinates service monitoring, restart, refresh, and update requests, alongside boot-time endpoint and privilege setup. Failure recovery is an explicit OS responsibility with lifecycle state and authority checks.

**C2:** Shared service initialization and lifecycle callbacks provide reusable machinery for servers and drivers. The [reliability architecture](https://wiki.minix3.org/doku.php?id=www:documentation:reliability) explains user-mode drivers, restricted kernel-call and IPC permissions, and supervised recovery.

The architecture page mixes implemented and historically planned behavior. Use it to understand the decomposition, and the server source to inspect actual control paths.

### [redox-os/kernel](https://github.com/redox-os/kernel)

**Language / role:** Rust and assembly; Redox microkernel.

**Status:** Official substantive GitHub mirror; the project identifies GitLab as its upstream development location.

The [userspace scheme implementation](https://github.com/redox-os/kernel/blob/master/src/scheme/user.rs) is a strong entry point into the kernel/server boundary, rather than just the scheduler or boot code.

**C1:** Requests move through explicit waiting and response states. Submission and completion records need validation, pending file descriptions remain owned across calls, and cancellation affects which side must release mapped resources. These are concrete invariants at an untrusted service boundary.

**C3:** The code includes direct switches to a scheme handler to avoid parts of ordinary scheduling and locking. Comments also discuss interference with scheduling heuristics and the cases where a direct switch cannot proceed. This makes the performance tradeoff inspectable without relying on benchmark percentages.

Study this file for the relationship between synchronous-looking resource operations, asynchronous server completion, and safe cleanup when a caller disappears.

### [Nils-TUD/Escape](https://github.com/Nils-TUD/Escape)

**Language / role:** Primarily C++; independent microkernel OS with userspace drivers and several architecture ports.

Escape is a less prominent but substantial system for studying how familiar file operations become service protocols. The relevant entry point is its [VFS channel implementation](https://github.com/Nils-TUD/Escape/blob/master/source/kernel/src/vfs/channel.cc).

**C1:** Reads and writes coordinate reply messages with cancellation. When a reply is already ready, the implementation changes receive behavior to finish the protocol consistently; when cancellation is unsupported, it forces blocking. Channel closure, driver disappearance, reference counts, and descriptor-transfer error cleanup interact in the same code.

**C2:** The channel abstraction maps open, read, write, size, cancellation, and descriptor delegation onto a common userspace-driver interface.

**C3:** Transfers can refer to an established shared-memory region by offset rather than sending a separate data message. The code checks buffer containment before choosing that path. This is a concrete optimization with an explicit fallback, not merely a zero-copy design aspiration. No current support commitment is inferred from repository activity.

### [cl91/NeptuneOS](https://github.com/cl91/NeptuneOS)

**Language / role:** Primarily C; experimental NT-style executive and OS personality above seL4.

The independently developed executive and driver infrastructure justify inclusion alongside the separate seL4 kernel entry. Focus on the executive described in the [developer guide](https://github.com/cl91/NeptuneOS/blob/master/docs/Developer-Guide.md), especially its object manager and process-separated driver model.

**C1:** Object-path lookup can lead to an out-of-process driver request and suspend the current service operation. The design therefore separates non-suspending parse methods from open methods that carry asynchronous thread context. Their reference-count and cleanup obligations differ, including on error.

**C2:** Object namespaces, handles, device-to-file opening, and NT-style driver requests provide reusable OS-personality abstractions above seL4 IPC.

Study how an API designed around in-kernel objects changes when drivers live in separate processes. Windows/ReactOS compatibility is an incomplete goal: the guide explicitly identifies pointer-sharing driver patterns that do not fit this model, and contains unfinished sections. This is not presented as a drop-in Windows replacement.

## Embedded isolation and capability runtimes

### [oxidecomputer/hubris](https://github.com/oxidecomputer/hubris)

**Language / role:** Rust; embedded microkernel OS with isolated tasks and userspace drivers.

The [IPC design document](https://github.com/oxidecomputer/hubris/blob/master/doc/ipc.adoc) explains why the system chooses synchronous rendezvous, memory leases, notifications, and explicit priority relationships.

**C1:** A blocked caller supplies backpressure instead of allowing a server's kernel-side message queue to grow. Leases make borrowed memory and permitted access part of the communication contract. Priority restrictions address specific deadlock and inversion risks; they are not a blanket proof that application protocols cannot deadlock.

**C3:** Rendezvous permits a single copy of message data and avoids maintaining arbitrary queues in the kernel. The document explains the resource and latency reasons for these choices, including their consequences for server structure.

Hubris is useful for engineers studying deterministic resource use on microcontrollers, where the cost of each task, buffer, and communication path matters as much as a general-purpose scheduling policy.

### [betrusted-io/xous-core](https://github.com/betrusted-io/xous-core)

**Language / role:** Rust; Xous microkernel, loader, and userspace services for security-oriented embedded devices.

**C1:** The [0.9 release history](https://github.com/betrusted-io/xous-core/blob/dev/RELEASE-v0.9.md) documents a page-ownership fix that exposed a conflict between execute-in-place mappings and code inspection for signing. The resulting loader/signature changes also addressed a time-of-check/time-of-use problem. This is unusually concrete evidence of kernel ownership rules interacting with boot and update security.

**C2:** The [API guide](https://github.com/betrusted-io/xous-core/blob/dev/API.md) distinguishes scalar messages, blocking replies, and memory lending, providing reusable patterns for service boundaries and connection management.

**C3:** Memory-lending and archived-data access reduce the need to serialize and copy every structured message, while introducing ownership and lifetime obligations. Study the API guide together with the failure history: each explains constraints that are easy to miss when considering message passing only as a function-call replacement. Count the kernel and bundled services once.

### [tock/tock](https://github.com/tock/tock)

**Language / role:** Rust; embedded OS combining type-protected kernel capsules with hardware-isolated applications.

Tock belongs here for its isolation and constrained authority architecture. It is not a claim that every driver runs in a separate userspace process.

**C1:** The [architecture overview](https://github.com/tock/book/blob/master/src/doc/overview.md) distinguishes trusted kernel code, safe-Rust capsules, and applications isolated by hardware memory protection. Different boundaries depend on different enforcement mechanisms, which is the main engineering lesson.

**C2:** Capsules, hardware interfaces, and nonblocking command/completion patterns permit reusable drivers and services without allocating a thread stack to every component.

**C4:** The [2.2 changelog](https://github.com/tock/tock/blob/master/CHANGELOG.md) explicitly covers two years of development since 2.1.1 while preserving the core syscall interface and stabilized drivers. It also explains alarm-wrap semantics, stable-Rust migration, and fixes to protection-state handling. This demonstrates compatibility and complexity management through concrete changes, rather than using project age as a proxy for maturity.

### [phoenix-rtos/phoenix-rtos-kernel](https://github.com/phoenix-rtos/phoenix-rtos-kernel)

**Language / role:** C and assembly; real-time microkernel for embedded systems.

The [architecture documentation](https://docs.phoenix-rtos.com/latest/architecture/index.html) places memory, threads, IPC, and low-level I/O in the kernel while services and drivers use ports and object identifiers.

**C1:** The [message-transfer implementation](https://github.com/phoenix-rtos/phoenix-rtos-kernel/blob/master/proc/msg.c) distinguishes incomplete boundary pages from fully covered pages. Mapping permissions, allocation failures, and release paths must preserve the sender/receiver contract without exposing unrelated bytes or leaking temporary mappings.

**C3:** Full interior pages can be mapped into the recipient while partial first and last pages use temporary copied buffers. The structure directly exposes the tradeoff between copy cost and page-granularity protection.

Study this repository for a concrete embedded IPC implementation where memory protection, bulk-transfer efficiency, and predictable cleanup meet. The source evidence supports the mechanism; it does not establish a particular worst-case execution-time bound for every platform.

### [CHERIoT-Platform/cheriot-rtos](https://github.com/CHERIoT-Platform/cheriot-rtos)

**Language / role:** Primarily C++ with assembly; capability-hardware RTOS and compartment runtime.

This entry represents hardware capabilities and intra-address-space compartments, broadening the category beyond conventional process-based microkernels. It requires CHERIoT-compatible hardware or simulation.

**C1:** The [architectural FAQ](https://github.com/CHERIoT-Platform/cheriot-rtos/blob/main/docs/faq.md) explains distinct loader, switcher, scheduler, and allocator trust boundaries. Revocation is tied to when heap memory can be reused; sealed thread state constrains what the scheduler can inspect.

**C2:** Compartments exchange bounded capabilities and sealed software-object tokens. These support service interfaces with restricted authority without reducing every authorization decision to a global integer identifier or ACL lookup.

**C3:** The design distinguishes shared libraries without mutable state from full compartment calls, allowing less expensive reuse where a complete protection-domain transition is unnecessary. The FAQ is substantive architectural reading about what each privileged component can access, and why. It should not be read as a claim that arbitrary C++ becomes safe without the platform's enforcement mechanisms.

## Historical and smaller microkernel implementations

### [l4ka/pistachio](https://github.com/l4ka/pistachio)

**Language / role:** C++ and assembly; historical L4Ka::Pistachio implementation of the L4 Version 4 API.

**Status:** Historical source repository; the last public push observed was October 2019. Its importance is architectural lineage, not evidence of present platform support.

**C2:** The checked-in [white paper source](https://github.com/l4ka/pistachio/blob/master/doc/whitepaper/whitepaper.tex) explains separation of API from architecture-specific ABI, independent threads and address spaces, mapping, IPC, and kernel-provided syscall entry points. These are reusable OS-construction mechanisms.

**C3:** Virtual message registers map onto physical registers or memory according to the target architecture, addressing cache/TLB footprint while preserving a portable interface. The kernel interface page allows syscall entry mechanisms to vary without baking every hardware detail into clients.

The same historical document identifies experimental SMP limitations and says that a proposed local-IPC optimization was not implemented in the release it describes. Study those qualifications alongside the design, and do not turn early performance aspirations into current guarantees.

### [nuta/resea](https://github.com/nuta/resea)

**Language / role:** Primarily C; compact microkernel OS with userspace servers.

**Status:** Explicitly unmaintained according to the repository README, which directs readers to the author's successor project. Retained as a substantive, bounded implementation for study.

**C1:** The [IPC source](https://github.com/nuta/resea/blob/main/kernel/ipc.c) documents why a userspace message must be copied before entering a state in which a page fault could involve the pager and deadlock. It also handles sender ordering, receiver exit, and the point beyond which an operation must not fail.

**C3:** A guarded fast path handles suitable call/reply-receive combinations; readiness and pending-notification conditions determine whether the shortcut is valid. This makes optimization assumptions particularly easy to follow.

The [memory-management design](https://github.com/nuta/resea/blob/main/docs/design/memory-management.md) explains the userspace pager that gives the IPC reentrancy constraints their context. This repository is useful for following a complete interaction across a small kernel/server boundary, not as a maintained deployment recommendation.

## Coverage, search method, and limitations

Discovery used substantially more than six distinct live web-search formulations. The main search angles were:

- General capability microkernels and the seL4, L4Re, NOVA, and Genode families.
- Rust microkernels and embedded isolation systems, including Redox, Xous, Hubris, and Tock.
- Complete multiserver systems, userspace drivers, asynchronous IPC, and POSIX compatibility.
- Persistent object-capability lineages, including EROS, KeyKOS, Coyotos, and CapROS.
- Manycore and heterogeneous hardware/OS designs, particularly Barrelfish and M³.
- Real-time kernels and hardware-capability compartments, including Phoenix-RTOS and CHERIoT.
- Classical L4 implementations and smaller independent systems such as Pistachio, Escape, and Resea.
- NT personalities over seL4, and searches for official GitHub sources or mirrors of GNU Mach/Hurd and Fuchsia.

Search results were used for discovery; retained entries were checked against canonical GitHub pages/API records and opened implementation or architectural sources. Follow-up queries increasingly returned the same families, course exercises, superficial boot kernels, unrelated uses of “microkernel,” or unverified forks. Stars were not used as quality evidence.

**Repository boundaries:** Monorepos are counted once. seL4/Microkit/NeptuneOS and Fiasco/L4Re are distinct repositories with different implementation roles, not independent kernel designs. Hedron is included because its own documentation establishes substantial divergence from NOVA. [The archived TUD-OS M³ repository](https://github.com/TUD-OS/M3) is not a second entry. Genode is included only as an official frozen archive with verified substantive code remaining on GitHub; its move is prominent in its entry.

**Exclusions and limits:** GNU Mach/Hurd and Fuchsia remain relevant systems, but this search did not establish suitable official substantive GitHub mirrors for inclusion. Unverified historical copies, course-solution repositories, and minimal demonstration kernels were omitted. This is a selected engineering reading guide, not an exhaustive census or a ranking. Source inspection was read-only: no candidate was built, benchmarked, or subjected to a security audit. Criterion assessments are reasoned judgments grounded in the cited mechanisms. Branch links describe the inspected state and can change; historical documents may discuss plans separately from completed code.

