# Conflict-free replicated data type libraries

Research date: **2026-10-09**.

This is a selection guide to **24 GitHub repositories** containing substantial CRDT implementations: collaborative documents, sequence algorithms, reusable datatype collections, and CRDT libraries embedded in replication frameworks. The selection includes production-oriented libraries and clearly identified research references. For monorepos, only the named CRDT subsystem is assessed. Inclusion means there is worthwhile engineering to study; it does not certify every algorithm, implementation, or deployment configuration.

Criteria legend:

- **C1 — Difficult correctness:** convergence, causal ordering, concurrent operations, invariants, input validation, or recovery from failures.
- **C2 — Reusable abstractions:** substantial interfaces or components useful across multiple applications or datatypes.
- **C3 — Performance with structure:** concrete work on memory, representation, synchronization, or execution cost within an understandable architecture.
- **C4 — Sustained evolution:** multi-year evidence of compatibility, testing, migration, or complexity management, beyond repository age alone.

Canonical repository identities and archive flags were checked through GitHub pages or the GitHub API. Each entry also uses opened primary documentation or source code beyond the root README. An unarchived repository is not necessarily maintained. Historical/reference labels below describe suitability for study, not an assertion that the code is unusable. No candidate code was executed, and no benchmark figures were independently reproduced.

## Collaborative document and collection frameworks

### 1. [automerge/automerge](https://github.com/automerge/automerge)

**Rust core; JavaScript/WebAssembly and C interfaces.** A document library combining JSON-like replicated objects, change history, persistence, and synchronization. Study how datatype semantics, historical views, patches, and an efficient network protocol coexist behind a document API.

