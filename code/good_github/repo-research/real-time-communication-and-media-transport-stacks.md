# Real-time communication and media transport stacks

Research date: **2026-10-09**.

This selection covers implementations that establish, secure, schedule, recover, route, or process live media transport: WebRTC endpoints, selective forwarding units (SFUs), streaming gateways, RTP/RTCP and RTSP libraries, NAT relays, network audio pipelines, and Media over QUIC. It includes both reusable libraries and substantial servers. General chat applications, thin SDK wrappers, codec-only projects, and offline media tools are outside the focus.

The 25 canonical repository URLs were checked through GitHub's API, and their READMEs and additional implementation or design sources were read. All selected repositories were unarchived at lookup; this status does not establish a maintenance guarantee. GStreamer's official mirror is identified explicitly. Source links follow the branches inspected and can change after this date. The criteria are evidence-grounded selection judgments, and the study suggestions do not imply that every component is uniformly exemplary.

**Criteria legend**

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, hostile input, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and components supporting multiple applications.
- **C3 — Performance:** concrete latency, throughput, memory, or scheduling constraints addressed through an understandable design.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or explicit complexity management.

## WebRTC endpoint implementations

### 1. [pion/webrtc](https://github.com/pion/webrtc)

**Go — embeddable WebRTC implementation.** Study how a browser-shaped PeerConnection API composes transport machinery while leaving media production to the application. Direct RTP/RTCP access makes it useful for gateways, recorders, embedded endpoints, and application-specific servers.

