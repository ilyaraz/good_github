# Flash filesystems for embedded devices

Research date: **2026-10-09**

This guide selects **13 GitHub repositories** containing substantive filesystem implementations for embedded flash storage. Its center is raw NOR/NAND flash on microcontrollers and embedded operating systems. It also includes two clearly marked adjacent approaches: immutable firmware filesystems and transactional filesystems above a flash translation layer. OS monorepos count once, even when they contain several relevant filesystems. These are selections for engineering study, not certifications of correctness or recommendations that every component is suitable for production.

**Criteria legend:** **C1** — difficult correctness, including persistent invariants, concurrency, corruption, and interrupted operations. **C2** — substantial reusable abstractions serving different devices or applications. **C3** — real memory, latency, throughput, or endurance constraints addressed through understandable architecture. **C4** — sustained evolution supported by compatibility, testing, or complexity-management evidence. Each entry justifies at least two criteria. Architectural judgments are inferences from the linked primary material; project guarantees remain conditional on the hardware and integration contracts.

## Portable microcontroller filesystems

### 1. [littlefs-project/littlefs](https://github.com/littlefs-project/littlefs)

**Language/role:** C; portable filesystem designed for microcontrollers, particularly small flash-backed systems.

An unusually useful starting point for studying how persistent data structures change when RAM must remain bounded. Metadata uses small logs, while file contents use a different copy-on-write representation; this division makes the design more instructive than a single undifferentiated log.

