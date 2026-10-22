# Remote build execution and build caching systems

Research date: **2026-10-09**.

This selection covers 23 GitHub repositories implementing remote build workers and schedulers, content-addressed build storage, distributed compilation, reusable task caches, and binary substitution. Build-tool monorepos are included only for their relevant execution or caching subsystems. The scope includes both services and the clients that must preserve build semantics while using them; it excludes general CI orchestration and generic object stores without substantial build-specific machinery.

The criteria below describe concrete reasons to study a repository, not a score for every component or a deployment recommendation. Repository pages and additional primary documentation or implementation files were opened for every selection. No candidate code was executed, and no performance measurements were independently reproduced.

- **C1 — Difficult correctness:** invariants, concurrency, input identity, adversarial or malformed inputs, cancellation, and failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces or models that support different tools, backends, platforms, or workloads.
- **C3 — Performance with structure:** explicit treatment of latency, I/O, memory, contention, or scheduling through understandable architecture.
- **C4 — Sustained evolution:** years of documented change together with evidence of compatibility work, testing, or complexity management. Age and recent commits alone do not qualify.

In the descriptions, **REAPI** means the Remote Execution API, **CAS** means content-addressable storage, and **AC** means an action cache mapping an action identity to its result and output digests. The linked implementation and documentation files are suggested study entry points. Most links track a development branch or current documentation and can change after the research date.

## Remote execution services and shared content stores

### [buildbarn/bb-storage](https://github.com/buildbarn/bb-storage)

**Go — REAPI storage service and composable blob-storage infrastructure.** This is the storage half of Buildbarn; it is useful for studying how a build cache differs from a simple key/value server. Its configuration schema documents the semantics of storage decorators and the underlying block allocator in considerable detail.

