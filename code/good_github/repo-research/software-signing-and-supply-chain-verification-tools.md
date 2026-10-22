# Software signing and supply chain verification tools

Research date: **2026-10-09**.

This selection covers software artifact signing, signing services, signature transparency, provenance and policy verification, and cryptographically secured software update metadata. It includes libraries and operational tools in Go, Python, TypeScript, Rust, C, and Java. General cryptography libraries, vulnerability scanners, SBOM inventories without substantive verification logic, and projects that merely sign their own releases are outside the scope. The 23 repositories below are a guide to code and design worth studying, not a security audit or a claim that every component is exemplary.

Criteria legend:

- **C1 — Difficult correctness:** security invariants, adversarial inputs, concurrency, or consequential failure modes.
- **C2 — Reusable abstractions:** substantial interfaces, models, or composable subsystems that serve multiple applications.
- **C3 — Performance with structure:** explicit resource, latency, throughput, or scale constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** evidence of years of development together with compatibility work, testing, or complexity management.

Repository identity and archive/fork metadata were checked through GitHub's API. Every entry also has inspected implementation or design evidence beyond the repository overview. Criteria below describe the specific evidence found; omission of a criterion is not a negative assessment.

## Artifact signing clients and reusable verification libraries

### 1. [sigstore/cosign](https://github.com/sigstore/cosign)

**Go — OCI artifact and blob signing, attestations, and verification.** Study how a user-facing signing tool coordinates registry objects, signer identity, certificates, transparency evidence, and multiple generations of signature bundles. This is particularly useful for understanding why a mathematically valid signature is only one part of accepting an artifact.

