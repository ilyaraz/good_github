# Task parallelism libraries and work-stealing schedulers

Research date: **2026-10-09**.

This selection covers 27 GitHub repositories implementing reusable task parallelism, fork–join execution, dependency-graph scheduling, fiber tasking, or work-stealing infrastructure. It includes compact libraries, HPC runtimes, and explicitly identified subsystems of larger language runtimes. Crossbeam is included as a scheduler building block, not a complete executor. Distributed task systems are included where their task scheduler is central to the implementation. General workflow orchestration, operating-system schedulers, and libraries that merely submit work to another runtime are outside the main scope.

The explanations identify engineering subjects worth studying; they are not correctness certifications or claims that every component is exemplary. Repository identities and archive flags were checked through GitHub, and implementation or design material was read for every entry. Default-branch links describe the inspected development code and can change after this date.

Criteria legend:

- **C1 — Difficult correctness:** substantive invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and mechanisms useful across multiple applications.
- **C3 — Performance with structure:** real scheduling, locality, allocation, or synchronization constraints addressed through an understandable architecture.
- **C4 — Sustained evolution:** evidence across years together with compatibility, testing, or complexity management. An old repository or recent push alone does not qualify.

## C++ task graphs and composable fork–join libraries

### 1. [uxlfoundation/oneTBB](https://github.com/uxlfoundation/oneTBB)

**Language/role:** C++; general parallel algorithms and task runtime. Study how an established library maps nested fork–join work onto a shared scheduler while managing locality, memory consumption, and execution controls.

