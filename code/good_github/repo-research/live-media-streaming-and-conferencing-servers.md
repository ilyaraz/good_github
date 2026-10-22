# Live media streaming and conferencing servers

Research date: **2026-10-09**.

This selection covers servers and substantial server engines that ingest, relay, distribute, mix, or coordinate live audio/video: broadcast streaming gateways, WebRTC selective forwarding units (SFUs), programmable media pipelines, complete conferencing backends, and audio conferencing/radio servers. It includes embeddable media engines when they implement the server media plane themselves. Pure client SDKs, generic codec libraries, signaling-only demonstrations, and video-on-demand catalog applications are outside scope. The 23 repositories below were checked against primary repository metadata and additional implementation or architecture material.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, protocol/numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or components supporting multiple applications.
- **C3 — Performance:** concrete latency, bandwidth, CPU, or memory constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by evidence of compatibility management, testing, or deliberate complexity management.

The criteria are judgments grounded in the cited material. They identify worthwhile study areas, not a claim that every component is exemplary or that a repository is ready for a particular production deployment. Links to branch files reflect the research snapshot and can change.

## Broadcast servers and protocol gateways

### 1. [ossrs/srs](https://github.com/ossrs/srs)

**Language/role:** C++ media server; the relevant subsystem is the streaming core under `trunk/src`, rather than ancillary tooling in the larger repository. It supports live delivery through RTMP, WebRTC, HLS, SRT, and related protocols.