- **C1:** The shutdown tests exercise closure before ICE starts, during connectivity establishment, and during candidate gathering. They check goroutine leakage, bounded completion, and completion of outstanding gathering promises: concrete concurrency and lifecycle obligations. [Shutdown tests](https://github.com/pion/webrtc/blob/main/peerconnection_close_test.go).
- **C2:** The design explicitly separates media transport from media creation, permits external media frameworks, and emphasizes reusable protocol libraries and a familiar public API. [Design document](https://github.com/pion/webrtc/blob/main/DESIGN.md).

### 2. [aiortc/aiortc](https://github.com/aiortc/aiortc)

**Python — asyncio WebRTC/ORTC stack.** A particularly accessible implementation for following the relationship between packet transport, coroutine lifecycles, and frame processing. The repository describes browser interoperability testing and provides both media and data-channel implementations.

- **C1:** Its jitter buffer handles modular sequence numbers, excessive misordering, capacity overflow, and picture-loss signaling. Whole-frame removal prevents partial frames from reaching the decoder. [Jitter-buffer implementation](https://github.com/aiortc/aiortc/blob/main/src/aiortc/jitterbuffer.py).
- **C2:** PeerConnection, sender/receiver, transceiver, and media helper APIs support live capture, recording, processing, and forwarding. The versioned history illustrates how those interfaces interact: it records encoder teardown, bundle policy, transport shutdown, and sending media without transcoding. [Changelog](https://github.com/aiortc/aiortc/blob/main/docs/changelog.rst).

### 3. [paullouisageneau/libdatachannel](https://github.com/paullouisageneau/libdatachannel)

**C++ with C API — native WebRTC data channels and media transport.** Study a transport-focused native library with selectable ICE and TLS backends, independently usable tracks, and composable media handlers.

- **C1:** The NACK responder checks RTCP bounds, maintains synchronized packet storage, and distinguishes plain retransmission from RTX wrapping with negotiated payload-type and SSRC mappings. Its bounded retransmission history exposes ownership and sequence-number concerns clearly. [NACK responder](https://github.com/paullouisageneau/libdatachannel/blob/master/src/rtcpnackresponder.cpp).
- **C2:** The documented C interface exposes tracks, codec packetizers/depacketizers, and chained RTCP handlers. Applications can provide encoded frames and assemble the required transport behavior without adopting a capture or rendering framework. [API guide, media handling](https://github.com/paullouisageneau/libdatachannel/blob/master/DOC.md#media-handling).

### 4. [algesten/str0m](https://github.com/algesten/str0m)

**Rust — WebRTC using a Sans-I/O protocol core.** Study explicit control over sockets, execution, and time. The core creates no networking threads or asynchronous tasks; callers supply input and drain output.

- **C1:** The documented contract requires draining output to a timeout after each mutation. Time is supplied externally, making state progression reproducible. The loss-recovery test injects seeded packet loss and checks retransmission feedback and recovered sequence continuity. [Run-loop and timing contract](https://github.com/algesten/str0m#run-loop), [NACK tests](https://github.com/algesten/str0m/blob/main/tests/nack.rs).
- **C2:** Separating the protocol engine from I/O allows applications to choose synchronous or asynchronous runtimes and multiplex connections in their own event loop. Both SDP-oriented and more direct media control are illustrated in the repository.

### 5. [sipsorcery-org/sipsorcery](https://github.com/sipsorcery-org/sipsorcery)

**C#/.NET — SIP, WebRTC, RTP, and media integration monorepo.** Study how VoIP call control and WebRTC negotiation share a managed communications library while media devices and codecs sit behind separate abstractions. Count the core and its media packages as one repository.

- **C1:** DTLS fingerprint tests require a changed fingerprint to be rejected after handshake completion without applying the rejected remote description. They also distinguish legitimate pre-handshake changes and unchanged-fingerprint renegotiation. [Fingerprint and negotiation tests](https://github.com/sipsorcery-org/sipsorcery/blob/master/test/unit/net/WebRTC/RTCPeerConnectionDtlsFingerprintUnitTest.cs).
- **C2:** The repository separates protocol support, media endpoint abstractions, Windows device support, and FFmpeg integration. This supports softphones, gateways, video endpoints, and other .NET applications with different media backends. [Package and architecture overview](https://github.com/sipsorcery-org/sipsorcery#sipsorcery-repository-overview).

The README declares a modified BSD license with additional use restrictions; engineering inclusion here is separate from suitability for a particular reuse license.

### 6. [elixir-webrtc/ex_webrtc](https://github.com/elixir-webrtc/ex_webrtc)

**Elixir — WebRTC API integrated with OTP processes.** Study a PeerConnection implemented as a GenServer that sends typed transport, track, RTP, RTCP, and data-channel messages to its controlling process. This provides a distinct concurrency model from callback-driven C++ and asyncio implementations.

- **C1:** The jitter buffer explicitly tracks initial waiting and timer state, rejects late packets, releases packets past their latency deadline, and flushes contiguous packets after gaps resolve. [Jitter-buffer implementation](https://github.com/elixir-webrtc/ex_webrtc/blob/master/lib/ex_webrtc/rtp/jitter_buffer.ex).
- **C2:** The PeerConnection API exposes process-oriented lifecycle management and packet-level media interfaces, including simulcast identifiers and transport-wide feedback correlation. These are useful building blocks for custom servers and media processing. [PeerConnection source and API documentation](https://github.com/elixir-webrtc/ex_webrtc/blob/master/lib/ex_webrtc/peer_connection.ex).

## Selective forwarding and plugin-based media servers

### 7. [versatica/mediasoup](https://github.com/versatica/mediasoup)

**C++, TypeScript, and Rust — embeddable SFU with native media workers.** Study the boundary between application-facing control APIs and a C++ media worker. The project deliberately leaves signaling to the application and supports both WebRTC and plain RTP.

- **C2:** Routers, transports, producers, and consumers provide a reusable media graph for conferencing, broadcast, and integration with external RTP tools. Node.js and Rust APIs expose this model. [Repository design goals and architecture](https://github.com/versatica/mediasoup#design-goals).
- **C3:** The congestion-control client connects feedback, pacing, and periodic probing, including probing when a muted or static stream underuses the available network capacity. [Congestion-control implementation](https://github.com/versatica/mediasoup/blob/v3/worker/src/RTC/TransportCongestionControlClient.cpp).
- **C1:** The same implementation documents why bitrate factors use double precision and clamps values before passing them to a dependency's signed 32-bit interface. Numerical interoperability is a visible correctness concern.

### 8. [meetecho/janus-gateway](https://github.com/meetecho/janus-gateway)

**C — general-purpose WebRTC server with media plugins.** Study a stable core/plugin boundary supporting forwarding, streaming, audio bridging, and SIP integration. The inspected main branch is the multistream generation; the README identifies the separate legacy 0.x line.

- **C2:** The plugin interface separates core ICE/DTLS/RTP transport setup from application-specific media behavior. Its callbacks cover media readiness, RTP/RTCP/data delivery, asynchronous requests, slow links, and teardown. [Plugin interface](https://github.com/meetecho/janus-gateway/blob/master/src/plugins/plugin.h).
- **C1:** That interface makes codec negotiation and coherent SDP payload types/versioning explicit plugin responsibilities, with session mappings and transaction identifiers connecting asynchronous work.
- **C4:** The dated changelog spans 2015–2026 and records browser compatibility, race fixes, thread safety, and security corrections. The plugin header also explains API-version checks intended to prevent incompatible modules from loading. [Changelog](https://github.com/meetecho/janus-gateway/blob/master/CHANGELOG.md).

### 9. [livekit/livekit](https://github.com/livekit/livekit)

**Go — distributed WebRTC server built on Pion.** Study the server's substantive SFU and allocation layers above its underlying WebRTC implementation. The relevant subsystem is `pkg/sfu`, rather than the separate agents SDKs promoted in the README.

- **C2:** The server supplies room, participant, and track infrastructure around reusable transport components, while its allocator works with explicit track priorities, downtracks, bandwidth estimators, and pacers. [Server overview](https://github.com/livekit/livekit/blob/master/README.md), [stream allocator](https://github.com/livekit/livekit/blob/master/pkg/sfu/streamallocator/streamallocator.go).
- **C3:** Allocation distinguishes stable and bandwidth-deficient states, gives screen sharing a different default priority, handles probes, and can reset bandwidth estimation after prolonged congestion while sending is paused.
- **C1:** Track-map locking, event-based allocation, and coalescing of pending work expose the concurrency consequences of changing subscriptions and priorities during media delivery in the same allocator source.

### 10. [jitsi/jitsi-videobridge](https://github.com/jitsi/jitsi-videobridge)

**Java and Kotlin — conferencing SFU and media transformation subsystems.** Study how receiver preferences and network estimates become actual packet-forwarding decisions. The monorepo includes both the bridge and `jitsi-media-transform`; it is counted once.

- **C3:** The allocation design separates source prioritization, LastN stream limits, and layer allocation. It describes how selected/on-stage sources, frame-rate constraints, and available bandwidth affect the chosen layers. [Allocation design](https://github.com/jitsi/jitsi-videobridge/blob/master/doc/allocation.md).
- **C1:** Adaptive source projection filters and rewrites packets across quality changes to preserve a coherent outgoing stream. Codec-specific projection contexts, keyframe requests, and shared state make this more than simple packet copying. [Adaptive source projection](https://github.com/jitsi/jitsi-videobridge/blob/master/jvb/src/main/java/org/jitsi/videobridge/cc/AdaptiveSourceProjection.java).

## Multiprotocol streaming servers and gateways

### 11. [ossrs/srs](https://github.com/ossrs/srs)

**C++ — streaming server joining RTMP, WebRTC, SRT, and HTTP delivery.** Study how live sources feed different output protocols and how the RTC source manages consumers and packet delivery. The architecture document contains older terminology, so current behavior should be checked against the implementation.

- **C2:** The architecture separates ingest, protocol conversion, forwarding, recording, and delivery. It provides an understandable map for tracing how a source can serve several media distribution paths. [Architecture](https://github.com/ossrs/srs/blob/develop/trunk/doc/Architecture.md).
- **C1:** RTC source code explicitly coordinates consumer lifetime, source changes, queued packet ownership, and delayed source cleanup. These paths are useful for studying disconnect and republish behavior. [RTC source implementation](https://github.com/ossrs/srs/blob/develop/trunk/src/app/srs_app_rtc_source.cpp).
- **C3:** The consumer waits on a condition and wakes when the queue exceeds its configured threshold, exposing the batching-versus-latency decision. The source also candidly marks queue operations needing further optimization.

### 12. [bluenviron/mediamtx](https://github.com/bluenviron/mediamtx)

**Go — live media router, proxy, and recorder.** Study protocol integration organized around named paths rather than a conferencing application. Each path connects a publisher or external source to multiple readers.

- **C2:** The architecture divides responsibilities among a path manager, paths, recorders, protocol servers, and administrative services. This supports camera proxying, protocol conversion, live distribution, and recording through one service model. [Architecture](https://github.com/bluenviron/mediamtx/blob/main/docs/2-features/02-architecture.md).
- **C1:** A path's implementation serializes publisher/reader changes, source readiness, reloads, and cancellation through channels. Explicit on-demand states and readiness/closure timers handle sources that arrive late, time out, or disappear; shutdown also resolves held requests. [Path lifecycle](https://github.com/bluenviron/mediamtx/blob/main/internal/core/path.go).

### 13. [ZLMediaKit/ZLMediaKit](https://github.com/ZLMediaKit/ZLMediaKit)

**C++ — streaming framework spanning surveillance and internet delivery.** Study the common track/frame layer connecting RTSP, RTMP, HLS, WebRTC, and related delivery forms. It provides both a complete server and an embeddable C API.

- **C2:** `MultiMediaSourceMuxer` fans common tracks and frames into protocol muxers and recorders, with coordinated track readiness and reset operations. [Multiprotocol muxer](https://github.com/ZLMediaKit/ZLMediaKit/blob/master/src/Common/MultiMediaSourceMuxer.cpp).
- **C1:** The same implementation handles ownership across thread switches, timestamp adjustment, and timer callbacks using weak ownership. Its paced sender bounds its cache even when publisher timestamps are identical or closely clustered.
- **C3:** Pacing adjusts delivery to buffer depth, while output enablement checks permit demand-driven work. These mechanisms are more useful study targets than the broad capacity claims in the [project overview](https://github.com/ZLMediaKit/ZLMediaKit/blob/master/README_en.md).

### 14. [OvenMediaLabs/OvenMediaEngine](https://github.com/OvenMediaLabs/OvenMediaEngine)

**C++ — live ingest, adaptive transcoding, and WebRTC/LLHLS delivery.** Study a server that combines an embedded transcoder with media routing, rather than only forwarding an already suitable encoding.

- **C2:** The router distinguishes providers, transcoders, publishers, relays, and orchestration observers. Stream creation and readiness notifications connect these roles, allowing several ingest and delivery protocols to share the pipeline. [Media-router application](https://github.com/OvenMediaLabs/OvenMediaEngine/blob/master/src/mediarouter/mediarouter_application.cpp).
- **C3:** The implementation separates inbound and outbound worker threads and queues, bounds the configured worker count, and assigns streams across workers. This is a concrete place to study concurrency and latency across routing and transcoding stages.

The [repository overview](https://github.com/OvenMediaLabs/OvenMediaEngine#features) identifies the corresponding ingest, retransmission/FEC, transcoding, and origin/edge features. Its advertised latency and audience-size figures were not independently benchmarked.

## Transport, security, NAT traversal, and telephony foundations

### 15. [Haivision/srt](https://github.com/Haivision/srt)

**C++ — Secure Reliable Transport protocol library.** Study recovery and packet scheduling for live contribution over unreliable networks. The library transports application data and does not require a particular media codec or container.

- **C1:** Timestamp-based packet delivery must reconcile separate sender/receiver clocks, timestamp rollover, arrival variation, and retransmission deadlines. The latency document derives the delivery-time model and explains drift correction. [Latency and TSBPD design](https://github.com/Haivision/srt/blob/master/docs/features/latency.md).
- **C3:** The live-streaming guide connects MTU-sized transport units, paced emission, receiver buffering, and recovery time. It explains why sending an entire frame in a burst and then sleeping can violate the desired delivery behavior. [Live-streaming design](https://github.com/Haivision/srt/blob/master/docs/features/live-streaming.md).

### 16. [ultravideo/uvgRTP](https://github.com/ultravideo/uvgRTP)

**C++ — RTP/SRTP media delivery library.** A useful smaller codebase for studying video packetization and transport of H.264/H.265/H.266, Opus, and volumetric media. Its scope includes RTP/RTCP and optional SRTP/ZRTP.

- **C2:** Context, session, media-stream, and codec-format layers provide reusable transport building blocks across several encoded media types. The shared H.26x implementation makes the relationship between common transport handling and codec-specific framing inspectable. [H.26x transport implementation](https://github.com/ultravideo/uvgRTP/blob/master/src/formats/h26x.cc).
- **C3:** The frame queue separates RTP/media headers from payload buffers using vectors and platform I/O structures. It also explicitly falls back to payload copying when encryption requires contiguous data, exposing a real boundary on avoiding copies. Frame pacing and transaction cleanup are in the same implementation. [Frame queue](https://github.com/ultravideo/uvgRTP/blob/master/src/frame_queue.cc).

### 17. [bluenviron/gortsplib](https://github.com/bluenviron/gortsplib)

**Go — RTSP client/server library with RTP media utilities.** Although used by MediaMTX, this is an independently reusable protocol implementation, not another listing of the server. Study RTSP session control alongside media timing and packet-format handling.

- **C1:** The global timestamp decoder extends wrapping RTP timestamps using signed deltas and rescales time by splitting integer/fractional division to reduce overflow while preserving resolution. It also coordinates tracks with different clock rates under a mutex. [Global timestamp decoder](https://github.com/bluenviron/gortsplib/blob/main/pkg/rtptime/global_decoder.go).
- **C2:** Client and server APIs cover playing, recording, pausing, transport selection, and codec-specific payload conversion. The server-session implementation is an entry point into the shared lifecycle beneath these operations. [Server session](https://github.com/bluenviron/gortsplib/blob/main/server_session.go).

### 18. [cisco/libsrtp](https://github.com/cisco/libsrtp)

**C — SRTP/SRTCP packet protection library.** Study the protocol-specific security state beneath WebRTC and telephony stacks, particularly the interaction of packet ordering, implicit counters, replay protection, and cryptographic policy.

- **C1:** The replay database reconstructs extended packet indices from transmitted sequence numbers and rollover state. Its comments explain the signed difference returned by index estimation and the replay-window bitmask; confusing these arithmetic domains changes acceptance behavior. [Replay database](https://github.com/cisco/libsrtp/blob/main/crypto/replay/rdbx.c).
- **C2:** The public interface separates sessions, streams, protection policies, and protect/unprotect operations, allowing transport stacks to reuse SRTP without adopting a full media engine. [Public API](https://github.com/cisco/libsrtp/blob/main/include/srtp.h).

### 19. [coturn/coturn](https://github.com/coturn/coturn)

**C — STUN/TURN connectivity and media relay server.** Study the infrastructure that carries media when direct connectivity fails, including the tension between accepting unauthenticated discovery traffic and preserving server resources.

- **C1:** The stateless-nonce design explains how valid-looking spoofed requests can allocate session state before authentication. It documents authenticated timestamp cookies, return-routability checks, challenge handling, and the limits of response rate limiting. [Stateless-nonce design](https://github.com/coturn/coturn/blob/master/docs/stateless-nonce.md).
- **C3:** The network architecture pairs listeners and relay servers on the same thread and normally keeps a session there throughout its lifetime, reducing cross-thread handoffs. It separately explains session movement for mobility. [Network architecture](https://github.com/coturn/coturn/blob/master/docs/netarch.md).

### 20. [baresip/re](https://github.com/baresip/re)

**C — libre asynchronous communications foundation.** Study a compact toolkit spanning SIP/SDP, RTP/RTCP/SRTP, STUN/TURN/ICE, timers, buffers, and event-driven I/O. This entry is the reusable foundation, rather than the separate Baresip user-agent application.

- **C2:** The repository's module inventory separates protocol layers from memory referencing, message queues, timers, and platform socket handling. It explicitly distinguishes stable APIs from modules whose interfaces may change. [Module inventory](https://github.com/baresip/re#modules).
- **C1:** The polling implementation maintains thread-local loop state, locks, atomics, a deferred file-descriptor-handler deletion list, and fallback destruction when threads exit. These are concrete lifetime and synchronization mechanisms beneath protocol callbacks. [Event-loop implementation](https://github.com/baresip/re/blob/main/src/main/main.c).
- **C3:** The same layer supports select, epoll, and kqueue and includes debug instrumentation for handlers that block the event loop too long.

### 21. [pjsip/pjproject](https://github.com/pjsip/pjproject)

**C/C++ — integrated SIP, media, and NAT-traversal monorepo.** Focus on PJMEDIA and PJNATH alongside SIP session control. Study how media transport can be extended and reused while following offer/answer negotiation and call lifecycle rules.

- **C2:** PJMEDIA's transport interface separates streams from network transports using operation tables and RTP/RTCP callbacks. It supports transport composition and a lifecycle of create, attach, detach, reuse, and destroy. [Media transport interface and design](https://github.com/pjsip/pjproject/blob/master/pjmedia/include/pjmedia/transport.h).
- **C1:** The same document specifies when SDP-derived settings become active, how ICE/SRTP transports participate in renegotiation, and when callbacks cease after detachment. It also explains which callbacks are thread-safe and which transport state still needs protection.
- **C3:** Reusing detached transports preserves sockets between calls, avoiding repeated setup and reducing the risk of advertised RTP ports being taken before media starts.

### 22. [sipwise/rtpengine](https://github.com/sipwise/rtpengine)

**C — RTP/SRTP media proxy with Linux kernel forwarding support.** Study the media path adjacent to SIP proxies, including SDP rewriting, network/crypto bridging, fan-out, and optional transcoding.

- **C1:** The architecture maps sockets to packet streams, media sections, call participants, and sinks. It specifies a call-wide read/write lock discipline: signaling changes take the write lock while packet handling takes the read lock. [Architecture and locking](https://github.com/sipwise/rtpengine/blob/master/docs/architecture.md).
- **C3:** The design traces decrypt/codec/encrypt stages and explains how sink handlers populate the kernel forwarding structures. This makes the split between flexible userspace processing and accelerated forwarding understandable.

The [testing guide](https://github.com/sipwise/rtpengine/blob/master/docs/tests.md) describes tests that start a real daemon in a simulated network environment and exercise actual SDP exchanges and RTP forwarding; some tests remain manual, as the guide explicitly notes.

## Network audio and composable media pipelines

### 23. [roc-streaming/roc-toolkit](https://github.com/roc-streaming/roc-toolkit)

**C++ with C API — real-time network audio toolkit.** Study audio-specific constraints that generic reliable transports do not resolve by themselves: sample-clock drift, loss recovery, bounded playout delay, and priority inversion.

- **C1:** Pipelines are driven in the user's clock domain, and the receiver dynamically resamples between sender and receiver clocks. The design explains why processing too early can classify still-recoverable packets as lost, while processing too late produces glitches. [Pipeline and timing design](https://github.com/roc-streaming/roc-toolkit/blob/master/docs/sphinx/internals/pipelines.rst).
- **C3:** Network, audio, pipeline, and control work communicate through queues. The threading guide describes lock-free scheduling, avoidance of priority inversion, and preallocated intrusive tasks to reduce allocation/copying on critical paths. [Threads and queues](https://github.com/roc-streaming/roc-toolkit/blob/master/docs/sphinx/internals/threads.rst).
- **C2:** Packet/frame readers and writers compose into sender/receiver pipelines, while slots allow different endpoint/protocol combinations in one node.

### 24. [GStreamer/gstreamer](https://github.com/GStreamer/gstreamer)

**Primarily C — media framework; official GitHub mirror.** The [GStreamer organization](https://github.com/GStreamer) identifies this as an official mirror; upstream development is on freedesktop.org GitLab. Count the monorepo once. Relevant subsystems are `gst-plugins-good/gst/rtpmanager`, `gst-plugins-bad/ext/webrtc`, and the RTSP components.

- **C1:** The RTP jitter-buffer source documents duplicate removal, packet reordering, timestamp reconstruction, missing-packet deadlines, retransmission scheduling, and bounded retry periods. [RTP jitter-buffer implementation and embedded documentation](https://github.com/GStreamer/gstreamer/blob/main/subprojects/gst-plugins-good/gst/rtpmanager/gstrtpjitterbuffer.c).
- **C2:** It exposes these behaviors as a pipeline element using caps, signals, properties, and upstream/downstream events. Depayloaders can consume packet-loss events while other elements act on retransmission requests; `rtpbin` incorporates the element automatically.
- **C3:** Configurable latency and early retransmission timing make recovery-versus-playout-delay decisions explicit within the same reusable element.

## Emerging transport architecture

### 25. [moq-dev/moq](https://github.com/moq-dev/moq)

**Rust and TypeScript — Media over QUIC libraries, relay, and media layers.** Study a contrasting architecture: application-aware groups and tracks above QUIC/WebTransport, with transport fan-out separated from media interpretation. This is an evolving draft-based stack; verify the negotiated protocol versions for a deployment.

- **C2:** The protocol model separates sessions, broadcasts, tracks, groups, and frames. Each group uses an ordered reliable QUIC stream while tracks may deliver groups out of order, supporting reusable publish/subscribe delivery. [moq-lite design](https://github.com/moq-dev/moq/blob/main/doc/concept/moq-lite.md).
- **C3:** Subscription priority, group ordering, and delay budgets express which work should be delivered first or become obsolete under congestion. The design ties these controls directly to live playback needs.
- **C1:** The audio-jitter design specifies clock units and observation points and uses a shared conformance corpus for Rust/TypeScript parity. It also explains how observing only frames surviving a delay budget can bias the estimator. [Audio-jitter design](https://github.com/moq-dev/moq/blob/main/doc/concept/audio-jitter.md).

## Coverage, search process, and limitations

Live discovery used more than six distinct formulations, including standalone WebRTC implementations; SFU/media-server architecture; SRT versus RIST; RTP/RTCP/RTSP libraries; SIP/RTP foundations; real-time network audio; Rust Sans-I/O; Elixir/OTP communications; surveillance-oriented streaming servers; official GStreamer mirrors; and Media over QUIC. Follow-up searches for smaller transport projects and official RIST sources increasingly returned already-covered architectural families, wrappers, or third-party copies. The final selection balances popular infrastructure with less widely known implementations such as uvgRTP, Roc, libre, str0m, and ex_webrtc.

Verification used public GitHub repository metadata and recursive source-tree listings, followed by reading READMEs and the linked design, implementation, test, or changelog material. Canonical names, branch names, archive status, and every retained source-file path were checked. Repository age or stars were not treated as quality evidence. C4 is awarded to Janus using dated history and explicit compatibility management; other entries qualify through their demonstrated mechanisms without an inferred longevity claim.

Important scope boundaries and limitations:

- The upstream [WebRTC source repository](https://webrtc.googlesource.com/src/) identifies googlesource.com as its master source and GitHub as a location for samples/reference apps. No third-party libwebrtc snapshot was substituted for a verified official substantive GitHub mirror.
- The RIST searches led to VideoLAN's libRIST and customized GitHub copies. The [VideoLAN source site](https://code.videolan.org/rist/librist) denied automated access, and an official substantive GitHub mirror was not established. libRIST is therefore a coverage gap, rather than a negative engineering judgment.
- The search encountered the archived `fishjam-dev/membrane_rtc_engine` location and its move notice. It was not counted as a separate historical implementation; ex_webrtc provides verified Elixir transport coverage here. Tutorial SFUs, SDK-only wrappers, awesome-lists, and incidental media features in general application repositories were excluded.
- No candidate code was executed, dependencies installed, benchmarks run, or repositories cloned. Performance judgments concern inspected mechanisms. Source review was selective rather than an exhaustive correctness or security audit, and draft protocols and branch-linked code may change rapidly.
