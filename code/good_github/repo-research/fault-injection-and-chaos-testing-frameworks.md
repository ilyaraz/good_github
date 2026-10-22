# Fault injection and chaos testing frameworks

Research date: **2026-10-09**.

This selection covers 26 GitHub repositories implementing software fault injection, chaos experiment orchestration, failure-oriented distributed-systems simulation, and storage or numerical fault models. It spans cluster-wide experiments, application instrumentation, constrained-device libraries, and research systems. Inclusion means that at least two of the criteria below have concrete supporting evidence; it does not mean every component is exemplary or that every project is suitable for deployment today. Descriptions of what engineers can learn are grounded assessments of the cited designs and code, rather than benchmark or correctness certifications.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions serving multiple use cases. **C3** — performance or resource constraints addressed through an understandable architecture. **C4** — demonstrated evolution across years, accompanied by compatibility work, testing, or complexity management.

Canonical repository identities, default branches, and archive flags were checked through the GitHub API. Source and documentation links below were opened and read. Archive status and older activity are called out where material; a recent push alone is not used to award C4 or assert active maintenance.

## Cluster and infrastructure experiment orchestration

### 1. [chaos-mesh/chaos-mesh](https://github.com/chaos-mesh/chaos-mesh)

**Go; Kubernetes chaos platform.** Study how fault injection becomes a reconciled resource lifecycle, including recovery after partial work, pauses, deletion, and repeated reconciliation. The relevant implementation is the controller subsystem and its node-level execution integrations.

