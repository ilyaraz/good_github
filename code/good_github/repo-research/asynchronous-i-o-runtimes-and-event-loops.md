# Asynchronous I/O runtimes and event loops

Research date: **2026-10-09**

This selection covers 26 GitHub repositories implementing event notification, asynchronous I/O scheduling, completion-based runtimes, cooperative fibers, or closely integrated networking reactors. It ranges from portable C libraries and server runtimes to an embedded executor. Networking frameworks qualify here when their event loop, scheduling, or concurrency model is a substantial reusable subsystem. CPython and Embassy are counted once each, with the relevant subsystems identified below.

The criteria are selection judgments grounded in the linked primary material, not a claim that every component is uniformly exemplary. Repository pages were opened to verify identities, and each selection has additional primary documentation or implementation evidence. Performance discussion concerns mechanisms and tradeoffs, not unverified benchmark rankings. Unless explicitly discussed, inclusion does not assert a particular maintenance cadence or compatibility guarantee.

**Criteria legend**

- **C1 — Correctness:** difficult invariants, concurrency, ownership, cancellation, adversarial conditions, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces that support different applications or backends.
- **C3 — Performance and structure:** concrete resource or latency constraints addressed through understandable architecture.
- **C4 — Evolution:** years of changes accompanied by compatibility, testing, or complexity-management evidence.

## Native event loops and server reactors

### 1. [libuv/libuv](https://github.com/libuv/libuv)

**C; portable asynchronous I/O and event-loop foundation.** Study how a common handle/request API accommodates OS-specific notification mechanisms, networking, filesystem work, processes, and timers.

