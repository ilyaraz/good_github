# Operational transformation and collaborative editing engines

Research date: **2026-10-09**.

This report selects **22 GitHub repositories** implementing the mechanics of concurrent text, rich-text, or structured-document editing. It covers operational transformation (OT), editing-oriented conflict-free replicated data types (CRDTs), and collaboration runtimes with substantive merging implementations. Small operation libraries and larger applications are both included when the relevant engine can be studied independently. Monorepos count once; their relevant subsystems are identified below.

The criteria are evidence-based selection judgments, not certifications of correctness or recommendations to deploy every project. Historical code can be valuable study material. Archive, discontinuation, and important algorithmic limitations are stated where verified; an unarchived repository is not automatically described as actively maintained.

**Criteria legend**

- **C1 — Difficult correctness:** concurrency, convergence, operation invariants, Unicode semantics, malformed input, or recovery from failure.
- **C2 — Reusable abstractions:** substantial operation models, data structures, protocols, or extension interfaces serving multiple applications.
- **C3 — Performance and structure:** concrete work on latency, memory, indexing, storage, or synchronization costs within an understandable architecture.
- **C4 — Sustained evolution:** years of development accompanied by compatibility management, testing, migrations, or other complexity-control evidence. Age or a recent push alone is insufficient.

## OT operation models and control algorithms

### 1. [Operational-Transformation/ot.js](https://github.com/Operational-Transformation/ot.js)

**JavaScript — text-operation algebra and client/server OT building blocks.** A particularly readable starting point for understanding how optimistic local editing interacts with acknowledgements and remote operations.

