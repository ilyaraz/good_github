# Financial messaging and market data protocol libraries

Research date: **2026-10-09**

This report selects **24 GitHub repositories** implementing financial session protocols, binary market-data encodings, exchange transports, market-data distribution, and payment-message formats. It includes ACH batch interchange because it carries financial instructions, while excluding trading strategies, matching engines, generic networking frameworks, and ordinary REST client wrappers. The emphasis is on engineering that an experienced developer can study: recovery state machines, encoding semantics, buffer ownership, extensibility, and compatibility.

Criteria describe the evidence inspected, not a certification of every component:

- **C1 — Difficult correctness:** protocol invariants, concurrency, numeric representation, malformed input, or recovery from failure.
- **C2 — Reusable abstractions:** substantial components usable across message types, counterparties, applications, or transports.
- **C3 — Performance with structure:** concrete choices addressing allocation, copying, throughput, or latency, with an understandable architecture.
- **C4 — Sustained evolution:** dated history accompanied by compatibility work, tests, or explicit complexity management; age alone is insufficient.

Each linked repository heading was checked against its GitHub repository page. The implementation and documentation links below are reading entry points verified separately from the root README. None of the selected repositories was marked archived in the checked GitHub metadata. That does not establish current maintenance; historical cases are explicitly identified. Branch links describe the inspected development trees and can move after this research date.

## FIX session engines and libraries

### 1. [quickfix/quickfix](https://github.com/quickfix/quickfix)

**C++; full FIX engine with language bindings.** A useful baseline for understanding how a financial session outlives its TCP connection. Study the interaction of application callbacks, message persistence, data dictionaries, and independent incoming/outgoing sequence numbers.

