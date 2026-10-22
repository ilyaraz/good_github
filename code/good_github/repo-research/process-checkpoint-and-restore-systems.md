# Process checkpoint and restore systems

Research date: **2026-10-09**.

This selection covers systems that preserve and resume an executing process or process group: native Linux engines, distributed MPI and GPU extensions, container runtime integration, checkpoint transport and coordination, JVM lifecycle support, and portable WebAssembly execution. Container projects are included only for their substantive process checkpoint/restore subsystems. Filesystem backups, VM-only snapshots, model-weight checkpoints, and application data persistence alone are outside scope.

The 16 repositories below are study targets, not interchangeable deployment recommendations. Criteria are engineering judgments grounded in the linked primary material; they do not imply that every component is exemplary or every workload is supported. Repository identity and archive status were checked through GitHub pages and the GitHub API. None was marked archived at inspection; historical implementations are identified separately. Recent activity alone is not counted as maturity evidence.

## Criteria legend

- **C1 — Correctness:** difficult invariants, concurrency, resource identity, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or mechanisms that serve multiple workloads or integrations.
- **C3 — Performance and structure:** concrete runtime, transfer, memory, or latency constraints addressed through an understandable design.
- **C4 — Sustained evolution:** years of change accompanied by compatibility work, testing, or deliberate complexity management.

## Native and distributed checkpoint engines

### 1. [checkpoint-restore/criu](https://github.com/checkpoint-restore/criu)

**Language/role:** C, assembly, and Python; native Linux process-tree checkpoint/restore engine.

CRIU is the central codebase for studying how userspace reconstructs kernel-visible process state. Its checkpoint path combines `/proc` inspection, `ptrace`, and injected code; restoration rebuilds resource sharing and the process hierarchy before transferring execution through a small restorer image.

