# Network filesystem clients and servers

Research date: **2026-10-09**.

This report selects **25 GitHub repositories** implementing remote filesystem protocols, embeddable clients and servers, or distributed filesystems with a shared namespace. It covers both conventional network mounts and application-facing distributed filesystem APIs. For large repositories, the named subsystem is the subject of the recommendation. Object storage appears where it backs a filesystem; generic object stores, synchronization tools, deployment wrappers, and browser-based file managers are outside the main scope.

The criteria below are engineering judgments grounded in the linked implementation and documentation, not claims that every component is exemplary. Repository URLs, canonical owners, default branches, and archive flags were checked against GitHub pages or the public GitHub API. None of the retained repositories was marked archived at the time of research; that fact alone does not establish maintenance health.

- **C1 — Correctness:** difficult invariants, concurrency, hostile inputs, protocol semantics, or recovery and failure handling.
- **C2 — Abstractions:** substantial interfaces or architectural boundaries reusable across applications and backends.
- **C3 — Performance:** explicit throughput, latency, memory, or I/O constraints addressed through an understandable design.
- **C4 — Evolution:** evidence of changes over years together with compatibility work, testing, or complexity management.

## NFS implementations and embeddable servers

### [nfs-ganesha/nfs-ganesha](https://github.com/nfs-ganesha/nfs-ganesha)

**C — userspace NFS server, also supporting 9P2000.L.** A particularly useful study of how a protocol server can export different backing filesystems without placing their implementation details in every request handler.

