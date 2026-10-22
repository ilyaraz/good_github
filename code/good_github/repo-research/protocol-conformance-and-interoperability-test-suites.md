# Protocol conformance and interoperability test suites

Research date: **2026-10-09**.

This guide selects 25 GitHub repositories containing substantial protocol conformance tests, interoperability matrices, or reusable harnesses with concrete protocol test suites. Coverage includes Internet transports, secure channels, RPC, messaging, file access, DNS, network control, cellular systems, and distributed protocols. Implementation repositories appear only where a substantial interoperability subsystem is identified. The descriptions are code-study recommendations grounded in the linked primary material, not certification claims or endorsements of every component.

**Criteria legend:** **C1** — difficult correctness involving state, invariants, concurrency, numerical semantics, adversarial inputs, or failure handling. **C2** — substantial reusable abstractions supporting different implementations or scenarios. **C3** — practical performance constraints addressed through understandable architecture. **C4** — sustained evolution with compatibility, testing, or complexity-management evidence. Each selection meets at least two criteria. Labels are conservative: neither age nor a recent push alone earns C4, and merely benchmarking something does not earn C3.

## Transport protocols and secure channels

### 1. [summerwind/h2spec](https://github.com/summerwind/h2spec)

**Go; HTTP/2 and HPACK conformance runner.** A compact example of translating normative requirements into executable groups indexed by specification section. Study how it distinguishes stream errors from connection errors and reports the actual wire event against the expected one.

