# Cryptographic transparency logs

Research date: **2026-10-09**

This report selects 21 repositories implementing cryptographically verifiable append-only logs, their proof and witnessing infrastructure, or key directories with verifiable update histories. It covers certificate transparency, software and artifact transparency, checksum databases, and key transparency. Ordinary application audit logs, generic blockchains, and certificate-search wrappers without meaningful verification machinery are outside the scope. The linked source files and design documents are suggested code-reading entry points. This is a selection guide based on primary-source inspection, not a security audit or a claim that every component is exemplary.

Criteria used below:

- **C1 — Difficult correctness:** cryptographic and structural invariants, concurrency, adversarial inputs, or recovery and failure handling.
- **C2 — Reusable abstractions:** substantial interfaces, protocols, or components supporting multiple applications and deployment arrangements.
- **C3 — Performance with structure:** concrete storage, bandwidth, latency, or computation constraints addressed through an understandable architecture.
- **C4 — Sustained evolution:** years of changes with evidence of compatibility work, testing, or complexity management; age alone is insufficient.

## General log engines and reusable primitives

### 1. [google/trillian](https://github.com/google/trillian)

**Go; general-purpose verifiable log service. Status: maintenance mode.** The repository recommends Tessera for new deployments while retaining stability for existing Trillian users. Study how a reusable Merkle-tree service separates application-specific admission rules from sequencing, signing, and persistent tree storage. Its application “personality” boundary is particularly useful when comparing certificate, artifact, and other logging services.

