# Secret storage and cryptographic key management systems

Research date: **2026-10-09**.

This report selects 23 GitHub repositories for studying the implementation of secret storage, cryptographic key lifecycles, encrypted credential formats, and hardware-backed or distributed key protection. It includes both services and local storage systems, plus a few substantial components that distribute or reconstruct secrets. Each entry identifies the relevant boundary explicitly. The selection is an engineering reading guide, not a security audit, deployment recommendation, or assertion that every component is exemplary. Publicly available source does not imply a uniform license across these projects.

Criteria legend:

- **C1 — Difficult correctness:** security invariants, concurrency, adversarial input, cryptographic semantics, or failure recovery require substantial care.
- **C2 — Reusable abstractions:** substantial interfaces or models support multiple applications, providers, storage systems, or policies.
- **C3 — Performance with structure:** the design addresses concrete latency, throughput, scaling, or resource constraints through understandable architectural boundaries.
- **C4 — Sustained evolution:** release or development history demonstrates years of compatibility work, testing, or complexity management; age alone does not qualify.

## Secret services and key-management servers

### 1. [hashicorp/vault](https://github.com/hashicorp/vault)

**Language / role:** Go; general-purpose secrets server, dynamic credential broker, and encryption service.

Vault is useful for tracing a request through authentication, authorization, auditing, secret-engine dispatch, and encrypted persistence. Its core also exposes the operational difficulty of credentials that expire or must be revoked in an external system.

- **C1:** The security barrier separates trusted plaintext processing from untrusted physical storage. Sealing controls access to the encryption hierarchy, while leases, rollback processing, and a write-ahead log address expiration and partially completed operations. These are distinct correctness problems rather than merely encryption-at-rest features.
- **C2:** Authentication methods, secret engines, and storage backends connect through separate extension boundaries. The same core coordinates policy, auditing, leasing, and persistence across these implementations.

