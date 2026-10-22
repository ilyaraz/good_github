# Authentication and identity federation servers

Research date: **2026-10-09**.

This report selects 27 substantial GitHub codebases implementing identity providers, authentication services, federation brokers, embeddable authorization servers, and domain or network authentication servers. It covers browser SSO, application identity, cloud federation, and Kerberos/RADIUS infrastructure. Monorepos count once, with the relevant subsystem identified. The selection is a guide to engineering study, not a security audit or a claim that every component is exemplary. Criteria assignments below are grounded judgments about the cited implementation or design material.

**Criteria legend**

- **C1 — Correctness:** difficult invariants, concurrency, adversarial inputs, protocol semantics, or failure handling.
- **C2 — Abstractions:** substantial, reusable interfaces or models supporting multiple applications and integration patterns.
- **C3 — Performance and structure:** explicit resource, latency, or throughput constraints addressed through understandable architecture; no comparative benchmark claims are implied.
- **C4 — Evolution:** evidence across years of compatibility work, testing, or deliberate management of accumulated complexity.

## General identity and access management platforms

### 1. [keycloak/keycloak](https://github.com/keycloak/keycloak)

**Language / role:** Java; OIDC/OAuth 2.0 and SAML identity provider, federation server, and identity administration platform.

Study its authentication flow interpreter: browser authentication becomes a sequence of configurable executions, nested flows, challenges, and required actions, rather than a single credentials check.

- **C1:** Required, alternative, and conditional executions have distinct completion semantics. A successful condition does not itself authenticate a user; challenge handling and the association between authentication sessions and user sessions must preserve that distinction. The development guide walks through the algorithm and its failure paths.
- **C2:** Authenticator factories, user-storage providers, and configurable flow executions allow the same server to support different credential sources and login policies without replacing its protocol endpoints.

