# Hypervisors and virtual machine monitors

Research date: **2026-10-09**.

This report selects **22 GitHub repositories** containing hypervisors, substantial userspace virtual machine monitors, or reusable implementations for constructing them. It covers general-purpose virtualization, cloud microVMs, embedded partitioning, capability microhypervisors, and specialized VMM libraries. Kernel monorepos are included only for their identified virtualization subsystems and count once. The selection emphasizes code worth studying; it is neither a deployment recommendation nor a claim that every component is uniformly exemplary.

Criteria used below:

- **C1 — Correctness:** difficult invariants, concurrency, hardware semantics, adversarial guest inputs, or failure recovery.
- **C2 — Abstractions:** substantial reusable interfaces or mechanisms serving multiple devices, platforms, guests, or VMM compositions.
- **C3 — Performance:** real execution, latency, memory, or I/O constraints addressed through an understandable architecture.
- **C4 — Evolution:** documented evolution accompanied by compatibility policy, testing, or explicit management of accumulated complexity. Age or recent activity alone does not qualify.

Every repository heading links to its verified canonical GitHub page. The implementation and documentation links within each entry are the recommended reading entry points; each was opened and read in addition to checking the repository itself. Interpretations about study value are grounded in those sources, rather than in star counts or unverified benchmark claims.

## General-purpose hypervisors and operating-system VMMs

### [torvalds/linux](https://github.com/torvalds/linux)

**Language/role:** C; the KVM subsystem of the Linux kernel, including architecture-specific virtualization support.

KVM is particularly useful for studying how a kernel virtualization mechanism presents a durable interface to independently developed userspace VMMs.