**Entry point:** The official [internal architecture](https://developer.hashicorp.com/vault/docs/internals/architecture) explains these boundaries and their failure-handling responsibilities.

### 2. [openbao/openbao](https://github.com/openbao/openbao)

**Language / role:** Go; Vault-derived secrets and encryption server with independent evolution.

OpenBao shares substantial ancestry with Vault, so it should be read as a diverging implementation rather than an unrelated architecture. Its separate work on namespace sealing and external KMS plugins provides a concrete reason to retain both repositories.

- **C1:** Namespace sealing adds tenant-specific cryptographic material and seal-state coordination across nodes. External auto-unseal plugins introduce process crashes and recovery into the root-of-trust path. The [release history](https://github.com/openbao/openbao/releases), including v2.6.0, describes both developments.
- **C2:** The [architecture document](https://github.com/openbao/openbao/blob/main/website/content/docs/internals/architecture.mdx) separates the barrier, storage, auth methods, secret engines, and lease machinery. External KMS plugins extend those boundaries to independently implemented unsealing providers.

**Entry points:** Architecture for the inherited core; releases for evidence of substantive divergence. Their inclusion does not mean the two projects' shared code should be counted twice when comparing implementation volume.

### 3. [cyberark/conjur](https://github.com/cyberark/conjur)

**Language / role:** Ruby and SQL; application identity, policy, and secret storage.

Conjur is particularly useful for studying the boundary between authenticating a workload and authorizing its access to secrets. Its PostgreSQL-backed service combines encrypted stored values with a policy model rather than making possession of a decryption key the only access-control mechanism.

- **C1:** A nondefault authenticator must be enabled by the server and authorized through policy. The design distinguishes initial login, rotatable API credentials, and short-lived authentication tokens, making credential lifecycle and authorization separate checks.
- **C2:** Authenticators implement a common contract, with optional login behavior and a validity check. Service identifiers allow multiple configurations of one authenticator type, while constructor injection separates external dependencies from the authentication logic.

**Entry point:** The [authenticator design](https://github.com/cyberark/conjur/blob/master/design/authenticators/AUTHENTICATORS.md) is a substantive guide to these contracts and policy gates; the repository overview describes the database and encryption boundary.

### 4. [Infisical/infisical](https://github.com/Infisical/infisical)

**Language / role:** TypeScript; secrets-management monorepo, with the backend KMS subsystem especially relevant here.

The KMS service is a strong study target for applying database transactions to cryptographic key lifecycles. Count the monorepo once: its UI, SDKs, secret service, and KMS are not separate repository selections.

- **C1:** Rotation locks the key record, archives existing material before replacement, and advances the version transactionally. Ciphertext parsing handles legacy and versioned formats, checks malformed lengths, and retrieves older key versions for decryption. Advisory locks also coordinate lazy organization-key creation.
- **C2:** The same service coordinates internal keys and external provider-backed keys, enforces algorithm and usage constraints, and exposes organization/project key operations. This makes it possible to follow how provider differences fit a shared lifecycle model.

**Entry point:** Read the [KMS service implementation](https://raw.githubusercontent.com/Infisical/infisical/main/backend/src/services/kms/kms-service.ts), especially rotation, versioned ciphertext handling, and organization-key initialization. These observations concern that inspected subsystem, not a blanket characterization of every Infisical encryption workflow.

### 5. [cloudfoundry/credhub](https://github.com/cloudfoundry/credhub)

**Language / role:** Java; centralized credential generation, storage, versioning, and retrieval.

CredHub makes the relationship between a credential database and an external encryption provider unusually explicit. It is worth studying for recovery design as well as normal CRUD and generation operations.

- **C1:** Restoring the database requires access to the encryption keys appropriate to the backed-up data. Rotation, database snapshots, and HSM availability therefore form a coupled recovery problem. The [backup and restore guide](https://docs.cloudfoundry.org/credhub/backup-restore.html) documents that dependency rather than treating a database backup as sufficient.
- **C2:** Its [KMS plugin protocol](https://docs.cloudfoundry.org/credhub/kms-plugin.html) defines version, encrypt, and decrypt operations through a protobuf service over a local socket. Reusing this provider contract allows encryption backends implemented in different languages without coupling the credential API to one HSM or cloud service.

**Entry points:** The two guides above provide complementary views of the provider boundary: normal calls and recovery obligations.

### 6. [openstack/barbican](https://github.com/openstack/barbican)

**Language / role:** Python; OpenStack secret and key-management service. **Official GitHub mirror:** primary development is hosted on OpenDev, as identified by the repository.

Barbican offers a cloud-platform perspective: API authentication, secret representation, persistence, cryptographic providers, and asynchronous work occupy different layers. The GitHub mirror contains substantive source and is included as a mirror, not as a separate project from OpenDev.

- **C2:** The [architecture guide](https://docs.openstack.org/barbican/latest/contributor/architecture.html) describes middleware, controllers, SQLAlchemy repositories, and cryptographic plugin boundaries. Backend-specific key protection is separated from the public secret-management API.
- **C3:** API processes and queue-driven workers separate request handling from longer-running operations. Multiple API and worker instances provide an understandable scaling structure around the shared persistence and messaging layers.

**Entry point:** The architecture guide is an older overview. Its explicitly prospective regional replication discussion is not evidence that every proposed topology was implemented; the criteria above use its concrete API, worker, and plugin structure.

### 7. [lyft/confidant](https://github.com/lyft/confidant)

**Language / role:** Python; AWS-oriented secret storage and service-to-credential mapping. **Archived in 2025; historical study candidate.**

Confidant is valuable for comparing ordinary server-managed secrets with blinded secrets inside one distribution system. The archival notice means it should not be presented as a currently maintained deployment choice.

- **C1:** For blinded secrets, clients encrypt and consuming services decrypt; the Confidant server can be excluded from decryption through KMS permissions. The resulting trust boundary depends on IAM policy, encryption contexts, and recipient configuration, not just the server's application ACLs.
- **C2:** The blinded-secret model accommodates distinct service groups, KMS keys, and cross-account or regional arrangements while preserving the credential-to-service distribution model. It illustrates how a service can manage encrypted records without necessarily possessing their plaintext.

**Entry point:** The official [blind-secrets design and usage guide](https://lyft.github.io/confidant/blind_secrets.html) explains the two trust models and their KMS configuration implications.

## Specialized KMS and protocol implementations

### 8. [minio/kes](https://github.com/minio/kes)

**Language / role:** Go; stateless key-encryption service between applications and a backing KMS. **Archived and deprecated in 2025.**

KES remains a useful historical example of moving a narrowly scoped key service close to applications while centralizing durable key custody elsewhere. Its archive/deprecation notice is material; this entry evaluates the available implementation rather than promising future fixes.

- **C1:** The key cache must coordinate simultaneous misses, backend deletion, cancellation, and backend unavailability. The implementation uses per-key coordination and rechecks the cache after acquiring the key-specific barrier, making races and cache/backend consistency visible.
- **C3:** Coalescing loads for the same key avoids duplicate backend requests while allowing unrelated key names to proceed independently. The cache and stateless service boundary address backing-KMS latency and load without requiring an opaque distributed application framework.

**Entry point:** Read [keystore.go](https://raw.githubusercontent.com/minio/kes/master/keystore.go), including the key cache, per-key barrier, deletion path, and background cleanup. No numerical performance claims are inferred from this design.

### 9. [Cosmian/kms](https://github.com/Cosmian/kms)

**Language / role:** Rust; KMIP-based key-management server, now identified in the repository as Eviden KMS.

This repository is useful for comparing standards-facing key lifecycle operations with database and hardware-provider integration. The canonical GitHub path remains under Cosmian; the inspected development branch is `develop`.

- **C1:** The [test architecture](https://github.com/Cosmian/kms/blob/develop/TESTS.md) includes KMIP binary and JSON TTLV cases, negative/error assertions, serialization round trips, and backend-oriented testing. Protocol decoding, operation failures, and key persistence are treated as separate test surfaces.
- **C3:** The documented [high-availability deployment](https://github.com/Cosmian/kms/blob/develop/documentation/docs/installation/high_availability_mode.md) uses stateless KMS nodes sharing database state behind a load balancer. This is a concrete scaling boundary: service instances can be added, while database correctness and availability remain explicit dependencies.

**Entry points:** The testing guide and HA design. These sources support studying the architecture; they do not establish a benchmark or certify a particular deployment's security properties.

### 10. [OpenKMIP/PyKMIP](https://github.com/OpenKMIP/PyKMIP)

**Language / role:** Python; KMIP protocol implementation, client library, and testing/development server.

PyKMIP is retained for its substantial protocol and object model. Its server is documented as a testing and demonstration facility, so it should not be confused with a hardened production key-management appliance.

- **C1:** The server maps authenticated TLS certificate identities to object ownership and evaluates operation policies by object type and operation. Missing policy entries deny access, and reserved policies have special handling. These are useful examples of identity and authorization invariants around standardized cryptographic objects.
- **C2:** KMIP represents keys, certificates, passwords, and other managed objects through shared operations and encodings. Client and server implementations make the same model useful for interoperability work, development, and integration testing.

**Entry point:** The [server documentation](https://pykmip.readthedocs.io/en/latest/server.html), especially authentication and operation policies, explains both the implementation model and the server's intended limitations.

### 11. [zama-ai/kms](https://github.com/zama-ai/kms)

**Language / role:** Rust; specialized key management for fully homomorphic encryption, including threshold operation.

This is a distributed-cryptography selection rather than a general password vault. It makes the interaction between cryptographic protocols, service state, and deployment assumptions visible.

- **C1:** Key creation and destruction compete over distributed epoch state. The architecture documents shared lifecycle leases during creation and exclusive leases during destruction, with conflicting destruction rejected. Failed resharing storage triggers cleanup; failed cleanup preserves enough state to retry deletion. These are concrete recovery invariants around threshold key material.
- **C2:** The [architecture document](https://raw.githubusercontent.com/zama-ai/kms/main/ai-docs/ARCHITECTURE.md) separates cryptographic algebra and execution, network types, service engines, and gRPC-facing orchestration. Centralized and threshold operation share a service-facing model while retaining distinct cryptographic implementations.

**Entry point:** Architecture, followed by the repository's security/deployment discussion. Claims here concern the implemented decomposition and protocol responsibilities; they do not imply that application authentication, side-channel protection, or deployment isolation is automatically supplied by the cryptographic protocol.

## Encrypted configuration and secret distribution

### 12. [getsops/sops](https://github.com/getsops/sops)

**Language / role:** Go; encrypted structured configuration and secret files.

SOPS is worth studying because its storage abstraction is a structured document rather than an undifferentiated ciphertext blob. That choice makes diffs useful but also makes document paths, types, and integrity rules part of the cryptographic design.

- **C1:** Leaf encryption binds values to their document paths through authenticated additional data. The [format reference](https://getsops.io/docs/reference/) explains consequences such as problematic YAML aliases whose paths change. Integrity and serialization behavior must remain consistent through editing and format conversion.
- **C2:** The [core implementation](https://raw.githubusercontent.com/getsops/sops/main/sops.go) separates tree traversal, typed values, cipher operations, and key-service interactions. Those interfaces support multiple document encodings and master-key providers without duplicating the entire editing workflow.

**Entry points:** The format reference and `sops.go`. Their combination shows how usability requirements for editable secrets constrain the cryptographic representation.

### 13. [bitnami/sealed-secrets](https://github.com/bitnami/sealed-secrets)

**Language / role:** Go; public-key encryption CLI and Kubernetes controller for storing encrypted secrets in Git.

The canonical repository currently uses `bitnami/sealed-secrets`; the older `bitnami-labs` location redirects. The important study boundary is the conversion from publicly distributable encrypted resources to ordinary Kubernetes Secrets inside the cluster.

- **C1:** The [cryptographic design](https://github.com/bitnami/sealed-secrets/blob/main/docs/developer/crypto.md) combines a fresh symmetric session key with RSA-OAEP wrapping. OAEP labels bind ciphertext to a namespace and name, a namespace alone, or cluster-wide scope. Scope is therefore enforced cryptographically, with explicit consequences for moving resources.
- **C2:** The CLI can encrypt using public material, while the controller owns private-key access and reconciles the custom resource into the standard Kubernetes Secret interface. Producers and workloads can use separate tools while sharing this resource contract.

**Entry point:** The cryptographic design, particularly scope labels. The controller's private-key persistence and recovery remain an essential operational dependency, not something eliminated by committing ciphertext to Git.

### 14. [external-secrets/external-secrets](https://github.com/external-secrets/external-secrets)

**Language / role:** Go; Kubernetes secret synchronization and lifecycle controller. It is a distribution layer over secret stores, not an independent encrypted vault.

External Secrets belongs here because translating stored secrets into workload resources has substantial lifecycle semantics. A simple provider API wrapper would not be an adequate description of this controller.

- **C1:** Refresh policy, ownership, and deletion interact. In particular, the [ExternalSecret API guide](https://external-secrets.io/latest/api/externalsecret/) explains that `CreatedOnce` tracks synchronization on the ExternalSecret; deleting and recreating that resource can cause a fresh synchronization. Confusing resource identity with target-secret existence can unexpectedly change credentials.
- **C2:** SecretStore and ClusterSecretStore references separate provider configuration from individual secret mappings. Templates, refresh policies, and target creation behavior form a reusable reconciliation model across backend providers.

**Entry point:** The API guide's refresh, target, and lifecycle sections. They expose the controller's state model and make a useful starting point before reading provider implementations.

### 15. [AGWA/git-crypt](https://github.com/AGWA/git-crypt)

**Language / role:** C++; transparent encryption of selected files through Git filters.

git-crypt is a compact but substantive example of adapting encryption to version-control semantics. Its documented limits, including metadata leakage and lack of revocation of already disclosed historical data, are part of the design being studied.

- **C1:** Deterministic encryption allows Git to compare encrypted versions, but equality leakage and authenticated file handling must be understood alongside filter configuration. The repository's security discussion describes its synthetic-IV construction and the importance of protecting `.gitattributes`.
- **C4:** The [changelog](https://raw.githubusercontent.com/AGWA/git-crypt/master/NEWS.md) records evolution from 2012 through 2025, including repository-format compatibility, Git behavior fixes, OpenSSL 1.1 support, and OpenSSL 3 compatibility work. These are concrete compatibility obligations, not merely an old creation date.

**Entry points:** The repository's security discussion and `NEWS.md`. The absence of a general key-rotation/revocation workflow makes this a different study target from a server KMS.

## Local credential stores

### 16. [gopasspw/gopass](https://github.com/gopasspw/gopass)

**Language / role:** Go; command-line password and team-secret storage with multiple stores and backends.

gopass offers a useful middle ground between a single encrypted file and a remote vault. Its architecture makes store composition, encryption choice, and synchronization behavior visible without requiring a large service deployment.

- **C1:** The [changelog](https://raw.githubusercontent.com/gopasspw/gopass/master/CHANGELOG.md) documents fixes involving recipient reencryption, path validation, autosynchronization locking, and identity-cache concurrency. These demonstrate concrete correctness pressure where encryption policy meets filesystem paths and background work.
- **C2:** The [architecture](https://github.com/gopasspw/gopass/blob/master/ARCHITECTURE.md) describes independently configured stores mounted into a namespace, with crypto and storage backends loaded through registries. It also explains why revision-control behavior was folded into storage instead of preserving an unhelpfully independent abstraction.

**Entry points:** Architecture and changelog. The explicit discussion of public versus internal Go APIs is also useful for understanding how a CLI project limits its compatibility commitments.

### 17. [keepassxreboot/keepassxc](https://github.com/keepassxreboot/keepassxc)

**Language / role:** C++ / Qt; offline encrypted credential database and desktop/CLI integrations.

KeePassXC is derived from KeePassX but has its own substantial format handling and integration work. The relevant subsystem is the encrypted KDBX reader and its stream layers; the desktop UI is not the sole reason for inclusion.

- **C1:** The [format dispatcher](https://raw.githubusercontent.com/keepassxreboot/keepassxc/develop/src/format/KeePass2Reader.cpp) validates signatures and critical versions before selecting a reader. The [KDBX4 reader](https://raw.githubusercontent.com/keepassxreboot/keepassxc/develop/src/format/Kdbx4Reader.cpp) checks required headers and authentication material, then processes authenticated blocks, decryption, optional decompression, and inner database content.
- **C2:** The reader composes distinct stream and format components rather than merging transport, encryption, compression, and XML processing into one parser. Those boundaries support multiple file versions and the application's broader database operations and interfaces.

**Entry points:** The two reader implementations. They are particularly useful for examining how hostile file input and backward-compatible format support affect error propagation and data-flow structure.

## PKCS#11 implementations and hardware-backed storage

### 18. [softhsm/SoftHSMv2](https://github.com/softhsm/SoftHSMv2)

**Language / role:** C++; software token implementing PKCS#11 object and key semantics.

SoftHSM is valuable for learning that a cryptographic token is an object system with access rules, persistence, and session behavior, not simply an algorithm dispatcher. Its canonical repository is now under `softhsm`.

- **C1:** [P11Objects.cpp](https://raw.githubusercontent.com/softhsm/SoftHSMv2/main/src/lib/P11Objects.cpp) implements attribute-level rules around sensitivity, extractability, modification, and copying. Attribute retrieval must handle mixed valid and invalid requests and buffer-size outcomes, while template updates use transactions to avoid partial changes.
- **C2:** Object classes and attribute handling sit alongside separate storage and cryptographic backend components in the [library source tree](https://github.com/softhsm/SoftHSMv2/tree/main/src/lib). A standard PKCS#11 interface makes the resulting token reusable by unrelated applications without exposing its internal object-store representation.

**Entry points:** `P11Objects.cpp` and the library tree. These support a concrete study of standards-driven semantics; software implementation does not imply the physical protections of a hardware HSM.

### 19. [opencryptoki/opencryptoki](https://github.com/opencryptoki/opencryptoki)

**Language / role:** C; PKCS#11 middleware and software/hardware tokens, including IBM cryptographic adapters.

openCryptoki is useful for studying a common token API over backends whose key formats and hardware restrictions differ substantially. The EP11 token is a focused entry into the larger codebase.

- **C1:** The [EP11 token documentation](https://github.com/opencryptoki/opencryptoki/blob/master/doc/README.ep11_stdll) describes adapter/domain isolation, checking the expected wrapping-key verification pattern, and the dependency between stored wrapped objects and HSM master keys. It also documents a stop-and-migrate procedure; changing the hardware master key without coordinating stored objects can invalidate them.
- **C4:** The [changelog](https://raw.githubusercontent.com/opencryptoki/opencryptoki/master/ChangeLog) spans dated 2010–2013 releases and later 3.x evolution. It records test-suite refactoring, object-format migration tools, OpenSSL compatibility changes, locking redesign, and later concurrent master-key-change support. This is evidence of sustained management of compatibility and concurrency complexity.

**Entry points:** EP11 documentation and changelog. The older migration procedure and later concurrent-change feature should be read with their version context, rather than assumed to describe one identical operational path.

### 20. [tpm2-software/tpm2-pkcs11](https://github.com/tpm2-software/tpm2-pkcs11)

**Language / role:** C and Python; PKCS#11 token backed by TPM 2.0, with provisioning tools.

This project exposes the mismatch between a general token API and TPM-specific object, authorization, and storage mechanics. It is particularly useful for understanding which state lives on disk and which secrets are protected by the TPM.

- **C1:** The [architecture](https://github.com/tpm2-software/tpm2-pkcs11/blob/master/docs/ARCHITECTURE.md) describes a persistent primary object, PIN-derived authorization for sealed wrapping material, and wrapped per-object authorization values. Login state, TPM authorization, and external metadata must remain consistent; the document does not treat every database field as TPM-protected.
- **C2:** SQLite-backed metadata and provisioning are separated from the PKCS#11-facing implementation. The standard interface allows applications to use TPM-backed keys without adopting the TPM's native command and object model themselves.

**Entry point:** The architecture document's key hierarchy and storage discussion. Follow the distinction between a user's PIN, the wrapping key, and individual object authorization rather than treating them as interchangeable keys.

### 21. [latchset/kryoptic](https://github.com/latchset/kryoptic)

**Language / role:** Rust; software PKCS#11 implementation with configurable storage and cryptographic mechanisms.

Kryoptic provides a contrasting implementation language and object model to the older C/C++ token projects. Its value here is the explicit representation of token state and pluggable persistence, not an inference that Rust alone resolves token security semantics.

- **C1:** The [token implementation](https://raw.githubusercontent.com/latchset/kryoptic/main/src/token.rs) maintains bidirectional mappings between handles and object identities and rejects conflicting insertions. It represents security-officer, user, and unauthenticated states explicitly and distinguishes session objects from persistent storage.
- **C2:** The token coordinates a dynamic storage interface, object factories, and a mechanism registry. This lets PKCS#11 operations share object and authentication machinery while storage implementations and cryptographic mechanisms vary.

**Entry point:** `src/token.rs`, with the [source tree](https://github.com/latchset/kryoptic/tree/main/src) providing the adjacent object, mechanism, and storage modules. This is a useful study of how a standards API becomes internal state and dispatch boundaries.

## Network-bound and compositional key recovery

### 22. [latchset/tang](https://github.com/latchset/tang)

**Language / role:** C; network-bound key reconstruction service. Tang is not a server-side escrow database of client plaintext keys.

Tang's narrow protocol offers a distinct architecture from authenticated CRUD secret servers. A client can arrange for reconstruction to depend on reaching a server that holds long-term exchange material, while the server does not learn the reconstructed client key.

- **C1:** The repository's protocol explanation describes blinded recovery and the key-retirement requirement: old exchange keys must remain available until dependent clients migrate. In [tangd.c](https://raw.githubusercontent.com/latchset/tang/master/src/tangd.c), recovery checks key usage, key type, algorithm compatibility, and the requested key identifier before the exchange operation.
- **C2:** Advertisement and recovery are represented as a small JOSE/HTTP protocol that different clients can consume. Separating reconstruction from disk encryption or credential storage lets higher-level tools choose how network presence participates in an unlocking policy.

**Entry points:** The repository's Tang protocol section and `src/tangd.c`. The design's trust assumptions about advertisements, network reachability, and client metadata differ from per-user authorization in a conventional vault.

### 23. [latchset/clevis](https://github.com/latchset/clevis)

**Language / role:** Shell and C; composable automated decryption and unlocking policies, including network and TPM bindings.

Clevis is the client-policy counterpart to systems such as Tang, but it is independently substantive: it composes bindings and integrates recovery into higher-level unlocking workflows. Tang and Clevis therefore represent different protocol responsibilities rather than duplicate implementations.

- **C1:** Threshold bindings make failure policy part of key protection. A threshold of one can allow recovery through any one available binding; higher thresholds require multiple successful components. The implementation must preserve the distinction between availability redundancy and a requirement for multiple independent factors.
- **C2:** The [Shamir-sharing pin manual](https://raw.githubusercontent.com/latchset/clevis/master/src/pins/sss/clevis-encrypt-sss.1.adoc) describes shares protected through other pins and recursive composition. The [pin source tree](https://github.com/latchset/clevis/tree/master/src/pins) includes distinct network, TPM, and other bindings behind this shared model.

**Entry points:** The `sss` manual and pin implementations. The documented composition makes this useful beyond any single disk-encryption or network-server integration.

## Coverage, search method, and limitations

Discovery used more than six distinct query families, including general secret-server architectures; KMS and envelope-encryption services; AWS-native credential stores; KMIP and OpenStack key management; Git/configuration encryption; Kubernetes secret reconciliation; local password-store design; software PKCS#11 and TPM storage; network-bound recovery; and threshold/FHE KMS implementations. Targeted follow-up searches examined rotation, master-key migration, cache concurrency, format parsing, test architecture, and release histories. Later searches increasingly returned the same projects, thin provider wrappers, unrelated cryptographic libraries, or forks without distinct implementation evidence.

Every retained canonical GitHub repository page was opened, and every entry has at least one separately opened primary implementation, design, API, test, or history source. Linked entry points are the material actually inspected; raw source links are used where GitHub's HTML file viewer was unreliable. Redirects were resolved for Sealed Secrets and SoftHSM. Barbican is explicitly labeled an official mirror. OpenBao's distinct evolution is documented; the report does not treat arbitrary forks as independent projects. Each monorepo is counted once.

The selection excludes secret scanners, awesome lists, tutorials, generated SDKs, crypto-primitive-only libraries, and projects whose relevant source no longer has a substantive official GitHub home. Local databases and secret-distribution controllers are included only where their storage, cryptographic, or lifecycle machinery materially fits the category. KES and Confidant are historical archived selections, and PyKMIP's server has a testing/development scope. The absence of an archive label on other entries is not a promise of ongoing maintenance.

Criteria judgments are grounded engineering assessments of the cited material. Documentation and default-branch sources can change; older architectural discussions are qualified where relevant. No candidate code was executed, dependencies installed, secrets accessed, or external services modified. This report does not measure performance, reproduce security tests, or establish cryptographic assurance from documentation alone.
