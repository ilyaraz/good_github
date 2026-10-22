# Computational fluid dynamics frameworks

Research date: **2026-10-09**

This report selects **25 GitHub repositories** implementing reusable CFD solvers, numerical frameworks, or substantial CFD kernel-generation infrastructure. It spans industrial finite-volume systems, finite elements, spectral and discontinuous methods, structured turbulence solvers, adaptive meshes, lattice Boltzmann methods, particle methods, and differentiable simulation. General numerical infrastructure is included only through a concrete fluid-simulation implementation. The entries are engineering study recommendations grounded in primary material, not a ranking or a claim that every component is uniformly exemplary.

Criteria used below:

- **C1 — Correctness:** difficult numerical semantics, invariants, concurrency, or failure handling.
- **C2 — Abstractions:** substantial reusable structure supporting different models, discretizations, or applications.
- **C3 — Performance:** concrete computational constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by evidence of compatibility work, testing, or complexity management.

Every repository heading links to an opened GitHub repository page. The documentation and source links within each entry are additional primary entry points that were opened and read. Statements about what engineers can learn are grounded interpretations of those sources; performance mechanisms are distinguished from independently measured results.

## General-purpose and unstructured CFD

### 1. [OpenFOAM/OpenFOAM-dev](https://github.com/OpenFOAM/OpenFOAM-dev)

**Language/role:** C++; OpenFOAM Foundation development repository for a broad finite-volume CFD system. This identifies the Foundation lineage specifically, rather than conflating different OpenFOAM distributions.

Study how an equation-facing C++ interface retains the information needed by sparse linear algebra and boundary handling. The implementation of `fvMatrix` associates a field with dimensional information, internal and boundary coefficients, and face-flux corrections.

- **C2:** The templated matrix abstraction joins field operations, equation assembly, and solver interfaces, allowing different transported quantities to share the same numerical machinery.
- **C3:** The source explains face-oriented addressing for vectorized assembly and solution. Its nested solver object also permits reuse of an expensive solver setup, specifically including AMG reuse during PISO iterations.

