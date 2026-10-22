# Email transport and mailbox servers

Research date: **2026-10-09**

This selection covers 22 GitHub codebases implementing SMTP transport, durable delivery queues, IMAP/POP/JMAP mailbox services, integrated mail servers, or substantial embeddable SMTP server frameworks. It spans small-domain hosting, large delivery systems, relational and object-backed mailboxes, and several approaches to protocol extensibility. Deployment bundles, mail clients, webmail interfaces, and thin email-service API wrappers are outside the scope. A repository's inclusion identifies useful engineering material; it does not assert that every component is exemplary or suitable for a particular production deployment.

Criteria used below:

- **C1 — Difficult correctness:** protocol and storage invariants, concurrency, adversarial input, or recovery from failure.
- **C2 — Reusable abstractions:** substantial interfaces or components supporting multiple policies, protocols, or deployment arrangements.
- **C3 — Performance with structure:** explicit resource, latency, throughput, or storage constraints addressed through an understandable design.
- **C4 — Sustained evolution:** documented evolution together with compatibility work, testing, or deliberate complexity management.

Each repository identity was checked by opening its GitHub page or API record, and each entry has separately inspected primary implementation or design material. Criteria are justified by the cited material, rather than by stars or language choice. Source links also serve as reading entry points.

## Unix transport agents and their successors

### [vdukhovni/postfix](https://github.com/vdukhovni/postfix)

