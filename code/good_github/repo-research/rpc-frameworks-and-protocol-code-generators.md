# RPC frameworks and protocol code generators

Research date: **2026-10-09**.

This selection covers 27 GitHub repositories implementing RPC runtimes, service-interface compilers, or reusable generators for network message protocols. It spans cross-language IDLs, capability RPC, HTTP and JSON-RPC, language-native interfaces, embedded systems, and specialized datacenter/HPC transports. Serialization projects are included when schema compilation and generated protocol code are central; general web frameworks, generated SDK collections, and application-specific RPC clients are outside the scope. Each repository is counted once, including monorepos.

The criteria below are judgments grounded in the cited implementation and documentation, not certifications that every component is exemplary or recommendations to deploy a particular version.

- **C1 — Correctness:** substantial invariants, concurrency, numerical/wire semantics, adversarial-input handling, or distributed failure modes.
- **C2 — Abstractions:** substantial reusable interfaces or compiler/runtime structures serving multiple use cases.
- **C3 — Performance and structure:** concrete latency, throughput, allocation, memory, or concurrency constraints addressed through an explainable architecture.
- **C4 — Evolution:** evidence across years of compatibility work, testing, migration, or deliberate complexity management; repository age alone does not qualify.

## Cross-language RPC and distributed objects

### 1. [grpc/grpc](https://github.com/grpc/grpc)

**Language/role:** C/C++ core, language bindings, and service-code-generation plugins. Study the boundary between generated service APIs, the generic call model, and HTTP/2 transport machinery in this monorepo.

