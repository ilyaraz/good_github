# Wireless and low-power mesh networking stacks

Research date: **2026-10-09**

This selection covers 24 substantial GitHub repositories implementing wireless mesh protocols, constrained-device networking, or the host and routing infrastructure directly supporting those networks. It spans IEEE 802.15.4/IPv6, Bluetooth, Zigbee, LoRa, proprietary low-power radios, community Wi-Fi routing, and synchronous flooding. Linux routing engines and host-side Zigbee stacks are included with their boundaries identified; they are not all embedded, battery-powered, or complete radio-to-application stacks. Operating-system repositories are counted once, for the named networking subsystem.

The criteria below identify useful engineering study material, not certification, measured superiority, or a claim that every component is exemplary. Repository identity and status were checked through GitHub pages or the GitHub API. Each selection also has a separately inspected implementation or technical-documentation source. Links in the criteria serve as suggested reading entry points.

## Criteria legend

- **C1 — Correctness:** substantial invariants, concurrency, protocol state, adversarial input, or failure-recovery problems.
- **C2 — Abstractions:** reusable interfaces or components supporting multiple applications, protocols, platforms, or deployment styles.
- **C3 — Performance architecture:** explicit treatment of airtime, latency, energy, memory, or computation within an understandable design.
- **C4 — Sustained engineering:** evidence across years of compatibility work, testing, migrations, or deliberate complexity management. Age and recent pushes alone do not qualify.

## IPv6 and IEEE 802.15.4 mesh stacks

### [openthread/openthread](https://github.com/openthread/openthread)

**Language / role:** C and C++; Thread networking stack, including IPv6, 6LoWPAN, mesh routing, and device/platform integration.

Study how a portable protocol core expresses precise contracts to a hardware radio implementation. The separation is useful for understanding both single-chip devices and host/co-processor arrangements.

