# Nonlinear video editors and compositing systems

Research date: **2026-10-09**

This selection covers 21 GitHub repositories implementing interactive nonlinear editors, node-based image/video compositors, and reusable timeline or composition engines. It includes one explicitly identified editorial interchange library because its timing and composition model is directly useful when building editing systems. General codecs, players, screen recorders, window-system compositors, and thin wrappers around rendering services are outside scope. Blender and GStreamer are counted once each, with the relevant subsystem identified.

Repository identities, default branches, and archive status were checked through GitHub repository pages or API responses. The linked implementation files and documentation were opened and read. Criteria assessments are engineering judgments grounded in those sources, not claims that every part of a repository is exemplary or production-ready. A recent push alone is not treated as evidence of maturity.

**Criteria legend**

- **C1 — Difficult correctness:** consequential invariants, concurrency, numerical semantics, malformed inputs, or failure recovery.
- **C2 — Reusable abstractions:** substantial models and interfaces supporting multiple editing, rendering, or integration use cases.
- **C3 — Performance with structure:** explicit responses to rendering, playback, memory, or latency constraints within an understandable design.
- **C4 — Sustained evolution:** multi-year evidence accompanied by compatibility work, testing, migration, or deliberate complexity management.

## Interactive editing applications

### 1. [KDE/kdenlive](https://github.com/KDE/kdenlive)

**C++/QML; desktop nonlinear editor. Official GitHub mirror:** the repository identifies KDE Invent as the development home. Particularly useful for studying how a rich editing UI preserves a valid timeline while coordinating an external media engine.

