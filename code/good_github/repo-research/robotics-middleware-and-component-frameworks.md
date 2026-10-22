# Robotics middleware and component frameworks

Research date: **2026-10-09**. This selection covers 23 GitHub repositories implementing robot communication, execution, component lifecycles, hardware abstraction, or component composition. It includes transport libraries with a clear robotics role, embedded clients, model-based integration tools, and relevant runtime subsystems inside larger repositories. It excludes ordinary robot applications, standalone drivers, algorithm libraries, tutorials, and bootstrap repositories without the implementation being evaluated.

The criteria below describe reasons to study the selected code, not a certification of production suitability or a claim that every component is exemplary. Architectural observations are grounded in linked primary material; the conclusions about study value are engineering judgments. Repository identity, archive state, and default branches were checked through GitHub pages and API-backed metadata. An unarchived repository is not automatically described as actively maintained.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions supporting many uses. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — sustained evolution with evidence of compatibility work, testing, or complexity management, rather than age alone.

## ROS execution and control infrastructure

### 1. [ros2/rclcpp](https://github.com/ros2/rclcpp)

**Language/role:** C++; ROS 2 client library, executors, composition, actions, and managed node lifecycles. Study how a general asynchronous robotics API maps ready entities to user callbacks while preserving ownership and cancellation rules.

