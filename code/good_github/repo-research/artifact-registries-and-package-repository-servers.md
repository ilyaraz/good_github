# Artifact registries and package repository servers

Research date: **2026-10-09**.

This selection covers 25 GitHub codebases that implement artifact registries, package hosting or proxy servers, public language repositories, and repository publication engines. It spans OCI images, Maven, npm, PyPI, Conda, Cargo, NuGet, RubyGems, Hex, Hackage, Composer, Go modules, Helm, Debian, and Nix. Public-service implementations are included for architectural study even when they are unsuitable as turnkey private servers. Each monorepo is counted once; the relevant subsystem is identified below.

Criteria legend:

- **C1 — Correctness:** demanding invariants, concurrency, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or models supporting multiple implementations and use cases.
- **C3 — Performance:** concrete resource or scaling constraints addressed through understandable architecture.
- **C4 — Evolution:** sustained development with evidence of compatibility work, testing, migrations, or complexity management.

The criteria are evidence-based selection judgments, not a claim that every component is exemplary. Linked implementation files and documentation are the suggested reading entry points. Repository identities were checked through their GitHub pages or API; implementation evidence was read separately from repository summaries.

## OCI registries and registry platforms

### 1. [distribution/distribution](https://github.com/distribution/distribution)

**Go — OCI/Docker registry implementation and reusable registry libraries.** Study the boundary between content-addressed objects, manifest references, and storage that may be local or remote.

