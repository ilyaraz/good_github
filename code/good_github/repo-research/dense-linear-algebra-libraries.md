# Dense linear algebra libraries

Research date: **2026-10-09**.

This selection covers 25 substantial GitHub repositories implementing dense matrix arithmetic, factorizations, or reusable matrix abstractions. It spans CPU microkernels, embedded workloads, GPUs, shared and distributed memory, managed languages, generic scalar arithmetic, and exact finite fields. For broader numerical libraries, only the named dense linear algebra subsystem is assessed. These are study recommendations grounded in inspected code and documentation, not assurances that every component is exemplary or suitable for a particular deployment.

## Criteria

- **C1 — Difficult correctness:** numerical semantics, storage invariants, concurrency, exceptional inputs, or failure propagation require careful implementation.
- **C2 — Reusable abstractions:** substantial interfaces or representations support multiple algorithms and applications.
- **C3 — Performance with structure:** the implementation addresses concrete hardware or algorithmic constraints through identifiable architectural choices.
- **C4 — Sustained evolution:** dated development history is accompanied by compatibility work, testing, or explicit complexity management. Age or recent activity alone is insufficient.

## Foundational CPU libraries

### 1. [Reference-LAPACK/lapack](https://github.com/Reference-LAPACK/lapack)

**Fortran, with C interfaces; dense numerical algorithms and reference BLAS.** Study how precise numerical contracts are preserved while high-level factorizations delegate expensive work to interchangeable BLAS implementations.

- **C1:** `DGETRF` specifies pivot indices, overwritten factor storage, leading dimensions, and the distinction between invalid arguments and an exactly singular factor. Its blocked implementation adjusts local pivot and failure indices before updating the trailing matrix.
- **C3:** The same routine selects blocked or recursive factorization using an environment-dependent block size, then expresses updates through triangular solves and GEMM.
- **C4:** The repository records releases from 1992 through 2025 alongside a numerical test suite. `DGET01` reconstructs the pivoted factorization and measures a residual scaled by matrix size, norm, and machine epsilon.

