# Load testing and performance benchmarking tools

Research date: **2026-10-09**.

This selection covers 28 repositories for generating service, storage, database, and network workloads; measuring small pieces of code; and tracking performance changes. The expanded count reflects distinct engineering problems: controlling arrivals, keeping the generator from becoming the bottleneck, preserving observable work under optimizing compilers, and drawing defensible conclusions from noisy measurements. It includes libraries and standalone tools, and counts monorepos and successor lineages once. This is a source-reading guide, not a ranking of measured speed or a claim that every component is exemplary.

Criteria used below:

- **C1 — Difficult correctness:** concurrency, ordering, measurement semantics, numerical analysis, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and composition mechanisms that support different workloads or environments.
- **C3 — Performance architecture:** explicit resource or throughput constraints addressed through an understandable design.
- **C4 — Sustained evolution:** multi-year evidence of compatibility work, testing, or management of implementation complexity. Age and popularity alone do not qualify.

## Service load-testing frameworks

### [grafana/k6](https://github.com/grafana/k6)

**Language / role:** Go runtime with JavaScript test scripts; programmable service load testing.

Study how a scenario's execution model determines what a load test actually measures. **C1:** the distinction between closed workloads, where slow iterations reduce subsequent arrivals, and open workloads, where arrival scheduling is independent of completion, directly addresses coordinated omission. **C2:** scenario executors expose different reusable scheduling policies—constant or changing virtual-user counts and constant or changing arrival rates—without requiring each script to implement a scheduler. The documentation also explains why arrival-rate executors need enough allocated virtual users; choosing an open model does not give the generator unlimited capacity. Entry point: the substantive [open versus closed workload model guide](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/).

### [locustio/locust](https://github.com/locustio/locust)

**Language / role:** Python; user-behavior load testing with gevent and distributed workers.

