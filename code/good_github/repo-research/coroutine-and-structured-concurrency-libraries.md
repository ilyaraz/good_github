# Coroutine and structured concurrency libraries

Research date: **2026-10-09**

This selection covers 25 GitHub repositories implementing coroutine primitives, cooperative task runtimes, or reusable structured concurrency abstractions. It spans stackful coroutines, compiler-generated state machines, effect-based fibers, lexical task groups, and process supervision. A coroutine library does not necessarily enforce structured concurrency: entries distinguish mandatory lifetime rules from optional grouping APIs and caller-managed cleanup. Broad repositories are included only for the named subsystem and counted once.

The criteria describe reasons to study the code, not a certification of correctness or a blanket recommendation to adopt every project:

- **C1 — Difficult correctness:** concurrency invariants, cancellation, resource lifetime, exception propagation, or other demanding failure modes.
- **C2 — Reusable abstractions:** substantial primitives that compose across applications and use cases.
- **C3 — Performance with structure:** concrete allocation, scheduling, latency, or execution-cost tradeoffs explained by the architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, and complexity management; age alone does not qualify.

## Python: nurseries, task groups, and distributed lifetimes

### 1. [python-trio/trio](https://github.com/python-trio/trio)

**Language/role:** Python; async I/O runtime organized around nurseries and cancellation scopes.

Study how API semantics constrain a scheduler. Trio deliberately aligns ordinary scheduling and cancellation checkpoints so programmers can reason about where another task may run and where cleanup must tolerate cancellation.

