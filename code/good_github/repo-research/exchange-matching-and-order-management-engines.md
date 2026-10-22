# Exchange matching and order management engines

Research date: **2026-10-09**.

This report selects **18 GitHub repositories** implementing exchange matching, order-book execution, or substantive financial order-management engines. It covers embeddable libraries, exchange services, trading OMS subsystems, and decentralized order books and batch clearing. Trading-platform monorepos are included only for the named execution subsystem. Retail fulfillment systems, market-data-only books, exchange API wrappers, and strategy collections are outside scope.

The criteria identify worthwhile engineering study, not deployment readiness or proof of correctness. Architecture conclusions below are grounded in inspected implementation and documentation; performance figures were not reproduced. Repository identity, default branch, fork status, and archive status were checked through the public GitHub API. None of the retained repositories was marked archived at inspection. Older projects are identified explicitly; an unarchived repository or a recent push does not establish maintenance quality.

## Criteria legend

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or failure and recovery behavior.
- **C2 — Reusable abstractions:** substantial components and interfaces supporting multiple instruments, venues, applications, or execution policies.
- **C3 — Performance with structure:** concrete responses to throughput, latency, allocation, memory-layout, or execution-budget constraints within an understandable architecture.
- **C4 — Sustained evolution:** multi-year evidence of testing, compatibility work, migrations, or deliberate complexity management. Age alone does not qualify.

## Embeddable matching engines

### 1. [exchange-core/exchange-core](https://github.com/exchange-core/exchange-core)

**Java — matching, risk/accounting, and persistence core.** A strong study of how order matching fits into a staged exchange pipeline. The repository describes Disruptor stages partitioned by account and symbol, integer arithmetic, journaling, and both simple and optimized book implementations. Treat it as an established reference with limited recent activity: the last repository push observed was October 2023.

