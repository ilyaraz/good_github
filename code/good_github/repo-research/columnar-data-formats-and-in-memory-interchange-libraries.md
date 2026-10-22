# Columnar data formats and in-memory interchange libraries

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing columnar memory layouts, cross-runtime array interchange, columnar file readers/writers, and reusable columnar compression frameworks. It includes established formats, independent implementations, experimental formats, and explicitly marked historical projects. ROOT is included only for its RNTuple subsystem; Apache Arrow's C++ implementation, PyArrow, and C++ Parquet implementation count together as one repository. Separately maintained Arrow implementations count individually because they implement materially different memory, type, and runtime designs.

The criteria assignments and suggested study topics are engineering judgments grounded in the linked primary material. They do not certify every component's correctness or endorse deployment. Repository identities, default branches, archive flags, and recent push metadata were checked using the public GitHub API; documentation and implementation files were read separately. No candidate code was built or executed, and benchmark claims were not independently reproduced.

**Criteria legend**

- **C1 — Difficult correctness:** invariants, ownership, concurrency, numerical semantics, malformed inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or representations useful across applications.
- **C3 — Performance with structure:** concrete resource constraints addressed through understandable architectural choices.
- **C4 — Sustained evolution:** multiyear development supported by compatibility work, regression handling, testing, or complexity management. Age alone does not qualify.

## Official Arrow implementations and interchange foundations

### 1. [apache/arrow](https://github.com/apache/arrow)

**Language/role:** C++ core with Python, R, and other bindings; columnar memory format, IPC, interchange, and file-format tooling.

Study the boundary between the shared format contract and a large native implementation. The relevant subsystems are C++ buffers, arrays, memory pools, C Data Interface integration, IPC, and Parquet. PyArrow and the C++ Parquet implementation are not additional selections.

