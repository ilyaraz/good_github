# Network routing protocol implementations

Research date: **2026-10-09**.

This selection covers 24 GitHub repositories containing substantive implementations of dynamic network routing protocols: Internet routing suites, BGP engines and libraries, distributed interior routing, IP and Ethernet mesh routing, multicast routing, constrained-device routing, and alternative network architectures. Operating systems and other monorepos are included only for the named routing subsystem and count once. Protocol configuration collections, route visualizers, static route managers, packet parsers without a routing engine, and ordinary application-level request routers are outside scope.

The criteria are engineering study lenses, not certifications of correctness or deployment recommendations:

- **C1 — Difficult correctness:** protocol invariants, concurrency, numerical semantics, hostile input, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces and components serving multiple protocols, integrations, or operating modes.
- **C3 — Performance with structure:** concrete resource or processing constraints addressed through an understandable design.
- **C4 — Sustained evolution:** changes across years accompanied by compatibility work, testing, or explicit complexity management.

Each entry identifies at least two criteria and links directly to primary material that was read. The engineering conclusions are grounded interpretations of that material. Repository identity and archive state were checked through GitHub repository pages or the GitHub API; none of the selected repositories was marked archived at the research date. This alone does not establish ongoing maintenance. Mirrors, development branches, and particularly quiet projects are identified below.

## General-purpose routing suites

### 1. [FRRouting/frr](https://github.com/FRRouting/frr)

**C; multiprotocol routing suite.** Study how independently running protocol daemons coordinate with Zebra, and how a large C system introduces concurrency without replacing its event-driven foundations. BGP, OSPF, IS-IS, RIP, and multicast implementations make this a useful comparison environment within one codebase.

