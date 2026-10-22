# Kernel tracing and runtime observability tools

Date of research: **2026-10-09**.

This report selects 26 GitHub repositories for studying how kernel and runtime events are captured, transported, correlated, and analyzed. It covers Linux tracing infrastructure, programmable tracers, application instrumentation, container observability, packet tracing, continuous profiling, trace analysis, and Windows ETW. Libraries qualify when they implement a substantial part of that tracing path. Linux's relevant subsystems are counted together; separately implemented LTTng components are identified individually.

The criteria below are engineering judgments grounded in the linked primary material, not assertions that every component has exemplary code or that a project has been independently audited. Repository identities were checked through GitHub pages or its API, and each entry includes additional documentation or implementation evidence. Links describe the inspected revision or documentation version; they do not promise future compatibility or maintenance.

## Criteria legend

- **C1 — Difficult correctness:** concurrency, invariants, numerical semantics, hostile or malformed input, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or machinery applicable to multiple tracing and analysis tasks.
- **C3 — Performance with structure:** explicit resource or throughput constraints addressed through an understandable architecture.
- **C4 — Sustained evolution:** multi-year change history accompanied by compatibility, testing, or complexity-management evidence.

## Linux tracing infrastructure and execution capture

### 1. [torvalds/linux](https://github.com/torvalds/linux)

**Language/role:** C and architecture assembly; specifically the tracing ring buffer, ftrace infrastructure, and `tools/perf`, not the entire kernel as an undifferentiated recommendation. Study the producer/consumer contract underlying many tools in this report.

