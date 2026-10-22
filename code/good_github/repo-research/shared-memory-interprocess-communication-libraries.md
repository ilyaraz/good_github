# Shared-memory interprocess communication libraries

Research date: **2026-10-09**.

This report selects **23 GitHub repositories** implementing reusable communication between processes through shared mappings: allocators and object transport, publish/subscribe middleware, bounded queues, socket-like channels, and memory-mapped persistent logs. Broader projects qualify through the specific shared-memory subsystem identified below. Shared-memory transport does not automatically imply end-to-end zero-copy, durability, or safe communication with hostile peers; the entries distinguish those properties where relevant.

Criteria used:

- **C1 — Difficult correctness:** concurrency, memory ownership, layout invariants, adversarial peers, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces and components supporting multiple applications or communication patterns.
- **C3 — Performance with structure:** concrete latency, allocation, copying, or contention concerns addressed through an understandable design.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility management, testing, or architectural maintenance.

Criterion assignments are engineering judgments grounded in the linked material, not certifications. Source files were inspected without building or executing candidate code. Historical and experimental projects remain useful study material, but inclusion does not imply present maintenance or production readiness.

## Shared allocation and object-transport frameworks

### 1. [boostorg/interprocess](https://github.com/boostorg/interprocess)

**Language/role:** C++; shared-memory objects, mapped files, process-shared synchronization, allocators, containers, and message queues.

