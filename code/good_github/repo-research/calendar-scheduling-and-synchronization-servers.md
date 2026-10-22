# Calendar scheduling and synchronization servers

Research date: **2026-10-09**.

This selection covers 22 GitHub repositories implementing calendar servers, the server-side engines and frameworks used to build them, cross-provider synchronization services, and appointment or resource-booking backends. It spans CalDAV/iTIP, groupware, encrypted synchronization, Exchange gateways, availability calculation, and reservation conflicts. Client-only applications, generic job schedulers, UI calendars, and standalone date parsers are outside the scope.

Repository identities were checked against their GitHub pages or repository API responses. Each entry also draws on opened implementation or design material beyond its README. The criteria below describe worthwhile engineering problems and study opportunities; they do not certify that every implementation is correct, secure, or suitable for deployment. Maintenance qualifications are explicit where material. Source links generally follow the inspected default branch and can change after this research date.

**Criteria legend**

- **C1 — Difficult correctness:** invariants, concurrency, time/recurrence semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or domain models serving multiple integrations, backends, or use cases.
- **C3 — Architectural performance work:** concrete resource, throughput, latency, or scaling constraints addressed in understandable code or design.
- **C4 — Sustained evolution:** evidence across years of compatibility, testing, migration, or complexity management, beyond repository age alone.

## Focused CalDAV servers and server frameworks

### 1. [Kozea/Radicale](https://github.com/Kozea/Radicale)

**Python; lightweight CalDAV/CardDAV server with filesystem storage.** A useful starting point for studying how a small server makes HTTP, authorization, calendar parsing, and durable storage boundaries visible without requiring a large groupware deployment.

