# Cellular radio access and core network stacks

Research date: **2026-10-09**.

This selection covers executable cellular radio-access and mobile-core implementations, their reusable protocol machinery, and substantial protocol test systems. It spans GSM/GPRS/EDGE, UMTS core interfaces, LTE/EPC, 5G NR/5GC, and an experimental CDMA2000 implementation. It includes complete systems and independently useful network functions; deployment recipes, modem-command wrappers, generic networking frameworks, and purely mathematical network simulators are outside the main selection.

The 24 repositories below were checked through their GitHub pages or public repository API, followed by architecture, implementation, or test material. Criteria are evidence-grounded engineering judgments, not certifications of correctness or production readiness. Public repository status does not establish active maintenance; mirrors, historical code, and experimental limitations are identified explicitly. Source links refer to the inspected branches and can change after this research date.

**Criteria legend**

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, hostile inputs, or failure recovery.
- **C2 — Abstractions:** substantial reusable interfaces or components that support multiple implementations, deployments, or procedures.
- **C3 — Performance:** concrete throughput, latency, timing, or resource constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or deliberate complexity management.

## Radio-access systems

### 1. [ocudu/ocudu](https://github.com/ocudu/ocudu)

**Language/role:** C++; full 5G CU/DU stack. **Official GitHub mirror** of the GitLab project and the continuation of srsRAN Project.

