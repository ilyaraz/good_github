# Federated messaging and chat servers

Research date: **2026-10-09**.

This selection covers **20 GitHub repositories** implementing Matrix homeservers, federating XMPP servers, linked IRC servers, and decentralized messaging relays. The last subgroup deliberately distinguishes relay and rendezvous architectures from domain-based federation. The emphasis is on implementation study: event consistency, authentication state machines, recovery, routing, resource limits, and extensible server design. Historical implementations are included where they offer substantial, distinct engineering material; inclusion is not a deployment recommendation or a claim that every component is exemplary.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial inputs, or failure recovery.
- **C2 — Abstractions:** substantial reusable interfaces or subsystems supporting multiple uses.
- **C3 — Performance architecture:** concrete resource or throughput constraints addressed through an understandable design.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or complexity management. Age or a recent push alone does not qualify.

## Matrix homeservers

### 1. [element-hq/synapse](https://github.com/element-hq/synapse)

**Language/role:** Python with Rust components; Matrix homeserver. A strong starting point for studying how a persistent, federated event graph is divided among cooperating processes without losing ordering guarantees.

- **C1:** The worker design assigns writers to replication streams and restricts which streams can have multiple writers. Event persistence workers own rooms, connect events into their graphs, and publish persistence progress. The same documentation warns that pagination and history purging must not run concurrently for a room, exposing a specific cross-worker correctness constraint. [Worker architecture and routing rules](https://element-hq.github.io/synapse/latest/workers.html).
- **C3:** Workers share PostgreSQL and use Redis for replication and cache coordination, with HTTP for operations requiring replies. Routing rules separate expensive initial synchronization from ordinary synchronization and distribute event persistence by room. Study the relationship between partitioning, affinity, and the work that remains centralized, rather than treating “more workers” as a universal scaling solution. [Worker configuration and scaling](https://element-hq.github.io/synapse/latest/workers.html).

### 2. [element-hq/dendrite](https://github.com/element-hq/dendrite)

**Language/role:** Go; Matrix homeserver. **Maintenance mode:** the repository says security fixes only, identifies the implementation as beta, and does not promise high availability or clustering. Its current room-input implementation is more useful evidence than older descriptions of a proposed microservice architecture.

- **C1:** The roomserver input path acknowledges messages after processing; cancellation leaves work available for redelivery. Durable consumer lifetime is distinct from a subscription's lifetime, and cleanup coordinates access to avoid races between dispatch and consumer removal. These are concrete recovery and lifecycle invariants. [Roomserver input implementation](https://raw.githubusercontent.com/element-hq/dendrite/main/roomserver/internal/input/input.go).
- **C3:** A headers-only dispatcher discovers rooms on a shared NATS stream, then creates per-room consumers and workers. A slow room can therefore make progress independently of unrelated rooms while each room retains serial processing. This is a useful example of separating scheduling fairness from ordering requirements. [Input dispatcher and worker code](https://raw.githubusercontent.com/element-hq/dendrite/main/roomserver/internal/input/input.go).

### 3. [matrix-construct/tuwunel](https://github.com/matrix-construct/tuwunel)

**Language/role:** Rust; Matrix homeserver and the stated successor to conduwuit. Counted once for this implementation line; conduwuit is not added as a second entry.

- **C1:** The event handler coordinates authorization, missing-event retrieval, state derivation, and timeline insertion across federation ingress paths. It explicitly documents lock acquisition order—federation, state, then insertion—and bounds candidate-server retries during dependency retrieval. Study how network recursion interacts with local locking and room state. [Room event handler](https://github.com/matrix-construct/tuwunel/blob/main/src/service/rooms/event_handler/mod.rs).
- **C2:** The workspace separates HTTP/API handling, domain services, database access, administration, and shared core facilities. Its development guide explains the relationship between Axum/Tower routing, services, and RocksDB, as well as the library boundaries used for development and reloading. These are substantial boundaries inside a full server, not merely a plugin registry. [Development architecture](https://github.com/matrix-construct/tuwunel/blob/main/docs/development.md).

### 4. [matrix-construct/construct](https://github.com/matrix-construct/construct)

**Language/role:** C++; historical Matrix homeserver. The [official Matrix server catalog](https://github.com/matrix-org/matrix.org/blob/main/content/ecosystem/servers/servers.toml) labels Construct **obsolete**. Its older architecture remains a distinct study target, particularly for readers interested in explicit I/O control.

- **C2:** The `libircd` interface is designed for embedding and groups dependencies behind library-facing headers. Its integration notes explain initialization, module-specific header stacks, and a single-threaded embedding requirement. This exposes both the reusable library surface and its integration constraints. [Library interface notes](https://github.com/matrix-construct/construct/blob/master/include/ircd/README.md).
- **C3:** The tuning guide relates asynchronous filesystem I/O, direct I/O, RocksDB caching, and device queue depth to avoiding blocking in the server. It also explains why page faults and cache residency matter to that execution model. Read this as a historical account of engineering tradeoffs, not as current operating-system tuning advice. [I/O and cache design notes](https://github.com/matrix-construct/construct/wiki/TUNING).

### 5. [palpo-im/palpo](https://github.com/palpo-im/palpo)

**Language/role:** Rust; Matrix homeserver using Salvo and PostgreSQL. A newer alternative whose README explicitly acknowledges a lack of large-scale production and prolonged federation experience. It describes Conduit inspiration and substantial reworking, rather than claiming to be a Tuwunel fork.

- **C1:** State-event creation is performed under a room-state lock and checks event-specific invariants before appending the event. Examples include immutable creation events, locally valid canonical aliases, restricted-join authorization, administrative-room visibility restrictions, and room-version-dependent power-level rules. [State-event validation and insertion](https://github.com/palpo-im/palpo/blob/main/crates/server/src/state.rs).
- **C2:** The workspace separates shared protocol/data types, identifier validation, macros, and server implementation. Typed room/user identifiers and raw typed event contents feed a common state-event construction path rather than every endpoint implementing its own representation. Study this boundary between protocol vocabulary and server policy. [Workspace crates](https://github.com/palpo-im/palpo/tree/main/crates).

## XMPP servers

### 6. [processone/ejabberd](https://github.com/processone/ejabberd)

**Language/role:** Erlang; multiprotocol messaging server. This entry concerns its **XMPP routing, session, and server-to-server subsystems**; its other protocols do not count as separate repositories.

- **C2:** The architecture centers on a router with extension modules and replaceable storage backends. Cluster documentation further decomposes delivery into a domain router, local router, session manager, and server-to-server manager. The separation makes local presence, offline delivery, and remote-domain routing understandable as cooperating services. [Architecture guide](https://docs.ejabberd.im/developer/extending-ejabberd/architecture/).
- **C3:** Cluster nodes exchange session and route information through Erlang distribution. Component load balancing prefers a local instance before a remote instance, while optional fixed buckets trade dynamic redistribution for session affinity. The guide also states the low-latency networking assumption and restart-order constraint after a complete cluster shutdown. [Clustering and load-balancing design](https://github.com/processone/docs.ejabberd.im/blob/master/content/admin/guide/clustering.md).

### 7. [esl/MongooseIM](https://github.com/esl/MongooseIM)

**Language/role:** Erlang; XMPP server with clustering and extensive service modules. Its [official history](https://esl.github.io/MongooseDocs/5.0.0/History/) documents the ejabberd fork, subsequent refactoring, and independent development. Its separately developed modules and host/service/storage architecture make it a substantive implementation to study alongside ejabberd.

- **C2:** Per-host modules and global services have different lifecycles and dependency ordering. The architecture distinguishes transient session state from durable archives and configuration, with different storage choices for each. Study this separation when considering how to extend a messaging service without making every module responsible for deployment topology. [High-level architecture](https://esl.github.io/MongooseDocs/6.8.0/user-guide/High-level-Architecture/).
- **C1 and C3:** The broadcast subsystem snapshots recipients, processes rate-limited batches, and checkpoints progress. Database leases assign job ownership; workers pause when ownership cannot be synchronized and another node can resume after lease expiry. The documentation explicitly permits duplicates around failures and supplies deterministic message IDs for deduplication. This combines load control with an honest delivery contract. [Broadcast ownership, recovery, and batching](https://github.com/esl/MongooseIM/blob/master/doc/modules/mod_broadcast.md).

### 8. [igniterealtime/Openfire](https://github.com/igniterealtime/Openfire)

**Language/role:** Java; XMPP server. Particularly useful for studying the interaction between nonblocking network processing, blocking enterprise integrations, and extension lifecycle requirements.

- **C3:** The networking guide separates Netty acceptor and I/O event loops from a blocking executor used for operations such as authentication, routing, and persistence. Connection types have their own acceptors, including server-to-server traffic and different TLS modes. The architectural lesson is where blocking work is moved so it does not starve network progress. [Internal networking](https://download.igniterealtime.org/openfire/docs/latest/documentation/internal-networking.html).
- **C2:** `AuthProvider` gives internal authentication and SASL code a common interface over default, JDBC, and LDAP implementations, including read-only providers. The provider guide explains why these implementations cannot simply follow ordinary unloadable plugin lifecycle: authentication must be available during startup and throughout service operation. [Authentication provider interface and lifecycle](https://download.igniterealtime.org/openfire/docs/latest/documentation/implementing-authprovider-guide.html).

### 9. [tigase/tigase-server](https://github.com/tigase/tigase-server)

**Language/role:** Java; XMPP server core. The repository identifies GitHub as the project's current source location. This entry covers the server core, rather than counting separately packaged Tigase extensions again.

- **C2:** `AbstractMessageReceiver` supplies a common foundation for packet-processing components such as session management, group chat, and publish/subscribe. It integrates component lifecycle, incoming/outgoing queues, statistics, and timeout-aware packet writing. [Shared receiver implementation](https://github.com/tigase/tigase-server/blob/master/src/main/java/tigase/server/AbstractMessageReceiver.java).
- **C1 and C3:** The same class documents concurrent packet processing and hashes a user's packets toward the same processing queue. It explicitly notes that priority handling can change ordering. Bounded queues, blocking enqueue behavior, and CPU/memory-related sizing expose the tradeoff between overload control, parallelism, and per-user ordering. This is a useful place to inspect assumptions before implementing a new component. [Queue and concurrency contract](https://github.com/tigase/tigase-server/blob/master/src/main/java/tigase/server/AbstractMessageReceiver.java).

### 10. [maranda/metronome](https://github.com/maranda/metronome)

**Language/role:** Lua with C support; XMPP server. Its README identifies a Prosody origin and substantial subsequent divergence, including core routing and group-chat/publish-subscribe APIs. It is retained as a distinct implementation, not as a mirror of Prosody.

- **C1:** The server-to-server module queues traffic until authentication, tracks connection inactivity, and handles dialback and certificate verification. Its bounce logic avoids responding to error/result stanzas with further errors, while certificate-chain validity and the asserted peer identity are checked separately. These details make it useful for studying failure handling in federated XML streams. [Server-to-server implementation](https://github.com/maranda/metronome/blob/master/plugins/mod_s2s/mod_s2s.lua).
- **C2:** Remote delivery is integrated through per-host hooks, explicit dependencies, and handlers for existing versus newly established connections. The module connects routing policy, transport establishment, authentication, and deferred delivery through shared host/session abstractions. Follow those boundaries to see how a compact dynamic-language server supports multiple virtual hosts and protocol extensions. [Module registration and routing hooks](https://github.com/maranda/metronome/blob/master/plugins/mod_s2s/mod_s2s.lua).

### 11. [ortuman/jackal](https://github.com/ortuman/jackal)

**Language/role:** Go; XMPP server. **Archived on 2023-11-03.** Retained for its explicit stream-state and component-interface design, without implying current maintenance.

- **C1:** The inbound server-to-server stream has explicit connecting, connected, dialback-authorizing, and disconnected states. A run queue serializes stream actions, disconnects, and deadlines; context cancellation and synchronization coordinate lifetime. Stanza-size limits and input shaping sit beside protocol processing rather than being left entirely to callers. [Inbound federation stream](https://github.com/ortuman/jackal/blob/main/pkg/s2s/in.go).
- **C2:** Transport, routing, cluster key/value state, shapers, and hooks are injected through distinct interfaces. This makes the federation stream a reusable protocol component with separable infrastructure dependencies. The [release history](https://github.com/ortuman/jackal/releases) supplies additional implementation context, including channel-binding compatibility changes and writer-buffer limits; it is historical evidence, not an indication that releases continue.

### 12. [jabberd2/jabberd2](https://github.com/jabberd2/jabberd2)

**Language/role:** C; **archived** XMPP server. A historical study of a multiprocess design with separate router, client-to-server, server-to-server, and session-manager daemons, as described in the repository README.

- **C1:** Outgoing federation tracks authentication state per source/destination route, queues packets while DNS or connection establishment is incomplete, and either flushes or bounces queues after dialback results. DNS handling distinguishes expired, reusable, and temporarily bad destinations. The source includes a detailed event/action outline alongside the implementation. [Outgoing server-to-server state machine](https://github.com/jabberd2/jabberd2/blob/master/s2s/out.c).
- **C2:** The daemon split assigns client authentication, interdomain transport, internal routing, and session features to separate processes. The protocol inventory maps capabilities to these components, making the architectural division concrete. Its protocol versions are historical and should not be interpreted as a present-day compliance statement. [Component-oriented protocol inventory](https://github.com/jabberd2/jabberd2/blob/master/README.protocol).

## Linked IRC servers

These servers implement federation within configured IRC networks. Their linking and reconciliation models differ from open Matrix or XMPP domain federation; that difference is part of their value for comparison.

### 13. [inspircd/inspircd](https://github.com/inspircd/inspircd)

**Language/role:** C++; modular IRC server. The relevant subsystem is `spanningtree`. The repository flags `master` as development code; the linked module guide describes the released version 4 interface.

- **C1:** `FJOIN` reconciles channel creation timestamps, membership, and modes after links join or reconnect. Its comments explain why the older timestamp wins and why the reconciliation decision must be propagated consistently: letting downstream servers make different decisions can desynchronize channel state. [FJOIN reconciliation](https://github.com/inspircd/inspircd/blob/master/modules/spanningtree/fjoin.cpp).
- **C2:** The spanning-tree module encapsulates network linking, link authentication, automatic reconnection/failover configuration, and protocol-capability requirements within the larger server's module system. Comparing its public configuration contract with the command handler shows how reusable mode and membership machinery is exposed through a specific interserver protocol. [Spanning-tree module guide](https://docs.inspircd.org/4/modules/spanningtree/).

### 14. [unrealircd/unrealircd](https://github.com/unrealircd/unrealircd)

**Language/role:** C; modular IRC server. A good pairing with InspIRCd for comparing extensible core APIs and synchronization of channel state across server links.

- **C1:** The server-only `SJOIN` command reconciles users, channel modes, and ban/exemption/invitation lists. The implementation must also translate one incoming server message into several client-visible changes, handling message tags and output-size limits during that expansion. Study the difference between the compact network synchronization operation and the notifications clients observe. [SJOIN implementation](https://github.com/unrealircd/unrealircd/blob/unreal60_dev/src/modules/sjoin.c).
- **C2:** The module API supports registered commands, hooks, overrides, and extension-defined behavior. The SJOIN module is a concrete example of a protocol feature built through that API rather than an unrelated plugin demo. [Module API](https://www.unrealircd.org/docs/Dev:Module_API).

### 15. [solanum-ircd/solanum](https://github.com/solanum-ircd/solanum)

**Language/role:** C; IRC daemon in the charybdis/ratbox lineage. Its technical documentation is especially valuable for connecting distributed protocol rules with low-level network-buffer contracts.

- **C1:** The TS6 specification explains server/user identifiers, spanning-tree propagation, negotiated capabilities, and deterministic handling of nickname collisions. It distinguishes unrecognized commands that terminate a link from extensible encapsulated commands that can be forwarded without local interpretation. [TS6 technical specification](https://github.com/solanum-ircd/solanum/blob/main/doc/technical/ts6.md).
- **C3:** The line-buffer notes cover partial nonblocking writes, incomplete lines, overflow handling, and accounting for allocated memory separately from useful bytes. The latter matters because many tiny lines can consume substantially more memory than their payload suggests. Read the documented buffer invariants as an implementation study; proposed features in the notes are not assumed to be implemented. [Line-buffer design](https://github.com/solanum-ircd/solanum/blob/main/doc/technical/linebuf.txt).

### 16. [ngircd/ngircd](https://github.com/ngircd/ngircd)

**Language/role:** C; comparatively compact IRC server with server linking. Useful for studying protocol compatibility without starting from a large extension ecosystem.

- **C1:** The protocol notes describe negotiated IRC+ extensions, the extended PASS handshake, and pre-registration capability checks. They also explain deliberate departures from strict RFC interpretation and the consequences of enabling strict mode. This exposes the boundary between syntactic compatibility and interoperable behavior. [Protocol and server-link negotiation](https://github.com/ngircd/ngircd/blob/master/doc/Protocol.txt).
- **C4:** The changelog provides concrete evidence across 2024–2026: certificate-validation behavior changes, portability and CI work, and fixes for busy spinning on unterminated input and enforcing advertised KICK/TOPIC limits. These entries tie ongoing evolution to failure modes and compatibility, rather than relying on repository age. [Release changelog](https://github.com/ngircd/ngircd/blob/master/ChangeLog).

### 17. [ircd-hybrid/ircd-hybrid](https://github.com/ircd-hybrid/ircd-hybrid)

**Language/role:** C; IRC server. Study channel reconciliation together with the project's explicit management of changes to server-link compatibility and module APIs.

- **C1:** The `SJOIN` handler reconciles timestamped channel state and modes. Removing or announcing mode lists must respect bounded parameter/message buffers, so distributed-state decisions and wire-format limits meet in the same implementation. [SJOIN state and mode handling](https://github.com/ircd-hybrid/ircd-hybrid/blob/8.2.x/modules/m_sjoin.c).
- **C4:** Release notes spanning 2020–2025 document module API rewrites, dynamic mode changes, minimum compatible linking versions, and corresponding services compatibility requirements. They provide unusually direct evidence of how a long-lived network service communicates intentional incompatibilities while restructuring internals. [Compatibility and architecture release notes](https://github.com/ircd-hybrid/ircd-hybrid/blob/8.2.x/NEWS.md).

### 18. [DALnet/bahamut](https://github.com/DALnet/bahamut)

**Language/role:** C; IRC daemon associated with DALnet. Its legacy, network-specific architecture offers a different study target from broadly configurable contemporary server frameworks; this entry makes no current-maintenance claim.

- **C1:** Server establishment rechecks for duplicate server connections after authentication because another connection may have won the race. The code resolves duplicate links and introduces servers before sending users, preserving topology assumptions during a network burst. [Server establishment and synchronization](https://github.com/DALnet/bahamut/blob/master/src/m_server.c).
- **C3:** The synchronization code groups user introductions by channel to improve allocation locality at the receiving server, uses markers to avoid duplicate introductions, and then sends users not already covered by a channel. This is an explicit performance decision embedded in a readable protocol phase. [Burst ordering implementation](https://github.com/DALnet/bahamut/blob/master/src/m_server.c). The separate [module notes](https://github.com/DALnet/bahamut/blob/master/doc/modules.txt) explain its older shared-library hook system and provide another route into the codebase.

## Decentralized messaging relay and rendezvous servers

These two projects broaden the comparison to chat infrastructure that does not replicate a conventional room database between domain servers. They are included for their substantive server implementations and messaging-specific protocols, rather than as generic message brokers.

### 19. [simplex-chat/simplexmq](https://github.com/simplex-chat/simplexmq)

**Language/role:** Haskell; SimpleX messaging and related server infrastructure. The selected subsystem is the SMP relay/router, which supports independently operated servers and client-selected receiving routes.

- **C1:** The protocol assigns separate sender/recipient queue IDs and authorization keys, defining who can send, retrieve, and acknowledge messages. It also states that routers retain messages only until acknowledgment or expiry; stronger reliability belongs to higher layers. This is useful for studying privacy-oriented capability design with an explicit failure contract, without treating cryptographic design claims as an independent audit. [SMP protocol and queue model](https://github.com/simplex-chat/simplexmq/blob/stable/protocol/simplex-messaging.md).
- **C2:** A unidirectional queue is the reusable primitive. Duplex conversations, redundancy, and higher-level group behavior are composed above it; the architecture separates routers, client libraries/agents, and applications. Optional proxy routing further separates the sender's network connection from the recipient's selected router. [System architecture overview](https://github.com/simplex-chat/simplexmq/blob/stable/protocol/overview-tjr.md).

### 20. [ssbc/go-ssb-room](https://github.com/ssbc/go-ssb-room)

**Language/role:** Go; Secure Scuttlebutt room server for peer discovery and tunneled connections, with membership and administration. A room here is a rendezvous service, not a Matrix-style replicated message history. Repository metadata showed the last push in 2023; current maintenance is not asserted.

- **C1:** The tunnel handler validates the requested portal, derives the caller from the authenticated network address, rejects self-connections, and checks that the target is present. Two forwarding goroutines share cancellation; errors propagate through the streams, and session termination removes peers from room state. This gives a compact example of identity and lifetime constraints around duplex forwarding. [Tunnel connection handler](https://github.com/ssbc/go-ssb-room/blob/master/muxrpc/handlers/tunnel/server/connect.go).
- **C2:** Protocol handling, membership storage, and web/admin routes are separable subsystems. Database interfaces have generated mocks, while the testing guide distinguishes web, administrative, SQLite, and Go/JavaScript MuxRPC tests. These boundaries support studying both alternative clients and management behavior without collapsing everything into one transport handler. [Subsystem and interoperability testing guide](https://github.com/ssbc/go-ssb-room/blob/master/docs/testing.md).

## Coverage, search method, and limitations

Discovery used multiple live-web formulations, followed by reading official GitHub repositories and additional primary implementation or design sources. Representative query angles included:

- Matrix homeserver implementations in Rust and C++, followed by event-state, worker, and federation-ingress architecture.
- XMPP servers in Go, Lua, C, Java, and Erlang, including less prominent implementations such as Jackal, Metronome, and jabberd2.
- XMPP clustering, routing, backpressure, stream authentication, and extension interfaces.
- IRC server protocols, netbursts, timestamp reconciliation, and daemon-specific linking implementations.
- Lightweight federated messaging servers and alternative project communities beyond the most commonly recommended servers.
- Decentralized SimpleX and Scuttlebutt relay/rendezvous architectures.
- Official GitHub hosting, mirrors, successor projects, and historical Matrix implementations.
- Follow-up searches for compatibility histories, concurrency boundaries, resource limits, and protocol tests.

Later distinct queries largely rediscovered the same substantive server families, or produced client libraries, tutorials, comparison lists, and immature prototypes. The retained set spans nine principal implementation languages and includes independent implementation families as well as forks with substantial separate evolution. Shared ancestry is not evidence of independence by itself; the entries identify concrete implementation differences. Each canonical repository URL was opened or checked through the GitHub API, and each repository has an additional inspected primary source beyond its README. Source and documentation links are entry points into the specific subsystems discussed; branch-based links can change after this research date.

The GitHub constraint affects coverage. The [official Matrix catalog](https://github.com/matrix-org/matrix.org/blob/main/content/ecosystem/servers/servers.toml) points Conduit to GitLab and Continuwuity to its own forge; neither is included as an assumed GitHub mirror. Prosody and psyced were considered, but a substantive official GitHub source mirror was not established in this search. Conduwuit is represented through its stated successor Tuwunel rather than counted twice. The `ssb-server` launcher was not retained as another entry because the inspected top-level implementation primarily assembled other packages. Chat clients, bridges, deployment collections, generic publish/subscribe brokers, and projects whose federation was only an aspiration were outside the retained set.

Archived Jackal and jabberd2, obsolete Construct, and maintenance-mode Dendrite are explicitly marked. Palpo's own production-experience caveat is preserved. Other entries are not blanket endorsements of maintenance, security, or operational maturity. No candidate code was executed, dependencies installed, or independent benchmarks run. Criterion assessments are engineering judgments grounded in the linked material; quantitative performance claims and unverified guarantees are intentionally absent.
