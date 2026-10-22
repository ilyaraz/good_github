# Archive readers and writers

Research date: **2026-10-09**.

This selection covers libraries and substantial archive engines that read, write, update, or extract containers of files or records. It includes general-purpose ZIP/TAR/7z implementations, specialized CAB/CHM/MPQ/RAR readers, and WARC web-archive libraries. Read-only and write-only projects qualify; compression codecs without substantial container handling, backup systems, and GUI front ends are outside the scope. The 27 repositories provide contrasting implementations across C, C++, Java, C#, Rust, Go, JavaScript, Python, Swift, Ruby, and PHP.

The criteria below are evidence-based selection judgments, not security certifications or claims that every component is exemplary. Source links generally follow development branches, so inspected behavior may precede a stable release. Repository pages were opened to verify identity and redirects; no blanket claim of active maintenance is made.

## Criteria legend

- **C1 — Correctness:** difficult invariants, concurrency, adversarial inputs, format semantics, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or components supporting different applications.
- **C3 — Performance:** concrete resource constraints addressed through an understandable design.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or complexity management; age alone is insufficient.

## Native archive engines and specialized formats

### 1. [libarchive/libarchive](https://github.com/libarchive/libarchive)

**C; multi-format streaming library and the bsdtar/bsdcpio tools.** Study the library subsystem: archive-entry metadata, format detection, compression filters, and filesystem adapters are separated behind opaque C objects.