Study how protocol components remain independent of deployment-specific threading. The [threading model](https://docs.ocudu.org/dev_guide/architecture_guide/realization/threading_model/) describes injected executors, serializing strands, priority pools, and queues between control procedures and deadline-sensitive MAC work.

- **C1:** The [UE resource-grid allocator](https://github.com/ocudu/ocudu/blob/main/lib/scheduler/ue_scheduling/ue_cell_grid_allocator.cpp) coordinates downlink grants, HARQ acknowledgments, time-domain allocations, and repetition bundles; unsuitable bundles defer allocation instead of issuing a partial grant.
- **C2:** Executors and strands let the same protocol components use different worker arrangements and synchronous test executors.
- **C3:** Thread priorities, bounded parallelism, and nonblocking communication explicitly address slot deadlines and priority inversion.

The archived srsRAN Project is not counted separately. Its [transition announcement](https://www.srsranproject.org/press_releases/srsran_becomes_ocudu/) identifies GitLab as the development home; the linked GitHub repository identifies itself as a mirror.

### 2. [duranta-project/openairinterface5g](https://github.com/duranta-project/openairinterface5g)

**Language/role:** Primarily C, with C++ components; OpenAirInterface LTE/NR RAN and UE monorepo, now under Duranta. The relevant subsystems are `openair1`, `openair2`, `openair3`, and radio/fronthaul integration.

An especially useful study is the relationship between scheduling policy, scarce physical resources, and standardized functional splits.

- **C1:** The [MAC scheduler design](https://github.com/duranta-project/openairinterface5g/blob/develop/doc/MAC/scheduler-architecture.md) explains how uplink and downlink grants share CCE resources, how future uplink slots depend on K2, and why scheduling order can deny later allocations.
- **C2:** The [F1 split design](https://github.com/duranta-project/openairinterface5g/blob/develop/doc/F1AP/F1-design.md) reuses message handlers across monolithic and separated CU/DU deployments, substituting direct callbacks or ASN.1/SCTP transport.
- **C3:** Scheduling runs per slot through replaceable pipeline stages, with explicit resource budgets and short-circuit checks.

This entry counts the current RAN repository once, rather than counting its older organization mirror or research forks.

### 3. [srsran/srsRAN_4G](https://github.com/srsran/srsRAN_4G)

**Language/role:** C/C++; LTE suite containing srsUE, srsENB, shared radio libraries, and the lightweight srsEPC core. Separate codebase from the former 5G srsRAN Project.

Study a relatively cohesive end-to-end LTE implementation and the evolution of its scheduler and protocol boundaries.

- **C1:** The [MAC scheduler](https://github.com/srsran/srsRAN_4G/blob/master/srsenb/src/stack/mac/sched.cc) coordinates per-carrier scheduling, UE lifecycle, buffer reports, and HARQ feedback through synchronized access to shared UE state.
- **C2:** The suite shares protocol and PHY facilities across UE, base-station, and core applications, while the scheduler isolates carrier-specific work.
- **C4:** The [release changelog](https://github.com/srsran/srsRAN_4G/blob/master/CHANGELOG) records years of concrete complexity management: scheduler refactoring for multiple carriers, nonblocking RRC/NAS work, TTCN-3 conformance adaptation, ASN.1 updates, and newer-compiler fixes through release 25.10.

Treat its prototype 5G features according to the repository's stated scope; this is primarily the LTE selection.

### 4. [RangeNetworks/openbts](https://github.com/RangeNetworks/openbts)

**Language/role:** C++; GSM/GPRS radio-access node integrating cellular signaling with SIP services. **Historical reference**, not presented as a currently maintained deployment choice.

Study an architecture that routes GSM service control into SIP, with separate GSM, GPRS, control, transceiver, and messaging components. The [repository README](https://github.com/RangeNetworks/openbts/blob/master/README) supplies that module map and a detailed history of interoperability and runtime fixes.

- **C1:** The compact [RLC sequence-number implementation](https://github.com/RangeNetworks/openbts/blob/master/GPRS/RLC.cpp) makes modular ordering assumptions explicit and converts between radio-block numbering and GSM frame numbering. It is a concrete example of numerical semantics embedded in a protocol stack.
- **C2:** Separate control/SIP state machines and the TRX interface divide service integration from the radio implementation.

GitHub metadata did not mark the repository archived, but its last public push was in 2024 when checked. That is not evidence of ongoing support.

### 5. [chrismoos/1xbts](https://github.com/chrismoos/1xbts)

**Language/role:** Primarily Rust; experimental CDMA2000 1x and HRPD/EV-DO RAN and core, with a TypeScript management UI.

This is a useful contrasting architecture outside the usual GSM/LTE lineage. The [system overview](https://1xbts.org/docs/architecture/system-overview/) assigns ownership to BTS, BSC, MSC, PCF, PDSN, HLR, and SMSC, and distinguishes radio/control transports from management RPCs.

- **C1:** The [power-control implementation and tests](https://github.com/chrismoos/1xbts/blob/main/crates/cdma-bsc/src/lib/power_control.rs) handle measured radio quality, automatic and manual targets, frame-error estimates, and gain-control behavior. Tests exercise disabled adjustment and deadband cases.
- **C2:** Explicit node boundaries support a supervised single-host network or distributed nodes; 1x and HRPD have distinct radio paths that share packet-core services.

The project describes handset/backend-dependent support and incomplete production hardening. Inclusion recognizes substantive implementation and test material, not demonstrated carrier-grade reliability or years of maturity.

## GSM/GPRS and UMTS network functions

The following five repositories are **official Osmocom GitHub mirrors**. Development and review occur through Osmocom's own infrastructure, as stated by the [official mirror organization](https://github.com/osmocom). They are separate network functions with distinct implementations, not forks counted as independent projects.

### 6. [osmocom/osmo-bts](https://github.com/osmocom/osmo-bts)

**Language/role:** C; GSM BTS Layer 2 and higher, including RSL, OML, LAPDm integration, and multiple PHY backends. Official mirror.

Study how one BTS implementation supports device-node, Ethernet, and UDP-based radio interfaces. The [architecture chapter](https://github.com/osmocom/osmo-bts/blob/master/doc/manuals/chapters/architecture.adoc) distinguishes physical links, PHY instances, and logical transceivers.

- **C1:** The [shutdown FSM](https://github.com/osmocom/osmo-bts/blob/master/src/common/bts_shutdown_fsm.c) coordinates power ramp-down across transceivers, asynchronous radio closure, timeout fallback, and repeated shutdown requests. It must also close radios whose startup is still in progress.
- **C2:** A PHY link can expose one or several instances; mapping those instances to TRXs allows the upper-layer BTS code to serve different hardware arrangements.

Read the architecture together with the root README's backend-specific limitations; the abstraction does not imply identical capabilities or validation quality across radios.

### 7. [osmocom/osmo-bsc](https://github.com/osmocom/osmo-bsc)

**Language/role:** C; GSM base-station controller between BTS equipment and the mobile switching core. Official mirror.

The [handover state machine](https://github.com/osmocom/osmo-bsc/blob/master/src/osmo-bsc/handover_fsm.c) is a strong entry point for resource transfer and rollback across asynchronous protocol boundaries.

- **C1:** Handover checks that old and new logical channels belong to the expected connection, rejects corrupted state, and releases partially established resources. Intra-BSC and inter-BSC cases share an explicit procedure lifecycle.
- **C2:** The controller supports multiple BTS families through Abis and alternative core-facing A-interface arrangements; channel, subscriber-connection, media, and handover state machines separate responsibilities. The [project overview](https://github.com/osmocom/osmo-bsc/blob/master/README.md) documents these interfaces and the split from the earlier all-in-one OpenBSC architecture.

Engineers can study how a long-lived call remains consistent while the radio and media endpoints change underneath it.

### 8. [osmocom/osmo-pcu](https://github.com/osmocom/osmo-pcu)

**Language/role:** C/C++; GPRS/EDGE packet control unit implementing radio RLC/MAC and adapting to BSSGP/NS toward an SGSN. Official mirror.

Study acknowledged radio delivery under small windows, changing coding schemes, and intermittent acknowledgments. The [downlink temporary-block-flow implementation](https://github.com/osmocom/osmo-pcu/blob/master/src/tbf_dl.cpp) exposes these mechanisms directly.

- **C1:** It distinguishes stalled windows, unacknowledged blocks, retransmission cycles, final-block repeats, and creation of new block sequence numbers. Getting these transitions wrong can lose data or prevent a flow from completing.
- **C2:** Shared TBF machinery handles GPRS and EGPRS coding and flow state while the PCU boundary adapts radio operations to the SGSN-facing protocol stack.

The [overview](https://github.com/osmocom/osmo-pcu/blob/master/README.md) explains BTS- and BSC-colocated arrangements and configuration propagation. It also lists unsupported modes, so this is not a claim of complete GPRS feature coverage.

### 9. [osmocom/osmo-msc](https://github.com/osmocom/osmo-msc)

**Language/role:** C; 2G/3G mobile switching center with mobility, call control, messaging, and visitor-location functions. Official mirror.

The [VLR authentication FSM](https://github.com/osmocom/osmo-msc/blob/master/src/libvlr/vlr_auth_fsm.c) is a particularly readable study of authentication policy embedded in network state.

- **C1:** Authentication tracks tuple reuse counts, chooses eligible vectors, distinguishes GSM and UMTS responses, and associates waiting states with protocol timers and failure outcomes.
- **C2:** The [interface overview](https://github.com/osmocom/osmo-msc/blob/master/README.md) separates A/IuCS radio access, MGCP media control, GSUP subscriber services, and MNCC external call control. The same switching core can therefore integrate with different access and service components.

The engineering interest lies in preserving subscriber and call state across several independent interfaces, rather than in treating the MSC as a single request/response server.

### 10. [osmocom/osmo-sgsn](https://github.com/osmocom/osmo-sgsn)

**Language/role:** C; serving GPRS support node for GPRS/EDGE and UMTS packet service. Official mirror.

Study mobility state shared across different radio access paths. The [GMM state machine](https://github.com/osmocom/osmo-sgsn/blob/master/src/sgsn/gprs_gmm_fsm.c) defines allowed event/state masks and explicitly handles retransmitted attach initiation and duplicate completion events.

- **C1:** Registered, suspended, deregistered, and common-procedure states must remain coherent despite repeated messages and explicit or implicit resumption. The implementation also exposes unfinished transitions, useful for understanding actual coverage limits.
- **C2:** The [project interface map](https://github.com/osmocom/osmo-sgsn/blob/master/README.md) combines Gb access, IuPS access, GTP toward a GGSN, and GSUP subscriber integration. The GMM layer connects to access-specific mobility FSMs instead of duplicating the whole node per radio family.

This complements the MSC entry by exposing packet mobility and session-management concerns.

## Mobile cores and gateway control planes

### 11. [open5gs/open5gs](https://github.com/open5gs/open5gs)

**Language/role:** C; EPC and 5G core monorepo. Relevant subsystems include MME/AMF, SMF, gateways/UPF, subscriber functions, and shared signaling libraries.

Study how one codebase implements both EPC control/user-plane separation and 5G service-based control functions. The [architecture introduction](https://open5gs.org/open5gs/docs/guide/01-quickstart/) explains function boundaries, discovery, and physically separated user planes.

- **C1:** The [AMF mobility state machine](https://github.com/open5gs/open5gs/blob/main/src/amf/gmm-sm.c) coordinates NAS messages, timers, and service-based responses. Its failure path can restore a saved UE context or enter an exception state, making transaction rollback a visible design concern.
- **C2:** Separate network functions and common framework facilities support multiple core generations and deployment layouts; SMF/UPF responsibilities bridge the EPC and 5GC organization.

This is a strong choice for following a real registration procedure from decoded signaling through subscriber/session state and downstream function calls.

### 12. [free5gc/free5gc](https://github.com/free5gc/free5gc)

**Language/role:** Primarily Go; 5G core integration superproject with substantial protocol integration tests. Network-function implementations are linked submodules, rather than all residing directly in this repository.

Study executable expectations across an entire service-based core. The [registration test suite](https://github.com/free5gc/free5gc/blob/main/test/registration_test.go) drives real NGAP/NAS exchanges, verifies message types, derives authentication responses, and checks later procedure steps.

- **C1:** Tests include duplicate registration, authentication resynchronization, abnormal PDU-session release, Xn/N2 handover, paging, multiple sessions, and multi-AMF/NAS-reroute cases. These expose cross-function correctness beyond the happy path.
- **C2:** The [submodule map](https://github.com/free5gc/free5gc/blob/main/.gitmodules) separates AMF, SMF, authentication, discovery, policy, subscriber, user-plane, and access-interworking functions; the test harness supplies a reusable integration boundary across them.

Counted once for the assembled core and its own substantive tests. The separately listed `gtp5g` is a reusable kernel dataplane implementation, not another count of the same Go core.

### 13. [magma/magma](https://github.com/magma/magma)

**Language/role:** C++, Go, and Python; mobile-core platform spanning access gateway, federation gateway, and cloud management. The access-gateway service architecture is the main study target here.

The [AGW architecture document](https://github.com/magma/magma/blob/master/docs/readmes/lte/architecture_overview.md) describes `magmad`, `sctpd`, mobility, session, policy, subscriber, and packet-pipeline services, including restart consequences.

- **C1:** In stateless mode, a separate SCTP termination service preserves RAN connections through application-service restarts. The document identifies which failures force other services to restart and which affect user service.
- **C2:** Session lifecycle and credit/rule state are separated from policy distribution and OVS programming. Federation and orchestration provide further boundaries for connecting an access network to an existing operator core.

Study the ownership and recovery implications of decomposing a core into cooperating services. Repository availability and documentation alone do not establish the current operational support level of every subsystem.

### 14. [travelping/ergw](https://github.com/travelping/ergw)

**Language/role:** Erlang; GGSN/PDN-gateway control plane using control/user-plane separation. **Historical public implementation:** GitHub metadata showed its last public push in 2022, without an archive flag.

The [context-dispatch implementation](https://github.com/travelping/ergw/blob/master/apps/ergw_core/src/ergw_context.erl) shows a different concurrency model from the C and Go cores: handler callbacks, process-based dispatch, registered session contexts, and admission queues.

- **C1:** Incoming requests are associated with contexts and retransmission status; missing contexts and handler exceptions produce protocol errors, while admission resources are released in an `after` block.
- **C2:** Callback-driven context handlers and separate GTP/PFCP integration allow gateway behavior to share infrastructure while using an external user plane.
- **C4:** [Release notes from 2016–2021](https://github.com/travelping/ergw/blob/master/NEWS.md) document protocol fixes, dependency compatibility, and an application/configuration split, rather than merely showing an old creation date.

Use it to study Erlang telecom architecture, with its historical dependency and feature limitations in mind.

## User-plane implementations

### 15. [omec-project/upf](https://github.com/omec-project/upf)

**Language/role:** Go PFCP agent and C++ BESS dataplane, with Python tooling/tests; 4G/5G UPF used in the Aether/SD-Core ecosystem.

Study translation from standardized PFCP rules into a programmable forwarding implementation. The current repository includes BESS under `bess/`; it is counted as one integrated codebase here.

- **C2:** The PFCP agent uses a common datapath abstraction to separate control-plane messages from backend-specific configuration. The [UPF state implementation](https://github.com/omec-project/upf/blob/main/pfcpiface/upf.go) combines that boundary with UE address allocation, tunnel identifiers, slice parameters, reporting, and response timers.
- **C3:** The repository describes DPDK, AF_PACKET, and AF_XDP packet-I/O modes alongside per-flow measurements and rate controls, making performance choices visible in the design.

The [developer guide](https://github.com/omec-project/upf/blob/main/docs/developer-guide.md) explains how BESS changes, protobuf consumers, architecture-specific builds, and integration tests are coordinated. This is useful for studying the control-plane/dataplane contract without assuming every possible backend remains supported.

### 16. [travelping/upg-vpp](https://github.com/travelping/upg-vpp)

**Language/role:** C dataplane with Go integration tests; GTP-U UPF/PGW-U/TDF-U implemented as an out-of-tree VPP plugin.

Study session updates that cross from control processing into worker-owned packet state.

- **C1:** The [multithreading interface](https://github.com/travelping/upg-vpp/blob/master/upf-plugin/upf/utils/upf_mt.h) gives create/update/delete requests and responses explicit session, rule, and procedure identifiers, and separates usage/session reports in the reverse direction.
- **C2:** The plugin boundary supplies cellular forwarding functions within VPP, while the event API isolates inter-thread transport from session operations.
- **C3:** Worker event rings are cache-line separated and synchronized explicitly. The [pool-claim helper](https://github.com/travelping/upg-vpp/blob/master/upf-plugin/upf/utils/pool_claim.h) tracks ownership of objects allocated from shared pools and asserts allocation/free invariants.

The root and plugin feature summaries differ in detail; capabilities such as QoS and buffering should be checked against the exact revision. No quantitative throughput claim is made here.

### 17. [free5gc/gtp5g](https://github.com/free5gc/gtp5g)

**Language/role:** C; Linux GTP-U kernel module with PFCP-style packet-detection, forwarding, and QoS rules.

Study how mobile-core rule semantics meet kernel packet buffers and routing. The [encapsulation/forwarding implementation](https://github.com/free5gc/gtp5g/blob/master/src/gtpu/encap.c) contains header-length checks, optional GTP extension handling, PDR lookup, and RCU-accessed rule pointers.

- **C1:** Packet-buffer lifetime, malformed/truncated headers, and forwarding-action combinations are concrete correctness concerns. Comments explicitly document an accounting use-after-free hazard and the required exclusivity of forwarding actions.
- **C2:** A configurable kernel dataplane applies PDR/FAR/QER-style rules independently of the higher-level core implementation; it also supports different endpoint roles in lookup logic.

The [README](https://github.com/free5gc/gtp5g/blob/master/README.md) documents kernel API compatibility guards, DKMS integration, and rule inspection. Kernel-version support is revision-specific; those notes should be read before using the module.

## Shared cellular protocol machinery

### 18. [osmocom/libosmocore](https://github.com/osmocom/libosmocore)

**Language/role:** C; common libraries for cellular signaling, message buffers, timers, event loops, codecs, control interfaces, and channel coding. Official Osmocom mirror.

This is the foundational abstraction study behind several independently listed network functions. The [library map](https://github.com/osmocom/libosmocore/blob/master/README.md) identifies the cellular-specific sublibraries rather than treating the repository as a generic utility collection.

- **C1:** The [FSM implementation](https://github.com/osmocom/libosmocore/blob/master/src/core/fsm.c) constrains allowed input events and transitions, associates protocol timers with state changes, and manages cascading termination with deferred deallocation machinery.
- **C2:** Static FSM descriptions are separated from per-procedure instances, private context, and per-instance logging. The same machinery supports many simultaneously existing subscriber procedures and network functions.

Study how explicit state and lifetime rules replace scattered implicit state machines, while remaining usable in a C event-driven codebase.

### 19. [wmnsk/go-gtp](https://github.com/wmnsk/go-gtp)

**Language/role:** Go; GTP protocol library for mobile-core nodes and test tools. The project explicitly labels its APIs experimental.

Study a reusable protocol stack that includes connection, session, bearer, and tunnel-identifier machinery rather than only packet serialization.

- **C1:** The [GTPv2 connection implementation](https://github.com/wmnsk/go-gtp/blob/main/gtpv2/conn.go) documents the outstanding-request sequence-number uniqueness invariant, manages shared state with synchronization, and handles receive-buffer ownership before concurrent message dispatch and cancellation.
- **C2:** A `net.PacketConn`-like API, registered message handlers, and session/TEID helpers let callers implement different gateway roles without embedding a single fixed network application.

The [GTPv2 guide](https://github.com/wmnsk/go-gtp/blob/main/gtpv2/README.md) is the second entry point for connection and message handling. Coverage differs across GTP versions; do not infer complete GTPv0, GTPv1-C, or GTP-prime implementations from the repository name.

### 20. [wmnsk/go-pfcp](https://github.com/wmnsk/go-pfcp)

**Language/role:** Go; PFCP message and information-element library for EPC/5GC control/user-plane separation. Experimental API; association lifecycle, message delivery, and session management are deliberately left to callers.

- **C1:** The [information-element implementation](https://github.com/wmnsk/go-pfcp/blob/main/ie/ie.go) handles declared lengths, vendor-specific enterprise identifiers, recursive grouped elements, and truncated input. It also documents that parsing retains references to the input buffer, exposing an important ownership contract.
- **C2:** The [message interface and parser](https://github.com/wmnsk/go-pfcp/blob/main/message/message.go) provide common marshaling, sequence, session-ID, and request-inspection operations across concrete PFCP message types.

Study the tradeoff between a reusable wire-format layer and application-owned transaction semantics. Its separation from `go-gtp` is substantive: PFCP configures forwarding behavior between control and user planes, whereas GTP covers different mobile-core signaling and tunnel protocols.

### 21. [pycrate-org/pycrate](https://github.com/pycrate-org/pycrate)

**Language/role:** Python; protocol description/codec framework with ASN.1 and CSN.1 support and a 3G/LTE experimental core. Relevant subsystems are `pycrate_mobile`, ASN.1 support, and `pycrate_corenet`.

The [current project overview](https://github.com/pycrate-org/pycrate/blob/master/README.md) identifies the new organization as the maintenance home since 2024; the archived P1sec repository is not counted separately.

- **C1:** The [signaling-procedure framework](https://github.com/pycrate-org/pycrate/blob/master/pycrate_corenet/ProcProto.py) interprets mandatory elements, unknown extensions, message criticality, and protocol outcomes. Its comments describe where real peers deviate from assumptions about ASN.1 criticality.
- **C2:** Common link-signaling and NAS procedure classes derive handling from protocol descriptions and allow per-element decoder/encoder overrides, supporting multiple cellular protocols without duplicating their scaffolding.
- **C4:** The overview records a 2017 origin together with later Python compatibility decisions, including the final Python 2 release and cross-platform testing—not age alone.

This is particularly useful for understanding protocol structure and interoperability; its Python core is not presented as a throughput-oriented carrier dataplane.

## Executable UE/RAN and network-function test systems

### 22. [aligungr/UERANSIM](https://github.com/aligungr/UERANSIM)

**Language/role:** C++; executable 5G UE and gNB simulator for exercising mobile cores. The radio link is simulated over UDP, not a complete NR PHY/MAC/RLC/PDCP implementation.

- **C1:** The [UE registration procedures](https://github.com/aligungr/UERANSIM/blob/master/src/ue/nas/mm/register.cpp) reject messages incompatible with current mobility state, coordinate backoff and procedure timers, validate registration results, and clear temporary authentication material.
- **C2:** The [interface description](https://github.com/aligungr/UERANSIM/wiki/Feature-Set) separates UE-owned NAS, gNB-owned NGAP, and the GTP user plane, allowing actual core-facing signaling to be tested without physical radio hardware.

Study the UE side of the same state transitions implemented in AMFs, including abnormal registration and service-request interactions. The feature wiki is older than current code; use it for the interface model, and inspect the selected revision for exact feature coverage.

### 23. [HewlettPackard/PacketRusher](https://github.com/HewlettPackard/PacketRusher)

**Language/role:** Go with eBPF/kernel integration; multi-UE/gNB control- and user-plane load testing and scenario execution. It derives from my5G-RANTester and reuses free5GC libraries, but has substantive separate tunnel, runtime-control, and testing work; the ancestor is not counted separately.

The [current README](https://github.com/HewlettPackard/PacketRusher/blob/main/README.md) explains eBPF, gtp5g, and userspace backends, shared socket/file-descriptor implications, and tunnel changes during handover.

- **C1:** The [changelog](https://github.com/HewlettPackard/PacketRusher/blob/main/CHANGELOG.md) documents fixes for per-UE message ordering, rapid registration/deregistration races, AMF association loss, and packets still arriving at the source gNB after handover.
- **C2:** Runtime UE controls and sequenced JSON scenarios provide reusable building blocks for mobility and session experiments.
- **C3:** Alternative tunnel backends expose different kernel/userspace and per-UE resource costs. These are concrete performance design choices; published throughput figures are not treated here as independently verified benchmarks.

### 24. [osmocom/osmo-ttcn3-hacks](https://github.com/osmocom/osmo-ttcn3-hacks)

**Language/role:** Primarily TTCN-3 test logic, with C/C++ support and Python orchestration; functional cellular network-element test suites. Official Osmocom mirror. Despite its name, this is substantial reusable testing infrastructure.

Study tests that replace several network peers around a real implementation under test. The [BSC suite](https://github.com/osmocom/osmo-ttcn3-hacks/blob/master/bsc/BSC_Tests.ttcn) emulates BTS/mobile and MSC sides, verifies handover behavior and counters, and uses guard timers.

- **C1:** Concurrent peer behavior, channel transitions, encryption parameters, procedure timeouts, and post-procedure cleanup make correctness observable at protocol boundaries.
- **C2:** The suite distinguishes raw codec-port tests from handler-mode tests that abstract SCCP/channel multiplexing; shared protocol libraries support multiple network-function suites.

The [test-system overview](https://github.com/osmocom/osmo-ttcn3-hacks/blob/master/README.md) explains suite organization and execution against different implementation versions. This entry is a companion for studying stack validation, not a deployable core or base station.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, including: complete LTE/NR SDR stacks; EPC/5GC cores; official Osmocom GSM/GPRS mirrors; BESS/VPP/eBPF UPFs; Erlang gateway and Go GTP/PFCP implementations; UE/gNB simulators and load testers; Python cellular codecs/cores; Rust and non-GSM cellular stacks; and targeted NB-IoT and UMTS searches. Candidate discovery was followed by direct GitHub metadata, source-file, architecture-document, and test inspection. Later narrow searches mainly repeated known implementations or found modem wrappers, deployment recipes, simulation models, and lightly differentiated forks, giving diminishing returns for this scope.

Important selection decisions:

- **Moves and mirrors:** OCUDU's official substantive GitHub mirror replaces the archived srsRAN Project entry. Duranta is the current OpenAirInterface RAN home. Pycrate's current organization replaces its archived predecessor. Osmocom mirrors are retained because the official organization still exposes substantive implementations.
- **No multiplication of one system:** OpenAirInterface, Magma, Open5GS, and the assembled free5GC core each count once. OMEC's now-integrated BESS source is not counted as another repository. Components are separate entries only when they offer distinct, reusable implementations, as with the Linux `gtp5g` module.
- **Adjacent exclusions:** General-purpose VPP/BESS, Wi-Fi/LoRa stacks, SIM-programming utilities, awesome-lists, deployment-only bundles, and statistical ns-3/NB-IoT models were not retained. FlexRIC searches did not establish an official substantive GitHub home to the same standard, so third-party mirrors were not substituted. O-RAN controller software and IMS/SIP infrastructure are not comprehensively covered.
- **Coverage limits:** UMTS is represented mainly through core interfaces and signaling machinery; the historical OpenBTS-UMTS repository was discovered but not retained as another fully verified entry. Closed modem/baseband firmware and non-GitHub implementations are outside the selection. The Rust CDMA2000 entry supplies architectural diversity but is explicitly experimental.
- **Evidence limits:** GitHub's unauthenticated API rate limit interrupted some recursive tree enumeration; repository identities/status had already been checked, and direct GitHub tree pages and raw source files supplied the remaining evidence. No candidate was cloned, installed, built, or executed. Tests described here were inspected, not run. Performance and production-use statements are not independently benchmarked, and the existence of tests is not proof that every component is correct.

This is a selection guide to useful engineering material. The criteria identify concrete areas worth studying within each codebase, rather than asserting that every subsystem is uniformly exemplary.