- **C1:** The [KVM locking documentation](https://docs.kernel.org/virt/kvm/locking.html) explains lock ordering, SRCU interactions, MMU invalidation, and fast page faults. Its discussion of an ABA-style mapping race shows why a seemingly valid atomic update can lose dirty-page information and why some fast paths must be restricted.
- **C2:** The [KVM API](https://docs.kernel.org/virt/kvm/api.html) separates system, VM, vCPU, and device operations through file descriptors and capability queries. This is a substantial boundary shared by very different VMMs, with explicit ownership and process/thread constraints.
- **C4:** The API documentation identifies Linux 2.6.22 as the point at which the basic API stabilized and describes compatibility through extensions and capability discovery. That documented compatibility mechanism, rather than the repository's age, supports the evolution criterion.

### [qemu/qemu](https://github.com/qemu/qemu)

**Language/role:** Primarily C; full-system machine emulation and VMM implementation. **Official GitHub mirror** of the QEMU project.

The relevant scope is QEMU's system emulator and virtualization machinery. Its translated execution path is valuable even when the reader's eventual interest is hardware-assisted virtualization: it makes guest concurrency and host memory-model mismatches unusually explicit.

- **C1:** The [multi-threaded TCG design](https://www.qemu.org/docs/master/devel/multi-thread-tcg.html) covers guest memory ordering, atomic operations, translated-block invalidation, and the need to stop other vCPUs for certain changes. Guest atomics wider than the host can require an exclusive fallback.
- **C3:** The same design connects performance to specific structures: per-vCPU execution threads and translation contexts, atomic jump-cache updates, lockless hash-table lookups, and carefully delimited global synchronization. It is a concrete study of removing hot-path locks without abandoning correctness constraints.

### [xen-project/xen](https://github.com/xen-project/xen)

**Language/role:** Primarily C; type-1 hypervisor and supporting tools. **Official GitHub mirror** of Xen's upstream repository.

Xen is a strong choice for studying cooperation across mutually isolated domains, especially the shared-memory protocols underlying split frontend/backend devices.

- **C1:** The [grant-table design notes](https://github.com/xen-project/xen/blob/master/docs/misc/grant-tables.txt) distinguish frame ownership, grant references, active mappings, reference counts, and locking. A crucial semantic detail is that ending a grant does not itself remove a remote domain's existing mapping; revocation and unmapping must be reasoned about separately.
- **C2:** Grant tables provide a reusable cross-domain memory-sharing mechanism rather than a separate ad hoc protocol for every device. The notes explain shared entries, hypervisor-private active entries, and map tracking, with synchronization designed to permit concurrent operations.

The document contains historical design material as well as later locking explanations. Treat it as a guide to mechanisms and tradeoffs, and check the relevant implementation before assuming every historical sketch describes the current ABI.

### [VirtualBox/virtualbox](https://github.com/VirtualBox/virtualbox)

**Language/role:** C and C++; Oracle's VirtualBox hosted virtualization implementation.

The Pluggable Device Manager is a useful entry into a large desktop VMM because it exposes lifecycle and synchronization contracts that device authors must obey across execution contexts.

- **C1:** The [PDM device interface](https://github.com/VirtualBox/virtualbox/blob/main/include/VBox/vmm/pdmdev.h) specifies different locking obligations for construction, destruction, relocation, reset, and power transitions. Destruction cannot simply inherit the normal device lock because it may destroy that lock.
- **C2:** The same interface provides a common device lifecycle and configuration contract spanning many emulated devices and ring-3/ring-0 contexts.
- **C3:** The [PDM critical-section implementation](https://github.com/VirtualBox/virtualbox/blob/main/src/VBox/VMM/VMMAll/PDMAllCritSect.cpp) makes contention handling concrete: ownership and nesting checks, bounded spinning, statistics, and transitions back to ring 3 when completing queued unlock work is necessary to avoid deadlock.

### [freebsd/freebsd-src](https://github.com/freebsd/freebsd-src)

**Language/role:** C; the **bhyve** userspace VMM and associated FreeBSD kernel virtualization subsystem. **Official publish-only GitHub mirror**; the whole operating system is not the unit being recommended.

Study bhyve for a relatively direct presentation of vCPU execution and userspace handling of hardware virtualization exits.

- **C1:** The [main runtime, `bhyverun.c`](https://github.com/freebsd/freebsd-src/blob/main/usr.sbin/bhyve/bhyverun.c), contains the per-vCPU execution loop, exit-handler validation, CPU activation and suspension, and coordinated CPU teardown. Its atomic CPU membership state and condition-variable shutdown protocol expose real multi-vCPU lifecycle obligations.
- **C2:** The runtime separates VM execution from exit-specific handlers and configurable CPU topology. The [bhyve manual](https://github.com/freebsd/freebsd-src/blob/main/usr.sbin/bhyve/bhyve.8) shows the reusable machine interface around this core: virtual-device configuration, topology, boot firmware, and host-resource access, including architecture-dependent requirements.

This entry covers FreeBSD bhyve. Propolis below is a separate Rust userspace implementation for the illumos branch of the bhyve kernel interface.

### [openbsd/src](https://github.com/openbsd/src)

**Language/role:** C; OpenBSD's **vmm kernel driver and vmd userspace monitor**. **Official read-only GitHub mirror** of OpenBSD's CVS source.

This subsystem offers a contrasting decomposition in which process boundaries and progressively reduced privileges are part of the VMM's structure.

- **C1:** The [VM process implementation](https://github.com/openbsd/src/blob/master/usr.sbin/vmd/vm.c) stages resource setup and guest initialization before tightening `unveil`/`pledge` restrictions. It also maintains per-vCPU startup, wakeup, and synchronization state. This makes both adversarial-input handling and concurrent guest lifecycle management visible in one place.
- **C2:** The [`vmm(4)` interface](https://man.openbsd.org/vmm.4) separates kernel VM execution from userspace management through VM file descriptors and operations for CPU state, interrupts, and memory sharing. Descriptor lifetime controls VM lifetime, giving the surrounding process architecture a concrete resource-ownership contract.

The relevant study target is this driver/monitor combination, not unrelated parts of the operating-system monorepo.

## Cloud, sandboxed, and specialized userspace VMMs

### [firecracker-microvm/firecracker](https://github.com/firecracker-microvm/firecracker)

**Language/role:** Rust; KVM-based microVM monitor for isolated workloads.

Firecracker's limited machine model makes the relationship between the control API, vCPU execution, virtual devices, and host isolation comparatively easy to trace.

- **C1:** The [design document](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md) treats guest software as untrusted and describes the VMM's use of seccomp and the jailer's host isolation. It also specifies that pausing a microVM stops both vCPU execution and the device event loop, an important consistency condition for management operations.
- **C3:** The design separates the API thread from the VMM event loop and per-vCPU threads so control-plane work does not occupy the main execution path. Device rate limiting uses separate token buckets for bandwidth and operation count, making resource control a first-class part of the architecture.

The value is in studying the consequences of a deliberately constrained device and execution model; the isolation story includes host configuration and the jailer, not Rust alone.

### [cloud-hypervisor/cloud-hypervisor](https://github.com/cloud-hypervisor/cloud-hypervisor)

**Language/role:** Rust; a VMM for modern cloud workloads, with KVM and Microsoft Hypervisor support.

Its device-assignment and migration documentation provides an unusually concrete route into the boundary between userspace VMM state, kernel VFIO state, and physical device behavior.

- **C1:** The [VFIO documentation](https://github.com/cloud-hypervisor/cloud-hypervisor/blob/main/docs/vfio.md) describes migration states, restoration of PCI command state, rearming MSI eventfds, and recovery when a device rejects a transition. Restoring serialized device data is insufficient when kernel-managed interrupt state also needs reconstruction.
- **C3:** Direct device assignment reduces software intervention in I/O, but migration introduces additional obligations such as DMA dirty tracking for pre-copy. The document explains those constraints and exclusions, including restrictions around virtual IOMMUs, rather than presenting passthrough as a universally interchangeable optimization.

This is a strong comparison with simpler emulated-device VMMs: the performance path itself creates substantial lifecycle and recovery complexity.

### [google/crosvm](https://github.com/google/crosvm)

**Language/role:** Rust; a sandbox-oriented VMM used in the ChromiumOS ecosystem. **Official GitHub mirror** of the project's googlesource repository.

The [architecture document](https://github.com/google/crosvm/blob/main/ARCHITECTURE.md) connects crate boundaries to security boundaries and host-platform differences, rather than merely listing modules.

- **C1:** Devices can run in separate sandboxed processes behind `ProxyDevice`. Device control channels have deliberately different privileges. Guest-memory access uses volatile abstractions because a guest can change memory concurrently, invalidating ordinary Rust-reference assumptions.
- **C2:** `BusDevice`, guest-memory abstractions, hypervisor interfaces, and platform event-waiting facilities provide reusable boundaries across devices and hosts. The document also explains how device address dispatch and asynchronous I/O fit into that composition.

It is especially useful for engineers examining where a memory-safe language needs explicit escape hatches and operating-system isolation to handle a concurrently executing, potentially hostile machine.

### [microsoft/openvmm](https://github.com/microsoft/openvmm)

**Language/role:** Primarily Rust; the OpenVMM VMM and OpenHCL paravisor in one repository, counted once.

OpenVMM is a useful study in reusing virtualization components across different process and execution environments. Its scope includes an actual VMM and paravisor; it should not be confused with publication of the proprietary Hyper-V implementation.

- **C1:** The [Mesh internals documentation](https://openvmm.dev/guide/reference/architecture/openvmm/mesh/internals.html) explains how channel endpoints move between processes without losing messages. Forwarding states, buffering, and peer-change handshakes preserve communication while endpoints change location.
- **C2:** Typed senders and receivers initially communicate through local queues, then can be promoted to remote ports using the same interface. Separate channel, node, serialization, worker, and process layers support different VMM component arrangements.
- **C3:** That promotion model preserves a simple in-process path without serialization while supporting out-of-process placement when needed. The architecture makes the cost boundary explicit instead of imposing distributed-message overhead on all local communication.

### [libkrun/libkrun](https://github.com/libkrun/libkrun)

**Language/role:** Rust with a C-facing API; a VMM packaged as an embeddable dynamic library, using KVM and macOS's Hypervisor framework.

The project has Firecracker/Chromium-derived implementation lineage, but its library embedding model and distinct platform integration make it a substantive separate codebase rather than a redundant fork entry.

- **C1:** The [VMM implementation](https://github.com/libkrun/libkrun/blob/main/src/libkrun/src/vmm/mod.rs) coordinates paused vCPU startup and subsequent execution. It uses explicit control messages for pause/resume handling and platform-specific synchronization; the Linux path waits for vCPU responses with a timeout.
- **C2:** The embedding interface lets container runtimes and other host programs create a VM without adopting a standalone monitor's control protocol. The internal VMM still owns guest memory, vCPU handles, and device management rather than merely wrapping an external executable.

The repository warns that its main 2.0 development line breaks API/ABI compatibility and directs stable consumers to stable branches. It also explains that host-side confinement remains the embedding application's responsibility. These are meaningful boundaries for studying the abstraction.

### [oxidecomputer/propolis](https://github.com/oxidecomputer/propolis)

**Language/role:** Rust; userspace VMM and device emulation for **illumos bhyve**, with server and standalone programs built around a common library.

Propolis is particularly valuable for device lifecycle and migration contracts. Its interface is closely coupled to recent illumos kernel functionality; the repository identifies AMD as its principal CI and migration platform.

- **C1:** The [implemented lifecycle trait](https://github.com/oxidecomputer/propolis/blob/master/lib/propolis/src/lifecycle.rs) specifies that vCPUs are paused before devices, devices must stop producing work while accepting and holding incoming work, and device resumption precedes vCPU resumption. Reset has its own ordering constraints. These are concrete asynchronous quiescence invariants.
- **C2:** The [migration interfaces](https://github.com/oxidecomputer/propolis/blob/master/lib/propolis/src/migrate.rs) distinguish non-migratable, empty-state, single-payload, and multi-payload devices. Versioned payloads let compound devices separate PCI, queue, and device-specific state while reporting mismatches and import/export failures explicitly.

These links target implemented contracts; older aspirational lifecycle prose elsewhere in the repository should not automatically be read as current behavior.

### [hermit-os/uhyve](https://github.com/hermit-os/uhyve)

**Language/role:** Rust; a specialized VMM for Hermit unikernels, with KVM and macOS Hypervisor-framework backends.

This is a useful smaller-scale contrast to general-purpose cloud monitors: a narrower guest contract allows loading, boot protocol, network setup, and CPU coordination to be followed together.

- **C1:** The [VM implementation](https://github.com/hermit-os/uhyve/blob/main/src/vm.rs) handles guest-image loading, resource validation, shared peripheral access, and version-dependent guest boot interfaces. Legacy layouts and newer network-interface requirements show that a specialized VMM still needs explicit compatibility checks.
- **C2:** `VirtualizationBackend` associates a vCPU implementation, network backend, and memory layout with the common VM machinery. That boundary supports reuse across host virtualization APIs without duplicating the complete loader and machine setup.

The repository reports weaker testing and feature parity on macOS. The inspected source also contains an unresolved soundness note around unsafe thread-sharing implementations. Those limits matter: this is a study candidate, not an assertion that every unsafe boundary has been settled.

## Embedded, static-partitioning, and multi-architecture hypervisors

### [projectacrn/acrn-hypervisor](https://github.com/projectacrn/acrn-hypervisor)

**Language/role:** Primarily C; an Intel-oriented embedded hypervisor with service-VM and device-model components.

ACRN exposes several deployment arrangements in one architecture, including pre-launched partitions and service-VM-managed guests. It is a useful bridge between cloud-style device emulation and systems with real-time workloads.

- **C1:** The [high-level design](https://projectacrn.github.io/latest/developer-guides/hld/hld-overview.html) traces an emulated I/O request from VM exit through shared request state, the service VM's kernel module or userspace device model, and eventual guest register/instruction-pointer update. Correct ownership and completion across those stages are essential to executing the trapped instruction exactly once.
- **C3:** The design connects reduced interference to dedicated resources and restricted interactions, and describes mediated passthrough in which a device's data path is direct while its control path remains emulated. These choices make the performance/isolation tradeoff inspectable.

The documentation's `latest` branch includes development material. Its stated real-time design goals should not be mistaken for a measured latency guarantee for arbitrary hardware and configurations.

### [siemens/jailhouse](https://github.com/siemens/jailhouse)

**Language/role:** C; a Linux-activated partitioning hypervisor that allocates hardware resources to isolated cells without CPU overcommit or a normal vCPU scheduler.

Jailhouse is a strong example of changing the problem to reduce runtime mechanisms: Linux performs initial setup, then the hypervisor enforces a comparatively static partition.

- **C1:** The [memory-layout document](https://github.com/siemens/jailhouse/blob/master/Documentation/memory-layout.txt) explains restricted mappings and separation of private CPU data from globally visible state. A cell's entire memory is not permanently mapped into the hypervisor; temporary mappings and visibility rules become explicit correctness obligations.
- **C3:** Static CPU assignment eliminates ordinary multiplexing, while the per-CPU layout gives local code a fixed virtual address for CPU-local state. The design connects a small runtime interface and predictable resource ownership to reduced interference and simpler access paths.

The public repository's last recorded push at inspection was in May 2024. It was not archived, but this report makes no claim of current release support or responsiveness. The snapshot remains substantial architectural material.

### [bao-project/bao-hypervisor](https://github.com/bao-project/bao-hypervisor)

**Language/role:** C; a static-partitioning hypervisor for embedded systems, including Arm and RISC-V configurations.

Bao is useful for studying how much hypervisor behavior can be established through resource assignment before guests execute.

- **C1:** The [configuration manual](https://bao-project.readthedocs.io/en/latest/bao_hyp/user_manual/config.html) specifies guest memory regions, CPU assignments, interrupts, image placement, and deliberately shared memory. It documents alignment and hardware-capacity constraints, making configuration validity part of the isolation argument rather than treating configuration as unstructured input.
- **C3:** The static CPU model avoids a normal CPU scheduler. The same manual exposes cache-color assignment, large-page-friendly alignment, and image placement without copying. These are concrete controls for memory cost and interference, with architectural consequences visible in the configuration model.

Bao's partitioning model is intentionally narrower than a general-purpose overcommitting VMM. The sources support studying its mechanisms; they do not establish universal timing bounds or certification for a user's target platform.

### [xvisor/xvisor](https://github.com/xvisor/xvisor)

**Language/role:** C; a portable, monolithic type-1 hypervisor with multiple architecture and device implementations.

Xvisor provides an instructive contrast to static partitioners because it brings scheduling and host-side service execution into the hypervisor itself.

- **C1:** The [design document](https://github.com/xvisor/xvisor/blob/master/docs/DesignDoc) defines vCPU lifecycle states and synchronization around scheduler-visible fields. Handling reset, runnable, executing, paused, and halted states correctly is fundamental to both guest control and scheduler concurrency.
- **C2:** Normal guest vCPUs and “orphan” vCPUs for host work share scheduling machinery. Per-CPU ready queues, replaceable scheduling algorithms, background load balancing, and device-tree-based configuration separate policy, execution, and machine description.

This is a useful codebase for following how a common scheduler and device-emulation framework serve different guests and host services. Architecture names in the repository should not be interpreted as evidence that every port has identical feature completeness or testing depth.

### [syswonder/hvisor](https://github.com/syswonder/hvisor)

**Language/role:** Rust; a separation-kernel-style hypervisor with static zones and architecture-specific backends. The inspected default development branch is `dev`.

hvisor adds a smaller Rust implementation to the embedded group. Its memory-virtualization design is a concrete starting point for studying the relationship between ownership types and hardware translation tables.

- **C1:** The [memory virtualization chapter](https://hvisor.syswonder.org/chap04/MemVirtualization.html) distinguishes owned and borrowed frames, uses RAII for frame reclamation, and describes alignment and overlap validation when installing guest regions. These are essential invariants when translating a zone's guest-physical addresses into host memory.
- **C2:** `MemoryRegion`, `MemorySet`, generic page-table interfaces, and architecture-specific page-table entries separate region management from translation-format details. The same model accommodates ordinary mappings and suitably aligned large-page mappings.

The project's discussion of formal verification describes work in progress, not a completed proof of the entire hypervisor. Architecture support also varies. The study value lies in the inspected abstractions and their obligations, without inferring production assurance from language choice or verification aspirations.

## Capability microhypervisors and reusable VMM foundations

### [udosteinberg/NOVA](https://github.com/udosteinberg/NOVA)

**Language/role:** C++; capability-based microhypervisor supporting virtualized and native execution components. The inspected branch is `release`.

NOVA is a strong choice for studying how access rights, object lifetime, and low-level concurrency can be organized into a compact virtualization kernel.

- **C1:** The [object-space implementation](https://github.com/udosteinberg/NOVA/blob/release/inc/space_obj.hpp) explicitly derives acquire/release ordering for publishing capability tables: another CPU must not observe a table pointer before its initialized entries become visible. This turns a subtle memory-ordering requirement into a local, documented invariant.
- **C2:** The [capability abstraction](https://github.com/udosteinberg/NOVA/blob/release/inc/capability.hpp) combines object identity with permissions and validates object type, subtype, and required rights. Separate permission families cover protection domains, execution and scheduling contexts, portals, semaphores, and device contexts, allowing a common authorization model to govern different resources.

Some features are identified by the project as experimental or incomplete. This entry refers to the current repository and its inspected interfaces, not every historical NOVA distribution.

### [cyberus-technology/hedron](https://github.com/cyberus-technology/hedron)

**Language/role:** C++; Intel x86 microhypervisor, published as a **mirror of Cyberus's internal repository**.

Hedron is retained separately from NOVA because the project documents independent evolution since their last common version in 2015, with substantial interface and implementation changes.

- **C1:** The [implementation notes](https://github.com/cyberus-technology/hedron/blob/master/docs/implementation.md) explain serialized early boot/resume, CPU synchronization, and reference counting combined with RCU. They distinguish immediate pre-free processing from actual reclamation after all CPUs pass a quiescent state.
- **C3:** The reclamation scheme is designed to avoid atomic reference-count operations on ordinary access paths while keeping object destruction safe. Its cost and correctness argument can be studied together in the same document.
- **C4:** The [versioned changelog](https://github.com/cyberus-technology/hedron/blob/master/CHANGELOG.md) records explicit API changes, including removal of preemptive scheduling and IOMMU-management interfaces. This documents deliberate complexity reduction and changing compatibility boundaries, rather than merely accumulated commits.

The public snapshot's last push was October 2023. The notes also acknowledge transitional error-handling weaknesses. Do not infer current internal development or supported deployment status from this mirror.

### [Bareflank/hypervisor](https://github.com/Bareflank/hypervisor)

**Language/role:** Primarily C++; a hypervisor microkernel and extension SDK, including support for Rust extensions. It is a substantial foundation for constructing hypervisors, not a complete general-purpose VM product by itself.

Its unusually explicit extension ABI makes it useful for studying the boundary between a small privileged core and replaceable virtualization policy.

- **C1:** The [microkernel syscall specification](https://github.com/Bareflank/hypervisor/blob/master/docs/Microkernel%20Syscall%20Specification.md) defines handle validation, resource ownership, legal call contexts, and status results. Virtual-state migration requires an inactive state, and translation invalidation has processor-local constraints—details that cannot be hidden by a convenient wrapper.
- **C2:** Separate VM, virtual-processor, and virtual-state objects give extensions a structured resource model. A versioned syscall surface lets separately implemented extensions interact with the microkernel while making the hardware execution boundary explicit.

The public repository's last recorded push was August 2024 and it was not archived. It belongs here as a substantive SDK snapshot; this report does not imply an actively supported standalone VMM release.

### [au-ts/libvmm](https://github.com/au-ts/libvmm)

**Language/role:** C; reusable VMM components for seL4 Microkit systems.

This library is valuable for studying the userspace composition that must still be built around a microkernel's virtualization primitives. It supplies actual VM, interrupt, fault, and device handling rather than only deployment manifests.

- **C1:** The [VMM manual](https://github.com/au-ts/libvmm/blob/main/docs/MANUAL.md) explains guest RAM mapping into both the VM and VMM, the distinction between host virtual and guest physical addresses, and the need to make guest machine descriptions agree with those mappings. Its interrupt routing and passthrough examples require explicit, exclusive resource ownership.
- **C2:** Common VMM mechanisms are composed with board-specific memory regions, interrupt routes, and virtual or passed-through devices. The Arm and x86 paths expose different interrupt-controller and execution requirements while sharing the library's purpose and surrounding Microkit composition model.

The project explicitly warns that it is not ready for production and changes frequently; platform and multicore capabilities differ. seL4's verification results should not be automatically attributed to this separate VMM library.

## Coverage, search process, and limitations

Discovery used more than six distinct search formulations, including combinations of:

- General-purpose hypervisors and full-system VMMs: QEMU, Xen, KVM, and official VirtualBox sources.
- Rust/KVM microVMs, sandboxed devices, cloud migration, and VFIO assignment.
- BSD VMMs, illumos bhyve userspace, and OpenBSD's kernel/userspace split.
- Embedded Arm and RISC-V static partitioning, mixed-criticality designs, and resource isolation.
- Multi-architecture hypervisors, including searches for less commonly covered architecture families.
- Capability microhypervisors, NOVA descendants, and hypervisor extension SDKs.
- seL4 VMM composition and specialized unikernel monitors.
- Smaller and historical implementations, including Go VMM searches, to challenge a list dominated by familiar C and Rust projects.

Later distinct queries mostly returned already-covered projects, management layers, minimal demonstrations, or candidates without equally strong accessible primary implementation evidence. The final selection spans C, C++, and Rust; Linux, BSD, illumos, ChromiumOS, Microsoft, embedded, and microkernel communities; and hardware-assisted, translated, static-partitioned, and library-based designs. It is not an exhaustive catalogue, and the language distribution reflects the verified candidates rather than an imposed quota.

Repository pages or GitHub API records were checked for exact owner/name, canonical URL, default branch, and archive status. Each retained repository also received a separate primary-source implementation or design inspection; a raw copy of its README was not treated as independent evidence. None of the selected repositories was marked archived at inspection. Mirror status and conspicuously older public snapshots are identified above. A recent repository push is not evidence of support quality, and no C4 judgment rests on that signal alone.

Management interfaces and orchestration projects such as libvirt, KubeVirt, and VM launch frontends were excluded because the category here is the hypervisor/VMM implementation. Minimal teaching or introspection demonstrations were not used to pad the list. Rust-vmm's community index was useful for discovery but was not counted as an implementation repository. Proprietary hypervisors without a substantive public GitHub implementation were outside scope. Candidates lacking complete primary-source verification were omitted rather than supplied with guessed repository or source paths.

Shared lineage was checked when selecting related projects: the three operating-system monorepos count once each; OpenVMM and OpenHCL count together; Hedron's documented separate evolution justifies its distinction from NOVA; and libkrun's embedding model and host integration justify its distinction from Firecracker. Propolis is an independently structured Rust userspace VMM for illumos bhyve, rather than a second listing of FreeBSD's userspace implementation.

All research was read-only. No candidate code was executed, built, benchmarked, or security-audited. Moving branch and `latest` documentation links may change after the research date. Criteria assessments identify concrete engineering material worth examining; performance and correctness claims are limited to the documented mechanisms, not independently verified guarantees.
