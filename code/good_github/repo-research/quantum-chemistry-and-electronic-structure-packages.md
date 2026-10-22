# Quantum chemistry and electronic structure packages

Research date: **2026-10-09**.

This selection covers **27 GitHub repositories** implementing molecular quantum chemistry, periodic electronic structure, correlated wavefunction solvers, semiempirical Hamiltonians, and the numerical libraries that make these calculations possible. The emphasis is on code an experienced engineer can study for numerical contracts, extensible scientific interfaces, and management of expensive computation. Molecular dynamics is included only where the repository contains a substantive electronic-structure engine. Each repository is counted once, including monorepos and official mirrors.

Criteria used below:

- **C1 — Difficult correctness:** numerical semantics, physical or representation invariants, concurrency, or consequential failure modes.
- **C2 — Reusable abstractions:** substantial interfaces or representations supporting multiple methods and applications.
- **C3 — Performance with structure:** identifiable architectural responses to memory, communication, or computational constraints.
- **C4 — Sustained evolution:** documented development over years together with testing, compatibility work, or complexity management.

The criterion assignments are engineering judgments grounded in the linked primary material. They are a selection guide, not a claim that every component is uniformly exemplary. Repository headings link to canonical GitHub pages opened during research; the implementation and documentation links provide starting points for deeper reading.

## Molecular frameworks and multireference suites

### [pyscf/pyscf](https://github.com/pyscf/pyscf)

**Language/role:** Python and C; a programmable molecular and periodic electronic-structure framework.

Study how a research library combines concise, composable method objects with explicit control over large numerical intermediates. Its objects retain settings and final results, while much of the computation lives in module-level functions.

