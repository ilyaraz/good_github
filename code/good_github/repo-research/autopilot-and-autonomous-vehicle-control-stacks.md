# Autopilot and autonomous vehicle control stacks

Research date: **2026-10-09**.

This selection covers software that closes vehicle control loops or coordinates sensing, estimation, planning, and actuation: embedded aircraft autopilots, companion-computer autonomy, road and racing vehicles, and marine vehicles. It includes both complete systems and substantial control subsystems whose boundary is identified below. Driver assistance and small research vehicles are explicitly distinguished from unrestricted autonomous driving. Each of the 20 repositories has a verified canonical GitHub page and additional primary implementation or architecture evidence.

Criteria used:

- **C1 — Difficult correctness:** numerical behavior, concurrency, state transitions, invariants, or failure handling that materially affects control.
- **C2 — Reusable abstractions:** substantial interfaces or components that support multiple vehicles, algorithms, missions, or hardware platforms.
- **C3 — Performance with structure:** an understandable architecture that addresses execution deadlines, latency, memory, or computational limits.
- **C4 — Sustained evolution:** documented development over years together with testing, compatibility, release, or complexity-management practices.

The criteria are evidence-based selection judgments, not claims that every component is exemplary or that a stack is certified for any particular deployment.

## Embedded autopilots and flight-control foundations

### 1. [PX4/PX4-Autopilot](https://github.com/PX4/PX4-Autopilot)

**Language / role:** C++ and C; embedded autopilot with estimation, flight control, actuator allocation, drivers, and middleware for several vehicle configurations.

