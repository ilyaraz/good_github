# Metrics instrumentation and aggregation libraries

Research date: **2026-10-09**

This report selects 25 GitHub repositories for studying application metric instrumentation, registries, collection and export, and the histogram or sketch structures used to aggregate measurements. It includes small focused libraries and substantial SDK subsystems. Monitoring databases, dashboards, tracing-only projects, and source-code quality metrics are outside the scope. Each repository was checked through its GitHub page and at least one separate primary implementation or documentation source. A monorepo appears once, with its relevant subsystem identified.

The criteria are engineering judgments grounded in the linked material, not certifications of every component:

- **C1 — Correctness:** nontrivial concurrency, numerical semantics, invariants, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or structures supporting different applications and integrations.
- **C3 — Performance and structure:** explicit resource or throughput constraints addressed through an understandable design.
- **C4 — Evolution:** sustained development accompanied by evidence of compatibility work, testing, or complexity management.

## JVM instrumentation and reporting systems

### [micrometer-metrics/micrometer](https://github.com/micrometer-metrics/micrometer)

**Language/role:** Java; dimensional instrumentation facade, meter implementations, and backend registries. The relevant monorepo components are `micrometer-core` and the registry implementations.

Study how one instrumentation API accommodates backends with different distribution and reporting semantics. The repository separates application-facing meters from backend-specific registries rather than making every backend look identical internally.