- **C1:** Handles cannot be reclaimed before their close callback; requests have distinct completion and cleanup rules. Loop and handle operations are generally confined to one thread. These explicit lifetime rules make the [design overview](https://docs.libuv.org/en/stable/design.html) a useful starting point for reviewing asynchronous C ownership.
- **C2:** Long-lived handles and short-lived requests separate resource identity from individual operations across several I/O families, as explained in the same design document.
- **C4:** The [ChangeLog](https://raw.githubusercontent.com/libuv/libuv/v1.x/ChangeLog) records the 2014 1.0 release through 2026 releases, including platform fixes, race corrections, and test changes. The repository also documents SemVer and ABI stability policies. This is evidence of sustained compatibility work, rather than merely an old creation date.

**Entry points:** design overview; ChangeLog.

### 2. [libevent/libevent](https://github.com/libevent/libevent)

**C; readiness events and buffered asynchronous streams.** A good study in building progressively richer abstractions over a small callback-driven core.

- **C1:** Events move between initialized, pending, and active states, with different rearming behavior for persistent events. The [event lifecycle guide](https://libevent.org/libevent-book/Ref4_event.html) explains deletion, signal constraints, and why reassigning a pending event is unsafe.
- **C2:** Bufferevents combine a transport with input/output buffers, exposing one interface for socket, filtering, and paired implementations. Their [design guide](https://libevent.org/libevent-book/Ref6_bufferevent.html) explains partial writes, watermarks, deferred callbacks, and reference-counted destruction while callbacks remain pending.
- **C3:** Watermarks bound buffering behavior, while deferred callbacks prevent deeply recursive callback chains. The architecture exposes these policies without making application code implement every partial I/O transition.

**Entry points:** event lifecycle guide; bufferevent guide. The book contains historical version annotations; use it for the explained contracts, not as a current platform-support matrix.

### 3. [chriskohlhoff/asio](https://github.com/chriskohlhoff/asio)

**C++; standalone Asio asynchronous I/O library.** Study executors and composed operations as a way to preserve scheduling semantics across reusable asynchronous components. The standalone repository is counted once; Boost.Asio is not a second selection.

- **C1:** A strand serializes handler execution. For composed operations, intermediate handlers must use the same strand as the final handler when shared state can also be accessed by cancellation or close operations. The [strands documentation](https://think-async.com/Asio/asio-1.30.2/doc/asio/overview/core/strands.html) gives the concrete socket-close example.
- **C2:** Associated executors carry the scheduling policy through an operation rather than hard-coding a thread or lock into every component. The same document shows both handler customization and executor binding, making it useful for studying extensible asynchronous APIs.

**Entry point:** the versioned strands and associated-executor guide.

### 4. [scylladb/seastar](https://github.com/scylladb/seastar)

**C++; per-core reactor and asynchronous server framework.** Particularly useful for engineers studying systems where cross-core sharing, storage latency, and CPU scheduling are intertwined.

- **C2:** Futures and continuations compose network I/O, disk I/O, and higher-level asynchronous operations. The [programming guide](https://docs.seastar.io/master/tutorial.html) connects these APIs to sharded services, resource limiting, and shutdown mechanisms.
- **C3:** Each core runs a cooperative scheduler over its own data, with explicit inter-core messages to reduce synchronization and cache-line traffic. The guide also explains task quotas and preemption points: a chain of ready futures can otherwise starve the reactor, so immediate continuation execution needs an explicit fairness policy.

**Entry point:** the programming guide, especially “Threads and memory,” “Preemption and Task Quota,” and “Introducing shared-nothing programming.” The useful lesson is the tradeoff between locality and cooperative progress, not a universal throughput advantage.

### 5. [mitchellh/libxev](https://github.com/mitchellh/libxev)

**Zig with a C API; portable completion-oriented event loop.** A compact comparison with libuv for studying caller-managed storage and a proactor interface over different OS backends.

- **C1:** The [general manual](https://raw.githubusercontent.com/mitchellh/libxev/main/docs/xev.7.scd) defines dead, added, and active completion states. Active completion memory cannot be modified or freed, and a loop must retain a stable address after it first runs.
- **C2:** Low-level completions and higher-level watchers separate platform-specific operations from reusable timer, socket, and file interfaces.
- **C3:** The caller supplies storage; the library's documented no-runtime-allocation design makes allocation costs explicit. Optional thread-pool work handles operations without suitable asynchronous OS support.

**Entry point:** `docs/xev.7.scd`. Platform descriptions in the README and manual are not perfectly synchronized; Linux, macOS, and WASI are the concrete backend examples used here, with no Windows-support claim.

## Rust runtimes and reactor building blocks

### 6. [tokio-rs/tokio](https://github.com/tokio-rs/tokio)

**Rust; general-purpose asynchronous runtime.** Study the interaction between the scheduler, I/O driver, timers, local task queues, and cross-thread wakeups.

- **C1:** The [runtime documentation](https://docs.rs/tokio/latest/tokio/runtime/) states a conditional fairness guarantee: task count and individual poll duration must be bounded. It distinguishes eventual scheduling from equal scheduling and permits spurious task wakeups.
- **C2:** A runtime combines configurable scheduling, I/O, and time services, with current-thread and multithreaded configurations for different workloads.
- **C3:** The documented scheduler uses worker-local queues, a global queue, work stealing, periodic I/O checks, and a bounded-use LIFO optimization. Those mechanisms expose the tension between locality and starvation prevention. Their exact tuning is explicitly described as implementation behavior that may change.

**Entry point:** runtime documentation, particularly “Detailed runtime behavior.”

### 7. [tokio-rs/mio](https://github.com/tokio-rs/mio)

**Rust; low-level portable readiness polling.** This is a runtime building block, not a task executor or complete async runtime. Study which OS differences can be hidden and which must remain in the public contract.

- **C1:** [`Poll` documentation](https://docs.rs/mio/latest/mio/struct.Poll.html) explicitly allows spurious readiness and requires draining an operation until `WouldBlock`; otherwise another event is not guaranteed. Close/error flags are hints rather than substitutes for handling actual I/O results.
- **C2:** `Poll`, registration interests, event sources, and application tokens provide a reusable event demultiplexing interface across platforms.
- **C3:** The repository deliberately omits timers, file operations, and thread pools, and documents an allocation-free runtime polling layer. That narrow boundary makes the costs of a higher-level runtime easier to isolate.

**Entry point:** `Poll`, including “Portability” and “Implementation notes.”

### 8. [smol-rs/async-io](https://github.com/smol-rs/async-io)

**Rust; executor-independent I/O reactor and timers used in the smol ecosystem.** Selected instead of the top-level smol crate, whose current role is chiefly re-exporting smaller libraries.

- **C1:** The [reactor implementation](https://raw.githubusercontent.com/smol-rs/async-io/master/src/reactor.rs) uses a polling-round ticker to reject stale readiness, locks the event collection to establish exclusive polling rights, and gives equal-deadline timers distinct identifiers.
- **C2:** `Async` adapts existing networking and descriptor types, while `Timer` exposes time through futures. The repository explains how `block_on` can drive I/O on the caller's thread, with a background reactor thread as fallback.
- **C3:** Timer insertion/removal operations are queued and processed in batches. Reading that queue alongside the ordered timer map makes the synchronization-versus-throughput tradeoff concrete.

**Entry point:** `src/reactor.rs`, starting with `Reactor`, timer operations, and readiness synchronization.

### 9. [monoio-rs/monoio](https://github.com/monoio-rs/monoio)

**Rust; per-core runtime with io_uring and readiness backends.** This is the verified current repository identity; older search results use `bytedance/monoio`.

- **C1:** The [`IoBuf` contract](https://docs.rs/monoio/latest/monoio/buf/trait.IoBuf.html) transfers buffer ownership to the runtime, offers owned slicing, and requires a valid stable address and initialized-byte count while the kernel accesses memory. This is a concrete example of asynchronous kernel lifetimes reshaping an API.
- **C3:** Tasks stay on one thread, avoiding migration requirements and enabling thread-local data. The repository candidly notes that uneven workloads can leave cores underused relative to a work-stealing runtime.
- **C2:** The runtime exposes asynchronous networking over alternative I/O drivers, but its distinct I/O traits entail ecosystem compatibility tradeoffs documented in the README.

**Entry point:** `monoio::buf::IoBuf`; the repository's design goals and limitations provide the architectural context.

### 10. [DataDog/glommio](https://github.com/DataDog/glommio)

**Rust; Linux io_uring runtime for cooperative per-core applications.** Especially useful for storage-service scheduling and workload isolation within one thread.

- **C2:** The [crate architecture documentation](https://docs.rs/glommio/latest/glommio/) presents timers, file/network I/O, CPU placement, task queues, and scheduling controllers as coordinated runtime abstractions.
- **C3:** Task queues carry adjustable CPU shares, allowing separate workloads to divide a core while permitting an otherwise idle workload to use available capacity. Direct I/O is a first-class choice. These are concrete application-level scheduling and storage policies rather than merely a thin syscall binding.

**Entry point:** crate documentation, especially “Scheduling,” “Direct I/O,” and “Controlled processes.” Linux/io_uring requirements and cooperative scheduling are meaningful boundaries; this is not a portable substitute for every general-purpose runtime.

### 11. [compio-rs/compio](https://github.com/compio-rs/compio)

**Rust; completion-based runtime spanning IOCP, io_uring, and polling.** Study how completion semantics can be shared across Windows and Unix-oriented designs, with a driver usable separately from the async executor.

- **C1:** [`CancelToken`](https://docs.rs/compio-runtime/latest/compio_runtime/struct.CancelToken.html) specifies immediate cancellation for operations registered after cancellation and deduplication of repeated operation-key registrations. These are useful invariants for cancellation races and operation bookkeeping.
- **C2:** The repository separates driver, runtime, buffers, filesystem, and networking crates. [`IoBuf`](https://docs.rs/compio-buf/latest/compio_buf/trait.IoBuf.html) supplies a common initialized-byte view and owned slicing for completion-based operations across several buffer types.

**Entry points:** cancellation-token contract; buffer contract. The inspected README explicitly declines an MSRV guarantee before 1.0 and says releases can require a recent stable Rust toolchain; no long-term compatibility claim is implied here.

## Python event loops and concurrency semantics

### 12. [python/cpython](https://github.com/python/cpython)

**Python and C; specifically the `asyncio` subsystem.** Study a standard-library event loop whose extension contracts and shutdown behavior must serve many independent libraries. The rest of the interpreter is outside this entry's scope.

- **C1:** The [event-loop reference](https://docs.python.org/3/library/asyncio-eventloop.html) distinguishes thread-safe scheduling, transport ownership of sockets, asynchronous-generator finalization, and executor shutdown. These are lifecycle obligations beyond simply polling descriptors.
- **C2:** The same API is implemented by selector and proactor loops, with protocols/transports and task/future integration above them.
- **C3:** [`BaseEventLoop._run_once`](https://raw.githubusercontent.com/python/cpython/main/Lib/asyncio/base_events.py) combines a ready deque and timer heap, compacts cancelled timers according to thresholds, and processes a snapshot of ready callbacks so newly scheduled callbacks wait until another I/O poll.

**Entry points:** event-loop reference; `Lib/asyncio/base_events.py`.

### 13. [python-trio/trio](https://github.com/python-trio/trio)

**Python; structured-concurrency I/O runtime.** Study how task lifetime rules and explicit cancellation points can simplify reasoning about an entire concurrent call tree.

- **C1:** The [core reference](https://trio.readthedocs.io/en/stable/reference-core.html) defines checkpoints as both cancellation and scheduling points, documents the implications for shared state, and explains nursery ownership of child tasks. Nurseries prevent tasks from silently becoming orphaned.
- **C2:** Nurseries, cancellation scopes, clocks, and instrumentation are reusable control structures rather than application-specific server machinery. The clock parameter also permits a mock clock, making time a replaceable dependency.
- **C3:** Checkpoints make cooperative progress explicit: missing them delays cancellation and other tasks, while guaranteed checkpoints in successful Trio async calls make review more predictable.

**Entry point:** core reference, especially checkpoints, cancellation, and nurseries.

### 14. [MagicStack/uvloop](https://github.com/MagicStack/uvloop)

**Cython and Python; a substantive asyncio-compatible loop implementation over libuv.** Study compatibility at the boundary between a Python event-loop API, C-level state, and native handles.

- **C1:** The [loop source](https://raw.githubusercontent.com/MagicStack/uvloop/master/uvloop/loop.pyx) handles Python execution contexts, socket I/O references, registered object lifetimes, and fork integration. The [release history](https://github.com/MagicStack/uvloop/releases) supplies a concrete failure case: cancellation during connection creation required detaching a socket to prevent double-close.
- **C3:** The same release notes document direct Python C-API context entry/exit, transport-write improvements, and SSL buffered-read changes. The implementation is substantial work on object overhead and transport behavior, not a generated wrapper.

**Entry points:** `uvloop/loop.pyx`; releases. Compatibility work includes new Python task arguments and CI coverage; no numerical speedup is assumed.

### 15. [twisted/twisted](https://github.com/twisted/twisted)

**Python; pluggable reactors and Deferred-based asynchronous networking.** Study an alternative composition model to native coroutine-first runtimes, especially error propagation through callback chains.

- **C1:** The [Deferred reference](https://docs.twisted.org/en/stable/core/howto/defer.html) explains transitions between callbacks and errbacks, how returning normally can consume a failure, and why adding paired callbacks differs from adding a callback followed by an errback. Cancellation also needs cooperation from the underlying operation.
- **C2:** Deferreds standardize delayed results across many operations, while the repository documents interchangeable OS and GUI reactors. Its Trial testing framework and reactor-selectable test runs show how those extension boundaries are exercised.

**Entry point:** Deferred reference. Focus on `twisted.internet` and its reactor/Deferred contracts; the repository's numerous protocol implementations are supporting context, not separate selections.

### 16. [gevent/gevent](https://github.com/gevent/gevent)

**Python, Cython, and C; greenlet-based cooperative I/O.** Useful for studying stackful coroutine scheduling and the hazards of making synchronous-looking APIs cooperative.

- **C1:** The [Hub contract](https://www.gevent.org/api/gevent.hub.html) describes per-thread hubs, switching into the event-loop greenlet, restrictions on blocking from switch hooks, and destruction after which existing hub-bound objects cannot safely continue.
- **C2:** The hub mediates greenlets, loop callbacks, error handling, and thread-pool facilities. The [backend comparison](https://www.gevent.org/loop_impls.html) explains the libev/libuv and Cython/CFFI implementations and their portability differences.

**Entry points:** Hub API; loop implementation comparison. Some comparison text is historical, including relative ages and past wheel limitations; those details are not treated as current measurements or support guarantees.

## JVM and Swift asynchronous infrastructure

### 17. [netty/netty](https://github.com/netty/netty)

**Java with native transport components; asynchronous networking event loops.** Study the separation between transport events, channel ownership, and reusable protocol handlers.

- **C1:** The [`ChannelPipeline` contract](https://netty.io/4.1/api/io/netty/channel/ChannelPipeline.html) explains handler ordering, thread-safe pipeline modification, and offloading that still preserves serial execution per handler context. Preserving order can itself become a bottleneck.
- **C2:** Inbound and outbound handlers traverse the pipeline in opposite directions. Handlers, contexts, channels, and executor groups allow protocol processing to be composed independently of the transport implementation.
- **C3:** The same reference explicitly discusses choosing ordered versus unordered execution when offloading work and skipping irrelevant handlers to reduce stack depth. These are visible architectural controls over event-processing cost.

**Entry point:** `ChannelPipeline`, especially event flow and executor-group dispatch. Native transports and protocol codecs in the monorepo are counted with the core, not separately.

### 18. [eclipse-vertx/vert.x](https://github.com/eclipse-vertx/vert.x)

**Java; Vert.x Core runtime and I/O toolkit.** Study the layer above a transport loop: execution contexts, deployment units, asynchronous results, worker execution, and an event bus.

- **C1:** The [core manual](https://vertx.io/docs/vertx-core/java/) explains context-affine execution and the need to dispatch external `CompletionStage` results back onto the correct context. The usual same-event-loop guarantee has scope and depends on not bypassing the model with arbitrary threads.
- **C2:** Core unifies network services, timers, filesystem access, event-bus communication, and verticle lifecycle without requiring a particular high-level web framework.
- **C3:** Its multi-reactor model uses multiple event loops while keeping ordinary verticle execution serialized. Blocked-loop detection and worker execution address the practical risk that one handler stops progress for unrelated I/O.

**Entry point:** core manual, particularly the reactor model, contexts, and blocking work. This entry is specifically `vertx-core`.

### 19. [typelevel/cats-effect](https://github.com/typelevel/cats-effect)

**Scala; asynchronous effect and fiber runtime for JVM and other targets.** Study a runtime in which resource handling and concurrency composition are represented as typed effects, with I/O integration evolving alongside the scheduler.

- **C2:** The [thread-model guide](https://typelevel.org/cats-effect/docs/thread-model) distinguishes suspending a fiber from blocking a thread and explains `Deferred`, cooperative yielding, and the separation of compute and blocking work.
- **C3:** The [release history](https://github.com/typelevel/cats-effect/releases) documents the integrated runtime and the port of the work-stealing pool to Scala Native, including epoll/kqueue support. This makes it useful for studying coordination among timers, polling, and runnable fibers across targets.
- **C1:** Release notes also document resource leaks from timeouts and pathological cancellation behavior in bounded parallel traversal, connecting high-level combinators to real runtime failure modes.

**Entry points:** thread-model guide; releases. The guide includes historical CE2/CE3 comparisons; use the release notes to contextualize newer integrated-runtime behavior.

### 20. [apple/swift-nio](https://github.com/apple/swift-nio)

**Swift with platform shims; event-loop and channel infrastructure.** Focus on `NIOCore`, `NIOPosix`, and `NIOEmbedded` within this repository.

- **C1:** The repository's architectural overview explains channel ownership of descriptors and event-loop affinity of future callbacks. [`SelectableEventLoop`](https://raw.githubusercontent.com/apple/swift-nio/main/Sources/NIOPosix/SelectableEventLoop.swift) separately represents internal and external lifecycle state, protects task queues, and documents the invariant that its thread never changes.
- **C2:** Channels, pipelines, promises, and bootstraps form a reusable networking model. Embedded channels and loops allow protocol behavior to be driven without real networking, providing a valuable separation for testing.
- **C3:** The loop source combines immediate and scheduled task structures, batched task storage, selector wakeups, and tick metrics; its comments also warn against putting expensive work in per-tick instrumentation.

**Entry point:** `Sources/NIOPosix/SelectableEventLoop.swift`, read alongside the repository's conceptual overview.

## Other language ecosystems

### 21. [ocaml-multicore/eio](https://github.com/ocaml-multicore/eio)

**OCaml; effects-based direct-style concurrent I/O.** Study how an effect handler can suspend ordinary-looking code while retaining explicit resource and cancellation structure.

- **C1:** The [`Eio.Cancel` reference](https://ocaml-multicore.github.io/eio/eio/Eio/Cancel/index.html) defines trees of cancellation contexts and protected children. It carefully distinguishes cancellation before an operation from cancellation after success while the fiber waits on the run queue, avoiding an oversimplified “cancellation always wins” rule.
- **C2:** The repository explains a generic I/O interface over platform backends, plus switches, flows, fibers, mock implementations, and capability-oriented access. These let applications vary their environment without replacing the concurrency model.

**Entry point:** cancellation reference; the repository's substantial design narrative supplies the broader effects, switches, capabilities, and testing context. This is counted once despite multiple backend libraries in the repository.

### 22. [ocsigen/lwt](https://github.com/ocsigen/lwt)

**OCaml; promise-based concurrency and asynchronous Unix I/O.** A useful contrast with Eio: composition is expressed through promises, with blocking work and readiness managed beneath that interface.

- **C1:** The [manual](https://ocsigen.org/lwt/latest/lwt/manual.html) explains that cancelling a promise need not cancel the actual operation. An operation must arrange its own cancellation callback; cancellation propagates through promise dependencies, and protected promises change that propagation.
- **C2:** Promise combinators, I/O channels, and synchronization helpers build on interchangeable event engines. [`Lwt_engine`](https://ocsigen.org/lwt/latest/lwt/Lwt_engine/index.html) exposes engine interfaces, libev/select implementations, and replacement that can transfer existing events.

**Entry points:** manual's cancellation and scheduler sections; `Lwt_engine` reference. The engineering interest lies in keeping promise semantics distinct from what an OS operation can actually cancel.

### 23. [panjf2000/gnet](https://github.com/panjf2000/gnet)

**Go; explicit event-driven networking framework.** A useful alternative to studying only Go's normal goroutine-per-connection application style. Its scope is reusable transport machinery rather than an application protocol server.

- **C1:** The [Unix event-loop implementation](https://raw.githubusercontent.com/panjf2000/gnet/master/eventloop_unix.go) handles `EAGAIN`, partial reads/writes, and edge-triggered progress. When a bounded read leaves a full read buffer, it can explicitly trigger another read event so unread socket data is not stranded.
- **C3:** A loop owns a poller, reusable packet buffer, and connection storage. Write paths use vectored output and buffer accounting, exposing how syscall cost, buffering, and fairness are managed together.
- **C2:** The repository's event-handler API supports building different application protocols over TCP, UDP, and Unix sockets.

**Entry point:** `eventloop_unix.go`, especially read/write handling. The repository explicitly treats this as a specialized alternative to Go's `net`, with different programming assumptions.

### 24. [socketry/async](https://github.com/socketry/async)

**Ruby; fiber scheduler and asynchronous reactor.** Study integrating runtime scheduling with ordinary Ruby I/O while retaining nested task ownership.

- **C1:** The [scheduler guide](https://socketry.github.io/async/guides/scheduler/index.html) explains thread confinement, cancellation of the scheduler's child task tree, and why applications must not depend on incidental optimistic-versus-deferred execution order. The repository's release notes give concrete fixes for interrupted I/O waits, timeout preservation, and fork cleanup.
- **C2:** The scheduler implements Ruby's fiber-scheduler interface, while nested tasks behave as awaitable results. `run_once` allows embedding inside another event loop, making it reusable beyond a standalone server.
- **C3:** Waiting tasks yield to an OS-backed event selector instead of occupying a thread per operation.

**Entry point:** scheduler guide, especially embedding and scheduling design.

### 25. [revoltphp/event-loop](https://github.com/revoltphp/event-loop)

**PHP; shared event-loop and fiber-suspension foundation.** Study a deliberately small interoperability layer beneath higher-level concurrency libraries.

- **C1:** The [fundamentals](https://revolt.run/fundamentals) explain one shared scheduler, callback iteration, and loop lifetime. The [fiber guide](https://revolt.run/fibers) demonstrates racing readable-stream activity against a timer and cancelling registrations after resumption, making cleanup obligations visible.
- **C2:** A driver interface and common timer, stream, signal, and suspension APIs let different concurrency libraries use the same scheduler. Suspension works both inside a fiber and from the main execution context.
- **C3:** Callbacks execute in fibers that can be reused when they do not suspend, avoiding unnecessary fiber creation. The loop waits until I/O or the next timer unless immediate work is pending.

**Entry points:** fundamentals; fiber/suspension guide. This is the event-loop layer, not an entire concurrent application framework.

## Embedded and interrupt-driven execution

### 26. [embassy-rs/embassy](https://github.com/embassy-rs/embassy)

**Rust; specifically `embassy-executor`, its timers, and async I/O integration.** Included to cover a different scale: event-driven execution under tight RAM and energy constraints, rather than only server sockets.

- **C1:** The [executor documentation](https://docs.embassy.dev/embassy-executor/0.10.0/cortex-m/index.html) specifies a platform wakeup callback that must bring a sleeping executor back to polling. It also describes scheduling fairness among runnable tasks and multiple executor priorities. Cooperative task bodies still have to return control.
- **C2:** A raw executor can be wrapped for a custom platform or RTOS; the main-loop and wakeup boundary is explicit, while HALs integrate hardware-specific behavior.
- **C3:** Tasks have statically sized storage, the executor needs no heap, and only awakened tasks are polled. Idle CPUs can sleep until interrupts or wake signals arrive, tying the architecture directly to memory and power budgets.

**Entry point:** `embassy-executor` documentation, particularly platform integration. The whole Embassy monorepo is counted once.

## Coverage, search process, and limitations

Discovery used more than six distinct live search formulations, followed by repository-page verification and deeper primary-source reads. Search angles included:

- Portable C event loops and their ownership models: libuv, libevent, libev, and related libraries.
- C++ reactors, futures, executors, and shared-nothing server architecture.
- Rust readiness polling, io_uring, IOCP, per-core scheduling, and decomposed runtime components.
- Python structured concurrency, replacement asyncio loops, Deferred reactors, and greenlets.
- JVM pipelines, Vert.x contexts, and Scala effect-runtime scheduling.
- OCaml effects versus promises; Swift event-loop ownership; explicit Go reactors.
- Ruby fiber scheduling, PHP's shared scheduler, Zig completion APIs, and embedded interrupt-driven execution.

Later targeted searches mainly added implementation evidence or alternatives within already-covered families; the embedded pass added Embassy because it introduced a materially different resource model. The selection is deliberately somewhat larger than 25 to preserve that distinction. It is not an exhaustive inventory of asynchronous libraries.

Important selection boundaries: the top-level smol re-export crate was replaced with `async-io`; standalone Asio and Boost.Asio were not double-counted; libuv and uvloop remain separate because uvloop has substantial Python-specific loop and transport implementation. Pure wrappers, tutorials, benchmark-only projects, and general web frameworks were excluded. Bare io_uring bindings and GUI toolkit loops were not independently catalogued. A libev GitHub candidate surfaced, but this research did not establish an official substantive GitHub mirror, so it was not retained. Libev is still discussed where it is an implementation dependency of verified projects.

No retained entry is presented as an unofficial mirror or an archival reconstruction. No repository was cloned or executed, and no comparative benchmark was run. Some primary manuals mix historical material with current APIs; entries flag material cases, and links to rolling documentation may change after the research date. Platform support, version compatibility, and production suitability require project-specific evaluation. Architectural strengths and the mapping to C1–C4 are reasoned assessments of the inspected material, not claims of a complete correctness audit.
