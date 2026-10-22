# Peer-to-peer overlays and distributed hash tables

Research date: **2026-10-09**.

This selection covers 24 repositories implementing distributed lookup, overlay membership, gossip dissemination, peer discovery, or routing over a peer-to-peer topology. It includes embeddable libraries and the relevant networking subsystems of larger systems. Kademlia, BitTorrent Mainline, Chord, HyParView, gossip meshes, and alternative encrypted routing designs are represented. Inclusion is a judgment about engineering study value, not a security endorsement or a claim that every component is exemplary.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions supporting multiple applications. **C3** — real resource or performance constraints addressed through an understandable architecture. **C4** — sustained evolution supported by compatibility, testing, or complexity-management evidence. Each entry justifies at least two criteria; omitted criteria are not negative findings. Repository headings link to verified GitHub roots, and the linked implementation and documentation sources are suggested reading entry points.

## General-purpose DHT implementations

### 1. [libp2p/go-libp2p-kad-dht](https://github.com/libp2p/go-libp2p-kad-dht)

**Go — libp2p Kademlia routing and provider discovery.** Study how a deployed DHT hardens the protocol's routing-table and peer-record rules without changing wire compatibility. This is a focused routing implementation rather than the entire libp2p stack.

- **C1:** Advertising DHT server support is insufficient for admission: the implementation's design notes describe a `FIND_NODE` probe before accepting a peer into the routing table. This makes reachability an explicit correctness concern.
- **C3:** Peer records are limited to 8 KiB, with addresses trimmed on both receipt and transmission. The documented approach bounds peerstore and message costs while retaining interoperability, an instructive example of resource limits layered onto a shared protocol.

