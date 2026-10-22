# API gateways and service mesh proxies

Research date: **2026-10-09**.

This report selects 25 substantial GitHub repositories for studying API request routing, policy execution, service-to-service proxying, and the configuration machinery that makes those data planes usable. It includes standalone gateways, gateway-building libraries, mesh data planes, and three explicitly identified Envoy gateway control planes. BFE represents the adjacent, gateway-capable L7 traffic-engine boundary; this is not a general inventory of web servers or load balancers. The explanations identify useful engineering problems, not an assurance that every component is exemplary.

Canonical repository names, default branches, and archive flags were checked against the public GitHub API. None of the retained repositories was marked archived at research time; that observation is not a maintenance or support guarantee. Linked architecture documents and implementation files were read, rather than relying solely on search snippets. Branch links can change after this research date, and historical documentation is identified where relevant.

## Criteria legend

- **C1 — Correctness:** difficult invariants, concurrency, adversarial inputs, protocol semantics, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or execution models supporting multiple use cases.
- **C3 — Performance with structure:** concrete resource or latency constraints addressed through understandable architectural choices, without assuming vendor benchmark claims are independently verified.
- **C4 — Evolution:** sustained development accompanied by compatibility, testing, migration, or complexity-management evidence; age alone does not qualify.

The criterion assignments are engineering judgments grounded in the cited mechanisms. Each entry supplies at least two reasons and links directly to useful reading entry points.

## Mesh data planes and programmable service proxies

### [envoyproxy/envoy](https://github.com/envoyproxy/envoy)

**C++ — extensible edge and service-mesh data plane.** Study how a proxy separates configuration coordination from connection processing while making concurrent behavior testable. The relevant subsystem is the core server and worker runtime, rather than every ancillary component in this monorepo.

- **C1:** Cross-thread updates, connection ownership, and shutdown ordering are explicit concerns. The developer documentation describes dispatcher posting, simulated time, and synchronization points for reproducing races in integration tests. These are concrete correctness techniques for an asynchronous network server. [Threading model and testing](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/intro/threading_model).
- **C3:** Accepted connections remain on one worker for their lifetime; configuration coordination runs on the main thread, and thread-local data avoids locks on much of the request path. The same document explains the tradeoff for balancing long-lived connections across workers. This is a particularly useful starting point for reasoning about throughput without treating concurrency as a black box.

### [linkerd/linkerd2-proxy](https://github.com/linkerd/linkerd2-proxy)

**Rust — purpose-built Linkerd sidecar proxy.** Study transparent protocol handling and composable asynchronous services under a per-pod resource budget. This is a separate Rust implementation, not a second listing of Linkerd's older JVM proxy or its control-plane repository.

