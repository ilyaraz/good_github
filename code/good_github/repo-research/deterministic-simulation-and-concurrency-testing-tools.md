# Deterministic simulation and concurrency testing tools

Research date: **2026-10-09**.

This selection covers 26 GitHub repositories for testing executable concurrent or distributed software: deterministic runtimes, controlled schedule exploration, weak-memory checking, system-call simulation, embedded database simulators, and concurrency test oracles. Stress testing and history checking are included where they complement simulation; they are explicitly distinguished from deterministic execution. FoundationDB and TigerBeetle count once each, specifically for their testing subsystems. This is a code-reading and selection guide, not a claim that every component is exemplary or that passing a bounded test proves a real system correct.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, memory semantics, adversarial inputs, or failures. **C2** — substantial reusable abstractions supporting different applications or tests. **C3** — performance or search-space constraints addressed through understandable architecture. **C4** — documented evolution over years, including compatibility, testing, or complexity management. Each entry gives evidence for at least two criteria. A criterion omitted from an entry is not necessarily absent from the project.

## Deterministic application and distributed-system runtimes

### 1. [tokio-rs/turmoil](https://github.com/tokio-rs/turmoil)

**Rust — simulation framework and simulated I/O crates.** Study how independently scheduled hosts and client test drivers can execute as futures inside one thread, while failures remain controllable from the test.

