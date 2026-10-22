# Media playback engines

Research date: **2026-10-09**.

This report selects 24 GitHub repositories implementing substantial playback machinery: native audiovisual pipelines, adaptive browser streaming, audio mixing and scheduling, and tracker-music replay. Frameworks and monorepos are included only for their identified playback subsystems. Browser engines here often delegate decoding and presentation to browser APIs; audio replay libraries may produce PCM for an application-supplied output device. These are legitimate but different boundaries of an engine. This is a guide to engineering study, not a ranking or a claim that every component is exemplary.

**Criteria legend:** **C1** — difficult correctness involving state, concurrency, numerical semantics, malformed inputs, or failure recovery. **C2** — substantial reusable abstractions serving multiple use cases. **C3** — real performance constraints addressed through inspectable architectural choices. **C4** — sustained evolution supported by compatibility, testing, or complexity-management evidence. Criteria below are evidence-grounded assessments; proposed study lessons are editorial inferences.

## Native audiovisual frameworks

### 1. [mpv-player/mpv](https://github.com/mpv-player/mpv)

**Language / role:** C; native audio/video player and embeddable libmpv engine.

Study how a running playback core is exposed to independent application event loops. **C1:** the client contract distinguishes synchronous calls that can wait indefinitely, asynchronous replies that require correlation, command ordering, and event-queue congestion. It also explains serialization through the playback-core lock. **C2:** the same commands, properties, and events support embedding and scripting without exposing individual decoder internals. The unusually explicit [client API header](https://raw.githubusercontent.com/mpv-player/mpv/master/include/mpv/client.h) is the best starting point.

The [client API change history](https://raw.githubusercontent.com/mpv-player/mpv/master/DOCS/client-api-changes.rst) adds useful evidence of compatibility management: versioned API changes, staged retirement of the old OpenGL callback interface, and documented render-control deadlock fixes. Its ancestry in MPlayer is acknowledged by the project; this is a substantially evolved playback implementation, not a second listing of that ancestor.

### 2. [videolan/vlc](https://github.com/videolan/vlc)

**Language / role:** principally C/C++; VLC playback core and LibVLC. **Official GitHub mirror:** development is hosted at VideoLAN's own forge, as the repository identifies.

Study the boundary between the internal player and its embedding interface. **C1:** the [internal player contract](https://raw.githubusercontent.com/videolan/vlc/master/include/vlc_player.h) specifies lock ownership, blocking destruction, and the lifetime of track/program pointers after unlocking. Those rules make asynchronous playback and UI coordination concrete. **C2:** the [LibVLC media-player API](https://raw.githubusercontent.com/videolan/vlc/master/include/vlc/libvlc_media_player.h) provides a reusable player object, media transitions, callbacks, and track/title control to host applications.

The two headers are complementary entry points: one reveals synchronization obligations inside the engine, while the other shows what is exposed to consumers. The inspected development headers should not be assumed to match every released LibVLC version.

### 3. [GStreamer/gstreamer](https://github.com/GStreamer/gstreamer)

**Language / role:** principally C; multimedia-framework monorepo, especially its pipeline core and playback elements. **Official GitHub mirror** of the freedesktop.org GitLab repository.

Study an engine that expresses playback as cooperating elements sharing a clock. **C1:** the [clock and synchronization guide](https://gstreamer.freedesktop.org/documentation/application-development/advanced/clocks.html) separates absolute time, running time, and stream position; describes flushing seeks; and explains clock loss and latency redistribution. Confusing these time domains directly breaks synchronization. **C2:** clocks, timestamped buffers, segment events, and sinks work across file playback, network buffering, and mixtures of live and recorded sources.

**C3:** the same guide explains why sinks compensate for the maximum pipeline latency and why an audio-device clock can avoid extra clock slaving. This is a particularly strong starting point for understanding synchronization before exploring individual playback plugins. Count the monorepo once, rather than counting its plugin subprojects separately.

### 4. [gpac/gpac](https://github.com/gpac/gpac)

**Language / role:** C; multimedia framework, including player/compositor pipelines and the libgpac filter engine.

Study scheduling and data ownership in a general graph that can terminate in audiovisual playback. **C1:** the [filter API's architectural introduction](https://raw.githubusercontent.com/gpac/gpac/master/include/gpac/filters.h) describes one-thread-at-a-time filter execution, packet-associated property changes, reference ownership, and specified reentrancy exceptions. **C2:** sessions, filters, PIDs, packets, and events form a common interface for sources, decoders, transformations, and sinks. **C3:** PID occupancy controls scheduling, while packet recycling and shared references reduce allocation and copying.

The [filter overview](https://github.com/gpac/gpac/wiki/Filters) explicitly connects this architecture to playback and custom pipelines. That overview is historical documentation: its banner says the wiki moved and will no longer be updated. Use the source header for the inspected implementation contract. Packaging and transcoding are adjacent capabilities, not the reason this repository is included.

## Mobile, embedded, and application-library engines

### 5. [androidx/media](https://github.com/androidx/media)

**Language / role:** Java/Kotlin; Jetpack Media3 monorepo, specifically ExoPlayer and its playback components.

Study how dependency injection makes buffering policy, track selection, transport, and rendering independently replaceable. **C2:** the official [customization guide](https://developer.android.com/media/media3/exoplayer/customization) defines `MediaSource`, `Renderer`, `TrackSelector`, `LoadControl`, and `LivePlaybackSpeedControl` boundaries. It also shows nested extension points such as data-source factories and retry policies. **C3:** asynchronous MediaCodec buffer queueing uses additional threads to schedule decoding/rendering, with the documented aim of reducing dropped frames and audio underruns.

The same guide explains consistent state propagation through `ForwardingSimpleBasePlayer`, offering a useful correctness study beyond simple interface composition. The repository documents stable versus explicitly unstable APIs and migration from earlier ExoPlayer projects. The old standalone ExoPlayer repository is not counted separately; the selected subsystem lives in Media3.

### 6. [rdkcentral/aamp](https://github.com/rdkcentral/aamp)

**Language / role:** C++ with JavaScript interfaces; Advanced Adaptive Media Player for RDK and embedded playback.

Study a network-facing adaptive engine layered over GStreamer. **C2:** its [architecture document](https://raw.githubusercontent.com/rdkcentral/aamp/dev_sprint_25_2/ARCHITECTURE.md) separates protocol fragment collectors, DRM, buffering/ABR, events, and the Universal Video Engine interface. **C1:** the [retry and timeout internals](https://github.com/rdkcentral/aamp/blob/dev_sprint_25_2/AAMP-Retry-Timeout-Internals.md) distinguish connection failures, first-byte delays, stalled transfers, and insufficient throughput. A low-bandwidth abort drives a bitrate reduction instead of the same retry path used for other failures.

**C3:** download recovery is coupled to available buffered playback time, so network policy has to respect a consumption deadline. This makes AAMP valuable for studying failure handling under embedded streaming constraints. These entry points use the verified `dev_sprint_25_2` branch; the repository explicitly notes that development branch names change.

### 7. [bilibili/ijkplayer](https://github.com/bilibili/ijkplayer)

**Language / role:** C with Java and Objective-C integration; Android/iOS playback engine derived from ffplay.

**Historical study selection:** the repository still advertises FFmpeg 3.4 and the 0.8.8 integration line; this report does not infer current dependency support or active maintenance from its popularity.

Study the adaptation of a native playback loop to mobile decoder and output systems. **C1:** [the playback core](https://raw.githubusercontent.com/bilibili/ijkplayer/master/ijkmedia/ijkplayer/ff_ffplay.c) gives queued packets a serial that changes on flushing, alongside abort state and queue accounting. This makes stale work and discontinuities visible in the implementation. **C3:** that same queue code recycles packet-list allocations; the mobile engine adds MediaCodec and VideoToolbox paths rather than merely wrapping a command-line player.

The [change history](https://raw.githubusercontent.com/bilibili/ijkplayer/master/NEWS.md) records accurate seeking, decoder reconfiguration crashes, thread competition, frame dropping, and cache changes. Its substantial mobile-specific evolution justifies treating it as its own project, while acknowledging the ffplay ancestry.

### 8. [wang-bin/QtAV](https://github.com/wang-bin/QtAV)

**Language / role:** C++/Qt; multimedia playback library over FFmpeg. **Historical / reduced-maintenance selection:** the README says its author is no longer developing QtAV, although patches are welcome.

Study the orchestration that sits between a demuxer and independently running audio/video consumers. **C1:** [the demux thread](https://raw.githubusercontent.com/wang-bin/QtAV/master/src/AVDemuxThread.cpp) manages bounded seek tasks, blocked packet queues, buffering, pause state, and end-of-stream coordination. Its separate treatment of audio-only or cover-art playback is an instructive special case. **C2:** the repository documents extensible decoders and audio outputs, multiple video outputs, and both Qt widget and QML integrations.

The demux thread is a better engineering entry point than the small player demo: it exposes the concurrency and lifecycle work required to turn FFmpeg primitives into a reusable Qt engine. The author's suggested successor SDK is not assumed to provide equally inspectable engine source and is not listed here.

## Browser streaming and decoding engines

### 9. [video-dev/hls.js](https://github.com/video-dev/hls.js)

**Language / role:** TypeScript/JavaScript; HLS playback engine using Media Source Extensions.

Study the interaction among playlist loading, transmuxing, bitrate choice, and browser buffer state. **C1:** the [design document](https://raw.githubusercontent.com/video-dev/hls.js/master/docs/design.md) explains discontinuity-driven remuxer resets, timestamp drift correction, detection of partially buffered fragments, and recovery from buffer holes. **C3:** adaptive selection compares estimated fragment completion against buffer starvation; workers and transferable objects reduce main-thread work and messaging overhead. **C2:** event-connected controllers separate stream scheduling, alternate audio, source buffers, keys, and manifests.

This is especially useful for understanding why successfully downloading a segment does not imply successful playback. The document is a conceptual map; individual algorithms and configuration defaults should be checked against the release under study rather than treated as permanently fixed.

### 10. [shaka-project/shaka-player](https://github.com/shaka-project/shaka-player)

**Language / role:** JavaScript; adaptive DASH/HLS engine with encrypted-media and offline playback support.

Study the normalization of asynchronous browser media operations into an explicit engine API. **C1:** [MediaSourceEngine](https://raw.githubusercontent.com/shaka-project/shaka-player/main/lib/media/media_source_engine.js) synchronizes and serializes operations where required while permitting independent work to proceed concurrently. It owns source-buffer queues and tracks requested timestamp offsets separately from browser-adjusted values. These are concrete examples of correctness across asynchronous APIs and browser quirks.

**C2:** the implementation presents a common layer over MediaSource, SourceBuffers, text rendering, and transmuxing; the surrounding project uses it within a player supporting multiple manifests, DRM systems, and offline content. Start with this implementation before the [architecture diagrams](https://shaka-project.github.io/shaka-player/docs/api/tutorial-architecture.html), which map the wider data flow and ownership relationships. The canonical repository is `shaka-project`, not one of the downstream forks surfaced by search.

### 11. [Dash-Industry-Forum/dash.js](https://github.com/Dash-Industry-Forum/dash.js)

**Language / role:** JavaScript; DASH reference-client playback engine.

Study a standards-oriented player whose dependency direction is explicitly documented. **C2:** the [architecture guide](https://dashif.org/dash.js/pages/developers/architecture/) separates infrastructure in `core/`, manifest semantics in `dash/`, and playback in `streaming/`. The streaming layer queries manifests through `DashAdapter`, while optional subsystems have separate bundles. **C3:** one stream object per presentation period and one processor per media type organize the schedule/load/append loop; metrics from that loop feed adaptive bitrate rules.

This is a useful comparison with hls.js: the study focus is multi-period DASH structure, dependency injection, and metric-driven representation choice. The guide identifies concrete controllers and `SourceBufferSink`, so readers can move from a high-level lifecycle to the implementation without treating the entire project as one undifferentiated player.

### 12. [canalplus/rx-player](https://github.com/canalplus/rx-player)

**Language / role:** TypeScript; browser DASH/Smooth Streaming engine with no required UI.

Study how a player preserves protocol-independent logic while moving work between execution environments. **C2:** the [file architecture](https://github.com/canalplus/rx-player/blob/dev/FILES.md) describes common manifest and transport interfaces, feature selection, browser compatibility functions, and an MSE abstraction that handles environments with or without direct MSE access. **C3:** the core can run in a Web Worker while public API and DRM logic remain on the main thread. This boundary is particularly relevant to applications on constrained devices.

The same source map points out integration, browser-conformance, and memory tests, giving readers several ways to examine whether architectural boundaries survive actual playback. Native HLS through the browser's direct-file path should not be confused with an independently implemented HLS pipeline in this project.

### 13. [videojs/http-streaming](https://github.com/videojs/http-streaming)

**Language / role:** JavaScript; Video.js HTTP Streaming (VHS), the HLS/DASH engine integrated with Video.js.

Study streaming policy inside a larger player ecosystem without counting its UI framework as another engine. **C3:** the [adaptive switching explanation](https://raw.githubusercontent.com/videojs/http-streaming/main/docs/bitrate-switching.md) combines measured segment-transfer bandwidth with display dimensions; it describes resolution headroom and a fallback when no candidate survives filtering. The optimization target includes avoiding wasted downloads for a small display, not simply selecting the largest available stream.

**C2:** the same selection policy is replaceable through `selectPlaylist`, while the repository exposes rendition information, bandwidth/throughput measurements, and request hooks to integrating applications. Its documented standard-media-element integration and separate DRM plugin show the division of responsibilities. The README identifies the maintenance status as stable and documents Video.js compatibility; this is a project statement, not a separate audit of every browser/version combination.

### 14. [xqq/mpegts.js](https://github.com/xqq/mpegts.js)

**Language / role:** TypeScript/JavaScript; live MPEG-TS/FLV playback through transmuxing and MSE.

Study continuous transport streams rather than only segment-manifest playback. **C1:** the [API guide](https://raw.githubusercontent.com/xqq/mpegts.js/master/docs/api.md) documents filling audio timestamp gaps, coordinating loading with `sourceopen`, and cleaning buffered history. **C3:** it exposes the explicit tradeoff between a network-jitter stash buffer and live latency, plus separate worker options for transmuxing and MSE. Live latency can be controlled by buffer chasing or playback-rate adjustment.

The repository acknowledges its flv.js origin but documents substantial separate development: MPEG-TS support, MSE-in-worker execution, new transport codec support, and rate-based live synchronization. flv.js is therefore not separately counted. A material limitation is that the repository still lists seeking in static MPEG-TS files as unfinished; this selection is strongest for studying live transport playback.

### 15. [zhaohappy/libmedia](https://github.com/zhaohappy/libmedia)

**Language / role:** TypeScript with WebAssembly codec modules; monorepo containing AVPlayer and its media pipelines.

Study a browser engine that can use WebCodecs, software decoding, or MSE. **C2:** [AVPlayer's implementation](https://raw.githubusercontent.com/zhaohappy/libmedia/master/packages/avplayer/src/AVPlayer.ts) composes I/O, demux, audio/video decode, and audio/video render pipelines, with configurable loaders and execution options. **C3:** the repository explains why demux and asynchronous I/O live in TypeScript while individual codecs are separate, demand-loaded Wasm modules; multithreading can fall back when shared-memory facilities are unavailable.

The [AVPlayer package](https://github.com/zhaohappy/libmedia/tree/master/packages/avplayer) identifies the relevant subsystem. Its source also documents worker separation for I/O/demux, audio, and video when shared-memory multithreading is unavailable. This supplies a different architecture from MSE-only stream controllers. Much of the detailed material is in Chinese; no independent throughput claims or long-term compatibility guarantees are inferred here.

## Audio playback, mixing, and scheduling

### 16. [mackron/miniaudio](https://github.com/mackron/miniaudio)

**Language / role:** C; device abstraction plus a higher-level playback engine, resource manager, and node graph.

Study how a compact distribution can still contain distinct engine layers. **C2:** the [programming manual](https://miniaud.io/docs/manual/index.html) describes data sources, graph nodes, sounds, and an independently usable resource manager. **C1:** resource jobs have per-object execution counters to preserve ordering across worker threads; the manual also states object-address stability and asynchronous seek/read obligations. **C3:** decoding is paged and scheduled off the audio thread, and loaded resources can be shared by reference.

The manual is unusually candid about constraints: its job queue uses a spinlock, and posting jobs can involve semaphore-related locking. It should not be described as a universally lock-free engine. ABI compatibility between releases is also explicitly not guaranteed. These documented tradeoffs make it a useful study of real-time aspirations versus actual synchronization contracts.

### 17. [jarikomppa/soloud](https://github.com/jarikomppa/soloud)

**Language / role:** C++; portable game-audio playback and mixing engine.

Study the distinction between a logical playing sound and a voice that consumes mixer work. **C3:** the [concepts guide](https://solhsa.com/soloud/concepts.html) explains virtual voices: audible priority determines which sounds are actually mixed, while protected voices receive special treatment. It also connects output-buffer size to latency and underrun risk. **C1:** voice groups make multi-voice commands atomic, avoiding starts in different audio buffers when the audio thread interrupts sequential application calls.

**C2:** sources, voice handles, and groups provide reusable controls for effects, music, and spatial sound. Handle uniqueness prevents an old handle from silently controlling a later sound occupying the same voice slot. The guide contains some older feature descriptions, so use it for these documented concepts rather than assuming every listed limit or resampler option describes the newest source.

### 18. [kcat/openal-soft](https://github.com/kcat/openal-soft)

**Language / role:** C++ implementing a C API; software engine for spatial and streaming audio playback.

Study the renderer beneath a standardized source/buffer interface. **C2:** OpenAL sources, streaming buffers, and EFX effects support multiple application and platform backends; this is an audio renderer rather than a container-decoding library. **C3:** the [annotated configuration](https://raw.githubusercontent.com/kcat/openal-soft/master/alsoftrc.sample) explains CPU-specific implementations, mix-ahead versus latency, and a substantive spatial-rendering choice: per-source HRTF filtering versus mixing into an ambisonic intermediate and filtering that result.

The [core source tree](https://github.com/kcat/openal-soft/tree/master/core) provides an implementation map through voice handling, conversion, HRTF, effects, and mixer components. The project acknowledges descent from an older OpenAL implementation, but its software mixing, spatial rendering, and backend architecture constitute substantial independent evolution. No advertised numerical latency or speed claim is needed for its inclusion.

### 19. [RustAudio/rodio](https://github.com/RustAudio/rodio)

**Language / role:** Rust; composable audio playback library using CPAL for device output.

Study sample-stream composition and the boundary between producers and the audio consumer. **C2:** the [library introduction](https://github.com/RustAudio/rodio/blob/master/src/lib.rs) makes `Source` the common abstraction for decoded files, generated tones, buffers, and user implementations. **C1:** [the mixer implementation and tests](https://raw.githubusercontent.com/RustAudio/rodio/master/src/mixer.rs) normalize channel count/sample rate and admit pending sources at an interleaved-frame boundary. The comments explain that starting mid-frame can swap the intended left/right channel phase; a specific test exercises that case.

**Current caveat:** the repository warns that its core engine is being rewritten and that examples on the development branch can differ from published releases. The source remains valuable, but readers should select a consistent revision and documentation version. The report does not equate Rust's memory safety with complete audio correctness.

### 20. [tesselode/kira](https://github.com/tesselode/kira)

**Language / role:** Rust; backend-independent game-audio engine with clocks, tracks, effects, and spatial playback.

Study expressing musical timing separately from wall-clock application updates. **C2:** the repository demonstrates clock-relative sound starts, property tweens, shared static sound data, and routing into effect-bearing mixer tracks. The [Sound trait contract](https://docs.rs/kira/latest/kira/sound/trait.Sound.html) supplies an extension boundary for custom active sounds.

**C3:** that contract prohibits allocation/deallocation in processing methods and separates per-buffer preparation from per-frame processing. It also defines when a finished sound can be unloaded. These are concrete constraints for extending a real-time engine, not merely claims that Rust is fast. The repository documents limited WebAssembly support, including the absence of streaming sounds there because that path depends on threads. This is strongest as a study of expressive desktop/game audio scheduling and real-time extension contracts.

### 21. [naudio/NAudio](https://github.com/naudio/NAudio)

**Language / role:** C#; .NET audio library, particularly its sample-provider playback/mixing model and output backends.

Study managed-code audio composition and native-device interoperability. **C2:** [MixingSampleProvider](https://raw.githubusercontent.com/naudio/NAudio/master/NAudio.Core/Wave/SampleProviders/MixingSampleProvider.cs) consumes interchangeable `ISampleProvider` inputs, validates compatible channel/sample-rate formats, and supports either finite output or silence-filled continuous output. **C1:** the same implementation makes input-list locking, end-of-input removal, and callback timing visible; these are useful points for examining concurrent control and audio reads rather than assuming all calls are freely concurrent.

**C4:** [release notes](https://raw.githubusercontent.com/naudio/NAudio/master/RELEASE_NOTES.md) span multiple years of WASAPI/ASIO behavior fixes, malformed-file handling, disposal bugs, and target-framework changes, including entries from 2017 through 2026. The repository also describes a major NAudio 3 transition; the cited release history includes the 2.x line, so examples and APIs should be matched to the chosen version.

### 22. [sbooth/SFBAudioEngine](https://github.com/sbooth/SFBAudioEngine)

**Language / role:** Objective-C/Objective-C++ with Swift-facing APIs; Apple-platform audio playback and decoding engine.

Study the gap between successful decoding and correctly timed rendering. **C1:** the [SFBAudioPlayer contract](https://raw.githubusercontent.com/sbooth/SFBAudioEngine/main/Sources/CSFBAudioEngine/include/SFBAudioEngine/SFBAudioPlayer.h) distinguishes decoding completion from rendering completion, transfers exclusive ownership of enqueued decoders, and reports decoder-open failures asynchronously. It states that gapless playback requires matching sample rate and channel count; other formats trigger graph reconfiguration.

**C2:** decoder protocols and decorators feed an AVAudioEngine processing graph, and the repository describes customization of that graph as well as Swift and Objective-C use. The header's queued playback, cancellation, seek, interruption, and graph-change events expose substantial application integration semantics. This is more than a format-binding wrapper. Its documented high-level URL playback is file-based, a useful scope limit when comparing it with network-streaming engines above.

## Tracker and legacy music replay

### 23. [OpenMPT/openmpt](https://github.com/OpenMPT/openmpt)

**Language / role:** C++ with C/C++ library interfaces; monorepo containing OpenMPT, libopenmpt, and their shared tracker replay machinery. **Official read-only GitHub mirror** of the project's Subversion repository.

Study reusable playback of music whose timing and synthesis are encoded as tracker patterns. **C2:** libopenmpt renders the shared replay engine into PCM rather than requiring applications to embed the tracker UI. **C3:** the [public library header](https://raw.githubusercontent.com/OpenMPT/openmpt/master/libopenmpt/libopenmpt.h) explains three distinct input strategies: caller-provided memory, small seekable callback reads, and cached non-seekable input. Their memory and I/O consequences are explicit.

The same header distinguishes integer output with clipping/dithering implications from floating-point headroom and specifies error and allocation ownership across the C boundary. That combination is useful for studying both integration cost and numerical output policy. Count the tracker application and libopenmpt once; they share playback code and evolve together, as the repository states.

### 24. [libxmp/libxmp](https://github.com/libxmp/libxmp)

**Language / role:** C; tracker-module replay library producing PCM, including historical-format behavior emulation.

Study compatibility where reproducing a historical bug can be the correct musical result. **C1:** the [changelog](https://github.com/libxmp/libxmp/blob/master/docs/Changelog) records tracker-specific effect-memory, pattern-loop, and tempo fixes alongside malformed-input crashes, out-of-bounds access, and fuzz-discovered failures. **C4:** that history includes 2015 static-analysis/fuzz fixes and 2025 playback and loader corrections, with explicit ABI-preserving API adjustments and named regression cases.

**C2:** the [API guide](https://xmp.sourceforge.net/libxmp.html) defines independent player contexts, loaded/playing states, subsongs, frame/buffer rendering, and a sample mixer usable for game effects. It also explains the CPU-versus-fidelity choice of hardware-modeled Amiga mixing. This is a separate implementation from OpenMPT, with its own context API and replay decisions; shared test material is evidence of interoperability work, not duplicate repository counting.

## Coverage and search notes

Discovery used more than six distinct live-search formulations, covering native libmpv/LibVLC/GStreamer architecture; browser MSE/HLS/DASH engines; Android Media3 and playback threading; Qt/FFmpeg and mobile engines; RDK adaptive streaming; Rust audio composition and scheduling; C/C++ game-audio engines; Apple gapless playback; tracker replay, fuzzing, and compatibility; and newer WebCodecs/Wasm/continuous-transport players. Later broad engine searches increasingly returned familiar projects, frontends, wrappers, and less-established candidates. The WebCodecs and MPEG-TS searches added libmedia and mpegts.js because they contributed distinct execution and transport models.

Every retained canonical GitHub repository was opened. Each entry also has at least one separately opened primary API, implementation, design, or history source; a second copy of the same README was not counted as independent evidence. Substantive architecture or implementation material was inspected for every entry. Some raw/documentation URLs failed through the browsing service; successful repository views, source headers, or alternate official documentation were used instead, and failed links are not included as evidence.

The selection excludes player skins and straightforward libmpv/LibVLC bindings, tutorial players, awesome lists, codec-only libraries, device-I/O-only libraries, commercial SDKs without inspectable engine implementation, and unrelated streaming servers. FFmpeg/ffplay is an important dependency and ancestor rather than a separate entry in this selection; media-center and whole-browser monorepos were not expanded into additional entries. These boundaries keep the report centered on playback orchestration and reusable engines. They do not imply that excluded codebases lack engineering value.

Repository and documentation observations establish study suitability, not independently measured performance or a complete maintenance/security audit. No candidate code was executed, dependencies installed, or large repositories cloned. Default branches and generated documentation can move; the historical QtAV/ijkplayer caveats, Rodio rewrite warning, GPAC documentation move, and official mirror labels should be preserved when using this guide.