- **C1:** The flow-control tests reduce the initial window to one byte and verify the resulting DATA length. Separate overflow cases require the appropriate `GOAWAY` or `RST_STREAM` with `FLOW_CONTROL_ERROR`, testing both arithmetic bounds and error scope. [Flow-control implementation](https://github.com/summerwind/h2spec/blob/master/http2/6_9_1_the_flow_control_window.go).
- **C2:** `TestGroup`, `TestCase`, connection helpers, and typed events provide common machinery for HTTP/2, HPACK, and generic suites; specification identifiers support selective execution and strict-mode requirements. [Repository usage and suite organization](https://github.com/summerwind/h2spec#readme).

**Scope/status:** The documented targets are RFC 7540 and RFC 7541, not a claim of complete coverage of later HTTP/2 revisions. GitHub metadata showed the last push in October 2023; treat it as an older reference suite.

### 2. [crossbario/autobahn-testsuite](https://github.com/crossbario/autobahn-testsuite)

**Python; WebSocket client/server conformance and robustness suite.** Useful for studying a protocol corpus that exercises both endpoint roles and organizes detailed results by implementation and case.

- **C1:** Coverage explicitly includes fragmentation, invalid UTF-8, reserved bits/opcodes, closing handshakes, and compression behavior. These expose interactions between frame parsing and connection state that ordinary echo tests miss. [Coverage and operating modes](https://github.com/crossbario/autobahn-testsuite#readme).
- **C2:** `CaseSet` indexes cases by hierarchical identifiers, expands selection patterns, applies implementation-specific exclusions, and generates a per-testee case matrix. This separates reusable case selection from endpoint execution. [CaseSet implementation](https://github.com/crossbario/autobahn-testsuite/blob/master/autobahntestsuite/autobahntestsuite/caseset.py).

**Scope/status:** The repository explicitly preserves a legacy Docker environment based on Python 2/PyPy2 for reproducibility. That compatibility constraint matters when studying or adopting the suite.

### 3. [quic-interop/quic-interop-runner](https://github.com/quic-interop/quic-interop-runner)

**Python; QUIC and WebTransport interoperability orchestration.** Study the boundary between an implementation-neutral endpoint contract and protocol-aware test verification.

- **C1:** QUIC cases cover stream/connection flow control, concurrent transfers, resumption, 0-RTT, key updates, lossy handshakes, NAT rebinding, and migration. Verification combines downloaded-content comparisons with packet-capture inspection for selected protocol requirements. [QUIC test contracts](https://github.com/quic-interop/quic-interop-runner/blob/master/quic.md).
- **C2:** Implementations are containers controlled through environment variables and mounted directories. An explicit unsupported-test exit code allows the matrix to grow without treating every missing feature as failure; logs, packet captures, and qlogs follow shared conventions. [Endpoint interface and matrix runner](https://github.com/quic-interop/quic-interop-runner#readme).

**Scope:** Interoperability under defined scenarios is narrower than complete RFC conformance. Most QUIC transfer cases use HTTP/0.9; HTTP/3 is a separate case.

### 4. [google/packetdrill](https://github.com/google/packetdrill)

**C with a domain-specific test language; TCP/UDP/IP stack testing.** Particularly valuable for studying tests that connect application-visible system calls with packet-level behavior and timing.

- **C1:** Scripts interleave timestamped packets and system calls. The interpreter tracks sockets and translates abstract sequence numbers, timestamps, ports, and addresses into live values; a separate thread handles calls expected to block. [Execution model](https://github.com/google/packetdrill#packetdrills-design).
- **C2:** One language expresses packet injection, expected output, syscall results, timing ranges, TCP options, and encapsulations. Local TUN and remote NIC modes reuse this model across different stack boundaries. [Language grammar](https://github.com/google/packetdrill/blob/master/syntax.md).

**Scope:** This repository includes the interpreter and concrete TCP tests, not just a traffic generator. Remote-mode timing variability can cause spurious failures, as its design discussion explains.

### 5. [tlsfuzzer/tlsfuzzer](https://github.com/tlsfuzzer/tlsfuzzer)

**Python; SSL/TLS conformance and adversarial protocol testing.** Study how a test oracle accepts permitted protocol alternatives while still rejecting incorrect error handling.

- **C1:** Tests check the expected alert or closure after malformed exchanges, rather than only detecting crashes. The documented scope includes TLS handshake signatures but excludes certificate-chain and hostname validation. [Scope and error expectations](https://github.com/tlsfuzzer/tlsfuzzer#readme).
- **C2:** Conversations are directed graphs of message generators and expectations. Child edges advance successful exchanges; sibling edges express alternatives, loops accept repeated session tickets, and branches rejoin after optional client authentication. [Decision-graph architecture](https://github.com/tlsfuzzer/tlsfuzzer/blob/master/docs/source/advanced-decision-graph.rst).

The graph documentation is also a useful discussion of oracle design: an overly permissive alternative can accidentally accept a standards violation.

### 6. [tls-attacker/TLS-Anvil](https://github.com/tls-attacker/TLS-Anvil)

**Java; combinatorial TLS conformance suite for clients and servers.** A strong example of separating a test's semantic intent from its parameter combinations and execution lifecycle.

- **C1:** The documented CBC-padding template mutates individual padding bits after a valid handshake and requires a fatal `BAD_RECORD_MAC` alert. Cipher-suite and record-length constraints ensure that a generated case exercises the intended condition. [Complete template example](https://github.com/tls-attacker/TLS-Anvil/blob/main/Docs/docs/05-Adding-New-Tests/02-Test-Case-Example.md).
- **C2:** Annotated JUnit templates define input-parameter models; TLS-Scanner supplies feature extraction, coffee4j supplies combinatorial testing, and TLS-Attacker executes exchanges. Separate framework and test-suite modules keep lifecycle machinery outside individual RFC cases. [Architecture](https://github.com/tls-attacker/TLS-Anvil/blob/main/Docs/docs/04-Architecture.md).

**Scope:** The repository includes TLS 1.2/1.3 tests and identifies DTLS 1.2 support as experimental.

## RPC, messaging, and media interoperability

### 7. [connectrpc/conformance](https://github.com/connectrpc/conformance)

**Go and YAML; Connect, gRPC, and gRPC-Web conformance.** Study a data-driven runner that can test either endpoint independently or pair two implementations.

- **C1:** Cases can supply malformed raw HTTP requests/responses, interrupt streams through cancellation or timeouts, and override expected results when message limits prevent normal completion. Explicit lists of acceptable error codes handle specification ambiguity without accepting every failure. [Test-authoring guide](https://github.com/connectrpc/conformance/blob/main/docs/authoring_test_cases.md).
- **C2:** Protobuf-shaped YAML expands across protocol, HTTP version, codec, compression, and TLS configurations. The runner groups cases by server configuration and controls client/server processes through a common stdin/stdout contract. [Architecture and process sequence](https://github.com/connectrpc/conformance#how-it-works).

This is especially useful for understanding how reference implementations can expose lower-level wire observations while presenting a stable adapter interface to other languages.

### 8. [grpc/grpc](https://github.com/grpc/grpc)

**C++ core with Python orchestration and multiple language clients; focus on `doc/interop-test-descriptions.md` and `tools/interop_matrix`.** Counted once as a monorepo, specifically for its interoperability subsystem.

- **C1:** The shared test contract specifies observable assertions for empty and large messages, client/server streaming, half-closes, compression flags, and feature-probing failures. It documents when a language API cannot expose enough information to verify a particular wire property. [Interop test descriptions](https://github.com/grpc/grpc/blob/master/doc/interop-test-descriptions.md).
- **C2:** A common test service and command-line contract feed a matrix of language/runtime containers. Release-specific client images are used against newer servers, making compatibility testing a repeatable extension of the same harness. [Version-matrix design and operation](https://github.com/grpc/grpc/blob/master/tools/interop_matrix/README.md).

**Limitation:** Some matrix infrastructure references Google-operated registries and CI services; the architecture is inspectable without assuming those operational permissions are available.

### 9. [eclipse-paho/paho.mqtt.testing](https://github.com/eclipse-paho/paho.mqtt.testing)

**Python; MQTT 3.1.1/5.0 client and broker testing utilities.** Study how a controllable broker, raw packet formats, and test clients enable behavior that a production client API might hide.

- **C1:** The MQTT 5 suite checks duplicate CONNECT rejection, incorrect protocol names, retained messages, offline queues, session expiry, topic aliases, flow control, and redelivery after reconnect. These are stateful delivery and failure-recovery properties. [MQTT 5 test implementation](https://github.com/eclipse-paho/paho.mqtt.testing/blob/master/interoperability/client_test5.py).
- **C2:** Packet serializers, versioned clients, a test broker, traffic proxies, and connection-loss tooling are reusable components rather than one broker's internal unit tests. The version-specific package boundaries are documented in the [interoperability guide](https://github.com/eclipse-paho/paho.mqtt.testing/blob/master/interoperability/README.md).

**Scope:** The root documentation calls MQTT-SN support a beginning; it should not be read as a completed MQTT-SN conformance suite.

### 10. [apache/qpid-interop-test](https://github.com/apache/qpid-interop-test)

**Python orchestration with C++, Java, JavaScript, and .NET client shims; AMQP 1.0/JMS interoperability.** Particularly useful for numerical and cross-language representation problems.

- **C1:** The comparator checks message counts and type identity, recursively compares compound AMQP values, and handles floating-point, binary, and UUID representations explicitly. [Type-aware comparison implementation](https://github.com/apache/qpid-interop-test/blob/main/src/qit/core/comparison.py).
- **C2:** An orchestrator builds sender × receiver × type matrices around a uniform CLI/JSON shim interface, separating native client behavior from test generation and reporting. [Architecture](https://github.com/apache/qpid-interop-test/blob/main/docs/ARCHITECTURE.md).
- **C3:** The rewrite documents deterministic seeded generation of large payloads to avoid transporting them through command-line arguments, plus parallel pytest execution and separate frame-size test configurations. [Change history](https://github.com/apache/qpid-interop-test/blob/main/CHANGES).

**Scope/status:** The inspected default branch is the QIT 2.0 rewrite. Some architecture-document roadmap sections lag the current README; planned features were not treated as implemented evidence.

### 11. [omg-dds/dds-rtps](https://github.com/omg-dds/dds-rtps)

**Python runner with native DDS test applications, including C/C++; DDS-RTPS vendor interoperability.** Study a standards-community test contract that different vendors compile against their own middleware.

- **C1:** Tests assert both successful matching and deliberate incompatibility: domains, XCDR representation, reliability, ownership, deadlines, and durability. Ownership tests distinguish competing writers; deadline tests check notifications when publication periods exceed the negotiated deadline. [Executable test definitions](https://github.com/omg-dds/dds-rtps/blob/master/test_suite.py).
- **C2:** A common `shape_main` program exposes QoS and endpoint parameters. Python dictionaries declare application instances, expected return codes, and optional custom checkers; the runner pairs vendor executables and generates reports. [Harness and executable contract](https://github.com/omg-dds/dds-rtps#readme).

**Scope:** These tests exercise documented interoperability scenarios. Passing them is not evidence that every DDS or RTPS feature is implemented.

### 12. [progval/irctest](https://github.com/progval/irctest)

**Python/pytest; IRC client-server conformance across RFC, modern IRC, and IRCv3 behavior.** A less widely known example of testing a protocol with several overlapping specifications and implementation conventions.

- **C1:** Capability-negotiation cases check invalid subcommands, registration suspension until `CAP END`, combinations of requested capabilities, and changes after registration. Assertions distinguish message ordering and protocol state, not merely connection success. [CAP tests](https://github.com/progval/irctest/blob/master/irctest/server_tests/cap.py).
- **C2:** Controller abstractions configure and launch different servers, clients, and services. Shared code manages per-test capabilities, port allocation under a file lock, and cleanup of process groups. [Controller implementation](https://github.com/progval/irctest/blob/master/irctest/basecontrollers.py).

**Scope:** Server-to-server IRC is explicitly excluded. Strict interpretations, deprecated extensions, and software-specific tests have separate selectors; the README acknowledges possible false positives.

### 13. [AMWA-TV/nmos-testing](https://github.com/AMWA-TV/nmos-testing)

**Python; broadcast-media NMOS API and controller interoperability.** Study how schema checks coexist with stateful tests, mock devices, and partially manual controller workflows.

- **C1:** Suites cover interactions between discovery/registration, connection management, events, channel mapping, and authorization. Pagination and scheduled activation require synchronized clocks; empty or unrepresentative device data can prevent a meaningful result. [Suite coverage and limitations](https://github.com/AMWA-TV/nmos-testing#readme).
- **C2:** `GenericTest` exposes parsed RAML specifications, schemas, and request validators. `ControllerTest` adds configurable mock senders/receivers and a testing façade. Result types distinguish failure, unsupported optional behavior, inapplicability, uncertainty, and manual checks. [Extension architecture](https://github.com/AMWA-TV/nmos-testing/blob/master/docs/5.1.%20Extension%20-%20Adding%20New%20Tests.md).

The result taxonomy is worth studying independently: an untestable condition is not silently counted as a pass.

## File access, mail, calendaring, and DNS

### 14. [microsoft/WindowsProtocolTestSuites](https://github.com/microsoft/WindowsProtocolTestSuites)

**Primarily C#/.NET, with C++ components; Windows open-protocol interoperability suites.** The monorepo includes file services, RDP, Kerberos, and Active Directory families. The SMB2/3 FileServer subsystem provides a concrete starting point.

- **C1:** The replay tests establish multichannel sessions and durable handles, break the original connection, and attempt writes with an invalid channel sequence, checking the required failure status. Applicability checks account for dialect, signing, and negotiated capabilities. [SMB replay implementation](https://github.com/microsoft/WindowsProtocolTestSuites/blob/main/TestSuites/FileServer/src/SMB2/TestSuite/Replay/Replay.cs).
- **C2:** `ProtoSDK` supplies message structures, encoders/decoders, and transports; protocol suites reuse those components alongside deployment scripts and Protocol Test Manager configuration. [Component architecture](https://github.com/microsoft/WindowsProtocolTestSuites#components).

**Scope:** Microsoft explicitly states that these suites neither cover every requirement nor certify an implementation.

### 15. [linux-nfs/pynfs](https://github.com/linux-nfs/pynfs)

**Python; NFSv4.0/v4.1 conformance and error-path testing. Official GitHub mirror of the linux-nfs repository.** Study direct RPC-level tests that can express sequences a normal filesystem client would rarely generate.

- **C1:** The NFSv4.1 harness targets unusual RPC orderings and error paths; its proxy supports operation-specific error codes, delays, probabilistic injection, and short-read behavior. This supports testing session failures and recovery independently of kernel-client policy. [NFSv4.1 testing and injection design](https://github.com/linux-nfs/pynfs/blob/master/nfs4.1/README).
- **C2:** Dependency-aware test selection, shared environments, reusable RPC/XDR machinery, and separate 4.0/4.1 trees provide infrastructure for many server implementations and protocol operations. [Repository structure](https://github.com/linux-nfs/pynfs/blob/master/README).

**Limitation:** The v4.1 guide explicitly distinguishes RPC-order correctness from precise timing/performance testing and documents limitations of its auxiliary server. Test failures still require checking the RFC and the test oracle.

### 16. [dovecot/imaptest](https://github.com/dovecot/imaptest)

**C; IMAP compliance, state tracking, and stress testing.** An especially strong study target for protocol correctness under concurrent mailbox modification.

- **C1:** State tracking detects unstable sequence-to-UID mappings, shrinking MODSEQs, unexpected metadata changes, non-atomic flag updates, and lost QRESYNC changes. Checkpointing drains pending commands and compares mailbox state across sessions. [Tracked invariants](https://github.com/dovecot/imaptest/blob/main/docs/features.md).
- **C2:** A scripted-test language supports multiple connections, pipelining, required capabilities, dynamic response-bound variables, binary literals, and monotonic MODSEQ expectations. It can describe valid response variation without hard-coding every generated identifier. [Script language](https://github.com/dovecot/imaptest/blob/main/docs/scripted_test.md).

The combination of continuously tracked state and explicit scripted exchanges makes this more instructive than a collection of independent command-response examples.

### 17. [apple/ccs-caldavtester](https://github.com/apple/ccs-caldavtester)

**Python and XML; CalDAV/CardDAV testing framework. Archived historical project.** Retained for its substantive protocol corpus and semantic verification design, with no implication of current maintenance.

- **C1:** The calendar verifier parses calendar structures, normalizes event timing, filters configured properties, reconciles recurrence overrides, and compares semantic calendar objects. This avoids equating a harmless serialization difference with a protocol defect. [Calendar comparison implementation](https://github.com/apple/ccs-caldavtester/blob/master/verifiers/calendarDataMatch.py).
- **C2:** XML scripts compose initialization, request sequences, repetition, feature requirements, cleanup, substitutions, and pluggable verifiers. The same runner can test other HTTP-based protocols by defining new scripts. [Execution and scripting design](https://github.com/apple/ccs-caldavtester/blob/master/README.md).

**Scope/status:** The archival notice says the original developers moved on. The inspected verifier uses Python 2 syntax; study or reuse requires accounting for that environment.

### 18. [CZ-NIC/deckard](https://github.com/CZ-NIC/deckard)

**Python; reproducible DNS behavior and DNSSEC test harness. CZ.NIC-hosted GitHub copy; project development and issue reporting point to its GitLab upstream.** Study deterministic control of both a resolver's client-facing replies and its upstream environment.

- **C1:** The harness intercepts upstream DNS traffic and supplies scripted responses, can withhold replies, and advances fake time for DNSSEC-related scenarios. This makes timeout and time-dependent validation cases reproducible. [Harness model](https://github.com/CZ-NIC/deckard/blob/master/README.rst).
- **C2:** Scenarios separate configuration, declarative network response ranges, and ordered test steps. Reusable matching and adjustment rules describe expected messages without coupling the whole test to a resolver's exact query order. [Scenario language](https://github.com/CZ-NIC/deckard/blob/master/doc/scenario_guide.rst).

**Scope:** User/network namespaces make the native harness Linux-specific. This is a protocol-behavior suite, not a throughput benchmark or a claim of exhaustive DNS conformance.

## Network control and cellular systems

### 19. [floodlight/oftest](https://github.com/floodlight/oftest)

**Python; OpenFlow switch test framework and suites.** An older but substantial reference for coordinating the control plane with observed forwarding behavior.

- **C1:** The conformance methodology checks overlapping flow rejection, identical-flow replacement and counter reset, flow modifications, barriers, packet-in/packet-out behavior, and error responses. It ties each setup sequence to a specific observable switch result. [Detailed test methodology](https://github.com/floodlight/oftest/blob/master/docs/Detailed_Testing_Methodology.txt).
- **C2:** The controller runs in a background thread and offers callbacks, polling queues, transaction-ID synchronization, and buffered protocol-message parsing. Together with configurable data-plane platforms, this supports both virtual and physical switches. [Controller implementation](https://github.com/floodlight/oftest/blob/master/src/python/oftest/controller.py).

**Scope/status:** The README requires Python 2.7; metadata showed a January 2024 last push. Some items in the methodology are proposed rather than completed, so it should be read alongside executable tests.

### 20. [openconfig/featureprofiles](https://github.com/openconfig/featureprofiles)

**Go; OpenConfig management/control-plane behavioral tests using Ondatra.** Study how protocol assertions are connected to telemetry and real packet forwarding across vendor testbeds.

- **C1:** The gRIBI leader-election scenario connects two clients, installs a route through the elected primary, verifies that a non-primary's update is ignored, then changes leadership and verifies forwarding changes. This joins protocol authority, persistent routing state, telemetry, and data-plane observation. [Leader-election test specification](https://github.com/openconfig/featureprofiles/blob/main/feature/gribi/otg_tests/base_leader_election_test/README.md).
- **C2:** Feature profiles group OpenConfig paths and protocol behavior; common Ondatra tests run through virtual-device KNE bindings or physical-device bindings. The structure supports gNMI/gNOI, gRIBI, and routing-protocol features under one testing approach. [Repository architecture and bindings](https://github.com/openconfig/featureprofiles#readme).

**Scope:** This is feature-level network-device validation, broader than wire-format conformance. Hardware and vendor-image requirements vary by test.

### 21. [osmocom/osmo-ttcn3-hacks](https://github.com/osmocom/osmo-ttcn3-hacks)

**TTCN-3 with C/C++ codec support and Python orchestration; cellular protocol suites. Official Osmocom GitHub mirror.** The collection covers network elements across cellular generations; the GGSN suite is a focused starting point.

- **C1:** GGSN tests increase recovery counters and verify that old PDP contexts are removed while newly created contexts survive. Duplicate deletion requests reuse cached success responses, whereas a new sequence number must receive a non-existent-context error. [Executable GTP tests](https://github.com/osmocom/osmo-ttcn3-hacks/blob/master/ggsn_tests/GGSN_Tests.ttcn).
- **C2:** Shared protocol templates, codec ports, and peer emulations support separate suites. The GGSN harness emulates SGSN-side GTP and Internet-side IP, with configurations for osmo-ggsn, kernel GTP-U, and Open5GS. [GGSN testbed architecture](https://github.com/osmocom/osmo-ttcn3-hacks/blob/master/ggsn_tests/README.md).

**Scope/status:** The [Osmocom organization](https://github.com/osmocom) identifies these repositories as official mirrors; upstream development uses Osmocom infrastructure. Not every suite is an implementation-independent certification test.

## Federated and distributed protocol suites

### 22. [matrix-org/complement](https://github.com/matrix-org/complement)

**Go; Matrix homeserver compliance and black-box integration testing.** Study explicit control of a federated peer to produce hard-to-reproduce event histories.

- **C1:** A concrete test withholds event A, sends dependent event B so it is rejected, supplies A, and resends B. It then checks that B is accepted and appears after A through the client sync API. This tests recovery from incomplete federated history across two protocol surfaces. [Rejected-event recovery test](https://github.com/matrix-org/complement/blob/main/tests/federation_unreject_rejected_test.go).
- **C2:** Docker-based homeserver deployments, client helpers, configurable mock federation handlers, and a local test PKI let tests target different implementations while sharing setup and assertion machinery. [Framework setup and organization](https://github.com/matrix-org/complement#readme).

**Scope:** The repository separates experimental Matrix proposal tests from stable tests. Its README points end-to-end encryption-specific testing to a separate project, which is not counted here.

### 23. [matrix-org/sytest](https://github.com/matrix-org/sytest)

**Perl; original Matrix black-box integration suite.** Included separately from Complement because it is a distinct implementation with a substantial asynchronous runner and fixture architecture, not a fork or wrapper.

- **C1:** Federation transaction tests exercise message-count limits and malformed canonical JSON, including the distinction between discarding an invalid event and rejecting an entire transaction. The source explicitly marks differing implementation expectations. [Federation transaction tests](https://github.com/matrix-org/sytest/blob/develop/tests/50federation/51transactions.pl).
- **C2:** Future-returning test blocks, dependency declarations, homeserver factories, and lazily created fixtures coordinate multiple servers. The developer guide explains why shared accumulated state made tests fragile and how setup/teardown fixtures reduce that coupling. [Runner and fixture design](https://github.com/matrix-org/sytest/blob/develop/DEVELOP.rst).

**Scope/status:** The README says new tests tend to be written in Complement. Implementation-specific accepted behavior in SyTest must not automatically be interpreted as normative Matrix compliance.

### 24. [libp2p/test-plans](https://github.com/libp2p/test-plans)

**Python/TypeScript orchestration with multiple native implementations; transport, hole-punching, and GossipSub interoperability.** Study how independent language implementations are tested under the same network scenario.

- **C1:** The hole-punch suite creates separate NATed LANs, a relay, and dialing/listening peers. It coordinates relay reservations, peer discovery, security/multiplexer negotiation, and transition to the direct connection, with explicit exit and timeout behavior. [Hole-punch topology and protocol flow](https://github.com/libp2p/test-plans/blob/master/hole-punch-interop/README.md).
- **C2:** GossipSub testing separates timed scenarios from the mixture of implementations. Shadow simulation, common instructions, configurable protocol parameters, and saved experiment artifacts permit the same scenario to be replayed across homogeneous and mixed networks. [GossipSub framework](https://github.com/libp2p/test-plans/blob/master/gossipsub-interop/README.md).

**Scope:** These subsystems use different runners. GossipSub's reported delivery, latency, and duplicate-message metrics are experimental observations, not claimed performance guarantees.

### 25. [ethereum/hive](https://github.com/ethereum/hive)

**Go harness with language-independent simulator containers; Ethereum client interoperability.** Focus on network synchronization, peer protocols, JSON-RPC, and Engine API simulations rather than treating all Ethereum implementation code as part of this category.

- **C1:** Synchronization simulations use each client as a source and test other clients as sinks. Engine API simulations act as a consensus client to validate execution-client responses during chain progression; peer-protocol simulations analyze responses to controlled messages. [Simulator responsibilities](https://github.com/ethereum/hive/blob/master/docs/overview.md).
- **C2:** A controller API launches clients with common genesis, fork, and test-chain configuration. Simulator programs can use any language, while the harness normalizes client startup, result reporting, log collection, and container cleanup. [Architecture and simulation API boundary](https://github.com/ethereum/hive/blob/master/docs/overview.md#how-it-works).

**Scope:** Some peer-protocol test logic is maintained in go-ethereum and adapted by Hive; this entry credits Hive's substantive orchestration and simulator subsystem, not independent authorship of every imported test.

## Search coverage, verification, and limitations

Discovery used more than six distinct live search formulations, including HTTP/2/WebSocket conformance; TLS adversarial testing; QUIC interoperability runners; MQTT/CoAP testware; NFS/SMB suites; DNS/IMAP/CalDAV testing; OpenFlow/P4/network-control tests; gRPC/Matrix compliance; AMQP/JMS; DDS/RTPS; cellular TTCN-3/SIP/Diameter; and industrial/NETCONF protocols. Later broader searches mostly added implementations, device simulators, specification documents, and previously found runners rather than equally strong independent suites. IRC and the official Osmocom mirror were useful later discoveries. Selection spans standalone small runners, reusable protocol test frameworks, vendor matrices, hardware testbeds, and large test monorepos; popularity was not a selection criterion.

Every retained canonical repository was checked through its GitHub page or GitHub API. At least one additional primary document or source file was opened for each, and the cited material includes substantive implementation or architectural details. GitHub archive/default-branch metadata was checked. Ordinary entries do not imply a maintenance guarantee; material archival, legacy-runtime, and mirror qualifications appear locally. For Deckard, the GitHub copy is in CZ.NIC's own organization and retains substantial source, while its homepage and contribution direction point to GitLab; mirror freshness was not independently compared commit-for-commit.

The selection excludes generic scanners and packet generators without an adequate conformance oracle, thin per-implementation interoperability containers, and duplicate forks. The [OpenID Foundation's conformance suite](https://openid.net/certification/about-conformance-suite/) points to GitLab; an authoritative substantive GitHub mirror was not established, so it is excluded. Eclipse's CoAP testware was inspected but not retained: the examined suite was smaller and contained incomplete/repeated test wrappers, while Osmocom provided a stronger TTCN-3 study target. Industrial-protocol and NETCONF searches frequently returned simulators or ordinary implementation tests; no claim of exhaustive coverage of those ecosystems, XMPP, or proprietary certification suites is made.

All work was read-only internet research followed by writing this report. No candidate dependencies were installed, repositories cloned, test programs executed, external services modified, or maintainers contacted. Criteria judgments and suggested learning value are grounded in the inspected design, not measured code quality. Passing any particular suite establishes only the observations and assumptions encoded by that suite.