- **C1:** Two-block metadata pairs support atomic updates despite erase-before-write constraints. Copy-on-write file data and explicit commit boundaries address recovery after power loss. The [design document](https://github.com/littlefs-project/littlefs/blob/master/DESIGN.md) explains metadata pairs, CTZ skip-lists, and the invariants behind their combination.
- **C2/C3:** A caller-supplied block-device interface separates read, program, erase, and synchronization operations from filesystem logic. Configurable caches, lookahead storage, and optional static buffers expose memory/performance tradeoffs without making RAM proportional to filesystem size. The [repository usage and testing guide](https://github.com/littlefs-project/littlefs#usage) also explains emulated-device tests and the requirement that `sync` actually persist cached writes.

### 2. [pellepl/spiffs](https://github.com/pellepl/spiffs)

**Language/role:** C; small NOR-flash filesystem with a flat namespace.

Study this alongside littlefs to understand a different response to scarce RAM: retain redundant lookup information on flash rather than maintain a complete in-memory object index.

- **C1:** Page headers track object identity, span, deletion, finalization, and index/data roles; those states must remain consistent with the block-level lookup table. The [technical specification](https://raw.githubusercontent.com/pellepl/spiffs/master/docs/TECH_SPEC) shows how NOR bit-clearing semantics implement these transitions.
- **C3:** Lookup pages reduce small SPI transactions, while logical page size trades metadata overhead against work-buffer size and scan cost. The same specification explains the reasoning instead of only reporting performance figures.

The [README and release history](https://github.com/pellepl/spiffs#features) document consistency checking, static wear leveling, regression fixes, and the introduction of AFL testing. They also explicitly state the limits: no directories or bad-block handling, variable write latency, and poor scaling beyond small devices. The old rewrite notice should not be interpreted as a completed new format.

### 3. [joembedded/JesFs](https://github.com/joembedded/JesFs)

**Language/role:** C; compact serial-NOR filesystem for bare-metal loggers and IoT firmware.

JesFs is worth studying for deliberately narrow semantics: a flat namespace, index/head/data sectors, and recovery of files whose final length was never recorded by a close operation.

- **C1:** The [high-level implementation](https://raw.githubusercontent.com/joembedded/JesFs/master/jesfs_hl.c) validates sector ownership, addresses, types, descriptor state, and sector-list traversal. Its unclosed-file handling uses the erased-byte pattern to infer the written extent. The [project explanation](https://github.com/joembedded/JesFs#technical-highlights) consequently requires avoiding or encoding `0xFF` in data that relies on this behavior; arbitrary binary logging cannot silently assume identical semantics.
- **C4:** The [header's version history](https://github.com/joembedded/JesFs/blob/master/jesfs.h) records development through multiple years, including disk checking in 2019, bounded string copying in 2022, supply-voltage checks in 2023, and read/open/check hardening in 2026. This is concrete evidence of complexity and failure-mode management, beyond repository age.

The high-level source and header are the principal reading entry points. The filesystem's narrow contracts are part of its educational value.

### 4. [pellepl/niffs](https://github.com/pellepl/niffs)

**Language/role:** C; internal-NOR filesystem with paged storage and an optional contiguous-file area. **Historical/unfinished:** the README says “Under construction”; the reviewed [master commit feed](https://github.com/pellepl/niffs/commits/master.atom) ends in October 2017.

This is a substantive implementation study, not an established deployment recommendation. Its distinctive subject is the tension between relocatable filesystem pages and files that must remain contiguous for streaming or firmware images.

- **C1:** The [internal implementation](https://raw.githubusercontent.com/pellepl/niffs/master/src/niffs_internal.c), particularly `niffs_chk`, explicitly handles interrupted erases, unfinished page moves, duplicate object headers, and orphaned data. Recovery also reasons about a spare sector needed to complete repairs.
- **C3:** The [linear-area design](https://github.com/pellepl/niffs/blob/master/LINEAR.md) separates contiguous, append-only files from the paged filesystem. It explains sector reservations and the important cost: this area is not wear-leveled. The choice makes physical layout and endurance tradeoffs directly visible.

## NAND-oriented implementations

### 5. [Aleph-One-Ltd/yaffs2](https://github.com/Aleph-One-Ltd/yaffs2)

**Language/role:** C; YAFFS filesystem core and integrations, especially for raw NAND. This repository is linked directly by the [official project site](https://yaffs.net/).

Study how flash-page tags, object identifiers, startup reconstruction, and garbage collection cooperate without relying on a conventional sector-overwrite model.

- **C1:** [How Yaffs Works](https://yaffs.net/sites/default/files/downloads/HowYaffsWorks.pdf) explains block state transitions, bad-block retirement, deletion/truncation semantics, and reconstruction. It also records a robustness change: mounting starts allocation in a new block rather than continuing a block that might have suffered an interrupted write.
- **C2/C3:** The same document separates the core from operating-system and flash interfaces, and explains chunk mapping, pooled object allocation, and the short-operation cache. These are concrete mechanisms for avoiding allocator fragmentation and excessive NAND traffic from small application reads/writes.

The design document is the best first entry point, followed by the [official YAFFS Direct guide](https://yaffs.net/sites/default/files/downloads/YaffsDirect.pdf). The design distinguishes YAFFS1 compatibility behavior from YAFFS2; those modes should not be conflated when studying hardware assumptions.

### 6. [rickyzheng/uffs](https://github.com/rickyzheng/uffs)

**Language/role:** C; Ultra-low-cost Flash File System for embedded NAND. **Historical:** the reviewed [master feed](https://github.com/rickyzheng/uffs/commits/master.atom) ends in January 2015, with power-cut simulation and unclean-block fixes.

UFFS exposes NAND controller details unusually clearly. It is useful for studying the boundary between filesystem consistency, spare-area layout, and hardware or software error correction.

- **C1:** The [flash implementation](https://raw.githubusercontent.com/rickyzheng/uffs/master/src/uffs/uffs_flash.c) distinguishes unsealed pages, corrected/uncorrectable ECC results, CRC failures, and bad blocks. It avoids applying tag ECC correction to an unsealed tag, illustrating why interrupted programming cannot be treated as an ordinary bit error.
- **C2:** The same implementation supports alternative page-operation callbacks and configurable spare/ECC layouts. The [README](https://github.com/rickyzheng/uffs#readme) documents multiple devices, bare-metal use, static allocation, and PC simulation; its history records hardware-ECC and full-page-write interface evolution.

A significant space tradeoff is also explicit: even a small file consumes an erase block. Retain this as a legacy NAND architecture reference, with no inference of current support.

## Filesystems inside embedded operating systems

### 7. [apache/nuttx](https://github.com/apache/nuttx)

**Language/role:** C; RTOS monorepo, specifically **SMARTFS/SMART MTD** and **NXFFS**. Counted once; bundled littlefs and SPIFFS are not additional entries.

NuttX offers a useful comparison within one VFS: a filesystem above a logical-sector mapping layer versus a simpler append-and-repack design.

- **C1:** [SMARTFS documentation](https://nuttx.apache.org/docs/latest/components/filesystem/smartfs.html) specifies sequence numbers, committed/released sector states, CRC options, relocation, and file/directory chains. These expose the persistent invariants that let a logical sector move while its filesystem identity remains stable.
- **C2/C3:** SMART separates MTD mapping from filesystem chains and permits multiple roots to share physical capacity. Its documentation discusses wear-leveling write amplification and garbage-collection latency. [NXFFS documentation](https://nuttx.apache.org/docs/latest/components/filesystem/nxffs.html) provides a contrasting implementation: contiguous allocation followed by repacking, with one writer and no later file growth after close.

The two documentation pages are the entry points. Their limitations matter: SMARTFS does not supply NAND bad-block management, and reclamation can make writes slow when space is scarce. A real-time OS does not make every filesystem operation time-bounded.

### 8. [apache/mynewt-core](https://github.com/apache/mynewt-core)

**Language/role:** C; embedded RTOS monorepo, specifically **`fs/nffs`**, the Newtron Flash File System.

Study explicit recovery of an object graph whose records may appear in any order during scanning, together with configurable memory pools and caches. The [official NFFS guide](https://mynewt.apache.org/latest/os/modules/fs/nffs.html) describes independently erasable areas and the small-device use case.

- **C1:** The [restore implementation](https://raw.githubusercontent.com/apache/mynewt-core/master/fs/nffs/src/nffs_restore.c) uses dummy objects while resolving references, moves recoverable children into `lost+found`, and sweeps missing or deleted objects. This is a concrete example of rebuilding consistency rather than merely trusting an on-flash directory tree.
- **C3:** The [cache implementation](https://raw.githubusercontent.com/apache/mynewt-core/master/fs/nffs/src/nffs_cache.c) allocates inode and block cache entries from memory pools and reclaims entries when exhausted. Together with the guide's configurable cache limits, it exposes the tradeoff between flash traversal cost and predictable memory allocation.

The two implementation files are the principal entry points. Automatic formatting after failed detection is configurable and can delete existing data, as the guide explicitly states. The separately published `apache/mynewt-nffs` tree was inspected but is not counted as another implementation.

### 9. [contiki-ng/contiki-ng](https://github.com/contiki-ng/contiki-ng)

**Language/role:** C; IoT operating-system monorepo, specifically **Coffee/CFS in `os/storage/cfs`**.

Coffee is valuable for its application-aware approach: sequential file allocation is combined with per-file modification logs, and applications can declare access patterns that change filesystem behavior.

- **C2:** The [Coffee API](https://raw.githubusercontent.com/contiki-ng/contiki-ng/develop/os/storage/cfs/cfs-coffee.h) exposes reservations, log sizing, firm file-size limits, and flash-aware I/O semantics. A database index that already respects flash programming rules can bypass Coffee's micro logs rather than pay for redundant adaptation.
- **C3:** The [implementation](https://raw.githubusercontent.com/contiki-ng/contiki-ng/develop/os/storage/cfs/cfs-coffee.c) separates cached file metadata, sequential page allocation, micro logs, merging, and reclamation. It offers append-only configuration to reduce code and explicitly rejects an incompatible combination with micro logs.

These two files are compact entry points into storage design for sensor-class systems. This entry concerns Contiki-NG's retained implementation; the original Contiki repository is not separately counted. No blanket crash-atomicity claim is inferred from the presence of logs.

## Embedded Unix and kernel implementations

### 10. [torvalds/linux](https://github.com/torvalds/linux)

**Language/role:** C for the relevant subsystems; upstream Linux source tree, published on GitHub. Relevant code includes **`fs/ubifs`**, **`fs/jffs2`**, **`drivers/mtd/ubi`**, and, for managed flash, **`fs/f2fs`**. The monorepo counts once.

This is the large-system comparison point: raw-flash wear/bad-block management, filesystem indexing, and managed-flash allocation are separate concerns.

- **C1/C2:** The [UBIFS documentation](https://docs.kernel.org/filesystems/ubifs.html) explains recovery by journal replay and the interface between UBIFS and UBI volumes. UBI handles wear and bad blocks underneath the filesystem. The document also distinguishes JFFS2's mount-time index reconstruction from UBIFS's on-media index.
- **C3:** The [F2FS architecture documentation](https://docs.kernel.org/filesystems/f2fs.html) explains its node-address table for limiting cascading pointer updates, multiple logs separating hot/cold data, and background segment cleaning. It explicitly targets flash-backed block devices such as eMMC and SD cards, whereas UBIFS targets the MTD/UBI model.

Those two architecture documents are the recommended entry points. Their different device assumptions are essential; F2FS is not a substitute for raw-NAND bad-block management.

### 11. [NetBSD/src](https://github.com/NetBSD/src)

**Language/role:** C; **CHFS**, the Chip File System, in `sys/ufs/chfs`. **Official automatic CVS-to-GitHub mirror:** the repository warns that commit links can change. This guide uses branch paths.

CHFS adds a BSD implementation and a university-origin design to the comparison. The [mount manual](https://raw.githubusercontent.com/NetBSD/src/trunk/sbin/mount_chfs/mount_chfs.8) explicitly restricts it to flash devices, distinguishing those from SSD/USB block devices.

- **C1:** The [garbage collector](https://raw.githubusercontent.com/NetBSD/src/trunk/sys/ufs/chfs/chfs_gc.c) coordinates a background thread, mount-field and vnode-cache locks, condition variables, and vnode reconstruction. Lock assertions and transitions make concurrency and reclamation invariants visible.
- **C2:** The [CHFS source tree](https://github.com/NetBSD/src/tree/trunk/sys/ufs/chfs) separates erase-block handling (`ebh`), scanning, write buffering, garbage collection, inode reconstruction, and VFS/vnode operations. It is useful for studying how raw-flash management is integrated into an existing kernel filesystem interface.

**Material limitation:** the current manual retains warnings about filling the filesystem and about old contents appearing after truncate/regrow. Their continued documentation is not proof of a fresh reproduction, but it prevents presenting CHFS as an unqualified deployment choice. Its value here is architectural and historical.

## Immutable firmware images and translated flash

### 12. [mikee47/IFS](https://github.com/mikee47/IFS)

**Language/role:** C++ with Python image-building tools; specifically the original **FWFS** firmware filesystem and **HYFS** hybrid filesystem for resource-limited embedded platforms.

Included for its own storage format and layering behavior, not merely its adapters to other filesystems. The [project documentation](https://github.com/mikee47/IFS#readme) describes immutable files, directories, and metadata stored as objects, plus a writable layer that copies files when modified.

- **C2:** The filesystem interface, object-based FWFS implementation, mount points, and HYFS overlay allow immutable firmware resources and writable application state to share a namespace. Resetting the writable layer restores the underlying defaults.
- **C3:** Prebuilt compact images avoid allocating a writable flash filesystem for fixed assets. The [FWFS implementation](https://raw.githubusercontent.com/mikee47/IFS/master/src/FWFS/FileSystem.cpp) walks object headers/references, derives file extents, and accesses a storage partition directly. These are useful mechanisms for studying small-memory resource serving and image layout.

The documentation and FWFS source are the entry points. This is a read-only-format/overlay study, not an independent NAND wear-leveling implementation. The reviewed [master feed](https://github.com/mikee47/IFS/commits/master.atom) ends in July 2024; that observation alone does not establish support status on other branches.

### 13. [tuxera/reliance-edge](https://github.com/tuxera/reliance-edge)

**Language/role:** C; transactional filesystem for microcontrollers, operating on a block-device interface. **Scope boundary:** raw flash needs an appropriate translation layer; this is not itself a raw-NAND FTL.

Study how application-visible transaction points are translated into durable metadata changes. This provides a useful comparison with per-operation consistency in smaller raw-flash filesystems.

- **C1:** The [volume implementation](https://raw.githubusercontent.com/tuxera/reliance-edge/master/core/driver/volume.c) maintains two metaroots and selects the latest complete one at mount. `RedVolTransact` flushes data before publishing the new metaroot, then flushes again before reporting completion. Its comments explicitly explain the corruption window that device write reordering would otherwise create.
- **C4:** The [release notes](https://github.com/tuxera/reliance-edge/blob/master/doc/release_notes.md) span, among other releases, 2020, 2022, and 2026. They describe retention of the earlier disk layout when introducing checksummed directory metadata, upgrade requirements, port fixes, and testing changes.

Those are the two principal entry points. The release notes explicitly identify some FTL integrations and fault/power-interruption test projects as commercial-only; their existence must not be mistaken for those components being available in this GitHub checkout.

## Coverage, search method, and limits

Discovery used more than six distinct formulations, including embedded NOR/NAND filesystems and power loss; internal-flash/contiguous-file designs; UFFS and NAND ECC; RTOS SMARTFS/NXFFS/NFFS; Coffee and sensor storage; BSD CHFS; transactional microcontroller filesystems; C++ firmware filesystems; and Rust-native flash filesystems. Follow-up searches excluding littlefs, SPIFFS, FatFs, and wrappers mostly returned already inspected projects, adapters, key-value stores, or thinly evidenced candidates. Discovery results were followed by reading canonical GitHub pages and additional implementation/design material; snippets alone were not used to retain entries.

The resulting selection is predominantly C because that is where the verified independent raw-flash implementations were concentrated. C++ firmware-image architecture supplies another implementation style. Rust searches chiefly surfaced bindings and key-value stores; language diversity was not manufactured by including them as independent filesystems. Similarly, [yomimono/chamelon](https://github.com/yomimono/chamelon) was inspected but excluded because its stated role is a MirageOS block-backed key-value implementation, with caveats about wear awareness. [StratifyLabs/sffs](https://github.com/StratifyLabs/sffs) was inspected but omitted because its sparse development record and unfinished design documentation added less well-supported coverage than the retained implementations.

Excluded categories include FTL-only libraries such as Dhara, standalone key-value stores such as EKV/NVS, generic FAT ports without distinctive flash-filesystem implementation, format/upload tools, and board-specific wrappers. YAFFS forks, littlefs ports, the original Contiki alongside Contiki-NG, and the separate NFFS extraction are not counted as independent projects. Linux's multiple flash filesystems and NuttX's multiple native implementations each remain one repository.

All 13 repository identities were verified by opening their GitHub pages; additional source files or architecture documents were read for every entry. Some GitHub API metadata requests were rate-limited, so source pages, raw files, and public commit feeds supplied the remaining evidence. Historical status is stated where directly supported; monorepo activity is not treated as evidence of active maintenance of every subsystem. No candidate code was run, no repository was cloned, and no benchmark or hardware power-cut test was performed. Performance observations concern documented mechanisms, not independently measured results.
