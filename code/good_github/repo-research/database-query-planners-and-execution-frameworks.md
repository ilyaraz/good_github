# Database query planners and execution frameworks

Research date: **2026-10-09**.

Scope: 24 GitHub repositories with substantive implementations of relational planning, query optimization, physical execution, or incremental query evaluation. The selection includes reusable libraries and the relevant subsystems of larger databases; it also includes DataFrame engines where they actually optimize and execute relational plans. Storage engines, SQL clients, parsers without substantial planning, and orchestration systems are outside this report's focus. Each monorepo appears once.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, numerical or SQL semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and representations supporting varied workloads or implementations.
- **C3 — Performance with structure:** concrete execution or planning constraints addressed through an understandable architecture.
- **C4 — Evolution:** documented evolution over years together with compatibility, testing, or complexity management.

The criteria identify engineering material worth studying, not a certification of every component. Statements about what an engineer can learn are grounded judgments based on the linked primary sources. Historical designs and implementation limitations are identified explicitly; inclusion does not itself assert current maintenance activity.

## Reusable planners and execution libraries

### 1. [apache/calcite](https://github.com/apache/calcite)

**Language/role:** Java; extensible SQL validation, relational algebra, optimization, and adapter framework.

Study how a planner can remain independent of storage while accommodating different relational operators, execution conventions, statistics, and cost models. Calcite is especially useful for understanding the boundary between a language frontend and an engine-specific physical implementation.

- **C1:** Rules must preserve query meaning, and the algebra guide makes the precondition for filter pushdown concrete: a predicate can move into an inner-join input only when its column references permit it. Immutable relational expressions and explicit field ordinals provide further invariants to track through rewrites.
- **C2:** `RelBuilder` constructs plans programmatically, while operators, rules, statistics, and costs are extension points. Logical expressions can adopt a physical convention without changing the entire frontend.

