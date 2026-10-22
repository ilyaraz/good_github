# Media container demultiplexers and multiplexers

Research date: **2026-10-09**.

This selection covers implementations that separate encoded media into tracks/packets, assemble those tracks into containers, or supply substantial container parsing and serialization machinery for those operations. It includes file containers, fragmented streaming containers, MPEG transport streams, and broadcast MXF. Codec implementations, network protocols, and players are included only where a clearly identified subsystem performs container work. The 24 repositories below are study candidates, not a claim that every component is uniformly exemplary or suitable for untrusted input without further review.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, timestamp/numerical semantics, malformed inputs, or failure recovery.
- **C2 — Abstractions:** substantial reusable interfaces and models supporting multiple applications.
- **C3 — Performance:** concrete memory, throughput, I/O, or latency constraints addressed through understandable architecture.
- **C4 — Evolution:** documented development across years together with compatibility, testing, or complexity management.

Criteria assignments are engineering judgments grounded in the linked primary material. Repository pages were opened to verify identities; additional source or documentation was read for every entry. Maintenance status is stated where explicitly established, rather than inferred from popularity or a recent push.

## General frameworks and packaging systems

### 1. [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg)

**Language/role:** C; `libavformat` demuxers, muxers, and media I/O. **Official GitHub mirror**; the repository identifies its upstream and directs contributions outside GitHub.

Study how a common packet API accommodates many container formats without hiding ownership and timing obligations.

- **C1:** The public API distinguishes presentation and decoding timestamps, represents unknown timestamps explicitly, and specifies stream time bases and monotonic DTS requirements. Muxer initialization can change the requested time base; trailer writing flushes outstanding data. Reference ownership also differs between ordinary and interleaved packet writing.
- **C2:** `AVFormatContext`, `AVStream`, format descriptors, configurable options, and callback-backed `AVIOContext` separate container operations from byte transport. The same abstractions support file reading, custom I/O, and remuxing.

