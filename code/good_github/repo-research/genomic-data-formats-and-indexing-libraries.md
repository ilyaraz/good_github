# Genomic data formats and indexing libraries

Research date: **2026-10-09**.

This report selects **28 GitHub repositories** implementing genomic file formats, compression, indexed access, or reusable genomic storage models. Coverage includes alignments, reference sequences, annotations, browser tracks, genotypes, nanopore signals, chromatin contacts, pangenome paths, and ancestral tree sequences. Broader repositories are included only for the identified storage or I/O subsystem; each monorepo counts once. This is a source-reading selection guide, not a certification that every component is exemplary or suitable for untrusted input.

The engineering assessments below are grounded in the linked primary material. Suggestions about what an engineer can learn are informed judgments. Links within entries double as source-tree or documentation starting points.

**Criteria legend**

- **C1 — Correctness:** demanding invariants, concurrency, numerical semantics, malformed inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or data models supporting multiple uses.
- **C3 — Performance:** concrete storage, CPU, memory, or I/O constraints addressed through understandable architecture.
- **C4 — Evolution:** sustained development with evidence of compatibility work, testing, or deliberate complexity management. Repository age and recent pushes alone do not qualify.

## Alignment and variant I/O foundations

### 1. [samtools/htslib](https://github.com/samtools/htslib)

**C — SAM/BAM/CRAM, VCF/BCF, BGZF, and genomic indexes.** A strong starting point for understanding how one C library combines format-specific decoders with shared I/O and query machinery.

