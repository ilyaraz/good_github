# HTTP client libraries

Research date: **2026-10-09**.

This selection covers **27 GitHub repositories** implementing reusable outbound HTTP clients, client protocol engines, or substantial client abstraction layers. It spans embedded systems, server workloads, browsers, mobile applications, and scientific computing. For repositories that also implement servers, only the client subsystem is evaluated. The emphasis is on code an experienced engineer can study for ownership, protocol state, cancellation, retries, extensibility, and resource control—not popularity or a performance ranking.

Repository identities, canonical URLs, default branches, and archive flags were checked through GitHub's API, with repository pages and implementation/documentation sources also inspected. None of the selected repositories was marked archived at research time. Branch links describe the inspected development sources; they do not imply that every described behavior is in every published release. Apache HttpClient and Ruby HTTPX are explicitly identified as mirrors below.

## Criteria legend

- **C1 — Correctness:** difficult invariants, concurrency, adversarial input, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces supporting different applications or execution environments.
- **C3 — Performance and structure:** concrete resource or performance constraints addressed through understandable architecture.
- **C4 — Evolution:** years of changes accompanied by evidence of compatibility work, testing, or complexity management.

The criteria assignments are engineering judgments grounded in the linked primary evidence. They are not claims that every component is uniformly exemplary.

## Native and embedded clients

### [curl/curl](https://github.com/curl/curl)

**C — libcurl, the reusable transfer library within the curl repository.** Study how a portable networking engine separates individual transfers from the application's event loop and from the lifetime of reusable connections.

