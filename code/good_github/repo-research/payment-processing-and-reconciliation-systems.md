# Payment processing and reconciliation systems

Research date: **2026-10-09**.

This selection covers merchant payment orchestration, financial switches, bank payment formats, settlement, payment-specific ledger infrastructure, and reconciliation against invoices or external financial records. It includes both complete applications and substantial reusable components. A ledger is included only where its transfer semantics directly support payment processing; general bookkeeping tools, blockchain consensus implementations, generated SDKs, and checkout examples are outside this selection. The 23 repositories below are study candidates, not an assertion that every component is exemplary or ready for a particular production deployment.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial input, or failure recovery.
- **C2 — Abstractions:** substantial reusable models and interfaces supporting multiple payment or reconciliation use cases.
- **C3 — Performance and structure:** concrete mechanisms addressing throughput, latency, contention, or memory constraints within an understandable architecture.
- **C4 — Evolution:** evidence across years of compatibility work, testing, migrations, or complexity management; age alone does not qualify.

Repository identities and archive flags were checked through public GitHub pages. Source links generally target the inspected default branch, so they may include unreleased changes. OCA entries specifically use the inspected `19.0` branch, and Payum uses `2.x`. Historical or archived selections are identified individually. An unarchived repository is not, by itself, evidence of ongoing maintenance.

## Merchant orchestration and gateway frameworks

### 1. [juspay/hyperswitch](https://github.com/juspay/hyperswitch)

**Rust — payment orchestration backend.** Study how a common payment server accommodates provider-specific connectors while separating request processing from deferred work. The relevant subsystem is the Rust backend; dashboards, card vaults, and client SDKs in other repositories are not counted here.

