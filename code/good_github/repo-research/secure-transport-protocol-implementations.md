# Secure transport protocol implementations

Research date: **2026-10-09**.

This report selects 25 GitHub repositories implementing secure communication protocols: TLS, DTLS, QUIC, SSH, Noise, and SRTP. The emphasis is on protocol engines, connection state, authenticated record processing, concurrency, and integration boundaries. General cryptographic primitive libraries, applications that merely enable HTTPS, thin bindings, VPN administration tools, and protocol specifications without implementations are outside this selection. QUIC implementations belong here because encryption and the TLS handshake are integral to their transport design; Noise and SRTP cover secure channels and protected real-time packets, respectively.

The criteria identify worthwhile engineering study, not a security certification or an assertion that every component is exemplary. Feature statements refer to the linked source or documentation; development branches and released packages can differ.

## Criteria legend

- **C1 — Difficult correctness:** protocol invariants, concurrency, adversarial input, cryptographic state, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces or components supporting different applications, platforms, or execution models.
- **C3 — Performance with structure:** concrete treatment of latency, throughput, allocation, copying, or resource limits within an understandable design.
- **C4 — Sustained evolution:** evidence of evolution over years together with compatibility work, testing, or deliberate complexity management.

## TLS libraries and runtime implementations

### 1. [openssl/openssl](https://github.com/openssl/openssl)

**Language/role:** C; general-purpose TLS/DTLS library, with QUIC also present in the repository. **Official GitHub mirror:** the project explains that its private main repository is automatically mirrored here and that contributions use GitHub pull requests.

Study the separation of handshake semantics from the mechanics of reading, writing, flushing, and retrying I/O. It is a particularly useful large-codebase example of refactoring a security-critical subsystem while retaining shared client/server and TLS/DTLS machinery.