- **C1:** A completed transfer need not have succeeded; completion messages, handle removal, and handle cleanup are separate responsibilities. Connection reuse additionally depends on framing, peer shutdown, receive errors, and whether the connection is still alive. These are useful examples of distinguishing protocol completion from resource lifetime. [Multi interface](https://curl.se/libcurl/c/libcurl-multi.html), [connection reuse](https://everything.curl.dev/transfers/conn/reuse.html).
- **C2, C3:** Easy handles hold transfer configuration while multi handles drive concurrent transfers through socket and timer callbacks. The multi handle also owns a shared connection cache, allowing transfer objects to be replaced without throwing away established connections. The two documents above are the recommended entry points.

### [yhirose/cpp-httplib](https://github.com/yhirose/cpp-httplib)

**C++ — header-only HTTP/HTTPS library; focus on its client and streaming APIs.** A useful smaller-scale contrast to event-loop engines: the project explicitly uses blocking sockets and supports HTTP/1.1 rather than HTTP/2 or HTTP/3. [Repository documentation](https://github.com/yhirose/cpp-httplib).

- **C2:** Its client exposes buffered requests, a lower-level `StreamHandle`, and an iterator-style streaming result. Study how these interfaces offer progressively more control over response consumption without requiring a separate application framework.
- **C3:** Streaming reads directly from the socket to avoid holding the whole body. The ownership tradeoff is explicit: these streaming APIs dedicate a connection to the result and close it on destruction, whereas ordinary client calls can reuse connections. Results are single-pass and must be consumed from one thread. [Streaming architecture and ownership guide](https://github.com/yhirose/cpp-httplib/blob/master/README-stream.md).

### [FreeRTOS/coreHTTP](https://github.com/FreeRTOS/coreHTTP)

**C — embedded implementation of a subset of HTTP/1.1.** Study a client whose memory and transport contracts are exposed directly, with proof infrastructure alongside the implementation.

- **C1:** The public contract distinguishes partial responses, insufficient buffer space, malformed chunks, invalid content lengths, and extraneous response data. It specifies when application buffers are temporarily owned by the library. The repository also contains CBMC proof targets for sending, header construction, and parser callbacks; this is evidence of verification effort, not a claim of universal correctness. [Public API and invariants](https://github.com/FreeRTOS/coreHTTP/blob/main/source/include/core_http_client.h), [CBMC proof entry point](https://github.com/FreeRTOS/coreHTTP/tree/main/test/cbmc/proofs).
- **C2, C3:** A supplied transport interface decouples protocol processing from networking. Caller-provided buffers can serve first as request-header storage and then as response storage, making memory reuse an architectural contract rather than an incidental optimization. Start with `HTTPRequestHeaders_t`, `HTTPResponse_t`, and `HTTPClient_Send` in the API header.

## Rust: protocol engine, policy client, and blocking client

### [hyperium/hyper](https://github.com/hyperium/hyper)

**Rust — HTTP client/server protocol engine; focus on client connections and bodies.** Study the boundary between a future that drives a connection and the handle used to submit requests.

- **C1:** The HTTP/1 client documents the race between readiness checks and peer closure, the effect of dropping an in-flight request future, and the need to preserve already-read bytes when handing an upgraded connection back to the application. [HTTP/1 connection implementation](https://github.com/hyperium/hyper/blob/master/src/client/conn/http1.rs).
- **C2, C3:** Generic I/O and `Body` contracts permit different transports and body producers. Incoming bodies advance through polling; consuming frames incrementally preserves backpressure and avoids compulsory whole-body buffering. This is a protocol building block, so study it together with a higher-level client such as reqwest to see where policy belongs. [Body abstraction and backpressure](https://github.com/hyperium/hyper/blob/master/src/body/mod.rs).

### [seanmonstar/reqwest](https://github.com/seanmonstar/reqwest)

**Rust — application-facing HTTP client.** Study how redirect policy and connection reuse are layered over lower-level HTTP machinery.

- **C1:** Redirect handling bounds the default chain, removes sensitive headers when the scheme/host/port changes, suppresses referrers on HTTPS-to-HTTP transitions, and asks whether a body can be cloned for replay. Custom redirect policies explicitly inherit responsibility for their own loop bounds. [Redirect implementation and tests](https://github.com/seanmonstar/reqwest/blob/master/src/redirect.rs).
- **C2, C3:** `ClientBuilder` collects policy and transport configuration; a cheaply cloned `Client` shares its internal pool through `Arc`. Pool lifetime and idle limits are explicit, encouraging applications to reuse a client instead of repeatedly paying connection setup costs. [Async client implementation](https://github.com/seanmonstar/reqwest/blob/master/src/async_impl/client.rs).

### [algesten/ureq](https://github.com/algesten/ureq)

**Rust — blocking HTTP client with a deliberately smaller execution model.** Study how a synchronous client still has substantial pool, deadline, and transport correctness work.

- **C1:** A connection with unconsumed input is rejected for reuse, and a socket probe rejects unexpected additional data. Expired timeout budgets fail before reaching transports that might otherwise turn a zero timeout into extra grace time. Incompatible requests are prevented from both borrowing from and returning to the agent's pool. [Pool implementation](https://github.com/algesten/ureq/blob/main/src/pool.rs).
- **C2, C3:** Connector and transport interfaces sit behind an agent-owned pool; idle pruning tracks both total storage and per-host positions. Shared agents provide reuse without requiring an async runtime. The crate documentation also explains explicit TLS-provider selection to avoid accidental changes from additive dependency features. [Crate architecture and configuration](https://github.com/algesten/ureq/blob/main/src/lib.rs).

## JVM and Scala

### [lysine-dev/okhttp](https://github.com/lysine-dev/okhttp)

**Kotlin/Java — HTTP client for JVM, Android, and GraalVM.** The former `square/okhttp` URL redirected to this canonical repository during verification. Study the distinction between a URL, a reusable connection address, and a particular route through DNS, proxies, and TLS configuration.

- **C1:** Route recovery and fast fallback coordinate alternative addresses, cancel losing TCP attempts, and perform TLS on the winner; a TLS failure can restart selection among remaining routes. This separates transport races from authentication and protocol negotiation. [Connection design](https://lysine.dev/okhttp/features/connections/).
- **C2, C3:** Address-based pooling supports HTTP/1 connection reuse and HTTP/2 multiplexing while route objects retain the dynamic connection choices. The historical Java-to-Kotlin migration is also instructive: binary compatibility was checked with `japicmp`, and Java versus Kotlin source compatibility was treated separately. [Migration and compatibility design](https://lysine.dev/okhttp/changelogs/upgrading_to_okhttp_4/).

### [apache/httpcomponents-client](https://github.com/apache/httpcomponents-client)

**Java — official GitHub mirror of Apache HttpClient; focus on the `httpclient5` subsystem.** Study an enterprise client with explicit route, endpoint, connection-operator, and pool boundaries.

- **C1:** `PoolingHttpClientConnectionManager` serves multiple execution threads, leases connections by route, enforces a maximum lifetime independent of ordinary expiry, and guards shutdown with an atomic state transition. The source exposes where concurrency and resource ownership meet.
- **C2, C3:** The manager implements both the client connection-manager interface and pool-control interface; connection construction, DNS/TLS configuration, and pool concurrency/reuse policy are separate collaborators. Per-route and aggregate limits make contention and resource budgeting inspectable. Start with the class contract and constructors, then follow lease/release behavior in [the connection-manager implementation](https://github.com/apache/httpcomponents-client/blob/master/httpclient5/src/main/java/org/apache/hc/client5/http/impl/io/PoolingHttpClientConnectionManager.java). The [project README](https://github.com/apache/httpcomponents-client/blob/master/README.md) identifies HttpCore as a separate dependency.

### [softwaremill/sttp](https://github.com/softwaremill/sttp)

**Scala — typed client API with interchangeable transport backends.** Study a substantial abstraction layer whose main contribution is specifying requests, effects, and response handling across execution models.

- **C1:** Streaming request types encode the required stream capability; the compiler rejects sending them through incompatible backends. WebSocket requests similarly carry effect/capability requirements. This moves a class of runtime integration mistakes into the type system. [Request type design](https://sttp.softwaremill.com/en/latest/requests/type.html).
- **C2:** Backends cover synchronous code, futures, functional effects, streaming, JVM, JavaScript, and Native. Wrapping backends adds tracing, metrics, redirects, or caching without changing the request description. Transport work belongs to those backends; sttp is valuable for studying how to preserve their differences while offering one API. [Backend architecture](https://sttp.softwaremill.com/en/latest/backends/summary.html).

## Python

### [urllib3/urllib3](https://github.com/urllib3/urllib3)

**Python — reusable HTTP connection-pooling and transport library.** Study the precise relationship between response consumption, admission control, and safe socket reuse.

- **C1:** A streamed response must be consumed or drained before releasing its connection for reuse. Closing a response and returning a reusable connection are deliberately different operations; otherwise unread bytes could contaminate a later exchange.
- **C2, C3:** `PoolManager` manages host-specific pools, while each `ConnectionPool` manages individual connections. A particularly useful contract is that `maxsize` normally limits retained connections, but `block=True` turns it into a limit on concurrent connections to that host. The docs also explain the memory/call-overhead tradeoff in upload block sizes. [Advanced pooling, streaming, and upload guide](https://github.com/urllib3/urllib3/blob/main/docs/advanced-usage.rst) is the entry point for all these mechanisms.

### [encode/httpx](https://github.com/encode/httpx)

**Python — synchronous and asynchronous application HTTP client.** Study a common request/response model paired with explicit transport substitution and resource lifetime.

- **C1:** Manual async streaming requires eventual `Response.aclose()`; otherwise connections remain open. The documentation distinguishes client lifetime from response lifetime and warns against repeatedly creating clients inside a hot loop. [Async lifecycle and streaming](https://github.com/encode/httpx/blob/master/docs/async.md).
- **C2:** Sync and async base transports support ordinary HTTP, direct WSGI/ASGI application calls, mock transports, and custom wrappers. URL-pattern mounts route requests to different transports. The transport retry option is narrowly defined for connection errors/timeouts, which is useful evidence of a deliberate policy boundary rather than an all-purpose retry promise. [Transport architecture](https://github.com/encode/httpx/blob/master/docs/advanced/transports.md).

### [aio-libs/aiohttp](https://github.com/aio-libs/aiohttp)

**Python — asyncio client/server framework; focus on `ClientSession` and connectors.** Study a client where sessions hold application state while connectors control transport resources.

- **C2:** `ClientSession` owns cookies and a connection pool, accepts replaceable connectors, supports request middleware, and supplies tracing callbacks with per-request context. TCP and Unix-domain connectors allow the request API to remain stable across transports.
- **C3:** Connector configuration separates total connection limits, per-endpoint limits, and DNS-cache lifetime. Session ownership of connectors is the default, with an explicit `connector_owner=False` contract for sharing. This is a concrete model for tuning concurrency while preserving a comprehensible shutdown boundary. Start with the session, tracing, and connector sections of [Advanced Client Usage](https://github.com/aio-libs/aiohttp/blob/master/docs/client_advanced.rst). The server subsystem is outside this entry's scope.

## JavaScript and TypeScript

### [nodejs/undici](https://github.com/nodejs/undici)

**JavaScript — Node.js HTTP transport and Fetch implementation.** Study the low-level dispatcher contract underlying higher-level request helpers.

- **C1:** Pipeline behavior depends on idempotency; streamed request bodies have narrower retry possibilities. Bodies must be consumed or destroyed, and graceful `close` differs from abrupt `destroy`. These details expose the failure coupling between requests sharing a connection.
- **C2, C3:** Concrete dispatchers share one lifecycle interface. Dispatch reports when the caller must await `drain`; response controllers offer pause/resume for backpressure. The API also documents a tradeoff between timer overhead and timeout precision. [Dispatcher contract](https://github.com/nodejs/undici/blob/main/docs/docs/api/Dispatcher.md) is a concentrated entry point for all three criteria. Higher-level APIs should be distinguished from this less-stable low-level extension surface.

### [sindresorhus/got](https://github.com/sindresorhus/got)

**TypeScript — application-oriented Node.js HTTP client.** Study configurable resilience and the construction of reusable API clients on top of a general request library.

- **C1:** Retry policy filters methods, status codes, and network errors, bounds `Retry-After`, and guards against delays exceeding Node's timer range. The documentation explains how overriding delay calculation can weaken default safeguards. [Retry policy](https://github.com/sindresorhus/got/blob/main/documentation/7-retry.md).
- **C2:** Extended instances compose defaults, hooks, contextual options, and handlers to add authentication, domain-specific errors, and response metadata. The plugin guide explicitly treats stream calls separately from promise-returning calls, illustrating why apparently uniform APIs still need distinct lifecycle handling. [Client/plugin construction](https://github.com/sindresorhus/got/blob/main/documentation/lets-make-a-plugin.md).

### [axios/axios](https://github.com/axios/axios)

**JavaScript — browser and Node.js HTTP client abstraction.** Study the nontrivial boundary between request configuration, interceptor execution, and platform adapters.

- **C1:** Dispatch checks cancellation before sending and again when an adapter resolves or rejects. Request configuration is normalized at the dispatch boundary; response transformation temporarily attaches context and cleans it in `finally` blocks. [Dispatch implementation](https://github.com/axios/axios/blob/v1.x/lib/core/dispatchRequest.js).
- **C2:** Config merging, header normalization, conditional interceptors, and platform adapter selection are separate mechanisms. The main class has distinct synchronous and promise-based interceptor execution paths, including rejection handling and compatibility options for ordering. This makes a useful study of preserving one public API across heterogeneous platforms and extension behaviors. [Axios core](https://github.com/axios/axios/blob/v1.x/lib/core/Axios.js).

## Go, PHP, and .NET application clients

### [go-resty/resty](https://github.com/go-resty/resty)

**Go — HTTP/REST client layered on Go's HTTP transport.** Study how retry policy and a request/response processing pipeline can be added without replacing the underlying networking stack. The inspected default branch is `v3`.

- **C1:** Retry handling distinguishes certificate/configuration failures from retryable network conditions, parses both forms of `Retry-After`, rejects negative delays, and saturates values that would overflow a duration. Backoff has explicit bounds and jitter. [Retry implementation](https://github.com/go-resty/resty/blob/v3/retry.go).
- **C2:** Request preparation, response parsing, and saving bodies to files are middleware functions. In v3, response middleware continues even after errors, carrying them in `CascadeError`; callers must understand that contract. Transport settings and customizable hooks sit beside these reusable pipeline interfaces. [Client and middleware contracts](https://github.com/go-resty/resty/blob/v3/client.go).

### [guzzle/guzzle](https://github.com/guzzle/guzzle)

**PHP — extensible HTTP client with promise-based handlers.** Study both middleware composition and the difficult lifecycle boundary between PHP callbacks and libcurl. The stable guide inspected describes Guzzle 7; the implementation link follows the repository's inspected `8.2` default branch.

- **C2:** Handlers map a PSR request plus options to a promise of a response; middleware wraps that contract. Ordering determines whether cookies, redirects, body preparation, and HTTP-error handling run correctly. [Handlers and middleware guide](https://docs.guzzlephp.org/en/stable/handlers-and-middleware.html).
- **C1, C3:** `CurlMultiHandler` integrates native transfers with the promise queue. Its explicit nesting depth and deferred-add/cancel/close bookkeeping handle callbacks that re-enter the event loop while native work is in progress; connection-cap options expose resource budgets. This is substantial implementation work beyond a thin cURL wrapper. [Multi-handler implementation](https://github.com/guzzle/guzzle/blob/8.2/src/Handler/CurlMultiHandler.php).

### [restsharp/RestSharp](https://github.com/restsharp/RestSharp)

**C# — .NET HTTP API client built on `HttpClient`.** Study request modeling, serialization, cancellation, and ownership above an existing platform transport.

- **C1:** The execution path links a per-request timeout token with caller cancellation, classifies timeout versus abort responses, disposes intermediate redirect responses, and rejects use after disposal. [Async execution implementation](https://github.com/restsharp/RestSharp/blob/dev/src/RestSharp/RestClient.Async.cs).
- **C2:** `RestClient` supports custom serializers, authentication, interceptors, supplied `HttpClient` instances, and message-handler composition. The configuration guide distinguishes who disposes an externally supplied client or handler, and when supplied handlers bypass the usual option configuration. Those distinctions are useful for dependency-injection and testing integrations. [Configuration and ownership guide](https://restsharp.dev/docs/advanced/configuration/).

## Ruby

### [lostisland/faraday](https://github.com/lostisland/faraday)

**Ruby — HTTP client abstraction with adapters and Rack-style middleware.** Study how to stabilize a reusable request pipeline while allowing independently maintained transports.

- **C2:** `RackBuilder` composes middleware around a terminal adapter, builds a common environment, and locks the stack after constructing the application. This makes ordering, registration, duplication, and mutation boundaries visible. [Builder implementation](https://github.com/lostisland/faraday/blob/main/lib/faraday/rack_builder.rb).
- **C4:** The [historical changelog](https://github.com/lostisland/faraday/blob/main/CHANGELOG.md) records staged adapter extraction and Ruby-version CI work in 2020–2022. The [upgrade guide](https://github.com/lostisland/faraday/blob/main/UPGRADING.md) explains compatibility staging through 1.x dependencies before the 2.0 split. A [2026 release on the 1.x line](https://github.com/lostisland/faraday/releases/tag/v1.10.6) documents a security backport and Ruby 3.3 testing. Together these establish sustained compatibility and complexity management. Start with the builder and upgrade guide; transport performance depends on the chosen adapter.

### [HoneyryderChuck/httpx](https://github.com/HoneyryderChuck/httpx)

**Ruby — concurrent HTTP client; official GitHub mirror of the GitLab project.** This is unrelated to Python's HTTPX. Study socket multiplexing, connection coalescing, and extensibility in a Ruby-native client.

- **C1:** Connection matching checks transport options and, for coalesced origins, certificate hostname validity rather than trusting an advertised origin alone. State also guards repeated connection exhaustion such as peers continually issuing GOAWAY without serving a request. [Connection implementation](https://github.com/HoneyryderChuck/httpx/blob/master/lib/httpx/connection.rb).
- **C2, C3:** The library batches concurrent requests onto sockets and negotiates HTTP/2, while features such as authentication and caching are plugins. The connection object separates queued requests, parser initialization, and selector-driven I/O. [Project architecture and plugin overview](https://github.com/HoneyryderChuck/httpx/blob/master/README.md). The repository identifies itself as a mirror and points contributions upstream to GitLab.

## BEAM: processless, pooled, and process-owned connections

### [elixir-mint/mint](https://github.com/elixir-mint/mint)

**Elixir — low-level functional HTTP/1 and HTTP/2 client.** Study an HTTP connection represented as data rather than as an automatically created process.

- **C1:** Each operation returns updated immutable connection state, which the caller must retain. Socket messages must be attributed to the right connection, and response events carry request references so multiplexed results remain distinguishable. Active-once socket delivery makes message handling part of the explicit contract.
- **C2:** `Mint.HTTP` provides one interface over HTTP/1, HTTP/2, negotiation, and proxies. Applications can place one or several connections inside their own process architecture, or drive sockets in passive mode. This separation makes Mint a useful foundation for studying pool implementations such as Finch. Start with the usage, architecture, and mode sections of [the `Mint.HTTP` module](https://github.com/elixir-mint/mint/blob/main/lib/mint/http.ex).

### [sneako/finch](https://github.com/sneako/finch)

**Elixir — HTTP client combining Mint with connection-pool management.** Study how a processless protocol client becomes a supervised, reusable application service.

- **C1:** HTTP/1 pool checkout validates reuse and switches socket mode; checkin restores active mode or removes the connection on failure. Async requests monitor their caller, and cancellation terminates the request process. Pool, receive, and request timeouts are distinct. [HTTP/1 pool implementation](https://github.com/sneako/finch/blob/main/lib/finch/http1/pool.ex).
- **C2, C3:** Pools are organized by origin, with configurable size and count, optional tags for traffic isolation, and lazy creation for new origins. The project explicitly targets efficient pooling and reduced copying, with queue telemetry in the implementation rather than an unsupported throughput claim. [Pool organization and supervision guide](https://github.com/sneako/finch/blob/main/README.md).

### [benoitc/hackney](https://github.com/benoitc/hackney)

**Erlang — HTTP client using connection processes and OTP supervision.** Study a different ownership choice from Mint: a `gen_statem` process owns each TCP/TLS connection and its request/response phases.

- **C1:** The connection process tracks protocol and streaming state and monitors the requesting owner so crashes trigger cleanup. The architecture guide makes state transitions and supervision boundaries explicit. [Design guide](https://github.com/benoitc/hackney/blob/master/guides/design.md).
- **C2, C3:** Pools and per-host admission control are separate components; the design describes atomic ETS counters and backoff instead of routing every admission through one server process. The client offers streaming and asynchronous response messages through the same overall ownership model. [Current client documentation](https://github.com/benoitc/hackney/blob/master/README.md).

**Documentation limitation:** the design guide labels itself 3.x and says SSL connections are never pooled, while the current README documents opt-in `ssl_pooling` keyed by TLS options. Use the design guide for the process model, not as a complete description of current TLS pooling. HTTP/3 is explicitly experimental.

## Swift and Dart

### [swift-server/async-http-client](https://github.com/swift-server/async-http-client)

**Swift — HTTP client built on SwiftNIO.** Study the bridge between event-loop futures, Swift concurrency, and bounded streaming.

- **C1:** The response-delegate contract makes head/body/finish callbacks mutually exclusive through returned futures, but permits terminal error delivery while a future is unresolved. No further delivery follows that terminal error. This is a concrete concurrency invariant that application delegates must respect. [Delegate contract in `HTTPHandler.swift`](https://github.com/swift-server/async-http-client/blob/main/Sources/AsyncHTTPClient/HTTPHandler.swift).
- **C2, C3:** Both async sequences and response delegates allow incremental processing with backpressure; delegates can implement file downloads or other sinks. Client shutdown is explicit and can interrupt in-flight requests. [API, streaming, and lifecycle guide](https://github.com/swift-server/async-http-client/blob/main/README.md) supplies the second entry point.

### [Alamofire/Alamofire](https://github.com/Alamofire/Alamofire)

**Swift — application networking layer over Foundation `URLSession`.** Study a richer client policy layer rather than another independent wire-protocol implementation.

- **C1:** Its root dispatch queue must be serial because it coordinates session/request state. `AuthenticationInterceptor` handles the queueing and threading around credential refresh. The guide also distinguishes cancelling a Swift task from cancelling its underlying HTTP request, with explicit opt-in behavior for particular async request wrappers.
- **C2, C3:** Request adapters/retriers, serializers, trust evaluators, redirect handlers, and event monitors have separate extension contracts. Request construction and response serialization may move to separate queues when profiling identifies bottlenecks. [Advanced usage and request-pipeline guide](https://github.com/Alamofire/Alamofire/blob/master/Documentation/AdvancedUsage.md) is the entry point; focus on dispatch queues, authentication, and Swift-concurrency sections.

### [cfug/dio](https://github.com/cfug/dio)

**Dart — HTTP client for Dart and Flutter; focus on the monorepo's `dio` package.** Study interceptor scheduling and platform adaptation. The repository is counted once, including its adapter packages.

- **C1:** `QueuedInterceptor` uses separate request/response/error queues. Queue advancement must happen exactly once whether a handler completes or cancellation arrives; the implementation also releases captured request state and observes asynchronous callback errors. These mechanisms prevent stalled queues and retained payloads. [Interceptor implementation](https://github.com/cfug/dio/blob/main/dio/lib/src/interceptor.dart).
- **C2, C3:** `HttpClientAdapter` separates the API from native and browser transports, while transformers handle payload conversion independently. The default background transformer can move larger JSON decoding work to an isolate. [Package guide](https://github.com/cfug/dio/blob/main/dio/README.md). Queued interceptors serialize their own phases, not every complete network request globally.

## Scientific-computing ecosystem

### [JuliaWeb/HTTP.jl](https://github.com/JuliaWeb/HTTP.jl)

**Julia — HTTP client/server library; focus on the client, transport, and request context.** Study reusable networking infrastructure in a language often associated with numerical applications. The inspected client guide describes the 2.0 architecture.

- **C1:** External cancellation has protocol-specific consequences: HTTP/1 closes the active connection, while HTTP/2 resets the active stream. Closed client objects reject further use, and request contexts can combine deadlines with cancellation.
- **C2, C3:** `Client` groups a transport, cookie jar, proxy policy, retry bucket, and protocol preferences; `Transport` exposes pool and header-size limits. `HTTP.open` and response streams provide incremental consumption, while shared retry buckets coordinate retries across requests. These are explicit policy/resource objects rather than only convenience request functions. Start with the reusable-client, cancellation, and streaming sections of [the client guide](https://github.com/JuliaWeb/HTTP.jl/blob/master/docs/src/guides/client.md). Older 1.x examples should not be assumed to describe this implementation.

## Coverage, search process, and limits

Discovery used **16 distinct live search formulations**, followed by direct GitHub API reads and official documentation inspection. Search angles included connection-pool architecture; Python/Rust async multiplexing; BEAM process ownership; Ruby adapters and HTTP/2; Swift backpressure; Scala effects and .NET clients; C/C++ transport design; Go retry/context handling; Node dispatchers; PHP middleware; Haskell/OCaml clients; Dart queued interceptors; embedded caller-owned buffers; Nim/Zig clients; and a final cross-language search for smaller clients and wrapper implementations. Later broad searches mostly revisited covered architectures or returned narrower wrappers, SDK generators, examples, and early exploratory projects. The two late additions, coreHTTP and Dio, filled concrete embedded and Dart gaps.

The final selection deliberately includes both protocol engines and substantial policy layers. Hyper/reqwest and Mint/Finch are separate implementations at different layers, not duplicate forks; their relationship is stated so readers can follow the boundary. Faraday, sttp, Axios, and RestSharp qualify through substantive abstraction and lifecycle work even though they delegate transport. Conversely, generated service SDKs, awesome-lists, benchmarks presented as libraries, and server-only search results were excluded. Large language/runtime monorepos containing standard HTTP clients were outside the chosen standalone-library emphasis. Other viable projects, including OCaml Cohttp and Java AsyncHttpClient, surfaced during discovery but are not evaluated here; omission is not a negative quality judgment.

All retained repositories have an inspected substantive primary source beyond repository identity verification. C4 is assigned conservatively where dated evolution and compatibility/testing evidence were actually inspected, rather than inferred from repository age or recent pushes. Performance discussion describes mechanisms, not comparative speed claims. This was read-only research: no candidate code was executed, no dependencies were installed, and no benchmark or security audit was performed. Moving branch documentation, the Guzzle stable-guide/development-branch distinction, HTTP.jl's major-version boundary, and Hackney's documented inconsistency limit version-specific conclusions.
