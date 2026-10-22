# Multimedia pipeline and transcoding frameworks

Research date: 2026-10-09.

This selection covers 22 GitHub repositories implementing reusable media graphs, transcoding backends, frame-processing environments, hardware pipeline APIs, and substantial packaging or job-orchestration stages. It includes file conversion and live processing. Packaging-only projects and application backends are identified explicitly. Each repository's canonical GitHub page and at least one additional primary implementation or architectural source were opened and inspected. The engineering study suggestions are grounded judgments about the cited material, not assurances that every component is exemplary.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, time or numerical semantics, malformed inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or composition models supporting multiple applications.
- **C3 — Performance:** concrete throughput, latency, memory, or hardware constraints addressed through identifiable architecture.
- **C4 — Evolution:** documented evolution over years accompanied by compatibility practices, testing, or complexity management. Age and popularity alone do not qualify.

## General-purpose native graphs and processing engines

### 1. [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg)

**Language/role:** C; codec, container, filtering, resampling, and transcoding libraries plus command-line applications. This is the project's official GitHub mirror; its primary development infrastructure is elsewhere.

Study how reusable media libraries become a concurrent end-to-end application without losing startup, buffering, and shutdown invariants.

- **C1:** The command-line scheduler documents a particularly instructive startup dependency: streams must initialize before mux headers, and an SDP description may require all headers before any media packets. It coordinates task readiness and delayed muxer startup around these constraints. **C3:** Demux, decode, filter, encode, and mux tasks exchange data through queues with buffering limits and explicit completion behavior. See the [scheduler interface and implementation commentary](https://ffmpeg.org/doxygen/trunk/ffmpeg__sched_8h.html).
- **C2:** The repository exposes distinct `libavcodec`, `libavformat`, `libavfilter`, `libswscale`, and `libswresample` libraries, supporting applications beyond the CLI.
- **C4:** The [dated API-change ledger](https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/APIchanges) records migrations and deprecations across 2018–2026, including evolving callback and packet guarantees. [FATE](https://ffmpeg.org/fate.html) supplies regression testing across architectures, operating systems, and compilers.

**Entry points:** scheduler documentation; API-change ledger.

### 2. [GStreamer/gstreamer](https://github.com/GStreamer/gstreamer)

**Language/role:** C/GObject; multimedia pipeline framework. The GitHub repository is an official mirror of the freedesktop.org GitLab monorepo. Its plugin and editing-service subprojects are counted here once.

Study the separation between graph composition and the shared temporal model required to make independently implemented elements cooperate.

- **C1:** Synchronization distinguishes clock time, buffer timestamps, and running time. Pausing, flushing seeks, segment clipping, and reverse playback require different transformations; timestamps cannot simply be treated as wall-clock deadlines. The [synchronization design](https://gstreamer.freedesktop.org/documentation/additional/design/synchronisation.html) describes these invariants and the conversion formulas.
- **C2:** Elements, pads, segment events, and selectable clocks provide a common contract for sources, processors, and sinks. The same design shows how a pipeline chooses an element-provided clock while each element interprets segments consistently. This is useful for studying extensibility that preserves system-wide semantics.

**Entry point:** synchronization design, then the corresponding core and plugin subprojects in the monorepo.

### 3. [gpac/gpac](https://github.com/gpac/gpac)

**Language/role:** C; multimedia framework with dynamically connected filters, packaging, playback, and processing tools.

Study automatic graph construction together with the lifecycle rules that make a mutable, multithreaded graph usable.

- **C2:** The [filter-session API](https://github.com/gpac/gpac/blob/master/include/gpac/filters.h) exposes registries, source/destination loading, capability-driven connection resolution, scheduler selection, and limits on automatically inserted filter chains. This is more substantial than a fixed command pipeline.
- **C1:** The same header distinguishes aborting from callbacks from stopping a session: calling the blocking stop operation inside a callback can deadlock. It also documents session locking around graph modifications and separate flush modes, including the risk of broken output when aborting without flushing. These contracts provide concrete examples of graph mutation and shutdown correctness.

**Entry point:** `include/gpac/filters.h`, especially session creation, connection resolution, locking, and abort/stop documentation.

### 4. [mltframework/mlt](https://github.com/mltframework/mlt)

**Language/role:** C/C++; media authoring and playback framework underlying editing and playout applications.

Study a small family of media-service abstractions that composes into both individual effects and timelines.

- **C2:** Producers, consumers, filters, and transitions are factory-created services; a playlist is itself a producer. That recursive arrangement allows timeline composition without introducing a separate execution model for every editing construct. See the [framework guide](https://www.mltframework.org/docs/framework/).
- **C1:** The guide makes ownership and teardown explicit: playlists retain producer references, callers release their own references, and threaded consumers must finish before destruction. Its normalization layer attaches conversion services in response to consumer requirements, exposing the interaction between requested output formats and upstream media processing.

**Entry point:** framework guide, particularly service factories, normalization, consumer lifetime, and playlists.

### 5. [BabitMF/bmf](https://github.com/BabitMF/bmf)

**Language/role:** C++ engine with Python and Go interfaces; programmable multimedia graphs with CPU and GPU modules.

Study how graph-level composition exposes device placement and data movement instead of hiding them behind a single transcoding call.

- **C2:** The [graph construction guide](https://babitmf.github.io/docs/bmf/getting_started_yourself/create_a_graph/) composes decoding, separate audio/video streams, and encoding before validating and running the graph. Modules and graph connections support custom processing workflows.
- **C3:** The [GPU transcoding guide](https://babitmf.github.io/docs/bmf/multiple_features/gpu_hardware_acc/gpu_transcoding/) distinguishes device-resident decoded frames from explicitly downloaded CPU frames. It explains CUDA input requirements for GPU encoders and demonstrates multiple encoders sharing one decoder. The engineering interest is avoiding redundant decode work and host/device transfers, not an unsupported speedup figure.

**Entry points:** graph construction; GPU transcoding and frame-transfer examples.

## Actor, clock, and live-media architectures

### 6. [membraneframework/membrane_core](https://github.com/membraneframework/membrane_core)

**Language/role:** Elixir/BEAM; pipeline and element runtime for multimedia processing.

Study backpressure as an explicit protocol between independently scheduled components.

- **C2:** Elements and pads provide reusable composition boundaries; demand can be expressed in buffers, bytes, or timestamp-based units. Plugins supply concrete codecs, transports, and processing stages around the core framework.
- **C1:** The [manual-demand guide](https://membrane-core.hexdocs.pm/manual_demands.html) specifies that new demand replaces rather than increments the pending request, and callbacks receive total outstanding demand. Timestamp-based demand requires monotonic timestamps, making DTS preferable to reordered PTS in relevant streams. It also explains how redemanding from the wrong callback can repeatedly schedule work and starve the mailbox. These are precise safety and liveness constraints, not merely an asynchronous API.

**Entry point:** manual-demand guide, including source versus filter redemand behavior.

### 7. [savonet/liquidsoap](https://github.com/savonet/liquidsoap)

**Language/role:** OCaml implementation and a streaming DSL; programmable audio/video source composition and output pipelines.

Study clock domains as both a correctness boundary and a scheduling boundary.

- **C1:** The [clock architecture documentation](https://www.liquidsoap.info/doc-dev/clocks.html) explains conflicts between independent synchronization sources, crossfade lookahead, and drift between devices. Buffers decouple clock domains and can isolate a recording path from a stalled network output; adaptive buffering carries its own signal-quality tradeoffs.
- **C2:** Composable sources and operators share a clock-assignment model, letting the same framework express playback, transitions, recording, and network output.
- **C3:** Outputs sharing a clock may perform encoding sequentially. The documentation explains how assigning separate clocks and buffering between them enables parallel execution. This makes scheduling costs visible in the composition model.

**Entry point:** clock architecture documentation. The cited page is the development documentation, so details should be checked against a chosen release.

### 8. [software-mansion/smelter](https://github.com/software-mansion/smelter)

**Language/role:** Rust with TypeScript interfaces; live-media composition, rendering, and processing engine.

Study a modern separation between transport/codec processing, rendering, and application-facing configuration.

- **C2:** The [development architecture guide](https://github.com/software-mansion/smelter/blob/master/DEVELOPMENT.md) separates the HTTP server and API conversion layer from `smelter-core` and `smelter-render`. The renderer consumes sets of frames and produces rendered outputs, and can be isolated through a WebAssembly wrapper.
- **C3:** The core handles queues, codecs, muxing, protocols, and audio; the renderer owns GPU upload/download and YUV/NV12-to-RGBA conversion. Those boundaries make data movement and scheduling understandable rather than incidental.
- **C1:** The same guide describes image snapshots and complete audio/video pipeline tests using RTP dumps. It also documents test sensitivity to CPU contention, a useful reminder that timing-related integration validation differs from deterministic renderer checks.

**Entry point:** `DEVELOPMENT.md`, including crate responsibilities and test procedures. The monorepo's GPU-video work is included in this single entry.

### 9. [OvenMediaLabs/OvenMediaEngine](https://github.com/OvenMediaLabs/OvenMediaEngine)

**Language/role:** C++; live-media server with a substantial transcoding and rendition pipeline. This is the canonical repository reached from the older AirenSoft owner URL.

Study how a live transcoder's workload differs from downstream packetization and viewer delivery.

- **C2:** [Transcoding configuration](https://ovenmedia.com/docs/ome/transcoding) separates output profiles, individual encodes, and rendition playlists. Dynamic profiles can be selected through webhooks, supporting different processing configurations for incoming streams.
- **C3:** The [performance guide](https://ovenmedia.com/docs/ome/performance-tuning) distinguishes socket workers, per-stream packetization workers, and session delivery/encryption workers. It explains why stream count, viewer count, and available CPU cores imply different pool sizes.

**Entry points:** transcoding configuration; performance tuning. **Scope caveat:** current documentation says hardware acceleration was removed from the open-source edition after version 0.20.5. This selection does not attribute that proprietary capability to the current GitHub implementation.

## Frame servers and programmatic file-processing backends

### 10. [vapoursynth/vapoursynth](https://github.com/vapoursynth/vapoursynth)

**Language/role:** C++ core, C plugin API, and Python scripting; programmable frame-processing graphs.

Study the ownership and metadata contracts around a plugin-oriented frame server.

- **C2:** The [API reference](https://www.vapoursynth.com/doc/apireference.html) and [version 4 API](https://www.vapoursynth.com/doc/api/vapoursynth4.h.html) expose cores, nodes, frames, plugin functions, frame requests, caching, and asynchronous retrieval. These support reusable processing plugins rather than a fixed filter chain.
- **C1:** Objects from different cores cannot be mixed; crossing that boundary requires deep copying. Reserved frame properties also encode essential interpretation rules. For example, the reference distinguishes `_Range` from the deprecated `_ColorRange`, whose integer meanings are reversed. This makes the codebase useful for studying how apparently small metadata compatibility decisions affect image correctness.

**Entry points:** API ownership/property reference; version 4 frame and filter interfaces.

### 11. [AviSynth/AviSynthPlus](https://github.com/AviSynth/AviSynthPlus)

**Language/role:** C++; scripted frame server with a plugin ecosystem. AviSynth+ is retained as a substantively evolved implementation, including its own multithreading system; classic AviSynth is not counted separately.

Study how a framework parallelizes third-party filters with different reentrancy guarantees.

- **C1:** The [multithreading documentation](https://avisynthplus.readthedocs.io/en/3.7/avisynthdoc/syntax/syntax_internal_functions_multithreading_new.html) distinguishes filters safe for shared concurrent use, filters requiring separate instances, and filters requiring serialization. Incorrect declarations can expose shared-state bugs; the framework cannot simply assume every plugin is thread-safe.
- **C3:** Separate instances consume additional memory, while a serialized stage can restrict downstream parallelism. `Prefetch` controls concurrency and buffering, with multiple pipeline sections allowing more nuanced scheduling. The tradeoff is explained in terms of actual execution and memory behavior.

**Entry points:** multithreading guide; [release notes](https://github.com/AviSynth/AviSynthPlus/releases), which also document architecture-specific fixes and API adjustments.

### 12. [PyAV-Org/PyAV](https://github.com/PyAV-Org/PyAV)

**Language/role:** Python/Cython; object-level bindings to FFmpeg containers, streams, packets, frames, and codecs. This is a substantive native binding layer, rather than a generated wrapper around command-line options.

Study which native multimedia semantics must remain explicit in a high-level language.

- **C2:** The object model supports decoding, frame manipulation, encoding, muxing, and integration with array/image workflows without prescribing a single application pipeline.
- **C1:** The [time-base guide](https://pyav.org/docs/stable/api/time.html) distinguishes codec, stream, and container time units and explains why packet timestamps must be rescaled after muxer initialization. The [encoding tests](https://raw.githubusercontent.com/PyAV-Org/PyAV/master/tests/test_encode.py) exercise supplied frame timestamps, audio resampling timestamps, encoder flushing, stream associations, and B-frame limits. These give concrete executable examples of semantics that a Python API cannot safely erase.

**Entry points:** time-base guide; `tests/test_encode.py`. The stable time guide rendered an older documentation version during this research; match API details to the installed release.

### 13. [HandBrake/HandBrake](https://github.com/HandBrake/HandBrake)

**Language/role:** C transcoding backend with several platform frontends. The relevant subsystem is **LibHB**, not the desktop interface alone; the [build documentation](https://handbrake.fr/docs/en/latest/developer/build-windows.html) identifies it as the core library used by the Windows GUI.

Study a reusable job-oriented backend that integrates discovery, codec selection, multiple passes, cancellation, and cleanup.

- **C1:** [`libhb/work.c`](https://raw.githubusercontent.com/HandBrake/HandBrake/master/libhb/work.c) shows job processing and failure/cancellation state. For JSON jobs, title scanning must happen before filling defaults that depend on source metadata. Pass setup and teardown are explicit parts of job execution.
- **C2:** Work objects are registered and instantiated for processing jobs, with codec-specific decoder and encoder selection behind common backend machinery. Hardware context handling is integrated with that selection. This is a useful study of reusable abstractions inside an application rather than a claim of a stable third-party SDK.

**Entry points:** `libhb/work.c`; LibHB build and frontend boundary documentation.

## Mobile and browser processing frameworks

### 14. [androidx/media](https://github.com/androidx/media)

**Language/role:** Java/Kotlin; the relevant Media3 subsystems are **Transformer and effects**, counted once within the larger Android media monorepo.

Study how a framework offers a coherent transformation API over heterogeneous device codecs.

- **C2:** The [customization guide](https://developer.android.com/media/media3/transformer/customization) documents replaceable encoder/decoder factories and muxers. Custom implementations can participate through defined interfaces instead of requiring a fork of the whole pipeline.
- **C1:** Requested resolutions may be incompatible with hardware alignment requirements; callers can choose supported fallback dimensions or demand an error. A muxer's negative-timestamp/edit-list capability also determines whether certain trimming optimizations are valid.
- **C3:** [Transformer's overview](https://developer.android.com/media/media3/transformer) describes a MediaCodec decode/encode and OpenGL processing path. The customization guide shows how capable muxers permit trim-only edits without re-encoding, connecting a format contract directly to avoided work.

**Entry points:** Transformer overview; customization guide.

### 15. [linkedin/LiTr](https://github.com/linkedin/LiTr)

**Language/role:** Java/Kotlin; Android media transformation framework around hardware codecs and rendering.

Study a compact stage-oriented design for custom Android transcoding operations.

- **C2:** The repository documents five principal interfaces: media source, decoder, renderer, encoder, and media target. Per-track configuration and compatible stage formats allow implementations to be replaced independently. Default implementations use Android extraction, codec, graphics, and muxing facilities.
- **C1:** The [`MediaTransformer` implementation](https://raw.githubusercontent.com/linkedin/LiTr/main/litr/src/main/java/com/linkedin/android/litr/MediaTransformer.java) separates task execution from callback delivery through an executor and a callback `Looper`. It maintains identified tasks and their futures and exposes task lifecycle operations. The separation is a concrete entry point for studying concurrency and application lifecycle integration.
- **C3:** The stage model accommodates hardware decoding/encoding and graphics-based rendering without making CPU frame copies the only processing interface.

**Entry points:** repository architecture/interface description; `MediaTransformer.java` on the `main` branch.

### 16. [Vanilagy/mediabunny](https://github.com/Vanilagy/mediabunny)

**Language/role:** TypeScript; programmatic media input/output, conversion, and WebCodecs-based processing.

Study a browser-oriented conversion API whose state and resource rules are explicit.

- **C2:** The [conversion guide](https://mediabunny.dev/guide/converting-media-files) composes input, output, track selection, resize/crop/rotation, audio conversion, and custom processing callbacks. These abstractions support both conventional conversion and application-specific media transforms.
- **C1:** Conversion validates track feasibility and reports why tracks are discarded. It distinguishes completion of the execution promise from progress reaching its maximum, and documents cancellation and resource release. Such rules matter when browser codec support or user cancellation changes the outcome midway through a job.
- **C3:** The conversion layer can copy compatible encoded media instead of decoding and re-encoding it. This is a concrete optimization boundary tied to track settings and format compatibility.

**Entry point:** converting-media-files guide, especially validation, execution lifecycle, and per-track customization.

## Hardware pipeline contracts and device memory

### 17. [intel/libvpl](https://github.com/intel/libvpl)

**Language/role:** C/C++; Intel VPL API headers and dispatcher. GPU implementation runtimes are separate; this repository should be studied for contracts and dispatch rather than credited with all underlying codec implementations.

Study asynchronous media dependencies and the boundary between application-owned surfaces and runtime scheduling.

- **C1:** The [transcoding procedures](https://intel.github.io/libvpl/latest/programming_guide/VPL_prg_transcoding.html) explain pointer-based dependency tracking, in-use buffer lifetimes, explicit synchronization before handing surfaces to non-VPL components, and tracing an aborted downstream operation back through earlier synchronization points.
- **C3:** Decode, optional processing, and encode can be queued before synchronizing the final operation. Surface-pool sizing must account for both connected stages and asynchronous depth; synchronizing every intermediate stage can defeat pipelining.
- **C2:** The [session guide](https://intel.github.io/libvpl/latest/programming_guide/VPL_prg_session.html) describes capability-filtered runtime selection and session lifecycle, separating application requirements from a particular implementation.

**Entry points:** transcoding procedures; session and implementation-selection guide.

### 18. [NVIDIA/VideoProcessingFramework](https://github.com/NVIDIA/VideoProcessingFramework)

**Language/role:** C++/CUDA with Python interfaces; **archived historical framework**. GitHub marks it archived on 2024-06-10, and its notice directs new development toward PyNvVideoCodec.

Study the older framework's explicit GPU surface pipeline as a design reference, not as a current maintenance recommendation.

- **C2:** NVIDIA's [implementation tutorial](https://developer.nvidia.com/blog/vpf-hardware-accelerated-video-processing-framework-in-python/) explains separately composable decode, upload, surface conversion, download, and encode objects.
- **C1:** Surface-returning operations can reuse their storage on subsequent calls, whereas downloaded arrays have different ownership behavior. Encoders also require draining buffered output. Those distinctions show why a Python-facing API still needs precise native lifetime and end-of-stream rules.
- **C3:** Device-resident surfaces let processing stages exchange GPU data without a host download between every operation. The relevant lesson is memory placement and transfer boundaries; no historical benchmark is treated as a current performance guarantee.

**Entry points:** repository archival/deprecation notice; NVIDIA's framework tutorial.

## Packaging stages and transcoding orchestration

### 19. [shaka-project/shaka-packager](https://github.com/shaka-project/shaka-packager)

**Language/role:** C++; media packaging, encryption, and adaptive-streaming output. It belongs here as a reusable processing stage, not as a codec transcoder.

Study a pipeline in which media processing and manifest generation are separate but coordinated.

- **C2:** The [design documentation](https://shaka-project.github.io/shaka-packager/html/design.html) describes demuxing, chunking, encryption, replication, trick-play generation, and muxing as connected handlers. Muxer listeners feed HLS/DASH notification and manifest structures, separating media events from output descriptions.
- **C1:** Sparse subtitle input creates a timing problem: no subtitle packet does not mean time has stopped. The design uses video-derived heartbeat information and coordinated segment boundaries so text chunking remains aligned with the audio/video stream. This is an unusually clear example of correctness spanning separate pipeline branches.

**Entry points:** design documentation; [packager documentation](https://shaka-project.github.io/shaka-packager/html/documentation.html).

### 20. [axiomatic-systems/Bento4](https://github.com/axiomatic-systems/Bento4)

**Language/role:** C++; MP4/ISO-BMFF parsing, transformation, encryption, and packaging SDK. This is container/sample processing rather than a general codec engine.

Study how a container-processing framework exposes extension hooks while preserving serialized layout constraints.

- **C2:** The [`AP4_Processor` interface](https://raw.githubusercontent.com/axiomatic-systems/Bento4/master/Source/C%2B%2B/Core/Ap4Processor.h) provides per-track and per-fragment handlers, sample transformation, processed-size calculation, initialization/finalization hooks, and byte-stream inputs/outputs. These are reusable foundations for different file transformations.
- **C1:** Its contracts explicitly restrict fragment finalization from changing atom sizes. Processed sample sizes are a separate concern from processing the samples themselves, and progress callbacks can abort processing through error returns. These constraints make the interface useful for studying how extensibility interacts with binary layout and partial failure; they are not a claim of immunity to malformed files.

**Entry point:** `Source/C++/Core/Ap4Processor.h`, especially `TrackHandler` and `FragmentHandler`.

### 21. [livepeer/go-livepeer](https://github.com/livepeer/go-livepeer)

**Language/role:** Go; distributed live-video transcoding node software.

Study the partitioning of a media workload across network roles and operational responsibilities.

- **C2:** The repository distinguishes broadcasters, orchestrators, and transcoders. The [multi-orchestrator architecture document](https://github.com/livepeer/go-livepeer/blob/master/doc/multi-o.md) further separates transcoding processes from reward, redemption, and blockchain-facing responsibilities. Standalone transcoders can participate without their own chain account.
- **C3:** The documented topology supports multiple orchestrators behind a load balancer and multiple transcoders attached to orchestrators. It makes independent scaling of coordination and codec work concrete rather than assuming that one process should perform every role.

**Entry point:** `doc/multi-o.md`. Its deployment examples reference older network environments; the architectural decomposition is the study target, not a current deployment recipe. No claim about current network economics or measured scalability is made.

### 22. [Unmanic/unmanic](https://github.com/Unmanic/unmanic)

**Language/role:** Python; plugin-based media-library processing and transcoding job orchestration.

Study reliable workflow composition above individual codec commands.

- **C2:** The [workflow documentation](https://docs.unmanic.app/docs/using_unmanic/workflow/) separates file discovery/testing, worker processing, file movement, and result handling into extensible stages. Ordered plugins can decide whether work is required and compose multiple processing steps.
- **C1:** Workers process successive outputs in a cache; the documented normal workflow replaces the original only after successful processing and retains it when a task fails. Worker stages independently check whether their operation is needed, rather than blindly repeating discovery decisions. This supplies a useful failure-staging pattern, without establishing crash-atomic replacement or every plugin's correctness.

**Entry point:** workflow guide, particularly worker chaining, cached outputs, and result handling.

## Coverage, exclusions, and research limits

Discovery used live web search across more than six distinct angles: general multimedia/filter-graph frameworks; distributed transcoding workers and job systems; Rust and Elixir media pipelines; scripted frame servers and plugin concurrency; Android hardware transformation; browser/WebCodecs conversion; GPU surface pipelines and vendor APIs; adaptive packaging; and clock-driven broadcast composition. Primary-source follow-up covered public APIs, architecture guides, implementation files, tests, release notes, and lifecycle documentation. Later searches increasingly returned already-covered projects, thin FFmpeg launchers, tutorials, and young projects without enough inspectable architectural evidence, so the selection stopped at 22.

The list deliberately includes smaller or more specialized systems alongside FFmpeg and GStreamer: demand-driven BEAM elements, an OCaml clock model, two independently evolved frame servers, browser processing, Android stages, and plugin-based batch workflows. Packaging and orchestration are included because they supply substantial pipeline behavior; they are labeled so readers do not mistake them for codec implementations. PyAV is retained for its native object and time semantics, and HandBrake for LibHB. A monorepo and its internal subsystems count once. AviSynth+ is included for substantive separate evolution, not to duplicate its ancestor.

Excluded classes include standalone codec implementations without a broader pipeline abstraction, playback-only clients, GUI editors whose backend is already represented, awesome lists, generated or thin command wrappers, tutorial transcoders, and unrelated workflow engines. Projects hosted elsewhere were not substituted with unofficial GitHub copies. FFmpeg and GStreamer remain eligible as official substantive mirrors. NVIDIA VideoProcessingFramework is explicitly historical; newer replacement branding does not establish a verified independent GitHub implementation.

This was source-and-documentation research, with no cloning, dependency installation, candidate-code execution, or benchmarking. Some documentation is versioned, development-oriented, or historical; those limitations are called out where material. Canonical repository pages were verified, but this report does not certify maintenance cadence, production suitability, security, or the correctness of every module. C4 is awarded only where inspected history and compatibility/testing evidence support it; other entries qualify through their stated C1–C3 evidence.
