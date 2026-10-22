# Durable workflow execution engines

Research date: **2026-10-09**

This report selects 25 public GitHub implementations that persist the progress of multi-step computations and recover or resume them after interruption. It covers event-history replay, database-backed embedded runtimes, persistent process interpreters, and WebAssembly execution. Persistent BPMN engines are included where their execution and recovery machinery fits the category. Ordinary queues, cron schedulers, workflow editors, hosted-service client SDKs, and applications merely using another engine are outside the selection.

The criteria below identify engineering material worth studying, not a guarantee that every component is exemplary or that every project is equally ready for production. Repository metadata and primary implementation/documentation sources were inspected. The retained repositories were not marked archived at inspection; that alone is not a maintenance or support guarantee. Preview status and specific evidence limitations are called out where observed. Public source availability also does not imply identical licensing terms.

**Criteria legend**

- **C1 — Correctness:** difficult invariants, concurrency, replay semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable mechanisms supporting multiple applications or execution patterns.
- **C3 — Performance and architecture:** identifiable performance constraints addressed through understandable architectural choices.
- **C4 — Evolution:** sustained changes over years accompanied by compatibility, testing, migration, or complexity-management evidence.

## Distributed execution and replay servers

### 1. [temporalio/temporal](https://github.com/temporalio/temporal)

**Language/role:** Go; Temporal server, distinct from its language SDKs.