- **C1:** The radio API specifies asynchronous transmit/receive completion, errors, source-address matching, sleep transitions, and timed operations. These contracts expose the failure and ordering conditions a port must preserve. Start with the [radio-operation API](https://openthread.io/reference/group/radio-operation).
- **C2:** The platform abstraction separates timers, radio, entropy, settings, and other hardware services from Thread logic. The porting guide explains indirect-transmission support for sleepy children and persistent datasets, showing that portability includes behavioral requirements rather than function signatures alone. Read the [platform-abstraction implementation guide](https://openthread.io/guides/porting/implement-platform-abstraction-layer-apis).

### [contiki-ng/contiki-ng](https://github.com/contiki-ng/contiki-ng)

**Language / role:** C; constrained-device operating system, scoped here to its IPv6/RPL and TSCH/6TiSCH networking implementation.

The TSCH subsystem is particularly useful for studying the boundary between interrupt-level radio timing and ordinary protocol processing.

- **C1:** Slot operations defer reception and transmission-completion work through ring buffers; RPL parent/rank changes must remain consistent with TSCH time-source and joining information. The [TSCH/6TiSCH design guide](https://github.com/contiki-ng/contiki-ng/blob/develop/doc/programming/TSCH-and-6TiSCH.md) explains these cross-layer relationships.
- **C3:** The same guide describes per-neighbor queues, slotframes, adaptive clock-drift compensation, and configurable neighbor/route capacities. Timing accuracy, duty cycling, and finite RAM are visible architectural concerns.
- **C4:** The [release history](https://github.com/contiki-ng/contiki-ng/releases) documents the 2024–2026 progression through 5.0, 5.1, and 5.2, including clock-width migration guidance, added regression coverage, and security hardening. This supports sustained engineering beyond merely retaining old code.

### [RIOT-OS/RIOT](https://github.com/RIOT-OS/RIOT)

**Language / role:** C; embedded operating system, scoped to the GNRC networking stack and its IPv6/6LoWPAN composition.

Study a threaded stack whose protocol modules communicate through common interfaces, alongside the memory-ownership rules that make sharing packets practical on small systems.

- **C1:** Packet fragments have atomic reference-count operations and a write-preparation operation that copies shared data. Allocation failure and even failure-induced release are documented explicitly. The [packet-buffer API](https://api.riot-os.org/group__net__gnrc__pktbuf.html) also distinguishes static-pool behavior from the debugging-oriented malloc backend.
- **C2:** GNRC uses protocol registration, message passing, and a common network interface to compose layers and demultiplex traffic. Its documentation calls out event-loop and message-queue requirements, making the abstraction's execution model inspectable. Start with the [GNRC architecture](https://api.riot-os.org/group__net__gnrc.html).
- **C3:** The static packet pool, sharing, and copy-on-write rules provide a concrete design for controlling memory consumption without requiring every protocol layer to duplicate whole packets.

### [openwsn-berkeley/openwsn-fw](https://github.com/openwsn-berkeley/openwsn-fw)

**Language / role:** C; OpenWSN firmware implementing an IEEE 802.15.4e/6TiSCH-oriented low-power IPv6 stack.

The especially instructive part is distributed schedule negotiation: changing a radio schedule is a transaction between devices that may lose messages or lose synchronization.

- **C1:** The [6top implementation](https://raw.githubusercontent.com/openwsn-berkeley/openwsn-fw/develop/openstack/02b-MAChigh/sixtop.c) checks transaction state before requests, handles operation-specific transitions and timeouts, and explicitly transfers packet ownership. Beacon advertisement also depends on synchronization and routing readiness.
- **C2:** Scheduling-function callbacks are registered separately from the 6top transaction machinery. The [OpenStack source layout](https://github.com/openwsn-berkeley/openwsn-fw/tree/develop/openstack) separates low/high MAC, header compression, IPv6, and transport, allowing an engineer to trace how schedule policy connects to the rest of the stack.

### [SiliconLabs/wisun-br-linux](https://github.com/SiliconLabs/wisun-br-linux)

**Language / role:** C; Linux Wi-SUN border-router software with a host/radio co-processor split. The separate radio firmware is outside this repository's scope.

This is a useful comparison with MCU-resident stacks: upper-layer work runs on Linux while radio-sensitive operations cross a documented host interface.

- **C1:** The [host-interface specification](https://raw.githubusercontent.com/SiliconLabs/wisun-br-linux/main/HIF.md) defines reset/version negotiation, request/confirmation/indication messages, transmission handles, and cancellation races. A cancellation can lose a race with successful transmission; completion reporting must still be coherent.
- **C2:** The same interface separates the host stack from transport and radio execution, with explicit API negotiation rather than an assumed lockstep implementation.
- **C3:** Frequency-hopping timing and neighbor timing information cross that boundary. The specification distinguishes ordinary contention-based transmission from scheduling toward low-function nodes, exposing how sleepy devices constrain host/radio responsibilities. The repository overview explains the [border-router/co-processor arrangement](https://github.com/SiliconLabs/wisun-br-linux).

## Bluetooth mesh implementations

### [zephyrproject-rtos/zephyr](https://github.com/zephyrproject-rtos/zephyr)

**Language / role:** C; Zephyr's Bluetooth Mesh subsystem, not the entire RTOS as a separate networking entry.

Study how a standards-oriented mesh stack makes transport concurrency and memory limits configurable without hiding their consequences.

- **C1:** Segmentation/reassembly must coordinate acknowledgments, retransmissions, and concurrent messages. Messages to the same destination are serialized while other destinations can have independent transactions. The [SAR configuration documentation](https://docs.zephyrproject.org/latest/services/connectivity/bluetooth/api/mesh/sar_cfg.html) explains these restrictions.
- **C3:** Segment counts and simultaneous transmit/receive contexts are configuration choices with direct RAM and throughput implications. The same SAR documentation makes the limits visible at the transport layer.
- **C2:** The [Bluetooth Mesh API overview](https://docs.zephyrproject.org/latest/services/connectivity/bluetooth/api/mesh.html) provides entry points to provisioning, access/models, configuration, and transport services, supporting applications beyond a single demonstration device.

### [apache/mynewt-nimble](https://github.com/apache/mynewt-nimble)

**Language / role:** C; NimBLE host/controller stack with a Bluetooth Mesh implementation and operating-system portability layer.

The mesh code shares lineage with other open Bluetooth Mesh implementations; its value here is the substantial NimBLE integration and execution environment, not a claim of independently invented mesh algorithms.

- **C1:** The [mesh transport implementation](https://raw.githubusercontent.com/apache/mynewt-nimble/master/nimble/host/mesh/src/transport.c) tracks sequence authentication, segment acknowledgments, retransmission attempts, blocked senders, and receive contexts. It also handles the special rule that unicast traffic accepted for a Friend relationship must pass through the Friend queue.
- **C3:** Segment storage comes from bounded pools; exhaustion is a first-class error. Delayed work and transmission-context ordering expose how reliability competes with finite RAM and timer resources.
- **C2:** The [repository architecture overview](https://github.com/apache/mynewt-nimble) describes the host/controller split, transports, and NimBLE Porting Layer. This makes it useful for comparing the same protocol responsibilities across operating systems.

### [bluez/bluez](https://github.com/bluez/bluez)

**Language / role:** C; Linux Bluetooth stack, scoped to its mesh daemon and application-facing D-Bus interfaces.

Study the boundary between a long-lived mesh service and separately implemented applications. This is a host-side mesh architecture, distinct from an RTOS model embedded in one firmware image.

- **C1:** The [mesh API](https://github.com/bluez/bluez/blob/master/doc/mesh-api.txt) specifies asynchronous provisioning, persistent node tokens, attachment, and failure results. Applications must persist the token returned by successful joining; an error response to completion removes the newly created node. Identity and recovery therefore cross a process boundary.
- **C2:** Applications expose object-manager, application, element, and provisioning-agent interfaces. The daemon centralizes mesh networking while models and application behavior remain separately implementable. Follow the same API from `Join` through `Attach` to see the lifecycle contract.

### [bluerange-io/bluerange-mesh](https://github.com/bluerange-io/bluerange-mesh)

**Language / role:** C and C++; BlueRange Mesh, formerly FruityMesh. It uses a custom connection-based BLE mesh, not the Bluetooth SIG Mesh protocol.

This implementation provides a useful alternative to managed flooding, particularly for studying queueing and time synchronization over connected BLE links.

- **C1:** Its synchronization exchange measures local send delay and applies a correction rather than assuming symmetric round-trip delay. Generation tracking also addresses time moving backward. The [implementation details](https://bluerange.io/docs/bluerange-mesh-community/ImplementationDetails.html) explain the resulting multi-hop timing problem.
- **C3:** Priority queues, weighted service, reserved buffer chunks, and rules for completing split messages make quality-of-service tradeoffs concrete. The documentation also acknowledges the exceptional treatment of vital traffic, so this is not evidence of unconditional fairness.
- **C2:** Modules, persistent configuration, board configuration, and build feature sets separate product behavior from common networking machinery. See the [developer architecture guide](https://bluerange.io/docs/bluerange-mesh-community/Developers.html).

### [drogue-iot/btmesh](https://github.com/drogue-iot/btmesh)

**Language / role:** Rust; embedded Bluetooth Mesh implementation using asynchronous execution and `no_std` components. Treat it as an experimental implementation: the repository describes hardware limitations and unfinished generic-HCI support; the checked metadata's last push was in January 2025.

Study the type and execution boundaries between protocol state, storage, randomness, and radio/network interfaces.

- **C1:** The [driver implementation](https://raw.githubusercontent.com/drogue-iot/btmesh/main/btmesh-driver/src/lib.rs) handles provisioning transitions, asynchronous configuration storage, state-dependent PDU processing, acknowledgments, and relay decisions. These are concrete distributed-state problems rather than benefits inferred solely from the language.
- **C2:** The driver is parameterized over network interfaces, cryptographic randomness, and backing storage. The [stack-state module](https://raw.githubusercontent.com/drogue-iot/btmesh/main/btmesh-driver/src/stack/mod.rs) distinguishes unprovisioned and provisioned states and their timer/retransmission behavior. Together these are useful examples of an embedded asynchronous protocol design; no qualification or production-readiness claim is implied.

## Zigbee host stacks and coordinator infrastructure

### [zigpy/zigpy](https://github.com/zigpy/zigpy)

**Language / role:** Python; reusable Zigbee application/controller stack. Radio adapters normally provide lower layers; this is not an independent complete on-radio Zigbee implementation.

The central study opportunity is coordinating unreliable, asynchronous device and radio behavior behind a stable application model.

- **C1:** The [controller application implementation](https://raw.githubusercontent.com/zigpy/zigpy/dev/zigpy/application.py) maintains device-scoped request listeners and retained asynchronous tasks. Startup connects and initializes the controller, with shutdown and error translation when initialization fails.
- **C2:** The same class separates abstract radio operations from shared application behavior, backup/topology handling, and device coordination. Alongside the [repository's ZCL/ZDO and radio-library overview](https://github.com/zigpy/zigpy), this provides a useful route through backend-independent Zigbee control.
- **C3:** Controller request limiting and priority-aware execution make constrained-radio capacity part of the host architecture, rather than allowing arbitrary application concurrency to overwhelm it.

### [Koenkk/zigbee-herdsman](https://github.com/Koenkk/zigbee-herdsman)

**Language / role:** TypeScript; Node.js Zigbee controller stack used by applications including Zigbee2MQTT. It evolved substantially from zigbee-shepherd; it is not listed as a separate thin fork or as a replacement for every radio-resident layer.

Study how a common adapter surface accommodates different coordinator command protocols while retaining backend-specific recovery logic.

- **C2:** The [adapter abstraction](https://raw.githubusercontent.com/Koenkk/zigbee-herdsman/master/src/adapter/adapter.ts) defines typed events and operations across several radio backends. Device joining, ZDO/ZCL traffic, and controller operations have shared representations.
- **C1:** The [Z-Stack adapter](https://raw.githubusercontent.com/Koenkk/zigbee-herdsman/master/src/adapter/z-stack/adapter/zStackAdapter.ts) correlates responses using addresses, endpoints, clusters, and transaction information. Keyed queues, route discovery, and bounded recovery paths illustrate the difficult behavior beneath the common interface when radio state and host expectations diverge.

### [zigpy/ziggurat](https://github.com/zigpy/ziggurat)

**Language / role:** Rust; host-side Zigbee NWK/APS implementation using an OpenThread radio co-processor. **Early alpha**, as the repository explicitly states.

Unlike controller libraries that delegate most networking to a coordinator's firmware, this project puts routing and other network-stack responsibilities on the host. It is useful for studying that alternative boundary, with maturity limitations kept explicit.

- **C1:** The [NWK routing implementation](https://raw.githubusercontent.com/zigpy/ziggurat/dev/crates/ziggurat-zigbee/src/nwk/routing.rs) distinguishes active, discovery, failed, and inactive routes; compares path costs before replacing active routes; and tracks expiration and separate routing identifiers. These are inspectable invariants for handling changing mesh paths.
- **C2:** Route results represent next-hop and source-routed forwarding separately, while route-reply handling returns explicit dispositions. This separation makes routing decisions inspectable apart from radio I/O. Read it alongside the [repository's host/RCP architecture](https://github.com/zigpy/ziggurat). C4 is deliberately not claimed for this young implementation.

## LoRa and other constrained-radio meshes

### [meshtastic/firmware](https://github.com/meshtastic/firmware)

**Language / role:** C++; embedded LoRa mesh firmware spanning multiple device platforms.

Study the interaction between managed flooding, learned next hops, duplicate suppression, and scarce shared airtime. The distinction between an overheard relay and end-to-end receipt is especially important.

- **C1:** The [mesh algorithm documentation](https://meshtastic.org/docs/overview/mesh-algo/) explains hop limits, duplicate handling, acknowledgment semantics, and fallback from learned next-hop transmission to flooding. It also discusses asymmetric links and older firmware, exposing failure cases that a simple flooding sketch misses.
- **C3:** Channel-activity detection, contention timing, suppression of redundant forwarding, and adaptive ancillary traffic address radio occupancy. The layered explanation connects these mechanisms to routing and application packets rather than presenting isolated radio tweaks.

### [meshcore-dev/MeshCore](https://github.com/meshcore-dev/MeshCore)

**Language / role:** C++; portable radio-mesh library and firmware family with distinct client, repeater, and room-server roles.

Study the division between reusable packet machinery and policies about forwarding, path use, and application delivery.

- **C1:** The [mesh interface](https://raw.githubusercontent.com/meshcore-dev/MeshCore/main/src/Mesh.h) distinguishes forwarding deduplication from application reception, whose callbacks may still receive duplicates. It exposes forwarding decisions and retransmission-delay hooks explicitly.
- **C2:** `Mesh` builds on a dispatcher and accepts separate time, randomness, and packet-history services; `MeshTables` abstracts duplicate tracking. This makes policy substitution and platform integration visible in a relatively compact core.
- **C3:** The [project FAQ](https://github.com/meshcore-dev/MeshCore/blob/main/docs/faq.md) describes the role split and discovery of paths by flooding, followed by path-directed traffic. Its recovery description includes application behavior, so it should not be read as a guarantee supplied by every library integration.

### [LoRaMesher/LoRaMesher](https://github.com/LoRaMesher/LoRaMesher)

**Language / role:** C++; LoRa mesh library using FreeRTOS and RadioLib. The inspected main branch documents a substantial protocol rewrite; evaluate that branch's implementation status separately from older LoRaMesher descriptions.

The useful material is the combination of distance-vector routing with scheduled radio access, and the way the design makes feedback and timing hazards explicit.

- **C1:** The [protocol specification](https://github.com/LoRaMesher/LoRaMesher/blob/main/PROTOCOL_SPEC.md) explains receiver-side split horizon for broadcast route advertisements, route aging/poisoning, and the separation of raw link measurements from accumulated path metrics. These address routing loops and self-reinforcing metric errors.
- **C2:** Message, routing, network, synchronization, and radio services have distinct responsibilities, making it possible to study routing policy separately from radio mechanics.
- **C3:** The same document describes slot scheduling, joining jitter, and timing guards. Read its implementation/planning qualifications together with the [repository overview](https://github.com/LoRaMesher/LoRaMesher); a specified mechanism is not by itself evidence that every listed feature is complete or field-validated.

### [markqvist/Reticulum](https://github.com/markqvist/Reticulum)

**Language / role:** Python; non-IP networking stack that can span LoRa, packet-radio, and other interfaces. It is included for constrained-link mesh transport, not as a tiny-MCU firmware stack.

Study how identities, destinations, links, and transported resources can remain independent of the underlying radio or conventional IP addressing.

- **C1:** The [network architecture manual](https://markqvist.github.io/Reticulum/manual/understanding.html) describes proof-based link establishment and expiry of unconfirmed state. Signed announcements and forwarding-state lifecycles expose concrete authenticity and resource-retention problems; their presence is not an independent security audit.
- **C2:** Destination, packet, link, and resource abstractions support applications across heterogeneous interfaces without requiring each application to implement radio-specific transport behavior.
- **C3:** Announcement queues, interface bandwidth allowances, and hop-aware prioritization bound control traffic on slow links. These mechanisms are explained in the same architecture manual, making bandwidth management part of the forwarding design.

### [nRF24/RF24Mesh](https://github.com/nRF24/RF24Mesh)

**Language / role:** C++; dynamic-address and topology-management layer over RF24Network for low-cost radios. RF24Network is a dependency, not a second counted selection here.

Study the separation of stable node identity from a changing tree/network address, and the compatibility work needed when broadening a small embedded library's radio support.

- **C1:** The [public mesh API](https://raw.githubusercontent.com/nRF24/RF24Mesh/master/RF24Mesh.h) exposes address renewal after connectivity loss, master-side address management, and update/service obligations. Applications must distinguish an identity from its current assigned address.
- **C2:** Templated radio/network types allow the same mesh layer to sit above different compatible radio implementations, while compatibility aliases preserve familiar APIs.
- **C4:** The [release history](https://github.com/nRF24/RF24Mesh/releases) records template-related evolution and parallel fixes in the 1.x and 2.x lines during 2024–2025, followed by rollover/allocation-related fixes in 2026. This is concrete evidence of compatibility and failure-mode maintenance across years.

## Community wireless routing and bridging

### [jech/babeld](https://github.com/jech/babeld)

**Language / role:** C; Babel routing daemon for mixed wired and wireless networks, including ad-hoc meshes. It is a routing control plane, not a radio driver or low-power MAC.

Study how loop avoidance, route withdrawal, kernel-route installation, and metric smoothing interact in a comparatively focused implementation.

- **C1:** The [route implementation](https://raw.githubusercontent.com/jech/babeld/master/route.c) encodes feasibility using sequence numbers and metrics. Its withdrawal logic explicitly avoids treating removal of a route as a trivial kernel-table deletion, because that can affect loop avoidance.
- **C3:** Prefix-indexed route organization and smoothed metrics address lookup work and route oscillation while keeping the decision process inspectable.
- **C4:** The [change history](https://raw.githubusercontent.com/jech/babeld/master/CHANGES) documents years of interoperability and compatibility work, including older-protocol compatibility, authentication/power-saving fixes, route-redistribution changes, and later regression tests. The history itself cautions that detecting behavior changes is not a proof of correctness.

### [OLSR/OONF](https://github.com/OLSR/OONF)

**Language / role:** C; modular networking framework containing OLSRv2, NHDP neighbor discovery, and related services for mobile/ad-hoc networks.

This entry is distinct from the older OLSRv1 daemon below. Study the reusable MANET packet machinery and how it supports multiple routing and discovery components.

- **C2:** The [RFC 5444 writer design](https://raw.githubusercontent.com/OLSR/OONF/master/docs/rfc5444/rfc5444_writer.txt) separates message ownership from prioritized content providers. Protocol components can contribute information through callbacks instead of each owning a complete packet encoder.
- **C3:** Compressed message generation can be shared across interfaces, with per-interface packet limits and network-wide message constraints. Encoding cost and MTU handling are explicit design inputs.
- **C1:** The [multithreading contract](https://raw.githubusercontent.com/OLSR/OONF/master/docs/rfc5444/rfc5444_multithreading.txt) distinguishes independent contexts from concurrent use of one context, which requires synchronization. The writer also restricts changes to callback registrations during callbacks, exposing its mutation invariants.

### [OLSR/olsrd](https://github.com/OLSR/olsrd)

**Language / role:** C; OLSRv1 routing daemon and extensions for wireless mesh routing.

Study the operational consequences of routing metrics and gateway selection. Its design documentation is particularly candid about interactions that can damage session stability or even introduce loops.

- **C1:** The [OLSR extensions document](https://github.com/OLSR/olsrd/blob/master/README-Olsr-Extensions) discusses gateway hysteresis intended to avoid breaking NAT sessions, and problematic interactions between gateway thresholds and limited-scope topology propagation. This is evidence of difficult correctness tradeoffs, not a claim that all combinations are safe.
- **C2:** Link-quality plugins and gateway mechanisms separate routing policy from the daemon's common processing.
- **C3:** The same document contrasts floating-point and fixed-point link-quality processing and describes reduced-scope topology dissemination. It is a historical design document: use it to understand mechanisms and tradeoffs, then check the relevant implementation/configuration before assuming its examples describe current defaults.

### [open-mesh-mirror/batman-adv](https://github.com/open-mesh-mirror/batman-adv)

**Language / role:** C; Linux kernel layer-2 mesh routing/bridging. **Project GitHub mirror:** the [hosting organization](https://github.com/open-mesh-mirror) identifies itself as the mirror of open-mesh.org Git repositories, and the repository identifies its upstream there. This is a substantive source mirror, not an independent fork.

Study the added complexity of making a multi-hop wireless network appear as a virtual Ethernet switch, particularly when it meets ordinary bridged networks.

- **C1:** The [bridge-loop-avoidance implementation](https://raw.githubusercontent.com/open-mesh-mirror/batman-adv/main/net/batman-adv/bridge_loop_avoidance.c) manages MAC/VLAN claims and backbone gateways using RCU, reference counts, locks, and deferred freeing. Distributed ownership and kernel object lifetime must both remain correct.
- **C2:** The virtual layer-2 interface allows higher protocols to operate over the mesh while underlying Ethernet-like interfaces can vary; the repository overview explains that boundary.
- **C4:** The [changelog](https://raw.githubusercontent.com/open-mesh-mirror/batman-adv/main/CHANGELOG.rst) records successive kernel-compatibility updates and fixes to races and lifetime handling across releases. It provides concrete evidence of ongoing complexity management across years, rather than relying on the age of B.A.T.M.A.N.

## Synchronous flooding and research middleware

### [ETHZ-TEC/Baloo](https://github.com/ETHZ-TEC/Baloo)

**Language / role:** C; research middleware for constructing low-power wireless protocols from synchronous-transmission primitives, built on a modified Contiki-NG base. **Historical research artifact:** the checked repository metadata showed its last push in 2020; it is not presented as a currently maintained production stack.

The distinct contribution is its Generic Middleware layer and round/callback execution model, rather than the inherited operating-system code.

- **C1:** The [program-flow documentation](https://raw.githubusercontent.com/wiki/ETHZ-TEC/Baloo/Baloo-program-flow.md) separates bootstrap and running states, validates control information, and defines when control changes and application callbacks take effect. Network rounds must preserve precise ordering despite application-level customization.
- **C2:** A fixed middleware process drives replaceable network-layer callbacks and synchronous-transmission primitives. The same guide shows how applications attach to pre/post-round and slot events.
- **C3:** Application processing is coordinated around radio rounds, exposing how timing-critical communication can coexist with cooperative application execution. This is useful research architecture, with hardware and artifact-age limitations kept explicit.

### [open-sf/osf](https://github.com/open-sf/osf)

**Language / role:** C; Open-SF research stack for multi-PHY synchronous flooding. It derives from Contiki-NG and BlueFlood but adds a substantially different interrupt-driven radio implementation and protocol framework. The documented mainline hardware scope is nRF52840; IPv6 work is described separately from the main stack.

Study how changing physical-layer modes interacts with network-wide communication rounds and tightly controlled radio timing.

- **C2:** The [protocol definitions](https://raw.githubusercontent.com/open-sf/osf/main/os/net/mac/osf/osf-proto.h) separate round types, PHY patterns, and configurable retransmission/slot parameters. Together with the extension system described in the repository, these support more than a single flooding experiment.
- **C3:** The [architecture overview](https://github.com/open-sf/osf) explains replacement of polling with an interrupt-driven radio driver for finer timer/state-machine control and describes testbed-oriented benchmarking support. The protocol header also places explicit bounds on round schedules. These are inspectable architecture choices; no comparative speed or energy claim is inferred without reproducing experiments.

## Search coverage, exclusions, and limits

Discovery used more than six distinct live-search formulations, including Thread/6LoWPAN/RPL; TSCH/6TiSCH and OpenWSN; Bluetooth Mesh across Zephyr, NimBLE, BlueZ, and Rust; Wi-SUN and host/radio splits; LoRa managed flooding and distance-vector meshes; RF24 and connection-based BLE; host-side Zigbee in Python, TypeScript, and Rust; Babel/OLSR/B.A.T.M.A.N. community routing; and Glossy-style synchronous flooding, Baloo, and Open-SF. Broader searches also checked DASH7 and ESP mesh frameworks. Later queries mostly returned already encountered stacks, application clients, SDK integrations, and mirrors, with synchronous flooding providing the final distinct architecture family.

Canonical GitHub identity was checked for every retained repository by opening its page or reading its API metadata. The technical links above were opened/read as separate evidence; search snippets alone were not used to qualify entries. Some GitHub file pages failed to render through the browser, so their exact source files were read from GitHub's raw-content service. No candidate code was installed, built, or executed.

Scope and exclusion decisions:

- LoRaWAN end-device stacks and other primarily star-network systems were not treated as meshes merely because they use low-power radios. VPN overlays, mesh dashboards, mobile clients, tutorial repositories, and simulation-only projects were outside the selected scope.
- The old painlessMesh GitHub mirror, unofficial RadioHead copies, and a ZBOSS backup mirror were not retained because a current, authoritative, substantive GitHub implementation was not established. The archived ESP-MDF framework was omitted in favor of directly inspectable protocol engines and more distinct architectures.
- TinyOS's archived `tinyos-main` tree contains valuable collection-protocol material, but its migration notice points to other development trees. Those archives were not promoted to a current canonical selection; resolving the successor lineage fully was outside this report's final selection.
- Monorepos are counted once. NimBLE's shared mesh lineage is acknowledged, while Baloo and Open-SF are retained for their substantial middleware/radio work rather than counted as additional generic Contiki-NG copies. RF24Network and application-layer companion repositories are not separately counted.
- Repository metadata was checked, but an unarchived repository or recent push is not taken as proof of ongoing support. Baloo's historical status, btmesh's experimental scope, Ziggurat's early-alpha status, LoRaMesher's evolving rewrite, and the B.A.T.M.A.N. mirror are called out individually. The open-mesh.org website presented an anti-bot barrier; mirror attribution rests on the project's GitHub organization and repository metadata.

The judgments that these designs satisfy C1–C4 are grounded engineering inferences from the cited code and documentation. They do not establish uniform code quality, protocol conformance, security assurance, hardware availability, or measured performance. Documentation and default-branch source can change after the research date, and vendor-supplied radio firmware remains outside several host-stack repositories.