- **C1:** Shared layers make deletion a reachability problem. The documented mark-and-sweep collector distinguishes deleting a manifest reference from deleting its underlying blobs, and explains why uploads during collection can cause reachable data to be swept. The requirement to stop writes is an explicit concurrency limitation, not a guarantee of online collection. See [garbage collection design and operation](https://distribution.github.io/distribution/about/garbage-collection/).
- **C2:** The [storage-driver contract](https://github.com/distribution/distribution/blob/main/registry/storage/driver/storagedriver.go) separates small-object operations, offset reads, streaming writes, redirects, and traversal. Its `FileWriter` distinguishes closing, committing, and cancelling an upload, making backend visibility semantics part of the interface.

### 2. [goharbor/harbor](https://github.com/goharbor/harbor)

**Go, TypeScript — registry platform providing project administration and artifact lifecycle services.** Harbor builds on Distribution but supplies a substantial independent management layer; it is not counted as another copy of Distribution.

- **C1:** Project permissions, token issuance, and quota checks sit between users and registry operations. The [architecture overview](https://github.com/goharbor/harbor/wiki/Architecture-Overview-of-Harbor) explains how authorization and quota middleware mediate pushes, offering a useful study of policy enforcement across separate services.
- **C2:** The same overview separates registry storage from artifact metadata management, replication adapters, and an asynchronous job service. These interfaces support multiple remote registries and lifecycle operations without embedding each integration in the registry protocol implementation.

The overview includes historical components; use it to understand subsystem boundaries, not as a current deployment inventory.

### 3. [project-zot/zot](https://github.com/project-zot/zot)

**Go — OCI-native registry with a compact core and optional extensions.** A useful contrast with larger registry platforms: the core implements OCI distribution and image-layout storage, while additional capabilities can be selected separately.

- **C2:** The [versioned architecture guide](https://zotregistry.dev/v2.1.11/general/architecture/) describes distinct HTTP, storage, and extension layers, with build-time and runtime extension choices. This makes protocol conformance and deployment specialization separable concerns.
- **C3:** The guide explains why the search extension keeps a metadata database instead of repeatedly walking artifact storage. Background scheduling coordinates tasks such as collection, mirroring, and integrity checking with foreground service demands. These are specific indexing and workload-management decisions rather than unsupported speed claims.

### 4. [quay/quay](https://github.com/quay/quay)

**Python, TypeScript/JavaScript — container registry service with distributed storage and background workers.** Study how protocol endpoints, domain models, persistence, and object storage are kept distinct within a large service.

- **C2:** The [architecture guide](https://github.com/quay/quay/blob/master/agent_docs/architecture.md) traces Flask endpoints through a registry model and data model into the database. Storage implementations and independently operated workers support replication, garbage collection, and repository mirroring.
- **C1:** [DistributedStorage](https://github.com/quay/quay/blob/master/storage/distributedstorage.py) distinguishes operations directed to a preferred location from operations attempted across locations. Its explicit handling of partial failures, all-location requirements, and read-only mode exposes the consistency choices behind geographically distributed blob storage. These policies should not be mistaken for automatic failover on every read.

## General repository frameworks and Maven servers

### 5. [pulp/pulpcore](https://github.com/pulp/pulpcore)

**Python — Pulp's repository framework, task system, content service, and core models.** The selected subsystem is the core platform; individual format plugins are not counted as separate repositories here.

- **C1:** Repository mutations create new immutable repository versions. The [add/remove task guide](https://pulpproject.org/pulpcore/docs/dev/learn/tasks/add-remove/) explains transactional version creation, cleanup on failure, and resource reservations that prevent conflicting asynchronous mutations.
- **C2:** The same guide distinguishes content records, stored artifacts, and remote artifacts, allowing synchronization policies to share a model while choosing when bytes are fetched.
- **C3:** The [service architecture](https://pulpproject.org/pulpcore/docs/admin/learn/architecture/) separates the Django API, asynchronous content serving, and worker processes. Each workload can be scaled independently, making Pulp particularly useful for studying control operations versus bulk content delivery.

### 6. [sonatype/nexus-public](https://github.com/sonatype/nexus-public)

**Java — official public codebase mirror for Nexus Repository Core.** Scope matters: the inspected README identifies Maven, raw, and APT formats with embedded H2 in Core. It distinguishes the downloadable Community Edition's additional formats and PostgreSQL support; those broader product features are not assumed to be present in this GitHub tree.

- **C1:** The [BlobStore API](https://github.com/sonatype/nexus-public/blob/main/public/common/components/nexus-blobstore-api/src/main/java/org/sonatype/nexus/blobstore/api/BlobStore.java) defines logical deletion separately from immediate physical removal. It explicitly warns that hard deletion disregards locking and concurrent readers, and distinguishes temporary objects and permanent storage.
- **C2:** [Repository facets](https://github.com/sonatype/nexus-public/blob/main/public/common/components/nexus-repository-config/src/main/java/org/sonatype/nexus/repository/Facet.java) supply composable repository behavior with configuration validation, lifecycle transitions, locking, and separate deletion/destruction hooks. Together with the blob-store interface, they provide a concrete study of extensible repository infrastructure.

### 7. [dzikoysk/reposilite](https://github.com/dzikoysk/reposilite)

**Kotlin — lightweight Maven repository and proxy server.** Particularly useful for understanding how a small server implements nontrivial upstream resolution policy.

- **C1:** The [mirror guide](https://github.com/dzikoysk/reposilite/blob/main/reposilite-site/data/guides/features/mirrors.md) specifies mirror priority, allowed and blocked groups, and the precedence of blocking rules. It also documents that cached artifacts survive later blocking changes and that upstream rate limiting is preserved instead of silently becoming a missing-artifact response. These details expose dependency-confusion and failure-reporting boundaries.
- **C3:** The same guide covers optional parallel Maven-metadata lookups, caching the selected upstream, artifact caching, and cache expiry. Study how resolution latency and upstream load interact with deterministic repository policy.

## JavaScript and TypeScript package registries

### 8. [verdaccio/verdaccio](https://github.com/verdaccio/verdaccio)

**TypeScript — private npm registry and caching proxy.** Useful for studying the semantics of combining private packages with upstream registry metadata.

- **C1:** A [maintainer explanation of package resolution](https://github.com/orgs/verdaccio/discussions/2285) describes merging local and upstream metadata, preferring cached tarballs, and rejecting publication of a version already present upstream. It clarifies that upstreams are read sources rather than destinations for local publication.
- **C4:** The [2021 migration guide](https://www.verdaccio.org/blog/2021/04/14/verdaccio-5-migration-guide/) documents concrete configuration, token-storage, and plugin-interface transitions. The current [version and testing policy](https://github.com/verdaccio/verdaccio/blob/master/VERSIONS.md) tracks supported majors, runtime compatibility, and branch-specific end-to-end tests. Together they establish evolution with explicit compatibility management. The inspected policy distinguishes stable 6.x from experimental development on `master`; the default branch is not synonymous with the stable release.

### 9. [cnpm/cnpmcore](https://github.com/cnpm/cnpmcore)

**TypeScript — npm-compatible registry service used by the cnpm/npmmirror community.** This offers a larger service-oriented counterpart to Verdaccio, including package synchronization and infrastructure integrations.

- **C2:** The [developer architecture guide](https://github.com/cnpm/cnpmcore/blob/master/DEVELOPER.md) separates controllers, domain entities and services, repository persistence, and infrastructure adapters. Queues, file storage, and authentication integrations have defined boundaries rather than being distributed throughout HTTP handlers.
- **C1:** The guide specifies ordered request validation: schema checking, user/token authentication, then resource-level authorization. Central role checks distinguish authentication from package-maintainer permissions, making publication authorization a concrete subject for code study. The guide is primarily in Chinese.

### 10. [jsr-io/jsr](https://github.com/jsr-io/jsr)

**Rust, TypeScript — public JavaScript/TypeScript registry, publishing service, and web application.** The monorepo includes both server and frontend; the publishing pipeline and serving architecture are the relevant subsystems.

- **C2:** The [architecture document](https://github.com/jsr-io/jsr/blob/main/architecture.md) describes queued publication, validation, dependency analysis, documentation generation, and production of npm-compatible tarballs. One package model drives both native module delivery and compatibility with another ecosystem.
- **C3:** Published files and compatibility archives are served from object storage through an edge worker, keeping ordinary downloads off the API/database path. Publication is handled asynchronously and clients poll its outcome. This is a clear example of separating expensive ingestion from the dominant read workload, explained in the same architecture document.

For lifecycle semantics, the [package guide](https://github.com/jsr-io/jsr/blob/main/frontend/docs/packages.md) distinguishes yanking, archiving, and immutability, including a narrowly constrained deletion exception.

## Python and Conda repositories

### 11. [devpi/devpi](https://github.com/devpi/devpi)

**Python — private Python indexes, an upstream cache, replication support, and related client/web components.** The server subsystem is the focus. Its user/team indexes and index inheritance provide more interesting semantics than a simple directory of wheel files.

- **C1:** [KeyFS](https://github.com/devpi/devpi/blob/main/server/devpi_server/keyfs.py) supports multiple concurrent read transactions and one write transaction. Readers observe a consistent snapshot despite later commits; serial tracking and change notifications connect transaction history to background processing.
- **C2:** The same implementation defines typed, parameterized keys and storage-connection protocols, separating logical package/index state from persistence details. Study how those abstractions support both request processing and replay or notification consumers without abandoning explicit transaction boundaries.

### 12. [pypi/warehouse](https://github.com/pypi/warehouse)

**Python — the application behind PyPI.** This is especially valuable as a public package service case study rather than a turnkey private-index recommendation.

- **C1:** The [upload implementation](https://github.com/pypi/warehouse/blob/main/warehouse/forklift/legacy.py) validates filenames, archive formats and contents, compression ratios, wheel metadata, and duplicate-file identities. Its checks include ambiguous archive formats and dangerous path components, making adversarial package ingestion a substantial engineering problem.
- **C3:** The [deployment architecture](https://warehouse.pypa.io/architecture/) separates uploads, ordinary web traffic, background workers, and CDN-backed downloads. Uploads bypass the CDN and receive their own process tuning; object delivery uses a primary store and fallback. Study how this isolates very different request sizes and durations.

### 13. [mamba-org/quetz](https://github.com/mamba-org/quetz)

**Python — Conda package server with channels and plugin hooks.** Included as a substantive implementation with limited recent activity: checked [GitHub metadata](https://api.github.com/repos/mamba-org/quetz) reported a last push on 2024-11-06 and did not mark the repository archived. That is an activity observation, not proof that all work has ceased.

- **C2:** [Package stores](https://github.com/mamba-org/quetz/blob/main/quetz/pkgstores.py) abstract channel creation, object operations, metadata, and download URLs across storage implementations. The [indexing pipeline](https://github.com/mamba-org/quetz/blob/main/quetz/tasks/indexing.py) adds hooks for package and index transformations.
- **C1:** Local writes use temporary files followed by rename; index generation stages files under temporary names before moving them into place. Validation compares stored files with database records and sizes. These mechanisms address partial publication and disagreement between metadata and storage, but do not imply an atomic transaction spanning every index file and backend.

## Rust package registries

### 14. [rust-lang/crates.io](https://github.com/rust-lang/crates.io)

**Rust, TypeScript — the crates.io registry backend and website.** Focus on background publication and the separation between registry APIs, indexes, and artifact delivery.

- **C1:** The [architecture guide](https://github.com/rust-lang/crates.io/blob/main/docs/ARCHITECTURE.md) describes a PostgreSQL-backed job queue using row locks to prevent simultaneous execution of the same job. Retry/backoff behavior and idempotence requirements make failure recovery part of the worker contract.
- **C3:** Crate archives and registry indexes are delivered through object storage and CDNs. Git and sparse-index updates occur in background work, while download statistics are derived from delivery logs instead of inserting synchronous database work into each download. The same guide connects these choices into an understandable request and event flow.

### 15. [kellnr/kellnr](https://github.com/kellnr/kellnr)

**Rust — private Cargo registry with package and documentation storage.** A smaller implementation in which protocol parsing, storage semantics, and tests can be studied together.

- **C1:** The [publish-body parser and tests](https://github.com/kellnr/kellnr/blob/main/crates/registry/src/pub_data.rs) validate attacker-controlled length prefixes before slicing the request body. Tests cover oversized lengths, missing prefixes, and short bodies, making a concrete boundary between malformed input and safe parsing visible.
- **C2:** The [storage trait](https://github.com/kellnr/kellnr/blob/main/crates/storage/src/storage.rs) distinguishes immutable writes from explicit overwrites and returns object metadata for conditional HTTP requests. This contract accommodates different artifact lifecycles—crate archives versus republished documentation—while supporting interchangeable storage implementations.

## NuGet repositories

### 16. [NuGet/NuGetGallery](https://github.com/NuGet/NuGetGallery)

**C# — NuGet gallery application, backend jobs, and shared service libraries.** The upload service is a useful entry into a production repository's multi-stage publication workflow.

- **C1:** [PackageUploadService](https://github.com/NuGet/NuGetGallery/blob/main/src/NuGetGallery/Services/PackageUploadService.cs) deliberately saves the package file before starting validation so competing uploads of the same identity cannot both proceed. Existing-file conflicts become conflict results; later failures trigger cleanup of related files. The code makes the database/object-store boundary explicit rather than pretending there is one distributed transaction.
- **C2:** The same service composes interfaces for package persistence, file storage, validation, namespaces, and supporting assets such as licenses and readmes. Engineers can follow how replaceable services cooperate while keeping publication sequencing centralized.

### 17. [loic-sharma/BaGet](https://github.com/loic-sharma/BaGet)

**C# — compact NuGet and symbol-package server.** Treat this as a historical architecture study: checked [GitHub metadata](https://api.github.com/repos/loic-sharma/BaGet) reported a last push on 2024-07-09, without an archived flag.

- **C2:** The [Core subsystem guide](https://github.com/loic-sharma/BaGet/tree/main/src/BaGet.Core) separates indexing, metadata, storage, search, and upstream access. The interfaces make a relatively small server useful for comparing database and object-store implementations.
- **C1:** [PackageIndexingService](https://github.com/loic-sharma/BaGet/blob/main/src/BaGet.Core/Indexing/PackageIndexingService.cs) handles malformed archives, version conflicts, optional overwrite, storage writes, database insertion, and search indexing in distinct stages. It also explicitly leaves additional validation and concurrent-storage conflict handling unresolved. Its study value includes these visible failure boundaries; it is not evidence that all publication races are solved.

## Other language ecosystem services

### 18. [rubygems/rubygems.org](https://github.com/rubygems/rubygems.org)

**Ruby — RubyGems.org package hosting, publication API, and dependency metadata service.** Study package ownership and version identity alongside an incremental metadata protocol.

- **C1:** The [Pusher model](https://github.com/rubygems/rubygems.org/blob/master/app/models/pusher.rb) orders package parsing, authorization, scoped-key checks, MFA requirements, validation, and persistence. It distinguishes idempotent publication from attempts to overwrite existing versions, locks version writes, and cleans up version records when artifact storage fails.
- **C3:** The [compact-index protocol](https://guides.rubygems.org/rubygems-org-compact-index-api/) supports conditional and ranged requests, appended updates, and whole-result digest validation. Periodic compaction balances incremental transfer against index growth. This is a concrete study of reducing dependency-resolution traffic without losing update integrity.

### 19. [hexpm/hexpm](https://github.com/hexpm/hexpm)

**Elixir — Hex package repository service for the Erlang/Elixir ecosystem.** Its release context makes database transactions and externally visible registry publication easy to compare.

- **C1:** The [release implementation](https://github.com/hexpm/hexpm/blob/main/lib/hexpm/repository/releases.ex) uses Ecto.Multi for related package/release changes, advisory matching, dependent-package updates, and audit records. Bulk retirement locks affected rows. Publication enqueues registry construction only after the tarball is stored, explicitly avoiding a registry entry that points to a not-yet-present archive.
- **C3:** The same context batches vulnerability lookup across release IDs and uses a set for membership, avoiding per-release database probes. Registry rebuilds are delegated to workers. These choices illustrate how a domain-oriented service can keep costly metadata work out of simple list and publication paths.

### 20. [haskell/hackage-server](https://github.com/haskell/hackage-server)

**Haskell — Hackage package server and reusable server framework.** Useful for comparing a strongly typed feature/state architecture with the service-interface approaches above.

- **C2:** The [feature framework](https://github.com/haskell/hackage-server/blob/master/src/Distribution/Server/Framework/Feature.hs) composes HTTP resources, state components, caches, and lifecycle hooks. State components expose checkpointing, backup, restoration, and comparison facilities rather than leaving persistence management implicit.
- **C1:** The [upload feature](https://github.com/haskell/hackage-server/blob/master/src/Distribution/Server/Features/Upload.hs) checks uploader and maintainer membership, name collisions under case normalization, and versions equivalent after removing trailing zeros. It rechecks whether insertion succeeded after earlier validation, acknowledging the intervening race. Archive acceptance and blob retention are connected through an explicit processing callback.

### 21. [composer/packagist](https://github.com/composer/packagist)

**PHP — the Packagist.org Composer repository service.** This includes package metadata generation and publication, not merely a static package catalogue. The README explicitly says the application is not intended as a supported self-hosting product.

- **C1:** [V2Dumper](https://github.com/composer/packagist/blob/main/src/Package/V2Dumper.php) publishes metadata through temporary files and rename, filters deleted versions, and checks recent deletion information to avoid inadvertently reintroducing removed package metadata.
- **C3:** The same implementation coordinates CDN upload and purge work, verifies outcomes, retries failures, and switches purge strategy when a queue backs up. It is an unusually concrete entry point for studying how database-derived package metadata reaches distributed caches under operational constraints.

## Go modules, Helm, Debian, and Nix artifacts

### 22. [gomods/athens](https://github.com/gomods/athens)

**Go — Go module proxy and storage service.** Study the difference between serving an already cached module and acquiring it through expensive upstream tooling.

- **C1:** The annotated [configuration and architecture choices](https://github.com/gomods/athens/blob/main/config.dev.toml) describe single-flight coordination so concurrent requests for the same module do not independently write it. The documentation distinguishes in-memory coordination from mechanisms suitable for multiple instances, including locking expiry and backend-specific guarantees.
- **C3:** Separate limits for module-fetch workers and protocol workers acknowledge that upstream retrieval can consume considerable memory and disk while cached serving has a different cost profile. The same file provides a direct map from resource constraints to concurrency controls and storage choices.

### 23. [helm/chartmuseum](https://github.com/helm/chartmuseum)

**Go — classic Helm chart repository server.** This serves chart packages and `index.yaml` repositories; it represents a different protocol and publication model from OCI-hosted Helm artifacts.

- **C1:** The [multitenant index implementation](https://github.com/helm/chartmuseum/blob/main/pkg/chartmuseum/server/multitenant/index.go) coordinates repository caches using locks and reconciles cached entries against storage objects. Timestamp tolerance and explicit force-regeneration behavior expose the subtleties of deciding whether cached metadata is still valid.
- **C3:** Index rebuilding is driven by changes rather than blindly repeated for every request. Cached index state and asynchronous statefile persistence separate expensive reconstruction from ordinary retrieval; persistence errors are handled without making the optional cache state the authoritative repository content.

### 24. [aptly-dev/aptly](https://github.com/aptly-dev/aptly)

**Go — Debian repository management and publication engine with a REST API.** Its relevance is package mirroring, snapshots, and publishing repository metadata; production HTTP delivery may be supplied separately.

- **C1:** The [publication implementation](https://github.com/aptly-dev/aptly/blob/master/deb/publish.go) defines a shared-pool lock key to prevent one publication's cleanup from deleting files needed by another. Signed release metadata and publication ordering add correctness obligations beyond copying `.deb` files into directories.
- **C2:** The same code handles snapshot and local-repository sources, components, architectures, and configurable publication storage. Study how immutable snapshots and mutable publication locations are represented separately so multiple repository workflows can share the publisher.

### 25. [zhaofengli/attic](https://github.com/zhaofengli/attic)

**Rust — multi-tenant Nix binary cache using content-defined chunking.** The project describes itself as an early prototype; this is an implementation study, not a maturity endorsement.

- **C3:** The [chunking design](https://github.com/zhaofengli/attic/blob/main/book/src/admin-guide/chunking.md) applies FastCDC to NAR archives and exposes size thresholds and chunk-size parameters. The tradeoff is explicit: chunk choices affect reuse and storage overhead, and changing them can reduce deduplication against existing data.
- **C1:** The [garbage collector](https://github.com/zhaofengli/attic/blob/main/server/src/gc.rs) uses database state, holder counts, and row locking with `SKIP LOCKED` to find reclaimable objects. It marks chunks deleted before removing remote objects, bounds deletion concurrency, and only removes the corresponding database rows after successful remote deletion. This is a useful case study in making database and object-store failures recoverable.

## Coverage, search process, and limitations

Discovery used live web searches across meaningfully different formulations: OCI registry implementations and garbage collection; multiprotocol repository managers; private Maven/npm/PyPI servers and proxy behavior; Rust and NuGet registry publication; RubyGems/Hex/Hackage/Composer service architecture; Go module proxies and Helm indexes; Debian snapshot publication; and Nix binary caches and Conda servers. Follow-up queries targeted storage interfaces, upload code, locking, metadata generation, tests, migration documents, release policies, and maintenance status. Later searches increasingly returned clients, wrappers, deployment recipes, or forks of already represented systems, rather than new substantial server architectures.

Canonical repository pages or API records were checked for all 25 selections, then additional primary documentation or source files were opened and read. Public raw GitHub files were used when rendered source pages failed. A late unauthenticated API rate limit affected further tree browsing, but did not prevent verification of the retained repository identities or their cited implementation evidence.

The selection deliberately includes smaller projects such as Reposilite, cnpmcore, Kellnr, and Attic alongside public-service codebases and established platforms. It excludes package-manager clients, dependency solvers without a package-serving role, scanners alone, static package lists, tutorial registries, deployment-only repositories, and near-duplicate forks. The Conda search found `rattler-server`, but its dependency-solving role did not fit this category. BaGetter was not added alongside BaGet merely to count a related implementation twice. Apache Archiva was considered but excluded from the retained list because it is a retired alternative; the [Apache Attic record](https://attic.apache.org/projects/archiva.html) dates its retirement to February 2024.

Maintenance and product scope require particular care: Nexus is a substantive official Core mirror; BaGet and Quetz have limited recent activity in the checked metadata; Attic carries a prototype warning; and Verdaccio's stable and development branches have different support status. No sustained-maintenance claim is inferred simply from a repository's creation date, stars, or latest push. C4 is assigned only where the cited evolution and compatibility material supports it.

This is a code-reading selection guide, not a benchmark, security audit, or deployment certification. No candidate code was run and no dependencies were installed. Performance criteria refer to documented mechanisms and code structure, without unverified throughput numbers. Branch links and project status can change after the research date, and some architecture documents describe earlier versions. The conclusions about what an engineer can learn are grounded interpretations of the cited material.
