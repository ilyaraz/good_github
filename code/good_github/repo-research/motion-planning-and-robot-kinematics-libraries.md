# Motion planning and robot kinematics libraries

Research date: **2026-10-09**

This report selects **26 distinct GitHub repositories** implementing reusable robot motion planning, trajectory generation, and forward/inverse kinematics. Coverage includes geometric and constrained planning, trajectory optimization, analytical and numerical inverse kinematics, differentiable computation, and CPU/GPU acceleration. Larger robotics frameworks are included for their named planning or kinematics subsystems; general simulation, perception, collision detection alone, and hardware drivers are outside scope. The criteria assessments are engineering judgments grounded in the linked primary material, not certifications of correctness or claims that every component is exemplary.

**Criteria legend:** **C1** — difficult correctness involving invariants, numerical semantics, concurrency, or failure modes. **C2** — substantial reusable abstractions supporting multiple applications. **C3** — concrete performance constraints addressed through understandable architecture. **C4** — documented evolution across years together with compatibility, testing, or complexity management. Every entry supports at least two criteria. Links within the criteria are suggested source or documentation entry points; each repository heading links to its verified GitHub page.

## Planning foundations and integrated frameworks

### 1. [ompl/ompl](https://github.com/ompl/ompl)

**Language / role:** C++, with Python bindings; sampling-based geometric and control-space planning.

Study how a large planner family shares state-space operations without embedding one robot model into every algorithm. The particularly instructive boundary is between generic planners and constrained state spaces.