- **C1:** The maintainer's design walkthrough explains distinguishing application TLS from mesh TLS, forwarding unknown protocols transparently, and selecting authenticated mesh behavior without requiring applications to change their protocol. These are interoperability and identity-boundary problems. [Maintainer's 2020 implementation tour](https://linkerd.io/2020/07/23/under-the-hood-of-linkerds-state-of-the-art-rust-proxy-linkerd2-proxy/).
- **C2 / C3:** The tour connects Tokio, Hyper, and Tower service composition with small proxy modules, then explains latency estimates and power-of-two-choices balancing as a way to avoid maintaining a globally ordered endpoint set. Its motivating constraints are sidecar memory consumption and tail latency. Treat this as a historical architectural tour, not a guarantee that every current internal detail is unchanged.

### [istio/ztunnel](https://github.com/istio/ztunnel)

**Rust — node-level L4 proxy for Istio ambient mesh.** Study the deliberate restriction of proxy functionality: ztunnel supplies secure transport and L4 authorization, while richer L7 behavior belongs to waypoint proxies.

- **C1:** Traffic capture must preserve original destinations and prevent authorization bypass. HBONE connection pooling is keyed by source identity, destination identity, and destination IP, making the security implications of connection reuse unusually concrete. [Istio's ztunnel design](https://github.com/istio/istio/blob/master/architecture/ambient/ztunnel.md).
- **C3:** The design uses specialized `Address` and `Authorization` resources over xDS transport instead of representing everything as general Envoy resources. The implementation also separates administrative and request-processing Tokio runtimes to isolate expensive administrative work from traffic. [Runtime architecture](https://github.com/istio/ztunnel/blob/master/ARCHITECTURE.md). The Istio monorepo document is supporting evidence, not another selected repository.

### [mosn/mosn](https://github.com/mosn/mosn)

**Go — modular mesh proxy and L4/L7 gateway.** Particularly useful for engineers interested in RPC protocols beyond HTTP and in the tension between Go's runtime networking model and very large numbers of persistent connections.

- **C1:** The documented RawEpoll path uses one-shot readiness notifications, prohibits competing reads through runtime netpoll during that phase, and rearms the file descriptor after processing. These rules make ownership and concurrent-read hazards explicit. [Core concepts and I/O model](https://mosn.io/en/docs/concept/core-concept/).
- **C2 / C3:** Unified codec, network-filter, and stream-filter interfaces support HTTP, SOFARPC, and Dubbo. The same document compares a goroutine-per-connection model with pooled event handling, identifying stack, buffer, and scheduling costs. Its I/O discussion is a design reference; the older TLS benchmark figures are intentionally not adopted here.

### [flomesh-io/pipy](https://github.com/flomesh-io/pipy)

**C++ with PipyJS — programmable proxy used as a mesh data plane.** Study a stream-processing model instead of a fixed catalog of gateway policies. Its category fit is explicit in the [Flomesh Service Mesh repository](https://github.com/flomesh-io/fsm), which documents injecting Pipy sidecars to enforce traffic policies; FSM itself is not counted separately.

- **C2:** Streams contain data, message-boundary, and stream-end events; filters compose into pipelines and sub-pipelines. This gives protocol decoding, transformation, and forwarding a common representation rather than requiring a separate processing framework per protocol. [Stream and pipeline concepts](https://flomesh.io/pipy/docs/en/intro/concepts).
- **C3:** The implementation overview describes asynchronous I/O, pooled reusable resources, and pointer-based internal data transfer where possible. These mechanisms connect the programmable filter model to allocation and copying costs. [Implementation overview](https://github.com/flomesh-io/pipy/blob/main/README.md). No numerical speed or footprint claim is needed to justify inclusion.

## OpenResty and Lua policy gateways

### [Kong/kong](https://github.com/Kong/kong)

**Lua/OpenResty — API gateway with scoped plugin execution.** Study the runtime machinery needed when the same plugin can be configured globally or for overlapping route, service, and consumer scopes.

- **C1 / C2:** The plugin iterator implements an explicit precedence order over route/service/consumer combinations, selects handlers by protocol subsystem, and distinguishes collection phases from later response phases. This is reusable policy execution with consequential matching semantics, not merely a collection of middleware functions. [Plugin iterator implementation](https://github.com/Kong/kong/blob/master/kong/runloop/plugins_iterator.lua).
- **C3:** That implementation pools per-request tables and preallocates downstream-phase storage, providing a direct example of reducing allocation costs inside a flexible plugin system.
- **C4:** The [historical changelog](https://github.com/Kong/kong/blob/master/CHANGELOG-OLD.md) records releases beginning in 2015, while the [upgrade guide](https://github.com/Kong/kong/blob/master/UPGRADE.md) documents database migrations, breaking changes across major generations, and control-plane/data-plane upgrade ordering. The latter is historical migration evidence, not a claim that its older instructions are the current upgrade procedure.

### [apache/apisix](https://github.com/apache/apisix)

**Lua/OpenResty — dynamically configured API gateway.** Study how routing and policy execution interact with several configuration-delivery topologies.

- **C2:** The core performs route matching, upstream selection, discovery, and configuration updates, while Lua plugins execute in workers; external runners provide additional extension options. Traditional, separated-control-plane, and standalone modes reuse the same gateway machinery. [Architecture](https://github.com/apache/apisix/blob/master/docs/en/latest/architecture-design/apisix.md).
- **C1:** Standalone API updates have explicit per-resource version rules: stale versions are rejected, equal versions are ignored, and newer versions replace resource data. The optional wait mechanism distinguishes acceptance from confirmation that every worker applied an update. This exposes distributed configuration semantics directly. [Deployment and update semantics](https://github.com/apache/apisix/blob/master/docs/en/latest/deployment-modes.md).

### [3scale/APIcast](https://github.com/3scale/APIcast)

**Lua/OpenResty — 3scale's API enforcement gateway.** A comparatively focused codebase for studying how authorization, URL mapping, reporting, and custom behavior compose within NGINX's lifecycle.

- **C2:** Policies provide phase-specific methods, share a context, and form both global and per-service chains. Versioned policy directories and a common policy object make the extension contract concrete. [Policy model and implementation guide](https://github.com/3scale/APIcast/blob/master/doc/policies.md).
- **C1:** Chain position alone does not determine execution order: NGINX phases also matter. The documentation demonstrates how URL rewriting changes which path is authorized/mapped and why only the first content-producing policy can send the response. These examples are valuable for studying security-sensitive ordering and response-commit invariants.

## Go gateways, routing engines, and composition libraries

### [TykTechnologies/tyk](https://github.com/TykTechnologies/tyk)

**Go — API gateway with authentication, quotas, and extensible middleware.** Study policy enforcement in a gateway that distinguishes API configuration, authenticated sessions, and per-endpoint limits.

- **C1:** The rate-limit middleware separates quota and rate-limit failures, performs bounded throttling retries and dry-run checks, and handles internal request loops so global allowances are not indiscriminately consumed again. The current implementation also distinguishes endpoint limits on MCP virtual-endpoint loops. [Rate-limit and quota middleware](https://github.com/TykTechnologies/tyk/blob/master/gateway/mw_rate_limiting.go).
- **C2:** Custom Go plugins are independently compiled extension units loaded by the gateway. The guide explains the actual compatibility boundary—matching Go toolchains, dependencies, and build flags—and how workspaces make that boundary manageable. [Go plugin development](https://github.com/TykTechnologies/tyk/blob/master/docs/plugins/go-development-flow.md).

### [luraproject/lura](https://github.com/luraproject/lura)

**Go — gateway-building framework underlying KrakenD.** Study API aggregation as a composition of small functions. This entry represents Lura's implementation; the KrakenD distribution is not counted again as an independent version of the same core.

- **C2:** The framework separates service configuration, HTTP routing, and proxy processing. A `Proxy` maps context and request to response; a `Middleware` accepts one or more proxies and returns another proxy, supporting both linear composition and branching. [Architecture overview](https://github.com/luraproject/lura/blob/master/docs/OVERVIEW.md).
- **C1:** Concurrent middleware races downstream requests and returns a successful result under a timeout, while merging middleware performs fork-and-join aggregation. Request-scoped contexts and cancellation make partial results, delayed backends, and wasted work central correctness concerns. The same overview explains these distinct execution models.

### [traefik/traefik](https://github.com/traefik/traefik)

**Go — service-discovering application gateway and ingress proxy.** Study how one traffic engine accepts configuration from containers, Kubernetes, files, and key-value systems without confusing their resource identities.

- **C2:** Provider adapters translate several infrastructure models into dynamic routing configuration; middleware, service, and transport references live in explicit provider namespaces. [Provider architecture and namespaces](https://github.com/traefik/traefik/blob/master/docs/content/reference/install-configuration/providers/overview.md).
- **C1:** The retry policy exposes method idempotency, network-error behavior, status matching, request-body limits, backoff, and an overall timeout. These controls make replay semantics and resource exhaustion part of the gateway contract. [Retry policy reference](https://github.com/traefik/traefik/blob/master/docs/content/reference/routing-configuration/http/middlewares/retry.md). The inspected development-branch document contains newer options, so it should not be treated as a compatibility statement for every released Traefik version.

### [zalando/skipper](https://github.com/zalando/skipper)

**Go — HTTP routing library and proxy for service composition.** Study the relationship between a routing language's expressiveness and the cost of evaluating it.

- **C2:** Routes combine predicates, request/response filters, and backend modes including direct responses, dynamic destinations, and loopback into route matching. Data clients supply routes from different sources, and routing tables are replaced when configuration changes. [Architecture](https://opensource.zalando.com/skipper/reference/architecture/).
- **C3:** Path and subtree predicates receive a radix-tree fast path; regular-expression and other predicates run afterward. Without suitable path predicates, matching can degenerate into scanning all routes. The document explains this performance/semantics tradeoff rather than hiding it behind a throughput headline.
- **C1:** The same request-lifecycle description distinguishes connection-error retries from general responses and applies response filters in reverse order, exposing failure and composition semantics worth tracing in the implementation.

### [easegress-io/easegress](https://github.com/easegress-io/easegress)

**Go — traffic orchestration engine with gateway pipelines.** Study configurable API composition that includes control flow and multiple request/response contexts. The canonical repository is now under `easegress-io`.

- **C2:** HTTP servers route into pipelines whose reusable filters validate, build, proxy, and combine requests. Filters can appear multiple times through aliases, while namespaces let one pipeline work with several backend exchanges. [Pipeline model](https://github.com/easegress-io/easegress/blob/main/docs/02.Tutorials/2.3.Pipeline-Explained.md).
- **C1:** Filter results drive conditional forward jumps, including explicit failure-response branches and termination. Each namespace permits at most one request and one response. These rules provide concrete invariants for preventing failure paths from continuing into inappropriate backend calls or mixing aggregation state.

### [bfenetworks/bfe](https://github.com/bfenetworks/bfe)

**Go — multi-tenant L7 routing and gateway-capable traffic engine.** This is the selection's edge-proxy boundary case: the main repository supplies forwarding machinery, while its API server and configuration agent are separate projects. Study tenant-to-cluster-to-subcluster routing rather than an API-management dashboard.

- **C1 / C3:** Backends move between normal and checking states after failures; retries may stay within a subcluster or cross to another. Weighted subcluster selection, an explicit blackhole destination for overload protection, and bounded idle connection pools expose availability/capacity tradeoffs. [Balancing and failure model](https://github.com/bfenetworks/bfe/blob/develop/docs/en_us/introduction/balance.md).
- **C2:** Typed callback points cover connection acceptance, TLS handshake, product/cluster selection, forwarding, response receipt, and completion. Explicit return outcomes control continuing, redirecting, responding, or closing. [Module callback contract](https://github.com/bfenetworks/bfe/blob/develop/docs/en_us/development/module/bfe_callback.md).

## JVM gateways and protocol mediation

### [spring-cloud/spring-cloud-gateway](https://github.com/spring-cloud/spring-cloud-gateway)

**Java — Spring gateway framework.** The inspected subsystem is the reactive WebFlux server; the repository also contains a Web MVC implementation. Study how route-specific filters participate in a reactive request lifecycle.

- **C2:** Handler mapping chooses a route, then a gateway handler executes its filter chain with pre-proxy and post-proxy phases. [WebFlux request flow](https://github.com/spring-cloud/spring-cloud-gateway/blob/main/docs/modules/ROOT/pages/spring-cloud-gateway-server-webflux/how-it-works.adoc).
- **C1 / C3:** Retrying reruns downstream filters, cannot safely follow an already committed response, and requires caching bodies for replay. Backoff, jitter, and timeout settings interact with memory retained in `DataBuffer` objects. [Retry factory semantics](https://github.com/spring-cloud/spring-cloud-gateway/blob/main/docs/modules/ROOT/pages/spring-cloud-gateway-server-webflux/gatewayfilter-factories/retry-factory.adoc). This is a strong source for studying why retries are more than wrapping a call in a loop.

### [Netflix/zuul](https://github.com/Netflix/zuul)

**Java — programmable Netty gateway.** Study inbound, endpoint, and outbound filters as an execution framework, including how that framework changes when asynchronous primitives change.

- **C2 / C3:** Zuul's server and outbound client are Netty-based; synchronous filters must not block the event loop, while blocking work belongs in asynchronous filters on a separate pool. Version 4 uses `CompletableFuture` for asynchronous results. [Zuul 4 architecture](https://github.com/Netflix/zuul/wiki/How-It-Works-4.0).
- **C1:** The upgrade document explains moving connection draining from per-write attribute checks to explicit close events, including different treatment of HTTP/2 connection and stream pipelines. It also provides a compatibility bridge for older RxJava filters and documents typed context keys. [Version 4 migration and draining semantics](https://github.com/Netflix/zuul/wiki/Upgrade-Guide-4.0). Older Zuul 1/Ribbon descriptions should not be substituted for this implementation.

### [apache/shenyu](https://github.com/apache/shenyu)

**Java — reactive API gateway and protocol-conversion platform.** Study live plugin reconfiguration directly in the gateway's request entry point.

- **C1:** `ShenyuWebHandler` keeps a volatile plugin list, synchronizes extension mutations, and builds replacement lists before publishing them. These are explicit concurrency mechanisms for updating executable policy while requests arrive. [Web handler implementation](https://github.com/apache/shenyu/blob/master/shenyu-web/src/main/java/org/apache/shenyu/web/handler/ShenyuWebHandler.java).
- **C2:** The handler creates a `ShenyuPluginChain` over ordered `ShenyuPlugin` instances and integrates the resulting `Mono` with configurable scheduling. Extension loading, ordering, and request execution meet at a small, useful source entry point instead of being scattered across protocol-specific front ends.

### [MAIF/otoroshi](https://github.com/MAIF/otoroshi)

**Scala — API gateway and reverse proxy with a trait-based extension system.** Study a richer plugin lifecycle than a simple request/response interceptor pair.

- **C2:** Separate traits cover route matching, pre-routing, access validation, request/response transforms, backend delegation, unmatched-request handling, and WebSocket tunnels. Typed contexts carry route, identity, configuration, and shared attributes. [Plugin system](https://github.com/MAIF/otoroshi/blob/master/manual/next/docs/plugins/plugins-system.md).
- **C1 / C3:** Access validation and transforms explicitly return allow/deny or short-circuit results; backend plugins choose whether to invoke a delegate. Synchronous variants and flags that disable unused callbacks avoid unnecessary asynchronous and transformation work. The document makes both control-flow obligations and execution overhead visible. It is the repository's `next` manual, so released-version APIs may differ.

### [membrane/api-gateway](https://github.com/membrane/api-gateway)

**Java — gateway spanning REST, SOAP/XML, and modern API policies.** Study protocol mediation and hostile-document handling in the same extensible proxy. `membrane/api-gateway` is the verified canonical location, rather than the older `service-proxy` name.

- **C1 / C3:** The XML protection interceptor enforces document limits, handles multipart XML, distinguishes body-reading failures from document-policy failures, and can remove DTDs. Its parser factories are thread-local because they are expensive and not shared safely between threads. [XML protection implementation](https://github.com/membrane/api-gateway/blob/master/core/src/main/java/com/predic8/membrane/core/interceptor/xmlprotection/XMLProtectionInterceptor.java).
- **C2:** Shared plugin/interceptor chains can standardize request and response handling across APIs while leaving per-API behavior configurable. [Reusable chain example](https://github.com/membrane/api-gateway/blob/master/distribution/examples/extending-membrane/reusable-plugin-chains/README.md). Together, these entry points connect reusable policy composition to a concrete adversarial-input subsystem.

### [gravitee-io/gravitee-api-management](https://github.com/gravitee-io/gravitee-api-management)

**Java with TypeScript administration interfaces — API-management monorepo.** The relevant subsystem is `gravitee-apim-gateway` and its policy execution engine; the portal and management applications are not separate selections.

- **C2:** The reactive engine handles synchronous proxy traffic and message-oriented APIs through common policy execution, with distinct plan-, API-, and platform-scoped flows. [Execution engine reference, version 4.7](https://documentation.gravitee.io/apim/4.7/create-apis/overview/execution-engine).
- **C1:** The reference explains why changing header/body policy order affects behavior, how a flow condition should govern both request and response phases, and how detected but invalid credentials interact with keyless plans. These are specific security and lifecycle invariants, not simply a plugin feature list.
- Compatibility is a particularly useful study angle: v2 emulation and migration guidance preserve access to older API definitions while acknowledging changed execution semantics. This entry does not infer that every policy or commercial connector is available in the same edition.

## .NET gateways and proxy construction

### [ThreeMammals/Ocelot](https://github.com/ThreeMammals/Ocelot)

**C# — ASP.NET Core API gateway and backend-for-frontend composition.** Study the ordering of gateway middleware alongside aggregation of partially successful backend calls.

- **C2:** Public injection points surround authentication, authorization, claim transformation, and other gateway stages. The documentation distinguishes replacing default middleware from adding behavior around it. [Middleware pipeline](https://ocelot.readthedocs.io/en/latest/features/middlewareinjection.html).
- **C1:** Aggregation has explicit partial-failure semantics: a downstream `HttpClient` exception can leave that route absent from the contexts delivered to the aggregator, and dependent aggregation can expand values from one response into further calls. [Aggregation semantics](https://ocelot.readthedocs.io/en/latest/features/aggregation.html). The documentation labels the new manual complex-aggregation path a pilot without thorough testing; it is a study opportunity, not evidence of uniform production readiness.

### [dotnet/yarp](https://github.com/dotnet/yarp)

**C# — toolkit for building custom HTTP gateways and reverse proxies.** This is a library rather than a packaged API-management product. Study an explicit boundary between ASP.NET middleware, destination selection, and final forwarding.

- **C2:** The proxy pipeline exposes routes, clusters, eligible destinations, session affinity, load balancing, and health-check stages through `IReverseProxyFeature`. Applications can replace or reorder stages. [Middleware architecture](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/yarp/middleware?view=aspnetcore-10.0).
- **C1 / C3:** Configuration is snapshotted when a request enters the proxy pipeline, insulating that request from concurrent configuration changes. Forwarding errors have a dedicated feature, response modification depends on whether headers have been committed, and streaming bodies avoid default buffering costs. These mechanisms make request lifetime and ownership unusually clear.

## Envoy gateway control planes and integrated gateways

These repositories contain substantial configuration translation and policy machinery of their own. They are not counted as three additional implementations of Envoy's packet-processing engine.

### [envoyproxy/gateway](https://github.com/envoyproxy/gateway)

**Go — standalone/Kubernetes gateway control plane for Envoy.** Study the translation boundary between user-facing resources, deployment infrastructure, and proxy configuration.

- **C2:** Providers, resource watchers, translators, an infrastructure manager, and the xDS server communicate through separate infrastructure and xDS intermediate representations. The IR decouples external configuration models from Envoy resources. [System design](https://github.com/envoyproxy/gateway/blob/main/site/content/en/community/design/system-design.md).
- **C1:** Reconciliation drives actual data-plane state toward declared state; listener compatibility and Gateway API conflict resolution must be handled before emitting configuration. The design spells out hostname/protocol conflicts and the mapping from routes and backend references to Envoy objects. Some provider discussion retains early-version wording, so use it as an architectural entry point rather than a current feature matrix.

### [projectcontour/contour](https://github.com/projectcontour/contour)

**Go implementation, with a large documentation tree — Kubernetes ingress/gateway controller for Envoy.** Study high-availability control-plane behavior and deployment lifecycle tradeoffs. GitHub's language summary can be dominated by generated/documentation HTML, which does not describe the controller implementation.

- **C1:** All controller instances can serve xDS, but only the elected leader writes resource status. The documentation explicitly identifies eventual consistency between replicas and the connection-draining implications of Envoy deployment choices. [Contour architecture](https://github.com/projectcontour/contour/blob/main/site/content/docs/main/architecture.md).
- **C2:** Watches over Ingress, HTTPProxy, Gateway API, services, endpoints, and secrets feed an Envoy management server. Bootstrap generation and runtime translation form reusable boundaries between Kubernetes configuration and proxy operation. This is valuable for studying a controller whose correctness includes operational behavior, not just producing valid configuration syntax.

### [higress-group/higress](https://github.com/higress-group/higress)

**Go/C++ with Wasm extensions — integrated API gateway built on Istio and Envoy.** The current project also emphasizes AI and MCP traffic, but retains general-purpose API gateway, ingress, discovery, and protocol-conversion machinery. It is a substantive integrated implementation, not an independent reimplementation of the underlying Envoy engine.

- **C2:** Dedicated controllers translate ingress resources, external registries, HTTP-to-RPC configuration, and scoped Wasm plugin resources into Istio configuration, which is then delivered as xDS. The separation among discovery, gateway, and management components is explicit. [Architecture, in Chinese](https://github.com/higress-group/higress/blob/main/docs/architecture.md).
- **C1 / C3:** The project identifies disruption of long-lived connections during reloads and gRPC/Dubbo balancing as original engineering problems. Its architecture explains the corresponding dynamic configuration path, including discovery, Pilot Agent, Envoy, and certificate management. [Project background](https://github.com/higress-group/higress/blob/main/README.md). Inclusion rests on the problem and implementation structure, not on accepting an unmeasured zero-disruption guarantee.

## Search coverage, exclusions, and limitations

Discovery used substantially more than six formulations. Search angles included OpenResty/Kong/APISIX/APIcast policy engines; Rust and Go mesh data planes; JVM/Spring/Zuul/Otoroshi gateways; .NET/Ocelot/YARP middleware; Go routing and aggregation engines; Kubernetes Gateway API and Envoy xDS control planes; less prominent projects such as MOSN, Easegress, Membrane, and BFE; and alternative programmable proxies, including Pipy. Later searches also considered WSO2 microgateways, Janus/Goku/Express Gateway, and LoxiLB. They increasingly returned existing candidates, deployment examples, broader API-management reference architectures, and adjacent network load balancers. Pipy was retained because its stream model and independently verified mesh use added a distinct architecture.

The selection avoids counting Lura and the KrakenD distribution twice, or counting the full Istio/Linkerd control-plane repositories merely because their proxies are included. Gravitee is counted once as a monorepo. Envoy Gateway, Contour, and Higress are included for their own translation and policy machinery, with their dependency on Envoy made explicit. Generic web servers, raw proxy libraries without an established gateway/mesh role, tutorial deployments, plugin-only wrappers, and broad L4/eBPF load balancers were outside the central scope. Sōzu was inspected but omitted to keep the list focused on API policy and service-mesh use rather than generic reverse-proxy infrastructure. Omitted candidates are not thereby judged poor projects.

All retained canonical URLs were verified by opening GitHub or reading its repository API, and every selection has an additional substantive primary document or implementation file. No retained repository is presented as an archived historical project or official mirror; none was identified as such in the inspected metadata and project material. Historical Linkerd and Kong documents are used only with that qualification. C4 is assigned sparingly: compatibility documentation without an established history is not automatically evidence of years of evolution.

This was read-only source/documentation research: no candidate repository was cloned, built, benchmarked, or executed. Some documentation describes development branches, older designs, or version-specific behavior; those limits are called out in the entries. Flomesh's mesh documentation host failed to fetch reliably, so Pipy's mesh role was verified from the official FSM GitHub README instead. The report is a diverse selection guide, not an exhaustive market survey, a security audit, or an endorsement of every feature and deployment mode.
