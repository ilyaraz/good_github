# Partial differential equation and finite element frameworks

Research date: **2026-10-09**

This selection covers **27 GitHub repositories** implementing reusable PDE discretization and simulation infrastructure: finite elements, discontinuous Galerkin methods, finite volumes, adaptive mesh refinement, spectral methods, and differentiable grid simulation. It includes both large distributed frameworks and smaller libraries whose numerical abstractions are especially accessible. Application suites are included when they expose substantial reusable solver infrastructure; a monorepo is counted once, with the relevant subsystem identified. GitHub mirrors are labeled explicitly.

The criteria below identify worthwhile engineering study, not a certification of every component or a ranking of numerical accuracy:

- **C1 — Correctness:** difficult invariants, numerical semantics, concurrency, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces supporting multiple equations, discretizations, or applications.
- **C3 — Performance:** concrete memory, computation, or communication constraints addressed through identifiable architecture.
- **C4 — Evolution:** evidence of development across years together with compatibility, testing, or complexity management.

## General finite element and distributed discretization engines

### 1. [dealii/dealii](https://github.com/dealii/dealii)

**Language/role:** C++; adaptive finite element library, including distributed and high-order discretizations.

Study how an apparently local choice—the polynomial degree on an element—affects global numbering, communication, constraints, and load balancing.

- **C1:** The authors' version 9.1 account explains how distributed hp discretization reconciles shared degrees of freedom across processor boundaries so the global count does not depend on partitioning. Variable amounts of per-cell data must survive mesh repartitioning.
- **C2:** Meshes, finite elements, degree-of-freedom management, constraints, and operator application form reusable layers rather than an equation-specific solver.
- **C3:** The same account connects unequal element costs to weighted partitioning, and describes matrix-free tensor-product evaluation, SIMD, and distributed host/device vectors. These are specific architectural responses to memory and communication costs.

**Technical entry point:** the authors' [deal.II 9.1 implementation and release report](https://dealii.org/deal91-preprint.pdf), especially distributed hp adaptivity and matrix-free evaluation. This is historical architectural evidence, not a statement that its backend details describe every current configuration.

### 2. [mfem/mfem](https://github.com/mfem/mfem)

**Language/role:** C++; general finite element discretization and operator library.

MFEM is particularly useful for studying how one mathematical operator can support different assembly and storage strategies.

- **C1:** Adaptive-mesh constraints enter through prolongation/restriction, while constrained operators must reproduce essential-boundary-condition elimination without requiring a stored global matrix.
- **C2:** Its operator decomposition separates parallel restriction **P**, element restriction **G**, basis evaluation **B**, and quadrature-point physics **D**. This separates mesh topology, approximation spaces, and coefficients.
- **C3:** Partial assembly stores quadrature data and applies the other factors when needed. The documentation also explains the resulting preconditioning tradeoff: an assembled matrix is unavailable to methods that require its entries.

