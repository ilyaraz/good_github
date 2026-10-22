# Erasure coding libraries

Research date: **2026-10-09**.

This selection covers 22 GitHub repositories implementing reusable erasure coding: matrix and polynomial Reed–Solomon codecs, transform-based large-block codecs, fountain and LDPC codes, streaming/network coding, GPU kernels, and storage-oriented coding interfaces. Ceph is included once, specifically for its erasure-code library and plugins. General storage products that merely consume these libraries, bindings without substantial independent logic, and unrelated error-correction implementations are excluded.

The criteria below identify worthwhile engineering study, not a guarantee that every component is safe, current, or equally well designed. In particular, recovering known missing shards and correcting unidentified corruption are different capabilities; individual entries identify that distinction where it matters.

## Criteria

- **C1 — Correctness:** difficult invariants, concurrency, finite-field semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or components supporting multiple applications or coding configurations.
- **C3 — Performance:** concrete computational, memory, latency, or repair-bandwidth constraints addressed through understandable architecture.
- **C4 — Evolution:** sustained development with evidence of compatibility work, testing, or complexity management across years. Age and recent pushes alone do not qualify.

Repository URLs and archive/default-branch metadata were checked through GitHub pages or the GitHub API. None of the retained repositories was marked archived at research time. Historical status and support caveats below are separate from GitHub's archive flag; a recorded push is not proof of ongoing support.

## Storage interfaces, arithmetic kernels, and GPU execution

### 1. [intel/isa-l](https://github.com/intel/isa-l)

**C and assembly; storage primitives, specifically the erasure-code subsystem.** Study the boundary between code construction and optimized execution: the erasure API accepts caller-chosen GF(256) coefficients, expands them into multiplication tables, and applies the same vector machinery to encoding and recovery.