Study how one live source feeds consumers whose clocks, buffering needs, and network speeds differ. The [RTMP source interfaces](https://github.com/ossrs/srs/blob/develop/trunk/src/app/srs_app_rtmp_source.hpp) expose particularly concrete contracts:

- **C1:** jitter correction tracks original and corrected timestamps; consumer queues specify monotonic enqueue timestamps and explicit packet ownership. Wakeup interfaces account for clients that receive control/close messages while waiting for media.
- **C2:** source, consumer, and message-queue interfaces separate live-stream ownership from delivery and forwarding.
- **C3:** queues are limited by media duration and discard whole groups of pictures when full; optional fast-vector and condition-wait paths make the buffering/performance tradeoffs visible.

**Entry points:** [RTMP source/consumer contracts](https://github.com/ossrs/srs/blob/develop/trunk/src/app/srs_app_rtmp_source.hpp); [streaming application subsystem](https://github.com/ossrs/srs/tree/develop/trunk/src/app).

### 2. [bluenviron/mediamtx](https://github.com/bluenviron/mediamtx)

**Language/role:** Go live media server/proxy supporting publishing, reading, recording, and protocol conversion. This is the current repository for the project formerly called rtsp-simple-server; forks and the former name are not separate entries.

The central study topic is the lifecycle of a named media path shared by publishers, readers, recorders, and on-demand sources. In [path.go](https://github.com/bluenviron/mediamtx/blob/main/internal/core/path.go):

- **C1:** a channel-driven event loop coordinates publisher/reader changes, cancellation, configuration reloads, readiness deadlines, and idle shutdown. Requests held while an on-demand publisher starts receive explicit timeout errors.
- **C2:** common source, publisher, reader, and stream abstractions let the same path lifecycle serve multiple protocols and recording/forwarding functions.

The [path tests](https://github.com/bluenviron/mediamtx/blob/main/internal/core/path_test.go) exercise actual RTSP requests and on-demand hooks, offering an accessible bridge between the state machine and external behavior.

**Entry points:** [path implementation](https://github.com/bluenviron/mediamtx/blob/main/internal/core/path.go); [path integration tests](https://github.com/bluenviron/mediamtx/blob/main/internal/core/path_test.go).

### 3. [OvenMediaLabs/OvenMediaEngine](https://github.com/OvenMediaLabs/OvenMediaEngine)

**Language/role:** C++ live streaming server with transcoding, WebRTC delivery, and low-latency HLS. The former AirenSoft repository URL redirects to this canonical owner.

Study how ingest, stream processing, and viewer delivery scale differently:

- **C2:** the [origin/edge design](https://github.com/OvenMediaLabs/OvenMediaEngine/blob/master/docs/origin-edge-clustering.md) separates origins from edges that pull requested streams. Static origin mappings and Redis-backed discovery support different deployment models; named track sets let edges request only relevant renditions or audio tracks.
- **C3:** the [performance guide](https://github.com/OvenMediaLabs/OvenMediaEngine/blob/master/docs/performance-tuning.md) distinguishes socket workers, per-stream packetization workers, and per-session encryption/delivery workers. It explains why many publishers and many viewers require different thread allocations and supplies a WebRTC load-testing tool.

These are architectural explanations rather than an assumed throughput guarantee; the guide also records an older RTP-timestamp issue affecting delay measurements.

**Entry points:** [origin/edge clustering](https://github.com/OvenMediaLabs/OvenMediaEngine/blob/master/docs/origin-edge-clustering.md); [performance tuning](https://github.com/OvenMediaLabs/OvenMediaEngine/blob/master/docs/performance-tuning.md).

### 4. [ZLMediaKit/ZLMediaKit](https://github.com/ZLMediaKit/ZLMediaKit)

**Language/role:** C++ server and client framework spanning RTSP, RTMP, WebRTC, SRT, HTTP delivery, and GB28181-oriented workflows.

The [multi-protocol muxer](https://github.com/ZLMediaKit/ZLMediaKit/blob/master/src/Common/MultiMediaSourceMuxer.cpp) is a useful example of combining protocol adaptation with shared media lifecycle logic:

- **C1:** its paced sender detects decreasing decode timestamps and flushes/reset its cache. It also bounds cache size when timestamps are identical or tightly clustered, a case where a time-based limit alone is insufficient.
- **C2:** common tracks and frames feed protocol outputs and recorders; adding a recorder reuses existing tracks and can flush the cached group of pictures into it.
- **C3:** pacing adjusts consumption against buffered media duration, while event-poller timers and cached frames make latency and memory control explicit.

**Entry points:** [MultiMediaSourceMuxer.cpp](https://github.com/ZLMediaKit/ZLMediaKit/blob/master/src/Common/MultiMediaSourceMuxer.cpp); [common media abstractions](https://github.com/ZLMediaKit/ZLMediaKit/tree/master/src/Common).

### 5. [DDVTECH/mistserver](https://github.com/DDVTECH/mistserver)

**Language/role:** C++ multi-protocol streaming toolkit and server.

MistServer offers a contrasting architecture to a single-process event-loop server. Its official [architecture overview within the showcase](https://mistserver.com/showcase) describes separate input, output, and processing processes connected through shared memory. The [stream implementation](https://github.com/DDVTECH/mistserver/blob/master/lib/stream.cpp) exposes input-process startup, output selection, shared-memory access, and packet ordering utilities.

- **C1:** process separation is an explicit fault-containment strategy: an output crash need not terminate the other outputs. Process startup and shared state make failure recovery and resource ownership valuable subjects to inspect; this is not a claim that every failure is isolated.
- **C2:** a common stream representation and output machinery support playback, restreaming, recording, and time-bounded access to buffered media.
- **C3:** shared memory connects independently scheduled media processes, avoiding a design in which every output requires another network copy from its input.

**Entry points:** [stream/process coordination](https://github.com/DDVTECH/mistserver/blob/master/lib/stream.cpp); [official architecture and use cases](https://mistserver.com/showcase).

### 6. [arut/nginx-rtmp-module](https://github.com/arut/nginx-rtmp-module)

**Language/role:** C module extending NGINX into an RTMP streaming server, with HLS/DASH, recording, and relay modules. **Historical/slow-moving selection:** repository metadata showed its last push in December 2024; ongoing maintenance is not assumed.

Study media fan-out inside NGINX's configuration and event framework. The [live module](https://github.com/arut/nginx-rtmp-module/blob/master/ngx_rtmp_live_module.c) provides substantial implementation evidence:

- **C1:** publisher/subscriber state, idle-publisher expiry, codec initialization headers, and per-subscriber chunk-stream timestamps must stay consistent as streams start, stop, and resume.
- **C2:** application-level configuration and chained publish/play/close handlers let live forwarding coexist with distinct recording, relay, notification, and access-control modules.
- **C3:** the packet path prepares shared buffer chains for fan-out and differentiates mandatory codec headers from ordinary media packets, exposing the relationship between buffering and decodable playback.

**Entry points:** [live forwarding implementation](https://github.com/arut/nginx-rtmp-module/blob/master/ngx_rtmp_live_module.c); [module source layout](https://github.com/arut/nginx-rtmp-module/tree/master).

### 7. [harlanc/xiu](https://github.com/harlanc/xiu)

**Language/role:** Rust live streaming server supporting RTMP, RTSP, WebRTC WHIP/WHEP, HLS, and HTTP-FLV.

Xiu provides a smaller, directly inspectable alternative to the large C++ gateways. Its [workspace](https://github.com/harlanc/xiu/blob/master/Cargo.toml) separates protocol crates, containers/codecs, applications, and a central stream hub.

- **C2:** the [stream hub](https://github.com/harlanc/xiu/blob/master/library/streamhub/src/lib.rs) uses protocol-implemented `TStreamHandler` objects and distinct packet/frame channels, allowing shared publication, subscription, notification, and statistics machinery across protocols.
- **C1:** concurrent Tokio tasks handle media, subscriber events, statistics, and shutdown; shared subscriber maps and statistics use explicit synchronization. Subscriber-send failures and exit broadcasts reveal the failure paths a maintainer must reason about.

The inspected hub uses unbounded channels in places. That is a useful resource-management tradeoff to investigate, not evidence of universally bounded memory or a reason to repeat the README's performance claims.

**Entry points:** [stream hub implementation](https://github.com/harlanc/xiu/blob/master/library/streamhub/src/lib.rs); [workspace decomposition](https://github.com/harlanc/xiu/blob/master/Cargo.toml).

### 8. [owncast/owncast](https://github.com/owncast/owncast)

**Language/role:** Go backend with a TypeScript web application; a complete self-hosted live broadcast and chat server.

Study the server's orchestration of an external transcoder and its output storage, rather than expecting an in-house codec implementation. The [transcoder](https://github.com/owncast/owncast/blob/develop/services/transcoder/transcoder.go) manages FFmpeg execution, completion, logs, latency settings, and multiple output variants.

- **C2:** codec selection and `HLSVariant` settings separate output policy from command generation. The [HLS handler](https://github.com/owncast/owncast/blob/develop/services/transcoder/hlsHandler.go) reports segment, variant-playlist, and master-playlist writes through a storage-provider interface.
- **C3:** variants expose bitrate, frame rate, scaling, CPU budget, and audio/video passthrough. The implementation reserves bitrate for audio and distinguishes average, maximum, and buffer settings rather than treating transcoding as one opaque command.

**Entry points:** [transcoder and variant construction](https://github.com/owncast/owncast/blob/develop/services/transcoder/transcoder.go); [HLS/storage boundary](https://github.com/owncast/owncast/blob/develop/services/transcoder/hlsHandler.go).

### 9. [Red5/red5-server](https://github.com/Red5/red5-server)

**Language/role:** Java RTMP media-server core. The inspected open-source README explicitly distinguishes its RTMP scope from the additional protocols in commercial Red5 products.

The [RTMP ingest profiling report](https://github.com/Red5/red5-server/blob/main/RTMP_INGEST_PERF_FIXES.md) is unusually useful because it ties a workload, profiler findings, code changes, and verification together:

- **C3:** it investigates eager formatting in disabled trace logs, unnecessary per-packet task dispatch, repeated channel-state allocation, and temporary chunk copies. The discussion separates socket costs from avoidable CPU/allocation overhead.
- **C1:** replacing asynchronous dispatch followed immediately by a join relies on a single-threaded receiver's packet-order invariant; the report explains exception handling and why ordering is retained.

The [README's integration-test description](https://github.com/Red5/red5-server/blob/main/README.md) covers concurrent FFmpeg publishers, FFprobe subscribers, and handshake/rejection checks. No numerical result from the profiling report is treated as a transferable capacity claim.

**Entry points:** [profiling and implementation analysis](https://github.com/Red5/red5-server/blob/main/RTMP_INGEST_PERF_FIXES.md); [integration-test workflow](https://github.com/Red5/red5-server/blob/main/README.md).

## WebRTC forwarding and conferencing engines

### 10. [meetecho/janus-gateway](https://github.com/meetecho/janus-gateway)

**Language/role:** C WebRTC server with media and transport plugins.

Janus is useful for studying a protocol core that supports substantially different media applications. Its [plugin catalog](https://janus.conf.meetecho.com/docs/pluginslist.html) includes streaming, video rooms, audio mixing, SIP, and recording/playback.

- **C2:** these media behaviors are separate plugins that applications can combine, rather than hard-coded room behavior in the transport core.
- **C1:** the [VideoRoom design](https://janus.conf.meetecho.com/docs/videoroom.html) deliberately separates publishing and subscribing PeerConnections to avoid renegotiation conflicts. It distinguishes room-management handles from subscription handles and explains multistream versus separate subscriptions.
- **C3:** multistream subscriptions trade connection/transport resources against client complexity, while room bitrate controls and selective subscriptions constrain media distribution.

**Entry points:** [VideoRoom architecture and protocol](https://janus.conf.meetecho.com/docs/videoroom.html); [media plugin boundaries](https://janus.conf.meetecho.com/docs/pluginslist.html).

### 11. [versatica/mediasoup](https://github.com/versatica/mediasoup)

**Language/role:** C++ media workers with TypeScript/Node.js and Rust integration layers; an embeddable SFU engine, not a standalone conferencing application.

The official [design document](https://mediasoup.org/documentation/v3/mediasoup/design/) separates the application-facing API from C/C++ subprocesses communicating through IPC.

- **C2:** transport and media routing are exposed below application signaling, so a caller can build conferencing, broadcasting, or plain-RTP integration without inheriting a prescribed room/signaling application.
- **C3:** libuv-based media workers handle ICE, DTLS, RTP, and RTCP separately from application logic. Bandwidth estimation and spatial/temporal layer allocation address the cost of forwarding simulcast and scalable video to receivers with different capacities.

The [repository layout](https://github.com/versatica/mediasoup/tree/v3) makes the `worker`, `node`, and `rust` boundaries visible. Count this repository once; the bindings are interfaces to the media engine, not independent servers.

**Entry points:** [media-worker design](https://mediasoup.org/documentation/v3/mediasoup/design/); [worker and language-binding layout](https://github.com/versatica/mediasoup/tree/v3).

### 12. [jitsi/jitsi-videobridge](https://github.com/jitsi/jitsi-videobridge)

**Language/role:** Java/Kotlin WebRTC SFU; the media-routing component of Jitsi, rather than the Jitsi Meet frontend.

The [bandwidth allocation specification](https://github.com/jitsi/jitsi-videobridge/blob/master/doc/allocation.md) is a strong bridge from product behavior to algorithmic code:

- **C1:** receiver constraints have deliberately different semantics: a zero-height constraint must never be exceeded, while a positive constraint can admit a lowest available layer when no layer otherwise qualifies. Allocation must account for inactive layers and changing sources.
- **C3:** prioritization, LastN, selected/on-stage sources, and layer pruning allocate limited receiver bandwidth. Applying sender constraints early enables suspension of unneeded layers.
- **C2:** [cascaded bridge relays](https://github.com/jitsi/jitsi-videobridge/blob/master/doc/relay.md) use ICE and DTLS/SRTP between bridges, separating regional media distribution from conference placement policy.

**Entry points:** [allocation algorithm](https://github.com/jitsi/jitsi-videobridge/blob/master/doc/allocation.md); [secure bridge relays](https://github.com/jitsi/jitsi-videobridge/blob/master/doc/relay.md).

### 13. [livekit/livekit](https://github.com/livekit/livekit)

**Language/role:** Go WebRTC media server built on Pion, with room, participant, track, and signaling services.

Study an opinionated SFU that packages application-level session semantics with a reusable media service. The [SFU internals guide](https://docs.livekit.io/reference/internals/livekit-sfu/) describes the key boundaries:

- **C2:** publishers expose independently subscribable tracks; applications retain control over individual audio/video streams rather than receiving a fixed server-composited result.
- **C3:** the SFU forwards encoded media and adapts track parameters to measured subscriber bandwidth. Distributed deployments use Redis-assisted routing to place participants of a room on the same node.

That last detail matters: the cited open-source architecture is evidence for scaling across rooms/nodes, not proof that an arbitrary single room is automatically split across a distributed media mesh. The repository's `pkg` subtree contains the corresponding server packages.

**Entry points:** [SFU architecture](https://docs.livekit.io/reference/internals/livekit-sfu/); [server package layout](https://github.com/livekit/livekit/tree/master).

### 14. [ionorg/ion-sfu](https://github.com/ionorg/ion-sfu)

**Language/role:** Go embeddable SFU with gRPC and JSON-RPC signaling examples. **Historical/inactive selection:** GitHub metadata reported the last repository push in July 2023; the repository was not archived, but active maintenance is not claimed.

Its small server surface makes individual forwarding invariants easier to inspect than in a full conferencing platform:

- **C1:** the [sequencer](https://github.com/ionorg/ion-sfu/blob/master/pkg/sfu/sequencer.go) maintains original and subscriber-specific sequence numbers/timestamps, protects shared state with a mutex, and remembers recent NACK requests to suppress duplicate retransmission work. Per-downtrack rewritten metadata must not be shared across subscribers.
- **C2:** the [documented integration model](https://github.com/ionorg/ion-sfu/blob/master/README.md) supports direct embedding or separate gRPC/JSON-RPC signaling, keeping application policy outside the forwarding engine.

**Entry points:** [packet sequencer](https://github.com/ionorg/ion-sfu/blob/master/pkg/sfu/sequencer.go); [SFU components and adjacent tests](https://github.com/ionorg/ion-sfu/tree/master/pkg/sfu).

### 15. [jech/galene](https://github.com/jech/galene)

**Language/role:** Go videoconferencing server with a JavaScript client and administrative/client protocols.

Galène is especially useful for studying compact media algorithms inside a complete server. Its [packet mapping implementation](https://github.com/jech/galene/blob/master/packetmap/packetmap.go) is small enough to read in one sitting.

- **C1:** sequence-number comparison works modulo 2^16; mapping and reverse mapping track picture-ID offsets, handle discontinuities, and reject unsafe drops. The code explicitly prevents overlapping mapped target intervals.
- **C3:** sparse interval mappings and a bounded circular history avoid retaining an unbounded per-packet mapping table.
- **C4:** the [dated changelog](https://github.com/jech/galene/blob/master/CHANGES) documents multiple years of browser workarounds, protocol-version retirement, Pion migration, incompatible configuration changes, and race/security fixes. This is stronger evidence of evolution management than repository age alone.

**Entry points:** [packet mapping](https://github.com/jech/galene/blob/master/packetmap/packetmap.go); [compatibility and change history](https://github.com/jech/galene/blob/master/CHANGES).

### 16. [lynckia/licode](https://github.com/lynckia/licode)

**Language/role:** C++ Erizo media engine with JavaScript service/control layers for WebRTC rooms.

The [architecture description](https://github.com/lynckia/licode/blob/master/doc/index.md) separates room provisioning through Nuve, room management through Erizo Controller, and media handling through Erizo. Within the engine:

- **C2:** the [pipeline API](https://github.com/lynckia/licode/blob/master/erizo/src/erizo/pipeline/Pipeline.h) composes inbound/outbound handlers and shared services, with explicit activation, close, update, and event propagation interfaces.
- **C1:** the [one-to-many processor](https://github.com/lynckia/licode/blob/master/erizo/src/erizo/OneToManyProcessor.cpp) rewrites SSRCs per subscriber and translates feedback back toward the publisher. Its requirement that sinks immediately copy a mutated packet is an important ownership invariant; subscriber membership and fan-out also interact with locking.

**Entry points:** [media pipeline abstractions](https://github.com/lynckia/licode/blob/master/erizo/src/erizo/pipeline/Pipeline.h); [fan-out and feedback translation](https://github.com/lynckia/licode/blob/master/erizo/src/erizo/OneToManyProcessor.cpp).

### 17. [fishjam-cloud/membrane_rtc_engine](https://github.com/fishjam-cloud/membrane_rtc_engine)

**Language/role:** Elixir RTC/SFU engine with endpoint packages. **Archived:** both repository metadata and the README state that the project is no longer maintained or updated. It remains a substantive historical implementation, not a maintained recommendation.

- **C2:** the [engine architecture](https://github.com/fishjam-cloud/membrane_rtc_engine/blob/master/engine/internal_docs/engine_architecture.md) uses a separate tee per track to forward to subscribed endpoints. Protocol-specific work belongs to endpoints; the engine requires RTP-formatted tracks but keeps its forwarding machinery largely protocol-independent. The monorepo contains WebRTC, HLS, RTSP, SIP, file, and recording endpoints.
- **C1:** the [track lifecycle](https://github.com/fishjam-cloud/membrane_rtc_engine/blob/master/engine/guides/track_lifecycle.md) distinguishes publication, readiness, resumed/paused variants, and switching. Media may flow only for a resumed variant; switching requires a keyframe, and a switch event must precede the first media packet.

**Entry points:** [engine architecture](https://github.com/fishjam-cloud/membrane_rtc_engine/blob/master/engine/internal_docs/engine_architecture.md); [track and variant lifecycle](https://github.com/fishjam-cloud/membrane_rtc_engine/blob/master/engine/guides/track_lifecycle.md).

## Programmable media pipelines and complete conferencing backends

### 18. [Kurento/kurento](https://github.com/Kurento/kurento)

**Language/role:** C/C++ media server with Java/JavaScript clients, documentation, and tests in a monorepo. The relevant subsystem is the server media pipeline; count the monorepo once, rather than counting former component repositories separately.

- **C2:** the [application architecture](https://doc-kurento.readthedocs.io/en/latest/user/writing_applications.html) constructs graphs of Media Elements. WebRTC endpoints, recording, processing filters, and other elements can be connected into different topologies, while application signaling stays outside the media plane.
- **C1:** the [NAT traversal implementation guide](https://github.com/Kurento/kurento/blob/main/doc-kurento/source/features/nat_traversal.rst) documents both ICE integration and connection-oriented RTP address discovery. It explains why the passive endpoint must ignore the advertised private address, wait for actual packets, and cannot initiate a one-way stream before discovery; symmetric RTP/RTCP and publicly reachable passive endpoints are explicit preconditions.

**Entry points:** [pipeline and signaling architecture](https://doc-kurento.readthedocs.io/en/latest/user/writing_applications.html); [NAT traversal contracts](https://github.com/Kurento/kurento/blob/main/doc-kurento/source/features/nat_traversal.rst).

### 19. [bigbluebutton/bigbluebutton](https://github.com/bigbluebutton/bigbluebutton)

**Language/role:** Scala/Java, Go, TypeScript/JavaScript, and recording tooling; a complete conferencing system aimed at virtual classrooms. Relevant subsystems include meeting actors, FreeSWITCH integration, GraphQL services, and recording/playback.

The official [3.0 architecture](https://docs.bigbluebutton.org/development/architecture/) is useful for understanding a conferencing server assembled from separately evolving services:

- **C1:** meeting messages and state are centralized in `MeetingActor`; permission-aware GraphQL subscriptions and middleware reconnection on permission refresh expose correctness boundaries between browser state and backend authority. Recorded events must be coordinated with raw media during later processing.
- **C2:** Redis messages separate meeting logic from the FreeSWITCH adapter; a common meeting API supports several learning-management and portal integrations. The architecture explicitly identifies media control versus mediasoup forwarding.

This entry concerns BigBlueButton's own orchestration and state machinery. Its external SFU/voice dependencies are not attributed to the monorepo as original implementations.

**Entry points:** [service and media architecture](https://docs.bigbluebutton.org/development/architecture/); [monorepo subsystem layout](https://github.com/bigbluebutton/bigbluebutton/tree/v3.0.x-develop).

### 20. [apache/openmeetings](https://github.com/apache/openmeetings)

**Language/role:** Java conferencing backend with web/client components. **Official Apache GitHub mirror**, as identified by repository metadata; its media server integration uses Kurento.

Study the boundary between conference-room semantics and an external media engine, particularly recording and screen sharing:

- **C1:** [KRoom](https://github.com/apache/openmeetings/blob/master/openmeetings-mediaserver/src/main/java/org/apache/openmeetings/mediaserver/KRoom.java) gates recording/sharing transitions with atomic compare-and-set, coordinates recording records with stream start/stop actions, and distinguishes an internal screen stream needed for recording from permission to expose it to participants.
- **C2:** room, stream, stream-processor, and Kurento-handler classes separate reusable media orchestration from persistence and participant notifications. The same room machinery supports normal and interview recordings, broadcast termination, and screen-sharing actions.

This is a substantive application-server integration, not a second independent implementation of Kurento's codecs or transport stack.

**Entry points:** [room media state](https://github.com/apache/openmeetings/blob/master/openmeetings-mediaserver/src/main/java/org/apache/openmeetings/mediaserver/KRoom.java); [media integration subsystem](https://github.com/apache/openmeetings/tree/master/openmeetings-mediaserver/src/main/java/org/apache/openmeetings/mediaserver).

## Voice conferencing and live audio distribution

### 21. [mumble-voip/mumble](https://github.com/mumble-voip/mumble)

**Language/role:** C++ voice communication client/server monorepo. The relevant server subsystem is `src/murmur`, not the desktop client's capture/playback code.

The [audio receiver buffer](https://github.com/mumble-voip/mumble/blob/master/src/murmur/AudioReceiverBuffer.cpp) shows that low-latency voice routing includes substantial policy and compatibility logic:

- **C1:** it excludes self-delivery and deafened recipients, handles positional-context compatibility, merges repeated recipients, and asserts that the final receiver set has no duplicates. Different audio contexts and volume adjustments must reconcile consistently.
- **C3:** receivers are partitioned into groups by compatible protocol version, audio context, and volume adjustment, allowing subsequent delivery work to operate on compatible groups. Capacity reservation and explicit profiling zones make the hot path visible.

**Entry points:** [receiver selection/grouping implementation](https://github.com/mumble-voip/mumble/blob/master/src/murmur/AudioReceiverBuffer.cpp); [Murmur server subsystem](https://github.com/mumble-voip/mumble/tree/master/src/murmur).

### 22. [xiph/Icecast-Server](https://github.com/xiph/Icecast-Server)

**Language/role:** C live audio/media streaming server. **Official GitHub mirror:** the repository points development issue reporting to Xiph's GitLab; the substantive mirrored source remains available on GitHub.

The [source lifecycle and listener loop](https://github.com/xiph/Icecast-Server/blob/master/src/source.c) offer an unusually direct view of long-lived streaming connections:

- **C1:** moving listeners between mounts requires compatible formats, running destinations, ordered tree locks, and preservation of any partially sent HTTP headers. The implementation explicitly documents deadlock avoidance.
- **C3:** listener writes have a per-iteration work budget; clients still referencing the oldest queued buffer when it must be discarded are disconnected as slow listeners. Source timeouts and reference-counted buffers expose resource limits and failure behavior.
- **C2:** format handlers, source mounts, relay logic, and listener state separate distribution from particular audio/container formats.

**Entry points:** [source and listener implementation](https://github.com/xiph/Icecast-Server/blob/master/src/source.c); [format, relay, and buffer subsystem layout](https://github.com/xiph/Icecast-Server/tree/master/src).

### 23. [signalwire/freeswitch](https://github.com/signalwire/freeswitch)

**Language/role:** C telephony/media switch. Included specifically for the substantive `mod_conference` audio/video conferencing subsystem, rather than its wider PBX feature set.

The [conference implementation](https://github.com/signalwire/freeswitch/blob/master/src/mod/applications/mod_conference/mod_conference.c) exposes the real-time bridge loop and its interactions with membership, recordings, and media policy:

- **C1:** a common timing source drives frame collection; conference and member audio locks protect concurrent state. Timer failure initiates teardown, and the loop coordinates changing video direction, floor ownership, silence termination, and recording eligibility.
- **C2:** conferencing is a module with separate member, control API, event, recording, and video components. Those boundaries support telephony participants, voice/video sessions, prompts, and recorded meetings without embedding each use case into the core switch.
- **C3:** each tick consumes a frame-sized quantity derived from sample rate, channel count, and interval, making the media deadline and buffering model explicit.

**Entry points:** [conference loop and lifecycle](https://github.com/signalwire/freeswitch/blob/master/src/mod/applications/mod_conference/mod_conference.c); [conference module decomposition](https://github.com/signalwire/freeswitch/tree/master/src/mod/applications/mod_conference).

## Search coverage and limitations

Discovery used more than six distinct live-web formulations, including: RTMP/SRT/RTSP server architecture; WebRTC SFUs and conferencing; Rust/Elixir media engines; audio streaming and voice servers; C++ OvenMediaEngine/ZLMediaKit/MistServer implementations; Java Red5/Ant Media servers; Kurento/Licode/BigBlueButton architecture; shared-memory broadcast designs; and project-specific repository-migration checks. Additional queries increasingly returned existing selections, downstream wrappers, tutorials, or client libraries. Primary evidence was then read through official GitHub repository/API access, source files, and project documentation. Canonical URLs, default branches, archive flags, and mirror descriptions were checked independently of search snippets.

Coverage spans broadcasting and conferencing; forwarding, mixing, and transcoding orchestration; single-process, subprocess/shared-memory, and multi-service designs; embedded engines and complete products; browser WebRTC, camera/broadcast protocols, telephony, and live radio. Smaller or less prominent implementations are included where their source provides concrete engineering material. Repository stars were not used as quality evidence.

Important boundaries and exclusions:

- Pion itself, libwebrtc, generic GStreamer/FFmpeg libraries, TURN-only infrastructure, players, and capture tools were not added merely because servers depend on them. This report focuses on implemented media servers and substantial conferencing backends.
- Simple demo SFUs, deployment wrappers around MediaMTX/mediasoup, duplicate forks, and obsolete repository names were excluded. Complete systems such as BigBlueButton and OpenMeetings are included for their own state/orchestration code, with dependency boundaries identified.
- Searches found references to Medooze's historical GitHub paths, but the upstream `medooze/media-server` and `medooze/media-server-node` endpoints could not be verified as accessible repositories during this pass. A downstream fork was not substituted as if it were the canonical upstream.
- Some older MistServer documentation URLs failed to load. Its implementation and the current official architecture overview supplied the retained evidence. Membrane RTC Engine is explicitly archived; ion-sfu and nginx-rtmp are marked with the limited activity observed, rather than being presented as actively maintained.
- This is source/document research, not an operational benchmark, security audit, or full code review. Candidate software was not installed or executed. Performance criteria describe mechanisms visible in the implementation; capacity, latency, and reliability in a particular deployment remain unmeasured. C4 is awarded only where multi-year compatibility/change evidence was actually inspected.
