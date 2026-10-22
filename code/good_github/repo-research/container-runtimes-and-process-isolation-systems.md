# Container runtimes and process isolation systems

Research date: **2026-10-09**.

This report selects **25 GitHub repositories** implementing container execution, container lifecycle management, or operating-system and VM-backed process isolation. It spans Linux OCI runtimes, system containers, HPC environments, userspace kernels, microVM integration, application sandboxes, FreeBSD jails, and Windows isolation. Higher-level projects are included when their lifecycle and isolation machinery is substantial; a CLI that merely invokes another runtime is insufficient. Monorepos are counted once, with the relevant subsystem identified.

The criteria below describe reasons to study a repository, not a security certification or a claim that every component is exemplary. Statements about engineering value are grounded interpretations of the linked implementation and design evidence. Different projects intentionally provide different isolation boundaries.

- **C1 — Difficult correctness:** invariants, concurrency, adversarial inputs, privilege transitions, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components supporting multiple workloads and integrations.
- **C3 — Performance with structure:** explicit resource or latency constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** years of development supported by compatibility practices, testing, release history, or deliberate complexity management.

## OCI execution and container lifecycle services

### 1. [opencontainers/runc](https://github.com/opencontainers/runc)

**Language/role:** Go with low-level C support; Linux OCI runtime and libcontainer implementation.

