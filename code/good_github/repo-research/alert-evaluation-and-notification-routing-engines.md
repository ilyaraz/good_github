# Alert evaluation and notification routing engines

Research date: **2026-10-09**

This selection covers engines that turn observations into stateful alerts, suppress or correlate alerts, and route notifications through receivers or escalation policies. It includes standalone engines and explicitly identified subsystems of larger monitoring platforms. The 23 repositories span local monitoring cores, distributed metric evaluators, search and stream processing, alert aggregation, and on-call routing. A repository is counted once, even when it implements several stages.

The criteria describe reasons to study the selected subsystem, not a claim that every component is exemplary:

- **C1 — Correctness:** demanding state, time, concurrency, numerical, input-validation, or failure semantics.
- **C2 — Abstractions:** substantial reusable models and interfaces that support different policies, data sources, or delivery mechanisms.
- **C3 — Performance and structure:** explicit handling of workload, latency, memory, or distribution constraints through understandable architecture.
- **C4 — Evolution:** documented years of change accompanied by compatibility work, testing, or complexity management.

Each linked repository root was opened, and each entry also links inspected primary documentation or implementation material. Those links are practical starting points for further study. Criteria judgments and recommendations about what to study are grounded engineering assessments; reported behavior comes from the cited sources.

## Metric evaluators and distributed rulers

### 1. [prometheus/prometheus](https://github.com/prometheus/prometheus)

**Language / role:** Go; the alerting-rule evaluator and notification producer within Prometheus.

Study how query results acquire alert identities and lifecycle state over time. The relevant subsystem is the rule manager and its handoff to the notifier within the larger time-series database.

