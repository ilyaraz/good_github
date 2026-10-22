# Actor runtimes and supervision frameworks

Research date: **2026-10-09**.

This guide selects 25 GitHub repositories implementing actor execution, messaging, virtual actors, or reusable supervision. It covers complete language runtimes, actor libraries, and supervision-only frameworks. For larger repositories, the relevant subsystem is identified. These systems make different promises about restart, message delivery, cancellation, identity, and state recovery; those differences are central to their educational value.

The criterion assessments below are grounded engineering judgments drawn from the linked implementation and documentation. Inclusion is a selection recommendation for study, not a claim that every component is exemplary or suitable for a particular production deployment.

**Criteria legend**

- **C1 — Correctness:** difficult invariants, concurrency, ordering, failure handling, or adversarial conditions.
- **C2 — Abstractions:** substantial reusable interfaces or architectural mechanisms supporting varied applications.
- **C3 — Performance:** explicit resource, scheduling, throughput, or latency constraints addressed through understandable structure.
- **C4 — Evolution:** sustained development supported by concrete compatibility, testing, or complexity-management evidence.

## BEAM foundations and typed supervision

### [erlang/otp](https://github.com/erlang/otp)

**Language / role:** Erlang and C; BEAM runtime and OTP libraries, especially the standard supervisor behavior.

Study the precise contract between a supervisor and its children: dependency-sensitive startup, reverse shutdown, restart classification, and escalation. OTP is especially useful for understanding why restart policy is part of application architecture rather than a generic retry loop.

- **C1:** Restart intensity and period bound failure storms. The documentation also explains how a finite shutdown timeout for a child supervisor can create an orphaning race, and why waiting indefinitely is normally appropriate for that case.
- **C2:** Child specifications separate factories, restart policy, shutdown behavior, and worker/supervisor identity. The same behavior supports independent children, dependency chains, and nested supervision trees through different strategies.

