# Reverse proxies and load balancers

Research date: **2026-10-09**.

This selection covers 24 GitHub repositories implementing reverse-proxy request paths, reusable proxy frameworks, service-mesh proxies, and transport- or packet-level load balancing. It includes a load-balancer availability manager where its relationship to the kernel forwarding engine is explicit. The emphasis is on code and design worth studying, rather than deployment recommendations or comparative benchmarks. Maintenance exceptions and experimental subsystems are identified where relevant; inclusion does not imply that every component is exemplary or currently suitable for production.

Criteria used below:

- **C1 — Correctness:** difficult invariants, concurrency, protocol semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or components supporting multiple use cases.
- **C3 — Performance and structure:** concrete resource or throughput constraints addressed through an understandable architecture.
- **C4 — Evolution:** evidence of sustained development together with compatibility, testing, or complexity-management practices.

## General-purpose edge proxies

### [nginx/nginx](https://github.com/nginx/nginx)

**Language/role:** C; web server and reverse proxy. Study the HTTP request lifecycle and module system, especially how asynchronous work outlives the function that initiates it.

- **C1:** Request finalization is a lifecycle protocol: pending buffered output installs a writer, while request reference counts determine when destruction is safe. Subrequests and output chains make “response generated” different from “request can be freed.”
- **C2:** HTTP phases, filters, upstream processing, buffers, and request memory pools provide reusable extension points within the same event-driven execution model.