- **C2:** Registry implementations reuse the common meter model while adapting it to different monitoring systems. This is useful for studying where a portable facade ends and backend policy begins. See the [repository's module and registry overview](https://github.com/micrometer-metrics/micrometer).
- **C1:** Distribution summaries distinguish windowed maxima, windowed percentiles, and cumulative histogram behavior. Expiry and buffer length determine when old maxima disappear; a quiet window can reset the maximum. Prometheus histogram handling has different rollover requirements.
- **C3:** Bucket bounds, precision, and ring-buffer length explicitly affect storage. Scaling a constrained measurement domain can reduce the required histogram range. These are documented design choices, not a blanket claim of low overhead. Start with the [distribution-summary semantics and memory discussion](https://docs.micrometer.io/micrometer/reference/concepts/distribution-summaries.html).

### [dropwizard/metrics](https://github.com/dropwizard/metrics)

**Language/role:** Java; registries, meters, timers, reservoirs, and reporters.

An especially useful codebase for understanding why a percentile needs a defined sampling policy. Its reservoir alternatives expose different meanings of “recent” and different costs, while preserving a common histogram interface.

- **C2:** `MetricRegistry`, `MetricSet`, reservoirs, and reporters divide naming, grouping, sampling, and delivery into reusable components. Applications can replace a reservoir without redesigning the reporting layer.
- **C1:** Uniform, exponentially decaying, sliding-count, and sliding-time reservoirs answer different statistical questions. Timer durations use a monotonic time source. Treating these policies as interchangeable would change the meaning of the reported metric.
- **C3:** Sampling bounds retained observations, whereas a sliding time window can retain every observation in its interval. The array-based time-window implementation addresses allocation costs. The [core manual](https://www.dropwizard.io/projects/metrics/en/latest/manual/core/) explains these semantic and resource tradeoffs and is the best entry point before following the corresponding classes in the repository.

### [Netflix/spectator](https://github.com/Netflix/spectator)

**Language/role:** Java; application instrumentation API and registry implementations, including Atlas reporting.

Study the interaction between a small metric API and a production step-based publishing system. The API's dimensional identifiers and registry implementations are reusable independently of the Atlas-specific publishing policy.

- **C2:** The repository separates the common API from integrations such as Atlas and other instrumentation systems. Registry and identifier abstractions support reuse across application environments. See the [module overview](https://github.com/Netflix/spectator).
- **C1:** Atlas configuration documents relationships between publication steps and low-latency stream steps, including divisibility and upper-bound requirements. Polling and collection timing must respect step boundaries; these are semantic constraints, not simply scheduling preferences.
- **C3:** Request batching, configurable timeouts, and collection delays expose the costs and failure modes of transporting metrics. A separately configurable debug registry also makes self-observation an explicit concern. Read [AtlasConfig.java](https://raw.githubusercontent.com/Netflix/spectator/main/spectator-reg-atlas/src/main/java/com/netflix/spectator/atlas/AtlasConfig.java), especially its timing, batching, and debug-registry contracts.

### [kamon-io/Kamon](https://github.com/kamon-io/Kamon)

**Language/role:** Scala/Java; observability monorepo, here selected for its core metric instruments and reporter model.

The useful study target is the boundary between inexpensive measurement updates and periodic reporting. Its histogram design integrates HdrHistogram-style representations into a broader metric system; this is distinct from studying the underlying histogram library alone.

- **C2:** Counters, gauges, histograms, timers, and range samplers share a reporting lifecycle. Instruments are written by application code while reporters consume periodic snapshots. See the [core metrics guide](https://kamon.io/docs/latest/core/metrics/).
- **C1:** Interval counters and persistent gauges have different reset behavior. Histogram precision and the maximum trackable domain are configurable semantics that callers must understand.
- **C3:** The histogram representation combines linear and exponential bucket organization to represent a large measurement range in an array. Configured precision and range determine storage and approximation behavior. The [metric-instrument design discussion](https://kamon.io/docs/latest/core/advanced/metric-instruments/) explains the representation and its connection to the instrument API.

## Go registries, SDK aggregation, and buffered reporting

### [prometheus/client_golang](https://github.com/prometheus/client_golang)

**Language/role:** Go; Prometheus instrumentation, custom collectors, registries, and exposition support.

Study both descriptor contracts and the concurrency machinery beneath histograms. The public interfaces are compact, but collecting a changing application state without violating registry or histogram invariants is substantial work.

- **C2:** `Collector`, `Metric`, `Registerer`, and `Gatherer` separate instrumentation from registration and collection. The [package documentation](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus) explains why a collector's descriptor set must remain consistent and why `DescribeByCollect` is unsuitable for some dynamic collectors.
- **C1:** Histogram collection swaps hot and cold counters and waits for in-flight observations before exposing a completed snapshot. These synchronization rules are documented directly in [histogram.go](https://raw.githubusercontent.com/prometheus/client_golang/main/prometheus/histogram.go).
- **C3:** Native histograms explicitly manage bucket growth through policies such as reset, enlargement of the zero bucket, and reduced resolution. The same implementation makes the connection between resource limits and measurement fidelity visible.

### [open-telemetry/opentelemetry-go](https://github.com/open-telemetry/opentelemetry-go)

**Language/role:** Go; OpenTelemetry monorepo, here limited to the metric API, `sdk/metric`, and metric exporters.

The metric SDK is a strong study target for the difference between an instrumentation event and an exported aggregation. In particular, delta and cumulative temporality demand different state-management rules even when they begin with the same observations.

- **C2:** The repository separates the instrumentation API, SDK aggregation, metric data model, and exporter integration. This enables multiple instruments and export paths to use shared aggregation machinery. See the [repository's component overview](https://github.com/open-telemetry/opentelemetry-go).
- **C1:** Delta histogram collection rotates maps, waits for active writers, and clears consumed state; cumulative collection merges interval data while preserving lifetime aggregates. The distinction also affects whether inactive attribute sets remain in subsequent exports.
- **C3:** Hot and cold maps, atomic updates, and coordinated writer completion reduce contention between recording and collection. Cardinality-limiting map machinery makes the cost of attribute combinations explicit. Read the [histogram aggregator implementation](https://raw.githubusercontent.com/open-telemetry/opentelemetry-go/main/sdk/metric/internal/aggregate/histogram.go).

### [uber-go/tally](https://github.com/uber-go/tally)

**Language/role:** Go; scoped metrics with buffered reporting and interchangeable reporters.

Tally is useful for studying hierarchical names and tags together with the operational cost of reporting. Its design distinguishes reporter handles that can be cached from repeated lookup and construction work.

- **C2:** Scopes carry prefixes and tags; reporter interfaces separate metric use from backend delivery. Test scopes expose snapshots for application-level assertions. [scope.go](https://raw.githubusercontent.com/uber-go/tally/master/scope.go) shows how these concepts share a registry and lifecycle.
- **C3:** Counters, gauges, and histograms are buffered, while timer reporting follows a different path. Cached reporter handles, traversal slices, and separate locks for metric maps make the implementation's cost structure inspectable. It is not accurate to describe all instruments as uniformly buffered.
- **C1:** Value buckets and duration buckets have distinct types. Boundary generation handles arithmetic overflow and conversion limits, and sorting works on copies rather than unexpectedly mutating caller inputs. See [histogram.go](https://raw.githubusercontent.com/uber-go/tally/master/histogram.go).

### [VictoriaMetrics/metrics](https://github.com/VictoriaMetrics/metrics)

**Language/role:** Go; standalone instrumentation library, separate from the VictoriaMetrics database.

The selected implementation is its decimal-range histogram. It provides a compact example of making bucket layout, sparse allocation, and exposition conventions part of one understandable design.

- **C1:** Updates protect the sum and bucket state with a mutex, reject NaN and negative observations, and handle exact power-of-ten boundaries to preserve the intended inclusive upper-bound convention.
- **C3:** Bucket storage is allocated as ranges are used, range strings are cached, and exposition skips empty buckets. This connects allocation behavior to the observed distribution rather than allocating every possible bucket eagerly.

Read [histogram.go](https://raw.githubusercontent.com/VictoriaMetrics/metrics/master/histogram.go). Its `vmrange` output is a specific range representation; it should not be assumed to have the same representation as a conventional cumulative Prometheus `le` histogram. The [repository guide](https://github.com/VictoriaMetrics/metrics) places this implementation alongside counters, gauges, sets, and other supported instruments.

### [hashicorp/go-metrics](https://github.com/hashicorp/go-metrics)

**Language/role:** Go; backend-neutral metric sinks and an interval-based in-memory aggregator.

Study the sink abstraction together with the ownership rules of retained snapshots. The in-memory implementation is particularly useful because it exposes the difference between completed intervals and an interval still being updated.

- **C2:** StatsD, statsite, Prometheus, in-memory, fanout, and discard-style sinks support different delivery and embedding needs. The [repository overview](https://github.com/hashicorp/go-metrics) describes the sink layer and application API.
- **C1:** Interval maps use explicit locking; the current interval must be copied or accessed according to its synchronization rules. Completion signaling distinguishes finished intervals. Aggregate calculations also handle count-dependent cases such as sample variance.
- **C3:** Retention is organized as a configured number of intervals, making temporal storage policy explicit. This does **not** by itself bound label cardinality or every collection stored within an interval. Read [inmem.go](https://raw.githubusercontent.com/hashicorp/go-metrics/master/inmem.go). The canonical repository is now under HashiCorp rather than its former `armon` owner.

## Clients shaped by process models and runtime integration

### [prometheus/client_python](https://github.com/prometheus/client_python)

**Language/role:** Python; Prometheus instruments, collectors, exposition, and multiprocess aggregation.

The multiprocess subsystem is an unusually concrete example of how a language's deployment model changes metric semantics. A registry local to one interpreter is insufficient for a prefork web service.

- **C2:** Registries and collectors separate instrument registration from collection. Multiprocess collection adds selectable gauge aggregation policies, including live-process variants, to accommodate different meanings of a gauge.
- **C1:** Correctness depends on directory cleanup across application restarts, marking dead workers, and using a registry that avoids exporting both ordinary and multiprocess copies. Different gauge modes retain or discard contributions from dead processes differently.

Start with the [multiprocess guide](https://prometheus.github.io/client_python/multiprocess/), which explains the storage lifecycle and operational hooks. Its restrictions are part of the design: custom collectors, Info and Enum metrics, exemplars, and several other ordinary-client capabilities are unavailable in this mode. The [repository overview](https://github.com/prometheus/client_python) supplies the broader single-process collector model. This entry should not be read as saying every client feature composes with multiprocess operation.

### [prometheus/client_js](https://github.com/prometheus/client_js)

**Language/role:** JavaScript/TypeScript; Node.js instrumentation and aggregation across workers.

This is the canonical repository reached from the former `siimon/prom-client` location. The current project also documents its package transition to `@prometheus-io/client`; old tutorials may use the earlier name.

- **C2:** Registries, collection callbacks, and per-metric aggregation policies support ordinary applications and clustered processes through related interfaces.
- **C1:** Cluster collection tracks requests and responses, applies timeouts, and cleans pending state. Worker shutdown and flushing introduce additional requirements for preserving aggregate counters. Read [lib/cluster.js](https://raw.githubusercontent.com/prometheus/client_js/main/lib/cluster.js).
- **C4:** The [changelog](https://raw.githubusercontent.com/prometheus/client_js/main/CHANGELOG.md) records years of API and runtime changes: asynchronous collection, TypeScript compatibility, numerical rounding fixes, OpenMetrics support, and the later package and IPC transition. It also documents aggregation tests and shutdown fixes. This is concrete compatibility and complexity-management evidence, beyond the repository's age.

### [prometheus/client_ruby](https://github.com/prometheus/client_ruby)

**Language/role:** Ruby; Prometheus client with interchangeable metric data stores.

Study how metric APIs remain stable while their synchronization and persistence strategy changes. Its file-backed store is a substantive implementation for multiple Ruby processes rather than merely an HTTP adapter.

- **C2:** Synchronized, single-threaded, and direct-file stores support different runtime assumptions under the same instrument API. The [repository's data-store guide](https://github.com/prometheus/client_ruby) explains the selection boundary.
- **C1:** `DirectFileStore` combines an in-process monitor with file locking, refreshes process-specific handles after a fork, and constrains which operations make sense for particular aggregation modes. For example, most-recent aggregation is gauge-specific and does not support increment-style updates.
- **C3:** Fixed offsets and binary numeric updates allow individual values to change without reserializing an entire metric collection. The implementation makes the tradeoff between direct updates and collection work visible. Read [direct_file_store.rb](https://raw.githubusercontent.com/prometheus/client_ruby/main/lib/prometheus/client/data_stores/direct_file_store.rb).

### [prometheus-net/prometheus-net](https://github.com/prometheus-net/prometheus-net)

**Language/role:** C#/.NET; metrics, registries, exemplars, and application-framework integrations.

This repository combines a broad .NET integration surface with inspectable low-level histogram optimization. It is useful for tracing a framework-generated measurement through to its final bucket representation.

- **C2:** Registries and instruments are reused by ASP.NET, HTTP-client, gRPC, and `System.Diagnostics.Metrics` integrations. These adapters share the underlying metric model rather than each implementing a separate aggregator. See the [repository integration guide](https://github.com/prometheus-net/prometheus-net).
- **C3:** Histogram observation maintains noncumulative bucket counts, with cumulative values produced during serialization. The implementation conditionally uses AVX and aligned pinned bucket-boundary storage, while retaining a non-vectorized path. This provides a concrete performance study with a visible fallback design.

Read [Histogram.cs](https://raw.githubusercontent.com/prometheus-net/prometheus-net/master/Prometheus/Histogram.cs). It also handles NaN observations and uses thread-safe numeric components. Those individual atomic components should not be mistaken for a guarantee that every histogram field is captured in one atomic cross-field snapshot.

### [PromPHP/prometheus_client_php](https://github.com/PromPHP/prometheus_client_php)

**Language/role:** PHP; Prometheus instrumentation with shared-storage adapters for stateless request workers.

The distinctive problem is preserving metric state across requests and workers while keeping updates and scrapes affordable. The APCng design is particularly valuable because it explains a storage redesign and its remaining limitations.

- **C2:** Collectors and rendering are separated from Redis, Predis, APC/APCng, and in-memory storage. The [repository usage and adapter documentation](https://github.com/PromPHP/prometheus_client_php) shows the same metric API serving different deployment arrangements.
- **C3:** APCng avoids repeated full-keyspace discovery by caching metadata and deriving lookup keys. Its design shifts costs between first-time metric creation, updates, and collection, rather than claiming every operation becomes free. The [APCng design note](https://raw.githubusercontent.com/PromPHP/prometheus_client_php/main/README.APCng.md) explains the key organization.

That note also identifies a significant limitation: summary observations can create many short-lived keys, with associated memory churn and fragmentation. This is a useful boundary case when comparing exact retained observations with histogram or sketch aggregation.

## Rust and native instrumentation cores

### [metrics-rs/metrics](https://github.com/metrics-rs/metrics)

**Language/role:** Rust; instrumentation facade, reusable utilities, and exporters in one workspace.

Study the distinction between a metric handle and the policy used to aggregate it. Application libraries emit measurements through the facade; an application's recorder determines their storage and export behavior.

- **C2:** The `Recorder` interface decouples instrumentation macros and handles from backend implementations. A histogram event can feed a bucketed histogram or another distribution representation chosen by the recorder; the facade does not prescribe one universal aggregation.
- **C3:** The unconfigured path minimizes work, and key strings distinguish static storage from owned values to avoid unnecessary allocation. These choices connect instrumentation ergonomics to costs paid on frequently executed paths.
- **C1:** Global recorder initialization and metric-key identity have observable consequences: measurements before recorder installation may be lost, and label ordering affects key equality. These contracts matter when libraries and applications share instrumentation.

The [metrics API documentation](https://docs.rs/metrics/latest/metrics/) covers these architectural boundaries. The [workspace overview](https://github.com/metrics-rs/metrics) identifies the companion utility and exporter crates; they count as one repository here.

### [prometheus/client_rust](https://github.com/prometheus/client_rust)

**Language/role:** Rust; typed Prometheus/OpenMetrics metric families and encoding.

The central study target is a metric family parameterized by its label set, instrument, and constructor. It makes both allocation policy and lock ownership visible through the API.

- **C2:** `Family<S, M, C>` supports structured label types and custom metric construction, including histogram families with chosen boundaries. Enum and struct labels can be represented directly rather than assembled as arbitrary string maps.
- **C1:** Borrowed access returns a mapped read-lock guard. The documentation explicitly warns that retaining guards while accessing more family members can deadlock; obtaining an owned clone changes that lifetime relationship.
- **C3:** Typed labels can avoid unnecessary string allocation, while borrowed-versus-owned metric access exposes a concrete cloning and synchronization tradeoff.

Read the [Family API and locking examples](https://docs.rs/prometheus-client/latest/prometheus_client/metrics/family/struct.Family.html). The [repository documentation](https://github.com/prometheus/client_rust) also lists specification-compliance gaps; the type-driven design should not be interpreted as complete implementation of every specification requirement.

### [jupp0r/prometheus-cpp](https://github.com/jupp0r/prometheus-cpp)

**Language/role:** C++; Prometheus metric families, registries, collection, and pull/push integration.

This is a useful comparison with clients that use atomics or multi-buffer histogram collection: its histogram has a direct mutex-based coherence model and keeps the numerical representation straightforward.

- **C1:** Bucket boundaries must be strictly ordered. Observation and collection take the same mutex, making counts and sum part of a coherent protected snapshot. Batch observation checks the expected bucket-vector shape.
- **C3:** Each observation updates one internal bucket; collection constructs cumulative counts. Boundary lookup uses binary search. These choices move work between the recording path and the less frequent collection path. See [core/src/histogram.cc](https://raw.githubusercontent.com/jupp0r/prometheus-cpp/master/core/src/histogram.cc).
- **C2:** `Family<T>`, registries, and `Collectable` separate metric ownership from HTTP exposition and gateway delivery. The [repository examples](https://github.com/jupp0r/prometheus-cpp) show handle lifetime and caching, useful topics when embedding instrumentation in long-running C++ services.

### [fluent/cmetrics](https://github.com/fluent/cmetrics)

**Language/role:** C; embeddable metric contexts, aggregation, and multiple wire-format encoders and decoders.

CMetrics is broader than a text formatter: it maintains a common in-memory representation through which metrics from different protocols can be manipulated and combined.

- **C2:** The context model supports counters, gauges, histograms, exponential histograms, summaries, and multiple encoding paths, including OTLP and Prometheus-related formats. The [repository's data-model and codec overview](https://github.com/fluent/cmetrics) is the starting point. Timestamp preservation varies with the destination format, so translation is not semantically invisible.
- **C1:** Exponential-histogram combination must align positive and negative bucket offsets and respect scale and zero-threshold compatibility. The concatenation/aggregation implementation checks incompatibilities and handles allocation failures while managing partially constructed state.

Read [src/cmt_cat.c](https://raw.githubusercontent.com/fluent/cmetrics/master/src/cmt_cat.c), particularly the metric-map matching and exponential-histogram paths. These routines are useful examples of defending aggregation invariants at a protocol boundary, where similarly named measurements are not automatically safe to merge.

## BEAM and OCaml instrumentation abstractions

### [beam-telemetry/telemetry_metrics](https://github.com/beam-telemetry/telemetry_metrics)

**Language/role:** Elixir; declarative metric definitions derived from Telemetry events.

This library supplies the definition layer; reporters perform storage and aggregation. That separation makes it valuable for studying reusable instrumentation without tying event producers to one collector implementation.

- **C2:** Definitions specify event names, measurement extraction, tag projection, filtering, and unit conversion. Counters, sums, last values, distributions, and summaries share the declarative model. Read the [Telemetry.Metrics API guide](https://telemetry-metrics.hexdocs.pm/Telemetry.Metrics.html).
- **C4:** The [release history](https://hex.pm/packages/telemetry_metrics/versions) spans releases from 2019 onward. More importantly, the [changelog](https://raw.githubusercontent.com/beam-telemetry/telemetry_metrics/main/CHANGELOG.md) documents Telemetry-version compatibility, missing-value and unit-conversion fixes, stabilization of the API, and later changes to tag projection. This is evidence of maintaining a shared contract across reporters and callers over time.

Use the API guide and changelog as the two main reading entry points. The existence of a distribution definition does not establish that every reporter implements the same storage or approximation policy.

### [rkallos/peep](https://github.com/rkallos/peep)

**Language/role:** Elixir; Telemetry.Metrics reporter with Prometheus and StatsD output.

Peep demonstrates a different BEAM architecture from sending every observation through a central reporter process. It also exposes the distinction between local aggregation and packet-oriented export.

- **C3:** Event handlers update aggregation state directly using atomics with ETS-based lookup. Histograms are aggregated as events arrive rather than retaining a raw batch. StatsD output packs updates into bounded packets and can encode aggregated counts. The [Peep design and configuration documentation](https://peep.hexdocs.pm/Peep.html) explains these decisions.
- **C2:** It consumes the shared Telemetry.Metrics definitions and provides output and storage configuration, letting applications reuse event instrumentation across reporting arrangements.
- **C1:** Startup and termination coordinate handler attachment with storage lifecycle. The implementation also handles stray network replies that could otherwise terminate the reporter. See the [v5.0.1 reporter implementation](https://raw.githubusercontent.com/rkallos/peep/v5.0.1/lib/peep.ex).

The inspected implementation does not support every Telemetry.Metrics type: summaries are excluded. Do not infer support merely from compatibility with the definition library.

### [Feuerlabs/exometer_core](https://github.com/Feuerlabs/exometer_core)

**Language/role:** Erlang; extensible metric entries, probes, histograms, caching, and reporter subscriptions.

Exometer is useful for comparing synchronous entry callbacks with probes hosted in their own Erlang processes. Its histogram documentation is particularly explicit about the accuracy and cost of different sliding-window representations.

- **C2:** Entry types, probe processes, cached readings, and reporter subscriptions form independently reusable pieces. The [repository architecture overview](https://github.com/Feuerlabs/exometer_core) describes their responsibilities.
- **C1:** Approximate histogram statistics have defined semantics: a reported sample count can describe the values used by the calculation rather than every event originally observed. Window size, slot period, truncation, and rounding affect interpretation.
- **C3:** Full sliding-window storage is contrasted with slot aggregation using summary values and retained samples. The documented timestamp-driven test facility compares accuracy and cost without needing wall-clock waits. Read the [exometer_histogram module documentation](https://exometer-core.hexdocs.pm/exometer_histogram.html).

The inspected module documentation is version 2.0.0. This entry recommends a concrete architecture to study; it does not assert a current maintenance cadence.

### [mirage/metrics](https://github.com/mirage/metrics)

**Language/role:** OCaml; typed metric sources, runtime selection, and pluggable reporters.

This provides a useful functional-language perspective: data fields retain type information, while metric sources and reporting are separated. Sources can also wrap computations to record duration and result status.

- **C2:** Typed field dictionaries, source/tag types, custom reporters, and computation wrappers support metrics from application operations and runtime statistics. A cache reporter bridges event-driven production and periodic collection by retaining the latest measurement per source.
- **C3:** Tags enable or disable sources at runtime. The API documents the disabled path's remaining closure-allocation cost, making selective production instrumentation a deliberate design choice. Latest-value caching also avoids requiring a network report for every event, although it is not a general replacement for aggregating distributions.

Read the [Metrics module documentation](https://ocaml.org/p/metrics/latest/doc/metrics/Metrics/index.html), including source types, monitoring, and reporter records. The inspected documentation identifies version 0.5.0. The [repository overview](https://github.com/mirage/metrics) connects the core abstraction to its companion runtime and reporting packages.

## Histogram and sketch aggregation primitives

### [HdrHistogram/HdrHistogram](https://github.com/HdrHistogram/HdrHistogram)

**Language/role:** Java; configurable-precision histograms, recording variants, and interval extraction.

Study both the bucket representation and the harder problem of extracting intervals while writers continue recording. Its broader API also makes coordinated omission an explicit measurement concern.

- **C1:** `Recorder` rotates active and inactive histograms through a writer/reader phaser and waits for in-flight writers. Recycled interval histograms are checked for appropriate provenance and implementation type. Read [Recorder.java](https://raw.githubusercontent.com/HdrHistogram/HdrHistogram/master/src/main/java/org/HdrHistogram/Recorder.java).
- **C3:** The bucket/sub-bucket organization relates precision and trackable range to array storage. Interval-histogram recycling avoids repeated allocation, while packed and conventional representations offer different cost tradeoffs. See the [representation and recording guide](https://github.com/HdrHistogram/HdrHistogram).

The base `Histogram` and its concurrent recording variants have different thread-safety contracts. Likewise, coordinated-omission correction requires an expected sampling interval; simply using the histogram does not automatically repair biased measurement. These distinctions make the project more instructive than a generic percentile API.

### [DataDog/sketches-go](https://github.com/DataDog/sketches-go)

**Language/role:** Go; mergeable distribution sketches, especially DDSketch.

The valuable study target is how relative-error quantile estimation interacts with signed values, mapping compatibility, bounded storage, and floating-point behavior. It is directly applicable to distributed metric aggregation.

- **C1:** DDSketch separates positive and negative stores from the near-zero count, rejects invalid inputs such as NaN and negative multiplicities, and checks index-mapping compatibility before merging. Explicit floating-point conversions address rank calculations whose rounding could otherwise vary with compiler fusion.
- **C3:** Store implementations distinguish growing storage from bounded collapsing storage. Collapsing bins limits memory but can lose the accuracy guarantee for observations represented by the collapsed region; the guarantee should not be generalized to all quantiles after collapse.
- **C2:** Mapping and store interfaces separate approximation policy from storage layout and permit different combinations under a shared merge and serialization API.

Read [ddsketch.go](https://raw.githubusercontent.com/DataDog/sketches-go/master/ddsketch/ddsketch.go), then the [repository's sketch and store overview](https://github.com/DataDog/sketches-go). No numerical benchmark claim is needed to appreciate the explicit memory/accuracy contract.

### [openhistogram/libcircllhist](https://github.com/openhistogram/libcircllhist)

**Language/role:** C, with language bindings; log-linear histograms and distribution operations.

The public interface is unusually rich in numerical and ownership contracts. It is a good study target for applications that need to merge, serialize, subtract, and interrogate distributions rather than only export fixed buckets.

- **C1:** The API distinguishes bucket behavior around zero and across signs, provides integer-and-scale insertion to control conversion issues, and documents subtraction underflow and accumulation failure behavior. Quantile interfaces distinguish statistical definitions, including Type 1 and Type 7.
- **C2:** Accumulation, subtraction, serialization, custom allocators, and bindings make the representation usable beyond one instrumentation client.
- **C3:** The fast-allocation variant spends more memory on indexing to accelerate lookup, and clearing can retain bucket storage for reuse. These are explicit alternatives to a single opaque “fast histogram” implementation.

Read [src/circllhist.h](https://raw.githubusercontent.com/openhistogram/libcircllhist/master/src/circllhist.h) for the contracts and data representation, and the [repository overview](https://github.com/openhistogram/libcircllhist) for integration and binding context.

## Coverage, search process, and limits

Discovery used live web searches with more than six distinct formulations, followed by opening official GitHub pages and separate primary material. Search angles included general instrumentation/registry libraries; Java reservoirs and backend facades; Go buffered reporters and SDK aggregation; Rust typed metric families and recorder abstractions; C/C++ histogram and codec libraries; Python/Ruby/Node multiprocess clients; .NET runtime integration; PHP Redis/APCu storage; BEAM Telemetry reporters and Exometer; OCaml and Haskell instrumentation; and mergeable sketches, HdrHistogram, and log-linear histograms. Follow-up searches targeted concurrency, bucket layout, lifecycle, compatibility history, and documented limitations. Later searches increasingly returned already covered architectures, small adapters, or monitoring products outside this category.

The selection deliberately includes less prominent implementations such as Peep, Exometer, CMetrics, the OCaml Metrics library, and libcircllhist alongside established facades and clients. Several Prometheus clients remain because their process models, storage designs, type systems, and synchronization approaches differ substantially. Conversely, the list does not repeat every OpenTelemetry language SDK or every port of the same histogram algorithm. Haskell and additional StatsD/Clojure candidates were explored but not retained without equally strong independently inspected evidence. Omission is not a quality judgment.

Monitoring servers and databases, dashboards, tracing-only packages, thin generated wrappers, tutorials, awesome-lists, and source-code complexity tools were excluded. The VictoriaMetrics entry is its standalone instrumentation library, and the OpenTelemetry and Kamon entries identify only their relevant metric subsystems. Repository transfers use their verified canonical locations; no unofficial fork is presented as a separate implementation, and no retained entry is presented as an official mirror or an archived project.

This is a source-based selection guide, not a benchmark, audit, or support recommendation. Candidate code was not executed and tests were not run. Maintenance activity is not inferred from stars, age, or a recent push; C4 is used only where release and compatibility evidence was inspected. Published API documentation can lag repository branches, with notable inspected versions stated above. Branch-linked source files may change after the research date. The criteria describe concrete areas worth studying, not a claim that every component of every repository is uniformly exemplary.