- **C2:** Parallel algorithms, task arenas, and task scheduling controls provide several levels of reusable parallelism. The release notes document concrete arena and resource-limiter behavior, including concurrency-limit fixes and preserving settings when attaching arenas. [Release notes](https://github.com/uxlfoundation/oneTBB/blob/master/RELEASE_NOTES.md).
- **C3:** The scheduler guide explains the relationship between local depth-first execution, stealing older tasks, cache locality, and limiting the live task graph. It also identifies task bypassing as a separate scheduling path. This is a useful explanation of why deque discipline is an architectural choice rather than simply a queue implementation detail. [How the scheduler works](https://github.com/uxlfoundation/oneTBB/blob/master/doc/main/tbb_userguide/How_Task_Scheduler_Works.rst).

### 2. [taskflow/taskflow](https://github.com/taskflow/taskflow)

**Language/role:** C++; task-dependency graphs and a work-stealing executor. Study the separation between graph construction, recursive subflows, execution, and worker notification.

- **C1:** The atomic notifier documents a lost-wakeup avoidance protocol: prepare to wait, recheck the predicate, and commit or cancel the wait. Its sequentially consistent fences coordinate predicate publication with waiter registration; the comments explain the dangerous case in which both sides miss an update. [Atomic notifier implementation](https://github.com/taskflow/taskflow/blob/master/taskflow/core/atomic_notifier.hpp).
- **C2:** Tasks can express explicit predecessor/successor relationships and create subgraphs dynamically. The same executor abstraction runs these decompositions, with profiling support for inspecting executions. [API examples and graph construction](https://github.com/taskflow/taskflow/blob/master/README.md).

### 3. [TheHPXProject/hpx](https://github.com/TheHPXProject/hpx)

**Language/role:** C++; asynchronous parallel and distributed runtime. This is the verified canonical repository; the former `STEllAR-GROUP/hpx` location redirects here. Study how standards-oriented application interfaces sit above configurable scheduling machinery.

- **C2:** HPX exposes futures, dataflow synchronization, parallel facilities, and local/remote operations through a common programming model. Its scheduler module separates thread-pool scheduling policies and points to resource-partitioner examples for selecting them. [Scheduler module guide](https://github.com/TheHPXProject/hpx/blob/master/libs/core/schedulers/docs/index.rst).
- **C3:** The local priority scheduler distinguishes priority queues, pending work, and staged work; it maintains victim-selection state and optional steal counters. Its creation path also handles NUMA placement hints. The implementation is useful for studying the cost of adding priorities and topology to a work-stealing runtime; placement behavior should be checked per operation, since some rescheduling paths explicitly ignore NUMA hints. [Local priority scheduler](https://github.com/TheHPXProject/hpx/blob/master/libs/core/schedulers/include/hpx/schedulers/local_priority_queue_scheduler.hpp).

### 4. [cmuparlay/parlaylib](https://github.com/cmuparlay/parlaylib)

**Language/role:** C++; shared-memory parallel algorithms with an integrated fork–join scheduler and allocator. Study the connection between higher-level sequence algorithms and their execution substrate.

- **C2:** Sequences, parallel algorithm primitives, nested parallelism, and allocation support form a reusable toolkit used by several graph and benchmark projects identified in the repository. [Project architecture and application links](https://github.com/cmuparlay/parlaylib/blob/master/README.md).
- **C1/C3:** The scheduler distinguishes ordinary worker idling from waiting at a join: join-related work searches must not time out and return prematurely. Its conservative waiting option addresses the deadlock risk of stealing a task that needs a lock held by the waiter. Elastic worker sleeping and randomized victim selection expose the accompanying CPU-use and responsiveness tradeoffs. [Scheduler implementation](https://github.com/cmuparlay/parlaylib/blob/master/include/parlay/scheduler.h).

### 5. [facebookincubator/dispenso](https://github.com/facebookincubator/dispenso)

**Language/role:** C++; compute-oriented thread pools, task sets, futures, and parallel algorithms. Study how explicit pool control and recursive task execution can be combined without requiring a compiler extension.

- **C2:** The library builds parallel loops, futures, task graphs, and task sets over a common pool abstraction, rather than exposing only a single parallel-loop helper. [Library overview](https://github.com/facebookincubator/dispenso/blob/main/README.md).
- **C1/C3:** The pool interface explains why related task abstractions steal while waiting for recursive work. Scheduling can execute inline when the pool is overloaded; bulk submission interleaves queuing and inline execution to control overhead. The code also separates polling from explicit wake signaling and documents shutdown and concurrent-resizing restrictions. [Thread-pool implementation and contracts](https://github.com/facebookincubator/dispenso/blob/main/dispenso/thread_pool.h).

### 6. [ConorWilliams/libfork](https://github.com/ConorWilliams/libfork)

**Language/role:** C++20; coroutine-based continuation stealing for strict fork–join computations. Study a portable coroutine design that separates task authoring from the scheduler and uses segmented stack storage to reduce allocation pressure.

- **C1/C3:** The lazy pool states a precise progress invariant: while any task is active, each NUMA locality must have a searching thief or no sleeping workers. Its transitions update active/thief counters and issue notifications to maintain that condition. This is unusually direct material for studying the correctness of energy-saving worker suspension. [Lazy pool and invariant commentary](https://github.com/ConorWilliams/libfork/blob/main/include/libfork/schedule/lazy_pool.hpp).
- **C2:** A small scheduler concept accepts resumable task handles, while context-switching awaitables permit explicit transfer to a scheduler. The contract requires a strong exception guarantee for submission. [Scheduler customization interface](https://github.com/ConorWilliams/libfork/blob/main/include/libfork/core/scheduler.hpp).

## Embedded and fiber-based task systems

### 7. [dougbinks/enkiTS](https://github.com/dougbinks/enkiTS)

**Language/role:** C++ implementation with C and C++ APIs; compact task and data-parallel scheduling for applications such as rendering engines. Study a relatively small runtime with explicit allocation and thread-placement controls.

- **C2:** Range tasks, pinned tasks, dependencies, configurable priorities, external-thread registration, allocator hooks, and profiler callbacks offer several reusable integration points. [Task interfaces and scheduler contracts](https://github.com/dougbinks/enkiTS/blob/master/src/TaskScheduler.h).
- **C1/C3:** Completion and dependency bookkeeping use separate atomic counters, while the range interface exposes grain size to avoid excessive partitioning. The project explicitly targets no allocations during scheduling and supports completion actions for task-lifetime management. These choices make ownership, dependency completion, and scheduling granularity concrete subjects for review. [Design goals and integration features](https://github.com/dougbinks/enkiTS/blob/master/README.md).

### 8. [google/marl](https://github.com/google/marl)

**Language/role:** C++11; hybrid thread/fiber task scheduler. **Archived**, as verified in GitHub metadata. Retained as a substantial architecture study.

- **C1:** Scheduler binding, unbinding, and destruction have explicit lifetime rules. Fibers remain associated with one worker thread; synchronization objects generally use shared internal state to avoid references outliving the submitting stack. The design document explains these choices and the queues for ready, waiting, and reusable fibers. [Scheduler internals](https://github.com/google/marl/blob/main/docs/scheduler.md).
- **C2/C3:** Blocking through Marl primitives suspends the fiber so a fixed worker-thread pool can execute other tasks. Ready fibers are resumed ahead of starting new tasks to limit further stack allocation. The application API includes events and wait groups, making this useful beyond a narrowly defined fork–join loop. [Usage and synchronization example](https://github.com/google/marl/blob/main/README.md).

### 9. [RichieSams/FiberTaskingLib](https://github.com/RichieSams/FiberTaskingLib)

**Language/role:** C++; fiber-backed execution of task graphs with arbitrary dependencies. Study the explicit handoff between waiting fibers, worker-local state, and priority task queues. GitHub's last-push metadata was March 2025; no claim of current release activity is made.

- **C1:** A ready fiber must not resume before the original thread has switched away from it. The scheduler checks `FiberIsSwitched`, refreshes thread-local state after migration, and coordinates the pinned-ready-fiber lock with sleeping to avoid missed wakeups. [Scheduler implementation](https://github.com/RichieSams/FiberTaskingLib/blob/master/source/task_scheduler.cpp).
- **C2/C3:** Counter-based dependency waits, task groups, priorities, and fiber-aware waiting permit application task graphs without blocking an OS thread for each dependency. The repository explains the API and includes a complete task-batch example. [Library guide](https://github.com/RichieSams/FiberTaskingLib/blob/master/README.asciidoc).

## Rust, OCaml, Nim, Haskell, and Julia

### 10. [rayon-rs/rayon](https://github.com/rayon-rs/rayon)

**Language/role:** Rust; parallel iterators, scoped tasks, fork–join execution, and customizable pools. Study the boundary between a safe application API and a sophisticated low-level scheduler.

- **C1/C3:** The sleep protocol uses packed worker counters and a jobs-event counter. Its design notes explicitly analyze counter rollover, externally injected jobs, and sequentially consistent fences needed to prevent every worker sleeping through new work. The document includes a proof sketch and explains why updating an event counter on every job was too expensive. [Sleep protocol](https://github.com/rayon-rs/rayon/blob/main/rayon-core/src/sleep/README.md).
- **C2/C4:** The API spans collection processing, manual task composition, and pools. Dated releases from 2016 through 2026 document compiler-version changes, compatibility-preserving renames, platform fallbacks, and correctness fixes, including invalid Unicode values in parallel character ranges. [Release history](https://github.com/rayon-rs/rayon/blob/main/RELEASES.md).

### 11. [crossbeam-rs/crossbeam](https://github.com/crossbeam-rs/crossbeam)

**Language/role:** Rust; the relevant subsystem is **`crossbeam-deque`**, a work-stealing data-structure library. The monorepo is counted once, and this entry does not describe a complete scheduler.

- **C1:** Queue ownership, atomic indices, buffer replacement, and epoch-based reclamation interact in an unsafe implementation derived from work-stealing and weak-memory research. The source also candidly documents a volatile-access workaround whose memory-model status deserves scrutiny; inclusion is not an endorsement of every unsafe detail. [Deque implementation](https://github.com/crossbeam-rs/crossbeam/blob/main/crossbeam-deque/src/deque.rs).
- **C2/C3:** Worker-owned FIFO/LIFO queues, shared steal handles, a global injector, and batch stealing support different scheduler policies. The API distinguishes an empty queue from a steal that must be retried, which is essential when composing a search loop. [Deque API and scheduler example](https://docs.rs/crossbeam/latest/crossbeam/deque/).

### 12. [ocaml-multicore/domainslib](https://github.com/ocaml-multicore/domainslib)

**Language/role:** OCaml; nested parallelism over domains using task pools, async/await, and parallel iterations. Study how algebraic-effect continuations participate in task suspension.

- **C1:** Promises atomically transition among pending, returned, and raised states. Waiter registration uses compare-and-set, completion resumes or discontinues stored continuations, and exception propagation preserves backtraces. The source states that a result may be set only once. [Task and promise implementation](https://github.com/ocaml-multicore/domainslib/blob/main/lib/task.ml).
- **C2/C3:** The same task machinery supports recursive spawning, parallel loops, reductions, scans, and search. Recursive range splitting and chunk-size selection give a compact example of controlling task overhead above a work-stealing pool. [Programming model and pool example](https://github.com/ocaml-multicore/domainslib/blob/main/README.md).

### 13. [mratsim/weave](https://github.com/mratsim/weave)

**Language/role:** Nim; experimental task runtime using message-based work requests. The checked repository last-push date was June 2024. Study an alternative to thieves directly modifying shared worker deques.

- **C2:** Spawn/sync futures and parallel loop operations expose nested parallelism while communicating through SPSC/MPSC channels. [Runtime overview and API](https://github.com/mratsim/weave/blob/master/README.md).
- **C3:** The design addresses adaptive stealing, lazy loop splitting, memory-pool pressure, and the code-size cost of specialization. It explicitly prioritizes total throughput over priority-driven latency or fairness. [Low-level design rationale](https://github.com/mratsim/weave/blob/master/weave/README.md).

The project's own warning limits the assurance claim: only one of two complex synchronization primitives was formally verified, and worker state machines were not. That limitation is material when considering production use.

### 14. [simonmar/monad-par](https://github.com/simonmar/monad-par)

**Language/role:** Haskell; deterministic parallel computations with IVars and interchangeable schedulers. Treat this as a historical implementation study: the checked last-push metadata was November 2023, not evidence of present maintenance.

- **C1:** The trace scheduler makes the IVar state machine explicit: empty, full, or holding blocked continuations. Atomic updates register readers and wake them on publication; a second put is an error. The same file exposes idle-worker coordination and shutdown. [Trace scheduler internals](https://github.com/simonmar/monad-par/blob/master/monad-par/Control/Monad/Par/Scheds/TraceInternal.hs).
- **C2:** `Par` computations are represented through operations such as fork, get, put, and yield, separating the computation interface from execution strategy. The repository contains several schedulers rather than binding the abstraction to one queue policy. [Scheduler implementations](https://github.com/simonmar/monad-par/tree/master/monad-par/Control/Monad/Par/Scheds).

The inspected trace scheduler uses a nonrandom victim scan and explicitly notes that traditional Cilk bounds should not be assumed for it.

### 15. [lehins/scheduler](https://github.com/lehins/scheduler)

**Language/role:** Haskell; reusable work-stealing scheduling for batches of actions, including per-worker state. This complements `monad-par` with an action-oriented API and explicit batch lifecycle controls.

- **C1:** Exceptions terminate workers and propagate to the scheduling thread. Internally, exception masking and cleanup preserve the original failure; worker-state reuse is guarded against concurrent acquisition, and batch identifiers distinguish cancellation requests for different batches. [Scheduler internals](https://github.com/lehins/scheduler/blob/master/scheduler/src/Control/Scheduler/Internal.hs).
- **C2:** The API supports worker IDs, pinned computation strategies, retained results, nested job submission, and reusable worker state. The guide distinguishes submission-order results from the less deterministic ordering created by nested scheduling. [Usage and exception semantics](https://github.com/lehins/scheduler/blob/master/scheduler/README.md).

### 16. [JuliaFolds2/FoldsThreads.jl](https://github.com/JuliaFolds2/FoldsThreads.jl)

**Language/role:** Julia; alternative executors for the JuliaFolds ecosystem. This is the repository's explicitly described **successor fork** of `JuliaFolds/FoldsThreads.jl`; the lineage is counted once. Its inspected code includes Julia 1.9 thread-ID compatibility handling. Last-push metadata was June 2023.

- **C2/C3:** `WorkStealingEx` supplies continuation stealing underneath reductions and transducers. Worker tasks are cached and reused so fine partitioning need not create a Julia task for every base case. [Executor design and API](https://github.com/JuliaFolds2/FoldsThreads.jl/blob/master/src/docs/WorkStealingEx.md).
- **C1:** The implementation coordinates cancellation contexts, promises, helper loops, and atomic arbitration between local continuation execution and another worker starting it. It is useful for understanding reduction-combination correctness. [Work-stealing implementation](https://github.com/JuliaFolds2/FoldsThreads.jl/blob/master/src/workstealing.jl).

The documentation calls this executor experimental, and the source still contains task-migration and thread-safety TODOs; it should be studied with those limits in view.

### 17. [JuliaParallel/Dagger.jl](https://github.com/JuliaParallel/Dagger.jl)

**Language/role:** Julia; task graphs across threads, processes, and accelerator processors. Study scheduling together with dependency tracking and data movement.

- **C1:** The current source documents a running-count invariant that credits newly ready work before decrementing completed work, avoiding a transient false zero. Per-task dependency counters, sealed dependent lists, weak references, and cleanup paths make lifetime and completion management substantial concerns. [Current scheduler implementation](https://github.com/JuliaParallel/Dagger.jl/blob/master/src/sch/Sch.jl).
- **C2/C3:** Processor scopes, occupancy, data-transfer costs, and load balancing connect a generic task interface to heterogeneous resources. Current code caches compatible processor sets and explains invalidation and object-identity safeguards. [Scheduler design guide](https://github.com/JuliaParallel/Dagger.jl/blob/master/docs/src/scheduler-internals.md).

The guide warns that it can lag implementation. In particular, current source says completion handlers schedule dependents without the central ready queue described by older portions of the guide; the source is the authority for that detail.

## C and C++ runtime research, locality, and HPC

### 18. [trolando/lace](https://github.com/trolando/lace)

**Language/role:** C; fine-grained fork–join runtime with split deques. Study how restricting thieves to a published portion of a deque can reduce interference with its owner.

- **C1:** The design describes task-slot states, publication and completion ordering, a shared tail/split word, and the fence needed when shrinking the shared region. It also explains leapfrogging: a worker awaiting stolen work tries to obtain work from that thief. [Design notes](https://github.com/trolando/lace/blob/master/docs/design.rst).
- **C2/C3:** A compact task API supports spawn/call/sync and worker coordination. Private versus shared deque regions, staged worker idling, NUMA-aware allocation, and per-worker scratch arenas address contention and allocation overhead through identifiable mechanisms. [Public task model](https://github.com/trolando/lace/blob/master/README.md).

### 19. [pmodels/argobots](https://github.com/pmodels/argobots)

**Language/role:** C; low-level threading/tasking framework with configurable execution streams, pools, and schedulers. Study an extensible runtime substrate rather than a single fixed task API.

- **C2:** A scheduler definition supplies initialization, run, and cleanup functions over a configurable list of pools. This makes scheduling policy separable from the work units and their storage. [Random work-stealing scheduler](https://github.com/pmodels/argobots/blob/main/src/sched/randws.c).
- **C3:** That implementation first attempts its own pool, then randomly selects another pool. Event-check frequency and optional sleeping let the runtime trade scheduling overhead against responsiveness. Owner-primary and owner-secondary pop contexts are explicit. The project supplies both a packaged test suite and examples for checking runtime configurations. [Testing and build configurations](https://github.com/pmodels/argobots/blob/main/README.md).

### 20. [sandialabs/qthreads](https://github.com/sandialabs/qthreads)

**Language/role:** C; lightweight user-level threads, full/empty-bit synchronization, and locality domains called shepherds. Study placement-aware scheduling and synchronization that suspends lightweight work units.

- **C1:** The Sherwood queue tracks total and stealable work separately, honors unstealable tasks, and coordinates queue links, lengths, and removal under its locking protocol. It illustrates the additional invariants introduced when some work cannot migrate. [Sherwood queue implementation](https://github.com/sandialabs/qthreads/blob/main/src/threadqueues/sherwood_threadqueues.c).
- **C3:** Affinity documentation explains how workers can be pinned and grouped by cache topology using hwloc, while the queue supports configurable steal chunks and pooled node allocation. This exposes locality and allocation choices alongside load balancing. [Affinity design](https://github.com/sandialabs/qthreads/blob/main/README.affinity).

### 21. [massivethreads/massivethreads](https://github.com/massivethreads/massivethreads)

**Language/role:** Primarily C, with C++ interfaces; lightweight user-level threads and work-stealing execution. **Historical research-oriented selection:** the README identifies its 2019 release and old tested platforms; checked last-push metadata was October 2024.

- **C1/C3:** The scheduler handles context switches, detached-thread cleanup, stack and descriptor reuse, and joining states. Its yield policies explicitly choose between local work and steals, while batched stack allocation and freelists address creation costs. [Scheduling and lifecycle implementation](https://github.com/massivethreads/massivethreads/blob/master/src/myth_sched_func.h).
- **C2:** Native, pthread-compatible, and TBB-like interfaces expose the runtime through different integration styles. The README documents a concrete compatibility lesson: removing automatic system-function wrapping because it caused problems, while acknowledging the resulting allocator-scalability tradeoff. [Interfaces and compatibility notes](https://github.com/massivethreads/massivethreads/blob/master/README.md).

### 22. [habanero-rice/hclib](https://github.com/habanero-rice/hclib)

**Language/role:** C/C++; finish–async, futures/promises, and locality-aware task execution. **Historical repository:** GitHub metadata reports the last push in July 2020. Its substantial runtime remains useful for studying resource-aware task scheduling; current maintenance is not claimed.

- **C2:** Finish scopes, parallel loops, and future-based dependencies are combined with modules that introduce resources such as GPU or communication execution. HClib positions itself as an intra-node scheduler that can integrate with inter-node communication systems. [Programming model and modules](https://github.com/habanero-rice/hclib/blob/master/README.md).
- **C1/C3:** Locality graphs describe hardware resources, while each worker has separate paths for finding its own work and stealing. The design explicitly identifies the deadlock risk when tasks are placed at locales no worker services. This is a concrete example of the tension between placement expressiveness and progress guarantees. [Locality graph architecture](https://github.com/habanero-rice/hclib/blob/master/inc/hclib-locality-graph.h).

### 23. [OpenCilk/cheetah](https://github.com/OpenCilk/cheetah)

**Language/role:** C/C++ runtime code; OpenCilk's compiler-coupled task runtime. Study continuation stealing at the compiler ABI boundary, where stack frames and runtime closures must cooperate. The inspected default branch is `dev`.

- **C1:** The scheduler has explicit closure ownership assertions, frame/fiber transfer rules at synchronization points, and memory-order constraints around the THE protocol's exception pointer. These are richer invariants than merely pushing and popping callable objects. [Scheduler implementation](https://github.com/OpenCilk/cheetah/blob/dev/runtime/scheduler.cpp).
- **C3:** Fiber storage uses worker-private pools plus a synchronized global pool, moving fibers in batches when local pools need replenishment or redistribution. This separates the common unsynchronized allocation path from cross-worker balancing. [Fiber-pool architecture](https://github.com/OpenCilk/cheetah/blob/dev/runtime/fiber-pool.cpp).

### 24. [ICLDisco/parsec](https://github.com/ICLDisco/parsec)

**Language/role:** Primarily C; PaRSEC's distributed, heterogeneous task-graph runtime. This is the parallel runtime, not an unrelated project named Parsec.

- **C2/C3:** Dynamic task discovery and parameterized task graphs provide different ways to represent computations. The latter allows a compact graph description queried on demand, while the runtime schedules with locality and data reuse in mind and overlaps communication with computation. [Programming model](https://github.com/ICLDisco/parsec/blob/master/README.rst).
- **C1:** The scheduler extension interface specifies when policies may be replaced and how per-execution-stream initialization is synchronized. It also defines a fairness requirement for tasks that request rescheduling: distance hints must prevent repeatedly selecting deferred work ahead of eligible work. [Scheduler interface and worked implementation](https://github.com/ICLDisco/parsec/blob/master/parsec/mca/sched/sched.h).

## Task scheduling inside standard language runtimes

### 25. [openjdk/jdk](https://github.com/openjdk/jdk)

**Language/role:** Java; specifically **`java.util.concurrent.ForkJoinPool` and its tests**, not the whole JDK. Study a work-stealing scheduler whose implementation must serve recursive tasks, externally submitted work, managed blocking, and a shared common pool.

- **C1/C3:** The implementation overview explains why arbitration occurs on queue slots, how promptly clearing references reduces garbage-collection retention, and how helping and compensation interact when workers block. It also documents the risk of unnecessary compensation causing oversubscription. [ForkJoinPool implementation overview](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/concurrent/ForkJoinPool.java).
- **C2:** The pool integrates the executor abstraction with fork–join tasks and configurable workers. Tests exercise recursive computations, worker-factory failures, managed blockers, submission, and lifecycle behavior; the testing notes also acknowledge why random steal-count observations are not portable assertions. [ForkJoinPool tests](https://github.com/openjdk/jdk/blob/master/test/jdk/java/util/concurrent/tck/ForkJoinPoolTest.java).

### 26. [dotnet/runtime](https://github.com/dotnet/runtime)

**Language/role:** C# for the relevant subsystem; **Task Parallel Library's default task scheduler and ThreadPool work queues**. Study the boundary between task semantics and the worker-pool implementation.

- **C1/C3:** Worker queues include local fast paths, synchronized resize/overflow paths, and steal arbitration. `TrySteal` explains why restoring the head index must become visible before another worker concludes the queue is empty. Dequeue policy distinguishes local, global, priority, and stolen work. [ThreadPool work queues](https://github.com/dotnet/runtime/blob/main/src/libraries/System.Private.CoreLib/src/System/Threading/ThreadPoolWorkQueue.cs).
- **C2:** The default task scheduler translates creation options into pool behavior, treats long-running tasks separately, and permits inline execution only after successfully removing an already queued task. Its comments distinguish execution from exception propagation by the waiting path. [ThreadPool task scheduler](https://github.com/dotnet/runtime/blob/main/src/libraries/System.Private.CoreLib/src/System/Threading/Tasks/ThreadPoolTaskScheduler.cs).

### 27. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language/role:** C/C++; specifically **OpenMP's `libomp` tasking runtime** under `openmp/runtime`. Counted once; the compiler and unrelated LLVM libraries are outside this entry.

- **C1:** A candidate steal must satisfy tied-task scheduling constraints and `mutexinoutset` dependencies. The runtime acquires dependency locks with rollback on failure, rechecks deque state under lock, and coordinates task completion with team progress. [Task scheduling implementation](https://github.com/llvm/llvm-project/blob/main/openmp/runtime/src/kmp_tasking.cpp).
- **C2/C3:** Per-thread deques, shared priority queues, and taskwait/taskgroup machinery implement reusable language-level task semantics while preserving separate execution paths for different task kinds. A focused regression test emulates compiler-generated detached tasks and verifies that `taskwait` waits for external event fulfillment. [Detached-task completion regression](https://github.com/llvm/llvm-project/blob/main/openmp/runtime/test/tasking/bug_taskwait_detach.cpp).

## Search coverage and limitations

Discovery used more than six meaningfully distinct live search formulations, including C++ graph/fork–join libraries; game-engine fiber systems; Rust queues and scoped tasks; OCaml/Nim/Haskell runtimes; Julia executors; C/HPC lightweight threads; Cilk and compiler runtimes; distributed heterogeneous scheduling; and Go/Zig/Swift/Kotlin alternatives. Follow-up searches specifically explored HClib/OmpSs, Haskell schedulers, and alternatives to the familiar Taskflow/Rayon/oneTBB group. Later searches mostly returned already represented projects, forks, examples, or broader asynchronous systems; HClib and `lehins/scheduler` were retained because they added distinct architectural material.

For retained entries, GitHub repository metadata verified canonical identities, branches, and archive flags. Repository trees located source files before citation; actual source or design documents, rather than search snippets alone, informed the criteria. The report follows HPX's repository redirect and counts the FoldsThreads successor lineage once. No retained project is being represented as an official mirror, and no unrelated fork is counted as an additional implementation.

Important boundaries and exclusions:

- Taskflow forks, its separately packaged work-stealing queue, and the superseded `pbbslib` were not counted as independent additions to already represented implementations.
- Tutorial schedulers, small benchmark-only artifacts, generic thread-pool wrappers, and numerical application repositories were excluded. Stars were not used as evidence for the criteria.
- Broader async/I/O ecosystems such as Tokio, Kotlin coroutines, and Swift concurrency were considered during discovery but left outside this selection's main emphasis on compute-task libraries. Go/Zig searches produced relevant experiments and broader async runtimes, but no additional entry was necessary to represent a distinct, sufficiently inspected architecture here.
- OmpSs-related material surfaced in discovery, but this report does not claim to have verified the canonical GitHub maintenance/mirror status of its runtime implementations. They were not retained on the strength of documentation or third-party copies alone.
- Status observations distinguish an archived repository from a quiet or historical one. Push dates provide context only; they are not C4 evidence. The strongest explicit C4 claim here is backed by Rayon's dated release history and compatibility/correctness work.
- This was read-only source research: no candidate dependencies were installed, no candidate code was executed, and no benchmark or correctness result was independently reproduced. Performance discussion therefore describes mechanisms and documented tradeoffs, not comparative speed claims. Judgments about what an engineer can learn are grounded interpretations of the cited material.
