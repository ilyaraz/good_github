# Journaling and copy-on-write filesystems

Research date: **2026-10-09**.

This selection covers 19 GitHub repositories implementing filesystem journaling, transactional shadow paging, or copy-on-write (COW) storage. It spans operating-system subsystems, independent drivers, embedded libraries, unikernel storage, and research prototypes. Operating-system monorepos count once; their relevant subsystems are identified below. Database engines, backup frontends, reflink wrappers, and block-device snapshot managers are outside the main selection. Inclusion identifies worthwhile engineering study, not production suitability or uniformly exemplary code.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial input handling, crash consistency, or recovery.
- **C2 — Abstractions:** substantial reusable mechanisms supporting multiple operations, backends, or storage uses.
- **C3 — Performance and structure:** concrete resource or performance constraints addressed through an understandable architecture.
- **C4 — Evolution:** documented evolution over years together with compatibility, testing, or complexity management.

Criteria below are judgments grounded in the cited mechanisms. Descriptions of guarantees refer to each project's design and assumptions, not an independent verification performed for this report. The linked implementation and design documents are suggested reading entry points.

## Operating-system filesystem implementations

### 1. [torvalds/linux](https://github.com/torvalds/linux)

**Language/role:** C; kernel monorepo. Relevant subsystems are ext4/JBD2, XFS, and Btrfs, counted together.

Study how different consistency strategies coexist behind the same filesystem interface. Ext4 exposes the distinction between metadata consistency and file-data durability; Btrfs demonstrates the allocation and reference-accounting consequences of sharing persistent trees.