Start with the substantive [`fvMatrix.H` source](https://cpp.openfoam.org/dev/fvMatrix_8H_source.html), then use the [generated source guide](https://cpp.openfoam.org/dev/) to follow the surrounding finite-volume classes.

### 2. [su2code/SU2](https://github.com/su2code/SU2)

**Language/role:** C++ with Python tooling; multiphysics simulation and design software. The relevant subsystem is **SU2_CFD**, counted once within the repository.

The useful architectural lesson is the separation between simulation orchestration and local numerical operations. Drivers coordinate iterations and integrations, while geometry, solver, and numerics objects serve distinct roles.

- **C2:** `CGeometry` represents the mesh, solver classes hold equation state and boundary behavior, and `CNumerics` implements local residual and Jacobian contributions. This supports multiple equations and primal/adjoint workflows without putting every concern into a single solver class.
- **C3:** The design exposes edge-based dual-mesh finite-volume operations and agglomerated multigrid levels. Engineers can trace how geometry organization supports repeated residual evaluation and convergence acceleration.

The [version-7 code-structure guide](https://su2code.github.io/docs_v7/Code-Structure/) is the main entry point. It explicitly cautions that some diagrams may lag implementation, so use it as an architectural map rather than an exact current class inventory.

### 3. [code-saturne/code_saturne](https://github.com/code-saturne/code_saturne)

**Language/role:** C/C++, Fortran, and Python; general-purpose finite-volume CFD. The repository identifies itself as a **public mirror** of Code_Saturne development.

Study incremental accelerator adoption in an existing numerical system. Its developer material discusses both the interfaces and the limitations of moving mesh-based computations between CPU and device memory.

- **C2:** Allocation modes and a common parallel-loop interface separate numerical operations from host/device execution policy. This is reusable infrastructure for multiple operators rather than a standalone accelerated demo.
- **C3:** The documentation identifies sparse linear solves and gradient calculations as accelerator targets, discusses memory-bound behavior and managed-memory migration, and describes CPU OpenMP, CUDA, and SYCL paths with differing maturity.

The [9.1 developer guide on node-level parallelism](https://code-saturne.org/doc/code_saturne-9.1/cs_dg_node_level_parallelism.html) is the substantive entry point. Its discussion of `CS_MALLOC_HD` and lambda-based loops makes the performance-portability tradeoffs inspectable; backend availability should be checked against the version being built.

### 4. [kynema/kynema-ugf](https://github.com/kynema/kynema-ugf)

**Language/role:** C++; unstructured low-Mach CFD for wind-energy and related applications. This is the canonical destination of the former **Exawind/nalu-wind** repository; its README records the 2026 rename.

Study a mesh-centric framework built around STK abstractions. `Realm` organizes a physics domain; equation systems register and assemble individual PDEs; fields and algorithms operate on selected mesh entities.

- **C2:** Parts, selectors, buckets, field states, realms, and equation systems provide explicit extension boundaries. The design guide explains how pressure projection and other equation systems fit that structure, including registration-order dependencies.
- **C3:** Bucket-level iteration and entity selection expose the grouping of mesh work and locally owned data needed for parallel execution, rather than hiding distribution beneath an opaque solver call.

Start with [code abstractions](https://kynema.github.io/kynema-ugf/source/theory/codeAbstractions.html). The repository README additionally documents CPU/MPI/GPU testing and its development lineage. This entry and Kynema-SGF below cover different unstructured and structured implementations, not duplicate listings of the rename.

### 5. [chaos-polymtl/lethe](https://github.com/chaos-polymtl/lethe)

**Language/role:** C++; deal.II-based finite-element CFD, particle simulation, and coupled multiphysics.

Lethe is particularly useful for studying the operational contracts around nonlinear solves: when to rebuild expensive objects, how to accept updates, and what should happen when convergence fails.

- **C1:** Its solver controls specify residual-based step acceptance and the relationship between linear and nonlinear tolerances. The documented failure-on-nonconvergence option makes unsuccessful time steps an explicit policy rather than an implicit numerical outcome.
- **C3:** Newton and inexact-Newton variants expose Jacobian reassembly thresholds, reuse across time steps, and preconditioner reuse. These are concrete tradeoffs between work per iteration and convergence reliability.

The [nonlinear solver control guide](https://chaos-polymtl.github.io/lethe/documentation/parameters/cfd/non-linear_solver_control.html) connects parameters to algorithmic behavior. Combined with the repository's deal.II/Trilinos/p4est-based implementation, it is a good starting point for understanding nonlinear CFD beyond the discretization formula alone.

## High-order, spectral, and discontinuous methods

### 6. [PyFR/PyFR](https://github.com/PyFR/PyFR)

**Language/role:** Python with generated platform-specific kernels; high-order flux-reconstruction CFD on unstructured meshes.

Study how a high-level language can orchestrate a solver while numerical work runs in generated kernels. PyFR's architecture makes time integration, spatial discretization, and execution backends separately visible.

- **C2:** An integrator combines a controller and stepper; a system owns elements, interfaces, and a backend. Controllers decide acceptance and time-step changes, while steppers perform individual updates.
- **C3:** Systems generate their required kernels and invoke them through queues/graphs. Pointwise kernel providers render PyFR-Mako specifications into backend-specific source, which is compiled and loaded; backend interfaces also manage matrices and exchange buffers.

The [developer guide](https://pyfr.readthedocs.io/en/latest/developer_guide.html), especially its Integrator, System, Backend, and Kernel Generator sections, provides both the architectural map and the implementation-level entry points. This is substantial code-generation infrastructure serving CFD, not merely a Python wrapper around a fixed solver.

### 7. [Nek5000/nekRS](https://github.com/Nek5000/nekRS)

**Language/role:** C++ and OCCA kernels; accelerated spectral-element incompressible and low-Mach flow solver.

Study the interaction between high-order numerical structure and accelerator-friendly operator evaluation. The project has its own substantial solver implementation despite its documented Nek5000/libParanumal ancestry.

- **C1:** The theory distinguishes variable-viscosity full-stress formulations from simplified alternatives and explains low-Mach pressure splitting, including the mass constraint in a closed system. These distinctions affect which equations are actually solved.
- **C3:** Tensor-product spectral elements enable sum-factorized operations rather than dense multidimensional operator application. The theory discusses storage/work reduction and local ordering; the repository supplies the OCCA-based execution layer.

Begin with the [theory documentation](https://nekrs.readthedocs.io/en/latest/theory.html), particularly spatial discretization and the incompressible/low-Mach equations. It is a useful route from mathematical operators to the memory and execution structure of a high-order implementation.

### 8. [ExtremeFLOW/neko](https://github.com/ExtremeFLOW/neko)

**Language/role:** Modern Fortran with C and device kernels; portable high-order spectral-element flow framework. It shares numerical heritage with Nek5000 but implements a distinct object-oriented solver stack.

- **C2:** Mesh, function-space, degree-of-freedom, geometric-coefficient, field, and gather/scatter types are separate from fluid/scalar schemes and linear solvers. The [important-types guide](https://neko.cfd/docs/develop/d3/d40/important_types.html) also identifies registries and reusable scratch storage.
- **C3:** The [implementation guide](https://neko.cfd/docs/develop/d1/d5a/contributing.html) traces Fortran numerical types through device-dispatch wrappers, C bindings, and CUDA/HIP/OpenCL kernels. For more complex operators, a factory selects a backend-specific derived type once, avoiding repeated backend-selection conditionals in subsequent calls.

This is a strong study choice for engineers interested in performance-oriented Fortran architecture. The guide acknowledges that backend organization is not completely uniform across the codebase, which makes it useful evidence of real implementation tradeoffs rather than an idealized diagram.

### 9. [flexi-framework/flexi](https://github.com/flexi-framework/flexi)

**Language/role:** Fortran; high-order discontinuous-Galerkin spectral-element CFD with finite-volume shock capturing.

Study the boundary between a high-order method's desirable smooth-flow behavior and the safeguards needed at discontinuities.

- **C1:** The Sod tutorial explains why a modal shock indicator can miss a discontinuity exactly on an element boundary, why initial finite-volume treatment may be necessary, and how separate switching thresholds prevent repeated DG/FV oscillation. It also discusses reconstruction limiting.
- **C2:** Element-local DG and subcell finite-volume representations participate in the same solver. The indicator, switching rules, and reconstruction choices are configurable numerical components rather than a single hard-coded shock-tube implementation.

The [Sod shock-tube implementation tutorial](https://numericsresearchgroup.org/userguide/html/04_tutorials/06_sod/index.html) is the substantive entry point. Read it as a worked explanation of reusable shock-capturing machinery within the broader FLEXI framework, with its limitations made explicit.

### 10. [trixi-framework/Trixi.jl](https://github.com/trixi-framework/Trixi.jl)

**Language/role:** Julia; high-order conservation-law framework, including compressible Euler and Navier–Stokes simulations.

- **C2:** A semidiscretization combines mesh, equations, spatial solver, initial/boundary data, source terms, and caches, then exposes an ODE problem to time integrators. The [architecture overview](https://trixi-framework.org/TrixiDocumentation/stable/overview/) explains the multiple-dispatch composition and cautions that not every combination is implemented.
- **C1:** The [subcell invariant-domain-preserving limiter tutorial](https://trixi-framework.org/TrixiDocumentation/stable/tutorials/subcell_shock_capturing/) shows how density bounds and nonlinear quantities such as pressure are constrained. Its correction callback must execute after each Runge–Kutta stage; choosing a spatial limiter alone is insufficient.

Engineers can study both flexible numerical composition and an important cross-layer contract: a spatial method's admissibility property depends on the time integrator invoking the required correction at the right stage. The selected subsystem is fluid conservation laws, not every PDE supported by Trixi.

## Structured-grid turbulence and multiphase solvers

### 11. [xcompact3d/Incompact3d](https://github.com/xcompact3d/Incompact3d)

**Language/role:** Fortran; Xcompact3d's compact finite-difference framework for incompressible turbulence. This is the combined framework repository, not the separately archived older Incompact3d code.

- **C1:** The [source-file guide](https://xcompact3d.readthedocs.io/en/latest/pages/user_guide/list_files.html) explains why intermediate-velocity boundary conditions must be applied before pressure correction to preserve the divergence constraint. It also describes staggered-pressure Poisson treatment and modified wave numbers compatible with the discrete operators.
- **C2:** Common Navier–Stokes and pressure routines are separated from case-specific initialization, boundaries, and forcing. The documented case dispatch and `BC_XXX` organization show how multiple flow configurations reuse the numerical core.

This is a useful codebase for tracing the consistency of the entire projection algorithm, not just a finite-difference stencil. The guide also records limitations of particular LES boundary combinations and force routines; support should therefore be assessed at the component and case level.

### 12. [CaNS-World/CaNS](https://github.com/CaNS-World/CaNS)

**Language/role:** Fortran; canonical incompressible-flow DNS solver with CPU and GPU configurations.

The repository README gives a substantive account of its staggered-grid pressure-correction algorithm, time integration, and direct pressure/Helmholtz solvers. It is comparatively focused and suitable for following a complete numerical path.

- **C1:** Boundary conditions determine the Fourier, sine, or cosine transforms used in the separable solve. The remaining direction can use a nonuniform grid and direct elimination, making operator/boundary compatibility an explicit numerical concern.
- **C3:** Pencil decomposition, MPI communication, CPU threading, and accelerator execution are exposed through selectable build paths. The [compilation guide](https://github.com/CaNS-World/CaNS/blob/main/docs/INFO_COMPILING.md) distinguishes the relevant decomposition and GPU communication options.

Start with the algorithm description in the linked repository and that compilation guide. The latter identifies an OpenMP-offload development branch separately; it should not be confused with the default OpenACC GPU configuration.

### 13. [MFlowCode/MFC](https://github.com/MFlowCode/MFC)

**Language/role:** Fortran/Fypp with Python tooling; compressible multiphase flow framework supporting multiple mixture-model formulations.

- **C2:** The [GPU programming guide](https://mflowcode.github.io/documentation/gpuParallelization.html) documents a Fypp macro layer for parallel loops, reductions, data regions, and device routines. The shared interface separates much numerical Fortran from backend directives while making data-lifetime semantics explicit.
- **C3:** [Case optimization](https://mflowcode.github.io/documentation/expectedPerformance.html) generates and caches binaries with simulation parameters fixed at compile time, enabling constant propagation, dead-code removal, and loop specialization. The documentation also explains the rebuild cost that makes this less attractive for frequently changing configurations.

Study specialization as an architectural choice, together with explicit device residency and reduction contracts. The GPU guide contains both implemented and evolving backend descriptions; it should not be read as a promise that every directive backend has identical support. No published speedup number is needed to justify this entry.

## Adaptive meshes, embedded boundaries, and coupled flow

### 14. [AMReX-Fluids/IAMR](https://github.com/AMReX-Fluids/IAMR)

**Language/role:** C++; block-structured adaptive-mesh, variable-density incompressible Navier–Stokes solver.

- **C1:** The [software guide](https://amrex-fluids.github.io/IAMR/docs_html/Software.html) describes ghost filling across both level and time boundaries. Coarse data must bracket requested interpolation times; conservative cell interpolation preserves coarse/fine averages. These are concrete correctness obligations under adaptive time stepping.
- **C2:** AMReX `StateData`, descriptors, interpolators, and level-oriented solver organization separate state registration and transfer policy from the physics update. The guide points into setup and evolution routines so readers can follow those responsibilities.

IAMR is a useful study of how a fluid solver uses a reusable AMR runtime while still owning numerical choices about state, projection, and interpolation. This entry counts IAMR, not AMReX itself, and does not treat the underlying mesh library as an independent CFD framework in this report.

### 15. [Pele-Suite/PeleC](https://github.com/Pele-Suite/PeleC)

**Language/role:** C++ with generated chemistry infrastructure; AMReX-based compressible reacting-flow solver. This is the canonical destination of **AMReX-Combustion/PeleC**.

- **C1:** The [embedded-boundary design notes](https://pele-suite.github.io/PeleC/geometry/EB.html) explain small-cut-cell instability and state redistribution. They also document how independently limited reconstructions can produce inconsistent thermodynamic states, and why zero slopes are a safer default in that treatment.
- **C2:** Geometry supplied by AMReX is connected to PeleC reconstruction, redistribution, chemistry, and AMR flux-register accounting. The notes expose the interfaces and bookkeeping needed to combine these mechanisms rather than treating embedded boundaries as a mesh-only feature.

Study conservation across irregular cells and refinement levels, including the consequences of clipping species fractions and reconstructing energy. The documentation is unusually useful because it discusses accuracy/robustness compromises and the need to account for redistributed contributions crossing coarse/fine boundaries.

### 16. [kynema/kynema-sgf](https://github.com/kynema/kynema-sgf)

**Language/role:** C++; AMReX-based structured-grid wind-energy CFD. The former **Exawind/amr-wind** GitHub URL redirects here.

- **C1:** The [discretization theory](https://kynema.github.io/kynema-sgf/theory/theory.html) traces predicted face velocities through MAC projection and subsequent momentum updates. Its multiphase treatment connects volume-fraction transport with mass-consistent momentum fluxes, making consistency between coupled updates an explicit concern.
- **C2:** Atmospheric-flow physics, turbine representations, transported quantities, and multiphase treatments are assembled on a shared structured-grid solver infrastructure. The documented update ordering gives engineers a concrete way to understand how additional physics interacts with projection.

Use the theory page as the main entry point and the repository overview to identify the supported application components. Kynema-SGF and Kynema-UGF have different mesh and discretization architectures despite their shared application community. The inspected multiphase theory also states limitations, including the absence of surface tension in the described formulation.

### 17. [IBAMR/IBAMR](https://github.com/IBAMR/IBAMR)

**Language/role:** C++ and Fortran; adaptive immersed-boundary and fluid–structure interaction framework.

- **C2:** [`IBHierarchyIntegrator`](https://ibamr.github.io/IBAMR-docs/ibamr/classIBAMR_1_1IBHierarchyIntegrator.html) composes an immersed-boundary strategy with an incompressible-flow hierarchy integrator. State contexts, force/source registration, and hierarchy callbacks provide extension points for different coupled models.
- **C1:** [`IBStrategy`](https://ibamr.github.io/IBAMR-docs/ibamr/classIBAMR_1_1IBStrategy.html) documents interpolation/spreading kernels and time-specific Eulerian–Lagrangian transfer. It explicitly distinguishes regridding from rebuilding structure-to-patch associations: the displacement reference for one is not necessarily the reference for the other.

That distinction makes IBAMR especially valuable for studying moving-structure correctness on adaptive meshes. The strategy interface supports different immersed-boundary formulations while exposing the lifecycle operations needed to keep mesh associations and coupling operators valid.

## Lattice-Boltzmann frameworks and numerical code generation

### 18. [lssfau/walberla](https://github.com/lssfau/walberla)

**Language/role:** C++ and Python; distributed block-structured multiphysics framework, particularly lattice-Boltzmann CFD and fluid–particle coupling. This GitHub repository is an **official mirror** of development hosted at FAU GitLab.

- **C2:** The [sweeps tutorial](https://www.walberla.net/doxygen/tutorial_basics_02.html) separates block storage, typed field retrieval, per-block numerical sweeps, and time-loop orchestration. A sweep works on its supplied block instead of embedding process-wide traversal into the algorithm.
- **C3:** That separation allows local block execution and distributed ownership to coexist; timing and scheduling are explicit framework concerns rather than additions to individual numerical kernels.
- **C4:** The [2019–2026 changelog](https://github.com/lssfau/walberla/blob/master/CHANGELOG.md) records language-standard transitions, API/dependency changes, tests for fluid–particle and free-surface features, a CI overhaul, and fixes to sparse-stencil communication and GPU object copying.

Study both the numerical execution model and how a large research framework retires interfaces, introduces generated kernels, and manages changing accelerator support.

### 19. [lssfau/lbmpy](https://github.com/lssfau/lbmpy)

**Language/role:** Python/SymPy with generated C/CUDA kernels; a lattice-Boltzmann method construction and optimization framework. This is the current **official GitHub mirror** of FAU-hosted development; the former `mabau/lbmpy` repository is archived and is not a second entry.

- **C2:** The [`creationfunctions.py` implementation](https://raw.githubusercontent.com/lssfau/lbmpy/master/src/lbmpy/creationfunctions.py) lays out a staged pipeline: numerical method, collision/update rule, kernel syntax tree, and compiled function. Users can intervene at intermediate representations instead of accepting a single opaque generator.
- **C3:** LBM-specific assignment simplifications are separated from hardware-level syntax-tree transformations. Configuration distinguishes collision-space choices from common-subexpression elimination, loop transformations, and CPU/GPU targets.

This is substantive numerical infrastructure rather than a generated wrapper: the code constructs moment/cumulant collision rules and their streaming updates. It complements waLBerla but is independently reusable, so the two entries cover distinct implementations and responsibilities.

## Particle methods and free-surface simulation

### 20. [pypr/pysph](https://github.com/pypr/pysph)

**Language/role:** Python with generated compiled kernels; reusable smoothed-particle hydrodynamics framework.

- **C2:** The [equation-design guide](https://pysph.readthedocs.io/en/main/design/equations.html) separates per-particle initialization, neighbor-pair loops, and post-loop work. Equation groups coordinate ordered phases and shared evaluation, allowing different SPH schemes to reuse the execution machinery.
- **C1:** Equation instances may be shared across execution threads, so storing particle-dependent temporary state on an equation object is unsafe. The guide explains using particle properties instead, and distinguishes real destination particles from source particles that may include remote or ghost data.

Study the contract between a convenient Python numerical API and generated parallel neighbor loops. The concurrency and particle-ownership rules are as important as the SPH formulas: a method that looks locally correct can be invalid when its equation object is reused across particles or threads.

### 21. [Xiangyu-Hu/SPHinXsys](https://github.com/Xiangyu-Hu/SPHinXsys)

**Language/role:** C++ with Python tooling; particle-based multiphysics, including fluid dynamics and fluid–structure interaction.

- **C2:** The [architecture guide](https://www.sphinxsys.org/html/SPHinXsysArch.html) separates `SPHBody` topology and state from `ParticleDynamics` operations. Real bodies, observer bodies, interactions, and external multibody coupling occupy distinct roles.
- **C1:** The documented coupled algorithm nests several time scales: solid updates inside fluid acoustic updates, with larger outer steps for slower dynamics. Construction order and coupling order are therefore part of the simulation's correctness contract.

This is a useful framework for studying reusable particle interactions across fluids and solids rather than a solver for one free-surface example. Follow the architecture's body/interaction/dynamics split and its time-stepping diagram to see how common particle infrastructure supports different physical update rules.

### 22. [DualSPHysics/DualSPHysics](https://github.com/DualSPHysics/DualSPHysics)

**Language/role:** C++ and CUDA; SPH simulation system for free-surface flow and interactions with structures, with CPU and GPU execution paths.

Study the less glamorous infrastructure that makes a large particle simulation practical: managing spatial-cell and particle buffers as the occupied domain changes.

- **C1:** [`JCellDivGpu.cpp`](https://github.com/DualSPHysics/DualSPHysics/blob/master/src/source/JCellDivGpu.cpp) checks cell-count conversions and upper bounds before allocation, detects CUDA allocation failures, and resets validity flags when dependent buffers are freed. These are concrete large-problem failure modes.
- **C3:** The same implementation separately tracks particle and cell capacities, reserves headroom, and reallocates when capacity is insufficient. This makes memory usage and repeated-allocation costs explicit within the GPU cell-division component.

The repository overview establishes the SPH/free-surface scope; the source file provides a focused implementation entry point. This entry's performance justification is buffer-management architecture, not an unverified GPU speedup claim.

## Compact, geophysical, and differentiable frameworks

### 23. [WaterLily-jl/WaterLily.jl](https://github.com/WaterLily-jl/WaterLily.jl)

**Language/role:** Julia; compact incompressible-flow framework with immersed bodies and CPU/GPU array execution.

- **C2:** The repository describes simulation construction from signed-distance body definitions and interchangeable array backends. Geometry and execution choices are reusable inputs to a common solver, rather than separate implementations for each example.
- **C1:** [`MultiLevelPoisson.jl`](https://github.com/WaterLily-jl/WaterLily.jl/blob/master/src/MultiLevelPoisson.jl) exposes the details of pressure multigrid: direction-dependent coarsening, face-coefficient restriction, boundary updates, and simultaneous residual criteria. The restriction scaling depends on whether the face-normal direction is coarsened.
- **C3:** Nested Poisson levels and recursive correction make the pressure solver's acceleration strategy inspectable within a relatively small module.

Study how compact Julia abstractions coexist with real numerical bookkeeping. The code also adjusts correction damping when residual behavior changes; this is more informative than treating multigrid as a black-box library call.

### 24. [CliMA/Oceananigans.jl](https://github.com/CliMA/Oceananigans.jl)

**Language/role:** Julia; finite-volume oceanic and geophysical flow framework with hydrostatic and nonhydrostatic models and CPU/GPU execution.

- **C1:** The [elliptic-solver documentation](https://clima.github.io/OceananigansDocumentation/stable/numerical_implementation/elliptic_solvers) explains why projection must use eigenvalues of the discrete staggered-grid operator, and how the zero-mean pressure choice removes the null-space ambiguity and avoids division by a zero eigenvalue.
- **C3:** Solver organization follows grid structure: transform methods for separable directions, a tridiagonal treatment for a stretched direction, and preconditioned conjugate gradients when nonuniformity prevents an efficient transform diagonalization.

This is a substantive CFD implementation, even though its principal community is geophysical modeling. Engineers can study how grid and boundary assumptions select an algorithm, and how pressure, free-surface behavior, and hydrostatic approximations change the solve. The documentation supplies mathematical and implementation detail rather than only application examples.

### 25. [tumaer/JAXFLUIDS](https://github.com/tumaer/JAXFLUIDS)

**Language/role:** Python/JAX; differentiable compressible-flow and multiphase simulation framework.

- **C2:** The available [API/design documentation](https://jax-fluids.readthedocs.io/en/latest/jaxfluids.html) separates domain information, material models, flux computation, initialization, and simulation management. It describes alternative convective-flux formulations and both conventional simulation and batched feed-forward execution for optimization workflows.
- **C1:** Its integration-step description makes the ordering of multiphase operations explicit: conservative-variable conversion, level-set advancement and reinitialization, geometry reconstruction, mixing, primitive-variable recovery, ghost extension, and boundary updates. Consistency depends on that sequence, not merely on choosing a Runge–Kutta method.

Study how differentiable array programming accommodates a genuine multiphase numerical pipeline. **Version limitation:** the inspected Read the Docs API identifies itself as 0.1.0, whereas the repository describes later development. It is evidence for the documented architecture and algorithm, not verification that every current API retains those names or signatures.

## Coverage, exclusions, and limitations

Discovery used live web searches across more than six distinct angles: general industrial/unstructured finite-volume CFD; finite-element multiphysics; high-order DG and spectral elements; Fortran turbulence/DNS; AMReX-based reacting and wind flows; lattice-Boltzmann frameworks and symbolic kernel generation; SPH and immersed-boundary coupling; Julia scientific software; and JAX/differentiable CFD. Follow-up queries targeted source structure, nonlinear controls, projection algorithms, GPU programming, and release history. Later broad queries increasingly returned already represented numerical families, small teaching solvers, or projects with incomplete-validation notices; Neko was retained after an additional primary-source check.

The selection deliberately mixes broad industrial systems with more focused, independently reusable research frameworks. It does not list generic mesh, linear-algebra, or PDE libraries without a fluid implementation; meshing/postprocessing tools; awesome-lists; or tutorial-only solvers. OpenLB is a significant ecosystem omission imposed by the GitHub focus: its [official download page](https://www.openlb.net/download/) directs public source access to GitLab, and this search did not establish an official substantive GitHub mirror to include. The list is not an exhaustive census of CFD or lattice-Boltzmann software.

Canonical repository pages and redirects were checked. Renamed Kynema and PeleC repositories are listed once under their current destinations; obsolete lbmpy and old Incompact3d repositories are not independent entries. Official mirrors are labeled. Shared ancestry is distinguished from duplication: nekRS and Neko expose separate implementations and backend architectures, while waLBerla and lbmpy provide different framework and numerical-generation layers.

The research inspected primary source and documentation, without cloning, building, running simulations, or reproducing benchmarks. Some generated documentation describes particular releases or predates current repository code; the SU2 and JAX-FLUIDS limitations are called out explicitly. Cached source views can also lag a branch head. No blanket claim of current maintenance, cross-backend equivalence, numerical certification, or measured scalability is made. C4 is assigned only where release-history and engineering-process evidence were actually inspected; age and stars alone were not used as quality evidence.