- **C1:** `TimelineModel` is the mutation entry point. Its documented contract requires failed requests to leave the model unchanged. Elementary operations accumulate forward and reverse lambdas; a partially completed group move can therefore roll back without separately simulating the entire edit. Clip extension checks propagate through clip and track constraints. Start with the unusually informative [timeline model header](https://github.com/KDE/kdenlive/blob/master/src/timeline2/model/timelinemodel.hpp).
- **C2:** The same composable operation machinery supports individual and compound edits, while stable object IDs and a hierarchical Qt model expose tracks and clips to QML. The [architecture guide](https://github.com/KDE/kdenlive/blob/master/dev-docs/architecture.md) explains the larger separation between Kdenlive’s application layer, MLT’s timeline/rendering services, and effect libraries.

### 2. [mltframework/shotcut](https://github.com/mltframework/shotcut)

**C++/QML; cross-platform desktop editor built on MLT.** A useful companion to Kdenlive: the underlying media framework is shared, but the application’s timeline model and effect UI integration are separate implementations.

- **C1:** The [multitrack model](https://github.com/mltframework/shotcut/blob/master/src/models/multitrackmodel.cpp) handles trim validity, adjacent blank regions, transition boundaries, locked tracks, and ripple edits across other tracks. Its coordinated MLT playlist mutations and Qt model notifications make off-by-one and model/view consistency problems concrete.
- **C2:** [QmlFilter](https://github.com/mltframework/shotcut/blob/master/src/qmltypes/qmlfilter.h) provides a common interface for typed effect properties, keyframe interpolation, presets, analysis, and undo tracking. Engineers can study how numerous effect-specific interfaces share one bridge to media services instead of each owning a separate parameter and animation system.

### 3. [jliljebl/flowblade](https://github.com/jliljebl/flowblade)

**Python/GTK; multitrack Linux editor using MLT.** Valuable for understanding the practical costs of maintaining a Python editing model alongside a native engine’s representation.

- **C1:** The atomic operations in [edit.py](https://github.com/jliljebl/flowblade/blob/master/flowblade-trunk/Flowblade/src/edit/edit.py) explicitly update both Python clip lists and MLT structures. Cuts and blank insertion account for MLT’s inclusive out points; edit actions also notify synchronization tracking and feed undo/redo. This is a concrete source of cross-language state invariants.
- **C2:** [Sequence](https://github.com/jliljebl/flowblade/blob/master/flowblade-trunk/Flowblade/src/sequence.py) packages the tractor, playlists, audio mix transitions, compositors, proxy references, and special preview tracks into the multitrack object edited by the application. Study how ordinary timeline tracks coexist with a hidden trimming/monitor track. The source also candidly documents design weaknesses, making this a useful tradeoff study rather than an endorsement of every abstraction.

### 4. [OpenShot/openshot-qt](https://github.com/OpenShot/openshot-qt)

**Python/Qt; OpenShot’s editor application.** This repository is distinct from `libopenshot` below: its strongest study material is application state, change propagation, and undo history rather than pixel processing.

- **C1:** [updates.py](https://github.com/OpenShot/openshot-qt/blob/develop/src/classes/updates.py) retains previous values and transaction IDs for reversible changes. It explicitly avoids mutating history-owned payloads during serialization, removes recursively nested history fields, and guards against reentrant undo/redo. These details expose failure modes that simple command-stack examples omit.
- **C2:** `UpdateAction`, `UpdateInterface`, watchers, and `UpdateManager` form a shared change-distribution mechanism for application consumers. The [developer guide](https://github.com/OpenShot/openshot-qt/blob/develop/doc/developers.rst) explains the boundary between this Python interface, the C++ video engine, and the audio library, including the need to match the engine’s Qt version to the selected Python binding.

### 5. [pitivi/pitivi](https://github.com/pitivi/pitivi)

**Python/GTK; GStreamer Editing Services-based editor. Official project mirror of GNOME GitLab.** A strong entry point for studying transactional editing behavior and its tests without beginning in a large C++ renderer.

- **C1:** The [undo implementation](https://github.com/pitivi/pitivi/blob/master/pitivi/undo/undo.py) supports nested operations, rollback on exceptions, mergeable actions, and deferred actions whose prerequisites are not yet restored. It retries those deferred actions and reports unresolved failures rather than silently treating the stack as complete.
- **C2:** Action stacks themselves implement the undoable-action interface, so compound operations compose recursively. Per-project logs expose signals and finalizing actions to coordinate observers and backend updates.

The second entry point is the [undo test suite](https://github.com/pitivi/pitivi/blob/master/tests/test_undo_undo.py), which exercises wrong-state operations, failed undo ordering, nested commits, checkpoints, and dirty-state transitions. These are concrete checks of the abstraction’s behavioral contract; no claim of exhaustive coverage is implied.

### 6. [olive-editor/olive](https://github.com/olive-editor/olive)

**C++/Qt; node-oriented nonlinear editor. Alpha/historical study target:** its README labels the software highly unstable, and GitHub metadata showed the latest repository push in December 2024.

- **C1:** [PreviewAutoCacher](https://github.com/olive-editor/olive/blob/master/app/render/previewautocacher.h) documents asynchronous cancellation semantics: cancellation means a result is no longer wanted, not that execution stops immediately. Callers must handle tickets with no result. Separate audio/video invalidation paths and time ranges expose the correctness problem of editing a graph while background work is pending.
- **C3:** The same subsystem prioritizes caching around the playhead, supports forced ranges, tracks queued/running jobs, and separates immediate frame requests from background caching. This is directly relevant to scrub latency and avoiding unnecessary preview work.

Use the [rendering source directory](https://github.com/olive-editor/olive/tree/master/app/render) to follow the associated render tickets, job tracker, playback caches, project copier, and OpenGL backend. Its architecture is worth studying independently of its release readiness.

### 7. [helospark/tactview](https://github.com/helospark/tactview)

**Java with native components; multitrack desktop editor. Smaller project; recent maintenance is not established:** GitHub reported its latest push in November 2024.

- **C2:** The [TimelineClip abstraction](https://github.com/helospark/tactview/blob/master/tactview-api/src/main/java/com/helospark/tactview/core/timeline/TimelineClip.java) combines interval-aware clips, non-intersecting effect channels, keyframe/value providers, cloning, and serialization. Time scaling changes the effective interval through integration and cached length calculations, making the API substantially richer than a list of media filenames.
- **C1/C3:** [TimelineManagerRenderService](https://github.com/helospark/tactview/blob/master/tactview-core/src/main/java/com/helospark/tactview/core/timeline/TimelineManagerRenderService.java) builds clip-dependency layers and renders work within each layer using futures and a fixed thread pool. It supplies dependent frames to effects, merges audio/video outputs, and returns temporary image buffers in cleanup paths. Study the interaction between dependency ordering, parallelism, and buffer ownership, including its error-handling tradeoffs.

### 8. [heroineworshiper/hvirtual](https://github.com/heroineworshiper/hvirtual)

**C/C++; Cinelerra-HV editing and compositing system.** This is the HV lineage, not a duplicate listing of the CV or GG forks. The Cinelerra community’s [lineage explanation](https://cinelerra-cv.wikidot.com/main:about) identifies this GitHub source repository and distinguishes the independently developed variants.

- **C1:** [RenderEngine](https://github.com/heroineworshiper/hvirtual/blob/master/cinelerra/renderengine.C) explicitly coordinates first-frame locks, separate audio/video render threads, playback interruption, and device teardown. Its synchronization clock uses the audio device when available and a software timer otherwise; comments explain why output devices remain valid until worker threads join.
- **C2:** The engine supports realtime playback and other render contexts, including nested engines that share devices and cache access that can come from the playback engine or local render state. This makes it useful for studying reuse across preview, nested composition, and rendering, together with the lifetime complexity that reuse creates.

The monorepo includes additional media utilities; the relevant subsystem here is `cinelerra/`.

### 9. [salsaman/LiVES](https://github.com/salsaman/LiVES)

**C/GTK with supporting scripts; video editor and VJ system. Historical study target:** the checked default branch was `LiVES-4.0`, with the latest repository push reported in August 2024.

- **C1:** [events.c](https://github.com/salsaman/LiVES/blob/LiVES-4.0/src/events.c) implements time-ordered event copying and insertion, remapping references to effect initialization events, rescaling parameter changes, and detecting inconsistent track/frame arrays. Copying a timeline therefore involves preserving linked lifecycle and parameter relationships, not merely duplicating clips.
- **C2:** The [event API](https://github.com/salsaman/LiVES/blob/LiVES-4.0/src/events.h) represents frames, audio seeks, filter initialization/deinitialization, filter maps, and parameter changes in a common event-list model used by recording, multitrack editing, and playback.
- **C3:** `process_events()` processes state-changing events while allowing preview frames to be dropped, and includes adaptive playback-quality accounting. This provides a distinct study of keeping live playback responsive without simply discarding the event history that determines the image.

### 10. [OpenCut-app/opencut-classic](https://github.com/OpenCut-app/opencut-classic)

**TypeScript/React plus Rust/wgpu; archived original OpenCut editor.** The [current project README](https://github.com/OpenCut-app/OpenCut/blob/main/README.md) points users to this previous implementation while describing a ground-up rewrite. Only the archived implementation is counted here.

- **C2:** [EditorCore](https://github.com/OpenCut-app/opencut-classic/blob/main/apps/web/src/core/index.ts) assembles timeline, commands, playback, scenes, projects, media, rendering, saving, audio, selection, clipboard, and diagnostics managers. Its command reactor performs derived timeline cleanup. This is useful for studying an editor’s application boundary and also the constraints of a singleton core.
- **C1/C3:** The [effects-renderer design](https://github.com/OpenCut-app/opencut-classic/blob/main/docs/effects-renderer.md) separates TypeScript effect definitions and pass selection from Rust-owned GPU resources and execution. It explains single/multiple passes, parameter-dependent blur iterations, sampling-density limits, and coordinate-orientation requirements at canvas import. These are concrete numerical and performance tradeoffs.

Some paths embedded in that design document predate source reorganization; use the directly linked current `EditorCore` file for application navigation.

## Node-based compositing systems

### 11. [NatronGitHub/Natron](https://github.com/NatronGitHub/Natron)

**C++/Qt and Python integration; node-based VFX compositor and OpenFX host.** Particularly strong material for demand-driven rendering, concurrent interactive edits, and cache design.

- **C1:** The [rendering/threading guide](https://github.com/NatronGitHub/Natron/blob/RB-2.6/Documentation/source/maintainers/rendering.rst) explains captured per-render hashes and thread-local context, preventing a render from reading an inconsistent mixture of old and live node state. It also describes coordination when overlapping image regions are already being rendered and cooperative abort handling.
- **C2:** Effects expose regions of definition/interest, required input frames, identity behavior, and metadata through an OpenFX-oriented action model. The same graph supports viewer requests and sequence writers, including temporal effects that request several source frames.
- **C3:** Rendering requests only needed regions, bypasses identity effects, divides supported work into tiles, and reuses RAM/disk cache entries. Viewer scheduling coalesces stale scrub requests. The guide maps each mechanism to concrete engine classes, making it an effective starting point rather than merely a performance feature list.

### 12. [GafferHQ/gaffer](https://github.com/GafferHQ/gaffer)

**C++/Python; node application with an image-compositing subsystem alongside scene and lighting tools.** The selection specifically concerns `GafferImage`, not every scene-processing feature in the repository.

- **C1:** [Merge.cpp](https://github.com/GafferHQ/gaffer/blob/main/src/GafferImage/Merge.cpp) documents deliberate numerical behavior: division with a zero numerator avoids an unusable NaN for the zero-over-zero case, and difference operations account for bitwise equality and NaNs. These choices are tied to compositor semantics and consistency with black-tile shortcuts.
- **C2/C3:** [ImagePlug](https://github.com/GafferHQ/gaffer/blob/main/include/GafferImage/ImagePlug.h) divides images into independently evaluated properties, including channel data, data windows, metadata, views, and deep-sample offsets. Context variables identify the requested tile/channel/view. Scoped removal of irrelevant variables reduces hash-cache pressure. Study how this representation supports reusable nodes while making partial evaluation and caching explicit.

The source also states its linear-color and associated-alpha expectations; callers must respect those contracts rather than assuming arbitrary image data is automatically normalized.

### 13. [blender/blender](https://github.com/blender/blender)

**C++ with Python integration; Blender’s compositor subsystem. Official GitHub mirror.** This monorepo is included once, specifically for `source/blender/compositor`.

- **C1:** The [node-tree evaluator header](https://github.com/blender/blender/blob/main/source/blender/compositor/COM_node_tree_evaluator.hh) explains why operations cannot be fused solely because they are adjacent pixel nodes. Different image domains or scalar/image behavior can change the result: its worked example shows how merging operations can incorrectly change output dimensions.
- **C3:** The evaluator compiles compatible groups into pixel operations and evaluates operations during compilation so subsequent decisions can use already computed results. It tracks node-to-operation mappings and separately handles nested zones and external-input reference counts. This connects an optimization to its semantic restrictions instead of presenting fusion as universally safe.
- **C2:** The [compositor source tree](https://github.com/blender/blender/tree/main/source/blender/compositor) exposes distinct context, result, domain, operation, scheduler, cache, and shader interfaces. It is a substantial example of turning an artist-facing graph into an execution model.

## Editing engines and editorial models

### 14. [mltframework/mlt](https://github.com/mltframework/mlt)

**C/C++; reusable nonlinear editing and media-composition framework.** Study the engine independently of Shotcut, Kdenlive, or Flowblade to understand what those applications inherit and what they implement themselves.

- **C2:** The [framework guide](https://www.mltframework.org/docs/framework/) develops producers, consumers, filters, transitions, playlists, and multitrack tractors as composable services. A playlist can itself act as a producer and be nested or filtered. Chains and links add temporal access for operations that need other frames, where ordinary filters lack the required upstream-seeking interface.
- **C1:** That guide explains reference ownership and why attached effects avoid positional maintenance problems when edits displace timeline content. It makes lifetime and time-coordinate semantics part of the API design.
- **C4:** The [release history](https://github.com/mltframework/mlt/releases) spans inspected releases from 2020 through 2026. Version 7 introduced retiming classes with an explicit migration path; later releases document format/API compatibility fixes, deadlock repairs, and memory/overflow corrections. This is evidence of managed evolution, including acknowledged breaking changes, rather than an age claim based on repository creation.

### 15. [GStreamer/gstreamer](https://github.com/GStreamer/gstreamer)

**C/GObject; GStreamer Editing Services (GES) and its nonlinear engine within the GStreamer monorepo. Official GitHub mirror:** the project’s [news archive](https://gstreamer.freedesktop.org/news/) records the official mirror; current development is on freedesktop GitLab.

- **C1:** The [GESTimeline contract](https://gstreamer.freedesktop.org/documentation/gst-editing-services/gestimeline.html) precisely defines overlapping source intervals, disallows full containment and triple overlaps in the relevant track/layer context, and describes automatic transition creation, adjustment, and removal. It also documents important failure caveats when adding tracks or layers containing existing elements.
- **C2:** The [GES architecture](https://gstreamer.freedesktop.org/documentation/gst-editing-services/) distinguishes user-visible layers from output tracks. A timeline is itself a GStreamer element, and the convenience pipeline supports preview and file rendering, allowing the editing model to participate in larger pipelines.
- **C3:** Timeline mutations are committed to the processing graph explicitly, so repeated drag updates need not immediately rebuild media output.

The verified source entry is [subprojects/gst-editing-services](https://github.com/GStreamer/gstreamer/tree/main/subprojects/gst-editing-services). Older standalone GES repositories are not counted separately.

### 16. [OpenShot/libopenshot](https://github.com/OpenShot/libopenshot)

**C++ with language bindings; reusable timeline, animation, compositing, and playback engine.** Unlike the separately listed editor UI, this library exposes media operations for embedding in other applications.

- **C1:** [Timeline.h](https://github.com/OpenShot/libopenshot/blob/develop/src/Timeline.h) documents strict weak ordering for clips and uses stable sorting to preserve compositing order for tied layer/position values, including loaded project order. It also exposes frame/sample-rate mapping and cache-invalidation epochs—concrete concerns when edits and cached output interact.
- **C2:** `Timeline` implements both timeline and reader interfaces, letting a layered composition be consumed through the same frame-reading abstraction used for source media. Clips carry trim ranges, positions, layers, and animated properties; readers, effects, and cache interfaces remain separate. The header’s worked example follows composition through `GetFrame()`.

The [source layout](https://github.com/OpenShot/libopenshot/tree/develop) provides additional navigation into `src`, bindings, examples, and tests. This is a useful boundary for learning reusable media APIs without conflating their contracts with the editor’s project-history UI.

### 17. [AcademySoftwareFoundation/OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO)

**C++/Python; editorial timeline model and interchange library, not a pixel renderer or complete editor.** Included as a clearly bounded supporting component for nonlinear editing systems.

- **C1:** [TimeRange](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/src/opentime/timeRange.h) makes inclusive-start/exclusive-end semantics, inclusive-end conversion, comparison tolerances, and invalid/negative-duration handling explicit. This is useful for studying interval algebra across differing media rates without assuming the name `RationalTime` means arbitrary-precision rational arithmetic.
- **C2:** The [architecture guide](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/architecture.md) separates timeline/track/stack/clip representation, temporal utilities, format adapters, and media-linker plugins. Available media range and selected source range are distinct; nested containers introduce their own coordinate spaces.

The value for an experienced engineer is understanding a reusable editorial representation that can preserve missing media and workflow-specific metadata. Applications remain responsible for media rendering and some validation policies; interchange fidelity should not be confused with a guarantee that every represented edit is renderable.

## Programmatic and browser composition engines

### 18. [Zulko/moviepy](https://github.com/Zulko/moviepy)

**Python/NumPy; programmatic video editing and composition.** A comparatively approachable implementation for tracing time-dependent clips, layering, masks, and audio composition without a desktop UI.

- **C1/C2:** [CompositeVideoClip](https://github.com/Zulko/moviepy/blob/master/moviepy/video/compositing/CompositeVideoClip.py) is itself a video clip. It orders layers, derives duration and frame rate from inputs, composes audio, recursively constructs masks, and handles mismatched mask/frame dimensions. The distinction between global clip time and background-relative time is visible in the frame function.
- **C3:** The implementation offers mask memoization with an explicit speed/memory tradeoff and deletes consumed cached mask data. This is a concrete optimization to inspect; it does not establish any realtime performance guarantee.
- **C4:** The [v2 migration guide](https://github.com/Zulko/moviepy/blob/master/docs/getting_started/updating_to_v2.rst) explains the shift to out-of-place `with_` methods, effect classes, and fewer dependencies. The inspected [release history](https://github.com/Zulko/moviepy/releases) includes 2017 Python compatibility fixes and 2025 dependency/API fixes, grounding the multi-year evolution claim.

### 19. [remotion-dev/remotion](https://github.com/remotion-dev/remotion)

**TypeScript/React with native rendering support; programmatic video composition and rendering monorepo.** The relevant subsystem is `packages/renderer`, together with its composition model. This is a source-study recommendation; its licensing should be evaluated separately for any adoption.

- **C1:** [render-frames.ts](https://github.com/remotion-dev/remotion/blob/main/packages/renderer/src/render-frames.ts) validates dimensions, frame counts, and rates; coordinates cancellation; manages browser-crash replacement and bounded frame retries; and distinguishes ownership of caller-provided browsers from internally opened ones during cleanup. These are substantive orchestration and failure-lifetime problems.
- **C3:** The same implementation manages a pool of browser pages and configurable concurrency, assembles frame-indexed asset information, and integrates off-thread video cache/thread settings. Engineers can trace where parallelism meets deterministic output ordering and resource cleanup.
- **C2:** The [renderFrames API](https://www.remotion.dev/docs/renderer/render-frames) exposes composition configuration, ranges, callbacks, reusable browser instances, and frame-buffer output, supporting batch rendering and custom consumers beyond the bundled studio interface.

### 20. [WebAV-Tech/WebAV](https://github.com/WebAV-Tech/WebAV)

**TypeScript/WebCodecs; browser editing and composition SDK.** Its media abstraction and encoder orchestration offer a different architecture from both DOM-based rendering and desktop native engines. The inspected code is the public SDK, not the separately advertised Pro product.

- **C2:** [IClip](https://github.com/WebAV-Tech/WebAV/blob/main/packages/av-cliper/src/clips/iclip.ts) supplies video/audio at a requested microsecond timestamp through an asynchronous `tick`, alongside readiness, metadata, cloning, optional non-destructive splitting, and destruction. Sprites add placement and timing, while the compositor consumes those abstractions.
- **C1/C3:** [Combinator](https://github.com/WebAV-Tech/WebAV/blob/main/packages/av-cliper/src/combinator.ts) sorts sprites by layer, resolves output duration, rejects indeterminate infinite output, and handles cancellation/error cleanup. It explicitly throttles the video encoder queue to avoid exhausting GPU memory and checks codec/configuration support before use.

Study the ownership and backpressure boundaries rather than adopting the README’s comparative speed claim as a verified benchmark. Browser and codec availability remain implementation constraints.

### 21. [etro-js/etro](https://github.com/etro-js/etro)

**TypeScript; framework-independent browser video-composition library.** A smaller substantive alternative built around layers, effects, canvas output, and Web Audio/MediaRecorder integration.

- **C2:** The [base-layer contract](https://github.com/etro-js/etro/blob/master/src/layer/base.ts) distinguishes activation, seeking, playback progression, rendering, stopping, and serialization. Custom layer implementations can participate in the movie lifecycle without owning the entire playback loop.
- **C1:** The [Movie implementation](https://github.com/etro-js/etro/blob/master/src/movie/movie.ts) coordinates asynchronous readiness of layers/effects, guards competing playback/refresh states, redirects audio for recording, and handles browser behavior when no media audio tracks exist. The layer base also counts repeated attachment occurrences so array-proxy operations do not prematurely detach a still-referenced layer.

The interesting study is lifecycle coordination across browser APIs and an extensible composition model. Its MediaRecorder-oriented export path should not be mistaken for the same offline, frame-scheduled architecture used by WebAV or Remotion.

## Coverage, search method, and limitations

Discovery used more than six distinct live web-search formulations. Angles included general nonlinear-editor/timeline architecture; node-based VFX compositors; MLT and GStreamer editing frameworks; Python editors and composition libraries; Java editors; Rust timeline/compositor projects; WebCodecs/browser editing SDKs; Cinelerra lineage; and historical compositors and VJ/multitrack systems. Follow-up searches checked official mirrors and project moves. Repository pages/API metadata then established canonical identities, and direct source/document reads established the retained technical claims. Stars were not used as quality evidence.

The resulting mix includes large C/C++ application communities, GTK/Python applications, a small Java editor, event-based live editing, node-graph evaluation, editorial interchange, and browser/programmatic composition. MLT-based applications are retained separately because their editing models and UI abstractions are substantive; their common backend is identified. OpenShot’s UI and engine are also independent repositories with different study targets. OpenCut’s rewrite and classic implementation are not double-counted. Cinelerra forks are not padded into separate entries.

Important boundaries and exclusions:

- **Lumiera:** inspected project material identifies a pre-alpha NLE and substantial design work, but this search did not establish an official substantive GitHub mirror. It was excluded under the GitHub requirement. See its [project status](https://lumiera.org/) and [design overview](https://lumiera.org/documentation/design/).
- **New Rust/browser editors and AI editing frontends:** discovery surfaced many projects, but claims about intended architectures, feature roadmaps, or wrappers were insufficient for inclusion without comparable implementation evidence. The search did not establish that these projects lack merit.
- **Other historical compositors:** searches for Ramen/Jahshaka and related projects did not yield sufficiently verified canonical implementations and additional primary evidence within this pass. They were not substituted with unofficial forks.
- **Adjacent media software:** general FFmpeg processing, standalone effects collections, players, live-stream routing servers, and lossless trimming utilities were omitted to keep the category centered on editing/composition systems. OpenTimelineIO is the explicit boundary inclusion and is labeled accordingly.

Later discovery passes mostly repeated the same ecosystems or surfaced immature/adjacent projects; LiVES was the final distinct architecture added. Some project sites timed out, including LiVES’ homepage and a Blender developer-documentation endpoint; repository implementation sources supplied the retained evidence instead. No repositories were cloned, dependencies installed, candidate code executed, or benchmarks reproduced. Branch links are moving references, and maintenance observations describe the research date. This report is a source-reading selection guide, not a comparative product test or a certification of correctness.