- **C1:** The state-machine design validates a received message against allowed transitions and keeps state changes local to the state-machine component. Separating message-flow state from handshake state makes nonblocking retries an explicit correctness concern.
- **C2:** Shared state-machine infrastructure supports client and server roles and both stream and datagram TLS, with protocol-specific handlers beneath the reusable `libssl` interface. The [state-machine design document](https://github.com/openssl/openssl/blob/master/ssl/statem/README.md) maps these boundaries and explains the duplication it removes.

### 2. [rustls/rustls](https://github.com/rustls/rustls)

**Language/role:** Rust; TLS client/server library.

Study how types can encode evidence that authentication has happened, rather than relying solely on successful return codes. The repository also offers an instructive boundary between protocol logic and interchangeable cryptographic implementations.

- **C1:** The [implementation-security manual](https://docs.rs/rustls/latest/rustls/manual/_01_impl_vulnerabilities/index.html) describes non-copyable verification-marker types required by traffic states. Transitions consume the previous state and a validated TLS message, making skipped checks and inappropriate state reuse harder to express.
- **C2:** Client/server configurations use a cryptographic-provider abstraction, allowing the protocol implementation to serve different platform and algorithm requirements. Synchronous stream helpers and asynchronous integrations illustrate reuse across execution models. Start with the repository's provider overview and the [manual index](https://docs.rs/rustls/latest/rustls/manual/index.html). The inspected manual documents a released version, while the repository describes newer API evolution.

### 3. [aws/s2n-tls](https://github.com/aws/s2n-tls)

**Language/role:** C99; TLS library with selectable underlying cryptographic libraries.

Study a systematic C coding discipline built around bounded buffers, shallow control flow, and explicit connection state. The implementation is especially useful for understanding how a team can make review conventions concrete in reusable code.

- **C1:** Table-driven handshake dispatch, checked memory operations, and `s2n_stuffer` read/write cursors address message ordering and buffer bounds. Negative tests deliberately tamper with records and attempt to overfill buffers.
- **C2:** Blob/stuffer abstractions centralize serialization and memory handling; opaque connection/configuration objects and POSIX-like blocking or nonblocking I/O support embedding in different applications. The [development guide](https://github.com/aws/s2n-tls/blob/main/docs/DEVELOPMENT-GUIDE.md) explains both layers and their invariants. It also explains reuse of a handshake buffer because the handshake alternates sending and receiving.

### 4. [Mbed-TLS/mbedtls](https://github.com/Mbed-TLS/mbedtls)

**Language/role:** C; configurable TLS/DTLS and X.509 library suitable for constrained systems.

Study how compile-time specialization interacts with an explicit TLS 1.3 state machine. This is a useful comparison with libraries that make most decisions at runtime.

- **C1:** Handshake handlers separate coordination, fetching, parsing, post-processing, and state changes. Pending output is flushed between handlers, so outbound key changes cannot accidentally strand data under the wrong key. Read retries preserve the current state.
- **C2:** TLS versions and key-exchange modes can be selected independently; PSK-only configurations can omit certificate/signature paths. The [TLS 1.3 architecture document](https://github.com/Mbed-TLS/mbedtls/blob/development/docs/architecture/tls13-support.md) connects these configuration choices to code organization and records the parser/writer conventions used to reduce bounds and byte-order mistakes.

### 5. [wolfSSL/wolfssl](https://github.com/wolfSSL/wolfssl)

**Language/role:** C; portable TLS/DTLS implementation spanning embedded and conventional operating systems.

Study the integration surface needed when standard allocation, files, sockets, and operating-system services cannot be assumed. Its extensive configuration also makes it useful for studying interactions among security-sensitive feature combinations.

- **C2:** The [portability manual](https://www.wolfssl.com/documentation/manuals/wolfssl/chapter05.html) explains replaceable allocation functions, memory/string operations, filesystem access, and per-context send/receive callbacks. These are substantive adaptation layers for different hosts and transports.
- **C1:** The [changelog](https://github.com/wolfSSL/wolfssl/blob/master/ChangeLog.md) documents concrete failures and fixes involving ChangeCipherSpec ordering, certificate authentication, and session lifetimes. These expose the correctness burden created by optional configurations and different input paths. They are evidence of difficult engineering problems, not grounds for assuming every configuration is safe or equally tested.

### 6. [h2o/picotls](https://github.com/h2o/picotls)

**Language/role:** C; TLS 1.3 protocol implementation with pluggable cryptographic backends.

Study a compact, application-driven handshake API and deliberate control over encrypted-output storage. It is also a useful TLS counterpart to the separately listed picoquic transport.

- **C2:** A shared `ptls_context_t` supplies randomness, key exchanges, cipher suites, and certificate callbacks to connection objects. The handshake consumes supplied input and produces output without owning the application's socket loop.
- **C3:** `ptls_buffer_t` accepts caller-owned storage, using dynamic allocation when necessary. The API exposes record overhead so applications can size packet payloads and avoid extra allocations/copies. The [usage guide](https://github.com/h2o/picotls/wiki/Using-picotls) walks through these buffer, context, and handshake contracts, including partial input consumption.

### 7. [mirleft/ocaml-tls](https://github.com/mirleft/ocaml-tls)

**Language/role:** OCaml; TLS engine and integrations for several schedulers and MirageOS.

Study a functional protocol engine in which the data flow is visible in function arguments and results. This offers a substantial architectural contrast with mutable connection objects and callback-driven C libraries.

- **C1:** `Tls.Engine.state` and explicit result variants represent continuation, alerts, EOF, and failure. Processing input yields a new state and separate network/application outputs, making failure propagation and state evolution visible.
- **C2:** The core performs no I/O and is independent of schedulers. Separate integrations serve Lwt, Async, Eio, Miou, and MirageOS; the [architecture document](https://github.com/mirleft/ocaml-tls/blob/main/design.md) explains the functional boundary and protocol layering. Its older illustrative types should be read alongside the current repository's integration overview.

### 8. [bcgit/bc-java](https://github.com/bcgit/bc-java)

**Language/role:** Java; the **`tls` subsystem** provides a TLS implementation and JSSE provider within the wider Bouncy Castle monorepo. **Official GitHub mirror**, identified as such by the repository.

Study how one protocol implementation can support both a standalone API and the Java platform's security-provider contracts. Count the monorepo once; the unrelated OpenPGP, CMS, and other modules are not the basis for this entry.

- **C1:** [`ProvTlsServer`](https://github.com/bcgit/bc-java/blob/main/tls/src/main/java/org/bouncycastle/jsse/provider/ProvTlsServer.java) connects cipher-suite selection to usable credentials, enforces group-size requirements, and rejects an application-protocol selection absent from the client's offer.
- **C2:** The same class bridges a general `DefaultTlsServer`/cryptographic-context model to JSSE key managers, SSL parameters, and connection sessions. These are reusable platform-integration abstractions rather than a wrapper that delegates the entire handshake to another TLS implementation.

### 9. [erlang/otp](https://github.com/erlang/otp)

**Language/role:** Erlang, with native cryptographic support; the **`lib/ssl` subsystem** implements TLS/DTLS inside the Erlang/OTP monorepo.

Study secure transport in a process-oriented runtime: accepting a socket, assigning connection work, and delivering application data are part of the concurrency contract.

- **C1:** The [TLS 1.3 handshake source](https://github.com/erlang/otp/blob/master/lib/ssl/src/tls_handshake_1_3.erl) explicitly rejects a second HelloRetryRequest and constructs certificate-verification and Finished data from handshake history. These are protocol-state and transcript invariants.
- **C2:** The [SSL API guide](https://www.erlang.org/doc/apps/ssl/using_ssl.html) separates transport acceptance from handshaking so a dedicated Erlang process can handle each connection. It also explains TCP-to-TLS upgrades, active-message delivery, and handshake timeouts; the warning about delivering handshake bytes to the wrong process makes the abstraction's ownership requirements concrete.

## QUIC transport implementations

### 10. [cloudflare/quiche](https://github.com/cloudflare/quiche)

**Language/role:** Rust, with a C API and TLS integration; QUIC and HTTP/3 implementation.

Study a low-level packet engine whose application owns sockets and timers. Within this repository, the QUIC transport and HTTP/3 layer are distinct study targets, not separate repository entries.

- **C2:** Connection/configuration objects expose packet input/output and multiplexed streams while leaving the event loop to the caller. HTTP/3 is layered on the transport rather than being the only application protocol it can carry.
- **C3:** Per-packet pacing timestamps let applications schedule transmission instead of emitting bursts; buffer-factory and buffer-splitting interfaces support avoiding copies. The [crate API documentation](https://docs.rs/quiche/latest/quiche/) explains these contracts, congestion-control selection, and the need to configure application-appropriate flow-control limits.

### 11. [quinn-rs/quinn](https://github.com/quinn-rs/quinn)

**Language/role:** Rust; asynchronous QUIC stack with a separately reusable deterministic protocol core.

Study the boundary between `quinn-proto`, which models the protocol, and the asynchronous user-facing stack. Explicit time and packet inputs make this a particularly clear design for reproducible network testing.

- **C2:** [`quinn-proto/src/lib.rs`](https://github.com/quinn-rs/quinn/blob/main/quinn-proto/src/lib.rs) documents an engine without networking or operating-system-derived protocol timestamps. `Endpoint` dispatches datagrams, while `Connection` owns stream and connection state, enabling integration with other event loops.
- **C1:** The [protocol tests](https://github.com/quinn-rs/quinn/blob/main/quinn-proto/src/tests/mod.rs) exercise certificate rejection, congestion windows, high-latency handshakes, 0-RTT acceptance/rejection, and buffering limits that force retransmission. These provide concrete entry points into coupled authentication, transport, and resource invariants.

### 12. [microsoft/msquic](https://github.com/microsoft/msquic)

**Language/role:** Primarily C; cross-platform QUIC library exposed through several language interfaces.

Study a QUIC library that owns scheduling and delivers application events through callbacks. Its execution model is a useful contrast with the caller-driven engines elsewhere in this report.

- **C1:** A connection and its streams execute on only one thread at a time, even if ownership moves between workers. API calls made from callbacks run inline to avoid deadlock; recursive callbacks are normally suppressed.
- **C3:** Workers align with processors and receive-side scaling, and the design discusses the latency/throughput tradeoff of sharing or separating datapath and protocol threads. The [execution-model document](https://github.com/microsoft/msquic/blob/main/docs/Execution.md) explains these guarantees and why long application callbacks delay protocol progress. The [architecture document](https://raw.githubusercontent.com/microsoft/msquic/main/docs/Architecture.md) maps the platform, TLS, crypto, and datapath boundaries.

### 13. [ngtcp2/ngtcp2](https://github.com/ngtcp2/ngtcp2)

**Language/role:** C transport library, with C++ examples; IETF QUIC with adapters for multiple TLS implementations.

Study the exact interface between QUIC and TLS: traffic-secret installation, CRYPTO data, interrupted handshakes, and connection lifetimes. This is useful when embedding a transport in an existing networking stack.

- **C1:** The [programmer's guide](https://nghttp2.org/ngtcp2/programmers-guide.html) distinguishes handshake completion from peer confirmation and documents connection-ID routing, path restrictions during handshake, and TLS-object lifetime obligations.
- **C2:** Callback tables and crypto-helper adapters isolate event delivery and TLS-provider integration from the transport core.
- **C3:** The same guide explains pacing, stream-level backpressure, and aggregation into GSO-compatible packet batches. These optimizations have explicit buffer and scheduling contracts rather than relying on an unsupported throughput claim.

### 14. [private-octopus/picoquic](https://github.com/private-octopus/picoquic)

**Language/role:** C; QUIC transport library using picotls for TLS.

Study a transport explicitly organized for conformance testing and network simulation, including migration/path state and the distinction between public and internal APIs.

- **C1:** A QUIC context requires serialized API access; callers may parallelize separate contexts. Time is supplied by the caller, enabling virtual-time network simulations rather than tests dependent on wall-clock timing.
- **C3:** Packet preparation evolved from per-connection, single-packet output to per-context output that can produce batches for UDP GSO. The [architecture document](https://github.com/private-octopus/picoquic/blob/master/doc/architecture.md) explains the application/network boundaries, optional logging, and handling of unreachable destinations.
- **C4:** That document traces the 2017–2020 specification/interoperability work and subsequent performance focus, with continuing interop tests and a stated stable-public/changing-internal API distinction.

### 15. [quic-go/quic-go](https://github.com/quic-go/quic-go)

**Language/role:** Go; QUIC transport and HTTP/3 implementation.

Study how multiplexed transport semantics fit Go's familiar readers, writers, goroutines, contexts, and cancellation without pretending a whole QUIC connection is one byte stream.

- **C1:** The [stream guide](https://quic-go.net/docs/quic/streams/) distinguishes graceful FIN from reset, independent send/receive closure, stream-limit accounting, and races between cancellation error codes. These are observable protocol semantics with consequences for application correctness.
- **C2:** Separate send, receive, and bidirectional stream interfaces support different application protocols and concurrency patterns.
- **C3:** The [optimization guide](https://quic-go.net/docs/quic/optimizations/) describes GSO batching with a fallback path, socket-buffer constraints, and path-MTU probing. It explains both the system-call cost being addressed and the packet-size constraints imposed by batching.

### 16. [aiortc/aioquic](https://github.com/aiortc/aioquic)

**Language/role:** Python with a C cryptographic extension; QUIC, HTTP/3, and a TLS 1.3 handshake implementation.

Study a readable high-level protocol implementation that isolates its hot cryptographic operations. Its own TLS handshake logic makes this substantially more than an asyncio wrapper over another QUIC library.

- **C2:** QUIC and HTTP/3 follow an I/O-independent design, allowing different concurrency models and deterministic inputs for tests. TLS operates on handshake messages and exposes traffic secrets needed by QUIC.
- **C3:** Packet-header protection and payload encryption run in a C extension linked to OpenSSL because these operations occur for every packet. The [design document](https://aioquic.readthedocs.io/en/latest/design.html) explains this division. Its historical motivation concerning other TLS libraries' APIs should not be treated as a current compatibility survey.

## SSH transport and channel implementations

### 17. [openssh/openssh-portable](https://github.com/openssh/openssh-portable)

**Language/role:** C; official portable OpenSSH client, server, and associated tools. This is the substantive portability project for OpenBSD's implementation, not an unrelated fork.

Study SSH across an operating-system security boundary, including how protocol state survives transitions between authentication and session processes.

- **C1:** The [privilege-separation design](https://github.com/openssh/openssh-portable/blob/master/README.privsep) describes a restricted privileged monitor, sandboxed network-facing authentication code, constrained RPC ordering, and serialization/transfer of authenticated connection state.
- **C4:** The [release history](https://www.openssh.org/releasenotes.html) documents years of protocol hardening, algorithm deprecation, portability work, and explicitly signaled incompatibilities. Examples include strict key exchange in the 2023 releases and further process/security changes in later releases. The portable layer also supplies missing OpenBSD APIs and operating-system-specific sandbox/authentication integration.

### 18. [libssh2/libssh2](https://github.com/libssh2/libssh2)

**Language/role:** C; embeddable SSH2 client library.

Study how a C API preserves partial protocol progress across nonblocking calls. It is a useful counterpart to OpenSSH's application/process architecture and to the higher-level asynchronous libraries below.

- **C1:** [`src/transport.c`](https://github.com/libssh2/libssh2/blob/master/src/transport.c) tracks partially processed packets and payload ownership across `EAGAIN`. During rekeying it redirects packet processing back into key exchange while guarding against recursive re-entry.
- **C2:** Session, authentication, channel, and file-transfer interfaces expose the same SSH transport to different embedding applications. The [API documentation index](https://libssh2.org/docs.html) supplies entry points into these subsystems; the transport source shows how their incoming-data paths converge on shared machinery.

### 19. [ronf/asyncssh](https://github.com/ronf/asyncssh)

**Language/role:** Python; asyncio-native SSH client and server implementation.

Study the translation from SSH channels and receive windows to application callbacks and streams. Multiple sessions on one encrypted connection make backpressure and closure semantics central to the design.

- **C1:** The [session/channel API](https://asyncssh.readthedocs.io/en/latest/api.html) specifies half-open behavior after EOF and flow-control notifications when remote windows close or reopen. High/low watermarks regulate when applications should stop producing data.
- **C2:** Reusable client/server session handlers cover commands, shells, forwarding, and other channel types. The same [API reference](https://asyncssh.readthedocs.io/en/latest/api.html) explains protocol callbacks and the higher-level stream model, allowing different application styles on the shared transport.

### 20. [apache/mina-sshd](https://github.com/apache/mina-sshd)

**Language/role:** Java; embeddable SSH client/server library.

Study SSH integrated into an application framework, particularly the division among sessions, channels, forwarding, and configurable networking services. It is not a drop-in operating-system privilege-separation design like OpenSSH.

- **C2:** The [internals guide](https://raw.githubusercontent.com/apache/mina-sshd/master/docs/internals.md) describes interchangeable I/O-service factories and hierarchical property resolution from channel to session to client/server instance.
- **C3:** The [TCP/IP forwarding design](https://github.com/apache/mina-sshd/blob/master/docs/technical/tcpip-forwarding.md) maps forwarding to channel objects and describes bounded memory in transfer handlers: a fixed buffer is fully written before another read begins. This provides a concrete, inspectable backpressure strategy rather than simply describing the library as asynchronous.

## Datagram security and real-time media

### 21. [pion/dtls](https://github.com/pion/dtls)

**Language/role:** Go; native DTLS client/server implementation.

Study handshake flight retransmission, cancellation, and the interaction between datagram protocol state and a connection-style API. The inspected main-branch source contains both DTLS 1.2 and 1.3 paths; this is not a claim that every published major version offers the same features.

- **C1:** The [handshaker tests](https://github.com/pion/dtls/blob/main/handshaker_test.go) inject loss of HelloVerifyRequest messages, check retransmission counts, and exercise slow-server behavior. The implementation must also coordinate concurrent handshake entry and cancellation.
- **C2:** [`conn.go`](https://github.com/pion/dtls/blob/main/conn.go) supplies reusable `Read`/`Write`, deadline, and `HandshakeContext` semantics. It separates version selection from the respective flight state machines and documents that canceling a completed handshake's context does not cancel the established connection.

### 22. [eclipse-californium/californium](https://github.com/eclipse-californium/californium)

**Language/role:** Java; **`scandium-core` DTLS subsystem** within the Californium CoAP monorepo.

Study DTLS where many connections share a server and asynchronous credentials or handshake results must return to the correct connection. The inclusion is based on Scandium's implementation, not merely CoAP's use of encryption.

- **C1:** [`DTLSConnector`](https://github.com/eclipse-californium/californium/blob/main/scandium-core/src/main/java/org/eclipse/californium/scandium/DTLSConnector.java) routes record processing and asynchronous handshake results through per-connection serial executors. It handles bounded job queues, executor rejection, connection removal, and records arriving in a future epoch.
- **C2:** The [Scandium module guide](https://github.com/eclipse-californium/californium/tree/main/scandium-core) documents a configurable connector with PSK, certificate, resumption, and endpoint-context integration. These boundaries allow reuse beyond a single demonstration CoAP server.

### 23. [cisco/libsrtp](https://github.com/cisco/libsrtp)

**Language/role:** C; SRTP/SRTCP packet-protection library for real-time media.

Study security state tied to packet sequence numbers rather than a reliable byte stream. This provides a distinct view of replay protection, multiple senders, and transport-specific key/nonce constraints. It protects media packets; it is not itself a general-purpose handshake protocol.

- **C1:** The [internal stream/policy structures](https://github.com/cisco/libsrtp/blob/main/include/srtp_priv.h) keep replay databases, sequence-related state, direction, and session keys together. The repeated-transmission option explicitly requires identical payloads when a sequence number is reused.
- **C2:** Opaque session and stream abstractions support multiple media sources with separate state and policies. The [implementation overview](https://github.com/cisco/libsrtp/blob/main/README.md) explains protect/unprotect operations, cryptographic backends, out-of-order delivery assumptions, and replay-protection tests.

## Noise secure-channel frameworks

### 24. [mcginty/snow](https://github.com/mcginty/snow)

**Language/role:** Rust; Noise Protocol Framework implementation.

Study a configurable secure-channel state machine where authentication relationships are selected by handshake pattern rather than a fixed TLS certificate workflow. The repository explicitly says it has not received a formal audit; inclusion is for architecture study.

- **C1:** [`HandshakeState`](https://docs.rs/snow/latest/snow/struct.HandshakeState.html) exposes whose turn it is, reports authentication/decryption failure and nonce exhaustion, and is consumed when converted into transport state. This makes phase transitions and failure conditions visible at the API boundary.
- **C2:** Pattern-based construction and swappable cryptographic resolvers support different key arrangements and algorithms. The handshake API offers transport states with either internal nonce tracking or explicit nonce management, providing reusable mechanisms for different enclosing protocols while leaving their security obligations to the caller.

### 25. [rweather/noise-c](https://github.com/rweather/noise-c)

**Language/role:** C; Noise reference implementation. **Historical/reference-study entry:** the inspected [commit history](https://github.com/rweather/noise-c/commits/master) shows its newest visible commit in December 2023. Ongoing maintenance or current-spec completeness is not established here; the repository is not labeled archived in the inspected page.

Study a small, explicit C object model for handshake orchestration, especially the transition from negotiated handshake state into separate send and receive cipher states.

- **C1:** The [HandshakeState API](https://rweather.github.io/noise-c/group__handshakestate.html) distinguishes required reads/writes, failure, split, and completion. It specifies invalid-state handling for fallback and destruction of sensitive state on cleanup.
- **C2:** Protocol-name/identifier construction combines handshake patterns and algorithms behind opaque objects. The same API supports key provisioning, application-driven I/O, and extraction of two transport cipher states, making it more substantive than a one-pattern demonstration.

## Coverage, search method, and limitations

Live discovery used more than six distinct query formulations, including TLS state-machine architecture; QUIC libraries and interoperability; SSH transport/nonblocking internals; embedded TLS/DTLS configuration; Noise handshake implementations; Go DTLS flight handling; Java Scandium concurrency; SRTP replay protection; and functional/runtime implementations in OCaml, Haskell, and Erlang. Additional searches covered Java TLS providers and .NET SSH. The [QUIC working group's implementation inventory](https://github.com/quicwg/quicwg.github.io/blob/main/implementations.md) helped broaden discovery beyond familiar names; retained claims rely on the projects' own sources, not that inventory or popularity metrics.

Every retained repository's GitHub root was opened, and at least one distinct implementation, design, test, or API source was opened and inspected. The selection spans C, Rust, Go, Java, Python, OCaml, and Erlang; small reference engines, embedded libraries, server-scale transports, runtime subsystems, and full SSH applications are represented. Later searches increasingly found additional implementations with already represented designs, bindings, downstream copies, or applications built on these engines. This is a representative selection, not an exhaustive ecosystem census.

Thin QUIC/TLS language bindings, generated wrappers, tutorial servers, awesome-lists, and ordinary HTTPS clients were excluded. General crypto libraries were excluded unless the selected repository itself implements the relevant secure protocol; Bouncy Castle and Erlang/OTP are counted once with their relevant subsystems identified. No downstream fork is counted as an independent implementation. OpenSSL and Bouncy Castle's substantive official GitHub mirrors are explicitly marked. Noise-C's limited recent evolution is disclosed rather than used as evidence for C4.

Some fetched pages are cached and some manuals document earlier releases. In particular, Pion's older retrieved README and newer source view differ during its DTLS 1.3 transition, so the report describes inspected main-branch mechanisms without asserting a current release-support matrix. Source links using branch names can move. No repositories were built, cloned, benchmarked, fuzzed, or independently security-audited in this research. Criterion judgments and suggested study value are grounded engineering inferences from the cited material; test existence is not proof of comprehensive coverage, and performance mechanisms are not comparative benchmark results.