**C; general-purpose SMTP transport agent.** This is an **unofficial release-tracking GitHub mirror maintained by Postfix developer Viktor Dukhovni**, not Postfix's authoritative development origin. Its identity is explained in the maintainer's [mailing-list announcement](https://www.mail-archive.com/postfix-devel%40postfix.org/msg01283.html). Count it as Postfix, not as a separate implementation.

An experienced engineer can study how independently running delivery and queue services cooperate without turning the queue manager into a protocol implementation:

- **C2:** SMTP reception, local pickup, cleanup, address rewriting, queue management, and individual delivery agents have distinct responsibilities and interfaces. The [source-distributed architecture overview](https://github.com/vdukhovni/postfix/blob/master/postfix/html/OVERVIEW.html) traces both network and local submission through these services.
- **C3:** The queue manager maintains a bounded active queue and keeps deferred work separate. The design explicitly addresses memory exhaustion under heavy load and prevents a large deferred backlog from dominating ordinary queue access. These mechanisms are described in the same [overview](https://github.com/vdukhovni/postfix/blob/master/postfix/html/OVERVIEW.html).

### [OpenSMTPD/OpenSMTPD](https://github.com/OpenSMTPD/OpenSMTPD)

**C; SMTP server and transport agent.** This is the official **portable** OpenSMTPD repository. Its [README](https://github.com/OpenSMTPD/OpenSMTPD/blob/master/README.md) cautions that portable sources can lag OpenBSD's smtpd tree; that distinction matters when comparing implementations or fixes.

- **C1:** The [scheduler implementation](https://github.com/OpenSMTPD/OpenSMTPD/blob/master/usr.sbin/smtpd/scheduler.c) handles envelope insertion, commit, rollback, temporary failure, permanent failure, and delivery completion as separate events. Its in-flight accounting and explicit transitions make it a useful study in keeping asynchronous queue state consistent.
- **C2:** That implementation routes operations through a scheduler backend interface—insert, commit, rollback, update, hold, and release—while processing IPC messages separately. This provides a concrete example of separating scheduling policy and queue representation from the surrounding daemon protocol.

The useful reading question is how each delivery outcome changes both persistent work and the scheduler's view of that work.

### [notqmail/notqmail](https://github.com/notqmail/notqmail)

**C; a substantive continuation of qmail/netqmail.** This is counted once as its own evolving successor, rather than alongside copies of the original qmail source.

- **C1:** [INTERNALS.md](https://github.com/notqmail/notqmail/blob/main/INTERNALS.md) specifies queue states through concrete files and directory transitions, inode-based message identity, atomic linking, and separate recipient completion markers. It also explains crash recovery and unavoidable duplicate-delivery windows, making the failure model unusually inspectable rather than implying exactly-once SMTP delivery.
- **C4:** [CHANGES.md](https://github.com/notqmail/notqmail/blob/main/CHANGES.md) records work across 2019–2024 including unit and send-job tests, integer-overflow fixes, temporary-file race fixes, DNS changes, and modern C prototypes. This is evidence of maintaining an inherited architecture while repairing security and compatibility problems.

Study the relationship between filesystem operations and acceptance semantics, including the documented limitations of bounce logging.

### [albertito/chasquid](https://github.com/albertito/chasquid)

**Go; SMTP transport for individuals and small groups.** This is the author's substantive GitHub **mirror** of the project hosted at blitiri.com.ar. Its smaller scope makes the delivery lifecycle comparatively approachable.

- **C1:** The [queue implementation](https://github.com/albertito/chasquid/blob/main/internal/queue/queue.go) combines persisted envelopes, startup reload, asynchronous delivery, queue limits, expiration, and separate local/remote couriers. It exposes the coordination between disk state and concurrent delivery workers.
- **C4:** The [release notes](https://github.com/albertito/chasquid/blob/main/docs/relnotes.md) document evolution across 2020–2026, including an SMTP-smuggling fix and backport, fuzz-testing changes, queue `fsync` work, and TLS interoperability workarounds. These are concrete compatibility and correctness investments, not merely an old repository date.

Read the queue alongside the release notes to see where implementation assumptions were subsequently strengthened.

## Programmable and high-volume transport

### [haraka/Haraka](https://github.com/haraka/Haraka)

**JavaScript/Node.js; extensible SMTP server with outbound delivery.** Haraka is useful for studying how asynchronous policy hooks interact with acceptance and a real delivery queue.

- **C2:** The repository's [README](https://github.com/haraka/Haraka/blob/master/README.md) describes hooks across connection, greeting, envelope, message-data, and queue stages. This lets deployments assemble submission, filtering, and routing behavior from a common protocol engine.
- **C1:** The [outbound guide](https://github.com/haraka/Haraka/blob/master/docs/Outbound.md) specifies disk queuing, temporary-failure retries, bounce hooks, and forced-TLS behavior that defers delivery when TLS requirements cannot be met.
- **C3:** The same guide explains per-domain recipient grouping, the alternative of splitting recipients into separate deliveries, and per-process delivery concurrency. These expose a tangible tradeoff between connection reuse and independently managed recipient outcomes.

This is a transport framework and MTA, not an IMAP mailbox engine.

### [zone-eu/zone-mta](https://github.com/zone-eu/zone-mta)

**JavaScript/Node.js; outbound MTA and submission system.** Study its division between message-body storage, delivery coordination, and configurable sending zones.

- **C3:** The [README's architecture discussion](https://github.com/zone-eu/zone-mta/blob/master/README.md) describes streaming incoming bodies into MongoDB GridFS, computing the DKIM body hash during ingestion, and using Redis for coordination. Sending zones separate connection and source-IP policies rather than putting every destination behind one undifferentiated delivery pool.
- **C1:** The [queue locker](https://github.com/zone-eu/zone-mta/blob/master/lib/queue-locker.js) tracks lock ownership, expiration, zone membership, and per-domain concurrency. Owner-based cleanup and expiration are explicit mechanisms for releasing work after a worker ceases to hold it.

The implementation is particularly useful for examining the boundary between a durable message object and shorter-lived claims on the right to deliver it.

### [KumoCorp/kumomta](https://github.com/KumoCorp/kumomta)

**Rust with Lua policy; high-volume mail transport.** The architectural interest is in how delivery identities and policy dimensions map onto queues, rather than in headline throughput claims.

- **C2:** The [message-flow documentation](https://docs.kumomta.com/userguide/performance/messageflow/) distinguishes scheduled queues identified by campaign, tenant, and destination domain from ready queues identified by egress source and destination site. Lua hooks connect injection, authentication/signing policy, and delivery decisions to this structure.
- **C3:** Ready queues have bounded capacity; overflow returns to scheduled work with jitter. Multiple domains sharing destination MX infrastructure can share a site-level delivery constraint, avoiding the mistake of treating every domain as independent capacity. The same [flow description](https://docs.kumomta.com/userguide/performance/messageflow/) explains how temporary SMTP failures move work back into scheduling.

This is a strong entry point for studying admission control and resource isolation in a policy-rich delivery service.

### [postalserver/postal](https://github.com/postalserver/postal)

**Ruby; application mail delivery platform with SMTP and HTTP delivery paths.** The useful subsystem is its delivery-worker and database queue architecture, rather than its administration interface.

- **C3:** [Workers and background tasks](https://docs.postalserver.io/other/workers-and-background-tasks/) describes database-coordinated workers, configurable thread counts, connection-pool implications, batching deliveries to reuse destination SMTP connections, and worker affinity for particular IP pools.
- **C1:** The same document specifies ownership of queued work, retry backoff, graceful shutdown, and housekeeping. It also documents an important limitation: abruptly killed workers can leave locked items which are eventually removed as stale, rather than automatically recovered as normal retry work.

Postal is therefore a useful case study in the difference between graceful worker shutdown and crash recovery. The cited architecture applies to the documented v3 system, which coordinates through the database rather than a separate message broker.

### [smtpd/qpsmtpd](https://github.com/smtpd/qpsmtpd)

**Perl; plugin-oriented SMTP daemon with queue integrations.** It separates SMTP transaction handling from acceptance policy and the downstream queue implementation.

- **C2:** [README.plugins.md](https://github.com/smtpd/qpsmtpd/blob/master/README.plugins.md) specifies ordered hooks, explicit recipient acceptance decisions, configuration, and plugin lifecycle. Its warning about opening database handles before forking illustrates why extension interfaces must also define resource ownership.
- **C1:** The [changelog](https://github.com/smtpd/qpsmtpd/blob/master/CHANGELOG.md), including the 1.02 release dated 2026-10-01, documents anchored address parsing, parser/serializer round-trip checks, fuzz comparisons, and command limits measured in octets. These address adversarial protocol input rather than only ordinary message handling.
- **C3:** That release history also explains replacement of potentially quadratic parsing with linear parsing. This links performance engineering directly to resource-exhaustion resistance.

Unreleased changelog items should not be mistaken for behavior in the last released version.

## Mailbox storage and access engines

### [dovecot/core](https://github.com/dovecot/core)

**C; IMAP/POP mailbox server and mail-storage infrastructure.** The index layer is a particularly rich study of concurrent mailbox views and incremental synchronization.

- **C1:** The [index-format design](https://doc.dovecot.org/main/developers/design/indexes/index_format.html) explains a main index, transaction log, and cache with distinct update rules. Transaction records support atomic changes and synchronization, while explicitly marked validity state protects readers of partially populated cached data.
- **C3:** Fixed-size index records support direct access and memory mapping; transaction logs let sessions process changes rather than repeatedly scan entire mailboxes. Cache selection and lazy main-index replacement balance read cost against unnecessary writes. These mechanisms are described in the same design document.

The cited `main` documentation is development/pre-release documentation, not a promise that every detail applies unchanged to a chosen stable Dovecot release.

### [cyrusimap/cyrus-imapd](https://github.com/cyrusimap/cyrus-imapd)

**C; IMAP mailbox system with LMTP delivery and related access protocols.** Cyrus is useful for distinguishing mailbox placement, namespace routing, and replication as separate problems.

- **C3:** The [version 3.2 architecture document](https://www.cyrusimap.org/3.2/imap/reference/architecture.html) describes frontends, mailbox backends, and the mupdate directory used to present a common namespace across backends. Mailbox partitioning and replication serve different scaling and availability purposes.
- **C1:** Its replication discussion explains logged changes, synchronization clients, and idempotent replay. This is concrete material for studying how a mailbox service catches up a replica without assuming an update is delivered only once.

The document is explicitly versioned historical architecture. It is a useful guide to the codebase's design lineage, not evidence that every current deployment uses exactly that topology. Cyrus stores and serves mail; an external MTA commonly hands messages to it through LMTP.

### [dbmail/dbmail](https://github.com/dbmail/dbmail)

**C; database-backed mailbox server with IMAP and LMTP.** DBMail offers a useful contrast to mailbox engines built primarily around directory trees or bespoke index files.

- **C2:** The [architecture overview](https://dbmail.org/en/architecture/architecture-overview-of-dbmail/) describes protocol processes sharing a relational mail model. Message ingestion, Sieve processing, and mailbox operations reuse stored representations rather than each maintaining an unrelated message store.
- **C3:** The [email-store design](https://dbmail.org/en/architecture/email-store/) distinguishes logical messages, physical messages, MIME parts, and ordered part lists. Cached/extracted fields and indexed SQL access allow common operations without reparsing an entire raw message. The document includes actual schema relationships and query examples, making the representation inspectable.

Study how MIME reconstruction, per-mailbox flags, and synchronization sequence values fit the relational model. This is architectural evidence, not a claim that a particular SQL backend or workload will outperform filesystem storage.

### [zone-eu/wildduck](https://github.com/zone-eu/wildduck)

**JavaScript/Node.js; distributed mailbox service with IMAP/POP and an HTTP API.** WildDuck separates mailbox metadata and change notification from the larger message-body objects.

- **C1:** The [server architecture](https://docs.wildduck.email/docs/architecture/wildduck-server/) describes reconstructing a mailbox's UID view from MongoDB and applying journaled changes, with Redis notifications prompting sessions to update their views. This exposes the problem of maintaining protocol-visible message order while other sessions change a mailbox.
- **C3:** The same document explains independent frontend instances, MIME-tree metadata, separately stored attachments, and attachment deduplication in GridFS. The representation is designed to avoid repeatedly moving or parsing complete messages for operations that need only metadata or selected parts.

A productive reading path follows one mailbox change from database state through the journal to another open IMAP session.

### [migadu/sora](https://github.com/migadu/sora)

**Go; IMAP/POP3/LMTP/ManageSieve server using PostgreSQL and object storage.** This is included for its concrete storage and concurrency design; no claim of long-term maturity is needed for its qualification.

- **C1:** The [architecture document](https://github.com/migadu/sora/blob/main/docs/architecture.md) describes mailbox-level PostgreSQL advisory transaction locks for operations such as moves, plus trigger-maintained mailbox counters. These make consistency rules visible at the boundary between application code and database transactions.
- **C3:** The same document explains partial indexes on unexpunged messages, indexed UID access, maintained counts that avoid repeated aggregate scans, and a filesystem LRU cache for object bodies. LMTP ingestion stages bodies locally before asynchronous upload to S3.

That staging boundary is an important failure-mode study: asynchronous object upload should not be interpreted as proof that every accepted message is already durable in remote object storage.

### [grommunio/gromox](https://github.com/grommunio/gromox)

**C++; groupware backend containing mailbox storage, delivery, IMAP/POP3, and Exchange-compatible access services.** Count the monorepo once; the relevant parts here are its mailbox engine and mail access/delivery services.

- **C2:** The [exmdb provider manual](https://github.com/grommunio/gromox/blob/master/doc/exmdb_provider.4gx) describes a shared mailbox engine callable locally or through RPC. Its client interface can dispatch to either location, allowing multiple protocol services to reuse the same storage operations.
- **C3:** That manual documents prepared-statement caching, bounded concurrent schema upgrades, and search processing that periodically yields SQLite locks. These are explicit responses to storage contention and upgrade I/O pressure.

The [system introduction](https://docs.grommunio.com/admin/introduction/) distinguishes per-user SQLite mailbox data from MariaDB account metadata and explains how Postfix, local delivery, IMAP-support services, and Gromox fit together. Gromox should not be mistaken for every component of the larger grommunio distribution.

## Integrated transport and mailbox systems

### [stalwartlabs/stalwart](https://github.com/stalwartlabs/stalwart)

**Rust; integrated SMTP, IMAP, POP3, and JMAP server.** The outbound scheduler is a useful subsystem to inspect within this broader monorepo.

- **C1:** [Delivery schedules](https://www.stalw.art/docs/mta/outbound/schedule/) are evaluated per recipient, with separate retry timing, delayed-delivery notification intervals, and expiration rules. The documentation explicitly limits each delayed notification interval to one notification, making notification state part of the delivery lifecycle.
- **C3:** [Queue configuration](https://stalw.art/docs/mta/outbound/queue/) describes predeclared virtual queues with per-node delivery-thread allocations and concurrency limits. This allows traffic classes, such as local and remote deliveries, to receive distinct resource budgets instead of competing entirely within one pool.

Study how queue selection and per-recipient strategy interact when one message has destinations with different delivery outcomes. These cited documents describe current documented behavior at research time; they are not benchmark evidence.

### [foxcpp/maddy](https://github.com/foxcpp/maddy)

**Go; composable SMTP transport, authentication, and mailbox server.** The repository labels its **IMAP storage as beta**, which should remain visible when considering it as a study or deployment candidate.

- **C2:** The [module reference](https://maddy.email/reference/modules/) gives modules narrow responsibilities and lets named instances be shared across configuration paths. Storage, authentication, checks, and SMTP targets can be composed without duplicating every resource-owning component.
- **C1:** The [queue target reference](https://maddy.email/reference/targets/queue/) describes disk buffering, exponential retries, permanent-failure handling, and delivery-status notification routing. It also explains the consequence of omitting a bounce destination rather than silently assuming DSNs always exist.
- **C3:** The queue has an explicit maximum parallelism setting for delivery goroutines, connecting configuration-level composition to a bounded execution resource.

This is a compact case study in making a mail pipeline configurable while retaining explicit ownership of retries and final failure.

### [mjl-/mox](https://github.com/mjl-/mox)

**Go; integrated SMTP/IMAP server aimed at running a complete mail service.** Its account store makes mailbox protocol invariants and message representation visible in one substantial source file.

- **C1:** [store/account.go](https://github.com/mjl-/mox/blob/main/store/account.go) documents and implements UID validity, modification sequences, deleted-message history boundaries, mailbox counts, and account consistency checking used in tests. These are the kinds of invariants an apparently simple message delete or mailbox recreation can violate.
- **C3:** The same file describes per-account database metadata alongside message files. Generated header prefixes can be supplied by a message reader without rewriting the stored message body, avoiding a full-body copy for that transformation.

Read the store around UID validity and modification-sequence handling before following protocol commands into it. The qualification rests on these concrete storage mechanisms, not on a broad claim that an integrated server is automatically simpler or safer.

### [apache/james-project](https://github.com/apache/james-project)

**Java; modular mail server platform with transport, mailbox, and distributed-server implementations.** The relevant subsystems are its mailbox APIs, Mailet processing, protocol services, and durable queues; the monorepo counts once.

- **C2:** The [project README](https://github.com/apache/james-project/blob/master/README.adoc) describes separately assembled mailbox, protocol, and Mailet components and different server compositions. This offers a substantial example of reusing mail-processing abstractions across storage and deployment choices.
- **C1:** The accepted, implemented [distributed mail queue decision, ADR 0031](https://github.com/apache/james-project/blob/master/src/adr/0031-distributed-mail-queue.md), specifies browse boundaries, clock-skew allowance, deletion markers, and constraints on changing bucket/slice configuration.
- **C3:** That decision separates RabbitMQ dequeue notifications, a Cassandra time-series projection for browsing, and blob storage for message bodies. It explicitly addresses Cassandra tombstone pressure and workload distribution.

ADR 0031 dates from 2020 and records limitations and follow-up work. Treat it as a documented implementation/design milestone, not a complete account of every current James queue or its supported use cases.

## Embeddable SMTP server frameworks

These repositories provide substantive server implementations and extension points, but should not be confused with complete hosted mailbox products or turnkey durable MTAs.

### [gen-smtp/gen_smtp](https://github.com/gen-smtp/gen_smtp)

**Erlang; SMTP client/server library with SMTP and LMTP session machinery.** It is useful for studying protocol state inside an OTP-style concurrent service.

- **C2:** [gen_smtp_server_session.erl](https://github.com/gen-smtp/gen_smtp/blob/master/src/gen_smtp_server_session.erl) defines callback boundaries for greetings, authentication, TLS, envelope commands, message data, and reset/error handling. Policy is delegated to a callback module while the session engine owns protocol progression.
- **C1:** The implementation represents session and envelope state explicitly, distinguishes ordering and timeout errors, and handles LMTP's per-recipient responses. Embedded tests exercise behaviors including invalid STARTTLS arguments and successful TLS/session transitions.

This is a good source-level comparison with thread- or event-loop-based SMTP engines: investigate what is kept in each session process and what the callback implementation must guarantee. A durable queue is an application-level concern, not something implied by using this library.

### [aio-libs/aiosmtpd](https://github.com/aio-libs/aiosmtpd)

**Python; asyncio SMTP/LMTP server framework.** Its value extends beyond a toy listener because the API exposes protocol policy, connection lifecycle, and defensive resource limits.

- **C2:** The [SMTP API documentation](https://github.com/aio-libs/aiosmtpd/blob/master/aiosmtpd/docs/smtp.rst) distinguishes handlers, protocol subclassing, and the controller that manages server execution. Separate session and envelope objects give extensions concrete state boundaries.
- **C1:** The same document explains TLS/authentication gates, command and line limits, and SMTPUTF8-related decoding. In particular, it explains why an inactivity timeout alone cannot stop a peer that repeatedly sends valid commands and provides configurable command-call budgets. These budgets are an available control, not a claim that a finite budget is enabled by default.

Study how byte-oriented protocol constraints survive a Unicode-capable host language and how application hooks inherit responsibility for accepting and storing messages.

### [janestreet/async_smtp](https://github.com/janestreet/async_smtp)

**OCaml; asynchronous SMTP client/server and spool library.** The public library is described as a foundation of Jane Street's internal mail system; it is not the whole internal system.

- **C1:** [multispool_intf.ml](https://github.com/janestreet/async_smtp/blob/master/src/multispool_intf.ml) describes a multiprocess filesystem spool using write/`fsync`/rename sequences and exclusive file creation to reserve names. It explicitly distinguishes checked-out entries from direct access that provides no exclusive-ownership guarantee.
- **C2:** The spool is parameterized over metadata, body data, queue identity, name generation, and disk-operation throttling. Separately, [server_plugin_intf.ml](https://github.com/janestreet/async_smtp/blob/master/src/server_plugin_intf.ml) gives typed state/session/envelope interfaces and callbacks for SMTP command phases and message processing.

This is an unusually clear study in making filesystem ownership and SMTP policy part of the library interface. The separation of small metadata from larger bodies also helps explain why the spool API has more structure than a generic directory of files.

## Search coverage, exclusions, and limits

Discovery used more than six meaningfully different live web-search formulations. The search angles included:

- Traditional SMTP MTA architecture and queues: Postfix, OpenSMTPD, Exim, and qmail successors.
- IMAP mailbox storage and synchronization: Dovecot, Cyrus, SQL-backed DBMail, and object-backed services.
- Rust and Go integrated servers and small-domain transport: Stalwart, Maddy, Mox, and chasquid.
- Node.js SMTP plugins, outbound queues, and distributed mailbox designs: Haraka, ZoneMTA, and WildDuck.
- High-volume delivery and worker coordination: KumoMTA and Postal.
- Java and C++ mail/groupware backends: James and Gromox.
- Erlang, Python, Perl, and OCaml server frameworks, including less prominent reusable spool implementations.
- Specific implementation searches for queue ownership, crash recovery, IMAP indexes, PostgreSQL/S3 storage, protocol fuzzing, release compatibility, and design decisions.

Later language- and architecture-specific searches mostly returned already-covered projects, deployment wrappers, clients, and small or archived experiments; the OCaml search still contributed `async_smtp`. This supplied a reasonable diminishing-returns stopping point without treating the repository count as a quota.

**Exclusions:** [Exim/exim](https://github.com/Exim/exim) was inspected but excluded: its GitHub repository is archived and states that updates stopped being pushed there on 2025-12-26 after development moved elsewhere. Mailcow, Mailu, docker-mailserver, and similar deployment compositions were outside this implementation-focused selection; so were webmail clients, spam-filter-only projects, and thin hosted-service wrappers. Forks and monorepo subsystems were not counted as multiple independent entries.

**Evidence limits:** Repository metadata did not mark any of the 22 retained repositories archived when checked; this is not a claim of uniform current maintenance. The report flags the unofficial Postfix mirror, the author's chasquid mirror, OpenSMTPD's portable-tree caveat, Maddy's beta storage status, Dovecot development documentation, and the historical Cyrus/James design documents. Postfix's source-distributed overview was read directly; its maintainer's mirror announcement was available through live search, but direct retrieval of that mailing-list page failed. No candidate code was executed, no performance benchmarks were reproduced, and no claim of end-to-end correctness follows merely from documented architecture. The criteria assessments are engineering inferences grounded in the linked mechanisms, tests, and history.
