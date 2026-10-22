# Binary delta encoding and patching libraries

Research date: **2026-10-09**.

This report selects **19 GitHub repositories** implementing reusable binary differencing, delta serialization, or patch application. Coverage includes local two-input diffing, remote signature-based diffing, archive transformations, embedded patchers, and ROM formats. Byte-exact reconstruction is the common requirement. Text diff viewers, executable-similarity analysis, numeric delta coding, and update managers that merely invoke another library are outside scope.

The criteria identify worthwhile engineering study, not a security certification or a claim that every component is exemplary. Architectural conclusions below are grounded interpretations of the linked code and documentation. Performance mechanisms are described without treating project benchmark results as independently reproduced measurements. Except where explicitly stated, inclusion makes no claim about current maintenance activity.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, malformed inputs, or failure handling. **C2** — substantial reusable abstractions applicable beyond one program. **C3** — concrete performance or memory constraints addressed through understandable architecture. **C4** — sustained evolution supported by compatibility work, tests, or complexity management across years.

## VCDIFF implementations and streaming APIs

### 1. [jmacd/xdelta](https://github.com/jmacd/xdelta)

**Language / role:** C; VCDIFF/RFC 3284 encoder, decoder, library, and command-line tool. The relevant implementation is `xdelta3`; the repository also contains historical `xdelta1` code.

Study how a codec exposes a resumable state machine while leaving source-block retrieval and output consumption to its caller. The repository distinguishes its Apache-licensed line from the separate historical GPL repository; they are not counted twice here.

