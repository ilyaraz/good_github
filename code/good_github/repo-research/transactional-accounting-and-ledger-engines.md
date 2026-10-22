# Transactional accounting and ledger engines

Research date: **2026-10-09**.

This report selects **20 GitHub repositories** implementing financial posting, double-entry bookkeeping, account balances, or the numerical and validation machinery of an accounting ledger. It covers specialized databases, network services, embedded libraries, accounting subsystems, and a separately identified group of offline ledger engines. The latter process accounting transactions but are not concurrent transaction servers. General databases, blockchain consensus projects, payment-provider SDKs, invoice-only applications, and financial dashboards are outside the selection.

The criteria identify worthwhile engineering study, not a production certification. A project can expose difficult correctness problems without solving every one perfectly. Claims below refer to the linked source or documented release family; deployment suitability, security, accounting compliance, and benchmark reproducibility were not independently audited.

## Criteria legend

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable models or interfaces supporting multiple use cases.
- **C3 — Performance and structure:** concrete performance constraints addressed through an understandable architecture.
- **C4 — Evolution:** evidence spanning years of compatibility work, testing, or deliberate complexity management, rather than age alone.

## Specialized databases and network ledger services

### 1. [tigerbeetle/tigerbeetle](https://github.com/tigerbeetle/tigerbeetle)

**Language / role:** Zig; replicated financial transaction database.

Study how a narrow account-and-transfer interface changes database design under contention. The architecture connects the accounting state machine to replication, a write-ahead log, checkpoints, and a forest of LSM trees, rather than delegating posting correctness to application SQL.

- **C1:** Immutable transfer history supports idempotence; checkpoint recovery reconstructs state by replaying the log. Replicated state and checksummed storage make crash and storage-failure behavior part of the accounting engine's design.
- **C3:** The documented execution model separates parallel storage prefetch from synchronous accounting execution. Batching and pipelined replication address contention while retaining a sequential commit order. These are architectural mechanisms, not a claim about a measured throughput figure.

**Entry point:** [Architecture and execution design](https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/ARCHITECTURE.md), which supplies the implementation rationale for both criteria.

### 2. [formancehq/ledger](https://github.com/formancehq/ledger)

**Language / role:** Go; programmable financial ledger service using Numscript.

Study the interaction between a financial transaction language, multi-posting atomic transactions, and relational storage. The linked contributor guide describes the PostgreSQL implementation and its v1/v2 compatibility behavior; it should not be read as a description of every newer release line.

- **C1:** The guide works through an easily missed race: locking an account balance row does nothing if the row does not yet exist. It describes creating missing balance rows before locking, and serializable import transactions to detect concurrent modification.
- **C2:** Logical ledgers, account/asset volumes, explicit postings, and Numscript provide reusable models for wallets, payment flows, and loans.
- **C3:** Configurable movement history and hash logging expose real write-cost tradeoffs. The guide explicitly identifies the ledger-wide lock required by synchronous hash chaining as a possible bottleneck.