- **C1:** The FSAL API documents mutexes, reference ownership, parent–child object lifetimes, and the danger of releasing an export while handles still depend on it. These are concrete concurrent lifetime invariants, not merely a declaration of thread safety.
- **C2:** Modules, exports, and object handles have operation vectors and public/private representations; version checks govern whether an independently built backend can load. Study the relationship between generic protocol handling and backend-specific handles in the [documented FSAL API](https://github.com/nfs-ganesha/nfs-ganesha/blob/next/src/include/fsal_api.h).

The [project introduction](https://github.com/nfs-ganesha/nfs-ganesha/blob/next/README.md) establishes protocol coverage and explains that contributions are reviewed through Gerrit rather than GitHub pull requests.

### [sahlberg/libnfs](https://github.com/sahlberg/libnfs)

**C — portable NFS client library.** Good for studying a network filesystem without the surrounding kernel: the same implementation exposes raw RPC, asynchronous filesystem operations, and synchronous calls.

- **C1:** Multithreaded operation has a specific lifecycle: mount first, start the service thread, use the synchronous API from application threads, drain outstanding I/O, then stop the service thread. The [threading document](https://github.com/sahlberg/libnfs/blob/master/README.multithreading) makes the supported concurrency boundary explicit.
- **C2:** The three API levels let an application choose protocol control or POSIX-like convenience. The [main documentation](https://github.com/sahlberg/libnfs/blob/master/README) also exposes reconnect/retry policies and explains why caches traversing nested exports need both device and inode identity.
- **C3:** The same documentation describes zero-copy transfers and the distinction between queued asynchronous calls and NFS session slots actually in flight. That is a useful example of a wire-protocol concurrency limit shaping throughput.

### [unfs3/unfs3](https://github.com/unfs3/unfs3)

**C — compact userspace NFSv3 server.** A manageable contrast to Ganesha and the kernel server, especially for understanding the limits of implementing filesystem semantics through ordinary host system calls.

- **C1:** The [filehandle implementation](https://github.com/unfs3/unfs3/blob/master/fh.c) encodes device/inode identity and generation information, checks handle lengths, and reconstructs path-related identity. It exposes the difficulty of keeping remote handles meaningful through namespace changes.
- **C4:** The [change history](https://github.com/unfs3/unfs3/blob/master/NEWS) records Connectathon 2003 conformance fixes, subsequent inode-width and client compatibility changes, stale-handle fixes, migration to libtirpc, and renewed macOS/Windows support. This is evidence of compatibility-driven evolution rather than age alone.

Limitations matter: the repository introduction excludes READDIRPLUS, and its [manual](https://github.com/unfs3/unfs3/blob/master/unfsd.8) says NLM locking is unsupported and documents userspace races. Treat this as an instructive bounded implementation, not a fully interchangeable NFS server.

### [huggingface/nfsserve](https://github.com/huggingface/nfsserve)

**Rust — embeddable NFSv3 server with an asynchronous virtual filesystem trait.** The former `xetdata/nfsserve` URL redirects here. Its stated use includes exposing a virtual filesystem through a localhost NFS mount; it is substantive library code rather than just the bundled demo.

- **C1:** The [VFS contract and implementation](https://github.com/huggingface/nfsserve/blob/main/src/vfs.rs) describe generation-tagged opaque handles, reserved file IDs, EOF behavior, and directory pagination constrained by reply bytes rather than entry count. These are valuable protocol-to-backend invariants.
- **C2:** `NFSFileSystem` separates lookup, attributes, reads, writes, and namespace operations from NFS transport, permitting independent backing stores and read-only or writable implementations.

Read the [project's protocol explanation and limitations](https://github.com/huggingface/nfsserve/blob/main/README.md) alongside the trait. The project explicitly calls itself incomplete; do not infer full NFSv3 operation or locking coverage from its convenient API.

## SMB servers and client libraries

### [samba-team/samba](https://github.com/samba-team/samba)

**Primarily C, with Python tooling — SMB server/client suite.** This entry concerns the SMB file service, particularly `source3/smbd` and its VFS boundary, rather than the entire Active Directory stack. GitHub is a source mirror; the repository directs upstream development and merge requests to Samba's Git/GitLab infrastructure.

- **C1:** The [SMB2 server request path](https://github.com/samba-team/samba/blob/master/source3/smbd/smb2_server.c) validates credit charges, request sizes, sequence windows, and duplicate message IDs. It is a substantial study of stateful resource accounting under untrusted requests.
- **C2:** The [VFS interface](https://github.com/samba-team/samba/blob/master/source3/include/vfs.h) provides an extensive filesystem operation boundary, including asynchronous I/O, ACLs, extended attributes, and locking. Its interface-version history shows the cost of evolving this abstraction as host and SMB semantics change.

Start with one request's validation and VFS dispatch before attempting the full server: the codebase's breadth is useful, but its scale makes a narrow reading path important.

### [sahlberg/libsmb2](https://github.com/sahlberg/libsmb2)

**C — portable SMB2/SMB3 client library with server support.** Useful for comparing an embeddable protocol engine with Samba's much broader service implementation.

- **C2:** The [library overview](https://github.com/sahlberg/libsmb2/blob/master/README) distinguishes synchronous POSIX-like calls, asynchronous POSIX-like calls, and raw packet access. Server handlers provide another integration boundary; server support is not equivalent to Samba's feature coverage.
- **C3:** Zero-copy reads/writes and compound commands address transfer overhead. The [public API](https://github.com/sahlberg/libsmb2/blob/master/include/smb2/libsmb2.h) explains both simple polling and callback-driven descriptor/event registration for larger event loops.
- **C1:** That API also specifies cancellation of pending operations when a context is destroyed, invalidation of dependent handles, lease/oplock-break callbacks, and unrecoverable event-loop failures. The ownership rules are an especially useful companion to the asynchronous API.

### [hierynomus/smbj](https://github.com/hierynomus/smbj)

**Java — SMB2/SMB3 client library.** A useful JVM example of mapping authenticated sessions, share connections, and protocol packets into a reusable application API.

- **C1:** In [Connection.java](https://github.com/hierynomus/smbj/blob/master/src/main/java/com/hierynomus/smbj/connection/Connection.java), a lock protects sequence-window credit allocation so concurrent senders cannot consume the same credits. Outstanding requests map to futures, cancellation is treated specially, and transport errors propagate to pending operations.
- **C2:** Connections, sessions, shares, configurable transports, packet conversion, signing, and encryption are distinct objects. The [usage documentation](https://github.com/hierynomus/smbj/blob/master/README.adoc) demonstrates their composition and separates operation timeouts from socket timeouts.

Study the public API alongside `send` and error handling: the interesting abstraction is not just a remote file object, but preservation of connection-wide protocol state while many operations are active.

### [TalAloni/SMBLibrary](https://github.com/TalAloni/SMBLibrary)

**C# — userspace SMB client/server library with storage adapters.** This provides a .NET and NT-semantics perspective rather than another POSIX-oriented SMB wrapper.

- **C2:** [INTFileStore](https://github.com/TalAloni/SMBLibrary/blob/master/SMBLibrary/NTFileStore/INTFileStore.cs) abstracts both filesystems and named pipes using create dispositions, share-access masks, security descriptors, byte-range locks, notifications, and device controls. Native Windows storage and custom backends can implement the same protocol-facing contract.
- **C1:** Asynchronous directory notification has an explicit pending-request/cancellation lifecycle. The [NTFileStore test](https://github.com/TalAloni/SMBLibrary/blob/master/SMBLibrary.Tests/NTFileStore/NTFileStoreTests.cs) starts a watch, cancels it, closes the handle, waits for completion, and checks for `STATUS_CANCELLED`—a concrete example of correctness extending beyond ordinary file reads and writes.

The repository contains both client and server implementations; examine the adapter boundary to understand which semantics a custom backend must supply.

## Kernel implementations and other remote-filesystem protocols

### [torvalds/linux](https://github.com/torvalds/linux)

**C — kernel monorepo; relevant subsystems are NFS/NFSD, SMB client/KSMBD, and 9P.** Counted once, not as a separate repository per protocol. The following two entry points deliberately sample client correctness and server scheduling.

- **C1:** The [NFSv4 client-identity document](https://github.com/torvalds/linux/blob/master/Documentation/filesystems/nfs/client-identifier.rst) explains persistent owner IDs, boot verifiers, principals, lease stealing, and lock recovery across restarts. It makes clear why identifier construction is a data-integrity issue.
- **C3:** The [KSMBD architecture](https://github.com/torvalds/linux/blob/master/Documentation/filesystems/smb/ksmbd.rst) splits file operations in the kernel from account and DCE/RPC management in userspace. Connection receivers dispatch requests to kernel work queues, allowing concurrent handling without making each operation a dedicated permanent thread.

The KSMBD document includes a feature-status matrix; partial or planned capabilities should not be generalized into full Samba equivalence.

### [libfuse/sshfs](https://github.com/libfuse/sshfs)

**C — FUSE filesystem client over SFTP.** Particularly good for studying the semantic gap between remote file-transfer operations and a locally mounted filesystem.

- **C1:** The [manual](https://github.com/libfuse/sshfs/blob/master/sshfs.rst) documents reconnect invalidation of open files, permission/identity mapping, rename and truncate workarounds, and caching controls. These make failure semantics and differences between servers visible to the caller.
- **C4:** The [dated changelog](https://github.com/libfuse/sshfs/blob/master/ChangeLog.rst) tracks the 2017 addition and subsequent removal of unsafe writeback-cache behavior, preservation of legacy options, platform work, and 2025–2026 maintainer/test changes. The 2026 entry includes malformed-reply handling and filesystem-operation test expansion.

Maintenance evidence is mixed: the README still warns about limited regular contributors, while the newer changelog records new maintainers and releases. It would be misleading to label the project simply abandoned or uniformly well staffed.

### [chaos/diod](https://github.com/chaos/diod)

**C — 9P2000.L file server and supporting protocol libraries.** A smaller protocol family makes it easier to follow the complete path from a wire request to a host filesystem operation.

- **C1:** The [protocol document](https://github.com/chaos/diod/blob/master/protocol.md) specifies negotiated message bounds, fid cloning and destruction, request cancellation through `flush`, and per-user attachment. These introduce state and lifetime obligations even in a relatively compact filesystem protocol.
- **C2:** The [libnpfs server implementation](https://github.com/chaos/diod/blob/master/src/libnpfs/srv.c) separates connections, requests, fids, and thread pools. Requests can be assigned through a fid's pool or the server default, while synchronized shutdown waits for connections to drain.

The README explicitly warns that reconnection requires remounting and that 9P has no server-driven cache invalidation mechanism. Those limits are part of the architectural comparison, not incidental deployment details.

### [Netatalk/netatalk](https://github.com/Netatalk/netatalk)

**C — AFP file server for Unix-like hosts.** A valuable alternative to NFS/SMB for studying how a server preserves a different operating system's file identity and metadata model.

- **C1:** The [CNID implementation](https://github.com/Netatalk/netatalk/blob/main/libatalk/cnid/cnid.c) validates reserved catalog identifiers in network byte order and preserves error classifications so callers can distinguish retryable failures from corruption and database failure. These are subtle cross-platform correctness details.
- **C2:** CNID backend registration and dispatch separate file identity management from its database implementation; a common API covers add, lookup, delete, and cache-stamp behavior.
- **C3:** The [directory-cache design discussion](https://github.com/Netatalk/netatalk/blob/main/doc/developer/dircache.md) traces directory enumeration through `readdir`, `stat`, the CNID database, and kernel caches. It distinguishes implemented validation tuning from proposed cache-first enumeration, making it useful for studying performance tradeoffs without treating every proposal as shipped behavior.

### [openafs/openafs](https://github.com/openafs/openafs)

**C — AFS clients, file servers, and supporting services.** This is the official GitHub browsing mirror of the upstream repository, confirmed by the project's [Git information page](https://openafs.org/pages/cvs.html); it is not an independently evolved fork despite the GitHub description's wording.

- **C1:** The [file-server callback implementation](https://github.com/openafs/openafs/blob/master/src/viced/callback.c) documents a strict recovery ordering: delayed callback breaks must finish before further requests from a reconnecting host are handled; failed breaks leave the host down. This gives a concrete cache-coherence invariant under network failure.
- **C3:** The same subsystem implements grouped callback breaks, adaptive expiration, and reclamation under bounded callback storage. It is an instructive alternative to repeatedly polling remote metadata: cached state is managed through promises and invalidation traffic.

Study callback creation, expiration, and delayed-break processing together. The file contains historical commentary as well as current code, so old introductory implementation limits should not automatically be treated as present-day constants.

## Clustered and parallel filesystems

### [ceph/ceph](https://github.com/ceph/ceph)

**Primarily C++ — CephFS metadata servers and userspace clients within the Ceph monorepo.** The relevant subject is CephFS over RADOS, rather than an undifferentiated recommendation of every Ceph storage interface.

- **C1:** The [distributed metadata-cache design](https://github.com/ceph/ceph/blob/main/doc/cephfs/mdcache.rst) describes capability revocation before conflicting locks can be granted, authoritative metadata-server ownership of each inode, and the treatment of clients that fail to return capabilities.
- **C3:** The [CephFS architectural introduction](https://github.com/ceph/ceph/blob/main/doc/cephfs/index.rst) separates data I/O directly to RADOS from metadata coordination. Metadata servers journal changes to RADOS while sharing responsibility for the namespace, keeping the metadata service out of the file-data path.

Experienced engineers can study how fine-grained caching rights connect client performance to distributed locking, including what must happen before cached state can safely move between participants.

### [gluster/glusterfs](https://github.com/gluster/glusterfs)

**C — distributed filesystem clients and brick servers.** Its distinctive learning value is the translator graph: distribution, replication, caching, and host filesystem access are composable participants in the request path.

- **C2:** The [architecture guide](https://docs.gluster.org/en/latest/Quick-Start-Guide/Architecture/) traces FUSE requests through DHT, AFR, protocol-client, protocol-server, and POSIX translators. Separate translators also implement read-ahead, caching, write-behind, and internal locks.
- **C1:** The [AFR developer design](https://github.com/gluster/glusterfs/blob/devel/doc/developer-guide/afr.md) explains locking replicated operations, marking pending changes, handling partial child failures, and repairing replicas. Namespace operations affecting multiple entries require correspondingly broader lock coordination.

The AFR document is a conceptual reading aid and contains older operation names; use it to understand replication invariants, then follow the current `xlators/cluster/afr` code rather than assuming every algorithm description is an exact specification of today's implementation.

### [lustre/lustre-release](https://github.com/lustre/lustre-release)

**C — parallel filesystem client and server implementation.** This is the official substantive GitHub mirror of the Whamcloud development repository, explicitly identified in its [README](https://github.com/lustre/lustre-release/blob/master/README).

- **C1:** The [distributed lock-manager implementation](https://github.com/lustre/lustre-release/blob/master/lustre/ldlm/ldlm_lock.c) distinguishes marking a lock destroyed from actually freeing its final reference, requires particular locks around state transitions, and handles waiting/granted locks and callbacks. These are concrete concurrent resource-lifetime invariants.
- **C2:** The lock manager supports resource namespaces, multiple lock types, processing policies, and callback suites. Extent locks, inode-bit locks, and file locks share infrastructure while retaining different granting rules.
- **C3:** Cached locks, LRU management, and specialized structures for matching/granting locks show why correctness infrastructure is also a performance subsystem.

Start with LDLM as a bounded subsystem before expanding into client I/O, object storage targets, or LNet; the full repository is substantially larger than this entry's reading path.

### [ThinkParQ/beegfs](https://github.com/ThinkParQ/beegfs)

**C/C++ — BeeGFS kernel client, metadata/storage services, and filesystem checker.** The current README explains that newer Rust management and Go administration components live in separate repositories. It also warns that pre-8 public history was published as squashed releases, limiting fine-grained historical study here.

- **C3:** The [architecture documentation](https://doc.beegfs.io/latest/architecture/overview.html) explains striped files, parallel client-to-storage access, and directory-based metadata distribution. The management service is not in the ordinary file-operation path.
- **C1:** The same document describes synchronous buddy mirroring, propagation delays during failover, and disposal handling for unlinked files still open on clients. These mechanisms connect replication, crash detection, and POSIX-visible object lifetime.

Use that document with the [repository/component guide](https://github.com/ThinkParQ/beegfs/blob/master/README.md) to map an operation to `client_module`, `meta`, and `storage`; do not assume this one repository contains the entire current BeeGFS stack.

### [waltligon/orangefs](https://github.com/waltligon/orangefs)

**C — OrangeFS/PVFS parallel filesystem clients and servers.** The GitHub API identifies this as the official repository. It offers unusually explicit documentation of asynchronous execution abstractions.

- **C2:** The [state-machine design](https://github.com/waltligon/orangefs/blob/master/doc/design/state-machine.tex) describes `.sm` definitions compiled into C structures, nested state machines, separate execution/data stacks, and parallel submachines whose outcomes must be collected.
- **C3:** The [flow design](https://github.com/waltligon/orangefs/blob/master/doc/design/flow-design.tex) separates a description of data movement from buffering, network/storage protocols, scheduling, and memory/file datatypes. One client operation can initiate flows to multiple servers concurrently.

The abstraction boundaries are useful for studying scalable I/O without hiding control flow in an unrestricted callback chain. These are historical design documents: the repository itself cautions that developer documentation may lag the code. Treat their motivation and organization as grounded evidence, not every old implementation detail as current behavior.

### [moosefs/moosefs](https://github.com/moosefs/moosefs)

**C — distributed filesystem with a FUSE client, metadata master, and chunk servers.** A useful codebase for following the entire buffered write lifecycle without moving among several implementation languages.

- **C1:** The [client write engine](https://github.com/moosefs/moosefs/blob/master/mfsclient/writedata.c) annotates when buffered bytes may change, protects per-inode/per-chunk state, tracks write IDs, and coordinates writes and flushes through condition variables. Error completion and delayed retries must release or retain buffers correctly.
- **C3:** The same implementation organizes work into inode, chunk, and block structures, bounds simultaneous chunk work, and manages a worker pool and reusable buffers. These are concrete mechanisms for controlling memory and parallelism while hiding network latency.

The [project and component introduction](https://github.com/moosefs/moosefs/blob/master/README.md) establishes the client/master/chunk-server roles. This entry makes no blanket claim that every capability advertised for the wider MooseFS product family is present in every build of this repository.

### [apache/hadoop](https://github.com/apache/hadoop)

**Primarily Java — HDFS within the Hadoop monorepo.** Scope: `hadoop-hdfs-project`, including clients, NameNodes, DataNodes, and their protocols; MapReduce and YARN are not separately counted.

- **C1:** The [HDFS design document](https://github.com/apache/hadoop/blob/trunk/hadoop-hdfs-project/hadoop-hdfs/src/site/markdown/HdfsDesign.md) connects block reports, heartbeats, re-replication, checksums, and writer restrictions to disk failures and network partitions.
- **C3:** Rack-aware replica placement and pipelined writes address network bandwidth and failure domains together. File data travels between clients and DataNodes rather than through the namespace authority.
- **C2:** The same design describes filesystem APIs, REST access, and an NFS gateway over the underlying block/namespace services, demonstrating reuse of the storage core across access methods.

Study the explicit workload assumptions: HDFS favors large streaming files and has different write semantics from a fully general POSIX filesystem. The overview's single-NameNode conceptual model is not a complete description of all modern HA and federation configurations.

### [quantcast/qfs](https://github.com/quantcast/qfs)

**C++ — Quantcast File System, including metadata/chunk servers and client libraries.** It evolved substantially from Kosmos File System; it is included as its own implementation lineage, without also counting the ancestor or derivative mirrors.

- **C1:** The [technical introduction](https://github.com/quantcast/qfs/blob/master/wiki/Introduction-To-QFS.md) explains chunk versioning to reject stale replicas after a failed server rejoins, checksummed reads, lease-based consistency, and atomic concurrent append. It also describes replicated and Reed–Solomon-protected storage.
- **C3:** The design targets large sequential workloads, using direct I/O, client caching, and background recovery that must not overwhelm foreground work.
- **C2:** The [developer guide](https://github.com/quantcast/qfs/blob/master/wiki/Developer-Documentation.md) maps the implementation into client, metaserver, chunk server, I/O libraries, erasure coding, FUSE, and language/Hadoop integration layers.

Several introductory platform examples are historical. The architectural mechanisms are useful study material; old benchmark comparisons are not treated here as present-day performance evidence.

## Filesystems over object stores and newer disaggregated designs

### [juicedata/juicefs](https://github.com/juicedata/juicefs)

**Go — shared filesystem client over object storage and pluggable metadata databases.** A strong example of concentrating filesystem logic in clients while reusing existing storage services.

- **C1:** The [architecture document](https://github.com/juicedata/juicefs/blob/main/docs/en/introduction/architecture.md) distinguishes fixed logical chunks, write-generated slices, and physical blocks. Reads must resolve overlapping slices to the newest valid bytes; compaction must preserve that logical content.
- **C2:** Filesystem access methods, object storage, and metadata engines are separate boundaries. The [project introduction](https://github.com/juicedata/juicefs/blob/main/README.md) identifies multiple database and object-store implementations and client interfaces using the same filesystem organization.
- **C3:** Concurrent block uploads and asynchronous slice compaction address transfer parallelism and fragmentation/read amplification. The architecture document also explicitly notes that aggressive metadata caching can trade consistency for performance.

Study the data mapping rather than assuming that one user-visible file corresponds to one object-store key.

### [seaweedfs/seaweedfs](https://github.com/seaweedfs/seaweedfs)

**Go, with additional implementation components — distributed file service over a volume-based blob store.** The former `chrislusf/seaweedfs` project now has this canonical organization. Scope here is the filer, filesystem clients, and their backing volume services, not every object/table feature in the monorepo.

- **C2:** The [architecture section](https://github.com/seaweedfs/seaweedfs/blob/master/README.md#architecture) separates masters that locate volumes, volume servers that hold blobs, and filers that provide directory/file metadata through different backend stores and access protocols.
- **C3:** Volume-level location tracking keeps masters out of reads, while append-oriented volume storage avoids treating every small blob as an independent host filesystem object. These are structural performance choices; this report does not adopt the project's numerical throughput claims.
- **C1:** The [filer implementation](https://github.com/seaweedfs/seaweedfs/blob/master/weed/filer/filer.go) exposes metadata-store dispatch, deletion queues, metadata logs, and exclusive-create error handling. In particular, a failed existence lookup must not be treated as permission to overwrite an existing entry.

### [cubefs/cubefs](https://github.com/cubefs/cubefs)

**Go — distributed filesystem and object service with partitioned metadata and data.** Useful for comparing sharded filesystem services with a design that puts metadata in a single external database.

- **C1:** The [architecture document](https://github.com/cubefs/cubefs/blob/master/docs/source/overview/architecture.md) distinguishes Raft-backed master state from metadata partitions replicated through Multi-Raft. Each metadata shard covers an inode range and maintains inode and dentry B-trees. Keeping these authorities and replicated states consistent is the central correctness problem exposed by this organization.
- **C2:** A volume is composed from metadata and data shards and is exposed through filesystem and object interfaces. Replicated DataNodes and erasure-coded BlobNodes are distinct data subsystems that can coexist.
- **C3:** Partitioned metadata, in-memory indexes, and horizontally scalable data services provide explicit scaling boundaries rather than a monolithic service with an unspecified performance claim.

The [project overview](https://github.com/cubefs/cubefs/blob/master/README.md) identifies the POSIX/HDFS/S3 roles. Shared access methods should not be assumed to have identical consistency semantics solely because they use one storage system.

### [deepseek-ai/3FS](https://github.com/deepseek-ai/3FS)

**C++ with Rust components and Python integration — disaggregated filesystem for SSD/RDMA environments.** A newer contrast to the established HPC and batch-processing systems above; no multi-decade maturity claim is made.

- **C1:** The [design notes](https://github.com/deepseek-ai/3FS/blob/main/docs/design_notes.md) specify chain-version checks, serialized chunk writes, pending versus committed versions, and acknowledgment propagation in CRAQ replication. They explain why failure recovery and replica reads require more than merely copying bytes to several machines.
- **C3:** The same design separates transactional metadata services from SSD chunk services and offers both FUSE and native clients. RDMA transfer and a replication protocol that can use multiple replicas for reads are tied to its read-heavy workload assumptions.
- **C1, testing evidence:** The [P specifications guide](https://github.com/deepseek-ai/3FS/blob/main/specs/README.md) identifies models for data replication and RDMA sockets, including tests with unreliable failure detection and multiple clients/failures. This is stronger evidence of deliberate failure reasoning than a benchmark alone, but it is not proof of the entire production implementation.

## Coverage and search notes

Discovery used more than six distinct live search formulations, covering: NFS RPC libraries and userspace servers; SMB clients and server APIs; Rust NFS and Plan 9/9P servers; SSHFS, AFP, and AFS; HPC parallel filesystems; metadata/chunk-server architectures; object-backed filesystems; RDMA/CRAQ designs; and less prominent systems such as UNFS3, OrangeFS, and QFS. Follow-up searches targeted Gluster translator design, Ceph metadata capabilities, BeeGFS mirroring, CubeFS replication, and WebDAV/SFTP alternatives. Later broad searches increasingly returned already-covered architectures, thin adapters, packaging repositories, and file-transfer/web-UI products rather than distinct filesystem implementations, giving diminishing returns for this scope.

Every retained repository has a verified canonical GitHub identity and at least one independently opened/read primary source beyond the main project README. Those additional sources include API contracts, implementation files, design documents, tests, or changelogs; rereading a README through a raw URL was not counted as independent evidence. GitHub HTML retrieval occasionally failed, so public GitHub API metadata and individual raw source files were used instead. No repositories were cloned, dependencies installed, or candidate code executed.

The selection deliberately avoids counting CSI provisioners, container images, generic FUSE frameworks, ordinary synchronization tools, and duplicate forks as independent filesystem implementations. WebDAV/SFTP file-transfer platforms and object-store-only mounts are adjacent areas, not exhaustively covered here. Linux, Ceph, Hadoop, and SeaweedFS each count once with explicit subsystem boundaries; OpenAFS, Samba, and Lustre are identified as substantive upstream mirrors. Public availability does not imply a uniform license across all components or editions.

This is a source-reading selection guide, not a deployment recommendation, conformance audit, maintenance guarantee, or independently reproduced performance comparison. Historical design documents and mismatches between maintenance statements and newer changelogs are called out where observed. Claims about architectural tradeoffs are grounded in the cited material; the judgment that those tradeoffs make a repository worth studying is an inference.
