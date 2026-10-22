# Deduplicating backup and archival systems

Research date: **2026-10-09**.

This report selects **24 GitHub repositories** implementing deduplicated backups, versioned archives, or storage engines directly useful for those workloads. It covers content-defined chunks, fixed-block image backups, whole-file sharing, compressed mountable archives, and research systems. Distribution-oriented projects are included only where their archive and shared-chunk formats provide a substantive archival design to study. This is a code-reading selection guide, not a deployment recommendation or a claim that every component is exemplary.

Criteria used below:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial input, metadata semantics, or recovery from failures.
- **C2 — Abstractions:** substantial reusable interfaces or data models supporting multiple operations, backends, or workloads.
- **C3 — Performance:** concrete resource constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or explicit complexity management.

## General-purpose encrypted backup repositories

### 1. [restic/restic](https://github.com/restic/restic)

**Go; encrypted filesystem snapshots over local and remote object stores.** A particularly useful starting point for understanding the separation between plaintext content identity, encrypted storage identity, pack files, indexes, and snapshot trees.

- **C1:** Repository objects are immutable and must become visible atomically. Exclusive and nonexclusive locks coordinate operations; deterministic tree serialization preserves deduplication. Independently authenticated blobs and pack headers let readers validate data and reconstruct indexes. These invariants are specified in the [repository design reference](https://restic.readthedocs.io/en/stable/100_references.html).
- **C3:** Packing small blobs amortizes storage operations; placing the header at the end permits streaming writes and header-only indexing. This connects the format directly to cloud latency and memory constraints, rather than merely asserting speed.
- **C4:** The [changelog](https://github.com/restic/restic/blob/master/CHANGELOG.md) documents releases from 2017 through 2026, including format evolution, platform fixes, and restoration of accidentally changed command behavior.

**Entry points:** the design reference and changelog above.

### 2. [borgbackup/borg](https://github.com/borgbackup/borg)

**Python, Cython, and C; deduplicating archiver with local and remote repositories.** Study the stable 1.x storage engine separately from the substantially different Borg 2 development branch. The repository README explicitly identifies `master` as unstable Borg 2 beta.

- **C1:** In the stable design, an append-only log records `PUT`, `DELETE`, and `COMMIT`; reopening discards uncommitted operations. Indexes and hints can be regenerated, and compaction validates that old segments contain no live objects before deleting them. See [stable data structures and file formats](https://borgbackup.readthedocs.io/en/stable/internals/data-structures.html).
- **C3:** Compaction tracks sparse bytes per segment to avoid scanning every segment. Chunk indexes and local caches expose the memory costs of global deduplication.
- **C2:** Archives, item metadata, and data chunks form an object graph over a lower-level repository. The [Borg 2 data-structure document](https://github.com/borgbackup/borg/blob/master/docs/internals/data-structures.rst) provides a useful comparison: packed objects, immutable index fragments, and authenticated repository metadata.

**Entry points:** the version-specific documents above; do not apply Borg 1 segment-format details to Borg 2.

### 3. [kopia/kopia](https://github.com/kopia/kopia)

**Go; encrypted snapshot system with filesystem and cloud backends.** Its layered storage model is especially useful for engineers building reusable storage libraries.

- **C2:** The [architecture document](https://github.com/kopia/kopia/blob/master/site/content/docs/Advanced/Architecture/_index.md) separates generic blob storage, content-addressed blocks, arbitrarily large objects, and label-addressable manifests. Snapshots and policies can share infrastructure without forcing every caller to manipulate chunk hashes.
- **C3:** Small blocks are aggregated into packs, indexes resolve block IDs to byte ranges, and caching addresses high-latency storage. Large files and directory listings use indirect objects rather than requiring one giant block.
- **C1:** Pack-local indexes provide a recovery path when the global index is damaged; data and metadata packs have distinct roles.

**Entry point:** the architecture document above, which also links the corresponding Go APIs.

### 4. [gilbertchen/duplicacy](https://github.com/gilbertchen/duplicacy)

**Go; cloud backup with cross-client chunk sharing.** Study a design that deliberately avoids a centralized chunk-location database, and the deletion protocol that this choice requires.

- **C1:** [Lock-Free Deduplication](https://github.com/gilbertchen/duplicacy/wiki/Lock-Free-Deduplication) explains why an apparently unreferenced chunk may still be needed by an unfinished backup. Its two-stage fossil process separates renaming from final deletion and gives backup and restore operations different rules for accessing fossils.
- **C2:** Content-derived filenames turn a small set of storage operations into a common backup substrate. Multiple clients can reuse chunks without directly coordinating with one another.
- **C3:** The design exchanges pack-index management for individual chunk lookups. This is a concrete architecture to compare with restic and Kopia, rather than a universal performance advantage.

**Entry point:** the linked design wiki, including its completion conditions for fossil deletion. Licensing should be evaluated separately from technical suitability.

### 5. [duplicati/duplicati](https://github.com/duplicati/duplicati)

**C#; encrypted block-deduplicating backups with a local database and remote volumes.** The backup pipeline makes the coordination between database state, worker completion, archive construction, and uploads unusually visible.

- **C1:** [`DataBlockProcessor`](https://github.com/duplicati/duplicati/blob/master/Duplicati/Library/Main/Operation/Backup/DataBlockProcessor.cs) explicitly handles two workers discovering the same absent block through an atomic database insertion. It also completes waiting senders on exceptions and records volume state before committing and starting an upload.
- **C3:** Channel-connected stages aggregate new blocks into bounded volumes. Partial volumes flow into a spill collector, and CPU-intensity controls throttle processing. These are practical throughput and resource-management mechanisms.
- **C2:** The same block-processing stage communicates through a backup database, channel bundle, and backend-manager interface, separating deduplication from the particular remote service.

**Entry point:** the processor implementation above; the surrounding `Operation/Backup` directory exposes the adjacent stages.

### 6. [rustic-rs/rustic_core](https://github.com/rustic-rs/rustic_core)

**Rust; reusable backup engine implementing the restic repository format.** This entry covers the core/backend/config workspace, rather than separately counting the Rustic CLI. It is a distinct implementation, not a restic fork. The README warns that its library API remains subject to change.

- **C2:** [`Repository`](https://github.com/rustic-rs/rustic_core/blob/main/crates/core/src/repository.rs) exposes repository states and operations over backend abstractions, including cached, decrypted, and hot/cold storage access. Backup, restore, repair, and prune share this engine.
- **C3:** `to_indexed_ids()` retains only data-blob IDs while keeping fuller tree information, reducing memory for operations that add data. `to_indexed()` retains the full index for operations needing locations. This is an explicit capability-versus-memory tradeoff.
- **C1:** Checked index-loading variants inspect pack headers missing from indexes, providing a concrete route from inconsistent indexing to reconstructed state.

**Entry point:** `repository.rs` above; the repository README supplies executable API examples and the compatibility scope.

## Stream-oriented backups and public-key designs

### 7. [bup/bup](https://github.com/bup/bup)

**Python and C; backups using Git-compatible objects and pack files.** Useful for studying how a version-control representation can be adapted to huge files and detailed filesystem metadata.

- **C3:** The [design guide](https://github.com/bup/bup/blob/main/DESIGN.md) explains content-defined hashsplitting into blobs and trees, avoiding whole-file delta processing for large inputs. It also describes the source boundary between Python orchestration and speed-sensitive C code.
- **C1:** Filesystem paths are handled as byte sequences, and the launcher deliberately preserves arguments that Python's ordinary startup could mishandle. Metadata preservation is treated as a separate problem from Git's content representation.
- **C2:** The same repository supports native filesystem backup, stream splitting, restoration, and filesystem-style browsing through a common object model.

**Entry point:** the design guide above; its historical explanations should be read alongside current code, not as benchmark results.

### 8. [andrewchambers/bupstash](https://github.com/andrewchambers/bupstash)

**Rust; encrypted stream and directory backups with offline decryption keys.** The README labels it beta and recommends redundant backups. GitHub metadata reported its last push in February 2024; recent maintenance is not assumed.

- **C1:** The [technical overview](https://github.com/andrewchambers/bupstash/blob/master/doc/technical_overview.md) separates encrypted leaves from a mostly unencrypted Merkle-tree structure, enabling server-side traversal and garbage collection without decryption keys. Partially concurrent collection must invalidate client caches correctly.
- **C3:** A client SQLite send log avoids retransmitting known chunks, stat caching skips repeated compression/encryption, and tree breadcrumbs support random access. The server can stream tree contents to reduce round trips.
- **C2:** An optional auxiliary content-index stream adds file browsing and partial retrieval to the generic stream model.

**Entry points:** technical overview; [repository status metadata](https://api.github.com/repos/andrewchambers/bupstash).

### 9. [dpc/rdedup](https://github.com/dpc/rdedup)

**Rust; embeddable stream-deduplication engine with optional public-key encryption.** Usually paired with tar or rdup for filesystem traversal. The README identifies missing/incomplete cloud integrations; the API reports a last push in August 2022, so this is also a historical architecture study.

- **C2:** The library separates chunking, hashing, compression, encryption, and asynchronous backend work. The [chunk processor](https://github.com/dpc/rdedup/blob/master/lib/src/chunk_processor.rs) accepts these components explicitly rather than hardwiring one codec pipeline.
- **C1:** The processor rechecks the newest generation when concurrent work may have moved a chunk. The [local backend](https://github.com/dpc/rdedup/blob/master/lib/src/aio/local.rs) implements temporary-file writes, data synchronization, rename publication, and shared/exclusive locking.
- **C3:** Workers communicate by channels and reuse existing chunks before compression and encryption, making the concurrency and avoided work inspectable.

**Entry points:** chunk processor and local backend above. The durability mechanisms are evidence of design intent, not a claim of proven crash safety on every filesystem.

### 10. [Tarsnap/tarsnap](https://github.com/Tarsnap/tarsnap)

**C; command-line client for the Tarsnap hosted backup service.** The repository contains the client, not the service's complete server implementation. Its README distinguishes development code from recommended official releases.

- **C1:** The [chunk-layer interface](https://github.com/Tarsnap/tarsnap/blob/master/tar/chunks/chunks.h) specifies transaction membership, checkpointing, missing-versus-corrupt read results, and reference-counted deletion. A chunk is removed only after its transaction references have been balanced by deletions.
- **C2:** Read, write, delete, statistics, and filesystem-check operations sit above a separate storage layer. This is a compact example of reusable internal abstractions with precise contracts.
- **C3:** Explicit read-cache requests and reuse of existing chunk references avoid redundant transfers; the API exposes compressed and uncompressed sizes separately.

**Entry points:** chunk interface and [chunk transaction implementation](https://github.com/Tarsnap/tarsnap/blob/master/tar/chunks/chunks_transaction.c).

### 11. [richfelker/bakelite](https://github.com/richfelker/bakelite)

**C; experimental incremental backup with public-key encryption and streamable storage.** The author explicitly reports limited testing, no third-party review, and potentially changing formats. Include it for its distinct data model, not maturity.

- **C1:** The README's data-model section distinguishes ciphertext-addressed Merkle objects from a private local index mapping plaintext hashes and inode identities to encrypted objects. This makes the tension between deduplication and an offline decryption key explicit, including what the local index leaks.
- **C3:** Backups can stream without local staging. Per-snapshot Bloom filters support storage-side identification of unreferenced objects without decrypting the object graph.
- **C2:** Independent snapshot roots share subtrees without parent chains, allowing retention decisions to be separated from incremental storage reuse.

**Entry points:** [data-model explanation](https://github.com/richfelker/bakelite/blob/main/README.md) and [`prune.c`](https://github.com/richfelker/bakelite/blob/main/prune.c), which checks filter-object hashes and emits candidate paths rather than deleting them itself.

### 12. [zbackup/zbackup](https://github.com/zbackup/zbackup)

**C++; format-agnostic deduplication of tar streams, dumps, and images.** A useful older design that matches rolling windows against existing blocks. GitHub metadata reports a June 2022 last push; continued maintenance is not inferred.

- **C1:** [`backup_creator.cc`](https://github.com/zbackup/zbackup/blob/master/backup_creator.cc) makes ring-buffer boundaries, partial final chunks, inline short literals, and chunk-reference emission explicit. It separates a rolling match from the stronger chunk-identity calculation.
- **C3:** [`chunk_storage.cc`](https://github.com/zbackup/zbackup/blob/master/chunk_storage.cc) groups chunks into bundles, bounds simultaneous compressors, waits for completion, and publishes bundles before their index. This is a readable producer/worker/storage pipeline.
- **C2:** Stream processing is independent of a filesystem traversal format; callers can supply archives or other byte streams.

**Entry points:** the two implementation files above. Its older cryptographic choices and in-memory index are study limitations, not recommendations for new designs.

## Deduplicating archives and reusable image formats

### 13. [fcorbelli/zpaqfranz](https://github.com/fcorbelli/zpaqfranz)

**C++; independently evolved ZPAQ 7.15 fork for versioned, deduplicating archives.** It warrants a separate entry because of its added recovery, verification, platform support, and sustained changes. The original ZPAQ mirror is not counted again.

- **C1:** Append-oriented archive updates, incomplete-transaction trimming, and extraction verification expose failure-sensitive archive semantics. The [autotest documentation](https://github.com/fcorbelli/zpaqfranz/blob/main/AUTOTEST/README.txt) describes decoding a known Windows-created archive on other architectures to detect PAQL execution and endianness problems.
- **C3:** The README discusses the cost of seeking among deduplicated fragments and memory-assisted extraction, as well as the listing cost of many historical versions. These are explicit consequences of the archive layout.
- **C4:** The [2021–2025 changelog](https://github.com/fcorbelli/zpaqfranz/blob/main/CHANGELOG.md) records ongoing compatibility and verification changes; the README explains retaining format compatibility despite listing-performance costs.

**Entry points:** autotest documentation and changelog above. No advertised throughput figures are adopted here.

### 14. [mhx/dwarfs](https://github.com/mhx/dwarfs)

**C++; compressed, deduplicating, read-only filesystem images.** Relevant as a mountable archival representation, particularly for collections of similar versions; it is not a backup scheduler.

- **C2:** The [format document](https://github.com/mhx/dwarfs/blob/main/doc/dwarfs-format.md) separates sections, blocks, inodes, directory entries, chunk lists, and shared-file mappings. Distinct file metadata can reference the same content without pretending the files are hardlinks.
- **C3:** Categorized fragments can be ordered by similarity before segmentation. The document also explains full-file mapping, segmented mapping, buffered reads, and sparse extents, with explicit speed, address-space, and error-handling tradeoffs.
- **C1:** Each section carries integrity information; the metadata graph is required to reconstruct files from shared chunks. The format discussion identifies the catastrophic consequences of losing that graph.

**Entry point:** the detailed format document above, including its internal reader abstractions.

### 15. [systemd/casync](https://github.com/systemd/casync)

**C; content-addressed archive and image synchronization.** Included for storing and reconstructing related directory-tree or disk-image versions from a common chunk store, even though image distribution is a major use case.

- **C2:** The README describes the composition of a reproducible directory serialization, a linear chunk index, and a compressed content-addressed store. The same model handles trees and arbitrary blobs.
- **C3:** Serializing before chunking removes file boundaries, allowing small neighboring files and large files to use the same chunk mechanism. Clients can reuse known chunks instead of retrieving entire new images.
- **C1:** [`caformat.h`](https://github.com/systemd/casync/blob/main/src/caformat.h) defines ordered metadata records, feature flags, strictly ordered directory entries, and a terminal lookup table. Reproducibility and random access depend on these format rules.

**Entry points:** [encoding/decoding explanation](https://github.com/systemd/casync/blob/main/README.md) and the format header above.

### 16. [folbricht/desync](https://github.com/folbricht/desync)

**Go; independent casync-compatible implementation and library.** This is a separate implementation with its own store composition and concurrency design, not a cosmetic fork. Archive distribution is its primary emphasis.

- **C2:** [Store backends](https://github.com/folbricht/desync/blob/master/docs/stores.md) compose caches, ordered stores, and failover groups. Index storage is intentionally separable from chunk storage.
- **C1:** The documentation distinguishes cache corruption, missing chunks, and server failure, including the requirement that failover-group members hold identical content. [`format.go`](https://github.com/folbricht/desync/blob/master/format.go) validates record sizes and manages the lifetime of payload readers while parsing archives.
- **C3:** Cache placement, compressed versus uncompressed stores, and the location of decompression work are explicit tuning decisions. A local uncompressed cache can coexist with a compressed remote source.

**Entry points:** store documentation and format decoder above.

## Virtual-machine and fleet backup systems

### 17. [proxmox/proxmox-backup](https://github.com/proxmox/proxmox-backup)

**Rust, with web/UI components; Proxmox Backup Server and client monorepo.** This is the **official read-only GitHub mirror**. Its [GitHub metadata](https://api.github.com/repos/proxmox/proxmox-backup) reports a last push of **2024-06-05**; the implementation described here is that mirror snapshot, not a claim about current upstream behavior.

- **C2:** The [technical overview](https://github.com/proxmox/proxmox-backup/blob/master/docs/technical-overview.rst) unifies manifests, blobs, fixed indexes for VM disks, and dynamic indexes for serialized file archives within a datastore.
- **C3:** VM dirty bitmaps avoid rereading unchanged image regions, while content-defined chunking tolerates shifts in file archives. Reusing prior chunk lists avoids uploading already stored content.
- **C1:** The [backup protocol](https://github.com/proxmox/proxmox-backup/blob/master/docs/backup-protocol.rst) requires index closure and an explicit finish operation. Disconnecting before completion leaves an unfinished snapshot to be removed. The technical overview also distinguishes server verification of encrypted chunks from plaintext verification.

**Entry points:** technical overview and backup protocol. Relevant subsystems are the datastore, client, and protocol implementation, rather than the whole UI.

### 18. [elemental-lf/benji](https://github.com/elemental-lf/benji)

**Python; block-deduplicating backups for Ceph RBD, images, and devices.** Derived from backy2's foundations but substantially evolved, including its own storage integrations and NBD access. The README explicitly calls it beta quality and warns about development-branch stability.

- **C1:** The [scrubbing design](https://github.com/elemental-lf/benji/blob/master/docs/source/scrub.rst) propagates a bad shared block's invalid state to every referencing version and prevents further deduplication against that block. A partial deep scrub cannot restore a version's valid status; a successful full one is required.
- **C2:** [Data layout](https://github.com/elemental-lf/benji/blob/master/docs/source/datalayout.rst) separates SQL metadata from pluggable file, S3, and B2 block stores. The document specifies PostgreSQL for distributed operation rather than assuming all SQL backends behave equivalently.
- **C3:** Metadata-only checks and full data scrubs have explicitly different transfer costs and guarantees, useful when downloading backup blocks incurs time or monetary cost.

**Entry points:** data layout and scrubbing documentation above.

### 19. [wamdam/backy2](https://github.com/wamdam/backy2)

**Python; fixed-block, encrypted backup of Ceph RBD and other block devices.** The upstream README explicitly says it receives minimal maintenance and practically no updates after its original hosting workload changed.

- **C2:** [Data layout](https://github.com/wamdam/backy2/blob/master/docs/source/datalayout.rst) separates block storage from version/checksum/sparse-block metadata. File and S3 backends expose independent concurrency and bandwidth controls.
- **C1:** [Encryption documentation](https://github.com/wamdam/backy2/blob/master/docs/source/encryption.rst) distinguishes rewrapping per-block keys in one database transaction from migrating encrypted data into a new backup version. It explains why metadata exports must be refreshed after rekeying.
- **C3:** Rewrapping keys avoids reading the data backend, whereas encryption-format migration deliberately reprocesses blocks and reuses already migrated content.

**Entry points:** data layout and encryption lifecycle above. Benji and backy2 are retained together for substantive divergence, not as interchangeable copies.

### 20. [backuppc/backuppc](https://github.com/backuppc/backuppc)

**Perl, with companion C components; centralized, whole-file pooled backups.** Especially valuable for studying deletion and migration in a system that shares data across hosts. Version 4's pool uses application-managed references; describing current BackupPC simply as a hardlink farm would be misleading.

- **C1:** The [BackupPC manual source](https://github.com/backuppc/backuppc/blob/master/doc-src/BackupPC.pod) describes per-backup reference deltas, per-host/global counts, a reference-checking utility, and two-phase deletion to avoid racing active backups.
- **C3:** The latest backup is represented in filled form, while older versions can use reverse deltas. This favors the common latest-restore operation and avoids repeated storage of identical files.
- **C4:** The manual explains V3-to-V4 coexistence and migration. The [ChangeLog](https://github.com/backuppc/backuppc/blob/master/ChangeLog) documents years of subsequent fixes, including safeguards against an invalid share name causing overly broad deletion.

**Entry points:** manual source and ChangeLog above.

### 21. [uroni/urbackup_backend](https://github.com/uroni/urbackup_backend)

**C/C++; client/server file and image backup engine.** Focus on the server's shared-file index and filesystem-dependent storage behavior. File deduplication, incremental network transfer, and image backups are related but distinct mechanisms.

- **C1:** [`server_hash.cpp`](https://github.com/uroni/urbackup_backend/blob/dev/urbackupserver/server_hash.cpp) handles missing indexed files, changed storage paths, maximum hardlink counts, fallback copying, and cross-client index entries. The useful lesson is maintaining consistency between a database index and actual filesystem objects.
- **C3:** The [administration manual](https://www.urbackup.org/administration_manual.html) describes optional client-side hashing to avoid retransferring files another client already supplied, plus changed-block transfer and btrfs-specific sharing.
- **C2:** The same engine supports file and image workflows, while its storage behavior adapts to hardlink, reflink, and snapshot capabilities rather than assuming one filesystem contract.

**Entry points:** server hashing implementation and manual sections 3, 6, and 11.6. The manual inspected is explicitly the 2.5.x edition.

### 22. [grke/burp](https://github.com/grke/burp)

**C; network backup with whole-file sharing and reverse-delta archives.** Included for repeated-version deduplication through hardlinks and deltas; this entry does not claim that the current implementation is a global content-addressed chunk store.

- **C1:** [Working-directory recovery](https://github.com/grke/burp/blob/master/docs/working_dir.txt) describes the `working`, `finishing`, and `current` states. Once finalization starts modifying the prior backup into reverse deltas, recovery must proceed forward. The document also explains why resuming across different filesystem snapshots can produce an inconsistent bare-metal restore.
- **C3:** [Shuffling](https://github.com/grke/burp/blob/master/docs/shuffling.txt) separates transfer, manifest construction, and final archive assembly. Keeping complete changed files instead of reverse deltas trades storage for faster old-version restores and less finalization work.

**Entry points:** the two lifecycle documents above. The scope is the documented hardlink/reverse-delta design, not historical claims about other Burp protocols.

## Backup storage substrates and research implementations

### 23. [opendedup/sdfs](https://github.com/opendedup/sdfs)

**Java; deduplicating filesystem over local and object storage.** Its README includes a backup-volume mode intended for archival data. This makes it relevant as storage underneath backup applications, rather than as a complete backup scheduler. GitHub reports a July 2023 last push; treat it as a dated implementation study.

- **C2:** [`AbstractChunkStore`](https://github.com/opendedup/sdfs/blob/master/src/org/opendedup/sdfs/filestore/AbstractChunkStore.java) separates hashed-chunk storage from callers and includes retrieval, deletion, synchronization, compaction, cache control, and archived-block restoration.
- **C3:** [`HashBlobArchive`](https://github.com/opendedup/sdfs/blob/master/src/org/opendedup/sdfs/filestore/HashBlobArchive.java) aggregates chunks into larger archive objects and manages caches, upload work, and compressed-length accounting. The architecture exposes the tradeoff between efficient object-store writes and filesystem-style reads.
- **C1:** Archived-data availability is represented explicitly through restoration operations and `DataArchivedException`, rather than being collapsed into ordinary missing-data handling.

**Entry points:** chunk-store interface and archive implementation above. Installation examples are not treated as current operational guidance.

### 24. [fomy/destor](https://github.com/fomy/destor)

**C; historical research platform for deduplicating backup workloads.** GitHub reports a last push in April 2016. The README explicitly disclaims crash consistency and concurrent backup/restore support; this is an experimental comparison platform, not a production backup recommendation.

- **C2:** The README describes interchangeable chunking, fingerprint-indexing, rewriting, and restoration strategies. This provides one codebase in which to compare sparse indexing, similarity/locality approaches, and container-based storage.
- **C3:** [`do_backup.c`](https://github.com/fomy/destor/blob/master/src/do_backup.c) wires read, chunk, hash, deduplication, rewrite, and filtering phases and records their costs. Its key study problem is the tension between maximum deduplication and fragmented, slow restores.

**Entry points:** [project and limitations overview](https://github.com/fomy/destor/blob/master/README.md) and the pipeline driver above. C1 and C4 are deliberately not awarded merely because the research problem is difficult or the repository is old.

## Coverage, verification, and limitations

Live searches used more than six distinct formulations: general encrypted deduplicating backups; content-defined versus fixed-block systems; Ceph/RBD and VM backup; centralized BackupPC/UrBackup/Burp designs; Rust stream engines and offline keys; C/C++ versioned archives; casync-compatible image stores; Java backup filesystems; academic indexing/restore prototypes; and exclusion-heavy queries seeking projects beyond the familiar names. Later queries found rdedup and Bakelite; final exclusion-heavy searches primarily returned already-covered systems, forks, wrappers, and general discussions, indicating diminishing returns for this selection.

Each retained canonical repository identity was checked through GitHub's repository API or repository page. Default branches and source paths were checked against source-tree listings, and each entry has a read primary implementation or design source beyond repository metadata. Repository-status metadata was checked on the research date. None of the retained repositories was marked archived by GitHub at that check; inactivity, beta status, and the stale official mirror are reported separately. A recent push alone was not used to award C4.

The selection avoids counting GUI fronts, deployment containers, benchmark harnesses, chunker-only libraries, and ordinary duplicate-file cleaners as backup engines. Attic was not added alongside its much-evolved Borg lineage. The original `zpaq/zpaq` history mirror was inspected but not retained: zpaqfranz supplies the separately evolved implementation here, and official mirror provenance was not established for a second ZPAQ entry. Obnam surfaced in the searches, but current primary development points outside GitHub; no qualifying official GitHub mirror was established. Cumulus, Asuran, and several smaller search hits were not promoted without completing equivalent provenance and implementation verification. Their omission is not a quality judgment.

Two deliberate boundaries broaden the report: Burp represents hardlink/reverse-delta sharing, while casync, desync, and DwarFS represent deduplicating archival formats and image stores rather than full operational backup suites. The SDFS entry concerns the backup-storage substrate. Tarsnap exposes only its client. Benji/backy2, casync/desync, and restic/Rustic Core are retained as substantive separate evolutions or implementations; shared formats and ancestry are made explicit.

Criterion judgments are engineering inferences from the cited mechanisms. No candidate code was run, no restoration or crash-injection experiments were performed, and no published performance number was independently reproduced. Security mechanisms are described as designs to inspect, not as certifications. Moving branch links and stable documentation aliases may evolve after this research date.
