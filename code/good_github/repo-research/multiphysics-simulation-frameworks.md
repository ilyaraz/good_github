# Multiphysics simulation frameworks

Research date: **2026-10-09**

This selection covers **25 GitHub repositories** that provide reusable machinery for coupled physical models: integrated finite-element and finite-volume environments, libraries that coordinate independent solvers, and substantial frameworks for subsurface, astronomical, mechanical, and biological simulation. The emphasis is on how coupling, numerical state, discretization, and computational cost shape software architecture. General numerical dependencies, visualization tools, thin solver adapters, and isolated demonstration programs are outside the selection.

Every repository heading links to its verified GitHub location. The technical links within each entry are also reading entry points; each repository was checked against material beyond its repository README. Criteria are evidence-based reasons to study the project, not a certification of every component or numerical model. Statements about what an engineer can learn are grounded interpretations of the cited designs and implementations.

## Criteria legend

- **C1 — Difficult correctness:** coupled numerical semantics, conservation, constraints, synchronization, state invariants, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces and composition mechanisms supporting multiple models and applications.
- **C3 — Performance with structure:** explicit treatment of memory, communication, parallel execution, sparse algebra, or computational work within an understandable design.
- **C4 — Sustained evolution:** evidence of development across years together with compatibility handling, testing, or complexity management. Age or a recent push alone does not qualify.

## Integrated finite-element and coupled-field frameworks

### 1. [idaholab/moose](https://github.com/idaholab/moose)

**Language / role:** C++; integrated finite-element and finite-volume multiphysics framework built around libMesh and PETSc. Study the framework and physics modules within this monorepo as one project.

MOOSE is particularly useful for understanding how a large application ecosystem can share nonlinear solution infrastructure while allowing application authors to introduce physics objects.