- **C2:** The format and filter interfaces compose independently, while entry objects preserve distinctions such as an unknown size versus a known zero size. One API serves many archive formats and caller-supplied I/O.
- **C3:** The internal peek/consume model returns upstream buffers directly when possible and copies when a requested block straddles buffers. Format detection uses the same look-ahead mechanism without consuming input. These are concrete mechanisms for processing large streams with limited copying. [Entry point: internals guide](https://github.com/libarchive/libarchive/wiki/LibarchiveInternals).
- **C4:** The dated history records years of format additions, compatibility fixes, malformed-input performance repairs, and adoption of OSS-Fuzz, rather than merely a sequence of release numbers. [Entry point: NEWS](https://github.com/libarchive/libarchive/blob/master/NEWS).

### 2. [nih-at/libzip](https://github.com/nih-at/libzip)

**C; reading, creating, and modifying ZIP archives.** Particularly useful for studying how an archive editor stages changes and handles failure while preserving existing data.

- **C1:** `zip_close` distinguishes surviving entries, changed metadata, and unchanged data; writes the central directory before committing; and rolls back its writable source on errors or cancellation. This exposes the archive-update transaction boundary without assuming that every storage backend has identical guarantees.
- **C3:** The same path can clone an unchanged prefix when the source supports it, reuse compressed content, and avoid unnecessary recompression. [Entry point: zip_close.c](https://github.com/nih-at/libzip/blob/main/lib/zip_close.c).
- **C4:** The API migration guide spans changes from 2013 through 2026, explains deprecations, and documents subtle compatibility changes such as preserving local and central extra-field ordering separately. [Entry point: API changes](https://github.com/nih-at/libzip/blob/main/API-CHANGES.md).

### 3. [zlib-ng/minizip-ng](https://github.com/zlib-ng/minizip-ng)

**C; ZIP reader/writer with encryption, multiple codecs, and split-volume support.** This is a substantial refactoring and rewrite of the original minizip, with a compatibility layer, rather than an unchanged fork. The repository explains that provenance and distinguishes development, stable, and legacy branches.

- **C2:** A stream virtual table unifies open/read/write/seek, lifecycle, and property operations. A stream can wrap a base stream, allowing the archive implementation to use memory, operating-system I/O, encryption, buffering, and codec layers through a common contract.
- **C3:** Buffered I/O and codec composition address archive throughput without binding the ZIP parser to one platform or compressor. Explicit stream properties carry byte counts, disk sizes, and compression settings. [Entry point: stream interface](https://github.com/zlib-ng/minizip-ng/blob/develop/mz_strm.h).

### 4. [ip7z/7zip](https://github.com/ip7z/7zip)

**C/C++; 7-Zip's archive engine and applications.** The relevant subsystem is `CPP/7zip/Archive`, not just the compression algorithms elsewhere in the repository. Study how many archive handlers fit a common extraction and update protocol.

- **C1:** The interface documentation specifies output-object ownership, sorted extraction indices, missing streams, per-entry error reporting, and concurrency rules. In particular, extraction callbacks are serialized with respect to one another, while progress callbacks may arrive concurrently.
- **C2:** Input/output archive interfaces, volume callbacks, property access, and extraction callbacks separate format handlers from storage and user interfaces. The detailed contract is a useful example of a reusable C++ plugin boundary. [Entry point: IArchive.h](https://github.com/ip7z/7zip/blob/main/CPP/7zip/Archive/IArchive.h).

### 5. [kyz/libmspack](https://github.com/kyz/libmspack)

**C; Microsoft-format decoding library, with cabextract in the same repository.** Focus on CAB and CHM archive reading; the presence of compressor declarations does not imply complete writer implementations for every advertised format.

- **C1:** The API explicitly handles ABI mismatches in file-offset widths, checksum and truncation failures, decoder ownership, and restrictions on concurrently sharing one decoder. CAB salvage mode deliberately changes how invalid offsets, file records, and checksums are treated, making recovery policy visible.
- **C2:** `mspack_system` replaces file I/O and allocation, while format-specific decompressor objects expose method tables over that common host interface. [Entry point: documented public interface](https://github.com/kyz/libmspack/blob/master/libmspack/mspack/mspack.h).

### 6. [ladislav-zezula/StormLib](https://github.com/ladislav-zezula/StormLib)

**C/C++; Blizzard MPQ archive manipulation.** This is the author's official repository. It adds a game-asset archive family with sector-based storage and compatibility peculiarities that ZIP-only libraries do not illustrate.

- **C1:** Sector reading combines offset tables, encryption keys, optional checksums, compressed-versus-stored sector detection, and game-dependent decompression choices. The source records real-world exceptions rather than treating every nominal format flag as sufficient.
- **C3:** Sector offsets and checksums are loaded lazily; a read gathers the required raw sectors and then processes them individually. This makes the mapping between logical reads, compressed storage, and buffering inspectable. [Entry point: SFileReadFile.cpp](https://github.com/ladislav-zezula/StormLib/blob/master/src/SFileReadFile.cpp).

### 7. [selmf/unarr](https://github.com/selmf/unarr)

**C; compact RAR/TAR/ZIP/7z reader descended from a comic-book archive engine.** This independently evolved continuation is retained once; the older `zeniko/unarr` mirror is not counted separately. The project documents important limits: no password-protected, self-extracting, or split archives, no RAR5 support, and a solid-7z performance limitation.

- **C2:** A small archive API supports file, memory, and Windows `IStream` inputs; sequential and offset-based entry selection; incremental decompression; and both normalized and raw names. Its ownership and entry-lifetime rules are explicit. [Entry point: public interface template](https://github.com/selmf/unarr/blob/master/unarr.h.in).
- **C4:** The changelog establishes separate evolution from 2017 onward: codec integration, API additions, unit/integration/fuzz testing, and fixes for RAR filter corruption and malformed-archive memory errors. This supports inclusion of the fork beyond packaging changes alone. [Entry point: changelog](https://github.com/selmf/unarr/blob/master/CHANGELOG.md).

## Java and .NET libraries

### 8. [apache/commons-compress](https://github.com/apache/commons-compress)

**Java; reusable archive and compression APIs.** This is Apache's official GitHub counterpart/mirror of the repository identified in its [GitBox source-management documentation](https://commons.apache.org/proper/commons-compress/scm.html); the GitHub project accepts contributions. Focus on `archivers`, particularly the distinction between ZIP streams and seekable ZIP files.

- **C1:** `ZipArchiveInputStream` documents the consequences of lacking the central directory: entries absent from that directory, duplicate names, incomplete attributes, and deferred sizes/checksums. Its optional support for stored entries with data descriptors also documents an ambiguity involving embedded archives.
- **C2:** Archive streams and entries provide common interfaces across formats, while specialized ZIP configuration exposes capabilities that cannot honestly be hidden by a universal API. This is a strong study in preserving format-specific semantics inside a reusable library. [Entry point: ZipArchiveInputStream](https://github.com/apache/commons-compress/blob/master/src/main/java/org/apache/commons/compress/archivers/zip/ZipArchiveInputStream.java).

### 9. [srikanth-lingala/zip4j](https://github.com/srikanth-lingala/zip4j)

**Java; ZIP file operations and streams, including encrypted and split archives.** Study the archive framing around Java's compression facilities, especially how entry boundaries interact with encryption.

- **C1:** The reader pushes back bytes over-read by the inflater, lets the cipher finish the entry, consumes an extended local header when present, and then verifies integrity. AES version two follows a different verification path from ordinary CRC validation.
- **C2:** The entry stream, cipher stream, and decompressor are separate layers selected from header metadata. Password callbacks and configurable character encoding sit above that stack. These are substantial container abstractions, not merely a one-call wrapper around `java.util.zip`. [Entry point: ZipInputStream](https://github.com/srikanth-lingala/zip4j/blob/master/src/main/java/net/lingala/zip4j/io/inputstream/ZipInputStream.java).

### 10. [adamhathcock/sharpcompress](https://github.com/adamhathcock/sharpcompress)

**C#; multi-format archive reading/writing with seekable and forward-only APIs.** Useful for comparing application-facing convenience APIs with the constraints of non-seekable inputs and solid compression.

- **C2:** Reader, Writer, and Archive APIs share an immutable compression-provider registry. Custom providers receive context such as stream size, seekability, and format-specific properties; providers can also supply codec framing hooks.
- **C3:** The usage guide explains why solid RAR and 7z entries should be extracted sequentially and provides a dedicated iteration path. It also exposes asynchronous extraction, progress, cancellation, and buffer controls. Study these choices together rather than assuming random access has equal cost for every format. [Entry point: usage and provider guide](https://github.com/adamhathcock/sharpcompress/blob/master/docs/USAGE.md).

### 11. [icsharpcode/SharpZipLib](https://github.com/icsharpcode/SharpZipLib)

**C#; ZIP/TAR library with additional compression streams.** Its editable ZIP implementation is a particularly clear comparison with libzip's update design.

- **C1:** `BeginUpdate`, `CommitUpdate`, and `AbortUpdate` expose a staged update lifecycle. The implementation rejects unsupported embedded/SFX updates and distinguishes a temporary-file update mode from a faster direct modification mode with weaker failure protection.
- **C2:** `IArchiveStorage` and `IDynamicDataSource` separate where an update is staged from where new entry data comes from; memory and disk implementations reuse the same update machinery. [Entry point: ZipFile and update interfaces](https://github.com/icsharpcode/SharpZipLib/blob/master/src/ICSharpCode.SharpZipLib/Zip/ZipFile.cs).

## Rust and Go: ownership, I/O models, and virtual filesystems

### 12. [zip-rs/zip2](https://github.com/zip-rs/zip2)

**Rust; the ZIP crate's reader/writer implementation.** Study the current `src/read` subsystem alongside its configurable codecs and writing APIs. The repository explicitly lists unsupported multi-disk archives.

- **C1:** Extraction has distinct symbolic-link policies, validates link destinations, and caps link payload lengths before allocating from attacker-supplied sizes. The code distinguishes recursively contained links from the weaker direct-target-only policy. [Entry point: extraction policy and implementation](https://github.com/zip-rs/zip2/blob/master/src/read/extract.rs).
- **C2:** Stream reading, archive metadata, individual entry readers, and extraction policy are separate modules. The archive-merging implementation also shows checked offset adjustment and reuse of existing file data rather than treating a ZIP as just a list of decompressed byte arrays. [Entry point: read module](https://github.com/zip-rs/zip2/blob/master/src/read/mod.rs).

### 13. [composefs/tar-rs](https://github.com/composefs/tar-rs)

**Rust; streaming TAR reader and builder.** The former `alexcrichton/tar-rs` URL redirects here. Study the interaction between borrowed entry readers, TAR metadata extensions, and filesystem extraction.

- **C1:** `unpack_in` examines path components, skips parent-directory traversal, creates directories carefully, and applies separate handling to hard links and symbolic links. Entry metadata may come from extended records rather than only the fixed header.
- **C2:** Entries implement `Read`, archives consume readers, and builders accept writers; filesystem unpacking is layered on top. The crate documentation states that concurrent mutation of the destination tree is outside its extraction threat model, so these checks should not be described as a race-proof sandbox. [Entry points: entry implementation](https://github.com/composefs/tar-rs/blob/main/src/entry.rs) and [crate documentation](https://docs.rs/tar/).

### 14. [nickbabcock/rawzip](https://github.com/nickbabcock/rawzip)

**Rust; low-level ZIP container reader/writer with caller-selected compression.** A useful contrast to codec-bundling libraries: the container machinery exposes entry locators and integrity information while allowing applications to choose their own processing stack.

- **C2:** Applications can supply compressors and CRC implementations, then pass the resulting integrity information back through explicit descriptors/verifiers. The guide demonstrates how the layers are finalized in the correct order.
- **C3:** The design avoids eagerly materializing the central directory and provides an in-memory zero-copy path. Its parallel-reading guide passes entry locators to workers so decompression can proceed separately from directory traversal. No comparative speed claim is needed to understand these choices. [Entry point: performance and composition guide](https://github.com/nickbabcock/rawzip/blob/master/docs/02-performance.md).

The repository explicitly leaves resource quotas, overlapping-entry policy, safe filesystem operations, duplicate names, and nesting limits to consumers; it is not a complete extraction policy by itself.

### 15. [bearcove/rc-zip](https://github.com/bearcove/rc-zip)

**Rust; ZIP reader with an I/O-independent parsing core.** Despite its broader motivation, the repository explicitly says it currently reads only. Count the core, synchronous adapter, Tokio adapter, and corpus crates as one project.

- **C1:** The archive state machine distinguishes locating the end record, resolving ZIP64 records, and parsing the central directory. The entry state machine's contract includes checking decompressed size and CRC against directory metadata. [Entry point: state-machine module](https://github.com/bearcove/rc-zip/blob/main/rc-zip/src/fsm/mod.rs).
- **C2:** `wants_read`, `space`, `fill`, and `process` let the caller drive a parser under different I/O models. Continuing returns the machine; completion consumes it and returns the archive. I/O errors remain outside parser errors. [Entry point: ArchiveFsm](https://github.com/bearcove/rc-zip/blob/main/rc-zip/src/fsm/archive.rs).

### 16. [mholt/archives](https://github.com/mholt/archives)

**Go; multi-format archive creation/extraction and `io/fs` integration.** It composes other format implementations but adds a substantive virtual-filesystem layer, not just renamed codec calls.

- **C2:** `FileFS`, `DirFS`, and `ArchiveFS` expose compressed files, directories, and archive members through Go filesystem interfaces. Format identification, context, and stream ownership are integrated into that abstraction.
- **C3:** Repeated directory enumeration would repeatedly scan unordered archives. `ArchiveFS` instead builds an index on the first `ReadDir`; the documentation recommends direct entry-order extraction when directory ordering is unnecessary. It also acknowledges that compressed TAR access can remain expensive. [Entry point: fs.go](https://github.com/mholt/archives/blob/main/fs.go).

### 17. [nwaples/rardecode](https://github.com/nwaples/rardecode)

**Go; RAR reader and decompression engine.** A compact place to study solid-archive semantics and post-decompression filters without a broad archiver application's UI code.

- **C1:** Moving to another solid entry drains the current decoder so shared dictionary state remains valid. Filter scheduling checks ordering and limits queued filters, and errors distinguish invalid filters from incompatible decoder transitions.
- **C3:** A sliding window, reusable filter buffers, and `Read`/`WriteTo` interfaces connect the decoder to Go streaming I/O. Buffer reuse and the handling of wrapped dictionary data are visible in one focused component. [Entry point: decode_reader.go](https://github.com/nwaples/rardecode/blob/main/decode_reader.go).

## JavaScript: streaming and resource scheduling

### 18. [gildas-lormeau/zip.js](https://github.com/gildas-lormeau/zip.js)

**JavaScript; ZIP reading/writing for browser and other JavaScript runtimes.** The library handles ZIP64, split files, encryption, and stream-oriented data, with a separate codec execution layer.

- **C2:** Reader/writer adapters and pluggable codecs separate container operations from data sources and compression execution. The pool can select web workers, native compression streams, or inline execution.
- **C3:** Worker acquisition reuses idle workers, caps pool growth, queues excess requests, and retires idle workers. The inspected source also includes a starvation timeout with an inline fallback. This is concrete concurrency/resource scheduling around archive processing. [Entry point: codec-pool.js](https://github.com/gildas-lormeau/zip.js/blob/master/lib/core/codec-pool.js).

### 19. [thejoshwolfe/yauzl](https://github.com/thejoshwolfe/yauzl)

**JavaScript/Node.js; ZIP reader.** Study why a library can stream individual entry contents while still requiring random access to the archive's central directory.

- **C1:** The implementation validates names, bounds integer-sized archive metadata, and uses an asserting transform to detect both excessive and insufficient entry output. Its directory-driven design avoids treating arbitrary local headers as the authoritative file list.
- **C2:** `RandomAccessReader` supports custom byte-range sources with reference-counted stream lifetimes. Lazy entry enumeration lets callers control outstanding work instead of opening every member concurrently. [Entry point: reader, validators, and stream accounting](https://github.com/thejoshwolfe/yauzl/blob/master/index.js).

### 20. [thejoshwolfe/yazl](https://github.com/thejoshwolfe/yazl)

**JavaScript/Node.js; ZIP writer.** It is a separate implementation from yauzl, with a different responsibility and state machine, so both are retained.

- **C1:** The writer counts compressed and uncompressed bytes, checks a promised input size, emits deferred CRC/size data descriptors, and selects ZIP64 records when ordinary fields cannot represent the result.
- **C3:** Input streams are opened lazily and entries are pumped in sequence to avoid exhausting file descriptors. CRC calculation, counting, compression, and output form a streaming pipeline; entry metadata is still retained for the final directory. [Entry point: writer pipeline and entry states](https://github.com/thejoshwolfe/yazl/blob/master/index.js).

### 21. [mafintosh/tar-stream](https://github.com/mafintosh/tar-stream)

**JavaScript/Node.js; TAR parser and generator independent of filesystem extraction.** Particularly useful for understanding backpressure across a stream containing nested entry streams.

- **C1:** The extraction state tracks remaining payload bytes, block padding, GNU long headers, PAX metadata, and entry locks. Finalization rejects incomplete data rather than silently accepting a truncated entry.
- **C3:** The parent parser waits for the current entry's consumption/acknowledgment, propagating backpressure to the archive input. The README explicitly requires draining entries; the implementation shows how child streams unlock the parent. [Entry point: extract.js](https://github.com/mafintosh/tar-stream/blob/master/extract.js).

## Python, Swift, Ruby, and PHP implementations

### 22. [miurahr/py7zr](https://github.com/miurahr/py7zr)

**Python; 7z reading, writing, encryption, and extraction.** Study how 7z's folders and solid streams shape extraction scheduling rather than assuming that each file is independently decompressible.

- **C2:** `SevenZipFile` separates public archive operations from a `Worker` and supports `WriterFactory`/`Py7zIO` extraction destinations. This permits custom sinks without turning every extraction into an in-memory byte dictionary.
- **C3:** A single folder is processed sequentially; multiple folders can be assigned separate workers. The source limits concurrent tasks and disables that path for some input/password conditions, making the connection between format independence, file handles, and parallelism explicit. [Entry point: SevenZipFile and Worker](https://github.com/miurahr/py7zr/blob/master/py7zr/py7zr.py).

The repository documents a migration away from `read`/`readall` and notes that symbolic-link checks are not a guarantee against every hostile case.

### 23. [weichsel/ZIPFoundation](https://github.com/weichsel/ZIPFoundation)

**Swift; ZIP creation, reading, and incremental modification.** Study how an archive library exposes both filesystem conveniences and closure-based chunk processing.

- **C1:** Reading validates buffer sizes, distinguishes files/directories/symlinks, refuses existing output items in the inspected extraction path, and checks whether a symlink target lies within a permitted location. CRC work and cancellation are visible API choices.
- **C2:** Filesystem extraction delegates to the same consumer-closure method used by custom destinations; `Archive` provides entry-oriented access rather than requiring whole-archive extraction.
- **C3:** The extraction API makes read/decompression buffer bounds explicit and delivers chunks to the consumer. This provides a concrete resource model for large entries. [Entry point: Archive+Reading.swift](https://github.com/weichsel/ZIPFoundation/blob/development/Sources/ZIPFoundation/Archive%2BReading.swift).

### 24. [rubyzip/rubyzip](https://github.com/rubyzip/rubyzip)

**Ruby; ZIP reading, writing, and modification.** The high-level archive editor is worth studying alongside its stream-oriented interfaces.

- **C1:** `commit` checks whether changes exist, writes a replacement archive through `OutputStream`, and renames the temporary file only after the write succeeds; cleanup runs even on failure. This is an explicit failure-handling boundary, without implying crash-durability guarantees.
- **C2:** The central-directory model, entries, per-entry output streams, and file/buffer output paths compose into an editable archive abstraction. Duplicate-name behavior is handled explicitly by lookup methods. [Entry point: Zip::File](https://github.com/rubyzip/rubyzip/blob/main/lib/zip/file.rb).

### 25. [maennchen/ZipStream-PHP](https://github.com/maennchen/ZipStream-PHP)

**PHP; ZIP generation directly to output streams.** This is a writer, particularly relevant to web downloads and remote input streams. Its README labels `main` unstable, so the inspected branch should not be confused with a released version.

- **C1:** Per-entry processing tracks CRC and sizes, selects ZIP64 metadata, and rejects mismatches with an explicitly supplied exact size. Deferred headers change the processing strategy: disabling them can require a preliminary pass and rewind.
- **C3:** Chunked input, incremental compression, and callback-based output avoid constructing the entire ZIP on disk before sending it. The pre-read versus deferred-header choice exposes a real streaming/compatibility tradeoff. [Entry point: File.php](https://github.com/maennchen/ZipStream-PHP/blob/main/src/File.php).

## Web-archive record containers

### 26. [webrecorder/warcio](https://github.com/webrecorder/warcio)

**Python; streaming WARC reader/writer and legacy ARC reader.** This expands the category beyond filesystem archives: entries are captured web records with embedded HTTP payloads.

- **C1:** `ArchiveIterator` tracks record boundaries, gzip-member boundaries, offsets, and inter-record blank lines. It detects gzip wrapping that prevents the expected record-level access and accounts differently for compressed and uncompressed record lengths.
- **C2:** A common record model supports WARC versions and ARC conversion; payload access can expose raw bytes or decompress and de-chunk HTTP content. Iteration supports a single pass over local or remote streams. [Entry point: archiveiterator.py](https://github.com/webrecorder/warcio/blob/master/warcio/archiveiterator.py).

### 27. [iipc/jwarc](https://github.com/iipc/jwarc)

**Java; WARC reading/writing with typed records and NIO.** This is a useful companion to warcio because it makes parser grammar and record typing central architectural choices.

- **C1:** A Ragel grammar defines strict and lenient header parsing separately, including folded fields, version syntax, and ARC-to-WARC header conversion. Actions handle real-world malformed dates and emit warnings rather than burying compatibility behavior in a generic line splitter.
- **C2:** The library models standard WARC records as distinct classes with typed accessors and permits extension record types. The parsing layer consumes byte buffers/channels, separating binary I/O from the higher-level record API. [Entry point: WarcParser.rl](https://github.com/iipc/jwarc/blob/master/src/org/netpreserve/jwarc/WarcParser.rl).

## Search coverage and limitations

Discovery used well over six distinct live-web query formulations. Angles included C archive engines and ZIP update libraries; Rust ZIP/TAR crates; Java and .NET format libraries; JavaScript asynchronous ZIP/TAR streams; Go virtual filesystems and RAR readers; Python 7z/WARC implementations; Swift, Ruby, and PHP libraries; CAB/MPQ specialists; and parsers that separate I/O from state transitions. Late searches for archive bindings and streaming designs increasingly returned already-covered implementations, wrappers, mirrors, and overlapping alternatives. The last distinct additions were unarr, jwarc, and rc-zip, which justified extending the selection to 27.

For every retained project, the GitHub repository page was opened and at least one separate primary source was read. Source inspection used selected implementation/API sections, not only search-result snippets or a second copy of the README. The exact file paths cited above were successfully retrieved; the `tar-rs` owner redirect was resolved. libarchive's tools, cabextract/libmspack, and rc-zip's workspace crates are each counted once. Minizip-ng and selmf/unarr are explicitly identified as substantively evolved descendants; duplicate forks are excluded.

The search also surfaced libzippp, language bindings to libarchive/unarr, and GUI archivers such as Ark. These were not added because this report prioritizes archive machinery and substantial independent abstractions over thin wrappers or front ends. Additional MPQ/WARC implementations and newer ZIP libraries were left outside this selection where they added less architectural coverage or were not investigated to the same depth; omission is not a negative quality judgment. General compression libraries, generated wrappers, tutorials, and popularity lists were not used to fill the list.

GitHub's unauthenticated API was rate-limited, so identity checks used repository pages and implementation checks used public source files and project documentation. No candidate code was run, dependencies installed, or performance/security claims independently benchmarked. Development-branch snapshots can differ from releases, and passing a criterion does not establish that all extraction paths are safe against every malicious archive. The descriptions of engineering lessons and criterion fit are grounded interpretations of the linked material.
