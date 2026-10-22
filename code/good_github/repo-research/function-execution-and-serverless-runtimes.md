# Function execution and serverless runtimes

Research date: **2026-10-09**.

This report selects **25 GitHub repositories** that implement function execution: complete FaaS platforms, language hosts and invocation protocols, edge and WebAssembly runtimes, research execution systems, and durable function engines. The last group coordinates remotely hosted user code rather than supplying its language sandbox. General deployment frameworks, infrastructure provisioning tools, and general-purpose virtual machines are outside the selection unless their function-execution subsystem is the subject of the entry. Each repository is counted once, including monorepos.

The criteria are judgments grounded in the linked primary material, not certifications of correctness or production readiness. Architectural mechanisms are distinguished from benchmark claims; no numerical performance comparisons are endorsed here. Branch links describe the inspected source snapshot and can change.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, adversarial input, or failures. **C2** — substantial reusable abstractions supporting multiple use cases. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — sustained evolution with evidence of compatibility management, testing, or controlled complexity, beyond repository age alone.

## Container platforms and function-serving infrastructure

### 1. [apache/openwhisk](https://github.com/apache/openwhisk)

**Language / role:** Scala-centered, polyglot serverless platform. Study the boundary between action containers, invokers, activation records, and the programming model of actions, triggers, rules, and compositions.

