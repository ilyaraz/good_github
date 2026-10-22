# Localization, mapping, and sensor fusion systems

Research date: **2026-10-09**.

This selection covers 27 repositories implementing robot localization, SLAM, inertial and satellite navigation, spatial sensor fusion, and reusable map representations. It includes estimation libraries, complete pipelines, collaborative mapping, embedded attitude estimation, and offline navigation analysis. Stone Soup represents the adjacent but directly relevant problem of locating and tracking targets through multiple sensors. General GIS, route planning, image-processing utilities, and calibration-only tools are outside the main scope.

The criteria below describe concrete engineering material worth studying, not a certification of correctness or deployment readiness. Architectural judgments are inferences from the linked implementation and documentation. No candidate code was installed, executed, or benchmarked.

## Criteria legend

- **C1 — Difficult correctness:** numerical semantics, state invariants, concurrency, measurement ambiguity, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and representations supporting different sensors, estimators, or applications.
- **C3 — Performance with structure:** explicit management of computation, latency, memory, or hardware resources through an understandable architecture.
- **C4 — Sustained evolution:** evidence spanning years together with compatibility work, tests, or deliberate complexity management. Repository age and recent pushes alone do not qualify.

## Reusable estimation and fusion frameworks

### 1. [borglab/gtsam](https://github.com/borglab/gtsam)

**Language/role:** C++, with Python and MATLAB interfaces; factor-graph smoothing and mapping infrastructure.

Study how a mathematical estimation model becomes an incremental solver with explicit variable identity, factor ownership, linearization, and elimination rules. The relevant subsystem is `gtsam/nonlinear`, especially iSAM2, rather than the repository's many application notebooks.