Study how ordinary C++ object construction becomes a cross-process operation. **C1:** named construction and destruction are atomic within managed segments, while relative pointers allow mappings at different virtual addresses. The allocator's pointer and mutex types are part of the segment's correctness model. **C2:** replaceable allocation algorithms and name indexes support much more than a single queue or message format. These mechanisms are explained in the [managed-memory guide](https://www.boost.org/doc/libs/latest/doc/html/interprocess/managed_memory_segments.html).

**C4:** the [documentation source and release history](https://github.com/boostorg/interprocess/blob/develop/doc/interprocess.qbk) records the message-queue implementation dating to Boost 1.52 in 2012, subsequent ABI changes, regression fixes, and the compatibility macro for the pre-1.87 segment-manager layout. This is unusually useful material on evolving an in-memory ABI.

### 2. [Flow-IPC/ipc](https://github.com/Flow-IPC/ipc)

**Language/role:** C++17; integrated IPC toolkit, with shared-memory allocation, sessions, structured messages, and transport modules maintained through component repositories.

Count the integrated project once; the relevant components are `ipc_shm`, `ipc_shm_arena_lend`, SHM-backed sessions, and structured transport. **C1:** session-scoped and application-scoped arenas impose different maximum object lifetimes; the jemalloc lending provider also restricts receiver writes. **C2:** the same session/channel model supports native C++ structures, allocator-aware containers, and Cap'n Proto messages. **C3:** provider selection changes how data is allocated and shared while retaining much of the public API, making the performance abstraction itself worth studying.

The [direct-allocation and SHM-transport manual](https://github.com/Flow-IPC/ipc/blob/main/src/doc/manual/l-transport_shm.dox.txt) explains arena ownership, cleanup, capacity, and the classic-versus-jemalloc tradeoffs. The inspected README targets Linux/x86-64; broader portability should not be assumed.

### 3. [cloudtoid/interprocess](https://github.com/cloudtoid/interprocess)

**Language/role:** C# and Rust implementations of a shared queue protocol, with C, Python, Node.js, and Go interfaces in the same repository.

This is particularly useful for studying cross-language agreement on shared bytes. **C1:** protocol v3 specifies atomic reservation, release publication, aligned record headers, participant leases, dead-reader recovery, and PID-reuse handling. Its specification explicitly distinguishes atomic enqueue reservations from a globally lock-free queue and describes possible loss during recovery. **C2:** a common protocol supports a managed .NET implementation and a native Rust engine used by several languages. **C3:** reusable buffers and coalesced notifications address allocation and system-call overhead.

Start with the unusually detailed [protocol specification](https://github.com/cloudtoid/interprocess/blob/main/src/website/docs/protocol.html) and the compact [.NET circular-buffer implementation](https://github.com/cloudtoid/interprocess/blob/main/src/dotnet/Interprocess/Memory/CircularBuffer.cs). Subscribers compete for messages; this is transient work distribution, not broadcast or durable storage.

## Real-time and publish/subscribe middleware

### 4. [eclipse-iceoryx/iceoryx2](https://github.com/eclipse-iceoryx/iceoryx2)

**Language/role:** Rust core with language bindings; service-oriented shared-memory publish/subscribe, events, and request/response.

Study the separation between user-facing loans and the transport's offset-transfer protocol. **C1:** the zero-copy connection API models maximum borrowed chunks, safe overflow, incompatible connection settings, corrupted returned offsets, and channel closure as explicit states or errors. **C2:** replaceable connection backends and service/port abstractions support several communication patterns. **C3:** publishers loan samples from shared storage and transfer references instead of routing payloads through a broker.

Entry points are the [zero-copy connection contracts](https://github.com/eclipse-iceoryx/iceoryx2/blob/main/iceoryx2-cal/src/zero_copy_connection/mod.rs) and [publisher implementation](https://github.com/eclipse-iceoryx/iceoryx2/blob/main/iceoryx2/src/port/publisher.rs). This is a substantive Rust-core successor to classic iceoryx, not a binding or duplicate fork. Platform support levels vary in the README.

### 5. [eclipse-iceoryx/iceoryx](https://github.com/eclipse-iceoryx/iceoryx)

**Language/role:** C++; classic iceoryx shared-memory middleware and its typed/untyped publishing and request/response APIs.

**Status:** the repository explicitly declares maintenance mode: security fixes only, no further major releases, with eventual EOL tied to iceoryx2's 1.0 release.

**C1:** a producer reserves a chunk, consumers receive relocatable references, and the chunk returns to its pool only after all relevant consumers release it. **C2:** configurable management/user segments and multiple fixed-size pools underpin both publish/subscribe and client/server use. **C3:** choosing a suitable preallocated chunk and distributing references exposes the tradeoff between predictable allocation and internal fragmentation.

The [shared-memory architecture](https://github.com/eclipse-iceoryx/iceoryx/blob/main/doc/shared-memory-communication.md) is a clear starting point. The [quality declaration](https://github.com/eclipse-iceoryx/iceoryx/blob/main/QUALITY_DECLARATION.md) separately documents the project's quality and testing policies; its scope should be read rather than generalized to every component.

### 6. [eclipse-ecal/ecal](https://github.com/eclipse-ecal/ecal)

**Language/role:** C++ core with multiple language interfaces; communication middleware whose local transport includes its own SHM implementation.

The relevant subsystem is the shared-memory transport, not the recording GUI or network transports. **C1:** publishers announce mapped files and synchronization objects; counters expose overwritten messages, while an optional acknowledgement handshake changes publisher blocking behavior. **C2:** transport selection sits beneath reusable publish/subscribe interfaces and can be configured at different scopes. **C3:** the design explicitly compares copying, which decouples subscriber processing, with optional zero-copy for large payloads.

Read the [SHM transport design](https://github.com/eclipse-ecal/ecal/blob/master/doc/rst/advanced/layers/shm.rst) alongside the [transport-layer overview](https://github.com/eclipse-ecal/ecal/blob/master/doc/rst/advanced/transport_layers.rst). The documentation says ordinary SHM transport involves copies; therefore, describing all eCAL local communication as end-to-end zero-copy would be inaccurate.

### 7. [eProsima/Fast-DDS](https://github.com/eProsima/Fast-DDS)

**Language/role:** C++; DDS/RTPS middleware, included specifically for its shared-memory transport and buffer-management subsystem.

**C1:** buffer descriptors carry segment identity and offsets; buffer validity generations and processing/enqueue counts govern reclamation. Port health checks handle ports left unusable by crashed processes. **C2:** the SHM implementation plugs into the general transport interface and configurable DDS participants. **C3:** distributing descriptors through shared ring-buffer ports lets multiple participants access one payload allocation instead of copying it separately through network transports.

The [official SHM transport guide](https://fast-dds.docs.eprosima.com/en/latest/fastdds/transport/shared_memory/shared_memory.html) explains segments, descriptors, ports, and health checks. [SharedMemManager.hpp](https://github.com/eProsima/Fast-DDS/blob/master/src/cpp/rtps/transport/shared_mem/SharedMemManager.hpp) exposes the atomic validity and lifetime machinery. SHM transport is distinct from Fast DDS's separately documented data-sharing delivery mechanism.

### 8. [dallison/subspace](https://github.com/dallison/subspace)

**Language/role:** C++ and Rust clients; shared-memory publish/subscribe with a control server and optional network bridges.

**C1:** slot membership, payload reference counts, retired/free bitsets, and reliable-subscriber backpressure determine when buffers may be reused. **C2:** clients can read next or newest messages, use shared/weak references, and select reliable or unreliable behavior. **C3:** after setup, the server handles coordination while payload transfer occurs directly through mapped buffers.

The [internals guide](https://github.com/dallison/subspace/blob/main/docs/internals.md) separates system, channel, and buffer control blocks from payload storage. The [shadow-process design](https://github.com/dallison/subspace/blob/main/docs/shadow-process.md) adds a distinctive failure study: companion processes retain channel state and file descriptors so a replacement server can recover them. Client socket connections must still be re-established; this is not disk durability.

### 9. [golems/ach](https://github.com/golems/ach)

**Language/role:** C with C++, Python, Common Lisp, and Java interfaces; message channels designed for real-time robot control.

**Historical study candidate:** GitHub metadata showed its last push in 2021; current maintenance is not asserted.

**C1:** each channel combines a variable-size data ring with a fixed-size index ring. Overwriting old frames, alignment, and sequence progression are explicit invariants, and readers receive a missed-frame status rather than silently assuming lossless delivery. **C2:** arbitrary byte messages and selectable next/newest access serve sensor streams and control loops. **C3:** newest-frame access avoids forcing time-sensitive consumers through an obsolete backlog.

Read the [manual source](https://github.com/golems/ach/blob/master/doc/ach-manual.xml) and the [SPIN model](https://github.com/golems/ach/blob/master/spin/ach.pml), whose assertions cover occupied/free index entries, alignment, and space accounting. The model is evidence of verification effort, not proof of every implementation detail.

## Channels, rings, and process-failure semantics

### 10. [mutouyun/cpp-ipc](https://github.com/mutouyun/cpp-ipc)

**Language/role:** C++; shared-memory routes, channels, and policy-based circular queues for Linux, Windows, and FreeBSD.

**C1:** joining and leaving receivers changes shared connection state while each receiver maintains a cursor; construction and consumption must agree on the selected queue policy. **C2:** single-writer routes, multi-writer channels, configurable read/write combinations, and reusable SHM handles provide more scope than a single SPSC example. **C3:** circular storage and a retry-then-semaphore waiting strategy make the latency-versus-idle-CPU tradeoff visible.

Start at the [queue and connection abstractions](https://github.com/mutouyun/cpp-ipc/blob/master/src/libipc/queue.h) and [circular-element implementation](https://github.com/mutouyun/cpp-ipc/blob/master/src/libipc/circ/elem_array.h). The README documents a receiver-count limit for channels; do not assume arbitrary fan-out or that every path is strictly lock-free.

### 11. [alephzero/alephzero](https://github.com/alephzero/alephzero)

**Language/role:** C transport with C++ APIs; local publish/subscribe, RPC, and progressive RPC.

**Historical study candidate:** last GitHub push observed in 2023. This project is unrelated to similarly named blockchain repositories.

**C1:** the transport keeps committed and working state pages and uses robust synchronization to address process death during updates. The source also contains version-transition logic and unfinished validation work, making it useful to examine the limits of the recovery design. **C2:** a common circular allocation/transport layer supports broadcast, request/reply, streaming replies, and subscriber history selection. **C3:** bounded retained history and futex notification avoid a master process in the message path.

Read [transport.c](https://github.com/alephzero/alephzero/blob/master/src/transport.c) together with the [transport tests](https://github.com/alephzero/alephzero/blob/master/src/test/test_transport.cpp), which exercise allocation/commit, eviction, wraparound, expired positions, resize, and timed waits.

### 12. [Squadrick/shadesmar](https://github.com/Squadrick/shadesmar)

**Language/role:** C++; shared-memory publish/subscribe and RPC with interchangeable copying strategies.

**Status:** explicitly alpha software for Linux/x86; last GitHub push observed in 2022. Treat it as a historical implementation study.

**C1:** readers can lag beyond ring capacity, and slot access must coordinate shared/exclusive locking with payload replacement and reclamation. **C2:** the copier interface separates application allocation and data movement from topic handling. **C3:** the source contains alternative copying implementations using ordinary operations, AVX, streaming stores, and prefetching; studying their placement outside or inside critical sections is more useful than repeating benchmark claims.

Entry points are [topic publication and lag handling](https://github.com/Squadrick/shadesmar/blob/master/include/shadesmar/pubsub/topic.h) and the [copy-strategy implementations](https://github.com/Squadrick/shadesmar/blob/master/include/shadesmar/memory/dragons.h). The inspected topic path copies payloads and uses locks.

### 13. [diwic/shmem-ipc](https://github.com/diwic/shmem-ipc)

**Language/role:** Rust; Linux SPSC shared rings and sealed write-once shared buffers, explicitly considering untrusted peer processes.

**Historical study candidate:** last GitHub push observed in 2022.

**C1:** the mapping code seals against shrinking, and the ring API distinguishes raw-pointer access from unsafe trusted slice access. This makes Rust aliasing assumptions and externally mutable memory central to the design. **C3:** the ring data path is paired with eventfd notification, optional huge pages, and memory locking; callers can integrate the descriptors into their own event loop.

The [shared-ring implementation](https://github.com/diwic/shmem-ipc/blob/master/src/sharedring.rs) documents the sender/receiver contract and notification behavior. [Memory mapping and sealing](https://github.com/diwic/shmem-ipc/blob/master/src/mem.rs) explains why writable mappings and safe immutable references require different treatment. Descriptor exchange is deliberately left to another channel, such as a Unix socket.

### 14. [boonzy00/ringmpsc](https://github.com/boonzy00/ringmpsc)

**Language/role:** Zig; broader channel library, included specifically for its Linux `SharedRing` cross-process SPSC subsystem.

**C1:** attachment checks magic, protocol version, and slot size; reserve/commit and acquire/release operations separate writing payload bytes from publishing them. **C3:** producer and consumer state occupy separate cache regions, peer positions are cached, and cross-process futex operations provide wakeups. The distinction between shared and process-private futexes is especially instructive.

Read [shared_ring.zig](https://github.com/boonzy00/ringmpsc/blob/main/src/primitives/shared_ring.zig) and the [cross-process architecture section](https://github.com/boonzy00/ringmpsc/blob/main/docs/architecture.md#cross-process-sharedring). The broader library's MPSC benchmark numbers should not be attributed to this IPC subsystem. Heartbeat expiry is a liveness heuristic, not proof of death; that limitation follows from the timeout-based design. No C4 claim is made.

## Go, Rust, Python, and .NET application interfaces

### 15. [cloudwego/shmipc-go](https://github.com/cloudwego/shmipc-go)

**Language/role:** Go; shared-memory stream transport using sockets for coordination.

**C1:** mapped buffer lists maintain free-list offsets and concurrent ownership; queue metadata must keep atomic fields correctly aligned across architectures. **C2:** streams expose buffer readers/writers and synchronous/asynchronous integration patterns, allowing applications to adopt SHM without designing their own message queue from scratch. **C3:** shared queues carry buffer offsets, and batching reduces the number of synchronization calls required to deliver multiple requests.

The [buffer manager](https://github.com/cloudwego/shmipc-go/blob/main/buffer_manager.go) exposes size-class lists and mapping ownership. The [queue implementation](https://github.com/cloudwego/shmipc-go/blob/main/queue.go) shows the paired send/receive mappings, producer/consumer counters, and peer-working flag. The README's large-payload motivation is more generalizable than its machine-specific benchmark numbers.

### 16. [cloudwego/shmipc-rs](https://github.com/cloudwego/shmipc-rs)

**Language/role:** Rust; a substantive implementation of the CloudWeGo SHM transport family, rather than a generated wrapper around the Go repository.

Study the portability and negotiation boundary. **C1:** the queue chooses legacy or aligned shared layouts according to protocol version and architecture; protocol negotiation validates supported wakeup modes and polling intervals. **C2:** sessions and streams expose the transport through Rust APIs, including an explicit distinction between streaming chunks and exact contiguous reads. **C3:** batching and selectable eventfd/polling coordination expose different CPU and wakeup costs.

Entry points are [queue layout and mapping](https://github.com/cloudwego/shmipc-rs/blob/main/src/queue.rs) and [protocol negotiation](https://github.com/cloudwego/shmipc-rs/blob/main/src/protocol/negotiation.rs). The README preserves legacy V2/V3 defaults and makes V4 opt-in; exact contiguous reads may coalesce into owned memory. Do not infer universal cross-version interoperability or zero-copy for every read.

### 17. [alex-petrenko/faster-fifo](https://github.com/alex-petrenko/faster-fifo)

**Language/role:** C++ queue core with Cython/Python API; shared-memory alternative to Python's multiprocessing queue.

**C1:** bounded byte capacity, message count, wraparound, timed waits, and competing producers/consumers interact in the native implementation. Both mutexes and condition variables are initialized for process sharing. **C2:** arbitrary serialized Python objects and customizable serializers retain a familiar queue interface. **C3:** `put_many` and `get_many` amortize locking across batches; this provides a concrete performance mechanism rather than relying on a lock-free label.

Start with [faster_fifo.cpp](https://github.com/alex-petrenko/faster-fifo/blob/master/cpp_faster_fifo/cpp_lib/faster_fifo.cpp) and the [Python test suite](https://github.com/alex-petrenko/faster-fifo/blob/master/cpp_faster_fifo/tests/test_faster_fifo.py). Serialization and copying remain part of this design. The repository's release notes also discuss spawn compatibility and receive-buffer/threading fixes, but no age-based C4 claim is needed here.

### 18. [justinstenning/SharedMemory](https://github.com/justinstenning/SharedMemory)

**Language/role:** C#; mapped buffers, shared arrays, multi-reader/multi-writer circular buffers, and a bidirectional RPC layer.

**C1:** separate reservation and completion positions let writers claim slots before making contiguous completed nodes readable; `Interlocked.CompareExchange` and event handles coordinate access and waiting. **C2:** a common mapped-buffer base supports arrays, raw structure transfer, ring buffers, and RPC fragmentation. **C3:** the fixed-node design makes capacity, packet sizing, and the cost of splitting large RPC messages explicit.

Read [CircularBuffer.cs](https://github.com/justinstenning/SharedMemory/blob/main/SharedMemory/CircularBuffer.cs) and [its tests](https://github.com/justinstenning/SharedMemory/blob/main/SharedMemory.Tests/CircularBufferTests.cs). The README discusses older .NET compatibility, but the presence of .NET Standard targets alone should not be treated as proof that named mappings and synchronization work identically on every operating system.

## JVM messaging and mapped logs

### 19. [aeron-io/aeron](https://github.com/aeron-io/aeron)

**Language/role:** Java and C with C++ client support; messaging system included for its shared-memory IPC publications and media-driver coordination.

**C1:** publisher limits depend on subscriber positions; stalled publication recovery, untethered subscribers, and log-buffer reuse form a substantial state machine. **C2:** a common publication/subscription API supports IPC alongside other transport modes. **C3:** shared log buffers separate payload access from driver control, while explicit flow control prevents unchecked overwriting.

The [IpcPublication implementation](https://github.com/aeron-io/aeron/blob/master/aeron-driver/src/main/java/io/aeron/driver/IpcPublication.java) is a focused route into these mechanisms. **C4:** the [changelog](https://github.com/aeron-io/aeron/blob/master/CHANGELOG.adoc) spans releases from 2015 to 2026 and documents client compatibility fixes, sanitizer support, and JDK test-matrix updates. Archive and Cluster are substantial adjacent subsystems, but their distributed features are not the reason for inclusion here.

### 20. [OpenHFT/Chronicle-Queue](https://github.com/OpenHFT/Chronicle-Queue)

**Language/role:** Java; brokerless messaging through persisted memory-mapped queue files shared between JVMs.

This broadens the category beyond ephemeral rings. **C1:** writers coordinate through a process-aware mapped lock with timeout and dead-owner recovery policies, while independent readers track positions in rolled files. **C2:** appenders, tailers, random seeks, and cycle/sequence indexes support event logs, replay, and process-to-process messaging. **C3:** off-heap mappings reduce heap pressure; the indexing guide explicitly warns that cross-cycle counting can touch cold files and harm latency.

Read the [indexing model](https://github.com/OpenHFT/Chronicle-Queue/blob/ea/docs/antora/modules/queue-operations/pages/indexing.adoc) and [TableStoreWriteLock](https://github.com/OpenHFT/Chronicle-Queue/blob/ea/src/main/java/net/openhft/chronicle/queue/impl/single/TableStoreWriteLock.java). Appenders have thread-affinity/lifecycle constraints. Persistence should not be confused with a blanket guarantee against power-loss failure, and commercial replication is outside this selection's scope.

### 21. [fizzed/shmemj](https://github.com/fizzed/shmemj)

**Language/role:** Java APIs with Rust native bindings; portable shared-memory primitives plus a socket-like channel layer.

**Historical study candidate:** last GitHub push observed in 2023.

The channel implementation makes this more than a thin system-call wrapper. **C1:** control metadata carries a magic value, version, peer PIDs, synchronization mode, and buffer sizes. Separate connection/read/write coordination and periodic peer-liveness checks handle timeouts and exited processes. **C2:** users can choose raw shared `ByteBuffer` access or a higher-level client/server channel. **C3:** selectable synchronization behavior and direct mapped buffers expose the overhead of waiting and copying at the Java/native boundary.

The main entry point is [DefaultShmemChannel.java](https://github.com/fizzed/shmemj/blob/master/shmemj-api/src/main/java/com/fizzed/shmemj/DefaultShmemChannel.java). Its PID-based checks are a concrete failure-handling mechanism, not a general proof of safe recovery from arbitrary corruption.

## Shared-state queues and reconnectable connections

### 22. [simonhf/sharedhashfile](https://github.com/simonhf/sharedhashfile)

**Language/role:** C with a C++ API; mapped shared hash tables, zero-copy IPC queues, and multiplexed process logging.

**Historical study candidate:** last GitHub push observed in 2020. The relevant subsystem is the IPC queue and its shared allocator, not merely the key/value API.

**C1:** offsets, stable identifiers, shared locks, and per-process queue caches must remain consistent as processes exchange ownership of fixed-size queue elements. **C2:** a set of named queues can model free buffers and bidirectional work/result channels over the same shared store. **C3:** transferring an element changes references instead of moving its payload, while batching queue bookkeeping reduces shared-lock traffic.

Read the `shf_q_*` functions in [shf.c](https://github.com/simonhf/sharedhashfile/blob/master/src/shf.c) and the [multi-process queue test](https://github.com/simonhf/sharedhashfile/blob/master/src/test.q.shf.c). Its default `/dev/shm` storage can outlive individual processes but does not survive reboot; this is not equivalent to Chronicle Queue's file-backed persistence.

### 23. [MengRao/tcpshm](https://github.com/MengRao/tcpshm)

**Language/role:** C++ headers; reconnectable client/server message queues with TCP and same-host shared-memory modes.

**C1:** sequence numbers and acknowledgements retain outgoing messages until consumption is acknowledged; reconnecting peers recover the connection identified by their names. The SHM queue additionally manages variable-length records, wrap padding, and cached read positions. **C2:** one connection API exposes allocation/push and front/pop operations over both transports, with configurable server-side connection grouping. **C3:** busy polling, cache-line-sized blocks, and a narrow SPSC design make the latency/CPU tradeoff explicit.

Entry points are [spsc_varq.h](https://github.com/MengRao/tcpshm/blob/master/spsc_varq.h) and the [interface guide](https://github.com/MengRao/tcpshm/blob/master/doc/interface.md). The implementation uses compiler-specific inline-assembly ordering constructs rather than portable C++ atomics. The README explicitly excludes power-loss recovery and multi-operation transactions; its use of “persistent” means process-restart recovery within those limits. Current maintenance is not asserted.

## Coverage, search method, and limitations

Live discovery used more than six distinct formulations, including C++ zero-copy/Boost/iceoryx libraries; Rust lock-free and untrusted-peer IPC; Go shared-memory streams; Java and .NET mapped queues; C robotics and newest-sample IPC; Python multiprocessing alternatives; Flow-IPC arena lending; eCAL transport architecture; and Zig/Nim/Swift IPC plus crash recovery and persistent queues. Later queries repeatedly returned the established candidates and small ring-buffer projects; TCPSHM and RingMPSC's explicit IPC subsystem were the final distinct additions.

Canonical names, default branches, and archive/fork flags were checked through the public GitHub API for the first 21 candidates. GitHub repository pages verified the final two after the anonymous API quota was exhausted. Every retained entry has an independently inspected architecture document, source file, or test source in addition to repository-level evidence. File links use branches observed during research and may change later. The inspected metadata marked none of the first 21 repositories archived or as forks; low-activity repositories are still explicitly identified above. No unofficial mirror or moved-away project is counted as an independent implementation.

Coverage intentionally includes C/C++, Rust, Go, Java, C#, Python-facing code, and Zig; industrial middleware, financial messaging, robotics, and smaller standalone libraries; locked and lock-free designs; cooperative and explicitly untrusted peers; and ephemeral versus file-backed communication. Classic iceoryx and iceoryx2 are retained because their implementations and architectural generations differ. The two CloudWeGo implementations are retained for their language and protocol/layout differences. Bindings and Flow-IPC component repositories are not counted separately.

Excluded are generic in-process queues without a verified IPC subsystem, socket-only IPC, distributed OpenSHMEM/RDMA libraries whose “shared memory” means remote-memory programming, tutorial programs, wrapper-only packages, benchmark collections, and projects whose substantive implementation could not be established. Examples surfaced but not selected include small syscall wrappers and numerous newer SPSC implementations whose coverage overlapped the better-documented entries. This is a selection guide, not an exhaustive inventory or a claim that every listed component is uniformly exemplary. Performance numbers were deliberately omitted: no benchmark or advertised recovery guarantee was independently reproduced.
