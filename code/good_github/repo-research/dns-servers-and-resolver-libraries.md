# DNS servers and resolver libraries

Research date: **2026-10-09**.

This selection covers 23 repositories implementing authoritative DNS, recursive resolution, DNS forwarding, or reusable DNS protocol and resolver libraries. It spans infrastructure daemons, embedded and router deployments, and application libraries. DNS administration interfaces, reconnaissance tools, thin language bindings, and deployment packaging are outside the scope. Each repository page and at least one additional primary implementation or documentation source were opened and read. The engineering judgments below are grounded in those sources; they are a selection guide, not a claim that every component is uniformly exemplary.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial input, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or components serving multiple use cases.
- **C3 — Performance and structure:** real resource or latency constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by evidence of compatibility work, testing, or complexity management. Age alone does not qualify.

## Authoritative and recursive servers

### 1. [isc-projects/bind9](https://github.com/isc-projects/bind9)

**C — authoritative, recursive, and forwarding server; official archived mirror.** The repository describes itself as an archived mirror of ISC's GitLab upstream. It remains a substantial source tree for studying the boundaries between a DNS daemon, protocol libraries, and a general event and resource-management substrate. Do not interpret the GitHub mirror's status as the status of BIND upstream.

- **C1:** The developer guide explains contracts expressed through `REQUIRE`, `ENSURE`, and `INSIST`, explicit error results, buffer-region invariants, and reference-counted memory contexts. These expose the lifetime and shutdown problems beneath seemingly simple DNS request handling. [Developer guide](https://github.com/isc-projects/bind9/blob/main/doc/dev/dev.md).
- **C2:** The same guide separates `lib/isc` facilities such as tasks, timers, sockets, and buffers from `lib/dns` resolution, validation, and zone machinery, with `named` coordinating them. Study how shared infrastructure supports both server operation and DNS utilities. Some details in this guide are historical, so use it as a source-tree map rather than a current build recipe. [Library organization and conventions](https://github.com/isc-projects/bind9/blob/main/doc/dev/dev.md).

### 2. [PowerDNS/pdns](https://github.com/PowerDNS/pdns)

**C++ — monorepo containing PowerDNS Authoritative, Recursor, and dnsdist.** Counted once; these are distinct server and traffic-management subsystems within one repository. The authoritative subsystem is particularly instructive for separating DNS semantics from database and replication choices.

- **C1:** Secondary operation includes SOA serial checks, retry backoff, and additional signature-freshness checks for presigned zones. Zone transfers must become visible transactionally: the BIND backend only replaces a zone file after retrieval and parsing succeed. This provides a concrete study of avoiding partially published zones. [Modes of operation](https://docs.powerdns.com/authoritative/modes-of-operation.html).
- **C2:** Native database replication and DNS primary/secondary replication are separate operating models. Backend capabilities determine how storage, notification, and transfer behavior fit together, rather than forcing every deployment into one persistence model. The distinction is useful for engineers designing protocol services over interchangeable storage systems. [Backend and replication behavior](https://docs.powerdns.com/authoritative/modes-of-operation.html).

### 3. [NLnetLabs/nsd](https://github.com/NLnetLabs/nsd)

**C — authoritative-only server.** NSD offers a focused comparison with servers combining authoritative and recursive roles: its interesting complexity lies in serving published zones, accepting updates through transfers, and containing resource use.

- **C1:** The failure-diagnosis documentation describes failed reloads that leave existing data serving, recovery from truncated incremental-transfer journals, and failures involving DNSSEC denial-of-existence data. Study the separation between preparing replacement state and keeping the existing service available. [Reload and transfer failure diagnosis](https://nsd.docs.nlnetlabs.nl/en/latest/reference/log-diagnosis.html).
- **C3:** Serving processes, per-process sockets through `SO_REUSEPORT`, CPU affinity, TCP limits, and transfer pipelining make the resource model explicit. Transfer concurrency has memory and connection costs rather than being an unqualified throughput knob. [Configuration reference](https://nsd.docs.nlnetlabs.nl/en/latest/manpages/nsd.conf.html).

The configuration reference also records removed options; older descriptions of NSD's on-disk database should not be assumed to describe the current implementation.

### 4. [NLnetLabs/unbound](https://github.com/NLnetLabs/unbound)

**C — validating recursive caching resolver and embeddable resolver library.** Unbound is useful for understanding how a recursive resolver schedules dependent queries while retaining a clear boundary between iteration, validation, and shared state.

- **C1:** The original design describes response scrubbing, trust distinctions, and a mesh of dependent resolution operations. Its test strategy includes deterministic state-machine replay. The current source-tree test guide separately documents unit/state-machine tests and longer tests using authoritative test servers and malformed packets. [Original architecture presentation, 2008](https://unbound.docs.nlnetlabs.nl/en/latest/_downloads/c51efbbb62ca2d74d7eaa24990c71d74/ripe56_unbound_02.pdf), [test guide](https://github.com/NLnetLabs/unbound/blob/master/doc/README.tests).
- **C2:** Iterator and validator modules sit above reusable worker, event, and cache machinery. The dependency mesh is a useful abstraction to study when one apparently simple lookup requires several prerequisite lookups. [Original architecture presentation](https://unbound.docs.nlnetlabs.nl/en/latest/_downloads/c51efbbb62ca2d74d7eaa24990c71d74/ripe56_unbound_02.pdf).

The presentation is explicitly historical evidence of the architecture, not evidence for current benchmark numbers or every present-day implementation detail.

### 5. [CZ-NIC/knot](https://github.com/CZ-NIC/knot)

**C — Knot DNS authoritative server; official GitHub mirror of CZ.NIC's GitLab project.** Its zone journal is a particularly concrete example of reconciling protocol history, transactional storage, and bounded disk usage.

- **C1:** Zone loading accounts for SOA serial ordering and journal changesets, with publication contingent on successful loading and signing. Journal operations use LMDB transactions. These mechanisms make version ordering and atomic visibility central to correctness. [Zone loading and journal operation](https://www.knot-dns.cz/docs/latest/html/operation.html).
- **C3:** The journal chunks changesets to control fragmentation and imposes per-zone size and depth limits. Purging old history or merging changesets trades retained incremental-transfer history against storage pressure. Study this as a bounded history store whose compaction must preserve DNS transfer semantics. [Journal organization and limits](https://www.knot-dns.cz/docs/latest/html/operation.html).

The linked operations chapter is the best initial map from operator-visible behavior to the persistence and zone-update implementation.

### 6. [CZ-NIC/knot-resolver](https://github.com/CZ-NIC/knot-resolver)

**C, Lua, and Python — validating caching resolver; official GitHub mirror with GitLab upstream.** The repository's [contribution guide](https://github.com/CZ-NIC/knot-resolver/blob/master/CONTRIBUTING.md) identifies the upstream location. The C/Lua resolver and the version-6 Python manager provide two complementary architectural study subjects.

- **C1:** The manager distinguishes parsed, validated, and normalized configuration objects. Normalized and unnormalized forms have different types, while state changes converge at a synchronization point. Partial updates are applied before normalization. This makes configuration races and invalid intermediate state concrete engineering concerns. [Manager architecture](https://github.com/CZ-NIC/knot-resolver/blob/master/ARCHITECTURE.md).
- **C2:** Configuration processing, desired-state management, and service-manager backends are separate components; systemd and supervisord are backend implementations. [Manager architecture](https://github.com/CZ-NIC/knot-resolver/blob/master/ARCHITECTURE.md).
- **C3:** The resolver scales through separate workers, with a shared MVCC cache as an explicit exception to otherwise separated worker state. The manager automates worker lifecycle. Study the tradeoff between process isolation and shared cache reuse. [Repository architecture overview](https://github.com/CZ-NIC/knot-resolver).

### 7. [coredns/coredns](https://github.com/coredns/coredns)

**Go — extensible DNS server used for service discovery, authoritative answers, and forwarding.** CoreDNS is a good place to study a small request-processing abstraction that supports substantially different DNS roles.

- **C2:** Server selection uses the most specific matching zone, followed by a plugin chain. Build-time `plugin.cfg` ordering and runtime Corefile configuration are distinct; plugins may answer, delegate, or fall through. This makes extension ordering part of observable protocol behavior. [CoreDNS manual](https://coredns.io/manual/toc/).
- **C1:** Recent maintenance illustrates mutable response ownership and concurrency hazards: the 1.12.3 notes discuss cached-response copying, TTL refresh races, and cached connection closure. [1.12.3 release notes, 2025](https://coredns.io/2025/08/05/coredns-1.12.3-release/).
- **C4:** The 2020 release notes document IPv6 address handling and CNAME/TXT fixes, while the 2025 notes address cache concurrency and record case preservation. Together these show years of protocol compatibility and complexity management, rather than merely a long commit history. [1.6.7 release notes](https://coredns.io/2020/01/28/coredns-1.6.7-release/), [1.12.3 release notes](https://coredns.io/2025/08/05/coredns-1.12.3-release/).

### 8. [gdnsd/gdnsd](https://github.com/gdnsd/gdnsd)

**C — authoritative server with geographic routing and service-state-aware failover.** The official site identifies GitHub as the **primary stable source repository**, while future 4.x development is on Codeberg. This entry covers the retained stable GitHub implementation. It does not provide recursive service or DNSSEC. [Official project and repository status](https://gdnsd.org/).

- **C1:** The manual explains read-copy-update with quiescent-state-based reclamation, single-writer shared locations, and the difference between avoiding torn counter reads and supporting multiple atomic writers. These are unusually explicit concurrency invariants for a DNS daemon. [Implementation manual](https://github.com/gdnsd/gdnsd/blob/main/docs/Manual.md).
- **C3:** The request path uses worker threads without conventional locking in DNS request flow; publication and reclamation are arranged around readers. The manual also explains overlapping process replacement and socket handoff. Study how the design keeps update and lifecycle work away from frequently executed query handling. [Implementation manual](https://github.com/gdnsd/gdnsd/blob/main/docs/Manual.md).

### 9. [dnsimple/erldns](https://github.com/dnsimple/erldns)

**Erlang — authoritative DNS server, deployable independently or embedded as an OTP application.** This adds an actor-runtime perspective to the process- and thread-oriented C servers. The repository distinguishes zone storage, network listeners, and request processing.

- **C1:** Its request pipeline explicitly handles EDNS response-size constraints and messages containing multiple questions; the design documents processing the first question and emitting an event for that case. Study where wire-level limits become pipeline policy, and how unusual input becomes observable. [Design document](https://github.com/dnsimple/erldns/blob/main/DESIGN.md).
- **C2:** Decoded DNS messages move through composable transformation stages, with the server's zones, listeners, and pipeline usable as separate components. This supports both the packaged daemon and applications embedding authoritative service. [Design document](https://github.com/dnsimple/erldns/blob/main/DESIGN.md), [component and embedding overview](https://github.com/dnsimple/erldns).

Scope caveat: the inspected repository describes AXFR support as a stub, so it should not be treated as a feature-equivalent replacement for a full transfer-capable authoritative server.

### 10. [TechnitiumSoftware/DnsServer](https://github.com/TechnitiumSoftware/DnsServer)

**C# — authoritative and recursive DNS server with application extensions.** The relevant code is the DNS server and its extension interfaces, not merely the accompanying management interface. It is useful for studying a broad DNS service implemented on a managed runtime.

- **C1:** The changelog gives concrete examples of difficult resolver correctness: failure-cache entries shadowing CNAME data, outbound IPv6 resource exhaustion, out-of-bailiwick data handling, and bounded work in recursive resolution. These are useful starting points for tracing how cache semantics and request budgets interact. [Changelog, including 15.5 and 15.6](https://github.com/TechnitiumSoftware/DnsServer/blob/master/CHANGELOG.md).
- **C2:** DNS application interfaces and APP records allow custom authoritative answer logic, including split-horizon and geographic behavior. The repository separates application interfaces and bundled apps from core server machinery, making it possible to study extension boundaries in a combined authoritative/recursive service. [Repository layout and DNS application model](https://github.com/TechnitiumSoftware/DnsServer).

The changelog also records removal of costly automatic prefetch behavior: feature removal can be as instructive as feature addition when managing recursive workload.

## Local forwarding and encrypted DNS transport

### 11. [DNSCrypt/dnscrypt-proxy](https://github.com/DNSCrypt/dnscrypt-proxy)

**Go — local DNS proxy supporting encrypted upstream transports and policy processing.** This is a transport, routing, and operational-failure study; support for upstream DNSSEC does not mean that the proxy independently implements a validating recursive resolver.

- **C1:** Bootstrap lookups are distinguished from user queries, with documented rules for when plaintext bootstrap resolution is used. Certificate timing also has explicit startup behavior for devices without reliable clocks. These are concrete examples of resolving circular startup dependencies without silently treating every lookup alike. [Annotated configuration: bootstrap and certificates](https://github.com/DNSCrypt/dnscrypt-proxy/blob/master/dnscrypt-proxy/example-dnscrypt-proxy.toml).
- **C3:** The configuration documents weighted power-of-two upstream selection using observed latency and success rates, continuous estimation, bounded resolver refresh concurrency, and query timeouts that shrink as client load approaches a limit. Study the interaction between selection policy and overload control. [Annotated configuration: load balancing and resource controls](https://github.com/DNSCrypt/dnscrypt-proxy/blob/master/dnscrypt-proxy/example-dnscrypt-proxy.toml).

These are documented policies, not independently measured performance claims.

### 12. [pymumu/smartdns](https://github.com/pymumu/smartdns)

**C — local forwarding resolver with address probing and router-oriented deployment.** SmartDNS distinguishes the time to receive a DNS answer from the time to reach the endpoint that answer names, making it a useful counterpoint to simple fastest-upstream selection.

- **C3:** Response modes choose between returning the first DNS response, waiting for an address probe, or collecting candidates to select a faster endpoint. Ping and TCP probes can be staged or disabled for particular domains. The documentation explains the latency tradeoff rather than asserting one universal winner. [Speed-check and response modes](https://pymumu.github.io/smartdns/en/config/check-speed-mode/).
- **C1:** Expired-cache handling returns a short response TTL while requerying and reprobling in the background. Prefetch, stale retention, periodic persistence, and per-domain cache disabling make freshness and restart behavior explicit policies. Study the failure assumptions of serving old addresses, particularly for changing domains. [Cache behavior](https://pymumu.github.io/smartdns/en/config/cache/).

The selection does not endorse every operational generalization in the documentation; the concrete mechanisms and their tradeoffs are the evidence.

### 13. [AdguardTeam/dnsproxy](https://github.com/AdguardTeam/dnsproxy)

**Go — standalone forwarding proxy and reusable DNS proxy components.** It combines encrypted transport handling with caching, private-network resolution behavior, and request admission controls. Its implementation is useful beyond the command-line executable.

- **C1:** The proxy source separates general and private caches and has explicit EDNS Client Subnet handling in cache lookup and response processing. Study how client-dependent answers and private reverse lookups affect cache scope; treating all responses as globally interchangeable would lose necessary context. [Proxy implementation](https://github.com/AdguardTeam/dnsproxy/blob/master/proxy/proxy.go).
- **C3:** The same implementation exposes a maximum-goroutine admission mechanism and reusable byte buffers, alongside upstream and listener state. This provides a readable map of where concurrency and allocation are controlled in a network proxy. [Proxy implementation](https://github.com/AdguardTeam/dnsproxy/blob/master/proxy/proxy.go).

DNSSEC-related forwarding flags should not be confused with an independent DNSSEC validation engine. The repository overview is a useful companion for separating supported client/listener transports from internal resolver behavior.

## Resolver libraries and protocol toolkits

### 14. [c-ares/c-ares](https://github.com/c-ares/c-ares)

**C — asynchronous stub resolver library.** c-ares is especially valuable for studying a DNS implementation that must coexist with an application's event loop, threads, cancellation, and memory ownership rules.

- **C1:** `ares_getaddrinfo` callbacks may occur immediately, during event processing, or during cancellation/destruction; they may also run on another thread. The documentation states that callbacks execute with the channel lock held and distinguishes cancellation from destruction errors. These contracts expose reentrancy and lifetime hazards directly. [Address-resolution API contract](https://c-ares.org/docs/ares_getaddrinfo.html).
- **C2:** A channel supplies reusable asynchronous resolution state, while the API supplies structured address results, explicit freeing, and address sorting. Event-loop integration must account for file-descriptor changes immediately after initiating a request. Study how the library defines its responsibilities without owning the application's whole runtime. [Address-resolution API and integration notes](https://c-ares.org/docs/ares_getaddrinfo.html).

The repository also documents parser fuzzing, but this selection does not equate the existence of fuzzing with proof that all malformed-input cases are safe.

### 15. [getdnsapi/getdns](https://github.com/getdnsapi/getdns)

**C — structured DNS API with synchronous and asynchronous interfaces.** getdns is a useful alternative to address-only APIs: callers can retain resource-record structure, TTLs, and DNSSEC-related information. Recursive operation can use libunbound; it is not counted as a wholly separate recursive engine.

- **C1:** The API specification separates immediate call errors from asynchronous completion status, specifies callback invocation and cancellation behavior, and permits callbacks before the initiating call returns. Transaction identifiers and explicit response ownership make reentrancy and cleanup visible parts of the interface. [API specification](https://getdnsapi.net/documentation/spec/).
- **C2:** Contexts, dictionaries, lists, and binary values underpin general-record, address, reverse, and service queries. Event-library adapters are extensions rather than an assumption baked into every call, and synchronous variants return the same response model. Study how a C API preserves DNS semantics while remaining usable across application architectures. [Data structures and event integration](https://getdnsapi.net/documentation/spec/).

The specification is the first entry point; follow its contracts into the repository implementation when comparing asynchronous and synchronous paths.

### 16. [NLnetLabs/ldns](https://github.com/NLnetLabs/ldns)

**C — DNS packet, record, DNSSEC, resolver, and zone toolkit.** The repository explicitly places ldns in **maintenance mode since 2020**, with bug fixes but no planned major feature development, and points toward NLnet Labs' Rust domain library. It remains substantive study material rather than a thin binding.

- **C1:** The design separates wire representation, including compression, from structured resource data. RRset handling must preserve owner, type, and TTL relationships. This is a useful place to study the invariants that packet-format convenience APIs can otherwise conceal. [Library design](https://www.nlnetlabs.nl/documentation/ldns/design.html).
- **C2:** Packet, resource-record, resource-data-field, and zone structures are shared across parsing, presentation conversion, networking, and cryptographic functionality. The separation supports both reusable library calls and command-line DNS tools. [Structure and module design](https://www.nlnetlabs.nl/documentation/ldns/design.html).

The design document contains historical planning language; use it to understand decomposition, then consult actual interfaces before assuming a particular proposed detail is implemented.

### 17. [hickory-dns/hickory-dns](https://github.com/hickory-dns/hickory-dns)

**Rust — DNS protocol, resolver, and server crates in one monorepo.** This is the project formerly named Trust-DNS; old-name copies and forks are not separate entries. It offers a useful path from wire protocol components to an embeddable resolver and server applications.

- **C1:** DNSSEC validation requires following DNSKEY/DS trust relationships and handling authenticated denial of existence. The resolver additionally handles CNAME chains and dual-stack lookups. These are dependencies and protocol states, not merely serialization concerns. [Repository DNSSEC and subsystem overview](https://github.com/hickory-dns/hickory-dns), [resolver API](https://docs.rs/hickory-resolver/latest/hickory_resolver/).
- **C2:** Protocol, resolver, and server responsibilities are split into crates, and the resolver integrates with an asynchronous runtime rather than requiring the standalone server. Its API documents upstream connections, lookup results, and system-configuration support, including compatibility limitations. [Resolver crate documentation](https://docs.rs/hickory-resolver/latest/hickory_resolver/).

The inspected released resolver documentation is a versioned API snapshot; repository development and released crate behavior should not be assumed identical.

### 18. [NLnetLabs/domain](https://github.com/NLnetLabs/domain)

**Rust — DNS building blocks, message types, and resolver/server-related components.** The strongest reason to study domain is its representation and buffer model. The repository marks several higher-level facilities, including parts of DNSSEC support, as experimental; this is not a claim of complete feature parity with ldns or a full validating resolver.

- **C2:** The base library models domain names, records, parsed messages, and message construction over generic octet sequences. Borrowed storage, owned storage, and builders fit a common set of interfaces, allowing the same DNS types to serve different application memory models. [Base module architecture](https://docs.rs/domain/latest/domain/base/index.html).
- **C3:** Callers can choose storage suitable for allocation-sensitive environments, including fixed-size buffers and configurations without the standard library. Parsing and composing use complete message buffers because compression pointers refer within the message. Study the link between wire-format constraints and explicit storage choices. [Buffer, parsing, and composition model](https://docs.rs/domain/latest/domain/base/index.html).

### 19. [mirage/ocaml-dns](https://github.com/mirage/ocaml-dns)

**OCaml — DNS protocol library plus client, server, and resolver components.** Its pure core and multiple runtime adapters make it a distinctive comparison with libraries tied to one event loop. The repository supports the Internet class and intentionally has narrower scope in some protocol areas.

- **C1:** Resource-record mappings use generalized algebraic data types to preserve type relationships. The implementer's architecture account describes packet parsing with explicit errors and defenses around compression and offsets. Study how static types and checked wire decoding divide responsibility for correctness. [Implementer design account](https://hannes.robur.coop/Posts/DNS), [current component overview](https://github.com/mirage/ocaml-dns).
- **C2:** Pure protocol and state logic are separated from I/O, with distinct client/server/resolver packages and Unix, Lwt, and Mirage integrations. The same core can therefore support ordinary processes and unikernel applications. [Repository architecture and package boundaries](https://github.com/mirage/ocaml-dns).

The design article is historical rationale, while the repository describes present scope, including transport restrictions for transfer and update operations.

### 20. [rthalley/dnspython](https://github.com/rthalley/dnspython)

**Python — DNS toolkit covering stub resolution, messages, zones, updates, transfers, and cryptographic DNS operations.** Its versioned zone model makes it particularly useful for studying transactional data structures in a high-level protocol library.

- **C1:** A versioned zone permits multiple readers and one writer, publishes changes at commit, and exposes immutable committed versions. Direct mutation outside the required transaction path is rejected. The documentation also distinguishes ordinary zones, which do not provide the same thread-safety guarantees. [Zone and transaction model](https://dnspython.readthedocs.io/en/stable/zone-class.html).
- **C2:** High-level resolution coexists with reusable names, records, message structures, and zone abstractions. Versioned and ordinary zones offer different storage and concurrency semantics behind related interfaces. Study how users can select the necessary consistency model without replacing the entire DNS toolkit. [Zone API](https://dnspython.readthedocs.io/en/stable/zone-class.html), [toolkit scope](https://github.com/rthalley/dnspython).

A notable boundary: reads outside an explicit transaction do not guarantee that several successive calls observe one consistent version.

### 21. [dnsjava/dnsjava](https://github.com/dnsjava/dnsjava)

**Java — DNS toolkit with asynchronous lookup, resolver composition, caching, transfers, and DNSSEC validation.** dnsjava is useful for comparing a protocol-aware library with the much narrower host-lookup facilities built into a language runtime.

- **C1:** The repository documents bounds on CNAME traversal and DNSSEC work, including NSEC3 hashing and signature/key matching attempts. This makes adversarial computational cost part of resolver correctness, alongside trust-anchor and validation policy. [Resolver and DNSSEC configuration](https://github.com/dnsjava/dnsjava).
- **C2:** `LookupSession` offers asynchronous lookup results, `SimpleResolver` exposes asynchronous message exchange, and `ValidatingResolver` wraps resolver behavior with validation and trust anchors. The examples connect high-level lookup, low-level messages, and dynamic updates without collapsing them into one convenience API. [API examples](https://github.com/dnsjava/dnsjava/blob/master/EXAMPLES.md).

An experienced engineer can study both decorator-style composition and the boundary between successful transport, usable DNS answers, and successful cryptographic validation.

### 22. [alexdalitz/dnsruby](https://github.com/alexdalitz/dnsruby)

**Ruby — DNS protocol and resolver library with DNSSEC and synchronous/asynchronous APIs.** Its resolver documentation exposes scheduling and timeout semantics in more detail than a typical language-level DNS wrapper.

- **C1:** Retry rounds across upstreams distinguish packet timeouts from an overall query timeout. DNSSEC prerequisite lookups have their own timeouts, so total validation time can exceed the original query timeout. Study this explicit distinction between a transport deadline and a multi-query validation operation. [Resolver API and timeout semantics](https://www.rubydoc.info/gems/dnsruby/Dnsruby/Resolver).
- **C3:** Concurrent queries share an I/O event loop, and TCP queries can reuse connections through pipelining. Asynchronous completion uses a caller-supplied queue and query identifier, connecting scheduling choices to the application's result-processing model. [Resolver concurrency and connection behavior](https://www.rubydoc.info/gems/dnsruby/Dnsruby/Resolver).

The useful comparison is with event-loop-aware C libraries and Java/Rust futures, rather than with a thin wrapper around an operating-system host lookup.

### 23. [MichaCo/DnsClient.NET](https://github.com/MichaCo/DnsClient.NET)

**C# — reusable stub resolver library with synchronous and asynchronous lookup.** This is distinct from the Technitium server: it concentrates on embedding DNS queries, response handling, caching, and transport fallback inside .NET applications.

- **C1:** `LookupClient` distinguishes response-ID mismatches, parse failures, truncated replies, timeouts, and other failure cases when deciding whether to retry an upstream, switch servers, or invoke transport fallback. Request IDs are refreshed for retries. Study this as a concrete failure-policy matrix rather than a generic retry loop. [Lookup implementation](https://github.com/MichaCo/DnsClient.NET/blob/dev/src/DnsClient/LookupClient.cs).
- **C2:** Query settings, response objects, transport handlers, caching, and audit information surround a reusable lookup API. The implementation shows where caller policy enters the query pipeline and where common behavior remains centralized across synchronous and asynchronous use. [Lookup implementation](https://github.com/MichaCo/DnsClient.NET/blob/dev/src/DnsClient/LookupClient.cs), [library overview](https://github.com/MichaCo/DnsClient.NET).

The source entry point is the repository's `dev` branch, so inspect the corresponding release before relying on an exact behavior in a deployed package.

## Search coverage, exclusions, and limitations

Discovery used multiple live-web formulations rather than only searching a predetermined list. The principal angles were:

- Authoritative versus recursive architecture: searches combining BIND, PowerDNS, Knot, Unbound, authoritative servers, and resolver design.
- Less prominent authoritative implementations: gdnsd, Erlang/OTP DNS servers, YADIFA, and alternative small servers.
- C asynchronous and DNSSEC libraries: c-ares, getdns, ldns, callback contracts, and event-loop integration.
- Go and Rust implementations: plugin-based servers, reusable DNS crates, encrypted forwarding, caches, and upstream selection.
- Managed and dynamic languages: Java, Python, Ruby, and .NET resolver APIs and validation behavior.
- Functional implementations: OCaml/Mirage protocol libraries, typed records, pure cores, and runtime adapters.
- Router and local-resolver communities: SmartDNS, DNSCrypt, bootstrap behavior, stale caching, and endpoint probing.
- Cross-cutting follow-ups: transactional zone publication, MVCC, compression-pointer parsing, DNSSEC work limits, release history, and official mirror status.

Follow-up searches increasingly returned already-covered implementations, bindings, deployment wrappers, and operational tutorials. The retained list spans C, C++, Go, Rust, Erlang, OCaml, Python, Java, Ruby, and C#, and includes both widely deployed infrastructure and smaller substantive implementations. No star counts or numerical throughput claims were used as quality evidence.

**Repository-location decisions:** BIND and the two Knot projects are retained as official substantive GitHub mirrors and labeled accordingly. gdnsd remains the project's explicitly designated stable GitHub source; its future 4.x work is elsewhere. ldns is retained with its maintenance-mode status. [miekg/dns](https://github.com/miekg/dns) was inspected but excluded because its README directs version-2 development to Codeberg and limits the GitHub version to specific fixes with eventual archival planned. The moved version was not substituted with an unofficial mirror. Thin bindings and Trust-DNS/Hickory duplicates were excluded; PowerDNS and Hickory each count once despite containing several products or crates.

**Limits of the evidence:** This was documentation and source inspection, not a benchmark, security audit, or execution of repository tests. No candidate code was installed or run. Historical design documents are marked as such, and branch-head sources may differ from published releases. C1–C3 assessments are engineering inferences from the identified mechanisms; the explicitly claimed C4 evidence uses dated maintenance records. Except where a primary source establishes a specific status, inclusion does not assert an ongoing maintenance commitment or recommend deploying the repository unchanged.
