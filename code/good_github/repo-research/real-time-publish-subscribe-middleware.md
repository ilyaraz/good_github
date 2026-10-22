# Real-time publish-subscribe middleware

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing publish-subscribe communication for responsive distributed applications, robotics, embedded devices, and interprocess data exchange. It includes DDS/RTPS, shared-memory middleware, brokerless messaging libraries, MQTT brokers, and servers that deliver live application events. “Real-time” here includes low-latency and soft real-time systems; inclusion does not establish hard deadline guarantees. The relevant subsystem is identified for broader repositories. Links within entries are suggested documentation and source-code entry points.

**Criteria legend:** **C1** — difficult correctness involving concurrency, invariants, protocol semantics, adversarial inputs, or failure recovery. **C2** — substantial reusable abstractions supporting multiple applications. **C3** — concrete performance constraints addressed through understandable architecture. **C4** — multi-year evolution accompanied by compatibility work, testing, or explicit complexity management. Criteria describe supported reasons to study a project, not a certification that every component is exemplary.

## DDS and RTPS implementations

### 1. [eProsima/Fast-DDS](https://github.com/eProsima/Fast-DDS)

**C++ · DDS implementation with a lower-level RTPS API.** Study how a standards-based data model connects discovery, writer histories, transport choices, and application-facing quality of service.

