# Stateful stream processing engines

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing engines that maintain state across stream records: keyed processors, event-time windows, complex-event queries, continuously maintained SQL results, incremental dataflow, and streaming graph computations. It includes distributed services and substantial embedded runtimes. For large monorepos, the relevant processing subsystem is named explicitly. Stateful SQL databases qualify through their incremental execution and state-management internals; brokers, connectors, and generic orchestration alone do not.

The emphasis is on what an experienced engineer can learn from implementation choices and their constraints. Inclusion is not a deployment recommendation, a licensing assessment, or a claim that every component is exemplary. Architecture documents sometimes describe a particular release or an intended model; those limits are called out below. In particular, consistent engine state does not automatically make arbitrary external side effects exactly once.

## Criteria legend

- **C1 — Difficult correctness:** meaningful invariants, concurrency, event-time or numerical semantics, adversarial inputs, or recovery and failure modes.
- **C2 — Reusable abstractions:** substantial mechanisms that support different operators, workloads, connectors, state representations, or execution settings.
- **C3 — Performance with structure:** concrete resource or throughput constraints addressed through an understandable architecture.
- **C4 — Sustained evolution:** evidence spanning years that also demonstrates compatibility work, testing, or deliberate management of complexity. Repository age or stars alone do not qualify.

The criteria stated for each repository are grounded in the linked primary material. Suggestions about what to study are editorial judgments based on that evidence.

## Distributed JVM engines

### [apache/flink](https://github.com/apache/flink)

**Language/role:** Java, with Scala components; distributed stateful dataflow engine.

Flink is particularly useful for studying how state partitioning, event processing, recovery, and backpressure interact within one runtime. Its state model distinguishes state owned by an operator from state associated with keys.