**C1:** The common pipeline explicitly orders finalizer initialization, desired phase, conditions, target records, and finalizer cleanup. Its design explains an earlier race caused by independently scheduled reconcilers and why recovery must precede releasing a deleting object. **C2:** Individual fault implementations provide per-target Apply/Recover operations; the shared machinery owns selection, persistence, retries, and lifecycle transitions. Field ownership and composition boundaries make this unusually useful controller-design material. Start with the [controller architecture](https://github.com/chaos-mesh/chaos-mesh/blob/master/controllers/README.md) and the [ordered reconciliation pipeline](https://github.com/chaos-mesh/chaos-mesh/blob/master/controllers/common/pipeline/README.md).

### 2. [litmuschaos/litmus](https://github.com/litmuschaos/litmus)

**Go and TypeScript; chaos control-plane monorepo and experiment documentation.** Study the relationship between an experiment definition, a selected application, execution infrastructure, and a recorded verdict. The relevant subsystem is ChaosCenter plus the documented chaos-resource contract; several operators and fault libraries belong to companion repositories and are not counted separately here.

**C1:** Probes distinguish checks before, after, and during injection, with separate retry, timeout, polling, and stop-on-failure semantics. Their results contribute to the experiment verdict, avoiding the assumption that successful injection proves resilience. **C2:** ChaosExperiment, ChaosEngine, and ChaosResult separate reusable fault templates, workload binding, and outcomes; workflows compose experiments. Read the [architecture overview](https://github.com/litmuschaos/litmus/blob/master/README.md) and the [probe execution contract](https://github.com/litmuschaos/litmus/blob/master/mkdocs/docs/experiments/concepts/chaos-resources/probes/litmus-probes.md). The latter describes the ChaosEngine model, not a guarantee that every ChaosCenter version exposes identical configuration.

### 3. [chaosblade-io/chaosblade](https://github.com/chaosblade-io/chaosblade)

**Go; experiment CLI, records, and executor integration within a larger repository.** The study target is the traditional CLI/executor subsystem, rather than treating newer adjacent components as necessary to understand fault injection.

**C1:** Destroying an experiment has distinct failure cases: undoing the injected fault, deleting its local record, and removing its Kubernetes resource can succeed or fail independently. The code preserves these distinctions and makes forced removal explicit. **C2:** The experiment model factors target, scope, matcher, and action; command specifications map actions and flags onto executors for different environments. This is useful for studying a common model over OS, container, and application-specific injectors. Entry points: the [experiment model and interfaces](https://github.com/chaosblade-io/chaosblade/blob/master/docs/chaos_experiment_model_EN.md) and [destroy/recovery orchestration](https://github.com/chaosblade-io/chaosblade/blob/master/cli/cmd/destroy.go).

### 4. [DataDog/chaos-controller](https://github.com/DataDog/chaos-controller)

**Go with Linux-level injection mechanisms; Kubernetes disruption controller.** This is a useful comparison with daemon-based platforms: it creates injector pods for specific targets and disruptions.

**C1:** The design distinguishes partial injection, cleanable versus vanished targets, and cleanup failures that must keep finalizers in place. Injector signal handling and retry behavior address recovery when the injection process itself is disrupted. **C2:** Resource reconciliation is separated from a common injector lifecycle and fault-specific implementations. **C3:** The architecture explicitly reduces idle resource consumption by creating injection pods on demand instead of reserving a daemon on every node. This is an architectural resource tradeoff, not an independently measured speed claim. Read the [lifecycle design](https://github.com/DataDog/chaos-controller/blob/main/docs/design.md) and [deployment/resource rationale](https://github.com/DataDog/chaos-controller/blob/main/README.md).

### 5. [krkn-chaos/krkn](https://github.com/krkn-chaos/krkn)

**Python; Kubernetes/OpenShift chaos runner with health and telemetry integration.** Study how a scenario runner coordinates injection, rollback, stabilization, and observations instead of treating a fault command as the entire experiment.

**C1:** The scenario base implementation catches plugin failures, uses a signal context, invokes recorded rollback actions on unsuccessful execution, and retains exit status and timing while attempting log and event collection. These are concrete failure-within-the-test concerns. **C2:** Scenario plugins expose a common execution/type contract; health checks have their own factory, type registration, threaded monitoring, stop event, and telemetry queue. The two extension systems support new faults and independent observations. Entry points: [scenario lifecycle implementation](https://github.com/krkn-chaos/krkn/blob/main/krkn/scenario_plugins/abstract_scenario_plugin.py) and [health-check architecture](https://github.com/krkn-chaos/krkn/blob/main/krkn/health_checks/README.md).

### 6. [chaostoolkit/chaostoolkit-lib](https://github.com/chaostoolkit/chaostoolkit-lib)

**Python; reusable Chaos Toolkit execution engine.** This selects the substantive core library, rather than separately counting its CLI and many integration extensions.

**C1:** The runner coordinates initial hypothesis gating, continuous background checks, activities, rollback policy, interruption, and a structured execution journal. The distinction between interruption, failed probes, and deviation is worth studying. **C2:** Experiments, strategies, controls, event handlers, and activity providers allow the same lifecycle to drive different target systems. **C4:** The changelog documents evolution from 2017 through 2026, including extension-signature compatibility, Python support changes, interrupted rollback reporting, and a 2026 fix preventing SIGTERM from being misclassified as an ordinary activity failure. Start with the [runner](https://github.com/chaostoolkit/chaostoolkit-lib/blob/master/chaoslib/run.py) and [changelog](https://github.com/chaostoolkit/chaostoolkit-lib/blob/master/CHANGELOG.md).

### 7. [powerfulseal/powerfulseal](https://github.com/powerfulseal/powerfulseal)

**Python; policy-driven Kubernetes and host experiments.** Useful for studying a relatively direct scenario interpreter with cloud drivers, inventories, actions, probes, and metrics. The [GitHub API](https://api.github.com/repos/powerfulseal/powerfulseal) recorded its last push in November 2023; it was not archived when checked, but this report does not imply current maintenance.

**C1:** A scenario carries retry policies, early failure, accumulated cleanup actions, and a success/failure result. This exposes practical interactions between disruptive steps and recovery checks; it is not a claim that cleanup covers every possible exception. **C2:** Action classes separate pods, nodes, HTTP probes, cloning, and external commands, while collector interfaces decouple observation from execution. Read the [scenario interpreter](https://github.com/powerfulseal/powerfulseal/blob/master/powerfulseal/policy/scenario.py) and [metrics/extensibility documentation](https://github.com/powerfulseal/powerfulseal/blob/master/docs/6_in-depth.md).

### 8. [Netflix/chaosmonkey](https://github.com/Netflix/chaosmonkey)

**Go; Spinnaker-oriented randomized instance termination.** Retained for its focused scheduling model and extension boundaries, rather than as a universal modern chaos platform. The [GitHub API](https://api.github.com/repos/Netflix/chaosmonkey) recorded its last push in January 2025 and did not mark it archived.

**C1:** Termination selection combines enabled-group eligibility, randomized scheduling, mean intervals, and minimum spacing. The documentation explicitly explains how minimum spacing changes the resulting probability distribution instead of pretending the requested mean remains exact. **C2:** Custom constrainers filter schedules through a defined interface, separating organization-specific limits from scheduling machinery. Engineers can study the boundary between stochastic behavior and operational policy. Entry points: [termination semantics](https://github.com/Netflix/chaosmonkey/blob/master/docs/Termination-behavior.md) and the [constrainer extension contract](https://github.com/Netflix/chaosmonkey/blob/master/docs/plugins/Constrainer.md).

## Network and container fault injection

### 9. [Shopify/toxiproxy](https://github.com/Shopify/toxiproxy)

**Go; programmable TCP fault proxy.** Study how faults are inserted into live byte streams while applications use ordinary TCP connections.

**C1:** Adding or removing a toxic interrupts running stages, rewires channels, drains buffered data, and handles links that closed during the change. These operations expose real shutdown and concurrency hazards. **C2:** Directional ToxicLink pipelines, per-connection state, and toxic interfaces support reusable latency, bandwidth, reset, timeout, and stream-shaping behavior. **C4:** The changelog records work from 2015 onward on closed-channel panics, race-sensitive tests, interruptible streams, deadline-aware writes, CLI compatibility, and end-to-end testing. Entry points: [live pipeline implementation](https://github.com/Shopify/toxiproxy/blob/main/link.go) and [evolution and regression history](https://github.com/Shopify/toxiproxy/blob/main/CHANGELOG.md).

### 10. [alexei-led/pumba](https://github.com/alexei-led/pumba)

**Go; container lifecycle disruption, network emulation, and resource stress.** Its injection operates through container runtimes and Linux networking rather than an application-level TCP proxy.

**C1:** Network configuration has ownership and cleanup semantics: the documented implementation refuses foreign or stale root queue disciplines, applies its own identifiable discipline, and explains why SIGKILL can prevent cleanup. Target resolution also rejects ambiguous matches and unsupported IPv6 targets instead of silently choosing a target. **C2:** Runtime integration, container selection, helper containers sharing network namespaces, and composable network effects support varied deployment/test setups. Study the [network architecture and fault semantics](https://github.com/alexei-led/pumba/blob/master/docs/network-chaos.md); the [repository overview](https://github.com/alexei-led/pumba/blob/master/README.md) places those mechanisms alongside lifecycle and stress commands.

## Distributed-system histories, adaptive exploration, and simulation

### 11. [jepsen-io/jepsen](https://github.com/jepsen-io/jepsen)

**Clojure; distributed-systems verification with fault injection.** The relevant subsystem is the Jepsen library under the monorepo's jepsen directory, especially nemeses, generators, clients, histories, and checkers.

**C1:** Failures create uncertain operation outcomes: a timed-out operation may still have taken effect. Jepsen's tutorial connects that ambiguity to consistency checking while partitioning and healing a cluster. **C2:** Nemesis setup/invoke/teardown protocols, reflection, composition, and validation wrappers separate reusable fault behavior from a particular database test. Engineers can study how fault schedules and ordinary workloads share a generator model while correctness is evaluated from histories. Entry points: [fault-injection tutorial](https://github.com/jepsen-io/jepsen/blob/main/doc/tutorial/05-nemesis.md) and [nemesis protocols and implementations](https://github.com/jepsen-io/jepsen/blob/main/jepsen/src/jepsen/nemesis.clj). Tutorial database versions are illustrative, not current deployment advice.

### 12. [dsfuzz/mallory](https://github.com/dsfuzz/mallory)

**Rust, Clojure, and LLVM instrumentation; adaptive distributed-system fault testing.** A research implementation associated with CCS 2023; its [recorded last push](https://api.github.com/repos/dsfuzz/mallory) was December 2023. It includes a modified Jepsen distribution, but is retained separately for the substantial Rust mediator and feedback-guided scheduler, not for the copied Jepsen code.

**C1:** Scheduling connects runtime observations, time windows, fault actions, delayed rewards, and inferred states. The Q-learning scheduler explicitly tracks requested rewards and synchronizes its state and value tables. **C2:** Scheduler, state-manager, action-policy, feedback, and nemesis-interface boundaries allow different exploration strategies over existing system-specific fault actions. Study the [integration/design overview](https://github.com/dsfuzz/mallory/blob/main/README.md) and [Q-learning scheduler](https://github.com/dsfuzz/mallory/blob/main/mediator/src/nemesis/schedules/qlearning/agent.rs). No claim of universally superior bug-finding performance is made.

### 13. [filibuster-testing/filibuster-java-instrumentation](https://github.com/filibuster-testing/filibuster-java-instrumentation)

**Java; service-level fault injection and generated resilience-test variations.** The repository includes the exploration engine as well as instrumentation; its [recorded last push](https://api.github.com/repos/filibuster-testing/filibuster-java-instrumentation) was January 2024, so it should be approached with dependency-compatibility checks.

**C1:** The engine associates outgoing calls with distributed execution indices, distinguishes abstract fault plans from observed concrete executions, and injects failures at matching invocations. **C2:** Analysis configurations and fault representations support exceptions, transformed responses, latency, and multiple client integrations. **C3:** BFS/DFS work collections, duplicate-execution checks, optional suppression of combinations, and redundant-injection avoidance explicitly address the cost of combinatorial exploration. Start with the [scope and integration overview](https://github.com/filibuster-testing/filibuster-java-instrumentation/blob/main/README.md) and [FilibusterCore implementation](https://github.com/filibuster-testing/filibuster-java-instrumentation/blob/main/src/main/java/cloud/filibuster/junit/server/core/FilibusterCore.java).

### 14. [tokio-rs/turmoil](https://github.com/tokio-rs/turmoil)

**Rust; deterministic distributed-system simulation.** Study failure tests that execute many logical hosts on one thread, with controlled network behavior rather than real machines.

**C1:** Seeded execution, partitions, held in-flight messages, repair, and release make timing-sensitive failure sequences reproducible. The documented unstable filesystem model distinguishes pending from durable writes and discards pending data on simulated crashes. **C2:** Hosts are asynchronous programs; simulated networking mirrors Tokio interfaces, while a simulation object supplies test control and observation. This makes the framework reusable across services that can substitute their I/O boundary. The [crate-level architecture and API guide](https://github.com/tokio-rs/turmoil/blob/main/crates/turmoil/src/lib.rs) is the main entry point. Filesystem and barrier facilities are explicitly marked unstable; simulation is evidence about the modeled environment, not every real kernel behavior.

### 15. [madsim-rs/madsim](https://github.com/madsim-rs/madsim)

**Rust; deterministic asynchronous runtime and simulated dependency ecosystem.** Useful for studying the engineering needed to bring an existing distributed application into a controlled failure environment.

**C1:** The network implementation combines node/socket identity, protocol-specific address binding, directed partitions, randomized loss, and latency under a shared random source. Resetting nodes closes their simulated sockets. **C2:** The repository provides the runtime plus adapters for Tokio, Tonic, etcd clients, Kafka clients, and S3-facing code; test builds switch to simulated implementations. The documentation also makes clear that uncontrolled I/O and randomness must be eliminated for determinism. Read the [integration model and constraints](https://github.com/madsim-rs/madsim/blob/main/README.md) and [network implementation](https://github.com/madsim-rs/madsim/blob/main/madsim/src/sim/net/network.rs). Adapter compatibility must be evaluated against the application's dependency graph.

## In-process failpoints and application chaos

### 16. [pingcap/failpoint](https://github.com/pingcap/failpoint)

**Go; compiler-checked failpoint markers, source rewriting, and runtime control.** Study how precise failure hooks can remain valid Go while being transformed for fault-enabled builds.

**C1:** Runtime control includes synchronized evaluation, enabling a point while holding its lock for preparatory work, pause-until-disable behavior, and context-based selection for parallel tests. **C2:** Named failpoints accept programmable actions and control-flow markers rather than a single fixed failure type. **C3:** The design addresses normal-build overhead through empty marker functions and exclusion of injected bodies; source rewriting expands enabled markers into ordinary conditional code. This is a design property, not a measured overhead figure. Entry points: [rewriting and control model](https://github.com/pingcap/failpoint/blob/master/README.md) and [runtime failpoint implementation](https://github.com/pingcap/failpoint/blob/master/failpoint.go).

### 17. [tikv/fail-rs](https://github.com/tikv/fail-rs)

**Rust; named, runtime-configurable failpoints.** A compact library with meaningful concurrency and lifecycle problems, especially when integrated into parallel test suites.

**C1:** Failpoints are global state. FailScenario serializes participating scenarios, cleans state after earlier failures, and uses Drop-based teardown that wakes paused points before clearing the registry. The documentation warns that unrelated tests can still trigger globally enabled points. **C2:** The macro and action grammar support typed early returns, panics, sleeps, pauses, callbacks, probabilities, and bounded trigger counts. Compile-time feature selection separates fault-enabled tests from normal builds. Study the [library implementation and embedded API guide](https://github.com/tikv/fail-rs/blob/master/src/lib.rs), especially FailScenario, cfg, and the fail_point macro. The explicit isolation limitations are as instructive as the convenience API.

### 18. [albertito/libfiu](https://github.com/albertito/libfiu)

**C with Python bindings; userspace fault-injection library and POSIX interposition.** This is the author's substantive GitHub **mirror**, not the primary hosting location; the [upstream project site](https://blitiri.com.ar/p/libfiu/) points to the blitiri-hosted source repository.

**C1:** Interposition can make the injector recursively call its own failure hooks, including during allocation while holding a registry lock. The implementation uses thread-local recursion suppression, reader/writer locking, and separate one-shot protection to address those hazards. **C2:** Application-side failure points are separated from a control API supporting named groups, probabilistic failure, external callbacks, and test-only builds. Study the [user/API guide](https://github.com/albertito/libfiu/blob/master/doc/guide.rst) and [core implementation](https://github.com/albertito/libfiu/blob/master/libfiu/fiu.c). Mirror status should not be mistaken for an independently evolving fork.

### 19. [bytemanproject/byteman](https://github.com/bytemanproject/byteman)

**Java; bytecode injection, event-condition-action rules, and test integration.** Although broader than chaos testing, fault injection for multithreaded and multi-JVM applications is an explicit original purpose.

**C1:** Rules can force returns or exceptions and coordinate independent threads through rendezvous operations. Runtime insertion/removal also raises class transformation and restoration concerns; the guide distinguishes removable rules from the agent itself, which cannot simply be unloaded. **C2:** An event-condition-action language and replaceable helper objects separate where injection occurs, when it fires, and what it does. JUnit/TestNG integration makes those mechanisms reusable in application tests. Read the [rule-engine introduction](https://github.com/bytemanproject/byteman/blob/main/docs/asciidoc/src/main/asciidoc/chapters/Introduction.adoc) and [agent lifecycle/usage guide](https://github.com/bytemanproject/byteman/blob/main/docs/asciidoc/src/main/asciidoc/chapters/Using-Byteman.adoc). Older examples in the guide should not be treated as a current JDK support matrix.

### 20. [codecentric/chaos-monkey-spring-boot](https://github.com/codecentric/chaos-monkey-spring-boot)

**Java; Spring application faults through watchers and assaults.** Study injection at framework-managed boundaries rather than instrumenting arbitrary methods globally.

**C1:** Coverage depends on bean creation, public-method interception, and the difference between AOP watchers and outgoing-client customizers. The documentation explicitly identifies clients constructed outside the Spring context as uninstrumented. **C2:** Watchers select application boundaries independently from latency, exception, and runtime assaults. **C4:** Releases show concrete compatibility work across years: the 2023 release moved to Spring Boot 3/Java 17 and fixed watcher/bean issues; the 2026 release moved to Spring Boot 4 and removed a deprecated setting. Entry points: [watcher mechanics](https://github.com/codecentric/chaos-monkey-spring-boot/blob/main/chaos-monkey-docs/src/main/asciidoc/watcher.adoc) and release notes for [3.0.0](https://github.com/codecentric/chaos-monkey-spring-boot/releases/tag/v3.0.0) and [4.0.0](https://github.com/codecentric/chaos-monkey-spring-boot/releases/tag/v4.0.0).

### 21. [App-vNext/Polly](https://github.com/App-vNext/Polly)

**C#; Simmy chaos strategies inside the Polly resilience monorepo.** Only the Simmy subsystem under src/Polly.Core/Simmy is selected here. The earlier standalone Simmy repository is not counted again.

**C1:** Strategy order changes which calls experience latency or short-circuiting faults. The latency implementation propagates the execution context, uses a TimeProvider, checks cancellation before invoking the application callback, and returns cancellation as an outcome. **C2:** Fault, latency, outcome, and behavior strategies compose with the same resilience pipeline and context-sensitive enable/rate generators used to target individual operations. This is useful for studying how injected faults exercise retries and circuit breakers without replacing the surrounding execution model. Read the [chaos composition guide](https://www.pollydocs.org/chaos/index.html) and [latency strategy implementation](https://github.com/App-vNext/Polly/blob/main/src/Polly.Core/Simmy/Latency/ChaosLatencyStrategy.cs).

### 22. [nestlabs/nlfaultinjection](https://github.com/nestlabs/nlfaultinjection)

**C++; portable fault-injection API for constrained systems. Archived.** Its [recorded last push](https://api.github.com/repos/nestlabs/nlfaultinjection) was December 2020. Retained as a compact architectural study, with no claim of current platform support.

**C1:** Configuration can race with fault execution. The API specifies caller-supplied locking and explains how callbacks must avoid reacquiring a non-reentrant mutex; tests check lock boundaries and callback behavior. **C2:** Per-module managers, named fault identifiers, callback chains, counters, skip/fail counts, optional arguments, and reboot hooks allow application-specific faults through a common mechanism. **C3:** Applications supply record storage and synchronization, while the stated dependency is the C standard library, reflecting constrained-device resource and portability goals. Entry points: the [manager/record contract](https://github.com/nestlabs/nlfaultinjection/blob/master/include/nlfaultinjection.hpp) and [behavioral tests](https://github.com/nestlabs/nlfaultinjection/blob/master/tests/TestFaultInjection.cpp).

## Filesystem failures and crash consistency

### 23. [dsrhaslab/lazyfs](https://github.com/dsrhaslab/lazyfs)

**C++17; FUSE filesystem with a controlled page cache. Research prototype.** Study data loss from unsynchronized writes and partial persistence, which ordinary process termination may fail to reproduce reliably.

**C1:** Faults distinguish whole unsynced-cache loss, selected writes from a sequence, and selected pieces of one write. Operation occurrence and before/after timing determine when failure happens; a completion FIFO allows tests to wait before checking consistency. **C2:** A filesystem layer plus the libpcache subsystem and configurable fault objects make the mechanism reusable across applications using the mounted path. Validation checks allowable operations, persistence indices, part sizes, and single-path versus two-path operations. Read the [fault model and control interface](https://github.com/dsrhaslab/lazyfs/blob/main/README.md) and [fault-type validation](https://github.com/dsrhaslab/lazyfs/blob/main/libs/libpcache/src/faults.cpp). Its documented backend tests do not establish identical semantics on all filesystems.

### 24. [scylladb/charybdefs](https://github.com/scylladb/charybdefs)

**C/C++; FUSE fault filesystem with a Thrift control plane. Archived.** The [recorded last push](https://api.github.com/repos/scylladb/charybdefs) was April 2021. Unlike LazyFS's controlled persistence model, this implementation emphasizes failures at filesystem-operation boundaries.

**C1:** Operation wrappers must preserve FUSE return conventions while substituting errors, delays, or caller termination. Two-path operations expose additional targeting choices; the repository's recovery-test description checks committed data after injected failures and restart. **C2:** A Thrift service independently configures operation lists, file-pattern matching, error selection, probability, delays, and clearing faults. This makes the same mounted filesystem usable by different test drivers. Entry points: [filesystem operation wrappers](https://github.com/scylladb/charybdefs/blob/master/charybde_ops.cc) and the [control-plane IDL](https://github.com/scylladb/charybdefs/blob/master/server.thrift). The IDL labels automatic delay as unimplemented; this report does not count it as a working capability.

## Instruction-level and numerical fault models

### 25. [DependableSystemsLab/LLTFI](https://github.com/DependableSystemsLab/LLTFI)

**C/C++ and Python; LLVM-level fault injection for native and compiled ML applications.** A substantive extension of LLFI, selected once here rather than duplicating its predecessor. Relevant subsystems are the LLVM passes, selector framework, runtime injection library, and experiment drivers.

**C1:** Injection must maintain correspondence among static instruction identity, dynamic occurrence, register position/width, and selected bit mutations. Runtime logs preserve those identifiers so an observed failure can be traced back to the injected event. **C2:** Independent instruction/register selectors and fault-injector registries separate targeting from mutation. Compile-time passes communicate with the runtime through explicit metadata, configuration, and logs; ML selectors add operator-region targeting. Study the [architecture and pass pipeline](https://github.com/DependableSystemsLab/LLTFI/blob/master/architecture.md) and [runtime injector](https://github.com/DependableSystemsLab/LLTFI/blob/master/runtime_lib/FaultInjectionLib.c). This is software modeling of hardware-like faults, not validation of a physical device's fault distribution.

### 26. [pytorchfi/pytorchfi](https://github.com/pytorchfi/pytorchfi)

**Python/PyTorch; runtime weight and neuron perturbation framework.** A smaller research-oriented codebase that complements LLVM instrumentation with model-level hooks. Its [recorded last push](https://api.github.com/repos/pytorchfi/pytorchfi) was July 2024; current PyTorch compatibility was not execution-tested.

**C1:** Injection involves tensor dimensions, layer traversal, batch-specific locations, hook removal, and model-copy isolation. The included signed bit-flip model quantizes against a layer range, applies two's-complement manipulation, and converts back while preserving dtype; it should not be described as arbitrary IEEE floating-point bit flipping. **C2:** The core separates model profiling and injection placement from pluggable mutation functions and reusable per-layer/per-batch sampling policies. Entry points: [FaultInjection core](https://github.com/pytorchfi/pytorchfi/blob/master/pytorchfi/core.py) and [neuron error models](https://github.com/pytorchfi/pytorchfi/blob/master/pytorchfi/neuron_error_models.py). The code includes uneven validation, so the selection highlights instructive numerical and instrumentation mechanics rather than uniformly defensive implementation.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations, including Kubernetes chaos platforms; network proxies and emulation; C/Rust/Go failpoints; Java instrumentation; Python experiment orchestration; Jepsen and service-level testing; deterministic Rust simulation; filesystem crash/data-loss injection; LLVM and PyTorch numerical injection; eBPF/syscall injection; embedded C/C++ frameworks; feedback-guided distributed fuzzing; and .NET/Simmy integration. Follow-up searches also checked Erlang and alternative Python/network tools. Canonical GitHub API metadata and source trees were then inspected, followed by actual documentation, implementation, test, or release-content reads for every retained repository.

The 26 entries extend the usual 15–25 guide slightly to preserve distinct coverage of .NET, constrained-device injection, adaptive research systems, and numerical fault models. Later searches largely returned already-covered projects, small wrappers, teaching/demo repositories, or adjacent tools with weaker framework fit. Stars were not used as quality evidence. The list intentionally counts Chaos Toolkit's core once, selects LLTFI without separately counting LLFI, and selects Polly's integrated Simmy subsystem without double-counting standalone Simmy. Mallory is the explicit exception for shared ancestry: its separate adaptive Rust implementation is the reason for inclusion.

Excluded classes include awesome-lists, deployment-only examples, thin client bindings to retained injectors, general-purpose load generators or fuzzers without a substantive fault-injection framework, proprietary service APIs, and physical voltage/clock glitching equipment. Kernel/eBPF searches informed coverage, but this is not an exhaustive catalog of Linux kernel fault-injection facilities or hardware simulators. Small related injector components were not automatically promoted into separate entries merely because they occupy separate repositories.

This was read-only research: no candidate dependencies were installed, code executed, or repositories cloned. Branch links identify the inspected default branches and can evolve after the research date. Maintenance assessments are deliberately limited: CharybdeFS and nlfaultinjection are archived; libfiu is the author's GitHub mirror of separately hosted upstream source; older recorded activity is disclosed for PowerfulSeal, Chaos Monkey, Mallory, Filibuster, and PyTorchFI. C4 is awarded only where substantive multi-year change evidence was inspected. Performance observations describe mechanisms and tradeoffs, not independently reproduced benchmark results.