- **C1:** The input/output protocol distinguishes requests for input, available output, source-block requests, and window boundaries. The caller must consume output and resume in the correct order; closing a stream performs additional error checks.
- **C2 / C3:** Separate stream, source, and configuration structures support both memory convenience functions and incremental processing. Source retrieval can use a synchronous callback or return control for deferred I/O, while window sizing controls buffering. These contracts are explained in the [programming guide](https://jmacd.github.io/xdelta/programming-guide/), the main study entry point.

### 2. [google/open-vcdiff](https://github.com/google/open-vcdiff)

**Language / role:** C++; VCDIFF encoder/decoder library. **Archived on April 18, 2026**, according to the repository banner; retain it as an influential historical implementation.

Study a streaming decoder whose public contract makes dictionary lifetime, partial input, output ownership, and resource limits explicit.

- **C1:** The decoder specifies legal start/chunk/finish sequencing, resets after decoding errors, and exposes maximum target-file and target-window sizes to limit expansion from hostile input.
- **C2 / C3:** It supports pluggable output containers and permits disabling references to earlier target windows, allowing previously decoded data to be discarded. Its output resizing guarantee is stated per window rather than per incoming chunk. These details are in the [decoder interface](https://github.com/google/open-vcdiff/blob/master/src/google/vcdecoder.h), which is considerably more informative than the basic usage example.

### 3. [SnowflakePowered/vcdiff](https://github.com/SnowflakePowered/vcdiff)

**Language / role:** C#; native .NET VCDIFF implementation. This is a declared hard fork of Metric/VCDiff with substantial rewritten code, not a binding to the C++ library.

Study how a managed implementation combines specialized memory access with a reusable decoder API.

- **C2:** The generic decoder accepts separate source and delta buffer types through `IByteBuffer`; a compatibility class adapts ordinary streams and manages their disposal. Maximum output size and checksum behavior are explicit constructor parameters. See [VcDecoderEx.cs](https://github.com/SnowflakePowered/vcdiff/blob/master/src/VCDiff/Decoders/VcDecoderEx.cs).
- **C3:** The documented implementation uses `Span<byte>`, `Memory<byte>`, vector intrinsics, and selected unsafe accesses to address allocation and scanning overhead. The [compatibility and implementation notes](https://github.com/SnowflakePowered/vcdiff/blob/master/README.md) also distinguish interleaving, checksums, and application-header support. Their compatibility table excludes compressed xdelta streams; numerical speed claims are not adopted here.

### 4. [ehrmann/vcdiff-java](https://github.com/ehrmann/vcdiff-java)

**Language / role:** Java; a substantive Java port of open-vcdiff, with separate core and CLI modules. Its README identifies the upstream baseline as open-vcdiff 0.8.4.

Study adaptation of a native codec state machine to Java streams and `ByteBuffer`, including the costs of retaining incomplete input.

- **C1:** The [streaming implementation](https://github.com/ehrmann/vcdiff-java/blob/master/core/src/main/java/com/davidehrmann/vcdiff/engine/VCDiffStreamingDecoderImpl.java) rejects invalid lifecycle calls, preserves unparsed bytes, resets after I/O exceptions, and detects unfinished windows at finalization.
- **C2:** The [decoder builder](https://github.com/ehrmann/vcdiff-java/blob/master/core/src/main/java/com/davidehrmann/vcdiff/VCDiffDecoderBuilder.java) constructs simple, incremental, or `InputStream` APIs and configures target limits and target matching. This is useful for studying multiple interfaces over one decoding engine. The repository documents unsupported xdelta extensions—application headers, its checksum extension, and secondary compression—so interoperability must be checked against the actual producer settings.

### 5. [ably/vcdiff-kotlin](https://github.com/ably/vcdiff-kotlin)

**Language / role:** Kotlin Multiplatform; decoder-only library, with one-shot, reusable, streaming, and structural-inspection interfaces.

Study the protocol machinery in a small native Kotlin implementation, particularly incremental window parsing and address-cache-driven reconstruction.

- **C1:** The [streaming decoder](https://github.com/ably/vcdiff-kotlin/blob/main/src/commonMain/kotlin/com/ably/vcdiff/StreamingDecoder.kt) distinguishes append from finalization, checks integer narrowing and source-copy bounds, implements overlapping target copies byte by byte, and verifies Adler-32 when present. These are concrete correctness concerns, not proof that all malformed inputs are handled safely.
- **C2:** The [API and limitations guide](https://github.com/ably/vcdiff-kotlin/blob/main/README.md) exposes incremental decoding and delta inspection in addition to reconstruction, making the implementation useful for transport clients and diagnostic tooling. Application headers, secondary compression, and custom code tables are explicitly unsupported. It is included for implementation substance; no C4 claim is made for this newer library.

## bsdiff-derived and general-purpose local differencing

### 6. [mendsley/bsdiff](https://github.com/mendsley/bsdiff)

**Language / role:** C; embeddable bsdiff and bspatch libraries derived from Colin Percival’s original work, with a deliberately different stream format.

Study a compact extraction of the binary-diff algorithm from a command-line program into caller-controlled allocation and I/O. The repository explicitly says its patches are incompatible with the original bsdiff utility; the example tool uses `ENDSLEY/BSDIFF43`.

- **C1:** [bspatch.c](https://github.com/mendsley/bsdiff/blob/master/bspatch.c) reconstructs data using signed control triples, bytewise addition, literal data, and source-position adjustments. It contains checks on control lengths, output bounds, and callback failures, making the decoder’s invariants unusually easy to trace.
- **C2:** The [stream API documentation](https://github.com/mendsley/bsdiff/blob/master/README.md) exposes allocation, freeing, writing, and reading through callbacks, removing mandatory filesystem and compression dependencies from the core. The separate implementation and altered format justify treating this as more than a packaging fork.

### 7. [hucsmn/qbsdiff](https://github.com/hucsmn/qbsdiff)

**Language / role:** Rust; BSDIFF40-compatible encoder and patcher, with optional command-line binaries.

Study how to retain a patch-format contract while changing the search strategy and resource controls. Compatibility concerns the format, not byte-identical output to the original encoder.

- **C2 / C3:** [bsdiff.rs](https://github.com/hucsmn/qbsdiff/blob/master/src/bsdiff.rs) exposes search parallelism, chunk sizing, compression level, and working-buffer size. The parallel scheme enforces a minimum chunk size to avoid degrading patch quality; suffix-array indexing has an explicit source-size limit.
- **C3:** [bspatch.rs](https://github.com/hucsmn/qbsdiff/blob/master/src/bspatch.rs) separates copy buffering from a bounded delta cache and writes through `Write`. Its API commentary explains why the source is a byte slice rather than a generic seek/read object: repeated random I/O can dominate patching. Both files prohibit unsafe Rust, but that alone is not treated as a correctness guarantee.

### 8. [divvun/bidiff](https://github.com/divvun/bidiff)

**Language / role:** Rust; binary diff and patch library with a separate CLI. The inspected main branch uses a hash-table design rather than the suffix arrays associated with older bidiff versions.

Study an explicit tradeoff between patch compactness, memory pressure, and parallel throughput.

- **C1:** [hashindex.rs](https://github.com/divvun/bidiff/blob/main/src/hashindex.rs) documents ownership and concurrency assumptions around memory maps, aligned integer access, and atomic compare-and-swap insertion. Its common-prefix comparison also handles machine endianness explicitly.
- **C3:** The [architecture overview](https://github.com/divvun/bidiff/blob/main/README.md) describes file-backed versus anonymous mappings, parallel scanning through ring-buffer channels, and independent zstd-compressed patch chunks for parallel application. These mechanisms distinguish it from a straightforward bsdiff translation. Published benchmark comparisons are workload-specific and have not been reproduced for this report.

### 9. [sisong/HDiffPatch](https://github.com/sisong/HDiffPatch)

**Language / role:** C/C++; binary file and directory differencing libraries with command-line tools. Relevant subsystems include `libHDiffPatch/HDiff` and `libHDiffPatch/HPatch`.

Study a larger codec family that accommodates streaming, compression plugins, caller-controlled caching, and interoperability formats.

- **C2 / C3:** The [patch API](https://github.com/sisong/HDiffPatch/blob/master/libHDiffPatch/HPatch/patch.h) distinguishes sequential output from random-access source and patch inputs, accepts decompressor plugins, and documents caller-provided caches. The header states that the patch functions themselves do not allocate memory; decompressor requirements remain a separate concern.
- **C4:** The [changelog](https://github.com/sisong/HDiffPatch/blob/master/CHANGELOG.md) records years of concrete evolution: cache and plugin work in 2017, large-file/32-bit fixes in 2019, CI and streaming changes in 2021, format compatibility work, and later concurrency and directory-patching fixes. Compatibility-breaking additions are identified explicitly.

HPatchLite belongs to the same implementation family and is not counted as a second independent library here.

## Embedded and constrained patch application

### 10. [eerimoq/detools](https://github.com/eerimoq/detools)

**Language / role:** Python and C; patch generation and application, including sequential and in-place workflows. It builds on bsdiff and HDiffPatch but adds its own patch processing and embedded APIs.

Study the boundary between a flexible host-side generator and a small incremental device-side decoder. Algorithm, patch type, and compression choice are separate decisions; support differs between the Python and C surfaces.

- **C1:** [detools.c](https://github.com/eerimoq/detools/blob/master/c/detools.c) implements explicit chunk and integer-decoding states, overflow rejection, decompressor dispatch, and incomplete-data handling. This makes streaming across arbitrary transport boundaries a first-class concern.
- **C2 / C3:** [detools.h](https://github.com/eerimoq/detools/blob/master/c/detools.h) defines read/write/seek callbacks, incremental-operation state, detailed error codes, and compile-time feature switches for file I/O and compression support. These are meaningful adaptation points for constrained firmware, beyond simply wrapping an external diff command.

### 11. [janjongboom/janpatch](https://github.com/janjongboom/janpatch)

**Language / role:** C; single-header JojoDiff patch applier, independently implemented rather than copied from JojoDiff’s `jptch`.

Study an embedded patcher in which storage behavior is explicit and inspectable. It applies patches; generation requires a compatible external encoder.

- **C2:** The [library guide](https://github.com/janjongboom/janpatch/blob/master/README.md) defines an application-supplied stream type and basic I/O callbacks, so the same parser can operate on POSIX files or embedded storage. It also documents integration tests against multiple JojoDiff versions.
- **C3:** [janpatch.h](https://github.com/janjongboom/janpatch/blob/master/janpatch.h) maintains separate source, patch, and output page buffers, translating byte-oriented patch operations into buffered storage access. Its page-boundary flushing and configurable buffer sizes are useful to study for flash-backed systems. The file also handles the changed default operation introduced by JojoDiff 0.8.5; this is interoperability evidence, without claiming a full adversarial-input audit.

## Signature-based remote deltas and build patching

### 12. [librsync/librsync](https://github.com/librsync/librsync)

**Language / role:** C; reusable signature/delta/patch engine and the `rdiff` utility. It does not implement rsync’s network protocol or filesystem metadata handling.

Study how to compute deltas when the encoder has only a signature of the old file, rather than its complete contents.

- **C2 / C3:** The [library architecture guide](https://librsync.github.io/page_librsync.html) separates signature creation, signature loading, delta generation, and patch application. Whole-file and incremental interfaces allow integration with different I/O systems. It also states that a job needs single-thread ownership or external synchronization.
- **C1 / C4:** [NEWS.md](https://github.com/librsync/librsync/blob/master/NEWS.md) records multi-year fixes and verification work, including invalid literal lengths, zero-length copies that could hang, small-signature heap corruption, platform testing, and avoiding unnecessary input-buffer copies. These changes connect protocol invariants to actual failure modes and maintenance practices.

### 13. [balena-os/librsync-go](https://github.com/balena-os/librsync-go)

**Language / role:** Go; a native reimplementation of librsync/rdiff, not a cgo wrapper.

Study how rolling checksums, signature lookup, strong-hash confirmation, and delta operations fit Go’s reader/writer interfaces.

- **C2 / C3:** [delta.go](https://github.com/balena-os/librsync-go/blob/master/delta.go) accepts `io.Reader`/`io.Writer`, uses a circular matching buffer, and confirms weak matches with strong checksums before emitting copies. `DeltaBuff` permits reuse of the literal buffer across many files and checks its size/capacity contract.
- **C1 / C4:** The [changelog](https://github.com/balena-os/librsync-go/blob/master/CHANGELOG.md) documents work from 2021 through 2025: signed rolling-checksum arithmetic, files shorter than a signature block, partial-block checksums, signature reads, tests, benchmarks, and larger buffered reads. This provides stronger evolution evidence than repository age or a recent push timestamp.

### 14. [OctopusDeploy/Octodiff](https://github.com/OctopusDeploy/Octodiff)

**Language / role:** C#; remote delta compression library and CLI based on the rsync algorithm.

Study a .NET design with explicit signature readers, delta writers, rolling-checksum algorithms, and progress reporting.

- **C2:** [DeltaBuilder.cs](https://github.com/OctopusDeploy/Octodiff/blob/master/source/Octodiff/Core/DeltaBuilder.cs) takes `ISignatureReader` and `IDeltaWriter`, separating match discovery from representation. Signature metadata selects the hashing algorithms, while copy and literal commands form the output abstraction.
- **C1 / C3:** The same implementation sorts signatures by weak checksum, checks strong hashes for candidates, and overlaps successive read buffers so a matching block can straddle a buffer boundary. The [format and resource notes](https://github.com/OctopusDeploy/Octodiff/blob/master/README.md) explain the signature-memory tradeoff and binary instruction representation. This is signature-based reconstruction, not compatibility with VCDIFF or BSDIFF40.

### 15. [itchio/wharf](https://github.com/itchio/wharf)

**Language / role:** Go; reference implementation of a build-transfer protocol. Relevant reusable subsystems include `wsync`, `pwr`, and the repository’s bsdiff implementation; the repository is counted once.

Study how binary deltas extend from one file to a container of files while retaining cross-file reuse and filesystem structure.

- **C1 / C3:** The [diff specification](https://itch.io/docs/wharf/algorithms/diff.html) explains weak/strong matching, short final blocks, consecutive-copy coalescing, and a preferred-file rule for identical content. That rule makes an unchanged container produce recognizable no-op ranges rather than arbitrary cross-file references.
- **C2:** [pwr/diff.go](https://github.com/itchio/wharf/blob/master/pwr/diff.go) separates container metadata, content pools, block signatures, compression settings, and patch/signature writers. It demonstrates a useful layer above a raw codec for distributing multi-file builds. The linked specification is the project’s official protocol documentation, rather than a third-party account.

## Archive-aware, operation-pipeline, and browser implementations

### 16. [google/archive-patcher](https://github.com/google/archive-patcher)

**Language / role:** Java; ZIP/JAR/APK-aware delta generation and application. **Archived on June 24, 2024**; this is a historical architecture reference.

Study why ordinary binary diffing is insufficient when small logical edits disturb compressed bytes, and how to transform archives without losing exact reconstruction.

- **C1:** The [format and design documentation](https://github.com/google/archive-patcher/blob/master/README.md) explains selectively inflating changed entries, differencing the transformed data, and recompressing to reproduce the original target archive byte for byte. Deflate compatibility windows are part of that correctness contract. ZIP64 is explicitly unsupported.
- **C2 / C3:** [PreDiffExecutor.java](https://github.com/google/archive-patcher/blob/master/generator/src/main/java/com/google/archivepatcher/generator/PreDiffExecutor.java) separates read-only planning from producing intermediate files and records a recompression plan. Recommendation modifiers provide a policy boundary for controlling preprocessing choices instead of hardwiring every decision into the delta algorithm.

### 17. [org-badiff/badiff](https://github.com/org-badiff/badiff)

**Language / role:** Java; byte-level diffs represented as reusable operation sequences, supporting files and byte arrays. **Official project-declared GitHub mirror:** its README identifies a separate definitive repository on `stash.robindps.com`. Treat this as a historical source reference, not a claim that the external service or project remains maintained.

Study a different architecture from suffix-array or rolling-hash codecs: chunked edit-graph work followed by operation transformations.

- **C2:** [Diff.java](https://github.com/org-badiff/badiff/blob/stable/badiff/src/main/java/org/badiff/Diff.java) composes application, storage, and queue interfaces. This supports multiple representations of a diff and reusable transformations over an operation stream.
- **C1 / C3:** [ParallelGraphOpQueue.java](https://github.com/org-badiff/badiff/blob/stable/badiff/src/main/java/org/badiff/q/ParallelGraphOpQueue.java) dispatches edit-graph work through futures while retaining an ordered queue, bounds active work by worker count, and reuses thread-local graph allocations. It is a concrete study of parallel computation inside an otherwise lazy pipeline.

### 18. [dchest/fossil-delta-js](https://github.com/dchest/fossil-delta-js)

**Language / role:** TypeScript/JavaScript; native implementation of Fossil’s binary delta algorithm and format, usable independently of the Fossil SCM.

Study a compact alternative to VCDIFF with copy, insert, and checksum records, and pay attention to JavaScript’s fixed-width bitwise arithmetic.

- **C1:** [fossil-delta.ts](https://github.com/dchest/fossil-delta-js/blob/master/fossil-delta.ts) implements explicitly masked rolling-hash arithmetic and decoder checks for copy bounds, advertised output size, final checksum, and termination. The distinction between byte counts and string character counts is visible in its string helpers.
- **C2:** The [API and migration guide](https://github.com/dchest/fossil-delta-js/blob/master/README.md) supports both byte arrays and `Uint8Array`, optional checksum verification, output-size inspection, and UTF-8 string adapters. It documents changed API names and output types when moving to ES modules. This is an actual codec implementation, not a wrapper around Fossil’s executable.

### 19. [marcrobledo/RomPatcher.js](https://github.com/marcrobledo/RomPatcher.js)

**Language / role:** JavaScript; reusable binary patching core and format modules, accompanied by a browser application and Node CLI. The core under `rom-patcher-js` is the relevant subsystem.

Study interoperability across ROM-patching communities, where headers, source identity, relative copy offsets, and format-specific checksums matter as much as general compression ratio.

- **C1:** The [BPS implementation](https://github.com/marcrobledo/RomPatcher.js/blob/master/rom-patcher-js/modules/RomPatcher.format.bps.js) implements variable-length numbers, separate source/target relative offsets, and copies from progressively reconstructed target data. It verifies the patch checksum during parsing and optionally verifies source and target CRCs during application.
- **C2:** [RomPatcher.js](https://github.com/marcrobledo/RomPatcher.js/blob/master/rom-patcher-js/RomPatcher.js) dispatches to distinct format modules through a common patch-parsing and validation surface, with additional ROM/header knowledge above them. This makes the repository useful beyond its GUI. Format support is not uniform, and CRC validation should not be confused with authentication.

## Coverage and search notes

Discovery used more than six meaningfully distinct live-search formulations: VCDIFF/xdelta implementations; bsdiff and HDiffPatch libraries; Rust suffix-array and hash-index alternatives; embedded and in-place firmware patchers; Go implementations of librsync; .NET remote delta compression; Java archive-aware and byte-array diffing; Fossil deltas in JavaScript; and BPS/UPS/IPS ROM patching. Follow-up searches for ddelta, zdelta, newer Rust chunk codecs, and alternatives increasingly returned overlapping implementations, wrappers, or projects with insufficient additional evidence for this selection.

For every retained repository, its GitHub page or public API was opened to verify the canonical location. Each entry also has an independently read non-README primary source—implementation, API contract, official design documentation, or changelog. GitHub API rate limits affected some metadata requests; direct repository pages and raw source files supplied the missing evidence. No candidate was cloned, built, installed, or executed.

The selection deliberately includes independent language ports and substantial rewrites, but does not count superficial forks or bindings separately. SnowflakePowered/vcdiff and ehrmann/vcdiff-java share open-vcdiff ancestry, which is stated above; balena’s implementation is native Go. HPatchLite is covered through the HDiffPatch family rather than used to inflate the count. Thin Perl/FFI/WASM wrappers, generic update front ends, tutorial patchers, diff viewers, numerical delta encoders, and broad SCM repositories were excluded. Historical zdelta imports were considered but not promoted solely for importing the original code and adding platform wrappers. Additional Rust alternatives were discovered; the chosen Rust entries offer particularly clear and distinct source-level tradeoffs.

This is a selection guide, not an exhaustive compatibility matrix, maintenance audit, or benchmark ranking. Archive status and the badiff mirror relationship are explicit; an unarchived repository is not thereby asserted to be actively maintained. C4 is claimed only where inspected historical change records show substantive evolution. The primary evidence establishes concrete mechanisms and study value, while complete security properties and performance under a reader’s workload remain unverified.