- **C1:** Children must finish before their nursery exits, and exceptions propagate through the task tree. The design also explains why inconsistent checkpoint behavior can cause starvation or ineffective timeouts. These are explicit semantic invariants, not merely convenience functions. [Design and internals](https://trio.readthedocs.io/en/stable/design.html).
- **C2:** A public low-level API supports higher-level locks, sockets, testing tools, and third-party extensions. The same design document explains the enforced boundary between scheduling/cancellation/I/O in `trio._core` and abstractions built above it.
- **C3:** The design prioritizes worst-case algorithmic behavior and tail latency, and explains the separate epoll, kqueue, and Windows I/O managers. This is useful performance reasoning without relying on throughput claims.

### 2. [agronholm/anyio](https://github.com/agronholm/anyio)

**Language/role:** Python; structured concurrency and I/O abstractions over asyncio and Trio.

AnyIO is especially useful for studying how one semantic contract can be implemented over backends with different native cancellation behavior.

- **C1:** Its cancellation guide distinguishes asyncio's edge cancellation from repeated, level-triggered cancellation inside AnyIO scopes. It explains shielding asynchronous cleanup, effective deadlines, and how cancellation-unaware synchronization code can busy-wait. [Cancellation and timeouts](https://anyio.readthedocs.io/en/stable/cancellation.html).
- **C2:** Task groups, nested cancellation scopes, byte/object streams, synchronization, worker execution, subprocesses, and testing integration provide a common application-facing layer across two runtimes. This is substantive semantic adaptation rather than a generated wrapper; the cancellation guide shows the behavioral differences it must reconcile.

### 3. [dabeaz/curio](https://github.com/dabeaz/curio)

**Language/role:** Python; independent coroutine runtime and task-group library. **Archived repository**, retained as a historical design reference.

Study a comparatively direct implementation of task bookkeeping, termination, result collection, and policy-driven groups. Curio is also useful for comparing task-group error reporting with Trio's nursery model.

- **C1:** `Task.cancel()` distinguishes requesting cancellation from waiting for termination. `TaskGroup` tracks running, completed, and daemon tasks, rejects invalid membership changes, and cancels remaining tasks when a member fails. Errors are also observable through result retrieval; do not assume precisely Trio's propagation behavior. [Task and TaskGroup implementation](https://github.com/dabeaz/curio/blob/master/curio/task.py).
- **C2:** The group abstraction supports waiting for all tasks, the first completion, or the first non-`None` result, as well as completion-order iteration and adopting existing tasks. The same source contains the API contracts and their implementation.

### 4. [goodboy/tractor](https://github.com/goodboy/tractor)

**Language/role:** Python; structured concurrency across actor processes, built on Trio. The repository describes several subsystems as **alpha/near-beta**.

Study what changes when a nursery owns OS processes rather than only in-process tasks: errors require serialization, cancellation needs an IPC protocol, and termination includes reaping children.

- **C1:** Actor nurseries supervise nested process lifetimes; remote errors return as `RemoteActorError`, and cancellation requests are acknowledged across process boundaries. The documented shutdown sequence includes escalation and reaping. These are intended runtime guarantees, not an independently verified absence of orphan-process bugs. [Distributed concurrency semantics](https://github.com/goodboy/tractor/blob/main/docs/explain/sc-distributed.rst).
- **C2:** `ActorNursery`, `Portal`, `Context`, and `MsgStream` separate spawning, remote calls, linked task lifetimes, and bidirectional streaming. The architecture explains per-actor Trio runtimes, typed message transports, and interchangeable process-spawn backends. [Runtime architecture](https://github.com/goodboy/tractor/blob/main/docs/explain/architecture.rst).

## JVM and functional runtimes

### 5. [Kotlin/kotlinx.coroutines](https://github.com/Kotlin/kotlinx.coroutines)

**Language/role:** Kotlin; multiplatform coroutine library with jobs, scopes, dispatchers, channels, and flows.

The main study target is the connection between a broad public concurrency API and a carefully optimized job lifecycle. The repository covers both ordinary parent-child cancellation and supervision alternatives.

- **C1:** `JobSupport` documents its state machine and notification order: cancellation reaches children, completion waits for children, exception collection becomes sealed, and final completion detaches the parent handle. Races between registration, cancellation, and completion are central concerns. [JobSupport implementation](https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-core/common/src/JobSupport.kt).
- **C2:** Jobs and deferred results compose with scope builders, channels, flow operators, synchronization, platform dispatchers, and test schedulers rather than serving a single application domain.
- **C3:** The state machine explicitly optimizes the common successful job with zero or one completion listener, avoiding a full finishing-state transition when possible. The [changelog](https://github.com/Kotlin/kotlinx.coroutines/blob/master/CHANGES.md) additionally gives concrete examples of compatibility repairs and simultaneous emitter/subscriber cancellation bugs.

### 6. [typelevel/cats-effect](https://github.com/typelevel/cats-effect)

**Language/role:** Scala; effect runtime and reusable cancellation, resource, and fiber abstractions.

Study how a fiber interpreter can move between threads while retaining a tractable memory-visibility argument, and how lifetime management is layered above raw fiber spawning.

- **C1:** `IOFiber` explains why only one thread owns its run loop, how atomic suspension and executor handoffs publish state, and how cancellation takes over a suspended fiber to run finalizers. [IOFiber implementation](https://github.com/typelevel/cats-effect/blob/series/3.x/core/shared/src/main/scala/cats/effect/IOFiber.scala).
- **C2:** `Supervisor` binds fibers to a `Resource` lifetime and supports either waiting for completion or canceling at finalization. Its documentation distinguishes this from unmanaged `start` and parent-bound `background`. [Supervisor guide](https://typelevel.org/cats-effect/docs/std/supervisor).
- **C3:** The run loop uses array-backed continuation stacks and carefully placed barriers, with explicit cancellation-check and automatic-yield thresholds. The source explains why these optimizations preserve its ownership model.

### 7. [zio/zio](https://github.com/zio/zio)

**Language/role:** Scala; typed effects, fibers, scopes, and concurrent combinators.

ZIO offers a useful comparison with Cats Effect: fiber parentage and interruption are prominent runtime concepts, while typed success and error channels shape composition.

- **C1:** The runtime coordinates interruption messages, a single running-state gate, observers, and child registration. For example, adding a child to an already interrupted or completed parent must not leave that child unsupervised. [FiberRuntime implementation](https://github.com/zio/zio/blob/series/2.x/core/shared/src/main/scala/zio/internal/FiberRuntime.scala).
- **C2:** Typed fibers support joining and concurrent combinators such as parallel traversal and racing. Normal child lifetimes are bound to parents, while daemon and explicitly scoped forking provide deliberate alternatives. [Fiber and lifetime guide](https://zio.dev/reference/fiber/).
- **C3:** The implementation includes cooperative-yield accounting and an interruption fast path that can drain work on the current executor thread, making the costs of responsiveness and context switching inspectable.

### 8. [kilim/kilim](https://github.com/kilim/kilim)

**Language/role:** Java; bytecode weaving plus a cooperative fiber runtime. **Historical JVM coroutine approach**; the README's compatibility discussion concerns older JDK generations and should not be read as a current-JDK support guarantee.

Study continuation transformation without language-level coroutine syntax. Kilim separates the weaver from runtime tasks, mailboxes, generators, and scheduling.

- **C1:** The weaver adds fiber state to pausable methods while preserving local-variable slots, stack requirements, method metadata, and exception-handler behavior. Its special handling of pausable blocks and catch handlers exposes the correctness burden of transforming ordinary bytecode into resumable execution. [MethodWeaver implementation](https://github.com/kilim/kilim/blob/master/src/kilim/analysis/MethodWeaver.java).
- **C2:** The transformed methods support reusable continuations, tasks, actors, mailboxes, and generators, with both ahead-of-time and runtime weaving options described in the repository.

Kilim belongs here as a coroutine implementation, not as a nursery system: its README explicitly says task cancellation is not directly supported.

## C and C++: lifetime machinery and coroutine building blocks

### 9. [hudson-trading/corral](https://github.com/hudson-trading/corral)

**Language/role:** C++20; cooperative, single-threaded structured concurrency independent of a particular I/O loop.

Study how to offer nursery semantics in a language without asynchronous destructors, while integrating with existing callback-based systems.

- **C1:** The nursery implementation waits for children even after cancellation, cancels siblings on failure, and propagates the first error. Its documentation explicitly warns that locals inside the nursery-body coroutine can die before sibling tasks, so shared data must have an enclosing lifetime. [Nursery implementation and contract](https://github.com/hudson-trading/corral/blob/master/corral/Nursery.h).
- **C2:** Nurseries accept generic awaitables, support child-start acknowledgments, and allow alternative error policies. The library's event-loop independence and callback bridges make these mechanisms useful with Asio and other existing I/O systems.

The single-threaded execution assumption is part of its design contract; separate thread-local instances are not permission to share tasks across threads.

### 10. [lewissbaker/cppcoro](https://github.com/lewissbaker/cppcoro)

**Language/role:** C++; foundational coroutine abstractions targeting the **Coroutines TS**. Treat this as a historical/reference implementation; the checked GitHub metadata reports its last push in January 2024, not evidence of ongoing maintenance.

Study small implementations of lazy tasks, shared tasks, generators, async synchronization, schedulers, and composition functions.

- **C1:** `async_scope` combines an atomic outstanding-work count with a suspended continuation. Joining must happen before destruction, and the final task must resume the joiner with appropriate memory ordering. Its internal detached task terminates on an unhandled exception, an important semantic limit. [async_scope implementation](https://github.com/lewissbaker/cppcoro/blob/master/include/cppcoro/async_scope.hpp).
- **C2:** The repository documents a large, reusable vocabulary including `task`, `shared_task`, async generators, cancellation tokens, synchronization primitives, `when_all`, and scheduling adapters.

Compiler and platform instructions reflect the TS-era implementation; do not assume it is interchangeable with every contemporary C++20 coroutine library.

### 11. [boostorg/cobalt](https://github.com/boostorg/cobalt)

**Language/role:** C++20; coroutine types and composition integrated with Boost.Asio.

Study a library that makes explicit choices about eager promises, lazy tasks, generators, execution contexts, and direct handoff between channel participants.

- **C1:** Racing has precise semantics for interrupting an outstanding wait versus requesting cancellation. The contract for `interrupt_await` requires synchronous resumption before it returns; ordered `left_race` is documented as potentially starving later alternatives. [Race semantics](https://github.com/boostorg/cobalt/blob/develop/doc/reference/race.adoc).
- **C2:** Tasks adapt Asio completion-token APIs into awaitable values, while the surrounding library supplies promises, generators, channels, and composition. [Task and Asio adapter implementation](https://github.com/boostorg/cobalt/blob/develop/include/boost/cobalt/task.hpp).
- **C3:** The repository explains that channels can transfer control directly instead of routing every handoff through an executor. Its usual single-threaded `io_context` assumption makes that optimization intelligible.

Coroutine ownership and race behavior depend on the particular type and operation; Cobalt is not described here as imposing a universal nursery rule.

### 12. [boostorg/coroutine2](https://github.com/boostorg/coroutine2)

**Language/role:** C++11 and later; stackful asymmetric coroutines over Boost.Context.

This is a distinct implementation family from C++20 promise-based coroutines. Study paired push/pull control transfer, separately allocated stacks, value storage, and unwinding across suspended execution.

- **C1:** The control block preserves exceptions for rethrowing at the caller, specially rethrows forced-unwind exceptions, and coordinates stack destruction with destruction of the yielded value. [Pull control-block implementation](https://github.com/boostorg/coroutine2/blob/develop/include/boost/coroutine2/detail/pull_control_block_cc.ipp).
- **C2:** Typed push/pull coroutines expose reusable producer/consumer control flow, including value and reference forms and customizable stack allocation. [Asymmetric coroutine documentation](https://www.boost.org/doc/libs/latest/libs/coroutine2/doc/html/coroutine2/coroutine/asymmetric.html).

It supplies coroutine control flow rather than a task scheduler or automatic structured task tree. The repository identifies it as the successor to the deprecated Boost.Coroutine library.

### 13. [jbaldwin/libcoro](https://github.com/jbaldwin/libcoro)

**Language/role:** C++20; coroutine primitives, executors, task groups, and asynchronous networking.

Study integration of generic executor concepts with task ownership and coroutine-aware synchronization. The README also discusses thread migration across `co_await` and the lifetime hazards of coroutine lambda captures.

- **C1:** `task_group` tracks active tasks atomically and signals an event on the transition to empty. It documents the hazard of awaiting emptiness before all producers have finished adding work. Its destructor blocks the calling thread until tasks finish, so asynchronous joining is the intended efficient path. [Task-group implementation](https://github.com/jbaldwin/libcoro/blob/main/include/coro/task_group.hpp).
- **C2:** Tasks, generators, events, locks, semaphores, queues, groups, thread pools, and I/O scheduling form a general toolkit rather than a single server framework.
- **C3:** The design offers inline I/O task processing or a thread pool for different execution costs, while the task-group source makes the cost of synchronous destruction explicit.

### 14. [facebook/folly](https://github.com/facebook/folly)

**Language/role:** C++; the relevant subsystem is **`folly/coro`**, not the whole utility collection.

Study coroutine integration with an established executor and future ecosystem. Folly's notion of executor stickiness is especially useful when comparing libraries that freely resume on completion threads.

- **C1:** `AsyncScope` requires asynchronous joining or cleanup before destruction and documents races between adding tasks and completing cleanup. Its ordinary error-handling policy is not Trio-style automatic sibling failure propagation; submitted tasks are expected to handle errors, with a configurable join behavior. [AsyncScope implementation](https://github.com/facebook/folly/blob/main/folly/coro/AsyncScope.h).
- **C2:** `Task`, concurrent collection, partial-failure handling, and `SemiFuture` bridges compose with the rest of Folly. The guide explains executor inheritance and explicitly moving child work to another executor. [Coroutine subsystem guide](https://github.com/facebook/folly/blob/main/folly/coro/README.md).

### 15. [sustrik/libdill](https://github.com/sustrik/libdill)

**Language/role:** C; cooperative coroutines, handles, bundles, and structured lifetime discipline. **Historical structured concurrency reference**; checked GitHub metadata shows a last push in April 2024, so no active-maintenance claim is made.

Study how a C API can make cancellation and cleanup composable without exceptions or asynchronous destructors.

- **C1:** Closing a coroutine handle makes its blocking calls fail with `ECANCELED`, allowing cleanup before termination. Crucially, the documentation says structured lifetimes must be arranged manually through handle ownership. [Structured concurrency design](https://sustrik.github.io/libdill/structured-concurrency.html).
- **C2:** Bundles group coroutines behind a handle and provide a deadline-aware wait. The implementation connects these abstractions to a ready queue, cancellation clauses, and timer structures. [Coroutine and bundle implementation](https://github.com/sustrik/libdill/blob/master/cr.c).

The cooperative model cannot rescue a coroutine that indefinitely avoids yielding or blocking. That limitation follows directly from the documented scheduling model.

## Rust and OCaml: ownership, promises, and effects

### 16. [tokio-rs/tokio](https://github.com/tokio-rs/tokio)

**Language/role:** Rust; asynchronous runtime, with **task ownership and `JoinSet`** as the relevant study area.

Study the difference between requesting task cancellation and observing completed destruction. Tokio supports structured task management, but ordinary spawning does not automatically construct a lexical nursery.

- **C1:** A `JoinSet` owns a dynamic collection of tasks; dropping it requests abortion, while `shutdown()` aborts and then drains completions. These are different lifetime guarantees. [JoinSet implementation](https://github.com/tokio-rs/tokio/blob/master/tokio/src/task/join_set.rs).
- **C2:** The collection supports completion-order results, explicit runtime selection, local tasks, and blocking-task integration. The underlying typed join handle captures return values and panics and specifies cancellation safety when awaited by reference. [JoinHandle implementation and contract](https://github.com/tokio-rs/tokio/blob/master/tokio/src/runtime/task/join.rs).

Dropping an ordinary `JoinHandle` detaches its task. Already running `spawn_blocking` work cannot be aborted in the same way as an async task; neither exception should be hidden behind a blanket structured-concurrency claim.

### 17. [najamelan/async_nursery](https://github.com/najamelan/async_nursery)

**Language/role:** Rust; executor-independent nursery built around managed join handles.

This smaller project is useful for studying how much structured task ownership can be added above an existing executor without implementing another runtime.

- **C1:** The result stream owns cancel-on-drop handles and completes only after incoming handles are exhausted and all tracked tasks finish. Leaving a nursery sender open therefore prevents completion. The implementation makes this closure invariant visible. [NurseryStream implementation](https://github.com/najamelan/async_nursery/blob/dev/src/nursery_stream.rs).
- **C2:** Separate spawning and result-stream objects support local and sendable futures, executor traits, stream consumption, and joining without retaining results. An unbounded channel feeds handles into `FuturesUnordered`. [Nursery implementation](https://github.com/najamelan/async_nursery/blob/dev/src/nursery.rs).

The README explicitly excludes built-in cooperative cancellation and non-`'static` futures. Forwarded blocking-task spawning is also outside nursery ownership. These limits distinguish it from lexical borrowing scopes or asynchronous cleanup systems.

### 18. [ocaml-multicore/eio](https://github.com/ocaml-multicore/eio)

**Language/role:** OCaml 5; effects-based direct-style fibers, I/O, and resource scopes.

Study a switch that owns both child fibers and resources. Eio connects effect handlers and cancellation contexts to an API where possession of a switch grants the ability to create longer-lived work.

- **C1:** The switch implementation checks domain ownership, combines failures, cancels children, waits for the fiber count to reach zero, and then runs protected release handlers. It accounts separately for daemon fibers and rechecks work created during release. [Switch implementation](https://github.com/ocaml-multicore/eio/blob/main/lib_eio/core/switch.ml).
- **C2:** Switches, fibers, streams, promises, network/file interfaces, and mock backends compose into a general I/O library. The repository's extensive guide explains how `Switch.run` bounds the lifetime of fibers and attached resources and how capability passing controls access.

The domain checks are meaningful constraints: a switch is not an unrestricted shared synchronization object across OCaml domains.

### 19. [ocsigen/lwt](https://github.com/ocsigen/lwt)

**Language/role:** OCaml; promise-based cooperative concurrency and I/O.

Lwt supplies the monadic/lightweight-thread counterpart to Eio's effect-based design. It is included for its coroutine-style sequencing and cancellation machinery, not as a claim that every spawned computation has a lexical parent.

- **C1:** The core describes immutable resolved promises, pending callback graphs, cancellation as a special rejection path, and ordering cancellation callbacks before ordinary callbacks. Its resolution machinery must also avoid stack overflow during cascades of completions. [Core implementation and reading guide](https://github.com/ocsigen/lwt/blob/master/src/core/lwt.ml).
- **C2:** Sequential `bind`, concurrent joining/choice, resolvers, cancellation, and sequence-associated storage form reusable composition mechanisms for the surrounding I/O library. The same source carefully separates these mechanisms into documented internal modules.

This is a particularly approachable large implementation file because its overview maps semantic concepts to the internal organization rather than merely listing public functions.

## JavaScript, Ruby, .NET, Haskell, and Go

### 20. [thefrontside/effection](https://github.com/thefrontside/effection)

**Language/role:** TypeScript/JavaScript; generator-based operations, scopes, tasks, and effect handling. Sources inspected are on the repository's **`v4` branch**.

Study structured lifetimes built from JavaScript generators rather than native `async` functions. The scope implementation is small enough to inspect as a unit while supporting integration into larger applications.

- **C1:** Scope destruction is signaled once, repeated destroy requests await a shared future, parent cleanup registers child destruction, and destructors run in reverse batches while preserving a failure outcome. [Scope internals](https://github.com/thefrontside/effection/blob/v4/lib/scope-internal.ts).
- **C2:** Scopes expose task execution, spawning, inherited contexts, and integration with explicit asynchronous resource disposal. `createScope` bridges framework ownership to operations and provides an asynchronous destruction API. [Public scope API](https://github.com/thefrontside/effection/blob/v4/lib/scope.ts).

The version-specific branch matters: older Effection guides describe earlier APIs and should not be silently combined with v4 source contracts.

### 21. [socketry/async](https://github.com/socketry/async)

**Language/role:** Ruby; fiber-based I/O runtime with hierarchical tasks.

Study how Ruby's fiber scheduler is connected to task state, result observation, cancellation causes, and a traversable ownership tree.

- **C1:** Task construction initializes state before publishing the task into its parent's graph. The tree distinguishes ordinary children from transient children, and cancellation propagates through non-transient descendants. Transient nodes can survive parent consumption through reparenting, so the lifecycle model has explicit exceptions. [Task implementation](https://github.com/socketry/async/blob/main/lib/async/task.rb), [task-tree implementation](https://github.com/socketry/async/blob/main/lib/async/node.rb).
- **C2:** Tasks provide reusable child spawning, waiting, timeouts, state inspection, and annotations above the scheduler. The task tree supports both application work and internal maintenance activity.
- **C3:** Child tasks execute immediately until their first blocking operation. The source explains the goals: deterministic initial execution, early error detection, and avoiding scheduling overhead for work that never blocks.

### 22. [Cysharp/UniTask](https://github.com/Cysharp/UniTask)

**Language/role:** C#; task-like async/await and coroutine integration for Unity, plus a smaller non-Unity subset.

Study a concurrency library shaped by frame-loop scheduling and allocation pressure rather than server-thread scheduling. This is coroutine integration with explicit cancellation tokens, not automatic nursery semantics.

- **C1:** The README documents lifecycle-bound cancellation, propagation of cancellation and unobserved errors, and the distinction between checking cancellation during a player-loop tick and registering for immediate cancellation. Player-loop injection order and loop replacement by other Unity systems are also concrete failure modes.
- **C2:** Awaitable Unity operations, timing primitives, task composition, async enumerables, and .NET bridges provide a broad vocabulary for game and UI workflows.
- **C3:** The pool implementation uses reusable linked nodes, an interlocked gate, configurable size limits, and pool-size observation. This makes the allocation strategy inspectable; it does not justify claiming every possible operation allocates nothing. [TaskPool implementation](https://github.com/Cysharp/UniTask/blob/master/src/UniTask/Assets/Plugins/UniTask/Runtime/TaskPool.cs).

### 23. [simonmar/async](https://github.com/simonmar/async)

**Language/role:** Haskell; scoped asynchronous actions over lightweight runtime threads.

Study an unusually compact structured concurrency design: lexical scope and exception safety are added above existing thread primitives, with results exposed through STM.

- **C1:** `withAsync` masks vulnerable setup, restores normal execution for the body, and cancels the child on both exceptional and ordinary scope exit. Results and exceptions are recorded in a transactional variable. [Internal implementation](https://github.com/simonmar/async/blob/master/Control/Concurrent/Async/Internal.hs).
- **C2:** `concurrently`, `race`, parallel traversal, STM wait operations, and the `Concurrently` applicative compose the same abstraction for different task arrangements. The public module explains why lower-level `async` alone can leak work when a later wait is skipped by an exception. [Public API and design explanation](https://github.com/simonmar/async/blob/master/Control/Concurrent/Async.hs).

The internal module is explicitly outside the public versioning contract. Unbounded parallel traversal also does not remove application resource limits.

### 24. [golang/sync](https://github.com/golang/sync)

**Language/role:** Go; **`errgroup` subsystem** in the official substantive GitHub mirror of [Go's sync repository](https://go.googlesource.com/sync).

Study how a small coordination abstraction can impose a shared error and cancellation boundary on goroutines. The repository is counted once; its other synchronization packages are not separate entries.

- **C1:** `WithContext` cancels on the first task error or after `Wait`; `Wait` still waits for all submitted functions. A `sync.Once` protects the first error, and the implementation explicitly explains why panics are not converted into deferred errors. [errgroup implementation](https://github.com/golang/sync/blob/master/errgroup/errgroup.go).
- **C2:** The same group supports fan-out, result aggregation, bounded task admission, and nonblocking `TryGo`. Tests exercise cancellation causes, zero-value behavior, and concurrency limits. [Tests and usage examples](https://github.com/golang/sync/blob/master/errgroup/errgroup_test.go).

Structured use requires calling `Wait` and having work observe the derived context; a group does not forcibly terminate arbitrary goroutines.

## Low-level stack-switching substrate

### 25. [python-greenlet/greenlet](https://github.com/python-greenlet/greenlet)

**Language/role:** C++/C and Python; stackful coroutine substrate for CPython.

Study the boundary between coroutine semantics and interpreter internals. Greenlet supplies explicit control transfer rather than a scheduler, cancellation scope, or nursery.

- **C1:** Switching preserves Python and exception state as well as native stack contents. The implementation discusses garbage collection causing reentrant switches, invalid thread ownership, failed stack transfers, and destruction of suspended greenlets. [Greenlet switching implementation](https://github.com/python-greenlet/greenlet/blob/master/src/greenlet/TGreenlet.cpp).
- **C2:** The reusable switching primitive can support synchronous-looking control flow and higher-level concurrency runtimes without requiring Python `async` syntax. Its ownership checks keep greenlets tied to their originating thread.
- **C4:** The changelog documents 2023 fixes for reentrant switching and CPython 3.12 compatibility, followed by 2025–2026 work on newer CPython versions, free-threaded builds, garbage-collection races, shutdown crashes, and platform packaging. This is sustained compatibility and failure-mode management, not merely an old creation date. [Change history](https://github.com/python-greenlet/greenlet/blob/master/CHANGES.rst).

## Coverage, search method, and limitations

Discovery used more than six distinct live search formulations, including general nursery/cancellation terminology; C++20 task scopes; Kotlin and Java fibers; Python Trio/AnyIO/Curio; Rust executor-independent nurseries; OCaml effects and promises; Scala and Haskell scoped effects; JavaScript and Ruby task lifetimes; C coroutine libraries; Unity player-loop tasks; Go error groups; and Swift structured concurrency. Later searches increasingly returned already represented mechanisms, language-runtime implementations, tutorials, or narrowly overlapping libraries. The selection therefore stops at 25 rather than treating the count as a quality target.

Every repository heading was verified through an opened GitHub repository page or the public GitHub repository API. Every entry also has an independently read primary source beyond that repository's root README, and at least one substantive implementation or architectural source. Several GitHub API requests encountered the unauthenticated rate limit; repository pages supplied the remaining canonical checks. Failed documentation paths were replaced with readable source-tree material and are not cited. Links to branches and `stable`/`latest` documentation can evolve after the research date.

The selection includes established ecosystems and smaller implementations such as Corral, async_nursery, libdill, and tractor. It does not rank by stars. Pure event loops, general thread pools, reactive-only systems, tutorial projects, generated wrappers, proposal-only repositories, and fork variants without separately established implementation value were excluded. Swift's native task system and Java's JDK concurrency facilities were treated as language/runtime scope rather than separate library selections. Libaco, libmill, and additional C++ coroutine libraries were discovery candidates but are not claimed to have failed the criteria; this is a diverse selection, not an exhaustive census.

Maintenance claims are intentionally narrow: Curio's archive status was verified, cppcoro and libdill are labeled as historical references, Kilim's older compatibility context is explicit, and `golang/sync` is identified as an official mirror. No code from these repositories was executed and no benchmarks were reproduced. Statements about what an engineer can learn are editorial inferences from the cited designs and implementations; documented contracts are not proof that every implementation path satisfies them. A project can be valuable to study while retaining sharp edges or semantics unsuitable for a particular application.