- **C1:** The [process architecture](https://github.com/FRRouting/frr/blob/master/doc/developer/process-architecture.rst) documents event ownership, cross-thread scheduling, caller-owned handler arguments, and the restriction against scheduling duplicate read/write tasks for one descriptor. These are concrete lifecycle and concurrency constraints.
- **C2:** That same event infrastructure supports multiple daemons and per-thread event loops, providing a shared execution model rather than separate scheduling machinery for each protocol.
- **C3:** [Next-hop tracking](https://github.com/FRRouting/frr/blob/master/doc/developer/next-hop-tracking.rst) replaces periodic whole-table validation with registrations and asynchronous Zebra notifications. The explanation connects the design to event-loop fairness and faster reaction to reachability changes; its performance goals should not be mistaken for measured guarantees.

### 2. [CZ-NIC/bird](https://github.com/CZ-NIC/bird)

**C; BGP, OSPF, RIP, and Babel daemon.** This is the project organization's substantive GitHub mirror/copy; the [README](https://github.com/CZ-NIC/bird/blob/master/README) points development to CZ.NIC's GitLab. Study an architecture centered on common routing tables, protocol modules, and a route-filter language.

- **C2:** The [design introduction](https://github.com/CZ-NIC/bird/blob/master/doc/prog-intro.sgml) explains separation of protocol, operating-system, resource-management, configuration, and filtering modules. Multiple tables and common address abstractions support reuse across protocols and address families.
- **C1:** The [BGP implementation overview](https://github.com/CZ-NIC/bird/blob/master/proto/bgp/bgp.c) explains simultaneous session-establishment connections, opaque preservation of unknown transitive attributes, and graceful-restart retention followed by stale-route removal.
- **C3:** The same source describes bucketing outgoing updates by attributes and replacing an already queued update for a destination. This exposes a specific batching and redundant-work reduction strategy.

The design introduction contains historical architecture discussion; use current source and the intended release branch when investigating threading behavior.

### 3. [holo-routing/holo](https://github.com/holo-routing/holo)

**Rust; routing suite with modeled management interfaces.** Study protocol engines organized as separate crates, including shared implementations for protocol versions, and configuration transactions integrated with the routing stack.

- **C2:** The [architecture guide](https://github.com/holo-routing/holo/wiki/Architecture) describes protocol logic separated from network I/O, reusable protocol libraries assembled by `holod`, and an internal message bus connecting routing, interfaces, authentication keys, and protocol instances.
- **C1:** The [implementation overview](https://github.com/holo-routing/holo/blob/master/README.md) describes transaction-based configuration, supervised packet-decoding tasks, fuzzing support, and recording/replaying event streams. These mechanisms address partial configuration, malformed input, and reproducibility of state-machine failures.
- **C3:** The overview explains offloading I/O and CPU-intensive work to separate Tokio tasks. This is an architectural approach to concurrency, not evidence for a particular throughput figure.

The architecture wiki is older than the current source and has incomplete sections; the report does not infer unlisted features from it.

### 4. [mc36/freeRtr](https://github.com/mc36/freeRtr)

**Java routing control plane, with C/P4 dataplane components; broad software router.** The [project README](https://github.com/mc36/freeRtr/blob/master/readme.md) explicitly lists GitHub among its synchronized source locations. Relevant code is under `src/org/freertr`, especially `rtr`, `ip`, and `tab`; unrelated utilities in the monorepo are not part of this recommendation.

- **C2:** The [common `ipRtr` abstraction](https://github.com/mc36/freeRtr/blob/master/src/org/freertr/ip/ipRtr.java) connects protocols to the IP forwarder through computed, redistributed, and changed route tables, with common handling for unicast, multicast, and FlowSpec. It is useful for studying cross-protocol route exchange and forwarding integration.
- **C3:** The [BGP engine](https://github.com/mc36/freeRtr/blob/master/src/org/freertr/rtr/rtrBgp.java) has full and incremental computation paths, change counters, per-family changed tables, and selective notifications to forwarding and VPN consumers. Study how recomputation scope is controlled across many route families.

Its breadth is substantial, but individual protocol classes can be large; the shared abstractions are the best starting point.

### 5. [bio-routing/bio-rd](https://github.com/bio-routing/bio-rd)

**Go; routing daemon and protocol components.** The repository describes BGP, IS-IS, and OSPF work, while its documented main executable is a configurable BGP speaker. Study its route-table and redistribution design without assuming feature parity among all named protocols.

- **C2:** The [routing-table design](https://github.com/bio-routing/bio-rd/blob/master/Documentation/user/routingtable/overview.md) uses a common LocRIB per VRF, protocol clients, and composable filter chains. This makes protocol integration and policy placement explicit.
- **C1:** The [redistribution implementation guide](https://github.com/bio-routing/bio-rd/blob/master/Documentation/dev/redistribution.md) explains `Path.CheckRedistribute`, copying paths before consumers modify attributes, protocol-specific conversion, and deduplication. The difficult invariant is that one consumer's filtering or conversion must not corrupt another consumer's view.

This smaller project is especially useful for comparing a shared-RIB model with protocol-specific RIB designs. The guide contains a misspelled internal link; the working routing-table path is linked above.

## BGP engines and programmable libraries

### 6. [openbgpd/openbgpd-openbsd](https://github.com/openbgpd/openbgpd-openbsd)

**C; official imported OpenBSD source for OpenBGPD.** This is the substantive protocol-source mirror; upstream contribution goes through OpenBSD. It is counted once, without separately listing the portability framework. The current organization is `openbgpd`; older `openbgpd-portable` organization URLs redirect.

- **C1:** The [daemon manual](https://github.com/openbgpd/openbgpd-openbsd/blob/master/src/usr.sbin/bgpd/bgpd.8) specifies rejection of erroneous, looping, and unreachable-next-hop paths before best-path tie breaking. The [route decision engine](https://github.com/openbgpd/openbgpd-openbsd/blob/master/src/usr.sbin/bgpd/rde.c) also shows privilege dropping, `chroot`, `pledge`, and message-passing boundaries.
- **C2:** The manual and RDE source separate TCP session management, route filtering/selection, and parent-process kernel synchronization. Named RIBs, policy processing, and distinct IPC responsibilities make the code useful for studying reusable control-plane services and containment boundaries.

Start with the manual's process description, then trace an update through `rde.c`; this avoids confusing the portable build repository with the protocol engine itself.

### 7. [osrg/gobgp](https://github.com/osrg/gobgp)

**Go; BGP daemon and embeddable library.** Study how one implementation serves standalone routing processes and applications that program routing behavior directly.

- **C2:** The [native-library guide](https://github.com/osrg/gobgp/blob/master/docs/sources/lib.md) demonstrates construction of a `BgpServer`, policy assignment, peer lifecycle, event callbacks, route injection, and route inspection through typed APIs. Packet types and server control can therefore be reused without scripting the CLI.
- **C1:** The [session state machine](https://github.com/osrg/gobgp/blob/master/pkg/server/fsm.go) distinguishes transport failure, notification, invalid message, timer expiry, administrative shutdown, and graceful restart. Atomic state wrappers and connection-manager cancellation expose the concurrency issues behind those transitions.

The inspected default-branch library example imports the v4 module path. Match examples to the release used in a study or integration; do not silently mix them with older major-version APIs.

### 8. [Exa-Networks/exabgp](https://github.com/Exa-Networks/exabgp)

**Python; programmable BGP speaker.** Its external-process API supports route injection, anycast control, monitoring, and FlowSpec automation. It does not install kernel forwarding entries. The [README](https://github.com/Exa-Networks/exabgp/blob/main/README.md) explicitly distinguishes the stable `5.0` branch from the developing asyncio-based `main` branch.

- **C2:** The process API and protocol implementation separate application policy from BGP session and message handling. This supports several operational applications using the same speaker rather than a fixed routing policy.
- **C1:** The [asynchronous command scheduler](https://github.com/Exa-Networks/exabgp/blob/main/src/exabgp/reactor/asynchronous.py) documents why peers must not read partially applied command batches. It tracks command application, closes discarded coroutine/generator callbacks, and reports callback failures to avoid indefinitely waiting clients.
- **C3:** The scheduler limits generator work before requeuing it, making fairness visible in the implementation. Its development-branch behavior should not be attributed to the stable branch.

### 9. [jwhited/corebgp](https://github.com/jwhited/corebgp)

**Go; BGP finite-state-machine library.** This is a deliberately focused foundation for custom speakers, collectors, or applications that want ownership of route storage and UPDATE generation.

- **C2:** The [plugin interface](https://github.com/jwhited/corebgp/blob/main/README.md) exposes capability negotiation, OPEN validation, established-session writers, UPDATE handlers, and closure callbacks. Optional composable UPDATE decoding is separate from policy; the library does not supply a RIB or originate application routes itself.
- **C1:** The [FSM implementation](https://github.com/jwhited/corebgp/blob/main/fsm.go) coordinates state transitions with a peer manager, handles competing FSMs, cancels outstanding dials, stops timers, and closes reader resources. The writer's lifetime ends with the established session, an important API invariant.

The README identifies the public API as pre-1.0 and not stable. That caveat is material for reuse, but does not diminish its value as an unusually clear study of BGP session/application separation.

### 10. [osrg/rustybgp](https://github.com/osrg/rustybgp)

**Rust; BGP implementation with Linux kernel integration.** Study parallel route-table processing and the coordination between route changes, policy, monitoring subscribers, and peers.

- **C3:** The [table manager](https://github.com/osrg/rustybgp/blob/master/daemon/src/table_manager.rs) hashes destinations into separately locked shards and uses `ArcSwap` for shared snapshots such as policy and subscribers. The code makes the granularity of parallelism concrete.
- **C1:** The same file documents why subscribers must be loaded inside the shard lock so updates after a snapshot are observable. Prefix-limit handling also explicitly requires a CEASE notification and session closure. The [end-to-end test guide](https://github.com/osrg/rustybgp/blob/master/tests/e2e/README.md) covers graceful restart in both roles, BFD-triggered teardown, Add-Path, and interoperability with a two-octet-AS BIRD peer.

The project advertises GoBGP API/configuration compatibility, but lists differences and missing features; this report does not treat that as universal drop-in equivalence or a benchmark result.

## Controller integration and distributed interior routing

### 11. [opendaylight/bgpcep](https://github.com/opendaylight/bgpcep)

**Java; BGP/BGP-LS and PCEP components for OpenDaylight.** This is the official GitHub mirror of the Gerrit project. Count the BGP, PCEP, and supporting modules together. Study how routing sessions and route stores integrate into a modeled controller rather than a traditional router CLI.

- **C2:** The [BGP developer guide](https://github.com/opendaylight/bgpcep/blob/master/docs/bgp-developer-guide.rst) describes parser/serializer extension registries, YANG models, `RIBSupport`, and a pipeline from received routes through import policy and best-path selection to advertised routes.
- **C1:** The current [BGP session implementation](https://github.com/opendaylight/bgpcep/blob/master/bgp/rib-impl/src/main/java/org/opendaylight/protocol/bgp/rib/impl/BGPSessionImpl.java) exposes guarded state, negotiated hold timers, per-family synchronization, multipath decoder constraints, and graceful-restart capabilities around a Netty channel.

Some developer-guide examples still reference older OpenDaylight releases. Use them for the architectural model and the current source for exact APIs and capability behavior.

### 12. [facebook/openr](https://github.com/facebook/openr)

**C++; distributed interior routing protocol/platform.** Open/R supplies a useful contrast to conventional link-state databases: routing runs over a general distribution mechanism for network state. The open-source architecture documentation explicitly says its BGP speaker is not included.

- **C1:** The [KvStore design](https://github.com/facebook/openr/blob/main/openr/docs/Protocol_Guide/KvStore.md) describes eventual consistency using CRDT-based state, initial synchronization, peer-down cleanup, and separate flooding domains. These create consistency and failure-recovery obligations beyond local shortest-path computation.
- **C2:** The [architecture guide](https://github.com/facebook/openr/blob/main/openr/docs/Protocol_Guide/Architecture.md) defines independently instantiable modules with thread-safe public APIs and asynchronous message queues. Discovery, state distribution, decisions, and forwarding updates can be studied as separate cooperating components.

The design guide explicitly deprioritizes early CPU/memory optimization. This entry therefore does not award C3 merely because the system targets large networks.

### 13. [brunorijsman/rift-python](https://github.com/brunorijsman/rift-python)

**Python; substantial research/interoperability implementation of Routing in Fat Trees.** The repository contains protocol state machines, RIB/FIB handling, system tests, and interoperability work, rather than only configuration examples. Treat it as a draft-era study implementation: its README and feature matrix reference different older draft versions, and the README calls it work in progress.

- **C1:** The [disaggregation guide](https://github.com/brunorijsman/rift-python/blob/master/doc/disaggregation-feature-guide.md) explains why default northbound routes need automatic more-specific or negative routes after particular failures. This makes topology-dependent recovery and blackhole avoidance tangible.
- **C3:** The [flooding-reduction guide](https://github.com/brunorijsman/rift-python/blob/master/doc/flooding-reduction-feature-guide.md) explains per-child flood-repeater selection, redundant paths, and reduced duplicate topology information in fat trees. It connects scaling pressure directly to the protocol structure.

[Automated testing documentation](https://github.com/brunorijsman/rift-python/blob/master/doc/automated-testing.md) describes unit, multi-node system, and Juniper interoperability tests. This is not a claim of compliance with the final RIFT RFC.

## Mesh and ad hoc routing

### 14. [jech/babeld](https://github.com/jech/babeld)

**C; Babel distance-vector routing daemon.** A particularly direct place to study loop avoidance under changing links and route metrics, including source-specific route representations.

- **C1:** [Route processing](https://github.com/jech/babeld/blob/master/route.c) implements feasibility using sequence numbers and advertised metrics. Its retraction code explains why simply removing a kernel route can create a loop, and therefore changes the metric to infinity. Route aging and metric smoothing are nearby.
- **C4:** The [change history](https://github.com/jech/babeld/blob/master/CHANGES) records years of parser, kernel, and interoperability fixes, explicit incompatible changes, and the addition of a behavior-regression test suite in 2026. The history carefully says that suite catches behavior changes rather than necessarily proving correctness.
- **C3:** The history also documents incremental redistribution instead of a full kernel route dump per change, and per-neighbor buffering for unicast. These are concrete processing/memory tradeoffs.

### 15. [OLSR/olsrd](https://github.com/OLSR/olsrd)

**C; OLSRv1 daemon from the OLSR/Freifunk community.** Study adaptation of link-state routing to wireless link quality, alongside the separation between topology computation and metric implementation.

- **C2:** The [link-quality plugin interface](https://github.com/OLSR/olsrd/blob/master/src/lq_plugin.h) provides callbacks for loss measurement, cost calculation, serialization, and state copying. Different metric implementations can share the protocol's topology and routing machinery.
- **C3:** The [SPF implementation](https://github.com/OLSR/olsrd/blob/master/src/olsr_spf.c) explains its AVL-tree-based candidate queue, chosen for repeated minimum extraction and re-keying, and includes an SPF backoff timer. This is a concrete implementation of route computation under repeated topology updates.

This is distinct from OONF/OLSRv2 below, with a different protocol generation and architecture. The repository contains an `unmaintained` directory, so the selection applies to the routing core and inspected plugin interface, not uniformly to every bundled component.

### 16. [OLSR/OONF](https://github.com/OLSR/OONF)

**C; OLSR.org Network Framework containing OLSRv2, NHDP, and DLEP components.** Study a second-generation implementation organized around a reusable networking framework rather than interpreting it as another copy of olsrd v1.

- **C2:** The [source organization](https://github.com/OLSR/OONF/tree/master/src) separates common utilities, configuration/core services, RFC 5444 message machinery, neighborhood discovery, and OLSRv2. The routing implementation uses shared timer, memory-class, address, and operating-system route abstractions.
- **C1:** [OLSRv2 routing](https://github.com/OLSR/OONF/blob/master/src/olsrv2/olsrv2/olsrv2_routing.c) coordinates per-domain topology changes with an asynchronous kernel route queue. Shutdown interrupts outstanding operations and queues installed-route removal, making callback lifetime and kernel/control-plane consistency visible.
- **C3:** The same file explicitly rate-limits Dijkstra runs and tracks changed domains, addressing redundant recomputation without hiding the scheduling structure.

### 17. [torvalds/linux](https://github.com/torvalds/linux)

**C; specifically the kernel's `net/batman-adv` mesh-routing implementation.** The [kernel documentation](https://github.com/torvalds/linux/blob/master/Documentation/networking/batman-adv.rst) explains how B.A.T.M.A.N. Advanced routes Ethernet frames and presents a virtual switch to higher protocols. This entry covers its distributed mesh protocol, not generic Linux forwarding or the rest of the kernel. It also avoids counting an independently hosted copy of the same subsystem.

- **C1:** The [B.A.T.M.A.N. V originator-message implementation](https://github.com/torvalds/linux/blob/master/net/batman-adv/bat_v_ogm.c) handles reference-counted originators, concurrent hash insertion, packet-buffer ownership, RCU-protected interface traversal, and explicit aggregation-queue locking. Network state changes must remain safe across kernel execution contexts.
- **C3:** The same implementation aggregates originator messages within the interface MTU and a maximum byte budget, using delayed work and randomized transmission timing. This provides a concrete study of control-packet overhead reduction alongside concurrency and memory-lifetime constraints.

## Multicast routing

### 18. [troglobit/pimd](https://github.com/troglobit/pimd)

**C; stand-alone PIM-SM/SSM daemon.** Study designated-router elections, rendezvous-point behavior, source/shared-tree transitions, and Join/Prune state in a compact multicast implementation. This is a quiet historical codebase: GitHub metadata showed its last push in 2022, although it was not archived.

- **C1:** [PIM protocol processing](https://github.com/troglobit/pimd/blob/master/src/pim_proto.c) checks checksums and neighbor/interface eligibility, handles zero-holdtime neighbor departure, and coordinates multicast state and timers. Correct reverse-path and election behavior is central to avoiding duplicate or missing delivery.
- **C4:** The [changelog](https://github.com/troglobit/pimd/blob/master/ChangeLog.md) spans many years of platform testing and protocol fixes. It explicitly records that correcting the RP hash algorithm improves Cisco interoperability while breaking compatibility with older pimd versions, and separately documents CLI incompatibility.

The changelog's 3.0 section is labeled unreleased. Neither that section nor a present-day README should be read as evidence of a recent stable release.

### 19. [troglobit/mrouted](https://github.com/troglobit/mrouted)

**C; DVMRP multicast routing daemon.** This repository preserves a historically important protocol while also documenting substantial recent engineering work. Study multicast parent/child topology and the relationship between route reports, forwarding state, and interface failures.

- **C1:** The [route engine](https://github.com/troglobit/mrouted/blob/master/src/route.c) updates child/subordinate bitmaps as interfaces and neighbors change, expires routes through failed parents, validates metrics, and interprets poison-reverse reports.
- **C4:** The [changelog](https://github.com/troglobit/mrouted/blob/master/ChangeLog.md) shows evolution from 2021 through 2026 with tunnel tests, route-list refactoring, timer/socket replacement, and parser hardening. The 2026 interface-rescan work preserves learned routes and prunes while keeping unchanged interface identifiers stable.
- **C3:** The timer/socket refactor and earlier route-report transmission at peering startup connect responsiveness improvements to specific implementation changes, without requiring an unsupported throughput claim.

## Routing in constrained-device stacks

### 20. [contiki-ng/contiki-ng](https://github.com/contiki-ng/contiki-ng)

**C; RPL Classic and RPL Lite within an IoT operating-system monorepo.** Scope is the RPL subsystem, not the whole OS. The [RPL programming guide](https://github.com/contiki-ng/contiki-ng/blob/develop/doc/programming/RPL.md) is unusually explicit about the engineering cost of implementing more of a standard.

- **C1:** DODAG formation, preferred-parent selection, Trickle-driven advertisements, and freshness checks on link-quality estimates show why apparently local parent choices affect network-wide reachability and stability.
- **C3:** The guide compares storing-mode routing tables against non-storing source-route headers: memory moves toward the root, while downward packets grow with path length. RPL Lite removes multiple-instance/DODAG and storing-mode complexity to reduce footprint, at a documented interoperability cost.
- **C4:** The guide traces Classic to the original implementation and Lite to a 2017 rewrite informed by deployment experience. The simplification is explicit complexity management over years, rather than age alone.

The repository's default branch is `develop`; the linked guide is on that verified branch.

### 21. [RIOT-OS/RIOT](https://github.com/RIOT-OS/RIOT)

**C; GNRC RPL subsystem within the RIOT operating system.** Study RPL integrated with a threaded, modular embedded networking stack. This is an independent implementation from Contiki-NG.

- **C1:** The [control-option validator](https://github.com/RIOT-OS/RIOT/blob/master/sys/net/gnrc/routing/rpl/gnrc_rpl_validation.c) checks message-specific option placement, option lengths, padding, and exact aggregate consumption. It is a useful concrete example of validating variable-length routing messages before acting on them.
- **C3:** The [RPL interface and configuration documentation](https://github.com/RIOT-OS/RIOT/blob/master/sys/include/net/gnrc/rpl.h) ties routing capacity to neighbor-information-base sizing, alternative-parent capacity, thread stack/priority, and a bounded message queue. The memory consequences of downward routing are visible to integrators.

The inspected documentation explicitly limits GNRC RPL to storing mode with OF0 and lists missing interoperability features. The objective-function manager registers OF0; an extension interface is not evidence that MRHOF is implemented.

### 22. [openthread/openthread](https://github.com/openthread/openthread)

**C++; Thread mesh routing within the OpenThread stack.** Scope is the MLE/router-table subsystem. Study bounded routing state, changing router identities, bidirectional wireless link information, and the interaction between route repair and control-message timing.

- **C1:** [Router-table implementation](https://github.com/openthread/openthread/blob/main/src/core/thread/router_table.cpp) compares router-ID sequence numbers with serial-number arithmetic, updates next hops from Route TLVs, and tracks finite/infinite reachability changes. It also repairs the ID-to-array-index mapping when deletion moves the last router entry.
- **C3:** Bounded router storage, direct ID indexing, and coalesced change events expose the resource model. The route-update code schedules a targeted unicast advertisement when a neighbor's link view is inconsistent, avoiding waiting for the normal advertisement cycle.
- **C2:** The [router-table interface](https://github.com/openthread/openthread/blob/main/src/core/thread/router_table.hpp) separates allocation, path costs, next-hop selection, and change events from callers elsewhere in the stack.

## Alternative network architectures

### 23. [scionproto/scion](https://github.com/scionproto/scion)

**Go; SCION inter-domain routing architecture implementation.** Scope includes the control service's path discovery, registration, and lookup, rather than treating every SDK or transport component as a routing protocol. This is a substantive alternative to destination-only BGP routing.

- **C1:** The [control-plane design](https://github.com/scionproto/scion/blob/master/doc/control-plane.rst) describes signed path-construction beacons, validation at each receiving AS, certificate retrieval, and policy-constrained propagation. Correctness combines path construction with authenticity and trust handling.
- **C2:** Reusable up, down, and core path segments separate discovery from the endpoint's construction of an end-to-end path. Registration and lookup are distinct services in that pipeline, supporting several valid path combinations.
- **C3:** The same design divides inter-core and intra-domain beaconing and selects subsets of stored beacons for periodic propagation. This is a concrete strategy for bounding dissemination work while retaining path choice.

Start with the control-plane document, which explains the corresponding service responsibilities and wire-level concepts together.

### 24. [named-data/NLSR](https://github.com/named-data/NLSR)

**C++; Named Data Link State Routing for NDN.** NLSR populates an NDN router's RIB with multiple faces for reachable name prefixes. Study how routing changes when destinations are names and forwarding can retain multiple next hops. Its [overview](https://github.com/named-data/NLSR/blob/master/README.md) describes link-state and hyperbolic modes within an authoritative domain; broader inter-domain ambitions are not treated here as completed functionality.

- **C1:** The [link-state calculator](https://github.com/named-data/NLSR/blob/master/src/route/routing-calculator-link-state.cpp) constructs an adjacency matrix from LSAs and explicitly reconciles asymmetric costs: a broken direction invalidates the link, otherwise both directions use the larger cost. This connects inconsistent observations to a deterministic routing decision.
- **C2:** The [LSDB abstraction](https://github.com/named-data/NLSR/blob/master/src/lsdb.hpp) stores adjacency, coordinate, and name advertisements with indexes by origin/type and shared retrieval, synchronization, and notification machinery. These common representations support different routing algorithms and advertisement types without separate database implementations.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations, including: multiprotocol BGP/OSPF/IS-IS suites; Go/Rust/Python BGP implementations; official BIRD/OpenBGPD mirrors; Babel/OLSR/OONF and B.A.T.M.A.N. mesh protocols; PIM/DVMRP multicast; RPL in Contiki and RIOT; Thread/MLE routing; controller BGP-LS/PCEP; Open/R and distributed routing; SCION and named-data routing; RIFT/fat-tree routing; and less common Erlang/Haskell implementations. Follow-up queries for individual projects resolved canonical owners and source locations. Late searches added RIFT's distinct fat-tree design and prompted a targeted check of kernel-resident B.A.T.M.A.N.; beyond those, results were predominantly overlapping BGP projects, small incomplete implementations, or adjacent subjects.

Every selected repository's canonical URL was opened or checked through the GitHub API. At least one additional implementation or architecture source was read for every selection; directory listings were used to locate files, not as a substitute for substantive evidence. Current source corrected several discovery impressions, including OpenBGPD's organization redirect, ExaBGP's branch distinction, and RIOT's incomplete RPL feature coverage. No repositories were cloned, dependencies installed, candidate code executed, or external services modified.

The selection spans C, C++, Go, Rust, Java, and Python, from constrained wireless devices to inter-domain routing and controller integration. It favors distinct implementations over minor forks. FRR's Quagga ancestry does not make its independently evolved suite a duplicate, while the OpenBGPD source mirror and portability framework are intentionally counted only once. BIRD, freeRtr, OpenBGPD, and OpenDaylight have their GitHub mirror/replication relationships disclosed in their entries.

Excluded classes include OpenWrt packaging feeds, routing labs and configuration-only repositories, static multicast tools, BGP monitoring/parsing tools without a speaker, and unrelated PCB/application routing results. The Linux entry is narrowly limited to batman-adv's distributed mesh protocol; generic bridge and IP forwarding machinery is not separately counted. RIFT-Python is retained for its substantial protocol implementation and documented system/interoperability testing, with draft-version limitations; it is not presented as a current standards-compliance reference. The list is selective, not an exhaustive inventory of every historical routing daemon or experimental language implementation.

No throughput figures, conformance results, or tests were independently reproduced. Maintenance activity and documentation quality vary; particularly old architectural documents and work-in-progress branches are identified where relevant. C1 recognizes difficult correctness work, not proof that the implementation is free of bugs, and the report does not claim that every component of a selected repository is uniformly exemplary.