**Technical entry point:** [finite element operator decomposition and partial assembly](https://mfem.org/performance/). This gives substantially more architectural information than a backend or feature list.

### 3. [FEniCS/dolfinx](https://github.com/FEniCS/dolfinx)

**Language/role:** C++ and Python; the DOLFINx problem-solving environment within FEniCS.

Study the boundary between compiled variational forms and mesh-dependent runtime objects. Related FEniCS repositories are dependencies, not additional entries here.

- **C1:** The FEM API distinguishes owned from ghost degrees of freedom in boundary-condition indices, and distinguishes point evaluation from interpolation for moment-based degrees of freedom. Coordinate pullbacks can require Newton iteration with scalar-type-dependent tolerances.
- **C2:** `Form`, `FunctionSpace`, `DofMap`, and coordinate elements are separate objects. Mesh-independent form compilation is distinct from creating a form attached to concrete spaces, coefficients, and integration domains.

**Technical entry point:** the [DOLFINx FEM API](https://docs.fenicsproject.org/dolfinx/main/python/generated/dolfinx.fem.html), particularly `DirichletBC`, `CoordinateElement`, `compile_form`, and `create_form`. It exposes numerical and distributed ownership contracts that application-level examples can hide.

### 4. [firedrakeproject/firedrake](https://github.com/firedrakeproject/firedrake)

**Language/role:** Python with compiled numerical kernels; automated finite element framework.

Firedrake is a strong study in composing a mathematical language, kernel generation, mesh iteration, and external solvers.

- **C1:** Its parallel contract requires collective operations on the mesh's communicator. The parallelism documentation discusses how Python object lifetime and collective PETSc destruction can produce deadlocks, illustrating correctness obligations beyond the weak form itself.
- **C2:** The authors' architecture paper separates symbolic variational forms, local assembly kernels, mesh-wide iteration, and PETSc solver objects. PyOP2 decouples local computations from their traversal over the domain.
- **C3:** That decomposition enables kernel optimization and loop transformations independently of the equation description; it also exposes memory bandwidth and communication as practical constraints.

**Technical entry points:** [parallelism and communicator/lifetime rules](https://www.firedrakeproject.org/parallelism.html) and the [authors' architecture paper](https://arxiv.org/pdf/1501.01809). The paper describes the original architecture; its particular compiler/backend inventory is historical.

### 5. [libMesh/libmesh](https://github.com/libMesh/libmesh)

**Language/role:** C++; reusable finite element infrastructure for multiphysics applications.

The degree-of-freedom layer is an unusually concrete entry into the interaction of mesh adaptivity, algebraic constraints, and distributed assembly.

- **C1:** `DofMap` handles recursively dependent constraints across ranks. Its implementation requests missing remote information and continues expansion until the distributed constraint graph is resolved. An empty constraint row must remain distinguishable from the absence of a constraint; duplicate rows also require explicit handling.
- **C2:** Degree-of-freedom indexing, constraint rows, sparsity construction, and related communication sit behind a shared `DofMap` interface used by different finite element systems. Separate handling of primal and adjoint constraints extends the abstraction beyond one forward solve.

**Technical entry point:** the source-backed [`DofMap` reference](https://libmesh.github.io/doxygen/classlibMesh_1_1DofMap.html), especially constraint insertion and recursive constraint processing. This is a useful route into implementation details without starting from the entire application framework.

### 6. [NGSolve/ngsolve](https://github.com/NGSolve/ngsolve)

**Language/role:** C++ with Python interfaces; high-order finite element framework.

Study static condensation as a reusable operator transformation, including the reconstruction needed after solving the reduced system.

- **C1:** Condensation classifies degrees of freedom as local, interface, or wirebasket. Solving the Schur complement requires excluding both eliminated local unknowns and prescribed boundary unknowns; the full solution then needs harmonic extension and the local inverse contribution.
- **C2:** The `BilinearForm` interface exposes condensation and reconstruction operators independently of a particular PDE. The coupling classification allows finite element spaces to participate through a common contract.
- **C3:** Eliminating element-interior unknowns reduces the globally coupled problem while preserving local recovery operations.

**Technical entry point:** the versioned [static-condensation tutorial](https://docu.ngsolve.org/v6.2.2304/i-tutorials/unit-1.4-staticcond/staticcond.html), including `FreeDofs(coupling=True)`, `harmonic_extension`, and `inner_solve`. It explains the algebra as well as the API.

### 7. [getfem/getfem](https://github.com/getfem/getfem)

**Language/role:** C++ with scripting-language interfaces; generic finite element and weak-form assembly library. **GitHub mirror.**

GetFEM is valuable for studying a numerical expression compiler embedded inside a simulation library.

- **C1:** Its generic weak-form language passes through parsing, semantic analysis, and symbolic differentiation. The resulting expressions must retain the tensor and derivative semantics needed for residual and tangent assembly.
- **C2:** The same language expresses many weak forms instead of requiring a separately handwritten assembly routine for every equation.
- **C3:** Expressions are compiled into instructions executed at integration points. Common subexpressions can share tensor storage, while sparsity information avoids unnecessary tensor operations; compilation and repeated quadrature evaluation are distinct stages.

**Technical entry point:** the developer documentation on [high-level generic assembly](https://getfem.org/project/libdesc_high_gen_assemb.html). The linked repository identifies itself as a mirror; do not assume GitHub is the upstream contribution venue.

### 8. [fempar/fempar](https://github.com/fempar/fempar)

**Language/role:** Object-oriented Fortran; finite element framework with parallel and domain-decomposition infrastructure. **Official GitHub mirror of the GitLab project.**

This provides a substantial Fortran counterpoint to C++ templates and Python form compilers.

- **C1:** Reference elements encode ownership and permutations of degrees of freedom on mesh entities. Those permutations are essential to matching neighboring elements consistently, especially for spaces whose unknowns are associated with edges or faces.
- **C2:** The design exposes mathematical concepts through types such as `reference_fe_t` and triangulation abstractions. Deferred operations cover cell/facet quadrature, interpolation, and mappings, allowing different element families to share assembly infrastructure.

**Technical entry point:** the authors' [FEMPAR design paper](https://arxiv.org/pdf/1708.01773), especially the reference-element and triangulation sections. It documents a particular architectural generation; the mirror's existence alone does not establish synchronization frequency or current maintenance cadence.

### 9. [dune-project/dune-pdelab](https://github.com/dune-project/dune-pdelab)

**Language/role:** C++; PDE discretization toolbox built on DUNE's generic grid and numerical interfaces. **Official mirror; development is on DUNE's GitLab.**

Study how local operators and grid operators compose spatial discretization with time integration.

- **C1:** The team's time-dependent tutorial makes boundary data at Runge–Kutta stages explicit, including the assumption that boundary-condition types remain fixed within a step. Correct timing of parameter updates is part of the operator contract.
- **C2:** Separate spatial and temporal `GridOperator` objects combine through `OneStepGridOperator`; time-stepping coefficients and solver backends remain interchangeable. Stationary parameter classes extend through `setTime` rather than a completely separate interface.
- **C3:** The documented diagonally implicit schemes can reuse an assembled matrix across stages when their diagonal coefficients and the linear problem permit it.

**Technical entry point:** the PDELab team's [nonlinear heat-equation implementation tutorial](https://dune-pdelab-course.readthedocs.io/en/latest/_downloads/3a78c5f7bcec0337dfe46d963f0cef93/tutorial03.pdf), a 2021 architectural example with actual class composition and algorithms.

### 10. [petsc/petsc](https://github.com/petsc/petsc)

**Language/role:** Primarily C; the **DMPlex/PetscSection/PetscFE PDE discretization subsystem** of the PETSc monorepo. **GitHub mirror; development is hosted on GitLab.**

This entry concerns PETSc's mesh and discretization machinery, not merely its general-purpose linear solvers.

- **C1:** Mesh closure ordering, entity orientation, and assignment of degrees of freedom must agree. Periodic topology presents an additional subtlety: a topologically identified mesh can require discontinuous coordinates to represent cells crossing the periodic boundary correctly.
- **C2:** DMPlex represents mesh entities in a directed acyclic graph, supporting dimension-independent traversal. `PetscSection` supplies field layout separately from topology, while finite element and solver interfaces build on these representations.

**Technical entry points:** the [DMPlex manual](https://petsc.org/release/manual/dmplex/) and [official source/distribution policy](https://petsc.org/release/install/download/). This separation of topology, coordinates, and field storage is useful even when studying a framework that uses PETSc indirectly.

## Multiphysics frameworks and equation languages

### 11. [idaholab/moose](https://github.com/idaholab/moose)

**Language/role:** C++; multiphysics framework and physics modules in one monorepo.

Study the framework's `Kernel` extension interface: a developer supplies one contribution to a weak residual, and the framework coordinates assembly and solution.

- **C1:** A nonlinear term needs a Jacobian consistent with its residual, including off-diagonal coupling to other fields. `ADKernel` derives Jacobian contributions from residual expressions, while ordinary kernels expose the corresponding manual methods.
- **C2:** Kernels represent individual weak-form contributions and can be composed into different multiphysics equations. The abstraction is smaller and more reusable than an entire application-specific solver.
- **C3:** Specialized value/gradient kernel interfaces allow factors independent of the test function to be computed outside repeated test-function work at a quadrature point.

**Technical entry point:** the [kernel system and implementation examples](https://mooseframework.inl.gov/docs/site/syntax/Kernels/index.html), including `computeQpResidual`, Jacobian methods, and `ADDiffusion`.

### 12. [FreeFem/FreeFem-sources](https://github.com/FreeFem/FreeFem-sources)

**Language/role:** C++ implementation of the FreeFEM finite element scripting language and runtime.

Composite finite element spaces make this a useful study in extending a numerical language while preserving the meaning of existing constructs.

- **C1:** The documented Stokes formulation uses a coarser pressure mesh and a refined velocity mesh, and explicitly regularizes the undetermined pressure constant. The implementation must assemble a coupled variational problem across those different spaces and meshes.
- **C2:** Composite spaces generalize ordinary vector spaces to products whose components can use different mesh types and independent periodic conditions. This supports domain, surface-volume, and FEM–BEM coupling through the same language construct.

**Technical entry point:** [composite finite element spaces](https://doc.freefem.org/documentation/composite.html), including the P2-iso-P1 Stokes example and its executable language syntax. The documentation identifies this extension as introduced in version 4.13.

### 13. [feelpp/feelpp](https://github.com/feelpp/feelpp)

**Language/role:** C++; embedded variational language, numerical library, and application toolboxes. Counted once as a monorepo.

The integration interface is a compact route into how mathematical notation becomes element and face assembly.

- **C1:** Integral evaluation exposes quadrature order and geometric mapping choices. Interior-face integrals introduce jump and average operators, making traces and penalty terms explicit for discontinuous Galerkin formulations.
- **C2:** `integrate` combines an integration range with an expression; the same structure covers cells, boundaries, and internal faces. It supports both scalar evaluation and expressions used in variational assembly rather than hard-coding one PDE.

**Technical entry point:** the [integration reference](https://docs.feelpp.org/dev/latest/reference/Integrals/integrate.html), including DG terms, geometry mappings, and local versus globally reduced evaluation. It is especially useful for engineers interested in the semantics of an embedded C++ numerical language.

### 14. [oomph-lib/oomph-lib](https://github.com/oomph-lib/oomph-lib)

**Language/role:** Primarily C++; object-oriented finite element and multiphysics framework.

Study its separation of geometric element behavior, physical equations, nodes, and global problem assembly.

- **C1:** Nodes distinguish pinned values from unknowns requiring equation numbers. Element-local to global equation mappings must preserve that distinction when assembling residuals and Jacobians; mesh connectivity uses node references rather than assuming a global node-number convention.
- **C2:** The documented hierarchy separates generalized elements, finite elements, geometric element families, and equation-specific behavior. This enables geometric machinery to serve multiple PDEs and lets nonstandard algebraic constraints participate in the larger problem.

**Technical entry point:** the [library design introduction](https://oomph-lib.github.io/oomph-lib/doc/intro/html/index.html), particularly the node, element, mesh, and inheritance discussions. Its value lies in showing the consequences of the object model for assembly, not merely listing supported physics.

### 15. [ElmerCSC/elmerfem](https://github.com/ElmerCSC/elmerfem)

**Language/role:** Primarily Fortran, with C/C++ components; multiphysics suite. The relevant subsystem is **`fem` and its reusable solver modules**.

The thermoelectric module provides a concrete view of an extensible Fortran solver lifecycle.

- **C1:** Transient static condensation requires retaining bubble-degree-of-freedom history. The source distinguishes nonlinear iterations from actual time-step transitions so the previous-step state is updated at the right moment, and documents the need for repeated solves to avoid lagging the condensed contribution.
- **C2:** `Model_t`, `Solver_t`, and shared assembly utilities organize initialization, bulk assembly, boundary assembly, Dirichlet enforcement, and solution. Individual physics modules implement local contributions within that common lifecycle.

**Technical entry point:** [`ThermoElectricSolver.F90`](https://github.com/ElmerCSC/elmerfem/blob/devel/fem/src/modules/ThermoElectricSolver.F90). This is a source-level example of framework reuse, not a claim that one module exercises every capability of Elmer.

## Compact and language-centered finite element libraries

### 16. [sfepy/sfepy](https://github.com/sfepy/sfepy)

**Language/role:** Python with C/Cython numerical components; finite element problem formulation and solution framework.

SfePy's term interface is worth studying as a bridge between declarative equations and explicit numerical kernels.

- **C1:** Terms distinguish unknown, test, material, and parameter arguments, as well as residual and derivative evaluation. Cell, facet, and facet-with-cell-connectivity modes have different semantics; the last is needed for full gradients on boundaries.
- **C2:** A `Term` subclass supplies argument preparation and an assembly function. The same contract covers a broad collection of weak forms and evaluation modes.
- **C3:** Numerical functions operate on preallocated element arrays and use either compiled routines or vectorized NumPy. The guide makes array shape and C-contiguous storage requirements explicit rather than leaving performance behavior hidden.

**Technical entry point:** the [developer guide](https://sfepy.org/doc/developer_guide.html), especially “How to Implement a New Term,” `get_fargs`, and the residual/matrix examples.

### 17. [kinnala/scikit-fem](https://github.com/kinnala/scikit-fem)

**Language/role:** Python; finite element assembly library built around NumPy/SciPy.

Study a relatively small set of mesh, element, basis, and form abstractions that still exposes the numerical machinery.

- **C1:** Degree-of-freedom sharing on nodes, edges, facets, and interiors encodes continuity. Form functions obey explicit element/quadrature array-shape contracts; facet bases also carry normals and boundary-specific data.
- **C2:** Forms receive discrete fields independently of the chosen mesh and element, making the assembly interface reusable across different approximation spaces.
- **C4:** The changelog documents changes across 2022–2026, including deprecation/removal sequences, compatibility aliases, Python-version transitions, and fixes for refinement, boundary matching, and periodic meshes. The project states its semantic-versioning scope in terms of documented or tested features.

**Technical entry points:** [advanced assembly and degree-of-freedom documentation](https://scikit-fem.readthedocs.io/en/latest/advanced.html) and the [repository changelog](https://github.com/kinnala/scikit-fem#changelog).

### 18. [evalf/nutils](https://github.com/evalf/nutils)

**Language/role:** Python; finite element and related numerical discretization framework using deferred array expressions.

Nutils offers a different architecture from either a conventional element-class hierarchy or an eager array assembly loop.

- **C1:** Evaluation distinguishes topology-local points from physical coordinates; geometry is itself an expression. Array shapes and differentiation therefore belong to the expression semantics, rather than being incidental properties of a sampled NumPy array.
- **C2:** Fields, geometry, basis functions, and their derivatives share a deferred expression representation that can be combined before evaluating at integration points.
- **C3:** Expression trees permit simplification and optimization before repeated evaluation. Keeping construction separate from execution provides an explicit place to reduce redundant work.

**Technical entry point:** the versioned [`nutils.evaluable` architecture/API documentation](https://docs.nutils.org/en/v9.1/nutils/evaluable/). Start with its explanation of deferred evaluation and topology-local arguments before exploring individual expression nodes.

### 19. [gridap/Gridap.jl](https://github.com/gridap/Gridap.jl)

**Language/role:** Julia; finite element framework expressed through native language abstractions.

Gridap is a useful comparison with frameworks that generate a separate low-level program from a variational DSL.

- **C2:** The authors organize the implementation around array, field, and map abstractions. Cellwise data, basis evaluation, and operations on physical fields compose through these interfaces rather than an equation-specific assembly engine.
- **C3:** Lazy cell arrays avoid materializing every intermediate value, while cached map evaluation reduces repeated allocation. Julia specialization compiles concrete combinations of these abstractions for a problem.

**Technical entry point:** the authors' [Gridap design paper](https://arxiv.org/pdf/2109.12818), particularly its lazy arrays and reusable evaluation-cache design. The paper describes the 2021 implementation generation. Separate Gridap ecosystem repositories are not counted as bundled core functionality or additional selections.

### 20. [Ferrite-FEM/Ferrite.jl](https://github.com/Ferrite-FEM/Ferrite.jl)

**Language/role:** Julia; finite element toolbox emphasizing explicit assembly and extensible data structures.

Its assembler interface gives a clear view of sparse storage, affine constraints, and parallel accumulation.

- **C1:** Constraint condensation implements transformations such as `C'KC`. Atomic assembly prevents conflicting global additions, but each task still needs its own assembler because scratch buffers are mutable. The documentation explicitly distinguishes concurrency safety from deterministic floating-point sums.
- **C2:** Custom assemblers and matrix formats implement common operations; the same constraint routines can work with standalone or blocked matrices.
- **C3:** Sparsity-pattern construction is separate from matrix allocation, allowing reuse. Storage-aware assembly can traverse sorted matrix entries alongside element entries, and CSC/CSR implementations share logic through an index-orientation abstraction.

**Technical entry point:** the [assembly developer documentation](https://ferrite-fem.github.io/Ferrite.jl/stable/devdocs/assembly/), including custom formats, constraint application, and atomic accumulation.

## Conservation laws, finite volumes, spectral methods, and differentiable simulation

### 21. [trixi-framework/Trixi.jl](https://github.com/trixi-framework/Trixi.jl)

**Language/role:** Julia; high-order PDE framework, especially discontinuous Galerkin discretizations of conservation laws.

Study how a numerical invariant influences operator composition rather than appearing only in a final error check.

- **C1:** The flux-differencing documentation derives the summation-by-parts structure and the role of symmetric two-point volume fluxes. Its example checks entropy change numerically, showing that conservation depends on the chosen volume and surface fluxes.
- **C2:** `DGSEM` combines basis order, surface flux, and volume integration strategy. `SemidiscretizationHyperbolic` then combines mesh, equations, initial/boundary conditions, and the spatial solver before producing an ODE problem for time integration.

**Technical entry point:** the [DGSEM flux-differencing tutorial](https://trixi-framework.org/TrixiDocumentation/dev/tutorials/DGSEM_FluxDiff/). The documented entropy behavior is conditional on the demonstrated formulation; it is not a blanket guarantee for every solver configuration.

### 22. [WIAS-PDELib/VoronoiFVM.jl](https://github.com/WIAS-PDELib/VoronoiFVM.jl)

**Language/role:** Julia; finite volume framework for coupled transport, reaction, and related PDE systems.

This smaller framework is particularly useful for connecting reusable physics callbacks with explicit conservation checks.

- **C1:** The terminal-flux example verifies a prescribed flux using an auxiliary test function. Its tests exercise all four combinations of sparse/dense unknown storage and edgewise/cellwise assembly.
- **C2:** Flux, reaction, and storage callbacks compose into `Physics` and `System`; physical parameters are carried separately as user data.
- **C4:** The 2021–2026 change history documents representation changes, callback deprecations followed by migration, and separation of mutable solver state into `SystemState`. It also records a multithreaded grid-access locking correction, connecting evolution to concrete correctness and complexity management.

**Technical entry points:** the [flux-conservation example and tests](https://wias-pdelib.github.io/VoronoiFVM.jl/dev/module_examples/Example125_TestFunctions1D/) and [change history](https://wias-pdelib.github.io/VoronoiFVM.jl/stable/changes/). The latter documents the move from the former `j-fu` ownership to WIAS-PDELib.

### 23. [DedalusProject/dedalus](https://github.com/DedalusProject/dedalus)

**Language/role:** Python/Cython; spectral PDE framework with distributed transforms.

Dedalus adds a distinct architectural family: global basis transforms rather than local finite element assembly.

- **C1:** A field's layout tracks which axes are in coefficient or grid space and which are local or distributed. A transform can execute only after the necessary axis becomes local; the order of layout changes is therefore a numerical and ownership invariant.
- **C2:** Distributor and layout abstractions coordinate multidimensional fields, transformations, and communication independently of a particular PDE.
- **C3:** Distributed transforms are implemented as a sequence of local transforms and MPI transposes. The documented process-mesh and layout construction explains where communication enters and how work is organized around it.

**Technical entry point:** the source-backed [`dedalus.core.distributor` reference](https://dedalus-project.readthedocs.io/en/latest/autoapi/dedalus/core/distributor/index.html), especially `Distributor`, `Layout`, and transform/transpose paths.

### 24. [usnistgov/fipy](https://github.com/usnistgov/fipy)

**Language/role:** Python; NIST finite volume framework for coupled PDEs.

FiPy is an accessible study of how equation terms map to cell-centered sparse systems.

- **C1:** The numerical documentation derives transient, convective, diffusive, and source contributions, including boundary-flux semantics and implicit versus explicit treatment. It also states a limitation: nonorthogonality can introduce errors in the described diffusion approximation.
- **C2:** Equation terms provide reusable building blocks that can be combined with variables, meshes, and solution methods for different transport problems.
- **C3:** Cell-centered storage and face coupling lead to sparse systems with limited local connectivity. The documentation relates the discretization choice to bandwidth and storage rather than making a universal speed claim.

**Technical entry point:** the [discretization and numerical approach](https://pages.nist.gov/fipy/en/latest/numerical/discret.html). Read its mesh-geometry assumptions alongside the term derivations when judging suitability for an application.

### 25. [clawpack/pyclaw](https://github.com/clawpack/pyclaw)

**Language/role:** Python and Fortran; reusable wave-propagation PDE solver framework, including the PetClaw parallel subsystem.

This is more than a thin kernel wrapper: the solver layer owns time advancement, boundary handling, state management, and failure recovery.

- **C1:** The base solver checks the CFL acceptance condition, backs up the solution before variable-size steps, and restores both state and time after rejection. Fixed-step runs fail explicitly when adaptation is impossible; time advancement also avoids accumulated roundoff in the fixed-step case.
- **C2:** A common solver interface coordinates boundary-condition implementations, pre-step hooks, and numerical step methods. Specialized solvers override the step operation while retaining reusable evolution logic.

**Technical entry point:** [`src/pyclaw/solver.py`](https://github.com/clawpack/pyclaw/blob/master/src/pyclaw/solver.py), especially `evolve_to_time`, acceptance/rejection, and ghost-cell boundary routines. The monorepo is counted once, including its parallel variant.

### 26. [AMReX-Codes/amrex](https://github.com/AMReX-Codes/amrex)

**Language/role:** C++ with Fortran interfaces/components; block-structured adaptive mesh refinement infrastructure for PDE applications.

AMReX is a framework for building solvers rather than a universal equation language. Its most instructive correctness machinery sits at coarse/fine mesh interfaces.

- **C1:** Fine and coarse levels can advance with different time steps. Flux registers accumulate time- and area-weighted flux mismatches, and refluxing applies the correction needed for conservation. Ghost filling also requires spatial and temporal interpolation with boundary handling.
- **C2:** `AmrCore`, mesh hierarchy hooks, distributed field containers, fill-patch operations, and flux registers provide reusable services for different application equations.
- **C3:** Block-structured data and level-local operations organize work around distributed patches; the architecture makes the necessary cross-level synchronization explicit.

**Technical entry point:** the [AmrCore and adaptive-advection implementation guide](https://amrex-codes.github.io/amrex/docs_html/AmrCore.html), particularly `FillPatch` and `FluxRegister`. Its interpolation caveats matter when extending conservation-preserving schemes.

### 27. [tum-pbs/PhiFlow](https://github.com/tum-pbs/PhiFlow)

**Language/role:** Python; differentiable PDE simulation framework with tensor-backend integration.

PhiFlow adds a useful perspective on representing geometry, fields, and implicit solves in simulations intended to participate in optimization workflows.

- **C1:** The fluid projection implementation handles obstacle masks, inactive cells, boundary-dependent pressure conditions, and pressure-system rank deficiency. It balances divergence when required before solving and subtracting the pressure gradient.
- **C2:** Field, geometry, obstacle, and `Solve` objects separate representation and solver configuration from the fluid operation. The pressure projection composes these objects instead of embedding a single fixed grid/solver arrangement.

**Technical entry point:** the source-expanded [fluid physics API](https://tum-pbs.github.io/PhiFlow/phi/physics/fluid.html), especially `make_incompressible`. The documentation explicitly describes a higher-order stencil tradeoff that disrupts exact operator consistency; this is a useful limitation to study, not an accuracy guarantee.

## Search coverage and limits

Discovery used substantially more than six distinct live query formulations. Search angles included distributed C++ FEM and hp adaptivity; Python weak-form compilers and assembly libraries; Julia FEM and conservation-law frameworks; object-oriented Fortran multiphysics; finite volume and block-structured AMR; spectral transforms; differentiable simulation; and Rust/lesser-known frameworks and official GitHub mirrors. Follow-up searches targeted degree-of-freedom constraints, assembly internals, operator APIs, conservation tests, and release/migration histories. Later broad searches increasingly returned already-covered projects, equation-specific applications, teaching repositories, or projects without a verified substantive GitHub upstream/mirror.

Every retained canonical GitHub repository page was opened, and each entry has additional opened primary technical material beyond its repository README. Sources include official API/developer documentation, actual source files, executable examples with tests, and papers written by framework developers. Search snippets, repository stars, and third-party summaries were not used as sufficient evidence for inclusion. C1–C4 assignments are engineering judgments drawn from the linked mechanisms; they are not claims of independently proven correctness or measured performance.

The selection deliberately excludes awesome lists, standalone tutorial repositories, generated bindings without substantial framework logic, pure mesh generators, and most application-specific CFD/structural codes. Supporting packages such as form languages, element tabulators, and linear-algebra backends were not separately counted merely because a listed framework depends on them. PETSc is the explicit exception in scope because its retained subsystem implements reusable mesh and PDE discretization abstractions. libMesh and MOOSE are retained as distinct framework layers with separate implementations, not as duplicate forks.

This is a selective survey rather than an exhaustive inventory. Boundary-element-only systems, meshfree methods, and neural PDE operator packages received less coverage. Some source pages could not be retrieved; retained entries use accessible technical alternatives. Versioned tutorials and older design papers are labeled where they provide historical architectural evidence. No repository code was installed or executed, benchmarks were not reproduced, and there is no blanket assertion that all repositories—or every documented subsystem—have the same maintenance status. GetFEM, FEMPAR, DUNE PDELab, and PETSc are explicitly identified as mirrors; GitHub contribution workflows and mirror freshness should be checked separately before development work.