- **C2:** The [format-neutral API](https://github.com/samtools/htslib/blob/develop/htslib/hts.h) separates file formats, index construction, record callbacks, single-region iterators, and multi-region iterators. Its shared thread-pool interface exposes queue sizing because many open files can otherwise consume excessive memory.
- **C1:** That API documents ownership, EOF versus error returns, coordinate conversion, and ambiguous reference-name parsing. These are observable contracts rather than merely parser implementation details.
- **C4:** The [release history](https://github.com/samtools/htslib/blob/develop/NEWS) connects 2019 changes such as larger coordinates and a new header API with compatibility aliases, through 2026 bounds checking, allocation-overflow protection, and removal of insufficiently tested experimental CRAM v4 code. This is unusually explicit evidence of managing both compatibility and complexity over years.

### 2. [samtools/htsjdk](https://github.com/samtools/htsjdk)

**Java — sequencing readers, writers, indexes, and codec infrastructure.** Study how a large object-oriented API represents indexed and streaming access without hiding all format differences.

- **C1:** [SamReader](https://github.com/samtools/htsjdk/blob/master/src/main/java/htsjdk/samtools/SamReader.java) specifies single-open-iterator restrictions, seekability limitations, overlap versus containment, one-based inclusive query coordinates, and the inclusion of coordinate-bearing unmapped reads. These contracts expose subtle correctness traps for clients.
- **C2:** The same source separates reader implementations, adapters, factories, and an indexing interface, including access to native index types rather than forcing every format into a BAM-shaped abstraction.
- **C4:** The [changelog](https://github.com/samtools/htsjdk/blob/master/CHANGELOG.md) describes the multi-year 2.x lineage and subsequent API migrations, including native CRAI queries, CSI support, and the transition to NIO paths. Read it alongside the interfaces to understand migration costs; default-branch documentation should not be assumed to describe every released version.

### 3. [zaeleus/noodles](https://github.com/zaeleus/noodles)

**Rust — independently implemented bioinformatics I/O crates.** Useful for studying typed representations of coordinates, virtual offsets, and format composition.

- **C2:** The [workspace overview](https://github.com/zaeleus/noodles/blob/master/README.md) explains per-format crates, an optional umbrella crate, and feature-controlled asynchronous I/O. BAM, CRAM, VCF, CSI, BGZF, FASTA, and annotation formats share infrastructure without requiring every consumer to enable every format.
- **C1/C3:** The [binning-index abstraction and implementation](https://github.com/zaeleus/noodles/blob/master/noodles-csi/src/binning_index.rs) uses typed intervals and BGZF positions, filters chunks below a minimum offset, and sorts and merges overlapping chunks before reading. Checked shifts guard maximum-position calculations, and accompanying tests exercise chunk combinations.

The project explicitly calls its API experimental. Its attraction here is its decomposition and implementation detail, rather than a claim of a frozen interface.

### 4. [biogo/hts](https://github.com/biogo/hts)

**Go — native SAM/BAM, BGZF, BAI/CSI/tabix, and FASTA-index support.** A compact alternative perspective on concurrency in compressed genomic I/O.

- **C1:** The [BGZF reader](https://github.com/biogo/hts/blob/master/bgzf/reader.go) serializes ownership of the underlying read head with a channel while decompressors work asynchronously. It tracks physical and in-block offsets separately and distinguishes corrupt or missing BGZF block-size information from ordinary EOF.
- **C3:** The same implementation separates read-ahead buffers, decompression workers, block ownership, and a configurable cache. This makes the interaction among parallel decompression, seeking, and reuse visible.
- **C2:** The [overview](https://github.com/biogo/hts/blob/master/README.md) describes consistent alignment and compression interfaces and demonstrates avoiding variable-length record decoding when only flags are needed.

GitHub metadata showed the latest push in August 2025; this entry does not imply a rapid maintenance cadence. The listed `cram` directory is not evidence of a complete CRAM implementation.

### 5. [pysam-developers/pysam](https://github.com/pysam-developers/pysam)

**Python/Cython over HTSlib — genomic file access and record manipulation.** Included as a substantive language boundary, not as an independent implementation of the underlying file codecs.

- **C1:** The [FAQ](https://github.com/pysam-developers/pysam/blob/master/doc/faq.rst) explains shared file-position hazards, why separate iterators may need separate file handles, and why changing a sequence invalidates associated quality storage. It also describes proxy-object lifetimes and coordinate conversions.
- **C3:** The same document explains releasing the GIL during I/O, the cost of reopening files for independent iterators, and why sequential traversal can avoid repeated seeks across many reference sequences. These are useful examples of performance decisions shaping a Python API.
- **C2:** The [repository overview](https://github.com/pysam-developers/pysam/blob/master/README.rst) identifies the HTSlib/samtools/tabix integration and bundled upstream versions.

The FAQ explicitly says thread safety has not been fully tested everywhere; GIL release should not be read as a blanket thread-safety guarantee.

### 6. [BioJulia/XAM.jl](https://github.com/BioJulia/XAM.jl)

**Julia — SAM/BAM records, readers, writers, and indexed overlap queries.** A useful smaller codebase for examining allocation policy and language-native iteration.

- **C2/C3:** The [I/O guide](https://github.com/BioJulia/XAM.jl/blob/develop/docs/src/man/hts-files.md) offers both allocating record iteration and `read!` into a reusable record. The distinction lets applications trade convenient ownership for lower allocation pressure while retaining the same format abstractions.
- **C1:** The [overlap iterator](https://github.com/BioJulia/XAM.jl/blob/develop/src/bam/overlap.jl) resolves reference names, obtains candidate index chunks, seeks using virtual offsets, and stops scanning when sorted records move beyond the query. It copies a reused internal record before returning it, exposing an important aliasing boundary.

This is specifically a SAM/BAM selection, not a claim of CRAM or VCF support. The source also retains an explicit EOF-handling workaround, useful context when evaluating polish.

## Specialized codecs and trace-format compatibility

### 7. [samtools/htscodecs](https://github.com/samtools/htscodecs)

**C — CRAM block codecs, including rANS, arithmetic coding, read names, and quality scores.** Study the computational core beneath several higher-level readers.

- **C1:** The [quality-codec round-trip fuzz target](https://github.com/samtools/htscodecs/blob/master/tests/fqzcomp_qual_fuzzrt.c) varies record segmentation and compression strategy, then checks decompressed length and byte identity. It tests more than whether a decoder avoids crashing.
- **C3:** The [interleaved rANS implementation](https://github.com/samtools/htscodecs/blob/master/htscodecs/rANS_static32x16pr.c) normalizes symbol frequencies, maintains multiple coding states, and selects different inner-loop strategies according to entropy. Comments explain table-size, alignment, compiler, and branch-behavior tradeoffs.

The reusable library is distinct from HTSlib's container/index machinery. Its value as a study target lies in entropy-coder invariants and architecture-conscious optimization; benchmark numbers are deliberately not repeated here.

### 8. [jkbonfield/io_lib](https://github.com/jkbonfield/io_lib)

**C — Staden sequencing trace formats and compatibility APIs.** A historically important codebase that remains useful for studying long-lived scientific data interfaces.

- **C2:** [Read.h](https://github.com/jkbonfield/io_lib/blob/master/io_lib/Read.h) defines a common representation for bases, sampled traces, and their positional relationship across formats including SCF, ABI, ZTR, and SFF. This is a different abstraction problem from alignment records.
- **C4:** The [change history](https://github.com/jkbonfield/io_lib/blob/master/CHANGES) documents years of threading, indexing, endianness, and test-harness fixes, followed by the 2026 decision to delegate BAM/CRAM I/O to HTSlib. It explicitly records API/ABI incompatibilities, removed interfaces, retained header APIs, and the cost of converting record memory layouts.

**Important boundary:** current io_lib is not counted as a separate current CRAM engine. Its maintainers recommend using HTSlib directly for SAM/BAM/CRAM; this entry is for trace I/O and the engineering of compatibility and consolidation.

## Reference sequences and annotation databases

### 9. [mdshw5/pyfaidx](https://github.com/mdshw5/pyfaidx)

**Python — FASTA indexing and subsequence access using samtools-compatible `.fai` files.** An accessible case study in mapping sequence coordinates onto physical file layout.

- **C1:** The [implementation](https://github.com/mdshw5/pyfaidx/blob/master/pyfaidx/__init__.py), particularly `Faidx.from_file` and `to_file`, accounts for line terminators, bounds policies, BGZF block offsets, and locking around seek/read operations. In-place replacement checks length to preserve the indexed layout.
- **C2:** The [API examples](https://github.com/mdshw5/pyfaidx/blob/master/README.rst) layer `Fasta`, records, and sequence slices over the index; they distinguish slicing coordinates from sequence display attributes and expose configurable duplicate-name policies.
- **C3:** Offset arithmetic and `.gzi` lookup permit targeted reads without materializing the whole reference. This is a clear small-scale illustration of how an external index enables a much larger logical object.

### 10. [lmdu/pyfastx](https://github.com/lmdu/pyfastx)

**C with Python bindings — indexed plain and gzip-compressed FASTA/FASTQ.** Especially interesting when comparing ordinary gzip access with BGZF-based designs.

- **C3:** The [index implementation](https://github.com/lmdu/pyfastx/blob/master/src/index.c) combines sequence offsets in SQLite with a `zran` gzip index, uses prepared statements and bulk transactions during construction, and retains sequence-cache state. Disk-backed indexing avoids requiring every sequence name and offset to live in Python memory.
- **C1:** The same code records line-ending width and whether sequence lines have uniform lengths, rather than assuming every FASTA is regularly wrapped. It separately tracks byte lengths and biological sequence lengths.
- **C2:** The [documented API](https://github.com/lmdu/pyfastx/blob/master/README.rst) supports ID/index access and iteration with or without index construction. It candidly explains that repeated membership tests can be expensive because they become SQLite queries.

### 11. [daler/gffutils](https://github.com/daler/gffutils)

**Python/SQLite — persistent GFF/GTF features and relationships.** Study a parser whose job includes preserving messy real-world conventions and reconstructing hierarchical annotation data.

- **C1:** The [dialect design](https://github.com/daler/gffutils/blob/master/doc/source/dialect.rst) models attribute separators, quoting, repeated keys, and semicolon conventions. It infers a dialect from input lines so serialization can retain the original formatting conventions.
- **C2/C3:** The [database schema](https://github.com/daler/gffutils/blob/master/doc/source/database-schema.rst) separates features, parent/child relationships, metadata, directives, duplicate IDs, and persistent autoincrement state. UCSC-style genomic bins support region lookup, while the relationship table supports gene/transcript/exon traversal.

The particularly useful lesson is that stable feature identity and parentage are separate concerns from genomic coordinates. The documentation characterizes its relationship model as suitable for relatively simple graph structures, not an unrestricted graph database.

## Browser and remote indexed access

### 12. [GMOD/tabix-js](https://github.com/GMOD/tabix-js)

**TypeScript — TBI/CSI queries over tabix-indexed data in browsers and Node.js.** A good study target for remote byte ranges, asynchronous sharing, and memory accounting.

- **C2/C3:** The [query dataflow](https://github.com/GMOD/tabix-js/blob/main/docs/dataflow.md) separates index parsing, compressed chunk retrieval, WebAssembly decompression, and byte scanning. Optional worker execution moves decompression while keeping line parsing in JavaScript.
- **C1:** The [cache design](https://github.com/GMOD/tabix-js/blob/main/docs/caching.md) describes shared in-flight reads and per-caller cancellation: one cancelled query must not discard a chunk another caller needs. It also explains why byte-weighted cache budgets cannot be mixed with caches measured in records or entries.

The cache documentation distinguishes retained decompressed bytes from peak memory, records a compatibility-sensitive change in the meaning of `chunkCacheSize`, and explains working-set thrashing. These limitations are part of the architectural lesson.

### 13. [GMOD/cram-js](https://github.com/GMOD/cram-js)

**TypeScript/JavaScript with C codecs compiled to WebAssembly — CRAM and CRAI reading.** This is a substantial container, record, and query implementation that reuses upstream codec code.

- **C2:** The [query architecture](https://github.com/GMOD/cram-js/blob/main/docs/dataflow.md) decomposes CRAI lookup into containers, slices, compressed blocks, record decoding, reference application, and mate-related access. A reference callback stays on the main thread because it cannot simply be transferred to a worker.
- **C3:** That design uses typed column arrays for read features, tags, and qualities; whole-slice worker execution; and block-level crossings into WebAssembly. It explains why decompression-only workers leave substantial work behind and why column arrays enable transferable results.
- **C1:** Shared container/header state, reference-dependent reconstruction, and record ownership across worker boundaries are concrete correctness concerns exposed by this architecture.

Do not mistake the repository for an independently authored implementation of every entropy codec: its current design explicitly incorporates HTS codecs in WebAssembly.

## Quantitative tracks and chromatin-contact indexes

### 14. [dpryan79/libBigWig](https://github.com/dpryan79/libBigWig)

**C — local/remote BigWig and BigBed reading, with BigWig writing.** Study the relationship between compressed interval blocks, summary levels, and numerical query semantics.

- **C2/C3:** The [public API and structures](https://github.com/dpryan79/libBigWig/blob/master/bigWig.h) expose interval iterators, configurable blocks per iteration, chromosome metadata, R-tree indexes, and zoom-level summaries. The writing documentation explains why mixing entry encodings creates extra blocks.
- **C1:** The [statistics implementation](https://github.com/dpryan79/libBigWig/blob/master/bwStats.c) distinguishes interval-level calculations from zoom-block calculations, weights partial overlaps, and handles empty coverage and floating-point variance behavior. It is a useful place to examine what a summarized query actually means.

The header explicitly states an endianness assumption. Its error-return approach and standalone scope are useful, but neither implies universal format portability or a completed parser-security audit.

### 15. [jackh726/bigtools](https://github.com/jackh726/bigtools)

**Rust, with Python bindings in the same repository — BigWig/BigBed readers and writers.** A contrasting design for the same track formats.

- **C2:** The [crate architecture](https://github.com/jackh726/bigtools/blob/master/bigtools/src/lib.rs) accepts readers implementing `Read` and `Seek`, returns region iterators, and makes `BBIDataSource` the abstraction for writing data. Consumers can supply generated values or custom scheduling instead of first creating a text file.
- **C3:** The same documentation separates per-chromosome work from compression and I/O on an asynchronous runtime. Serial and parallel streaming data sources make the scheduling choices explicit.

The [repository overview](https://github.com/jackh726/bigtools/blob/master/README.md) identifies the Rust library, related command-line tools, and Python interface. Count those as one implementation family; the instructive comparison is with libBigWig's block-oriented C API, not the number of wrappers or binaries.

### 16. [38/d4-format](https://github.com/38/d4-format)

**Rust, with C/Python interfaces — Dense Depth Data Dump quantitative genomic tracks.** Study a format designed around the distribution of per-base values rather than only generic compression.

- **C2:** The [primary-table interfaces](https://github.com/38/d4-format/blob/master/d4/src/ptab/mod.rs) separate readers, writers, partitions, encoders, and decoders. Decoding explicitly distinguishes a definite value from a value that requires checking a secondary table.
- **C1/C3:** The [track reader](https://github.com/38/d4-format/blob/master/d4/src/d4file/reader.rs) pairs a bit-array primary table with a sparse secondary table and splits both over corresponding genomic regions. That correspondence is an important invariant when distributing work across partitions.

The monorepo also contains framing, indexing, bindings, and command-line components; this entry centers on the format library. GitHub metadata showed the latest push in November 2025, so current support responsiveness was not established.

### 17. [open2c/cooler](https://github.com/open2c/cooler)

**Python/HDF5 — indexed sparse genomic contact matrices and multi-resolution containers.** Useful for learning how a domain format can add sparse structure to a general dense-array container.

- **C1:** The [schema](https://github.com/open2c/cooler/blob/master/docs/schema_v3.rst) specifies ordered genomic bins, sorted pixel coordinates, offset arrays, and different semantics for symmetric-upper and ordinary square storage. Reconstructing symmetry incorrectly would change query results; schema-v2 compatibility is explicitly addressed.
- **C2/C3:** The [selection model](https://github.com/open2c/cooler/blob/master/docs/concepts.rst) provides lazy table and matrix selectors, genomic-region lookup, and URIs for individual collections inside HDF5. The schema's chromosome and row-offset indexes map those requests onto compressed sparse rows.

This selection concerns `.cool`/`.mcool` layout and query abstractions, rather than endorsing every downstream matrix-analysis routine in the repository.

### 18. [4dn-dcic/pairix](https://github.com/4dn-dcic/pairix)

**C with Python bindings — one- and two-dimensional indexing of paired genomic coordinates.** Retained despite its tabix ancestry because paired-coordinate indexing is a substantive extension with its own `.px2` format and query semantics.

- **C1:** The [format and query guide](https://github.com/4dn-dcic/pairix/blob/master/README.md) specifies chromosome-pair sorting, position ordering, wildcard queries, symmetric-query interpretation, and optional query flipping. These semantics matter for upper-triangular Hi-C pairs.
- **C2/C3:** The [index implementation](https://github.com/4dn-dcic/pairix/blob/master/src/index.c) combines chromosome-pair identifiers, hierarchical bins, linear offsets, and iterators with two coordinate ranges. Presets and configurable columns generalize it beyond one fixed text layout.

The bundled bgzip code is not counted as a new compressor. GitHub metadata showed the latest push in January 2025. Some non-pairs parser paths carry explicit testing caveats in the source, so this is primarily a paired-coordinate indexing study target.

## Genotype formats and cohort storage

### 19. [limix/bgen](https://github.com/limix/bgen)

**C — BGEN genotype-probability decoding and partitioned metadata access.** A focused alternative to large all-purpose HTS libraries.

- **C1:** The [layout-2 decoder](https://github.com/limix/bgen/blob/main/src/layout2.c) handles phased and unphased probabilities, variable ploidy, missingness bits, allele counts, bit widths, and float32/float64 output. Reconstructing probabilities from packed integers is a substantial numerical and combinatorial contract.
- **C2/C3:** The [interface guide](https://github.com/limix/bgen/blob/main/doc/interface.rst) separates file, genotype, sample, variant, metafile, and partition handles, with explicit destruction rules. Metadata partitions and per-variant genotype access let callers avoid loading an entire cohort representation.

**Maintenance caveat:** the GitHub API reported the latest push as 2024-06-17. It was not archived at research time, but ongoing maintenance was not established. This selection is an implementation reference, not a blanket recommendation for new deployments.

### 20. [chrchang/plink-ng](https://github.com/chrchang/plink-ng)

**C/C++ with Python/Cython and R interfaces — specifically the PLINK 2 `pgenlib` subsystem.** The repository counts once; the broader association-analysis toolset is outside this entry's scope.

- **C1:** The [pgenlib Python API contract](https://github.com/chrchang/plink-ng/blob/master/2.0/Python/python_api.txt) specifies ordered sample subsets, allele-offset arrays, missing-value conventions, phased-dosage reconstruction, and fixed dosage precision. It also identifies chromosome-specific adjustments that remain the caller's responsibility.
- **C2/C3:** The same API supports individual variants, ranges, lists, alternative output orientations, and caller-provided NumPy buffers. Its rationale explicitly connects required output buffers to allocation overhead.

The [binding entry point](https://github.com/chrchang/plink-ng/blob/master/2.0/Python/README.md) links the interface into the canonical upstream monorepo and provides writer examples and test entry points. Repackaged pgenlib repositories are not separate selections.

### 21. [GenomicsDB/GenomicsDB](https://github.com/GenomicsDB/GenomicsDB)

**C++ with Java integration — sparse-array storage and querying of variant calls.** Study the consequences of organizing cohort data by genomic position versus by sample.

- **C3:** The [storage overview](https://github.com/GenomicsDB/GenomicsDB/blob/main/docs/overview.rst) explains why column-major storage favors queries across samples at a locus, why sample-wide queries have a different locality cost, and how repeated incremental imports accumulate fragments that affect querying.
- **C1/C2:** The [import model](https://github.com/GenomicsDB/GenomicsDB/blob/main/docs/import-etl.rst) maps calls onto array cells, defines fixed- and variable-length fields and missing values, and explains partitioning constraints for distributed imports. It is reusable storage infrastructure rather than one analysis algorithm.

A material limitation is explicit: indexed VCF input with multiple records at the same chromosome/position requires preprocessing. The choice of an internal cell model imposes constraints on otherwise valid external files.

### 22. [sgkit-dev/bio2zarr](https://github.com/sgkit-dev/bio2zarr)

**Python — genomic conversion into chunked Zarr arrays, especially VCF Zarr.** Study how a conversion pipeline discovers array shapes while controlling memory and distributing work.

- **C2/C3:** The [VCF conversion design](https://github.com/sgkit-dev/bio2zarr/blob/main/docs/vcf2zarr/overview.md) first produces an intermediate columnar format, then encodes Zarr arrays. This permits correct field dimensions and bounded working memory; initialization, partition work, and finalization can run across a cluster.
- **C1:** The [property-based VCF test](https://github.com/sgkit-dev/bio2zarr/blob/main/tests/test_vcf_hypothesis.py) generates VCF inputs and runs the indexed conversion path. It deliberately uses CSI for positions outside TBI's range. This test demonstrates generated-input robustness coverage, not complete semantic round-trip verification.

The documentation calls the ecosystem early-stage, treats the intermediate format as unstable, and marks local-allele reduction experimental. Those are material adoption constraints, not reasons to overlook the pipeline architecture.

### 23. [zhengxwen/SeqArray](https://github.com/zhengxwen/SeqArray)

**R/C++ — sequencing-specific genotype storage on GDS.** The GitHub repository is the development version; the project distinguishes it from Bioconductor releases.

- **C1/C3:** The [format and access tutorial](https://github.com/zhengxwen/SeqArray/blob/master/vignettes/SeqArrayTutorial.Rmd) describes two-bit genotype arrays, additional bit planes for more alleles, per-variant indexing, variable-length annotation lengths, and independent compressed blocks for random access. It also documents extra storage for additional ploidy.
- **C2:** The [R integration design](https://github.com/zhengxwen/SeqArray/blob/master/vignettes/SeqArray.Rmd) composes sample/variant filtering, data retrieval, margin-wise functions, and parallel execution. Work can be split by samples or variants while callers use common operations.

This is specifically the sequencing schema and access layer, built over gdsfmt/CoreArray; the underlying generic storage engine is not claimed as a separate implementation within this repository.

## Nanopore signal formats

### 24. [hasindu2008/slow5lib](https://github.com/hasindu2008/slow5lib)

**C with Python bindings — SLOW5/BLOW5 raw nanopore signals.** A useful contrast between textual records, individually compressed binary records, and read-ID indexing.

- **C1:** The [index implementation](https://github.com/hasindu2008/slow5lib/blob/master/src/slow5_idx.c) builds ID-to-offset/size mappings through different text and binary paths, checks index/file version agreement, and warns about an older index timestamp. These mechanisms expose stale-index and layout-consistency problems directly.
- **C2/C3:** The [usage and architecture guide](https://github.com/hasindu2008/slow5lib/blob/master/docs/getting_started.md) distinguishes sequential access, indexed read-ID lookup, parallel access, and layered signal/record compression. Applications can use lower-level functions or the optional multithread API.

The documentation records native-Windows and codec-specific big-endian limitations. Compression portability and library portability should therefore be evaluated separately.

### 25. [nanoporetech/pod5-file-format](https://github.com/nanoporetech/pod5-file-format)

**C++/Python — streaming nanopore signal files built on Apache Arrow.** Particularly useful for studying file design under acquisition-time failure and downstream batch-access requirements.

- **C1:** The [design document](https://github.com/nanoporetech/pod5-file-format/blob/master/docs/DESIGN.md) describes recognizable completion footers, append-only data, and recovery by sequentially reading the underlying Feather structure. Recovery is a stated design goal, not a claim that arbitrary corruption is repairable.
- **C2/C3:** The same document explains memory-mappable Arrow data, direct signal-location information, chunked long-read signals, dictionary encoding, and lock-free file reading. Self-describing named columns support schema extension.

The [repository overview](https://github.com/nanoporetech/pod5-file-format/blob/master/README.md) identifies the core library and language tooling. The format deliberately prioritizes sequential writing and does not optimize editing existing files; that tradeoff is central to understanding it.

## Pangenome and ancestry representations

### 26. [jltsiren/gbwt](https://github.com/jltsiren/gbwt)

**C++ — compressed substring indexes over haplotype paths in graphs.** Study how a genomic path collection becomes a multi-string FM-index rather than a conventional coordinate-indexed file.

- **C2/C3:** The [architecture overview](https://github.com/jltsiren/gbwt/blob/master/README.md) distinguishes compressed, dynamic, and cached GBWT representations; node-local records improve locality, while separate insertion and merging algorithms address index construction.
- **C1:** The [serialization specification](https://github.com/jltsiren/gbwt/blob/master/SERIALIZATION.md) makes rank/select conventions, local alphabets, run-length encoding, endmarkers, reverse-strand identifiers, and forward/reverse path pairing explicit. These invariants connect on-disk representation to query semantics.

The serialization document also distinguishes the portable Simple-SDS format from earlier SDSL-based storage and records version-dependent compression. This entry is the path index; graph sequence storage is handled by the next project.

### 27. [jltsiren/gbwtgraph](https://github.com/jltsiren/gbwtgraph)

**C++ — GBWT-backed sequence graphs, GBZ serialization, and GFA conversion.** Separate from GBWT because it adds a substantive graph representation and format layer, rather than only forwarding index calls.

- **C2/C3:** The [implementation overview](https://github.com/jltsiren/gbwtgraph/blob/master/README.md) uses GBWT for topology and paths while retaining node sequences for direct views. It supplies handle-graph interfaces, explicit cached overlays, haplotype-supported traversal, and minimizer/k-mer indexing.
- **C1:** The [GBZ specification](https://github.com/jltsiren/gbwtgraph/blob/master/SERIALIZATION.md) requires a bidirectional GBWT and defines version combinations, node-presence rules, flags, path-name mapping, and translation from string-named GFA segments to node-ID ranges.

Its GFA support is deliberately a subset: overlaps, containments, and optional fields are not generally preserved. Cache lifetime is also consequential because documented local caches retain every accessed node record.

### 28. [tskit-dev/tskit](https://github.com/tskit-dev/tskit)

**C/Python — ancestral tree-sequence tables, indexes, and `.trees` serialization.** Included for its genomic data representation and storage subsystem, not for simulation or inference applications built around it.

- **C1:** The [data model](https://github.com/tskit-dev/tskit/blob/main/docs/data-model.md) specifies valid node references, finite genomic intervals, older parents, unique edges, and ordering rules. Load-time validation and edge indexes connect these requirements to efficient tree traversal; mutable tables and immutable indexed tree sequences have different roles.
- **C2/C3:** The [file-format documentation](https://github.com/tskit-dev/tskit/blob/main/docs/file-formats.md) maps tables directly into a columnar binary numerical store based on kastore. This supports reuse of one compact representation across many ancestry analyses.

Compatibility has a clear boundary: current documentation supports earlier files within the same major format version, while pre-kastore HDF5 files require conversion using an older tskit release.

## Search coverage, verification, and limitations

Discovery used live web searches with more than six distinct formulations: SAM/BAM/CRAM and BGZF foundations; Rust/Go/Julia native implementations; BigWig/BigBed and dense tracks; browser tabix/CRAM access; plain/gzip FASTA random access; GFF/GTF annotation databases; BGEN/PGEN and cohort storage; Arrow/Zarr/GDS genomics; nanopore POD5/SLOW5; graph-path indexes; and Hi-C paired-coordinate indexing. Later cross-cutting searches mainly rediscovered these families and broader analysis packages. The list extends beyond 25 to retain distinct annotation, R/Bioconductor, and paired-coordinate architectures rather than adding more wrappers for the same codec.

Every retained canonical repository URL was checked through GitHub's repository API. Source trees were inspected, and each entry has at least one additional opened primary implementation or architectural source beyond repository metadata or a tagline. The GitHub API marked all retained repositories as non-archived at research time. That is not evidence of a support commitment. In particular, the latest-push observations for [limix/bgen](https://api.github.com/repos/limix/bgen), [biogo/hts](https://api.github.com/repos/biogo/hts), [38/d4-format](https://api.github.com/repos/38/d4-format), and [Pairix](https://api.github.com/repos/4dn-dcic/pairix) are status observations, not C4 evidence. No retained repository was identified as merely an official mirror or an unmodified fork.

Specifications-only collections such as hts-specs, benchmark collections, tutorials, workflow wrappers, and repackaged bindings were excluded as entries. Broad analysis libraries such as SeqAn and SeqLib surfaced in discovery but were not added merely because they also read genomic files. The selection favors distinct storage and indexing designs; it is not an exhaustive catalog of SRA, every annotation parser, or every HTSlib binding. Pysam is retained because its ownership, coordinate, and concurrency boundary is itself substantial; borrowed codec implementations are identified explicitly.

Research was read-only: no candidate code was executed, dependencies installed, repositories cloned, benchmarks reproduced, or maintainers contacted. Performance assessments concern observed architecture, not independently measured speed. Links point to the verified default-branch material available on the research date, so future branch contents may differ. Tests cited here were read, not run; C1 means that a project contains instructive correctness challenges and mechanisms, not that all such challenges are solved.
