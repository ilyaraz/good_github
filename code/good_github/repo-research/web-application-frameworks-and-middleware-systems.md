# Web application frameworks and middleware systems

Research date: **2026-10-09**

This selection covers **26 GitHub repositories** implementing server-side web frameworks, reusable request-processing middleware, typed routing, real-time application infrastructure, and frameworks that coordinate server and browser execution. It emphasizes codebases with instructive correctness boundaries and reusable architecture, from small routers to large framework monorepos. Generic networking libraries, standalone web servers, UI-only component libraries, application templates, and middleware lists are outside the main scope. A monorepo is counted once; its relevant subsystem is identified below.

The criteria are:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial inputs, resource lifetime, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or composition mechanisms serving multiple use cases.
- **C3 — Performance and structure:** concrete resource or performance constraints addressed through understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or explicit complexity management.

Each repository heading links to its verified canonical GitHub page. Linked guides and implementation files are the recommended reading entry points as well as evidence. The study recommendations and criterion assignments are engineering judgments grounded in those sources, not claims that every component is exemplary. Documentation versions are identified when material behavior is version-specific; “latest” links and default branches can change.

## Integrated frameworks and request-processing kernels

### 1. [django/django](https://github.com/django/django)

**Language / role:** Python; integrated web framework. Concentrate on the request handler, middleware, and their synchronous/asynchronous boundary.

Django is useful for studying how a broad framework preserves a precise request/response contract while evolving its execution model.