**Entry point:** [Contributor guide: data consistency, storage features, and test strategy](https://github.com/formancehq/ledger/blob/main/CONTRIBUTING.md). Its migration, stress, and rolling-upgrade test descriptions are also useful reading.

### 3. [blnkfinance/blnk](https://github.com/blnkfinance/blnk)

**Language / role:** Go; ledger and financial workflow service.

Study a ledger that makes queued execution, inflight transactions, historical balances, reconciliation, and downstream work visible in its implementation. It is especially useful for understanding how posting behavior differs between synchronous calls and recovered queue work.

- **C1:** The transaction execution plan distinguishes zero-value split legs caused by rounding from queued zero-value work: the latter needs a persisted terminal rejection to avoid an endless recovery loop. This is a concrete example of financial semantics interacting with failure recovery.
- **C2:** Ledgers, balances, transaction workflows, and reconciliation form a reusable financial core rather than a single payment integration.
- **C3:** Weighted semaphores bound asynchronous transaction and bulk processors; balance-monitor work is separately bounded. Execution modes distinguish single, queued-batch, and hot queued-batch processing.

**Entry point:** [Transaction execution types and concurrency controls](https://github.com/blnkfinance/blnk/blob/main/transaction.go). The repository README establishes the surrounding ledger and reconciliation roles.

### 4. [LerianStudio/midaz](https://github.com/LerianStudio/midaz)

**Language / role:** Go; source-available core banking monorepo. The relevant subsystem is the **ledger core**, with the optional Tracer reservation integration. **Elastic License 2.0**, not a permissive open-source license.

Study the boundary between double-entry posting and an external transaction-validation service. The monorepo counts once; its CRM, fee, and fraud components are not separate ledger selections.

- **C1:** The topology document distinguishes pre-commit reservation from post-commit confirmation/release, including pending transactions, transport failures, fail-open versus fail-closed behavior, and expiry-based reconciliation.
- **C2:** Organizations, ledgers, assets, portfolios, accounts, and n:n transactions model several financial products. A transport-independent reservation interface admits REST and gRPC implementations.
- **C3:** The design discusses per-tenant connection-pool multiplication and why ledger and validation processes scale separately.

**Entry point:** [Ledger/Tracer deployment and failure topology](https://github.com/LerianStudio/midaz/blob/develop/docs/architecture/ledger-tracer-topology.md). The reviewed document explicitly marks some deployment guidance as recommendations and says the gRPC/mTLS integration's live-cluster soak was pending; those are limitations, not verified deployment results.

### 5. [mojaloop/central-ledger](https://github.com/mojaloop/central-ledger)

**Language / role:** JavaScript, with TypeScript declarations and SQL migrations; payment-scheme central ledger and settlement-position engine.

Study accounting at the boundary between participating financial institutions. This is a scheme-level ledger, not a generic end-user wallet database: participant positions, liquidity cover, limits, transfer states, and settlement are central concepts.

- **C1:** Position preparation checks the incoming transfer state, combines current and reserved positions, and computes available position against liquidity cover and participant limits. Incorrect states and insufficient liquidity lead to explicit rejection paths.
- **C2:** Separate participant, position, transfer, transaction, timeout, and settlement domains make the implementation reusable across payment-scheme workflows.
- **C3:** The prepare path processes bins of transfers while carrying accumulated position/state information, making the batching boundary and its accounting consequences inspectable.

**Entry point:** [Position prepare processor](https://github.com/mojaloop/central-ledger/blob/main/src/domain/position/prepare.js), supported by the repository's domain layout and transfer-state diagrams.

## Embedded posting libraries

### 6. [GaloyMoney/cala](https://github.com/GaloyMoney/cala)

**Language / role:** Rust; embeddable PostgreSQL ledger library, not a standalone server.

Study how transaction templates and database batching can coexist with explicit consistency rules. Journals, accounts, decimal amounts, CEL-parameterized templates, account sets, velocity controls, and an outbox give the library considerably more substance than a transfer helper.

- **C1:** The posting design locks the affected balance set, checks template versions, and evaluates chained balance and velocity changes before writing. Later postings in a batch observe earlier ones in input order. It also bounds distinct locked balances to avoid exhausting PostgreSQL's shared lock table.
- **C2:** Typed builders and parameterized templates separate application-specific financial operations from ledger persistence.
- **C3:** The posting pipeline uses array-oriented SQL phases, amortizing database round trips across a batch. Service, cache, and repository responsibilities are documented separately.

**Entry points:** [Posting pipeline design](https://docs.rs/cala-ledger/latest/cala_ledger/posting/index.html) and [crate API with template example](https://docs.rs/cala-ledger/latest/cala_ledger/). The `latest` documentation pages may resolve to different cached crate versions; use a fixed crate version when comparing implementations.

### 7. [envato/double_entry](https://github.com/envato/double_entry)

**Language / role:** Ruby / ActiveRecord; configurable double-entry accounting library.

Study the practical integration of a ledger into an existing application's database transaction. Account definitions, user-scoped account instances, allowed transfer codes, line history, and cached balances form a compact but substantial accounting abstraction.

- **C1:** The locking implementation orders account locks to avoid deadlocks, handles missing balance rows and concurrent creation, and requires the locking transaction to be outermost. The README also documents reconciliation between line history and cached balances.
- **C2:** Scoped accounts and configured transfer types support many application-specific money flows without baking their business rules into the storage layer.
- **C3:** The README explains the contention cost of unscoped accounts; balance rows serve both as a cache and as database lock targets.

**Entry point:** [Account-locking implementation](https://github.com/envato/double_entry/blob/main/lib/double_entry/locking.rb), alongside the repository README's locking and account-checker sections. Multi-transfer atomicity requires correct use of the documented locking API.

### 8. [flash-oss/medici](https://github.com/flash-oss/medici)

**Language / role:** TypeScript / Node.js / Mongoose; MongoDB double-entry books and journals.

Study a document-store implementation with hierarchical account paths, fluent debit/credit entry construction, journal reversal, and customizable schemas. Its documentation is unusually useful about the limits of balance reads and concurrency.

- **C1:** `Entry.commit` validates the zero total at the configured precision, validates documents, and propagates an optional MongoDB session. The README's overdraft example combines a database transaction with account write locks; merely calling the fluent entry API does not establish those guarantees.
- **C2:** Books, journals, hierarchical accounts, metadata, and schema customization support embedding in different applications.
- **C3:** Transaction documents duplicate frequently queried journal fields to avoid repeated population/join work, while write locks are limited to accounts whose balances need protection.

**Entry point:** [Entry construction and commit](https://github.com/flash-oss/medici/blob/master/src/Entry.ts). Read it with the README's ACID and voiding sections: amounts use JavaScript numbers, and backdated voids have a documented balance-cache caveat.

### 9. [elixir-fintech/double_entry_ledger](https://github.com/elixir-fintech/double_entry_ledger)

**Language / role:** Elixir / Ecto / PostgreSQL; event-sourced, multi-tenant ledger library.

Study a command-processing design that separates durable commands, journal events, transactions, and balance projections. Pending, posted, and available balances give it a useful authorization/settlement model.

- **C1:** Its optimistic-concurrency processor constructs an `Ecto.Multi`, retries stale-entry failures with exponential backoff, and exposes explicit handling for exhausted retries and malformed commands. The repository also describes idempotency keys and immutable balance-history records.
- **C2:** The processor behaviour defines callbacks for building and extending atomic workflows, while stores and APIs isolate accounts, instances, commands, and transactions. This offers an extensible application library rather than just an HTTP transfer endpoint.

**Entry point:** [Optimistic-concurrency processor behaviour and implementation](https://github.com/elixir-fintech/double_entry_ledger/blob/main/lib/double_entry_ledger/occ/processor.ex). No multi-year maturity claim is made for this selection.

### 10. [imetaxas/double-entry-bookkeeping-api](https://github.com/imetaxas/double-entry-bookkeeping-api)

**Language / role:** Java / Spring / JDBC; historical embedded bookkeeping library.

Study an older, readable separation of ledger construction, data access, transfer orchestration, and validation. Its README targets Spring 5 and embedded H2/HSQL/Derby or JDBC databases. Repository metadata showed its last push in 2018; treat it as historical code, not evidence of current framework support.

- **C1:** `transferFunds` uses serializable transaction isolation with rollback on exceptions. Validation checks duplicate references, account/currency agreement, zero-sum legs grouped by currency, and overdrafts after balance updates. The validator's scale-sensitive `BigDecimal.equals` comparison is a concrete numerical detail worth examining.
- **C2:** Ledger and chart-of-accounts builders, connection options, DAO interfaces, and transfer/validation services separate accounting semantics from several database configurations.

**Entry points:** [Transfer service](https://github.com/imetaxas/double-entry-bookkeeping-api/blob/master/src/main/java/com/yanimetaxas/bookkeeping/service/TransferServiceImpl.java) and [transfer validator](https://github.com/imetaxas/double-entry-bookkeeping-api/blob/master/src/main/java/com/yanimetaxas/bookkeeping/validation/TransferValidatorImpl.java). Historical status was checked through the [GitHub repository API](https://api.github.com/repos/imetaxas/double-entry-bookkeeping-api).

## Accounting frameworks and domain-rich posting subsystems

### 11. [adamcharnock/django-hordak](https://github.com/adamcharnock/django-hordak)

**Language / role:** Python / Django and database procedures; reusable bookkeeping core.

Study the choice to enforce accounting constraints below the ORM. Hordak is particularly instructive when several writers might access the same database, and when account trees and multiple currencies must retain consistent semantics.

- **C1:** Its trigger documentation describes deferred transaction-balance checks, currency/account consistency, bank-account type restrictions, and propagation of account-tree properties. The intent is to retain integrity even for writes that bypass Django.
- **C2:** Core accounts, transactions, legs, balance utilities, and statement-import models are intended as a foundation for separately built interfaces.
- **C4:** The changelog spans 2016–2024 with Django/Python compatibility work, migration fixes, rounding-allocation tests, and an explicit deprecation route through 1.17 before 2.0.

**Entry points:** [Database-trigger design](https://django-hordak.readthedocs.io/en/latest/hordak-database-triggers.html) and [changelog / upgrade guidance](https://django-hordak.readthedocs.io/en/latest/changelog.html). Some explanatory pages retain older amount-field/sign conventions; check the version-specific schema when studying 2.x.

### 12. [arrobalytics/django-ledger](https://github.com/arrobalytics/django-ledger)

**Language / role:** Python / Django; accounting engine and application framework.

Study the state transitions between editable journal entries, verified postings, locked ledgers, and financial reporting periods. Its entity → ledger → journal entry → transaction structure is the relevant accounting core; its UI is secondary here.

- **C1:** Journal-entry logic validates debit/credit balance and chart-of-accounts agreement. Posting eligibility considers verification, prior posting, ledger locking, and closed periods. These are accounting lifecycle invariants, not a claim that an application-level lock flag is a database concurrency lock.
- **C2:** Entity hierarchies, multiple charts of accounts, configurable fiscal years, and cash/accrual reporting support varied organizational structures and business workflows.

**Entry points:** [Journal-entry implementation](https://github.com/arrobalytics/django-ledger/blob/master/django_ledger/models/journal_entry.py) and [model API / dependency documentation](https://django-ledger.readthedocs.io/en/latest/models.html).

### 13. [ekmungai/python-accounting](https://github.com/ekmungai/python-accounting)

**Language / role:** Python / SQLAlchemy; accounting library with financial reporting.

Study the transformation of source-document transactions into posting pairs, including line items, compound entries, taxes, and reporting-period rules. Its advertised IFRS/GAAP reporting orientation is a project goal, not an independent compliance finding.

- **C1:** Transaction validation protects posted records and distinguishes closed and adjusting periods. Ledger construction creates corresponding post/folio entries, allocates compound postings, and handles tax-inclusive versus tax-exclusive amounts using decimal-backed fields.
- **C2:** Entities, account classifications, reporting periods, transaction subclasses, and report classes provide a reusable domain model for accounting applications.

**Entry points:** [Transaction lifecycle and validation](https://github.com/ekmungai/python-accounting/blob/main/python_accounting/models/transaction.py) and [posting construction](https://github.com/ekmungai/python-accounting/blob/main/python_accounting/models/ledger.py). The posting code contains explicit session commits; inspect the custom session behavior before assuming caller-wide atomicity. Hash fields are not treated here as proof of tamper-proof storage.

### 14. [ekmungai/eloquent-ifrs](https://github.com/ekmungai/eloquent-ifrs)

**Language / role:** PHP / Laravel Eloquent; accounting and reporting library.

Study the same broad accounting problem through a separate PHP implementation: transaction documents and line items feed a ledger, with VAT, exchange rates, reporting periods, and entity segregation. This is not counted as a fork or wrapper of the Python repository.

- **C1:** Posting rejects missing line items and unbalanced compound entries. Saving checks closed/adjusting periods and currency restrictions; ledger generation applies exchange rates and creates opposite entry types for posting pairs and VAT.
- **C2:** Transaction subclasses, reusable account/report models, configurable labels, and Eloquent integration let application developers compose several document and reporting workflows.

**Entry points:** [Transaction validation and posting](https://github.com/ekmungai/eloquent-ifrs/blob/master/src/Models/Transaction.php) and [ledger/VAT construction](https://github.com/ekmungai/eloquent-ifrs/blob/master/src/Models/Ledger.php). Numerical precision and the surrounding database transaction boundary deserve separate review; the selection does not imply exact arithmetic or atomicity merely from the package's accounting purpose.

### 15. [apache/fineract](https://github.com/apache/fineract)

**Language / role:** Java; financial-services monorepo. Relevant subsystems: **`fineract-accounting` and the journal-entry/accounting processors in `fineract-provider`**.

Study how lending, savings, and other product events become general-ledger entries. This is a richer domain example than a generic wallet: different accounting policies choose different posting processors, and branch closures constrain reversals.

- **C1:** Journal-entry services validate debit/credit amounts and eligible GL accounts. Reversal paths check accounting closure dates and construct opposite debit/credit entries while retaining links to the underlying product transaction.
- **C2:** Accounting rules, bridge data, processor interfaces, and factories separate product events from cash-based, upfront-accrual, and periodic-accrual accounting. The loan processor factory makes that variation directly inspectable.

**Entry points:** [Journal-entry write service](https://github.com/apache/fineract/blob/develop/fineract-provider/src/main/java/org/apache/fineract/accounting/journalentry/service/JournalEntryWritePlatformServiceImpl.java) and [loan accounting processor factory](https://github.com/apache/fineract/blob/develop/fineract-provider/src/main/java/org/apache/fineract/accounting/journalentry/service/AccountingProcessorForLoanFactory.java). The entire banking platform is counted once.

## Historical and smaller alternative storage designs

### 16. [moov-io/accounts](https://github.com/moov-io/accounts)

**Language / role:** Go / SQL; **archived historical** general-ledger and financial-account service. GitHub marks it archived on 2022-08-26.

Study the relationship between a customer-funds ledger and ACH-oriented banking operations. It is retained for its explicit account/transaction repository design and settlement-boundary rules, not as a current Moov deployment recommendation.

- **C1:** Transaction validation computes a signed zero-sum total. SQL persistence writes the transaction and its lines in a database transaction with rollback paths, and differentiates internal debit overdraft checks from external-bank handling and initial deposits.
- **C2:** Account and transaction repository interfaces, HTTP transaction/reversal operations, and interchangeable SQL storage support several account-service uses within the documented bank/FBO model.

**Entry points:** [Transaction model and API handlers](https://github.com/moov-io/accounts/blob/master/cmd/server/transactions.go) and [SQL transaction repository](https://github.com/moov-io/accounts/blob/master/cmd/server/transaction_storage_sql.go). The source includes unfinished edge-case notes; invariants and concurrency should be critically examined rather than assumed complete.

### 17. [hoophq/sequence](https://github.com/hoophq/sequence)

**Language / role:** Clojure / DynamoDB; compact historical asset-movement ledger service. The former `decimals/sequence` URL redirects here.

Study a less common alternative to mutable SQL balance rows: linked balance/transaction records, functional transformation of request context, and DynamoDB transactional writes. The inspected transaction implementation last changed in 2020, despite newer repository-level activity; no active-maintenance or long-term compatibility claim is made.

- **C1:** The code derives debit and credit balances from prior account records, constructs linked record identifiers, and submits the related records through DynamoDB transaction writes with conditional puts. This exposes the intended conflict-detection and atomic-write mechanism for examination; it is not a cryptographic-security endorsement of its hashes.
- **C2:** Tenant-qualified account keys, currency-aware balances, automatic account genesis, and an asset-neutral API support multiple ledgers and asset types.

**Entry points:** [Transaction transformation and chain writes](https://github.com/hoophq/sequence/blob/master/src/decimals/transactions.clj) and [DynamoDB persistence](https://github.com/hoophq/sequence/blob/master/src/decimals/dynamodb.clj). The implementation is smaller and less developed than the main service selections, but supplies a distinct storage architecture. Its [file commit history](https://github.com/hoophq/sequence/commits/master/src/decimals/transactions.clj) is the relevant historical reference.

## Offline ledger engines: accounting and numerical semantics

### 18. [ledger/ledger](https://github.com/ledger/ledger)

**Language / role:** C++; plain-text double-entry ledger and reporting engine.

Study an accounting language implementation with commodity-aware amounts and sophisticated reporting. The repository explicitly reads journals to produce reports without maintaining a separate database; this selection concerns its ledger semantics, not distributed posting.

- **C1:** The amount abstraction distinguishes commodities, internal precision, and display formatting, and expands precision during arithmetic. Its evolution records rounding, total-cost, valuation, and multi-commodity edge cases that are easy to mishandle in simpler money libraries.
- **C2:** Amounts, commodities, balances, transactions, expression evaluation, and reports compose a reusable accounting-language engine.
- **C4:** Release notes across 2019, 2020, 2023, and later development document behavioral regression fixes, Python compatibility changes, parser fuzzing, sanitizer builds, and regression-test expansion.

**Entry points:** [Amount abstraction](https://github.com/ledger/ledger/blob/main/src/amount.h) and [release/development history](https://github.com/ledger/ledger/blob/main/NEWS.md).

### 19. [hledgerorg/hledger](https://github.com/hledgerorg/hledger)

**Language / role:** Haskell; reusable `hledger-lib` accounting engine plus CLI, terminal, and web applications. The former `simonmichael/hledger` URL redirects here.

Study a functional decomposition of journal parsing, balancing, account data, valuation, and reports. The monorepo counts once, with the library as the principal study target.

- **C1:** The balancing implementation separately handles real and balanced virtual postings, converts amounts to cost where appropriate, and distinguishes entry-local from display-level precision. Missing amounts, inferred costs, and assertions are explicit parts of the engine rather than incidental report formatting.
- **C2:** Shared typed journal, amount, query, and report models support several interfaces and custom programs through the library.
- **C4:** The library changelog records years of API renaming, amount-style redesign, compiler/dependency compatibility work, and explicitly marked breaking changes. Recent preview and stable release lines should be distinguished when reading `main`.

**Entry points:** [Balancing implementation](https://github.com/hledgerorg/hledger/blob/main/hledger-lib/Hledger/Data/Balancing.hs) and [library changelog](https://github.com/hledgerorg/hledger/blob/main/hledger-lib/CHANGES.md).

### 20. [beancount/beancount](https://github.com/beancount/beancount)

**Language / role:** Python with a native parser; plain-text accounting and inventory/lot engine.

Study the distinction between a currency balance and an inventory of positions held at different costs. This is especially useful for securities and multi-currency accounting, where simply summing quantities destroys information needed for later booking and valuation.

- **C1:** Inventory keys include currency and cost identity, preserving lot distinctions. The model distinguishes creating, augmenting, and reducing lots, and supports transformations into units, cost, or market value. The changelog documents booking and extreme-precision failures that required correction.
- **C2:** Inventory reduction, positions, conversion functions, directives, and validation form reusable accounting primitives for tools beyond the command-line frontend.
- **C4:** The history shows maintenance across multiple years, Python-version support, and an explicit v2/v3 branch and release transition, rather than only a recent commit timestamp.

**Entry points:** [Inventory model and conversion design](https://github.com/beancount/beancount/blob/master/beancount/core/inventory.py) and [change history / version transition](https://github.com/beancount/beancount/blob/master/CHANGES).

## Search coverage, exclusions, and limits

Discovery used more than six distinct live-search formulations: double-entry databases; Go ledger services and programmable posting; Rust/PostgreSQL and CEL templates; Ruby locking and MongoDB journals; Python/Django accounting cores; PHP/Eloquent accounting; Java/JDBC libraries; Elixir command processing; Clojure/DynamoDB immutability; payment-scheme/core-banking accounting; plain-text ledger semantics; and PostgreSQL-native ledger extensions. Follow-up queries increasingly returned small transfer demonstrations, wrappers, or implementations repeating already-covered SQL designs. Searches were followed by opening canonical GitHub repository pages and reading additional primary implementation or design material for every retained project. Public GitHub API metadata and source-tree listings were used to resolve paths and historical status.

The selection spans Zig, Go, Rust, Ruby, TypeScript/JavaScript, Python, PHP, Java, Elixir, Clojure, C++, and Haskell. It includes custom replicated storage, PostgreSQL, other SQL backends, MongoDB, DynamoDB, and file-based journals. Scale ranges from embedded libraries and compact historical services to a specialized database and financial-services monorepos. Stars were not used as quality evidence.

SDKs such as Blnk's language clients and Modern Treasury's generated clients were excluded because the substantive posting engine is elsewhere. Numscript is discussed within Formance rather than counted as a second ledger. Forks and copied READMEs, including Medici and Python Accounting derivatives encountered in search, were not counted independently. Blockchain implementations, generic immutable databases, and pedagogical transfer APIs were excluded. PostgreSQL-extension searches found candidates such as `RustedBytes/pg-ledger`, but this report does not claim comprehensive coverage of that newer sub-ecosystem or retain candidates solely on their feature lists. Broad ERP applications were omitted unless a concrete accounting subsystem was the study target.

Source and documentation review is the evidence here: no candidate repository was cloned, installed, or executed, and no throughput claims were independently measured. Mutable branch links and occasionally differently cached documentation versions limit exact reproducibility. Archived/historical status is called out, and repository-level recency is not used to infer sustained maintenance. The C1–C4 assessments are reasoned judgments from the cited material, not a claim that every component of each codebase is uniformly exemplary.
