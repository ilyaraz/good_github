# Audio and video codecs

Research date: **2026-10-09**.

This selection covers 26 substantive GitHub codebases implementing audio or video compression, decompression, or reusable codec infrastructure. It spans delivery codecs, professional editing formats, speech and music coding, lossless audio, compact decoders, managed-language implementations, and neural audio compression. Framework monorepos appear once, with the relevant subsystem identified. This is an engineering study guide, not a ranking or a claim that every component is exemplary.

Criteria legend:

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, malformed input, or recovery behavior.
- **C2 — Reusable abstractions:** substantial interfaces and components useful across applications or codec implementations.
- **C3 — Performance with structure:** concrete latency, throughput, memory, or computational constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility management, testing, or complexity control; repository age alone does not qualify.

Criterion assignments below are engineering judgments grounded in the linked primary material. Each repository page was opened, and each entry has an independently inspected implementation or technical documentation source. Branch links are moving references; the explicitly versioned FDK AAC source is an exception.

## Codec frameworks and multi-format implementations

### [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg)

**C and assembly; multi-format codec library and multimedia tools. Official GitHub mirror.** Focus on `libavcodec`, rather than treating the command-line application as the entire project. This is an unusually broad study of how unrelated codec algorithms fit a common packet/frame lifecycle.

