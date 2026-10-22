# Real-time audio servers and routing engines

Research date: **2026-10-09**.

This selection covers 22 repositories implementing audio-server scheduling, live signal routing, network audio transport and mixing, programmable processing graphs, or virtual audio devices. It includes both callback/deadline-oriented engines and explicitly identified buffered, soft real-time systems. Routing policy is included where it controls a real audio graph. General media libraries, device-access wrappers, patchbay-only GUIs, music-library servers, and speech-service orchestration are outside the main scope. Monorepos are counted once, with the relevant subsystem identified below.

**Criteria legend:** **C1** — difficult correctness involving concurrency, timing, numerical semantics, invariants, or failure handling. **C2** — substantial reusable abstractions supporting different applications. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — documented evolution over years with compatibility, testing, or complexity-management evidence. A criterion indicates an engineering study opportunity, not a certification that every implementation choice is correct or exemplary.

## System audio servers and routing policy

### 1. [PipeWire/pipewire](https://github.com/PipeWire/pipewire)

**C; multiprocess multimedia server and processing graph. Official project GitHub mirror; development is hosted on freedesktop.org GitLab.** Focus on the audio graph, SPA components, and client/server scheduling rather than the video subsystems.

An experienced engineer can study how separately executing clients participate in one device-paced graph without routing every wakeup through a central server. The repository also contains JACK, ALSA, and PulseAudio integration, making it useful for studying compatibility at the system boundary.

