# Distributed task queues and job schedulers

Research date: **2026-10-09**.

This selection covers 26 GitHub repositories implementing distributed background work, persistent task queues, recurring-job coordination, or cluster batch scheduling. It spans broker-backed workers, relational-database queues, standalone job servers, distributed cron, and scientific computing schedulers. A networked queue serving distributed workers belongs here even when its queue server is not itself a replicated cluster. The emphasis is on concrete mechanisms an experienced engineer can study, not popularity or a blanket production recommendation.

Criteria used below:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and models supporting different applications.
- **C3 — Performance:** real resource or throughput constraints addressed through understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or deliberate complexity management.

Each linked repository heading is a verified canonical GitHub location. Additional links point to primary documentation or implementation material that was opened and read. Criteria describe the specific evidence cited; they do not imply that every component is uniformly exemplary. Delivery guarantees must be distinguished from the effects of user code: none of the queue mechanisms below establishes universal exactly-once external side effects.

## Broker-backed workers and network job servers

### 1. [celery/celery](https://github.com/celery/celery)

**Python — distributed task framework.** Study how a task abstraction crosses producer, broker, worker, retry, and result-backend boundaries, with configurable execution pools and transports.

- **C1:** Acknowledgment timing has carefully qualified semantics. `acks_late` moves acknowledgment after task execution, but child-process termination can still acknowledge a message unless additional worker-loss behavior is configured. The guide explains why unconditional redelivery can create destructive failure loops. This is useful material for reasoning about idempotence and poison tasks. See the [task execution and acknowledgment guide](https://docs.celeryq.dev/en/stable/userguide/tasks.html).
- **C2:** The same guide explains named task registration, bound tasks, custom task classes, retry behavior, and lifecycle hooks: reusable boundaries between application code and worker machinery.
- **C4:** The [5.0 release history](https://docs.celeryq.dev/en/stable/history/changelog-5.0.html) records 2020–2021 fixes involving thread-local backends, serialization regressions, and test hangs; the repository's later Python/version support matrix demonstrates continued compatibility management rather than age alone.

### 2. [Bogdanp/dramatiq](https://github.com/Bogdanp/dramatiq)

**Python — actor-style background processing over RabbitMQ or Redis.** A useful study in keeping the execution model small while moving cross-cutting behavior into middleware.

- **C1:** Messages are acknowledged after successful processing, with redelivery after worker failure. Graceful shutdown stops consumption, lets workers finish, and returns remaining in-memory work. Time limits also expose a concrete runtime limitation: interrupting a Python thread cannot reliably interrupt a blocking system call. These boundaries are explained in the [advanced topics guide](https://dramatiq.io/advanced.html).
- **C2:** That guide documents middleware composition for retries, limits, callbacks, pipelines, and optional result storage. Broker implementations and middleware provide reusable extension points without requiring each actor to implement transport or shutdown logic.

The interesting comparison with Celery is the placement and size of abstractions, not an unsupported claim that one framework is universally simpler or faster.

### 3. [sidekiq/sidekiq](https://github.com/sidekiq/sidekiq)

**Ruby — Redis-backed threaded job processing.** Study worker concurrency as an application-wide resource budget, and the difference between graceful recovery and durable reservation.

- **C1:** The open-source fetch path uses Redis `BRPOP`, which removes a job before execution. A hard process failure can therefore lose in-progress work; graceful push-back does not eliminate that window. The [reliability documentation](https://github.com/sidekiq/sidekiq/wiki/Reliability) explicitly distinguishes these semantics from commercial Pro mechanisms. Pro's `super_fetch` is not attributed to this open-source implementation.
- **C3:** The [scaling guide](https://github.com/sidekiq/sidekiq/wiki/Scaling) connects worker threads to Redis and database connection pools, CPU versus I/O behavior, queue latency, and isolation of long or memory-heavy jobs. This provides concrete architectural reasons why increasing concurrency can exhaust downstream resources instead of increasing throughput.

### 4. [taskforcesh/bullmq](https://github.com/taskforcesh/bullmq)

**TypeScript — persistent job queues; the Redis-backed Node.js worker path is the focus here.** Study dependency-aware job states together with event-loop-sensitive ownership renewal.

- **C1:** Active jobs require continued liveness updates. A stalled job may return to the waiting queue or fail after repeated stalls; CPU-heavy work can prevent timely renewal by blocking the event loop. The [stalled-job guide](https://docs.bullmq.io/guide/jobs/stalled) explains this relationship and process-isolated workers. “Stalled” is an event, not an additional persistent job state.
- **C2:** The [architecture guide](https://docs.bullmq.io/guide/architecture) describes waiting, delayed, active, completed, failed, and dependency-waiting states. Parent jobs become runnable after their children finish, making flows a reusable dependency model rather than an application-specific convention.

Read these two documents together: a dependency graph still runs on a delivery system whose ownership can expire and require retry-safe handlers.

### 5. [hibiken/asynq](https://github.com/hibiken/asynq)

**Go — Redis-backed asynchronous task processing.** The processor is a compact entry point into lease ownership, cancellation, capacity limits, and queue selection.

- **C1:** In [processor.go](https://github.com/hibiken/asynq/blob/master/processor.go), task execution is tied to leases and contexts. Lease expiration cancels processing and leaves recovery to the recovery machinery; completion and retry operations check lease validity. This makes the boundary between executing work and retaining authority to update its state explicit.
- **C3:** The same implementation bounds execution with a semaphore, adds jitter to polling, and distinguishes strict priority from randomized weighted queue selection. These are concrete responses to Redis load, worker capacity, and starvation risk.

The repository documents a pre-1.0 API and Redis Cluster limitations involving Lua scripts. Those constraints matter when treating its interfaces and storage assumptions as reusable examples.

### 6. [contribsys/faktory](https://github.com/contribsys/faktory)

**Go — language-neutral background-job server.** Study a server/client boundary that keeps job storage and reservation policy out of language-specific workers.

- **C1:** The [worker lifecycle protocol](https://github.com/contribsys/faktory/wiki/Worker-Lifecycle) defines reserved jobs that require `ACK` or `FAIL`, with expiration allowing re-execution. Worker heartbeats and quiet/terminate states make shutdown coordination part of the protocol rather than an informal client convention.
- **C2:** The same document specifies version negotiation, worker identities, long-lived connections, typed job payloads, and queue-directed fetching. Independent language clients can implement the same execution contract.
- **C3:** Fetching can block briefly when no job exists, reducing busy polling. Queue order affects starvation; the documentation discusses randomizing that order when strict priority is inappropriate.

This entry concerns the public server and protocol, not commercial-only scheduling or batch features.

### 7. [beanstalkd/beanstalkd](https://github.com/beanstalkd/beanstalkd)

**C — standalone network work queue.** Its small wire protocol is particularly useful for studying an explicit job state machine without a large application framework.

- **C1:** The [protocol specification](https://github.com/beanstalkd/beanstalkd/blob/master/doc/protocol.txt) defines reservation time-to-run, expiry back to ready state, delayed release, buried jobs, and `DEADLINE_SOON`. The latter prevents a worker from blocking on another reservation too close to an existing job's deadline. Binary payload framing and error responses are also specified precisely.
- **C2:** Named tubes, producer selection, consumer watch sets, opaque job bodies, priorities, delays, and reserve/release/delete operations form a reusable language-neutral queue model. Failed work can be buried and later kicked back into circulation.

This is a queue server for distributed clients and workers, not evidence of a replicated consensus-based queue cluster.

### 8. [gearman/gearmand](https://github.com/gearman/gearmand)

**C++ — distributed function/job server with a language-neutral protocol.** Study the differences between detached background jobs and foreground work with streamed results.

- **C2:** The [Gearman protocol](https://gearman.org/protocol/) separates function registration, job submission, worker wakeup, assignment, progress, and completion. Workers advertise capabilities; clients submit a function name and opaque payload. This supports heterogeneous worker implementations without embedding language runtimes in the server.
- **C3:** `WORK_DATA` permits partial results to flow before completion, avoiding the need to buffer an entire result. Unique identifiers may coalesce queued or already-running requests, reducing redundant work while changing result fan-out semantics. Both mechanisms are described in the protocol.
- **C1:** Coalescing, detached clients, and the `PRE_SLEEP`/`NOOP`/`GRAB_JOB` sequence provide concrete concurrent protocol behavior to inspect; a notification and a successful job assignment are distinct operations.

### 9. [taskiq-python/taskiq](https://github.com/taskiq-python/taskiq)

**Python — asynchronous task framework with pluggable brokers and result backends.** Particularly useful for studying the seam between execution lifecycle and transport-specific guarantees.

- **C2:** The [architecture overview](https://taskiq-python.github.io/guide/architecture-overview.html) separates broker `kick`/`listen`, task messages, result storage, dependency injection, and ordered middleware hooks. Broker integrations can live outside the core rather than forcing every transport into one implementation.
- **C1:** The [receiver implementation](https://github.com/taskiq-python/taskiq/blob/master/taskiq/receiver/receiver.py) exposes acknowledgment stages for receipt, execution, and result saving; the default is acknowledgment after saving. Choosing a stage changes the relationship between transport acknowledgment and durable result visibility.
- **C3:** The receiver separately bounds asynchronous execution and prefetching with semaphores, making memory pressure and work concurrency different controls.

Durability and redelivery remain dependent on the chosen broker integration; the core abstraction alone does not establish a universal delivery guarantee.

### 10. [choria-io/asyncjobs](https://github.com/choria-io/asyncjobs)

**Go — NATS JetStream-backed task processing.** A less-established but substantive example that separates stored task records from work-queue entries referencing them. The repository describes heavy ongoing development, so this is an architecture study candidate rather than a maturity claim.

- **C1:** The [task lifecycle](https://choria-io.github.io/asyncjobs/reference/task-lifecycle/index.html) distinguishes failure to create a work-queue entry from ordinary execution failure, and documents orphaned records when queue retention expires without a processor. Dependency failure has its own terminal state. The guide also makes clear that default task storage is not replicated.
- **C2:** The [routing, concurrency, and retry guide](https://choria-io.github.io/asyncjobs/reference/routing-concurrency-retry/index.html) specifies handler routing, global and per-route middleware, and replaceable retry policies.
- **C3:** That guide distinguishes per-client from queue-wide concurrency limits. Its runtime timeout discussion also exposes the duplicate-execution risk when a slow handler is mistaken for a failed one.

## Database-backed queues and embedded worker frameworks

### 11. [riverqueue/river](https://github.com/riverqueue/river)

**Go — PostgreSQL-backed job queue.** Focus on the Go job/worker subsystem and the relationship between database transactions and asynchronous execution.

- **C1:** The [transactional enqueueing guide](https://riverqueue.com/docs/transactional-enqueueing) demonstrates inserting application data and the corresponding job in one transaction. This closes both the “committed data but no job” gap and the “worker runs before data commits” race. The guarantee concerns the database transaction, not arbitrary external effects performed later.
- **C2:** The repository's typed job-argument and worker interfaces separate durable job kinds and serialized arguments from execution behavior. Together with transactional client operations, they support reusable workers across application domains without making callers construct queue SQL themselves.

Study the transaction examples alongside the repository's typed-worker examples: the strongest design point is integrating asynchronous work with the application's existing consistency boundary.

### 12. [oban-bg/oban](https://github.com/oban-bg/oban)

**Elixir — persistent background-job framework.** This entry specifically examines the PostgreSQL Basic engine, not commercial engines or every database backend in the repository.

- **C1:** The [Basic engine implementation at v2.24.1](https://github.com/oban-bg/oban/blob/v2.24.1/lib/oban/engines/basic.ex) uses a fenced query structure to prevent query-planner behavior from causing a limited fetch to update more rows than intended. Claiming work also records execution ownership and attempts transactionally. The comments make the subtle SQL invariant unusually accessible.
- **C3:** Fetch demand is computed from configured capacity minus currently running jobs. Ordered selection with `FOR UPDATE SKIP LOCKED` allows competing workers to claim available work without waiting on each other's selected rows, while the demand bound prevents overfilling a worker.

The [Basic engine API](https://oban.hexdocs.pm/Oban.Engines.Basic.html) supplies an interface map; the versioned source is the substantive reading entry point. Do not generalize this engine's behavior to paid global-concurrency features.

### 13. [graphile/worker](https://github.com/graphile/worker)

**TypeScript — PostgreSQL-backed Node.js task workers.** Study the economics of database round trips and the operational consequences of prefetching jobs into a local queue.

- **C1:** The [performance guide](https://worker.graphile.org/docs/performance) documents the downside of local prefetch: jobs already locked for a process can remain unavailable after that process crashes until recovery takes effect. Prefetch capacity therefore changes failure recovery as well as throughput.
- **C3:** The same guide describes batching completion and failure updates, reducing database round trips and write-ahead-log churn. It also explains why adding too many workers can move the bottleneck into PostgreSQL and lower useful throughput. Its performance harness and workload descriptions provide a starting point for reproducing measurements rather than accepting a headline benchmark.

This is a useful contrast with queues that delegate most scheduling and acknowledgment behavior to an external message broker.

### 14. [timgit/pg-boss](https://github.com/timgit/pg-boss)

**TypeScript — PostgreSQL job queue with explicit queue policies.** Study how database-backed state constraints can expose materially different concurrency and retry contracts through one API.

- **C1:** The [queue policy reference](https://pgboss.io/api/queues) describes interactions between active jobs, retries, and singleton keys. Under the `stately` policy, a job can fail permanently when retry occupancy prevents another retry; strict FIFO policies can intentionally block a key behind failed work until intervention. These are semantic choices, not merely tuning flags.
- **C2:** Standard, singleton, exclusive, stately, and per-key FIFO policies provide reusable scheduling models for different workloads. The same API describes dead-letter handling and queue configuration, making ordering, deduplication, and failure policy explicit application decisions.

PostgreSQL locking can coordinate job claims, but marketing language about exactly-once delivery should not be read as an exactly-once guarantee for user-code side effects.

### 15. [bensheldon/good_job](https://github.com/bensheldon/good_job)

**Ruby — PostgreSQL-backed Rails Active Job execution.** Study durable job state integrated with a framework that already defines serialization, callbacks, and retry behavior.

- **C1:** The [job model](https://github.com/bensheldon/good_job/blob/main/app/models/good_job/job.rb) exposes job state and locking machinery, including advisory-lock and skip-locked/hybrid paths. It is a concrete entry point for tracing how a framework-level job becomes an exclusively claimed database record and how concurrency controls interact with execution.
- **C4:** The [changelog](https://github.com/bensheldon/good_job/blob/main/CHANGELOG.md) contains 2021 Rails 7 testing and Ruby 3 support work, alongside 2026 concurrency-race fixes, parallel-test changes, and deprecation of concurrency options. This provides evidence of multi-year compatibility and complexity management, not merely an old repository creation date.

The study value lies in the coupling between Rails lifecycle semantics, database ownership, and operational changes across releases.

### 16. [apalis-dev/apalis](https://github.com/apalis-dev/apalis)

**Rust — asynchronous job-processing framework; focus on `apalis-core` and worker machinery.** Its ecosystem includes separate storage integrations, while the core emphasizes Rust futures and Tower services.

- **C1:** In the [worker module](https://github.com/apalis-dev/apalis/blob/main/apalis-core/src/worker/mod.rs), attempts are incremented when a future is first polled rather than merely constructed. Tracked tasks and readiness checks also participate in pause and shutdown behavior. These mechanisms address correctness specific to lazy asynchronous execution.
- **C2:** Tower `Service`/`Layer` composition separates handlers, middleware, and worker behavior from storage adapters, supporting reusable retry, tracing, and execution policies.
- **C3:** Service readiness and polling provide explicit backpressure; paused or shutting-down workers do not simply continue pulling work into an unbounded execution path.

The inspected default branch and published documentation may describe different release generations. Treat these source-level observations as a dated snapshot, not an assertion about every released crate version.

### 17. [HangfireIO/Hangfire](https://github.com/HangfireIO/Hangfire)

**C# — persistent background jobs and recurring execution for .NET.** The recurring scheduler is a useful subsystem for understanding how an application library coordinates across multiple server processes.

- **C1:** The [recurring scheduler implementation](https://github.com/HangfireIO/Hangfire/blob/main/src/Hangfire.Core/Server/RecurringJobScheduler.cs) uses distributed locking and storage transactions around scheduling work. It also handles unsupported job versions and compatibility cases, so recovery is not just a timer callback followed by an enqueue.
- **C2:** Storage operations, background-process execution, job construction, and time-zone resolution are separated behind reusable interfaces or injected collaborators. This makes recurring scheduling adaptable without embedding one database's implementation throughout the scheduler.
- **C3:** The code distinguishes storage capabilities for batched operations and manages connections for parallel scheduling. Polling frequency is an explicit tradeoff against storage work.

The entry concerns the public core; commercial extensions and third-party storage providers require separate evaluation.

## Distributed recurring-job coordination

### 18. [quartz-scheduler/quartz](https://github.com/quartz-scheduler/quartz)

**Java — job and trigger scheduling, including clustered JDBC JobStore.** Study shared-database coordination and the costs of giving recurring triggers a cluster-wide owner.

- **C1:** The [Quartz 2.3 clustering guide](https://www.quartz-scheduler.org/documentation/quartz-2.3.0/configuration/ConfigJDBCJobStoreClustering.html) explains database-mediated trigger acquisition and recovery after a scheduler node fails. Recovery execution is conditional on the job's recovery setting, and synchronized clocks are an operational requirement. This is richer than simply having several processes evaluate the same cron expression.
- **C3:** The guide identifies contention from cluster-wide locking and suggests partitioning work when very short jobs make coordination overhead dominate. It connects a specific synchronization design to its scaling limit.

The cited guide is explicitly versioned 2.3 documentation. It supports the JDBC clustering architecture discussed here, not a claim that all configuration defaults are unchanged in newer releases. The canonical repository was also verified through GitHub's API.

### 19. [kagkarlsson/db-scheduler](https://github.com/kagkarlsson/db-scheduler)

**Java — persistent embedded scheduler using a relational database.** A focused alternative for studying scheduled work without deploying a separate scheduling service.

- **C1:** The [scheduler implementation](https://github.com/kagkarlsson/db-scheduler/blob/master/db-scheduler/src/main/java/com/github/kagkarlsson/scheduler/Scheduler.java) separates due-work execution from housekeeping and dead-execution detection. Shutdown keeps heartbeats alive until worker execution has stopped, avoiding a window in which another scheduler could mistake still-running local work for abandoned work.
- **C2:** Task definitions, schedules, client operations, and polling strategies are distinct concepts. Recurring work reschedules through the persistent task model instead of requiring the application to maintain an independent timer loop.
- **C3:** The scheduler selects between fetching candidates and locking/fetching work, exposing alternative database-claim strategies rather than assuming one contention pattern fits every deployment.

The repository's architecture description and the shutdown order in the source form a particularly approachable pair for tracing failure recovery end to end.

### 20. [apache/shardingsphere-elasticjob](https://github.com/apache/shardingsphere-elasticjob)

**Java — distributed scheduling through logical job sharding and a registry.** The relevant project is ElasticJob in this repository, counted once.

- **C1:** The [failover design](https://shardingsphere.apache.org/elasticjob/current/en/features/failover/) distinguishes assigning shards at the next scheduled run from compensating unfinished work during the current run. It explicitly requires idempotent application behavior. Failover can also add registry traffic, making it unsuitable for some short-interval workloads.
- **C2:** The [elastic scheduling design](https://shardingsphere.apache.org/elasticjob/current/en/features/elastic/) separates numeric shard assignments from application data processing. Applications map shards to their own domains, while the framework manages membership, leader election, and reassignment.
- **C1:** That design also delays ordinary resharding until the next trigger and blocks execution while sharding completes. Registry nodes separately represent membership, shard ownership, execution, failover, and leader coordination, exposing the invariants rather than hiding them behind a generic “high availability” label.

### 21. [xuxueli/xxl-job](https://github.com/xuxueli/xxl-job)

**Java — centralized scheduling and distributed executors.** Study the boundary between trigger generation, routing, remote execution, and completion reporting.

- **C1:** The [current Chinese architecture and operations guide](https://github.com/xuxueli/xxl-job/blob/master/doc/XXL-JOB%E5%AE%98%E6%96%B9%E6%96%87%E6%A1%A3.md) discusses rare duplicate triggers, lost completion callbacks, heartbeat-based failure handling, and graceful draining of scheduling and executor work. These documented edge cases are more informative than interpreting a scheduling lock as an end-to-end exactly-once guarantee.
- **C2:** The same guide separates the scheduling center from executor-side `JobHandler` implementations and exposes routing and integration interfaces. Central policy can evolve independently of the application task body.
- **C3:** Fast and slow dispatch pools and time-wheel scheduling show how trigger latency and slow remote executors affect the scheduler's internal organization.

The current guide states that a custom scheduler replaced the earlier Quartz-based design. Older English documentation describes that earlier architecture and was not used to characterize the current implementation.

### 22. [PowerJob/PowerJob](https://github.com/PowerJob/PowerJob)

**Java — distributed scheduler with standalone, broadcast, Map, and MapReduce execution.** Count the monorepo once; the main study targets are `powerjob-server` and `powerjob-worker`.

- **C1:** The worker's [HeavyTaskTracker implementation](https://github.com/PowerJob/PowerJob/blob/master/powerjob-worker/src/main/java/tech/powerjob/worker/core/tracker/task/heavy/HeavyTaskTracker.java) rejects stale status reports and backward state transitions while coordinating updates through segmented locks. Its comments also expose a clock-skew assumption in timestamp comparisons. This is concrete material on reconciling asynchronous reports from distributed execution.
- **C2:** The repository's execution modes share task-tracking infrastructure rather than requiring independent schedulers for every processing pattern. The tracker separates reporting, persistence, and task progress from user processors.
- **C3:** Cached task summaries and segmented locking provide a readable implementation for studying the tradeoff between persistence lookups and concurrent status-update contention. This is an architectural inference from the code, not a measured performance claim.

### 23. [dkron-io/dkron](https://github.com/dkron-io/dkron)

**Go — distributed cron and remote execution.** The canonical repository is now under `dkron-io`; the older `distribworks` location redirects here and is not a separate project.

- **C1:** The [architecture and startup guide](https://dkron.io/docs/basics/getting-started/) distinguishes a scheduling leader, replicated state, and execution agents. It describes Raft replication of state stored in BoltDB and separate membership behavior through Serf. This separation is useful for reasoning about which component supplies agreement and which detects cluster membership.
- **C2:** Server and agent roles, tag-based execution targets, and job configuration make the scheduler reusable across machine groups without hard-coding host assignments into individual tasks.

Leader coordination and replicated metadata do not by themselves prove that an external command executes exactly once during failures. Study the boundary between initiating an execution query and receiving its results rather than collapsing those actions into a single transaction.

### 24. [jhuckaby/Cronicle](https://github.com/jhuckaby/Cronicle)

**JavaScript — multi-server cron with a web interface and plugin execution.** The repository explicitly describes a maintenance phase focused mainly on bug and security fixes, with xyOps presented as its successor; Cronicle remains a substantive study target in its own right.

- **C1:** The [inner-workings document](https://github.com/jhuckaby/Cronicle/blob/master/docs/InnerWorkings.md) explains persistent event cursors and catch-up behavior. It also states a concrete failover limitation: after an unclean primary failure, the replacement may not know about interrupted jobs, so catch-up does not automatically guarantee their replay.
- **C2:** Server groups, scheduling policies, and a JSON-oriented plugin interface allow different scripts and executables to participate in the same scheduling system.

The design uses hostname-based primary selection and requires shared storage for backup-primary failover. It is valuable precisely because the documentation exposes those assumptions; it should not be described as a Raft-style consensus scheduler.

## Cluster batch and scientific computing schedulers

### 25. [SchedMD/slurm](https://github.com/SchedMD/slurm)

**C — cluster resource management and batch scheduling.** Focus on `slurmctld` and the backfill scheduling subsystem; the larger repository is counted once.

- **C1:** The [scheduling configuration and design guide](https://slurm.schedmd.com/sched_config.html) explains how backfill considers lower-priority jobs while reserving resources for higher-priority jobs' expected starts. Time estimates, partitions, and resource availability become coupled scheduling constraints rather than a simple FIFO queue.
- **C3:** The same guide separates quick event-triggered scheduling from broader periodic scans. It discusses bounded search depth, whole-node reservations, and periodically releasing locks so lengthy scheduling passes do not make the controller unresponsive. Continuing a scan versus restarting it also trades scheduling progress against responsiveness to newly arrived work.

Study Slurm when the scarce resource is a coordinated set of machines and accelerators, rather than only a worker thread or database connection. The guide gives concrete reasons for scheduler cost and utilization tradeoffs without requiring unsupported benchmark claims.

### 26. [htcondor/htcondor](https://github.com/htcondor/htcondor)

**Primarily C++ — distributed high-throughput batch computing.** Focus on the `schedd`, negotiator, `startd`, shadow, and starter responsibilities within the monorepo.

- **C2:** The [administrator architecture guide for 25.0](https://htcondor.readthedocs.io/en/25.0/admin-manual/introduction-admin-manual.html) separates job queues at access points, ClassAd resource advertisements, matching by the negotiator, execution-host policy, and per-job process supervision. ClassAds provide a reusable language for expressing resource requirements and offers across heterogeneous machines.
- **C3:** The guide connects scaling to that decomposition: additional access points spread queue and submission load, while per-running-job shadows impose memory costs on an access point. This makes capacity planning traceable to daemon responsibilities rather than a generic “distributed” claim.
- **C1:** Execution-host policy governs starting, suspending, resuming, vacating, and killing jobs. Those transitions are coordinated across distinct daemons, providing substantial ownership and preemption behavior to inspect.

## Coverage, search process, and limits

Discovery used more than six distinct live-search formulations, followed by direct repository, documentation, and source inspection. Search angles included Python acknowledgment and retry behavior; Ruby and Node.js Redis workers; Go queue leases; PostgreSQL transactional enqueueing and `SKIP LOCKED`; Rust asynchronous worker abstractions; .NET persistent recurring jobs; Java database schedulers and Chinese distributed-scheduling projects; distributed cron leadership; C/C++ job-server protocols; NATS task processing; and HPC backfill and matchmaking. Searches for less prominent Go, Rust, PHP, Erlang, and NATS projects broadened discovery beyond the familiar Celery/Sidekiq family. Later queries increasingly returned the same candidates, integrations, forks, and listicles; the NATS candidate was retained because it added a distinct architecture.

All 26 canonical repository pages or GitHub API records were opened, and each retained project has additional primary material beyond its README. Source files, detailed protocol or architecture guides, and release history supplied the implementation evidence. GitHub archive metadata was checked for the initial 25-project selection; none was marked archived. That is not an active-maintenance endorsement. Choria's development warning and Cronicle's maintenance phase are called out separately. Redirected repository identities were normalized, and forks or translated documentation copies were not counted as independent implementations.

General-purpose brokers such as Redis, RabbitMQ, Kafka, and NATS were treated as infrastructure rather than separate task-queue implementations. General workflow orchestrators, local-only timer libraries, framework-wide repositories with incidental queue adapters, tutorials, thin wrappers, and awesome-lists were outside this selection's center of gravity. Other legitimate queues were omitted where they would mostly repeat an already well-covered design; this is a diverse selection guide, not an exhaustive ecosystem census.

No candidate code was executed, dependencies installed, or independent performance measurements made. Documentation and default branches can move; explicitly versioned links are used where the inspected material was version-specific. Implementation-derived interpretations are identified where relevant. C4 is claimed only where release and compatibility evidence was actually inspected, rather than inferred from repository age or recent activity. The main limitation is that source and documentation inspection can expose design mechanisms and stated failure boundaries, but cannot establish their behavior under every real deployment or failure injection.
