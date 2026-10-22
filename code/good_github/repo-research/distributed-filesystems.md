# Distributed filesystems

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories that implement distributed file namespaces, parallel filesystems, or substantial filesystem layers over distributed storage. It includes persistent POSIX-oriented clusters, object-backed filesystems, batch-oriented systems, ephemeral HPC storage, wide-area caching, and decentralized file graphs. These systems deliberately offer different consistency and durability contracts; a familiar file API does not imply identical POSIX semantics. In larger monorepos, the relevant filesystem subsystem is identified and the repository is counted once.

The criteria below describe study value, not a production endorsement or a claim that every component is exemplary. Architectural facts come from the linked primary material; judgments about what an engineer can learn are grounded in those facts.

- **C1 — Difficult correctness:** invariants, concurrency, adversarial inputs, consistency, or failure recovery that require careful reasoning.
- **C2 — Reusable abstractions:** substantial interfaces and components supporting multiple workloads, policies, backends, or integrations.
- **C3 — Performance with structure:** concrete I/O, network, memory, or scaling constraints addressed through understandable architectural choices.
- **C4 — Sustained evolution:** years of changes accompanied by evidence of compatibility work, testing, or complexity management. Age or a recent push alone does not qualify.

## Shared POSIX-oriented clusters

### 1. [ceph/ceph](https://github.com/ceph/ceph)

**Language / role:** C++, with Python tooling; study **CephFS**, its metadata servers and clients, and their relationship to RADOS within the storage monorepo.

