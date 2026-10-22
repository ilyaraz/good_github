# Storage integrity checking and data recovery tools

Research date: **2026-10-09**.

This selection covers 23 GitHub repositories implementing filesystem and volume consistency checks, damaged-media acquisition, file recovery, parity reconstruction, archival fixity, and storage-device verification. General backup systems, partition-management front ends, and generic cryptography libraries are outside the main scope. OpenZFS and The Sleuth Kit are included specifically for their checking and recovery subsystems, and each monorepo counts once. The linked implementation files and technical documents are suggested reading entry points.

Criteria legend:

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, damaged or adversarial inputs, and failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components serving multiple tools, formats, devices, or workflows.
- **C3 — Performance with structure:** explicit management of I/O, memory, computation, or parallelism within an understandable design.
- **C4 — Sustained evolution:** documented changes over years accompanied by compatibility work, testing, or complexity management.

Criteria judgments are grounded engineering assessments of the cited material, not claims that every component is exemplary. Repository identities, default branches, and archive flags were checked through GitHub pages or its public API. An unarchived flag is not treated as proof of active maintenance.

## Filesystem and volume consistency

### 1. [tytso/e2fsprogs](https://github.com/tytso/e2fsprogs)

**Language/role:** C; ext2/ext3/ext4 administration, with `e2fsck` as the relevant checker.

Study how a filesystem checker decomposes global consistency into passes and carries compact summaries between them. The first pass is especially instructive because its introductory comment states both its invariants and the information later passes require.

