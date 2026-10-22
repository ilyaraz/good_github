# File synchronization engines

Research date: **2026-10-09**.

This selection covers engines that reconcile filesystem replicas, propagate directory changes, synchronize files with cloud services, or implement the delta-transfer machinery used by those systems. It includes 21 repositories, spanning complete synchronizers, event-driven replication coordinators, and explicitly identified file-level building blocks. Backup-only systems, general database replication, distributed filesystems without a distinct file-sync focus, and thin graphical wrappers are outside the main scope. These are study recommendations based on the cited implementations, not a claim that every component is exemplary or that every project is suitable for a new deployment.

**Criteria legend:** **C1** — difficult correctness, including conflicts, concurrency, interrupted operations, filesystem semantics, or hostile inputs. **C2** — substantial abstractions reusable across backends, platforms, policies, or applications. **C3** — concrete performance constraints addressed through an understandable design. **C4** — sustained evolution accompanied by compatibility work, testing, or deliberate complexity management. Each entry justifies at least two criteria. Architectural assessments are grounded in the linked material; they are not results of running or auditing the software.

## General-purpose and peer-to-peer reconciliation

### 1. [syncthing/syncthing](https://github.com/syncthing/syncthing)

**Language / role:** Go; continuous synchronization among multiple devices.

Study the separation between local filesystem state, peers' advertised versions, the selected global version, and the block-transfer process. This makes Syncthing especially useful for understanding how metadata convergence and byte reconstruction interact.

