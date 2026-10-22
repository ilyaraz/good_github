# Software switches and packet processing frameworks

Research date: **2026-10-09**.

This selection covers software forwarding engines, reusable packet I/O and processing libraries, graph-based network-function frameworks, P4 software targets, and programmable kernel dataplanes. It includes 24 repositories across C, C++, Rust, Go, Lua, Erlang, and P4/Python toolchains. The emphasis is on implementation ideas an experienced engineer can study: ownership, scheduling, protocol semantics, graph composition, and the relationship between abstractions and packet-processing cost. Dedicated traffic generators, SDN controllers, hardware-only targets, and general TCP/IP stacks are outside the main scope.

Criteria used below:

- **C1 — Difficult correctness:** invariants, concurrency, packet/protocol semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components serving different applications.
- **C3 — Performance with structure:** concrete treatment of throughput, latency, locality, allocation, or synchronization costs within an understandable design.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility, testing, or complexity-management evidence. Age or a recent push alone does not qualify.

Repository headings link to verified canonical GitHub locations. Linked implementation files and documents are reading entry points, not merely project descriptions. Criterion assignments are grounded engineering judgments, not certifications of correctness or production readiness. Historical status notes reflect the repository metadata and documentation inspected on the research date; an unarchived repository is not automatically actively maintained.

## Complete forwarding engines and OpenFlow switches

### [openvswitch/ovs](https://github.com/openvswitch/ovs)

**Language / role:** C; programmable multilayer virtual switch. A particularly useful study of how a coherent control-plane model interacts with cached forwarding decisions.