- **C1:** Middleware can short-circuit, exceptions are converted into responses between layers, and streaming responses must be wrapped without eagerly consuming their contents. Hybrid middleware must also advertise its sync/async capabilities and return the correct callable form. These are distinct control-flow and resource invariants, documented in the [middleware guide, version 5.2](https://docs.djangoproject.com/en/5.2/topics/http/middleware/).
- **C2:** A factory accepting `get_response` composes arbitrary middleware while specialized view, exception, and template-response hooks expose additional stages. The same guide explains this reusable contract and its ordering.
- **C4:** The [1.10 release notes, dated August 2016](https://docs.djangoproject.com/en/5.2/releases/1.10/), explain the replacement of the old middleware model to obtain strict layering. The 5.2 guide still documents the compatibility mixin and semantic differences, providing concrete evidence of long-term migration management.

### 2. [rails/rails](https://github.com/rails/rails)

**Language / role:** Ruby; application-framework monorepo. Relevant subsystems are Action Pack/Action Dispatch and Active Support's execution and reloading machinery.

The particularly instructive problem is coordinating concurrent application execution with development-time code replacement and framework-owned resources.

- **C1:** The Executor manages query-cache lifetime and returns database connections; the Reloader waits for safe execution boundaries. Invoking a reload from a child thread while its parent remains inside the Executor can deadlock. The [threading and code-execution guide](https://guides.rubyonrails.org/threading_and_code_execution.html) explains the dependency cycle rather than merely advising “thread safety.”
- **C2:** The Executor's run/complete callbacks provide a common boundary used by HTTP requests, jobs, and channel handling, replacing several formerly separate mechanisms.
- **C4:** The [upgrade guide](https://guides.rubyonrails.org/upgrading_ruby_on_rails.html) covers many release generations and documents `config.load_defaults` plus generated initializers that let applications adopt changed defaults incrementally across deployments.

### 3. [symfony/symfony](https://github.com/symfony/symfony)

**Language / role:** PHP; framework and component monorepo. Focus on HttpKernel, HttpFoundation, and EventDispatcher.

Study how an event-driven kernel separates request interpretation, controller resolution, argument resolution, response creation, and exception handling without tying those steps to one application architecture.

- **C1:** Listener priority and propagation determine whether later handlers run; setting an exception response stops lower-priority listeners. Main requests and subrequests must be distinguished. Long-running runtimes also require resetting service state between requests to prevent leakage. These boundaries are explained in the [HttpKernel lifecycle guide](https://symfony.com/doc/current/components/http_kernel.html).
- **C2:** `HttpKernelInterface::handle()` formalizes conversion of a request to a response, while independently replaceable resolvers and listeners supply the behavior. The guide demonstrates using the component outside a complete Symfony application, making this a useful study of a reusable framework kernel.

### 4. [dotnet/aspnetcore](https://github.com/dotnet/aspnetcore)

**Language / role:** Primarily C#; ASP.NET Core monorepo. Relevant areas are HTTP middleware, application building, routing, and endpoint execution.

This is a strong entry point for understanding how a small request-delegate contract supports a large application platform.

- **C1:** Once a response starts, changing status or headers is invalid; writing after a downstream handler may violate content length or corrupt the body. Exception handlers must surround the work they protect. The [middleware guide](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/middleware/?view=aspnetcore-10.0) connects these restrictions to concrete pipeline behavior.
- **C2:** `Use`, terminal `Run`, path-based `Map`, and predicate-based branches compose the same request delegates. `UseWhen` can rejoin the main pipeline, whereas `MapWhen` has different branch semantics. Those distinctions provide reusable building blocks for authentication, static content, diagnostics, and application-specific processing.

### 5. [spring-projects/spring-framework](https://github.com/spring-projects/spring-framework)

**Language / role:** Primarily Java; framework monorepo. The relevant subsystems are Spring MVC and Spring WebFlux, rather than the whole dependency-injection ecosystem.

Read the two web stacks as an explicit comparison of concurrency assumptions. Similar controller-facing concepts sit above materially different scheduling and I/O contracts.

- **C1:** WebFlux assumes application code does not block event-loop workers. Its reactive pipeline processes stages sequentially, but integration with blocking libraries requires deliberately switching execution resources. The [WebFlux architecture overview](https://docs.spring.io/spring-framework/reference/web/webflux/new-framework.html) explains mutable-state and scheduling implications.
- **C3:** The same overview distinguishes throughput and resource predictability from raw execution speed: nonblocking work can scale with a small fixed thread pool, while MVC permits blocking and relies on larger pools. It also explains when the client and server share event-loop resources. This is concrete performance architecture, not a benchmark ranking.

## Asynchronous applications and real-time execution

### 6. [phoenixframework/phoenix](https://github.com/phoenixframework/phoenix)

**Language / role:** Elixir, with a JavaScript client; web framework. Focus here on Channels, socket handling, and their integration with PubSub. Phoenix LiveView is a separate repository and is not counted as part of this entry.

- **C1:** Channel processes hold per-client/per-topic state. The client reconnects and rejoins after failures, but server-to-client delivery is explicitly at-most-once: missed messages are not automatically persisted or replayed. Studying this boundary prevents confusing reconnection with reliable delivery. See the [Channels architecture and reconnection guide](https://phoenix.hexdocs.pm/channels.html).
- **C2:** Topics, channel callbacks, socket handlers, and transport separation support chat, notifications, device communication, and other long-lived application interactions through the same abstractions.
- **C3:** Local PubSub distribution and forwarding to other nodes separate local fan-out from inter-node propagation. The guide describes that mechanism and the lightweight-process structure; no numerical capacity claim is needed to see the scaling design.

### 7. [playframework/playframework](https://github.com/playframework/playframework)

**Language / role:** Scala and Java; asynchronous web framework. The inspected 3.0 documentation uses Apache Pekko terminology.

Play is especially useful for studying why returning a future does not by itself make an application nonblocking.

- **C1:** Blocking work placed on the wrong dispatcher can exhaust request-processing capacity. Thread switches also affect application class-loader access, particularly during development reloads; `ClassLoaderExecutionContext` preserves that context for asynchronous callbacks. These failure modes are explained in the [thread-pool guide](https://www.playframework.com/documentation/3.0.x/ThreadPools).
- **C3:** Internal I/O pools, the default application dispatcher, and dedicated execution contexts are distinct resources. The guide connects database-bound pool sizing to connection-pool capacity and describes separating expensive work by workload. This gives an engineer an understandable architecture for investigating latency and saturation.

### 8. [ktorio/ktor](https://github.com/ktorio/ktor)

**Language / role:** Kotlin; client/server framework monorepo. This entry concerns `ktor-server`, especially application lifetime and server plugins.

- **C1:** The application owns a `SupervisorJob` and a coroutine scope. In the inspected [Application implementation](https://github.com/ktorio/ktor/blob/main/ktor-server/ktor-server-core/common/src/io/ktor/server/application/Application.kt), `disposeAndJoin()` cancels and joins that job before uninstalling plugins; the older non-joining disposal method is deprecated. This is a compact example of coordinating asynchronous work with teardown.
- **C2:** Plugins can intercept calls, transform incoming and outgoing bodies, attach request-local attributes, and respond to lifecycle hooks. The [custom-server-plugin guide](https://ktor.io/docs/server-custom-plugins.html) separates these operations and explains route-scoped validation ordering.

Study the contrast between the accessible plugin API and the underlying application lifetime: extension points must remain valid while work is running and be dismantled in a defined order.

### 9. [drogonframework/drogon](https://github.com/drogonframework/drogon)

**Language / role:** C++; asynchronous HTTP application framework.

The most valuable reading is the unusually concrete explanation of event-loop ownership and callbacks that resume on a different thread from the original HTTP handler.

- **C1:** I/O belongs to an associated event loop; calls from another thread enqueue work there. A synchronous operation that waits for a callback on its own blocked loop deadlocks. These dependencies are illustrated in the official [threading-model document](https://github.com/drogonframework/drogon/wiki/ENG-FAQ-1-Understanding-drogon-threading-model).
- **C3:** “Fast DB” clients share HTTP-server threads to avoid cross-thread submission and context switches, creating an explicit tradeoff: their queries must remain asynchronous. Coroutine APIs improve sequencing without removing event-loop blocking or race hazards.

This is an instructive codebase for understanding the performance consequences of where work executes, beyond simply selecting an asynchronous API.

### 10. [mojolicious/mojo](https://github.com/mojolicious/mojo)

**Language / role:** Perl; web framework with rendering and nonblocking response support.

Study the transition from a controller's request-local stash to templated, encoded, or incrementally streamed responses.

- **C1:** Automatic rendering must be disabled with `render_later` when asynchronous work will finish the response later. Template expressions escape HTML/XML-sensitive characters by default, with explicit escape bypasses. Response streams also need a defined ending. The [rendering guide](https://docs.mojolicious.org/Mojolicious/Guides/Rendering) exposes all three correctness boundaries.
- **C2:** The renderer supports pluggable template systems and encoding handlers while helpers and plugins extend a shared controller interface.
- **C3:** Streaming `write`/`write_chunk` calls accept drain callbacks that run after preceding bytes are written. This lets applications sequence output instead of generating the whole response eagerly, and can deliver the document head before the rest of the page.

## Composable routers, plugin systems, and configuration

### 11. [Pylons/pyramid](https://github.com/Pylons/pyramid)

**Language / role:** Python; extensible WSGI web framework.

Pyramid stands out for treating application configuration as a system that can be validated and composed, rather than an incidental sequence of mutations.

- **C1:** Registering indistinguishable views creates an ambiguity and raises `ConfigurationConflictError` before the application starts. Committing configuration changes the conflict boundary, so ordering and overrides have deliberate semantics. See [advanced configuration](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/advconfig.html).
- **C2:** `Configurator.include()` composes configuration from other packages and records the inclusion relationship, allowing the including application to override included registrations. Two-phase configuration reduces accidental dependence on statement order and gives reusable packages a defined extension mechanism.

Experienced engineers can study this as an alternative to “last registration wins” designs, particularly when building systems that combine independently authored modules.

### 12. [jeremyevans/roda](https://github.com/jeremyevans/roda)

**Language / role:** Ruby; routing-tree web toolkit built around Rack and plugins.

Roda's [repository architecture and routing documentation](https://github.com/jeremyevans/roda#readme) is substantive: routing branches execute ordinary code, matchers consume path segments, and plugins extend the request, response, and application interfaces. The recommendation to freeze applications is an architectural technique, not a claim that arbitrary application state becomes safe.

- **C2:** Routing-tree composition permits shared work at a branch, while a small core delegates optional behavior to plugins. This makes the boundary between application control flow and framework extension unusually visible.
- **C1:** The [RouteCsrf plugin documentation](https://roda.jeremyevans.net/rdoc/classes/Roda/RodaPlugins/RouteCsrf.html) specifies method-and-path-bound tokens, explains the danger of exposing the underlying secret through readable session cookies, and distinguishes strict defaults from per-call exceptions. It is a useful study of a security invariant integrated with routing.

### 13. [expressjs/express](https://github.com/expressjs/express)

**Language / role:** JavaScript; Node.js routing and middleware framework.

Express is worth studying for how much lifecycle behavior emerges from a compact continuation-based interface, and where that interface needs explicit error rules.

- **C2:** Application middleware, mounted sub-stacks, and router middleware share the request/response/`next` contract. A handler either ends the request or transfers control; the [middleware guide](https://expressjs.com/en/guide/using-middleware/) shows how this supports independent, reusable route groups.
- **C1:** The [error-handling guide](https://expressjs.com/en/guide/error-handling/) distinguishes thrown synchronous errors, rejected promises returned by handlers, and callback errors that must be forwarded manually. Passing an error skips ordinary middleware. These distinctions are essential to avoiding hanging requests and errors that escape the framework.

The cited documentation is for Express 5; its automatic forwarding of returned promise rejections should not be assumed for older major versions.

### 14. [fastify/fastify](https://github.com/fastify/fastify)

**Language / role:** JavaScript with TypeScript interfaces; Node.js framework centered on plugin scopes and lifecycle hooks.

- **C2:** Plugin registration creates hierarchical contexts: children inherit parent decorators and hooks, while parents do not automatically receive child additions. The [encapsulation guide](https://fastify.dev/docs/latest/Reference/Encapsulation/) shows how routes with different authentication requirements can coexist without globally applying every hook.
- **C1:** Request/reply decorators reject shared reference values because otherwise mutable objects would be shared across requests. Decorator dependencies are checked at boot, and asynchronous setup must use plugin registration. See the [decorator design guide](https://fastify.dev/docs/latest/Reference/Decorators/).
- **C3:** Defining request and reply fields before object creation preserves shapes useful to the JavaScript engine; adding fields during processing can cause deoptimization. The same guide connects an extension API to a specific runtime cost.

Study encapsulation and object initialization together: the framework addresses both behavioral scope and per-request overhead.

### 15. [go-chi/chi](https://github.com/go-chi/chi)

**Language / role:** Go; HTTP router and optional middleware collection.

Chi provides a manageable implementation for studying a router that retains standard-library interoperability as its main abstraction boundary.

- **C2:** Routes, mounted subrouters, and middleware use ordinary `net/http` handlers; request context carries cancellation and request-scoped values. The [repository's router and middleware documentation](https://github.com/go-chi/chi#readme) explains how inline middleware and groups compose without requiring a proprietary handler type.
- **C3:** The [Mux implementation](https://github.com/go-chi/chi/blob/master/mux.go) combines a radix-tree router with a precomputed handler chain and a `sync.Pool` of routing contexts. `ServeHTTP` reuses an existing parent-router context or obtains, resets, and later returns one to the pool. Its comments also identify remaining context-allocation costs.

The source makes the relationship between modular routing and allocation control visible without requiring a large framework tour.

## Middleware contracts and asynchronous composition

### 16. [elixir-plug/plug](https://github.com/elixir-plug/plug)

**Language / role:** Elixir; web-application interface and middleware library.

Plug deserves a separate entry from Phoenix because it implements the reusable connection and pipeline contract rather than Phoenix's channel/application conventions.

- **C1:** `Plug.Conn` records unfetched request fields, request-local assigns, and response lifecycle states. Operations can reject modifications after a response is sent, chunked, or upgraded; streaming code must handle failed chunk delivery. These rules are specified in the [connection API](https://hexdocs.pm/plug/Plug.Conn.html).
- **C2:** Function plugs and module plugs compose through `init/1` and `call/2`. A built pipeline is itself a plug, usable inside another pipeline or by a web-server adapter. [Plug.Builder](https://hexdocs.pm/plug/Plug.Builder.html) documents compilation, initialization choices, and halting downstream execution.

This is a useful comparison with callback-based middleware: control state travels explicitly in the connection value.

### 17. [tower-rs/tower](https://github.com/tower-rs/tower)

**Language / role:** Rust; asynchronous service and middleware abstractions. The relevant monorepo pieces include `tower-service` and the middleware built around its contract. Tower is protocol-generic, but its direct role in HTTP application stacks makes it fit this category.

- **C1:** A successful `poll_ready` may reserve capacity for a later `call`; dropping the service or response future must release reserved resources. Calling an unready service may panic, and a clone need not inherit the original instance's readiness. The [Service contract](https://docs.rs/tower-service/latest/tower_service/trait.Service.html) explains these invariants and demonstrates the clone trap.
- **C2:** A service maps a request to a future yielding a response or error, equally applicable to clients and servers. Wrappers such as the documented timeout example can propagate readiness and compose without knowing the underlying protocol implementation.

Study this repository when designing an asynchronous extension interface that must express capacity as well as results.

### 18. [tokio-rs/axum](https://github.com/tokio-rs/axum)

**Language / role:** Rust; HTTP routing and request-handling framework integrated with Tower.

- **C2:** Middleware can wrap a whole router, route groups, method routers, or handlers through Tower services and layers. This reuses an external middleware contract instead of creating an isolated framework-specific ecosystem. The [middleware architecture guide](https://docs.rs/axum/latest/axum/middleware/) is the best starting point.
- **C1:** That guide carefully explains the mismatch between routing and readiness: the router may not know which service it needs until it has the request. Axum drives readiness inside the response future, so backpressure-sensitive services need special treatment, such as wrapping the entire application or shedding load. Errors from middleware also need conversion into HTTP responses through the appropriate error-handling layer.

The value here is the documented integration boundary, including what an otherwise compatible Tower service must not assume.

### 19. [actix/actix-web](https://github.com/actix/actix-web)

**Language / role:** Rust; web framework. Focus on the `actix-web` application, middleware, and HTTP-worker model within the repository.

- **C1:** Each worker receives a separate application instance; shared state requires deliberate `Arc`/`Data` use and synchronization. Blocking handlers or extractors stall a worker, and graceful shutdown allows a bounded completion period before remaining workers are dropped. The [server guide](https://actix.rs/docs/server/) explains these lifetime and concurrency boundaries.
- **C2:** Middleware separates a `Transform` builder from the resulting `Service`, with a chain assembled for each thread. The [middleware reference](https://docs.rs/actix-web/latest/actix_web/middleware/) explains registration at application, scope, and resource levels and the reverse wrapping order.
- **C3:** Worker-local state avoids mandatory shared-state locking, while asynchronous handlers let workers progress on other requests. The server guide explicitly discusses the costs introduced when state is shared.

### 20. [Kludex/starlette](https://github.com/Kludex/starlette)

**Language / role:** Python; ASGI framework and toolkit. `Kludex/starlette` is the canonical repository opened for this research; older references may use the former owner path.

Starlette is especially useful for studying the difference between convenient request/response middleware and middleware operating directly on asynchronous protocol messages.

- **C1:** `BaseHTTPMiddleware` has documented `contextvars` propagation limitations that can affect middleware elsewhere in the stack. Error-wrapper placement also matters: CORS wrapping must include externally generated error responses when those responses need CORS headers. These interactions appear in the [in-repository middleware documentation](https://github.com/Kludex/starlette/blob/main/docs/middleware.md).
- **C2:** Pure ASGI middleware composes through `scope`, `receive`, and `send`, allowing event interception and interoperability with other ASGI applications and servers. The document explains this interface alongside the higher-level middleware API and its limitations.

## Functional and typed framework designs

### 21. [pedestal/pedestal](https://github.com/pedestal/pedestal)

**Language / role:** Clojure; server-side libraries. Focus on the interceptor subsystem and its HTTP integration.

Pedestal makes the middleware execution machine explicit in data, which is useful for understanding dynamic pipelines and asynchronous continuation.

- **C1:** Execution has forward `:enter`, reverse `:leave`, and reverse `:error` phases. Handling an error can resume normal unwinding; returning a `core.async` channel suspends the chain and moves continuation to asynchronous processing. The [interceptor-chain API](https://pedestal.io/api/0.8/io.pedestal.interceptor.chain.html) specifies these transitions and termination behavior.
- **C2:** Context maps, an extensible interceptor queue, callbacks, and observers provide reusable processing machinery beyond a fixed list of HTTP filters. Interceptors can enqueue further work or terminate the remaining entry phase while preserving the leave phase.

The API links directly to implementation source, making it a practical starting point for tracing the state machine rather than treating interceptors as opaque callbacks.

### 22. [http4s/http4s](https://github.com/http4s/http4s)

**Language / role:** Scala; functional HTTP toolkit and application middleware. Focus on server middleware and effectful request/response composition.

- **C1:** Producing a `Response` is not the same as finishing its body stream. The [BracketRequestResponse API, version 0.23](https://http4s.org/v0.23/api/org/http4s/server/middleware/BracketRequestResponse%24.html) ties acquisition/release to the full interaction and documents a critical limitation: discarding the response body after applying the middleware can prevent release and leak resources. Outer placement is therefore recommended.
- **C2:** Middleware variants work with `HttpApp`, `HttpRoutes`, contextual requests, generic effects, and `Resource`-based acquisition. The same lifetime abstraction can support metrics or other per-request resources without being coupled to one handler's business logic.

This is valuable precisely because the documentation exposes where ordinary effect bracketing is insufficient and where application composition can still break cleanup assumptions.

### 23. [yesodweb/yesod](https://github.com/yesodweb/yesod)

**Language / role:** Haskell; web-framework monorepo built on WAI. Relevant subsystems include `yesod-core` routing/handlers and the reusable subsite model.

- **C1:** Routing generates an intermediate route datatype and typed parameter conversions. Invalid `PathPiece` inputs can be rejected before the handler executes; overlapping routes are checked conservatively, with an explicit escape hatch and first-match semantics when overlap is allowed. See the [routing and handlers chapter](https://www.yesodweb.com/book/routing-and-handlers).
- **C2:** A route declaration supplies both dispatch and typed URL construction. Subsites let an application mount reusable functionality, while parameter typeclasses extend parsing to domain-specific values.

Study the boundary between compile-time structure and runtime validity. The guide explicitly notes that a well-typed URL can still refer to a nonexistent database record: type-safe routing does not imply successful business lookup.

### 24. [ocsigen/eliom](https://github.com/ocsigen/eliom)

**Language / role:** OCaml; framework for client/server web applications. This entry emphasizes server-side state and service scopes rather than separately counting Ocsigen's other repositories.

- **C2:** Scoped references and service registration distinguish a request, browser tab/client process, browser session, session group, site, and global state. Persistence is a separate choice. The [sessions and server-state manual](https://ocsigen.org/eliom/latest/manual/server-state) shows how these abstractions express user state without forcing every application to invent its own scope system.
- **C1:** Volatile service state and persistent data state can diverge after restart; selectively discarding only one kind of state can likewise desynchronize a session. Secure scopes, scope-specific cookies, timeout rules, and explicit discard operations make these correctness boundaries visible.

The manual also acknowledges limitations around resource cleanup and evolving group-discard semantics. Those caveats make this a useful architectural study, not a blanket recommendation for every deployment.

## Frameworks spanning server rendering and browser execution

### 25. [vercel/next.js](https://github.com/vercel/next.js)

**Language / role:** Primarily TypeScript/JavaScript, with Rust tooling; full-stack React framework monorepo. Relevant here are the Next.js application runtime, routing, rendering, and cache semantics, not the build tooling alone.

- **C1:** Route segments can impose conflicting static/dynamic cache requirements. The inspected [caching guide for the previous model](https://nextjs.org/docs/app/guides/caching-without-cache-components) specifies incompatible combinations, request-time behavior, and how parent/child settings interact. This is a substantial consistency problem spanning layouts, pages, and data access.
- **C3:** Persistent data caching, time-based and tagged invalidation, per-render request deduplication, and preloading address different costs and lifetimes. The guide separates their controls rather than presenting caching as one global switch.

**Version caveat:** This source is explicitly labeled the previous model, without Cache Components. It is an entry point for studying that documented architectural lineage, not a claim that its defaults describe every current Next.js configuration.

### 26. [sveltejs/kit](https://github.com/sveltejs/kit)

**Language / role:** JavaScript/TypeScript; full-stack Svelte application framework monorepo. Focus on the Kit runtime and its server/browser boundary; deployment adapters belong to the same repository and are not counted separately.

- **C1:** Shared server variables can leak one user's state to another. Kit's application state uses component-tree context, and SSR propagation differs from browser reactivity. Separately, the framework rejects direct or indirect browser imports of server-only modules. See [state management](https://svelte.dev/docs/kit/state-management) and [server-only module enforcement](https://svelte.dev/docs/kit/server-only-modules).
- **C3:** Server-side internal fetches can call endpoint handlers directly without an HTTP round trip. Responses consumed during SSR can be serialized into HTML and reused during hydration, avoiding another network request while preserving the rendered data. The state-management guide explains that mechanism and its header-serialization boundary.

This is a useful study of how request isolation, module boundaries, and rendering optimizations interact in one application framework.

## Coverage, search method, and limitations

Discovery used more than twenty distinct live search formulations, followed by opening canonical GitHub roots and additional primary material for every retained repository. Search angles included integrated MVC kernels; Python WSGI/ASGI middleware; Node.js plugin encapsulation; Rust service readiness and backpressure; Go router composition; C++ event-loop ownership; JVM dispatchers and coroutine lifetime; Elixir channels and connection pipelines; Clojure interceptors; Haskell typed routing; Scala effect/resource middleware; Perl streaming; server-rendered JavaScript applications; and OCaml/Crystal/Nim framework communities.

Representative formulations included `Rust web framework middleware service Tower Axum Actix architecture`, `site:github.com fastify encapsulation middleware hooks framework`, `site:pedestal.io interceptor error async context queue`, `site:yesodweb.com book routing dispatch type safe overlapping routes`, `site:http4s.org middleware resource body stream`, and `web framework middleware architecture OCaml Crystal Nim GitHub`. Later searches for configuration conflicts, structured concurrency, backpressure, and routing-tree plugins mostly added variations of mechanisms already represented; the additional scoped-state design in Eliom warranted expanding the selection to 26.

Important selection boundaries and limitations:

- Framework layers are not conflated. Phoenix and Plug, and Axum and Tower, are retained separately because their independent repositories implement materially different abstractions. The report explains those boundaries. No fork is counted as an independent implementation.
- Searches also surfaced Kemal, Amber, Opium, Clastic, and smaller frameworks. They were not fully vetted for retention here; their omission is not a negative quality or maintenance judgment. This is a diverse selection, not an exhaustive ecosystem inventory.
- Repository pages were checked for canonical identity and archive/move notices; none of the retained pages displayed an archive notice. No retained entry is presented as an official mirror or historical-only implementation. This does **not** establish a uniform maintenance cadence or current support window, and recent pushes or stars were not used to justify quality.
- Evidence consists of opened official repository pages, implementation files, project API references, architectural guides, and selected migration/release documentation. Search snippets alone were not used to qualify retained entries. The Starlette documentation site failed to load during one fetch, so its independently opened in-repository middleware guide supplied the implementation evidence instead.
- C4 is awarded selectively where migration history and compatibility mechanisms were actually inspected. Other entries can qualify through C1–C3 without an unsupported claim about age. Performance conclusions concern mechanisms and tradeoffs; no cross-framework speed ranking or numerical benchmark claim is made.
- No candidate code was executed, dependencies installed, repositories cloned, or external services modified. Documentation explains intended behavior; this report is not a security audit, a test-suite execution, or proof of all implementation paths.
