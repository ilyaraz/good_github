# Discrete-event simulation frameworks

Research date: **2026-10-09**.

This selection covers 26 GitHub repositories implementing reusable discrete-event simulation engines or substantial modeling frameworks built on such engines. It spans process interaction, queueing networks, DEVS and hybrid models, distributed actors, optimistic parallel simulation, and network and hardware simulation. Domain-specific platforms qualify when their scheduling or modeling infrastructure is reusable and substantial. The descriptions identify useful engineering study paths, not a guarantee that every component is exemplary.

Canonical repository identities and archive flags were checked through GitHub pages or repository metadata. Each entry also has inspected primary documentation or implementation evidence beyond its root README. None of the selected repositories was marked archived at research time; this does not establish active maintenance. Official mirrors and repositories with notably older recorded pushes are identified below.

## Criteria legend

- **C1 — Difficult correctness:** event ordering, lifecycle invariants, concurrency, numerical semantics, rollback, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and modeling structures supporting different applications.
- **C3 — Performance with structure:** concrete mechanisms addressing simulation costs while retaining an understandable architecture.
- **C4 — Sustained evolution:** documented evolution over years together with compatibility, testing, or deliberate complexity management. Repository age alone does not qualify.

## Process interaction and queueing libraries

### [salabim/salabim](https://github.com/salabim/salabim)

**Python — process-oriented simulation with resources, queues, monitoring, and animation.** Particularly useful for studying how a convenient modeling language exposes a precise process lifecycle.

