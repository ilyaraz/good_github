# Industrial and embedded communication protocol stacks

Research date: **2026-10-09**.

This report selects 25 GitHub repositories implementing industrial fieldbuses, industrial application protocols, vehicle and agricultural buses, and communication stacks designed for constrained embedded devices. It includes both device and controller implementations, small transport libraries, and larger client/server frameworks. General networking applications, PLC programming environments, board-specific examples, and thin bindings are outside the selection. Publicly readable commercial/evaluation code and official mirrors are explicitly identified.

Criteria are engineering judgments grounded in the linked primary material, not certifications or guarantees that every component is exemplary:

- **C1 — Difficult correctness:** protocol invariants, concurrency, numerical representation, malformed inputs, and failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces and layers supporting different applications, devices, or transports.
- **C3 — Performance with structure:** concrete memory, timing, throughput, or power constraints addressed through understandable design choices.
- **C4 — Sustained evolution:** documented development over years together with compatibility work, testing, or complexity management.

The source and documentation links within each entry are the recommended reading entry points. Moving branches and generated documentation describe the inspected versions; the report does not assume identical capabilities across releases or language implementations.

## Industrial Ethernet and cyclic device communication

### 1. [OpenEtherCATsociety/SOEM](https://github.com/OpenEtherCATsociety/SOEM)

**C · EtherCAT master library.** Study how an application-facing master coordinates mailbox traffic and hardware access without becoming an entire control application. The repository separates protocol sources from operating-system and hardware adaptation directories.

