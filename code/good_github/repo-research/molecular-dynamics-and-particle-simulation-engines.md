# Molecular dynamics and particle simulation engines

Research date: **2026-10-09**.

This selection covers 26 GitHub repositories that implement molecular or physically interacting particle dynamics: atomistic and coarse-grained MD, Brownian reaction–diffusion, event-driven collisions, granular discrete elements, smoothed particle hydrodynamics (SPH), gravitational N-body dynamics, and particle-in-cell (PIC) plasma simulation. The emphasis is on engines and substantial simulation libraries whose numerical methods and software architecture can be studied together. Visualization packages, trajectory analysis, force-field-only libraries, and wrappers around other engines are outside the main selection.

Each repository was verified through its GitHub page or public GitHub API, and an additional implementation or technical documentation source was read. Criteria below are evidence-based selection judgments, not guarantees that every component is exemplary. Links to development branches describe inspected code and may change after this date; they are not promises about a particular released binary.

**Criteria legend**

- **C1 — Difficult correctness:** numerical invariants, statistical semantics, concurrency, edge cases, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and data models supporting different simulations or algorithms.
- **C3 — Performance with structure:** concrete computational constraints addressed through understandable algorithms, layouts, decomposition, or execution architecture.
- **C4 — Sustained evolution:** years of development accompanied by evidence of compatibility management, testing, or architectural complexity management. Age alone does not qualify.

## General atomistic and molecular engines

### 1. [lammps/lammps](https://github.com/lammps/lammps)

**Language / role:** C++ with accelerator backends and language interfaces; general classical MD and materials/particle simulation.

Study the interaction between spatial decomposition, particle ownership, and neighbor-list construction. This is especially useful when a seemingly local optimization must preserve correctness across MPI boundaries and different potential cutoffs.

- **C1:** The neighbor-list design distinguishes owned and ghost atoms, full and half lists, orthogonal and triclinic geometry, and Newton-pair settings. Migration and periodic remapping occur at rebuilding steps; a skin-displacement condition determines when cached neighbors cease to be valid.
- **C3:** Multiple-page neighbor storage, spatial particle sorting, bin stencils, and multiple bin sizes for disparate cutoffs address memory consumption and unnecessary pair work. The documentation explains their tradeoffs rather than merely asserting scalability.