- **C1:** Checkpoints combine operator state with stream positions. Barrier alignment prevents records from different checkpoint epochs from contaminating the same snapshot; unaligned checkpoints instead capture relevant in-flight data. Recovery therefore involves both stored state and the records needed to reconstruct execution. See the [stateful processing design](https://github.com/apache/flink/blob/master/docs/content/docs/concepts/stateful-stream-processing.md).
- **C2:** Key groups provide a unit for assigning and redistributing keyed state independently of individual user-defined operators. This makes rescaling and the keyed programming model reusable across aggregations, joins, and custom stateful functions. The same [design document](https://github.com/apache/flink/blob/master/docs/content/docs/concepts/stateful-stream-processing.md) explains the relationship.
- **C3:** Aligned versus unaligned checkpoints expose a concrete tradeoff between waiting under backpressure and persisting additional channel data. Study this alongside the checkpoint invariants, rather than treating checkpoint latency as an isolated optimization.

### [apache/spark](https://github.com/apache/spark)

**Language/role:** Scala/Java; the **Structured Streaming** subsystem of the Spark monorepo.

The relevant subject is incremental execution of relational queries, especially micro-batch scheduling and the state-store boundary. This repository counts once; the broader batch engine is context rather than a separate selection.

- **C1:** The versioned state-store contract applies updates transactionally and associates successive versions with processing progress. Checkpointed offsets and replay also depend on source and sink capabilities; the documented end-to-end guarantee assumes replayable sources and appropriate sink behavior. See the [Spark 3.5.8 programming guide](https://spark.apache.org/docs/3.5.8/structured-streaming-programming-guide.html).
- **C2:** Streaming reuses DataFrame/Dataset and SQL abstractions, while `StateStoreProvider` separates stateful operators from storage implementations. This is a useful example of exposing a common query model across batch and continuously arriving data.
- **C3:** The guide explains why RocksDB-backed state can move large state out of JVM-managed memory and reduce garbage-collection pressure. Its memory and checkpoint options make the resource implications of the state-store interface concrete. These details are grounded in the [versioned guide's state-store sections](https://spark.apache.org/docs/3.5.8/structured-streaming-programming-guide.html), not a claim about every later default.

### [apache/storm](https://github.com/apache/storm)

**Language/role:** Java; especially **Trident**, Storm's stateful micro-batch abstraction.

Trident is a compact case study in making repeated execution safe when a source may replay either the same batch or a different batch for an outstanding transaction.

- **C1:** Transactional state records a transaction identifier with its value to avoid applying a replay twice. Opaque transactional state additionally preserves the preceding value so that retries whose batch contents change can still derive the correct result. Ordered state updates are part of this contract. The [Trident state document](https://github.com/apache/storm/blob/master/docs/Trident-state.md) develops these cases explicitly.
- **C2:** `State`, `StateFactory`, query/update functions, and `MapState` separate processing logic from persistence and transactional policy. They are useful abstractions to study when implementing multiple storage backends under one processing API.
- **C3:** Batched `multiGet`/`multiPut` operations and cached maps reduce remote store round trips while preserving the state-update model. See the same [state implementation guide](https://github.com/apache/storm/blob/master/docs/Trident-state.md).

The document contains historical examples; its transactional reasoning is the evidence here, not its old descriptions of other systems' capabilities.

### [apache/samza](https://github.com/apache/samza)

**Language/role:** Java/Scala; distributed stream processor. The repository identifies itself as an **official Apache Samza mirror**.

Samza offers a clear architecture for colocating partitioned durable state with processing tasks and reconstructing that state from a log after reassignment.

- **C1:** A task's local store is backed by a changelog, allowing a replacement task to reconstruct the state after failure or movement. Partition isolation and the relationship between input partitioning and local state are central correctness constraints. See the [state-management documentation](https://samza.apache.org/learn/documentation/0.7.0/container/state-management.html).
- **C2:** The `StorageEngine` boundary separates a store's data structures and query operations from the framework's changelog-based fault tolerance. This supports stateful applications without prescribing one application-level indexing structure.
- **C3:** Local disk-backed access avoids a remote request for each state operation and permits state that exceeds available memory. The [architecture discussion](https://samza.apache.org/learn/documentation/0.7.0/container/state-management.html) explains both the locality benefits and the resulting partitioning constraints.

The inspected architecture reference is version **0.7.0**. It supports these design lessons, but should not be used to infer current storage defaults or current operational compatibility.

### [hazelcast/hazelcast](https://github.com/hazelcast/hazelcast)

**Language/role:** Java; Hazelcast's integrated **Jet stream-processing engine**.

Jet belongs in this monorepo: the [former standalone repository](https://github.com/hazelcast/hazelcast-jet) documents its integration into Hazelcast 5. It is not counted again as an independent engine.

- **C1:** Consistent snapshots, input-barrier handling, and source acknowledgements have to agree on which records are covered by recovery. The [Hazelcast 5.7 fault-tolerance documentation](https://docs.hazelcast.com/hazelcast/5.7/fault-tolerance/fault-tolerance) describes snapshot replication and the source/sink obligations that make particular guarantees possible.
- **C2:** Processors save and restore application-specific state through the snapshot mechanism, while connectors implement different recovery strategies. Transactional sinks coordinate commit with snapshots; idempotent sinks require a different completion discipline. This is a useful separation of runtime consistency from connector semantics.

Study the [fault-tolerance contracts](https://docs.hazelcast.com/hazelcast/5.7/fault-tolerance/fault-tolerance) before generalizing the guarantees: replicated in-cluster snapshots and durable recovery after losing an entire cluster are distinct concerns. An external sink's behavior remains part of the correctness argument.

## Kafka-centric application engines

### [apache/kafka](https://github.com/apache/kafka)

**Language/role:** Java; specifically **Kafka Streams**, not the broker by itself.

Kafka Streams makes a useful contrast with centrally managed processing clusters: an application library owns tasks, local stores, and recovery while Kafka provides partitioned input and durable changelogs.

- **C1:** When a task moves, its state store must be restored from its changelog before processing resumes. The relationship between partition assignment, local state, and restoration is explicit in the [Kafka Streams 3.3 architecture](https://kafka.apache.org/33/streams/architecture/).
- **C2:** The DSL and Processor API share tasks and state stores. Joins, aggregations, windowed computation, and custom processors use a common stateful execution substrate rather than unrelated persistence mechanisms.
- **C3:** Local stores keep routine state operations near processing, while standby replicas reduce the restoration work on reassignment. The [architecture guide](https://kafka.apache.org/33/streams/architecture/) explains this locality-versus-recovery tradeoff.

The cited guide is versioned. The evidence supports the architectural model, not an assertion that every configuration or external side effect receives the same delivery guarantee.

### [quixio/quix-streams](https://github.com/quixio/quix-streams)

**Language/role:** Python; Kafka-oriented StreamingDataFrame engine with local persistent state.

Quix Streams is useful for examining the boundary between a familiar dataframe API and the less familiar recovery lifecycle beneath stateful operations.

- **C1:** State changes, changelog production, checkpoint completion, and source-offset recovery must remain coordinated. Restoration happens before normal processing, and changelog retention can determine whether a lost local store is recoverable. These are concrete failure modes in the [stateful-processing guide](https://quix.io/docs/quix-streams/advanced/stateful-processing.html).
- **C2:** Stateful functions and window operations operate on state scoped to a Kafka partition and key. The dataframe API exposes state access without requiring each application to implement the RocksDB and changelog machinery itself. See the [state API and lifecycle](https://quix.io/docs/quix-streams/advanced/stateful-processing.html).

Study key isolation and checkpoint ordering together: an expressive application API still has to prevent one key's state access from accidentally crossing the partitioned execution model. This selection does not infer a blanket exactly-once guarantee for arbitrary Python side effects.

### [faust-streaming/faust](https://github.com/faust-streaming/faust)

**Language/role:** Python/asyncio; a substantively evolved **community fork** of Faust.

The original Robinhood repository is not counted separately. This fork has its own continuing compatibility and recovery work, making it more than a duplicate source snapshot.

- **C1:** Table changelogs only reflect mutations made through the proper table operations. Mutating a referenced object without assigning it back can bypass logging; incorrect stream/table co-partitioning can likewise make local results invalid. The [tables guide](https://faust-streaming.github.io/faust/userguide/tables.html) explains these application-visible invariants.
- **C2:** Asynchronous agents, partitioned tables, windowed tables, and explicit repartitioning support different stateful workflows through one programming model. The [table API](https://faust-streaming.github.io/faust/userguide/tables.html) is a productive entry point.
- **C4:** The [changelog](https://github.com/faust-streaming/faust/blob/master/CHANGELOG.md) records recovery/rebalance and concurrency fixes across earlier releases, then Python 3.13/3.14 compatibility and expanded live-Kafka testing in 2026. That combination demonstrates evolution plus compatibility and testing work, rather than merely an old creation date.

### [lovoo/goka](https://github.com/lovoo/goka)

**Language/role:** Go; application library for Kafka-based stateful stream processing.

Goka combines processors, partitioned group tables, lookup views, and emitters. The repository documents **at-least-once** processing; its appeal here is the explicit implementation of recovery and task lifecycle.

- **C1:** The [partition processor](https://github.com/lovoo/goka/blob/master/partition_processor.go) coordinates table recovery, joined tables, message processing, cancellation, and shutdown. Active, passive, and recovery-only behavior share machinery, so the transition into processing is a substantive correctness boundary.
- **C2:** Application processors and lookup views use the same partitioned table model, while storage is abstracted from processor orchestration. The [processor source](https://github.com/lovoo/goka/blob/master/partition_processor.go) makes those interfaces and lifecycle dependencies concrete.

This is a particularly approachable codebase for studying why local state cannot simply be opened and used immediately after a rebalance. Recovery readiness and errors from concurrent components must be incorporated into the processor's state machine.

### [LGouellec/streamiz](https://github.com/LGouellec/streamiz)

**Language/role:** C#/.NET; Streamiz Kafka Streams, an independent implementation inspired by Kafka Streams.

Streamiz is worth comparing with the Java engine as an implementation of similar stream/table concepts in a different runtime, rather than as a generated language binding.

- **C1:** Its [processor state manager](https://github.com/LGouellec/streamiz/blob/develop/core/Processors/Internal/ProcessorStateManager.cs) tracks store-specific changelog partitions, restoration callbacks, and checkpoint offsets. It distinguishes persistent, in-memory, and unlogged stores instead of assuming every store follows an identical recovery path.
- **C2:** The stream/table DSL is supported by reusable state-store, changelog-registration, and offset-checkpoint interfaces. The [state-manager implementation](https://github.com/LGouellec/streamiz/blob/develop/core/Processors/Internal/ProcessorStateManager.cs) is a focused entry point into how those abstractions cooperate.

Study registration and offset bookkeeping before assuming feature parity with Java Kafka Streams. The repository's own feature comparison is useful context, but the criteria here rest on the implemented state lifecycle rather than similarity of product names.

## Streaming SQL and incremental dataflow

### [risingwavelabs/risingwave](https://github.com/risingwavelabs/risingwave)

**Language/role:** Rust; streaming SQL engine with continuously maintained materialized views.

RisingWave exposes the tension between low-latency operator-local updates and durable state shared through an object-storage-oriented architecture.

- **C1:** Its [state-management architecture article](https://risingwave.com/blog/state-management-for-cloud-native-streaming-getting-to-the-core/) describes epochs, aligned barriers, and a durability boundary that requires state uploads and metadata registration to complete. Reads must reconcile multiple locations holding updates from different stages of this process.
- **C2:** Epoch-aware state operations such as lookup, iteration, and batched ingestion let multiple stateful relational operators share a storage substrate.
- **C3:** Operator-local state, a shared buffer, and remote persistent state separate the hot processing path from bulk persistence. This makes caching and asynchronous transfer understandable parts of the consistency model, rather than independent performance tricks. See the [same architecture account](https://risingwave.com/blog/state-management-for-cloud-native-streaming-getting-to-the-core/).

The detailed reference is a **2022 design account**. It establishes the architectural problem and mechanisms studied here; individual components should be checked against current source before treating that account as today's exact implementation.

### [MaterializeInc/materialize](https://github.com/MaterializeInc/materialize)

**Language/role:** Rust; incremental streaming SQL with storage, compute, and adapter layers.

Materialize is especially valuable for engineers interested in the semantics of continually changing relational results and the limits that compaction imposes on historical reads.

- **C1:** The [platform formalism](https://github.com/MaterializeInc/materialize/blob/main/doc/developer/platform/formalism.md) models updates with data, logical time, and multiplicity differences. Read validity depends on progress and compaction frontiers; read capabilities constrain how far state can be compacted. These are explicit invariants, not just a feature list.
- **C2:** The same formalism separates timestamped collections and the responsibilities of storage, compute, and adapters. This provides reusable contracts for managing dataflows and retaining enough information for their consumers.

Read the [formal model](https://github.com/MaterializeInc/materialize/blob/main/doc/developer/platform/formalism.md) as a map for investigating the monorepo. It expressly describes intended behavior rather than promising an exact description of every current implementation detail. Inclusion here concerns the available engineering material and does not imply that all repository components have identical licensing terms.

### [feldera/feldera](https://github.com/feldera/feldera)

**Language/role:** Rust execution engine and Java SQL compiler; the **DBSP** subsystem and its integration into Feldera.

Feldera is a strong choice for studying incremental computation as an algebraic execution model and then examining the testing required to make SQL implementations match that model.

- **C1:** The team's [correctness discussion](https://www.feldera.com/blog/correctness-at-feldera) describes comparisons against other SQL engines, incremental-versus-batch checks, and crash-versus-uninterrupted executions. It also addresses numeric behavior and casts, where mathematical identities alone do not settle SQL implementation semantics.
- **C2:** DBSP composes stateful delay, lifting, and fixed-point mechanisms to build incremental computations. The [DBSP source subtree](https://github.com/feldera/feldera/tree/main/crates/dbsp), including its tests and benchmarks, is the implementation entry point.

The correctness article distinguishes mathematical foundations from implementation testing. Its discussion of machine-checked theory should not be read as a claim that the entire production engine is formally verified. This monorepo counts once, rather than counting the compiler and DBSP runtime as independent repositories.

### [ArroyoSystems/arroyo](https://github.com/ArroyoSystems/arroyo)

**Language/role:** Rust; distributed SQL stream-processing engine.

Arroyo offers a relatively direct path from SQL operators to a partitioned execution graph and the checkpointing required by windows and joins.

- **C1:** The [concepts documentation](https://doc.arroyo.dev/concepts/) relates event-time watermarks, late-data handling, barrier snapshots, operator state, and source positions. Saving a Kafka offset without its corresponding operator state would not provide a consistent recovery boundary.
- **C2:** SQL is compiled into a graph whose operators are divided into parallel subtasks. Key-space partitioning and reusable window/join operators allow different queries to use the same distributed execution and state-management machinery. See the [execution concepts](https://doc.arroyo.dev/concepts/).

A useful reading exercise is to trace one keyed window from query plan through watermark advancement and checkpoint recovery. The inspected documentation describes its checkpoint storage representation; treat storage details and state-size assumptions as version-dependent rather than universal constraints of the architecture.

### [TimelyDataflow/differential-dataflow](https://github.com/TimelyDataflow/differential-dataflow)

**Language/role:** Rust; reusable incremental dataflow engine/library built on Timely Dataflow.

This is an engine component rather than a turnkey durable streaming service. It qualifies through substantial stateful incremental execution, including changing inputs, joins, reductions, and iterative computations.

- **C1:** The [trace module](https://docs.rs/differential-dataflow/latest/differential_dataflow/trace/) stores changes indexed by key, value, logical time, and difference. Queries accumulate changes according to the time partial order, so retention and compaction must preserve the answers still available to consumers.
- **C2:** Trace interfaces separate operators from particular indexing representations. Immutable batches, cursors, builders, and mergers provide a reusable vocabulary for managing incremental state.
- **C3:** Indexed arrangements and incremental merging organize work around changed records and reusable state. The [trace documentation](https://docs.rs/differential-dataflow/latest/differential_dataflow/trace/) exposes the machinery behind that approach without requiring benchmark claims.

It is retained separately from systems that use related technology because this repository implements a general-purpose library with its own interfaces. Timely itself is not counted again in this report.

## Embedded, edge, and specialized runtimes

### [bytewax/bytewax](https://github.com/bytewax/bytewax)

**Language/role:** Python dataflow API over a Rust runtime.

The repository states that Bytewax became **community-maintained in May 2025**, when the company was no longer commercially viable and the original core team stepped back from daily maintenance. That status matters when assessing support.

- **C1:** Recovery combines operator snapshots and progress stored across partitioned SQLite recovery files. A restart must select a consistent snapshot across those partitions; preserving overlapping snapshots also matters for staggered backups. See the [recovery design](https://github.com/bytewax/bytewax/blob/main/docs/guide/concepts/recovery.md).
- **C2:** Stateful dataflow operators use a common recovery mechanism, including when the number of workers changes. The [recovery example](https://github.com/bytewax/bytewax/blob/main/docs/guide/getting-started/recovery-example.md) connects application state updates to that runtime behavior.

This is useful for studying durable state beneath a compact Python API. Recovery of internal computation and delivery to external outputs are separate contracts; replay can still require idempotent outputs or application-level deduplication.

### [lf-edge/ekuiper](https://github.com/lf-edge/ekuiper)

**Language/role:** Go; edge-oriented SQL/rule stream-processing engine.

eKuiper broadens the selection beyond large server clusters. Its rules maintain windows and extension-defined state under the resource constraints of edge deployments.

- **C1:** The [state and fault-tolerance guide](https://github.com/lf-edge/ekuiper/blob/master/docs/en_US/guide/rules/state_and_fault_tolerance.md) ties checkpointed state to rewindable input. It explicitly separates an exactly-once guarantee for managed state from sink behavior that may duplicate outputs and require deduplication.
- **C2:** The runtime manages internal operator state, such as windows, and exposes a stream-context mechanism for extensions to participate in state handling. That gives custom processing logic a shared persistence contract rather than leaving every extension to invent its own recovery protocol. See the [state-extension documentation](https://github.com/lf-edge/ekuiper/blob/master/docs/en_US/guide/rules/state_and_fault_tolerance.md).

The instructive aspect is the narrowness of the guarantee: a configurable quality-of-service label still has to be interpreted in terms of which state and side effects the engine actually controls.

### [siddhi-io/siddhi](https://github.com/siddhi-io/siddhi)

**Language/role:** Java; stream processing and complex-event processing engine.

Siddhi provides a useful view of state through event lifecycles, patterns, windows, and incremental aggregates, rather than focusing only on checkpoint storage.

- **C1:** In the [architecture guide](https://siddhi.io/en/next/development/architecture/), windows must account for current events through corresponding expiration or reset behavior. Downstream selectors update aggregates for insertion, expiration, and reset; missing a lifecycle event would corrupt retained results.
- **C2:** The compiler translates the SQL-like language into query objects and then executable runtimes. Extensible window and stream processors, partitions, joins, and pattern/sequence machinery reuse that compilation and execution structure. See the [processor architecture](https://siddhi.io/en/next/development/architecture/).

The inspected guide describes the **5.2 architecture**. It is a productive starting point for following one event through a window and aggregate, with clear invariants connecting otherwise separate operators. No general deployment-maintenance claim is inferred from this design material.

### [ParaGroup/WindFlow](https://github.com/ParaGroup/WindFlow)

**Language/role:** C++17; header-only stream-processing runtime for multicore CPUs and GPUs.

WindFlow is included for substantial **single-node parallel stateful processing**, not as evidence of a finished distributed checkpointing system. Its repository includes persistent operators, windows, and graph composition.

- **C2:** `MultiPipe` and `PipeGraph` compose operators and user functions into processing graphs. Windowing and operator variants reuse this structure rather than requiring a separate runtime per workload. See the [project documentation](https://paragroup.github.io/WindFlow/).
- **C3:** Its execution architecture builds on FastFlow and lock-free single-producer/single-consumer communication queues, with distinct CPU/GPU execution concerns. The [architecture overview](https://paragroup.github.io/WindFlow/) connects the programming abstractions to the shared-memory scheduling substrate.

This is a useful complement to Java and Rust distributed systems when studying data movement, operator parallelism, and heterogeneous hardware. The documentation describes distributed support as work in progress; that prospective capability is not used as evidence for inclusion.

### [microsoft/Trill](https://github.com/microsoft/Trill)

**Language/role:** C#/.NET; temporal, primarily single-node streaming query engine.

Trill is a research-oriented reading choice with a published execution model. The repository is not archived, but the checked metadata's latest push was in January 2024; this report does not establish present operational support.

- **C1:** The [Trill paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/trill-vldb2015.pdf) defines temporal records and explains how batching must preserve the results of event-at-a-time processing. Punctuation and temporal progress affect when results can be emitted.
- **C3:** Columnar batches and generated code reduce per-record overhead without changing the query abstraction. The [equi-join implementation](https://github.com/microsoft/Trill/blob/master/Sources/Core/Microsoft.StreamProcessing/Operators/EquiJoin/EquiJoinStreamable.cs) selects specialized implementations from stream properties, including partitioning and interval structure, with generated and row-based execution paths.

Study that specialization logic alongside the temporal model: it shows the conditions under which a faster join implementation is valid. The paper's benchmark numbers are not reproduced or treated as a current comparison with other engines.

### [deib-polimi/renoir](https://github.com/deib-polimi/renoir)

**Language/role:** Rust; distributed dataflow research platform with stateful window operators.

Renoir provides readable implementation material for event-time windows and network batching. Its inclusion does not assert production-grade durable recovery; the inspected evidence is narrower.

- **C1:** The [event-time window implementation](https://github.com/deib-polimi/renoir/blob/master/src/operator/window/descr/event_time.rs) checks watermark ordering, validates window parameters, finalizes windows on progress, and handles stream termination and restart markers. Tests exercise ordinary and sparse arrivals.
- **C2:** Window descriptions, managers, and accumulators separate time/window policy from the aggregate being computed. These interfaces support multiple window behaviors through common operator machinery.
- **C3:** The [batcher](https://github.com/deib-polimi/renoir/blob/master/src/block/batcher.rs) exposes fixed, adaptive, timed, and single-message modes. Its handling of pending buffers and network backpressure makes the throughput/latency tradeoff visible in code.

The source is especially useful for comparing arrival-triggered batching with timer-driven flushing, and for seeing how those choices interact with progress and termination rather than only with steady-state throughput.

## Alternative coordination and state models

### [numaproj/numaflow](https://github.com/numaproj/numaflow)

**Language/role:** Rust/Go; Kubernetes-native data processing, specifically the **Reduce and Accumulator** stateful subsystems.

Numaflow is relevant through its window and accumulator execution contracts, not merely because it orchestrates containerized functions.

- **C1:** Accumulator data is retained in a write-ahead log and replayed after a pod restart. Watermark progress and an explicit end-of-window exchange with the user-defined function determine completion and log cleanup. Stalled progress can retain unbounded state. See the [accumulator protocol](https://numaflow.numaproj.io/user-guide/user-defined-functions/reduce/windowing/accumulator/).
- **C2:** Fixed, sliding, session, and accumulator windows share keyed/non-keyed processing concepts. The [windowing guide](https://numaflow.numaproj.io/user-guide/user-defined-functions/reduce/windowing/windowing/) explains how window identity and user keys organize state and partition work.

Study the function/runtime boundary: a function's returned output is not the only signal required to release durable state. Keyed partitioning also has different scaling implications from a single non-keyed reduction; broad Kubernetes autoscaling claims would obscure that distinction.

### [apache/geaflow](https://github.com/apache/geaflow)

**Language/role:** Java; Apache **Incubating** streaming graph-computing engine.

GeaFlow extends the category beyond scalar keyed aggregates to changing graph state and iterative graph computation, while also supporting stream and batch execution.

- **C1:** The [state design](https://geaflow.apache.org/docs/concepts/state_principle/) couples checkpointed state with source offsets, partitions state through key groups, and distinguishes local state from distributed persistence. Dynamic graph state also has to represent changing vertices and edges across versions.
- **C2:** Graph state and key/value, list, and map state use explicit storage interfaces. Separately, the [framework design](https://geaflow.apache.org/docs/concepts/framework_principle/) maps logical processing graphs to physical execution and uses a cycle scheduler for streaming windows and iterative computation.
- **C3:** The state interfaces expose a real representation tradeoff: a store that supports sub-key operations can avoid rewriting an entire composite value on each update. This gives a concrete reason to separate logical state abstractions from backing-store capabilities.

The canonical ASF repository is counted once; its former organizational lineage is not treated as another independent implementation.

### [onyx-platform/onyx](https://github.com/onyx-platform/onyx)

**Language/role:** Clojure; **archived** distributed data-processing engine, retained as a historical architecture study.

Onyx separates its coordination model from the data plane and exposes window aggregation as a reusable state transition protocol.

- **C1:** Its [low-level architecture](https://github.com/onyx-platform/onyx/blob/0.14.x/doc/user-guide/architecture-low-level-design.adoc) uses a totally ordered control log and deterministic replica transitions, with side effects separated from state transitions. Membership changes, barriers, and recovery are part of the same consistency problem.
- **C2:** The [aggregation state-management guide](https://github.com/onyx-platform/onyx/blob/0.14.x/doc/user-guide/aggregation-state-management.adoc) separates initialization, creation of serializable state updates, application of updates, and merging of aggregate state. Windows and triggers participate in checkpointed execution through those interfaces.

This is an instructive combination of functional control-plane design and application-defined aggregation. Its archived status is verified, and its exactly-once state reasoning should not be generalized to arbitrary application side effects. The linked documentation is the repository's `0.14.x` line, not a claim of current product support.

### [WallarooLabs/wally](https://github.com/WallarooLabs/wally)

**Language/role:** Pony runtime with application APIs; distributed stateful stream processor formerly named **Wallaroo**.

The former Wallaroo repository resolves to this canonical Wally repository. The retained documentation still uses the old name. It is one codebase, not two projects, and the inspected metadata does not mark it archived.

- **C1:** The [state model](https://github.com/WallarooLabs/wally/blob/master/documentation/content/core-concepts/working-with-state.md) gives a state object to one computation at a time, serializing its updates. Separately, the [crash-resilience design](https://github.com/WallarooLabs/wally/blob/master/documentation/content/operators-manual/resilience-crash.md) coordinates distributed snapshots, a consistent recovery generation, and input replay.
- **C2:** Domain-specific state objects and state computations separate application update logic from runtime ownership and recovery. Computations consume a message and state and may produce output, giving multiple business computations a common lifecycle.

The resilience document describes support that must be enabled and is disabled by default in that documented configuration. Treat these pages as the historical design lineage and verify present configuration before relying on their recovery behavior; no current support commitment is inferred.

## Coverage, search method, and limitations

Live discovery used more than six distinct query families: distributed checkpointing and keyed state; JVM/Kafka stores; Rust streaming SQL and incremental view maintenance; Python tables/windows; Go edge processing; C++ CPU/GPU runtimes; C# temporal/Kafka engines; Clojure/Pony coordination; event-time research runtimes; Kubernetes accumulators; and streaming graph state. Later queries increasingly returned inspected engines, integration layers, brokers, or small examples, indicating diminishing returns.

Every canonical repository page and at least one additional substantive primary source were opened. Some source files were read through raw-file URLs when GitHub HTML retrieval failed. Earlier API checks confirmed specific status questions; a redundant final API-wide sweep hit the unauthenticated rate limit. Repository-page verification and substantive-source inspection were already complete. This is not a comprehensive maintenance audit.

Exclusions include brokers without stateful execution, connector wrappers, tutorials, generic actor libraries, and ordinary asynchronous iterator libraries. Apache Beam's programming model and overlapping runners were not counted merely for exposing stateful APIs; ksqlDB was omitted to prioritize distinct implementations over another Kafka Streams-based SQL layer. Former repositories, monorepo subsystems, and predecessor forks are not double-counted. Commercial-only engines and projects without a substantive official GitHub implementation or mirror are outside scope.

No candidate code was executed, dependencies installed, repositories cloned, or comparative benchmarks run. Embedded libraries are not implicitly credited with distributed durability. C4 requires inspected longitudinal compatibility/testing evidence; other entries qualify through their stated criteria. Versioned and historical references establish design lessons, while operational fitness requires release-specific evaluation.
