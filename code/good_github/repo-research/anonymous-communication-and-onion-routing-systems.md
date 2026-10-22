# Anonymous communication and onion routing systems

Research date: **2026-10-09**. This selection covers 23 GitHub codebases implementing anonymous network layers, mix networks, metadata-hiding communication protocols, reusable onion-service libraries, and substantial applications whose architecture depends on anonymity. It includes deployed systems and explicitly identified research or historical implementations. Inclusion is an engineering-study recommendation, not a security certification or a claim that every component is exemplary. Encryption alone is insufficient for this category; the relevant systems also address identities, communication relationships, network locations, or traffic patterns.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, adversarial inputs, or failure handling. **C2** — substantial reusable abstractions supporting multiple applications or operating contexts. **C3** — concrete performance constraints addressed through an intelligible architecture. **C4** — sustained evolution accompanied by compatibility work, testing, or complexity management. Criteria below are evidence-based assessments; documented design goals are not treated as proofs that implementations achieve them.

## Anonymous network layers

### 1. [i2p/i2p.i2p](https://github.com/i2p/i2p.i2p)

**Java — reference I2P router and application libraries; project GitHub source copy, with development/issue links also pointing to I2P's own hosting.** Study the separation between routers, application destinations, unidirectional tunnels, and the network database. The monorepo is counted once, including its streaming and client interfaces.