Start with the short but substantive [implementation optimizations document](https://raw.githubusercontent.com/libp2p/go-libp2p-kad-dht/master/optimizations.md), then use the repository's lookup, routing-table refresh, and provider components to follow those policies into implementation.

### 2. [libp2p/rust-libp2p](https://github.com/libp2p/rust-libp2p)

**Rust — modular networking stack; scope: `protocols/kad` and its swarm integration.** The monorepo counts once. Its useful study angle is a DHT expressed as a composable network behaviour with an application-controlled record store.

- **C1:** The Kademlia behaviour coordinates pending bucket replacements, query termination, record expiration, republication, and replication. Incoming records can be surfaced for application validation rather than automatically written; request and whole-query timeouts are distinct. These are concrete boundaries between routing liveness and data acceptance. See [the behaviour implementation](https://raw.githubusercontent.com/libp2p/rust-libp2p/master/protocols/kad/src/behaviour.rs).
- **C2:** `Behaviour<TStore>` separates record storage from network behaviour and query orchestration. This supports different persistence and validation policies within the same swarm framework, rather than coupling the DHT to one application. The [Kademlia changelog](https://raw.githubusercontent.com/libp2p/rust-libp2p/master/protocols/kad/CHANGELOG.md) is a useful companion: it records API migrations, provider-record attack fixes, and runtime/browser timer corrections.

### 3. [savoirfairelinux/opendht](https://github.com/savoirfairelinux/opendht)

**C++ — distributed value storage with listeners, cryptographic operations, and language bindings.** Study the boundary between an asynchronous DHT engine and an API usable by ordinary application threads. The repository acknowledges ancestry in `jech/dht`; the C++ value model, listeners, cryptographic API, threading layer, and bindings provide substantial separate evolution.

- **C1:** `DhtRunner` supports an internal event-loop thread or caller-driven execution. Its interface exposes cancellation, asynchronous callbacks, shutdown, and connectivity changes that require reconnecting and registering listeners again. These lifecycle operations make concurrency and churn central concerns.
- **C2:** Filtered retrieval, publication, subscriptions, and signed/encrypted puts share one runner abstraction. Applications can choose callbacks or futures without implementing the lower-level overlay loop themselves.

The [runner header and its API comments](https://raw.githubusercontent.com/savoirfairelinux/opendht/master/include/opendht/dhtrunner.h) are the strongest entry point; the repository overview explains the wider binding and proxy ecosystem.

### 4. [tomp2p/TomP2P](https://github.com/tomp2p/TomP2P)

**Java — asynchronous DHT, replication, and peer-storage toolkit. Archived on 2025-04-22; retained as a historical engineering reference.** Its interesting distinctions are explicit responsibility transfer and the separation of data protection from transport-message authentication.

- **C1:** The documentation distinguishes owner-driven republication and TTL from indirect replication, where responsibility moves as peers join or leave and periodic repair fills gaps. It also explains why replicated data needs its own signature: a forwarding peer is not necessarily the original author.
- **C2:** Futures, replaceable storage, and custom routed commands make the library useful beyond a single key-value application. The extension points expose storage and communication policies without requiring a new routing implementation.

Read the [advanced documentation](https://tomp2p.net/doc/advanced/) for replication, protection domains, custom storage, and routing controls. Its configurable parallelism and failure thresholds also provide a concrete performance-tuning study, but the archive status should govern adoption decisions.

### 5. [bmuller/kademlia](https://github.com/bmuller/kademlia)

**Python — asyncio Kademlia library over UDP.** A comparatively compact implementation for reading iterative lookup end to end, with enough failure handling to be more useful than a classroom sketch.

- **C1:** The crawl tracks contacted nodes, removes failed respondents, changes strategy when the closest set stops improving, and terminates once the remaining candidates have been contacted. Value lookup handles conflicting replies and may cache the selected result at a close node that lacked it; that selection policy should not be mistaken for consensus.
- **C3:** The shared crawl machinery issues parallel requests under the `alpha` parameter, making the latency-versus-traffic tradeoff visible in a small amount of asynchronous code.

Read [the node and value crawl implementations](https://raw.githubusercontent.com/bmuller/kademlia/master/kademlia/crawling.py). A material limitation in the repository README is that original-publisher periodic republication is not automatic; applications must arrange it.

## BitTorrent lookup, signed records, and connection establishment

### 6. [arvidn/libtorrent](https://github.com/arvidn/libtorrent)

**C++ — BitTorrent library; scope: its Kademlia DHT and BEP 44 storage subsystem.** Study the interaction between wire encodings, mutable records, storage policy, and an existing high-throughput networking engine. The whole torrent engine is not being evaluated here.

- **C1:** Mutable items combine signatures, increasing sequence numbers, and optional compare-and-swap. Exact bencoded bytes matter for hashes and signatures; re-encoding a logically equivalent value can invalidate authentication. The [DHT storage guide](https://libtorrent.org/dht_store.html) explains these rules and provides test vectors.
- **C2:** `dht_storage_interface` allows replacement of the default peer, mutable-item, and immutable-item stores. The documented boundary places message authentication above storage while exposing sequence handling, capacity, and periodic cleanup below it. See the [DHT API reference](https://libtorrent.org/reference-DHT.html).

These two guides are particularly useful for engineers designing extensible storage without accidentally changing protocol semantics.

### 7. [anacrolix/dht](https://github.com/anacrolix/dht)

**Go — embeddable Mainline DHT with peer discovery and BEP 44 data operations.** Study a UDP server that separates transactions, traversal, tokens, and record storage while remaining usable outside a torrent client.

- **C1:** Server state includes a synchronized routing table, a transaction dispatcher, a one-time closure signal, and rotating query-token state. Initialization and shutdown must coordinate with packet handling and outstanding requests; the server code makes these ownership boundaries visible.
- **C2:** A supplied `net.PacketConn`, configurable BEP 44 storage, and separate traversal and transaction packages let applications adapt networking and persistence. This is more than an application-specific discovery helper.
- **C3:** Outgoing requests pass through a configurable rate limiter, putting resource policy alongside the transaction machinery.

Start with [the server implementation](https://raw.githubusercontent.com/anacrolix/dht/master/server.go). Security-related node-ID configuration is conditional; the inspected default configuration should not be read as a promise of universal identity hardening.

### 8. [webtorrent/bittorrent-dht](https://github.com/webtorrent/bittorrent-dht)

**JavaScript — Node.js UDP Mainline DHT library.** Despite the organization name, this repository's DHT is not a browser WebRTC overlay. It is useful for studying substantial protocol machinery behind an event-and-callback API.

- **C1:** Mutable retrieval verifies signatures and the requested key binding, while immutable retrieval checks the content hash. Routing-table replacement also has asynchronous hazards: ping handling deliberately serializes checks to avoid recursively accumulating ping work.
- **C3:** LRU value/table caches, bounded peer storage, serialized ping operations, and rebootstrap after isolation expose how a long-running JavaScript DHT manages memory and background traffic.

The [client implementation](https://raw.githubusercontent.com/webtorrent/bittorrent-dht/master/client.js) brings together lookup, announcement, mutable/immutable storage, secret rotation, and routing maintenance. It makes a useful comparison with the Go, C, and Rust Mainline implementations in this section because the same wire ecosystem produces different state-management choices.

### 9. [jech/dht](https://github.com/jech/dht)

**C — compact, embeddable BitTorrent DHT.** Study how a caller-driven event loop can support an operational DHT without an application framework or a large object hierarchy.

- **C1:** Search state retains additional candidate nodes so it can backtrack when the closest peers fail. Per-node request, reply, and acknowledgement state distinguishes discovery progress from a completed exchange.
- **C3:** The implementation explicitly caps peers, hashes, searches, and in-flight search requests. Separate bucket and search structures make the relationship between retained routing knowledge and temporary lookup work understandable.

Start with [the implementation](https://raw.githubusercontent.com/jech/dht/master/dht.c), then the repository README's `dht_periodic`, callback, search, and persistence integration instructions. This is a strong small-codebase complement to OpenDHT, whose shared ancestry is noted separately rather than hidden as an unrelated implementation.

### 10. [pubky/mainline](https://github.com/pubky/mainline)

**Rust — Mainline client/server library emphasizing arbitrary DHT records.** Its study value includes client/server role policy and an explicit signed-record API, rather than only torrent peer lookup.

- **C1:** `MutableItem` ties the target to a public key and optional salt and carries a signed value with an `i64` sequence. Its signing constructor and explicitly unchecked constructor expose a meaningful trust boundary for callers. See the [mutable-item API](https://docs.rs/mainline/latest/mainline/struct.MutableItem.html).
- **C2:** Synchronous and asynchronous APIs, configurable client/server operation, request filtering, and a local test-network builder support both applications and protocol experiments. The [crate documentation](https://docs.rs/mainline/latest/mainline/) explains these abstractions and the adaptive promotion of reachable clients to servers.

The project explicitly documents that its server has **no built-in rate limiting**. A custom request filter runs after parsing and does not govern incoming responses; this limitation matters when studying deployment policy.

### 11. [holepunchto/hyperdht](https://github.com/holepunchto/hyperdht)

**JavaScript — DHT-backed encrypted stream establishment and discovery.** Study the transition from locating a public key to creating a usable connection through NAT and relay paths. Although it builds on `dht-rpc`, the connection orchestration is substantive implementation work, not a generated wrapper.

- **C1:** The connection state machine owns queries, punchers, sessions, and streams and must destroy them coherently. It handles direct/relay transitions and races between local-network shortcuts and NAT traversal; failure of one candidate path must not prematurely kill another viable path.
- **C2:** Key-addressed listening and connecting, encrypted streams, topic discovery, and mutable/immutable values provide reusable application primitives above raw DHT RPCs.

Start with [connection orchestration](https://raw.githubusercontent.com/holepunchto/hyperdht/main/lib/connect.js), then the repository's server/client API documentation. The code is especially instructive for cancellation and resource ownership when several connectivity strategies run concurrently.

## Gossip, membership, and application overlay frameworks

### 12. [libp2p/go-libp2p-pubsub](https://github.com/libp2p/go-libp2p-pubsub)

**Go — publish/subscribe overlay routers, especially Gossipsub.** This is an overlay inclusion, not a DHT claim. Study the maintenance of a bounded dissemination mesh under churn and hostile participation.

- **C1:** Mesh lower/upper bounds, outbound-peer quotas, score-aware pruning, and graft/prune backoff interact to preserve connectivity and resist unhelpful topology changes. The implementation documents relationships between gossip history and cache lifetime rather than treating them as independent knobs.
- **C3:** Retransmission limits, gossip-history windows, and `IHAVE` budgets bound redundant and adversarial traffic. Those controls are organized in the router rather than left entirely to each subscribing application.

The [Gossipsub router implementation](https://raw.githubusercontent.com/libp2p/go-libp2p-pubsub/master/gossipsub.go) is the main entry point. The repository overview explains how shared topic, validation, and tracing APIs accommodate Floodsub, Randomsub, and Gossipsub, giving useful context for the router's extension boundaries.

### 13. [lasp-lang/partisan](https://github.com/lasp-lang/partisan)

**Erlang — distributed actor communication with configurable overlay membership.** Study a concrete HyParView implementation inside a general BEAM networking framework, including the consequences of imperfect failure detection.

- **C1:** The HyParView manager maintains a small symmetric active view and a larger passive backup view. Join forwarding, shuffling, failure-driven promotion, and restart epochs must agree; stale control messages and false failure suspicions are explicit concerns. Its comments also acknowledge that probabilistic repair does not guarantee freedom from partitions.
- **C2:** Membership is a peer-service-manager implementation within a framework supporting different topologies and communication channels. Applications can change membership policy without rebuilding their message-passing layer.

Read [the HyParView manager and its extensive design comments](https://raw.githubusercontent.com/lasp-lang/partisan/develop/src/partisan_hyparview_peer_service_manager.erl). The code also describes X-BOT optimization and coordinated neighbor swaps, a useful follow-on for understanding how topology quality can be improved without casually breaking membership invariants.

### 14. [nknorg/nnet](https://github.com/nknorg/nnet)

**Go — Chord-based messaging overlay with transport, router, and middleware abstractions.** This is the networking library, not an evaluation of the NKN blockchain. It broadens the selection beyond XOR-distance designs.

- **C1:** The Chord implementation coordinates join retries, successor/predecessor/finger updates, disconnection cleanup, and one-time readiness. Incoming connections are rejected until the overlay is ready, making startup ordering part of the protocol rather than a caller convention. See [the Chord overlay implementation](https://raw.githubusercontent.com/nknorg/nnet/master/overlay/chord/chord.go).
- **C2:** Transport interfaces, routing modes, and event middleware support direct delivery, relaying, and broadcast strategies. The repository documents these as separable layers, useful for studying how an overlay can serve a general messaging API.

The README still lists tests as forthcoming work. This report does not infer comprehensive test coverage or production readiness from the architecture or its performance-oriented descriptions.

### 15. [RingsNetwork/rings](https://github.com/RingsNetwork/rings)

**Rust — Chord overlay with native and browser/WebAssembly operation.** Study DID-addressed routing and the division between protocol transitions and runtime effects in a WebRTC-capable system.

- **C1:** The security design binds signatures to a network identifier and message family. It also describes an atomic admission/eviction boundary: a connection must not be retired between checking its topology references and updating the connection pool. These are precise replay and concurrency concerns, not merely claims of encrypted transport.
- **C2:** The repository separates the core communication layer from node-level applications and privacy mechanisms. Its protocol/interpreter split is a reusable way to keep routing logic distinct from runtime-dependent networking effects.

Read the repository's architecture overview and [security/layer-contract document](https://raw.githubusercontent.com/RingsNetwork/rings/master/SECURITY.md). That document explicitly excludes permissionless Sybil/eclipsing resistance and distinguishes ordinary routing from optional privacy features; those limitations are part of the study value.

### 16. [Tribler/py-ipv8](https://github.com/Tribler/py-ipv8)

**Python — asyncio overlay framework with authenticated communities and DHT discovery.** Study how an extensible application-overlay model is paired with a controllable simulated network for testing.

- **C1:** The test framework supports request-cache timeouts, asynchronous message delivery, teardown, and deadlock detection. These facilities make missing replies and lifecycle errors observable instead of depending only on live-network tests. See the [TestBase tutorial](https://py-ipv8.readthedocs.io/en/latest/basics/testbase_tutorial.html).
- **C2:** `DHTCommunity` provides key-value operations, while `DHTDiscoveryCommunity` extends it to connect to identities by public-key hash. The distinction allows storage and peer rendezvous to be composed with other communities. The [DHT guide](https://py-ipv8.readthedocs.io/en/latest/further-reading/dht.html) documents signed versus unsigned values, multiple returned values, and retry requirements when peers are offline.

Together these entry points show both the application abstraction and how distributed behaviour can be exercised deterministically enough to debug.

## Encrypted routing and peer-discovery subsystems

### 17. [cjdelisle/cjdns](https://github.com/cjdelisle/cjdns)

**C with Rust components — encrypted IPv6 overlay with distributed route discovery.** Study the separation of switching, routing, and cryptographic sessions, especially how discovered paths become compact forwarding labels.

- **C1:** Routing-label encodings must preserve a representable reverse path. The design also places progress and loop-avoidance constraints on returned routes and distinguishes what the requester can verify from what depends on peer cooperation.
- **C3:** The architecture separates route discovery from packet switching, letting established paths use label-based forwarding instead of repeating distributed lookup for each packet. This is an architectural performance argument, not a benchmark claim.

The [design whitepaper in the source tree](https://github.com/cjdelisle/cjdns/blob/master/doc/Whitepaper.md) is the best entry point: read the switch, router, and CryptoAuth sections together. The useful lesson is how forwarding representation constrains the control plane, rather than encryption considered in isolation.

### 18. [yggdrasil-network/yggdrasil-go](https://github.com/yggdrasil-network/yggdrasil-go)

**Go — experimental IPv6 overlay; the project describes its public network as a testbed.** Study routing that combines spanning-tree coordinates, keyspace reachability information, and opportunistic path shortcuts.

- **C1:** The [implementation design](https://yggdrasil-network.github.io/implementation.html) explains fallback from broken shortcut paths to keyspace routing and the role of propagated Bloom filters. Peering discovery and overlay routing are separate mechanisms.
- **C3:** The [changelog](https://raw.githubusercontent.com/yggdrasil-network/yggdrasil-go/develop/CHANGELOG.md) records RTT-aware route costs, reduced parsing allocations, and bounded packet queues. These changes connect topology decisions with CPU, latency, and memory constraints.
- **C4:** The 2024–2026 history includes explicit v0.5 protocol compatibility, restored TLS compatibility, tree-stability changes, endian fixes, and malformed-packet corrections. This is evidence of evolution with compatibility and failure management, beyond repository age.

Use the changelog for current cost-selection behaviour: the higher-level design page does not fully reflect subsequent routing changes.

### 19. [PurpleI2P/i2pd](https://github.com/PurpleI2P/i2pd)

**C++ — independent I2P router implementation; scope: network-database discovery and maintenance.** Study a DHT-like floodfill directory inside an anonymity network, where bootstrapping, router reachability, and record freshness interact.

- **C1:** NetDb handles reseeding when usable router information is insufficient, timestamp and record checks, malformed lookup lengths, and maintenance changes when transports are offline. Its locking and record-update rules make concurrent receipt and expiration meaningful correctness problems.
- **C3:** A dedicated message-processing loop drains queued work, while profile persistence is scheduled asynchronously and guarded against overlapping saves. This separates routine message handling from expensive maintenance.

Read [the NetDb implementation](https://raw.githubusercontent.com/PurpleI2P/i2pd/openssl/libi2pd/NetDb.cpp), with the official [I2P network-database architecture](https://i2p.net/en/docs/overview/network-database/) for RouterInfo, LeaseSet, and floodfill context. Inclusion is specific to this subsystem; it is not a review of the router's anonymity guarantees.

### 20. [i2p/i2p.i2p](https://github.com/i2p/i2p.i2p)

**Java — I2P reference implementation; scope: Kademlia/floodfill network database. Official read-only GitHub mirror.** The [developer guide](https://i2p.net/en/docs/development/new-developers/) identifies GitLab as the development host and GitHub as a mirror. This remains a substantive source mirror and is distinct from i2pd's implementation.

- **C1:** Database startup, expiration, reseeding, negative results, and client-specific state have different lifetimes. The facade explicitly avoids discarding needed persisted peers immediately at startup and coordinates search completion with synchronized active-search bookkeeping.
- **C3:** An active-search map coalesces duplicate lookups, negative caching avoids repeatedly pursuing failed keys, and exploration work has a queue bound. These controls connect directory semantics to resource management under failures.

Start with [KademliaNetworkDatabaseFacade](https://raw.githubusercontent.com/i2p/i2p.i2p/master/router/java/src/net/i2p/router/networkdb/kademlia/KademliaNetworkDatabaseFacade.java). Its datastore, peer-selection, exploration, and floodfill extension boundaries make this a useful comparison with the C++ NetDb architecture without counting the same repository twice.

### 21. [TokTok/c-toxcore](https://github.com/TokTok/c-toxcore)

**C — reusable peer-to-peer communications core; scope: its DHT and connectivity layer.** Study identity-based discovery combined with NAT traversal, while recognizing the repository's experimental status and stated security-review limitations.

- **C1:** DHT packet processing must validate lengths and addressed identities before accepting encrypted requests. Close-node and friend-specific lists, ping state, expiring shared-key caches, and hole-punch timing create overlapping state lifecycles. See [the DHT implementation](https://raw.githubusercontent.com/TokTok/c-toxcore/master/toxcore/DHT.c).
- **C2:** The core is exposed as a client library with callbacks and an application-driven iteration interface. Internal networking, clock, randomness, and memory dependencies are passed into the DHT machinery, allowing its protocol logic to sit inside multiple clients rather than one UI application.

The repository's API overview provides the application-facing entry point. Cryptographic mechanisms are grounds for studying difficult correctness, not evidence here of audited security.

### 22. [ethereum/go-ethereum](https://github.com/ethereum/go-ethereum)

**Go — monorepo; scope: `p2p/discover`, particularly discovery v5.** Counted once for its substantive discovery subsystem, without evaluating blockchain execution or consensus. Study authenticated UDP discovery as a reusable component with its own concurrency model.

- **C1:** The v5 transport centralizes packet dispatch and tracks active calls, authentication challenges, per-node queues, timeouts, and completion channels. Shutdown coordinates cancellation and goroutines; resolving a node also has to respect record sequence freshness.
- **C2:** `ListenV5`, an abstract UDP connection, and registered TALK protocol handlers expose discovery and application-specific request/response messaging independently of Ethereum execution logic.

Read [the v5 UDP transport](https://raw.githubusercontent.com/ethereum/go-ethereum/master/p2p/discover/v5_udp.go). Its dispatch-loop ownership is a useful contrast with mutex-centered servers and callback-heavy JavaScript implementations elsewhere in this report.

## Content-oriented and small-world overlays

### 23. [hyphanet/fred](https://github.com/hyphanet/fred)

**Java — the original Freenet lineage, now Hyphanet; distributed encrypted storage over an adaptive overlay.** This is separate from the modern Rust Freenet below. Study request forwarding where anonymity-related caching policy, route failures, and congestion cannot be treated independently.

- **C1:** `RequestSender` documents registration/unregistration obligations, terminal-state ordering, two-stage timeout handling, and rerouting after disconnection. Its hop-budget logic limits repeated failures while considering where data may be cached. See [request routing and transfer coordination](https://raw.githubusercontent.com/hyphanet/fred/next/src/freenet/node/RequestSender.java).
- **C3:** The [release history](https://github.com/hyphanet/fred/releases) explains fixes for bulk-queue starvation under real-time traffic, ignored backoff, and data-healing work concentrated near a node's location. These are explicit queueing and routing-resource tradeoffs, rather than unsupported speed claims.

The release history also documents contemporary compatibility decisions, including the 2026 transition away from Java 8, making clear that the historical lineage is not synonymous with an archived project.

### 24. [freenet/freenet-core](https://github.com/freenet/freenet-core)

**Rust — modern Freenet's small-world routing and distributed application-state substrate.** Study the relationship between overlay maintenance and a general contract/state interface. This is an evolving system; the design paper distinguishes implemented mechanisms from experimental and open work.

- **C1:** Ring code makes subscription-renewal timing constraints explicit, including compile-time relationships between renewal budgets and cleanup timeouts. Cancellation and connection lifecycle management must remain coherent during churn. See [the ring implementation](https://raw.githubusercontent.com/freenet/freenet-core/main/crates/core/src/ring.rs).
- **C2:** The [October 2026 design paper](https://freenet.org/pdf/freenet-whitepaper.pdf) describes reusable WebAssembly contracts, application-defined state merging, and summary/delta synchronization over the routing substrate. This broadens the system beyond a fixed storage schema.
- **C3:** The same paper explains gap-targeted neighbor acquisition and performance-aware routing in a small-world topology. These mechanisms give engineers concrete topology/resource policies to examine; their presence does not establish the paper's performance ambitions as measured results.

## Coverage, search method, and limitations

Discovery used live web searches across more than six distinct formulations: general Kademlia libraries; Rust/Go/C++/Java/Python implementations; BitTorrent Mainline and BEP 44 storage; HyParView, Plumtree, and Erlang membership; Chord, Pastry, and Tapestry overlays; browser/WebRTC DHTs; encrypted IPv6 meshes; I2P and Tox discovery; and Freenet/Hyphanet routing. Additional language-focused searches for Haskell, OCaml, and C# broadened discovery but did not produce stronger verified inclusions. Follow-up searches increasingly returned the same implementations, thin wrappers, or coursework, which provided the stopping signal.

Every retained GitHub repository root was opened, and at least one additional primary implementation or documentation source was read. The cited entry points include implementation code, API semantics, architectural documents, test descriptions, and release histories. Criteria assignments and recommended study angles are grounded engineering judgments drawn from those materials. Stars were not used as quality evidence.

The selection deliberately excludes tutorial-only DHTs, simulations without a substantive reusable implementation, lists of links, and higher-level wrappers duplicating an included substrate. FreePastry/Pastry-related results were investigated, but an authoritative substantive GitHub implementation was not verified sufficiently for inclusion; this is a provenance limitation of this search, not a claim that the ecosystem lacks such work. Chord coverage is consequently smaller than Kademlia/Mainline coverage. Whole torrent clients and blockchain systems were not included solely because they use peer networking; the larger retained repositories name the particular overlay subsystem worth studying.

TomP2P is explicitly historical and archived; I2P's Java repository is explicitly an official mirror. Shared ancestry and ecosystem overlap are called out where material, while independent implementations are retained when their architecture differs substantially. No blanket active-maintenance claim is made for the other entries. This was source/documentation research: no repositories were cloned, dependencies installed, candidate code executed, or tests and benchmarks independently run. Links to moving branches and current documentation describe the inspected sources, not a commit-pinned audit, and some design documents lag implementation changes as noted above.
