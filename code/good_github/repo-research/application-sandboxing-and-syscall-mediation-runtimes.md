# Application sandboxing and syscall mediation runtimes

Research date: **2026-10-09**.

This report selects 23 GitHub repositories implementing application confinement, sandbox construction, library isolation, user-space operating-system interfaces, or substantial syscall mediation. It includes reusable enforcement libraries as well as complete runtimes. Syscall instrumentation and compatibility tools are identified separately: intercepting a syscall does not, by itself, establish a boundary against malicious native code. SGX library OSes also have a different trust direction, protecting applications from an untrusted host.

The criteria below are engineering assessments grounded in the cited source and documentation, not security certifications or claims that every component is exemplary. Repository pages were opened to verify identity; implementation or design material beyond the root README was inspected for every entry. Source links generally follow the inspected default branch and can change after this research date.

## Criteria legend

- **C1 — Difficult correctness:** meaningful invariants, concurrency, adversarial inputs, ABI semantics, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or mechanisms useful across applications and policies.
- **C3 — Performance with structure:** explicit runtime costs addressed through understandable architectural choices.
- **C4 — Sustained evolution:** multi-year evidence of compatibility work, testing, or complexity management, rather than repository age alone.

## Linux process confinement and sandbox construction

### [containers/bubblewrap](https://github.com/containers/bubblewrap)

**Language/role:** C; low-level, unprivileged sandbox construction used by Flatpak and other consumers.

Study the boundary between a mechanism provider and its policy-setting caller. Bubblewrap constructs an initially empty mount namespace, then exposes selected resources and optionally adds PID, network, IPC, and syscall restrictions. Its README explicitly makes the caller responsible for choosing a secure configuration; the executable is not a complete policy by itself.

