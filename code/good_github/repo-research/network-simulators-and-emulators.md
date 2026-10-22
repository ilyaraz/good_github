# Network simulators and emulators

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories for packet and flow simulation, execution of real applications in modeled networks, virtual network laboratories, radio and mobility simulation, and controlled network impairment. It includes one interconnection-network simulator and two explicitly scoped operating-system subsystems. General distributed-system simulators qualify here only where their network modeling is substantial. The criteria below are engineering-study judgments grounded in the linked implementation and documentation, not a claim that every model is accurate for every experiment.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions serving multiple use cases. **C3** — concrete performance constraints addressed through understandable architecture. **C4** — sustained evolution accompanied by compatibility work, testing, or complexity management.

## Simulation engines and general network models

### 1. [nsnam/ns-3-dev-git](https://github.com/nsnam/ns-3-dev-git)

**Language/role:** C++, with Python bindings; discrete-event packet-network simulator. **Repository status:** official read-only GitHub mirror; development and issue handling are on the project's GitLab repository.

Study how a simulation engine separates event scheduling, simulation time, node context, and technology-specific model libraries. Its event API makes several easily overlooked semantic choices explicit.

- **C1:** Equal-time events execute in insertion order; cancellation differs from removal; integer time resolution trades precision against representable duration. Correct node context must also follow a packet to its receiving node. These are documented simulation invariants, not merely implementation details. [Events and simulator manual](https://www.nsnam.org/docs/manual/html/events.html).
- **C2/C3:** Interchangeable scheduler structures, simulator implementations, and adapters accommodate sequential, distributed, and real-time operation. The manual explains the memory/work tradeoff of cancellation and why scheduler choice depends on event distributions. [Same architectural entry point](https://www.nsnam.org/docs/manual/html/events.html).
- **C4:** The release history records model corrections and platform compatibility across many generations, including Python 2 retirement in 3.30 and Python 3.14 build fixes in 3.46.1. [Release notes](https://github.com/nsnam/ns-3-dev-git/blob/master/RELEASE_NOTES.md).

### 2. [omnetpp/omnetpp](https://github.com/omnetpp/omnetpp)

**Language/role:** C++ simulation kernel and Java IDE; component-oriented discrete-event framework used to build network simulators.

Study the infrastructure beneath model suites such as INET: messages, modules, channels, queues, introspection, and statistics share a coherent object system.

- **C1:** Its ownership tree tracks a message as it moves from a module to the future-event set and then to its destination. Ownership checks catch sending queued objects, rescheduling already scheduled messages, and reusing one message in incompatible places.
- **C2:** The object and container contracts include duplication, child traversal, naming, and runtime inspection, letting independently written models participate in common debugging and simulation facilities.
- **C3:** The manual explains costs rather than treating abstraction as free: the base object has no data members, small value types need not inherit from it, and reference-counted name pooling reduces repeated allocation.

Entry point for these claims: [simulation library manual source, especially object ownership and class extension](https://github.com/omnetpp/omnetpp/blob/master/doc/src/manual/ch-sim-lib.tex). OMNeT++ supplies the framework; individual network protocols generally live in separate model repositories.

### 3. [inet-framework/inet](https://github.com/inet-framework/inet)

**Language/role:** C++ and NED; wired, wireless, transport, and application models for OMNeT++.

Study the reusable packet representation underneath a large protocol suite. It must support both abstract field access and serialization without forcing every protocol to manage byte buffers directly.

- **C1:** Packets retain immutable chunks, distinguish front-popped, active, and back-popped regions, and constrain region-tag overlap. These contracts matter when several protocol layers inspect, fragment, aggregate, and reinterpret the same data.
- **C2/C3:** The same packet API supports field-based and byte-based representations, metadata, encapsulation, and fragmentation. Duplicated packets share chunks; popping headers normally moves iterators instead of copying payloads.

Entry points: [Packet.h and its representation contract](https://github.com/inet-framework/inet/blob/master/src/inet/common/packet/Packet.h), [packet developer guide](https://inet.omnetpp.org/docs/developers-guide/ch-packets.html). The repository itself cautions that protocol-model validity must be checked for the intended experiment.

### 4. [shadow/shadow](https://github.com/shadow/shadow)

**Language/role:** Rust and C; network simulation that directly executes Linux application processes.

Study the boundary between a real process and a simulated kernel. Shadow combines a discrete-event network with unmodified application binaries rather than requiring each application to be rewritten as a simulator model.

- **C1:** A preloaded shim and seccomp interception redirect system calls into modeled time, descriptors, signals, TCP/UDP, and routing. Seeded randomness includes intercepted random-byte sources, making determinism a system-wide concern.
- **C2:** The syscall boundary provides a reusable integration mechanism for different network applications and experiment topologies.
- **C3:** Hot time-related calls can be handled in the shim; shared memory reduces interprocess copying; scheduling limits runnable work to available cores and uses work stealing and CPU affinity.

Entry point: [Shadow 2 design overview](https://github.com/shadow/shadow/blob/main/docs/design_2x.md). These are documented architectural mechanisms, not independently reproduced throughput claims.

### 5. [simgrid/simgrid](https://github.com/simgrid/simgrid)

**Language/role:** C++ core with multiple APIs; distributed-application simulator with substantial network-performance models. **Repository status:** official GitHub mirror; most development occurs on FramaGit.

The relevant subsystem is network resource modeling and routing, particularly the alternative to simulating every packet. Study how application communications become competing resource-consumption actions.

- **C1:** A linear max-min solver enforces capacity constraints and updates remaining work as competing activities start and finish. TCP models additionally account for window limits, RTT-dependent sharing, and reverse-direction traffic.
- **C2/C3:** Selectable analytical models and an ns-3 integration expose different fidelity/cost tradeoffs. Flow models recompute rates at communication events; the packet backend processes packet events. Network zones and routing models compose larger platforms.

Entry point: [model architecture, equations, validation references, and ns-3 integration limits](https://simgrid.org/doc/latest/Models.html). Calibration is part of the model contract; a flow-level result should not be interpreted as packet-level behavior.

## Virtual network laboratories and real-stack emulation

### 6. [mininet/mininet](https://github.com/mininet/mininet)

**Language/role:** Python with a C namespace helper; emulation of hosts, switches, and links using real Linux networking.

Study a compact topology API that connects real processes through virtual interfaces. The useful abstraction boundary is particularly visible in link configuration.

- **C2:** Nodes execute commands, interfaces configure themselves, and links connect nodes. Separate interface and link subclasses cover veth pairs, Open vSwitch patch links, and traffic-controlled links.
- **C1:** Traffic shaping must compose qdisc hierarchies, validate loss and bandwidth parameters, and handle checksum-offload behavior. `TCULink` documents a concrete failure mode in which offload settings can produce invalid TCP checksums with a userspace switch.
- **C3:** Interface discovery combines address queries to reduce subprocess overhead, while specialized links avoid unnecessary interface operations.

Entry point: [mininet/link.py](https://github.com/mininet/mininet/blob/master/mininet/link.py). This is an established codebase; the [API snapshot](https://api.github.com/repos/mininet/mininet) showed its last push in July 2024, so inclusion does not imply a current release cadence.

### 7. [coreemu/core](https://github.com/coreemu/core)

**Language/role:** Python with native namespace support; Common Open Research Emulator.

Study session orchestration across virtual nodes, services, control networks, mobility, and external radio emulation. CORE's own network emulation and EMANE's radio modeling have a clearly documented integration boundary.

- **C1:** Sessions carry lifecycle states and hooks, protect node collections with a lock, and coordinate shutdown and resource cleanup. The state and object lifecycle are substantive correctness work when a running topology changes. [Session implementation](https://github.com/coreemu/core/blob/master/daemon/core/emulator/session.py).
- **C2:** Node-type registration and separate mobility, service, link, and distributed controllers allow different experiments to share the session engine. EMANE adapters map model configuration into XML and connect radio instances to namespace nodes through TAP devices. [EMANE integration architecture](https://github.com/coreemu/core/blob/master/docs/emane.md).

### 8. [GNS3/gns3-server](https://github.com/GNS3/gns3-server)

**Language/role:** Python; controller and compute backend for a network-emulation laboratory.

Study orchestration of heterogeneous emulators across local and remote compute services. The selected repository contains the backend, rather than counting the GUI and appliance catalog as additional simulators.

- **C2:** The controller owns project state, while compute services launch node emulators such as QEMU and Dynamips. HTTP/JSON APIs and notification streams expose this separation to different clients.
- **C1:** Node operations must serialize while independent nodes can proceed concurrently. The architecture explicitly describes internal per-node locking, a single-controller expectation, and conflict responses.

Entry point: [GNS3 architecture and concurrency contract](https://docs.gns3.com/docs/using-gns3/design/architecture). GNS3 coordinates emulation; fidelity of a specific router or appliance also depends on the selected emulator and image.

### 9. [srl-labs/containerlab](https://github.com/srl-labs/containerlab)

**Language/role:** Go; topology orchestration and wiring for container-based network laboratories.

Study the control plane that turns a declarative network into running devices, interfaces, and links. This qualifies as emulation infrastructure: the connected network operating systems and Linux containers carry real traffic.

- **C1:** Deployment distinguishes a new lab from reconciliation of an existing one, rejects incompatible option combinations, aggregates node failures, and gives cancellation precedence before post-deployment work. Link stitching waits for node workers and required endpoints.
- **C2:** Node, link, runtime, and management-network abstractions separate vendor-specific behavior from topology deployment.
- **C3:** Bounded worker concurrency and staged synchronization address deployment scale without allowing dependent interface operations to race ahead.

Entry point: [core/deploy.go](https://github.com/srl-labs/containerlab/blob/main/core/deploy.go). The file exposes both the concurrency strategy and its ordering constraints.

### 10. [KatharaFramework/Kathara](https://github.com/KatharaFramework/Kathara)

**Language/role:** Python; container-based network emulator with Docker and Kubernetes backends.

Study how a reusable scenario model is separated from the chosen execution backend. Devices connect through modeled collision domains, while lab files and startup configuration form a reproducible scenario.

- **C2:** A manager facade delegates to a selected backend; `Lab`, `Machine`, and `Link` objects support programmatic use as well as filesystem-defined scenarios. [Manager facade](https://github.com/KatharaFramework/Kathara/blob/main/src/Kathara/manager/Kathara.py).
- **C1:** Scenario operations distinguish missing devices, duplicate objects, already occupied interface numbers, and invalid collision-domain attachment. This is graph and resource-identity correctness that must remain consistent as scenarios are edited. [Lab model and connection API](https://github.com/KatharaFramework/Kathara/blob/main/src/Kathara/model/Lab.py).

### 11. [imunes/imunes](https://github.com/imunes/imunes)

**Language/role:** Tcl/Tk with native support; graphical and batch network emulation on FreeBSD and Linux.

Study an architecture in which Tcl manages an experiment and the operating system executes the emulated network. Its backend split offers a useful contrast with Python-based laboratory frameworks.

- **C2:** Runtime procedures dispatch through node-specific hooks and separate operating-system implementations, allowing one topology-management layer to coordinate different node types and platforms. [Runtime source tree](https://github.com/imunes/imunes/tree/master/runtime).
- **C1:** Deployment computes which nodes, interfaces, and links need creation or configuration, checks prerequisites, and splits asynchronous operations from their completion waits. It must also maintain running configuration and experiment identity across topology edits. [Deployment state and staged execution](https://github.com/imunes/imunes/blob/master/runtime/execute.tcl).

This is a study of a substantial evolving orchestration system, not an endorsement of every procedure's complexity or error handling.

### 12. [intrig-unicamp/mininet-wifi](https://github.com/intrig-unicamp/mininet-wifi)

**Language/role:** Python with Linux wireless integration; Wi-Fi and software-defined wireless-network emulation. **Lineage:** explicitly a Mininet fork, retained because its mobility, association, and wireless-medium integration constitute substantial separate implementation.

Study the translation from moving stations to changes in a real wireless stack and a modeled radio medium.

- **C1:** Mobility updates must keep access-point range sets, associated-station lists, RSSI, disconnects, and authentication-process state consistent. The source distinguishes SNR and interference modes and handles movement out of an access point's range.
- **C2:** A reusable mobility layer coordinates station/access-point objects, association-control policies, and the wmediumd connector, supporting mobile experiments beyond static Mininet links.

Entry point: [mn_wifi/mobility.py](https://github.com/intrig-unicamp/mininet-wifi/blob/master/mn_wifi/mobility.py). Its inheritance from Mininet is part of the selection, not a second claim of independent origin.

## Radio, cellular, vehicular, and sensor networks

### 13. [adjacentlink/emane](https://github.com/adjacentlink/emane)

**Language/role:** C++; distributed, real-time wireless-network emulation framework.

Study a common physical layer that allows different radio models to share an emulated electromagnetic environment. EMANE is independently useful and also integrates with CORE.

- **C1:** Receive decisions combine transmitter power, antenna gains, path loss, sensitivity, and interfering transmissions. Common physical-layer headers encode timing, frequency segments, and antenna information so heterogeneous transmissions can affect each other.
- **C2:** Radio models share the physical layer and exchange events and control messages; propagation can derive from locations or externally supplied path-loss events. Legacy and MIMO API modes coexist with documented over-the-air compatibility.

Entry point: [physical-layer architecture and calculations](https://emane.io/physical-layer). The compatibility modes are concrete evidence of managing model interfaces; no blanket claim of radio accuracy is made here.

### 14. [sommer/veins](https://github.com/sommer/veins)

**Language/role:** C++ and NED, with Python launch tooling; vehicular-network simulation coupled to SUMO road traffic.

Study a co-simulation where network behavior and vehicle movement influence one another, rather than a network replay over a fixed mobility trace.

- **C1:** The TraCI scenario manager subscribes to vehicle creation and movement, creates matching OMNeT++ nodes, and advances SUMO at configured intervals. Node lifecycle and the ordering of mobility updates therefore affect network results.
- **C2:** Mobility, application interaction, physical-layer effects, and vehicular MAC models are separate modules. Applications can issue traffic-control commands through a shared TraCI interface.
- **C3:** Region-of-interest filtering limits participating vehicles, while physical-layer short-circuit evaluation avoids unnecessary loss-model work.

Entry point: [module architecture, TraCI integration, and physical-layer optimization](https://veins.car2x.org/documentation/modules/). The selection relies on the mechanisms described there, not the page's numerical speedup claim.

### 15. [Unipisa/Simu5G](https://github.com/Unipisa/Simu5G)

**Language/role:** C++ and NED; LTE and 5G NR models built on OMNeT++ and INET.

Study cellular user-plane composition and the evolution of bearer, QoS, session, and tunnel abstractions. The changelog is unusually useful architectural reading because it explains model boundaries and migrations.

- **C1:** Session types constrain valid combinations of radio stacks, anchors, bearers, and tunnels. The documented implementation rejects incompatible configurations and distinguishes IP, Ethernet, and unstructured payload paths; it explicitly limits a UE to one session.
- **C2:** Central configuration, per-node control entry points, and reusable protocol-layer modules coordinate bearers, classification, and GTP-U state across different deployment scenarios.
- **C4:** Dated releases from 2021 through 2026 record tested OMNeT++/INET combinations, platform changes, and refactoring. The installation guide documents both fingerprint and unit-test workflows.

Entry points: [architectural changes and compatibility history](https://github.com/Unipisa/Simu5G/blob/master/WHATSNEW.md), [build modes and test workflows](https://github.com/Unipisa/Simu5G/blob/master/INSTALL.md).

### 16. [contiki-ng/cooja](https://github.com/contiki-ng/cooja)

**Language/role:** Java with native-firmware integration; sensor-network simulator, including MSPSim instruction-level emulation in this repository.

Study the interface between an event-driven network simulator, heterogeneous mote implementations, and an interactive GUI. MSPSim is included here rather than counted as a second repository.

- **C1:** The simulation thread consumes a command queue alongside simulation events and asserts that event time never moves backward. Configuration loading also waits for simulation-thread work before resolving mote references. [Simulation.java](https://github.com/contiki-ng/cooja/blob/master/java/org/contikios/cooja/Simulation.java).
- **C2:** The `Mote` interface separates memory, hardware interfaces, type, simulation membership, configuration persistence, and addition/removal hooks. Different mote implementations can participate in the same network simulation. [Mote.java](https://github.com/contiki-ng/cooja/blob/master/java/org/contikios/cooja/Mote.java).

The configuration API explicitly separates saved configuration from live state; reloading a scenario restarts its nodes.

## Focused packet, congestion, and interconnection simulators

### 17. [Broadcom/csg-htsim](https://github.com/Broadcom/csg-htsim)

**Language/role:** C++; packet-level discrete-event simulation for congestion-control and datacenter-network research.

Study how a comparatively compact simulator represents transport packets and switch paths without implementing a complete operating-system network stack. This repository documents its lineage through TCP, multipath transport, NDP, and EQDS research.

- **C1:** Packet code enforces invariants such as freezing global packet size after first use, legal transitions between upward and downward routing, and reference-count checks when recycling packets.
- **C2/C3:** `Packet`, `PacketFlow`, `PacketSink`, and route abstractions support multiple transport models. A typed packet pool reuses objects through a free list rather than allocating a new object for every packet.

Entry point: [sim/network.h](https://github.com/Broadcom/csg-htsim/blob/master/sim/network.h). The architectural performance evidence is object reuse; the README's comparative speed claim was not independently benchmarked. Related htsim research forks are not separately counted.

### 18. [TL-System/ns.py](https://github.com/TL-System/ns.py)

**Language/role:** Python and SimPy; composable packet, queueing, scheduling, and congestion-control models.

Study an accessible model library whose explicit semantic contracts make it more than a collection of simulator examples. Components connect through packet inputs and outputs rather than requiring a large common inheritance hierarchy.

- **C1:** Model notes define byte/rate/time units, exact-fit buffer admission, ownership during downstream retention, equal-time event ordering, retransmission accounting, and differences between physical arrivals and unique delivered bytes.
- **C2:** Sources, ports, wires, sinks, shapers, and several scheduling disciplines can be composed into different experiments; callback-based release connects bounded-buffer stages.

Entry point: [model notes and documented boundaries](https://github.com/TL-System/ns.py/blob/main/docs/model_notes.md). The document explicitly describes simplified transport and scheduling behavior. Its educational BBR model, for example, is not a claim of Linux BBRv3 equivalence.

### 19. [akeranen/the-one](https://github.com/akeranen/the-one)

**Language/role:** Java; Opportunistic Network Environment for mobility and delay-tolerant message routing.

Study store-carry-forward networking, where intermittent contacts and finite message buffers replace the assumption of a continuously available end-to-end path.

- **C1:** The active-router implementation distinguishes successful completion from contact failure, aborts broken transfers, expires messages, and avoids evicting messages currently being sent when making buffer space.
- **C2:** Shared transfer machinery exposes policy decisions and completion/abort hooks to routing implementations, allowing experiments to vary routing strategy without rewriting connection lifecycle management.

Entry point: [ActiveRouter.java](https://github.com/akeranen/the-one/blob/master/src/routing/ActiveRouter.java). This is established research code with explicit modeling simplifications; its [API snapshot](https://api.github.com/repos/akeranen/the-one) showed a December 2024 last push, so current maintenance activity is not assumed. Unofficial ONE mirrors were excluded.

### 20. [booksim/booksim2](https://github.com/booksim/booksim2)

**Language/role:** C++; cycle-accurate interconnection-network and network-on-chip simulator.

This deliberately broadens coverage beyond Internet and wireless networks. Study routers, virtual channels, flow control, routing functions, and traffic injection at a hardware-oriented level.

- **C1:** Router buffer state tracks credits and occupancy across virtual channels, checks overflow, and validates how private and shared buffer space are partitioned. The simulation also separates warm-up, measurement, and draining so measured packets finish before final latency reporting. [Buffer policies and accounting](https://github.com/booksim/booksim2/blob/master/src/buffer_state.cpp).
- **C2:** Topologies, routing algorithms, traffic patterns, and router microarchitectures are configurable and designed for extension without replacing the whole simulator.

Further entry point: [BookSim user guide source](https://github.com/booksim/booksim2/blob/master/doc/manual.tex). This is a classic research implementation: parts of the guide retain historical SVN/toolchain instructions, and the [GitHub API snapshot](https://api.github.com/repos/booksim/booksim2) showed a June 2024 last push. Use the architecture and model definitions as the study target; do not infer a modern packaging workflow from the old guide.

## Link impairment and failure emulation

### 21. [ravinet/mahimahi](https://github.com/ravinet/mahimahi)

**Language/role:** C++; composable network-emulation shells and web-performance measurement tools.

Study how real application traffic can pass through repeatable link conditions. The packet shell separates namespace/TUN/process plumbing from the queue implementing an impairment.

- **C1:** Trace-driven links reject decreasing timestamps and zero-duration traces, track partially transmitted packets, and assert byte/packet accounting when queue policies drop data. [Link queue implementation](https://github.com/ravinet/mahimahi/blob/master/src/frontend/link_queue.cc).
- **C2:** A queue-parameterized packet shell creates the network namespace, establishes routing and DNS forwarding, and runs independent uplink/downlink queues. Different impairments reuse this execution machinery. [PacketShell implementation](https://github.com/ravinet/mahimahi/blob/master/src/packet/packetshell.cc).

This is an established research toolkit; its [API snapshot](https://api.github.com/repos/ravinet/mahimahi) showed an April 2025 last push. No claim about present release frequency or modern distribution compatibility is inferred.

### 22. [Shopify/toxiproxy](https://github.com/Shopify/toxiproxy)

**Language/role:** Go; programmable TCP proxy for emulating adverse connection conditions in tests.

Study a smaller-scale alternative to topology emulation: a stream-processing pipeline whose impairments can change while connections remain open.

- **C1:** Custom toxics must handle interruption at blocking operations, preserve in-flight bytes during updates, close correctly at end-of-stream, and synchronize shared state. These rules prevent the emulator itself from accidentally corrupting a stream.
- **C2/C3:** The `Toxic`, buffered-toxic, and stateful-toxic interfaces support reusable stages over timestamped chunks. Explicit buffering prevents a latency stage from unintentionally imposing a bandwidth limit, with a documented memory/backpressure tradeoff.

Entry points: [custom toxic architecture and lifecycle contract](https://github.com/Shopify/toxiproxy/blob/main/CREATING_TOXICS.md), [changelog with interruption, timeout, race-test, and API changes](https://github.com/Shopify/toxiproxy/blob/main/CHANGELOG.md). TCP stream impairment is narrower than arbitrary packet-network emulation.

### 23. [jagt/clumsy](https://github.com/jagt/clumsy)

**Language/role:** C; interactive Windows packet impairment using WinDivert.

Study packet interception and reinjection without changing the application or configuring it to use a proxy. It adds a Windows implementation to a field otherwise dominated by Linux research tools.

- **C1:** Receive and periodic processing threads coordinate through a mutex; stopping involves flushing module state, sending queued packets, closing the interception handle, and joining workers. This makes shutdown and ownership as interesting as the impairment algorithms.
- **C2:** A common module lifecycle supplies startup, packet processing, and close-down hooks for different impairments.
- **C3:** A periodic consumer keeps delayed packets moving even when receive activity is absent, and the loop measures processing cost against its timing interval.

Entry point: [capture, module dispatch, timing, and shutdown in divert.c](https://github.com/jagt/clumsy/blob/master/src/divert.c). The code also contains an acknowledged assertion-related FIXME; this is useful concurrency-study material, not a claim of flawless synchronization.

### 24. [torvalds/linux](https://github.com/torvalds/linux) — NetEm subsystem

**Language/role:** C; Linux kernel network-emulation queuing discipline. **Scope:** `net/sched/sch_netem.c`, not the entire kernel as a simulator.

Study the impairment engine underneath many Linux-based emulators: delay, jitter, loss correlation, duplication, corruption, and reordering operate directly on kernel packet buffers.

- **C1:** Correlated randomness uses scaled integer arithmetic; loss generators maintain Markov-chain state. The implementation carefully preserves a packet timestamp when reusing overlapping `sk_buff` storage for queue-tree links.
- **C2:** NetEm participates in the qdisc interface and can be composed with other disciplines for classification and rate control rather than absorbing every policy into one emulator.
- **C3:** Its implementation distinguishes frequently accessed packet-path state from cold configuration/timer fields and organizes queued packets by transmission time.

Entry point: [sch_netem.c](https://github.com/torvalds/linux/blob/master/net/sched/sch_netem.c). Inclusion is limited to this substantial subsystem; kernel-wide quality and performance are outside this report.

### 25. [freebsd/freebsd-src](https://github.com/freebsd/freebsd-src) — dummynet subsystem

**Language/role:** C; FreeBSD traffic shaper, packet scheduler, and network emulator. **Repository status:** official publish-only GitHub source mirror. **Scope:** dummynet under `sys/netpfil/ipfw` and its user-facing configuration contract.

Study a scheduler framework that separates packet classification, per-flow queues, scheduler instances, and emulated links.

- **C1:** Scheduler callbacks specify ownership on both successful enqueue and drop, and account for reconfiguration with nonempty queues. Queue removal must undo scheduling state as well as release storage. [Scheduler API contract](https://github.com/freebsd/freebsd-src/blob/main/sys/netpfil/ipfw/dn_sched.h).
- **C2:** Pipes, queues, flow masks, scheduler masks, weights, and link parameters support many queueing and link experiments through the same subsystem.
- **C3:** The manual distinguishes normal link emulation from a faster bypass mode and explicitly explains the resulting latency-fidelity tradeoff. [ipfw manual, dummynet configuration section](https://github.com/freebsd/freebsd-src/blob/main/sbin/ipfw/ipfw.8).

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, including: general discrete-event network frameworks; namespace/container emulation; Rust and Go network simulators; CORE/EMANE/IMUNES/GNS3 architecture; wireless sensor, vehicular, and cellular models; datacenter congestion-control simulators; SimPy packet models; opportunistic networking; cycle-accurate interconnection networks; TCP fault injection and Windows impairment; and kernel NetEm/dummynet scheduling. Targeted owner and project-name searches resolved canonical repositories and distinguished forks and mirrors. Later searches largely returned the retained families, their wrappers, or narrower research variants; this is a diverse selection, not an ecosystem census.

Every retained canonical URL was checked through the GitHub API, and every entry has an opened implementation or substantive architectural source beyond repository identification. Repository pages, project documentation, individual source files, and release histories were read; search snippets and stars were not treated as quality evidence. All 25 repositories were unarchived in the API snapshot. Unarchived status alone does not establish active maintenance; older implementation/documentation limitations are called out where relevant. Links to moving branches describe the research-date snapshot and can subsequently change.

The ns-3, SimGrid, and FreeBSD mirrors are explicitly identified. Mininet-WiFi is retained as a substantive separately evolved fork; Containernet, additional htsim variants, and BookSim derivatives were not added merely to multiply related implementations. Closed-source products, topology-only example collections, thin wrappers, unofficial historical mirrors, and general simulation libraries without substantial network-specific implementation were excluded. Narrower DPDK emulators and emerging simulators surfaced in discovery but were not exhaustively evaluated; satellite, underwater, and quantum-network ecosystems are not comprehensively covered.

No candidate code was executed, dependencies installed, or large repositories cloned. Performance criteria refer to inspected mechanisms, not reproduced benchmarks. Model validity, runtime compatibility, and maintenance responsiveness remain experiment-specific questions. The explanations of what an engineer can learn are grounded in the sources but remain editorial judgments.