- **C1:** The verification implementation distinguishes signature verification from certificate-chain construction, expected issuer/subject checks, certificate extensions, and trusted time. Its certificate helpers explicitly require callers to validate chain lifetime against a timestamp. See [`pkg/cosign/verify.go`](https://github.com/sigstore/cosign/blob/main/pkg/cosign/verify.go).
- **C2:** `CheckOpts`, substitutable signature-verification functions, OCI signature/attestation handling, and adapters to `sigstore-go` trusted material compose several verification paths instead of binding the tool to one key or storage model. The same source is the main architectural entry point.

The [changelog](https://github.com/sigstore/cosign/blob/main/CHANGELOG.md) is a useful second entry point for bundle-format and OCI-storage compatibility, malformed-log-entry fixes, and the v2-to-v3 transition. Treat version-specific examples accordingly.

### 2. [sigstore/sigstore-python](https://github.com/sigstore/sigstore-python)

**Python — Sigstore CLI and importable signing/verification API.** A relatively approachable implementation for studying the order of operations in identity-based verification, particularly the relationship between short-lived signing certificates and evidence that remains verifiable later.

- **C1:** [`sigstore/verify/verifier.py`](https://github.com/sigstore/sigstore-python/blob/main/sigstore/verify/verifier.py) explicitly sequences trusted-time establishment, certificate-path and SCT validation, policy checks, log inclusion/checkpoint checks, and consistency between the log entry and signed material. It also limits timestamp counts to constrain denial-of-service inputs.
- **C2:** The verifier separates trusted roots and caller-supplied verification policy from message/DSSE-specific verification. Shared certificate checks are centralized, while callers must complete the payload-specific signature and consistency checks.

The [cross-version verification workflow](https://github.com/sigstore/sigstore-python/blob/main/.github/workflows/cross-version-verify.yaml) exercises new bundles with selected older client versions and distinguishes Rekor v1/v2 compatibility. This is concrete testing evidence, not a claim that every historic version remains supported.

### 3. [sigstore/sigstore-js](https://github.com/sigstore/sigstore-js)

**TypeScript — JavaScript Sigstore libraries; one monorepo, including the verification subsystem.** Study the implementation of the trust protocol in a package ecosystem different from Go and Python. The repository includes signing, bundles, trust-root access, service clients, and mocks; it is not just an invocation wrapper around Cosign.

- **C1:** [`packages/verify/src/verifier.ts`](https://github.com/sigstore/sigstore-js/blob/main/packages/verify/src/verifier.ts) verifies timestamps, signing keys, log evidence, signatures, and identity policy. It rejects duplicate timestamp/log evidence so repeated copies cannot satisfy a threshold intended to require distinct evidence.
- **C2:** `SignedEntity`, `TrustMaterial`, `VerificationPolicy`, and the verifier's key/timestamp/log submodules separate data representation from trust decisions. This accommodates public-key and certificate signers as well as distinct signed-content forms.

For a smaller algorithmic entry point, read [`packages/verify/src/tlog/merkle.ts`](https://github.com/sigstore/sigstore-js/blob/main/packages/verify/src/tlog/merkle.ts). Count the repository once rather than treating its npm packages as independent projects.

### 4. [notaryproject/notation-go](https://github.com/notaryproject/notation-go)

**Go — Notary Project signing and verification library for OCI artifacts and arbitrary blobs.** Useful for studying a certificate-and-policy-oriented alternative to Sigstore's identity/transparency workflow, and the boundary between core signature processing, registry access, and external signing providers.

- **C1:** [`verifier/verifier.go`](https://github.com/notaryproject/notation-go/blob/main/verifier/verifier.go) composes signature integrity, applicable trust policy, trusted identities, certificate stores, and revocation validation. Code-signing and timestamping certificate revocation have separate validator settings; integrity processing is explicitly distinguished from configurable policy behavior.
- **C2:** [`notation.go`](https://github.com/notaryproject/notation-go/blob/main/notation.go) defines signer, blob-signer, verifier, descriptor-generation, and structured verification-outcome abstractions. It also models partial registry failure: a signature can have been pushed successfully even when subsequent referrers-index cleanup fails.

These two files expose both the extensibility contracts and the failure semantics an integrating application must preserve.

### 5. [secure-systems-lab/securesystemslib](https://github.com/secure-systems-lab/securesystemslib)

**Python — Shared signing/key abstractions and signed-envelope support used by TUF and in-toto.** This is the canonical upstream, not the older `in-toto/securesystemslib` fork. Study how higher-level supply-chain tools avoid coupling metadata formats directly to a particular cryptographic backend.

- **C1:** [`securesystemslib/dsse.py`](https://github.com/secure-systems-lab/securesystemslib/blob/main/securesystemslib/dsse.py) handles pre-authentication encoding, rejects duplicate signature key IDs during decoding, validates signature thresholds, and counts accepted keys. The source also documents its key-ID matching deviation from the DSSE specification—an important interoperability limitation to inspect rather than overlook.
- **C2:** [`signer/_signer.py`](https://github.com/secure-systems-lab/securesystemslib/blob/main/securesystemslib/signer/_signer.py) dispatches private-key URIs through an extensible signer registry and supports caller-provided secret handlers. Hardware, cloud, and local signing can share the same application-level interface, while backend/network failures remain visible to callers.

## Identity and signature transparency infrastructure

### 6. [sigstore/fulcio](https://github.com/sigstore/fulcio)

**Go — OIDC-based certificate authority for software signing.** Study how an authenticated workload or human identity becomes a short-lived code-signing certificate, without distributing a long-lived private signing key through every build environment.

- **C1:** The [certificate-issuance walkthrough](https://github.com/sigstore/fulcio/blob/main/docs/how-certificate-issuing-works.md) separates OIDC-token authentication from proof of possession of the requested key, identity/extension construction, CA signing, and certificate-transparency submission. The precertificate/SCT/final-certificate sequence is a consequential protocol boundary.
- **C2:** The same design supports multiple identity forms and CA signing backends, including KMS, PKCS#11, hosted CA services, and local/ephemeral keys. These are alternative implementations within a common issuance pipeline.

Read the [security model](https://github.com/sigstore/fulcio/blob/main/docs/security-model.md) alongside the walkthrough: its trust assumptions include the identity provider, certificate logging, and verification of signing time. Certificate transparency and Rekor's artifact-signature transparency are separate services.

### 7. [sigstore/rekor](https://github.com/sigstore/rekor)

**Go — Rekor v1 signature transparency service and client; maintenance mode.** Retained as a substantive implementation and comparison point for Rekor v2. The repository explicitly states its maintenance status; recent repository activity should not be interpreted as renewed feature development.

- **C1:** [`pkg/verify/verify.go`](https://github.com/sigstore/rekor/blob/main/pkg/verify/verify.go) distinguishes inclusion proofs, checkpoint signatures, consistency proofs, and signed entry timestamps. Its contracts warn that an inclusion proof alone is insufficient without a trusted or verified tree head.
- **C2:** Rekor supports pluggable signed-material types rather than one application-specific record. The [type integration guide](https://github.com/sigstore/rekor/blob/main/types.md) covers independent formats such as Minisign, SSH, PKIX/X.509, TUF, and hashed artifact records.

An experienced engineer can study where canonicalization, log commitments, and signature-format adaptation meet—and how callers can misuse otherwise correct proof primitives.

### 8. [sigstore/rekor-tiles](https://github.com/sigstore/rekor-tiles)

**Go — Rekor v2, a separate implementation using a tile-backed transparency log.** This is the official redesign, not an independent fork counted for breadth. Its inclusion alongside v1 provides a concrete architectural comparison.

- **C1:** [`pkg/verify/verify.go`](https://github.com/sigstore/rekor-tiles/blob/main/pkg/verify/verify.go) binds canonical entry bytes and a checked log index to an inclusion proof and signed checkpoint. It also exposes consistency-proof verification and witnessed-checkpoint verification, keeping their responsibilities explicit.
- **C3:** The [repository's storage architecture](https://github.com/sigstore/rekor-tiles#storage-backends) separates entry sequencing from tile storage: examples pair Spanner with GCS or MySQL with S3, while a POSIX implementation serves smaller deployments. Backend-specific binaries also separate their dependency sets. The documented motivation is lower operational cost and simpler maintenance; no independent throughput claim is made here.

The [end-to-end test guide](https://github.com/sigstore/rekor-tiles/blob/main/tests/README.md) provides the second implementation-study entry point, showing distinct backend test environments. Some operational planning prose in the README is dated; this report does not infer a current public-service rollout schedule from it.

## Provenance, authorization, and policy verification

### 9. [in-toto/in-toto](https://github.com/in-toto/in-toto)

**Python — Supply-chain layouts, signed link metadata, artifact rules, and verification.** Study a model in which the release owner authorizes a sequence of steps and functionaries, then checks the evidence of what actually happened across those steps.

- **C1:** [`in_toto/verifylib.py`](https://github.com/in-toto/in-toto/blob/develop/in_toto/verifylib.py) verifies layout expiration, authorized signature thresholds, and artifact relationships. Different signing subkeys of one main key do not count as separate functionaries toward a threshold. Artifact rules consume sets of materials/products and compare paths and hashes across links.
- **C2:** Layouts, steps, inspections, and reusable rule operations express many pipelines independently of a particular CI provider. The verifier's separation of signature authorization, command alignment, and artifact-rule evaluation makes those semantics inspectable; notably, command misalignment is not simply equivalent to a cryptographic verification failure.

Use [`tests/test_verifylib.py`](https://github.com/in-toto/in-toto/blob/develop/tests/test_verifylib.py) as the second entry point for boundary cases around these verification rules.

### 10. [in-toto/witness](https://github.com/in-toto/witness)

**Go — Pluggable provenance collection and signed policy verification.** Witness originated at TestifySec and is now in the in-toto ecosystem. It is useful for studying how heterogeneous build evidence becomes a normalized collection that can be evaluated at release or deployment time.

- **C1:** The [policy model and verification sequence](https://github.com/in-toto/witness/blob/main/docs/concepts/policy.md) require valid collection signatures, authorized functionaries, optional trusted timestamps, cross-step material/product consistency, and successful embedded Rego evaluation. Expired policies fail verification.
- **C2:** Policies combine attestation types, per-step functionaries, X.509 roots or public keys, certificate constraints, and Rego modules. This supports policy composition across CI, promotion, and admission use cases without fixing one build environment.

Read [`cmd/verify.go`](https://github.com/in-toto/witness/blob/main/cmd/verify.go) after the policy document to see how the CLI assembles verification options and connects the policy model to execution. Do not conflate merely collecting an attestation with satisfying its policy.

### 11. [slsa-framework/slsa-verifier](https://github.com/slsa-framework/slsa-verifier)

**Go — SLSA provenance verifier; historical study selection, no longer actively maintained.** The current README explicitly announces the maintenance limitation and points GitHub Actions users toward GitHub artifact attestations. It remains a substantial source for studying the difference between trusting a signature and trusting the builder that issued it.

- **C1:** [`verifiers/internal/gha/verifier.go`](https://github.com/slsa-framework/slsa-verifier/blob/main/verifiers/internal/gha/verifier.go) derives workflow information from certificates, checks builder identity and source repository, and then checks provenance including the subject digest. Delegating/reusable builders require special identity handling; certificate identity and claimed builder identity are not assumed interchangeable.
- **C2:** [`verifiers/verifier.go`](https://github.com/slsa-framework/slsa-verifier/blob/main/verifiers/verifier.go) provides dispatch and common entry points for artifacts, container images, GitHub attestations, npm packages, and verification-summary attestations. Builder-specific semantics sit beneath those entry points.

This is an explicitly labeled implementation-history resource, not a recommendation to begin a new dependency on an unmaintained tool.

### 12. [gittuf/gittuf](https://github.com/gittuf/gittuf)

**Go — Independently verifiable authorization and activity history for Git repositories.** Study supply-chain verification at the source-control boundary: a valid commit signature does not, by itself, establish that the signer was authorized to change a protected namespace.

- **C1:** The [design document](https://github.com/gittuf/gittuf/blob/main/docs/design-document.md) addresses malicious policy changes, tampering with activity history, and forged enforcement decisions. It combines threshold roots, delegated namespace rules, and a reference-state log stored under custom Git references. Freeze attacks are explicitly outside the stated threat model.
- **C2:** Principals, root-of-trust metadata, rule files, delegations, and repository namespaces provide reusable authorization constructs independent of one hosting forge. The design also explains an important semantic difference from TUF artifact distribution: unprotected namespaces are implicitly allowed.

Pair the design with [`internal/policy/verify.go`](https://github.com/gittuf/gittuf/blob/main/internal/policy/verify.go) to study policy verification against repository history. The project identifies itself as incubating; the report does not equate that with a frozen interface.

### 13. [notaryproject/ratify](https://github.com/notaryproject/ratify)

**Go — Artifact verification orchestration and Kubernetes admission integration.** The canonical repository moved from the `ratify-project` organization. Its README warns that `main` is undergoing Ratify v2 development and may be unstable, and directs v1 development to `v1-dev`.

- **C2:** [`internal/verifier/factory.go`](https://github.com/notaryproject/ratify/blob/main/internal/verifier/factory.go) separates verifier implementation type, instance name, parameters, and scopes. Multiple named configurations can use the same verifier implementation; registration and construction are checked explicitly. The current code integrates the separately packaged `ratify-go` core.
- **C3:** The [concurrency design and implementation addendum](https://github.com/notaryproject/ratify/blob/main/docs/design/Concurrency.md) documents admission-webhook timeout pressure and parallelization across subjects, stores, and artifacts, together with changes to concurrent authentication-cache access. This is evidence about the v1 architecture's performance engineering, not a benchmark or an assertion that v2 has identical internals.

Study this repository for the operational layer around verification: configuration, admission latency, and composing verifier implementations. Keep the v1 history and in-progress v2 structure distinct.

## Secure update metadata and repository signing

### 14. [theupdateframework/python-tuf](https://github.com/theupdateframework/python-tuf)

**Python — TUF reference implementation and reusable update/repository APIs.** Particularly valuable for studying how protocol invariants become state transitions rather than a loose sequence of cryptographic checks.

- **C1:** [`TrustedMetadataSet`](https://github.com/theupdateframework/python-tuf/blob/develop/tuf/ngclient/_internal/trusted_metadata_set.py) enforces role-loading order, root rotation, rollback/version checks, expiration, delegation authority, and snapshot consistency. It distinguishes intermediate metadata retained for rollback protection from metadata acceptable for completing an update.
- **C2:** The [ngclient design retrospective](https://github.com/theupdateframework/python-tuf/blob/develop/docs/_posts/2022-05-04-ngclient-design.md) explains the division into `Metadata`, `TrustedMetadataSet`, `Updater`, and `FetcherInterface`. Trust-state validation, orchestration/persistence, and transport customization have different contracts.

The retrospective candidly describes weaknesses in the previous abstractions and global state, making this a strong complexity-management case study as well as a protocol implementation. Its historical code-size figures should not be mistaken for present-day measurements.

### 15. [theupdateframework/go-tuf](https://github.com/theupdateframework/go-tuf)

**Go — TUF v2 metadata and update-client implementation.** Compare it with Python-TUF to study similar security-state boundaries expressed through Go types, errors, and client configuration. It is a separate implementation, not a mirror of the Python repository.

- **C1:** [`metadata/trustedmetadata/trustedmetadata.go`](https://github.com/theupdateframework/go-tuf/blob/master/metadata/trustedmetadata/trustedmetadata.go) handles root/timestamp/snapshot/target transitions and the subtle retention of expired intermediate metadata for rollback protection. It explicitly documents that the trusted metadata object requires external synchronization for concurrent access.
- **C2:** [`metadata/updater/updater.go`](https://github.com/theupdateframework/go-tuf/blob/master/metadata/updater/updater.go) separates update orchestration and target retrieval from the trusted-metadata state machine. The metadata layer can therefore be studied and integrated independently of the complete download workflow.

The most useful comparison is the division of responsibility between “can this metadata be trusted?” and “which metadata should be fetched or persisted next?”

### 16. [awslabs/tough](https://github.com/awslabs/tough)

**Rust — TUF client, repository-editing libraries, and `tuftool` signing CLI; one monorepo.** A strong choice for studying authenticated streaming and the contract between a secure download library and its caller.

- **C1:** [`tough/src/lib.rs`](https://github.com/awslabs/tough/blob/develop/tough/src/lib.rs) documents that streamed target bytes are available before the final checksum result: consumers must discard them if verification fails. The higher-level save path checks destination containment and uses a temporary file before persistence. Expiration enforcement defaults to the safe mode, while rollback protection depends on retained metadata state.
- **C2:** The [delegated-targets design](https://github.com/awslabs/tough/blob/develop/doc/delegated-targets/README.md) distinguishes `RepositoryEditor` from `TargetsEditor`, with explicit sign-and-switch operations for editing delegated roles. Transport, loading, metadata editing, and key sources are separate integration boundaries.
- **C3:** The asynchronous target stream and bounded metadata/download handling address memory and untrusted-size constraints without requiring every artifact to become a single in-memory buffer.

Some crate-level introductory comments lag the delegation documentation and implementation; this entry does not assert complete conformance to every TUF extension.

### 17. [theupdateframework/tuf-on-ci](https://github.com/theupdateframework/tuf-on-ci)

**Python — TUF repository publication and distributed signing ceremonies on CI.** Useful for studying the human and workflow side of threshold signing: metadata changes, signer invitations, key rotation, signatures, and publication must form a coherent state machine.

- **C1:** [`signer/src/tuf_on_ci_sign/_signer_repository.py`](https://github.com/theupdateframework/tuf-on-ci/blob/main/signer/src/tuf_on_ci_sign/_signer_repository.py) compares proposed roles with known-good state, rejects unexpected changes to online-role files in that comparison, considers previous-root signers during rotation, and verifies newly generated signatures before accepting them.
- **C2:** The [signer manual](https://github.com/theupdateframework/tuf-on-ci/blob/main/docs/SIGNER-MANUAL.md) describes reusable roles, delegations, signing events, and signer workflows, including signers using forks. This machinery supports multiple repositories and signing arrangements rather than one hard-coded release process.

The manual explicitly places trust in the local signing tool rather than CI-generated status messages. The repository describes low-to-moderate artifact/key change frequency as its optimal use case, which is a meaningful scope boundary.

## Native formats, compact signing tools, and signing services

### 18. [jedisct1/minisign](https://github.com/jedisct1/minisign)

**C — Compact detached file-signature tool using Ed25519.** A smaller substantive counterpoint to the distributed frameworks above. Study how a narrow signature format handles authenticated versus unauthenticated metadata and supports large release artifacts.

- **C1:** [`src/minisign.c`](https://github.com/jedisct1/minisign/blob/master/src/minisign.c) validates signature encodings and algorithm identifiers, checks key IDs, verifies the artifact signature, and separately verifies the signature covering the trusted comment. Legacy versus prehashed formats have explicit policy handling.
- **C3:** `message_load_hashed()` incrementally hashes the file through a fixed-size buffer and retains only the digest for signing/verification. This is a concrete memory-scaling mechanism visible in a small implementation; it is not an unsupported claim about execution speed.

[`src/helpers.c`](https://github.com/jedisct1/minisign/blob/master/src/helpers.c) is the second entry point for allocation, output, and error-handling helpers. This entry qualifies through correctness and resource handling, not through claiming the project is a broad framework.

### 19. [mtrojnar/osslsigncode](https://github.com/mtrojnar/osslsigncode)

**C — OpenSSL-based Authenticode signing, timestamping, extraction, and verification.** Study the interaction between cryptographic containers and Windows executable/installer formats, particularly the fact that format parsing itself is exposed to adversarial inputs.

- **C1:** [`pe.c`](https://github.com/mtrojnar/osslsigncode/blob/master/pe.c) implements PE header and signature-location handling, Authenticode digest/page-hash processing, checksum updates, and malformed-file checks. Signature validity depends on hashing the correct format-defined portions of the file, not simply hashing every byte.
- **C4:** The dated [NEWS history](https://github.com/mtrojnar/osslsigncode/blob/master/NEWS.md) documents evolution across 2021–2026: a modular file-format architecture, OpenSSL 3/provider compatibility, changes to testing infrastructure, and repeated parser/verification security fixes.

The same history records serious memory-corruption fixes in 2026. Those are material study evidence and a reason not to describe every historical release as safe merely because the project is long-lived.

### 20. [ebourg/jsign](https://github.com/ebourg/jsign)

**Java — Cross-platform Authenticode signing library, CLI, and build integrations.** Useful for examining how native package peculiarities can be isolated behind Java interfaces while sharing cryptographic providers, certificate handling, and timestamping.

- **C1:** [`AuthenticodeSigner.java`](https://github.com/ebourg/jsign/blob/master/jsign-core/src/main/java/net/jsign/AuthenticodeSigner.java) validates the file against its signing certificate, constructs and verifies CMS signatures before embedding them, selects Authenticode versus RFC 3161 timestamping, and handles existing signatures. It contains compatibility-specific ASN.1 algorithm handling to align output with native signing expectations.
- **C2:** [`Signable.java`](https://github.com/ebourg/jsign/blob/master/jsign-core/src/main/java/net/jsign/Signable.java) abstracts content/digest generation, certificate suitability, signature retrieval/replacement, and persistence. Format providers are discovered through class loaders, so common signing logic can support multiple formats and embedding environments.

These two classes make a useful reading pair: one owns signing orchestration, the other makes file-format obligations explicit.

### 21. [indygreg/apple-platform-rs](https://github.com/indygreg/apple-platform-rs)

**Rust — Apple-platform monorepo; relevant subsystem: `apple-codesign` and the `rcodesign` CLI.** Counted once. Study a native code-signing implementation that can operate outside macOS, including nested bundles, Mach-O signature structures, CMS, notarization, and remote signing.

- **C1:** The [remote signing design](https://github.com/indygreg/apple-platform-rs/blob/main/apple-codesign/docs/apple_codesign_remote_signing_design.rst) analyzes malicious relay servers, wrong-certificate responses, signer presence, session lifetime, and trust-anchor exchange. It keeps the private key on the signing peer and explains why encryption alone does not establish who is authorized to request signatures.
- **C2:** [`apple-codesign/src/lib.rs`](https://github.com/indygreg/apple-platform-rs/blob/main/apple-codesign/src/lib.rs) introduces reusable parsed-signature structures and distinct Mach-O, bundle, DMG, and unified signing interfaces. Binary structures and signing orchestration are exposed as library facilities rather than only CLI commands.

The crate documentation explicitly declines full equivalence with Apple's operating-system execution verification and recommends comparing generated signatures with Apple's tools. This is a signing/format study resource, not a replacement implementation of every Gatekeeper policy.

### 22. [mozilla-services/autograph](https://github.com/mozilla-services/autograph)

**Go — Central signing service for Mozilla content, extensions, updates, and other formats.** Study centralized key custody and request authorization in an operational signing system, with format-specific signers beneath a shared API.

- **C1:** The [architecture document](https://github.com/mozilla-services/autograph/blob/main/docs/architecture.md) separates authenticated request payloads, nonce-based replay checks, user-to-signer authorization, and signing. Its threat model explicitly states that authorization to request a signature does not establish the trustworthiness of the submitted content.
- **C2:** File, data, and hash signing use separate interfaces implemented by signer packages; HSM-backed implementations fit beneath the same service boundary. The [XPI signer design](https://github.com/mozilla-services/autograph/blob/main/signer/xpi/README.md) demonstrates a substantive format adapter: archive manifests, per-request end-entity certificates, COSE/PKCS7 signatures, and repackaging.

The two documents are useful together because they distinguish service authorization from the invariants of the signed package format. Architectural prose should be checked against code when assessing deployment-specific storage or authentication configuration.

### 23. [sassoftware/relic](https://github.com/sassoftware/relic)

**Go — Multi-format package signing CLI and remote signing service with HSM/cloud-key support.** A less prominent but substantial codebase spanning RPM/DEB, Windows packages, Java archives, Apple formats, and other signed artifacts.

- **C1:** [`lib/pkcs9/verify.go`](https://github.com/sassoftware/relic/blob/master/lib/pkcs9/verify.go) checks timestamp message imprints against the external signed data, requires the expected signer-info cardinality, verifies the timestamp signature, and preserves certificate parsing failures for useful error propagation. This illustrates the binding required between a timestamp and the actual signature it timestamps.
- **C2:** [`signers/signers.go`](https://github.com/sassoftware/relic/blob/master/signers/signers.go) separates format identification, stream/file verification, upload transformation, signing, and final file fixups. It explicitly distinguishes format integrity verification from X.509 chain building, helping callers avoid treating one as the other.

Study the signer contracts for an alternative to a single-format signing tool: remote execution, hardware key custody, and package-format operations can vary independently while sharing the command/service infrastructure.

## Coverage, search method, and limitations

Discovery used more than six distinct live web-search formulations, including: OCI signing with Cosign/Notation; TUF implementations and Rust clients; in-toto/Witness/SLSA provenance verification; Rekor and tile-backed transparency logs; Windows Authenticode and Java signing; Apple/Rust code signing; HSM-backed signing servers such as Autograph and Relic; detached Minisign-style tools; and Uptane/firmware verification. Follow-up queries sought less prominent implementations and additional language communities. Later broad queries increasingly returned already covered projects, standards documents, tutorials, or applications merely consuming these tools, indicating diminishing returns within this scope.

Canonical repository URLs, default branches, archive status, and fork status were checked through public GitHub API responses. Relevant source-tree paths were then checked against tree listings, and public source/design files were fetched and read. The retained set contains no repository marked archived at the check; this is not a maintenance guarantee. Explicitly different status signals are preserved above: Rekor v1 is in maintenance mode, SLSA Verifier is no longer actively maintained, and Ratify is undergoing a major rewrite. Ratify's old organization URL and the stale `in-toto/securesystemslib` fork were not counted separately.

Specifications and pure attestation-schema repositories were used for discovery context but excluded as standalone implementation selections. General certificate-transparency engines, generic cryptography/PKI stacks, broad CI engines, and vulnerability/SBOM tools were omitted where their relevant signing or verification contribution was indirect. Automotive update stacks were explored but not expanded into an OTA-system survey; this report concentrates on reusable trust, signing, and verification mechanisms. Different Sigstore clients and TUF implementations remain separate entries because they implement substantial protocol logic in different languages; packages inside a monorepo do not.

All research was read-only. No candidate code was executed, dependencies installed, maintainers contacted, or external services modified. Tests and performance mechanisms were inspected, not independently run or benchmarked. Claims about what an engineer can learn are grounded judgments from the cited material. Moving branch links may change after this date; older design documents, notably parts of Ratify and Tough, must be distinguished from current implementation claims. The selection favors inspectable engineering substance over stars and does not claim exhaustive ecosystem coverage.