- **C1:** The executor checks callback-group availability, marks mutually exclusive groups unavailable during execution, handles canceled timers, and distinguishes spurious middleware wakeups from successful message acquisition. The loaned-message path also exposes the take/callback/return ownership boundary. These are concrete concurrency and lifetime problems in the [executor implementation](https://github.com/ros2/rclcpp/blob/rolling/rclcpp/src/rclcpp/executor.cpp).
- **C2:** The same execution machinery serves timers, subscriptions, services, clients, and custom waitables; the repository also contains component and lifecycle packages.
- **C4:** The [package changelog](https://github.com/ros2/rclcpp/blob/rolling/rclcpp/CHANGELOG.rst) documents executor benchmarks and shutdown-ownership changes in 2020, clock and future fixes in 2022, and regression tests, executor deprecations, and callback-group race fixes in 2026.

**Entry points:** executor implementation and package changelog linked above.

### 2. [ros2/rclc](https://github.com/ros2/rclc)

**Language/role:** C; a ROS 2 client layer particularly relevant to embedded execution and micro-ROS. Unlike a generated language binding, it supplies an executor, lifecycle support, and parameter-server facilities on top of existing `rcl` types.

- **C1:** The [executor implementation](https://github.com/ros2/rclc/blob/rolling/rclc/src/rclc/executor.c) distinguishes logical-execution-time scheduling from ordinary ROS callback scheduling, validates handles, constructs wait sets, and implements configurable trigger predicates. Periodic spinning separates one iteration from the endless loop explicitly to make timing behavior testable.
- **C2:** Publishers, subscriptions, timers, services, and actions share a C execution model; lifecycle and parameter packages extend it beyond simple message wrappers.
- **C3:** Fixed handle capacity, explicit execution order/triggering, and periodic invocation make scheduling and memory decisions visible to constrained-system developers.

**Entry point:** executor source above. **Limitation:** the repository documents a single-threaded executor and explicitly does not claim general production readiness; deterministic mechanisms are not a blanket hard-real-time guarantee.

### 3. [ros-controls/ros2_control](https://github.com/ros-controls/ros2_control)

**Language/role:** C++ with Python tooling; robot hardware and controller component framework. Study the boundary between controller management services and the time-sensitive read–update–write loop.

- **C1:** Controller activation depends on available hardware interfaces; update errors can deactivate a controller chain and invoke command-mode switching. Fallback activation also depends on resource availability. The [Controller Manager documentation](https://control.ros.org/rolling/doc/ros2_control/controller_manager/doc/userdoc.html) describes these failure paths and their consequences.
- **C2:** Controller plugins, hardware components, lifecycle states, and resource management let the framework support different robot mechanisms and interchangeable controllers.
- **C3:** The same documentation explains FIFO scheduling, memory locking, CPU affinity, overrun handling, and how error recovery can introduce jitter. This makes performance constraints and architectural tradeoffs unusually explicit.

**Entry point:** Controller Manager documentation above, especially determinism and controller switching. The cited Rolling documentation describes development behavior; deployed distributions may differ.

### 4. [ros/ros_comm](https://github.com/ros/ros_comm)

**Language/role:** C++ and Python; historical ROS 1 communication libraries and graph tools. **Archived:** GitHub marks this repository read-only. It remains useful for studying the earlier ROS execution model and maintaining legacy systems.

- **C1:** The [C++ callback queue](https://github.com/ros/ros_comm/blob/noetic-devel/clients/roscpp/src/libros/callback_queue.cpp) combines queue locks, per-callback removal identifiers, thread-local execution state, and shared/exclusive locking. Removing a callback from inside an executing callback needs special lock handling; clearing a queue is distinct from having no callbacks in flight.
- **C2:** The repository supplies reusable client libraries and communication infrastructure across topics, services, callbacks, and graph inspection rather than a single robot-specific application.

**Entry point:** `clients/roscpp/src/libros/callback_queue.cpp` above. Treat this as an archived implementation study, not evidence of continuing upstream support.

## Component lifecycles, devices, and composition

### 5. [orocos-toolchain/rtt](https://github.com/orocos-toolchain/rtt)

**Language/role:** C++; Orocos Real-Time Toolkit. A useful study in separating a component's public interface from the activity that executes it.

- **C1:** [`TaskContext`](https://github.com/orocos-toolchain/rtt/blob/master/rtt/TaskContext.hpp) documents the distinction between pre-operational and stopped states, configuration before starting, and the requirement for a running activity before asynchronous invocations or state-machine execution can proceed. Peer disconnection also has to remove data-flow connections and peer relationships coherently.
- **C2:** Provided/required services, typed ports, properties, operations, execution engines, and pluggable activities form a reusable component model for machine and robot control.

**Entry point:** `rtt/TaskContext.hpp` above. **Status:** retain as a substantial older implementation; the checked GitHub metadata reported its last push in June 2022. No claim of current maintenance is made, and the old 1.x online manual should not be mistaken for the 2.x API.

### 6. [robotology/yarp](https://github.com/robotology/yarp)

**Language/role:** C++ with language bindings; robot communication and device interfaces, including humanoid and embedded use cases. Study an API that makes freshness, completeness, and buffer ownership separate choices.

- **C1:** [`BufferedPort` documentation](https://www.yarp.it/latest/classyarp_1_1os_1_1BufferedPort.html) specifies asynchronous object lifetimes, callback locking, and explicit acquire/release ownership. Acquired objects cannot be reused until released, making memory retention a visible correctness concern.
- **C2:** Typed buffered ports build on the broader port and device abstractions; communication carriers can be selected independently of payload-facing code.
- **C3:** The default policy can drop old messages to reduce latency. Strict sending waits for prior transmissions, while strict receiving retains FIFO messages and can increase latency and memory use with a slow consumer. The documentation explains the tradeoff rather than merely claiming speed.

**Entry point:** `BufferedPort` API and its linked implementation.

### 7. [OpenRTM/OpenRTM-aist](https://github.com/OpenRTM/OpenRTM-aist)

**Language/role:** C++; AIST's implementation of the OMG Robotics Technology Component model. This is the project organization's repository, which GitHub records as having fork ancestry; no second copy of that lineage is counted here.

- **C1:** The [RT Component architecture](https://www.openrtm.org/openrtm/en/doc/aboutopenrtm/rtc_architecture) separates inactive, active, and error states from execution contexts. Contexts can be attached and detached dynamically, and one context can synchronously execute several components, exposing lifecycle and scheduling coordination problems.
- **C2:** Data ports, provided/required service ports, introspection profiles, and swappable configuration sets support components ranging from sensor interfaces to higher-level behavior modules. CORBA supplies the distributed, cross-language connection model.

**Entry point:** RT Component architecture above. This entry evaluates the C++ implementation; the separate Python and Java implementations are not additional entries.

### 8. [robotraconteur/robotraconteur](https://github.com/robotraconteur/robotraconteur)

**Language/role:** C++ core with multiple language bindings; distributed robot and automation services. Study the interaction between remote objects and streaming state rather than only topic publication.

- **C1:** [`WireMember.h`](https://github.com/robotraconteur/robotraconteur/blob/master/RobotRaconteurCore/include/RobotRaconteur/WireMember.h) distinguishes sender timestamps from local receive time, supports bounded value lifespans, and specifies timeout-aware validity waits and asynchronous close. Expired values become invalid instead of silently remaining usable robot state.
- **C2:** The [service-model introduction](https://robotraconteur.github.io/robotraconteur/doc/core/latest/python/tutorial/Introduction.html) explains service definitions, runtime interface discovery, object references, properties, functions, events, pipes, wires, and memories. Dynamic clients can obtain service definitions when connecting; exclusive object locks address shared-device access.

**Entry points:** service-model introduction and wire API above.

### 9. [Servicerobotics-Ulm/AceSmartSoftFramework](https://github.com/Servicerobotics-Ulm/AceSmartSoftFramework)

**Language/role:** C++; ACE-backed implementation of the SmartSoft component-developer API. A less widely known but substantive study in standardized communication patterns and dynamic wiring.

- **C1:** [`smartQuery.hh`](https://github.com/Servicerobotics-Ulm/AceSmartSoftFramework/blob/master/AceSmartSoftKernel/smartQuery.hh) explicitly separates protection of pending queries from protection of changing connections. It documents query-versus-disconnect races, correlation identifiers, connection identifiers for stale connections, and incompatible-service outcomes.
- **C2:** Query, push, send, event, state, and wiring patterns provide recurring component interactions over an implementation-specific middleware layer. The repository connects these patterns to service-oriented robotics composition and the RobMoSys component model.

**Entry point:** query-pattern API above. **Status:** an older implementation snapshot, with the checked metadata reporting a December 2022 last push; this is not presented as a currently supported platform recommendation.

### 10. [fawkesrobotics/fawkes](https://github.com/fawkesrobotics/fawkes)

**Language/role:** C++; robot framework centered on plugins, interfaces, and a shared blackboard. Study explicit ownership of shared robot state and the distinction between interface identity and interface version.

- **C1:** The [blackboard interface manager](https://github.com/fawkesrobotics/fawkes/blob/master/src/libs/blackboard/internal/interface_manager.cpp) rejects a second writer, checks interface hashes before attaching to shared memory, maintains reference counts, and coordinates locks and notifications during creation and closure.
- **C2:** The [BlackBoard interface](https://github.com/fawkesrobotics/fawkes/blob/master/src/libs/blackboard/blackboard.h) provides typed read/write acquisition, pattern-based discovery, listeners, observers, and separate notifications for data, messages, readers, and writers. Robot components can share this mechanism without knowing each other's implementation.

**Entry points:** blackboard interface and manager above. GitHub was unarchived; the checked last-push metadata was May 2025, so no ongoing maintenance cadence is inferred.

### 11. [jhu-cisst/cisst](https://github.com/jhu-cisst/cisst)

**Language/role:** C++; computer-assisted intervention libraries. **Relevant subsystem:** `cisstMultiTask`, counted once within this broader repository, rather than its numerical or vision libraries.

- **C1:** [`mtsStateTable`](https://github.com/jhu-cisst/cisst/blob/main/cisstMultiTask/mtsStateTable.h) stores heterogeneous task state in a circular buffer and explicitly assumes one writer with multiple readers. The documented reader/write-head relationship and indexed collection batches make snapshot consistency and history retention concrete topics to study.
- **C2:** Typed state arrays, accessors, collection callbacks, and task/component integration provide reusable machinery for instrumenting and connecting robot tasks.
- **C4:** The [changelog](https://github.com/jhu-cisst/cisst/blob/main/CHANGELOG.md) records 2024–2026 platform work and API evolution, including manager consolidation, removal of obsolete implementations, refusing to remove connected interfaces, race fixes, and improved test reliability. This shows complexity management, including deliberate breaking changes.

**Entry points:** state-table header and changelog above.

### 12. [rock-core/tools-orogen](https://github.com/rock-core/tools-orogen)

**Language/role:** Ruby with generated C++ integration; Rock's component specification and code-generation engine for Orocos. The retained repository is the generator implementation, not a collection of generated wrappers.

- **C1:** The [task-context specification implementation](https://github.com/rock-core/tools-orogen/blob/master/lib/orogen/spec/task_context.rb) resolves declared port types, checks name uniqueness, handles inherited model extensions, and ensures shared-pointer types exist in the project's typekit. These checks protect the consistency of generated component interfaces.
- **C2:** Its model separates component declarations from generation and supports periodic, triggered, sequential, file-descriptor, interrupt-driven, and slave activities. Engineers can study how a robotics DSL captures repeated integration work while leaving application algorithms in ordinary libraries.

**Entry point:** `lib/orogen/spec/task_context.rb` above. Its role is distinct from RTT's runtime and Syskit's deployment management below.

### 13. [rock-core/tools-syskit](https://github.com/rock-core/tools-syskit)

**Language/role:** Ruby; Rock's model-based component management layer, integrated with the Roby plan manager. Especially valuable for engineers interested in reconciling desired component networks with already-running processes.

- **C1:** The [network-generation engine](https://github.com/rock-core/tools-syskit/blob/master/lib/syskit/network_generation/engine.rb) computes a deployment in a transaction, validates it, then merges it into the running plan. It handles reusable versus restarting deployments, configuration precedence, failed resolution, and commit/discard behavior; this is substantial graph and lifecycle correctness work.
- **C2:** Requirements, deployment models, merge solvers, data-flow policies, and staged extension hooks form a reusable orchestration system rather than a fixed robot launch script.
- **C3:** The engine computes port dynamics and connection policies, including logging-buffer decisions, and tries to reuse compatible deployed tasks. System composition therefore incorporates data-flow and restart costs.

**Entry point:** network-generation engine above.

## Communication substrates and application runtimes

### 14. [lcm-proj/lcm](https://github.com/lcm-proj/lcm)

**Language/role:** C core, generators, and multiple language bindings; Lightweight Communications and Marshalling for low-latency systems, including robotics. Study a compact brokerless transport with explicit buffering and serialization boundaries.

- **C1:** The [UDP provider](https://github.com/lcm-proj/lcm/blob/master/lcm/lcm_udpm.c) coordinates a receive thread, filled/empty packet queues, transmit serialization, initialization condition variables, shutdown notification pipes, and fragmented-message buffers.
- **C3:** Small received packets use a fixed-size ring buffer to avoid allocation on that path. Queue ownership, kernel receive buffers, and packet processing are identifiable architectural units.
- **C4:** The [release history](https://github.com/lcm-proj/lcm/blob/master/NEWS.md) spans releases from 2016 through 2026 and documents binding compatibility, build-system changes, an unsubscribe/handler race fix, and UDP overflow repair. The repository explicitly prioritizes backward-compatible evolution; Go and C# bindings are marked unmaintained in its README.

**Entry points:** UDP provider and release history above.

### 15. [eclipse-ecal/ecal](https://github.com/eclipse-ecal/ecal)

**Language/role:** C++ with C and other language interfaces; brokerless communication used in autonomous-driving and robotics integration. Study local shared-memory transport alongside network publication, recording, and replay.

- **C2:** Publish/subscribe and client/server interfaces are separated from message serialization, with support for different payload formats and tooling that observes the same communication system.
- **C3:** The [publisher-send activity diagram source](https://github.com/eclipse-ecal/ecal/blob/master/doc/arch/ecal_send_activity_hl.plantuml) shows prerequisite checks, matching-subscriber checks, conditions for activating zero-copy mode, and forwarding to shared-memory, UDP, and TCP writers. It makes transport selection and the effect of network subscribers on the local fast path directly inspectable.

**Entry point:** publisher-send architecture diagram above, read alongside the repository's transport overview. Performance relevance is grounded in transport mechanisms; no headline throughput figure is adopted as an independently verified result.

### 16. [gazebosim/gz-transport](https://github.com/gazebosim/gz-transport)

**Language/role:** C++; Gazebo's separately reusable component communication library for publication/subscription and service calls. This is the transport repository, not the simulator monorepo.

- **C1:** [`NodeShared.cc`](https://github.com/gazebosim/gz-transport/blob/gz-transport15/src/NodeShared.cc) creates a transport context per process so ZeroMQ contexts are not shared across processes. Concurrent creation uses shared lookup followed by exclusive locking and a second existence check. Discovery configuration also ensures message and service discovery ports differ.
- **C2:** Nodes, publishers, subscriptions, request/reply handlers, and discovery infrastructure supply a common communication substrate for simulation and robotics components.
- **C3:** The implementation explains its read-heavy shared-mutex choice and centralizes per-process transport resources, exposing the performance rationale in the code.

**Entry point:** `NodeShared.cc` on the verified `gz-transport15` branch. The repository's default development branch is `main`; this entry deliberately points to the inspected version branch.

### 17. [themoos/core-moos](https://github.com/themoos/core-moos)

**Language/role:** C++; MOOS communication and application infrastructure for mobile and marine robotics. Study a database-mediated notification model with explicit control over application and communication timing.

- **C2:** [`CMOOSApp`](https://github.com/themoos/core-moos/blob/master/Core/libMOOS/App/MOOSApp.cpp) standardizes startup, connection/disconnection callbacks, mail processing, iteration, notification, and mission-file configuration. Applications override hooks while reusing the communications lifecycle.
- **C3:** `SleepAsRequired` separates ordinary periodic execution, periodic iteration with communication-driven mail, and communication-driven iteration capped by a maximum rate. The implementation handles early mail wakeups without necessarily running the control iteration, making responsiveness versus work-rate control visible.
- **C1:** The run loop explicitly controls whether disconnected applications may iterate and whether failed iteration hooks cause termination; received mail can be ordered by timestamp before application processing.

**Entry point:** `Core/libMOOS/App/MOOSApp.cpp`, especially `SleepAsRequired` and `DoRunWork`. MOOS-IvP and other copies of core MOOS are not counted again.

### 18. [ApolloAuto/apollo](https://github.com/ApolloAuto/apollo)

**Language/role:** C++ with Python interfaces; **only the `cyber/` Cyber RT runtime subsystem** is selected from this autonomous-driving monorepo.

- **C1:** The [choreography scheduler](https://github.com/ApolloAuto/apollo/blob/master/cyber/scheduler/policy/scheduler_choreography.cc) uses per-coroutine-identifier locking to prevent concurrent addition/removal races, protects the routine registry, rejects duplicate routine identifiers, and bounds priorities before queue placement.
- **C2:** Cyber RT supplies reusable component/task interfaces, message channels, runtime configuration, and record/replay tools; its [subsystem overview](https://github.com/ApolloAuto/apollo/blob/master/cyber/README.md) identifies that scope independently of Apollo's driving algorithms.
- **C3:** Configured tasks can be assigned to choreography processors while other work enters a pool. CPU sets, affinity, scheduler policy, and processor priorities are explicit, inspectable controls over latency-sensitive execution.

**Entry points:** Cyber RT overview and choreography scheduler above. Apollo is counted once; no quality judgment about the rest of its autonomous-driving stack is implied.

## Alternative language ecosystems and newer runtimes

### 19. [dora-rs/dora](https://github.com/dora-rs/dora)

**Language/role:** Rust runtime with Python, C, and C++ node interfaces; distributed dataflow-oriented robotics middleware. Study the distinction between node processes, in-process operators, and orchestration.

- **C2:** The [architecture reference](https://github.com/dora-rs/dora/blob/main/guide/src/concepts/architecture.md) separates message protocols, reusable core libraries, per-machine daemons/operator runtimes, and CLI/coordinator orchestration. Typed inputs and outputs connect nodes written in different languages through Arrow data.
- **C3:** Shared-memory payload transfer, a separate operator thread connected through a bounded channel, and configurable input queues expose where copies, process isolation, and backpressure enter the system.
- **C1:** Node spawning and process monitoring, multiple asynchronous event sources, and coordinator/daemon lifecycle management make failure and ordering semantics meaningful implementation topics.

**Entry point:** architecture reference above. This is a changing architecture: the root README acknowledges partial recovery of running dataflows across coordinator restarts. Its numerical comparisons with ROS are not independently validated here.

### 20. [copper-project/copper-rs](https://github.com/copper-project/copper-rs)

**Language/role:** Rust; generated robotics execution runtime with logging and replay. Study how a static task graph and recorded workload information influence scheduling.

- **C1:** [Profile-guided scheduling](https://github.com/copper-project/copper-rs/blob/master/doc/profile-guided-scheduling.md) validates a saved execution plan against the static graph and rejects measurements from a different mission or workload signature. Comparing a prediction with an unrelated run would otherwise produce misleading scheduling decisions.
- **C2:** The [public API contract](https://github.com/copper-project/copper-rs/blob/master/doc/v1-api-surface.md) distinguishes source, processing, sink, bridge, resource, clock, and replay abstractions and labels stable, experimental, internal, and deprecated surfaces.
- **C3:** Scheduling search runs offline; declared deadlines, source periods, available CPUs, pipeline depth, and headroom constrain generated plans without adding search to the runtime hot path.

**Entry points:** scheduling design and API contract above. A compatibility policy alone does not establish years of evolution, so C4 is not claimed. The documented synthetic fixture is explicitly not representative robotics performance evidence.

### 21. [hybridgroup/gobot](https://github.com/hybridgroup/gobot)

**Language/role:** Go; framework for robotics, drones, and physical computing. The useful study target is the lifecycle and event-driven framework beneath its large driver collection.

- **C2:** [`Robot`](https://github.com/hybridgroup/gobot/blob/release/robot.go) combines connections, devices, work routines, events, and remotely exposed commands into one reusable entity. Collections of robots use the same lifecycle abstraction.
- **C1:** Startup orders connection and device initialization before launching work, stops on initialization errors, and handles asynchronous work and interrupt signaling. Shutdown attempts all device/connection cleanup and aggregates errors; the implementation also avoids sending on the completion channel when startup did not succeed, which could otherwise block.

**Entry point:** `robot.go` on the verified `release` default branch. It is a useful contrast to C++ component frameworks, but the presence of Go concurrency primitives is not treated as proof of hard-real-time behavior.

### 22. [viamrobotics/rdk](https://github.com/viamrobotics/rdk)

**Language/role:** Go; Viam's robot server and development kit. Study robot resources as a mutable dependency graph, including local/remote naming and orderly teardown.

- **C1:** The [resource graph](https://github.com/viamrobotics/rdk/blob/main/resource/resource_graph.go) rejects self-dependencies and circular dependencies, maintains a transitive-closure matrix during mutation, synchronizes graph access, and removes marked resources in topological order. It also distinguishes missing names from ambiguous remote matches.
- **C2:** Components and services share resource, API, model, registry, and dependency concepts. The graph supports adding, merging, replacing parents, and removing resources, making it relevant to many hardware configurations rather than one fixed robot topology.
- **C3:** A secondary name/API cache accelerates lookup while imposing a clear consistency obligation on the graph storage layer.

**Entry point:** `resource/resource_graph.go`; its adjacent tests are visible in the verified [resource directory](https://github.com/viamrobotics/rdk/tree/main/resource).

### 23. [intrinsic-ai/intrinsic-core](https://github.com/intrinsic-ai/intrinsic-core)

**Language/role:** Primarily C++ with additional SDK/tooling languages; industrial robotics runtime and component platform. **Relevant subsystem:** ICON's hardware abstraction and module lifecycle under `intrinsic_control/intrinsic/icon/hal`, counted once within the monorepo.

- **C1:** The [hardware-module interface](https://github.com/intrinsic-ai/intrinsic-core/blob/main/intrinsic_control/intrinsic/icon/hal/hardware_module_interface.h) specifies initialization, preparation, activation, motion enablement, and fault transitions. Failed realtime callbacks fault and disable motion. It explicitly prohibits resetting the realtime clock concurrently with blocking tick operations.
- **C2:** Separate module processes expose state and command interfaces through IPC, letting heterogeneous devices implement one lifecycle and hardware integration contract.
- **C3:** Preparation may block, whereas cyclic status reads and command application belong to the realtime phase. That phase separation makes timing obligations reviewable at the extension boundary.

**Entry point:** hardware-module contract above. This is a newly public repository in the checked metadata; C4 is deliberately not inferred from the organization's history or from the size of the codebase.

## Coverage, search method, and limitations

Discovery used live web searches with more than six distinct formulations: ROS executors and embedded C clients; Orocos/YARP/OpenRTM component architectures; SmartSoft, Rock, OPRoS, and Finroc alternatives; medical-robotics multitasking; MOOS/LCM/eCAL transports; Rust dataflow runtimes; Go robot frameworks; blackboard architectures; autonomous-driving runtime schedulers; and historical Urbi/MIRA/XBot families. Follow-up queries checked exact project identities and implementation locations. Searches eventually returned mostly already-covered frameworks, broad surveys, application-specific projects, wrappers, or projects whose substantive public core could not be verified to the same standard.

Every retained repository was opened directly or checked through GitHub's API-backed connector, and at least one additional primary architectural or implementation source was read. Source trees and individual files were inspected without cloning repositories, installing dependencies, or running their code. Only primary sources support the repository assessments; surveys and search results were discovery aids. Root URLs are unique, and monorepo selections explicitly name their subsystem.

Important exclusions and boundaries:

- Generic DDS, ZeroMQ, and other general-purpose messaging implementations were not added simply because robot frameworks depend on them. LCM, eCAL, and Gazebo Transport were retained for their direct relevance to robot/autonomy component communication.
- The [RoboComp workspace manifest](https://github.com/robocomp/robocomp/blob/development/robocomp.repos) now points to separate core, tools, interfaces, and cortex repositories. Its top-level bootstrap repository was not treated as the framework implementation, and the split repositories were not evaluated deeply enough for inclusion in this pass.
- XBot2's inspected [versioned quickstart](https://advrhumanoids.github.io/xbot2/v2.11.1/quickstart.html) explicitly describes that distribution as not open source and directs users to binary packages; public example and integration repositories were not substituted for a verified public core implementation. Finroc, MIRA, OPRoS, and several older families were discovered but not retained without equally complete verified GitHub implementation evidence. Their omission is not a judgment that their designs are weak.
- ROS 1 is explicitly archived. RTT and ACE/SmartSoft are retained as older study targets with their observed activity limitations. None of the selected entries is represented as a relocated project's unofficial mirror, and no duplicate fork lineage is counted as a separate project.
- This is a source-selection guide, not a benchmark, exhaustive code audit, maintenance guarantee, or comparative safety assessment. Links generally follow named branches and may change. No numerical performance claims were independently measured; C4 is used only where the inspected history supports sustained engineering work.
