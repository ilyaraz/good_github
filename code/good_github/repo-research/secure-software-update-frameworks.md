# Secure software update frameworks

Research date: **2026-10-09**.

This report selects 22 GitHub repositories for studying authenticated update distribution, trusted metadata, installation failure recovery, and update lifecycle design. It spans reusable protocol implementations, repository publishers, operating-system and firmware installers, bootloaders, and application updaters. These occupy different trust boundaries: an authenticated download, protection against stale metadata, and recovery after a failed installation are separate properties. Inclusion is an engineering study recommendation, not a security audit or a claim that every project supplies all three.

Criteria used below:

- **C1 — Difficult correctness:** security invariants, adversarial input, concurrency, or failure recovery materially shape the implementation.
- **C2 — Reusable abstractions:** substantial interfaces or components support multiple applications, deployment policies, or platforms.
- **C3 — Performance with structure:** concrete bandwidth, storage, memory, flash, or latency constraints receive architectural treatment.
- **C4 — Sustained evolution:** primary history shows years of development together with compatibility, testing, or complexity management.

Each linked repository heading identifies a separately verified GitHub repository. The following links are the most useful documentation or implementation entry points inspected for that selection. Criteria are evidence-based assessments; they are not claims made by a certification authority.

## Trusted metadata and distribution protocols

### 1. [theupdateframework/python-tuf](https://github.com/theupdateframework/python-tuf)

**Language/role:** Python; TUF metadata APIs and client implementation.

