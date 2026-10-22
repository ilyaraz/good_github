# Telephony signaling and call switching systems

Research date: **2026-10-09**.

This selection covers implementations that establish, route, maintain, and release telephone calls: SIP proxies and back-to-back user agents (B2BUAs), PBX and softswitch cores, reusable signaling stacks, H.323 gatekeepers, and SS7/SIGTRAN/ISDN and mobile switching components. It includes 25 repositories across C, C++, Java, Erlang, Python, Go, Rust, and TypeScript. Media processing appears only where it accompanies substantive signaling or call control. Repository identity and archive status were checked through GitHub's repository API; the linked implementation and documentation entry points were opened and read.

The criteria below are selection judgments grounded in the cited material, not certifications of correctness or recommendations to deploy every project unchanged.

- **C1 — Difficult correctness:** protocol invariants, concurrency, adversarial input, resource lifetimes, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces or architectural layers that support different applications.
- **C3 — Performance with structure:** concrete measures for latency, throughput, contention, memory, or overload, with understandable design boundaries.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate complexity management; repository age alone does not qualify.

## SIP routing and programmable call control

### 1. [kamailio/kamailio](https://github.com/kamailio/kamailio)

**C — SIP signaling server and programmable proxy.** A particularly useful study of what changes when a fast message router becomes a stateful transaction processor. Its transaction manager documents costs and ownership boundaries rather than treating statefulness as free.