- **C1:** The optimized book explicitly validates correspondence between its order-ID index and linked order chains, duplicate IDs, link direction, price ordering, and aggregate bucket volume. The shared test suite covers unauthorized cancellation/amendment and unknown or duplicate orders, making the invariants inspectable rather than merely advertised. See [OrderBookDirectImpl.java](https://github.com/exchange-core/exchange-core/blob/master/src/main/java/exchange/core2/core/orderbook/OrderBookDirectImpl.java) and [OrderBookBaseTest.java](https://github.com/exchange-core/exchange-core/blob/master/src/test/java/exchange/core2/core/orderbook/OrderBookBaseTest.java).
- **C3:** Adaptive radix trees index prices and orders; pooled order and bucket objects and cached best orders reduce allocation and traversal costs. Comparing this representation with the simpler implementation is useful for understanding the complexity introduced by optimization. The README also states which network and persistence costs its benchmarks omit.

### 2. [enewhuis/liquibook](https://github.com/enewhuis/liquibook)

**C++ — header-only matching library.** Particularly useful for studying how a matcher can integrate with an application's existing order model. This is a matching component, with accounting and transport left to its host. The last repository push observed was March 2024.

- **C1:** Matching distinguishes ordinary orders from all-or-none orders and tracks deferred candidate matches when quantity conditions prevent immediate execution. Cancellation, replacement, and partial fills complicate callback ordering and remaining-quantity accounting. The [matching implementation](https://github.com/enewhuis/liquibook/blob/master/src/book/order_book.h) exposes these paths directly; [unit tests](https://github.com/enewhuis/liquibook/blob/master/test/unit/ut_order_book.cpp) inspect multi-order fills, market orders, and successful and failed cancellations.
- **C2:** `OrderBook<OrderPtr>` accepts caller-defined order types and ordinary or smart pointers through a small required interface. Separate order, trade, and book listeners let hosts connect execution and market-data handling without embedding those services in matching logic. Optional depth-book support extends the same core abstraction.

### 3. [chronoxor/CppTrader](https://github.com/chronoxor/CppTrader)

**C++ — market manager, matching engine, and order-book processing components.** Study the boundary between managing symbols/books and executing individual order lifecycles. The manager's explicit statement that it is not thread-safe is a useful integration contract.

- **C1:** The [manager implementation](https://github.com/chronoxor/CppTrader/blob/main/source/trader/matching/market_manager.cpp) validates orders before dispatch, handles remaining quantities differently for IOC/FOK orders, and converts triggered stops into executable order forms. Order lookup, book mutation, and event callbacks must remain consistent across these transitions.
- **C2:** The [MarketManager interface](https://github.com/chronoxor/CppTrader/blob/main/include/trader/matching/market_manager.h) separates symbols, books, orders, and `MarketHandler` notifications. Matching can run automatically or be invoked explicitly, supporting both exchange-style execution and externally controlled processing.
- **C3:** Orders, books, and symbols use dedicated pools, while indexed symbol/book containers and an order hash map make ownership and access paths visible. This is a concrete allocation-management design, not just a throughput claim.

### 4. [jeog/SimpleOrderbook](https://github.com/jeog/SimpleOrderbook)

**C++ with Python bindings — matching and contingent-order engine.** Despite its name, this is a useful study of complex order relationships: OCO, OTO, brackets, trailing stops, and changes caused by partial fills. It is a historical reference: last push observed March 2021. Its README explicitly describes v0.6 all-or-none functionality as unstable and potentially expensive.

- **C1:** Orders are processed within execution windows, while asynchronous callbacks use a separate thread. A returned future does not imply that callbacks have completed. The [dispatcher and execution code](https://github.com/jeog/SimpleOrderbook/blob/master/src/orderbook/core.cpp) makes queue locking, execution locking, promises, and shutdown behavior concrete.
- **C2:** Synchronous and asynchronous submission share the same engine, and contingent orders can resize their exit legs as entry and exit fills accumulate. [TickPrice](https://github.com/jeog/SimpleOrderbook/blob/master/include/tick_price.hpp) separately encapsulates tick ratios and rounding, with compile-time constraints on supported ratios and precision. Study this numerical boundary carefully: it includes floating-point conversion and rounding, unlike integer-only engines elsewhere in this report.

### 5. [geseq/orderbook](https://github.com/geseq/orderbook)

**Go — compact matching library with order/trade notifications.** A less prominent implementation worth examining for its explicit sequencing and allocation decisions. The README calls it experimental and warns that more test coverage is needed; some feature-checklist text also lags the inspected amendment and snapshot code.

- **C1:** Mutating commands check sequential tokens to detect loss of deterministic ordering. Amendments preserve FIFO position for same-price quantity reductions, but lose priority when size increases or price changes. [Amendment tests](https://github.com/geseq/orderbook/blob/main/amend_snapshot_test.go) assert actual maker order, atomic rejection of invalid changes, detached snapshots, and aggregate-volume updates.
- **C3:** The [book implementation](https://github.com/geseq/orderbook/blob/main/orderbook.go) separates price levels, order indexes, trigger indexes, and a trigger queue, and uses object pools with fixed-precision decimal quantities. Its README discusses scheduler jitter and the throughput cost of yielding. The token check should not be mistaken for a general guarantee of safe concurrent mutation.

### 6. [intrepidkarthi/orderbook](https://github.com/intrepidkarthi/orderbook)

**Go — embeddable matcher with recovery, gateway, auction, and research layers.** A newer experimental project with unusually explicit verification boundaries. The author states that it has never run a live market; its breadth is not evidence of production maturity.

- **C1:** The [differential harness](https://github.com/intrepidkarthi/orderbook/blob/main/pkg/matching/differential_test.go) drives generated command tapes through the engine and an independently represented reference matcher. It compares observations after each command and tests continued execution after snapshot restoration at multiple points. The comments explain allowed differences and why model independence matters.
- **C2:** The [design specification](https://github.com/intrepidkarthi/orderbook/blob/main/docs/SPEC.md) separates numeric/order types, book storage, matching, write-ahead logging, auctions, market data, and research consumers through downward dependencies. This offers useful examples of keeping simulation and presentation concerns out of an embeddable engine.
- **C3:** A single-writer matching core, pooled book objects, and caller-supplied result buffers address allocation and contention costs. Published measurements describe the core's boundary; they should not be read as end-to-end venue performance.

## Exchange services and integrated matching backends

### 7. [dharmeshsing/CoinTossX](https://github.com/dharmeshsing/CoinTossX)

**Java — exchange and market-microstructure research platform modeled on JSE trading rules.** Its main distinction is session behavior rather than another continuous price-time matcher. Historical research software: last push observed May 2022, with Java 8 requirements in the inspected README.

- **C1:** The [CrossingProcessor](https://github.com/dharmeshsing/CoinTossX/blob/master/MatchingEngine/src/main/java/crossing/CrossingProcessor.java) validates orders against the current session, ends and starts sessions during transitions, and changes to a volatility auction when a circuit breaker is breached. Correctness therefore includes temporal market rules and transitions, not merely choosing the best resting price.
- **C2:** The [TradingSessionFactory](https://github.com/dharmeshsing/CoinTossX/blob/master/MatchingEngine/src/main/java/crossing/tradingSessions/TradingSessionFactory.java) composes price-time, auction, and filter/uncross strategies with stop-order and expiration processors. Native order entry, matching, market-data distribution, and client simulation occupy separate modules. Engineers can study how common matching policies are reused across opening, continuous, intraday, volatility, and closing sessions.

### 8. [mkipnis/DistributedATS](https://github.com/mkipnis/DistributedATS)

**C++ — distributed FIX exchange integrating QuickFIX, Liquibook, and DDS.** Counted separately from Liquibook because its substantial contribution is exchange integration and order routing, not an independently invented matching algorithm.

- **C1:** The [Market implementation](https://github.com/mkipnis/DistributedATS/blob/master/MatchingEngine/src/Market.cpp) maintains counterparty-specific client-order indexes, handles unknown-order rejection, and maps replacement IDs onto existing orders. This makes the interaction between FIX order identity and underlying matcher identity a concrete study topic.
- **C2:** The [high-level design](https://github.com/mkipnis/DistributedATS/blob/master/docs/HighLevelDesign.md) follows messages from FIX gateways into DDS structures, matching-engine subscribers, execution reports, and data services. Content filters partition markets and route replies; data services retain report copies for mass-status requests. The reusable boundaries support multiple gateways and matching engines without making a single process responsible for every protocol and query.

Do not infer replicated matching-state failover merely from the word “distributed”; the inspected design establishes message routing and service separation.

### 9. [viabtc/viabtc_exchange_server](https://github.com/viabtc/viabtc_exchange_server)

**C — cryptocurrency exchange backend with matching and balance accounting.** Useful for comparing decimal arithmetic and explicit process boundaries with JVM/Rust engines. Historical implementation: last push observed December 2021; the README's deployment baseline is older Ubuntu releases.

- **C1:** The [market implementation](https://github.com/viabtc/viabtc_exchange_server/blob/master/matchengine/me_market.c) compares decimal prices, breaks same-price ties by order ID, executes against maker prices, and updates trade fees and balances. Its [operation loader](https://github.com/viabtc/viabtc_exchange_server/blob/master/matchengine/me_load.c) validates serialized parameters and reconstructs operations through replay-specific paths. Numerical precision and replay side effects are both central review concerns.
- **C3:** Matching uses in-memory order indexes and skip-list traversal. The broader architecture separates the authoritative matcher from history reads, market-price aggregation, and HTTP/WebSocket access, moving database queries and fan-out away from the matching service. This is a useful process-level performance design; the report makes no claim that the published throughput is reproducible today.

### 10. [openware/peatio](https://github.com/openware/peatio)

**Ruby/Rails — exchange accounting and order/trade execution backend.** The relevant subsystem is `app/trading/matching`, especially trade execution. This is the substantially evolved Openware fork of the original Peatio lineage, counted once; original Peatio and OpenDAX deployment packaging are not additional entries. Last push observed April 2023.

- **C1:** The [trade executor](https://github.com/openware/peatio/blob/2-6-stable/app/trading/matching/executor.rb) locks both orders and affected accounts inside a database transaction, validates prices, order state, and remaining volume, and records accounting operations before publishing the trade. Failed execution can resubmit still-waiting orders to matching. Study the boundary between an in-memory match and a committed financial trade.
- **C4:** The [changelog](https://github.com/openware/peatio/blob/2-6-stable/CHANGELOG.md) records releases across 2017–2020, compatibility changes, race-condition fixes, and a fix for disappearing orders and cancellation problems caused by restoring orders to the matching daemon. The inspected 2.6 release notes additionally document database support and migration requirements. This is evidence of sustained complexity management, not a claim of current maintenance.

### 11. [gitbitex/gitbitex-new](https://github.com/gitbitex/gitbitex-new)

**Java — cryptocurrency exchange with replayable in-memory matching.** Particularly useful for studying the relationship between command offsets, output sequences, and snapshots. The README describes standby operation with one running matcher at a time; last push observed November 2025.

- **C1:** The [MatchingEngine](https://github.com/gitbitex/gitbitex-new/blob/main/src/main/java/com/gitbitex/matchingengine/MatchingEngine.java) surrounds command handling with start/end messages carrying input offsets. Snapshot restoration reloads the command offset, global output sequence, products, accounts, per-product order/trade/book sequences, and resting orders. These are the state components that must agree for replay to produce consistent results.
- **C2:** Product, account, and order books are distinct components behind command dispatch and a message-sender interface. The [MatchingEngineLoader](https://github.com/gitbitex/gitbitex-new/blob/main/src/main/java/com/gitbitex/matchingengine/MatchingEngineLoader.java) separately refreshes a prepared engine from persisted snapshots. Engineers can study how recovery preparation is separated from normal order execution; this code alone does not prove exactly-once delivery or lossless failover.

### 12. [openexch/match](https://github.com/openexch/match)

**Java — matching cluster built around Aeron Cluster.** A newer **beta** implementation, explicitly described in its architecture document as unaudited and not yet recommended for deployments holding real funds. Only this repository is counted; its companion OMS, operations gateway, and UI are contextual dependencies.

- **C1:** The [architecture document](https://github.com/openexch/match/blob/main/docs/ARCHITECTURE.md) makes matching a deterministic consumer of a replicated log, with snapshots and archive replay. The inspected book implementation also distinguishes historical fixed configuration from configuration supplied through replicated messages, avoiding replica-local environment settings for those values.
- **C3:** [DirectIndexOrderBook](https://github.com/openexch/match/blob/main/match-cluster/src/main/java/com/match/application/orderbook/DirectIndexOrderBook.java) is a concrete array-backed implementation: packed order fields, per-level metadata, free-slot stacks, and an order-location map. Its bounded price range and per-level capacity expose the memory-versus-flexibility tradeoff. Study this implementation alongside the repository's other book variants; do not generalize its comments about constant-time operations to every workload or the complete cluster.

## Financial order-management and execution subsystems

### 13. [nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader)

**Rust and Python — execution engine, order lifecycle, and venue reconciliation.** Included for the execution/OMS subsystem rather than its strategy and analytics features. The inspected `develop` documentation describes evolving 2.0 architecture; release-specific behavior should be checked before adopting it.

- **C1:** The [reconciliation guide](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/execution/reconciliation.md) distinguishes missing reports from authoritative flat positions, cached from uncached orders, and startup from continuous reconciliation. It explains fill identities, historical-data limits, stale state, and the requirement to resolve authoritative position mismatches before strategies start.
- **C2:** Responsibilities are divided among `LiveNode`, `ExecutionManager`, `ExecutionEngine`, execution clients, and shared cache. Venue adapters provide reports while common machinery converts them into order and position events, allowing recovery logic to span multiple venues.
- **C4:** [Release history](https://github.com/nautechsystems/nautilus_trader/blob/develop/RELEASES.md) spans at least 2021–2026 and documents order-FSM fixes, simulated matching refactoring, increased test coverage, migrations, and breaking API changes. The latest undated development section is not treated as a completed release.

### 14. [QuantConnect/Lean](https://github.com/QuantConnect/Lean)

**C# with Python-facing strategy support — brokerage transaction and order-ticket subsystem.** Included for `Engine/TransactionHandlers` and related order abstractions, not as an exchange matching engine. A useful contrast with venue-side books because requests and executions arrive asynchronously from external brokerages.

- **C1:** [BrokerageTransactionHandler tests](https://github.com/QuantConnect/Lean/blob/master/Tests/Engine/BrokerageTransactionHandlerTests/BrokerageTransactionHandlerTests.cs) cover cancel-pending transitions, updates after partial fills, and invalid updates that must not corrupt already-filled or canceled orders. These are realistic order-state races and rejection paths.
- **C2:** The [transaction handler](https://github.com/QuantConnect/Lean/blob/master/Engine/TransactionHandlers/BrokerageTransactionHandler.cs) connects brokerage interfaces, requests, order tickets, execution models, and order events while maintaining open and complete order collections. The same architecture accommodates live and backtesting brokerages.
- **C3:** The inspected implementation uses a request-processing pool that preserves per-order request ordering, with concurrency controlled by brokerage capability; synchronous backtesting takes a different processing path. This is a concrete example of reconciling parallel request throughput with order-local sequencing.

## On-chain order books and batch-clearing engines

### 15. [Ellipsis-Labs/phoenix-v1](https://github.com/Ellipsis-Labs/phoenix-v1)

**Rust — Solana order book with atomic settlement.** The official README now calls this **Phoenix Legacy**. It remains a substantive official repository; this entry does not imply that newer Phoenix products use the same implementation. Its distinguishing model avoids a separate crank for settlement.

- **C1:** [Quantity types](https://github.com/Ellipsis-Labs/phoenix-v1/blob/master/src/quantities.rs) distinguish ticks, base lots, quote lots, and conversion factors so arithmetic expresses units. The [FIFO market implementation](https://github.com/Ellipsis-Labs/phoenix-v1/blob/master/src/state/markets/fifo.rs) combines price/sequence priority, expiration checks, fee rounding, and checked narrowing in fee-adjustment calculations.
- **C3:** Bids, asks, and trader seats use capacity-parameterized red-black trees, and the market can be accessed through a byte-slice-backed representation. These choices address constrained account storage and serialization costs. The interesting engineering question is how bounded storage and numeric representations interact with matching and settlement, rather than a claimed transactions-per-second number.

### 16. [openbook-dex/openbook-v2](https://github.com/openbook-dex/openbook-v2)

**Rust with TypeScript client — Solana central limit order book.** The relevant subsystem is `programs/openbook-v2`. The README identifies its Mango V4 and earlier OpenBook/Serum ancestry; V2 is retained for its substantive implementation, without also counting the older forks. Last push observed July 2024.

- **C1:** The [matching code](https://github.com/openbook-dex/openbook-v2/blob/master/programs/openbook-v2/src/state/orderbook/book.rs) accounts for quote budgets including fees, post-only and fill-or-kill behavior, and self-trade policies that decrement, cancel the maker, or abort the transaction. It coordinates changes to resting orders with fill/out events and open-orders accounts.
- **C3:** Matching explicitly bounds expired-order cleanup and fill-event processing to avoid excessive compute use. The [order tree](https://github.com/openbook-dex/openbook-v2/blob/master/programs/openbook-v2/src/state/orderbook/ordertree.rs) uses a fixed-capacity, zero-copy representation with crit-bit traversal and expiry metadata. This is a particularly clear case of execution-budget constraints shaping both data structures and matching semantics.

### 17. [dydxprotocol/v4-chain](https://github.com/dydxprotocol/v4-chain)

**Go protocol, with TypeScript indexer — perpetual-exchange CLOB subsystem.** Count the monorepo once, concentrating on `protocol/x/clob/memclob` and its keeper interfaces. This is useful for studying an in-memory book that must interact with block proposal, committed state, and order replay.

- **C1:** [MemClob](https://github.com/dydxprotocol/v4-chain/blob/main/protocol/x/clob/memclob/memclob.go) checks that placement leaves an uncrossed book, tracks operations proposed for blocks and replay, and handles reduce-only orders when fills change a position's sign. [Reduce-only tests](https://github.com/dydxprotocol/v4-chain/blob/main/protocol/x/clob/memclob/memclob_place_order_reduce_only_test.go) cover absent positions, position-increasing orders, existing matches, remaining books, and collateralization outcomes.
- **C2:** The matching implementation sits behind a `MemClob` interface and communicates with an expected keeper interface rather than owning the entire blockchain application. Separate indexes track books, subaccount orders, reduce-only orders, expirations, and cancellation lifetimes. Engineers can study how trading-specific state is reconciled with the protocol's broader execution lifecycle.

### 18. [scslab/speedex](https://github.com/scslab/speedex)

**C++ — research implementation of parallel batch exchange and clearing.** A deliberate architectural contrast to continuous FIFO matching: SPEEDEX computes exchange prices for batches and organizes account/order state for parallel processing. This is the standalone research implementation, not the separately linked Stellar prototype. Last push observed January 2024.

- **C1:** [Offer-clearing logic](https://github.com/scslab/speedex/blob/master/orderbook/offer_clearing_logic.h) uses wide price-ratio multiplication and explicit tax/rounding operations. Partial clearing rounds the amount removed from an offer separately from the amount credited. The [block validator](https://github.com/scslab/speedex/blob/master/block_processing/block_validator.cc) checks clearing commitments, transaction validity, merged updates, and final account-state validity.
- **C3:** Validation uses TBB parallel reduction, thread-local validators, and parallel completion of order-book updates. The repository separates price computation, Merkle-trie-backed books, account storage, and block processing. It is valuable for studying how changing market semantics enables a different concurrency design, with numerical and state-validation obligations still explicit.

## Search coverage, exclusions, and limitations

Discovery used more than six distinct live-search formulations, including Java/Disruptor exchange cores; C++ embeddable matching and FIX integration; Go price-time books and recovery; financial OMS reconciliation and cancel/replace behavior; Ruby cryptocurrency exchange accounting; Rust/Solana atomic order books; blockchain CLOB replay; parallel and frequent-batch clearing; and C#, Elixir/Erlang, OCaml, and Haskell alternatives. Further searches increasingly returned the same established engines, recently published portfolio projects, wrapper SDKs, or benchmark collections. Selection stopped after those additional angles produced diminishing returns in distinct, sufficiently evidenced implementations.

Every retained canonical repository was verified through the GitHub API. Its source-tree index and at least two additional implementation, test, design, or release files were retrieved and inspected. Linked file paths were checked against the actual default-branch trees, including `main` for CppTrader, `2-6-stable` for Peatio, and `develop` for NautilusTrader. Source links are branch links and can change after this research date.

Important exclusions and boundaries:

- **Unavailable original:** `opentradesolutions/opentrade` returned HTTP 404 from the GitHub API. Unofficial copies surfaced in search, but no official substantive mirror was established, so they were not substituted.
- **Confirmed problematic candidate:** `realyarilabs/exchange` offered an OTP-based contrast, but its inspected [expiration filter](https://github.com/realyarilabs/exchange/blob/master/lib/exchange/order_book.ex) ends its predicate with unconditional `true`. The inference from that source is that the intended expiry check does not filter candidates. Given this defect and sparse top-level documentation, it was excluded rather than added for language diversity.
- **No duplicated lineage or packaging:** Liquibook forks, CppTrader forks, the earlier Serum/OpenBook lineage, and OpenDAX packaging were not counted as extra engines. DistributedATS qualifies through its distinct integration implementation; Peatio's Openware fork qualifies through substantial documented evolution.
- **Scope exclusions:** Retail OMS products, order-book reconstruction without matching, FIX libraries alone, market-data libraries, exchange clients, AMM-only protocols, awesome lists, and assignment/tutorial engines were excluded. Lean and NautilusTrader qualify specifically through their substantive financial execution/OMS subsystems.
- **Verification limits:** No candidate code was executed, dependencies installed, benchmarks reproduced, deployment audits performed, or exchange adoption independently verified. Test files establish inspectable verification practice, not that every test currently passes. C4 is awarded only where inspected history demonstrates multi-year complexity or compatibility management. Recent repositories can qualify through C1–C3 without implying maturity.

The result is a comparative reading guide: choose libraries for local matching invariants, integrated backends for accounting and recovery boundaries, OMS subsystems for asynchronous venue state, and on-chain/batch engines for constrained storage, settlement, and alternative execution semantics.
