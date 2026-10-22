# Offline-first data replication frameworks

Research date: **2026-10-09**.

This report selects 26 substantive GitHub repositories for studying software that keeps application data usable locally and reconciles changes after disconnection. It covers document replication protocols, relational synchronization, optimistic application state, CRDT libraries, and peer-to-peer storage. Some entries are complete application data layers; others are explicitly identified building blocks or server components. Enterprise database synchronization is included where disconnected operation is a documented design case. Ordinary cluster replication, transport libraries alone, and applications that merely consume a sync engine are outside the scope.

Each linked repository heading is a verified canonical GitHub location. The accompanying implementation or documentation links were also opened and read. Criteria are judgments grounded in those sources, not correctness certifications or maintenance recommendations. Source availability does not imply a uniform open-source license across this selection.

**Criteria legend**

- **C1 — Difficult correctness:** concurrency, convergence, invariants, adversarial data, or recovery from partial failure.
- **C2 — Reusable abstractions:** substantial interfaces or data models that serve different applications, storage systems, or transports.
- **C3 — Performance with structure:** concrete mechanisms for controlling computation, I/O, memory, or synchronization work within an understandable architecture.
- **C4 — Sustained evolution:** years of development accompanied by evidence of compatibility, testing, or complexity management. Age and recent activity alone do not establish this criterion. This report qualifies entries primarily through C1–C3 rather than assigning C4 without a longitudinal audit.

## Document databases and replication protocols

### 1. [apache/pouchdb](https://github.com/apache/pouchdb)

**JavaScript — local document database and CouchDB-compatible replication.** Study how a common document API spans browser and Node storage while preserving replication semantics. The former `pouchdb/pouchdb` URL redirects to this Apache repository; the repository identifies the project as incubating.