- **C1:** The [sync implementation](https://github.com/automerge/automerge/blob/main/rust/automerge/src/sync.rs) explicitly requires a reliable, ordered peer stream, tracks in-flight messages and remote heads, and explains how requests for unrelated orphan dependencies can stall synchronization. This is useful evidence that datatype convergence and transport correctness are separate concerns.
- **C2/C3:** The [project overview](https://github.com/automerge/automerge/blob/main/README.md) describes a reusable Rust core shared by language interfaces, compact persistence, and incremental synchronization.
- **C4:** Inspected releases span [August 2023](https://github.com/automerge/automerge/releases/tag/js/automerge-wasm-0.2.10) to [September 2026](https://github.com/automerge/automerge/releases/tag/js/automerge-3.5.0). The [Rust changelog](https://github.com/automerge/automerge/blob/main/rust/CHANGELOG.md) records compatibility changes, stricter validation, recovery for documents affected by earlier bugs, and performance regressions and fixes.

### 2. [yjs/yjs](https://github.com/yjs/yjs)

**JavaScript; shared document types.** A particularly instructive implementation of a common sequence mechanism underlying arrays, text, and maps, with networking and editor bindings supplied separately.

- **C1:** [Yjs Internals](https://github.com/yjs/yjs/blob/main/INTERNALS.md) explains stable item identities, deterministic integration of concurrent insertions, and the different treatment of deletions. A snapshot needs both a state vector and a delete set; the vector alone is insufficient.
- **C2:** The [README/API guide](https://github.com/yjs/yjs/blob/main/README.md) exposes reusable shared types, transactions, undo management, and update APIs while separating network providers from the core.
- **C3:** The internals document describes grouping consecutive characters into items, splitting those items when edits interrupt a run, dual document/insertion-order representations, and position-search caching. These are concrete responses to per-character object and lookup overhead, rather than merely speed claims.

### 3. [y-crdt/y-crdt](https://github.com/y-crdt/y-crdt)

**Rust; Yrs core with C and WebAssembly interfaces.** This is a substantive Rust implementation of the Yjs algorithm and protocol, not just an FFI wrapper around the JavaScript implementation. It merits a separate entry for its native APIs and transaction model.

- **C1:** The [Yrs crate documentation in source](https://github.com/y-crdt/y-crdt/blob/main/yrs/src/lib.rs) explains full-state versus incremental updates, stable cursor positions, and undo scoped by transaction origin so remote edits need not be undone with local edits. It also documents transaction restrictions around undo operations.
- **C2:** The [repository organization and compatibility matrix](https://github.com/y-crdt/y-crdt/blob/main/README.md) distinguish the core from bindings and identify differences among implementations. Shared maps, arrays, XML/text, observers, and undo form a reusable collaboration substrate.

The stated goal is Yjs behavior and binary-protocol compatibility; the matrix should be consulted instead of assuming complete feature parity.

### 4. [loro-dev/loro](https://github.com/loro-dev/loro)

**Rust with language bindings; structured documents and version history.** Useful for studying CRDTs that must support checkout and version control as well as live synchronization. Its [supported types](https://github.com/loro-dev/loro/blob/main/README.md) include rich text, movable lists, movable trees, and maps.

- **C1:** The [internal diff design](https://github.com/loro-dev/loro/blob/main/crates/loro-internal/docs/diff_calc.md) distinguishes causal imports from concurrent imports and checkout. It explains why equal visible values may still require updating winner metadata, and why shallow history complicates replay correctness.
- **C2:** Different container types share document history and diff machinery, allowing structured applications to combine them.
- **C3:** The same design document describes critical-version replay bases, limiting work to changed containers, lazy shallow-map history initialization, and fast paths that deliberately fall back when their causal preconditions fail. This makes optimization boundaries unusually visible.

### 5. [streamich/json-joy](https://github.com/streamich/json-joy)

**TypeScript; JSON CRDT subsystem within a larger JSON tooling monorepo.** Focus on `packages/json-joy/src/json-crdt`, rather than treating all of the repository's codecs, routing, and operational-transformation utilities as CRDT work.

- **C1:** The [model fuzzing description](https://github.com/streamich/json-joy/blob/master/packages/json-joy/src/json-crdt/__tests__/fuzzer/README.md) generates patches across multiple peers and changes their merge order to check convergence. It explicitly distinguishes that test from the weaker server-ordered case.
- **C2/C3:** The [block-wise RGA design](https://github.com/streamich/json-joy/blob/master/packages/json-joy/src/json-crdt/nodes/rga/README.md) implements strings, binary blobs, and arrays with one abstract sequence engine. Separate indexes by identifier and position, subtree lengths, chunk coalescing, and balanced reconstruction address both positional access and metadata cost.

Study the representation and test strategy; the project's superlative performance marketing is not independently established here.

### 6. [composablesys/collabs](https://github.com/composablesys/collabs)

**TypeScript; composable collaborative collections.** The relevant implementations are `core` and `crdts`; the top-level published convenience package re-exports them. Particularly useful when an application needs custom collaborative objects beyond a fixed JSON schema.

- **C1:** [`PrimitiveCRDT`](https://github.com/composablesys/collabs/blob/master/crdts/src/base_collabs/primitive_crdt.ts) states the runtime's eventual, exactly-once, causal-order message-delivery contract and the implementer's strong-eventual-consistency obligation. It also separates message application from saved-state loading.
- **C2:** The [source organization](https://github.com/composablesys/collabs/blob/master/README.md) and primitive base class show explicit extension points for custom types, parent/child composition, metadata, events, and persistence.

The interesting abstraction is the boundary between runtime guarantees and a datatype's own semantics. The inspected repository metadata last reported a push in March 2025; current support commitments were not established.

## Sequence engines and rich-text research references

### 7. [josephg/diamond-types](https://github.com/josephg/diamond-types)

**Rust; text CRDT and operation-history engine.** Study the distinction between original positional edits, a temporary merge representation, and transformed edits that can be applied to a document.

- **C1:** The current opening sections of [INTERNALS.md](https://github.com/josephg/diamond-types/blob/master/INTERNALS.md) describe a causal DAG and how concurrent changes can produce different valid replay orders with the same document result.
- **C3:** The causal graph is run-length encoded to exploit mostly sequential editing. The [README](https://github.com/josephg/diamond-types/blob/master/README.md) also identifies translation between positional edits and CRDT identities as a central performance target.

**Scope limitation:** the README describes plain-text support, ongoing expansion, and an out-of-date published Cargo package. The internals file labels its later section as an older design. Use the current source alongside it; do not treat the entire document as a description of today's layout or repeat the repository's comparative speed claims as measured facts.

### 8. [noib3/cola](https://github.com/noib3/cola)

**Rust; operation-based text CRDT independent of text storage.** The former `nomad/cola` URL redirects here. Its unusual separation of convergence metadata from the actual text makes it useful for editor implementers with an existing rope, piece table, or gap buffer.

- **C1:** [`Replica`](https://github.com/noib3/cola/blob/main/src/replica.rs) tracks insertion/deletion clocks, a run tree, and a backlog for operations whose dependencies are missing. Its API explains that applying yielded deletion ranges in the wrong order can permanently diverge the external buffer.
- **C2:** The same implementation returns positions or ranges to apply to an independently owned buffer. [Crate-level documentation](https://github.com/noib3/cola/blob/main/src/lib.rs) describes caller-defined text-length metrics and optional serialization.

**Status:** the protocol documentation explicitly warns that pre-stable protocol versions can change frequently. Cross-version compatibility should not be assumed.

### 9. [inkandswitch/peritext](https://github.com/inkandswitch/peritext)

**TypeScript; historical research prototype for rich-text CRDT semantics.** Retained for its substantial algorithm and testable abstraction, not as a currently supported editor package. It extends the simplified Automerge-like Micromerge implementation.

- **C1:** The [formatting implementation](https://github.com/inkandswitch/peritext/blob/main/src/peritext.ts) anchors formatting boundaries before or after stable element IDs and distinguishes text endpoints. The code exposes the difficult interaction among concurrent insertion, formatting removal, and mark attributes.
- **C2:** The [code tour](https://github.com/inkandswitch/peritext/blob/main/README.md) separates operation generation/application, document materialization, incremental patches, and the ProseMirror bridge. This is reusable design knowledge for other editor integrations and annotation systems, although the prototype's mark schema is limited.

The README describes example-based tests and generative convergence fuzzing. Repository metadata last reported a push in September 2022; prefer a maintained implementation for deployment.

## General datatype collections and composition kernels

### 10. [rust-crdt/rust-crdt](https://github.com/rust-crdt/rust-crdt)

**Rust; serializable state- and operation-based datatype collection.** A good study of how a strongly typed API can expose causal context instead of hiding it behind ordinary collection methods.

- **C1:** The [usage explanation](https://github.com/rust-crdt/rust-crdt/blob/master/README.md) demonstrates how a removal based on a refreshed internal state can erase data a user never observed. Read contexts generate distinct add/remove contexts to preserve the intended observation boundary.
- **C2:** [`CvRDT`, `CmRDT`, and `ResetRemove`](https://github.com/rust-crdt/rust-crdt/blob/master/src/traits.rs) provide reusable replication and validation contracts. They expose structured compatibility errors and explicitly document operation-order assumptions rather than claiming that every delivery order is valid.

The inspected metadata last reported a push in June 2024. Treat the code and API contracts as the evidence; no current maintenance commitment was verified.

### 11. [basho/riak_dt](https://github.com/basho/riak_dt)

**Erlang; reusable state-based CRDTs from the Riak ecosystem.** The [README](https://github.com/basho/riak_dt/blob/develop/README.md) distinguishes this library from the older database prototype on a historical branch.

- **C1:** [`riak_dt_orswot.erl`](https://github.com/basho/riak_dt/blob/develop/src/riak_dt_orswot.erl) explains precisely how an absent element is distinguished from an unseen insertion: compare its birth dot against the other replica's version vector. Concurrent add/remove semantics and deferred removals are explicit.
- **C2:** The module implements the shared `riak_dt` behavior, exposes update/merge/serialization operations, and accepts a containing map's parent clock for composition.
- **C3:** ORSWOT avoids per-removal tombstones by retaining compact causal information. The source includes version-conversion interfaces and QuickCheck convergence/serialization property hooks, useful evidence of engineering beyond a textbook set implementation.

### 12. [lasp-lang/types](https://github.com/lasp-lang/types)

**Erlang; historical reference collection for state, delta-state, and pure operation-based datatypes.** The [repository](https://github.com/lasp-lang/types/blob/master/README.md) identifies itself as a reference implementation; inspected metadata last reported a push in February 2019.

- **C1:** [`state_causal_type.erl`](https://github.com/lasp-lang/types/blob/master/src/state_causal_type.erl) makes removal semantics concrete: retain shared dots and values not dominated by the other side's causal context, then merge contexts.
- **C2:** The same module supplies a universal merge over dot sets, dot functions containing CRDT values, and recursively nested dot maps. Concrete collections can reuse this causal kernel instead of independently implementing the same bookkeeping.

This is a useful comparison with Riak DT: the emphasis is on a common mathematical representation and several replication families, rather than just one production datatype API. Historical status is a reason to inspect assumptions and tests, not a claim of sustained current support.

### 13. [CBaquero/delta-enabled-crdts](https://github.com/CBaquero/delta-enabled-crdts)

**C++; research reference implementations of delta-enabled datatypes.** An unusually direct bridge from delta-CRDT papers to templated implementations of counters, sets, registers, maps, and bounded counters.

- **C1:** [`delta-crdts.cc`](https://github.com/CBaquero/delta-enabled-crdts/blob/master/delta-crdts.cc) separates a compact per-replica causal prefix from a cloud of exceptional dots; compaction absorbs only contiguous or already dominated dots. The same file shows the distinction between ordinary product joins and lexicographic joins.
- **C2:** The [datatype catalog and API examples](https://github.com/CBaquero/delta-enabled-crdts/blob/master/README.md) show mutations returning mergeable delta states, optional full-state replication, product composition, and a reusable dot kernel.

**Important qualification:** the README itself says the code is early and was not properly tested. Retained as a substantive algorithmic reference meeting C1/C2, not as evidence of production readiness, formal verification, or C4.

### 14. [jemc/pony-crdt](https://github.com/jemc/pony-crdt)

**Pony; historical delta-state CRDT collection.** A less common language ecosystem with an implementation worth comparing against the C++ and Erlang causal kernels. Inspected metadata last reported a push in August 2019.

- **C1:** [`DotKernel`](https://github.com/jemc/pony-crdt/blob/master/crdt/_private/dot_kernel.pony) distinguishes active values from remembered causal dots. Removing a value preserves the causal evidence needed to reject its later reappearance; convergence consults both replicas' histories.
- **C2:** The kernel is generic over immutable payloads and explicitly supports different outer interpretations, such as summing counter values or collecting set members. The [library contract](https://github.com/jemc/pony-crdt/blob/master/README.md) makes every mutation's delta available while retaining a full-state synchronization option.

Study how shared causal context, payload constraints, and mutable local state are expressed in Pony. It is a separate language implementation inspired by the research references, not another listing of their source.

### 15. [heckj/CRDT](https://github.com/heckj/CRDT)

**Swift; generic delta-state datatypes.** It builds on ReplicatingTypes but documents substantive additions: generic actor identities and explicit delta-state transfer. The upstream package is not counted separately here.

- **C1:** The [causal-tree list implementation](https://github.com/heckj/CRDT/blob/main/Sources/CRDT/GenericCRDTs/List.swift) exposes Lamport/actor identities, anchors, tombstones, deterministic sibling ordering, and checks for duplicate IDs and missing anchors.
- **C2:** The [library overview](https://github.com/heckj/CRDT/blob/main/README.md) describes reusable counters, registers, sets, maps, and lists with generic identities and delta replication.

The author explicitly identifies missing serialization and long-text memory optimizations. Accordingly, this entry claims C1/C2, not performance parity with document engines. Metadata last reported a push in December 2024; current support was not established.

### 16. [concordant/c-crdtlib](https://github.com/concordant/c-crdtlib)

**Kotlin Multiplatform; datatype library targeting JVM and JavaScript.** This is the Concordant project's substantive GitHub copy/mirror; its [developer documentation](https://github.com/concordant/c-crdtlib/blob/master/README.dev.md) places CI, documentation, and package infrastructure on INRIA GitLab. Mirror synchronization and current maintenance were not established; GitHub metadata last reported a push in September 2022.

- **C1:** [`BCounter.kt`](https://github.com/concordant/c-crdtlib/blob/master/src/commonMain/kotlin/crdtlib/crdt/BCounter.kt) implements non-negativity through per-replica rights: local increments plus received rights minus transferred/consumed rights. It checks arithmetic and rejects decrements exceeding local rights.
- **C2:** The [CRDT API](https://github.com/concordant/c-crdtlib/blob/master/README.md) factors timestamps through an environment, supports version-vector-based delta generation, and offers counters, registers, sequences, and maps with different conflict policies across both language targets.

The API is explicitly described as unstable. The bounded-counter invariant is a stronger study target than a generic claim that all numeric updates commute.

### 17. [k98kurz/CRDTs](https://github.com/k98kurz/CRDTs)

**Python; datatype collection with serialization and resynchronization interfaces.** Useful for examining a dynamically typed API spanning counters, registers, sets, maps, and several list representations.

- **C1:** The [ORSet implementation](https://github.com/k98kurz/CRDTs/blob/master/crdts/orset.py) validates clock identity and update shape, tracks add/remove timestamp metadata, and reconstructs concise update histories for resynchronization. Its [tests](https://github.com/k98kurz/CRDTs/blob/master/tests/test_orset.py) include idempotent update application and replay from history.
- **C2:** The [overview and protocol guide](https://github.com/k98kurz/CRDTs/blob/master/readme.md) expose replaceable clocks, update objects, data wrappers, packing, checksum ranges, and Merkle-history reconciliation across the datatype collection.

Read the actual clock and tie-breaking semantics before equating its type names with another library's definitions. The paper references are not proof that this implementation has been formally verified. Metadata last reported a push in February 2025.

### 18. [stg-tud/Bismuth](https://github.com/stg-tud/Bismuth)

**Scala; `Modules/RDTs` algebraic replicated datatype library.** This is the current repository named by REScala's migration notice; the old snapshot is not counted separately. The [module overview](https://github.com/stg-tud/Bismuth/blob/main/README.md) explicitly identifies both predefined datatypes and derived typeclass machinery.

- **C1:** [`Lattice.scala`](https://github.com/stg-tud/Bismuth/blob/main/Modules/RDTs/src/main/scala/rdts/base/Lattice.scala) states the associative, commutative, idempotent merge contract and handles subsumption and normalization when different structural representations denote the same information.
- **C2:** Product and sum derivation, map/option/set/function instances, and a decomposition-based `diff` turn convergence into a compositional library abstraction instead of a separate hand-written merge for every application record.
- **C3:** Merge implementations take account of state-versus-delta size and fold a smaller map into a larger one, illustrating how generic algebraic APIs can still carry useful optimization structure.

This is research software. The monorepo also contains consensus experiments; they are outside this entry's CRDT scope.

## Datatype libraries integrated with replication and storage

### 19. [derekkraan/delta_crdt_ex](https://github.com/derekkraan/delta_crdt_ex)

**Elixir; replicated key/value library implemented with OTP processes.** Study the boundary between an individual CRDT's state and the process responsible for synchronizing it with changing neighbors.

- **C1:** [`DeltaCrdt.CausalCrdt`](https://github.com/derekkraan/delta_crdt_ex/blob/master/lib/delta_crdt/causal_crdt.ex) manages acknowledgments, outstanding synchronization, neighbor monitors, and persisted-state loading. Its handling of dead neighbors and partial-diff continuations exposes failure and lifecycle concerns beyond an isolated merge function.
- **C2:** The [public guide](https://github.com/derekkraan/delta_crdt_ex/blob/master/README.md) provides map-like operations and explicit neighbor configuration for embedding in distributed Elixir applications.
- **C3:** The implementation uses MerkleMap to find differences and bounds synchronization work with `max_sync_size`, separating comparison, delta transfer, and CRDT state application.

Metadata last reported a push in May 2024. The current inspected README describes MerkleMap-based synchronization; older discussions of the package should not be assumed to describe this architecture exactly.

### 20. [ipfs/go-ds-crdt](https://github.com/ipfs/go-ds-crdt)

**Go; Merkle-CRDT-backed implementation of the go-datastore interfaces.** A useful larger-scale counterpart to in-memory CRDT collections: causal dissemination, durable key/value state, and application hooks must work together.

- **C1:** [`set.go`](https://github.com/ipfs/go-ds-crdt/blob/master/set.go) implements an add-wins observed-remove set, resolves competing values by priority and identifier, and serializes non-atomic priority updates with a mutex. Removal enumeration also guards against accidentally matching a different key through a shared prefix.
- **C2:** The [architecture/usage guide](https://github.com/ipfs/go-ds-crdt/blob/master/README.md) separates the datastore, broadcaster, and DAG synchronization interfaces; IPFS components are convenient implementations rather than the only possible application wiring.
- **C3:** Batching, deltas, and prefix-oriented persistent storage address synchronization and lookup costs within that decomposition.

The README's deployment and throughput figures are project claims, not independently reproduced measurements; they are unnecessary to the selection rationale.

### 21. [vlcn-io/cr-sqlite](https://github.com/vlcn-io/cr-sqlite)

**Rust/C; loadable SQLite extension implementing replicated relations.** Included as an embeddable CRDT library at the SQL storage boundary, rather than as a separate database service.

- **C1:** [`changes_vtab_write.rs`](https://github.com/vlcn-io/cr-sqlite/blob/main/core/rs/core/src/changes_vtab_write.rs) makes conflict resolution explicit: causal-length handling precedes column-version comparison, with deterministic value comparison and optional site-ID tie-breaking. Error paths handle inconsistent row/clock metadata and statement cleanup.
- **C2:** The [extension API](https://github.com/vlcn-io/cr-sqlite/blob/main/README.md) upgrades ordinary tables to replicated relations, exposes changes through a virtual table, and provides schema-alteration helpers. Applications can retain ordinary SQL reads and writes while transport code exchanges change rows.

This is a study of replication semantics crossing SQLite's extension and value APIs. The repository was unarchived when checked, but this research did not establish a current maintenance commitment or validate support for every SQLite schema feature.

### 22. [apache/pekko](https://github.com/apache/pekko)

**Scala with Java APIs; Distributed Data subsystem.** Counted once for `distributed-data` and its typed actor integration. Pekko identifies itself as an independently developed fork of Akka; the Akka lineage is not listed again here.

- **C1:** The [Distributed Data guide](https://github.com/apache/pekko/blob/main/docs/src/main/paradox/typed/distributed-data.md) explains that an update timeout does not imply rollback: some replicas may already have received the update, and gossip can complete dissemination later. It also specifies purity requirements for update functions.
- **C2:** Typed keys, a replicator actor, configurable read/write consistency, and an extensible family of counters, sets, maps, and registers provide a reusable distributed-library API.
- **C3:** [`ORSet.scala`](https://github.com/apache/pekko/blob/main/distributed-data/src/main/scala/org/apache/pekko/cluster/ddata/ORSet.scala) distinguishes atomic delta operations, causal-delivery requirements, and groups that can coalesce additions. This is a concrete example of reducing replication traffic while preserving datatype-specific constraints.

### 23. [AntidoteDB/antidote](https://github.com/AntidoteDB/antidote)

**Erlang; `apps/antidote_crdt` operation-based datatype library.** The former standalone `AntidoteDB/antidote_crdt` repository is archived and points here; it is not counted separately. Only the datatype application, not the entire database, is assessed.

- **C1:** The [recursive-reset map](https://github.com/AntidoteDB/antidote/blob/master/apps/antidote_crdt/src/antidote_crdt_map_rr.erl) explains why resetting an entry removes observed effects while preserving concurrent updates, and why an entry is deleted only if its resulting nested state is bottom.
- **C2:** The [library API and development guide](https://github.com/AntidoteDB/antidote/blob/master/apps/antidote_crdt/README.md) separates source-side `downstream` effect generation from replica-side `update`, with reusable counters, flags, sets, registers, and nested maps. It states causal-order requirements and documents EUnit and PropEr checks.

This offers an instructive contrast with state/delta libraries: correctness depends on the surrounding system satisfying the documented delivery contract, not simply exchanging arbitrary effects in arbitrary order.

### 24. [replikativ/replikativ](https://github.com/replikativ/replikativ)

**Clojure/ClojureScript; CRDT library and peer replication framework.** Relevant implementations include observed-remove maps, registers, grow-only sets, and the git-like CDVCS datatype. The [repository guide](https://github.com/replikativ/replikativ/blob/master/README.md) separates networking, storage, CRDT code, and cross-platform integration tests.

- **C1:** The [ORMap core](https://github.com/replikativ/replikativ/blob/master/src/replikativ/crdt/ormap/core.cljc) maintains addition/removal identities and exposes concurrent values. Removing an ambiguous key requires choosing an identity instead of silently selecting one of several alternatives.
- **C2:** [Replication protocols](https://github.com/replikativ/replikativ/blob/master/src/replikativ/protocols.cljc) separate pure downstream application, initial handshakes, missing external values, and pull operations. The pull contract explicitly limits atomicity to the backing store's boundary, an important abstraction limit for applications spanning peers.

Study the combination of immutable datatype logic and asynchronous replication infrastructure. A git-like history CRDT should not be mistaken for automatic semantic resolution of every application-level branch conflict.

## Search coverage, exclusions, and limitations

Discovery used more than a dozen live web-search formulations, followed by GitHub repository/API checks, recursive source-tree inspection, and targeted reads. Representative angles included:

- Rust document engines: `CRDT library Rust Automerge Loro diamond types architecture`.
- JavaScript and structured documents: `CRDT library JavaScript Yjs Yrs json joy delta state` and searches for Collabs composition.
- BEAM implementations: `CRDT libraries Erlang riak_dt lasp delta_crdt Elixir` and operation-based Antidote searches.
- Delta-state kernels: `CRDT library delta C++`, including the reference implementation and Pony descendants.
- Native/mobile and multiplatform APIs: searches for Swift merge libraries and Kotlin/JVM implementations.
- Storage integration: searches for Merkle-CRDT go-datastore implementations, CR-SQLite, and Pekko Distributed Data.
- Algebraic and less prominent ecosystems: Scala/REScala datatype searches, Python/Java/Clojure library searches, and a separate .NET CRDT search.

Later searches increasingly repeated the major algorithm families or produced wrappers, application demos, and broad feature claims needing separate validation. The final selection deliberately includes less prominent substantive implementations rather than ranking by stars. It is not a complete registry: in particular, new .NET and Go candidates surfaced but were not investigated as deeply as the retained implementations.

Pure editor applications, hosted collaboration-service clients, operational-transformation-only projects, tutorial samples, awesome lists, and language bindings without a distinct CRDT core were excluded. Yrs is retained because it is an actual Rust implementation. The old REScala snapshot and archived standalone Antidote datatype repository were replaced by their declared current homes. `nomad/cola` was resolved to its canonical owner. ReplicatingTypes is not duplicated alongside the substantively extended Swift implementation. The Concordant GitHub copy is flagged because its own documentation points to GitLab infrastructure; its mirror freshness remains a limitation.

Historical projects are retained only where the algorithmic implementation or reusable abstractions make them worthwhile study references. Dates described as “last reported a push” are GitHub API observations, not proof of active development or abandonment, and are never used alone to award C4. C1/C2/C3 assessments are engineering judgments grounded in the cited implementations; they are not correctness proofs or independent performance results. Links use the inspected default branches and may change after the research date.
