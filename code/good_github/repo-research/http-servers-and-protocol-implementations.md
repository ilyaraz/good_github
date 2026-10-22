# HTTP servers and protocol implementations

Research date: **2026-10-09**.

This selection covers **27 GitHub repositories** implementing HTTP servers, embeddable server engines, HTTP/1 parsing and framing, HTTP/2, and HTTP/3. The emphasis is on code an experienced engineer can study for protocol correctness, resource ownership, concurrency, extensibility, and performance tradeoffs. Application frameworks, client-only convenience libraries, and general networking libraries without a directly examined HTTP implementation are outside the selection. Large repositories are included only for named HTTP subsystems.

The criterion judgments below are grounded engineering assessments of the cited material, not certifications that every component is exemplary or suitable for a particular deployment. Repository pages and additional primary implementation or architecture material were opened for every entry. Links to moving branches and versioned documentation are reading entry points, not a reproducible commit snapshot.

## Criteria legend

- **C1 — Correctness:** difficult invariants, concurrency, adversarial input, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or components supporting different applications.
- **C3 — Performance:** concrete resource or throughput/latency constraints addressed through an understandable architecture.
- **C4 — Evolution:** years of substantive development accompanied by compatibility work, testing, or management of complexity. Age and popularity alone do not qualify.

## General-purpose HTTP servers

### [nginx/nginx](https://github.com/nginx/nginx)

**Language/role:** C; HTTP server, reverse proxy, and cache. This is the official NGINX Open Source repository.

