# Distributed tracing instrumentation and collection systems

Research date: **2026-10-09**

This selection covers libraries that create and propagate spans, automatic instrumentation agents, and systems that receive, process, sample, and forward distributed traces. Full tracing platforms are included only where their collection subsystem provides a substantial study target. The 22 repositories span Go, Java, Scala, C#, C/C++, Python, TypeScript, Rust, and Erlang/Elixir. Each repository heading links to its verified canonical GitHub page; the nearby implementation and documentation links are suggested reading entry points.

Criteria are judgments grounded in the cited material, not certifications of the entire codebase:

- **C1 — Difficult correctness:** invariants, concurrency, context isolation, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and components supporting multiple integrations or use cases.
- **C3 — Performance with structure:** concrete resource or throughput constraints addressed through an understandable design.
- **C4 — Sustained evolution:** evidence across years together with compatibility, testing, or complexity management. Age alone does not qualify.

## Collection pipelines and sampling

### 1. [open-telemetry/opentelemetry-collector](https://github.com/open-telemetry/opentelemetry-collector)

**Language/role:** Go; vendor-neutral telemetry collection framework, with trace pipelines as the relevant subsystem.

Study how a configurable processing graph becomes a running service, particularly the difference between sharing receivers/exporters and creating separate processor instances. This is a useful foundation for understanding the other Collector-based projects here.

