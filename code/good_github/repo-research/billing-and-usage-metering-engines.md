# Billing and usage metering engines

Research date: **2026-10-09**.

This selection covers software that turns consumption or subscription state into billable quantities, rated charges, credit deductions, and invoices. It includes SaaS billing backends, cloud metering and rating pipelines, and telecom charging systems. Metering-only components are identified explicitly. Payment SDKs, invoice editors, generic accounting systems, and monitoring tools without a substantive billing-metering role are outside the scope.

The 18 repositories below were checked through their GitHub pages or GitHub API metadata, then examined through additional primary documentation, implementation files, or tests. Criteria assessments are engineering judgments grounded in those sources; inclusion is a guide to worthwhile study, not a claim that every component is exemplary or production-ready.

## Criteria legend

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure recovery.
- **C2 — Abstractions:** substantial reusable models or extension mechanisms supporting multiple use cases.
- **C3 — Performance and structure:** concrete approaches to throughput, latency, storage, or workload scaling within an understandable architecture.
- **C4 — Evolution:** years of development accompanied by compatibility work, meaningful testing, or explicit complexity management. Repository age alone does not qualify.

## Subscription and usage billing platforms

### 1. [killbill/killbill](https://github.com/killbill/killbill)

**Java — subscription, invoice, payment, and usage billing engine.** Study how account-level invoicing reconciles subscription events, billing periods, plan changes, and previously generated charges. The useful architectural boundary is between catalog/entitlement state and the invoice computation it drives.