- **C1:** The tracing buffer distinguishes reserved writes from fully committed writes. Interrupting writers nest like a stack, and the outermost writer controls full commitment; readers must not observe incomplete records. The [lockless ring-buffer design](https://docs.kernel.org/trace/ring-buffer-design.html) explains these invariants and page ownership in detail.
- **C3:** Per-CPU buffers, reader-page exchanges, and selectable overwrite versus producer/consumer behavior expose explicit throughput and data-loss tradeoffs in that design.
- **C2:** The [perf-trace manual](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-trace.txt) shows a common frontend for syscall, fault, scheduler, and other tracepoint events, including recorded-data analysis and call-chain collection.

### 2. [strace/strace](https://github.com/strace/strace)

**Language/role:** C; syscall and signal tracing through `ptrace`. Especially useful for engineers studying process-state machines and the practical burden of decoding operating-system ABIs.

- **C1:** The [internals guide](https://github.com/strace/strace/blob/master/doc/INTERNALS.md) explains attach/seize differences, fork and clone tracking, syscall entry/exit state, and per-tracee control blocks. Correctness depends on interpreting stops and resuming the right thread with the right signal semantics.
- **C2:** Architecture-specific register acquisition feeds a shared event dispatcher and decoder machinery, separating process control from the interpretation of individual syscalls.
- **C4:** The [NEWS history](https://github.com/strace/strace/blob/master/NEWS) spans multiple years of syscall and ioctl additions, ABI updates, and decoder repairs. Recent entries include limiting nested netlink errors and handling oversized declared response lengths: concrete evidence of compatibility and malformed-input work, rather than age alone.

### 3. [rostedt/trace-cmd](https://github.com/rostedt/trace-cmd)

**Language/role:** C; ftrace recording and the `libtracecmd` trace-file API. This is the maintainer's substantive GitHub mirror; the [README](https://github.com/rostedt/trace-cmd/blob/master/README) identifies kernel.org as the official upstream. Mirror availability should not be confused with the upstream review location.

- **C1:** The [iteration API](https://github.com/rostedt/trace-cmd/blob/master/Documentation/libtracecmd/libtracecmd-iterate.txt) documents timestamp ordering, missed-event callbacks, and synchronization metadata for host/guest traces. Its distinction between an iteration's logical CPU index and the record's actual CPU is a useful example of an easily misused API invariant.
- **C2:** Single-file and multi-file iterators, event-specific callbacks, filters, and missed-event reporting let analysis applications reuse the trace decoding and traversal machinery.

Study this repository when the question is how raw ftrace output becomes a consumable trace artifact with explicit ordering and loss semantics.

### 4. [namhyung/uftrace](https://github.com/namhyung/uftrace)

**Language/role:** C with assembly and scripting support; function tracing that combines user functions, library calls, kernel functions, and system events. Study instrumentation at the boundary between executable code and a trace recorder.

- **C1:** The [recording manual](https://github.com/namhyung/uftrace/blob/master/doc/uftrace-record.md) explains that normal return tracing modifies execution-stack return addresses. Its entry-only alternative estimates return time when that interference is unsuitable; the same manual documents concurrent first-access problems in dynamic symbol binding.
- **C3:** Separate user/kernel buffer sizing, recording threads, depth limits, and record-time function filters directly address trace volume and collection overhead.
- **C2:** The [repository overview](https://github.com/namhyung/uftrace/blob/master/README.md) describes multiple capture mechanisms feeding common record, replay, report, graph, and scripting operations. This makes the code useful beyond a single instrumentation technique.

## Programmable tracing languages and toolkits

### 5. [iovisor/bcc](https://github.com/iovisor/bcc)

**Language/role:** C/C++ compilation and loading infrastructure, with Python and other frontends; a toolkit for building kernel and runtime observability programs. Study how a reusable tracing substrate supports many small operational tools.

- **C2:** The [API reference](https://github.com/iovisor/bcc/blob/master/docs/reference_guide.md) exposes probe attachment, USDT integration, maps, stack collection, and event transport through consistent C-side and userspace interfaces.
- **C1:** The reference distinguishes per-CPU map copies, which are not mutually synchronized, from shared state, and documents memory-access and verifier constraints. Choosing the right map semantics is part of measurement correctness.
- **C3:** The [project overview](https://github.com/iovisor/bcc/blob/master/README.md) demonstrates in-kernel histogram aggregation with only summaries returned to userspace. The codebase also contains both the original toolkit and `libbpf-tools`; those are one repository here.

### 6. [bpftrace/bpftrace](https://github.com/bpftrace/bpftrace)

**Language/role:** C++; a high-level tracing language compiled through LLVM and attached to Linux BPF hooks. Study the translation from concise probe programs into constrained kernel execution and userspace output.

- **C2:** The [language documentation, version 0.24](https://bpftrace.org/docs/release_024/language) describes probe/predicate/action blocks and shared language constructs across kernel probes, user probes, tracepoints, and typed argument access.
- **C1:** That documentation makes architecture-dependent register arguments, bounded string reads, type restrictions, and missing-probe behavior explicit. These are semantic constraints a tracing compiler must preserve.
- **C3:** The same guide explains stack-versus-preallocated object storage, per-CPU output-buffer sizing, symbol-cache policies under ASLR, and map/probe limits. These connect resource limits to observable failure modes rather than merely claiming low overhead.

The linked language version is intentional; the repository has newer development and documentation versions.

### 7. [iovisor/ply](https://github.com/iovisor/ply)

**Language/role:** C; a small BPF tracing language with libc as its required runtime dependency. Its [README](https://github.com/iovisor/ply/blob/master/README.md) explicitly designates this IO Visor repository as the official destination. GitHub records a fork relationship to `wkz/ply`; the two are not counted independently.

- **C1:** The [compiler implementation](https://github.com/iovisor/ply/blob/master/src/libply/compile.c) performs symbol allocation, iterative rewriting and type inference, explicit type validation, IR generation, and BPF generation. Error propagation and unresolved types provide concrete correctness concerns in a compact compiler.
- **C2:** Provider hooks and builtin-function hooks participate in common compilation passes, allowing different probe sources to share the frontend and backend machinery.

This is a useful smaller study target alongside LLVM-based tracers. The README also describes cross-compilation and QEMU-based tests for supported architectures; no claim of feature parity with BCC or bpftrace is intended.

### 8. [oracle/dtrace](https://github.com/oracle/dtrace)

**Language/role:** C; Oracle's official Linux DTrace implementation. The former `oracle/dtrace-utils` location redirects here. Study how DTrace's language and provider model are implemented on a BPF backend.

- **C1:** The [code generator](https://github.com/oracle/dtrace/blob/devel/libdtrace/dt_cg.c) translates CTF type sizes and bit fields into legal BPF loads, and spells out trampoline register and context invariants. This is substantive compiler and ABI work.
- **C2:** Generic trampoline generation separates the execution context used by D clauses from individual kernel probe attachment, while shared IR and register-management machinery supports the generated programs.
- **Compatibility context:** The [README](https://github.com/oracle/dtrace/blob/devel/README.md) documents supported Oracle Linux generations, deprecated older builds, testing, and previous releases. These are useful compatibility-management entry points; the selection criteria here are C1 and C2.

The entry points use the verified `devel` branch; historical design notes elsewhere in the repository should not automatically be treated as the current implementation.

## LTTng capture and control components

### 9. [lttng/lttng-modules](https://github.com/lttng/lttng-modules)

**Language/role:** C; LTTng's Linux kernel instrumentation and buffering, in an explicitly identified official GitHub mirror. Study a separate high-throughput tracing design rather than assuming it shares ftrace's buffer implementation.

- **C1:** The [ring-buffer frontend](https://github.com/lttng/lttng-modules/blob/master/src/lib/ringbuffer/ring_buffer_frontend.c) documents synchronization, complete-subbuffer checks, memory-ordering requirements, CPU-hotplug protection, and reset restrictions. It distinguishes approximate polling from the barriers needed for actual consumption.
- **C3:** Producer/consumer and overwrite modes, per-CPU state, and subbuffer transfer through splice make the data path and its resource choices inspectable.
- **C4:** The [ChangeLog](https://github.com/lttng/lttng-modules/blob/master/ChangeLog) contains releases across many years, distribution-kernel adaptations, tracepoint signature changes, ABI refactoring, and tests. This is direct evidence of managing an out-of-tree tracer against evolving kernel interfaces.

### 10. [lttng/lttng-ust](https://github.com/lttng/lttng-ust)

**Language/role:** C; application and library instrumentation, with language agents. This is an official GitHub mirror. Study safe runtime registration of probes in a process whose threads and shared libraries continue executing.

- **C1:** The [tracepoint implementation](https://github.com/lttng/lttng-ust/blob/master/src/lib/lttng-ust-tracepoint/tracepoint.c) specifies mutex nesting, fork/clone assumptions, callsite references, and RCU-delayed reclamation of replaced probe arrays. These are explicit lifetime and synchronization contracts.
- **C2:** The [instrumentation API manual](https://github.com/lttng/lttng-ust/blob/master/doc/man/lttng-ust.3.txt) defines reusable providers, typed event fields, tracepoints, and simpler logging interfaces for instrumented applications.

This component earns a separate entry from the kernel modules because its central problems are userspace linkage, concurrent callsites, and probe-provider lifecycle. It is not another frontend around the same kernel implementation.

### 11. [lttng/lttng-tools](https://github.com/lttng/lttng-tools)

**Language/role:** C/C++; tracing sessions, consumer and relay daemons, and a control library. This is an official GitHub mirror; upstream is on git.lttng.org and review primarily uses LTTng Review.

- **C1:** The [relay-daemon architecture](https://github.com/lttng/lttng-tools/blob/master/doc/relayd-architecture.md) explains connection/session/trace/stream ownership, RCU lookup combined with reference acquisition, lock ordering, and destruction after disconnect. It is an unusually concrete guide to concurrent object lifetime.
- **C2:** The [component overview](https://github.com/lttng/lttng-tools/blob/master/README.adoc) separates the control API and session registry from data consumers, network relaying, and crash-buffer recovery.
- **C3:** The relay design uses indexed tables for protocol identifiers and limits RCU read-side sections while reference counts protect objects returned to callers.

Read this entry for the control and transport plane of tracing, complementing the two recording libraries above.

## Runtime observability, security sensors, and profiling

### 12. [inspektor-gadget/inspektor-gadget](https://github.com/inspektor-gadget/inspektor-gadget)

**Language/role:** Go and eBPF C, with optional WebAssembly processing; a framework for host and Kubernetes inspection. Study packaging and execution of independently developed tracing programs.

- **C2:** The [current gadget introduction](https://github.com/inspektor-gadget/inspektor-gadget/blob/main/docs/gadget-devel/gadget-intro.md) defines a gadget as an OCI image containing programs, metadata, and optional WASM modules. Multiple data sources can share a gadget.
- **C3:** Its data-source API distinguishes event streams transported through perf/BPF ring buffers from map iterators that expose accumulated statistics. This makes collection mode and data movement explicit architectural decisions.

The [containerized-gadget design](https://github.com/inspektor-gadget/inspektor-gadget/blob/main/docs/design/002-containerized-gadgets.md) explains the motivation for decoupling gadget releases from the framework. It contains historical proposals and unfinished details, so current behavior is grounded in the current gadget guide rather than inferred from every proposed command.

### 13. [cilium/tetragon](https://github.com/cilium/tetragon)

**Language/role:** eBPF C and Go; process observability, configurable kernel tracing, and optional runtime enforcement. Study how a policy representation controls work performed inside the kernel.

- **C2:** [TracingPolicy](https://github.com/cilium/tetragon/blob/main/docs/content/en/docs/concepts/tracing-policy/_index.md) combines hook points, selectors, and actions, and supports loading policies in Kubernetes or through non-Kubernetes interfaces. Policy domains separate those control sources.
- **C3:** [Event throttling](https://github.com/cilium/tetragon/blob/main/docs/content/en/docs/concepts/cgroup-rate.md) tracks cgroup activity per CPU and emits throttle transition events. The documented implementation currently applies this mechanism to base process-exec and process-exit events, an important scope limit.
- **C1:** The policy documentation explicitly calls out TOCTOU hazards in low-level tracing configuration. This makes the relationship between observed arguments, enforcement points, and process behavior a concrete study topic.

### 14. [aquasecurity/tracee](https://github.com/aquasecurity/tracee)

**Language/role:** Go and eBPF C; Linux runtime event collection, detection, and forensic capabilities. Study maintaining a typed event contract across kernel code, policy processing, and an external API.

- **C1:** The [event-development guide](https://github.com/aquasecurity/tracee/blob/main/docs/contributing/adding-events.md) requires consistent event IDs and layouts across BPF, Go metadata, protobuf definitions, and gRPC translation. Probe dependencies and argument decoding are part of the event definition, making mismatches a concrete correctness risk.
- **C2:** A common workflow connects new probe handlers to event metadata, policy filtering, serialization, and consumers; the [overview](https://github.com/aquasecurity/tracee/blob/main/docs/docs/overview.md) describes raw observations and detections within a unified event model.
- **C3:** The handler pattern applies scope filters before field extraction and submission, then permits field-based filtering, exposing where unnecessary work and event traffic can be avoided.

### 15. [falcosecurity/libs](https://github.com/falcosecurity/libs)

**Language/role:** C/C++; capture drivers, `libscap`, and `libsinsp`, used beneath Falco and other consumers. This entry covers the capture and inspection implementation rather than counting every dependent product separately.

- **C2:** The [architecture and layout](https://github.com/falcosecurity/libs/blob/master/README.md) separate kernel/eBPF drivers, raw capture and savefiles, machine-state enrichment, filtering, and plugin data sources. This is a reusable event-processing stack.
- **C1:** The [fuzzing documentation](https://github.com/falcosecurity/libs/blob/master/docs/fuzzing.md) identifies the raw-event decoder boundary and concrete malformed-input cases: excessive parameter counts, alternate parameter-length widths, and mixed or zero-length fields. The harness targets field-boundary decoding rather than only end-to-end happy paths.

The README additionally distinguishes architectures covered by driver CI from experimental ones. This is useful testing evidence, without claiming that the presence of CI or a fuzzer establishes complete coverage.

### 16. [pixie-io/pixie](https://github.com/pixie-io/pixie)

**Language/role:** C++, Go, and eBPF C; Kubernetes application observability. Relevant subsystems are kernel/userspace capture and the Pixie Edge Module data pipeline, with the larger monorepo counted once.

- **C2:** The [eBPF architecture guide](https://docs.px.dev/about-pixie/pixie-ebpf/) explains how syscall probes feed protocol parsing and queryable tables, TLS-library uprobes capture data at a different boundary, and generated tracing programs feed the same analysis environment.
- **C3:** CPU profiling uses sampling, while protocol collection and parsing are divided between probes and the userspace Edge Module. These are concrete ways to constrain work performed in probes; no universal overhead percentage is assumed here.

The [repository overview](https://github.com/pixie-io/pixie/blob/main/README.md) connects those mechanisms to query scripting and local cluster data processing. Study the conversion from low-level observations to application-level records, and treat support for individual protocols and runtime versions as separate compatibility questions.

### 17. [open-telemetry/opentelemetry-ebpf-profiler](https://github.com/open-telemetry/opentelemetry-ebpf-profiler)

**Language/role:** Go, eBPF C, and supporting native code; host-wide continuous profiling across native, interpreted, and JIT-compiled runtimes. Study unwinding when an application cannot simply supply a conventional frame-pointer chain.

- **C1:** The [internals document](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/blob/main/doc/internals.md) describes selecting runtime-specific unwinders, tracking executable mappings, and converting BPF frames into userspace representations. File identity and mapping lifetime are central to correct attribution.
- **C3:** Trace hashing and conversion caches avoid repeatedly enriching identical stacks; compressed reporting and shorter kernel-side identifiers address bandwidth and kernel-memory costs. The document also explicitly permits reporting loss, rather than promising reliable delivery.
- **C2:** Interpreter handlers, the process manager, tracer, and reporter form reusable boundaries for adding runtime support.

The [README](https://github.com/open-telemetry/opentelemetry-ebpf-profiler/blob/main/README.md) records kernel-support transitions. The internals document warns that components can change, so its historical backend details should be read with the current code.

### 18. [cloudflare/ebpf_exporter](https://github.com/cloudflare/ebpf_exporter)

**Language/role:** Go and eBPF C; custom kernel measurements exported as Prometheus metrics and OpenTelemetry traces. Study numerical and binary-layout semantics at the kernel-to-monitoring-system boundary.

- **C1:** The [histogram transformation implementation](https://github.com/cloudflare/ebpf_exporter/blob/master/exporter/histogram.go) fills missing buckets, produces cumulative counts, transforms bucket boundaries, and handles optional sums. Sparse kernel maps cannot be published directly as correct Prometheus histograms.
- **C2:** The [configuration documentation](https://github.com/cloudflare/ebpf_exporter/blob/master/README.md) separates metric definitions, compiled programs, label decoders, and binary-map layouts, allowing the exporter to serve many kernel measurements.
- **C3:** Measurements can accumulate in kernel maps before userspace collection, reducing the need to export each observed event.

The similarly named `monitoring-projects/ebpf-exporter` was checked and is a fork of this project; it is not a second selection.

## Packet identity and network-stack tracing

### 19. [cilium/pwru](https://github.com/cilium/pwru)

**Language/role:** Go and eBPF C; tracing packets through Linux kernel functions and BPF network programs. Study the difference between following a packet's identity and repeatedly applying a filter to its changing contents.

- **C1:** The [usage documentation](https://github.com/cilium/pwru/blob/main/README.md) covers following packets after NAT or decapsulation, stack-based tracking, and XDP/TC tracing. Packet transformation and object lifetime make correlation more difficult than a simple address match.
- **C3:** The [BPF implementation](https://github.com/cilium/pwru/blob/main/bpf/kprobe_pwru.c) uses bounded queues/maps and per-CPU scratch storage. Its XDP entry/exit coordination remembers whether a packet passed the entry filter before later tracking it as an skb.
- **C2:** Multiple probe backends and configurable metadata extraction reuse common event and filtering structures.

The README ties particular backends and output features to kernel requirements, making it a useful starting point for compatibility investigation.

### 20. [retis-org/retis](https://github.com/retis-org/retis)

**Language/role:** Rust and eBPF C; packet tracing with Linux, Netfilter, conntrack, and Open vSwitch context. Study an extensible event model for reconstructing a packet journey.

- **C2:** The [collector design](https://github.com/retis-org/retis/blob/main/docs/collectors/overview.md) separates probe placement from optional data collectors and event sections. Explicitly requested collectors are mandatory, while automatically selected collectors can be skipped when prerequisites are absent.
- **C1:** [Tracking events](https://github.com/retis-org/retis/blob/main/docs/events/skb_tracking.md) distinguish a logical tracking ID from the skb address, including cloned objects sharing an ID. The collector guide also documents tracking-window termination when an skb is consumed and undefined behavior for nested ftrace tracking windows.

These limitations are useful evidence of the real correlation problem, not a reason to infer perfect packet reconstruction. Retis is a particularly useful Rust entry alongside the Go/C implementation in pwru.

## Trace transport, analysis, and visualization frameworks

### 21. [google/perfetto](https://github.com/google/perfetto)

**Language/role:** C++ with TypeScript UI and other support code; system tracing daemons, an instrumentation SDK, SQL analysis, and visualization. Relevant subsystems include ftrace collection and the core tracing service.

- **C1:** The [TraceBuffer design](https://github.com/google/perfetto/blob/main/docs/design-docs/trace-buffer.md) explains reconstructing packets from producer chunks, incomplete fragments and patches, per-writer ordering, and explicit loss reporting. It guarantees complete valid packets rather than exposing arbitrary partial buffer contents.
- **C3:** Shared-memory producer chunks feed a service-owned buffer; destructive reads, overwrite/discard modes, and bounded read batches expose the throughput and IPC tradeoffs.
- **C2:** Producer/writer sequences and data sources support many instrumented processes and collection modes through the same service.

The [contribution guide](https://github.com/google/perfetto/blob/main/docs/contributing/getting-started.md) states that primary development moved from Android Gerrit to GitHub in March 2025; this is no longer merely the old GitHub mirror.

### 22. [efficios/babeltrace](https://github.com/efficios/babeltrace)

**Language/role:** C/C++ with a C API and Python bindings; trace processing and Common Trace Format support. This is EfficiOS's official GitHub mirror; upstream development and review also use EfficiOS/LTTng infrastructure.

- **C2:** The [API architecture](https://github.com/efficios/babeltrace/blob/master/doc/api/libbabeltrace2/dox/main-page.dox) defines source, filter, and sink component classes assembled into graphs, with ports and message iterators. CTF readers and live-session consumers become components rather than special-purpose applications.
- **C1:** The [API fundamentals](https://github.com/efficios/babeltrace/blob/master/doc/api/libbabeltrace2/dox/api-fund.dox) distinguish borrowed, shared, and unique objects and specify pre/postconditions and object-state restrictions. These contracts matter when plugins exchange reference-counted events and metadata.
- **C3:** Expensive checks on processing hot paths are separated into developer mode, making the safety-versus-throughput choice explicit.

Study Babeltrace for a reusable analysis engine beneath frontends, rather than as a kernel event producer itself.

### 23. [eclipse-tracecompass/org.eclipse.tracecompass](https://github.com/eclipse-tracecompass/org.eclipse.tracecompass)

**Language/role:** Java; a trace-analysis framework and application, including LTTng kernel analysis and CTF reading. The old `tracecompass/tracecompass` mirror is archived and is not counted.

- **C2:** The [developer guide](https://github.com/eclipse-tracecompass/org.eclipse.tracecompass/blob/master/doc/org.eclipse.tracecompass.doc.dev/doc/Developer-Guide.mediawiki) separates event-driven state providers from querying and visualization. Its scheduler example converts `sched_switch` events into CPU-state histories.
- **C3:** The same guide describes persistent history-tree storage versus in-memory history and their disk, memory, and query tradeoffs. This provides substantial architecture beyond a graphical trace viewer.
- **C1:** Numerical state-system queries have explicit semantics: averages weight values by interval duration, while null handling differs between averaging and extrema.

The [API policy](https://github.com/eclipse-tracecompass/org.eclipse.tracecompass/blob/master/API_POLICY.md) additionally documents deprecation and retention expectations. Some developer-guide sections discuss unavailable or experimental backends; the selection does not assume those work as production features.

## Windows kernel and runtime telemetry

### 24. [microsoft/perfview](https://github.com/microsoft/perfview)

**Language/role:** C# with native support; performance analysis and the reusable TraceEvent library for ETW and runtime traces. Counted once, including the library subsystem.

- **C2:** The [TraceEvent programmer's guide](https://github.com/microsoft/perfview/blob/main/documentation/TraceEvent/TraceEventProgrammersGuide.md) separates session control, raw sources, provider-specific parsers, and typed callbacks. Kernel, CLR, and dynamically described events can share that pipeline.
- **C1:** Callback event objects are reused. Retaining one after its callback requires cloning it or copying its fields; otherwise later events can overwrite the observed data.
- **C3:** That same ownership rule enables the scanning loop to reuse objects and reduce allocation. The guide explains the cost of cloning versus selectively copying needed fields.

This repository is especially valuable for studying APIs where a deliberate performance optimization creates a strict consumer-lifetime contract.

### 25. [microsoft/krabsetw](https://github.com/microsoft/krabsetw)

**Language/role:** C++ and C++/CLI; ETW session, provider, and event-consumption abstractions, also exposed to .NET. Although presented as a wrapper, it supplies a substantive reusable trace-consumption model.

- **C2:** The [guided API example](https://github.com/microsoft/krabsetw/blob/master/docs/KrabsExample.md) describes separate kernel/user trace types, provider registration, event filters, callbacks, and explicit start/stop lifecycle.
- **C3:** The [ETW primer](https://github.com/microsoft/krabsetw/blob/master/docs/EtwPrimer.md) explains the processing thread donated to each session and why callbacks must promptly hand work off: slow dequeuing can lose events. It also separates schema retrieval from field parsing.

Study this code when integrating native Windows telemetry into another application. The documentation contains version-dependent ETW details; this report relies on the architectural model rather than repeating historical limits or claimed event-rate numbers.

### 26. [rabbitstack/fibratus](https://github.com/rabbitstack/fibratus)

**Language/role:** Go with extensibility support; Windows runtime telemetry, forensic capture, and behavioral detection. Relevant here is its ETW ingestion and event-enrichment architecture, not the effectiveness of particular security rules.

- **C1:** The [architecture document](https://github.com/rabbitstack/fibratus/blob/master/docs/architecture.md) describes binary-record normalization, process snapshots, ancestry lookup, and callstack resolution. Preserving correspondence between event-time addresses and changing process/module state is a concrete correctness challenge inferred from those mechanisms.
- **C2:** Collection and enrichment feed a typed rule-expression pipeline, stateful event sequences, and multiple outputs. The [repository overview](https://github.com/rabbitstack/fibratus/blob/master/README.md) also describes capture files and Python filaments for independent analysis tooling.

This offers a useful comparison with PerfView and krabsetw: a full event-correlation application built on Windows kernel telemetry, rather than only a session-control or event-decoding library.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, including Linux eBPF tracing compilers; ftrace/perf/LTTng tools and official mirrors; Windows ETW consumers; Rust packet tracing; Kubernetes runtime sensors; continuous-profiler unwinding; lightweight and embedded tracers; kernel-metric exporters; CTF/state-system analysis; and alternative tracing ecosystems. Candidate identities, forks, redirects, branches, and implementation entry points were then checked through primary repositories and project documentation. Later searches increasingly repeated the retained families or produced narrower viewers, adapters, historical experiments, and tutorials; this is a substantial selection, not an exhaustive census.

The list spans C, C++, Go, Rust, Java, C#, assembly boundaries, Python interfaces, and optional WASM processing. It ranges from the compact ply compiler to kernel subsystems and large observability monorepos. Three LTTng repositories remain because recording in kernel context, concurrent userspace instrumentation, and session/relay control are separate substantive implementations. Falco's shared capture libraries are represented once rather than multiplying entries through dependent applications.

SystemTap was investigated but omitted because its [official contribution/source page](https://www.sourceware.org/systemtap/getinvolved.html) directs readers to Sourceware and a fallback GitLab mirror; an official substantive GitHub mirror was not established. Unrelated forks, generated wrappers, awesome lists, tracing demonstrations, and generic monitoring dashboards were excluded. The archived old Trace Compass mirror was replaced by its verified current repository. The IO Visor and personal ply trees, and the Cloudflare exporter and its discovered fork, were not counted separately.

Coverage is strongest for Linux and Windows. BSD/macOS-native tracing and bare-metal/RTOS tracing received less depth; the report should not be read as excluding worthwhile projects in those ecosystems. Read-only source inspection was performed, with no candidate builds, benchmarks, dependency installation, or runtime validation. C4 is used selectively where history and engineering practice were inspected; recent pushes or repository age alone were not treated as evidence. Numerical throughput claims from project marketing were not adopted.