- **C1:** An RPC has independent directional message streams, ordered message delivery, and a terminal status distinct from payload data. Mapping length-prefixed messages onto fragmented HTTP/2 frames and carrying status in trailers creates concrete framing and completion invariants.
- **C2:** The same service definition yields client and server interfaces, with synchronous, asynchronous, and streaming APIs across supported languages.
- **C3:** HTTP/2 flow control explicitly limits memory committed to in-flight messages. The [concepts and protocol architecture](https://github.com/grpc/grpc/blob/master/CONCEPTS.md) is the useful starting point for all three criteria.

### 2. [apache/thrift](https://github.com/apache/thrift)

**Language/role:** C++ IDL compiler with numerous language runtimes. The relevant subsystems are the compiler, transport/protocol libraries, generated processors, and cross-language tests.

- **C1:** The [RPC specification](https://github.com/apache/thrift/blob/master/doc/specs/thrift-rpc.md) distinguishes declared exceptions, application exceptions, one-way calls, response sequence IDs, and framed versus unframed transport. Its discussion of differences between older synchronous and asynchronous Java implementations is particularly useful for studying interoperability pitfalls.
- **C2:** Generated clients and processors operate over separate transport and serialization abstractions, allowing applications to change those layers without redesigning their service definitions. The repository also documents mixed-version deployment and client/server tests across languages.

The specification explicitly draws on older Java versions; treat its implementation-specific observations as historical context, not a complete description of every current binding.

### 3. [capnproto/capnproto](https://github.com/capnproto/capnproto)

**Language/role:** C++ serialization compiler/runtime and capability-based RPC, including its asynchronous support library. Study distributed object references and promise pipelining together.

- **C1:** Connection loss invalidates capabilities; dropping the last reference closes the remote object. Capability identifiers are scoped to connections, linking reference management to authority and resource lifetime.
- **C2:** Interfaces are first-class values that can be passed as arguments or embedded in structures, supporting dynamically created remote objects rather than only startup-registered services.
- **C3:** Promise pipelining sends dependent operations before earlier results arrive, reducing sequential network round trips while preserving composable interfaces. These mechanisms are explained in the [RPC design](https://capnproto.org/rpc.html).

The repository’s default `v2` development branch warns about breaking changes and directs stability-oriented users to `master`; account for that distinction when reading code.

### 4. [zeroc-ice/ice](https://github.com/zeroc-ice/ice)

**Language/role:** C++ and multiple language runtimes, with Slice IDL compilers. Focus on generated proxies, dispatch, connection management, and invocation semantics within the larger Ice suite.

- **C1:** The [automatic-retry design](https://docs.zeroc.com/ice/3.8/runtime/invocation/automatic-retries) explains when a partially transmitted operation can safely be retried, why marshal failures are excluded, and how an `idempotent` declaration permits more aggressive retry behavior. It explicitly separates transport failure from a successful invocation returning a user exception.
- **C2:** Slice-generated proxies and server stubs isolate application contracts from language and connection details. Retry policy is integrated into the communicator/proxy model rather than scattered through generated business methods.

This is a useful codebase for examining why a timeout or lost reply cannot generally reveal whether a remote mutation happened.

## Protocol compilers and generated message runtimes

### 5. [protocolbuffers/protobuf](https://github.com/protocolbuffers/protobuf)

**Language/role:** C++ `protoc` compiler and multilingual message runtimes. It belongs here as protocol-code-generation infrastructure, not as a complete RPC transport.

- **C1:** The [wire-format guide](https://protobuf.dev/programming-guides/encoding/) exposes exact integer and message semantics: continuation-bit varints, field-number/wire-type tags, signed-number encodings, and length-delimited data. Unknown fields can be skipped because wire types specify how their payloads are represented.
- **C2:** A shared schema language and compiler produce language-specific message APIs backed by runtimes. Engineers can study how a common wire contract is separated from target-language representations and compiler extensions.

The repository cautions that even release branches can be unstable between release commits; use a pinned release when comparing generated code and runtime behavior.

### 6. [google/flatbuffers](https://github.com/google/flatbuffers)

**Language/role:** C++ `flatc` compiler with generated accessors and runtimes for many languages. The relevant subsystem is schema-driven binary protocol generation and buffer access.

- **C1:** Cross-platform layout depends on explicit alignment, little-endian scalars, relative offsets, and vtable lookup. Generated accessors handle absent fields through default values, making schema evolution a layout problem as well as an API problem.
- **C2:** Schema compilation produces reusable typed accessors over a common binary representation.
- **C3:** Data is accessed through offsets rather than first reconstructing an entire object graph; buffers are built backwards to simplify bookkeeping. The [internals guide](https://flatbuffers.dev/internals/) walks through the representation and generated C++ code, making the performance tradeoff inspectable.

### 7. [nanopb/nanopb](https://github.com/nanopb/nanopb)

**Language/role:** C runtime and Python generator for Protocol Buffers on memory-constrained systems.

- **C1:** Stream callbacks must honor complete reads/writes, distinguish valid end-of-message from premature EOF, and obey substream bounds. Decoding fails when bounded strings, byte arrays, or repeated fields exceed generated capacities.
- **C2:** The generator maps the same schema to either callbacks for variable-length data or statically allocated C fields, while lightweight stream interfaces support different I/O backends.
- **C3:** Compile-time bounds and callback-based processing expose memory budgeting directly, avoiding a mandatory dynamically allocated object representation. The [basic-concepts guide](https://jpa.kapsi.fi/nanopb/docs/concepts.html) connects generator options, generated structures, stream contracts, and runtime checks.

This is especially instructive when the engineering constraint is predictable RAM use rather than server throughput.

### 8. [square/wire](https://github.com/square/wire)

**Language/role:** Kotlin/Java compiler infrastructure, Java/Kotlin/Swift generation, message runtimes, and gRPC support.

- **C2:** Schema loading, configurable outputs, custom handlers, and generated runtimes form a reusable compilation pipeline. The [compiler guide](https://square.github.io/wire/wire_compiler/) explains how source schemas differ from imported dependencies.
- **C3:** Schema-level pruning removes unreachable declarations before code generation, addressing mobile code size when ordinary shrinkers cannot eliminate types referenced by encoders and decoders.
- **C4:** The [changelog](https://github.com/square/wire/blob/master/CHANGELOG.md) documents 2019–2026 evolution, including unknown-enum preservation, pruning reachability fixes, explicit incompatible schema-API changes, and later malformed-input/recursion fixes. This is evidence of compatibility and correctness management, not merely longevity.

Study the schema/compiler and runtime subsystems as one project; their coordinated evolution is the main attraction.

### 9. [smithy-lang/smithy](https://github.com/smithy-lang/smithy)

**Language/role:** Java implementation of a protocol-agnostic service IDL, semantic model, and reusable code-generation infrastructure. Focus on model processing and directed code generation; language-specific SDK generators also live in separate repositories.

- **C1:** Generation must respect model dependencies and generation scope. The directed pipeline orders shapes by dependencies, and its documentation distinguishes a single service’s closure from multi-service shape closures, including different treatment of service-defined errors. These are semantic obligations for correct generated APIs.
- **C2:** `SymbolProvider`, `SymbolWriter`, integrations, directives, and writer delegation separate name/type mapping, emitted syntax, and extension behavior. The [generator architecture](https://smithy.io/2.0/guides/building-codegen/implementing-the-generator.html) is a substantive entry point for studying compiler framework design.

The inclusion is for the reusable model/codegen engine, not a claim that this repository contains every Smithy protocol backend.

## Service frameworks and cluster-aware RPC

### 10. [apache/brpc](https://github.com/apache/brpc)

**Language/role:** C++ RPC framework with protocol adapters, channels, controllers, and a user-level threading subsystem.

- **C2:** Server, Channel, and Controller form the main application-facing abstractions; naming services, load balancers, and protocol implementations are extension points. Composite channels support sharded or parallel access.
- **C3:** The [architecture overview](https://brpc.apache.org/docs/overview/) discusses connection reuse, parallel request reading/parsing, and the problem of a large message delaying other descriptors assigned to an I/O thread. Its performance treatment is tied to scheduling and connection structure rather than just benchmark rankings.

Study how one C++ service infrastructure supports different wire protocols and exposes profiling/operational introspection. The relevant code is the RPC runtime and threading machinery; the separately hosted Raft implementation is not counted here.

### 11. [apache/dubbo](https://github.com/apache/dubbo)

**Language/role:** Java RPC and microservice framework. Focus on protocol, cluster invocation, discovery, and extension mechanisms in this monorepo.

- **C1:** [`FailoverClusterInvoker`](https://raw.githubusercontent.com/apache/dubbo/3.3/dubbo-cluster/src/main/java/org/apache/dubbo/rpc/cluster/support/FailoverClusterInvoker.java) refreshes provider candidates before retries, rechecks destruction/availability, tracks attempted providers, and distinguishes business exceptions from retryable invocation failures. It makes changing cluster membership part of the retry algorithm.
- **C2:** The [architecture guide](https://dubbo.apache.org/en/overview/what/overview/) separates service governance from RPC data-plane behavior and describes independent service definitions, invocation models, protocol implementations, discovery, and routing policies.

An experienced reader can trace how a language-level interface call becomes provider selection and a concrete protocol exchange. The implementation link deliberately targets the verified `3.3` branch.

### 12. [twitter/finagle](https://github.com/twitter/finagle)

**Language/role:** Scala/JVM protocol-agnostic RPC framework, usable from Java. Its service/filter composition is a particularly clear abstraction study.

- **C2:** A `Service` maps requests to future responses; a `Filter` transforms requests/responses and composes with another service. `ServiceFactory` adds acquisition semantics needed by connection pools. The [services and filters guide](https://twitter.github.io/finagle/guide/ServicesAndFilters.html) shows how these same abstractions structure both application and framework internals.
- **C4:** The [development changelog](https://raw.githubusercontent.com/twitter/finagle/develop/CHANGELOG.rst) records multiple years of runtime changes, API breaks, integration-test adjustments, deadline fixes, and backup-request load controls.

Maintenance caveat: the inspected changelog’s latest named release is `24.5.0`, followed by unreleased entries. Its README’s monthly-release/active-development language is not independently established as a current cadence here. Retain it for its substantial architecture and documented evolution.

### 13. [line/armeria](https://github.com/line/armeria)

**Language/role:** Java asynchronous service framework with gRPC and Thrift integration. The relevant subsystem is the RPC client/server stack and reusable client decorators.

- **C1:** [`RetryingClient`](https://raw.githubusercontent.com/line/armeria/main/core/src/main/java/com/linecorp/armeria/client/retry/RetryingClient.java) handles aggregated and streaming responses differently, coordinates derived request contexts and logs, and aborts duplicate streams on failure. Retrying a streamed response is visibly more complex than repeating a function call.
- **C2:** Retry rules, content-aware rules, configuration mappings, and decorators isolate policy from the underlying client.
- **C3:** Content inspection is bounded through a maximum content length and a truncating response view, while response duplication preserves a stream for the caller. Study these mechanisms to understand how middleware can examine responses without requiring unbounded aggregation.

The implementation source is cited because the rendered documentation page did not expose readable text during this search.

### 14. [cloudwego/kitex](https://github.com/cloudwego/kitex)

**Language/role:** Go RPC runtime and generators for Thrift/Protobuf services, with pluggable service-governance components.

- **C1:** Its [retry guide](https://www.cloudwego.io/docs/kitex/tutorials/service-governance/retry/) distinguishes connection failures before sending from application-level retries requiring idempotency. Chain-stop, duration limits, and retry circuit-breaking address retry amplification and downstream overload.
- **C2:** Code generation, message protocols, transport protocols, middleware, discovery, and load balancing are independently extensible parts of the framework.
- **C3:** Backup requests and mixed retry policies explicitly trade extra work against latency variability; the guide documents when each finishes and how to limit retries.

Study the interaction between request-level policy and system-wide load. The inspected guide says streaming APIs do not yet support retries; do not generalize unary retry behavior to streaming.

## Specialized datacenter and HPC transports

### 15. [erpc-io/eRPC](https://github.com/erpc-io/eRPC)

**Language/role:** C++ RPC library for datacenter networks, with specialized network backends. This is a systems/research-oriented implementation study.

- **C1:** The [implementation notes](https://github.com/erpc-io/eRPC/blob/master/NOTES.md) specify exactly when handlers relinquish request/response buffer ownership, why event-loop reentry is unsafe while RX-ring memory is exposed, and how outstanding requests relate to session-reset continuations.
- **C3:** Short foreground requests can execute directly over receive-ring storage; retaining buffers for retransmission and separating foreground/background work creates explicit lifetime and latency tradeoffs.

Material limitation: those notes contain unresolved session-reset/machine-failure-detection and allocation TODOs. Their presence is not proof every issue persists, but it prevents treating this source as evidence of comprehensive production failure handling. Hardware requirements also limit transferability of its performance results; no benchmark numbers are adopted here.

### 16. [mercury-hpc/mercury](https://github.com/mercury-hpc/mercury)

**Language/role:** C asynchronous RPC framework for HPC, with network abstraction and bulk-data layers.

- **C1:** Completion and cancellation are asynchronous. A successful submission does not guarantee successful completion, and reference counting prevents RPC handles being freed while still used. Callbacks must examine their final result.
- **C2:** Network abstraction, RPC registration/serialization, and a separate bulk interface let applications reuse the RPC model across native transports and data sizes.
- **C3:** `HG_Progress` advances operations separately from `HG_Trigger` callback execution; handles can be reused without reallocating resources. The [RPC-layer guide](https://mercury-hpc.github.io/user/hg/) explains these mechanisms and their ownership rules.

This smaller community project usefully contrasts explicit progress engines with event-loop and thread-pool RPC designs.

## Go frameworks with compact or HTTP-oriented protocols

### 17. [connectrpc/connect-go](https://github.com/connectrpc/connect-go)

**Language/role:** Go RPC implementation supporting Connect, gRPC, and gRPC-Web, with generated Protobuf service interfaces.

- **C1:** Streaming responses separate HTTP success from RPC success: an HTTP 200 stream must end with a terminal envelope, which can contain an RPC error. The protocol also specifies mappings for non-protocol HTTP failures and distinguishes errors that require application judgment before retrying.
- **C2:** Generated clients/handlers integrate with ordinary HTTP infrastructure while serving multiple RPC protocols and unary/streaming interaction patterns.

The [protocol reference](https://connectrpc.com/docs/protocol/) is the main entry point. Study how interoperable error and streaming semantics are expressed using widely implemented HTTP features rather than exposing HTTP/2 framing directly to applications.

### 18. [twitchtv/twirp](https://github.com/twitchtv/twirp)

**Language/role:** Go RPC framework and Protobuf service generator over standard HTTP.

- **C1:** The [wire specification](https://github.com/twitchtv/twirp/blob/main/PROTOCOL.md) distinguishes routing failures, malformed messages, deadlines, and application errors. Errors are JSON even when the successful payload encoding is binary; a deadline error explicitly does not establish that a mutation failed to complete.
- **C2:** Generated clients and handlers map service definitions onto conventional HTTP paths and support both Protobuf and JSON messages. Standard HTTP implementations supply the transport underneath the generated service layer.

Twirp is useful for studying a deliberately constrained RPC contract and what remains necessary for interoperability even with a comparatively small protocol surface. This entry concerns the original implementation, not independent third-party language ports.

### 19. [storj/drpc](https://github.com/storj/drpc)

**Language/role:** Go transport-agnostic RPC runtime and `protoc-gen-go-drpc` generator.

- **C1:** The [stream implementation](https://raw.githubusercontent.com/storj/drpc/main/drpcstream/stream.go) distinguishes send completion, receive completion, termination, cancellation, and final completion after outstanding operations finish. It requires monotonically increasing stream identifiers and serializes state transitions.
- **C2:** Encoding, transport, streams, server dispatch, and generated service bindings are separate reusable pieces.
- **C3:** Manual flushing permits coalesced writes; maximum buffer retention trades reuse against memory consumption; lazy context signaling avoids unnecessary allocations. These are concrete optimization decisions in the same stream implementation.

Its positioning as a gRPC replacement should not be read as identical wire compatibility. Study its own stream state machine and framing, with HTTP/protocol adapters treated separately.

## Rust RPC implementations

### 20. [grpc/grpc-rust](https://github.com/grpc/grpc-rust)

**Language/role:** Rust gRPC monorepo; this entry focuses on the Tonic runtime, transport, and generated client/server subsystem. The former `hyperium/tonic` URL redirects here and is not counted separately.

- **C1:** Tonic’s channel must obey Tower’s readiness contract: readiness authorizes a request before it must be polled again. This makes backpressure and mutable access part of the API’s correctness story.
- **C2:** Generic gRPC and encoding traits separate protocol logic from the HTTP/2 implementation and code generation.
- **C3:** A background connection task and buffered multi-producer channel support cheap cloned handles for concurrent requests. The [Channel documentation](https://docs.rs/tonic/latest/tonic/transport/struct.Channel.html) explains why this structure is used.

The repository warns that `master` prepares breaking changes and points to `0.14.x` for released Tonic code. The cited API documentation describes the released implementation rather than every developing subsystem.

### 21. [google/tarpc](https://github.com/google/tarpc)

**Language/role:** Rust RPC using service traits and procedural macros instead of a separate IDL. The repository explicitly says it is not an official Google product.

- **C1:** Request lifecycle management includes cascading cancellation; the server’s response guard cancels requests if processing is aborted. The request stream also drives response sending and must keep being polled for progress.
- **C2:** A transport can be any suitable stream/sink, while generated service traits, channels, hooks, and server limits separate application methods from dispatch machinery. See the [server architecture/API](https://docs.rs/tarpc/latest/tarpc/server/index.html).

Study how cancellation and multiplexing become ordinary Rust ownership, future, and stream concerns. Optional serialization also allows the service abstraction to be reused for in-memory transports.

### 22. [paritytech/jsonrpsee](https://github.com/paritytech/jsonrpsee)

**Language/role:** Rust asynchronous JSON-RPC clients, servers, subscriptions, and procedural-macro API generation. It is the documented successor to Parity’s earlier JSONRPC crate, not an additional copy of that repository.

- **C1:** RPC middleware uses shared `&self` access, so mutable middleware state needs explicit safe interior mutability. The documented server composition also coordinates WebSocket upgrades with graceful shutdown and connection limits.
- **C2:** HTTP middleware and RPC middleware have separate contracts; per-call, notification, and batch handling can be composed without conflating them with transport-level behavior. The [server builder implementation guide](https://docs.rs/jsonrpsee-server/latest/jsonrpsee_server/struct.ServerBuilder.html) includes a substantial worked integration.

This is a useful contrast to binary IDL systems: the difficulty lies in asynchronous endpoint execution and subscription/transport integration rather than a bespoke binary encoding.

## Language-native, realtime, and broker-backed RPC

### 23. [trpc/trpc](https://github.com/trpc/trpc)

**Language/role:** TypeScript RPC framework using shared inferred types, without a separate schema compiler. It qualifies as an RPC framework, not as a code generator.

- **C1:** Batched calls preserve individual results and failures; mixed statuses require a distinct HTTP response treatment. Runtime input parsing and wire error mapping remain necessary even though clients share compile-time types.
- **C2:** Routers, procedures, adapters, and client links let the same service definitions work across supported host frameworks and transport patterns.
- **C3:** A data-loader mechanism combines parallel calls using the same HTTP method into one request. The [HTTP RPC specification](https://trpc.io/docs/rpc) explains batching, method mapping, subscriptions, and error responses.

Study where TypeScript inference ends and runtime protocol obligations begin. This project is distinct from Tencent’s similarly named tRPC family.

### 24. [Cysharp/MagicOnion](https://github.com/Cysharp/MagicOnion)

**Language/role:** C# RPC and realtime framework over gRPC, using C# interfaces as service contracts; supports .NET and Unity clients.

- **C1:** Each StreamingHub connection owns a hub instance with sequential method execution. Cross-client calls can still run concurrently; waiting on another method from the same connection can deadlock. Disconnecting destroys the instance, and application state restoration is separate from reconnection.
- **C2:** Unary services, typed receiver interfaces, and groups supply reusable request/response and server-to-client communication abstractions.

The [StreamingHub fundamentals](https://cysharp.github.io/MagicOnion/streaminghub/fundamentals) makes ordering, state ownership, and connection lifetime explicit. It is a strong study target for game/chat-style RPC where long-lived stateful sessions matter as much as ordinary method invocation.

### 25. [microsoft/vs-streamjsonrpc](https://github.com/microsoft/vs-streamjsonrpc)

**Language/role:** C#/.NET JSON-RPC over streams, WebSockets, and pipelines, including client proxy generation.

- **C1:** The [resiliency guide](https://microsoft.github.io/vs-streamjsonrpc/docs/resiliency.html) distinguishes invocation order, concurrent execution, and interleaving after `await`. It explains how serializing calls with a semaphore can deadlock when a peer calls back, and how disconnection relates to cancellation of local work.
- **C2:** Transport-independent dispatch, configurable synchronization contexts, target objects, and generated proxies make the engine reusable for IDE/process communication and other bidirectional RPC scenarios.

The guide records a default ordering change in version 2.6. This is a valuable compatibility detail, but by itself is not used to claim C4. Study the dispatch mechanism rather than assuming JSON-RPC guarantees sequential execution.

### 26. [nameko/nameko](https://github.com/nameko/nameko)

**Language/role:** Python microservice framework; the relevant subsystem is AMQP-backed RPC, service entrypoints, and dependency/proxy extensions.

- **C1:** Requests are acknowledged after processing. If the connection closes without acknowledgement, the broker can allocate the message again. This exposes a failure window that application designers must reason about; a single consumer assignment is not an exactly-once side-effect guarantee.
- **C2:** Decorated service methods, service-to-service proxies, and standalone cluster proxies reuse the same RPC abstraction inside and outside the service container. The [built-in extensions guide](https://nameko.readthedocs.io/en/stable/built_in_extensions.html) documents both synchronous and asynchronous invocation.

The redelivery implication above is an engineering inference from the documented acknowledgement behavior. The inspected stable documentation identifies itself as 2.12.0; this report does not establish a current release cadence.

### 27. [tomerfiliba-org/rpyc](https://github.com/tomerfiliba-org/rpyc)

**Language/role:** Python symmetric object-proxy RPC, with synchronous and asynchronous invocation.

- **C1:** Exposing an object exposes a navigable object graph, so attribute-access policy is part of protocol correctness and security. The [security design](https://rpyc.readthedocs.io/en/latest/docs/security.html) explains restricted wrappers, custom attribute hooks, and why classic mode intentionally grants broad authority.
- **C2:** The [implementation theory](https://rpyc.readthedocs.io/en/latest/docs/theory.html) separates immutable values passed by value from mutable/location-sensitive objects passed by reference, reconstructed as network proxies. Symmetric peers can both dispatch requests and serve callbacks.

Study transparent remote object behavior and its limits. The project documentation recommends trusted-network use and distinguishes service-restricted operation from classic full-control mode; these are material architectural boundaries, not interchangeable configurations.

## Search coverage, exclusions, and limitations

Discovery used more than six distinct live-search formulations, including: cross-language RPC/IDL compiler architecture; Rust async RPC and JSON-RPC; Go Kitex/Twirp/Connect/DRPC alternatives; JVM and C++ service frameworks; Python broker-backed and object-proxy RPC; embedded Protobuf generators; .NET and TypeScript RPC; protocol-agnostic Smithy/Wire generation; datacenter packet-loss/ownership design; and HPC RPC over libfabric/UCX. Follow-up searches targeted retries, concurrency, compiler pruning, source code, and changelogs. Later broad searches increasingly returned already-covered families, third-party ports, tutorials, or application-specific clients, so expansion stopped after retaining distinct implementation approaches rather than filling a quota.

Each retained canonical repository page was opened, including the Tonic redirect, and at least one additional primary document or implementation source was read. Architecture, protocol specifications, source comments, and API contracts supply the substantive evidence. Wire and Finagle’s inspected multi-year changelogs support their C4 judgments. Repository stars and raw commit counts were not used as quality evidence. Source links target verified pages/files; mutable branches and `latest` documentation can change after this research date.

The selection excludes duplicate forks and generated wrappers, general API SDK collections, RPC applications such as blockchain endpoint proxies, and unrelated uses of the acronym RPC. OpenAPI/REST generators were left outside this report’s service-RPC and binary-protocol emphasis. Additional implementations such as SRPC, third-party Twirp ports, and other language bindings appeared in searches but were not needed to represent another clearly distinct architecture after the retained set. This is not an exhaustive inventory of historical CORBA/ONC-RPC, Erlang, or every language community.

No retained project is presented as an official mirror or archived project without evidence of that status, and no current maintenance cadence is inferred from a recent push or a README assertion. Finagle, eRPC, and Nameko have explicit evidence limitations above; Cap’n Proto and Tonic have branch caveats. Some documentation fetches failed or rendered no text; readable official documentation or raw implementation files were used instead. No candidate code was executed, repositories were not cloned, and performance claims were limited to documented mechanisms rather than unverified benchmark comparisons.