**Entry point:** [Server development guide, including authentication SPI and algorithm walkthrough](https://www.keycloak.org/docs/latest/server_development/index.html).

### 2. [goauthentik/authentik](https://github.com/goauthentik/authentik)

**Language / role:** Python, Go, and TypeScript; identity provider and authentication/federation platform.

Study how its flow engine separates identifying a pending user, verifying credentials, and attaching that user to an authenticated session. This is a useful comparison with Keycloak's execution model.

- **C1:** Policy evaluation can occur during planning or immediately before a stage. Policies that depend on information obtained by earlier stages therefore have timing-sensitive behavior. The user-login stage performs the session transition; merely identifying a user is insufficient.
- **C2:** Reusable stages, stage bindings, and policies compose enrollment, authentication, recovery, and invalidation flows. The same primitives support materially different identity journeys.

**Entry point:** [Flow architecture, planning, stages, and policy timing](https://docs.goauthentik.io/add-secure-apps/flows-stages/flow/).

### 3. [zitadel/zitadel](https://github.com/zitadel/zitadel)

**Language / role:** Go and TypeScript; identity platform and authorization/federation server.

Study identity management implemented with event sourcing and separate command and query models. Its architecture exposes the difference between durable identity changes and the projections used to serve reads.

- **C1:** Commands append authoritative events, while projections consume them asynchronously. Spoolers replay missed events, and coordination assigns projection work; recovery and consistency are therefore first-class concerns.
- **C2:** Commands, event storage, queries, and projections form reusable boundaries across identity and organization operations instead of binding each API directly to one mutable record representation.
- **C3:** Read projections and background processing address query cost and reconstruction work while keeping the write model separate. This supports studying performance tradeoffs without relying on advertised throughput numbers.

**Entry point:** [Software architecture: event sourcing, CQRS, and spoolers](https://zitadel.com/docs/concepts/architecture/software).

### 4. [apereo/cas](https://github.com/apereo/cas)

**Language / role:** Java; institutional SSO and multi-protocol authentication server.

Study the separation of web interaction, ticket issuance, and authentication. The architecture distinguishes a ticket-granting ticket representing SSO from service tickets presented to individual applications.

- **C1:** Ticket validation must bind a ticket to the service for which it was issued. The validation documentation explains service matching and authorization extension points, making recipient binding and ticket lifecycle concrete study topics. [Ticket validation](https://apereo.github.io/cas/8.0.x/authentication/CAS-Protocol-TicketValidation.html).
- **C2:** Web, ticket, and authentication tiers separate browser orchestration from credential verification and protocol handling, allowing CAS, SAML, and other integrations to reuse server components. [Architecture](https://apereo.github.io/cas/7.3.x/planning/Architecture.html).

The linked architecture and validation documents are versioned separately; they are not a claim that configuration is identical between CAS releases.

### 5. [JanssenProject/jans](https://github.com/JanssenProject/jans)

**Language / role:** Primarily Java in the relevant subsystem; Janssen authentication server and associated identity services. Focus on **`jans-auth-server`** within the monorepo.

Study the lifecycle of an identity-provider session independently of the relying party's application session.

- **C1:** Sessions have unauthenticated and authenticated states, separate idle and absolute lifetimes, and configurable identifier rotation at authentication. The documentation explicitly distinguishes browser-cookie expiration, server-side session lifetime, and activity inside an RP that the identity provider cannot observe.
- **C2:** Session-event interception scripts and selectable cache/persistence providers allow deployment-specific behavior around a shared authentication model. Memory, Redis, Memcached, and database storage are documented alternatives, rather than assumptions embedded in every flow.

**Entry points:** [Session lifecycle and extension mechanisms](https://docs.jans.io/stable/janssen-server/auth-server/session-management/); [authentication-server subsystem](https://github.com/JanssenProject/jans/tree/main/jans-auth-server).

### 6. [wso2/product-is](https://github.com/wso2/product-is)

**Language / role:** Java; WSO2 Identity Server product assembly and integration repository. Much underlying implementation lives in associated Carbon component repositories; this entry counts the product and its integration surface once.

Study a protocol-neutral authentication framework built around adapters and multi-step authentication, plus the tests that assemble these components into a server.

- **C1:** Inbound processors validate protocol requests before converting them to a common representation; authentication steps advance only after a successful authenticator. JIT provisioning belongs to the identity-provider configuration, creating another boundary between authenticating an identity and provisioning it.
- **C2:** Separate inbound request/response processors, local or federated authenticators, and provisioning components permit different protocols and upstream identity systems to use the same orchestration framework. [Architecture](https://is.docs.wso2.com/en/7.0.0/references/architecture/).

**Further entry point:** [Product integration-test modules](https://github.com/wso2/product-is/tree/master/modules/integration).

### 7. [OpenIdentityPlatform/OpenAM](https://github.com/OpenIdentityPlatform/OpenAM)

**Language / role:** Java; community OpenAM access-management and federation server.

Study authentication chains whose short-circuit rules affect both success and the authentication strength recorded in a session.

- **C1:** Required, requisite, sufficient, and optional modules have different failure and continuation semantics. The guide also documents how skipped modules can affect calculated authentication level and how to change that behavior. These are subtle policy invariants, not merely plugin loading details. [Authentication services](https://doc.openidentityplatform.org/openam/admin-guide/chap-auth-services).
- **C2:** Authentication modules, post-authentication plugins, and realm-specific services allow different applications and administrative domains to share the engine while supplying their own credential checks and chains. The same guide documents these extension boundaries.

**Further entry point:** [16.1.3 release notes](https://github.com/OpenIdentityPlatform/OpenAM/releases/tag/16.1.3), including realm-scoped session destruction and end-session token-hint fixes. These illustrate concrete federation failure modes; the entry does not count predecessor OpenAM repositories separately.

### 8. [casdoor/casdoor](https://github.com/casdoor/casdoor)

**Language / role:** Go with a JavaScript/TypeScript interface; identity provider and federated login platform.

Study the interface between a broad upstream-provider model and the detailed validation needed by modern token protocols.

- **C1:** Its DPoP implementation checks proof structure, JWT type and algorithm, embedded keys and signatures, request method/URI, issuance time, access-token hashes, and refresh-token key binding. These checks provide a concrete adversarial-input study; inspecting this file alone does not establish end-to-end replay protection. [DPoP implementation](https://github.com/casdoor/casdoor/blob/master/object/token_dpop.go).
- **C2:** The provider model accommodates endpoints, scopes, identity-field mapping, OIDC issuer information, and SAML metadata in a common configuration abstraction. This is useful for examining the benefits and complexity of unifying heterogeneous upstream systems. [Provider model](https://github.com/casdoor/casdoor/blob/master/object/provider.go).

## Federation brokers and protocol-focused services

### 9. [dexidp/dex](https://github.com/dexidp/dex)

**Language / role:** Go; OIDC identity broker over upstream systems such as LDAP, SAML, and hosted identity providers.

Study a deliberately narrower server that gives applications one downstream protocol while adapting many upstream authentication sources.

- **C1:** Connectors expose differing capabilities. In particular, upstream SAML assertions cannot generally be refreshed noninteractively, so the broker cannot uniformly promise refresh-token behavior. This makes protocol translation constraints visible. [Connector contracts and capability matrix](https://dexidp.io/docs/connectors/).
- **C2:** Connector interfaces and storage backends separate identity acquisition from OIDC handling and persistence. The storage documentation requires atomic update/delete behavior, references backend conformance tests, and explains the SQLite in-memory concurrency restriction. These are meaningful contracts for alternative implementations. [Storage design and requirements](https://dexidp.io/docs/configuration/storage/).

### 10. [ory/hydra](https://github.com/ory/hydra)

**Language / role:** Go; OAuth 2.0/OIDC authorization server with separately supplied login and consent applications.

Study the correctness and cost of passing an authorization transaction through multiple browser redirects and external user interfaces.

- **C1:** Ory's flow redesign replaces intermediate opaque database references with authenticated encrypted flow data. Decoding checks request age and network context, illustrating how integrity and context binding must accompany moving state into URLs or cookies.
- **C2:** Login and consent interfaces keep the protocol engine independent of a particular user database or login UI.
- **C3:** The redesign reduces intermediate database operations and retains the final consent persistence step. The engineering account connects query/index behavior and write volume to a specific flow representation; no numerical speedup is assumed here.

**Entry point:** [Official engineering account of the authorization-flow and database optimization](https://www.ory.sh/oauth2-oidc-server-performance-tuning-scale/).

### 11. [simplesamlphp/simplesamlphp](https://github.com/simplesamlphp/simplesamlphp)

**Language / role:** PHP; SAML identity/service-provider software and federation platform.

Study attribute processing and consent as a resumable pipeline surrounding federated authentication.

- **C1:** An authentication-processing filter may redirect the browser, save state, and later resume the chain. The developer contract requires resumable state to live in the state array, warns about serialization constraints, and separates processing from page rendering to avoid incorrect reload behavior.
- **C2:** Ordered filters can apply globally, at an IdP or SP, or through individual metadata. Attribute transformation, release decisions, and consent therefore reuse one extensible processing model across federations.

**Entry point:** [Authentication-processing filters and their implementation contract](https://simplesamlphp.org/docs/stable/simplesamlphp-authproc.html).

### 12. [IdentityPython/SATOSA](https://github.com/IdentityPython/SATOSA)

**Language / role:** Python; federation proxy connecting front-end and back-end authentication protocols.

Study a broker whose main abstraction is an internal identity representation between protocol adapters. Its “micro services” are transformation plugins in the processing chain, not necessarily separate network services.

- **C1:** The base flow saves the originating requester, restores the proper front end after back-end authentication, reconstructs the subject from configured attributes, and routes errors with the preserved context. Correct request/response correlation and identity mapping are central to avoiding misdelivery across federation boundaries. [Core orchestration](https://github.com/IdentityPython/SATOSA/blob/master/src/satosa/base.py).
- **C2:** Configurable front ends, back ends, internal attribute mappings, and request/response transformation chains support protocol bridging and federation-specific attribute policies without rewriting the proxy. [Configuration and internal attribute model](https://github.com/IdentityPython/SATOSA/blob/master/doc/README.md).

### 13. [authelia/authelia](https://github.com/authelia/authelia)

**Language / role:** Go; authentication server providing reverse-proxy authentication and an OIDC identity provider.

Study its explicit decision to distinguish authorization context available in proxy requests from context available to OIDC flows.

- **C1:** An OIDC refresh request can originate from a relying party rather than the end user's network, and proxy-specific properties such as resource URI and method are not generally present. The design record explains why applying proxy access rules unchanged would produce incorrect policy decisions.
- **C2:** OIDC client authorization policies are a separate abstraction from forward-auth access-control rules. Subject-oriented policy and authentication context can be reused across relying parties without pretending that the server continuously authorizes their protected resources.

**Entry point:** [Architecture decision on OIDC client authorization policy](https://www.authelia.com/reference/architecture-decision-log/1/).

## Application identity, compact providers, and embeddable server engines

### 14. [kanidm/kanidm](https://github.com/kanidm/kanidm)

**Language / role:** Rust; identity provider spanning OIDC, passkeys, Unix integration, and network authentication.

Study identity-directory replication where availability must coexist with schema, uniqueness, and deletion constraints.

- **C1:** Its replication design addresses changes identified by time and server identity, clock rollback, concurrent attribute changes, schema and uniqueness conflicts, tombstones, and replicas that fall behind the retention window. Identity state is therefore treated as a distributed consistency problem.
- **C3:** Replication update vectors and indexes support incremental transfer; local replicas address read capacity and client latency. The design explains the structures behind those goals rather than providing only a scaling claim. [Replication design and notes](https://kanidm.github.io/kanidm/master/developers/designs/replication_design_and_notes.html).

**Further entry point:** [Repository overview and supported identity protocols](https://github.com/kanidm/kanidm/blob/master/README.md). The design document explores replication generally; it should not be read as a support guarantee for every possible topology.

### 15. [sebadob/rauthy](https://github.com/sebadob/rauthy)

**Language / role:** Rust; compact OAuth 2.0/OIDC identity provider with passkey support.

Study the resource budgeting required when an HTTP service performs deliberately expensive password verification.

- **C1:** Concurrent Argon2 operations multiply memory demand. The tuning guide discusses limiting hashing threads and accounting for per-hash memory, making login-induced resource exhaustion a concrete correctness and availability concern.
- **C3:** HTTP workers, password-hashing workers, and allocator behavior have separate controls. The guide also distinguishes visible CPU counts from container limits, linking deployment constraints to the concurrency structure instead of assuming more workers always help.

**Entry points:** [Project and server overview](https://sebadob.github.io/rauthy/); [resource and performance tuning](https://sebadob.github.io/rauthy/config/tuning.html).

### 16. [logto-io/logto](https://github.com/logto-io/logto)

**Language / role:** TypeScript; application identity platform. Focus on **`packages/core`**, including tenant orchestration and the OIDC integration layer.

Study how a product wraps a reusable OIDC engine with tenant-specific databases, connectors, configuration, and resource lifecycles. Its use of node-oidc-provider does not make the tenant-management implementation a duplicate of that engine.

- **C1:** `Tenant` marks itself disposed synchronously before awaiting cleanup, rejects new request reservations, and drains existing requests subject to a timeout before closing the database pool. The same object coordinates cache invalidation for signing-key changes. [Tenant implementation](https://github.com/logto-io/logto/blob/master/packages/core/src/tenants/Tenant.ts).
- **C2:** Tenant-owned environment, queries, libraries, and provider instances give integrations a common boundary. The OIDC adapter maps application metadata and tenant configuration into the protocol engine's models. [OIDC adapter](https://github.com/logto-io/logto/blob/master/packages/core/src/oidc/adapter.ts).

### 17. [supabase/auth](https://github.com/supabase/auth)

**Language / role:** Go; standalone authentication and session/token service used by Supabase.

Study refresh-token rotation under concurrent requests and lost responses. The token service makes the distinction between retrying a legitimate refresh and reusing a revoked credential unusually concrete.

- **C1:** Refresh processing checks session and client relationships, locks rows transactionally, and handles revoked-parent tokens, token-family revocation, and reuse intervals. A previous response that was lost can require returning an already-issued token rather than treating every repeated request as an attack.
- **C3:** Contention retries are bounded and coordinated above the database operation so requests waiting to retry do not unnecessarily occupy database-pool connections. [Token service](https://github.com/supabase/auth/blob/master/internal/tokens/service.go).

**Further entry point:** [Refresh endpoint and token-format handling](https://github.com/supabase/auth/blob/master/internal/api/token_refresh.go), useful for following the boundary between HTTP input validation and session/token state changes.

### 18. [ory/kratos](https://github.com/ory/kratos)

**Language / role:** Go; headless identity, authentication, and self-service account server. Protocol authorization can be supplied separately by Hydra; these are distinct server implementations.

Study typed authentication flows that can drive either browser experiences or API clients while maintaining assurance and session state.

- **C1:** The login-flow model distinguishes browser and API flows, creation and expiry, browser CSRF state, forced reauthentication, requested assurance, and internal MFA context. Those fields expose the invariants that a frontend must preserve across a multi-step login. [Login-flow model](https://github.com/ory/kratos/blob/master/selfservice/flow/login/flow.go).
- **C2:** Login strategies share credential-type identification, UI-node grouping, login execution, and completed-authentication metadata. Separate interfaces handle linking and fast-login behavior, allowing methods to compose around a common flow representation. [Strategy interfaces](https://github.com/ory/kratos/blob/master/selfservice/flow/login/strategy.go).

### 19. [supertokens/supertokens-core](https://github.com/supertokens/supertokens-core)

**Language / role:** Java; application authentication, account, and session backend.

Study the relationship between account-linking invariants, database isolation, and online schema migration.

- **C1:** The schema rework describes explicit uniqueness reservations, locking for user operations, and staged transitions from legacy reads through dual writes to the migrated representation. Transition guards and resumable backfills are intended to preserve tenant-specific identifier and account-linking invariants during migration.
- **C3:** The design replaces dependence on serializable read-check-write behavior with constraint-backed reservations and targeted locking under read-committed isolation. It explains how to reduce serialization contention without simply weakening the required uniqueness guarantees.

**Entry point:** [Schema rework and migration design](https://github.com/supertokens/supertokens-core/blob/master/SCHEMA-REWORK.md). Treat this as the documented design and migration contract, rather than proof that every deployment has completed the migration.

### 20. [DuendeSoftware/products](https://github.com/DuendeSoftware/products)

**Language / role:** C#; product monorepo containing the embeddable **IdentityServer** OAuth 2.0/OIDC server. This is the verified current repository, rather than the redirected former IdentityServer repository. It is source-available under Duende's licensing terms.

Study refresh-token policy as an explicit tradeoff among replay detection, response loss, cleanup, and persistence cost.

- **C1:** Reusable and one-time refresh tokens have different failure behavior. Consumed timestamps, configurable deletion, and an overridable consumed-token acceptance method support controlled grace behavior when a legitimate client loses a response; cleanup timing must agree with that policy.
- **C2:** The refresh service is replaceable, while endpoint, validation, service, and store components are separated in the implementation. Applications can customize policy and persistence around a full protocol server engine. [Refresh-token behavior and extension points](https://docs.duendesoftware.com/identityserver/tokens/refresh/).

**Further entry point:** [IdentityServer implementation subtree](https://github.com/DuendeSoftware/products/tree/main/identity-server/src/IdentityServer).

### 21. [panva/node-oidc-provider](https://github.com/panva/node-oidc-provider)

**Language / role:** JavaScript; embeddable OAuth 2.0/OIDC authorization-server engine, rather than an OAuth client SDK.

Study a focused protocol implementation with replaceable application and persistence boundaries.

- **C1:** DPoP validation checks JWT type and algorithm, proof keys, time, nonce, HTTP method, normalized target URI, and token hashes. The implementation also invokes a replay-detection uniqueness check unless the relevant configuration allows replay. This provides an inspectable path through proof validation and replay policy. [DPoP validation](https://github.com/panva/node-oidc-provider/blob/main/lib/helpers/validate_dpop.js).
- **C2:** Account lookup and claims, interaction handling, storage adapters, and grant extensions let different applications host the same protocol engine. The documentation explains the short-lived interaction session and the need for a production persistence adapter. [Provider API and integration documentation](https://github.com/panva/node-oidc-provider/blob/main/docs/README.md).

### 22. [malach-it/boruta-server](https://github.com/malach-it/boruta-server)

**Language / role:** Elixir; OAuth 2.0/OIDC server and identity-management umbrella application. **The repository identifies itself as open beta.** Focus on `apps/boruta_identity` and its relationship to the protocol applications; the separate underlying Boruta library is not counted again.

Study authentication orchestration through Elixir callbacks and Ecto contexts, offering a different implementation community from the larger Java and Go systems.

- **C1:** WebAuthn registration and authentication maintain challenges and branch on enrolled credentials, enforcement policy, missing assertions, and verification failure. The code delegates cryptographic verification to Wax while retaining responsibility for flow state. [WebAuthn implementation](https://github.com/malach-it/boruta-server/blob/master/apps/boruta_identity/lib/boruta_identity/webauthn.ex).
- **C2:** The identity-provider context associates clients with configurable backends and templates; mutations invalidate cached provider data. These are reusable boundaries for different client identity experiences. [Identity-provider context](https://github.com/malach-it/boruta-server/blob/master/apps/boruta_identity/lib/boruta_identity/identity_providers.ex).

## Domain, network, and cloud identity infrastructure

### 23. [freeipa/freeipa](https://github.com/freeipa/freeipa)

**Language / role:** Python and C; integrated Linux/Unix identity and authentication system combining directory, Kerberos, certificate, and policy services. **Official substantive GitHub mirror; upstream source hosting is on Codeberg**, as described by the [project's source-contribution page](https://www.freeipa.org/page/Contribute/Code).

Study how an existing Kerberos environment can use an external OAuth identity provider without requiring every Kerberos service to become an OAuth application.

- **C1:** The external-IdP design bridges device authorization, Kerberos preauthentication, and a local RADIUS transport. It addresses identity association, replicated client credentials, and carrying oversized state through RADIUS attributes—concrete correctness boundaries between protocols. [External-IdP design](https://github.com/freeipa/freeipa/blob/master/doc/designs/external-idp/external-idp.md).
- **C2:** The bridge lets upstream identity verification feed Kerberos ticket issuance while existing services continue using Kerberos and existing host-access policy. The workshop documents using this facility with FreeIPA 4.10 or later. [Implemented integration walkthrough](https://github.com/freeipa/freeipa/blob/master/doc/workshop/12-external-idp-support.rst).

### 24. [krb5/krb5](https://github.com/krb5/krb5)

**Language / role:** C; MIT Kerberos, including the KDC and administration services. **Official GitHub mirror**, identified in [MIT's source-code guidance](https://k5wiki.kerberos.org/wiki/Getting_source_code).

Study authentication-server extensibility under a protocol whose exchanges can span multiple packets and different KDC instances.

- **C1:** KDC preauthentication plugins have separate server-wide and per-request state. The plugin guide warns that per-request state covers one AS request, not an entire multi-step exchange; cookies and callbacks handle cross-request state and asynchronous work. [KDC preauthentication interface](https://github.com/krb5/krb5/blob/master/doc/plugindev/kdcpreauth.rst).
- **C2:** Typed plugin operations for challenge data, verification, and reply data allow different preauthentication mechanisms to reuse KDC processing and database access.
- **C4:** The [1.18 release history from 2020](https://web.mit.edu/kerberos/krb5-1.18/krb5-1.18.html) records replay-cache and testing work, while the [current release notes](https://github.com/krb5/krb5/blob/master/README) discuss staged cryptographic retirement and mixed-version PAC compatibility. This is evidence of sustained compatibility and complexity management, not merely repository age.

### 25. [FreeRADIUS/freeradius-server](https://github.com/FreeRADIUS/freeradius-server)

**Language / role:** C; RADIUS authentication, authorization, and accounting server. The inspected **`master` branch is explicitly version 4 development code, not a released v4 product**, according to its [README](https://github.com/FreeRADIUS/freeradius-server/blob/master/README.md).

Study network authentication when requests can yield for backends, time out, conflict with later packets, or lose their originating socket.

- **C1:** The scheduler design gives file-descriptor events precedence over timer processing, checks whether a request's socket has closed or a conflicting packet has arrived, and models yield/resume behavior. Ordering is part of request correctness, not just throughput optimization.
- **C3:** Separate network and worker scheduling, runnable priority heaps, and CPU-cost-based worker selection expose the structure behind load distribution and contention control. The document also discusses when signaling should give way to polling.

**Entry point:** [Version 4 scheduler design](https://github.com/FreeRADIUS/freeradius-server/blob/master/doc/antora/modules/developers/pages/scheduler.adoc). Some passages are proposals; this entry describes a development design and does not claim every proposed mechanism is shipped.

### 26. [openstack/keystone](https://github.com/openstack/keystone)

**Language / role:** Python; OpenStack identity, token, and service-catalog server with federation. **Official substantive mirror of the OpenDev repository**, identified by the [repository README](https://github.com/openstack/keystone/blob/master/README.rst).

Study the boundary between authenticating a federated identity and authorizing a token for a particular cloud project.

- **C1:** Federated authentication first obtains an unscoped token; project-scoped access depends on subsequent authorization. Trusted identity-provider remote IDs are globally unique and associated with mappings, making issuer identity and attribute interpretation part of the trust boundary.
- **C2:** Protocol handling by the fronting HTTP server is separated from Keystone's identity mapping and token issuance. The same framework supports external SAML/OIDC sources and Keystone-to-Keystone federation, rather than embedding one upstream provider's account model.

**Entry point:** [Federation architecture, trust mappings, and scoped-token flow](https://docs.openstack.org/keystone/latest/admin/federation/introduction.html).

## Historical implementation worth studying

### 27. [babelouest/glewlwyd](https://github.com/babelouest/glewlwyd)

**Language / role:** C; OAuth 2.0/OIDC authentication server. **Archived and no longer maintained.** Its README explicitly says it should no longer be used in production. This entry is for historical implementation study.

Study a dynamically loaded C plugin architecture around authentication workflows and host-provided identity/session operations.

- **C1:** The plugin contract includes scope-sensitive session validation, authentication age, and notification that a session has been used, which can invalidate authentication-scheme state. It also specifies ownership of returned allocations and endpoint registration/removal, exposing both authentication and memory-lifecycle invariants.
- **C2:** Plugins implement a small lifecycle interface and receive host callbacks for endpoints, users, clients, scopes, and authentication schemes. The abstraction supports protocol and account workflows, though plugins are fully trusted rather than sandboxed. [Plugin interface and ownership contract](https://github.com/babelouest/glewlwyd/blob/master/src/plugin/README.md).

**Further entry point:** [OIDC implementation guide](https://github.com/babelouest/glewlwyd/blob/master/docs/OIDC.md), including multi-key selection and nested encrypted-token handling. Several documented protocol extensions were drafts; do not assume present-day interoperability from historical support claims.

## Coverage, search method, and limitations

Discovery used live web search across more than six distinct formulations, followed by reading official repository pages or GitHub API records and additional primary material. Search angles included:

- Broad self-hosted OIDC/SAML identity and access-management servers.
- Java enterprise and institutional federation, including CAS and OpenAM families.
- Go headless authorization servers, identity brokers, and application authentication services.
- Rust identity providers, replication designs, and resource-constrained authentication.
- PHP and Python SAML federation proxies and attribute-processing systems.
- C# and Node.js embeddable authorization-server engines and storage extension points.
- Account linking, refresh-token rotation, multitenancy, and online identity-schema migration.
- Kerberos, RADIUS, Unix identity integration, and cloud federation.
- Less prominent C and Elixir implementations, including maintenance and archive checks.

Successive searches increasingly returned already inspected projects, client SDKs, deployment recipes, small wrappers, or projects outside the GitHub scope. The list extends to 27 because application identity, browser federation, and domain/network authentication provide materially different engineering problems. Pure directory servers, general authorization-policy engines, OAuth client libraries, and reverse proxies without a substantive authentication/provider implementation were not included merely because they integrate with these systems.

The [LemonLDAP::NG GitHub repository](https://github.com/LemonLDAPNG/lemonldap-ng) was excluded after inspection found a pointer/verification repository rather than the server implementation; development is hosted on OW2 GitLab. Shibboleth was discovered, but no official substantive GitHub server mirror was verified during this search. New stubs, tutorials, and unmaintained projects without enough distinctive implementation evidence were excluded. Glewlwyd is an explicitly labeled historical exception because its C plugin contract provides a substantial, contrasting design. Fork ancestry alone was not treated as a separate project contribution.

Each retained canonical repository URL was opened directly or checked through the GitHub API. Each entry also uses an independently read implementation file, design document, or technical guide beyond the repository's headline description. Source links target the branches observed during research and can change. Documentation spanning different versions is identified where material; designs and beta/development code are not represented as uniformly deployed behavior. GitHub archival metadata and explicit project notices informed the status labels, but an unarchived repository is not by itself evidence of active maintenance.

No candidate repositories were cloned or executed, and no dependencies were installed. Performance criteria refer to inspected resource-management mechanisms, not reproduced benchmarks. Security properties described here are study topics supported by source material, not a certification of the full deployment. C4 is assigned only where release material across years supports it; the absence of C4 on another entry is a limit of this selection's evidence, not a statement that the project lacks history.