Study how the flight stack separates vehicle control from its execution and communication environment. The [architecture document](https://github.com/PX4/PX4-Autopilot/blob/main/docs/en/concept/architecture.md) follows the estimator/controller/actuator path and explains uORB and scheduling rather than merely listing supported aircraft.

- **C1:** Asynchronous, thread-safe uORB communication and controller-to-actuator transformations expose synchronization and numerical constraints at the boundaries between independently executing modules.
- **C2:** Flight-stack modules sit above reusable drivers, communication, and operating-system facilities; vehicle-specific control and actuator mappings share that infrastructure.
- **C3:** Work queues share thread stacks and priorities to reduce memory and context-switch costs. Their explicit prohibition on blocking operations is a useful scheduling contract to compare with more expensive independent tasks. These distinctions are documented in the linked architecture source.

### 2. [ArduPilot/ardupilot](https://github.com/ArduPilot/ardupilot)

**Language / role:** Primarily C++, with C and Python tooling; aircraft, rover, boat, and submarine autopilots sharing a large common library layer.

Study how hardware abstraction and scheduling support a family of vehicle applications. The [threading guide](https://ardupilot.org/dev/docs/learning-ardupilot-threading.html) describes AP_HAL callbacks, platform-specific threads, scheduler work, and synchronization. Some platform examples are historical, so they should be read as architectural explanations rather than a current hardware support matrix.

- **C1:** Timer callbacks, semaphores, and separation of slow storage work from time-sensitive execution make concurrency and blocking behavior explicit correctness concerns.
- **C2:** The HAL and common facilities are reused by distinct vehicle applications rather than requiring a separate firmware architecture for each vehicle.
- **C4:** The repository documents development since 2010; the [release procedure](https://ardupilot.org/dev/docs/release-procedures.html) adds concrete evidence of complexity management: per-commit AutoTester runs, protected release branches, tracked backports, vehicle-specific release notes, and beta issue tracking.

### 3. [paparazzi/paparazzi](https://github.com/paparazzi/paparazzi)

**Language / role:** C flight software with supporting ground and configuration tools; a configurable unmanned-aircraft system covering fixed-wing, rotorcraft, and other vehicle forms.

Study configuration-driven firmware construction. The [firmware architecture guide](https://wiki.paparazziuav.org/wiki/FirmwareArchitecture) distinguishes MCU interfaces, external-device drivers, architecture-specific code, board definitions, and XML-selected modules.

- **C1:** The guide explicitly distinguishes directly ordered estimation/control calls from generated periodic and event callbacks. It explains why call ordering matters and where architecture-specific interrupt, reset, and sensor-scaling behavior enters the abstraction. This is a concrete case of configuration affecting control-loop correctness.
- **C2:** XML module descriptions generate initialization and execution hooks, supporting mission payloads, sensors, guidance, and core functionality through a common composition mechanism. Configuration indirection also allows internal file moves without rewriting every airframe definition.

The guide identifies legacy subsystem terminology and the transition toward modules; an engineer should trace the selected airframe's actual generated configuration rather than assume all historical descriptions apply uniformly.

### 4. [iNavFlight/inav](https://github.com/iNavFlight/inav)

**Language / role:** C; navigation-enabled flight firmware, particularly useful for comparing fixed-wing and multirotor mission control within an embedded system.

Study the interaction of pilot input, navigation modes, sensor validity, and vehicle-specific control laws. The [navigation guide](https://inavflight.github.io/docs/next/core-features/flight-modes-navigation/) explains mode composition, coordinated turns, pitch/throttle coupling, and different meanings of position hold for hovering aircraft and fixed wings.

- **C1:** Navigation arming checks consider GNSS precision as well as satellite count. The [failsafe documentation](https://inavflight.github.io/docs/inav-configurator/failsafe-tab/) describes receiver-loss transitions, recovery of pilot authority, and emergency landing when GNSS is lost during failsafe return-to-home. Their interaction makes failure semantics a substantial study topic.
- **C2:** Common mission and navigation modes select the required lower-level control functions while exposing vehicle-specific constraints and tuning. The same navigation interface therefore covers materially different aircraft dynamics.

The cited navigation page is the development documentation; the failsafe page identifies its released documentation version. Parameter behavior should be checked against the firmware revision being studied.

### 5. [bitcraze/crazyflie-firmware](https://github.com/bitcraze/crazyflie-firmware)

**Language / role:** C; embedded control firmware for Crazyflie-family small aircraft and related positioning hardware.

Study how a constrained onboard controller combines streamed commands with autonomous trajectories. The [commander and setpoint design](https://www.bitcraze.io/documentation/repository/crazyflie-firmware/master/functional-areas/sensor-to-control/commanders_setpoints/) is a particularly clear entry point into control authority and trajectory execution.

- **C1:** A stale low-level setpoint triggers staged watchdog behavior, and low-level commands take priority over the high-level commander. Explicitly relaxing that priority is necessary to return authority to high-level operation; this makes command handoff a real state-management problem.
- **C2:** Setpoints encode position, velocity, attitude, and disabled axes through a shared contract. A high-level planner produces seventh-order polynomial trajectories while presenting the same downstream control interface.

The [unit-testing guide](https://www.bitcraze.io/documentation/repository/crazyflie-firmware/master/development/unit_testing/) provides a second entry point into configuration-dependent tests, mocking, and sanitizer-enabled host tooling. This selection does not treat small aircraft size as evidence of simple software.

### 6. [rosflight/rosflight_firmware](https://github.com/rosflight/rosflight_firmware)

**Language / role:** C++; flight-controller firmware intended to work with companion-computer autonomy. This is the low-level control and safety foundation, not a complete onboard mission planner.

Study the deliberately narrow boundary between embedded control and higher-level robotics. The [code architecture guide](https://docs.rosflight.org/git-main/developer-guide/firmware/code-architecture/) walks through Board, CommLink, state management, command arbitration, controllers, and mixing.

- **C1:** StateManager tracks armed, error, and failsafe states; CommandManager combines RC and companion commands subject to those states. Hard-fault recovery also interacts with saved armed status, illustrating that reboot behavior is part of the control design.
- **C2:** Board and CommLink abstractions are supplied to the flight core, allowing the same control organization to operate with different hardware and software-in-the-loop backends. Controllers output forces and torques separately from actuator mixing.

The unusually explicit architecture documentation makes this a useful smaller comparison against PX4 and ArduPilot without mistaking its narrower scope for a full autonomy stack.

## Companion-computer aerial autonomy

### 7. [aerostack2/aerostack2](https://github.com/aerostack2/aerostack2)

**Language / role:** C++ and Python; ROS 2 architecture for autonomous aerial robots and multi-aircraft applications.

Study how platform interfaces, estimation/control, behaviors, and mission execution compose. The [architecture guide](https://aerostack2.github.io/_01_aerostack2_concepts/architecture/index.html) explains the layers and concurrent processes. The [Follow Reference behavior](https://aerostack2.github.io/_04_robot_behaviors/follow_reference/index.html) supplies a concrete implementation-level example.

- **C1:** That behavior validates flying state and localization, resolves coordinate frames, rejects unsupported goals, and defines pause/cancel behavior. Moving target frames and yaw policies expose subtleties that a simple position-command API can conceal.
- **C2:** A common behavior server owns action lifecycle and validation while interchangeable plugins generate position references or delegate to polynomial trajectories. Platform abstraction and mission interfaces reuse those behaviors across aircraft backends.

This is valuable for studying autonomy above a flight controller: the behavior/action contract and platform integration are the relevant subsystems, rather than an alternative embedded motor-control implementation.

### 8. [ctu-mrs/mrs_uav_managers](https://github.com/ctu-mrs/mrs_uav_managers)

**Language / role:** C++; substantive control, estimation, and safety managers within the MRS UAV ecosystem. The managers repository is selected instead of counting its umbrella repositories separately.

Study controller replacement and safety intervention around a running vehicle. The [controller plugin interface](https://ctu-mrs.github.io/docs/plugin-interface/controllers/) defines inputs, hardware-dependent output modalities, and controller-specific error thresholds.

- **C1:** Position error and odometry-innovation thresholds feed emergency behavior. The [obstacle-bumper design](https://ctu-mrs.github.io/docs/features/obstacle-bumper/) explains how the control manager combines a static safety margin with stopping distance derived from vehicle dynamics, then takes control to escape an unsafe region.
- **C2:** Dynamically loaded controller plugins can be switched during flight and independently implement actuator, attitude, acceleration, velocity, or position outputs supported by the hardware interface. This is a substantial contract between control algorithms and platform capabilities.

The inspected documentation warns that its upcoming ROS 2 material may be outdated. Treat those pages as design evidence and verify the chosen repository branch/API before porting a controller.

### 9. [KumarRobotics/kr_autonomous_flight](https://github.com/KumarRobotics/kr_autonomous_flight)

**Language / role:** C++ and Python with ROS; integrated quadrotor autonomy for GPS-denied environments.

Study the connection from mapping and local planning to trajectory execution. The [autonomy core tree](https://github.com/KumarRobotics/kr_autonomous_flight/tree/master/autonomy_core) separates estimation, control, interfaces, map/planning, and state-machine components. The [local planning server implementation](https://raw.githubusercontent.com/KumarRobotics/kr_autonomous_flight/master/autonomy_core/map_plan/action_planner/src/local_plan_server.cpp) exposes the actual planning and handoff logic.

- **C1:** The planner handles missing maps and goals, locks shared map/trajectory state, checks candidate trajectories, and uses the previous planned trajectory to obtain a continuous replanning start state. Failed planning produces explicit action failure.
- **C3:** Planning bounds include a horizon, motion limits, and a maximum expansion count; motion primitives and voxel collision checks make the computational tradeoffs inspectable alongside their control consequences.

The repository describes an experimental ROS 2 branch with incomplete external dependency migration. The selected source is the established ROS 1 layout; the existence of the newer branch is not evidence that it reproduces the reported flight system.

## Road vehicles, driver assistance, and autonomous racing

### 10. [ApolloAuto/apollo](https://github.com/ApolloAuto/apollo)

**Language / role:** Primarily C++, with Python and other tooling; a large autonomous-driving monorepo. Counted once, with emphasis on the control subsystem and its Cyber middleware boundary.

Study how a vehicle controller consumes asynchronous localization, chassis, and planning data. Start with the [control tree](https://github.com/ApolloAuto/apollo/tree/master/modules/control) and the [ControlComponent implementation](https://github.com/ApolloAuto/apollo/blob/master/modules/control/control_component/control_component.cc).

- **C1:** Input and timestamp validation, locked copies of incoming data, engagement advice, and emergency-stop decisions interact in the command path. Empty trajectories and inconsistent motion/gear situations are explicitly handled rather than being left entirely to controller mathematics.
- **C2:** A configurable control-task pipeline and dependency-injection facilities separate controller execution from message transport and shared context. The component can organize control tasks or work with configured submodules, making architectural variation visible within one system.

This entry is about inspecting concrete control integration inside the larger monorepo; inclusion does not establish the quality or deployment readiness of every Apollo subsystem.

### 11. [autowarefoundation/autoware_universe](https://github.com/autowarefoundation/autoware_universe)

**Language / role:** Primarily C++; ROS 2 autonomous-driving components. The whole repository counts once, with the lateral trajectory controller as the detailed entry point.

Study numerical-model choices at a production-shaped ROS boundary. The [MPC lateral controller documentation](https://autowarefoundation.github.io/autoware_universe/main/control/autoware_mpc_lateral_controller/) describes the optimization formulation, vehicle models, solver options, filtering, delay compensation, and controller interfaces.

- **C1:** Steering dynamics, input delay, filtered error signals, and steering-rate constraints affect the generated commands. The treatment of reference trajectories and synchronization with longitudinal control makes numerical correctness broader than simply solving a quadratic program.
- **C2:** The MPC implementation separates vehicle models, quadratic-program solvers, reference trajectories, and the surrounding trajectory-follower interface. Engineers can compare bicycle models with and without steering delay and replace solver/model components through explicit interfaces.

The document is particularly useful for connecting mathematical design choices to code organization. It supports a claim of meaningful numerical and abstraction complexity, without requiring unverified claims about road-driving performance.

### 12. [commaai/openpilot](https://github.com/commaai/openpilot)

**Language / role:** Python and C++ with embedded integrations; Level 2 driver assistance requiring driver supervision, included for its vehicle-control architecture.

Study controller selection and disengagement behavior in a system spanning perception, vehicle interfaces, and actuation. The [controlsd implementation](https://raw.githubusercontent.com/commaai/openpilot/master/openpilot/selfdrive/controls/controlsd.py) selects angle, curvature, PID, or torque lateral controllers and a separate longitudinal controller.

- **C1:** Control activation, resets, fault conditions, vehicle-model parameter bounds, and curvature limiting interact in the command path. The [safety document](https://github.com/commaai/openpilot/blob/master/docs/SAFETY.md) states driver-override and actuation constraints and describes simulation, hardware, and vehicle testing.
- **C2:** Common vehicle state/control messages and controller interfaces support multiple actuator behaviors and vehicle configurations. The code makes the boundary to the separate `opendbc` project explicit; its external vehicle-interface and safety implementation should not be mistaken for code wholly contained in this repository.

The useful study target is supervised assistance and its control integration, not a claim of driverless capability.

### 13. [autorope/donkeycar](https://github.com/autorope/donkeycar)

**Language / role:** Python; a reusable small-scale autonomous-car framework supporting learned and other driving pipelines.

Study a compact control runtime whose architecture is easy to trace. The [parts guide](https://docs.donkeycar.com/parts/about/) explains how a Vehicle executes ordered parts, passes named values through shared memory, applies run conditions, and shuts components down.

- **C2:** The same part contract accommodates cameras, actuators, pilot models, recording, and other processing stages. Named inputs and outputs allow pipelines to be assembled without each component knowing all the others.
- **C3:** A part can update in a separate thread while the vehicle loop consumes its latest result through `run_threaded`. This separates blocking device acquisition from the configured driving-loop cadence and exposes the cost of ordering and scheduling decisions.

Its educational setting does not make it a one-off tutorial: the reusable runtime is the reason for selection. Python threading and a configured loop frequency should not be interpreted as a hard real-time guarantee.

### 14. [duckietown/dt-core](https://github.com/duckietown/dt-core)

**Language / role:** Primarily Python with ROS; the core autonomy stack for small Duckietown vehicles.

Study how perception, state estimation, mode selection, and control connect in a bounded road environment. The [packages tree](https://github.com/duckietown/dt-core/tree/ente/packages) includes lane filtering/control, line detection, ground projection, stop-line processing, and finite-state-machine components. The [lane controller node](https://raw.githubusercontent.com/duckietown/dt-core/ente/packages/lane_control/src/lane_controller_node.py) is a concrete integration point.

- **C1:** The controller selects pose information according to driving mode, incorporates stop and obstacle information, bounds lateral error, and uses elapsed time and executed wheel-command feedback. Correctness therefore depends on consistent state and message semantics, not just the nominal lane-following formula.
- **C2:** The controller algorithm and ROS node are separated, while the package/message structure connects reusable perception and control stages. That decomposition supports experiments that replace individual stages of the running vehicle stack.

This is a teaching and research environment with constrained vehicles and roads; it is not evidence of general-road autonomous-driving capability.

### 15. [erdos-project/pylot](https://github.com/erdos-project/pylot)

**Language / role:** Python on ERDOS; an autonomous-driving research platform integrating perception, prediction, planning, and control with simulation and vehicle interfaces.

Study dataflow timing rather than treating a driving stack as an ordinary sequential pipeline. The [PID control operator](https://raw.githubusercontent.com/erdos-project/pylot/master/pylot/control/pid_control_operator.py) is a short but substantive entry into the system's stream contract.

- **C1:** Control waits for watermarks on pose and waypoint streams at a common timestamp before producing a command. It maintains input queues, distinguishes simulator and real-world timing behavior, and emits a braking command when usable waypoints are exhausted.
- **C2:** Operators communicate through typed streams and callbacks, allowing control and upstream algorithms to be replaced within the larger dataflow graph. This is a reusable execution model for evaluating combinations of driving components.

Treat this as a research reference: the documented setup references an older CARLA generation, and current dependency compatibility and maintenance were not established by this research. The repository was not assumed archived merely because its examples are older.

### 16. [ForzaETH/race_stack](https://github.com/ForzaETH/race_stack)

**Language / role:** Python and C++ with ROS; integrated autonomy for small autonomous racing cars.

Study the coupling between vehicle limits, trajectory tracking, and execution delay. The [controller package](https://github.com/ForzaETH/race_stack/tree/ros2-humble/controller) documents a controller manager, MAP tracking, pure pursuit, follow-the-gap behavior, and opponent trailing.

- **C1:** Tracking adjusts speed for lateral error and path curvature, compensates actuation/computation delay, and scales steering in response to tire-slip concerns. Opponent following adds another interaction between geometry, state, and command limits.
- **C2:** The manager presents common inputs and outputs for distinct controller strategies, separating controller choice from the surrounding perception and planning stack.
- **C3:** A configured execution loop and explicit delay-compensation parameters connect runtime latency to control design, rather than treating computation time as irrelevant to trajectory tracking.

The repository warns that the ROS 2 Humble port is less tested and lacks some ROS 1 features. Published ROS 1 results should not be transferred to that branch without separate validation.

## Marine autonomy and vessel control

### 17. [LSTS/dune](https://github.com/LSTS/dune)

**Language / role:** C++; DUNE, an onboard navigation and control environment used across underwater, surface, and other robotic vehicles.

Study how drivers, navigation, control, and supervision share one runtime. The [Task base-class implementation](https://raw.githubusercontent.com/LSTS/dune/master/src/DUNE/Tasks/Task.hpp) defines typed IMC message binding, parameter declarations, entity state, activation/deactivation, resource hooks, and timed message consumption.

- **C1:** Tasks distinguish requested activation from successful activation and explicit failure. Resource release must tolerate partial initialization; timed waits also consider shutdown. These contracts expose recovery and lifecycle correctness beyond the nominal navigation loop.
- **C2:** The same task/entity/message abstraction supports sensor drivers and control functions, with reusable parameter handling and lifecycle callbacks instead of bespoke orchestration for each device.

The [release history](https://github.com/LSTS/dune/releases) provides useful follow-up examples: path-reference timeouts, activation-state fixes, driver robustness changes, and removal of obsolete tasks. Those changes show where the abstract runtime encounters practical vehicle failure modes; no uniform current-support claim is made for every listed driver.

### 18. [moos-ivp/moos-ivp](https://github.com/moos-ivp/moos-ivp)

**Language / role:** C++; marine autonomy middleware and the IvP behavior-based helm. Its autonomy layer typically operates above a vehicle-specific low-level controller.

Study how independent mission behaviors contribute to one chosen vehicle action. The [helm design documentation](https://oceanai.mit.edu/ivpman/pmwiki/pmwiki.php?n=Helm.HelmDesignIntro) explains the backseat/frontseat division, MOOS process communication, behavior lifecycle, and IvP optimization.

- **C1:** Active behaviors express potentially competing preferences over heading, speed, or depth. A multiobjective decision process must turn them into one command, with behavior activation and priority affecting the result. Numerical representation and arbitration are central correctness concerns.
- **C2:** Behaviors extend a common base and communicate through a shared autonomy environment, permitting new mission logic without replacing vehicle drivers or the entire helm.
- **C3:** Piecewise-linear objective functions provide a structured representation for repeated multiobjective optimization during operation. The documentation explains the computational organization; this selection makes no unsupported throughput claim.

Count the integrated repository once rather than separately listing its middleware and individual example behaviors.

### 19. [pypilot/pypilot](https://github.com/pypilot/pypilot)

**Language / role:** Primarily Python with native and servo-support components; a sailboat autopilot integrating heading, navigation, and wind-oriented steering modes.

Study real control subtleties in a comparatively approachable codebase. The [autopilot implementation](https://raw.githubusercontent.com/pypilot/pypilot/master/pypilot/autopilot.py) connects sensors, selectable pilots, mode properties, servo commands, and timed processing.

- **C1:** Heading wraparound, wind-direction conventions, bounded control error, and integrator resets matter across mode changes. The code adjusts a commanded heading when compass calibration changes so that recalibration does not inadvertently request a different physical course.
- **C2:** Pilot implementations are loaded behind a shared autopilot interface. Sensor availability constrains the usable steering modes, and the property/client-server machinery connects control to external instruments and user interfaces.

This is a useful counterpoint to aerial and automotive stacks: wind-relative objectives and intermittent instrument availability create different control semantics. Its modularity should be studied together with those marine assumptions rather than as a universal controller ready for arbitrary vehicles.

### 20. [vortexntnu/vortex-auv](https://github.com/vortexntnu/vortex-auv)

**Language / role:** Python and C++ with ROS 2; guidance, navigation, and control software for competition AUVs and ROVs.

Study marine dynamics and the boundary between controller mathematics and ROS integration. The [control tree](https://github.com/vortexntnu/vortex-auv/tree/main/control) contains several controller families; the [velocity LQR library](https://github.com/vortexntnu/vortex-auv/blob/main/control/velocity_controller_lqr/velocity_controller_lqr/velocity_controller_lqr_lib.py) exposes parameters, state models, matrix construction, and command limiting.

- **C1:** The LQR path constructs state-dependent dynamics, augments the model for integral action, solves for feedback gains, and saturates the resulting inputs. Windup flags suppress further integral accumulation, connecting actuator limits to numerical state evolution.
- **C2:** A controller library with explicit parameters and state inputs is separated from its surrounding ROS package. The repository also offers distinct control approaches, making controller integration and replacement practical study targets.

The implementation retains vehicle-specific assumptions and coefficients, and the repository identifies unfinished documentation. Reusing its abstractions still requires checking the dynamics model and tuning for the actual vehicle.

## Search coverage and limitations

Discovery used live web searches across more than six distinct angles: embedded aircraft autopilots and firmware scheduling; fixed-wing navigation and failsafes; ROS/ROS 2 companion autonomy and controller plugins; full-size autonomous-driving control architectures; Python dataflow and small research cars; F1TENTH-style racing and delay compensation; AUV/ASV and sailboat control; and Rust/alternative embedded implementations. Follow-up queries targeted source files, architectural guides, safety state machines, testing, and release procedures. Later searches increasingly returned the same established families, isolated algorithms, wrappers, or projects whose substantive source could not be verified.

Canonical GitHub repository pages were opened for every retained entry. Each was also checked against an additional primary source containing architecture, implementation, or behavioral detail; a second copy of its top-level README was not treated as independent evidence. Linked source branches and development documentation may change. The criterion assignments are engineering inferences from the cited mechanisms, not independent measurements of reliability or performance.

Ground-control applications, communication-only libraries, simulator-only projects, awesome lists, and tutorial-only repositories were excluded. PX4, Apollo, Autoware Universe, and other monorepos are each counted once; component trees identify the relevant study target. Related umbrella repositories and ordinary forks were not counted as additional systems. [Agilicious](https://github.com/uzh-rpg/agilicious) was investigated but its public GitHub material did not expose the substantive implementation needed for this selection. COLA2 discovery led to hosting outside GitHub without a verified substantive official GitHub mirror. [LibrePilot's official mirror](https://github.com/librepilot/LibrePilot) was considered, but accessible implementation/documentation evidence was insufficient for inclusion in this pass. The Rust search did not yield an additional sufficiently verified stack; C/C++ and Python consequently dominate the selection.

This was read-only source and documentation research: no candidate was cloned, built, installed, or run. Research-oriented entries and incomplete ROS migrations are marked where observed; recent page availability alone was not treated as proof of active maintenance. The selection is broad across vehicle types and architecture styles, but it is not an exhaustive inventory or a deployment qualification assessment.