- **C1:** The session implementation queues messages received ahead of sequence, generates retransmissions or sequence-reset gap fills, and coordinates logon recovery with persisted state. The `NextExpectedMsgSeqNum` path also shows the different recovery behavior when message persistence is disabled. Read [`Session.cpp`](https://github.com/quickfix/quickfix/blob/master/src/C++/Session.cpp).
- **C2:** Message-store and log factories, application callbacks, and the data-dictionary provider are injected into the session rather than being tied to a particular broker or storage engine. The same source exposes these boundaries and their lifecycle.

The [NEWS history](https://github.com/quickfix/quickfix/blob/master/NEWS) is a useful second entry point for changes to sequence synchronization, timestamp precision, session schedules, and protocol edge cases. The separate Java, C#, and Go projects below are substantive language implementations, not additional listings of these bindings.

### 2. [quickfix-j/quickfixj](https://github.com/quickfix-j/quickfixj)

**Java; FIX engine and extensible session infrastructure.** Particularly instructive for protocol deadlocks and the boundary between synchronization, persistence, and application callbacks.

- **C1:** `nextResendRequest` explains why a request with a sequence number that is too high must still be serviced: queuing it immediately can leave both counterparties waiting for each other's resend. Sequence-reset handling also reconciles queued messages and chunked resend ranges. Read [`Session.java`](https://github.com/quickfix-j/quickfixj/blob/master/quickfixj-core/src/main/java/quickfix/Session.java).
- **C2:** The session coordinates replaceable responders, message stores, application callbacks, and dictionary-driven validation. These allow the same protocol implementation to serve different transports, persistence choices, and FIX application versions. The repository additionally separates engine, generated messages, dictionary generation, and performance/stress tooling into modules.

The explicit deadlock rationale makes this more valuable than merely comparing its API with the C++ implementation; the code records why apparently stricter sequencing would be wrong.

### 3. [connamara/quickfixn](https://github.com/connamara/quickfixn)

**C#; native .NET FIX engine.** Study how the QuickFIX session model is maintained alongside .NET-specific APIs and type evolution.

- **C1:** [`Session.cs`](https://github.com/connamara/quickfixn/blob/master/QuickFIXn/Session.cs) handles persisted replay, special unbounded resend values, duplicate requests, and sequence resets that must not move the target sequence backward. Its CME enhanced-resend path illustrates a venue-specific complication within the shared state machine.
- **C2:** Application and message-factory interfaces, separate session/application dictionaries, and message-store factories support custom counterparties without replacing the engine. The repository's DDTool generates message and field classes from dictionaries.

Read the [release notes](https://github.com/connamara/quickfixn/blob/master/RELEASE_NOTES.md) alongside the session code: they explicitly describe package renaming, framework migrations, repeating-group fixes, and the transition of date/time fields to .NET `DateOnly`/`TimeOnly`. Development-tree migration notices should not be mistaken for a recommendation to use an unreleased version.

### 4. [quickfixgo/quickfix](https://github.com/quickfixgo/quickfix)

**Go; FIX engine with explicit session-state types.** A strong comparison with the larger single-session classes above: behavior is divided among logged-on, resend, timeout, logon, and logout states.

- **C1:** [`resend_state.go`](https://github.com/quickfixgo/quickfix/blob/main/resend_state.go) preserves recovery state across pending timeouts, retains a stash of out-of-order messages, and advances chunked resend ranges using the store's next expected sequence number. These are concrete interactions between liveness and ordering.
- **C2:** [`in_session.go`](https://github.com/quickfixgo/quickfix/blob/main/in_session.go) supplies normal logged-on behavior that recovery states reuse. The wider engine combines this state interface with dictionary-based validation, generated typed messages, and interchangeable stores.

Useful study question: which responsibilities belong in a reusable state transition, and which must remain coupled to durable sequence numbers? The small recovery module makes that boundary easy to inspect.

### 5. [artiofix/artio](https://github.com/artiofix/artio)

**Java; FIX/FIXP gateway with a separated engine and application library.** Study a substantially different deployment architecture from an embedded callback engine.

- **C1:** Replay distinguishes actual messages from administrative gap fills and identifies sequence-number epochs with a sequence index. Reacquiring a session can replay messages missed by an application; disabling persistent logging removes that capability. These semantics are explained in [Replays](https://github.com/artiofix/artio/wiki/Replays).
- **C2:** Engine-owned networking and persistence are separated from application-side libraries managing sessions, allowing session ownership to be transferred through explicit APIs.
- **C3:** The [architecture overview](https://github.com/artiofix/artio/wiki/Overview) decomposes work into single-threaded Framer, Indexer, and Replayer agents connected through Aeron streams. It explains IPC versus UDP placement, session multiplexing, and the requirement to keep each library and its sessions on one thread.

The interesting lesson is the relationship between recovery guarantees and ownership boundaries, rather than an isolated latency claim.

### 6. [fix8/fix8](https://github.com/fix8/fix8)

**C++; FIX schema compiler and runtime framework.** Useful for studying specialization: the project combines generated field/message encoders and decoders with a shared runtime, instead of treating all messages as generic tag maps.

- **C1:** [`runtime/session.cpp`](https://github.com/fix8/fix8/blob/master/runtime/session.cpp) routes administrative messages through logon, resend, sequence-reset, and logout handlers. Message construction can fail before dispatch, while sequence advancement and persistence must follow the correct path; the source documents the need to persist the logout sequence before termination.
- **C2:** The compiler/runtime split supports custom schemas, generated instantiation tables, and application-specific session behavior. This architecture is described in the [project overview](https://github.com/fix8/fix8/blob/master/README.md) and exercised by the shared runtime's message factory.

Read the generated-code boundary together with the runtime handler paths. It exposes the costs and benefits of moving schema knowledge into C++ types while retaining configurable session behavior.

### 7. [paritytrading/philadelphia](https://github.com/paritytrading/philadelphia)

**Java; compact FIX library with reusable message containers.** A less expansive alternative for studying buffer-oriented parsing and protocol profiles.

- **C1:** [`FIXMessageParser.java`](https://github.com/paritytrading/philadelphia/blob/main/libraries/core/src/main/java/com/paritytrading/philadelphia/FIXMessageParser.java) uses buffer marks and resets for incomplete input, constrains the message body with a temporary buffer limit, checks checksums when configured, and scans past garbled messages.
- **C3:** The parser reuses its message object and consumes a `ByteBuffer` directly. This makes the allocation and callback-lifetime tradeoff visible, rather than hiding it behind a broad framework.
- **C4:** The [changelog](https://github.com/paritytrading/philadelphia/blob/main/CHANGELOG.md) documents releases from 2015 through 2022, upgrade guides, FIXT corrections, and changes to string views and internal APIs. Its subsequent development section also documents integer-format and overflow handling; that undated section is not counted as a released version.

## Binary financial encodings

### 8. [aeron-io/simple-binary-encoding](https://github.com/aeron-io/simple-binary-encoding)

**Java generator with multiple language targets; SBE codecs.** This is the canonical repository reached from the former `real-logic/simple-binary-encoding` URL. It belongs here because SBE is explicitly designed for low-latency financial application messages, although its codecs are reusable elsewhere.

- **C2:** XML schemas drive codecs across Java, C++, C#, Go, Rust, and other supported targets; the shared representation is a substantial cross-language abstraction rather than a collection of endpoint wrappers.
- **C3:** [Design Principles](https://github.com/aeron-io/simple-binary-encoding/wiki/Design-Principles) explains direct buffer access, flyweight objects, native field representations, and forward streaming access. It also states the consequence: retained data must be copied out, and messages larger than transfer buffers need an external fragmentation mechanism.
- **C1:** The same design document distinguishes compatible optional-field extensions from mandatory or structural changes requiring a new message type. This is a concrete wire-compatibility invariant, not a claim that all arbitrary schema changes are safe.

Study the constraints alongside the optimizations; they explain when this encoding is appropriate.

### 9. [objectcomputing/mFAST](https://github.com/objectcomputing/mFAST)

**C++; FAST encoder/decoder with generated application types.** Especially useful for comparing generated typed access with runtime template interpretation.

- **C2:** The [design and usage article](https://objectcomputing.github.io/mFAST/) explains a compact application type system, generated C++ types from FAST XML templates, mutable/constant references, and visitor-based operations. Applications can also use templates parsed at runtime.
- **C3:** The design uses region-based memory management and flyweight access, avoids string-based field lookup for generated types, and makes encoder/decoder visitors independently linkable. Those are inspectable structural performance choices; the article's old machine-specific speed ratios are deliberately not reproduced here.

**Limit:** The [repository's compatibility notes](https://github.com/objectcomputing/mFAST/blob/master/ReadMe.md) explicitly describe only partial FAST 1.2 support, including unsupported SET, BIT GROUP, and TIMESTAMP features. mFAST is a separate implementation built from the ground up, not merely a fork listing of QuickFAST.

### 10. [objectcomputing/quickfast](https://github.com/objectcomputing/quickfast)

**C++ with .NET integration; historical FAST implementation.** Study runtime template interpretation, application builders, and feed sequencing as an alternative design to mFAST.

- **C1:** [`Decoder.cpp`](https://github.com/objectcomputing/quickfast/blob/master/src/Codecs/Decoder.cpp) decodes presence maps, reuses template IDs, applies template resets, recognizes the reset template, and reports unknown templates. These operations share state across compressed messages.
- **C2:** Decoding is separated into data sources, template/context machinery, and a `ValueMessageBuilder`, so applications can choose how decoded values become messages.
- **C3:** [`PacketSequencingAssembler.cpp`](https://github.com/objectcomputing/quickfast/blob/master/src/Codecs/PacketSequencingAssembler.cpp) separates bounded look-ahead storage, deferred packets, and recovery-feed processing. It is a useful study of ordered delivery over redundant or incomplete packet streams.

**Historical status:** The checked [default-branch commit feed](https://github.com/objectcomputing/quickfast/commits/master.atom) ends in March 2017. Treat this as a design reference requiring fresh build and dependency evaluation, not evidence of current maintenance.

## Exchange protocols and transport recovery

### 11. [libtrading/libtrading](https://github.com/libtrading/libtrading)

**C API usable from C++; historical multi-protocol trading connectivity library.** Covers FIX, FAST, and exchange-specific protocols including ITCH and OUCH. It offers a useful contrast with both generated C++ frameworks and JVM middleware.

- **C1:** [`fast_message.c`](https://github.com/libtrading/libtrading/blob/master/lib/proto/fast_message.c) makes FAST field states explicit: undefined, assigned, and empty values behave differently under copy, delta, default, and optional-field rules. Partial and garbled input are distinguished.
- **C2:** The [quick-start/API guide](https://github.com/libtrading/libtrading/blob/master/docs/quickstart.md) describes session configuration, message representations, typed fields, and FAST templates as reusable C-level components, rather than a single exchange application.

**Historical status:** The checked [default-branch commit feed](https://github.com/libtrading/libtrading/commits/master.atom) ends in January 2018. Its published latency examples use an old hardware/software environment and are not presented here as contemporary measurements. The value is in the compact implementation and explicit wire-state semantics.

### 12. [paritytrading/nassau](https://github.com/paritytrading/nassau)

**Java; SoupBinTCP, MoldUDP64, and BinaryFILE transport library.** A strong small codebase for separating reliable delivery from the application messages carried inside it.

- **C1:** [`MoldUDP64Client.java`](https://github.com/paritytrading/nassau/blob/main/libraries/core/src/main/java/com/paritytrading/nassau/moldudp64/MoldUDP64Client.java) distinguishes backfill, gap-fill, and synchronized states; tracks expected sequence numbers; retries timed-out requests; and skips already-received messages.
- **C3:** The client allocates direct receive/transmit buffers at construction and dispatches through listeners. Blocking/nonblocking channel choices and recovery channels remain explicit.
- **C4:** The [changelog](https://github.com/paritytrading/nassau/blob/main/CHANGELOG.md) spans 2014–2022 and records sequence/count fixes, API migration, resource-management work, and correction of coordinated omission in a performance test. This is unusually useful evidence of benchmark methodology evolving with the implementation.

The last dated release in that changelog is 1.0.0 in 2022; no stronger release-cadence claim is implied.

### 13. [paritytrading/juncture](https://github.com/paritytrading/juncture)

**Java; exchange application-message codecs, currently focused on Nasdaq ITCH 5.0.** It complements Nassau's transport framing with typed application messages and is a separate implementation layer, not a duplicate transport library.

- **C2:** [`ITCH50.java`](https://github.com/paritytrading/juncture/blob/main/libraries/nasdaq/src/main/java/com/paritytrading/juncture/nasdaq/itch50/ITCH50.java) supplies message structures and symmetric buffer readers/writers for order additions, executions, cancellations, trades, auctions, and status events. The types can serve recorders, book builders, and replay tools.
- **C3:** [`ITCH50Parser.java`](https://github.com/paritytrading/juncture/blob/main/libraries/nasdaq/src/main/java/com/paritytrading/juncture/nasdaq/itch50/ITCH50Parser.java) constructs message instances once, dispatches by type byte, and integrates through Nassau's `MessageListener`. Reuse makes object lifetime across callbacks an important study point.

**Scope limit:** The [changelog](https://github.com/paritytrading/juncture/blob/main/CHANGELOG.md) explicitly removed Cboe FX support in 1.0.0 because its documentation was no longer public. This report does not credit that historical capability as current support.

## Market-data middleware and normalized feeds

### 14. [finos/OpenMAMA](https://github.com/finos/OpenMAMA)

**C/C++ core with Java and C# APIs; middleware and payload abstraction, plus OpenMAMDA market-data functionality.** Counted once for the `mama` and `mamda` subsystems. Study integration boundaries that must preserve lifecycle semantics across very different messaging providers.

- **C2:** The [bridge architecture](https://openmama.finos.org/openmama_bridge.html) describes per-bridge virtual function tables and distinct transport, queue, timer, subscription, publisher, and payload components. Multiple middleware and wire-format implementations can coexist in one application.
- **C1:** The [developer guide](https://openmama.finos.org/openmama_developer_guide.html) specifies dispatch-thread restrictions and shutdown ordering: stop dispatch, destroy event objects, then queues and transports. Event queues must outlive the subscriptions and timers using them.

This is retained for its substantive bridge contracts, event lifecycle, and market-data layer; the project is broader than a thin wrapper around a single provider SDK.

### 15. [Refinitiv/Real-Time-SDK](https://github.com/Refinitiv/Real-Time-SDK)

**C/C++, Java, and C#; LSEG Real-Time SDK, particularly ETA codecs and Reactor/Watchlist beneath EMA.** The canonical GitHub owner remains `Refinitiv` despite the LSEG product name. Count the monorepo once.

- **C1:** [`DecodeIteratorImpl.java`](https://github.com/Refinitiv/Real-Time-SDK/blob/master/Java/Eta/Core/src/main/java/com/refinitiv/eta/codec/DecodeIteratorImpl.java) tracks nested decoding levels, buffer position, wire-format version, and field/element set definitions. It exposes the state required for a container-oriented financial wire format.
- **C2:** [`Watchlist.java`](https://github.com/Refinitiv/Real-Time-SDK/blob/master/Java/Eta/ValueAdd/src/main/java/com/refinitiv/eta/valueadd/reactor/Watchlist.java) separates login, directory, and item handlers, maps application requests to streams, and dispatches timeouts. EMA builds a higher-level API over this reusable lower-level machinery.

Study both layers to understand why an application API and a protocol engine need different abstractions. The root documentation distinguishes the open-source implementation directories from separately governed dependencies and materials; this entry concerns the former.

### 16. [devexperts/QD](https://github.com/devexperts/QD)

**Java; Quote Distribution subsystem and dxFeed infrastructure.** Relevant monorepo components include `qd-core`'s QTP protocol implementation, record schemes, and feed/event interfaces. The repository is considerably more substantial than a market-data download client.

- **C1:** [`BinaryQTPParser.java`](https://github.com/devexperts/QD/blob/master/qd-core/src/main/java/com/devexperts/qd/qtp/BinaryQTPParser.java) distinguishes incomplete input from corrupt lengths/messages, marks and resets input when bytes are missing, enforces a maximum message size, and invokes resynchronization/error handling without discarding already-valid work indiscriminately.
- **C2:** Parsing is parameterized by a data scheme and symbol codec and uses protocol/record descriptions rather than hard-coding a single exchange schema. The parser's consumer boundary separates wire handling from downstream processing.

The [release notes](https://github.com/devexperts/QD/blob/master/ReleaseNotes.txt) are a useful companion for decimal-format interoperability, reconnect behavior, evolving subscription semantics, and explicitly marked incompatible API changes. No blanket claim of transparent compatibility across every version is intended.

### 17. [databento/dbn](https://github.com/databento/dbn)

**Rust core with Python/C integration; Databento Binary Encoding.** Study a normalized market-data format shared by live streams, historical streams, and files, rather than an HTTP API wrapper.

- **C1:** [`decode/dbn/fsm.rs`](https://github.com/databento/dbn/blob/main/rust/dbn/src/decode/dbn/fsm.rs) separates prelude, metadata, record, and consumption states. It explicitly represents the need for more bytes, successful metadata/records, and errors while tracking input format versions and upgrade policy.
- **C2:** The decoder state machine is independent of I/O and underlies synchronous/asynchronous integrations. [`decode/dbn/sync.rs`](https://github.com/databento/dbn/blob/main/rust/dbn/src/decode/dbn/sync.rs) adapts it to `io::Read`, files, compressed streams, metadata access, and explicit version-upgrade choices.
- **C3:** Aligned input/compatibility buffers, record references, and batch processing make copying, ownership, and upgrading costs visible in the state machine.

The distinction between input representation and upgraded output representation is the central architectural lesson.

### 18. [bmoscon/cryptofeed](https://github.com/bmoscon/cryptofeed)

**Python; multiple exchange WebSocket/REST feed handlers with normalized events.** Retained for application-protocol reconciliation and stateful order-book ingestion, not merely the existence of many exchange adapters.

- **C1:** The [Binance implementation](https://github.com/bmoscon/cryptofeed/blob/master/cryptofeed/exchanges/binance.py) reconciles snapshot sequence numbers with incremental update ranges, ignores old messages, and drops/reset books when continuity is lost. Snapshot numeric values are parsed with `Decimal` before constructing book levels.
- **C2:** Exchange-specific messages are converted into common order-book/event objects and delivered through registered callbacks. The [project interface overview](https://github.com/bmoscon/cryptofeed/blob/master/README.md) describes the shared event vocabulary and feeds, while the Binance source shows the normalization boundary in practice.

A useful study of the difficulty hidden behind a uniform API: each venue still has its own sequencing and snapshot rules. The inspected adapter is evidence for those mechanisms, not proof of uniform correctness across every supported exchange.

## Payment and bank-message libraries

### 19. [jpos/jPOS](https://github.com/jpos/jPOS)

**Java; ISO 8583 messaging framework.** The relevant subsystem is its ISO message/channel/packager infrastructure, although the repository also provides a larger runtime. Study how a common message model supports many incompatible network dialects.

- **C1:** [`BaseChannel.java`](https://github.com/jpos/jPOS/blob/main/jpos/src/main/java/org/jpos/iso/BaseChannel.java) coordinates input locking, connection state, message lengths, keepalives, raw-message processing, and filtering. Its receive path explicitly preserves the socket reference needed for diagnostics while another path may close the channel.
- **C2:** [`GenericPackager.java`](https://github.com/jpos/jPOS/blob/main/jpos/src/main/java/org/jpos/iso/packager/GenericPackager.java) builds field packing behavior from XML definitions. Combined with channel subclasses and incoming/outgoing filters, this separates network framing, field representation, and application processing.

This is a good entry point for studying interoperability without pretending ISO 8583 is one universally interchangeable wire format. The repository's license is AGPL; commercial licensing is documented by the project.

### 20. [moov-io/iso8583](https://github.com/moov-io/iso8583)

**Go; ISO 8583 construction and parsing with configurable field specifications.** Particularly useful for nested fields and the distinction between tagged and positional composites.

- **C1:** [`field/composite.go`](https://github.com/moov-io/iso8583/blob/master/field/composite.go) explains why tagged subfields can arrive out of order or be absent, while positional subfields cannot use those freedoms. Packing sorts tags deterministically; unpacking delegates each subfield's length/data semantics to its own specification.
- **C2:** A composite itself implements the field interfaces, so nested structures can reuse the same specification, padding, encoding, prefix, and marshal/unmarshal machinery. The [usage guide](https://github.com/moov-io/iso8583/blob/master/README.md) connects these specifications to typed Go application structures and custom network variants.

Study the recursive field abstraction and its invariants rather than starting with a single standard example message. The extensibility is needed precisely because participating systems specialize the format.

### 21. [knovichikhin/pyiso8583](https://github.com/knovichikhin/pyiso8583)

**Python; focused ISO 8583 byte/dictionary codec.** A smaller substantive library whose boundary is deliberately narrower than jPOS: it exposes message representation without providing a payment-switch runtime.

- **C1:** [`decoder.py`](https://github.com/knovichikhin/pyiso8583/blob/master/iso8583/decoder.py) processes extended bitmaps, checks length prefixes and field bounds, distinguishes byte/nibble counts, and rejects extra data after the final field. Its errors preserve partially decoded/encoded dictionaries and the failure position.
- **C2:** The [specification model](https://github.com/knovichikhin/pyiso8583/blob/master/README.rst) separates data encoding, length encoding, length units, maximum sizes, and fixed/variable field forms. Multiple network specifications can coexist without changing decoder logic.

Useful for studying diagnostic quality and avoiding a common error: treating binary, BCD, ASCII, and EBCDIC field lengths as interchangeable character counts.

### 22. [prowide/prowide-core](https://github.com/prowide/prowide-core)

**Java; SWIFT FIN/MT model, parser, writers, and utilities.** Study tolerance and preservation when real financial messages contain special blocks, nested messages, and irregular content.

- **C1:** [`SwiftParser.java`](https://github.com/prowide/prowide-core/blob/main/src/main/java/com/prowidesoftware/swift/io/parser/SwiftParser.java) distinguishes text blocks from tag-list blocks, preserves unparsed content, and balances braces only for tag names where the standard permits nested blocks. The source explains why applying that change indiscriminately would alter historical handling of malformed messages.
- **C2:** Shared message/block/tag models support typed MT classes, conversion, writing, and application utilities across message categories rather than a single payment type.
- **C4:** The [changelog](https://github.com/prowide/prowide-core/blob/main/CHANGELOG.md) spans 2006–2026, including parser/writer regression fixes, model simplification, sequence-boundary corrections, and standards-release updates.

The open-source model/parser should not be conflated with Prowide's separately offered comprehensive message validation and translation products.

### 23. [prowide/prowide-iso20022](https://github.com/prowide/prowide-iso20022)

**Java; ISO 20022 MX models plus a substantive XML/header parsing layer.** Retained despite generated model directories because the handwritten core solves significant integration problems beyond schema-to-class generation.

- **C2:** [`MxReadImpl.java`](https://github.com/prowide/prowide-iso20022/blob/main/iso20022-core/src/main/java/com/prowidesoftware/swift/model/mx/MxReadImpl.java) explains its SAX-based extraction of `AppHdr` and `Document` from arbitrary envelopes, header-version detection, and a shared dictionary whose types are reused across message definitions.
- **C1:** The same implementation documents deliberate namespace behavior, including different treatment for system messages and headers. This makes the consequences of the shared model explicit rather than assuming generic JAXB unmarshalling is sufficient.
- **C4:** The [2020–2026 changelog](https://github.com/prowide/prowide-iso20022/blob/main/CHANGELOG.md) records parser refactoring, header-version support, wildcard round-trip handling, date/time fixes, and migration notes when dictionary classes change.

This is a separate parser/model architecture from FIN/MT. Restricted usage guidelines and full SWIFT business-rule validation are not implied by successful XML parsing.

### 24. [moov-io/ach](https://github.com/moov-io/ach)

**Go; ACH financial interchange file reader, writer, and validator.** Included as a batch-message protocol library; the relevant code is the core ACH representation and validation, not the optional server.

- **C1:** [`file.go`](https://github.com/moov-io/ach/blob/master/file.go) aggregates entry/addenda counts, entry hashes, debit/credit amounts, batch numbering, and file block counts. `Create` and validation are distinct operations, with explicit options controlling exceptions to ordinary validation behavior.
- **C2:** The [project guide](https://github.com/moov-io/ach/blob/master/README.md) describes a reusable reader/writer/validator across ACH record and entry categories. The source exposes batch interfaces and international-batch handling under the shared file model.

Study how redundant control records become invariants that can be recomputed and checked. Format validation is a specific library capability; it is not a statement that every file is authorized, accepted by a bank, or compliant with every operational rule.

## Coverage, search process, and limitations

Discovery used live web searches followed by repository-page checks and separate primary implementation/documentation reads. More than six distinct search formulations were used, including:

1. `GitHub FIX protocol engine QuickFIX QuickFIXJ QuickFIXn` and language-specific Rust/Go/FIX8/Artio searches.
2. `GitHub FAST protocol encoder decoder OpenFAST mFAST` and follow-up searches for the financial OpenFAST implementation.
3. `GitHub Nasdaq ITCH SoupBinTCP MoldUDP64 library` and searches for Nassau, Libtrading, and Rust ITCH parsers.
4. `GitHub Simple Binary Encoding OpenMAMA Real-Time-SDK dxFeed QD` and separate canonical-project queries.
5. `GitHub ISO 20022 SWIFT ISO8583 financial messaging library`, followed by jPOS, Moov, Prowide, and Python codec searches.
6. Searches for DBN's native format implementation and C# market-data protocol libraries.
7. Additional searches for FpML and financial-protocol libraries in OCaml, Haskell, and Erlang to test language and protocol blind spots.

Later searches increasingly returned already-covered projects, generated model packages, provider wrappers, educational feed simulators, and unrelated meanings of “FAST.” The result deliberately balances embedded engines, compiler-driven codecs, small direct-buffer libraries, large vendor/community middleware, and payment formats across C, C++, C#, Java, Go, Python, and Rust.

**Important exclusions:** matching engines, order-book-only projects, REST SDKs without meaningful protocol machinery, sample applications, and generated-only wrappers were not retained. The financial OpenFAST project was linked by QuickFAST to SourceForge; this research did not establish an official substantive GitHub repository for it. The prominent `OpenFAST/openfast` search result is wind-turbine simulation software and unrelated. Tiny ITCH demonstrations and FPGA learning projects were not used to pad the list. FpML and functional-language searches did not yield sufficiently verified additions within this pass; this is a coverage limitation, not a claim those ecosystems lack useful work.

**Evidence limits:** repository pages, raw source files, project guides, changelogs, and selected public commit feeds were read; no candidate code was executed, no dependencies were installed, and no performance claims were independently benchmarked. The unauthenticated GitHub API reached its shared rate limit, so remaining verification used normal public repository pages and raw files. Architecture and criteria judgments are grounded engineering interpretations of those sources. Historical inactivity is stated where checked; an unarchived repository, a recent edit, or a standards-support claim alone is not taken as evidence of production suitability.