Study request lifetime management across redirects, subrequests, and output filters. **C1:** redirects must clear module contexts that could become inconsistent with the new location; reference counts and finalization must remain balanced. Subrequest output is ordered even when requests progress independently. **C2:** request phases, module configuration, variables, and filter chains provide a reusable extension architecture. The [development guide](https://nginx.org/en/docs/dev/development_guide.html) explains these mechanisms and maps them to the source tree.

**C4:** the [dated changelog](https://nginx.org/en/CHANGES) records evolution across years, including internal API fixes, directive deprecations, module binary-compatibility repairs, and graceful-shutdown defects. It is particularly useful alongside the guide to see where the abstractions have needed repair.

### [apache/httpd](https://github.com/apache/httpd)

**Language/role:** C; Apache HTTP Server. **Official substantive GitHub mirror**, rather than the project's sole development infrastructure.

Start with the event multi-processing module to study the interaction between processes, worker threads, listener threads, and connection filters. **C1:** graceful restarts must distinguish old processes finishing requests from new processes accepting work; scoreboard exhaustion can occur even below the active-request limit. Lingering close also has to let clients receive an error while still transmitting. **C3:** idle keep-alive sockets and some blocked writes move away from request workers, while filters that require whole response bodies constrain this optimization. The [event MPM architecture and limitations](https://httpd.apache.org/docs/2.4/mod/event.html) explain the handoffs, synchronization assumptions, and versioned changes unusually concretely.

### [caddyserver/caddy](https://github.com/caddyserver/caddy)

**Language/role:** Go; extensible HTTP server with automatic HTTPS.

Study how a server replaces a live configuration while requests and shared services continue running. **C1:** Caddy provisions and validates the new configuration before retiring the old one; configurations briefly coexist, and cleanup follows explicit module lifecycles. **C2:** the core handles configuration while host and guest modules implement applications, HTTP handlers, and other extensions through named interfaces. **C3:** immutable configuration units avoid synchronizing every hot-path configuration read; provisioning moves work such as CIDR parsing out of individual requests. These claims and the necessary treatment of shared upstream state are explained in the [architecture guide](https://caddyserver.com/docs/architecture).

### [h2o/h2o](https://github.com/h2o/h2o)

**Language/role:** C; HTTP/1 and HTTP/2 server and embeddable library. The inspected repository README labels its HTTP/3 support experimental.

Study the relationship between HTTP/2 scheduling and the TCP/TLS data already committed to transmission. **C3:** H2O's latency optimization uses observed RTT and congestion-window information to decide when to limit unsent data and TLS record sizes, balancing prompt reprioritization against extra kernel interaction. **C1:** its configuration separates advertised stream limits, concurrently processed requests, streaming requests, input windows, and idle timeouts—distinct boundaries needed to keep multiplexed peers from monopolizing resources. The [HTTP/2 implementation and directive guide](https://h2o.examp1e.net/configure/http2_directives.html) provides both rationale and controls. Treat its server-push discussion as version-specific historical context, not a statement about present browser support.

## Servers organized around language runtimes

### [jetty/jetty.project](https://github.com/jetty/jetty.project)

**Language/role:** Java; Eclipse Jetty server, connectors, and HTTP protocol implementations.

Study scheduling when a task may either complete immediately or block. **C1:** HTTP/2 progress can require writes to enable reads and reads to enable writes; rejecting internal tasks can stop a server, so limiting requests is not equivalent to bounding the executor queue. **C3:** Jetty's adaptive execution strategy chooses among production/consumption handoffs using task blocking information and immediately available threads, considering CPU-cache locality as well as progress. The [threading architecture guide](https://jetty.org/docs/jetty/12/programming-guide/arch/threads.html) also explains leased and reserved threads, pool shrinking, and the difference between application concurrency and internal execution capacity.

### [undertow-io/undertow](https://github.com/undertow-io/undertow)

**Language/role:** Java; embeddable HTTP server, with optional Servlet integration.

Study a server assembled from workers, listeners, and a handler chain instead of a mandatory global container. **C2:** listeners translate wire protocols into `HttpServerExchange`; handlers can compose or choose the next handler, and embedding applications can share workers and buffer pools across listeners. **C3:** XNIO I/O threads run nonblocking work, while blocking tasks are dispatched to a separate worker pool. Channel callbacks retain an assigned I/O-thread affinity. The [Undertow architecture and handler guide](https://undertow.io/undertow-docs/undertow-docs-2.1.0/index.html) exposes these boundaries. This is versioned 2.1 documentation; its dependency and Servlet-version details should not be mistaken for current release requirements.

### [dotnet/aspnetcore](https://github.com/dotnet/aspnetcore)

**Language/role:** C#; monorepo entry restricted to **Kestrel**, especially its HTTP/2 connection engine.

Study how a multiplexed connection owns stream lifetimes while dispatching application work independently. **C1:** connection processing tracks header parsing, flow control, settings, and client misbehavior; the implementation includes a time-windowed limit for repeated excessive-load responses. **C3:** completed streams are pooled only after graceful completion, with bounded pool size and expiration, while the connection object itself is not reused. The comments and implementation in [Http2Connection.cs](https://github.com/dotnet/aspnetcore/blob/main/src/Servers/Kestrel/Core/src/Internal/Http2/Http2Connection.cs) make the correctness/performance boundary visible; its [raw source](https://raw.githubusercontent.com/dotnet/aspnetcore/refs/heads/main/src/Servers/Kestrel/Core/src/Internal/Http2/Http2Connection.cs) is a convenient reading alternative.

### [ninenines/cowboy](https://github.com/ninenines/cowboy)

**Language/role:** Erlang; HTTP server built on Ranch connection management.

Study the mapping from HTTP connections and streams to lightweight processes. **C1:** HTTP/2 requests execute independently while frames share a connection; Cowboy separates the connection process from request processes and retains control over protocol-specific framing headers. **C2:** stream handlers receive request, response, body, message, and early-error events, while middleware handles routing and application dispatch. The [Cowboy 2.6 flow and process-model guide](https://ninenines.eu/docs/en/cowboy/2.6/guide/flow_diagram/) explains why request processes are not reused and why low-level stream handlers must avoid blocking the connection. This is an explicitly versioned architectural reading, not evidence for the latest protocol feature set.

### [mtrudel/bandit](https://github.com/mtrudel/bandit)

**Language/role:** Elixir; independently implemented HTTP/1 and HTTP/2 server for Plug applications.

Study a deliberately explicit HTTP/2 process model. **C1:** the connection process owns linked stream processes and handles their exits; a stream failure need not terminate its connection, while connection termination removes its streams. Incremental frame parsing and orderly error handling are separated from application execution. **C2:** `Bandit.Adapter` handles application-facing HTTP semantics, while stream and connection modules own transport-specific behavior. The [HTTP/2 implementation document](https://github.com/mtrudel/bandit/blob/main/lib/bandit/http2/README.md) also identifies protocol tests, Plug integration tests, frame tests, and strict h2spec execution. It candidly describes scheduling and flow-control limitations, making it a useful companion to Cowboy rather than a duplicate wrapper.

### [http-kit/http-kit](https://github.com/http-kit/http-kit)

**Language/role:** Java and Clojure; event-driven HTTP server/client with a Ring-facing server API.

Study a compact Java NIO engine underneath a functional application interface. **C1:** worker-to-I/O-thread operations travel through a concurrent queue; lifecycle state distinguishes running from draining, and setup failures close partially created selector/channel resources. **C3:** a selector loop and shared direct input buffer make socket ownership and buffer reuse explicit rather than assigning an I/O thread to every connection. These mechanisms are visible in [HttpServer.java](https://raw.githubusercontent.com/http-kit/http-kit/master/src/java/org/httpkit/server/HttpServer.java). **C2:** the repository's Ring integration supports reuse of existing Clojure handlers and middleware, alongside asynchronous streaming. The repository recommends a reverse proxy for production deployments.

### [yesodweb/wai](https://github.com/yesodweb/wai)

**Language/role:** Haskell; monorepo entry focused on the **Warp HTTP server** and its WAI boundary.

Study how functional application interfaces meet socket lifetimes and graceful shutdown. **C2:** WAI provides a common application/middleware interface that decouples web frameworks from server backends. **C1:** Warp's connection machinery tracks applications still using a socket and coordinates shutdown with receive operations using STM state; HTTP/1 and HTTP/2 have distinct graceful-close handling. **C3:** connection construction uses receive buffer pools, a reusable write buffer, and a sendfile path. Start at [Warp's Run.hs](https://github.com/yesodweb/wai/blob/master/warp/Network/Wai/Handler/Warp/Run.hs), or its [raw implementation](https://raw.githubusercontent.com/yesodweb/wai/master/warp/Network/Wai/Handler/Warp/Run.hs). Only this server/interface subsystem is being assessed, not every package in the repository.

### [benoitc/gunicorn](https://github.com/benoitc/gunicorn)

**Language/role:** Python; UNIX application HTTP server with an arbiter and configurable worker models.

Study process supervision and application isolation rather than only byte parsing. **C1:** an arbiter reacts to child exits, worker-count signals, and configuration reloads while workers own request handling; failure recovery is therefore separated from individual clients. **C2:** synchronous, threaded, and asynchronous workers allow the same hosting infrastructure to serve applications with different concurrency needs. **C3:** the worker choice changes memory sharing, keep-alive behavior, and vulnerability to long blocking operations. The [design guide](https://gunicorn.org/design/) explains these tradeoffs. In particular, the synchronous worker closes connections after responses; statements about keep-alive must be tied to a worker type.

### [pgjones/hypercorn](https://github.com/pgjones/hypercorn)

**Language/role:** Python; ASGI/WSGI server using h11, h2, and other protocol libraries, with asyncio, uvloop, or Trio workers.

Study the substantial orchestration layer between reusable protocol engines and application/runtime APIs. **C2:** the server supports different event-loop models and application interfaces while reusing protocol implementations. **C1:** slow-client backpressure must propagate through an awaited ASGI send without blocking the event loop, and must stop waiting when the connection closes. **C3:** this avoids requiring an application to keep producing output while the peer cannot consume it. The [backpressure discussion](https://hypercorn.readthedocs.io/en/latest/discussion/backpressure.html) gives the contract; the [design choices](https://hypercorn.readthedocs.io/en/latest/discussion/design_choices.html) describe the callback-versus-streaming I/O decision. Its value here is server coordination, distinct from h11/h2's protocol state machines.

## Embedded servers and application-facing libraries

### [civetweb/civetweb](https://github.com/civetweb/civetweb)

**Language/role:** C with a C++ interface; embeddable and standalone web server. A substantive independent descendant of Mongoose: the repository documents separate development since the 2013 fork.

Study a bounded, blocking-I/O server whose threading model remains easy to trace. **C1:** accepted sockets pass through a synchronized queue; a full queue blocks further enqueueing, and initialization has an explicit completion guarantee. **C2:** an application-owned server context, callbacks, and per-URI handlers support embedding without adopting a larger application framework. The [embedding and internals guide](https://github.com/civetweb/civetweb/blob/master/docs/Embedding.md) explains worker creation, queue ownership, socket timeouts, and stack-memory costs.

**C4:** the [release notes](https://github.com/civetweb/civetweb/blob/master/RELEASE_NOTES.md) document substantial post-fork API rewrites, CI/test integration, TLS-library compatibility updates, and HTTP/2 fixes. This separate evolution justifies retaining both CivetWeb and Mongoose.

### [cesanta/mongoose](https://github.com/cesanta/mongoose)

**Language/role:** C; embedded HTTP server within a network library for desktop, RTOS, and bare-metal environments.

Study a poll-driven connection manager with explicit application and protocol callbacks. **C1:** the API assumes access from the same thread/task; send and receive buffers have explicit ownership and draining behavior, and protocol handlers run before application handlers. These rules expose the concurrency and partial-I/O obligations an embedder must respect. **C2:** the same connection/event interface supports HTTP and other protocols across differing platform stacks. **C3:** multiplexing connections through `mg_mgr_poll` is an understandable architecture for environments where a thread per connection is undesirable. The [architecture, event, and buffer documentation](https://mongoose.ws/documentation/) is the primary entry point. The examined scope is the HTTP/event subsystem, not every bundled network protocol.

### [boostorg/beast](https://github.com/boostorg/beast)

**Language/role:** C++; reusable HTTP/1 and WebSocket components on Boost.Asio.

Study how parsing algorithms can remain independent of application buffer and threading policy. **C2:** role-symmetric message and stream operations support building both clients and servers, while deliberately staying below a complete web framework; the [design choices](https://www.boost.org/doc/libs/latest/libs/beast/doc/html/beast/design_choices.html) explain this boundary. **C1:** the [basic_parser interface and implementation comments](https://raw.githubusercontent.com/boostorg/beast/develop/include/boost/beast/http/basic_parser.hpp) specify incremental consumption, recoverable `need_more`, terminal errors, EOF-delimited bodies, and separate header/body limits. **C3:** the same interface documents a no-additional-allocation case for a single input buffer and an eager-parse option, making performance choices visible alongside validity rules.

### [golang/go](https://github.com/golang/go)

**Language/role:** Go; **official GitHub mirror**, with this entry restricted to the standard library's **net/http server**.

Study a small application-facing interface backed by detailed connection lifecycle machinery. **C2:** `Handler`, `ResponseWriter`, and `Request` let server behavior compose while hiding connection management. **C1:** `server.go` defines when a handler may use its response writer/body, how a panic affects HTTP/1 versus HTTP/2, and how graceful shutdown closes listeners and idle connections while waiting for active work. Hijacked connections require separate treatment, and a shut-down server cannot be reused. The [annotated server source](https://go.dev/src/net/http/server.go) includes both the public contracts and their implementation, including shutdown locking, state tracking, and polling tradeoffs.

### [hyperium/hyper](https://github.com/hyperium/hyper)

**Language/role:** Rust; low-level asynchronous HTTP/1 and HTTP/2 library with server and client APIs.

Study an HTTP implementation designed as infrastructure for higher-level libraries. **C2:** the `Body` trait admits different body producers and consumers, while `Incoming` represents a received stream; clients and servers share this vocabulary. **C3:** bodies advance when polled, so processing frames before requesting more preserves backpressure and avoids mandatory whole-message buffering. The [body module documentation](https://docs.rs/hyper/latest/hyper/body/index.html) shows data/trailer frames and the distinction between streaming and collecting. Its warning that collection requires size limits for untrusted inputs makes an important boundary explicit: the reusable abstraction does not eliminate the application's resource policy.

### [valyala/fasthttp](https://github.com/valyala/fasthttp)

**Language/role:** Go; alternative HTTP server/client implementation emphasizing object reuse.

Study the costs that an allocation-conscious API transfers to its callers. **C3:** request and response acquisition/release pools reduce garbage-collection pressure, while body access can expose reusable storage. **C1:** request objects must not be copied or used concurrently; references to context members and body slices generally cannot survive handler return or release. The [API reference](https://pkg.go.dev/github.com/valyala/fasthttp) documents these ownership restrictions, the special timeout-error path, and incremental body streams. The repository explicitly says its API is not identical to `net/http` and recommends the standard package for many workloads. This is a useful comparative design study, not an unconditional performance recommendation.

### [inhabitedtype/httpaf](https://github.com/inhabitedtype/httpaf)

**Language/role:** OCaml; HTTP/1.1 parsing, serialization, and pipelined server connections, independent of I/O.

Study a protocol engine built using Angstrom and Faraday with an explicit driver interface. **C2:** the same core can be connected to different runtimes because it requests operations instead of owning sockets. **C1:** the driver must distinguish read, yield, EOF, partial successful writes, and closed output; exceptions move a connection through an error-handling path. **C3:** the interface exposes bigstring ranges and vectors of output buffers, avoiding a requirement to flatten every response. The [public interface, especially Server_connection](https://raw.githubusercontent.com/inhabitedtype/httpaf/master/lib/httpaf.mli), documents these sequencing and ownership obligations. No claim about present maintenance cadence is needed for its value as an architectural study.

## Protocol engines and parsers

### [python-hyper/h11](https://github.com/python-hyper/h11)

**Language/role:** Python; HTTP/1.1 protocol engine with no network I/O.

Study the correctness hidden behind HTTP/1 connection reuse and protocol switching. **C1:** its state module models client, server, keep-alive, CONNECT-switch, and Upgrade-switch state; event-triggered transitions interact with transitions triggered by joint states, including an explicit precedence rule for a conflict. **C2:** symmetric protocol events let applications use the same engine in either role with synchronous or asynchronous I/O. The commentary in the [core state-machine implementation](https://raw.githubusercontent.com/python-hyper/h11/master/h11/_state.py) explains the invariants and deliberately centralizes transition logic. It is particularly approachable for examining state-machine design without first understanding an event loop or a large server configuration system.

### [python-hyper/h2](https://github.com/python-hyper/h2)

**Language/role:** Python; in-memory HTTP/2 protocol stack.

Study the decomposition of connection-wide rules from per-stream rules. **C1:** frames drive interacting state machines; connection role constrains legal operations, and stream transitions govern errors and the header-validation context for requests, responses, and trailers. **C2:** the engine exposes byte input/output and events without choosing sockets or a concurrency framework. **C3:** stream instances share transition tables rather than duplicating them. The [low-level implementation guide](https://python-hyper.org/projects/hyper-h2/en/stable/low-level.html) also identifies imperfectly incorporated state variables and priority-frame exceptions. That candid discussion makes the project useful for learning where a theoretically neat protocol model becomes more complicated in code.

### [nghttp2/nghttp2](https://github.com/nghttp2/nghttp2)

**Language/role:** C library with accompanying client, server, proxy, and load-testing tools; HTTP/2 and HPACK.

Study a protocol library that can be embedded into an existing event loop without replacing it. **C2:** opaque session objects and configurable callbacks separate protocol processing from I/O and permit internal evolution without exposing representation details. **C1:** a session must not be used concurrently; send/receive calls must not reenter from callbacks; shutdown must account for output already handed to the application but not yet transmitted. The [programmer's guide](https://nghttp2.org/documentation/programmers-guide.html) lays out these constraints and compares callback-based versus memory-buffer APIs. Its HTTP/2 library does not implement HTTP/1; applications that need both must deliberately compose them.

### [ngtcp2/nghttp3](https://github.com/ngtcp2/nghttp3)

**Language/role:** C; HTTP/3 and QPACK library independent of a particular QUIC implementation.

Study the boundary between HTTP framing and QUIC's transport bookkeeping. **C1:** applications must retain outbound payload until acknowledgement permits release. Incoming protocol bytes, application-consumed payload, and data deferred by cross-stream synchronization affect flow-control credit differently. **C2:** callbacks and explicit binding of control/QPACK streams allow the HTTP/3 layer to operate over different QUIC stacks rather than bundling one transport policy. The [programmer's guide](https://nghttp2.org/nghttp3/programmers-guide.html) explains these contracts, reset/stop-sending requests, and resource cleanup. The repository states that server push is unsupported; completeness should be assessed against the required feature subset.

### [cloudflare/quiche](https://github.com/cloudflare/quiche)

**Language/role:** Rust with a C-facing integration surface; QUIC and HTTP/3. This entry focuses on the **h3/QPACK subsystem and its transport boundary**.

Study the separation of packet-driven transport progress from HTTP request/response events. **C2:** the application supplies sockets and timers, while HTTP/3 connections expose stream events, headers, and body operations on top of QUIC. **C1:** request completion follows stream closure across potentially multiple frames; the HTTP/3 engine validates peer messages and reports protocol errors while initiating the appropriate connection close, leaving application cleanup explicit. The [h3 module guide](https://docs.quic.tech/quiche/h3/index.html) walks through setup, polling, completion, and errors. The repository cautions that its command-line example applications are not production servers, a distinction separate from the library's design value.

### [nodejs/llhttp](https://github.com/nodejs/llhttp)

**Language/role:** TypeScript parser specification generating C, with C integration helpers; HTTP/1 parser.

Study how generation can make a highly optimized parser more reviewable. **C3:** the project explicitly represents a parser graph and generates matching optimizations instead of requiring every protocol change to preserve hand-unrolled C. **C1:** graph/span checks complement protocol-specific rejection paths; the [parser specification](https://raw.githubusercontent.com/nodejs/llhttp/main/src/llhttp/http.ts) includes duplicate Content-Length detection, numeric overflow handling, and strict Transfer-Encoding/Content-Length conflict checks with explicit leniency controls. The repository explains the generator architecture and its limited verification claims. This is retained for its substantive parser specification, not as a generated wrapper, and graph checking should not be mistaken for a proof of complete HTTP correctness.

### [h2o/picohttpparser](https://github.com/h2o/picohttpparser)

**Language/role:** C; HTTP/1 request/response/header parser and chunked decoder.

Study a small parser where memory and input-progress decisions remain visible. **C3:** request/header parsing returns slices into caller-owned input instead of allocating strings; the implementation includes an SSE4.2 scanning path. **C1:** incomplete input is distinguished from invalid input, bounds checks guard parsing, and the previous-input-length completion check limits repeated scanning as data arrives slowly. These mechanisms are visible in [picohttpparser.c](https://raw.githubusercontent.com/h2o/picohttpparser/master/picohttpparser.c), with integration examples on the repository page. The header parser is stateless, while the incremental chunked decoder has state. Retaining it separately from H2O exposes a reusable parsing component; it is not a full HTTP semantics or connection-management engine.

## Coverage, search process, and limitations

Discovery used more than six distinct formulations, including event-driven C servers; Java handler/thread architectures; embedded C/C++ servers; HTTP/2 and HTTP/3/QPACK implementations; Rust/Python state machines; Go allocation-oriented servers; Erlang/Elixir process models; Haskell/OCaml runtime-independent interfaces; Clojure event loops; and incremental parsers/fuzzing. Representative searches included `HTTP server implementation architecture event loop GitHub nginx h2o caddy`, `embedded HTTP server C C++ CivetWeb Mongoose Boost Beast architecture GitHub`, `HTTP3 HTTP2 implementation QUIC QPACK nghttp3 quiche nghttp2 GitHub`, and `HTTP server Erlang Cowboy Haskell Warp OCaml httpaf GitHub`. Later searches surfaced Bandit and http-kit; subsequent parser and server-comparison searches mainly repeated already represented architectures or led to adjacent testing tools.

All 27 repository URLs were opened, and every retained project has an additional opened primary source beyond its top-level README. Architectural claims come from project documentation or source, not stars or search snippets. The selection deliberately spans complete servers and reusable engines; their responsibilities differ, so performance rankings would be misleading. No candidate code was executed, dependencies installed, or benchmarks reproduced.

NGINX and Apache represent configurable standalone servers; Jetty, Undertow, Kestrel, and the language-runtime servers provide contrasting scheduling models; embedded libraries expose constrained-resource decisions; protocol engines cover HTTP/1 through HTTP/3. Apache HTTP Server and Go are explicitly identified as official mirrors. CivetWeb is included alongside Mongoose because its separate evolution is documented. H2O/picohttpparser and Hypercorn/h11/h2 illustrate composition across separate substantive repositories, rather than counting identical code under different names. Monorepos are counted once.

Excluded were educational tiny-nginx derivatives, unverified mirrors, generated bindings without substantive implementation, client-only convenience packages, and higher-level routing frameworks whose wire engine is already represented. Proxy/cache-focused systems and generic networking frameworks were not exhaustively surveyed. Ruby, Swift, and smaller operating-system-specific servers are coverage gaps; omission is not a negative quality judgment. A discovered differential-testing project was useful as a coverage cross-check but was not counted as an HTTP implementation.

Some documentation is explicitly versioned or contains historical material, as identified in the entries. The report makes no blanket claim of active maintenance, release readiness, security, or uniform protocol completeness. C4 is assigned only where the inspected history supports evolution and concrete maintenance work; other entries qualify through implementation evidence. The final list contains 27 distinct repository URLs, each with at least two justified criteria.
