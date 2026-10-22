# Multidimensional array and tensor libraries

Research date: 2026-10-09

This report selects 25 GitHub repositories implementing reusable multidimensional arrays, tensor operations, or substantial array execution systems. It covers dense storage and views, accelerator backends, labeled and irregular arrays, and distributed or symmetry-aware tensors. For broader frameworks, the relevant array subsystem is identified; the repository is counted once. The emphasis is on engineering mechanisms worth studying, rather than popularity or installation recommendations.

Criteria are engineering judgments grounded in the linked primary material:

- **C1 — Difficult correctness:** invariants, ownership, concurrency, numerical semantics, or failure modes.
- **C2 — Reusable abstractions:** substantial interfaces and representations supporting multiple applications.
- **C3 — Performance with structure:** concrete performance constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** dated development history accompanied by compatibility, testing, or complexity management.

## Dense arrays, ownership, and language-specific designs

### 1. [numpy/numpy](https://github.com/numpy/numpy)

**Language/role:** C, Python, and C++; general-purpose numerical N-dimensional arrays.

Study the separation between a data buffer and the metadata interpreting that buffer. This explains how slicing and transposition can share storage while dtype, byte order, shape, and strides vary independently.

- **C1:** Shared views must retain the buffer after the original array disappears; read-only flags, non-native byte order, and arbitrary byte strides complicate correct element access.
- **C2:** The same ndarray representation supports basic numeric values, structured records, and object references, while exposing reusable array operations and native-language integration.
- **C3:** Metadata-only transposition avoids moving elements, and ufunc iteration selects the fastest-varying memory dimension for its inner loop. These mechanisms and their locality tradeoffs are explained in [array internals](https://numpy.org/doc/stable/dev/internals.html).

### 2. [rust-ndarray/ndarray](https://github.com/rust-ndarray/ndarray)

**Language/role:** Rust; generic N-dimensional containers, views, and numerical operations.

Study how one array family accommodates owned, borrowed, and shared storage without making every numerical algorithm depend on one ownership model.

- **C1:** `ArcArray` mutation must break sharing when necessary; slicing has explicit bounds and zero-step failure rules. These are concrete ownership and indexing obligations.
- **C2:** Array, shared-array, copy-on-write, and view forms share array operations and dimension abstractions. Start with the [ArrayBase API and ownership discussion](https://docs.rs/ndarray/latest/ndarray/struct.ArrayBase.html).
- **C4:** The [release history](https://raw.githubusercontent.com/rust-ndarray/ndarray/master/RELEASES.md) documents 2021 lifetime-preserving views and a broadcast/BLAS fix, 2024 reshape deprecations and aliasing checks, and the 2025 reference-type redesign and subsequent soundness correction. This is evidence of continuing API and correctness management, not a claim of unchanging compatibility.

### 3. [xtensor-stack/xtensor](https://github.com/xtensor-stack/xtensor)

**Language/role:** C++; expression-template arrays with NumPy-style broadcasting.

Study lazy array expressions together with the lifetime machinery needed to make them usable in ordinary C++ functions.

- **C1:** Expressions retain lvalues by reference but move rvalues into value closures to avoid dangling references. Returning composed expressions introduces further scope and forwarding hazards.
- **C2:** Containers, views, scalar wrappers, and arithmetic expressions participate in the same expression interface.
- **C3:** Deferred evaluation lets composed operations avoid intermediate arrays; closure selection also avoids unnecessary operand copies. The [closure-semantics design](https://xtensor.readthedocs.io/en/latest/closure-semantics.html) includes implementation traits and examples of returning expressions safely.

### 4. [boostorg/multi_array](https://github.com/boostorg/multi_array)

**Language/role:** C++; Boost's multidimensional container and non-owning adaptor module.

Study a comparatively focused generic-container design: owning arrays, external-buffer references, subarrays, and views expose compatible interfaces.

- **C1:** Assignment requires matching shapes and performs an elementwise deep copy; const adaptors must preserve immutability while non-owning references depend on external storage lifetimes.
- **C2:** The common MultiArray concept allows algorithms to work across containers and adaptors. Storage ordering, index bases, reshaping, and slicing are separately configurable concerns.

The [user and implementation guide](https://www.boost.org/doc/libs/latest/libs/multi_array/doc/user.html) explains the component relationships, ownership differences, assignment semantics, and test categories. Its historical introduction predates standard `mdspan`; read that passage in its original context.

### 5. [kokkos/mdspan](https://github.com/kokkos/mdspan)

**Language/role:** C++; reference implementation of non-owning multidimensional views.

Study how a small interface separates shape, index mapping, and element access instead of prescribing one allocation strategy.

- **C2:** `Extents`, `LayoutPolicy`, and `Accessor` are independent customization points. Static and dynamic extents can coexist in one view, and algorithms can accept different memory layouts through the same interface.
- **C3:** Layout policies change memory access patterns without changing an algorithm's logical loop structure; compile-time extents expose optimization opportunities. See the [project's mdspan design introduction](https://github.com/kokkos/mdspan/wiki/A-Gentle-Introduction-to-mdspan).

The repository documents differences in its C++14/17/20 backports and compiler configurations. It is a view implementation, not a full numerical-operation library.

### 6. [SciSharp/NumSharp](https://github.com/SciSharp/NumSharp)

**Language/role:** C#/.NET; NumPy-shaped arrays implemented without embedding Python.

Study numerical buffers at the boundary between a managed runtime and native memory. The useful design includes storage ownership, pinning, views, and dtype-sensitive execution.

- **C1:** Zero-copy buffer views share mutations with their source. Pinning and ownership tracking must keep pointers valid and free memory correctly; externally supplied memory has distinct cleanup responsibilities.
- **C3:** Native buffers support predictable layout and avoid marshaling. `GC.AddMemoryPressure`/`RemoveMemoryPressure` make large native allocations visible to the collector, addressing a failure mode where tiny managed wrappers conceal substantial memory use.

The [buffering and memory architecture guide](https://scisharp.github.io/NumSharp/docs/buffering.html) traces public constructors through `ArraySlice`, `UnmanagedMemoryBlock`, and `UnmanagedStorage`. NumPy compatibility is a stated target, not assumed complete equivalence.

### 7. [Kotlin/multik](https://github.com/Kotlin/multik)

**Language/role:** Kotlin with C++ native integration; multiplatform arrays and numerical engines.

Study dimension-typed array APIs over primitive memory, together with a separation between core array interfaces and Kotlin/OpenBLAS implementations.

- **C1:** Reshape validates element counts. The implementation distinguishes a buffer covering the full contiguous array from a strided view, copying the latter when needed for reshape.
- **C2:** Dimension types and `MultiArray` interfaces support generic code across ranks, while math, linear-algebra, and statistics engines are separate modules.
- **C3:** `NDArray` chooses direct buffer iteration for consistent layouts and a stride-aware iterator otherwise. Its [implementation](https://raw.githubusercontent.com/Kotlin/multik/develop/multik-core/src/commonMain/kotlin/org/jetbrains/kotlinx/multik/ndarray/data/NDArray.kt) also distinguishes copying the backing storage from packing only the view's meaningful elements.

### 8. [gorgonia/tensor](https://github.com/gorgonia/tensor)

**Language/role:** Go; tensor storage and arithmetic supporting Gorgonia and independent numerical code.

Study an array implementation designed around runtime dtypes and Go's slice/memory model. `Dense` combines access metadata (`AP`), backing storage, and an execution `Engine`; the repository explains these components and earlier design tradeoffs.

- **C1:** Shape/dtype requirements and shared backing slices interact with explicitly in-place operations. The API distinguishes copying operations from `UseUnsafe`, which permits clobbering data.
- **C2:** Engines abstract allocation and execution; functional options expose output reuse and accumulation without requiring a separate array type for each behavior.
- **C3:** Reused outputs and BLAS-backed operations address allocation and numerical-kernel costs. Inspect the [package API, including Dense, Engine, and FuncOpt](https://pkg.go.dev/gorgonia.org/tensor), beyond its embedded README. Some narrative documentation is historical; this entry does not infer present maintenance cadence from it.

### 9. [lehins/massiv](https://github.com/lehins/massiv)

**Language/role:** Haskell; multidimensional arrays with parallel computation and several storage representations.

Study the `Array r ix e` family, where representation, index type, and element type remain separate. Manifest arrays hold memory; delayed arrays describe computations and support fusion.

- **C2:** Pull, push, stream, and windowed delayed representations serve different operations while sharing array abstractions. Manifest variants cover boxed, primitive, unboxed, and foreign-memory storage.
- **C3:** Windowed arrays distinguish stencil interiors from borders, allowing different access paths. Delayed composition avoids allocating every intermediate result.
- **C1:** Padding changes output shape and boundary semantics. The [stencil implementation](https://raw.githubusercontent.com/lehins/massiv/master/massiv/src/Data/Massiv/Array/Stencil.hs) makes same/valid padding and wrap, edge, reflect, and other border policies concrete.

## Accelerators and transformable tensor runtimes

### 10. [cupy/cupy](https://github.com/cupy/cupy)

**Language/role:** Python, Cython, and GPU kernels; NumPy/SciPy-style GPU arrays.

Study the memory-management layer beneath an eager array API, especially how array lifetime differs from allocation lifetime.

- **C1:** Stream-ordered allocation requires correct stream/event dependencies. Memory returned to an asynchronous pool may not yet be available to synchronous allocation, causing an apparent out-of-memory condition.
- **C2:** Device and pinned-memory pools, allocator callbacks, and memory-pointer abstractions support multiple allocation strategies behind the array interface.
- **C3:** Reusing pooled allocations reduces allocation and synchronization overhead; separate pinned buffers support host-to-device transfers. The [memory-management guide](https://docs.cupy.dev/en/stable/user_guide/memory.html) explains caching, limits, asynchronous deallocation, and experimental allocator variants without hiding their constraints.

### 11. [arrayfire/arrayfire](https://github.com/arrayfire/arrayfire)

**Language/role:** C++ with C APIs and accelerator backends; general-purpose array computation.

Study a tensor API that combines deferred computation with its own memory manager and device streams.

- **C1:** Handing an array to custom CUDA code requires evaluation, buffer locking, and eventual unlocking. Using a different stream adds explicit synchronization obligations on both sides.
- **C2:** `af::array` and the operation API provide a common interface over CPU and multiple accelerator backends; device-pointer interoperability lets applications introduce custom kernels.
- **C3:** Sharing ArrayFire's stream avoids unnecessary synchronization while preserving execution order. The [CUDA interoperability guide](https://arrayfire.org/docs/interop_cuda.htm) explains both the ownership protocol and the same-stream versus separate-stream cases.

### 12. [pytorch/pytorch](https://github.com/pytorch/pytorch)

**Language/role:** C++, Python, and GPU kernels; focus on **ATen's tensor and iteration subsystem**.

Study `TensorIterator` as a reusable implementation layer beneath many elementwise operations. The larger neural-network and compiler systems are outside this entry's focus.

- **C1:** The iterator coordinates broadcasting and dtype conversion; common computation dtype is distinct from output dtype. Configuration order is constrained, and invalid common-dtype queries fail explicitly.
- **C2:** CPU and GPU kernel helpers consume the same iterator configuration, allowing arithmetic, comparisons, and transcendental operations to reuse iteration machinery.
- **C3:** The [TensorIterator header](https://raw.githubusercontent.com/pytorch/pytorch/main/aten/src/ATen/TensorIterator.h) documents parallel grain-size decisions and splitting work into subiterators that can use 32-bit GPU indexing. These are concrete architectural responses to overhead and indexing costs.

### 13. [jax-ml/jax](https://github.com/jax-ml/jax)

**Language/role:** Python with compiled runtime integration; transformed array programs.

Study the boundary between a familiar array API and a typed intermediate representation, particularly the interaction of tracing, differentiation, vectorization, and compilation.

- **C1:** Traces specialize Python computations into typed primitive expressions. The intermediate form restricts variable dependencies and captures constants explicitly, so ordinary Python behavior cannot simply be assumed under every transformation.
- **C2:** Transformation-specific interpretation rules operate on shared primitives; differentiation and batching may transform incrementally during tracing rather than always materializing a full intermediate program.
- **C3:** JIT compilation targets XLA, while vectorization moves mapped work into primitive operations. The [jaxpr language documentation](https://docs.jax.dev/en/latest/601/jaxpr.html) explains the representation that makes these transformations composable.

### 14. [ml-explore/mlx](https://github.com/ml-explore/mlx)

**Language/role:** C++, Python, and accelerator kernels; lazy array framework originating on Apple silicon.

Study dynamic graph construction and the point at which array values become materialized. The Apple unified-memory model is an additional useful design context; the repository also describes other installation targets.

- **C2:** One array graph supports numerical operations, gradient transformations, vectorization, and graph optimization.
- **C3:** Unused results need not execute, but constructing their graphs still costs something. Evaluation frequency trades fixed execution overhead against growing graph-management costs.

The [lazy-evaluation guide](https://ml-explore.github.io/mlx/build/html/usage/lazy_evaluation.html) explains explicit and implicit evaluation, including scalar extraction and printing. Its sentence about compilation is historical relative to the wider documentation; the conclusions here concern evaluation and materialization, not the absence of compilation support.

### 15. [huggingface/candle](https://github.com/huggingface/candle)

**Language/role:** Rust with accelerator kernels; focus on the **candle-core tensor subsystem**.

Study a compact tensor layout layer independently of the repository's model implementations. `Layout` stores shape, element strides, and starting offset.

- **C1:** Broadcasting rejects incompatible ranks and dimensions. The layout also represents whether different logical indices can reach the same storage, which matters when reasoning about overlapping views.
- **C2:** Layout transformations are reusable across tensor operations and devices rather than embedded in each model.
- **C3:** Broadcasting introduces zero strides instead of repeated data. `strided_blocks` identifies contiguous trailing dimensions and distinguishes single, uniform, and general block iteration. These mechanisms are directly visible in [layout.rs](https://raw.githubusercontent.com/huggingface/candle/main/candle-core/src/layout.rs).

### 16. [elixir-nx/nx](https://github.com/elixir-nx/nx)

**Language/role:** Elixir and native integration; **Nx arrays and numerical definitions**, with EXLA and Torchx in the same repository.

Study how numerical programming can be embedded in a general-purpose functional language while allowing multiple execution implementations.

- **C1:** `defn` deliberately changes some language semantics: tensor-aware operators and numerical truth values differ from ordinary Elixir booleans. Compile-time transforms and runtime tensor computations must also be distinguished.
- **C2:** Numerical definitions operate on scalars through N-dimensional tensors and support custom compilers and container protocols.
- **C3:** Compiled definitions are cached by input shapes and types, allowing different values to reuse compilation. The [Nx.Defn documentation](https://nx.hexdocs.pm/Nx.Defn.html) explains evaluator/compiler separation, specialization, and the supported subset of Elixir.

## Labeled, chunked, sparse, and ragged arrays

### 17. [pydata/xarray](https://github.com/pydata/xarray)

**Language/role:** Python; labeled N-dimensional arrays and datasets.

Study the layers from `Variable` to `DataArray`, `Dataset`, and `DataTree`, including the separation of dimension names, coordinate variables, and lookup indexes.

- **C1:** A variable's dimension-name count must match its array rank. Coordinate dimensions and lengths must be compatible with the data variable; label indexes translate physical-coordinate queries into integer indexing.
- **C2:** Array data can be supplied by different underlying implementations while the labeled-data model remains reusable.
- **C3:** Lazy indexing wrappers defer reads until after subsetting, avoiding unnecessary I/O. The [internal-design guide](https://docs.xarray.dev/en/stable/internals/internal-design.html) distinguishes this mechanism from Dask's broader lazy evaluation and explains why subclassing these composite objects is difficult.

### 18. [dask/dask](https://github.com/dask/dask)

**Language/role:** Python; focus on the **dask.array collection and its task-graph construction**.

Study an array represented as a graph of smaller arrays rather than a single allocation. Scheduler and dataframe code are not separate entries here.

- **C1:** Chunk metadata, graph keys, rank, dtype, and overall shape must agree. Slicing may produce irregular chunks, and some operations impose additional compatibility constraints on block shapes.
- **C2:** Blocks can be stored arrays or tasks that produce them; metadata also tracks the underlying array type, permitting different block implementations.
- **C3:** Chunked execution exposes work units that can be scheduled without materializing the full logical array at once. The [array internal-design document](https://docs.dask.org/en/stable/array-design.html) gives the graph-key convention, chunk invariants, metadata propagation, and an operation-construction example.

### 19. [pydata/sparse](https://github.com/pydata/sparse)

**Language/role:** Python; sparse arrays of arbitrary dimension for the PyData ecosystem.

Study how sparsity changes the meaning and implementation of familiar array operations, especially when the implicit fill value is not zero.

- **C1:** Coordinate ordering and duplicate-coordinate promises are invariants: falsely declaring data sorted or duplicate-free can cause undefined behavior. Operations must also preserve the semantics of the implicit fill value.
- **C2:** COO arrays support broadcasting, reductions, dot products, and NumPy ufunc integration beyond the two-dimensional sparse-matrix model.
- **C3:** Explicit coordinate/value storage and transformed fill values can preserve a compact representation; the documented `exp` example changes the fill value to one. The [COO API and embedded source](https://sparse.pydata.org/en/stable/api/COO/) explain constructor normalization flags, storage, caching, and operations.

### 20. [scikit-hep/awkward](https://github.com/scikit-hep/awkward)

**Language/role:** Python and compiled kernels; nested, ragged, optional, and record-valued arrays.

Study how an array library can represent irregular structure with buffers and composable layout nodes instead of requiring rectangular shapes.

- **C1:** Ragged-list offsets must delimit valid content ranges, including empty lists and arrays. A legal layout need not start at content offset zero or consume all of its content.
- **C2:** List nodes compose with other content nodes, including record fields and numeric buffers; the same representation also supports encoded strings.
- **C3:** An offsets buffer describes many variable-length lists over shared content. The [ListOffsetArray representation and simplified implementation](https://awkward-array.org/doc/main/reference/generated/ak.contents.ListOffsetArray.html) show how slicing changes structural metadata and explain its relationship to Arrow's list representation.

### 21. [scipp/scipp](https://github.com/scipp/scipp)

**Language/role:** C++ and Python; labeled scientific arrays with units, masks, and optional variances.

Study numerical semantics that ordinary shape-compatible arithmetic cannot capture. Scipp is particularly useful for understanding arrays whose scientific meaning includes coordinate agreement and measurement uncertainty.

- **C1:** Arithmetic checks compatible units and aligned coordinates. Broadcasting an operand with variances raises an error because it would introduce correlations the representation cannot track, potentially understating subsequent uncertainties.
- **C2:** The computation model combines named dimensions, values, masks, and uncertainty propagation; in-place operations preserve the left-hand shape while binary operations align dimensions.

The [computation guide](https://scipp.github.io/user-guide/computation.html) specifies these rules and their implementation consequences. Correlated-error tracking is explicitly a limitation, rather than an implied feature.

## Symmetry-aware and distributed tensors

### 22. [QuantumKitHub/TensorKit.jl](https://github.com/QuantumKitHub/TensorKit.jl)

**Language/role:** Julia; tensors as maps between structured vector spaces, including internal symmetries.

Study a tensor abstraction whose indices carry algebraic information rather than only integer extents.

- **C1:** Tensor composition requires compatible domain and codomain spaces. With symmetry, allowed data blocks depend on matching fused charges; index ordering must agree with the chosen matrix representation.
- **C2:** `AbstractTensorMap`, concrete tensor maps, adjoint wrappers, and diagonal maps support generic operations over space types.
- **C3:** Symmetry organizes storage into allowed sectors, while compatible matrix representations permit composition and factorization through matrix operations. The [tensor construction and storage manual](https://raw.githubusercontent.com/QuantumKitHub/TensorKit.jl/main/docs/src/man/tensors.md) develops this design from the no-symmetry case to charge sectors. The repository separately documents storage and factorization migrations.

### 23. [ITensor/ITensors.jl](https://github.com/ITensor/ITensors.jl)

**Language/role:** Julia; index-aware tensor computation, including the repository's NDTensors storage layer.

Study an API that identifies dimensions by index objects rather than requiring callers to remember physical axis order.

- **C1:** Addition and contraction use index identity and automatically handle required permutations. Array-backed constructors also make sharing and element-type conversion relevant to mutation behavior.
- **C2:** The logical ITensor interface is independent of memory layout and sits above storage representations, allowing tensor algorithms to work in terms of indices.

The [ITensor type and constructor documentation](https://docs.itensor.org/ITensors/stable/ITensorType.html) exposes this logical/physical separation with storage examples. The repository's migration notes explain that MPS/MPO algorithms moved into ITensorMPS.jl; those algorithms are not counted as part of this entry's current scope.

### 24. [ValeevGroup/tiledarray](https://github.com/ValeevGroup/tiledarray)

**Language/role:** C++; distributed dense and block-sparse tensor arithmetic.

Study how mathematical tensor expressions are decomposed into tiled tasks over the MADNESS runtime. Tile types and sparse structure are customization points, not merely implementation details.

- **C2:** The framework supports dense and block-sparse tensors with replaceable tile representations, allowing applications to adapt storage and computation to their workload.
- **C3:** Expression evaluation creates parallel tasks whose local BLAS work is normally expected to be single-threaded. The [runtime/build integration guide](https://raw.githubusercontent.com/ValeevGroup/tiledarray/master/INSTALL.md) explains why nested BLAS threading oversubscribes cores and identifies the shared-runtime exception.
- **C1:** Runtime integration requires appropriate MPI thread support and coordinated choices of numerical libraries. These concurrency and integration constraints are explicit, rather than hidden behind the expression syntax.

### 25. [cyclops-community/ctf](https://github.com/cyclops-community/ctf)

**Language/role:** C++ with Python/Cython interfaces; Cyclops Tensor Framework for distributed tensor arithmetic.

Study tensors whose storage and operations span an MPI world, with sparsity, symmetry, and user-defined arithmetic represented in the tensor interface.

- **C1:** Global versus local indices, symmetry-packed versus unpacked data, and sparse zero handling affect what read operations return. Allocating read APIs also specify distinct ownership/deallocation contracts.
- **C2:** Tensor construction accepts dimensions, symmetry descriptors, an execution world, and an arithmetic structure, making the abstraction useful beyond ordinary dense floating-point arrays.
- **C3:** Local-data APIs preserve distribution; all-data APIs explicitly warn that replicating the tensor on every process is not memory-scalable. These distinctions are documented in the [Tensor interface header](https://raw.githubusercontent.com/cyclops-community/ctf/master/src/interface/tensor.h). The repository also describes single- and multi-process test commands. Its old tagged-release date alone is not used to infer current development activity.

## Search coverage and limitations

Live searches used more than a dozen formulations across several distinct angles. Representative discovery queries included:

- `multidimensional array tensor library C++ xtensor Eigen mdspan GitHub architecture`
- `Rust multidimensional array library ndarray tensor candle burn GitHub`
- `Julia multidimensional arrays tensor library GitHub TensorKit NDTensors`
- `GitHub multidimensional arrays libraries Java Kotlin C# Go NumSharp Multik Gorgonia tensor`
- `GitHub array library sparse labelled ragged distributed numpy xarray awkward sparse dask`
- `GitHub tensor library distributed tiledarray cyclops tensor framework TBLIS`
- `GitHub GPU array library ArrayFire CuPy mlx tensor memory lazy evaluation`
- `multidimensional array library units variances scipp GitHub`
- `tensor array library OCaml Nim Arraymancer Owl GitHub architecture`
- `javascript ndarrays library strides dtype github`

Follow-up searches targeted ownership rules, source files, stencil behavior, tensor representation, and release history. Later searches increasingly returned overlapping dense-array designs, thin wrappers, broader ML frameworks, or narrower contraction libraries; the selection emphasizes distinct implementation lessons. Other surfaced candidates, including Blitz++, Arraymancer, Owl, and JavaScript ndarray implementations, were not fully audited for this report. Their omission is not a negative quality judgment or a claim of ecosystem completeness.

Every retained repository's GitHub page was opened, and at least one additional primary documentation or implementation source was read. GTensor was excluded because repeated repository-page and source fetches failed in this research environment, despite relevant search results. Failed documentation URLs were replaced with successfully opened canonical documentation or raw implementation files. Some GitHub source rendering was incomplete, so verified raw files are linked where appropriate.

Matrix-only solver packages, array storage formats, tutorials, model collections without an independently substantial tensor layer, and thin backend wrappers were outside the selection. No forks are counted as separate implementations, and monorepos appear once. No candidate code was executed, repositories cloned, or dependencies installed. Published performance ratios and star counts were not used as evidence. Except where C4 is explicitly justified, maintenance cadence and multi-year compatibility were not independently established. Architectural judgments are inferences from the inspected material, not claims that every component is uniformly exemplary.
