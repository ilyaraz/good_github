# End-to-end encrypted messaging libraries

Research date: **2026-10-09**.

This selection covers reusable implementations of encrypted messaging protocols and substantial client SDKs that coordinate encryption, identities, devices, persistence, and delivery. It includes pairwise ratchets, MLS groups, Matrix, OMEMO/XMPP, OTR, peer-to-peer messaging, and encrypted messaging over email. Generic cryptographic primitives, transport-only security, complete chat applications without a reusable core, and thin language bindings are outside the selection. Monorepos appear once, with the relevant subsystem identified.

The criteria describe engineering material worth studying, not a security certification or an assertion that every component is exemplary. Maintenance and integration limitations are distinguished from architectural interest. Repository identity, default branch, archive status, and source paths were checked against public GitHub pages and API metadata; a recent push alone is not treated as evidence of maturity.

- **C1 — Difficult correctness:** protocol invariants, concurrency, adversarial inputs, state transitions, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces and components that support multiple applications or integration choices.
- **C3 — Performance with structure:** concrete resource or throughput constraints addressed through understandable implementation choices.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate complexity management.

## Pairwise ratchets and Matrix encryption

### 1. [signalapp/libsignal](https://github.com/signalapp/libsignal)

**Rust; Java, Swift, and TypeScript APIs.** Focus on `rust/protocol`, rather than the monorepo's unrelated media and networking components. This is a useful study of keeping a messaging protocol core separate from application identity policy, persistent session records, and language bridges.

