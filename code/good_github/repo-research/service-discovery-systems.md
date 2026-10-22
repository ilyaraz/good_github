# Service discovery systems

Research date: **2026-10-09**

This report selects **23 GitHub repositories** implementing service registries, discovery clients and bridges, DNS-based discovery, decentralized membership used for discovery, and local-network mDNS/DNS-SD. It includes complete systems and substantial reusable subsystems; membership libraries are explicitly distinguished from complete service catalogs. Historical projects and official mirrors are labeled. Selection reflects the specific engineering material cited, not a claim that every component is exemplary or suitable for a new deployment.

## Criteria

- **C1 — Correctness:** difficult invariants, concurrency, protocol semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and mechanisms serving multiple applications or deployment models.
- **C3 — Performance:** concrete resource, latency, throughput, or scaling concerns addressed through understandable structure.
- **C4 — Evolution:** sustained development accompanied by compatibility, testing, or complexity-management evidence; age alone is insufficient.

## Registries and application discovery frameworks

### [hashicorp/consul](https://github.com/hashicorp/consul)

**Go — distributed service catalog, health checking, DNS/HTTP discovery, and service-mesh control plane.** Concentrate on the catalog and agent architecture: it offers a useful study of how membership observations, durable registry state, and application-facing discovery fit together.