- **C1:** The [iSAM2 interface](https://github.com/borglab/gtsam/blob/develop/gtsam/nonlinear/ISAM2.h) specifies which new variables may accompany an update and restricts marginalization to Bayes-tree leaves. It also explains that marginalization fixes affected linearization points—an important consistency constraint for downstream estimators.
- **C2, C3:** The [implementation](https://github.com/borglab/gtsam/blob/develop/gtsam/nonlinear/ISAM2.cpp) maintains the factor graph, variable index, cached linear factors, and Bayes tree across updates. This provides reusable incremental inference while controlling which portions require relinearization and elimination.

The inspected `develop` branch explicitly permits API changes; the README directs production users to stable releases.

### 2. [MRPT/mrpt](https://github.com/MRPT/mrpt)

**Language/role:** C++, with Python bindings; mobile-robot probabilistic estimation toolkit.

The relevant monorepo subsystems are `mrpt_slam`, `mrpt_bayes`, `mrpt_poses`, `mrpt_maps`, and `mrpt_obs`. This is useful for comparing particle localization and several map/sensor models within one type system.

- **C1:** The [motion-model documentation](https://github.com/MRPT/mrpt/blob/develop/doc/source/tutorial-motion-models.rst) develops uncertainty propagation on SE(2)/SE(3), including Gaussian and sampled odometry models. It makes the distinction between a pose increment and a probability distribution over increments explicit.
- **C2:** [CMonteCarloLocalization2D](https://github.com/MRPT/mrpt/blob/develop/modules/mrpt_slam/include/mrpt/slam/CMonteCarloLocalization2D.h) combines a weighted pose distribution with reusable particle-filter machinery and observation/action interfaces. Multiple proposal strategies and free-space-constrained initialization are exposed through that abstraction.

The inspected tree uses MRPT 3's reorganized `modules/` layout; older MRPT examples may use different paths and APIs.

### 3. [locusrobotics/fuse](https://github.com/locusrobotics/fuse)

**Language/role:** C++; ROS nonlinear least-squares sensor-fusion framework.

Study the boundary between independently arriving sensor observations and a shared optimization graph. Sensor models, motion models, variables, constraints, optimizers, and publishers have separate extension contracts.

- **C1:** [AsyncSensorModel](https://github.com/locusrobotics/fuse/blob/devel/fuse_core/include/fuse_core/async_sensor_model.h) documents private callback queues and delivery of optimizer results into the sensor's callback context. It explicitly distinguishes the synchronization obligations of single-threaded and multithreaded spinners.
- **C2, C3:** The [fixed-lag smoother](https://github.com/locusrobotics/fuse/blob/devel/fuse_optimizers/src/fixed_lag_smoother.cpp) batches transactions, applies motion models, optimizes, and marginalizes old variables. Its lock-order comments and handling of pending transactions make asynchronous integration and bounded estimation history concrete.

### 4. [cra-ros-pkg/robot_localization](https://github.com/cra-ros-pkg/robot_localization)

**Language/role:** C++; configurable EKF/UKF state-estimation nodes and satellite-coordinate integration for ROS.

This is a particularly useful integration-oriented codebase: real sensor messages require selective updates, consistent frames and units, meaningful covariances, and numerical safeguards.

- **C1:** The [EKF correction implementation](https://github.com/cra-ros-pkg/robot_localization/blob/rolling-devel/src/ekf.cpp) excludes NaN/infinite measurements, handles invalid or tiny variances, normalizes angular innovations, gates by Mahalanobis distance, and uses the Joseph covariance update.
- **C2:** The [configuration guide](https://github.com/cra-ros-pkg/robot_localization/blob/rolling-devel/doc/configuring_robot_localization.rst) explains per-variable fusion, planar operation, differential measurements, and avoiding duplicate information from related measurements.
- **C4:** The [changelog](https://github.com/cra-ros-pkg/robot_localization/blob/rolling-devel/CHANGELOG.rst) connects 2014 test-suite and covariance-stability work to 2026 ROS API and negative-time fixes. This is evidence of sustained handling of compatibility and failure cases, not simply longevity.

### 5. [JuliaRobotics/RoME.jl](https://github.com/JuliaRobotics/RoME.jl)

**Language/role:** Julia; robotics variables and factors for the Caesar/IncrementalInference ecosystem.

RoME offers a different abstraction style from the C++ frameworks: typed probabilistic factors, manifold operations, and sampling interfaces. The inference backend is a separate project; RoME supplies robotics-specific modeling components.

- **C1:** The [IMU delta factor](https://github.com/JuliaRobotics/RoME.jl/blob/develop/RoME/src/factors/Inertial/IMUDeltaFactor.jl) represents preintegrated rotation, velocity, position, elapsed time, covariance, and bias Jacobians on a dedicated group/manifold representation. This exposes the numerical conventions hidden inside many complete odometry systems.
- **C2:** The [bearing-range factor](https://github.com/JuliaRobotics/RoME.jl/blob/develop/RoME/src/factors/BearingRange2D.jl) accepts samplable beliefs, defines its measurement manifold, and also provides a parametric Gaussian measurement interface. The same robotics factor can participate in different inference workflows.

### 6. [dstl/Stone-Soup](https://github.com/dstl/Stone-Soup)

**Language/role:** Python; multisensor target tracking and state-estimation framework.

Include this for sensor fusion and target localization, rather than map construction. It is valuable when the hard problem includes uncertain association between detections, tracks, and sensors.

- **C1:** The [Chernoff updater](https://github.com/dstl/Stone-Soup/blob/main/stonesoup/updater/chernoff.py) implements distribution fusion and its Gaussian covariance-intersection specialization, with explicit covariance and measurement-prediction semantics. This is useful for studying fusion of estimated states rather than assuming every input is an independent raw observation.
- **C2:** The [track-fusion example](https://github.com/dstl/Stone-Soup/blob/main/docs/examples/trackfusion/Track2Track_Fusion_Example.py) composes radar sensors, different local trackers, track-to-detection feeders, a fusion tracker, and comparison metrics. Those components demonstrate substantial reusable interfaces across tracking architectures.

## Satellite navigation, inertial systems, and embedded fusion

### 7. [tomojitakasu/RTKLIB](https://github.com/tomojitakasu/RTKLIB)

**Language/role:** C; GNSS positioning library with real-time and post-processing applications.

Study the complete path from receiver observations and navigation data to a position estimate. This is a GNSS localization implementation, not an INS fusion system by itself.

- **C1:** [rtkpos.c](https://github.com/tomojitakasu/RTKLIB/blob/master/src/rtkpos.c) handles carrier-phase cycle slips, single-to-double-difference transformations, state covariance, and integer ambiguity resolution. These interacting discrete and continuous decisions are richer than a basic Kalman-filter example.
- **C2:** The repository documents a portable positioning library reused by streaming, real-time receiver, conversion, and post-processing applications, with several positioning modes and receiver protocols. The [LAMBDA unit tests](https://github.com/tomojitakasu/RTKLIB/blob/master/test/utest/t_lambda.c) provide an additional entry point into the numerical core through fixed ambiguity-resolution cases.

Treat this upstream as a historical reference when choosing a deployment baseline; current maintenance of downstream forks is not evidence about this repository.

### 8. [chichengcn/gici-open](https://github.com/chichengcn/gici-open)

**Language/role:** C++; GNSS/INS/camera integrated-navigation library, also called GICI-LIB.

GICI connects several GNSS solution families with inertial and visual estimation under a factor-graph architecture. Its acknowledged reuse of RTKLIB, OKVIS, and SVO components does not make it a mere wrapper: the fusion and estimator orchestration are substantial.

- **C1:** The [GNSS/IMU/camera estimator](https://github.com/chichengcn/gici-open/blob/master/src/fusion/gnss_imu_camera_srr_estimator.cpp) stages initialization, dispatches measurement roles, rejects reprojection outliers, detects persistent visual divergence, and marginalizes the moving estimation window.
- **C2, C3:** [EstimatorBase](https://github.com/chichengcn/gici-open/blob/master/include/gici/estimate/estimator_base.h) separates measurement admission, estimation, coordinates, initialization, and graph access. Solver iteration, thread, and time limits make resource policy configurable across derived estimators.

### 9. [rodralez/NaveGo](https://github.com/rodralez/NaveGo)

**Language/role:** MATLAB/GNU Octave; integrated-navigation processing, sensor simulation, and error analysis.

This adds an offline engineering perspective: connect an inertial sensor's error profile to simulated measurements and then inspect the navigation filter's intermediate quantities.

- **C1:** [ins_gnss.m](https://github.com/rodralez/NaveGo/blob/master/ins-gnss/ins_gnss.m) coordinates IMU and GNSS times, corrects antenna lever arms, propagates Earth/transport rates, applies error-state feedback, and renormalizes the attitude quaternion.
- **C2:** [acc_gen.m](https://github.com/rodralez/NaveGo/blob/master/simulation/acc_gen.m) accepts different reference-trajectory representations and composes gravity, Coriolis terms, white noise, static bias, dynamic bias, and random walk. Together with the documented analysis tools, this supports comparisons across sensor profiles and navigation configurations.

**Maintenance qualification:** The repository's README announces that its lead developer stepped down and the project transitioned to community stewardship. Do not infer an actively staffed maintenance team from its availability.

### 10. [xioTechnologies/Fusion](https://github.com/xioTechnologies/Fusion)

**Language/role:** C, with a Python package; embedded IMU attitude and heading fusion.

Study a compact streaming estimator whose state and failure-recovery rules are visible without the surrounding complexity of a full SLAM stack. It estimates orientation; it does not independently provide drift-free position.

- **C1:** [FusionAhrs.c](https://github.com/xioTechnologies/Fusion/blob/main/Fusion/FusionAhrs.c) combines quaternion integration and normalization with startup gain changes, gyro-overrange recovery, and acceleration/magnetic rejection logic. These mechanisms address physical conditions that violate nominal sensor assumptions.
- **C2, C3:** The [public AHRS interface](https://github.com/xioTechnologies/Fusion/blob/main/Fusion/FusionAhrs.h) exposes a fixed-size state, settings, internal status, and update variants with or without a magnetometer or with an external heading. Together with the per-sample implementation, this supports reusable embedded integration without a growing trajectory or optimization graph.

## Visual estimation and collaborative mapping

### 11. [rpng/open_vins](https://github.com/rpng/open_vins)

**Language/role:** C++; filter-based visual–inertial navigation research platform.

OpenVINS is useful for studying how an MSCKF implementation manages an evolving state and its covariance, rather than only the familiar high-level filter equations.

- **C1, C2:** [StateHelper](https://github.com/rpng/open_vins/blob/master/ov_msckf/src/state/StateHelper.cpp) implements state cloning, covariance-block propagation, marginalization, and local-index updates. Typed state variables make those operations reusable while exposing the indexing invariants they must preserve.
- **C1, C3:** [UpdaterMSCKF](https://github.com/rpng/open_vins/blob/master/ov_msckf/src/update/UpdaterMSCKF.cpp) projects out feature states, performs chi-square rejection, compresses the measurement system, and applies one assembled update. The decomposition connects estimator consistency with the cost of processing many feature tracks.

### 12. [UZ-SLAMLab/ORB_SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3)

**Language/role:** C++; visual, visual–inertial, and multi-map SLAM.

This research implementation is especially instructive for map lifecycle and coordination between local mapping, loop correction, and global bundle adjustment. The README labels its principal release as version 1.0 from December 2021; inclusion is not a claim of current production support.

- **C1:** [LoopClosing.cc](https://github.com/UZ-SLAMLab/ORB_SLAM3/blob/master/src/LoopClosing.cc) stops local mapping before loop correction and coordinates interruption of global bundle adjustment. It also contains distinct map-merging paths for inertial configurations.
- **C2:** [Atlas.cc](https://github.com/UZ-SLAMLab/ORB_SLAM3/blob/master/src/Atlas.cc) manages current and stored maps, map creation, camera registration, and keyframe/map-point insertion. This supplies reusable multi-map structure across the repository's camera and inertial configurations.

### 13. [HKUST-Aerial-Robotics/VINS-Fusion](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion)

**Language/role:** C++; optimization-based monocular/stereo visual–inertial state estimation.

Study a sliding-window estimator that supports camera/IMU extrinsic and timing calibration. This is a substantive extension of VINS-Mono, so VINS-Mono is not counted separately. The upstream describes its GPS integration as a toy example and documents older Ubuntu/ROS environments.

- **C1:** The [marginalization implementation](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion/blob/master/vins_estimator/src/factor/marginalization_factor.cpp) distinguishes local parameter dimensions, assembles normal equations, eliminates old state blocks, and retains a prior for later windows.
- **C2, C3:** The [estimator](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion/blob/master/vins_estimator/src/estimator/estimator.cpp) assembles different sensor configurations, conditionally estimates calibration variables, and applies solver-time limits. Sensor-mode changes and sliding-window bookkeeping reveal the practical cost of supporting several configurations in one estimator.

### 14. [princeton-vl/DROID-SLAM](https://github.com/princeton-vl/DROID-SLAM)

**Language/role:** Python/PyTorch and C++/CUDA; learned dense visual SLAM.

This provides a contrasting architecture in which learned correspondence updates interact with explicit geometric optimization. It is a research system with GPU dependencies and evaluation scripts, not a generic device-independent SLAM service.

- **C1:** The [bundle-adjustment implementation](https://github.com/princeton-vl/DROID-SLAM/blob/main/droid_slam/geom/ba.py) constructs pose/depth normal equations, masks invalid projections, fixes selected poses, uses a Schur solve, and retracts pose updates onto the manifold.
- **C3:** The [asynchronous implementation](https://github.com/princeton-vl/DROID-SLAM/blob/main/droid_slam/droid_async.py) separates frontend and backend processes, supports separate GPU devices, protects shared snapshots, and aligns pose/scale between histories. The README explicitly notes that asynchronous execution is nondeterministic.

### 15. [ethz-asl/maplab](https://github.com/ethz-asl/maplab)

**Language/role:** C++; modular multi-session and multi-robot mapping research framework.

The relevant subsystems are VI-map storage, map management, optimization, and the mapping console/server. Study persistent map operations and access discipline across sessions, rather than treating the project only as a camera odometry frontend. The checked documentation retains an Ubuntu 18.04/ROS Melodic baseline.

- **C1:** The [MapManager access guide](https://github.com/ethz-asl/maplab/blob/master/docs/pages/tutorials-extending-maplab/A_Using-the-MapManager.md) explains scoped write locks, shared const access, and the distinction between direct and thread-safe map access.
- **C2:** The [MapManager interface](https://github.com/ethz-asl/maplab/blob/master/backend/map-manager/include/map-manager/map-manager.h) provides map-type-independent storage and operations, with explicit read/write access objects. This supports shared mapping tools without embedding storage ownership and locking separately in every algorithm.

### 16. [v4rl-ucy/covins](https://github.com/v4rl-ucy/covins)

**Language/role:** C++; COVINS/COVINS-G collaborative visual–inertial mapping backend.

Count this for its separate communication and collaborative backend, not its bundled ORB-SLAM3 frontend. COVINS-G accepts different odometry frontends and joins maps contributed by multiple agents. It is a historical research framework; the checked [repository metadata](https://api.github.com/repos/v4rl-ucy/covins) reported its latest push in December 2023.

- **C1:** [map_be.cpp](https://github.com/v4rl-ucy/covins/blob/master/covins_backend/src/covins_backend/map_be.cpp) implements map fusion and shared/exclusive map checkout using usage counters and mutexes. It must preserve client, keyframe, landmark, and loop-constraint relationships while maps are accessed concurrently.
- **C2:** [communicator_be.cpp](https://github.com/v4rl-ucy/covins/blob/master/covins_backend/src/covins_backend/communicator_be.cpp) converts buffered keyframe and landmark messages into backend map objects, distinguishing creation from updates. This communication boundary is what makes a collaborative backend reusable across agents and frontends.

## Laser SLAM and LiDAR odometry

### 17. [cartographer-project/cartographer](https://github.com/cartographer-project/cartographer)

**Language/role:** C++; 2D/3D SLAM with local submaps and global trajectory optimization.

**Historical project:** Its README explicitly says it is no longer actively maintained. The ROS forks are not counted as independent selections. The original implementation remains useful for studying the separation of low-latency local estimation from asynchronous global correction.

- **C1:** The [2D local trajectory builder](https://github.com/cartographer-project/cartographer/blob/master/cartographer/mapping/internal/2d/local_trajectory_builder_2d.cc) collates range data, waits for the required pose extrapolator initialization, filters points, matches scans, and inserts results into submaps.
- **C2, C3:** The [2D pose graph](https://github.com/cartographer-project/cartographer/blob/master/cartographer/mapping/internal/2d/pose_graph_2d.cc) manages multiple trajectories and sensor constraints through a work queue and thread pool. Queue size/delay metrics and trajectory-state checks expose both performance and lifecycle concerns.

### 18. [SteveMacenski/slam_toolbox](https://github.com/SteveMacenski/slam_toolbox)

**Language/role:** C++; ROS 2 planar SLAM, persistent pose graphs, and localization.

Study the engineering needed to resume mapping, edit a graph, and localize within previous map data. Its modified Karto integration and solver plugins are more substantial than a launch/configuration wrapper.

- **C1:** The [Ceres solver plugin](https://github.com/SteveMacenski/slam_toolbox/blob/ros2/solvers/ceres_solver.cpp) anchors an initial pose, guards node operations with a mutex, validates constraint endpoints, and manages parameter-block removal. These details expose graph gauge and object-lifetime obligations.
- **C2:** The [serialization interface](https://github.com/SteveMacenski/slam_toolbox/blob/ros2/include/slam_toolbox/serialization.hpp) stores and reloads both the mapper's pose graph and its dataset, supporting the README's resumed-mapping and localization workflows. It handles archive failures, but the inspected two-file write should not be assumed atomic.

### 19. [introlab/rtabmap](https://github.com/introlab/rtabmap)

**Language/role:** C++; RTAB-Map core library and standalone mapping application.

The relevant subsystem is `corelib`; the separate ROS integration repository is not counted. This is a strong place to study how a long-running mapper controls its working set while retaining information for later localization and loop closure.

- **C1:** [Memory.cpp](https://github.com/introlab/rtabmap/blob/master/corelib/src/Memory.cpp) maintains relationships between signatures, visual words, neighbor links, and database-backed history. Graph reduction explicitly preserves references that may still be needed by transferred nodes.
- **C3:** [Rtabmap.cpp](https://github.com/introlab/rtabmap/blob/master/corelib/src/Rtabmap.cpp) invokes forgetting when configured time or working-memory thresholds are exceeded, protects selected locations from eviction, and repairs the local optimized graph after transfers. Resource limits are coupled to map consistency rather than implemented as blind deletion.

### 20. [TixiaoShan/LIO-SAM](https://github.com/TixiaoShan/LIO-SAM)

**Language/role:** C++; LiDAR–inertial smoothing and mapping with optional GPS and loop constraints.

Study its two-estimator arrangement: a persistent mapping graph and a periodically reset IMU graph. The default branch is the original ROS 1 implementation; the README points to a separate ROS 2 branch.

- **C1:** [mapOptmization.cpp](https://github.com/TixiaoShan/LIO-SAM/blob/master/src/mapOptmization.cpp) gates GPS factors by timing, covariance, and initialization conditions, and assembles odometry and loop-closure constraints. The unusual filename spelling is the actual upstream path.
- **C1, C3:** [imuPreintegration.cpp](https://github.com/TixiaoShan/LIO-SAM/blob/master/src/imuPreintegration.cpp) carries marginal covariances into priors when resetting its graph, checks implausible velocity/bias estimates, and repropagates queued IMU measurements after a correction. This links bounded optimization cost with continued high-rate odometry.

### 21. [hku-mars/FAST_LIO](https://github.com/hku-mars/FAST_LIO)

**Language/role:** C++; iterated-filter LiDAR–inertial odometry and incremental mapping.

FAST-LIO provides a useful comparison with graph-based LIO-SAM: the estimation loop centers on an iterated error-state filter and a dynamically updated local point map.

- **C1:** [IMU_Processing.hpp](https://github.com/hku-mars/FAST_LIO/blob/main/src/IMU_Processing.hpp) initializes gravity/bias-related state, stitches measurements across scan boundaries, sorts points by acquisition time, and propagates IMU poses for scan undistortion.
- **C3:** [laserMapping.cpp](https://github.com/hku-mars/FAST_LIO/blob/main/src/laserMapping.cpp) combines the iterated update with incremental spatial-index insertion, selective downsampling, and removal of regions outside a moving local map. These mechanisms address repeated-neighbor-search and map-growth costs without requiring unsupported headline throughput claims.

### 22. [koide3/glim](https://github.com/koide3/glim)

**Language/role:** C++, with GPU-backed registration components; extensible point-cloud localization and mapping.

GLIM is useful for studying direct registration factors across multiple scans and adding application-specific constraints without rewriting the mapping pipeline.

- **C1, C2:** The [extension guide](https://github.com/koide3/glim/blob/master/docs/extend.md) specifies pose, velocity, and bias keys, distinguishes LiDAR-only from inertial configurations, and warns that added factors may refer only to variables still inside the smoother window. Callback slots and dynamically loaded modules form concrete extension contracts.
- **C3:** The [GPU odometry implementation](https://github.com/koide3/glim/blob/master/src/glim/odometry/odometry_estimation_gpu.cpp) builds voxelized registration factors using reusable stream/buffer resources and limits retained keyframes using overlap and scoring. Performance choices are visible at the graph-construction level.

### 23. [PRBonn/kiss-icp](https://github.com/PRBonn/kiss-icp)

**Language/role:** C++ core, Python interface, ROS integration; LiDAR odometry.

This is a deliberately compact odometry pipeline, not a complete loop-closing SLAM system. It is a useful counterpoint to the larger frameworks because the major algorithmic choices remain easy to follow.

- **C2:** [KissICP.cpp](https://github.com/PRBonn/kiss-icp/blob/main/cpp/kiss_icp/pipeline/KissICP.cpp) composes preprocessing, voxelization, motion prediction, adaptive correspondence thresholds, registration, and model-deviation feedback through distinct components that can be studied and reused independently of the Python and ROS interfaces.
- **C3:** [VoxelHashMap.cpp](https://github.com/PRBonn/kiss-icp/blob/main/cpp/kiss_icp/core/VoxelHashMap.cpp) caps retained points per voxel, rejects excessively close samples, and removes distant map content. The spatial representation makes the memory and nearest-neighbor workload policy inspectable.

The README deprecates ROS 1 support and identifies the last release that supported it; integrations should not assume both ROS generations remain equivalent.

## Reusable spatial map representations

### 24. [OctoMap/octomap](https://github.com/OctoMap/octomap)

**Language/role:** C++; probabilistic 3D occupancy octrees, with visualization and distance-map subsystems.

Focus on the `octomap` library. It supplies the map representation and sensor-update machinery that a localization or planning system can consume; it does not estimate the sensor trajectory by itself.

- **C1, C3:** [OccupancyOcTreeBase.hxx](https://github.com/OctoMap/octomap/blob/devel/octomap/include/octomap/OccupancyOcTreeBase.hxx) turns rays into occupied/free updates, maintains log-odds occupancy, propagates child state, and prunes homogeneous regions. Correct update semantics and compact hierarchical storage are tightly connected.
- **C2, C4:** The [changelog](https://github.com/OctoMap/octomap/blob/devel/octomap/CHANGELOG.txt) records generic tree/node refactoring, CTest adoption, numerical fixes, and compiler/ROS compatibility work across releases from 2010 through 2024. This supports both extensibility and a sustained complexity-management record.

### 25. [ethz-asl/voxblox](https://github.com/ethz-asl/voxblox)

**Language/role:** C++; CPU volumetric mapping with truncated and Euclidean signed distance fields.

Study the transition from surface reconstruction to a distance field useful for collision queries, plus the tradeoffs between alternative integration policies. This is a research mapping library; it assumes externally supplied poses.

- **C1:** The [ESDF integrator](https://github.com/ethz-asl/voxblox/blob/master/voxblox/src/integrator/esdf_integrator.cc) tracks observed space, parent relationships, and raise/open queues as distance information changes. It also distinguishes cleared and artificially initialized regions used in planning.
- **C2, C3:** The [TSDF integrator interfaces](https://github.com/ethz-asl/voxblox/blob/master/voxblox/include/voxblox/integrator/tsdf_integrator.h) offer common configuration with simple, merged-ray, and fast integration strategies. Thread-safety assumptions, integration-time limits, and approximate-set tradeoffs are documented rather than hidden behind a single opaque routine.

### 26. [nvidia-isaac/nvblox](https://github.com/nvidia-isaac/nvblox)

**Language/role:** C++/CUDA, with Python interfaces; GPU occupancy and signed-distance mapping.

Study how a sparse map representation is adapted to GPU execution. The repository contains a substantive mapping implementation; the ROS wrappers and separate Torch repositories are not counted again.

- **C2, C3:** The [technical design](https://github.com/nvidia-isaac/nvblox/blob/public/docs/pages/technical_details.rst) explains custom layers, sparse voxel-block allocation, contiguous block storage, and correspondence between voxel blocks and CUDA thread blocks for coalesced access.
- **C1, C3:** The [ESDF CUDA implementation](https://github.com/nvidia-isaac/nvblox/blob/public/nvblox/src/integrators/esdf_integrator.cu) marks obstacle sites, tracks blocks requiring clearing, uses synchronized shared state and atomic work-list insertion, and sweeps distance information. It exposes the consistency work required when surfaces change under parallel processing.

### 27. [ANYbotics/grid_map](https://github.com/ANYbotics/grid_map)

**Language/role:** C++; layered 2.5D robot-centric maps and conversion/filtering interfaces.

This covers a different representation from occupancy octrees and dense reconstruction: elevation, variance, traversability, and other quantities share a moving grid.

- **C1, C2, C3:** [GridMap.cpp](https://github.com/ANYbotics/grid_map/blob/master/grid_map_core/src/GridMap.cpp) manages named matrix layers, coordinate/index conversions, submaps, and circular-buffer movement. Moving a map clears exposed regions and adjusts indices instead of copying all retained cells; wraparound and whole-map shifts are explicit cases.
- **C4:** The [core changelog](https://github.com/ANYbotics/grid_map/blob/master/grid_map_core/CHANGELOG.rst) documents evolution from 2015 onward, including moved-map iterator tests, circular-buffer bug fixes, Eigen alignment, and compiler/distribution compatibility. These are concrete examples of managing representation complexity over time.

## Coverage, verification, and limitations

Discovery used more than twenty distinct live search formulations, including LiDAR–inertial factor graphs; MSCKF visual–inertial estimation; ROS EKF/UKF and asynchronous fusion; GNSS/INS tight integration; octree, TSDF, and ESDF mapping; Julia/Rust/Python estimation libraries; collaborative mapping; learned dense SLAM; embedded AHRS; UWB/range-only localization; and MATLAB/Octave navigation simulation. Searches also checked less prominent frameworks and alternative implementations rather than ordering by stars. Later queries largely repeated the established architectural families; NaveGo was retained because it added a materially different analysis workflow and implementation language.

Canonical repository names and default branches were checked through the GitHub API for the first 26 researched candidates; NaveGo was verified by opening its GitHub repository page after the shared unauthenticated API rate limit was reached. Source-tree inventories and actual source/document bodies were read, including at least one non-README implementation or design source for every selection. The links above are verified entry points on the inspected branches, which can change after this date. No repository was cloned or executed.

The API did not mark any of those 26 repositories archived. That is not evidence of active maintenance: [Cartographer explicitly declares inactivity](https://github.com/cartographer-project/cartographer/blob/master/README.rst), [NaveGo announces a stewardship transition](https://github.com/rodralez/NaveGo/blob/master/README.md), and ORB-SLAM3, VINS-Fusion, maplab, RTKLIB, voxblox, and COVINS are included as valuable historical/research references rather than promises of current support. Maintenance qualifications use the checked upstream documentation and metadata; C4 is awarded only where the report identifies substantive change history.

The selection excludes tutorial/student reimplementations, Docker collections, thin ROS bindings, hardware SDK wrappers without the estimation core, and duplicated forks. It does not attempt an exhaustive catalog of invariant filters, range-only localization, calibration, neural mapping, or every vehicle flight-stack estimator. Rust searches surfaced promising projects, but none was retained solely to satisfy language variety. COVINS is counted for its independently substantive collaborative backend despite bundled upstream frontend code; GICI is counted for its integrated estimator architecture despite acknowledged component reuse. Numerical accuracy and timing claims were not independently reproduced, and no claim is made that every subsystem is uniformly exemplary.