- **C1:** Shared descriptors, memory, namespaces, credentials, timers, and thread state must be recreated in a valid order. The restorer must occupy memory that conflicts with neither CRIU nor the target, then restore registers through `sigreturn`. The [checkpoint/restore architecture](https://github.com/checkpoint-restore/criu/blob/criu-dev/Documentation/under-the-hood/checkpointrestore.md) explains these dependencies concretely.
- **C2:** The same engine supports process and container workflows. Its repository also exposes Compel for code injection and libsoccr for TCP socket state, demonstrating reusable mechanisms beneath the command-line interface. These are subsystems of this single repository, not separate entries. See the [repository's library overview](https://github.com/checkpoint-restore/criu#advanced-features).

### 2. [dmtcp/dmtcp](https://github.com/dmtcp/dmtcp)

**Language/role:** C++ and C; transparent checkpointing of multithreaded and distributed Linux applications.

DMTCP provides a contrasting architecture: application-library interposition and a computation coordinator, without a kernel module. The [quick-start design explanation](https://github.com/dmtcp/dmtcp/blob/main/QUICK-START.md) describes tracking threads, forked children, remotely launched processes, and loaded libraries under one computation.

- **C1:** Checkpoint callbacks distinguish a phase in which user threads still run from one in which they are suspended. Virtual identifiers remain stable while their real resources change on restart; both details are explained in [NEWS](https://github.com/dmtcp/dmtcp/blob/main/NEWS).
- **C2:** Plugin lifecycle events and identifier translation let applications and extensions add resource-specific handling, as demonstrated by MANA's separate implementation.
- **C4:** The release history documents evolution from older multiarchitecture and MPI compatibility fixes through 2023 plugin changes and 2024–2026 thread, compiler, and glibc fixes. It explicitly records the incompatible checkpoint-image format introduced in 4.0.0, rather than promising universal image compatibility. This is useful compatibility-management evidence, not merely project age.

### 3. [mpickpt/mana](https://github.com/mpickpt/mana)

**Language/role:** C++ and C; DMTCP extension for transparent MPI checkpoint/restart.

MANA separates application memory from an MPI-library “lower half” inside one process. It saves the application portion and rebuilds the MPI side on restart. The [NERSC architecture explanation](https://docs.nersc.gov/development/checkpoint-restart/mana/) is useful for this split; its operational instructions and older collective algorithm should be read alongside the newer upstream changelog.

- **C1:** MPI requests and messages cannot simply disappear across a checkpoint. The [1.5.0 changelog](https://github.com/mpickpt/mana/blob/main/CHANGELOG.md) documents rewritten point-to-point draining, prevention of message loss/reordering, and completion of pending nonblocking collectives.
- **C2:** Separating application state from MPI implementation state reduces dependence on particular MPI libraries and interconnects; current changes include an upper-half stub supporting MPICH-ABI applications.
- **C4:** The changelog traces the 2019 prototype's later architectural rewrite, 2024–2026 releases, platform testing, a yanked release, and checkpoint/restart tests run in pull-request CI. It also records a remaining OFI-provider restart hang, so coverage should not be generalized to every MPI configuration.

### 4. [DMTCP-CRAC/CRAC-early-development](https://github.com/DMTCP-CRAC/CRAC-early-development)

**Language/role:** C++/C and CUDA; historical GPU checkpointing research implementation derived from DMTCP. Unrelated to Java CRaC below.

Retain this for its substantive CUDA-specific implementation, not as another copy of DMTCP. The [split-CUDA subtree](https://github.com/DMTCP-CRAC/CRAC-early-development/tree/master/contrib/split-cuda) separates upper/lower halves, generated wrappers, and log/replay machinery. The authors' [CRAC paper, sections 3.1–3.2](https://arxiv.org/html/2008.10596) supplies the architectural rationale.

- **C1:** CUDA-managed allocations and pointers must remain meaningful after the CUDA runtime is recreated. The design must distinguish library-owned mappings from application memory while handling streams and unified memory.
- **C3:** Putting the application and helper in one address space avoids the interprocess marshaling costs of a separate GPU proxy. The paper explains the resulting loading and allocation tradeoffs; no benchmark number is assumed portable to other workloads.

**Status limitation:** [GitHub repository metadata](https://api.github.com/repos/DMTCP-CRAC/CRAC-early-development) reports the last push in December 2023. The README explicitly says the general-purpose port is unfinished and identifies a Gromacs problem in this version. Study it as a historical research artifact, not current CUDA compatibility guidance.

## Container runtimes with substantive restore machinery

### 5. [google/gvisor](https://github.com/google/gvisor)

**Language/role:** Primarily Go; checkpointing in the Sentry application kernel and `runsc` runtime.

gVisor is an independent architectural family: it can save state represented by its own application kernel. Study the interaction between object-graph serialization and restoring application execution, rather than treating the whole sandbox project as checkpoint-specific.

- **C1:** Its [state encoding design](https://github.com/google/gvisor/blob/master/pkg/state/README.md) preserves cycles, intrusive pointers, and pointers into other objects. It resolves order-dependent load callbacks and detects dependency cycles—problems ordinary tree-shaped serialization cannot solve.
- **C3:** The [checkpoint/restore guide](https://gvisor.dev/docs/user_guide/checkpoint_restore/) explains background loading that prioritizes pages needed by running threads, direct I/O, and the tradeoff between compression and parallel kernel/memory restoration.
- **C2:** The state package separates graph discovery, type encoding, wire objects, and reconstruction, making the mechanism comprehensible across many kernel resource types.

The guide also distinguishes sandbox networking from host-network sockets that cannot retain established connections across restore.

### 6. [opencontainers/runc](https://github.com/opencontainers/runc)

**Language/role:** Go; OCI container runtime, specifically `libcontainer` checkpoint/restore integration with CRIU.

runc is valuable for the boundary between a process-state engine and a container lifecycle. Its [CRIU integration](https://raw.githubusercontent.com/opencontainers/runc/main/libcontainer/criu_linux.go) translates OCI configuration into checkpoint options and prepares the environment that restored processes expect.

- **C1:** External network/PID namespaces require matching keys and inherited descriptors on restore. Mountpoint reconstruction must respect nested bind mounts and avoid duplicating tmpfs contents that CRIU restores itself. Feature/version checks prevent unsupported combinations from proceeding blindly.
- **C2:** Container-level options expose iterative pre-dumps, page servers, lazy pages, external resources, and cgroup handling through one lifecycle implementation reusable by higher-level container systems.

The [checkpoint integration tests](https://github.com/opencontainers/runc/blob/main/tests/integration/checkpoint.bats) exercise repeated checkpoint/restore and usable standard-I/O pipes after restoration. This offers a concrete way to study observable correctness, without assigning a maturity criterion merely because runc is well known.

### 7. [containers/crun](https://github.com/containers/crun)

**Language/role:** C; OCI runtime and embeddable runtime library, including a distinct CRIU integration.

crun provides a useful comparison with runc's Go implementation. Its [checkpoint/restore implementation](https://raw.githubusercontent.com/containers/crun/main/src/libcrun/criu.c) makes explicit the interface between libcrun container state, dynamically available libcriu capabilities, mount setup, and error cleanup.

- **C1:** Restore must recreate missing mountpoints, join shared namespaces, and place newly created tasks in the correct cgroup. The code explains why relocating every hierarchy on a cgroup-v2 system could recursively copy a named v1 hierarchy on successive restores. Cleanup also restores the runtime's original cgroup membership after creating the child.
- **C2:** The libcrun/libcriu boundary translates a common OCI configuration and checkpoint options into reusable native operations. Optional CRIU functions and namespace-version requirements are handled at this boundary rather than being scattered into individual workloads.

This entry concerns the C/R subsystem; the runtime's general speed reputation is not used as performance evidence.

## Checkpoint orchestration, transport, and migration

### 8. [cedana/cedana](https://github.com/cedana/cedana)

**Language/role:** Go; process/container checkpoint daemon and orchestration layer above CRIU.

Cedana is useful for studying how checkpointing becomes an extensible service. The [architecture guide](https://github.com/cedana/cedana/blob/main/docs/developer-guides/architecture.md) follows a concrete `dump runc` request through the CLI, daemon, runtime plugin, and CRIU.

- **C2:** Typed plugin features provide runtime-specific commands and middleware, while common code handles defaults, storage, and execution. The same pattern applies to dump, restore, run, and management operations, allowing multiple process/container integrations.
- **C1:** Middleware order is semantically important: validation and runtime adaptation precede process-state collection, external-file and network detection, GPU handling, saved metadata, and final CRIU option checks. This is substantive orchestration of mutually dependent state, not merely a generated RPC wrapper.

The [daemon guide](https://github.com/cedana/cedana/tree/main/docs) distinguishes independently usable daemon functionality from the larger managed Cedana offering. GPU and storage behavior depends on the available plugins; the public daemon should not be equated with every commercial-system capability.

### 9. [laravel/zeropod](https://github.com/laravel/zeropod)

**Language/role:** Go with eBPF components; containerd shim that checkpoints idle containers and restores them on demand.

The canonical repository is now `laravel/zeropod`; the former `ctrox/zeropod` URL redirects here. Its [activation design](https://github.com/laravel/zeropod#how-it-works) links checkpointing to incoming TCP traffic: an activator handles wakeup while the shim maintains a lifecycle view compatible with the surrounding runtime.

- **C1:** Checkpoint and restore can race with traffic, timers, process exits, and migration cleanup. The [container implementation](https://github.com/laravel/zeropod/blob/main/shim/container.go) includes a checkpoint/restore mutex, tracked checkpointed PIDs, retry state, and explicit handling of already-restored or failed restores.
- **C3:** Idle-state persistence releases application memory; the activation architecture forwards initial connections and lets subsequent connections take the ordinary path. Activity tracking delays another checkpoint to reduce repeated freeze/thaw cycles.

This is a substantive policy and lifecycle system over CRIU. The README labels live migration experimental; activation behavior and compatibility should be assessed for the specific workload.

### 10. [twosigma/fastfreeze](https://github.com/twosigma/fastfreeze)

**Language/role:** Rust; historical integrated checkpoint/restore pipeline for applications inside Linux containers.

FastFreeze combines CRIU, filesystem capture, compression, image sharding, storage commands, and time/CPU adaptation into a recoverable job workflow. Its main study value is the coordination code surrounding the checkpoint engine.

- **C1:** The [checkpoint implementation](https://github.com/twosigma/fastfreeze/blob/master/src/cli/checkpoint.rs) waits until the application is stopped before archiving its files. It monitors helper failures and distinguishes a failed CRIU dump from a later upload failure when deciding whether the application can safely resume.
- **C3:** Streaming shard pipelines overlap capture, compression, and upload; a CPU budget selects compression policy. The [streamer integration](https://github.com/twosigma/fastfreeze/blob/master/src/image_streamer.rs) exposes explicit readiness/progress messages and separate filesystem and shard pipes.

**Status limitation:** [GitHub repository metadata](https://api.github.com/repos/twosigma/fastfreeze) reports the last push in December 2021. The README limits the implementation to its documented container/glibc environment and says network connections are dropped on restore. Its custom CRIU assumptions and dependencies make it a historical architecture reference, not an assertion of current-host support.

### 11. [checkpoint-restore/go-criu](https://github.com/checkpoint-restore/go-criu)

**Language/role:** Go; CRIU integration library, retained particularly for its PHaul migration subsystem.

This entry is justified by handwritten migration control, not generated protobuf bindings. The [PHaul client](https://raw.githubusercontent.com/checkpoint-restore/go-criu/master/phaul/client.go) implements iterative pre-copy and a final dump/copy/restore handoff.

- **C3:** Iteration stops when the remaining dump is small, progress worsens, or an iteration cap is reached. The implementation uses actual dump statistics rather than assuming pre-copy always converges.
- **C1:** The [local/remote interface contract](https://raw.githubusercontent.com/checkpoint-restore/go-criu/master/phaul/api.go) specifies the frozen interval and distinguishes successful migration, which kills the source tree, from failure, which resumes it. Parent-image and memory-tracking requirements are explicit.
- **C2:** Local final-handoff behavior is separated from remote iteration control and the page-transfer descriptor, making the algorithm usable within different migration transports and container integrations.

The older Python `p.haul` project is not counted separately here.

### 12. [checkpoint-restore/criu-image-streamer](https://github.com/checkpoint-restore/criu-image-streamer)

**Language/role:** Rust; checkpoint-image streaming, sharding, and reconstruction component.

This is supporting infrastructure rather than an independent process-state engine. Its [capture implementation](https://raw.githubusercontent.com/checkpoint-restore/criu-image-streamer/master/src/capture.rs) is a compact study in preserving image semantics while optimizing pipe-based transfers.

- **C3:** It uses `splice()` to avoid userspace copies and selects output shards according to available pipe capacity. A heap tracks capacity so a slow shard does not dictate round-robin throughput; chunk size balances serialization cost and blocking.
- **C1:** Nondeterministic shard placement requires sequence markers to reconstruct the stream. Progress notifications also distinguish socket readiness from the point at which the application is stopped, which matters when filesystem capture runs beside memory capture.
- **C2:** UNIX-pipe interfaces permit composition with compression, encryption, and remote upload tools. The [protocol and synchronization guide](https://github.com/checkpoint-restore/criu-image-streamer#synchronization) describes the integration boundary.

The documented implementation does not support incremental checkpoints. Its performance techniques should be studied separately from workload-specific throughput claims.

### 13. [checkpoint-restore/criu-coordinator](https://github.com/checkpoint-restore/criu-coordinator)

**Language/role:** Rust; coordination of CRIU operations across dependent processes, containers, or Kubernetes pods.

This smaller project fills a different gap from image transport: several individually valid process checkpoints may still form an invalid distributed snapshot. Its [server implementation](https://github.com/checkpoint-restore/criu-coordinator/blob/main/src/server.rs) makes the coordination protocol visible through client status and dependency maps.

- **C1:** Network-lock, network-unlock, and post-dump handling wait for corresponding dependency states. Mutexes, condition variables, timeout budgets, and explicit response messages govern concurrent arrivals and stalled participants.
- **C2:** The [CRIU action-script integration](https://github.com/checkpoint-restore/criu-coordinator#usage-example) connects the protocol to existing engines and orchestration levels without embedding one application-specific checkpoint algorithm.

Study the assumptions as closely as the synchronization: the inspected post-dump code treats a missing dependency as potentially already completed. This selection does not establish consensus, durable coordinator recovery, or correctness under arbitrary network partitions. Those are boundaries to investigate, not guarantees inferred from the project's description.

## JVM coordination and portable execution

### 14. [openjdk/crac](https://github.com/openjdk/crac)

**Language/role:** Java and C++; OpenJDK development repository for Coordinated Restore at Checkpoint.

The relevant subsystem is Java/JVM coordination around an underlying snapshot engine. An already initialized JVM can resume from a checkpoint, but files, sockets, and environment-dependent resources require lifecycle handling. The [project documentation](https://github.com/CRaC/docs#crac) explains why raw process capture is insufficient.

- **C1:** Checkpoint preparation must release or reconcile resources that cannot safely survive restoration; failure during checkpoint and failure after restore are distinct execution outcomes. The project documents checkpoint rejection when the instance cannot be safely captured.
- **C2:** The [Context implementation/API](https://github.com/openjdk/crac/blob/crac/src/jdk.crac/share/classes/jdk/crac/Context.java) treats contexts as resources and distributes before-checkpoint/after-restore notifications through a hierarchy. This supports libraries and frameworks without tying each to a particular snapshot engine.

The repository's current README says Linux uses CRIU and that maintenance of its former custom CRIU fork has stopped. Count this JDK repository once; documentation, example applications, and that legacy fork are not additional systems.

### 15. [eclipse-openj9/openj9](https://github.com/eclipse-openj9/openj9)

**Language/role:** Java, C++, and C; OpenJ9's CRIU API and VM checkpoint/restore support.

OpenJ9 provides a separately implemented JVM integration with useful controls for adaptation at restore. Focus on `openj9.criu` and VM support rather than the entire JIT/compiler codebase.

- **C1:** The [CRIUSupport API source](https://github.com/eclipse-openj9/openj9/blob/main/jcl/src/openj9.criu/share/classes/org/eclipse/openj9/criu/CRIUSupport.java) distinguishes concurrent hooks from hooks where only the checkpoint-requesting Java thread runs. The latter permit global changes but can deadlock if they acquire resources held by suspended threads.
- **C2:** Restore-time environment and VM-option registration, checkpoint hooks, and explicit checkpoint capability checks give applications reusable lifecycle controls. The [CRIU support guide](https://eclipse.dev/openj9/docs/criusupport/) also explains checkpoint/restore security-provider handling.
- **C3:** The same guide describes reducing checkpoint-phase GC threads to lower restore work, and distinguishes portable compiled code from nonportable restore behavior.

The guide labels the feature a technical preview with specific container-image/platform support and changeable APIs. Those stated limits matter more than generic JVM maturity.

### 16. [oss-fun/chiwawa](https://github.com/oss-fun/chiwawa)

**Language/role:** Rust compiled to WebAssembly; research runtime for portable execution-state checkpointing.

Chiwawa runs a Wasm interpreter inside Wasm, making guest execution state explicit rather than depending on a particular host runtime's native stack. This is a bounded virtual-process alternative to saving arbitrary operating-system processes.

- **C1:** The [migration design](https://github.com/oss-fun/chiwawa/blob/main/doc/migration.md) captures per-thread frames, registers, globals, shared memory, and thread-ID allocation state. Its stop protocol handles running threads and atomic waiters, including preservation of already-counted notification permits.
- **C3:** A monitor can replace instruction handlers with checkpoint traps, avoiding per-instruction polling in that mode. A fallback amortizes filesystem trigger checks when host threads are unavailable; serialization excludes host pointers and reconstructs pointer-dependent runtime state.
- **C2:** Explicit guest state allows the checkpoint mechanism to cross host runtimes and execution strategies; the [dispatcher/build overview](https://github.com/oss-fun/chiwawa#dispatcher-modes) describes the host-feature alternatives.

**Research limitation:** The design explicitly omits tables and WASI state, so it is incorrect for guests relying on those restored resources. A thread blocked indefinitely inside a WASI call can also prevent checkpoint completion. This is not a general replacement for native process restoration.

## Search coverage and limitations

Discovery used more than six distinct live-web search formulations, covering native process-tree restoration; MPI/BLCR/HPC checkpointing; Rust/Go orchestration; JVM CRaC/OpenJ9; CUDA/UVM and proxy versus split-process designs; WebAssembly live migration; OCI runtimes and gVisor; checkpoint streaming and migration; and FreeBSD/OpenVZ/Windows alternatives. Follow-up searches and repository browsing increasingly returned the same engines, integration layers, examples, or out-of-scope snapshot tools. Primary evidence was then read through GitHub pages, public GitHub API/file reads, project documentation, release histories, and the CUDA CRAC authors' paper.

The resulting selection is intentionally Linux-heavy: that is where this search found the strongest verifiable GitHub implementations of native process restoration. JVM and Wasm entries broaden the execution model, while Rust transport/coordination and C/Go OCI implementations broaden the engineering scale. No native Windows or FreeBSD system was retained on insufficient evidence. BLCR and several older GPU projects were investigated but not promoted without a verified official substantive GitHub repository and adequate implementation evidence.

Excluded groups include ordinary CRIU invocation scripts, tutorials, generated-only bindings, checkpoint inspection tools without restoration machinery, and application-managed data libraries such as SCR/FTI/VELOC for this particular process-state scope. NVIDIA's `cuda-checkpoint` distribution is relevant integration context, but was not selected as a comparable source-code study of the driver implementation. VM-only snapshot engines and filesystem/system-restore tools were also excluded. CRIU's Compel/libsoccr, runc's libcontainer, gVisor's state package, and each JVM's checkpoint support are counted within their parent repositories. The CUDA CRAC derivative is retained specifically for its separately implemented GPU architecture; ordinary forks are not counted.

No candidate was cloned, built, or executed, and no performance figures were independently reproduced. Primary sources sometimes describe different revisions: upstream MANA's dated changelog, for example, supersedes parts of older deployment documentation. Historical status and compatibility limits are made explicit rather than inferred from stars or repository age.
