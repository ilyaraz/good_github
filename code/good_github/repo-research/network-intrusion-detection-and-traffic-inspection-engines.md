# Network intrusion detection and traffic inspection engines

Research date: **2026-10-09**

This selection covers 20 GitHub codebases that implement network intrusion detection, protocol dissection, stateful traffic inspection, application classification, or reusable inspection engines. It includes packet-facing systems, a behavioral detector built on network flows, and a small number of substantial libraries for constructing analyzers. Capture-only drivers, security distributions, dashboards around other engines, rule collections, and model-training demonstrations are outside the selection.

The criteria describe engineering worth studying, not a claim that every component is exemplary or that a detector is accurate on every workload. Architectural implications below are grounded engineering judgments from the linked implementation material. Repository identity, default branches, and archive status were checked through GitHub repository pages or the GitHub API. An unarchived repository is not automatically considered actively maintained; notable historical projects and official mirrors are identified explicitly.

**Criteria legend**

- **C1 — Difficult correctness:** protocol/state invariants, concurrency, numerical semantics, adversarial input, or consequential failure modes.
- **C2 — Reusable abstractions:** substantial interfaces or frameworks supporting different protocols, policies, integrations, or analysis tasks.
- **C3 — Performance with structure:** concrete mechanisms addressing packet rate, memory, latency, or scale within an understandable architecture.
- **C4 — Sustained evolution:** multi-year change history accompanied by compatibility work, testing, or deliberate complexity management.

## Intrusion detection and programmable security policy

### 1. [OISF/suricata](https://github.com/OISF/suricata)

**Language / role:** C and Rust; network IDS, inline IPS, and network security monitoring engine.

Study the boundary between TCP reconstruction, application parsing, and signature inspection. Suricata makes the consequences of processing incomplete or attacker-controlled streams unusually explicit, including differences between passive inspection and inline enforcement.