CephFS is useful for understanding how a coherent file namespace can sit above a distributed object store without routing file contents through metadata servers. The [CephFS architecture](https://docs.ceph.com/en/latest/cephfs/index.html) describes separate metadata and data pools, a resizable metadata-server cluster, direct client data I/O, and metadata journaling to RADOS.

- **C1:** Clients and metadata servers cooperatively maintain a distributed metadata cache, with the MDS acting as authority. Mutations must remain consistent with the journal and other clients' cached state; this is a concrete distributed coherence and recovery problem.
- **C3:** Separating direct RADOS data access from namespace operations removes a metadata gateway from the bulk-data path. Aggregating metadata mutations into journal writes addresses a different bottleneck explicitly.

**Entry points:** the architecture above and the verified [`src/mds` implementation](https://github.com/ceph/ceph/tree/main/src/mds). The linked documentation is the development-version documentation, rather than a promise about every supported release.

### 2. [gluster/glusterfs](https://github.com/gluster/glusterfs)

**Language / role:** C; distributed filesystem built from composable translators operating on storage bricks.

The unusually instructive part is the correspondence between normal filesystem operations and the replication translator's distributed transactions. The [AFR replication design](https://docs.gluster.org/en/latest/Administrator-Guide/Automatic-File-Replication/) explains readable replica selection, dirty and pending extended attributes, quorum, and self-healing.

- **C1:** A write has lock, pre-operation, filesystem-operation, post-operation, and unlock phases. Extended attributes record interrupted or partially successful changes so repair can distinguish good replicas from replicas needing data, metadata, or directory-entry healing.
- **C2:** Translators implement a common filesystem-operation interface. AFR applies its transaction machinery to writes, renames, attributes, and other operations instead of baking replication into one application-specific storage API.
- **C3:** The same design documents lock piggybacking, eager locking, and delayed post-operations, exposing how performance optimizations complicate an otherwise understandable transaction protocol.

**Entry point:** the AFR document above, which supplies a concrete reading map into translator operations such as `afr_writev`.

### 3. [moosefs/moosefs](https://github.com/moosefs/moosefs)

**Language / role:** C; master/chunkserver filesystem with Unix-style clients.

MooseFS provides a comparatively direct way to study namespace management separately from chunk placement and repair. Its [architecture documentation](https://moosefs.com/architecture) distinguishes the open-source Community architecture from Pro, an important distinction when reading claims about metadata availability.

- **C1:** Per-file or per-directory redundancy policies drive replication and recreation of missing copies after storage failures. Metaloggers retain metadata copies, but Community master recovery still requires an operator; automatic Pro master failover must not be attributed to this repository's Community offering.
- **C3:** Clients obtain chunk locations from the master and then transfer data directly to chunkservers. Parallel chunk I/O and replication avoid carrying file contents through the namespace authority.

**Entry points:** the architecture above and its linked [Design & Architecture chapter](https://docs.moosefs.com/design-and-architecture/). The inspected architecture also distinguishes Community single-parity erasure coding from Pro's wider parity options; older comparisons that describe all erasure coding as proprietary can be misleading.

### 4. [lizardfs/lizardfs](https://github.com/lizardfs/lizardfs)

**Language / role:** C++; distributed chunk filesystem. **Official GitHub mirror**, explicitly identified as such by its README.

LizardFS is a substantive MooseFS derivative rather than another copy of the same project. Its [FAQ](https://lizardfs-docs.readthedocs.io/en/latest/faq/general.html) confirms the fork, while the [architecture and replication-mode documentation](https://lizardfs-docs.readthedocs.io/en/latest/introduction.html) describes shadow metadata servers, standard replication, XOR, and Reed–Solomon modes.

- **C1:** Metadata shadows must track the active master, and file chunks can have different recovery schemes. The write path differs materially between chained replicated writes and client-distributed erasure-coded writes, as the FAQ explains.
- **C2:** Per-file and per-directory goals combine placement policy with multiple redundancy modes. The handbook also explains a tape-storage path whose read-only treatment and explicit restoration expose useful abstractions for heterogeneous storage.

**Entry points:** the two documentation pages above. **Activity caveat:** the [repository API](https://api.github.com/repos/lizardfs/lizardfs) reported its last push in August 2024 and did not mark it archived. Treat it as a valuable established implementation to study; this report does not infer current support from the mirror's existence.

### 5. [leil-io/leilfs](https://github.com/leil-io/leilfs)

**Language / role:** C++; LeilFS, formerly SaunaFS, in the MooseFS/LizardFS lineage. The old `leil-io/saunafs` URL redirects here; it is counted only once.

This derivative warrants a separate entry because its [release history](https://github.com/leil-io/leilfs/blob/dev/NEWS) records substantial independent work: FoundationDB integration, a metadata group-commit pipeline, new transaction machinery, chunk locking, and write batching. The [master architectural reference](https://github.com/leil-io/leilfs/blob/dev/src/master/README.md) maps these concerns to concrete interfaces and source-file groups.

- **C1:** The master models open-but-unlinked files separately from trash, delays inode reuse to protect stale handles, tracks advisory locks, and increments a metadata version on mutations. These invariants connect namespace semantics to recovery and external clients.
- **C2:** Interfaces such as `IMetadataBackend`, `IKVConnector`, and filesystem-operation interfaces separate the metadata model from persistence and extensions.
- **C3:** Documented group commits and multi-buffer write batching address metadata commit overhead and storage throughput. Release notes also record races and cache invalidation fixes, making the costs of these changes visible.

**Entry points:** the master reference and `NEWS` above. The development branch contains evolving features; release notes should be checked before attributing a feature to a deployed version.

### 6. [cubefs/cubefs](https://github.com/cubefs/cubefs)

**Language / role:** Go; distributed file and object storage, with the filesystem metadata and replicated-data subsystems most relevant here.

CubeFS offers a useful contrast to a single metadata authority. Its [architecture](https://cubefs.io/docs/master/overview/architecture.html) divides the system into resource management, metadata partitions, replicated or erasure-coded data, and protocol gateways.

- **C1:** A metadata partition owns an inode range and maintains inode and dentry B-trees, replicated through Multi-Raft. Correctness therefore spans replicated namespace state, partition ownership, and the independent data-placement layer.
- **C2:** A volume groups metadata and data partitions into a filesystem instance, while the object view maps a volume to a bucket. This gives a concrete example of shared storage abstractions serving POSIX, HDFS, and S3 access.
- **C3:** Metadata partitions and data nodes scale separately, and the data subsystem offers both replica groups and erasure-coded stripes. Engineers can study how distinct durability and access patterns fit a common management plane.

**Entry point:** the architecture page above. It establishes component boundaries; it should not be read as proof that every protocol has identical concurrency semantics.

## Object-backed filesystems and distributed caching

### 7. [juicedata/juicefs](https://github.com/juicedata/juicefs)

**Language / role:** Go; filesystem clients combining an external metadata engine with object storage.

The [Community architecture](https://juicefs.com/docs/community/architecture/) is particularly useful for studying random file modification over immutable object-sized storage. It distinguishes logical chunks, slices representing writes, and physical blocks stored in object storage and cache.

- **C1:** Overlapping slices must return the latest written data for every byte range, while gaps, truncation, reference counts, and compaction interact with metadata. The document explains valid slice ranges and warns that aggressive metadata caching changes consistency behavior.
- **C2:** Metadata engines and object stores are separate replaceable components. FUSE, Hadoop, Python, and gateway integrations reuse that file model.
- **C3:** Blocks enable concurrent upload, while asynchronous compaction reduces the read and metadata costs of fragmented, overlapping writes. The representation explains the tradeoff rather than merely claiming fast cloud access.

**Entry point:** the Community architecture above. Community sources are the scope of this entry; enterprise and hosted-service behavior should be evaluated separately.

### 8. [seaweedfs/seaweedfs](https://github.com/seaweedfs/seaweedfs)

**Language / role:** Primarily Go; study the **filer and mounted filesystem** over the distributed volume store. The former `chrislusf` owner is not a separate project.

SeaweedFS is instructive because its master tracks volumes rather than every file, while filers add names and directories using a separate metadata store. The repository's architecture explanation and [production topology document](https://github.com/seaweedfs/seaweedfs/blob/master/note/slides/seaweedfs-production-setup.md) distinguish the read/write path from maintenance work.

- **C2:** The filer separates namespace storage from volume storage and accepts different database backends. File and object frontends can reuse these layers rather than each implementing placement and storage.
- **C3:** Small blobs are packed into append-only volume files, clients cache volume locations, and bulk data bypasses the master after lookup. Background balancing, vacuum, and coding run through separate administration and worker components.
- **C1:** Master quorum, volume replication, and erasure-coded shard placement involve different failure boundaries. The deployment document makes those boundaries explicit instead of treating extra frontend processes as sufficient for durability.

**Entry point:** the production topology above, read alongside the repository's architecture section. This entry does not treat its POSIX-like filer as a blanket claim of full POSIX equivalence.

### 9. [opencurve/curve](https://github.com/opencurve/curve)

**Language / role:** C++; **CurveFS** in a monorepo that also contains CurveBS block storage.

The [CurveFS design](https://github.com/opencurve/curve/blob/master/docs/cn/curvefs_architecture.md), in Chinese, describes a FUSE client, a metadata cluster, and data stored either in S3-compatible storage or CurveBS. The filesystem is the reason for inclusion, not the block service alone.

- **C1:** Metadata partitions cover inode ranges, directory entries live with their parent-directory partition, and Raft copysets manage replication. The design walks through path lookup and separates etcd-based management failover from metaserver replication.
- **C2:** One namespace layer supports two substantially different data models: extents within a CurveBS volume and chunk/block mappings into object-store keys.
- **C3:** Clients contain memory and disk caching, while independently managed metadata and data clusters address separate scaling limits.

**Entry point:** the CurveFS design above. **Activity caveat:** the [API](https://api.github.com/repos/opencurve/curve) reported an August 2024 last push, without an archive flag. The report treats the available code and design as study material and does not assert ongoing maintenance or completed implementation of every roadmap item.

### 10. [datenlord/datenlord](https://github.com/datenlord/datenlord)

**Language / role:** Rust; cloud-oriented distributed filesystem and caching platform, including asynchronous FUSE and storage layers.

DatenLord adds a useful language and implementation contrast to the C/C++ and Go systems. The inspected code is more concrete evidence than the README's broad hardware and deployment ambitions: [`VirtualFs`](https://github.com/datenlord/datenlord/blob/master/src/fs/virtualfs.rs) defines asynchronous file operations, and [`StorageManager`](https://github.com/datenlord/datenlord/blob/master/src/storage/storage_manager/manager.rs) translates file ranges into storage blocks.

- **C2:** `VirtualFs` isolates filesystem operations from FUSE transport details, while `StorageManager<S>` accepts a generic storage implementation. These are reusable boundaries across namespace, cache, and persistence work.
- **C3:** Block loads and stores run concurrently through Tokio tasks; the manager tracks cache modification times and invalidates stale file caches before access. Partial-block handling and truncation are visible in one reading-sized module.
- **C1:** Empty operations, byte-to-block boundaries, dirty state, invalidation, and shrinking files all require consistent treatment. Several optional filesystem methods explicitly return unimplemented errors, so the trait's surface is not evidence that every POSIX feature works.

**Entry points:** the two source files above.

### 11. [Alluxio/alluxio](https://github.com/Alluxio/alluxio)

**Language / role:** Java; virtual distributed filesystem and caching layer for analytics, rather than the final durable storage system.

The [open-source architecture](https://github.com/Alluxio/alluxio/blob/main/docs/en/overview/Architecture.md) explains masters, workers, clients, under-filesystems, and a separate job service. The repository README explicitly distinguishes this public analytics-oriented edition from the enterprise architecture.

- **C2:** Under-filesystem integrations and a common namespace let computation frameworks use heterogeneous backing stores. A reusable job service handles loading, persistence, replication, and movement as separate operations.
- **C1:** The leading master journals filesystem state, standby masters reconstruct it, and failover selects a new authority. Distinguishing a standby from a checkpoint-only secondary master is an especially useful correctness lesson.
- **C3:** Application data bypasses the master, workers provide caching near computation, and heavyweight operations are moved to job workers to preserve metadata-serving capacity.

**Entry point:** the architecture document above. It explicitly says Alluxio is not itself persistent storage; cached copies and backing-store persistence must be reasoned about separately.

## Large-file and batch-oriented storage

### 12. [apache/hadoop](https://github.com/apache/hadoop)

**Language / role:** Java, with native clients; **HDFS** under `hadoop-hdfs-project`, counted once within Apache Hadoop's GitHub source mirror.

The [HDFS architecture](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html) provides a detailed study of a filesystem designed around large sequential files and hardware failures. Its single-writer, append/truncate-oriented model is an explicit workload choice.

- **C1:** Heartbeats, block reports, checksums, stale replicas, safe mode, and re-replication interact with namespace persistence through the edit log and filesystem image. Recovery cannot be reduced to copying a missing block without understanding metadata state.
- **C3:** Rack-aware replica placement trades write-network cost against failure isolation. Pipelined replication, nearby replica selection, and direct DataNode access expose how that policy affects the data path.
- **C2:** Pluggable block-placement policies and distinct filesystem clients let the same underlying service support different cluster topologies and consumers.

**Entry points:** the architecture above and [`hadoop-hdfs-project`](https://github.com/apache/hadoop/tree/trunk/hadoop-hdfs-project). The opened `stable` design page identifies itself as version 3.3.5; use it for architectural fundamentals, not as a claim about the latest release or all current features.

### 13. [quantcast/qfs](https://github.com/quantcast/qfs)

**Language / role:** C++; Quantcast File System for large sequential files and batch processing.

QFS is a substantial alternative to HDFS, with a metaserver, chunkservers, and a client library. Its [technical introduction](https://github.com/quantcast/qfs/blob/master/wiki/Introduction-To-QFS.md) explains stale-chunk versioning with a concrete failure example, leases, checksums, atomic append, and Reed–Solomon storage.

- **C1:** Restarted chunkservers can report obsolete chunk versions after missing writes. The metaserver must reject stale contents, while client failover and atomic replicated append preserve the relevant file contract.
- **C3:** Direct I/O, client write-back caching, metadata caching, and erasure coding address CPU, lookup, and capacity costs through identifiable components.
- **C2:** Per-file replication, striping, recovery modes, storage tiers, and optional S3-backed data expose policy choices behind the same filesystem API.

**Entry point:** the technical introduction above. Its limitations are valuable: erasure-coded files have restricted random rewrites, and simultaneous reads and writes to the same unstable chunk are not a general supported workflow. The README separately records Java, Python, Hadoop, and platform compatibility work across releases.

## Parallel, HPC, and high-throughput training filesystems

### 14. [lustre/lustre-release](https://github.com/lustre/lustre-release)

**Language / role:** C; parallel filesystem with kernel clients, metadata services, object-storage targets, and LNet. **Substantive GitHub mirror of the official Whamcloud development repository**, as identified on the repository page.

[Understanding Lustre Internals](https://wiki.lustre.org/Understanding_Lustre_Internals) supplies an unusually detailed component map, following operations through metadata and object clients, layout layers, RPC, and backend abstractions.

- **C2:** `obdclass` and the object-storage-device abstraction organize a large implementation around interchangeable component operations and backing filesystems such as ldiskfs and ZFS.
- **C3:** A file's layout stripes data across targets, allowing concurrent access to different storage servers. Metadata services, bulk-data services, and LNet have distinct responsibilities, making aggregate throughput understandable from the architecture.
- **C1:** Parallel access is coupled with coherent namespace operations, recovery machinery, and online LFSCK. The internals document explains management-client participation in log handling and distributed locking.

**Entry point:** the internals guide above, which links its descriptions to source. It spans historical and newer components; individual version assumptions matter when tracing current code.

### 15. [ThinkParQ/beegfs](https://github.com/ThinkParQ/beegfs)

**Language / role:** C++ servers and C kernel-client code; BeeGFS parallel cluster filesystem.

The [architecture guide](https://doc.beegfs.io/latest/architecture/overview.html) gives a clear account of striped file contents, distributed metadata, a kernel client, and userspace services. It also explains placement under low-space conditions rather than stopping at a diagram.

- **C3:** Clients contact multiple storage servers directly and simultaneously; metadata can also be distributed across servers. This separates bulk bandwidth from directory-lookup latency.
- **C2:** Storage pools group targets by storage class, while capacity pools classify available space and guide target selection. These policies support heterogeneous disks and workloads without changing the client file interface.
- **C1:** Placement must fall back from normal to low-space and emergency targets when a requested stripe pattern cannot otherwise be satisfied. This is a concrete invariant around usable allocation, rather than a generic scalability claim.

**Entry point:** the architecture guide above. The repository is a public source distribution; its commit count should not be mistaken for the full amount of upstream engineering history.

### 16. [waltligon/orangefs](https://github.com/waltligon/orangefs)

**Language / role:** C; official PVFS/OrangeFS repository for cluster parallel I/O.

OrangeFS is worth studying for its explicit decomposition of network I/O, storage I/O, request processing, and data movement. The repository's [flow design](https://github.com/waltligon/orangefs/blob/master/doc/design/flow-design.tex) defines transfers between memory, network, and storage endpoints and separates the transfer description from the protocol that executes it.

- **C2:** Flow descriptors and protocol interfaces abstract endpoint combinations, buffering, scheduling, and MPI-like file/memory datatypes. The same machinery can serve client and server transfers.
- **C3:** One operation can issue concurrent flows to several servers, while a scheduler accounts for network and disk activity together. This is a concrete architecture for overlapping I/O and supporting noncontiguous requests.
- **C1:** Descriptor ownership changes while a transfer is active; callers must not mutate an in-flight descriptor. Completion and trailing write acknowledgements mark different stages of progress.

**Entry point:** the flow design above. **Documentation caveat:** it is a historical PVFS design document, and the repository README warns that developer documents may lag current code. Use it as a design map and check current implementation details before relying on old protocol specifics.

### 17. [daos-stack/daos](https://github.com/daos-stack/daos)

**Language / role:** Primarily C, with a Go control plane; **DFS, DFuse, and I/O interception** over the DAOS distributed storage stack.

The [filesystem guide](https://docs.daos.io/master/user/filesystem/) explains how `libdfs` provides a hierarchical namespace inside a DAOS container and how DFuse exposes it to ordinary applications. This filesystem layer, not merely the underlying object store, establishes category fit.

- **C1:** The guide explicitly distinguishes conflicting create/unlink/rename operations, interrupted-operation atomicity, and write visibility. It also documents open-unlink behavior and filesystem checking for orphaned objects.
- **C2:** Native DFS, DFuse, and interception share the same stored file data, allowing different applications to use different access paths.
- **C3:** Interception can bypass the FUSE/kernel data path; event-queue threads and request threads expose resource and concurrency tradeoffs.

**Entry point:** the filesystem guide above. **Semantic limitation:** the inspected documentation says relaxed consistency is the default and balanced mode is not fully supported. It also lists unsupported or restricted POSIX features, including hard links and cross-client append behavior. Do not summarize this as an unrestricted POSIX replacement.

### 18. [llnl/UnifyFS](https://github.com/llnl/UnifyFS)

**Language / role:** C; ephemeral shared filesystem over node-local storage for HPC jobs.

The [overview and high-level design](https://github.com/llnl/UnifyFS/blob/dev/docs/overview.rst) describe a client library that intercepts application I/O and a server on each allocated compute node, communicating through Mochi. Its lifetime and API restrictions are central to the design.

- **C3:** Checkpoint/restart and bulk-synchronous workloads can use local storage across the allocation, with application interception avoiding a mandatory conventional system mount.
- **C1:** The [limitations and consistency guide](https://github.com/llnl/UnifyFS/blob/dev/docs/limitations.rst) requires writers to flush and applications to synchronize before readers observe their data. It connects these rules to MPI-I/O synchronization and explicitly excludes file locking and directory operations.
- **C2:** Linked applications and higher-level I/O libraries can share the namespace, while persistence uses a separate staging API or utility.

**Entry points:** the two documents above. Data must be copied to permanent storage before the server processes end. The [API](https://api.github.com/repos/llnl/UnifyFS) reported a September 2025 last push; README wording alone was not treated as proof of current development activity.

### 19. [deepseek-ai/3FS](https://github.com/deepseek-ai/3FS)

**Language / role:** C++; Fire-Flyer File System for disaggregated SSD storage, RDMA networks, and training/inference I/O.

The [design notes](https://github.com/deepseek-ai/3FS/blob/main/docs/design_notes.md) connect workload requirements to metadata transactions, chunk placement, chain replication, and the costs of the FUSE path.

- **C1:** CRAQ separates write propagation from reads across replicas. Metadata uses transactional key-value storage, with conflict retries and directory-ancestor checks needed to prevent cycles during moves.
- **C3:** The native interface uses shared memory regions and ring buffers, batches small requests, and permits asynchronous zero-copy data operations while retaining FUSE for metadata. This gives a clear example of identifying and bypassing a specific I/O bottleneck.
- **C2:** Per-directory chunk and stripe settings support different file layouts, and both FUSE and native clients serve the shared file model.

**Entry point:** the design notes above. They also document semantic compromises, including not tracking read-only open descriptors in the same way as a local filesystem. Published benchmark numbers are intentionally not repeated as general performance guarantees.

### 20. [oss-tsukuba/gfarm](https://github.com/oss-tsukuba/gfarm)

**Language / role:** C; Gfarm cluster and wide-area filesystem with explicit replica-location control.

Gfarm broadens the selection beyond the usual cloud-storage projects. Its [implementation overview](https://github.com/oss-tsukuba/gfarm/blob/2.8/OVERVIEW.en) describes filesystem nodes that can also be clients, a metadata server with a replica catalog, and a library for file access, replication, and file-affinity scheduling.

- **C2:** `libgfarm`, metadata service `gfmd`, and storage daemon `gfsd` separate namespace and placement from remote file operations. FUSE and integrations such as Hadoop and Samba expose these facilities to different application environments.
- **C3:** Replica placement and locality reduce access concentration and distant transfers. The [release notes](https://github.com/oss-tsukuba/gfarm/blob/2.8/RELNOTES) specifically record nearest-source replica scheduling improvements.
- **C4:** The same notes show dated 2023–2026 evolution with older-protocol compatibility, authentication compatibility repairs, sanitizer-driven fixes, and large-transfer corrections. That is concrete maintenance evidence beyond repository age.

**Entry points:** `OVERVIEW.en` and `RELNOTES` above. The default source branch was `2.8` when checked.

## Wide-area, disconnected, and decentralized filesystems

### 21. [openafs/openafs](https://github.com/openafs/openafs)

**Language / role:** C; Andrew File System implementation. **Officially linked GitHub mirror**: the project's [source-access page](https://openafs.org/pages/cvs.html) directs browser users here while identifying the upstream Git/Gerrit workflow.

OpenAFS is valuable for studying a namespace that crosses independently administered cells and a cache-coherence design based on callbacks. The [administration guide's architectural concepts](https://docs.openafs.org/AdminGuide/HDRWQ7.html) explain cells, volumes, transparent location, caching, and replication.

- **C1:** A server breaks callbacks when cached content becomes obsolete. Writable files use per-file callbacks, while read-only replicated volumes can use a callback for the whole volume; publication of a new volume version invalidates the old promise.
- **C2:** Volumes act as independently movable, replicated, quota-controlled units beneath a uniform namespace. Cells provide an administrative boundary without forcing applications to embed individual server locations.
- **C3:** Local caching avoids repeat network fetches, and volume-level callbacks reduce tracking overhead for read-only data.

**Entry points:** the architectural concepts above and the official source-access page. The guide explicitly distinguishes cache freshness from when an application actually requests or notices new data.

### 22. [cmusatyalab/coda](https://github.com/cmusatyalab/coda)

**Language / role:** C and C++; Coda distributed filesystem, including its supporting runtime and recoverable-storage libraries.

Coda offers a different correctness problem from always-connected cluster storage: a user can continue with cached files while disconnected and later reconcile changes. The [system overview](https://github.com/cmusatyalab/coda/blob/master/docs/manual/system_overview.md) explains server and Venus cache-manager roles; [operational scenarios](https://github.com/cmusatyalab/coda/blob/master/docs/manual/scenarios.md) expose hoarding and reintegration mechanics.

- **C1:** Reconnection replays client changes, and failed reintegration checkpoints the client modify log and leaves conflicts requiring repair. This is concrete evidence of divergent state and recovery handling, not merely offline reads.
- **C3:** A persistent hoard database gives files priorities to influence cache eviction and prefetching. Engineers can study the tradeoff between disconnected working-set coverage and limited local capacity.
- **C2:** The repository consolidates Coda with its LWP, RPC2, and RVM libraries; the README explains the dependency and packaging complexity that motivated bringing those components back together.

**Entry points:** the two manual chapters above. Some examples retain historical platform names and operational context, but the repository is a substantive source tree rather than an archived paper artifact.

### 23. [xtreemfs/xtreemfs](https://github.com/xtreemfs/xtreemfs)

**Language / role:** Java services and C++ client components; replicated filesystem for federated infrastructure.

The [OSD developer design](https://github.com/xtreemfs/xtreemfs/blob/master/doc/dev-guide/xtreemfs_osd.tex) breaks storage service work into preprocessing, storage, replication, deletion, and cleanup stages. It offers a tractable view of concurrency inside one distributed-filesystem server.

- **C1:** Requests for one file are assigned to the same storage thread to avoid sharing mutable file metadata across workers. The preprocessing stage validates signed capabilities, tracks open files, and participates in delayed deletion; cleanup handles objects orphaned by partial client operations.
- **C3:** The storage stage distributes work over threads, file contents can be striped across OSDs, and immutable replicas may be populated fully or lazily on reads. These are concrete choices in scheduling and remote-data movement.
- **C2:** A storage-layout abstraction separates object handling from how objects are arranged in the underlying local filesystem.

**Entry point:** the OSD design above. **Historical-study caveat:** the [API](https://api.github.com/repos/xtreemfs/xtreemfs) reported an October 2024 last push and no archive flag. The cited developer chapter describes read-only replication; it is not used to claim complete coverage of all later replication protocols.

### 24. [tahoe-lafs/tahoe-lafs](https://github.com/tahoe-lafs/tahoe-lafs)

**Language / role:** Python; decentralized, capability-secured file store with directories and encrypted, erasure-coded file shares.

The [architecture document](https://github.com/tahoe-lafs/tahoe-lafs/blob/master/docs/architecture.rst) explains three layers: distributed key-value storage, a file/directory graph, and applications. This belongs in the category while offering a very different trust model from a managed POSIX cluster.

- **C1:** Encryption, erasure coding, and Merkle verification let clients reconstruct and validate files despite unavailable or corrupt shares. Capabilities distinguish read access from write authority and bind retrieval to content validation.
- **C2:** The file graph composes a lower-level capability store; directory edges carry metadata and applications can build backup or sharing behavior above it.
- **C3:** Segmenting files bounds memory use and allows verification and consumption before an entire file arrives. Server selection spreads shares and accounts for storage capacity, with explicit discussion of insufficient distinct servers.

**Entry point:** the architecture above. Introducer availability, share placement, mutable-file behavior, and repair still matter; this is not a claim that arbitrary server loss is harmless. Canonical repository identity and archive status were verified through the GitHub API after browser fetch failures.

### 25. [ipfs/kubo](https://github.com/ipfs/kubo)

**Language / role:** Go; IPFS daemon, including UnixFS import, mutable-filesystem organization, pinning, and distributed content retrieval.

Kubo is included at the decentralized edge of the category: it distributes verifiable file graphs rather than providing a coherently writable shared POSIX mount. The [file-import code-flow guide](https://github.com/ipfs/kubo/blob/master/docs/add-code-flow.md) follows chunking through DAG construction, block storage, and pinning, and identifies the relevant Kubo and Boxo boundaries.

- **C1:** File identity depends on a cryptographic DAG, and pinning must preserve reachable content against garbage collection. Mutable filesystem paths are an organizational layer over content-addressed data, not a replacement for these retention rules.
- **C2:** CLI, CoreAPI, importer, and reusable Boxo components separate application entry points from chunking, UnixFS representation, block storage, and pinning.
- **C3:** Content-defined chunking can reuse unchanged chunks after edits, while DAG layout supports partial retrieval and avoids requiring one monolithic file object.

**Entry point:** the code-flow guide above. **Material maintenance limitation:** the inspected README says there is no dedicated maintainer and that Shipyard's maintenance work ended on **2026-09-30**. The repository was not marked archived; those facts should not be conflated with supported maintenance.

## Coverage, verification, and limitations

Discovery used more than six distinct live search formulations: POSIX replication and metadata authorities; Go/Rust object-backed filesystems; HDFS/Java and sequential large-file systems; HPC parallel I/O and burst buffers; erasure coding and adversarial storage; AFS/Coda and disconnected operation; recent AI/RDMA systems; MooseFS-derived projects; and Japanese grid/wide-area storage. Follow-up searches investigated project renames, official mirrors, source architecture, and less familiar research implementations. Later broad searches mostly returned already-covered projects, tutorials, generic storage frameworks, or nonofficial forks; Gfarm was a substantive late addition.

Every retained canonical repository was checked through its repository page and/or the GitHub repository API. All 25 also have independently opened primary documentation or source beyond the root README, including architectural or implementation material. The API archive flags were checked: none of the retained repositories was marked archived at the research date. Push dates are used only to qualify uncertain activity, not to award C4. URLs to source use verified branches; moving branches and `latest` documentation can change after this report.

LizardFS is retained as a documented independent MooseFS derivative. LeilFS is retained for substantial additional metadata, persistence, and I/O evolution, with SaunaFS counted as its former name. Lustre, LizardFS, OpenAFS, and Apache Hadoop's GitHub mirror roles are made explicit rather than represented as separate upstream projects. Other forks and renamed paths are not counted again.

Excluded boundaries include object-only and block-only systems without a substantial filesystem layer, CSI operators and clients counted separately from their parent filesystem, synchronization applications, wrappers around remote object APIs, classroom GFS reimplementations, and repository lists. JULEA appeared in discovery but was left out as a broader storage research framework; this report focuses on file services and their implementation. GekkoFS results did not establish an official substantive GitHub mirror during this search, so unofficial GitHub copies were not substituted. RozoFS was investigated but not retained because its canonical repository could not be verified successfully through the available fetch paths.

This was read-only source and documentation research: no candidate was cloned, built, benchmarked, or deployed. Some older developer guides describe historical designs, and some current documents describe development branches. Reported benchmark rankings, vendor superlatives, and star counts were not used as quality evidence. The selection is intended to guide focused architectural reading, with semantic and maintenance differences kept visible.
