# Packet capture and protocol analysis tools

Research date: **2026-10-09**.

This selection covers packet acquisition, capture-file processing, protocol dissection, stream reconstruction, indexed packet retention, and specialized network or bus analyzers. It includes applications and substantial libraries in C, C++, Rust, Go, Python, Java, and JavaScript. Each of the 26 repositories has a verified GitHub location and an inspected implementation or architectural source beyond its repository landing page. The criteria below are evidence-grounded engineering judgments, not a claim that every component is exemplary or a recommendation to deploy every project.

Criteria legend:

- **C1 — Difficult correctness:** invariants, concurrency, numerical or wire-format semantics, adversarial input, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or models supporting multiple protocols, backends, applications, or workflows.
- **C3 — Performance with structure:** explicit resource or throughput constraints addressed through understandable architectural choices.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or complexity management; age alone does not qualify.

## Capture engines and acquisition infrastructure

### [the-tcpdump-group/libpcap](https://github.com/the-tcpdump-group/libpcap)

**C — Portable packet-capture library.** Study how a stable capture interface accommodates operating-system mechanisms with different buffering, filtering, timestamp, and shutdown semantics. Its Linux backend is especially instructive because portability extends to differing kernel capabilities within one operating system.

- **C1:** The Linux implementation uses acquire/release operations when transferring ownership of ring frames and blocks. It also distinguishes a VLAN identifier of zero from the absence of VLAN metadata and handles kernel-version differences in that distinction. These are concrete concurrency and capture-fidelity obligations. See [the Linux backend](https://raw.githubusercontent.com/the-tcpdump-group/libpcap/master/pcap-linux.c).
- **C3:** That backend implements memory-mapped TPACKET capture, with separate V2/V3 handling and filtering paths. The useful study is how the library organizes ring consumption and kernel capability checks around an application-facing capture abstraction, rather than a universal throughput claim. The same [implementation](https://raw.githubusercontent.com/the-tcpdump-group/libpcap/master/pcap-linux.c) is the primary entry point.

### [ntop/PF_RING](https://github.com/ntop/PF_RING)

**C — Linux capture infrastructure, including a kernel module and userspace library.** Focus on the open-source kernel/userspace implementation in this repository; do not assume every separately offered PF_RING ZC component has the same availability or licensing.

- **C1:** The kernel implementation makes packet distribution and shared-state lifetime explicit. Its fragment-affinity cache addresses a subtle issue: later IP fragments lack transport fields needed for the ordinary flow hash, yet must reach the appropriate consumer. Locking, cluster membership, and deferred reclamation are visible in [the kernel implementation](https://raw.githubusercontent.com/ntop/PF_RING/dev/kernel/pf_ring.c).
- **C3:** Ring-backed delivery and clustered consumers address capture overhead and distribution across readers. The architecture is worth studying alongside its compatibility costs: the [changelog](https://raw.githubusercontent.com/ntop/PF_RING/dev/CHANGELOG.md) records kernel adaptation, namespace races, and shutdown fixes, making the engineering tradeoffs more concrete than feature or speed claims alone.

### [LibtraceTeam/libtrace](https://github.com/LibtraceTeam/libtrace)

**C — Trace-reading and capture library with a parallel processing API.** A useful bridge between packet I/O formats and applications that need coordinated worker and reporting stages.

- **C2:** Callback sets, packet hashing, thread-local initialization, reporting, and result combiners form a reusable processing framework. Applications can supply their own flow assignment and aggregation logic without rebuilding trace acquisition. Start with [the parallel API header](https://github.com/LibtraceTeam/libtrace/blob/master/lib/libtrace_parallel.h).
- **C1:** That API documents ownership and lifecycle obligations: publishing a packet affects who must release it; paused combiners must make retained packets safe; final draining occurs after processing threads stop. These contracts expose the hard boundary between concurrent capture, deferred reporting, and shutdown. The [callback and combiner declarations](https://github.com/LibtraceTeam/libtrace/blob/master/lib/libtrace_parallel.h) are particularly valuable reading.

### [netsniff-ng/netsniff-ng](https://github.com/netsniff-ng/netsniff-ng)

**C — Linux networking toolkit; the relevant subsystem is the netsniff-ng capture/analyzer and its ring backend.** Count the repository once, including its related utilities.

- **C3:** The receive path separates ring sizing, creation, mapping, frame setup, binding, polling, and fanout. Its TPACKET V2/V3 handling makes memory-mapped acquisition and packet distribution inspectable without treating a zero-copy label as a benchmark. See [ring_rx.c](https://raw.githubusercontent.com/netsniff-ng/netsniff-ng/main/ring_rx.c).
- **C1:** The same implementation checks ring layouts, includes compile-time structure-layout assertions, and retries ring allocation with a reduced layout after memory exhaustion. This is useful code for studying ABI assumptions and resource-failure recovery at the kernel/userspace boundary. Begin with the setup and teardown functions in [the receive-ring implementation](https://raw.githubusercontent.com/netsniff-ng/netsniff-ng/main/ring_rx.c).

### [xdp-project/xdp-tools](https://github.com/xdp-project/xdp-tools)

**C/eBPF — The xdp-dump subsystem captures packets at XDP program entry and exit.** This monorepo counts once. xdpdump is an acquisition and observation tool, not a general protocol dissector; its distinctive value is observing traffic, including drops, that ordinary capture may miss.

- **C1:** Event handling validates record lengths and program indices, accounts for lost events, and maintains identifiers used to relate observations before and after program execution. The capture record must preserve what was observed and what the XDP program decided. See [xdpdump.c](https://raw.githubusercontent.com/xdp-project/xdp-tools/main/xdp-dump/xdpdump.c).
- **C3:** The design uses BPF tracing and perf-buffer delivery, with a configurable wakeup threshold that trades notification overhead against delivery behavior. The [xdp-dump documentation](https://raw.githubusercontent.com/xdp-project/xdp-tools/main/xdp-dump/README.org) explains attachment modes, entry/exit capture, metadata, and the libpcap fallback when no XDP program is available.

## General dissection and stateful analysis

### [wireshark/wireshark](https://github.com/wireshark/wireshark)

**C/C++ — Wireshark, TShark, and shared capture/dissection infrastructure.** This GitHub repository is the project's **official read-only mirror**; development is hosted on GitLab, as the repository states. Study the common protocol engine rather than treating the GUI as the entire project.

- **C2:** Protocol dissection is a cascade of registered dissectors, with reusable protocol-tree and plugin mechanisms. That architecture supports a large protocol ecosystem and multiple frontends. The [dissector development chapter](https://www.wireshark.org/docs/wsdg_html_chunked/ChapterDissection.html) explains registration, layering, and extension points.
- **C1:** Protocol messages do not necessarily align with TCP segments. The reassembly interface separates minimum-header requirements, message-length determination, and complete-PDU dissection; it also supplies fragmentation machinery for other protocols. The [reassembly guide](https://www.wireshark.org/docs/wsdg_html_chunked/ChDissectReassemble.html) is a concrete entry point for studying incomplete observations and message-boundary correctness.

### [the-tcpdump-group/tcpdump](https://github.com/the-tcpdump-group/tcpdump)

**C — Command-line capture and protocol printers.** An unusually direct study of defensive parsing in a large collection of independently evolving wire formats.

- **C1:** Contributor guidance assumes packets may be truncated at any byte. It requires bounds-aware extraction macros, explicit checks for intervening fields, and correct unaligned and byte-order handling. The [contributor guide](https://raw.githubusercontent.com/the-tcpdump-group/tcpdump/master/CONTRIBUTING.md) explains the coverage obligation rather than simply advising developers to be careful.
- **C4:** The [2023–2026 change history](https://raw.githubusercontent.com/the-tcpdump-group/tcpdump/master/CHANGES) records continuing truncation fixes, integer/checksum corrections, timestamp edge cases, cross-compilation, and platform compatibility work. The contributor guide also documents packet fixtures with expected output, timezone-stable regression results, and a compiler/options build matrix. Together, these provide evidence of sustained complexity management.

### [zeek/zeek](https://github.com/zeek/zeek)

**C++ and Zeek scripts — Stateful network protocol analysis and event-driven policy.** Study how imperfect packet observations become protocol events without forcing every application to implement transport state itself.

- **C1:** The TCP reassembler distinguishes meaningful gaps from partial connections and shutdown artifacts, handles keepalive-related edge cases, and checks delivery-position invariants. Its [TCP_Reassembler.cc](https://raw.githubusercontent.com/zeek/zeek/master/src/analyzer/protocol/tcp/TCP_Reassembler.cc) exposes the reasoning needed when the observer did not see the whole connection.
- **C2:** Analyzer registration, port association, dynamic protocol detection, scheduled analyzers, and failure events provide a reusable separation between protocol engines and script policy. The [analyzer framework API](https://docs.zeek.org/en/current/scripts/base/frameworks/analyzer/main.zeek.html) is the complementary entry point: it shows how applications select and react to analyzers rather than embedding every decision in packet parsing.

### [OISF/suricata](https://github.com/OISF/suricata)

**C and Rust — Network inspection engine; focus on TCP stream handling and application-layer inspection.** The inclusion concerns these packet-analysis subsystems, not a blanket assessment of every IDS feature.

- **C1:** Stream inspection must reconcile normalization, missing bytes, urgent data, depth limits, and different passive/inline behavior. Randomized inspection chunks also address predictable inspection boundaries that an adversary could exploit. These obligations are described in the [stream inspection design](https://docs.suricata.io/en/latest/devguide/internals/engines/stream/inspection_raw_data.html).
- **C3:** The same design selects different storage strategies for contiguous data, small gaps, and large gaps, then advances a sliding window according to inspection progress. Memory caps and inspection depth are architectural constraints, while parser requests govern when complete entities are ready. This is a useful example of tying data structures and retention to downstream consumption rather than buffering streams indefinitely.

### [kpcyrd/sniffglue](https://github.com/kpcyrd/sniffglue)

**Rust — A sandboxed, multithreaded packet sniffer.** A smaller application worth reading for the boundary between privileged acquisition, untrusted packet parsing, and presentation.

- **C1:** Initialization and packet processing are deliberately separated by staged sandbox activation. The repository describes seccomp, privilege reduction, and parser fuzzing; [main.rs](https://github.com/kpcyrd/sniffglue/blob/main/src/main.rs) shows when sandbox stages occur relative to device setup and processing threads.
- **C3:** Capture access is synchronized, but the worker releases the acquisition lock before parsing. Workers send results through a bounded channel to the output stage. That gives an understandable treatment of parallel work, output serialization, and backpressure. Follow the capture mutex, worker loop, and `sync_channel` in [the main implementation](https://github.com/kpcyrd/sniffglue/blob/main/src/main.rs).

## Indexed packet retention and retrieval

### [arkime/arkime](https://github.com/arkime/arkime)

**C capture engine; JavaScript/Node.js viewer — Full-packet retention with searchable session metadata.** Study the relationship among packet files, metadata indexes, distributed sensors, and interactive retrieval.

- **C2:** The repository separates threaded capture and protocol parsing from indexed session metadata and the viewer's packet-retrieval interfaces. Standard PCAP storage and independently managed metadata make these components useful across different deployment arrangements. The repository overview and [architecture guide](https://arkime.com/architecture) describe these boundaries.
- **C3:** The architecture distinguishes scaling across sensors from adding capture threads within a sensor. It discusses disk contention between packet writes and database work, viewer placement, and packet-broker distribution, including asymmetric flows. Those are concrete resource and locality constraints, not merely a claim of high throughput. Start with the deployment diagrams and storage discussion in [the architecture guide](https://arkime.com/architecture).

### [google/stenographer](https://github.com/google/stenographer)

**C++ capture process and Go service — Indexed packet recording and selective retrieval.** **Archived on November 4, 2022.** Retain it as a historical architectural study, not as evidence of a currently maintained deployment choice.

- **C3:** Its [design document](https://raw.githubusercontent.com/google/stenographer/master/DESIGN.md) follows packets from AF_PACKET shared blocks through asynchronous direct disk writes, while separate index writers construct searchable attribute-to-offset indexes. Query results combine index sets and stream selected packets. The design explicitly favors sustained recording and selective reads.
- **C1:** Captures and indexes are written under temporary names and exposed after the relevant flush/publication steps; the supervisor handles capture-process restarts and temporary-file cleanup. The design also makes the handoff between packet writers and index writers visible. Study these failure and publication boundaries in [DESIGN.md](https://raw.githubusercontent.com/google/stenographer/master/DESIGN.md), while recognizing that this is design documentation rather than a crash-consistency audit.

## Packet, stream, and capture-file libraries

### [seladb/PcapPlusPlus](https://github.com/seladb/PcapPlusPlus)

**C++ — Capture backends, packet parsing/construction, and transport reassembly.** This is more than a libpcap wrapper: its own packet model and reassembly machinery are central reasons for inclusion.

- **C2:** A shared packet-parsing layer works across capture sources, including conventional libpcap/Npcap and specialized acquisition backends. The [feature/API overview](https://pcapplusplus.github.io/docs/features) explains the device abstraction and file-reading interfaces, useful when comparing backend flexibility against platform-specific capabilities.
- **C1:** TCP reconstruction handles retransmissions, out-of-order fragments, missing data, bidirectional callbacks, and retained closed-connection state. Its options also bound out-of-order buffering and control cleanup work. The documented contracts in [TcpReassembly.h](https://raw.githubusercontent.com/seladb/PcapPlusPlus/master/Packet%2B%2B/header/TcpReassembly.h) make it possible to examine how a library exposes uncertainty and resource tradeoffs to callers.

### [mfontanini/libtins](https://github.com/mfontanini/libtins)

**C++ — Protocol data units, sniffing, packet construction, and TCP stream following.** Especially useful for engineers seeking an object-oriented protocol library with explicit stream-consumer behavior.

- **C2:** `StreamFollower` identifies connections and creates stream contexts with callbacks for client/server data and lifecycle events. Applications build their own consumers around a common reconstruction model. The [TCP streams tutorial](https://libtins.github.io/tutorial/tcp-streams/) demonstrates those interfaces and their relationship to packet input.
- **C1:** Stream termination is not dependent solely on seeing FIN or RST: timeout and excessive buffering can end tracking. The API distinguishes packet timestamps from wall-clock time, which matters for offline replay, and documents when callback data is cleared. The same [guide](https://libtins.github.io/tutorial/tcp-streams/) makes missed packets, retained data, and application ownership part of the contract.

### [secdev/scapy](https://github.com/secdev/scapy)

**Python — Packet construction, capture, dissection, and protocol experimentation.** Study its declarative packet language and bidirectional layer definitions, rather than judging it solely as an interactive utility.

- **C2:** Packet classes compose reusable field descriptors, payload layers, and layer-binding rules. The same definitions support construction and dissection, with distinct human, internal, and wire representations. The [protocol-development guide](https://scapy.readthedocs.io/en/latest/build_dissect.html) explains the machinery behind those abstractions.
- **C1:** Lengths, checksums, and discriminator fields depend on other fields or layers. Scapy resolves these through conversion hooks, field precedence, bindings, and `post_build` after payload construction. These are nontrivial serialization invariants, particularly when callers intentionally override defaults. Start with the build/dissect ordering and variable-length-field examples in [the guide](https://scapy.readthedocs.io/en/latest/build_dissect.html).

### [kbandla/dpkt](https://github.com/kbandla/dpkt)

**Python — Binary packet parsing and serialization.** A compact alternative for studying how a general packet base class supports a broad collection of protocol definitions with relatively little framework machinery.

- **C2:** A metaclass derives slots, struct formats, header lengths, and defaults from declarative header tuples. This moves repeated packet-layout work into a shared abstraction. The core [dpkt.py implementation](https://raw.githubusercontent.com/kbandla/dpkt/master/dpkt/dpkt.py) is the best starting point before reading individual protocols.
- **C1:** The same core checks bit-field layout against the containing struct width and generates masked/shifted field accessors with value-range checks. Explicit byte order and separate parsing/packing error types expose the numerical and malformed-input obligations underlying the convenient packet classes. Study the metaclass and field-property construction in [dpkt.py](https://raw.githubusercontent.com/kbandla/dpkt/master/dpkt/dpkt.py).

### [gopacket/gopacket](https://github.com/gopacket/gopacket)

**Go — Packet decoding, capture integrations, and TCP reassembly.** This is a **continuation fork of google/gopacket**, counted as one lineage here. Its separate evolution is supported by substantive decoder and capture fixes in the inspected [release history](https://github.com/gopacket/gopacket/releases), rather than by merely copying the original repository.

- **C1:** Reassembly has sequence-wrap arithmetic, gap/overlap information, capture metadata, and concurrency contracts around shared stream pools. The release history additionally records fixes for blocked capture shutdown and malformed packet decoders. Start with [tcpassembly.go](https://raw.githubusercontent.com/gopacket/gopacket/master/reassembly/tcpassembly.go).
- **C2:** `StreamFactory`, streams, assemblers, and shared pools separate application interpretation from flow state. Scatter/gather access allows consumers to inspect reconstructed data without always flattening it into a new buffer. The types and ownership comments in [the reassembly source](https://raw.githubusercontent.com/gopacket/gopacket/master/reassembly/tcpassembly.go) provide an instructive API-level study.

### [JulianSchmid/etherparse](https://github.com/JulianSchmid/etherparse)

**Rust — Typed parsing, slicing, and writing of Ethernet/IP/transport headers.** Its most distinctive study angle is the choice between strict decoding, borrowed views, and useful partial results from incomplete captures.

- **C1:** `LaxSlicedPacket` can preserve successfully parsed headers while returning the layer and error that stopped further parsing. It also records when captured length must stand in for an unusable declared length. The [lax-parser API](https://docs.rs/etherparse/latest/etherparse/struct.LaxSlicedPacket.html) explains these semantics rather than treating every short packet as equivalent.
- **C3:** Borrowed header slices and fully decoded structures offer different amounts of work; callers can extract only the fields they need. The [crate documentation](https://docs.rs/etherparse/latest/etherparse/) explains allocation behavior and separates ordinary parsing from facilities such as fragmentation that need additional storage. This supports studying selective decoding without inventing comparative speed figures.

### [rusticata/pcap-parser](https://github.com/rusticata/pcap-parser)

**Rust — Streaming PCAP and PCAPNG parsing.** A focused example of capture-format correctness and borrowed-buffer API design, particularly useful when a whole capture cannot fit in memory.

- **C1:** PCAPNG requires section-local state: interface descriptions and link types must be interpreted in the correct section, while incomplete input differs from final EOF. The [PcapNGReader API](https://docs.rs/pcap-parser/latest/pcap_parser/pcapng/struct.PcapNGReader.html) documents the state that consumers must track and how refill/consume operations interact.
- **C3:** The reader accepts a `Read` source and uses a circular buffer instead of loading an entire file. Borrowed blocks constrain when the buffer may move; `consume_noshift` makes that distinction explicit. A block must fit in the configured buffer, an important limitation explained in the same [reader documentation](https://docs.rs/pcap-parser/latest/pcap_parser/pcapng/struct.PcapNGReader.html).

## Classification, reconstruction, and specialized analyzers

### [ntop/nDPI](https://github.com/ntop/nDPI)

**C — Embeddable deep-packet-inspection and protocol-classification library.** Study how a passive classifier manages candidate dissectors and shared state across embedding applications.

- **C2:** Initialization separates global state from local detection modules, configuration, finalization, packet processing, and cleanup. Allocator hooks and selectable cache scope expose integration concerns that simple protocol recognizers omit. The [library initialization guide](https://www.ntop.org/guides/nDPI/library_initialization.html) is a substantive API entry point.
- **C3:** Candidate selection uses transport information and port-based prioritization while seeking additional evidence; detection stops after a result or configured limits. This limits repeated classification work. The [internals explanation](https://www.ntop.org/ndpi-internals-and-frequent-questions/) also distinguishes detection methods, helping readers avoid equating every classification with equally strong payload evidence.

### [cisco/mercury](https://github.com/cisco/mercury)

**C++ core with Python tooling — Passive protocol metadata extraction and fingerprinting.** The repository describes the project as **beta**. Its relevance is protocol parsing and metadata generation from captured traffic, not simply an application-identification label.

- **C2:** Fingerprints encode selected protocol structure as normalized parse trees, retaining meaningful ordering/nesting while excluding session-specific values. The [fingerprint design explanation](https://github.com/cisco/mercury/wiki/About-Mercury) describes this representation and the many-to-many relationship between fingerprints and applications; a fingerprint is not a unique identity proof.
- **C3:** The repository's architecture describes Linux AF_PACKET/TPACKETv3 capture with per-worker rings and independently processing workers, including explicit ring-memory and thread configuration. Pair that [repository architecture overview](https://github.com/cisco/mercury) with the fingerprint design to study acquisition parallelism feeding structured protocol extraction. No numerical throughput claim is adopted here.

### [simsong/tcpflow](https://github.com/simsong/tcpflow)

**C++ — TCP stream reconstruction into files and extracted artifacts.** Particularly useful for understanding the interaction between sequence-space reconstruction and filesystem resource management.

- **C1:** The stream writer tracks the next expected sequence number separately from the file position, handles out-of-order data, and treats bytes preceding an initially observed stream differently depending on whether a SYN was seen. Its source explicitly discusses reconstruction beyond the 32-bit sequence boundary. See [tcpip.cpp](https://raw.githubusercontent.com/simsong/tcpflow/master/src/tcpip.cpp).
- **C3:** Flow state survives closing an output file. Files can be reopened and sought back to the retained position as descriptor availability changes; packet indexes can be sorted at completion instead of maintained in order on every arrival. These are concrete resource and work-placement choices in [the stream/file implementation](https://raw.githubusercontent.com/simsong/tcpflow/master/src/tcpip.cpp), not evidence that every error path is flawless.

### [irontec/sngrep](https://github.com/irontec/sngrep)

**C/ncurses — SIP capture and call-flow inspection.** A useful specialist application for following the progression from packets to messages, dialogs, media metadata, and an interactive view.

- **C1:** Capture and presentation share mutable call state. The capture implementation uses synchronization and defers rotation work from a signal handler through a signal-safe flag, instead of doing file operations directly in that handler. See [capture.c](https://raw.githubusercontent.com/irontec/sngrep/master/src/capture.c).
- **C3:** Calls are indexed by Call-ID, while the message path performs retransmission checks and updates dialog state. Configured call limits trigger rotation that avoids removing locked calls, connecting resource management to UI/data lifetime. The [SIP implementation](https://raw.githubusercontent.com/irontec/sngrep/master/src/sip.c) makes those interactions visible; the limit should not be interpreted as an unconditional hard bound when calls cannot be evicted.

### [kismetwireless/kismet](https://github.com/kismetwireless/kismet)

**C/C++ with web and capture-helper components — Wireless capture and protocol/device analysis.** The repository identifies itself as an **official GitHub mirror**. Focus on the datasource and capture-helper architecture, including wireless-specific acquisition constraints.

- **C2:** Datasources expose consistent configuration and identity while capture helpers isolate device-specific acquisition. The repository includes multiple radio families; the [Wi-Fi datasource documentation](https://github.com/kismetwireless/kismet-docs/blob/master/readme/040-datasources_wifi.md) gives a concrete path through channel settings, monitor interfaces, and the Linux Wi-Fi helper.
- **C1:** Concurrent helpers must coordinate monitor-interface creation, for which the documented implementation uses a lockfile. Hardware and driver behavior can also produce misleading checksum information or false observations. The same [datasource guide](https://github.com/kismetwireless/kismet-docs/blob/master/readme/040-datasources_wifi.md) explains why capture fidelity depends on driver interfaces, channel configuration, and interpretation of device-supplied evidence.

### [emanuele-f/PCAPdroid](https://github.com/emanuele-f/PCAPdroid)

**Java and C — Android traffic capture, per-application analysis, and PCAP export.** Its non-root mode uses Android's VPN interface and a local transport proxy, which changes the interpretation of the resulting capture.

- **C1:** The proxy must emulate TCP behavior toward the app while opening separate upstream sockets. Sequence numbers, acknowledgements, windows, and synthesized headers therefore belong to the emulated connection. The [implementation explanation](https://github.com/emanuele-f/PCAPdroid/blob/master/docs/how_it_works.md) explicitly describes why remote segmentation and exact wire-level TCP behavior cannot be reconstructed from this mode.
- **C2:** Root and non-root acquisition, per-application connection analysis, export, and third-party capture integration support several Android observation workflows. Study the [repository's integration overview](https://github.com/emanuele-f/PCAPdroid) alongside the proxy design. The important limitation is concrete: non-root PCAP output is useful for application/protocol inspection, but is not a faithful recording of the original external TCP packets.

### [greatscottgadgets/packetry](https://github.com/greatscottgadgets/packetry)

**Rust/GTK4 — USB packet analysis with Cynthion capture and offline capture-file workflows.** This extends the selection beyond IP traffic with a substantive bus-protocol analyzer.

- **C1:** USB decoding uses explicit transaction states for continuation, retry, completion, failure, ambiguity, and invalid input. Rules differ for setup, data, handshakes, isochronous transfers, and split transactions; unknown endpoint information can preserve ambiguity. The [decoder state machine](https://raw.githubusercontent.com/greatscottgadgets/packetry/main/src/decoder.rs) is an excellent entry point for protocol correctness under partial knowledge.
- **C3:** Capture storage separates a single writer from cloneable readers, uses block-oriented packet data and compact indexes, and publishes shared metadata through synchronization-aware structures. The [capture storage implementation](https://raw.githubusercontent.com/greatscottgadgets/packetry/main/src/capture.rs) shows how live capture, reconstruction, and interactive navigation can share a growing dataset without representing every relationship as a heavyweight object.

## Search coverage and limitations

Discovery used more than six distinct live-web search formulations, followed by direct inspection of primary sources. The search angles included portable capture APIs; Linux packet rings and high-rate acquisition; full-packet indexing and retrieval; stateful TCP/application inspection; C++/Go reassembly libraries; Python packet-definition frameworks; Rust streaming and partial parsers; SIP/DNS specialists; wireless capture; encrypted-traffic metadata; Android VPN capture; eBPF/XDP observation; and USB/industrial protocol analysis. Later passes surfaced overlapping engines, frontends, wrappers, and instructional projects; the distinct XDP and USB designs were retained rather than stopping with the familiar desktop/network tools.

Each retained repository's GitHub page was opened, and at least one additional primary implementation, API, or design source was read. Links near the criteria identify the intended study entry points. The original google/gopacket and its continuation are not counted separately; neither are tools inside the xdp-tools or netsniff-ng monorepos. Wireshark and Kismet are identified as official mirrors, and Stenographer is explicitly historical/archived. No other maintenance claim follows merely from a repository being accessible.

Important exclusions include tutorials, awesome-lists, generated/thin wrappers, duplicate forks, general dataplane frameworks without a focused capture/analyzer subsystem, and deployment bundles whose distinct value is orchestration. The [DNS-OARC/dnscap repository](https://github.com/DNS-OARC/dnscap) states that it moved to Codeberg; it was excluded because a continuing substantive official GitHub mirror was not established. DNS remains represented inside the general protocol engines, rather than through a weak standalone addition. The specialist search is not a complete catalog of every industrial or radio protocol ecosystem.

This is a source-backed selection guide, not a benchmark, security audit, or uniform quality rating. Performance criteria refer to observable design decisions; no comparative speed figures were independently measured. Repositories were not cloned or executed, and dependencies were not installed. Default-branch and latest-documentation links can evolve after the research date. C4 is used only where the inspected history and testing process jointly support it; other projects need not satisfy C4 to qualify.
