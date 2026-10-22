# Content-addressable storage systems

Research date: **2026-10-09**.

This report selects 24 GitHub repositories in which content-derived identifiers are central to storing, retrieving, sharing, or retaining data. It includes standalone blob servers, embedded storage engines, peer-to-peer implementations, deduplicating backup repositories, distribution tools, and build caches. In larger projects, the entry identifies the storage subsystem to study. A content address may cover a canonical object representation, including metadata, rather than the raw bytes of a physical container file. Cache eviction and archival retention consequently require different correctness arguments.

The criteria below are evidence-based reasons to study a codebase, not a certification that every component is correct or suitable for production. Architectural judgments about learning value are grounded in the linked primary material. Canonical repository URLs and archive status were checked through the GitHub API; implementation and documentation files were read separately. Links generally follow the inspected default branch and can change after this research date.

- **C1 — Difficult correctness:** invariants, concurrency, adversarial inputs, integrity, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces or data models that support multiple applications or backends.
- **C3 — Performance with structure:** concrete resource constraints addressed by an understandable storage architecture.
- **C4 — Sustained evolution:** documented development across years together with compatibility, testing, migration, or complexity management. Repository age alone does not qualify.

## Networked, general-purpose, and archival blob stores

### [ipfs/kubo](https://github.com/ipfs/kubo)

**Language / role:** Go; a complete IPFS daemon with a persistent block repository, content routing, gateways, and administrative APIs.

Study how a service exposes immutable, content-addressed DAGs while retaining mutable operational state such as pins and the Mutable File System. Kubo is especially useful for following the boundary between an IPFS node and its underlying blockstore and DAG libraries.