- **C1:** `AlertingRule` tracks pending, firing, and inactive state by label fingerprint; rejects duplicate label sets produced after applying alert labels; and retains resolved alerts to improve delivery across network failures and Alertmanager restarts. Hold duration and `keep_firing_for` impose different temporal conditions. Read the [alerting implementation](https://github.com/prometheus/prometheus/blob/main/rules/alerting.go).
- **C2:** Expression evaluation, periodic rule management, and queued notification delivery are separate components. The notifier decouples rule execution from slow delivery and discovers Alertmanager targets. The [internal architecture guide](https://github.com/prometheus/prometheus/blob/main/documentation/internal_architecture.md) is useful orientation, although it explicitly originated against Prometheus 2.3.1 and should be read alongside current code.

### 2. [VictoriaMetrics/VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics)

**Language / role:** Go; **vmalert**, the monorepo's standalone alerting and recording-rule service.

This is a useful study of evaluating rules outside the storage server, including the consequences of persisting rule results asynchronously.

- **C1:** Remote write persists alert state, and remote read can restore it after restart. Sequential rule evaluation does not make asynchronously written recording results immediately visible to dependent queries. Dynamic identifying labels can also prevent a pending alert from retaining its identity. These are concrete state and consistency concerns in the [vmalert guide](https://docs.victoriametrics.com/victoriametrics/vmalert/).
- **C2:** Data-source queries, recording/state storage, and Alertmanager delivery are independently configured boundaries; rule types accommodate several query ecosystems.
- **C3:** Group concurrency, evaluation delay/offset, and result limits expose workload controls. Exceeding a result limit discards the evaluation results rather than silently selecting a subset. The same [guide's rule-group reference](https://docs.victoriametrics.com/victoriametrics/vmalert/) explains the tradeoffs without requiring a claimed throughput figure.

### 3. [grafana/grafana](https://github.com/grafana/grafana)

**Language / role:** Go backend and TypeScript frontend; **`pkg/services/ngalert`**, Grafana's alerting subsystem.

Study a service that must reconcile query evaluation, rule revisions, per-instance state, and organization-specific notification configuration inside a larger application.

- **C1:** Evaluation distinguishes errors, no data, and successful results, and requires unique label sets for alert instances. The state manager interprets those results over time; the scheduler also manages changed and deleted rules. These concerns are described in the [ngalert architecture README](https://github.com/grafana/grafana/blob/main/pkg/services/ngalert/README.md).
- **C2:** Scheduling, evaluation, state management, storage, sending, and notification processing have explicit package boundaries. `MultiOrgAlertmanager` separates organizations' routing state, while senders connect evaluation to internal or external Alertmanagers. This is a substantial example of embedding an alert engine rather than simply calling a notification API. The same [subsystem guide](https://github.com/grafana/grafana/blob/main/pkg/services/ngalert/README.md) provides the package map; its Grafana 8 framing makes it architectural orientation rather than a promise that every scheduling detail remains unchanged.

### 4. [grafana/mimir](https://github.com/grafana/mimir)

**Language / role:** Go; the **ruler** in a multi-tenant metrics system.

Mimir is particularly useful for studying the boundary between scheduling rules and distributing the queries those rules require.

- **C1:** Tenant-scoped rules can use explicitly configured tenant federation. Federated evaluation applies relevant query limits and fails the evaluation when a participating query fails, rather than returning a misleading partial result. See the [ruler architecture](https://grafana.com/docs/mimir/latest/references/architecture/components/ruler/).
- **C3:** A hash ring distributes rule groups among rulers. Internal evaluation uses a ruler's querier; remote evaluation delegates to the query frontend and can benefit from query sharding. The documentation explains why expensive expressions can exceed their evaluation intervals in the internal arrangement. These are concrete resource and scheduling choices, not merely a distributed deployment diagram. The [evaluation modes and sharding discussion](https://grafana.com/docs/mimir/latest/references/architecture/components/ruler/) is the best entry point.

### 5. [thanos-io/thanos](https://github.com/thanos-io/thanos)

**Language / role:** Go; the **Ruler** evaluating Prometheus rules over distributed query APIs.

Study what changes when an alert expression reads several remote stores instead of one local database.

- **C1:** The ruler exposes a per-group partial-response strategy; aborting is the safe default described for alert evaluation because missing stores can hide the very condition being monitored. Replica labels also need appropriate removal before notification deduplication. See the [Ruler design and operational semantics](https://thanos.io/tip/components/rule.md/).
- **C3:** Query work is outsourced to the query layer, and rule sets can be functionally partitioned among replicated ruler groups. Evaluation-duration and failure metrics make missed scheduling budgets observable. The documented stateless mode further separates rule execution from local persistent time-series storage. The same [component guide](https://thanos.io/tip/components/rule.md/) makes the availability-versus-completeness tradeoffs unusually explicit.

### 6. [bosun-monitor/bosun](https://github.com/bosun-monitor/bosun)

**Language / role:** Go; expression-based monitoring and alerting server.

Bosun is valuable for studying the semantics of operations on tagged numerical result sets and how those semantics propagate into notification policy.

- **C1:** Warning and critical expressions accept scalar or number-set results. Unjoined groups are errors unless explicitly allowed; missing observations can become unknown alerts; dependency expressions suppress affected evaluations. The documentation also warns that the rule editor does not exercise dependencies. Read the [definitions reference](https://bosun.org/definitions).
- **C2:** Alerts, expressions, reusable macros, templates, lookups, and notifications are distinct configuration constructs. Lookup-selected notifications connect tag values to recipients without duplicating complete rules. The [same reference](https://bosun.org/definitions) distinguishes reloadable rule configuration from system configuration requiring restart. These abstractions make the project worth inspecting even without assuming a particular current maintenance cadence.

### 7. [ccfos/nightingale](https://github.com/ccfos/nightingale)

**Language / role:** Go backend; Nightingale / 夜莺 alert evaluation and notification processing.

This adds a Chinese open-source monitoring community and a central-versus-edge deployment model to the selection. The linked primary architecture material is in Chinese.

- **C1:** The evaluation path maintains pending-duration state for matching query results and removes that pending state when a result disappears. Alert events are saved before subsequent notification processing; notification-side transformations do not retroactively modify the saved event. See the [alerting walkthrough](https://n9e.github.io/zh/docs/usecase/alerting/).
- **C2:** Rules, subscriptions, notification rules, and processing steps are separate concepts. Relabeling, updating, dropping, and callbacks can be composed after event generation, providing a useful boundary between observation and delivery policy in the same walkthrough.
- **C3:** The [deployment architecture](https://n9e.github.io/zh/docs/prologue/architecture/) describes shared database/Redis state, automatic rule distribution across engine nodes, and edge evaluators near their data sources. This is evidence of explicit workload placement; it is not proof of exactly-once evaluation during failover.

## Search-backed and stream-oriented evaluators

### 8. [jertel/elastalert2](https://github.com/jertel/elastalert2)

**Language / role:** Python; periodic Elasticsearch/OpenSearch queries with stateful rule types and alert actions.

This is the substantive continuation of Yelp's ElastAlert, counted once rather than listing the original and successor as separate designs. Study the boundary between retrieving observations, deciding that a pattern matches, and delivering a notification.

- **C1:** Saved Elasticsearch state supports restarting without simply beginning from the current time. The engine handles backend outages and retries failed alert delivery for a configured period. The [reliability explanation](https://elastalert2.readthedocs.io/en/latest/elastalert.html) exposes these recovery responsibilities.
- **C2:** Rule types, alert actions, and match enhancements are independent extension points. Frequency, spike, flatline, and change rules reuse the query/processing machinery while custom actions can reuse matching logic. The [modularity guide](https://elastalert2.readthedocs.io/en/latest/elastalert.html) explains these interfaces. Retry support should not be read as an exactly-once delivery guarantee.

### 9. [opensearch-project/alerting](https://github.com/opensearch-project/alerting)

**Language / role:** Kotlin and Java; server-side OpenSearch monitors, triggers, and actions.

Study how alert lifecycle semantics change between a query-wide condition and a collection of independently identified matching buckets or documents.

- **C1:** Monitor contexts distinguish query/trigger errors from empty results. Bucket monitoring exposes newly created, deduplicated, and completed alerts to trigger/action logic, making lifecycle handling part of the API. Read the [monitor reference](https://docs.opensearch.org/latest/observing-your-data/alerting/monitors/).
- **C2:** Monitors, trigger conditions, and notification actions separate data retrieval from policy and delivery, while allowing different query granularities.
- **C3:** PPL monitors document query-duration, result-row, and payload-size bounds; custom conditions are validated, and dry runs evaluate without creating alerts or invoking actions. The [PPL monitor guide](https://docs.opensearch.org/latest/observing-your-data/alerting/ppl-monitors/) is a concrete entry point for bounded execution and testable policy semantics.

### 10. [influxdata/kapacitor](https://github.com/influxdata/kapacitor)

**Language / role:** Go; TICKscript stream and batch processing, especially the **AlertNode**.

Kapacitor is useful for studying alerts as stateful operators inside a dataflow, with distinct semantics for streaming observations and batch windows.

- **C1:** Alert levels can have separate reset predicates, and the node supports flapping detection, state-change-only delivery, and grouped alert state. Batch-wide conditions introduce additional semantics beyond evaluating each point independently. These mechanisms are specified in the [AlertNode reference](https://docs.influxdata.com/kapacitor/v1/reference/nodes/alert_node/).
- **C2:** Alert nodes compose with the larger processing graph; inhibition and alert topics separate event production from downstream handlers. Different receiver implementations can therefore share the same detection pipeline. The [node API](https://docs.influxdata.com/kapacitor/v1/reference/nodes/alert_node/) is a useful starting point for following those abstractions into the Go implementation.

### 11. [riemann/riemann](https://github.com/riemann/riemann)

**Language / role:** Clojure; event-stream processing and notification routing.

Riemann offers a markedly different design from YAML rule schedulers: alert policies are compositions of stream functions over event maps.

- **C1:** The index retains recent state by host/service, and TTL expiration produces events that can re-enter processing. Partitioning streams by keys is essential when detecting transitions independently for different services. The [concepts guide](https://riemann.io/concepts.html) explains this temporal model.
- **C2:** Partitioning, transition detection, rollups, and notification sinks are composable stream operators. This makes the code interesting for reusable stateful functional abstractions, including batching notifications.
- **C4:** The [changelog](https://github.com/riemann/riemann/blob/main/CHANGELOG.md) records 2018 integration/test work, 2020 transport-decoding fixes, 2023 Java compatibility and pull-request test-suite improvements, and a 2025 Opsgenie alert-closing fix. Those changes demonstrate sustained compatibility and failure-mode work, beyond repository age alone.

### 12. [moira-alert/moira](https://github.com/moira-alert/moira)

**Language / role:** Go; Graphite/Prometheus alert checking with Redis-backed scheduling and notifications.

Moira has a particularly readable service decomposition: filter, checker, API, and notifier. It makes a good case study of an operationally meaningful queue pipeline.

- **C1:** Checkers distinguish OK, warning, error, no-data, and exception states. A trigger schedule can suppress event creation, whereas a subscription schedule delays notifications already generated. Failed sends return to Redis for later processing. See the [architecture document](https://moira.readthedocs.io/en/latest/development/architecture.html).
- **C2:** Trigger definitions, tag-selected subscriptions, and delivery senders separate detection ownership from recipient policy.
- **C3:** The filter stores relevant metric patterns instead of indiscriminately retaining the input stream; Redis notifications drive checking, with separate queues for local and remote checks and periodic no-data checks. The [service/data-flow walkthrough](https://moira.readthedocs.io/en/latest/development/architecture.html) ties resource controls to the alert lifecycle.

## Monitoring cores with substantial alert subsystems

### 13. [sensu/sensu-go](https://github.com/sensu/sensu-go)

**Language / role:** Go with embedded JavaScript filtering; event pipelines in the Sensu backend.

The relevant study area is the public upstream event-processing engine. Documentation can also discuss commercial product features, so the whole product should not be assumed to reside in this repository.

- **C1:** Filters short-circuit when an event is denied. Inclusive filters require their expressions to pass, while exclusive filters reject on a matching expression; these distinctions affect whether a notification escapes suppression. JavaScript evaluation and reusable runtime assets add another execution boundary. See the [filter reference](https://docs.sensu.io/sensu-go/latest/observability-pipeline/observe-filter/filters/).
- **C2:** Pipeline workflows explicitly compose filters, a mutator, and a handler. Their semantics also specify that filters/mutators attached to a referenced handler are ignored in pipeline execution, avoiding ambiguous layering. The [pipeline guide](https://docs.sensu.io/sensu-go/latest/observability-pipeline/observe-process/pipelines/) is useful for studying reusable policy resources and configuration precedence.

### 14. [Icinga/icinga2](https://github.com/Icinga/icinga2)

**Language / role:** C++; check-state transitions, dependencies, and notification objects within Icinga 2.

Study the interaction of retry-driven state machines and a configuration language that assigns notification policy to many services.

- **C1:** Soft failures become hard states only after configured attempts. Acknowledgements, downtime, and reachability/dependency conditions can suppress notifications, while recovery routing depends on earlier notification history. These interacting gates are detailed in the [monitoring-basics implementation guide](https://github.com/Icinga/icinga2/blob/master/doc/03-monitoring-basics.md).
- **C2:** Typed objects, inheritance, and `apply` rules compose services, notifications, users, groups, time periods, and notification commands. This offers reusable configuration abstractions that are substantially richer than a list of webhook URLs. The [notification sections of the same guide](https://github.com/Icinga/icinga2/blob/master/doc/03-monitoring-basics.md) connect the object model to delivery behavior.

### 15. [NagiosEnterprises/nagioscore](https://github.com/NagiosEnterprises/nagioscore)

**Language / role:** C; host/service state and notification logic in Nagios Core.

Nagios remains an instructive study of notification eligibility as a sequence of explicit decisions. It belongs here because those decisions are an engine in their own right, independently of the age of the surrounding monitoring interface.

- **C1:** Notification checks are driven by check results and hard-state changes; a notification interval is not itself an autonomous send timer. Host failure can suppress service notifications, recovery depends on prior problem notification, and overlapping contact-group membership must not duplicate delivery. See the [notification algorithm documentation](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/notifications.html).
- **C2:** Global, host/service, and contact-level filters combine with time periods and notification commands. The [documented filter sequence](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/notifications.html) provides a concrete model for separating eligibility, recipients, and transport without collapsing every rule into one callback.

### 16. [zabbix/zabbix](https://github.com/zabbix/zabbix)

**Language / role:** C server with Go/PHP elsewhere in the repository; action and escalation processing. **Official GitHub mirror:** Zabbix documents its primary Git server separately and mirrors master and supported releases to GitHub in its [source-access guide](https://www.zabbix.com/documentation/7.0/en/manual/installation/getting_zabbix).

Study long-lived escalation state whose behavior depends on maintenance, action changes, and overlapping events.

- **C1:** Maintenance can pause rather than cancel escalation. Action time-period conditions affect initiation differently from ongoing steps, and disabling versus deleting an action has different cancellation behavior. Overlapping escalations also have defined interactions. These cases are explained in the [escalation semantics](https://www.zabbix.com/documentation/current/en/manual/config/notifications/action/escalations).
- **C2:** Actions compose numbered steps, durations, recipient groups, media, and operations, allowing delayed, repeated, and multi-stage response policies. The same escalation guide makes the model inspectable without assuming that sending an initial message completes the workflow.

### 17. [netdata/netdata](https://github.com/netdata/netdata)

**Language / role:** Primarily C for the relevant **health/alert engine**; a larger mixed-language monitoring repository.

Netdata is useful for studying compact alert expressions close to collected measurements, including exceptional numerical values and the distinction between state and notification timing.

- **C1:** Lookup failures and arithmetic can produce NaN or infinity. State-aware threshold expressions support hysteresis, while notification delay, direction, and backoff affect execution of notifications without postponing the underlying state transition. See the [alert-configuration reference](https://learn.netdata.cloud/docs/alerts-&-notifications/alert-configuration-reference).
- **C2:** Chart-specific alerts and reusable templates combine lookups, calculated expressions, warning/critical conditions, label matching, and an external notification executable. This cleanly exposes several reuse boundaries. The [same reference](https://learn.netdata.cloud/docs/alerts-&-notifications/alert-configuration-reference) is the entry point for following the health subsystem rather than treating the entire dashboard as the subject.

### 18. [apache/hertzbeat](https://github.com/apache/hertzbeat)

**Language / role:** Java backend and TypeScript UI; **`hertzbeat-alerter`** and its collection-to-alert pipeline.

Study a Java implementation that links monitoring results to grouped alerts, recipient rules, templates, and typed notification handlers.

- **C2:** The dispatcher stores a grouped alert, matches notice rules, selects receiver-specific handlers and templates, and invokes post-alert plugin hooks. It scopes a notification's constituent alerts to the rule and recomputes shared labels/status. These are substantive reusable boundaries in [AlertNoticeDispatch](https://raw.githubusercontent.com/apache/hertzbeat/master/hertzbeat-alerter/src/main/java/org/apache/hertzbeat/alert/notice/AlertNoticeDispatch.java).
- **C3:** The project's [collection architecture walkthrough](https://hertzbeat.apache.org/blog/2025/03/30/how-does-metrics-collection-work/) follows scheduled tasks through worker pools and queues into real-time alert calculation and then storage. Collection distribution uses consistent hashing. The source dispatcher also submits notification work to a worker pool and handles task rejection explicitly. These choices expose throughput and overload concerns without establishing a benchmark or guaranteed delivery on rejection.

## Alert aggregation, notification routing, and escalation

### 19. [prometheus/alertmanager](https://github.com/prometheus/alertmanager)

**Language / role:** Go; deduplication, grouping, inhibition, silencing, and receiver routing for alerts generated elsewhere.

This is the central selection for studying delivery policy independently of expression evaluation.

- **C1:** High-availability peers receive alerts independently and replicate silence and notification state. Grouping, inhibition, and silence matching interact with that distributed state; the architecture explicitly advises sending to all peers rather than load-balancing alert input. See the [Alertmanager architecture](https://github.com/prometheus/alertmanager/blob/main/docs/alertmanager.md).
- **C2:** A routing tree selects aggregation and receiver behavior, while silence and inhibition mechanisms express different suppression policies. The architecture describes the corresponding processing responsibilities.
- **C4:** The [changelog](https://github.com/prometheus/alertmanager/blob/main/CHANGELOG.md) documents API v1 deprecation in 2019 and removal in 2024, plus the UTF-8 matcher transition with fallback/classic modes and configuration validation. This is concrete evidence of managing compatibility across years, rather than merely accumulating integrations.

### 20. [alerta/alerta](https://github.com/alerta/alerta)

**Language / role:** Python; alert aggregation, lifecycle management, correlation, and plugin-based routing.

Alerta is particularly useful for studying how heterogeneous upstream events become one actionable alert record.

- **C1:** Deduplication updates an existing alert using its identity, while correlation associates explicitly related event types. Severity changes interact with open/closed/acknowledged state; an acknowledged alert can reopen on a worsening condition. The [alert-processing tutorial](https://docs.alerta.io/gettingstarted/tutorial-4-alerts.html) walks through these distinctions.
- **C2:** Plugins have separate pre-receive, post-receive, and status-change hooks. A routing plugin can choose an ordered subset of downstream plugins from alert attributes, rather than hard-wiring every integration into ingestion. The [plugin tutorial](https://docs.alerta.io/gettingstarted/tutorial-3-plugins.html) also explains why plugin network timeouts matter to processing latency. This provides useful extension points and highlights the consequences of placing custom work on the processing path.

### 21. [target/goalert](https://github.com/target/goalert)

**Language / role:** Go backend and TypeScript UI; on-call schedules, rotations, escalation policies, and outgoing notifications.

GoAlert stands out for implementing much of escalation progression in database operations rather than hiding it entirely in application timers.

- **C1:** The escalation manager's SQL couples selection of eligible alerts, progression of escalation state, and creation of notification work. It uses processing locks and row-locking constructs, including `FOR UPDATE SKIP LOCKED`, to manage concurrent work. Read [escalationmanager/db.go](https://github.com/target/goalert/blob/master/engine/escalationmanager/db.go).
- **C3:** Separate bounded queries handle new, normal, and deleted-step escalation cases; limited batches and skipped locked rows make contention and work budgets explicit. The same implementation is a useful study of SQL as an engine component.
- **C2:** The [engine source tree](https://github.com/target/goalert/tree/master/engine) separates escalation, schedules, rotations, heartbeat processing, notification-policy cycles, and processing locks. Follow those boundaries to understand how changing on-call ownership affects delivery without rebuilding every policy around individual phone numbers.

### 22. [grafana-cold-storage/oncall](https://github.com/grafana-cold-storage/oncall)

**Language / role:** Python backend and TypeScript frontend; **historical, archived Grafana OnCall OSS**. The former `grafana/oncall` URL redirects to this canonical cold-storage repository. It is included as a code study, not as an actively maintained deployment recommendation.

Study the three-level model connecting incoming alert routes, escalation chains, and each recipient's notification preferences.

- **C1:** Routes are evaluated in order, and escalation steps introduce waits, repeats, and notification actions. Acknowledgement, resolution, and silencing affect continued escalation. These temporal rules are documented in the [routing and escalation guide](https://grafana.com/docs/oncall/latest/configure/escalation-chains-and-routes/).
- **C2:** Integration routing selects reusable chains; chains select on-call users or other targets; personal notification policies determine delivery channels. The [alerts source tree](https://github.com/grafana-cold-storage/oncall/tree/dev/engine/apps/alerts) exposes models, tasks, escalation snapshots, migrations, and tests for examining that separation. The product documentation also contains Cloud-only features; those are not evidence that the archived OSS implements them.

### 23. [keephq/keep](https://github.com/keephq/keep)

**Language / role:** Python backend and TypeScript UI; alert-driven workflows, enrichment, and notification/provider actions.

The relevant subsystem is the workflow manager that turns incoming alert events into selected workflow executions. It provides a concrete example of controlling mutable execution context while optimizing repeated trigger evaluation.

- **C1:** The manager creates a separate parsed workflow instance for each queued run because execution mutates its context, and it protects scheduler queue insertion with a lock. This is an explicit concurrency invariant in [workflowmanager.py](https://github.com/keephq/keep/blob/main/keep/workflowmanager/workflowmanager.py).
- **C2:** Declarative triggers, filtering, enrichment steps, and provider actions support different alert-response policies. The manager additionally translates supported legacy filters into CEL expressions, making compatibility part of the execution boundary.
- **C3:** It fetches enabled tenant workflows once and reuses parsed workflows for trigger evaluation across an event batch, while keeping execution instances separate. The [same implementation](https://github.com/keephq/keep/blob/main/keep/workflowmanager/workflowmanager.py) shows the distinction between reducing repeated parsing and sharing mutable runtime state. These observations do not depend on a claimed throughput number.

## Search coverage and limitations

Discovery used live web searches across more than six distinct formulations, followed by repository-root and primary-document/source inspection. Search angles included:

- Prometheus-compatible alert evaluation, HA notification deduplication, ruler sharding, and remote query execution.
- Elasticsearch/OpenSearch monitor engines, query windows, state recovery, and custom rule types.
- Graphite alerting, Redis-backed checking, stream functions, batch dataflows, and tagged expression languages.
- On-call routing, escalation chains, schedules, transactional notification work, and alert correlation plugins.
- Traditional C/C++ monitoring cores, dependency suppression, notification filters, maintenance, and recovery semantics.
- Java/JVM, Python, Go, Clojure, and additional Rust/Erlang/Scala-oriented searches to avoid selecting solely from one implementation community.
- Chinese-language searches for 夜莺 alert-engine architecture and notification processing, which added Nightingale's central/edge model.
- Historical alternatives and successive broader searches, which increasingly returned already-covered engines, thin webhook routers, notification adapters, or adjacent workflow products.

The resulting selection deliberately includes both widely used architectural reference points and less commonly cited engines such as Bosun, Moira, Riemann, and Nightingale. Shared ancestry does not make the distributed Prometheus-family systems interchangeable: their entries identify distinct evaluation, tenancy, storage, or failure-handling questions. ElastAlert's original and successor were not counted separately. Monorepos are counted once and scoped to their alerting subsystem.

Excluded classes include rule collections, awesome lists, tutorials, generated wrappers, UI-only dashboards, general notification SDKs, and thin forwarding services without inspected evidence of a substantial engine. Searches also considered older alternatives such as Seyren, Cabot, and Argus; this report does not claim to exhaust every historical implementation or to establish their current maintenance status.

This was read-only source and documentation research: no candidate code was installed, executed, benchmarked, or subjected to a full correctness audit. Architecture guides can lag implementation; historical framing is called out where evident. Zabbix is explicitly identified as an official mirror, and Grafana OnCall as archived. Other entries do not imply a maintenance or support guarantee. C4 is used only where inspected multi-year compatibility/testing history supports it. The report is a selection guide for engineering study, not a uniform endorsement or a quantitative performance ranking.