- **C1:** Atomic-to-molecular-orbital integral transformations must preserve permutation symmetries across full and packed representations. The developer guide explains the different symmetry layouts, triangular packing, and conversion checks; confusing these conventions can silently change a Hamiltonian. [AO-to-MO implementation guide](https://pyscf.org/contributor/ao2mo_developer.html).
- **C2:** The common `kernel`, `run`, `set`, and `apply` conventions let methods participate in consistent workflows. Scanners update molecular dependencies when geometries change, a useful example of controlling scientific state without hiding it. [Design guide](https://pyscf.org/design.html).
- **C3:** The transformation layer provides both in-memory and out-of-core paths, with HDF5-backed access for intermediates that exceed RAM. The same AO-to-MO guide explains the distinction and common loading interface.

### [psi4/psi4](https://github.com/psi4/psi4)

**Language/role:** C++ and Python; molecular electronic-structure methods with a native numerical core and Python driver.

This is a strong study of the contracts underneath apparently ordinary matrix operations. The useful entry point is the [BLAS, LAPACK, and matrix programming guide](https://psicode.org/psi4manual/master/prog_blas.html), which connects storage conventions to quantum-chemical basis representations.

- **C1:** BLAS wrappers use row-major conventions while LAPACK interfaces retain column-major conventions. AO, symmetry-adapted, orthogonalized, and molecular-orbital bases also have distinct ordering and linear-dependency rules. Correct dimensions alone do not establish a correct calculation.
- **C2:** Shared matrix and vector types, symmetry blocks, and numerical wrappers give many electronic-structure methods a common implementation vocabulary.
- **C3:** Blocking matrices by irreducible representation and supporting large vector operations address actual computational scale while keeping symmetry and storage boundaries explicit in the API.

### [nwchemgit/nwchem](https://github.com/nwchemgit/nwchem)

**Language/role:** Primarily Fortran and C, with Python tooling; a broad computational-chemistry suite containing molecular and periodic electronic-structure implementations.

Study a scientific application organized around persistent calculation state. The [architecture description](https://nwchemgit.github.io/NWChem-Architecture.html) explains how tasks and independent modules communicate through the runtime database.

- **C1:** Restart semantics are part of the architecture: database contents survive between tasks and jobs. A restarted task should see the same relevant state as a task executed immediately after its predecessor; retained options must be explicitly unset when they are no longer intended.
- **C2:** Typed database entries, geometry and basis objects, and module boundaries decouple input interpretation from individual scientific methods. This makes the repository useful for studying extensibility in a large Fortran application.

The [developer guide](https://nwchemgit.github.io/Developer.html) is a second entry point for programming conventions, parallel infrastructure, and expectations for QA tests.

### [Molcas/OpenMolcas](https://github.com/Molcas/OpenMolcas)

**Language/role:** Primarily Fortran, with Python tooling; multiconfigurational and multireference quantum chemistry. **Official GitHub mirror:** the repository identifies GitLab as the main development location.

The relevant subsystem here is **RASSCF**. Its [method and implementation documentation](https://molcas.gitlab.io/OpenMolcas/sphinx/users.guide/programs/rasscf.html) exposes how a mathematically constrained wavefunction becomes a practical solver.

- **C1:** The active space is divided into orbital groups with different hole and electron restrictions. Spin-adapted configuration functions and the split graphical unitary group approach preserve constraints that an arbitrary determinant truncation could violate.
- **C2:** Complete, restricted, and generalized active-space treatments share a configurable multiconfigurational framework; state averaging supports several electronic states within the orbital optimization.
- **C3:** The implementation converts to determinant representations in selected inner loops, including sigma-vector and density-matrix work, while retaining the spin-adapted outer representation. This is a concrete example of choosing different representations for correctness and expensive kernels.

The repository warns that some older Molcas documentation describes features outside OpenMolcas; this entry concerns the documented RASSCF implementation.

### [qsimulate-open/bagel](https://github.com/qsimulate-open/bagel)

**Language/role:** C++; distributed molecular electronic structure, including relativistic and multireference methods.

The canonical repository is now under `qsimulate-open`; it describes BAGEL as the GPL version of QSimulate-QM. Its in-memory, distributed design makes it particularly interesting for studying the consequences of eliminating a disk-based intermediate interface.

- **C1:** The [Dirac–Hartree–Fock implementation guide](https://nubakery.org/scf/dhf.html) discusses four-component operators, kinetic or magnetic balance, Kramers symmetry, overlap linear dependencies, and convergence controls. These are representation and stability obligations, not merely choices of solver tolerance.
- **C3:** Density fitting is used in the relativistic implementation, while the repository explicitly targets distributed-memory execution and states that it is not optimized for workstation use. That combination makes memory ownership and distributed tensor work central architectural concerns.

The linked Nubakery documentation remains a useful architectural entry point, but its examples should be treated as version-specific; this report does not infer current release cadence from their availability.

### [VeloxChem/VeloxChem](https://github.com/VeloxChem/VeloxChem)

**Language/role:** Python and C++; molecular electronic structure and response calculations for spectroscopy.

Study the boundary between scientific workflow code and numerical kernels. The [source-structure guide](https://veloxchem.org/docs/source-struct/) follows an SCF driver into native computation, and the [program-structure guide](https://veloxchem.org/docs/program-struct/) maps the larger collection of drivers and supporting modules.

- **C2:** Molecular objects, basis objects, SCF drivers, response drivers, and iterative-solver components provide reusable building blocks for ground-state and response workflows. The common driver organization is useful to inspect when adding a new observable or response method.
- **C3:** Python coordinates the calculation, while C++ implements expensive one- and two-electron integral evaluation and exchange-correlation integration. The documented division shows where a high-level interface ends and compute-intensive work begins, rather than treating the language boundary as an incidental wrapper.

### [evangelistalab/forte](https://github.com/evangelistalab/forte)

**Language/role:** C++ and Python; strongly correlated and multireference electronic structure.

Forte is useful for studying solver composition. Its [Python API introduction](https://forte.readthedocs.io/en/latest/nb_api_intro.html) constructs a graph from molecular input through Hartree–Fock to an active-space solver, with explicit state and orbital-space specifications.

- **C1:** Charge, spin multiplicity, spatial symmetry, orbital counts per irreducible representation, and the requested number of roots jointly define the problem. The examples expose these contracts instead of allowing a method name to stand in for a complete wavefunction specification.
- **C2:** `MolecularModel`, Hamiltonian generation, Hartree–Fock nodes, and `ActiveSpaceSolver` nodes can be composed and reused. FCI and selected-CI calculations fit into the same workflow architecture, making the repository interesting beyond any one correlation method.

The inspected API tutorial is from the published 0.2.3 documentation; it supports the architectural assessment, not a guarantee that every example is unchanged on the current branch.

## Selected configuration interaction, tensor networks, and quantum Monte Carlo

### [QuantumPackage/qp2](https://github.com/QuantumPackage/qp2)

**Language/role:** Fortran generated through IRPF90, with OCaml and Python tooling; determinant-driven wavefunction development and CIPSI selected configuration interaction.

Study how representation choices make an irregular scientific algorithm tractable. The authors' [implementation paper, especially sections III and VII](https://arxiv.org/html/1902.08154v3), is unusually concrete about data structures; the [project documentation](https://quantum-package.readthedocs.io/en/master/) explains its role as a method-development environment.

- **C1:** Bitstrings encode occupied spin orbitals, but a fixed ordering and fermionic phase convention are also required. The integral hash must identify orbital quartets related by permutation symmetry without confusing distinct integrals.
- **C2:** Arbitrary determinant spaces, IRPF90-generated dependency management, and a plugin system support experimentation with multiple wavefunction methods.
- **C3:** In-memory integral lookup uses symmetry-aware hashing with locality-conscious buckets. Davidson iteration avoids treating the enormous determinant-space Hamiltonian as a conventional dense diagonalization problem.

The documentation explicitly distinguishes this development environment from a general-purpose production package optimized for every SCF workload.

### [block-hczhai/block2-preview](https://github.com/block-hczhai/block2-preview)

**Language/role:** C++ and Python; matrix-product-state and density-matrix-renormalization-group algorithms, including quantum-chemical Hamiltonians.

The [MPO reloading guide](https://block2.readthedocs.io/en/latest/developer/mpo-reloading.html) is an excellent entry point into the relationship between tensor-network objects, storage, and parallel execution.

- **C1:** A lazily loaded matrix-product operator depends on persistent, readable backing files. It cannot be simplified or parallelized as though all its data were resident; for parallel reloads, the documented procedure serializes the already-parallelized operators separately for each rank.
- **C2:** Matrix-product states, matrix-product operators, moving environments, and DMRG solvers are separate objects. Their composition supports reuse of a Hamiltonian across calculations and solver workflows.
- **C3:** Minimal-memory reload mode fetches operator and blocking data as sites are needed and releases them afterward. Serialization also avoids repeatedly rebuilding expensive Hamiltonians and the associated memory fragmentation.

### [sanshar/Dice](https://github.com/sanshar/Dice)

**Language/role:** C++ with Python integration; a monorepo containing correlated-electron methods. This entry focuses on its **semistochastic heat-bath configuration interaction (SHCI)** implementation.

Study the boundary between deterministic wavefunction selection and stochastic correction. The [SHCI getting-started and algorithm guide](https://sanshar.github.io/Dice/gettingstarted.html) explains selection thresholds, perturbative correction, and distributed execution.

- **C1:** Variational selection and perturbative correction use different thresholds. The semistochastic correction combines a deterministic contribution with a stochastic difference; the relationship among these terms matters for interpreting the final energy and sampling error.
- **C3:** Heat-bath selection reduces the determinant search, while the semistochastic treatment avoids making the entire perturbative space a deterministic storage problem. MPI and OpenMP provide additional execution structure.
- **C2:** The solver can consume an FCIDUMP Hamiltonian independently of the program that generated its orbitals and integrals, enabling reuse as an active-space solver.

The inspected guide contains older versioned examples; this is an architectural selection, not a claim that its installation commands match every current configuration.

### [hande-qmc/hande](https://github.com/hande-qmc/hande)

**Language/role:** Fortran, C, Python, and Lua; stochastic wavefunction and density-matrix methods, including FCIQMC, CCMC, and DMQMC.

HANDE is particularly valuable for studying how stochastic numerical software should be analyzed and tested.

- **C1:** Consecutive FCIQMC and CCMC estimators are correlated, so naïve independent-sample error bars are inappropriate. The [analysis guide](https://hande.readthedocs.io/en/latest/manual/analysis.html) explains blocking, equilibration selection, and the different treatment required for independently sampled DMQMC runs.
- **C2:** The reusable `pyhande` analysis library underlies lightweight command-line scripts and supports more complex, bulk analysis across calculation types and restarted output files.
- **C1, additional evidence:** The [test-suite guide](https://hande.readthedocs.io/en/latest/manual/tests.html) distinguishes exact trajectory comparisons from agreement in expectation. Integer width, precision, and processor layout can change the Markov chain. It also candidly documents a limitation of deterministic OpenMP QMC testing rather than claiming universal reproducibility.

### [QMCPACK/qmcpack](https://github.com/QMCPACK/qmcpack)

**Language/role:** Primarily C++, with Python tooling; real-space quantum Monte Carlo for electronic systems.

The [performance-portable driver design](https://qmcpack.readthedocs.io/en/develop/performance_portable.html) explains a substantial architectural transition: shared execution machinery for CPU and GPU simulations.

- **C2:** The driver layer separates the organization of walkers from the implementation of underlying computational tasks. Its unified interfaces reduce the need for distinct scientific algorithms in separate CPU and GPU drivers.
- **C3:** Walkers are distributed across MPI ranks and grouped into crowds and batches. Host threads drive batches, with computational work dispatched to the appropriate CPU or accelerator implementation. This exposes several useful parallelism levels rather than relying on a single global thread count.

The same guide describes input changes such as population settings when moving from older drivers. This is concrete compatibility material, although this entry does not assign C4 without a broader longitudinal review. The repository is counted once; its workflow tools are not separate selections.

## Periodic, plane-wave, finite-element, and multiresolution engines

### [cp2k/cp2k](https://github.com/cp2k/cp2k)

**Language/role:** Primarily Fortran with native accelerator support; electronic structure and atomistic simulation. The selected subsystem is **Quickstep's Gaussian and plane-wave DFT machinery**.

Study the connection between an approximation's error controls and its implementation. The [cutoff-convergence tutorial](https://manual.cp2k.org/trunk/methods/dft/cutoff.html) explains how Gaussian products are mapped onto a hierarchy of real-space grids.

- **C1:** `CUTOFF` and `REL_CUTOFF` control different things: grid resolution and assignment of Gaussian products to grid levels. Raising only one does not establish convergence. The tutorial demonstrates why the controls must be examined together.
- **C3:** Smooth, broad products can be handled on coarser grids while sharper products require finer grids. This multigrid organization reduces unnecessary work while retaining explicit accuracy controls.

The practical study value is the complete path from a mathematical representation to grid assignment, numerical convergence, and computation cost. Other CP2K simulation capabilities are not counted as additional repositories.

### [QEF/q-e](https://github.com/QEF/q-e)

**Language/role:** Primarily Fortran and C; the Quantum ESPRESSO suite of plane-wave and pseudopotential electronic-structure methods. **Official GitHub mirror:** development is hosted on GitLab.

The relevant core includes PW, phonon calculations, and shared numerical libraries. Start with the [parallelization architecture](https://www.quantum-espresso.org/Doc/user_guide/node20.html).

- **C1:** Communicator membership, rank ordering, and data distribution differ among images, k-point pools, band groups, plane-wave groups, FFT tasks, and linear-algebra groups. Correct local calculations still require compatible collective operations and redistribution boundaries.
- **C3:** The hierarchy distinguishes loosely coupled images and pools from tightly coupled operations within a pool. FFT task groups and square process grids for dense linear algebra address different limits on useful parallelism.
- **C2:** The repository separates shared FFT, Kohn–Sham solver, and linear-algebra components from scientific applications. This makes it useful for studying numerical infrastructure shared by a family of executables.

### [abinit/abinit](https://github.com/abinit/abinit)

**Language/role:** Primarily Fortran, with C and Python components; periodic DFT, response, and many-body electronic-structure calculations. **Official GitHub mirror:** the repository points to its primary GitLab development service.

ABINIT is a particularly good selection for studying numerical regression infrastructure in a large scientific application.

- **C1:** The [test-suite implementation guide](https://docs.abinit.org/developers/testsuite_howto/) describes separate absolute and relative tolerances, acceptable differing-line counts, chained calculations, and tests parameterized by MPI process count. A numerical test is a structured contract rather than a plain text diff.
- **C4:** The [project history](https://docs.abinit.org/about/history/) records the expansion from ground-state calculations through response functions, PAW, parallel FFT work, and a replaced build system across successive releases. Combined with the reusable `BaseTest`, `ChainOfTests`, and `TestSuite` infrastructure, this supports sustained evolution with explicit complexity management rather than an age-only maturity claim.

The test harness is an especially useful entry point for engineers maintaining algorithms whose answers vary slightly across compilers or parallel configurations.

### [JuliaMolSim/DFTK.jl](https://github.com/JuliaMolSim/DFTK.jl)

**Language/role:** Julia; a plane-wave density-functional toolkit with accessible mathematical and implementation layers.

Study how physical terms, discretization, and symmetry reduction remain visible in a high-level scientific codebase. The [periodic-problem guide](https://docs.dftk.org/dev/guide/periodic_problems/) introduces the model and plane-wave setting; the [symmetry developer guide](https://docs.dftk.org/stable/developer/symmetries/) follows symmetry through the calculation.

- **C1:** Reducing a k-point grid requires corresponding weights and symmetry operations on densities and other quantities. The worked comparison of calculations with and without symmetry also explains why adaptive diagonalization tolerances can produce different intermediate histories despite compatible final answers.
- **C2:** Models, plane-wave bases, k-points, Hamiltonians, and individual energy terms provide separable representations on which multiple methods can operate.
- **C3:** Irreducible k-point sampling reduces repeated work through an explicit symmetry mechanism, providing a comprehensible optimization with testable mathematical conditions.

### [shankar1729/jdftx](https://github.com/shankar1729/jdftx)

**Language/role:** C++ and CUDA; joint density-functional theory, including electronic systems coupled to fluid or electrochemical environments.

The [version 1.5.0 developer guide](https://jdftx.org/1.5.0/DevGuide.html) offers a detailed architectural map. It is a versioned design reference, so its class descriptions should be checked against the current checkout when implementing changes.

- **C2:** Shared minimization and Pulay machinery supports electronic, ionic, and fluid problems. `FluidSolver` subclasses, electronic state objects, and thin application front ends build on `libjdftx`, illustrating reuse across coupled physical models.
- **C3:** `ManagedMemory` centralizes host/device storage concerns, while real-space and reciprocal-space field types make representation changes visible. This concentrates accelerator and data-movement responsibilities instead of scattering them through every scientific method.

The distinguishing study opportunity is the composition of different physical subsystems using common numerical solvers, together with an explicit memory-management layer.

### [deepmodeling/abacus-develop](https://github.com/deepmodeling/abacus-develop)

**Language/role:** C++; ABACUS, a pseudopotential electronic-structure engine supporting plane-wave and numerical atomic-orbital bases.

Study how one application supports different basis representations without pretending they have identical accelerator behavior. The [GPU implementation guide](https://abacus.deepmodeling.com/en/latest/advanced/acceleration/cuda.html) identifies both class boundaries and data movement.

- **C2:** Plane-wave wavefunctions, Hamiltonian operations, Hamiltonian solvers, and diagonalization algorithms occupy distinct components such as `Psi`, `Hamilt`, and `HSolver`. These interfaces allow solver and execution choices within the same physical calculation.
- **C3:** The documented plane-wave path places major solver objects and kernels on the GPU, while charge-density transfers remain part of the SCF cycle. The atomic-orbital path accelerates a different subset, including grid integration and diagonalization. This is concrete evidence of performance design constrained by representation and residency.

The guide includes backend-specific restrictions; this entry does not generalize a single GPU configuration into a claim about all supported platforms.

### [dftfeDevelopers/dftfe](https://github.com/dftfeDevelopers/dftfe)

**Language/role:** C++; DFT-FE, adaptive finite-element electronic structure for all-electron and pseudopotential calculations.

This adds a spatial discretization family that differs substantially from Gaussian-orbital and global plane-wave engines. The repository documents its deal.II/p4est foundations and CPU/GPU execution options.

- **C2:** The [library-build design](https://github.com/dftfeDevelopers/dftfe/blob/publicGithubDevelop/MakeLibrary.md) describes real and complex library targets, exported public interfaces, generated configuration headers, and dependency visibility. These are substantive boundaries for embedding a large solver in another application, including the obligation to keep consumer build configuration consistent.
- **C3:** Adaptive finite elements allocate spatial resolution selectively, while distributed meshes and accelerator backends address the cost of large electronic-structure calculations. The library design exposes backend and scalar-type choices as build-level structure rather than an opaque executable-only configuration.

The study focus is adaptive-discretization infrastructure and the transition from an application to a reusable scientific library. No published system-size or speedup claim is treated here as an independently reproduced benchmark.

### [MRChemSoft/mrchem](https://github.com/MRChemSoft/mrchem)

**Language/role:** C++ and Python; molecular Hartree–Fock and DFT using multiresolution, multiwavelet representations.

The [input and numerical-control guide](https://mrchem.readthedocs.io/en/latest/users/user_inp.html) is unusually revealing about internal error budgets and distributed storage.

- **C1:** Nuclear smoothing, Poisson and Helmholtz operators, basis order, and SCF convergence interact with the overall requested precision. The guide distinguishes convergence of energy from convergence of orbitals and explains why numerical noise limits further iteration.
- **C3:** Dedicated MPI memory-bank processes store data instead of computing, exchanging computational capacity for a larger feasible problem. Shared potentials introduce a separate memory-versus-NUMA-access tradeoff.
- **C1, additional evidence:** A documented reproducibility mode uses more memory to make results invariant, within double precision, to the MPI process count. The normal mode instead targets agreement within the selected numerical precision. This distinction is useful when designing parallel scientific tests.

## Semiempirical and tight-binding implementations

### [grimme-lab/xtb](https://github.com/grimme-lab/xtb)

**Language/role:** Primarily Fortran, with a C API; extended tight-binding quantum-chemical methods and associated molecular calculations.

The [C API design](https://xtb-docs.readthedocs.io/en/latest/capi.html) is a strong example of exposing a stateful Fortran engine safely to other languages.

- **C1:** Environment, molecule, calculator, and results handles have distinct lifetimes. Errors remain attached to an environment and can block subsequent operations; topology-like molecular properties have different mutability rules from coordinates. Reusing results with incompatible dimensions or electronic settings is a documented hazard.
- **C2:** Opaque handles separate foreign-language callers from Fortran representation details while retaining reusable calculation objects. This supports embedding the same engine into geometry workflows and other host programs.

The engineering value is the explicit treatment of ownership, failure propagation, and reusable numerical state. The selected quantum-chemical implementation is not being equated with every force-field capability also shipped in the repository.

### [dftbplus/dftbplus](https://github.com/dftbplus/dftbplus)

**Language/role:** Primarily Fortran, with C and Python interfaces; density-functional tight-binding electronic structure.

Study how an electronic solver participates in a coupled calculation. The [Python API recipe](https://dftbplus-recipes.readthedocs.io/en/latest/interfaces/pyapi/pyapi.html) documents geometry updates, observables, and externally supplied electrostatic potentials.

- **C1:** A population-dependent external field must respond to the current electronic populations; consistent forces additionally require its spatial gradients. The API spells out population-sign conventions, array shapes, and atomic units, all of which can otherwise produce plausible but incorrect results.
- **C2:** Callbacks for potentials and gradients let a host program couple DFTB+ to polarizable surroundings. An arbitrary user-data object is passed back to the callback, avoiding a requirement to place the external model inside the solver's implementation.

This is a substantive engine with an embedding interface, not merely a Python wrapper around an unrelated executable. The callback path is a useful first subsystem to inspect.

### [tblite/tblite](https://github.com/tblite/tblite)

**Language/role:** Fortran with C and Python interfaces; a reusable implementation of extended tight-binding Hamiltonians intended for integration into other programs.

Tblite earns a separate entry because it implements the numerical model as a library shared across host applications. The [Fortran API guide](https://tblite.readthedocs.io/en/latest/api/fortran.html) describes object consistency, failure handling, and distributed work ownership.

- **C1:** Changing immutable structural properties requires reconstructing dependent objects. For parallel work, each interaction belongs to exactly one partition, and summing partition contributions must recover the whole calculation; the full SCF driver must perform reductions at the required stages.
- **C2:** Structure, calculator, context, logger, interaction containers, and partition objects have distinct responsibilities. Contexts permit customized output and error retrieval without exposing host-specific behavior throughout the model.
- **C3:** Interaction loops and neighbor-list blocks can be partitioned while some structure-dependent quantities remain replicated. The guide explicitly identifies this remaining serial or replicated work as a limit on scaling.

### [openmopac/mopac](https://github.com/openmopac/mopac)

**Language/role:** Primarily Fortran; semiempirical molecular-orbital calculations. The repository identifies itself as the official continuation of the commercial MOPAC line, not an unrelated historical fork.

The **MOZYME** subsystem provides a particularly clear numerical-performance case study.

- **C1:** Truncation and incomplete orbital rotations can gradually degrade orthogonality when localized orbitals are reused through many SCF calculations. The [detailed MOZYME manual](https://openmopac.net/Manual/mozyme.html) explains the resulting energy drift, the cost of reorthogonalization, and the need for a fresh final energy calculation in affected workflows.
- **C3:** The [solver guide](https://openmopac.net/guides/mozyme/) describes localized orbitals and sparse pseudodiagonalization as alternatives to conventional canonical-orbital work. Lewis-structure analysis supplies the initial guess and constrains the calculation to compatible closed-shell systems.

This is useful code to study precisely because the optimization has explicit applicability limits and numerical consequences. The report does not repeat historical hardware benchmarks as current performance estimates.

## Reusable integral and electronic-structure kernels

### [evaleev/libint](https://github.com/evaleev/libint)

**Language/role:** C++; a compiler and numerical library for Gaussian molecular integrals.

Libint is a substantive domain-specific code generator as well as a reusable runtime library. Start with its [compiler/library overview](https://github.com/evaleev/libint/wiki) and [modern C++ API guide](https://github.com/evaleev/libint/wiki/using-modern-CPlusPlus-API).

- **C1:** Shell contraction, Cartesian versus spherical functions, operator parameters, and multipole component ordering are part of the numerical contract. The API guide makes these conventions concrete rather than treating all integral buffers as interchangeable arrays.
- **C2:** `BasisSet`, `Shell`, and a common `Engine` abstraction support many one- and two-body operators. The generator can produce libraries tailored to angular momenta, derivative orders, and integral families.
- **C3:** Distinguishing the maximum supported angular momentum from the range receiving stronger generated optimization exposes a practical code-size and execution-cost tradeoff. The overview also documents high-precision reference testing as a way to scrutinize generated kernels.

### [sunqm/libcint](https://github.com/sunqm/libcint)

**Language/role:** C with a Common Lisp code generator; analytical Gaussian integrals, including Cartesian, spherical, and spinor representations.

The repository's operator-expression language and uniform integral-call interface are useful starting points for studying automated numerical-kernel generation.

- **C1:** Screening very small integrals can invalidate a bound that a caller expected to be conservative. The repository documents the cutoff interaction with Schwarz estimates, as well as numerical limitations of quadrature and angular momentum. These are consequential API semantics, not merely implementation details.
- **C2:** Symbolic operator descriptions generate families of C integral evaluators with a shared calling convention, supporting ordinary, derivative, and relativistic operators.
- **C4:** The [ChangeLog](https://github.com/sunqm/libcint/blob/master/ChangeLog) records years of concrete numerical and portability work: quadrature stability, Cartesian/spinor transformations, integer overflow, architecture-specific errors, and refactoring. It also records removal of erroneous integral functionality, evidence of complexity management rather than unqualified feature accumulation.

The ChangeLog should be read alongside the repository overview because some overview text describes older implementation details.

### [electronic-structure/SIRIUS](https://github.com/electronic-structure/SIRIUS)

**Language/role:** C++ with Fortran/Python interfaces and CPU/GPU backends; reusable electronic-structure infrastructure for pseudopotential plane-wave and full-potential calculations.

Study a library intended to supply computational building blocks to electronic-structure applications. The inspected design pages are from **SIRIUS 7.5.0**, so they are versioned architectural evidence.

- **C1:** The [Fourier and plane-wave normalization guide](https://electronic-structure.github.io/SIRIUS-doc/d7/d56/ft_pw.html) distinguishes normalized wavefunction basis states from Fourier expansions of density and potential. Dropping the associated volume or FFT normalization factors would change the physics while leaving array sizes valid.
- **C3:** The [k-point data-distribution guide](https://electronic-structure.github.io/SIRIUS-doc/d6/dc8/data_dist.html) describes local panels of block-cyclic matrices needed for distributed PBLAS/ScaLAPACK operations when wavefunction-related arrays cannot fit on one node.
- **C2:** The repository packages these electronic-structure operations as reusable classes and language interfaces, rather than requiring every host application to reproduce the same storage and numerical infrastructure.

## Coverage, search process, and limitations

Discovery used more than six distinct live search formulations, followed by opening official repositories and additional primary material. Search angles included:

- General molecular electronic-structure suites and Python/C++ frameworks.
- Multireference, relativistic, active-space, and response implementations.
- Selected CI, determinant-driven algorithms, tensor networks, and DMRG.
- Stochastic wavefunction and density-matrix methods, including analysis and testing.
- Periodic plane-wave, pseudopotential, and full-potential architectures.
- Adaptive finite-element and multiwavelet discretizations.
- Tight-binding, semiempirical, embedding, and foreign-language API designs.
- Gaussian integral generators, shared electronic-structure kernels, MPI layout, and GPU data residency.

Searches combined discovery terms with targeted queries for architecture, source organization, tests, numerical failure modes, and developer documentation. Additional broad queries increasingly repeated the same architecture families or surfaced orchestration tools and teaching implementations; a final semiempirical search added MOPAC. The selection exceeds the approximate 15–25 guide because the additional entries represent distinct numerical methods or reusable implementation layers, rather than forks or duplicate wrappers.

**Scope exclusions:** standalone input generators, workflow orchestrators, visualization tools, generic quantum-circuit frameworks, educational-only exercises, repository catalogs, and proprietary engines without inspectable substantive GitHub source were not retained. Candidates hosted elsewhere were omitted when an official substantive GitHub mirror was not established. OpenMolcas, Quantum ESPRESSO, and ABINIT are explicitly identified as mirrors. A solver and the integral library it uses can both appear because they contain distinct implementations at different architectural layers; a mirror and its upstream count only once.

**Evidence limits:** all 27 retained canonical GitHub pages were opened, and each entry has at least one additional opened primary source with relevant implementation, design, testing, or numerical material. Public GitHub API metadata requests encountered rate limits, so repository-page and official-documentation verification supplied the evidence; stars and push timestamps were not used as quality substitutes. No candidate code was executed, dependencies installed, or performance benchmark reproduced. Published manuals can lag current branches, especially the older or versioned BAGEL, Forte, Dice, JDFTx, and SIRIUS material. No blanket claim of active maintenance is made. C4 is used selectively where evolution is supported by concrete historical and maintenance evidence. Other omissions should not be interpreted as a negative assessment of the projects.