- **C1:** Path resolution during privileged namespace setup is security-sensitive. The inspected `safe_openat` implementation uses `openat2` with `RESOLVE_IN_ROOT` and `RESOLVE_NO_MAGICLINKS`, handles retryable failures, and has a fallback that treats final-component symlinks and descriptor validation explicitly. This is a concrete study of kernel-version compatibility interacting with escape prevention. [Implementation entry point](https://github.com/containers/bubblewrap/blob/main/safe_openat.c).
- **C2:** Mount construction, namespace selection, descriptor handling, and externally supplied seccomp filters form a composable substrate for different application policies. The [repository's security and usage discussion](https://github.com/containers/bubblewrap#sandbox-security) explains both the abstraction and pitfalls involving terminals, D-Bus, and nested sandboxes.

### [google/nsjail](https://github.com/google/nsjail)

**Language/role:** C++; Linux process supervisor combining namespaces, resource controls, and seccomp policies.

NsJail is useful for studying how one supervisor supports single executions, repeated execution, and network-service workloads without hiding the individual Linux isolation mechanisms. Its Protobuf configuration describes filesystem, identity, resource, and syscall policy together.

- **C1:** The syscall-filter installation code coordinates `no_new_privs`, Kafel compilation, listener creation, close-on-exec, and descriptor transfer to the parent. It explicitly refuses notification-based execution when the selected mode lacks a supervisor, avoiding silently running without the requested policy. [Filter implementation](https://github.com/google/nsjail/blob/master/sandbox.cc).
- **C2:** The same supervision machinery serves command execution, fuzzing, network challenge services, and desktop examples, with policies supplied as configuration or command-line options. The [repository documentation](https://github.com/google/nsjail#readme) is the policy and execution-mode entry point.

### [netblue30/firejail](https://github.com/netblue30/firejail)

**Language/role:** C; application-oriented Linux confinement with a substantial desktop profile ecosystem.

Firejail exposes the engineering cost of keeping ordinary applications usable under filesystem, network, capability, and syscall restrictions. Unlike a minimal namespace constructor, its scope includes application-specific compatibility policy.

- **C1:** The sandbox lifecycle coordinates capability reduction, signal handling, process-group termination, and AppArmor application. The code distinguishes stacking an AppArmor profile from replacing one, documenting that replacement can relax existing protection. [Lifecycle implementation](https://github.com/netblue30/firejail/blob/master/src/firejail/sandbox.c).
- **C2:** Reusable profile rules and shared profile fragments support many applications, while the common runtime performs enforcement. This is valuable for studying the division between generic mechanisms and compatibility exceptions.
- **C4:** The [release notes](https://github.com/netblue30/firejail/blob/master/RELNOTES) document changes across 2019–2026, including syscall behavior changes, disabling problematic overlay functionality, evolving application profiles, syscall-ABI updates, and test/CI corrections. These provide stronger evidence of sustained complexity management than its age alone.

### [google/minijail](https://github.com/google/minijail)

**Language/role:** C/C++ with supporting tooling; containment library and launcher used in ChromeOS and Android. **Official GitHub mirror:** the README identifies Chromium's Gitiles repository as the main source.

Study the combination of an embeddable self-confinement API and an external launcher, including when policy becomes effective during dynamic loading. The documented threat model is mitigation of compromise in known binaries; it expressly excludes safely executing arbitrary attacker-controlled binaries or shared libraries.

- **C1:** Policy generation must include failure paths and distinguish launcher syscalls from application requirements. The tools documentation explains that preloading can install filters after `execve`, and that audit-based inference can otherwise over-authorize calls such as `ioctl`, `mmap`, and `prctl`.
- **C2:** `libminijail` and `minijail0` expose the same containment mechanisms to programs and service launchers. [Repository and threat-model entry point](https://github.com/google/minijail#readme).
- **C3:** The policy compiler accepts architecture-specific constants and syscall-frequency files for profile-guided BPF optimization. [Tooling design and policy-generation cautions](https://github.com/google/minijail/blob/main/tools/README.md).

### [ioi/isolate](https://github.com/ioi/isolate)

**Language/role:** C; sandbox and resource-accounting runtime for hostile programming-contest submissions.

Isolate is a compact alternative to general container management for studying execution limits, reproducibility, cleanup, and reporting. Its interface separates sandbox initialization, execution, and cleanup, allowing contest systems to reuse the mechanism.

- **C1:** The manual carefully separates wall time from CPU time, per-process address-space limits from aggregate control-group accounting, and process-count failures from sandbox failures. It warns that multi-process time and memory enforcement requires control-group mode. [Execution and resource semantics](https://github.com/ioi/isolate/blob/master/isolate.1.txt).
- **C2:** Directory rules, environment rules, resource limits, and machine-readable execution metadata provide a reusable execution contract for different graders and languages.
- **C3:** The [NEWS file](https://github.com/ioi/isolate/blob/master/NEWS) records a change to process placement in cgroups to reduce sandbox startup work. The same history describes fixes for shared `/dev/shm` exposure and resource-limit state surviving between runs—useful examples of optimizing repeated execution without ignoring isolation state.

### [multikernel/sandlock](https://github.com/multikernel/sandlock)

**Language/role:** Rust core with C ABI, Python, and Go interfaces; application sandbox combining Landlock, seccomp filters, and a syscall-notification supervisor.

This adds a newer design centered on dynamic mediation rather than mount namespaces. Its architecture includes notification handlers for network operations, resource tracking, and a userspace copy-on-write filesystem. Treat it as an implementation study; no C4 or independently validated security/performance claim is assigned.

- **C1:** The documented launch protocol installs restrictions, transfers the notification descriptor, waits for supervisor readiness, closes inherited descriptors, and only then executes the workload. The control registry also handles crashes and inherited state using semaphore undo, instance tokens, and a small insertion journal.
- **C2:** The core supports CLI, OCI, and language integrations. A `Handler` trait extends the notification chain, while built-in handling precedes extensions and registration rejects explicitly denied syscalls. These are substantive policy-composition abstractions. [Architecture and extension-order entry point](https://github.com/multikernel/sandlock/blob/main/docs/architecture.md).

The same document states a material limitation: copy-on-write staging covers regular files, directories, and symlinks; effects on sockets, FIFOs, and devices are not reverted. Kernel requirements and policy opt-outs are documented in the [repository](https://github.com/multikernel/sandlock#requirements).

## Brokered native application and library sandboxes

### [google/sandboxed-api](https://github.com/google/sandboxed-api)

**Language/role:** C++; Sandboxed API and its underlying **Sandbox2** subsystem, counted together as one repository.

Study how a C/C++ library can move into a restricted process while retaining an API usable by its original caller. SAPI generates a host-side proxy and sandbox-side RPC stub; Sandbox2 supplies the lower-level execution and policy machinery.

- **C1:** Pointers and arrays cross address spaces through explicit synchronization types, and library calls can fail because of crashes, policy violations, resource exhaustion, or RPC errors. The transaction abstraction monitors the sandbox and supports restarting failed library instances. [SAPI architecture and failure model](https://developers.google.com/code-sandboxing/sandboxed-api/explained).
- **C2:** Policy, executor, and sandboxee are separate abstractions, while generated library interfaces make the resulting isolated component reusable by different host applications. This is more than a wrapper around a command launcher. [Sandbox2 architectural entry point](https://developers.google.com/code-sandboxing/sandbox2/explained).

### [sandboxie-plus/Sandboxie](https://github.com/sandboxie-plus/Sandboxie)

**Language/role:** C/C++; Windows application isolation, kernel driver, injected DLL, service, and user interfaces.

This is a **substantively evolved community fork**, explicitly described as such by its README. The original Sophos source repository is not counted separately. Study the interaction of Windows access tokens, kernel enforcement, compatibility hooks, and virtualized filesystem/registry views; the core is shared by Plus and Classic.

- **C1:** Restricted primary tokens remain relevant even when an application bypasses patched user-mode syscall stubs. Selected operations are redirected through `SbieDrv`, while `SbieDll` merges sandbox and host filesystem/registry views. Keeping access enforcement correct independently of compatibility redirection is the central invariant.
- **C2:** The driver, injected runtime, and helper service support many applications and multiple independently configured sandboxes. This is a substantial native Windows virtualization layer, not only a launch policy. [Isolation mechanism and component responsibilities](https://sandboxie-plus.github.io/sandboxie-docs/Content/IsolationMechanism/).

The [repository's project history and feature description](https://github.com/sandboxie-plus/Sandboxie#project-history) identify the fork and its separate evolution, including changes to token construction and per-sandbox network controls.

### [chromium/chromium](https://github.com/chromium/chromium)

**Language/role:** Primarily C++; the **sandbox subsystem** inside Chromium's monorepo. **Official GitHub mirror**, as identified by the repository.

The relevant selection is the process sandbox, not Chromium as a whole. Its Windows design provides an especially clear account of broker/target separation, policy evaluation, interception, and operating-system enforcement.

- **C1:** The broker performs permitted operations for a restricted target. Interception and IPC provide compatibility; restricted tokens, job objects, desktop isolation, and integrity levels provide the underlying restrictions. This separation prevents assuming that patching an API is itself a security boundary.
- **C2:** Both broker and target link the sandbox library, with distinct responsibilities for policy, process creation, IPC, and interception. The model is reusable across differently privileged process roles.
- **C3:** The target evaluates policy locally to avoid unnecessary IPC, but the documentation explicitly excludes that optimization from the security guarantee. This is a precise example of accelerating a path without trusting it. [Design entry point](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/design/sandbox.md).

## Application kernels and enclave library OSes

### [google/gvisor](https://github.com/google/gvisor)

**Language/role:** Go with low-level support code; application kernel and `runsc` sandbox runtime.

Study a sandbox that implements the application's operating-system interface in a userspace kernel, the Sentry. The Gofer handles access to host-backed files, with configuration-dependent direct access described in the security model.

- **C1:** The Sentry independently implements guest system calls rather than passing guest arguments directly into corresponding host calls. Its own permitted host interface is separately constrained, so both guest-to-Sentry and Sentry-to-host boundaries require reasoning. [Security architecture](https://github.com/google/gvisor/blob/master/g3doc/architecture_guide/security.md).
- **C2:** Virtualized processes, files, networking, and other OS resources support application workloads through a common Linux-facing interface. This is reusable OS implementation work, not merely a list of blocked calls.
- **C3:** The design explicitly discusses expensive sandbox transitions and the tradeoff between delegating operations to the host and maintaining guest-side caches. It explains why some choices reduce duplicate resource consumption while costing performance on particular workloads. The same architecture document is the best starting point; it also states that hardware side channels are outside the general protection claim.

### [gramineproject/gramine](https://github.com/gramineproject/gramine)

**Language/role:** Primarily C; Linux-compatible, multi-process library OS, including an Intel SGX backend. Formerly Graphene; counted once under its canonical repository.

Gramine is valuable for studying how Linux semantics change when OS services are reconstructed inside an application runtime. In SGX mode its principal security concern includes an untrusted host; it should not be treated as interchangeable with host-protecting process sandboxes.

- **C1:** Each process maintains local state and coordinates with peers through messages over host Unix-domain sockets. A leader assigns process identities and manages locking protocols. This makes familiar operations into distributed-state problems, with explicit limitations for file synchronization and cross-process futexes.
- **C2:** The runtime implements syscall, pseudo-filesystem, VFS, process, signal, and IPC abstractions across applications. The documented mapping of Linux operations onto its internal mechanisms is unusually useful for understanding compatibility boundaries. [Implementation-oriented feature reference](https://gramine.readthedocs.io/en/stable/devel/features.html).

Read the limitations alongside the supported-call list: the inspected reference describes partially implemented operations and filesystem state that is not fully synchronized across processes. Those are part of the learning value, not evidence of complete Linux equivalence.

### [occlum/occlum](https://github.com/occlum/occlum)

**Language/role:** Rust with C support; multi-process library OS for Intel SGX.

Occlum offers a different enclave architecture: multiple LibOS processes share an enclave, with optional PKU-based fault isolation. It is useful for comparing enclave resource management and host-I/O mediation with per-process library-OS designs.

- **C1:** Filesystem choices have distinct trust semantics. Its SEFS layers provide integrity-only or encrypted storage, while HostFS intentionally exchanges data with the untrusted host without equivalent protection. UnionFS overlays a writable encrypted layer on an integrity-protected image. [Filesystem architecture](https://github.com/occlum/occlum/blob/master/docs/fs_overview.md).
- **C2:** Multiple filesystem implementations are composed under a common LibOS view, alongside legacy-application execution and Linux-facing services. The mounting and image model supports different confidentiality and persistence requirements.
- **C3:** Sharing an enclave is an explicit architectural response to process startup and IPC costs; the [repository overview](https://github.com/occlum/occlum#readme) also explains optional PKU and dynamic enclave-memory support. Published numerical speedups are not adopted here as independently verified results.

## Enforcement libraries and policy compilation

### [seccomp/libseccomp](https://github.com/seccomp/libseccomp)

**Language/role:** C; architecture-aware syscall-policy construction and BPF generation library.

This is the core library to study when the hard problem is converting a portable filtering API into correct architecture-specific programs. Its value lies in filter semantics and code generation, beyond the mechanics of invoking the kernel's seccomp API.

- **C1:** The generator manages argument tests, architecture handling, instruction blocks, jump targets, and endian conversion. Incorrect merging or branch construction can weaken an intended policy. [BPF generator](https://github.com/seccomp/libseccomp/blob/main/src/gen_bpf.c).
- **C2:** The API abstracts BPF instructions and architecture-specific syscall numbers behind reusable filtering operations for many host programs.
- **C3:** The generator supports priority ordering and balanced syscall decision trees, with explicit intermediate representations for constructing the result.
- **C4:** The [changelog](https://github.com/seccomp/libseccomp/blob/main/CHANGELOG) documents multi-year evolution including the stable API treatment of return values, user notifications, architecture additions, generated syscall tables, testing changes, and fixes to filter-state and comparison handling. These changes connect longevity directly to compatibility and correctness management.

### [rust-vmm/rust-vmm](https://github.com/rust-vmm/rust-vmm)

**Language/role:** Rust; specifically the **`seccompiler` subsystem** in the rust-vmm monorepo.

The old [`rust-vmm/seccompiler`](https://github.com/rust-vmm/seccompiler) repository is archived and points to this monorepo; it is not counted separately. Study a relatively focused typed compiler from syscall policies to loadable seccomp BPF, rather than the monorepo's other virtualization components.

- **C1:** Conditions validate argument indices and translate 64-bit comparisons into tests of high and low words with carefully calculated branch offsets. These are security-sensitive numerical and control-flow semantics. [Condition lowering](https://github.com/rust-vmm/rust-vmm/blob/main/seccompiler/src/backend/condition.rs).
- **C2:** Conditions form AND-composed rules; syscall entries hold OR-composed rules; filters add match/default actions and target architecture. Equivalent Rust and JSON representations feed compilation and installation. [API and semantic model](https://github.com/rust-vmm/rust-vmm/blob/main/seccompiler/src/lib.rs).

This is a reusable enforcement component, not a full filesystem/network sandbox on its own.

### [landlock-lsm/rust-landlock](https://github.com/landlock-lsm/rust-landlock)

**Language/role:** Rust; safe application-facing library for Landlock self-confinement.

Study how a security API can expose compatibility choices explicitly when running on kernels that support different restriction sets. A successful function return and complete enforcement are deliberately distinguishable outcomes.

- **C1:** Compatibility state distinguishes full, partial, unsupported, and dummy behavior; best-effort and hard-requirement modes take different paths when a feature is unavailable. The implementation includes tests for these transitions rather than treating unsupported enforcement uniformly. [Compatibility state machine](https://github.com/landlock-lsm/rust-landlock/blob/main/src/compat.rs).
- **C2:** A ruleset builder composes handled accesses and path rules, then returns an enforcement status from `restrict_self`. Its types also support progressively narrowing an application's rights as initialization completes. [Ruleset API and implementation](https://github.com/landlock-lsm/rust-landlock/blob/main/src/ruleset.rs).

The library is useful both for applications restricting themselves and for launchers applying policy before executing other programs.

### [jart/pledge](https://github.com/jart/pledge)

**Language/role:** C; Linux userspace implementation of OpenBSD-inspired `pledge` and `unveil` interfaces using seccomp and Landlock.

Study the translation from an understandable set of behavioral promises into lower-level syscall and argument rules. The code is especially instructive about semantic differences between similarly named APIs on different operating systems.

- **C1:** The implementation documentation spells out one-way restriction, `no_new_privs`, initialization timing, thread-exit versus process-exit behavior, and special handling of identity and file-mode changes. These are concrete semantic traps when porting a security interface. [Detailed `pledge` implementation contract](https://github.com/jart/pledge/blob/master/libc/calls/pledge.c).
- **C2:** Promise groups such as standard I/O, path reading, process creation, and networking provide reusable policy vocabulary instead of requiring every application to author BPF.

A material caveat in the inspected contract is that unsupported kernels may produce a successful no-op. Path filtering belongs to `unveil`, and the networking promise is not an address-level firewall. The [repository overview](https://github.com/jart/pledge#readme) is the compact starting point; deployment assumptions must be read with the source contract.

## Syscall mediation, instrumentation, and reproducibility

### [facebookexperimental/reverie](https://github.com/facebookexperimental/reverie)

**Language/role:** Rust; framework for intercepting, modifying, suppressing, or injecting Linux system calls.

Reverie belongs here as a reusable mediation runtime. Its documented uses include tracing, fault injection, and controlling scheduling to expose concurrency problems; those uses should not be confused with a ready-made malicious-code security policy.

- **C1:** The tool interface ties thread execution ownership to ownership of futex and child-clear-tid synchronization. Its comments explain the deadlock possible when a joiner's wait and an exiting thread's wake are handled in different domains. A single ownership enum encodes that relationship. [Tool contract](https://github.com/facebookexperimental/reverie/blob/main/reverie/src/tool.rs).
- **C2:** Global and per-thread tool state, typed syscall wrappers, async handlers, event subscriptions, and a backend/tool separation let different instrumentation policies share process-control machinery. [Framework architecture](https://github.com/facebookexperimental/reverie#readme).

The README warns about ptrace overhead for syscall-heavy workloads; selective event subscription is useful to inspect, without assuming that every listed backend has equivalent maturity or guarantees.

### [proot-me/proot](https://github.com/proot-me/proot)

**Language/role:** C; ptrace-based userspace virtualization of filesystem paths and process execution.

PRoot is selected for syscall mediation and compatibility. Its manual explicitly says guest resource requests reach the host kernel and can use host devices and networking, so this entry is not a recommendation for a hostile-code boundary.

- **C1:** Path translation must account for guest roots, current directories, directory descriptors, symlinks, and host/guest bind substitutions. The implementation canonicalizes from the guest's viewpoint before converting the final path to a host path. [Path translation implementation](https://github.com/proot-me/proot/blob/master/src/path/path.c).
- **C2:** The runtime supplies unprivileged `chroot`/bind-style views, integrates QEMU user-mode for other instruction sets, and offers an extension mechanism for instrumentation. [Primary manual](https://github.com/proot-me/proot/blob/master/doc/proot/manual.rst).

This is a useful codebase for studying the distance between emulating namespace-like behavior at the syscall ABI and enforcing a kernel-backed access policy.

### [dettrace/dettrace](https://github.com/dettrace/dettrace)

**Language/role:** C++; research runtime for determinizing process trees through ptrace and controlled execution.

DetTrace is a **historical/prototype-oriented selection**. Its README describes older tested kernel ranges, an Intel x86-64 dependency, and limitations for newer Debian workloads. It is included for architecture, not as evidence of current general-purpose compatibility.

- **C1:** The scheduler maintains separate runnable, blocked, and finished process sets. Parent exit and surviving children require special transitions, and invalid removals or empty scheduling states are explicit errors. [Scheduler implementation](https://github.com/dettrace/dettrace/blob/master/src/scheduler.cpp).
- **C2:** The runtime applies determinization to a command and its descendants, with a reproducible initial filesystem and controlled observations such as file timestamps. This provides a reusable execution abstraction for reproducible computation and builds. [Scope, workflow, and limitations](https://github.com/dettrace/dettrace#readme).

The engineering lesson is how nondeterministic OS behavior becomes a runtime state-management problem; deterministic execution should not be read as a claim of a hardened security sandbox.

### [srg-imperial/SaBRe](https://github.com/srg-imperial/SaBRe)

**Language/role:** C and assembly; load-time selective binary rewriting for syscall, vDSO, and function mediation.

SaBRe adds a distinct interception mechanism to the selection. Its plugins implement tracing and syscall fault injection. The project contrasts a first architecture with separated plugin infrastructure against a second architecture sharing more of the client's runtime and libraries.

- **C1:** Interception can occur during thread-library and sanitizer initialization. The recursion protector uses initial-exec TLS to avoid recursive resolution through `__tls_get_addr`, and separately tracks when vDSO calls become usable. [Recursion and initialization implementation](https://github.com/srg-imperial/SaBRe/blob/master/plugin_api/recursion_protector.c).
- **C2:** A plugin interface separates event handling from binary rewriting, supporting tracing, no-op interception, and fault injection across x86-64 and RISC-V. The [architecture comparison](https://github.com/srg-imperial/SaBRe#sabre-10-vs-20) explains allocator, dependency, and TLS consequences for plugin authors.

This is an instrumentation substrate; sharing the client's address space is not itself protection against a malicious client.

## In-process library isolation and WebAssembly sandboxes

### [PLSysSec/rlbox](https://github.com/PLSysSec/rlbox)

**Language/role:** Header-only C++; typed interface for interacting with sandboxed libraries.

RLBox is worth studying because protecting the host requires controlling how it consumes results from a compromised library, not only isolating that library's instructions. Actual isolation is supplied by separately selected backends; the generic API does not make every backend a security boundary.

- **C1:** `tainted` and `tainted_volatile` values constrain operations on untrusted data. The `copy_and_verify` path deliberately copies pointed-to data before invoking a verifier, with an explicit comment identifying a time-of-check/time-of-use attack otherwise. It also rejects inappropriate verification operations on function and void pointers. [Typed-boundary implementation](https://github.com/PLSysSec/rlbox/blob/main/code/include/rlbox.hpp).
- **C2:** The same application-facing sandbox, callback, pointer, and verification abstractions support different isolation backends. The [repository's usage and testing guide](https://github.com/PLSysSec/rlbox#using-this-library) explains that separation and documents cross-platform and sanitizer testing.

### [bytecodealliance/wasmtime](https://github.com/bytecodealliance/wasmtime)

**Language/role:** Rust; embeddable WebAssembly runtime, including WASI capability-mediated system access.

This monorepo is selected for its sandbox runtime and host interfaces. Study how a validated execution format, compiler-generated checks, runtime allocation, and host-provided capabilities cooperate to isolate untrusted modules.

- **C1:** Linear-memory bounds, typed control transfers, inaccessible guest call-stack internals, and restricted imports form the boundary. Runtime mitigations include guard regions and clearing reusable instance state; WASI filesystem access follows a capability model. [Security architecture](https://github.com/bytecodealliance/wasmtime/blob/main/docs/security.md).
- **C2:** Embedders define imported functionality and resource access while reusing the execution engine across different applications and modules.
- **C3:** Pooling memories and tables avoids repeated allocation, copy-on-write heap images defer initialization work, and `InstancePre` moves import resolution/type checking before repeated instantiation. These are explicit architectural responses to short-lived-instance costs. [Instantiation design guide](https://github.com/bytecodealliance/wasmtime/blob/main/docs/examples-fast-instantiation.md).

Host imports still define what a module can do outside its isolated memory; broad imports can deliberately grant broad authority.

### [bytecodealliance/lucet](https://github.com/bytecodealliance/lucet)

**Language/role:** Rust with a C embedding interface; historical ahead-of-time WebAssembly compiler and runtime. **Archived and end-of-life:** the README says maintenance ceased and directs users to Wasmtime.

Retained as a separate historical implementation, not a second current recommendation for the Wasmtime ecosystem. Lucet makes the compile/load boundary especially visible: a compiler produces native shared objects that an embedding runtime loads and instantiates.

- **C1:** The security design separates compiler-input attacks, guest-to-host attacks, and guest-to-guest attacks. It distinguishes runtime fault isolation from application responsibilities such as resource limits and safe host bindings, and records incomplete ABI checking in the historical design. [Security model](https://github.com/bytecodealliance/lucet/blob/main/docs/src/Security.md).
- **C2:** `lucet-runtime` exposes Rust and C interfaces for module loading, instance resource management, exported calls, and exception recovery. Its public API, runtime internals, macros, and test crates are separated. [Runtime architecture](https://github.com/bytecodealliance/lucet/blob/main/docs/src/lucet-runtime.md).

The end-of-life notice takes precedence over older documentation that still describes development as active.

## Coverage, search process, and limitations

Discovery used 21 live web queries across distinct formulations, including: general application sandbox/syscall mediation; Linux namespaces with seccomp; library OSes and SGX; Windows driver/token isolation; Rust syscall interception and deterministic execution; Landlock and pledge-style APIs; in-process WebAssembly/RLBox isolation; contest execution sandboxes; selective binary rewriting; Capsicum-based supervisors; macOS Seatbelt libraries; and seccomp user-notification runtimes. Follow-up searches and source inspection added less familiar implementations such as SaBRe, DetTrace, rust-landlock, and Sandlock. Later searches largely returned already covered mechanisms, small wrappers, tutorials, or recent projects with weaker evidence; the notification search supplied the final distinct implementation.

The selection spans C, C++, Rust, Go, and assembly, from small enforcement libraries to application kernels and browser subsystems. Linux has the broadest coverage. Windows is represented by two substantially different architectures; macOS coverage is limited to cross-platform frameworks and Chromium's wider subsystem. The BSD searches did not yield a separately retained userspace runtime with equally strong inspected evidence, and the native kernel implementations of Capsicum, pledge, and Landlock are outside this report's main runtime scope.

General OCI orchestration, full virtual-machine monitors, malware-analysis products, language interpreters without a specifically examined sandbox boundary, thin convenience wrappers, tutorial repositories, and lists of projects were not retained. Native Client and other historical mechanisms appear only where relevant to inspected frameworks; no guessed GitHub mirror was substituted. The archived standalone seccompiler repository was replaced by its actual monorepo location. Sandbox2/SAPI, Chromium's sandbox, and rust-vmm's seccompiler each count once. The original Sandboxie release and its evolved community fork are not double-counted.

Canonical GitHub pages and additional primary implementation/design sources were opened for every retained entry. Public raw source reads supplemented browser reads; no candidate was cloned, installed, or executed. C4 is assigned only where inspected multi-year history supports it. A non-archived repository is not assumed to be actively maintained, and performance claims are architectural explanations rather than reproduced benchmarks. This report is a source-reading selection guide, not a deployment comparison or an independent security audit.