Study how a workflow service coordinates persistent history, mutable execution state, timers, and task delivery across separately scalable services. The [architecture overview](https://github.com/temporalio/temporal/blob/main/docs/architecture/README.md) separates deterministic workflow code from side-effecting activities and explains how workers exchange commands and results with the server.

- **C1:** The [History Service design](https://github.com/temporalio/temporal/blob/main/docs/architecture/history-service.md) explains transactional consistency between mutable state and internal tasks, validation of history against committed state, generation-based fencing, and a transactional outbox for eventual delivery to Matching.
- **C2:** Workflow/activity separation, durable timers, queries, and independently hosted workers form a reusable orchestration model rather than an application-specific pipeline.
- **C3:** History shards distribute execution ownership; persisted mutable-state summaries and in-memory caches avoid reconstructing the entire history on every request. The same History Service document connects these choices to latency and scaling constraints.

### 2. [cadence-workflow/cadence](https://github.com/cadence-workflow/cadence)

**Language/role:** Go; distributed long-running workflow orchestration server.

Cadence and Temporal share ancestry but have substantial separate development. Cadence is especially useful for studying how a durable engine defines a portable persistence contract across relational and nonrelational databases.

- **C1:** Its [persistence design](https://github.com/cadence-workflow/cadence/blob/master/docs/persistence.md) requires explicit transactional/locking behavior for SQL backends and conditional multi-row writes plus strong consistency for non-SQL implementations. Those requirements expose the invariants underneath the storage adapter.
- **C2:** Workflow execution storage is separated from visibility/search, and backend interfaces permit different stores for these workloads. The document also explains separate sharding keys for execution, history, and task-list records.
- **C4:** The [changelog](https://github.com/cadence-workflow/cadence/blob/master/CHANGELOG.md) records changes across 2023–2025, including persistence-test fixes, workflow-reset replication fixes, retracted releases, upgrade cautions, and migration toward adaptive task-list partitioning. This is concrete evolution and compatibility evidence, not an inference from repository age.

### 3. [restatedev/restate](https://github.com/restatedev/restate)

**Language/role:** Rust; durable execution server for services, keyed virtual objects, and workflows.

The [architecture reference](https://docs.restate.dev/references/architecture) is an unusually detailed starting point for a log-oriented runtime: ingress, replicated log, partition processors, and consensus-backed metadata have distinct responsibilities.

- **C1:** Quorum-committed log records determine durable order. Attempt epochs fence late responses from superseded executions; sealed log segments and metadata changes support leader handover. Cross-partition delivery uses sequence-number deduplication.
- **C2:** Invocation journals, durable promises, timers, service calls, and keyed state share the same execution infrastructure, supporting more than fixed workflow graphs.
- **C3:** RocksDB materializes partition-local state while the replicated log remains authoritative. Snapshots bound recovery work, and co-location of orchestration and keyed state keeps common operations within one partition. These are architectural mechanisms, not a throughput claim.

### 4. [resonatehq/resonate](https://github.com/resonatehq/resonate)

**Language/role:** Rust core server, with other server implementations, SDKs, and Lean/TLA+ specification in one monorepo.

Study durable distributed async/await as a protocol built around functions and promises. Count this monorepo once; the relevant entry points are its [core server architecture](https://github.com/resonatehq/resonate/blob/main/impl/server/core/README.md) and [executable specification](https://github.com/resonatehq/resonate/blob/main/spec/README.md).

- **C1:** A Lean abstract machine defines request transitions and invariants, a TLA+ model explores less-atomic execution, and a trace checker compares real traffic against the specification. The specification explicitly distinguishes proved properties from still-open theorems; it is not evidence that the entire system is formally verified.
- **C2:** Storage, worker transport, and gateway plugins are separate extension points. Durable function calls and remote calls retain a common promise-based programming model across languages and deployment styles.

## Task orchestration and event-driven workflow platforms

### 5. [inngest/inngest](https://github.com/inngest/inngest)

**Language/role:** Go engine with TypeScript platform components; durable step execution on user-hosted compute.

Study the contract between an orchestration server and handlers that may be invoked repeatedly. The [durable workflow execution walkthrough](https://www.inngest.com/docs/durable-execution/durable-workflows) follows state transmission, step identifiers, result persistence, retries, and waits.

- **C1:** Saved step results rebuild a handler's progress, while an interrupted side effect can still require idempotency. The documentation explicitly illustrates a refund succeeding before its result is saved, avoiding a misleading universal exactly-once interpretation.
- **C2:** Steps compose with parallel work, event waits, delays, error handling, and compensation using ordinary language control flow.
- **C3:** The documented TypeScript checkpointing path runs ordinary sequential steps in one handler and falls back to separate orchestration requests for cases such as retries and parallel execution. This offers a concrete study of reducing request overhead while preserving recovery semantics.

### 6. [hatchet-dev/hatchet](https://github.com/hatchet-dev/hatchet)

**Language/role:** Go orchestration engine, with multiple worker SDKs and a TypeScript interface.

Hatchet connects database-backed task scheduling to durable workflow composition. Its [architecture and guarantees](https://docs.hatchet.run/v1/architecture-and-guarantees) separates the API server, scheduling engine, workers, and PostgreSQL source of truth; the [durable execution guide](https://docs.hatchet.run/v1/durable-execution) explains checkpointed task progress.

- **C1:** State transitions are transactional, dependency resolution must remain consistent across restarts, and task delivery is explicitly at least once. Worker reconnection and retry behavior are part of the execution contract.
- **C2:** Dependencies, durable child work, waits, retries, schedules, and heterogeneous worker types support both background jobs and longer workflows.
- **C3:** Bidirectional gRPC supports dispatch and updates, while concurrency limits, rate limits, and priorities constrain work admission. The architecture also identifies database connections, payload size, graph complexity, and network placement as practical bottlenecks.

### 7. [conductor-oss/conductor](https://github.com/conductor-oss/conductor)

**Language/role:** Java; persistent, definition-driven distributed workflow engine.

This is the Conductor OSS repository selected for the report, rather than a second entry for the historical Netflix repository. Study the difference between persisting a workflow state machine and replaying user-language control flow.

- **C1:** The [durable execution semantics](https://github.com/conductor-oss/conductor/blob/main/docs/architecture/durable-execution.md) specify persisted task transitions, response timeouts, redelivery, and recovery by a sweeper. Its failure matrix covers worker failure after a side effect but before completion is reported.
- **C2:** Executions retain an immutable snapshot of their workflow definition, plus task state and variables. Wait/human tasks and failure workflows extend the same engine to callbacks, approvals, and compensation. Definition snapshots let existing executions continue independently of later metadata changes.

### 8. [littlehorse-enterprises/littlehorse](https://github.com/littlehorse-enterprises/littlehorse)

**Language/role:** Java server with polyglot SDKs; Kafka Streams-based workflow kernel.

The [architecture and deployment guide](https://littlehorse.io/docs/server/operations) explains a different persistence family: Kafka supplies the write-ahead log and changelogs, while RocksDB supplies local indexed state.

- **C1:** Requests enter Kafka before a processor applies them; missing local state can be rebuilt from changelogs. The design explicitly depends on Kafka durability and uses transactions heavily.
- **C2:** Workflow specifications, task definitions, external-event definitions, and worker APIs support general business processes; the repository's executable example combines retries, correlation, a timeout, and conditional progression.
- **C3:** Each scheduled task is managed by one kernel instance to reduce distributed coordination. A heartbeat-based worker assignment protocol controls which servers each worker connects to, balancing task coverage against excessive connections. Local state indexing and partitioning make performance choices visible.

## Embedded code-first runtimes and persistence providers

### 9. [dbos-inc/dbos-transact-py](https://github.com/dbos-inc/dbos-transact-py)

**Language/role:** Python; embedded database-backed workflow and durable-queue runtime.

DBOS is a useful counterpoint to server-centered orchestration. Its [architecture](https://docs.dbos.dev/architecture) places the execution engine in the application, with workflow inputs, step outputs, queue state, and scheduling state in a system database.

- **C1:** Recovery re-invokes a workflow with saved inputs and substitutes recorded step outputs. Deterministic workflow code and retry-safe steps remain explicit requirements. Distributed failure detection/recovery requires coordination rather than following automatically from merely sharing a database.
- **C2:** Decorated workflows and steps compose with durable queues, application clients, notifications, and version-aware recovery. This entry represents the Python engine, not every DBOS language implementation separately.
- **C3:** Database writes and payload sizes govern overhead; the documentation recommends externalizing large objects and returning references. Queue concurrency and rate controls connect application load to the database's capacity.

### 10. [cschleiden/go-workflows](https://github.com/cschleiden/go-workflows)

**Language/role:** Go; embeddable workflow runtime with pluggable persistence.

Study a comparatively compact implementation that combines Temporal-style workflow APIs with a direct-to-backend deployment model. The [maintainer's design walkthrough](https://cschleiden.dev/blog/2022-02-13-go-workflows-part1/) explains event scheduling, suspension, completion, and replay, while the repository documents the current API and backends.

- **C1:** Workflow execution must avoid nondeterministic Go constructs such as ordinary `select` behavior and map iteration. Activity scheduling/completion events reconstruct control flow after a worker disappears.
- **C2:** Workflow, activity, worker, client, and backend abstractions can be composed in one process or separate processes. The [repository guide](https://github.com/cschleiden/go-workflows/blob/main/README.md) lists SQLite, MySQL, PostgreSQL, Redis, and an in-memory testing backend.

The 2022 walkthrough is historical design evidence; its early production-readiness wording is not treated as a current status assessment.

### 11. [Azure/durabletask](https://github.com/Azure/durabletask)

**Language/role:** C#; Durable Task Framework orchestration runtime and storage providers.

Study how ordinary `async`/`await` is adapted into a persistent orchestration protocol. The [replay and durability guide](https://github.com/Azure/durabletask/blob/main/docs/concepts/replay-and-durability.md) distinguishes recorded events from local variables reconstructed during replay.

- **C1:** Deterministic orchestration decisions must match history; recorded activity results, timer events, child-orchestration outcomes, and failures drive resumption. Directly consulting wall-clock time can change the replayed command sequence.
- **C2:** A shared orchestration model works across extensible persistence providers, with activities, child workflows, external events, and durable timers.
- **C3:** The guide relates history growth to replay memory, latency, and storage, then explains `ContinueAsNew`, sub-orchestrations, and batching as ways to bound those costs.

**Support qualification:** The repository describes DTFx as community-maintained with best-effort issue handling and no official Microsoft support entitlement; its supported-product alternatives are separate offerings.

### 12. [microsoft/durabletask-netherite](https://github.com/microsoft/durabletask-netherite)

**Language/role:** C#; a separate execution/storage backend for Durable Task Framework and Durable Functions.

Netherite deserves a separate entry because it changes execution and persistence architecture, not just client bindings. The repository describes replacing many small storage operations with ordered partition streams, batching, and log/checkpoint storage.

- **C1:** [OutboxState](https://github.com/microsoft/durabletask-netherite/blob/main/src/DurableTask.Netherite/PartitionState/OutboxState.cs) holds outgoing batches until the generating event is durable and resends pending batches after recovery. [DedupState](https://github.com/microsoft/durabletask-netherite/blob/main/src/DurableTask.Netherite/PartitionState/DedupState.cs) rejects repeated inter-partition events using origin positions and subpositions.
- **C3:** Event Hubs streams and FASTER-backed partition state reorganize the I/O path for batching. The outbox implementation exposes the connection between commit positions, durability notifications, message transmission, and recovery.

Compatibility is intentionally bounded: the repository says existing application APIs can largely be reused, but existing task-hub contents cannot simply be migrated between backends.

### 13. [microsoft/duroxide](https://github.com/microsoft/duroxide)

**Language/role:** Rust; embeddable Tokio runtime with a bundled SQLite provider. **Preview**, as stated in the repository.

The [execution model](https://github.com/microsoft/duroxide/blob/main/docs/execution-model.md) makes a useful distinction between ordinary async execution and a durable orchestration turn: replay, advance until blocked, collect actions, persist, and await another completion.

- **C1:** Completion tokens bind to persistent event IDs; replay-safe select and join operations impose deterministic polling/result behavior. The [provider contract](https://github.com/microsoft/duroxide/blob/main/docs/provider-implementation-guide.md) requires atomic history append, queue updates, processed-message deletion, and lock release for a turn.
- **C2:** Runtime orchestration decisions are separate from the storage provider. Independent orchestration/activity queues, child workflows, timers, external events, and session routing make the runtime reusable without embedding business semantics in the database adapter.

This entry uses the Microsoft home; the archived former `affandar/duroxide` location is not counted separately.

### 14. [stidsborg/Cleipnir.ResilientFunctions](https://github.com/stidsborg/Cleipnir.ResilientFunctions)

**Language/role:** C#; the execution core integrated into Cleipnir.NET.

Select the actual runtime repository rather than counting its higher-level integration layer as another engine. Study how effect persistence, function ownership, and failed-replica recovery interact.

- **C1:** [IFunctionStore](https://github.com/stidsborg/Cleipnir.ResilientFunctions/blob/main/Core/Cleipnir.ResilientFunctions/Storage/IFunctionStore.cs) documents owner/version guards and serialized effect flushing. It explicitly forbids persisting a stale effect snapshot during a status change, which could overwrite concurrent flushes.
- **C2:** The store contract separates function state, messages, replicas, types, and dead-letter handling, allowing the execution machinery to work through backend implementations.
- **C1, further evidence:** [ReplicaWatchdog](https://github.com/stidsborg/Cleipnir.ResilientFunctions/blob/main/Core/Cleipnir.ResilientFunctions/CoreRuntime/Watchdogs/ReplicaWatchdog.cs) takes over a failed replica's messages before making its functions claimable. Its comments explain why reversing that order can create a restart that misses messages.

### 15. [airbnb/skipper](https://github.com/airbnb/skipper)

**Language/role:** Kotlin/JVM, usable from Java; embedded workflow runtime with storage and scheduler adapters.

Study checkpoint-based method resumption, persisted fields, hibernation, and lease-based scheduling. The [core concepts](https://skipper.airbnb.tech/docs/core-concepts/) explain deterministic workflow methods, reusable actions, and checkpoints around state mutations that can also be affected by signals.

- **C1:** The [TLA+ liveness model](https://github.com/airbnb/skipper/blob/main/formal/tla/README.md) ties safety properties to durable workflow tasks and timers. It models crashes, expired leases, and partial start/signal operations, and maps model transitions to implementation functions.
- **C2:** Typed action handles, persisted `@StateField` values, signals, waits, and pluggable persistence expose a reusable JVM orchestration model.

**Material limitation:** The checked-in model documents liveness failures at a named revision, including gaps between workflow/timer persistence and scheduling, and an ABA scenario involving task versions. It also lists unmodeled behaviors. This is a valuable failure-analysis study, not evidence of comprehensive verification or a claim that those findings describe every current release.

## Framework-native and persistent process interpreters

### 16. [durable-workflow/workflow](https://github.com/durable-workflow/workflow)

**Language/role:** PHP; embedded Laravel durable runtime, also used by the ecosystem's standalone server.

Study event-sourced coroutines within a conventional web-framework queue system. The [execution explanation](https://durable-workflow.com/docs/how-it-works/) describes Fiber-backed suspension and reconstruction of progress from history.

- **C1:** Workflow code replays, while activities are at-least-once queued work. Logical activity identity persists across retries and is distinguished from individual attempt identity, giving callers a meaningful idempotency key.
- **C2:** Activities, timers, side effects, child workflows, parallel composition, signals, and worker sessions share the Laravel persistence/queue integration. The core package is counted once; its server and language SDKs are not duplicate entries.

The [repository guide](https://github.com/durable-workflow/workflow/blob/main/README.md) also documents the v1/v2 transition: existing applications retain the legacy runtime to drain old work, while fresh v2 applications can omit its tables and watchdog. That is useful compatibility evidence, without asserting C4 solely from one migration.

### 17. [wavezync/durable](https://github.com/wavezync/durable)

**Language/role:** Elixir; PostgreSQL-backed engine in the monorepo's `durable/` package. The package README advertises a prerelease dependency.

This smaller project offers a BEAM-native pipeline model in which context passes between steps. The relevant implementation is the [executor](https://github.com/wavezync/durable/blob/main/durable/lib/durable/executor.ex), not its companion dashboard.

- **C1:** Resumption restores persisted context and the current step; execution also coordinates waiting, cancellation, child workflows, and parallel-step children. [StaleJobRecovery](https://github.com/wavezync/durable/blob/main/durable/lib/durable/queue/stale_job_recovery.ex) addresses workers that die while owning jobs, with separate optional recovery for zombie workflows.
- **C2:** A workflow DSL combines branches, parallel work, retries, compensations, scheduled starts, event waits, and human input. Ecto persistence and OTP supervision connect those abstractions to an existing Elixir application.

The source demonstrates substantive mechanisms, but this review does not establish comprehensive race freedom or years of production evolution; C4 is not claimed.

### 18. [floraison/flor](https://github.com/floraison/flor)

**Language/role:** Ruby; a persistent interpreter for a Scheme/Ruby-influenced workflow language.

Flor is useful for studying durability through explicit interpreter state and messages. Process definitions are separate from reusable taskers; execution data is serialized through Sequel-backed storage.

- **C1:** The [storage implementation](https://github.com/floraison/flor/blob/master/lib/flor/unit/storage.rb) stores execution/node state and manages message creation, reservation, and consumption. Reservation conditionally checks message status and prior metadata, exposing the concurrency problem of multiple executors claiming work.
- **C2:** The [cancellation guide](https://github.com/floraison/flor/blob/master/doc/cancelling.md) covers whole-execution and subtree cancellation, cancellation handlers, and tasker cleanup callbacks. This supports long-lived human and machine activities rather than only synchronous function composition.

Some documentation sections remain incomplete. The concrete implementation is the stronger entry point for unanswered execution and storage questions.

### 19. [danielgerlag/workflow-core](https://github.com/danielgerlag/workflow-core)

**Language/role:** C#; embeddable persistent workflow interpreter for .NET.

Study the separation between workflow definition, state persistence, queued execution, and cluster locking. Workflows can be authored through a fluent API or JSON/YAML definitions, with persistence between steps.

- **C1:** [Multi-node configuration](https://github.com/danielgerlag/workflow-core/blob/master/docs/multi-node-clusters.md) distinguishes local defaults from external queues and distributed lock providers required for clustered coordination. Persistence alone is not represented as sufficient for safe multi-node operation.
- **C2:** [Saga compensation](https://github.com/danielgerlag/workflow-core/blob/master/docs/sagas.md) composes undo steps, whole-saga cleanup, parameter mapping, and retry behavior. The same primitives work in code and serialized workflow definitions.

The default memory persistence provider is for demonstration/testing; the durable interpretation of this entry requires a persistent provider. The separately named `danielgerlag/conductor` wrapper is not the Conductor OSS Java engine above and is not counted here.

### 20. [elsa-workflows/elsa-core](https://github.com/elsa-workflows/elsa-core)

**Language/role:** C#; workflow execution core within the Elsa monorepo, with code and declarative authoring.

Elsa's architecture decisions are valuable because they explain specific failures in resumable graph execution rather than simply listing supported activities.

- **C1:** The [token-centric flowchart decision](https://github.com/elsa-workflows/elsa-core/blob/main/docs/adr/0005-token-centric-flowchart-execution-model.md) replaces execution-count heuristics that misbehaved around loops, XOR splits, and resumed activities. Tokens, blocking, and cleanup give joins and cancellation explicit semantics.
- **C2:** Race, stream, and converge merge modes express different reusable graph behaviors. The [bookmark-management decision](https://github.com/elsa-workflows/elsa-core/blob/main/docs/adr/0003-direct-bookmark-management-in-workflowexecutioncontext.md) places durable suspension bookmarks in canonical workflow context, while tracking newly created bookmarks separately for activity lifecycle behavior.

These documents are dated accepted design decisions, useful alongside current source; they should not be mistaken for an exhaustive specification of every later Elsa release.

### 21. [flowable/flowable-engine](https://github.com/flowable/flowable-engine)

**Language/role:** Java; BPMN execution and asynchronous job machinery within a broader BPMN/CMMN/DMN repository.

The relevant subsystem is the persistent BPMN process engine and its async executor. The [advanced engine documentation](https://www.flowable.com/open-source/docs/bpmn/ch18-Advanced) provides a concrete account of storage, acquisition, retries, and transaction boundaries.

- **C1:** Jobs are persisted before commit listeners dispatch them. Lock ownership and expiration coordinate executors; recovery releases expired locks. Timers, async continuations, suspended jobs, and dead-letter jobs have distinct lifecycle transitions.
- **C2:** Persistent process definitions support human/system tasks and extensible BPMN parsing and listeners, with embedded and service deployment options described in the repository.
- **C3:** Separate tables simplify acquisition queries. A full in-memory executor queue causes jobs to be unlocked for another executor, while acquisition batch sizes explicitly trade throughput against optimistic-lock contention.

### 22. [camunda/camunda](https://github.com/camunda/camunda)

**Language/role:** Java; Camunda monorepo, specifically the [Zeebe subsystem](https://github.com/camunda/camunda/tree/main/zeebe).

Study a BPMN workflow engine implemented as partitioned stream processing. The [internal-processing documentation](https://docs.camunda.io/docs/components/zeebe/technical-concepts/internal-processing/) follows commands, legal state transitions, emitted events, and follow-up commands that advance a process.

- **C1:** Job and process lifecycles restrict which commands are valid. Unexpected engine errors can ban an affected process instance, preserving its inspectable data while preventing one faulty execution from blocking the entire partition.
- **C3:** Per-partition adaptive limits control in-flight requests. Backpressure rejects excess work while allowing job-completion/failure messages, so overload control does not indiscriminately prevent already-running work from finishing.

This monorepo is counted once; Zeebe is not also listed under an older standalone repository path. The report concerns implementation study, not an assumption that all Camunda components share the same license or deployment entitlement.

## Sandboxed durable program execution

### 23. [golemcloud/golem](https://github.com/golemcloud/golem)

**Language/role:** Rust; distributed WebAssembly component runtime, including persistent agent/program execution.

The relevant subsystem is `golem-worker-executor`, especially its durable host boundary. The [reliability documentation](https://github.com/golemcloud/golem/blob/main/docs/src/content/v1.5/concepts/reliability.mdx) explains why a custom WASI implementation can observe external interactions and apply persistence/retry behavior.

- **C1:** The [durability implementation](https://github.com/golemcloud/golem/blob/main/golem-worker-executor/src/durable_host/durability.rs) distinguishes recording host invocations from reading recorded invocations during replay. It also handles replay-to-live transitions, stable invocation identity, retry classification, and restrictions on side effects in read-only execution.
- **C2:** Durability is implemented at reusable host interfaces rather than at one business-workflow DSL. HTTP, clocks, randomness, storage, and inter-component calls can participate in a common runtime model.

This is a broader durable-computing platform, included for its execution engine. The linked documentation is explicitly the versioned v1.5 material; main-branch implementation details can evolve beyond it.

### 24. [obeli-sk/obelisk](https://github.com/obeli-sk/obelisk)

**Language/role:** Rust; deterministic workflow engine built around WebAssembly components and WIT interfaces. **Pre-release**, with CLI/API/schema changes explicitly expected.

Study durable structured concurrency rather than only linear replay. The [structured-concurrency guide](https://obeli.sk/docs/latest/concepts/structured-concurrency/) describes execution trees and persistent join sets; the repository explains SQLite/PostgreSQL execution logs and separate workflow, activity, and webhook roles.

- **C1:** Closing a join set accounts for unfinished children, propagates errors after retry exhaustion, and applies explicit cancellation rules. Cancellation can traverse persisted join sets without advancing workflow code; the guide explains the resulting limits on cleanup/finally handlers.
- **C2:** WIT-generated bindings and component interfaces separate deterministic orchestration from side-effecting activities. Join sets support completion-order collection, while detached scheduling deliberately opts out of parent-child lifetime guarantees.

The explicit distinction between structured children and detached executions makes this a particularly useful comparison with native-language future-based engines.

### 25. [iopsystems/durable](https://github.com/iopsystems/durable)

**Language/role:** Rust; PostgreSQL-backed durable runtime for WASI component workflows, embeddable in another application.

The [execution walkthrough](https://github.com/iopsystems/durable/blob/main/README.md) records external-operation results and substitutes them when restarting a component. It distinguishes at-least-once external effects from the stronger guarantees for changes in the worker's own database.

- **C1:** The [simulation-testing guide](https://github.com/iopsystems/durable/blob/main/docs/deterministic-simulation-testing.md) exposes worker registration, task claims, transaction recording, leader changes, and suspension. Tests can inject clock, entropy, and PostgreSQL notification behavior while using a real database, making recovery interleavings inspectable.
- **C2:** The WASI/component boundary, durable HTTP/database interactions, embedded worker, and injectable runtime interfaces are reusable across workflows and host applications.

The testing guide contains an important limit: its described `DstScheduler` records scheduling events but does not itself control execution order. This report therefore does not equate that helper with exhaustive deterministic scheduling or proof of correctness.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations: general durable workflow/event-sourcing engines; lightweight Go/Rust runtimes; Python database-backed execution; C# persistent orchestration and providers; Ruby/Elixir/PHP frameworks; WebAssembly durable execution; Kafka-based and JVM engines; persistent BPMN execution; and replay/determinism alternatives. Follow-up searches targeted architecture, recovery, state transitions, and concurrency rather than stars. Later queries increasingly returned already-covered projects, wrappers, tutorials, adjacent agent frameworks, and small implementations of similar checkpoint/replay designs. Skipper was retained from a late JVM search because its implementation/model evidence added a distinct study angle.

Canonical owner/repository URLs and archive status were checked through opened repository pages or GitHub API-backed repository reads. Every retained entry has additional opened primary material beyond repository identification, and each has substantive architecture, implementation, or behavioral-contract evidence. Source links were taken from inspected trees or successfully opened documents. Where a versioned website failed to load, a current official page or repository implementation supplied the evidence instead; search snippets alone were not used to qualify entries.

The selection deliberately avoids separately counting language SDKs, DBOS language variants, Durable Workflow's server wrapper, Cleipnir.NET's integration layer, or monorepo subprojects. Cadence and Temporal are retained as separately evolved implementations; Netherite is retained because it supplies a materially different execution backend. General data-pipeline schedulers, lightweight in-memory DAG libraries, state-machine libraries without demonstrated durable execution, hosted-only engines, and educational implementations are outside this report. Ruby, Elixir, and PHP coverage is selective rather than exhaustive, and newer projects do not receive C4 merely for having tests or a recent push.

Criterion assignments are engineering judgments grounded in the cited mechanisms. No candidate code was executed, dependencies installed, services contacted beyond read-only research, or performance measurements independently reproduced. The report therefore compares study opportunities and documented contracts, not benchmark rankings, audited production guarantees, or uniform maintenance quality. Particularly material limits are the explicitly preview/prerelease runtimes, Skipper's revision-specific model failures, incomplete Flor documentation, and incomplete formal-proof coverage in Resonate.
