# Cluster membership and gossip protocol libraries

Research date: **2026-10-09**.

This report selects 21 GitHub repositories implementing reusable cluster membership, failure detection, anti-entropy, or gossip dissemination. It includes SWIM libraries, partial-view overlays, and group communication systems where membership is integral to message delivery. Public-network pub/sub appears where the gossip implementation itself is substantial; cluster discovery adapters are included only when they expose a reusable framework worth studying. Full databases and orchestration products are outside the main scope.

The criteria identify useful engineering study material, not a certification of production readiness or uniform code quality. **C1** means difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** means substantial reusable abstractions. **C3** means concrete performance constraints addressed through understandable architecture. **C4** means sustained evolution accompanied by compatibility work, testing, or complexity management. Each entry justifies at least two criteria; an old repository alone does not earn C4.

## SWIM and embeddable failure detection

### 1. [hashicorp/memberlist](https://github.com/hashicorp/memberlist)

**Go — embeddable SWIM membership with Lifeguard extensions.** A useful baseline for studying how an unreliable failure detector becomes an application-facing membership service. It combines direct and indirect probes, suspicion, dissemination, and application delegates rather than treating a missed packet as conclusive failure.

- **C1:** The suspicion implementation distinguishes independent confirmations from repeated reports. It shortens a timer as corroboration arrives, accounts for time already elapsed, and coordinates confirmation counts with timer callbacks. These are concrete concurrency and false-positive concerns.
- **C2:** Membership, metadata, application broadcasts, and transport customization are exposed through reusable configuration and delegate interfaces. Applications can consume the failure detector without adopting a service-discovery agent.