- **C1:** The [invoice subsystem explanation](https://docs.killbill.io/latest/invoice_subsystem) works through charged-through dates, advance versus arrears billing, proration credits, persisted events, and invoice repair. These are concrete temporal and financial consistency problems, with examples showing the underlying database records.
- **C2:** The [internal design](https://docs.killbill.io/latest/internal_design) separates core services into independently packaged modules communicating over a persistent event bus. Plugin contracts can change invoicing behavior or integrate gateways, tax systems, and other business logic.

Start with those two documents, then follow the corresponding `invoice`, `subscription`, and `beatrix` modules. Distinguish the public engine from capabilities supplied by the commercial Aviate extension.

### 2. [getlago/lago-api](https://github.com/getlago/lago-api)

**Ruby/Rails — Lago's actual metering and billing backend.** This is the implementation repository; the better-known `getlago/lago` deployment/overview repository is not counted separately. Especially useful for studying the interaction between event aggregation, price models, and proration.

- **C1:** The [prorated graduated charge implementation](https://github.com/getlago/lago-api/blob/main/app/services/charge_models/prorated_graduated_service.rb) assigns tiers using full quantities while calculating charges from prorated quantities. It handles events crossing multiple tiers, zero-proration additions, orphan removals, and negative intermediate results. This is substantially more instructive than a simple quantity-times-price example.
- **C2:** The [charge-model factory](https://github.com/getlago/lago-api/blob/main/app/services/charge_models/factory.rb) composes grouped charging with standard, graduated, percentage, package, volume, custom, and dynamic strategies. It also distinguishes forecasting without per-event aggregation from actual prorated billing.

These two files provide a compact route into the broader service and specification trees.

### 3. [openmeterio/openmeter](https://github.com/openmeterio/openmeter)

**Go — event metering, entitlements, credit balances, and billing.** A strong study target for the boundary between a high-volume consumption pipeline and transactional financial state.

- **C2:** CloudEvents and meter definitions feed separate balance, billing, and notification workers. The same consumption data supports usage queries, access decisions, and invoice generation.
- **C3:** The [architecture document](https://github.com/openmeterio/openmeter/blob/main/docs/architecture.md) makes the storage split explicit: Kafka decouples ingestion, ClickHouse stores events and aggregates, and PostgreSQL owns product and billing state. It also describes optional Redis state, a buffering collector, and leader-elected webhook reconciliation.

The same document exposes an important correctness boundary: event deduplication is disabled by default; when enabled, its storage can be in-process or Redis-backed. Do not infer unconditional exactly-once billing from the presence of Kafka. The repository describes its releases as beta and potentially breaking.

### 4. [meteroid-oss/meteroid](https://github.com/meteroid-oss/meteroid)

**Rust backend, TypeScript UI — pricing, subscription, invoicing, and metering monorepo.** Inspect the `modules/metering` ingestion service alongside the billing logic in `modules/meteroid/crates/meteroid-store`.

- **C1:** [Subscription proration](https://github.com/meteroid-oss/meteroid/blob/main/modules/meteroid/crates/meteroid-store/src/services/subscriptions/proration.rs) distinguishes advance-billed, usage, and one-time components; handles differing billing cadences; and rounds credits and charges to currency subunits. Embedded tests cover period boundaries, upgrades, component additions/removals, and exclusion of usage from proration. The implementation mixes decimal amount conversion with floating-point proration factors, a useful numerical design choice to examine carefully.
- **C3:** The [metering consumer](https://github.com/meteroid-oss/meteroid/blob/main/modules/metering/src/ingest/consumer.rs) batches Kafka events into ClickHouse using both row and time limits, commits consumer state after flushing, and restarts its processing loop after errors. The control flow exposes throughput and recovery decisions without requiring a claimed benchmark.

### 5. [flexprice/flexprice](https://github.com/flexprice/flexprice)

**Go — metering, pricing, subscription, invoice, and credit infrastructure.** Useful for studying why invoice idempotency must reflect the business operation rather than only a billing period.

- **C1:** The implemented [proration-invoice idempotency design](https://github.com/flexprice/flexprice/blob/main/docs/design/2026-07-22-proration-charge-invoice-idempotency.md) explains how changing two distinct subscription line items at the same effective time formerly collided. It defines operation-specific keys, canonicalizes line-item/date pairs for aggregated drafts, and documents which database uniqueness constraints and application checks remain in effect.
- **C2/C3:** The [architecture](https://github.com/flexprice/flexprice/blob/main/docs/ARCHITECTURE.md) separates domain contracts, repositories, services, and integrations; distinguishes PostgreSQL financial state from ClickHouse usage data; and uses Temporal orchestration plus Kafka retry/dead-letter handling. Separate deployment modes isolate API latency from consumer and workflow load.

The architecture identifies an enterprise boundary under `internal/ee`; some discussed billing paths are in that subtree. Public source visibility should not be read as a promise that all components have identical licensing or edition availability.

### 6. [uselotus/lotus](https://github.com/uselotus/lotus)

**Python/Django with TypeScript and Go components — usage pricing and packaging platform.** Focus on `backend/metering_billing`, particularly the distinction between usage used for access checks and usage used for charging.

- **C1:** The [metric-handler implementation](https://github.com/uselotus/lotus/blob/main/backend/metering_billing/aggregation/billable_metrics.py) explicitly distinguishes a gauge's current state from its billable normalized peak, and a rate's current value from its maximum over a billing period. These differences prevent apparently reasonable aggregations from silently changing billing semantics.
- **C2:** Counter, gauge, and rate handlers implement a shared interface for validation, creation, current usage, total billable usage, and daily breakdowns. The [invoice implementation](https://github.com/uselotus/lotus/blob/main/backend/metering_billing/invoice.py) composes recurring and usage charges, subtracts already invoiced amounts, and follows customer-specific plan versions during renewal.

The handler code also contains continuous-aggregate construction and special treatment of distinct counts, making it useful for examining where pre-aggregation is valid.

### 7. [polarsource/polar](https://github.com/polarsource/polar)

**Python/FastAPI backend, TypeScript clients — billing platform with a substantive metering subsystem.** Count the monorepo once; the relevant study area is `server/polar/meter`, with related event, customer-meter, and subscription code.

- **C1:** The [meter service](https://github.com/polarsource/polar/blob/main/server/polar/meter/service.py) restricts changes to a meter's filter and aggregation once it is aggregating events. Its quantity-query code distinguishes sums/counts and extrema from averages/distinct counts: the latter cannot be reconstructed by simply combining daily aggregates.
- **C2/C3:** Aggregation objects supply reusable query behavior, while the service selects an optimized total-calculation path only for suitable operators. The [aggregation tests](https://github.com/polarsource/polar/blob/main/server/tests/meter/test_aggregation.py) exercise operator summability and nested event properties against the database.

This is a useful example of billing semantics determining query optimization. The hosted merchant-of-record business and the source code are different evaluation concerns.

### 8. [useautumn/autumn](https://github.com/useautumn/autumn)

**TypeScript — billing, entitlements, credits, and balance processing.** Particularly relevant to AI and job-based products whose final consumption is unknown when work starts. The verified default branch was `dev`.

- **C1:** The [balance-worker durability tests](https://github.com/useautumn/autumn/blob/dev/apps/balance-worker/tests/unit/processor/track-lock-durability.test.ts) deliberately delay durable state application. They distinguish acknowledging ordinary tracking after log commitment from acknowledging a lock-taking operation only after its reservation row exists.
- **C2:** The [balance-locking contract](https://github.com/useautumn/autumn/blob/dev/apps/docs/mintlify/documentation/customers/balance-locking.mdx) separates reservation from finalization, with confirmation, release, adjusted actual usage, and expiry. The abstraction applies to token generation, queued jobs, and other operations with uncertain final cost.

Study the implementation/test contract alongside the API guide; a check followed by a separate debit is not equivalent to the atomic reservation described here.

### 9. [UniBee-Billing/unibee-api](https://github.com/UniBee-Billing/unibee-api)

**Go — UniBee's recurring billing backend.** The standalone deployment repository and generated client SDKs are excluded from the count. This smaller project is useful for tracing the full calculation from metric usage into invoice lines.

- **C1:** [Event charging](https://github.com/UniBee-Billing/unibee-api/blob/main/internal/logic/metric_event/event_charge/event_charge.go) computes an event's incremental charge as the difference between cumulative charges before and after usage, with standard allowances and graduated tiers. [Invoice calculation utilities](https://github.com/UniBee-Billing/unibee-api/blob/main/internal/logic/invoice/invoice_compute/util.go) reconcile discounts, tax, refunds, and line totals, including allocation of rounding remainders.
- **C2:** Plan-bound metric prices feed a common invoice construction path that also accepts subscription quantities and add-ons. This makes the repository more than a payment-gateway wrapper.

The monetary utilities contain floating-point intermediate calculations; inclusion recognizes the numerical problem and reusable calculation pipeline, not an audit of precision. API metadata showed the latest push in January 2026; no stronger maintenance claim is made.

## Cloud metering and rating pipelines

### 10. [openstack/cloudkitty](https://github.com/openstack/cloudkitty)

**Python — rating service; official substantive GitHub mirror of development at OpenDev.** CloudKitty prices collected measurements and exposes rated data. It is not itself a complete invoicing/payment platform.

- **C2/C3:** The [architecture](https://docs.openstack.org/cloudkitty/latest/admin/architecture.html) separates scope discovery, collection, ordered rating modules, storage, and retrieval. Scopes partition work among processors; dynamically loaded fetchers, collectors, and storage drivers support different infrastructure sources. Rating modules can use metadata rules or Python logic.
- **C4:** The [release history](https://docs.openstack.org/releasenotes/cloudkitty/) spans multiple OpenStack generations with explicit upgrade guidance. Concrete examples include historical-resource-metadata and reprocessing-concurrency fixes in the [2024.1 notes](https://docs.openstack.org/releasenotes/cloudkitty/2024.1.html), followed by a backward-compatible Loki metadata-query migration in the [2026.2 notes](https://docs.openstack.org/releasenotes/cloudkitty/2026.2.html).

Start with the architecture and release history to see how rating correctness evolves with storage and collector behavior.

### 11. [openstack/ceilometer](https://github.com/openstack/ceilometer)

**Python — cloud usage collection and normalization; official substantive GitHub mirror of OpenDev.** Include it as the metering stage of a billing pipeline. Its [project overview](https://docs.openstack.org/ceilometer/latest/contributor/overview.html) explicitly places rating and invoice generation outside its remit.

- **C2:** The [system architecture](https://docs.openstack.org/ceilometer/latest/contributor/architecture.html) defines polling and notification agents, listener/pollster plugins, sample/event normalization, pipelines, and multiple publishers. A common collection framework handles different OpenStack services and hardware sources.
- **C3:** Those agents support horizontal scaling and workload sharing. Compute-node polling keeps hypervisor access local, while central polling handles service APIs; downstream storage is delegated to systems such as Gnocchi. The design also identifies the load that polling can impose on source APIs.

This is a study in collecting financially useful usage data without embedding a specific pricing model into every collector.

### 12. [cloudfoundry-attic/cf-abacus](https://github.com/cloudfoundry-attic/cf-abacus)

**JavaScript/Node.js — historical Cloud Foundry usage metering and aggregation microservices. Archived by the owner on 2022-01-21.** Valuable as an architectural reference rather than a current deployment recommendation.

- **C1:** The [dataflow implementation](https://github.com/cloudfoundry-attic/cf-abacus/blob/master/lib/utils/dataflow/src/index.js) includes duplicate-output detection, database-backed checks, per-output/group locks, input logging, and special handling of duplicate responses from downstream sinks. It exposes the failure boundaries of a distributed usage pipeline.
- **C2/C3:** Reusable mapping/reduction machinery supports the collector, meter, accumulator, and aggregator stages. The [design notes](https://github.com/cloudfoundry-attic/cf-abacus/blob/master/doc/design.md) specify key/time document identifiers at each stage, making organization, resource-instance, consumer, and plan aggregation boundaries concrete.

Read the dataflow code together with those identifiers to understand how partitioning and aggregation shape storage access.

## Telecom charging and integrated provider billing

### 13. [cgrates/cgrates](https://github.com/cgrates/cgrates)

**Go — online/offline charging, rating, account balances, and sessions.** A useful contrast to monthly SaaS billing: charging decisions are also inputs to ongoing service authorization.

- **C1:** The [account service](https://github.com/cgrates/cgrates/blob/main/accounts/accounts.go) obtains locks for matching tenant/account keys, releases acquired locks on errors, and supports debit calculation across multiple accounts. Its simulation-versus-storage distinction exposes the difference between quoting consumption and committing it.
- **C2:** The [rate service](https://github.com/cgrates/cgrates/blob/main/rates/rates.go) selects rate profiles using event data and filters, then builds cost intervals and combines their charges. Together with account matching, this makes rating reusable across event types rather than fixed to one call-record schema.

These are current `main` source paths; older CGRateS material uses different subsystem layouts and should not be assumed to describe the current tree exactly.

### 14. [sigscale/ocs](https://github.com/sigscale/ocs)

**Erlang/OTP — 3GPP online charging and prepaid balance management.** Study session-based unit reservation and how protocol handlers share one rating core.

- **C1:** [The rating module](https://github.com/sigscale/ocs/blob/master/src/ocs_rating.erl) distinguishes initial, interim, final, and immediate-event operations; separately represents debited and reserved amounts; and returns explicit insufficient-credit outcomes. Balance buckets are read with Mnesia write locks within transactions. The API contract requires matching session attributes when releasing a session.
- **C2:** That module works with octets, seconds, messages, product offers, tariff/usage prices, and multiple protocol families. The [Diameter charging callback](https://github.com/sigscale/ocs/blob/master/src/ocs_diameter_3gpp_ro_application_cb.erl) is a concrete adapter into this shared rating interface.

The repository also produces charging records for downstream billing; online authorization and offline invoice production remain distinct responsibilities.

### 15. [freeside/Freeside](https://github.com/freeside/Freeside)

**Perl — integrated ISP/WISP/VoIP billing and provisioning.** Focus on the `FS` billing subsystem rather than treating the ticketing and monitoring portions as separate projects. This is a legacy codebase; GitHub metadata showed its latest push in July 2024, without an archive flag.

- **C1:** [Customer billing](https://github.com/freeside/Freeside/blob/master/FS/FS/cust_main/Billing.pm) disables autocommit, takes a customer row lock, runs pre-bill events, and rolls back on failures. It also coordinates cancellations, package changes, tax contexts, linked packages, and billing-date advancement.
- **C2/C3:** The [VoIP CDR package](https://github.com/freeside/Freeside/blob/master/FS/FS/part_pkg/voip_cdr.pm) composes usage charges with recurring charges and configurable rating policies. It retrieves outstanding CDRs through a bounded cursor and changes their status as they are processed, illustrating how a long-lived billing abstraction meets large-record-set constraints.

Useful for understanding transactional billing inside a broad operational application, including the complexity costs of many historical package options.

### 16. [Star2Billing/a2billing](https://github.com/Star2Billing/a2billing)

**PHP with Asterisk integration — prepaid and postpaid telecom rating and billing.** A historical study target: GitHub metadata showed its latest push in January 2023, and the installation documentation targets an old software stack. It was not marked archived.

- **C1:** The [rate engine](https://github.com/Star2Billing/a2billing/blob/develop/common/lib/Class.RateEngine.php) computes affordable call duration separately from final call cost. It combines initial and subsequent billing blocks, connection/disconnection charges, free time, duration rounding, and minimum charges—many interacting numerical rules.
- **C2:** The same engine selects tariff groups, rate cards, and trunks and serves different telecom products. The [integration/installation guide](https://github.com/Star2Billing/a2billing/blob/develop/INSTALL.rst) explains its AGI/AMI boundary, dialplan entry modes, and separate recurring-service and callback processes.

Use it to compare tariff-model expressiveness and legacy coupling. Its historical deployment instructions are evidence about architecture, not contemporary operational guidance.

### 17. [inextrix/ASTPP](https://github.com/inextrix/ASTPP)

**PHP, Lua, and C — FreeSWITCH-based VoIP billing platform.** The relevant subsystems are live call charging and post-call CDR processing; the verified default branch was `V6.0`.

- **C1:** The included [FreeSWITCH `mod_nibblebill` implementation](https://github.com/inextrix/ASTPP/blob/V6.0/freeswitch/mod/mod_nibblebill.c) maintains per-call billing state, mutex protection, initial-increment state, and a final-bill flag intended to prevent repeated hangup charging. Its low-balance and no-balance actions connect monetary state to call control.
- **C2:** [ASTPP's CDR processing layer](https://github.com/inextrix/ASTPP/blob/V6.0/freeswitch/fs/lib/astpp.cdr.php) handles customer, provider, reseller, and additional receiver records with corresponding balance adjustments. This reusable account hierarchy distinguishes the integrated application from the included switch module alone.

The switch module has upstream FreeSWITCH provenance; it is not counted as another independent repository. The source also provides a useful comparison between periodic charging and final settlement.

### 18. [magnussolution/magnusbilling7](https://github.com/magnussolution/magnusbilling7)

**PHP/Yii billing backend with a JavaScript administration UI — Asterisk provider billing.** Study the AGI calculation layer together with account/agent credit management; the verified default branch was `source`.

- **C1:** [Call calculation](https://github.com/magnussolution/magnusbilling7/blob/source/resources/asterisk/CalcAgi.php) computes credit-limited call duration, applies package offers and billing increments, separates provider purchase cost from customer charges, and records final CDR values. The interaction between free allowances, minimum durations, and reseller charges is the substantive correctness problem.
- **C2:** The calculator is used across several call flows, while [the credit manager](https://github.com/magnussolution/magnusbilling7/blob/source/protected/components/UserCreditManager.php) models prepaid/postpaid credit, parent-agent credit, refills, and follow-up service charging. Its Yii account layer and agent settlement paths make it a separate application study target alongside other Asterisk billing systems.

Treat this as a comparative legacy design, not evidence that check-then-update credit paths are universally race-free. Some architecture documents are only drafts; the assessment above comes from executable implementation files.

## Coverage, search method, and limitations

Discovery used more than six distinct live-search formulations: SaaS usage-based billing; Rust pricing engines; Go metering and credit systems; TypeScript billing/entitlements; Python billing platforms; OpenStack rating and telemetry; Cloud Foundry usage aggregation; Erlang online charging; telecom/Asterisk billing; Java/C++ rating engines; and municipal water/electricity billing. Follow-up searches and GitHub source-tree inspection located backend repositories, architectural documents, pricing algorithms, durability tests, and release notes. Later searches increasingly returned SDKs, deployment projects, commercial products without engine source, forks, and small utility-billing CRUD applications rather than stronger distinct engines.

The resulting coverage spans Java, Ruby, Go, Rust, Python, TypeScript/JavaScript, Erlang, Perl, PHP, Lua, and C; event-stream pipelines, modular billing applications, relational billing backends, and online prepaid charging. Related frontend/SDK/deployment repositories were consolidated into their implementation projects. Generic Gnocchi-style storage engines and FinOps dashboards were not added merely because billing systems can consume their output. jBilling-related distributions and NG Billing searches did not establish a sufficiently clear, independently verified canonical engine for an additional entry. Municipal utility results did not yield a retained engine with comparably strong primary evidence.

Flowglad appeared in live search results, but both a repository open and the GitHub API returned 404 during verification; it was excluded rather than replaced with an unaffiliated fork. Abacus is explicitly archived. CloudKitty and Ceilometer are retained because their official GitHub mirrors contain substantive source, even though development happens at OpenDev. Last-push observations for older projects are reported only as limited metadata, not proof of support or abandonment.

Verification was read-only: no candidate code was run, dependencies installed, or maintainers contacted. Source paths follow the branches verified on the research date and may move. Tests were read as evidence of intended behavior, not executed. No star counts or unverified throughput figures were used to justify inclusion, and the report does not certify billing accuracy, security, or deployment suitability.