- **C1:** Nodes carry shared activation records and dependency counts; links become scheduling dependencies only after negotiation. Asynchronous links use alternating buffer slots, with explicit extra-cycle latency, to avoid concurrent buffer access. The [graph-scheduling design](https://docs.pipewire.org/page_scheduling.html) explains these invariants and unfinished-cycle/xrun handling.
- **C2, C3:** Nodes, ports, links, and drivers support different processing topologies. Configuration runs separately from real-time data processing, with buffers and metadata prepared in shared memory beforehand; remote nodes can directly signal their peers. The same [scheduling document](https://docs.pipewire.org/page_scheduling.html) is the best implementation-oriented starting point, followed by the repository’s audio compatibility directories.

### 2. [jackaudio/jack2](https://github.com/jackaudio/jack2)

**C++; low-latency interapplication audio/MIDI server.** JACK2 is a separate implementation of the JACK server core, not merely a repackaged JACK1 fork. Its README describes dataflow activation, parallel execution of independent clients, and synchronous versus asynchronous processing modes.

- **C1, C3:** Graph mutations write a next state while real-time execution reads the current state; graph switching and coherent topological reads are explicit operations. Study [JackGraphManager.cpp](https://github.com/jackaudio/jack2/blob/develop/common/JackGraphManager.cpp), especially RunNextGraph, TopologicalSort, and connection changes, to connect the scheduling model with its concurrency machinery.
- **C4:** The dated [ChangeLog](https://github.com/jackaudio/jack2/blob/develop/ChangeLog.rst) records multiple years of protocol/alignment changes, platform compatibility repairs, semaphore fixes, an ARM ring-buffer thread-safety fix, and separation of example tools from the server. These are stronger evolution signals than repository age alone. The inspected changelog labels 1.9.23 as work in progress and dates 1.9.22 to 2023; this report makes no claim about release cadence.

### 3. [jackaudio/jack1](https://github.com/jackaudio/jack1)

**C; original JACK server implementation and historical architectural comparison.** Retained separately because JACK1 and JACK2 have substantive different server implementations. The GitHub repository was not marked archived when inspected; “historical” here describes its first-generation design, not a claim that it is unavailable.

The especially valuable reading is the [transport design](https://github.com/jackaudio/jack1/blob/master/doc/transport.dox): it explains coordination among independently developed audio applications, rather than merely listing API calls.

- **C1:** Transport state remains stable throughout a processing cycle. The design separates the single timebase owner from requests any client can make, defines delayed repositioning, and uses a starting state plus timeout for clients that cannot immediately synchronize.
- **C3:** Transport callbacks execute in existing process threads, and state changes are deferred to a following cycle to avoid another graph traversal and context switch. These performance choices are tied directly to sample-accurate behavior in the same design document. Its compatibility discussion also exposes the costs of deprecated interfaces and extensible binary structures, without relying on age alone to award C4.

### 4. [pulseaudio/pulseaudio](https://github.com/pulseaudio/pulseaudio)

**C; network-capable desktop sound server. Official GitHub mirror of the freedesktop.org GitLab project.** Useful for studying a policy-rich sound server whose responsibilities include device changes, stream routing, filtering, and persistent user settings.

- **C1:** [asyncmsgq.c](https://github.com/pulseaudio/pulseaudio/blob/master/src/pulsecore/asyncmsgq.c) distinguishes asynchronous posts from synchronous request/reply operations. It explicitly manages message-object and audio-memory references, writer-side locking, semaphore completion, dispatch, and queue flushing. These are concrete lifetime and cross-thread completion obligations; the implementation should not be summarized as universally lock-free.
- **C2:** The [default server startup configuration](https://github.com/pulseaudio/pulseaudio/blob/master/src/daemon/default.pa.in) demonstrates independently loadable modules for device discovery, stream restoration, JACK detection, network protocols, null sinks, role policies, and automatic filters. Read it as a map from reusable server mechanisms to user-visible routing behavior, then follow individual modules relevant to the use case.

### 5. [ratchov/sndio](https://github.com/ratchov/sndio)

**C; portable version of OpenBSD’s audio/MIDI subsystem, including sndiod.** A comparatively compact alternative to the larger Linux desktop stacks, with substantive mixing and synchronization behavior.

- **C2:** The [sndiod manual](https://github.com/ratchov/sndio/blob/master/sndiod/sndiod.8) describes subdevices as reusable configurations: applications share playback mixing, capture fan-out, channel mapping, encoding conversion, monitoring, and MIDI hubs through a common device abstraction. Multiple subdevices allow different processing configurations to coexist.
- **C1:** [sndiod/dev.c](https://github.com/ratchov/sndio/blob/master/sndiod/dev.c) makes stream lifecycle and recovery concrete. It distinguishes stopped/draining streams, detects insufficient playback data or capture space, and applies different xrun policies: ignore, preserve synchronization through skipped cycles, or terminate. Follow the slot processing code to study how buffer availability, stream state, and transport timing interact.

### 6. [PipeWire/wireplumber](https://github.com/PipeWire/wireplumber)

**C and Lua; routing-policy/session-management engine for PipeWire. Official project GitHub mirror.** This is the control layer that creates and reconfigures routes; PipeWire performs the sample processing.

- **C2:** [Understanding Session Management](https://github.com/PipeWire/wireplumber/blob/master/docs/rst/design/understanding_session_management.rst) separates device enablement, profiles/routes, permissions, node configuration, link management, and metadata. These abstractions support desktop defaults, device hotplug, Bluetooth profile changes, and customized routing policies.
- **C1:** [Events and Hooks](https://github.com/PipeWire/wireplumber/blob/master/docs/rst/design/events_and_hooks.rst) specifies event priorities, FIFO ordering within a priority, before/after hook dependencies, and asynchronous hook state machines. New events can interrupt the remaining hooks of a lower-priority event. The worked profile/route/node examples make ordering and reentrancy hazards inspectable rather than implicit in callbacks.

## Programmable audio servers and processing graphs

### 7. [supercollider/supercollider](https://github.com/supercollider/supercollider)

**C++ server implementation and SuperCollider language; scsynth and supernova audio servers within a larger monorepo.** The language and IDE are not separate entries.

- **C2:** The [server architecture](https://github.com/supercollider/supercollider/blob/develop/HelpSource/Reference/Server-Architecture.schelp) explains Synths, Groups, unit generators, and indexed audio/control buses. A node tree determines execution order while buses carry signals, allowing independently controlled synthesis and effects processes to be repatched through network commands.
- **C1:** The [server plugin API](https://github.com/supercollider/supercollider/blob/develop/HelpSource/Reference/ServerPluginAPI.schelp) distinguishes scalar, control, audio, and demand rates, and documents shared/exclusive sound-buffer and audio-bus access for supernova. These expose numerical-rate and concurrent-access contracts that plugin authors must respect.

Study the contrast between ordered server execution and parallel-server resource access. The architecture document explicitly warns that some details are old; use it for the conceptual model and the plugin API/current source for implementation-specific assumptions.

### 8. [elk-audio/sushi](https://github.com/elk-audio/sushi)

**C++; headless plugin host and audio/MIDI routing engine for Elk Audio OS and desktop backends.** Relevant both to embedded audio appliances and engines embedded in other hosts.

- **C1, C2:** The [library guide](https://github.com/elk-audio/sushi/blob/master/docs/LIBRARY.md) separates active hosts from reactive embedding and distinguishes ordinary control APIs from the real-time controller. Control calls are scheduled internally instead of being called freely from the audio callback. It also documents fixed buffer-size obligations and limitations of reactive MIDI synchronization—valuable boundary contracts for engine reuse.
- **C3:** [audio_graph.cpp](https://github.com/elk-audio/sushi/blob/master/src/engine/audio_graph.cpp) reserves track storage, distributes tracks to worker slots, configures the real-time worker pool, measures rendering, and uses an explicit wake-and-wait operation for multicore execution. This is a readable example of turning track-level parallelism into a bounded audio-cycle workflow.

### 9. [HEnquist/camilladsp](https://github.com/HEnquist/camilladsp)

**Rust; configurable multichannel real-time DSP and routing engine.** Particularly useful for speaker crossovers, room correction, and inserting channel processing between applications and devices.

- **C2, C3:** The repository’s detailed configuration documentation models a pipeline of mixers and filters: mixers change channel routing/count, IIR filters use biquads, and FIR filters use FFT convolution. Fixed chunk size exposes the latency/processing-efficiency tradeoff directly. Start with the [processing and configuration guide](https://github.com/HEnquist/camilladsp#camilladsp-engine-v41).
- **C1:** [processing.rs](https://github.com/HEnquist/camilladsp/blob/master/src/processing.rs) shows separate capture/playback message channels, a startup barrier, and distinct handling for audio, pause, end-of-stream, channel failure, filter-parameter updates, pipeline rebuilds, and device changes. Study how configuration changes cross into processing and which changes require stopping the stream; do not assume every update is allocation-free or seamless.

### 10. [falkTX/Carla](https://github.com/falkTX/Carla)

**C++ engine with Python frontend; plugin host with rack and patchbay routing.** Its signal-processing backend, rather than its patchbay GUI alone, earns inclusion.

- **C2:** [CarlaEngineGraph.hpp](https://github.com/falkTX/Carla/blob/main/source/backend/engine/CarlaEngineGraph.hpp) separates external connections, sequential RackGraph processing, and a PatchbayGraph containing audio, CV, and MIDI buffers. Plugin insertion/removal, port reconfiguration, and internal/external connections expose a reusable host graph model across plugin formats and audio drivers.
- **C1, C3:** [CarlaEngineGraph.cpp](https://github.com/falkTX/Carla/blob/main/source/backend/engine/CarlaEngineGraph.cpp) makes processing policy visible: rack buffers are prepared separately, outputs/events are initialized, and unavailable or un-lockable plugins are skipped through a try-lock path. Follow RackGraph::process and the patchbay implementation to study the tradeoffs between graph mutability, plugin coordination, and uninterrupted block processing.

The README identifies several bridge/export features as experimental; the selection does not imply uniform maturity across all hosting modes.

### 11. [savonet/liquidsoap](https://github.com/savonet/liquidsoap)

**OCaml; programmable media-flow engine for continuous radio and streaming. Buffered, soft real-time rather than a studio callback server.** Included for its audio source graphs, live inputs, transitions, mixing, and output routing.

- **C1:** The [clock design and usage guide](https://github.com/savonet/liquidsoap/blob/main/doc/content/clocks.md) explains conflicts between simultaneous synchronization sources, hardware clock drift, and operators such as crossfade that consume inputs at a different rate. The engine rejects incompatible clock arrangements instead of silently treating all sources as one clock.
- **C2, C3:** Sources, operators, clocks, and buffers form reusable composition boundaries. The same guide shows buffering between clock domains, separating a network output from local recording so stalls do not propagate, and assigning outputs to separate clocks for parallel work. It also documents overload/catchup diagnostics. These are unusually explicit explanations of why timing belongs in the graph’s semantics, not only in an I/O loop.

## Network audio transport, mixing, and remote processing

### 12. [roc-streaming/roc-toolkit](https://github.com/roc-streaming/roc-toolkit)

**C++ core with a C API; real-time network audio toolkit and command-line endpoints.** Useful for studying a reusable transport engine rather than a single collaboration application.

- **C1, C2:** [Pipeline internals](https://github.com/roc-streaming/roc-toolkit/blob/master/docs/sphinx/internals/pipelines.rst) distinguish packet/frame readers and writers, slots, endpoints, and sessions. Receivers reconstruct frames on demand, use resampling to bridge sender/receiver clock domains, and can combine media and repair endpoints for FEC. The explanation connects packet routing to playback deadlines and the time still available to recover missing data.
- **C3:** [Threads and queues](https://github.com/roc-streaming/roc-toolkit/blob/master/docs/sphinx/internals/threads.rst) separates network, sound I/O, pipeline, and control responsibilities. Queue-based communication limits shared state; configuration tasks run between frames, and intrusive task storage avoids allocation/copying in common scheduling paths. The documentation carefully qualifies platform-dependent lock-free/wait-free behavior.

### 13. [jacktrip/jacktrip](https://github.com/jacktrip/jacktrip)

**C++; bidirectional multichannel network audio and hub-server implementation.** Its uncompressed audio transport makes the buffering and network-jitter tradeoff especially visible.

- **C1:** [JitterBuffer.cpp](https://github.com/jacktrip/jacktrip/blob/main/src/JitterBuffer.cpp) explicitly handles packet loss, split ring-buffer writes, underruns, overflow corrections, and zero-filling when playback requests more data than is available. Read insertSlotNonBlocking, readSlotNonBlocking, and processPacketLoss together; the method names do not mean the whole implementation is lock-free, since these paths use a mutex.
- **C3:** The same implementation adjusts queue latency from observed occupancy and correction history, quantizes adjustments to audio slots, and exposes underrun/overflow statistics. This is concrete adaptive latency control, not just a low-latency claim. The repository’s separation of audio interfaces, UDP transport, hub listeners, and buffering provides a clear route from device callbacks to multiuser network operation.

### 14. [jamulussoftware/jamulus](https://github.com/jamulussoftware/jamulus)

**C++/Qt; centralized real-time ensemble server with per-client mixes.** Count the server and client together as one repository; the server’s timed processing is the study target.

- **C1:** [server.cpp](https://github.com/jamulussoftware/jamulus/blob/main/src/server.cpp) snapshots connected channels under a mutex, decodes their incoming data, and waits for worker completion before advancing processing. It separately mixes, Opus-encodes, and transmits each listener’s output. The code makes channel disconnection and coordination between receive, decode, and mix stages explicit.
- **C3:** Constructor comments state that timer processing must avoid allocation, and the implementation reserves worst-case vectors before starting. Decode and mix/encode workloads can be partitioned across a thread pool with explicit completion waits. Study CServer::OnTimer alongside initialization to understand both the intended real-time discipline and the cost of synchronization under participant growth.

This architecture contrasts usefully with peer-to-peer SonoBus and JackTrip’s transport/hub model.

### 15. [sonosaurus/sonobus](https://github.com/sonosaurus/sonobus)

**C++/JUCE; peer-to-peer audio engine and mixer, available standalone and as a plugin.** The connection server is for discovery; audio travels between peers. Its AOO dependency is acknowledged rather than counted as another implementation in this report.

- **C2:** The repository documents independently configurable peer audio, local processing, recording, and standalone/plugin use. [ChannelGroup.cpp](https://github.com/sonosaurus/sonobus/blob/main/Source/ChannelGroup.cpp) supplies a concrete reusable abstraction for channel groups, panning, monitoring, effect parameters, and reverb sends.
- **C1, C3:** The same file handles live monitor-delay changes through atomic flags, a try-lock, channel-count checks, and fade-out/change/fade-in transitions. Gain ramps and separate processing state help explain how interactive controls can change a running route without treating parameter changes as arbitrary sample discontinuities.

Study ChannelGroup::processMonitor and processBlock as the local routing layer, then follow the repository’s processor into network peer management. This is an application-owned routing engine, not a general desktop sound daemon.

### 16. [snapcast/snapcast](https://github.com/snapcast/snapcast)

**C++; synchronized multiroom audio server and clients. Buffered, soft real-time playback.** This is the verified current canonical repository; the older badaix owner URL is not counted separately.

- **C1:** The [binary protocol](https://github.com/snapcast/snapcast/blob/develop/doc/binary_protocol.md) specifies the joining sequence, codec-header-before-audio requirement, timestamped chunks, message lengths, and periodic client/server time exchange. The clock-offset calculation explicitly assumes symmetric network latency, an important limitation when reasoning about synchronization accuracy.
- **C2, C3:** The repository describes pluggable PCM sources, multiple codecs, client groups, and platform playback backends. Server timestamps and client chunk buffers separate distribution from scheduled playout, with playback-rate correction used to keep clients aligned. Study this architecture when synchronized distribution matters more than the minimum possible interactive round-trip delay; no numerical synchronization guarantee is adopted here.

The protocol document is the best additional entry point beyond the repository’s substantial “How does it work” explanation.

### 17. [bondagit/aes67-linux-daemon](https://github.com/bondagit/aes67-linux-daemon)

**C++ daemon and web UI; AES67/RAVENNA session and channel-routing control.** The repository integrates a separate RAVENNA ALSA kernel driver: that driver handles RTP/PTP processing, while this daemon configures and monitors it through netlink. Do not attribute the entire data plane to the daemon.

- **C1:** [session_manager.cpp](https://github.com/bondagit/aes67-linux-daemon/blob/master/daemon/session_manager.cpp) parses SDP media descriptions, derives packet sample counts, examines PTP reference-clock/domain compatibility, and protects source/sink state with locks. These are substantive protocol and reconfiguration concerns even though sample transport lives below the daemon.
- **C2:** The [daemon API guide](https://github.com/bondagit/aes67-linux-daemon/blob/master/daemon/README.md) exposes configurable RTP sources/sinks, ALSA channel maps, SDP acquisition, discovery, and status. It specifies that sink playout delay cannot be shorter than the source packet’s announced sample span, and distinguishes sequence, source, payload, and timestamp errors. This makes a useful control-plane counterpart to Roc’s userspace transport pipelines.

### 18. [teodly/inferno](https://github.com/teodly/inferno)

**Rust; unofficial Dante-compatible audio-over-IP implementation, reusable library, ALSA plugin, and recorder. Project GitHub mirror of its GitLab development repository. Experimental.** The README explicitly says protocol behavior is partly reverse engineered/guessed and cautions against serious use; this is an implementation study selection, not an interoperability endorsement.

- **C1:** [ring_buffer.rs](https://github.com/teodly/inferno/blob/dev/inferno_aoip/src/ring_buffer.rs) models timestamped writes, missing spans, late repair, overwrite detection, atomic readable positions, and externally owned buffers that can become invalid. These expose unusually rich invariants at the Rust/foreign-buffer boundary.
- **C2, C3:** Owned and external storage share buffer-proxy interfaces, while ring input/output handles support different integrations. [media_clock.rs](https://github.com/teodly/inferno/blob/dev/inferno_aoip/src/media_clock.rs) separates clock overlays from sample timebases and bridges asynchronous clock updates into a real-time receiver. It includes tests and explicitly unfinished clock-wrap/correction details, which should be treated as review targets rather than guarantees.

### 19. [apohl79/audiogridder](https://github.com/apohl79/audiogridder)

**C++/JUCE; remote DSP server and DAW-side network bridge.** It hosts plugin chains on another computer and transports audio/MIDI, processing state, and plugin UI interaction.

- **C1:** [AudioWorker.cpp](https://github.com/apohl79/audiogridder/blob/master/Server/Source/AudioWorker.cpp) establishes sample rate, block size, channel/sidechain maps, and processing precision from the handshake. It checks incoming channel capacity, handles float/double fallback, and closes failed connections rather than continuing with an invalid stream.
- **C2, C3:** A reusable ProcessorChain and channel mapper connect transport buffers to plugin bus layouts. The worker sends chain latency back to the client and measures processing against a threshold derived from the block duration. The source is a useful example of adapting a local plugin-processing contract to a network request/response pipeline without pretending network time disappears.

Start with AudioWorker::init, run, and processBlock, then follow the ProcessorChain in the same source directory. The server/plugin pair is counted once.

### 20. [netham45/screamrouter](https://github.com/netham45/screamrouter)

**C++ audio engine, Python control service, and TypeScript frontend; whole-house network audio router.** Its own mixing, scheduling, and rate-control implementation makes it distinct from the Scream virtual soundcard below.

- **C1, C3:** [mix_scheduler.cpp](https://github.com/netham45/screamrouter/blob/main/src/audio_engine/output_mixer/mix_scheduler.cpp) handles attaching/detaching input workers, sentinel-based wakeup during shutdown, source-ready queues, queue-depth/age telemetry, and dropping oldest chunks at a configured cap. These are inspectable lifecycle and latency/backlog policies.
- **C2, C3:** The repository separates protocol receivers, input processing, output mixers, senders, and synchronization from the Python API. [sink_rate_controller.cpp](https://github.com/netham45/screamrouter/blob/main/src/audio_engine/output_mixer/sink_rate_controller.cpp) smooths per-source backlog, uses target/tolerance bands, caps speedup, and dispatches rate-change callbacks after releasing its state lock. Study it as a concrete example of joining heterogeneous streams while keeping buffering policy separate from transport and DSP.

No hard real-time guarantee or measured whole-house synchronization accuracy is inferred from the project’s feature claims.

## Virtual audio routing devices

### 21. [ExistentialAudio/BlackHole](https://github.com/ExistentialAudio/BlackHole)

**C; macOS Core Audio HAL loopback driver.** It routes applications’ outputs back into corresponding input channels; it is a virtual cable, not an arbitrary patchbay or complete sound server.

- **C1, C3:** [BlackHole.c](https://github.com/ExistentialAudio/BlackHole/blob/master/BlackHole/BlackHole.c) implements host/sample-time mapping, ring-buffer wrap splitting, silence when output is unavailable, and late-write rejection. The I/O path uses buffer copies and vector operations, while allocation is tied to starting I/O. Read GetZeroTimeStamp and DoIOOperation together. The source also identifies a limitation around simultaneous writes from main and mirrored devices, so generic multi-source mixing should not be assumed.
- **C4:** The [changelog](https://github.com/ExistentialAudio/BlackHole/blob/master/CHANGELOG.md) records fixes across 2019–2025, including buffer allocation during device changes/sleep, clock-related Apple Silicon failures, and later compatibility changes. Some release dates appear out of sequence, so this report uses the documented history of specific fixes rather than inferring a release cadence.

### 22. [duncanthrax/scream](https://github.com/duncanthrax/scream)

**C++ Windows virtual audio driver with C Unix receivers; network soundcard.** The driver derives from Microsoft’s MSVAD sample, but the network transport, receivers, and shared-memory integration form a substantive implementation beyond an untouched tutorial.

- **C2:** The repository documents a small PCM wire format carrying rate, width, channel count, and speaker mapping. Windows playback can feed multiple receiver backends, and the project also supports a VM shared-memory transport. This is a reusable virtual-device-to-network boundary rather than an application-specific codec wrapper.
- **C1, C3:** The [JACK receiver](https://github.com/duncanthrax/scream/blob/master/Receivers/unix/jack.c) resamples incoming PCM into a ring buffer, converts interleaved samples into per-port callback buffers, limits reads to available complete frames, and zero-fills underruns. Study the separation between process_source_data and jack_process to see where conversion/storage growth happens versus deadline-driven consumption. The [Unix receiver dispatcher](https://github.com/duncanthrax/scream/blob/master/Receivers/unix/scream.c) shows how latency settings and output backends are selected.

## Coverage, search process, and limitations

The discovery pass used **20 search formulations**, including general real-time audio servers; JACK/PipeWire graph architecture; BSD sndio and PulseAudio mirrors; network music systems; Rust/C++ DSP graphs; embedded headless plugin hosts; AES67/RAVENNA routing; virtual audio cables and network soundcards; remote plugin DSP; and less common implementation languages. Later network searches added Inferno and ScreamRouter. Final broad queries increasingly returned already represented architectures, setup wrappers, awesome lists, speech/AI pipelines, and newly advertised projects for which this pass did not establish equally useful implementation evidence.

Every retained canonical GitHub repository page was opened. Each entry has additional primary implementation/design/API evidence that was read, including raw source when GitHub’s rendered pages or documentation sites failed. GitHub API rate limits prevented a systematic metadata sweep; public repository pages and source-tree payloads supplied canonical names, branches, mirror/archive information, and source paths instead. No candidates were cloned, built, installed, benchmarked, or run. Current branch links are reading entry points and can change after the research date.

The list emphasizes executable routing/dataflow machinery. Patchbay frontends such as qpwgraph and QjackCtl, ordinary device-access libraries such as PortAudio, music-library servers, general DAWs, wrapper/setup repositories, and speech-service gateways were excluded from the selection. Broad WebRTC/telephony servers would warrant a separate search rather than being counted merely because they transport audio. Bundled AOO/JUCE dependencies, NetJACK within JACK2, and the AES67 kernel-driver integration are not extra repository entries. JACK1 and JACK2 remain separate because the latter explicitly implements a different server core.

PipeWire, WirePlumber, PulseAudio, and Inferno are flagged as project mirrors; JACK1 is identified as a historical design; Inferno’s experimental status is explicit. The inspected repositories were not marked archived. This does not establish active maintenance or production suitability. C4 is used only where dated, substantive maintenance history was inspected. Other criterion assignments are grounded engineering judgments from the linked material, not independent proofs of correctness, security, scalability, or hard real-time behavior.