- **C1:** Data-sharing delivery couples reader and writer histories through the same shared-memory sample. Acknowledgement, sample reuse, and reader history depth therefore have observable consequences; the documentation explains when an earlier sample becomes inaccessible and the constraints on eligible types. This is a concrete ownership and delivery-semantics problem. [Data-sharing design](https://fast-dds.docs.eprosima.com/en/latest/fastdds/transport/datasharing.html).
- **C3:** Flow controllers bound transmitted bytes per period and separate scheduling policy, writer priority, bandwidth reservation, and sender-thread settings. The example explains where controllers attach to participants and writers, making bandwidth management traceable through the API. [Flow-control example and explanation](https://github.com/eProsima/Fast-DDS/blob/master/examples/cpp/flow_control/README.md).

### 2. [eclipse-cyclonedds/cyclonedds](https://github.com/eclipse-cyclonedds/cyclonedds)

**C · DDS implementation and DDSI-RTPS networking core.** A useful codebase for studying how a reliable distributed data space is built over datagrams, alongside the typed topic interface described in the repository.

- **C1:** Reliable writers retain samples in a writer history cache; readers detect gaps through heartbeats and request repairs with AckNack messages. Cache reclamation depends on reader acknowledgements, while unresponsive readers create an explicit failure-policy question. [Reliable-communication internals](https://github.com/eclipse-cyclonedds/cyclonedds/blob/master/docs/manual/about_dds/reliable_communication.rst).
- **C3:** The same design explains why heartbeat suppression and merging acknowledgements or retransmissions matter: overly aggressive timing can produce redundant repair traffic. This exposes the latency-versus-control-traffic tradeoff rather than merely advertising speed. Start in that document, then follow the [DDSI implementation](https://github.com/eclipse-cyclonedds/cyclonedds/tree/master/src/core/ddsi).

### 3. [OpenDDS/OpenDDS](https://github.com/OpenDDS/OpenDDS)

**C++ · DDS middleware with Java bindings, multiple transports, security, and extensible types.** Study the separation between discovery, data transport, generated serialization, and the common DDS layer.

- **C2:** RTPS is implemented as a pluggable transport plus a separately configured discovery mechanism. The design maps those responsibilities to the common DCPS, RTPS, and RTPS/UDP libraries and records interoperability-sensitive distinctions between discovery modes. [RTPS design notes](https://github.com/OpenDDS/OpenDDS/blob/master/docs/design/RTPS). These notes contain historical implementation limits, so use current release documentation when deciding feature support.
- **C4:** Release notes span multiple years and connect changes to concrete maintenance concerns: dependency upgrades, IDL mapping evolution, thread configuration, and fixes involving participant removal during deserialization. The 2026 notes also explain moving maintenance work away from network-reading reactor threads. [Release history](https://github.com/OpenDDS/OpenDDS/blob/master/NEWS.md).

### 4. [Atostek/RustDDS](https://github.com/Atostek/RustDDS)

**Rust · native DDS/RTPS implementation with Rust-oriented APIs.** Especially instructive for adapting DDS concepts to generic data readers/writers, Serde-based payload handling, and a nonblocking event loop.

- **C1:** The transmit design follows socket congestion all the way back to application writes. It treats control traffic, bulk samples, fragmented sends, reliable acknowledgement windows, and best-effort nonblocking semantics separately. [Nonblocking transmit design](https://github.com/Atostek/RustDDS/blob/master/src/rtps/nonblocking_transmit_design.md).
- **C3:** Per-socket scheduling and fragment resume positions prevent a large sample from monopolizing progress or repeatedly restarting. Read the document's **as-built notes**: control-message coalescing remains a future optimization, and repair traffic retries through subsequent reader NACKs rather than the resumable push path. These distinctions make it a valuable example of documenting the gap between a design and its implementation.

### 5. [s2e-systems/dust-dds](https://github.com/s2e-systems/dust-dds)

**Rust · DDS/RTPS implementation; the `dds` crate is the main subsystem.** Study protocol state machines alongside the mapping from DDS's object model to Rust types. The repository describes its DDS coverage as the minimum profile; this is not an assertion of every optional DDS feature.

- **C1:** The stateful writer tracks matched readers, acknowledged changes, heartbeat timing, durability-dependent starting positions, and monotonic AckNack/NackFrag counts. Its handlers distinguish stale control messages from new repair requests. [Stateful writer implementation](https://github.com/s2e-systems/dust-dds/blob/main/dds/src/rtps/stateful_writer.rs).
- **C2:** The design document examines generic writer creation, object-safety constraints, serialization versus key extraction, and typed listeners. These are reusable API-design problems beyond DDS. Treat its actor-model discussion as recorded design history, not independent proof of the current runtime organization. [Software design document](https://github.com/s2e-systems/dust-dds/blob/main/dds/docs/software_design.md).

### 6. [eProsima/Micro-XRCE-DDS-Client](https://github.com/eProsima/Micro-XRCE-DDS-Client)

**C · constrained-device DDS-XRCE client.** This is substantive middleware, not a generated DDS binding: clients use an agent to create DDS entities and mediate their publications and subscriptions.

- **C1:** Reliable streams handle acknowledgements, ordering, and fragmentation. A full stream history has different consequences for outgoing writes and incoming data that must be requested again. [Client streams and configuration](https://micro-xrce-dds.docs.eprosima.com/en/latest/client.html).
- **C3:** History depth and transport MTU determine stream-buffer size; smaller histories save memory but can increase repair traffic. Compile-time profiles let applications remove unneeded capabilities. Follow the documentation into the [output reliable-stream implementation](https://github.com/eProsima/Micro-XRCE-DDS-Client/blob/master/src/c/core/session/stream/output_reliable_stream.c) when studying the bounded-buffer machinery.

### 7. [embedded-software-laboratory/embeddedRTPS](https://github.com/embedded-software-laboratory/embeddedRTPS)

**C++ · embedded RTPS implementation using lwIP and FreeRTOS APIs.** Unlike an XRCE client, an Ethernet-capable microcontroller participates directly in a DDS system. This is a research-oriented implementation with explicitly rudimentary QoS, incomplete RTPS coverage, and message-size restrictions documented in its [project introduction](https://github.com/embedded-software-laboratory/embeddedRTPS/blob/master/Readme.md).

- **C2:** The implementation separates discovery, entities, message handling, storage, and platform-facing communication, offering a compact view of an RTPS participant on embedded systems.
- **C3:** Its thread pool separates incoming/outgoing user traffic from discovery-related traffic, uses semaphore notification when work is absent, and records queue-overflow diagnostics. Stack sizes and priorities are configuration inputs. [Thread-pool implementation](https://github.com/embedded-software-laboratory/embeddedRTPS/blob/master/src/ThreadPool.cpp).

The thread-pool source explicitly acknowledges unfinished runtime shutdown synchronization. Retain it as an implementation study, not evidence of production readiness or verified current maintenance.

## Shared memory, robotics, and edge-to-cloud middleware

### 8. [eclipse-iceoryx/iceoryx](https://github.com/eclipse-iceoryx/iceoryx)

**C++ · classic iceoryx shared-memory IPC.** The relevant subsystem is `iceoryx_posh`, supported by the `iceoryx_hoofs` containers and concurrency primitives. **Maintenance status:** the current README says classic iceoryx receives security fixes only, with no further major releases planned; the maintainers direct new development toward iceoryx2.

- **C1:** The lock-free queue design explains cyclic indices, compare-and-swap, capacity constraints, empty detection, and practical ABA avoidance. It explicitly distinguishes lock-free progress from wait-free fairness. [Queue design and proof sketch](https://github.com/eclipse-iceoryx/iceoryx/blob/main/doc/design/lockfree_queue.md).
- **C2:** Memory pools, ports, discovery, ABI checks, gateways, and the RouDi daemon have named architectural boundaries. These let engineers study reusable IPC infrastructure independently of the application payload. [Architecture](https://github.com/eclipse-iceoryx/iceoryx/blob/main/doc/website/concepts/architecture.md).

### 9. [eclipse-iceoryx/iceoryx2](https://github.com/eclipse-iceoryx/iceoryx2)

**Rust core with language bindings · successor implementation for shared-memory IPC.** Counted separately from classic iceoryx because it is a distinct Rust implementation, not a wrapper or mirror. Study typed pub-sub services and cross-process resource compatibility.

- **C1:** Opening a service checks payload types, messaging patterns, capacity requirements, overflow behavior, versions, and corrupted or incompletely created resources. Failure cases include another process dying during service creation. [Publish-subscribe service builder](https://github.com/eclipse-iceoryx/iceoryx2/blob/main/iceoryx2/src/service/builder/publish_subscribe.rs).
- **C3:** Zero-copy delivery depends on explicit payload-layout constraints and bounded resource settings. The backpressure example shows application-selected handling when delivery cannot proceed; its `ZeroCopySend` requirements explain why ordinary heap-owning objects cannot simply be put in shared memory. [Backpressure and payload requirements](https://github.com/eclipse-iceoryx/iceoryx2/blob/main/examples/rust/publish_subscribe_with_backpressure/README.md).

### 10. [eclipse-ecal/ecal](https://github.com/eclipse-ecal/ecal)

**C++ · brokerless enhanced Communication Abstraction Layer.** The core pub-sub implementation supports local shared-memory exchange and network delivery, with recording and diagnostic tools around it.

- **C2:** Transport policy distinguishes communication within a process, between processes, and between hosts. Transport layers can be configured at machine, process, or connection level while retaining a common messaging interface. [Transport-layer architecture](https://github.com/eclipse-ecal/ecal/blob/master/doc/rst/advanced/transport_layers.rst).
- **C1/C3:** Registration, monitoring, payload reception, shared-memory synchronization, and callbacks have distinct threading responsibilities. Payload lifetime is protected during callbacks, but a blocking subscriber callback can cause missed messages. This gives a concrete concurrency and latency boundary to study. [Threading model](https://github.com/eclipse-ecal/ecal/blob/master/doc/rst/advanced/threading_model.rst).

### 11. [lcm-proj/lcm](https://github.com/lcm-proj/lcm)

**C/C++ core, generators, and language bindings · Lightweight Communications and Marshalling.** A compact alternative for typed pub-sub in robotics and other latency-sensitive applications. Its UDP multicast protocol requires an agreed group and port; it does not supply automatic discovery.

- **C1:** The protocol makes channel naming, network byte order, sequence-number wraparound, and multi-datagram payload fragmentation explicit. These provide a focused study of wire-format and reassembly invariants. [UDP multicast protocol](https://github.com/lcm-proj/lcm/blob/master/docs/content/udp-multicast-protocol.md).
- **C4:** Release history runs from 2008 through 2026 and records platform and language compatibility work, generator changes, and fixes such as unsubscribing while a callback is active and UDP overflow handling. [Release history](https://github.com/lcm-proj/lcm/blob/master/NEWS.md). The README flags Go and C# bindings as unmaintained, so maintenance is not uniform across the repository.

### 12. [eclipse-zenoh/zenoh](https://github.com/eclipse-zenoh/zenoh)

**Rust · pub-sub, query, and storage middleware with a router daemon.** Count the `zenoh`, `zenoh-ext`, transport crates, and `zenohd` as one repository. Study how live distribution and queryable data share an addressing model.

- **C2:** Key expressions describe sets of keys; publishers, subscribers, queryables, and storage components compose around that common model. The canonical expression rules and separation of routing selectors from query parameters give the abstraction precise semantics. [Abstractions manual](https://zenoh.io/docs/manual/abstractions/).
- **C3:** The transport pipeline separates serialization batches, reusable batch storage, ring-buffer stages, priority channels, notification, and deadline/backoff behavior. The source explains why batches are boxed and reused instead of repeatedly moved or allocated. [Transmission pipeline](https://github.com/eclipse-zenoh/zenoh/blob/main/io/zenoh-transport/src/common/pipeline.rs).

### 13. [eclipse-zenoh/zenoh-pico](https://github.com/eclipse-zenoh/zenoh-pico)

**C · native Zenoh implementation for constrained devices.** This is a separate implementation rather than a binding to the Rust core. Its platform and transport matrix spans desktop systems and embedded/RTOS environments.

- **C2:** Session and transport boundaries support the same pub-sub ecosystem across multiple network transports and operating-system ports. Compile-time feature gates make those abstractions usable under constrained configurations. [Project architecture and platform overview](https://github.com/eclipse-zenoh/zenoh-pico/blob/main/README.md).
- **C1:** The unicast lease machinery coordinates peer expiry, interest removal, liveliness notifications, transport cleanup, locking, and optional reconnection through the executor. Weak session ownership must survive cleanup when reconnection is requested. [Unicast lease and failure handling](https://github.com/eclipse-zenoh/zenoh-pico/blob/main/src/transport/unicast/lease.c).

## Brokerless messaging and low-latency transport libraries

### 14. [zeromq/libzmq](https://github.com/zeromq/libzmq)

**C++ · ZeroMQ messaging engine; focus on PUB/SUB and XPUB/XSUB.** Study message-oriented sockets and composable subscription forwarding without requiring a central broker.

- **C2:** PUB/SUB supplies fan-out and subscriber filtering; XPUB/XSUB exposes subscription control messages so applications can construct forwarding devices. The manual states that PUB drops messages for a subscriber at its high-water mark rather than blocking the sender. [Socket-pattern semantics](https://github.com/zeromq/libzmq/blob/master/doc/zmq_socket.adoc).
- **C1/C3:** The distributor maintains matching, active, and eligible pipe regions, defers newly attached pipes during multipart sends, and accounts for message references when writes fail. This connects efficient fan-out directly to multipart and lifetime invariants. [Distributor implementation](https://github.com/zeromq/libzmq/blob/master/src/dist.cpp).

### 15. [nanomsg/nng](https://github.com/nanomsg/nng)

**C · brokerless messaging library; focus on the pubsub0 protocol.** NNG is a substantive rewrite of nanomsg with its own evolution. Its default branch currently documents development toward a breaking major version and directs production users to `stable`; the links below describe the inspected development branch.

- **C2:** Sockets and independently subscribed contexts separate application protocol state from a connection. Raw and cooked modes expose different levels of control, while subscriptions are byte-prefix matches. [SUB protocol and context API](https://github.com/nanomsg/nng/blob/main/docs/ref/proto/sub.md).
- **C1:** Buffer overflow is a defined semantic choice: retain old messages or discard them in favor of new ones. Filtering happens on subscribers; publishers send to every subscriber, so topic filtering does not reduce transmitted bandwidth. These details prevent incorrect assumptions about loss and fan-out. [PUB protocol](https://github.com/nanomsg/nng/blob/main/docs/ref/proto/pub.md).

### 16. [aeron-io/aeron](https://github.com/aeron-io/aeron)

**Java and C, with C++ interfaces · reliable UDP and IPC message transport.** This is the canonical repository reached from the former `real-logic/aeron` location. Focus on publications, subscriptions, and the transport; Archive and Cluster are additional subsystems in the same monorepo.

- **C1/C3:** `Publication` exposes nonblocking `offer` and `tryClaim`, distinguishes backpressure from disconnects and administrative retries, and documents the different thread-safety contracts of concurrent versus exclusive publications. Term buffers and position limits make the implementation strategy visible. [Publication API and implementation](https://github.com/aeron-io/aeron/blob/master/aeron-client/src/main/java/io/aeron/Publication.java).
- **C4:** The multi-year changelog records continued work on wire/URI validation, memory ordering, fragment assembly, architecture portability, and object lifetimes. It distinguishes unreleased changes from dated releases, allowing investigation of how low-latency primitives evolve safely. [Changelog](https://github.com/aeron-io/aeron/blob/master/CHANGELOG.adoc).

## Brokered and application-facing live messaging

### 17. [nats-io/nats-server](https://github.com/nats-io/nats-server)

**Go · subject-based messaging server.** Focus here on Core NATS routing; JetStream is a separate persistence subsystem within the same repository. Core NATS is explicitly at-most-once and sends to currently connected subscribers. [Core semantics](https://docs.nats.io/learn/core-nats/).

- **C3:** The subscription index represents subject tokens and wildcard branches separately, groups queue subscriptions, and uses a bounded match cache. Its comments discuss why heavy subscription churn can make caching counterproductive. [Subscription index](https://github.com/nats-io/nats-server/blob/main/server/sublist.go).
- **C1:** The source matches subscriptions under a lock when registering interest-change notifications to avoid missing concurrent changes. The repository also documents lock ordering and reload synchronization across server, client, and account state. [Lock-ordering rules](https://github.com/nats-io/nats-server/blob/main/locksordering.txt).

### 18. [nsqio/nsq](https://github.com/nsqio/nsq)

**Go · distributed real-time messaging platform.** Topics fan messages out to independent channels; consumers within a channel share work. This gives it both pub-sub and queueing behavior, so the topic/channel delivery subsystem is the relevant scope.

- **C1:** Delivery uses consumer readiness, FIN/REQ acknowledgements, timeout requeueing, and application idempotency. The design candidly identifies message loss from unclean shutdown when data remains in memory or unflushed buffers; its at-least-once description must be read with that boundary. [Design and delivery guarantees](https://nsq.io/overview/design.html).
- **C3:** Configurable in-memory queue depth spills excess messages to disk, while ephemeral channels deliberately discard overflow. The same design explains push-based delivery and operational topology choices. The [channel implementation](https://github.com/nsqio/nsq/blob/master/nsqd/channel.go) is the next source entry point.

### 19. [centrifugal/centrifugo](https://github.com/centrifugal/centrifugo)

**Go · channel-based server for browser, mobile, and other live application clients.** Backends publish through server APIs while clients maintain subscriptions over supported persistent transports. Study the server's recovery, authentication, and channel-policy integration; some messaging primitives are supplied by its Centrifuge library dependency.

- **C1:** Recovery identifies a stream by both epoch and offset. A recreated stream cannot reuse an old client's position, and recovery succeeds only when the entire missing interval remains available. [History and recovery design](https://centrifugal.dev/docs/server/history_and_recovery).
- **C3:** History is bounded by size and TTL, with separate metadata lifetime and a recovery publication limit. It is an intentionally limited cache for brief disconnects and reconnect bursts; failed continuity requires reloading authoritative application state. The design makes that performance-versus-retention boundary explicit rather than promising durable delivery.

### 20. [crossbario/crossbar](https://github.com/crossbario/crossbar)

**Python · WAMP application router with a pub-sub broker and routed RPC.** A useful contrast to C/C++ transport stacks: routing, process management, security domains, and application integration are central abstractions.

- **C2:** A node controller manages router, container, and guest workers. Router realms separate routing and administration; roles govern topic and procedure access. These abstractions support heterogeneous application components. [Architecture in the getting-started guide](https://crossbario.readthedocs.io/en/stable/Getting-Started.html).
- **C1:** The broker maintains both subscription observations and per-session membership, cleans up on detach, preserves subscriptions with retained events, and emits subscription lifecycle events. The implementation exposes the invariants connecting session lifetime, retention, and observer removal. [Broker implementation](https://github.com/crossbario/crossbar/blob/master/src/crossbar/router/broker.py).

## MQTT brokers for telemetry and live device messaging

### 21. [eclipse-mosquitto/mosquitto](https://github.com/eclipse-mosquitto/mosquitto)

**C · MQTT broker, client library, and utilities.** Focus on the broker's MQTT 3.x/5 delivery machinery. Its relatively direct protocol handlers make it useful for tracing how a received publication becomes stored state, an acknowledgement, or subscriber delivery.

- **C1:** Publication handling distinguishes QoS levels, duplicated or reused message identifiers, ACL rejection, queue quotas, message expiry, and acknowledgement responses. The current source even documents a compatibility compromise around receive-maximum enforcement. [Broker publication handler](https://github.com/eclipse-mosquitto/mosquitto/blob/master/src/handle_publish.c).
- **C4:** The changelog records releases across well over a decade, protocol evolution, persistence migration, deprecations, platform tests, and fixes to thread-creation failure and will/session-expiry interactions. This is concrete evidence of managing compatibility and failure behavior over time. [Changelog](https://github.com/eclipse-mosquitto/mosquitto/blob/master/ChangeLog.txt).

### 22. [emqx/emqx](https://github.com/emqx/emqx)

**Erlang/OTP · distributed MQTT platform; focus on `apps/emqx`.** The repository is broader than messaging, but its broker and routing subsystem is directly relevant. The README states that releases starting with 5.9 use **BSL 1.1**; it should be described as source-available rather than assuming its former open-source licensing.

- **C2:** The broker separates subscription operations, publish hooks, persistence acceptance, local dispatch, remote-node forwarding, and shared-subscription routing. Legacy publish functions preserve their return format while newer functions expose the transformed message. [Broker implementation](https://github.com/emqx/emqx/blob/master/apps/emqx/src/emqx_broker.erl).
- **C1/C3:** Subscription setup assigns shards and can wait for route synchronization. Publishing aggregates routes, filters unroutable destinations, and deduplicates shared routes before dispatch. This is a concrete intersection of parallel routing, cluster state, and delivery correctness, visible in the same implementation.

### 23. [vernemq/vernemq](https://github.com/vernemq/vernemq)

**Erlang/OTP · distributed MQTT broker.** Study stateful client queues and the tension between MQTT session guarantees and an eventually consistent cluster.

- **C1:** The netsplit documentation identifies a detection window in which remote subscriptions can be missed or duplicate client identities can survive. Partition-time operations are configurable, and subscription/retained-message state converges after healing. This is unusually explicit material about real failure boundaries. [Network-partition behavior](https://docs.vernemq.com/vernemq-clustering/netsplits.md).
- **C2/C3:** Each subscriber queue has explicit online, offline, wait-for-offline, and drain states, with session membership, expiry, delayed wills, queue limits, and batched migration. The decomposition makes session lifecycle and bounded delivery work independently understandable. [Queue state machine](https://github.com/vernemq/vernemq/blob/main/apps/vmq_server/src/vmq_queue.erl).

### 24. [nanomq/nanomq](https://github.com/nanomq/nanomq)

**C · edge MQTT broker and messaging bus.** The canonical owner is `nanomq`; some documentation still uses the earlier `emqx/nanomq` address. Study its broker as a separate application built on an NNG-derived networking layer, not as another copy of NNG itself.

- **C2:** `nano_work` supplies a common worker/state-machine structure for broker, HTTP, and bridge paths. Protocol handlers, ACL processing, configuration, and optional integrations are separate components. [Code structure and state-machine guide](https://github.com/nanomq/nanomq/blob/master/CodeGuidance.md).
- **C1/C3:** INIT/RECV/SEND/WAIT/END/CLOSE transitions make asynchronous processing, will-message handling, disconnect generation, and message cleanup explicit. Together with the repository's explanation of NNG-based asynchronous I/O, this offers a compact study of concurrency on edge hardware. The guide warns that its directory sketch may lag changes; use the [current broker source](https://github.com/nanomq/nanomq/blob/master/nanomq/apps/broker.c) for navigation.

### 25. [bytebeamio/rumqtt](https://github.com/bytebeamio/rumqtt)

**Rust · MQTT ecosystem monorepo; focus on the embeddable `rumqttd` broker.** Count `rumqttd` and `rumqttc` once. The broker is interesting for its separation between asynchronous network links and a router that owns scheduling and data-log consumption.

- **C1:** Connection state includes pending acknowledgements, inflight limits, subscription progress, and state saved across disconnects. The architecture describes rejection of unsolicited or out-of-order acknowledgements and the transitions that make a blocked connection eligible again. [Broker architecture](https://github.com/bytebeamio/rumqtt/blob/main/rumqttd/architecture.md).
- **C3:** Shared input/output buffers carry events while channels notify the router that work exists. A ready queue and parked data requests avoid spinning on caught-up connections; explicit rescheduling handles a network link whose output buffer has filled. The same document gives an unusually concrete path from these data structures to backpressure behavior.

## Search coverage and limitations

Discovery used more than six distinct live-web formulations, including **DDS/RTPS architecture**, **Rust DDS implementations**, **shared-memory robotics pub-sub**, **embedded RTOS middleware**, **Zenoh-pico and DDS-XRCE**, **brokerless low-latency transports**, **MQTT broker architectures**, **WAMP routing**, and **WebSocket message recovery**. Follow-up searches targeted acknowledgement histories, congestion control, netsplits, and less prominent implementations. The final embedded and brokerless passes largely returned already-covered families, wrappers, or adjacent systems; embeddedRTPS was the last addition because direct RTPS on microcontrollers added a distinct design.

Canonical URLs were checked through the GitHub API for 24 entries and by opening the repository page for embeddedRTPS. Repository introductions and at least one separate substantive design, implementation, protocol, or API source were read for every entry. GitHub API rate limiting affected the final candidate check; public repository pages and raw source remained available. Source-tree links were checked against repository trees or successfully retrieved files. No repositories were cloned, built, or benchmarked.

The report favors middleware implementations over generated bindings, tiny event emitters, tutorials, and integration-only adapters. Durable event-log platforms, general work queues, databases with a pub-sub feature, and whole robotics/operating-system monorepos were outside the main selection. Additional MQTT brokers such as FlashMQ were discovered but omitted to keep that already well-represented family proportionate; omission is not a quality judgment. ROS middleware adapters and language bindings are not counted again as independent implementations.

Classic iceoryx's maintenance-only status, NNG's development-branch warning, LCM's unmaintained bindings, EMQX's licensing change, and embeddedRTPS's incomplete coverage are called out where relevant. No retained repository is presented as an official mirror or as an archived project. Repository availability and recent activity do not by themselves establish maintenance quality; C4 is used only where release-history content supports it. Source and default-branch links can change, and some design notes are historical. The study recommendations are engineering judgments grounded in the cited mechanisms, not proof of specification conformance, suitability for a particular deployment, or comparative performance.