- **C1:** Garbage collection takes the blockstore GC lock before obtaining mutable-file-system roots, drains competing pin-lock holders, marks pinned descendants, and only then sweeps. It also normalizes CIDs to account for different codecs referring to the same stored block. These are concrete concurrency and identity invariants in [`gc/gc.go`](https://github.com/ipfs/kubo/blob/master/gc/gc.go).
- **C2:** The node presents the same content model through UnixFS, HTTP gateways, RPC, and network block exchange; the [repository overview](https://github.com/ipfs/kubo/blob/master/README.md) identifies these integration boundaries and the associated APIs. This makes the code useful beyond a single file-sharing workflow.

### [ipfs/helia](https://github.com/ipfs/helia)

**Language / role:** TypeScript; an embeddable IPFS implementation for JavaScript and browser applications.

Helia supplies a contrasting implementation style to Kubo: applications assemble storage, routing, codecs, and block-fetching strategies. Its monorepo includes the core implementation and data-oriented packages such as UnixFS, DAG-CBOR, JSON, and CAR support.

- **C1:** The implementation explicitly explains why GC must exclude blockstore writes while an imported DAG is not yet pinned. It also supports coordinating ownership of that lock across processes. Read the `holdGcLock` contract in [`packages/helia/src/helia.ts`](https://github.com/ipfs/helia/blob/main/packages/helia/src/helia.ts).
- **C2:** The [system diagram and package map](https://github.com/ipfs/helia/blob/main/README.md) separate blockstores, datastores, block brokers, routing, and application representations. The implementation exposes replaceable hashers and codecs, with on-demand loaders, instead of requiring one storage or serialization stack.

### [n0-computer/iroh-blobs](https://github.com/n0-computer/iroh-blobs)

**Language / role:** Rust; BLAKE3-addressed blob storage and verified transfer over Iroh connections.

This is a focused study of partial retrieval: a request can select ranges within a blob or within a sequence of blobs. The [README](https://github.com/n0-computer/iroh-blobs/blob/main/README.md) explicitly warns that the inspected development line is not production quality and points production users to version 0.35; that warning should accompany any evaluation.

- **C1:** The [protocol implementation and specification](https://github.com/n0-computer/iroh-blobs/blob/main/src/protocol.rs) require validation on both sending and receiving sides, include verification information in range responses, and distinguish interrupted transfers from unavailable or invalid data.
- **C3:** The same source explains bounded-memory streaming, batching small blobs to avoid round trips, and compact range-set encoding for fragmented or interrupted downloads. These optimizations have visible protocol consequences rather than being isolated microbenchmarks.

### [ethersphere/bee](https://github.com/ethersphere/bee)

**Language / role:** Go; the Swarm network client. Relevant subsystems are content-addressed chunks and local chunk storage.

Study the separation between a chunk's network identity and its physical storage location. Bee includes other protocols and accounting machinery; the sources below isolate the CAS portion rather than treating the whole system as a uniform blob store.

- **C1:** [`pkg/cac/cac.go`](https://github.com/ethersphere/bee/blob/master/pkg/cac/cac.go) validates chunk lengths and recomputes the Binary Merkle Tree hash, including the span header, before accepting a chunk as content-addressed. The retrieval index also carries reference counts that govern when physical storage can be released.
- **C2 / C3:** [`chunkstore.go`](https://github.com/ethersphere/bee/blob/master/pkg/storer/internal/chunkstore/chunkstore.go) separates the address-to-location index from the Sharky byte store through interfaces. Repeated puts share a stored chunk, while `GetInto` permits callers to reuse buffers. It is a concrete example of deduplication, lifetime management, and allocation control meeting at a narrow storage boundary.

### [perkeep/perkeep](https://github.com/perkeep/perkeep)

**Language / role:** Go; personal data storage, synchronization, and indexing built over immutable blobs.

Perkeep is valuable for studying how many storage implementations can share a small blob protocol while higher layers model files and personal information. Its physical packing layer is particularly instructive for systems that need both fine-grained deduplication and efficient whole-file reads.

- **C1 / C2:** [`pkg/blobserver/interface.go`](https://github.com/perkeep/perkeep/blob/master/pkg/blobserver/interface.go) specifies digest and size validation, enumeration ordering, cancellation and channel-closing obligations, and partial deletion semantics. The same interfaces serve local, remote, encrypted, sharded, and replicated stores.
- **C3:** [`blobpacked.go`](https://github.com/perkeep/perkeep/blob/master/pkg/blobserver/blobpacked/blobpacked.go) explains how logical blobs are rearranged into contiguous ZIP containers according to likely access patterns. A mapping index preserves logical identity, and embedded manifests preserve reconstruction information if that index is lost. This exposes the distinction between logical CAS objects and physical I/O layout.

### [9fans/plan9port](https://github.com/9fans/plan9port)

**Language / role:** C; the **Venti server and libraries** inside the Plan 9 from User Space monorepo.

Venti is an important historical architecture retained as substantive source in this repository, not a separate modern implementation. It uses SHA-1 scores for write-once archival blocks. Study its design in that historical context, including the protocol's explicit limitations concerning authentication.

- **C1:** The [Venti protocol manual](https://github.com/9fans/plan9port/blob/master/man/man7/venti.7) distinguishes acknowledgement of a buffered write from a `sync` response guaranteeing prior writes reached permanent storage. It also specifies outstanding request-tag uniqueness and canonical zero truncation for data and pointer blocks.
- **C2 / C3:** The protocol builds arbitrary file trees from typed blocks without requiring the server to understand application metadata. The [server manual](https://github.com/9fans/plan9port/blob/master/man/man8/venti.8) separates append-only arenas from rebuildable indexes and Bloom filters, making the durability and lookup-performance tradeoffs unusually explicit.

### [commercialhaskell/casa](https://github.com/commercialhaskell/casa)

**Language / role:** Haskell; Content-Addressable Storage Archive, with separate client, server, and shared-type packages.

Casa is a smaller substantive counterpoint to large distributed stores. It exposes batched blob transfer over HTTP and stores content under SHA-256 keys, making it useful for studying a [package-distribution CAS](https://academy.fpblock.com/blog/casa/) implemented with streaming functional APIs and a relational backend.

- **C1:** The [client](https://github.com/commercialhaskell/casa/blob/master/casa-client/src/Casa/Client.hs) parses responses against the requested key-to-length map, rejects unrequested keys, and hashes returned bytes before yielding them. Content identity is therefore checked at the consumer boundary rather than inferred from a successful HTTP response.
- **C2 / C3:** The [server](https://github.com/commercialhaskell/casa/blob/master/casa-server/src/Casa/Server.hs) separates protocol handlers from its database backend, derives keys from uploaded bytes, and uses a unique database constraint for deduplication. Batched pull responses and the client's Conduit source/sink abstractions provide reusable transfer machinery without one request per object. This is a study of those mechanisms, not a claim that every parser or resource limit has been audited.

### [DataONEorg/hashstore-java](https://github.com/DataONEorg/hashstore-java)

**Language / role:** Java; filesystem-backed object storage for DataONE scientific data repositories.

HashStore distinguishes persistent dataset identifiers from content identifiers, allowing multiple identifiers to refer to one stored object. Its [overview](https://github.com/DataONEorg/hashstore-java/blob/main/README.md) documents separate object, metadata, and bidirectional reference layouts. Metadata addressed by identifier and format is not itself necessarily content-addressed.

- **C1:** The storage path validates submitted checksums and sizes before final placement, coordinates writes by persistent identifier, and coordinates shared-object operations by content identifier. [`FileHashStore.java`](https://github.com/DataONEorg/hashstore-java/blob/main/src/main/java/org/dataone/hashstore/filehashstore/FileHashStore.java) exposes the synchronization and reference-maintenance work behind deduplication.
- **C2:** The [`HashStore` interface](https://github.com/DataONEorg/hashstore-java/blob/main/src/main/java/org/dataone/hashstore/HashStore.java) separates storage, validation, tagging, retrieval, and metadata operations. It supports both all-at-once submissions and workflows where bytes arrive before their identifier or validation metadata, a useful abstraction for ingestion services.

## Chunked distribution and backup repositories

### [systemd/casync](https://github.com/systemd/casync)

**Language / role:** C; content-addressed synchronization and storage of filesystem images and directory trees.

The distinguishing idea is to serialize a directory tree reproducibly and then chunk the resulting stream across file boundaries. The [README's encoding and decoding explanation](https://github.com/systemd/casync/blob/main/README.md) describes compressed hash-named chunks and a separate reconstruction index. The API check found the repository unarchived; no claim of a frequent current release cadence is made.

- **C1:** [`src/caformat.h`](https://github.com/systemd/casync/blob/main/src/caformat.h) specifies ordered directory entries, metadata records, lookup trailers, and feature flags for permissions, IDs, timestamps, extended attributes, and filesystem-specific properties. Preserving deterministic serialization while representing these semantics is the central correctness topic.
- **C3:** Chunking across file boundaries avoids letting individual file sizes determine storage units. Shared chunk stores, compression, local seed reuse, and HTTP delivery address disk and network costs while keeping the encoding/index/store decomposition understandable.

### [folbricht/desync](https://github.com/folbricht/desync)

**Language / role:** Go; a separately implemented casync-compatible distribution tool and library.

This is retained alongside casync because it has its own implementation and architectural choices, especially parallel chunking and composable remote stores. It is format-compatible, not a command-line drop-in replacement.

- **C1 / C3:** The [chunking and concurrency explanation](https://github.com/folbricht/desync/blob/master/docs/concepts.md) describes independently chunking overlapping portions of a file and finding common boundaries before joining the results. It candidly discusses inputs, such as long zero-filled regions, for which the parallel workers fail to align efficiently. Seed and reflink strategies further separate hashing cost from reconstruction I/O.
- **C2:** The [store architecture](https://github.com/folbricht/desync/blob/master/docs/stores.md) composes local and remote stores, writable caches, fallback chains, and failover groups. It documents important semantic differences: grouped replicas must hold equivalent contents, and a corrupt cache chunk fails the operation rather than being silently skipped.

### [huggingface/xet-core](https://github.com/huggingface/xet-core)

**Language / role:** Rust with Python bindings; the Xet client-side storage, chunking, caching, and reconstruction engine used by Hugging Face tooling.

The [repository overview](https://github.com/huggingface/xet-core/blob/main/README.md) identifies separate data-processing, protocol-client, format, and runtime crates. This is substantive CAS machinery, but the repository is not the complete hosted CAS service.

- **C1:** The official [upload protocol](https://github.com/huggingface/hub-docs/blob/main/docs/xet/upload-protocol.md) requires every referenced xorb to finish uploading before publishing its shard. Reconstruction terms identify ordered chunk ranges, and verification hashes accompany registration. This provides a concrete study of publication ordering when multiple upload stages execute concurrently.
- **C3:** The same protocol explains grouping chunks into compressed xorbs, local shard caches for deduplication, range-based reconstruction, and adaptive upload concurrency. These mechanisms address the bandwidth and object-request costs of large model and dataset files while retaining explicit format and pipeline boundaries.

### [restic/restic](https://github.com/restic/restic)

**Language / role:** Go; encrypted backup repositories using content-addressed blobs, packs, trees, and snapshots.

Restic is particularly useful for distinguishing plaintext chunk identity from the storage identity of an encrypted pack. Its repository format exposes how deduplication, authenticated encryption, and multiple storage backends coexist.

- **C1:** The [repository design](https://github.com/restic/restic/blob/master/doc/design.rst) requires immutable files to be published atomically so parallel clients cannot observe partial writes. It specifies independently authenticated blobs and pack headers, version checks, and strict encoding rules.
- **C3:** A trailing pack header permits streaming writes without rewriting the whole pack and allows index reconstruction by reading headers rather than all payloads. Independent blob authentication also supports repository reorganization without re-encrypting every blob.
- **C4:** The [changelog](https://github.com/restic/restic/blob/master/CHANGELOG.md) spans releases from 2017 through 2026 and records concrete evolution, including concurrent cache-cleanup fixes, a content-defined-chunking attack mitigation, and backend failure handling. The design separately records repository-format compatibility rules.

### [borgbackup/borg](https://github.com/borgbackup/borg)

**Language / role:** Python with C/Cython performance components; authenticated, deduplicating backup storage.

The inspected default branch is **Borg 2 beta**, explicitly marked unstable in the [README](https://github.com/borgbackup/borg/blob/master/README.rst). The following sources describe that development line, not the on-disk format of stable Borg 1 repositories.

- **C1:** The [security design](https://github.com/borgbackup/borg/blob/master/docs/internals/security.rst) models an untrusted repository and explains authenticating both object data and its meaning in the object graph. The [pack specification](https://github.com/borgbackup/borg/blob/master/docs/internals/packs.rst) goes further into header authentication, separation of metadata/data slots, corrupted length fields, and validated recovery scans.
- **C3:** Packs combine individually addressable chunks to reduce per-object operations on high-latency storage. Their self-describing records permit rebuilding location indexes, while range reads retrieve individual chunks. It is a strong example of performance changes forcing detailed reconsideration of corruption boundaries and recovery behavior.

### [kopia/kopia](https://github.com/kopia/kopia)

**Language / role:** Go; encrypted snapshot backups over local, remote, and cloud blob storage.

Kopia's repository layers provide a clear vocabulary for studying CAS embedded inside a larger application. Content identity belongs to logical blocks and objects; the physical pack names can be random. The [README](https://github.com/kopia/kopia/blob/master/README.md) supplies the application and backend context.

- **C2:** The [architecture document](https://github.com/kopia/kopia/blob/master/site/content/docs/Advanced/Architecture/_index.md) separates ordinary blob storage, content-addressable block storage, arbitrarily sized content-addressable objects, and label-addressable manifests. Large objects use indirection, while snapshots and policies obtain human-usable labels over the same underlying content layer.
- **C3:** Small encrypted blocks are packed together to reduce cloud-storage overhead. An index maps block IDs to container offsets and lengths, and a local index in each pack supports recovery. Caching and this layout explicitly target high-latency backends rather than assuming a local filesystem's access costs.

### [bup/bup](https://github.com/bup/bup)

**Language / role:** Python and C; deduplicating backups built directly on Git object and packfile formats.

Bup is independently implemented backup software, not a Git fork. It is useful for understanding why a source-control storage format needs different ingestion and chunking policies for large backup files. Its [README](https://github.com/bup/bup/blob/main/README.md) includes testing limitations as well as integration and release information.

- **C2:** Git blobs and trees provide a reusable representation that other Git-aware tooling can inspect, while bup adds remote backup and filesystem views. The [design document](https://github.com/bup/bup/blob/main/DESIGN.md) explains why chunk sequences are represented as actual trees, preserving graph traversal and reachability semantics.
- **C3:** Content-defined splitting limits how much data changes after an insertion into a large file. Hierarchical fanout avoids making the sequence of chunk identifiers into another enormous object; writing packfiles directly avoids an obligatory loose-object staging and repacking cycle. These are explicit architectural responses to large-file and index-memory constraints.

## Build and execution caches

### [buildbarn/bb-storage](https://github.com/buildbarn/bb-storage)

**Language / role:** Go; the Buildbarn CAS and action-cache storage daemon, independently usable without remote execution workers.

Study this repository for cache correctness under eviction, not for permanent archival retention. It makes the distinction between immutable CAS objects and action-cache records that reference those objects central to its design.

- **C1:** The [storage ADR](https://github.com/buildbarn/bb-adrs/blob/main/0002-storage.md) derives exact `FindMissing` behavior and action-result completeness checks from clients that do not download intermediate outputs. A cached action result is not useful if its referenced blobs have disappeared. The ADR is historical design rationale; its statements about cloud-provider consistency should not be treated as current provider documentation.
- **C2 / C3:** The current [configuration schema](https://github.com/buildbarn/bb-storage/blob/main/pkg/proto/configuration/blobstore/blobstore.proto) documents sharding, mirroring, fallback, existence caching, and completeness-checking decorators. Its local storage configuration exposes a digest-to-location hash table and LRU-like block lifecycle, making both composition and eviction costs inspectable.

### [TraceMachina/nativelink](https://github.com/TraceMachina/nativelink)

**Language / role:** Rust; relevant subsystem is `nativelink-store`, serving CAS and action-cache roles within a remote execution system.

The inspected implementation carries **Functional Source License 1.1 with an Apache 2.0 future license** in its source header; it should not be described simply as an Apache-licensed project. Its storage subsystem is useful independently as an architectural study.

- **C2 / C3:** The [store-module guide](https://github.com/TraceMachina/nativelink/blob/main/nativelink-store/README.md) explains composable stores and decorators: fast/slow tiers, size-based routing, compression, verification, and durable backends. The composition lets small and large artifacts take different storage paths without duplicating the complete CAS service.
- **C1:** [`verify_store.rs`](https://github.com/TraceMachina/nativelink/blob/main/nativelink-store/src/verify_store.rs) checks declared sizes, excess input, EOF placement, and computed digests while forwarding a stream. Verification failures propagate before successful stream completion; the code exposes how validation and concurrent downstream writes must cooperate.

### [buchgr/bazel-remote](https://github.com/buchgr/bazel-remote)

**Language / role:** Go; a bounded disk CAS and action cache with HTTP and gRPC interfaces.

This provides a more compact implementation than an entire remote execution platform. The [README](https://github.com/buchgr/bazel-remote/blob/master/README.md) distinguishes SHA-256-addressed CAS entries from action-cache keys and documents eviction, proxy backends, and compressed transfer semantics.

- **C1:** [`cache/disk/casblob/casblob.go`](https://github.com/buchgr/bazel-remote/blob/master/cache/disk/casblob/casblob.go) verifies the uncompressed digest and declared length, rejects truncated or excess input, and manages completion of the on-disk chunk-offset table. Compression must preserve logical object identity.
- **C3:** Independently compressed chunks support offset reads without decoding an entire blob. Buffer pooling, streaming of already compressed data, and bounded disk-cache eviction address allocation, bandwidth, and capacity constraints through identifiable components. The README also distinguishes executable compatibility promises from the absence of a stable Go-library API promise.

### [buildbuddy-io/buildbuddy](https://github.com/buildbuddy-io/buildbuddy)

**Language / role:** Go and TypeScript monorepo; relevant subsystem is the Go remote-cache CAS server.

The scope here is the CAS service and its cache interface, not the build-results UI or an assumption that all enterprise storage features belong to the open-source edition. The [cache configuration guide](https://github.com/buildbuddy-io/buildbuddy/blob/master/docs/config-cache.md) explicitly describes the OSS cache as a single-node disk cache.

- **C1:** The [CAS server implementation](https://github.com/buildbuddy-io/buildbuddy/blob/master/server/remote_cache/content_addressable_storage_server/content_addressable_storage_server.go) validates digests after decompression, rejects negative sizes and oversized batches, and returns per-object statuses. Tenant-prefix attachment also makes namespace handling part of the request path.
- **C2 / C3:** The server operates through a cache interface while implementing batching, compressor negotiation, tree-cache policies, and fallback reconstruction from content-defined chunks. This is useful for studying how a common protocol layer handles storage capabilities and performance policies without embedding one disk layout directly in every RPC.

## Versioned object stores and embedded database engines

### [git/git](https://github.com/git/git)

**Language / role:** C; the object database, pack indexes, and hash-format machinery of Git. **Official publish-only GitHub source mirror.**

Treat the object store as the subsystem under study rather than attempting to review the entire version-control application. Git offers especially rich material on evolving persistent identities and accelerating lookups while retaining older representations.

- **C1:** The [hash-function transition design](https://github.com/git/git/blob/master/Documentation/technical/hash-function-transition.adoc) explains that changing an object's hash also changes references embedded in parent objects. It discusses bidirectional name mappings, signed-object consequences, and refusing unsupported repository extensions. These are design and compatibility requirements, not a claim that every transition goal is implemented.
- **C3:** The [multi-pack-index design](https://github.com/git/git/blob/master/Documentation/technical/multi-pack-index.adoc) addresses lookup degradation when many packs accumulate and full repacking is too expensive. One cross-pack object index, optional extensions, and retention of ordinary pack indexes make performance improvements compatible with fallback and downgrade paths.

### [ostreedev/ostree](https://github.com/ostreedev/ostree)

**Language / role:** C; libostree's content-addressed filesystem repository and deployment library.

OSTree adapts the object-store model to operating-system and application trees. Its objects include ownership and extended attributes, which changes both identity and checkout semantics compared with source-control blobs.

- **C1:** The [repository anatomy](https://github.com/ostreedev/ostree/blob/main/docs/repo.md) distinguishes content, directory-tree, and directory-metadata objects, and explains which uncompressed bytes and metadata contribute to checksums. The [README](https://github.com/ostreedev/ostree/blob/main/README.md) states the immutability requirement imposed by hardlink-based checkouts: mutating a shared file can corrupt repository content.
- **C2 / C3:** The shared library supports multiple repository modes for privileged deployments, unprivileged builders, containers, and HTTP serving. Splitting directory metadata avoids repeated attribute listings; hardlink checkouts share data without recopying whole installations. These uses follow from the repository's concrete representation choices.

### [mirage/irmin](https://github.com/mirage/irmin)

**Language / role:** OCaml; libraries for branchable and mergeable stores, with particular interest in the `irmin-pack` backend.

Irmin is useful for studying persistent content-addressed graphs inside an application-selected storage stack. The most instructive material here follows a physical layout change through its concurrency constraints and migration policy.

- **C1 / C3:** The [chunked-suffix design](https://github.com/mirage/irmin/blob/main/doc/irmin-pack/design/chunked_suffix.md) examines one writer coexisting with multiple readers during garbage collection. Readers must continue to see a valid generation while a control file publishes new storage bounds. Splitting the append-only suffix into files reduces the temporary disk-space cost of retaining the old layout during collection.
- **C4:** The [change history](https://github.com/mirage/irmin/blob/main/CHANGES.md) records the chunked suffix and on-disk format change in 2022, migration and GC fixes in 2023, and compatibility and CI work in 2024–2025. It also documents removal of stream proofs to simplify difficult cached-I/O ordering, providing concrete evidence of complexity management.

### [attic-labs/noms](https://github.com/attic-labs/noms)

**Language / role:** Go; **archived, explicitly unmaintained historical project** with a typed Merkle-DAG database and Noms Block Store.

The [README](https://github.com/attic-labs/noms/blob/master/README.md) recommends research use rather than reliance and points to Dolt. Noms remains valuable for its original general-purpose data model. Its inclusion does not imply that its acknowledged migration, GC, and synchronization limitations were resolved.

- **C1:** The [technical overview](https://github.com/attic-labs/noms/blob/master/doc/intro.md) makes canonical value identity an invariant: equivalent logical values must have the same hash. Immutable chunks are separate from dataset-head updates requiring optimistic concurrency.
- **C2 / C3:** The typed model supports blobs, maps, sets, lists, records, and explicit references. The [NBS design](https://github.com/attic-labs/noms/blob/master/go/nbs/README.md) narrows persistence to inserting chunks, publishing a root, and garbage collection; new data becomes durable at root publication. Related chunks are colocated instead of maintaining a general key ordering that the workload does not need.

### [dolthub/dolt](https://github.com/dolthub/dolt)

**Language / role:** Go; the content-addressed block store beneath Dolt's versioned SQL database, primarily `go/store`.

Dolt descends from Noms but has substantial separate evolution into a SQL system with its own journaling, locking, and storage operations. It is included alongside its ancestor to study those differences, not counted as an interchangeable fork. The storage subsystem is the category fit.

- **C1:** The current [NBS source-tree documentation](https://github.com/dolthub/dolt/blob/main/go/store/nbs/README.md) details lifetime advisory locks, read-only fallback after a journal-lock timeout, and why the presence of a lock file is not proof that a lock is held. Its older introductory material is inherited from Noms, so it should be read alongside current documentation rather than treated as a blanket current backend-support statement.
- **C3:** The official [block-store architecture](https://www.dolthub.com/docs/architecture/storage-engine/block-store/) explains separating sorted hash prefixes, ordinals, suffixes, and chunk lengths. The in-memory index resolves a chunk's physical offset before reading payload data, while the content-independent chunk interface supports the database's higher-level trees.

## Search coverage and limitations

Discovery used 20 distinct live-web query formulations, followed by repository API checks, source-tree inspection, and direct reading of implementation or design material. Search angles included general CAS architecture; Rust verified blob transfer; IPFS and Swarm; remote-execution caches; encrypted deduplicating backups; casync-style image distribution; Git/OSTree filesystem objects; Noms/Irmin/Dolt databases; Venti archival storage; C++ and less prominent deduplication systems; Java scientific repositories; Haskell package archives; and garbage-collection-oriented implementations. Later surveys increasingly repeated already covered projects or surfaced smaller projects for which this investigation did not establish comparable architectural evidence. This is a diverse selection, not an exhaustive census.

The report spans Go, Rust, C, TypeScript, Python/Cython, OCaml, Haskell, and Java, and ranges from library-sized implementations to daemons and monorepo subsystems. Each retained repository has a verified canonical GitHub URL, separately read primary material, and at least two justified criteria. No repository was cloned or executed, and no benchmark claim was independently reproduced.

Important boundaries and exclusions:

- General object stores and key-value databases were not included merely because a caller could choose a hash as a key. For example, the C++ search surfaced NuDB, but this report prioritizes implementations that define an actual CAS protocol, representation, or lifecycle.
- Protocol-only repositories, awesome lists, example applications, thin wrappers, and tutorial-style distributed-file projects were not counted as storage implementations. Newer candidates such as OpenXet and casq remain outside this selection because the completed primary-source inspection was concentrated on the retained systems; exclusion is not a quality verdict.
- Shared lineage is explicit: desync is a separate casync-compatible implementation; Noms is the historical ancestor of Dolt; bup reuses Git formats. These relationships do not represent independent invention of every component.
- Git is an official source mirror; Venti is a historical subsystem in plan9port; Noms is archived. Borg 2 and the inspected iroh-blobs development line carry explicit readiness warnings. Xet-core supplies client machinery rather than the full hosted service. NativeLink's inspected license header is flagged, and BuildBuddy's OSS cache scope is distinguished from enterprise features.
- A recent push was not used as evidence for C4 or as a guarantee of maintenance. C4 is assigned where read histories demonstrate changes and compatibility or complexity-management work. Several design documents describe goals or historical decisions; the entries identify those as such rather than converting them into unqualified present-day guarantees.

The strongest study path depends on the question: Kubo and Helia expose reachability races; iroh-blobs exposes verified partial retrieval; Venti and Perkeep separate archival identity from physical layout; restic and Borg expose authenticated packing and recovery; Buildbarn exposes eviction-sensitive cache semantics; and Irmin and Dolt expose persistent-graph storage under changing readers, writers, and layouts.