- **C1:** The Double Ratchet implementation consumes cached message keys, rejects duplicate counters, bounds forward jumps, and limits retained receiver chains. Deserializing stored root and chain keys also validates their shapes. These are concrete interactions between replay handling, delayed delivery, corrupted storage, and resource exhaustion. See [the ratchet implementation](https://github.com/signalapp/libsignal/blob/main/rust/protocol/src/double_ratchet.rs).
- **C2:** Separate asynchronous traits cover identity trust, sessions, ordinary and signed prekeys, post-quantum prekeys, and group sender keys. Applications supply storage and trust decisions without rewriting the ratchet. See [storage traits](https://github.com/signalapp/libsignal/blob/main/rust/protocol/src/storage/traits.rs).

**Integration limitation:** The repository explicitly says use outside Signal is unsupported and APIs may change without notice. The public source is highly relevant for study, but does not promise a stable general-purpose dependency contract.

### 2. [wireapp/proteus](https://github.com/wireapp/proteus)

**Rust; asynchronous pairwise encryption used by Wire.** Proteus implements the Axolotl/Double Ratchet family without header keys, with prekey session establishment and CBOR serialization. Study its explicit send-chain, receive-chain, envelope, and session boundaries.

- **C1:** Receive chains distinguish outdated, duplicate, invalidly authenticated, and excessively distant messages. Skipped keys are staged separately, their retention is bounded, and authenticated cached keys are removed only after verification. The implementation also handles arithmetic overflow when merging retained keys. See [session and receive-chain code](https://github.com/wireapp/proteus/blob/develop/src/internal/session.rs).
- **C2:** Session logic works with an application-provided `PreKeyStore`; independently serializable keys, messages, and sessions make the engine usable beneath different storage and transport systems. The same source exposes these boundaries.

The [changelog](https://github.com/wireapp/proteus/blob/develop/CHANGELOG) records migration from libsodium to RustCrypto and WASM-related CBOR work. This also reveals a documentation caveat: the README's primitive-provider description lags that migration.

### 3. [status-im/doubleratchet](https://github.com/status-im/doubleratchet)

**Go; compact reusable Double Ratchet engine.** This is a smaller implementation worth comparing with the larger Rust cores, particularly for the division between cryptographic state, persistent sessions, and message-key acknowledgment.

- **C1:** Decryption computes prospective ratchet changes on a separate state value before applying them after successful decryption. It also retains message keys pending confirmation and exposes explicit deletion, making delivery semantics an application concern rather than something to infer from a generic decrypt API. See [session operations](https://github.com/status-im/doubleratchet/blob/develop/session.go).
- **C2:** Constructor options replace the cryptographic implementation and skipped-key store, while independently configuring forward skips, retention duration, and total keys per session. See [configuration options](https://github.com/status-im/doubleratchet/blob/develop/options.go).

**Historical status:** The README calls the library beta; [GitHub metadata](https://api.github.com/repos/status-im/doubleratchet) records its latest repository push in 2020. Its key-retention behavior deserves particular attention when studying replay and acknowledgment policy; this entry does not imply current maintenance.

### 4. [matrix-org/vodozemac](https://github.com/matrix-org/vodozemac)

**Rust; Olm and Megolm cryptographic ratchets.** This library supplies the lower-level encryption machinery underneath Matrix clients. It is especially useful for studying how delayed-message support can coexist with bounded secret retention.

- **C1:** The receive chain finds or derives a candidate key, authenticates/decrypts, and only then removes an old key or installs the advanced chain. Failed authentication therefore does not commit that chain advancement. See [receiver-chain implementation and tests](https://github.com/matrix-org/vodozemac/blob/main/src/olm/session/receiver_chain.rs).
- **C3:** A fixed-capacity key store bounds retained skipped keys. When advancing far enough that intermediate keys would immediately be discarded, the implementation advances the chain without expanding those message keys. The source explains the delivery assumptions behind the retention policy.
- **C4:** The [2024–2026 changelog](https://github.com/matrix-org/vodozemac/blob/main/CHANGELOG.md) documents libolm compatibility, API changes, stricter signature handling, and a fix for imported one-time keys being overwritten. This is evidence of managing compatibility and security-sensitive evolution, beyond repository age.

### 5. [matrix-org/matrix-rust-sdk](https://github.com/matrix-org/matrix-rust-sdk)

**Rust; Matrix client SDK, specifically `matrix-sdk-crypto`.** This is the application encryption state machine above the ratchets. Study device trust, cross-signing, key sharing, recovery, and storage integration rather than treating it as another implementation of Olm arithmetic.

- **C1:** The crypto API represents sender trust requirements explicitly, distinguishing untrusted, cross-signed, and legacy-session acceptance. It has separate failure types for session creation, identity trust, room encryption, verification, and secret imports. See [crypto API and state-machine exports](https://github.com/matrix-org/matrix-rust-sdk/blob/main/crates/matrix-sdk-crypto/src/lib.rs).
- **C2:** The [architecture document](https://github.com/matrix-org/matrix-rust-sdk/blob/main/ARCHITECTURE.md) separates the crypto state machine from network operations and places persistence behind `CryptoStore`. SQLite, IndexedDB, and memory implementations support native and browser clients, while higher SDK layers coordinate encryption synchronization.

This monorepo is counted once. Its value is the substantial orchestration above `vodozemac`, not its generated platform bindings alone.

## MLS group encryption and integration

### 6. [openmls/openmls](https://github.com/openmls/openmls)

**Rust; Messaging Layer Security implementation.** OpenMLS is a strong entry point for studying how to turn a complex group protocol into an API that constrains application mistakes.

- **C1:** Its [message-validation design](https://github.com/openmls/openmls/blob/main/book/src/message_validation.md) describes typed processing stages for syntax, group/epoch consistency, sender checks, signatures, membership tags, proposals, and commits. It maps individual validation requirements to tests and separates validated commits from the application's decision to merge them.
- **C2:** [Provider traits](https://github.com/openmls/openmls/blob/main/book/src/traits/traits.md) separate randomness, cryptographic operations, and persistence. Versioned storage traits and distinct key/entity interfaces allow alternative backends while preserving the protocol's typed data model.

The application still owns policy decisions such as credential acceptance and some key-package lifecycle management. The provider boundary makes those responsibilities visible rather than eliminating them.

### 7. [awslabs/mls-rs](https://github.com/awslabs/mls-rs)

**Rust; MLS implementation with configurable providers.** A useful counterpart to OpenMLS because identity validation, application rules, storage, and cryptographic providers are explicit components of client configuration.

- **C1:** [Message verification](https://github.com/awslabs/mls-rs/blob/main/mls-rs/src/group/message_verifier.rs) distinguishes member, external, new-member-commit, and new-member-proposal senders. It selects the appropriate signing identity, checks membership-tag rules, and rejects invalid combinations such as a new-member commit without an update path. Tests accompany these checks.
- **C2:** [The `ClientConfig` trait](https://github.com/awslabs/mls-rs/blob/main/mls-rs/src/client_config.rs) composes key-package and group-state repositories, pre-shared-key storage, identity providers, protocol rules, cryptography, extensions, and supported versions. This supports substantially different embedding applications without coupling them to one credential or database scheme.

**Qualification caveat:** The repository claims RFC conformance but explicitly says it has not received a full independent third-party security audit. Conformance claims and deployment assurance should not be conflated.

### 8. [cisco/mlspp](https://github.com/cisco/mlspp)

**C++17; MLS protocol library.** MLS++ offers a contrasting C++ design, with explicit ownership, serialized messages, and a higher-level session interface over lower-level group state.

- **C1:** [Session implementation](https://github.com/cisco/mlspp/blob/main/src/session.cpp) enforces the configured handshake encryption policy, locates state by message epoch, retains epoch history for decryption, and associates outgoing commits with cached successor state. These are instructive boundaries between receiving a commit and advancing local state.
- **C2:** [The public session API](https://github.com/cisco/mlspp/blob/main/include/mls/session.h) separates `Client`, `PendingJoin`, and movable `Session` objects. It exposes group membership operations, proposal commits, roster inspection, exported secrets, and application-message protection independently of a delivery transport.

Study the lower-level state API as well when designing an application: the convenience `unprotect` path returns plaintext and its source explicitly notes that exposing authenticated sender information would be useful.

### 9. [Traderjoe95/mls-kotlin](https://github.com/Traderjoe95/mls-kotlin)

**Kotlin/JVM; MLS implementation with low- and high-level APIs.** A less prominent implementation with an instructive Kotlin type model and explicit error values.

- **C1:** [Group state](https://github.com/Traderjoe95/mls-kotlin/blob/main/protocol/src/main/kotlin/com/github/traderjoe95/mls/protocol/group/GroupState.kt) distinguishes active and suspended states and returns typed failures for invalid operations and unknown proposals. Proposal updates construct successor state values. The client also checks group identity and epoch availability before selecting decryption state.
- **C2:** [Group clients](https://github.com/Traderjoe95/mls-kotlin/blob/main/protocol/src/main/kotlin/com/github/traderjoe95/mls/protocol/client/GroupClient.kt) manage epoch history above the protocol state and accept authentication and pre-shared-key services. Applications can choose direct protocol control or a client that manages several lifecycle concerns for them.

**Status limitation:** Although the README describes RFC compliance, its roadmap still lists missing standard functionality and testing/API work. [Repository metadata](https://api.github.com/repos/Traderjoe95/mls-kotlin) shows its latest push in 2024. Treat it as a comparative implementation study, without assuming complete or current production support.

### 10. [wireapp/core-crypto](https://github.com/wireapp/core-crypto)

**Rust with Kotlin, Swift, and TypeScript interfaces; integrated MLS/Proteus engine.** CoreCrypto is valuable because it tackles the failures between protocol operations, persistent storage, and application delivery—not merely cryptographic calls.

- **C1:** [Transaction documentation](https://github.com/wireapp/core-crypto/blob/main/cc-book/src/concepts/client/transactions.md) specifies commit/rollback behavior, transaction-context lifetime, and a single active writer. A callback that fails rolls back its changes, addressing partially completed cryptographic operations and rejected delivery-service commits.
- **C2:** The [architecture](https://github.com/wireapp/core-crypto/blob/main/cc-book/src/development/ARCHITECTURE.md) unifies MLS and Proteus beneath application-level operations, with encrypted SQLCipher storage on native platforms and encrypted IndexedDB storage in browsers. Platform bindings share that substantive implementation.
- **C3:** The transaction guide explains a concrete throughput/latency tradeoff: batching a backlog reduces transaction overhead, but a long batch blocks concurrent sends. This is useful material for designing synchronization and interactive messaging together.

### 11. [xmtp/libxmtp](https://github.com/xmtp/libxmtp)

**Rust core with platform SDKs; XMTP encrypted messaging client.** Focus on `crates/xmtp_mls`, its persistence, identities, and operation intents. This is a substantial integration layer above OpenMLS, not a second independent MLS primitive implementation.

- **C1:** [Intent definitions and serialization](https://github.com/xmtp/libxmtp/blob/main/crates/xmtp_mls/src/groups/intents.rs) encode membership, permission, metadata, and message operations. Versioned decoding rejects missing or unsupported payloads, and guarded metadata updates carry an expected committed value so a stale intent can be abandoned instead of overwriting a newer value.
- **C2:** The [onboarding architecture](https://github.com/xmtp/libxmtp/blob/main/ONBOARDING.md) separates delivery, identity, encryption, local persistence, validation, and platform SDKs. Engineers can study how protocol operations become durable client actions usable by multiple application surfaces.

The onboarding document contains evolving backend descriptions; this report relies on its component boundaries and inspected source, not on a claim about current network decentralization.

## OMEMO and XMPP

### 12. [Syndace/python-omemo](https://github.com/Syndace/python-omemo)

**Python; protocol-level OMEMO orchestration.** This library handles more than the ratchet: device lists, bundles, trust, session creation, and coexistence of specification versions.

- **C1:** Its [functionality specification](https://github.com/Syndace/python-omemo/blob/main/functionality.md) details skipped-key limits and eviction, signed-prekey overlap for delayed messages, inactive-device handling, and trust keyed by identity key plus bare JID. It also states where collision avoidance and backend assumptions are limited.
- **C2:** [The backend contract](https://github.com/Syndace/python-omemo/blob/main/omemo/backend.py) permits multiple OMEMO implementations, with typed session, key-exchange, content, and failure interfaces. Legacy and newer OMEMO backends can share identity and trust while keeping their own sessions; applications supply publication, download, and storage integration.

Study this alongside a ratchet library to see which responsibilities belong to the messaging protocol rather than to cryptographic primitives.

### 13. [gkdr/libomemo](https://github.com/gkdr/libomemo)

**C; legacy OMEMO XML, device-list, bundle, and payload layer.** Its narrow boundary is useful: it implements XEP-0384 version 0.3.0 framing and payload handling, while explicitly leaving Double Ratchet session encryption to another component.

- **C1:** [Message-processing code](https://github.com/gkdr/libomemo/blob/dev/src/libomemo.c) parses untrusted XML, checks required encrypted/header elements, distinguishes malformed inputs, and manages ownership of extracted nodes and buffers across cleanup paths. This is security-sensitive format integration that a ratchet implementation alone does not solve.
- **C2:** [The C interface](https://github.com/gkdr/libomemo/blob/dev/src/libomemo.h) separates bundles, device lists, messages, and an injectable AES-GCM/randomness provider. XML-string input/output and storage-independent protocol functions avoid requiring the consumer to adopt an entire XMPP stack.

**Scope and status:** This is not a complete encryption engine or a current-namespace OMEMO implementation. [GitHub metadata](https://api.github.com/repos/gkdr/libomemo) records its latest push in 2023.

### 14. [dino/libomemo-c](https://github.com/dino/libomemo-c)

**C; Signal-derived ratchet implementation adapted for OMEMO.** This is a substantively evolved fork, not a thin wrapper: its [README](https://github.com/dino/libomemo-c/blob/main/README.md) documents changed KDF context strings, wire encodings, signature handling, Ed25519 identities, and ratchet behavior for newer OMEMO versions while retaining legacy support.

- **C1:** [Session-cipher code](https://github.com/dino/libomemo-c/blob/main/src/session_cipher.c) combines version-sensitive state and KDF selection with duplicate-counter detection, bounded future jumps, identity-bound MAC checks, and cleanup of temporary message keys. Engineers can study the difficulty of supporting related but incompatible wire protocols in one engine.
- **C2:** Its context and store interfaces allow consumers to provide cryptography, locking, identity storage, prekey storage, and serialized session persistence. This makes it reusable in different clients rather than tied to Dino's UI or network stack; the README documents those contracts.

The archived upstream `signalapp/libsignal-protocol-c` is deliberately not counted again. The distinct OMEMO changes justify retaining this descendant.

### 15. [conversejs/libomemo.js](https://github.com/conversejs/libomemo.js)

**TypeScript; browser and Node.js OMEMO cryptographic library.** A substantial modernization of the old Signal JavaScript implementation, with explicit legacy and OMEMO 2 profiles. It supplies per-device ratchet cryptography; consumers still build XMPP stanzas, device-list publication, and encrypted content envelopes.

- **C1:** [Session cipher](https://github.com/conversejs/libomemo.js/blob/master/src/session/cipher.ts) separately bounds work from forward counter jumps and memory retained for skipped keys. It also checks that trust uses the correct published identity-key form, preventing silent substitution of internal curve-key bytes for an Ed25519 identity.
- **C2:** [Protocol profiles](https://github.com/conversejs/libomemo.js/blob/master/src/session/protocol-profile.ts) encapsulate version-specific KDF strings, MAC inputs, key representations, protobuf formats, and framing, while shared session code implements the ratchet. This is a useful design for supporting protocol variants without duplicating the whole state machine.

**Assurance limitation:** The repository explicitly states that it has not undergone a formal independent security audit. Its fork ancestry is disclosed, and the TypeScript/OMEMO adaptation supplies the substantive separate evolution.

### 16. [igniterealtime/Smack](https://github.com/igniterealtime/Smack)

**Java; XMPP client library, specifically `smack-omemo` and its backend integration.** Study how encryption interacts with a real federated messaging protocol: device discovery, prekey publication, carbon copies, session repair, and application trust decisions.

- **C1:** [OMEMO service code](https://github.com/igniterealtime/Smack/blob/master/smack-omemo/src/main/java/org/jivesoftware/smackx/omemo/OmemoService.java) refuses encryption when identity decisions remain unresolved, records recipients that could not be processed, and synchronizes relevant receive paths to avoid simultaneous ratchet changes and bundle publication.
- **C2:** The service's generic cryptographic types and replaceable store/ratchet creation hooks separate the backend from XMPP orchestration. [The manager API](https://github.com/igniterealtime/Smack/blob/master/smack-omemo/src/main/java/org/jivesoftware/smackx/omemo/OmemoManager.java) presents that machinery through connection- and device-oriented operations for applications.

The entire Smack repository counts once. Its inclusion is specifically for the substantive OMEMO subsystem, not for unrelated XMPP extensions or transport encryption.

## Off-the-Record messaging

### 17. [otr4j/otr4j](https://github.com/otr4j/otr4j)

**Java; OTRv3 and interactive OTRv4 implementation.** This is the community fork with substantial refactoring and OTRv4 work, distinct from `jitsi/otr4j`. It is useful for studying deniable messaging, authentication handshakes, and explicit protocol-state separation.

- **C1:** The [design document](https://github.com/otr4j/otr4j/blob/master/docs/design.md) describes separate authentication, messaging, and Socialist Millionaire's Protocol state machines. Validation gates access to client-profile fields, verification uses checked failures, and cryptographic wrappers use `AutoCloseable` to clear sensitive material.
- **C2:** The same design sets out layers for the host-facing API, protocol messages, encoding, session management, and isolated cryptography. A host application supplies `OtrEngineHost` integration while the library contains the protocol machinery.

**Research-stage limitation:** The [README](https://github.com/otr4j/otr4j/blob/master/README.md) explicitly calls the OTRv4 implementation feature-incomplete and tested but not reviewed; noninteractive initiation is missing. [Metadata](https://api.github.com/repos/otr4j/otr4j) shows its latest push in 2024, so the README's active-development wording is not taken as proof of present maintenance.

## Broader reusable encrypted messaging cores

### 18. [TokTok/c-toxcore](https://github.com/TokTok/c-toxcore)

**C; peer-to-peer encrypted messaging network library.** This descendant of `irungentoo/toxcore` has substantial independent evolution; only the TokTok repository is counted. It expands the study beyond store-and-forward servers to encrypted connections, packet queues, retries, and peer networking.

- **C1:** [Network-crypto implementation](https://github.com/TokTok/c-toxcore/blob/master/toxcore/net_crypto.c) combines connection states, authenticated packet decoding, nonce progression, packet-size checks, and bounded queues. Correctness involves both cryptography and network failure behavior.
- **C3:** The same module maintains send-rate, resend, round-trip, and congestion state; queue admission and retry behavior respond to saturation. This gives concrete performance mechanisms to study rather than an unsupported speed claim.
- **C4:** The [changelog](https://github.com/TokTok/c-toxcore/blob/master/CHANGELOG.md) spans 2017 through 2026 and documents compatibility-preserving releases, fuzzing work, memory-safety fixes, and abstraction of clocks, randomness, and allocation for testability.

**Assurance limitation:** The repository calls this an experimental cryptographic network library and says its security model is not fully specified and it has not received a formal independent cryptographic audit.

### 19. [chatmail/core](https://github.com/chatmail/core)

**Rust with C and JSON-RPC interfaces; encrypted messaging core used by Delta Chat/chatmail applications.** This is the canonical GitHub destination of `deltachat/deltachat-core-rust`, not an additional repository. It combines email transport, MIME, OpenPGP-based encryption, Autocrypt, and SecureJoin beneath application APIs.

- **C1:** [SecureJoin implementation](https://github.com/chatmail/core/blob/main/src/securejoin.rs) validates invitation/authentication tokens and fingerprints and distinguishes handshake messages that should be deleted from messages that must remain available to another device. Study authentication state alongside asynchronous delivery and multi-device processing.
- **C2:** The [core overview and integration documentation](https://github.com/chatmail/core/blob/main/README.md) describes a reusable library and JSON-RPC server that hide SMTP/IMAP, MIME, and encryption protocol details from clients and bots. This is a complete messaging core rather than only a key-exchange primitive.

The transport's use of email does not make this a generic mail library: its reusable chat APIs and end-to-end encryption workflow establish category fit.

### 20. [VirgilSecurity/virgil-e3kit-js](https://github.com/VirgilSecurity/virgil-e3kit-js)

**TypeScript/JavaScript; service-integrated client-side encryption SDK.** E3Kit adds a different architecture: application identities and public-key cards, recoverable key handling, and encrypted group sessions exposed through browser, Node.js, and React Native packages.

- **C1:** [Group implementation](https://github.com/VirgilSecurity/virgil-e3kit-js/blob/master/packages/e3kit-base/src/groups/Group.ts) checks session identity and epoch freshness, handles historical epochs and key rotation, restricts membership edits to the initiator, and creates a new epoch when removing participants. These are substantive authorization and lifecycle concerns above primitive encryption.
- **C2:** That class composes a private-key loader, card manager, group manager, and cryptographic session interface. The [repository overview](https://github.com/VirgilSecurity/virgil-e3kit-js/blob/master/README.md) documents platform packages and use with different messaging transports, allowing the encryption layer to be embedded in several kinds of application.

**Integration limitation:** This architecture depends on Virgil service components. [Repository metadata](https://api.github.com/repos/VirgilSecurity/virgil-e3kit-js) records its latest push in 2024; current service availability was not evaluated. Marketing claims about regulatory compliance or quantum resistance were not used as quality evidence.

## Coverage, search method, and limitations

Discovery used more than a dozen live query formulations covering: Signal/Double Ratchet implementations in Rust and Go; MLS implementations and interoperability; Matrix/Olm/Megolm; Wire's protocol and storage layers; OMEMO in Python, C, Java, and TypeScript; OTR libraries and forks; encrypted messaging SDKs; peer-to-peer cores; and native/Kotlin implementations. The [MLS working group's implementation inventory](https://github.com/mlswg/mls-implementations/blob/main/implementation_list.md) supplied an additional primary-source cross-check. Later searches increasingly returned the same protocol families, application repositories, thin bindings, or small demonstrations; the Kotlin implementation and Dino fork were the last distinct additions.

Every retained repository had its canonical identity verified through its GitHub page or API, and at least one additional source document or implementation file was opened and read. Source paths and branches were checked against repository trees. The report distinguishes documented contracts from judgments about what an engineer can learn; the latter are grounded selection judgments, not independent security findings.

Inspected but unselected historical material included the [archived Signal C implementation](https://github.com/signalapp/libsignal-protocol-c) and the [OTRv4 GitHub mirror](https://github.com/otrv4/libotr-ng). Counting both original and adapted implementations without a useful distinction would overstate breadth. Generic TLS/Noise/NaCl libraries, encrypted-storage SDKs without messaging-specific machinery, standalone clients, tutorial ratchets, generated wrappers, and implementation lists themselves were not counted. Closely related retained projects operate at materially different layers or show substantive protocol evolution.

No candidate code was executed, no dependencies were installed, and no repository was cloned. Tests and design claims were inspected rather than independently reproduced. This is a source-based selection guide, not an exhaustive census, a cryptographic audit, a performance ranking, or a guarantee of deployment suitability. The selection is larger than a narrow-category shortlist because reusable messaging code spans protocol engines, device/identity orchestration, and complete client cores with different failure models.
