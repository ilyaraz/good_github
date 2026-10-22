# Distributed array computing frameworks

Research date: **2026-10-09**

This report selects 22 GitHub repositories that implement reusable arrays, matrices, or tensors whose storage and computation span processes or machines. It covers task graphs, MPI, partitioned global address spaces (PGAS), distributed object lifetimes, and accelerator sharding. Distributed matrix libraries qualify as a substantial two-dimensional specialization. General runtimes and machine-learning monorepos appear only where a specific distributed-array subsystem supplies the evidence. Selection reflects architectural study value, not a recommendation that every project is suitable for a new deployment.

Criteria legend:

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, or distributed failure modes.
- **C2 — Reusable abstractions:** substantial interfaces and implementation mechanisms supporting different applications.
- **C3 — Performance with structure:** concrete memory, communication, locality, or execution constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility work, testing, or explicit complexity management. Age or a recent commit alone does not qualify.

## Python task graphs and block arrays

### 1. [dask/dask](https://github.com/dask/dask)

**Language/role:** Python; the Dask Array collection within the larger Dask repository.

Study how a familiar array interface becomes a graph of independently executable blocks while retaining enough metadata for slicing and composition. The separation between graph keys, chunk geometry, and local array types is particularly instructive.

- **C1:** Chunk lengths describe every axis, their sums determine the global shape, and operations must preserve compatible block geometry. Slicing can create irregular chunks, so correctness cannot assume a single uniform block size. The [array design documentation](https://docs.dask.org/en/stable/array-design.html) explains this representation and its invariants.
- **C2:** An array combines a task graph, name, chunk structure, dtype, and an empty local-array exemplar, `_meta`. This allows the same collection machinery to represent different local array implementations instead of tying the distributed abstraction to one storage class. The same [design entry point](https://docs.dask.org/en/stable/array-design.html) connects those components.

The selection is Dask Array; the scheduler repository is not counted as another array framework.

### 2. [cubed-dev/cubed](https://github.com/cubed-dev/cubed)

**Language/role:** Python; distributed array computation with explicitly planned memory consumption and chunked persistent intermediates.

Cubed is useful for comparing a storage-mediated execution design with a runtime that primarily retains intermediates in worker memory.

- **C2:** Its [layered design](https://cubed-dev.github.io/cubed/design.html) separates Zarr storage, executors, a blockwise primitive, core array operations, and the public Array API. Executor implementations can change without redefining array operations.
- **C3:** The [computation model](https://cubed-dev.github.io/cubed/computation.html) plans blockwise operations and rechunking using chunk sizes, dtypes, and operation memory requirements. Intermediate arrays are materialized in storage; fusion reduces the resulting I/O. This exposes a concrete tradeoff between bounded task memory, parallelism, and storage traffic.

The memory model is worth studying as an engineering contract; it should not be read as an unconditional bound on arbitrary user code supplied to a kernel.

### 3. [mars-project/mars](https://github.com/mars-project/mars)

**Language/role:** Python/Cython; distributed tensor and related collections on an actor-based execution system.

Mars makes the transition from a large logical array operation to schedulable distributed work unusually visible. Its tensor subsystem is the relevant portion of this broader analytics project.

- **C1:** Session isolation and distributed data lifetimes are explicit services. Reference counts determine when stored data and metadata can be removed, rather than assuming a client object's lifetime directly matches its remote storage. See the [development architecture](https://mars-project.readthedocs.io/en/stable/development/overview.html).
- **C2:** Logical tileables, chunks, operands, and subtasks form distinct abstraction levels. The task service tiles the logical graph, fuses chunk work, and creates execution units; metadata, storage, and scheduling remain separate services.
- **C3:** Storage transfer and spilling, task fusion, and locality-aware scheduling address memory pressure and communication costs within that architecture. The [service overview](https://mars-project.readthedocs.io/en/stable/development/overview.html) is the best starting point.

These claims describe the documented architecture, without inferring current maintenance from the availability of older documentation.

### 4. [nums-project/nums](https://github.com/nums-project/nums)

**Language/role:** Python; NumPy-style distributed block arrays with backend-mediated execution. **Historical: GitHub marks the repository archived on 2025-11-10.**

NumS is a useful compact study of the boundary between array metadata, remote objects, and execution placement. The [repository overview](https://github.com/nums-project/nums) describes its distributed backends and optimization approach.

- **C1:** A block tracks its grid position, shape, dtype, remote object identifier, and deferred transpose state. A transpose can reuse a remote object while changing metadata; gathering and subsequent operations must interpret that state consistently. See the implementation in [array/base.py](https://raw.githubusercontent.com/nums-project/nums/master/nums/core/array/base.py).
- **C2:** `BlockArrayBase`, the array grid, and the kernel manager separate a logical array from backend objects and kernel dispatch. Broadcasting and unary/binary operations build on that shared representation rather than implementing independent distributed containers for each operation.

The archive makes it a historical implementation reference, not evidence of ongoing support.

### 5. [Python-for-HPC/ramba](https://github.com/Python-for-HPC/ramba)

**Language/role:** Python with Numba compilation; NumPy-like distributed arrays using MPI or Ray execution.

Ramba is valuable for studying the interaction between deferred array operations, generated kernels, and a distributed runtime. Its implementation concentrates substantial machinery in a large source module, which is itself a useful complexity tradeoff to examine.

- **C2:** The [project documentation](https://github.com/Python-for-HPC/ramba) describes a common array interface over distributed execution, including MPI's collective/SPMD calling model. Array programs can express operations without manually writing each message exchange.
- **C3:** Deferred operations are fused into compiled loops to reduce temporary arrays and repeated memory traversals. In [ramba.py](https://raw.githubusercontent.com/Python-for-HPC/ramba/main/ramba/ramba.py), `FunctionMetadata` manages parallel-Numba, serial-Numba, and Python execution paths, remembers compilation failures by argument types, and works alongside generated-function caching. This provides concrete material on avoiding repeated compilation and managing fallback costs.

No claim of current dependency compatibility is inferred from the installation examples.

### 6. [bsc-wdc/dislib](https://github.com/bsc-wdc/dislib)

**Language/role:** Python; distributed arrays and algorithms scheduled through PyCOMPSs.

The most useful subsystem here is the block-structured `ds-array`: a distributed matrix of dense NumPy or sparse SciPy blocks shared by multiple algorithms.

- **C1:** Slicing may preserve irregular edge blocks instead of rebuilding the entire partitioning. The representation distinguishes the top-left block shape, regular block shape, and global shape; operations must respect these differences. The [user guide](https://dislib.readthedocs.io/en/latest/user-guide.html) explains the layout, while the [array API](https://dislib.readthedocs.io/en/latest/dislib.array.html) exposes its metadata and operation constraints.
- **C2:** Dense and sparse blocks use one distributed container, with collection, slicing, rechunking, transposition, and matrix operations supporting higher-level estimators.
- **C3:** The user guide discusses small-block scheduling overhead versus available parallelism, and why different algorithms favor different row/column partitionings. This is a concrete example of array layout becoming an algorithm-level decision.

## MPI and interactive analytics arrays

### 7. [helmholtz-analytics/heat](https://github.com/helmholtz-analytics/heat)

**Language/role:** Python; distributed numerical arrays combining local PyTorch tensors with MPI communication.

HeAT is a strong entry point for studying how a local tensor backend becomes a global array without hiding all distribution metadata.

- **C1:** `DNDarray` couples local storage with global shape, split axis, communicator, and balance state. Changing local storage validates shape assumptions and invalidates cached distribution information. Counts and displacements must also handle uneven ownership. These mechanisms are visible in [dndarray.py](https://raw.githubusercontent.com/helmholtz-analytics/heat/main/heat/core/dndarray.py).
- **C2:** The same distributed array representation underlies numerical operations while preserving the local backend's device and dtype abstractions. The [official documentation](https://heat.readthedocs.io/en/stable/) explains the PyTorch/MPI split.
- **C3:** The implementation distinguishes inexpensive metadata derivation for balanced layouts from communication needed to discover uneven layouts, and exposes redistribution and balancing operations. It makes the cost of restoring a useful partitioning explicit.

### 8. [Bears-R-Us/arkouda](https://github.com/Bears-R-Us/arkouda)

**Language/role:** Chapel server and Python client; interactive analysis over distributed server-resident arrays.

Arkouda offers a different control model from Python workers: Python sends operations to a Chapel service and holds handles to the resulting arrays. Study where this interface permits familiar expressions and where it deliberately forces an explicit transfer.

- **C2:** A `pdarray` carries identifying metadata for a server-side symbol rather than owning the full local dataset. Operator wrappers use that handle to compose analytics. The [pdarray implementation guide](https://bears-r-us.github.io/arkouda/usage/pdarray.html) explains this boundary.
- **C3:** Direct Python iteration is disabled, and conversion to a local NumPy array checks transfer size and expected received bytes. These choices make expensive data movement visible instead of silently pulling elements across the client/server boundary.

The implementation guide contains older dimensionality/type descriptions; those are not treated as present limits. The [release history](https://github.com/Bears-R-Us/arkouda/releases) supplies a separate view of evolving NumPy alignment tests, compatibility checks, and transfer-related optimizations.

## Julia distributed array interfaces

### 9. [JuliaParallel/DistributedArrays.jl](https://github.com/JuliaParallel/DistributedArrays.jl)

**Language/role:** Julia; the `DArray` abstraction over worker-owned local array chunks.

This is a particularly clear study of the semantic costs that remain when distributed arrays resemble local arrays.

- **C1:** The [manual](https://juliaparallel.org/DistributedArrays.jl/stable/) explains two nontrivial correctness issues: distributed reduction order can change floating-point results, and the creating process's garbage collection does not naturally track the amount of remote storage. Explicit `close` is therefore important for remote lifetime management.
- **C2:** `DArray` separates global indexing and distribution from the concrete local array type. Initializers receive owned index ranges; `localpart` and `localindices` expose local work without abandoning the shared abstraction. The same manual documents worker assignment and per-dimension partition counts.

Study the local-part interface together with the lifetime section, rather than assuming ordinary Julia object ownership automatically explains every remote allocation.

### 10. [JuliaParallel/Dagger.jl](https://github.com/JuliaParallel/Dagger.jl)

**Language/role:** Julia; the `DArray` subsystem of a broader task-graph runtime.

Dagger's distributed arrays illustrate how a dynamic scheduler and array partitioning can coexist. The important distinction is between the logical block structure and where subsequent computation actually executes.

- **C2:** The [DArray guide](https://juliaparallel.org/Dagger.jl/dev/darray/) layers distributed indexing and array operations on task-managed partitions. `Blocks` and `AutoBlocks` express chunking without requiring every array operation to implement its own scheduler.
- **C3:** The same guide describes processor assignments, including row, column, cyclic, and multidimensional mappings. The current PGAS-style representation references all partitions, while later work can be reassigned by the scheduler. This provides concrete material on initial placement versus dynamic execution locality.

The selection concerns distributed arrays, not every Dagger scheduler feature. Development documentation is used for its described design; it is not a promise that every backend has identical support.

### 11. [jipolanco/PencilArrays.jl](https://github.com/jipolanco/PencilArrays.jl)

**Language/role:** Julia/MPI; multidimensional arrays decomposed along selected axes, including the redistribution machinery used by distributed transforms.

PencilArrays isolates a problem that broader array frameworks can obscure: changing which dimensions are distributed while preserving global coordinates and local memory order.

- **C1:** A transposition requires compatible global sizes and MPI Cartesian topology, with restrictions on how decomposed dimensions differ. Source and destination may alias, adding another invariant beyond message matching. The [transposition API](https://jipolanco.github.io/PencilArrays.jl/dev/Transpositions/) states these constraints explicitly.
- **C3:** That API contrasts nonblocking point-to-point communication with `Alltoallv`; the point-to-point path can interleave transfers with local data permutations. Communication and local transposition are thus separate, inspectable costs.

The [repository overview](https://github.com/jipolanco/PencilArrays.jl) establishes the reusable multidimensional decomposition role. This is more than an FFT application: the array and redistribution abstractions are the project itself.

## PGAS libraries and language-supported arrays

### 12. [GlobalArrays/ga](https://github.com/GlobalArrays/ga)

**Language/role:** C and Fortran with C++ interfaces; globally indexed distributed arrays with one-sided operations.

Global Arrays is especially useful for understanding why a global indexing abstraction does not remove memory-consistency obligations.

- **C1:** The [programming-model introduction](https://globalarrays.readthedocs.io/en/latest/Section0-Introduction.html) distinguishes local completion from remote completion and explains ordering and synchronization requirements for access to overlapping regions. A completed put or accumulate call cannot simply be interpreted as a globally synchronized update.
- **C2:** Global indices abstract address mapping and data movement while retaining access to local regions and regular or irregular distributions. This supports applications beyond a single matrix algorithm.
- **C4:** The [changelog](https://raw.githubusercontent.com/GlobalArrays/ga/develop/CHANGELOG.md) records years of concrete compatibility and correctness work: large-message handling, nonblocking-handle redesign, compiler and integer-width fixes, tests, and retirement of obsolete platform code. These changes support a sustained-evolution criterion rather than relying on the project's age alone.

Some introductory documentation is historical; its exact datatype or dimensionality limits are not presented as current limits.

### 13. [dash-project/dash](https://github.com/dash-project/dash)

**Language/role:** C++ library over the DART runtime; PGAS containers and algorithms.

DASH's `NArray` is valuable for studying the separation between a container, an ownership pattern, and a team of participants.

- **C2:** The [NArray documentation](https://dash.readthedocs.io/en/latest/Containers/NArray/) makes `Pattern` responsible for translating global and local coordinates independently of element type and allocation. Dimension count, layout, index type, and team are separate design parameters. Views and slices reuse this distribution machinery.
- **C3:** The same documentation distinguishes global references, which can involve remote access, from native references obtained through the local view. Owner-computes iteration avoids paying remote-access and global-indexing costs for every element; blocked layouts also account for partial final blocks.

This selection focuses on the implemented distributed container design. The available documentation has unfinished passages, so it should be cross-checked against source before adopting a particular API or relying on an exception contract.

### 14. [chapel-lang/chapel](https://github.com/chapel-lang/chapel)

**Language/role:** Chapel plus its compiler/runtime implementation; distributed domains, arrays, and distribution modules within the monorepo.

Chapel provides a language-level counterpart to library-only designs. Its central lesson is that an index set, its placement, and the values indexed by it can be independently reusable concepts.

- **C2:** The [distributions primer](https://chapel-lang.org/docs/primers/distributions.html) separates distributions, domains, and arrays. A distribution maps domain indices to locales and determines array storage and iteration; programs can use common array operations across different mappings.
- **C3:** Distributed `forall` iteration follows ownership and uses local execution resources. Sharing a distribution aligns ownership across arrays, while block and cyclic distributions expose different placement strategies. The primer also explains how cyclic logical indices can still have compact local storage.

The relevant study target is this distributed-array subsystem, not the entire compiler as a general-purpose language project. Its examples make locality consequences observable at the programming-model boundary.

### 15. [pnnl/lamellar-runtime](https://github.com/pnnl/lamellar-runtime)

**Language/role:** Rust; asynchronous HPC runtime with PGAS arrays, active messages, and distributed reference counting.

Lamellar adds a distinctive ownership-oriented approach. The separate `pnnl/lamellar` repository is an integration/staging repository pointing to this runtime; it is not counted again.

- **C1:** The [array module documentation](https://docs.rs/lamellar/latest/lamellar/array/index.html) explains that array storage must remain alive while a reference exists anywhere in the system. Distributed reference counting and garbage-collecting active messages extend lifetime management beyond what Rust's compiler can establish inside one process.
- **C2:** Read-only, atomic, local-lock, global-lock, and explicitly unsafe array variants express different access contracts. Block/cyclic distributions, distributed/local/one-sided iteration, reductions, and type conversion share the array framework. Local data accessors preserve the selected access contract.

The [runtime repository](https://github.com/pnnl/lamellar-runtime) also documents collective participation and multiple transport backends. The lesson is not that Rust alone solves distributed safety, but how runtime protocols complement the language's local guarantees.

## Distributed tensor algebra and matrix specializations

### 16. [ValeevGroup/tiledarray](https://github.com/ValeevGroup/tiledarray)

**Language/role:** C++; tiled dense and sparse distributed tensor algebra using asynchronous tasks.

TiledArray is a strong study target for the interaction between block sparsity, futures, and distributed container lifetime.

- **C1:** The [DistArray reference](https://valeevgroup.github.io/tiledarray/dox-master/class_tiled_array_1_1_dist_array.html) describes remote tile retrieval through futures, delayed distributed destruction, and cleanup that may execute ready tasks while waiting. Sparse truncation is collective and changes both shape information and retained tiles. These mechanisms create correctness obligations beyond ordinary local-container destruction.
- **C2:** `DistArray` separates tile type, policy, tiled index ranges, and process mapping. This supports different tile representations and sparse/dense policies under distributed algebra expressions rather than fixing a single physical tensor layout.
- **C3:** Tile-level sparsity and asynchronous tile availability let the implementation avoid unnecessary work and expose dependency-level parallelism. The [repository overview](https://github.com/ValeevGroup/tiledarray) provides the surrounding algebra and runtime context.

### 17. [cyclops-community/ctf](https://github.com/cyclops-community/ctf)

**Language/role:** C++ with Python/Cython interfaces; Cyclops Tensor Framework for MPI-distributed tensor algebra.

CTF offers a compact mathematical interface over substantial communication and local-kernel machinery. Study how indexed tensor expressions support multiple data representations and algebraic operations.

- **C2:** The [repository documentation](https://github.com/cyclops-community/ctf) describes distributed tensors with symmetry, sparsity, and user-defined element/algebra types. Einstein-style index expressions provide a shared mechanism for contractions and related operations rather than a collection of isolated parallel kernels.
- **C3:** Local BLAS kernels and optional tensor-transposition libraries sit beneath the distributed interface. The [build and testing guide](https://github.com/cyclops-community/ctf/wiki/Building-and-testing) exposes selectable numerical, threading, and communication-related dependencies, making the boundary between distributed algorithms and optimized local work inspectable.

The repository also documents multi-process test targets. Those are useful verification entry points, but their existence alone is not treated as evidence of comprehensive correctness or current platform support. Tagged releases and documentation can be older than development changes.

### 18. [elemental/Elemental](https://github.com/elemental/Elemental)

**Language/role:** C++ with additional interfaces; distributed dense/sparse matrix computation, including extended and arbitrary precision.

Elemental belongs here as a substantial matrix specialization. Its distributed matrix and process-grid abstractions are reusable across many numerical algorithms.

- **C1:** The [documentation tour](https://elemental.github.io/documentation/dev/tour.html) works through ill-conditioned systems, distinguishes residual size from forward error, and demonstrates changes in numeric precision. This gives concrete material for studying numerical semantics alongside distribution rather than equating a successfully completed collective with an accurate answer.
- **C2:** `Matrix`, `DistMatrix`, scalar field types, and process grids are separate abstractions. The tour carries similar operations across local/distributed storage and different precision types, allowing engineers to follow which concerns remain shared and which require distribution-specific machinery.
- **C3:** Process-grid shape and the mapping of processes to the network affect execution; the tour explicitly discusses these configuration decisions.

The cited material is the development documentation, not a benchmark or a statement of current compatibility with every dependency.

### 19. [RBigData/pbdDMAT](https://github.com/RBigData/pbdDMAT)

**Language/role:** R with native numerical dependencies; distributed dense matrices and statistical computations over MPI/BLACS/ScaLAPACK infrastructure.

This is a useful R-community example of adapting distributed matrix layouts to a high-level object system. It includes distribution management and statistical operations, rather than merely generated bindings.

- **C2:** In [00-classes.r](https://raw.githubusercontent.com/RBigData/pbdDMAT/master/R/00-classes.r), matrix classes distinguish global dimensions, local dimensions, storage mode, block dimensions, BLACS context, and communicator. That metadata provides a common representation for distributed operations exposed through R methods.
- **C1:** The [changelog](https://raw.githubusercontent.com/RBigData/pbdDMAT/master/ChangeLog) records concrete correctness problems and fixes involving redistribution, matrix indexing, reductions, factorization, and which routines require square blocks. These are substantive distributed-layout and numerical edge cases.

A useful review caution is visible in the class source: a `valid.ddmatrix` function checks local-size/context consistency, but its class-level validity hook is commented out. The existence of that function therefore must not be mistaken for automatic enforcement on every object construction.

## Accelerator and compiler-based distributed arrays

### 20. [nv-legate/cupynumeric](https://github.com/nv-legate/cupynumeric)

**Language/role:** Python/C++/CUDA; NumPy-style distributed arrays implemented on Legate. **Archived and end-of-life; the repository identifies v26.06.01 as the final release and states that maintenance/support has ended.**

Formerly cuNumeric, this remains useful for studying the lowering of array semantics to a task runtime, with the lifecycle limitation made explicit in the [repository notice](https://github.com/nv-legate/cupynumeric).

- **C1:** [deferred.py](https://raw.githubusercontent.com/nv-legate/cupynumeric/main/cupynumeric/_thunk/deferred.py) handles overlapping input/output storage, including partial overlap, before issuing operations. Broadcasting and reduction also require consistency between logical shapes, task inputs, and reduction operators.
- **C2:** Deferred arrays wrap Legate logical stores; operations construct tasks with inputs, outputs, alignment constraints, and reduction behavior. This is a reusable bridge from a large array API to partitioned execution rather than one specialized distributed kernel.

The overlap-copy helpers and binary-operation construction are particularly useful entry points for understanding where NumPy aliasing semantics impose costs on a distributed implementation.

### 21. [jax-ml/jax](https://github.com/jax-ml/jax)

**Language/role:** Python/C++; global `jax.Array`, sharding, and multi-controller execution within the larger JAX monorepo.

The relevant design is a global array whose device shards may belong to different processes, with compilation determining distributed execution and communication.

- **C1:** The [multi-process guide](https://docs.jax.dev/en/latest/multi_process.html) explains that participating processes must execute compatible distributed operations in the same order. Violations can hang rather than produce a convenient exception. It also distinguishes globally present shards from those addressable by the current process.
- **C2:** Meshes, named shardings, and partition specifications separate a logical array from how its dimensions map to devices. These concepts support operations beyond one model architecture or training loop.
- **C3:** The same guide shows global computations being partitioned across processes with communication introduced as needed, and discusses explicit gathering/replication. It is useful for tracing which array expressions become cross-process collectives.

This entry does not treat the entire automatic-differentiation or machine-learning ecosystem as category evidence.

### 22. [pytorch/pytorch](https://github.com/pytorch/pytorch)

**Language/role:** Python/C++/CUDA; `torch.distributed.tensor` (DTensor) and `DeviceMesh` within the PyTorch monorepo.

DTensor is worth studying for its explicit representation of intermediate distributed states, especially values that are only partial contributions to a global result.

- **C1:** The [DTensor API](https://docs.pytorch.org/docs/2.14/distributed.tensor.html) specifies cross-rank metadata assumptions, optional construction checks, uneven-shard metadata requirements, and gradient placement semantics. `Partial` represents a value awaiting reduction; it is not interchangeable with either a replica or an ordinary shard.
- **C2:** A device mesh and per-dimension placements describe tensor layout independently of individual operators. Operator handling propagates or transforms that layout while preserving the tensor interface.
- **C3:** Redistribution maps layout changes to specific mechanisms: all-gather, all-to-all, local chunking, all-reduce, or reduce-scatter. The same documentation makes those communication choices directly inspectable.

The cited versioned documentation also marks some behavior experimental. This entry is restricted to the distributed tensor subsystem and does not imply that every PyTorch component meets these criteria.

## Coverage, search method, and limitations

Discovery used live web searches with substantially more than six distinct formulations. Search angles included Python distributed NumPy/task-graph arrays; MPI-based NumPy alternatives; Julia distributed arrays and pencil decompositions; C/C++ PGAS containers and one-sided arrays; distributed sparse tensor contraction; distributed dense matrices and ScaLAPACK interfaces; Chapel distributions; Rust PGAS arrays and ownership; accelerator/NumPy runtimes; and compiler/ML tensor sharding. Additional searches for historical distributed arrays and Fortran/Java implementations mostly produced overlap, local-only containers, domain-specific applications, or weaker candidates. Lamellar was a substantive late addition from the Rust search; subsequent breadth checks had diminishing returns.

Every retained canonical GitHub repository page was opened. Each entry also uses an opened/read primary source beyond its repository README: architecture documentation, implementation source, API semantics, testing instructions, or a changelog. Source inspection was selective, not a complete code audit. Criteria are reasoned assessments grounded in the cited mechanisms; they are not certifications that all code is correct, fast, or exemplary. No stars-based scoring, numerical performance claims, dependency installation, repository execution, or benchmarks were used.

The selection spans Python, Julia, C++, C, Fortran, Chapel, Rust, and R, from interactive analytics to tightly coupled HPC and accelerator collectives. Language coverage refers to interfaces and implementation roles, not an assertion that each project is written equally in every listed language. Cubed contributes storage-mediated execution; Arkouda contributes a client/server model; Lamellar contributes distributed ownership; the matrix libraries provide specialized numerical depth.

Important boundaries and exclusions:

- Local-only array libraries, pure storage formats, generic schedulers without a substantive array layer, tutorial repositories, and single scientific applications were excluded. Xarray-style labeled interfaces and Zarr-style storage alone were not treated as distributed execution frameworks.
- Dask's scheduler, Legate's underlying runtime, and Lamellar's staging repository were not counted separately from the selected array implementations. Monorepos count once and name the relevant subsystem; no fork is counted as an independent project.
- NumS and cuPyNumeric are explicitly historical/archived selections. Their value is architectural study, and their presence is not a deployment recommendation. No moved-away project is retained solely because an obsolete GitHub shell exists.
- Several projects expose older or development documentation. Where it disagrees with newer material, the report avoids unsupported current feature limits or maintenance claims. Accessibility, repository age, and recent release visibility are not themselves C4 evidence; C4 is asserted only where the inspected history supports it.
- This is a broad selection guide, not an exhaustive inventory. In particular, proprietary systems and projects without a substantive GitHub implementation fall outside the requested scope.
