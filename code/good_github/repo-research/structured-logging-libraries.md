# Structured logging libraries

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories whose libraries preserve log events as fields, records, templates, or structured reports. It includes standalone loggers, substantial structured-output components, and clearly identified standard-library subsystems. The emphasis is on code an experienced engineer can study: event representation, context propagation, extension contracts, serialization, and behavior under concurrency or overload. Collectors, storage engines, and dashboards are outside scope. Repository headings link to verified GitHub pages; the accompanying primary-source links are reading entry points and evidence for the specific claims.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure behavior.
- **C2 — Abstractions:** substantial reusable interfaces or composition mechanisms that serve multiple use cases.
- **C3 — Performance architecture:** explicit resource or throughput constraints addressed through understandable design choices.
- **C4 — Evolution:** documented change over years together with compatibility, regression fixes, testing, or complexity management.

The criteria below are evidence-based selection judgments, not an audit or a claim that every component is exemplary. Performance discussion concerns mechanisms and tradeoffs, not independently reproduced benchmark results.

## Go: typed events and small extension contracts

### [uber-go/zap](https://github.com/uber-go/zap)

**Go — typed structured logger and extensible encoding core.** Study the boundary between a convenient logging API and the smaller core that decides whether, where, and how an event is written.

- **C1 / C2:** `zapcore.Core` separates field attachment, admission through `Check`, writing, and synchronization. `Write` must honor the earlier admission decision instead of checking it again; tee cores and encoders make the same event machinery reusable across outputs. These are useful contracts for reasoning about custom cores. See the [zapcore API](https://pkg.go.dev/go.uber.org/zap/zapcore).
- **C3:** Typed fields and specialized encoding reduce general-purpose formatting work. The sampler deliberately trades exact counting for a fast admission path; its documentation acknowledges possible over- or undersampling under load. See the [repository design explanation](https://github.com/uber-go/zap) and [core API](https://pkg.go.dev/go.uber.org/zap/zapcore).
- **C4:** The [changelog](https://raw.githubusercontent.com/uber-go/zap/master/CHANGELOG.md) records the 2017 stable API commitment and subsequent work including nil-object handling and a `WithLazy` race fix in 2025. This supports sustained compatibility and correctness work, beyond an old creation date.

### [rs/zerolog](https://github.com/rs/zerolog)

**Go — fluent structured-event construction with pooled buffers.** A compact place to study how allocation control changes the lifetime rules of a public API.

- **C1:** Events return to a pool when finalized and must not be reused afterward. Context mutation has a separate concurrency rule: `UpdateContext` is not safe for simultaneous use, while child loggers can be built with `With`. Duplicate field names are not automatically deduplicated, making downstream interpretation part of the application contract. See the [API documentation](https://pkg.go.dev/github.com/rs/zerolog).
- **C2 / C3:** Typed object and array marshaling interfaces coexist with hooks, sampling, and contextual children. The [event implementation](https://raw.githubusercontent.com/rs/zerolog/master/event.go) resets contextual state on return to the pool and refuses to retain oversized buffers, explicitly bounding the memory cost of pooled entries.

### [golang/go](https://github.com/golang/go)

**Go — the `log/slog` standard-library subsystem. Official GitHub mirror:** the repository identifies `go.googlesource.com/go` as the canonical development repository. Only `log/slog` is evaluated here, not the whole language implementation.

- **C1:** The [Handler contract and implementation](https://go.dev/src/log/slog/handler.go) require handlers to cope with concurrent method calls and define normalization rules for attributes. A canceled logging context must not prevent handling: cancellation itself can be what the log needs to explain.
- **C2 / C3:** `Handler` supports interchangeable backends, derived handlers with attributes or groups, and early admission through `Enabled`. That early check avoids processing arguments for disabled events. Study how a small public interface carries both semantic rules and opportunities to avoid work. The same [source entry point](https://go.dev/src/log/slog/handler.go) documents these responsibilities alongside their implementation.

### [go-kit/log](https://github.com/go-kit/log)

**Go — minimal key/value logging interface and decorators.** Useful for comparing a deliberately small abstraction with richer event-builder APIs.

- **C2:** `Logger.Log(keyvals ...interface{}) error` supports contextual decorators and deferred values without prescribing one encoding or destination. The package documents how errors propagate through wrappers rather than disappearing inside a universal policy. Start with the [package API and design documentation](https://pkg.go.dev/github.com/go-kit/log).
- **C1 / C3:** `NewSyncWriter` protects individual writes, whereas `NewSyncLogger` protects an entire logging operation. The former is sufficient only when an event is emitted in one write; the latter accommodates implementations that issue several. The [synchronization API](https://pkg.go.dev/github.com/go-kit/log) makes the atomicity-versus-lock-duration tradeoff unusually explicit.

## Rust: structured context and composable consumers

### [tokio-rs/tracing](https://github.com/tokio-rs/tracing)

**Rust — structured events and spans with subscriber-driven processing.** This monorepo counts once, including its core, subscriber, and appender components. Its structured event logging is relevant here even though tracing also serves broader diagnostic purposes.

- **C1:** Entering a span, exiting it, and closing its last handle are different lifecycle events. Holding an entered-span guard across an `await` can incorrectly attribute other tasks' events to that span. The [span documentation](https://docs.rs/tracing/latest/tracing/span/index.html) explains this asynchronous-context failure mode and the intended instrumentation model.
- **C2:** Callsite metadata, typed fields, events, spans, and subscribers separate application instrumentation from collection and presentation. The [repository's component guide](https://github.com/tokio-rs/tracing) describes formatted logging and compatibility with the `log` ecosystem. Study the division between event production and layered consumers rather than treating spans as merely another string field.

### [slog-rs/slog](https://github.com/slog-rs/slog)

**Rust — structured logger contexts and composable drains.** The project README explicitly encourages considering `tracing`; retain this as a useful alternative design with a small stable core, without interpreting that recommendation as an archival notice.

- **C2:** `Drain` carries associated success and error types and accepts both the immediate record and inherited key/value context. Filtering, mapping errors, and combining destinations can therefore be implemented as ordinary drain composition. See the [Drain API](https://docs.rs/slog/latest/slog/trait.Drain.html).
- **C1:** Error-handling adapters distinguish ignoring errors from turning them into panics. The flush contract distinguishes records already queued at invocation from later concurrent submissions, avoiding an obligation to wait forever while producers remain active. The [same API documentation](https://docs.rs/slog/latest/slog/trait.Drain.html) is a substantive guide to these boundary conditions.

## JavaScript and TypeScript: stream pipelines and runtime boundaries

### [pinojs/pino](https://github.com/pinojs/pino)

**JavaScript — structured JSON logging with worker-based transports.** Study the split between producing a log event and performing potentially expensive delivery work.

- **C3 / C2:** Transports can run in worker threads and expose writable-stream interfaces. This moves transformation and transmission away from the application's event loop while keeping destinations replaceable. Worker options must obey the structured-clone boundary. The [transport architecture guide](https://raw.githubusercontent.com/pinojs/pino/main/docs/transports.md) explains the implementation model and its configuration consequences.
- **C1:** Admission at the logger and routing among transport targets are distinct stages; multi-target routing depends on the numeric level remaining available. Transport closure must finish the destination's pending work before signaling completion, or records can be lost. Study the closure and backpressure examples in the [transport guide](https://raw.githubusercontent.com/pinojs/pino/main/docs/transports.md).

### [winstonjs/winston](https://github.com/winstonjs/winston)

**JavaScript — object-mode logging pipeline with formats and multiple transports.** Its central logger is a useful example of applying Node stream semantics to mutable structured records.

- **C2:** Records pass through a format pipeline before reaching independent transports; symbolic level metadata provides internal routing information alongside user-facing fields. The [logger source](https://raw.githubusercontent.com/winstonjs/winston/master/lib/winston/logger.js) also shows adaptation of legacy transports and validation of writable object-mode destinations.
- **C1:** `_transform` uses a `finally` path to complete the stream callback even if a formatter throws, and `_final` coordinates completion of transports. These details expose how extension failures and shutdown interact with stream progress. Start with those methods in the [same implementation](https://raw.githubusercontent.com/winstonjs/winston/master/lib/winston/logger.js), rather than only reading configuration examples.

### [trentm/node-bunyan](https://github.com/trentm/node-bunyan)

**JavaScript — JSON records, serializers, child context, and per-stream filtering.** Included particularly as a historical design reference. Its stable 1.x and 2.x beta development lines should be checked separately; this report does not infer a current maintenance cadence from repository availability.

- **C1:** The [logger implementation](https://raw.githubusercontent.com/trentm/node-bunyan/master/lib/bunyan.js) takes care not to mutate field objects retained by raw streams and converts serializer exceptions into diagnostic values. These are concrete examples of defending the logging path against extension code and shared-object aliasing.
- **C2 / C3:** The same implementation supports contextual child loggers and both object-consuming and serialized streams. It serializes once when serialized output is needed, while allowing raw consumers to receive the record itself. This is a small but instructive fan-out optimization.

Additional historical entry point: the [1.x changelog](https://raw.githubusercontent.com/trentm/node-bunyan/1.x/CHANGES.md) documents testing-tool changes made while preserving old Node compatibility. Read version history before adopting examples from a different branch.

### [dahlia/logtape](https://github.com/dahlia/logtape)

**TypeScript — structured logging across JavaScript runtimes.** Its documentation makes the boundary between a message and retained properties especially clear: logging templates and ordinary JavaScript string interpolation do not preserve the same information. See the [structured-logging guide](https://logtape.org/manual/struct).

- **C2:** Log records, sinks, and formatters are separate concepts, allowing structured properties to survive changes in presentation or destination. The [sink guide](https://logtape.org/manual/sinks) explains synchronous sinks and adapters for asynchronous outputs.
- **C1 / C3:** Asynchronous sink adaptation serializes pending work within its originating context and handles failures without poisoning the promise chain. Drain waits concern accepted work, not a universal durability guarantee. Queues are unbounded by default but support size and overflow policies; the currently executing record is excluded from the queued count. These details in the [sink guide](https://logtape.org/manual/sinks) make it a useful study of precise asynchronous API semantics.

## Python, PHP, and Ruby: extensible records and application lifecycles

### [hynek/structlog](https://github.com/hynek/structlog)

**Python — event dictionaries transformed by processor chains.** Study how a minimal data representation can support enrichment, filtering, rendering, and integration with another logging system.

- **C2 / C3:** Processors receive a logger, method name, and event dictionary; the last processor adapts the result to the wrapped logger's calling convention. Early filtering can avoid running the rest of the chain. The [processor guide](https://www.structlog.org/en/stable/processors.html) explains the dictionary-copy boundary, `DropEvent`, and supported final return shapes.
- **C1:** Context storage differs between threads, asynchronous tasks, and greenlets. Hybrid synchronous/asynchronous applications cannot assume context automatically crosses those boundaries. Clearing request context, merging it into events, and restoring nested bindings are explicit concerns in the [contextvars guide](https://www.structlog.org/en/stable/contextvars.html).

### [Delgan/loguru](https://github.com/Delgan/loguru)

**Python — configurable sinks, serialized records, and contextual enrichment.** A useful comparison with structlog: one convenient logger coordinates a broad set of sink and lifecycle behaviors.

- **C2:** Sinks may be files, callables, or coroutine functions; serialized output retains the record as structured data. `bind`, `contextualize`, and `patch` provide distinct ways to attach or transform fields. The [logger API](https://loguru.readthedocs.io/en/stable/api/logger.html) explains these interfaces and the context-local behavior of `contextualize`.
- **C1:** Completion has two stages: draining queued handlers and awaiting coroutine-sink work for the relevant event loop. Multiprocessing users must also arrange for child-process queued messages to be transmitted before exit. Study `complete()` in the [same API reference](https://loguru.readthedocs.io/en/stable/api/logger.html); merely returning from an application function is not equivalent to completing every sink.

### [Seldaek/monolog](https://github.com/Seldaek/monolog)

**PHP — structured records with handlers, processors, and formatters.** Particularly useful for understanding how logging designed for requests adapts to long-running workers.

- **C2 / C1:** Context and extra fields flow through replaceable processors and handlers. Resettable components let a worker clear buffered state between jobs, limiting memory accumulation and cross-job data leakage. The [usage guide](https://seldaek.github.io/monolog/doc/01-usage.html) describes the composition model and long-running-process reset protocol.
- **C4:** The [changelog](https://raw.githubusercontent.com/Seldaek/monolog/main/CHANGELOG.md) documents the 2022 transition from arrays to `LogRecord`, including compatibility support through `ArrayAccess`, and later fixes involving fibers, cyclic handling, sockets, and rotation. Entries through 2026 show continued management of compatibility and operational edge cases, rather than age alone.

### [reidmorrison/semantic_logger](https://github.com/reidmorrison/semantic_logger)

**Ruby — structured logging with asynchronous appenders.** Study the relationship between application-facing appenders, a processor, and queues that determine operational behavior under load.

- **C1:** The [asynchronous appender](https://raw.githubusercontent.com/reidmorrison/semantic_logger/master/lib/semantic_logger/appender/async.rb) distinguishes blocking from nonblocking overflow, tracks dropped records, and coordinates flush, close, retry, and reopening after a fork. The [processor](https://raw.githubusercontent.com/reidmorrison/semantic_logger/master/lib/semantic_logger/processor.rb) also avoids using the same logging system for its internal diagnostics, preventing recursive failure reporting.
- **C2 / C3:** An asynchronous wrapper can adapt different appenders while forwarding appropriate metadata operations directly. Size/time batching and worker-side delivery separate the calling thread's work from destination work. Follow the delegation and queue setup in the [async implementation](https://raw.githubusercontent.com/reidmorrison/semantic_logger/master/lib/semantic_logger/appender/async.rb).

## .NET and Java: message templates and serialization systems

### [serilog/serilog](https://github.com/serilog/serilog)

**C# — message-template capture into a sink-independent property model.** Study how values become durable event data before a sink chooses a text or JSON representation.

- **C2:** Scalars, sequences, dictionaries, and structures form a common value model; destructuring policies customize object capture separately from formatting. The [structured-data guide](https://github.com/serilog/serilog/wiki/Structured-Data) explains the distinction between destructuring and stringification and the constraints on custom transformations.
- **C1:** The [property converter](https://raw.githubusercontent.com/serilog/serilog/dev/src/Serilog/Capturing/PropertyValueConverter.cs) limits traversal depth, string length, and collection size. It also manages failures while reading properties and restricts dictionary-key conversion. This is substantive defensive serialization code: object graphs and user getters cannot be treated as harmless strings.

### [NLog/NLog](https://github.com/NLog/NLog)

**C# — logging framework with structured event properties, layouts, and targets.** The [structured-logging guide](https://github.com/NLog/NLog/wiki/How-to-use-structured-logging) demonstrates preservation of template parameters and their inclusion in JSON output.

- **C2:** Event properties, layouts, and targets let the same captured data support different output shapes and destinations; scoped properties extend the model beyond a single call. The structured-logging guide is the best entry into that separation.
- **C1 / C3:** The [asynchronous target wrapper](https://raw.githubusercontent.com/NLog/NLog/dev/src/NLog/Targets/Wrappers/AsyncTargetWrapper.cs) implements queue overflow policies, batching, and shutdown coordination. Its choice between locking and concurrent queues explicitly considers allocations and blocking behavior. Shutdown must also release writers waiting on a full queue, making lifecycle correctness inseparable from throughput design.

### [apache/logging-log4j2](https://github.com/apache/logging-log4j2)

**Java — Log4j 2, focusing on JSON Template Layout and its event resolvers.** The monorepo counts once; selection concerns the structured serialization subsystem rather than every Log4j component.

- **C2:** Templates compile into resolver machinery that maps log events into configurable schemas. Resolver plugins allow new field semantics without hardwiring one output format. The [JSON Template Layout manual](https://logging.apache.org/log4j/2.x/manual/json-template-layout.html) explains custom resolvers and standard schema examples.
- **C1 / C3:** The same manual discusses numeric counter overflow versus allocation with larger numeric representations, schema-type consequences of conversion policies, and exceptions to low-allocation operation. These are concrete examples of balancing JSON semantics, failure behavior, and garbage-collection pressure. Read the resolver and recycling sections rather than relying on an overall performance slogan.

### [logfellow/logstash-logback-encoder](https://github.com/logfellow/logstash-logback-encoder)

**Java — structured JSON encoders, providers, and asynchronous appenders for Logback.** This is a substantive output subsystem, not merely a generated adapter.

- **C2:** Composable JSON providers combine event fields, context, and structured arguments into different schemas. The [repository documentation](https://github.com/logfellow/logstash-logback-encoder) explains provider composition for logging and access events as well as reusable encoding buffers.
- **C1 / C3:** The [Disruptor appender implementation](https://raw.githubusercontent.com/logfellow/logstash-logback-encoder/main/src/main/java/net/logstash/logback/appender/AsyncDisruptorAppender.java) requires a positive power-of-two ring-buffer size, coordinates concurrent producers with a consumer, and implements timeout/drop behavior. Daemon-thread and shutdown choices affect whether queued records survive termination. Study the bounded-buffer invariants together with the documented overload options.

## Functional ecosystems: typed payloads, immutable events, and effect integration

### [7mind/izumi](https://github.com/7mind/izumi)

**Scala — the LogStage subsystem of the Izumi monorepo.** Counted once; the unrelated dependency-injection and utility subsystems are not part of this selection.

- **C2:** LogStage combines structured message capture with codecs, routing, text/JSON sinks, and effect-oriented logging interfaces. A strict logger can require explicit codecs instead of accepting fallback string conversion. The [LogStage architecture and API guide](https://izumi.7mind.io/logstage/) covers these alternatives and integration with effect types and ZIO context.
- **C3:** Macros extract the structure of interpolated messages at compile time, shifting work out of the runtime logging call. Typed codecs then control conversion of captured values. Study the macro-to-event-to-sink path described in the [guide](https://izumi.7mind.io/logstage/); this is an architectural performance argument, not a claim that all logging work is free.

### [taoensso/telemere](https://github.com/taoensso/telemere)

**Clojure/ClojureScript — structured signals with filters, transformations, and handlers.** Its generalized signal model includes logging while allowing other diagnostic events to use the same processing machinery.

- **C2 / C3:** Call-level and handler-level filtering, sampling, rate limits, and transformations compose around data-rich signals. A transform can discard an event before delivery. The [handler API](https://cljdoc.org/d/com.taoensso/telemere/1.4.0/api/taoensso.telemere) exposes these stages instead of hiding all policy inside an output writer.
- **C1:** Asynchronous handlers distinguish blocking, dropping newest, and dropping oldest work. Sequential handling requires a single worker; drain timeouts and backpressure/error callbacks define additional failure boundaries. Statistics are documented as non-atomic snapshots. The [same API reference](https://cljdoc.org/d/com.taoensso/telemere/1.4.0/api/taoensso.telemere) is valuable for studying explicit guarantees and deliberately weaker ones.

### [BrunoBonacci/mulog](https://github.com/BrunoBonacci/mulog)

**Clojure — μ/log, immutable structured events with asynchronous publishers.** The repository describes its core as feature-complete and limits further core changes; this is a declared project scope, not evidence that its publishing ecosystem is abandoned.

- **C1 / C3:** A bounded ring buffer accepts events using compare-and-set operations, and publisher-specific buffers separate delivery from event production. Because serialization occurs later, payloads must remain immutable. Overload can lose events rather than allow unlimited memory growth. These choices are explained in the [internals guide](https://cljdoc.org/d/com.brunobonacci/mulog/0.10.1/doc/%CE%BC-log-internals).
- **C2:** A publisher protocol abstracts downstream delivery. Successful publishing advances the buffer, while failed delivery can be retried in a later publishing cycle; serialized publisher execution constrains concurrency. Study the [publisher and buffer design](https://cljdoc.org/d/com.brunobonacci/mulog/0.10.1/doc/%CE%BC-log-internals) alongside the repository's structured-event and tracing examples.

### [Soostone/katip](https://github.com/Soostone/katip)

**Haskell — typed structured payloads and composable scribes.** Distinguishes event severity from the amount of payload detail each destination requests.

- **C2:** `LogItem` determines which fields survive at a chosen verbosity; a `Scribe` supplies acceptance, writing, and finalization behavior. Different scribes can retain different fields from the same payload. The [Core API](https://hackage-content.haskell.org/package/katip-0.8.8.4/docs/Katip-Core.html) explains this domain-oriented extension model.
- **C1 / C3:** The [Core implementation](https://raw.githubusercontent.com/Soostone/katip/master/katip/src/Katip/Core.hs) uses bounded transactional queues and per-scribe workers, drops when a queue cannot accept an item, and uses a termination message plus worker waiting during finalization. Scribe composition also has to preserve finalizer behavior when one action fails. This provides concrete material on combining typed interfaces with concurrent resource lifecycles.

## Native and runtime-integrated logging

### [apple/swift-log](https://github.com/apple/swift-log)

**Swift — structured metadata and a backend-neutral logging API.** Particularly useful for studying a facade whose backend must preserve the language's value-semantics expectations.

- **C1:** The [LogHandler protocol source](https://raw.githubusercontent.com/apple/swift-log/main/Sources/Logging/LogHandler.swift) requires independent metadata and log-level state when a logger is copied, with example checks demonstrating the contract. A backend that accidentally shares mutable state violates that behavior; explicit global overrides require their own synchronization strategy.
- **C2:** Backends implement a protocol rather than forcing applications to depend on a concrete writer. Metadata providers and compatibility bridges between logging method signatures extend the interface while preserving integration points. Study the protocol's comments and defaults in the [same source](https://raw.githubusercontent.com/apple/swift-log/main/Sources/Logging/LogHandler.swift), especially where forwarding methods could otherwise recurse.

### [odygrd/quill](https://github.com/odygrd/quill)

**C++ — asynchronous logging with structured/JSON output and custom argument codecs.** The repository documents structured logging support; its architecture is especially valuable for understanding deferred formatting without borrowing unsafe caller state.

- **C1:** Arguments are copied into a binary representation before background processing. Timestamp ordering uses a grace mechanism rather than an unconditional global-order guarantee; queue policies explicitly choose between blocking and dropping. The [architecture overview](https://quillcpp.readthedocs.io/en/latest/overview.html) explains lifetime, ordering, crash-loss, and lifecycle constraints.
- **C2 / C3:** Thread-local single-producer/single-consumer queues feed a backend that performs formatting and I/O. Custom codecs extend argument support, while queue configuration and preallocation tune resource use. Study the [frontend/backend design](https://quillcpp.readthedocs.io/en/latest/overview.html), including its limits, before interpreting latency-oriented benchmark claims.

### [erlang/otp](https://github.com/erlang/otp)

**Erlang — the Kernel application's Logger subsystem.** The OTP monorepo counts once. Relevant components are Logger's structured reports, metadata, filters, handlers, and overload protection, not the entire runtime.

- **C2:** Reports can be maps or key/value lists, with metadata attached at primary, process, and event levels. Filters and handler callbacks separate event policy from formatting and delivery. The [Logger architecture guide](https://www.erlang.org/doc/apps/kernel/logger_chapter.html) explains the pipeline and report-formatting callbacks.
- **C1 / C3:** Built-in handlers use synchronized, dropping, and flushing overload thresholds with ordering constraints. Dropping must also unblock synchronous callers; optional handler termination/restart protects against excessive memory use. Study the threshold invariants and escalation behavior in the [same guide](https://www.erlang.org/doc/apps/kernel/logger_chapter.html). This makes overload a defined state machine rather than an incidental queue failure.

## Coverage, search process, and limitations

Discovery used substantially more than six distinct live-search formulations. Search families included Go typed encoders and `slog` handler contracts; Rust spans, drains, and asynchronous context; JavaScript worker transports and object-mode streams; Python processors and contextual state; .NET message templates; Java JSON providers and ring buffers; Scala macros and effect integration; Clojure immutable events and publisher buffers; Haskell scribes and transactional queues; Swift metadata value semantics; C/C++ named fields and deferred formatting; and Ruby/PHP asynchronous appenders and processors. Later queries for smaller C/C++, Ruby, Java, and Clojure projects added μ/log but otherwise mostly returned already covered architectures, thin integrations, textual-only logging, or unrelated log-structured storage. This provided a practical diminishing-returns stopping point.

Each retained repository's GitHub page was opened, and at least one separate primary implementation or documentation source was read. Search-result snippets were used for discovery, not as the sole evidence for retention. Sources include actual handler and encoder implementations, API contracts, architectural guides, and selected changelogs. No candidate code was installed or executed, and no independent throughput, correctness, or security audit was performed.

The selection deliberately mixes established frameworks with smaller projects such as LogTape, Katip, Telemere, and μ/log. It includes logging facades only where the structured-data and backend contracts themselves provide substantive material. Logstash Logback Encoder is retained because it implements schema composition and asynchronous delivery, rather than merely forwarding another library's calls. Go's repository is identified as an official mirror. Bunyan is included for historical design study, while μ/log's stated core scope and slog's recommendation to consider tracing are preserved instead of being flattened into an unsupported claim of active development.

Collectors and backends such as Loki or Fluent Bit, awesome lists, tutorials, generated wrappers, and unrelated storage projects were excluded by scope. Elixir's Logger documentation was also investigated, but OTP's underlying Logger was selected to avoid counting the same overload machinery as an independent implementation. The list is not exhaustive: omission of another viable library is not a quality judgment, and stars were not used as evidence for any criterion.

Links to default branches and rolling documentation can change; versioned API references describe the versions in their URLs. Cross-project examples are not claimed to be compatible with every released version. **C4** is asserted only where the reviewed history supports both sustained evolution and concrete compatibility or correctness management. Other entries qualify through their documented abstractions, implementation constraints, or failure semantics; repository availability alone does not establish maintenance status.