- **C1:** The stream engine handles normalization, gaps, urgent data, inspection progress, and stream-depth limits. Inspection consumes reconstructed data through windows; randomized chunk boundaries and parser-triggered inspection address evasion and delayed detection. These are concrete correctness obligations, not merely packet decoding. [Stream inspection internals](https://docs.suricata.io/en/latest/devguide/internals/engines/stream/inspection_raw_data.html).
- **C3:** The same design uses a continuous buffer for contiguous data, red-black-tree storage for small gaps, and regions for large gaps, explicitly trading representation complexity for memory efficiency. The linked internals explain how consumed data can leave the window.
- **C4:** The repository documents regression tests, sanitizer runs, PCAP fuzzing, and IDS/IPS traffic replay as acceptance checks. Its change history spans multiple major generations and records fixes for detection bypasses, protocol edge cases, memory handling, and build compatibility. [ChangeLog](https://github.com/OISF/suricata/blob/main/ChangeLog).

### 2. [snort3/snort3](https://github.com/snort3/snort3)

**Language / role:** C++; Snort 3 intrusion prevention engine with Lua configuration.

This is a strong study of turning a large security engine into explicit extension contracts. Its inspector taxonomy separates stream reconstruction, raw-packet processing, service inspection, service identification, and pre/post-detection work.

- **C2:** Plugins share a versioned `BaseApi`, while modules validate configuration and transfer configured state to plugin instances. Codecs and inspectors can be extended independently; module scope distinguishes global, network, inspection, and IPS policies. [Extension and module design](https://github.com/snort3/snort3/blob/master/doc/devel/extending.txt).
- **C1:** Codec contracts require length validation before interpreting packet headers and explicit propagation of the next protocol and layer length. Reconstruction also invokes distinct formatting and length-update operations. These interfaces expose how malformed input and rebuilt packets must remain consistent across plugins. The same developer document provides the concrete decoding and reconstruction contracts.

### 3. [zeek/zeek](https://github.com/zeek/zeek)

**Language / role:** C++ and Zeek scripting language; programmable network security analysis.

Study how to separate protocol observations from site-specific interpretation. The engine emits events, while scripts maintain state and correlate activity across sessions and hosts; this supports detection, inventory, logging, and research without embedding every policy in a dissector.

- **C2:** Input, packet, session, and file analysis are distinct stages with plugin extension points. Stateful event handlers provide a reusable policy layer above these stages. [Architecture](https://docs.zeek.org/en/current/about/architecture.html).
- **C3:** Zeek scales its principal single-threaded analysis loop through worker processes, with manager, logger, and proxy roles separating coordination and output. The deployment documentation explains symmetric flow distribution and the disruption caused when workers leave and rejoin a fanout group. [Cluster architecture and flow balancing](https://docs.zeek.org/en/current/cluster-setup.html).

### 4. [kismetwireless/kismet](https://github.com/kismetwireless/kismet)

**Language / role:** C++ and C; wireless intrusion detection and multi-radio traffic inspection. **Official GitHub mirror**, as identified in repository metadata.

Kismet adds wireless and device-oriented engineering to a category otherwise dominated by IP streams. Its documented scope includes Wi-Fi, Bluetooth/BTLE, Zigbee, and other radio sources. [Project introduction](https://www.kismetwireless.net/docs/readme/intro/kismet/).

- **C1:** The packet chain makes capture ordering, queue handoff, duplicate handling, and shared device updates explicit. Its FIFO transfers packets in queue order, while assignment identifiers guide which processing thread sees packets affecting the same devices.
- **C3:** Post-capture processing extracts enough link-layer information to assign work before the full dissection pipeline. This reduces device-lock contention; the chain then separates dissection, decryption, classification, tracking, and logging. Backlog accounting and reader-pause thresholds expose overload management. [Packet-chain implementation and design comments](https://github.com/kismetwireless/kismet/blob/master/packetchain.h).

### 5. [stratosphereips/StratosphereLinuxIPS](https://github.com/stratosphereips/StratosphereLinuxIPS)

**Language / role:** Python; Slips behavioral network IDS/IPS. Its packet/PCAP interpretation relies on Zeek; the substantive subsystem here is its own flow profiling and detection engine.

Study how multiple detectors contribute evidence over time rather than emitting an independent alert for every observation. Slips creates per-IP profiles, divides activity into time windows, and stores both detection evidence and the underlying interpreted flows.

- **C1:** Alert construction depends on temporal scope and accumulated evidence crossing a threshold. The architecture distinguishes evidence from alerts, explains window-specific threat state, and notes that interface-scoped evidence can contribute to a broader alert. These distinctions are important invariants for avoiding accidental conflation of unrelated observations.
- **C2:** Detection modules share profile data through Redis and communicate using publish/subscribe channels; normalized flows are retained in SQLite. This separates ingestion, enrichment, detection, and evidence presentation. [Architecture and data model](https://github.com/stratosphereips/StratosphereLinuxIPS/blob/master/docs/architecture.md); [module development guide](https://stratospherelinuxips.readthedocs.io/en/develop/create_new_module.html).

### 6. [haka-security/haka](https://github.com/haka-security/haka)

**Language / role:** C and Lua; programmable packet filtering and inspection runtime. **Historical/dormant:** GitHub metadata reports its last push in November 2017; it is not marked archived.

Haka is worth reading for its language-oriented design, rather than as an assertion of current operational suitability. It combines capture modules, protocol dissectors, and Lua policy with a protocol grammar abstraction.

- **C1:** Calling a downstream dissector transfers packet ownership. The architecture explicitly requires that dissector to accept the packet before it can continue onto the network, and identifies the point where a stateless dissector creates stateful flow context. [Ownership and flow architecture](https://github.com/haka-security/haka/blob/develop/doc/developer/arch.rst).
- **C2:** Grammars support composition, recursive declarations, exported parsing entry points, conversion, validation, memoization, and actions. This is a reusable protocol-description system, beyond a collection of hard-coded Lua checks. [Grammar reference](https://github.com/haka-security/haka/blob/develop/doc/ref/grammar.rst).

## Protocol analysis and forensic inspection pipelines

### 7. [wireshark/wireshark](https://github.com/wireshark/wireshark)

**Language / role:** C and C++; Wireshark/TShark packet dissection engine and applications. **Official read-only GitHub mirror** of the project’s GitLab repository.

The relevant subsystem is the dissection engine, not just the graphical packet viewer. Study how many independently developed protocol parsers cooperate through common buffers, protocol trees, dispatch, conversations, and reassembly facilities.

- **C2:** A dissector decodes one layer and hands encapsulated data to another. Built-in and dynamically loaded dissectors use the same basic model, with an explicit exported ABI for plugins. [How dissection works](https://www.wireshark.org/docs/wsdg_html_chunked/ChapterDissection.html).
- **C1:** Reassembly requires grouping the correct fragments, deciding when a message is complete, and preserving packet context. Shared machinery reports overlapping/conflicting fragments, multiple tails, oversized fragments, and reconstruction errors; the guide also treats TCP message reassembly. [Reassembly design and APIs](https://www.wireshark.org/docs/wsdg_html_chunked/ChDissectReassemble.html).

### 8. [arkime/arkime](https://github.com/arkime/arkime)

**Language / role:** C capture engine and JavaScript services; session-oriented inspection, full-packet retention, indexing, and forensic retrieval.

Study the capture/parser subsystem and its relationship to storage and retrieval. Arkime explicitly positions itself alongside IDS tools; inclusion here rests on its own traffic parsing and session indexing, not on treating it as a signature IDS.

- **C2:** The architecture separates a threaded capture application, per-sensor viewer, and search database. Packet data remains in PCAP while extracted session metadata is indexed, and APIs expose both packets and structured session information. [Component description](https://github.com/arkime/arkime/blob/main/README.md).
- **C3:** Packet retention and metadata retention scale through different resources. The deployment design discusses horizontal capture expansion, additional capture threads, packet brokers for asymmetric paths, and disk-I/O bottlenecks when capture processes share a host. [Deployment architecture](https://arkime.com/architecture).

### 9. [elastic/beats](https://github.com/elastic/beats)

**Language / role:** Go; **Packetbeat subsystem** of the Beats monorepo, counted once. Packetbeat reconstructs application transactions from observed network traffic.

Study the boundary between transport tracking, protocol-specific state, and event publication. This is particularly useful for understanding an analyzer whose primary output is structured transactions rather than packet displays or attack signatures.

- **C1:** A TCP protocol plugin must handle payload delivery, FIN, missing-byte notifications, and connection timeouts. The gap callback can request that a stream be dropped, and an optional expiration callback handles timed-out state. These contracts make incomplete captures and lifecycle failures visible to each application parser.
- **C2:** The protocol registry separates TCP and UDP implementations, per-protocol construction/configuration, and the reporter used to publish transaction events. [Plugin and transport contracts](https://github.com/elastic/beats/blob/main/packetbeat/protos/registry.go). The contribution guide describes full-program tests driven by PCAP fixtures. [Protocol implementation/testing guide](https://github.com/elastic/beats/blob/main/packetbeat/SUPPORT_PROTOCOL.md).

### 10. [dreadl0ck/netcap](https://github.com/dreadl0ck/netcap)

**Language / role:** Go; packet/stream inspection and typed audit-record production, with detection and forensic features.

Netcap is useful for studying the path from network bytes to reusable records. Its own decoders and stream handling provide substance beyond its optional integrations with nDPI and libprotoident.

- **C2:** The documented architecture distinguishes layer decoders from custom whole-packet decoders for abstractions such as flows and connections. Lifecycle hooks and Protocol Buffer records separate decoding from downstream serialization and analysis. [Internals](https://github.com/dreadl0ck/netcap/blob/master/docs/internals.md).
- **C1 / C3:** Reassembly distinguishes cumulative bytes inspected in each stream direction from per-connection and global out-of-order buffering. Reaching a byte limit closes that direction while retaining connection state, preventing subsequent packets from immediately recreating the same state to bypass the cap. Buffer pressure can instead force delivery with gaps. [Reassembly limits and resulting semantics](https://github.com/dreadl0ck/netcap/blob/master/docs/STREAM_REASSEMBLY_LIMITS.md).

The internals document contains older package references; use it for concepts and the current source tree for exact package locations.

## Classification, fingerprinting, and flow-feature engines

### 11. [ntop/nDPI](https://github.com/ntop/nDPI)

**Language / role:** C; embeddable application-protocol classification and metadata inspection library.

Study the library boundary between an external flow manager and an incremental detector. nDPI is a distinct engine even when applications such as ntopng and NFStream incorporate it.

- **C1:** Its API requires staged initialization and explicitly prohibits parallel calls that create detection contexts. Per-packet processing receives connection state, packet length, and time; the separate give-up operation handles a flow whose classification is unfinished. [Detection API contracts](https://github.com/ntop/nDPI/blob/dev/src/include/ndpi_api.h).
- **C2:** Independent detection contexts, caller-supplied flow information, configurable allocators, and protocol metadata APIs let the classifier be embedded in different capture and analysis architectures. The API header is the useful starting point.
- **C4:** The changelog spans releases from 2017 through 2026 and records API/configuration changes, protocol revisions, portability work, and fuzzing/test improvements. It also makes removed options and changed component behavior visible. [Change history](https://github.com/ntop/nDPI/blob/dev/CHANGELOG.md).

### 12. [ntop/ntopng](https://github.com/ntop/ntopng)

**Language / role:** C++ and Lua; flow-aware traffic monitoring and behavioral checking above packet inspection.

The interesting subsystem is the flow/check execution layer above nDPI, not merely the web interface. It turns classification and connection state into reusable monitoring and alerting hooks.

- **C2:** `FlowChecksExecutor` maintains separate check lists for flow creation, protocol detection, periodic updates, and flow termination. It dispatches corresponding methods and then flushes resulting alerts. [Check executor](https://github.com/ntop/ntopng/blob/dev/src/FlowChecksExecutor.cpp).
- **C3:** The documentation explicitly places flow checks in C++ for efficiency, while offering a Lua extension path. The Lua check runs once when the application protocol becomes known rather than on every packet or periodic update; the C++ executor also provides optional per-check timing. This exposes a concrete extension-cost tradeoff. [Flow-check execution model](https://www.ntop.org/guides/ntopng/api/lua_c/flow_checks/index.html).

### 13. [LibtraceTeam/libprotoident](https://github.com/LibtraceTeam/libprotoident)

**Language / role:** C++; lightweight application-protocol identification using the first four payload bytes in each direction and associated flow information.

This is a useful alternative design to full application-message dissection. Its restricted observation model makes classification priorities, ambiguity, and state requirements easy to examine. GitHub metadata showed the last push in August 2024; no current maintenance cadence is inferred.

- **C2:** Protocol modules carry an identifier, category, priority, and matching callback. The public flow-data structure and update/guess API let callers supply their own flow tracking, including an explicit direction value. [Public data and module API](https://github.com/LibtraceTeam/libprotoident/blob/master/lib/libprotoident.h).
- **C3:** Classification checks priority-ordered module lists and stops at the first match. Implementation comments explain why a simple serial loop was preferred to threading tiny callbacks. The input update path also stops collecting after a bounded observation amount to avoid sequence-wrap complications. [Classification and flow-update implementation](https://github.com/LibtraceTeam/libprotoident/blob/master/lib/libprotoident.cc).

### 14. [DanieleDeSensi/peafowl](https://github.com/DanieleDeSensi/peafowl)

**Language / role:** C engine with C++ and Python APIs; application identification and protocol-field extraction independent of the packet-capture backend.

Peafowl provides a compact study of incremental classification. A caller supplies packets, while the engine tracks bidirectional flows and exposes packet and flow-level results.

- **C1:** A protocol inspector distinguishes a match, a definite non-match, insufficient data, and an error. Per-flow private state persists between packets, so an incomplete first observation need not become a premature classification. [Inspector contract and protocol-extension procedure](https://peafowl.readthedocs.io/en/latest/newprotocols.html).
- **C2:** The same underlying inspectors become available through the C, C++, and Python interfaces. A flow-termination callback exposes accumulated statistics before internal state is removed; the flow model covers both connection termination and inactivity expiry. [Flow lifecycle and callbacks](https://peafowl.readthedocs.io/en/latest/flows.html).

### 15. [Montimage/mmt-dpi](https://github.com/Montimage/mmt-dpi)

**Language / role:** C; MMT-DPI protocol classification, attribute extraction, and session tracking, including mobile-network protocols.

Study a data-extraction engine organized around registered attributes and handler contexts. The checked upstream GitHub repository is `Montimage/mmt-dpi`; its current README also directs build/release users to `montimage-projects/mmt-dpi`. This family is counted once.

- **C2:** The core manages sessions and processing contexts, while shared-library plugins implement protocol classification, field extraction, and optional session hooks. Packet, attribute, and session callbacks consume a protocol hierarchy and typed extracted fields. [Architecture](https://github.com/Montimage/mmt-dpi/blob/main/docs/ARCHITECTURE.md).
- **C1 / C3:** The threading contract separates process-global registration from one handler per worker. Per-handler snapshots keep registry work off the packet path, while mutexes and atomic flags protect lifecycle operations. The document explains initialization/shutdown ordering and a ThreadSanitizer harness comparing concurrent replay against a serial baseline. [Thread ownership and concurrency verification](https://github.com/Montimage/mmt-dpi/blob/main/docs/THREADING.md).

### 16. [nfstream/nfstream](https://github.com/nfstream/nfstream)

**Language / role:** Python and C; network-flow metering, statistical feature computation, and application metadata extraction, incorporating nDPI.

NFStream adds substantial metering and extension machinery rather than simply exposing the nDPI API. Study how packet observations become consistently keyed, expiring flows that can feed both offline experiments and live analysis.

- **C1:** Flow keys canonicalize direction and include VLAN and tunnel identity. The meter distinguishes active, idle, and custom expiration, making the definition of a flow and the timing of emitted records explicit. [Meter implementation](https://github.com/nfstream/nfstream/blob/master/nfstream/meter.py).
- **C3:** An ordered LRU flow cache lets expiry scanning stop once the oldest remaining flow is still live; scanning also has a fixed work budget. This connects timing semantics to per-iteration processing cost in the same implementation.
- **C2:** `NFPlugin` supplies initialization, packet-update, expiration, and cleanup hooks, allowing custom features and analysis without replacing metering. [Plugin lifecycle](https://github.com/nfstream/nfstream/blob/master/nfstream/plugin.py).

### 17. [cisco/mercury](https://github.com/cisco/mercury)

**Language / role:** C++ with Python tooling; network metadata parsing and protocol fingerprinting. The project README describes the software as beta.

Mercury is especially useful for studying metadata analysis of encrypted protocols without assuming that encrypted payload can be decoded. Its fingerprint representation is built from selected and normalized protocol elements.

- **C1:** The parsing design represents bounded byte regions as pointer pairs with explicit null, empty, and readable states. It distinguishes readable from complete data, propagates truncation, and states lifetime requirements for parsed views into packet buffers. [Safe-parsing design](https://github.com/cisco/mercury/blob/main/doc/safe-parsing.md).
- **C3:** Separating top-level parsing from later field parsing avoids dynamically allocating a variable-sized collection of header objects. This provides a concrete allocation-versus-reparsing tradeoff within the same design.
- **C2:** The fingerprint specification defines a tree-based representation, versioned protocol formats, and exact, prefix, and approximate matching concepts. It explicitly handles evolution and truncated observations. [Network Protocol Fingerprinting specification](https://github.com/cisco/mercury/blob/main/doc/npf.md).

### 18. [cisco/joy](https://github.com/cisco/joy)

**Language / role:** C with Python analysis tools; flow and intraflow feature extraction. **Archived.** Its README points to Mercury for newer fingerprinting tools and describes Joy as research-oriented alpha/beta software.

Joy remains instructive as a different architecture from Mercury: it aggregates packet lengths/times, byte distributions, TLS records, and protocol metadata into flow records and exposes a reusable library.

- **C1:** Feature readiness and feature-consumption flags are separate. External-processing callbacks mark data consumed without immediately deleting the record; callback-buffer lifetime is explicitly documented. Correct deletion therefore depends on the downstream consumer’s progress. [Library API](https://github.com/cisco/joy/blob/master/src/include/joy_api.h).
- **C2 / C3:** The API supports multiple worker contexts and includes a packet-to-context function that keeps both directions of a flow together. Configurable feature flags and per-feature callbacks let an embedding application control extraction and processing. The [project overview and release notes](https://github.com/cisco/joy/blob/master/README.md) also document the transition to a reusable library and threaded processing.

## Research frameworks and reusable inspection building blocks

### 19. [stanford-esrg/iris](https://github.com/stanford-esrg/iris)

**Language / role:** Rust with DPDK; research framework for programmable traffic analysis.

Iris represents a newer architecture, without claiming the operational history of Zeek or Suricata. Its subscription model combines filters, requested data types, and callbacks, exposing packets, reconstructed streams, and parsed sessions through one framework.

- **C2:** Applications can define new data types and stateful filters and attach callbacks to connection state transitions. This lets multiple analyses share connection tracking and protocol-derived abstractions. [Programming model](https://github.com/stanford-esrg/iris/blob/main/README.md).
- **C1:** The state-transition implementation explicitly separates raw transport packets from reconstructed streams and models when transitions cannot be totally ordered across layers. It warns that observing handshake packets does not validate their sequence numbers and that payload may overlap a handshake. These are valuable examples of documenting an analyzer’s actual guarantees. [Connection-state semantics](https://github.com/stanford-esrg/iris/blob/main/core/src/conntrack/conn/conn_state.rs).

### 20. [seladb/PcapPlusPlus](https://github.com/seladb/PcapPlusPlus)

**Language / role:** C++; reusable protocol parsing and TCP/IP reconstruction components for custom inspection applications.

This entry is specifically about the inspection and reconstruction engines. The repository also contains capture wrappers and packet-crafting functionality, but its inclusion does not rest on those wrappers alone.

- **C1:** TCP reconstruction tracks both connection directions, distinguishes retransmissions from new data, queues out-of-order segments, and reports missing bytes when a gap cannot be resolved. Closed-connection information can be retained to recognize late packets. [TCP reassembly contract](https://github.com/seladb/PcapPlusPlus/blob/master/Packet++/header/TcpReassembly.h).
- **C2:** Callbacks for connection creation, data delivery, and termination make the engine reusable across application protocols. The broader library supplies composable protocol layers, IP reconstruction, and packet filtering. [Feature and subsystem guide](https://pcapplusplus.github.io/docs/features).
- **C3:** Reassembly exposes limits on retained out-of-order fragments and the number of closed connections purged in one cleanup call, making memory retention and cleanup latency explicit rather than hidden behind the callback interface.

## Coverage and search notes

Discovery used more than six distinct live-search formulations, followed by repository-page/API checks and direct reading of implementation files or official technical documentation for every retained repository. The search angles included:

- Signature IDS/IPS architecture: Suricata, Snort, and Zeek.
- DPI toolkit alternatives: nDPI, lightweight payload classification, and libprotoident.
- Go and Rust traffic-analysis engines, connection reconstruction, and DPDK research frameworks.
- Cisco encrypted-traffic metadata and fingerprinting tools.
- Lua-programmable inspection and historical engines, including Haka and AIEngine.
- Wireless intrusion detection and Kismet’s packet-processing architecture.
- Behavioral flow detection and Stratosphere Linux IPS.
- Reusable C++ reconstruction components, including PcapPlusPlus and libtins.
- Academic DPI libraries, including Peafowl.
- Industrial/mobile protocol inspection and Montimage MMT-DPI.
- Follow-up searches for less common implementation languages and alternative DPDK-based IDS engines.

Later broad searches increasingly returned the same established engines, thin API/dashboard combinations, student demonstrations, or general capture infrastructure. The selection therefore stops at 20 distinct codebases rather than treating every search hit as a qualifying implementation. It spans C, C++, Rust, Go, Python, Lua, and a dedicated analysis language, from embeddable classifiers to clustered monitors and wireless sensors.

Important boundaries and exclusions:

- **AIEngine:** its [GitHub page](https://github.com/camp0/aiengine) says the actual project is on Bitbucket. It was excluded because a continuing official substantive GitHub mirror was not established.
- **tcpdump:** the expected GitHub repository could not be verified through the GitHub API in this session. It was omitted rather than substituting an unverified fork or guessing a new canonical location.
- **Security Onion, Dalton, rule repositories, and deployment labs:** valuable surrounding infrastructure, but not independently implemented inspection engines for this report. Host-focused IDS/EDR and general log-security platforms were also excluded.
- **DPDK, PF_RING, generic packet APIs, and standalone pattern matchers:** infrastructure alone does not establish category fit. PcapPlusPlus is retained specifically because its own substantial reconstruction engine was inspected.
- **Forks and shared dependencies:** nDPI consumers are included only for additional substantive engine layers; no ordinary fork is counted separately. MMT-DPI is counted once despite its related GitHub locations. Beats is counted once for Packetbeat.

This was read-only source research: no candidate code was executed, no dependencies were installed, and no throughput or detection-accuracy claims were independently benchmarked. Linked default-branch files can evolve. C4 is awarded only where the inspected history and testing/compatibility evidence support it; age, stars, and recent pushes alone were not used as substitutes.