- **C1:** Received blocks are checked against their expected hashes before entering a temporary file. Concurrent edits produce conflict copies, and case-insensitive filename collisions are treated explicitly rather than silently overwriting another path. The documentation also explains why conflict copies themselves propagate. [Synchronization mechanics](https://docs.syncthing.net/users/syncing.html)
- **C3:** Needed blocks can come from another local file or a peer, reducing unnecessary transfers. Watcher events are accumulated, while periodic full scans compensate for missed notifications; this exposes a concrete tradeoff between scan cost and eventual detection. [Scanning and block reuse](https://docs.syncthing.net/users/syncing.html)

**Entry point:** [Understanding Synchronization](https://docs.syncthing.net/users/syncing.html), then follow the repository's `lib` implementation. This is a device synchronizer, not a transactional distributed filesystem.

### 2. [bcpierce00/unison](https://github.com/bcpierce00/unison)

**Language / role:** OCaml with platform support code; bidirectional reconciliation of two independently modified directory trees.

Unison is a particularly clear study in specifying what synchronization means. Its archive records the last synchronized state, allowing a deletion to be distinguished from a newly created file and identical concurrent edits to be recognized as false conflicts.

- **C1:** The manual describes reconciliation stages, temporary-file replacement, and invariants for both replica contents and persistent archives. It also documents the awkward file-to-directory replacement window where interruption can require manual cleanup, rather than presenting atomicity as unconditional. [Reconciliation and invariants](https://github.com/bcpierce00/unison/blob/master/doc/unison-manual.tex)
- **C4:** Release notes across 2022–2026 document OCaml/platform changes, recovery behavior, timestamp-policy fixes, and protocol/archive compatibility boundaries. Version 2.54 explicitly drops pre-2.52 interoperability and archive support: useful evidence of managed compatibility costs. [Release history](https://github.com/bcpierce00/unison/blob/master/NEWS.md)

**Entry points:** the manual's reconciliation/invariants sections and `NEWS.md`. The repository describes a small maintenance team; current release notes also flag GUI maintenance limitations.

### 3. [mutagen-io/mutagen](https://github.com/mutagen-io/mutagen)

**Language / role:** Go; continuous synchronization for local, SSH, and container development environments. The relevant subsystem is `pkg/synchronization`, rather than its separate network-forwarding functionality.

Study its explicit ancestor/alpha/beta reconciliation model and the boundary between deciding changes and applying them.

- **C1:** The reconciler documents invariants about untracked, problematic, and synchronizable entries. It preserves the ancestor when a scan cannot establish a safe result and distinguishes safe two-way, resolved two-way, and one-way policies. The comments explain why deletion-only differences can be handled differently from newly introduced content. [Reconciler implementation](https://github.com/mutagen-io/mutagen/blob/master/pkg/synchronization/core/reconcile.go)
- **C3:** Accelerated scans reuse watcher information or polling snapshots; full scans remain an alternative. The documentation explains that application-time checks still catch conflicting changes missed by an outdated scan. Filesystem probing separately handles executability and Unicode normalization behavior. [Probing and scanning](https://mutagen.io/documentation/synchronization/probing-and-scanning)

**Entry points:** `reconcile.go` and the probing/scanning design documentation.

### 4. [equalitie/ouisync](https://github.com/equalitie/ouisync)

**Language / role:** Rust library and CLI, with language bindings; encrypted peer-to-peer file repositories. The GUI lives elsewhere and is not counted separately.

Ouisync offers a distinct design in which a peer can help synchronize encrypted data without possessing permission to read it. Its storage representation is part of the synchronization protocol, rather than merely a cache of ordinary files.

- **C1:** Per-replica branches and snapshots represent concurrent histories. Signed Merkle-like snapshot roots authenticate encrypted blocks, and version vectors prevent an older snapshot from replacing a known newer one. The design also separates blind, read, and write capabilities and states its threat-model limits. [Technical paper](https://github.com/equalitie/ouisync/blob/master/doc/paper.md)
- **C2:** The repository exposes the engine as a Rust library with bindings, while repository access modes and share tokens support distinct replication and access arrangements. [Library organization](https://github.com/equalitie/ouisync/blob/master/README.md) and [repository model](https://github.com/equalitie/ouisync/blob/master/doc/paper.md)

**Entry points:** `doc/paper.md` and the library organization described in the README. The paper explicitly says it is explanatory documentation, not a formal specification.

## Cloud and desktop synchronization engines

### 5. [rclone/rclone](https://github.com/rclone/rclone)

**Language / role:** Go; multi-backend transfer and synchronization. Counted once, with emphasis on `sync`, `bisync`, and the filesystem interfaces.

Study how an engine accommodates providers with different capabilities instead of assuming every remote behaves like POSIX storage.

- **C1:** Bisync persists previous listings, distinguishes changed-versus-deleted cases, locks concurrent runs, supports access probes, and aborts excessive deletions. Its error handling can invalidate the trusted baseline and block subsequent runs; the manual explains recovery and concurrent-modification limitations. [Bisync operation](https://github.com/rclone/rclone/blob/master/docs/content/bisync.md)
- **C2:** The filesystem feature model makes differences explicit: case sensitivity, duplicate names, empty directories, costly hash/modtime queries, partial uploads, and optional server-side copy/move operations. These are operational contracts used across storage implementations. [Feature interfaces](https://github.com/rclone/rclone/blob/master/fs/features.go)

**Entry points:** `docs/content/bisync.md` and `fs/features.go`. Bisync's default size/time comparison is not equivalent to content comparison; the documentation describes that boundary.

### 6. [nextcloud/desktop](https://github.com/nextcloud/desktop)

**Language / role:** C++/Qt, with Swift Apple integration; Nextcloud desktop synchronization. Focus on `src/libsync` and the Apple File Provider subsystem.

Study synchronization as a desktop subsystem that must combine journals, discovery, propagation, conflict presentation, and virtual-file behavior. This codebase shares ownCloud ancestry; it is retained separately because its Nextcloud-specific conflict protocol and Apple synchronization package show substantive independent development.

- **C1:** Conflict tests simulate independent local and remote edits and verify conflict-copy behavior, including the server capability for uploading conflicts and associated conflict headers. The engine interface also documents delayed upload of still-changing files. [Conflict tests](https://github.com/nextcloud/desktop/blob/master/test/testsyncconflict.cpp) and [engine interface](https://github.com/nextcloud/desktop/blob/master/src/libsync/syncengine.h)
- **C2:** `NextcloudFileProviderKit` packages fetching, creation, modification, deletion, and virtual-file integration for Apple synchronization applications, alongside the main engine's discovery/journal/propagation boundaries. [File Provider package](https://github.com/nextcloud/desktop/blob/master/shell_integration/MacOSX/NextcloudFileProviderKit/README.md)

**Entry points:** `src/libsync/syncengine.h` and `test/testsyncconflict.cpp`; the linked Swift package provides a second platform-specific study path within the same repository.

### 7. [owncloud/client](https://github.com/owncloud/client)

**Language / role:** C++/Qt; ownCloud desktop synchronization. The current release line targets ownCloud Infinite Scale; older server compatibility must be assessed against the appropriate release.

This is useful for studying how remote discovery, local metadata, rename detection, and virtual files evolve with a server platform.

- **C1:** Discovery keeps deleted-item candidates available so a later rename match can cancel the deletion. Deleted-directory recursion is deferred until the remaining discovery establishes whether the directory was moved. Local information includes inode and virtual-file state, while remote information includes file IDs, etags, and permissions. [Discovery structures and invariants](https://github.com/owncloud/client/blob/master/src/libsync/discoveryphase.h)
- **C4:** The changelog covers multiple years of fixes and platform transitions. Recent entries document finer CfAPI locking, the removal of legacy suffix-based virtual files, and the compatibility transition from ownCloud 10 to Infinite Scale, including a separate update-channel strategy. [Changelog](https://github.com/owncloud/client/blob/master/CHANGELOG.md)

**Entry points:** `discoveryphase.h` and `CHANGELOG.md`. Shared ancestry with Nextcloud is acknowledged; these are separately evolved products, not duplicate mirrors.

### 8. [haiwen/seafile](https://github.com/haiwen/seafile)

**Language / role:** C; Seafile's synchronization client daemon. Despite the repository's broad project landing page, the server core and desktop GUI are separate repositories and are not included here.

Study the interaction between commit history, filesystem objects, block storage, and the client task state machine.

- **C1:** The daemon explicitly represents commit, fetch, merge, upload, cancellation, and error states, with per-library tracking for corruption, pending work, and deletion confirmation. The project describes conflict handling based on history. [Task/state definitions](https://github.com/haiwen/seafile/blob/master/daemon/sync-mgr.h) and [repository scope](https://github.com/haiwen/seafile/blob/master/README.markdown)
- **C3:** Filesystem objects are content-addressed and reusable across snapshots; files are divided using content-defined chunking. The data model connects this structure to deduplication across versions and incremental transfer. [Data model](https://manual.seafile.com/latest/develop/data_model/)

**Entry points:** `daemon/sync-mgr.h` and the data-model documentation. The latter describes the broader storage model; the daemon is the repository-specific implementation focus.

### 9. [abraunegg/onedrive](https://github.com/abraunegg/onedrive)

**Language / role:** D synchronization implementation, with Python test tooling; Linux client for Microsoft OneDrive. GitHub's aggregate language label is not a reliable description of the engine itself.

Study a cloud client's three distinct state domains: remote DriveItems, the last successfully applied SQLite baseline, and the live local filesystem.

- **C1:** The architecture requires the database to advance only after local application or remote commitment succeeds. Downloads validate private temporary content before replacement; resynchronization deliberately discards the historical baseline and consequently changes what can safely be inferred about deletions and conflicts. [Architecture](https://github.com/abraunegg/onedrive/blob/master/docs/client-architecture.md)
- **C3:** Remote enumeration can use Graph delta state, while monitor mode combines filesystem notifications, remote notifications, and scheduled reconciliation. Expected filesystem effects from the client's own operations are correlated with events to avoid interpreting every download or rename as fresh user activity. [Monitor and enumeration design](https://github.com/abraunegg/onedrive/blob/master/docs/client-architecture.md)

**Entry points:** `docs/client-architecture.md` and the D [sync engine](https://github.com/abraunegg/onedrive/blob/master/src/sync.d).

### 10. [cozy-labs/cozy-desktop](https://github.com/cozy-labs/cozy-desktop)

**Language / role:** JavaScript/Node.js; the repository now presents the product as **Twake Desktop**. The selected subsystem is `core`, not the graphical shell.

Study a synchronization pipeline organized around a local metadata database: filesystem events and remote CouchDB changes enter PouchDB, whose changes feed drives application to the opposite side.

- **C1:** The design separates normalized path identity from the path used for actual operations. The merge implementation handles path/ID collisions, file-versus-directory conflicts, deletion state, and events generated by conflict renames. [Core design](https://github.com/cozy-labs/cozy-desktop/blob/master/core/index.js) and [merge implementation](https://github.com/cozy-labs/cozy-desktop/blob/master/core/merge.js)
- **C2:** Local and remote sides feed a common metadata/merge mechanism and expose readable-stream transfer behavior. This makes event ingestion, normalization, reconciliation, and content movement separable engineering concerns. [Metadata workflow and side interfaces](https://github.com/cozy-labs/cozy-desktop/blob/master/core/index.js)

**Entry points:** `core/index.js` and `core/merge.js`. Platform comments should be read as the project's design assumptions, not a universal statement about every filesystem configuration.

### 11. [samschott/maestral](https://github.com/samschott/maestral)

**Language / role:** Python; Dropbox synchronization client. **Archived:** the README dates the maintenance shutdown to 2026-07-28.

Maestral remains a useful study of adapting a cloud API's coarse events to richer local filesystem events.

- **C1:** Remote revision IDs, content hashes, and local modification state determine whether a download is redundant, safe, or requires a conflict copy. Upload handling addresses selective-sync collisions, case conflicts, and file/folder replacement; the remote revision to replace is supplied to Dropbox. [Sync logic](https://github.com/samschott/maestral/blob/main/docs/background/sync_logic.rst)
- **C3:** Events are collapsed and hierarchically ordered; redundant descendant events are discarded for folder moves/deletions. Parallel file processing is separated from operations that require ordering, making the concurrency policy visible. [Event processing](https://github.com/samschott/maestral/blob/main/docs/background/sync_logic.rst)

**Entry points:** `docs/background/sync_logic.rst` and the [README's scope/archival notice](https://github.com/samschott/maestral/blob/main/README.md). The public Dropbox API used here does not provide the official client's binary-delta transfer feature.

### 12. [syncany/syncany](https://github.com/syncany/syncany)

**Language / role:** Java; encrypted folder synchronization over pluggable storage. **Archived, historical alpha:** the team explicitly states an indefinite hiatus and no expected maintenance.

Study how reconciliation can be implemented over storage that does not itself run a synchronization server.

- **C1:** The database reconciler compares branches using database-version headers and vector clocks, with deterministic tie-breaking for concurrent versions. Its implementation explains selection of a winning history and computation of the losing branch to prune and winning branch to apply. [Database reconciler](https://github.com/syncany/syncany/blob/develop/syncany-lib/src/main/java/org/syncany/operations/down/DatabaseReconciliator.java)
- **C2:** Storage plugins let the same synchronization/encryption machinery operate over FTP, SFTP, WebDAV, S3, and other storage types. The engine's database-history representation is separate from provider transport. [Project architecture and status](https://github.com/syncany/syncany/blob/develop/README.md)

**Entry points:** `DatabaseReconciliator.java` and the README. Retained as substantive historical architecture, with its alpha status preserved rather than presented as a deployment recommendation.

## Cluster replication and event-driven coordination

### 13. [LINBIT/csync2](https://github.com/LINBIT/csync2)

**Language / role:** C; asynchronous multi-host file synchronization for clusters and server farms. It is distinct from the similarly named client-only csync project.

Study persistent per-peer work tracking and synchronization groups rather than only pairwise directory comparison.

- **C1:** Each host compares its filesystem to a local metadata database. Dirty records preserve outstanding updates for unreachable peers; a separate action table preserves scheduled actions across interruption. Concurrent dirty versions cause a conflict unless policy resolves it, while removals can be recognized from history. [Algorithm and database schema](https://github.com/LINBIT/csync2/blob/master/doc/csync2.adoc)
- **C2:** Synchronization groups combine host sets, include/exclude rules, path prefixes, conflict policy, and post-update actions. This supports overlapping replication topologies and configuration deployment without requiring every host to share the same entire tree. [Group model](https://github.com/LINBIT/csync2/blob/master/doc/csync2.adoc)

**Entry point:** `doc/csync2.adoc`. Its documented scope favors infrequently modified configuration/application files; it explicitly distinguishes this from synchronously replicating a live database.

### 14. [lsyncd/lsyncd](https://github.com/lsyncd/lsyncd)

**Language / role:** Lua and C; one-way live mirroring driven by filesystem events. **Maintenance caveat:** the README says the project needs a new maintainer and is up for adoption.

Study how a small operating-system-facing core can support a configurable synchronization scheduler.

- **C2:** C handles monitoring, process management, signals, pipes, logging, and alarms; Lua handles the higher-level logic. Cascading configuration layers allow custom actions without embedding all policy in the native core. [Developer architecture](https://github.com/lsyncd/lsyncd/blob/master/docs/appendices/devdocs/index.md)
- **C3:** Events are aggregated before external synchronization processes are launched. Its rsync-plus-SSH action can execute remote renames instead of retransmitting moved files; the developer document also explains replacing linear-list work with Lua hash tables. [Operation and scope](https://github.com/lsyncd/lsyncd/blob/master/README.md)

**Entry points:** developer architecture and README. Lsyncd explicitly disallows composing opposing mirrors into a bidirectional synchronizer because writes can feed back and overwrite newer data.

### 15. [clsync/clsync](https://github.com/clsync/clsync)

**Language / role:** C; filesystem-event aggregation and external synchronization coordination for Linux/FreeBSD. **Historical/dormant:** GitHub metadata reports the last push in July 2021; current maintenance is not assumed.

Study event scheduling under filesystem monitoring constraints and the boundary between detecting changes and executing a transfer.

- **C2:** Monitoring, filtering, event indexing, and invocation of an external synchronizer are separate stages. The transfer endpoint can be rsync or another handler, while the repository includes several operating-system monitoring implementations. [Developer walkthrough](https://github.com/clsync/clsync/blob/master/DEVELOPING) and [project scope](https://github.com/clsync/clsync/blob/master/README.md)
- **C3:** The documented execution loop aggregates events into hash tables and distinguishes normal, large-file, and immediate queues before preparing inclusion/exclusion lists and invoking synchronous or threaded handlers. These are concrete scheduling mechanisms for controlling work. [Queue and execution flow](https://github.com/clsync/clsync/blob/master/DEVELOPING)

**Entry points:** `DEVELOPING` and the README. The developer walkthrough itself warns it may be outdated; use it as an orientation aid, not a current formal specification.

### 16. [deajan/osync](https://github.com/deajan/osync)

**Language / role:** Bash; stateful bidirectional synchronization built on rsync. Included because it implements reconciliation/recovery policy beyond merely constructing an rsync command.

Study the costs of implementing a restartable synchronization workflow in shell across heterogeneous Unix-like environments.

- **C1:** The main `Sync` function records progress independently for initiator and target. Its staged workflow computes current/deleted lists, handles conflicts and attributes, updates replicas, propagates deletions, and finally records post-run state. Resume logic returns to recorded steps after failures. [Implementation](https://github.com/deajan/osync/blob/master/osync.sh)
- **C4:** The 2018–2023 changelog documents race fixes, remote locking, filename edge cases, configuration-upgrade support, retained boolean syntax compatibility, and adaptation to a newer rsync protocol. This is evidence of managing real compatibility and failure complexity over time. [Changelog](https://github.com/deajan/osync/blob/master/CHANGELOG.md)

**Entry points:** the nine-step `Sync` function in `osync.sh` and `CHANGELOG.md`. The project's soft-delete/conflict-backup policy is an engineering mechanism, not a guarantee against every possible loss scenario.

## Delta transfer and file reconstruction

### 17. [RsyncProject/rsync](https://github.com/RsyncProject/rsync)

**Language / role:** C; incremental file/tree transfer, normally with a source-to-destination direction rather than bidirectional conflict reconciliation.

Study the concrete generator → sender → receiver pipeline around the remote-difference algorithm.

- **C1:** The receiver reconstructs a file from literals and references to the existing basis, verifies the resulting whole-file checksum, and normally replaces the basis through a temporary file. Protocol version affects interpretation of the contextual byte stream, making compatibility part of correctness. [Implementation overview](https://rsync.samba.org/how-rsync-works.html)
- **C3:** The generator produces block signatures, the sender uses rolling checksums to locate reusable blocks at shifted offsets, and independent processes overlap work. The overview discusses CPU-heavy matching versus disk-heavy reconstruction and cache/seek behavior. [Process and resource model](https://rsync.samba.org/how-rsync-works.html)

**Entry point:** [How Rsync Works](https://rsync.samba.org/how-rsync-works.html). This is a conceptual and historical implementation guide; particular options, such as in-place operation, require checking current source/manual behavior rather than generalizing its default replacement description.

### 18. [librsync/librsync](https://github.com/librsync/librsync)

**Language / role:** C; reusable signature/delta/patch library. A synchronization building block, not a complete directory synchronizer or an implementation of rsync's wire protocol.

Study how to embed delta processing inside a host application's own I/O and scheduling model.

- **C1:** Operations are explicit resumable state machines. Suspension points must either complete or restart without losing information, and completion must flush pending output before reporting success. Those invariants make buffer-boundary and partial-progress handling worth studying. [Streaming API and internals](https://github.com/librsync/librsync/blob/master/doc/streaming.md)
- **C2:** Opaque jobs and caller-provided buffers separate signature creation, signature loading, delta generation, and patch application from networking and filesystem metadata. The host can integrate nonblocking streams and provide basis-file access. [Streaming interfaces](https://github.com/librsync/librsync/blob/master/doc/streaming.md)

**Entry points:** `doc/streaming.md` and the [README's explicit scope boundaries](https://github.com/librsync/librsync/blob/master/README.md). Higher layers remain responsible for filenames, permissions, directory structure, transport, and conflict policy.

### 19. [google/cdc-file-transfer](https://github.com/google/cdc-file-transfer)

**Language / role:** C++; incremental transfer and streaming tools originating in Stadia development workflows. **Archived.** Counted once, with emphasis on `cdc_rsync` and shared chunking machinery rather than treating its tools as independent repositories.

Study content-defined chunking as an alternative way of structuring remote difference discovery for large development assets.

- **C2:** The chunker exposes streaming `Process`/finalization behavior, a chunk callback, and configurable minimum, target, and maximum sizes. Its comments explain hash-width and boundary-selection choices, making the algorithm reusable beyond one CLI. [Chunker implementation](https://github.com/google/cdc-file-transfer/blob/main/fastcdc/fastcdc.h)
- **C3:** The architecture computes content-defined chunks so insertions do not shift all later boundaries, then matches chunk identities and transfers differences with compression. The source discusses the tradeoff between hash representation, boundary selection, and deduplication. [Design discussion](https://github.com/google/cdc-file-transfer/blob/main/README.md)

**Entry points:** `fastcdc/fastcdc.h` and the README's algorithm discussion. The report does not generalize the project's published benchmark ratios to other workloads.

### 20. [oll3/bita](https://github.com/oll3/bita)

**Language / role:** Rust; HTTP-based differential file reconstruction, with reusable `bitar` library. Especially relevant to image/embedded-system updates; it is not a directory conflict resolver.

Study how a prepared chunk archive lets a client reconstruct a target using arbitrary local seed files and an ordinary HTTP range server.

- **C1:** Output reconstruction uses verified chunks and a chunk-location index. In-place reordering distinguishes safe copies from chunks that must first be held in memory so their source bytes survive another write. [Clone output implementation](https://github.com/oll3/bita/blob/main/bitar/src/clone_output.rs)
- **C3:** The archive dictionary identifies reusable chunks, avoiding a separate patch for every source/target version pair. Adjacent missing chunks can be fetched together, and chunks already at the correct output offset avoid redundant writes. [Archive/clone architecture](https://github.com/oll3/bita/blob/main/README.md)

**Entry points:** `bitar/src/clone_output.rs` and the README's compression/cloning sections. In-place reconstruction is a different failure model from atomic whole-file replacement; no crash-atomicity claim is made here.

### 21. [cph6/zsync](https://github.com/cph6/zsync)

**Language / role:** Go in the current tree; the original author's zsync implementation, now rewritten from its older implementation. Client-driven differential download using HTTP and a published control file.

Study moving difference discovery onto the downloader while keeping the server a conventional file host.

- **C1:** The control-file specification defines block checksums, reconstruction metadata, a final whole-file verification step, and filename handling intended to prevent writing outside an expected directory. It distinguishes format requirements from the client's choice of reconstruction algorithm. [Format and reconstruction contract](https://github.com/cph6/zsync/blob/master/SPEC.md)
- **C3:** Clients reuse blocks from older or related local files and fetch only missing ranges; publishers generate the control file once for many downloaders. The server need not compute per-client deltas. [System overview](https://github.com/cph6/zsync/blob/master/SPEC.md)
- **C4:** The release history documents the rewrite, explicit old-control-file compatibility, backward-compatibility integration tests, and removal of specialized gzip logic to reduce complexity. [Evolution and compatibility](https://github.com/cph6/zsync/blob/master/NEWS)

**Entry points:** `SPEC.md` and `NEWS`. The README describes limited development activity, and the specification/API remain pre-1.0; a recent push alone is not treated as a maintenance guarantee.

## Search coverage and limitations

Discovery used live web search with more than six distinct formulations, including bidirectional conflict/reconciliation engines; Rust delta synchronization; C++ cloud-client architecture; cluster replication with csync2/lsyncd; Python cloud clients; Java/encrypted synchronization; rsync/librsync/HTTP delta delivery; and targeted Seafile and Mutagen architecture queries. Searches found both established systems and smaller projects such as Ouisync, clsync, osync, bita, and zsync's current implementation. Follow-up searches increasingly returned the same families, small replacements, or adjacent database/storage projects.

Canonical owner/repository URLs and default branches were verified through GitHub pages or the GitHub repository API. For every retained repository, additional primary material was opened and read, including implementation comments, algorithms, architecture documentation, tests, or release notes; a second rendering of a README was not counted as independent evidence. Repository metadata was also checked for archival status. Non-archived status is not asserted to mean active maintenance. Source links generally follow the inspected default branch and can change after this research date.

The selection intentionally excludes general synchronization frameworks such as the database-oriented DeltaSync results and OpenDAL's storage-access abstraction; backup-first tools and kernel/block replication systems are adjacent categories. Small rsync launchers and GUI-only clients add little independent engine architecture. Pydio Cells Sync, DTSync, and Mirror were considered during discovery but not retained in this bounded selection; their omission is not a finding that their implementations lack merit. Recent Rust replacements surfaced in searches, but broad safety/performance claims without sufficiently inspected supporting material were not used to pad the list.

Nextcloud and ownCloud are the sole deliberately related lineage pair retained: their cited current subsystems and release histories show substantive separate evolution. No unofficial mirror is substituted for a departed upstream. Archived Syncany, Maestral, and CDC File Transfer, dormant clsync, and Lsyncd's maintainer request are called out because historical engineering value and present deployment suitability are different judgments.

This was read-only source/documentation research: no candidate was cloned, installed, built, benchmarked, or tested. Evidence supports the stated study topics and criteria, not a security audit or a universal data-loss guarantee. The list is strongest on desktop/Unix/cloud synchronization and delta transfer; proprietary engines and mobile-only clients are not comprehensively covered.
