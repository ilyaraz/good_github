# Directory services and identity synchronization systems

Research date: **2026-10-09**

This selection covers directory servers, virtual directories, domain identity infrastructure, identity reconciliation and provisioning engines, and substantial connector libraries. The emphasis is on maintaining identity data and its meaning across protocols, databases, replicas, and applications. General authentication products appear only when a concrete directory or synchronization subsystem merits study. The 23 repositories range from compact LDAP services to enterprise identity platforms; each monorepo is counted once.

Criteria legend:

- **C1:** difficult correctness involving invariants, concurrency, adversarial inputs, or failure recovery.
- **C2:** substantial reusable abstractions supporting multiple integrations or use cases.
- **C3:** real performance constraints addressed through an understandable architecture.
- **C4:** sustained evolution demonstrated through compatibility work, testing, or complexity management—not merely repository age.

The criteria below are engineering assessments grounded in the linked material. Source and documentation links are also suggested reading entry points. Inclusion is a guide to useful code, not a claim that every component is exemplary or that every project has the same maintenance cadence. Repository pages were opened to verify canonical GitHub locations; no candidate code was executed.

## Directory servers and virtual directories

### 1. [openldap/openldap](https://github.com/openldap/openldap)

**C — general-purpose LDAP server, libraries, and replication. Official GitHub mirror of the OpenLDAP-hosted repository.**

Study `slapd` through the boundary between ordinary directory operations and replication. The replication guide explains why object identity, update ordering, deletions, and recovery need explicit representations rather than a periodic copy of entries.

- **C1:** syncrepl uses synchronization state and cookies to resume consumers; the guide distinguishes single-provider guarantees from the consistency problems introduced by independent writers and network partitions.
- **C2:** the consumer engine is independent of the database backend, while the provider is an overlay. The same machinery supports polling, persistent updates, partial replicas, and proxy arrangements.
- **C3:** delta-syncrepl transfers logged changes instead of whole changed entries and falls back to ordinary synchronization when the retained log is insufficient. This is a concrete bandwidth/recovery tradeoff, not a blanket throughput claim.