- **C1:** The send/receive interface is a state machine: both directions cannot simultaneously return `EAGAIN`, elapsed time cannot make an operation ready, and end-of-stream requires a defined draining transition. These are precise progress and buffering invariants, not merely error-code conventions. [API contract](https://ffmpeg.org/doxygen/trunk/group__lavc__encdec.html).
- **C2:** The same API accommodates audio and video, delayed output, and zero, one, or multiple outputs per input, using reference-counted packets and frames. The linked contract explains why this abstraction survives different codec dataflows.
- **C3:** The developer guide describes portable C kernels plus architecture-specific implementations and requires `checkasm` coverage for new assembly. [Developer documentation](https://ffmpeg.org/developer.html).

Entry points: the API contract and developer documentation above. The repository explicitly identifies itself as a mirror of FFmpeg's upstream Git repository.

### [pdeljanov/Symphonia](https://github.com/pdeljanov/Symphonia)

**Rust; audio decoding, demuxing, and metadata framework.** Study the relationship between codec crates and `symphonia-core`; the monorepo is counted once. Its typed audio interface offers a useful comparison with C codec APIs.

- **C1:** `AudioDecoder` distinguishes discardable packet errors from reset-required changes and unrecoverable failures. Implementors must clear their output buffer on errors, and seeking requires resetting discontinuous decoder state. These contracts prevent stale audio and incorrect reuse of prediction history.
- **C2:** The trait separates codec parameters, packet decoding, borrowed output buffers, final verification, and a zero-copy `PacketRef` path. Codec support is independently selectable through crates and features, rather than hardwired into one playback application.

Entry point: [audio codec traits and contracts](https://raw.githubusercontent.com/pdeljanov/Symphonia/main/symphonia-core/src/codecs/audio.rs). The repository's support classifications distinguish conformance-tested implementations from less complete ones; the framework's breadth should not be read as equal maturity for every codec.

### [jcodec/jcodec](https://github.com/jcodec/jcodec)

**Java; independent audio/video codec and container implementations.** Focus on the H.264 decoder for a readable managed-runtime treatment of a complex video standard, while recognizing the repository's documented profile and performance limits.

- **C1:** `H264Decoder` keeps distinct short- and long-term reference pictures, applies reference marking, waits for slice tasks, deblocks the completed picture, and only then updates references. Correct ordering and picture lifetime are central concerns.
- **C2:** The decoder extends a shared `VideoDecoder` abstraction and delegates to frame readers, slice decoders, and a deblocking filter; it accepts both byte streams and already-separated NAL units. This is reusable codec machinery, not just a Java binding to FFmpeg.

Entry point: [H.264 decoder implementation](https://raw.githubusercontent.com/jcodec/jcodec/master/src/main/java/org/jcodec/codecs/h264/H264Decoder.java). Its README explicitly cautions about performance relative to native implementations; no speed claim is made here.

## Video delivery codecs

### [webmproject/libvpx](https://github.com/webmproject/libvpx)

**C, assembly, and C++ tests; VP8/VP9 SDK. Official mirror of the WebM upstream.** Useful for studying a shared codec interface spanning two format generations and multiple CPU implementations.

- **C1:** The decoder API specifies decode-order input, fragmented-input lifetimes, output iterator validity, capability checks, and conditions affecting initialization thread safety. [Decoder interface](https://raw.githubusercontent.com/webmproject/libvpx/main/vpx/vpx_decoder.h).
- **C2:** Decoder interfaces advertise optional capabilities, including external buffers and frame threading, while preserving common initialization and frame retrieval operations.
- **C4:** The changelog documents 2024–2026 ABI-compatible and ABI-breaking releases, a bit-exact encoding test script, architecture equivalence fixes, and race/overflow repairs. That is concrete compatibility and validation history. [Changelog](https://raw.githubusercontent.com/webmproject/libvpx/main/CHANGELOG).

Entry points: decoder interface and changelog above. GitHub labels the repository as a public mirror; upstream review happens elsewhere.

### [videolan/dav1d](https://github.com/videolan/dav1d)

**C and assembly; AV1 decoder. Official read-only VideoLAN mirror.** Especially valuable for tracing parallel decoding without losing track of frame dependencies and API backpressure.

- **C1:** The scheduler combines ordered task insertion, pending-task queues, mutexes, and atomic progress notifications. Comments explain why newly runnable work must reset task traversal. [Task scheduler](https://raw.githubusercontent.com/videolan/dav1d/master/src/thread_task.c).
- **C3:** Thread count and maximum frame delay are separately configurable, exposing a throughput/latency tradeoff. The API also makes draining, picture allocation, and `EAGAIN` handling explicit. [Decoder API](https://raw.githubusercontent.com/videolan/dav1d/master/include/dav1d/dav1d.h).

Entry points: task scheduler and decoder API above. The repository names `code.videolan.org` as its origin; this entry counts the decoder once, not as a separate GitHub fork.

### [xiph/rav1e](https://github.com/xiph/rav1e)

**Rust and assembly; AV1 encoder.** A strong comparison with C encoders because the project provides an explicit map from encoder concepts to modules.

- **C1:** Entropy writing, coding context, partition selection, reconstruction, and rate-distortion decisions are separate but interdependent modules. The project also identifies fuzz targets and encode/decode tests against both dav1d and aom, which address interoperability rather than only self-consistency.
- **C3:** The architecture isolates CPU-feature selection and assembly bindings from motion estimation, transforms, filters, and high-level encoding. This makes optimized kernels and the surrounding algorithmic decisions separately inspectable.

Entry point: [source architecture guide](https://github.com/xiph/rav1e/blob/master/doc/STRUCTURE.md), including direct links to the implementation and cross-decoder tests. The guide is a navigation aid, not evidence that every module or optimized path has equivalent test coverage.

### [AOMediaCodec/SVT-AV1](https://github.com/AOMediaCodec/SVT-AV1)

**Primarily C, with assembly and C++ tests; scalable AV1 encoder. Official organization-hosted GitHub mirror; canonical development URL is GitLab.** The verified GitHub repository contains substantive source, design documents, and tests, rather than only a relocation notice.

- **C1:** The design restricts each control-process type to one instance to avoid incoherent decisions and deadlocks. Resource managers pass reusable objects through empty/full FIFOs, making producer/consumer ownership central to correctness.
- **C3:** The encoder explicitly separates process, picture, and picture-segment parallelism. Control stages and data-processing stages have different scaling rules, providing a concrete architecture for studying throughput bottlenecks.

Entry point: [encoder design](https://github.com/AOMediaCodec/SVT-AV1/blob/main/Docs/svt-av1-encoder-design.md). The repository's canonical GitLab notice should guide contributions and checks for the newest upstream state.

### [cisco/openh264](https://github.com/cisco/openh264)

**C/C++ and assembly; H.264 encoder and decoder.** Particularly useful for integration with interactive applications because its API documentation discusses incomplete pictures and recovery decisions.

- **C1:** The decoder walkthrough separates return status from the output-buffer status, distinguishes parsing from reconstruction, and demonstrates explicitly triggering pending reconstruction. Error handling can require requesting a new IDR picture; successful input consumption alone does not establish valid output.
- **C2:** Encoder and decoder interfaces expose initialization, configuration, frame processing, and parsing-only use, with concrete integration examples. These support applications beyond the bundled command-line programs.

Entry point: [codec API and lifecycle examples](https://raw.githubusercontent.com/cisco/openh264/master/codec/api/wels/codec_api.h). The repository README lists known size and rate-control limitations, which should be checked for a prospective workload.

### [ultravideo/kvazaar](https://github.com/ultravideo/kvazaar)

**C; HEVC encoder.** Its dependency-aware work queue is a particularly approachable subsystem for studying parallel codec execution.

- **C1:** The queue implementation documents lock-order rules for jobs, dependencies, and the queue itself. Jobs maintain unresolved-dependency counts, reverse dependencies, reference counts, and explicit execution states.
- **C3:** Worker threads execute ready jobs while dependency completion releases further work. This turns encoder parallelism into an inspectable scheduling mechanism, rather than scattering synchronization through every coding operation.

Entry point: [thread queue implementation](https://raw.githubusercontent.com/ultravideo/kvazaar/master/src/threadqueue.c). The repository also documents speed/quality presets and a reusable library API; these are useful context for exploring which encoder tasks feed the queue.

### [strukturag/libde265](https://github.com/strukturag/libde265)

**C++ implementation with a C API; HEVC decoder.** Good for studying the boundary between internal parallelism and externally safe API use.

- **C1:** The API requires callers to serialize operations on each decoder context. Starting internal WPP/tile workers does not remove that ownership rule. The distinction is explicit and prevents a common integration error.
- **C2:** Applications can feed byte-stream data or NAL units, advance decoding, retrieve images, and flush through a shared decoder context. This allows different demuxers and playback systems to use the same implementation.
- **C3:** The repository documents wavefront/tile parallelism and CPU-specific acceleration as separate mechanisms.

Entry point: [decoder API, ownership, and input operations](https://raw.githubusercontent.com/strukturag/libde265/master/libde265/de265.h). Its conformance statement is qualified in the README; it should not be turned into a blanket claim of perfect HEVC coverage.

### [fraunhoferhhi/vvenc](https://github.com/fraunhoferhhi/vvenc)

**C++; H.266/VVC encoder with a C interface.** Study how a computationally expensive standard is exposed through practical presets, rate control, and a small application-facing lifecycle.

- **C1:** The README explicitly discusses floating-point contraction changing encoded output across builds and provides a build option for bit-exactness. The API separately specifies caller-owned payload capacity and retry behavior when output memory is insufficient.
- **C2:** Opaque encoder instances, YUV planes, access units, timestamps, and configuration objects separate codec internals from application storage and delivery.
- **C3:** The project documents frame/task parallelism, speed/quality presets, and single-/two-pass variable-rate control rather than presenting a single undifferentiated encoding mode.

Entry point: [public API template](https://raw.githubusercontent.com/fraunhoferhhi/vvenc/master/include/vvenc/vvenc.h.in). The numerical reproducibility and parallelism discussion is in the repository README.

### [fraunhoferhhi/vvdec](https://github.com/fraunhoferhhi/vvdec)

**C++; H.266/VVC decoder with a C interface.** Complementary to VVenC: this is a distinct decoder implementation and repository, with different buffering and validation concerns.

- **C1:** Returned frames may remain referenced internally. External allocators must retain each plane until the corresponding unreference callback; the API also exposes decoded-picture hash verification and distinguishes retryable input starvation from restart-required errors.
- **C2:** The interface carries per-plane strides, bit depth, timestamps, video-usage information, and reference-decoder timing metadata, allowing applications to preserve semantics beyond the pixel array.
- **C3:** Thread count, parallel parsing delay, and SIMD selection are explicit parameters, making performance policy visible at the boundary.

Entry point: [API template and external-buffer contract](https://raw.githubusercontent.com/fraunhoferhhi/vvdec/master/include/vvdec/vvdec.h.in). The repository documents Main10 support and a conformance-bitstream testing option.

## Professional and intermediate video formats

### [gopro/cineform-sdk](https://github.com/gopro/cineform-sdk)

**C/C++; full-frame wavelet video codec and SDK. Legacy professional codec codebase.** This adds a substantially different compression family from block-based inter-frame delivery codecs. The README's platform-validation examples are historical; current platform maintenance is not inferred from them.

- **C2:** Encoder/decoder SDKs support multiple pixel layouts and high-bit-depth workflows, with distinct metadata, sample-encoding, and asynchronous-pool components. The complete implementation is the subject here, not just the educational WaveletDemo.
- **C3:** Independent frames are dispatched across an encoder pool with a configurable queue. The pool source explains why preparation cannot safely change while worker encoders are busy, connecting throughput design to lifecycle restrictions.

Entry point: [encoder pool implementation](https://raw.githubusercontent.com/gopro/cineform-sdk/master/EncoderSDK/EncoderPool.cpp). The repository README also explains retained older bitstreams and interlaced processing paths, useful context for the SDK's complexity.

### [AcademySoftwareFoundation/openapv](https://github.com/AcademySoftwareFoundation/openapv)

**C; Advanced Professional Video reference encoder/decoder.** A useful modern counterpoint to CineForm: intra-frame coding, high-bit-depth formats, tiling, and partial decoding aimed at recording and editing workflows.

- **C1:** The bitstream reader tracks end-of-buffer failures explicitly, and callers must inspect the failure marker rather than treating returned bits as automatically valid. [Bitstream primitives](https://raw.githubusercontent.com/AcademySoftwareFoundation/openapv/main/src/oapv_bs.c).
- **C3:** The project combines tile-based parallel processing and architecture-specific kernels. Its thread pool has explicit worker states, task/result signaling, and allocator ownership, providing a small, inspectable performance subsystem. [Thread pool](https://raw.githubusercontent.com/AcademySoftwareFoundation/openapv/main/src/oapv_tpool.c).

Entry points: bitstream primitives and thread pool above. Format-level statements about avoiding visible degradation are not treated here as mathematical losslessness or independently measured quality results.

## Conventional audio: speech, music, and lossless coding

### [xiph/opus](https://github.com/xiph/opus)

**C and assembly; interactive speech and music encoder/decoder.** Useful for studying a stateful codec that spans different signal types and latency needs within one public API.

- **C1:** Encoder state must persist across frames; the API fixes allowable frame durations, bounds packet storage, and distinguishes discontinuous transmission from errors. Packet-loss concealment and forward-error-correction behavior add recovery semantics beyond straightforward decompression.
- **C2:** Caller-allocated or library-allocated state, integer/float sample interfaces, application modes, and runtime controls let the same codec serve communications and stored audio without exposing the entire implementation.

Entry point: [Opus public API and usage contracts](https://raw.githubusercontent.com/xiph/opus/main/include/opus.h). The repository separates SILK, CELT, and newer neural support; the API is a useful starting point before following those subsystems.

### [xiph/vorbis](https://github.com/xiph/vorbis)

**C; Vorbis reference implementation.** Especially useful for learning the boundary between transform blocks, compressed packets, and sample-accurate output.

- **C1:** Synthesis handles short/long block transitions with different overlap-add paths, detects packet-sequence discontinuity, tracks granule positions, and trims partial final output without rewinding beyond available samples. [Block and synthesis implementation](https://raw.githubusercontent.com/xiph/vorbis/main/lib/block.c).
- **C2:** The public API separates stream information, DSP state, blocks, analysis, synthesis, and PCM retrieval, letting applications choose lower-level integration instead of a file-only interface. [Codec interface](https://raw.githubusercontent.com/xiph/vorbis/main/include/vorbis/codec.h).

Entry points: block processing and codec interface above.

### [xiph/flac](https://github.com/xiph/flac)

**C with C++ interfaces; FLAC reference encoder/decoder and metadata tooling.** Study `libFLAC` for lossless reconstruction and streaming state, rather than only the `flac` command-line utility.

- **C1:** The decoder distinguishes lost synchronization, seek failure, aborted callbacks, allocation failure, and chained-stream transitions. Sample-accurate seeking and metadata filtering interact with that state machine.
- **C2:** Client callbacks abstract input, output, seeking, metadata, and errors; file convenience APIs supply the same operations internally. [Stream-decoder interface](https://raw.githubusercontent.com/xiph/flac/master/include/FLAC/stream_decoder.h).
- **C4:** The 2022–2025 changelog records interface-version changes, an explicit breaking-change porting path, fuzzing additions, seeking fixes, and validation of re-encoded audio through matching MD5 sums. [Changelog](https://raw.githubusercontent.com/xiph/flac/master/CHANGELOG.md).

Entry points: stream-decoder interface and changelog above.

### [dbry/WavPack](https://github.com/dbry/WavPack)

**C and assembly; lossless and hybrid audio codec.** Its hybrid mode makes this more than another lossless decoder: a correction stream restores information omitted from the primary stream.

- **C1:** Packing must keep predictor/decorrelation state, serialized shaping information, and correction data consistent. The implementation explicitly separates block packing from entropy coding and documents correction metadata used for lossless reconstruction. [Packing implementation](https://raw.githubusercontent.com/dbry/WavPack/master/src/pack.c).
- **C4:** The 2024–2026 changelog records multithreaded stress-test coverage, a small-buffer deadlock fix, fuzz-discovered failures, and raw-decoder bounds repairs. These show evolution of correctness controls alongside concurrency. [Changelog](https://raw.githubusercontent.com/dbry/WavPack/master/ChangeLog).

Entry points: packing implementation and changelog above. The README additionally documents callback I/O and stress testing of C versus assembly implementations.

### [google/liblc3](https://github.com/google/liblc3)

**C with a Python validation implementation; LC3/LC3 Plus audio coding.** A good study in organizing a low-latency codec around bounded frames and separately testable signal-processing stages.

- **C1:** The project validates the C implementation against a Python implementation and specification intermediate values, and includes round-trip fuzzing. That is stronger numerical evidence than listening tests alone; it does not imply an independent audit of every mode.
- **C3:** The core separates PCM loading, frame analysis, and bitstream encoding. Analysis invokes attack detection, pitch analysis, spectral processing, and quantization-related stages; state/buffer sizing depends explicitly on frame duration and sample rate.

Entry point: [codec orchestration and memory sizing](https://raw.githubusercontent.com/google/liblc3/main/src/lc3.c). Validation and conformance procedures are described in the repository README.

### [drowe67/codec2](https://github.com/drowe67/codec2)

**C99; low-bit-rate speech codec, with related FreeDV components in the repository.** Focus on `libcodec2` speech coding. This represents bandwidth-constrained radio communications rather than general music distribution.

- **C1:** Mode-specific encoding packs voicing, pitch, energy, and spectral parameters under a fixed bit budget. The 3200 mode combines two analysis frames and asserts that the final bit count matches the mode contract.
- **C2:** A shared codec object dispatches mode-specific encode/decode functions and exposes samples/bits per frame and optional bit-error-rate-aware decoding. This hides different coding modes behind a reusable communications interface.

Entry point: [mode dispatch, parameter packing, and reconstruction](https://raw.githubusercontent.com/drowe67/codec2/main/src/codec2.c). **Maintenance qualification:** the README describes the 2023 refactor and says most existing Codec 2 modes, except 3200 for M17, are not receiving active development while replacement work proceeds. The older `codec2-dev` repository is not counted separately.

### [mstorsjo/fdk-aac](https://github.com/mstorsjo/fdk-aac)

**C/C++ codec core; standalone distribution of Android-derived Fraunhofer FDK AAC.** This is substantive codec source and portability work, not merely an FFI wrapper. The inspected API entry point is deliberately pinned to **v2.0.3**; it is not a description of every later HEAD change.

- **C1:** The decoder distinguishes input-buffer exhaustion from malformed data and has different feed rules for streaming transports and packetized inputs. Callers must also accommodate stream information becoming known during decoding.
- **C2:** Transport selection, raw configuration, buffer filling, frame decoding, and stream-information retrieval are distinct API steps. This supports different container/network integrations without coupling the decoder to a particular file reader.

Entry point: [v2.0.3 decoder API and integration guide](https://raw.githubusercontent.com/mstorsjo/fdk-aac/v2.0.3/libAACdec/include/aacdecoder_lib.h).

## Compact and independent-language audio implementations

### [lieff/minimp3](https://github.com/lieff/minimp3)

**C; compact single-header MPEG audio decoder.** A useful small-codebase contrast to full media frameworks, with real bitstream and numerical complexity rather than a tutorial decoder.

- **C1:** Frame discovery validates candidate headers and free-format frame sizes; Layer III decoding restores and saves the bit reservoir and checks side-information bounds before synthesis. Those cross-frame dependencies make naive random-frame decoding incorrect.
- **C3:** The repository provides scalar and SSE/NEON paths and compile-time controls for output representation and codec subsets. The main decoder keeps frame parsing, reservoir handling, and synthesis visible in a compact implementation.

Entry point: [decoder implementation](https://raw.githubusercontent.com/lieff/minimp3/master/minimp3.h). The README reports conformance-vector testing; its numerical benchmark results are not reproduced or generalized here.

### [lostromb/concentus](https://github.com/lostromb/concentus)

**C#, Java, and Go; substantial Opus ports.** Counted separately from libopus because it implements the codec in other runtimes, including an explicit translation of codec state and arithmetic, rather than only wrapping the C library.

- **C1:** The C# encoder preserves separate SILK/CELT state, fixed-point Q14/Q15 quantities, delay compensation, and partial versus full reset semantics. Its porting comments explain replacing variable-size C struct extensions with managed members.
- **C2:** Encoder/decoder and multistream interfaces expose the codec across managed applications; application modes and control/state objects keep the port reusable.

Entry point: [C# Opus encoder implementation](https://raw.githubusercontent.com/lostromb/concentus/master/CSharp/Concentus/Opus/Structs/OpusEncoder.cs). **Version qualification:** the README identifies the portable implementations' libopus 1.1.2 lineage. Do not assume feature parity with current libopus; newer native-factory support does not erase that distinction.

### [mewkiz/flac](https://github.com/mewkiz/flac)

**Go; FLAC stream, frame, and metadata implementation.** Offers a smaller independent-language route into lossless audio format semantics.

- **C1:** Frame parsing adjusts per-channel bit widths for decorrelated stereo, reconstructs channel relationships, validates CRC-16, and exposes MD5 hashing of decoded samples. These checks cover different layers of integrity, not interchangeable checksums.
- **C2:** `io.Reader`-based frame construction can parse headers separately from sample data, while frame objects expose decoded subframes and stream verification hooks. This supports inspection tools as well as audio decoding.

Entry point: [frame parser, channel reconstruction, and verification](https://raw.githubusercontent.com/mewkiz/flac/master/frame/frame.go). This is an independent implementation, not the Go binding layer for `xiph/flac`.

## Neural audio codecs

### [facebookresearch/encodec](https://github.com/facebookresearch/encodec)

**Python/PyTorch; neural waveform codec research implementation.** A distinct study target for engineers interested in learned compression rather than standardized transform-codec arithmetic.

- **C1:** The model enforces power-of-two codebook cardinality, tracks sample/frame-rate relationships, carries segment scales for normalization, and reconstructs overlapping segments. Correctness includes tensor layout and temporal reconstruction, not just network weights.
- **C2:** `EncodecModel` composes encoder, residual quantizer, decoder, bandwidth policy, and optional segmentation. A separate language-model component maintains streaming state for code probabilities, exposing reusable layers of the compression system.

Entry point: [model composition, segment encoding, and decoding](https://raw.githubusercontent.com/facebookresearch/encodec/main/encodec/model.py). Treat this as research software; the repository's supported-platform and model assumptions are not a universal deployment guarantee.

### [descriptinc/descript-audio-codec](https://github.com/descriptinc/descript-audio-codec)

**Python/PyTorch; neural audio codec with training and inference code.** Particularly useful for inspecting the mechanics of residual vector quantization and variable-rate training.

- **C1:** Vector quantization separates commitment and codebook losses through deliberate gradient detachment, uses a straight-through estimator, and normalizes code vectors before nearest-neighbor selection. The distinction between forward values and backward gradients is central numerical behavior.
- **C2:** `VectorQuantize` and `ResidualVectorQuantize` expose projected latents, discrete codes, reconstructed vectors, and selectable quantizer counts. Quantizer dropout is handled differently in training and inference, allowing reusable rate-dependent representations.

Entry point: [quantization implementation](https://raw.githubusercontent.com/descriptinc/descript-audio-codec/main/dac/nn/quantize.py). Compression-ratio and perceptual-quality marketing claims are not used as selection evidence.

## Search coverage and limitations

Discovery used **16 distinct query formulations** across eight angles: general codec architecture/SIMD/testing; AV1/HEVC/VVC implementations; lossless FLAC/WavPack/ALAC; pure Rust and managed-language decoders; speech/LC3/Opus/Codec 2; neural EnCodec/DAC/Mimi; professional wavelet/APV formats; and official mirrors plus less familiar implementation/testing projects. Repository pages, API headers, source implementations, design documents, and selected changelogs were opened. Follow-up queries increasingly returned already-covered implementations, packaging repositories, application integrations, and small new ports, reducing their value for this selection.

The selection intentionally includes academic, foundation, corporate, and individual-maintainer projects, along with C, C++, assembly, Rust, Java, C#, Go, and Python. Frameworks and codec families are not split into duplicate monorepo entries. VVenC/VVdeC are separate implementations; Concentus and the Go FLAC library are substantive independent-language implementations, not duplicate listings of bindings.

FFmpeg, libvpx, dav1d, and SVT-AV1 are clearly marked mirrors. The SVT-AV1 GitHub tree was retained because it still exposes substantive project source and documentation. An x264 mirror was found, but its official provenance was not sufficiently established in this search, so it was not retained. This report also does not attempt exhaustive coverage of x265, libaom, legacy MPEG/speech codecs, or proprietary/hardware implementations. Their absence is not a judgment of quality.

Excluded classes include FFmpeg build recipes, codec wrappers, transcoders whose main contribution is orchestration, image-only libraries, audio playback/DSP libraries, awesome lists, and unrelated mesh/haptic codecs. New small codec projects surfaced in late searches, but were not added merely to enlarge the list. Two professional-video entries extend the broad-category guide slightly beyond 25 because they add distinct architectures.

The work was read-only research: no candidate repository was cloned, built, benchmarked, or executed. API and code inspection establish useful study subjects, not independent conformance or security certification. C4 is assigned only where inspected multi-year change records substantiate it. Maintenance is not inferred from stars, creation dates, or recent pushes; explicit legacy and limited-maintenance caveats are retained. Mutable source links, upstream mirror lag, and the deliberately pinned FDK AAC version are the main evidence limitations.
