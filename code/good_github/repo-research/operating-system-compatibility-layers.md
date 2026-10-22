# Operating system compatibility layers

Research date: **2026-10-09**.

This selection covers implementations that reproduce an operating system's application-facing behavior on another host or execution substrate: binary/API runtimes, foreign-kernel ABI subsystems, library operating systems, Android integration, and substantial POSIX interface shims. It includes 20 repositories. For operating-system monorepos, only the named compatibility subsystem is assessed. Container integration and source-level portability are identified separately from binary ABI emulation.

The criteria are selection judgments grounded in the linked implementation material, not certifications of correctness or recommendations to deploy every project. Repository URLs and archival status were checked through repository pages and the GitHub API; an unarchived repository is not by itself evidence of active maintenance.

- **C1 — Difficult correctness:** invariants, concurrency, adversarial inputs, semantic mismatches, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and mechanisms supporting different applications or subsystems.
- **C3 — Performance with structure:** concrete overhead or resource constraints addressed through an understandable design.
- **C4 — Sustained evolution:** evidence across years of compatibility preservation, testing, or complexity management.

## Windows and macOS application environments

### [wine-mirror/wine](https://github.com/wine-mirror/wine)

**Language/role:** C, with assembly and other implementation languages; Windows binary and API compatibility on Unix. **GitHub source mirror:** the repository explicitly identifies WineHQ's GitLab repository as its upstream. Wine's loader and Winelib provide both execution of Windows binaries and a library interface for porting applications.