Read the [replication architecture and configuration guide](https://www.openldap.org/doc/admin26/replication.html), especially syncrepl, delta-syncrepl, and mirror mode.

### 2. [389ds/389-ds-base](https://github.com/389ds/389-ds-base)

**C, Python, and Rust — LDAP server with extensible server and storage components.**

The useful study target is the interaction of replication metadata, directory authorization, and server plugins. Its architecture reference contains historical deployment details, so use it for mechanisms rather than current storage defaults or replica limits.

- **C1:** replication distinguishes stable entry UUIDs from mutable DNs, records change sequence numbers and replica update vectors, and retains tombstones for deleted entries. These structures expose the correctness burden of renames and deletions across replicas.
- **C2:** operation-specific plugins separate access control, replication, and backend behavior from the network frontend.
- **C3:** the access-control plugin caches subject, target, and result information in connection/operation extensions to avoid repeated policy evaluation.

Start with the [architecture and replication design](https://www.port389.org/docs/389ds/design/architecture.html). The repository README additionally documents sanitizer-enabled builds and its test entry points.

### 3. [apache/directory-server](https://github.com/apache/directory-server)

**Java — ApacheDS LDAP directory server and embeddable directory service.**

ApacheDS offers a particularly readable decomposition of protocol handling, directory semantics, and storage. Study the `DirectoryService`, rather than treating the whole server as a single LDAP request handler.

- **C1:** `OperationManager` protects against concurrent modifications; the service tracks sessions and pending requests so operations can be abandoned. Initialization also establishes schema and configuration state before protocol service begins.
- **C2:** requests pass through an ordered interceptor chain and then `PartitionNexus`, which selects a backend using the DN. This permits reusable authorization, normalization, and schema processing across partitions.

Read the [DirectoryService architecture](https://directory.apache.org/apacheds/advanced-ug/1.2-directory-service.html) and [interceptor extension guide](https://directory.apache.org/apacheds/advanced-ug/6-implementing-interceptor.html). These are ApacheDS 2.0 documents; they describe extension contracts and ordering constraints, not a promise that arbitrary interceptor rearrangement is safe.

### 4. [OpenIdentityPlatform/OpenDJ](https://github.com/OpenIdentityPlatform/OpenDJ)

**Java — Open Identity Platform's separately evolved OpenDJ directory-server lineage.**

This is the community continuation, not a second listing of a ForgeRock repository. Its own release stream contains implementation changes, security fixes, and expanded test/build coverage.

- **C1:** replication replays operations and retains history for conflict resolution. Recovery depends on retention and generation state; eventual convergence does not imply immediate read-after-write consistency on another replica.
- **C2:** directory servers own entries and conflict resolution, while replication servers relay and retain changes. The roles can be colocated or deployed independently.
- **C3:** separating the two roles reduces the number of fully meshed replication participants. Assured replication explicitly trades acknowledgement latency for additional confirmation.

Read [Managing Data Replication](https://doc.openidentityplatform.org/opendj/admin-guide/chap-replication) and the project's [release history](https://github.com/OpenIdentityPlatform/OpenDJ/releases), which establishes substantive continued evolution of this lineage.

### 5. [samba-team/samba](https://github.com/samba-team/samba)

**C and Python — Active Directory domain-controller and directory replication subsystems within Samba. Official team GitHub mirror; contribution workflow is on GitLab.**

The relevant scope is the AD directory database and DRS replication, not Samba's file-server implementation. A productive entry point is conversion and transactional application of replicated objects.

- **C1:** the implementation validates replication metadata, translates remote attribute identifiers, and uses a multipass schema-resolution process. Applying objects starts an LDB transaction and restores prior schema state on failures.
- **C2:** incoming DRS objects are converted into a common LDB representation through schema and prefix-map abstractions. This reusable translation layer accommodates different object classes and schema updates rather than hardcoding a user-record format.

Read [replicated_objects.c](https://github.com/samba-team/samba/blob/master/source4/dsdb/repl/replicated_objects.c), especially `dsdb_repl_resolve_working_schema`, `dsdb_convert_object_ex`, and the transaction-wrapped commit path. The code comments connect implementation decisions to AD protocol requirements.

### 6. [kanidm/kanidm](https://github.com/kanidm/kanidm)

**Rust — identity directory, replication, Unix integration, and read-only LDAP gateway.**

Kanidm is useful for studying how a typed directory model can centralize validation and authorization while serving several protocols. The architecture document explains both read and write paths, though it also acknowledges ongoing evolution.

- **C1:** incoming requests become schema-checked events; writes enforce access controls before plugins transform entries. Post-write plugins maintain reference consistency and reverse group-membership links within the transaction.
- **C2:** protocol representations, events, query processing, backend storage, and pre/post-operation plugins have distinct responsibilities.
- **C3:** the documented design combines indexed candidate selection with copy-on-write structures and a single writer, allowing concurrent searches without blocking on that writer.

Start with the [architecture design](https://kanidm.github.io/kanidm/stable/developers/designs/architecture.html). No comparative benchmark claims from the repository's marketing text are needed to justify inclusion.

### 7. [lldap/lldap](https://github.com/lldap/lldap)

**Rust — compact SQL-backed user/group directory with LDAP and GraphQL interfaces.**

LLDAP deliberately implements a limited LDAP surface. That narrower scope makes it useful for tracing one identity model through a web administration interface, authentication flow, and legacy LDAP consumers.

- **C1:** its authentication design distinguishes the OPAQUE-based web flow from LDAP password binds and describes refresh-token removal and JWT blacklisting on logout. The document also identifies incomplete notification work, making revocation boundaries worth examining carefully.
- **C2:** shared authentication types, domain logic, and protocol infrastructure are separated; the same SQL-backed users and memberships serve GraphQL and LDAP across several database engines.

Read [docs/architecture.md](https://github.com/lldap/lldap/blob/main/docs/architecture.md), then follow its `auth`, `server/src/domain`, and `server/src/infra` map. This is a focused directory implementation, not a replacement for every general-purpose LDAP operation.

### 8. [glauth/glauth](https://github.com/glauth/glauth)

**Go — lightweight LDAP frontend, authentication gateway, and pluggable directory backends.**

GLAuth provides a smaller example of composing directory access around existing identity sources. Its backend chain can combine locally configured authentication features with an upstream directory.

- **C1:** authorization is scoped by action and target subtree through capabilities. Correctly preserving those scopes across different backend types and chained authentication is a meaningful security boundary; the compatibility switch that bypasses capabilities makes this boundary explicit.
- **C2:** the LDAP frontend delegates to interchangeable file, LDAP, ownCloud, and database backends. Chaining supports adding an authentication check before forwarding to an existing directory.

Read [backend architecture and chaining](https://glauth.github.io/docs/backends.html) and [capability semantics](https://glauth.github.io/docs/capabilities.html). Platform limitations of Go plugins are documented; do not assume every backend deployment mode is portable to Windows.

### 9. [TremoloSecurity/MyVirtualDirectory](https://github.com/TremoloSecurity/MyVirtualDirectory)

**Java — LDAP virtual directory and namespace router.**

MyVirtualDirectory is valuable for studying a directory assembled from multiple backends rather than a single authoritative database. Its namespace routing exposes protocol semantics that a simple reverse proxy would miss.

- **C1:** routing adjusts search bases and scopes for individual namespaces, distinguishes missing objects from other backend failures, and has separate paths for renames within and across namespaces. Cross-backend moves deserve scrutiny for partial failure; inclusion does not imply distributed atomicity.
- **C2:** global and namespace-local interceptor chains provide reusable transformation and backend composition, with explicit initialization and shutdown behavior.

Read [Router.java](https://github.com/TremoloSecurity/MyVirtualDirectory/blob/master/src/main/java/net/sourceforge/myvd/router/Router.java) and [InsertChain.java](https://github.com/TremoloSecurity/MyVirtualDirectory/blob/master/src/main/java/net/sourceforge/myvd/core/InsertChain.java). The README explains how its tests use real OpenLDAP instances.

## Domain identity infrastructure and directory consumers

### 10. [freeipa/freeipa](https://github.com/freeipa/freeipa)

**Python and C — integrated domain identity management. Official GitHub mirror.**

FreeIPA contributes integration logic and directory plugins on top of components such as 389 Directory Server and Samba. Study that integration code as its own system, rather than counting the bundled upstream implementations again.

- **C1:** its Samba integration design explains incompatible POSIX and Windows identity models. SID generation requires appropriate object classes, bounded numeric identifiers, and absence of an existing SID; LDAP object-class constraints affect the order of user changes.
- **C2:** the `ipasam` adapter and directory plugins translate FreeIPA's schema into Samba's domain services, while enrollment and management use FreeIPA APIs and LDAP controls.

Read the [Samba domain-controller integration design](https://github.com/freeipa/freeipa/blob/master/doc/designs/adtrust/samba-domain-controller.md). It explicitly documents limitations and unfinished work, so it should not be read as a claim that FreeIPA is a drop-in Windows AD domain controller.

### 11. [univention/univention-corporate-server](https://github.com/univention/univention-corporate-server)

**Python, C, and shell — UCS identity management, directory replication, and service integration. Official GitHub mirror.**

The selected monorepo subsystem is Directory Listener/Notifier and its application-facing listener modules. It demonstrates how directory changes become configuration changes in services that do not speak LDAP.

- **C1:** monotonically advancing transaction IDs let disconnected listeners request missed changes. When the target LDAP server is unavailable, replication buffers changes in a failed-LDIF file for later replay.
- **C2:** application-specific listener modules share the same change-delivery mechanism. The documented CUPS example turns directory object creation, modification, and deletion into corresponding configuration edits.

Read [Domain replication with Listener and Notifier](https://docs.software-univention.de/ucs-operation/5.2/en/domain-infrastructure/listener-notifier.html), including transaction recovery and module resynchronization. This repository's distinct contribution is the integration machinery surrounding the underlying directory servers.

### 12. [SSSD/sssd](https://github.com/SSSD/sssd)

**C and Python — local identity cache and directory integration for Linux system interfaces.**

SSSD belongs here as the consumer side of distributed identity: it maintains local representations of remote users, groups, and policy for operating-system services.

- **C1:** only backends write the persistent cache; responders return cached data after checking validity or requesting refresh. The design explicitly handles expired entries and stale-data fallback when the remote backend cannot be reached.
- **C2:** per-domain providers and separate NSS, PAM, sudo, and other responders isolate remote-source behavior from consuming interfaces.
- **C3:** persistent, negative, and memory-mapped caches address different costs. The last can avoid even contacting the responder for a recently resolved identity.

Read [SSSD Architecture](https://sssd.io/docs/architecture.html) and the [unified cache-request interface](https://sssd.io/contrib/cache_req.html). These expose cache semantics and request reuse more clearly than a feature checklist.

### 13. [keycloak/keycloak](https://github.com/keycloak/keycloak)

**Java — LDAP/AD federation and synchronization subsystem within an IAM monorepo.**

The selected material is user federation, not the broader token or SSO stack. Study the tensions between a local application-facing user model and an externally owned LDAP identity.

- **C1:** read-only, writable, and unsynchronized edit modes assign different ownership to local and remote attributes. Mapper configuration does not automatically change when those modes change, exposing a concrete configuration-consistency hazard. LDAP passwords are not imported for remote password validation.
- **C2:** multiple LDAP providers map into a shared user model through configurable attribute mappers, with import and non-import storage modes.
- **C3:** the documentation explains the cost of validating imported users through additional LDAP searches and how caching affects single-user access.

Read the [LDAP federation design and administration chapter](https://github.com/keycloak/keycloak/blob/main/docs/documentation/server_admin/topics/user-federation/ldap.adoc). It provides concrete synchronization semantics rather than merely advertising LDAP support.

## Reconciliation, provisioning, and synchronization orchestration

### 14. [Evolveum/midpoint](https://github.com/Evolveum/midpoint)

**Java — identity governance, provisioning, correlation, and reconciliation engine.**

MidPoint is especially valuable for examining the difference between desired identity state and the state of independently failing resources.

- **C1:** the consistency mechanism records unfinished operations on shadow objects, including deltas, status, attempts, and timestamps. Failed communication can postpone work without blocking unrelated resources; reconciliation and refresh tasks revisit it.
- **C2:** resource events pass through classification, correlation, situation determination, and configurable reactions. The policy machinery is shared across live synchronization, reconciliation, discovery, and import, with channels for exceptions.

Read the [consistency mechanism](https://docs.evolveum.com/midpoint/reference/before-4.8/synchronization/consistency/) and [synchronization algorithm](https://docs.evolveum.com/midpoint/reference/master/resources/resource-configuration/schema-handling/synchronization/). The first is explicitly versioned historical documentation; use it for the mechanism and check version-specific configuration before implementation work.

### 15. [apache/syncope](https://github.com/apache/syncope)

**Java — identity management and provisioning core within Apache Syncope.**

Syncope is a strong comparison with midPoint: both integrate external identity stores, but Syncope presents a particularly explicit separation between workflow, provisioning managers, mappings, and connector execution.

- **C1:** propagation can save tasks for re-execution. Priority tasks run sequentially and halt on failure, while tasks without priority can run concurrently. A preliminary read can legitimately turn a requested create into an update or the reverse.
- **C2:** user, group, and arbitrary-object provisioning managers, resource mappings, workflow adapters, and propagation hooks are separate extension contracts.
- **C3:** comparing existing external state with requested modifications avoids unnecessary operations; incremental pull depends on connector change-tracking support rather than pretending every resource supports it.

Read the [reference guide's architecture and provisioning sections](https://syncope.apache.org/docs/4.0/reference-guide.html), particularly sections 2.2 and 3.7. These document execution semantics, failure behavior, and the extension interfaces together.

### 16. [Internet2/grouper](https://github.com/Internet2/grouper)

**Java — group/entitlement registry, loaders, change processing, and provisioning.**

Grouper brings the higher-education community's distributed administration requirements into scope. Its relevant subsystem turns authoritative group and membership state into downstream LDAP, SQL, and SCIM representations.

- **C2:** the Subject API, group registry, rules/change-log components, and target-specific provisioners form reusable layers for heterogeneous institutional systems. See the [architecture map](https://github.com/Internet2/grouper/blob/GROUPER_6_BRANCH/ARCHITECTURE.md).
- **C4:** the [historical changelog](https://github.com/Internet2/grouper/blob/GROUPER_6_BRANCH/CHANGELOG.md) documents evolution across 2012, 2016, and 2018: change-log-driven provisioning, replacement of a provisioner to address performance and configuration complexity, safeguards against excessive removals, and migration of configuration/library layers.

The changelog supports sustained complexity management; its older entries are not presented as descriptions of the current provisioner's entire implementation. Start with the architecture map, then use the historical changes to understand why provisioning abstractions evolved.

### 17. [lsc-project/lsc](https://github.com/lsc-project/lsc)

**Java — LDAP Synchronization Connector engine for directory-oriented data integration.**

LSC is a focused alternative to a full governance platform. It compares source and destination data, transforms attributes, and can produce differences or execute synchronization.

- **C1:** synchronization rules distinguish identifier construction, pivot matching, renaming, creation, update, and deletion. Attribute policies distinguish forcing, keeping, and merging values; these choices determine whether existing destination information survives a run.
- **C2:** source/destination services and scriptable transformations let the same engine handle LDAP, JDBC data, files, and additional plugins without rewriting the reconciliation loop.

Read [Synchronization Rules](https://lsc-project.org/documentation/latest/syncrules.html) and the [plugin extension model](https://lsc.readthedocs.io/en/latest/plugins.html). This is useful code for studying explicit reconciliation policy without the surrounding approval and governance stack.

### 18. [jelhub/scimgateway](https://github.com/jelhub/scimgateway)

**TypeScript/JavaScript — SCIM 1.1/2.0 gateway to LDAP, REST, SQL, and other provisioning targets.**

SCIM Gateway exposes the mismatch between standardized provisioning requests and target-specific APIs. The plugin contracts specify paging, identifiers, requested attributes, group enrichment, and tenant/endpoint selection.

- **C1:** its changelog records fixes for incomplete paginated group membership, create-then-read races against directory targets, and repeated membership changes. These are concrete consistency and idempotency problems encountered at protocol boundaries.
- **C2:** one SCIM processing layer delegates user/group operations to endpoint plugins, with common mapping and REST helpers. The `baseEntity` contract supports selecting distinct tenants or endpoints.

Read the [gateway implementation and plugin API contracts](https://github.com/jelhub/scimgateway/blob/master/lib/scimgateway.ts) and [changelog](https://github.com/jelhub/scimgateway/blob/master/CHANGELOG.md). Fix history is evidence of the problem space, not proof that every connector has identical behavior.

### 19. [lithnet/miis-autosync](https://github.com/lithnet/miis-autosync)

**C# — synchronization orchestration service for Microsoft FIM/MIM.**

This is an independently implemented scheduler/controller around Microsoft's synchronization service, not an open implementation of the proprietary MIM engine. Its cycle progresses from import to delta synchronization, export, and confirming import until staged changes are consumed.

- **C1:** synchronization runs require exclusion while imports and exports may overlap. The implementation also serializes service state transitions, locks individual controller operations, and distinguishes cancellation from stopping without cancelling work.
- **C2:** per-management-agent controllers and configurable scheduled, change-driven, and PowerShell triggers provide a reusable orchestration layer across connected systems.

Read the repository's execution-cycle explanation, then [ExecutionEngine.cs](https://github.com/lithnet/miis-autosync/blob/master/src/Lithnet.Miiserver.AutoSync/ExecutionEngine.cs). The source exposes controller lifecycle and configuration-version handling. Current support cadence was not established; inclusion is based on inspectable architecture and category fit.

## Connector frameworks and directory client infrastructure

### 20. [Tirasa/ConnId](https://github.com/Tirasa/ConnId)

**Java and C# — identity connector framework, API/SPI, and connector hosting infrastructure.**

ConnId merits a separate entry from its consuming identity platforms: it owns the reusable boundary between an identity manager and independently packaged connectors. It is the evolved ICF lineage, not a listing of each downstream fork.

- **C1:** its contract distinguishes stable resource identifiers from mutable names, models connector initialization/disposal, and isolates connector instances and versions. Correctness depends on preserving object identity and lifecycle when resources behave differently.
- **C2:** the manager-facing API and connector-facing SPI separate provisioning policy from protocol translation. Bundles expose schemas and operations while the framework supplies instance management and pooling.

Read the substantive [ConnId connector development guide](https://github.com/Evolveum/docs/blob/master/connectors/connid/1.x/connector-development-guide/index.adoc), maintained by a framework contributor, especially architecture, identifier semantics, bundles, and lifecycle. The guide explicitly discusses exceptions to name uniqueness.

### 21. [Evolveum/connector-ldap](https://github.com/Evolveum/connector-ldap)

**Java — substantive ConnId LDAP/Active Directory connector implementation.**

This is included separately from ConnId because it implements protocol-specific synchronization and schema translation rather than merely wrapping the framework.

- **C1:** the AD DirSync implementation carries cookies into synchronization tokens, requests deleted entries, and refetches objects because DirSync may return only changed attributes—even omitting object class. This is a useful example of reconstructing complete identity meaning from partial change notifications.
- **C2:** synchronization strategies reuse connection management, schema translation, error handling, and ConnId delta/result contracts. Different directory behaviors are adapted behind the provisioning-facing interface.

Read [AdDirSyncStrategy.java](https://github.com/Evolveum/connector-ldap/blob/master/src/main/java/com/evolveum/polygon/connector/ldap/sync/AdDirSyncStrategy.java) and the [changelog](https://github.com/Evolveum/connector-ldap/blob/master/CHANGELOG.MD). Listed fixes include binary AD security-descriptor syntax, inherited user object classes, and LDAP presence-filter translation.

### 22. [pingidentity/ldapsdk](https://github.com/pingidentity/ldapsdk)

**Java — UnboundID LDAP SDK, connection management, protocol extensions, and directory tooling.**

The SDK is substantial infrastructure for building directory integrations, not a generated API wrapper. Connection pooling provides a particularly good entry point into the interaction between concurrency, authentication state, and failure recovery.

- **C1:** `bindAndRevertAuthentication` restores the pool's identity after a temporary bind and discards the connection if restoration fails. Defunct-connection handling prevents broken or incorrectly authenticated connections from returning to normal circulation.
- **C2:** standalone connections and pools share `LDAPInterface`; server-set and post-connect abstractions support multiple servers and TLS setup without rewriting callers.
- **C3:** pool sizing, reusable connections, queueing, health checks, and configurable retry operation types expose the actual cost and failure model of repeated directory access.

Read [LDAPConnectionPool.java and its extensive API documentation](https://github.com/pingidentity/ldapsdk/blob/master/src/com/unboundid/ldap/sdk/LDAPConnectionPool.java).

### 23. [cannatag/ldap3](https://github.com/cannatag/ldap3)

**Python — pure-Python LDAP client with multiple execution strategies.**

ldap3 is useful for studying how one protocol API supports synchronous scripts, threaded applications, asynchronous requests, and LDIF-producing workflows while exposing different safety guarantees.

- **C1:** thread-safe strategies return operation-local status, result, response, and request tuples. The documentation explicitly says the higher-level abstraction layer is not itself thread-safe. Escaping, schema checks, referrals, and restart behavior add further protocol-boundary concerns.
- **C2:** interchangeable connection strategies and server pools share a common operation surface; LDIF generation and restartable connections are behaviors of that abstraction rather than separate applications.
- **C3:** reusable threaded connections and deferred open/bind operations avoid connection work where appropriate, with configurable pool lifetime and keepalive behavior.

Read the [Connection and strategy guide](https://ldap3.readthedocs.io/en/latest/connection.html), starting with strategy guarantees and lazy connections. No claim about present release cadence is inferred from the repository's age or language-compatibility tagline.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations. The main angles were LDAP server replication; Java directory interceptors and virtual directories; Rust/Go lightweight identity stores; FreeIPA/Samba/UCS/SSSD domain integration; identity governance and ConnId provisioning; LDAP-specific reconciliation; SCIM gateways and group provisioning; and C#/Microsoft synchronization orchestration. Later searches for Python/Ruby LDAP synchronization and Go SCIM engines mostly returned narrow adapters, experimental implementations, examples, or already-covered architectural families. The Microsoft-oriented search added Lithnet as a distinct, substantive orchestration design.

Each retained canonical repository was opened, and at least one additional primary design document, API guide, source file, or changelog was read. Repository READMEs were not counted twice through raw URLs. For several GitHub files, the GitHub connector supplied the source when browser rendering was inconvenient. Some wiki/documentation requests failed; unavailable pages are not used as retained evidence. In particular, Lithnet is supported by its repository and execution-engine source rather than its inaccessible wiki pages.

The selection deliberately excludes directory Docker images, installation-only repositories, awesome lists, demonstration SCIM endpoints, and small application-specific sync scripts. Pure OIDC/SAML brokers and general authorization engines are outside scope unless their actual directory synchronization subsystem was inspected. Connector families are not expanded into one entry per trivial adapter. OpenLDAP, Samba, FreeIPA, and UCS are identified as official GitHub mirrors; OpenDJ's community continuation is counted once, with its own evolution checked. No archived-only tutorial or discontinued upstream duplicate is retained.

Coverage favors LDAP/AD and enterprise provisioning because those searches yielded the strongest primary implementation evidence. It does not exhaust commercial cloud-directory internals, which are generally unavailable as complete GitHub implementations. Several architecture documents retain historical terminology or version-specific details; those limitations are called out rather than silently promoted to current operational facts. C4 is awarded only where an inspected history demonstrates evolution and complexity management. Performance statements describe mechanisms, not unverified numerical superiority. Testing references were inspected as documentation only; no test suite, deployment, or security audit was performed.
