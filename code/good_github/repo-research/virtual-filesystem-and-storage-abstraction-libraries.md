# Virtual filesystem and storage abstraction libraries

Research date: **2026-10-09**.

This selection covers reusable libraries that present files, directories, archives, object stores, or mounted key spaces through a common application interface. It includes in-memory implementations whose filesystem semantics are substantial enough to study, plus the relevant library subsystems of three larger projects. It excludes kernel filesystems, distributed storage servers, synchronization applications, and most individual service adapters. The 25 repositories below are a source-reading guide, not a ranking or a claim that every backend provides identical guarantees.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial paths, resource lifetimes, or failure handling.
- **C2 — Abstraction:** substantial reusable interfaces and composition mechanisms supporting multiple uses.
- **C3 — Performance:** concrete I/O, memory, latency, or concurrency constraints addressed through understandable structure.
- **C4 — Evolution:** sustained development evidenced by compatibility work, tests, migrations, or complexity management; age alone does not qualify.

The criteria assessments are engineering judgments grounded in the linked primary material. Repository pages and additional implementation or design sources were opened for every entry. Links to moving branches describe the inspected state, rather than a permanent API promise. Maintenance is not inferred from stars or repository age; specific status qualifications appear where relevant.

## Object storage and streaming data access

### 1. [fsspec/filesystem_spec](https://github.com/fsspec/filesystem_spec)

**Python — filesystem interfaces, buffered remote files, and composable storage access.** Study how a filesystem abstraction serves distributed data processing while remaining usable by ordinary file-consuming Python code.