Entry points: [LU implementation and contract](https://github.com/Reference-LAPACK/lapack/blob/master/SRC/dgetrf.f); [LU reconstruction test](https://github.com/Reference-LAPACK/lapack/blob/master/TESTING/LIN/dget01.f).

### 2. [OpenMathLib/OpenBLAS](https://github.com/OpenMathLib/OpenBLAS)

**C, assembly, and Fortran; optimized BLAS with bundled LAPACK.** Particularly useful for studying the interaction between processor dispatch, threading, scratch storage, and a long-established numerical interface. The development branch is `develop`; the README warns that `master` is outdated.

- **C1:** The usage documentation explains the internal buffer pool and why concurrent callers can exhaust resources even with a single-threaded build. This makes resource bounds and nested application/library parallelism concrete correctness concerns.
- **C3:** Runtime CPU selection, affinity controls, and configurable thread counts expose the division between portable interfaces and machine-specific execution.
- **C4:** The 2011–2026 changelog connects continued evolution to unit tests, BLAS edge-case compatibility, architecture fixes, and recent level-3/GETRF race corrections.

Entry points: [threading, buffers, and dispatch](https://github.com/OpenMathLib/OpenBLAS/blob/develop/USAGE.md); [dated change history](https://github.com/OpenMathLib/OpenBLAS/blob/develop/Changelog.txt).

### 3. [flame/blis](https://github.com/flame/blis)

**C99 and architecture-specific kernels; a framework for constructing BLAS implementations.** Study the boundary between the reusable matrix-operation machinery and the small kernels that need hardware specialization.

- **C2:** Contexts register kernels, block sizes, and preferences. External plugins can add operations and optimized implementations without requiring modifications to the BLIS source tree.
- **C3:** A control tree represents packing, partitioning, and computation choices. The plugin guide walks through changing those choices and registering architecture-specific kernels while retaining reference fallbacks. This is unusually explicit performance architecture, rather than an opaque collection of optimized routines.

Entry point: [plugin, context, and control-tree guide](https://github.com/flame/blis/blob/master/docs/PluginHowTo.md). BLIS and libflame are separate implementations at different layers of the dense algebra stack, not duplicate forks.

### 4. [flame/libflame](https://github.com/flame/libflame)

**C object-based algorithms, with Fortran/LAPACK compatibility code; dense factorizations.** Study algorithms expressed as matrix partitions and repartitions instead of extensive hand-written index arithmetic. The repository is retained for its architecture; this report makes no claim of a current release cadence.

- **C2:** `FLA_Obj` views and algorithm-control objects separate matrix partitions from the selected Cholesky, triangular-solve, and Hermitian-update subalgorithms.
- **C1:** The inspected blocked Cholesky variant translates a failing diagonal-block result back to the original matrix position and uses the correct conjugate-transpose update.
- **C3:** Block-size selection and subalgorithm controls are explicit inputs to the blocked traversal, making the performance policy separable from the mathematical update sequence.

Entry point: [blocked lower Cholesky variant 3](https://github.com/flame/libflame/blob/master/src/lapack/dec/chol/l/flamec/FLA_Chol_l_blk_var3.c).

## Specialized multiplication and embedded workloads

### 5. [giaf/blasfeo](https://github.com/giaf/blasfeo)

**C and assembly; BLAS and factorization routines for embedded optimization.** The distinguishing workload is matrices that fit in cache. Study how a library changes storage and calling conventions when packing overhead matters repeatedly across a sequence of small operations.

- **C3:** The documented panel-major format groups fixed-height panels with column-major elements inside each panel. The inspected GEMM selects hardware-specific microkernels and separate paths for aligned interiors and incomplete or offset panels.
- **C1:** GEMM handles submatrix offsets and remainder dimensions, and explicitly invalidates the destination's cached inverse diagonal. That cached-state invariant is easy to miss when studying only the arithmetic.
- **C2:** The repository offers both conventional BLAS/LAPACK interfaces and an API built around its own matrix representation.

Entry point: [panel-major double-precision operations, especially `blasfeo_hp_dgemm_nn`](https://github.com/giaf/blasfeo/blob/master/blasfeo_hp_pm/d_blas3_lib4.c). Matrix-format explanations are in the repository README.

### 6. [libxsmm/libxsmm](https://github.com/libxsmm/libxsmm)

**C with generated machine code and C++/Fortran interfaces; specialized small matrix kernels.** Focus on the dense GEMM subsystem rather than the repository's broader tensor and sparse operations. Study when dispatching a shape-specific kernel is preferable to a general BLAS call.

- **C3:** Explicit kernel dispatch lets callers amortize specialization overhead across repeated calls; batching can communicate upcoming operands for prefetching. Larger problems require caller-side tiling.
- **C1:** The matrix-multiplication guide documents generated-code displacement limits and stack-scratch limits, with reference-kernel fallback when a shape exceeds them.
- **C2:** Kernel handles and typed interfaces expose specialized computation without requiring callers to manipulate generated instructions directly.

Entry point: [matrix multiplication, dispatch, batching, and size limits](https://github.com/libxsmm/libxsmm/blob/main/documentation/libxsmm_mm.md). This is a specialized kernel library, not a complete LAPACK replacement.

### 7. [bluss/matrixmultiply](https://github.com/bluss/matrixmultiply)

**Rust; a focused GEMM backend for real and complex matrices.** Its deliberately narrow operation set makes the macro/microkernel design more approachable than a complete solver library.

- **C1:** The representation permits negative and zero input strides, but mutable matrix elements must not alias. Thread-safety also depends on distinct destination matrices. These are explicit obligations at an unsafe pointer-based boundary.
- **C3:** Portable kernels coexist with CPU-specific variants and runtime feature selection. Packing, architecture parameters, threading, and kernels occupy separate modules; compile-time configuration can tune cache-sensitive blocking parameters.
- **C2:** Arbitrary row and column strides support views and both common storage orders without requiring each consumer to write its own GEMM.

Entry point: [representation, safety contracts, and module organization](https://github.com/bluss/matrixmultiply/blob/master/src/lib.rs). The README also records portability and alignment fixes; complex multiplication is explicitly described as experimental.

## GPU and shared-memory task execution

### 8. [CNugteren/CLBlast](https://github.com/CNugteren/CLBlast)

**C++ and OpenCL; tunable BLAS across accelerator vendors.** Study the tradeoff between general kernels and preprocessing that makes a more constrained kernel possible.

- **C3:** Direct GEMM handles the original problem in one kernel. Indirect GEMM adds preprocessing/postprocessing to satisfy alignment, size, offset, and transpose assumptions. The guide explains why the extra data movement may be worthwhile for larger problems but costly for smaller ones.
- **C1:** Direct kernels explicitly handle incomplete tiles. Correctness tests compare results with a CPU BLAS or clBLAS reference and provide expanded-coverage modes.
- **C2:** C and C++ interfaces leave device buffers and transfers under caller control while offering a broad BLAS operation set.

Entry points: [GEMM design](https://github.com/CNugteren/CLBlast/blob/master/doc/details_gemm.md); [correctness testing](https://github.com/CNugteren/CLBlast/blob/master/doc/testing.md). The README discloses device-specific and FP16 testing limitations.

### 9. [icl-utk-edu/magma](https://github.com/icl-utk-edu/magma)

**C/C++, CUDA/HIP, and Fortran support; heterogeneous dense factorizations and solvers.** This is the ICL-hosted GitHub codebase; some build documentation still refers to its earlier Bitbucket location. Study CPU/GPU cooperation and expert interfaces for workspace and execution control.

- **C1:** GPU LU preserves partial-pivoting and singularity contracts while adding allocation failures, device storage, execution queues, and hybrid/native modes to the interface.
- **C3:** The LU implementation contains explicit decisions for small-matrix CPU execution and transposed versus nontransposed GPU paths. It makes data movement and blocking part of algorithm selection.
- **C4:** The project's dated release history documents repeated solver additions, platform support, and removal of previously deprecated interfaces. The 2026 release removes the legacy sparse subsystem; dense algorithms are the focus here.

Entry points: [GPU LU implementation](https://github.com/icl-utk-edu/magma/blob/master/src/zgetrf_gpu.cpp); [official release history](https://icl.utk.edu/magma/).

### 10. [icl-utk-edu/plasma](https://github.com/icl-utk-edu/plasma)

**C with OpenMP and Fortran interfaces; tiled dense linear algebra on multicore CPUs.** Study how a factorization becomes a dependency graph while numerical kernels remain separately testable and replaceable. The inspected GitHub branch is `main`; the README retains historical QUARK/Bitbucket transition text.

- **C3:** Tiled Cholesky expands into diagonal factorization, triangular solves, Hermitian updates, and GEMM tasks. The library controls task parallelism and documents the need to avoid competing multithreaded BLAS execution.
- **C1:** The core Cholesky task declares an OpenMP `inout` dependency over its matrix storage, checks sequence status, and translates LAPACK failure information into the enclosing asynchronous request.
- **C2:** Tile descriptors and sequence/request objects provide common machinery for multiple decompositions.

Entry points: [tiled Cholesky traversal](https://github.com/icl-utk-edu/plasma/blob/main/compute/pzpotrf.c); [dependent task and failure propagation](https://github.com/icl-utk-edu/plasma/blob/main/core_blas/core_zpotrf.c).

## Distributed dense matrices

### 11. [Reference-ScaLAPACK/scalapack](https://github.com/Reference-ScaLAPACK/scalapack)

**Fortran and C with MPI; distributed-memory dense solvers.** Study the explicit representation of global matrices whose elements live in different processes and local memory layouts.

- **C2:** Matrix descriptors combine global shape, block sizes, process-grid context, source coordinates, and local leading dimension. The same representation underlies distributed BLAS and solver routines.
- **C1:** `PDGETRF` distinguishes global and local arguments, validates block alignment and square blocking, represents distributed pivoting, and encodes descriptor errors separately from scalar-argument errors and singularity.
- **C3:** The implementation is a blocked right-looking LU using parallel level-3 BLAS, with communication/grid operations visible beside the numerical work.

Entry point: [distributed LU and descriptor contract](https://github.com/Reference-ScaLAPACK/scalapack/blob/master/SRC/pdgetrf.f). The repository lists releases through 2026; describing it as universally abandoned would be inaccurate.

### 12. [icl-utk-edu/slate](https://github.com/icl-utk-edu/slate)

**C++ with MPI, OpenMP, and GPU backends; distributed dense operations and solvers.** Study how tile abstractions connect distributed communication to CPU/GPU task execution.

- **C2:** Matrix, Hermitian-matrix, and triangular-matrix views let algorithms express structure and submatrices while execution targets remain template/configuration choices.
- **C1:** Cholesky coordinates task dependencies, tile broadcasts, device workspace, and failure indices across distributed tiles.
- **C3:** Its lookahead option, separately allocated kernel queues, and batched device resources expose how the critical panel work is overlapped with trailing updates.

Entry point: [distributed Cholesky implementation](https://github.com/icl-utk-edu/slate/blob/master/src/potrf.cc). The [official project page](https://icl.utk.edu/slate/) confirms this GitHub repository and documents ABI/deprecation changes and solver checks. ScaLAPACK compatibility is an integration concern, not evidence that the two implementations are duplicates.

### 13. [eth-cscs/DLA-Future](https://github.com/eth-cscs/DLA-Future)

**C++ with asynchronous execution, MPI, and CPU/GPU support; distributed dense eigensolvers and factorizations.** Study a matrix representation whose access operations participate in scheduling rather than immediately returning unrestricted references.

- **C1:** Tiles expose read-only and read/write senders. Sub-pipelines sequence their accesses between earlier and later operations on the original matrix; retiling must respect block divisibility and tile ownership.
- **C2:** The matrix abstraction separates distribution, allocation mapping, device type, and tile access. It supports preallocated external storage as well as owned storage.
- **C3:** Column-major, block, and tile allocation layouts permit storage decisions to vary without rewriting each numerical algorithm.

Entry point: [matrix storage, tile access, and sub-pipeline implementation](https://github.com/eth-cscs/DLA-Future/blob/master/include/dlaf/matrix/matrix.h). The README distinguishes asynchronous C++ interfaces from synchronous C/ScaLAPACK-like interfaces; the latter cover a documented subset.

### 14. [elemental/Elemental](https://github.com/elemental/Elemental)

**C++ with MPI and optional extended-precision arithmetic; historical distributed dense linear algebra.** **Historical/unmaintained:** the project's own deprecation notice says it has not been maintained since 2016 and points to an LLNL fork. It remains a substantive original implementation, retained for study rather than a maintenance recommendation.

- **C2:** `DistMatrix` supports families of elementwise and blockwise distributions, including replicated and process-row/process-column layouts, over generic scalar types.
- **C1:** Its distribution layer checks grid and distribution agreement. ScaLAPACK descriptor conversion explicitly rejects incompatible distributions and nonzero cuts instead of silently constructing an invalid mapping.

Entry point: [distributed matrix families and interoperability checks](https://github.com/elemental/Elemental/blob/master/include/El/core/DistMatrix.hpp). Focus on the dense subsystem; optimization, lattice reduction, and sparse-direct functionality are outside this entry. No downstream fork is counted separately.

## Rust and C++ matrix abstractions

### 15. [dimforge/nalgebra](https://github.com/dimforge/nalgebra)

**Rust; generic dense vectors, matrices, and decompositions.** Study how one API accommodates compile-time dimensions, dynamic dimensions, owned buffers, and borrowed views. The relevant subsystem is general matrix storage and algebra, beyond its graphics/geometry uses.

- **C2:** `Matrix<T, R, C, S>` separates element type, row and column dimensions, and storage. Matrix/vector aliases and allocator constraints reuse that representation across many shapes and operations.
- **C1:** Unsafe storage traits require buffers to remain compatible with their declared dimensions. Contiguity and unchecked slice access have explicit safety contracts; exposing safe buffer resizing could violate matrix invariants and cause undefined behavior.

Entry points: [generic matrix representation](https://github.com/dimforge/nalgebra/blob/main/src/base/matrix.rs); [storage safety contracts](https://github.com/dimforge/nalgebra/blob/main/src/base/storage.rs). These boundaries are more instructive than assuming Rust alone makes every custom storage implementation safe.

### 16. [sarah-quinones/faer-rs](https://github.com/sarah-quinones/faer-rs)

**Rust; dense matrix decompositions and low-level numerical kernels.** **Official retained GitHub mirror:** the README explicitly says development moved to Codeberg and the GitHub repository remains a mirror. Study the separation between ergonomic matrix operations and explicit allocation/parallelism control.

- **C2:** Owning `Mat` and lightweight `MatRef`/`MatMut` views support high-level decompositions over a lower-level API with memory and threading controls.
- **C3:** The design paper describes BLIS-style multiplication, CPU-feature dispatch, SIMD handling of generic scalar representations, and fused memory-bound kernels that avoid extra matrix passes.
- **C1:** The documented decomposition choices include pivoted LU/QR and Bunch–Kaufman LDLT, exposing numerical choices beyond a single generic solve routine.

Entry point: [in-repository design paper](https://github.com/sarah-quinones/faer-rs/blob/main/paper.md). Its future-work statements are historical design context, not assertions that planned APIs or scalar support have shipped.

### 17. [boostorg/ublas](https://github.com/boostorg/ublas)

**C++ headers; generic matrix/vector expressions and factorizations.** Study the dense matrix and LU subsystem rather than the repository's tensor extension. It illustrates reusable algebra expressed through views and expression interfaces.

- **C2:** LU operates on generic matrix types through row/column proxies, projected ranges, triangular adaptors, and outer products. The implementation does not require a single concrete dense container.
- **C1:** Pivoted factorization maintains a permutation object, reports the first singular pivot, and includes optional reconstruction checks against the original matrix after applying row swaps.

Entry point: [generic LU, permutation handling, and reconstruction assertions](https://github.com/boostorg/ublas/blob/develop/include/boost/numeric/ublas/lu.hpp). This is a useful abstraction study; no claim is made that its generic kernels outperform specialized BLAS implementations.

## Go, Java, and .NET numerical libraries

### 18. [gonum/gonum](https://github.com/gonum/gonum)

**Go with some assembly; `mat`, BLAS, and LAPACK subsystems of a broader numerical monorepo.** Study the interaction between a small matrix interface and concrete, allocation-conscious operations.

- **C2:** Matrix, symmetric, and triangular interfaces interoperate with dense containers, implicit transpose wrappers, and reusable factorization objects. BLAS/LAPACK backends can be selected behind common wrappers.
- **C1:** The package documents receiver/input aliasing rules, restrictions on partially overlapping storage, and hazards when resetting matrices sharing backing arrays.
- **C3:** Operations inspect concrete capabilities to choose GEMM, symmetric multiplication, or matrix-vector routines; empty receivers reuse available backing storage when resized.

Entry point: [matrix interfaces, dispatch, invariants, and aliasing guide](https://github.com/gonum/gonum/blob/master/mat/doc.go). The monorepo counts once; unrelated statistics, graph, and optimization packages are not the basis for inclusion.

### 19. [lessthanoptimal/ejml](https://github.com/lessthanoptimal/ejml)

**Java; dense real/complex matrices, decompositions, and layered APIs.** Study its dense modules, where procedural operations, `SimpleMatrix`, and symbolic equations share lower-level algorithms.

- **C1:** The inspected Householder QR scales a column by its largest magnitude before computing a norm, handles a zero column explicitly, and stores reflectors separately from the reconstructed orthogonal matrix.
- **C3:** The implementation reuses work arrays and reorders loops for row-major cache access, documenting the small/large-matrix tradeoff.
- **C4:** The 2009–2026 changelog records numerical repairs, concurrent-workspace bugs, zero-sized-matrix tests, benchmark expansion, and Java module compatibility work.

Entry points: [Householder QR implementation](https://github.com/lessthanoptimal/ejml/blob/SNAPSHOT/main/ejml-ddense/src/org/ejml/dense/row/decomposition/qr/QRDecompositionHouseholder_DDRM.java); [change history](https://github.com/lessthanoptimal/ejml/blob/SNAPSHOT/change.txt). The source branch is `SNAPSHOT`.

### 20. [optimatika/ojAlgo](https://github.com/optimatika/ojAlgo)

**Java; dense matrix stores and decompositions within a broader mathematics/optimization library.** Study how generic scalar arithmetic and specialized primitive storage meet at decomposition factories.

- **C2:** Dense LU implementations share decomposition machinery across doubles, complex values, rationals, quaternions, and extended-precision values using store factories and numerical-operation hooks.
- **C1:** The LU API distinguishes successful factorization from a solvable system and explicitly warns that pivot-ratio rank/singularity judgments can be unreliable after rounding; it provides reconstruction checks with a numerical context.
- **C3:** The double-precision factory selects raw or dense implementations according to matrix shape and storage limits, rather than using one path universally.

Entry points: [LU contract and factory selection](https://github.com/optimatika/ojAlgo/blob/develop/src/main/java/org/ojalgo/matrix/decomposition/LU.java); [dense LU implementation](https://github.com/optimatika/ojAlgo/blob/develop/src/main/java/org/ojalgo/matrix/decomposition/DenseLU.java). Optimization solvers are not separately counted.

### 21. [mathnet/mathnet-numerics](https://github.com/mathnet/mathnet-numerics)

**C# with F# integration and optional native providers; dense linear algebra within Math.NET Numerics.** Study how a managed matrix hierarchy exposes reusable storage while allowing optimized numerical providers underneath.

- **C2:** Dense matrices use a distinct column-major storage object and participate in the broader matrix/factorization hierarchy. Native providers can replace the managed numerical implementation behind that API.
- **C3:** The dense multiply override dispatches dense/dense operations directly to the provider, handles diagonal operands separately, and falls back to generic matrix behavior for other representations.
- **C1:** Constructors distinguish copying from directly binding an external array; the latter deliberately shares mutations with the caller, making ownership semantics part of the public contract.

Entry point: [dense storage construction and multiplication dispatch](https://github.com/mathnet/mathnet-numerics/blob/master/src/Numerics/LinearAlgebra/Double/DenseMatrix.cs). This entry assesses the linear algebra subsystem, not the entire numerical package or its current release cadence.

## Julia and alternative numerical domains

### 22. [JuliaLang/LinearAlgebra.jl](https://github.com/JuliaLang/LinearAlgebra.jl)

**Julia; the standard-library linear algebra package, now in its own repository.** Study multiple dispatch as the boundary between generic algorithms and BLAS/LAPACK specialization. The main Julia monorepo is not counted again.

- **C2:** LU is a reusable factorization object with factors, permutations, and status. Strided BLAS-compatible matrices dispatch to LAPACK, while abstract matrices can use the generic factorization implementation and explicit pivot strategies.
- **C1:** The implementation distinguishes an unpivoted zero-pivot failure from singularity, supports checked/allowed-singular modes, and documents in-place failures when a result cannot be represented by the input element type.
- **C3:** In-place factorization and factor-storage reuse make allocation policy visible to callers rather than requiring repeated allocation.

Entry point: [LU representation, dispatch, pivoting, and compatibility annotations](https://github.com/JuliaLang/LinearAlgebra.jl/blob/master/src/lu.jl). Development-branch documentation can describe features requiring a newer Julia version; it is not a blanket installed-version guarantee.

### 23. [JuliaArrays/StaticArrays.jl](https://github.com/JuliaArrays/StaticArrays.jl)

**Julia; statically sized arrays with specialized small dense linear algebra.** Study the matrix multiplication subsystem and the balance between runtime work and compiler-generated code.

- **C2:** Static size information works across immutable matrices, mutable matrices, and wrappers around ordinary storage while retaining the `AbstractArray` interface.
- **C3:** Generated multiplication selects unrolled, loop-based, and generic approaches. Chunked matrix-vector construction reduces generated-code growth and avoids temporary mutable containers.
- **C1:** Multiplication checks dimensions and preserves structural wrappers for valid triangular/diagonal products, so specialization must respect algebraic structure as well as shape.

Entry point: [generated matrix multiplication and structure propagation](https://github.com/JuliaArrays/StaticArrays.jl/blob/master/src/matrix_multiply.jl). The README explicitly warns that large static arrays can stress the compiler and become slower; the intended study case is small dense matrices.

### 24. [JuliaLinearAlgebra/GenericLinearAlgebra.jl](https://github.com/JuliaLinearAlgebra/GenericLinearAlgebra.jl)

**Julia; numerical factorizations for generic scalar types, including high precision.** The README presents the package partly as an experimentation environment. Study how textbook decompositions are adapted beyond the scalar types supported by conventional BLAS/LAPACK.

- **C2:** Generic singular-value, eigenvalue, QR, and Cholesky functionality extends Julia's algebra interfaces to element types such as `BigFloat`; support varies by operation and type.
- **C1:** The SVD code implements bidiagonal iteration, estimates small singular values to decide whether shifting is safe, uses a Demmel–Kahan zero-shift path to preserve relative accuracy, and explicitly handles zero singular values when adjusting vectors.

Entry point: [generic SVD iteration, deflation, and sign handling](https://github.com/JuliaLinearAlgebra/GenericLinearAlgebra.jl/blob/master/src/svd.jl). This is a particularly readable numerical-semantics study, without assuming that arbitrary user-defined scalars satisfy every algorithm's requirements.

### 25. [linbox-team/fflas-ffpack](https://github.com/linbox-team/fflas-ffpack)

**C++ templates with BLAS integration; exact dense linear algebra over finite fields and integers.** Focus on the dense FFLAS/FFPACK subsystem. Its inclusion broadens the category beyond floating-point semantics while retaining the same substantial matrix-kernel and factorization concerns.

- **C1:** GEMM conversion must preserve field representations, including balanced modular values. Lazy-reduction helpers track bounds and decide when modular reduction is needed before additions/subtractions exceed representable limits.
- **C2:** Field parameters, element types, and algorithm/mode helpers separate the algebraic domain from matrix operations.
- **C3:** The implementation combines recursive Winograd choices and numerical-kernel integration; the project also provides autotuning of algorithm thresholds.

Entry point: [field-aware GEMM conversion and reduction logic](https://github.com/linbox-team/fflas-ffpack/blob/master/fflas-ffpack/fflas/fflas_fgemm.inl). Exact arithmetic creates different correctness obligations from tolerance-based floating-point comparisons.

## Coverage, search process, and limitations

Discovery used more than six distinct live-web query families: BLAS/LAPACK foundations; Rust factorization and strided multiplication; distributed MPI/eigensolver libraries; Java/Go/.NET matrices; Julia static and generic arithmetic; embedded/cache-resident kernels; OpenCL/CUDA libraries; C++ expression-template libraries and official mirrors; and finite-field/exact algebra. Follow-up searches checked less prominent projects and batched GPU alternatives. Later broad searches mostly added overlapping implementations or candidates needing a separate maturity audit, rather than changing the architectural coverage of this selection. This is a curated guide, not an exhaustive census.

Each retained canonical GitHub repository was opened and also checked through the GitHub API. At least one additional primary implementation or architectural document was read for every entry. No retained repository was marked archived by the API at research time; that flag does not establish maintenance. Elemental's explicit deprecation notice and faer's explicit mirror notice therefore take precedence over simplistic activity heuristics. GitHub source reads also corrected stale search/cache branch information, notably PLASMA's `main` and nalgebra's `main`.

Important exclusions and boundaries:

- Thin/generated bindings, tutorials, lists, and duplicate forks were omitted. BLAS++/LAPACK++ are relevant integration layers, but this selection emphasizes substantive implementations and matrix abstractions.
- NumPy/SciPy, machine-learning tensor frameworks, sparse-only libraries, and application-specific numerical solvers were not added merely because they call dense BLAS.
- Armadillo was omitted because its [official FAQ identifies the move from GitHub to GitLab](https://arma.sourceforge.net/faq.html). Searches for Eigen and Blaze were not used to justify treating an arbitrary GitHub fork as the canonical project. This makes the C++ convenience-library coverage less complete than the overall ecosystem.
- KBLAS and Octavian surfaced as additional specialized candidates. Their batch-GPU and Julia-GEMM roles overlap covered families; their omission is a selection decision, not a negative quality judgment.
- Some web-rendered source pages and historical documentation were inaccessible; direct read-only GitHub API file retrieval supplied implementation evidence instead. No candidate code was installed, compiled, cloned, or executed. Testing claims describe inspected tests/history, not tests run during this research.

The criteria assignments and suggested study paths are grounded engineering judgments inferred from the linked material. They do not certify numerical accuracy across all inputs, benchmark superiority, current platform compatibility, or a guaranteed maintenance horizon. Links to development branches may change after the research date.