- **C1:** Servers persist registered-service and agent state through Raft, while Serf supplies gossip communication and network coordinates. These mechanisms expose different consistency and failure concerns within one discovery system. The architecture also explains persistence across restarts. [Architecture](https://developer.hashicorp.com/consul/docs/architecture).
- **C2:** A shared catalog supports DNS and HTTP consumers, externally registered services, and health-aware discovery across deployment environments. This makes the discovery subsystem reusable beyond any one RPC framework. These interfaces and the health-check integration are described in the repository overview linked above.
- **C3:** The documented WAL uses rotating append-only log files, and network coordinates support proximity-based service selection. Both connect implementation structure to operational costs without requiring an unsupported throughput claim. [Architecture](https://developer.hashicorp.com/consul/docs/architecture).

### [Netflix/eureka](https://github.com/Netflix/eureka)

**Java — client/server service registry with peer replication.** Study the availability tradeoff between keeping a usable registry during partitions and promptly removing dead instances. The cited peer documentation describes the established Eureka architecture; the experimental historical “Eureka 2.0 Architecture” wiki is not used as evidence for current behavior.

- **C1:** Peer operations are reconciled through subsequent heartbeats. Self-preservation suspends expiry when renewals drop, deliberately allowing stale registrations; clients must handle unreachable instances. Startup registry transfer and partition recovery are explicitly documented. [Peer communication](https://github.com/Netflix/eureka/wiki/Understanding-Eureka-Peer-to-Peer-Communication).
- **C3:** Clients retain a local registry and fetch deltas; count reconciliation triggers a full fetch when needed. Servers cache compressed and uncompressed representations. This is a concrete study of reduced discovery traffic coupled to repair mechanisms. [Client/server communication](https://github.com/Netflix/eureka/wiki/Understanding-eureka-client-server-communication).

### [alibaba/nacos](https://github.com/alibaba/nacos)

**Java — service discovery and configuration platform; relevant subsystem: Naming.** Study the distinction between ephemeral runtime registrations and durable service resources, rather than treating every endpoint as an interchangeable key/value entry.

- **C1:** The Naming specification separates AP-oriented ephemeral client state and Distro synchronization from CP-oriented persistent state and recovery. It specifies service-level type consistency and explains why query results are filtered views rather than raw storage contents. [Naming specification](https://github.com/alibaba/nacos/blob/develop/specs/en/naming/naming-spec.md).
- **C2:** Namespace/group/service identity, subordinate clusters and instances, publisher/subscriber models, and separate runtime and management APIs form reusable discovery abstractions. Health-check and authorization extension points preserve that model.
- **C3:** Subscription pushes update client memory, asynchronously refresh disk caches, and provide reconnect, cache-miss, and polling recovery paths. The same [specification](https://github.com/alibaba/nacos/blob/develop/specs/en/naming/naming-spec.md) connects these mechanisms. It is a development-branch contract, not a guarantee that every released version behaves identically.

### [polarismesh/polaris](https://github.com/polarismesh/polaris)

**Go — service discovery and governance server.** The registration and health-check subsystems provide a less ubiquitous example of managing large populations of changing instances. Maintenance cadence is not inferred from the feature list; the metadata checked showed a latest push in October 2025.

- **C1:** Re-registration preserves an existing isolation setting when the new request omits it. Health checking coordinates per-instance state, expiry, and deletion while callbacks run concurrently. These are concrete operational invariants, not simply CRUD validation. [Instance lifecycle](https://github.com/polarismesh/polaris/blob/main/service/instance.go), [health-check scheduler](https://github.com/polarismesh/polaris/blob/main/service/healthcheck/check.go).
- **C3:** Registration can use a batch path that merges creation requests. The health subsystem uses a timing wheel, randomized scheduling, and interval bounds instead of an undifferentiated scan for every heartbeat. The same two files show the separation between registration work and timed checks.

### [apache/servicecomb-service-center](https://github.com/apache/servicecomb-service-center)

**Go — standalone microservice registry with instance, schema, dependency, and access-rule metadata.** Study a registry that models service contracts and versions as well as addresses.

- **C1:** The design connects provider heartbeats to expiring instance state in etcd and consumer watches to local-cache updates. Its storage layout separates instance records, leases, service indexes, schemas, and dependencies, making cross-record lifecycle concerns visible. [Service-Center design](https://github.com/apache/servicecomb-service-center/blob/master/docs/design-guides/design.rst).
- **C2:** API, metadata logic, server core, aggregation/cache/indexing, and registry-adapter layers have explicit responsibilities. REST/gRPC interfaces and SDK consumers reuse this model rather than embedding one application's routing rules.
- **C3:** The design keeps endpoint selection on the consumer's cached view and places caching/indexing between core logic and storage. The [design guide](https://github.com/apache/servicecomb-service-center/blob/master/docs/design-guides/design.rst) is the entry point; its particular example intervals should not be assumed universal defaults.

### [apache/curator](https://github.com/apache/curator)

**Java — ZooKeeper recipes; relevant subsystem: Curator Service Discovery.** This monorepo counts once. Study how a low-level coordination system becomes a service-instance API with provider selection and explicit cache semantics.

- **C1:** The guide distinguishes a last-known watched cache from guaranteed-fresh state, requires lifecycle management of discovery objects, and documents temporary exclusion after instance errors. It also explains the watcher-retention problem when old ZooKeeper versions are paired with repeatedly created providers. [Service Discovery guide](https://curator.apache.org/docs/service-discovery/).
- **C2:** `ServiceInstance`, `ServiceDiscovery`, `ServiceProvider`, provider strategies, `ServiceCache`, and `DownInstancePolicy` separate registration, selection, observation, and failure policy.
- **C3:** A watcher-maintained cache avoids querying ZooKeeper on every lookup; provider reuse also prevents the documented historical memory-exhaustion pattern. These mechanisms and their limits are explained in the same guide.

### [vert-x3/vertx-service-discovery](https://github.com/vert-x3/vertx-service-discovery)

**Java — asynchronous application discovery infrastructure and registry bridges.** Study the separation between a published record, a service reference, and the actual client/proxy object acquired by a consumer.

- **C2:** Service types describe both location and client construction; backend, importer, and exporter SPIs allow distributed-map or external-registry integration. HTTP services, event-bus proxies, message sources, and data sources share the model. [Discovery guide](https://vertx.io/docs/vertx-service-discovery/java/).
- **C1:** Lifecycle correctness spans asynchronous bridge startup, successful storage before publication events, concurrent binding collections, and reference release during shutdown. `DiscoveryImpl` records importers after successful startup and gathers asynchronous bridge-close operations. This is useful code for examining ordering and cleanup obligations; it is not a claim that arbitrary concurrent close/register calls are safe. [Implementation](https://github.com/vert-x3/vertx-service-discovery/blob/master/vertx-service-discovery/src/main/java/io/vertx/servicediscovery/impl/DiscoveryImpl.java).

### [apache/juddi](https://github.com/apache/juddi)

**Java, with .NET clients — UDDI web-service registry; archived official Apache mirror.** The project retired in February 2023. It is retained for studying the older business/service/binding registry model and standards compatibility, not as a maintained deployment choice. [Apache Attic status](https://attic.apache.org/projects/juddi.html).

- **C1:** Publication validation handles case-folded keys, duplicate keys, entity limits, string constraints, and relationships between businesses, services, bindings, and technical models. The amount of validation illustrates how discovery metadata becomes a correctness problem when independently administered entities share a registry. [Publication validator](https://github.com/apache/juddi/blob/master/juddi-core/src/main/java/org/apache/juddi/validation/ValidatePublish.java).
- **C2:** JAX-WS API endpoints, core registry logic, and JPA persistence are separated. The architecture supports UDDI v2/v3, multiple persistence implementations, different servlet containers, and client transports including SOAP and in-VM access. [Version 3.2 architecture guide](https://svn-eu.apache.org/repos/asf/juddi/cms-site/trunk/content/docs/3.2/juddi-guide/html/ch03.html). Generated API classes alone are not the basis for inclusion; the substantive registry core is.

## DNS discovery for clusters and schedulers

### [coredns/coredns](https://github.com/coredns/coredns)

**Go — extensible DNS server; relevant subsystems: Kubernetes and etcd discovery plugins.** Study how independently composed DNS functions interact with an asynchronously updated service inventory.

- **C1:** The Kubernetes plugin synchronizes watches before declaring readiness and returns `SERVFAIL` for unsynchronized Kubernetes records. Its verified-pod mode checks namespace/IP membership rather than manufacturing answers from arbitrary query names. [Kubernetes plugin](https://coredns.io/plugins/kubernetes/).
- **C2/C3:** Plugin chaining composes discovery, forwarding, caching, and other DNS behavior. The Kubernetes documentation explicitly exposes the memory cost of verified-pod watches and options to limit watched resources.
- **C4:** The [2017 1.0 release notes](https://github.com/coredns/coredns/blob/master/notes/coredns-1.0.0.md) document fuzz testing, synchronization fixes, and configuration changes; the present repository documents a staged Corefile deprecation policy. Together with the evolving plugin contract, this supplies concrete evidence of compatibility and test management across years.

### [kubernetes/dns](https://github.com/kubernetes/dns)

**Go — kube-dns service-discovery implementation and related components.** The relevant implementation is kube-dns. The repository explicitly says NodeLocal DNSCache has moved elsewhere; that moved subsystem is not counted here. Study the translation from Service/Endpoints events to DNS records.

- **C1:** The implementation uses a common lock for the DNS tree and reverse-record map so they cannot drift independently. Startup waits for resource synchronization, and separate controllers handle Service and Endpoint changes. [KubeDNS implementation](https://github.com/kubernetes/dns/blob/master/pkg/dns/dns.go).
- **C2:** The [DNS-based service-discovery specification](https://github.com/kubernetes/dns/blob/master/docs/specification.md) defines interoperable naming and record behavior for services and endpoints, independently of an application language.
- **C3:** Watch-driven local stores and an in-memory DNS tree separate Kubernetes API traffic from the DNS query path. This repository is useful alongside CoreDNS as a different implementation of overlapping discovery semantics, not as another copy of CoreDNS.

### [skynetservices/skydns](https://github.com/skynetservices/skydns)

**Go — historical etcd-backed DNS service discovery.** The canonical repository remains readable and was not marked archived; checked metadata showed its latest push in March 2021. Treat it as a historical implementation. Do not count the Spotify fork as a separate project.

- **C1:** The server handles recursive CNAME chains with loop checks, distinguishes missing names from backend failures, and handles response-size overflow/truncation. These are protocol correctness obligations beyond translating a key to an address. [DNS server implementation](https://github.com/skynetservices/skydns/blob/master/server/server.go).
- **C3:** Separate response and signature caches, shared in-flight forwarding, and round-robin processing even on cached answers expose the interaction between caching and discovery behavior. The same implementation contains SRV-record construction and duplicate removal.

### [d2iq-archive/mesos-dns](https://github.com/d2iq-archive/mesos-dns)

**Go — DNS discovery from Mesos master state; archived October 2024.** This is the canonical destination of the former `mesosphere/mesos-dns` repository. Study scheduler-derived discovery, where tasks do not individually register themselves with a separate service catalog.

- **C1:** The record generator rejects missing master state, applies DNS-label rules, and explicitly handles the mismatch between a newly discovered leader and stale configured fallback masters. Stable naming during leadership and membership changes is a documented concern. [Record generator](https://github.com/d2iq-archive/mesos-dns/blob/master/records/generator.go).
- **C2:** A distinct record-generation layer turns framework, agent, master, and task state into A/AAAA/SRV record sets. Functional options inject the state loader and HTTP transport; enumeration models also expose the generated data through an API. This makes the source useful for studying a reusable state-to-discovery projection.

## Registration agents and discovery-to-proxy bridges

### [gliderlabs/registrator](https://github.com/gliderlabs/registrator)

**Go — Docker lifecycle-to-registry bridge.** Study third-party registration: a process observes containers and publishes service instances without application SDK changes. This is an older Docker-centric design; inclusion does not assert compatibility with every current Docker or registry release.

- **C1:** The bridge serializes registry updates, refreshes leases, reconciles a full container listing, and distinguishes explicit deregistration from letting a TTL expire. It retains dead-container information when later cleanup may need it; reconciliation explicitly assumes re-registration is idempotent. [Bridge implementation](https://github.com/gliderlabs/registrator/blob/master/bridge/bridge.go).
- **C2:** Adapter factories selected by URI scheme separate registry behavior from Docker observation. A common service model handles ports and metadata with container-wide and per-port overrides. [Service model](https://gliderlabs.github.io/registrator/latest/user/services/).

### [airbnb/nerve](https://github.com/airbnb/nerve)

**Ruby — health-checking registration daemon, the producer side of SmartStack.** Historical study: the inspected default-branch history ends in July 2020; this is not an assertion of current maintenance. [Commit history](https://github.com/airbnb/nerve/commits/master).

- **C1:** Registry-reporting failure is distinguished from service failure. If the reporter cannot be reached, the watcher clears its remembered status so a later cycle will report again. Throttled transitions also force later reconsideration and use a distinct result from an ordinary failed check. [Service watcher](https://github.com/airbnb/nerve/blob/master/lib/nerve/service_watcher.rb).
- **C2:** Service watchers compose multiple health checks and a separate reporter. Check classes are selected by type and can be loaded from external modules, allowing the registration state machine to serve different protocols and services.
- **C3:** Transition reporting includes configurable rate limiting and shadow behavior, addressing registry churn from flapping services within the same readable state machine.

### [airbnb/synapse](https://github.com/airbnb/synapse)

**Ruby — service discovery translated into local proxy configuration, the consumer side of SmartStack.** Historical study: the inspected default-branch history ends in November 2020. Nerve and Synapse are separate cooperating implementations, not forks of one another. [Commit history](https://github.com/airbnb/synapse/commits/master).

- **C1:** The ZooKeeper watcher distinguishes being connected enough to survive a short interruption from actually receiving updates. It re-establishes child/data watches, retries selected connection failures, and creates the watched path before discovery. [ZooKeeper watcher](https://github.com/airbnb/synapse/blob/master/lib/synapse/service_watcher/zookeeper/zookeeper.rb).
- **C2:** Watchers and configuration generators separate discovery from proxy output. The repository documents composable multi-watchers with union, sequential fallback, and source-selection strategies, plus a policy for retaining previous backends when discovery becomes empty.
- **C3:** The watcher pools ZooKeeper connections and runs retrying discovery work in a background thread. This offers a concrete bridge architecture for studying how registry instability is kept out of the proxy's request path.

## Gossip membership and decentralized discovery

### [hashicorp/serf](https://github.com/hashicorp/serf)

**Go — decentralized discovery/orchestration library and agent.** Study the higher-level events and join/leave intent layered over gossip membership. The original website was shut down in 2024; documentation survives in this repository, which is the source cited here.

- **C1:** Direct and indirect probes feed suspicion before declaring failure. Lifeguard adapts detection when the observing node is itself degraded. Lamport timestamps order join/leave intent and user messages in an eventually consistent system. [Gossip internals](https://github.com/hashicorp/serf/blob/master/docs/internals/gossip.html.markdown).
- **C2:** The library is distinct from its CLI agent; applications can consume membership and events to update load balancers, caches, or DNS. These uses are described in the repository overview.
- **C3:** Bounded-fanout UDP dissemination is complemented by less frequent full-state TCP exchange. The internals explain propagation versus failure-detection cadence and packet-size constraints; they do not establish that total cluster traffic is constant.

### [hashicorp/memberlist](https://github.com/hashicorp/memberlist)

**Go — reusable membership and failure-detection engine beneath discovery systems such as Serf.** This is a discovery building block, not a service catalog or consensus store.

- **C1:** SWIM-style state transitions, UDP probing, TCP reconciliation, and incarnation-number handling confront delayed and inconsistent observations. The security model explicitly separates authenticated cluster membership from per-node identity and Byzantine safety. [Protocol and security model](https://github.com/hashicorp/memberlist/blob/master/SECURITY.md).
- **C2:** Admission/conflict/merge delegates, configurable transport, and shared-key rotation mechanisms let embedding systems supply their own policy while reusing the membership machinery.
- **C3:** The same primary document describes bounds on full-state transfers, decompression, and inbound message queues. These are concrete resource controls with explicitly stated limits, rather than evidence of unlimited resistance to malicious peers.

### [quickwit-oss/chitchat](https://github.com/quickwit-oss/chitchat)

**Rust — gossip membership, failure detection, and per-node metadata dissemination.** A discovery foundation used in Quickwit, rather than a standalone registry with a standardized service API. Study an alternative to SWIM: scuttlebutt reconciliation combined with an adaptive failure detector.

- **C1:** The repository explains versioned tombstones, garbage-collection watermarks, and forced state resets when peers have missed deletions. It also documents the limits of dead-node state removal after long partitions. The [failure detector implementation and tests](https://github.com/quickwit-oss/chitchat/blob/main/chitchat/src/failure_detector.rs) exercise initialization, smoothing, and live/dead/live transitions.
- **C3:** Reconciliation sends deltas, including partial deltas constrained by packet capacity. Failure estimation uses a bounded sampling window with maintained statistics. These structures make the bandwidth and memory tradeoffs inspectable without assuming perfect delivery or globally consistent liveness.

## Local-network mDNS and DNS-SD

### [apple-oss-distributions/mDNSResponder](https://github.com/apple-oss-distributions/mDNSResponder)

**C/C++ — Apple's official source-distribution repository for Bonjour's responder and DNS-SD APIs.** Treat this as an official published-source mirror, not evidence that all development occurs publicly on GitHub. Study a portable protocol core with platform-specific networking and a shared system daemon.

- **C2:** The architecture separates application, mDNS core, and platform support. Applications can advertise, browse, and resolve services through the same core on different operating systems. [Code architecture](https://github.com/apple-oss-distributions/mDNSResponder/blob/main/Documents/mDNSResponder.md).
- **C1:** The API contract explains shared-connection parent/child ownership, callback batching, double-deallocation, and concurrent event-processing hazards. Callers must provide synchronization for shared references. [DNS-SD API header](https://github.com/apple-oss-distributions/mDNSResponder/blob/main/mDNSShared/dns_sd.h).
- **C3:** The architecture explicitly motivates a shared daemon to avoid every application transmitting its own multicast queries and retaining its own answer cache.

### [avahi/avahi](https://github.com/avahi/avahi)

**C — Linux-oriented mDNS/DNS-SD daemon, core library, and client interfaces.** Study how service discovery is integrated into applications with different event loops and threading models.

- **C1:** The threading guide specifies when an `AvahiClient`/poll pair can be shared, which callbacks already hold locks, and how helper-thread shutdown and object access must be coordinated. [Threading contract](https://github.com/avahi/avahi/blob/master/docs/THREADS).
- **C2:** Client/poll abstractions support externally supplied event loops or a dedicated threaded loop. The release history documents additional Qt/libevent integration and a D-Bus prepare/start API that lets clients subscribe before results arrive. [NEWS](https://github.com/avahi/avahi/blob/master/docs/NEWS).
- **C1, further evidence:** The same NEWS explains an actual signal-subscription race and preservation of the older API, plus a reflected-record cache bug that caused stale answers and self-conflicts. This makes compatibility and asynchronous delivery concrete study topics.

### [python-zeroconf/python-zeroconf](https://github.com/python-zeroconf/python-zeroconf)

**Python — mDNS/DNS-SD library with threaded and asyncio-facing discovery.** Study how packet-level record updates become coherent service-added, service-removed, and service-updated notifications.

- **C1:** Browser processing treats expired PTR records, new address records, and NSEC records differently. It coalesces notifications with explicit precedence and delivers updates after cache processing; threaded browsers initialize their callback queue before listener installation. [Browser implementation](https://github.com/python-zeroconf/python-zeroconf/blob/master/src/zeroconf/_services/browser.py).
- **C2:** A shared browser base supports threaded and event-loop callback delivery, reusing the discovery logic across synchronous and asynchronous consumers.
- **C3:** PTR-query scheduling uses expiry-aware refreshes, randomized startup, and packet grouping with known answers. The code makes both network-traffic reduction and event-loop responsiveness visible.

### [jmdns/jmdns](https://github.com/jmdns/jmdns)

**Java — mDNS registration, browsing, and resolution library.** Study protocol state machines within a Java API, including discovery on machines with several network interfaces.

- **C1:** The prober advances service/host state through repeated probes before announcement, accounts for conflicts and cancellation, and throttles probing. Record construction deliberately avoids marking an unproven name unique. [Prober state task](https://github.com/jmdns/jmdns/blob/master/src/main/java/javax/jmdns/impl/tasks/state/Prober.java).
- **C2:** The multihomed `JmmDNS` abstraction manages underlying per-address `JmDNS` instances as topology changes. Its contract explicitly warns that many operations are not transactional and that applications must maintain registrations; the API is labeled experimental. [Multihomed API](https://github.com/jmdns/jmdns/blob/master/src/main/java/javax/jmdns/JmmDNS.java).

### [keepsimple1/mdns-sd](https://github.com/keepsimple1/mdns-sd)

**Rust — independent mDNS/DNS-SD library for publishing and discovering services.** Study a dedicated-thread design that can be called from both synchronous and asynchronous applications. The repository labels the implementation beta and documents partial protocol coverage and interoperability checks.

- **C1:** Conflict handling is scoped to interfaces, compares address records before declaring conflict, renames conflicting records, and restarts probing. Interface changes and service/record lifetimes are explicit daemon concerns. [Service daemon](https://github.com/keepsimple1/mdns-sd/blob/main/src/service_daemon.rs).
- **C2:** A channel-based `ServiceDaemon` API separates callers from the protocol loop and exposes browsing, registration, resolution, monitoring, and shutdown without requiring a particular async runtime.
- **C3:** The implementation uses bounded channels, a polling loop, and scheduled timers. These provide concrete resource and scheduling decisions to examine, without implying that slow-consumer behavior is cost-free.

## Coverage, search process, and limitations

Live discovery searches used substantially more than six formulations. The main angles were centralized registries (`Consul`, `Eureka`, `Nacos`); less ubiquitous governance registries (`Polaris`, `ServiceComb`); ZooKeeper/application libraries (`Curator`, `Vert.x`); DNS over etcd and Kubernetes; Mesos and Docker discovery; SmartStack registration/proxy bridges; SWIM and scuttlebutt gossip; mDNS/DNS-SD across C, Java, Python, Rust, and Erlang; SSDP; and historical UDDI registries. Follow-up searches and directory inspection resolved implementations, moved repositories, and historical status. The late protocol and standalone-registry queries produced mostly overlapping implementations, wrappers, or adjacent metadata catalogs; jUDDI supplied the final distinct architecture family.

Every retained canonical repository was opened through GitHub, with API metadata used where available. Every entry also has an opened/read primary source beyond its root README, and substantive architectural or implementation evidence. Some GitHub rendered pages failed and the public API reached its unauthenticated rate limit; individual raw source files and public directory pages supplied the missing evidence. No candidate code was executed, dependencies installed, or repositories cloned. Source links generally track the inspected default branch rather than immutable commits, so readers should pin a revision for detailed comparison.

The selection excludes tutorial registries, generated integration wrappers, awesome-lists, duplicate SkyDNS forks, and general DNS/network stacks without a substantial discovery focus. General coordination databases such as etcd and ZooKeeper are dependencies here, rather than additional entries solely because applications can build discovery on them. Whole service meshes, generic RPC frameworks, MCP/agent metadata catalogs, and pure peer-routing/DHT projects were not expanded into this category. SSDP and Erlang discovery received discovery searches but no retained entries; this is a representative engineering selection, not exhaustive protocol coverage. NodeLocal DNSCache's relocation is acknowledged rather than attributing its current implementation to `kubernetes/dns`.

The criterion assignments and suggested study value are grounded engineering judgments drawn from the cited material. They are not benchmark results, production endorsements, comprehensive audits, or claims that an unarchived repository is actively maintained. Historical wikis and design documents are identified where version context matters; C4 is applied selectively rather than inferred from stars, creation dates, or recent pushes.