- **C2:** The Router centralizes payment flows, while the Scheduler has separate producer and consumer responsibilities. These boundaries let payment operations and scheduled tasks share infrastructure without becoming a single request handler. The [architecture document](https://github.com/juspay/hyperswitch/blob/main/docs/architecture.md) explains the division and data movement.
- **C3:** That design batches due database tasks into Redis queues, uses Redis caching to reduce database load and latency, and describes separate database read/write roles and telemetry. These are concrete performance mechanisms, rather than a throughput claim inferred from its use of Rust. Start with the architecture document, then the [backend crates](https://github.com/juspay/hyperswitch/tree/main/crates).

The repository advertises reconciliation in the wider product offering; this entry's qualification rests on the inspected orchestration architecture, not an assumption that every advertised module is implemented in this repository.

### 2. [killbill/killbill](https://github.com/killbill/killbill)

**Java — billing platform with an independent payment subsystem.** The engineering attraction is the boundary between business billing, payment attempts, and external gateway outcomes. Study the payment subsystem rather than treating the entire subscription platform as payment infrastructure.

- **C1:** The explicit [payment state-machine configuration](https://github.com/killbill/killbill/blob/master/payment/src/main/resources/org/killbill/billing/payment/PaymentStates.xml) distinguishes authorization states such as pending, successful, failed, and errored, and specifies permitted operation transitions. This makes asynchronous completion and uncertain outcomes visible in the model.
- **C2:** Payment methods select gateway plugins, and recurring invoice payments and direct one-off operations use related abstractions. The [versioned payment design guide](https://docs.killbill.io/0.20/userguide_payment) explains these interfaces and the Janitor mechanism for querying a gateway after an uncertain result.

The linked guide is explicitly for the unsupported 0.20 release and is a historical design explanation; the source configuration was inspected on `master`. Its value here is explaining why a timeout cannot safely be interpreted as a declined payment, not prescribing current deployment settings.

### 3. [activemerchant/active_merchant](https://github.com/activemerchant/active_merchant)

**Ruby — shared payment gateway abstraction.** This is useful for studying how a long-lived common API absorbs divergent acquirer conventions without becoming a generated API client collection.

- **C2:** The [Gateway base class](https://github.com/activemerchant/active_merchant/blob/master/lib/active_merchant/billing/gateway.rb) defines the purchase/authorize/capture/void/refund vocabulary, shared response error categories, capability metadata, and request option conventions. Its currency formatting hooks also reveal where a supposedly universal interface needs provider-specific behavior.
- **C4:** The [changelog](https://github.com/activemerchant/active_merchant/blob/master/CHANGELOG) contains dated releases spanning 2008 through 2024, followed by further changes. Examples include Ruby compatibility updates, XML dependency repairs, schema-version tests, idempotency fields, and fixes to split refunds and currency handling. This is direct evidence of sustained adaptation to external protocol changes.

Do not infer uniformly exact arithmetic from its integer-cent public convention: the inspected formatting helpers also use floating-point conversions. That boundary is itself a useful review topic.

### 4. [Payum/Payum](https://github.com/Payum/Payum)

**PHP — extensible payment workflow framework.** Study the inspected `2.x` gateway design, particularly the distinction between a payment command, a handler, saved state, and the next action presented to a customer.

- **C1:** Capture is explicitly re-entrant: after a provider redirects the customer back, the handler reads the saved checkout identifier and retrieves its status instead of blindly creating another checkout. The [custom gateway guide](https://github.com/Payum/Payum/blob/2.x/docs/develop-gateway-with-payum.md) demonstrates pending and captured results and token-based return URLs. This is a concrete multi-step payment correctness problem, although the example alone does not prove end-to-end exactly-once behavior.
- **C2:** The same guide separates validated configuration, the PSP API object, typed command handlers, results, and gateway metadata. Capabilities are derived from implemented handler interfaces, reducing the risk that declared capabilities drift from executable behavior. These abstractions support custom gateways across application frameworks.

### 5. [jeequan/jeepay](https://github.com/jeequan/jeepay)

**Java — multi-merchant payment platform with Chinese payment-channel integrations.** This adds an implementation community and payment-method mix that differ from the predominantly Stripe-centered examples found in broad searches. Relevant modules include the payment gateway, merchant service, operator service, shared business services, and messaging components.

- **C1:** [PayOrderProcessService](https://github.com/jeequan/jeepay/blob/master/jeepay-payment/src/main/java/com/jeequan/jeepay/pay/service/PayOrderProcessService.java) checks order-state updates within a transaction and conditionally advances an unprocessed division state before scheduling a split-payment task. It is useful for reviewing repeated completion signals and the boundary between a database update and queue publication.
- **C2:** The [project structure guide](https://github.com/jeequan/jeepay/blob/master/docs/project-structure.md) separates gateway, merchant, operator, common MQ, and business-service modules. The inspected channel abstraction supplies common merchant configuration and callback construction, while concrete channels implement payment-specific behavior.

These observations establish substantive engineering content, not a guarantee that database and message-broker effects are atomically committed.

### 6. [rbkmoney/hellgate](https://github.com/rbkmoney/hellgate)

**Erlang — historical payment-processing core.** The repository is unarchived, but its inspected [default-branch commit feed](https://github.com/rbkmoney/hellgate/commits/master.atom) ends in January 2022. Treat it as a historical architecture study; current maintenance and deployability were not established.

- **C1:** [hg_invoice_payment.erl](https://github.com/rbkmoney/hellgate/blob/master/apps/hellgate/src/hg_invoice_payment.erl) validates capture currency and allowed hold-payment activity, then handles routing, processing, accounting, refunds, chargebacks, adjustments, failures, and repair scenarios as explicit states and events. The distinction between provider sessions and accounting completion is especially instructive.
- **C2:** The module exposes common operations over payment state and reconstructs state through `merge_change` and `collapse_changes`. Separate activity types and cash-flow construction allow the same core to cover authorization holds, captures, refunds, and dispute lifecycles rather than only successful purchases.

The source also records unresolved design questions around callbacks. Its explicit complexity is valuable evidence for study, not grounds to assume all retry paths are correct.

## Financial switching, settlement, and transfer infrastructure

### 7. [jpos/jPOS](https://github.com/jpos/jPOS)

**Java — financial messaging and transaction-processing framework.** The [official introduction](https://jpos.org/docs/welcome/) identifies gateways, issuers, acquirers, switches, ISO 8583 messaging, routing, and failure handling as its intended domain.

- **C1:** The [TransactionManager implementation](https://github.com/jpos/jPOS/blob/main/jpos/src/main/java/org/jpos/transaction/TransactionManager.java) snapshots transaction state into persistent space, distinguishes preparing/committing/completed phases, and recovers in-flight work on startup. Prepare, commit, abort, retry, and pause paths make crash recovery and partial participation concrete.
- **C2:** Transaction participants, context recovery hooks, configurable participant groups, and shared spaces form reusable orchestration machinery around financial messages. Study how this lifecycle composes with protocol handling rather than implementing every gateway as a bespoke socket loop.
- **C3:** The same manager exposes session limits, active/paused counters, retry scheduling, and timing instrumentation. These connect concurrency control and observability to the transaction architecture without requiring an unsupported benchmark claim.

### 8. [mojaloop/central-ledger](https://github.com/mojaloop/central-ledger)

**JavaScript/TypeScript — inter-provider clearing and position tracking.** This repository implements part of the Mojaloop hub, not an entire independently deployable national payment system. Its stated role includes real-time clearing messages and net positions for deferred settlement.

- **C1:** The [transfer prepare handler](https://github.com/mojaloop/central-ledger/blob/main/src/handlers/transfers/prepare.js) compares both duplicate identifiers and payload hashes. It distinguishes a repeated request from a modified request using the same identifier, and handles already-finalized versus in-progress transfers differently. This is a particularly useful implementation of idempotency beyond merely caching a key.
- **C2:** The same path factors validation, participant/proxy lookup, persistence, FX handling, and Kafka notifications into collaborating services. The [transfer-handler directory](https://github.com/mojaloop/central-ledger/tree/main/src/handlers/transfers) contains separate preparation, validation, fulfilment, timeout, and integration-test concerns.

The older root transfer tutorial contains legacy examples; the claims above use the inspected current handler instead.

### 9. [mojaloop/central-settlement](https://github.com/mojaloop/central-settlement)

**JavaScript — settlement-window and inter-provider settlement service.** This is a separate substantive repository from Central Ledger: it coordinates settlement windows and settlement/account states after clearing. It belongs to the same ecosystem and should not be mistaken for an unrelated competing platform.

- **C1:** The [settlement domain implementation](https://github.com/mojaloop/central-settlement/blob/main/src/domain/settlement/index.js) refuses aborts after committed transfers or settling/settled states. It also checks for an individually committed account transfer while the enclosing settlement is still in a reserved state, exposing the difficulty of partial completion.
- **C2:** Settlement models, windows, window contents, participants, and currency accounts are separate concepts. Event-trigger processing validates applicable windows and excludes incompatible gross/immediate models. This is reusable scheduling and settlement-policy machinery, not simply summing payments.

The same file is the main study entry point. The root README additionally documents a concrete compatibility issue when moving request validation from Joi to AJV; no claim of complete integration-test coverage is made from its mixed documentation.

### 10. [interledger/rafiki](https://github.com/interledger/rafiki)

**TypeScript — Interledger and Open Payments infrastructure for financial service providers.** Study the backend's outgoing-payment lifecycle alongside the repository's connector, accounting, and authorization components. The monorepo is counted once.

- **C1:** The [outgoing-payment service](https://github.com/interledger/rafiki/blob/main/packages/backend/src/open_payments/payment/outgoing/service.ts) uses database transactions and row locking for state-sensitive operations, rejects actions in the wrong state, and tracks grant spending and reversals. This ties authorization limits to concurrent payment execution rather than treating authorization as only an HTTP check.
- **C2:** The [backend composition root](https://github.com/interledger/rafiki/blob/main/packages/backend/src/index.ts) wires accounting, peers, receivers, routes, quotes, and incoming/outgoing payment services. It also selects TigerBeetle or PostgreSQL accounting implementations, providing a concrete example of a payment service boundary with replaceable storage/accounting infrastructure.

Rafiki's stated operating audience is financial service providers; this selection is about its implementation, not a recommendation to operate a regulated service.

### 11. [tigerbeetle/tigerbeetle](https://github.com/tigerbeetle/tigerbeetle)

**Zig — replicated financial-transfer database.** This is the ledger/storage layer of payment systems, rather than a gateway or bank-statement matcher. It is included for its directly applicable reservation, posting, reversal, and balance semantics.

- **C1:** [Two-phase transfers](https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/coding/two-phase-transfers.md) reserve funds before posting, voiding, or expiry. Pending transfers resolve at most once; resolution creates another immutable transfer. The documentation explains how pending amounts participate in balance invariants and how partial posting releases the remainder.
- **C3:** The [architecture document](https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/ARCHITECTURE.md) starts from contention on popular accounts and write-heavy workloads. It connects batching, execution inside the database, deterministic replicated state transitions, checksummed storage, and bounded allocation to those constraints. This makes it unusually useful for studying the interaction of correctness and throughput without adopting its numerical performance claims.

## Bank rails and payment-message components

### 12. [moov-io/ach](https://github.com/moov-io/ach)

**Go — ACH/Nacha file construction, parsing, and validation.** This is a reusable protocol component, not a complete ACH origination or reconciliation service. Study file-level financial controls and how strict validation coexists with real-world nonstandard input.

- **C1:** [file.go](https://github.com/moov-io/ach/blob/master/file.go) constructs batch counts, record counts, entry hashes, and debit/credit control totals. Its validation options make exceptions to trace-number, routing, addenda, and amount checks explicit instead of silently treating every input as conformant. [Malformed-input tests](https://github.com/moov-io/ach/blob/master/malformed_test.go) supply additional evidence that invalid files are a first-class concern.
- **C2:** Common file, batch, entry, and addenda abstractions support different Standard Entry Class codes, international batches, and both Go-library and HTTP-server use. This is more reusable than a single bank's export script.

Permissive validation options are compatibility mechanisms; enabling them changes which invariants the caller can rely on.

### 13. [moov-io/iso8583-connection](https://github.com/moov-io/iso8583-connection)

**Go — concurrent ISO 8583 request/response transport.** The focus is transport lifecycle, message correlation, and connection pools for acquiring or issuing services. It complements a message codec and is not counted as another copy of that codec.

- **C1:** [connection.go](https://github.com/moov-io/iso8583-connection/blob/master/connection.go) tracks pending responses under synchronization, uses separate read/write paths, and notifies outstanding requests when a connection fails. Shutdown waits for active sends while handling timeout and closure races.
- **C3:** [pool.go](https://github.com/moov-io/iso8583-connection/blob/master/pool.go) distributes requests across available connections and recreates failed connections with increasing reconnect delays bounded by configuration. The separation between a connection and its pool makes load distribution and failure recovery inspectable.

This is a strong smaller codebase for studying why a timeout, unsolicited message, late response, and closed socket must remain distinguishable.

### 14. [moov-io/wire](https://github.com/moov-io/wire)

**Go — archived, historical Fedwire FAIM parser/writer.** GitHub marks this repository archived. Its README explicitly says the legacy FAIM format is no longer accepted for live Fedwire traffic following the ISO 20022 transition in July 2025. Retain it for archival processing, migration, and protocol-design study, not new live integrations.

- **C1:** [fedWireMessage.go](https://github.com/moov-io/wire/blob/master/fedWireMessage.go) validates mandatory tags and relationships that depend on message type, subtype, and business-function code. It separates base required fields from conditional transfer information and exposes explicit validation exceptions.
- **C2:** The message model composes typed amount, institution, remittance, reference, and accountability-data records. Together with the repository's reader/writer and HTTP surface, it can process multiple FAIM message families rather than one fixed transfer template.

The source file and the root README's migration/status explanation are the principal entry points. This is a deprecated-format implementation, not an official mirror of a project that moved off GitHub.

### 15. [OCA/bank-payment](https://github.com/OCA/bank-payment)

**Python — Odoo payment orders, mandates, and bank-file generation.** Focus on `account_payment_order`, `account_banking_mandate`, the PAIN base module, and the SEPA transfer/direct-debit modules. The addon monorepo counts once.

- **C1:** The [SEPA direct-debit payment-order implementation](https://github.com/OCA/bank-payment/blob/19.0/account_banking_sepa_direct_debit/models/account_payment_order.py) groups payments by execution date, priority, purpose, scheme, and mandate sequence; generates transaction counts/control sums; and changes mandate state after upload. The ordering is deliberate: accounting moves are generated before first-use mandates become recurring, while one-off and final mandates expire.
- **C2:** It extends shared payment-order and XML-generation behavior instead of reproducing the entire payment workflow. Mandates, payment modes, payment orders, and format-specific generators support different bank-payment use cases through composable addons, as cataloged on the repository page.

Read this for business-protocol state transitions, particularly the difference between generating a file and declaring it uploaded.

## Reconciliation engines and financial operations

### 16. [formancehq/payments](https://github.com/formancehq/payments)

**Go — PSP connectivity and normalized payment-data ingestion.** This supplies the external-provider side of reconciliation and also abstracts payment operations. It is a substantive connector framework, not a generated client for one provider.

- **C1:** The [connector development guide](https://github.com/formancehq/payments/blob/main/CONTRIBUTING.md) specifies persisted pagination state through `State`, `NewState`, and `HasMore`, including providers whose ordering does not permit a simple page counter. It also specifies asset precision and integer smallest-unit amounts, exposing a common reconciliation failure: confusing dollars with cents or assuming every currency has two decimals.
- **C2:** The plugin contract covers installation, polling, payment operations, and webhook behavior. Workflow task trees express independent parent work and dependent child fetches, while provider responses become common account, balance, and payment models. The guide is the primary architectural entry point and links concrete implementations.

Community and enterprise directories coexist in the repository. This entry evaluates the inspected shared design and does not imply identical availability or licensing for every connector.

### 17. [formancehq/reconciliation](https://github.com/formancehq/reconciliation)

**Go — ledger/cash-pool consistency evaluation and operational alerts.** Its stated job is checking that ledger balances agree with externally held funds. This differs from pairing individual bank-statement lines with invoices.

- **C1:** The [reconciliation runner](https://github.com/formancehq/reconciliation/blob/main/internal/reconciliation/runner.go) handles rule locks, rule revisions, job claim tokens, point-in-time source reads, and transactional persistence of evaluations and alert changes. It deliberately refuses to turn cancellation after loss of a worker lease into a successfully completed evaluation.
- **C2:** Manual and scheduled triggers share the runner, while template evaluators and source resolvers supply the financial checks. Passing outcomes retain compact balance proofs; failures retain richer evidence. The [runner tests](https://github.com/formancehq/reconciliation/blob/main/internal/reconciliation/runner_test.go) cover changed rules, explicit historical evaluation times, cancellation, stable error evidence, and successful-versus-failed evidence serialization.

These are default-branch observations; the report does not assert that every inspected runner feature is in a released package.

### 18. [blnkfinance/blnk](https://github.com/blnkfinance/blnk)

**Go — financial ledger with a configurable reconciliation subsystem.** Focus on its reconciliation engine rather than counting its ledger, identities, and API as separate projects. It compares external bank/provider records against internal transactions.

- **C1:** The [matching regression tests](https://github.com/blnkfinance/blnk/blob/main/reconciliation_matching_test.go) pin down fractional amount tolerances, negative refund/debit amounts, strict comparison boundaries, sub-second date drift, unknown operators, and string/currency matching. These are concrete numerical and rule-consistency hazards, not just happy-path examples.
- **C2:** [reconciliation.go](https://github.com/blnkfinance/blnk/blob/main/reconciliation.go) separates matching criteria, strategy/group configuration, external-data input, persisted progress, dry runs, and match/unmatched results. Those abstractions support different reconciliation policies without replacing the surrounding ledger.

**Material caveat:** the inspected tests explicitly expect a group labeled `MIXED` to bypass currency checking. That behavior deserves careful scrutiny before using cross-currency grouping. This report does not endorse it as a safe general policy.

### 19. [frappe/erpnext](https://github.com/frappe/erpnext)

**Python/JavaScript — ERP payment-to-invoice reconciliation subsystem.** The selection is specifically `erpnext/accounts/doctype/payment_reconciliation`; inventory, manufacturing, and other ERP modules are outside this entry.

- **C1:** [payment_reconciliation.py](https://github.com/frappe/erpnext/blob/develop/erpnext/accounts/doctype/payment_reconciliation/payment_reconciliation.py) validates allocations against remaining payment amounts and invoice outstandings, handles exchange-rate differences and gain/loss journals, and checks for conflicting automatic reconciliation work. This is a useful study of financial residuals and partial allocation, not only equal-amount matching.
- **C2:** Payment Entries, Journal Entries, invoices, return invoices, accounting dimensions, and receivable/payable accounts feed a common allocation workflow. The same implementation scopes queries by company and permitted dimensions and delegates posting through accounting helpers, making it reusable across customer and supplier flows.

Its numerical comparisons and precision policy should be inspected directly; no universal exact-decimal guarantee is inferred from the accounting domain.

### 20. [OCA/account-reconcile](https://github.com/OCA/account-reconcile)

**Python/JavaScript — Odoo community bank-statement reconciliation addons.** Focus on `account_reconcile_oca` and its statement/accounting abstractions. This is a separate function from the bank-file generation repository above.

- **C1:** The [bank-statement-line model](https://github.com/OCA/account-reconcile/blob/19.0/account_reconcile_oca/models/account_bank_statement_line.py) recomputes suspense entries, uses currency precision when deciding whether a balance remains, handles exchange counterparts, and tracks whether the reconciliation data changed. These details expose the difference between selecting a plausible match and constructing balanced accounting entries.
- **C2:** The model extends shared reconciliation abstractions and supports rule-based write-offs, manual counterpart editing, partner information, and statement/day/week aggregation. Multiple interaction paths reuse the same accounting model rather than keeping independent UI-only matching state.

The inspected `19.0` branch contains fewer addons than some older branches; do not assume every addon advertised for Odoo 18 has been ported. The repository is counted once despite its version branches.

### 21. [GrandmasterTash/OpenRec](https://github.com/GrandmasterTash/OpenRec)

**Rust with YAML/Lua rules — historical file-based reconciliation engine.** The repository is unarchived, but its inspected [commit feed](https://github.com/GrandmasterTash/OpenRec/commits/main.atom) ends in January 2022. It is an implementation study, not a claim of current maintenance or a complete finance-operations product.

- **C2:** The [concepts guide](https://github.com/GrandmasterTash/OpenRec/blob/main/docs/concepts.md) separates Steward orchestration, Jetwash normalization, and Celerity matching. Configurable projections, merged columns, grouping, net-to-zero/tolerance constraints, and unmatched-data carry-forward support invoice/payment and other financial reconciliation shapes.
- **C3:** The repository describes external merge sorting to keep large datasets on disk. The [Celerity pipeline](https://github.com/GrandmasterTash/OpenRec/blob/main/celerity/src/lib.rs) makes phases explicit and caps parallel derivation by source-file count and available CPUs. Study the resulting I/O, memory, and scheduling tradeoffs; advertised numerical throughput is not relied upon here.

The library explicitly requires callers to prevent simultaneous jobs against the same charter/data folder. File-arrival atomicity and recovery are integration responsibilities worth studying alongside the matcher.

## Bitcoin and Lightning payment applications

### 22. [btcpayserver/btcpayserver](https://github.com/btcpayserver/btcpayserver)

**C# — self-hosted merchant payment processor.** The relevant subsystem is invoice/payment accounting and settlement observation, rather than cryptocurrency consensus. Study how an invoice can receive several payments and still require a separate settlement decision.

- **C1:** The [invoice guide](https://docs.btcpayserver.org/Users/invoices/) distinguishes fully paid-but-processing from settled, expired, invalid, partial, overpaid, and late cases. In [PaymentService](https://github.com/btcpayserver/btcpayserver/blob/master/BTCPayServer/Services/Invoices/PaymentService.cs), payment persistence precedes settlement-event publication; update processing emits that event on a transition into settled status.
- **C2:** The service uses payment-method handler lookup, invoice repositories, persisted payment entities, and an event aggregator. These abstractions let different payment methods participate in a common merchant invoice lifecycle instead of requiring a separate invoice engine for each rail.

The inspected insertion path treats a database update exception as an already-existing payment. Review that error boundary rather than assuming it is a complete transactional-outbox or exactly-once design.

### 23. [lnbits/lnbits](https://github.com/lnbits/lnbits)

**Python — wallet/account and payment layer over Lightning funding sources.** This differs from BTCPay's merchant-invoice focus: the central concern is partitioning a funding source into application wallets and coordinating internal versus external payments.

- **C1:** [payments.py](https://github.com/lnbits/lnbits/blob/dev/lnbits/core/services/payments.py) acquires per-wallet asynchronous locks, rereads the balance before paying, reserves routing fees, checks for existing payment identifiers, and refreshes pending outcomes from the funding source. It distinguishes internal invoice settlement from an external network payment.
- **C2:** The same service operates against funding-source abstractions while exposing common invoice/payment models to wallet APIs and extensions. That separation allows applications to use the wallet layer without depending on a particular Lightning-node implementation, as explained by the repository's architecture overview in its README.

The observed locks are process-local Python locks; they should not be interpreted as proof of multi-process or distributed serialization. That deployment boundary is an important part of the study.

## Search coverage and limitations

Discovery used more than six distinct live search formulations, including payment orchestration and Kill Bill/Hyperswitch; bank/gateway/settlement reconciliation; ISO 8583 switches; ACH and Fedwire validation; ledger-based payment invariants; Odoo/ERPNext bank matching; Mojaloop/Interledger clearing; gateway abstractions in Ruby/PHP; Chinese payment platforms using 支付 and 对账; Bitcoin/Lightning invoice handling; and Rust/file-based reconciliation engines. Follow-up searches for less familiar matching systems found OpenRec and several products, SDKs, classroom engines, and synthetic-data demonstrations. Later broad queries increasingly returned those same projects or adjacent bookkeeping tools, giving diminishing returns for this scope.

Each retained repository's public GitHub page was opened, and at least one additional primary implementation, test, or design source was read. Source paths were verified by successful retrieval or inspected GitHub trees. The shared unauthenticated GitHub API rate limit was reached early; public repository HTML, raw source files, official documentation, and commit feeds supplied the remaining evidence. This did not require cloning, installing dependencies, running candidate code, or accessing credentials.

Important selection boundaries:

- Reconciliation is not one operation: Formance checks ledger/cash-pool consistency; Blnk and OpenRec implement transaction matching; ERPNext and OCA allocate payments and create accounting effects; Mojaloop coordinates clearing and settlement states. Their inclusion does not imply interchangeable semantics.
- Separate Mojaloop and Formance repositories are retained because their implementations own different processing stages. Monorepos and version branches are each counted once; mirrors and ordinary forks are not presented as independent projects.
- Generated provider clients, single-provider checkout wrappers, awesome lists, and tutorial/portfolio payment engines were excluded. General plain-text accounting and blockchain consensus projects were not used to inflate payment-system coverage.
- Lerian Matcher surfaced in official documentation, but the searched canonical GitHub implementation URL returned 404. It was excluded rather than substituted with a public SDK or deployment chart.
- Moov Wire is archived and format-deprecated. Hellgate and OpenRec have inspected default-branch histories ending in 2022 and are explicitly historical selections. No sustained-maintenance claim is inferred from the other repositories merely being unarchived.
- C1–C4 assessments are grounded engineering judgments about the cited evidence. Tests were read, not executed; operational deployment claims, throughput figures, security certification, and complete failure-mode correctness were not independently established. The noted mixed-currency, locking, exception-handling, and publication boundaries illustrate why these are selection guides rather than blanket endorsements.
