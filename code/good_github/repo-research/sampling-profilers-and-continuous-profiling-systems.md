# Sampling profilers and continuous profiling systems

Research date: **2026-10-09**.

This selection covers 26 repositories implementing statistical stack collection, sampled allocation profiling, or the collection, transport, storage, and querying needed for continuous profiling. It includes embedded libraries, external process inspectors, operating-system collectors, and distributed services. Mixed tracing/profiling tools are included only where a substantial sampling subsystem is identifiable. These are study recommendations grounded in inspected primary material, not claims that every component is exemplary or that every project is currently maintained.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions supporting multiple uses. **C3** — real performance constraints addressed through understandable architecture. **C4** — sustained evolution accompanied by compatibility work, testing, or complexity management. Each entry explicitly supports at least two criteria. Links in the entries are reading entry points as well as evidence.

## Continuous profiling services and host agents

### [grafana/pyroscope](https://github.com/grafana/pyroscope)

**Language/role:** Go and TypeScript; continuous profiling ingestion, storage, query services, and UI. Study how a specialized observability database separates ingestion durability from expensive profile aggregation. The inspected documentation describes the v2 architecture; older descriptions of local-disk ingesters should not be assumed to describe this design.

- **C1:** Ingestion waits for both durable object storage and a metadata-index entry. The metastore uses Raft replication, making the relationship between data visibility, metadata, and failure recovery a substantive correctness problem.
- **C3:** Separate write/query services, application-aware placement, parallel query execution, and background segment compaction address write cost and read amplification. The [v2 architecture description](https://grafana.com/docs/pyroscope/latest/reference-pyroscope-v2-architecture/about-pyroscope-v2-architecture/) explains these mechanisms rather than merely promising scalability. The [architecture index](https://grafana.com/docs/pyroscope/latest/reference-pyroscope-v2-architecture/) leads to individual component and block-format designs.

### [parca-dev/parca](https://github.com/parca-dev/parca)

**Language/role:** Go and TypeScript; continuous profile server and query UI. Particularly useful for studying the translation between a profile's logical call stacks and a columnar representation containing labels, mappings, functions, and sample values.

- **C1:** The [Arrow-to-profile converter](https://github.com/parca-dev/parca/blob/main/pkg/parcacol/arrow.go) handles sliced-array offsets, dictionary indices, nullable locations, field-name lookup, and required-column errors. These details determine whether samples remain associated with the correct frames and labels.
- **C2:** A common profile model connects ingestion, symbolization, querying, and different presentation forms. The [package tree](https://github.com/parca-dev/parca/tree/main/pkg) exposes those boundaries explicitly, including `profile`, `normalizer`, `profilestore`, `symbolizer`, and `query`. The repository's pprof ingestion and label-based selection make these abstractions useful across runtimes, rather than only for one collector.

### [parca-dev/parca-agent](https://github.com/parca-dev/parca-agent)

**Language/role:** Primarily Go with native/eBPF integration; host-wide collection and profile export. Its current reporter imports the OpenTelemetry eBPF profiler. It is retained for its substantial Parca-specific labeling, conversion, and export implementation, not counted as an independently invented version of that unwinder.

- **C1:** The [reporter implementation](https://github.com/parca-dev/parca-agent/blob/main/reporter/parca_reporter.go) distinguishes process-invariant resource labels from per-sample labels so Arrow and OTLP exports preserve their meaning. It also distinguishes raw GPU sample counts, sampling periods, and exact kernel-duration measurements instead of silently mixing incompatible units.
- **C2:** Shared executable tracking, metadata resolution, counters, and reporter interfaces support multiple export representations. The [reporter subtree](https://github.com/parca-dev/parca-agent/tree/main/reporter) includes pprof conformance tests, OTLP tests, Arrow encoding tests, and encoding/decoding benchmarks. This is a useful study of adapting a shared collector to a separate profiling platform.

### [open-telemetry/opentelemetry-ebpf-profiler](https://github.com/open-telemetry/opentelemetry-ebpf-profiler)

**Language/role:** Go, C/eBPF, and Rust; whole-system Linux profiler with native, interpreted, and JIT stack support. Study the boundary between privileged stack collection and user-space interpretation. The repository identifies its OTel Profiles support as alpha; its internal document also warns that interfaces evolve.

- **C1:** Interpreter handlers must identify runtime versions and layouts, configure unwinding metadata, and convert mixed native/interpreter traces correctly as processes and mappings change. File identity and address-relative frames are explicit parts of the design.
- **C3:** Kernel-side compact representations, trace hashing, conversion caches, and deferred native symbolization reduce repeated work and kernel-memory use. The [internals document](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/blob/main/doc/internals.md) explains the tracer, process manager, reporter, and interpreter responsibilities; the [interpreter subtree](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/tree/main/interpreter) is the implementation entry point. The documented reporting path may drop data, so its guarantees should not be confused with durable ingestion.

### [yandex/perforator](https://github.com/yandex/perforator)

**Language/role:** Go, C++, and TypeScript; cluster-wide continuous profiling with collection, binary storage, symbolization, and querying. The relevant subsystem is `perforator/` within the larger repository, not its vendored dependencies.

- **C1:** Executable identity and synchronized binary uploads prevent different agents from repeatedly uploading the same artifact. Build IDs, fallback identities, and metadata lifetimes are central to recovering the right source locations from sampled addresses.
- **C3:** Agents aggregate and compress samples, while expensive symbolization moves to a shared service. Profile metadata, binary metadata, and large objects are assigned to ClickHouse, PostgreSQL, and S3-compatible storage respectively. The [architecture overview](https://perforator.tech/docs/en/explanation/architecture/overview) explains this division and the stateless storage proxy. Enter the implementation through the [profiling subsystem](https://github.com/yandex/perforator/tree/main/perforator).

### [intel/gprofiler](https://github.com/intel/gprofiler)

**Language/role:** Python orchestration with native profiler integrations; system-wide, multi-runtime sampling. Its distinctive study value is combining different collectors into meaningful profiles, rather than merely launching subprocesses.

- **C1:** [Profile merging](https://github.com/intel/gprofiler/blob/master/gprofiler/merge.py) rescales sample counts with probabilistic rounding to avoid systematic rounding bias. The repository also explicitly disables runtime samplers for hardware-event profiling because event-count samples and time-based samples are not meaningfully interchangeable.
- **C2:** The integration layer enriches samples with application/container metadata and substitutes runtime-aware stacks for native interpreter stacks. Its [repository architecture and runtime options](https://github.com/intel/gprofiler#architecture-support) document differing backend capabilities and fallback choices. The merge code also preserves older protocol behavior, providing a concrete example of compatibility constraints inside a unifying data model.

### [apache/skywalking-rover](https://github.com/apache/skywalking-rover)

**Language/role:** Go and C/eBPF; SkyWalking host agent with on-CPU/off-CPU profiling and continuous profiling policies. Focus on `pkg/profiling`; its broader networking and tracing features are outside this selection's justification.

- **C1:** The [profiling task manager](https://github.com/apache/skywalking-rover/blob/main/pkg/profiling/task/manager.go) handles duplicate task identities, extensions of running tasks, replacement/shutdown, asynchronous execution, cancellation, and maximum-duration timers. These interactions make lifecycle correctness a real engineering concern.
- **C2:** Profiling runners share a task interface, while process discovery and profiling are separate dependent modules. The [module design](https://github.com/apache/skywalking-rover/blob/main/docs/en/concepts-and-designs/module_design.md) explains dependency-ordered startup, APIs, and shutdown hooks. This offers a smaller, readable alternative to studying an entire observability backend.

### [volcengine/continue-profiling-agent](https://github.com/volcengine/continue-profiling-agent)

**Language/role:** C, eBPF, and Rust; continuous host recorder with rotating local history and offline/TUI inspection. It supplies a useful alternative architecture to centralized ingestion services.

- **C1:** The [store specification](https://github.com/volcengine/continue-profiling-agent/blob/main/docs/en/store-format.md) discusses partially flushed tails, record validation, cross-day timestamps, and a Rust reader that defensively drops the final indexed record. It also documents differences between BPF and perf metadata and the limits of environment-derived pod labels.
- **C3:** Interned strings and stack IDs, compressed append-oriented files, and deliberate exclusion of high-cardinality thread IDs constrain long-running storage costs. The [architecture guide](https://github.com/volcengine/continue-profiling-agent/blob/main/docs/en/architecture.md) separates capture, unwinding, rotation, and viewing. Its README carries a specific kernel-compatibility warning; inclusion here is a code-study recommendation, not blanket deployment advice.

## Runtime-specific stack samplers

### [async-profiler/async-profiler](https://github.com/async-profiler/async-profiler)

**Language/role:** C++ and Java; HotSpot sampling profiler with native/kernel stacks and additional allocation/lock modes. Study how JVM internals and operating-system sampling interact without requiring safepoint-only stack capture.

- **C1:** The [stack-walking design](https://github.com/async-profiler/async-profiler/blob/master/docs/StackWalkingModes.md) explains failures of `AsyncGetCallTrace`, VM-structure-based unwinding, crash protection, and mixed Java/native frames. It documents the change to VM-structure walking as the default in version 4.2.
- **C3:** The [CPU sampling-engine guide](https://github.com/async-profiler/async-profiler/blob/master/docs/CpuSamplingEngines.md) compares per-thread perf descriptors, process interval timers, and CPU timers in terms of fairness, resolution, descriptor pressure, and container restrictions. This is unusually explicit documentation of why alternate implementations exist and what each sacrifices.

### [benfred/py-spy](https://github.com/benfred/py-spy)

**Language/role:** Rust; external CPython stack sampler with live, recorded, and stack-dump modes. Study remote-memory inspection across changing interpreter layouts and operating systems.

- **C1:** The [PythonSpy implementation](https://github.com/benfred/py-spy/blob/master/src/python_spy.rs) selects version-specific ABI layouts, retries attachment until stack reading works, and handles platform-specific locking and Python-to-OS thread identification. Nonblocking mode has explicitly weaker thread-identification options.
- **C2:** `PythonSpy` provides a common stack-retrieval interface above process access, interpreter discovery, native unwinding, and version dispatch. The [repository's implementation explanation](https://github.com/benfred/py-spy#how-does-py-spy-work) describes symbol lookup and BSS-based interpreter discovery. The same collection machinery feeds different reporting workflows rather than embedding presentation into the memory reader.

### [P403n1x87/austin](https://github.com/P403n1x87/austin)

**Language/role:** C; external CPython frame-stack sampler intended to feed other analysis tools. Its small collector boundary makes it useful alongside larger Python profiler implementations.

- **C1:** [Thread-stack collection](https://github.com/P403n1x87/austin/blob/master/src/py_thread.c) checks self-referential frame links, distinguishes interpreter-frame layouts and shim frames across Python versions, and truncates stacks when frame resolution fails.
- **C3:** That implementation caches resolved frames and reuses locally copied stack chunks before falling back to remote reads. The [source tree](https://github.com/P403n1x87/austin/tree/master/src) separates platform access, version descriptions, stack storage, caching, and output events, making the cost of repeated process-memory inspection easy to trace architecturally.

### [plasma-umass/scalene](https://github.com/plasma-umass/scalene)

**Language/role:** Python and C++; statistical CPU, GPU, and memory profiler. Study attribution when Python execution, native calls, sleeping threads, and asynchronous tasks share a process.

- **C1:** The [CPU sample processor](https://github.com/plasma-umass/scalene/blob/master/scalene/scalene_cpu_profiler.py) checks negative elapsed times and invalid GPU measurements, normalizes utilization, and distinguishes timer-deferral-based attribution from bytecode-based attribution. Its loop-top bias handling is an implemented heuristic, not evidence that inferred per-line times are exact.
- **C2:** The [profiling package](https://github.com/plasma-umass/scalene/tree/master/scalene) separates CPU/memory collection, signal management, statistics, accelerator integrations, and rendering. The CPU processor consumes an explicit statistics object and sample inputs, providing a concrete boundary for studying or testing attribution independently of collection and UI.

### [joerick/pyinstrument](https://github.com/joerick/pyinstrument)

**Language/role:** Python and C with a web renderer; in-process statistical wall-time profiler. Especially useful for request latency and asynchronous Python, where CPU-only samples answer a different question.

- **C1:** Its [sampling and async design](https://github.com/joerick/pyinstrument/blob/main/docs/how-it-works.md) explains interval-gated stack capture and attribution of time outside an async context to the `await` that suspended it. Context inheritance and strict-mode behavior expose subtle attribution semantics.
- **C4:** The [embedded changelog](https://github.com/joerick/pyinstrument#changelog) spans earlier profiling/session changes through dated 2024–2026 releases, including async support, C-extension leak fixes, start/stop mismatch handling, bounded HTML sample output, and expanded interpreter wheel coverage. This is evidence of compatibility and complexity management, not just an old repository date.

### [rbspy/rbspy](https://github.com/rbspy/rbspy)

**Language/role:** Rust; external Ruby sampler usable as a CLI and library. Study how version-dependent runtime inspection can remain behind a compact public operation.

- **C1:** The [architecture document](https://github.com/rbspy/rbspy/blob/main/ARCHITECTURE.md) traces Ruby-version detection, symbol-based or BSS-heuristic thread discovery, and validation of candidate thread structures. Stack extraction requires different layouts and behaviors across Ruby versions.
- **C2:** `RubySpy::new` and stack-trace retrieval hide version dispatch and platform details. Generated bindings and shared macros isolate differences instead of duplicating the entire collector. The [new-Ruby-version checklist](https://github.com/rbspy/rbspy/blob/main/NEW_RUBY_VERSION_CHECKLIST.md) is a second entry point into how that abstraction is maintained; the repository explicitly warns that its library API is not yet stable.

### [tmm1/stackprof](https://github.com/tmm1/stackprof)

**Language/role:** C extension and Ruby; in-process CPU, wall-time, allocation, and custom sampling. Contrast its VM-cooperating design with rbspy's external memory inspection.

- **C1:** The [sampling design](https://github.com/tmm1/stackprof#sampling) explains postponing sampling work so interrupted GC or inconsistent VM state is not inspected unsafely. The [native implementation](https://github.com/tmm1/stackprof/blob/master/ext/stackprof/stackprof.c) includes atomic running-state access, compatibility paths for postponed jobs, and explicit GC sample bookkeeping.
- **C3:** Allocation-free stack capture and native aggregation into frame, line, and call-edge counts constrain per-sample work. Raw sample storage is optional, so users can trade detailed reconstruction against the cost of retaining every sample. These choices are visible in the same extension rather than hidden behind a feature list.

### [adsr/phpspy](https://github.com/adsr/phpspy)

**Language/role:** C; external PHP sampling for CLI, Apache, and FPM. The documented scope is non-ZTS PHP on Linux; architecture support has explicit limitations.

- **C1:** The [stack reader](https://github.com/adsr/phpspy/blob/master/phpspy_trace.c) checks remote-memory reads, bounds stack walking, distinguishes internal and user functions, and controls whether an errored sample is completed. These are concrete defenses against incomplete or changing target state.
- **C2:** Collection emits stack-begin, frame, and stack-end events through an event-handler interface. [Version-specific instantiation](https://github.com/adsr/phpspy/blob/master/phpspy_trace_tpl.c) maps common traversal code onto different Zend structures. Together these separate runtime layout, collection, and output without making each output format a separate sampler.

### [reliforp/reli-prof](https://github.com/reliforp/reli-prof)

**Language/role:** PHP with FFI; external PHP sampler and VM inspector. The inspected default branch was `0.13.x`. Focus on sampling and its trace format; the repository's broader heap-inspection features are not needed to justify inclusion.

- **C1:** The [binary trace specification](https://github.com/reliforp/reli-prof/blob/0.13.x/docs/tracing/binary-trace-format.md) defines segment-local IDs, definition-before-use ordering, length-delimited events, reserved boundary markers, and recovery after incomplete writes. It is explicitly marked draft.
- **C3:** String/frame/stack interning and run-length encoding of repeated stacks reduce the cost of long-running capture. Independently decodable segments support rotation and conversion without requiring a monolithic in-memory trace. The same [format document](https://github.com/reliforp/reli-prof/blob/0.13.x/docs/tracing/binary-trace-format.md) provides a particularly accessible case study in trading compactness against streaming and recovery requirements.

## Native libraries and operating-system sampling tools

### [torvalds/linux](https://github.com/torvalds/linux)

**Language/role:** C; specifically `tools/perf`, its supporting libraries, and the kernel perf-event interface. The Linux monorepo is counted once; unrelated kernel subsystems are outside scope.

- **C1:** The [perf ring-buffer design](https://github.com/torvalds/linux/blob/master/Documentation/userspace-api/perf_ring_buffer.rst) details producer/consumer ownership, overflow behavior, per-CPU versus per-thread operation, and the memory barriers needed before publishing or reclaiming data.
- **C2:** The [perf-record reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-record.txt) exposes a shared collection framework across hardware/software events, processes, CPUs, call-graph strategies, and filters.
- **C3:** Memory-mapped buffers, asynchronous transfer, configurable buffer sizes, and acquire/release optimizations directly address sample throughput and observer overhead. The ring-buffer document connects those performance choices to their correctness requirements.

### [mstange/samply](https://github.com/mstange/samply)

**Language/role:** Rust; cross-platform command-line sampler using Firefox Profiler for visualization. The repository also contains reusable symbolication and processed-profile crates.

- **C2:** The [symbolication API](https://github.com/mstange/samply/blob/main/API.md) is reused through `wholesym`, samply's local server, and Firefox integration. It identifies modules with debug IDs and supports inline frames, source, and assembly, bridging platform collectors with a common analysis interface.
- **C3:** The [symbol library's design](https://github.com/mstange/samply/blob/main/samply-symbols/src/lib.rs) explicitly targets large binaries and large address batches without an expensive preprocessing step. State machines separate parsing from file access so native and WebAssembly callers can supply their own I/O; best-effort symbol lookup supports incomplete artifacts. This is a concrete performance architecture behind the standalone sampler.

### [gperftools/gperftools](https://github.com/gperftools/gperftools)

**Language/role:** C++; specifically the CPU profiler (`libprofiler`), not the allocator as a whole. A compact foundational implementation for studying aggregation inside asynchronous sampling paths.

- **C1:** [ProfileData](https://github.com/gperftools/gperftools/blob/master/src/profiledata.cc) explicitly distinguishes asynchronous-signal safety from reentrancy, bounds stack depth and eviction-buffer use, and handles interrupted/partial writes. Its lifecycle keeps output state and accumulated samples coordinated.
- **C3:** A fixed-size associative hash table combines repeated stacks; least-count entries are evicted into a preallocated output buffer. This makes allocation and I/O costs visible and bounded structurally. The [CPU profiling guide](https://github.com/gperftools/gperftools/blob/master/docs/cpuprofile.adoc) connects the collector to its linking, activation, and analysis interface.

### [tikv/pprof-rs](https://github.com/tikv/pprof-rs)

**Language/role:** Rust; embeddable CPU sampling library with guard-based lifetime management and report generation. Useful for studying the limits of Rust's guarantees when interacting with native unwinders and signals.

- **C1:** The repository's signal-safety discussion explains avoiding blocking lock acquisition during `SIGPROF`, preallocation, and known unwinder hazards. The [profiler implementation](https://github.com/tikv/pprof-rs/blob/master/src/profiler.rs) also explains why alternate signal stacks only make sense with a compatible unwinder. Inclusion does not imply its unwinding is universally signal-safe.
- **C3:** The [collector](https://github.com/tikv/pprof-rs/blob/master/src/collector.rs) uses fixed-associativity buckets and buffered spill to a temporary file; generic counters separate sample accumulation from later iteration/reporting. Embedded tests exercise counter behavior. This is substantive sampler code, not merely a wrapper around an external profiler command.

### [microsoft/perfview](https://github.com/microsoft/perfview)

**Language/role:** Primarily C# with native helpers; Windows CPU/memory profiling and the reusable TraceEvent library. Focus on sampled CPU stacks, event collection, and symbol resolution rather than treating every event-analysis feature as sampling.

- **C1:** The [TraceEvent programmer's guide](https://github.com/microsoft/perfview/blob/main/documentation/TraceEvent/TraceEventProgrammersGuide.md) explains lost asynchronous events, broken stack walks, module-load tracking, JIT method ranges, and the multi-stage process of recovering symbols. Missing metadata cannot simply be repaired by a nicer viewer.
- **C2:** Session, provider, consumer, parsed-event, and `TraceLog` abstractions support reusable analysis outside the GUI. The [TraceEvent documentation subtree](https://github.com/microsoft/perfview/tree/main/documentation/TraceEvent) leads from collection to stack and symbol APIs. The repository explicitly supports analysis of historical traces and older target runtimes even though current collection has newer platform requirements.

### [VerySleepy/verysleepy](https://github.com/VerySleepy/verysleepy)

**Language/role:** C++ with wxWidgets; Windows sampling profiler. The README identifies this former fork as the official repository. Treat it as a long-evolved code-study project; the latest numbered release listed in the inspected history is 0.91 from 2021, with 0.92 described as under development.

- **C1:** The [sampler](https://github.com/VerySleepy/verysleepy/blob/master/src/profiler/profiler.cpp) coordinates suspension, register capture, resumption after failures, WoW64 contexts, and imperfect Windows stack-walking metadata. Comments explain troublesome import thunks and why correction heuristics exist.
- **C4:** The [release history](https://github.com/VerySleepy/verysleepy#history) documents 2013–2021 work on late symbol loading, file-format/database changes, 64-bit fixes, MinGW symbol support, many-thread behavior, symbol cleanup, and CI. This supports sustained compatibility work without implying a current rapid release cadence.

### [Donpedro13/etwprof](https://github.com/Donpedro13/etwprof)

**Language/role:** C++; focused Windows ETW sampling recorder producing ETL files for external analysis. A less widely known example of controlling recording volume while retaining enough context to symbolize samples. The inspected README lists version 0.3, released in April 2024.

- **C1:** Filtering must preserve relevant process/thread/module events as well as sampled stacks. The implementation tracks stack-key lifetimes and removes stale thread IDs when another process reuses them. A post-capture merge adds binary/PDB identification metadata that kernel events alone do not supply. The [theory of operation](https://github.com/Donpedro13/etwprof/blob/master/Documentation/Theory_of_operation.md) explains the pipeline.
- **C3:** A real-time kernel session feeds `TraceRelogger`, which filters before writing ETL rather than retaining a complete system-wide trace. Study the implementation boundary in [ProfilerCommon.cpp](https://github.com/Donpedro13/etwprof/blob/master/Sources/etwprof/Profiler/ProfilerCommon.cpp), where event relevance is decided.

### [google/orbit](https://github.com/google/orbit)

**Language/role:** C++; native sampling plus dynamic instrumentation and an interactive analysis UI. **Historical: archived on 2025-01-31**, and the README states that Google engineers no longer maintain it. Its substantive source remains available; it is not a migration-only placeholder.

- **C1:** The [perf-event processor](https://github.com/google/orbit/blob/main/src/LinuxTracing/PerfEventProcessor.cpp) delays processing to accommodate out-of-order arrival, enforces monotonic processing timestamps, and turns late events into explicit discarded-time ranges. It coalesces repeated discard coverage instead of emitting an event for every loss.
- **C2:** The [LinuxTracing subsystem](https://github.com/google/orbit/tree/main/src/LinuxTracing) separates event queues, visitors, context switches, memory maps, and unwinding. Numerous colocated tests cover event ordering and unwind scenarios. Study this subsystem as an architecture for joining sampling and scheduling data, without counting historical forks as additional projects.

## Statistical allocation profiling

### [janestreet/memtrace](https://github.com/janestreet/memtrace)

**Language/role:** OCaml; streaming client for the runtime's statistical memory profiler. Included because its inputs are sampled allocations with backtraces and tracked lifetimes, not an exhaustive allocation trace. The sampling engine itself belongs to OCaml's `Gc.Memprof`; this repository supplies the tracing/encoding layer.

- **C1:** Allocation, promotion, and collection events must retain object identity, and the compressed stream must contain enough information for the decoder to reconstruct evolving cache state. The [internal design](https://github.com/janestreet/memtrace/blob/master/docs/internal.md) also explains why per-word sampling and combined allocations complicate attribution.
- **C3:** A bounded skewed-associative backtrace cache, prediction of successive frames, packed fields, and inline debug information reduce trace size without depending on the original executable at analysis time. The same design document distinguishes runtime sampling mechanisms from Memtrace's compact serialization techniques, making it a useful complement to CPU samplers.

## Search coverage and limitations

Discovery used sixteen distinct query formulations across general sampling profilers, Linux native collection, eBPF continuous profiling, Python external and in-process profilers, Ruby/PHP VM inspection, Windows/.NET/ETW, HPC call-path profiling, OCaml allocation profiling, and embedded Rust samplers. Later searches also looked for less prominent native and continuous collectors. They added pprof-rs, CPA, and etwprof; the final cross-runtime queries mostly returned already examined projects, forks, wrappers, and viewers. The list is a curated selection, not a complete ecosystem census.

Every retained canonical GitHub repository was opened, and at least one separate primary design document or implementation file was read. Source-tree indexes were used to locate relevant code; a directory listing or a second copy of the root README alone was not treated as sufficient implementation evidence. Public GitHub HTML and raw source reads supplemented live web search when API rate limits or web-page retrieval failed. No candidate code was executed and no dependencies were installed. Source links target the branches inspected on the research date and can change subsequently.

Important scope choices:

- [HPCToolkit's GitHub repository](https://github.com/HPCToolkit/hpctoolkit) was excluded because its archived default branch is a migration notice directing development to GitLab, rather than an official maintained substantive GitHub mirror. Consequently, this report's HPC-specific coverage is limited.
- Standalone profile viewers and format converters, such as Speedscope and pprof, were not separately counted. Nor were generic instrumentation-only tracers, benchmark harnesses, tutorial samplers, or launcher-only integrations. A profiler using one of these components can still qualify through its own collection or storage implementation.
- gProfiler's included samplers are not presented as new independent implementations; its selection rests on merging and metadata semantics. Likewise, Parca Agent's relationship to the OpenTelemetry unwinder is explicit. Linux and gperftools are counted once each with their relevant subsystems identified.
- Operating-system permissions, runtime versions, sampling bias, incomplete stacks, and dropped data affect practical suitability. No numerical overhead claims were independently benchmarked or adopted as quality evidence. Except where dated history supports C4, no maintenance or longevity conclusion is inferred from stars, creation dates, or recent pushes.

The criterion judgments are engineering inferences from the linked mechanisms. They identify productive reading paths and hard problems being addressed; they do not certify the absence of bugs or make all collection modes equivalent.