- **C1:** Revision trees preserve conflicting versions, while a deterministic winner makes ordinary reads consistent between replicas. Live replication must also handle reconnection, cancellation, and deletion tombstones; destroying a local database is deliberately different from replicating deletions. These distinctions are explained in the [replication guide](https://pouchdb.com/guides/replication.html).
- **C2:** Directional replication and bidirectional `sync` compose across local and remote databases independently of their storage adapter. The [testing guide](https://github.com/apache/pouchdb/blob/master/TESTING.md) makes that abstraction concrete through browser, Node, and HTTP adapter combinations and integration tests against CouchDB.

**Entry points:** the replication guide for semantics; `TESTING.md` for the compatibility and adapter test matrix.

### 2. [apache/couchdb](https://github.com/apache/couchdb)

**Erlang — document server and reference implementation of a disconnected replication protocol.** The relevant subsystem is the replicator, rather than CouchDB's internal cluster replication. It is useful for understanding the server side of the PouchDB/CouchDB family without treating the two implementations as interchangeable.

- **C1:** Replication combines MVCC revision histories, conflicting leaf revisions, change sequence identifiers, and persisted checkpoints. Recovery must determine common replication history rather than assume both endpoints recorded the same last operation. Sequence identifiers also cannot be assumed to be simple integers. See the [replication protocol specification](https://docs.couchdb.org/en/stable/replication/protocol.html).
- **C2:** The same specification defines an HTTP/JSON protocol between independently implemented source and target databases, including change discovery, revision transfer, and replication logs. That separation is a reusable interoperability boundary, not merely a database-specific background job.

**Entry point:** the protocol specification, including its checkpoint and replication-log definitions and links to the reference replicator.

### 3. [pubkey/rxdb](https://github.com/pubkey/rxdb)

**TypeScript — reactive local database with a backend-independent replication layer.** Particularly useful for studying a protocol that can sit over application-specific HTTP endpoints rather than requiring a particular server database.

- **C1:** A pushed change contains both the assumed master state and the new local state. The backend reports conflicts when that assumption fails. Initial synchronization and reconnects use checkpoint iteration; live observation uses a stream with an explicit resynchronization signal when events may have been missed. See the [replication architecture](https://rxdb.info/replication.html).
- **C2:** Pull, push, checkpoint, conflict-handler, and stream interfaces separate transport and backend choices from local persistence.
- **C3:** Batched documents reduce serialization and storage overhead, while browser leader election avoids every tab independently performing replication. These mechanisms are described alongside the protocol in the same architecture guide.

**Entry point:** the replication documentation, especially checkpoint iteration versus event observation.

### 4. [couchbase/couchbase-lite-core](https://github.com/couchbase/couchbase-lite-core)

**C++ — native embedded database and replication core beneath Couchbase Lite SDKs.** This is a source-available internal engine; its repository warns that internal APIs are unstable, and some enterprise components are separate. Study the implementation through SDK architecture rather than assuming it is a stable standalone C++ application framework.

- **C1:** The [replicator overview](https://github.com/couchbase/couchbase-lite-core/blob/master/docs/overview/Replicator.md) decomposes work into actors, pushers, pullers, checkpoints, and database access. On reconnect, the public wrapper creates a new connection-scoped replicator, reducing the state that must be reset correctly.
- **C3:** Actor queues serialize component state while thread pools permit concurrency. Batchers flush by time or size, database access uses pooling, and BLIP multiplexes request/reply traffic over WebSockets. The component boundaries make the interaction of concurrency and I/O inspectable.

**Entry point:** `docs/overview/Replicator.md`. It is a 2021/LiteCore 3.0 design overview with an explicitly dated diagram, so use it as an architectural map rather than a complete specification of today's implementation.

## Relational and application-state synchronization

### 5. [vlcn-io/cr-sqlite](https://github.com/vlcn-io/cr-sqlite)

**C and Rust — SQLite extension for convergent replicated tables.** This places replication metadata inside the database while leaving transport to the application. The useful study target is the implemented CRR/change-table model; proposals for later versions should not be confused with shipped behavior.

- **C1:** Replicated tables record per-column versions and site/database version metadata. Incoming changes enter through `crsql_changes`, making conflict handling part of SQL storage semantics. The repository's API documents conversion to replicated relations and schema-alteration boundaries.
- **C2:** Applications can retain ordinary local tables alongside replicated tables and exchange changes over their chosen network. The [whole-CRR synchronization guide](https://vlcn.io/docs/cr-sqlite/networking/whole-crr-sync) explains both this separation and the requirement for matching replicated schemas.
- **C3:** Per-peer database-version cursors support incremental transfer; applications can select change subsets by table, key, and version rather than resending complete databases.

**Entry points:** the repository's SQL API examples and the whole-CRR synchronization guide.

### 6. [powersync-ja/powersync-service](https://github.com/powersync-ja/powersync-service)

**TypeScript — server-side synchronization service for offline SQLite clients.** This entry covers the downstream replication service, not the entire client SDK and application upload path. Its distinctive contribution is sharing replication work across many partially overlapping client datasets.

- **C2:** Database change capture, synchronization rules/streams, and bucket storage are separate concerns. The [service architecture](https://docs.powersync.com/architecture/powersync-service) describes source connectors and interchangeable MongoDB/PostgreSQL storage for synchronization state.
- **C3:** Parameterized buckets represent reusable subsets of source data. Clients sharing a bucket share its operation history; incremental delivery and history compaction reduce repeated work and accumulated storage. This is a concrete architecture for scaling selective replication, rather than simply broadcasting every source change.

**Entry point:** the service architecture, particularly bucket histories and the distinction between source databases and bucket storage. The repository contains substantial service implementation, but it should not be mistaken for a standalone bidirectional client library.

### 7. [Nozbe/WatermelonDB](https://github.com/Nozbe/WatermelonDB)

**JavaScript/Flow with native database integration — reactive local database and application-defined synchronization.** Study its synchronization subsystem for a pragmatic server-authoritative design that allows local edits throughout a sync cycle.

- **C1:** The [sync implementation document](https://watermelondb.dev/docs/Implementation/SyncImpl) explains per-column client-wins conflict handling using change-tracking metadata. It also covers edits made during upload, replay after failure before checkpoint persistence, and rejecting a push when the server changed after the corresponding pull.
- **C2:** The protocol specifies client/server responsibilities while leaving the backend implementation to the application. This makes the handling of creates, updates, deletes, and migration-aware pulls reusable across backend stacks.
- **C3:** The database's lazy loading and native-thread SQL architecture avoid materializing the entire dataset as JavaScript objects; this complements its local-first synchronization model.

**Entry point:** `SyncImpl`, including its failure cases. The inspected guide is versioned 0.27.1; it is an implementation explanation, not a guarantee of API compatibility across releases.

### 8. [Mimetis/Dotmim.Sync](https://github.com/Mimetis/Dotmim.Sync)

**C# — provider-based synchronization between relational databases, including SQLite clients.** It broadens the selection beyond browser ecosystems: applications edit a local relational database and later invoke a synchronization agent.

- **C1:** The [conflict guide](https://dotmimsync.readthedocs.io/Conflict.html) distinguishes competing inserts, updates, and deletes. Resolution can select either side, merge a row, or roll back synchronization; callbacks expose the database connection and transaction, making conflict policy interact explicitly with transactional state.
- **C2:** A shared `SyncAgent` composes client and server providers, with configurable table sets and conflict hooks. The [official introduction](https://dotmimsync.readthedocs.io/) demonstrates SQLite paired with SQL Server and documents additional relational providers.

**Entry points:** the conflict guide and provider-based introduction. These inspected documentation pages identify themselves as 0.9.5 and describe a beta; do not infer current support guarantees or current API versions from them.

### 9. [jumpmindinc/symmetric-ds](https://github.com/jumpmindinc/symmetric-ds)

**Java — heterogeneous database synchronization for intermittently connected sites.** Its relevant use case is distributed local databases such as branch or store nodes, rather than only always-connected server replication.

- **C1:** The [user guide](https://symmetricds.sourceforge.net/doc/3.8/html/user-guide.html) describes transactionally tracked batches, acknowledgments, and retries. Its offline-node mode continues capturing and batching changes, but moves batches through files instead of HTTP; applications must transport those files.
- **C2:** Capture, routing, transformation, extraction, transfer, and loading are separate subsystems. Routers select target nodes and subsets of rows, while Java extension points customize loading and other stages.
- **C3:** Batching and channels provide explicit units for scheduling and controlling synchronization work across heterogeneous databases.

**Entry point:** the user guide's Architecture, Channels, and Offline Synchronization sections. This is historical 3.8 documentation; the verified repository currently exposes a `release/3.18` branch. The older guide is used for design study, not current configuration instructions. Commercial Pro features are outside this entry's scope.

### 10. [aspen-cloud/triplit](https://github.com/aspen-cloud/triplit)

**TypeScript — client, embedded database, and synchronization server monorepo.** Study the boundary between optimistic local transactions and accepted server changes, together with incremental query updates.

- **C1:** The [client sync engine](https://github.com/aspen-cloud/triplit/blob/main/packages/client/src/sync-engine.ts) separates in-flight writes from subsequently accumulated writes using buffered state. Its write synchronization logic also reconstructs rollback data and removes specific pending transactions, exposing the subtle bookkeeping behind optimistic updates.
- **C2:** The repository combines storage abstractions, schema/query facilities, client synchronization, and server components. Multiple application bindings reuse that shared model rather than defining separate replication protocols.
- **C3:** The implementation applies changes to incrementally maintained query views, and the repository describes delta synchronization rather than full repeated dataset transfer.

**Entry point:** `packages/client/src/sync-engine.ts`, especially buffered write submission, rollback, and pending-write cleanup. The monorepo is counted once.

### 11. [rocicorp/mono](https://github.com/rocicorp/mono)

**TypeScript — official public repository containing Replicache and Zero.** The offline replication study target here is **Replicache**; Zero is not counted as another repository.

- **C1:** Replicache keeps pending local mutations over a server-confirmed base. When a server patch arrives, it rewinds to that base, applies the patch, and replays unacknowledged mutations before publishing the rebased state. The [how-it-works guide](https://doc.replicache.dev/concepts/how-it-works) explains why mutation replay and acknowledgment tracking are central correctness concerns.
- **C2:** Transactional mutators, local key/value views, subscriptions, and application-provided backend endpoints form reusable abstractions for optimistic applications. The same guide explains client groups and synchronization across browser tabs.

**Entry points:** the Replicache conceptual guide and the repository's mirror notes. **Visibility limitation:** the repository is an official published subset of an internal repository. Its README records a history rewrite on 2026-09-30 and removal of some server/IVM-related tests; public Replicache/client tests remain. Public source should not be treated as the complete internal validation environment.

### 12. [livestorejs/livestore](https://github.com/livestorejs/livestore)

**TypeScript — event-sourced application state materialized into reactive SQLite.** Study how a durable event stream becomes a local queryable database, and how synchronization changes the relationship between pending and accepted events.

- **C1:** The [SyncState API documentation](https://docs.livestore.dev/api/livestore/livestore/namespaces/syncstate/classes/syncstate/) documents upstream/local heads, pending events, rebase behavior, and invariants such as continuous parent chains and the ordering of upstream versus local heads. These are concrete constraints behind reconnect and rebase handling.
- **C2:** The repository describes application-defined events and materializers, platform adapters, and replaceable synchronization providers. Keeping event propagation separate from SQLite materialization supports different schemas and application runtimes.

**Entry points:** the repository's “How LiveStore works” explanation and the `SyncState` invariants. Its event-sourcing architecture is a different study target from row-level change capture, even though both expose local SQL queries.

### 13. [garden-co/jazz](https://github.com/garden-co/jazz)

**Rust and TypeScript — local-first relational database and application framework.** **Version caveat:** the verified repository identifies itself as **Jazz 2.0 alpha with an entirely new API**. This entry describes that architecture, not the older Classic Jazz CoValue API.

- **C1:** The [local-first data model](https://jazz.tools/docs/concepts/local-first-data-model) describes retained row-version histories and causal relationships, with deterministic per-field resolution. Its [transaction documentation](https://jazz.tools/docs/writing/transactions) distinguishes offline mergeable transactions from exclusive transactions that require authority validation and can be rejected and rolled back.
- **C2:** Relational data, local queries, replicated histories, and explicit transaction/durability semantics are exposed as a reusable application data layer across TypeScript and Rust. The split between local commit and authority acceptance is particularly useful to study when applications require both offline editing and cross-write invariants.

**Entry points:** the data-model and transaction guides. Exclusive acceptance requires a reachable authority; the alpha also has platform-specific limitations noted in the repository, including its React Native scaffold.

## Composable application data and synchronization orchestration

### 14. [GetDutchie/brick](https://github.com/GetDutchie/brick)

**Dart — generated models and composable offline repositories for Flutter applications.** Its replication approach uses local persistence, queued remote requests, and rehydration rather than a general-purpose CRDT.

- **C1:** The [Supabase offline repository implementation](https://github.com/GetDutchie/brick/blob/main/packages/brick_offline_first_with_supabase/lib/src/offline_first_with_supabase_repository.dart) distinguishes remote-required and optimistic policies, initializes a persisted request queue, handles remote failures, and coordinates SQLite/memory updates. Realtime events can require additional fetching to restore model associations; deletes must map remote unique fields back to local queries.
- **C2:** Shared repository/provider interfaces and generated model mappings let application code work across local SQLite and remote services. The [maintainer's integration description](https://github.com/GetDutchie/brick/issues/445) explains queue persistence, dependency-aware association writes, and provider testing.

**Entry points:** the Supabase repository source and integration discussion. This is useful for studying the practical impedance mismatch between remote REST-style operations and relational local object models.

### 15. [orbitjs/orbit](https://github.com/orbitjs/orbit)

**TypeScript — composable data sources and coordination strategies.** This is Orbit.js, distinct from the peer-to-peer OrbitDB project below. It lets applications combine memory, browser persistence, and remote JSON:API sources.

- **C1:** The [coordination guide](https://orbitjs.com/docs/0.15/getting-started) makes ordering explicit: restore a backup before activating the strategy that writes to it; choose blocking durability versus optimistic remote requests; persist queues and transform logs so they survive application closure.
- **C2:** Sources, transforms, buckets, and coordinator strategies separate data operations from persistence and networking policy. An application can mix blocking and nonblocking strategies for different operations and supply exception handling.

**Entry point:** the guide's coordinator, remote-server, and bucket sections. The inspected guide is version 0.15 and explicitly says its simple network example needs production error handling. Orbit provides substantial orchestration primitives, but the application still chooses retry and conflict policy.

## Replicated document and structured-data engines

### 16. [automerge/automerge-repo](https://github.com/automerge/automerge-repo)

**TypeScript over Automerge — document lifecycle, persistence, and network synchronization.** This is the application-facing orchestration repository; the underlying Automerge engine is not separately counted.

- **C1:** The [storage subsystem](https://github.com/automerge/automerge-repo/blob/main/packages/automerge-repo/src/storage/StorageSubsystem.ts) illustrates crash/concurrency-sensitive persistence: write a replacement snapshot before removing covered chunks, preserve chunks created outside the compacted set, and guard simultaneous compaction. It also persists peer synchronization state.
- **C2:** A `Repo` manages document handles and composes a storage adapter with zero or more network adapters. Applications can reuse document synchronization across different persistence and transport choices, as explained in the [repository abstraction guide](https://automerge.org/docs/reference/repositories/).
- **C3:** Incremental chunks avoid repeatedly writing whole documents; compaction is triggered by accumulated incremental size relative to snapshots.

**Entry points:** the repository abstraction guide and `StorageSubsystem.ts`. This pairing exposes practical durable replication work beyond the mathematical merge algorithm.

### 17. [yjs/yjs](https://github.com/yjs/yjs)

**JavaScript — CRDT shared types for offline-capable collaborative data.** Yjs is a reusable replication engine; applications add persistence and network providers. Study its representation rather than expecting a turnkey backend in this repository.

- **C1:** The [internal architecture document](https://github.com/yjs/yjs/blob/main/INTERNALS.md) explains identifiers combining client and clock, insertion origins, deletion sets, and deterministic integration of concurrent operations. These rules support convergent maps, arrays, and text.
- **C2:** Multiple shared data types reuse the same underlying CRDT structures and update protocol, allowing editors and other structured applications to share replication machinery independently of transport.
- **C3:** Compound runs reduce object overhead; per-client struct stores permit efficient lookup, while state-vector exchange identifies missing updates instead of retransmitting everything. These optimizations are connected directly to the data representation in `INTERNALS.md`.

**Entry point:** `INTERNALS.md`, especially struct storage, insertion ordering, and synchronization.

### 18. [loro-dev/loro](https://github.com/loro-dev/loro)

**Rust with language bindings — structured CRDT documents and version history.** It covers maps, lists, movable lists, trees, and text, offering a different set of data-model tradeoffs from text-centric collaboration engines.

- **C1:** The [versioning deep dive](https://loro.dev/docs/advanced/version_deep_dive) explains operation identifiers, peer counters, causal histories, version vectors, and frontiers. Unique peer identity and the distinction between causal order and concurrent operations are essential to correctly combining disconnected edits.
- **C2:** The repository exposes reusable document containers, import/export, and history/version facilities across Rust and bindings. Applications can use the same replication engine for several structured-data models rather than inventing separate merge logic for each.
- **C3:** Version vectors and compact causal frontiers support identifying and exchanging missing history; the architecture distinguishes the operation log from the currently materialized state.

**Entry point:** the versioning deep dive, then the repository's container and binding examples. Network service, authentication, and application-level invariants remain integration concerns.

## Peer-to-peer and programmable replication systems

### 19. [orbitdb/orbitdb](https://github.com/orbitdb/orbitdb)

**JavaScript — peer-to-peer databases built on signed replicated logs.** Study how a database materialization is separated from a causally structured append-only history and from peer discovery/transfer.

- **C1:** The [operation-log design](https://github.com/orbitdb/orbitdb/blob/main/docs/OPLOG.md) explains immutable signed entries, Merkle-DAG references, and Lamport ordering. Independently appended histories must produce a deterministic order when peers reconnect; signature validation and causal ordering solve distinct parts of that problem.
- **C2:** Databases derive their state from the replicated log, allowing different database models to share log, identity, and replication machinery. The [replication guide](https://github.com/orbitdb/orbitdb/blob/main/docs/REPLICATION.md) shows peer synchronization and persisted block storage in a complete setup.

**Entry points:** `docs/OPLOG.md` and `docs/REPLICATION.md`. This project is unrelated to Orbit.js despite the similar name.

### 20. [holepunchto/autobase](https://github.com/holepunchto/autobase)

**JavaScript — multiwriter replication and deterministic views over Hypercore logs.** Its distinctive design permits optimistic view construction while the final order of concurrent inputs is still being established.

- **C1:** The repository explains that new information can reorder inputs, causing a view to undo and reapply operations. Application `apply` logic must therefore be deterministic and avoid external side effects. Stable signed progress also depends on indexer agreement; accepting an offline append and finalizing its position are separate events.
- **C2:** Application-defined `open` and `apply` functions construct different materialized views over the same multiwriter mechanism.
- **C3:** The [linearizer implementation](https://raw.githubusercontent.com/holepunchto/autobase/main/lib/linearizer.js) separates dependency tracking, head/tail management, consensus, and topological ordering. The repository also describes fast-forwarding over stable history to reduce catch-up work.

**Entry points:** the repository's view/ordering contract and `lib/linearizer.js`. This is a strong study target for the cost of revisable order, rather than a promise that every write immediately has a globally final position.

### 21. [anyproto/any-sync](https://github.com/anyproto/any-sync)

**Go — encrypted peer-to-peer synchronization protocol for local-first data.** This is reusable synchronization infrastructure beneath applications, with separate node and supporting-service components.

- **C1:** The repository and [protocol overview](https://sync.any.org/) describe per-object change DAGs with signed, encrypted changes and CRDT reconciliation. This combines disconnected concurrency with verification and access boundaries: storage providers should not need plaintext in order to relay encrypted histories.
- **C2:** Spaces, objects, change histories, and synchronization nodes provide reusable protocol concepts. The overview distinguishes the generic synchronization layer from object interpretation and materialization, allowing different application schemas to use the same infrastructure.

**Entry points:** the repository's protocol/component overview and the official protocol site. Encryption and signatures are architectural mechanisms, not a claim that every application built on the protocol automatically has correct authorization or data-retention behavior.

### 22. [sourcenetwork/defradb](https://github.com/sourcenetwork/defradb)

**Go — local/edge document database combining queries with peer-to-peer replication.** Study how replicated causal history is exposed alongside an application database API rather than hidden entirely in a synchronization subsystem.

- **C1:** The [database-internals API](https://docs.source.network/defradb/references/database-internals/database-api/) represents objects as Merkle-CRDT histories. Concurrent changes can leave multiple heads; the API therefore returns arrays of latest commits and exposes predecessor links and deltas rather than assuming one global latest write.
- **C2:** Schema-driven GraphQL-style queries coexist with traversal and validation of replication history. Application objects, historical commits, and peer synchronization are reusable database facilities rather than a single application's event log.
- **C3:** The implementation model stores small delta-state updates connected by content identifiers, making the unit of replicated history explicit.

**Entry points:** the repository's replication overview and the database-internals API. The inspected current API page identifies itself as documentation version 1.1; older versioned conceptual pages were not used to infer current APIs.

### 23. [replikativ/replikativ](https://github.com/replikativ/replikativ)

**Clojure/ClojureScript — composable CRDT replication with asynchronous middleware.** A useful smaller-community codebase for studying explicit separation among replicated datatypes, persistent storage, and transport.

- **C1:** The [core implementation](https://github.com/replikativ/replikativ/blob/master/src/replikativ/core.cljc) coordinates initial subscription/handshake state, publication, persistent log writes, in-memory CRDT application, and acknowledgments through asynchronous channels. Reading their ordering is instructive for failure handling and duplicate publication.
- **C2:** The repository combines several replicated datatypes with `konserve` storage and `kabel` transport abstractions. Applications can reuse the middleware while choosing their replicated model and persistence implementation.
- **C3:** The [changelog](https://github.com/replikativ/replikativ/blob/master/CHANGELOG.md) records append-log, lowest-common-ancestor, reconnection, and concurrency work, giving concrete leads for studying efficiency and failure fixes.

**Entry points:** `src/replikativ/core.cljc` and `CHANGELOG.md`. The inspected changelog documents a 0.2.x line without a sufficient dated history to support a C4 claim; no current maintenance promise is inferred.

### 24. [mirage/irmin](https://github.com/mirage/irmin)

**OCaml — programmable, Git-like persistent storage with synchronization and custom merge.** This is a foundation for applications that work on independent local branches and later reconcile them, rather than a packaged mobile sync service.

- **C1:** The [architecture guide](https://irmin.org/tutorial/architecture/) separates immutable content-addressed storage from mutable branch references. Correctness depends on stable hashes, consistent object references, and atomic `test_and_set` operations when branch heads change; the guide discusses filesystem locking as one implementation strategy.
- **C2:** Configurable contents, merge functions, and storage backends support different application data models. The [introduction](https://irmin.org/tutorial/introduction/) places clone, branch, merge, and synchronization operations in that reusable store interface.
- **C3:** Immutable objects and structural sharing permit related versions and branches to reuse stored data rather than copy complete states.

**Entry points:** the architecture guide's immutable/mutable store split and the introductory merge/synchronization model.

### 25. [n0-computer/iroh-docs](https://github.com/n0-computer/iroh-docs)

**Rust — replicated key/value document metadata with peer-to-peer synchronization.** This is the document layer, not merely Iroh's network transport. Content blobs and metadata synchronization are separate responsibilities.

- **C1:** The [Replica API](https://docs.rs/iroh-docs/latest/iroh_docs/sync/struct.Replica.html) documents verification of namespace and author signatures on remote entries, deletion through empty entries, and incremental synchronization message processing. Inserting a content hash does not itself fetch or persist that content.
- **C2:** Namespaces, authors, keys, and content hashes form a general replication model. Storage implementations and surrounding blob/gossip protocols can be composed around it, as described in the repository.
- **C3:** Range-based reconciliation compares fingerprints and subdivides differing ranges to discover missing entries, avoiding a full record-by-record exchange when replicas substantially overlap.

**Entry points:** the repository's reconciliation overview and `sync::Replica` documentation. Offline access to an entry's metadata does not imply that its referenced blob has already been cached locally.

### 26. [amark/gun](https://github.com/amark/gun)

**JavaScript — peer-to-peer graph data synchronization.** A distinctive study target for field-level convergence and message processing in a compact event-driven core; its graph model differs from relational sync and document-history systems above.

- **C1:** The [core source](https://github.com/amark/gun/blob/master/src/root.js) validates graph fields and state metadata, deduplicates messages, compares incoming state against known state, defers future-dated updates, and breaks equal-state ties deterministically. These branches expose the dependence of convergence on clock and value-ordering rules.
- **C2:** Graph updates, subscriptions, and event hooks connect application data to storage and network processing. The same field-level machinery serves different graph shapes rather than a fixed application schema.
- **C3:** The core schedules work in small batches and aggregates acknowledgments around asynchronous processing, illustrating event-loop responsiveness alongside replication bookkeeping.

**Entry point:** `src/root.js`, especially graph validation, `ham`, and acknowledgment handling. The value of this entry is its inspectable design tradeoffs; inclusion is not an endorsement of every clock assumption or module.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations and followed primary sources from the resulting candidates. Search angles included:

- Offline-first document replication, CouchDB protocol compatibility, and browser databases.
- SQLite synchronization, relational CRDT extensions, and selective server-to-client replication.
- Optimistic mutation replay, event sourcing, and incremental application queries.
- CRDT documents, causal versioning, movable collections, and persistence/compaction.
- Signed peer-to-peer logs, Merkle-DAG databases, encrypted object replication, and range reconciliation.
- Dart/Flutter and .NET mobile persistence, Clojure middleware, and OCaml programmable merge stores.
- Intermittently connected Java database networks, batch acknowledgments, and file-carried offline synchronization.

Later language-specific and less-famous-project queries added Brick, Replikativ, Irmin, Dotmim.Sync, and the disconnected-node use case of SymmetricDS. Subsequent discovery increasingly returned already-covered engines, thin wrappers, early prototypes, or adjacent transport/server infrastructure. The list extends slightly beyond 25 to preserve these genuinely different communities and designs; it does not count bindings, related packages, or monorepo subsystems as separate projects.

Excluded classes include tutorials, generated wrappers, awesome lists, application repositories whose main contribution is not reusable synchronization, and ordinary always-connected database replication. Transport-only Iroh/libp2p-style libraries do not independently qualify. Electric's downstream synchronization work was considered, but was not retained as an additional entry after selecting PowerSync's server-component architecture; this is a scope choice, not a judgment that downstream replication is irrelevant. Automerge's core is represented through `automerge-repo`, and Replicache/Zero count once through `rocicorp/mono`. Forks were not used to inflate coverage.

Repository roots and distinct primary architectural, API, implementation, or testing sources were inspected for every retained entry. Some GitHub source pages required reading their contents through the GitHub connector or raw source endpoint. No repositories were cloned, candidate code executed, dependencies installed, maintainers contacted, or external services modified. Stars and benchmark headlines were not used as quality evidence, and no numerical speed claims are made.

The principal limits are uneven documentation age and unequal public visibility. The report flags versioned/historical guides, Jazz's alpha transition, LiteCore's internal API scope, and Rocicorp's partial public mirror. It does not infer active maintenance from repository presence or recent activity, and it does not label old projects abandoned without primary evidence. Criterion judgments and suggested study value are grounded engineering inferences from the cited mechanisms. They do not establish that each implementation satisfies every application invariant, handles all adversarial conditions, or has equally exemplary code throughout.
