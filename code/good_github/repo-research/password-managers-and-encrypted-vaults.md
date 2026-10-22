# Password managers and encrypted vaults

Research date: **2026-10-09**

This selection covers personal and team password managers, reusable password-database engines, and encrypted file vaults or containers. It includes desktop, mobile, browser, command-line, server, and filesystem implementations. The 23 repositories were checked against their canonical GitHub pages or public GitHub API metadata, and each has additional primary implementation or design evidence. Criteria describe concrete engineering study opportunities; they are not security certifications or claims that every component is exemplary.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, adversarial input, or failure handling. **C2** — substantial abstractions reused across operations, platforms, or integrations. **C3** — real performance or resource constraints addressed through understandable architecture. **C4** — sustained evolution supported by compatibility work, testing, or complexity management, rather than repository age alone.

## Local password managers

### 1. [keepassxreboot/keepassxc](https://github.com/keepassxreboot/keepassxc)

**C++ / Qt; cross-platform desktop password manager and CLI.** A substantial evolution of the KeePassX lineage, with its own database, browser-integration, sharing, and platform code. Study how a desktop application preserves an interoperable encrypted format while adding new interfaces and operations.

- **C1:** The [KDBX4 reader](https://github.com/keepassxreboot/keepassxc/blob/develop/src/format/Kdbx4Reader.cpp) validates required headers, checks both the header checksum and keyed authentication, and composes authenticated-block, cipher, decompression, and XML-reading stages. Each stage has distinct failure handling; simply decrypting bytes is only part of the correctness problem.
- **C4:** The [changelog](https://github.com/keepassxreboot/keepassxc/blob/develop/CHANGELOG.md) documents evolution across 2019–2026, including merge dry runs, network-share merge behavior, global custom-data merge fixes, browser-key merging, and GUI-test reliability. These are concrete examples of managing compatibility and data-preservation complexity over years.

### 2. [Kunzisoft/KeePassDX](https://github.com/Kunzisoft/KeePassDX)

**Kotlin, Java, and native C; Android password and passkey manager.** Particularly useful for studying portable password databases under mobile memory limits and Android credential-integration requirements.

- **C1:** The [KDF clamping tests](https://github.com/Kunzisoft/KeePassDX/blob/master/database/src/test/java/com/kunzisoft/keepass/tests/crypto/KdfClampingTest.kt) exercise excessive iteration counts, memory, parallelism, and parameters injected as though read from a malicious file. They also check rejection when the available-memory policy cannot satisfy the requested KDF.
- **C2:** The [database model](https://github.com/Kunzisoft/KeePassDX/blob/master/database/src/main/java/com/kunzisoft/keepass/database/element/database/DatabaseKDBX.kt) builds on typed versioned groups and entries, with pluggable KDF selection, composite credentials, hardware challenge-response callbacks, attachment compression, and minimum-format-version determination. This shared database layer supports much more than a single screen or storage operation.

### 3. [strongbox-password-safe/Strongbox](https://github.com/strongbox-password-safe/Strongbox)

**Objective-C and Swift; iOS/macOS client for KeePass and Password Safe formats.** Study a native application that unifies multiple encrypted formats and supports meaningful database comparison and merging. The repository states that functional source is published for inspection, but some nonfunctional assets/build configuration are omitted and contributions are not accepted; it is not a turnkey reproducible-build example.

- **C1:** The [merger](https://github.com/strongbox-password-safe/Strongbox/blob/master/model/Sync/DatabaseMerger.m) performs dry runs against a clone, compares modification timestamps, combines deletion records, and reconciles recycle-bin and entry-template references. These interactions expose the difficulty of preserving both history and user intent during synchronization.
- **C2:** [DatabaseModel](https://github.com/strongbox-password-safe/Strongbox/blob/master/model/DatabaseModel.h) presents a common node hierarchy, metadata, attachment pool, composite-key factors, recycling operations, and cross-serialization identifiers across the supported formats. It is a useful example of application-wide domain abstractions over heterogeneous persistence formats.

### 4. [pwsafe/pwsafe](https://github.com/pwsafe/pwsafe)

**C++; Password Safe desktop application and encrypted database format.** A good counterpoint to KDBX: the persistence design is explicitly documented rather than discoverable only through application code.

- **C1:** The [version 3 format specification](https://github.com/pwsafe/pwsafe/blob/master/docs/formatV3.txt) defines independent encryption and authentication keys, typed records, termination markers, corruption/truncation detection, and serialization rules. Its distinction between mandatory fields and extensible fields makes parser and writer invariants concrete.
- **C4:** The [changelog](https://github.com/pwsafe/pwsafe/blob/master/docs/ChangeLog.txt) records long-running format and application evolution, including preserving unknown header/record fields for future versions and independent clients, changes in build tooling, and platform-specific regression fixes. Study how compatibility promises reach beyond the currently shipping application.

## Reusable password-database engines

### 5. [keeweb/kdbxweb](https://github.com/keeweb/kdbxweb)

**TypeScript; KeePass KDBX3/KDBX4 engine for browsers and Node.js.** This is the underlying database library, not a second listing of the KeeWeb application. The inspected GitHub API metadata reports its latest push in December 2024; no claim of current maintenance is made.

- **C1:** The [merge tests](https://github.com/keeweb/kdbxweb/blob/master/test/format/kdbx.merge.spec.ts) cover deletion records, metadata timestamps, binary attachments, icons, and groups moved into or out of deleted subtrees. The documented merge contract also acknowledges limits of peer-to-peer entry-history merging, which is valuable context when studying synchronization guarantees.
- **C2:** The [library API documentation](https://github.com/keeweb/kdbxweb#usage) exposes credentials, database creation/loading/saving, groups, entries, cleanup, version conversion, and merging. Its injected Argon2 implementation lets a common format engine accommodate different browser and server execution environments.

### 6. [sseemayer/keepass-rs](https://github.com/sseemayer/keepass-rs)

**Rust; reusable KDB/KDBX parser with experimental KDBX4.1 writing.** Useful for studying an independent implementation rather than a language binding to the desktop application. Preserve the upstream qualification that writing is experimental.

- **C1:** The [KeePassXC writer-compatibility tests](https://github.com/sseemayer/keepass-rs/blob/master/tests/keepassxc_writer_compat_tests.rs) demonstrate why self-round-trip tests are insufficient: a permissive reader can hide an incorrect writer. They check literal XML representations of nullable booleans and integer-valued fields that another implementation rejects when serialized incorrectly.
- **C2:** The crate exposes a database/credential API used by its optional CLI utilities, while its [authenticated block-stream layer](https://github.com/sseemayer/keepass-rs/blob/master/src/format/hmac_block_stream.rs) separates framing, per-block key derivation, authentication, and structured errors from the higher-level database model. It is a focused study of reusable format machinery.

## Synchronized and team password vaults

### 7. [bitwarden/clients](https://github.com/bitwarden/clients)

**Primarily TypeScript; monorepo for web, browser-extension, desktop, and CLI clients.** Counted once; mobile clients are separate repositories and are not included here. The relevant subsystem is shared client state, vault data, and synchronization.

- **C1:** The [state-management design history](https://contributing.bitwarden.com/architecture/clients/services/vision/) explains how account switching complicated state routing and how mixing persisted and in-memory account data created a risk of serializing decrypted secrets. This is unusually candid material about correctness pressures in a growing security application.
- **C2:** The [service implementation guide](https://contributing.bitwarden.com/architecture/clients/services/implementation/) distinguishes observable domain reads, internal cache updates, and server-backed writes. It explains why a live-sync notification must update local state without repeating the originating server mutation. The documentation describes an ongoing migration, not a uniformly completed architecture.

### 8. [bitwarden/server](https://github.com/bitwarden/server)

**C# / ASP.NET Core and SQL; official password-manager backend.** The focus here is the password-vault authorization and service infrastructure, not every product in this broader repository. Compare it with the independent Vaultwarden implementation below.

- **C1:** The [organization cipher authorization handler](https://github.com/bitwarden/server/blob/main/src/Core/Vault/Authorization/Ciphers/CipherOrganizationAuthorizationHandler.cs) ties organization-wide operations to the authenticated principal, organization role, delegated collection permissions, and provider membership. It provides a concrete starting point for tracing tenant boundaries and the distinction between organization-wide and collection-specific access.
- **C2:** The [server architecture documentation](https://contributing.bitwarden.com/architecture/server/) describes command/query separation and separate API-contract versus internal-data models. These abstractions support multiple clients and make persistence changes independent of public request/response shapes; the surrounding source separates API, identity, notifications, and database implementations.

### 9. [dani-garcia/vaultwarden](https://github.com/dani-garcia/vaultwarden)

**Rust; unofficial, independent Bitwarden-compatible server.** A substantial API implementation, not a fork of Bitwarden's C# backend. Study protocol compatibility and asynchronous server design with several SQL backends.

- **C1:** The [cipher API](https://github.com/dani-garcia/vaultwarden/blob/main/src/api/core/ciphers.rs) checks ownership/access and uses the client's last-known revision to reject stale updates. It deliberately accepts absence of that field for older clients, illustrating the tension between stronger concurrency checks and backward compatibility.
- **C2:** The [database layer](https://github.com/dani-garcia/vaultwarden/blob/main/src/db/mod.rs) exposes common connection/pool abstractions over SQLite, MySQL, and PostgreSQL. It coordinates semaphore permits, pooled synchronous Diesel connections, asynchronous callers, and blocking-task execution—including drop behavior—behind interfaces used across API operations.

### 10. [passbolt/passbolt_api](https://github.com/passbolt/passbolt_api)

**PHP / CakePHP; Passbolt Community Edition team-password API.** A strong study target for the server half of client-encrypted sharing, where access metadata and encrypted copies must remain consistent even though the server does not decrypt the secret.

- **C1:** [ResourcesShareService](https://github.com/passbolt/passbolt_api/blob/master/src/Service/Resources/ResourcesShareService.php) applies permission changes and secret changes in a database transaction, handles grant/revoke consequences, and dispatches its sharing event afterward. Trace failures here to understand why granting access is not merely inserting an ACL row.
- **C2:** The [service tree](https://github.com/passbolt/passbolt_api/tree/master/src/Service) separates permission calculation, secret updates, resource operations, user/group management, and OpenPGP concerns. The sharing implementation composes these services through a change-set object, providing reusable business operations rather than duplicating sharing rules in controllers.

### 11. [psono/psono-client](https://github.com/psono/psono-client)

**TypeScript/JavaScript; Psono browser and web client. Official GitHub mirror.** The repository explicitly names GitLab as the canonical development host, but retains substantial implementation and tests on GitHub. Study the client-side hierarchy of encrypted objects and shared access.

- **C1:** The [entity-model specification](https://doc.psono.com/admin/development/entity-model.html) distinguishes datastores, secrets, shares, direct permissions, and inherited permissions. Child keys live inside encrypted parent objects; removing a share link is different from deleting the underlying share. These distinctions create nontrivial confidentiality and authorization invariants.
- **C2:** The [crypto service](https://github.com/psono/psono-client/blob/master/src/js/services/crypto-library.ts) centralizes password-derived authentication, symmetric and public-key encryption, file operations delegated to workers, recovery-code checks, and signing-related utilities. The same service boundary supports multiple client targets and object types.

### 12. [padloc/padloc](https://github.com/padloc/padloc)

**TypeScript; monorepo containing a shared core, server, web UI, and platform clients.** Useful for following one vault domain model across personal and organizational use. The security whitepaper has unfinished sections; use its concrete protocol descriptions without treating it as a complete threat analysis.

- **C1:** The [security whitepaper](https://github.com/padloc/padloc/blob/main/security.md) describes per-accessor wrapping of a shared vault key, account private-key protection, and public-key/identity verification before encrypting a shared vault. Group membership and vault membership jointly determine recipients, making membership changes a cryptographic concern.
- **C2:** The same design builds vaults from reusable symmetric, password-based, and shared-key containers. The [package organization](https://github.com/padloc/padloc/tree/main/packages) separates this core from UI, server, PWA, extension, and native packaging, making it possible to study how domain and cryptographic logic are shared across products.

### 13. [AliasVault/AliasVault](https://github.com/AliasVault/AliasVault)

**Rust, TypeScript, C#, Swift, and Kotlin; password/passkey vault with email-alias support.** Counted as one monorepo, focusing on vault encryption and the shared core. Email ingress is a separate trust boundary: the server receives email before encrypting it for storage.

- **C1:** The [architecture document](https://github.com/AliasVault/AliasVault/blob/main/ARCHITECTURE.md) details password-derived vault encryption, SRP authentication, passkey serialization, and a mobile-to-browser unlock exchange with one-time retrieval and expiration. Study the distinction between authenticating a session and transferring the vault-decryption capability.
- **C2:** The [core-library guide](https://github.com/AliasVault/AliasVault/blob/main/core/README.md) identifies a Rust core exposed through WebAssembly and mobile bindings, platform-neutral TypeScript API/sync/SQLite logic, generated cross-language models, and a common vault schema. This is a concrete design for sharing behavior and data contracts across several runtimes.

## Command-line stores and native integrations

### 14. [gopasspw/gopass](https://github.com/gopasspw/gopass)

**Go; command-line password manager with mounted stores and configurable encryption/storage backends.** Study how a filesystem-oriented password store grows into a team tool while retaining scriptability.

- **C2:** The [architecture guide](https://github.com/gopasspw/gopass/blob/master/ARCHITECTURE.md) explains root/leaf store composition, mount-prefix translation, backend registries and loader priorities, and a deliberate public API boundary under `pkg/`. Crypto and storage implementations can vary between stores within one namespace.
- **C4:** The [changelog](https://github.com/gopasspw/gopass/blob/master/CHANGELOG.md) spans releases from 2017 through 2026, while the architecture guide explains accumulated compatibility work: fallback configuration parsers, preventing consumers from importing unstable internals, merging storage/revision-control abstractions, and executable-level integration tests. These are documented responses to evolution, not merely an old repository date.

### 15. [IJHack/QtPass](https://github.com/IJHack/QtPass)

**C++ / Qt; native GUI for pass-style encrypted stores.** More substantial than a generated command wrapper: it owns store navigation, recipients, process coordination, settings, and alternative execution backends.

- **C1:** The [path validator](https://github.com/IJHack/QtPass/blob/main/src/pathvalidator.cpp) checks password-store boundaries for existing and not-yet-existing files. It resolves symlinks through the nearest existing ancestor before rebuilding the remaining path and uses a separator-aware root-prefix check—an instructive adversarial-filesystem problem.
- **C2:** The [Pass abstraction](https://github.com/IJHack/QtPass/blob/main/src/pass.h) supports interchangeable real-pass and direct GPG/Git implementations and exposes shared store, recipient, and process operations to the GUI. The factory and transaction code provide useful follow-on reading about backend lifecycle and grouping subprocess completion into user operations.

### 16. [doy/rbw](https://github.com/doy/rbw)

**Rust; independent Bitwarden CLI with a background unlocking agent.** The maintainer describes it as feature-complete for their needs, with regression fixes and contributed features still considered. Its agent architecture distinguishes it from a stateless API wrapper.

- **C1:** The [agent loop](https://github.com/doy/rbw/blob/main/src/bin/rbw-agent/agent.rs) combines Unix-socket requests, lock timeouts, periodic synchronization, and server notifications. Requests run concurrently while shared state is protected by an asynchronous mutex; logout notifications must clear the same state that requests use.
- **C4:** The [2020–2025 changelog](https://github.com/doy/rbw/blob/main/CHANGELOG.md) tracks compatibility with changing Bitwarden API validation, prelogin endpoints, per-item encryption keys, and client/agent versions. It also records lock-timeout regressions and fallback behavior when page locking is unavailable. This makes protocol evolution and secret-lifetime maintenance visible across several years.

## Encrypted file vaults and containers

### 17. [cryptomator/cryptofs](https://github.com/cryptomator/cryptofs)

**Java; Cryptomator's encrypted `java.nio.file` filesystem provider.** Selected as the reusable vault engine rather than separately counting the desktop frontend. Study how encryption is integrated into familiar filesystem semantics.

- **C1:** [MoveOperation](https://github.com/cryptomator/cryptofs/blob/develop/src/main/java/org/cryptomator/cryptofs/MoveOperation.java) distinguishes same-filesystem and cross-filesystem moves, rejects unsupported atomic moves, handles nonempty directories, and attempts cleanup of partially copied targets. The original is deleted only after a successful copy.
- **C2:** [CryptoFileSystemProvider](https://github.com/cryptomator/cryptofs/blob/develop/src/main/java/org/cryptomator/cryptofs/CryptoFileSystemProvider.java) implements the standard Java filesystem-provider abstraction, including paths, streams, channels, attributes, and vault initialization. Existing NIO-based applications can therefore operate on encrypted vaults through a broad, established interface.

### 18. [rfjakob/gocryptfs](https://github.com/rfjakob/gocryptfs)

**Go; encrypted FUSE overlay filesystem.** A particularly accessible implementation for studying per-file cloud-friendly encryption and the compatibility surface exposed to mounting tools.

- **C1:** The [forward-mode cryptographic design](https://nuetzlich.net/gocryptfs/forward_mode_crypto/) binds authenticated blocks to both file identity and block number, uses fresh IVs for modifications, and treats sparse blocks and long encrypted filenames separately. These choices show how cryptographic invariants interact with ordinary filesystem operations.
- **C4:** The repository's README release history records format-feature compatibility over multiple years, including the introduction of reverse mode and later cipher/name options. The [stable CLI ABI](https://github.com/rfjakob/gocryptfs/blob/master/Documentation/CLI_ABI.md) specifies password-input framing, option termination, and error codes; the repository states that this interface is regression-tested. This makes compatibility observable to downstream applications, not just to file-format readers.

### 19. [netheril96/securefs](https://github.com/netheril96/securefs)

**C++; encrypted userspace filesystem with full and lite formats.** An unusually explicit comparison of confidentiality, directory lookup, random access, and portability tradeoffs within one codebase.

- **C1:** The [design document](https://github.com/netheril96/securefs/blob/master/docs/design.md) explains per-file key separation and authenticated block positions, and candidly identifies the lite format's inability to detect replay of an older valid block at the same position. That limitation matters when distinguishing authentication from freshness.
- **C3:** The same design explains why whole-file authentication would be expensive for large random-access files, why randomized filename lookup needs a B-tree in full format, and why lite format chooses deterministic authenticated names. The [implementation tree](https://github.com/netheril96/securefs/tree/master/sources) is a starting point for tracing those format-specific tradeoffs into code. No numerical throughput claim is needed to establish the performance constraints.

### 20. [cryfs/cryfs](https://github.com/cryfs/cryfs)

**Rust rewrite plus historical C++; encrypted cloud filesystem that also obscures file sizes and directory structure.** The inspected default branch is **CryFS 2.0 alpha**, explicitly unsuitable for important data. The repository points users to the stable 1.0 series and preserves older C++ code under `old-cpp`; the rewrite and stable implementation must not be conflated.

- **C1:** The Rust [concurrent store](https://github.com/cryfs/cryfs/blob/main/crates/concurrent-store/src/store.rs) coalesces simultaneous loads of an object, shares the loaded reference, asynchronously drops it after the final reference, and makes new loads wait for an in-progress drop. It exposes a concrete object-lifecycle concurrency problem beneath filesystem operations.
- **C2:** The [block-store interface](https://github.com/cryfs/cryfs/blob/main/crates/blockstore/src/lib.rs) composes encrypted, integrity-checking, compressed, on-disk, in-memory, read-only, and test stores. This layered storage architecture is worth studying independently of the alpha frontend's readiness.

### 21. [veracrypt/VeraCrypt](https://github.com/veracrypt/VeraCrypt)

**C, C++, and assembly; encrypted file containers and volumes.** Included for the file-container/vault subsystem, although the repository also implements whole-disk and boot encryption. This is a substantive independent evolution of TrueCrypt, not an unchanged archival fork.

- **C1:** The [encryption-scheme documentation](https://github.com/veracrypt/VeraCrypt/blob/master/doc/html/en/Encryption%20Scheme.html) describes standard versus hidden header discovery, derivation and validation of candidate header keys, and the separation between header keys and volume master keys. Password changes re-encrypt the header rather than all sectors. Study these format/lifecycle rules without assuming sector encryption also provides authenticated data storage.
- **C3:** The [parallelization design](https://github.com/veracrypt/VeraCrypt/blob/master/doc/html/en/Parallelization.html) describes splitting encryption/decryption work among processors and parallelizing header-key derivation. It gives a clear route into performance-sensitive block processing; its illustrative scaling claims are not treated here as measured universal speedups.

### 22. [dyne/Tomb](https://github.com/dyne/Tomb)

**Zsh; orchestration of LUKS/dm-crypt encrypted file containers.** A useful example of security-sensitive systems programming in shell. It delegates cryptographic primitives to established tools but owns consequential volume, key, mount, and process lifecycle logic.

- **C1:** The [main implementation](https://github.com/dyne/Tomb/blob/master/tomb) contains explicit input-file validation, signal/exit cleanup, key delivery to cryptsetup through standard input, and mount/close handling. Correctness depends on shell quoting, partial failure, external-tool behavior, and preventing conflicting use of the same container.
- **C4:** The [changelog](https://github.com/dyne/Tomb/blob/master/ChangeLog.md) documents 2017–2025 regression work: testing old stable versions, moving tests to sharness, util-linux and cryptsetup compatibility, loop-device cleanup, double-mount prevention, and password-prompt fixes. It is strong evidence of sustained maintenance of a deliberately small architecture.

### 23. [Picocrypt/Picocrypt](https://github.com/Picocrypt/Picocrypt)

**Go; compact encrypted file/volume application. Archived historical project.** The repository explicitly says development is permanently frozen; a community successor is not counted as another implementation here. Study the original as a bounded design, not as an actively maintained deployment recommendation.

- **C1:** The [internals document](https://github.com/Picocrypt/Picocrypt/blob/main/Internals.md) specifies authenticated encryption components, nonce renewal before stream-counter limits, ordered versus unordered keyfile handling, and Reed–Solomon header/data encoding. The final padded-block ambiguity receives an explicit format flag—an excellent small example of edge cases shaping a storage format.
- **C4:** The [2022–2025 changelog](https://github.com/Picocrypt/Picocrypt/blob/main/Changelog.md) records chunked keyfile hashing, cancellation and disk-space handling, race-related fixes, overwrite prevention, and later protection of temporary archives and incomplete outputs. These changes demonstrate evolution around failure modes and data handling despite the project's eventual archive status.

## Coverage, search method, and limitations

Discovery used more than six distinct live search formulations: broad password-manager architecture; pass/GPG/Git stores; team end-to-end encrypted sharing; Android/iOS KeePass clients; Rust and age-based vaults; encrypted FUSE/cloud filesystems; Bitwarden-compatible implementations; encrypted containers; cross-language vault cores; and lesser-known offline projects. Targeted searches then located official design documents, protocol descriptions, tests, and changelogs. Later broad searches for less familiar languages and vault designs mostly returned small personal projects, course prototypes, generic encryption tools, or general secrets infrastructure, providing diminishing returns for this selection.

Canonical URLs and branches were checked using public GitHub pages or API metadata. Primary source files were read directly from GitHub's public source hosting; documentation was opened on official project sites. GitHub API rate limiting was worked around with ordinary public repository pages and raw source files. No candidate code was executed, dependencies installed, or large repositories cloned.

The list favors distinct engineering boundaries: application-level merging, reusable format engines, shared-vault authorization, command/agent interfaces, encrypted filesystem semantics, and container lifecycle. It does not duplicate every frontend of a selected project. KeeWeb's database engine is retained instead of also counting its application; CryptoFS represents Cryptomator's core; each listed monorepo counts once. Psono's substantive official GitHub mirror is labeled. Picocrypt's archive, CryFS's alpha rewrite, keepass-rs's experimental writer, and Strongbox's build-source limitations are explicit.

Excluded classes include awesome-lists, packaging-only repositories, deployment recipes, thin API wrappers, course/tutorial vaults, password generators without a vault, general cryptographic libraries, and infrastructure secret-management platforms whose central abstraction is machine/service credentials rather than these user-facing vaults. This is selective coverage, not an exhaustive product census. Criterion assignments are engineering judgments grounded in the linked material; source inspection establishes what is interesting to study, not a comprehensive audit or a guarantee of security, performance, or future maintenance.