- **C1:** Pass 1 checks inode modes, size/block counts, and exclusive block ownership. It records duplicate allocations for a separate pass, alongside directory, extended-attribute reference-count, and encryption-policy information. These are interacting on-disk invariants, not merely checksum comparisons. See [`e2fsck/pass1.c`](https://github.com/tytso/e2fsprogs/blob/master/e2fsck/pass1.c).
- **C3:** The same implementation deliberately gathers bitmaps and directory-block information during the sequential inode scan so subsequent passes normally avoid rereading inode records. Its architecture makes the trade between retained state and disk I/O explicit.

### 2. [kdave/btrfs-progs](https://github.com/kdave/btrfs-progs)

**Language/role:** C; Btrfs userspace checking, rescue, and extraction tools.

This is a useful comparison between proving structural consistency and salvaging whatever a damaged filesystem still exposes.

- **C1:** `btrfs check` cross-checks shared-extent references, backreferences, missing extents, and directory/inode connectivity. Its handling of alternate metadata mirrors illustrates why a checker must understand redundancy and object relationships. See the [`btrfs-check` technical manual](https://github.com/kdave/btrfs-progs/blob/devel/Documentation/btrfs-check.rst).
- **C3:** That manual documents two materially different resource strategies: retain metadata in memory, or use `lowmem` and accept additional reads. It also explains the cost of quota-accounting backreference walks.

The separate [`btrfs-restore` manual](https://github.com/kdave/btrfs-progs/blob/devel/Documentation/btrfs-restore.rst) explains relaxed validation, alternate roots, and extraction without modifying the source image; recovered data can be incomplete or from an older version. That distinction is central to understanding the recovery subsystem.

### 3. [dosfstools/dosfstools](https://github.com/dosfstools/dosfstools)

**Language/role:** C; FAT utilities, principally `fsck.fat` for this category.

Study repair policy for a comparatively small filesystem whose real-world compatibility rules are considerably less simple than its basic allocation model.

- **C1:** The checker separates loops within one cluster chain from cross-links between files, tracks cluster ownership, and recursively checks directory entries. See [`src/check.c`](https://github.com/dosfstools/dosfstools/blob/master/src/check.c).
- **C4:** The [release history](https://github.com/dosfstools/dosfstools/blob/master/NEWS) spans releases from 2014 through 2021 and records concrete compatibility work: DOS codepages, Atari variants, Windows volume labels, legacy short-name behavior, reserved-field preservation, and overflow fixes for malformed filesystems.

The inspected NEWS file's latest release entry is 4.2 from 2021. This entry makes no claim of a current release cadence.

### 4. [exfatprogs/exfatprogs](https://github.com/exfatprogs/exfatprogs)

**Language/role:** C; exFAT utilities, including `fsck.exfat` and orphan-cluster recovery.

Study how a checker reconciles a cluster allocation bitmap, FAT chains, file lengths, and directory metadata rather than treating any one structure as authoritative.

- **C1:** [`fsck/fsck.c`](https://github.com/exfatprogs/exfatprogs/blob/master/fsck/fsck.c) detects already-allocated clusters, cyclic chains, bitmap disagreements, and invalid chain transitions. It distinguishes observed allocation from the bitmap stored on disk and implements truncation and recovery decisions around those differences.
- **C4:** [NEWS](https://github.com/exfatprogs/exfatprogs/blob/master/NEWS) documents evolution across 2021–2026, including Windows partition compatibility, recovery from short I/O completions, invalid sector-size handling, allocation-bitmap overflow fixes, and scan improvements for large unused directory tails. These are concrete examples of maintaining a repair tool across formats, platforms, and damaged inputs.

### 5. [device-mapper-utils/thin-provisioning-tools](https://github.com/device-mapper-utils/thin-provisioning-tools)

**Language/role:** Rust, with earlier C++ history; metadata checking, repair, dump, and restore for dm-thin, dm-cache, and dm-era.

The [project README](https://github.com/device-mapper-utils/thin-provisioning-tools/blob/main/README.md) identifies this as the new upstream location; the older `jthornber` repository is a mirror and is not counted separately. The recovery workflow can write repaired metadata to a different device or round-trip it through XML.

- **C1:** [`src/thin/check.rs`](https://github.com/device-mapper-utils/thin-provisioning-tools/blob/main/src/thin/check.rs) combines metadata checksums, parent/child key-range validation, mapping summaries, and allocation accounting. Shared subtrees make reference accounting more subtle than a simple tree traversal.
- **C2:** [`src/pdata/btree_walker.rs`](https://github.com/device-mapper-utils/thin-provisioning-tools/blob/main/src/pdata/btree_walker.rs) defines a generic visitor, an I/O-engine boundary, shared space maps, and aggregated traversal errors. Its `visit_again` hook preserves information about shared nodes while avoiding repeated I/O. This is a substantial reusable core beneath several metadata tools.

### 6. [openzfs/zfs](https://github.com/openzfs/zfs)

**Language/role:** C; the relevant subsystem is pool scrubbing and resilvering, not the entire filesystem.

The [`zpool scrub` manual](https://github.com/openzfs/zfs/blob/master/man/man8/zpool-scrub.8) establishes category fit: it verifies block checksums and can repair corruption using redundant copies.

- **C1:** The scan implementation must remain correct while blocks are freed and while work is checkpointed. Its design commentary describes removing freed blocks from queued reads and draining outstanding sorted I/O before persisting a logical checkpoint. See [`module/zfs/dsl_scan.c`](https://github.com/openzfs/zfs/blob/master/module/zfs/dsl_scan.c).
- **C3:** That file explains the scheduling architecture: traverse metadata in logical order, reorder data reads into physical-address order, cap queue memory, and alternate metadata discovery with queue draining. It is an unusually clear study of performance constraints shaping recovery machinery.

## Damaged-media acquisition and file recovery

### 7. [ISpillMyDrink/OpenSuperClone](https://github.com/ISpillMyDrink/OpenSuperClone)

**Language/role:** C; Linux damaged-drive imaging and targeted acquisition, derived from HDDSuperClone.

Study how recovery changes when repeated reads can be expensive or harmful to a failing source. This is a substantive continuation: the repository documents driver, recovery-setting, localization, and interface changes beyond repackaging its predecessor.

- **C1:** The [recovery-phase design](https://github.com/ISpillMyDrink/OpenSuperClone/wiki/Recovery-Phases) distinguishes forward/backward passes, error-based and speed-based skipping, trimming, scraping, and retries. Failed ranges change state as the algorithm narrows them to individual sectors.
- **C2:** [Virtual Disk Mode](https://github.com/ISpillMyDrink/OpenSuperClone/wiki/Virtual-Disk-Mode) exposes the recovery session as a block device usable by other recovery applications. Reads acquire missing source data into the destination; repeated reads use the destination image. This abstraction separates filesystem-level selection from physical acquisition.

The wiki explicitly has incomplete areas; these two pages contain useful operational design material, but should not be mistaken for a complete architecture specification.

### 8. [cgsecurity/testdisk](https://github.com/cgsecurity/testdisk)

**Language/role:** Primarily C, with C++ GUI components; TestDisk partition recovery and PhotoRec file carving, counted together.

Study the boundary between filesystem-aware recovery and signature-based extraction. The repository includes both families, while PhotoRec's developer notes make its extension model particularly approachable.

- **C1:** The [PhotoRec theory of operation](https://github.com/cgsecurity/testdisk/blob/master/README_dev_photorec.txt) describes multiple passes, inferred block size, optional brute-force recovery, finalization, and abort handling when interrupted or when the destination fills. Correctness depends on state transitions and partial results, not just finding a magic byte sequence.
- **C2:** [`src/filegen.h`](https://github.com/cgsecurity/testdisk/blob/master/src/filegen.h) separates format hints, header registration, ongoing data validation, final file checks, and renaming callbacks. These contracts let format-specific carvers share the scanning and recovery machinery.

### 9. [sleuthkit/sleuthkit](https://github.com/sleuthkit/sleuthkit)

**Language/role:** C/C++; filesystem/image analysis library and command-line tools, specifically `tsk_recover` and its supporting filesystem API.

Study recovery built on filesystem interpretation rather than solely on byte signatures. The relevant command can select allocated, unallocated, or all files and exports their content through the library's walkers.

- **C1:** [`tools/autotools/tsk_recover.cpp`](https://github.com/sleuthkit/sleuthkit/blob/develop-4.1x/tools/autotools/tsk_recover.cpp) handles output-path length limits, control characters, traversal-like path components, and read/write failures. These show the additional correctness burden of turning names and metadata from a damaged or untrusted image into host files.
- **C2:** [`tsk/fs/tsk_fs.h`](https://github.com/sleuthkit/sleuthkit/blob/develop-4.1x/tsk/fs/tsk_fs.h) exposes common filesystem, file, attribute-run, block, and callback abstractions, including sparse and missing runs. `TskRecover` layers recovery policy on `TskAuto` and file-walk callbacks instead of implementing each filesystem again.

### 10. [sleuthkit/scalpel](https://github.com/sleuthkit/scalpel)

**Language/role:** C++; configurable file carver and indexing engine. **Historical/unmaintained:** its [README](https://github.com/sleuthkit/scalpel/blob/master/README) explicitly says active maintenance stopped and describes abandoned integration work after memory leaks were encountered.

Retain this as a study of high-throughput carving architecture, with that limitation visible.

- **C1:** [`src/dig.cpp`](https://github.com/sleuthkit/scalpel/blob/master/src/dig.cpp) coordinates the reader, pattern-search workers, buffer ownership, and completion state. Concurrent chunk processing and overlapping header/footer matches create substantial correctness obligations; inclusion is not a claim that the historical implementation satisfies all of them without defects.
- **C3:** The same engine uses full/empty buffer queues to overlap disk reads with CPU work. The README documents multithreading, asynchronous I/O, and different matching capabilities for its CPU and historical GPU modes, making the throughput architecture and its compromises inspectable.

### 11. [samueltardieu/recoverjpeg](https://github.com/samueltardieu/recoverjpeg)

**Language/role:** C and C++; focused JPEG and MOV salvage from disk images or devices.

A smaller codebase worth reading beside the large multi-format carvers. Its narrow scope makes the limits of structural recovery easy to see.

- **C1:** [`src/recoverjpeg.c`](https://github.com/samueltardieu/recoverjpeg/blob/master/src/recoverjpeg.c) parses JPEG markers and segment lengths, distinguishes escaped bytes and restart markers, and rejects oversized candidates. It illustrates why plausible structure is weaker evidence than correct image content.
- **C3:** The [recoverjpeg manual](https://github.com/samueltardieu/recoverjpeg/blob/master/doc/recoverjpeg.md) explicitly trades scan alignment against work, and read-buffer size against memory and system-call overhead. It also describes resume offsets and directory splitting for filesystems with directory-size limits.

The manual states that this is not a complete JPEG parser and that structurally valid recovered pictures can remain corrupted.

## Parity, error correction, and recoverable archive formats

### 12. [amadvance/snapraid](https://github.com/amadvance/snapraid)

**Language/role:** C; snapshot-style parity protection, scrubbing, and recovery for arrays of ordinary files.

Study recovery whose reference point is the last synchronization. The [manual](https://github.com/amadvance/snapraid/blob/master/doc/snapraid.1) distinguishes `scrub`, `check`, and `fix`, including the fact that `fix` restores the recorded state and cannot infer whether a difference was intentional.

- **C1:** Recovery combines saved file hashes with parity algebra. The [`raid/raid.h` contract](https://github.com/amadvance/snapraid/blob/master/raid/raid.h) explains that finite-field polynomials, generators, coefficients, and parity data must agree; incompatible modes cannot be mixed. It also states initialization and mode-changing concurrency restrictions.
- **C3:** The same interface documents Cauchy and Vandermonde modes and CPU-specific arithmetic backends, including GFNI, AVX, and NEON paths. Separating the parity engine from file-state and command logic provides a concrete way to study optimized arithmetic without losing the larger recovery model.

### 13. [Parchive/par2cmdline](https://github.com/Parchive/par2cmdline)

**Language/role:** C++; official PAR2 creation, verification, and repair implementation, including libpar2.

Study repair as a pipeline that must first discover usable blocks, decide whether recovery is possible, reconstruct missing data, and verify the result.

- **C1:** [`src/par2repairer.cpp`](https://github.com/Parchive/par2cmdline/blob/master/src/par2repairer.cpp) separates source verification, available/missing block accounting, matrix construction, reconstruction, cancellation, and target reverification. Failure paths remove incomplete target files in several reconstruction stages.
- **C3:** Its buffer allocator chooses chunk sizes from the memory budget and missing-block count, allowing reconstruction to proceed in pieces. File verification has separate thread controls and synchronization. The reusable [`ReedSolomon` interface](https://github.com/Parchive/par2cmdline/blob/master/src/reedsolomon.h) keeps matrix construction and block processing distinct from file discovery and I/O.

### 14. [Yutaka-Sawada/MultiPar](https://github.com/Yutaka-Sawada/MultiPar)

**Language/role:** C; Windows Parchive tooling. The study target is the available `source/par2j` verification and repair engine, not an assumption that every distributed GUI component is present as source.

This is a distinct implementation alongside par2cmdline, with extensive Windows and hardware-specific engineering.

- **C1:** [`source/par2j/verify.c`](https://github.com/Yutaka-Sawada/MultiPar/blob/master/source/par2j/verify.c) implements block discovery and checksum-based matching, including multiple candidate blocks sharing a CRC and handling read errors. Recovery must identify original slices inside incomplete or displaced data before decoding can help.
- **C3:** [`source/par2j/reedsolomon.c`](https://github.com/Yutaka-Sawada/MultiPar/blob/master/source/par2j/reedsolomon.c) contains explicit cache-block sizing, aligned chunk selection, thread-count decisions, matrix-inversion workers, and OpenCL integration. It is useful for studying how a single recovery algorithm is mapped to CPU caches, threads, and accelerators.

### 15. [speed47/dvdisaster](https://github.com/speed47/dvdisaster)

**Language/role:** C; optical-image error correction and recovery. **Unofficial continuation**, explicitly identified by its [README](https://github.com/speed47/dvdisaster/blob/master/README.md), with substantive platform, GUI, adaptive-reading, and recovery changes; it is not presented as an official mirror.

- **C1:** The [RS03 codec specification](https://github.com/speed47/dvdisaster/blob/master/documentation/codec-specs/rs03.tex) explains how data, CRC, and parity layers spread codewords across the medium, and how the recovery information itself is protected. This connects error-correction layout to physical damage patterns and metadata survivability.
- **C4:** The [changelog](https://github.com/speed47/dvdisaster/blob/master/CHANGELOG) records multi-year evolution, including Windows memory-mapped I/O corruption fixes, GTK3 migration, recovery of images whose custom redundancy size was forgotten, and adaptive-scanning regression fixes. The README states an upstream-format compatibility goal backed by regression tests.

No throughput multipliers from the project's promotional comparisons are adopted here.

### 16. [MarcoPon/SeqBox](https://github.com/MarcoPon/SeqBox)

**Language/role:** Python; a recoverable single-file container and raw-media scanning/reassembly tools.

Study a format that makes a file recognizable after filesystem metadata disappears. It requires encoding data into SeqBox beforehand; it is not a universal undelete tool.

- **C1:** The [format explanation](https://github.com/MarcoPon/SeqBox/blob/master/README.md) describes independently recognizable blocks carrying a file identifier, sequence number, version, and checksum. Recovery validates blocks and reassembles fragmented data by identity and sequence, potentially using good blocks from multiple copies.
- **C3:** [`sbxscan.py`](https://github.com/MarcoPon/SeqBox/blob/master/sbxscan.py) scans with configurable steps and buffering, persists source positions and block metadata in SQLite, and batches commits. This keeps scanning and reconstruction separate and avoids making the recovered payload itself an in-memory index.

SeqBox's block recovery should be distinguished from an erasure code that reconstructs missing bytes; the next project adds that capability in a separate implementation.

### 17. [darrenldl/blockyarchive](https://github.com/darrenldl/blockyarchive)

**Language/role:** Rust; `blkar`, implementing SeqBox and error-correcting EC-SeqBox. **Archived by the owner in June 2022**; retained for its implementation and specifications, not as an actively maintained recommendation.

This is more than a duplicate of SeqBox: it adds Reed–Solomon shards, burst-error interleaving, and a concurrent engine.

- **C1:** [`SBX_FORMAT.md`](https://github.com/darrenldl/blockyarchive/blob/master/SBX_FORMAT.md) specifies metadata/data/parity roles, sequence-number rules, and block-set interleaving. The key engineering problem is preserving recoverability when consecutive sectors disappear, including sectors that carry recovery metadata.
- **C3:** [`src/encode_core.rs`](https://github.com/darrenldl/blockyarchive/blob/master/src/encode_core.rs) constructs bounded channels connecting reader, encoder, and writer stages, circulates reusable data buffers, and propagates stage errors. It provides a concrete example of bounded parallelism in an archival tool.

### 18. [lrq3000/pyFileFixity](https://github.com/lrq3000/pyFileFixity)

**Language/role:** Python; archival fixity checking, header protection, adaptive error correction, and repair tools.

Study selective protection: file headers and metadata can receive more redundancy than less critical portions of a file. The value here is the inspectable policy and codec integration, rather than a throughput claim.

- **C1:** [`structural_adaptive_ecc.py`](https://github.com/lrq3000/pyFileFixity/blob/master/pyFileFixity/structural_adaptive_ecc.py) manages variable protection rates, encoded metadata fields, and blockwise hashes/ECC. The format records software-version information to aid future recovery, acknowledging that decoding parameters are part of the preservation problem.
- **C2:** [`lib/eccman.py`](https://github.com/lrq3000/pyFileFixity/blob/master/pyFileFixity/lib/eccman.py) provides an `ECCMan` facade over codec implementations, parameter calculation, and Reed–Solomon parameter detection from a known sample. Shared codec and hashing interfaces underpin several protection workflows.

## Device verification and file-integrity auditing

### 19. [AltraMayor/f3](https://github.com/AltraMayor/f3)

**Language/role:** C; flash-capacity fraud detection and write/read verification.

Study testing against devices that acknowledge writes while aliasing addresses or retaining only cached data. This is a storage-integrity checker with a deliberately adversarial device model.

- **C1:** [`src/libprobe.c`](https://github.com/AltraMayor/f3/blob/master/src/libprobe.c) explains why sequential and random reads can disagree on fake drives and structures probing to account for that behavior. Position-dependent data, cache handling, alignment, and I/O errors all matter to avoiding false confidence.
- **C2:** [`src/libdevs.h`](https://github.com/AltraMayor/f3/blob/master/src/libdevs.h) defines an abstract device, file-backed devices with configurable real/announced sizes and cache behavior, reset operations, and performance/safety wrappers. These abstractions make probing logic reusable and unusual device behaviors reproducible without tying everything to one hardware path.

### 20. [smartmontools/smartmontools](https://github.com/smartmontools/smartmontools)

**Language/role:** C++; `smartctl` and `smartd` for device health, self-tests, and storage error reporting. The repository identifies itself as the **official upstream since June 2025**, rather than its former mirror role.

This covers device diagnostics adjacent to content verification: SMART results do not establish that every stored file matches an expected checksum.

- **C2:** [`include/smartmon/dev_interface.h`](https://github.com/smartmontools/smartmontools/blob/main/include/smartmon/dev_interface.h) defines shared device lifecycle, error reporting, ATA/SCSI/NVMe interfaces, autodetection, and ownership for tunneled devices. It is a substantial portability layer across OS and transport boundaries.
- **C4:** The [preserved release history](https://github.com/smartmontools/smartmontools/blob/main/doc/old/NEWS-5.0-7.5.txt) spans 2004–2025 and records protocol, bridge, namespace, and compatibility fixes. Examples include SCSI bounds checks, corrected NVMe self-tests, USB reset behavior, and reproducible release builds.

### 21. [rfjakob/cshatag](https://github.com/rfjakob/cshatag)

**Language/role:** Go, previously C; silent-corruption detection using SHA-256 and timestamps stored in extended attributes.

A compact but substantive study of integrity decisions at the boundary between file content, metadata, and concurrent modification.

- **C1:** [`check.go`](https://github.com/rfjakob/cshatag/blob/master/check.go) reads modification time before and after hashing, rejects a detected mid-read change, validates stored attributes, and explicitly accommodates SMB timestamp precision. These checks expose why a checksum utility still needs filesystem semantics.
- **C4:** The [2012–2024 changelog](https://github.com/rfjakob/cshatag/blob/master/CHANGELOG.md) documents the C-to-Go rewrite, tests and CI, macOS/SMB compatibility, and the later behavior change that preserves a corruption baseline unless `-fix` is requested. Here `-fix` updates the stored checksum; it does not reconstruct damaged file content.

### 22. [rhash/RHash](https://github.com/rhash/RHash)

**Language/role:** C; checksum-file verification and a reusable multi-algorithm hashing library.

Study how a general integrity checker separates digest computation from manifest parsing, file traversal, and output conventions. The repository's canonical owner capitalization was verified as `rhash`.

- **C2:** [`librhash/rhash.h`](https://github.com/rhash/RHash/blob/master/librhash/rhash.h) provides high-level file hashing and incremental contexts, multiple digests over one input stream, explicit lifecycle operations, and context reuse. This is a library boundary usable independently of the command-line verifier.
- **C4:** The [changelog](https://github.com/rhash/RHash/blob/master/ChangeLog) documents years of platform and format evolution, including special-character filename escaping, large-file support on 32-bit targets, older libc/Windows compatibility, OpenSSL integration, and explicit soname changes for an API break. These are relevant to long-lived checksum manifests and consumers.

### 23. [jessek/hashdeep](https://github.com/jessek/hashdeep)

**Language/role:** C/C++; recursive multi-hash generation, matching, and file-set auditing.

Study the difference between checking individual digests and checking that a collection corresponds to its recorded inventory. The README describes audit failure for missing, new, or conflicting entries; this entry does not infer active maintenance from repository availability.

- **C1:** [`src/hashlist.cpp`](https://github.com/jessek/hashdeep/blob/master/src/hashlist.cpp) distinguishes no match, partial digest agreement, size mismatch, and filename mismatch. It checks other available digest algorithms after finding an initial match, making the matching semantics explicit rather than treating the first matching checksum as sufficient.
- **C3:** [`src/threadpool.cpp`](https://github.com/jessek/hashdeep/blob/master/src/threadpool.cpp) documents and implements a fixed worker pool with a work queue, mutex, and separate condition variables for the producer and workers. It gives an approachable concurrency model for processing large file inventories without spawning an unbounded worker per file.

## Coverage and search notes

Discovery used more than six distinct live-web search formulations, including filesystem `fsck`/repair tools; damaged-drive imaging and ddrescue alternatives; file carving and photo recovery; parity archives and SnapRAID; bit-rot/xattr/fixity tools; device-mapper metadata repair; Rust recoverable containers; optical-disc ECC; SMART/flash-fraud testing; and APFS/NTFS/XFS-related recovery searches. Follow-up queries resolved ownership and provenance, notably recoverjpeg's owner, the thin-provisioning-tools move, and smartmontools' transition from mirror to upstream.

Primary review combined opened GitHub repository pages, public API metadata and source trees, and direct reads of selected implementation files, format specifications, manuals, and changelogs. Every retained repository has implementation-level or architectural evidence beyond a feature list. Later searches predominantly repeated existing candidates or surfaced wrappers, tutorials, broad partition front ends, and unrelated storage engines, giving diminishing returns for this scope.

Important boundaries and limitations:

- **GitHub coverage is not ecosystem completeness.** GNU ddrescue was discovered and investigated, but no official substantive GitHub mirror was established in this search, so unofficial mirrors and wrappers were not substituted for it. Likewise, this report does not purport to cover every XFS, F2FS, NTFS, APFS, or proprietary recovery implementation.
- **Related implementations are distinguished, not double-counted.** TestDisk/PhotoRec and the OpenZFS subsystem each count once; the old thin-provisioning-tools location is omitted. SeqBox and blockyarchive have different implementations and repair capabilities. The dvdisaster continuation is included because its primary sources establish independent evolution, with its unofficial status explicit.
- **Preservation format tools need prior preparation.** PAR2, SeqBox, EC-SeqBox, optical ECC, and checksum baselines address different failure models from unprepared-media carving or damaged-drive acquisition. Device-health monitoring is also distinct from end-to-end content verification.
- **This was source research, not execution or certification.** No candidate code was run, dependencies installed, large repositories cloned, or recovery effectiveness benchmarked. Sources on default branches can change. Historical and archived projects remain useful study material, but their inclusion is not a blanket operational endorsement.