- **C2:** General coefficient matrices and separate table initialization, bulk coding, and single-source parity updates let higher-level libraries choose their own code and repair policy. The [API header](https://github.com/intel/isa-l/blob/master/include/erasure_code.h) documents the coefficient/table/buffer contracts.
- **C3:** Runtime instruction-set dispatch, portable baseline functions, and kernels computing several output vectors together expose a clear architecture for reducing repeated input traffic. The [release notes](https://github.com/intel/isa-l/blob/master/Release_notes.txt) document GFNI, SVE, and RISC-V vector work, plus fixes to table sizing and unaligned accesses.

The repository explicitly leaves substantial argument validation to callers. It is particularly useful for studying low-level contracts, not as an example of a fully defensive public decoder. Entry points: the API header and release notes above.

### 2. [tsuraan/Jerasure](https://github.com/tsuraan/Jerasure)

**C; Reed–Solomon, Cauchy, and RAID-oriented coding machinery.** A historical reference implementation whose recorded last push was January 2018. Study how a finite-field matrix becomes a binary matrix and then an executable sequence of copies and XORs.

- **C1:** Recovery selects surviving matrix rows and inverts the resulting matrix; erasure identifiers, word widths, alignment, and packet sizes must agree. The [public header](https://github.com/tsuraan/Jerasure/blob/master/include/jerasure.h) explains these representations and singular-matrix failure handling.
- **C3:** Its smart scheduling reuses previous dot products, while lazy and cached decode schedules make different setup-versus-execution tradeoffs. These mechanisms are documented in the same header. The [repository overview](https://github.com/tsuraan/Jerasure#readme) explains the replacement of the original arithmetic backend with GF-Complete while preserving earlier usage patterns.

Entry points: `include/jerasure.h` and the repository overview above. Do not count the Ceph-hosted Jerasure fork as an additional independent library in this selection.

### 3. [openstack/liberasurecode](https://github.com/openstack/liberasurecode)

**C; pluggable storage erasure-code API. Official GitHub mirror of OpenDev development.** This is more than a thin binding: it owns backend lifecycle, fragment formatting, metadata, validation, and native coding backends.

- **C1:** Backend instances share a registry protected by a read/write lock; the implementation explicitly includes backend initialization within the protected scope because initializers cannot be assumed thread-safe. Fragment metadata also carries backend/version and checksum information. See the [implementation](https://github.com/openstack/liberasurecode/blob/master/src/erasurecode.c).
- **C2:** Dynamically loaded backends sit behind one interface for encode/decode, individual-fragment reconstruction, and determining the fragments required for repair. The [public API](https://github.com/openstack/liberasurecode/blob/master/include/erasurecode/erasurecode.h) makes ownership and cleanup responsibilities explicit.

Study how a uniform storage contract accommodates different mathematical engines without forcing applications to link every backend. Entry points: `src/erasurecode.c` and `include/erasurecode/erasurecode.h`.

### 4. [ceph/ceph](https://github.com/ceph/ceph)

**C++; the `src/erasure-code` library and plugin subsystem within the Ceph monorepo.** Included for its coding and repair abstractions, not for the whole storage platform or another copy of ISA-L/Jerasure.

- **C2:** The [plugin interface](https://github.com/ceph/ceph/blob/main/src/erasure-code/ErasureCodeInterface.h) separates requested outputs, available chunks, reconstruction, and the cost of fetching helpers. This shows why a storage codec needs more than `encode` and `decode`.
- **C3:** The [LRC guide](https://github.com/ceph/ceph/blob/main/doc/rados/operations/erasure-code-lrc.rst) explains recursively composed coding layers and placement locality, reducing the number of storage nodes contacted for repair. It exposes the tradeoff between extra local parity and repair traffic.

The related [CLAY guide](https://github.com/ceph/ceph/blob/main/doc/rados/operations/erasure-code-clay.rst) explains sub-chunk repair and helper-count tradeoffs, but the inspected main-branch documentation marks CLAY deprecated in Umbrella and scheduled for removal in Vampire. Entry points: the interface and LRC guide; CLAY remains an explicitly qualified design reference.

### 5. [sandialabs/gibraltar](https://github.com/sandialabs/gibraltar)

**C and CUDA; GPU Reed–Solomon library. Historical implementation; recorded last push October 2020.** The [overview](https://github.com/sandialabs/gibraltar/blob/master/README) identifies CUDA, Jerasure, and CPU-reference backends.

- **C1:** GPU recovery combines finite-field tables, matrix coefficients, synchronized shared-memory initialization, and strict buffer divisibility assumptions. The [CUDA kernel](https://github.com/sandialabs/gibraltar/blob/master/src/gib_cuda_checksum.cu) also preserves a documented compiler-workaround path, illustrating toolchain-dependent correctness.
- **C3:** The [host driver](https://github.com/sandialabs/gibraltar/blob/master/src/gib_cuda_driver.c) specializes kernels for the data/parity counts, caches generated PTX, and distinguishes mapped-host-memory operation from device-buffer operation. The kernel stages arithmetic tables in shared memory.

Study specialization and data movement together. This is a historical architecture reference: the source retains old CUDA assumptions, and driver-error paths may terminate the process. Entry points: the host driver and CUDA kernel above.

## General-purpose Reed–Solomon libraries

### 6. [klauspost/reedsolomon](https://github.com/klauspost/reedsolomon)

**Go and assembly; general storage and transport shard coding.** Although descended from Backblaze's Java implementation, this has substantial independent work in streaming, incremental operations, architecture-specific kernels, and large-shard-count coding.

- **C1:** The [hardening tests](https://github.com/klauspost/reedsolomon/blob/master/hardening_test.go) cover mismatched update buffers, empty-versus-missing shard semantics, SIMD tails, and overflowing shard counts. Guard regions detect writes beyond shard boundaries.
- **C2:** The [core interface](https://github.com/klauspost/reedsolomon/blob/master/reedsolomon.go) distinguishes full, data-only, and selected-shard reconstruction, incremental parity, updates, and split/join operations. It documents when caller storage is reused and when integrity remains unverified.
- **C3:** The [repository guide](https://github.com/klauspost/reedsolomon#readme) explains shard-size-aware goroutine selection and the Leopard path for larger shard counts.

Entry points: `reedsolomon.go` and `hardening_test.go`. Especially useful for studying the interaction between a convenient API and aggressive buffer/kernel optimization.

### 7. [Backblaze/JavaReedSolomon](https://github.com/Backblaze/JavaReedSolomon)

**Java; compact systematic Reed–Solomon implementation.** A useful conceptual baseline for several later ports. The repository carries a `non-production` topic, so its value here is as a substantive, readable implementation rather than a support recommendation.

- **C1:** [ReedSolomon.java](https://github.com/Backblaze/JavaReedSolomon/blob/master/src/main/java/com/backblaze/erasure/ReedSolomon.java) constructs a systematic matrix from a Vandermonde matrix, selects surviving rows for recovery, reconstructs missing data, and then regenerates missing parity. These stages expose the central invariants clearly.
- **C3:** The [performance notes](https://github.com/Backblaze/JavaReedSolomon#performance-notes) describe twelve loop-order/arithmetic variants and a benchmark parameterized to the intended workload. This is a concrete example of separating the algorithm from the inner-loop strategy.

Entry points: the codec class and the performance notes. Its small class structure is particularly approachable before studying SIMD or transform-based alternatives.

### 8. [tahoe-lafs/zfec](https://github.com/tahoe-lafs/zfec)

**C core with Python and Haskell interfaces; erasure coding library and file tools.** The APIs distinguish primary and secondary blocks, reconstruction metadata, and output buffers while deliberately avoiding unnecessary copies.

- **C2:** The [repository API description](https://github.com/tahoe-lafs/zfec#api) connects low-level buffer operations to higher-level file and language interfaces. It explicitly explains that returning references to mutable input can change previously returned results.
- **C3:** The [C core](https://github.com/tahoe-lafs/zfec/blob/master/zfec/fec.c) separates finite-field table generation, multiply-add loops, and matrix operations, making its space-versus-arithmetic tradeoffs inspectable.
- **C4:** [NEWS.txt](https://github.com/tahoe-lafs/zfec/blob/master/NEWS.txt) records validation and test fixes in 2009, Python and Windows compatibility work in 2018–2020, GIL-release and platform packaging work in 2023, and changed platform baselines in 2024.

Entry points: `zfec/fec.c` and `NEWS.txt`. This is a strong example of how language-runtime behavior becomes part of a coding library's engineering obligations.

### 9. [rust-rse/reed-solomon-erasure](https://github.com/rust-rse/reed-solomon-erasure)

**Rust, with optional C SIMD support; generic matrix-based erasure coding.** The repository explicitly seeks new owners/maintainers, and its recorded last push was August 2023. Its ancestry in the Java, Go, and Haskell projects is acknowledged rather than treated as a new algorithm.

- **C1:** The [crate source](https://github.com/rust-rse/reed-solomon-erasure/blob/master/src/lib.rs) makes field order, unique element enumeration, equal-length arithmetic buffers, and initialized-versus-missing shards part of the API contract. It states that corrupt-shard detection must be supplied separately.
- **C2:** `Field` supports multiple finite fields, while `ReconstructShard` abstracts both optional owned buffers and supplied buffers with validity flags. GF(256), GF(65536), `no_std`, and shard-by-shard operation demonstrate substantive generalization beyond a mechanical port. See the [repository usage and implementation notes](https://github.com/rust-rse/reed-solomon-erasure#readme).

Entry point: `src/lib.rs`, then its linked `core`, `matrix`, and field modules. The maintenance caveat is material for adoption.

### 10. [NicolasT/reedsolomon](https://github.com/NicolasT/reedsolomon)

**Haskell with C/assembly SIMD kernels; historical language port, last recorded push January 2017.** GitHub marks this as a fork of the Go library, but it contains a substantive Haskell implementation and distinct backend code. It is included for those differences.

- **C1:** The literate [core implementation](https://github.com/NicolasT/reedsolomon/blob/master/src/Data/ReedSolomon.lhs) expresses missing shards with `Maybe`, checks dimensions before reconstruction, and confines mutable-vector recovery work to `ST` before returning immutable results.
- **C2:** The small [Backend abstraction](https://github.com/NicolasT/reedsolomon/blob/master/src/Data/ReedSolomon/Backend.hs) supplies field multiply and multiply-XOR over storable vectors. The codec takes a backend polymorphic in the state thread, separating mutation and arithmetic strategy.

Study the translation of an imperative codec into a functional API with controlled mutation. Entry points: `Data/ReedSolomon.lhs` and `Data/ReedSolomon/Backend.hs`. The literate source also retains its Go antecedent for comparison.

### 11. [catid/cm256](https://github.com/catid/cm256)

**C++ implementation with C API; bounded-size Cauchy MDS block coding.** A smaller design than Leopard or Wirehair, built around indexed equal-sized blocks that may arrive out of order. Recorded last push: October 2024; the README still contains historical build guidance.

- **C1:** The [API header](https://github.com/catid/cm256/blob/master/include/cm256.h) specifies block-index ranges, encoder identity, shared parameters, and in-place replacement of recovery blocks. The single-block encoding function deliberately does not validate inputs.
- **C3:** The [implementation](https://github.com/catid/cm256/blob/master/src/cm256.cpp) explains its scaled Cauchy construction and why making the first recovery row all ones yields an XOR-only fast path without losing the required rank properties.

Entry points: `include/cm256.h` and `src/cm256.cpp`. Particularly useful for studying how an algebraic choice simplifies common recovery cases without adding a large framework.

### 12. [vivint/infectious](https://github.com/vivint/infectious)

**Go; Reed–Solomon erasure recovery plus error correction.** Unlike erasure-only shard codecs, it can use extra shares to correct corruption through Berlekamp–Welch. Recorded last push: October 2023.

- **C1:** The [correction implementation](https://github.com/vivint/infectious/blob/master/berlekamp_welch.go) first checks syndromes, solves a finite-field constraint system when needed, and rejects a nonzero polynomial-division remainder. It also makes mutation and reordering of the supplied shares explicit.
- **C2:** [fec.go](https://github.com/vivint/infectious/blob/master/fec.go) separates reusable code parameters, whole-input and single-share encoding, callback-driven reconstruction, and share ownership. `Decode`, `Correct`, and `Rebuild` support different caller requirements rather than hiding all work in one operation.

Entry points: `fec.go` and `berlekamp_welch.go`. The documentation's reused-buffer warning is an important part of understanding the interface, and error correction should not be confused with authentication.

### 13. [ArashPartow/schifra](https://github.com/ArashPartow/schifra)

**C++; configurable Reed–Solomon error/erasure codecs with an erasure-channel layer. Historical GitHub snapshot; recorded last push January 2020.** Included specifically because it implements erasure-channel coding, not merely because it contains generic error correction.

- **C1:** The [erasure-channel implementation](https://github.com/ArashPartow/schifra/blob/master/schifra_erasure_channel.hpp) maps lost interleaved rows to erasure locations, computes locator roots and correction values, and rejects a zero denominator. It states uniqueness, range, and uncorrupted-survivor assumptions explicitly.
- **C2:** Templated block/FEC lengths, configurable finite fields, interleaving, and general-versus-erasure-specific decoders offer a different abstraction style from shard matrix libraries. The [repository overview](https://github.com/ArashPartow/schifra#readme) describes shortened, punctured, and product-code configurations.

Entry point: `schifra_erasure_channel.hpp`, with the repository's erasure-channel examples as usage context. Inspect the repository license when considering reuse; this report makes no claim that its advertised commercial/certified variants are the same as the inspected source.

## Transform-based large-block Reed–Solomon

### 14. [catid/leopard](https://github.com/catid/leopard)

**C/C++; systematic Reed–Solomon using finite-field transforms.** The inspected repository includes both the legacy API and Leopard2's context/codec/plan interface. Study how transform algorithms become reusable execution plans.

- **C1:** The [Leopard2 API guide](https://github.com/catid/leopard/blob/master/docs/leopard2_api.md) defines context/codec/plan lifetimes, concurrency with separate scratch and outputs, alias rejection, parameter validation, and GF16 odd-payload layouts.
- **C2:** Immutable codecs capture coding parameters; decode plans precompute work for an erasure pattern; execution uses caller-provided scratch. This separates setup cost from repeated recovery.
- **C3:** The [repository's decoder and backend discussion](https://github.com/catid/leopard#decoder-profiles) explains different low/high-rate transform paths and CPU-dispatched kernels. The API guide details truncated transforms, selective outputs, and compact tail staging.

Entry points: `docs/leopard2_api.md` and the repository's decoder/backend documentation. Compatibility is profile- and layout-dependent; the existence of a legacy API is not a blanket interoperability guarantee.

### 15. [AndersTrier/reed-solomon-simd](https://github.com/AndersTrier/reed-solomon-simd)

**Rust; GF(65536) transform-based erasure coding.** Descended from `reed-solomon-16` and Leopard, but independently structured around Rust engines, coding rates, and runtime architecture selection.

- **C1:** The [Engine contract](https://github.com/AndersTrier/reed-solomon-simd/blob/master/src/engine.rs) describes power-of-two transform sizes and exactly which truncated regions are valid after FFT/IFFT. These are subtle invariants for optimized interchangeable implementations.
- **C2:** Engines separate low-level transforms and arithmetic from coding-rate logic; the same interface has naive, portable optimized, AVX2, SSSE3, NEON, and automatic-dispatch implementations.
- **C3:** The [repository guide](https://github.com/AndersTrier/reed-solomon-simd#readme) discusses initialization overhead, workload-dependent performance, and larger tests excluded from the default test run. It also documents the shard-layout compatibility boundary introduced in version 3.

Entry points: `src/engine.rs` and its engine modules. A useful study in retaining a readable reference implementation alongside hardware-specific kernels.

### 16. [paritytech/reed-solomon-novelpoly](https://github.com/paritytech/reed-solomon-novelpoly)

**Rust workspace; novel-polynomial-basis coding, particularly parameterized for validator shard distribution.** Recorded last push: February 2024. The relevant library is the nested `reed-solomon-novelpoly` crate; the workspace also contains benchmark, fuzzing, and comparison tooling.

- **C1:** [CodeParams and reconstruction](https://github.com/paritytech/reed-solomon-novelpoly/blob/master/reed-solomon-novelpoly/src/novel_poly_basis/mod.rs) round requested counts to transform-compatible powers of two while preserving a coding-rate inequality. Recovery checks shard availability and equal lengths, and handles two-byte field symbols and output padding.
- **C3:** The same implementation evaluates the error-locator polynomial once for a shard-loss pattern and reuses it across symbol positions. The [repository overview](https://github.com/paritytech/reed-solomon-novelpoly#readme) candidly notes the fixed full-domain Walsh-transform cost at small sizes.

Entry points: `novel_poly_basis/mod.rs` and the [crate root's systematic/round-trip tests](https://github.com/paritytech/reed-solomon-novelpoly/blob/master/reed-solomon-novelpoly/src/lib.rs). Study parameter derivation as part of the algorithm, not just an input check.

## Fountain, sparse, network, and streaming codes

### 17. [catid/wirehair](https://github.com/catid/wirehair)

**C++ with C API; fountain erasure coding.** Study the additional state and compatibility requirements that arise when recovery packets are generated on demand and enough packets does not always mean immediate decodability.

- **C1:** The [codec implementation](https://github.com/catid/wirehair/blob/master/WirehairCodec.cpp) includes packet identity/fingerprint handling and process-local hashing used to complicate collision clustering. Its comments explicitly distinguish duplicate detection from message authentication.
- **C2:** The [V2 wire-profile specification](https://github.com/catid/wirehair/blob/master/V2_WIRE_PROFILE.md) separates canonical serialized equation identity from in-process objects and C ABI layout. It fixes field arithmetic, seed rules, packet mapping, and precode geometry so independent encoder/decoder instances agree.

The [repository overview](https://github.com/catid/wirehair#readme) documents the non-MDS recovery model and differing legacy/V2 behavior. Entry points: `WirehairCodec.cpp` and `V2_WIRE_PROFILE.md`. Versioned equation contracts are a substantial engineering topic beyond the fountain algorithm itself.

### 18. [cberner/raptorq](https://github.com/cberner/raptorq)

**Rust; RaptorQ implementation of RFC 6330, with Python bindings.** This is a useful codebase for following a complicated standard into a solver whose memory and row-selection behavior matter.

- **C1:** The author's [unofficial RFC errata and optimization notes](https://github.com/cberner/raptorq/blob/master/RFC6330_ERRATA.md) derive phase termination and binary/nonbinary row invariants. They are implementation reasoning, not asserted here to be IETF-approved errata.
- **C3:** The [inactivation solver](https://github.com/cberner/raptorq/blob/master/src/pi_solver.rs) maintains row-degree statistics, histograms, single-one rows, and connected-component information for row selection. These structures avoid repeatedly rediscovering matrix properties during elimination.

Entry points: `RFC6330_ERRATA.md` and `src/pi_solver.rs`. The repository also distinguishes its public API from benchmark-only exports, making internal optimization experiments easier to separate from compatibility commitments.

### 19. [LucaFulchir/libRaptorQ](https://github.com/LucaFulchir/libRaptorQ)

**C++11; RaptorQ with raw and RFC-oriented APIs, plus compiled C/C++ interfaces. Author-provided GitHub source mirror; historical snapshot with last recorded push December 2022.** The [README](https://github.com/LucaFulchir/libRaptorQ/blob/master/README.md) explicitly provides this GitHub checkout alongside its Fenrir main server, and describes a release-candidate state.

- **C1:** The [decoder](https://github.com/LucaFulchir/libRaptorQ/blob/master/src/RaptorQ/v1/Decoder.hpp) manages arriving repair symbols, padding, retry eligibility, concurrent decode attempts, cancellation, and source-symbol availability. These states make it more than a matrix-solver wrapper.
- **C2:** The source separates a raw decoder from RFC framing and iterator-facing APIs; the README documents matching header-only and compiled C++ APIs and a separate C interface.
- **C3:** Decoder construction branches on whether shared precomputation caching is enabled, exposing a concrete setup/memory tradeoff.

Entry points: the README's API map and `src/RaptorQ/v1/Decoder.hpp`. Its historic compatibility and platform warnings should be read before considering integration; mirror freshness beyond the inspected snapshot was not established.

### 20. [OpenFEC/OpenFEC](https://github.com/OpenFEC/OpenFEC)

**C; application-level FEC framework with Reed–Solomon, LDPC-Staircase, and other codecs. Older codebase; recorded last push November 2023.** Especially useful for comparing incremental sparse-code decoding with block-oriented RS behind one interface.

- **C1:** The [API contract](https://github.com/OpenFEC/OpenFEC/blob/master/src/lib_common/of_openfec_api.h) distinguishes insufficient decoding progress, recoverable errors, and fatal session errors. It also requires received symbol buffers to remain alive because the decoder does not copy them.
- **C2:** Generic session and parameter prefixes, codec IDs, decoded-symbol callbacks, incremental symbol submission, and finish-decoding operations support several code families without assuming identical decoder behavior.
- **C3:** The [LDPC-Staircase implementation](https://github.com/OpenFEC/OpenFEC/blob/master/src/lib_stable/ldpc_staircase/of_ldpc_staircase_api.c) manages sparse parity-check structures and per-equation bookkeeping. The API explains why sparse iterative decoding can begin as symbols arrive.

Entry points: `of_openfec_api.h` and `of_ldpc_staircase_api.c`. This is the coding project, unrelated to the similarly named election-data API.

### 21. [itzmeanjan/rlnc](https://github.com/itzmeanjan/rlnc)

**Rust; random linear network coding with intermediate-node recoding.** A newer implementation: GitHub records creation in 2025, so no multi-year C4 claim is made.

- **C1:** The [decoder](https://github.com/itzmeanjan/rlnc/blob/main/src/full/decoder.rs) distinguishes received packets from rank-increasing packets, rejects incorrect lengths, and validates the recovered padding/boundary format. Recovery completion depends on matrix rank, not a raw arrival count.
- **C2:** The [crate's architecture documentation](https://github.com/itzmeanjan/rlnc/blob/main/src/lib.rs) separates encoder, recoder, and decoder. A recoder combines already coded packets without first reconstructing the original, supporting different network topologies from endpoint-only FEC.

Entry points: `src/lib.rs` and `src/full/decoder.rs`. The implementation makes the distinction between useful and dependent equations particularly easy to study; its error checks do not amount to authenticated network coding.

### 22. [catid/siamese](https://github.com/catid/siamese)

**C++ with C API; streaming erasure coding and hybrid-ARQ support. Historical implementation; recorded last push November 2020.** Distinct from this author's block codecs: the protected packet set changes as a stream progresses.

- **C1:** The [API](https://github.com/catid/siamese/blob/master/siamese.h) defines packet-number wraparound, bounded in-flight state, duplicate/disabled results, acknowledgement ordering, and timing requirements for RTT estimation. It explicitly requires external serialization of API calls.
- **C3:** The [algorithm description](https://github.com/catid/siamese#how-siamese-works) explains reusable lane sums and structured XOR-heavy matrix operations. Reusing intermediate work across recovery packets reduces repeated encoding, while the documented dense-solver cost grows with losses.

Entry points: `siamese.h` and the README's algorithm explanation. It is intended for full reliable delivery and modest-loss workloads; its historical benchmark and recovery-probability figures are not reproduced as current comparative claims.

## Search coverage and limitations

Discovery used more than six distinct formulations, including storage-oriented RS/SIMD libraries; Go/Java/Haskell ports; Rust novel-polynomial and GF16 implementations; Cauchy and small-block codecs; RaptorQ/fountain libraries; LDPC; random linear network coding; local-repair and regenerating codes; CUDA/GPU coding; and C#/OCaml alternatives. Later searches added Gibraltar and Siamese, then increasingly returned existing families, close ports, applications, wrappers, or broader error-correction packages. Search results were used for discovery; retained claims were checked against opened repository pages/API metadata and additional source, API, or design material.

The selection deliberately retains different implementation scales: small inspectable codec cores, generic language-level libraries, low-level optimized kernels, and one storage-plugin subsystem. Related ancestry is disclosed for the Backblaze/Go/Haskell/Rust family and the Leopard-derived implementations. The Haskell repository is retained despite GitHub's fork flag because its language implementation and backend abstraction are substantial. The OpenStack and libRaptorQ GitHub mirrors are identified explicitly.

Important exclusions include PyECLib and other bindings where the underlying implementation is already represented; the Ceph Jerasure fork; `tetcoin/erase` and other close RS forks; extra ports that did not add enough architectural variety; benchmark-only projects such as `spcl/ec-perf`; storage/transport applications whose erasure coding is chiefly a dependency; and quantum-erasure or secure-data-deletion search false positives. GF-Complete is an important arithmetic dependency, but is not counted as a standalone erasure codec here. GPU application prototypes and proprietary accelerator SDK instructions were not substituted for an inspectable library implementation.

This is a curated selection rather than an exhaustive catalog. GPU coverage is historical, and the search did not establish an equally strong standalone GitHub library for every repair-code family or language. No dependencies were installed, candidate code executed, repositories cloned, or benchmarks independently reproduced. Performance criteria refer to inspected mechanisms and documented constraints, not cross-project speed rankings. Dates and maintenance caveats are research-time snapshots. Statements about what an engineer can learn, and the mapping from evidence to C1–C4, are grounded judgments rather than project guarantees.
