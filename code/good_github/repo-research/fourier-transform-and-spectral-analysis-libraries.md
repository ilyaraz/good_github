# Fourier transform and spectral analysis libraries

Research date: **2026-10-09**.

This selection covers **28 GitHub repositories** implementing Fourier transforms or substantial spectral-analysis machinery: CPU and embedded FFTs, GPU kernel generation, distributed and sparse transforms, nonuniform FFTs, short-time transforms, and statistical spectrum estimation. Broader numerical repositories are included only for named subsystems. The emphasis is on code an experienced engineer can study, not a performance ranking or a claim that every component is exemplary.

Repository identities, default branches, and archive status were checked through GitHub repository pages or the GitHub API. Each entry also uses an opened implementation file or substantive primary document. Links to development branches describe the inspected source, which can differ from released packages. None of the selected repositories was marked archived at inspection; that does not establish active maintenance. Specific historical and mirror qualifications appear below.

Criteria legend:

- **C1 — Difficult correctness:** numerical semantics, invariants, concurrency, adversarial inputs, or failure modes.
- **C2 — Reusable abstractions:** substantial interfaces and components supporting multiple applications.
- **C3 — Performance with structure:** concrete computational or memory constraints addressed through an understandable design.
- **C4 — Sustained evolution:** evidence of years of changes together with compatibility, testing, or complexity management. Repository age and stars do not establish this criterion.

## CPU, embedded, and language-native transform engines

### 1. [FFTW/fftw3](https://github.com/FFTW/fftw3)

**C, with an OCaml code generator; general-purpose FFT engine.** Study the separation between transform descriptions, planning, and execution. This is the authors' development repository: much of the distributable C code is generated, so the GitHub checkout is not equivalent to a release tarball.