- **C1:** The intra-container concurrency design explicitly connects runtime opt-in, action concurrency limits, decoupled log collection, and Kafka message buffering. It documents that buffered activations can be lost on an invoker crash—a useful concrete failure boundary, rather than a blanket reliability promise. Start with [intra-instance concurrency](https://github.com/apache/openwhisk/blob/master/docs/intra-concurrency.md).
- **C2:** Namespaces, packages, actions, and feeds form a reusable execution and composition model, with explicit naming rules and resource limits. The [system reference](https://github.com/apache/openwhisk/blob/master/docs/reference.md) provides the second entry point.

The repository also records a breaking Akka-to-Pekko transition requiring cluster replacement and traffic cutover; readers should distinguish current source from older deployment descriptions.

### 2. [fission/fission](https://github.com/fission/fission)

**Language / role:** Go; Kubernetes FaaS with reusable language environments. Particularly useful for understanding how source packages become specialized function pods without requiring a fresh image build for every function change.

- **C2:** Executor, router, builder manager, storage service, and admission webhook have distinct responsibilities. Three executor types—pool manager, new deployment, and container—support different deployment models behind the function abstraction. See the [architecture](https://fission.io/docs/architecture/).
- **C3:** The repository describes maintaining warm environment containers and loading function code into a selected container on demand. The architecture also removes the control plane from subsequent request forwarding once a pod is placed. These are identifiable cold-start and request-path optimizations, without relying on the README's latency number.

Read the repository's warm-pool explanation alongside the architecture page. The latter documents the older REST controller's deprecation, avoiding confusion with historical Fission diagrams.

### 3. [knative/serving](https://github.com/knative/serving)

**Language / role:** Go; request-driven, scale-to-zero serving infrastructure for containerized functions and services. This is the serving subsystem, not the whole Knative ecosystem or its function-scaffolding CLI.

- **C1:** Scaling from zero requires coordinating buffered requests, the activator, autoscaler, and arriving pods. The queue-proxy sidecar enforces the configured concurrency before forwarding to user code. These coupled admission and lifecycle responsibilities are explained in the [serving architecture](https://knative.dev/docs/serving/architecture/).
- **C2:** Controllers, resource validation, and the internal networking abstraction separate workload lifecycle from interchangeable ingress implementations.
- **C3:** The activator buffers bursts, while per-pod queue proxies collect the metrics that inform scaling. The same architecture page connects these components to the actual traffic path, making this a strong study of feedback-controlled serving rather than merely “autoscaling support.”

### 4. [nuclio/nuclio](https://github.com/nuclio/nuclio)

**Language / role:** Go-centered, with language-specific workers; event and data-processing FaaS. Study its processor internals when event-source semantics and worker allocation matter as much as HTTP serving.

- **C1:** Its documented allocator design distinguishes synchronous workers from asynchronous processing, while retaining exclusive allocation where a runtime event processor cannot safely be shared. Event listeners also own source-specific checkpoint, acknowledgement, and retry behavior. See [processor architecture](https://docs.nuclio.io/en/stable/concepts/architecture.html).
- **C2:** A common event representation, runtime engines, event processors, and data bindings decouple function logic from event sources and deployment platforms.
- **C3:** The architecture discusses parallel workers, shared-memory communication, persistent data connections, and batching. These mechanisms expose the performance tradeoffs directly. Delivery guarantees remain dependent on the event-source implementation; the documentation should not be read as a universal exactly-once guarantee for arbitrary external side effects.

### 5. [fnproject/fn](https://github.com/fnproject/fn)

**Language / role:** Go; container-native function server. The agent package is a compact entry into execution scheduling below the deployment API.

- **C1:** Resource reservations must survive cancellation and be released once. The resource tracker uses a condition variable for admission, context cancellation to wake waiters, and `sync.Once` for token release. Study [resource.go](https://github.com/fnproject/fn/blob/master/api/agent/resource.go).
- **C2:** The [agent package contract](https://github.com/fnproject/fn/blob/master/api/agent/doc.go) separates call creation/execution, memory ownership, container lifecycle, and start/end callbacks. Local Docker execution and load balancing across sub-agents implement the same central abstraction.
- **C3:** Admission accounts for both CPU and memory, including resources reserved by idle warm containers; blocking and nonblocking acquisition expose an explicit capacity tradeoff.

### 6. [openfaas/faas](https://github.com/openfaas/faas)

**Language / role:** Go-centered gateway and platform integration repository. Study the function-facing gateway and provider boundary; the complete OpenFaaS implementation spans multiple repositories.

- **C2:** Functions are OCI-packaged workloads managed through a gateway API, with orchestration supplied through the provider interface. The [stack architecture](https://docs.openfaas.com/architecture/stack/) distinguishes gateway, queue, metrics, and infrastructure responsibilities.
- **C3:** Synchronous invocation and queued asynchronous invocation follow different execution paths. Prometheus metrics feed scaling, and the asynchronous path uses NATS to buffer work. This provides a concrete example of separating request handling from queued capacity management.

**Distribution limitation:** The inspected repository describes Community Edition usage restrictions and separately maintained commercial distributions. Treat the public code as the study target; do not assume commercial-only scaling or event integrations are implemented in this repository. The repository README and stack documentation are the entry points.

### 7. [open-runtimes/executor](https://github.com/open-runtimes/executor)

**Language / role:** PHP with coroutine-based serving; a container runtime executor used in the Open Runtimes ecosystem. This selection targets the executor implementation, not the collection of language-image templates.

- **C1:** Execution crosses container readiness, log availability, runtime disappearance, and command timeout boundaries. The [Docker runner](https://github.com/open-runtimes/executor/blob/main/src/Executor/Runner/Docker.php) implements bounded waits and translates orchestration failures into executor errors.
- **C2:** The [HTTP controllers](https://github.com/open-runtimes/executor/blob/main/app/controllers.php) expose runtime creation, invocation, command execution, log streaming, and deletion through an injected runner abstraction. They handle version-specific runtime conventions, environment construction, and resource configuration, allowing many language runtimes to share one lifecycle service.

Its value is the connection between a relatively small HTTP contract and substantial container lifecycle behavior, including validation and compatibility concerns.

## Language hosts, invocation adapters, and local runtime emulation

### 8. [Azure/azure-functions-host](https://github.com/Azure/azure-functions-host)

**Language / role:** C#; the host/runtime behind Azure Functions. Focus on the host and language-worker boundary, rather than treating each language worker as another entry in this report.

- **C1:** Startup, capability negotiation, function loading, invocation, and response correlation are distinct protocol phases. Messages share a bidirectional gRPC stream and carry request identifiers. Maintaining those lifecycle relationships is a concrete correctness problem exposed by the [language extensibility design](https://github.com/Azure/azure-functions-host/wiki/Language-Extensibility).
- **C2:** The host manages function events while separate language processes execute user code. The same contract carries function metadata, binding data, parameters, results, and structured logs, supporting multiple language implementations without embedding them into one interpreter.

The wiki is an older architectural description; use it to understand the protocol, not as authority for every current process-count or configuration default. The canonical repository identifies the current implementation under its `dev` branch.

### 9. [aws/aws-lambda-rust-runtime](https://github.com/aws/aws-lambda-rust-runtime)

**Language / role:** Rust; Lambda execution runtime, HTTP adapter, event types, extensions, and shared Runtime API client in one workspace.

- **C1:** The [runtime implementation](https://github.com/aws/aws-lambda-rust-runtime/blob/main/lambda-runtime/src/runtime.rs) combines typed deserialization, panic-catching service layers, response handling, and invocation context. The inspected source also has separate sequential/concurrent execution paths and ordered snapshot/restore hooks, making lifecycle ordering explicit.
- **C2:** Tower `Service` and `Layer` abstractions allow reusable handler middleware. The workspace separates the runtime protocol client from HTTP/event adaptation and extension support, so it serves much more than one handler template.
- **C3:** The concurrent path sizes the API-client pool to the worker count and uses independently polled worker tasks; it exposes how protocol concurrency affects allocation and connection reuse.

Start with the workspace overview in the repository and `runtime.rs`; avoid assuming newer optional execution modes apply to all Lambda environments.

### 10. [aws/aws-lambda-runtime-interface-emulator](https://github.com/aws/aws-lambda-runtime-interface-emulator)

**Language / role:** Go; local Lambda Runtime and Extensions API emulator. **Official AWS source export/mirror:** the README says the GitHub repository is generated from an internal source of truth; it contains substantial runtime implementation, not just generated API wrappers.

- **C1:** [Shutdown handling](https://github.com/aws/aws-lambda-runtime-interface-emulator/blob/develop/internal/lambda/rapid/shutdown.go) coordinates unexpected process exits, mutex-protected state, exit-notification channels, extension shutdown events, deadlines, and forced termination. It explicitly guards against indefinite waits for processes that cannot exit promptly.
- **C2:** The same emulator can exercise different language Runtime API clients and packaged extensions, converting local HTTP invocations into the execution protocol described in the repository README.

Its scope is deliberately limited: it does not reproduce Lambda's cloud orchestrator, security/authentication configuration, or every service integration. That boundary makes it useful for studying protocol fidelity and process lifecycle independently of a full FaaS control plane.

### 11. [GoogleCloudPlatform/functions-framework-nodejs](https://github.com/GoogleCloudPlatform/functions-framework-nodejs)

**Language / role:** TypeScript/Node.js; portable function invocation framework. This is a focused host implementation with real execution semantics, despite being smaller than the platform repositories.

- **C1:** [Function wrappers](https://github.com/GoogleCloudPlatform/functions-framework-nodejs/blob/main/src/function_wrappers.ts) guard against duplicate callbacks, catch rejected promises and request-associated errors, and normalize binary/structured CloudEvents and legacy event shapes.
- **C2:** HTTP, callback-style background functions, promise-based functions, and CloudEvent handlers share a common wrapping and response mechanism rather than requiring unrelated servers.
- **C4:** The [changelog](https://github.com/GoogleCloudPlatform/functions-framework-nodejs/blob/main/CHANGELOG.md) records releases across 2021–2026, conformance-test integration, testing helpers, Node support changes, and TypeScript module-resolution fixes. This is concrete evidence of sustained compatibility and test management, not merely an old creation date.

### 12. [brefphp/bref](https://github.com/brefphp/bref)

**Language / role:** PHP; Lambda runtimes for HTTP applications, event functions, and console workloads. The runtime subsystem is the study target, alongside its broader deployment tooling.

- **C1:** [FpmHandler](https://github.com/brefphp/bref/blob/master/src/FpmRuntime/FpmHandler.php) reserves time for cleanup before the invocation deadline, restarts FPM after communication failures or timeouts, and handles stale PID/socket state. Its comments explain why a superficially gentler signal can let a previous request continue executing.
- **C2:** The [FPM runtime guide](https://bref.sh/docs/runtimes/fpm-runtime) explains how API Gateway requests become FastCGI requests, allowing existing PHP frameworks to execute through Lambda without rewriting their HTTP model.
- **C4:** The [November 2020 release account](https://bref.sh/news/01-bref-1.0) documents OS/runtime and extension migrations; the [3.0 upgrade guide](https://bref.sh/docs/upgrading/v3) specifies subsequent PHP, image, layer, and extension changes. Together they show years of deliberate compatibility management.

## JavaScript and TypeScript edge execution

### 13. [cloudflare/workerd](https://github.com/cloudflare/workerd)

**Language / role:** Primarily C++; JavaScript/Wasm server runtime underlying Cloudflare Workers. Study capability binding and isolate composition rather than assuming a traditional process-per-service architecture.

- **C2:** Explicit service and resource bindings supply capabilities to independently configured workers. The same runtime supports application serving, programmable proxies, and local execution of Workers applications. See the repository's design principles.
- **C3:** Cloudflare's [architecture explanation](https://blog.cloudflare.com/workerd-open-source-workers-runtime/) connects same-process worker execution to lower inter-service overhead and explains why native implementations of built-in APIs can be shared across isolates instead of loading separate JavaScript copies into each one.

Compatibility dates are another useful subsystem to inspect. **Isolation limitation:** the repository expressly says standalone `workerd` is not a hardened sandbox; Cloudflare's hosted deployment adds defenses beyond this repository. Capability-oriented design should not be mistaken for a complete hostile-tenant security boundary.

### 14. [supabase/edge-runtime](https://github.com/supabase/edge-runtime)

**Language / role:** Rust with JavaScript/TypeScript interfaces; Deno-based server for edge functions and programmable request routing.

- **C1:** Main and user runtimes have different authority. User runtimes require memory/time limits and receive only explicitly allowed environment variables, while the main runtime performs routing and preprocessing. These are concrete resource and authority boundaries in the repository architecture.
- **C2:** The [implementation introduction](https://supabase.com/blog/edge-runtime-self-hosted-deno-functions) describes the Rust HTTP server, main-worker thread, and user-worker API. The main module can authenticate, route, and delegate requests, making the execution system reusable for both hosted functions and proxies.
- **C3:** Embedding `deno_core` permits multiple separately configured V8 contexts within the server process, rather than launching a general Deno CLI for every invocation.

The README labels the software beta and warns of API/configuration changes. Treat numerical defaults in the older introduction as historical, not current limits.

### 15. [vercel/edge-runtime](https://github.com/vercel/edge-runtime)

**Language / role:** TypeScript; local edge-function execution and Web API compatibility packages. It is useful for studying a test/development runtime, not a complete distributed edge hosting service.

- **C1:** [EdgeVM](https://github.com/vercel/edge-runtime/blob/main/packages/vm/src/edge-vm.ts) handles cross-realm `instanceof` behavior, rejected promises, exception forwarding, fetch-listener cardinality, invalid responses, and `waitUntil` work. These are subtle language and event-lifecycle semantics that simple VM wrappers commonly miss.
- **C2:** The [VM API guide](https://edge-runtime.vercel.app/packages/vm) exposes configurable contexts and extension hooks, while the implementation composes reusable Web API primitives with fetch dispatch. Separate packages support testing and runtime adaptation.

The VM documentation describes simulation of edge conditions locally. Its use of Node VM contexts is not evidence that this package alone provides a production security sandbox for hostile code.

## WebAssembly function and component runtimes

### 16. [spinframework/spin](https://github.com/spinframework/spin)

**Language / role:** Rust; framework and execution runtime for serverless WebAssembly applications. The canonical repository is now under `spinframework`; it is counted once, not again under its older organization name.

- **C1:** [Store limits and tests](https://github.com/spinframework/spin/blob/main/crates/core/src/limits.rs) implement asynchronous memory/table growth admission. Tests check accepted versus rejected growth and memory accounting, including a real component instantiation.
- **C2:** Runtime-supplied capabilities allow application variables, key/value storage, SQL, and other services to change implementation without changing application code. The versioned [runtime configuration guide](https://github.com/spinframework/spin-docs/blob/main/content/v3/dynamic-configuration.md) describes provider selection and override precedence.

An experienced reader can move from the small limiter to the larger component host: it is a clear example of embedding Wasmtime while retaining application-level configuration and resource policy. The linked configuration guide is explicitly for Spin v3, rather than a claim that it specifies every current release.

### 17. [wasmCloud/wasmCloud](https://github.com/wasmCloud/wasmCloud)

**Language / role:** Rust runtime plus Go Kubernetes components; distributed hosting for Wasm components, including functions. **Relevant monorepo subsystem:** `crates/wash-runtime`, with the operator providing placement around it.

- **C1:** Capability availability is part of host construction. The runtime example supplies a deny-all outgoing HTTP implementation when a handler is absent, making the default authority boundary explicit. See the [runtime architecture and embedding guide](https://github.com/wasmCloud/wasmCloud/blob/main/crates/wash-runtime/README.md).
- **C2:** Engine, Host, and Workload separate compilation/configuration, capability plugins, and component lifecycle. WASI HTTP, configuration, logging, blob storage, and key/value interfaces can be supplied by host plugins rather than baked into each function.

The inspected root README documents the current `wash-runtime` structure and a deprecated gateway retained for compatibility. Older actor/lattice descriptions should not automatically be applied to this snapshot. Read the runtime guide with the root monorepo map.

### 18. [faasm/faasm](https://github.com/faasm/faasm)

**Language / role:** C++; stateful WebAssembly serverless runtime with a scientific/parallel-computing emphasis. Useful when functions must cooperate over data instead of remaining isolated stateless handlers.

- **C2:** The [host interface](https://github.com/faasm/faasm/blob/main/docs/source/host_interface.md) combines function chaining, input/output, state, WASI, dynamic linking, and parallel-programming support. Its filesystem model explicitly separates global reads from local writes, directing inter-function sharing through state APIs.
- **C3:** [State documentation](https://github.com/faasm/faasm/blob/main/docs/source/state.md) explains byte-addressable state access: a function can request only its relevant portion of a large value rather than transferring the entire object. This ties data movement costs to a concrete reusable abstraction.

These mechanisms make Faasm a distinct study of state transfer and legacy-program support. They do not by themselves establish a particular consistency guarantee for every combination of concurrent state operations.

### 19. [funlessdev/funless](https://github.com/funlessdev/funless)

**Language / role:** Elixir with Rust/Wasmtime execution; experimental research FaaS for cloud/edge environments. The repository explicitly says it is not production-ready.

- **C2:** The core schedules invocations and stores function/module metadata; workers provide execution. The [invocation domain module](https://github.com/funlessdev/funless/blob/main/worker/lib/worker/domain/invoke_function.ex) further separates provisioning, raw-resource storage, waiting for missing code, and execution through ports/adapters.
- **C3:** The documented worker caches function resources to avoid repeatedly transferring code. The source demonstrates a concrete recovery path: try provisioning, look up locally stored code keyed by function identity/hash, then wait for code if it is still missing.

Study this for the interaction between BEAM orchestration and Wasm execution. The root README's old `apps/worker` path is stale relative to the inspected tree; the verified implementation entry point above uses `worker/lib/worker/domain`.

## Research and historical execution architectures

### 20. [open-lambda/open-lambda](https://github.com/open-lambda/open-lambda)

**Language / role:** Primarily Go; research-oriented serverless platform. The repository presents its single-node worker as the main implemented system and distinguishes it from ongoing cluster work.

- **C1:** A lambda instance can exist without a backing sandbox, create one on demand, restart it after failure, and pause it when idle. Requested instance count can exceed the number of containers that available memory permits. These lifecycle distinctions are explicit in the [worker design](https://github.com/open-lambda/open-lambda/blob/main/docs/worker/README.md).
- **C2:** Sandbox, lambda, and event layers separate isolation mechanisms, execution instances, and triggers; the sandbox layer is pluggable.
- **C3:** Instance demand responds to queued work and measured invocation time, while the SOCK execution approach targets provisioning overhead. This makes the worker a useful experimental platform for admission and cold-start policies, without implying production readiness.

### 21. [ut-osa/nightcore](https://github.com/ut-osa/nightcore)

**Language / role:** C++ core with multiple language workers; historical ASPLOS 2021 research FaaS prototype for latency-sensitive microservices. The inspected branch is `asplos-release`.

- **C1:** The [dispatcher](https://github.com/ut-osa/nightcore/blob/asplos-release/src/engine/dispatcher.cpp) maintains connected, idle, running, requested, and assigned worker state under synchronization. Completion/failure handling must account for a worker that has already disconnected.
- **C3:** Dispatch distinguishes inline from shared-memory payloads, queues calls when no worker is available, limits concurrency, and can discard excessively delayed queued work relative to measured processing time. These choices make queueing and communication overhead directly inspectable.

The repository's language-worker examples and dispatcher are useful entry points for internal function calls. Treat the project as an experimental design and benchmark artifact; this report makes no claim of current production maintenance or of reproducing its advertised latency.

### 22. [knix-microfunctions/knix](https://github.com/knix-microfunctions/knix)

**Language / role:** Python and Java components; container-isolated applications with process-based function execution. **Archived historical project** from Nokia Bell Labs; the repository also explains that research priorities shifted and maintenance time became limited.

- **C1:** The [Python function worker](https://github.com/knix-microfunctions/knix/blob/develop/FunctionWorker/python/FunctionWorker.py) forks invocation processes, manages signal behavior and child reaping, decodes user input, and applies workflow input transformations while propagating metadata and errors.
- **C3:** API/state helper objects are initialized before forking so children benefit from copy-on-write; per-invocation work is moved after the fork where possible. This exposes a different startup/resource tradeoff from per-function containers or Wasm instances.

The root overview also identifies workflow support compatible with Amazon States Language and long-running functions. Study the implementation as historical systems work, with particular attention to inherited process state and isolation boundaries.

## Durable execution of functions

### 23. [inngest/inngest](https://github.com/inngest/inngest)

**Language / role:** Go execution backend with TypeScript UI components; event-triggered durable functions. User functions can remain hosted separately and are invoked over HTTP.

- **C1:** [Queue item leasing](https://github.com/inngest/inngest/blob/main/pkg/execution/queue/lease_item.go) checks existing leases, atomically acquires local capacity, releases permits once on failure paths, applies account/function constraints, and acquires a lease before requeueing the partition pointer. The source explains the contention and ordering consequences of getting that sequence wrong.
- **C2:** The repository's architecture separates event intake, runner, queue, executor, incremental state, and management APIs. Event waiting, cancellation, retries, and step results are execution-engine responsibilities rather than application-specific queue code.
- **C3:** Multi-tenant queueing and layered capacity constraints make fairness and backpressure part of the architecture.

**License scope:** The inspected README describes the server/CLI as SSPL with delayed Apache publication; the SDK license is separate.

### 24. [microsoft/durabletask-netherite](https://github.com/microsoft/durabletask-netherite)

**Language / role:** C#; execution/storage backend for Durable Functions and the Durable Task Framework.

- **C2:** Netherite preserves the application-facing Durable Functions/DTFx API while replacing the backend representation. It therefore supports existing orchestrations and entities through a substantial execution abstraction. The repository clearly distinguishes API compatibility from unsupported migration of existing task-hub contents.
- **C3:** Its architecture replaces many small queue/table operations with ordered Event Hubs streams and partition state represented by immutable logs and checkpoints. Batching is the concrete response to storage-operation throughput limits. Start with the repository's “Why a new engine?” discussion and the official [configuration guide](https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/quickstart-netherite).

**Support limitation:** Microsoft states that Netherite backend support ends **March 31, 2028**. The same guide explains partition configuration and that switching providers starts a fresh task hub. This is a useful backend-design study, not an unqualified new-deployment recommendation.

### 25. [restatedev/restate](https://github.com/restatedev/restate)

**Language / role:** Rust; durable execution server for remotely deployed handlers, including serverless functions. The server persists and coordinates invocation progress; the application's language runtime remains separate.

- **C1:** Journaling and replay must preserve completed work, while entity state needs single-writer coordination. The current [architecture and key concepts](https://docs.restate.dev/foundations/key-concepts) describe crash recovery, duplicate-request handling through idempotency keys, and behavior when service-to-server journal communication fails.
- **C2:** Durable handlers, timers, promises, virtual-object state, and resilient service communication provide reusable building blocks for workflows and event processing across language SDKs.
- **C3:** Waiting handlers can suspend on FaaS and resume later, avoiding occupied function execution while external events are pending; the same document explains concurrency flow control.

Read these guarantees within the SDK/journal contract. Arbitrary unjournaled external effects are not made exactly-once simply by placing a handler behind the server.

## Coverage, search process, and limitations

Live discovery used more than six distinct formulations, including: Kubernetes FaaS architecture; WebAssembly function isolation; edge isolate runtimes; OpenLambda/Nightcore cold-start research; cloud Runtime API implementations; PHP FastCGI on Lambda; JVM/KNIX execution; and durable serverless workflow engines. Follow-up searches checked project status and Netherite retirement. Later results increasingly repeated the same platforms or surfaced deployment plugins, language-image templates, tutorials, and small unproven wrappers, providing diminishing additional coverage.

The selection spans Kubernetes control/data planes, plain container executors, cloud-language hosts, local emulation, V8 contexts, Wasm components, fork-based research systems, and journaled remote execution. Implementation communities include Apache, CNCF projects, cloud providers, independent PHP projects, Supabase/Vercel, university research, and Nokia Bell Labs. The language mix includes Go, Scala, C#, Rust, C++, TypeScript, PHP, Elixir, Python, and Java components.

Canonical repository pages or GitHub API metadata were read for every entry, followed by separate primary documentation or implementation material. Additional source files were read directly from GitHub where useful; rereading a root README through its raw URL was not counted as an independent source. Unauthenticated GitHub API rate limiting occurred during metadata checks; normal repository pages and raw source remained accessible and supplied the remaining verification. No candidate code was executed, dependencies installed, or repositories cloned.

General VM/isolation projects such as Firecracker and general-purpose Wasm engines were left out because the focus here is the function execution layer built above them. Deployment-oriented tools such as Serverless Framework and SAM were excluded from the main list. SDK examples, runtime-image catalogs, benchmark-only companion repositories, and forks were not counted as independent systems. Spin's organization move is normalized to its canonical URL; the AWS emulator's official internal-source export and KNIX's archival status are identified explicitly.

This is a source-based selection guide, not an exhaustive inventory, benchmark comparison, security audit, or claim that every component in each repository is uniformly exemplary. Research prototypes and archived systems are retained for substantive architectural contrasts. Maintenance is not inferred from stars, age, or a recent push, and **C4** is awarded only where the inspected historical and compatibility material supports it.