- **C1:** Constraint-preserving interpolation can fail near singularities or high manifold curvature. The documentation explains discrete geodesics, differentiability requirements, memory-contiguity assumptions, and the consequences of an interpolation API that normally assumes success. These are concrete numerical and interface-contract hazards. [Constrained planning](https://ompl.kavrakilab.org/core/constrainedPlanning.html)
- **C2:** `StateSpace`, `ControlSpace`, `StateValidityChecker`, `SpaceInformation`, and `Planner` separate problem representation from search. The ownership and thread-safety contracts make the abstraction boundaries explicit. [API overview](https://ompl.kavrakilab.org/core/api_overview.html)

**Version note:** The repository now advertises VAMP integration, while the inspected core documentation still identifies the 1.7-era interface. Treat the conceptual contracts as the entry point and check the chosen revision for newer APIs.

### 2. [moveit/moveit2](https://github.com/moveit/moveit2)

**Language / role:** Primarily C++, with Python interfaces; ROS 2 manipulation framework. Relevant subsystems are `moveit_core`, `moveit_kinematics`, and `moveit_planners`; the monorepo is counted once.

Study the integration work required to turn an abstract path planner into a robot-facing planning pipeline.

- **C1:** Planning requests must reconcile joint bounds, self-collision, attached objects, constraint frames, and trajectory timing. The adapter documentation describes bounded repair of slightly invalid start states and explicitly distinguishes a geometric path from a velocity/acceleration-constrained trajectory. [Motion-planning concepts](https://moveit.picknik.ai/main/doc/concepts/motion_planning.html)
- **C2:** Planner plugins and request/response adapters allow OMPL, CHOMP, and industrial planners to participate in the same request-processing architecture. Preprocessing, planning, and time parameterization remain separate extension points. The same [pipeline guide](https://moveit.picknik.ai/main/doc/concepts/motion_planning.html) explains their responsibilities.

### 3. [tesseract-robotics/tesseract](https://github.com/tesseract-robotics/tesseract)

**Language / role:** C++, with Python support; ROS-independent planning environment and kinematics infrastructure for industrial automation.

Study mutable robot environments that can be replicated for independent planning jobs.

- **C1:** The environment enforces a connected scene graph, defines subtree-removal behavior, and records mutations in an ordered command history for replay and serialization. This makes model validity and reproducible environment changes explicit concerns. [Environment design](https://raw.githubusercontent.com/tesseract-robotics/tesseract/master/docs/page_environment.dox)
- **C2:** Runtime kinematics plugins have per-group configuration, multiple solver choices, and compositions for robots on tracks or external positioners. These abstractions support analytical and numerical solvers within the same model. [Kinematics design and configuration](https://raw.githubusercontent.com/tesseract-robotics/tesseract/master/docs/page_kinematics.dox)
- **C3:** Deep-cloned environments provide each planner/thread with mutable local computation state, reducing shared-state contention. The environment document explains the tradeoff directly.

### 4. [humanoid-path-planner/hpp-core](https://github.com/humanoid-path-planner/hpp-core)

**Language / role:** C++; core constrained path-planning algorithms in the Humanoid Path Planner ecosystem.

Study how path validation, steering, roadmaps, and problem construction cooperate for articulated robots with nonlinear constraints. The relevant scope is `hpp-core`; adjacent HPP packages are not counted as separate entries here.

- **C1:** `PathValidation` returns the largest valid portion of a path and a failure report, supports checking in reverse, and also validates individual configurations. That contract supports useful partial progress when a candidate edge is invalid. [Path-validation interface](https://raw.githubusercontent.com/humanoid-path-planner/hpp-core/devel/include/hpp/core/path-validation.hh)
- **C2:** `Problem`, `PathPlanner`, `Roadmap`, `SteeringMethod`, and `ProblemSolver` separate reusable planning responsibilities. The wider architecture places nonlinear constraints and robot kinematics in distinct layers below the planning core. [HPP architecture](https://humanoid-path-planner.github.io/hpp-doc/)

### 5. [sbpl/sbpl](https://github.com/sbpl/sbpl)

**Language / role:** C++; search-based planning over discrete robot state spaces, including navigation lattices and robot-arm examples.

This is a classic implementation study for engineers interested in heuristic search and incremental solution improvement. Its documentation contains legacy ROS references; this report does not infer current maintenance from repository age.

- **C1:** The ARA* implementation manages state-ID mappings, heap membership, closed-iteration markers, predecessor/successor relaxations, and an inconsistent-state list. Their consistency is central to reusing search work correctly. [ARA* implementation](https://raw.githubusercontent.com/sbpl/sbpl/master/src/planners/araplanner.cpp)
- **C2:** Search delegates successor/predecessor generation and heuristic evaluation to `DiscreteSpaceInformation`. The [source organization](https://github.com/sbpl/sbpl/tree/master/src) separates environment representations, heuristics, planners, and supporting data structures, allowing the same search machinery to serve different robot models.

### 6. [krishauser/Klampt](https://github.com/krishauser/Klampt)

**Language / role:** C++ and Python; locomotion and manipulation planning toolkit.

Study the relationship between robot-level planning and lower-level configuration-space planning, particularly for contact and closed-chain problems.

- **C1:** Contact and stance spaces add inverse-kinematics and balance constraints to collision avoidance. The planning manual also covers closed-chain interpolation and time optimization under velocity, acceleration, torque, and friction constraints. [Planning manual](https://github.com/krishauser/Klampt/blob/master/Cpp/docs/Manual-Planning.md)
- **C2:** The two planning interfaces let users either obtain robot-aware sampling and collision checks or supply their own feasibility tests and samplers. `WorldPlannerSettings`, robot configuration spaces, and planner factories make those levels accessible without forcing one application structure. The same manual is a substantive architectural entry point.

The repository’s version history documents compatibility decisions, including retaining `MotionPlan` as an alias while introducing `KinematicPlanner`; this is useful context when reading older examples.

### 7. [roboticslibrary/rl](https://github.com/roboticslibrary/rl)

**Language / role:** C++; integrated kinematics, dynamics, scene abstraction, and motion-planning library.

Study an object-oriented decomposition in which robot mathematics and geometry feed independently configurable planning components.

- **C1:** The API makes operational frames, joint state, Jacobians, pose interpolation, and recursive edge validation visible. Correctness depends on consistent frame conventions and on checking the motion between configurations, rather than merely checking endpoint poses. [Component architecture and examples](https://www.roboticslibrary.org/api)
- **C2:** `rl::mdl`, `rl::sg`, and `rl::plan` separate articulated models, geometric scenes, and planning. The PRM example independently supplies a model, sampler, edge verifier, and nearest-neighbor structure; scene capabilities distinguish collision-only and distance-query backends. The same API guide shows the composition in code.

**Compatibility note:** That guide distinguishes older scene-loading calls from the newer `XmlFactory` interface and marks `rl::kin` as deprecated in favor of `rl::mdl`.

### 8. [haosulab/MPlib](https://github.com/haosulab/MPlib)

**Language / role:** C++ and Python; robot-manipulation motion planning without a ROS dependency.

Study the substantive integration layer around robot models, collision worlds, OMPL planning, and trajectory timing. Its value includes the representation conversions needed to make those libraries cooperate.

- **C1:** The planner distinguishes full robot configurations from move-group configurations, maps joint names and indices, validates dimensions, and wraps revolute angles into permitted intervals with explicit numerical tolerances. Those details prevent plausible-looking vectors from representing the wrong robot state. [Planner implementation](https://raw.githubusercontent.com/haosulab/MPlib/main/mplib/planner.py)
- **C2:** `Planner` composes `ArticulatedModel`, `PlanningWorld`, an allowed-collision matrix, and `OMPLPlanner`, with configurable joint limits and scene objects. The same implementation exposes the reusable orchestration and the boundary between Python policy and compiled modeling/planning components.

## Optimization and trajectory generation

### 9. [RobotLocomotion/drake](https://github.com/RobotLocomotion/drake)

**Language / role:** C++ and Python; broad robotics monorepo, included for `planning/trajectory_optimization` and associated multibody constraints.

Study how trajectory representations become mathematical programs while preserving the difference between path shape and timing.

- **C1:** `KinematicTrajectoryOptimization` represents a normalized B-spline path plus a separate duration. Its documentation explicitly distinguishes generalized-position derivatives `q̇` from multibody velocities `v`, and distinguishes linear velocity bounds from nonlinear acceleration/jerk bounds. [Kinematic trajectory optimization](https://drake.mit.edu/doxygen_cxx/classdrake_1_1planning_1_1trajectory__optimization_1_1_kinematic_trajectory_optimization.html)
- **C2:** The trajectory subsystem offers kinematic optimization, direct collocation, direct transcription, and a shared multiple-shooting abstraction. These connect reusable costs and constraints to solver-backed programs. [Trajectory algorithms](https://drake.mit.edu/doxygen_cxx/group__planning__trajectory.html)

Only the relevant planning subsystem is assessed here; the monorepo counts once.

### 10. [tesseract-robotics/trajopt](https://github.com/tesseract-robotics/trajopt)

**Language / role:** C++; trajectory optimization using sequential convex optimization and quadratic-programming backends.

Study the mechanics of a practical trust-region optimizer, including the distinction between optimizing a local approximation and satisfying the original constraints.

- **C1:** The optimizer reports convergence, time/iteration limits, and failure separately. It clamps a drifted or invalid warm start before constructing trust-box bounds, and tracks actual constraint violations separately from convexified constraints. [Optimizer implementation](https://raw.githubusercontent.com/tesseract-robotics/trajopt/master/trajopt_sco/src/optimizers.cpp)
- **C2:** Costs, constraints, convex models, callbacks, and solver selection are explicit boundaries. The repository supports several QP backends; the implementation separates evaluation, convexification, and model evaluation.
- **C3:** A separate multithreaded optimizer evaluates costs and constraints through OpenMP loops. The same source exposes the parallelization boundary instead of hiding it inside an opaque solver.

### 11. [borglab/gpmp2](https://github.com/borglab/gpmp2)

**Language / role:** C++, with Python and MATLAB interfaces; Gaussian-process motion planning through factor-graph optimization.

Counted once via the Borg Lab continuation: the [original project explicitly directs users here](https://github.com/gtrll/gpmp2). Its GTSAM integration and Python 3 packaging distinguish this continuation from the original Python 2 setup.

- **C1:** Graph construction combines start/end pose and velocity priors, optional position/velocity limit factors, obstacle factors, and Gaussian-process-interpolated obstacle factors between support states. This exposes the numerical distinction between trajectory support points and intermediate collision evaluation. [Graph-building implementation](https://raw.githubusercontent.com/borglab/gpmp2/master/gpmp2/planner/BatchTrajOptimizer-inl.h)
- **C2:** The generic optimizer is parameterized by robot, signed-distance field, GP prior, and obstacle-factor types; public entry points cover arms and mobile manipulators. [Batch optimizer interface](https://raw.githubusercontent.com/borglab/gpmp2/master/gpmp2/planner/BatchTrajOptimizer.h)

Collision and limit factors are optimization terms; their presence should not be read as a universal feasibility guarantee.

### 12. [loco-3d/crocoddyl](https://github.com/loco-3d/crocoddyl)

**Language / role:** C++ and Python; optimal robot trajectories and feedback policies, including multi-contact motion.

Study an optimal-control architecture whose abstractions are written around manifold states and differentiable action models.

- **C1:** State coordinates and tangent perturbations can have different dimensions. The action interface specifies dynamics, equality/inequality constraints, Jacobians, and Hessians in those spaces. It also requires `calc()` before `calcDiff()` because derivatives use cached values—a concrete ordering invariant. [Action model contract](https://raw.githubusercontent.com/loco-3d/crocoddyl/devel/include/crocoddyl/core/action-base.hpp)
- **C2:** An action model bundles dynamics, costs, and constraints for one trajectory node while keeping model and computation data distinct. Separate residual, activation, state, and integration abstractions support different robot tasks and solvers. The same header explains the mathematical contract that implementations must satisfy.

This entry concerns trajectory optimization under specified modeling/contact assumptions, rather than discovery of arbitrary contact sequences.

### 13. [pantor/ruckig](https://github.com/pantor/ruckig)

**Language / role:** C++, with bindings; online trajectory generation under velocity, acceleration, and jerk limits.

Study the numerically delicate transition from arbitrary initial motion to a target position, velocity, and acceleration, synchronized across degrees of freedom.

- **C1:** Tests exercise endpoint state agreement, nonnegative durations, absence of NaNs, repeated recalculation during execution, and randomized input regimes. These directly target numerical and state-transition failure modes. [Trajectory tests](https://raw.githubusercontent.com/pantor/ruckig/main/test/test_target.cpp)
- **C2:** The repository documents separate input, output, and trajectory objects, selectable synchronization/control interfaces, and dynamic degrees of freedom. The update loop explicitly transfers the generated state into the next input and replans when the observed state differs.

**Scope limit:** Local state-to-state generation is the relevant open-source implementation. The community version routes intermediate-waypoint calculation through a cloud API; the repository says that mode is not real-time capable. No cloud service was used in this research.

### 14. [hungpham2511/toppra](https://github.com/hungpham2511/toppra)

**Language / role:** C++ and Python implementations; time parameterization of a supplied geometric path under kinematic/dynamic constraints.

Study the separation between finding a path and finding a feasible, fast traversal of that path.

- **C1:** The derivation distinguishes path derivatives from time derivatives, including the acceleration term involving squared path speed. The guide explains smoothness requirements and why noisy interpolated waypoints can cause large fluctuations. [User guide and kinematic derivation](https://hungpham2511.github.io/toppra/notes.html)
- **C2:** Geometric-path objects, constraint objects, parameterization algorithms, and final trajectory parametrizers can be combined independently. The API examples compose velocity and acceleration constraints with an interpolated path. [Documentation entry point](https://hungpham2511.github.io/toppra/index.html)
- **C3:** Grid resolution trades numerical fidelity against solve cost; the guide describes automatic bisection-based grid selection and configurable error thresholds.

**Transition note:** The current repository warns that the separate Python implementation will be dropped in favor of C++ with bindings; the published guide still describes Python behavior.

## Hardware acceleration and differentiable computation

### 15. [NVlabs/curobo](https://github.com/NVlabs/curobo)

**Language / role:** Python, CUDA, and Warp; GPU robot kinematics, optimization, and motion generation.

Study a motion-generation system built around batched robot computations rather than one configuration per API invocation.

- **C2:** Differentiable forward kinematics produces tool-frame poses with gradients back to joint coordinates. The documented interface supports reuse within inverse kinematics, motion planning, MPC, and batched reachability analysis. [Forward-kinematics walkthrough](https://nvlabs.github.io/curobo/latest/api/curobo.examples.getting_started.forward_kinematics.html)
- **C3:** The walkthrough explains GPU evaluation using a parallel product-of-exponentials formulation and explicit batch dimensions for configurations, positions, and quaternions. Together with the repository’s separated kinematics, collision, and trajectory-optimization capabilities, this provides a concrete acceleration architecture to study.

**Version note:** cuRoboV2 is a substantial rewrite with changed public APIs. The repository points v1 users to tag `v0.7.8`; the linked walkthrough belongs to V2. No benchmark speedup is independently asserted here.

### 16. [KavrakiLab/vamp](https://github.com/KavrakiLab/vamp)

**Language / role:** C++, with Python bindings; CPU SIMD-accelerated sampling-based planning.

Study how vectorized collision checking and forward kinematics fit into recognizable RRT-Connect and roadmap algorithms. This is a separate implementation project also integrated into newer OMPL versions.

- **C2:** The RRT-Connect implementation is templated over robot representation and vectorization/validation parameters, accepts multiple goals, and uses replaceable sampling and nearest-neighbor components. [RRT-Connect implementation](https://raw.githubusercontent.com/KavrakiLab/vamp/main/src/impl/vamp/planning/rrtc.hh)
- **C3:** The same code allocates aligned configuration storage, bounds sample/iteration budgets, and keeps vectorized motion validation separate from tree growth and parent-chain reconstruction. This makes the relationship between memory layout and planner structure inspectable.

**Scope limit:** The repository ships precompiled robot models and uses a separate generation tool for additional robots. Its environment representations and collision approximations should be reviewed for the intended application; quoted demonstration timings are not general guarantees.

### 17. [UM-ARM-Lab/pytorch_kinematics](https://github.com/UM-ARM-Lab/pytorch_kinematics)

**Language / role:** Python/PyTorch; differentiable forward kinematics, Jacobians, and batched inverse kinematics.

Study numerical IK expressed as tensor kernels with explicit problem and retry dimensions.

- **C1:** The solver computes quaternion-based orientation error, offers damped least-squares and SVD formulations, and tracks position and rotation convergence separately for each attempt. The solution object documents that unconverged solution slots are not valid results. [IK implementation](https://raw.githubusercontent.com/UM-ARM-Lab/pytorch_kinematics/master/src/pytorch_kinematics/ik.py)
- **C2:** Robot trees can be converted into serial subchains, with selectable roots/end links and device/dtype control. This supports both whole-model FK and task-specific IK.
- **C3:** The implementation isolates a fused IK-step kernel compatible with `torch.compile`, while representing multiple targets and retries as batch dimensions. That design exposes the tradeoff between stable damping, convergence, and tensor throughput.

## Kinematics models and specialized solvers

### 18. [stack-of-tasks/pinocchio](https://github.com/stack-of-tasks/pinocchio)

**Language / role:** C++, with Python bindings; articulated-body kinematics, Jacobians, derivatives, and dynamics.

Study manifold-aware kinematics and the separation between a structural robot model and reusable computation data.

- **C1:** The IK example computes an SE(3) logarithmic error in the joint frame, adjusts the Jacobian using `Jlog6`, solves a damped system, and updates the configuration with manifold integration. It explicitly reports failure to converge. [Inverse-kinematics example](https://raw.githubusercontent.com/stack-of-tasks/pinocchio/devel/examples/inverse-kinematics.py)
- **C2:** The same example composes model/data construction, FK, Jacobians, Lie-group operations, and integration as independent primitives; these underpin custom solvers rather than only one fixed IK routine.
- **C4:** The changelog spans releases from 2020 through 2026 and records numerical fixes, code-generation repairs, compiler/Eigen compatibility, deprecations, and evolving constraint APIs. [Versioned changelog](https://raw.githubusercontent.com/stack-of-tasks/pinocchio/devel/CHANGELOG.md)

### 19. [orocos/orocos_kinematics_dynamics](https://github.com/orocos/orocos_kinematics_dynamics)

**Language / role:** C++, with PyKDL bindings; kinematic structures and forward/inverse solvers.

Study a compact numerical library designed for repeated robot-control calculations.

- **C1:** The Levenberg–Marquardt solver documents adaptive damping, task-space weighting, and distinct termination conditions for tiny gradients, ineffective joint increments, and iteration exhaustion. [LMA solver header](https://raw.githubusercontent.com/orocos/orocos_kinematics_dynamics/master/orocos_kdl/src/chainiksolverpos_lma.hpp)
- **C3:** That header describes cached FK/Jacobian intermediates, linear-in-chain-length Jacobian computation for fixed task dimension, and allocation restricted to construction. The preallocated workspace is visible in the class definition.
- **C4:** The changelog records releases in 2021 and 2025 with Python-version testing, binding compatibility, Windows fixes, and a joint thread-safety change. [Changelog](https://raw.githubusercontent.com/orocos/orocos_kinematics_dynamics/master/CHANGELOG.md)

**Compatibility note:** The repository distinguishes ROS 2 `master` from the ROS 1 `release-1.5` branch and warns that C++ and Python package versions must match.

### 20. [JuliaRobotics/RigidBodyDynamics.jl](https://github.com/JuliaRobotics/RigidBodyDynamics.jl)

**Language / role:** Julia; articulated mechanisms, spatial kinematics, Jacobians, and dynamics.

Study a native Julia implementation that carries robot geometry through generic scalar types and explicit coordinate-frame checks.

- **C1:** The design includes checks that reference frames agree before operations, singularity-free rotation parameterizations, and support for loop-joint constraints. These target errors that ordinary dimension checking does not catch. [Design documentation](https://juliarobotics.org/RigidBodyDynamics.jl/stable/)
- **C2:** Algorithms accept numerical, automatic-differentiation, and symbolic scalar types. `MechanismState` separately parameterizes state, model, and promoted cache scalars. [MechanismState contract](https://juliarobotics.org/RigidBodyDynamics.jl/stable/mechanismstate/)
- **C3:** State-dependent cached quantities avoid recomputing shared intermediates, while type-sorted joint collections expose an approach to controlling dispatch costs.

**Documentation limit:** The published stable pages retain old Julia installation guidance. The architectural contracts are useful; those installation paragraphs are not evidence of current runtime requirements.

### 21. [petercorke/robotics-toolbox-python](https://github.com/petercorke/robotics-toolbox-python)

**Language / role:** Python with compiled components; manipulator models, kinematics, and mobile-robot planning algorithms.

Study readable numerical methods behind a broad robotics API, especially the explicit IK result and failure contracts.

- **C1:** The IK base class distinguishes a quadratic weighted pose-error tolerance from linear position/orientation accuracy, limits iterations and restarts, rejects joint-limit violations, and returns success, residual, and failure reason separately. [IK implementation](https://raw.githubusercontent.com/petercorke/robotics-toolbox-python/main/src/roboticstoolbox/robot/IK.py)
- **C2:** The same solver abstraction supports Newton–Raphson, Gauss–Newton, Levenberg–Marquardt, and QP variants over elementary-transform-sequence models. Masks and initial guesses allow task-specific formulations. The repository also supports DH and URDF model construction.

The source documents compatibility behavior when replacing tuple results with `IKSolution`, offering a useful smaller example of API evolution without counting the MATLAB toolbox as another project.

### 22. [openrr/k](https://github.com/openrr/k)

**Language / role:** Rust; robot link trees, forward kinematics, URDF loading, and Jacobian IK.

Study a smaller native Rust kinematics library whose public model is a `Chain` of related nodes and joints, with `SerialChain` views for individual tasks.

- **C1:** Pose-error computation separates translation from a scaled-axis rotation error, and constrained IK selects the operational coordinates to solve. Separate distance/angle tolerances and bounded attempts make success conditions explicit. [IK source](https://docs.rs/k/latest/src/k/ik.rs.html)
- **C2:** The generic `InverseKinematicsSolver` trait works over scalar types and serial chains; coordinate constraints support reduced-DOF tasks, while a configurable null-space function adds posture objectives for redundant manipulators. [Jacobian solver API](https://docs.rs/k/latest/k/struct.JacobianIkSolver.html)

This is useful for examining reusable solver traits and robot-state representation at a smaller scale than a full planning framework.

### 23. [Phylliade/ikpy](https://github.com/Phylliade/ikpy)

**Language / role:** Python; chain-based forward and inverse kinematics with robot-description import.

Study the modeling and residual-construction layer around general numerical optimization, particularly active versus fixed joints.

- **C1:** The inspected solver expands active variables into a full chain, constructs position/orientation residuals, applies link-derived bounds, and optionally regularizes toward the initial configuration. It rejects undefined combinations such as optimizing neither position nor orientation. [Numerical solver source documentation](https://ikpy.readthedocs.io/en/latest/_modules/ikpy/inverse_kinematics.html)
- **C2:** Chains and links isolate robot representation from optimizer selection and task definition. Position-only, axis-orientation, and combined targets reuse the same FK-based residual construction, with interchangeable least-squares/scalar optimization.

**Version limit:** The inspected source documentation identifies itself as 3.3.4. The current repository additionally advertises an experimental JAX backend and revised optimizer budgets; those newer performance claims are not used to justify this entry.

### 24. [kevinzakka/mink](https://github.com/kevinzakka/mink)

**Language / role:** Python with native hot paths; differential inverse kinematics using MuJoCo models.

Study how local motion objectives become one constrained quadratic program. The project acknowledges its origin as a port of Pink; this selection counts Mink’s MuJoCo implementation once.

- **C1:** The solve contract distinguishes weighted objectives, inequality limits, and equality tasks. It exposes damping, tangent-space velocity, configuration-limit handling, and a `NoSolutionFound` exception. [IK problem construction and solver contract](https://kevinzakka.github.io/mink/api/inverse_kinematics.html)
- **C2:** Composable frame, posture, and center-of-mass tasks combine with position, velocity, and collision-avoidance limits. The tutorial explains their translation into quadratic objectives and constraints. [Tasks and limits](https://kevinzakka.github.io/mink/tutorial/tasks_and_limits.html)

**Scope limit:** This is a local differential solver. The API applies a default configuration limit, but additional limits must be supplied explicitly; collision avoidance is not implied merely by calling `solve_ik`.

### 25. [rdiankov/openrave](https://github.com/rdiankov/openrave)

**Language / role:** C++ and Python; robot motion-planning environment, included especially for the IKFast analytical kinematics compiler.

This is a historical design reference for compiling robot equations into reusable numerical code. The repository remains publicly available; this review does not establish its present maintenance cadence or promise modern dependency compatibility.

- **C1:** IKFast handles multiple solution branches and degenerate axis alignments; its design discusses invalid square-root/trigonometric domains and division-by-zero cases. Those issues make analytical IK substantially more difficult than a symbolic formula for a generic pose. [IKFast implementation and embedded design documentation](https://raw.githubusercontent.com/rdiankov/openrave/master/python/ikfast.py)
- **C2:** Several IK task types cover pose, rotation, translation, direction, and other partial constraints; redundant chains can expose free joint parameters. Generated C++ solvers can be used independently of the OpenRAVE runtime.
- **C3:** Symbolic work is performed during generation so repeated planning queries use specialized compiled evaluation. No microsecond timing claim is assumed to generalize across robots.

### 26. [Jmeyer1292/opw_kinematics](https://github.com/Jmeyer1292/opw_kinematics)

**Language / role:** C++; analytical forward/inverse kinematics for industrial arms with an ortho-parallel base and spherical wrist.

Study a deliberately constrained robot family whose geometry is captured by a small parameter set, avoiding a general symbolic compiler.

- **C1:** The implementation handles multiple analytical branches and explicitly treats the wrist singularity where joint five is zero and ordinary angle extraction becomes ambiguous. It also contains a concrete Eigen-expression lifetime/evaluation precaution. [Kinematics implementation](https://raw.githubusercontent.com/Jmeyer1292/opw_kinematics/master/include/opw_kinematics/opw_kinematics_impl.h)
- **C2:** Geometry parameters, joint-zero offsets, and sign corrections adapt the same templated solver to multiple manufacturers’ conventions. The repository explains equivalent solutions differing by full rotations and exposes forward checking and harmonization utilities.

**Scope limit:** The library does not enforce joint limits. Callers must reject invalid branches and consider equivalent rotations when checking limits; its README also labels some bundled example parameter sets as untested.

## Coverage, search method, and limitations

Discovery used more than six meaningfully different live-search formulations: sampling-based versus search-based planning; industrial ROS/ROS-independent frameworks; trajectory optimization and factor graphs; jerk-limited generation and path retiming; analytical versus numerical IK; Rust and Julia implementations; GPU/differentiable kinematics; CPU SIMD planning; and broader Java/C#/closed-loop searches. Follow-up searches revisited newer and smaller projects, including EXOTica, OxMPL, QuIK, Rust OPW implementations, and other recent kinematics libraries. Later searches increasingly returned already covered projects, ports, teaching code, or overlapping application frameworks. The selection is broad rather than exhaustive.

Every retained canonical repository was opened on GitHub. Each also has an additional opened primary source, including implementation files, solver contracts, architecture documentation, or tests. Browser cache misses for current Tesseract and HPP files were resolved with read-only requests to their public raw GitHub files. No repositories were cloned, dependencies installed, candidate code executed, external services modified, or maintainers contacted.

The list deliberately includes both large integration frameworks and smaller implementations with clear numerical contracts. Dependencies are counted separately only when they are substantive libraries in this category: for example, OMPL, Pinocchio, and TOPPRA remain distinct implementations even when a framework composes them. GPMP2’s original and continuation repositories are not counted twice; generated IKFast outputs, binding-only projects, incidental forks, awesome-lists, and tutorial collections are excluded. General collision engines and dynamics-only libraries were omitted when their relevance to planning/kinematics was primarily indirect.

Some sources are version-skewed: OMPL’s inspected core site, Julia’s published stable documentation, IKPy’s 3.3.4 source documentation, and TOPPRA’s Python guide require the qualifications stated above. Tesseract’s older standalone documentation repository was observed to be archived; this report instead links current documentation files inside the retained core repository. Historical value is identified for SBPL and OpenRAVE without equating longevity with active maintenance. C4 is claimed only where release history and concrete compatibility/testing work were inspected. Performance assessments concern visible architectural choices; this report contains no independently reproduced benchmark results.