- **C1:** The C Data Interface specifies producer-owned storage, recursive release callbacks, moved structures, dictionary children, and when a released structure becomes invalid. These are concrete lifetime obligations across independently managed runtimes. [C Data Interface](https://arrow.apache.org/docs/format/CDataInterface.html).
- **C2 and C3:** `Buffer`, `MemoryPool`, `Device`, and `MemoryManager` separate ownership, allocation, and device accessibility. Buffer slices share storage; aligned allocation and device-aware views avoid unnecessary copies while exposing when a transfer is necessary. [C++ memory architecture](https://github.com/apache/arrow/blob/main/docs/source/cpp/memory.rst).

### 2. [apache/arrow-rs](https://github.com/apache/arrow-rs)

**Language/role:** Rust; native Arrow and Parquet libraries, including array, buffer, schema, IPC, and Flight crates.

Useful for studying how a common binary layout becomes a typed, reference-counted Rust API without erasing the distinction between physical buffers and logical arrays.

- **C1:** `ArrayData::validate` checks buffer counts, alignment, length-plus-offset arithmetic, null-buffer lengths, child data, and type-specific offset constraints. More expensive content checking is separated from basic structural validation. [ArrayData implementation](https://github.com/apache/arrow-rs/blob/main/arrow-data/src/data.rs).
- **C2 and C3:** Typed arrays coexist with `ArrayRef` and record batches. Shared buffers permit inexpensive owned slices, while iterator/stream patterns provide alternatives to a dedicated chunked-array class. This makes allocation ownership and lazy processing visible in the API. [Array architecture and examples](https://docs.rs/arrow-array/latest/arrow_array/).

### 3. [apache/arrow-java](https://github.com/apache/arrow-java)

**Language/role:** Java; independent Arrow implementation with off-heap vectors, IPC, and native interoperability.

The central study topic is deliberate memory accounting outside the JVM heap. This is an independent implementation, not a binding around Arrow C++.

- **C1:** Reference-counted `ArrowBuf` storage has explicit close/release obligations. A tree of allocators propagates child allocations into parent accounting, checks limits, and detects outstanding allocations when an allocator closes.
- **C2 and C3:** The memory interfaces are separated from Netty and Unsafe implementations. Direct buffers support I/O and JNI sharing without intermediate copies, while child allocators let applications assign resource budgets to subsystems.

Both criteria are developed concretely in the [memory-management design](https://arrow.apache.org/java/main/memory.html), the principal entry point for this repository.

### 4. [apache/arrow-go](https://github.com/apache/arrow-go)

**Language/role:** Go; native Arrow arrays, IPC, C interchange, and Parquet support.

Study explicit buffer lifetime management inside a garbage-collected language, especially when arrays cross goroutine channels or native boundaries.

- **C1:** The project documents ownership transfer through `Retain`/`Release`, including the extra retain required before sending an object through a channel. The buffer implementation uses atomic reference counts and keeps sliced parents alive until their children release them. [Ownership rules](https://github.com/apache/arrow-go#reference-counting); [buffer implementation](https://github.com/apache/arrow-go/blob/main/arrow/memory/buffer.go).
- **C2 and C3:** Allocator-backed buffers can wrap imported C Data Interface storage, distinguish mutable/resizable storage, and round capacity growth to allocation boundaries. The same abstraction supports foreign-memory cleanup and reusable Go-side buffers. The buffer implementation above makes those tradeoffs inspectable.

### 5. [apache/arrow-js](https://github.com/apache/arrow-js)

**Language/role:** TypeScript/JavaScript; official Arrow vectors, tables, builders, and IPC support for browsers and Node.js.

Useful for studying how Arrow's physical representation maps onto JavaScript typed arrays while retaining nested and dictionary-encoded values.

- **C1:** `Data` tracks logical offsets, child arrays, type IDs, validity bitmaps, dictionary vectors, and variadic buffers. Union validity must be obtained from the correct child and, for dense unions, the correct child offset; null counts also depend on sliced bitmap ranges. [Data implementation](https://github.com/apache/arrow-js/blob/main/src/data.ts).
- **C2 and C3:** Tables and vectors expose ordinary JavaScript access patterns while `makeVector` can wrap typed arrays without copying. Builders and IPC conversion serve both locally constructed columns and externally produced record batches. [Usage and typed-array examples](https://github.com/apache/arrow-js#cookbook).

### 6. [apache/arrow-julia](https://github.com/apache/arrow-julia)

**Language/role:** Julia; native Arrow arrays and IPC integrated with Julia's table and array protocols.

Study a language-native interpretation of a foreign memory format: Arrow vectors behave as Julia abstract arrays, and tables participate in the Tables.jl ecosystem.

- **C2:** The implementation exposes primitive, list, struct, union, map, and dictionary representations through familiar Julia interfaces. This supports consumers beyond a single dataframe package.
- **C3:** The manual explains mapping a file, inspecting its metadata, and wrapping eligible underlying bytes as array views. It separately describes record-batch streaming, compression, and concurrent batch writing with a configurable task count. These expose the tradeoff between materialization, working memory, and parallelism.

Entry point: [manual, including reading and multithreaded writing](https://github.com/apache/arrow-julia/blob/main/docs/src/manual.md). The [repository's support list](https://github.com/apache/arrow-julia#format-support) explicitly excludes Flight, tensors, and the C Data Interface; do not assume parity with every Arrow implementation.

### 7. [apache/arrow-dotnet](https://github.com/apache/arrow-dotnet)

**Language/role:** C#; official managed Arrow arrays and asynchronous IPC implementation.

Study how native allocation lifetimes are carried through .NET memory abstractions and shared arrays.

- **C1:** `SharedMemoryOwner` uses volatile reads and compare-and-exchange when retaining memory, rejects retention after disposal, and disposes the underlying owner when the reference count reaches zero. [Shared memory ownership](https://github.com/apache/arrow-dotnet/blob/main/src/Apache.Arrow/Memory/SharedMemoryOwner.cs).
- **C2 and C3:** The implementation uses `Span<T>`, `Memory<T>`, memory managers, aligned allocation, and array visitors to support serialization and traversal. [Implementation overview](https://github.com/apache/arrow-dotnet#implementation).

The same overview documents limitations, including incomplete deserialization validation and restrictions on large arrays. Those limits matter when studying trusted versus untrusted interchange. The repository also contains dedicated [array reference-counting tests](https://github.com/apache/arrow-dotnet/blob/main/test/Apache.Arrow.Tests/ArrayDataReferenceCountingTests.cs).

### 8. [apache/arrow-nanoarrow](https://github.com/apache/arrow-nanoarrow)

**Language/role:** C, with C++ helpers and Python/R bindings; small libraries for producing and consuming Arrow C Data, C Stream, C Device, and IPC representations.

This is a particularly useful integration-layer study: applications can participate in Arrow interchange without adopting the full C++ stack.

- **C1:** Array-view validation distinguishes checking buffer sizes and endpoint offsets from deeper content validation. The API also distinguishes allocation of structure members from allocation of data buffers, and documents thread-safety boundaries. [C API declarations and contracts](https://github.com/apache/arrow-nanoarrow/blob/main/src/nanoarrow/nanoarrow.h).
- **C2 and C3:** Schema views, array views, builders, custom buffer deallocators, and shared buffers are reusable building blocks. Custom cleanup can attach an existing runtime's allocation without copying its bytes; the core can be bundled as a small C dependency. [Project scope and bundling model](https://github.com/apache/arrow-nanoarrow#nanoarrow).

## Independent array designs and specialized interchange

### 9. [man-group/sparrow](https://github.com/man-group/sparrow)

**Language/role:** C++20; an independent implementation of Arrow columnar layouts with idiomatic C++ containers and C-interface conversion.

Study the interaction of value semantics, nullable reference proxies, type erasure, and foreign ownership.

- **C1:** Imported arrays may borrow C structures or take ownership; extraction transfers the release obligation to the caller. Copying an array deliberately performs a deep copy even when the source is a view, simplifying nested ownership semantics. [Dynamic arrays and ownership](https://github.com/man-group/sparrow/blob/main/docs/source/array.md).
- **C2 and C3:** Typed arrays share a container-like API and expose nullable proxies. Dynamically typed arrays use visitation into typed arrays instead of providing dynamic iterators, an explicit performance-driven API choice. [Typed-array design](https://github.com/man-group/sparrow/blob/main/docs/source/typed_array.md); dynamic-array design above.

### 10. [uwdata/flechette](https://github.com/uwdata/flechette)

**Language/role:** JavaScript; independent Arrow IPC reader/writer and column extraction library from the UW Interactive Data Lab community.

Useful for studying the last conversion step between binary columns and the values expected by visualization and analysis libraries.

- **C1:** Conversion choices distinguish `bigint` from JavaScript numbers and timestamps from `Date` objects. The batch implementation separately handles validity, float16 special values, and padded buffers whose physical length exceeds logical length. [Batch implementations](https://github.com/uwdata/flechette/blob/main/src/batch.js).
- **C2 and C3:** Direct batches return typed-array subviews when null handling permits it; other batches perform value conversion. Tables can expose column arrays or zero-copy row proxies, with documented restrictions on property enumeration and object spreading. [Table API and proxy tradeoffs](https://github.com/uwdata/flechette/blob/main/docs/api/table.md).

The README explicitly notes simpler byte-buffer inputs and upfront dictionary decoding; its speed comparisons are not treated here as independently verified results.

### 11. [geoarrow/geoarrow-c](https://github.com/geoarrow/geoarrow-c)

**Language/role:** C/C++; experimental geospatial type system and conversion library using Arrow extension arrays.

Study the adaptation of irregular geometry into reusable columnar representations, including WKB, WKT, and GeoArrow encodings with Z and M dimensions.

- **C1:** The WKB reader checks remaining bytes before reading scalar fields and coordinate sequences, handles endianness and ISO/EWKB dimension flags, and limits nested geometry depth. [WKB reader](https://github.com/geoarrow/geoarrow-c/blob/main/src/geoarrow/wkb_reader.c).
- **C2:** Builders and readers share an ArrowArray boundary and expose geometry visitation rather than requiring callers to implement every format pair. Existing buffers can be wrapped by the C++ builder and exported through the common interchange representation. [Builder/reader example and supported representations](https://github.com/geoarrow/geoarrow-c#geoarrow-c).

The repository identifies itself as experimental; broad conversion coverage is not a claim of a stable long-term API.

### 12. [jorgecarleitao/arrow2](https://github.com/jorgecarleitao/arrow2)

**Language/role:** Rust; independent Arrow implementation. **Historical: archived and explicitly unmaintained since January 2024.**

Retained for its documented alternative design, not as a current maintenance recommendation. It is not merely a snapshot of the official Rust implementation.

- **C1:** Array design requires checked constructors to reject invalid Arrow layouts, including UTF-8 invariants, and isolates optional unchecked constructors for expensive validation paths. Slicing is the designated way to change logical offsets. [Array design](https://github.com/jorgecarleitao/arrow2/blob/main/src/array/README.md).
- **C2 and C3:** Mutable-to-immutable array conversion is designed to avoid allocation and element transformation. The I/O architecture exposes separate metadata, byte-reading, and CPU-bound decoding stages so applications can independently schedule I/O and computation. [I/O design](https://github.com/jorgecarleitao/arrow2/blob/main/src/io/README.md).

Its README also records possible panics on untrusted Parquet/Avro input; the historical status and caveat should accompany any reuse.

## Established persistent formats and independent readers/writers

### 13. [apache/parquet-java](https://github.com/apache/parquet-java)

**Language/role:** Java; Apache Parquet implementation, formerly named Parquet MR.

Study nested record shredding and reconstruction, with schema conversion separated from encoded column storage. This is the implementation repository; the separate Parquet specification repository is not counted again.

- **C1:** Record assembly uses states indexed by repetition and definition levels, including paths of group converters and transitions that open and close nested groups. The reader must reconstruct missing, repeated, and defined values from independently stored columns. [Record-reader state machine](https://github.com/apache/parquet-java/blob/master/parquet-column/src/main/java/org/apache/parquet/io/RecordReaderImplementation.java).
- **C2:** `ReadSupport`, `WriteSupport`, record materializers, and record consumers permit different object models to share the same columnar engine. Avro, Thrift, and Protobuf integrations demonstrate this separation. [Conversion APIs and integrations](https://github.com/apache/parquet-java#mapreduce-integration).

### 14. [apache/orc](https://github.com/apache/orc)

**Language/role:** Java and C++; independent implementations of the ORC columnar file format, in one repository.

Study type-aware encoding, stripe/row indexes, vectorized reading, and how selective reads interact with remote-storage costs.

- **C2:** The reader separates filter columns from projected columns and converts pushed-down search arguments into vector filters. This allows the format library to serve multiple query engines without embedding their execution model. [Lazy-filter design](https://github.com/apache/orc/blob/main/site/develop/design/lazy_filter.md).
- **C3:** The I/O design studies coalescing nearby reads through `DataReader`, balancing extra bytes against request/seek costs and discarding excess bytes when memory tolerance requires it. The lazy-filter design separately defers non-filter columns until a batch has matches. [I/O design and measured workload setup](https://github.com/apache/orc/blob/main/site/develop/design/io.md).

The documented optimizations have explicit scope limits, including reads across stripe boundaries; their workload-specific benchmark numbers are not generalized here.

### 15. [parquet-go/parquet-go](https://github.com/parquet-go/parquet-go)

**Language/role:** Go; independent Parquet reader/writer originally developed at Twilio Segment.

An approachable study of reusable row-group composition and the interaction between generic typed APIs and column-oriented bulk operations.

- **C1:** Merging row groups requires compatible schemas and sorting definitions; conversions and sort-prefix rules constrain which merges preserve the promised ordering. [Merge contracts](https://github.com/parquet-go/parquet-go#merging-row-groups-parquetmergerowgroups).
- **C2 and C3:** `RowGroup`, column chunks, and row readers support files, buffers, and composed views. Optional writer-to interfaces let copying bypass a generic row-by-row path. The README also explains why bloom-filter construction increases buffering requirements. [Row-group interfaces](https://github.com/parquet-go/parquet-go/blob/main/row_group.go).

The package explicitly retains pre-v1 API compatibility flexibility; API stability should not be inferred from compatibility with the Parquet file format.

### 16. [aloneguid/parquet-dotnet](https://github.com/aloneguid/parquet-dotnet)

**Language/role:** C#; a managed Parquet implementation with low-level column APIs and typed/untyped object serialization.

Study compiled reconstruction of nested objects rather than a thin native-library binding.

- **C1:** The Dremel assembler tracks separate value, definition-level, and repetition-level positions, plus a repetition state machine for nested collections. A value is consumed only when its definition level makes it present. [Field assembler compiler](https://github.com/aloneguid/parquet-dotnet/blob/master/src/Parquet/Serialization/Dremel/FieldAssemblerCompiler.cs).
- **C2 and C3:** Expression trees compile schema-specific reconstruction over spans and raw column data, serving both ordinary classes and dictionary-shaped untyped objects. This separates general schema handling from the repeated per-record operation.

The [release notes](https://github.com/aloneguid/parquet-dotnet/blob/master/docs/release-notes.md) provide useful accompanying cases: temporal precision/mapping changes, dictionary-page counting, lost interleaved nulls, and page-position fixes. These are concrete compatibility and correctness lessons, not evidence that all edge cases are solved.

### 17. [dask/fastparquet](https://github.com/dask/fastparquet)

**Language/role:** Python/Cython; Parquet implementation integrated with pandas, NumPy, and filesystem abstractions. **Historical/retiring: the README announces retirement in March 2026.**

This repository is marked as a fork of `parquet-python`, but has substantive independent evolution: its README documents the 2016 fork for vectorized loading and parallel access. The ancestor is not counted separately.

- **C1:** Its usage notes explicitly discuss NULL versus NaN/NaT, dictionary-label consistency across partitions, timezone metadata, and decimal-to-float precision loss. These are unusually clear examples of semantic mismatches between a file format and a dataframe runtime. [Representation and compatibility notes](https://github.com/dask/fastparquet/blob/main/docs/source/details.rst).
- **C4:** Dated release notes cover 2021–2023 evolution: two-pass row filtering, dtype round trips, pandas compatibility, overflow fixes, and a regression caught by Dask tests. [Release history](https://github.com/dask/fastparquet/blob/main/docs/source/releasenotes.rst).

Recent repository pushes do not override the explicit retirement notice or establish support for pandas 3.

### 18. [hyparam/hyparquet](https://github.com/hyparam/hyparquet)

**Language/role:** JavaScript; Parquet reader designed for browsers, Node.js, and HTTP range access.

Study a compact implementation where nested decoding and network-read planning are directly visible. Its companion writer is a different repository and is not counted here.

- **C1:** The Dremel assembler maintains a container stack, tracks definition/repetition depths, continues rows across input boundaries, and distinguishes values, nulls, and empty lists. [Nested assembly](https://github.com/hyparam/hyparquet/blob/master/src/assemble.js).
- **C2 and C3:** An asynchronous byte-buffer abstraction decouples storage from parsing. Read plans select row groups and physical columns, incorporate indexes/filters, and coalesce nearby ranges to reduce network requests. [Read planner](https://github.com/hyparam/hyparquet/blob/master/src/plan.js).

This is a useful contrast to native readers: transfer volume, asynchronous fetching, and JavaScript value reconstruction are central constraints.

## Newer layouts and composable compression formats

### 19. [vortex-data/vortex](https://github.com/vortex-data/vortex)

**Language/role:** Rust with language bindings and query-engine integrations; extensible compressed arrays and a persistent columnar format. This is the current repository, formerly under SpiralDB.

Study a design in which physical encodings remain composable rather than becoming a single fixed array layout.

- **C2:** Array encodings have vtables, children, buffers, statistics, and a logical type. Canonical encodings provide a common target so every operation need not support every pair of compression representations. [Array architecture](https://github.com/vortex-data/vortex/blob/develop/docs/concepts/arrays.md).
- **C3:** Out-of-memory layouts form trees backed by lazily fetched segments. Layout strategies choose partitioning, statistics, and compression; sequence IDs preserve output placement while write/compression work runs in parallel. [Layout architecture](https://github.com/vortex-data/vortex/blob/develop/docs/concepts/layouts.md).

The README promises backward file compatibility from version 0.36.0 while allowing library APIs to change. That is a format-specific contract, not a blanket maturity claim.

### 20. [lance-format/lance](https://github.com/lance-format/lance)

**Language/role:** Rust with Python and other bindings; columnar file/container and higher-level table machinery for multimodal and selective-access workloads.

The relevant subsystem here is the file and encoding layer, rather than the entire search/index stack.

- **C1:** Structural encodings must preserve list/struct validity and repetition information while allowing partial reads. The documented definition-level convention differs from Parquet's, illustrating why superficially similar encodings cannot simply be interchanged. [Encoding strategy](https://github.com/lance-format/lance/blob/main/docs/src/format/file/encoding.md).
- **C2 and C3:** Independently paginated columns remove a shared row-group boundary. Column descriptors locate pages, external/global buffers hold auxiliary data, and structural encodings separate I/O scheduling from compression algorithms. [File-container design](https://github.com/lance-format/lance/blob/main/docs/src/format/file/index.md).

The project distinguishes stable storage-version compatibility from SDK/API compatibility and experimental storage versions; the study focus is selective I/O and the resulting format contracts.

### 21. [facebookincubator/nimble](https://github.com/facebookincubator/nimble)

**Language/role:** C++; columnar file format aimed particularly at wide datasets, with extensible block encodings. **Experimental:** the README explicitly disclaims stability/versioning guarantees.

Study the encoding tree and the policy that chooses it, particularly for sparse, wide feature data.

- **C2:** Encodings recursively contain encoded substreams, while `EncodingSelectionPolicy` separates selection from encoding. Manual cost estimates, learned selection, and replayed layouts are distinct policies; replay also supports deterministic reproduction. [Encoding architecture](https://github.com/facebookincubator/nimble/blob/main/dwio/nimble/docs/Encodings.md).
- **C1 and C3:** Selection excludes a parent's encoding from nested candidates to avoid recursive self-selection. Nullable encoding separates the validity stream from compact non-null values, allowing sparse-boolean encoding of highly skewed validity data. Cost selection weights estimated size by decoding cost. [Nullable representation](https://github.com/facebookincubator/nimble/blob/main/dwio/nimble/docs/develop/nullable_encoding.rst); encoding architecture above.

### 22. [maxi-k/btrblocks](https://github.com/maxi-k/btrblocks)

**Language/role:** C++; research implementation accompanying the SIGMOD 2023 BtrBlocks columnar-compression work.

A focused study of compression selection and cascading, with integer, double, and string scheme families. Treat this as a research codebase: its README describes the tests as rudimentary, and the API snapshot showed the last push in April 2025.

- **C2:** Scheme interfaces separate compression, decompression, applicability, and estimated compression ratio; a common picker operates across typed scheme families. [Compression-scheme interfaces](https://github.com/maxi-k/btrblocks/blob/master/btrblocks/scheme/CompressionScheme.hpp).
- **C3:** The picker offers sampled selection and exhaustive comparison, limits cascading depth, handles constant/all-null cases, and falls back to uncompressed storage when the chosen encoding expands the data. These expose both estimation quality and runtime cost. [Scheme picker](https://github.com/maxi-k/btrblocks/blob/master/btrblocks/compression/SchemePicker.hpp).

No production-hardening or current maintenance guarantee is inferred from the associated paper.

### 23. [cwida/FastLanes](https://github.com/cwida/FastLanes)

**Language/role:** C++ with bindings; research-driven columnar file format and data-parallel encoding framework.

Study compression expressed as operators, including compositions that use correlations across columns. This selection is the file-format implementation, not separate benchmark forks or isolated codec projects.

- **C2:** Physical expressions contain typed encoding and decoding operators for dictionary, run-length, floating-point, string, null, validity-mask, and cross-column operations. Visitor helpers distinguish encoding and decoding variants, exposing a reusable execution vocabulary. [Physical-expression representation](https://github.com/cwida/FastLanes/blob/dev/src/include/fls/expression/physical_expression.hpp).
- **C3:** The project's published design describes lightweight data-parallel encodings, automatic vectorization, partial decompression, and small-batch access intended to constrain cache/memory working sets. The README includes the file-format paper's architectural abstract and links to the underlying research. [Design/publication entry point](https://github.com/cwida/FastLanes#publications).

The advertised speed and compression multipliers are deliberately not repeated as established results.

## R-oriented and scientific columnar storage

### 24. [fstpackage/fstlib](https://github.com/fstpackage/fstlib)

**Language/role:** C++; implementation of the fst tabular format and the storage backend used by R's fst package.

Study a smaller native library whose table interface is designed around external column buffers and block streaming. The GitHub API snapshot showed the last push in February 2025; ongoing maintenance is not assumed.

- **C2:** `IFstTable` is a temporary serialization/deserialization interface over columns, with typed writers, column factories, names, keys, annotations, and dimensions. It decouples the file implementation from one dataframe's memory ownership. [Table interface](https://github.com/fstpackage/fstlib/blob/develop/lib/fst/interface/ifsttable.h).
- **C1 and C3:** The block streamer bounds per-thread batches, uses thread-specific scratch buffers, and orders writes from parallel work. It handles final partial blocks and distinct fixed-ratio/compressed paths. This is concrete material for studying concurrency, buffer sizing, and sequential file layout together. [Block-streaming implementation](https://github.com/fstpackage/fstlib/blob/develop/lib/fst/blockstreamer/blockstreamer_v2.cpp).

The R wrapper is not counted separately.

### 25. [root-project/root](https://github.com/root-project/root)

**Language/role:** C++; **RNTuple subsystem only** within the broader ROOT scientific-computing monorepo.

This adds a scientific-data community and a different object model. Study how nested C++ event data becomes typed columns and pages, with file/object-store backends beneath the user-facing event API.

- **C1:** The format distinguishes backward-incompatible epochs, forward-incompatible feature flags, and ignorable optional extensions. It also specifies checksums and the endianness difference between a ROOT-file anchor and RNTuple payload. [Binary format specification](https://github.com/root-project/root/blob/master/tree/ntuple/doc/BinaryFormatSpecification.md).
- **C2 and C3:** Storage, primitive-column, logical-type, and event-iteration layers have distinct responsibilities. Page sources/sinks, cluster pools, projected views, and descriptor lock guards isolate I/O, caching, selective reads, and evolving metadata. [RNTuple code architecture](https://github.com/root-project/root/blob/master/tree/ntuple/doc/Architecture.md).

ROOT's overall history does not by itself establish the age or stability of every RNTuple feature; the evidence here is subsystem-specific.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations. The main angles were:

- Standard columnar format implementations and design documents: Arrow, Parquet, and ORC.
- Language-specific ownership and APIs: Rust, Java, Go, C#, Julia, C, and modern C++.
- Browser/Node readers and interchange: range requests, typed arrays, IPC extraction, and JavaScript numerical conversion.
- Newer cloud/ML formats: wide schemas, random access, page layout, recursive compression, and object-storage I/O.
- Compression research: BtrBlocks and FastLanes, distinguishing implementation repositories from experiment-only forks.
- Less prominent and specialized communities: GeoArrow, R/fst, independent C++ arrays, and ROOT/RNTuple.

Later searches increasingly returned the same format families, wrappers, general database engines, and benchmark artifacts. Two useful late discoveries—Sparrow and Flechette—were retained because their ownership and value-conversion designs add distinct study material. Other Go Parquet implementations, including `fraugster/parquet-go` and `xitongsys/parquet-go`, were examined during discovery; this is a selective guide rather than a list of every implementation. Similarly, Julia Parquet alternatives were considered without expanding the list with another substantially overlapping file reader.

General SQL/dataframe engines, table/catalog formats alone, generic serialization systems, tensor-only interchange, and general-purpose compression libraries were outside the core scope. Arrow's C++ Parquet code and the fst R wrapper were not double-counted. The original Feather implementation and extra Arrow/Parquet implementation forks were not needed to represent separate current implementations; the deliberately retained historical selections are clearly marked. No selected repository is presented as an unofficial mirror.

Each retained repository has a verified canonical GitHub URL, separately inspected primary implementation/design material beyond its repository overview, and at least two justified criteria. Default-branch links are intentionally navigable but can change after the research date. Archive flags and push timestamps are only status observations; they do not establish support commitments. Experimental and retired projects remain useful for architectural study, while security assurance, full feature conformance, and comparative performance remain unverified.