- **C1:** Components have explicit current, scheduled, passive, requesting, waiting, standby, and interrupted states. Activation, cancellation, interruption, and resumption have different effects on outstanding requests and remaining delay; same-time priorities and urgent scheduling make tie behavior explicit. These are substantive invariants behind apparently simple process methods. See the [component lifecycle and operations](https://salabim.org/manual/Component.html).
- **C2:** The same component abstraction supports timed work, all-or-any resource acquisition, state predicates, and interaction with other components. The manual describes these operations as composable primitives rather than restricting users to a fixed queueing model. The component guide is also the best initial reading path for understanding the relationship between process code and the scheduler.

### [CiwPython/Ciw](https://github.com/CiwPython/Ciw)

**Python — queueing-network simulation with blocking, customer routing, and state tracking.** A strong study target when model semantics, rather than only event-queue mechanics, determine correctness.

- **C1:** Its three-phase account distinguishes advancing time, executing a scheduled event, and completing consequent actions such as unblocking. Consequent actions finish before another scheduled event is selected. Simultaneous scheduled events are selected randomly to avoid systematic order bias. See [simulation mechanisms](https://ciw.readthedocs.io/en/latest/Background/mechanisms.html).
- **C2:** Networks combine arrival and service distributions, routing, server counts, finite capacities, and optional trackers. A separate state-digraph detector can run a model until circular blocking causes deadlock, with state-dependent time-to-deadlock measurements. The [deadlock guide](https://ciw.readthedocs.io/en/latest/Guides/System/deadlock.html) demonstrates how detection and observation attach to the general simulation object.

### [r-simmer/simmer](https://github.com/r-simmer/simmer)

**R/C++ — trajectory-based DES with a compiled event engine.** Study how an expressive statistical-language interface connects to a lower-level scheduler without moving all model customization into C++.

- **C1:** Event ordering uses time and priority. Resource release, resource management, post-release processing, ordinary activities, and new arrivals receive deliberately different priorities. Splitting release processing avoids incorrect behavior when capacity changes, queued arrivals, and releases coincide.
- **C2:** Trajectories are linked activity structures; sources, arrivals, resources, managers, and monitors have distinct responsibilities. R callbacks supply model-specific behavior.
- **C3:** The event loop and core bookkeeping reside in C++, connected through Rcpp. The ordered event container also supports unscheduling through stored iterators. This is a concrete division between expressive modeling and frequently executed scheduling work, without relying on a claimed speedup.

The inspected [architecture paper, especially sections on the C++ core and event ordering](https://r-simmer.org/articles/simmer-02-jss.pdf), explains all three criteria. Its stated package version describes the paper, not necessarily today's release.

### [JuliaDynamics/ConcurrentSim.jl](https://github.com/JuliaDynamics/ConcurrentSim.jl)

**Julia — event and coroutine-based simulation, formerly SimJulia.** Useful for studying a small event algebra underlying processes and synchronization.

- **C1:** Events pass once through idle, scheduled, and processed states. Callback registration is constrained by that lifecycle, and a yielding process resumes through an event callback. A recurring signal must therefore create a fresh event rather than reuse an already processed one.
- **C2:** Processes, timeouts, event combinations, and synchronization build on a shared event abstraction. The resulting composition supports resource contention and interacting simulations without embedding one particular domain into the engine.

The [events guide](https://juliadynamics.github.io/ConcurrentSim.jl/stable/guides/events/) connects the state machine to executable modeling examples. The former SimJulia name is the same project lineage and is not counted separately.

### [heal-research/SimSharp](https://github.com/heal-research/SimSharp)

**C#/.NET — process simulation using iterator methods, with resource and real-time extensions.** This is a separate implementation and extension of SimPy-style ideas, not an independently counted fork of the same source tree.

- **C1:** Preempted resource holders must handle interruption correctly. The thread-safe environment locks scheduling access while preserving the distinction between thread-safe submission and the execution of model processes. Real-time execution has explicit best-effort timing semantics.
- **C2:** Processes expose sequences of events. Resources distinguish leasing from consumption and discrete from continuous quantities; filtered resource pools handle heterogeneous reusable objects, while stores handle consumable items. These distinctions make a useful abstraction-design study.

Start with the separate [modeling and resource manual](https://github.com/heal-research/SimSharp/blob/master/docs/README.md). **Activity caveat:** GitHub metadata recorded the latest repository push on 2023-06-09; it was not archived. Treat it as an established codebase requiring a fresh compatibility check before adoption.

### [holgerbrandl/kalasim](https://github.com/holgerbrandl/kalasim)

**Kotlin — process-oriented simulation embedded in a Kotlin modeling DSL.** A useful comparison with Python generators and C# iterators because the environment also organizes dependency injection, randomness, and monitoring.

- **C1:** The scheduler specifies FIFO behavior for otherwise tied events and allows explicit priority changes. Resource requests and releases interact with component rescheduling, so reproducibility depends on more than selecting the next timestamp.
- **C2:** An environment owns simulation time, the event queue, and random-number facilities; components express behavior through process sequences, with resource and state primitives alongside them. Kotlin duration support and the documented older tick-oriented API expose an interesting units-and-interface design boundary.

The [basics guide](https://www.kalasim.org/basics/) describes both the environment structure and scheduling semantics. It is the most useful first entry point for understanding how the DSL maps to the execution model.

### [liuxfiu/simulus](https://github.com/liuxfiu/simulus)

**Python — direct-event and process simulation with synchronized groups of simulators.** Worth studying for its transition from local simulation to conservative parallel execution.

- **C1:** Synchronization groups coordinate simulator clocks and use mailbox delays to determine a safe lookahead. The implementation rejects invalid lookahead and duplicate group membership; these checks enforce conditions needed for causal advancement.
- **C2:** A group coordinates independent simulators through mailboxes while retaining their local modeling interfaces. The grouping abstraction separates application decomposition from execution placement.
- **C3:** The same synchronization layer supports local multiprocessing and distributed MPI execution. Minimum communication delay becomes an architectural input to synchronization, rather than merely a model parameter.

Read the [synchronization implementation](https://github.com/liuxfiu/simulus/blob/master/simulus/sync.py), including group initialization, mailbox inspection, and parallel execution setup. No claim is made that arbitrary models obtain useful parallel speedups.

### [agoussia/godes](https://github.com/agoussia/godes)

**Go — goroutine-based process simulation.** A smaller but substantive implementation showing how concurrent language mechanisms can represent sequential simulated progress.

- **C1:** Runners transition among ready, active, waiting, scheduled, interrupted, and terminated states. Scheduler channels transfer control between goroutines; advancing time, interruption, and resumption validate state and temporal assumptions. This makes the distinction between Go concurrency and simulation-time execution visible.
- **C2:** Runner interfaces, boolean-condition controls, queues, distributions, and statistics provide reusable model primitives. The core schedules user-defined runners rather than prescribing a domain-specific network or manufacturing model.

The [model scheduler](https://github.com/agoussia/godes/blob/master/model.go) is the main implementation entry point. Its package-global model and time state are a relevant design constraint for engineers considering isolated concurrent experiments. The project is included for its architecture, not its README's unverified comparative performance claims.

## Experiment frameworks and extensible simulation platforms

### [rossetti/JSL](https://github.com/rossetti/JSL)

**Java — simulation library and experiment infrastructure; focus on `JSLCore`.** Useful for studying a scheduler integrated with observers, execution controls, and conditional actions rather than a minimal event heap alone.

- **C1:** The executive coordinates initialization, event cancellation and rescheduling, and conditional-action processing. Initialization clears both the event calendar and conditional actions, making setup order significant; rescheduling an already scheduled event is rejected.
- **C2:** The executive delegates event storage through a calendar interface and separates event execution, observation, and conditional-action processing. The repository's core/extensions split also separates baseline simulation facilities from optional integrations.

Read [`Executive.java`](https://github.com/rossetti/JSL/blob/main/JSLCore/src/main/java/jsl/simulation/Executive.java) for these boundaries and lifecycle checks. **Activity caveat:** the checked repository's latest push was 2023-10-27. This entry concerns the Java JSL codebase and does not imply that its documentation or dependencies track newer related projects.

### [umontreal-simul/ssj](https://github.com/umontreal-simul/ssj)

**Java — stochastic simulation toolbox; focus on `simevents` and event-list implementations.** Particularly valuable for comparing event scheduling with the surrounding random-variate and statistical abstractions.

- **C1:** Events are associated with a simulator and have defined scheduling, cancellation, and same-time ordering semantics. The simulator manages its stopped/running state even when event execution exits exceptionally. These are concrete lifecycle obligations, not simply priority-queue ordering.
- **C2:** `Event`, `Simulator`, and `EventList` separate model behavior, clock execution, and storage strategy. A simulator can receive a different event-list implementation; the default uses a splay tree. Explicit simulator instances also make state ownership visible, though the simulator itself is not thread-safe.

Read [`Simulator.java`](https://github.com/umontreal-simul/ssj/blob/master/src/main/java/umontreal/ssj/simevents/Simulator.java) alongside [`Event.java`](https://github.com/umontreal-simul/ssj/blob/master/src/main/java/umontreal/ssj/simevents/Event.java). This entry selects the DES subsystem, not every numerical routine in the larger toolbox.

### [averbraeck/dsol](https://github.com/averbraeck/dsol)

**Java — multi-formalism simulation framework with discrete-event, DEVS, and flow-oriented facilities.** Its most instructive material concerns controlling a simulation from a separate user-interface or application thread.

- **C1:** Run state and replication state are distinct state machines. Starting, stepping, stopping, and completing a replication must coordinate with the worker thread without losing a start notification or emitting replication-start behavior twice. Error policies distinguish continuing, pausing, and terminating execution.
- **C2:** Simulator lifecycle control is reusable across models and experiments, while the broader framework separates simulation formalisms and modeling facilities into modules. The [manual](https://simulation.tudelft.nl/dsol/manual/) provides the subsystem map.

The [simulator-state design discussion](https://simulation.tudelft.nl/dsol/manual/8-advanced/simulator-state/) is unusually concrete about races and acknowledgment between controlling and simulation threads. The canonical repository verified here is `averbraeck/dsol`, even where documentation retains older DSOL naming.

### [jaamsim/jaamsim](https://github.com/jaamsim/jaamsim)

**Java — graphical DES platform with extensible simulation-object palettes.** Study the relationship between a visual model editor and a general event kernel.

- **C1:** The event manager orders events by integer tick, priority, and same-priority insertion policy. Its process handoff uses locking and condition waits that account for spurious wakeups. Negative delays, overflow, and scheduling from restricted callback contexts receive explicit handling.
- **C2:** Custom Java simulation objects join the same model, input, and graphical infrastructure as built-in objects. This is a substantial extension mechanism beyond editing a fixed palette of prepackaged blocks.
- **C3:** The kernel reuses event objects and separates event-tree operations from process handoff. These are inspectable allocation and scheduling decisions; no numerical speedup is assumed.

Start with [`EventManager.java`](https://github.com/jaamsim/jaamsim/blob/master/src/main/java/com/jaamsim/events/EventManager.java), then relate its scheduling API to the repository's object-extension description.

## Typed asynchronous models and distributed actors

### [asynchronics/nexosim](https://github.com/asynchronics/nexosim)

**Rust — asynchronous, component-based DES with typed ports and mailboxes.** A strong modern counterpart to coroutine and actor simulators.

- **C1:** The documented execution contract combines chronological progression with causal ordering of message delivery. Causal ordering should not be mistaken for one total order over all unrelated events at a timestamp. Typed messages and distinct request/reply paths make communication contracts explicit.
- **C2:** Models expose input, output, requestor, and replier interfaces; mailboxes and addresses connect models, while initialization and prototypes support assembling larger systems from components.
- **C3:** A custom executor distributes model execution across threads. Mailbox boundaries and fixed-capacity queues make the relationship between model structure and execution costs inspectable.

The [crate documentation](https://docs.rs/nexosim/latest/nexosim/) explains the ports, model assembly, execution, and ordering guarantees with examples. Performance qualification here rests on those mechanisms, not benchmark rankings.

### [EDF-Lab/Sim-Diasca](https://github.com/EDF-Lab/Sim-Diasca)

**Erlang — distributed actor simulation; focus on the monorepo's `sim-diasca` subsystem.** This framework uses discrete ticks and logical substeps called diascas to reconcile actor communication with simulated causality.

- **C1:** A tick is scheduled once; spontaneous actor execution and message-triggered execution have separate rules. Diascas resolve causal exchanges without advancing physical simulation time. The time manager tracks actors in sets to prevent duplicate scheduling and explicitly documents races involving messages that affect subsequent diascas.
- **C2:** Actor models, scenarios, deployment, time management, and observation are separate facilities. A model can define spontaneous future actions and triggered responses while reusing the engine's distributed coordination.

Read the [time-manager implementation and design notes](https://github.com/EDF-Lab/Sim-Diasca/blob/main/sim-diasca/src/core/services/scheduling/class_TimeManager.erl) and the [modeller guide](https://olivier-boudeville-edf.github.io/Sim-Diasca/modeller-guide/Sim-Diasca-modeller-guide-english.pdf). This is an event/actor framework with discretized time, not a claim that every actor executes at every tick.

## DEVS and hybrid modeling engines

### [SimulationEverywhere/cadmium](https://github.com/SimulationEverywhere/cadmium)

**C++ — the original template-based Cadmium implementation of parallel DEVS.** Included deliberately for its compile-time modeling architecture.

- **C1:** The atomic simulator distinguishes internal, external, and confluent transitions. It checks supplied times against the last and next transition times, gathers output before state transitions, and clears consumed message bags. These operations encode DEVS semantics that can be broken by superficially plausible reorderings.
- **C2:** Models, time representations, loggers, and typed input/output message bags are separate template parameters or abstractions. Model assertions and typed ports make interface validation part of composition.

Read [`pdevs_simulator.hpp`](https://github.com/SimulationEverywhere/cadmium/blob/main/include/cadmium/engine/pdevs_simulator.hpp). **Lineage caveat:** this repository's latest recorded push was 2023-10-06. The separately verified [Cadmium v2 repository](https://github.com/SimulationEverywhere/cadmium_v2) describes a newer object-oriented implementation. It is not counted as a second selection here; readers seeking the current development direction should compare it with this historical template-based codebase.

### [smiz/adevs](https://github.com/smiz/adevs)

**C++ — DEVS simulation with coupled models and hybrid-system facilities.** Especially useful for examining a simulator that makes dependencies among output-producing models explicit.

- **C1:** The simulator separates output computation from state changes and selects internal, external, or confluent transitions. It rejects negative time advances. Its handling of Mealy-style output dependencies uses imminent, active, and pending sets and detects invalid dependency situations instead of silently producing an arbitrary order.
- **C2:** Value and time types are generic, and atomic models, coupled models, graphs, and event listeners have separate roles. Interfaces for exposing next events and injecting inputs also make the simulator usable inside a larger execution environment.

The [simulator implementation](https://github.com/smiz/adevs/blob/main/include/adevs/simulator.h) contains both the algorithm and explanatory comments. It is a good entry point for understanding how DEVS composition interacts with output dependencies and dynamic model structure.

### [CIFASIS/power-devs](https://github.com/CIFASIS/power-devs)

**C++/Qt — graphical DEVS and hybrid modeling environment with generated C++ simulations.** A historical but substantive example connecting a visual model hierarchy to a compact runtime.

- **C2:** Atomic C++ models combine into hierarchical coupled models. The environment translates the graphical model into an executable simulation, preserving explicit internal, external-input, and external-output couplings.
- **C3:** The coupling runtime maintains a heap of child event times and per-child routing indices. This avoids repeatedly treating all model connections as one undifferentiated list, while retaining readable coupling and child-model structures.

Read [`engine/coupling.cpp`](https://github.com/CIFASIS/power-devs/blob/powerdevs-dev/engine/coupling.cpp) together with the root description of the graphical-to-C++ workflow. **Historical status:** the latest GitHub push recorded was 2021-03-20, and the repository was not archived. Older GUI, Scilab, and real-time integration assumptions need reassessment before use; no build compatibility was tested.

## Optimistic parallel kernels and HPC modeling

### [ROSS-org/ROSS](https://github.com/ROSS-org/ROSS)

**C/MPI — parallel DES using logical processes and optimistic Time Warp execution.** A central study target for understanding why parallel simulation requires more than dispatching a priority queue across workers.

- **C1:** Timestamped messages can arrive after a logical process has advanced beyond them. Rollback therefore has to restore model state and undo the effects of incorrectly ordered execution. ROSS emphasizes model-supplied reverse computation, making reversibility an explicit modeling obligation.
- **C3:** Reverse computation trades additional model logic for reduced state-saving storage. Logical-process decomposition and distributed execution expose the communication, memory, and synchronization costs of optimistic simulation.
- **C4:** The project's history documents development from its early versions through the 2015 simplification effort, which removed deprecated functionality and internal state while preserving repository history. This is evidence of deliberate complexity management across years, not just longevity.

The official [architecture and project-history overview](https://ross-org.github.io/about.html) is the inspected entry point for these claims.

### [ROOT-Sim/core](https://github.com/ROOT-Sim/core)

**C11/MPI — optimistic parallel simulation kernel.** Valuable for studying the complete rollback path, including memory restoration, message cancellation, and re-execution.

- **C1:** A straggler can force rollback to an earlier checkpoint. The logical-process code restores state, emits or matches anti-messages, and silently replays intermediate events while suppressing duplicate outward effects. Correctness depends on the interaction among these operations, not merely restoring a timestamp.
- **C2:** Model event dispatch is separated from logical-process execution and allocator-assisted state management. This supports different event-driven models without requiring each model to implement the kernel's checkpoint and message machinery.
- **C3:** Checkpointing, replay, and communication are distinct mechanisms, allowing optimistic execution to balance recovery work against saved state and interprocess traffic.

Read [`src/lp/process.c`](https://github.com/ROOT-Sim/core/blob/master/src/lp/process.c), particularly straggler processing and rollback. This entry counts the kernel repository once; related model packages and front ends are not separate selections.

### [wilseypa/warped2](https://github.com/wilseypa/warped2)

**C++ — Time Warp simulation with worker threads and MPI communication.** Useful for studying the coordination around optimistic execution, especially global virtual time and termination.

- **C1:** Event dispatch carefully orders global-virtual-time reporting, event acquisition, and passive-to-active transitions to avoid inconsistent global observations or premature termination. Stragglers and anti-messages interact with rollback and cancellation.
- **C2:** Event, state, output, communication, and global-virtual-time managers are distinct collaborators of the dispatcher. Their interfaces expose the recoverable-state and communication boundaries.
- **C3:** Worker event processing is separated from the loop coordinating communication, global progress, and termination. Fossil collection uses globally safe progress to reclaim past state.

The main reading path is [`TimeWarpEventDispatcher.cpp`](https://github.com/wilseypa/warped2/blob/master/src/TimeWarpEventDispatcher.cpp). **Activity caveat:** the checked latest push was 2024-06-17; the repository was not archived. Treat it as a research kernel whose current toolchain support must be assessed separately.

### [codes-org/codes](https://github.com/codes-org/codes)

**C/C++ — reusable HPC network, storage, and workload simulation infrastructure built on ROSS.** It qualifies separately because it supplies a substantial modeling and interconnection layer rather than merely repackaging the kernel.

- **C1:** Its modeling guidance addresses reverse computation, consistent nanosecond units, and routing events between logical-process types. The network interface also documents ordering limitations when issuing multiple network events in one event handler and provides explicit sequence markers. These are useful examples of making model-level causality constraints visible to users.
- **C2:** A common model-net interface accommodates different interconnect models while higher-level components describe workloads and services. Disk, network, and server behaviors can remain separate logical-process types with event-based interfaces.

Read the [modeling best practices](https://github.com/codes-org/codes/blob/master/doc/codes-best-practices.tex) and [`model-net.h`](https://github.com/codes-org/codes/blob/master/codes/model-net.h). The documented limitations are part of the selection rationale, not evidence that arbitrary combinations are automatically correct.

## Network, distributed-system, and hardware simulation platforms

### [omnetpp/omnetpp](https://github.com/omnetpp/omnetpp)

**C++/NED — modular DES framework widely used for networks.** A substantial engine and modeling environment with a readable account of time representation and future-event storage.

- **C1:** Event order uses simulation time, scheduling priority, and insertion order. Decimal fixed-point simulation time avoids several equality and rounding hazards of floating-point clocks while making precision and range explicit design decisions.
- **C2:** Simple and compound modules, programmable channels, and NED-defined topologies separate component implementation from hierarchical model assembly.
- **C3:** The future-event-set interface is replaceable; the documented default binary-heap implementation is one storage policy behind that interface. This provides a concrete boundary for studying queue-performance tradeoffs.

The [simulation manual](https://doc.omnetpp.org/omnetpp/manual/) contains the inspected sections on the event loop, simulation time, modules, and future-event sets. The repository uses the Academic Public License; inclusion here describes public source and engineering relevance, not an assertion of unrestricted commercial licensing.

### [nsnam/ns-3-dev-git](https://github.com/nsnam/ns-3-dev-git)

**C++ with Python interfaces — network simulator; official read-only GitHub mirror.** Development is hosted on GitLab. Focus here is the reusable `core` event engine, not the full collection of protocol models.

- **C1:** The engine specifies FIFO order for tied timestamps, distinguishes cancellation from removal, and uses integer time with a configurable resolution. The documentation explains the precision/range tradeoff and why event execution itself consumes no simulated time.
- **C2:** `SimulatorImpl` separates execution engines from the public API; adapters add behavior such as real-time pacing or local clocks. Scheduling data structures are a further independent choice.
- **C3:** Map, heap, list, and calendar-style schedulers expose different queue tradeoffs. A supplied benchmark supports evaluating a model's event distribution rather than assuming one queue is universally best.

Read [Events and Simulator](https://www.nsnam.org/docs/manual/html/events.html) for these mechanisms and their API consequences. Mirror status is explicit in the canonical GitHub repository description.

### [simgrid/simgrid](https://github.com/simgrid/simgrid)

**C++ with multiple language interfaces — distributed-application simulation; official GitHub mirror of development on FramaGit.** It combines actor-level program behavior with models of contended computation and communication resources.

- **C1:** Actors interact with a central simulation coordinator through simulation calls. The engine resolves immediate work before advancing to the next completion, while resource models enforce shared-capacity constraints. The [design document](https://simgrid.org/doc/latest/Design_goals.html) explains how these layers support reproducible simulated execution.
- **C2:** Actors, activities, resources, and execution contexts have separate roles. Application behavior can be reused with different platform and resource models.
- **C3:** Context factories offer different actor execution mechanisms, including optimized cooperative switching; resource sharing is handled separately from actor code.
- **C4:** Historical [release notes](https://simgrid.org/doc/latest/Release_Notes.html) document years of internal rewrites, integration testing, removals of unsupported features, and compatibility work such as deprecation wrappers and API/ABI restoration. These are concrete evolution practices, not an inferred maturity score from repository age.

### [sstsimulator/sst-core](https://github.com/sstsimulator/sst-core)

**C++ with Python configuration — component-based simulation of computer architectures.** This entry concerns the SST core, counted once, rather than separately counting model libraries that use it.

- **C1:** Synchronization must preserve ordering across both threads and MPI ranks. The code coordinates barriers, flushing local events, checkpoint periods, and shutdown state; checkpoint requirements can impose synchronization even when cross-partition links are absent.
- **C3:** Separate thread and rank synchronization backends exploit minimum partition intervals and skip-ahead opportunities. Cases without communication can use simpler synchronization paths. The hierarchy makes the costs and obligations of parallel execution inspectable.

Read [`syncManager.cc`](https://github.com/sstsimulator/sst-core/blob/master/src/sst/core/sync/syncManager.cc), including its explanation of thread synchronization before rank synchronization and event-queue flushing. The surrounding component/link architecture makes this a reusable hardware-system framework; no claim is made that all component models scale equally well.

### [accellera-official/systemc](https://github.com/accellera-official/systemc)

**C++ — official SystemC reference library with an event-driven hardware/system modeling kernel.** Particularly useful for studying same-time concurrency semantics rather than only chronological event ordering.

- **C1:** A delta cycle separates evaluation, channel update, and notification. Runnable methods and coroutine-based threads execute before channel updates become visible to processes awakened for the next delta. The kernel also handles stopped execution, errors, and process cleanup. These phases define observable model behavior even when physical simulation time does not advance.
- **C2:** Processes, events, modules, and channels separate behavioral activity from communication and hierarchy. This supports varied hardware and system models under a shared execution contract.

Start with the `crunch` loop in [`sc_simcontext.cpp`](https://github.com/accellera-official/systemc/blob/main/src/sysc/kernel/sc_simcontext.cpp). The inspected [release notes](https://github.com/accellera-official/systemc/blob/main/RELEASENOTES.md) provide platform-test information and compatibility constraints, including build-configuration and ABI considerations; those constraints should inform reuse of the reference implementation.

## Search coverage, exclusions, and limits

Discovery used more than six distinct live-search formulations and continued beyond the initial familiar libraries. Search angles included Python process simulation and queueing networks; R and Julia simulation engines; Java/Kotlin/.NET experiment libraries; Rust asynchronous and Go goroutine simulators; C++ DEVS and hybrid modeling; optimistic Time Warp, rollback, and MPI kernels; network future-event sets; hardware delta-cycle engines; and Erlang distributed actors. Additional functional-language, JavaScript, and smaller-framework searches increasingly returned already covered architectures or less substantial candidates. GitHub pages and metadata established identity, while source files, detailed manuals, and design documents supplied the qualification evidence.

The 26 entries slightly exceed the broad-category guide because the ecosystem has materially different correctness contracts: process suspension, queue blocking, DEVS confluence, actor causality, conservative lookahead, optimistic rollback, and hardware delta cycles. CODES is retained as a reusable modeling layer above ROSS; these are distinct repositories and responsibilities. Monorepos are counted once, and relevant subsystems are identified. Criteria assignments are engineering judgments grounded in the linked evidence, not benchmark results or completed audits.

Important exclusions and boundaries:

- **SimPy:** the [official project is on GitLab](https://gitlab.com/team-simpy/simpy). An official, substantive GitHub mirror was not established during this search, so unrelated or stale mirrors were not substituted.
- **Aivika:** its [GitHub README announces a move](https://github.com/dsorokin/aivika/blob/master/README.md). Continued official GitHub mirroring was not established, so it was excluded despite relevant simulation abstractions.
- **DESMO-J and other non-GitHub distributions:** a relevant framework was insufficient without a verified canonical GitHub repository or official substantive mirror. This is a limitation of the requested repository scope, not a negative quality assessment.
- Model-only collections, tutorial implementations, generated wrappers, package feedstocks, and awesome lists were excluded. The original Cadmium and its successor were not counted as two selections. SimSharp is an independently implemented extension, not a duplicate source fork.
- Archived status and older push dates were checked, but a recent push alone was never used to claim sustained maintenance. The explicitly marked older repositories remain architectural study candidates. C4 is awarded only where inspected history also describes compatibility, testing, or complexity management.

Research was read-only. No candidate code was executed, dependencies installed, large repositories cloned, benchmarks reproduced, or maintainers contacted. Links generally target current documentation or verified default-branch files and can evolve. Source inspection supports the stated mechanisms and category fit; it does not establish end-to-end correctness, present buildability, licensing suitability, or performance for a particular workload.