- **C1:** Admission, deduplication, sequencing, and inclusion are separate operations. The [transparent logging design](https://github.com/google/trillian/blob/master/docs/TransparentLogging.md) distinguishes a leaf's Merkle hash from its deduplication identity and explains the relationship between accepted submissions, promises, and integrated log entries.
- **C2:** The same service supports multiple trees and application personalities; the application supplies policy and external APIs while Trillian supplies verifiable storage. The design above provides the architectural starting point.
- **C4:** The [changelog](https://github.com/google/trillian/blob/master/CHANGELOG.md) records releases from 2018 onward, including schema migration work, consistency-proof compatibility, election and shutdown fixes, and changes to integration testing. This is concrete evidence of managing a long-lived distributed storage contract.

### 2. [transparency-dev/tessera](https://github.com/transparency-dev/tessera)

**Go; library for building logs backed by static Merkle tiles.** Tessera is a useful counterpart to Trillian: applications embed a log-writing library, while readers retrieve published objects. Its GCP, AWS, and POSIX implementations expose the different tradeoffs of transactional databases, object storage, and local persistence.

- **C1:** The [design philosophy](https://github.com/transparency-dev/tessera/blob/main/docs/design/philosophy.md) separates assigning a durable sequence number from integrating the entry into a published tree. Concurrent instances must preserve that sequence, and publication must not advertise unavailable data.
- **C2:** Storage implementations preserve the same application-facing behavior without forcing every backend through an overly restrictive storage interface. The [design collection](https://github.com/transparency-dev/tessera/tree/main/docs/design) explains why native backend mechanisms matter.
- **C3:** Sequencing, integration, and checkpoint publication form an asynchronous pipeline. The design discusses batching expensive storage operations and applying backpressure when integration falls behind; these are specific throughput and latency tradeoffs, rather than an unsupported speed claim.

### 3. [transparency-dev/merkle](https://github.com/transparency-dev/merkle)

**Go; Merkle proofs and compact-range algorithms.** This is a focused reusable library, rather than a deployed log. It is valuable for understanding the data structures behind incremental tree construction and combining independently computed tree fragments.

- **C1:** In [compact/range.go](https://github.com/transparency-dev/merkle/blob/main/compact/range.go), constructors check range ordering and the required number of subtree hashes. Merging requires adjacent ranges and compatible factories; computing a complete root requires a range beginning at zero. These checks encode mathematical preconditions directly in the API.
- **C2:** `RangeFactory`, the supplied hash function, and node-visitor callbacks separate Merkle arithmetic from persistence and application payloads. The same implementation supports incremental appends and merging precomputed ranges.
- **C3:** Compact ranges retain a minimal collection of perfect subtree roots covering an interval, avoiding storage of every intermediate node in that working representation. The source is a concise entry point into how representation choices reduce work without obscuring the invariants.

### 4. [golang/mod](https://github.com/golang/mod)

**Go; official GitHub mirror, with the `sumdb` subsystem relevant here.** Counted once as a monorepo: the selection concerns the checksum-database client, signed notes, and transparent-log primitives, not all Go module tooling. Study a verifier that must coexist with ordinary HTTP requests, caches, and concurrent package downloads.

- **C1:** [sumdb/client.go](https://github.com/golang/mod/blob/master/sumdb/client.go) verifies records before caching them, merges checkpoints into a consistent timeline, and persists the latest trusted checkpoint using compare-and-swap. Independent processes updating the configuration must not overwrite a newer trusted state. Inconsistency triggers a distinct security-error path.
- **C2:** `ClientOps` abstracts remote reads, persistent trust configuration, caching, and security reporting. The surrounding [sumdb tree](https://github.com/golang/mod/tree/master/sumdb) separates client logic, note signatures, and Merkle operations so embedders can supply their own environment.
- **C3:** Concurrent request caches suppress duplicate in-flight record and tile fetches. This makes verification practical in a parallel downloader while retaining validation before persistence.

## Certificate transparency servers, libraries, and auditors

### 5. [FiloSottile/sunlight](https://github.com/FiloSottile/sunlight)

**Go; static certificate-transparency log implementation.** The repository describes Sunlight as production-ready. Its architecture splits certificate submission from reads served through object storage, making it an instructive example of a deliberately small write service with a cacheable public read surface.

- **C1:** The repository documents a checkpoint lock using compare-and-swap storage to prevent accidentally running two writers from producing divergent histories. At the protocol boundary, [checkpoint.go](https://github.com/FiloSottile/sunlight/blob/main/checkpoint.go) adapts CT signed tree heads to note verification and rejects mismatched origins, unsupported extensions, invalid algorithm combinations, and trailing data.
- **C3:** Static tiles move public reads away from the sequencing process; batching and worker pools address submission cost. The useful architectural question is how that division changes the load on the small portion of the system that must serialize writes. The [project documentation](https://sunlight.dev/) supplies context alongside the source entry point.

### 6. [cloudflare/azul](https://github.com/cloudflare/azul)

**Rust; static CT log built on Cloudflare Workers and Durable Objects.** Azul provides a substantially different deployment model from conventional database-backed Go services. Its workspace includes CT service code and separate signed-note, tile, and API components.

- **C1:** Cloudflare's [implementation account](https://blog.cloudflare.com/azul-certificate-transparency-log/) explains how a sequencer Durable Object serializes the log and keeps checkpoint state in transactional storage. Request validation, sequencing, deduplication, and object publication have distinct responsibilities.
- **C3:** Batcher Durable Objects combine submissions before they reach the sequencer, reducing scheduling contention. Deduplication combines a short-term cache with longer-term Workers KV storage, while R2 serves the durable static log objects. This is a concrete study in reconciling strongly consistent sequencing with distributed and eventually consistent surrounding services.

Start in [crates/ct_worker](https://github.com/cloudflare/azul/tree/main/crates/ct_worker), then use the engineering account to follow why the batching layer exists. No throughput figures are assumed here.

### 7. [aditsachde/itko](https://github.com/aditsachde/itko)

**Go; historical static CT server with an RFC 6962 compatibility proxy. Archived February 2026.** The public test log stopped accepting submissions. Itko derives from Sunlight, but merits a separate entry for its substantive compatibility and storage design, rather than as another copy of the same implementation.

- **C1:** The [design document](https://github.com/aditsachde/itko/blob/main/DESIGN.md) describes active/passive operation using Consul sessions and compare-and-swap state. The relationship between leader ownership, signatures, and published checkpoints is a useful failover case study.
- **C3:** Supporting legacy `get-proof-by-hash` over static storage requires a reverse index that native tiled reads do not need. Itko partitions hashes by prefix into sorted, binary-searchable files and fronts the static representation with a stateless compatibility proxy. The document also explains how cache behavior affects legacy proof availability.

Read this as a historical exploration of protocol compatibility and operational tradeoffs, not as evidence of a currently maintained service.

### 8. [google/certificate-transparency-go](https://github.com/google/certificate-transparency-go)

**Go; CT protocol libraries, clients, parsers, tools, and a Trillian frontend.** This repository is broader than a server implementation. It offers a particularly useful boundary between hostile real-world X.509 data and the cleaner abstractions expected by a verifiable storage engine.

- **C1:** The repository explains why its ASN.1 and X.509 parsers intentionally tolerate some certificates rejected by the standard Go parsers: CT must observe malformed material rather than silently lose visibility into it. Precertificate and signed-certificate-timestamp handling add further distinctions that ordinary certificate consumers can overlook.
- **C2:** TLS encodings, CT clients, scanning utilities, and the [Trillian subsystem](https://github.com/google/certificate-transparency-go/tree/master/trillian) compose into different consumers and deployments. The frontend translates the public CT HTTP API into Trillian operations instead of embedding application policy into the log engine.

The Trillian subsystem's documentation also describes multiprocess integration tests and randomized API hammering. It is a good entry point for understanding how protocol-level behavior is tested across service boundaries.

### 9. [SSLMate/certspotter](https://github.com/SSLMate/certspotter)

**Go; certificate-transparency monitor and append-only auditor.** Cert Spotter is included for verification and hostile-input handling, not merely for extracting domain names. Study how a monitoring program avoids missing certificates because their unrelated fields are malformed.

- **C1:** The repository describes parsing only the identifiers needed for monitoring and handling ambiguous null-byte name representations conservatively. Its log auditing and checkpoint handling also make tree-consistency failures part of the monitor's responsibilities.
- **C4:** The [changelog](https://github.com/SSLMate/certspotter/blob/master/CHANGELOG.md) spans 2016–2026 and records concrete compatibility and recovery work: handling an empty-tree consistency ambiguity, changing polling behavior, supporting static CT, correcting crash and checkpoint-state handling, and fixing interrupted entry downloads.
- **C3:** The same history documents parallel entry downloading and adaptation to static logs. Together with the repository's monitoring design, this illustrates how an always-running consumer manages download work without treating successful HTTP responses as sufficient evidence of a valid history.

The repository overview and changelog are complementary entry points into the security model and the failure modes found through continued operation.

### 10. [google/certificate-transparency](https://github.com/google/certificate-transparency)

**C++ and Python; historical CT implementation and verification libraries. Archived June 2026.** This is distinct from the Go repository. Its value is historical and algorithmic; the old C++ server is deprecated.

- **C1:** [python/ct/crypto/verify.py](https://github.com/google/certificate-transparency/blob/master/python/ct/crypto/verify.py) separates signed-tree-head signature verification, tree-size and timestamp checks, Merkle consistency verification, and SCT verification. It handles key types and precertificate inputs explicitly rather than collapsing all verification into one boolean operation.
- **C2:** `LogVerifier` composes signature and Merkle verification through a replaceable Merkle-verifier dependency, supporting independent client-side verification workflows.

Read [DEPRECATED.md](https://github.com/google/certificate-transparency/blob/master/DEPRECATED.md) alongside the verifier. It documents how the historical server's in-memory Merkle-tree representation and startup requirements motivated a different storage architecture. Those limitations are part of the study value; they are not evidence that this server is suitable for a new deployment.

## Software, artifact, and supply-chain transparency

### 11. [sigstore/rekor](https://github.com/sigstore/rekor)

**Go; Rekor v1 artifact-signature transparency service. Status: maintenance mode.** Rekor is useful for studying what an application adds above a generic append-only tree: admission checks, canonical entry encodings, type evolution, and artifact-oriented indexes.

- **C1:** [pkg/types/entries.go](https://github.com/sigstore/rekor/blob/main/pkg/types/entries.go) separates unmarshalling historical entries from deciding whether a type/version is currently insertable. It also canonicalizes JSON before logging, avoiding changes in leaf identity caused by ordinary serialization differences.
- **C2:** The entry interface exposes version identification, canonicalization, index keys, verifiers, artifact hashes, and artifact-to-entry construction. The registry in [pkg/types/types.go](https://github.com/sigstore/rekor/blob/main/pkg/types/types.go) dispatches implementations through factories. These are substantial reusable boundaries for supporting different signature and artifact formats.

The interesting compatibility lesson is that an old record must remain interpretable even when accepting new records of that format is no longer allowed. This repository and Rekor v2 below are separate implementations with materially different storage and client contracts.

### 12. [sigstore/rekor-tiles](https://github.com/sigstore/rekor-tiles)

**Go; Rekor v2 service using Tessera and static log tiles.** This redesign narrows the entry surface and changes how clients obtain and retain verification evidence. The repository describes GCP, AWS, and POSIX deployment arrangements.

- **C1:** The [client migration guide](https://github.com/sigstore/rekor-tiles/blob/main/CLIENTS.md) requires clients to reject unknown entry kinds and versions, reconstruct the exact canonical leaf when necessary, and take the root and size from a verified checkpoint. Successful submission waits for a checkpoint containing the entry, changing the admission-to-inclusion boundary.
- **C3:** Readers fetch tiles and compute proofs instead of calling dynamic proof endpoints. Checkpoint publication is batched, trading submission latency for reduced publication work. The guide makes the resulting timeout and monitoring implications explicit.

Use the repository's deployment overview and the client guide together: the instructive material is the connection between a simpler server read path and more explicit client verification duties. Features described as future witnessing work in that guide should not be assumed to be deployed merely because the document discusses them.

### 13. [prefix-dev/siglog](https://github.com/prefix-dev/siglog)

**Rust; tiled transparency server with SQL state, OpenDAL object storage, and a Rekor v2 mode.** This is a newer implementation, included for inspectable mechanisms rather than a claim of long operational maturity. Its stored operating mode and witness policy are explicit parts of the server configuration.

- **C1:** The [bulk-import design](https://github.com/prefix-dev/siglog/blob/main/docs/bulk-import.md) describes a two-pass validation process with an input fingerprint and a database transaction held across uploads. After failure, uncommitted objects can remain; resumption compares bytes rather than silently overwriting them. Import does not itself publish a checkpoint, preserving the normal publication and witnessing boundary.
- **C3:** Bulk import bypasses per-entry HTTP and database work, using bounded chunks and concurrent object uploads. The same document describes independent-root, tile-boundary, restart, changed-input, and rollback checks that exercise this optimized path.

The repository also distinguishes its auxiliary lookup index from authenticated log evidence: an index result is a hint, not a checkpoint-authenticated answer. That distinction is useful when studying feature additions around a minimal transparent log.

### 14. [microsoft/scitt-ccf-ledger](https://github.com/microsoft/scitt-ccf-ledger)

**C++ service application with Python client and tests; SCITT transparency service on CCF.** This adds a ledger-receipt architecture to the selection. Study how generic signed statements, application registration policies, governance, and verifiable receipts fit together.

- **C1:** The [configuration documentation](https://github.com/microsoft/scitt-ccf-ledger/blob/main/docs/configuration.md) distinguishes API authentication, signed-statement verification, and registration policy. Policy receives protected and unprotected COSE material separately. Governance-controlled configuration is part of the admission boundary rather than an incidental deployment setting.
- **C2:** Policy mechanisms allow applications to restrict acceptable statements without redesigning the ledger. The [SCITT protocol documentation](https://github.com/microsoft/scitt-ccf-ledger/blob/main/docs/scitt.md) describes how CCF Merkle receipts are carried with, or separately from, COSE statements, exposing a reusable verification contract to clients.

The documents refer to specific evolving SCITT drafts and state unsupported envelope features. Treat this as an implementation of the documented protocol versions, not an unqualified assertion of compatibility with every later specification.

### 15. [bytecodealliance/registry](https://github.com/bytecodealliance/registry)

**Rust; historical Warg package registry and transparency libraries. Archived July 2025.** The relevant subsystem is `crates/transparency`, together with the registry's signed package histories. The repository states that Bytecode Alliance work moved toward OCI registry tooling; this remains a substantive historical implementation, not a currently developed replacement for that work.

- **C1:** [crates/transparency/src/log/mod.rs](https://github.com/bytecodealliance/registry/blob/main/crates/transparency/src/log/mod.rs) makes leaf/branch hash domain separation and binary-tree indexing explicit. A checkpoint binds a root to a log length; proof construction must preserve that association.
- **C2:** Generic `LogBuilder` and `LogData` traits separate appending/checkpointing from proof access, with distinct log representations behind them. The [registry design overview](https://github.com/bytecodealliance/registry/blob/main/docs/README.md) connects these primitives to immutable signed package logs, consumers, monitors, and importing registries.

This is a useful example of keeping package-state semantics above reusable transparency primitives. The monorepo is counted once, rather than treating its constituent crates as independent projects.

## Witnesses, cosigning, and independently operated logs

### 16. [transparency-dev/witness](https://github.com/transparency-dev/witness)

**Go; checkpoint witness and multi-log witnessing service.** A witness retains previous checkpoints and cosigns verified extensions. This repository makes the persistent state machine behind that seemingly small operation unusually visible.

- **C1:** [witness/witness.go](https://github.com/transparency-dev/witness/blob/main/witness/witness.go) distinguishes stale state, inconsistent sizes, equal-sized trees with different roots, invalid proofs, and signature or origin errors. These distinctions matter when a feeder races another update or retries using an outdated checkpoint.
- **C2:** [witness/persistence.go](https://github.com/transparency-dev/witness/blob/main/witness/persistence.go) defines an atomic, per-origin state-update callback instead of exposing unrelated reads and writes. That contract separates persistence implementations from the verification state machine. Feeders and the multi-log service can reuse the core across different logs.

An experienced engineer can use the two files together to trace exactly which state must be committed atomically before a new signature is safe to release. Inclusion of this component does not imply that any single witness alone solves all split-view attacks; deployment trust policies still matter.

### 17. [sigsum/sigsum-go](https://github.com/sigsum/sigsum-go)

**Go; official GitHub mirror of Sigsum libraries and submit, verify, and monitoring tools.** The repository identifies the [Glasklar upstream](https://git.glasklar.is/sigsum/core/sigsum-go/). It belongs in this category because its tools perform transparency-proof and witness-policy verification rather than merely posting signed blobs.

- **C1:** [doc/policy.md](https://github.com/sigsum/sigsum-go/blob/main/doc/policy.md) specifies trusted log and witness keys, rejects duplicate identities, and defines how nested quorum groups are evaluated. Names and declaration ordering prevent ambiguous or cyclic group definitions. These are security-sensitive configuration semantics.
- **C2:** The policy language expresses thresholds, all-of, and any-of groups for different trust arrangements. It is shared across submitters, verifiers, monitors, and server-side witness selection; offline verification can operate from keys and policy without configured service URLs.

Study the policy document alongside the repository's library/tool layout to see how a small protocol ecosystem shares verification rules without tying every consumer to a single deployment. Mirror status is explicit; this is not counted separately from its upstream project.

### 18. [sigsum/log-go](https://github.com/sigsum/log-go)

**Go; official GitHub mirror of the Sigsum log server.** The [upstream project](https://git.glasklar.is/sigsum/core/log-go/) uses Trillian-backed primary and secondary nodes. It is worth studying separately from the Sigsum client library for its replication and failover protocol.

- **C1:** The [architecture](https://github.com/sigsum/log-go/blob/main/doc/architecture.md) requires replicated leaf durability before the primary publishes the corresponding signed tree head when a secondary is configured. The secondary uses a preordered log rather than independently sequencing entries. Loss of replication therefore affects publication availability instead of permitting two competing orders.
- **C2:** Application-level replication separates independently stored primary and secondary trees, while public Sigsum operations, Trillian storage, and witness interaction remain distinct protocols. The [release notes](https://github.com/sigsum/log-go/blob/main/NEWS) document interoperability with multiple witness implementations and a transition to the common witness protocol while preserving the public log protocol.

The related failover documentation warns that restoring an old backup can violate append-only history. The reusable service boundaries are valuable, but operators must understand the coordinated recovery procedure rather than treating this as ordinary interchangeable database replication.

## Key transparency and authenticated directories

### 19. [facebook/akd](https://github.com/facebook/akd)

**Rust; auditable key directory with a reusable verification core.** AKD extends the scope from public event logs to privacy-preserving maps whose changes remain auditable. The host application supplies storage and service integration.

- **C1:** [akd_core/src/lib.rs](https://github.com/facebook/akd/blob/main/akd_core/src/lib.rs) explains the interaction of VRF-derived labels, commitments, epochs, and fresh/stale entries. Lookup and history proofs combine membership and nonmembership evidence to establish which version is current; append-only audit proofs relate old and new states.
- **C2:** The split between the directory implementation and `akd_core` supports a small verifier, including environments without the full server stack. The [testing guide](https://github.com/facebook/akd/blob/main/TESTING.md) describes a storage-consistency suite for new storage implementations and directory integration tests using those stores.
- **C3:** The core documentation explains marker-based history proofs and batched tree updates. These address proof size and repeated tree work while retaining explicit verification semantics.

This is a strong choice for studying why a verifiable key directory requires more than placing a mutable key-value map next to an ordinary append-only log.

### 20. [signalapp/key-transparency-server](https://github.com/signalapp/key-transparency-server)

**Go; key-transparency server combining log and prefix-tree state.** The server separates query, writing, and testing interfaces. Its persistence documentation is especially useful for readers interested in authenticated structures on an eventually consistent storage layer.

- **C1:** [docs/database.md](https://github.com/signalapp/key-transparency-server/blob/main/docs/database.md) explains how reads are constrained by a signed tree size and why publishing a tree head before the corresponding data is visible is unsafe. The frontier of an incomplete log chunk needs different treatment from immutable complete chunks; persistent prefix-tree updates must retain the references needed to reconstruct the authenticated state.
- **C3:** Log storage groups nodes into chunks, stores selected hashes, and recomputes intermediate values. Prefix-tree updates store immutable path-related information rather than rewriting a complete historical tree. The document connects these choices to storage traffic and lookup work.

Study the database design before the service endpoints: the interesting engineering lies in making proofs refer to one coherent historical state despite different consistency and caching properties in the underlying stores.

### 21. [google/keytransparency](https://github.com/google/keytransparency)

**Go; historical multi-application key-transparency directory. Archived October 2024.** This is useful for comparing earlier map-plus-log architecture with AKD and Signal's implementation. Its remaining work-in-progress language should not be mistaken for a current development commitment.

- **C1:** The [design document](https://github.com/google/keytransparency/blob/master/docs/design.md) combines unique VRF-derived map positions, proofs about signed map heads, and an append-only history of map revisions. It explicitly considers malicious key changes, network segmentation, and the need for users to inspect their own history.
- **C2:** The directory is designed for multiple applications and key formats, with application-specific interpretation of key material above generic lookup, mutation, revision, and proof machinery. That separation makes the code relevant beyond a single messaging application's schema.

The design also leaves parts of gossip and revocation unresolved. Read its threat model as an architectural account with stated limitations, not as proof that every described ecosystem mechanism was completed. The repository and design document provide the implementation and conceptual entry points respectively.

## Search coverage and limitations

Discovery used substantially more than six distinct live-search formulations, including general append-only Merkle log engines; static and tiled CT implementations; CT auditors and hostile-certificate parsing; witnesses and checkpoint cosigning; Rust transparency implementations; Go checksum databases; SCITT/CCF receipts; Warg package transparency; and privacy-preserving key transparency. Additional language-oriented searches considered Erlang and JVM projects. These angles reached different communities: Google and transparency-dev, Sigstore, independent CT operators, Cloudflare, Sigsum, Microsoft, Bytecode Alliance, Signal, Meta, and prefix.dev.

Each retained GitHub repository page was opened, and at least one additional primary design document, implementation file, subsystem document, or changelog was read. Raw source was used when GitHub's rendered file view was unavailable; a second rendering of the same README was not counted as independent evidence. Architectural claims above come from those materials. The judgments that particular mechanisms are worthwhile to study are grounded editorial inferences, not measured comparisons between projects.

The search intentionally excludes generic Merkle libraries without a clear transparency role, tutorial implementations, simple CT-search wrappers, specification-only repositories, and ordinary immutable databases. Catlfish's Erlang implementation surfaced on its non-GitHub upstream, but an appropriate substantive official GitHub mirror was not verified. Early CONIKS-related implementations and small newer wrappers were considered but did not add enough verified implementation coverage to this selection. Later queries mainly returned those overlaps, wrappers, or already retained families.

The selection is Go-heavy because the verified ecosystem is Go-heavy; Rust and the C++/Python implementations provide meaningful architectural diversity rather than artificial language quotas. Trillian and Rekor v1 are explicitly in maintenance mode. Itko, the original Google CT repository, Warg registry, and Google's older key-transparency repository are explicitly historical/archived. The two Sigsum repositories and Go's module repository are identified as official mirrors. Newer projects are not credited with C4 merely because their repositories have recent activity.

No candidate code was executed, dependencies installed, or repositories cloned. Tests mentioned here were inspected through source or documentation, not independently rerun. Some sources contain forward-looking or draft-standard material; such plans are not treated as deployed capabilities. Performance qualifications identify implemented architectural responses to concrete constraints and do not imply independently reproduced benchmarks.