- **C1:** Fan-out uses synchronous calls: a blocking processor can stall sibling pipelines and the shared receiver. Pipeline construction also rejects components that do not support the selected signal. These are concrete coupling and configuration invariants documented in the [architecture guide](https://opentelemetry.io/docs/collector/architecture/).
- **C2:** Receiver, processor, exporter, and pipeline boundaries allow independent protocol implementations and processing chains, with the same framework deployable beside applications or as a remote gateway. The [architecture guide](https://opentelemetry.io/docs/collector/architecture/) explains instance ownership and composition rather than merely listing integrations.

### 2. [open-telemetry/opentelemetry-collector-contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib)

**Language/role:** Go; Collector component monorepo. Focus on `processor/tailsamplingprocessor`, not every receiver or exporter.

The tail sampler is a particularly instructive example of bounded, stateful processing inside an otherwise composable telemetry pipeline.

- **C1:** All spans for a trace must reach one collector instance. Late arrivals may inherit an existing decision or receive a new decision after eviction; decision caches change those semantics. Rebatching also discards the original request context, imposing processor-ordering requirements. See the [tail-sampling implementation guide](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/tailsamplingprocessor/README.md).
- **C3:** Circular-buffer capacity, decision waiting time, cache size, and sampling-evaluation latency determine memory use and premature trace loss. The same guide provides diagnostic metrics and explains why slow downstream processing can worsen eviction. These are useful resource/accuracy tradeoffs, not a claim of lossless collection.

The inspected component is labeled **beta**; stability and ownership vary throughout this monorepo.

### 3. [honeycombio/refinery](https://github.com/honeycombio/refinery)

**Language/role:** Go; distributed tail-sampling proxy.

Study sampling as a distributed state-management problem: concentrating spans, deciding when a trace is sufficiently complete, and retaining decisions after releasing span payloads.

- **C1:** Root-span arrival triggers a short completion delay, while a separate timeout handles missing roots. Subsequent spans reuse a retained sampling decision. Graceful shutdown stops intake and drains traces toward peers. These failure and late-arrival behaviors are explicit in the [configuration reference](https://github.com/honeycombio/refinery/blob/main/refinery_config.md).
- **C3:** Incoming queues can drop spans; memory pressure can eject traces early; collection workers partition traces using consistent hashing. The [same reference](https://github.com/honeycombio/refinery/blob/main/refinery_config.md) connects queue bounds, memory limits, span limits, and worker concurrency to their operational consequences.

The repository documents Honeycomb-oriented deployment and sampling semantics; assess that integration boundary when studying reuse elsewhere.

### 4. [jaegertracing/jaeger](https://github.com/jaegertracing/jaeger)

**Language/role:** Go; tracing platform, focusing on collectors, Kafka ingestion, and storage-export components.

Jaeger offers a concrete study of adapting the OpenTelemetry Collector framework into a tracing-specific system. The relevant implementation is collection and ingestion, rather than its separately developed UI.

- **C2:** Jaeger v2 composes upstream Collector components with Jaeger-specific storage exporters and query extensions. A single binary supports distinct operational roles, making framework reuse and domain-specific extension visible in the [v2 architecture](https://www.jaegertracing.io/docs/2.11/architecture/).
- **C3:** The architecture distinguishes direct storage writes, short-lived in-memory buffering, and a persistent Kafka queue with independently scalable ingesters. It explicitly identifies dropped-data risk when storage cannot sustain a traffic spike, and the cost of extra serialization when another Collector is placed upstream. See the [same architecture discussion](https://www.jaegertracing.io/docs/2.11/architecture/).

The repository also publishes configuration-deprecation guarantees; do not confuse this v2 design with older Jaeger agent/client architectures.

### 5. [openzipkin/zipkin](https://github.com/openzipkin/zipkin)

**Language/role:** Java, with a JavaScript UI; trace reception, validation, codecs, and storage integration.

Study the boundary between the trace model, its encodings, collection transports, and persistence. The monorepo counts once; the collector and core/storage libraries are the relevant parts.

- **C2:** The core library supplies trace models and v1/v2 JSON codecs, while `StorageComponent` abstracts storage and queries with synchronous or asynchronous calls. These are reusable outside the packaged server, as explained in the [repository's core/storage overview](https://github.com/openzipkin/zipkin#core-library).
- **C3:** Collection is separated from application execution through asynchronous reporting, and persistence implementations use backend-specific indexing rather than treating storage as a generic append operation. The [architecture guide](https://zipkin.io/pages/architecture.html) explains transport and collector responsibilities; the repository describes Cassandra and Elasticsearch indexing choices and distinguishes testing-only in-memory storage from realistic workloads.

## Runtime agents and automatic instrumentation

### 6. [open-telemetry/opentelemetry-java-instrumentation](https://github.com/open-telemetry/opentelemetry-java-instrumentation)

**Language/role:** Java; bytecode agent, instrumentation APIs, and standalone library instrumentations.

Study safe injection into applications with different class loaders and dependency versions. The repository contains substantial shared machinery beyond its large catalog of integrations.

- **C1:** Muzzle records referenced classes, fields, and methods at build time and checks them against the application's classpath at runtime. A mismatch rejects the instrumentation; helper dependencies also determine injection order. The [Muzzle design](https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/docs/contributing/muzzle.md) explains compatibility checks and tests against both supported and unsupported library versions.
- **C2:** The [agent structure](https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/docs/contributing/javaagent-structure.md) separates system, bootstrap, agent, and extension class loaders. Its common Instrumenter API works for both injected and standalone instrumentation, exposing a reusable design beneath framework-specific interception.

### 7. [apache/skywalking-java](https://github.com/apache/skywalking-java)

**Language/role:** Java; Apache SkyWalking's tracing agent and plugin system.

Study an agent whose trace model explicitly distinguishes entry, local, and exit spans, and separates process-to-process propagation from thread-to-thread continuation.

- **C1:** `ContextCarrier` serializes context across service boundaries; `ContextSnapshot` captures and continues it across threads. These distinct mechanisms must preserve the same causal trace while obeying different lifetime and transport constraints. The [plugin development guide](https://github.com/apache/skywalking-java/blob/main/docs/en/setup/service-agent/java-agent/Java-Plugin-Development-Guide.md) gives concrete sequences for both.
- **C2:** Plugins declare interception points while shared agent code handles bytecode manipulation and tracing context. The guide also describes interceptor APIs and a plugin test tool that verifies collected/reported data. This makes the project useful for studying how instrumentation authors are insulated from agent internals.

This is the separate Java-agent repository; the broader SkyWalking backend is not counted again.

### 8. [pinpoint-apm/pinpoint](https://github.com/pinpoint-apm/pinpoint)

**Language/role:** Primarily Java; agent, collector, and tracing platform in one monorepo.

Focus on agent plugins and their shared data contract with the collector. Pinpoint distinguishes a transaction's distributed spans from the method-level `SpanEvents` recorded inside each span.

- **C1:** Distributed spans share a propagated transaction ID, while service-type and annotation identifiers must remain unique and consistently interpreted across agent, collector, and web components. The [plugin developer guide](https://pinpoint-apm.gitbook.io/pinpoint/documents/plugin-dev-guide) explains these invariants and the call-stack representation.
- **C2:** `ProfilerPlugin`, `ServiceLoader`, and declarative type metadata provide an extension mechanism covering instrumentation and downstream interpretation. The same guide describes its loading contract; the [compatibility tables](https://github.com/pinpoint-apm/pinpoint#compatibility) show why agent and collector versions must be considered separately.

### 9. [DataDog/dd-trace-dotnet](https://github.com/DataDog/dd-trace-dotnet)

**Language/role:** C# and C++; managed tracer and native CLR instrumentation. Focus on `tracer`, not the separate continuous-profiler subsystem.

Study the bridge between rewritten runtime methods and reusable managed instrumentation, including async completion and target types that cannot be referenced directly.

- **C1:** CallTarget distinguishes method entry, ordinary return, and asynchronous completion. Cleanup and exception recording must follow the completed task, including differing `Task`/`ValueTask` result shapes. The [automatic-instrumentation guide](https://github.com/DataDog/dd-trace-dotnet/blob/master/docs/development/AutomaticInstrumentation.md) describes these contracts and limitations.
- **C2:** Common callback shapes, instrumentation attributes, and duck-typing constraints let integrations handle many library APIs without taking direct dependencies on their types. The same guide ties this machinery to package-version matrices, mock-agent assertions, and expected span metadata, providing a concrete path from abstraction to verification.

### 10. [elastic/apm-agent-python](https://github.com/elastic/apm-agent-python)

**Language/role:** Python; framework integrations, callable instrumentation, and background APM transport.

This is a useful contrast with VM bytecode agents: collection combines framework lifecycle signals with `wrapt`-based interception of client libraries.

- **C1:** Span creation requires an active transaction; async workloads use a distinct capture interface; distributed transaction continuation requires extracting the incoming TraceParent. These lifetime and causality requirements are explicit in the [custom-instrumentation guide](https://www.elastic.co/docs/reference/apm/agents/python/instrumenting-custom-code).
- **C2:** The agent separates framework integration, library instrumentation, and background collection. Framework hooks cover requests and tasks, callable wrappers cover outbound operations, and background threads handle transport/configuration. The [implementation overview](https://www.elastic.co/docs/reference/apm/agents/python/how-agent-works) explains those boundaries, including per-worker-process thread ownership.

### 11. [inspectIT/inspectit-ocelot](https://github.com/inspectIT/inspectit-ocelot)

**Language/role:** Java; configurable tracing agent and configuration-server monorepo. Focus on agent instrumentation and propagation.

Study instrumentation that can change while an application is running. Its rule-driven model offers a different design from agents that instrument every relevant class only during loading.

- **C1:** Context data can propagate upward or downward through calls, locally across threads, or globally across JVM boundaries. The [propagation model](https://inspectit.github.io/inspectit-ocelot/docs/instrumentation/data-propagation) makes direction and scope explicit, exposing difficult interactions between nested execution and configurable data collection.
- **C3:** By default, loaded classes are analyzed and retransformed asynchronously in batches. Injected action classes may become uncollectable orphans, so the agent attempts reuse. The [instrumentation-process design](https://inspectit.github.io/inspectit-ocelot/docs/instrumentation/process) connects batch pacing and class recycling to CPU and class-loader resource constraints, and documents the synchronous alternative's tradeoffs.

## eBPF and network-derived tracing

### 12. [open-telemetry/opentelemetry-ebpf-instrumentation](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation)

**Language/role:** Go and C/eBPF; OpenTelemetry eBPF Instrumentation, or OBI.

Study how process discovery, executable analysis, probes, metadata enrichment, and trace export fit together. The inspected repository marks OBI as **in development**, with breaking changes possible between v0 minor releases.

- **C1:** Propagation must respect an application's existing `traceparent`, distinguish network-level from Go library-level injection, and account for kernel permissions and runtime-specific context association. The [distributed-tracing documentation](https://opentelemetry.io/docs/zero-code/obi/distributed-traces/) also states limitations around encrypted traffic, proxies, and pre-existing connections.
- **C2:** The [pipeline map](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/main/devdocs/pipeline-map.md) separates discovery/attachment from span reading, enrichment, filtering, and export. Optional stages and a proposed privilege split make the architecture a useful study in composing host-level instrumentation with telemetry pipelines.

OBI is the upstream selected for the Beyla lineage; Beyla is not counted separately below.

### 13. [open-telemetry/opentelemetry-go-instrumentation](https://github.com/open-telemetry/opentelemetry-go-instrumentation)

**Language/role:** Go and C/eBPF; automatic tracing of Go library calls.

This project is distinct from both the Go SDK and OBI's broader host instrumentation. Study its treatment of compiled Go executables, including binaries stripped of conventional debugging information. The repository labels it **work in progress**.

- **C1:** Probe attachment depends on locating functions and supplying the correct struct-field offsets for the target Go build and dependencies. The [technical design](https://github.com/open-telemetry/opentelemetry-go-instrumentation/blob/main/docs/how-it-works.md) follows process analysis through symbol discovery, offset injection, map setup, and event decoding.
- **C2:** Analyzer, Manager, Controller, and per-library Probe objects divide discovery, orchestration, extraction, and standard SDK export. Probe manifests expose symbols and fields in a reusable form instead of embedding every integration into one attachment routine. These interfaces and the event path are described in the same design document.

### 14. [deepflowio/deepflow](https://github.com/deepflowio/deepflow)

**Language/role:** Rust/C agent and Go server; network/eBPF collection and distributed-trace correlation.

Focus on the agent's protocol-log machinery and the agent/server boundary. This is a useful alternative to systems that obtain every span from an application SDK.

- **C1:** The [HTTP protocol implementation](https://raw.githubusercontent.com/deepflowio/deepflow/main/agent/src/flow_generator/protocol_logs/http.rs) handles stream IDs, request/response completion and merging, Go HTTP/2 uprobe records, and priority-aware extraction of trace IDs, span IDs, and request IDs. Those mechanisms show the ambiguity and state reconciliation involved in turning observations into correlated operations.
- **C2:** HTTP records implement shared protocol-information and log-attribute interfaces, allowing common downstream handling of protocol-specific data. The [repository architecture](https://github.com/deepflowio/deepflow#software-architecture) separately assigns collection to per-host agents and management, enrichment, ingestion, and querying to servers; the project also exposes protocol-extension mechanisms.

The study target is the public Community implementation. Product documentation also describes Enterprise features, so it should not be assumed that every advertised capability lives in this repository. No headline performance multiplier is adopted here.

## Instrumentation libraries and language SDKs

### 15. [openzipkin/brave](https://github.com/openzipkin/brave)

**Language/role:** Java; distributed-tracing library, propagation, context integration, and client/server instrumentations.

Study a compact tracing core with unusually explicit distinctions between span lifetime, current scope, sampling state, and propagation formats.

- **C1:** Closing a scope restores context but does not finish its span. Joining an incoming span can share its ID or create a new child depending on the propagation protocol; reporters may require shared-ID behavior to be disabled. The [core library guide](https://github.com/openzipkin/brave/tree/master/brave) explains these causality and lifecycle subtleties.
- **C2:** `SpanCustomizer`, context-scope decorators, propagation factories, baggage configuration, and sampling functions offer independently reusable extension points. The core guide demonstrates their composition; the [compatibility policy](https://github.com/openzipkin/brave#version-compatibility-policy) explains dependency isolation and testing against multiple integrated-library versions.

### 16. [kamon-io/Kamon](https://github.com/kamon-io/Kamon)

**Language/role:** Scala and Java; JVM instrumentation, distributed tracing, and context propagation.

Focus on core context/tracing and the instrumentation/reporter modules, particularly propagation across asynchronous JVM frameworks and actor-oriented communication.

- **C1:** Immutable request contexts still require correctly bounded thread-local scopes. Closing a scope restores the previous context; failing to close it can contaminate unrelated requests when threads are reused. The [context design](https://kamon.io/docs/latest/core/context/) explains this stack-like behavior and why one request's context may need activation on several threads.
- **C2:** Typed context keys and configurable codecs separate stored state from transport. HTTP-header and binary codecs support different communication styles, including remote actors and message brokers. The same guide defines the custom-codec contract and how decoding extends an existing context.

### 17. [open-telemetry/opentelemetry-go](https://github.com/open-telemetry/opentelemetry-go)

**Language/role:** Go; tracing API, SDK, propagation, and exporters. Focus on `sdk/trace`.

Study an in-process span-export pipeline where application goroutines and a background processor have different latency and shutdown obligations.

- **C1:** The [batch span processor](https://raw.githubusercontent.com/open-telemetry/opentelemetry-go/main/sdk/trace/batch_span_processor.go) coordinates producer calls, atomic stopped state, one-time shutdown, queue draining, timers, and export cancellation. It refuses new spans after shutdown and must synchronize access to its export batch.
- **C3:** A bounded channel, maximum batch size, export timeout, and timer-driven batching make its resource budget explicit. Queue-full behavior can drop spans or block producers; the source warns that choosing blocking changes application performance. This is a concrete study of observability overhead versus data retention.

The repository marks tracing stable; other repositories provide much of the framework-specific Go instrumentation.

### 18. [open-telemetry/opentelemetry-js](https://github.com/open-telemetry/opentelemetry-js)

**Language/role:** TypeScript/JavaScript; Node/browser APIs, SDKs, context managers, and exporters.

Study how one tracing API accommodates different execution environments. The context manager is especially useful for understanding why asynchronous causality is more than storing a global current span.

- **C1:** The Node context manager associates state with an asynchronous execution chain. Imperative attachment returns a disposable token that restores prior state; omitted restoration can leak context into unrelated instrumentation. The [async-hooks context-manager guide](https://github.com/open-telemetry/opentelemetry-js/blob/main/packages/opentelemetry-context-async-hooks/README.md) explains this contract.
- **C2:** The repository separates public instrumentation APIs from SDK implementations and supplies interchangeable context/propagation machinery. Its [library-author and runtime guidance](https://github.com/open-telemetry/opentelemetry-js#library-author) explains the API boundary, while the context-manager guide points to different browser implementations.

The inspected README explicitly calls browser client instrumentation experimental; Node and browser behavior should not be assumed identical.

### 19. [open-telemetry/opentelemetry-cpp](https://github.com/open-telemetry/opentelemetry-cpp)

**Language/role:** C++; telemetry API/SDK, focusing on trace processing and export.

The batch processor is a valuable small entry into native ownership, atomics, condition variables, and background export lifecycles.

- **C1:** Its [implementation](https://raw.githubusercontent.com/open-telemetry/opentelemetry-cpp/main/sdk/src/trace/batch_span_processor.cc) delays launching the worker until constructor initialization is complete. Force-flush uses sequence counters and synchronization state to coordinate callers with the worker, while ownership of completed records moves into the processor.
- **C3:** A bounded circular buffer drops excess spans and triggers early export when sufficiently full. Worker notification deliberately avoids a lock on the span-ending path; the source explains that a missed notification is recovered by a later notification or scheduled wakeup. This exposes a specific contention/latency tradeoff rather than a generic speed claim.

### 20. [open-telemetry/opentelemetry-erlang](https://github.com/open-telemetry/opentelemetry-erlang)

**Language/role:** Erlang with Elixir APIs; BEAM tracing API, SDK, and OTLP export applications.

Study telemetry in an OTP supervision environment rather than translating a thread-based SDK literally. The repository separates the optional SDK from the no-op-capable API and documents startup ordering and application-failure isolation.

- **C1:** The [batch processor source](https://raw.githubusercontent.com/open-telemetry/opentelemetry-erlang/main/apps/opentelemetry/src/otel_batch_processor.erl) is a `gen_statem` coordinating ETS buffers, exporter processes, timeouts, and table handoff. It explicitly handles invalid spans, unavailable buffers, absent exporters, and exports that run too long.
- **C3:** Producers store finished spans in ETS while timed or size-triggered batch export controls transport overhead. Two table slots and a separate export runner make the buffering/export boundary visible in the source.
- **C4:** The [2023–2025 changelog](https://github.com/open-telemetry/opentelemetry-erlang/blob/main/CHANGELOG.md) records OTP compatibility accommodations and fixes for atom/persistent-term leaks, queue sizing, runner termination, and attribute representation. This supports sustained complexity management, beyond the project's creation date.

### 21. [open-telemetry/opentelemetry-rust](https://github.com/open-telemetry/opentelemetry-rust)

**Language/role:** Rust; API, SDK, propagators, and exporters. Focus on the trace SDK and OTLP integration.

Study the boundary between synchronous SDK lifecycle methods and asynchronous runtimes. The inspected repository marks trace API, SDK, and OTLP exporter **beta**, independently of other signal statuses.

- **C1:** The [batch processor documentation](https://docs.rs/opentelemetry_sdk/latest/opentelemetry_sdk/trace/struct.BatchSpanProcessor.html) warns that blocking shutdown on Tokio's current-thread runtime can deadlock. Exporter-client choices also constrain which runtime/processor combinations work; these are concrete lifecycle and dependency-composition hazards.
- **C3:** A dedicated background thread exports bounded batches on size or time thresholds, with explicit force-flush and shutdown behavior. Queue capacity, batch size, and schedule delay make the throughput and buffering tradeoffs directly inspectable in the same API documentation.

### 22. [fast/fastrace](https://github.com/fast/fastrace)

**Language/role:** Rust; tracing library and background collection with OpenTelemetry reporting support.

Study a design that deliberately offers different span mechanisms for general asynchronous work and tightly bounded local execution. This is the successor selected for the minitrace lineage.

- **C1:** `LocalSpan` requires a single-thread execution region and must not span an `.await` point. Root-span drop controls trace reporting, and final flushing matters for termination. The [library documentation](https://docs.rs/fastrace/latest/fastrace/) explains these constraints and the future wrapper used for async work.
- **C3:** The [LocalSpan API](https://docs.rs/fastrace/latest/fastrace/local/struct.LocalSpan.html) specializes span bookkeeping for a single thread and makes child creation a no-op without an active local parent. Reporting runs on a background collector thread, and compile-time enablement supports disabling instrumentation, as described in the library documentation. The project publishes headline speed comparisons, but this selection relies on architecture rather than treating those numbers as generally applicable.

## Search coverage, exclusions, and limits

Discovery used more than six distinct live search formulations, followed by repository-page verification and reading separate primary implementation or design material for every retained repository. Search angles included:

- Collector architecture and trace-aware tail sampling, including Refinery and OpenTelemetry.
- JVM bytecode agents and plugin systems, including SkyWalking, Pinpoint, and inspectIT Ocelot.
- CLR profiler architecture and managed instrumentation.
- Python framework hooks, callable wrapping, and asynchronous instrumentation.
- eBPF automatic instrumentation, process analysis, Beyla/OBI, and DeepFlow.
- Erlang/Elixir batching and supervision; Rust SDKs and local-span implementations.
- Scala/JVM context propagation, actors, and transport codecs.
- JavaScript asynchronous context managers, C++ export synchronization, and additional Ruby/PHP/Haskell discovery queries.

Later queries increasingly returned existing candidates, integration examples, wrappers, or adjacent observability projects. The selection stops at 22 substantive repositories rather than adding every language binding. Ruby, PHP, and Haskell received discovery searches but no retained entry met the same depth of primary-source inspection in this pass; coverage is therefore broad, not exhaustive.

Two lineage exclusions avoid double counting. [Beyla's repository](https://github.com/grafana/beyla) directs core development upstream to OBI and describes vendoring that implementation. [minitrace's repository](https://github.com/tikv/minitrace-rust) explicitly says development continues as fastrace and that minitrace will no longer be maintained. The old names are historical context, not additional recommendations. Generic logging/profiling tools, pure specifications, tutorials, awesome-lists, deployment-only bundles, and storage/UI-centered projects without an inspected collection subsystem were also excluded.

Repository pages were opened to verify identity and category fit; source files, technical guides, or substantive subsystem documentation supplied additional evidence. Public source was read without cloning or executing candidate code. Some general DeepFlow documentation endpoints failed to return readable content, so its detailed claims here are limited to the public protocol implementation and repository architecture. Moving branch and `latest` documentation links can change; the cited observations describe this research pass. Maintenance activity is not inferred merely from stars, commit counts, or a recent crawl, and C4 is assigned only where the inspected history supports it. These are engineering study selections, not an assertion that every component or deployment mode is equally robust.