**Entry point:** [Developer explanation of neighbor lists](https://docs.lammps.org/Developer_par_neigh.html), which connects the data structures directly to those correctness and performance decisions.

### 2. [gromacs/gromacs](https://github.com/gromacs/gromacs)

**Language / role:** C++; biomolecular and general molecular simulation. **Official GitHub backup/mirror:** the repository identifies GitLab as the development and issue-tracking home.

Study how a production molecular engine co-designs its hottest interaction kernel with scientific validation.

- **C3:** The [NxM nonbonded algorithm design](https://github.com/gromacs/gromacs/blob/main/docs/doxygen/lib/nbnxm.md) replaces individual atom-pair lists with spatially formed atom clusters. Cluster-pair kernels regularize access for SIMD and GPUs; GPU superclusters add another level of data reuse.
- **C1:** [Physical validation](https://github.com/gromacs/gromacs/blob/main/docs/dev-manual/physical_validation.rst) tests timestep convergence of conserved quantities, kinetic-energy distributions, and configurational ensemble distributions. It explicitly recognizes that a failing integrator test can reveal discontinuous potentials or constraint errors elsewhere in the model.

**Entry points:** The two documents above provide a compact performance-design and correctness-validation pairing. The longer statistical tests are distinguished from checks intended for every build.

### 3. [openmm/openmm](https://github.com/openmm/openmm)

**Language / role:** C++ computational library, GPU implementations, and Python application/API layers; extensible molecular simulation.

Study the separation of a reusable physical model from a particular simulation execution. This is a useful example of making hardware backends and new force implementations independently extensible.

- **C2:** The [core-library architecture](https://docs.openmm.org/latest/developerguide/02_core_library.html) separates public `System`, `Force`, `Integrator`, and `Context` objects from implementation objects and kernel factories. A shared `System` can have multiple contexts, while each context receives its own force implementation state and integrator.
- **C3:** The [architectural overview and low-level API](https://docs.openmm.org/latest/userguide/library/01_introduction.html) explain hardware-specific computation beneath a platform-independent API. State is queried in bulk because device-to-host transfers are expensive. Logical kernels need not correspond one-to-one with GPU launches, leaving room for splitting or combining computation.

**Entry points:** The two linked architecture guides, followed by the repository's `platforms` implementations.

### 4. [ccp5UK/dl-poly](https://github.com/ccp5UK/dl-poly)

**Language / role:** Fortran with MPI; general classical molecular dynamics. **Official substantive GitHub mirror:** its repository metadata points to the CCP5 GitLab upstream.

Study the distributed implementation of molecular constraints, not just unconstrained point-particle integration.

- **C1:** The [parallelisation manual](https://github.com/ccp5UK/dl-poly/blob/devel/documentation/source/UserManual/parallelisation/parallelisation.rst) explains why bonds shared across processor domains require neighboring processors to exchange corrected positions or velocities during SHAKE/RATTLE iterations. Ordinary halo exchange alone is insufficient.
- **C3:** That same document connects domain allocation, link-cell pair construction, halo particles, and atom migration to named source routines, while identifying density uniformity as an efficiency limitation.
- **C2:** The [bond-constraint treatment](https://github.com/ccp5UK/dl-poly/blob/devel/documentation/source/UserManual/integration_algs/bond_constraints.rst) distinguishes position and velocity corrections for different integrators, providing reusable machinery for constrained molecular models.

**Entry points:** The linked parallelisation and bond-constraint chapters.

### 5. [TinkerTools/tinker](https://github.com/TinkerTools/tinker)

**Language / role:** Fortran and OpenMP; molecular mechanics and MD, particularly polarizable multipole force fields. This entry concerns the CPU Tinker codebase, not separate Tinker-family GPU projects.

Study a polarizable engine in which force evaluation itself contains an iterative numerical solve, and integration must handle multiple physical timescales.

- **C1:** [`source/induce.f`](https://github.com/TinkerTools/tinker/blob/main/source/induce.f) implements direct/mutual induced dipoles, including a preconditioned conjugate-gradient solver. It states the prerequisite that multipoles be rotated into the global frame and maintains prior dipoles for prediction.
- **C3:** [`source/respa.f`](https://github.com/TinkerTools/tinker/blob/main/source/respa.f) explicitly splits fast and slow force terms in reversible multiple-timestep integration. Its inner loop applies position and velocity constraints and accumulates fast-term virials before the outer slow-force update.

**Entry points:** Those two numerical source files. The repository README also cautions that parameter files and executables from different Tinker versions are not generally interchangeable; inclusion here should not be read as a compatibility guarantee.

### 6. [brucefan1983/GPUMD](https://github.com/brucefan1983/GPUMD)

**Language / role:** CUDA/C++; GPU molecular dynamics with empirical and neuroevolution potentials. The relevant subsystem is the `gpumd` simulation engine; the same repository also contains NEP training tools.

Study how a common force interface accommodates many-body models while keeping forces, virials, and transport observables mathematically consistent.

- **C1:** The [forces-and-stresses derivation](https://github.com/brucefan1983/GPUMD/blob/master/doc/theory/forces_and_stresses.rst) derives an antisymmetric pair-force representation for general many-body site energies and connects it to the virial. This is more subtle than applying a pair-potential formula to every model.
- **C2:** [`Potential`](https://github.com/brucefan1983/GPUMD/blob/master/src/force/potential.cuh) defines a shared computation contract over box geometry, types, device positions, potential energy, forces, and virials. Protected many-body accumulation methods accept different intermediate precisions while producing double-precision outputs.

**Entry points:** The theory document and potential base interface above. No hardware speedup figure is assumed to transfer between models or GPUs.

### 7. [OpenMD/OpenMD](https://github.com/OpenMD/OpenMD)

**Language / role:** C++ and MPI; MD of liquids, interfaces, nanoparticles, and models with orientational degrees of freedom.

Study a less prominent engine that unifies ordinary atoms, directional atoms, and rigid bodies without forcing all of them to expose identical physical degrees of freedom.

- **C2:** [`StuntDouble`](https://github.com/OpenMD/OpenMD/blob/main/src/primitives/StuntDouble.hpp) is the common object manipulated by integrators and minimizers. Dynamic values live in snapshots outside the object, while the interface dispatches access to the appropriate storage.
- **C1:** The same implementation distinguishes translational and rotational state: freezing a linear directional object removes a different number of degrees of freedom than freezing a nonlinear rigid object or a point atom. Its stated interface contract also guards against physically meaningless operations such as torquing an ordinary atom.
- **C2:** [`ForceManager`](https://github.com/OpenMD/OpenMD/blob/main/src/brains/ForceManager.hpp) separates setup, short-range and long-range interactions, modifiers, and pre/post computation. Initialization is deferred until force-field atom types are known.

**Entry points:** `StuntDouble.hpp` and `ForceManager.hpp`.

## Soft matter, coarse-graining, events, and reactions

### 8. [glotzerlab/hoomd-blue](https://github.com/glotzerlab/hoomd-blue)

**Language / role:** C++/GPU kernels with Python configuration; soft-matter MD and hard-particle Monte Carlo.

Study reusable neighbor-search infrastructure beneath multiple interaction objects, with explicit choices about accuracy and amortized work.

- **C1:** The [neighbor-list implementation and API documentation](https://github.com/glotzerlab/hoomd-blue/blob/trunk/hoomd/md/nlist.py) specify the half-buffer displacement rebuild rule and topology-based exclusions. They also state the particular default settings under which changing the buffer affects performance but not correctness.
- **C2:** Multiple pair forces can share one list, whose effective cutoff covers the maximum required interaction range, or use independent lists.
- **C3:** `Cell`, `Tree`, and `Stencil` expose alternative search algorithms; the buffer mediates between rebuilding too often and evaluating too many irrelevant candidate pairs. See also the [neighbor-list reference](https://hoomd-blue.readthedocs.io/en/latest/hoomd/md/module-nlist.html).

**Entry points:** `hoomd/md/nlist.py` and the linked reference.

### 9. [espressomd/espresso](https://github.com/espressomd/espresso)

**Language / role:** C++ with Python control and parallel backends; coarse-grained soft matter, electrostatics, hydrodynamic coupling, and related particle models.

Study how the cell/particle layer coordinates changing ownership, ghost communication, and force accumulation across a growing collection of physical methods.

- **C1:** [`CellStructure`](https://github.com/espressomd/espresso/blob/python/src/core/cell_system/CellStructure.hpp) documents that pending ghost-force reductions must finish before resorting or changing decomposition. It also repairs particle-index pointers after storage reallocation and records scratch-storage concurrency restrictions.
- **C3:** Persistent ghost-exchange buffers avoid repeated allocation; dirty flags permit skipping unnecessary clearing and reduction of torque, dipole, or virial buffers.
- **C4:** The [changelog](https://github.com/espressomd/espresso/blob/python/CHANGELOG.md) spans releases from 2011 through 2026, records semantic versioning since 4.0, and documents concrete checkpoint, feature-dependency, compiler, and numerical fixes, including compatibility-affecting parameter changes.

**Entry points:** The cell-system header and changelog. Some inspected cell-system work is on the development branch.

### 10. [espressopp/espressopp](https://github.com/espressopp/espressopp)

**Language / role:** C++ with Python and MPI; soft-matter MD and adaptive-resolution simulation.

The repository explicitly states that ESPResSo++ and ESPResSo share roots but have independent development and different implementations. Study its integration extension mechanism and the bookkeeping needed when atomistic and coarse-grained descriptions coexist.

- **C2:** [`MDIntegrator`](https://github.com/espressopp/espressopp/blob/master/src/integrator/MDIntegrator.hpp) publishes signals around position updates, force initialization, local-force computation, ghost-force collection, and velocity updates. Extensions attach to these stages instead of duplicating the full integration loop.
- **C1:** The [AdResS extension](https://github.com/espressopp/espressopp/blob/master/src/integrator/Adress.py) ensures atomistic particles are initialized and propagated alongside coarse-grained particles. It documents consistency requirements between its multistep setting and the RESPA integrator.
- **C3:** The same source explains the tradeoff between frequent updates of moving resolution regions and their communication/computational cost.

**Entry points:** `MDIntegrator.hpp` and the AdResS implementation documentation.

### 11. [lorenzo-rovigatti/oxDNA](https://github.com/lorenzo-rovigatti/oxDNA)

**Language / role:** C++/CUDA with Python bindings; standalone coarse-grained DNA/RNA and other particle models.

Study an interaction framework designed around anisotropic, bonded particles and specialized sampling. This is the standalone engine, not the oxDNA model implementation inside LAMMPS.

- **C2:** [`BaseInteraction`](https://github.com/lorenzo-rovigatti/oxDNA/blob/master/src/Interactions/BaseInteraction.h) delegates particle allocation, topology interpretation, interaction-dependent sanity checks, and energy-term evaluation to model implementations. It also exposes hard-potential/infinite-energy state and configuration-generation hooks.
- **C3:** The [performance guide](https://github.com/lorenzo-rovigatti/oxDNA/blob/master/docs/source/performance.md) connects measured time in lists, forces, observables, and integration to tunable neighbor skins, cell sizes, and occupancy capacity. It describes GPU particle sorting and the memory/performance tradeoff in automatic cell sizing.
- **C1:** That guide explicitly relates excessively large timesteps to instability and cell occupancy settings to allocation failure.

**Entry points:** The interaction interface and performance guide. The repository documents single-core or single-GPU simulations; Python-level replica orchestration is a separate form of parallelism.

### 12. [halmd-org/halmd](https://github.com/halmd-org/halmd)

**Language / role:** C++/CUDA with Lua scripting; molecular dynamics focused on soft matter, nanofluidics, and long-time numerical stability.

Study an engine where dependency tracking and precision policy are explicit design subjects.

- **C1:** The [floating-point design note](https://github.com/halmd-org/halmd/blob/testing/doc/develop/floating_point.rst.in) identifies accumulated position/velocity updates and derived observables as places requiring higher precision. It distinguishes input precision from the precision used for reductions, while candidly noting incomplete generic precision support.
- **C2:** [Signals and data caches](https://github.com/halmd-org/halmd/blob/testing/doc/develop/signals.rst.in) describe C++ data dependencies combined with Lua-connected signal/slot relationships. Sampling state can trigger integration and force recomputation through these dependencies.
- **C3:** Cache observers suppress redundant recomputation, preserving scriptable composition without blindly recalculating every dependency.

**Entry points:** The two design notes. The module-writing document encountered during research was skeletal, so it is deliberately not used as architectural evidence.

### 13. [dynamomd/DynamO](https://github.com/dynamomd/DynamO)

**Language / role:** C++; event-driven particle dynamics, including collision-based models.

Study discrete-event scheduling as an alternative to advancing every interaction at a fixed timestep. The particularly instructive code is the handling of nearly simultaneous events under finite precision.

- **C1:** [`Scheduler::runNextEvent`](https://github.com/dynamomd/DynamO/blob/master/src/dynamo/dynamo/schedulers/scheduler.cpp) recalculates a queued collision before execution. It handles invalidation, nonfinite event times, and a rejection watchdog that prevents rounding-induced cycles in which two events repeatedly exchange order.
- **C2:** The scheduler handles interaction, local, global, and system events through separate interfaces and dispatches updates to output plugins.
- **C3:** The [source organization](https://github.com/dynamomd/DynamO/blob/master/src/Readme.md) separates event-driven simulation from the reusable `magnet` sorting/collision library and `coil` visualization library; the scheduler supports neighbor-based event selection rather than requiring all-pair scheduling.

**Entry points:** The scheduler source and source-layout guide. The watchdog is an engineering response to finite precision, not a claim of exact arithmetic.

### 14. [readdy/readdy](https://github.com/readdy/readdy)

**Language / role:** C++ with Python bindings; interacting-particle Brownian reaction–diffusion and changing molecular complexes.

Study the combination of continuous stochastic motion, competing discrete reactions, and graph-structured particle complexes.

- **C1:** The [simulation guide](https://readdy.github.io/simulation.html) explains why reactions sharing reactants cannot simply be applied independently. Its Gillespie handler selects by normalized rates and removes conflicting events after consumption; the alternative approximation has documented timestep-dependent bias. Topology graphs must also be connected and have configured bond potentials.
- **C2:** System specification is copied into independently configurable simulations, with kernel, integrator, reaction-handler, and observable interfaces.
- **C3:** The same guide explains the cell-linked neighbor search and the tradeoff between smaller cells, fewer candidate pairs, and greater bookkeeping, alongside single-threaded and parallel CPU kernels.

**Entry point:** The linked simulation guide, especially kernel configuration and reaction handling. The statistical statement concerns ordering within a timestep, not exactness of the complete discretized Brownian simulation.

## Differentiable and language-native simulation libraries

### 15. [jax-md/jax-md](https://github.com/jax-md/jax-md)

**Language / role:** Python/JAX; differentiable molecular dynamics compiled through XLA for different devices.

Study how scientific simulation changes when compilation requires fixed array shapes and simulation states are transformed functionally.

- **C1:** [`jax_md/partition.py`](https://github.com/jax-md/jax-md/blob/main/jax_md/partition.py) explicitly represents cell-list overflow. A compiled update cannot silently resize a list; substantial changes in occupancy can exceed the capacity estimated at allocation.
- **C2:** `CellList` and `CellListFns` separate data and operations, including named side buffers, spatial identifiers, and allocation/update functions. These are reusable partitioning primitives beneath interaction calculations.
- **C3:** Allocation occurs outside JIT compilation, while fixed-capacity updates remain JIT-compatible. The code documents the reason for this split and offers capacity multipliers instead of pretending dynamic storage is free under XLA.

**Entry point:** `partition.py`, especially `CellList`, `cell_list`, and neighbor-list construction. The repository describes itself as research software with possible API changes.

### 16. [JuliaMolSim/Molly.jl](https://github.com/JuliaMolSim/Molly.jl)

**Language / role:** Julia; extensible MD, CPU/GPU simulation, and differentiable trajectories.

Study a language-native design that exposes customization through Julia types and dispatch while documenting the numerical conditions those extensions must preserve.

- **C1:** The [developer guide](https://github.com/JuliaMolSim/Molly.jl/blob/master/docs/src/developer.md) explains minimum-image cutoff limits, molecules split across periodic boundaries, and why coordinate scaling must first make molecules whole. It also distinguishes precision modes and identifies GPU tests that ordinary CI does not execute.
- **C2:** The same guide specifies a custom neighbor-finder interface, including eligibility, special interactions, update cadence, and sparse pair metadata.
- **C2/C1:** The [differentiable-simulation guide](https://github.com/JuliaMolSim/Molly.jl/blob/master/docs/src/differentiable.md) reuses simulation abstractions for Enzyme differentiation, but documents unsupported combinations involving constraints, virtual sites, GPU pressure/virial paths, and memory use.

**Entry points:** Those two developer-facing guides. Differentiability should not be assumed for every combination of features.

### 17. [lumol-org/lumol](https://github.com/lumol-org/lumol)

**Language / role:** Rust; classical molecular simulation, MD, Monte Carlo, and minimization. **Archived repository:** retain as a historical engineering study, not as a currently maintained deployment recommendation. Its README's older active-development wording is superseded by GitHub's archived status.

Study trait-based energy models and a substantial electrostatics implementation in a language less common in this ecosystem.

- **C2:** [`energy/functions.rs`](https://github.com/lumol-org/lumol/blob/master/lumol-core/src/energy/functions.rs) implements reusable potential types through `Potential` and interaction-specific traits, separating energy/force evaluation from how simulations use the interaction.
- **C1:** [`energy/global/ewald.rs`](https://github.com/lumol-org/lumol/blob/master/lumol-core/src/energy/global/ewald.rs) separates real-space, reciprocal-space, and self-energy terms. Embedded tests check forces by finite differences, virials, cell geometries, invalid parameters, and molecule-move energy changes.
- **C3:** Ewald factors are cached according to the cell, and the implementation includes parallel execution and synchronized shared state rather than only a didactic pair loop.

**Entry points:** The potential implementations and Ewald source/tests above.

## Granular and discrete-element particles

### 18. [CFDEMproject/LIGGGHTS-PUBLIC](https://github.com/CFDEMproject/LIGGGHTS-PUBLIC)

**Language / role:** C++; discrete-element granular simulation. **Legacy lineage:** the official repository identifies commercial Aspherix as its successor. LIGGGHTS derives from LAMMPS, but its separately evolved granular contact machinery makes it a substantive distinct study rather than a duplicate fork.

Study history-dependent contact laws and the conditions under which timestep and neighbor choices miss physical interactions.

- **C2:** The [`pair_style gran` specification](https://github.com/CFDEMproject/LIGGGHTS-PUBLIC/blob/master/doc/pair_gran.txt) composes normal, tangential, cohesion, rolling-friction, and surface models. Tangential displacement is accumulated over a contact's lifetime, rather than computed solely from current separation.
- **C1:** [`fix check/timestep/gran`](https://github.com/CFDEMproject/LIGGGHTS-PUBLIC/blob/master/doc/fix_check_timestep_gran.txt) checks Rayleigh/Hertz timescale estimates and whether particles can traverse the neighbor skin in one step. The contact documentation also exposes ghost-velocity requirements and the need to restore material properties separately from restart state.

**Entry points:** The contact-model and timestep-check documents. The repository's successor notice should guide interpretation of its maintenance status.

### 19. [woodem/woo](https://github.com/woodem/woo)

**Language / role:** C++/OpenMP with Python scripting; extensible granular-material and discrete-element mechanics.

Study multi-dispatch for contact geometry and material laws together with parallel contact lifecycle management.

- **C2:** [`ContactLoop.hpp`](https://github.com/woodem/woo/blob/master/src/dem/ContactLoop.hpp) separates shape-pair geometry, material-pair physics, and constitutive-law dispatch. New combinations can be expressed as functors rather than a single expanding collision switch.
- **C1:** The contact loop defers deletion through per-thread removal lists and checks for invalid contact-container state before traversal. Periodic image shifts and shape-order swaps are explicit in [`ContactLoop.cpp`](https://github.com/woodem/woo/blob/master/src/dem/ContactLoop.cpp).
- **C3:** The implementation uses guided OpenMP traversal and periodically reorders contacts to reduce imbalance between active and inactive work. The code presents reordering as a practical optimization, not a universal speedup claim.

**Entry points:** The contact-loop header and implementation.

## Smoothed particle hydrodynamics and coupled fluids

### 20. [pypr/pysph](https://github.com/pypr/pysph)

**Language / role:** Python, generated Cython/OpenCL, and parallel execution support; a framework for SPH and related particle methods.

Study a simulation-specific programming model that turns user-defined equations into compiled neighbor loops.

- **C2:** The [framework design](https://github.com/pypr/pysph/blob/main/docs/source/design/overview.rst) separates particle arrays, nearest-neighbor search, equations, equation groups, and integration stages. Source and destination arrays express interactions between fluids and boundaries without duplicating the engine.
- **C1:** Equation groups preserve dependencies such as computing pressure before acceleration. The guide explains the distinction between local and remote particles and why reductions require separate treatment from independent destination-particle updates.
- **C3:** Python equations generate compiled code; typed temporaries and reduction helpers make execution costs visible. The [equation-writing guide](https://github.com/pypr/pysph/blob/main/docs/source/design/equations.rst) develops this extensibility contract further.

**Entry points:** The design overview and equation guide. Users still bear responsibility for ordering equations correctly.

### 21. [DualSPHysics/DualSPHysics](https://github.com/DualSPHysics/DualSPHysics)

**Language / role:** C++/CUDA/OpenMP; SPH for free-surface and engineering flows. This selection focuses on the `src/source` solver; the repository also includes a multiphase source subtree.

Study GPU neighbor construction in a solver with moving boundaries, periodic particles, and excluded/out-of-domain particles.

- **C3:** [`JCellDivGpuSingle.cpp`](https://github.com/DualSPHysics/DualSPHysics/blob/master/src/source/JCellDivGpuSingle.cpp) calculates an active cell domain, checks storage capacity, sorts particles by cell, and constructs begin/end ranges. It can reuse boundary partitioning and reorder only the fluid portion when its validity conditions hold.
- **C1:** Moving boundaries or periodic conditions invalidate cached bounds. The code separately tracks excluded boundary/fluid particles, handles empty domains, and checks excessive cell counts and CUDA errors rather than treating sorting as a context-free operation.

**Entry points:** The cell-division implementation and [`JSphGpuSingle.h`](https://github.com/DualSPHysics/DualSPHysics/blob/master/src/source/JSphGpuSingle.h) for its solver-level context. The README distinguishes the solver source from the broader preprocessing/postprocessing distribution.

### 22. [InteractiveComputerGraphics/SPlisHSPlasH](https://github.com/InteractiveComputerGraphics/SPlisHSPlasH)

**Language / role:** C++ with Python bindings; particle-based fluid simulation with multiple incompressibility, viscosity, and boundary methods.

Study how competing published SPH methods fit behind a common application architecture.

- **C2:** The [architecture document](https://github.com/InteractiveComputerGraphics/SPlisHSPlasH/blob/master/doc/architecture.md) separates `Simulation`, `TimeStep`, `FluidModel`, and `BoundaryModel`. A pressure solver is selected through the timestep interface, while fluid phases independently select non-pressure effects and boundary objects select coupling methods.
- **C1:** CFL-based timestep updates and rigid-fluid boundary treatment are explicit shared responsibilities. The design also documents restrictive invariants: one simulation singleton and at most one implementation of each non-pressure effect per fluid model.
- **C3:** Neighborhood search is behind a dedicated interface, allowing different search implementations without embedding them into each pressure solver. The [changelog](https://github.com/InteractiveComputerGraphics/SPlisHSPlasH/blob/master/Changelog.txt) records SIMD/search changes and scene-format migration requirements.

**Entry points:** Architecture and changelog. The singleton constraint matters when evaluating embedding or concurrent independent simulations.

### 23. [Xiangyu-Hu/SPHinXsys](https://github.com/Xiangyu-Hu/SPHinXsys)

**Language / role:** C++ with heterogeneous-computing support; SPH multiphysics, fluid–structure interaction, and coupled solid dynamics.

Study a simulation library where physical bodies, their interaction topology, and their time evolution are assembled separately by application code.

- **C2:** The [architecture overview](https://github.com/Xiangyu-Hu/SPHinXsys/blob/master/tutorials/sphinx/SPHinXsysArch.rst) separates `SPHBody` spatial/topological structure from `ParticleDynamics` operations. It describes staged construction of bodies, interactions, coupled Simbody objects, and output.
- **C1:** Fluid–structure coupling uses nested integration levels: solid evolution, fluid acoustic relaxation, and fluid viscous updates. Force transfer and imposed constraints must occur at the appropriate level, making scheduling part of numerical correctness.
- **C3:** Those distinct timestep levels avoid advancing every physical process at the smallest timescale. The [numerical schemes](https://github.com/Xiangyu-Hu/SPHinXsys/blob/master/tutorials/sphinx/theory.rst) provide the corresponding mathematical context.

**Entry points:** Architecture overview and theory chapter. The tutorial vocabulary describes the documented conceptual design; implementation details vary across backends and versions.

## Gravitational and plasma particle engines

### 24. [hannorein/rebound](https://github.com/hannorein/rebound)

**Language / role:** C with Python bindings; gravitational N-body dynamics, orbital integration, and collisional particles.

Study numerical integration as a first-class, interchangeable subsystem, especially when close encounters and long-time orbital accuracy impose different requirements.

- **C1:** [`integrator_ias15.c`](https://github.com/hannorein/rebound/blob/main/src/integrator_ias15.c) implements adaptive high-order integration and documents the consequences of minimum timestep and error-control choices. It distinguishes global and individual acceleration-error criteria and records the change in default criterion in 2024.
- **C2:** Integrator registration collects creation, stepping, cleanup, state-field descriptors, and documentation in one interface. The [changelog](https://github.com/hannorein/rebound/blob/main/changelog.md) explains the move from global variables to per-simulation state and later changes that make custom integrators and Python bindings easier to maintain.

**Entry points:** IAS15's implementation and the architectural migration notes in the changelog. Different integrators have different conservation and encounter-handling properties; this entry is not a blanket accuracy ranking.

### 25. [SmileiPIC/Smilei](https://github.com/SmileiPIC/Smilei)

**Language / role:** C++ with Python configuration; kinetic plasma simulation using particle-in-cell methods.

Study how field/particle numerical consistency interacts with dynamic parallel decomposition when particle density is highly nonuniform.

- **C1:** The [algorithm description](https://github.com/SmileiPIC/Smilei/blob/master/doc/Sphinx/Understand/algorithms.rst) explains charge-conserving current deposition using Esirkepov's method. Contributions along resolved grid directions derive from charge flux across cell boundaries rather than an arbitrary projection.
- **C3:** The [parallelization design](https://github.com/SmileiPIC/Smilei/blob/master/doc/Sphinx/Understand/parallelization.rst) decomposes space into many small patches. OpenMP schedules patches locally; MPI load balancing moves contiguous portions of a Hilbert-ordered patch sequence between processes.
- **C2:** Patches provide a common unit of storage, scheduling, and migration, with documented tradeoffs between cache use, imbalance, and synchronization. Alternative rectangular arrangements have different restrictions and disable this load-balancing mechanism.

**Entry points:** The algorithms and parallelization chapters.

### 26. [BLAST-WarpX/warpx](https://github.com/BLAST-WarpX/warpx)

**Language / role:** C++ with Python interfaces and AMReX-based CPU/GPU execution; electromagnetic and electrostatic PIC.

Study the particle subsystem and its interaction with mesh refinement, rather than treating WarpX as only a field solver.

- **C2/C3:** The [particle developer guide](https://github.com/BLAST-WarpX/warpx/blob/development/Docs/source/developers/particles.rst) describes per-box/per-tile containers, physical/photon/laser species, structure-of-arrays attributes, and portable inner loops. It explicitly distinguishes independent operations from scatter-add deposition into shared grid cells.
- **C1:** The [mesh-refinement theory](https://github.com/BLAST-WarpX/warpx/blob/development/Docs/source/theory/amr.rst) identifies spurious particle self-forces, electromagnetic reflections, and possible Gauss-law violations at refinement interfaces. Buffer regions and coarse/fine gather/deposition choices are numerical safeguards, not merely data-transfer optimizations.

**Entry points:** The particle implementation guide and refinement chapter. The repository is counted once; AMReX is an underlying dependency, not a second selected engine.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations, followed by repository/API verification and direct reading of documentation or source. Search angles included general MD architecture; soft-matter and adaptive-resolution engines; GPU materials and polarizable force fields; Julia/Rust/JAX differentiable simulation; event-driven collision scheduling; granular DEM; SPH fluids and multiphysics; gravitational N-body and plasma PIC; and particle reaction–diffusion. Additional searches targeted neighbor-list implementations, testing, and smaller projects beyond the familiar engine names. Later queries increasingly returned implementations in already represented families, experimental visual simulators, wrappers, or supporting libraries; the selection was expanded for ReaDDy's distinct reaction-conflict semantics rather than for repository count alone.

Canonical identities, default branches, and archive status were checked where applicable. **GROMACS and DL_POLY are explicitly retained as official substantive GitHub mirrors. Lumol is archived. LIGGGHTS-PUBLIC is a separately evolved LAMMPS-derived legacy engine with an announced successor.** ESPResSo and ESPResSo++ explicitly describe their independent development. No maintenance claim is inferred merely from a recent push or an old creation date.

Important exclusions are analysis/viewer projects such as oxView, generated distribution wrappers, tutorials and minimal demos, potential-training libraries without an engine, and general rigid-body/game engines. Searches also surfaced substantial supporting libraries such as [AutoPas](https://github.com/AutoPas/AutoPas) and [OpenFPM](https://github.com/mosaic-group/openfpm); they were not added because this report prioritizes integrated physical evolution and engine-level numerical semantics over particle infrastructure alone. Additional engines exist in each family, and the list is a selection guide rather than an exhaustive census.

This was read-only research: repositories were not cloned, built, benchmarked, or executed. Source-level observations establish what is implemented or documented, not that every numerical path has been independently validated. C1–C4 assignments and suggestions about what engineers can learn are grounded interpretations of the linked primary material. Performance discussion deliberately focuses on mechanisms and tradeoffs, without transferring published speedup figures to untested hardware or workloads.