- **C1:** Coupled nonlinear residuals and Jacobians sit within a framework whose verification strategy includes analytical solutions and manufactured solutions. Its design document connects numerical responsibilities with regression, unit, and performance testing. [Software design description](https://mooseframework.inl.gov/sqa/moose_sdd.html).
- **C2:** Registered object factories, object warehouses, application ownership, mesh abstractions, systems, and assembly objects give physics extensions a defined place in the execution model. The same design description explains these relationships rather than merely listing modules.
- **C4:** The document traces development from 2008 and describes tests required with new code, staged integration, and testing of dependent applications. This supplies evidence of evolution managed through an explicit verification process.

### 2. [KratosMultiphysics/Kratos](https://github.com/KratosMultiphysics/Kratos)

**Language / role:** C++ with extensive Python interfaces; a shared simulation core plus applications for structural mechanics, fluids, particles, contact, and coupled problems.

An experienced engineer can study how numerical kernels and application orchestration are separated without forcing every physics application to invent its own execution lifecycle.

- **C2:** `AnalysisStage` organizes the analysis lifecycle, `PythonSolver` encapsulates solving a physical problem, and reusable `Process` objects handle tasks such as loads and output. The documented inheritance model lets applications override selected hooks while inheriting changes in the common implementation. [Solving strategies](https://kratosmultiphysics.github.io/Kratos/pages/Kratos/For_Users/Tutorials/Solving_Strategies.html).
- **C3:** The repository explicitly combines a C++ core and application architecture with OpenMP and MPI execution. Python supplies orchestration over that parallel numerical infrastructure. The engineering study point is the boundary between reusable workflow objects and performance-sensitive implementations, rather than a claim of uniform scaling across applications. [Repository architecture and parallelism overview](https://github.com/KratosMultiphysics/Kratos#readme).

### 3. [ElmerCSC/elmerfem](https://github.com/ElmerCSC/elmerfem)

**Language / role:** Primarily Fortran, with C/C++; multiphysics finite-element environment spanning thermal, fluid, structural, electromagnetic, and other models.

Elmer offers a useful view of extensibility in a Fortran-centered scientific codebase. The `fem` subsystem separates the solver library from dynamically loaded equation solvers. [FEM subsystem](https://github.com/ElmerCSC/elmerfem/tree/devel/fem).

- **C1:** Matrix assembly handles real and complex systems, antiperiodic sign changes, and elimination of element-local bubble degrees of freedom. Correctness requires transformations to remain consistent across matrix and force contributions; this is visible in the assembly routines rather than inferred from a feature list. [MatrixAssembly.F90](https://github.com/ElmerCSC/elmerfem/blob/devel/fem/src/MatrixAssembly.F90).
- **C2:** Dynamically loaded solver modules build on common mesh, equation, and assembly services, allowing different physical equations to use the same execution environment.
- **C3:** The assembly implementation supports several matrix representations and static condensation. It exposes the tradeoff between reducing the global system and preserving the correct element-level algebra.

### 4. [feelpp/feelpp](https://github.com/feelpp/feelpp)

**Language / role:** C++ with Python interfaces; mathematical expression infrastructure, finite-element algorithms, and multiphysics toolboxes. Relevant monorepo subsystems include `feelpp` and `feelpp-toolboxes`.

Feel++ is worth studying where the framework boundary is a mathematical language rather than a fixed catalog of physical solvers. Its coefficient-form PDE toolbox makes this concrete.

- **C1:** A system can contain multiple scalar or vector unknowns, with coefficients depending on other unknowns and with explicitly prescribed coefficient shapes. Cross-field dependencies, boundary expressions, and time discretization must therefore agree on both algebraic meaning and dimensions. [Coefficient-form PDE manual](https://docs.feelpp.org/toolboxes/latest/cfpdes/manual.html).
- **C2:** The same manual shows how function spaces, coefficient expressions, equations, boundary conditions, and time integration compose into a general solver. The repository also supplies specialized toolboxes for applications such as fluid–structure interaction and heat–fluid coupling, providing a comparison between generic and domain-specific interfaces.

### 5. [goma/goma](https://github.com/goma/goma)

**Language / role:** Primarily C; coupled finite-element simulation of transport, fluid and solid mechanics, chemistry, and free or moving boundaries.

Goma is a strong study candidate for tightly coupled assembly. Its background documentation explains precisely where equation contributions meet and how that common representation reaches different algebra packages.

- **C1:** Active equations and boundary conditions are solved together at the same time level and Newton iteration. Moving geometry and multiple conservation equations consequently require consistent coupled linearization. [Numerical and implementation background](https://docs.gomafem.com/background.html).
- **C2:** The element-level organization accumulates contributions into a common local matrix before global assembly. This gives multiple physical models a shared implementation contract instead of independent solver-specific assembly paths.
- **C3:** That local representation feeds modified sparse-row, variable-block-row, or frontal solver formats. The background guide makes the relationship between finite-element assembly and alternative storage/solver choices visible, without requiring a numerical speedup claim.

### 6. [oofem/oofem](https://github.com/oofem/oofem)

**Language / role:** C++; object-oriented finite-element framework covering structural, transport, and fluid problems, including staggered coupled analyses.

The `EngngModel` interface is an unusually informative starting point for the boundary between physical problem management, numerical methods, and persistent simulation state.

- **C1:** Its interface documents changing degree-of-freedom numbering, committing material history after a step, and recursive saving/restoring of domains and integration-point state. Those are central invariants for nonlinear history-dependent models and restarts. [Engineering-model interface and design comments](https://raw.githubusercontent.com/oofem/oofem/master/src/core/engngm.h).
- **C2:** Engineering models map physical entities to numerical-method abstractions, while a shared context and field manager support communication between submodels such as heat and structural analyses. Metasteps separate groups of steps with different controls.
- **C3:** The same interface describes batching remote element data for nonlocal material models to avoid fine-grained communication. It is a concrete example of a distributed-memory concern shaping the model API.

### 7. [oomph-lib/oomph-lib](https://github.com/oomph-lib/oomph-lib)

**Language / role:** C++; finite-element library emphasizing multiphysics, nonlinear problems, fluid–structure interaction, and adaptive discretizations.

Study this project for its explicit treatment of dependencies between elements on different meshes. The introductory documentation describes how problems, meshes, and elements form the main application structure. [Library overview](https://oomph-lib.github.io/oomph-lib/doc/html/index.html).

- **C1:** An element's external `Data` may belong to another mesh. The documented numbering procedure assigns global numbers across all meshes before local equation numbering, avoiding unresolved cross-mesh dependencies. Hanging-node accessors also preserve constrained values and positions. [Data structures and equation numbering](https://oomph-lib.github.io/oomph-lib/doc/the_data_structure/html/index.html).
- **C2:** `GeneralisedElement`, internal and external data, and mesh composition allow new interactions to reuse the nonlinear problem infrastructure. Default finite-difference Jacobian support supplies a useful reference path when developing additional couplings.

### 8. [sfepy/sfepy](https://github.com/sfepy/sfepy)

**Language / role:** Python-centered finite-element framework for systems of coupled PDEs, with compiled numerical support.

SfePy exposes much of the problem construction process in Python, making it useful for studying a compact separation between mathematical declarations and numerical state.

- **C1:** Essential boundary conditions remove degrees of freedom from the solved system, while evaluation and state manipulation must maintain the relationship between reduced and full vectors. The primer also explains when variable data share storage with a state vector—an important aliasing concern during residual evaluation and updates. [SfePy primer](https://sfepy.org/doc/primer.html).
- **C2:** Regions, fields, unknown and test variables, materials, weak-form terms, and solvers are separate objects that can be assembled through problem descriptions or an interactive API. This supports coupled formulations while leaving the constituent numerical objects inspectable.

### 9. [halbux/sparselizard](https://github.com/halbux/sparselizard)

**Language / role:** C++; finite-element formulation library for nonlinear coupled fields, including electromechanics, acoustics, thermal problems, and circuit coupling.

Its piezoelectric micromembrane example provides a particularly concrete engineering reading path: electric potential, structural displacement, and acoustic pressure appear in one formulation.

- **C1:** The implementation combines reciprocal piezoelectric terms, rotated anisotropic material tensors, harmonic fields, and pressure/acceleration coupling at the fluid–solid boundary. It explicitly compensates pressure scaling in both coupling and output, illustrating how conditioning changes must preserve physical interpretation. [Coupled PMUT implementation](https://github.com/halbux/sparselizard/blob/master/examples/pmut-axisymmetry-2d/main.cpp).
- **C2:** Fields, regions, parameters, test functions, and integrals compose through a common formulation API, with predefined physics operators and separately chosen interpolation orders. The same example demonstrates reuse across three physical systems.
- **C3:** Hierarchical interpolation orders and adaptive refinement let work be allocated by field and region. The [official technical overview](https://www.sparselizard.org/) describes these mechanisms; its promotional performance comparisons are not used here.

### 10. [4C-multiphysics/4C](https://github.com/4C-multiphysics/4C)

**Language / role:** C++; parallel research framework for finite-element and particle-based computational mechanics and multiphysics.

4C is useful for comparing partitioned and monolithic solution strategies within one codebase, especially when the mathematical block structure needs to remain visible to the algebra layer.

- **C2:** Individual fields can have independently configured solvers, while a monolithic multiphysics problem supplies an additional coupled solver. The documentation demonstrates this with structure–scalar interaction and relates it to fluid–structure and thermo–structure systems. [Coupled linear-solver architecture](https://4c-multiphysics.github.io/4C/documentation/analysis_guide/linear_solvers.html).
- **C3:** Block preconditioners, multigrid, distributed sparse algebra, and static condensation of contact multipliers are discussed in relation to the structure of the coupled system. This is more informative than treating solver selection as a generic backend switch.

The [build and parallel-backend guide](https://4c-multiphysics.github.io/4C/documentation/installation/installation.html) additionally exposes MPI/Kokkos integration and oversubscription constraints. The project describes itself as research software; this entry does not imply qualification for safety-critical calculations.

## Frameworks that couple independent solvers

### 11. [precice/precice](https://github.com/precice/precice)

**Language / role:** C++ coupling library with interfaces and adapters for other languages and simulation packages; partitioned multiphysics across solver boundaries.

preCICE is a particularly good study target for understanding why a coupling API needs a transactional time-step protocol, not just field exchange calls.

- **C1:** Implicit coupling requires saving a complete solver checkpoint, restoring it when the coupling iteration has not converged, and advancing accepted time only after convergence. The documentation explains that restoring insufficient state breaks the deterministic behavior needed by quasi-Newton coupling acceleration. [Implicit coupling protocol](https://precice.org/couple-your-code-implicit-coupling.html).
- **C2:** The participant interface separates mesh/data registration, reads and writes, advancement, and checkpoint requests from the internal solver implementation. The same integration structure accommodates explicit coupling and subcycling, making it reusable across independently developed physics programs.

The checkpoint discussion is the best first reading: it ties an apparently small API contract to numerical convergence and correct solver lifecycle management.

### 12. [MxUI/MUI](https://github.com/MxUI/MUI)

**Language / role:** Header-oriented C++ coupling library; configurable spatial and temporal sampling between heterogeneous simulation codes.

MUI is distinctive because sampled, time-stamped data are its core abstraction. This can bridge particle and continuum methods without imposing a common mesh or discretization.

- **C1:** The `uniface` implementation coordinates pushed data, commits, time-indexed logs, fetches, and barriers. Time samplers influence which data must be available before a fetch can proceed; numerical comparisons near time bounds and asynchronous arrival therefore affect correctness. [uniface implementation](https://raw.githubusercontent.com/MxUI/MUI/master/src/uniface.h).
- **C2:** Spatial samplers, temporal samplers, and configurable types are composed with the communication interface. An application chooses the interpretation of exchanged data instead of inheriting one fixed interpolation rule.
- **C3:** The implementation includes a fixed-point data path and separates sampling from communication/storage machinery. The [source organization](https://github.com/MxUI/MUI/tree/master/src) is a useful second entry point for tracing those responsibilities and the template-based implementation.

### 13. [multiscale/muscle3](https://github.com/multiscale/muscle3)

**Language / role:** Python and C++ with additional language interfaces; orchestration and communication for coupled multiscale simulation components.

MUSCLE3 is especially valuable for distributed checkpointing and restart semantics. Its documentation explains difficult cases and limitations rather than presenting snapshots as a transparent serialization feature.

- **C1:** Consistent restart depends on the relationship between component snapshots and messages already sent or received. Message counters and duplicate-message handling address replay, while the checkpoint guide explains why arbitrary wall-clock snapshots can be inconsistent. [Checkpointing deep dive](https://muscle3.readthedocs.io/en/master/checkpointing_deep_dive.html).
- **C2:** Components expose ports and interaction patterns, with scale bridges handling mismatched simulation time scales. Explicit coupling rules permit an output to feed multiple inputs but disallow multiple outputs feeding one input, keeping component composition understandable. [Coupling model](https://muscle3.readthedocs.io/en/master/coupling.html).

This is a useful complement to integrated PDE frameworks: the main engineering problem is coordinating independently progressing simulations and preserving causality.

### 14. [esmf-org/esmf](https://github.com/esmf-org/esmf)

**Language / role:** Fortran and C++; Earth System Modeling Framework for assembling coupled climate and Earth-system applications.

ESMF exposes resource layout as part of component composition, making it useful for studying frameworks in which different physical models run on different sets of processes.

- **C1:** Distributed object creation has collective participation requirements. State reconciliation creates the information needed to represent distributed objects consistently, and mismatched participation can violate the execution contract. [Superstructure reference](https://earthsystemmodeling.org/docs/release/latest/ESMF_refdoc/node4.html).
- **C2:** Gridded components and coupler components share initialization, run, and finalization conventions, exchanging import and export `State` objects. The hierarchy supports reusable component interfaces rather than a single fixed climate model.
- **C3:** Persistent execution threads and virtual machines define how components occupy computational resources. The same reference discusses sequential and concurrent layouts, coupling across process sets, and overlap of communication and computation.

### 15. [amusecode/amuse](https://github.com/amusecode/amuse)

**Language / role:** Python orchestration around community solvers, including C++ and Fortran codes; astrophysical multiphysics and multiscale simulation.

AMUSE brings together stellar dynamics, stellar evolution, and hydrodynamics through common interfaces. Its [community-code guide](https://amuse.readthedocs.io/en/latest/reference/available-codes.html) establishes that breadth, but explicitly warns that its detailed inventory is not up to date.

- **C1:** The Bridge coupling scheme uses kick–drift–kick splitting. Its documentation identifies assumptions about subsystem separation, time-step choice, and synchronization, including cases where synchronization can reduce integration order. Those qualifications are important numerical API semantics. [Bridge reference](https://amuse.readthedocs.io/en/latest/reference/bridge.html).
- **C2:** Common solver interfaces let different subsystem integrators participate in the same Bridge, and Bridges can be nested. Derived interaction systems can limit which gravitational interactions are calculated. Study this for composition of existing numerical programs with different strengths and time scales.

## Subsurface and fractured-media multiphysics

### 16. [GEOS-DEV/GEOS](https://github.com/GEOS-DEV/GEOS)

**Language / role:** C++; coupled subsurface flow, transport, geomechanics, and fracture simulation. Relevant subsystem: `src/coreComponents/physicsSolvers/multiphysics`.

GEOS provides a clear implementation comparison between fully implicit block assembly and sequential coupling of constituent solvers.

- **C1:** `CoupledSolver` propagates state resets to subsolvers, manages time-step cuts, checks solution validity across all constituents, and evaluates outer coupling convergence. It explicitly rejects unsupported combinations such as sequential coupling with the coupled solver's line search enabled. [CoupledSolver implementation](https://raw.githubusercontent.com/GEOS-DEV/GEOS/develop/src/coreComponents/physicsSolvers/multiphysics/CoupledSolver.hpp).
- **C2:** A variadic template composes typed subsolvers, with hooks for coupling degrees of freedom, assembling off-diagonal contributions, and mapping one solver's solution into another's fields.
- **C3:** The sequential path rebuilds system sparsity only when the mesh modification timestamp requires it. This places an optimization next to its invalidation condition, making the correctness/performance relationship easy to inspect.

The [common solution strategy](https://github.com/GEOS-DEV/GEOS/blob/develop/src/coreComponents/physicsSolvers/SolutionStrategy.rst) provides context for Newton iteration, line search, and time-step recovery.

### 17. [amanzi/amanzi](https://github.com/amanzi/amanzi)

**Language / role:** C++; environmental subsurface simulation and reusable infrastructure for coupled flow, transport, chemistry, energy, and mechanics.

Amanzi is useful for studying how a domain-oriented simulator separates process coupling from mesh and solver infrastructure. Its repository describes hierarchical coupling, including weak and strong coupling, mixed dimensions, and subcycling.

- **C2:** Process kernels and coupling infrastructure support combinations of flow, transport, reactions, and other models. The input specification exposes those processes alongside distinct material, region, mesh, execution, and numerical-control sections. [Unstructured input and process specification](https://amanzi.github.io/amanzi/UserGuide/guides/input_spec/AmanziInputSpec-u.html).
- **C3:** The specification explains why structured patches and arbitrary unstructured cells require different data layouts and numerical implementations. It also describes partitioner choices, including preserving element columns in a partitioning option, rather than assuming every mesh partition has equivalent computational behavior.

The cited manual is explicitly versioned **1.6-dev**. It is architectural evidence, not a promise that every listed input option remains the recommended interface in the repository's current branch.

### 18. [pmgbergen/porepy](https://github.com/pmgbergen/porepy)

**Language / role:** Python; mixed-dimensional modeling of fractured porous media, including flow, thermal effects, poromechanics, and fracture deformation.

PorePy is a useful counterpoint to large C++ systems: much of the physical model composition and differentiable equation construction remains directly inspectable in Python.

- **C1:** The momentum-balance implementation distinguishes matrix-domain equations from fracture-interface force balance and contact constraints. It makes stress sign conventions and mortar-interface displacement variables explicit. Its three-field discretization also documents geometric grid conditions required for consistency. [Momentum and interface-balance implementation](https://raw.githubusercontent.com/pmgbergen/porepy/develop/src/porepy/models/momentum_balance.py).
- **C2:** Equation, constitutive-law, variable, boundary-condition, initialization, and solution-strategy mixins compose into a model. Shared automatic-differentiation operators connect those responsibilities without requiring a separate monolithic class for every physical combination.

Study both the benefits and the complexity of this approach: the source itself records typing and method-resolution concerns associated with the mixin architecture.

## Differentiable finite-volume frameworks in Julia

### 19. [sintefmath/Jutul.jl](https://github.com/sintefmath/Jutul.jl)

**Language / role:** Julia; implicit finite-volume multiphysics infrastructure with automatic differentiation, used by reservoir, battery, and carbon-capture applications. The project explicitly calls the framework experimental.

Jutul is a good study target for separating physical models from computational execution while retaining an inspectable simulation loop.

- **C1:** The simulation configuration includes nonlinear convergence limits, time-step cuts, and failure handling. Model variables are associated with domain entities, with shape requirements that must match the discretization. [Models, contexts, and simulation guide](https://sintefmath.github.io/Jutul.jl/stable/usage/).
- **C2:** `SimulationModel` separates mesh/domain information from the physical system; `MultiModel` composes named submodels. Primary variables, secondary variables, parameters, and computational contexts have distinct roles.
- **C3:** Contexts control allocation and matrix layout, while a reusable `Simulator` and `simulate!` avoid rebuilding and reallocating the simulation machinery for repeated runs. These explicit mechanisms are stronger performance evidence than a language-level speed claim.

### 20. [WIAS-PDELib/VoronoiFVM.jl](https://github.com/WIAS-PDELib/VoronoiFVM.jl)

**Language / role:** Julia; coupled nonlinear conservation-law framework used for semiconductor drift–diffusion, electrolytes, and reactive transport.

The project is especially instructive for the interface between local constitutive functions and generic assembly with automatic differentiation.

- **C1:** Flux callbacks see the unknowns at both ends of an edge; storage, reactions, and boundary contributions follow distinct contracts. Correct species indexing and local dependencies determine the assembled coupled equations and their derivatives. [Physics callback API](https://wias-pdelib.github.io/VoronoiFVM.jl/stable/physics/).
- **C2:** Those callbacks let different physical models share the same finite-volume infrastructure, with user data or closures carrying model parameters.
- **C4:** The changelog records changes across 2019–2024 and beyond, including compatibility aliases, deprecations, notebook and ODE-interface testing, and refactoring solver strategies to avoid a combinatorial proliferation of interfaces. It also documents numerical changes that required updating expected test results. [Evolution and compatibility record](https://wias-pdelib.github.io/VoronoiFVM.jl/stable/changes/).

## Mechanics, particles, biomechanics, and coupled design

### 21. [sofa-framework/sofa](https://github.com/sofa-framework/sofa)

**Language / role:** C++; modular physical simulation framework with an emphasis on interactive and medical simulation.

SOFA's most distinctive study opportunity is its multi-model representation: mechanical, collision, and visual models can use different discretizations linked by mappings.

- **C1:** Mappings propagate velocities through a Jacobian and forces through its transpose to maintain virtual-work consistency. Nonlinear mappings also contribute geometric stiffness through derivatives of the mapping Jacobian; this can change matrix symmetry and solver requirements. [Mapping architecture and mathematics](https://sofa-framework.github.io/doc/simulation-principles/multi-model-representation/mapping/).
- **C2:** The mapping interface separates position application, derivative application, transpose application, and geometric-stiffness effects. New representations can participate through that shared contract rather than requiring bespoke pairwise simulator integrations.
- **C3:** Separate discretizations allow collision, mechanics, and rendering to use different resolutions. The mapping architecture makes the transfer cost and consistency obligations explicit while allowing computational effort to differ by subsystem.

### 22. [projectchrono/chrono](https://github.com/projectchrono/chrono)

**Language / role:** C++; multibody, deformable-body, contact, and fluid–structure simulation. This entry focuses on the monorepo's Chrono FSI/SPH subsystem.

Chrono is useful for studying a layered coupling API with both general interfaces and a specialized implementation that reduces data movement.

- **C2:** `ChFsiSystem` coordinates fluid and multibody systems; `ChFsiFluidSystem` and `ChFsiInterface` define the abstraction boundary. Higher-level problem builders set up SPH particles, boundary representations, rigid bodies, and finite-element participants. [FSI/SPH class architecture](https://api.chrono.projectchrono.org/manual_fsi_sph_class_guide.html).
- **C3:** The specialized SPH interface avoids the general interface's intermediate buffer route and works more directly with the SPH data manager. The guide explains why maintaining a specialized path alongside the reusable abstraction matters for host/device transfer costs.

The study focus is this concrete coupling layer, rather than an assertion that all Chrono modules have identical numerical or performance properties.

### 23. [Xiangyu-Hu/SPHinXsys](https://github.com/Xiangyu-Hu/SPHinXsys)

**Language / role:** C++; smoothed-particle-hydrodynamics framework for coupled fluid, solid, and multibody systems.

Its two-dimensional fluid–structure benchmark is a useful executable reading example of how the framework composes bodies, materials, neighborhood relations, dynamics operators, and observers.

- **C1:** The FSI loop separates fluid advection, fluid acoustic, and solid time scales. It transfers viscous and pressure forces and averages solid velocity/acceleration across substeps, making multi-rate coupling semantics visible. [FSI benchmark implementation](https://github.com/Xiangyu-Hu/SPHinXsys/blob/master/tests/2d_examples/test_2d_fsi2/fsi2.cpp).
- **C2:** The benchmark builds the coupled problem from reusable body, relation, material, and dynamics objects rather than a single bespoke FSI routine.
- **C3:** Particle sorting, cell-linked-list updates, and refreshed contact configurations appear explicitly in the loop. Their ordering relative to motion and periodic conditions illustrates how neighborhood-search optimization must respect changes in the simulated geometry.

### 24. [febiosoftware/FEBio](https://github.com/febiosoftware/FEBio)

**Language / role:** C++; nonlinear finite-element biomechanics framework. Relevant subsystems include FECore, FEBioMech, FEBioMix, and FEBioFluid; they count as one repository.

FEBio's biphasic-solute solver is a concrete place to study how mechanics, pore-fluid pressure, and species concentrations enter one nonlinear solution process.

- **C1:** The solver evaluates displacement, pressure, concentration, residual, and energy convergence measures, handles line-search failures and divergence through matrix reformation, and starts with an unsymmetric stiffness assumption. Those choices expose numerical failure modes specific to coupled systems. [Biphasic-solute solver](https://github.com/febiosoftware/FEBio/blob/develop/FEBioMix/FEBiphasicSoluteSolver.cpp).
- **C2:** It extends a biphasic solver, registers additional solution variables through shared degree-of-freedom services, and assembles elastic, biphasic, and solute domains through common residual and linear-system objects. This shows both the reuse and the branching complexity of an inheritance-based physics hierarchy.

The [FEBioMix source directory](https://github.com/febiosoftware/FEBio/tree/develop/FEBioMix) supplies the surrounding domain, material, and analysis implementations. No clinical validation claim is implied by inclusion.

### 25. [su2code/SU2](https://github.com/su2code/SU2)

**Language / role:** C++ with Python tooling; simulation and design framework whose multizone subsystem supports coupled flow, solid, thermal, and radiation problems.

SU2 belongs here through its multiphysics driver and coupled sensitivities, not simply through its CFD solvers.

- **C1:** The conjugate heat-transfer/radiation example tracks interface heat balance and outer block Gauss–Seidel convergence across fluid and solid variables. Coupled adjoint calculations extend the consistency requirement to sensitivities used in design. [Radiation and conjugate heat-transfer tutorial](https://su2code.github.io/tutorials/Turbulent_RHT_CHT/).
- **C2:** Multizone simulation gives zones separate meshes and configurations, supports nonmatching interfaces, and combines inherited defaults with zone-specific settings. Coupling behavior depends on the participating solvers, making the driver a reusable coordination layer. [Multizone architecture](https://su2code.github.io/docs_v7/Multizone/).

These reading entry points describe the **version 7** interface and a versioned tutorial. They establish the architecture and numerical issues; they should not be treated as unqualified configuration instructions for a newer release.

## Coverage, search process, and limitations

Discovery used live web searches across more than six distinct angles: integrated multiphysics frameworks; finite-element application/plugin architectures; partitioned coupling and co-simulation; MPI interpolation and OpenPALM/CWIPI-style interfaces; Python/Julia/Rust implementations; subsurface reactive transport and fractured media; particle and meshless FSI; biomechanics; climate and astrophysical coupling; and electromagnetic, thermal, and multizone design problems. Targeted follow-up searches sought architecture manuals, source implementations, checkpoint semantics, testing, and changelogs. Later broad searches increasingly repeated the retained families or returned individual research solvers and thin integrations; late distinct additions included VoronoiFVM.jl and 4C. This is a substantial selection, not an exhaustive ecosystem census.

Canonical GitHub repository pages were opened for every retained entry. Additional primary documents or actual source files were read for each; reading a raw copy of a README was not counted as independent evidence. The C++ emphasis reflects the verified candidates, with Fortran-centered systems, Python composition frameworks, and Julia finite-volume designs included deliberately. No project was included merely to fill a language quota or because of its stars.

Important boundaries and exclusions:

- **Moved project:** [ufz/ogs](https://github.com/ufz/ogs) explicitly says not to use that repository and directs development to GitLab. It was excluded rather than represented as a maintained GitHub project.
- **Verification limitation:** [onera/cwipi](https://github.com/onera/cwipi) is an official substantive candidate whose repository documents both GitHub and ONERA GitLab distribution. Its deeper documentation/source pages could not be read reliably through the research browser, so it was not promoted into the verified selection. This is a retrieval limitation, not a negative quality judgment.
- **Adjacent infrastructure:** General finite-element foundations such as deal.II, FEniCS, and MFEM were outside the chosen emphasis on explicit multiphysics composition frameworks. Thin adapters, wrappers, tutorial-only repositories, and separate applications of an already-listed framework were not counted as independent framework entries.
- **Status and evidence limits:** No retained repository was presented as an archived historical project or a moved-away placeholder. Inclusion does not itself assert a maintenance cadence. C4 is assigned only where multi-year change and quality-management evidence was actually inspected; most projects qualify through other criteria. Versioned documentation and the outdated AMUSE code inventory are identified where used. Source links track the explicitly named branches, including OOFEM's inspected `master` interface, and can change after this date.

The research was read-only: no candidate code was executed, benchmarked, installed, or cloned. Architectural suitability is inferred from inspected implementation and documentation, not from independent verification of simulation outputs. In particular, numerical convergence, conservation, scaling, and model validity still depend on the chosen formulation, discretization, configuration, and application.