- **C1:** Inbound and outbound tunnels, expiring destination advertisements, packet fragmentation, and concurrent streaming state interact. The implementation history records concrete fixes for duplicate tunnel fragments, bounded fragment-reassembly storage, garlic parsing bounds, and missing synchronization in streaming acknowledgments. [Implementation history](https://github.com/i2p/i2p.i2p/blob/master/history.txt).
- **C2 / C3:** Applications address cryptographic destinations through message-oriented middleware; the streaming library converts best-effort delivery into ordered streams with congestion control adapted to the network's bandwidth-delay characteristics. This supports web services, messaging, and file transfer through a common substrate. [Technical introduction](https://github.com/i2p/i2p.website/blob/main/content/en/docs/overview/tech-intro.md).
- **C4:** The multi-year history documents protocol/API releases, compatibility changes, concurrency fixes, and resource controls, rather than merely showing an old creation date. The technical introduction itself warns that some sections may lag the implementation.

### 2. [PurpleI2P/i2pd](https://github.com/PurpleI2P/i2pd)

**C++ — independent I2P router implementation.** This is a useful comparison with the Java router: the same network obligations are expressed through native libraries, explicit synchronization, and separately packaged client interfaces.

- **C1:** `TunnelPool` protects inbound/outbound collections separately and coordinates creation, expiration, recreation, and fallback selection when one direction lacks working tunnels. Those are concrete lifecycle invariants under network failure and concurrency. [TunnelPool.cpp](https://github.com/PurpleI2P/i2pd/blob/openssl/libi2pd/TunnelPool.cpp).
- **C3 / C4:** The dated changelog spans multiple years and connects performance work with robustness: stream receive-queue limits, faster NACK processing, congestion-detection changes, steady-clock timers, malformed-reseed handling, race fixes, and evolving OpenSSL/protocol support. [ChangeLog](https://github.com/PurpleI2P/i2pd/blob/openssl/ChangeLog).

The repository's `libi2pd`, client-library, and daemon split is also useful for tracing which responsibilities belong to the router versus application integration.

### 3. [oxen-io/lokinet](https://github.com/oxen-io/lokinet)

**C++ — LLARP layer-three onion-routing overlay.** Study the boundary between operating-system IP traffic and an anonymity network, including path selection, endpoint discovery, flow state, and tunnel interfaces.

- **C1:** The documented backend owns lookups, timeouts, handover, and flow management; routing and DHT messages have distinct parsing and validation components. Correctness crosses packet formats, asynchronous network state, and OS integration. [Project structure](https://github.com/oxen-io/lokinet/blob/dev/docs/project-structure.md).
- **C2:** The architecture exposes an embeddable C interface, separates packet frontends from `.loki`/`.snode` backends, and isolates link, path, cryptography, and platform facilities. These support anonymous services and routed IP traffic through shared machinery. The same document candidly identifies oversized backends and incomplete interface boundaries, making it useful for studying architectural debt as well as abstractions.

Entry points: the [architecture map](https://github.com/oxen-io/lokinet/blob/dev/docs/project-structure.md) and [core library tree](https://github.com/oxen-io/lokinet/tree/dev/llarp). No claim about current release cadence is needed for selection.

## Mix networks and packet machinery

### 4. [katzenpost/katzenpost](https://github.com/katzenpost/katzenpost)

**Go — mixnet monorepo: mix servers, directory authorities, client daemon, and Pigeonhole storage.** Study how packet mixing, network consensus, anonymous replies, and application storage fit together. Former component repositories are not counted separately.

- **C1:** The PKI specification requires a consistent network view for path selection, synchronized key epochs, and advance publication of routing keys. It explicitly says consensus faults can require operator intervention rather than claiming Byzantine fault tolerance. [PKI specification](https://github.com/katzenpost/website/blob/main/content/en/docs/specs/pki.md).
- **C2:** The repository describes reusable Sphinx, wire-protocol, certificate, and PKI libraries, plus Pigeonhole's capability-controlled streams. Couriers separate clients from storage replicas; read and write capabilities allow different application roles without exposing a common stream identifier to storage. [Architecture and Pigeonhole overview](https://github.com/katzenpost/katzenpost#architecture).

Entry points: the PKI specification and the [server subsystem](https://github.com/katzenpost/katzenpost/tree/main/server), whose tree includes startup, key-file, shutdown, and formal-model material. Cryptographic agility and post-quantum mechanisms are implementation subjects, not an independent security endorsement.

### 5. [nymtech/nym](https://github.com/nymtech/nym)

**Rust, with supporting TypeScript — mixnet nodes, clients, service providers, and SDKs in a larger monorepo.** The relevant scope is the mixnet/client transport stack, not its unrelated wallet or economic machinery.

- **C1:** The SDK's TCP proxy must recreate ordered sessions over a network that does not guarantee message order. Its implementation separates incoming/outgoing tasks, tracks session IDs, manages anonymous reply SURBs, and propagates cancellation. This is a concrete example of reconciling stream semantics with anonymous packet transport. [TCP proxy server](https://github.com/nymtech/nym/blob/develop/sdk/rust/nym-sdk/src/tcp_proxy/tcp_proxy_server.rs).
- **C2:** Mixnet clients and the proxy form application-facing abstractions for reaching upstream services and returning replies without learning a conventional client address. The repository also separates node modes, common libraries, and service-provider programs. [Repository architecture](https://github.com/nymtech/nym#the-nym-privacy-platform).

Entry points: the proxy implementation and [SDK tree](https://github.com/nymtech/nym/tree/develop/sdk). This entry counts the monorepo once.

### 6. [nymtech/sphinx](https://github.com/nymtech/sphinx)

**Rust — independently packaged Sphinx packet-format library.** Retained separately from Nym because it is a substantive reusable cryptographic packet implementation, not a generated binding or duplicate repository.

- **C1:** Parsing checks minimum packet size; processing returns distinct forward-hop and final-hop results. Crucially, the code assigns replay detection to the surrounding mix node rather than pretending packet decryption alone provides it. [Packet implementation and malformed-input test](https://github.com/nymtech/sphinx/blob/develop/src/packet/mod.rs).
- **C2:** Packet construction, routing delays, destinations, payload processing, and single-use reply blocks are separate concepts reusable by different mixnet clients and nodes. The explicit packet result types make routing responsibilities visible.
- **Compatibility evidence:** Version handling distinguishes legacy payload keys, derived-key seeds, and a newer SURB recovery mechanism, with tests for version serialization and behavior. This is useful evolution evidence without assigning C4 solely from version numbers. [Version implementation](https://github.com/nymtech/sphinx/blob/develop/src/version.rs).

### 7. [UCL-InfoSec/loopix](https://github.com/UCL-InfoSec/loopix)

**Python — historical Loopix research implementation using Twisted.** Study a comparatively compact continuous-time mixing design; its Python 2-era code should be approached as a research artifact.

- **C1:** The client maintains distinct real, loop, and drop streams, substitutes cover packets when the real queue is empty, and samples subsequent transmission times. These choices are part of traffic-pattern correctness, not merely user-visible functionality. [Client implementation](https://github.com/UCL-InfoSec/loopix/blob/master/loopix/loopix_client.py).
- **C3:** Scheduled callbacks and queued processing separate network I/O from packet handling; separate configurable exponential rates expose the latency/cover-traffic tradeoff. The mix core unwraps a packet into its next destination and requested delay. [Mix core](https://github.com/UCL-InfoSec/loopix/blob/master/loopix/mix_core.py).

The selection does not imply current deployment suitability or that the research implementation fully handles every malicious input.

### 8. [mixminion/mixminion](https://github.com/mixminion/mixminion)

**Python and C — historical Type III anonymous remailer.** Useful for studying delayed anonymous email, reply blocks, fragmentation, persistent queues, and delivery failure recovery. The README calls it an alpha and explicitly warns against relying on it for strong anonymity.

- **C1:** Message construction combines compression, fixed-size padding, fragmentation, checksums, two-leg routes, and reply packets; it checks empty path legs and recognizes excessively compressible payloads. [BuildMessage.py](https://github.com/mixminion/mixminion/blob/master/lib/mixminion/BuildMessage.py).
- **C3:** The history records a concrete MMTP redesign to pipeline packets without waiting for each round-trip acknowledgment, unify client/server sending logic, and bound bandwidth and outgoing connections. It also documents recovery from corrupt directories, interrupted deliveries, and queue-locking errors. [HISTORY](https://github.com/mixminion/mixminion/blob/master/HISTORY).

Its `ClientAPI.py` labels itself an unfinished draft; it is not counted as evidence of a complete stable embedding interface.

## Anonymous communication research systems

### 9. [vuvuzela/vuvuzela](https://github.com/vuvuzela/vuvuzela)

**Go — research messaging system combining mixing with differential-privacy noise.** Study how privacy parameters become distributed round state and how a server coordinates bulk cryptographic work.

- **C1:** Servers sign round settings so participants cannot be tricked into using inconsistent onion keys or mailbox counts that make noise distinguishable. The implementation authenticates the previous server in the chain and tracks whether a round still accepts onions. [Mixnet implementation](https://github.com/vuvuzela/vuvuzela/blob/master/mixnet/mixnet.go).
- **C3:** A decryption worker pool, batched onions, synchronization barriers, and separate service handling expose the computational structure behind mixing and noise generation. This makes throughput/round-latency tradeoffs inspectable without repeating headline benchmark claims.

Entry points: [mixnet code](https://github.com/vuvuzela/vuvuzela/blob/master/mixnet/mixnet.go) and [mixnet tests](https://github.com/vuvuzela/vuvuzela/blob/master/mixnet/mixnet_test.go). This is presented as research software, not a verified currently maintained messaging service.

### 10. [vuvuzela/alpenhorn](https://github.com/vuvuzela/alpenhorn)

**Go — metadata-private contact establishment and conversation bootstrapping.** This complements Vuvuzela with a different protocol problem: initiating communication without requiring prior in-person key exchange.

- **C1:** The keywheel derives round-specific session keys and dialing tokens, advances secrets when erasing old rounds, and refuses derivation for earlier unavailable rounds. Its tests check cross-party token agreement, erased-key behavior, and persistence round trips. [Keywheel tests](https://github.com/vuvuzela/alpenhorn/blob/master/keywheel/keywheel_test.go).
- **C2:** Contact addition, dialing, and key evolution are separate packages. The keywheel exposes session-key and incoming/outgoing dialing-token operations, parameterized by users, rounds, and intents; these are composable conversation-bootstrap primitives rather than UI-bound logic. [Keywheel implementation](https://github.com/vuvuzela/alpenhorn/blob/master/keywheel/keywheel.go).

Treat it as a research codebase. Tests are evidence of specified invariants, not evidence that every serialization or concurrency edge case is safe.

### 11. [dedis/Dissent](https://github.com/dedis/Dissent)

**C++/Qt — archived anonymous group-communication framework based on DC-nets and shuffles.** Its unusually detailed design document is a good entry into group membership, protocol rounds, and accountable anonymity.

- **C1:** Round setup authenticates participants and constructs a fresh round identifier from server contributions to prevent replay and cross-round confusion. The design separates freshness from causal timestamps and explains what happens when servers fail or send invalid messages. [DESIGN](https://github.com/dedis/Dissent/blob/master/DESIGN).
- **C2:** Transport, connection addressing, overlay topology, identity, cryptography, sessions, anonymity protocols, and SOCKS tunneling have separate roles. This permits multiple group protocols and applications over common connection/session machinery. [Design architecture](https://github.com/dedis/Dissent/blob/master/DESIGN).

The [research group's description](https://dedis.cs.yale.edu/dissent/) explicitly frames it as an experimental prototype. Administrative recovery from misbehavior remains part of the documented design; archive status is visible on GitHub.

### 12. [dedis/prifi](https://github.com/dedis/prifi)

**Go — archived experimental DC-net for local-area anonymity.** Study a client/relay/trustee topology optimized for the organizational network setting rather than global onion routing.

- **C1:** The three roles cooperate across communication rounds while membership and connections change. The README describes both protocol-unit tests and integration configurations that exercise clients, trustees, relay startup, and end-to-end SOCKS traffic. [Testing and protocol overview](https://github.com/dedis/prifi).
- **C2:** `PriFi-Lib` is network-independent and uses a `MessageSender` interface. A separate ONet wrapper maps distributed-system entities to protocol roles; local and relay-side SOCKS components expose the anonymity mechanism to ordinary applications. [Architecture document](https://github.com/dedis/prifi/blob/master/README_architecture.md).

Both GitHub and the README identify the archived/experimental status. The architecture is worth studying without treating old build/test instructions as evidence that it currently builds unchanged.

### 13. [kwonalbert/riffle](https://github.com/kwonalbert/riffle)

**Go — historical research prototype for anonymous file sharing and microblogging.** The author explicitly warns that it models protocol performance and must not be adapted directly for real anonymous communication.

- **C1:** The server coordinates verifiable key shuffles, request permutations, upload/download rounds, and proof checks. Per-round channels and wait groups make phase ordering and concurrency obligations concrete. [Server implementation](https://github.com/kwonalbert/riffle/blob/master/server/server.go).
- **C3:** Expensive key-shuffle/proof work is structurally separated from subsequent symmetric packet shuffling; the code exposes both file-sharing and broadcast paths and includes profiling hooks. This supports studying amortization and batching rather than treating anonymity costs as a black box.

Entry points: the server implementation and [experiment scripts](https://github.com/kwonalbert/riffle/tree/master/scripts). Performance-oriented shortcuts and assumptions in the prototype are part of the lesson, not a production-quality claim.

### 14. [kwonalbert/atom](https://github.com/kwonalbert/atom)

**Go — research prototype of a horizontally scalable anonymous broadcast network.** Study the distinction between physical servers and logical group members, and the tradeoffs between trap-based and proof-based execution.

- **C1:** A group member maintains round-specific buffers, condition variables, shuffle verification, and re-encryption verification. Correctness depends on collecting the right batches before progressing through phases. [Member implementation](https://github.com/kwonalbert/atom/blob/master/server/member.go).
- **C2 / C3:** The repository isolates cryptographic operations from servers, clients, directory, trustees, and result storage; physical servers can participate in multiple groups. Partitioning and re-encrypting batches for adjacent groups makes the scale-out mechanism explicit. The code also exposes an even-batch-size assumption rather than hiding it. [Architecture and prototype warning](https://github.com/kwonalbert/atom).

Entry points: `server/member.go` and [integration test](https://github.com/kwonalbert/atom/blob/master/atom_test.go). The author explicitly identifies unresolved security-sensitive work; no deployment recommendation is implied.

### 15. [privacylab/talek](https://github.com/privacylab/talek)

**Go, with CPU/GPU backends — research private publish/subscribe messaging using PIR.** This broadens the category beyond relay-based anonymity: communication access patterns are hidden from untrusted storage services.

- **C2:** Topic handles represent an author's message stream and shareable read access. Below that, the PIR server obtains a registered backend through a common shard interface, separating messaging semantics from computation strategy. [PIR library](https://github.com/privacylab/talek/blob/master/pir/libpir.go).
- **C3:** The implementation exposes batch size, cell count, and cell length, validates request-mask dimensions, and manages backend-owned database memory. The README documents alternative CPU, CUDA, and OpenCL implementations and the extra testing needed when the backend interface changes. [Backend and test guidance](https://github.com/privacylab/talek).

Entry points: `pir/libpir.go` and [PIR subsystem](https://github.com/privacylab/talek/tree/master/pir). This is a research selection; ongoing maintenance and contemporary GPU-toolchain compatibility were not established.

## Onion-service libraries and communication applications

### 16. [blueprint-freespeech/gosling](https://github.com/blueprint-freespeech/gosling)

**Rust with C/C++ and other language bindings — onion-service authentication and authorization library.** A substantive protocol/library project that generalizes ideas from Ricochet Refresh.

- **C1:** Identity and endpoint handshakes have required call ordering, distinct proof domains, fresh cookies, identity signatures, and proofs of ownership of onion-service client-authorization keys. These prevent several forms of impersonation and state confusion. [Protocol specification](https://gosling.technology/gosling-spec.xhtml).
- **C2:** Application-specific challenges and named endpoints/channels let different applications reuse authentication without fixing their application protocol. Separate Tor providers cover mock testing, a C Tor daemon, and an explicitly experimental Arti integration; the repository documents integration and fuzz-test targets across these boundaries. [Library structure and test configuration](https://github.com/blueprint-freespeech/gosling).

Entry points: the protocol specification and [Rust library manifest](https://github.com/blueprint-freespeech/gosling/blob/main/source/gosling/crates/gosling/Cargo.toml). The experimental provider is not described as production-ready.

### 17. [blueprint-freespeech/ricochet-refresh](https://github.com/blueprint-freespeech/ricochet-refresh)

**C++/Qt — peer-to-peer instant messaging over Tor onion services.** This is the substantive continuation of Ricochet; the original repository is not counted again. Its default branch identifies itself as development/alpha and points to `maint-3.0` for the release branch.

- **C1:** Peer authentication, contact requests, unknown-peer resource exhaustion, channel authorization, malformed packets, and connection teardown interact. The protocol defines when channel operations are allowed and when unknown connections should expire. [Protocol v3](https://github.com/blueprint-freespeech/ricochet-refresh/blob/main/doc/protocol-v3.md).
- **C2:** Connection, packet, and channel layers separate transport from extensible operations. Named channel types multiplex different functions, while authentication attaches credentials to a connection and version negotiation supports protocol evolution. [Protocol layers](https://github.com/blueprint-freespeech/ricochet-refresh/blob/main/doc/protocol-v3.md).

Start with the protocol and [design overview](https://github.com/blueprint-freespeech/ricochet-refresh/blob/main/doc/design.md). Some prose carries older Tor terminology; the study recommendation concerns the application protocol, not every historical transport explanation.

### 18. [briar/briar](https://github.com/briar/briar)

**Java — official substantive GitHub mirror of Briar's independently hosted source.** The relevant subsystems are Bramble transport/synchronization and the applications built on them. Briar uses Tor for Internet communication and Bluetooth/Wi-Fi for local synchronization; those transports do not have identical anonymity properties.

- **C1:** `ReorderingWindow` maintains a persisted bitmap, rejects duplicates/out-of-window indices, bounds sequence numbers, and implements explicit sliding rules. This is a compact study of transport-state invariants. [ReorderingWindow.java](https://github.com/briar/briar/blob/master/bramble-core/src/main/java/org/briarproject/bramble/transport/ReorderingWindow.java).
- **C2:** Bramble separates record reading, synchronization sessions, database operations, events, and transport plugins. `IncomingSession` dispatches acknowledgments, offers, requests, messages, and version records onto database execution paths shared across transports. [IncomingSession.java](https://github.com/briar/briar/blob/master/bramble-core/src/main/java/org/briarproject/bramble/sync/IncomingSession.java).

The session code also documents a blocking-read interruption limitation. That makes the boundaries and remaining lifecycle complexity visible. The GitHub repository explicitly labels itself a mirror of the Briar project's source host.

### 19. [agl/pond](https://github.com/agl/pond)

**Go — historical asynchronous messaging system over Tor.** The author explicitly says the project is in stasis and directs new users elsewhere. Retained for its distinctive treatment of metadata, revocation, and offline delivery.

- **C1:** Fixed-size exchanges, randomized connection times, ratcheting keys, and replay handling are designed together. The technical document explains why visible counters can leak metadata and how removing them changes replay and key-selection requirements. [Technical design](https://github.com/agl/pond/blob/master/doc/tech.html).
- **C2:** The repository separates transport, client state, shared-secret introduction, and BBS group signatures. Group signatures let a server accept authorized senders and support revocation without receiving an ordinary list of sender identities. [Component map](https://github.com/agl/pond).

Entry points: the technical design and [group-signature implementation tree](https://github.com/agl/pond/tree/master/bbssig). The design explicitly acknowledges that a global observer capable of breaking its Tor assumption breaks Pond's corresponding guarantee.

### 20. [simplex-chat/simplexmq](https://github.com/simplex-chat/simplexmq)

**Haskell — metadata-minimizing messaging routers, client library, and agent.** This is a protocol-stack selection, not a claim that every direct connection provides onion-routing anonymity. Its category fit is the avoidance of shared participant identifiers and the explicit treatment of transport privacy and proxying.

- **C1:** Each queue has distinct sender/recipient identifiers and authorization keys. The protocol specifies command authentication, acknowledgments, subscription transitions, transport negotiation, and proxy forwarding under potentially compromised routers. [SMP specification](https://github.com/simplex-chat/simplexmq/blob/stable/protocol/simplex-messaging.md).
- **C2:** Persistent one-way queues compose into duplex conversations and higher-level contacts, groups, and broadcasts without exposing those application objects as router-level identities. The server, client, and agent separate queue transport from connection management. [Components](https://github.com/simplex-chat/simplexmq).

The current specification includes batching and a detailed version history. It also explicitly bounds message retention and assigns stronger delivery guarantees to higher layers, making privacy/reliability tradeoffs unusually clear.

### 21. [onionshare/onionshare](https://github.com/onionshare/onionshare)

**Python, Qt, and web components — file transfer, website hosting, and chat over onion services.** Substantial application-level anonymity engineering: local service lifecycle, private access, file handling, and browser-facing security.

- **C1:** Onion-service client authentication and the delivery of addresses/private keys form separate trust boundaries. The security design explains that anonymity can be lost through how an address is shared. The changelog adds concrete failure cases: symlink traversal, upload-mode enforcement, username validation, and shutdown races. [Security design](https://docs.onionshare.org/2.6/en/security.html).
- **C4:** The history traces years of changes including the 2014 XSS fix, Python/Qt migrations, ephemeral onion services, client-authentication changes, CI/packaging work, and later reconnect/shutdown fixes. This is sustained compatibility and security maintenance evidence. [Changelog](https://github.com/onionshare/onionshare/blob/main/CHANGELOG.md).

Those two documents are the best starting points for understanding why a seemingly simple Tor application needs careful state and input handling.

### 22. [freedomofpress/securedrop](https://github.com/freedomofpress/securedrop)

**Primarily Python, with Rust and deployment configuration — anonymous source/journalist communication.** Counted once for the application/server repository; separate workstation and client projects are not duplicate entries. Its README says security and bug fixes continue while much feature work occurs in related projects.

- **C1:** Public source and authenticated journalist onion services have separate roles; encrypted submissions, source identity handling, minimal metadata, and offline document viewing shape the architecture. Recent implementation history includes cross-worker session-key corruption and atomic API idempotence fixes. [System architecture](https://docs.securedrop.org/en/stable/what_is_securedrop.html).
- **C4:** The changelog spans early DeadDrop/SecureDrop migration through current APIs, documenting unit/integration testing, database and deployment migrations, asynchronous deletion, backup verification, and compatibility/security repairs. [Changelog](https://github.com/freedomofpress/securedrop/blob/develop/changelog.md).

Study it for the composition of software and operational isolation. Older documentation sections should be read alongside current source and release notes rather than assumed to describe every current deployment detail.

### 23. [maqp/tfc](https://github.com/maqp/tfc)

**Python with a Rust component — Tinfoil Chat, onion-routed messaging with separated transmitter, network relay, and receiver.** The data-diode architecture makes it a distinct systems study. **Material limitation:** the current README warns that the `/rr` command enables covert exfiltration; the 2026 update log says the unit tests require rewriting. This entry is not a deployment endorsement.

- **C1:** Ratchet ordering, one-way links, duplicate suppression, data validation, and strict separation of key/plaintext roles interact. The update log describes typed key/datagram objects and distinct cryptographic paths intended to make these boundaries easier to check. [Update log](https://github.com/maqp/tfc/wiki/Update-Log).
- **C3:** Traffic masking uses separate input, sender, noise-generator, and logging processes with prioritized queues and timed output. The design discusses the tension between sending real data, maintaining cover traffic, and hiding timing differences; it acknowledges the limits of timing guarantees in Python. [Security design](https://github.com/maqp/tfc/wiki/Security-design).

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations, including onion-routing implementations across Tor/I2P/Lokinet; Sphinx and mixnet packet libraries; Loopix/Vuvuzela/Alpenhorn; DC-nets and anonymous broadcast; PIR/private publish-subscribe; Type II/III remailers; Tor-based messengers; reusable onion-service authentication libraries; whistleblower/file-sharing systems; and official GitHub mirrors. Follow-up searches excluding familiar names added Gosling, Briar, and TFC. Later queries increasingly returned already inspected projects, forks, launchers, lists, and lightly substantiated new projects.

All 23 repository roots were opened directly, with canonical URLs and default branches checked from GitHub pages. Each retained entry has additional opened primary implementation, design, or history material; relevant excerpts were read, not accepted solely from search snippets. The shared unauthenticated GitHub API quota became exhausted, so verification continued through public repository HTML and raw source files. Nothing was installed, built, cloned, or executed from these repositories. Source and test inspection therefore does not establish that an old toolchain still builds, that tests currently pass, or that documented guarantees hold against every adversary.

Important boundaries and exclusions:

- **Tor and Arti:** Tor is central to the category, but [torproject/tor](https://github.com/torproject/tor) now presents a migration notice instead of a substantive default-branch source tree. The search did not establish an official substantive GitHub mirror for Arti; third-party mirrors were not substituted. This GitHub-only constraint is a material gap, not a judgment on Tor's engineering quality.
- **Related implementations:** The original Ricochet is represented by its substantive Refresh continuation. The [deprecated Go Nym mixnet](https://github.com/nymtech/nym-mixnet) points to the Rust replacement and is not counted again. Loopix remains separately useful as a different research implementation; Sphinx is separately retained for its reusable packet-library scope.
- **Other hosts and adjacent categories:** Cwtch did not yield a verified qualifying GitHub mirror in this search. General encrypted messengers, ordinary VPNs, censorship-circumvention tools without an anonymity layer, cryptocurrency-only mixers, and content-storage networks were not included merely for mentioning privacy. Mixmaster search results did not establish a sufficiently clear canonical GitHub implementation for inclusion.
- **Historical status:** Dissent and PriFi are explicitly archived; Pond is explicitly in stasis; Mixminion and the named research prototypes carry the qualifications above. No maintenance claim is inferred from stars, repository age, or a recent push. Claims about performance are architectural observations, not comparative benchmark results.

The set is deliberately a selection guide across threat models and implementation styles. Low-latency onion routing, timed mixing, DC-nets, PIR, identifier minimization, and endpoint isolation solve different parts of anonymous communication and should not be treated as interchangeable guarantees.