Study the separation between client API implementations and server-owned Windows objects. **C1:** the mutex implementation tracks owner identity, recursive acquisition, abandonment when a thread exits, access rights, and wakeups. Its assertions expose invariants that would disappear in a simplistic mapping to a host mutex. **C2:** mutexes participate in a shared object interface with operations for signaling, waiting, destruction, and handle lookup; this is a reusable model for Windows kernel-object semantics. These mechanisms are visible in [server/mutex.c](https://github.com/wine-mirror/wine/blob/master/server/mutex.c).

**Entry point:** follow `mutex_sync_ops`, `do_grab`, `do_release`, and `abandon_mutexes` in that source file, then use the repository's `server` and `dlls` organization to trace the boundary outward.

### [ValveSoftware/Proton](https://github.com/ValveSoftware/Proton)

**Language/role:** C/C++, Python, and build scripts; a Wine-based Windows gaming environment integrated with Steam. This is a separately evolved integration project, not an independent reimplementation of all Wine functionality. The repository combines Wine with graphics, media, VR, and Steam-facing components.

Study compatibility as persistent application state management. **C1:** the launcher models distribution and application-prefix state separately, uses filesystem locks, tracks installed files, and handles upgrades and downgrades without treating the entire prefix as disposable. **C2:** its runtime assembly and configuration apply across games and host environments. **C4:** the current launcher retains explicit migration logic for Proton 3.7, including a dated 2018 broken-prefix case, and later controller-registry changes. This is concrete accumulated compatibility work, not merely an old repository date. See the [launcher and `CompatData` implementation](https://github.com/ValveSoftware/Proton/blob/proton_11.0/proton).

**Entry point:** `Proton`, `CompatData`, and `upgrade_pfx` in the launcher. Read this repository for integration and lifecycle design; study Wine separately for the underlying Windows API implementation.

### [darlinghq/darling](https://github.com/darlinghq/darling)

**Language/role:** Objective-C, C, and C++; Darwin/macOS compatibility on Linux, including numerous component repositories assembled by the main project.

Study how a foreign OS's cross-process services shape the architecture. **C1:** Mach IPC and related services require shared coordination among processes in a Darling container. The project's [darlingserver design discussion](https://github.com/darlinghq/darling/issues/1093) explains why these services need a supervising process and why the earlier kernel-module approach made failures difficult to debug. **C2:** the server supplies common services to multiple guest processes instead of implementing a separate workaround inside each application. **C4:** the [release record](https://github.com/darlinghq/darling/releases) documents the 2022 switch to a userspace implementation, subsequent source and build reorganizations, and later compatibility additions through 2026.

**Entry points:** the darlingserver design discussion and release record. Some older documentation describes the superseded kernel module; the release record establishes that the userspace transition actually shipped. Framework presence should not be mistaken for complete application compatibility.

### [cygwin/cygwin](https://github.com/cygwin/cygwin)

**Language/role:** C and C++; POSIX runtime on Windows, principally `winsup/cygwin` with supporting Newlib code. **Official project mirror:** the repository identifies `cygwin.com/cgit/newlib-cygwin/` as its source. This supports applications built for Cygwin's runtime, rather than arbitrary Linux ELF binaries.

Study the gap between POSIX process semantics and Windows facilities. **C1:** reproducing `fork` requires restoring the child's address-space state and coordinating parent and child; DLL placement and address-space randomization complicate that contract. Signal delivery and interruptible socket operations introduce further coordination. **C2:** shared process bookkeeping, descriptor handling, path translation, and the DLL interface support a broad Unix software environment. **C3:** the architecture discussion explains why native NT interfaces are used where appropriate and why `spawn` maps more efficiently to Windows than a `fork`/`exec` sequence. See [Highlights of Cygwin Functionality](https://cygwin.com/cygwin-ug-net/highlights.html).

**Entry point:** that architecture chapter, especially process creation, signals, and descriptor selection. Its implementation history is useful, but consult current code before assuming every historical socket detail still applies.

### [msys2/msys2-runtime](https://github.com/msys2/msys2-runtime)

**Language/role:** C/C++; an explicitly Cygwin-derived runtime adapted for a Unix-style build environment interoperating with native Windows programs. Its separate value here is the evolved interoperation behavior, not a second count of Cygwin's inherited implementation.

Study automatic argument conversion at a process boundary. **C1:** the path converter must distinguish Windows paths, UNC paths, URLs, rooted Unix paths, path lists, and quoted substrings without changing unrelated arguments. These cases have distinct conversion functions in [msys2_path_conv.cc](https://github.com/msys2/msys2-runtime/blob/msys2-3.6.10/winsup/cygwin/msys2_path_conv.cc). **C2:** conversion is a runtime service used by mixed toolchains, with separate controls for process arguments and environment variables. The [filesystem-path documentation](https://www.msys2.org/docs/filesystem-paths/) explains both the behavior and explicit exclusion mechanisms when heuristic recognition is wrong.

**Entry points:** the converter's `path_type` dispatch and the filesystem-path guide. This is a useful example of making unavoidable heuristics configurable while retaining compatibility with native executables.

## Linux ABI implementations inside other kernels

### [freebsd/freebsd-src](https://github.com/freebsd/freebsd-src)

**Language/role:** C and assembly; assess **Linuxulator**, particularly `sys/compat/linux`, rather than the entire FreeBSD OS. The repository is the FreeBSD project's publish-only GitHub source repository.

Study how an existing kernel hosts a second executable ABI. **C1:** Linux futex behavior involves address alignment, private versus shared identity, atomic operations, wake/requeue behavior, priority-inheritance operations, and robust-list cleanup. The current [linux_futex.c](https://github.com/freebsd/freebsd-src/blob/main/sys/compat/linux/linux_futex.c) shows this translation using FreeBSD kernel machinery. **C2:** the ABI execution-vector design groups syscall dispatch, error translation, signal handling, and executable setup into reusable per-ABI infrastructure. The official [Linux emulation architecture article](https://docs.freebsd.org/en/articles/linux-emulation/) explains that structure and the threading-semantic mismatches it must accommodate.

**Entry points:** the futex implementation and architecture article. The article originated in the 2006 Linux 2.6/NPTL work; it is valuable historical design material, not a statement of today's supported Linux versions or architecture coverage.

### [NetBSD/src](https://github.com/NetBSD/src)

**Language/role:** C and assembly; assess **`sys/compat/linux` and its connection to NetBSD's emulation framework**. **Official automatic CVS conversion:** the repository warns that Git commit links can change; branch-based source paths are used here.

Study a compact, explicit registration interface for a foreign ABI. **C2:** `emul_linux` supplies the emulation name and filesystem prefix, error mapping, syscall table, signal/trap callbacks, register initialization, and process/thread lifecycle hooks. **C1:** those hooks allocate and reset per-thread emulation state and preserve Linux child-TID behavior across process creation and exit. The lifecycle code asserts assumptions about remaining threads and handles guest-memory writes during cleanup. See [linux_exec.c](https://github.com/NetBSD/src/blob/trunk/sys/compat/linux/common/linux_exec.c).

**Entry point:** `emul_linux` and its lifecycle callbacks in that file. The surrounding source listing separates common Linux translations from architecture-dependent material, making this a useful comparison with FreeBSD's execution-vector approach. This entry makes no claim that every Linux syscall or every NetBSD architecture is supported.

### [TritonDataCenter/illumos-joyent](https://github.com/TritonDataCenter/illumos-joyent)

**Language/role:** C and assembly; assess the **LX brand** in the SmartOS/Triton illumos derivative. This is a substantive downstream implementation of Linux compatibility, not an additional listing of the generic illumos upstream.

The introductory design commentary in [lx_brand.c](https://github.com/TritonDataCenter/illumos-joyent/blob/master/usr/src/uts/common/brand/lx/os/lx_brand.c) is unusually useful. **C1:** usermode emulation must avoid consuming a Linux application's potentially tiny thread stack. The design maintains separate native and brand stacks, tracks execution mode, and saves/restores extra state through signal delivery and context operations. **C2:** brand callbacks integrate executable loading, process/thread lifecycle, signals, and syscalls into a common zone personality. **C3:** some calls are serviced in-kernel, while others return to the brand library; the comments explain moving more work onto the regular illumos syscall path for accuracy and performance.

**Entry point:** the overview and `brand_ops` table in `lx_brand.c`. It shows a hybrid kernel/userspace translator with explicit boundary bookkeeping.

## Userspace kernels and Linux execution environments

### [google/gvisor](https://github.com/google/gvisor)

**Language/role:** Go, with supporting assembly and C/C++ tests; a Linux-compatible application kernel for sandboxed workloads. The relevant subsystem is the **Sentry**, not merely the `runsc` command-line wrapper.

Study Linux compatibility as a security boundary. **C1:** the Sentry maintains its own process identities, memory-management behavior, signals, filesystems, and networking; guest syscalls are implemented rather than forwarded wholesale to the host. The [architecture introduction](https://gvisor.dev/docs/architecture_guide/intro/) explains the restricted host interface and the more privileged Gofer used for necessary external access. **C2:** the Linux-facing kernel implementation is separated from interchangeable interception platforms, including Systrap and KVM, and can serve varied container workloads. **C3:** the same guide explains dynamic host-resource use and the differing interception mechanisms instead of requiring a fully provisioned guest OS per sandbox.

**Entry point:** the architecture introduction's Sentry, Gofer, and platform discussion. Compatibility depends on implemented interfaces; the project's design explicitly does not make unsupported kernel functionality transparently available.

### [gramineproject/gramine](https://github.com/gramineproject/gramine)

**Language/role:** C and assembly; a Linux-compatible library OS, formerly Graphene, with Linux and Intel SGX execution backends.

Study the distinction between emulated application semantics and a deliberately small host abstraction. **C2:** the [new-syscall guide](https://github.com/gramineproject/gramine/blob/master/Documentation/devel/new-syscall.rst) walks from the architecture-specific syscall table into LibOS handlers and then, only where needed, the Platform Adaptation Layer (PAL). It explains why expanding the PAL should be avoided when existing operations suffice. **C1:** the [futex implementation](https://github.com/gramineproject/gramine/blob/master/libos/src/sys/libos_futex.c) models waiter ownership and requeueing under a shared lock; its comments specify which lock guards the futex association after a waiting thread wakes.

**Entry points:** those two files. The inspected futex implementation explicitly limits cooperating waiters to one process, a useful reminder that a multi-process library OS can still have narrower semantics for a particular Linux operation.

### [occlum/occlum](https://github.com/occlum/occlum)

**Language/role:** Rust, with C/assembly and SGX integration; a multi-process library OS for running existing applications in an Intel SGX enclave.

Study how an OS compatibility layer preserves familiar filesystem behavior while changing the trust model. **C1:** the [filesystem design](https://github.com/occlum/occlum/blob/master/docs/fs_overview.md) distinguishes integrity-only images, encrypted writable storage, and explicitly untrusted host access. Attestable input images and mutable runtime state require different guarantees. **C2:** its root filesystem composes a read-only integrity-protected SEFS branch with a writable encrypted branch through UnionFS; HostFS, RamFS, ProcFS, and DevFS supply other behavior behind the filesystem interface. **C3:** the repository describes multiple LibOS processes sharing a single enclave as its multitasking architecture; this is an overhead-management design worth studying without accepting the README's benchmark multipliers as universal results.

**Entry point:** `docs/fs_overview.md`, particularly the SEFS layering and HostFS boundary. The compatibility target is an enclave execution environment, not a complete desktop OS replacement.

### [ish-app/ish](https://github.com/ish-app/ish)

**Language/role:** C, assembly, and Objective-C; Linux userspace on iOS through x86 usermode emulation and syscall translation. The **kernel/syscall layer** is the reason for inclusion; CPU translation alone would not qualify.

Study how guest address spaces and host synchronization fit together. **C1:** [kernel/futex.c](https://github.com/ish-app/ish/blob/master/kernel/futex.c) keys futex objects by guest memory context and address, reference-counts them, and changes waiter ownership when requeueing. It separately handles guest-memory faults and value mismatches before waiting. **C2:** this guest-kernel machinery supports a Linux userspace environment rather than a single application; the repository documents loading an Alpine root filesystem and running programs within it. Its command-line testing path and register-comparison tool provide useful debugging entry points.

**Entry point:** `kernel/futex.c`, alongside the repository's command-line testing instructions. Unsupported futex operations return `ENOSYS`; do not interpret the presence of a handler as complete Linux futex compatibility. The project also candidly documents readability costs in its separate instruction interpreter.

### [linux-noah/noah](https://github.com/linux-noah/noah)

**Language/role:** C with a Perl launcher; historical Linux binaries on macOS using a hypervisor to intercept Linux syscalls and translate them to Darwin operations. **Archived in 2020.** Its README says it is experimental, missing many syscalls, and may not run on newer macOS.

Study a relatively compact virtual-kernel boundary. **C1:** [src/base.c](https://github.com/linux-noah/noah/blob/master/src/base.c) translates guest addresses, copies buffers across page boundaries, distinguishes failed string accesses, and supplies consistent Linux-style error returns for unimplemented calls. **C2:** syscall handler/name tables and shared guest-memory primitives support the different subsystem emulations rather than scattering those mechanisms across individual handlers. The [hacking guide](https://github.com/linux-noah/noah/blob/master/HACKING.md) separates VMM components from Linux subsystem emulation and explains tracing outside the guest when guest `ptrace` is unavailable.

**Entry points:** `src/base.c` and `HACKING.md`. Retained as an architectural case study, not as a currently supported way to run Linux applications on macOS.

### [proot-me/proot](https://github.com/proot-me/proot)

**Language/role:** C; a targeted Linux environment compatibility layer implementing `chroot`, bind-mount-like behavior, and executable routing in userspace. It is narrower than a foreign-kernel ABI implementation.

Study syscall interception and filesystem-view translation without a guest kernel. **C1:** [path/path.c](https://github.com/proot-me/proot/blob/master/src/path/path.c) handles bounded path construction, guest-relative executable lookup, and symlink details such as preserving the final component for script invocation. These are semantic obligations, not just string-prefix substitution. **C2:** the [official design and usage overview](https://proot-me.github.io/) explains a `ptrace`-based instrumentation engine, extension mechanism, guest/host filesystem bindings, and integration with QEMU usermode execution. It also describes CARE, an execution-archiving application of the same mechanisms.

**Entry points:** the path implementation and official overview. PRoot translates requests to the existing host kernel; its fake-root behavior should not be confused with implementing a new kernel or granting real host privileges.

## Android ABI and environment integration

### [libhybris/libhybris](https://github.com/libhybris/libhybris)

**Language/role:** C/C++; load Android/Bionic-linked libraries, especially hardware adaptation libraries, into processes using another libc such as glibc or musl.

Study binary-library compatibility below an application runtime. **C1:** the README identifies Bionic/glibc TLS conflicts, while [hybris/common/hooks.c](https://github.com/libhybris/libhybris/blob/master/hybris/common/hooks.c) shows why pthread objects cannot simply be passed through. Mutex initialization chooses ordinary allocations or shared-memory handles; condition-variable waits translate Android object representations and deal with static initialization. **C2:** a common symbol-hooking layer and version-specific linker material provide a basis for different Android driver interfaces, rather than targeting one device library.

**Entry point:** `hooks.c`, especially `_hybris_hook_pthread_mutex_init` and `_hybris_hook_pthread_cond_wait`. The code includes special handling that declines to wait for some Android-shared synchronization objects, so study its compromises as well as its abstractions. Driver availability, Android headers, and surrounding hardware-adaptation services remain relevant to whether a particular library can be used.

### [anbox/anbox](https://github.com/anbox/anbox)

**Language/role:** C++; Android container runtime and host-service bridge on GNU/Linux. **Archived and discontinued:** its README states that the existing repositories will receive no further active maintenance and points desktop users toward Waydroid.

Study the historical host-mediated hardware design. The README explains namespaces for the Android container, a host daemon handling hardware access, and reuse of Android emulator protocols for graphics. **C1:** the [RPC channel implementation](https://github.com/anbox/anbox/blob/master/src/anbox/rpc/channel.cpp) frames messages, associates invocations with pending completions, serializes writes with a mutex, and forces pending completion handling when transport failure reports disconnection. **C2:** the channel and message-sender interfaces form reusable host/guest communication machinery used within the larger Android environment, instead of exposing each application directly to host hardware.

**Entry point:** `src/anbox/rpc/channel.cpp`, read alongside the repository's architecture overview. This is distinct historical implementation material; it is not the proprietary Anbox Cloud product, and it should not be treated as maintained desktop software.

### [waydroid/waydroid](https://github.com/waydroid/waydroid)

**Language/role:** Python and shell; Android-on-Linux container and desktop integration. This repository owns substantial lifecycle and host integration logic; it does not contain the whole Android operating system image.

Study the boundary between an Android environment and a Linux login session. **C1:** the D-Bus `Start` method checks the caller's UID and PID against the requested session. Container startup rejects duplicate sessions and coordinates drivers, network setup, image mounts, protocol selection, and LXC state. Shutdown coordinates hardware services, container termination, unmounts, and session notification. **C2:** separate actions, helpers, services, and a D-Bus manager expose reusable lifecycle operations over that state. These mechanisms are visible in [container_manager.py](https://github.com/waydroid/waydroid/blob/main/tools/actions/container_manager.py).

**Entry point:** `DbusContainerManager`, `do_start`, and `stop`. The repository describes direct access to needed hardware, making this a different integration design from Anbox's mediated hardware path. It is included for environment compatibility engineering, not characterized as syscall-by-syscall emulation.

## Portable POSIX runtimes and focused interface shims

### [jart/cosmopolitan](https://github.com/jart/cosmopolitan)

**Language/role:** C and assembly; a portable libc/runtime and executable strategy spanning Windows and multiple Unix-family systems. This is compatibility for software built with its toolchain, not a loader for arbitrary foreign executables.

Study one application interface backed by different OS implementations. **C1:** [libc/proc/fork.c](https://github.com/jart/cosmopolitan/blob/master/libc/proc/fork.c) documents an explicit lock order and coordinates standard I/O, allocation, descriptors, mappings, randomness, and thread state across parent and child. Child-side lock reset is essential when only the calling thread survives. **C2:** the common runtime interface contains platform-dependent behavior, including Windows-specific process and signal bookkeeping, so applications can share a POSIX-facing programming model. The repository also documents focused POSIX test targets and syscall/function tracing.

**Entry point:** `fork_prepare`, `fork_parent`, and `fork_child` in `fork.c`. This file exposes the interactions among runtime subsystems more clearly than a list of supported operating systems would.

### [mheily/libkqueue](https://github.com/mheily/libkqueue)

**Language/role:** C; userspace implementation of the BSD `kqueue`/`kevent` event interface on other operating systems.

Study a narrow API with substantial concurrency obligations. **C1:** [src/common/kevent.c](https://github.com/mheily/libkqueue/blob/master/src/common/kevent.c) handles event registration and modification, receipts, filter state, and cancellation. It explains why waiting must release the queue mutex for cross-thread wakeups while backend tracking prevents returning into a freed queue. It also documents a remaining registration/disable race, useful evidence of semantic difficulty rather than a reason to assume perfection. **C2:** common knote/filter lifecycle logic delegates platform operations through backend interfaces. **C3:** the README explicitly discusses global-lock contention and the cost of fork cleanup, exposing correctness/performance choices through configuration.

**Entry point:** the common `kevent` path. The repository documents running its tests against native BSD/macOS kqueue behavior and enabling sanitizers, making it a useful study in differential compatibility testing.

### [jiixyj/epoll-shim](https://github.com/jiixyj/epoll-shim)

**Language/role:** C; Linux `epoll` and related descriptor APIs implemented using kqueue, used to port software such as libinput, libevdev, and Wayland. The repository is unarchived, but its last recorded push at this research date was in December 2024; no claim of current active development is made.

Study the distinction between file descriptors and shared file descriptions. **C1:** [epoll_shim_ctx.c](https://github.com/jiixyj/epoll-shim/blob/master/src/epoll_shim_ctx.c) uses reference counts, atomic memory ordering, mutexes, and virtual operations for close/read/write/poll behavior. **C2:** that common machinery supports multiple Linux-style descriptor types. **C3:** the README explains lower-overhead macro wrapping versus broader symbol interposition. **C4:** its dated 2020–2024 changelog records semantic fixes, new host support, reference-counting improvements, and changing lookup structures, alongside tests runnable against Linux's behavior. See the [repository documentation and changelog](https://github.com/jiixyj/epoll-shim#changelog).

**Entry points:** the descriptor context implementation and changelog. Documented limitations include interprocess sharing of shimmed descriptors and some edge-triggered behavior for poll-only devices.

## Coverage, search method, and limitations

Discovery used more than six distinct live-search formulations, covering Windows/macOS API emulation; Linux ABI implementations in BSD and illumos; Cygwin and MSYS2 provenance; Linux-on-macOS and Linux-on-iOS execution; SGX library operating systems; Android containers and Bionic bridging; kqueue/epoll translations; and less-common OS/2 personalities and Rust compatibility projects. Later OS/2, historical Windows/POSIX, and broad Rust queries mostly returned incomplete projects, unrelated portability code, or whole-kernel projects outside the chosen focus, yielding diminishing additions to this selection.

Every retained repository was opened or checked through GitHub's API, and at least one separate implementation or design source was read for each. Some documentation sites and indexed raw-file URLs failed through the web reader; the corresponding public GitHub source was read directly where needed. No candidate repository was cloned, built, or executed. Compatibility and performance claims here are documentary/code observations, not independently reproduced benchmarks.

The selection deliberately excludes launchers around another compatibility layer, ordinary cross-platform utility libraries, graphics-only API translators, and full-machine virtualization projects. CPU emulation appears only where a substantial OS-interface implementation is also examined. It does not claim comprehensive coverage of OS/2, legacy commercial Unix personalities, or Windows driver-API emulation. Proton and MSYS2 are retained because their distinct integration and interoperation implementations are identified; additional Wine/Cygwin repackagings are not counted. FreeBSD, NetBSD, and illumos-derived monorepos each count once.

The collection is strongest for C and C++ systems, reflecting the selected implementations, with Go, Rust, Python, Objective-C, and assembly represented where they serve a substantive role. Historical projects and documented semantic gaps are retained when they offer a clear engineering comparison. The criteria describe what an experienced engineer can investigate, not a claim that every component in these repositories is uniformly exemplary.
