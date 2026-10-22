# Lossless compression libraries

Research date: 2026-10-09

This selection covers 27 GitHub repositories with substantial implementations of reusable lossless compression: general byte streams, entropy coders, embedded systems, numerical arrays, integer sequences, and database strings. Archive libraries appear only where their compression engines themselves merit study. For libraries offering both lossless and lossy operation, only the lossless configuration is in scope. The explanations are engineering assessments grounded in the linked primary material, not benchmark rankings or assurances that every component is exemplary.

Criteria legend:

- **C1 — Correctness:** demanding invariants, concurrency, numerical semantics, malformed input, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and components serving multiple use cases.
- **C3 — Performance:** concrete resource constraints addressed through understandable implementation structure.
- **C4 — Evolution:** documented changes across years together with compatibility, testing, or complexity management.

## General-purpose native libraries

### 1. [madler/zlib](https://github.com/madler/zlib)

**Language/role:** C; DEFLATE, zlib, and gzip compression library.

Study an incremental codec API whose semantics distinguish completion, dictionary negotiation, corruption, and temporarily insufficient buffers. It is particularly useful for understanding how a long-lived C interface accommodates callers with different memory and I/O arrangements.

- **C1, C2:** `z_stream` separates caller-owned input/output buffers from codec state and allocator callbacks. The API specifies repeated `Z_FINISH` calls, nonfatal `Z_BUF_ERROR`, dictionary checksums, and invalid-stream errors. These contracts make partial progress and resource ownership explicit. Entry point: [zlib.h](https://github.com/madler/zlib/blob/develop/zlib.h).
- **C4:** The [ChangeLog](https://github.com/madler/zlib/blob/develop/ChangeLog) records changes across 2022–2026 including distance validation, sanitizer support, portability work, initialized-state copying, and atomic initialization of fixed decoding tables. This is concrete evolution around correctness and compatibility.

### 2. [zlib-ng/zlib-ng](https://github.com/zlib-ng/zlib-ng)

**Language/role:** C with architecture-specific code; independently evolved zlib-derived implementation.

Study how a familiar compression interface can coexist with extensive CPU specialization. This is a substantive implementation with its own native API and optimized algorithms, rather than a packaging fork of zlib.

- **C2:** The project supplies zlib-compatible and native interfaces, including dual-linking support, while retaining configurable build and platform support. Entry point: [project architecture and build overview](https://github.com/zlib-ng/zlib-ng/blob/develop/README.md).
- **C1, C3:** Runtime dispatch assembles a function table from generic fallbacks and detected instruction sets. Atomic pointer publication, barriers, pointer validation, and explicit initialization failure behavior sit beside separate checksum, matching, and inflate implementations. Entry point: [functable.c](https://github.com/zlib-ng/zlib-ng/blob/develop/functable.c).

### 3. [ebiggers/libdeflate](https://github.com/ebiggers/libdeflate)

**Language/role:** C; whole-buffer DEFLATE, zlib, and gzip compression/decompression.

Study the architectural consequences of choosing bounded chunks as the unit of work. Its API is deliberately different from zlib's streaming interface; this makes it especially relevant to storage engines that already know chunk boundaries.

- **C2, C3:** Reusable compressor/decompressor objects operate on caller-provided buffers. The project explains why whole-buffer operation removes suspension overhead and why single-stream processing of large files is outside its intended use. Entry point: [API and design motivation](https://github.com/ebiggers/libdeflate/blob/master/README.md#api).
- **C1, C3:** The decoder documents word-sized bit buffers, speculative preloading versus consumable bits, end-of-input handling, and `SAFETY_CHECK` failures. These comments connect fast paths directly to their invariants. Entry point: [deflate_decompress.c](https://github.com/ebiggers/libdeflate/blob/master/lib/deflate_decompress.c).

### 4. [richgel999/miniz](https://github.com/richgel999/miniz)

**Language/role:** C codec implementation; embeddable DEFLATE/zlib library with optional ZIP support.

Study a compact implementation that exposes low-level codec state as well as convenience APIs. The source repository is split into files; distributable amalgamations provide the familiar single-source integration option.

- **C2, C3:** Heap-free low-level `tdefl`/`tinfl` interfaces, configurable feature removal, zlib-style calls, and optional archive facilities provide several integration levels. Entry point: [integration and API overview](https://github.com/richgel999/miniz/blob/master/readme.md).
- **C1:** The inflater implements resumable execution through explicit coroutine state. Input exhaustion must distinguish “more input may arrive” from inability to make progress, while preserving the bit accumulator across calls. Entry point: [miniz_tinfl.c](https://github.com/richgel999/miniz/blob/master/miniz_tinfl.c).

### 5. [facebook/zstd](https://github.com/facebook/zstd)

**Language/role:** C; reference Zstandard library, dictionary tooling, and command-line utilities.

Study the interaction of LZ matching, Huffman/FSE entropy coding, reusable dictionaries, and framing. The repository is counted once; its library is the relevant subsystem.

- **C1:** Independent frames contain blocks with dependencies on earlier blocks. Window limits, dictionary identifiers, content-size interpretation, checksums, and sequence execution create a rich set of decoder invariants. Entry point: [compression format specification](https://github.com/facebook/zstd/blob/dev/doc/zstd_compression_format.md).
- **C2, C3:** The API separates one-shot calls, reusable contexts, streaming, and reusable prepared dictionaries. It also distinguishes stable APIs from experimental static-linking interfaces and explains unknown or untrusted decompressed sizes. Entry point: [lib/zstd.h](https://github.com/facebook/zstd/blob/dev/lib/zstd.h).

### 6. [lz4/lz4](https://github.com/lz4/lz4)

**Language/role:** C; LZ4 block compression, higher-compression encoder, and frame layer.

Study the boundary between a minimal block codec and a portable, self-describing stream. That separation is valuable when designing a database page format or network framing protocol around a compressor.

- **C1, C2:** The block API requires exact compressed size and a destination capacity; its safe decoder specifies bounded reads/writes and malformed-input errors. Dictionary and streaming state are separate from frame metadata. Entry point: [lib/lz4.h](https://github.com/lz4/lz4/blob/dev/lib/lz4.h).
- **C2, C3:** Frame descriptors add block configuration, checksums, optional content size, and dictionary identification without forcing those costs onto raw-block users. The API also documents memory/cache tradeoffs and freestanding operation. Entry point: [frame format](https://github.com/lz4/lz4/blob/dev/doc/lz4_Frame_format.md).

### 7. [google/snappy](https://github.com/google/snappy)

**Language/role:** C++; throughput-oriented byte compression with a C interface.

Study optimized LZ copying together with adaptable input/output ownership. Its implementation comments are unusually helpful for understanding why ordinary memory-copy intuition can fail inside a decompressor.

- **C1, C3:** An overlapping back-reference may generate repeated bytes as it copies; this differs from both `memcpy` and `memmove`. The implementation separates careful incremental copying from wider copies and vector pattern generation. Entry point: [snappy.cc](https://github.com/google/snappy/blob/main/snappy.cc).
- **C2, C3:** `Source` and `Sink` support noncontiguous input, caller scratch space, direct append buffers, and ownership transfer. Their lifetime contracts permit fewer copies without coupling the codec to one container. Entry point: [snappy-sinksource.h](https://github.com/google/snappy/blob/main/snappy-sinksource.h).

### 8. [google/brotli](https://github.com/google/brotli)

**Language/role:** C core with other language components; Brotli reference implementation.

Study a codec combining LZ77, Huffman coding, and context modeling. Focus on the `c/` encoder/decoder subsystem; language integrations are not separate entries.

- **C1:** The decoder preserves substates while parsing variable-length integers and metablock headers. Separate error codes cover malformed Huffman alphabets, context maps, distances, padding, dictionaries, and allocation failures. Entry point: [c/dec/decode.c](https://github.com/google/brotli/blob/master/c/dec/decode.c).
- **C2:** Opaque decoder instances and one-shot/streaming APIs distinguish more-input, more-output, completion, and failure conditions. This provides a useful model for embedding a complicated bitstream parser. Entry point: [decoder API](https://github.com/google/brotli/blob/master/c/include/brotli/decode.h).

The repository's overview explicitly notes that the Brotli stream itself carries neither a checksum nor an uncompressed length; format validity and end-to-end integrity are different concerns.

### 9. [tukaani-project/xz](https://github.com/tukaani-project/xz)

**Language/role:** C; XZ Utils, specifically the reusable `src/liblzma` subsystem.

Study LZMA/LZMA2 filter composition and a multithreaded decoder constrained by memory and output order. The [official project site](https://tukaani.org/xz/#development) identifies GitHub as the primary repository, rather than an unofficial mirror.

- **C1, C3:** The threaded decoder distinguishes running and cached memory, threading and hard memory limits, ordered output, pending worker errors, and mutex-protected progress. Only the oldest output buffer needs certain partial-progress updates, reducing contention. Entry point: [stream_decoder_mt.c](https://github.com/tukaani-project/xz/blob/master/src/liblzma/common/stream_decoder_mt.c).
- **C2:** The base API defines reusable stream state, allocator ownership, action semantics, and detailed return conditions for applications composing codecs and I/O. Entry point: [liblzma base API](https://github.com/tukaani-project/xz/blob/master/src/liblzma/api/lzma/base.h).

The official site also documents the 2024 compromised release tarballs and subsequent security issues; inclusion is for implementation study, not a blanket endorsement of historical releases.

### 10. [lzfse/lzfse](https://github.com/lzfse/lzfse)

**Language/role:** C; reference LZFSE implementation associated with Apple's Compression library.

Study a smaller Lempel–Ziv/FSE implementation with distinct literal and length/match/distance streams. Its project overview maps the codec, FSE machinery, LZVN support, and public entry points clearly. Entry point: [source layout](https://github.com/lzfse/lzfse/blob/master/README.md).

- **C1:** Packed-header decoding must reconstruct frequency tables and consume precisely the permitted bits. A suspended match must resume before decoding another symbol.
- **C3:** The match execution loop reserves output slack for wider copies and switches to careful handling near the boundary. Separating entropy state, match execution, and public wrappers makes the optimization strategy inspectable. Implementation entry point for both criteria: [lzfse_decode_base.c](https://github.com/lzfse/lzfse/blob/master/src/lzfse_decode_base.c).

No claim of current development activity is inferred from its continued availability.

### 11. [intel/isa-l](https://github.com/intel/isa-l)

**Language/role:** C and assembly; storage-acceleration monorepo, specifically `igzip` compression/decompression.

Study a low-level DEFLATE implementation where explicit workspace, Huffman tables, history, and flush state expose performance decisions to callers. The unrelated erasure-code and RAID subsystems are outside this entry.

- **C2:** The interface supports stateful/stateless use, caller-provided level buffers, selectable Huffman tables, and prepared dictionaries that can be reused across streams. Entry point: [igzip_lib.h](https://github.com/intel/isa-l/blob/master/include/igzip_lib.h).
- **C1, C3:** The compression engine tracks buffered history, dictionary hash state, flush transitions, and input/output progress, avoiding unnecessary history reconstruction while maintaining a valid stream. Entry point: [igzip.c](https://github.com/intel/isa-l/blob/master/igzip/igzip.c).

The repository explicitly assigns callers responsibility for valid API arguments; not all invalid pointers or parameters are checked.

## Embedded, entropy, and block-sorting designs

### 12. [atomicobject/heatshrink](https://github.com/atomicobject/heatshrink)

**Language/role:** C; LZSS compression for embedded and real-time systems.

Study a small codec whose integration model is incremental work under strict memory constraints. It is a useful contrast to compressors that assume large buffers and a general-purpose allocator.

- **C2, C3:** The `sink`/`poll`/`finish` protocol supports small input/output increments, static or dynamic allocation, and explicit window/lookahead configuration. The optional search index trades memory for encoding work. Entry point: [usage and resource model](https://github.com/atomicobject/heatshrink/blob/master/README.md).
- **C1:** Decoder states separately preserve tag bits, partial back-reference indices/counts, and pending output. Allocation validates parameter relationships and the sink reports how much input actually fits. Entry point: [heatshrink_decoder.c](https://github.com/atomicobject/heatshrink/blob/master/heatshrink_decoder.c).

### 13. [Cyan4973/FiniteStateEntropy](https://github.com/Cyan4973/FiniteStateEntropy)

**Language/role:** C; standalone FSE and Huff0 entropy-coding building blocks.

Study the entropy stage independently of an LZ compressor. Although related code is incorporated into Zstandard, this repository exposes a separately reusable codec API and its table-construction machinery.

- **C1:** Symbol counts must be normalized into a power-of-two state-table budget while retaining representable symbols. Table serialization, special distributions, and bounded output introduce precise integer and bitstream invariants. Entry point: [fse_compress.c](https://github.com/Cyan4973/FiniteStateEntropy/blob/dev/lib/fse_compress.c).
- **C2, C3:** The advanced API separates counting, normalization, table construction, serialization, and encoding. Callers can reuse a compression table across blocks, while table-log selection controls CPU/memory costs. Entry point: [fse.h tutorial and API](https://github.com/Cyan4973/FiniteStateEntropy/blob/dev/lib/fse.h).

### 14. [IlyaGrebnov/libbsc](https://github.com/IlyaGrebnov/libbsc)

**Language/role:** C++; reusable block-sorting compressor with optional GPU acceleration.

Study a transform pipeline rather than a conventional LZ-only codec: optional LZP preprocessing, BWT or sort transforms, and selectable QLFC entropy coding.

- **C1, C2:** The library validates transform/coder combinations, supports in-place and separate-buffer operation, handles uncompressible data, and records sizes, mode, transform index, and checksums. Entry point: [libbsc.cpp pipeline](https://github.com/IlyaGrebnov/libbsc/blob/master/libbsc/libbsc/libbsc.cpp).
- **C3:** The project explicitly connects block size and concurrent block count to memory consumption, with separate resource considerations for CUDA transforms. Entry point: [memory and acceleration documentation](https://github.com/IlyaGrebnov/libbsc/blob/master/README).

### 15. [flanglet/kanzi](https://github.com/flanglet/kanzi)

**Language/role:** Java; configurable transform/entropy pipeline and compressed streams.

Study composition across LZ, BWT, and context-modeling approaches, with block parallelism built into the stream implementation. Its format is its own; standard gzip/zstd interoperability is not the purpose. The related C++ and Go implementations are not counted again.

- **C2:** Data transforms and entropy codecs can be combined at runtime through an interface-oriented design. The library is reusable independently of the CLI. Entry point: [design and integration overview](https://github.com/flanglet/kanzi/blob/master/README.md).
- **C1, C3:** `processBlock` apportions jobs, snapshots listeners, creates per-task contexts, validates task results, and preserves interruption state when propagating failure. Block identifiers coordinate concurrent tasks with output. Entry point: [CompressedOutputStream.java](https://github.com/flanglet/kanzi/blob/master/java/src/main/java/io/github/flanglet/kanzi/io/CompressedOutputStream.java).

## Structured data and scientific workloads

### 16. [Blosc/c-blosc2](https://github.com/Blosc/c-blosc2)

**Language/role:** C; compression framework and compressed storage for binary/numerical data.

Study the layers above a byte codec: reversible preprocessing, codec selection, chunks, persistent containers, and multidimensional partitioning. Only lossless codec/filter combinations are in scope; optional lossy codecs or filters do not make every configuration lossless.

- **C2, C3:** The N-dimensional layer uses two levels of partitioning to support selective access to large compressed arrays. The project also documents compatibility with the earlier Blosc API and in-memory format. Entry point: [architecture overview](https://github.com/Blosc/c-blosc2/blob/main/README.rst).
- **C1, C2:** Context APIs, filter pipelines, pre/postfilter callbacks, buffer validation, and lazy-chunk size contracts expose substantial integration and ownership semantics. Global thread configuration has different safety requirements from per-context operation. Entry point: [blosc2.h](https://github.com/Blosc/c-blosc2/blob/main/include/blosc2.h).

### 17. [Deutsches-Klimarechenzentrum/libaec](https://github.com/Deutsches-Klimarechenzentrum/libaec)

**Language/role:** C; adaptive entropy coding for integer samples, with SZIP-compatible support.

Study a CCSDS-oriented codec for low-entropy scientific or instrument data. The project's README lists both this official GitHub location and DKRZ GitLab as source locations.

- **C2, C3:** Sample width, signedness, endianness, block size, preprocessing, and reference-sample interval are explicit parameters. The documentation explains how interval/block choices affect adaptation, buffering, and error propagation. Entry point: [encoding guide](https://github.com/Deutsches-Klimarechenzentrum/libaec/blob/main/README.md).
- **C1:** Decoding must reconstruct signed reference samples, reverse preprocessing, and write samples in the selected representation while advancing partial stream state. Entry point: [src/decode.c](https://github.com/Deutsches-Klimarechenzentrum/libaec/blob/main/src/decode.c).

### 18. [llnl/fpzip](https://github.com/llnl/fpzip)

**Language/role:** C++ with a C API; spatially correlated floating-point arrays.

Study lossless numerical compression where execution semantics can affect reproducibility. Select full precision for this category; reducing retained precision invokes the library's optional lossy behavior.

- **C1:** The API documentation addresses register precision, rounding, compiler optimization, special floating-point values, and alternative arithmetic modes. Encoder and decoder must agree on the representation and coding assumptions. Entry point: [fpzip.h](https://github.com/llnl/fpzip/blob/develop/include/fpzip.h).
- **C2, C3:** The encoder separates spatial prediction, value mapping, probability modeling, and range coding. Multiple fields and file/memory interfaces make those mechanisms reusable for scientific containers. The implementation provides floating-point, emulated, and integer prediction paths. Entry point: [src/write.cpp](https://github.com/llnl/fpzip/blob/develop/src/write.cpp).

### 19. [fast-pack/FastPFOR](https://github.com/fast-pack/FastPFOR)

**Language/role:** C++; integer-array compression research library.

Study block bit packing and exception handling for small integer values, a different workload from arbitrary byte strings. The canonical owner/name was verified; older documentation still contains links using the former owner.

- **C2:** A collection of integer codecs supports comparative use and reuse, including applications that first transform values into deltas. Entry point: [scope, codec choices, and input contract](https://github.com/fast-pack/FastPFOR/blob/master/README.md).
- **C3:** `FastPForImpl` selects a bit width by estimating packed-data and exception costs, groups exception payloads, and processes configurable pages/blocks. Reusable buffers and per-thread instance guidance expose memory and concurrency tradeoffs. Entry point: [headers/fastpfor.h](https://github.com/fast-pack/FastPFOR/blob/master/headers/fastpfor.h).

Its README explicitly assumes decoder input came from a corresponding encoder. This entry does not claim suitability for unchecked adversarial data.

### 20. [cwida/fsst](https://github.com/cwida/fsst)

**Language/role:** C++ with a C API; static-symbol-table compression for strings.

Study compression that preserves individual-string access instead of requiring decompression of a surrounding block. This is particularly relevant to database scans, joins, and storage formats.

- **C2, C3:** A trained symbol table maps short byte sequences to codes, with an escape mechanism for other bytes. Batch APIs accept pointers plus lengths; a decoder table is read-only and shareable, while encoders can be duplicated for threads. Entry point: [fsst.h](https://github.com/cwida/fsst/blob/master/fsst.h).
- **C1, C3:** The representation must preserve escape interpretation, symbol boundaries, and optional zero termination. Equality comparisons can use compressed strings when they share the same encoding table. The project explains why table size and memory pressure change the tradeoffs of its 8-bit and 12-bit variants. Entry point: [format and design overview](https://github.com/cwida/fsst/blob/master/README.md).

## Independent implementations in Go, Rust, JavaScript, Java, and C#

### 21. [klauspost/compress](https://github.com/klauspost/compress)

**Language/role:** Go with optional assembly; multi-codec library, especially `zstd`, `s2`, and `flate`.

Study a substantial native implementation ecosystem rather than foreign-function wrappers. This monorepo counts once; the Zstandard decoder is a particularly useful entry into its concurrency architecture.

- **C1, C2:** A decoder supports one active stream alongside concurrent independent `DecodeAll` calls. A decoder pool, ordered output channel, cancellation, checksums, and wait groups coordinate state reuse and shutdown. Entry point: [zstd/decoder.go](https://github.com/klauspost/compress/blob/master/zstd/decoder.go).
- **C2, C3:** Streaming and whole-buffer APIs reuse allocations. Parallel encoding divides work into jobs, supplies overlap context, and emits results in order; its documentation also spells out dictionary restrictions and output-compatibility expectations. Entry point: [Zstandard package guide](https://github.com/klauspost/compress/blob/master/zstd/README.md).

### 22. [PSeitz/lz4_flex](https://github.com/PSeitz/lz4_flex)

**Language/role:** Rust; independent LZ4 block/frame implementation.

Study safe slice-based decoding alongside performance-oriented alternatives and embedded-oriented feature choices. The project describes itself as a complete rewrite of its original predecessor, rather than a thin binding.

- **C1, C3:** The safe decoder rejects zero match offsets and truncated metadata, and distinguishes fast-loop buffer margins from boundary cases, including external dictionaries. Entry point: [decompress_safe.rs](https://github.com/PSeitz/lz4_flex/blob/main/src/block/decompress_safe.rs).
- **C4:** The [changelog](https://github.com/PSeitz/lz4_flex/blob/main/CHANGELOG.md) documents 2023–2026 compatibility and safety work: removal of an unchecked-decoding feature because of Cargo feature unification, empty-frame compatibility, integer-overflow fixes, backported match-offset fixes, and allocator-free APIs. These are concrete examples of managing optimization complexity over time.

### 23. [Frommi/miniz_oxide](https://github.com/Frommi/miniz_oxide)

**Language/role:** Rust codec implementation; DEFLATE/zlib, with a separate experimental C API shell.

Study an implementation derived from miniz that expresses codec state and buffer access in safe Rust. Focus on the `miniz_oxide/` crate; the repository's C reference/test material is not the selected implementation.

- **C1, C2:** `InflateState` encapsulates dictionary storage, pending output, flush history, and reset policy. `MinReset`, `ZeroReset`, and `FullReset` make the cost and security implications of retained memory explicit. Entry point: [inflate/stream.rs](https://github.com/Frommi/miniz_oxide/blob/master/miniz_oxide/src/inflate/stream.rs).
- **C2, C3:** The core decoder and streaming adapter are separate; the adapter can bypass its wrapping dictionary for a first-call finish into a sufficiently sized buffer. The lower layer exposes incremental progress and decompression flags for higher-level integrations. Entry point: [inflate/core.rs](https://github.com/Frommi/miniz_oxide/blob/master/miniz_oxide/src/inflate/core.rs).

The root documentation calls the C API experimental; this entry does not generalize the Rust crate's integration experience to that shell.

### 24. [101arrowz/fflate](https://github.com/101arrowz/fflate)

**Language/role:** TypeScript/JavaScript; DEFLATE, gzip, zlib, and ZIP facilities.

Study how a browser-compatible codec combines synchronous primitives, incremental streams, and workers. Its code is compact, so following a particular stream class and its worker adapter is more productive than reading the entire source linearly.

- **C2:** The library provides whole-buffer, streaming, asynchronous, and archive APIs built on shared compression primitives. Entry point: [usage guide](https://github.com/101arrowz/fflate/blob/master/README.md).
- **C1, C3:** The async stream adapter transfers buffers, tracks queued bytes, signals draining, terminates workers on completion/error, and handles pushes after finalization. The inflater retains a sliding history and incomplete input across pushes. Entry point: [src/index.ts, especially `astrmify`, `AsyncDeflate`, and `Inflate`](https://github.com/101arrowz/fflate/blob/master/src/index.ts).

### 25. [nodeca/pako](https://github.com/nodeca/pako)

**Language/role:** JavaScript codec core with TypeScript interfaces; zlib port for browsers and Node.js.

Study a substantive language port of zlib's stateful algorithms. Comparing its typed arrays and indices with the C original exposes how low-level semantics survive a different runtime.

- **C1, C3:** The inflater preserves separate header, dictionary, Huffman, match, checksum, and terminal states. Typed-array workspaces replace pointer-based code tables, while a separate fast inflater handles the optimized decoding path. Entry point: [src/zlib/inflate.mjs](https://github.com/nodeca/pako/blob/master/src/zlib/inflate.mjs).
- **C2:** Convenience calls and chunked `Deflate`/`Inflate` objects support different error-handling and streaming styles. The documentation explicitly lists missing zlib APIs and flush-mode limitations instead of promising complete API equivalence. Entry point: [API examples and limitations](https://github.com/nodeca/pako/blob/master/README.md).

### 26. [airlift/aircompressor](https://github.com/airlift/aircompressor)

**Language/role:** Java; independent codec implementations plus optional native backends.

Study how block and framed compression are exposed to both heap arrays and foreign-memory segments. Focus on the Java implementations, especially Zstandard; the presence of native backends does not make this merely a wrapper repository.

- **C2, C3:** Common compressor/decompressor interfaces accommodate `byte[]` and `MemorySegment`, while framing can remain in Java independently of the selected block backend. Entry point: [API and implementation overview](https://github.com/airlift/aircompressor/blob/master/README.md).
- **C1, C3:** The Java frame decoder combines raw memory access with explicit input/output limit checks, block-type dispatch, per-frame state resets, repeated-offset state, and checksum verification. Entry point: [ZstdFrameDecompressor.java](https://github.com/airlift/aircompressor/blob/master/src/main/java/io/airlift/compress/v3/zstd/ZstdFrameDecompressor.java).

### 27. [icsharpcode/SharpZipLib](https://github.com/icsharpcode/SharpZipLib)

**Language/role:** C#; managed compression and archive library.

Study the compression engines and stream adapters within a larger archive library. Its independently implemented DEFLATE and BZip2 functionality makes it relevant beyond archive-container handling.

- **C2:** Namespaces separate checksums, compression engines, compression streams, and archive formats, allowing reuse from .NET languages without requiring one archive abstraction. Entry point: [scope and namespace layout](https://github.com/icsharpcode/SharpZipLib/blob/master/README.md).
- **C1:** `Inflater` distinguishes needing input, needing a dictionary, and completion. Explicit Huffman decoding substates, bit requirements, output-window state, and checksum tracking preserve progress across partial calls. Entry point: [Inflater.cs](https://github.com/icsharpcode/SharpZipLib/blob/master/src/ICSharpCode.SharpZipLib/Zip/Compression/Inflater.cs).

## Search coverage and limitations

Discovery used live web searches with more than six distinct formulations, including general streaming compression; pure Rust and Go implementations; Java/C# codecs; browser compression; embedded LZSS; integer and database-string compression; scientific lossless arrays; CPU/GPU acceleration; and BWT/entropy pipelines. Representative query phrases were `compression library Rust pure Rust lz4 lzma miniz`, `integer string compression library FastPFor FSST`, `scientific lossless compression library libaec fpzip blosc2`, `pure Java C# compression library aircompressor SharpZipLib kanzi`, and `lossless compression library GPU nvcomp CPU ISA-L`. Later searches added ISA-L and libbsc; subsequent broad searches increasingly returned already-covered algorithm families, ports, small demonstrations, and experimental projects without a clear additional selection benefit.

Every retained canonical GitHub repository was opened through its repository page or checked through the GitHub API. Repository introductions and additional implementation/API material were downloaded and read; the links above use verified source paths and branches. API metadata was available for most candidates; after unauthenticated API rate limiting, repository pages supplied the remaining identity checks. Sources were inspected without cloning repositories, installing dependencies, or running their code. No claims of active maintenance are inferred merely from non-archived status, stars, or availability. C4 is used only where multi-year change evidence was actually inspected.

The report deliberately includes independent language implementations and the substantially evolved zlib-ng derivative, but does not multiply counts for bindings, packaging forks, vendored codec copies, or Kanzi's language siblings. Blosc1 is represented by Blosc2 rather than counted separately; [Blosc1's own overview](https://github.com/Blosc/c-blosc) says it is in maintenance mode. [NVIDIA/nvcomp](https://github.com/NVIDIA/nvcomp) was excluded: its current GitHub repository is archived and no longer contains even the examples/benchmarks, directing users elsewhere. GPU coverage here is consequently limited to libbsc's documented acceleration, rather than a survey of GPU codec internals.

This is not exhaustive coverage of media-specific lossless formats, archive managers, academic entropy-coding experiments, or every standard-library implementation. Numerical performance advertisements were not reproduced as comparable measurements. Source review establishes concrete study opportunities, not a security audit: FastPFOR's trusted-input assumption, ISA-L's caller-validation contract, optional lossy configurations, and historical release caveats remain material distinctions.