- **C1:** The simulated network supports partitions and holding/releasing in-flight messages. The filesystem model distinguishes pending writes from durable data and discards pending writes on a crash. These are concrete mechanisms for exercising recovery and ordering bugs. The filesystem API is explicitly marked unstable. [Runtime and I/O documentation](https://github.com/tokio-rs/turmoil/blob/main/crates/turmoil/src/lib.rs)
- **C2:** Host software is supplied as futures, while simulated sockets mirror Tokio interfaces. The repository separates the framework, network, filesystem, and io_uring simulation into crates, making the environment useful beyond any one protocol. [Crate structure](https://github.com/tokio-rs/turmoil/tree/main/crates)

Integration still requires routing relevant operations through the simulated interfaces; this is not transparent execution of arbitrary binaries.

### 2. [madsim-rs/madsim](https://github.com/madsim-rs/madsim)

**Rust — alternative async runtime and ecosystem adapters.** A useful study in making a simulator usable through familiar application dependencies rather than inventing an entirely separate programming model.

- **C1:** A seeded runtime owns randomness, task execution, timers, network, and filesystem simulation. A supervisor handle controls nodes and failures; execution limits and a panic when no task can run make stalled simulations observable. [Runtime implementation](https://github.com/madsim-rs/madsim/blob/main/madsim/src/sim/runtime/mod.rs)
- **C2:** The runtime registers simulator implementations by type, while the repository supplies adapters for Tokio, tonic, etcd, Kafka, and S3 APIs. Normal and simulation builds select different implementations through configuration. These abstractions support application-level distributed tests, not just isolated scheduling examples. [Simulator extension points and adapters](https://github.com/madsim-rs/madsim/tree/main/madsim/src/sim)

The dependency replacement and patching requirements in the repository README are a material integration cost; uncontrolled dependencies can undermine determinism.

### 3. [jellevandenhooff/gosim](https://github.com/jellevandenhooff/gosim)

**Go — source translation, simulated Go runtime, and simulated Linux services.** Particularly interesting for the boundary between language semantics and operating-system emulation.

- **C1:** The translator redirects goroutines, channels, maps, and globals into a controlled runtime. Per-machine globals prevent simulated processes from accidentally sharing application state; a simulated filesystem tracks in-flight writes for crash behavior. [Design document](https://github.com/jellevandenhooff/gosim/blob/main/docs/design.md)
- **C2:** Three distinct layers—runtime, standard-library hooks, and simulated OS—let ordinary Go packages participate in network and disk simulations. The CLI preserves a familiar test workflow, and metatesting can compare simulated runs and inspect their logs. [Design and test integration](https://github.com/jellevandenhooff/gosim/blob/main/docs/design.md)
- **C3:** Coroutine switching, jumping virtual time when all goroutines wait, and caching translated packages address execution and iteration costs explicitly.

The project calls itself experimental. Its design documents Go-version-specific hooks and uncontrolled sources such as pointer values; a seed alone cannot compensate for every escape from the model.

### 4. [IntersectMBO/io-sim](https://github.com/IntersectMBO/io-sim)

**Haskell — pure IO simulator, concurrency interfaces, and partial-order exploration.** Study how a monadic interface can preserve much of the structure of real concurrent code while producing inspectable execution traces.

- **C1:** IOSim models STM, asynchronous exceptions, timers, and thread operations. IOSimPOR discovers potentially racing steps and reruns a computation with selected races reversed; failure output includes controls for replay. [IOSimPOR guide](https://github.com/IntersectMBO/io-sim/blob/main/io-sim/how-to-use-IOSimPOR.md)
- **C2:** The `io-classes` interfaces allow implementations to run in real `IO` or simulation, with tracing of threads and transactional variables. This supports network and disk models built above the simulator. [Interface package](https://github.com/IntersectMBO/io-sim/tree/main/io-classes)
- **C3:** Schedule bounds, branching controls, and race-order prioritization balance exploration against test cost, including interaction with property-test shrinking.

IOSimPOR does not usually explore every schedule, and it treats steps at different simulated times as non-racing. Those assumptions matter when interpreting results.

### 5. [osukhoroslov/anysystem](https://github.com/osukhoroslov/anysystem)

**Rust, with Python process implementations — event-driven distributed-system simulation and model checking.** The former `systems-group/anysystem` URL redirects here; it is one repository, not two projects.

- **C1:** Processes communicate through messages and timers; network behavior can include loss, duplication, corruption, partitions, and node crashes. Model checking can start from an existing simulation state and restore that state after exploration. [Model-checker implementation](https://github.com/osukhoroslov/anysystem/blob/main/src/mc/model_checker.rs)
- **C2:** Separate process, node, network, and strategy abstractions support arbitrary message-passing algorithms. Exploration policies accept user-defined invariant, goal, pruning, and state-collection predicates. [Strategy interface](https://github.com/osukhoroslov/anysystem/blob/main/src/mc/strategy.rs)
- **C3:** Visited states can be stored fully, stored as hashes, or not cached. The code explicitly documents the memory/speed tradeoff and collision risk of hash-only storage.

This is a substantial framework also used for teaching, rather than a tutorial implementation. Process execution is instantaneous in its simulation model; it does not transparently reproduce arbitrary application runtimes.

### 6. [glideapps/determined](https://github.com/glideapps/determined)

**TypeScript — cooperative task scheduling, virtual time, and entropy replay.** A comparatively compact implementation for studying promise scheduling and cancellation without needing a custom VM.

- **C1:** The task interface distinguishes checkpoints, blocking, injected failure, deadlines, and cooperative cancellation. Scheduling and virtual-duration budgets expose livelock or runaway scenarios. Its comments carefully distinguish requesting cancellation from actually interrupting work. [Simulation implementation](https://github.com/glideapps/determined/blob/main/simulation.ts)
- **C2:** Production and simulated runners share task interfaces. Entropy is a separate abstraction with recording and replay implementations; replay checks both exhaustion and the names of requested entropy events, helping detect divergence. [Entropy implementation](https://github.com/glideapps/determined/blob/main/entropy.ts)

The useful abstraction is explicit participation in simulation: relevant yields, randomness, time, and blocking must pass through its APIs. It should not be read as a general simulator of every Node.js or browser operation.

### 7. [pingidentity/opendst](https://github.com/pingidentity/opendst)

**Java — instrumented distributed simulation with virtual threads.** An experimental option with a different integration approach from Lincheck: application packaging, simulated services, and network faults are central.

- **C1:** It controls supported thread, time, randomness, and blocking TCP operations, including partial receives and injected connection failures. The explicit gap inventory identifies important uncontrolled paths, including filesystem access, native code, subprocesses, and NIO. [Known gaps](https://github.com/pingidentity/opendst/blob/main/KNOWN_GAPS.md)
- **C2:** A Maven packager, SDK, agent, and runner have separate roles. The parent runner supplies execution plans to isolated child simulation JVMs; each child creates service classloaders and reports structured assertion and guidance signals. This is reusable orchestration around different applications. [Execution architecture](https://github.com/pingidentity/opendst/blob/main/DESIGN.md)

The documented 0.1 architecture requires JDK 25 or later and includes experimental thread-subclass rewriting. The limitations document should govern adoption decisions more than the README's broad determinism language.

## System-level simulation and instrumentation

### 8. [shadow/shadow](https://github.com/shadow/shadow)

**Rust and C — deterministic discrete-event network simulation of Linux applications.** Study an architecture that runs native application processes while replacing their observable network and timing environment.

- **C1:** A preloaded shim and seccomp interception route system calls into a simulated kernel. Seeded random inputs and modeled time, sockets, signals, and packet delivery aim to make executions reproducible. [Version 2 design](https://github.com/shadow/shadow/blob/main/docs/design_2x.md)
- **C2:** Configurable network graphs and unmodified application binaries support experiments across networked applications rather than one application-specific simulator.
- **C3:** Hot-path calls can execute in the shim using shared state; other calls use a control channel. Shared-memory mapping reduces copying, while worker scheduling and CPU pinning address large experiments. [Design](https://github.com/shadow/shadow/blob/main/docs/design_2x.md)

The project provides a concrete method for comparing deterministic syscall traces, rather than requiring users to assume reproducibility. Unsupported syscall features remain a compatibility boundary. [Determinism testing](https://github.com/shadow/shadow/blob/main/docs/testing_determinism.md)

### 9. [facebookexperimental/hermit](https://github.com/facebookexperimental/hermit)

**Rust — controlled execution and schedule perturbation for Linux x86-64 binaries.** Useful for understanding how determinization can be implemented below application libraries.

- **C1:** Deterministic execution serializes guest threads and virtualizes supported time, random, and system-call behavior. Chaos mode varies scheduling reproducibly; verification compares executions, and schedule analysis helps investigate failures. [User guide](https://github.com/facebookexperimental/hermit/blob/main/docs/USER_GUIDE.md)
- **C2:** The architecture separates container/CLI setup, Reverie event interception, and Detcore state and scheduling. That separation supports testing ordinary binaries and different workflows without embedding a scheduler into every application. [Architecture](https://github.com/facebookexperimental/hermit/blob/main/docs/Developers/Architecture.md)

The guide distinguishes deterministic execution from experimental record/replay, and documents dependencies on syscall coverage, stable inputs, and preemption facilities. Match the revision, executable, configuration, and inputs when interpreting a replay claim. The repository was not marked archived when checked.

### 10. [simgrid/simgrid](https://github.com/simgrid/simgrid)

**C++ with language bindings — Mc SimGrid model checker within a distributed-simulation framework. Official GitHub mirror; primary development is on Framagit.** The relevant subsystem is correctness exploration, not merely performance prediction.

- **C1:** Mc SimGrid explores executable pthread, SimGrid, and MPI applications for safety failures and communication nondeterminism. Its documentation distinguishes observation through MPI, synchronization interception, and instrumented memory access. [Model-checking tutorial](https://github.com/simgrid/simgrid/blob/master/docs/source/Tutorial_Model-checking.rst)
- **C2:** Different instrumentation routes let a shared exploration engine cover message passing and shared-memory synchronization.
- **C3:** Stateless exploration forks application executions at choices and applies variants of dynamic partial-order reduction to avoid redundant paths. The tutorial also explains why event visibility and state-space size limit conclusions. [Implementation-oriented tutorial](https://github.com/simgrid/simgrid/blob/master/docs/source/Tutorial_Model-checking.rst)

The project explicitly describes this subsystem as less mature than its performance-simulation facilities. The repository README confirms the substantive, officially maintained mirror relationship.

## Simulation infrastructure embedded in production systems

### 11. [apple/foundationdb](https://github.com/apple/foundationdb)

**C++/Flow — cluster simulator, fault injection, and workload tests inside the database monorepo.** Study the architectural cost and benefits of designing production execution around interfaces that also admit simulation.

- **C1:** The simulator models machines, storage, networking, and correlated failures. Transaction workloads can use structural invariants, such as preserving a ring of key-value relationships, to detect isolation failures. [Simulation and testing](https://github.com/apple/foundationdb/blob/main/documentation/sphinx/source/testing.rst)
- **C2:** Flow supports production and simulated execution; process-local state, network services, file implementations, and fault-injection controls form shared infrastructure used across many workloads. The simulator source shows explicit process context and fault selection rather than a separate toy database model. [Simulator implementation](https://github.com/apple/foundationdb/blob/main/fdbrpc/sim2.cpp)

This is an embedded testing architecture to study, not a standalone package readily applied to unrelated software. The testing documentation also separates simulation from live performance and hardware-failure testing; simulation does not validate every physical behavior.

### 12. [tigerbeetle/tigerbeetle](https://github.com/tigerbeetle/tigerbeetle)

**Zig — VOPR, simulated storage/network, and correctness checkers within the database monorepo.** Especially valuable for studying fault models that preserve the conditions under which recovery is expected to succeed.

- **C1:** VOPR checks safety and liveness while running production consensus and recovery code with substituted clocks, network, and disks. Storage faults are constrained by zone and replica placement; the fault atlas preserves recoverable copies where appropriate. [Simulated storage](https://github.com/tigerbeetle/tigerbeetle/blob/main/src/testing/storage.zig)
- **C2:** The same deterministic infrastructure supports randomized runs and targeted replica scenarios. Additional checkers inspect cluster state, including agreement of caught-up replicas' data files, rather than merely waiting for a crash. [VOPR guide](https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/internals/vopr.md)

Replay is tied to both seed and Git commit. The harness is closely coupled to TigerBeetle, but its environment interfaces, recovery assumptions, and test-oracle design are reusable engineering lessons.

## Controlled scheduling and language-level model checking

### 13. [tokio-rs/loom](https://github.com/tokio-rs/loom)

**Rust — concurrency permutation testing with modeled synchronization.** A strong entry point for studying how instrumentation of common primitives exposes executions ordinary unit tests rarely encounter.

- **C1:** Tests use modeled threads, atomics, locks, and cells to explore concurrency and memory-order effects. The repository explicitly documents incomplete C11 coverage, including load-buffering omissions and treatment of sequentially consistent accesses; results must be interpreted within those limits.
- **C3:** The model builder exposes preemption, branch, time, and permutation bounds, checkpointing, and optional expensive location tracking. These make search cost and debugging cost explicit. [Model builder](https://github.com/tokio-rs/loom/blob/master/src/model.rs)
- **C4:** Dated releases from 2019 through 2023 document atomic-coherence corrections, an `UnsafeCell` false-negative fix, lock fixes, standard-library API parity, and minimum Rust version changes. [Changelog](https://github.com/tokio-rs/loom/blob/master/CHANGELOG.md)

The changelog is evidence of sustained correctness and compatibility work, not a claim about current response times or release cadence.

### 14. [awslabs/shuttle](https://github.com/awslabs/shuttle)

**Rust — randomized controlled-concurrency testing.** Study the deliberate tradeoff between finding useful schedules and attempting exhaustive exploration.

- **C1:** Shuttle controls task scheduling so a discovered failure can be replayed. Its probabilistic concurrency testing scheduler maintains distinct task priorities and selected priority-change points, with explicit invariants in the implementation. [PCT scheduler](https://github.com/awslabs/shuttle/blob/main/shuttle-schedulers/src/pct.rs)
- **C2:** Scheduling is separated from the engine and from wrappers for standard synchronization, Tokio, randomness, and collections. Multiple scheduler implementations share an interface. [Scheduler implementations](https://github.com/awslabs/shuttle/tree/main/shuttle-schedulers/src)
- **C3:** PCT bounds exploration by iterations and bug depth; the implementation learns and updates a step bound as executions reveal longer paths. This offers a concrete search strategy for tests too large for exhaustive checking.

A passing randomized campaign is not a proof that all executions are correct.

### 15. [microsoft/coyote](https://github.com/microsoft/coyote)

**C#/.NET — systematic testing through binary rewriting and controlled runtimes.** Study how ordinary unit-test ergonomics can coexist with an execution engine that owns scheduling choices.

- **C1:** IL rewriting injects control hooks into supported concurrency operations. The engine repeatedly executes tests under different choices and records failing traces for replay. External nondeterminism must be expressed through controlled choices or mocks. [Concurrency unit testing](https://github.com/microsoft/coyote/blob/main/docs/concepts/concurrency-unit-testing.md)
- **C2:** A common testing engine supports task-based code, actor/state-machine code, and modeled external-service outcomes. Configuration and replay are exposed as library APIs, rather than only through a bespoke standalone language.

The history is also instructive about practical compatibility work: framework-target changes, additional thread and synchronization support, uncontrolled nondeterminism detection, and fixes to replay and coverage reporting. [Change history](https://github.com/microsoft/coyote/blob/main/History.md) These changes are not used here to infer a present maintenance commitment.

### 16. [JetBrains/lincheck](https://github.com/JetBrains/lincheck)

**Kotlin/Java — JVM concurrency tests, scenario generation, and result verification.** Useful for examining the separation between producing an execution and deciding whether its results are legal.

- **C1:** Model checking inserts switches at shared-memory and synchronization operations and produces reproducible traces. It assumes sequential consistency; a distinct stress mode can expose real JVM behaviors outside that model but lacks deterministic schedule replay. [Testing strategies](https://github.com/JetBrains/lincheck/blob/master/docs/topics/lincheck-testing-strategies.md)
- **C2:** Declarative operations can be checked against a separate sequential implementation, with configurable verification models and final-state validation. This supports many data structures without embedding a checker into each one. [Result validation](https://github.com/JetBrains/lincheck/blob/master/docs/topics/lincheck-results-validation.md)

The current repository also exposes arbitrary concurrent-code tests. Its documented package/API migration is relevant when comparing older examples to current code; do not assume model checking covers the relaxed Java memory model.

### 17. [barrucadu/dejafu](https://github.com/barrucadu/dejafu)

**Haskell — systematic concurrency testing through abstract concurrency operations.** Study how to test nondeterministic results, deadlocks, and exceptions as explicit outcomes of a computation.

- **C1:** Tests can collect a set of results and representative traces across schedules. The exploration API takes a memory model for unsynchronized `IORef` operations rather than treating every concurrency operation identically. [SCT implementation](https://github.com/barrucadu/dejafu/blob/master/dejafu/Test/DejaFu/SCT.hs)
- **C2:** `MonadConc` and the companion concurrency package abstract real and test execution; HUnit and tasty integration, configurable exploration, and stateful refinement testing provide multiple ways to use the same engine. [Core test modules](https://github.com/barrucadu/dejafu/tree/master/dejafu/Test/DejaFu)
- **C3:** Systematic and randomized modes expose the completeness/cost tradeoff instead of relying solely on repeated OS scheduling.

The API warns that the executions tried and their order can change between releases, which matters when keeping long-lived regression traces.

### 18. [parapluu/Concuerror](https://github.com/parapluu/Concuerror)

**Erlang — stateless model checking of process interleavings.** A particularly well-commented implementation for following dynamic partial-order reduction from theory into a language runtime.

- **C1:** The scheduler records events, detects deadlock and abnormal termination, assigns happens-before relationships, and determines which races can be reversed. [Scheduler source](https://github.com/parapluu/Concuerror/blob/master/src/concuerror_scheduler.erl)
- **C3:** Sleep sets, wakeup sequences, and race analysis reduce redundant interleavings; the source introduction explains the exploration loop and the role of each phase.
- **C4:** The changelog records releases across 2015–2020, OTP support transitions, added tests and coverage infrastructure, receive-pattern changes, and fixes to process/monitor semantics. [Changelog](https://github.com/parapluu/Concuerror/blob/master/CHANGELOG.md)

Its basic testing contract requires a closed, terminating test. The older `mariachris/Concuerror` repository directs users here and is not counted separately. Historical changelog evidence does not establish current OTP compatibility beyond the versions actually checked.

### 19. [ocaml-multicore/dscheck](https://github.com/ocaml-multicore/dscheck)

**OCaml — experimental exploration of instrumented atomic operations.** A smaller implementation with unusually explicit assumptions, useful for studying trace equivalence.

- **C1:** Programs replace their atomics with `TracedAtomic`, spawn modeled domains, and assert invariants. The README requires deterministic tests, no races on non-atomic variables, communication through atomics, and progress sufficient for exploration to finish.
- **C3:** DPOR modes address combinatorial schedule growth. An optional trace tracker, used to test the checker itself, defines dependence through same-variable accesses with at least one write and builds keys for comparing equivalent causal traces. This makes the reduction's validation machinery inspectable. [Trace tracker](https://github.com/ocaml-multicore/dscheck/blob/main/src/trace_tracker.ml)
- **C2:** The traced atomic interface separates algorithm code from the exploration machinery and supplies reusable testing operations. [Public instrumented interface](https://github.com/ocaml-multicore/dscheck/blob/main/src/tracedAtomic.mli)

The narrow assumptions are part of the tool's value as a study target, and should not be mistaken for support for arbitrary OCaml synchronization.

### 20. [javapathfinder/jpf-core](https://github.com/javapathfinder/jpf-core)

**Java — extensible model-checking VM for Java bytecode.** Study a VM-level alternative to replacing synchronization libraries or merely perturbing the host scheduler.

- **C1:** JPF represents application state, transitions, thread choices, and data choices explicitly so searches can explore alternative program executions. [Choice-generator architecture](https://github.com/javapathfinder/jpf-core/blob/master/docs/devel/ChoiceGenerators.md)
- **C2:** Typed choice generators separate domain-specific input selection from VM mechanics; configuration can select and parameterize generators without rewriting a test driver.
- **C3:** On-the-fly partial-order reduction identifies scheduling-relevant instructions using instruction kind, object reachability, and thread/lock information. Its interaction with garbage-collector reachability is an instructive example of reusing existing runtime analysis. [POR design](https://github.com/javapathfinder/jpf-core/blob/master/docs/devel/Partial-Order-Reduction.md)

This verifies execution in JPF's modeled environment, with corresponding library and runtime compatibility requirements; it is not a guarantee about every behavior of an arbitrary production JVM.

## Weak-memory and low-level synchronization verification

### 21. [dvyukov/relacy](https://github.com/dvyukov/relacy)

**C++ — header-based verifier for synchronization algorithms.** A good study target when correctness depends on atomic semantics rather than only coarse task ordering.

- **C1:** Modeled atomics dispatch by memory order, validate permitted compare-exchange failure orders, distinguish weak/strong compare-exchange, and pass operations into thread/context state. This makes subtle synchronization semantics visible in code. [Atomic implementation](https://github.com/dvyukov/relacy/blob/master/relacy/atomic.hpp)
- **C2:** Replacement primitives and parameterized test execution allow different data structures and algorithms to use a common verifier. Random, context-bounded, and full-search schedulers share configurable test parameters and history reporting. [Test parameters](https://github.com/dvyukov/relacy/blob/master/relacy/test_params.hpp)

The repository documents current compiler-matrix testing and optional substitution of `std` types, but also warns that standard-header interception can break as toolchains evolve. Read the modeled semantics rather than assuming complete equivalence with every contemporary C++ feature.

### 22. [MPI-SWS/genmc](https://github.com/MPI-SWS/genmc)

**C++/LLVM — stateless model checking of C/C++ and experimental Rust inputs. Official periodically updated mirror of an internal repository.** Particularly useful for comparing language-level and hardware-oriented memory models.

- **C1:** GenMC supports RC11, SC, and IMM, with explicit discussion of their differing allowed outcomes and how compilation affects interpretation. It checks races and memory errors within supported models. [Feature and semantics guide](https://github.com/MPI-SWS/genmc/blob/master/doc/manual/features.md)
- **C3:** Barrier-aware checking reduces unnecessary exploration around barriers, rather than treating every synchronization operation as an unrelated choice. The guide supplies a concrete example of this reduction.
- **C2:** The implementation organizes execution events, labels, visitors, interpreter hooks, and driver handlers as extension points. [Development architecture](https://github.com/MPI-SWS/genmc/blob/master/doc/development.md)

The mirror status and supported LLVM/Rust combinations are stated in the repository README; avoid assuming the public branch contains every internal change.

### 23. [nidhugg/nidhugg](https://github.com/nidhugg/nidhugg)

**C++/LLVM — stateless checking of pthread programs under several memory models.** An instructive implementation family for distinguishing hardware memory behavior from ordinary thread interleaving.

- **C1:** It targets SC, TSO, PSO, POWER, and a documented under-approximation of ARM. The manual requires deterministic steps and finite executions, or explicit imposed bounds. [Manual source](https://github.com/nidhugg/nidhugg/blob/master/doc/manual.tex)
- **C3:** Dynamic partial-order reduction explores representatives of execution classes; loop/search bounds and optional IR transformations address otherwise unmanageable execution spaces. The manual describes the compilation, transformation, and checking pipeline.
- **C2:** Operating at LLVM IR allows the same checking infrastructure to accept different compiled C/C++ tests using supported pthread operations. [Implementation tree](https://github.com/nidhugg/nidhugg/tree/master/src)

The checked README supports LLVM 8–19 but disables ARM and POWER models with LLVM 15 and later. This is a material configuration limitation, not a minor installation detail.

## Stress harnesses and concurrency-result validation

### 24. [openjdk/jcstress](https://github.com/openjdk/jcstress)

**Java — concurrency stress harness, generated tests, and handwritten litmus tests.** This is probabilistic testing on real JVM/hardware behavior, not deterministic simulation.

- **C1:** Tests classify observed concurrent outcomes as allowed or forbidden and exercise JVM, library, and hardware concurrency semantics. The harness collects outcomes from multiple actors over many state instances; memory-model explanations accompany its samples. [Sample entry points](https://github.com/openjdk/jcstress/tree/master/jcstress-samples/src/main/java/org/openjdk/jcstress/samples)
- **C3:** Sampling throughput is part of the testing problem. `WorkerSync` makes actor rendezvous, state-update coordination, contended layout, and alternative spinning/yielding/parking policies explicit. [Worker synchronization](https://github.com/openjdk/jcstress/blob/master/jcstress-core/src/main/java/org/openjdk/jcstress/infra/runners/WorkerSync.java)
- **C2:** An annotation-based harness and result-grading model support new tests beyond the bundled suite.

Failure to observe a forbidden outcome does not prove its impossibility. Its value alongside schedule model checkers is exposure to actual compiler and machine behavior.

### 25. [jepsen-io/jepsen](https://github.com/jepsen-io/jepsen)

**Clojure — distributed fault testing, workload generation, history capture, and checking.** Included as an end-to-end concurrency-testing framework; executions against real systems are not generally deterministic.

- **C1:** Logical clients issue concurrent operations while a nemesis introduces faults. Recorded invocation/completion histories are checked for correctness, separating what the system did from what the client hoped it did. [Namespace and execution architecture](https://github.com/jepsen-io/jepsen/blob/main/doc/whats-here.md)
- **C2:** OS setup, database lifecycle, clients, generators, nemeses, and checkers have distinct protocols. Composable generators are interpreted by a worker engine; composed fault packages include workload and reporting metadata. This supports databases, coordination services, and other distributed state machines.

Study the separation of workload, fault injection, observation, and oracle. It offers a useful comparison with in-process simulators: tests exercise real deployment behavior, but a saved history is not itself deterministic replay of the original execution. The monorepo is counted once.

### 26. [anishathalye/porcupine](https://github.com/anishathalye/porcupine)

**Go — executable-specification linearizability checker and history visualizer.** An oracle that can be paired with a simulator or a real-system stress harness; it does not generate schedules itself.

- **C1:** The checker compares a concurrent history with a sequential specification. Its model API requires pure state transitions and consistent equality/hash behavior; call/return events and timed operations have explicit representations. [Model contracts](https://github.com/anishathalye/porcupine/blob/master/model.go)
- **C2:** User-provided initialization, transition, equality, partitioning, and description functions support different object semantics and diagnostic visualizations, including nondeterministic specifications.
- **C3:** Partitioning can split independent histories into smaller checks; optional state hashing reduces equality work. Both optimizations are governed by semantic contracts rather than being unconditional shortcuts. [Model contracts and partitioning](https://github.com/anishathalye/porcupine/blob/master/model.go)

Incorrect specifications or invalid partitions can invalidate the result. The project's headline benchmark multipliers are intentionally not repeated here; comparative performance was not independently measured.

## Search coverage, verification, and limitations

Discovery used more than six distinct live-search formulations, including: Rust async simulation runtimes; systematic C#/JVM concurrency testing; FoundationDB-style cluster simulation; Go source/runtime simulation; Haskell IO/STM schedule exploration; Erlang DPOR; OCaml atomic checking; C/C++ weak-memory tools; native Linux determinization; linearizability checkers; MPI/network simulation; and Java, TypeScript, and Python alternatives. Later broad queries mostly returned existing candidates, resource lists, adjacent simulators, or additional small/new implementations of already represented approaches. The selection extends slightly beyond 25 to retain distinct language and instrumentation approaches rather than forcing them into one representative.

Every retained repository's public GitHub page was opened, including redirects and default-branch metadata. Each was also checked against an additional primary document or source file containing implementation or architecture detail. Source bodies, not search snippets alone, ground the entries. The GitHub anonymous API hit a shared rate limit; verification continued through public repository pages and raw source reads. No repositories were cloned, dependencies installed, or candidate code executed. All retained repositories were unarchived when checked; this is not a blanket claim of active maintenance. Only explicit, dated evolution evidence is used for C4.

GenMC and SimGrid are labeled official mirrors. AnySystem's old organization URL was normalized to its current owner. Old Concuerror repositories and ordinary forks were not counted independently. CDSChecker and Knossos were investigated but not retained: this selection favors the documented model boundaries and integration approaches above; CDSChecker's historical GitHub copy also pointed to external project/source hosting, while Knossos overlaps the retained history-checking coverage and its README explicitly cautions about algorithm confidence. This is a selection decision, not evidence that either project lacks research value.

Resource lists, tutorials, general-purpose mocking clocks, generic property-test libraries, and simulators without a demonstrated software-correctness testing role were excluded. Specification-only model checkers and commercial systems without a substantive public implementation—such as the Antithesis platform itself—are outside this report's repository scope. Python searches found additional promising candidates, but no standalone Python scheduler received the same retained-entry verification depth; Python process implementations are represented through AnySystem. The report therefore makes no claim to exhaust that sub-ecosystem.

The study recommendations and C1–C4 judgments are grounded engineering assessments of the cited material. Runtime fidelity, weak-memory coverage, determinism, and test-oracle correctness remain separate questions. Reproducibility generally depends on stable code, configuration, inputs, and instrumentation coverage; no seed or passing test removes those boundaries.