**Entry point and evidence:** [Relational algebra and builder guide](https://calcite.apache.org/docs/algebra.html), which includes actual construction examples, field-resolution rules, and convention switching. The repository overview confirms the storage-independent framework and adapter scope.

### 2. [apache/datafusion](https://github.com/apache/datafusion)

**Language/role:** Rust; embeddable SQL/DataFrame planner and Arrow-based execution engine.

Study a library whose customization boundaries extend from data sources through optimizer rules to physical execution. The interesting integration problem is connecting asynchronous I/O to CPU-intensive, partitioned query processing.

- **C2:** `TableProvider`, `OptimizerRule`, and `ExecutionPlan` are explicit integration interfaces. The project explains why extension APIs are preferable to maintaining a heavily modified fork and how executable examples help integrations survive API changes. See the [architecture and extension policy](https://datafusion.apache.org/contributor-guide/architecture.html).
- **C3:** Physical execution uses asynchronous streams and partitioned execution on Tokio. Its [crate architecture documentation](https://docs.rs/datafusion/latest/datafusion/index.html) explains cooperative yielding and why mixing CPU work with latency-sensitive network I/O on one runtime can hurt utilization and tail latency.

These are useful entry points for evaluating an embeddable engine, including the resource-management responsibilities left to its host application.

### 3. [facebookincubator/velox](https://github.com/facebookincubator/velox)

**Language/role:** C++; composable physical execution library accepting already optimized plans.

Study the conversion from plan nodes into pipelines, drivers, and operators, with shared state managed at task scope. Velox's repository explicitly distinguishes its execution role from SQL parsing and optimization.

- **C1:** Parallel hash builders must coordinate before probes proceed. For right/full outer joins, a barrier selects one probe worker to emit unmatched build-side rows after all probing finishes. These are concrete synchronization and duplicate-output hazards.
- **C2:** Custom plan nodes, operators, join bridges, and split handling support integration into multiple host engines. The documentation also states the limits: several exchange and merge facilities are not generic extension points.
- **C3:** Pipelines can use different degrees of parallelism; local exchanges repartition or gather data between them.

**Entry point and evidence:** [What's in the Task?](https://facebookincubator.github.io/velox/develop/task.html), a detailed explanation of ownership, split queues, barriers, bridges, and exchange clients.

### 4. [apache/arrow](https://github.com/apache/arrow)

**Language/role:** C++ within a multilingual monorepo; specifically **Acero**, Arrow's streaming execution subsystem.

Study how batch-level compute kernels become a graph execution engine. This entry concerns Acero, rather than treating the Arrow memory format alone as a query framework.

- **C2:** `Declaration` describes computation, `ExecPlan` owns an execution, and `ExecNode` models sources, transformations, and sinks. File-format and filesystem complexity lives outside the core execution logic.
- **C1:** `ExecBatch` has equal-length columns and a stream-level schema; scalar columns represent repeated values. Plan and node instances have execution state and are not restartable. These contracts matter when implementing operators or adapting foreign batches.
- **C3:** Array/scalar representations avoid materializing constants, and compatible record-batch conversions share buffers.

**Entry point and evidence:** [Acero overview](https://arrow.apache.org/docs/cpp/acero/overview.html). It explicitly states that Acero supplies neither SQL optimization nor distributed coordination and marks internal structures as experimental.

### 5. [dolthub/go-mysql-server](https://github.com/dolthub/go-mysql-server)

**Language/role:** Go; storage-independent MySQL-compatible query engine and server.

Study a SQL engine that can operate over application-supplied storage, with Dolt identified by the repository as a production implementation. Its architecture is more directly reusable than a database whose query layer assumes one internal storage format.

- **C2:** Shared `Node` and `Expression` interfaces, backend implementations, and an engine test harness let integrators supply storage while reusing analysis and execution. Crucially, the harness can test the integrator's own backend.
- **C1:** Analyzer phases have ordering and repetition requirements; individual rules are expected to preserve or increase the degree of name/type resolution. The repository also documents a concrete compatibility trap: its pure-Go regular-expression option differs from the ICU-compatible implementation and does not pass every compatibility test.

**Entry point and evidence:** [Architecture overview](https://raw.githubusercontent.com/dolthub/go-mysql-server/main/ARCHITECTURE.md), covering analyzer rules, plan nodes, execution, and backend test integration; the repository overview supplies the regex compatibility limitation. Some package descriptions in the architecture document are historical, so use it as a conceptual map.

### 6. [cmu-db/optd-original](https://github.com/cmu-db/optd-original)

**Language/role:** Rust; **archived research prototype** of a Cascades optimizer, with a DataFusion bridge. GitHub marks it archived on January 7, 2025; the repository warns against production use.

Study the separation of a generic optimizer from engine-specific representations and the challenges of adaptive optimization. This is the original implementation, not the separate newer `cmu-db/optd` service, which is not counted here.

- **C2:** The repository separates `optd-core`, DataFusion representations, the bridge, planner tests, and cardinality/performance tooling. It accepts user-defined rules and cost models instead of hardwiring one complete database.
- **C3:** Runtime feedback and cardinality estimation connect plan search to observed execution. The [physical-property design discussion](https://github.com/cmu-db/optd-original/issues/123) explains why choosing a cheapest memo-group expression is insufficient when ordering requirements and enforcement costs differ.

**Entry points:** [Core framework directory](https://github.com/cmu-db/optd-original/tree/main/optd-core) and the linked design discussion. The latter is an open proposal describing unresolved work, not evidence that every proposed physical-property mechanism was completed.

## Embedded, vectorized, and compiled engine implementations

### 7. [postgres/postgres](https://github.com/postgres/postgres)

**Language/role:** C; PostgreSQL's optimizer and executor. **Official GitHub mirror** of development hosted elsewhere; the repository explicitly says GitHub pull requests are not its contribution workflow.

Study an optimizer that distinguishes lightweight candidate `Path` trees from executable `Plan` trees and stores alternatives for each `RelOptInfo`. It is a strong reference for understanding why relational identities need detailed applicability conditions.

- **C1:** The optimizer documentation derives legal outer-join reorderings, including strictness conditions on predicates, and describes `join_is_legal` checks for outer, semi-, and anti-join constraints. Incorrect equivalence reasoning would change results.
- **C3:** Dynamic programming builds smaller join relations before larger ones, permitting safe pruning and memory reclamation. Alternatives retain useful ordering and parameterization properties; GEQO supplies a different search strategy for large join spaces.

**Entry point and evidence:** [Optimizer implementation README](https://raw.githubusercontent.com/postgres/postgres/master/src/backend/optimizer/README). Read its “Paths and Join Pairs,” join construction, and outer-join sections before following individual optimization passes.

### 8. [sqlite/sqlite](https://github.com/sqlite/sqlite)

**Language/role:** C, with Tcl testing; embedded planner and VDBE execution. **Official Git mirror**; upstream development uses Fossil.

Study query optimization under the constraints of an embedded library, where planning cost and predictable deployed behavior both matter.

- **C1:** Moving outer-join `ON` constraints into the common predicate representation requires provenance tags in the AST. The [optimizer overview](https://sqlite.org/optoverview.html) also explains affinity and collation conditions that restrict apparently simple index optimizations.
- **C3:** The N3 join-order search retains a bounded set of promising paths; the documented star-query failure mode explains how locally cheap dimension scans can crowd out a better global plan.
- **C4:** The [NGQP history and stability guide](https://sqlite.org/queryplanner-ng.html) connects the 2013 planner rewrite with later regression management, the conditional Query Planner Stability Guarantee, and the 2025 star-query heuristic revision and regression test.

Those two guides are the entry points; the mirror's source map identifies the `where*` planner files and `vdbe.c` executor.

### 9. [duckdb/duckdb](https://github.com/duckdb/duckdb)

**Language/role:** C++; embedded analytical database, focusing on planning and vectorized execution.

Study the relationship between semantic binding, logical optimization, physical operators, and an execution representation that can preserve compressed values.

- **C2:** The [internals overview](https://duckdb.org/docs/current/internals/overview) separates parser representations from catalog-aware binding and subsequent planning. The execution layer has reusable `Vector` and `DataChunk` containers.
- **C3:** Flat, constant, dictionary, and sequence vectors represent the same logical data in different physical forms. `UnifiedVectorFormat` gives generic operators a common view, avoiding a combinatorial explosion of specialized functions while retaining specialized fast paths. Dictionary vectors can preserve compression during execution.

**Second entry point and implementation evidence:** [Execution format](https://duckdb.org/docs/current/internals/vector), including selection vectors, nested types, and short-string representation. This is particularly useful for studying the tradeoff between general operator code and encoding-aware execution.

### 10. [ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse)

**Language/role:** C++; analytical DBMS, specifically column execution, query pipelines, and aggregation.

Study how a column representation, processor graph, storage interface, and aggregate-state API work together. The architecture documentation is unusually candid about where abstractions deliberately expose layout details for efficiency.

- **C2:** `IColumn`, `IDataType`, `IStorage`, processors, and `QueryPipeline` separate data layout, serialization, data access, and execution. Pipelines support pulling results, pushing inserts, and connected `INSERT SELECT` processing.
- **C3:** Operators work on columns; specialized routines access concrete layouts to avoid per-value boxing. Parallel processors compose into executable pipelines.
- **C1:** Aggregate states have ownership and destruction-order requirements, may allocate additional memory, and can be serialized for distributed execution or spilling. Persisted aggregate states also create compatibility obligations.

**Entry point and evidence:** [Architecture overview](https://clickhouse.com/docs/resources/develop-contribute/introduction/architecture). Focus on columns, tables, interpreters, and aggregate functions; specific analyzer details are version-sensitive.

### 11. [pola-rs/polars](https://github.com/pola-rs/polars)

**Language/role:** Rust with Python bindings; relational DataFrame optimizer and execution engine.

Study how a composable expression API produces plans that can be inspected independently of execution. This qualifies through its optimizer and execution machinery, not merely because it exposes a DataFrame API.

- **C2:** Lazy queries have unoptimized and optimized representations, and the public inspection tools expose logical and streaming physical plans. The [query-plan guide](https://docs.pola.rs/user-guide/lazy/query-plan/) traces a concrete filter from an explicit operator into the scan.
- **C3:** Predicate, projection, and slice pushdown reduce work at the source; common-subplan elimination shares scans; join ordering reduces memory pressure. The [optimization guide](https://docs.pola.rs/user-guide/lazy/optimizations/) distinguishes one-time passes from fixed-point simplification/type coercion and runtime-dependent cardinality estimation.

These two guides are good entry points for comparing a relational compiler for programmatic expressions with a conventional SQL optimizer.

### 12. [hyrise/hyrise](https://github.com/hyrise/hyrise)

**Language/role:** C++; research in-memory relational database, focusing on its SQL pipeline and optimizer.

Study a research platform with explicit intermediate representations and practical benchmark support. The repository identifies the current codebase as a rewrite of the earlier Hyrise; the archived predecessor is not counted separately.

- **C2:** The [SQL pipeline documentation](https://github.com/hyrise/hyrise/wiki/SQL) separates parsing, AST-to-logical-plan translation, optimization, and logical-to-physical translation. Logical plans are DAGs rather than a mandate for one execution algorithm.
- **C3:** Statistics and costs guide predicate ordering and scan selection; physical translation can select hash, sort-merge, or nested-loop join implementations. This makes it useful for experiments that change one planning or execution choice while keeping the surrounding system intact.

**Entry point:** The linked SQL wiki, read alongside the repository's benchmark and testing overview. The wiki page is dated 2020: it establishes the architecture and study path, not an exhaustive inventory of current algorithms.

### 13. [heavyai/heavydb](https://github.com/heavyai/heavydb)

**Language/role:** Primarily C++; CPU/GPU relational execution with LLVM query compilation. Former names include MapD and OmniSciDB.

Study compiled query execution across heterogeneous processors: expression translation, generated row/query functions, runtime helper functions, device-specific native code, and code caching.

- **C1:** Generated aggregate code must honor null sentinels rather than treating every machine integer as a SQL value. The documentation shows this concern in a concrete sum helper and describes a scalar code-generator variant used for isolated testing.
- **C3:** LLVM IR is optimized for the target device; GPU compilation proceeds through PTX to device machine code. A bounded code cache addresses compilation reuse and memory consumption.

**Entry point and evidence:** [Code-generation architecture](https://heavyai.github.io/heavydb/execution/codegen.html). This official documentation identifies itself as **OmniSciDB 6.0.0dev**, so its exact backend APIs are historical. The current repository still establishes the CPU/GPU JIT-engine scope; no claim is made that all older implementation details remain unchanged.

## Distributed SQL planning and execution

### 14. [apache/spark](https://github.com/apache/spark)

**Language/role:** Primarily Scala/Java for this subsystem; **Spark SQL, Catalyst, and adaptive query execution**, within the wider Spark monorepo.

Study how optimization continues after distributed execution has produced useful statistics. This entry focuses on SQL plans and relational execution, rather than Spark's entire general-purpose analytics surface.

- **C3:** Adaptive query execution can coalesce shuffle partitions, split skewed partitions, and replace a sort-merge join with a broadcast or shuffled hash join. These mechanisms address task overhead, memory constraints, sorting, and network traffic rather than a single universal execution strategy.
- **C2:** Adaptive rules and cost evaluation are configurable extension boundaries. Storage Partition Join uses partitioning information supplied by compatible DataSource V2 implementations to avoid exchanges, connecting an abstract data-source contract to physical planning.

**Entry point and evidence:** [SQL performance-tuning guide](https://spark.apache.org/docs/latest/sql-performance-tuning.html), especially adaptive execution, customization, and storage-partition joins. Its before/after plans make the effects of physical-property information inspectable.

### 15. [trinodb/trino](https://github.com/trinodb/trino)

**Language/role:** Java; distributed SQL planning and execution across heterogeneous data sources.

Study a clearly named hierarchy of stages, tasks, drivers, operators, splits, and exchanges, alongside the additional mechanisms needed to retry distributed work.

- **C2:** Connector SPI implementations expose different sources through a common model. Stages describe the plan, tasks instantiate it on workers, drivers sequence operators, and exchanges move intermediate results. See [execution concepts](https://trino.io/docs/current/overview/concepts.html).
- **C1:** Fault-tolerant execution distinguishes query retries from task retries and depends on connector support. Intermediate exchange data is spooled for reuse after worker failure; parse errors are not retried. These constraints prevent interpreting “retry” as a universally safe operation.
- **C3:** Recovery introduces explicit buffering, storage, and I/O tradeoffs instead of retaining all intermediate data in memory.

**Second entry point:** [Fault-tolerant execution](https://trino.io/docs/current/admin/fault-tolerant-execution.html). Trino is the independently evolved PrestoSQL lineage; PrestoDB is not duplicated in this selection.

### 16. [apache/impala](https://github.com/apache/impala)

**Language/role:** Java planning and C++ execution; distributed analytical SQL engine.

Study an execution API that separates plan information from per-instance runtime state and makes lifecycle obligations explicit. It provides a useful contrast to fully vectorized Rust libraries and JVM-only distributed executors.

- **C1:** Execution subclasses must check cancellation, initialize children in a defined order, release resources, and reject corrupted serialized plans. Ownership, deep-copy requirements, and the distinction between shared plan state and runtime state are visible at the API boundary.
- **C2:** `PlanNode` and `ExecNode` supply common contracts for many relational operators and multiple fragment instances.
- **C3:** Plan nodes expose LLVM code generation and fragment parallelism without putting every operator behind a separate bespoke execution mechanism.

**Entry points and evidence:** [Execution-node interface](https://raw.githubusercontent.com/apache/impala/master/be/src/exec/exec-node.h) and [component architecture](https://impala.apache.org/docs/build/html/topics/impala_components.html), which explains coordinators, executors, catalog distribution, and membership failure handling.

### 17. [apache/drill](https://github.com/apache/drill)

**Language/role:** Primarily Java; distributed MPP query layer for structured and self-describing data.

Study the transition from a relational plan to a parallel execution topology. Drill is useful for seeing how plan fragments and execution instances differ, including the consequences of an optimistic concurrency model.

- **C2:** Logical and physical plans are distinct; the Foreman's parallelizer creates major fragments separated by exchanges and minor fragments containing relational operators. A serialized physical plan can also be inspected and submitted independently of SQL.
- **C3:** Minor fragments execute in threads and are scheduled with data locality where possible. The documented planner assumes concurrent execution of fragments, connecting available parallelism directly to feasible execution plans.

**Entry point and evidence:** [Drill query execution](https://drill.apache.org/docs/drill-query-execution/). The repository confirms its MPP and self-describing-data scope; the guide supplies the concrete fragmentation, scheduling, and exchange model.

### 18. [pingcap/tidb](https://github.com/pingcap/tidb)

**Language/role:** Go; TiDB SQL planning and execution, particularly cost-based physical planning.

Study how required ordering, estimated cardinality, and execution location influence plan selection. The useful subsystem is TiDB's planner, not the separately implemented TiKV storage engine.

- **C2:** Logical operators expose statistics derivation, possible physical properties, physical implementation enumeration, and task construction through common interfaces. Tasks distinguish work in the SQL layer, storage coprocessors, and MPP execution.
- **C3:** Bottom-up statistics/property derivation feeds a top-down memoized search keyed by required properties. Pruning impossible orderings reduces search, and costs account for CPU, memory, network, and I/O.

**Entry point and evidence:** [Cost-based optimization development guide](https://pingcap.github.io/tidb-dev-guide/understand-tidb/cbo.html), with executable-structure pseudocode and a worked aggregate/join example. The chapter contains historical source paths and an older Cascades roadmap; those roadmap statements are not treated here as current implementation status.

### 19. [cockroachdb/cockroach](https://github.com/cockroachdb/cockroach)

**Language/role:** Go; distributed SQL database, specifically the `pkg/sql/opt` optimizer.

Study memo representations, normalization, physical properties, and the separation between preparation and execution-time rewriting. Its optimizer documentation explains failure modes as well as the happy path.

- **C1:** Memo groups must contain logically equivalent expressions. The design explicitly distinguishes a dangerous false equivalence, which produces incorrect plans, from missed equivalence, which primarily loses efficiency. Required physical properties may demand enforcement operators such as sorts.
- **C2:** Properties, statistics, costs, memo storage, transformations, and search form separate optimizer modules. Cached prepared expressions can be refined after placeholder values become known.
- **C3:** Compact memo groups represent many alternative trees; cost models must preserve the optimal-substructure assumption required by dynamic programming.

**Entry point and evidence:** [Optimizer package design](https://raw.githubusercontent.com/cockroachdb/cockroach/master/pkg/sql/opt/doc.go). This report concerns engineering structure; repository availability is not a claim of unrestricted licensing.

### 20. [apache/asterixdb](https://github.com/apache/asterixdb)

**Language/role:** Java; SQL++ database and the **Algebricks optimizer/Hyracks runtime** in `hyracks-fullstack`. **Official Apache GitHub mirror.**

Study a framework designed to separate a query language's data model from reusable algebra and parallel execution. The same monorepo includes both the database and its underlying compilation/runtime frameworks; the older separate Hyracks repository is not counted again.

- **C2:** Algebricks supplies data-model-neutral operators and rewriting while language implementations provide metadata, expression typing, comparators, hashing, and runtime functions.
- **C1:** Correct outer joins require language-specific null writers; sort and hash-join semantics depend on compatible comparators and hash functions. These are concrete obligations at abstraction boundaries.
- **C3:** Physical operators account for ordering and partitioning, and aggregation implementations can spill when state exceeds memory.

**Entry points and evidence:** [Current framework source tree](https://github.com/apache/asterixdb/tree/master/hyracks-fullstack) and the authors' [Algebricks architecture paper](https://asterix.ics.uci.edu/pub/p422-borkar.pdf), especially Sections 3.1–3.5. The paper is historical architectural evidence, not a current SQL++ feature inventory.

## Incremental query execution and maintained views

### 21. [TimelyDataflow/differential-dataflow](https://github.com/TimelyDataflow/differential-dataflow)

**Language/role:** Rust; incremental data-parallel computation framework used for relational and iterative queries.

Study how query execution changes when inputs are updates rather than immutable batches. Its reusable execution contribution is indexing and propagating changes across operators, including computations beyond a single acyclic SQL plan.

- **C2:** Collections of `(data, time, diff)` updates support composable operations; arrangements give operators a shared indexed representation rather than forcing every consumer to build its own state.
- **C3:** Arrangements stream indexed batches and maintain a compact merged history, reducing duplicate indexing work and supporting efficient later lookup.
- **C1:** Completion of a logical timestamp means no further updates at that time may arrive; reasoning about updates and completion is central to correct incremental results.

**Entry point and evidence:** [Arrangements chapter](https://timelydataflow.github.io/differential-dataflow/chapter_5/chapter_5.html). This is an execution building block, not a standalone SQL parser or cost-based optimizer.

### 22. [MaterializeInc/materialize](https://github.com/MaterializeInc/materialize)

**Language/role:** Rust; SQL planning and incremental view execution over timely/differential dataflow.

Study how a database adds SQL errors, query timestamps, and maintained views to a lower-level incremental runtime. This entry is distinct from Differential Dataflow because it implements the database-facing semantics and plan rendering.

- **C1:** The [rendering implementation](https://raw.githubusercontent.com/MaterializeInc/materialize/main/src/compute/src/render.rs) explains parallel collections of successful rows and errors. Division by zero, invalid casts, and overflow must surface as SQL errors; errors can also be retracted when corrected input arrives. The documented invariant requires correct rows when the error collection is empty.
- **C2:** Plans are rendered into reusable dataflow operators, while storage, compute, and SQL adaptation have distinct responsibilities.
- **C3:** Time-varying collections use updates and compaction rather than materializing every historical version.

**Second entry point:** [Materialize formalism](https://raw.githubusercontent.com/MaterializeInc/materialize/main/doc/developer/platform/formalism.md), covering frontiers and capabilities. It explicitly describes intended behavior; use it with the implementation, not as proof that every modeled command exists.

### 23. [risingwavelabs/risingwave](https://github.com/risingwavelabs/risingwave)

**Language/role:** Primarily Rust; streaming SQL plans and incremental execution, with persisted operator state.

Study a change-propagation engine organized around long-running actors, each containing a chain of relational executors. Its execution and recovery model contrasts with Differential Dataflow's arrangements and timestamp lattice.

- **C2:** A frontend stream plan is fragmented, parallelized into actors, and scheduled onto compute nodes. Actors combine mergers, executors, and dispatchers, giving clear boundaries for local computation and remote exchange.
- **C1:** Mergers align checkpoint barriers; consistency requires a snapshot to include each update through an epoch exactly once and exclude later updates. Recovery reconstructs pipelines and restores executor state from a consistent snapshot.
- **C3:** Shared state storage and asynchronous flushing address the cost of persisting state without making each checkpoint a fully blocking data-processing phase.

**Entry point and evidence:** [Streaming-engine developer guide](https://risingwavelabs.github.io/risingwave/design/streaming-overview.html), including plan fragmentation, actor execution, checkpointing, and recovery. Its storage examples reflect the guide's documented design.

### 24. [feldera/feldera](https://github.com/feldera/feldera)

**Language/role:** Rust runtime and Java SQL compiler; incremental query execution using DBSP circuits.

Study compilation from SQL views into a program that transforms input changes into output changes. Feldera combines a Calcite-based frontend with its own incremental compilation and runtime machinery, so it contributes substantially more than an integration wrapper.

- **C1:** A single input change can modify multiple tables and contain insertions and deletions; corresponding changes must propagate to all dependent views. SQL dialect choices remain explicit rather than disappearing in the streaming model. See the [SQL/DBSP introduction](https://docs.feldera.com/sql/intro/).
- **C2:** The [circuit API](https://docs.rs/dbsp/latest/dbsp/circuit/index.html) exposes streams, operator traits, nested circuits, scheduling, and handles for supplying inputs and consuming outputs.
- **C3:** A circuit can run in the calling thread or in a runtime containing multiple worker circuits, separating circuit construction from parallel execution.

Those two documents are the entry points. The SQL introduction explicitly distinguishes DBSP's standing-query model from a general transactional database.

## Coverage, search process, and limitations

Live web discovery used more than six distinct formulations, including: relational-algebra optimizer frameworks; Cascades/memo and adaptive optimization; vectorized execution libraries; Go storage-independent SQL engines; distributed SQL exchanges and scheduling; DataFrame lazy optimizers; incremental view maintenance and arrangements; research in-memory databases; GPU/LLVM query compilation; and semi-structured language compilation through Algebricks/Hyracks. Follow-up searches targeted operator interfaces, physical properties, barriers, failure recovery, and repository migrations. Later targeted searches mainly returned already identified systems, old paths, and duplicate integrations, yielding diminishing returns for this selection.

For every retained project, its exact GitHub repository page was opened, and at least one separate primary design document, implementation file, API guide, or substantive project discussion was opened and read. The linked entry points are those inspected sources, not search snippets. Raw implementation files are used where the browser could read them more reliably than GitHub's rendered source pages. Some attempted deep links were unavailable; they are not cited as verified evidence.

The selection covers C, C++, Java, Scala, and Rust/Go implementations; embedded libraries, full databases, cluster engines, research systems, and incremental runtimes; and rule-based, cost-based, adaptive, vectorized, compiled, and change-propagating architectures. Less ubiquitous entries include optd-original, Hyrise, go-mysql-server, Acero, and Algebricks/Hyracks. It is not an exhaustive catalog: graph/SPARQL-specific engines and additional lakehouse accelerators remain outside this pass's main emphasis.

Excluded from the retained list were tutorial/toy databases, standalone SQL parsers, query clients, plan-format specifications without substantial execution, benchmark-only artifacts, and lists of links. PrestoDB and additional Spark/Velox/DataFusion integrations were not added merely to count related implementations. The original Hyrise and standalone historical Hyracks trees were not duplicated. The new optd service was distinguished from the archived original rather than conflating their maturity or implementation.

No code was executed, dependencies installed, or repositories cloned. Performance descriptions identify mechanisms, not independently reproduced benchmark results. Most criteria judgments use C1–C3; C4 is explicitly assigned only where the inspected material establishes multi-year evolution and concrete compatibility/regression management. Versioned documentation, historical wiki pages, the Algebricks paper, and open optd design work are valuable study material but cannot establish the exact behavior of every current checkout.