- **C1:** Flow modifications preserve a coherent pipeline for each packet, while cached datapath flows undergo asynchronous revalidation. OpenFlow bundles add transactional updates, including failure rollback. The distinction between logical atomicity and cache convergence is explained in the [switch design document](https://docs.openvswitch.org/en/latest/topics/design/).
- **C3:** The same design explains why translated datapath flows are cached and how revalidation reconciles that optimization with changing configuration; performance machinery is tied to explicit semantics.
- **C4:** The [NEWS history](https://raw.githubusercontent.com/openvswitch/ovs/main/NEWS) records successive 2024–2026 releases, supported DPDK versions, compatibility changes, deprecations, and removals. This is useful evidence of deliberate evolution, including the cost of retiring old platforms and interfaces.

### [FDio/vpp](https://github.com/FDio/vpp)

**Language / role:** C; vector packet-processing platform with switching, routing, and plugins. **Official GitHub mirror** of the FD.io repository. Study the VLIB execution engine underneath the many protocol implementations.

- **C2:** Registered nodes form a directed processing graph; input, internal, and cooperative-process nodes supply reusable execution abstractions. This provides a common runtime for forwarding features rather than a separate packet loop for each feature.
- **C3:** Nodes process vectors of packets, amortizing dispatch and improving instruction-cache reuse. Frames carry work between nodes, with cached frame allocation on graph arcs.
- **C1:** Cycles and self-enqueue complicate frame ownership. The documentation describes ownership transfer and the required pairing of frame acquisition and submission. These details make the [VLIB architecture guide](https://docs.fd.io/vpp/25.10/developer/corearchitecture/vlib.html) a strong starting point for understanding both speed and lifetime invariants.

### [lagopus/lagopus](https://github.com/lagopus/lagopus)

**Language / role:** C; OpenFlow software switch with DPDK and conventional packet I/O. **Historical study material:** the inspected repository's last push was in 2018.

- **C1:** The [OpenFlow datapath implementation](https://raw.githubusercontent.com/lagopus/lagopus/master/src/dataplane/ofproto/datapath.c) brings together action-set ordering, group selection, packet-field mutation, and byte-order handling. It also contains an explicit unresolved concern about modifying packets after output has been queued: useful evidence of a difficult ownership problem, not proof that every case is solved.
- **C3:** Its multicore DPDK forwarding architecture makes the boundary between OpenFlow operations and packet I/O visible, allowing readers to trace specification-level operations into the datapath.

The [test-writing guide](https://raw.githubusercontent.com/lagopus/lagopus/master/docs/how-to-write-tests-in-lagopus.md) explains Unity fixtures and generated test integration. Read it alongside the datapath to see how this codebase organized behavioral checks; the presence of tests does not establish current support.

### [FlowForwarding/LINC-Switch](https://github.com/FlowForwarding/LINC-Switch)

**Language / role:** Erlang; extensible OpenFlow software switch. **Historical:** the inspected repository's last push was in 2015. Especially interesting for a process-oriented architecture rather than a minimal polling loop.

- **C2:** Version-specific OpenFlow backends sit behind a common application structure. Logical switches, port processes, and backend APIs separate reusable switch machinery from protocol-version behavior.
- **C1:** Concurrent port/control messages, ETS-backed flow state, and the distinction between action lists and action sets expose real state-management and execution-order problems. Supervision and process boundaries provide an alternative way to organize those responsibilities.

The [LINC internals document](https://raw.githubusercontent.com/FlowForwarding/LINC-Switch/master/docs/LINC_internals.md) follows supervisors, logical switches, `gen_server` ports, and packet processing. The project explicitly values flexibility; it should not be selected on an assumed throughput advantage over the C dataplanes.

## Packet I/O foundations and portable dataplane libraries

### [DPDK/dpdk](https://github.com/DPDK/dpdk)

**Language / role:** C; packet I/O, memory, synchronization, and pipeline libraries. **Official GitHub mirror**, identified as such by the project's [testing infrastructure documentation](https://core.dpdk.org/testing/). Relevant subsystems here are rings and the Packet Framework/SWX pipeline, not every library in the monorepo.

- **C1:** The [ring library guide](https://doc.dpdk.org/guides/prog_guide/ring_lib.html) details producer/consumer ownership, bulk operations, and alternative synchronization modes. Relaxed-tail and head-tail synchronization address concrete problems such as preemption of a thread responsible for publishing progress.
- **C2:** The [Packet Framework guide](https://doc.dpdk.org/guides/prog_guide/packet_framework.html) defines interchangeable ports, lookup tables, and actions; SWX extends this to dynamically described headers and pipelines.
- **C3:** Burst interfaces, compact lookup results, and specialized queue synchronization make the cost of generality explicit. Study the library contracts before individual NIC drivers: they reveal assumptions inherited by many other projects in this report.

### [OpenDataPlane/odp](https://github.com/OpenDataPlane/odp)

**Language / role:** C; portable dataplane API and its Linux implementation. A useful counterpoint to frameworks that expose a single preferred I/O model.

- **C2:** Packet I/O supports direct access, queues, and scheduler-driven delivery through a common device lifecycle. Classification and traffic management can be composed with these modes rather than replacing the application model.
- **C1:** Thread-safety and ordering are explicit API choices. For example, an `MT_UNSAFE` receive queue cannot be concurrently consumed by multiple threads; scheduler modes distinguish parallel, atomic, and ordered execution.
- **C3:** Direct calls and scheduled queues offer different synchronization and distribution costs, while hash-based steering can keep a flow on one input queue.

Start with the substantial [packet I/O user guide](https://raw.githubusercontent.com/OpenDataPlane/odp/master/doc/users-guide/users-guide-pktio.adoc). Its configuration and lifecycle discussion is more useful for understanding portability constraints than a list of supported platforms.

### [luigirizzo/netmap](https://github.com/luigirizzo/netmap)

**Language / role:** C; shared-memory packet I/O, including the VALE software switch. VALE is counted as part of this repository, not as a second project.

- **C1:** Ring indices divide ownership between the kernel and userspace. The API specifies forward-only movement, an unused slot, buffer-change notification, and restrictions on fragmented packets. Ring sizes must not simply be assumed to be powers of two.
- **C2:** NICs, host-stack endpoints, VALE ports, pipes, and monitors share an interface, allowing the same processing loop to attach to different packet paths.
- **C3:** Preallocated memory-mapped buffers and batched synchronization reduce allocation and system-call work; buffer-index exchange supports avoiding payload copies where permitted.

The [netmap manual source](https://raw.githubusercontent.com/luigirizzo/netmap/master/share/man/man4/netmap.4) is the best entry point: it explains the actual ring contract, not just the kernel-bypass motivation.

### [larthia/nethuns](https://github.com/larthia/nethuns)

**Language / role:** C; portable packet I/O abstraction over backends including libpcap, netmap, AF_PACKET, and AF_XDP. A smaller project with a concrete reusable implementation rather than only language bindings.

- **C2:** The [public API implementation](https://raw.githubusercontent.com/larthia/nethuns/master/src/nethuns/api.h) presents a common socket, receive, release, send, and flush vocabulary. Backend selection lets applications retain that vocabulary while changing the underlying mechanism.
- **C1:** Received-packet identifiers and explicit release operations expose lifetime responsibilities. The [internal ring implementation](https://raw.githubusercontent.com/larthia/nethuns/master/src/nethuns/sockets/ring.h) uses acquire/release atomic operations around slot reuse; the relationship between packet lifetime and buffer availability is directly inspectable.
- **C3:** Inline operations and backend-specific packet headers keep the abstraction near the underlying rings. Study which details the common API can hide and which still affect application behavior; portability is not a promise of identical backend capabilities.

### [CloudNativeDataPlane/cndp](https://github.com/CloudNativeDataPlane/cndp)

**Language / role:** Primarily C, with language bindings; userspace packet-processing libraries built primarily on AF_XDP. Its kernel-driver-based deployment model is distinct from frameworks that supply their own PCI device drivers.

- **C2:** Nodes have process, initialization, teardown, and context interfaces; cloning creates instances for different ports or queues. Graph creation, inspection, and per-node statistics are reusable library operations.
- **C3:** The [graph library guide](https://cndp.io/guide/prog_guide/graph_lib.html) explains a graph per worker, burst processing, and an optimization that transfers an entire stream when packets share a next node, avoiding repeated pointer copying.
- **C1:** Those optimizations have explicit constraints: topology becomes fixed after graph creation, fast-path operations assume a single worker per graph, and divergent next-node decisions require a fallback path.

Study the graph subsystem and its packet-device nodes; the repository also contains a network stack, which is not the reason for its inclusion here.

## Composable packet graphs and modular routers

### [kohler/click](https://github.com/kohler/click)

**Language / role:** C++; modular router framework. **Historical baseline:** the inspected repository's last push was in 2022. Valuable for understanding the abstractions inherited or modified by later graph frameworks.

- **C2:** The [Element interface](https://raw.githubusercontent.com/kohler/click/master/include/click/element.hh) unifies push and pull processing, ports, tasks, timers, configuration, and optional live reconfiguration. Elements compose without forcing all modules into the same scheduling style.
- **C1:** The [Packet interface](https://raw.githubusercontent.com/kohler/click/master/include/click/packet.hh) makes sharing and writable access explicit through cloning and `uniqueify`. Copy-on-write, insufficient headroom, allocation failure, and header-annotation preservation interact in ways a simple packet struct would conceal.

An experienced engineer can compare the elegance of element composition with the ownership and execution contracts required to make it work. The source comments are particularly useful for learning which operations may copy or invalidate an existing packet reference.

### [tbarbette/fastclick](https://github.com/tbarbette/fastclick)

**Language / role:** C++; substantially evolved Click derivative for high-performance processing. Retained separately because batching, flow facilities, and later optimization integrations materially change the implementation and programming model.

- **C2:** `BatchElement` adds batch-aware push/pull interfaces while allowing configurations to cross boundaries between batch-capable and conventional elements. This is an instructive extension of an existing abstraction rather than a clean-slate replacement.
- **C3:** The [batching design guide](https://github.com/tbarbette/fastclick/wiki/Batching) explains batching modes, splitting and reconstruction, and template-based helpers that avoid per-packet virtual dispatch. The cost of mixing old and new element types remains visible.
- **C4:** The repository's project history traces the 2015 FastClick work through flow and PacketMill-related extensions in 2021. Read that history together with the documented compatibility machinery to study sustained expansion without requiring every existing element to adopt the new interface immediately.

### [NetSys/bess](https://github.com/NetSys/bess)

**Language / role:** C++ dataplane with Python configuration tooling; modular software switch framework. **Historical upstream snapshot:** the inspected repository's last push was in 2022; downstream forks are not counted separately here.

- **C2:** Ports connect devices or applications, while modules exchange packets through gates. The [BESS overview](https://github.com/NetSys/bess/wiki/BESS-Overview) explains the separation between the daemon, configuration interface, drivers, and processing modules.
- **C3:** Processing topology and CPU scheduling are distinct. A queue can break immediate downstream execution and create another task; hierarchical policies then allocate resources by cycles, packets, bits, or invocation count. The [scheduler guide](https://github.com/NetSys/bess/wiki/The-BESS-Scheduler) explains rate limits, weighted fairness, priorities, and blocked subtrees.

Study how packet graphs interact with a separate scheduling tree. This makes BESS particularly useful for reasoning about resource isolation and fairness, beyond simply connecting packet transformations.

### [snabbco/snabb](https://github.com/snabbco/snabb)

**Language / role:** Lua/LuaJIT with low-level support code; packet-processing toolkit with application graphs and direct device drivers. Useful for studying how a high-level implementation reaches hardware without hiding lifecycle problems.

- **C2:** Applications and links provide a common composition model for network functions and device-facing components, with packet-processing programs built within the same runtime.
- **C1:** The [Mellanox ConnectX driver](https://github.com/snabbco/snabb/blob/master/src/apps/mellanox/connectx.lua) documents a shared-queue state machine, prohibited transitions, and the ordering required to disable DMA before releasing resources. Control-process and I/O-process failure handling are first-class concerns.
- **C3:** Direct drivers and LuaJIT are coupled with explicit packet and queue machinery. The driver is a concrete place to examine how minimizing the runtime path increases responsibility for safe device teardown and shared-memory ownership.

This is not evidence that every driver has identical failure guarantees; the cited implementation is the selected case study.

### [outscale/packetgraph](https://github.com/outscale/packetgraph)

**Language / role:** C11; DPDK-based graph library for software network functions. **Archived by its owner on 2025-07-21.** Its documented dependency baseline is old, so treat it as an architectural study.

- **C2:** Network “bricks” compose switches, firewalls, interfaces, tunnels, and other functions. A graph executes synchronously on one core; explicit queue bricks connect graphs across threads.
- **C3:** The repository explains burst propagation without storing packets in ordinary links, separating the inexpensive local graph path from asynchronous boundaries.
- **C1:** The [queue brick implementation](https://raw.githubusercontent.com/outscale/packetgraph/master/src/queue.c) shows what those boundaries require: packet reference increments, dropping and freeing an old burst under queue pressure, paired endpoints, and draining on reset/destruction.

Study the queue code alongside the repository's graph model to understand where a seemingly simple compositional API acquires buffering, overload policy, and lifetime obligations.

## Network-function frameworks and language-based ownership

### [NetSys/NetBricks](https://github.com/NetSys/NetBricks)

**Language / role:** Rust with native packet-I/O support; research framework for composing and isolating network functions. **Historical research artifact:** the inspected repository's last push was in 2019.

- **C1:** Unique packet ownership makes forwarding an ownership transfer, preventing the sender from continuing to access that packet through the safe programming model. The safety argument depends on the framework and trusted low-level code; it is not a guarantee for arbitrary unsafe Rust.
- **C2:** Operators cover parsing, transformation, filtering, grouping, windows, and state partitioning, giving several network-function styles a shared vocabulary.
- **C3:** Same-core composition avoids process-boundary packet copying, while explicit cross-core distribution exposes a different cost.

The authors' [OSDI 2016 paper](https://www.usenix.org/system/files/conference/osdi16/osdi16-panda.pdf), especially the architecture and programming-model sections, is the substantive companion to the repository. It explains both the isolation model and the performance motivation without requiring the old build environment.

### [capsule-rs/capsule](https://github.com/capsule-rs/capsule)

**Language / role:** Rust over DPDK; network-function development framework influenced by NetBricks. **Historical dependency baseline:** the repository documents Rust 1.50 and DPDK 19.11, and its last inspected push was in 2022.

- **C2:** Packet types implement a shared trait with an associated enclosing packet type, supporting extensible protocol layering instead of an unstructured collection of byte-offset helpers.
- **C1:** The [packet trait implementation](https://raw.githubusercontent.com/capsule-rs/capsule/master/core/src/packets/mod.rs) distinguishes consuming parse operations from immutable peeking. An unsafe internal clone is deliberately kept away from the public interface because it shares mutable storage; implementations must enforce parsing invariants and bounds.

Study how ownership and associated types encode part of the packet model, and where validation still remains an implementation responsibility. The [packet API documentation](https://docs.rs/capsule/latest/capsule/packets/index.html) provides a map of the protocol types, but the source reveals the important safety boundary.

### [aregm/nff-go](https://github.com/aregm/nff-go)

**Language / role:** Go with a native DPDK fast path; Network Function Framework. **Canonical transferred location:** the former `intel-go/nff-go` URL redirects here. The inspected repository's last push was in 2022.

- **C2:** Applications assemble flows from receivers, handlers, splitters, and senders, separating packet-processing logic from the worker layout.
- **C3:** The [scheduler implementation](https://raw.githubusercontent.com/aregm/nff-go/master/flow/scheduler.go) adapts worker clones and uses receive-side scaling/RETA mappings to distribute incoming traffic. This is substantive runtime machinery beyond a Go wrapper around DPDK.
- **C1:** Worker changes require lifecycle coordination across Go and native execution. Atomic stop flags and acknowledgments precede releasing a core, and cloned flow contexts have explicit copy/delete responsibilities.

The scheduler is the most revealing entry point for studying the interaction between a declarative flow API, mutable deployment decisions, and a foreign-function execution boundary.

### [sdnfv/openNetVM](https://github.com/sdnfv/openNetVM)

**Language / role:** C; DPDK-based manager and library for network-function chains. A research-oriented system with separate management and NF execution responsibilities.

- **C2:** `NF_Lib` supplies lifecycle, packet handling, flow tables, service chains, and NF messaging. Packet metadata selects actions such as dropping, forwarding to another NF, or transmitting through a port.
- **C3:** Shared-memory queues and batching allow the manager and NFs to exchange packets without making each NF implement the complete I/O path.
- **C1:** The [NF development guide](https://github.com/sdnfv/openNetVM/blob/master/docs/NF_Dev.md) explains readiness signaling and the mutually exclusive managed-loop versus advanced ring-processing modes. Mixing their ownership responsibilities would be a correctness error.

Study the guide's transition from the basic handler to advanced ring access. Its shared-core scheduling section is explicitly experimental and not fully tested, so that feature should not be presented as an established production guarantee.

## P4 software-switch implementations and targets

### [p4lang/behavioral-model](https://github.com/p4lang/behavioral-model)

**Language / role:** C++; BMv2 programmable-switch behavioral model. A reference and testing implementation, not a production-throughput recommendation. The relevant subsystem is the reusable switch engine and its `simple_switch` target.

- **C2:** Parsers, match/action tables, and target-specific processing are separated so different switch architectures can reuse the underlying machinery.
- **C1:** The [simple_switch architecture document](https://github.com/p4lang/behavioral-model/blob/main/docs/simple_switch.md) specifies metadata behavior and the ordering of cloning, resubmission, multicast, dropping, and unicast decisions. Correctness depends on the combined pipeline semantics, not just individual table lookups.

An engineer can use this implementation to study how a programmable language becomes an executable packet-processing model, and why seemingly independent operations need an explicit priority order. The document also distinguishes the P4 architecture from control interfaces such as Thrift and the gRPC-enabled target.

### [P4ELTE/t4p4s](https://github.com/P4ELTE/t4p4s)

**Language / role:** Python compiler tooling, generated C, and C runtime for P4 software switches. **Experimental:** the repository documents language-feature limitations, including unsupported header-stack functionality.

- **C2:** The [compiler implementation](https://raw.githubusercontent.com/P4ELTE/t4p4s/master/src/compiler.py) generates switch code through a structured translation/template pipeline, separating P4-program logic from hardware-dependent runtime code.
- **C3:** The [DPDK runtime](https://raw.githubusercontent.com/P4ELTE/t4p4s/master/src/hardware_dep/dpdk/main.c) maintains per-core tables and parser state, receives bursts, invokes generated packet handling, and implements transmit/drop behavior. This makes the compiler/runtime boundary concrete.

Study how a general match/action description is lowered into a conventional high-performance packet loop. Inclusion is for the substantive software-switch runtime as well as the compiler; neither the presence of generated C nor successful compilation alone establishes complete P4 conformance.

### [p4lang/p4-dpdk-target](https://github.com/p4lang/p4-dpdk-target)

**Language / role:** C/C++; target driver and control infrastructure for running P4 pipelines on DPDK SWX. This is a distinct target implementation, counted separately from the underlying DPDK monorepo.

- **C2:** Its architecture separates the table-driven interface from pipeline, port, and device managers. Compiler-generated artifacts describe a program while the target machinery manages its runtime realization.
- **C1:** The [context-JSON implementation](https://raw.githubusercontent.com/p4lang/p4-dpdk-target/main/src/pipe_mgr/core/pipe_mgr_ctx_json.c) maps logical fields into match-key layouts using bit widths, offsets, positions, and byte-order metadata. Preserving these mappings is a concrete semantic obligation between compiler output and installed tables.

The [release notes](https://raw.githubusercontent.com/p4lang/p4-dpdk-target/main/RELEASENOTES.md) provide a capability boundary, including match types, action profiles/selectors, multiple pipelines, and unit-testing infrastructure. Read the context parser alongside the repository architecture to see why this is more than a generated API wrapper.

## Kernel-integrated programmable dataplanes

### [polycube-network/polycube](https://github.com/polycube-network/polycube)

**Language / role:** C++ control components and C/eBPF dataplanes; composable network services using Linux eBPF/XDP. **Historical snapshot caution:** the inspected repository's last push was in 2023.

- **C2:** “Cubes” expose a common model for dataplane ports, virtual connections, control logic, and management. YANG-described services share management infrastructure while supplying different packet behavior.
- **C3:** The [architecture introduction](https://polycube-network.readthedocs.io/en/latest/intro.html) explains kernel-resident fast paths, a userspace slow path for more complicated work, and the use of XDP for processing before later kernel networking costs are incurred.

Study how the framework joins fast-path code to service lifecycle and management rather than treating an eBPF program as an isolated packet filter. This is also a useful comparison with entirely userspace graph systems: execution and composition cross a kernel boundary, and the framework must provide more than a packet callback.

### [xdp-project/xdp-tools](https://github.com/xdp-project/xdp-tools)

**Language / role:** C; XDP utilities and reusable **libxdp** infrastructure. Inclusion is specifically for libxdp's dispatcher, attachment lifecycle, and AF_XDP facilities, not merely its command-line examples.

- **C2:** libxdp enables multiple independently developed XDP programs to share an interface and provides AF_XDP socket/UMEM helpers, avoiding repeated low-level attachment and buffer setup code in applications.
- **C1:** The [libxdp design/API document](https://raw.githubusercontent.com/xdp-project/xdp-tools/main/lib/libxdp/README.org) explains execution priorities, configurable chain-call return actions, and program/link references pinned in bpffs. Composition changes both control flow and object lifetime.
- **C3:** AF_XDP separates packet exchange through shared rings from higher-level application processing, while dispatcher behavior makes the overhead and ordering of composing several programs explicit.

Study the documented kernel-version and attachment constraints as part of the abstraction. A reusable API cannot erase the capabilities of the kernel on which it operates.

### [microsoft/xdp-for-windows](https://github.com/microsoft/xdp-for-windows)

**Language / role:** C; Windows programmable packet-processing and AF_XDP infrastructure. Offers a different operating-system implementation of ideas often encountered only through Linux examples.

- **C2:** The [architecture document](https://github.com/microsoft/xdp-for-windows/blob/main/docs/architecture.md) separates the XDP interface layer, program processing, AF_XDP sockets, and generic versus native integration. Network-interface capabilities and lifecycles are explicit framework concerns.
- **C3:** Shared-memory rings carry data between the kernel and userspace, while control operations use a separate path. Generic NDIS integration and native device integration expose different placement and performance tradeoffs within the same architecture.

Study the boundary between interface providers and packet consumers, including how applications discover and use capabilities. This project should not be read as a source-compatible implementation of Linux XDP: its Windows driver model, APIs, and integration points matter to the design.

## Coverage, search method, and limitations

Discovery used live web searches across more than six distinct angles: OpenFlow and virtual switching; Click-style graphs and vector execution; portable packet I/O and lockless rings; Rust ownership and Go flow runtimes; NFV managers and service chains; P4 reference switches and DPDK targets; Linux eBPF/AF_XDP and Windows XDP; and smaller frameworks such as Nethuns, CNDP, and Packetgraph. Follow-up searches pursued source trees, scheduler designs, buffer contracts, release histories, and original research papers. Later broad searches increasingly returned already-covered frameworks, educational drivers, wrappers, or adjacent applications.

Every retained canonical GitHub repository was opened, and each was paired with an additional primary source that was actually read. These included implementation files, project-maintained architecture/API documentation, and the NetBricks authors' paper. Repository pages supplied canonical-location and archive evidence; GitHub API metadata was additionally inspected for 22 of the 24 repositories. Packetgraph's archive banner was checked directly. Some GitHub document fetches failed through the web reader; public raw source files were read instead. Reading a raw copy of a README was not counted as independent implementation evidence.

The selection deliberately includes both established infrastructure and historical research systems, with status distinguished above. FastClick is retained separately from Click because its batching and later dataplane work constitute substantive separate evolution. VALE, VLIB, DPDK's Packet Framework/SWX, and libxdp are identified as subsystems and each monorepo is counted only once. NFF-Go uses its resolved canonical owner. VPP and DPDK are explicitly labeled official mirrors.

Excluded classes include tutorial-only drivers, awesome lists, thin bindings, duplicate forks, standalone traffic generators, control-plane-only SDN systems, and hardware-only switch targets. Full TCP/IP stacks and individual load balancers are adjacent to this category but were not used to inflate coverage. Research artifacts can be excellent sources of ideas without being suitable dependencies today; dated toolchains and experimental features are material limitations. No candidate code was executed, no performance claims were benchmarked, and this review did not audit every component or establish maintenance responsiveness. The list is a guide to substantive code and design material, not a ranking or a claim that each repository is uniformly exemplary.