- **C1:** The client has explicit synchronized, awaiting-confirmation, and awaiting-confirmation-with-buffer states. A remote operation must be transformed against both outstanding and buffered edits; selections must pass through the corresponding transformations. Reconnection resends outstanding work. These cases are visible in the [client state machine](https://github.com/Operational-Transformation/ot.js/blob/master/lib/client.js).
- **C2:** The [text-operation implementation](https://github.com/Operational-Transformation/ot.js/blob/master/lib/text-operation.js) packages retain/insert/delete operations, base and target lengths, normalization, composition, inversion, and transformation independently of an editor widget. Overridable sending and applying methods separate the control algorithm from transport and presentation.

Study the state transitions alongside the algebra: implementing transformation functions alone does not provide a complete collaboration protocol.

### 2. [ottypes/json0](https://github.com/ottypes/json0)

**JavaScript/CoffeeScript — nested-JSON OT type.** Useful for studying the semantics behind deployed structured-document collaboration, including operations that cannot be reduced to string replacement.

- **C1:** Concurrent list insertion, removal, replacement, and movement alter paths differently from object-key changes. Moves preserve concurrent edits to the moved value; invertible deletions retain their previous content. The [operation specification](https://github.com/ottypes/json0/blob/master/README.md) explains these distinctions.
- **C2:** A registered subtype supplies its own apply/transform/compose/invert behavior inside a JSON document. The [implementation](https://github.com/ottypes/json0/blob/master/lib/json0.js) also translates legacy string operations into the text subtype, illustrating compatibility at an operation-format boundary.

This is the legacy JSON0 design. Its documentation explicitly identifies missing object moves and quadratic pairwise transformation cost for large compound operations. It is retained for its substantive semantics, not as the newest JSON OT design.

### 3. [ottypes/json1](https://github.com/ottypes/json1)

**TypeScript/JavaScript — JSON-tree OT with subtree moves and embedded types.** A strong case study in extending an operation language without making each edit kind an unrelated special case.

- **C1:** Operations combine pickup, drop, and embedded-edit phases. Canonical traversal order and the requirement to redeposit picked-up subtrees constrain valid operations; concurrent initialization and move conflicts add further correctness obligations. These rules are developed in the [JSON1 specification](https://github.com/ottypes/json1/blob/master/spec.md).
- **C2:** The same representation supports cross-container subtree movement, compound edits, and registered text or rich-text subtypes. The [API and interoperability notes](https://github.com/ottypes/json1/blob/master/README.md) distinguish Unicode indexing from JSON0's older string offsets and explain why converting an operation does not necessarily commute with transformation.

**Material limitation:** the README labels this a preview and explicitly reports obscure convergence bugs found by fuzzing, incomplete cursor transformation, and possible API changes. These are part of the study value, not evidence of proven correctness.

### 4. [slab/delta](https://github.com/slab/delta)

**TypeScript — Quill's reusable rich-text document/change algebra.** The canonical repository is now `slab/delta`; the older `quilljs/delta` URL redirects here. Scope is the operation library rather than an entire synchronization server.

- **C1:** Transforming changes requires resolving simultaneous insertions, overlapping deletions, attribute conflicts, and cursor positions. Inversion also needs the base document to recover removed content and formatting. These algorithms are implemented in [Delta.ts](https://github.com/slab/delta/blob/main/src/Delta.ts).
- **C2:** A common Delta representation describes both complete rich-text content and modifications. Registered embed handlers extend composition, inversion, and transformation to embedded objects instead of flattening everything into plain text.

The [changelog](https://github.com/slab/delta/blob/main/CHANGELOG.md) is a useful companion: it records Unicode-surrogate diff fixes, changes to inversion, the TypeScript rewrite, custom-embed OT support, and explicit breaking API/platform changes. This is a compact codebase for studying the boundary between text algebra and editor-specific content.

## Integrated OT backends and editor engines

### 5. [share/sharedb](https://github.com/share/sharedb)

**JavaScript — OT-backed document database and synchronization backend.** Study how a reusable operation type becomes a networked system with document lifecycle, subscriptions, persistence, and recovery.

- **C1:** The [client document implementation](https://github.com/share/sharedb/blob/main/lib/client/doc.js) tracks pending and in-flight operations, matches acknowledgements using source/sequence identifiers, ignores duplicate old operations, catches up on version gaps, and transforms incoming edits against local work. Failed transformations can trigger a hard rollback. It even accounts for edits submitted synchronously from operation callbacks.
- **C2:** Document identity, subscriptions, operation types, middleware, database adapters, and pub/sub integration are distinct extension points. The [project documentation](https://share.github.io/sharedb/) describes their use for JSON collaboration, presence, queries, and historical versions.

Its main educational strength is the distance between a correct transformation function and a robust document protocol: reconnects, creation/deletion races, event reentrancy, and persistence all matter.

### 6. [ether/etherpad](https://github.com/ether/etherpad)

**TypeScript/JavaScript — full collaborative editor; focus on Changeset/EasySync.** The repository supplies an integrated setting in which text, authorship attributes, revisions, and editor behavior meet.

- **C1:** [Changeset.ts](https://github.com/ether/etherpad/blob/develop/src/static/js/Changeset.ts) validates old/new lengths, inserted-character banks, newline counts, and canonical operation form. Its `follow` transformation handles concurrent insert ordering and line-sensitive behavior; composition has separate length constraints.
- **C2:** Serialized changesets, attribute pools, operation iterators, assemblers, and attributed text form a reusable internal representation shared across editing and history handling. The separation is worth studying even when the surrounding application is not needed.
- **C3:** Compact attribute identifiers, coalescing consecutive operations, and iterators over operation streams address representation and processing costs without requiring whole-document replacements.

The [changelog](https://github.com/ether/etherpad/blob/develop/CHANGELOG.md) also exposes compatibility and testing work, including plugin interoperability fixes and downstream-client test gates. It is evidence of engineering tradeoffs, not a claim that every historical subsystem or test suite remains equally maintained.

### 7. [FirebaseExtended/firepad](https://github.com/FirebaseExtended/firepad)

**JavaScript — collaborative text/rich-text editor engine backed by Firebase. Archived.** The former `firebase/firepad` URL redirects to this canonical repository. This is a historical integration study.

- **C1:** The [Firebase adapter](https://github.com/FirebaseExtended/firepad/blob/master/lib/firebase-adapter.js) uses transactional revision slots, distinguishes acknowledgements from competing submissions, retries after disconnects, validates operation lengths, and buffers revisions until the expected one arrives.
- **C3:** The same adapter periodically checkpoints the composed document and initializes from a checkpoint plus subsequent operations, avoiding replay of the complete history for every join. Its comments also acknowledge the cost of representing the current document as a composed text operation.
- **C2:** Adapter events such as operation, acknowledgement, retry, and cursor updates create a boundary between the datastore and OT/editor integration. The [project overview](https://github.com/FirebaseExtended/firepad/blob/master/README.md) places this machinery in a reusable editor component.

Its distinct value is protocol adaptation to a transactional realtime datastore; archive status makes it unsuitable to describe as an actively supported dependency.

### 8. [gobby/libinfinity](https://github.com/gobby/libinfinity)

**C/GObject — Infinote collaboration library and server, including text and GTK adapters.** This adds a native-library architecture and the adOPTed family of concurrency control to the selection.

- **C1:** [InfAdoptedAlgorithm](https://github.com/gobby/libinfinity/blob/master/libinfinity/adopted/inf-adopted-algorithm.c) implements request transformation, state-vector reasoning, and group undo/redo. Causal predecessor/successor calculations and request-log management make the consistency machinery explicit.
- **C2:** The algorithm accepts implementations of `InfAdoptedOperation`; text operations live in `libinftext`, while session transport is handled separately. The [component overview](https://github.com/gobby/libinfinity/blob/master/README.md) distinguishes the core library, server, text plugin, GTK integration, and server-plugin interface.

Study the division between a generic concurrency algorithm and domain-specific operations. It is a substantive alternative to browser-first designs. The API check showed an unarchived repository with its latest recorded push in May 2024; this report makes no stronger current-maintenance claim.

### 9. [saros-project/saros](https://github.com/saros-project/saros)

**Java — collaborative IDE system; focus on the shared core's Jupiter subsystem.** The project integrates concurrent editing into multiple IDEs rather than exposing only a browser text component.

- **C1:** The [Jupiter implementation](https://github.com/saros-project/saros/blob/master/core/src/saros/concurrent/jupiter/internal/Jupiter.java) tracks local/remote vector times and unacknowledged operations, applies transformation priorities, and checks impossible remote timestamps. The [package overview](https://github.com/saros-project/saros/blob/master/core/src/saros/concurrent/jupiter/package-info.java) explains convergence, causality, and intention-preservation goals.
- **C2:** The algorithm is separated from inclusion transformation and operation interfaces, while activities carry user and file identity. The shared core supports the larger editor/resource integration rather than embedding all consistency logic in one IDE's UI.

Treat this as a historical systems case study: the GitHub API's latest recorded push was July 2022, although the repository is not archived. The source itself marks some timestamp-operation behavior as untested, so the documentation's goals should not be read as universal guarantees.

### 10. [apache/incubator-retired-wave](https://github.com/apache/incubator-retired-wave)

**Java — official archived GitHub copy of the retired Apache Wave reference implementation.** Study the document-operation engine inside the `wave` subsystem, in the context of a federated collaboration system.

- **C1:** The [document Transformer](https://github.com/apache/incubator-retired-wave/blob/master/wave/src/main/java/org/waveprotocol/wave/model/document/operation/algorithm/Transformer.java) decomposes each operation into insertion and non-insertion portions, transforms four combinations, and composes the results. The code notes an observable representation difference from the reference implementation: redundant annotations may remain without changing operational effect.
- **C2:** `DocOp`, paired transformation results, decomposers, composers, and specialized transformers separate document-operation mechanics from the server and web client. This is a useful example of controlling the complexity of rich-document OT with intermediate representations.

The [project overview](https://github.com/apache/incubator-retired-wave/blob/master/README.md) identifies the server/client reference implementation and separate unit, database, and larger test targets. Retirement and the read-only archive are explicit; this entry is for historical architecture study.

### 11. [ckeditor/ckeditor5](https://github.com/ckeditor/ckeditor5)

**TypeScript/JavaScript — rich-text editor framework; focus on `ckeditor5-engine` model-operation transformation.** Counted once as a monorepo. The selected subsystem is its public source for structured editing operations.

- **C1:** [transform.ts](https://github.com/ckeditor/ckeditor5/blob/master/packages/ckeditor5-engine/src/model/operation/transform.ts) handles pairs of insert, move, split, merge, rename, attribute, marker, and root operations. Transforming operation sets must update base versions and sometimes pad with no-ops when one operation splits into several; undo relations and removal priority influence conflict resolution.
- **C2:** Operation classes and a transformation dispatch table provide a common model for many rich-text features. Studying this layer shows why tree-shaped editing needs more machinery than adjusting character offsets.

The [release changelog](https://github.com/ckeditor/ckeditor5/blob/master/CHANGELOG.md) supplies additional context on engine fixes and migration costs. This entry concerns the model engine; availability of commercial collaboration packages or a hosted collaboration service is a separate product question.

## CRDT and history-based editing engines

### 12. [yjs/yjs](https://github.com/yjs/yjs)

**JavaScript — shared types for collaborative text, rich text, XML-like structures, arrays, and maps.** A strong study target for the relationship between convergence algorithms and practical in-memory representation.

- **C1:** [INTERNALS.md](https://github.com/yjs/yjs/blob/main/INTERNALS.md) explains item identities, left/right origins for concurrent insertion, deletion sets, and garbage collection. Insertions and deletions use different replication mechanisms, making their interaction worth examining rather than treating every update identically.
- **C2:** Shared types, transactions, update events, and transport-independent synchronization support several editors and application models. The [Yjs documentation](https://docs.yjs.dev/) describes the provider and editor-integration ecosystem around these boundaries.
- **C3:** The internals document explains grouping consecutive characters into items, per-client storage indexed by identity, and cached position searches. These are concrete responses to object allocation, lookup, and synchronization costs.

The architectural lesson is how one list-oriented conflict-resolution core can underpin multiple public types while exposing document-friendly APIs.

### 13. [y-crdt/y-crdt](https://github.com/y-crdt/y-crdt)

**Rust — Yrs, a native reimplementation of the Yjs CRDT with language bindings.** Included separately because its transaction model, native storage, and interoperability responsibilities are substantive implementation work.

- **C1:** The [Yrs crate documentation and source](https://github.com/y-crdt/y-crdt/blob/main/yrs/src/lib.rs) specifies unique client identities, exclusive mutable transactions, and state-vector-based synchronization. It explicitly warns that concurrently reused client IDs can corrupt document state and explains what incremental update delivery assumes.
- **C2:** Typed text, array, map, and XML references share a document/transaction abstraction. The same source documents rich-text formatting, embeds, observer updates, and configurable thread-safety constraints, making it useful beyond a single editor binding.
- **C3:** Transaction completion batches cleanup, metadata compression, and notification. State-vector differences let a peer send the missing portion of a document rather than serialize the entire visible value each time.

Compatibility is a concrete concern: the documented `small-client` feature preserves interoperability with older client-ID formats. Protocol compatibility should be checked for the versions being integrated.

### 14. [automerge/automerge](https://github.com/automerge/automerge)

**Rust core with JavaScript/WebAssembly and other interfaces — local-first collaborative documents.** Study the separation of document history, materialized state, and per-peer synchronization.

- **C1:** The [core documentation](https://github.com/automerge/automerge/blob/main/rust/automerge/src/lib.rs) describes sequential actor histories, concurrent heads, retained conflicting map values, and text-indexing differences across native and WebAssembly targets. Deterministically selecting a visible winner does not erase the conflicting alternatives.
- **C2:** Explicit and automatic transaction APIs share reading, mutation, historical-query, and synchronization interfaces across maps, lists, and text. Incremental patches allow an editor to maintain a materialized view without rebuilding it after every change.
- **C3:** The [sync implementation](https://github.com/automerge/automerge/blob/main/rust/automerge/src/sync.rs) maintains peer-specific heads, in-flight state, and compact knowledge summaries to negotiate missing changes. It also contains protocol-version handling and compatibility-test integration.

The documented synchronization protocol assumes a reliable, ordered stream; that transport requirement is distinct from the document CRDT's ability to merge concurrent histories.

### 15. [loro-dev/loro](https://github.com/loro-dev/loro)

**Rust with WebAssembly bindings — collaborative JSON, rich text, and versioned document containers.** Especially useful for studying rich-text intent and the consequences of trimming history.

- **C1:** The [rich-text design article](https://www.loro.dev/blog/loro-richtext) explains paired style anchors, boundary expansion, concurrent formatting, and several text-coordinate systems. The [shallow-snapshot concurrency contract](https://github.com/loro-dev/loro/blob/main/docs/shallow-snapshot-concurrency.md) distinguishes outdated dependencies from temporarily missing dependencies and links guarantees to concrete tests.
- **C3:** The rich-text design separates content indexing from style-range indexing using B+ trees, allowing different storage granularity for text and formatting. History compaction is also treated as an explicit synchronization tradeoff.
- **C2:** The engine exposes collaborative containers and version/history operations for applications beyond one editor, while the rich-text representation can be translated to familiar editor deltas.

**Material limitation:** peers that continue editing from before a published shallow root may be unable to merge their changes into shallow replicas. The contract explains when rejection or indefinitely pending changes occur; compaction is not transparent to every offline peer.

### 16. [josephg/diamond-types](https://github.com/josephg/diamond-types)

**Rust — text-editing CRDT/history engine with positional-operation interoperability.** A focused performance study, with an evolving API and deliberately exposed tradeoffs.

- **C1:** [ListBranch and ListOpLog](https://github.com/josephg/diamond-types/blob/master/src/list/mod.rs) distinguish a document checkout from its operation history. A branch's content and version must change together; operations carry identities, causal parents, original positions, and lengths. Merging must reconcile these histories before emitting edits for a view.
- **C3:** The same source describes struct-of-arrays storage and independent run-length encoding of operation fields. The current portion of [INTERNALS.md](https://github.com/josephg/diamond-types/blob/master/INTERNALS.md) explains compact causal graphs and the distinction between original, merge-internal, and transformed operations.
- **C2:** The operation log supports checkout, history traversal, binary encoding, merging, and transformed-operation iteration, allowing an editor to consume ordinary positional changes.

The README warns that the published Cargo package lags repository development. `INTERNALS.md` explicitly labels a later section as an older design; that section should not be mistaken for the current implementation.

### 17. [composablesys/collabs](https://github.com/composablesys/collabs)

**TypeScript — composable collaborative collections; focus on `core` and `crdts`.** Its distinguishing contribution is treating collaborative objects as composable building blocks rather than providing only a fixed document schema.

- **C2:** [CList](https://github.com/composablesys/collabs/blob/master/crdts/src/list/c_list.ts) contains mutable collaborative values and composes membership, position, and presence state from smaller objects. A separate total-order abstraction and local views support list movement, archive, and restore behavior.
- **C1:** Deleting a value permanently discards later/concurrent operations on that value, while archive/restore follows different semantics. [CRichText](https://github.com/composablesys/collabs/blob/master/crdts/src/list/c_rich_text.ts) adds formatting spans that affect concurrent and future characters, typed formatting values, and configurable end-boundary growth.

The rich-text source candidly documents differences from Peritext, including local-format inference and limitations around some non-growing span boundaries. It is useful for examining how application-facing composition and event APIs expose, rather than eliminate, semantic choices in collaboration.

### 18. [streamich/json-joy](https://github.com/streamich/json-joy)

**TypeScript — JSON CRDT, rich-text CRDT, and OT tooling in a larger monorepo.** Scope here is the collaboration machinery, particularly `packages/json-joy/src/json-crdt` and its editor integrations.

- **C1:** The [block-RGA implementation](https://github.com/streamich/json-joy/blob/master/packages/json-joy/src/json-crdt/nodes/rga/AbstractRga.ts) manages timestamped chunks, tombstones, chunk splitting, and deterministic insertion. Maintaining both visible positions and stable identities makes changes to tree metadata correctness-sensitive.
- **C3:** Chunks coalesce runs, subtree lengths accelerate position lookup, and a second set of tree links indexes identities. These structures address the two different access patterns of local position-based editing and remote identity-based operations.
- **C2:** The [ProseMirror binding architecture](https://github.com/streamich/json-joy/blob/master/packages/collaborative-prosemirror/README.md) demonstrates a reusable boundary: local transactions become Peritext operations, while incoming CRDT changes produce targeted editor transactions with cached block reuse.

This is one monorepo entry; its serializers and unrelated utilities are not independently counted. Promotional “fastest” claims and cross-library benchmark ratios are deliberately not adopted here.

### 19. [cryptpad/chainpad](https://github.com/cryptpad/chainpad)

**JavaScript — hash-linked patch-chain collaboration algorithm.** An architectural alternative to both conventional centralized OT servers and ordinary item-identity CRDTs.

- **C1:** The [algorithm and internals documentation](https://github.com/cryptpad/chainpad/blob/master/readme.md) distinguishes the agreed document from uncommitted local work. Reorganizations can revert accepted local patches, which must then return to the pending work; transformations apply to local uncommitted edits.
- **C2:** The engine exposes separate transport and user-interface bindings, plus operation and patch abstractions. [Patch.js](https://github.com/cryptpad/chainpad/blob/master/client/Patch.js) implements ordered operation composition, application, inversion, checkpoint construction, and validation.
- **C3:** Checkpoints bound how much history a joining client must download, with an explicit tradeoff between checkpoint size/frequency and replay cost.

**Material limitation:** the project's blockchain analogy does not imply Byzantine resistance. Its documentation explicitly says the consensus design does not defend against malicious longer side chains. Treat the hash chain as part of the collaboration model, not a standalone security guarantee.

### 20. [xi-editor/xi-editor](https://github.com/xi-editor/xi-editor)

**Rust — discontinued editor core; focus on `rust/rope` revision/CRDT engine.** Included for a substantive editing engine that connects asynchronous plugins, undo, and replica merging.

- **C1:** [engine.rs](https://github.com/xi-editor/xi-editor/blob/master/rust/rope/src/engine.rs) supports edits against previous revisions and a separate full CRDT merge operation for asynchronous or peer-to-peer editing. Deletion multiplicities prevent undoing one of two concurrent deletions from incorrectly resurrecting text.
- **C3:** The engine represents visible text and tombstones with ropes and tracks deleted subsets of a conceptual union string. The [CRDT design document](https://github.com/xi-editor/xi-editor/blob/master/docs/docs/crdt.md) explains snapshot-based coordinate transforms, selective undo, and garbage collection constrained by undo history and in-flight plugin references.
- **C2:** Revision tokens, deltas, undo groups, and mergeable engine state form abstractions usable independently of any particular frontend.

The repository explicitly says the project is discontinued. The conceptual design document discusses an earlier centralized design; the implementation additionally contains the full merge operation, so read the two together.

## Collaboration runtimes and document services

### 21. [yorkie-team/yorkie](https://github.com/yorkie-team/yorkie)

**Go — collaborative document store with an in-repository CRDT implementation.** A useful bridge between sequence algorithms and the operational concerns of a client/server document service.

- **C1:** [RGATreeSplit](https://github.com/yorkie-team/yorkie/blob/main/pkg/document/crdt/rga_tree_split.go) uses creation tickets plus offsets to preserve identities across splits. The implementation explicitly handles garbage associated with split tombstones and identity-preserving restoration, illustrating how undo-related operations and garbage collection interact.
- **C3:** Text is grouped into blocks to reduce per-character metadata. A splay tree handles visible-index lookup, while a left-leaning red-black tree handles stable-ID lookup; editing splits blocks as needed.
- **C2:** The [system overview](https://github.com/yorkie-team/yorkie/blob/main/README.md) separates clients, documents, and the server, with persisted changes/snapshots and multiple storage backends. The shared document model supports offline modification and later synchronization.

The selected code is the Go document/CRDT core and service, rather than counting each SDK as another engine. Server-side restoration primitives should not be confused with a complete server-side undo-stack implementation; the source makes that distinction explicit.

### 22. [microsoft/FluidFramework](https://github.com/microsoft/FluidFramework)

**TypeScript — collaborative application runtime; focus on distributed data structures and MergeTree.** Counted once despite its many packages and reference services.

- **C1:** The [MergeTree implementation guide](https://github.com/microsoft/FluidFramework/blob/main/packages/dds/merge-tree/README.md) explains how a remote operation's client identity and reference sequence number determine which inserted or removed segments existed in its coordinate system. Local operations awaiting sequencing require special treatment.
- **C2:** MergeTree is reused by sequence and matrix data structures. At the runtime level, loaders, containers, data stores, distributed data structures, and services have separate responsibilities, as described in the [architecture guide](https://fluidframework.com/docs/concepts/architecture).
- **C3:** Segment grouping and B+ tree indexing accelerate position lookup; stored summaries reduce loading work. A total-order broadcast service assigns operation sequence numbers while clients perform the domain-specific merging.

This is an important comparison point for fully decentralized engines: its consistency architecture deliberately relies on ordered service delivery and compatible client-side merge logic.

## Coverage, verification, and limitations

Discovery used more than six distinct live-search formulations. Search angles included browser OT backends; JSON-tree and rich-text operation types; native C and Java concurrency algorithms; Rust editing engines; CRDT shared-type libraries; composable collections; Go collaborative document services; hash-chain collaboration; Fluid's ordered-broadcast architecture; and Python/Go/C++ ports. Follow-up searches for less prominent implementations increasingly returned small direct ports, demonstration editors, and bindings to engines already represented here.

Canonical repository names and URLs were checked through GitHub repository pages or the public GitHub API. Each retained entry was also checked against an additional primary implementation or architectural source, read directly rather than inferred from a search snippet. Source links identify the inspected entry points. Some use moving default branches and can change after this research date. Release notes were used selectively for context; **no entry relies on C4 alone, and this report does not award C4 merely for age, archive status, or recent activity**.

Important exclusions and boundaries:

- **ProseMirror's `prosemirror-collab` was excluded:** its [GitHub README](https://github.com/ProseMirror/prosemirror-collab/blob/master/README.md) says development moved to `code.haverbeke.berlin`, and the GitHub repository is archived. An ongoing official GitHub mirror was not established in this research.
- Thin rich-text wrappers, Yrs language bindings, simple editor demos, benchmark-only repositories, and awesome-lists were not counted as independent engines. Yrs itself qualifies as a substantive native implementation; monorepo subsystems and SDKs were not multiplied into separate entries.
- Generic replicated databases and CRDT collections without a clear collaborative-editing role were outside scope. Application repositories were included only where a substantial engine was directly inspectable.
- The selection is strongest in JavaScript/TypeScript and Rust, with C, Java, and Go supplying distinct designs. Searches for Python and C++ additions did not establish comparably strong, independently differentiated candidates within this pass; language diversity was not padded with wrappers.

The explanations of what an engineer can learn and which criteria a repository satisfies are grounded assessments of the linked material. No candidate code was executed, no dependencies were installed, and no benchmark results were independently reproduced. Known limitations are reported where material, but this is a source-selection guide rather than a comprehensive correctness, security, or maintenance audit.