**Entry point:** [Supervision principles](https://www.erlang.org/doc/system/sup_princ.html), including restart strategies, shutdown ordering, and automatic shutdown compatibility notes.

### [elixir-lang/elixir](https://github.com/elixir-lang/elixir)

**Language / role:** Elixir; standard-library supervision abstractions built on Erlang/OTP. The relevant subsystem is `DynamicSupervisor` and its interaction with `PartitionSupervisor`, rather than a separate actor VM.

This is a useful study of how a language library exposes lifecycle management while acknowledging the costs of serialized coordination. Dynamic child creation is particularly relevant to connection handlers, jobs, and other populations whose membership changes at runtime.

- **C2:** `DynamicSupervisor` provides reusable lifecycle management for children created on demand. Its API separates child creation from application-specific worker behavior.
- **C3:** Child startup runs through a single supervisor process, which can become a bottleneck. The guide shows partitioning that work among multiple supervisors and routing requests through `PartitionSupervisor`; this is a concrete architectural response to contention, with an explicit routing choice.

**Entry point:** [DynamicSupervisor guide and scalability discussion](https://elixir.hexdocs.pm/DynamicSupervisor.html).

### [gleam-lang/otp](https://github.com/gleam-lang/otp)

**Language / role:** Gleam; typed actors and supervision APIs on the BEAM.

Study how typed message subjects, actor state, initialization, and termination are presented over OTP facilities. This is a substantive language-level abstraction layer: its static supervisor uses Erlang/OTP underneath, so it should not be mistaken for an independently implemented scheduler.

- **C1:** The actor API makes continuation, normal stopping, and abnormal stopping explicit. Supervisor restart tolerance bounds repeated failure, while one-for-one, one-for-all, and rest-for-one strategies express different dependency assumptions. See the [actor API](https://gleam-otp.hexdocs.pm/gleam/otp/actor.html).
- **C2:** Generic actor state and typed subjects combine with opaque supervisor handles, builders, and child specifications. Applications can reuse the same supervision structure with different actor protocols. See the [static supervisor API](https://gleam-otp.hexdocs.pm/gleam/otp/static_supervisor.html).

The linked APIs are the recommended entry points for comparing typed interfaces with the underlying OTP lifecycle model.

## JVM and .NET actor systems

### [akka/akka-core](https://github.com/akka/akka-core)

**Language / role:** Scala and Java; JVM actor runtime with typed behaviors and supervision. This is the canonical destination to which the former `akka/akka` repository redirected during research.

Study the placement of behavior construction relative to supervision. Moving `setup` inside or outside a supervision wrapper changes what state and children are reconstructed, making this a particularly instructive example of lifecycle semantics encoded through composition.

- **C1:** Restart is distinct from stop: cleanup may require both `PreRestart` and `PostStop`, and child termination depends on the selected supervision arrangement. Bounded restart policies and exception-specific handling make failure behavior explicit.
- **C2:** Typed behaviors, actor references, and composable supervision wrappers let applications define protocols separately from execution and recovery policy.

**Entry point:** [Typed fault tolerance](https://doc.akka.io/libraries/akka-core/current/typed/fault-tolerance.html). The repository documents Business Source License terms for current core code; inclusion here does not imply an Apache-style license.

### [apache/pekko](https://github.com/apache/pekko)

**Language / role:** Scala and Java; Apache actor, remoting, and distributed application framework.

Pekko began as a fork of Akka 2.6, but qualifies separately through substantive independent evolution. Its 1.1 release series documents migration of classic remoting and the multinode testkit from Netty 3 to Netty 4, JUnit 5 support, typed mailbox APIs, and failure-detector changes.

- **C1:** Supervision controls state reconstruction and child lifecycle; distributed correctness also appears in fixes for sharding delivery, TLS handshakes, and startup failures. Compare [typed fault tolerance](https://pekko.apache.org/docs/pekko/current/typed/fault-tolerance.html) with the release fixes.
- **C2:** Typed and classic actor interfaces coexist with remoting and persistence/testkit abstractions. The evolution of those interfaces is visible in the [1.1 release notes](https://pekko.apache.org/docs/pekko/current/release-notes/releases-1.1.html).

Those two documents are useful entry points for studying both inherited architecture and the fork's separate engineering work. Experimental compatibility features should not be treated as universal interoperability guarantees.

### [akkadotnet/akka.net](https://github.com/akkadotnet/akka.net)

**Language / role:** C#; a separate .NET implementation of the Akka actor model.

Study the separation between an actor's externally stable reference, its mailbox, and the replaceable actor instance. This distinction clarifies what restart preserves and why retrying a failed message is a separate decision.

- **C1:** Restart replaces the actor instance while retaining its reference and mailbox; the message that caused failure is not automatically replayed. Child suspension and termination, restart hooks, and DeathWatch form a detailed lifecycle protocol. See [supervision](https://getakka.net/articles/concepts/supervision.html).
- **C3:** Dispatchers batch mailbox work and expose throughput and time-deadline controls. Thread-pool, pinned, and other dispatcher choices illustrate fairness, blocking isolation, and thread-allocation tradeoffs without requiring a different actor API. See [dispatchers](https://getakka.net/articles/actors/dispatchers.html).

The two guides provide a productive route from observable recovery semantics to the scheduling mechanisms that implement actor execution on .NET.

## Virtual actors and distributed computation

### [dotnet/orleans](https://github.com/dotnet/orleans)

**Language / role:** C#; distributed virtual actors, called grains.

Orleans is valuable for studying the distinction between durable logical identity and an individual in-memory activation. The runtime handles activation and placement while applications program grain interfaces and state behavior.

- **C1:** Single-threaded activation execution does not eliminate asynchronous deadlocks. The scheduling guide walks through circular grain calls and explains how reentrancy permits request interleaving. This makes the interaction between `await`, isolation, and progress concrete. See [request scheduling](https://learn.microsoft.com/en-us/dotnet/orleans/grains/request-scheduling).
- **C2:** Grain identity, references, activation management, and persistence integration constitute a reusable distributed programming model rather than an application-specific queue. The [repository overview](https://github.com/dotnet/orleans) explains these boundaries.

**Entry point:** The request-scheduling guide above is the best starting point for evaluating what virtual-actor isolation actually guarantees; it also exposes constraints that are easy to miss from the high-level programming model.

### [dapr/dapr](https://github.com/dapr/dapr)

**Language / role:** Go; the actors subsystem of the broader Dapr distributed application runtime. The monorepo is counted once, specifically for this subsystem.

Study a virtual-actor implementation in which sidecars, a placement service, state providers, and application handlers cooperate. The documentation connects actor identity to placement-table hashing and routing, rather than treating location transparency as unexplained magic.

- **C1:** A per-actor turn lock covers an entire asynchronous operation, including its returned task. Circular calls can time out. Timers depend on an active instance, whereas reminders can reactivate an actor, creating materially different lifecycle semantics.
- **C2:** Actor activation, persistence integration, reminders, and language-independent service interfaces are reusable across applications. Placement responsibilities are separated from user actor code.

**Entry point:** [Actor runtime concepts](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-features-concepts/), especially distribution, garbage collection, timers/reminders, and turn-based access. Actor-state persistence should not be confused with keeping a particular activation alive.

### [ray-project/ray](https://github.com/ray-project/ray)

**Language / role:** C++ and Python; Ray Core's stateful actor execution and recovery subsystem, within a larger distributed-computing monorepo.

Study the boundary between restarting a worker, recovering its state, and retrying its methods. Ray provides a useful counterpoint to supervision frameworks designed primarily around service trees.

- **C1:** Restart reruns an actor's constructor; state recovery requires application logic such as checkpointing. At-most-once execution can still return an error after a method ran if its reply was lost. Enabling retries introduces at-least-once behavior and duplicate-effect concerns. Creator fate-sharing and detached actors add further lifetime distinctions.
- **C2:** Actor handles expose reusable stateful workers within Ray's task/object execution model, while restart and task-retry policies can be configured separately.

**Entry point:** [Actor fault tolerance](https://docs.ray.io/en/latest/ray-core/fault_tolerance/actors.html). Read its ordering qualifications for threaded and asynchronous actors before assuming the serial semantics of a conventional actor loop.

## Go actors and supervision-only frameworks

### [asynkron/protoactor-go](https://github.com/asynkron/protoactor-go)

**Language / role:** Go; local and distributed actor framework.

The mailbox is a compact but substantial implementation to study. It separates user messages from system messages and coordinates scheduling through atomic state rather than assigning a permanent goroutine to every mailbox operation.

- **C1:** The mailbox uses compare-and-swap transitions between idle and running states. After a run finishes, it checks for remaining messages and attempts rescheduling, addressing the race between message arrival and relinquishing execution ownership.
- **C2:** Mailbox, dispatcher, message-invoker, and middleware interfaces separate storage, execution, delivery, and instrumentation. This exposes meaningful extension points beneath the actor API.

**Entry point:** [Mailbox implementation](https://github.com/asynkron/protoactor-go/blob/dev/actor/mailbox.go). Trace the scheduler-state transitions alongside the separate system-message queue. The source supports the architectural assessment here; benchmark numbers advertised elsewhere were not used as selection evidence.

### [ergo-services/ergo](https://github.com/ergo-services/ergo)

**Language / role:** Go; Erlang-inspired process behaviors, actors, networking, and supervision.

Study how OTP-style lifecycle policy is re-expressed through Go behavior interfaces and child factories. Supervisor initialization and restart ordering expose dependencies that would otherwise be hidden inside application goroutine management.

- **C1:** Children initialize sequentially; a failed initialization terminates the supervisor instead of leaving a successfully initialized parent with an incomplete child set. Restart strategies distinguish isolated failures from dependent siblings, and intensity limits bound repeated restarts.
- **C2:** A supervisor is implemented through the same process-behavior machinery as other actors. Child specifications and factories support nested reusable components, while ordering options distinguish parallel shutdown from ordered recovery.

**Entry point:** [Supervisor documentation](https://docs.ergo.services/actors/supervisor), including startup, links, restart strategies, and the `KeepOrder` option. It is a useful comparison with both OTP's process model and ordinary Go cancellation patterns.

### [thejerf/suture](https://github.com/thejerf/suture)

**Language / role:** Go; supervision trees for long-running services, without requiring an actor messaging runtime.

Suture deserves attention precisely because its abstraction is small: a service implements `Serve(context.Context) error`, and a supervisor is itself a service. The difficult work lies in lifecycle coordination, restart control, and cooperative shutdown.

- **C1:** Cancellation cannot forcibly terminate a Go goroutine. The documentation discusses shutdown failures and the danger of reusing service state while an earlier execution is still alive. Startup synchronization and distinguished return errors control races and escalation.
- **C2:** The service interface composes ordinary Go components into supervision trees. Tokens, event hooks, and special termination errors support management without prescribing application message types.

**Entry point:** [Suture v4 API and lifecycle documentation](https://pkg.go.dev/github.com/thejerf/suture/v4). Its decaying failure count, backoff, and jitter also provide a concrete study of restart-storm control. Treat cooperative stopping as part of the service contract.

## Native scheduling, language runtimes, and WebAssembly

### [actor-framework/actor-framework](https://github.com/actor-framework/actor-framework)

**Language / role:** C++; C++ Actor Framework, usually called CAF.

Study an actor scheduler that maps many actor state machines onto a smaller worker pool. Its documentation clearly separates ready/waiting transitions, external enqueueing, worker behavior, and policy customization.

- **C2:** Scheduler policies have explicit coordinator and worker data and hooks. They expose reusable control over execution without requiring applications to replace the actor programming model.
- **C3:** Cooperative execution multiplexes actors over workers. Because an actor runs nonpreemptively, blocking work can occupy a worker and harm other actors; detached actors provide an explicit alternative. The scheduler's work-distribution choices make the throughput/fairness/resource tradeoff inspectable.

**Entry point:** [Scheduler architecture](https://actor-framework.readthedocs.io/en/stable/core/Scheduler.html). This is especially useful for engineers moving from one-thread-per-object designs to actor multiplexing, because it describes both the machinery and the conditions under which that machinery stops helping.

### [Stiffstream/sobjectizer](https://github.com/Stiffstream/sobjectizer)

**Language / role:** C++; SObjectizer, combining agents, actor messaging, publish/subscribe, and other coordination facilities.

Study how dispatchers and binders separate an agent's behavior from its execution resources. Cooperations group agents, while dispatcher handles and binding policy make lifetime and thread allocation explicit.

- **C1:** For handlers not marked thread-safe, execution remains serialized even when successive events run on different pool threads. Thread migration therefore does not imply simultaneous handler execution.
- **C2:** Agents and cooperations can bind to different dispatcher arrangements without rewriting their message protocols. Per-agent and group binding provide distinct composition boundaries.
- **C3:** Single-thread, active-object, and pool dispatchers allow applications to choose where they share threads and where they isolate work.

**Entry point:** [Dispatcher internals and usage](https://github.com/Stiffstream/sobjectizer/wiki/SO-5.7-InDepth-Dispatchers). Follow the dispatcher handle's lifetime, then the binder's role, before comparing the scheduling alternatives.

### [ponylang/ponyc](https://github.com/ponylang/ponyc)

**Language / role:** C/C++ and Pony; compiler plus the Pony actor runtime. The runtime and concurrency-testing machinery are the relevant subsystems.

Pony is a valuable language/runtime co-design example. Actor behaviors are asynchronous message handlers, and each actor executes behaviors sequentially under a cooperative scheduler.

- **C1:** The runtime's message queues and backpressure involve atomic operations and difficult interleavings. Its systematic-testing machinery controls runtime-thread scheduling and uses seeds to reproduce executions, including work on queues, garbage collection, and cycle detection. See [systematic runtime testing](https://github.com/ponylang/ponyc/blob/main/SYSTEMATIC_TESTING.md).
- **C2:** Actors and asynchronous behaviors are language-level constructs rather than conventions imposed through a library. Their explicit calling semantics make the distinction between sending work and receiving a result visible. See the [actor tutorial](https://tutorial.ponylang.io/types/actors.html).

**Caveat:** The repository describes Pony as pre-1.0 and warns of breaking changes. This entry is an actor-runtime study recommendation, not an assertion of OTP-style supervision equivalence.

### [cloudwu/skynet](https://github.com/cloudwu/skynet)

**Language / role:** C and Lua; lightweight service/actor runtime, especially associated with game-server development.

Study the two-level queue design: each service has a message queue, and runnable service queues enter a global queue. Queue state tracks whether a mailbox is already globally scheduled or currently dispatched.

- **C1:** The `in_global` state, queue locks, release handling, and initialization ordering protect against duplicate scheduling and premature dispatch. See [message-queue implementation](https://github.com/cloudwu/skynet/blob/master/skynet-src/skynet_mq.c).
- **C3:** Per-service ring buffers, global runnable-queue coordination, growth, and overload accounting show how memory and scheduling costs are structured.
- **C4:** The [dated history](https://github.com/cloudwu/skynet/blob/master/HISTORY.md) records evolution across 2014–2025, including timer races, retiring-service deadlocks, dead-service leaks, initialization changes, and Lua/allocator upgrades. This is concrete complexity-management evidence beyond repository age.

The source and history are complementary entry points: read the current queue invariants alongside the failure classes that prompted changes.

### [lunatic-solutions/lunatic](https://github.com/lunatic-solutions/lunatic)

**Language / role:** Rust; a WebAssembly process/actor runtime built around Wasmtime.

Study the interaction between sandboxed computation, host scheduling, signals, links, and monitors. A common process contract covers WebAssembly and native processes, while process creation coordinates registration and linking with starting execution.

- **C1:** The process loop prioritizes signals and distinguishes normal completion, failure, linked-process death, and explicit kill. Link setup before child execution addresses a startup race. See the [process implementation](https://github.com/lunatic-solutions/lunatic/blob/main/crates/lunatic-process/src/lib.rs).
- **C2:** A shared process interface and configurable WebAssembly spawning separate lifecycle operations from executable code and host resource configuration. See [WebAssembly process creation](https://github.com/lunatic-solutions/lunatic/blob/main/crates/lunatic-process/src/wasm.rs).

**Caveat:** Implementation comments acknowledge paths where a native host panic can bypass link notification, and that distributed linking lacks the local startup guarantee. These are substantive boundaries to study, not evidence of complete distributed fault tolerance. Current maintenance continuity was not established by this review.

## Rust actor libraries

### [slawlor/ractor](https://github.com/slawlor/ractor)

**Language / role:** Rust; actor framework inspired by `gen_server`, with a separate clustering component.

Study its unusually explicit runtime-semantics document before studying convenience APIs. It distinguishes configuration from mutable actor state and explains which events can interrupt a handler.

- **C1:** Separate channels prioritize kill, stop, supervision, and user messages. Kill can interrupt asynchronous work, whereas stop waits for the current handler. Per-sender local FIFO is qualified rather than generalized across senders or remote reconnections; panic handling also depends on the process's panic strategy.
- **C2:** Typed actor state, calls/casts, reply ports, and supervision events provide reusable protocol and lifecycle building blocks. Supervisors receive information on which to implement policy instead of being synonymous with automatic restart.

**Entry point:** [Runtime semantics](https://github.com/slawlor/ractor/blob/main/docs/runtime-semantics.md).

**Caveat:** The repository describes clustering as not production-ready; its local actor semantics should not be read as a guarantee of equivalent remote reliability or deployment security.

### [tqwewe/kameo](https://github.com/tqwewe/kameo)

**Language / role:** Rust; typed actors running on Tokio.

Study the `Actor` trait's lifecycle rather than only its message-send syntax. Startup, panic handling, linked-actor death, stopping, and undelivered messages are distinct extension points.

- **C1:** Messages sent to self during startup receive special ordering relative to external messages. Link-death and panic hooks make failure propagation configurable, while shutdown errors have their own consequences. These contracts matter when establishing and restoring state invariants.
- **C2:** Associated argument/error types, typed message/reply handling, lifecycle callbacks, and supervision strategy compose into reusable actor components.
- **C3:** The API exposes bounded mailboxes for backpressure alongside unbounded alternatives, putting queue-growth policy into the runtime interface rather than hiding it in application code.

**Entry point:** [Actor trait and lifecycle documentation](https://docs.rs/kameo/latest/kameo/actor/trait.Actor.html). Review ordering and hook defaults against the crate version selected by an application; the linked `latest` documentation is version-moving.

### [actix/actix](https://github.com/actix/actix)

**Language / role:** Rust; the Actix actor framework. This entry concerns actor execution and supervision, not the separate Actix Web repository.

Study a supervision model whose restart semantics differ from replacing an actor object. That difference is useful when comparing apparently similar APIs across frameworks.

- **C1:** `Supervisor` restarts an actor by creating a new execution context and invoking its restarting hook; it does not recreate the actor value. Applications must account for surviving state when restoring invariants. This should not be assumed to provide universal recovery from every panic.
- **C2:** Typed messages and handlers, addresses, contexts, and asynchronous/synchronous execution facilities provide reusable components around the actor model. Supervision layers lifecycle behavior onto those components.

**Entry point:** [Supervisor API and restart example](https://docs.rs/actix/latest/actix/struct.Supervisor.html). Compare the example with frameworks that rerun a constructor, and identify which resources belong to actor state versus its replaced execution context.

## Other language communities and distributed designs

### [apple/swift-distributed-actors](https://github.com/apple/swift-distributed-actors)

**Language / role:** Swift; peer-to-peer distributed actor clustering built around Swift's distributed actor facilities.

Study the runtime work required beneath language-level distributed calls: transport, membership gossip, failure detection, discovery, and termination observation. The design also considers testing clusters within one process using in-memory or real transports and injected communication faults.

- **C1:** Remote death observation depends on cluster failure detection and node-down decisions. Testing with delayed or lost messages exposes failure cases that local actor tests cannot exercise.
- **C2:** Pluggable transport/discovery mechanisms and a typed receptionist separate locating actors from their application behavior. Cluster events and watching extend that abstraction to lifecycle changes.

**Entry point:** [Official distributed-actors architecture article](https://www.swift.org/blog/distributed-actors/).

**Caveat:** The repository describes a beta preview without pre-1.0 source-compatibility guarantees. The article is architectural background, and its historical API examples should be checked against the selected revision rather than treated as current recipes.

### [haskell-distributed/distributed-process](https://github.com/haskell-distributed/distributed-process)

**Language / role:** Haskell; Cloud Haskell's process and related supervision packages in a monorepo.

Study the layering between transport connections, process mailboxes, typed channels, remote spawning, and lifecycle monitoring. This provides a functional-language comparison with BEAM-inspired systems without requiring an entire replacement VM.

- **C1:** Supervisor policies distinguish orderly shutdown from immediate kill and can escalate after a timeout. Branch restart modes separate stopping all children first from restarting each in turn; reversing shutdown order matters when children depend on siblings. See [supervision principles](https://haskell-distributed.github.io/tutorials/5ch.html).
- **C2:** `Network.Transport` separates connection/error semantics from distributed processes. Higher-level managed processes and supervision build on those reusable foundations. See the [architecture and documentation overview](https://haskell-distributed.github.io/documentation.html).

Those are the two recommended entry points. Some tutorial material retains references to older package layouts; verify exact policy constructors against the monorepo revision being studied.

### [jodal/pykka](https://github.com/jodal/pykka)

**Language / role:** Python; local actors, references, proxies, and futures, principally through thread-based execution.

Study how a compact library exposes actor ownership while adapting ordinary Python method calls and exceptions. This is a useful local-concurrency contrast with distributed or virtual actor systems.

- **C1:** The documented actor loop distinguishes a request with a reply future from an unhandled message: exceptions can be delivered to the requester, while an unhandled failure triggers actor shutdown and the failure hook. Initialization, startup, orderly stop, and failure callbacks also execute under different lifecycle conditions.
- **C2:** Actor references, ask/tell operations, proxies, and futures provide reusable boundaries for interacting with isolated state without requiring application-specific queues at every call site.

**Entry point:** [Actor API, lifecycle, and embedded implementation](https://pykka.readthedocs.io/stable/reference/actors/). This entry does not imply automatic distributed supervision or state recovery; its value is the inspectable mapping from Python calls to actor execution.

### [kquick/Thespian](https://github.com/kquick/Thespian)

**Language / role:** Python; actor systems with interchangeable local and multiprocess/networked execution bases.

Study the separation between application actor code, opaque addresses, and the system base responsible for delivery and scheduling. Different bases expose different capabilities, so location transparency does not mean every deployment behaves identically.

- **C1:** A handler exception causes one retry of the message; a second exception returns a poison-message notification while the actor continues. Process death is different: the parent receives a child-exited notification and decides how to recover. Parent shutdown also normally propagates to children.
- **C2:** The actor API remains stable across alternative system bases, allowing reuse of behavior while changing process and transport arrangements. Opaque addresses prevent application code from depending on a particular routing representation.

**Entry point:** [Actor user's guide](https://thespianpy.com/doc/using.html), particularly system implementations, actor failure, parent lifecycle, and poison-message behavior. Retried handlers require attention to partially completed side effects.

### [celluloid/celluloid](https://github.com/celluloid/celluloid)

**Language / role:** Ruby; object-oriented actors, call proxies, and supervision. Included as a historical architecture and evolution study.

Study how ordinary Ruby objects acquire actor behavior through proxying and injected methods. The architecture separates actor-system registration from supervision relationships, with a supervision container itself implemented as an actor.

- **C2:** Synchronous, asynchronous, and future-based call proxies expose different interaction styles over actor execution. Registry and supervision-container abstractions support reusable component management. See the [architecture notes](https://github.com/celluloid/celluloid/blob/master/architecture.md).
- **C4:** The [changelog](https://github.com/celluloid/celluloid/blob/master/CHANGES.md) records 2015–2020 work on shared call abstractions, test restructuring, JRuby differences, and reintegrating the supervision component. These changes demonstrate management of compatibility and internal complexity over multiple releases.

**Caveat:** The architecture notes predate the supervision component's reintegration, so read them with the changelog. Current maintenance continuity was not established; this selection should not be read as an endorsement of present-day production support.

## Search coverage and limitations

Live discovery used more than six distinct formulations, including: BEAM/OTP supervision; Rust actor lifecycle and supervision; C++ actor schedulers; Go actor frameworks and service supervision; Python actors and failure handling; Orleans/Dapr virtual-actor reentrancy; Swift/Pony/Haskell distributed actors; Lua game-service runtimes; Ruby supervision; Gleam typed OTP; and WebAssembly actors. Follow-up queries targeted mailbox races, deterministic concurrency testing, restart semantics, release history, and less familiar runtimes. JavaScript/TypeScript and statechart-adjacent searches were also sampled. Later queries increasingly repeated candidates or surfaced small experiments, adapters, tutorials, and benchmark collections.

Every retained canonical repository was opened, and at least one additional primary source containing substantive API, implementation, architecture, or evolution material was read. Repository links establish identity; the linked entry points explain why each project qualifies. Akka's repository rename was resolved to its canonical destination. Pekko is retained despite its ancestry because independently documented engineering changes establish separate evolution; multiple ports or sibling projects were otherwise not automatically counted as separate discoveries. No retained entry is presented as an official mirror.

The selection deliberately includes both substantial runtimes and small-surface supervision libraries, but excludes ordinary process managers, thin provider adapters, tutorials, awesome-lists, and benchmark-only repositories. The JavaScript/statechart ecosystem and additional Rust alternatives are not exhaustively catalogued. Their omission is not a quality judgment. Libraries built on OTP are distinguished from independent runtime implementations, and large application platforms are assessed only for their actor subsystems.

This was read-only source and documentation research: repositories were not cloned, candidate code was not executed, and advertised performance numbers were not independently measured or used as ranking evidence. Statements about study value and qualifying criteria are grounded inference from the cited mechanisms. Current docs and branch links can change; historical, beta, and implementation-specific limitations are called out where material. Neither an old creation date nor a recent push was treated as proof of sustained maintenance, and C4 is assigned only where the inspected history supplies concrete evolution evidence.
