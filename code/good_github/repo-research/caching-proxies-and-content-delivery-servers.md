# Caching proxies and content delivery servers

Research date: **2026-10-09**.

This selection covers HTTP forward and reverse caches, cache implementations embedded in larger servers, programmable caching layers, CDN routing and distribution systems, and specialized package and video delivery origins. It includes 20 repositories. General servers are included only for a named caching subsystem; peer-to-peer systems are included for their server-side content distribution machinery. Historical and dormant projects are identified explicitly. The assessment concerns useful engineering material to study, not a claim that every component is exemplary or suitable for a new deployment.

Criteria: **C1** — difficult correctness involving invariants, concurrency, adversarial inputs, or failures. **C2** — substantial abstractions reusable across use cases. **C3** — real performance constraints addressed through an understandable architecture. **C4** — sustained evolution with evidence of compatibility work, testing, or complexity management. Criteria below are grounded assessments of the linked primary material. The documentation and implementation links are suggested reading entry points.

## Core HTTP caching engines

### 1. [varnish/varnish](https://github.com/varnish/varnish)

**C — Varnish Software's Varnish Cache distribution.** Study how a cache separates freshness, serving stale content, retaining validators, and origin health policy. This is the separately evolving GitHub distribution, not the former `varnishcache/varnish-cache` repository. Its release notes document additions including integrated TLS; the upstream project's [explanation of the split](https://vinyl-cache.org/organization/on_vinyl_cache_and_varnish_cache.html) establishes the relationship.

- **C1:** Grace and keep have different semantics: an object retained for conditional revalidation must not automatically become deliverable. The documented lookup rules also distinguish an existing backend fetch from one that needs to be started. See the [grace/keep design](https://github.com/varnish/varnish/blob/main/doc/sphinx/users-guide/vcl-grace.rst).
- **C3:** Request coalescing limits duplicate origin work, while asynchronous refresh and grace address the latency and thread wake-up costs of making many clients wait. The same guide explains these tradeoffs and how backend health changes policy. The [release history](https://github.com/varnish/varnish/releases) adds concrete examples of request parsing, retry, and logging changes.

### 2. [squid-cache/squid](https://github.com/squid-cache/squid)

**C++ — forward proxy and hierarchical web cache.** Squid is particularly useful for studying the interaction between caching, protocol translation, access controls, content adaptation, and asynchronous transaction lifetimes.

- **C1:** The [architecture guide](https://wiki.squid-cache.org/ProgrammingGuide/Architecture) describes ordering between Host forgery checks, access checks, ICAP/eCAP adaptation, redirectors, and cache decisions. It also explains why TCP connection closure and shared UDP socket lifetime require different handling.
- **C2:** Client-facing protocols, server-facing protocols, cache storage, adaptation, and support services form distinct processing areas. Storage mediates data from memory, disk, or the upstream server rather than being an incidental response map. The architecture guide is the entry point for this decomposition, although it candidly contains unfinished sections.
- **C4:** The [ChangeLog](https://github.com/squid-cache/squid/blob/master/ChangeLog) records years of compiler/platform fixes, regression repairs, transaction-lifetime fixes, and removal of obsolete subsystems. Entries from 2021–2025 include preserving truncated-entry state, fixing malformed chunk handling, and retiring dead protocols and APIs.

### 3. [apache/trafficserver](https://github.com/apache/trafficserver)

**C++ — Apache Traffic Server, a caching forward/reverse proxy and CDN building block.** The most distinctive study target is its disk cache: compact indexes, object fragments, volumes, and the relationship between HTTP transactions and asynchronous cache operations.

- **C1:** The [cache architecture](https://docs.trafficserver.apache.org/en/latest/developer-guide/cache-architecture/architecture.en.html) explains why a short directory tag is only a candidate match: the complete key must be checked after reading the fragment, and collision iteration must not skip valid entries.
- **C3:** That design makes explicit the tradeoff between compact directory entries, approximate read sizes, fragment sizes, wasted space, and disk I/O efficiency. It provides considerably more architectural detail than a performance headline.
- **C2:** The broader [cache developer guide](https://docs.trafficserver.apache.org/en/latest/developer-guide/cache-architecture/index.en.html) connects cache virtual connections, HTTP tunnels, RAM cache policies, cache APIs, and tiered storage. Its authors describe the architecture documents as reconstructed and provisional; use them alongside the implementation rather than as an infallible specification.

### 4. [nginx/nginx](https://github.com/nginx/nginx)

**C — NGINX Open Source; specifically proxy buffering and the HTTP file cache.** Study the interaction of cache population, shared metadata, bounded buffering, background updates, and cache maintenance within a general web server.

- **C1:** The [proxy module reference](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache_lock) specifies per-key population locking, lock age and timeout behavior, and the distinction between bypassing lookup and preventing storage. It also documents the cache-key consequence of disabling HEAD-to-GET conversion.
- **C3:** The same reference explains response buffering to memory and temporary files, shared cache metadata, and cache loader/manager controls. Background refresh can serve stale content while fetching an update, exposing origin-load versus freshness tradeoffs directly in configuration. Start with [`proxy_cache_path`](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache_path) and follow its associated directives.

The cited manual includes some commercial-only directives; their presence is not evidence that those features belong to this repository. The criteria here concern the documented open-source caching mechanisms.

### 5. [haproxy/haproxy](https://github.com/haproxy/haproxy)

**C — official GitHub mirror of HAProxy's development repository; specifically its embedded HTTP cache.** This offers a useful contrast with disk-oriented CDN caches: a deliberately limited RAM cache integrated into a load balancer's request/response rules.

- **C1:** The [cache chapter](https://docs.haproxy.org/3.2/configuration.html#6) states explicit exclusion rules and bounded `Vary` handling. Unsupported variation and malformed repeated single-valued headers prevent serving the cached response; variation is not treated as an arbitrary extra string in the key.
- **C3:** Cache storage is shared across threads and divided into fixed-size blocks. Object-size limits, expiry caps, secondary-entry bounds, and oldest-object removal make memory and CPU costs visible. The same chapter explains the cost of computing variation keys.
- **C2:** `cache-use` and `cache-store` participate in conditional request and response rules, allowing cache policy to compose with the server's routing machinery. The manual also documents their dependency: skipping key computation on the request path prevents storing the response.

### 6. [apache/httpd](https://github.com/apache/httpd)

**C — official Apache HTTP Server mirror; `mod_cache` and its storage providers.** Study how caching composes with a server's authentication phases, handlers, and output filters. This entry concerns those modules rather than treating the entire server as a dedicated cache.

- **C1:** The [caching guide](https://httpd.apache.org/docs/2.4/caching.html) explains conditional revalidation, variants, and the consequences of executing the cache in the early quick-handler phase. Bypassing later authorization processing is an architectural issue that a cache implementer must understand.
- **C2:** The alternative normal-handler placement permits caching at a controlled point in the filter chain, with downstream filtering or personalization. On a miss, a filter captures a cacheable response while normal processing continues; on a 304, it serves the retained body.
- **C3:** The guide makes the fast early path versus flexible late path tradeoff explicit and describes disk-cache size/inode management through `htcacheclean`. These mechanisms connect performance decisions to request-processing structure.

### 7. [tempesta-tech/tempesta](https://github.com/tempesta-tech/tempesta)

**C — Linux-integrated web accelerator, caching proxy, and firewall.** This is an unusual kernel-resident design rather than a conventional socket-based userspace proxy. The repository describes the project as beta and `master` as an unstable development branch.

- **C1:** The [HTTP cache implementation](https://github.com/tempesta-tech/tempesta/blob/master/fw/cache.c) distinguishes cacheability, validators, freshness metadata, and HTTP/2 header reconstruction. For example, cached responses must not carry HTTP/1 chunked transfer encoding into HTTP/2.
- **C3:** Cache keys are assigned to NUMA nodes; comments explain the deliberate choice of a cheap mapping and the consequences of node-count changes. The [Tempesta DB design](https://github.com/tempesta-tech/tempesta/blob/master/db/README.md) describes persistent in-kernel storage designed for deferred-interrupt context, where reads and writes cannot sleep. Together these make memory locality and execution-context constraints concrete.

## Programmable and application-aware caching layers

### 8. [cloudflare/pingora](https://github.com/cloudflare/pingora)

**Rust — proxy framework; `pingora-cache` is the relevant subsystem.** This is a construction kit for network services rather than a ready-configured CDN appliance. Its repository warns that proxy caching integration and related APIs are experimental.

- **C1:** [`lock.rs`](https://github.com/cloudflare/pingora/blob/main/pingora-cache/src/lock.rs) models elected writers, waiting readers, transient failures, abandoned writers, and separate timeout outcomes. Dropping a writer permit without releasing it is a meaningful failure state, not just a mutex implementation detail.
- **C2:** [`storage.rs`](https://github.com/cloudflare/pingora/blob/main/pingora-cache/src/storage.rs) defines asynchronous storage operations and hit/miss handlers independently of a particular backend. Streaming-write tags prevent a reader from receiving the wrong concurrent fill; purge targets distinguish a logical key from an exact entry identity. These contracts are useful examples of expressing cache correctness at abstraction boundaries.

### 9. [darkweak/souin](https://github.com/darkweak/souin)

**Go — shared HTTP caching middleware with integrations for multiple servers and frameworks.** Study how a common policy engine is adapted to different hosting environments and storage implementations.

- **C1:** The [middleware implementation](https://github.com/darkweak/souin/blob/master/pkg/middleware/middleware.go) handles `Vary: *`, varied cache keys, response snapshots, and request coalescing through `singleflight`. It also contains explicit handling for aborted HTTP handlers and coordination of storage-eviction workers.
- **C2:** The handler operates on storage interfaces and configurable storage order, while server/framework integrations reuse the caching layer. The separate [revalidation code](https://github.com/darkweak/souin/blob/master/pkg/rfc/revalidation.go) translates request validators into a shared representation, illustrating separation between HTTP policy and storage behavior.

The project's RFC-compliance description is its own claim. The selection is based on the concrete implementation responsibilities above, not an independent certification of complete compliance.

### 10. [ledgetech/ledge](https://github.com/ledgetech/ledge)

**Lua — Redis-backed HTTP cache and ESI layer for NGINX/OpenResty.** Treat this as a historical study candidate: the [GitHub metadata](https://api.github.com/repos/ledgetech/ledge) records its latest repository push in 2021, although the repository is not archived.

- **C1:** [`collapse.lua`](https://github.com/ledgetech/ledge/blob/master/lib/ledge/collapse.lua) acquires an expiring Redis lock through an atomic Lua script, avoiding the race between a separate lookup and expiring write. Its return contract distinguishes contention from Redis failure.
- **C3:** The [streaming and collapsed-forwarding design](https://github.com/ledgetech/ledge#philosophy-and-nomenclature) explains delivery while content is being fetched and the tradeoffs when concurrent requests wait for an origin fill. The documented collapse window bounds waiting after a fatal origin-side failure.
- **C2:** Cache-key policy, ESI, hooks, background jobs, and the HTTP state machine are separable parts of the layer. This makes it useful for studying a programmable cache that uses an external shared store rather than local disk.

### 11. [jiangwenyuan/nuster](https://github.com/jiangwenyuan/nuster)

**C — a substantively extended HAProxy-derived HTTP cache.** Counted separately because it adds its own cache engines, stores, management API, and persistence machinery. The [GitHub metadata](https://api.github.com/repos/jiangwenyuan/nuster) records a latest push in 2021; it is not presented as currently maintained.

- **C2:** The [cache configuration and store documentation](https://github.com/jiangwenyuan/nuster#store) describes rule-specific cache keys, lifetimes, stale behavior, and memory/disk storage combinations. HTTP caching and the separate REST cache mode share storage machinery; this entry focuses on HTTP caching.
- **C3:** Management work is moved out of request iterations into the master process, with bounded cleaner, loader, and saver batches. Its asynchronous persistence mode writes memory first and saves to disk later, making latency/durability tradeoffs explicit.
- **C1:** The [disk store implementation](https://github.com/jiangwenyuan/nuster/blob/master/src/nuster/store/disk.c) tracks metadata and temporary files and finalizes stored objects through rename. It is a concrete place to examine incomplete writes, cleanup, persistence, and publication of cache objects.

### 12. [trickstercache/trickster](https://github.com/trickstercache/trickster)

**Go — general HTTP reverse cache plus time-series query acceleration.** Its combination of byte-range caching, partial time-series reuse, and progressive request collapsing makes it more than a metrics-specific wrapper.

- **C1:** The [collapsed-forwarding design](https://github.com/trickstercache/trickster/blob/main/docs/collapsed-forwarding.md) explicitly checks whether responses are safe to share, covering authorization, cookies, variation, non-idempotent methods, and truncated bodies. It specifies that incomplete transfers must not be represented as complete cache objects.
- **C3:** Progressive collapsing streams a single origin response to concurrent clients before the fill completes. The [range-request design](https://github.com/trickstercache/trickster/blob/main/docs/range_request.md) fetches only missing ranges and can split upstream requests when an origin lacks multipart-range support.

The linked design documents describe `main` and should not be assumed to describe every released version. An indexed README still contained an older release-status notice that was absent from the current raw README, so that notice is not used here.

## Specialized origins and distributed delivery

### 13. [ironsmile/nedomi](https://github.com/ironsmile/nedomi)

**Go — media-oriented HTTP cache with chunk-level storage.** A historical, incomplete implementation: [GitHub metadata](https://api.github.com/repos/ironsmile/nedomi) records its latest push in 2018. Its README documents limitations including no HTTPS support and no cache reload from disk after restart.

- **C3:** The [cache-zone design](https://github.com/ironsmile/nedomi#cache-zones) divides large files into parts and bounds storage by object count and part size. The motivation is partial media consumption: storing every byte of every fetched media object can waste capacity.
- **C1:** The [segmented LRU implementation](https://github.com/ironsmile/nedomi/blob/master/cache/lru/lru.go) maintains a hash lookup plus multiple linked-list tiers under a mutex. Promotion and eviction must keep list membership, tier identifiers, and lookup entries consistent; optional invariant checks make that concern visible.

This is useful for examining a compact cache policy and its limitations, rather than as evidence of a finished production server.

### 14. [kaltura/nginx-vod-module](https://github.com/kaltura/nginx-vod-module)

**C — substantial NGINX module implementing a video-on-demand delivery origin.** It repackages MP4 content into HTTP streaming formats and supports local, remote-range, and mapped sources. Counted for its own packaging and cache implementation, not as another copy of NGINX.

- **C1:** The [test guide](https://github.com/kaltura/nginx-vod-module/blob/master/test/README.md) covers corrupted MP4 inputs, bad upstream responses, iframe byte-range validation, reference-output comparisons, and cache stress tests. It even describes allocator-memory pollution to reveal incorrect assumptions about zero-initialized memory.
- **C3:** The [buffer cache implementation](https://github.com/kaltura/nginx-vod-module/blob/master/ngx_buffer_cache.c) documents shared-memory layout and coordinates tree lookup, reference counts, queues, and buffer reuse. The repository's performance guidance separates metadata/manifest caching from a downstream HTTP cache or CDN and discusses asynchronous file I/O.

This is the origin/packaging part of a delivery system; the project itself recommends a caching tier in front for larger deployments.

### 15. [apache/trafficcontrol](https://github.com/apache/trafficcontrol)

**Go, Java, and TypeScript — archived CDN platform monorepo.** GitHub marks it archived on **2025-11-24**. Relevant subsystems include Traffic Router, Traffic Monitor, Traffic Ops, and the Grove caching proxy. They are counted together once.

- **C2:** The [Traffic Router overview](https://github.com/apache/trafficcontrol/blob/master/docs/source/overview/traffic_router.rst) describes DNS and HTTP routing as distinct mechanisms with different information available to the decision. Cache health, location, delivery-service policy, and content placement are explicit concepts.
- **C3:** HTTP routing uses consistent hashing to concentrate a resource on an appropriate cache within a group, increasing effective aggregate cache capacity. Health/load information also allows routing around overloaded nodes. The same overview explains these mechanisms rather than merely asserting global scale.
- **C1:** The [Grove guide](https://github.com/apache/trafficcontrol/blob/master/grove/README.md) exposes bounded parent concurrency, retry/error caching policy, soft cache-size limits, and the slow-client timeout tradeoff. Its optional non-RFC-strict mode is stated openly, making this a useful study of operational policy compromises.

### 16. [dragonflyoss/dragonfly](https://github.com/dragonflyoss/dragonfly)

**Go — peer-to-peer content distribution control services and scheduling.** The repository covers delivery of files, container images, OCI artifacts, and other large content. Its inclusion concerns distribution and cache scheduling, not the unrelated Dragonfly key-value database.

- **C1:** The [scheduler implementation](https://github.com/dragonflyoss/dragonfly/blob/main/scheduler/scheduling/scheduling.go) handles cancellation, unavailable peer streams, bounded scheduling retries, and fallback to the source. Persistent-cache replication also requires comparing available replicas with the target rather than blindly selecting another peer.
- **C2:** Normal tasks, persistent tasks, and persistent-cache tasks share a scheduling interface while using distinct resource managers. Parent evaluation, dynamic configuration, and protocol-version-specific responses are separated in the same implementation.
- **C3:** Peer selection and replication distribute download work across cached peers instead of sending every transfer to the origin. The [scheduling tests](https://github.com/dragonflyoss/dragonfly/blob/main/scheduler/scheduling/scheduling_test.go) are a verified source-tree entry point for following this subsystem's scenarios; they were not executed for this report.

### 17. [uber/kraken](https://github.com/uber/kraken)

**Go — peer-to-peer registry distribution layer.** Study the separation between content-addressed blob transport and mutable human-readable names, and the distinction between coordinating peers and transferring the bytes.

- **C2:** The [architecture document](https://github.com/uber/kraken/blob/master/docs/ARCHITECTURE.md) separates host agents, origins, trackers, upload proxies, and the build index. Origins have pluggable storage, while the central distribution components are not intrinsically tied to Docker images.
- **C1:** That document explicitly disclaims consistency guarantees for tag-to-digest mappings and recommends unique tags. Replication uses retrying queues and components use self-healing hash rings. These are useful failure-model boundaries to study, not evidence that arbitrary mutable-tag workflows are strongly consistent.
- **C3:** Trackers arrange peers into a sparse graph while origins supply seed content. The design moves distribution work into the peer network rather than requiring the tracker to move each byte. This architectural rationale is also explained in the [repository's distribution overview](https://github.com/uber/kraken#architecture); its headline throughput claims are not used as selection evidence.

### 18. [unpkg/unpkg](https://github.com/unpkg/unpkg)

**TypeScript — production source for the UNPKG package CDN, including edge workers and a Bun file backend.** The monorepo is counted once. It is useful for studying the boundary between package resolution, versioned URLs, HTTP caching, and extracting files from registry artifacts.

- **C1:** The [main request handler](https://github.com/unpkg/unpkg/blob/main/packages/unpkg-www/src/request-handler.tsx) resolves version ranges and package exports before selecting the response. It differentiates unresolved version redirects from stable versioned resources, including their cache lifetimes and redirect behavior.
- **C2:** Shared package operations support separate public-file, browser, and ESM workers, while the backend handles artifact retrieval and extraction. The [backend request handler](https://github.com/unpkg/unpkg/blob/main/packages/unpkg-files/src/lib/request-handler.ts) exposes file/list/build operations with explicit path and exact-version validation.
- **C3:** Long-lived responses are attached to versioned content, while mutable resolution results receive shorter lifetimes. The backend also returns content digests and lengths, making the edge/origin division and cache identity visible in implementation.

### 19. [esm-dev/esm.sh](https://github.com/esm-dev/esm.sh)

**Go and TypeScript — JavaScript module CDN with on-demand builds.** Unlike a cache that simply forwards opaque bytes, this delivery server must resolve packages and build browser-consumable modules before serving reusable artifacts.

- **C1:** The [build queue](https://github.com/esm-dev/esm.sh/blob/main/server/build_queue.go) shares a task among requests for the same path. It keeps the queue key stable when package installation changes build context, and canceling one client's wait does not cancel work needed by other clients.
- **C3:** The queue uses bounded concurrency, FIFO pending work, negative-cache checks, and shared completion channels to control expensive duplicate builds. It releases capacity and schedules subsequent work when a task finishes, including panic handling.

The [hosting guide](https://github.com/esm-dev/esm.sh/blob/main/HOSTING.md) supplies a second useful entry point: exact-version purges remove generated artifacts, while floating specifiers refresh version resolution and preserve builds when the resolved version is unchanged. This exposes another concrete cache-identity boundary.

### 20. [jech/polipo](https://github.com/jech/polipo)

**C — archived, explicitly unmaintained HTTP caching proxy.** Retained as a compact historical design study. The repository's own README says maintenance has ended.

- **C1:** The [manual](https://github.com/jech/polipo/blob/master/polipo.texi) explains partial instances caused by range requests and interrupted transfers. It distinguishes arbitrary partial data in memory from the initial contiguous portion stored on disk, and discusses falling back from segmented retrieval when a resource changes.
- **C3:** Its single-threaded nonblocking model, persistent connections, pipelining probes, range completion, and separate memory pools address latency and resource usage through a relatively compact architecture.
- **C4:** The [CHANGES history](https://github.com/jech/polipo/blob/master/CHANGES) documents releases across 2007–2014, HTTP compatibility work, platform fixes, compliance testing, integer-overflow repairs, and corrections to revalidation loops. This supports sustained historical engineering, not present-day maintenance.

## Search coverage and limitations

Discovery used more than six distinct live-web formulations: established HTTP caching engines; Go/Rust reverse caches; Lua/OpenResty caching and invalidation; media byte-range caches; peer-to-peer registry distribution; JavaScript package CDNs; time-series reverse caches; Java/Erlang alternatives; self-hosted CDN platforms; and the Varnish/Vinyl repository transition. Later language- and niche-oriented searches largely returned existing selections, small wrappers, narrow registry download caches, semantic LLM caches, or projects without enough inspected evidence to add confidently. Primary repository pages or the GitHub API verified every selected canonical URL; additional documentation or implementation material was opened for every entry. Public source-tree metadata and raw files were read without cloning or executing candidate code.

The selection deliberately omits generic cache databases, client-only caches, proxy tutorials, container/configuration wrappers, CDN asset catalogs such as library inventories, and general reverse proxies without an inspected caching subsystem. Package and video projects are included only where the repository implements a substantive delivery origin. Kaltura's module, Pingora's caching crates, and the cache subsystems in HAProxy/httpd are explicitly narrower selections within their respective projects.

The former `varnishcache/varnish-cache` repository was excluded because the official project [moved to the Vinyl forge](https://vinyl-cache.org/organization/moving.html); its frozen GitHub location is not treated as a continuing mirror. The distinct Varnish Software distribution is included once. HAProxy and Apache httpd are identified as official mirrors. Polipo and Traffic Control are archived; Ledge, nuster, and nedomi are historical/dormant study selections based on their recorded GitHub activity and documented limitations, not assumptions of active support.

Repository metadata was checked on the research date, but a recent push alone was not used to claim maintenance quality or satisfy C4. Some documentation follows development branches, and version-specific behavior may differ. No benchmarks, builds, security audits, or test suites were run. Performance criteria refer to inspected mechanisms and tradeoffs, not independently reproduced throughput numbers. The relative value of each codebase as a study target is an engineering inference from those sources.