- **C1:** The transaction manager correlates responses, absorbs upstream retransmissions, retransmits downstream, and coordinates timers, shared-memory message clones, and mutexes. Configuration operations on the original private message can cease to affect the forwarded clone, an important ordering invariant. [Transaction-manager implementation guide](https://github.com/kamailio/kamailio/blob/master/src/modules/tm/README).
- **C2, C3:** The same module exposes transaction callbacks and locally originated transactions, plus combined serial/parallel forking by contact priority. Its guide explicitly explains trading memory and copying/locking overhead against repeated parsing and DNS work. This is unusually concrete material for studying extensibility alongside performance. [TM guide and API](https://github.com/kamailio/kamailio/blob/master/src/modules/tm/README).

### 2. [OpenSIPS/opensips](https://github.com/OpenSIPS/opensips)

**C — SIP server with integrated B2BUA facilities.** Study its separation between protocol entities and application call scenarios. OpenSIPS and Kamailio share ancestry but have substantive separate implementations and evolution; they are not counted as interchangeable mirrors.

- **C1:** B2B logic must handle messages arriving during bridging and after a leg has been disconnected. The documentation identifies ACK/BYE/reply cases handled internally, and cleanup of expired sessions sends BYE on every remaining dialog. [B2B logic guide](https://github.com/OpenSIPS/opensips/blob/master/modules/b2b_logic/README.md).
- **C2:** `b2b_entities` supplies UAC/UAS mechanisms, while `b2b_logic` supplies higher-level services through dedicated request/reply routes. Sessions can originate from an incoming INVITE or third-party call control, and clustering belongs to the lower entity layer. This supports studying a reusable call-control engine embedded in a proxy. [Layering and scenario API](https://github.com/OpenSIPS/opensips/blob/master/modules/b2b_logic/README.md).

### 3. [BelledonneCommunications/flexisip](https://github.com/BelledonneCommunications/flexisip)

**C++ — SIP proxy, push-notification integration, and B2BUA; official Linphone/Belledonne GitHub mirror.** Mobile clients make call routing more complicated because a destination may register only after being awakened.

- **C1, C2:** `ForkContext` connects incoming/outgoing transactions to branches, late registrations, cancellation, response selection, and completion notifications. Its contract distinguishes a new contact requiring dispatch from an already pending transaction, and separates the incoming replier from fork lifecycle observers. [Fork-context interfaces](https://github.com/BelledonneCommunications/flexisip/blob/master/src/fork-context/fork-context.hh).
- **C4:** The changelog provides dated 2020–2026 evidence of registration and push-routing regressions, reversions after production side effects, transitional compatibility for renamed payload keys, and configuration deprecations. It is useful evidence of managing interoperability over time, rather than merely adding features. [Changelog](https://github.com/BelledonneCommunications/flexisip/blob/master/CHANGELOG.md).

### 4. [drachtio/drachtio-server](https://github.com/drachtio/drachtio-server)

**C++ — SIP engine controlled by external Node.js applications.** This repository is the server, not the separate JavaScript SDK. It is a good example of putting application policy across a process boundary while retaining native protocol machinery.

- **C1:** `TimerDHandler` retains INVITE/ACK relationships to answer retransmitted final responses. The dialog controller also distinguishes application-facing send operations from operations executed on the SIP stack thread, exposing the lifetime and execution-context problems in remote call control. [Dialog-controller header](https://github.com/drachtio/drachtio-server/blob/main/src/sip-dialog-controller.hpp).
- **C2:** Requests, dialogs, client connections, and proxying have separate controllers. The server supports multiple SIP listeners and an application connection interface; its README explicitly records a server/SDK wire-protocol compatibility boundary. [Server architecture and configuration](https://github.com/drachtio/drachtio-server/blob/main/README.md).

### 5. [sippy/b2bua](https://github.com/sippy/b2bua)

**Python — signaling-focused SIP B2BUA and stack.** Study how an answering UA and originating UA can evolve independently while a small call-control layer mediates their events.

- **C1:** The transaction manager rejects duplicate transaction identifiers, defers CANCEL until the appropriate provisional-response state, manages retransmission timers, and handles unmatched ACK/CANCEL differently. These are concrete failure-ordering concerns rather than simple request forwarding. [Transaction manager](https://github.com/sippy/b2bua/blob/master/sippy/SipTransactionManager.py).
- **C2:** Abstract events isolate call legs. The controller can transform events or replace a UA to implement failover and controlled transfer without replacing the whole SIP implementation. [Architecture and call-flow guide](https://github.com/sippy/b2bua/blob/master/documentation/documentation.md).

### 6. [erlnets/nksip](https://github.com/erlnets/nksip)

**Erlang — SIP application-server framework.** Useful for comparing actor-oriented call state and dynamically constructed extension chains with C/C++ callback architectures. GitHub reported its last push in May 2024; this report does not assert current maintenance.

- **C1:** The dialog implementation tracks early/confirmed states, secure targets, sequence numbers, session updates, timer cancellation, and the point at which a route set becomes fixed. It also updates an unfinished INVITE when its remote target changes. [Dialog state implementation](https://github.com/erlnets/nksip/blob/master/src/nksip_call_dialog.erl).
- **C2, C3:** Plugins use dependency-ordered callbacks and can continue processing with modified arguments. The chain is compiled into a runtime module to reduce dispatch overhead, and services can have different plugin sets. The documentation is evidence of the mechanism, not an independently measured speed claim. [Plugin architecture](https://github.com/erlnets/nksip/blob/master/doc/advanced/plugin_architecture.md).

### 7. [fonoster/routr](https://github.com/fonoster/routr)

**TypeScript with Java/protobuf components — programmable SIP proxy, registrar, and location service.** The relevant monorepo subsystems are EdgePort, dispatcher, Connect processor, and location service; they count as one repository.

- **C1:** The Connect router verifies token permissions, resolves caller/callee resources, applies direction-dependent access checks, and distinguishes agent, peer, and PSTN routing. It passes call identifiers and session-affinity information into location lookup, making identity and route consistency visible in application code. [Connect router](https://github.com/fonoster/routr/blob/main/mods/connect/src/router.ts).
- **C2:** EdgePort handles SIP transport/message conversion, the dispatcher selects processors, and replaceable processors and middleware implement policy. The core specification explains these gRPC/protobuf boundaries. It is explicitly a draft design document, so its aspirational performance requirements are not treated as proven results. [Core specification](https://github.com/fonoster/routr/blob/main/CORE.md).

### 8. [Metaswitch/sprout](https://github.com/Metaswitch/sprout)

**C++ — Clearwater Sprout SIP router and Bono edge proxy, including IMS functions. Archived historical project.** The repository states that active Project Clearwater support ended on 2019-12-01. Retained for its unusually explicit architectural documentation, not as a current deployment recommendation.

- **C1, C2:** The architecture explains ordering authentication, registration, and proxy modules; linking one incoming transaction to multiple outgoing transactions; and optimistic updates to shared registration bindings under concurrent REGISTER requests. Separate store implementations support live and local-test configurations. [Bono/Sprout architecture](https://github.com/Metaswitch/sprout/blob/dev/docs/Bono%20Sprout%20Architecture.md).
- **C3:** Separate transport and worker pools permit parallel processing despite per-connection serialization. Overload measurement excludes external I/O latency, and an I/O trap detects worker operations that fail to mark that boundary. [Thread-pool design](https://github.com/Metaswitch/sprout/blob/dev/docs/Bono%20Sprout%20Architecture.md), [I/O accounting and traps](https://github.com/Metaswitch/sprout/blob/dev/docs/IOTraps.md).

## PBX, softswitch, and service orchestration

### 9. [asterisk/asterisk](https://github.com/asterisk/asterisk)

**C — PBX and communications engine.** Study the channel, bridge, dialplan, and module abstractions rather than attempting an undirected read of the entire codebase.

- **C1:** The project's locking discussion gives concrete channel-driver/core lock-order rules and explains why apparently sensible unlock/relock and recursive-lock workarounds can produce stale assumptions, deadlocks, or livelocks. It also candidly distinguishes desired rules from problematic existing patterns. [Locking in Asterisk](https://docs.asterisk.org/Development/Reference-Information/Other-Reference-Information/Locking-in-Asterisk/).
- **C2:** Channel drivers represent external technologies, bridges connect channels, and applications/functions execute dialplan behavior. External control through AGI and independently configurable modules broaden the same engine across PBX, conferencing, and programmable call handling. [Architecture guide](https://github.com/asterisk/documentation/blob/main/docs/Fundamentals/Asterisk-Architecture/Asterisk-Architecture-The-Big-Picture.md).

### 10. [signalwire/freeswitch](https://github.com/signalwire/freeswitch)

**C, with C++ modules — modular softswitch and media/call-control engine.** A useful counterpart to Asterisk for studying an explicit session-state lifecycle and pluggable telephony behavior.

- **C1:** The core state machine handles recovery, routing, execution, hangup, and reporting. Recovery paths synchronize with the other channel's reset/media state before restoring a bridge; hangup completion and reporting have their own ordering. [Core state machine](https://github.com/signalwire/freeswitch/blob/master/src/switch_core_state_machine.c).
- **C2:** The core API provides common sessions, memory-pool-backed data, heartbeats, and media callbacks, while state handling invokes dialplan and application interfaces. These boundaries support distinct endpoint and service modules within one switching engine. [Core API](https://github.com/signalwire/freeswitch/blob/master/src/include/switch_core.h).

### 11. [yatevoip/yate](https://github.com/yatevoip/yate)

**C++ — message-driven telephony engine and software PBX.** Its central message bus offers a different organizing principle from a primarily channel-oriented PBX.

- **C1:** The dispatcher releases its handler-list lock before invoking a callback, marks handlers unsafe to destroy, and rescans when the list changes during dispatch. Queue operations and post-dispatch hooks have separate locking and lifetime concerns. [Message dispatcher implementation](https://github.com/yatevoip/yate/blob/master/engine/Message.cpp).
- **C2:** `Message`, `MessageHandler`, filters, relays, priorities, and broadcast semantics form a reusable contract for routing modules, drivers, and external integrations. The message API includes encoding/decoding for external communication. [Engine interfaces](https://github.com/yatevoip/yate/blob/master/yatengine.h).

### 12. [2600hz/kazoo](https://github.com/2600hz/kazoo)

**Erlang — distributed telephony service platform.** Focus on `applications/ecallmgr`, the layer managing FreeSWITCH nodes and call ownership, rather than the platform's many unrelated administrative APIs. GitHub reported a last push in February 2025; present commercial-product activity is not inferred from this repository.

- **C1:** The usurp monitor coordinates call-control/publisher takeover notifications, indexes registrations by call and process, monitors process death, and removes stale entries from both ETS indexes. This is concrete material for examining distributed control ownership and cleanup. [Usurp monitor](https://github.com/2600hz/kazoo/blob/master/applications/ecallmgr/src/ecallmgr_usurp_monitor.erl).
- **C2:** Ecallmgr hides which FreeSWITCH node owns a call or conference and abstracts switch-specific commands from higher-level applications. This is a substantive orchestration layer, not a second implementation of FreeSWITCH's signaling stack. [Ecallmgr overview](https://github.com/2600hz/kazoo/blob/master/applications/ecallmgr/doc/README.md).

### 13. [sems-server/sems](https://github.com/sems-server/sems)

**C++ — SIP Express Media Server; selected for its SBC/B2BUA call-control framework.** Its signaling and policy layers make it relevant beyond its audio-processing functionality.

- **C2:** Composable call-control modules receive start/connect/end/route events and can alter routing, reject calls, enforce concurrent-call limits, or set duration timers. Namespaced per-call variables and mandatory-configuration validation give the extension system a concrete contract. [SBC call-control API](https://github.com/sems-server/sems/blob/master/doc/Readme.sbc_call_control.txt).
- **C3:** The tuning guide explains one-thread-per-session versus pooled signaling execution, separate media threads, stack-memory costs, and how a blocking call can stall every session assigned to a worker. It is an older design note, retained as architectural evidence rather than current tuning advice. [Threading and load tradeoffs](https://github.com/sems-server/sems/blob/master/doc/Tuning.txt).

### 14. [willamowius/gnugk](https://github.com/willamowius/gnugk)

**C++ — GNU Gatekeeper for H.323 call routing, authorization, and interworking.** This provides an important non-SIP signaling family, including E.164 routing and neighboring gatekeepers.

- **C1:** The change history records concrete TPKT-length validation, out-of-bounds packet-read fixes, Q.931 authentication fixes, and races in H.460.19 multiplex identifiers. These expose the difficult parser and interworking surface of a gatekeeper. [Implementation change history](https://github.com/willamowius/gnugk/blob/master/changes.txt).
- **C2:** Calls traverse a configurable policy chain that can resolve, rewrite, forward, or decline a route. Policies compose internal registration, parent/neighbor queries, DNS/ENUM, SQL, HTTP, Lua, and external queue decisions across different H.323 request types. [Routing architecture and configuration](https://www.gnugk.org/gnugk-manual-6.html).

## Reusable SIP protocol stacks

### 15. [pjsip/pjproject](https://github.com/pjsip/pjproject)

**C/C++ — portable signaling/media libraries; selected subsystem: PJSIP transactions.** The monorepo counts once. Concentrating on signaling reveals a library intended for embedding rather than a single fixed PBX application.

- **C1:** A transaction records explicit INVITE/non-INVITE and UAC/UAS state, retransmission state, transport errors, pending transmissions, and group/chained locks. The header documents a second mutex for timer protection and deadlock avoidance. [Transaction API and data model](https://github.com/pjsip/pjproject/blob/master/pjsip/include/pjsip/sip_transaction.h).
- **C2:** A common transaction object and registered transaction-layer module support both endpoint roles and stateful processing behind the same API. The tree also documents sanitizer-backed fuzzing infrastructure, useful when investigating parser robustness without implying that every protocol path is covered. [Transaction layer](https://github.com/pjsip/pjproject/blob/master/pjsip/include/pjsip/sip_transaction.h), [fuzzing guide](https://github.com/pjsip/pjproject/blob/master/FUZZING.MD).

### 16. [resiprocate/resiprocate](https://github.com/resiprocate/resiprocate)

**C++ — SIP stack, Dialog Usage Manager, and related servers.** Counted once for the monorepo; the most useful starting point here is DUM rather than its TURN or media components.

- **C1:** DUM handles forking, merged requests, offer/answer, refreshes, authentication, and redirection. Its handle manager explicitly tracks valid object identifiers and supports shutdown only when outstanding handles are gone, exposing asynchronous object-lifetime concerns. [DUM overview](https://github.com/resiprocate/resiprocate/wiki/DUM-Overview), [handle manager](https://github.com/resiprocate/resiprocate/blob/master/resip/dum/HandleManager.hxx).
- **C2:** Dialog usages and application-supplied handlers/factories let one manager serve multiple user agents and support B2BUAs, registrations, subscriptions, and calls. Engineers can study how a reusable protocol engine presents higher-level call objects without erasing SIP semantics. [DUM interface model](https://github.com/resiprocate/resiprocate/wiki/DUM-Overview).

### 17. [freeswitch/sofia-sip](https://github.com/freeswitch/sofia-sip)

**C — Sofia-SIP user-agent library, FreeSWITCH-hosted continuation.** This is distinct from the FreeSWITCH switching engine: it supplies reusable signaling mechanisms used beneath applications.

- **C1:** The NUA documentation explains asynchronous communication between application and protocol threads, operation handles carrying dialog/session state, and delivery of callbacks in the application event-loop context. Correct handle ownership and event ordering are central to the interface. [NUA design and programming guide](https://github.com/freeswitch/sofia-sip/blob/master/libsofia-sip-ua/nua/nua.docs).
- **C2, C3:** NUA adds call semantics above the lower NTA transaction layer, while reactor roots, typed tag parameters, and memory homes provide common infrastructure. A separate protocol thread preserves time-sensitive stack processing when application work blocks. These are explicit architectural mechanisms, not throughput claims. [NUA layering, event loops, and memory model](https://github.com/freeswitch/sofia-sip/blob/master/libsofia-sip-ua/nua/nua.docs).

### 18. [RestComm/jain-sip](https://github.com/RestComm/jain-sip)

**Java — JAIN-SIP implementation derived from NIST's stack. Historical git-svn mirror with RestComm/TeleStax productization work.** The repository description identifies this lineage; GitHub reported its last push in January 2024. It should not be mistaken for a newly maintained upstream merely because the mirror remains available.

- **C1:** The transaction stack keeps separate concurrent maps for early dialogs, established dialogs, pending transactions, merged requests, and transactions awaiting ACK. Timer and dialog lifecycle management make it a useful Java concurrency study. [Transaction-stack implementation](https://github.com/RestComm/jain-sip/blob/master/src/gov/nist/javax/sip/stack/SIPTransactionStack.java).
- **C2, C3:** The stack exposes configurable timer/network/parser abstractions and high/low watermarks for limiting transaction-table growth. Its separately configurable TCK can target an implementation under test, showing an API-level compatibility discipline without establishing present-day test results. [Stack controls](https://github.com/RestComm/jain-sip/blob/master/src/gov/nist/javax/sip/stack/SIPTransactionStack.java), [TCK instructions](https://github.com/RestComm/jain-sip/blob/master/how-to-run-the-tck.txt).

### 19. [emiago/sipgo](https://github.com/emiago/sipgo)

**Go — SIP library for servers and user agents.** Useful for studying how protocol state machines coexist with Go channels, contexts, callbacks, and mutexes.

- **C1:** Transaction interfaces distinguish completion, cancellation, transport failure, timeout, and retransmission. The implementation explicitly documents FSM locking and callback reentrancy hazards; `OnTerminate` callbacks cannot safely invoke arbitrary transaction operations. [Transaction interfaces and synchronization](https://github.com/emiago/sipgo/blob/main/sip/transaction.go).
- **C2:** Shared client/server transaction interfaces compose with dialog caches and handlers. Integration tests exercise authentication, INVITE/ACK, hangup from either side, and empty-cache cleanup, giving a concrete path from low-level transactions to reusable call handling. These tests were inspected, not run. [Dialog integration tests](https://github.com/emiago/sipgo/blob/main/dialog_integration_test.go).

### 20. [restsend/rsipstack](https://github.com/restsend/rsipstack)

**Rust — SIP transaction/dialog stack for host and embedded applications.** Included for architectural contrast, without assigning the long-evolution criterion or treating README compliance claims as independently proven.

- **C1:** Typed transaction events distinguish received messages, timers, responses, and termination. The implementation tracks original requests, last replies/ACKs, connections, and timer identifiers across client/server INVITE and non-INVITE roles. [Transaction implementation](https://github.com/restsend/rsipstack/blob/main/src/transaction/transaction.rs).
- **C2:** Endpoint construction, transports, transactions, and dialogs form separate layers. The documented platform interfaces allow Tokio-hosted and allocation-enabled `no_std` backends, with explicit transport limitations for embedded targets; proxy and UA examples exercise the same stack. [Architecture and API guide](https://github.com/restsend/rsipstack/blob/main/README.md).

## SS7, SIGTRAN, ISDN, and mobile switching

### 21. [osmocom/libosmo-sigtran](https://github.com/osmocom/libosmo-sigtran)

**C — SCCP/SIGTRAN library and OsmoSTP signaling transfer point; official Osmocom GitHub mirror.** The primary development repository is on Osmocom Gitea. This includes the substantive GitHub mirror once; the older `libosmo-sccp` repository is not a separate selection.

- **C1:** The application-server FSM connects ASP availability to routing, peer notifications, and selection of active transports. The code treats override/load-sharing/round-robin and broadcast modes separately and frees messages when no usable ASP exists. [Application-server FSM](https://github.com/osmocom/libosmo-sigtran/blob/master/src/xua_as_fsm.c).
- **C2:** The reusable library implements M3UA, SUA, and connection-oriented/connectionless SCCP, while OsmoSTP uses those layers to route and translate signaling. This is a useful boundary between a protocol toolkit and a deployable network element. [Repository scope and upstream provenance](https://github.com/osmocom/libosmo-sigtran/blob/master/README.md).

### 22. [osmocom/osmo-msc](https://github.com/osmocom/osmo-msc)

**C — 3GPP Mobile Switching Centre; official Osmocom GitHub mirror.** Relevant components include mobile call control and MNCC integration with external switching. Radio access and packet-core projects are outside this entry.

- **C1:** The MNCC call implementation uses child FSMs, explicit parent completion/release events, call-reference matching, error termination, and reparenting. These are useful examples of call lifetime management, particularly in inter-MSC handover; the file's own historical scope comment is narrower than all normal call handling. [MNCC call implementation](https://github.com/osmocom/osmo-msc/blob/master/src/libmsc/mncc_call.c).
- **C2:** The checked-in sequence chart shows how MNCC setup, RTP endpoint creation, alerting, completion, and release connect through an external SIP connector to a PBX. It makes the interface between mobile switching and external call-routing policy concrete. [MNCC/SIP call sequence](https://github.com/osmocom/osmo-msc/blob/master/doc/sequence_charts/mncc_call_fsm.msc).

### 23. [RestComm/jss7](https://github.com/RestComm/jss7)

**Java — SS7 stack and services, including M3UA, SCCP, TCAP, MAP, CAP, and ISUP.** A substantial alternative to C signaling stacks. GitHub reported its last push in June 2024; some documentation reflects older Java/JBoss environments and should be read historically.

- **C1:** TCAP dialogs manage a finite invoke-ID space, local/remote transaction identifiers, concurrent timer execution, dialogue state, scheduled components, and protocol conditions on dialogue portions. The explicit lock and operation tables expose correctness demands beyond serialization of ASN.1 structures. [TCAP dialog implementation](https://github.com/RestComm/jss7/blob/master/tcap/tcap-impl/src/main/java/org/restcomm/protocols/ss7/tcap/DialogImpl.java).
- **C2:** The architecture separates hardware-dependent lower layers from higher-level user protocols, preserving upper APIs across TDM and M3UA deployments. It also describes colocated and signaling-gateway arrangements plus standalone/application-server integration. [Architecture chapter](https://github.com/RestComm/jss7/blob/master/docs/userguide/sources-asciidoc/src/main/asciidoc/Chapter-Design.adoc).

### 24. [asterisk/libpri](https://github.com/asterisk/libpri)

**C — ISDN signaling library with Q.921/Q.931 and supplementary-service support.** Valuable for studying circuit-era call-control invariants and switch variants through an embeddable API. GitHub reported its last push in March 2024; no current release cadence is assumed.

- **C1:** Q.931 call teardown distinguishes master calls, competing subcalls, and the winning leg, cancels timers, and delays destruction until relevant timers and subcalls are finished. Message preparation also resets optional information so stale state cannot leak into a later message. [Q.931 implementation](https://github.com/asterisk/libpri/blob/master/q931.c).
- **C2:** The public API exposes network/CPE roles, multiple switch variants, call and D-channel events, hold/retrieve operations, and diagnostic controls. Applications consume a common event model while the implementation handles wire-level differences. [Public library interface](https://github.com/asterisk/libpri/blob/master/libpri.h).

### 25. [asterisk/libss7](https://github.com/asterisk/libss7)

**C — userspace MTP2/MTP3/ISUP signaling library.** This is distinct from libpri's ISDN protocols and from libosmo-sigtran's adaptation/routing focus; it is a useful smaller entry into native SS7 link and circuit state.

- **C1:** MTP2 manages forward/backward sequence numbers, acknowledgement/retransmission indicators, alignment/proving states, ordered retransmission buffers, and timer-triggered return to idle. The interplay of buffers and link state is the main study target. [MTP2 implementation](https://github.com/asterisk/libss7/blob/master/mtp2.c).
- **C2:** The API separates application event polling and scheduling from link transport configuration and ISUP operations such as setup, release, continuity, blocking, and circuit-group reset. ITU and ANSI modes share the library interface. [Link and call-control API](https://github.com/asterisk/libss7/blob/master/libss7.h).

## Coverage and search notes

Discovery used 18 meaningfully distinct live web queries, followed by GitHub API identity checks and direct reads of source, architecture documentation, tests, and change history. Search angles included SIP proxy architecture; PBX/softswitch cores; SS7/SIGTRAN; ISDN; H.323 gatekeepers; Python and Erlang B2BUAs; Go and Rust signaling libraries; distributed call orchestration; IMS/Clearwater; and cloud-oriented processor architectures. Later broad and niche queries increasingly returned already-covered implementations, wrappers, media bridges, or additional projects in the same architectural families. This is a diverse selection, not an exhaustive ecosystem census.

Scope deliberately excludes media-only RTP proxies, codecs, general WebRTC SFUs, SIP capture/monitoring tools, configuration GUIs such as FreePBX/FusionPBX, generated clients, deployment-only repositories, and tutorial applications. SEMS is retained specifically for its SBC/B2BUA framework. PJSIP, reSIProcate, Kazoo, Routr, and Sprout are counted once per monorepo. Downstream copies such as vendor-patched Kamailio trees and additional SEMS forks are not presented as independent projects without separately established implementation differences.

GitHub marked Sprout archived; its end-of-support statement is explicit. Flexisip and the two Osmocom entries are identified as official mirrors, and the older JAIN-SIP mirror's provenance is called out. NkSIP, Kazoo, JAIN-SIP, jSS7, and libpri have older last-push dates; those observations establish only the repository snapshot, not whether every downstream deployment or commercial product is maintained. No years-of-evolution claim is inferred from creation dates or push dates.

The work was read-only internet research: no candidate code was run, dependencies installed, large repositories cloned, or maintainers contacted. Tests and performance mechanisms were inspected but not executed or benchmarked. C1 indicates meaningful correctness problems to study, not proof that the implementation has no defects; C2 and C3 likewise describe grounded architectural judgments. Branch-linked entry points can evolve after the research date, and historical design documents may lag current code. In particular, Routr's draft specifications are distinguished from inspected implementation, and SEMS's older tuning note is not offered as present-day deployment guidance.