- **C1:** The filesystem backend writes through a temporary file, flushes and optionally synchronizes it, replaces the destination, and synchronizes the containing directory. Its path conversion and collision checks make filesystem assumptions explicit. These are concrete crash-consistency and hostile-path concerns, rather than simply serializing an `.ics` file. Start with [`storage/multifilesystem/base.py`](https://github.com/Kozea/Radicale/blob/master/radicale/storage/multifilesystem/base.py).
- **C2:** The architecture separates request handlers from authentication, rights, storage, and web plugins, with documented replacement interfaces. This makes it useful for studying extensibility in a compact protocol server. See the architecture and plugin sections of [`DOCUMENTATION.md`](https://github.com/Kozea/Radicale/blob/master/DOCUMENTATION.md).
- **C3:** The [changelog](https://github.com/Kozea/Radicale/blob/master/CHANGELOG.md) documents elimination of quadratic collision checking in depth-one PROPFIND, reductions in repeated filesystem metadata calls, and limits on pathological recurrence expansion. These are specific workload and adversarial-cost improvements; no independent benchmark was performed here.

### 2. [jelmer/xandikos](https://github.com/jelmer/xandikos)

**Python; Git-backed CalDAV/CardDAV server.** Study the unusual choice of making Git blobs and history part of the calendar storage model, together with indexes that are built according to actual query demand. The README labels multi-user support experimental, which matters when evaluating its deployment scope.

- **C1:** The Git store validates imported objects, checks duplicate calendar UIDs and replacement ETags, and protects its UID maps against concurrent scanners. The implementation builds new mappings locally and swaps them under a lock, keeping expensive blob parsing outside that critical section. [`store/git.py`](https://github.com/jelmer/xandikos/blob/master/xandikos/store/git.py) exposes these invariants and the content-addressed parsed-object cache.
- **C2 / C3:** A separate index interface supports an in-memory implementation and an automatic index manager. The manager counts requests for unavailable index keys and adds indexes after a threshold, rather than indexing every possible property immediately. That is a reusable query/storage seam with a concrete read-performance tradeoff. See [`store/index.py`](https://github.com/jelmer/xandikos/blob/master/xandikos/store/index.py).

This is particularly informative alongside Radicale: similar external protocols lead to very different persistence, history, and query-cost decisions.

### 3. [sabre-io/dav](https://github.com/sabre-io/dav)

**PHP; embeddable WebDAV/CalDAV/CardDAV server framework.** This is a server construction library, rather than an administrator-ready calendar product. Its scheduling subsystem is a strong entry point into the difference between storing events and correctly processing invitations.

- **C1:** The scheduling plugin distinguishes organizer changes from attendee responses, compares old and new calendar objects, generates iTIP actions, and handles local inbox delivery and calendar updates. Cancellation, declining, free/busy access, and delivery status are separate paths. See [`CalDAV/Schedule/Plugin.php`](https://github.com/sabre-io/dav/blob/master/lib/CalDAV/Schedule/Plugin.php).
- **C2:** Scheduling is attached through server events and a delivery event that additional transports can implement. Local delivery and mail-based delivery can therefore share scheduling semantics while using different mechanisms. The same [plugin implementation](https://github.com/sabre-io/dav/blob/master/lib/CalDAV/Schedule/Plugin.php) also exposes the boundary between the server, calendar backend, and invitation broker.

The inspected implementation explicitly distinguishes implemented local/mail scheduling from unsupported iSchedule transport. That boundary is useful to study and should not be mistaken for universal scheduling-protocol coverage.

### 4. [sabre-io/Baikal](https://github.com/sabre-io/Baikal)

**PHP; deployable calendar/contact server built on sabre/dav.** Baïkal earns a separate place for application assembly, configuration, persistence choices, and upgrade management. It is not an independent implementation of sabre's protocol algorithms.

- **C2:** The server composition connects PDO-backed calendars and address books, principals, authentication modes, ACLs, property storage, WebDAV synchronization, scheduling, sharing, and optional invitation email. [`Core/Frameworks/Baikal/Core/Server.php`](https://github.com/sabre-io/Baikal/blob/master/Core/Frameworks/Baikal/Core/Server.php) shows how a reusable protocol framework becomes a configurable product.
- **C4:** The release history supplies specific multi-year compatibility evidence: [0.9.4, published in November 2023](https://github.com/sabre-io/Baikal/releases/tag/0.9.4), addressed MySQL/SQLite schema differences and PHP 8.2 compatibility; [0.12.0, published in August 2026](https://github.com/sabre-io/Baikal/releases/tag/0.12.0), addressed PHP 8.4/8.5 deprecations and dependency integration. The [upgrade guide](https://sabre.io/baikal/upgrade/) explains preserving configuration/data and handling older endpoint layouts.

Study this repository when the question is how to preserve an installed server across runtime and dependency changes, rather than how to implement recurrence from scratch.

### 5. [lennart-k/rustical](https://github.com/lennart-k/rustical)

**Rust; CalDAV/CardDAV server with a SQLite backend.** The useful focus is synchronization bookkeeping: a calendar mutation must become an ordered change that clients can later discover, including deletion. The project describes itself as under active development with rough edges; protocol completeness should be evaluated separately.

- **C1:** The SQLite implementation maintains calendar synchronization tokens and a change log within mutation transactions. Its incremental query uses a window function to select the latest change per object and separates changed objects from deletions. This is concrete evidence of attention to incremental-sync state, not merely an endpoint named “sync.” Start at [`store_sqlite/src/calendar_store/mod.rs`](https://github.com/lennart-k/rustical/blob/main/crates/store_sqlite/src/calendar_store/mod.rs).
- **C2:** Calendar reading, writing, and pruning are separate asynchronous traits. Their contract includes query prefiltering, change retrieval, deletion, restoration, and import, allowing protocol handlers to depend on a storage interface rather than SQLite details. See [`store/src/calendar_store.rs`](https://github.com/lennart-k/rustical/blob/main/crates/store/src/calendar_store.rs).

The separation is valuable for studying where a backend can optimize a calendar query and where the protocol layer must still establish the final semantics.

### 6. [robur-coop/caldav](https://github.com/robur-coop/caldav)

**OCaml; CalDAV server for Unix or MirageOS, with Git-backed persistence.** This provides a substantially different implementation community and deployment model from the PHP and Python servers. Its most instructive boundary is the typed filesystem abstraction used for WebDAV resources and properties.

- **C1:** A resource's content and WebDAV properties occupy separate stored files. The interface explicitly requires write and destroy operations to run inside a batch because both files must change together. This documents an important invariant and the caller's responsibility; it is not evidence that arbitrary callers automatically obtain atomicity. See [`webdav_fs.mli`](https://github.com/robur-coop/caldav/blob/main/src/webdav_fs.mli).
- **C2:** The interface distinguishes files and directories, returns typed errors through asynchronous operations, and builds the filesystem through an OCaml functor over a Mirage key-value backend extended with batching. The [implementation](https://github.com/robur-coop/caldav/blob/main/src/webdav_fs.ml) handles property sidecars, directory listings, timestamps, and digest-derived ETags behind that seam.

Study it for how module signatures can communicate persistence obligations and make the same server logic usable in conventional and unikernel environments.

### 7. [emersion/go-webdav](https://github.com/emersion/go-webdav)

**Go; WebDAV/CalDAV/CardDAV library with server handlers and backend contracts.** This is another explicit scope exception: a reusable server library, not a turnkey synchronization service. Its compact CalDAV handler is useful for examining protocol-to-domain translation.

- **C1:** Filter decoding rejects contradictory combinations such as `is-not-defined` with time/text constraints, and mutually exclusive property/component selection forms. Conditional-write options are passed to the backend, making the location of concurrency-precondition enforcement visible. See [`caldav/server.go`](https://github.com/emersion/go-webdav/blob/master/caldav/server.go).
- **C2:** The context-aware backend interface covers calendar discovery, retrieval, creation, object queries, writes, and deletion, while HTTP/XML handling lives in the handler. The same [source file](https://github.com/emersion/go-webdav/blob/master/caldav/server.go) is a concise entry point into this storage-independent design.

Do not infer complete CalDAV scheduling or synchronization support from the repository name. The inspected handler covers calendar query and multiget and contains unimplemented property-selection work. The abstraction and validation code qualify it; complete protocol coverage is not a selection claim.

## Groupware and larger calendar engines

### 8. [Bedework/bw-calendar-engine](https://github.com/Bedework/bw-calendar-engine)

**Java; the core Bedework calendar engine.** This repository contains the engine and scheduling machinery, rather than every Bedework deployment component. It is a useful study target for enterprise calendaring where invitation processing, persistent state, and protocol integration need distinct layers.

- **C1:** Implicit scheduling handles deleted events, recurring masters with overrides, removed attendees, organizer cancellations, and attendee replies. It can generate individual cancellations for removed attendees while avoiding redundant work for people who already declined. See [`ImplicitSchedulingHandler.java`](https://github.com/Bedework/bw-calendar-engine/blob/master/bw-calendar-engine-impl/src/main/java/org/bedework/calsvc/scheduling/ImplicitSchedulingHandler.java).
- **C2:** The handler hierarchy deliberately splits attendee, organizer, and implicit scheduling responsibilities; its comments explain the complexity-management reason for that division. At repository level, API, CalDAV integration, read/write core, indexing, and inbound/outbound scheduling are distinct [engine modules](https://github.com/Bedework/bw-calendar-engine/tree/master).

An experienced engineer can trace one meeting change through the domain handlers rather than treating CalDAV, storage, and invitation delivery as one large request function. Related Bedework repositories are not counted as additional independent projects here.

### 9. [apple/ccs-calendarserver](https://github.com/apple/ccs-calendarserver)

**Python/Twisted; historical Apple CalendarServer. Archived in February 2020.** Retained as a distributed-systems study artifact, not a maintained deployment recommendation. Its design documents are unusually useful for understanding how calendar sharing interacts with partitioned ownership.

- **C2:** The [cross-pod design](https://github.com/apple/ccs-calendarserver/blob/master/doc/Developer/CrossPodDesign.md) presents remote store objects through interfaces resembling local objects, using a conduit for inter-pod calls. It addresses calendar owners versus sharees, copies of sharing bindings, and pods running different software versions.
- **C3:** That design avoids broadcasting to discover shared calendars. Separately, the [master/worker design](https://github.com/apple/ccs-calendarserver/blob/master/doc/Developer/MasterWorker.md) distributes connections according to active worker load, limits outstanding requests, pauses acceptance when saturated, and tracks worker termination and restart. These are explicit backpressure and failure-recovery mechanisms.

The lesson is not merely “add workers”: application ownership rules determine routing, while a separate process-control layer governs overload. The repository's archived status bounds the relevance of its dependencies and operational assumptions.

### 10. [nextcloud/server](https://github.com/nextcloud/server)

**PHP; the DAV calendar backend inside the Nextcloud server monorepo.** The relevant subsystem is `apps/dav`, not the separately developed calendar web interface. Study how calendaring fits into a broader account, sharing, database, and event-dispatch platform.

- **C1:** The backend groups object creation, duplicate-UID checking, stored metadata, change tracking, and related updates inside atomic operations. Incremental synchronization distinguishes initial enumeration from changes since a token, captures a token boundary, and interprets deletion records. See [`CalDavBackend.php`](https://github.com/nextcloud/server/blob/master/apps/dav/lib/CalDAV/CalDavBackend.php).
- **C3:** Calendar queries first use stored component and occurrence-bound metadata to reduce the candidate set, then perform calendar-aware postfiltering when SQL bounds alone cannot establish the answer. The same [backend source](https://github.com/nextcloud/server/blob/master/apps/dav/lib/CalDAV/CalDavBackend.php) exposes both stages and their responsibilities.

This is a strong example of why recurring-event search needs both database-friendly approximations and a semantically stronger final check. The monorepo is counted once, and no claim is made about the quality of unrelated Nextcloud subsystems.

### 11. [cyrusimap/cyrus-imapd](https://github.com/cyrusimap/cyrus-imapd)

**C; mail server with substantive HTTP CalDAV support.** Its calendar implementation is interesting precisely because it reuses a mature mailbox-oriented storage system rather than introducing an entirely separate calendar database.

- **C2:** Per-user DAV databases map resource URLs to mailbox/message identifiers and store protocol-specific metadata such as calendar UIDs, lock information, scheduling tags, and time bounds. The official [database architecture documentation](https://www.cyrusimap.org/imap/concepts/deployment/databases.html) explains the division between mailbox content and DAV lookup metadata.
- **C3:** The documentation identifies calendar-UID indexing as necessary for scheduling lookups across collections. This is a specific access-path requirement imposed by invitation semantics. [`imap/http_caldav.c`](https://github.com/cyrusimap/cyrus-imapd/blob/master/imap/http_caldav.c) is the implementation entry point for the HTTP/CalDAV layer that uses this machinery.

Study the impedance mismatch between a calendar resource and a mailbox message, and how auxiliary indexes let the protocol expose a different resource model without replacing the underlying storage architecture. This entry concerns the calendar subsystem, not just Cyrus's reputation as an IMAP server.

### 12. [Alinto/sogo](https://github.com/Alinto/sogo)

**Objective-C; SOGo groupware with CalDAV and ActiveSync integration.** This adds a different language ecosystem and an architecture built around existing mail, directory, and database services.

- **C2:** The appointment-folder implementation shares persistent folder machinery across events and tasks while handling ownership, sharing, free/busy inclusion, and calendar object access. [`SOGoAppointmentFolder.m`](https://github.com/Alinto/sogo/blob/master/SoObjects/Appointments/SOGoAppointmentFolder.m) is a useful entry point into how groupware concepts become protocol-visible resources.
- **C3:** The [installation and configuration guide](https://github.com/Alinto/sogo/blob/master/Documentation/SOGoInstallationGuide.asciidoc) explains worker counts, listening backlogs, caching, and ActiveSync synchronization/ping intervals and response-size limits. Long-lived synchronization requests consume resources differently from ordinary short HTTP requests; those controls expose the resulting capacity tradeoffs.

An engineer can connect the calendar object model to actual operational constraints instead of studying only a protocol handler. The performance evidence here is architectural and configuration-level; it does not establish a throughput comparison with the other servers.

### 13. [stalwartlabs/stalwart](https://github.com/stalwartlabs/stalwart)

**Rust; mail and collaboration server with a groupware calendar subsystem.** Counted once as a monorepo. The relevant code lies under `crates/groupware`, where scheduling and indexed persistent objects have distinct responsibilities.

- **C1:** Event updates compare old and new iTIP snapshots, distinguish organizer and attendee operations, reject organizer mismatches, and handle cancellation when a previously scheduled event ceases to be scheduled. The rules are explicit error-producing branches in [`scheduling/event_update.rs`](https://github.com/stalwartlabs/stalwart/blob/main/crates/groupware/src/scheduling/event_update.rs).
- **C2:** Calendar containers and calendar events implement common indexing/object contracts for ACLs, quotas, change logging, and searchable properties. Versioned serialization and property hashes participate in this common machinery. See [`calendar/index.rs`](https://github.com/stalwartlabs/stalwart/blob/main/crates/groupware/src/calendar/index.rs).

The study opportunity is the connection between invitation state transitions and a shared object/index layer. The mail server's broader history should not be used as a substitute for separately evaluating the maturity of its newer calendar functionality.

### 14. [EGroupware/egroupware](https://github.com/EGroupware/egroupware)

**PHP; groupware monorepo with a substantial calendar business layer.** This is valuable for studying the accumulation of real scheduling rules: recurrence exceptions, participant changes, resource conflicts, access control, notifications, and synchronization timestamps.

- **C1:** The calendar update layer handles those concerns together and explicitly documents user-time versus server-time conversion conventions. It also documents a resource-capacity limitation: adding overlapping reservations can overcount demand when two reservations each overlap the proposed event but do not overlap each other. That is a concrete interval-aggregation edge case, not proof of complete correctness. See [`class.calendar_boupdate.inc.php`](https://github.com/EGroupware/egroupware/blob/master/calendar/inc/class.calendar_boupdate.inc.php).
- **C2:** The same [business-layer source](https://github.com/EGroupware/egroupware/blob/master/calendar/inc/class.calendar_boupdate.inc.php) describes separation from request/UI handling and storage, with updates, authorization, recurrence handling, and notifications exposed through reusable domain operations.

The code is useful both for its abstractions and for its candid record of difficult boundary cases. Readers should preserve that distinction rather than interpreting an extensive implementation as an assurance that all conflict checks are exact.

### 15. [Zimbra/zm-mailbox](https://github.com/Zimbra/zm-mailbox)

**Java; Zimbra mailbox server, including its calendar engine.** The recurrence subsystem is a focused entry point into a much larger collaboration server. It makes the relationships among a recurring rule, explicit dates, exceptions, cancellations, invitations, and timezone metadata inspectable.

- **C1:** Recurrence expansion accepts a bounded time window and accounts for exception and cancellation structures. The code tracks invitation identity through recurrence objects and warns that assigning an invitation ID across a whole chain is only safe for a single-invitation recurrence. This is a subtle provenance invariant. See [`mailbox/calendar/Recurrence.java`](https://github.com/Zimbra/zm-mailbox/blob/develop/store/src/java/com/zimbra/cs/mailbox/calendar/Recurrence.java).
- **C2:** The recurrence interface and composite forms provide shared expansion, metadata encoding/decoding, timezone mapping, and XML representation across single dates and repeating structures. The same [implementation](https://github.com/Zimbra/zm-mailbox/blob/develop/store/src/java/com/zimbra/cs/mailbox/calendar/Recurrence.java) shows a reusable domain model rather than logic tied to one HTTP endpoint.

Study this entry for recurrence representation and persistence. The repository's mailbox, search, and transport code is broader than the calendar slice evaluated here.

## Synchronization services and protocol gateways

### 16. [etesync/server](https://github.com/etesync/server)

**Python; Etebase server used by EteSync's encrypted calendar/contact/task synchronization.** This is not a conventional plaintext CalDAV store. The [EteSync project](https://www.etesync.com/) establishes its calendar role, while the server implements generic encrypted collections. The repository was not archived when checked, but its last observed push was in July 2024; current maintenance should not be assumed.

- **C1:** Collection writes enforce revision ETags and synchronization-token preconditions, use transactions and row locks, check dependencies, and roll back grouped failures. Change reporting is deferred until after commit. These mechanisms are visible in [`fastapi/routers/collection.py`](https://github.com/etesync/server/blob/master/etebase_server/fastapi/routers/collection.py).
- **C2:** Collections, items, revisions, chunks, membership, and deletion markers form a reusable synchronization protocol above encrypted payloads. The same [router implementation](https://github.com/etesync/server/blob/master/etebase_server/fastapi/routers/collection.py) shows how the server can enforce synchronization consistency without implementing the payload's calendar semantics.

This is useful for separating two different correctness problems: consistent encrypted-object replication on the server and event/recurrence interpretation by clients.

### 17. [mguessan/davmail](https://github.com/mguessan/davmail)

**Java; DavMail CalDAV-to-Exchange gateway. Official substantive GitHub mirror synchronized with the project's main Subversion repository.** That relationship is stated in the repository README; the [official project site](https://davmail.sourceforge.net/) describes the gateway. It is not a standalone authoritative calendar store.

- **C1:** The CalDAV connection handler forwards conditional-write headers, treats scheduling-inbox deletion differently from ordinary event deletion, and distinguishes individual missing objects in multiget responses from connection/SSL/timeout failures that must propagate. It also contains concrete calendar-client interoperability handling. See [`CaldavConnection.java`](https://github.com/mguessan/davmail/blob/master/src/java/davmail/caldav/CaldavConnection.java).
- **C2:** The handler translates calendar resource operations through an Exchange-session abstraction, separating CalDAV request/response behavior from provider operations. The [release notes](https://github.com/mguessan/davmail/blob/master/RELEASE-NOTES.md) document Exchange/Graph-specific recurrence, invitation, duplicate-event, and retry work, illustrating the breadth behind that boundary.

Study the semantic translation and failure mapping, not just HTTP forwarding. Provider API differences and long-lived calendar-client quirks make a gateway substantially more demanding than a generated API wrapper.

### 18. [ridafkih/keeper.sh](https://github.com/ridafkih/keeper.sh)

**TypeScript; server-side cross-provider calendar synchronization service.** This is the upstream repository; an older search-visible fork was excluded. It separates ingestion from destination synchronization across providers such as Google, Outlook, and CalDAV, with source/destination mappings and explicit ownership of created events.

- **C1:** The distributed synchronization lock uses Redis scripts for atomic acquisition, signaling, renewal, and holder-checked release. It handles mutation preemption, cancellation while acquisition is in flight, and restoration of a preceding waiter when a newer waiter is canceled. These are unusually concrete concurrency concerns in [`sync-lock.ts`](https://github.com/ridafkih/keeper.sh/blob/main/packages/sync/src/sync-lock.ts).
- **C3:** Provider-specific distributed rate limits share Google ingestion/push budgets and account for Outlook mailbox limits. The orchestration also calculates authoritative coverage before permitting reconciliation and guards retry updates against stale runs. See [`sync-user.ts`](https://github.com/ridafkih/keeper.sh/blob/main/packages/sync/src/sync-user.ts).

This is a strong study target for synchronization under provider quotas and concurrent user edits. The rate-limit and locking design provides evidence of real constraints, not evidence of a measured maximum deployment size.

## Appointment booking and resource reservation backends

### 19. [calcom/cal.diy](https://github.com/calcom/cal.diy)

**TypeScript; Cal.diy appointment-scheduling application and backend.** At research time, `calcom/cal.com` redirected to this repository. Its README describes a community fork with enterprise features removed and recommends personal/non-production use. It is counted once under the verified current URL; the capabilities of commercial Cal.com are not attributed to it.

- **C1:** Availability calculation combines working schedules, selected external calendars, existing bookings, buffers, booking/duration limits, timezone choices, and rescheduling exclusions. Busy-time retrieval failures have an explicit result path, and available ranges are computed by subtracting busy intervals. See [`getUserAvailability.ts`](https://github.com/calcom/cal.diy/blob/main/packages/features/availability/lib/getUserAvailability.ts).
- **C2:** A shared calendar-service base implements calendar-provider operations, event creation/update, attendee mapping, timezone-aware iCalendar construction, and conditional updates. It separates those concerns from the availability service. See [`CalendarService.ts`](https://github.com/calcom/cal.diy/blob/main/packages/lib/CalendarService.ts).

Inherited source may still reference richer scheduling concepts; that alone does not establish that removed enterprise product features remain supported. The value here is studying the inspected scheduling and provider-integration code within the fork's stated scope.

### 20. [alextselegidis/easyappointments](https://github.com/alextselegidis/easyappointments)

**PHP; appointment-booking server for service providers.** A useful counterpoint to general groupware: its core question is which service-duration slots remain bookable under provider schedules, existing appointments, capacity, and notice rules.

- **C1:** Availability calculation considers working-plan exceptions, breaks, unavailability, existing appointments, multiple-attendant capacity, provider timezone, advance-notice limits, and exclusion of the appointment being rescheduled. [`Availability.php`](https://github.com/alextselegidis/easyappointments/blob/main/application/libraries/Availability.php) makes the interaction of these constraints inspectable.
- **C2:** The backend exposes separate resources for providers, services, appointments, unavailabilities, working-plan exceptions, blocked periods, and related administration through a documented API. The [OpenAPI specification](https://github.com/alextselegidis/easyappointments/blob/main/openapi.yml) is an entry point into that reusable domain boundary, rather than treating the booking form as the entire system.

The interesting abstraction is the distinction between business availability rules and a particular booking interface. Inspecting the API alongside the availability implementation helps reveal which rules are domain operations and which are presentation choices.

### 21. [LibreBooking/librebooking](https://github.com/LibreBooking/librebooking)

**PHP; resource reservation and scheduling server.** The README identifies its lineage from the last open Booked release in 2020 and describes subsequent independent development. It is retained as a substantively evolved project, not counted alongside the original as a duplicate implementation.

- **C1:** Conflict identification works over reservation-series instances and resources, handles buffered ranges and endpoint adjacency, excludes relevant self/modified/deleted reservations, and distinguishes reservation conflicts from blackouts. See [`ReservationConflictIdentifier.php`](https://github.com/LibreBooking/librebooking/blob/develop/lib/Application/Reservation/ReservationConflictIdentifier.php). The presence of capacity logic is not a claim that every interval-capacity case has been proved correct.
- **C2:** Validation construction distinguishes create, update, delete, approve, check-in, and check-out operations. Plugins provide rule sets, with explicit fallbacks for plugin methods absent from older implementations. [`ReservationValidationFactory.php`](https://github.com/LibreBooking/librebooking/blob/develop/lib/Application/Reservation/Validation/ReservationValidationFactory.php) exposes a reusable reservation-policy extension point.

This is particularly useful for rooms, equipment, and other shared resources, where recurrence, blackout windows, approval, and capacity differ from a simple one-person appointment. Consult the current repository's operational and security notices before any deployment decision.

### 22. [fmeringdal/nettu-scheduler](https://github.com/fmeringdal/nettu-scheduler)

**Rust; calendar and appointment-scheduling REST backend. Historical/inactive study selection.** The repository was not archived when checked, but its last observed push was in June 2022. Retention reflects the substance of its domain code, not a claim of current support.

- **C1:** Slot generation requires the entire requested duration to fit a free interval, aligns candidate starts to a requested interval, merges compatible user availability for services, and groups resulting slots by timezone/date. Included unit tests exercise boundary fits, disjoint periods, and multiple users. See [`domain/src/booking_slots.rs`](https://github.com/fmeringdal/nettu-scheduler/blob/master/scheduler/crates/domain/src/booking_slots.rs). These tests support specific algorithmic cases, not comprehensive DST correctness.
- **C2:** The [scheduler crates](https://github.com/fmeringdal/nettu-scheduler/tree/master/scheduler/crates) separate domain logic, API handling, API structures, infrastructure, and utilities. Account, user, service, event, and calendar concepts support embedding scheduling behind another application instead of prescribing a single booking UI.

Study it for the shape of a standalone scheduling API and its interval algorithms. Treat external-provider integrations and dependency compatibility as historical until separately revalidated.

## Search coverage, exclusions, and limits

Discovery used live web search across more than six distinct formulations, followed by repository/API identity checks and opened primary sources. Search angles included standalone CalDAV implementations; Java enterprise calendaring and Apple CalendarServer; mail/groupware servers with calendar subsystems; Rust, Go, and OCaml implementations; appointment booking and resource capacity; encrypted calendar synchronization; Exchange gateways; Git-backed calendar storage; and cross-provider synchronization services. Searches deliberately included smaller projects as well as established platforms. Later queries increasingly returned the same repositories, clients, frontends, generic schedulers, or thin wrappers; Xandikos and the upstream Keeper service were the final substantive additions.

The selection covers nine principal implementation languages and several persistence models: ordinary files, Git, relational stores, mailbox-backed resources, and opaque encrypted collections. Frameworks are explicitly labeled. Baïkal and sabre/dav share implementation lineage but expose different substantive study areas: product integration/upgrades versus protocol and scheduling machinery. Groupware monorepos are counted once, with the relevant calendar subsystem identified.

Important exclusions and qualifications:

- **DAViCal:** excluded from this GitHub-specific selection because its [official developer instructions](https://wiki.davical.org/index.php?title=Developer_Setup) point development to GitLab and state that old GitHub mirrors are no longer updated. This is not a judgment about the quality of DAViCal itself.
- **Client-only or UI-only projects:** DAVx5, vdirsyncer, khal, client CalDAV libraries, and the Nextcloud calendar frontend were not substituted for servers. Generic cron/workflow schedulers and standalone iCalendar parsers were also excluded.
- **Duplication:** older Keeper forks were excluded in favor of the upstream; Cal.com's observed redirect is represented by one Cal.diy entry; additional sabre-based administration layers were not added merely to enlarge the list. DavMail's official substantive mirror is labeled as such.
- **Maintenance:** archived Apple CalendarServer and quiet EteSync/Nettu repositories are clearly qualified. Repository activity alone was not used to award C4. Baïkal's C4 claim instead rests on dated compatibility and migration evidence across multiple years.
- **Evidence limits:** research was read-only. No candidate code was executed, dependencies installed, benchmark reproduced, or protocol conformance suite run. Performance and abstraction assessments are grounded engineering interpretations of the cited implementations and documentation. Known source limitations and incomplete protocol coverage are preserved rather than hidden.

This is a selection guide for studying calendar engineering, not a ranking or a claim that every component of every listed repository is uniformly exemplary.