Entry point: the extensively documented [libavformat public API](https://github.com/FFmpeg/FFmpeg/blob/master/libavformat/avformat.h), especially its demuxing, muxing, and interleaved-writing sections.

### 2. [GStreamer/gstreamer](https://github.com/GStreamer/gstreamer)

**Language/role:** predominantly C; native container elements in the multimedia monorepo. **Official GitHub mirror of the freedesktop GitLab repository.** Relevant starting subsystem: `gst-plugins-good/gst/isomp4` and the core aggregator base class.

- **C1:** `GstAggregator` documents an explicit lock order, buffer-reference validity, aggregate-thread restrictions, and ordered delivery of stream-start, caps, segment, and EOS events. These are concrete concurrency contracts for multi-input muxers, not merely a plugin interface.
- **C2:** The base class handles queued pads and serialized events while subclasses implement aggregation. This lets container-specific code reuse stream coordination.
- **C3:** QTMux's implementation notes explain normal, fragmented, fast-start, and robust recording strategies, including when output must be seekable and when sample data moves through a temporary file.

Entry points: [aggregator implementation and contract](https://github.com/GStreamer/gstreamer/blob/main/subprojects/gstreamer/libs/gst/base/gstaggregator.c) and [QTMux's “Hacker notes”](https://github.com/GStreamer/gstreamer/blob/main/subprojects/gst-plugins-good/gst/isomp4/gstqtmux.c).

### 3. [gpac/gpac](https://github.com/gpac/gpac)

**Language/role:** C; MP4Box and the GPAC filter framework, including ISOBMFF demuxing, muxing, and segmentation.

Study the conversion of application-specific import/export code into a configurable processing graph.

- **C2:** Filters exchange PIDs, packets, properties, and events; muxers and demuxers use the same graph machinery as other processing components. Automatic connection resolution and dynamic reconfiguration make this a substantial application-building abstraction.
- **C3:** The design describes reference-counted packets, memory recycling, queues, and blocking rules that prevent full downstream buffers from producing unbounded work.
- **C4:** The historical rearchitecture document explicitly describes the first major core redesign after 15 years, removal of duplicated import code, and compatibility goals for existing command lines and binary outputs. This is evidence of complexity management, not just age.

Entry points: [historical rearchitecture rationale](https://github.com/gpac/gpac/wiki/Rearchitecture) and the [ISOBMFF mux filter](https://github.com/gpac/gpac/blob/master/src/filters/mux_isom.c). The historical wiki is marked frozen; use it for rationale rather than current command syntax.

### 4. [axiomatic-systems/Bento4](https://github.com/axiomatic-systems/Bento4)

**Language/role:** C++; MP4 reading/writing SDK and packaging tools.

The linear reader is a useful smaller entry into a substantial atom-, movie-, track-, and sample-oriented library.

- **C1:** Per-track trackers retain sample indexes, next decoding timestamps, EOS state, ownership of sample tables, and fragment-specific seek locations. Seeking and advancing a fragment must keep these states consistent.
- **C2:** `AP4_LinearReader` separates sample traversal from `SampleReader`, including a decrypting implementation. Applications can read a chosen track or consume samples across tracks through a shared interface.
- **C3:** The API supports traversal in physical storage order and retrieving sample metadata without reading its payload; buffer-fullness accounting makes the cost of servicing different tracks visible.

Entry point: [AP4_LinearReader and AP4_DecryptingSampleReader](https://github.com/axiomatic-systems/Bento4/blob/master/Source/C%2B%2B/Core/Ap4LinearReader.h).

### 5. [shaka-project/shaka-packager](https://github.com/shaka-project/shaka-packager)

**Language/role:** C++; media demuxing and packaging for DASH/HLS, with native MP4 and other format implementations.

- **C1:** The MP4 muxer handles delayed initialization from the first sample, empty streams, edit-list offsets, and protection-scheme-specific encryption-box versions. These show how container correctness depends on sample timing and encryption metadata together.
- **C2:** `MediaHandler` formalizes permitted input/output graph shapes and carries stream information, samples, segment boundaries, and cue events through typed processing stages. Initialization, dispatch, and downstream flushing have explicit contracts.
- **C3:** Separate single-segment, multi-segment, and low-latency segmenter implementations sit behind the MP4 muxer, making output policy a visible architectural choice.

Entry points: [MediaHandler](https://github.com/shaka-project/shaka-packager/blob/main/packager/media/base/media_handler.h) and [MP4Muxer](https://github.com/shaka-project/shaka-packager/blob/main/packager/media/formats/mp4/mp4_muxer.cc).

### 6. [ireader/media-server](https://github.com/ireader/media-server)

**Language/role:** C/C++; multimedia library collection. Relevant subsystems are `libmpeg` for MPEG-TS/PS and `libmov` for MP4, alongside other container libraries.

This is useful for studying compact native container libraries embedded in a wider streaming stack.

- **C1:** The TS demuxer interprets adaptation-field lengths, PCR/OPCR fields, program information, continuity counters, and final buffered PES data. Its flush path has codec-specific handling to deliver trailing video data. The examined input function assumes a complete 188-byte packet and uses assertions: callers must honor that contract; this is not evidence of comprehensive adversarial-input hardening.
- **C2:** The MOV reader exposes callback-based track discovery, packet delivery with PTS/DTS, caller-supplied allocation, and seek results that report the actual position. I/O and payload allocation are separated from container parsing.

Entry points: [TS demuxer](https://github.com/ireader/media-server/blob/master/libmpeg/source/mpeg-ts-dec.c) and [MOV reader API](https://github.com/ireader/media-server/blob/master/libmov/include/mov-reader.h).

## Focused native container libraries

### 7. [webmproject/libwebm](https://github.com/webmproject/libwebm)

**Language/role:** C++; WebM/Matroska parsing and muxing. **Official mirror of the WebM project's Chromium-hosted repository**, explicitly marked mirror-only.

- **C1:** The muxer distinguishes nanosecond frame timestamps from cluster timecode units, requires initialization before use, and requires cue insertion after a frame to compute the correct block number. Frame duration can change the selected block representation.
- **C2:** `IMkvWriter` abstracts writing, position, seekability, and element notifications. `Segment`, `Cluster`, tracks, frames, and cues provide reusable models rather than binding construction to one file-writing application.
- **C3:** Live/file modes, configurable cluster size and duration, chunked output, and queued-frame draining expose practical latency, indexing, and output-layout tradeoffs.

Entry point: [muxer interfaces and Segment/Cluster contracts](https://github.com/webmproject/libwebm/blob/main/mkvmuxer/mkvmuxer.h). This entry counts the repository once, including its parser and muxer components.

### 8. [xiph/ogg](https://github.com/xiph/ogg)

**Language/role:** C; libogg, the reference Ogg container implementation, independent of the codecs carried inside it.

- **C1:** Framing code verifies capture patterns and checksums, waits for incomplete headers/bodies, resynchronizes after corruption, detects page-sequence holes, and reconstructs packets continued across pages. Granule positions are assigned to the last complete packet, a subtle container timing rule.
- **C2:** Separate synchronization and logical-stream state machines let applications multiplex multiple streams while keeping page framing independent of codec interpretation.
- **C4:** The changelog records evolution from 2002 through 2025, including multi-page assembly fixes, large-packet bounds, changed flushing heuristics with test updates, fuzzing support, undefined-behavior fixes, allocation-failure handling, and CI improvements.

Entry points: [framing implementation](https://github.com/xiph/ogg/blob/main/src/framing.c) and [CHANGES](https://github.com/xiph/ogg/blob/main/CHANGES).

### 9. [l-smash/l-smash](https://github.com/l-smash/l-smash)

**Language/role:** C; L-SMASH's official ISO base media/QuickTime muxing and demuxing library.

Study a detailed C API that makes the difference between media samples and presentation timelines explicit.

- **C1:** The sample contract distinguishes decoding and composition timestamps, non-output samples, and timeline mappings. It specifies ownership transfer when appending samples and requires flushing each track's pooled samples before finishing a movie or creating a fragment. The seeking API cautions that the nearest random-access point does not necessarily suffice to decode the requested sample correctly.
- **C2:** Opaque roots, file modes, tracks, media parameters, sample descriptions, and constructed timelines form reusable layers for both reading and writing, including fragmented output.

Entry point: [lsmash.h](https://github.com/l-smash/l-smash/blob/master/lsmash.h), especially Sample, Media, and Timeline APIs. Selected for its substantive implementation/API design; no claim of current release cadence is made.

## Broadcast files and transport streams

### 10. [ebu/bmx](https://github.com/ebu/bmx)

**Language/role:** C++ with C dependencies; MXF reading, writing, essence extraction, and rewrapping. **Community continuation of BBC BMX**; the repository explains that the original BBC repository was archived. Only this lineage entry is counted.

- **C1:** `MXFFileReader` distinguishes complete and incomplete files, searches partitions for usable metadata, determines or infers essence wrapping, and separates failures while opening and validating a file. Broadcast files introduce cross-partition metadata and index obligations beyond simple packet extraction.
- **C2:** File factories, package resolvers, track readers, and low-level libMXF/libMXF++ layers support different MXF profiles and application entry points.
- **C4:** The changelog spans dated snapshots from at least 2017 onward and records index-table repairs, sanitizer findings, growing-file support, format-compatibility fixes, and subsequent EBU platform work. This also verifies substantive continuation beyond a renamed fork.

Entry points: [MXFFileReader](https://github.com/ebu/bmx/blob/main/src/mxf_reader/MXFFileReader.cpp) and [changelog](https://github.com/ebu/bmx/blob/main/CHANGELOG.md).

### 11. [tsduck/tsduck](https://github.com/tsduck/tsduck)

**Language/role:** C++; MPEG transport-stream toolkit and reusable demuxing/packetization library.

Study transport signaling and recovery independently from audio/video decoding.

- **C1:** `SectionDemux` validates long-section CRCs, tracks discontinuities and truncation, distinguishes current/next tables, and can detect changed section content with an unchanged version number. Its explicit incomplete-table flushing APIs explain when reconstructed tables may be inconsistent.
- **C2:** PID filters and table, section, and invalid-section handlers separate reassembly from application policy. The developer guide describes how the command-line tools sit over reusable library classes, with demuxing and packetization available to external applications.

Entry points: [SectionDemux](https://github.com/tsduck/tsduck/blob/master/src/libtsduck/dtv/demux/tsSectionDemux.h) and the [developer guide](https://tsduck.io/docs/tsduck-dev.html), particularly demux/packetization and plugin development.

### 12. [justdan96/tsMuxer](https://github.com/justdan96/tsMuxer)

**Language/role:** C++; transport-stream remuxing/muxing application, including TS/M2TS and Blu-ray-oriented output.

- **C1:** The muxer couples PCR generation, decoder-buffer timing, PAT/PMT emission, PES packetization, stream PID assignments, and file-block boundaries. Its PCR path computes stuffing/null packets from elapsed time and target bitrate, exposing the arithmetic needed for coherent transport output.
- **C3:** Output buffering, asynchronous-writer coordination, block completion, and separate handling of final buffered bytes make throughput and I/O failure behavior visible. `flushTSBuffer` waits for asynchronous writing before closing/reopening output and checks the final write length.

Entry point: [TSMuxer implementation](https://github.com/justdan96/tsMuxer/blob/master/tsMuxer/tsMuxer.cpp), particularly `writePCR`, `flushTSBuffer`, `finishFileBlock`, and `muxPacket`. This is a specialized application architecture rather than a universal container SDK.

### 13. [asticode/go-astits](https://github.com/asticode/go-astits)

**Language/role:** Go; native MPEG-TS demuxer and muxer.

- **C1:** The demuxer drains accumulated packets at EOF while tolerating incomplete trailing groups; PAT/PMT updates alter program and elementary-stream maps. The muxer manages wrapping continuity/version counters and packet capacity when adaptation fields and PES headers compete for space.
- **C2:** Standard `io.Reader`/`io.Writer`, functional options, packet-skipping hooks, and custom packet-group parsers make the library useful in file and streaming applications without tying it to one input mechanism.

Entry points: [demuxer.go](https://github.com/asticode/go-astits/blob/master/demuxer.go) and [muxer.go](https://github.com/asticode/go-astits/blob/master/muxer.go). Material limits are documented in source: context checks do not interrupt an already-blocked read, and the examined muxer leaves multiple-program and 192-byte packet support unimplemented.

## Java container models

### 14. [sannies/mp4parser](https://github.com/sannies/mp4parser)

**Language/role:** Java; MP4 parsing, construction, authoring, and streaming modules. The canonical repository is `sannies/mp4parser`, not a guessed repository named after the Maven artifact.

- **C1:** Building a movie requires translating per-track durations into a movie timescale and calculating chunk and encryption auxiliary-data offsets after layout is known. The builder exposes the coupling among track edits, sample tables, and final byte positions.
- **C2:** The repository's documented workflow composes codec-specific `Track` objects into a `Movie`, passes that to an `MP4Builder`, and writes a generic `Container`. Track transformations support operations such as cropping and appending without decoding frames.

Entry point: [DefaultMp4Builder](https://github.com/sannies/mp4parser/blob/master/muxer/src/main/java/org/mp4parser/muxer/builder/DefaultMp4Builder.java). The repository README supplies the corresponding authoring workflow and explicitly distinguishes container manipulation from codec processing.

### 15. [jcodec/jcodec](https://github.com/jcodec/jcodec)

**Language/role:** Java; multimedia library with native MP4, Matroska, MPEG-PS/TS, and other container components. Relevant subsystem: `org.jcodec.containers`.

- **C1:** `MP4DemuxerTrack` simultaneously walks chunk offsets, sample sizes, decoding durations, composition-offset runs, sync samples, and edits. Seeking must restore several independent cursors, and packet construction converts media timestamps into edited presentation time.
- **C2:** Track objects return `MP4Packet` values through a seekable channel abstraction and support caller-provided buffers. Container state, packet data, frame classification, and I/O remain separate concepts usable by decoding, editing, or extraction clients.

Entry point: [MP4DemuxerTrack](https://github.com/jcodec/jcodec/blob/master/src/main/java/org/jcodec/containers/mp4/demuxer/MP4DemuxerTrack.java). A good code-reading exercise is to compare sequential reads with `seekPointer` and `gotoSyncFrame`; the selection does not imply uniform input validation throughout the larger codec library.

## Browser and JavaScript/TypeScript implementations

### 16. [gpac/mp4box.js](https://github.com/gpac/mp4box.js)

**Language/role:** TypeScript in the inspected source; JavaScript-facing MP4 parsing, sample extraction, construction, and fragmentation. This is a separate implementation from the C GPAC repository.

- **C1:** `ISOFile` tracks incomplete parsing, once-only readiness notifications, sample-table construction, extraction progress, and fragment sequence numbers. Segmentation validates positive limits and requires consistent sample counts across the tracks being fragmented.
- **C2:** Callbacks for readiness, samples, segments, and errors expose multiple workflows over the same box/sample model. Extraction and segmentation are configured per track rather than hardwired into a player.
- **C3:** `MultiBufferStream`, configurable retention of media-data bytes, and explicit sample-buffer accounting address incremental network input and browser memory use.

Entry point: [ISOFile implementation](https://github.com/gpac/mp4box.js/blob/main/src/isofile.ts). It is particularly useful for comparing push-based progressive parsing with the pull-oriented native readers above.

### 17. [videojs/mux.js](https://github.com/videojs/mux.js)

**Language/role:** JavaScript; MPEG-TS/AAC to fragmented-MP4 transmuxing and container inspection. The README labels maintenance **Stable**; its older FLV path is explicitly in maintenance mode.

- **C1:** Audio/video assembly must reconcile decode and presentation timestamps, audio and video clock rates, trimmed audio, silence insertion, GOP alignment, and fragment sequence numbers. The source makes these transformations explicit before emitting `moof`/`mdat` data.
- **C2:** Stream stages separate transport parsing, elementary-stream processing, segment construction, and coalescing; clients receive media plus timing/metadata events.
- **C4:** The dated changelog documents years of compatibility and correctness work, including IE11 fixes, 64-bit integer API changes, malformed ADTS handling, rollover-stream fixes, and caption behavior changes with migration detail.

Entry points: [MP4 transmuxer](https://github.com/videojs/mux.js/blob/main/lib/mp4/transmuxer.js) and [changelog](https://github.com/videojs/mux.js/blob/main/CHANGELOG.md).

### 18. [Vanilagy/mediabunny](https://github.com/Vanilagy/mediabunny)

**Language/role:** TypeScript; native browser-oriented media reading, writing, and conversion, with muxers/demuxers beneath optional WebCodecs processing.

- **C2:** Sources and targets handle byte access, format-specific demuxers/muxers handle container structure, and packet/sample APIs support higher-level conversion. The documentation explains how conversion composes reading and writing while checking output-track and codec compatibility.
- **C3:** Lazy reads, streamed output, encoder backpressure, and coordinated reading/writing address large-file memory use and pipeline throughput. These are documented mechanisms; no unverified speed comparison is asserted here.

Entry points: [technical overview within the introduction](https://mediabunny.dev/guide/introduction#technical-overview) and [writing-media guide](https://mediabunny.dev/guide/writing-media-files). The author identifies this as the successor unifying `mp4-muxer` and `webm-muxer`; those predecessors are not counted separately. C4 is intentionally not inferred from their lineage alone.

## Rust demuxing and parsing

### 19. [pdeljanov/Symphonia](https://github.com/pdeljanov/Symphonia)

**Language/role:** Rust; multimedia demuxing framework alongside audio decoding. The relevant components are the format crates and `symphonia-core` format interfaces, not the audio algorithms.

- **C1:** `FormatReader` specifies that packets belong to one track, that successful seeking invalidates decoder state, and that accurate seeking lands at or before the target. `ResetRequired` means the track list must be examined again and decoders recreated; EOF has a distinct result.
- **C2:** A shared trait exposes packets, tracks, metadata revisions, chapters, attachments, and underlying media-source ownership across the format implementations. Applications can filter tracks and choose decoding policy independently of demuxing.

Entry point: [FormatReader API and behavioral contract](https://docs.rs/symphonia-core/0.6.1/symphonia_core/formats/trait.FormatReader.html). The repository reports different support levels by format; this selection does not treat every demuxer as equally complete.

### 20. [mozilla/mp4parse-rust](https://github.com/mozilla/mp4parse-rust)

**Language/role:** Rust with a C API; ISO BMFF parsing and sample-index machinery for media consumers. This is demuxing infrastructure rather than a muxer or complete playback stack.

- **C1:** The parser uses fallible allocation collections, checked offset arithmetic, bounded-reader types, and detailed status codes for malformed sizes, timescales, descriptors, and unsupported features. Its C-facing structures make representation and borrowed-data lifetime concerns explicit.
- **C2:** A Rust media context and separate C API provide track information, codec configuration, timing, and sample-table/index access through caller-supplied I/O. The boundary is reusable across a native application's demuxing and decoding stages.

Entry points: [parser implementation](https://github.com/mozilla/mp4parse-rust/blob/master/mp4parse/src/lib.rs) and [C API](https://github.com/mozilla/mp4parse-rust/blob/master/mp4parse_capi/src/lib.rs). The inspected code also supports image-container cases; inclusion here rests on its MP4 track/sample functionality.

## Go file and fragmented-media libraries

### 21. [Eyevinn/mp4ff](https://github.com/Eyevinn/mp4ff)

**Language/role:** Go; MP4 parsing/writing and tools, with emphasis on fragmented media used by streaming systems.

- **C2:** File, initialization segment, media segment, fragment, and box models provide both semantic and structural views. Encoding modes distinguish writing the segment model from preserving the box tree, useful for applications ranging from inspection to repackaging.
- **C3:** Lazy `mdat` decoding avoids loading payload bytes and explicitly requires seekable input. Buffered file writing reduces small-box write calls while allowing large media-data writes to bypass a redundant copy. Fragment optimization can move repeated sample values into default fields.
- **C1:** The file parser tracks misplaced boxes and enforces supported `moof`/`mdat` relationships; the API documents that a failed decode may still return a partially populated file.

Entry point: [mp4/file.go](https://github.com/Eyevinn/mp4ff/blob/master/mp4/file.go), including decode modes, encoding modes, and `WriteToFile`.

### 22. [abema/go-mp4](https://github.com/abema/go-mp4)

**Language/role:** Go; MP4 box reading/writing and traversal infrastructure. This is a lower-level foundation for demuxers and muxers, not a codec or automatic playback pipeline.

- **C1:** Recursive reading checks child sizes against their parent and payload size against file size. Parsing carries QuickTime compatibility and metadata-key context through nesting, showing that a box's interpretation can depend on its enclosing and preceding structure.
- **C2:** `ReadHandle` separates decoding a payload, copying its raw data, and expanding children. A callback receives box paths and contextual information, letting applications inspect, selectively traverse, or rewrite container structures without one mandatory in-memory representation.

Entry point: [read.go](https://github.com/abema/go-mp4/blob/master/read.go). Its explicit seekable-reader contract is relevant when assessing whether an application can use it directly on a live network stream.

### 23. [bluenviron/mediacommon](https://github.com/bluenviron/mediacommon)

**Language/role:** Go; shared media entities and format helpers for the Blue Environment streaming projects. Focus here: `pkg/formats/fmp4`.

This is deliberately a study of the layer above generic MP4 boxes. It uses `abema/go-mp4` for box serialization, and is not presented as another independent low-level box parser.

- **C1:** Part serialization lays out multiple track fragments, computes media-data positions, then patches `trun` data offsets relative to `moof`. Track serialization derives flags from actual samples and uses versioned fields for base decoding time and signed composition offsets.
- **C2:** `Part`, `PartTrack`, and sample structures express fragmented media in stream-processing terms, hiding box assembly from callers while retaining sequence numbers, track IDs, decode bases, durations, sync status, and payloads. The repository identifies multiple consuming streaming libraries/applications.

Entry points: [part.go](https://github.com/bluenviron/mediacommon/blob/main/pkg/formats/fmp4/part.go) and [part_track.go](https://github.com/bluenviron/mediacommon/blob/main/pkg/formats/fmp4/part_track.go).

## Elixir pipeline components

### 24. [membraneframework/membrane_mp4_plugin](https://github.com/membraneframework/membrane_mp4_plugin)

**Language/role:** Elixir; MP4 parsing/serialization and MP4/CMAF muxer elements for Membrane.

- **C1:** The CMAF muxer documents why video segments must start on keyframes, how synchronized outputs follow one video track, and why more than one video track is disallowed in that synchronization arrangement. Requested segment duration cannot override the available keyframe boundaries.
- **C2:** Input/output pad mappings support combined audio/video output or separate synchronized tracks. Finalization events and segment metadata let downstream components integrate the muxer into adaptive-streaming pipelines.
- **C3:** Chunks relax independent-playability requirements to reduce delivery latency; the implementation describes player-sensitive chunk-duration constraints and how chunk collection changes while waiting to finalize a segment.

Entry point: [CMAF muxer implementation and extensive module documentation](https://github.com/membraneframework/membrane_mp4_plugin/blob/master/lib/membrane_mp4/muxer/cmaf.ex). The repository also documents sink requirements and fixture-playback checks; it should not be treated as a drop-in muxer for an arbitrary file sink.

## Coverage, search method, and limitations

Discovery used live web search across more than six distinct formulations: general media-framework muxer/demuxer architecture; Rust MP4/Matroska parsing; JavaScript/TypeScript WebCodecs and transmuxing; Go MPEG-TS/MP4 libraries; Java ISO parser/authoring APIs; standalone Ogg/WebM/L-SMASH libraries; broadcast MXF/BMX; and alternative Elixir, Python, and C# ecosystems. Additional searches checked canonical owners, project succession, and non-GitHub migrations. Later queries increasingly returned wrappers, duplicate lineages, or projects outside the requested hosting scope, so the selection stopped at 24 substantive repositories.

Primary evidence was read from repository pages, implementation files, API contracts, official design documents, and changelogs. GitHub's read-only fetch interface was used where web-rendered source pages failed or exposed mostly navigation. All retained repository identities were verified by opening their canonical GitHub pages. Source links refer to inspected paths, generally on moving default branches; the Symphonia API link is versioned.

Important scope choices:

- **MKVToolNix is omitted despite strong category fit.** Its [official source page](https://mkvtoolnix.download/source.html) points to Codeberg; an official substantive GitHub mirror was not established. Unofficial mirrors were not substituted.
- The archived BBC BMX predecessor is represented by its EBU continuation. Mediabunny's predecessor muxers are represented by the successor. FFmpeg, GStreamer, and libwebm remain eligible because their official substantive GitHub mirrors were verified and labeled.
- Codec-only libraries, FFmpeg language bindings, player applications without a separately inspected container implementation, tutorial muxers, and awesome-lists were not added to fill language or count targets. Python and C# searches did not produce a stronger independently verified native implementation for this selection; that is a search limitation, not a claim that none exists.
- Lower-level parsing libraries are identified as such. `mediacommon` depends on `go-mp4`, but contributes a separate semantic fragment-assembly layer; both are retained to make that architectural boundary inspectable.

No repositories were cloned, dependencies installed, candidate code executed, or benchmarks run. C3 means the inspected design addresses a concrete performance constraint, not that measured superiority was established. C4 is assigned only where historical changes and compatibility/testing/complexity evidence were read. Other entries may also qualify, but that was not assumed. The review samples meaningful implementation paths and does not establish comprehensive correctness, security, conformance, or current support commitments.