- **C1:** An AC completeness-checking layer verifies that referenced output blobs still exist before returning a cached result. This addresses independently evicted metadata and content. The local store also has explicit constraints on block reuse and action-cache updates.
- **C2:** A common blob-access model composes sharding, mirroring, read caching, existence caching, and completeness checks. The documentation exposes the assumptions of each composition rather than treating them as interchangeable reliability features.
- **C3:** Old/current/new block generations, refresh-on-read, and probabilistic placement spread storage work while reclaiming space. Study these mechanisms alongside weighted rendezvous sharding in the [blob-store configuration and design comments](https://raw.githubusercontent.com/buildbarn/bb-storage/main/pkg/proto/configuration/blobstore/blobstore.proto).

### [buildbarn/bb-remote-execution](https://github.com/buildbarn/bb-remote-execution)

**Go — Buildbarn scheduler, workers, and execution runners.** This is a complementary implementation repository, not a second copy of bb-storage. The scheduler queues work, the worker stages inputs and collects outputs, and a separate runner actually invokes the command.

- **C1:** The worker/runner boundary addresses corruption of cached inputs that are hard-linked into execution directories and permits privilege separation. The repository also explains the UNIX executable-write/fork race motivating separate execution responsibilities.
- **C2:** The runner is a gRPC abstraction with readiness checks and a run request specifying directories, environment, output streams, and resource reporting. A different execution environment can implement that boundary without replacing storage and scheduling.
- **C3:** Reuse of cached input files reduces staging work, while the isolation boundary makes the associated correctness obligations visible. Read the repository's architecture discussion and the [runner protocol](https://github.com/buildbarn/bb-remote-execution/blob/main/pkg/proto/runner/runner.proto) together.

### [buildfarm/buildfarm](https://github.com/buildfarm/buildfarm)

**Java — Distributed REAPI execution and caching cluster.** Buildfarm is particularly useful for studying the operational state surrounding execution: shared queues, worker discovery, leases, and the relationship between result metadata and distributed content. The canonical repository is now under `buildfarm`, rather than its former `bazelbuild` location.

- **C1:** Its dispatched-operation monitor requeues work when worker leases expire, with bounded requeue attempts. The optional output-presence check turns an AC entry whose content is missing into a cache miss.
- **C3:** Action-digest operation merging avoids duplicate execution; queue-depth limits bound admitted work. The Redis backplane tracks shared state and CAS locations, while local metadata caches have explicit capacity implications.

The [configuration reference](https://buildfarm.github.io/buildfarm/docs/configuration/configuration/) is the substantive entry point: it describes these failure and capacity controls. The [quick start](https://buildfarm.github.io/buildfarm/docs/quick_start/) connects them to the server, worker, and backplane deployment roles.

### [buildbuddy-io/buildbuddy](https://github.com/buildbuddy-io/buildbuddy)

**Go and TypeScript — Build cache, remote executors, and build-result tooling.** Focus on the executor runner pool and workspace lifecycle rather than the monorepo's UI. The runner code provides a detailed case study in retaining expensive execution environments between otherwise isolated actions.

- **C1:** Recycled workspaces require output cleanup before the next task. A failed virtual-filesystem input download can override an apparently successful command result, preventing missing-input behavior from being accepted as a valid build. Some failure states mark a runner unsuitable for reuse.
- **C3:** Container/workspace reuse, persistent workers, and pool memory/disk accounting balance startup savings against resource limits and contamination risk. These policies are visible in [the runner implementation](https://github.com/buildbuddy-io/buildbuddy/blob/master/enterprise/server/remote_execution/runner/runner.go).

**License scope:** the studied execution code is in the enterprise subtree and has a [separate Enterprise License](https://github.com/buildbuddy-io/buildbuddy/blob/master/enterprise/LICENSE), including production-use restrictions. Do not infer its terms from the core repository's MIT license.

### [TraceMachina/nativelink](https://github.com/TraceMachina/nativelink)

**Rust — REAPI cache and remote execution service.** NativeLink supplies a useful Rust perspective on asynchronous storage composition. The fast/slow store is an especially focused subsystem to inspect before exploring the wider scheduler and worker implementation.

- **C1:** Concurrent requests for the same digest coordinate through shared initialization state. Cancellation cleanup prevents abandoned population attempts from leaving misleading in-flight state. Upload tracking also affects existence checks while writes are still progressing.
- **C2:** Fast and slow stores share a storage abstraction, allowing a local fast tier to front another backend.
- **C3:** Coordinated population avoids repeated slow-backend transfers; size-dependent bypass behavior exposes the tradeoff between caching large objects and serving them directly. These mechanisms are implemented in [fast_slow_store.rs](https://raw.githubusercontent.com/TraceMachina/nativelink/main/nativelink-store/src/fast_slow_store.rs).

**License scope:** the current [license](https://github.com/TraceMachina/nativelink/blob/main/LICENSE) is FSL-1.1-Apache-2.0 with restrictions on competing use and a later Apache conversion. This is a source-study selection, not a claim that the current version is under an unrestricted open-source license.

### [buchgr/bazel-remote](https://github.com/buchgr/bazel-remote)

**Go — Bounded disk cache with HTTP/gRPC service and remote-storage proxies.** Compared with a full executor cluster, this repository offers a more concentrated view of the cache write path and the engineering required to keep it bounded and trustworthy.

- **C1:** Writes validate digest and size, reserve capacity before committing, and use temporary storage with cleanup on failure. Compressed and uncompressed representations must preserve the same content identity. Deferred cleanup also releases reservations when a write does not complete.
- **C3:** A semaphore limits blocking filesystem operations, and the disk LRU and reservation accounting coordinate concurrent writes against the capacity budget. Proxy storage can extend the deployment without changing the basic cache interface.

Start with [cache/disk/disk.go](https://raw.githubusercontent.com/buchgr/bazel-remote/master/cache/disk/disk.go), especially the write path and its lock/reservation boundaries. The repository documentation supplies the server and proxy configuration context.

## Compiler caches and distributed compilation

### [mozilla/sccache](https://github.com/mozilla/sccache)

**Rust — Compiler-result cache and distributed compilation client/server.** Sccache is valuable for studying how multiple compilers and storage backends fit behind a compiler-wrapper interface. Its long-lived service, short-lived invocations, and alternative client-side execution path expose different state-sharing choices.

- **C1:** Direct-mode reuse depends on validating the recorded included-file hashes. If those dependencies cannot establish a hit, the normal preprocessing path remains necessary; a command-line match alone is insufficient.
- **C2:** Storage implementations share a trait, including an IPC-backed implementation that lets different process arrangements reuse the compilation pipeline.
- **C3:** Retaining service state and avoiding repeated preprocessing on valid direct hits attack costs that can dominate small compilations. The [architecture document](https://raw.githubusercontent.com/mozilla/sccache/main/docs/Architecture.md) explains these paths and their boundaries; the repository documentation identifies the distributed toolchain-packaging and worker roles.

### [ccache/ccache](https://github.com/ccache/ccache)

**C++ — Compiler cache with shared/remote storage support.** Ccache is a strong study of the boundary between a compiler's observable semantics and a reusable cache key. Its documentation is unusually candid about cases that require bypassing optimizations.

- **C1:** Direct-mode manifests record included-file hashes, while timestamp checks guard against source/header modification races. Path rewriting, newly appearing headers, and compiler-produced auxiliary files complicate safe reuse.
- **C3:** Direct, preprocessor, and depend modes exchange different amounts of preprocessing and dependency work for hit opportunities. The [manual](https://ccache.dev/manual/latest.html) explains those tradeoffs and remote storage mechanisms.
- **C4:** The [release notes](https://ccache.dev/releasenotes.html) document compiler/path regressions and test fixes in 2016, and storage-helper compatibility, C++ module hashing, and Windows remote-cache tests in 2026. This is evidence of sustained semantic and compatibility maintenance, not merely repository age. Remote-backend interfaces are evolving, so consult the version-specific notes before copying configuration.

### [distcc/distcc](https://github.com/distcc/distcc)

**C, with a Python include server — Distributed C/C++ compilation.** The useful distinction here is between ordinary distcc, which distributes compilation after preprocessing, and pump mode, which also moves preprocessing to remote machines.

- **C1:** Pump mode must compute a sufficient transitive set of headers and preserve path meaning across machines. Include arguments, preprocessor line information, and returned dependency/object paths require coordinated rewriting.
- **C3:** A persistent include server reuses dependency analysis, and source/header compression is reused across transfers. Moving preprocessing removes a client-side bottleneck but introduces a more demanding input-discovery problem.

The [pump design explanation](https://raw.githubusercontent.com/distcc/distcc/master/README.pump) describes the include-graph analysis and path transformations. This makes distcc worth studying alongside cache systems even though its central function is distributing work rather than retaining build results.

### [icecc/icecream](https://github.com/icecc/icecream)

**C++ — Distributed compilation with a central scheduler and packaged compiler environments.** Icecream shares historical lineage with distcc, but its separate scheduler and environment-distribution design make it a substantive independent implementation rather than a duplicate entry.

- **C1:** The scheduler explicitly accounts for different arrival orders of client termination and worker completion messages. Disconnect cleanup must remove a client's jobs from every tracking structure. Packaged compiler environments address the separate problem of matching toolchains across workers.
- **C3:** Server selection considers occupancy and estimated speed; the code includes alternative selection policies and smoothing of observed job statistics. This is a useful example of scheduling heterogeneous workers using imperfect measurements.

Read [scheduler/scheduler.cpp](https://github.com/icecc/icecream/blob/master/scheduler/scheduler.cpp), particularly its message-flow comments, cleanup logic, and server-selection functions. The repository's environment documentation explains the compiler-package side of the design.

### [fastbuild/fastbuild](https://github.com/fastbuild/fastbuild)

**C++ — Build system with integrated distributed compilation and object caching.** FASTBuild adds a different community and deployment model: network-discovered workers and cache directories integrated directly into a native build engine, including substantial Windows/MSVC considerations.

- **C1:** Distribution is bypassed for compiler modes whose extra outputs or path semantics cannot be safely handled. Compiler toolchains are synchronized into isolated remote environments so that worker-local compiler installations do not silently determine results.
- **C2:** Compiler configuration and object-build nodes connect toolchain identity, local execution, distributed execution, and cache eligibility within one reusable build model.
- **C3:** Object caching and distributed compilation are independent optimization choices; their documentation explains overheads and restrictions rather than assuming every compilation should use both.

Start with [distributed compilation](https://fastbuild.org/docs/features/distribution.html) and [object caching](https://fastbuild.org/docs/features/caching.html), particularly unsupported options, toolchain synchronization, and cache access policies.

## Remote execution clients and build-engine integration

### [bazelbuild/reclient](https://github.com/bazelbuild/reclient)

**Go, with compiler dependency-scanning components — Remote execution integration for existing build invocations.** Rewrapper and reproxy let an existing build drive remote execution without requiring it to become a new build system. The interesting code is the coordination between local execution, remote execution, and output installation.

- **C1:** Racing local and remote attempts cannot both write final outputs unsafely. The action implementation stages remote outputs and coordinates ownership with a running local attempt. It also handles preservation of unchanged output modification times and remote working-directory semantics.
- **C3:** Predicted remote download latency influences when local racing begins. This makes speculation a controlled latency policy, with additional considerations for work that can continue to populate the remote cache.

The main entry point is [reproxy/action.go](https://raw.githubusercontent.com/bazelbuild/reclient/main/internal/pkg/reproxy/action.go). Follow the race state transitions and output movement before treating a remote invocation as equivalent to a simple subprocess call.

### [bazelbuild/bazel](https://github.com/bazelbuild/bazel)

**Java and C++ — Action graph, remote cache client, and remote/dynamic execution strategies.** The relevant scope is Bazel's execution machinery, not the entire build language and analysis engine. It is a reference case for connecting declared action inputs to shared results and speculative execution.

- **C1:** Dynamic execution races local and remote attempts while coordinating output access through sandboxing or output locking. Failure of the first completing branch is deliberately surfaced rather than hidden by a successful alternative, exposing environment discrepancies.
- **C2:** Actions and execution strategies separate what a build needs from where and how the command runs. The [remote-caching model](https://bazel.build/remote/caching) distinguishes AC metadata from CAS content.
- **C3:** Delayed local execution after likely remote hits and explicit CPU/memory limits balance latency against duplicate work. The [dynamic-execution guide](https://bazel.build/remote/dynamic) also explains restrictions involving persistent workers and sandboxing.

### [facebook/buck2](https://github.com/facebook/buck2)

**Rust and Starlark — Build engine with REAPI integration and deferred output materialization.** The materializer is the most distinctive study target: a successful remote action need not immediately imply that every output exists on the client's filesystem.

- **C1:** Deferred outputs require management of artifact availability, CAS expiration, and stale-output cleanup. Cleanup must coordinate with active materialization; expiration may require recovery through a restarted build rather than trusting obsolete metadata.
- **C3:** Intermediate outputs are downloaded only when a local consumer needs them. Optional SQLite state carries materialization knowledge across process restarts, avoiding unnecessary repeated downloads.

The [deferred-materialization document](https://buck2.build/docs/users/advanced/deferred_materialization/) explains the lifecycle and failure cases. The [remote-execution guide](https://buck2.build/docs/users/remote_execution/) shows how execution platforms connect to separate CAS, AC, and execution services. These are complementary views of the same monorepo subsystem.

### [pantsbuild/pants](https://github.com/pantsbuild/pants)

**Python and Rust — Process execution engine with fine-grained remote caches and REAPI execution.** Pants offers a useful view of remote execution as part of a multi-language plugin engine, with explicit environment configuration rather than an assumption that every worker resembles the client.

- **C2:** Remote-environment targets describe worker platform properties and environment-aware tool choices. Process results can use REAPI, GitHub Actions cache, or filesystem-backed providers under the broader caching model.
- **C3:** Remote process parallelism is separately bounded to avoid overwhelming workers. Fine-grained cache reuse creates a different pressure: the documentation records request-rate limitations for the experimental GitHub Actions provider.

Read [remote execution](https://www.pantsbuild.org/stable/docs/using-pants/remote-caching-and-execution/remote-execution) together with [remote caching](https://www.pantsbuild.org/stable/docs/using-pants/remote-caching-and-execution/remote-caching). **Status limitation:** the inspected documentation labels remote execution and some cache providers experimental; the selection does not imply equal readiness across them.

### [apache/buildstream](https://github.com/apache/buildstream)

**Python — Sandboxed integration builds, artifact caches, and remote execution.** BuildStream broadens the scope beyond per-source compilation to integration and packaging pipelines. Its remote architecture makes the distinction between an execution result and a reusable named build artifact especially clear.

- **C1:** Remote sandbox execution is intended to preserve local sandbox results, while lost operations and selected server errors have explicit retry handling. Interactive shells remain local because the remote protocol does not provide interactive execution semantics.
- **C2:** Commands and staged filesystem content pass through CAS and REAPI; published artifacts use a separate artifact-cache path involving the Remote Asset API. This decomposition supports different execution and artifact services.
- **C3:** Content-addressed input and output transfer allows already-present filesystem data to be reused across remote actions.

The [remote-execution architecture](https://docs.buildstream.build/master/arch_remote_execution.html) is the main study entry point, covering the local CAS, remote CAS, execution service, retry behavior, and artifact publication boundaries.

## Task-output caches

### [gradle/gradle](https://github.com/gradle/gradle)

**Java, Kotlin, and Groovy — Task-output and artifact-transform caching.** Focus on task identity, input normalization, and the cache contract. Gradle is useful for examining why byte-for-byte hashing of every visible file is not always the right definition of equivalent build work.

- **C1:** Cache keys account for task implementation, actions, properties, and declared inputs/outputs. Path sensitivity and classpath normalization must remove irrelevant differences without erasing distinctions that affect results.
- **C2:** The same cache framework applies to custom cacheable tasks and artifact transforms, with explicit opt-in and declaration requirements rather than implicit caching of arbitrary side effects.
- **C3:** Compile-classpath normalization can use ABI-relevant differences, while runtime-classpath normalization ignores incidental archive metadata. These choices reduce unnecessary misses across machines and rebuilt dependencies.

Read [build-cache concepts](https://docs.gradle.org/current/userguide/build_cache_concepts.html) for semantic identity and [the build-cache guide](https://docs.gradle.org/current/userguide/build_cache.html) for task/transform integration and local/remote reuse.

### [apache/maven-build-cache-extension](https://github.com/apache/maven-build-cache-extension)

**Java — Maven lifecycle extension for local and remote build-result reuse.** This repository tackles caching in an existing plugin ecosystem where many inputs and behaviors were not originally designed around hermetic execution. That makes configuration and reconciliation logic central engineering concerns.

- **C1:** Source selection, effective project configuration, and plugin parameters contribute to reuse decisions. The documentation distinguishes missed reuse from semantically unsafe key collisions and explains why project-specific configuration can be necessary for correctness.
- **C2:** The extension restores results into Maven's ordinary lifecycle and provides configuration for plugin execution and parameter reconciliation. Remote transport uses Maven's resolver infrastructure rather than requiring a new build language.
- **C3:** Module-level keys and version normalization support reuse of unaffected project subtrees instead of rebuilding an entire reactor.

Start with [cache concepts and limitations](https://maven.apache.org/extensions/maven-build-cache-extension/concepts.html) and the [extension overview](https://maven.apache.org/extensions/maven-build-cache-extension/index.html). The configuration-dependent correctness boundary is itself a reason to study this implementation, not a guarantee of universal safe caching.

### [vercel/turborepo](https://github.com/vercel/turborepo)

**Rust, with TypeScript documentation/tooling — Monorepo task graph and local/remote task cache.** Turborepo operates at the task-output level: it restores declared files and logs for deterministic tasks. This provides a useful comparison with compiler caches and per-action REAPI systems.

- **C1:** Global and task-specific hashes capture different invalidation scopes, including configuration, dependency changes, and environment inputs. Correct reuse depends on declared outputs and task determinism; restoring a cache entry cannot repair undeclared side effects.
- **C2:** The fingerprint-and-output model applies to different repository tasks rather than being tied to one compiler. Separating global invalidation from package/task inputs supports reuse across a dependency graph.
- **C3:** Local and remote result restoration avoids repeating whole tasks, while shared worktree caches introduce relocation constraints: absolute paths embedded in outputs are not automatically rewritten.

The [caching guide source](https://raw.githubusercontent.com/vercel/turborepo/main/apps/docs/content/docs/crafting-your-repository/caching.mdx) explains hash inputs, output declarations, log replay, and the worktree caveat in one substantive entry point.

## Container-build graph caching

### [moby/buildkit](https://github.com/moby/buildkit)

**Go — Build graph solver, workers, and container-build cache.** The relevant subsystem is the LLB graph solver and its cache model. It is especially instructive about the difference between identifying concurrent work and identifying results that remain reusable later.

- **C1:** A vertex digest can deduplicate work within a solve without being a sufficient persistent cache identity. For example, a mutable image reference needs a resolved content identity before long-term reuse is safe.
- **C2:** Vertex, operation, and cache-map interfaces separate graph shape, execution, and content-dependent cache identity. Frontends and workers can participate without collapsing those concerns into one build script.
- **C3:** The solver postpones expensive content-based checks and can resolve remote cache results lazily, while sharing concurrent requests for the same work.

Read the [solver design document](https://raw.githubusercontent.com/moby/buildkit/master/docs/dev/solver.md), particularly `Vertex`, `Op`, and `CacheMap`. It gives a more precise architectural entry point than treating BuildKit as merely a faster container command.

## Nix remote builds and binary caches

### [NixOS/nix](https://github.com/NixOS/nix)

**C++ — Remote derivation builds, store operations, and binary substitution.** The selected subsystem is `libstore`'s build worker and goal scheduler. Nix contributes a different unit of reuse: store paths and derivations, with substitution integrated into the same machinery that decides whether to build.

- **C1:** Shared goals, weak ownership, failure propagation, and balanced running-job counters require coordinated lifetimes. Worker teardown and goal removal contain explicit assertions and cleanup ordering.
- **C2:** Build goals and substitution goals fit a common scheduling model, connecting locally available results, remote cache retrieval, and actual derivation execution.
- **C3:** Separate build and substitution job limits reflect different resource demands; goal deduplication avoids issuing the same work repeatedly.

The implementation entry point is [libstore/build/worker.cc](https://raw.githubusercontent.com/NixOS/nix/master/src/libstore/build/worker.cc). The [distributed-build manual](https://nix.dev/manual/nix/2.34/advanced-topics/distributed-builds.html) supplies the SSH and platform-matching context for remote builders.

### [zhaofengli/attic](https://github.com/zhaofengli/attic)

**Rust — Multi-tenant Nix binary-cache server and client.** Attic is useful for studying shared physical storage beneath separately authorized logical caches. The repository describes it as an early prototype, so the design should not be read as a production-readiness assertion.

- **C1:** Tenant caches are restricted views over shared NAR/chunk storage. Reusing the same underlying content must not imply that every tenant can access it; server-side signing also separates upload authorization from distribution of signing keys.
- **C2:** Logical caches and shared content storage provide different abstractions for policy and physical reuse.
- **C3:** FastCDC content-defined chunking deduplicates overlapping NAR content across artifacts. Minimum/average/maximum chunk sizes and the chunking threshold affect metadata overhead and reuse; changing chunk boundaries also affects compatibility with previously uploaded content.

Read the repository's storage/tenant model and the [chunking configuration guide](https://docs.attic.rs/admin-guide/chunking.html). Together they connect authorization boundaries to the mechanics of byte-level deduplication.

### [nix-community/harmonia](https://github.com/nix-community/harmonia)

**Rust — Nix binary-cache serving; focus on `harmonia-cache`.** Harmonia serves store content through the Nix cache protocol. The monorepo is counted once; the relevant study target is its metadata lookup, NAR streaming, compression, and HTTP behavior.

- **C1:** Release notes describe replacing memory-mapped file reads after instrumentation could alter mapped bytes and thereby break NAR signatures. They also record fixes for range responses, content encoding during interrupted downloads, and signed content-addressed realizations. Byte identity and transport semantics are inseparable here.
- **C3:** Direct SQLite metadata lookup, batched payload streaming, and configurable compression address serving overhead. The mmap reversal is a concrete example of revising an optimization when it violates content integrity.

The repository documentation establishes the serving architecture; the [release notes](https://github.com/nix-community/harmonia/releases) provide substantive implementation and failure-history entry points, particularly the 3.1–3.3 changes. These are reported design changes, not independently reproduced performance results.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, including REAPI servers and storage implementations; distributed C/C++ compilation and compiler caches; Gradle/Maven shared task caches; Rust build caches; remote-execution clients and local/remote racing; container-build solver caches; Nix binary-cache servers and remote builders; and less familiar or historical projects such as Scoot, BuildCache, recc, and BlueKing Turbo. Follow-up searches targeted scheduler code, cache integrity, materialization, configuration schemas, and release histories. Later queries mostly repeated these families or surfaced wrappers, forks, and projects whose substantive implementation could not be verified within the required GitHub scope.

The selection spans Go, Rust, C, C++, Java, and Python, and ranges from focused disk-cache implementations to build-engine monorepos and distributed clusters. Buildbarn's two entries implement distinct storage and execution responsibilities. Other monorepos appear only once. Compiler-result, action-result, task-output, container-graph, and Nix store-path caches are deliberately distinguished because their invalidation and failure models differ.

Important exclusions and limits:

- **Non-GitHub homes and moved repositories:** [BuildGrid's official documentation](https://buildgrid.gitlab.io/buildgrid/) points to its GitLab implementation and the BuildBox/recc ecosystem. No substantive official GitHub mirror was verified for inclusion. [mbitsnbites/buildcache](https://github.com/mbitsnbites/buildcache) is an archived relocation stub pointing to GitLab and was excluded rather than presented as a current GitHub implementation.
- **Insufficient primary verification:** historical and regional candidates were searched, but not retained when their canonical repository or a substantive additional primary source could not be reliably opened. In particular, the searched BlueKing Turbo repository could not be verified successfully through the live browser. This is a retrieval limitation, not a claim that the project lacks merit or no longer exists.
- **Scope boundaries:** generic CI runners, general Redis/object-storage implementations, deployment-only wrappers, lists of projects, and proprietary services without a studyable implementation were excluded. Other broad build systems with overlapping cache features were not added merely to increase the count.
- **Evidence strength:** architectural facts come from the cited project sources; the proposed engineering lessons and C1–C4 assignments are grounded judgments. No claim is made that every configuration preserves hermeticity, that every selected repository is actively maintained, or that an advertised speedup generalizes. C4 is used only where multi-year compatibility/testing evidence was actually inspected. Prototype, experimental, and restrictive-license qualifications are stated in the relevant entries.

This is a selection guide for comparative code study. It favors concrete mechanisms and documented tradeoffs over popularity or a uniform claim of exemplary quality.
