# Incremental computation and dataflow engines

Research date: **2026-10-09**.

This selection covers 24 GitHub repositories implementing demand-driven recomputation, differential and relational change propagation, compiled dataflows, and stateful dataflow execution. It includes small reusable libraries, distributed systems, and historically important research implementations. General task/dataflow runtimes are identified separately: executing dependency graphs does not necessarily provide automatic incremental view maintenance. In monorepos, the relevant subsystem is named explicitly.

The criteria below describe reasons to study the implementation, not a certification of every component or a recommendation to deploy every project. Repository pages and additional primary implementation or design material were inspected for every entry. Stars were not used as quality evidence.

- **C1 — Difficult correctness:** meaningful invariants, concurrency, numerical or temporal semantics, adversarial inputs, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces or execution models supporting multiple applications.
- **C3 — Performance with structure:** concrete resource or execution costs addressed through an understandable architecture.
- **C4 — Sustained evolution:** evidence of evolution over years together with compatibility, testing, or complexity management; age alone is insufficient.

## Demand-driven and self-adjusting computation

### 1. [salsa-rs/salsa](https://github.com/salsa-rs/salsa)

**Rust — memoized, dependency-tracked query framework.** Salsa is a useful starting point for understanding why an incremental cache needs more than a map from arguments to results. Study its distinction between a query being checked in the current revision and its result actually changing.

- **C1:** Memo validity depends on dependency revisions. When reexecution produces an equal result, backdating preserves the earlier change revision, preventing an unchanged intermediate answer from falsely invalidating its consumers.
- **C2:** Inputs and derived queries provide an application-independent model suitable for compiler and analysis databases.
- **C3:** Durability levels let validation skip whole classes of dependencies that could not have changed, rather than traversing every memo dependency on every revision.

