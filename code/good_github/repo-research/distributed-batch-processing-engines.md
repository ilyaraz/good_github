# Distributed batch processing engines

Research date: 2026-10-09

This selection covers engines that actually execute bounded, partitioned data processing or computational DAGs across machines: MapReduce, general dataflow, distributed dataframe/ETL, MPI-based analytics, and scientific task runtimes. Unified streaming engines are included only where their batch execution is explicit. Monorepos are counted once, with the relevant subsystem identified. The 24 entries are a code-reading guide, not a ranking or a claim that every component is exemplary.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failures. **C2** — substantial reusable abstractions supporting varied workloads. **C3** — real performance constraints addressed through an understandable architecture. **C4** — sustained evolution supported by compatibility, testing, or complexity-management evidence. Criteria below are judgments grounded in the linked material; repository age and popularity are not substitutes for evidence.

## General cluster and DAG engines

### 1. [apache/spark](https://github.com/apache/spark)

**Language/role:** Scala and Java core, with Python and other interfaces; distributed analytics engine. Study the relationship between lazy partitioned computations, shuffle boundaries, persistence, and recovery. The relevant monorepo areas are the core execution engine and SQL execution, rather than treating each API as a separate project.

- **C1:** RDD partitions can be recomputed after node loss, while closure capture and accumulator behavior expose the distinction between driver state, task-local copies, and repeated execution. These semantics make a useful correctness case study. The [RDD programming guide](https://spark.apache.org/docs/latest/rdd-programming-guide.html) explains recovery, shared variables, and execution behavior.
- **C2 / C3:** Transformations, actions, partitioned key/value operations, broadcasts, and persistence compose into many workloads. The same guide explains why shuffles incur network, serialization, memory, and disk costs and why storage levels affect reuse. It is a substantive entry point into the engine's abstraction/performance tradeoffs.

### 2. [apache/hadoop](https://github.com/apache/hadoop)

**Language/role:** Primarily Java; the **MapReduce subsystem** within the Hadoop monorepo. HDFS and YARN provide context, but the selected engine is `hadoop-mapreduce-project`. Study explicit task attempts and the boundary between successful computation and committed output.

- **C1:** Concurrent speculative attempts must not publish conflicting results. `OutputCommitter` coordinates setup, commit, abort, and cleanup; the documentation explains attempt-specific temporary output and warns that arbitrary side files need attempt-unique names. See the [MapReduce tutorial's output-commit sections](https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html#OutputCommitter).
- **C2 / C3:** Input formats, record readers, partitioners, comparators, combiners, and output formats separate application logic from partitioning and I/O. The [same implementation-oriented guide](https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html) describes shuffle/sort and buffering, making the classic model useful beyond its word-count examples.

### 3. [apache/flink](https://github.com/apache/flink)

**Language/role:** Primarily Java; bounded DataStream and relational batch execution inside a unified dataflow engine. Study how knowing that input terminates changes scheduling, state, ordering, and recovery.

- **C1:** Batch and streaming modes have different emission and ordering behavior. Custom operators must respect batch assumptions; batch recovery backtracks to stages with available intermediate results. These are documented semantic constraints, not simply configuration choices. See [execution modes and failure recovery](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/execution_mode/).
- **C2 / C3:** A common dataflow API supports bounded and unbounded applications, while batch mode introduces staged execution, materialized shuffles, and specialized aggregation strategies. The guide follows an actual operator graph through chaining and shuffle boundaries, providing a clear entry into the runtime architecture.

### 4. [apache/tez](https://github.com/apache/tez)

**Language/role:** Java; a programmable DAG execution engine on YARN, used beneath higher-level systems. Study the separation between task input/processor/output implementations and the application master that coordinates their graph.

- **C1:** The [DAG state machine](https://github.com/apache/tez/blob/master/tez-dag/src/main/java/org/apache/tez/dag/app/dag/impl/DAGImpl.java) explicitly handles recovery, vertex reruns, termination, internal errors, and asynchronous commit completion. Its transition table makes otherwise implicit lifecycle invariants inspectable.
- **C2:** The repository describes interchangeable input, processing, and output implementations assembled into arbitrary task DAGs. This is a reusable execution substrate rather than a single query language. Read the repository overview alongside `DAGImpl` to connect the public composition model to its concrete lifecycle machinery.

### 5. [hpcc-systems/HPCC-Platform](https://github.com/hpcc-systems/HPCC-Platform)

**Language/role:** C++ and ECL; **Thor**, the batch data-refinery engine, plus its compiler and runtime support. Roxie, the online query engine in the same monorepo, is not a second entry. Study how declarative ECL becomes executable activities and how those activities share memory infrastructure.

- **C1 / C3:** Thor must spill buffered rows and continue when memory is exhausted. The [memory-manager design](https://hpcc-systems.github.io/HPCC-Platform/devdoc/MemoryManager.html) specifies callback priorities, forbidden allocations during callbacks, lock-order deadlock hazards, and atomic pointer updates during resizing.
- **C2 / C4:** Activity interfaces allow reusable engine operations and extension while preserving compatibility with older workunits. The [new-activity walkthrough](https://hpcc-systems.github.io/HPCC-Platform/devdoc/newActivity.html) explains that mechanism. The repository additionally documents release/support tracks spanning 2023–2026 and a Thor regression-test workflow, supporting sustained evolution rather than an age-only claim.

### 6. [hazelcast/hazelcast](https://github.com/hazelcast/hazelcast)

**Language/role:** Java; the **Jet execution engine** integrated into the Hazelcast monorepo. Its [official configuration documentation](https://docs.hazelcast.com/operator/5.20/jet-engine-configuration) explicitly identifies batch and stream processing. Study cooperative processors and bounded queues; the older separate Jet repository is not counted again.

- **C1:** When an outbox is full, a processor must preserve enough state to resume without losing or duplicating work. The [cooperative execution design](https://docs.hazelcast.com/hazelcast/5.6/architecture/execution-engine) explains nonblocking `offer`, processor/tasklet suspension, and the tasklet state machine.
- **C2 / C3:** DAG processors, inboxes/outboxes, and lazy traversers form reusable execution contracts. Cooperative tasklets share CPU threads and report progress so the runtime can back off instead of spinning. This is particularly useful for studying how an API contract controls both concurrency correctness and scheduling overhead.

## Distributed dataframes, ETL, and Python computation

### 7. [dask/distributed](https://github.com/dask/distributed)

**Language/role:** Python; Dask's distributed scheduler and worker runtime. This entry selects the execution repository, not a second listing for the separate collection APIs. Study a dynamic scheduler whose task states and accounting rules are documented in unusual detail.

- **C1:** Task transitions update dependency sets, worker occupancy, resource usage, locations, and errors together. The [scheduler state-machine guide](https://distributed.dask.org/en/stable/scheduling-state.html) includes state-variable invariants, transition effects, and optional validation checks.
- **C2 / C3:** The same runtime accepts graphs from delayed functions, dataframes, and submitted futures. Root-task queuing limits work assigned to saturated workers; workers fetch dependencies from peers. The guide connects these decisions to explicit scheduler and worker state, making it possible to reason about memory pressure and scheduling behavior without treating the runtime as a black box.

### 8. [ray-project/ray](https://github.com/ray-project/ray)

**Language/role:** Python and C++; **Ray Data**, backed by Ray Core, in the Ray monorepo. Study distributed preprocessing and batch inference through the interaction of physical operators, task/actor execution, and the object store.

- **C2:** Dataset operations build logical plans that are lowered into physical execution plans. This supports varied file readers and batch transformations, including user functions. The [Ray Data internals guide](https://docs.ray.io/en/latest/data/data-internals.html) is the main entry point.
- **C1 / C3:** Backpressure limits buffered blocks, while object-store spill and UDF heap requirements are distinct concerns. The guide explains that memory hints influence scheduling rather than enforcing OS limits, and demonstrates how other Ray workloads can consume all CPUs and prevent Data tasks from running. These are concrete resource-progress and failure-mode lessons.

### 9. [Eventual-Inc/Daft](https://github.com/Eventual-Inc/Daft)

**Language/role:** Rust engine with Python interfaces; distributed dataframe processing for structured and multimodal data. Study the separation between its logical optimizer, per-node Swordfish engine, and Flotilla distributed scheduler. This is a distinct engine implementation even though its distributed runner uses Ray.

- **C2:** SQL/DataFrame expressions and Python UDFs become logical operators and expression trees. Local and distributed runners execute that planned computation. The [architecture documentation](https://docs.getdaft.io/en/stable/architecture/) traces the complete path.
- **C3:** Expensive operations such as image decoding and model inference receive separate scheduling/batching boundaries; the optimizer delays them when semantics permit. A Ray actor hosts a Swordfish instance per worker node, and the scheduler considers locality and load. Async channels between native operators and explicit blocking sinks explain how batch jobs can pipeline work within each node.

### 10. [apache/datafusion-ballista](https://github.com/apache/datafusion-ballista)

**Language/role:** Rust; distributed DataFusion SQL/DataFrame engine, including ETL pipelines. Study the additional execution machinery needed to turn an embedded columnar engine into a distributed batch system.

- **C1 / C3:** The [shuffle design](https://datafusion.apache.org/ballista/contributors-guide/shuffle.html) explains the blocking barrier: writers close materialized Arrow IPC outputs before downstream stages resolve their partition locations. It connects this choice to bounded resource use, failed-fetch recovery, selective map-task reruns, and retry budgets, while acknowledging stage stalls and extra I/O.
- **C2:** Schedulers and executors can be extended with formats, operators, expressions, or dialects. Arrow IPC/Flight and protocol-based boundaries give the distributed layer reusable interfaces. See the [architecture guide](https://datafusion.apache.org/ballista/contributors-guide/architecture.html). DataFusion itself is not counted separately here because its standalone execution is not distributed.

### 11. [mars-project/mars](https://github.com/mars-project/mars)

**Language/role:** Python/Cython; tensor, dataframe, and general-function computation over a distributed execution layer. Study the transition from user-visible large objects to executable chunks, rather than just the NumPy-like surface API.

- **C2:** Tileables, chunks, operands, and graphs underpin several computational interfaces. The [architecture guide](https://mars-project.readthedocs.io/en/stable/development/overview.html) describes separate task, scheduling, storage, metadata, session, and lifecycle services over the Oscar actor framework.
- **C1 / C3:** Execution performs high-level pruning, chunk-graph fusion, and locality-aware scheduling. Reference counts govern removal from both storage and metadata services; spilling and worker transfers belong to the storage service. These boundaries expose the interaction between distributed object lifetime and memory-efficient execution. The inspected architecture guide describes version 0.10.0; current release support was not established.

### 12. [bodo-ai/Bodo](https://github.com/bodo-ai/Bodo)

**Language/role:** Python, C++, and compiler infrastructure; dataframe/SQL processing with MPI-based distributed execution. Study a compiler-and-SPMD approach alongside centrally scheduled task engines.

- **C2:** The repository contains dataframe processing, native compilation of custom transformations, and integrated SQL, with a shared execution substrate. This is substantial implementation, not merely a pandas adapter.
- **C3:** The authors' [SPMD architecture discussion](https://www.bodo.ai/blog/scaling-gpu-dataframes-why-bodos-spmd-architecture-outperforms-task-based-engines) describes workers executing the same program, direct collective communication, streamed processing, and reducing device/host data movement. Its GPU path illustrates why communication topology belongs in engine design. Treat the article's comparative benchmarks as vendor-reported experiments; this selection relies on its architectural explanation and makes no speedup claim.

### 13. [cylondata/cylon](https://github.com/cylondata/cylon)

**Language/role:** C++ core with Python/Java interfaces; distributed relational operators using Arrow and MPI. It is both an embeddable library and a standalone distributed framework. Study how local kernels are composed with communication rather than assuming a cluster service is required for a batch engine.

- **C2:** Tables and local/distributed relational operators can be embedded in other data and ML applications. The [architecture document](https://raw.githubusercontent.com/cylondata/cylon/main/docs/docs/arch.md) separates data, operators, communication, and transport layers.
- **C3:** The [table implementation](https://raw.githubusercontent.com/cylondata/cylon/main/cpp/src/cylon/table.cpp) makes distributed join concrete: hash-shuffle both inputs, apply a local join, and construct the output table; a one-process case bypasses the shuffle. Arrow representation and separate timings for shuffle and join expose where costs occur. The architecture document contains older roadmap material, so its unimplemented items are not treated as current features.

## Native and research-oriented dataflow designs

### 14. [deib-polimi/renoir](https://github.com/deib-polimi/renoir)

**Language/role:** Rust; distributed dataflow with explicit support for terminating reductions over bounded input. Study Rust's typed operator composition and the grouping of operators into deployable blocks.

- **C2:** Streams, keyed streams, sources, joins, reductions, and iteration operators form a reusable dataflow API. The repository explains how blocks group sequential operators between repartition boundaries.
- **C1 / C3:** The [Stream API documentation](https://deib-polimi.github.io/renoir/renoir/struct.Stream.html#method.group_by_reduce) explains why `group_by_reduce` can aggregate locally before shuffling, while `group_by(...).reduce(...)` moves individual records first. The associative reduction contract enables that optimization. It also documents end-of-stream emission and block boundaries, exposing the semantic conditions under which reduced network traffic is valid. Included as a research engine; the README's comparative performance claim is not adopted here.

### 15. [thrill/thrill](https://github.com/thrill/thrill)

**Language/role:** C++; explicitly experimental distributed batch research framework. Study the distributed immutable array (DIA) model and compile-time fusion of user-defined functions.

- **C2:** DIA operations cover transformations, reductions, sorting, and prefix computations, with a common operation interface. The authors' [system paper, especially Sections II–III](https://arxiv.org/pdf/1608.05634), provides the implementation-oriented entry point.
- **C3:** Local operations and the initial work of a distributed operation are chained into compiled pipelines. The Link/Main/Push decomposition explains where pipelines end, where communication occurs, and where the next pipeline begins. Lazy stage construction resolves dependencies, while consuming prior storage as items advance avoids retaining two full datasets. This is a particularly clear study of abstraction costs in native batch execution; the repository explicitly cautions that it is experimental.

### 16. [DSC-SPIDAL/twister2](https://github.com/DSC-SPIDAL/twister2)

**Language/role:** Primarily Java, with Python interfaces and HPC integration; composable data analytics runtime. Study distributed construction of a job's execution graph and the continuum from collection APIs to communication operators.

- **C2:** TSet, Compute, and Operator APIs expose progressively lower levels of control and can be combined. The [batch-job guide](https://twister2.org/docs/concepts/batch_jobs) explains how each worker runs an `IWorker` program and constructs transformations.
- **C3:** TSets execute lazily at actions; cached or persisted results feed subsequent transformations. Memory and disk links let programmers control reuse and relieve memory pressure. These mechanisms distinguish its HPC-oriented execution model from a central driver issuing every transformation. The inspected [release page](https://twister2.org/docs/download) lists releases through 2020; included for its research architecture, without asserting present maintenance.

### 17. [husky-team/husky](https://github.com/husky-team/husky)

**Language/role:** C++; research distributed analytics engine for mixed coarse-grained transformations, graph work, and ML. Study object lists and typed communication channels as an alternative to immutable partition-only abstractions.

- **C2:** The [executor implementation](https://raw.githubusercontent.com/husky-team/husky/master/core/executor.hpp) provides reusable object-list execution, loading, globalization, and balancing, with a pluggable balancing algorithm.
- **C1 / C3:** Balancing broadcasts object counts, plans migration, finalizes deletions, flushes channels, and incorporates immigrants. Synchronous execution polls incoming channels before processing and flushes outputs afterward; asynchronous execution has explicit completion/progress handling and restricts supported channels. These concrete ordering requirements make it useful for studying migration and relaxed execution. The code also contains stated limitations; this entry does not imply production readiness or verified current maintenance.

## General task runtimes with substantial batch execution machinery

### 18. [bsc-wdc/compss](https://github.com/bsc-wdc/compss)

**Language/role:** Java runtime with Python, C/C++, and R bindings; COMPSs/PyCOMPSs distributed computational workflows. Included because it owns dependency analysis, execution, and data movement, rather than merely submitting jobs to another engine.

- **C1:** The runtime derives a dependency graph from accesses in application code, schedules only available parallelism, moves the required data, and reacts to task failures and exceptions. The [programming-model/runtime overview](https://compss-doc.readthedocs.io/en/stable/Sections/0_Intro.html) explains these responsibilities and the single-memory/storage illusion they support.
- **C2:** Task implementations can be language functions, external binaries, threaded programs, or multi-node MPI applications. This permits scientific batch workflows to combine computational models without replacing their inner algorithms. The repository identifies its runtime/bindings subtree and integration-test suite, providing a route from this conceptual model into the implementation.

### 19. [JuliaParallel/Dagger.jl](https://github.com/JuliaParallel/Dagger.jl)

**Language/role:** Julia; distributed DAG and out-of-core execution across workers, threads, and accelerators. Study the distinction between the central scheduler's global knowledge and each worker's local execution queues. The moved-out DTable package is not part of this selection.

- **C1:** Tasks transition through waiting, ready, running, and finished states; completion unlocks downstream dependencies and releases unneeded chunks. Worker errors propagate to the core scheduler. See [scheduler internals](https://juliaparallel.org/Dagger.jl/stable/scheduler-internals/).
- **C2 / C3:** Processor and scope abstractions support heterogeneous execution. Scheduling estimates both data-movement cost and queued work; worker-side stealing is permitted only when processor scopes are compatible. The [user documentation](https://juliaparallel.org/Dagger.jl/stable/) connects this to arrays, nested task graphs, file I/O, and GPU work, illustrating a reusable computational engine beyond dataframe ETL.

### 20. [chrislusf/gleam](https://github.com/chrislusf/gleam)

**Language/role:** Go; distributed MapReduce/DAG engine supporting Go functions and external pipe programs. Study a relatively compact driver/master/agent/executor design and how adjacent stages become execution groups. This is unrelated to the Gleam programming language.

- **C2:** Dataset flows combine partitioned transformations, joins, and pipe operations and can run locally or on distributed executors, as shown in the repository's execution overview.
- **C1 / C3:** The [logical planner](https://raw.githubusercontent.com/chrislusf/gleam/master/distributed/plan/plan_logical.go) permits merging only when task/shard counts and reader relationships allow it, and stops at driver/worker boundaries. The [physical planner](https://raw.githubusercontent.com/chrislusf/gleam/master/distributed/plan/plan_physical.go) groups corresponding tasks and asserts equal task counts. This is a focused example of safety conditions around fusion. The README describes incomplete features; no comprehensive fault-tolerance or maintenance guarantee is inferred.

## Historical systems and preserved architectural case studies

### 21. [apache/incubator-nemo](https://github.com/apache/incubator-nemo)

**Language/role:** Primarily Java; batch/dataflow engine with configurable compilation and runtime optimization policies, including a Beam runner. **Retired and archived:** the [ASF status record](https://incubator.apache.org/projects/nemo.html) records retirement on 2025-06-23; the substantive official GitHub archive remains available.

- **C2:** Compile-time and runtime passes operate over an intermediate DAG, allowing deployment policies to change execution without changing user computation. The repository's Beam examples establish batch-engine fit.
- **C1:** [PolicyImpl](https://raw.githubusercontent.com/apache/incubator-nemo/master/compiler/optimizer/src/main/java/org/apache/nemo/compiler/optimizer/policy/PolicyImpl.java) checks that annotating passes preserve graph structure and reshaping passes preserve existing execution properties. It runs DAG-integrity validation after optimization and saves diagnostic graphs on failure. Study this separation of optimization intent, mutation permissions, and validation rather than assuming optimizer passes are interchangeable arbitrary callbacks.

### 22. [discoproject/disco](https://github.com/discoproject/disco)

**Language/role:** Erlang core with Python workers; historical distributed MapReduce and pipeline engine. Study the division between a fault-oriented control runtime and user-language processing, plus explicit grouping of intermediate files. Its Python-2-era examples make its historical context clear; current support is not established.

- **C2:** Jobs can be expressed as sequences of stages, each pairing grouping rules with a task. Labels and host locations provide several grouping choices beyond a fixed map/reduce pair. See [pipeline data flow](https://disco.readthedocs.io/en/latest/howto/pipeline.html).
- **C3:** Node-local grouping can condense intermediate data before a global shuffle, with different choices trading task count against per-task memory. The same guide explains the mechanism rather than merely asserting locality. The [worker protocol](https://disco.readthedocs.io/en/latest/howto/worker.html) is a second entry point for understanding worker negotiation and task/input/output messages across the language boundary.

### 23. [MicrosoftResearch/Naiad](https://github.com/MicrosoftResearch/Naiad)

**Language/role:** C#; historical timely-dataflow research engine combining batch, iterative, and incremental computation. **Archived on 2024-06-17**, according to its repository page; its README explicitly describes an alpha release with limited testing.

- **C1:** The [progress-tracker implementation](https://raw.githubusercontent.com/MicrosoftResearch/Naiad/release_0.5/Naiad/Runtime/Progress/ProgressTracker.cs) exposes centralized and distributed tracking, pointstamp-count state, frontier-change notifications, and completion waiting. Study how distributed progress becomes a concrete termination condition rather than a simple count of finished tasks.
- **C2:** Dataflow construction and execution primitives support higher-level iterative and incremental libraries. The [project's conceptual introduction](https://microsoftresearch.github.io/Naiad/html/2a378dc0-df87-470e-9d7c-450ef7248667.htm) establishes this broad scope and explicitly includes batch computation. It is a valuable architectural reference, with the repository's testing and epoch-handling caveats retained rather than silently treating it as a supported modern engine.

### 24. [apache/hama](https://github.com/apache/hama)

**Language/role:** Java; bulk-synchronous parallel engine for scientific and data-analytics jobs. **Retired project; official GitHub mirror.** The repository identifies itself as a mirror, and the official tutorial carries the retirement notice. Included for its general BSP runtime, rather than counting its graph or ML layers separately.

- **C1:** A superstep separates local computation, communication, and a barrier; advancement occurs only when peers enter synchronization. The [BSP tutorial](https://hama.apache.org/hama_bsp_tutorial.html) makes clear that `sync()` advances the computation rather than ending the job, and demonstrates iterative loops.
- **C2 / C3:** `BSPPeer` combines message passing, counters, and input/output access, supporting reusable scientific computation patterns. Sender-side combiners aggregate messages to reduce communication. Study the algebraic requirements of those aggregations and the synchronization model as an alternative to long chains of separately scheduled MapReduce jobs.

## Coverage, search process, and limitations

Discovery used more than six distinct formulations, including: distributed batch engines and shuffle schedulers; MapReduce alternatives; Rust/C++ distributed dataflow; distributed dataframe engines; Apache Tez/Nemo/Hama; MPI/HPC analytics and Cylon/Twister2; Erlang and .NET batch systems; and Go/Julia DAG execution. Targeted searches then located architecture, state-machine, operator, progress-tracking, compatibility, and retirement evidence. Later discovery returned many duplicates, forks, generic schedulers, streaming-only projects, and wrappers; additions were retained only when they contributed a distinct execution design.

All 24 canonical repository pages were opened. Each entry also uses at least one independently inspected primary document or implementation file, with substantive architecture or code behind its criteria. Several GitHub tree pages and old documentation URLs failed in the web reader; direct public source reads and working official documentation supplied the missing evidence. GitHub's unauthenticated API was rate-limited, so it was not used as evidence. No candidate code was executed, no dependencies were installed, and no large repositories were cloned.

The scope deliberately excludes cluster allocation systems and generic job queues, pipeline front ends without their own relevant execution machinery, streaming-only runtimes, and standalone single-process engines. Beam was investigated as a programming model, but its external distributed runners are represented by their engines rather than counting the abstraction again. Hive/Pig-style front ends and orchestration across existing engines were likewise not added. IgnisHPC and MBrace were explored but not retained: their split repositories would require additional component-level verification to select a single substantial engine repository confidently. These exclusions are scope/evidence decisions, not quality judgments.

Versions differ across the inspected sources. Moving documentation URLs and default branches describe the material available on the research date, while older guides are labeled where material. Archived/retired status is explicit for Nemo, Naiad, and Hama; other research or historical entries make no unverified claim of active maintenance. C4 is awarded selectively where multi-year evolution and compatibility/testing evidence were actually inspected. Performance criteria refer to mechanisms and tradeoffs, not independently reproduced benchmark results. The scientific task-runtime entries occupy the broader edge of this category, but each owns distributed execution and data/dependency handling rather than only launching another batch engine.