Study how a container configuration becomes a process with carefully ordered namespace, filesystem, capability, and resource setup. **C1:** the libcontainer specification describes parent/child synchronization that places the initial process in its cgroups before initialization can create escaping children. It also explains root-filesystem transitions and handling standard descriptors outside the new root. **C2:** the separation between container configuration, resource controls, and lifecycle operations makes this machinery usable by higher-level container systems. Start with the [libcontainer specification](https://github.com/opencontainers/runc/blob/main/libcontainer/SPEC.md); its older profile details should be read as design context, not as a current kernel-support matrix.

**C4:** the [changelog](https://github.com/opencontainers/runc/blob/main/CHANGELOG.md) documents evolution from 2021 through 2026, including staged deprecations, backports, runtime-spec conformance corrections, and fixes for configurations whose requested read-only behavior could not be enforced.

### 2. [containers/crun](https://github.com/containers/crun)

**Language/role:** C; OCI runtime with an embeddable library interface.

An informative counterpart to runc for studying the same operating-system obligations with a different language and embedding model. **C1:** the [container implementation](https://github.com/containers/crun/blob/main/src/libcrun/container.c) coordinates execution, hooks, notification channels, and process exit; its pidfd handling explicitly accommodates a process disappearing during lookup. **C2:** the [libcrun interface](https://github.com/containers/crun/blob/main/src/libcrun/container.h) exposes container loading, execution contexts, lifecycle operations, feature reporting, and checkpoint/restore configuration. Its ownership and concurrency comments are useful: configuration JSON is cached on first access, so that access must not race on the same handle.

The repository motivates the C implementation through startup and memory costs, but its example benchmark is not used here as a general performance ranking.

### 3. [youki-dev/youki](https://github.com/youki-dev/youki)

**Language/role:** Rust; OCI runtime with a reusable libcontainer crate.

Study explicit protocol modeling around operations that remain delicate even in a memory-safe language. **C1:** the [main-process implementation](https://github.com/youki-dev/youki/blob/main/crates/libcontainer/src/process/container_main_process.rs) models one-shot initialization requests and their phases: hook and network setup may arrive in either order, but must precede seccomp installation and readiness. It also reaps the intermediate process and handles unprivileged UID/GID-map setup. **C2:** the [crate interface](https://github.com/youki-dev/youki/blob/main/crates/libcontainer/src/lib.rs) separates containers, processes, root filesystems, syscalls, security controls, and workloads. It re-exports the OCI specification crate used by its public API, avoiding a subtle dependency-version mismatch for consumers.

These are concrete opportunities to study typed state transitions and library boundaries, beyond the language choice alone.

### 4. [containerd/containerd](https://github.com/containerd/containerd)

**Language/role:** Go; container lifecycle daemon and runtime integration framework for Linux and Windows.

Study the boundary between durable container metadata, filesystem preparation, and running tasks. **C1:** the [runtime-v2 design](https://github.com/containerd/containerd/blob/main/docs/runtime-v2.md) specifies asynchronous event ordering so that an immediately exiting process cannot publish an exit before its start event. **C2:** the same document describes a small shim API, replaceable runtime engines, and one-to-one or one-to-many relationships between shims and containers; image preparation and snapshotters remain separate concerns.

**C4:** the [release and compatibility policy](https://github.com/containerd/containerd/blob/main/RELEASES.md) records release lines across multiple years, distinguishes stable APIs from unsupported surfaces, and describes migration warnings and API-symbol checks. It is a useful example of managing compatibility across a large integration ecosystem.

### 5. [cri-o/cri-o](https://github.com/cri-o/cri-o)

**Language/role:** Go; Kubernetes CRI implementation backed by OCI runtimes.

Study how a node service translates orchestration requests into concrete runtime operations while preserving retry behavior. **C1:** [container creation](https://github.com/cri-o/cri-o/blob/main/server/container_create.go) distinguishes context timeouts from other failures, conditionally retains resources, and recognizes duplicate creation requests. The same implementation confines path resolution and filters annotations before internal values can be overwritten. **C2:** its CRI boundary combines image management, pod sandboxes, process lifecycle, and resource isolation while allowing OCI execution implementations underneath. The [runtime configuration manual](https://github.com/cri-o/cri-o/blob/main/docs/crio.8.md) provides the operational entry point.

The interesting abstraction is the translation and recovery layer between kubelet and execution engines, rather than another implementation of Linux namespaces.

## System containers and native jail machinery

### 6. [lxc/lxc](https://github.com/lxc/lxc)

**Language/role:** C; low-level Linux system-container runtime and library.

Study containers intended to behave like complete Linux systems, including their init process, console, reboot, and attachment semantics. **C1:** [startup and supervision](https://github.com/lxc/lxc/blob/main/src/lxc/start.c) contain explicit ordering constraints around signal setup, parent-death notification, user and cgroup namespaces, security labels, and privilege dropping. The code also handles namespace references and state clients during shutdown and reboot. **C2:** the [public container interface](https://github.com/lxc/lxc/blob/main/src/lxc/lxccontainer.h) exposes lifecycle, configuration, console, attachment, snapshots, migration, and resource controls through a common container object.

The contrast with a command-oriented OCI runtime is particularly useful: long-lived system-container behavior is part of the core abstraction.

### 7. [lxc/incus](https://github.com/lxc/incus)

**Language/role:** Primarily Go; system-container and VM manager built above lower-level execution components.

Study the management layer required to turn isolation primitives into remotely operated instances. **C1:** the [security design](https://github.com/lxc/incus/blob/main/doc/explanation/security.md) covers unprivileged containers, non-overlapping UID/GID maps, daemon-access authority, and bridge filtering against address spoofing. These details expose interactions between instance isolation and host administration. **C2:** the [REST API](https://github.com/lxc/incus/blob/main/doc/rest-api.md) defines synchronous results, asynchronous operations, stable numeric status codes, and discoverable API extensions for compatible feature growth.

Incus began as a community fork of LXD, as its repository explains. It is retained for its separate management implementation and evolving API, and LXD is not separately counted here. LXC and Incus represent different architectural layers.

### 8. [systemd/systemd](https://github.com/systemd/systemd)

**Language/role:** Primarily C; this entry concerns **systemd-nspawn and its container-manager interfaces**, not the entire service-manager monorepo.

Study the integration between a container's PID 1 and the host's service and resource managers. **C1:** the [nspawn manual source](https://github.com/systemd/systemd/blob/main/man/systemd-nspawn.xml) explains user-namespace requirements for untrusted workloads and how the provenance of an `.nspawn` settings file affects whether privilege-expanding settings are accepted. **C2:** the [Container Interface](https://systemd.io/CONTAINER_INTERFACE/) specifies mount visibility, device handling, cgroup delegation, console behavior, and execution-environment conventions that other container managers can implement.

This is a useful study in integration contracts: a seemingly harmless choice such as exposing only part of a cgroup hierarchy can violate assumptions made by the guest init system.

### 9. [freebsd/freebsd-src](https://github.com/freebsd/freebsd-src)

**Language/role:** C; **FreeBSD jail kernel subsystem** within the OS source tree. This GitHub repository is an official publish-only source mirror.

Study isolation inside the kernel rather than solely through a userspace runtime. **C1:** [kern_jail.c](https://github.com/freebsd/freebsd-src/blob/main/sys/kern/kern_jail.c) documents locks protecting prison structures and uses a dedicated teardown task queue to avoid deadlocks during virtual-network destruction. Reference counts, process attachment, and live/dying states make the lifetime problem concrete. **C2:** [jail.h](https://github.com/freebsd/freebsd-src/blob/main/sys/sys/jail.h) defines parameterized creation, update, attachment, hierarchy, and permission interfaces, including distinctions between inherited, new, and disabled facilities.

The relevant reusable abstraction is the jail/prison object and its kernel-wide confinement contract. This entry does not rate the rest of the FreeBSD monorepo.

## HPC-oriented container execution

### 10. [apptainer/apptainer](https://github.com/apptainer/apptainer)

**Language/role:** Go and C; application containers for shared systems and HPC.

Study how container portability is designed around an existing scheduler, user identity, and host hardware. The project explicitly favors integration over isolation by default. **C1:** the [user-namespace and fakeroot guide](https://apptainer.org/docs/admin/main/user_namespace.html) explains privilege mapping, kernel-dependent filesystem support, and fallback from kernel overlayfs to fuse-overlayfs. **C2:** the runtime combines a transportable SIF image model with host-user execution and configurable resource controls; the [security and runtime administration guide](https://apptainer.org/docs/admin/main/security.html) explains how cgroup versions and delegation determine which controls unprivileged callers can apply.

This is especially useful for engineers comparing application-container assumptions with Kubernetes-style pod isolation. Its default host integration should not be mistaken for a complete hostile-workload boundary.

### 11. [NVIDIA/enroot](https://github.com/NVIDIA/enroot)

**Language/role:** Shell and C; unprivileged container execution with filesystem separation and HPC integration.

The repository describes an enhanced unprivileged chroot and deliberately limited isolation. **C1:** [runtime.sh](https://github.com/NVIDIA/enroot/blob/main/src/runtime.sh) ties FUSE helper lifetimes to the container through process-group and orphan-handling behavior, and sequences environment generation, mounts, and hook execution. This is unusually instructive shell-level process-lifecycle engineering. **C2:** the [standard-hook interface](https://github.com/NVIDIA/enroot/blob/main/doc/standard-hooks.md) supports host-user databases, device restrictions, GPUs, and InfiniBand adapters without embedding every site policy in the launcher.

Study the small runtime core and its extension points as an alternative to a general-purpose container daemon. The inclusion is for container execution and composition, not a claim of strong isolation from the host.

## Userspace kernels and VM-backed isolation

### 12. [google/gvisor](https://github.com/google/gvisor)

**Language/role:** Primarily Go; userspace application kernel and the `runsc` OCI runtime.

Study a Linux-compatible execution environment that implements application system calls rather than simply forwarding them. **C1:** the [architecture introduction](https://gvisor.dev/docs/architecture_guide/intro/) explains the Sentry's own process tables, memory management, signals, filesystem behavior, and synchronization, with restricted host access and a separate Gofer for operations requiring additional authority. **C2:** that application-kernel interface, exposed through an OCI runtime, supports existing container workloads without requiring each application to adopt a new sandbox API.

The key learning opportunity is the compatibility boundary: application-visible Linux semantics must be reconstructed under a narrower host interface. The documentation is explicit that unimplemented kernel features remain unavailable; this is a substantive tradeoff, not transparent equivalence with Linux.

### 13. [kata-containers/kata-containers](https://github.com/kata-containers/kata-containers)

**Language/role:** Go and Rust; VM-backed container runtime, guest agent, and supporting VMM components in one monorepo.

Study how pod and container concepts cross a host/guest boundary. **C1:** the [architecture document](https://github.com/kata-containers/kata-containers/blob/main/docs/design/architecture/README.md) separates host state, guest-VM state, and individual container environments. Container setup inside the guest still needs namespaces and cgroups; the VM boundary does not remove those obligations. **C2:** a shimv2 runtime and guest-agent division supports multiple containers per VM and multiple hypervisor implementations. **C3:** the documented shim redesign consolidates runtime state and avoids repeated runtime invocations and excess per-container processes.

The repository's runtime, runtime-rs, agent, and Dragonball components are counted together. This is an especially useful comparison with gVisor's userspace-kernel approach.

### 14. [firecracker-microvm/firecracker](https://github.com/firecracker-microvm/firecracker)

**Language/role:** Rust; microVM monitor and jailer for container and function workloads.

Study a deliberately small machine model and its host-side containment. **C1:** the [design document](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md) treats guest execution as untrusted and explains trust boundaries, device mediation, and the relationship between pausing vCPUs and pausing device processing. **C3:** each microVM has a separate process, an API thread outside the fast path, vCPU threads, and an epoll-driven VMM/device loop. Restricted device emulation and I/O rate limiting address footprint and resource contention through a clear architecture.

Firecracker is a building block rather than an OCI container engine by itself. The repository is included because its explicit purpose and implementation concern isolation of container and function workloads; no numerical startup or density claim is inferred here.

### 15. [firecracker-microvm/firecracker-containerd](https://github.com/firecracker-microvm/firecracker-containerd)

**Language/role:** Go; substantive containerd-to-microVM runtime integration.

Study the lifecycle mismatch between a VM and the containers running inside it. **C1:** the [shim design](https://github.com/firecracker-microvm/firecracker-containerd/blob/main/docs/shim-design.md) evaluates failure containment and resource accounting for one host shim per VM versus global or per-container shims. It also examines VM-to-shim mapping and guest connections. **C2:** the [architecture](https://github.com/firecracker-microvm/firecracker-containerd/blob/main/docs/architecture.md) separates a VM control API, an out-of-process runtime, and an in-guest agent that manages container operations and proxies I/O.

This is retained separately from Firecracker because it implements orchestration and supervision across the VM boundary, not just a thin launch wrapper. The architecture document includes older containerd component references; use it for the decomposition and consult current code for exact dependency versions.

### 16. [libkrun/libkrun](https://github.com/libkrun/libkrun)

**Language/role:** Rust with a C API; embeddable virtualization-based process isolation on Linux and macOS/ARM64.

Study the packaging of a VMM as a library rather than an external VM-management service. **C2:** the [C interface](https://github.com/libkrun/libkrun/blob/main/include/libkrun.h) exposes VMM construction, device objects, shared filesystems, and explicit handle ownership. **C3:** that interface documents a DAX shared-memory window for direct file mapping; the repository also explains transparent socket impersonation, which provides selected networking behavior without a conventional virtual NIC.

Two boundaries matter when reading this code: the project considers guest and VMM part of the same security context, so host restrictions still determine accessible resources; and the checked `main` branch is an evolving **2.0 API/ABI incompatible with 1.x**, as the repository states. The API source is an entry point into a substantial VMM implementation, not the sole basis for inclusion.

### 17. [QuarkContainer/Quark](https://github.com/QuarkContainer/Quark)

**Language/role:** Rust; OCI runtime with a tightly coupled QKernel guest kernel and QVisor monitor.

Study a less widely known alternative to both a conventional Linux guest and gVisor. **C1:** the repository's architectural explanation makes guest/host communication explicit: shared-memory QCall queues, a dedicated handling thread, and different paths for I/O data operations and control operations create important synchronization and trust obligations. **C3:** this co-design targets VM-exit and I/O overhead; the [performance-test document](https://github.com/QuarkContainer/Quark/blob/main/doc/perf_test.md) supplies actual workload commands and identifies what its startup and memory measurements include.

Treat this as a specialized implementation to investigate. The checked README pins an older Rust nightly and describes preliminary ARM support; the supplied comparative results are historical project experiments, not independently reproduced or current rankings.

## Linux process and library sandboxes

### 18. [containers/bubblewrap](https://github.com/containers/bubblewrap)

**Language/role:** C; low-level unprivileged sandbox-construction tool used by larger application frameworks.

Study a small mechanism-oriented component whose caller chooses policy. **C1:** [bubblewrap.c](https://github.com/containers/bubblewrap/blob/main/bubblewrap.c) handles PID-namespace init duties, zombie reaping, and an exit-status race between the application and namespace init process. It also discusses the race between resolving a descriptor-backed mount target and performing the mount. **C2:** namespace, filesystem, descriptor, capability, and seccomp options can be composed by different enclosing frameworks.

The README explicitly distinguishes constructing a sandbox from supplying a complete security policy: protection depends on the arguments chosen by the caller. That boundary is part of the engineering lesson, particularly for applications embedding a command-line sandbox mechanism.

### 19. [google/nsjail](https://github.com/google/nsjail)

**Language/role:** C++; configurable Linux process isolation and supervision.

Study a reusable sandbox engine that can run once, supervise a network service, or repeatedly execute a workload. **C1:** [contain.cc](https://github.com/google/nsjail/blob/master/contain.cc) orders namespace initialization and privilege dropping, restores the parent-death signal after identity changes, and checks whether the parent died before that signal could be installed. Descriptor inheritance is handled explicitly. **C2:** the same containment machinery is parameterized by Protobuf configuration and combined with cgroups, resource limits, network setup, and Kafel seccomp policies for several execution modes.

The useful distinction from bubblewrap is integrated supervision and resource configuration, rather than only construction of the process environment.

### 20. [google/minijail](https://github.com/google/minijail)

**Language/role:** Primarily C; sandbox launcher and self-confinement library used in ChromeOS and Android. **Official read-only GitHub mirror**; the [project homepage](https://google.github.io/minijail/) identifies Chromium Googlesource as upstream.

Study privilege reduction around executable startup and in-process sandbox entry. **C1:** [libminijail.c](https://github.com/google/minijail/blob/main/libminijail.c) separates parent-side and post-exec restrictions, constrains capability-set combinations, and handles interactions between seccomp logging and thread synchronization. **C2:** both a launcher and an embeddable library share these confinement mechanisms, allowing services to be confined externally or to sandbox themselves.

The current README's threat model is narrower than arbitrary malicious-code execution: it targets known system binaries that might be compromised, and explicitly excludes attacker-controlled binaries or shared libraries. That qualification is central to category fit and comparison.

### 21. [ioi/isolate](https://github.com/ioi/isolate)

**Language/role:** C; sandbox for untrusted executables, especially programming-contest evaluation.

Study the interaction between containment and meaningful resource measurements. **C1:** the [manual](https://github.com/ioi/isolate/blob/master/isolate.1.txt) distinguishes CPU time from wall time, per-process address-space limits from cgroup memory limits, and single-process execution from accounting for an entire process group. It also defines mutual exclusion for operations on the same sandbox. **C2:** separate initialization, execution, cleanup, and machine-readable metadata operations form a reusable interface for grading systems and other execution services.

Its reproducibility discussion covers scheduling, CPU-frequency variation, and other environmental effects that make apparently simple execution limits difficult to interpret. The repository links its original design papers, but the retained evidence here is the current operational contract.

### 22. [netblue30/firejail](https://github.com/netblue30/firejail)

**Language/role:** C; application sandbox using Linux namespaces, seccomp, capabilities, and reusable application profiles.

Study application-oriented confinement with privileged setup and a broad compatibility surface. **C1:** [sandbox.c](https://github.com/netblue30/firejail/blob/master/src/firejail/sandbox.c) sequences filter construction, filesystem setup, namespace operations, capability changes, and final privilege dropping. The supervision path also handles timeouts and processes that ignore graceful termination. **C2:** its profile-driven model applies a common isolation engine to graphical applications, servers, and login sessions, while namespace and filtering mechanisms remain reusable beneath those application choices.

The repository identifies the launcher as an SUID program. That makes the transition from privileged setup to restricted execution an essential part of what to study, and distinguishes its deployment model from wholly unprivileged sandbox launchers.

### 23. [google/sandboxed-api](https://github.com/google/sandboxed-api)

**Language/role:** C++; **Sandbox2 process-isolation engine and Sandboxed API library isolation**, counted once.

Study how to confine a library behind a process boundary while making the resulting component reusable. **C1:** [PolicyBuilder](https://github.com/google/sandboxed-api/blob/main/sandboxed_api/sandbox2/policybuilder.h) documents rule-order semantics that can change the resulting policy, bounds generated BPF policy length, and makes namespace-related security assumptions explicit. **C2:** [Executor](https://github.com/google/sandboxed-api/blob/main/sandboxed_api/sandbox2/executor.h) separates process creation, descriptor ownership, IPC, resource limits, and optional fork-server use. Above this engine, SAPI supplies reusable sandboxed C/C++ library interfaces and per-library policies.

Although interface generation is part of SAPI, this is not a generated-wrapper-only project: the same repository contains the substantive Sandbox2 implementation and its execution and policy abstractions.

## Windows container and application isolation

### 24. [microsoft/hcsshim](https://github.com/microsoft/hcsshim)

**Language/role:** Go; Host Compute Service integration, containerd shims, and guest-compute-service components.

Study Windows container supervision and the boundary between host APIs, utility VMs, and container tasks. **C1:** [internal/hcs/system.go](https://github.com/microsoft/hcsshim/blob/main/internal/hcs/system.go) requires exactly one background exit waiter per compute-system handle while supporting multiple public waiters. Cleanup also explicitly avoids holding the callback-map lock while unregistering callbacks, whose own synchronization could otherwise conflict. **C2:** the repository provides reusable HCS/HNS interfaces and runtime integration spanning process-isolated Windows containers and VM-backed execution.

The README also describes a transition toward separate sandbox and task services, with parity testing against the earlier pipeline. Some V2 platform implementations are marked forthcoming, so this entry does not imply every described V2 path is complete.

### 25. [sandboxie-plus/Sandboxie](https://github.com/sandboxie-plus/Sandboxie)

**Language/role:** C and C++; Windows application isolation with driver, service, injected runtime, and user interfaces.

Study the coordination needed to isolate ordinary desktop applications and their filesystem/registry effects. **C1:** the [driver's process implementation](https://github.com/sandboxie-plus/Sandboxie/blob/master/Sandboxie/core/drv/process.c) explains a subtle process-creation race: one process may create a process object while another creates its first thread, so parent state must be retained under the appropriate lock. **C4:** the [changelog](https://github.com/sandboxie-plus/Sandboxie/blob/master/CHANGELOG.md) records separate evolution from 2020 through 2026, including Windows, browser, Electron, ARM64, and application-compatibility fixes.

This is explicitly a community fork after the original source release, not a claim of official continuation of the former proprietary product. Its substantial later evolution justifies inclusion; Plus and Classic share core components and are counted together.

## Coverage, search process, and limitations

Discovery used **13 distinct live search queries**, followed by direct GitHub repository/API checks and reads of primary documentation or source files. Search angles included OCI runtime implementations; gVisor/Kata/Firecracker architecture; namespace/seccomp sandboxes; HPC runtimes and host integration; Windows HCS and application sandboxing; FreeBSD jails; Rust and Landlock sandbox libraries; historical runtime projects; and a final cross-platform alternatives search. Later broad searches increasingly repeated these architecture families or surfaced newer frontends whose independent implementation evidence was thinner. Selection favors distinct engineering mechanisms rather than project popularity.

The retained set includes C, C++, Go, Rust, and shell implementations; kernel, library, CLI, daemon, and host/guest designs; and cloud, desktop, mobile-system, contest-grading, HPC, Windows, and BSD communities. Canonical repository links were checked by opening the repository page or reading GitHub API metadata. Each retained repository also had additional primary material opened and read; linked implementation and documentation entry points identify that evidence. API rate limiting was handled with public repository pages and direct source reads rather than treating snippets as verification.

Important scope decisions and limitations:

- [rkt](https://github.com/rkt/rkt) marks its project ended and was not retained as a current selection. [Charliecloud's GitHub landing page](https://github.com/hpc/charliecloud) directs development to GitLab; an ongoing official substantive GitHub mirror was not established, so it was excluded. Sarus also surfaced during HPC discovery but was not retained after its architecture-documentation endpoint was inaccessible in this pass.
- General VM monitors, language-only/Wasm sandboxes, image builders, orchestration platforms, security scanners, tutorial runtimes, and thin launch wrappers were outside the selected scope. Moby was inspected but omitted to leave room for native jail and process-sandbox implementations. This is a selection guide, not an exhaustive inventory.
- Minijail and FreeBSD are explicitly identified as official mirrors. Incus and Sandboxie are identified as substantive forks with separate evolution; their predecessors are not separately counted. No inference of active maintenance is made merely from repository age, stars, or a recent push.
- C4 is assigned only where the inspected material supports both a multi-year history and compatibility or complexity-management practices. Other projects may also meet C4, but that is not needed to justify their inclusion here.
- This was read-only research: no candidate code was built or run, and no benchmark or isolation claim was independently validated. Links to development branches can change, and some design documents preserve historical details. Performance discussion therefore concerns documented mechanisms and tradeoffs, not comparative numerical guarantees.