The [algorithm reference](https://salsa-rs.github.io/salsa/reference/algorithm.html) explains revision tracking, verification, backdating, and durability together; it is the best architectural entry point for these claims.

### 2. [janestreet/incremental](https://github.com/janestreet/incremental)

**OCaml — dynamically changing computation graphs with explicit stabilization.** Particularly valuable for engineers studying graph mutation rather than a fixed DAG: `bind` can replace a subgraph while observers determine which computations are necessary.

- **C1:** The implementation documents parent/dependency height ordering, membership of stale necessary nodes in the recomputation heap, and invalidation of nodes created within obsolete `bind` scopes. Adding edges also requires cycle detection.
- **C2:** Variables, observers, maps, binds, and generative functors separate graph instances and allow application-specific computations to share the same engine.
- **C3:** Separate height-adjustment and recomputation heaps preserve execution order while limiting work to necessary nodes; cutoffs suppress downstream propagation when an application-defined equality condition holds.

Start with the unusually detailed [implementation overview in `incremental_intf.ml`](https://github.com/janestreet/incremental/blob/master/src/incremental_intf.ml), which explains invariants, scope lifetimes, stabilization failure behavior, and debug assertions.

### 3. [Adapton/adapton.rust](https://github.com/Adapton/adapton.rust)

**Rust — named, demand-driven self-adjusting computation. Archived research implementation; GitHub marks it archived on September 8, 2026.** Its distinctive subject is preserving computation identity as an application's data and control structure change.

- **C1:** The demanded computation graph tracks observations and dirty/clean transitions. Named cells and thunks make reuse depend on identity across executions, with explicit namespace and cycle-related behavior to understand.
- **C2:** The engine exposes reusable `Art` references, mutable cells, thunks, names, and forcing operations. A naive evaluator and the incremental evaluator implement the same conceptual interface, making semantic comparison possible.
- **C3:** Demand-driven graph cleaning avoids recomputing unobserved branches and attempts to reuse named computations after structural changes.

The [engine documentation](https://docs.rs/adapton/latest/adapton/engine/index.html) describes the calculus, identity choices, forcing, and graph inspection facilities. Treat this as an architectural research reference, not evidence of current maintenance.

### 4. [fsprojects/FSharp.Data.Adaptive](https://github.com/fsprojects/FSharp.Data.Adaptive)

**F# — adaptive values and incrementally maintained sets, maps, and lists.** Study the connection between scalar dependency tracking and collection-level deltas, including use through .NET and Fable.

- **C1:** Transactions mark affected values outdated; later forcing evaluates them. Dynamic dependencies and unchanged intermediate results complicate which consumers actually need reevaluation.
- **C2:** Adaptive scalar and collection interfaces support both ordinary dependency graphs and applications that need fine-grained collection changes.
- **C3:** Its push/pull design combines eager invalidation with lazy computation; collection operators propagate changes rather than requiring full collection replacement. The [implementation explanation](https://fsprojects.github.io/FSharp.Data.Adaptive/) develops this model.
- **C4:** The repository traces the project to Aardvark work beginning in 2013. Its [release notes](https://github.com/fsprojects/FSharp.Data.Adaptive/blob/master/RELEASE_NOTES.md) record subsequent .NET/Fable compatibility work and fixes involving concurrent transactions, callback deadlocks, weak callbacks, and index races—concrete evidence of managing an evolving implementation.

### 5. [wcharczuk/go-incr](https://github.com/wcharczuk/go-incr)

**Go — generic incremental graphs inspired by Jane Street's design.** This is a separate implementation, useful for examining how graph stabilization and dynamic binds fit Go's generics and synchronization model.

- **C1:** Dynamic edge insertion must repair node heights without introducing a cycle or violating recomputation ordering. The height-adjustment implementation explicitly checks cycles and height limits and coordinates its heap state with a mutex.
- **C2:** Generic input, mapping, binding, and observation interfaces allow arbitrary Go values and functions to participate. Equality cutoffs are opt-in, so the framework does not impose a universal equality policy on application values.
- **C3:** Specialized height buckets organize repair and stabilization work; the repository also describes parallel stabilization by height. Its documentation acknowledges that incremental bookkeeping can cost more than recomputation for cheap workloads.

Read the repository's stabilization discussion alongside [`adjust_heights_heap.go`](https://github.com/wcharczuk/go-incr/blob/main/adjust_heights_heap.go).

### 6. [ocurrent/current_incr](https://github.com/ocurrent/current_incr)

**OCaml — compact self-adjusting computation with deterministic resource lifetimes.** A substantive smaller alternative whose central concern is releasing resources when a computation branch becomes unused, rather than waiting for garbage collection.

- **C1:** The core tracks readers on an execution timeline, invalidates obsolete intervals, and runs release callbacks. It prevents input mutation during propagation and restores propagation state even when callbacks raise exceptions.
- **C2:** Modifiable values, reads, writes, release hooks, and a separable collection abstraction support computations with externally meaningful lifetimes. The README also describes Crowbar fuzz testing of generated computations.
- **C3:** A priority queue orders affected reads; the separable map implementation gives elements their own timelines so retained elements need not all be rebuilt after a collection change.

[`lib_incr/modifiable.ml`](https://github.com/ocurrent/current_incr/blob/master/lib_incr/modifiable.ml) contains the timeline, propagation, release, and collection machinery in one navigable implementation.

## Differential dataflow foundations and graph compilation

### 7. [TimelyDataflow/timely-dataflow](https://github.com/TimelyDataflow/timely-dataflow)

**Rust — parallel dataflow runtime with logical timestamps and progress tracking.** Its defining problem is knowing when an operator can safely conclude that no more data for a logical time can arrive, including through nested or cyclic computations.

- **C1:** Capabilities account for permission to produce timestamped output. Connectivity summaries describe how times can advance across an operator, while antichains represent progress under partial orders. Incorrect accounting can cause premature completion or prevent progress.
- **C2:** Operators, scopes, timestamp types, and communication interfaces form a reusable substrate for streaming and iterative computation.
- **C3:** Operators participate in explicit scheduling and progress notifications instead of requiring global rounds for every action; the interface distinguishes local progress from progress requiring worker aggregation.

Read the [progress module](https://docs.rs/timely/latest/timely/progress/index.html) and the [`Operate` contract](https://docs.rs/timely/latest/timely/progress/operate/trait.Operate.html), especially topology initialization and capability creation rules.

### 8. [TimelyDataflow/differential-dataflow](https://github.com/TimelyDataflow/differential-dataflow)

**Rust — incremental collections, relational operators, and iterative computations over Timely.** It adds a change algebra and maintained indexes to the execution substrate, making it a distinct layer worth studying separately.

- **C1:** Collection contents are determined by accumulated differences at times less than or equal to a requested time. Retractions and partially ordered timestamps must retain their meaning through joins, reductions, and iteration.
- **C2:** Collection operators and the separate `Trace`, batch, cursor, builder, and merger interfaces support both application programs and alternative data representations.
- **C3:** Traces organize updates into sorted, consolidated batches. Indexed access and batch merging provide a concrete route from the mathematical model to efficient repeated incremental queries.

The [trace module documentation](https://docs.rs/differential-dataflow/latest/differential_dataflow/trace/index.html) explains the `(key, value, time, difference)` representation and its storage abstractions. The repository's examples connect these primitives to changing relational and graph computations.

### 9. [hydro-project/hydro](https://github.com/hydro-project/hydro)

**Rust — distributed dataflow programming and compilation; relevant subsystems are Hydro's typed API and DFIR.** This monorepo is especially useful for studying the boundary between a declarative graph and generated local execution code.

- **C1:** Hydro distinguishes bounded from asynchronously changing collections and makes nondeterministic operations explicit. Some operators require algebraic obligations such as commutativity; documentation distinguishes written proof claims from Verus-checked proofs. These are meaningful correctness boundaries, not a claim that every user closure is automatically verified. See [safety and correctness](https://hydro.run/docs/hydro/reference/correctness/).
- **C2:** Typed distributed streams and DFIR provide reusable programming and compiler-target layers rather than a single application pipeline.
- **C3:** The documented DFIR design combines scheduled graph regions with compiled pull/push iterator trees to reduce scheduling and buffering overhead.

**Documentation caveat:** The [DFIR architecture page](https://hydro.run/docs/dfir/architecture/) explicitly says that its scheduled subgraphs/handoffs design is being replaced by inline code generation. Read it as an explained design and migration context, not a complete description of the current compiler.

### 10. [MicrosoftResearch/Naiad](https://github.com/MicrosoftResearch/Naiad)

**C# — original timely-dataflow research system. Archived on June 17, 2024; the repository presents an alpha research release.** Include it for the original formulation and its independent implementation, not as another maintained Rust Timely package.

- **C1:** Safe notifications in cyclic graphs require tracking both outstanding events and whether an event at one graph location could generate an earlier event elsewhere. Nested loop timestamps, pointstamps, occurrence counts, and progress frontiers make this a rich correctness study.
- **C2:** Its low-level graph and notification model supports multiple higher-level libraries, including LINQ-style processing and the original differential dataflow work.

The authors' [Naiad SOSP paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2013/11/naiad_sosp2013.pdf), particularly the timestamp, notification, and progress-tracking sections, is the substantive design entry point. Read it alongside the repository's `release_0.5` documentation; that release explicitly warns about limited testing and implementation limitations.

## Incremental relational engines and compiled view maintenance

### 11. [feldera/feldera](https://github.com/feldera/feldera)

**Rust and Java — incremental SQL system; relevant subsystem is the Rust DBSP engine and its SQL compiler integration.** Study how a formal stream-processing model becomes a reusable execution library without letting generated type combinations overwhelm compilation.

- **C2:** DBSP exposes streams, circuits, operators, batches, and traces. The system's SQL layer builds on these abstractions rather than embedding all execution behavior in the parser or planner.
- **C3:** The engine deliberately separates dynamically dispatched internals from strongly typed wrappers. This addresses compilation and monomorphization costs while retaining typed interfaces, and supports both memory-resident and persistent batch/trace representations.
- **C1:** The same layering exposes a concrete safety boundary: dynamically typed operator interfaces require discipline, while static wrappers enforce types for callers. The crate documentation also connects incremental transformations to the DBSP formal model.

Begin with the architectural commentary in [`crates/dbsp/src/lib.rs`](https://github.com/feldera/feldera/blob/main/crates/dbsp/src/lib.rs), which explains these layers and points into their implementations.

### 12. [MaterializeInc/materialize](https://github.com/MaterializeInc/materialize)

**Rust — incremental SQL database; relevant subsystem is compute-plan rendering onto Timely and Differential Dataflow.** Particularly instructive for understanding why database semantics require machinery beyond a generic incremental join library.

- **C1:** SQL evaluation can fail on casts, arithmetic, and other expressions. Compute rendering represents successful rows and errors as separate collections, so an error can itself be retracted when its cause disappears. A final result is valid only when its error collection is empty.
- **C2:** The renderer translates relational plans into reusable dataflow operators, imports, arrangements, indexes, and sinks.
- **C3:** Shared arrangements and demand-aware source projection avoid building every query as an entirely independent pipeline.

[`src/compute/src/render.rs`](https://github.com/MaterializeInc/materialize/blob/main/src/compute/src/render.rs) provides both the architectural explanation and executable construction logic, including the `oks`/`errs` model. This entry concerns that subsystem, not an assertion that the entire database has one uniform design or licensing model.

### 13. [risingwavelabs/risingwave](https://github.com/risingwavelabs/risingwave)

**Rust — distributed streaming SQL and maintained materialized views.** Its actor/executor decomposition and checkpoint protocol make a useful comparison with Timely-based database designs.

- **C2:** Plans are divided into actors containing input merging, chains of relational executors, and output dispatch. This separates local change processing from partitioning and exchange. See the [streaming architecture](https://github.com/risingwavelabs/risingwave/blob/main/docs/dev/src/design/streaming-overview.md).
- **C1:** Checkpoint barriers fan out with data and align at multi-input boundaries. Durable progress requires coordinating compute flushes and metadata commitment; consistent snapshot reads do not by themselves imply immediate read-after-write visibility.
- **C3:** Local shared buffers and asynchronous flushing batch state changes into storage objects, reducing the cost of emitting many small files while retaining a checkpoint boundary.

The [checkpoint design](https://github.com/risingwavelabs/risingwave/blob/main/docs/dev/src/design/checkpoint.md) connects barriers, buffering, recovery, and visibility. Its guarantees should be read at their stated boundaries rather than generalized to arbitrary external sinks.

### 14. [pathwaycom/pathway](https://github.com/pathwaycom/pathway)

**Python and Rust — incremental table-processing engine with a Python programming interface.** The retained subject is the substantial Rust execution implementation, not merely its Python bindings or application examples.

- **C2:** Graph, table, column, and universe handles separate API construction from dataflow execution, allowing relational operations and application pipelines to share an engine. The module boundary is visible in [`src/engine/mod.rs`](https://github.com/pathwaycom/pathway/blob/main/src/engine/mod.rs).
- **C3:** The dataflow implementation keeps specialized integer/pointer/generic representations and lazily materializes conversions. Universe data can cache arranged and consolidated collection forms, avoiding repeated representation work when downstream operators need different views of the same data.

Study [`src/engine/dataflow.rs`](https://github.com/pathwaycom/pathway/blob/main/src/engine/dataflow.rs), especially the value and universe-data representations, to see how a high-level table interface maps onto Timely/Differential collections and traces. These implementation choices support its inclusion without relying on advertised throughput or AI application claims.

### 15. [vmware-archive/differential-datalog](https://github.com/vmware-archive/differential-datalog)

**Haskell compiler and Rust runtime — Differential Datalog (DDlog). Archived on July 13, 2026.** A historical but substantive compiler/runtime example for turning declarative rules into continuously maintained results.

- **C2:** Typed relations, rules, functions, modules, and generated Rust libraries allow embedding a rule-driven incremental computation in other software. The [tutorial](https://github.com/vmware-archive/differential-datalog/blob/master/doc/tutorial/tutorial.md) demonstrates transactional updates and output changes and identifies corresponding test inputs and expected results.
- **C1:** The language distinguishes set and multiset behavior; deleting an input must retract the consequences of rules rather than merely append new answers.
- **C3:** Generated dataflows use arrangements keyed for their consumers. The [profiling guide](https://github.com/vmware-archive/differential-datalog/blob/master/doc/profiling/profiling.md) explains why one logical operation may expand into several physical operators and why arrangement size, peak state, CPU use, and update churn need separate examination.

Treat its archived implementation and documented single-machine/in-memory orientation as scope constraints.

### 16. [dbtoaster/dbtoaster-backend](https://github.com/dbtoaster/dbtoaster-backend)

**Scala compiler backend with generated C++/Scala and other runtime targets — compiled incremental view maintenance.** The repository is the backend of DBToaster's compiler toolchain, not a complete SQL frontend by itself. Its research-oriented documentation includes older toolchain assumptions.

- **C2:** The pipeline separates SQL/calculus processing, M3 trigger programs, backend generation, and native compilation. Generated update handlers can be embedded in application programs. The [architecture overview](https://dbtoaster.github.io/docs_architecture.html) explains the staged compilation boundaries.
- **C3:** Rather than interpret a standing query for each update, the compiler specializes maintenance logic and intermediate state into generated code, with staging and subsequent native compilation providing further optimization opportunities.
- **C1:** Integration must preserve insert/delete semantics; the [custom-adaptor guide](https://dbtoaster.github.io/docs_customadaptors.html) explains event protocols and representing updates as deletion plus insertion.

Read the architecture and adaptor interfaces together to connect query compilation to the runtime contract. No current performance ranking or maintenance claim is inferred from the older documentation.

### 17. [mit-pdos/noria](https://github.com/mit-pdos/noria)

**Rust — research database using partially materialized dataflow.** Retained as a historical research system, with a substantive GitHub implementation. Its value is the interaction between query-driven materialization, replay, and distributed execution domains.

- **C1:** Graph migration and state replay must coexist with ordinary updates. Within a domain, processing one task at a time provides an atomicity boundary for stateful nodes; cross-domain communication and replay require additional coordination.
- **C2:** SQL queries are translated into a graph of reusable relational operators and maintained query results, supporting changing application query sets.
- **C3:** Domain boundaries expose a concrete tradeoff: colocated operators can access state without internal locking, whereas separating domains can require duplicated state or rematerialization. Partial materialization targets the cost of retaining all intermediate results.

The extensive [server implementation overview](https://github.com/mit-pdos/noria/blob/master/server/src/lib.rs) explains domains, channels, state access, migration, and replay messages. It is more informative for architectural study than treating the repository's original performance results as current comparisons.

### 18. [electric-sql/d2ts](https://github.com/electric-sql/d2ts)

**TypeScript — differential dataflow library; relevant monorepo package is `packages/d2ts`.** A smaller implementation in which frontier bookkeeping and incremental relational operators remain relatively easy to inspect together. Its origins include educational differential-dataflow material, but the repository contains a reusable operator library and substantive execution machinery.

- **C1:** The join operator rejects backwards input frontiers and mismatched graphs. It processes one side's delta against the old opposite index, then the other delta against the updated first index, accounting for simultaneous changes without simply applying the same pair contribution twice.
- **C2:** Stream builders and composable operators support application-defined relational pipelines.
- **C3:** Joins maintain indexes rather than recomputing Cartesian combinations from scratch, and compact retained history as the output frontier advances.

Start with the concrete [join implementation](https://github.com/electric-sql/d2ts/blob/main/packages/d2ts/src/operators/join.ts). The inspection supports studying these mechanisms; it does not establish that every exposed join variant has been independently verified.

### 19. [wotbrew/relic](https://github.com/wotbrew/relic)

**Clojure/ClojureScript — immutable in-memory relational data structure with incremental materialized queries.** This brings a persistent functional-data perspective absent from server-oriented SQL systems. The author describes the project as an experiment, and it targets in-memory use cases.

- **C1:** Projection can map several input rows to one output row. Its `transform` node maintains a reverse-support index so deleting one input does not prematurely delete an output still supported by another; the faster unprotected variant documents its stronger precondition.
- **C2:** Queries are ordinary values, with joins, aggregates, constraints, transactions, and change tracking. The public API stores maintenance state alongside the database and requires mutations to pass through its transaction functions.
- **C3:** Materialization exchanges memory and write work for faster repeated reads, using maintained indexes and per-operator insert/delete propagation.

Read the [core dataflow implementation](https://github.com/wotbrew/relic/blob/master/src/com/wotbrew/relic/impl/dataflow.cljc) and the [public API contracts](https://github.com/wotbrew/relic/blob/master/src/com/wotbrew/relic.cljc), particularly `transform`, `transact`, `mat`, and `track-transact`.

## Stateful streaming and general dataflow execution

### 20. [microsoft/Trill](https://github.com/microsoft/Trill)

**C# — in-memory temporal stream-query engine.** Its distinctive contribution for study is connecting precise event lifetimes with generated, batched execution inside a managed runtime.

- **C1:** Intervals, start edges, and end edges encode event lifetimes. Operators preserve ordering requirements on synchronization time, while punctuations and low watermarks communicate progress that enables state cleanup.
- **C2:** Typed `IStreamable` queries and LINQ-style composition separate logical query construction from the physical operator graph instantiated on subscription.
- **C3:** Generated columnar batches, expression transformations, row-based fallbacks, and reference-counted batch pools address per-row overhead and garbage-collection pressure without abandoning a structured operator pipeline.

The primary entry point is the repository's detailed [Trill internals document](https://github.com/microsoft/Trill/blob/master/Documentation/DocSources/TrillInternals.docx), whose text was inspected. It covers temporal representation, logical/physical operators, generated code, and memory management. The repository has research-era build instructions; no present maintenance commitment is inferred from them.

### 21. [apache/flink](https://github.com/apache/flink)

**Java, with Scala components — distributed stateful dataflow engine.** Relevant subjects are runtime state management, keyed operators, and checkpoint/recovery, rather than the entire connector ecosystem. Flink belongs here as a dataflow runtime; not every Flink pipeline is an incremental relational view.

- **C1:** Consistent recovery requires matching source positions with operator state. Multi-input operators normally align checkpoint barriers; recovery also depends on sources being rewindable.
- **C2:** Keyed state, key groups, operator state, and configurable state backends provide reusable mechanisms for many stateful computations and parallelism changes.
- **C3:** Aligned and unaligned checkpoints expose an explicit cost tradeoff: waiting for alignment versus recording in-flight data, with implications for backpressure and checkpoint I/O.

The [stateful stream-processing concepts](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/stateful-stream-processing/) explain this architecture and its constraints. Exactly-once state recovery should not be silently extended to arbitrary external side effects or sinks.

### 22. [bytewax/bytewax](https://github.com/bytewax/bytewax)

**Python and Rust — stateful streaming dataflows on Timely. Community-maintained since May 2025 according to the repository; its original commercial team stepped back.** This lifecycle change matters when choosing an implementation to adopt, but does not remove its architectural value.

- **C2:** Python dataflow descriptions and operator/connector interfaces are compiled into Rust/Timely execution, with Python state logic invoked through PyO3. Composite operators reuse core execution primitives.
- **C1:** Recovery snapshots travel on a separate output and are partitioned into SQLite recovery storage. An epoch becomes resumable only after coordinated worker progress establishes that the necessary snapshots were written; resuming also involves input/output state and replay.
- **C3:** Cooperative operators must yield to the runtime, and epochs participate in both recovery and backpressure. This makes throughput, fairness, and recoverability connected implementation concerns.

The [contributor architecture guide](https://github.com/bytewax/bytewax/blob/main/docs/guide/contributing/architecture.md) explains compilation, scheduling, epochs, snapshot routing, and recovery. Its recovery design is not a blanket guarantee for every connector's external effects.

### 23. [dask/distributed](https://github.com/dask/distributed)

**Python — distributed task/dataflow scheduler.** Its scope is dependency-graph execution, worker state, and failure handling; it does not automatically turn arbitrary Python functions into differential updates.

- **C1:** A task moves among states such as waiting, queued, processing, memory, and erred. Each transition must keep dependency sets, waiting consumers, worker processing sets, and result-location information consistent. Transition handlers produce further recommended transitions, and validation can check invariants.
- **C2:** The same scheduler supports dynamic futures and higher-level collection-generated graphs, decoupling execution from individual application algorithms.
- **C3:** Root-task queuing and worker-saturation policy control how much work is admitted to workers, linking concurrency decisions to memory pressure instead of simply launching every available task.

The [scheduler state-machine documentation](https://distributed.dask.org/en/stable/scheduling-state.html) is a substantive entry point: it enumerates state containers, transitions, recommendations, and their relationships rather than presenting only a user API.

### 24. [uxlfoundation/oneTBB](https://github.com/uxlfoundation/oneTBB)

**C++ — shared-memory parallel runtime; relevant subsystem is Flow Graph.** Counted once, specifically for message-driven graph execution rather than for its unrelated containers and allocator. It complements distributed engines with concurrency inside a process.

- **C1:** Join buffering policies have distinct acceptance and ownership protocols. A reserving join must release already acquired reservations if another input is unavailable; a queueing join removes inputs only after a successor accepts the tuple. See the [join-node specification source](https://github.com/uxlfoundation/oneAPI-spec/blob/main/source/elements/oneTBB/source/flow_graph/join_node_policies.rst).
- **C2:** Generic function, join, buffering, input, and limiter nodes compose into application-specific dataflow and dependency graphs.
- **C3:** Limiter feedback bounds messages admitted to a region. The [limiter guide](https://uxlfoundation.github.io/oneTBB/main/tbb_userguide/use_limiter_node.html) carefully distinguishes admitted objects from an additional object buffered upstream—a useful example of why a concurrency threshold alone is not the entire memory bound.

## Coverage, search method, and limitations

Discovery used live web searches across more than six distinct formulations, followed by opening canonical GitHub pages and reading additional primary sources. Search angles included:

1. General incremental-computation frameworks and dependency-tracked memoization: Salsa, Adapton, and self-adjusting computation.
2. OCaml, F#, and Go graph stabilization, adaptive collections, and explicit resource lifetimes.
3. Timely/differential dataflow, logical progress, recursive computation, and DBSP.
4. SQL incremental view maintenance, DBToaster, Noria, and compiled Datalog.
5. Python/Rust streaming runtimes and distributed task schedulers.
6. TypeScript differential operators and Clojure immutable relational engines.
7. C# temporal/Naiad implementations and C++ shared-memory graph scheduling.
8. Targeted source, architecture, checkpoint, profiling, changelog, and archive-status searches for candidates found through those broader queries.

Later broad queries increasingly returned projects already covered, thin wrappers, tutorials, application-specific pipelines, and workflow orchestrators. Language-specific searches still added distinct architectures, notably Relic and oneTBB. The final list balances established systems with smaller implementations such as `current_incr`, `go-incr`, D2TS, and Relic; the shared Timely lineage is explicit rather than concealed as independent algorithmic invention.

Excluded were awesome-lists, generated integrations, simple teaching ports without comparable reusable machinery, application-only demos, and general workflow schedulers lacking a relevant execution-engine contribution. Build systems, full compilers, reactive UI libraries, and general message brokers were not expanded into adjacent-category surveys. Forks and former repository locations were not counted separately; DBSP is covered within Feldera, and DFIR within Hydro. No retained entry relies on an abandoned GitHub placeholder for an implementation moved elsewhere.

Lifecycle status is stated where primary evidence establishes it: Adapton's Rust implementation, DDlog, and Naiad are archived; Noria and DBToaster are retained for research architecture; Bytewax documents its transition to community maintenance. Absence of an archive label is not treated as proof of active maintenance. Hydro's architecture-document migration warning is preserved explicitly. Some documentation follows moving default branches or `latest`/`stable` versions, so this report is a dated reading guide rather than a commit-pinned audit.

The inspection was read-only and source-based: no candidate code was installed or executed, and no throughput claims were independently benchmarked. Architectural judgments and criterion assignments are grounded interpretations of the linked material. They do not establish production readiness, prove all operator variants correct, or erase the operational differences between an in-memory research library and a distributed database.