- **C1:** The mailbox implementation manages ticket allocation, completion, expiration, queue rotation, and shared pool access under mutexes. These are concrete ownership and concurrency problems when cyclic communication and configuration requests overlap. Read [`src/ec_main.c`](https://raw.githubusercontent.com/OpenEtherCATsociety/SOEM/master/src/ec_main.c).
- **C3:** The same implementation uses a fixed mailbox pool and bounded queue indices, and caches EEPROM reads with a bitmap. This exposes the tradeoffs between predictable resources, repeated device access, and queue-management complexity; no numerical latency guarantee is inferred.

### 2. [OpenEtherCATsociety/SOES](https://github.com/OpenEtherCATsociety/SOES)

**C · EtherCAT slave/device stack.** A useful counterpart to SOEM: study the device-side relationship between application state, Sync Managers, mailbox availability, and process outputs. It is a separate implementation role, not a duplicate master wrapper.

- **C1:** [`soes/esc.c`](https://raw.githubusercontent.com/OpenEtherCATsociety/SOES/master/soes/esc.c) explicitly rejects invalid state transitions, validates mailbox and process-data configurations, and disables outputs through an application hook during downward/error transitions. Error acknowledgement is part of the state machine.
- **C2:** The repository documents an address-offset hardware abstraction for EtherCAT-controller access and polling, interrupt, or mixed execution. The implementation adds pre/post state-change and safe-output hooks, allowing the protocol machinery to serve different device applications. The root overview and `esc.c` are complementary entry points.

### 3. [ethercrab-rs/ethercrab](https://github.com/ethercrab-rs/ethercrab)

**Rust · Asynchronous EtherCAT master for hosted and `no_std` environments.** Study how Rust ownership constraints meet frames that are prepared, transmitted, and completed by separate execution paths.

- **C1:** [`PduStorage`](https://docs.rs/ethercrab/latest/ethercrab/struct.PduStorage.html) documents explicit capacity and frame-size invariants. Its `try_split` operation can succeed only once, preserving the ownership/lifetime relationship between transmit, receive, and PDU-loop handles.
- **C3:** Const-generic storage bounds the number and size of in-flight frames, while the root example separates the TX/RX task from application process-data work. This makes resource budgeting visible to an embedded integrator rather than implicit in an unbounded queue.

### 4. [rtlabs-com/p-net](https://github.com/rtlabs-com/p-net)

**C · PROFINET device stack; public evaluation edition.** The current repository explicitly says it lacks ports and cannot be built without additional sources. It remains a substantial protocol-code study target, but should not be presented as a complete, immediately buildable public distribution.

- **C1:** [`pf_cmrpc.c`](https://raw.githubusercontent.com/rtlabs-com/p-net/public/src/device/pf_cmrpc.c) implements the context-management RPC protocol machine: connect/release, parameter access, retransmissions, application relations, and notification sessions. The comments distinguish the stateless RPC machine from the state kept in relations and sessions.
- **C3:** The implementation allocates relations and sessions from configured arrays and explicitly accounts for RPC header size, fragment-body capacity, and buffer-width limits. These are inspectable resource constraints rather than a generic small-footprint claim.

### 5. [EIPStackGroup/OpENer](https://github.com/EIPStackGroup/OpENer)

**C · EtherNet/IP I/O adapter stack.** Study a Common Industrial Protocol object system and its connection establishment rules, particularly the difference between explicit messaging and reusable I/O connections.

- **C1:** [`cipconnectionmanager.c`](https://raw.githubusercontent.com/EIPStackGroup/OpENer/master/source/src/cip/cipconnectionmanager.c) checks an existing connection using the vendor, connection-serial, and originator-serial tuple. It also parses connection paths and validates electronic keys, exposing identity and compatibility invariants that a packet codec alone would miss.
- **C2:** The connection manager registers services against CIP classes and dispatches through class-specific connection-opening functions. This object/service abstraction supports application-specific connectable objects alongside built-in classes, rather than hard-coding a single adapter's behavior.

## CAN, agricultural machinery, and vehicle networks

### 6. [CANopenNode/CANopenNode](https://github.com/CANopenNode/CANopenNode)

**C · CANopen device stack.** Study the object dictionary as the shared boundary between network services, real-time process data, application variables, and persistence.

- **C1:** The [object-dictionary design](https://raw.githubusercontent.com/CANopenNode/CANopenNode/master/doc/objectDictionary.md) explains why SDO access and the fast PDO thread require coordinated locking, including when the application must use the same protection. It also prohibits bypassing extension accessors through direct variable access.
- **C2:** Indexed entries, stream-like read/write functions, and optional extensions support custom storage and arbitrarily sized data without requiring services to know application-specific structures.
- **C4:** The [changelog](https://raw.githubusercontent.com/CANopenNode/CANopenNode/master/doc/CHANGELOG.md) records the 2020 driver/interface reorganization, subsequent object-dictionary and SDO/PDO rewrites, and 2024 MISRA analysis. It documents migration consequences rather than implying an unchanged API.

### 7. [lely-industries/lely-core](https://github.com/lely-industries/lely-core)

**C/C++ · CANopen master/slave libraries and asynchronous infrastructure; official GitHub mirror.** Development is hosted on the project's linked GitLab repository. Count this monorepo once, focusing on `liblely-co`, `liblely-coapp`, and their event/I/O layers.

- **C1:** The [state-machine design](https://opensource.lely.com/canopen/docs/fsm/) describes parameterized events, entry/exit actions, and transient states used for error handling. It explains how transition functions return the next state and why the design localizes additions.
- **C2:** The [library overview](https://opensource.lely.com/canopen/docs/overview/) describes a passive CANopen core: applications supply frames and time, while network objects distribute input and callbacks request output. Higher-level event loops, futures, and C++ application interfaces build on that core.
- **C3:** Requests are nonblocking and can share one thread; the core does not create threads or read the system clock. This makes scheduling and platform integration explicit. Upstream documentation may evolve ahead of a particular mirror revision.

### 8. [OpenCyphal/libcanard](https://github.com/OpenCyphal/libcanard)

**C · Cyphal/CAN transport for real-time embedded systems.** Study the boundary between transport reliability, application payload ownership, and a user-supplied memory allocator. This is a transport implementation, not the whole application/schema toolchain.

- **C1:** [`libcanard/canard.h`](https://raw.githubusercontent.com/OpenCyphal/libcanard/master/libcanard/canard.h) specifies transfer-ID duplicate suppression and distinct payload lifetimes: single-frame data can borrow the caller's buffer, while multi-frame payload storage has an explicit owner and release obligation.
- **C2:** The inspected API separates transport kinds, subscriptions, memory resources, and platform transmission callbacks; the repository supports Classic CAN, CAN FD, and redundant interfaces.
- **C3:** Separate resources for TX transfers, frames, RX sessions, and payloads permit targeted memory budgets. Complexity documentation explicitly assumes constant-time allocation; that assumption is an integration requirement, not an unconditional guarantee.

### 9. [Open-Agriculture/AgIsoStack-plus-plus](https://github.com/Open-Agriculture/AgIsoStack-plus-plus)

**C++ · ISO 11783/ISOBUS and J1939-based agricultural communication.** A less ubiquitous, substantial stack covering machinery interoperability, virtual terminals, and task-controller roles. Study how small CAN frames support larger application messages.

- **C1:** [`can_transport_protocol.cpp`](https://raw.githubusercontent.com/Open-Agriculture/AgIsoStack-plus-plus/main/isobus/src/can_transport_protocol.cpp) distinguishes broadcast-announcement transfers from connection-mode transfers, tracks sequence and clear-to-send counts, timestamps state changes, and checks session and message-size limits. Broadcast errors require different behavior from directed connection errors.
- **C2:** The transport manager receives frame-send and message-delivery callbacks and works with shared control-function and network-configuration abstractions. Those transport facilities underpin multiple ISOBUS services; the repository separately exposes hardware integration and higher-level application protocols.

### 10. [COVESA/vsomeip](https://github.com/COVESA/vsomeip)

**C++ · Automotive SOME/IP communication and service discovery.** Study how one middleware spans intra-device IPC and communication between ECUs. Application-data serialization is outside this library's scope.

- **C2:** The [implementation overview](https://github.com/COVESA/vsomeip/wiki/vsomeip-in-10-minutes) explains transport endpoints, service instances, request/response, and event-group subscriptions. The repository separates the main library, configuration, service discovery, and end-to-end protection modules.
- **C3:** Local endpoints use Unix-domain sockets with Boost.Asio, while a per-device routing manager handles external traffic. The documented direct local path avoids routing every local message through that central component. This is a concrete architectural performance choice, not a measured throughput claim.

## Industrial application protocols and reusable PLC access

### 11. [open62541/open62541](https://github.com/open62541/open62541)

**C · OPC UA client/server stack.** Study a large standards implementation that retains a small dependency core and replaceable architecture, information-model, and cryptographic backends.

- **C2:** The root architecture description separates public API, core services, EventLoop-based platform support, and plugins. The [`Nodestore` interface](https://raw.githubusercontent.com/open62541/open62541/master/include/open62541/plugin/nodestore.h) exposes the underlying information-model representation to storage implementers without making it the ordinary application API.
- **C3:** That interface documents reference-type bitsets for subtype comparisons and tagged node pointers that compact common numeric identifiers. It explicitly accounts for processor-dependent encoding limits, providing a concrete study of memory and browse-performance optimization within a reusable model.

### 12. [eclipse-milo/milo](https://github.com/eclipse-milo/milo)

**Java · OPC UA protocol stack and client/server SDKs.** Study the distinction between transport connections, secure channels, sessions, and application-level subscriptions. The verified canonical owner is `eclipse-milo`.

- **C1:** The [client guide](https://github.com/eclipse-milo/milo/wiki/Client) explains that sessions can outlive network connections. Recovery may reactivate a session or create another and transfer subscriptions; application retry decisions and per-operation status handling remain explicit responsibilities.
- **C2:** The repository separates low-level stack modules from SDKs. The guide provides three complementary access levels: service calls with detailed statuses, cached address-space/node wrappers, and subscriptions. This is useful for studying how convenience APIs coexist with protocol fidelity.

The inspected guide identifies a 1.2.0 snapshot baseline; applications using older releases must consult the corresponding migration material.

### 13. [apache/plc4x](https://github.com/apache/plc4x)

**Primarily Java and Go · Multi-protocol industrial communication libraries.** Count the monorepo once, focusing on `plc4j`, `plc4go`, and protocol definitions. It contains protocol implementations behind a common PLC-access model, rather than merely wrapping one external stack.

- **C1:** The [OPC UA driver documentation](https://plc4x.apache.org/plc4x/latest/users/protocols/opcua.html) explains limits on browse depth, total nodes, and references, including cyclic references and servers that produce endless fresh nodes. It also distinguishes channel-renewal, handshake, and request timeouts.
- **C2:** The root describes uniform industrial-device access across drivers and languages; the driver guide shows how protocol-specific addressing and security options fit that interface. This is a useful study of the tension between a common API and unequal protocol capabilities.

Capabilities are not uniform: the inspected documentation limits Go OPC UA to unencrypted, unchunked communication, and the root marks C/Python implementations as not ready and .NET work as abandoned.

### 14. [libplctag/libplctag](https://github.com/libplctag/libplctag)

**C · EtherNet/IP and Modbus TCP PLC data-access library.** Study an intentionally tag-centered API that hides the PLC connection as an implementation detail while exposing explicit data transfer and local value access.

- **C2:** The [API guide](https://github.com/libplctag/libplctag/wiki/API) models named CIP data and numbered Modbus regions as long-lived tag handles. The same interface exposes reads, writes, typed accessors, callbacks, and operation status across different PLC addressing schemes.
- **C3:** The guide explains why repeated connection setup is expensive and why handles should be retained; idle connections can close and reopen internally without destroying the handle. The separation supports connection reuse while preserving application-visible data objects.
- **C4:** The repository documents production use and largely stable API evolution since 2012, explicit compatibility-checking APIs, and an OS/compiler test matrix for releases. These are project-reported practices, not independent hardware validation.

## Modbus and building automation

### 15. [stephane/libmodbus](https://github.com/stephane/libmodbus)

**C · Modbus RTU and TCP library.** Study how a relatively small API still requires careful framing, byte representation, serial behavior, and recovery semantics.

- **C1:** [`src/modbus.c`](https://raw.githubusercontent.com/stephane/libmodbus/master/src/modbus.c) separates function, metadata, and data parsing stages, calculates expected response lengths, and handles protocol-specific errors and transport recovery.
- **C2:** Backend operations and backend-specific header/checksum lengths allow common request/reply machinery to serve serial and Ethernet transports rather than duplicating the entire protocol implementation.
- **C4:** The [release history](https://raw.githubusercontent.com/stephane/libmodbus/master/NEWS.md) documents changes across 2022–2026, including float-endianness regression repair, strict-aliasing and integer-overflow fixes, socket/serial lifecycle corrections, and associated test changes. It is especially useful for studying correctness issues that survive a simple protocol's apparent simplicity.

### 16. [pymodbus-dev/pymodbus](https://github.com/pymodbus-dev/pymodbus)

**Python · Modbus clients, servers, and simulation with synchronous/asynchronous interfaces.** Study how an implementation shares protocol logic while accommodating different execution models.

- **C1:** [`TransactionManager`](https://raw.githubusercontent.com/pymodbus-dev/pymodbus/dev/pymodbus/transaction/transaction.py) coordinates request identifiers, retries, locks, response futures, deadlines, and partial local-echo removal. Its synchronous and asynchronous paths make an instructive comparison in maintaining equivalent semantics.
- **C2:** The manager explicitly separates application APIs from transports, framers, and PDUs, with tracing hooks at packet, PDU, and connection levels. This supports clients, servers, custom function codes, and multiple framing/transport combinations.

The [API-change record](https://raw.githubusercontent.com/pymodbus-dev/pymodbus/dev/API_changes.rst) is essential companion reading: it records changes to bit ordering, datastore interfaces, and TLS configuration. The project explicitly does not use standard semantic-versioning rules; do not infer drop-in compatibility from version-number familiarity.

### 17. [bacnet-stack/bacnet-stack](https://github.com/bacnet-stack/bacnet-stack)

**C · BACnet application, network, and data-link layers.** Study an embedded building-automation stack whose services are assembled from codecs, handlers, object implementations, and link choices.

- **C1:** The [developer architecture guide](https://raw.githubusercontent.com/bacnet-stack/bacnet-stack/master/doc/README.developer) explains device-address binding and the transaction state machine for confirmed messages, retries, timeouts, and segmentation. It candidly discusses its InvokeID keying, providing a concrete invariant to inspect.
- **C2:** Service codecs are distinct from application handlers and send functions; adding a service includes tests and an example. The repository supports embedded and hosted environments and several link families, making it useful for studying reusable services above heterogeneous transports.

The root documents CI across BACnet/IP, IPv6, Ethernet, MS/TP, routers, and multiple embedded ports; that matrix is stronger evidence than popularity, but does not establish every device's interoperability.

## Power systems and telemetry

### 18. [mz-automation/libiec61850](https://github.com/mz-automation/libiec61850)

**C · IEC 61850 client/server library with MMS, GOOSE, Sampled Values, and R-Session.** Study the interaction between a power-system information model and several distinct communication services.

- **C1:** [`reporting.c`](https://raw.githubusercontent.com/mz-automation/libiec61850/v1.6_develop/src/iec61850/server/mms_mapping/reporting.c) maintains report-buffer cursors, overflow state, segmentation state, ownership/reservation data, and separate synchronization for report-control values and notification creation. Threadless configurations change the locking path.
- **C2:** The repository exposes reusable model and service APIs across client/server roles, plus implementation-independent TLS configuration and configurable log storage. Reporting maps logical-node data into MMS-facing behavior rather than baking one substation model into a codec.

The [changelog](https://raw.githubusercontent.com/mz-automation/libiec61850/v1.6_develop/CHANGELOG) provides useful counterexamples and regression topics, including malformed-input bounds, association-specific dataset lifetimes, and deterministic timeout instrumentation. It is evidence of difficult failure modes, not proof that all such defects are eliminated.

### 19. [mz-automation/lib60870](https://github.com/mz-automation/lib60870)

**C · IEC 60870-5-101/104 telecontrol; official read-only GitHub mirror.** Study the serial/TCP telecontrol library separately from libIEC61850: the protocol implementation and redundancy model are distinct, although they share common/HAL infrastructure.

- **C1:** The [CS104 server API](https://support.mz-automation.de/doc/lib60870/latest/group__CS104__SLAVE.html) documents redundancy groups sharing event queues, group configuration before startup, and transfer of destruction responsibility when a group is added to a server. Connection activation/deactivation is distinct from socket establishment.
- **C2:** Application handlers, ASDU processing, protocol parameters, redundancy modes, and threaded/threadless operation are separate interfaces, supporting different remote-terminal and server designs.
- **C3:** Queue capacities are configured explicitly, and the repository states that CS104-server dynamic allocation is restricted to setup. That is a specific runtime-memory design choice, not a claim about all library roles.

### 20. [stepfunc/dnp3](https://github.com/stepfunc/dnp3)

**Rust · DNP3 master/outstation stack, with C/C++/.NET/Java bindings; source-available commercial software.** The [core library notice](https://github.com/stepfunc/dnp3/blob/main/dnp3/README.md) explicitly describes a non-commercial/non-production license and says it is not open source. Its publicly readable implementation is valuable for architectural study.

- **C1:** The [outstation database implementation](https://raw.githubusercontent.com/stepfunc/dnp3/main/dnp3/src/outstation/database/mod.rs) guards shared state through a transactional handle and notifies the asynchronous task after updates. Event handling distinguishes buffered, selected, and confirmed data; discarding undelivered events explicitly protects in-flight response/confirmation exchanges.
- **C2:** Typed measurement/update interfaces, event classes, configurable event buffers, and separate master/outstation roles support many telemetry models. The non-Rust bindings expose a substantive native implementation and are not counted as independent repositories.

## Constrained-device application and network stacks

### 21. [obgm/libcoap](https://github.com/obgm/libcoap)

**C · CoAP application-protocol implementation.** Study how message-sized buffers, large resources, and application ownership interact across constrained and hosted transports. The verified GitHub owner is `obgm`.

- **C1:** [`coap_block.h`](https://raw.githubusercontent.com/obgm/libcoap/develop/include/coap3/coap_block.h) documents block numbers, continuation bits, size encodings, and the ordering constraint that no further options may be added after available PDU space determines a block's size.
- **C2:** The block API lets callers choose library-managed transfers, individual blocks or an assembled body, and additional transfer modes. The wider library supports several embedded hosting environments and alternative security backends.
- **C3:** Block sizing can shrink to fit the remaining PDU space; assembly and caching choices expose the memory-versus-convenience tradeoff directly. These mechanisms address constrained packet and memory budgets without requiring whole-resource delivery in every configuration.

### 22. [eclipse-wakaama/wakaama](https://github.com/eclipse-wakaama/wakaama)

**C · Lightweight M2M device-management stack.** Study registration and bootstrap behavior above CoAP, with configurable client, server, and bootstrap-server roles.

- **C1:** [`core/registration.c`](https://raw.githubusercontent.com/eclipse-wakaama/wakaama/main/core/registration.c) distinguishes pending, successful, and failed registration updates, handles continuation responses, and manages transaction payload lifetimes across callbacks. Registration is a stateful protocol, not just a periodically repeated HTTP-like request.
- **C2:** The root documents separable roles, data formats, protocol-version options, and configurable transport-related behavior.
- **C3:** Its raw Block1 option allows firmware-write blocks to reach an application without retaining and parsing the entire large request in RAM, enabling direct storage to flash.

**Release caveat:** The repository warns that the old 1.0 release is unsupported and affected by security issues, and directs users to the main branch. Do not equate an old release tag with the inspected implementation.

### 23. [openthread/openthread](https://github.com/openthread/openthread)

**C++ core with C APIs · Thread/IPv6 low-power mesh stack.** Count the repository once; relevant subsystems include mesh forwarding, platform interfaces, and Spinel host/controller communication.

- **C1:** [`mesh_forwarder.cpp`](https://raw.githubusercontent.com/openthread/openthread/main/src/core/thread/mesh_forwarder.cpp) coordinates queued messages, direct/indirect transmission, reassembly storage, timers, and shutdown cleanup. Ownership and cancellation must remain consistent when radio operations and device roles change.
- **C2:** The [co-processor architecture guide](https://openthread.io/platforms/co-processor) separates radio-controller, networking, and host-application responsibilities, with Spinel providing a reusable management boundary.
- **C3:** The guide explains the power/resource tradeoff: an NCP can maintain the network while a more powerful host sleeps, whereas an RCP keeps more networking work on the host. This gives a concrete architectural reason for the alternative partitions.

### 24. [lwip-tcpip/lwip](https://github.com/lwip-tcpip/lwip)

**C · Embedded TCP/IP; project GitHub mirror of Savannah development.** Study `src` and the API architecture rather than counting vendor-specific lwIP forks or board ports as independent stacks.

- **C1:** The [API architecture source](https://raw.githubusercontent.com/lwip-tcpip/lwip/master/doc/doxygen/main_page.h) explains the single execution context for raw callbacks, packet processing, and timers. Blocking in that context is forbidden; sequential/socket APIs use a different execution model.
- **C2:** Raw callback, sequential, and BSD-style socket APIs coexist, with the higher-level interfaces built over the lower-level core. This is a particularly clear case of several programming models sharing one protocol engine.
- **C3:** The documentation explicitly links callback operation and zero-copy send/receive to lower memory and execution overhead, while acknowledging the application-programming cost. These are design tradeoffs, not portable benchmark promises.

### 25. [smoltcp-rs/smoltcp](https://github.com/smoltcp-rs/smoltcp)

**Rust · Event-driven TCP/IP for bare-metal and real-time systems.** Study an independently implemented stack with caller-visible storage and explicit protocol limitations, rather than a binding to an operating-system network stack.

- **C1:** [`src/socket/tcp.rs`](https://raw.githubusercontent.com/smoltcp-rs/smoltcp/main/src/socket/tcp.rs) represents TCP lifecycle states explicitly and implements round-trip estimation and retransmission timing with bounded integer representations and clamping. It is a useful entry point into timing, sequence-space, and connection-state correctness.
- **C3:** The repository states that heap allocation is not required. The implementation uses ring-buffer socket storage and stores estimator values in smaller integer fields to save space, making memory constraints visible in the design.

The root explicitly lists implemented and omitted features. Its benchmark claim is not repeated here because it does not establish performance on an arbitrary embedded target.

## Coverage and search notes

Discovery used more than six distinct live-web formulations, including industrial EtherCAT/CANopen stacks; OPC UA/Modbus/BACnet; EtherNet/IP/PROFINET/POWERLINK; IEC 61850/60870/DNP3; CANopen versus Cyphal transport libraries; Rust embedded networking and EtherCAT; agricultural ISOBUS/J1939; automotive SOME/IP; constrained CoAP/LwM2M/Thread; and KNX/IO-Link alternatives. Follow-up searches targeted protocol architecture, transaction state machines, redundancy queues, source files, and release/API histories. Later discovery increasingly returned already selected implementations, downstream ports, thin wrappers, demonstrations, or projects with less clearly established substance.

Each selected canonical GitHub repository page was opened. Each entry also has an independently read primary implementation or technical-documentation source beyond its root README. The selection spans C, C++, Rust, Java, Python, and PLC4X's Go implementation; C-family code predominates because that is what the inspected device-stack ecosystem supplied. Master/device pairs and contrasting implementations of the same protocol are retained when their architectures offer distinct study value. Monorepos and language bindings are counted once.

Exclusions include SCADA dashboards and simulators that delegate protocol work to other libraries; vendor examples and CANopen/lwIP integration forks; generic networking servers; and unverified third-party mirrors. KNX, IO-Link, and POWERLINK were searched but are not exhaustively represented. This report also does not attempt coverage of every proprietary fieldbus, safety profile, or radio protocol.

Material limits: this was read-only source/documentation research, with no builds, dependency installation, hardware testing, benchmark reproduction, or conformance testing. Some documentation endpoints were unavailable; readable repository sources or alternate official documentation supplied the evidence used here. GitHub pages and documentation can differ by branch or snapshot, as highlighted for Milo, PLC4X, and Wakaama. p-net's missing public ports and Step Function DNP3's restricted license materially affect practical reuse. Lely, lib60870, and lwIP are identified as mirrors; their presence on GitHub does not relocate upstream development. Except where dated evolution or release practices are explicitly supported, inclusion makes no claim about maintenance cadence.