- **C2:** Serializable filesystem instances and delayed `OpenFile` objects let workers reconstruct access without serializing live file handles. URL chaining composes archive access, remote storage, and local caches; dictionary-style mappings expose another reusable view of the same storage. The [features guide](https://filesystem-spec.readthedocs.io/en/latest/features.html) explains these boundaries.
- **C1 / C3:** Buffered range access avoids downloading entire objects, while listing-cache invalidation and several local caching policies make freshness and memory tradeoffs explicit. Transactions defer writes, but the guide describes them as backend-specific and only semi-atomic; it also distinguishes the thread/process guarantees of different caches. The [base filesystem and buffered-file implementation](https://github.com/fsspec/filesystem_spec/blob/master/fsspec/spec.py) is the second entry point.

### 2. [apache/opendal](https://github.com/apache/opendal)

**Rust core with language bindings — uniform access to heterogeneous storage services.** The relevant subsystem is the Rust storage core and its service/layer architecture; bindings are not counted separately.

- **C2:** The current architecture keeps backend implementations typed, erases them at a shared service boundary, and composes them into `Operator`. Operations and runtime resources have separate layer hooks. Study the [internal architecture overview](https://github.com/apache/opendal/blob/main/core/core/src/docs/internals/mod.rs) for this separation.
- **C1 / C3:** Services advertise capabilities that operators validate before dispatch. Their contracts require preserving options, atomicity, structured errors, cancellation, and cleanup. Concrete reader/writer body types avoid dynamic dispatch inside backend implementations until the deliberate erasure boundary. The [service implementation guide](https://github.com/apache/opendal/blob/main/core/core/src/docs/internals/accessor.rs) also requires capability-specific conformance checks against actual services. These are documented contracts, not proof that every provider is equivalent.

### 3. [apache/arrow-rs-object-store](https://github.com/apache/arrow-rs-object-store)

**Rust — asynchronous object-storage API.** This is the standalone `object_store` repository, rather than another entry for the Arrow monorepo. It offers a useful comparison with interfaces that try to make object stores look like POSIX filesystems.

- **C2:** `ObjectStore` supports cloud, local, memory, and custom implementations, with composable throttling and request-limiting adapters. Its deliberately stateless object operations make the abstraction's scope clear. Start with the [crate's architectural documentation and trait implementation](https://github.com/apache/arrow-rs-object-store/blob/main/src/lib.rs).
- **C1 / C3:** The same source explains atomic object replacement, conditional operations, multipart upload semantics, and vectored I/O. It explicitly cautions about translating these semantics into cursor-based buffered readers and writers. The design keeps object-store preconditions visible instead of silently assuming filesystem behavior; the [rendered API guide](https://docs.rs/object_store/latest/object_store/) provides the navigable interface reference.

### 4. [google/go-cloud](https://github.com/google/go-cloud)

**Go — the Go CDK's `blob` subsystem.** Counted once for its portable blob library, not for its unrelated database or messaging APIs. The repository says its focus is maintaining existing APIs and drivers and describes the APIs as alpha.

- **C2:** A portable bucket interface sits above driver interfaces, while `As` hooks retain access to provider-specific capabilities. This is a substantial example of balancing portability with escape hatches. The [driver contract](https://github.com/google/go-cloud/blob/master/blob/driver/driver.go) defines range reads, paginated listings, writers, metadata, and error translation.
- **C1:** That contract distinguishes eventual listing consistency, visibility before writer close, cancellation cleanup, and conditional creation. The reusable [driver conformance suite](https://github.com/google/go-cloud/blob/master/blob/drivertest/drivertest.go) tests canceled writes and preservation of existing contents. It also records an unfilled test case for cancellation after multipart chunks have been uploaded, which limits any claim of comprehensive failure coverage.

### 5. [fs2-blobstore/fs2-blobstore](https://github.com/fs2-blobstore/fs2-blobstore)

**Scala — FS2 stream-based access to hierarchical and flat stores.** A useful functional-programming counterpart to callback, file-handle, and trait-object designs.

- **C2:** `Store[F, BlobType]` expresses reads and listings as streams, writes as pipes, and operations through an effect type. It separates URL validation from path-store delegation and includes rotating output streams. Read the [storage contract](https://github.com/fs2-blobstore/fs2-blobstore/blob/master/core/src/main/scala/blobstore/Store.scala).
- **C1 / C3:** The [S3 implementation](https://github.com/fs2-blobstore/fs2-blobstore/blob/master/s3/src/main/scala/blobstore/s3/S3Store.scala) manages multipart uploads with bounded channels, pooled buffers, part-number limits, and resource finalizers. Successful stream completion builds the completion request; other exit cases issue an abort. Its existence check before a non-overwriting write is separate from the upload, so it should not be read as an atomic conditional-create guarantee.

## Composable filesystems and reusable conformance models

### 6. [PyFilesystem/pyfilesystem2](https://github.com/PyFilesystem/pyfilesystem2)

**Python — whole-filesystem objects and common filesystem algorithms.** A useful established design reference; the inspected documentation identifies release 2.4.16, and this report does not infer a current release cadence from the repository's presence.

- **C2 / C1:** A small set of essential methods supports generic walking, copying, metadata, and subdirectory views. The [implementer guide](https://pyfilesystem2.readthedocs.io/en/latest/implementers.html) specifies compatible signatures and exception behavior, thread safety, and a reusable `FSTestCases` suite. It also identifies operations such as `scandir` that remote backends should specialize to reduce round trips.
- **C4:** The [changelog](https://github.com/PyFilesystem/pyfilesystem2/blob/master/CHANGELOG.md) records successive years of Python compatibility, standardized root-deletion behavior, timestamp precision fixes, move-error cleanup, and regression-test improvements. These changes show the work required to maintain a common contract across implementations, rather than merely accumulating adapters.

### 7. [spf13/afero](https://github.com/spf13/afero)

**Go — filesystem interfaces with memory, native, archive, and layered implementations.** Particularly useful for studying composition through ordinary filesystem operations.

- **C2 / C1:** [Copy-on-write implementation](https://github.com/spf13/afero/blob/master/copyOnWriteFs.go) combines a base and writable overlay. It copies base files before metadata changes as well as content changes, distinguishes missing paths from other errors, and documents restrictions on directory opening and renaming base-only files.
- **C3:** [Cache-on-read implementation](https://github.com/spf13/afero/blob/master/cacheOnReadFs.go) has explicit miss, stale, hit, and local-only states. Expiration checks use modification times, and the comments explain timestamp-resolution limits and write forwarding. These two similarly shaped wrappers provide different semantics, making their comparison more instructive than treating all filesystem layering as interchangeable.

### 8. [go-git/go-billy](https://github.com/go-git/go-billy)

**Go — storage-independent filesystem contracts originating in go-git.** Study how a consumer with demanding file behavior separates required operations from optional capabilities.

- **C2:** [Core interfaces](https://github.com/go-git/go-billy/blob/main/fs.go) compose basic files, directories, temporary files, links, and rooted views. Separate interfaces and capability bits describe locking and durable synchronization; supporting a write API is explicitly distinguished from the backing storage being writable.
- **C1:** The file contract requires concurrent `ReadAt` behavior, distinguishes `Stat` from `Lstat`, and specifies root-boundary errors. The [bounded OS implementation](https://github.com/go-git/go-billy/blob/main/osfs/os_bound.go) is a concrete study of rooted operations, host-path interpretation, ancestor creation, and cleanup of opened root handles. Capability negotiation is important here because not every backend can supply every guarantee.

### 9. [avfs/avfs](https://github.com/avfs/avfs)

**Go — filesystem and operating-system behavior emulation.** This smaller project is distinctive for modeling identities and foreign-OS semantics, rather than only replacing disk access with a map.

- **C1:** The [specification](https://github.com/avfs/avfs/blob/master/spec.md) explains immutable user identity, views that share storage while retaining distinct identity state, and an atomic current-directory pointer. Its rationale addresses permission checks changing identity mid-operation and accidental copying of synchronization state.
- **C2:** The same document separates filesystem, identity-manager, path, feature, and error interfaces. Memory, native, restricted-root, read-only, and fault-injection implementations share a conformance model. The specification explicitly treats identity management as test/development infrastructure and does not make performance a primary goal. The [core VFS source](https://github.com/avfs/avfs/blob/master/vfs.go) is a second entry point into the contracts.

### 10. [hack-pad/hackpadfs](https://github.com/hack-pad/hackpadfs)

**Go — small filesystem capability interfaces, including browser/Wasm storage.** Study a design that extends `io/fs` through optional operations instead of requiring every backend to implement one large interface.

- **C2:** [Filesystem interfaces and dispatch helpers](https://github.com/hack-pad/hackpadfs/blob/main/fs.go) let implementations supply only supported capabilities. A common key-value filesystem underlies memory and IndexedDB use, alongside mounted and streaming-tar implementations described by the repository.
- **C1:** The [key-value implementation](https://github.com/hack-pad/hackpadfs/blob/main/keyvalue/fs.go) validates paths, distinguishes missing parents from non-directory parents, checks nonempty-directory deletion, and uses a transaction for file rename. Its recursive directory-rename path explicitly notes incomplete recovery on failure. This makes it valuable for studying where transactional primitives do and do not extend to compound filesystem operations.

### 11. [manuel-woelker/rust-vfs](https://github.com/manuel-woelker/rust-vfs)

**Rust — physical, memory, embedded, alternate-root, and overlay filesystems.** A compact implementation suited to studying asset loading and testable filesystem consumers.

- **C2 / C1:** The [overlay implementation](https://github.com/manuel-woelker/rust-vfs/blob/master/src/impls/overlay.rs) merges directory entries, gives upper layers precedence, copies files up before appending, and records lower-layer deletions in whiteout files. That is substantive namespace behavior beyond an interchangeable `open` function.
- **C4:** The repository's dated changelog spans 2016–2026 and records a trait-based redesign, exported conformance tests, concurrency fixes in directory creation, memory-file flush visibility, and Rust-version management. The [reusable test macros](https://github.com/manuel-woelker/rust-vfs/blob/master/src/test_macros.rs) are a second entry point. The README also announces an intention to sunset its current async feature; do not assume equal long-term direction for the sync and async APIs.

## JVM, .NET, and C++ filesystem models

### 12. [google/jimfs](https://github.com/google/jimfs)

**Java — in-memory implementation of `java.nio.file`.** Study a filesystem model behind standard Java APIs, including channels, links, directory streams, watchers, and configurable path conventions.

- **C1:** [FileSystemView](https://github.com/google/jimfs/blob/master/jimfs/src/main/java/com/google/common/jimfs/FileSystemView.java) coordinates store locks, rejects invalid directory moves, distinguishes same-store moves from copy-and-delete, and handles supported attribute views during cross-filesystem copying.
- **C2 / C3:** The public NIO integration supports many existing consumers, while [RegularFile](https://github.com/google/jimfs/blob/master/jimfs/src/main/java/com/google/common/jimfs/RegularFile.java) separates file locking from block-backed byte storage and geometric block-list growth. The README cautions that POSIX permission attributes are not enforced and that behavior does not exactly reproduce every operating system; it is a model with stated boundaries.

### 13. [apache/commons-vfs](https://github.com/apache/commons-vfs)

**Java — URI-based filesystem providers and virtual file objects.** The relevant implementation is `commons-vfs2`; protocol modules are counted together.

- **C2:** The [API and configuration guide](https://commons.apache.org/proper/commons-vfs/api.html) separates `FileSystemManager`, `FileObject`, provider registration, archive resolution, temporary storage, and replication. Classpath provider discovery makes the extension boundary concrete.
- **C1 / C3:** [AbstractFileObject](https://github.com/apache/commons-vfs/blob/master/commons-vfs2/src/main/java/org/apache/commons/vfs2/provider/AbstractFileObject.java) manages synchronized attachment, cached type/children information, content closure, and exception translation. The guide explains soft-reference file-object caching and warns that closing a globally shared filesystem affects all threads. Study it for the interaction between remote metadata latency and shared object lifetimes.

### 14. [xoofx/zio](https://github.com/xoofx/zio)

**C# — uniform paths and composable .NET filesystems.** Physical, memory, ZIP, aggregate, mount, subdirectory, and read-only views support both application access and testing.

- **C2:** The repository explains how `IFileSystem`, normalized `UPath` values, filesystem entries, and watcher interfaces work across composed filesystems. This is a broader design than wrapping static `System.IO` methods for mocking.
- **C1 / C3:** The [memory implementation](https://github.com/xoofx/zio/blob/main/src/Zio/FileSystems/MemoryFileSystem.cs) uses filesystem-level and node-level locking, explicit shared/exclusive access, lock cleanup, and coordinated directory operations. Deep cloning takes an exclusive filesystem lock, while ordinary directory operations can enter shared filesystem access. Study how the implementation reconciles concurrency with .NET file-sharing and replacement semantics. Its [documentation directory](https://github.com/xoofx/zio/tree/main/doc) provides the API reading path.

### 15. [cginternals/cppfs](https://github.com/cginternals/cppfs)

**C++ — object-oriented local and SSH filesystem backends.** A smaller codebase with a useful separation between handles, streams, and backend ownership. No current maintenance cadence is asserted.

- **C2:** [AbstractFileSystem](https://github.com/cginternals/cppfs/blob/master/source/cppfs/include/cppfs/AbstractFileSystem.h) is the extension boundary beneath the public file-handle API. The repository documents unified paths, URL selection, directory traversal, tree differences, and the limitation that custom backends cannot simply be registered with the global opener.
- **C3:** [FileHandle implementation](https://github.com/cginternals/cppfs/blob/master/source/cppfs/source/FileHandle.cpp) dispatches same-filesystem copies and moves to backend-native methods, falling back to stream transfer for different filesystems and refreshing destination metadata afterward. This directly exposes the cost boundary between native operations and cross-backend I/O. The fallback move is copy-then-delete, so it is not a cross-filesystem atomic move.

## PHP storage abstractions

### 16. [thephpleague/flysystem](https://github.com/thephpleague/flysystem)

**PHP — common storage operations over local, remote, and archive adapters.** Study the split between application-facing operations and provider implementations.

- **C2:** [Filesystem](https://github.com/thephpleague/flysystem/blob/3.x/src/Filesystem.php) centralizes configuration merging, normalized paths, stream operations, visibility propagation, and URL-generation capabilities over an injected adapter. The repository contains distinct adapters and common adapter-test utilities.
- **C1:** [Path normalization](https://github.com/thephpleague/flysystem/blob/3.x/src/WhitespacePathNormalizer.php) handles separator conversion, invalid Unicode/control input, and traversal above the logical root. The filesystem source checks stream resources and rewinds only when seekable. These details are useful examples of enforcing shared preconditions without pretending that all backend streams or permission models are identical.

### 17. [KnpLabs/Gaufrette](https://github.com/KnpLabs/Gaufrette)

**PHP — filesystem/file objects over adapters, including database-backed storage.** Useful for comparing a file-object registry and adapter capability model with Flysystem's operation-oriented facade.

- **C2 / C1:** [Filesystem implementation](https://github.com/KnpLabs/Gaufrette/blob/master/src/Gaufrette/Filesystem.php) validates keys, translates unsuccessful adapter results into exceptions, applies overwrite policy, and keeps its file-object registry consistent during rename and deletion. Its existence checks should not be mistaken for atomic exclusion of competing writers.
- **C4:** The [changelog](https://github.com/KnpLabs/Gaufrette/blob/master/CHANGELOG.md) documents successive PHP compatibility transitions through PHP 8.5, third-party SDK breakages, retirement of obsolete adapters, shared adapter tests, and expanded functional CI. The dated 1.0.0 entry is July 2026; the README's older statement that no stable release exists is stale. This is a particularly useful record of the compatibility burden behind a reusable adapter ecosystem.

## Browser filesystems and mounted key spaces

### 18. [streamich/memfs](https://github.com/streamich/memfs)

**TypeScript — in-memory Node filesystem semantics and browser File System API adapters.** Count the repository's packages once; the inspected tree separates the filesystem core from API adapters.

- **C2:** The repository supports Node-style APIs, browser file-system handles, and adapters in both directions. [Node volume implementation](https://github.com/streamich/memfs/blob/master/packages/fs-node/src/volume.ts) shows the substantial compatibility surface built over the common model.
- **C1:** [Superblock](https://github.com/streamich/memfs/blob/master/packages/fs-core/src/Superblock.ts) separates inodes, links, and open descriptors, enforces a symlink-hop budget, resolves intermediate symlinks for `lstat`, and checks traversal permissions. The README explicitly lists watcher differences from native systems, including semantic path watching and event delivery timing. It is a useful compatibility study without assuming native watcher behavior is reproduced exactly.

### 19. [zen-fs/core](https://github.com/zen-fs/core)

**TypeScript — mounted, cross-platform Node-style filesystems.** The selected repository includes memory, fetch, message-port, passthrough, shared-buffer, and copy-on-write backends; external backend packages are not separate entries.

- **C2:** [FileSystem base class](https://github.com/zen-fs/core/blob/main/src/internal/filesystem.ts) supplies the backend contract beneath mounting and Node API emulation. It provides a place to compare synchronous and asynchronous operations, stream access, and capability attributes.
- **C1:** [Copy-on-write backend](https://github.com/zen-fs/core/blob/main/src/backends/cow.ts) manages a readable base, writable layer, and a deletion journal so removed lower-layer entries do not reappear. It validates the writable backend and coordinates initialization of both sides. Study this as overlay state management; the presence of a journal alone does not establish database-style crash atomicity.

### 20. [isomorphic-git/lightning-fs](https://github.com/isomorphic-git/lightning-fs)

**JavaScript — persistent browser filesystem with a deliberately limited Node-compatible API.** Designed around the operations needed by isomorphic-git, rather than full Node filesystem emulation.

- **C3:** The repository explains the split between in-memory directory metadata and IndexedDB file contents, delayed metadata persistence, and the decision to avoid an unconditional in-memory content cache. This gives a concrete latency-versus-memory design to study.
- **C1 / C2:** [DefaultBackend](https://github.com/isomorphic-git/lightning-fs/blob/main/src/DefaultBackend.js) acquires exclusive access before activating cached metadata and saves metadata before releasing it. The current code selects a Web Locks mutex when available and an IndexedDB-based alternative otherwise. Shared tabs/workers therefore coordinate through serialized access; delayed persistence is not an immediate-durability promise. The repository also documents replacement backends and an optional HTTP read fallback.

### 21. [unjs/unstorage](https://github.com/unjs/unstorage)

**TypeScript — asynchronous key-value storage with filesystem-style mount routing.** Included as a storage abstraction, not as a POSIX filesystem implementation.

- **C2 / C1:** [Storage core](https://github.com/unjs/unstorage/blob/main/src/storage.ts) normalizes keys, selects mounts by longest prefix, masks parent-driver keys covered by nested mounts, and manages watcher and driver cleanup. Metadata and raw values form explicit parts of the abstraction. These are meaningful namespace invariants even though the public API is key-value oriented.
- **C3:** The same implementation groups multi-item operations by mounted driver and runs independent batches concurrently, allowing native batch methods where available. Study it for a small routing core that preserves backend-specific opportunities. Its transaction-option types and snapshot helpers should not be read as a universal transaction or consistent-snapshot guarantee.

## Native libraries and substantial library subsystems

### 22. [icculus/physfs](https://github.com/icculus/physfs)

**C — PhysicsFS archive and asset filesystem abstraction.** Particularly relevant to games, mod loading, and packaged application resources, while the library interface remains reusable.

- **C2:** The [public header and design documentation](https://github.com/icculus/physfs/blob/main/src/physfs.h) explain a prioritized search path, one write directory, archive mounting at virtual paths, and portable pathname notation. A single hierarchy can combine native directories and multiple archive formats.
- **C1:** The same material specifies rejection of dangerous path components, symbolic links disabled by default, and the distinction between synchronized library state and unsynchronized per-file access. Concurrent use of the same file handle requires caller coordination. It also explains UTF-8 conversion and older archive naming limitations. These explicit boundaries make it a strong study of portability and containment without overstating thread safety.

### 23. [GNOME/glib](https://github.com/GNOME/glib)

**C — the GIO filesystem and stream subsystem. Official read-only GitHub mirror.** The repository identifies GNOME GitLab as upstream. Only GIO's file/storage abstraction is in scope; GLib is counted once.

- **C2:** The [GIO architecture overview](https://docs.gtk.org/gio/overview.html) separates immutable file identifiers, file information, enumerators, streams, volumes, and mounts. Local implementations live in GIO; remote implementations belong to the separate GVfs package, with out-of-process backends.
- **C1 / C3:** [GFile implementation and API contracts](https://github.com/GNOME/glib/blob/main/gio/gfile.c) distinguish display names from actual path bytes, account for aliases, and define cancellable replacement with optional ETag checks and backup failures. The overview explains async completion in the initiating main context and why blocking filesystem calls can freeze a UI. Study the API's resource and completion model, not the entire GLib codebase indiscriminately.

### 24. [KDE/kio](https://github.com/KDE/kio)

**C++/Qt — network-transparent file jobs and protocol workers. Official read-only GitHub mirror**, as identified by the [KDE GitHub organization](https://github.com/KDE).

- **C2:** The repository describes extensible protocol access used by file managers and file dialogs. [WorkerBase](https://github.com/KDE/kio/blob/master/src/core/workerbase.h) defines a concrete worker/application protocol for data, directory entries, metadata, and operation results, including the worker's socket-driven execution model.
- **C1 / C3:** The same contract negotiates resumption according to both endpoints' capabilities and specifies overwrite, partial-file, permissions, and modification-time behavior. MIME discovery can hold and reuse a download worker when handing the resource to an application, avoiding a second request. This is a distinctive example of making remote I/O both correct and responsive across application boundaries.

### 25. [OSGeo/gdal](https://github.com/OSGeo/gdal)

**C/C++ — GDAL's VSI virtual filesystem layer.** GDAL is a geospatial library, but the selected subsystem is the reusable I/O abstraction in `port`, not its format-driver catalog.

- **C2:** The [VSI guide](https://gdal.org/en/stable/user/virtual_file_systems.html) describes composable path-prefix handlers for memory, archives, HTTP ranges, and cloud stores. An archive handler can operate over a network handler without a format consumer implementing that combination itself.
- **C1 / C3:** The guide distinguishes sequential streaming from random access, documents restrictions on interleaving archive reads and writes, and explains adaptive request sizes, shared LRU caching, and seek-optimized ZIP indexing. These choices address remote analytical workloads whose access patterns differ sharply from ordinary downloads. [Virtual handle and handler interfaces](https://github.com/OSGeo/gdal/blob/master/port/cpl_vsi_virtual.h) provide the source entry point. Handler capabilities vary; the guide also identifies format drivers that cannot use the virtual layer.

## Coverage, search process, and limitations

Discovery used **18 distinct query formulations**, followed by repository and source verification. Search angles included Python data-access filesystems; Rust object storage and overlays; Go filesystem contracts and conformance testing; Java NIO and virtual providers; PHP adapter ecosystems; browser persistence and Node emulation; C/C++ archive and asset libraries; .NET virtual filesystems; GIO/KIO desktop I/O; and functional-language streaming storage. Later searches for embedded assets, union mounts, and conformance suites increasingly returned already-covered designs, thin adapters, filesystem-image tools, or full mountable systems. The final functional-language pass added fs2-blobstore.

The selection spans Python, Rust, Go, Scala, Java, C#, PHP, TypeScript/JavaScript, C, and C++. Smaller projects were retained for distinctive mechanisms, not popularity: AVFS models immutable user views, hackpadfs combines optional interfaces with transactional key-value storage, rust-vfs exposes whiteout overlays, and cppfs separates native operations from cross-backend streaming.

Individual fsspec cloud adapters, additional Flysystem adapters, and language bindings were not counted independently. The older PyFilesystem generation and additional related browser filesystem projects were not added merely to duplicate families already represented. Kernel VFS code, FUSE/Dokan hosting frameworks, distributed storage systems, sync clients, and archive-mount applications were outside the chosen application-library boundary. TrueVFS was discovered, but a canonical substantive GitHub repository was not established in this pass, so it was not retained. Searches also surfaced newer agent-oriented filesystems; their broader execution or mounted-system scope was not pursued here.

Verification used live web search, official documentation, public GitHub repository pages, and direct reads of source files and changelogs. The unauthenticated GitHub API hit a shared rate limit; repository-page metadata and public source reads supplied the remaining canonical URL and branch checks. Some KDE documentation endpoints returned access errors, so mirror status was verified on KDE's official GitHub organization and implementation evidence came from the mirror itself. No selected repository displayed an archive banner at inspection. This observation is not a maintenance guarantee.

No candidate code was executed, dependencies installed, or performance benchmarks reproduced. Contract documentation and implementation structure support the criteria judgments; they do not establish universal backend conformance, security certification, crash safety, or performance superiority. Particularly useful limitations are called out in the individual entries rather than hidden by the shared abstraction.