Study the separation between a control process and processes that execute simulated users. **C2:** user classes, runner events, and custom master/worker messages support application-specific behavior without replacing orchestration. **C3:** the master coordinates spawning and statistics while workers execute users; the documentation connects process placement to Python CPU limits. **C1:** custom message callbacks have observable scheduling consequences: a blocking callback can interfere with worker heartbeats, while concurrently dispatched callbacks run in greenlets that the framework does not join. These details make the extension API a useful concurrency study. Entry point: [distributed execution and custom messaging](https://docs.locust.io/en/stable/running-distributed.html).

### [apache/jmeter](https://github.com/apache/jmeter)

**Language / role:** Primarily Java; extensible, multi-protocol test-plan execution. This is Apache's official GitHub read-only source mirror, listed alongside GitBox on the [source repositories page](https://jmeter.apache.org/svnindex.html).

Study a test-plan interpreter built from samplers, controllers, timers, assertions, and listeners. **C2:** these components compose protocol operations, control flow, validation, and reporting across many workloads. **C1:** synchronization has a carefully bounded meaning: the Critical Section Controller serializes children sharing a lock name within one JVM, but does not provide a cluster-wide lock across distributed JMeter engines. That is a concrete example of a seemingly simple test-plan operation whose correctness depends on deployment topology. Entry point: the [component reference](https://jmeter.apache.org/usermanual/component_reference.html), especially Critical Section Controller and listener behavior.

### [gatling/gatling](https://github.com/gatling/gatling)

**Language / role:** Scala and Java; scenario-based load-testing engine with multiple language DSLs.

Study the relationship between a declarative scenario and its per-user state. **C2:** actions pass a `Session` through a workflow; attributes, checks, and feeders let the same execution machinery drive different application protocols and journeys. **C1:** sessions are immutable: setting an attribute returns a new session, and discarding that return value silently discards the intended state change. The API also carries success/failure state through the chain. This makes the codebase useful for understanding how immutable messages can simplify concurrent execution while imposing precise contracts on extension code. Entry point: [Session API and execution examples](https://docs.gatling.io/concepts/session/api/).

### [artilleryio/artillery](https://github.com/artilleryio/artillery)

**Language / role:** JavaScript/TypeScript; load-testing monorepo. The relevant subsystem is the core engine and its engine/plugin extension interfaces.

Study how an extensible runner crosses Node worker boundaries. **C2:** plugins receive the test script and event emitter, can hook virtual-user behavior, and can report counters, histograms, and rates through shared interfaces. Cleanup callbacks provide a place to finish buffered reporting. **C1:** the v2 worker model cannot transfer function objects from the main thread to workers; plugins that add executable functions must arrange that work inside the worker. This is a concrete serialization and lifecycle constraint, not just a catalog of plugins. Entry point: [extension APIs, hooks, metrics, and worker considerations](https://www.artillery.io/docs/reference/extension-apis).

### [Hyperfoil/Hyperfoil](https://github.com/Hyperfoil/Hyperfoil)

**Language / role:** Java; distributed load generation organized around sessions, sequences, and event-loop execution.

Study a cooperative execution engine with explicit resource reservation. **C1:** a `Step` that returns `false` is blocked and must not have produced side effects, so retrying it must preserve behavior. **C2:** the step/session contract and resources scoped to sequences let protocols and actions extend the engine. **C3:** the session implementation uses a limited pool of sequence instances, preallocated running-sequence storage, reserved resources, and an event executor; its progress loop stops when no sequence can advance. These are concrete mechanisms for controlling work and allocation in the generator. Entry points: the [Step contract](https://github.com/Hyperfoil/Hyperfoil/blob/master/api/src/main/java/io/hyperfoil/api/config/Step.java) and [SessionImpl](https://github.com/Hyperfoil/Hyperfoil/blob/master/core/src/main/java/io/hyperfoil/core/session/SessionImpl.java).

### [tag1consulting/goose](https://github.com/tag1consulting/goose)

**Language / role:** Rust; programmable HTTP load testing using scenarios and transactions.

Study per-user state and communication between execution and reporting. **C2:** `GooseUser` combines an HTTP client, cookies, configuration, and typed session data with reusable scenario/transaction definitions. **C3:** separate channels carry metrics, log messages, throttling requests, and shutdown notifications; this exposes the boundaries between user activity and centralized coordination. Startup/shutdown transactions also have distinct throttling behavior. Entry point: [GooseUser API and fields](https://docs.rs/goose/latest/goose/goose/struct.GooseUser.html).

**Version caveat:** the official [Gaggle documentation](https://book.goose.rs/gaggle/overview.html) says distributed support was removed in 0.17.0 and directs users of that older feature to 0.16.4. Current Goose should not be described as supporting the documented historical manager/worker mode.

### [processone/tsung](https://github.com/processone/tsung)

**Language / role:** Erlang, with reporting utilities; distributed, multi-protocol load testing.

Study long-running generators that cannot afford to retain every measurement. **C3:** Tsung computes means and standard deviations online and periodically writes aggregates, distinguishing samples, cumulative samples, counters, and sums. Its reporting model explicitly treats unacknowledged operations differently because a response time is not meaningful for them. **C2:** shared session and measurement machinery supports protocols including HTTP, XMPP, LDAP, and MQTT. **C4:** the changelog documents evolution from 2015 through the listed 2023 release, including Erlang time-API compatibility, race fixes, HTTP framing fixes, and MQTT/WebSocket corrections. This supports a historical evolution claim, not an assertion of a frequent current release cadence. Entry points: [statistics/report semantics](https://tsung.readthedocs.io/en/latest/reports.html) and [changelog](https://github.com/processone/tsung/blob/develop/CHANGELOG.md).

## Focused HTTP and RPC generators

### [giltene/wrk2](https://github.com/giltene/wrk2)

**Language / role:** C with Lua scripting; constant-throughput HTTP benchmarking.

This is a substantive variant of `wg/wrk`, retained for its different scheduling and latency model rather than counted as an interchangeable fork. Study how intended arrival time changes measured latency. **C1:** latency is measured relative to when a request should have been sent, with explicit treatment of pipelining and catch-up, rather than only from actual dispatch. **C3:** per-thread event loops and histograms separate connection handling from aggregation; the implementation also distinguishes static and dynamically scripted request generation. The repository calls the work experimental/development and discusses timing granularity and calibration limitations. Entry points: the repository's measurement discussion and the [request scheduler, event loops, and histogram implementation](https://raw.githubusercontent.com/giltene/wrk2/master/src/wrk.c).

### [tsenart/vegeta](https://github.com/tsenart/vegeta)

**Language / role:** Go; HTTP load generator available as both a CLI and library.

Study a rate-driven attacker whose target source, pacing, and transport are separable. **C2:** `Targeter`, `Pacer`, and attacker options allow request generation and arrival policies to vary independently. **C1:** the implementation deliberately serializes sequence-number allocation and timestamps to preserve their ordering, uses a wait group to finish workers before closing results, and makes stopping idempotent. **C3:** workers can grow under pressure up to a configured ceiling, exposing the tradeoff between maintaining the requested rate and bounding generator resources. Entry point: [attack orchestration and lifecycle source](https://raw.githubusercontent.com/tsenart/vegeta/master/lib/attack.go).

### [fortio/fortio](https://github.com/fortio/fortio)

**Language / role:** Go; HTTP/gRPC and network load testing, reusable execution and statistics machinery.

Study a protocol-independent periodic runner rather than only the command-line frontend. **C2:** a `Runnable` receives a context and worker identifier, allowing the same scheduling machinery and runner options to drive different operations. **C1:** the abort controller coordinates a shared stop channel under a mutex, handles stop-before-start, and prevents closing a channel more than once; start-time recording also takes a synchronized snapshot. These small interfaces expose the difficult lifecycle behavior that reusable load generators must get right. Entry point: [periodic runner interfaces, options, and abort state](https://raw.githubusercontent.com/fortio/fortio/master/periodic/periodic.go).

### [bojand/ghz](https://github.com/bojand/ghz)

**Language / role:** Go; gRPC benchmarking through dynamic service/method descriptions.

Study a runner that must reconcile load scheduling with several RPC lifecycles. **C2:** method descriptors, data and metadata providers, and streaming interceptors let the same worker support unary, client-streaming, server-streaming, and bidirectional calls. **C1:** workers create per-request timeout/cancellation contexts and coordinate outstanding asynchronous requests through an error group when stopping. These contracts matter because finishing a load phase is different from simply ceasing to create calls. The separate load model supports constant, step, and linear schedules. Entry points: [worker implementation](https://github.com/bojand/ghz/blob/master/runner/worker.go) and [load scheduling guide](https://ghz.sh/docs/load).

## Storage, database, and network workloads

### [axboe/fio](https://github.com/axboe/fio)

**Language / role:** C; configurable storage and filesystem I/O workload generator.

Study the interaction between queueing, data verification, and submission policy. **C1:** overlapping in-flight writes can leave nondeterministic contents; `serialize_overlap` addresses false verification failures by serializing conflicts, with an explicit throughput cost. **C2:** pluggable I/O engines and composable job options cover synchronous/asynchronous operations, verification, addressing, and queue depth. **C3:** offloaded submission separates submission threads from completion handling to help avoid coordinated omission, but the manual also documents overhead and limitations with asynchronous engines. Those qualifications are useful architectural evidence rather than a universal speed claim. Entry point: the [fio manual](https://fio.readthedocs.io/en/latest/fio_doc.html), particularly `serialize_overlap`, `io_submit_mode`, and engine options.

### [akopytov/sysbench](https://github.com/akopytov/sysbench)

**Language / role:** C and Lua/LuaJIT; threaded database and system workload framework.

Study the boundary between a native execution harness and script-defined workload lifecycle. **C2:** Lua hooks and common SQL routines share connection handling, workload options, preparation, and cleanup while accommodating database-driver differences. **C3:** the OLTP implementation partitions table preparation and warmup by thread identifier and thread count, rather than funneling setup through one worker. This provides a concrete example of treating data preparation as part of the scalability problem, alongside the timed workload. The repository also supplies non-database workloads, making the harness broader than one SQL benchmark. Entry point: [common OLTP lifecycle, driver selection, and parallel preparation](https://raw.githubusercontent.com/akopytov/sysbench/master/src/lua/oltp_common.lua).

### [brianfrankcooper/YCSB](https://github.com/brianfrankcooper/YCSB)

**Language / role:** Java; database benchmark core and datastore bindings in one repository.

Study how a common workload is translated into different datastore semantics. **C2:** the `DB` interface gives each client thread a binding instance with initialization, cleanup, and CRUD/scan operations; it explicitly leaves some durability and existence semantics to the binding instead of pretending all databases behave identically. **C1:** the acknowledged counter maintains a contiguous frontier of completed insert identifiers despite out-of-order acknowledgments, using a bounded window and an overflow failure. This is a concrete concurrency invariant behind selecting usable keys during a workload. Entry points: [DB binding contract](https://raw.githubusercontent.com/brianfrankcooper/YCSB/master/core/src/main/java/site/ycsb/DB.java) and [AcknowledgedCounterGenerator](https://github.com/brianfrankcooper/YCSB/blob/master/core/src/main/java/site/ycsb/generator/AcknowledgedCounterGenerator.java). The core and bindings count as one project.

### [redis/memtier_benchmark](https://github.com/redis/memtier_benchmark)

**Language / role:** C++; Redis and Memcached workload generation, including Redis Cluster.

Study the work required to make the benchmark client itself survive topology changes. **C1:** cluster routing initializes slots with an invalid sentinel, handles Redis hash tags, and guards against routing through stale or unavailable connection groups during bootstrap and refresh. **C3:** connection pools, queue limits, and event-loop yielding after unsuccessful routing attempts show how cluster correctness interacts with keeping the generator responsive. These mechanisms make it more instructive than a fixed request loop: a disrupted cluster exercises the load generator's own state machine as well as the server. Entry point: [cluster client routing, connection groups, and request pumping](https://raw.githubusercontent.com/redis/memtier_benchmark/master/cluster_client.cpp). The verified canonical owner is `redis`, rather than the older RedisLabs location.

### [minio/warp](https://github.com/minio/warp)

**Language / role:** Go; S3-compatible object-storage benchmarking and recorded-run analysis.

Study how concurrent requests become aggregate throughput and latency reports. **C1:** analysis uses a common interval after workers have begun and before they finish, distinguishes operation types and partial operations, and rejects analysis paths with insufficient data. Distributed run merging considers overlapping absolute time, so a merged report is not simply a sum of unrelated intervals. **C2:** load generation, saved request data, re-analysis, comparison, and merging form reusable stages for different S3 operations and object-size distributions. This is useful for studying a benchmark's data model as well as its request loop. Entry points: the repository's Analysis section and [analysis orchestration source](https://raw.githubusercontent.com/minio/warp/master/cli/analyze.go).

### [esnet/iperf](https://github.com/esnet/iperf)

**Language / role:** C; iperf3 network throughput measurement, distinct from the iperf2 implementation.

Study why control-plane completion and data-plane completion are not interchangeable. **C1:** the FAQ explains that a stop/control message can arrive before all test data, producing sender/receiver discrepancies in short runs; NIC offload also changes how observations should be interpreted. **C3:** the release history documents the move to multiple threads for parallel streams in 3.16. **C4:** the 2023–2026 notes connect that architectural evolution to OpenSSL compatibility, malformed control-message fixes, and an authentication change requiring compatibility consideration. Entry points: [measurement and implementation FAQ](https://software.es.net/iperf/faq.html) and [release/news history](https://software.es.net/iperf/news.html). The evidence supports specific changes, not a promise of attainable bandwidth on arbitrary hardware.

### [tumi8/MoonGen](https://github.com/tumi8/MoonGen)

**Language / role:** Lua with C/C++ and DPDK; programmable packet generation and network experiments.

This is the continuation identified by the [original MoonGen repository](https://github.com/emmericp/MoonGen); the lineage is counted once. Study the distinction between enqueueing packets and controlling their departure on the wire. **C1:** NICs fetch queued packets asynchronously, so sleeping between software sends can produce unintended bursts rather than the specified inter-packet gaps. **C3:** the design combines independent LuaJIT execution contexts, batched packet processing, and hardware rate control; an alternative fills gaps with deliberately invalid packets that suitable hardware discards. Hardware and switch behavior therefore remain part of the experiment's assumptions. Entry point: the verified current-branch [rate-control design discussion](https://github.com/tumi8/MoonGen/blob/v22.11/ratecontrol.md), alongside the repository's threading model.

## Language, process, and regression benchmarking

### [google/benchmark](https://github.com/google/benchmark)

**Language / role:** C++; reusable microbenchmark harness.

Study the boundary between the work a programmer writes and the work an optimizer leaves behind. **C1:** `DoNotOptimize` and `ClobberMemory` have precise limits: known expressions may still be folded, and memory must be appropriately escaped for a memory clobber to matter. Timer pause/resume and manual timing introduce additional contracts. **C2:** fixtures, arguments, counters, threaded benchmarks, and manual timing let the same harness measure ordinary functions, concurrent workloads, and externally timed operations. The useful lesson is that compiler barriers, iteration control, and timing modes belong in the harness API rather than in ad hoc stopwatch code. Entry point: [user guide, optimizer controls, and timing modes](https://google.github.io/benchmark/user_guide.html).

### [openjdk/jmh](https://github.com/openjdk/jmh)

**Language / role:** Java; JVM microbenchmark harness with generated benchmark code.

Study why a JVM benchmark requires controlled state and generated execution scaffolding. **C2:** annotations describe benchmark methods, state scope, modes, warmup, and forks, allowing the harness to generate and execute many benchmark configurations. **C1:** returning one computed value is insufficient when a method performs several independent computations whose results might be discarded; the Blackhole examples explain how to keep that work observable and why naive consumption can itself distort the benchmark. The repository is useful for connecting JIT optimization hazards to a reusable harness contract. Entry point: the explanatory [Blackholes sample](https://raw.githubusercontent.com/openjdk/jmh/master/jmh-samples/src/main/java/org/openjdk/jmh/samples/JMHSample_09_Blackholes.java), read with the repository's harness/build overview.

### [dotnet/BenchmarkDotNet](https://github.com/dotnet/BenchmarkDotNet)

**Language / role:** C#; .NET benchmark generation, execution, and analysis.

Study an explicit multi-stage experiment pipeline. **C2:** benchmark methods, jobs, and parameter combinations generate isolated Release projects and child-process executions for the chosen runtime configuration. **C1:** the engine separates pilot calibration, overhead warmup/measurement, workload warmup, and actual samples; it subtracts estimated overhead and gathers GC statistics in an additional iteration to reduce diagnostic interference. These stages expose the assumptions behind a reported timing and provide a useful model for adapting a harness to multiple runtimes. Entry point: [how the generated harness and measurement engine work](https://benchmarkdotnet.org/articles/guides/how-it-works.html).

### [criterion-rs/criterion.rs](https://github.com/criterion-rs/criterion.rs)

**Language / role:** Rust; statistical microbenchmarking with saved baselines.

This is the successor linked by [bheisler/criterion.rs](https://github.com/bheisler/criterion.rs), not a second independent entry. Study the analysis pipeline rather than treating a confidence interval as an unexplained output. **C1:** the implementation rejects zero-time measurements, classifies outliers, bootstraps estimates, applies regression for the appropriate sampling mode, and combines significance and noise thresholds when assessing change. **C2:** analysis is generic over a `Measurement` and benchmark `Routine`, with report callbacks and saved baseline data separating measurement from presentation and comparison. Entry point: [analysis implementation](https://raw.githubusercontent.com/criterion-rs/criterion.rs/master/src/analysis/mod.rs). Statistical machinery reduces some errors; it does not establish that a workload represents production behavior.

### [sharkdp/hyperfine](https://github.com/sharkdp/hyperfine)

**Language / role:** Rust; repeatable command/process benchmarking.

Study the lifecycle around an external command, where shell startup and preparation can dominate a small workload. **C1:** the tool distinguishes setup, per-run preparation, conclusion, and cleanup; it also addresses warmup and shell overhead when shell execution is selected. A benchmark result depends on putting work in the correct phase. **C2:** the benchmark engine is separated from an `Executor` interface and combines these lifecycle hooks with parameterized command scans and structured reports. This makes it useful for studying reusable process-level experiments without requiring code changes to the measured program. Entry points: the repository's usage/lifecycle documentation and [benchmark engine](https://raw.githubusercontent.com/sharkdp/hyperfine/master/src/benchmark/mod.rs). Shell behavior should be checked for the version used.

### [psf/pyperf](https://github.com/psf/pyperf)

**Language / role:** Python; benchmark runner, process management, and result comparison.

Study how an apparently simple Python timing function becomes a controlled multi-process experiment. **C1:** the runner calibrates loop counts, distinguishes warmups from retained values, and exposes different warmup needs for JIT implementations; affinity, environment inheritance, and timeouts make important sources of variation explicit. **C2:** a reusable `Runner` and a common serialized result format support function, statement, and command benchmarks plus later comparisons. The value is in the interaction between calibration and process isolation rather than in a single timer function. Entry point: [runner architecture, calibration, workers, and environment controls](https://pyperf.readthedocs.io/en/latest/runner.html).

### [airspeed-velocity/asv](https://github.com/airspeed-velocity/asv)

**Language / role:** Python with a web presentation layer; performance tracking across project revisions and environments.

Study benchmark discovery and lifecycle conventions designed for repeated historical runs. **C2:** naming conventions, suites, parameters, setup/teardown, and multiple benchmark types provide a shared interface for timing, memory, and tracked values. **C1:** benchmarks normally execute in separate processes, while repeated measurements and profiling have specific reuse behavior; setup can run multiple times and must tolerate that lifecycle. The guide even distinguishes spawn from fork for CUDA contexts, showing that process isolation is a semantic choice rather than a universally safe default. Entry point: [writing benchmarks and execution-lifecycle guidance](https://asv.readthedocs.io/en/stable/writing_benchmarks.html). This adds regression-history orchestration to the selection, beyond single-run timing tools.

### [haskell/criterion](https://github.com/haskell/criterion)

**Language / role:** Haskell; microbenchmark composition and statistical analysis.

Study measurement under lazy evaluation. **C1:** benchmarking an already saturated pure expression can measure reuse of its first result; `nf` and `whnf` instead accept a function and argument and deliberately choose evaluation depth. Lazy I/O can also leak resources if results are insufficiently forced. **C2:** `Benchmarkable`, named groups, pure-function adapters, and I/O adapters compose different measurements behind one runner. The analysis implementation adds a separate numerical study: filtering very short measurements, bootstrap confidence intervals, regression, and validation of requested predictor metrics. Entry points: the repository's detailed tutorial and [Criterion.Analysis](https://github.com/haskell/criterion/blob/master/Criterion/Analysis.hs). This is distinct from the Rust project despite the shared name and statistical influence.

### [JuliaCI/BenchmarkTools.jl](https://github.com/JuliaCI/BenchmarkTools.jl)

**Language / role:** Julia; parameterized benchmark definitions, trial collection, and comparison.

Study the separation between an evaluation, a timed sample containing several evaluations, and a trial containing multiple samples. **C1:** batching amortizes timer overhead but can invalidate a benchmark that mutates its input; the manual explains when to use one evaluation per sample and how setup is scoped. GC controls and overhead subtraction are also explicit parameters. **C2:** benchmark definitions, groups, tuning, and trial/result objects let suites reuse the same measurement and comparison machinery while retaining per-benchmark parameters. This provides a useful counterpart to compiler-oriented and process-oriented harnesses. Entry point: the substantive [manual on sampling, setup, tuning, and benchmark groups](https://juliaci.github.io/BenchmarkTools.jl/stable/manual/).

## Coverage, search method, and limitations

Live discovery used more than six distinct search formulations, spanning: distributed HTTP frameworks; constant-arrival load and coordinated omission; Rust load generators; Erlang and event-loop architectures; gRPC and streaming RPC benchmarks; storage queue depth and verification; database driver/workload frameworks; Redis Cluster and S3 generators; network throughput and DPDK packet generation; C++/JVM/.NET microbenchmark harnesses; Python calibration and performance history; and Haskell/Julia evaluation and sampling semantics. Later queries repeatedly returned the same families or overlapping alternatives, so expansion stopped after adding the distinct packet-generation and language-semantics cases.

Every retained repository's GitHub root was opened, and at least one separate primary implementation or documentation source was opened and read. Failed documentation fetches were replaced with readable source files where possible. Exact source links are included above; branches and versionless documentation can change after this research date. The explanations of what an engineer can study and the C1–C4 assignments are grounded judgments based on those sources, not claims by maintainers that their entire repositories satisfy a quality standard.

The search also surfaced Nighthawk, NBomber, drill, TRex, dperf, and benchmark-result services. They were not retained after balancing overlap and the depth of primary-source inspection; their absence is not a negative quality judgment. Awesome lists, thin wrappers, tutorial projects, application-specific result collections, and commercial-only services were excluded. Original wrk was not counted separately from the selected substantive wrk2 variant; the old Criterion.rs and MoonGen locations were used only to verify successor provenance. JMeter's official GitHub mirror and Goose's historical distributed feature are explicitly identified.

No candidate code was executed, no dependencies installed, and no throughput or accuracy claims were independently reproduced. Maintenance cadence was not inferred from stars or a recent push. C4 is used only where reviewed history supports a concrete multi-year claim; experimental and historical qualifications are preserved. The report is broad across architectures and languages, but is not an exhaustive inventory of every protocol, language runtime, or hardware benchmark.