Study entry point: [`suspicion.go`](https://raw.githubusercontent.com/hashicorp/memberlist/master/suspicion.go), especially confirmation deduplication, logarithmic timeout adjustment, and timer reset behavior. The repository README explains the surrounding protocol and embedding model.

### 2. [hashicorp/serf](https://github.com/hashicorp/serf)

**Go — membership-driven events and distributed queries, with a library and agent.** Serf builds on memberlist, but merits a separate entry for its application-level query, event, filtering, and lifecycle machinery. The relevant subsystem is `serf/`, rather than only its command-line executable.

- **C1:** Query handling must coordinate acknowledgments, response deduplication, deadlines, and channel closure. Its close lock and nonblocking delivery paths make races and slow consumers explicit; relay responses also respect message-size and peer-protocol constraints.
- **C2:** Tags, filtered queries, events, and response channels form reusable coordination facilities above membership discovery.
- **C4:** The dated changelog documents years of query-race fixes, protocol-version handling, Lifeguard integration, and snapshot changes that reduce blocking from disk operations. This is evidence of evolution tied to correctness and compatibility, rather than age alone.

Study entry points: [`serf/query.go`](https://raw.githubusercontent.com/hashicorp/serf/master/serf/query.go) and the [changelog](https://raw.githubusercontent.com/hashicorp/serf/master/CHANGELOG.md). The repository notes that the former standalone documentation site was shut down; use the checked-in documentation.

### 3. [clockworksoul/smudge](https://github.com/clockworksoul/smudge)

**Go — compact LAN-oriented SWIM membership and messaging.** This smaller implementation makes packet-budget and retransmission decisions unusually accessible. Its documented scope is private-network discovery, not arbitrary Internet deployment.

- **C1:** Broadcast identity includes origin information and an index. A locked broadcast map distinguishes messages still eligible for retransmission from retained duplicate-suppression records, then removes sufficiently old records.
- **C3:** It piggybacks bounded messages on protocol traffic and scales retransmission effort with membership size. The broadcast queue orders work by counters, exposing the tradeoff between dissemination, duplicate suppression, and retained state.

Study entry point: [`broadcast.go`](https://raw.githubusercontent.com/clockworksoul/smudge/main/broadcast.go). **Historical activity caveat:** the inspected [default-branch commit feed](https://github.com/clockworksoul/smudge/commits/main.atom) ends in May 2021; this is a study candidate, without a claim of current maintenance.

### 4. [uber-node/ringpop-node](https://github.com/uber-node/ringpop-node)

**JavaScript — SWIM membership combined with consistent hashing and request forwarding. Archived.** The repository was archived in September 2020 and explicitly says development is inactive. It remains a substantive reference for the interaction between membership and routing.

- **C1:** Incarnation numbers and membership checksums address stale state and divergence. The design explains why one-way full synchronization can fail to merge partitioned membership and why bidirectional synchronization is needed. Flap damping adds another failure-management layer.
- **C2:** A hash ring, membership service, and request-forwarding mechanism form a reusable sharding substrate. Studying them together shows what applications must do while nodes disagree about ownership.
- **C3:** The ring uses an ordered tree, while gossip and synchronization avoid making every application request perform full membership reconciliation.

Study entry point: the official [architecture and design documentation](https://ringpop.readthedocs.io/en/latest/architecture_design.html). This entry is explicitly historical, not an adoption recommendation.

### 5. [apple/swift-cluster-membership](https://github.com/apple/swift-cluster-membership)

**Swift — runtime-independent SWIM and Lifeguard protocol machinery.** Particularly useful for engineers designing a networking core that can run under different event loops and be tested without real sockets.

- **C1:** The handbook distinguishes a node's unique incarnation from its host and port, preventing a restarted process from being confused with its predecessor. It also warns that handlers must accumulate all required directives instead of returning early and silently omitting protocol actions.
- **C2:** `Instance` holds protocol state; a `Shell` supplies the execution environment; returned `Directive` values request effects. This separates membership decisions from timers, networking, and runtime integration.

Study entry point: [`HANDBOOK.md`](https://raw.githubusercontent.com/apple/swift-cluster-membership/main/HANDBOOK.md), which describes the state-machine boundary, identities, directives, and isolated test logging.

### 6. [scalecube/scalecube-cluster](https://github.com/scalecube/scalecube-cluster)

**Java — reactive cluster membership, failure detection, gossip, and metadata synchronization.** Its SWIM implementation adds synchronization for recovery after partitions. It is useful for studying protocol composition around asynchronous streams and an explicit scheduler.

- **C1:** Membership processing coordinates failure-detector events, gossip, incarnation changes, suspicion deadlines, and seed synchronization. Initial synchronization merges asynchronous attempts with error handling and a timeout; periodic synchronization provides a separate reconciliation path.
- **C2:** Transport, failure detection, gossip, metadata storage, and scheduling are injected components. The membership interface exposes asynchronous start, stop, lookup, and event-stream operations, allowing the cluster service to be embedded in larger reactive systems.

Study entry points: [`MembershipProtocolImpl.java`](https://raw.githubusercontent.com/scalecube/scalecube-cluster/master/cluster/src/main/java/io/scalecube/cluster/membership/MembershipProtocolImpl.java) and [`MembershipProtocol.java`](https://raw.githubusercontent.com/scalecube/scalecube-cluster/master/cluster/src/main/java/io/scalecube/cluster/membership/MembershipProtocol.java).

### 7. [caio/foca](https://github.com/caio/foca)

**Rust — small, transport-independent SWIM core. Official GitHub mirror.** The repository identifies itself as a mirror of the author's separately hosted repository; it retains substantive source and examples. Its `no_std` plus allocation model and explicit runtime contract make it relevant to constrained and unconventional runtimes.

- **C1:** The message protocol correlates direct and indirect probes, tracks suspicion, and handles peers learning that they have been considered dead. The runtime contract requires every scheduled timer event to be delivered: late delivery is permitted, silently losing an event is not.
- **C2:** The embedding application supplies identity, serialization, transport effects, and scheduling. Custom broadcast handling and state application let applications build synchronization behavior without forcing a particular socket stack.

Study entry points: the [`Message` protocol documentation](https://docs.rs/foca/latest/foca/enum.Message.html) and [`Runtime` contract](https://docs.rs/foca/latest/foca/trait.Runtime.html). Published API pages and the repository can represent different releases; check the selected package version before implementation work.

### 8. [al8n/memberlist](https://github.com/al8n/memberlist)

**Rust — substantial reimplementation of HashiCorp's memberlist approach.** This is related by protocol lineage to the Go project, but has an independently structured Rust implementation, including a protocol core separated from I/O and adapters for different execution environments.

- **C1:** Its Lifeguard suspicion state explicitly excludes the original reporter from independent confirmation counts, ignores duplicate reports, and recomputes deadlines with saturating duration arithmetic. The state returns an updated deadline for the caller to re-arm, making scheduling responsibility visible.
- **C2:** `memberlist-proto` exports endpoint, event, delegate, probing, and framing abstractions separately from runtime and transport integration. The repository documents multiple runtime backends and configurable identities and addresses, extending reuse beyond a single async networking stack.

Study entry points: [`memberlist-proto/src/lib.rs`](https://raw.githubusercontent.com/al8n/memberlist/main/memberlist-proto/src/lib.rs) and its [`suspicion` module](https://raw.githubusercontent.com/al8n/memberlist/main/memberlist-proto/src/suspicion/mod.rs). Protocol ancestry should not be mistaken for automatic wire compatibility with the Go implementation.

### 9. [icgood/swim-protocol](https://github.com/icgood/swim-protocol)

**Python — asyncio SWIM with replaceable transports.** A compact example of fitting membership into Python task and object lifecycles. The project documents defaults aimed at small clusters; those defaults are not evidence of large-scale validation.

- **C1:** Membership status transitions are constrained: a member cannot jump directly from online to offline without suspicion, and invalid reverse transitions are rejected. Task ownership holds strong references to subtasks and arranges cancellation and cleanup, addressing asyncio lifecycle hazards alongside protocol state.
- **C2:** The API separates members, the failure-detection worker, and transport implementations. Transport plugins implement probe and gossip operations while the worker owns dissemination and detection behavior.

Study entry point: the official [API reference](https://icgood.github.io/swim-protocol/swimprotocol.html), particularly `Status`, `TaskOwner`, `Worker`, and transport interfaces. The inspected [commit feed](https://github.com/icgood/swim-protocol/commits/main.atom) ends in October 2023 with Python-version support changes; present-day maintenance is not assumed.

## Anti-entropy and actor-cluster membership

### 10. [quickwit-oss/chitchat](https://github.com/quickwit-oss/chitchat)

**Rust — Scuttlebutt-style metadata anti-entropy with failure detection.** Chitchat disseminates per-node versioned key-value state and exposes live membership. Its most instructive feature is the interaction among packet limits, out-of-order deltas, deletion, and garbage collection.

- **C1:** A maximum observed version does not mean every intervening operation was received. The algorithm specifies invariants for version progress and garbage-collection progress, and explains when a stale peer needs reset state instead of an ordinary delta. Tombstones cannot simply disappear without accounting for lagging replicas.
- **C2:** Applications receive reusable node metadata and membership facilities rather than a fixed schema or service-discovery product.
- **C3:** Deltas fit within packet budgets and compact superseded changes. The design explicitly considers what can be truncated or omitted without violating convergence conditions.

Study entry point: [`ALGORITHM.md`](https://raw.githubusercontent.com/quickwit-oss/chitchat/main/ALGORITHM.md). The README explains failure detection and deletion retention. Finite retention and dead-node cleanup mean applications must understand the stated recovery assumptions rather than assume unlimited reliable history.

### 11. [apache/pekko](https://github.com/apache/pekko)

**Scala/Java — the `cluster` subsystem of a larger actor toolkit.** Counted once as a monorepo. Pekko originated from Akka 2.6 and has its own subsequent Apache development; this report selects Pekko rather than counting the two lineages as interchangeable additional entries.

- **C1:** Membership gossip uses vector clocks and a seen set to reconcile concurrent changes and determine convergence. Unreachable members affect convergence and lifecycle transitions; failure detection and the decision to remove a member are distinct. The leader's role depends on the converged membership state.
- **C3:** Dissemination biases toward members that have not seen an update, but adjusts that bias to avoid overwhelming lagging members. Converged peers exchange compact status information, and stale queued gossip can be discarded rather than consuming resources indefinitely.

Study entry point: the official [cluster concepts and implementation discussion](https://pekko.apache.org/docs/pekko/current/typed/cluster-concepts.html), covering gossip, convergence, leader actions, failure detection, and performance choices. This entry concerns cluster membership mechanics, not an assessment of every actor-toolkit component.

## Partial-view overlays and gossip dissemination

### 12. [lasp-lang/partisan](https://github.com/lasp-lang/partisan)

**Erlang — alternative distribution layer with selectable membership overlays.** Relevant implementations include full mesh and HyParView, along with named communication channels. It offers a substantial comparison with standard BEAM distribution assumptions.

- **C1:** The HyParView manager maintains active-view symmetry and passive backups, handles stale messages using epochs and disconnect counters, and repairs topology through joins, promotions, and shuffles. Its X-BOT discussion explains coordinated swaps that must preserve view-size and connectivity properties.
- **C2:** Peer-service managers implement a common interface, allowing applications to select different overlay structures and communication behavior.
- **C3:** Partial views limit maintained connectivity. Named parallel channels separate traffic classes, while optional monotonic channels expose an explicit load-shedding tradeoff.

Study entry point: [`partisan_hyparview_peer_service_manager.erl`](https://raw.githubusercontent.com/lasp-lang/partisan/develop/src/partisan_hyparview_peer_service_manager.erl), which includes extensive algorithm commentary and implementation. Backend capabilities differ: do not assume every monitoring or leave operation is implemented uniformly across overlays.

### 13. [dcos/lashup](https://github.com/dcos/lashup)

**Erlang — historical DC/OS control-plane substrate combining HyParView, failure detection, multicast, and a replicated store.** Useful for understanding how a sparse membership graph supports services above it rather than functioning as an isolated algorithm.

- **C1:** Membership tracks active and passive peers, monitors, failure events, and asynchronous responses. Repair and shuffle paths must preserve useful connectivity despite failed neighbors and racing topology changes.
- **C2:** The project composes membership, reachability information, dissemination, and CRDT-backed state into a reusable control-plane layer.
- **C3:** A sparse connection graph limits connection overhead, while randomized retries and a join window curb repeated join work and churn when the active view is full. The README also acknowledges limitations of its key-value anti-entropy approach.

Study entry point: [`lashup_hyparview_membership.erl`](https://raw.githubusercontent.com/dcos/lashup/master/src/lashup_hyparview_membership.erl). **Historical activity caveat:** the inspected [default-branch feed](https://github.com/dcos/lashup/commits/master.atom) ends in October 2019.

### 14. [n0-computer/iroh-gossip](https://github.com/n0-computer/iroh-gossip)

**Rust — topic-scoped gossip using HyParView and PlumTree.** Its protocol implementation makes a clean study of how neighbor selection and broadcast repair interact, with I/O separated from protocol state.

- **C1:** Active and passive views repair failed connectivity. PlumTree's eager and lazy paths must recognize duplicates, request missing payloads, and promote useful peers. Included simulation tests exercise symmetric connections, merging separated groups, broadcasts, and departures.
- **C2:** The core maintains independent swarms per topic and accepts generic peer identities and peer data, making the algorithm reusable apart from one application payload.
- **C3:** Eager peers forward full payloads while lazy peers advertise message identifiers. Timed requests repair loss without flooding every link with every payload; the documentation also explains how changing senders affects redundant traffic.

Study entry point: [`src/proto.rs`](https://raw.githubusercontent.com/n0-computer/iroh-gossip/main/src/proto.rs), including its architectural overview and simulation tests.

### 15. [libp2p/go-libp2p-pubsub](https://github.com/libp2p/go-libp2p-pubsub)

**Go — GossipSub and other pub/sub routers for public peer-to-peer overlays.** This belongs on the gossip side of the category: it is not a replacement for a cluster-wide failure detector. It broadens the selection to adversarial rather than solely cooperative peers.

- **C1:** Peer scoring validates threshold relationships and invalid numerical values. Penalties cover invalid deliveries, premature re-grafting, and unfulfilled gossip promises; score decay and retention complicate behavior across disconnections. These are concrete adversarial and numerical correctness concerns.
- **C2:** Pub/sub infrastructure separates routing choices from subscriptions, message validation, signing, and tracing. Applications can use the same surrounding facilities with different dissemination strategies.

Study entry point: [`score_params.go`](https://raw.githubusercontent.com/libp2p/go-libp2p-pubsub/master/score_params.go). Read its parameter relationships and delivery windows as part of the protocol, not merely as tuning constants; poor configuration can alter peer acceptance and propagation behavior.

### 16. [dotnet/dotNext](https://github.com/dotnet/dotNext)

**C# — `DotNext.Net.Cluster.Discovery.HyParView` within the DotNext monorepo.** Counted once, with scope limited to partial-view membership, rumor dissemination, and the ASP.NET Core integration. The broader utility collection is not the reason for inclusion.

- **C2:** A transport-independent `PeerController` handles neighborhood maintenance while `IRumorSender` supplies delivery. Lifecycle hooks, peer discovery/removal events, and an HTTP binding allow applications to integrate membership without adopting a single networking implementation.
- **C3:** Active and passive views have configurable capacities; shuffle walks and queue capacity make connectivity and internal work limits explicit. This exposes the resource consequences of topology maintenance through a relatively small API.

Study entry point: the official [HyParView and gossip guide](https://dotnet.github.io/dotNext/features/cluster/gossip.html), including controller lifecycle, startup-event handling, failure removal, configuration, and the ASP.NET Core binding.

## Coordinated views and membership-aware group communication

### 17. [lalithsuresh/rapid](https://github.com/lalithsuresh/rapid)

**Java — research implementation of strongly consistent group membership.** RAPID contrasts with ordinary eventually consistent SWIM: it aggregates distributed observations, identifies a membership change, and agrees on a new configuration. It is a research reference with explicit communication and failure-model assumptions.

- **C1:** Multiple observers and a group-cut mechanism address asymmetric reachability and correlated reports before a consensus step installs a view. The paper carefully separates alert dissemination from agreement; gossip alone does not establish a globally consistent membership decision.
- **C2:** Failure detectors and messaging clients/servers have replacement interfaces, allowing the membership mechanism to be embedded with different probes and transports.
- **C3:** Deterministic monitoring overlays bound observation relationships, and a common-case consensus path reduces coordination work when participants agree on the proposed change.

Study entry point: the authors' [USENIX ATC 2018 paper](https://www.usenix.org/system/files/conference/atc18/atc18-suresh.pdf), including the algorithm, assumptions, and implementation API. The inspected [repository feed](https://github.com/lalithsuresh/rapid/commits/master.atom) shows a June 2023 dependency update after a 2021 release-preparation commit; this does not establish active protocol development today.

### 18. [belaban/JGroups](https://github.com/belaban/JGroups)

**Java — configurable group communication with membership, reliable delivery, and state transfer.** Particularly valuable when studying how membership changes interact with data delivery, rather than considering failure detection in isolation.

- **C1:** The group membership service has client, coordinator, and participant roles, separate temporary membership state, view identifiers, acknowledgment collection, and merge handling. Ordering a view installation relative to its digest and state transfer is explicitly treated as a race-sensitive operation.
- **C2:** A configurable protocol stack separates discovery, transport, failure detection, suspicion verification, membership, stability, fragmentation, and flow control. Applications can select a coherent communication stack through a channel abstraction.
- **C3:** Delta views avoid repeatedly transmitting unchanged membership, while the implementation takes care to preserve ordering when view transmission can block.

Study entry point: [`protocols/pbcast/GMS.java`](https://raw.githubusercontent.com/belaban/JGroups/master/src/org/jgroups/protocols/pbcast/GMS.java), especially view installation, acknowledgment handling, and membership-change batching.

### 19. [corosync/corosync](https://github.com/corosync/corosync)

**C — cluster engine with reusable closed-process-group APIs and Totem membership.** This is the coordinated group-communication boundary of the category, not a SWIM implementation. The selected subsystem couples membership recovery to ordered multicast delivery.

- **C1:** Totem tracks operational, gather, commit, and recovery states, with distinct current, transitional, failed, and deliverable memberships. Ring identifiers, retransmission queues, and regular/recovery sort queues encode the difficult relationship between a changing membership and which messages may be delivered.
- **C2:** The CPG API exposes group membership changes and message-delivery callbacks to applications. Its interface explicitly distinguishes implemented delivery guarantees from enum values that are not implemented.
- **C3:** Idle-token handling reduces unnecessary work; flow-control state and retransmission machinery make resource pressure part of the protocol implementation.

Study entry points: [`exec/totemsrp.c`](https://raw.githubusercontent.com/corosync/corosync/main/exec/totemsrp.c) and [`include/corosync/cpg.h`](https://raw.githubusercontent.com/corosync/corosync/main/include/corosync/cpg.h).

### 20. [zeromq/zyre](https://github.com/zeromq/zyre)

**C — local-area peer discovery, membership events, and group messaging over ZeroMQ.** Zyre uses discovery beacons and peer connections, with an alternative gossip discovery mechanism. It is useful as a contrasting LAN-oriented design rather than another SWIM variant.

- **C1:** Peer state tracks message sequence numbers and distinguishes an initial handshake from subsequent traffic. Evasive and expired deadlines, reconnect behavior, and sequence gaps connect liveness decisions to the messaging protocol.
- **C2:** Node and group operations expose discovery, joining, leaving, and received-message events as an application-facing library.
- **C3:** Peer socket limits and send failure handling make backpressure concrete. On a blocked send path the implementation can disconnect and drop queued work; reliable transport should not be interpreted as unlimited application-level delivery guarantees.

Study entry point: [`src/zyre_peer.c`](https://raw.githubusercontent.com/zeromq/zyre/master/src/zyre_peer.c), especially sequence checking, expiry refresh, connection setup, and send-failure cleanup.

## Pluggable cluster formation

### 21. [bitwalker/libcluster](https://github.com/bitwalker/libcluster)

**Elixir — supervision-based cluster formation with a UDP gossip discovery strategy.** Its main contribution is a reusable strategy framework, not a full SWIM failure detector. Discovery connects nodes through the configured distribution mechanism; those layers retain responsibility for their own connection and liveness semantics.

- **C2:** Multiple named topologies, replaceable discovery strategies, and configurable connect/disconnect/list-nodes callbacks support different deployment environments and distribution backends. The gossip strategy is one concrete implementation within that framework.
- **C4:** The [package release history](https://hex.pm/api/packages/libcluster) spans releases from 2016 through 2025. The changelog records configuration migration, multicast-interface fixes, OTP-related compatibility, cipher API updates, logging changes, and reconnect fixes—specific evidence of maintaining a reusable abstraction over time.

Study entry points: [`lib/strategy/gossip.ex`](https://raw.githubusercontent.com/bitwalker/libcluster/main/lib/strategy/gossip.ex), for heartbeat jitter and UDP socket lifecycle, and the [changelog](https://raw.githubusercontent.com/bitwalker/libcluster/main/CHANGELOG.md). The simple discovery strategy should not be credited with guarantees supplied only by a more elaborate membership protocol.

## Coverage, exclusions, and limits

Discovery used separate live web searches for Go SWIM/memberlist implementations; Rust SWIM and Scuttlebutt anti-entropy; Java strongly consistent membership and reactive clustering; Erlang/Elixir HyParView and distribution; JavaScript and Python implementations; C/C++ group communication; public-network GossipSub and PlumTree; and .NET partial-view libraries. Additional Haskell/OCaml and smaller C/C++ searches did not yield another candidate with enough verified substance to improve this selection. Later distinct queries increasingly returned the same projects, demonstrations, or application products.

Every retained canonical GitHub repository was opened, and at least one separate primary implementation or architecture/API source was read. Links above point to those inspected materials. GitHub source, official project documentation, package history, and the RAPID authors' paper supplied the evidence; search snippets and star counts were not used as substitutes. Some raw-source requests failed through the web renderer and were subsequently read directly from GitHub's public raw endpoint. No candidate code was installed or executed, and this is not a comparative benchmark or a security audit.

The selection deliberately excludes tutorials, course simulators, generated bindings, gists, link collections, and whole database products whose membership code is incidental to the requested library scope. [hashicorp/hyparview](https://github.com/hashicorp/hyparview) was inspected but omitted: its README lists unresolved asymmetric-link, recovery, and failure-integration work. The more substantial HyParView implementations above provide stronger study targets. Social-feed protocols sharing the Scuttlebutt name were not treated as interchangeable with versioned cluster-state anti-entropy.

Ringpop is explicitly archived; Foca is explicitly an official mirror. Smudge, Lashup, swim-protocol, and RAPID have activity caveats grounded in the inspected default-branch feeds. Absence of such a caveat is not a claim that maintainers currently provide support. Branch links and `latest` documentation can change or refer to different release snapshots. Claims about invariants and tradeoffs are grounded in the inspected source and documentation; judgments about what is most instructive are editorial inferences. Partial-view overlays, eventually consistent failure detectors, and agreed membership views solve different problems and should be compared with those differences intact.