- **C1:** Planning can overwrite input; real-data layouts, strides, alignment, and unnormalized round trips are explicit API contracts. These are practical examples of numerical semantics that cannot be hidden behind a simple `fft()` signature. **C3:** Measured and estimated planning costs, planning-rigor flags, and reusable “wisdom” make the setup-versus-execution tradeoff visible. Read the [reference manual source](https://github.com/FFTW/fftw3/blob/master/doc/reference.texi).
- **C4:** The [NEWS history](https://github.com/FFTW/fftw3/blob/master/NEWS) records multiple generations of SIMD, compiler, MPI, and ABI fixes, including an alignment-sensitive real-transform crash with a reproducing test and signed-zero assumptions broken by compiler optimization. This supports studying long-term compatibility engineering, not merely an old project.

### 2. [mreineck/pocketfft](https://github.com/mreineck/pocketfft)

**C++; compact multidimensional FFT/DCT/DST implementation.** This is an author-maintained GitHub contribution mirror of the project hosted at MPCDF GitLab; count it once. Its `cpp` branch is particularly useful for studying a substantial numerical engine contained in one header.

- **C1:** Axis validation, repeated-axis rejection, input/output stride consistency, and accurate twiddle construction expose the numerical and memory-layout invariants. The [header implementation](https://github.com/mreineck/pocketfft/blob/cpp/pocketfft_hdronly.h) also separates real and complex plans.
- **C2/C3:** Shape/stride/axis interfaces cover multidimensional and noncontiguous arrays; specialized codelets and Bluestein plans address different factorizations. Optional plan caching and a thread pool are explicit mechanisms rather than hidden external dependencies. The [repository's interface and implementation notes](https://github.com/mreineck/pocketfft/blob/cpp/README.md) explain why caching is disabled by default and where vectorization and threading apply.

### 3. [mborgerding/kissfft](https://github.com/mborgerding/kissfft)

**C; small mixed-radix FFT library.** A useful contrasting study to large planners: recursive decomposition and the butterfly kernels remain close enough to inspect together.

- **C1:** Fixed-point division macros appear inside butterfly stages, while forward/inverse signs and generic-radix temporary allocation require careful handling. These details are visible in the [FFT implementation](https://raw.githubusercontent.com/mborgerding/kissfft/master/kiss_fft.c).
- **C3:** Dedicated radix-2/3/4/5 kernels feed a generic fallback; the optional OpenMP path parallelizes independent top-level subtransforms before recombination. The same source makes the scheduling boundary and memory traffic understandable. The [project guide](https://github.com/mborgerding/kissfft) describes the floating-point, fixed-point, and build configurations. Small scope should not be confused with supporting every size equally efficiently.

### 4. [marton78/pffft](https://github.com/marton78/pffft)

**C/C++; SIMD FFT and FFT-based convolution.** This is a substantive fork of Julien Pommier's PFFFT, not a second listing of an unchanged copy: additions include double precision, AVX support, convolution functionality, and restructured sources.

- **C1/C3:** The API distinguishes an internal spectrum order optimized for inverse transforms and convolution from conventional ordered output. Alignment, scaling, workspace ownership, and read-only setup sharing across threads are explicit. Read the [single-precision API header](https://github.com/marton78/pffft/blob/master/include/pffft/pffft.h); its restrictions and workspace warnings are part of the design.
- **C4:** The [history and upstream commit map](https://github.com/marton78/pffft/blob/master/README.md#history--origin--changes) document years of independent extensions, selected upstream portability fixes, and CTest integration. This is a useful example of managing a numerical fork without losing track of its ancestor.

### 5. [ejmahler/RustFFT](https://github.com/ejmahler/RustFFT)

**Rust; SIMD-aware arbitrary-length FFT engine.** Study how a safe public trait interface fronts architecture-specific algorithms and algorithm composition.

- **C2:** `FftPlanner` returns shared `Arc<dyn Fft<T>>` objects and reuses internal data across planning calls. Its intermediate `Recipe` representation describes a transform before constructing the executable algorithm graph. Read [the planner](https://github.com/ejmahler/RustFFT/blob/master/src/plan.rs).
- **C3:** Planner dispatch chooses available SIMD implementations, while scalar recipes compose mixed-radix, Good–Thomas, Rader, Bluestein, and small butterflies. The [API documentation](https://docs.rs/rustfft/latest/rustfft/) explains factorization-sensitive costs and why bypassing the planner can bypass SIMD. It also makes the caller's normalization responsibility explicit.

### 6. [wendykierp/JTransforms](https://github.com/wendykierp/JTransforms)

**Java; real and complex multidimensional transforms.** Study the implementation cost of supporting primitive Java arrays, large-array storage, arbitrary lengths, and parallel execution within one library.

- **C1:** Real-spectrum packing, input offsets, inverse scaling, and separate integer/long indexing paths create concrete correctness obligations. The [double-precision 1D implementation](https://github.com/wendykierp/JTransforms/blob/master/src/main/java/org/jtransforms/fft/DoubleFFT_1D.java) documents the layouts alongside executable code.
- **C2/C3:** A reusable transform instance precomputes tables and selects split-radix, mixed-radix, or Bluestein plans. The same implementation integrates concurrency utilities and large-array overloads rather than exposing only a single array-in/array-out example. It is a substantial Java adaptation with its own execution and storage architecture, despite drawing on earlier FFT algorithms.

### 7. [gonum/gonum](https://github.com/gonum/gonum)

**Go; the `dsp/fourier` and internal FFTPACK subsystems.** Count the monorepo once. Study a native Go numerical API built over a translated and extended FFTPACK implementation.

- **C1:** Odd/even real-spectrum packing, Nyquist handling, frequency indexing, length validation, and unnormalized inverse semantics are visible in [the public transform implementation](https://github.com/gonum/gonum/blob/master/dsp/fourier/fourier.go). The [FFTPACK tests](https://github.com/gonum/gonum/blob/master/dsp/fourier/internal/fftpack/fftpack_test.go) compare against original-Fortran golden values, direct DFTs, and round trips over many lengths.
- **C2/C3:** `FFT` and `CmplxFFT` retain work arrays and factorization data; `Reset` reuses capacity, and caller-provided destinations avoid repeated allocations. The API cleanly separates coefficient generation, reconstruction, and frequency/index helpers.

### 8. [indutny/fft.js](https://github.com/indutny/fft.js)

**JavaScript; compact radix-4/radix-2 FFT engine.** This is an older, narrowly scoped implementation: repository metadata showed its last push in March 2023. It is retained as an inspectable JavaScript performance study, without a current-maintenance claim.

- **C1:** The implementation rejects unsupported sizes and aliased input/output buffers, reconstructs conjugate symmetry for real transforms, and scales the inverse explicitly. Read [the complete transform engine](https://github.com/indutny/fft.js/blob/master/lib/fft.js).
- **C3:** Precomputed trigonometric tables and bit-reversal patterns feed separate complex and real radix-4 paths. The [API guide](https://github.com/indutny/fft.js) encourages caller-owned storage to reduce garbage collection. Its power-of-two-only restriction is important; this is not a general arbitrary-length planner.

### 9. [ARM-software/CMSIS-DSP](https://github.com/ARM-software/CMSIS-DSP)

**C and architecture intrinsics; embedded DSP, specifically `Source/TransformFunctions`.** Study how FFT mathematics changes when fixed-point arithmetic, instruction sets, and tightly constrained buffers become first-class concerns.

- **C1:** The [Q15 complex FFT source](https://github.com/ARM-software/CMSIS-DSP/blob/main/Source/TransformFunctions/arm_cfft_q15.c) documents input/output fixed-point formats and required scaling by transform size. It also distinguishes the Neon buffer API from the in-place interface and optional bit reversal used by other paths.
- **C3:** MVE vector butterflies, rearranged twiddle tables, staged downscaling, and specialized radix dispatch are all inspectable in that source. The [project build guidance](https://github.com/ARM-software/CMSIS-DSP) shows how implementations are selected for Cortex targets and datatypes. The relevant study unit is the transform subsystem, not an endorsement of every DSP routine.

### 10. [kfrlib/kfr](https://github.com/kfrlib/kfr)

**C++; the DFT module of a broader DSP framework.** Study the boundary between convenient vector operations and explicit execution resources.

- **C1/C2:** Reusable plans support real/complex and multidimensional transforms, but packing format, normalization, buffer overlap, and concurrent scratch ownership remain explicit contracts. The [DFT guide](https://github.com/kfrlib/kfr/blob/main/docs/docs/dft/dft.md) explains CCs versus Perm layouts and sharing immutable plans with separate execution storage.
- **C3:** Plans choose mixed-radix, four-step, or Bluestein implementations; caller-owned scratch avoids per-call allocations. The [cache implementation](https://github.com/kfrlib/kfr/blob/main/include/kfr/dft/cache.hpp) reveals mutex-protected plan reuse and the additional allocations incurred by convenience functions. This makes API convenience and steady-state execution cost directly comparable.

## GPU transform planning and kernel generation

### 11. [DTolm/VkFFT](https://github.com/DTolm/VkFFT)

**C/C++ header library with generated GPU kernels; multiple compute backends.** Study a transform compiler that targets Vulkan, CUDA, HIP, OpenCL, Level Zero, and Metal.

- **C2/C3:** Initialization inspects the device, constructs per-axis plans, generates kernel text, and invokes the selected runtime compiler. Multi-stage algorithms can produce multiple kernels per axis. The [API guide source](https://github.com/DTolm/VkFFT/blob/master/documentation/VkFFT_API_guide.tex) explains that pipeline and resource lifetime.
- **C1:** The same guide makes axis-order differences from FFTW, complex storage, batching, scaling, and real-transform layouts explicit. The [project overview](https://github.com/DTolm/VkFFT) describes Rader/Bluestein fallbacks, memory-transfer reduction, and precision choices, including half-precision storage with single-precision computation. Those mechanisms support the selection; benchmark superiority claims are not adopted here.

### 12. [ROCm/rocm-libraries](https://github.com/ROCm/rocm-libraries)

**C++/HIP; the `projects/rocfft` subsystem.** This is the current repository location for rocFFT. The old `ROCm/rocFFT` repository announces its move and is not counted separately.

- **C1:** Real inverse transforms require Hermitian symmetry; odd/even lengths, planar/interleaved storage, and in-place strides affect physical buffer requirements. Read [the real-data design guide](https://github.com/ROCm/rocm-libraries/blob/develop/projects/rocfft/docs/how-to/real-data.rst).
- **C3:** The engine combines built-in kernels with plan-specific runtime compilation. Compiled kernels are cached within a process and can be persisted for reuse across processes. The [runtime-compilation guide](https://github.com/ROCm/rocm-libraries/blob/develop/projects/rocfft/docs/how-to/runtime-compilation.rst) makes initialization cost and cache lifetime understandable. Only rocFFT is evaluated here; unrelated ROCm libraries do not supply its qualifying evidence.

### 13. [clMathLibraries/clFFT](https://github.com/clMathLibraries/clFFT)

**C++/OpenCL; portable FFT planning and generated kernels.** Historical reference: repository metadata showed its last push in October 2022, although it was not archived. Useful for studying a vendor-independent OpenCL design; current device compatibility was not tested.

- **C1/C2:** Plans encapsulate dimensions, strides, batches, scaling, and array formats while retaining OpenCL context references. The library documents thread-safe plan operations and asynchronous enqueue behavior, including the caller's responsibility for queue synchronization. Read [the API/architecture document](https://github.com/clMathLibraries/clFFT/blob/master/src/library/mainpage.h).
- **C3:** That document explains cached OpenCL binaries and an optional constrained path that avoids additional device allocation. The [library source tree](https://github.com/clMathLibraries/clFFT/tree/master/src/library) separates plan management, enqueueing, Stockham generation, transposes, and binary lookup, providing a navigable architecture for the performance mechanisms.

## Distributed and sparse transforms

### 14. [icl-utk-edu/heffte](https://github.com/icl-utk-edu/heffte)

**C++/MPI; distributed FFT orchestration across CPU and GPU backends.** Study the data-distribution layer surrounding local FFT engines.

- **C2:** `box3d` describes each rank's input/output region, while templated `fft3d` and `fft3d_r2c` objects present a shared interface to several backend libraries. Raw buffers, vector-like containers, precision choices, and optional workspaces fit the same decomposition model.
- **C3:** `plan_options` exposes point-to-point versus all-to-all communication and strided versus contiguous local transforms. The [basic-usage architecture guide](https://github.com/icl-utk-edu/heffte/blob/master/doxygen/basic_usage.md) explains which work belongs to MPI redistribution and which belongs to FFTW, MKL/oneMKL, cuFFT, or rocFFT. This is substantial distributed execution machinery, not merely generated bindings.

### 15. [2decomp-fft/2decomp-fft](https://github.com/2decomp-fft/2decomp-fft)

**Fortran/MPI; pencil decomposition, distributed FFTs, and related array services.** Study how a reusable decomposition library supports both spectral and other distributed solvers.

- **C1:** Transform inputs and outputs must have compatible pencil orientations; dimensions need not divide the processor grid evenly, which introduces load imbalance. The [HOWTO](https://github.com/2decomp-fft/2decomp-fft/blob/dev/HOWTO.md) also documents deferred-I/O buffer lifetime, a concrete failure mode for applications reusing transform work arrays.
- **C2/C3:** Generic real/complex transpose interfaces, separate decomposition/FFT/I/O modules, and interchangeable local FFT backends serve multiple solver designs. The [repository guide](https://github.com/2decomp-fft/2decomp-fft) describes CUDA-aware MPI/NCCL GPU support and rank/decomposition-aware testing. Follow the `dev` branch used by the current repository, rather than counting older copies separately.

### 16. [mpi4py/mpi4py-fft](https://github.com/mpi4py/mpi4py-fft)

**Python/Cython and MPI; distributed transforms and distributed NumPy arrays.** Study how configurable global redistributions compose with local numerical transforms.

- **C1:** Changing transform order changes which axis is distributed and which real-transform dimension is shortened. The [parallel-transform guide](https://github.com/mpi4py/mpi4py-fft/blob/master/docs/source/parallel.rst) works through unequal local shapes, forward normalization, and reconstruction checks rather than treating a distributed array as a local ndarray.
- **C2/C3:** `PFFT`, `DistArray`, and subcommunicators support slab and pencil layouts, mixed FFT/DCT/DST operations, and collapsed local axes to reduce intermediate work. The same guide explains padding for convolution. Its older examples contain NumPy spelling that may need adaptation; the architectural explanation remains the study target.

### 17. [eth-cscs/SpFFT](https://github.com/eth-cscs/SpFFT)

**C++/MPI/OpenMP with CUDA/ROCm support; sparse-frequency 3D FFTs.** This adds a distinct problem shape: only selected Fourier coefficients are retained, as in spherical cutoffs in materials simulation.

- **C1:** A frequency-domain z-column must reside on one rank; real transforms impose additional Hermitian/index restrictions. Thread safety depends on separate execution resources and MPI thread support. These contracts are detailed in the [implementation/usage notes](https://github.com/eth-cscs/SpFFT/blob/master/docs/source/details.rst).
- **C2/C3:** `Grid` owns reusable resources and `Transform` associates sparse indices with them. Reference counting preserves resource lifetime. The [interface design](https://github.com/eth-cscs/SpFFT/blob/master/README.md) and details document distinguish buffered `Alltoall`, compact `Alltoallv`, and datatype-based `Alltoallw` exchanges, including precision-versus-communication-volume tradeoffs.

## Nonuniform Fourier transforms

### 18. [flatironinstitute/finufft](https://github.com/flatironinstitute/finufft)

**C++/CUDA with several language interfaces; precision-targeted NUFFTs.** The repository includes both FINUFFT and the integrated cuFINUFFT implementation; the older separate cuFINUFFT repository is not an additional project here.

- **C1:** GPU spreading must accumulate contributions from irregular points without races. The [GPU implementation document](https://github.com/flatironinstitute/finufft/blob/master/docs/impl_gpu.rst) explains per-thread kernel evaluation, barriers, disjoint shared-memory updates, and atomic accumulation into the global grid.
- **C2/C3:** The library supplies standard NUFFT types in multiple dimensions and interfaces. Its output-driven GPU strategy assigns blocks to grid tiles and batches point contributions to reduce global-memory traffic. The [project overview](https://github.com/flatironinstitute/finufft) establishes the supported transform family; the implementation document supplies the concrete optimization structure.

### 19. [NFFT/nfft](https://github.com/NFFT/nfft)

**C; nonequispaced transforms and related transform families.** Study a broader mathematical library spanning NFFT/NNFFT, nonequispaced sine/cosine transforms, spherical/rotation-group variants, and iterative reconstruction.

- **C1:** The [NFFT kernel](https://github.com/NFFT/nfft/blob/develop/kernel/nfft/nfft.c) distinguishes forward and adjoint sums, includes direct-transform implementations, and explicitly partitions adjoint accumulation into disjoint output ranges for parallel safety. The adjoint is not presented as a general inverse.
- **C2/C3:** Plan-based computation and selectable kernel-precomputation strategies expose memory-versus-recomputation tradeoffs. The [project guide](https://github.com/NFFT/nfft/blob/develop/README.md) identifies reusable transform modules and iterative inverse methods; the kernel shows full, partial, and on-demand interpolation-weight paths. FFTW provides local uniform transforms, while the nonequispaced machinery is implemented here.

### 20. [jipolanco/NonuniformFFTs.jl](https://github.com/jipolanco/NonuniformFFTs.jl)

**Julia; native CPU/GPU type-1 and type-2 NUFFTs.** Study a Julia implementation using AbstractFFTs and KernelAbstractions rather than a language binding to FINUFFT.

- **C1:** Separate real/complex plan-data types encode different Fourier storage shapes. Accuracy depends on kernel choice, support width, and oversampling; the [accuracy document](https://github.com/jipolanco/NonuniformFFTs.jl/blob/master/docs/src/accuracy.md) includes an explicit direct-sum reference calculation and parameter sweep.
- **C2/C3:** The [plan implementation and detailed API](https://github.com/jipolanco/NonuniformFFTs.jl/blob/master/src/plan.jl) expose multiple simultaneous fields, spatial blocking/sorting, CPU lock-versus-atomic accumulation, and GPU global/shared-memory strategies. Callbacks fuse operations into transform stages to reduce extra memory passes. These are concrete mechanisms; hardware-independent performance equivalence is not assumed.

### 21. [mmuckley/torchkbnufft](https://github.com/mmuckley/torchkbnufft)

**Python/PyTorch; differentiable Kaiser–Bessel NUFFT operators.** Study how a numerical transform is integrated with automatic differentiation and tensor execution.

- **C1:** The [autograd implementation](https://github.com/mmuckley/torchkbnufft/blob/main/torchkbnufft/_autograd/interp.py) saves interpolation state and uses the corresponding adjoint in backward propagation. Inspecting its returned gradients also clarifies that this is not a promise of differentiation with respect to every argument.
- **C2/C3:** Table interpolation, sparse interpolation matrices, and Toeplitz-embedded forward/adjoint compositions provide different reusable operator paths. The [operation-mode guide](https://github.com/mmuckley/torchkbnufft/blob/main/README.md) explains batching over coils, sensitivity-map integration, device/dtype consistency, and amortizing repeated reconstruction work with precomputed kernels.

### 22. [pynufft/pynufft](https://github.com/pynufft/pynufft)

**Python with CPU and accelerator paths; planned min-max-interpolation NUFFT.** Study a decomposition of the transform into scaling, oversampled FFT, and sparse interpolation, with a reverse path and iterative solvers.

- **C2:** Geometry planning separates image dimensions, oversampled-grid dimensions, interpolation support, and transformed axes. The [CPU implementation](https://github.com/pynufft/pynufft/blob/master/nufft/_nufft_class_methods_cpu.py) exposes forward, adjoint, self-adjoint, and solver-facing operations rather than a single transform call.
- **C3:** Planning materializes CSR interpolation and its conjugate transpose, precomputes scaling and copy indices, and then reuses them. This makes preprocessing cost and sparse-matrix storage tradeoffs inspectable. The [project description](https://github.com/pynufft/pynufft/blob/master/README.md) establishes the min-max algorithm and accelerator scope; the CPU implementation is the evidence assessed here, not a claim that all backends have identical behavior.

## Spectral estimation and time-frequency analysis

### 23. [scipy/scipy](https://github.com/scipy/scipy)

**Python/C/C++/Fortran monorepo; specifically `scipy.signal.ShortTimeFFT`.** Count SciPy once. This entry concerns the windowed-transform and reconstruction layer, distinct from the separately listed PocketFFT engine.

- **C1:** The [ShortTimeFFT implementation](https://github.com/scipy/scipy/blob/main/scipy/signal/_short_time_fft.py) computes canonical dual windows, checks numerical invertibility, rejects unsuitable window types, and handles overlap, padding, and spectrum conventions. Reconstruction is expressed as inverse transforms weighted by a dual window and overlap-added.
- **C2:** A parameterized transform object supports analysis, synthesis, different frequency layouts, and alternative dual-window constructions. The [tests](https://github.com/scipy/scipy/blob/main/scipy/signal/tests/test_short_time_fft.py) exercise invalid configurations, scaling, odd/even sizes, and reconstruction. This is a strong study of turning time-frequency mathematics into a reusable, testable API.

### 24. [JuliaDSP/DSP.jl](https://github.com/JuliaDSP/DSP.jl)

**Julia; specifically periodogram, spectrogram, and multitaper analysis.** Study configuration types that carry numerical conventions and preallocated execution state together.

- **C1:** `MTConfig` validates sample counts, FFT and taper dimensions, positive sampling frequency, and the incompatibility of complex input with a one-sided transform. Its normalization accounts for taper energy and taper weights. Read [the multitaper implementation](https://github.com/JuliaDSP/DSP.jl/blob/master/src/multitaper.jl).
- **C2/C3:** The same module reuses FFT plans, input/output work arrays, and tapers across periodograms, spectrograms, cross spectra, and coherence. In-place methods make allocation control visible. Its documentation explicitly says adaptive multitaper weighting is not supported by the cited `mt_pgram` interface; do not infer feature parity with every other multitaper library.

### 25. [cokelaer/spectrum](https://github.com/cokelaer/spectrum)

**Python with native support routines; Fourier and parametric PSD estimation.** Study the shared state model surrounding distinct estimators, and compare autoregressive spectral estimation with periodogram-based approaches.

- **C1:** The public Burg implementation recursively updates complex reflection coefficients, prediction errors, residual variance, and optional model-selection criteria; it rejects nonpositive estimated variance. Read [the Burg implementation](https://github.com/cokelaer/spectrum/blob/main/src/spectrum/burg.py). That file also labels a private faster alternative as having incorrect `rho`, so it should not be treated as an interchangeable validated path.
- **C2:** [The PSD abstractions](https://github.com/cokelaer/spectrum/blob/main/src/spectrum/psd.py) coordinate sampling rate, frequency ranges, one-/two-sided conventions, Fourier versus parametric estimators, and invalidation when configuration changes. The selection is for these concrete numerical and abstraction problems, not uniform code quality throughout the package.

### 26. [gaprieto/multitaper](https://github.com/gaprieto/multitaper)

**Python; Thomson, sine, and quadratic multitaper analysis.** A substantive Python implementation of the author's multitaper methods, useful for studying uncertainty and estimator corrections beyond computing an FFT magnitude.

- **C1:** [The numerical utilities](https://github.com/gaprieto/multitaper/blob/main/multitaper/utils.py) implement adaptive spectral weights, effective degrees of freedom, jackknife intervals, line tests, and quadratic corrections. The adaptive loop updates weights from eigenspectra and leakage terms and uses a relative-change stopping criterion.
- **C2/C3:** [The estimator classes](https://github.com/gaprieto/multitaper/blob/main/multitaper/mtspec.py) retain tapers, eigenvalues, eigenspectra, weights, and normalization state for further analysis. Callers can supply precomputed DPSS data, and vectorized weight updates avoid nested per-frequency Python loops. Inspect convergence and degenerate-data behavior when adapting this scientific code; it was not executed in this review.

### 27. [Eden-Kramer-Lab/spectral_connectivity](https://github.com/Eden-Kramer-Lab/spectral_connectivity)

**Python with NumPy/CuPy execution; multivariate frequency-domain estimation.** Study the progression from windowed Fourier coefficients to spectral matrices and directed connectivity measures.

- **C1:** [Minimum-phase decomposition](https://github.com/Eden-Kramer-Lab/spectral_connectivity/blob/master/src/spectral_connectivity/minimum_phase_decomposition.py) implements Wilson factorization, causal projection, per-sub-spectrum convergence, conjugate symmetry, and failure handling for rank-deficient inputs. It distinguishes convergence of iterates from actual reconstruction accuracy—an especially useful numerical-engineering lesson.
- **C2/C3:** [The transform layer](https://github.com/Eden-Kramer-Lab/spectral_connectivity/blob/master/src/spectral_connectivity/transforms.py) represents tapering and time/frequency parameters separately from downstream measures. The decomposition code also uses real FFTs only when the symmetry condition holds and isolates unhealthy members of a batch. This is relevant spectral infrastructure even though its motivating community is electrophysiology.

### 28. [preraulab/multitaper_toolbox](https://github.com/preraulab/multitaper_toolbox)

**MATLAB, Python, R, and Rust; multitaper spectra and spectrograms.** Study an algorithm maintained across several execution environments, with especially concrete evidence in its Python batch path.

- **C1:** A NaN invalidates its whole overlapping window, while an all-zero segment remains zero. [Regression tests](https://github.com/preraulab/multitaper_toolbox/blob/master/python/test_nan_windows.py) compare batched and single-window behavior across detrending and weighting choices and verify the affected time windows.
- **C3:** [The spectrogram implementation](https://github.com/preraulab/multitaper_toolbox/blob/master/python/multitaper_spectrogram_python.py) chunks windows to bound memory, batches threaded real FFTs, and retains a separate per-window path for adaptive weights. It also has an optional Rust path whose supported weighting modes are checked explicitly. This gives a concrete study of optimizing an analysis routine while preserving its missing-data contract.

## Coverage, search process, and limits

Discovery used live web searches followed by direct GitHub pages/API reads and primary documentation. More than six meaningfully different formulations were used, including:

- CPU algorithm/planner searches: “FFT library GitHub FFTW pocketfft kissfft architecture” and comparisons of FFTW, PocketFFT, PFFFT, and RustFFT.
- GPU searches: “GPU FFT library GitHub VkFFT rocFFT clFFT,” followed by runtime compilation and repository-migration checks.
- Distributed searches: MPI FFT libraries, heFFTe/PFFT, slab/pencil decomposition, and sparse-frequency transforms.
- Nonuniform searches: FINUFFT/NFFT/PyNUFFT, differentiable NUFFTs, and native Julia implementations.
- Language/community searches: Rust planners, Java JTransforms, Go FFTPACK, JavaScript FFTs, and embedded fixed-point/SIMD libraries.
- Spectral-analysis searches: multitaper, Welch, parametric spectrum estimation, Julia DSP, and neuroscience/geoscience toolboxes.

Later searches increasingly returned already-covered algorithm families, bindings, benchmark collections, and application-specific packages. The list was extended beyond 25 because native Julia NUFFTs and sparse distributed FFTs supplied distinct architectures. It remains selective: PFFT, FFTPACK variants, other Julia NFFT packages, and larger imaging/DSP frameworks are not all enumerated. Their absence is not a negative quality assessment.

Excluded from independent counts were the old rocFFT location, the separately hosted cuFINUFFT now integrated into FINUFFT, duplicate Spectrum/2DECOMP forks, ordinary language wrappers around an already-listed engine, benchmark-only repositories, tutorials, and awesome lists. Binary vendor FFT implementations were not substituted with GitHub examples and presented as open implementation repositories. PocketFFT's official contribution mirror and PFFFT's substantive fork are explicitly qualified above.

Criterion assignments and “what to study” recommendations are engineering judgments grounded in the linked material. No candidate code was run, no dependencies were installed, and no performance figures were independently measured. Testing claims describe inspected tests, not successful local test runs. The search did not audit every numerical edge case, all accelerator backends, licensing suitability, or release-to-development compatibility. In particular, “not archived” and recent repository activity were not used as substitutes for C4 evidence.