- **C1:** The [ext4 journal documentation](https://docs.kernel.org/filesystems/ext4/journal.html) explains commit records, checksummed replay, and revocation records that prevent an old metadata image from overwriting a block subsequently reused for file data. Its fast-commit discussion works through why replay must record idempotent outcomes rather than blindly repeat operations.
- **C2:** The [Btrfs design](https://btrfs.readthedocs.io/en/stable/dev/dev-btrfs-design.html) uses a common keyed B-tree representation for several metadata types, reference-counted extents for snapshots, and backreferences for validation and relocation. These mechanisms serve namespace management, allocation, snapshots, and maintenance.
- **C3:** The [XFS logging design](https://docs.kernel.org/filesystems/xfs/xfs-delayed-logging-design.html) connects finite log reservations, rolling transactions, intent records, and delayed logging to forward progress and reduced metadata logging overhead. It explicitly distinguishes an in-memory atomic operation from what has actually reached stable storage.

### 2. [openzfs/zfs](https://github.com/openzfs/zfs)

**Language/role:** Primarily C; OpenZFS implementation for Linux and FreeBSD.

Study the interaction between COW trees and the transaction-group pipeline, especially the less obvious problem that flushing filesystem changes generates further allocation metadata that must itself be flushed.

- **C1:** The project's [COW explanation](https://github.com/openzfs/openzfs-docs/blob/master/docs/Basic%20Concepts/Copy-on-write.rst) describes parent-held checksums and the final uberblock update. The implementation's consistency boundary is a transaction group, rather than an arbitrary collection of completed application writes.
- **C3:** The architectural comment and implementation in [module/zfs/txg.c](https://github.com/openzfs/zfs/blob/master/module/zfs/txg.c) separate open, quiescing, and syncing states so accepting work can overlap with persistence. They also explain convergence: later sync passes can reuse blocks allocated within the same syncing group, defer frees, and stop compression to finish the metadata recursion. This is a particularly useful example of performance engineering constrained by a persistence invariant.

### 3. [koverstreet/bcachefs-tools](https://github.com/koverstreet/bcachefs-tools)

**Language/role:** C filesystem implementation with Rust/C userspace tooling; the repository now contains the filesystem itself under `fs/`.

The verified repository README identifies this as the official development tree, with an out-of-mainline kernel module. The old [koverstreet/bcachefs](https://github.com/koverstreet/bcachefs) repository is archived and directs development here; it is not a second selection. GitHub's inherited fork label does not make this a separate competing implementation.

- **C1:** The [principles of operation](https://github.com/koverstreet/bcachefs-tools/blob/master/doc/bcachefs-principles-of-operation.tex) describe atomic multi-key updates, journal reservations, ordered write-lock acquisition, transaction restart, and recovery handling of B-tree updates whose journal sequence did not persist. These expose the boundary between concurrent in-memory commit and durable commit.
- **C2:** The same design builds filesystem state from B-tree key/value records and generation-tagged allocation buckets. Extents, inodes, directory entries, reverse mappings, and background maintenance reuse these foundations.
- **C3:** Large, internally log-structured B-tree nodes accumulate journaled changes before node writeback, addressing random-update write amplification. The transaction layer avoids holding B-tree locks across I/O. Study these mechanisms without assuming the document's comparative performance claims hold for every workload.

### 4. [freebsd/freebsd-src](https://github.com/freebsd/freebsd-src)

**Language/role:** C; official publish-only source repository. Focus: UFS/FFS journaled soft updates and its recovery checker, rather than the imported OpenZFS implementation.

Study a hybrid that combines dependency tracking with a journal, including the interaction between vnode locks, buffer locks, allocation, and reclamation.

- **C1:** [ffs_softdep.c](https://github.com/freebsd/freebsd-src/blob/main/sys/ufs/ffs/ffs_softdep.c) documents lock-order reversals and safe restart points. It checks journal capacity before operations hold buffers that would themselves need flushing to reclaim journal space, preventing a circular wait.
- **C3:** The same implementation batches work through dependency lists and journal processing, with resource-pressure controls and explicit yielding. The performance problem is how to defer metadata work while preserving forward progress under bounded journal and buffer capacity.
- **C1, recovery detail:** [sbin/fsck_ffs/suj.c](https://github.com/freebsd/freebsd-src/blob/main/sbin/fsck_ffs/suj.c) checks overlapping allocation records before freeing a block and determines when indirect blocks are safe to follow. It also provides a fallback to a full check when journal checking fails. This is useful for studying why recovery cannot interpret old block addresses without considering reuse.

### 5. [NetBSD/src](https://github.com/NetBSD/src)

**Language/role:** C; official automatic CVS conversion on GitHub. Focus: WAPBL journaling with FFS. The repository warns that converted commit links can change; the links below use source paths rather than commit hashes.

Study a filesystem-independent physical logging service, with a compact description of its circular log and locking rules embedded in the implementation.

- **C1:** [sys/kern/vfs_wapbl.c](https://github.com/NetBSD/src/blob/trunk/sys/kern/vfs_wapbl.c) describes two generation-numbered commit headers, circular-log head/tail ownership, completed versus outstanding writes, and per-field synchronization requirements. Transaction admission considers buffered bytes, record counts, deallocations, and journal capacity.
- **C2:** The same file exposes transaction, buffer, flush, and replay operations through a filesystem-independent logging interface, rather than embedding every recovery operation in namespace code.
- **Practical boundary:** The [WAPBL manual source](https://github.com/NetBSD/src/blob/trunk/share/man/man4/wapbl.4) explains its FFS integration, journal placement, old-system compatibility restrictions, and the latency consequence of committing outstanding metadata on `fsync`. Those qualifications are part of the abstraction's contract.

### 6. [DragonFlyBSD/DragonFlyBSD](https://github.com/DragonFlyBSD/DragonFlyBSD)

**Language/role:** C; official read-only system-source mirror. Focus: HAMMER2, not a separate entry for every HAMMER generation.

Study an alternative to the usual COW B-tree: a radix-tree block topology with filesystem roots, snapshots, and a separately managed free-space map.

- **C1:** The in-tree [HAMMER2 DESIGN](https://github.com/DragonFlyBSD/DragonFlyBSD/blob/master/sys/vfs/hammer2/DESIGN) explains propagating modifications to the volume root, deferring block frees, and rotating volume headers so recovery can select a complete valid version after a partial write.
- **C2:** The same design makes independently mountable filesystem roots and snapshots instances of its PFS abstraction. Block references and radix-tree topology are reused for files and filesystem metadata.
- **C3:** The document connects embedded directory names and inode block references to locality and space usage, and separates frontend operations from backend I/O and compression work. It also discusses snapshot-related bulk-free costs. Its later clustering sections include proposed behavior; they should not be read as evidence that every distributed feature is implemented.

### 7. [haiku/haiku](https://github.com/haiku/haiku)

**Language/role:** C++; official GitHub source mirror, with contributions directed to Haiku's review service. Focus: the writable BFS implementation under `src/add-ons/kernel/file_systems/bfs/`.

Study how journaling integrates with transaction-aware block caching and typed filesystem indexes while retaining compatibility with the original Be filesystem.

- **C1:** [Journal.cpp](https://github.com/haiku/haiku/blob/master/src/add-ons/kernel/file_systems/bfs/Journal.cpp) implements replay, transaction flushing, and lock-sensitive flush behavior. It preserves the original replay format's restriction on block-run lengths and documents a legacy full-log replay corner case, making both compatibility and unresolved complexity visible.
- **C2:** [BPlusTree.cpp](https://github.com/haiku/haiku/blob/master/src/add-ons/kernel/file_systems/bfs/BPlusTree.cpp) provides typed key handling, cached-node access, iterators, and transaction listeners. The same tree machinery accommodates directory/index containers and multiple scalar key types, while writable nodes join the block-cache transaction. This is a substantive object-oriented storage abstraction rather than just a POSIX syscall adapter.

## Independent COW implementations and cross-platform drivers

### 8. [maharmstone/btrfs](https://github.com/maharmstone/btrfs)

**Language/role:** Primarily C; WinBtrfs, an independent Windows implementation of the Btrfs format. The README explicitly identifies it as a reimplementation without Linux-kernel code.

Study COW persistence alongside Windows cache-manager, security, and filesystem semantics. Its mapping of ACLs and alternate data streams to extended attributes makes cross-platform behavior particularly instructive.

- **C1:** [src/flushthread.c](https://github.com/maharmstone/btrfs/blob/master/src/flushthread.c) repeatedly reconciles changed trees and allocation state, checks tree sizes and new addresses, writes trees, and then publishes superblock roots. The code exposes how updating allocation metadata can itself force more tree work.
- **C2:** The [repository documentation](https://github.com/maharmstone/btrfs#readme) describes reusable mappings between Windows concepts and Btrfs objects, as well as subvolumes, reflinks, send/receive, and multiple storage layouts. These provide several consumers for the tree and extent machinery.
- **C4:** The [release history](https://github.com/maharmstone/btrfs/releases) spans releases in 2021–2026; the README records support for successively introduced Linux format features and retains an explicit unsupported-feature list. Full transaction-log support remains listed as unfinished, so format compatibility should not be inferred to be complete.

### 9. [linux-apfs/linux-apfs-rw](https://github.com/linux-apfs/linux-apfs-rw)

**Language/role:** C; independent Linux APFS driver with experimental write support. This is not Apple's implementation. Its README states that testing is limited and mounts default to read-only.

Study how a reverse-engineered COW format becomes a writable driver, especially object versions, checkpoint publication, and the need to leave space for recovery from an almost-full filesystem.

- **C1:** [transaction.c](https://github.com/linux-apfs/linux-apfs-rw/blob/master/transaction.c) flushes changes before publishing a checkpoint superblock, validates ephemeral-object sizes and checksums, and applies different space bounds to ordinary updates, deletion, and sync. The explicit limitations are valuable evidence of the correctness burden, not proof that it has all been resolved.
- **C2:** [btree.c](https://github.com/linux-apfs/linux-apfs-rw/blob/master/btree.c) uses shared query objects and traversal machinery for catalog and object-map operations. Object-map lookup adds transaction-ID-sensitive addressing and caching; catalog traversal handles its own format variants through that common infrastructure.

### 10. [redox-os/redoxfs](https://github.com/redox-os/redoxfs)

**Language/role:** Rust; official substantive mirror of the Redox GitLab repository. A COW filesystem for Redox's microkernel environment, also usable through Linux FUSE.

Study how explicit transaction state and typed disk/block interfaces organize allocation, encryption, checksums, and publication of a new filesystem generation.

- **C1:** [src/transaction.rs](https://github.com/redox-os/redoxfs/blob/master/src/transaction.rs) defers deallocation to avoid premature block reuse, tracks allocator changes, checks batched write lengths, and writes a new generation header after cached blocks. These are concrete ordering and failure-path concerns; Rust ownership alone does not settle the storage-device durability contract.
- **C2:** The [Disk trait](https://github.com/redox-os/redoxfs/blob/master/src/disk/mod.rs) separates block access from filesystem logic, with file, memory, sparse, cache, and I/O modules exposed alongside it. Batched writes have a default implementation. The transaction layer can therefore work above multiple storage representations, useful for both operating-system integration and testing.

### 11. [bfffs/bfffs](https://github.com/bfffs/bfffs)

**Language/role:** Rust; Black Footed Ferret File System, a developing COW filesystem whose documented executable implementation is a FUSE server on FreeBSD. The repository showed no published releases when inspected; planned features should not be treated as shipped guarantees.

Study an unusually explicit separation of the filesystem, transaction database, addressing layers, allocation, RAID, and asynchronous device I/O.

- **C1:** The [implementation guide](https://github.com/bfffs/bfffs/blob/master/doc/implementation.md) distinguishes transaction-scoped datasets, relocatable indirect records, and directly addressed records with a single-reference invariant. Its testing strategy includes mocked lower layers for otherwise hard-to-trigger failures, full-stack tests, and randomized torture tests.
- **C2:** The same guide explains a generic tree implementation shared by direct and indirect COW B+ trees, and the separation of `bfffs-core` from the FUSE frontend. The proposed kernel frontend is explicitly hypothetical, not an existing second implementation.
- **C3:** Clean-data caching and dirty writeback are distinct modules. An fio backend exercises the core without FUSE overhead, while the device scheduling layer controls queued I/O. This makes performance boundaries inspectable rather than hiding them inside a single filesystem loop.

## Embedded and unikernel storage

### 12. [littlefs-project/littlefs](https://github.com/littlefs-project/littlefs)

**Language/role:** C; portable filesystem library for constrained devices and flash storage.

Study a design where bounded memory, flash erase granularity, wear, and sudden power loss all shape the persistent data structures.

- **C1:** The [design document](https://github.com/littlefs-project/littlefs/blob/master/DESIGN.md) combines small two-block metadata logs with COW file data, including revision arithmetic and the relationship between atomic metadata updates and block erasure.
- **C2:** The repository's public configuration interface supplies read, program, erase, and sync callbacks, storage geometry, and optional caller-owned buffers. This is a reusable filesystem core rather than a driver for one board.
- **C3:** The design bounds metadata-log work and RAM use, and explains why unrestricted upward COW propagation would concentrate writes and wear. The architectural choices explicitly trade memory, access cost, and write amplification.
- **Evidence of testing:** [tests/test_powerloss.toml](https://github.com/littlefs-project/littlefs/blob/master/tests/test_powerloss.toml) constructs partial metadata states, including a newer revision count without a complete replacement, then checks that data remains readable and subsequent writes work. This is stronger evidence than the fail-safe tagline alone.

### 13. [tuxera/reliance-edge](https://github.com/tuxera/reliance-edge)

**Language/role:** C; configurable transactional filesystem for microcontrollers, with POSIX-like and minimalist API choices.

Study application-visible transaction points implemented through block branching and alternating metadata roots, including what can be reclaimed before versus after a commit.

- **C1:** [core/driver/inodedata.c](https://github.com/tuxera/reliance-edge/blob/master/core/driver/inodedata.c) distinguishes already-branched blocks from committed blocks that require a new allocation. [core/driver/volume.c](https://github.com/tuxera/reliance-edge/blob/master/core/driver/volume.c) flushes buffers, advances sequence numbers, validates metadata-root CRCs, and selects a valid root at mount. Together they establish the COW-style category fit beyond the word “transactional.”
- **C2:** Configurable volume geometry, storage/OS adaptation, two API styles, and optional POSIX features let the same transactional core serve different embedded environments and memory budgets.
- **C4:** The [release notes](https://github.com/tuxera/reliance-edge/blob/master/doc/release_notes.md) document releases from 2017 through 2026, configuration compatibility, disk-layout changes, concurrency fixes, and regression fixes. They also distinguish commercial-only facilities and tests; the power-interruption and error-injection suites mentioned there must not be assumed to be included in the public tree.

### 14. [gkostka/lwext4](https://github.com/gkostka/lwext4)

**Language/role:** C; embeddable ext2/ext3/ext4 library, intended particularly for microcontrollers using managed block storage.

Study how a widely deployed on-disk format and its journal protocol can be implemented outside a full operating-system kernel. The README explicitly says this is not a raw-flash filesystem.

- **C1:** [src/ext4_journal.c](https://github.com/gkostka/lwext4/blob/master/src/ext4_journal.c) implements recovery transaction tracking, a red-black tree of revoked blocks, circular-log wrapping, and journal checksum variants. The revoke records carry transaction IDs so recovery can suppress obsolete writes to reused blocks.
- **C2:** The [repository's configuration and integration documentation](https://github.com/gkostka/lwext4#readme) describes ext2/3/4 configurations, endian support, a C-library dependency boundary, and configurable block caching. Journaling and extents can be selected according to the device's memory budget, allowing one implementation to serve multiple MCU and FUSE-based environments.
- **Scope qualification:** This is a separate library drawing on HelenOS and other filesystem work, not a claim of a clean-room implementation or complete support for every modern ext4 feature. Its compatibility matrix is part of the useful reading.

### 15. [yomimono/chamelon](https://github.com/yomimono/chamelon)

**Language/role:** OCaml; independent implementation of a littlefs subset, exposing persistent hierarchical key/value storage for MirageOS. It is not a binding around the C library and is not a POSIX filesystem.

Study functional-language modules at the boundary between a binary filesystem format and a reusable unikernel storage interface.

- **C1:** [lib/commit.ml](https://github.com/yomimono/chamelon/blob/main/lib/commit.ml) handles chained XOR tags, CRC inputs, commit padding, program-block alignment, and serialization of successive commits. These are nontrivial persistent-format invariants; the README additionally describes serializer tests and property-based fuzzing.
- **C2:** [mirage/kv.ml](https://github.com/yomimono/chamelon/blob/main/mirage/kv.ml) is parameterized over `Mirage_block.S` and adapts the filesystem to Mirage's key/value interface with explicit lookup and write errors. It illustrates reuse through OCaml functors and module contracts.
- **Boundary:** The README explicitly disclaims constant-memory traversal, flash wear leveling, bad-block tracking, and large-filesystem suitability. Its omission of littlefs's threaded directory links and global move state is a deliberate divergence; C1 here identifies complexity worth studying, not equivalence to littlefs's guarantees.

## Research systems and historical implementations

### 16. [NVSL/linux-nova](https://github.com/NVSL/linux-nova)

**Language/role:** C; UC San Diego NOVA filesystem in a Linux research tree. Focus only on `fs/nova/`; the copied kernel is not another general Linux selection. The documented mainline baseline is Linux 5.1, so this is presented as a historical research implementation, without claiming current-kernel support.

Study a hybrid of per-inode logging, COW data pages, and small journals for operations crossing inode boundaries, designed for byte-addressable persistent memory.

- **C1:** [fs/nova/journal.c](https://github.com/NVSL/linux-nova/blob/master/fs/nova/journal.c) explicitly handles atomic multi-inode directory operations such as rename and unlink. It includes per-CPU journal traversal, checksums, and recovery code, showing why independently logged objects still require coordination.
- **C3:** The [repository's architecture description](https://github.com/NVSL/linux-nova#readme) separates metadata logs from file data and divides logging by inode. This reduces global-log contention, makes log cleaning more localized, and permits parallel recovery scanning. DAX mapping and data/metadata protection introduce a different performance and failure model from sector-oriented storage.

### 17. [utsaslab/WineFS](https://github.com/utsaslab/WineFS)

**Language/role:** C; SOSP 2021 research artifact based on a substantially modified PMFS, with WineFS under `Linux-5.1/fs/winefs/`. Its bundled comparison systems are not additional selections.

Study how virtual-memory translation and filesystem aging influence allocation policy. The repository includes an older full experimental environment, so its historical “active development” README wording is not treated as a verified current-maintenance claim.

- **C1:** [Linux-5.1/fs/winefs/journal.c](https://github.com/utsaslab/WineFS/blob/main/Linux-5.1/fs/winefs/journal.c) contains transaction undo/redo, generation checks, log invalidation, and persistent barriers. Reverse-order undo and ordering of persistent writes make the failure model concrete.
- **C3:** The [design and artifact description](https://github.com/utsaslab/WineFS#readme) uses huge-page-aligned allocation for memory-mapped files and a hole-filling allocator for other files, preserving useful free extents as the filesystem ages. Per-CPU journaling addresses metadata concurrency. Study these explicit mechanisms and the strict/relaxed consistency modes; no benchmark speedup is generalized here beyond the original setup.

### 18. [oscarlab/betrfs](https://github.com/oscarlab/betrfs)

**Language/role:** C/C++; research filesystem built around a write-optimized Bε-tree/Bε-DAG. Use the verified [`v0.6` source](https://github.com/oscarlab/betrfs/tree/v0.6), whose README targets Linux 4.19.99; the default branch's older build instructions do not describe that version.

Study how delayed updates change the usual COW granularity tradeoff: copying too much amplifies writes, while copying too little fragments future reads.

- **C1:** The authors' [How to Copy Files paper](https://oscarlab.github.io/papers/fast20-zhan.pdf) explains transforming the tree into a shared DAG, deferred clone messages, and translation prefixes that make keys meaningful along different shared paths. Correct reads and updates must coexist with partially shared structure and deferred changes.
- **C3:** Its copy-on-abundant-write policy accumulates small modifications before physically breaking sharing, separating update size from copy size to preserve locality. This is a substantive alternate COW algorithm, not merely a frontend invoking reflink.
- **C2:** The [`v0.6` architecture description](https://github.com/oscarlab/betrfs/blob/v0.6/README.md) separates VFS-to-index translation, the storage index, and a lower filesystem. It identifies reusable transaction/index machinery and a module for running index regression tests inside the kernel. Treat this as a research code-reading target with a specific toolchain, not a current distribution filesystem.

### 19. [mit-pdos/fscq](https://github.com/mit-pdos/fscq)

**Language/role:** Coq with Haskell integration; explicitly **unmaintained research prototype**. The repository's default branch contains DFSCQ, associated with the 2017 follow-on work; the `security` branch contains later security-oriented work.

Study what it takes to specify recovery as part of filesystem correctness instead of treating it as an exceptional code path.

- **C1:** [src/Log.v](https://github.com/mit-pdos/fscq/blob/master/src/Log.v) defines distinct inactive, active, flushing, rollback, and recovering transaction states and their representation predicates over cached and durable state. These expose proof obligations hidden behind a conventional journal API.
- **C2:** The authors' [Crash Hoare Logic description](https://adam.chlipala.net/papers/FscqSOSP15/) explains crash conditions, recovery procedures, and logical disk address spaces for composing storage layers. The default branch's log implementation composes transaction state with group logging and buffer-cache representations, illustrating reusable proof and storage abstractions.
- **Trust boundary:** The repository explicitly excludes its Haskell/FUSE integration and dependencies from the verified core. The 2015 paper supplies foundational context; it should not be mistaken for a complete description or proof of every component on the current default branch.

## Coverage, search process, and limitations

Discovery used live web searches followed by repository-page verification and reads of distinct implementation/design sources. Search formulations covered, among others:

- General COW architecture: Btrfs, OpenZFS, and bcachefs.
- Embedded journaling and transactional storage: littlefs, lwext4, and Reliance Edge.
- BSD and alternative-OS mechanisms: HAMMER2, WAPBL, journaled soft updates, and BFS.
- Rust filesystem implementations: RedoxFS and BFFFS.
- Independent format implementations: Windows Btrfs and writable Linux APFS.
- Persistent-memory journals and COW: NOVA, WineFS, and PMFS lineage.
- Write-optimized cloning: BetrFS, Bε-trees, and copy-on-abundant-write.
- Functional-language and formal-verification implementations: Chamelon and FSCQ.
- Broader follow-up searches for less familiar COW designs, including Tux3, historical versioning filesystems, and recent FUSE projects.

The later broad searches increasingly returned wrappers, backup tools, databases, duplicated upstream code, or projects whose architectural/implementation evidence was weaker than the retained set. Tux3 and ext3cow were discovery leads but were not retained after prioritizing independently verified, better-supported implementations. CrashMonkey is relevant testing infrastructure, but not itself a journaling or COW filesystem. Reflink libraries, ordinary FAT/ext2-only libraries, read-only image viewers, and storage-management frontends were excluded. OpenZFS ports and downstream littlefs copies were not counted separately; WinBtrfs and Chamelon qualify because they are substantive independent implementations. WineFS and NOVA qualify on their distinct filesystem work, not their vendored Linux trees.

Official GitHub mirrors are labeled. The bcachefs relocation was checked, and only its present development repository is counted. Repository pages can contain stale activity descriptions; absent explicit release/history evidence, this report makes no promise of active maintenance. C4 is assigned selectively rather than inferred from creation dates or stars. No candidate code was executed, dependencies installed, or large repositories cloned. GitHub API rate limiting and occasional browser rendering failures were handled by reading public source files directly. These are source-based selections, not fresh crash-testing results, performance measurements, or a comprehensive audit of every subsystem.
