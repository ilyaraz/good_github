# Firewalls and packet filtering engines

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing packet-filtering engines, stateful firewalls, application firewalls, inline prevention, and substantive libraries or controllers used to build them. Kernel and networking monorepos are counted once, with the relevant subsystem identified. Capture-filter compilers and policy controllers are explicitly distinguished from complete enforcement engines. The engineering assessments below are grounded judgments from the cited implementation and documentation, not security audits or claims that every component is exemplary.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, protocol or numerical semantics, adversarial input, and failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or models supporting multiple applications and configurations.
- **C3 — Performance:** concrete throughput, latency, memory, or scaling constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by evidence of compatibility work, testing, or complexity management. Age or recent activity alone does not qualify.

## Kernel and portable stateful engines

### 1. [torvalds/linux](https://github.com/torvalds/linux)

**Language/role:** C; Netfilter, particularly the nftables execution engine and flowtable acceleration, within the Linux kernel.

Study how a general rule interpreter coexists with a connection-oriented forwarding shortcut. The useful boundary is between interpreting a policy and preserving that policy's effects when subsequent packets bypass much of the stack.

- **C1:** `nft_do_chain()` selects an RCU-protected ruleset generation, interprets verdicts, and bounds its jump stack; payload evaluation checks packet extent and transport-header availability. These are concrete consistency and malformed-input concerns. Entry point: [nftables execution core](https://github.com/torvalds/linux/blob/master/net/netfilter/nf_tables_core.c).
- **C3:** Flowtables use a resizable hash table and retain NAT information, while fragments, TCP FIN/RST, and packets exceeding the MTU return to the conventional path. The documentation also explains asynchronous hardware offload and stale-cache limitations. Entry point: [flowtable architecture](https://github.com/torvalds/linux/blob/master/Documentation/networking/nf_flowtable.rst).

### 2. [openbsd/src](https://github.com/openbsd/src)

**Language/role:** C; PF kernel firewall in OpenBSD's official read-only Git conversion of its CVS source tree.

PF is valuable for studying the interaction of rule semantics, bidirectional connection state, normalization, and resource limits. This entry concerns OpenBSD PF; the FreeBSD entry below focuses on IPFW rather than counting another PF port.

- **C1:** The central packet path handles state references and locking, distinguishes unreassembled fragments, and treats ICMP state lookup separately from ordinary rule evaluation. Entry point: [PF implementation](https://github.com/openbsd/src/blob/master/sys/net/pf.c).
- **C2/C3:** A common rule language combines protocol/address matching with interface-bound or floating state, SYN proxying, and per-source state limits. Established flows can avoid ruleset evaluation, making state both a policy abstraction and a performance mechanism. Entry point: [official PF filtering guide](https://www.openbsd.org/faq/pf/filter.html).

### 3. [freebsd/freebsd-src](https://github.com/freebsd/freebsd-src)

**Language/role:** C; IPFW interpreter and dynamic-state machinery in FreeBSD's official publish-only source repository.

Study a kernel rule machine whose instruction evaluation interacts with packet ownership, fragmentation, credentials, and dynamically created connection entries. The monorepo also contains PF and IPFilter, but they are not additional selections here.

- **C1:** `ipfw_chk()` documents assumptions about mutable packet buffers and fragment offsets; its instruction implementations depend on those invariants. Entry point: [IPFW rule interpreter](https://github.com/freebsd/freebsd-src/blob/main/sys/netpfil/ipfw/ip_fw2.c).
- **C3:** The interpreter caches credential lookups to reduce repeated work and lock contention. Its separate dynamic-state implementation hashes flows, updates state counters, and coordinates expiration with rule-chain and bucket locking. Entry point: [dynamic states and expiration](https://github.com/freebsd/freebsd-src/blob/main/sys/netpfil/ipfw/ip_fw_dynamic.c).

### 4. [rmind/npf](https://github.com/rmind/npf)

**Language/role:** C99; portable NPF stateful-filter/NAT library, with configuration libraries and a DPDK integration example.

This is a useful smaller counterpart to whole-kernel trees: an embeddable engine with explicit connection-lifetime documentation. It is the standalone NPF repository, not a second listing of NetBSD's monorepo. Its visible default-branch head was dated July 2024; treat it as a quieter implementation study, without assuming current release support.

- **C1/C3:** Connections have forward and reverse keys, reference counts, background reclamation, an explicitly documented lock order, and an epoch-protected database access model. Entry point: [connection tracking implementation](https://github.com/rmind/npf/blob/master/src/kern/npf_conn.c).
- **C2:** The state model separates interface-bound tracking from global tracking and supports the same connection machinery for implicit return-traffic permission and NAT. Documentation explains the policy and spoofing consequences of `stateful-all`, rather than hiding them behind one switch. Entry point: [stateful-filtering semantics](https://github.com/rmind/npf/blob/master/docs/stateful.md).

## Programmable and accelerated datapaths

### 5. [facebook/bpfilter](https://github.com/facebook/bpfilter)

**Language/role:** C; a rule-to-eBPF compiler and program-lifecycle library with a CLI.

Study the construction of verifier-compatible filtering programs from a shared rule representation. The interesting architecture is the boundary between generic match logic and hook-specific preprocessing.

- **C1:** The generation contract assigns fixed roles to registers and keeps protocol identifiers in registers because older verifiers cannot reliably track the equivalent stack values. Unsupported protocol layers are explicitly excluded from later matching. Entry point: [program-generation contract](https://github.com/facebook/bpfilter/blob/main/src/libbpfilter/cgen/program.h).
- **C2:** A common runtime representation supports XDP, TC, Netfilter, and cgroup flavors. Dynamic packet pointers, header slices, aligned scratch storage, and pre-read socket fields let shared code work across different context-access restrictions. Entry point: [runtime layout and invariants](https://github.com/facebook/bpfilter/blob/main/src/libbpfilter/cgen/runtime.h).

### 6. [xdp-project/xdp-tools](https://github.com/xdp-project/xdp-tools)

**Language/role:** C; `xdp-filter` plus the reusable `libxdp` loader/dispatcher in a tools monorepo.

The filter deliberately offers a smaller matching vocabulary than Netfilter. Study it together with the dispatcher to understand how early packet drops and multiple independently loaded programs can coexist.

- **C1/C3:** Feature selection removes unnecessary matching work. The filter documentation also exposes a subtle lifecycle hazard: retained maps do not remember whether their entries were created under allow or deny policy, so changing policy can invert their meaning. Entry point: [xdp-filter behavior and lifecycle](https://github.com/xdp-project/xdp-tools/blob/main/xdp-filter/README.org).
- **C2:** `libxdp` represents programs through a common API and composes multiple XDP programs using a dispatcher, priorities, and chain-call actions built on `freplace`. Entry point: [libxdp architecture and API](https://github.com/xdp-project/xdp-tools/blob/main/lib/libxdp/README.org).

### 7. [gamemann/xdp-firewall](https://github.com/gamemann/xdp-firewall)

**Language/role:** C; configurable stateless XDP firewall and traffic-rate filtering system.

This is a more compact, operationally oriented engine than the kernel or distributed projects. Study the ordering of address blocks, expiry, protocol parsing, rate statistics, and rule evaluation. Its advertised stateless scope matters: rate/temporary-block state is not full TCP connection tracking.

- **C1:** The implementation checks header bounds before access, expires temporary block-map entries using a monotonic kernel timestamp, and constrains rule iteration for BPF execution. These checks expose the correctness demands of accepting raw packets; they are not proof of complete IPv6-extension or fragmentation handling.
- **C3:** Early map-based drops precede the configurable rule loop, while build-time switches remove optional filtering, rate-accounting, and logging work. The README explains the feature/performance tradeoff. Entry points: [packet program](https://github.com/gamemann/xdp-firewall/blob/master/src/xdp/prog.c) and [configuration and feature guide](https://github.com/gamemann/xdp-firewall/blob/master/README.md).

### 8. [FDio/vpp](https://github.com/FDio/vpp)

**Language/role:** C, with Python tests; the ACL plugin in the official GitHub mirror of VPP hosted at `git.fd.io`.

Study `src/plugins/acl`, rather than treating the entire switching/routing framework as a firewall. Its design records are particularly useful because they explain discarded arrangements and remaining tradeoffs.

- **C1:** The multicore design discusses rule-replacement races, session ownership, memory exhaustion, and the consequences of state-table limits. It includes historical unresolved alternatives; read it as engineering reasoning, not a guarantee that every described race is eliminated. Entry point: [ACL multicore design](https://github.com/FDio/vpp/blob/master/src/plugins/acl/acl_multicore_doc.rst).
- **C3:** The hash-lookup design groups rules by masks while preserving rule ordering, duplicate entries, port-range checks, and noninitial-fragment behavior. It makes the extra structures needed to accelerate an ordered ACL explicit. Entry point: [ACL hash-lookup design](https://github.com/FDio/vpp/blob/master/src/plugins/acl/acl_hash_lookup_doc.rst).

### 9. [DPDK/dpdk](https://github.com/DPDK/dpdk)

**Language/role:** C; the ACL packet-classification library within DPDK, an enforcement building block rather than a complete firewall.

The GitHub repository is a [replication of the project's main repository](https://mails.dpdk.org/archives/users/2021-October/005940.html). Study how a reusable classifier exposes enough layout information for aggressive optimization without fixing one packet format.

- **C2:** ACL contexts support user-defined fields, masks, ranges, category membership, and priority. Rule addition, runtime-structure construction, and packet classification are separate operations.
- **C3:** The documented implementation builds multibit tries, trades the number of tries against memory consumption, and offers scalar and several SIMD classifiers over the same runtime representation. Field-grouping restrictions are explained in terms of the unrolled search loop. Entry point: [ACL architecture, constraints, and API examples](https://github.com/DPDK/dpdk/blob/main/doc/guides/prog_guide/packet_classif_access_ctrl.rst).

## Distributed policy engines and firewall control libraries

### 10. [cilium/cilium](https://github.com/cilium/cilium)

**Language/role:** Go control plane and C/eBPF datapath; identity-based network policy and host/workload firewalling within Cilium.

Study the policy subsystem and packet path, rather than the project's unrelated observability features. It demonstrates how endpoint identities, transport-level matching, and optional application proxies meet in an executable policy.

- **C1/C2:** The policy implementation performs specific-identity and wildcard-identity lookups and resolves precedence, prefix specificity, deny decisions, and proxy redirection. The LPM policy-map representation makes these semantics concrete. Entry point: [datapath policy implementation](https://github.com/cilium/cilium/blob/main/bpf/lib/policy.h).
- **C3:** Packet-path documentation explains where socket-layer enforcement can avoid repeated endpoint-policy traversal after TCP establishment, while retaining the required L7 proxy path. Entry point: [life of a packet](https://github.com/cilium/cilium/blob/main/Documentation/network/ebpf/lifeofapacket.rst). This is development-branch documentation, not a claim about every released version.

### 11. [projectcalico/calico](https://github.com/projectcalico/calico)

**Language/role:** Go and C/eBPF; Felix policy calculation, reconciliation, and enforcement in the Calico monorepo.

Calico is especially useful for studying a firewall as an incremental distributed-state compiler. Focus on Felix's calculation graph, event sequencing, and dataplane managers.

- **C1:** Policy changes depend on other objects: Felix's event sequencer coalesces changes and orders IP-set updates before the policies referring to them. That dependency ordering is a concrete correctness problem during continuous reconfiguration. Entry point: [Felix architecture](https://github.com/projectcalico/calico/blob/master/felix/DESIGN.md).
- **C2/C3:** Shared manager/driver machinery supports multiple dataplanes. The BPF design explains host-versus-workload direction, TC placement relative to Netfilter, and XDP's role in dropping untracked hostile traffic earlier. Entry point: [BPF dataplane overview](https://github.com/projectcalico/calico/blob/master/felix/design/bpf-overview.md).

### 12. [firewalld/firewalld](https://github.com/firewalld/firewalld)

**Language/role:** Python; zone-based firewall policy daemon and backend controller, with kernel enforcement supplied by Netfilter.

Study the translation and lifecycle layer between applications, persistent configuration, runtime policy, and backend rule installation. This is substantive firewall orchestration rather than an independent packet interpreter.

- **C1:** The transaction class stages backend rule application, module handling, and pre/post/failure callbacks, with explicit propagation of backend failures. Its name should not be interpreted as a blanket guarantee of cross-backend atomic rollback. Entry point: [transaction implementation](https://github.com/firewalld/firewalld/blob/main/src/firewall/core/fw_transaction.py).
- **C2:** Zones model connection/interface trust, and runtime versus permanent configuration is a deliberate API distinction. The project also documents tests isolated in network namespaces, useful when studying reconfiguration without affecting the host. Entry point: [architecture scope and testing guide](https://github.com/firewalld/firewalld/blob/main/README.md).

### 13. [google/nftables](https://github.com/google/nftables)

**Language/role:** Go; independently implemented Netlink control library for Linux nftables. It is neither the upstream nftables project nor an official Google product.

This is a handwritten protocol implementation, not a generated binding or shell-command wrapper. Study how firewall objects become batched kernel messages and how replies are reconciled with requests.

- **C1:** Connection state is mutex-protected; batch flushing handles sequence-correlated replies and continues draining replies after an error. `FlushWithGenID` detects a concurrently changed ruleset through the generation ID. Entry point: [connection and batching implementation](https://github.com/google/nftables/blob/main/conn.go).
- **C2:** Set abstractions cover maps, intervals, concatenations, timeouts, dynamic updates, and key byte order, enabling many rule-generation applications. Entry point: [set model and encoding](https://github.com/google/nftables/blob/main/set.go). The README warns about API evolution; no API-stability claim is made here.

## Desktop and mobile application firewalls

### 14. [evilsocket/opensnitch](https://github.com/evilsocket/opensnitch)

**Language/role:** Go/C daemon and Python GUI; interactive Linux application firewall.

Study the separation of interception, userspace decisions, system rules, and the user interface. Its daemon is more interesting for this category than the presentation layer.

- **C1:** The NFQUEUE wrapper manages native handles, a protected queue registry, Go channels, packet-copy limits, and teardown paths. This exposes the concurrency and resource-lifetime problems at a C/Go/kernel boundary. Entry point: [NFQUEUE implementation](https://github.com/evilsocket/opensnitch/blob/master/daemon/netfilter/queue.go).
- **C2:** A common firewall interface covers interception, DNS/connection queueing, configuration serialization, system-rule management, and lifecycle operations for iptables and nftables backends. Entry point: [backend abstraction](https://github.com/evilsocket/opensnitch/blob/master/daemon/firewall/rules.go).

### 15. [safing/portmaster](https://github.com/safing/portmaster)

**Language/role:** Primarily Go, with native platform components; Windows/Linux application firewall and DNS-aware policy system.

Study process attribution and connection-level verdicts across two OS interception mechanisms. The repository also includes paid-product and privacy-network features; the relevant subsystem is `service/firewall`.

- **C1/C3:** Packet handling reuses an existing connection's handler or verdict, treats process-information-only events separately, and locks connection state during policy reevaluation. Fast-track handling for critical/internal connections makes the performance-versus-policy boundary visible. Entry point: [packet and verdict lifecycle](https://github.com/safing/portmaster/blob/development/service/firewall/packet_handler.go).
- **C2:** The architecture combines NFQUEUE on Linux and a WFP driver on Windows behind application policies, with distinct process-attribution mechanisms and a service/UI boundary. Entry point: [technical introduction](https://github.com/safing/portmaster/blob/development/README.md).

### 16. [henrypp/simplewall](https://github.com/henrypp/simplewall)

**Language/role:** C, with some C++; application firewall that programs Windows Filtering Platform directly.

Study WFP provider/sublayer/filter management and application-rule persistence. The project explicitly distinguishes itself from a UI controlling Windows Firewall.

- **C1:** Engine initialization handles Base Filtering Engine availability; provider and sublayer creation use transaction abort/commit paths and distinguish temporary from persistent objects. Entry point: [WFP implementation](https://github.com/henrypp/simplewall/blob/master/src/wfp.c).
- **C4:** The dated 2019–2026 changelog records profile-format changes, race fixes, UWP/service handling, Windows 7 compatibility fixes, loopback changes, and SDK updates. This is concrete compatibility and complexity management across years. Entry point: [changelog](https://github.com/henrypp/simplewall/blob/master/CHANGELOG.md).

### 17. [objective-see/LuLu](https://github.com/objective-see/LuLu)

**Language/role:** Objective-C; macOS outbound application firewall using a Network Extension filter.

Study how an interactive allow/block prompt becomes a safe flow lifecycle. The asynchronous interval between identifying an application, pausing related flows, and receiving the user's decision is the central engineering problem.

- **C1:** The filter handles a race where an alert has already been answered while a related flow is being queued; it removes and reevaluates that flow rather than leaving it paused without a future drain. Shutdown also resumes held flows. Entry point: [flow-verdict implementation](https://github.com/objective-see/LuLu/blob/master/LuLu/Extension/FilterDataProvider.m).
- **C2:** Rule storage separates signing identity or unsigned path from arrays of rules and code-signing flags; loading includes migration from the older rule format. This identity-centered model supports policy reuse across flows. Entry point: [rule storage and migration](https://github.com/objective-see/LuLu/blob/master/LuLu/Extension/Rules.m).

### 18. [M66B/NetGuard](https://github.com/M66B/NetGuard)

**Language/role:** Java and C/JNI; Android firewall using `VpnService` without root.

Study a mobile firewall that must mediate traffic through a userspace forwarding engine rather than install arbitrary kernel rules. Android's VPN-service constraints are part of the architecture.

- **C1:** The native TCP implementation tracks sequence/state transitions, sockets, forwarding data, and session expiration. A wrong transition can break permitted traffic just as readily as a wrong policy decision can permit unwanted traffic. Entry point: [native TCP handling](https://github.com/M66B/NetGuard/blob/master/app/src/main/jni/netguard/tcp.c).
- **C3:** The same implementation uses `epoll` socket events and scales session timeouts with occupancy. The Java service coordinates VPN and JNI lifetimes with network, metering, screen, and application changes. Entry point: [VPN service orchestration](https://github.com/M66B/NetGuard/blob/master/app/src/main/java/eu/faircode/netguard/ServiceSinkhole.java).

### 19. [celzero/rethink-app](https://github.com/celzero/rethink-app)

**Language/role:** Kotlin Android firewall/policy application integrating a separate Go `firestack` networking engine.

Study policy composition under changing device and network state. Its lineage includes Intra/Outline-related code, but its application firewall, rule managers, and split-routing behavior constitute substantial separate development; the external Go engine is not counted again here.

- **C1:** The firewall evaluator orders self-traffic handling, unknown/new applications, temporary permission, metered-network policy, and VPN-lockdown behavior. It also defines what happens when accessibility-based foreground detection is unavailable. Entry point: [TUN firewall evaluator](https://github.com/celzero/rethink-app/blob/main/app/src/main/java/com/celzero/bravedns/service/TunFirewallManager.kt).
- **C2:** A shared result model pairs rule identities with allow/block/stall actions and user-facing explanations across application, domain, IP, and network-state decisions. Entry point: [firewall rule/result model](https://github.com/celzero/rethink-app/blob/main/app/src/main/java/com/celzero/bravedns/service/FirewallRuleset.kt).

## Reusable filtering and compilation libraries

### 20. [basil00/WinDivert](https://github.com/basil00/WinDivert)

**Language/role:** C; WFP/WDF driver and userspace packet interception, filtering, modification, and reinjection API.

Study the kernel/userspace boundary of a firewall building block. The visible default-branch head is from April 2022, so this is a longstanding, quiet codebase rather than an assertion of current maintenance.

- **C1:** The API documentation explains injected-packet loops, checksum-offload flags, queue loss, and the requirement to preserve overlapped-I/O buffers until completion.
- **C2/C3:** A filter language and several interception layers support firewalls, NAT, and other packet applications. Selective interception and batched receive/send reduce copy and context-switch overhead; queue size/time and thread count remain explicit tradeoffs. Entry points: [architecture](https://github.com/basil00/WinDivert/blob/master/README) and [detailed API, performance, and failure semantics](https://github.com/basil00/WinDivert/blob/master/doc/windivert.html).

### 21. [the-tcpdump-group/libpcap](https://github.com/the-tcpdump-group/libpcap)

**Language/role:** C; portable capture-filter compiler and classic BPF evaluator. Capture filtering selects packets delivered to an application; it does not itself block those packets from traversing the host.

Study this as foundational filter-language and VM machinery, particularly the boundary between bytecode validation and runtime execution.

- **C1:** Instruction validation rejects invalid scratch-register indices, constant divide/modulo by zero, and oversized constant shifts. The implementation also distinguishes the unsafe legacy `bpf_filter` interface from length-aware filtering. Entry point: [BPF validation and evaluation](https://github.com/the-tcpdump-group/libpcap/blob/master/bpf_filter.c).
- **C4:** The changelog spans the 1994 releases through 2026, documenting platform fixes, filtering regressions, compiler/register issues, and build/test changes; the root documentation explicitly discusses binary compatibility. Entry point: [release and compatibility history](https://github.com/the-tcpdump-group/libpcap/blob/master/CHANGES).

### 22. [Igalia/pflua](https://github.com/Igalia/pflua)

**Language/role:** Lua/LuaJIT; packet-filter compiler/library originating in the Snabb ecosystem. **Historical:** its visible default-branch head is dated January 2017; it remains a useful compiler study, not a current-maintenance recommendation.

The repository explains a staged pipeline from filter syntax through lowered expressions, optimization, A-normal form, SSA, and generated Lua. Its alternative libpcap/BPF pipeline provides a useful semantic comparison.

- **C1:** The optimizer explicitly reconciles unsigned 32-bit filter arithmetic with Lua and signed bit operations, including clamping and multiplication behavior. Entry point: [optimizer and numerical semantics](https://github.com/Igalia/pflua/blob/master/src/pf/optimize.lua).
- **C3:** Optimization removes redundant tests and reasons about packet offsets before LuaJIT compilation. The test configuration compares optimized/unoptimized execution, alternative pipelines, and libpcap arithmetic through property tests and regressions. Entry point: [differential/property-test wiring](https://github.com/Igalia/pflua/blob/master/tests/Makefile). No historical headline speed claim is adopted here.

### 23. [cloudflare/cbpfc](https://github.com/cloudflare/cbpfc)

**Language/role:** Go; classic BPF to eBPF or C compiler for embedding packet predicates in larger programs.

Study translation between two related virtual machines where preserving behavior is insufficient unless the result also satisfies the target verifier.

- **C1:** Compilation builds control-flow blocks, initializes registers, inserts divide-by-zero and packet-access guards, and handles packet-offset restrictions. Entry point: [compiler and explicit limitations](https://github.com/cloudflare/cbpfc/blob/master/cbpfc.go).
- **C2:** The generated predicate is intended for embedding into a larger C/eBPF application, with both output forms sharing the preparation pipeline. The test backend runs classic BPF on a Unix datagram socket as an executable reference. Entry point: [kernel reference backend](https://github.com/cloudflare/cbpfc/blob/master/kernel_test.go).

## Inline inspection and prevention engines

### 24. [OISF/suricata](https://github.com/OISF/suricata)

**Language/role:** C and Rust; Suricata's inline IPS/filtering path, rather than passive monitoring alone.

Study how stream normalization, immediate blocking decisions, and parallel capture must agree. This broad inspection engine belongs here because its inline path actually permits, drops, rejects, or rewrites traffic.

- **C1:** IPS inspection uses a sliding TCP-data window and reconciles overlapping data with the first received bytes. Documented exception policies address parser failures and resource limits that could otherwise bypass rules. Entry point: [IPS behavior](https://github.com/OISF/suricata/blob/main/doc/userguide/ips/ips-concept.rst).
- **C3:** Worker mode gives each thread a complete packet pipeline, requiring both directions of a flow to reach the same worker in order. The capture guide explains why ordinary asymmetric NIC RSS can violate that assumption. Entry point: [capture and flow-affinity architecture](https://github.com/OISF/suricata/blob/main/doc/userguide/performance/packet-capture.rst).

### 25. [snort3/snort3](https://github.com/snort3/snort3)

**Language/role:** C++, with Lua configuration; extensible inline intrusion-prevention engine.

Study the transition from decoding and stream inspection to a concrete acquisition-layer verdict. The plugin architecture provides a different decomposition from fixed-function L3/L4 firewalls.

- **C1:** The analyzer distinguishes packets held for detection, retry-queued packets, injected replacements, and final DAQ verdicts. Correct ownership and finalization matter when inspection cannot finish immediately. Entry point: [packet analysis and verdict lifecycle](https://github.com/snort3/snort3/blob/master/src/main/analyzer.cc).
- **C2:** Versioned plugin APIs separate modules, codecs, inspectors, and policy scopes. The developer guide explains validated configuration, ownership transfer, and when stream/service/packet inspectors run. Entry point: [extension architecture](https://github.com/snort3/snort3/blob/master/doc/devel/extending.txt).

## Search coverage and limitations

Discovery used more than six distinct live-web formulations, including: Linux nftables/bpfilter engines; BSD PF/IPFW/NPF state tracking; eBPF/XDP and DPDK firewalls; Windows WFP and WinDivert; macOS and Android application firewalls; Lua/classic-BPF filter compilation; Kubernetes policy datapaths; and inline Suricata/Snort processing. Follow-up searches investigated Rust implementations, VPP ACLs, mobile policy engines, and official mirror provenance. Later searches mostly returned already-covered engines, small demonstration projects, wrappers, or forks without enough additional engineering evidence.

Every retained root URL was opened as a GitHub page or checked through the public GitHub API. Repository READMEs, independent source files, and design/API/test material were then read. The unauthenticated API rate limit was reached during metadata checks; public repository pages and raw source files supplied the remaining verification. No candidate code was executed, no repositories were cloned, and no dependencies were installed. Moving default-branch links identify inspected entry points; development documentation can describe behavior newer than a stable release.

The GitHub constraint creates a significant omission: upstream nftables, iptables, conntrack-tools, and related Netfilter userspace libraries are principally hosted at `git.netfilter.org`. The project's [current official mirror list](https://www.nftables.org/mirrors.html#git), including its newly announced mirror, points to `repo.or.cz`, not GitHub. Unofficial GitHub copies were therefore not substituted. Linux's actual nftables engine is covered in `torvalds/linux`; `google/nftables` is explicitly a separate control library.

Generic WAFs, browser blockers, DNS-only blockers, log-driven banning scripts, pure packet-capture utilities, and tutorial XDP filters were excluded unless they supplied a substantive engine or reusable filtering implementation. Firewall distributions and multiple copies of the same PF/NPF lineage were not added merely to increase the count. Rust discovery did not yield a stronger independently evidenced standalone selection than the retained set; language diversity was not used as a quota.

Official mirrors/conversions are labeled. The selected repositories did not display GitHub's archived flag/banner at inspection; that does not establish active maintenance. Quiet and historical examples are called out, with branch-head dates checked for [NPF](https://github.com/rmind/npf/commit/99f0756f5c7af1cfd0ff9e36257fc40281eab13f), [WinDivert](https://github.com/basil00/WinDivert/commit/97101072dbe31d744ca3429da389350a3df39e18), and [pflua](https://github.com/Igalia/pflua/commit/3c0b47078a24a0306e557af6063bc918e5897adb). C4 is awarded only where the inspected history supports it. Performance assessments concern mechanisms and tradeoffs, not independently reproduced benchmark results.
