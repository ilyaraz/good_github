# QUIC and reliable datagram transport libraries

Research date: **2026-10-09**.

This selection covers **26 GitHub repositories** implementing reusable QUIC transports or reliability mechanisms over datagram networks. It includes general QUIC engines, alternative runtime integrations, game transports, ARQ cores, media transport, and delay-sensitive bulk transfer. QUIC's reliable streams and its optional **unreliable** DATAGRAM extension are different delivery mechanisms; inclusion here does not imply that every exposed datagram API retransmits data. HTTP/3 is discussed only where it helps explain the underlying transport library.

The criteria below are engineering judgments grounded in the linked implementation material, rather than security certifications or comparative performance rankings. Repository identities, default branches, and archived status were checked through GitHub's API; source files and documentation were read separately. None of the selected repositories was marked archived at research time. This alone does not establish active maintenance, and notable activity or maturity limitations are called out below.

## Criteria legend

- **C1 — Correctness:** difficult invariants, concurrency, numerical behavior, hostile input, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components that support multiple applications and integration models.
- **C3 — Performance with structure:** concrete latency, throughput, allocation, or resource constraints addressed through an understandable design.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate management of complexity; age alone is insufficient.

## QUIC engines and integration boundaries

### 1. [quinn-rs/quinn](https://github.com/quinn-rs/quinn)

**Rust — asynchronous QUIC library with a deterministic protocol core.** Study how a reusable protocol state machine can be separated from networking and then exposed through an ergonomic asynchronous API. The repository separates `quinn`, `quinn-proto`, and `quinn-udp`.