Study how a client progresses from a bootstrap trust anchor through root, timestamp, snapshot, and targets metadata without conflating downloaded objects with trusted state. **C1:** the updater verifies metadata during refresh, retrieves delegated metadata as needed, and verifies target files. Its cache contract is also explicit: simultaneous updater instances sharing a cache are unsupported, an important application-level concurrency constraint. **C2:** metadata manipulation, client orchestration, and the replaceable network fetcher interface are separated, allowing applications to reuse protocol logic with their own transport. The repository also exposes repository-building support, but labels that library API unstable; stability should be assessed per component. See the [repository's component overview](https://github.com/theupdateframework/python-tuf) and [Updater API and cache rules](https://theupdateframework.readthedocs.io/en/latest/api/tuf.ngclient.updater.html).

**Start with:** the [client API index](https://theupdateframework.readthedocs.io/en/latest/api/tuf.ngclient.html) and the Updater documentation above.

### 2. [theupdateframework/go-tuf](https://github.com/theupdateframework/go-tuf)

**Language/role:** Go; TUF metadata, verification state machine, and updater libraries.

The useful distinction here is between individual metadata objects and the state machine that can accept them. **C1:** `TrustedMetadata` requires sequential root versions, verifies a new root using both previously trusted authority and its own signing policy, and constrains when other metadata can enter trusted state. Its implementation documents that concurrent use requires external synchronization. **C2:** the v2 architecture separates metadata, trusted state, fetching, configuration, and update orchestration; applications can work at the appropriate level instead of embedding the entire updater. The repository explains the v2 redesign and deprecation of the legacy implementation, making it useful for studying how security-sensitive interfaces are simplified. Sources: [architecture overview](https://github.com/theupdateframework/go-tuf) and [trusted-metadata implementation](https://raw.githubusercontent.com/theupdateframework/go-tuf/master/metadata/trustedmetadata/trustedmetadata.go).

**Start with:** the [trustedmetadata source and tests directory](https://github.com/theupdateframework/go-tuf/tree/master/metadata/trustedmetadata).

### 3. [theupdateframework/rust-tuf](https://github.com/theupdateframework/rust-tuf)

**Language/role:** Rust; generic TUF client, trust database, and repository interfaces. **Status:** the README calls this beta and warns that APIs can change even in patch releases.

Study the type boundary between received metadata and verified metadata. **C1:** the database stores `Verified` metadata, supports bootstrap from pinned keys with a threshold, and distinguishes that path from accepting an already trusted root. This exposes the security significance of constructors rather than hiding trust establishment in deserialization. **C2:** asynchronous `RepositoryProvider` and `RepositoryStorage` traits separate retrieval from publication, while a format parameter supports different serialization implementations. The client retains responsibility for length and hash verification even when a backend does not perform early rejection. These are substantial implementation choices, independent of the other Rust implementation below. Sources and entry points: [trust database](https://raw.githubusercontent.com/theupdateframework/rust-tuf/develop/tuf/src/database.rs) and [repository traits](https://raw.githubusercontent.com/theupdateframework/rust-tuf/develop/tuf/src/repository.rs).

### 4. [awslabs/tough](https://github.com/awslabs/tough)

**Language/role:** Rust; TUF client and repository tooling, including the `tuftool` CLI and cloud key integrations.

**C1:** bounded metadata downloads, safe target paths, and expiration enforcement expose concrete defenses around untrusted repository data. An especially useful correctness case is the project's April 2026 advisory: delegated metadata lacked required expiration, length, and hash validation in affected versions; the documented fixes are tough 0.22.0 and tuftool 0.15.0. This is a reason to study the corrected trust path and regression boundary, not evidence that earlier releases were safe. **C2:** transport, key-source/signing, loading, and repository-editing interfaces let the same implementation support filesystem repositories, network clients, and publishing tools. See the [API architecture](https://docs.rs/tough/latest/tough/) and [delegated-metadata security advisory](https://github.com/awslabs/tough/security/advisories/GHSA-4v58-8p28-2rq3).

**Start with:** those two sources. Some API overview prose about delegation support appears out of step with the advisory; use version-specific implementation and advisory information for that feature.

### 5. [theupdateframework/tuf-js](https://github.com/theupdateframework/tuf-js)

**Language/role:** TypeScript; TUF client and related packages for JavaScript applications.

**C1:** the updater explicitly sequences root, timestamp, snapshot, and targets refreshes, advances roots incrementally, and verifies a downloaded target before copying the temporary file to its destination. The cached-metadata path handles verification failures rather than equating cache presence with validity. **C2:** the monorepo separates canonical JSON, metadata models, the client, CLI, and repository mocks. Within the client, fetching and trusted-metadata storage remain distinct from update orchestration, supporting both embedding and testing. Study how a familiar asynchronous application language expresses the same trust transitions as the Python, Go, and Rust implementations. Sources and entry points: [package boundaries](https://github.com/theupdateframework/tuf-js/tree/main/packages) and [updater implementation](https://raw.githubusercontent.com/theupdateframework/tuf-js/main/packages/client/src/updater.ts).

## Secure repository publication and multi-device coordination

### 6. [theupdateframework/tuf-on-ci](https://github.com/theupdateframework/tuf-on-ci)

**Language/role:** Python and CI workflows; TUF repository maintenance with offline signers and automated online roles.

This is a substantive publishing system for repositories with low or moderate change frequency. **C1:** signing events track required signatures before publication; changing a signer requires both the new signer's participation and authorization through the delegating role. Offline ownership and online timestamp/snapshot signing are distinct responsibilities. **C2:** reusable workflows, local signing tools, configurable publication destinations, and multiple online signing integrations separate repository policy from the CI provider's routine execution. Engineers can study how human authorization becomes a machine-checkable publication state rather than relying on a successful build alone. See the [project scope](https://github.com/theupdateframework/tuf-on-ci/) and [repository maintenance workflow](https://github.com/theupdateframework/tuf-on-ci/blob/main/docs/REPOSITORY-MAINTENANCE.md).

**Start with:** the maintenance guide's signing-event, signer-change, online-key, and publication sections.

### 7. [repository-service-tuf/repository-service-tuf-worker](https://github.com/repository-service-tuf/repository-service-tuf-worker)

**Language/role:** Python/Celery; repository publication service worker. **Status:** the repository labels the project experimental.

The worker adds substantial database, queue, and publication orchestration around TUF. **C1:** partially signed bootstrap roots remain pending until their threshold is satisfied. Artifact publication is serialized under a lock while SQL state becomes targets metadata, then snapshot and timestamp metadata, preventing independent workers from publishing inconsistent intermediate states. **C2:** task execution, signing, storage, persistent settings, and scheduled metadata renewal have separate responsibilities. **C3:** concurrent artifact intake and database work are separated from the consistency-critical publication step; hashed-bin metadata organizes larger target sets. This is an instructive throughput-versus-consistency design, without a measured throughput claim here. Sources: [repository and status](https://github.com/repository-service-tuf/repository-service-tuf-worker) and [worker development architecture](https://repository-service-tuf.readthedocs.io/projects/rstuf-worker/en/latest/devel/).

**Start with:** the architecture's bootstrap, artifact mutation, and `publish_artifacts` task descriptions.

### 8. [uptane/aktualizr](https://github.com/uptane/aktualizr)

**Language/role:** C++; Uptane client library and service coordinating Primary and Secondary devices.

**C1:** documented fixes address failed Secondary verification, installation reporting across unexpected shutdowns, and completing an already initiated update after metadata expiry. These are concrete distributed-update failure boundaries. **C2:** `libaktualizr`, Primary/Secondary communication, and pluggable package managers separate orchestration from installation mechanisms. **C4:** the inspected 2018–2020 changelog records API changes, testing work, removal of unfinished implementations, and an explicit Secondary protocol migration: update the backward-compatible Primary before its Secondaries. That is meaningful compatibility management across devices, rather than merely an old creation date. Sources: [library and integration overview](https://github.com/uptane/aktualizr) and [release history](https://github.com/uptane/aktualizr/blob/master/CHANGELOG.md).

**Start with:** that changelog's 2020.8 protocol migration and 2020.4–2020.5 failure-handling changes. The historical documentation is valuable; this research did not establish a current release cadence.

## Embedded Linux, operating systems, and device firmware

### 9. [rauc/rauc](https://github.com/rauc/rauc)

**Language/role:** C; signed bundle installation for embedded Linux.

**C1:** RAUC's slot model groups related partitions, selects an inactive installation group, and coordinates bootability with the bootloader. Marking a successful boot and arranging watchdog/fallback behavior remain explicit integration responsibilities. This is useful for studying the boundary between installer guarantees and board policy. **C2:** slot types, parent-child groups, bootloader interfaces, and image handlers support varied storage layouts without replacing the installation engine. **C3:** streaming and skipping already matching read-only images reduce transfer or write work; the documentation explains why checksum-based skipping is unsuitable as proof that a writable image remains unmodified. Signed bundles provide the authentication layer. Sources: [repository overview](https://github.com/rauc/rauc) and [slot, boot, and update design](https://rauc.readthedocs.io/en/latest/basic.html).

**Start with:** the basic design guide's slot-selection, boot-confirmation, and redundant-update sections.

### 10. [sbabic/swupdate](https://github.com/sbabic/swupdate)

**Language/role:** C, with Lua integration; configurable embedded software-update engine.

**C1:** the signed-image design discusses two distinct traps: authenticating an entire streamed archive only after writes have occurred, and independently signing subimages without binding them into one release. Its signed `sw-description` binds each component's hash to the selected update. In builds enabling `CONFIG_SIGNED_IMAGES`, required signature and hash checks cannot simply be disabled at runtime. **C2:** storage handlers and scripting support heterogeneous installations, while cryptographic providers and services separate verification, hashing, and decryption from particular algorithm implementations. The study value is the interaction between stream processing, release-level authenticity, and installer extensibility. Sources: [framework overview](https://github.com/sbabic/swupdate) and [signed-image design and configuration](https://sbabic.github.io/swupdate/signed_images.html).

**Start with:** the signed-image guide. These authentication guarantees depend on building and configuring the signed-image mode.

### 11. [mendersoftware/mender](https://github.com/mendersoftware/mender)

**Language/role:** C++ in the current client; device-side update orchestration, distinct from Mender's server and commercial services.

**C1:** the state-script model makes reboot, commit, rollback, and failure states explicit, including which scripts may repeat after power loss and when rollback is no longer possible. Correct integrations require idempotent hooks. Artifact authentication is separately enabled using `ArtifactVerifyKey` or `ArtifactVerifyKeys`; configured clients reject unsigned artifacts, and multiple keys support rotation. **C2:** update modules and lifecycle hooks support application payloads and root-filesystem updates while retaining a common orchestration model. Study the interaction between the client's persisted state machine and application-provided scripts, especially where scripts assume responsibility for reversibility. Sources and entry points: [state-script execution and failure semantics](https://docs.mender.io/artifact-creation/state-scripts) and [artifact signature verification](https://docs.mender.io/artifact-creation/sign-and-verify).

Do not infer that every feature of the wider hosted product is implemented in this client repository.

### 12. [fwup-home/fwup](https://github.com/fwup-home/fwup)

**Language/role:** C; streaming firmware image construction and installation using a constrained configuration/task language.

**C1:** signed metadata can be authenticated before update operations, while resources are verified during streaming. Installation ordering matters: the configuration must arrange switching to the new filesystem after its data is written. Public-key verification must be enabled; an unsigned-use configuration is not an authenticated updater. **C2:** resource declarations and tasks express partition, filesystem, and boot-environment operations across different embedded layouts. **C3:** the implementation explicitly addresses one-pass processing, block caching, sparse resources, and minimizing writes. Release notes document configurable cache behavior to avoid delta-window thrashing and fixes for repeated block decryption, giving concrete optimization history rather than a generic speed claim. Sources: [configuration, verification, and streaming design](https://github.com/fwup-home/fwup) and [release notes](https://github.com/fwup-home/fwup/releases).

**Start with:** the README's update/task examples and the release notes' cache, delta, and write-path changes.

### 13. [ostreedev/ostree](https://github.com/ostreedev/ostree)

**Language/role:** C; content-addressed filesystem replication and operating-system deployment library.

OSTree belongs here as an authenticated OS-update building block, rather than a complete equivalent of TUF. **C1:** the project supports GPG-verified replication; its deployment design also addresses changes to `/etc` between preparing an update and rebooting by deferring the configuration merge and bootloader work in staged deployments. Mutable `/var` remains a separate application-state responsibility. **C2:** a reusable library separates content objects, trees, and deployment management, supporting higher-level OS and application distribution systems. **C3:** hardlink-based sharing and content addressing reduce duplication across filesystem trees while preserving a comprehensible object model. Sources: [repository overview](https://github.com/ostreedev/ostree), [object and library introduction](https://ostreedev.github.io/ostree/introduction/), and [deployment design](https://ostreedev.github.io/ostree/deployment/).

**Start with:** the introduction and deployment guide. Signed replication alone should not be read as a claim of TUF-style protection against every stale-metadata or key-compromise scenario.

### 14. [fwupd/fwupd](https://github.com/fwupd/fwupd)

**Language/role:** C/GObject; host service and plugin framework for updating device firmware.

**C1:** the security model separates the privileged daemon from network access, authenticates update metadata/content, uses file descriptors rather than untrusted filesystem paths across boundaries, and applies authorization policy to installation. Device-enforced firmware signatures form an additional, device-dependent trust layer. **C2:** plugins implement discovery and device-specific operations within a shared lifecycle: preparation, detachment, writing, reattachment, and reload. The tutorial explains reattachment after failure and cases where a device changes plugins after reboot, exposing complexity beyond simply calling a flash writer. Study how transport, authorization, device identity, and lifecycle recovery are kept distinct. Sources and entry points: [security and privilege model](https://github.com/fwupd/fwupd/blob/main/SECURITY.md) and [plugin lifecycle tutorial](https://fwupd.github.io/libfwupdplugin/tutorial.html).

The framework coordinates heterogeneous hardware; its guarantees necessarily depend on each device's update and signature capabilities.

## Microcontroller boot and constrained-device update protocols

### 15. [mcu-tools/mcuboot](https://github.com/mcu-tools/mcuboot)

**Language/role:** C core with supporting tooling; secure boot and firmware image replacement for microcontrollers.

**C1:** signed image formats, persistent swap state, and test/confirm/revert behavior address both malicious images and resets during installation. The design makes flash layout and boot-state transitions central to correctness. **C2:** reusable `bootutil` logic is separated from platform-specific boot applications and flash access, supporting ports and unit testing without reimplementing the entire update algorithm. **C3:** alternative swap strategies trade scratch space, sector-layout restrictions, erase operations, and wear. The documentation derives flash endurance implications rather than presenting update speed as a single universal number. Engineers can study how persistent metadata encodes recoverable progress when ordinary filesystem transactions are unavailable. Sources: [repository overview](https://github.com/mcu-tools/mcuboot) and [image, swap, and boot design](https://docs.mcuboot.com/design.html).

**Start with:** the design document's image format, swap status, and swap-strategy comparisons.

### 16. [wolfSSL/wolfBoot](https://github.com/wolfSSL/wolfBoot)

**Language/role:** C; portable secure bootloader using wolfCrypt, with firmware signing tools and application-facing update APIs.

**C1:** ordinary firmware updates validate a secondary-slot image, swap it into the boot slot, and mark it for testing. An application confirms success through `wolfBoot_success()`; otherwise a subsequent boot can restore the backup. Persistent progress permits interrupted ordinary image swaps to resume. **C2:** the hardware abstraction layer and application update/confirmation interface separate board integration from the core lifecycle. A particularly important boundary is documented explicitly: **bootloader self-update erases and rewrites the bootloader in place and is not power-fail safe**, unlike the recoverable application-image path. Sources: [architecture overview](https://github.com/wolfSSL/wolfBoot) and [firmware update and self-update design](https://raw.githubusercontent.com/wolfSSL/wolfBoot/master/docs/firmware_update.md).

**Start with:** the update design, comparing normal firmware updates, confirmation, and bootloader self-update rather than generalizing one path's recovery properties to all operations.

### 17. [RIOT-OS/RIOT](https://github.com/RIOT-OS/RIOT)

**Language/role:** C; the **SUIT subsystem** within the RIOT operating-system monorepo, counted once. **Status:** its API documentation explicitly labels the implementation experimental and based on SUIT draft 09.

**C1:** the manifest state model distinguishes authenticating a COSE payload from authenticating the manifest digest, and distinguishes fetched, verified, installed, and finalized component states. Errors cover stale sequence numbers, malformed CBOR, signature/digest failures, policy failures, and storage exhaustion. These distinctions are useful when data may be written before all final conditions are satisfied. **C2:** transport, worker, policy, and storage modules separate update processing from particular network and device arrangements, including CoAP and VFS-related support. Study this as a constrained-device protocol implementation, without assuming conformance to a later SUIT specification. Sources: [repository context](https://github.com/RIOT-OS/RIOT) and [SUIT API, states, errors, and module architecture](https://api.riot-os.org/group__sys__suit.html).

**Start with:** the SUIT API's manifest state definitions and linked storage/transport modules.

## Desktop and mobile application updaters

### 18. [sparkle-project/Sparkle](https://github.com/sparkle-project/Sparkle)

**Language/role:** Objective-C with Swift-facing integration; macOS application updates.

**C1:** archive signatures and Apple code signing support a carefully constrained key-transition policy: regular application updates may change either the EdDSA key or the Apple signing certificate, but not both simultaneously. Verification before extraction adds further archive-format conditions to key rotation. **C2:** the framework separates updater integration and UI behavior from distribution through appcasts, with support for different application update arrangements. **C4:** the changelog records years of filesystem-safety fixes, XML parser hardening, compatibility work, and unit/UI testing; current documentation also explains migration away from the older updater API. Sources and entry points: [integration, signing, and migration documentation](https://sparkle-project.org/documentation/) and [historical changelog](https://github.com/sparkle-project/Sparkle/blob/2.x/CHANGELOG).

Study archive authentication separately from feed authentication: the current documentation makes signed feeds an opt-in feature, with its own failure and key-rotation behavior.

### 19. [vslavik/winsparkle](https://github.com/vslavik/winsparkle)

**Language/role:** C++ implementation with a C ABI; Windows application updates using Sparkle-style appcasts.

This is a separate Windows implementation, not a second listing of Sparkle's source. **C1:** its public API specifies signing-key precedence during migration: configuring EdDSA causes legacy DSA keys/signatures to be ignored. It also documents lifecycle constraints around asynchronous work: configure before initialization, initialization starts helper-thread work, and cleanup cancels pending activity and shuts helpers down. These are consequential contracts for host applications. **C2:** the small C ABI and application callbacks allow the update engine to be embedded across application languages and UI designs without exposing its C++ internals. Sources: [project overview](https://github.com/vslavik/winsparkle) and [public interface and lifecycle contract](https://raw.githubusercontent.com/vslavik/winsparkle/master/include/winsparkle.h).

**Start with:** `winsparkle.h`, especially key configuration, initialization, cleanup, and application callback APIs.

### 20. [NetSparkleUpdater/NetSparkle](https://github.com/NetSparkleUpdater/NetSparkle)

**Language/role:** C#/.NET; application updater with multiple UI integrations, including WinForms, WPF, and Avalonia.

**C1:** strict security mode requires signatures for both the appcast and update artifact; weaker modes change that guarantee. The integration guidance also calls out synchronization-context handling when background update work interacts with application UI. **C2:** signature verification and UI behavior are replaceable, while the version-3 architecture separates appcast serialization, downloading, and filtering through dedicated interfaces. The upgrade guide discusses version parsing and compatibility metadata, making this a useful study of how a reusable updater adapts to multiple version conventions and consumer applications. Sources and entry points: [security modes and embedding guide](https://github.com/NetSparkleUpdater/NetSparkle) and [API and format migration guide](https://github.com/NetSparkleUpdater/NetSparkle/blob/develop/UPGRADING.md).

Evaluate the selected security mode and verifier configuration; the presence of signing support does not make every integration equally authenticated.

### 21. [update4j/update4j](https://github.com/update4j/update4j)

**Language/role:** Java; modular application updating and launching. **Status:** GitHub marks the repository archived on **2024-03-18**; retain it as a historical design study.

**C1:** the update API supports public-key verification and staged archive installation, and checks downloaded JARs for conflicts that could prevent a future JVM from starting. Ordinary checksum-based change detection is not an authentication substitute; applications must configure signature verification appropriately. **C2:** separate `Delegate`, `UpdateHandler`, and `Launcher` service interfaces organize bootstrap, updating, and business-application launch. The documentation also explains module-path/class-path isolation and service-provider selection, useful for understanding why updating a running Java application is more complex than replacing files. Sources: [repository and archive status](https://github.com/update4j/update4j) and [architecture and update API documentation](https://github.com/update4j/update4j/wiki/Documentation).

**Start with:** the documentation's archive-update API, services, and bootstrap/business application separation. Archived status materially limits suitability for a new security-sensitive deployment.

### 22. [shorebirdtech/updater](https://github.com/shorebirdtech/updater)

**Language/role:** Rust with a C-compatible interface; patch updater integrated with Shorebird's Flutter runtime.

**C1:** the architecture tracks base-version compatibility and attempted, successful, and next-boot patches, with fallback behavior. Authentication requires a configured `patch_public_key`; hashes alone do not establish the publisher's identity. **C2:** a thin C interface separates runtime integration from Rust APIs, patch storage, networking, and configuration synchronization. **C3:** configured verification modes make a concrete startup tradeoff: strict mode rechecks patches at boot, whereas install-only mode avoids that repeated work but does not detect later on-disk modification through boot-time verification. Sources: [repository scope](https://github.com/shorebirdtech/updater) and [library architecture and verification modes](https://github.com/shorebirdtech/updater/blob/main/library/README.md).

**Start with:** the library README's patch lifecycle and verification policy. It explicitly contains imagined architecture and unimplemented goals, including persistence concerns; do not treat every described transactional property as an implemented guarantee.

## Coverage, search method, and limitations

Discovery used multiple distinct live-search formulations, followed by opening canonical repository pages and additional primary implementation or documentation sources. Search angles included:

- TUF clients by language: Python, Go, Rust, JavaScript/TypeScript, and PHP; trusted metadata, delegation, and signing-key rotation.
- TUF repository publication through CI, offline signers, task queues, and concurrent server workers.
- Uptane automotive Primary/Secondary coordination and package-manager integration.
- Embedded Linux signed OTA engines, inactive-slot installation, power-loss recovery, and streaming firmware writers.
- Content-addressed OS deployment and host-managed peripheral firmware updates.
- MCU secure boot, flash swap algorithms, SUIT manifests, and constrained-device storage/transport abstractions.
- macOS, Windows, .NET, Java, and Flutter application updating, including appcast signatures and startup verification cost.

Further searches increasingly returned the same implementations, integration layers, and tutorials. The selection includes lesser-known substantial projects such as fwup, tuf-on-ci, the RSTUF worker, and the RIOT SUIT subsystem alongside established engines. Separate implementations of TUF and appcast-based updating are retained because their code, integration surfaces, and architectural tradeoffs differ. Monorepos are counted once; no fork or mirror is presented as an independent implementation.

Excluded classes include specification-only repositories, awesome-lists, generic cryptographic libraries, thin bindings and build-system integrations, tutorials, and cloud-management products without a sufficiently evidenced update-engine implementation. PHP-TUF was considered but omitted because its own [repository warning](https://github.com/php-tuf/php-tuf) describes the implementation as incomplete and not secure for production; the retained experimental implementations are included for specifically documented, substantive architectural study and are labeled accordingly. This is a curated comparison, not an exhaustive ecosystem inventory or a production-readiness ranking.

Every retained repository had its GitHub identity checked and at least one additional primary source opened; README copies alone were not counted as additional evidence. No candidate code was executed, dependencies installed, or repositories cloned. Performance observations describe documented mechanisms rather than independent benchmarks. C4 is used only where inspected history establishes both sustained development and compatibility/testing work; it is not inferred from stars or creation dates. Archive and experimental notices are reported where observed, and no blanket claim of active maintenance is made. Links to moving branches and documentation may change after the research date.