**Entry point:** The [development guide](https://nginx.org/en/docs/dev/development_guide.html) explains the structures and invariants, including request finalization, subrequests, and module development. It is a more useful starting point for implementation study than a configuration recipe.

### [haproxy/haproxy](https://github.com/haproxy/haproxy)

**Language/role:** C; TCP/HTTP proxy and load balancer. **Official GitHub mirror** of HAProxy's upstream Git repository, as identified by the repository itself.

- **C1:** The internal guide states buffer bounds and wraparound invariants and distinguishes raw buffers from the structured HTTP representation. Thread affinity, connection ownership, and synchronization are explicit design concerns.
- **C3:** Per-thread polling and scheduling, memory pools, and cache-conscious object layout connect the performance goals to concrete implementation rules; blocking operations are constrained rather than hidden behind a generic concurrency layer.
- **C4:** The [published branch history](https://www.haproxy.org/) spans many release generations. Its maintenance policy separates features from fixes and applies fixes to development first, then progressively older branches, to preserve upgrade paths.

**Entry points:** [Core principles](https://raw.githubusercontent.com/haproxy/haproxy/master/doc/internals/core-principles.txt) and [branch lifecycle/backport policy](https://raw.githubusercontent.com/haproxy/haproxy/master/BRANCHES).

### [envoyproxy/envoy](https://github.com/envoyproxy/envoy)

**Language/role:** C++; extensible L4/L7 proxy used at service and network boundaries. Study ownership across the main thread and worker event loops.

- **C1:** A worker owns its connections for their lifetimes. Configuration updates reach workers through posted callbacks and thread-local state, making cross-thread publication a central correctness problem. The design documentation also explains simulated-time and threading approaches used in tests.
- **C3:** Nonblocking worker dispatchers avoid shared connection-processing locks. The documentation discusses a real limitation of connection-based distribution: long-lived HTTP/2 connections can produce uneven work, motivating optional connection balancing. Blocking work and log flushing receive separate treatment.

**Entry point:** [Threading model](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/intro/threading_model), which connects scheduling, ownership, configuration propagation, and testing.

### [caddyserver/caddy](https://github.com/caddyserver/caddy)

**Language/role:** Go; extensible server with a substantial reverse-proxy module. Study the boundary between request policy, upstream selection, and HTTP transport behavior.

- **C1:** Retry semantics distinguish failure to connect from failure after a connection succeeds. The latter defaults to retrying GET requests, and retry duration interacts with attempt counts. Dynamic upstreams also have different health-check constraints from static ones.
- **C2:** Selection policies, dynamic upstream sources, transports, and request/response handling are configurable module boundaries rather than a single fixed proxy pipeline. These support service discovery, balancing, and customized gateway behavior.

**Entry point:** The [reverse-proxy reference](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy) documents the retry conditions, health state, buffering, transport interfaces, and extension points in sufficient detail to guide source exploration.

### [traefik/traefik](https://github.com/traefik/traefik)

**Language/role:** Go; dynamic reverse proxy and application load balancer. Study how routing services compose and how operational state propagates through that composition.

- **C2:** Backend server balancing, weighted service composition, mirroring, and failover are separate service constructs. This makes the repository useful for studying a declarative traffic-routing model that can be populated by different configuration providers.
- **C1:** Composition creates nonlocal invariants: health checks must propagate through parent services, and sticky routing across multiple balancing levels requires affinity at each level. An unhealthy selected server can require choosing a replacement and updating the affinity cookie.

**Entry point:** [HTTP load-balancing services](https://doc.traefik.io/traefik/reference/routing-configuration/http/load-balancing/service/), especially the nested service, health-check, and stickiness sections.

### [graygnuorg/pound](https://github.com/graygnuorg/pound)

**Language/role:** C; HTTP reverse proxy and load balancer. This is a substantive continuation: its README describes a 2018 fork for newer OpenSSL support and continuation after the original maintainer stopped development in 2022. The original project is not counted separately.

- **C1:** The service implementation combines a session hash with expiration ordering under a service mutex. Backend removal, expiry timers, and session deletion interact; backend priority totals also receive integer-overflow checks.
- **C4:** The documented continuation history is backed by detailed releases addressing compatibility and correctness. Recent notes include 32-bit duration handling, bounded descriptor queues, and changing service-match errors into HTTP 500 responses rather than silently trying another service.

**Entry points:** [Service, session, and balancing implementation](https://raw.githubusercontent.com/graygnuorg/pound/master/src/svc.c) and [release history](https://github.com/graygnuorg/pound/releases). This is a useful smaller counterpart to the larger C proxies.

## Programmable proxies and service-routing systems

### [cloudflare/pingora](https://github.com/cloudflare/pingora)

**Language/role:** Rust; asynchronous framework for building proxies. Study a proxy lifecycle exposed as typed application callbacks, rather than only a ready-made daemon.

- **C2:** `ProxyHttp` separates per-request context, upstream selection, request/response filters, and body processing. Applications can reuse the transport machinery while supplying routing and policy.
- **C1:** Callback contracts expose serious obligations. Cache keys must distinguish response-relevant request properties to avoid cache poisoning; handlers that finish a request without forwarding it must account for draining its body or disabling connection reuse.

**Entry point:** The [`ProxyHttp` trait and its contract documentation](https://raw.githubusercontent.com/cloudflare/pingora/main/pingora-proxy/src/proxy_trait.rs). The repository explicitly labels the caching-proxy integration experimental, so its contracts should not be mistaken for a stable application API across releases.

### [dotnet/yarp](https://github.com/dotnet/yarp)

**Language/role:** C#; reverse-proxy toolkit built on ASP.NET Core. Study the separation of HTTP forwarding from the higher-level routing and balancing product.

- **C2:** `IHttpForwarder` translates an incoming `HttpContext` into an upstream request and copies the response back. Direct forwarding deliberately leaves destination discovery, routing, balancing, and affinity to the caller, allowing reuse in custom middleware.
- **C3:** The implementation guidance connects API choice to resource behavior: `HttpMessageInvoker` avoids the response buffering associated with ordinary `HttpClient` usage, preserving streaming and reducing memory/latency costs. Reusing the transport also matters for connection pooling.

**Entry point:** [Direct forwarding architecture and usage](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/yarp/direct-forwarding?view=aspnetcore-10.0), including transport configuration, streaming, transforms, and forwarding errors.

### [zalando/skipper](https://github.com/zalando/skipper)

**Language/role:** Go; programmable HTTP reverse proxy and routing engine. Study the interaction of its route language, extensible filters, and dynamically supplied routing state.

- **C2:** Routes combine predicates, ordered filters, and backend types. Responses traverse filters in reverse order; shunt, loopback, and dynamic backends permit local responses, rematching after transformation, and late destination selection. These are reusable execution abstractions.
- **C1:** Routing retains the last successfully loaded state during data-source failures and rebuilds lookup structures after updates. Its documentation candidly identifies nondeterministic merging when different sources provide the same route ID, an important boundary on the consistency guarantee.
- **C3:** Matching first narrows candidates with a path lookup tree, then evaluates the remaining predicates, rather than applying every route condition to every request.

**Entry points:** [Proxy and filter overview in `doc.go`](https://github.com/zalando/skipper/blob/master/doc.go) and [routing package documentation](https://pkg.go.dev/github.com/zalando/skipper/routing).

### [fabiolb/fabio](https://github.com/fabiolb/fabio)

**Language/role:** Go; service-discovery-driven HTTP/TCP load balancer. Study how a proxy consumes an external service registry without interrupting established traffic.

- **C1:** A routing table is fully rebuilt before it replaces the active table atomically. Existing connections and in-flight requests survive the replacement, including removal of their route from the new table.
- **C2:** Routing state is derived from service registrations, health checks, and explicit route commands in Consul KV. That separation between discovery inputs and the published routing table supports automatic discovery with operator-provided routing overrides across the proxy's supported transports.

**Entry point:** [Dynamic reloading](https://fabiolb.net/feature/dynamic-reloading/). The atomic replacement and treatment of existing requests are concrete local guarantees; they should not be expanded into an unsupported claim that every Fabio instance changes configuration simultaneously.

### [sozu-proxy/sozu](https://github.com/sozu-proxy/sozu/)

**Language/role:** Rust; reverse proxy designed around runtime configuration and worker replacement. Study the control process, worker event loops, and protocol state machines together.

- **C1:** Workers maintain readiness state for edge-triggered I/O and transition through protocol-specific states. Configuration changes use an explicit command/response protocol; worker replacement must preserve the distinction between receiving new work and finishing existing connections.
- **C3:** Single-threaded workers, reusable buffers, slab-managed connection state, and independent worker processes give a visible structure to allocation and concurrency costs. The architecture explains how worker upgrades can proceed incrementally.

**Entry point:** [Architecture document](https://github.com/sozu-proxy/sozu/blob/main/doc/architecture.md), including command distribution, worker operation, buffers, and HTTP/TLS/WebSocket state transitions. This is particularly useful alongside Envoy's thread model and NGINX's request-lifetime model.

### [linkerd/linkerd2-proxy](https://github.com/linkerd/linkerd2-proxy)

**Language/role:** Rust; Linkerd's service-mesh data-plane proxy, rather than its control-plane repository. Study transparent interception and the composition of request-processing services in a resource-constrained sidecar.

- **C2:** Tokio, Hyper, Tower, and the proxy's own crates provide separable asynchronous I/O, HTTP, middleware, discovery, and transport-security responsibilities. Protocol detection selects HTTP-aware processing or TCP forwarding.
- **C3:** The published architecture explains latency-sensitive balancing using an exponentially weighted estimate and the power of two choices. Sampling candidates avoids globally ordering all endpoints and reduces the tendency for multiple balancers to select the same apparent best backend.

**Entry point:** The official [architecture walkthrough](https://linkerd.io/2020/07/23/under-the-hood-of-linkerds-state-of-the-art-rust-proxy-linkerd2-proxy/). This is a dated 2020 explanation of design foundations, not evidence that every present-day default or balancing detail is unchanged.

### [mosn/mosn](https://github.com/mosn/mosn)

**Language/role:** Go; extensible L4/L7 proxy with HTTP and RPC protocol support. Study persistent-connection migration and protocol-neutral network/stream filtering.

- **C1:** The documented hot-upgrade design transfers listener and client descriptors plus buffered connection state between processes. It suspends writes during read-side migration to prevent old and new processes from corrupting the same stream. Migration timing is staggered to spread the transition load.
- **C2:** Codec extension points and distinct network/stream filter abstractions accommodate protocols such as Dubbo and SOFARPC alongside HTTP, rather than treating every application protocol as an HTTP variant.
- **C3:** The core design compares Go's connection-oriented netpoll model with a raw-epoll/goroutine-pool approach, exposing stack and scheduling costs.

**Entry points:** [Core concepts](https://mosn.io/en/docs/concept/core-concept/) and [hot-upgrade design](https://mosn.io/en/docs/concept/smooth-upgrade/). Migration support is a documented implementation scheme, not a blanket guarantee for every protocol or deployment.

### [Netflix/zuul](https://github.com/Netflix/zuul)

**Language/role:** Java; asynchronous gateway and reverse-proxy framework. The relevant subsystem is its Netty-based request pipeline and origin proxying.

- **C2:** Inbound filters, an endpoint, and outbound filters divide request handling into reusable stages. `ProxyEndpoint` forwards to origins, while other endpoints can terminate requests locally, allowing a shared gateway framework to serve different routing policies.
- **C3:** The 4.0 architecture uses asynchronous completion with `CompletableFuture`. Its documentation explicitly separates blocking filters onto another thread pool so that they do not occupy Netty event-loop threads.

**Entry point:** [How Zuul 4.0 works](https://github.com/Netflix/zuul/wiki/How-It-Works-4.0), which is specific about the execution model and version. The interesting engineering question is how filter extensibility coexists with restrictions on work performed on an I/O thread.

## Cache and protocol-focused reverse proxies

### [apache/trafficserver](https://github.com/apache/trafficserver)

**Language/role:** C++; caching HTTP proxy with reverse-proxy remapping. Study both its persistent cache layout and the structures that select remap rules.

- **C1:** Storage is organized into spans, volumes, and stripes; object placement and directory entries must remain consistent with that layout. Hash collisions and changes to storage mapping have explicit consequences for lookup and cache validity.
- **C3:** Each stripe has an in-memory directory, allowing a cache miss to be determined without reading the object from disk. Fixed directory structures and compact metadata expose the memory/storage tradeoff.
- **C2:** The remapping architecture separates mappings, host/path lookup structures, regular-expression mappings, and plugin-associated data.

**Entry points:** [Cache architecture](https://docs.trafficserver.apache.org/en/latest/developer-guide/cache-architecture/architecture.en.html) and [URL rewrite architecture](https://docs.trafficserver.apache.org/en/latest/developer-guide/core-architecture/url_rewrite_architecture.en.html). Some developer documentation describes reconstructed internals; use it as a source-navigation guide rather than a permanent storage-format specification.

### [h2o/h2o](https://github.com/h2o/h2o)

**Language/role:** C; HTTP server with a substantial reverse-proxy handler. The selected subsystem is upstream proxying, pooling, and buffering, rather than static-file serving alone.

- **C1:** Connection reuse has protocol constraints: enabling the upstream PROXY protocol requires disabling persistent upstream connections. The documented balancing behavior also distinguishes choosing a fresh connection from reusing an existing pooled connection and specifies fallback after connection failures.
- **C3:** Response buffering trades memory or disk usage against the time an upstream connection remains occupied. Bounding the buffer can save local resources while requiring more upstream connections; the documentation makes that coupling explicit.

**Entry point:** [Proxy directives and behavior](https://h2o.examp1e.net/configure/proxy_directives.html). Experimental upstream protocol features are identified in that reference and should be evaluated separately from the established proxy path.

### [nghttp2/nghttp2](https://github.com/nghttp2/nghttp2)

**Language/role:** C/C++; HTTP/2 library and applications. **Relevant subsystem: `nghttpx`, the C++ reverse proxy.** The library and proxy are counted once as a monorepo.

- **C1:** `nghttpx` translates between frontend and backend protocol configurations while handling TLS negotiation, affinity, and connection reuse. Its TLS early-data behavior delays forwarding by default until handshake completion, making replay concerns part of proxy policy.
- **C3:** HTTP/2 backend connections multiplex streams, but stream-concurrency limits can require additional backend connections. The documented connection-pool behavior provides a concrete study of balancing multiplexing efficiency against available concurrency.

**Entry point:** [nghttpx HOW-TO](https://nghttp2.org/documentation/nghttpx-howto.html), covering reverse-proxy modes, backend mapping, TLS, affinity, and pooling. HTTP/3 frontend support is documented as experimental; no claim is made here of HTTP/3 backend support.

## Transport and packet-level load balancing

### [facebookincubator/katran](https://github.com/facebookincubator/katran)

**Language/role:** C/eBPF and C++; XDP load-balancing data plane with a C++ control library. Study where packet processing and configuration meet.

- **C1:** Virtual services are identified by address, port, and protocol. Consistent-hash ring sizing and configured limits must agree between control and data planes, while connection tracking preserves backend selection for existing flows.
- **C3:** XDP placement, an LRU flow cache, CPU locality, and NUMA-aware configuration expose the architectural choices behind the fast packet path.
- **C2:** `KatranLb` provides a control API for virtual services and real servers, allowing a separate service-control system to manage the data plane.

**Entry point:** [Usage and architecture constraints](https://github.com/facebookincubator/katran/blob/main/USAGE.md). The repository's direct-server-return model and packet restrictions make this a specialized L4 design, not a substitute for HTTP-aware proxying.

### [github/glb-director](https://github.com/github/glb-director)

**Language/role:** C; DPDK-based director for a distributed L4 load-balancing system. Study graceful backend changes without making every director share per-flow state.

- **C1:** Rendezvous ordering supplies primary and secondary backend choices whose relative order survives membership changes. Draining swaps their roles; the design states restrictions on simultaneous inactive hosts and explains why differing director health views can remain safe under its assumptions.
- **C3:** A precomputed table and keyed packet hashing keep selection work small in the forwarding path. Encapsulation and direct return separate inbound distribution from return traffic.

**Entry point:** [GLB hashing design](https://github.com/github/glb-director/blob/master/docs/development/glb-hashing.md). Its explicit draining assumptions are especially valuable: this is an algorithm with operational preconditions, not a generic promise that consistent hashing alone preserves every connection.

### [iqiyi/dpvs](https://github.com/iqiyi/dpvs)

**Language/role:** C; DPDK-based virtual server and L4 load balancer. Study a userspace network stack organized around CPU-local forwarding state.

- **C3:** The architecture separates a master/control worker, forwarding workers, and optional receive/KNI workers. Polling and core assignment are explicit; the tuning guide relates receive drops and inter-core message timeouts to worker load and excessively long processing loops.
- **C2:** Multiple forwarding/NAT modes, scheduling algorithms, and network-stack components share this worker framework. The repository describes per-CPU connection tables and receive steering/connection redirection, illustrating how different forwarding modes reuse infrastructure under locality constraints.

**Entry point:** [Worker performance tuning](https://github.com/iqiyi/dpvs/blob/master/doc/Worker-Performance-Tuning.md), read together with the architecture in the repository overview. Performance depends on NIC capabilities, queue steering, and CPU placement; published benchmark numbers are deliberately not used as selection evidence.

### [loxilb-io/loxilb](https://github.com/loxilb-io/loxilb)

**Language/role:** Go control plane and C/eBPF data plane; network load balancer for Kubernetes, edge, and related networking environments. Study the interface between service state and kernel packet-processing state.

- **C2:** The architecture separates the load-balancer API, configuration of BPF maps, routing integration, and the external `kube-loxilb` component that watches Kubernetes services and endpoints. This permits integration beyond one fixed in-cluster deployment pattern.
- **C3:** Go manages configuration while eBPF programs execute packet processing in the kernel. This separation keeps control operations out of the forwarding path and avoids routing every packet through a userspace control process.

**Entry point:** The project's [architecture document](https://github.com/loxilb-io/loxilbdocs/blob/main/docs/arch.md). Here bypassing the ordinary kernel network stack does not mean that eBPF executes outside the kernel.

### [acassen/keepalived](https://github.com/acassen/keepalived)

**Language/role:** C; load-balancer health/availability management using Linux IPVS and VRRP. **Boundary:** Linux IPVS performs forwarding; this repository supplies health checks, configuration, failover, and process coordination.

- **C1:** Health-check results alter real-server membership or weight, while VRRP coordinates virtual-address ownership. Supervision, protocol timing, and independent failure of checker and VRRP processes are integral to keeping those responsibilities consistent.
- **C2:** A shared scheduling/core framework supports protocol-specific health checkers and separate VRRP, IPVS-checker, and BFD responsibilities. These can be composed without embedding application forwarding into each checker.
- **C3:** Cooperative I/O scheduling and process separation make responsiveness of availability control an architectural concern.

**Entry point:** [Software design](https://www.keepalived.org/documentation/user-guide/software-design/), including the process model, scheduler, watchdog behavior, and kernel interaction. Read its internal “thread” terminology in the context of its own event-scheduling abstractions.

### [yyyar/gobetween](https://github.com/yyyar/gobetween)

**Language/role:** Go; TCP/TLS/UDP load balancer. **Maintenance status:** the README explicitly says maintenance mode, with pull requests accepted.

- **C1:** UDP forwarding creates client/backend associations without TCP's connection lifecycle. The implementation documentation requires expiry or request/response limits to bound session growth; fire-and-forget behavior has different reuse and lifetime rules.
- **C2:** Discovery providers, health checking, and selection strategies are separable parts of the load-balancer configuration, supporting several transport and backend-discovery combinations.
- **C3:** The UDP design distinguishes session retention from backend-connection caching, making the cost of per-datagram routing versus retained state visible.

**Entry points:** [Protocol implementation notes](https://github.com/yyyar/gobetween/wiki/Protocols) and [transparent UDP proxying](https://github.com/yyyar/gobetween/wiki/Transparent-UDP-proxy). Transparent mode also changes return-path requirements, so the deployment topology is part of the design.

## Historical, specialized proxy implementation

### [dlundquist/sniproxy](https://github.com/dlundquist/sniproxy)

**Language/role:** C; hostname-based TCP proxy that inspects initial HTTP or TLS SNI data without terminating TLS. **Deprecated:** the README announces deprecation dated 2023-12-13 and limited maintainer response for significant reliability/security problems. It also explains mismatches with multi-host HTTP/2 connection reuse and HTTP/3 over UDP.

- **C1:** Its connection state machine coordinates initial parsing, asynchronous DNS, connection establishment, and half-closed sockets. EOF on one side does not simply discard buffered data still waiting to reach the other side.
- **C3:** Libev callbacks and bounded buffers make backpressure explicit: read readiness depends on available buffer space, while transient nonblocking errors differ from terminal failure.

**Entry point:** [`connection.c`](https://raw.githubusercontent.com/dlundquist/sniproxy/master/src/connection.c). Retained as a compact historical study of transparent stream proxying and lifecycle correctness, not as an unqualified modern edge-proxy recommendation.

## Coverage, search method, and limitations

Discovery used more than six distinct search formulations, followed by direct repository and primary-document reads. The search angles included general HTTP reverse-proxy internals; Rust proxy frameworks; service-mesh data planes; Go service-discovery/Consul routing; caching and protocol conversion; Java and .NET proxy frameworks; XDP/eBPF and DPDK load balancers; UDP/SNI transparent proxying; smaller C projects; and Erlang/Scala/Perl alternatives. Follow-up searches checked canonical owners, architecture paths, maintenance statements, and release histories. Later queries mostly returned already-covered implementations, configuration wrappers, or projects without comparable primary evidence.

Every retained repository's GitHub page was opened, and at least one additional primary source containing implementation or architectural material was read. Documentation rendered from project source, project-maintained wiki pages, and official architecture articles were used alongside source files. Repository headings are the unique project inventory; separately hosted documentation repositories are evidence, not additional projects. No candidate software was installed, cloned, or executed, and no throughput comparisons were independently reproduced.

Important boundaries and exclusions:

- [varnishcache/varnish-cache](https://github.com/varnishcache/varnish-cache) is excluded despite its technical relevance: the GitHub repository is archived and announces relocation to the Vinyl Cache forge. The inspected GitHub material did not establish a continuing official substantive mirror. This is an intentional gap in cache-proxy coverage.
- [heroku/vegur](https://github.com/heroku/vegur) surfaced as a substantive Erlang proxy library, but its GitHub repository is archived and independent source-file retrieval failed during this search. Its README alone did not meet this report's two-source verification rule, so it was not retained.
- Forward-proxy-only tools, ingress controllers that only configure another proxy, reverse-tunnel utilities, tutorials, thin wrappers, and general API-management products without a separately inspected proxy design were excluded. Service meshes and gateways were included selectively for their actual forwarding implementations.
- HAProxy's official mirror and Pound's separately evolved continuation are identified explicitly. SNIProxy's deprecation and gobetween's maintenance mode are material study/deployment distinctions. Other entries make no blanket maintenance or support promise; a visible repository and documentation do not establish one.

The C1–C4 judgments are grounded engineering assessments of the cited mechanisms, not certification of correctness. C4 is assigned sparingly where history and maintenance practices were both inspected. Some design documents describe a particular release or an older architectural foundation; those qualifications are stated rather than assuming all current behavior is identical. The list favors diverse, inspectable implementations over exhaustiveness or popularity.