- **C2:** `quinn-proto` obtains neither packets nor relevant timestamps directly from the operating system. Its `Endpoint` dispatches incoming datagrams while `Connection` owns connection and stream state, permitting custom event loops independently of the higher-level Tokio integration. Start with the [protocol crate's API and architecture comments](https://github.com/quinn-rs/quinn/blob/main/quinn-proto/src/lib.rs).
- **C1:** the [protocol tests](https://github.com/quinn-rs/quinn/blob/main/quinn-proto/src/tests/mod.rs) exercise stateful lifecycle boundaries, including pending incoming connections surviving server-configuration replacement and retry after temporarily disabling a server. These are useful examples of testing invariants across configuration changes rather than only successful transfers.

### 2. [cloudflare/quiche](https://github.com/cloudflare/quiche)

**Rust, with a C API — QUIC and HTTP/3 implementation.** Study application-driven packet processing and how seemingly small recovery bookkeeping components encode transport invariants. This is independent of Google's similarly named QUICHE.

- **C2:** the library leaves sockets and the timer-capable event loop to its caller, while owning packet processing and connection state. The [integration guide in the README](https://github.com/cloudflare/quiche/blob/master/README.md) explains the receive/send/timeout boundary and the Rust/C embedding surface.
- **C1:** [`BytesInFlight`](https://github.com/cloudflare/quiche/blob/master/quiche/src/recovery/bytes_in_flight.rs) distinguishes open and completed periods with outstanding bytes. Its transitions and tests cover adding bytes, saturation when subtracting, idle intervals, and accumulated active duration. This is a focused entry into accounting that informs congestion and transport measurements.

### 3. [ngtcp2/ngtcp2](https://github.com/ngtcp2/ngtcp2)

**C — QUIC transport core with separate TLS integration helpers.** Particularly useful for studying the contract between a transport engine and an application that controls clocks, I/O, and memory lifetimes.

- **C2:** `ngtcp2_conn`, callback tables, settings, and transport parameters provide the core abstraction; crypto helper libraries adapt several TLS implementations. The [programmer's guide](https://github.com/ngtcp2/ngtcp2/blob/main/doc/source/programmers-guide.rst) explains these boundaries in detail.
- **C1:** the same guide specifies that application stream buffers remain alive until acknowledgement callbacks release them, distinguishes graceful stream completion from abrupt shutdown, and defines timer-expiry handling. These are concrete ownership and lifecycle obligations.
- **C3:** its pacing and GSO sections connect send quantum, transmission timestamps, and packet aggregation to reducing UDP syscall overhead. They also explain how flow-control blocking must be handled while building batches. The guide is the best single entry point for all three criteria.

### 4. [private-octopus/picoquic](https://github.com/private-octopus/picoquic)

**C — portable QUIC library and protocol experimentation platform.** Study an architecture intended to support both applications and repeatable network experiments, including migration and multipath work.

- **C1:** callers supply virtual time, allowing the same transport logic to run against a network simulator. A QUIC context and all its connections must be accessed serially; separate contexts can run in parallel. These explicit concurrency and time contracts are documented in the [architecture guide](https://github.com/private-octopus/picoquic/blob/master/doc/architecture.md).
- **C2:** context, connection, path, and stream objects sit between separate application and networking APIs. Applications can use the supplied socket loop or provide another event manager.
- **C4:** that guide describes interoperability-driven development during 2017–2020 and the later performance focus. It also records the evolution from per-connection, single-packet output to context-level batching, while distinguishing the intended stability of the public API from changeable internal structures. This is evidence of managed evolution, not merely an old repository date.

### 5. [h2o/quicly](https://github.com/h2o/quicly)

**C — modular QUIC stack developed primarily for H2O.** A useful study of explicit byte-range accounting and application-controlled stream scheduling.

- **C1:** [`sendstate.h`](https://github.com/h2o/quicly/blob/master/include/quicly/sendstate.h) separately represents acknowledged ranges, pending ranges, bytes sent in flight, and final stream size. It carefully distinguishes the end-of-stream position from byte counts; transfer completion includes acknowledgement of that final position.
- **C2:** the [public header](https://github.com/h2o/quicly/blob/master/include/quicly.h) supplies callbacks for stream creation, closure, time, and datagrams, plus a stream-scheduler interface. The scheduler chooses streams while consulting the engine's ability to send, illustrating a policy/mechanism boundary inside a transport implementation.

### 6. [aiortc/aioquic](https://github.com/aiortc/aioquic)

**Python with native cryptographic operations — QUIC, TLS 1.3, and HTTP/3 library.** Particularly approachable for tracing protocol behavior and understanding why an implementation can combine a high-level language with selected native hot paths.

- **C2:** its [design document](https://github.com/aiortc/aioquic/blob/main/docs/design.rst) separates QUIC and HTTP/3 state from actual I/O, supporting different concurrency models and direct protocol testing.
- **C3:** the same document identifies per-packet header protection and payload encryption as important costs and places those operations in a C extension linked to OpenSSL.
- **C1:** the [changelog](https://github.com/aiortc/aioquic/blob/main/docs/changelog.rst) records fixes for repeated `STOP_SENDING`, anti-amplification accounting, and limits on buffered CRYPTO data and pending path challenges. These are concrete adversarial-state concerns worth tracing into the code.

Activity limitation: the GitHub API reported its latest push as October 2025; this report does not infer ongoing 2026 maintenance from the README's testing claims.

## QUIC at service and platform scale

### 7. [microsoft/msquic](https://github.com/microsoft/msquic)

**C, with language bindings — cross-platform QUIC library that manages execution and I/O.** Study how callback semantics, thread placement, and platform abstractions fit together in a transport intended for broad embedding.

- **C1:** the [execution guide](https://github.com/microsoft/msquic/blob/main/docs/Execution.md) explains that one connection and its streams execute on one thread at a time, although ownership can move between threads. Listener callbacks can run concurrently. It also documents callback reentrancy rules and shutdown notifications needed for safe cleanup.
- **C3:** worker placement follows NUMA and receive-side scaling considerations. Protocol work and application callbacks share execution threads, making callback duration part of transport latency; separate datapath execution offers another throughput tradeoff.
- **C2:** the [architecture guide](https://github.com/microsoft/msquic/blob/main/docs/Architecture.md) separates platform-independent QUIC logic from TLS, crypto, datapath, and operating-system abstractions. The execution guide provides the fuller explanation where the architecture document is incomplete.

### 8. [aws/s2n-quic](https://github.com/aws/s2n-quic)

**Rust — configurable QUIC implementation with extensive verification infrastructure.** Study both dependency substitution and how transport requirements are connected to automated checks. The relevant subsystem is the `quic/` workspace; the monorepo is counted once.

- **C2:** the [provider module](https://github.com/aws/s2n-quic/blob/main/quic/s2n-quic/src/provider.rs) exposes distinct providers for TLS, I/O, connection identifiers, congestion control, limits, events, and other policies. It also makes the distinction between public providers and internal or feature-gated ones visible.
- **C1:** the [CI design](https://github.com/aws/s2n-quic/blob/main/docs/dev-guide/ci.md) describes property testing with Bolero/Kani, concurrency permutation testing with Loom, and packet/UDP-level fuzzing. These target different failure classes rather than treating all verification as one test suite.
- **C3:** the same document explains randomized network simulations, congestion-window recovery plots, flame graphs, and heap profiling. This makes performance behavior inspectable alongside correctness and normative RFC coverage.

### 9. [facebook/mvfst](https://github.com/facebook/mvfst)

**C++ — client/server QUIC transport using Folly-oriented abstractions.** Study how a transport exposes detailed buffer, scheduling, and lifecycle control while supporting server deployment constraints.

- **C3:** the [repository overview](https://github.com/facebook/mvfst/blob/main/README.md) explains its thread-local server architecture, configurable connection-ID routing, restart support, and UDP GSO. Its source-layout guide separates codecs, congestion control, state, client/server transports, and application APIs.
- **C2:** [`QuicSocket`](https://github.com/facebook/mvfst/blob/main/quic/api/QuicSocket.h) exposes connection and stream flow control, stream priorities, peek/consume operations, datagram callbacks, and transport observations. These are substantial application-facing abstractions beyond an HTTP client wrapper.
- **C1:** the header documents callback lifetimes and borrowed data validity, early-data parameter ownership, and graceful closure waiting for streams to become idle. Those contracts are useful starting points for studying asynchronous resource ownership.

### 10. [google/quiche](https://github.com/google/quiche)

**C++ — QUIC transport within Google's broader QUICHE protocol collection. Official synchronized GitHub repository.** The [README](https://github.com/google/quiche/blob/main/README.md) explicitly identifies GitHub and Googlesource as automatically synchronized public repositories. Count the monorepo once; focus here on `quiche/quic/core`, not its separate HTTP/2 machinery.

- **C2:** the [connection interface](https://github.com/google/quiche/blob/main/quiche/quic/core/quic_connection.h) separates connection packet processing from session callbacks for streams, crypto data, flow-control changes, resets, and datagrams. Platform interfaces allow embedding in different host projects.
- **C1:** that interface exposes the complexity of duplicate and temporarily undecryptable packets, address validation and anti-amplification, path state, and multiple closure forms. Its explicit non-thread-safe contract makes external execution ownership part of the design.

Embedding limitation: the README describes platform integration work and little-endian support; this is a large transport toolkit rather than a uniformly drop-in socket replacement.

### 11. [litespeedtech/lsquic](https://github.com/litespeedtech/lsquic)

**C — QUIC and HTTP/3 engine for servers and clients.** Study the engineering tradeoffs of a throughput-oriented engine with both historical and IETF protocol machinery.

- **C2:** the extensive [Library Guts document](https://github.com/litespeedtech/lsquic/blob/master/docs/internals.rst) explains the engine → connection → stream structure, internal interfaces, connection queues, and callbacks.
- **C3:** it describes dynamically sized outgoing batches, coalesced-packet bookkeeping, connection tick scheduling, and promotion from a small initial connection representation to a full connection. These are concrete ways of managing packet-processing and connection costs.
- **C1:** the same discussion places version checks, token verification, connection limits, and retired-identifier handling before new connection creation.

Reading caveat: the internals document explicitly discusses version 2.29.6 and admits that performance sometimes outweighed readability. Use it as an architectural map and compare it with the current source, not as an exact specification of today's implementation.

### 12. [quic-go/quic-go](https://github.com/quic-go/quic-go)

**Go — general QUIC transport and HTTP/3 implementation.** Study how an idiomatic Go library organizes packet-number spaces, loss recovery, and network-facing resource controls.

- **C1:** the [sent-packet handler](https://github.com/quic-go/quic-go/blob/master/internal/ackhandler/sent_packet_handler.go) keeps separate Initial, Handshake, and application-data histories, tracks peer address validation, and manages probe-timeout backoff. The anti-amplification limit and treatment of spurious losses make protocol safety and recovery policy visible together.
- **C3:** the same component reuses acknowledged-packet storage to avoid allocations and expresses its time-based loss threshold using integer units rather than floating-point arithmetic. Congestion, RTT, logging, and packet history are distinct collaborators.
- **C2:** the [repository overview](https://github.com/quic-go/quic-go/blob/master/README.md) identifies its reusable QUIC transport, HTTP/3 support, and separate projects built above it, including WebTransport. The transport is useful independently of those higher layers.

### 13. [mozilla/neqo](https://github.com/mozilla/neqo)

**Rust with NSS — Firefox's QUIC transport, HTTP/3, and QPACK libraries.** Study typed protocol state and the boundary between a browser transport and its TLS backend.

- **C2:** the [transport crate](https://github.com/mozilla/neqo/blob/main/neqo-transport/src/lib.rs) exposes connection output, events, stream identifiers, datagram queue behavior, statistics, and transport parameters while separating packet, crypto, path, flow-control, and recovery modules.
- **C1:** that API distinguishes errors such as acknowledging an unsent packet, invalid migration, exhausted keys, and blocked key updates. The compact [recovery-token definitions](https://github.com/mozilla/neqo/blob/main/neqo-transport/src/recovery/token.rs) separately represent stream data, control frames, crypto, acknowledgements, and MTU probes—an informative model for associating packet outcomes with the state that produced them.

Maturity limitation: the repository explicitly calls the server experimental and unsuitable for production use; Firefox's client deployment should not be generalized to server readiness.

## Additional QUIC communities and design choices

### 14. [alibaba/xquic](https://github.com/alibaba/xquic)

**C — client/server QUIC and HTTP/3 library with multipath work.** Study how a library serves mobile and server integrations without owning the application's event loop.

- **C2:** the [transport API guide](https://github.com/alibaba/xquic/blob/main/docs/API.md) separates engine callbacks from connection callbacks, and further separates common transport callbacks from ALPN-specific application-protocol callbacks. This allows a new application protocol to reuse the transport integration.
- **C3:** the guide explains individual-packet and `sendmmsg` batch callbacks, including configuration needed to enable batching. Timestamp and timer callbacks let the embedding application supply its own timing mechanism while the engine determines when work is due.
- **C1:** the engine must outlive all dependent connections, and the application must reinvoke engine logic when the requested timer expires. These lifecycle obligations provide a concrete starting point for investigating missed-timer and shutdown failures.

### 15. [Tencent/tquic](https://github.com/Tencent/tquic)

**Rust with Rust/C/C++ interfaces — QUIC library with multipath and configurable congestion control.** Useful for comparing callback-oriented Rust embedding with future-oriented APIs elsewhere in this list.

- **C2:** the [public API source](https://github.com/Tencent/tquic/blob/develop/src/lib.rs) separates `TransportHandler`, which receives connection/stream events, from `PacketSendHandler`, which sends batches. This gives applications control of I/O without making them implement transport state.
- **C1:** those interfaces specify that connection and stream objects cease to be accessible after their closure callbacks, and that partially sent packet batches must be retried. The same source defines bounded connection identifiers, ACK-range limits, and anti-amplification accounting constants.
- **C3:** the [project overview](https://github.com/Tencent/tquic/blob/develop/README.md) identifies selectable CUBIC, BBR, BBRv3, and COPA controllers and multipath support. Together with batch I/O, these provide distinct congestion and path-policy study targets; no benchmark superiority is assumed here.

### 16. [ptrd/kwik](https://github.com/ptrd/kwik)

**Java — independently implemented QUIC client/server library.** Study QUIC recovery expressed through Java concurrency primitives and an injectable clock, rather than through a native-code binding.

- **C1:** [`LossDetector`](https://github.com/ptrd/kwik/blob/master/core/src/main/java/tech/kwik/core/recovery/LossDetector.java) combines a concurrent ordered packet log, atomic in-flight counts, volatile state, and synchronization preventing new sends during reset. It separates RTT estimation, congestion control, and loss callbacks.
- **C4:** the [2023–2026 changelog](https://github.com/ptrd/kwik/blob/master/CHANGELOG.md) records stream-state and final-size fixes, flow-control enforcement, interoperability changes, Maven/module compatibility, and later recovery/path work. This is sustained compatibility and correctness evolution with specific examples.

Limitations: the README says server migration and application-controlled stream priorities remain incomplete, and notes that extreme network conditions and the homegrown TLS integration have not received comprehensive security testing. Its value here is as an independent implementation to study, not an unconditional deployment recommendation.

### 17. [kazu-yamamoto/quic](https://github.com/kazu-yamamoto/quic)

**Haskell — QUIC library built around lightweight threads.** Adds a useful functional-language and software-transactional-memory perspective to an ecosystem dominated by C-family languages and Rust.

- **C1:** the [loss-recovery implementation](https://github.com/kazu-yamamoto/quic/blob/main/Network/QUIC/Recovery/LossRecovery.hs) combines STM-managed congestion state with per-encryption-level packet histories and atomic reference updates. It handles discarded packet-number spaces, newly acknowledged packets, RTT sampling, and address-validation-dependent probe-timeout reset.
- **C2:** the [main API module](https://github.com/kazu-yamamoto/quic/blob/main/Network/QUIC.hs) provides bidirectional/unidirectional streams, independent shutdown/reset operations, datagram operations including an STM variant, and synchronization points for 0-RTT, 1-RTT, and established connections.

Integration caveat: the documented Windows requirement for the native I/O manager is substantive—the alternate manager prevents asynchronous exceptions from delivering the timeouts on which handshake progress relies.

## Reliable UDP for games and general applications

### 18. [lsalzman/enet](https://github.com/lsalzman/enet)

**C — message-oriented reliable UDP library.** A compact architectural comparison with QUIC when the application needs channels, sequencing, and retransmission without a full encrypted QUIC stack.

- **C2:** the [design document](https://github.com/lsalzman/enet/blob/master/docs/design.dox) explains independently sequenced channels, optional reliable delivery, connection monitoring, and transparent fragmentation/reassembly. Separate channels prevent a missing reliable packet in one channel from stalling another.
- **C3:** the same document connects command aggregation, in-flight windows, bandwidth allocation, and dynamic throttling to packet overhead and network capacity.
- **C4:** the [2007–2024 changelog](https://github.com/lsalzman/enet/blob/master/ChangeLog) documents sequence-overflow compatibility issues, reliable-window fixes, packet-size limits, RTT changes, and MTU negotiation corrections. It is unusually useful evidence of the edge cases discovered over a transport library's lifetime.

### 19. [skywind3000/kcp](https://github.com/skywind3000/kcp)

**C — embeddable ARQ algorithm, commonly carried over UDP.** Study the minimum transport machinery needed for selective retransmission, window management, and externally scheduled progress.

- **C2:** the [English integration documentation](https://github.com/skywind3000/kcp/blob/master/README.en.md) describes a core with no built-in socket operations or clock acquisition. The application supplies packet output and time, making KCP usable inside different network/session layers.
- **C1:** [`ikcp.c`](https://github.com/skywind3000/kcp/blob/master/ikcp.c) exposes wire-length and command checks, conversation-ID validation, wrap-aware time differences, cumulative/selective acknowledgement processing, and retransmission state in one tractable implementation.
- **C3:** fast retransmit, update intervals, window sizes, and congestion behavior expose a real latency/bandwidth tradeoff. Treat the README's numerical TCP comparisons as project claims, not general benchmark results; they are not used to justify this selection.

KCP supplies an ARQ core, so an embedding application still needs its own session and security design.

### 20. [xtaci/kcp-go](https://github.com/xtaci/kcp-go)

**Go — substantial KCP implementation and UDP session layer with FEC.** Retained separately from the C core because its session management, packet-processing pipeline, and runtime optimizations provide distinct implementation material.

- **C2:** [`sess.go`](https://github.com/xtaci/kcp-go/blob/master/sess.go) layers stream delivery over KCP, FEC, checksum/encryption processing, and transmission queues. `UDPSession` integrates `net.PacketConn`, connection ownership, deadlines, and read/write notification channels.
- **C1:** session closure and socket-error notification use once-only coordination and atomic state; the documented pipeline shows where data is transformed before it reaches the ARQ core.
- **C3:** the [design discussion](https://github.com/xtaci/kcp-go/blob/master/README.md#key-design-considerations) explains slice locality, clock-query costs, shared packet-buffer pools, and packet clocking. Those tradeoffs are more informative than its headline benchmark numbers.

Security limitation: its own documentation discusses replay attacks and the need for authentication in an upper layer. Packet encryption here should not be equated with QUIC's TLS-based authenticated transport.

### 21. [ValveSoftware/GameNetworkingSockets](https://github.com/ValveSoftware/GameNetworkingSockets)

**C++ — reliable and unreliable message transport over UDP.** Study a game-oriented protocol that separates message segments from the packets carrying them.

- **C1:** the [SNP wire-format specification](https://github.com/ValveSoftware/GameNetworkingSockets/blob/master/src/steamnetworkingsockets/clientlib/SNP_WIRE_FORMAT.md) explicitly allows apparently lost packets to arrive after negative acknowledgement. Correctness therefore requires handling unnecessary retransmission safely, while retaining enough packet/segment history to infer delivery.
- **C3:** the same specification explains run-length-encoded acknowledgement information, compact relative message/stream positions, and mixed reliable/unreliable segments. These are understandable mechanisms for reducing small-message overhead.
- **C2:** the [repository overview](https://github.com/ValveSoftware/GameNetworkingSockets/blob/master/README.md) describes a connection-oriented, message-oriented API with fragmentation/reassembly, reliability choices, and peer-to-peer support. It is a reusable transport layer rather than a game-state replication engine.

### 22. [RevenantX/LiteNetLib](https://github.com/RevenantX/LiteNetLib)

**C# — managed reliable UDP library for .NET/Mono applications.** Study packet lifetime management and multiple delivery policies under a managed runtime.

- **C1:** [`ReliableChannel`](https://github.com/RevenantX/LiteNetLib/blob/master/LiteNetLib/ReliableChannel.cs) validates acknowledgement sizes and window positions, compares wrapped sequence numbers, locks pending-packet state, and distinguishes ordered delivery from unordered duplicate tracking.
- **C3:** that implementation uses bounded pending arrays, packet pooling, retransmission timestamps, and small-packet merging within MTU limits. The data structures make the allocation/packet-overhead tradeoffs directly inspectable.
- **C2:** the [README](https://github.com/RevenantX/LiteNetLib/blob/master/README.md) documents multiple channels and reliable ordered, reliable unordered, reliable sequenced, and unreliable modes. Reliable sequenced delivery concerns the newest packet rather than delivery of every historical update.

Version caveat: the current default branch describes LiteNetLib 2, links the older 1.x branch, and explicitly warns that `master` can be unstable.

### 23. [mas-bandwidth/yojimbo](https://github.com/mas-bandwidth/yojimbo)

**C++ — client/server game transport with typed messages and reliable channels.** Study the relationship between application messages, packet acknowledgements, and large block transfers. This is the verified current repository identity, rather than an independently counted older owner alias.

- **C2:** the [reliable ordered channel implementation](https://github.com/mas-bandwidth/yojimbo/blob/main/source/yojimbo_reliable_ordered_channel.cpp) composes an allocator, message factory, configurable channel, sequence buffers, packet-to-message mappings, and block-fragment state. These are reusable abstractions with explicit resource limits.
- **C1:** its sequence-buffer divisibility assertions expose wraparound assumptions. The [fuzzing guide](https://github.com/mas-bandwidth/yojimbo/blob/main/fuzz/README.md) adds both raw-parser fuzzing and structured sender/receiver scripts that generate valid traffic under packet loss, reaching stateful reassembly paths that random bytes rarely reach.

Scope limitation: the README assumes a single-threaded client/server model, matching configuration on both sides, and games with at most roughly 100 players. Treat those as intended design bounds.

### 24. [holepunchto/libudx](https://github.com/holepunchto/libudx)

**C with libuv — multiplexed, congestion-controlled reliable streams over UDP.** A less prominent implementation worth studying for the link between write ownership, backpressure, and acknowledgement processing.

- **C1:** [`udx.c`](https://github.com/holepunchto/libudx/blob/main/src/udx.c) checks that acknowledged bytes do not exceed in-flight or queued bytes, distinguishes cancellation from acknowledgement, and manages stream/socket closure through reference counts and callbacks. Selective-acknowledgement structures track received data.
- **C3:** send capacity is bounded by both congestion and receiver windows. Queued-write high-watermark transitions generate drain callbacks, connecting transport capacity directly to application backpressure.
- **C2:** the [public header](https://github.com/holepunchto/libudx/blob/main/include/udx.h) separates sockets, streams, write requests, and callback types; its explicit stream states and MTU machinery are useful entry points into the libuv integration.

## Media and bulk-transfer reliability policies

### 25. [Haivision/srt](https://github.com/Haivision/srt)

**C++ with a C API — Secure Reliable Transport for live media and bulk transfer.** Study how retransmission and delivery policy change when late data can be less useful than missing data. SRT has UDT ancestry but is a substantive evolved transport, not a thin wrapper around UDT.

- **C2:** the [API guide](https://github.com/Haivision/srt/blob/master/docs/API/API.md) explains logical SRT sockets, UDP-socket sharing, blocking/nonblocking operation, and separate live, buffer, and message transfer modes.
- **C1:** socket closure includes deferred cleanup, while live mode enables timestamp-based delivery and late-packet dropping. The API's separation of live and file congestion/retransmission behavior shows why “reliable” cannot mean identical delivery policy in every mode.
- **C3:** the [live-streaming guide](https://github.com/Haivision/srt/blob/master/docs/features/live-streaming.md) relates packet sizing, send pacing, receiver buffering, and media timing. It is a concrete explanation of latency constraints rather than a generic claim that UDP is faster.

### 26. [bittorrent/libutp](https://github.com/bittorrent/libutp)

**C++ with a C interface — uTP reliable ordered byte streams over UDP. Historical study selection.** Especially valuable for delay-based congestion control and the numerical problems introduced by remote timing information.

- **C1:** [`utp_internal.cpp`](https://github.com/bittorrent/libutp/blob/master/utp_internal.cpp) handles wrapped sequence/timestamp spaces, suspicious acknowledgement windows, selective acknowledgement, and clock-drift estimation. It also accounts for local clock irregularities while sampling RTT.
- **C3:** its LEDBAT-related control logic uses delay history and congestion-window adjustment to pursue low additional queueing delay, rather than only maximizing the sender's rate.
- **C2:** the [interface overview](https://github.com/bittorrent/libutp/blob/master/README.md) describes callback-driven reads and writes for event-based integration with limited buffering.

Maintenance/API limitation: GitHub reported the latest push in October 2023, although the repository is not archived. The README explicitly considers the API unstable and the interface non-thread-safe. Include it as a useful implementation study, without implying current maintenance or a stable dependency contract.

## Coverage and search notes

Discovery used more than six distinct formulations, including general QUIC implementations; Rust/C/C++/Go protocol engines; Java/Python and Haskell alternatives; multipath QUIC; game-oriented reliable UDP in C#/C++; KCP and selective-retransmission ARQ; SRT/UDT/uTP congestion control; smaller reliable-stream projects; and Zig/embedded implementations. The [QUIC working group's implementation inventory](https://github.com/quicwg/quicwg.github.io/blob/main/implementations.md) was a discovery aid, followed by repository/API checks and reading project-owned source or documentation. Later broad searches increasingly repeated the retained transport families or surfaced wrappers, application frameworks, and newer implementations requiring a separate assessment.

The final coverage is **17 QUIC repositories and 9 other datagram-based reliability libraries**, spanning eight main implementation languages and large vendor, browser, game, media, and independent-project communities. The list intentionally goes slightly beyond the usual 15–25 guide because the non-QUIC families contribute materially different reliability and congestion designs.

Pure bindings, HTTP/3-only layers, VPN/tunnel applications, WebTransport wrappers, benchmarking tools, tutorials, and resource lists were excluded as entries. Complete servers such as NGINX and HAProxy were not included solely for their internal QUIC support. KCP-Go is retained because it supplies a distinct Go implementation and session/FEC/runtime layer; copied KCP forks are not counted separately. Yojimbo's bundled dependencies are likewise not separately counted. Google's official synchronized GitHub repository is explicitly identified above. RIST was searched, but the surfaced librist material identified VideoLAN's GitLab as canonical; no official substantive GitHub mirror was established during this search.

This is a selection guide, not an exhaustive ecosystem census. Zig stacks and additional Rust game libraries surfaced but were not evaluated to the same primary-source depth as the retained entries. No candidate code was executed, dependencies installed, repositories cloned, or benchmark claims independently reproduced. The linked branch-based files can change after the research date. Criteria assessments identify worthwhile engineering material; they do not imply that every component, supported mode, or historical design choice is uniformly exemplary.
