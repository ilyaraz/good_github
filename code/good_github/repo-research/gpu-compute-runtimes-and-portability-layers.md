# GPU compute runtimes and portability layers

Research date: **2026-10-09**

This selection covers implementations that execute, schedule, compile for, or manage memory for general GPU computation, plus substantial programming layers that make those operations portable across devices or languages. It includes vendor runtimes, OpenCL/SYCL/OpenMP implementations, API translation, portable C++ kernels, WebGPU compute infrastructure, and managed-language runtimes. Algorithm-oriented libraries are included only where kernel generation, dispatch, or device-memory abstractions are central. These are engineering study recommendations, not claims of uniform code quality, complete standards conformance, or interchangeable backend capabilities.

Criteria legend:

- **C1 — Difficult correctness:** synchronization, lifetime invariants, memory models, numerical semantics, validation, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and implementation structures supporting many applications or backends.
- **C3 — Performance with structure:** explicit treatment of dispatch, compilation, allocation, transfers, locality, or hardware mapping through understandable architectural boundaries.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or complexity management; repository age alone does not qualify.

## Runtime implementations and API compatibility

### 1. [intel/compute-runtime](https://github.com/intel/compute-runtime)

**Language/role:** C++; Intel GPU implementation of OpenCL and oneAPI Level Zero, commonly called NEO.

An unusually useful codebase for following an API call all the way to hardware submission. The two API frontends share device discovery, memory management, command encoding, and operating-system integration.

- **C1:** Residency must be established before submission, allocations referenced by unfinished work require deferred deletion, and command-buffer reuse waits for all recorded contexts, including copy engines.
- **C2:** Shared runtime objects and graphics-family template specializations separate API behavior from hardware and OS differences.
- **C3:** The direct-submission ring avoids a kernel-mode call for every submission; task-count completion tracking and compiler caching expose the surrounding tradeoffs.

**Entry point:** The substantive [architecture guide](https://github.com/intel/compute-runtime/blob/master/ARCHITECTURE.md) explains these invariants, the ownership tree, submission sequence, and unit/multithreaded/simulator testing layout.

### 2. [ROCm/rocm-systems](https://github.com/ROCm/rocm-systems)

**Language/role:** Primarily C/C++; relevant subsystems are `projects/clr`, `projects/hip`, `projects/rocr-runtime`, and `projects/hip-tests`.

Count this monorepo once. Its migration table identifies CLR, HIP, HIP tests, and ROCr as consolidated components; listing their previous repositories separately would duplicate the implementation. Engineers can study the relationship between a higher-level compute runtime and the lower-level HSA dispatch/memory interface.

- **C1:** ROCr distinguishes fine-grained visibility from coarse-grained allocations whose ownership must be explicitly transferred. AQL barrier packets encode dependencies between dispatches.
- **C2:** HSA agents, queues, signals, and memory operations form reusable services underneath GPU programming models; CLR houses both HIP and OpenCL runtime work.
- **C3:** User-mode queues provide a direct dispatch path, while CLR documents separate HIP and OpenCL validation routes.

**Entry points:** [ROCr execution and memory semantics](https://github.com/ROCm/rocm-systems/blob/develop/projects/rocr-runtime/runtime/docs/what-is-rocr-runtime.rst); [CLR subsystem and tests](https://github.com/ROCm/rocm-systems/blob/develop/projects/clr/README.md).

### 3. [pocl/pocl](https://github.com/pocl/pocl)

**Language/role:** C/C++; Portable Computing Language, an extensible OpenCL implementation with CPU and GPU device backends.

PoCL is valuable for understanding how much of a heterogeneous runtime can be shared while compilation and command execution remain device-specific.

- **C1:** Device drivers must propagate event-state changes, callbacks, reference counts, and locking correctly. The developer guide explicitly identifies event handling as a source of data races; backing storage is allocated lazily per device.
- **C2:** `pocl_device_ops` separates discovery, memory, compilation, events, and optional SVM/image/device-transfer operations behind callbacks.
- **C3:** A simple synchronous command executor is deliberately distinguished from backend-specific batching; direct device-to-device migration can avoid staging through host memory.

**Entry point:** [Writing a PoCL device driver](https://portablecl.org/docs/html/driver_design.html), which identifies the implementation files and explains the callback contracts rather than merely listing supported targets.

### 4. [intel/llvm](https://github.com/intel/llvm)

**Language/role:** C/C++; study the `sycl` runtime and `unified-runtime` subprojects, not the entire LLVM-derived tree.

DPC++ supplies a substantial SYCL implementation with a runtime adaptation layer. Its independent SYCL/Unified Runtime functionality warrants inclusion alongside upstream LLVM's different OpenMP offload subsystem below.

- **C2:** Unified Runtime interposes a C API, loader, and adapter libraries between DPC++ and device runtimes. Plugin objects own backend adapter handles.
- **C1:** Kernel/program caching must distinguish device images, specialization constants, device sets, kernel names, and contexts; collapsing these identities incorrectly would reuse the wrong executable.
- **C3:** Separate in-memory and persistent caches address repeated runtime-object creation and JIT compilation, including application restarts.

**Entry points:** [Unified Runtime placement](https://github.com/intel/llvm/blob/sycl/sycl/doc/design/UnifiedRuntime.md); [kernel/program cache design](https://github.com/intel/llvm/blob/sycl/sycl/doc/design/KernelProgramCache.md). Unified Runtime is counted within this repository, not as another standalone entry.

### 5. [AdaptiveCpp/AdaptiveCpp](https://github.com/AdaptiveCpp/AdaptiveCpp)

**Language/role:** Primarily C++; heterogeneous compiler/runtime supporting SYCL and other C++ programming models, formerly hipSYCL/Open SYCL.

Study the boundary between a normal compiled runtime and header-level code that requires a device compiler. Kernel-launch glue passes callable objects into the runtime, allowing backend-specific syntax to remain outside it.

- **C2:** The architecture separates the SYCL interface, runtime, compiler, and glue; runtime backends are dynamically loaded plugins.
- **C1:** The runtime specification defines persistent buffer allocations, per-device data validity, conflicting accessor ranges, and submission-order dependencies.
- **C3:** Page-granularity data tracking makes a concrete tradeoff between dependency precision, transfer volume, and scheduling overhead. Lazy allocation and stable allocation identities help make costs predictable.

**Entry points:** [Architecture](https://github.com/AdaptiveCpp/AdaptiveCpp/blob/develop/doc/architecture.md); [runtime specification](https://github.com/AdaptiveCpp/AdaptiveCpp/blob/develop/doc/runtime-spec.md).

### 6. [CHIP-SPV/chipStar](https://github.com/CHIP-SPV/chipStar)

**Language/role:** C/C++; HIP/CUDA compilation and runtime portability through SPIR-V, OpenCL, and Level Zero.

This is a strong example of reconciling programming models that look similar but have incompatible details. It combines compiler transformations, a device bitcode library, and an implementation of the HIP host API.

- **C1:** Lowering handles dynamically sized shared memory, host-accessible device globals, textures, warp-sensitive operations, and kernel argument metadata. These are semantic translations, not textual renamings.
- **C2:** HIP API bindings use abstract backend classes with separate OpenCL and Level Zero implementations. Device functions are supplied through a reusable bitcode layer.
- **C3:** The compiler/runtime split makes it possible to inspect where work is performed once during translation versus at module registration or kernel launch.

**Entry point:** [Developer internals](https://github.com/CHIP-SPV/chipStar/blob/main/docs/Development.md), including transformation passes, runtime files, and pre-`main` registration. Portability remains bounded by backend capabilities and supported HIP features.

### 7. [kpet/clvk](https://github.com/kpet/clvk)

**Language/role:** C++; OpenCL implementation on Vulkan, using clspv for kernel compilation.

The queue implementation is a compact way to study translating an event-oriented compute API into Vulkan resource and submission machinery.

- **C1:** In-order dependencies are recorded explicitly because both an executor thread and the calling thread may execute commands. Memory initialization has its own locked state and retained completion event.
- **C3:** Command groups and batches address submission overhead. The enqueue path handles resource exhaustion by flushing and retrying while outstanding work may release resources.
- **C2:** OpenCL contexts, kernels, programs, queues, and memory objects remain recognizable components over a different backend API.

**Entry point:** [Queue implementation](https://github.com/kpet/clvk/blob/main/src/queue.cpp). The inspected source explicitly says out-of-order execution is ignored; do not infer every optional OpenCL capability from the project's OpenCL version label.

### 8. [vosen/ZLUDA](https://github.com/vosen/ZLUDA)

**Language/role:** Primarily Rust, with LLVM/native components; CUDA compatibility on non-NVIDIA GPUs, AMD-focused in the inspected documentation.

ZLUDA adds the binary/API compatibility perspective missing from source-portability libraries. Study its PTX transformation pipeline and how translated device code is prepared for later execution.

- **C1:** The pipeline normalizes predicates, resolves function pointers, inserts conversions and explicit memory operations, handles 32-bit addressing, and selects constrained floating-point behavior when required.
- **C2:** Distinct parser, translation, compiler, runtime, cache, and library-compatibility components support applications beyond a single kernel family.
- **C3:** A separate precompilation tool extracts device code and warms the cache in parallel, trading startup work against potentially compiling unused code.

**Entry points:** [PTX-to-LLVM pass orchestration](https://github.com/vosen/ZLUDA/blob/master/ptx/src/pass/mod.rs); [precompilation design and tradeoff](https://github.com/vosen/ZLUDA/blob/master/docs/src/precompiling.md). Inclusion does not assert universal CUDA, library, or GPU compatibility.

### 9. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language/role:** Primarily C/C++; relevant subsystem is `offload`, especially `libomptarget` and accelerator plugins.

This entry concerns the runtime behind compiler-directed accelerator execution. It is useful for understanding the ABI and data-mapping obligations that a directive-based programming interface hides from users.

- **C1:** The target runtime documents and implements alignment preservation for partially mapped structures: allocating a member range without compensating padding can misalign pointer fields on the GPU. It also distinguishes disabled and mandatory offload failure policies.
- **C2:** Target-independent runtime machinery cooperates with a plugin manager and device implementations, serving compiler-generated offload operations across accelerators.

**Entry points:** [Offload subsystem scope](https://github.com/llvm/llvm-project/blob/main/offload/README.md); [target-independent runtime implementation](https://github.com/llvm/llvm-project/blob/main/offload/libomptarget/omptarget.cpp). The subsystem README describes OpenMP offload as usable while the broader offload API is still being designed.

## Portable C++ execution and data abstractions

### 10. [kokkos/kokkos](https://github.com/kokkos/kokkos)

**Language/role:** C++; parallel execution and memory abstraction for heterogeneous HPC applications.

Kokkos is particularly instructive because data layout is part of portability, not merely a choice of kernel launcher. Study how execution spaces, memory spaces, and multidimensional views interact.

- **C1:** Memory accessibility is distinct from the execution space used for initialization. Ownership, unmanaged views, initialization, and host/device copies have explicit contracts.
- **C2:** Views combine element type, layout, memory space, and traits into a reusable data abstraction that works with parallel dispatch.
- **C3:** Default layouts vary with execution space to support GPU coalescing or CPU locality; initialization also addresses first-touch placement.

**Entry point:** [View programming guide](https://kokkos.org/kokkos-core-wiki/ProgrammingGuide/View.html), especially layout and data-placement sections. Its detailed contracts are more useful for implementation study than assuming all spaces behave like ordinary host arrays.

### 11. [llnl/RAJA](https://github.com/llnl/RAJA)

**Language/role:** C++; performance-portability layer for loops, reductions, and kernel execution.

RAJA is a useful contrast to frameworks centered on owning array containers: the programmer can retain a loop body and vary its execution policy independently.

- **C2:** Nested `KernelPolicy` statements describe loop ordering, execution mapping, tiling, and lambda invocation; views provide multidimensional indexing over existing storage.
- **C3:** The same kernel body can map to sequential execution, OpenMP loop collapse, or CUDA/HIP thread and block dimensions. Block-stride loops and explicit tile sizes expose hardware mapping without rewriting the computation.

**Entry point:** [Kernel execution-policy walkthrough](https://raja.readthedocs.io/en/v2025.12.2/sphinx/user_guide/tutorial/kernel_exec_pols.html), which includes concrete mappings and a reference-result comparison. This is a versioned architectural reference, not a claim that it documents every feature on the development branch.

### 12. [alpaka-group/alpaka](https://github.com/alpaka-group/alpaka)

**Language/role:** Header-only C++20; portable accelerator kernels and host-side execution abstractions.

The inspected default branch is `dev_v3.x`; its frame-based model should not be confused with older alpaka tutorials. It decomposes a virtual index domain into frames, maps worker threads to data, and exposes shared-memory caching and multidimensional views.

- **C2:** Kernel functors, argument adaptation, device selection, queues, and data views let one application combine different accelerator backends.
- **C1:** `KernelBundle` enforces kernel/argument transfer constraints, requires a const callable returning `void`, and passes stored arguments as const references because threads in a block share them.
- **C3:** Explicit frame caching and separate mapping of data to workers preserve control over locality and parallelism.

**Entry points:** [Current model and example](https://github.com/alpaka-group/alpaka/blob/dev_v3.x/README.md); [KernelBundle implementation](https://github.com/alpaka-group/alpaka/blob/dev_v3.x/include/alpaka/KernelBundle.hpp).

### 13. [libocca/occa](https://github.com/libocca/occa)

**Language/role:** C++ core with language interfaces; device, memory, kernel, and stream abstraction plus the OCCA Kernel Language.

OCCA is useful for studying a runtime-selected backend model driven by structured properties, including backend-specific overrides, rather than making every choice a C++ template parameter.

- **C2:** Device objects unify memory allocation, wrapped external memory, memory pools, streams, and kernels across execution modes.
- **C1:** The device implementation tracks references and rejects use of uninitialized/freed devices. Stream ordering is local: in-order operations on one stream do not establish completion order across streams.
- **C3:** Kernel construction uses source/property-derived hashes and backend build paths; the source also exposes unfinished cache-lifetime work, making it useful for assessing real complexity rather than assuming every cache path is complete.

**Entry points:** [Device implementation](https://github.com/libocca/occa/blob/main/src/core/device.cpp); [stream semantics](https://github.com/libocca/occa/blob/main/docs/guide/occa/device-streams.md). Some documentation sections are incomplete; no current release-support promise is inferred.

### 14. [ddemidov/vexcl](https://github.com/ddemidov/vexcl)

**Language/role:** C++; vector-expression programming layer targeting OpenCL, CUDA, and OpenMP.

VexCL belongs here for its code-generation and multi-device execution layer, rather than simply for having numerical operations. It shows how expression templates can drive a runtime compiler.

- **C2:** Compatible device vectors participate in compound expressions, user-defined functions, and generated kernels; vectors can span multiple compute devices.
- **C3:** A vector expression becomes one generated kernel, compiled when first encountered. Offline binary caches reduce repeated compilation, and the documentation distinguishes runtime scalar arguments from embedded constants that permit further specialization.
- **C1:** Expression compatibility requires both equal sizes and the same device set, an important invariant when operations are partitioned across devices.

**Entry point:** [Expression semantics and generated code](https://github.com/ddemidov/vexcl/blob/master/docs/expressions.rst). Numerical speed examples in that documentation are not treated as contemporary benchmark results.

### 15. [boostorg/compute](https://github.com/boostorg/compute)

**Language/role:** C++; OpenCL-backed containers, iterators, algorithms, and runtime kernel generation.

This is an algorithm-level portability layer whose implementation exposes queues, contexts, local memory, and generated kernels. It is useful for tracing a familiar generic interface down to actual GPU work.

- **C2:** Device iterators, callable objects, containers, and `meta_kernel` let the library build executable OpenCL code from reusable C++ algorithms.
- **C1:** Reduction code must coordinate local-memory updates with barriers and handle incomplete final blocks correctly.
- **C3:** Reduction dispatch distinguishes CPU and GPU paths and uses staged block reductions with temporary device storage, exposing launch and temporary-memory costs behind the generic API.

**Entry point:** [Reduction implementation](https://github.com/boostorg/compute/blob/master/include/boost/compute/algorithm/reduce.hpp). These are concrete engineering concerns, not a claim that parallel floating-point reduction reproduces sequential evaluation bit-for-bit.

## Vulkan, WebGPU, and explicit compute frameworks

### 16. [gfx-rs/wgpu](https://github.com/gfx-rs/wgpu)

**Language/role:** Rust; cross-platform graphics and computation API with native backends and browser WebGPU support.

Focus on compute pipelines, resource tracking, and the boundary between `wgpu-core` and `wgpu-hal`. The codebase is relevant despite also supporting graphics because these runtime services directly underpin general compute dispatch.

- **C1:** The core validates untrusted API use, tracks resource lifetimes and initialization, and generates usage-transition barriers. Command buffers recorded independently need their assumed initial states reconciled at submission.
- **C2:** An idiomatic public API sits over a validating core and an unsafe portable hardware abstraction, with different responsibilities assigned to each layer.
- **C3:** Deferred barrier generation and lazy buffer initialization show how safety semantics interact with recorded-command performance.

**Entry point:** [Internal architecture](https://wgpu.rs/doc/wgpu/documentation/internals/architecture/index.html), including submission-time tracking, synchronization, and memory initialization.

### 17. [google/dawn](https://github.com/google/dawn)

**Language/role:** Primarily C++; native WebGPU implementation and shader infrastructure. **Official GitHub mirror** of the project hosted on `dawn.googlesource.com`.

Study compute-capable WebGPU execution together with the separation between API validation, native backend translation, and command serialization.

- **C1:** `dawn_native` performs state tracking and validation; `dawn_wire` validates serialized commands before forwarding them. The documented test structure distinguishes validation, GPU end-to-end, internal, and fuzz testing.
- **C2:** Native and wire implementations share a procedure-table API, while backend directories implement D3D12, Metal, and Vulkan translation. Tint supplies shader-language translation.
- **C3:** The wire client intentionally performs little state tracking, moving heavier work to the server; procedure tables also support selecting execution paths without changing callers.

**Entry point:** [Repository and runtime architecture](https://github.com/google/dawn/blob/main/docs/dawn/overview.md). Its code-generation machinery supports a substantive runtime, not merely generated bindings.

### 18. [KomputeProject/kompute](https://github.com/KomputeProject/kompute)

**Language/role:** C++ with Python bindings; general-purpose compute framework over Vulkan.

Kompute offers a smaller codebase for studying how managers, sequences, operations, tensors, and algorithms organize explicit GPU work. Existing Vulkan applications can supply resources rather than surrendering ownership to the framework.

- **C1:** Ownership is acyclic, externally supplied resources retain explicit ownership boundaries, and destroyed resources cannot simply be rebuilt. Asynchronous completion includes operation `postEval` processing, not just waiting for a fence.
- **C2:** Reusable sequences and operations separate orchestration from particular shaders and tensors.
- **C3:** The documentation distinguishes asynchronous submission from actual parallel execution through queues, preventing misleading assumptions about overlap.

**Entry points:** [Memory-ownership architecture](https://github.com/KomputeProject/kompute/blob/master/docs/overview/memory-management.rst); [asynchronous operation semantics](https://github.com/KomputeProject/kompute/blob/master/docs/overview/async-parallel.rst). Older examples may use earlier API spellings.

### 19. [LuisaGroup/LuisaCompute](https://github.com/LuisaGroup/LuisaCompute)

**Language/role:** Primarily C++, with Rust and Python components; cross-platform compute framework originating in rendering research.

The relevant artifact is the reusable compute framework, not the separate LuisaRender application. Its C++ embedded DSL traces kernels into an AST, while typed resources and commands feed a unified runtime.

- **C2:** Frontend, runtime resource wrappers, and backend code generation/dispatch are separate components; CUDA, DirectX, Metal, and CPU implementations instantiate the shared interfaces.
- **C3:** Resource-usage information supports dependency discovery and command rescheduling. Stream delegates collect commands before committing them.
- **C1:** The stream implementation validates command/stream compatibility in debug builds and commits pending commands before synchronization; moving a delegate clears its former stream pointer to avoid duplicate ownership of the pending work.

**Entry points:** [Architecture overview](https://github.com/LuisaGroup/LuisaCompute/blob/stable/README.md); [stream implementation](https://github.com/LuisaGroup/LuisaCompute/blob/stable/src/runtime/stream.cpp).

### 20. [tracel-ai/cubecl](https://github.com/tracel-ai/cubecl)

**Language/role:** Rust; portable kernel language extension, JIT compiler, and compute runtimes.

CubeCL adds a compute-focused Rust design above raw GPU API wrappers. Its model maps kernel parallelism onto CUDA/HIP, WebGPU/Metal/Vulkan, and CPU execution, with specialization and autotuning.

- **C2:** The `Runtime` trait separates device enumeration, target properties, tensor-readability constraints, and the compute server/client relationship from any one backend.
- **C1:** Profiling failures and missing measurements are explicit states. In particular, the server distinguishes “no timing measured” from a genuine zero-duration result, preventing an invalid measurement from winning autotuning comparisons.
- **C3:** Shared server infrastructure centralizes profiling and runtime services across backends, while first-use client initialization and runtime tuning address repeated execution costs.

**Entry points:** [Runtime contract](https://github.com/tracel-ai/cubecl/blob/main/crates/cubecl-runtime/src/runtime.rs); [server implementation and profiling errors](https://github.com/tracel-ai/cubecl/blob/main/crates/cubecl-runtime/src/server/base.rs).

## Managed and dynamic language execution layers

### 21. [m4rs-mt/ILGPU](https://github.com/m4rs-mt/ILGPU)

**Language/role:** C#; .NET GPU JIT compiler and accelerator runtime.

ILGPU is useful for studying how managed-language methods become device kernels while the host retains typed launchers, accelerator objects, and memory ownership.

- **C1:** Implicitly grouped kernels cannot safely use shared memory or group/warp operations because participation is not guaranteed. Cache clearing also has explicit concurrency restrictions, and compiled kernels have driver-memory lifetimes beyond ordinary method calls.
- **C2:** Backend compilation, reusable IR contexts, accelerators, buffer views, and kernel-loading APIs separate compilation from execution.
- **C3:** Dynamically generated typed launcher delegates avoid boxing; weak-reference kernel caching and parallel compilation address host overhead and retention.

**Entry points:** [Kernel contracts](https://github.com/m4rs-mt/ILGPU/blob/master/Docs/03_Advanced/02_Kernels.md); [compiler/runtime internals](https://github.com/m4rs-mt/ILGPU/blob/master/Docs/03_Advanced/07_Inside-ILGPU.md).

### 22. [beehive-lab/TornadoVM](https://github.com/beehive-lab/TornadoVM)

**Language/role:** Primarily Java with native components; JVM heterogeneous compilation and task-graph execution.

TornadoVM makes the dataflow between Java methods and accelerator memory explicit through task graphs and execution plans. It supports both annotated loops and lower-level kernel programming.

- **C2:** Off-heap data types, task graphs, immutable graph snapshots, and execution plans form reusable layers around compiled methods and backend selection.
- **C1:** Parallel loop annotations require absence of cross-iteration dependencies; off-heap arrays need initialization, and reduction implementation differs between GPU workgroups and CPU execution.
- **C3:** Transfer policies distinguish first execution, every execution, and user-requested copy-back. Warmup installs compiled code in a cache, separating compilation from repeated execution.

**Entry point:** [Core programming and execution model](https://github.com/beehive-lab/TornadoVM/blob/master/docs/source/programming.rst), including transfer timing, reductions, and the distinction between graph definition and actual data movement.

### 23. [JuliaGPU/KernelAbstractions.jl](https://github.com/JuliaGPU/KernelAbstractions.jl)

**Language/role:** Julia; backend-independent kernel programming interface used with CUDA, ROCm, oneAPI, Metal, and CPU execution.

Study a relatively small abstraction layer that composes with separately implemented GPU backends and Julia's task scheduler.

- **C2:** Backend types and the associated host/device interface let common kernels and data adaptation work without callers knowing the backend's concrete array type.
- **C1:** Backend synchronization must yield cooperatively to Julia rather than blocking inside a foreign library. This is a scheduling contract, particularly relevant when communication and GPU computation overlap.
- **C3:** The same cooperative wait supports concurrency without monopolizing a host scheduling thread; generic `adapt` dispatch preserves backend-specific storage conversion.

**Entry point:** [Backend implementation contracts](https://juliagpu.github.io/KernelAbstractions.jl/dev/implementations/). The inspected development documentation places the core backend interface in the sibling KernelInterface package; backend implementations remain separate projects.

### 24. [JuliaGPU/CUDA.jl](https://github.com/JuliaGPU/CUDA.jl)

**Language/role:** Primarily Julia; CUDA kernel compilation, arrays, runtime integration, and library interfaces.

This is a vendor-specific runtime integration rather than a cross-vendor API. It earns a separate entry because coordinating GPU work with a garbage-collected, task-based language is substantial engineering. The repository's version-6 organization separates CUDACore and associated packages while retaining a coordinated CUDA.jl interface.

- **C1:** Each task has its own stream, library handles, and active device. Sharing results across task-local streams requires synchronization; ordinary CPU arrays and pinned memory have different asynchronous-transfer behavior.
- **C2:** Native Julia kernels and CUDA library operations participate in the same array and task execution model.
- **C3:** Cooperative waits, concurrent task submission, and reusable pinned buffers expose concrete ways to overlap host/device work while accounting for pinning costs.

**Entry point:** [Tasks and threads](https://cuda.juliagpu.org/stable/usage/multitasking/), with worked synchronization and transfer examples. The documentation's own multithreading caveat should be retained when applying these patterns.

### 25. [inducer/pyopencl](https://github.com/inducer/pyopencl)

**Language/role:** Python and C++; OpenCL runtime integration, arrays, memory-management helpers, and parallel-programming facilities.

PyOpenCL goes beyond mechanically generated bindings: its memory interfaces reconcile OpenCL object lifetimes, NumPy storage, and Python garbage collection.

- **C1:** SVM pointers lack OpenCL buffer reference-counting protection. Garbage collection can free memory while GPU operations still use it; queue-associated deallocation provides a concrete ordering mechanism. Deferred device allocation also changes when out-of-memory failures appear.
- **C2:** Buffer objects, opaque and NumPy-wrapped SVM, mapping objects, allocators, and pools support multiple storage/interop use cases through common interfaces.
- **C4:** The API documentation records evolution from earlier buffer ownership interfaces through SVM introduction in 2016 and substantial deallocation/representation changes in 2022, with explicit version-gated compatibility behavior.

**Entry point:** [Memory runtime reference and SVM design](https://documen.tician.de/pyopencl/runtime_memory.html), including ownership transfer, mapping events, and allocation/deallocation semantics.

## Coverage, search process, and limits

Discovery used more than six distinct live-search formulations, including: GPU runtimes with SYCL/OpenCL/HIP; Rust and Vulkan/WebGPU portability; HPC execution/memory frameworks; OpenCL-on-Vulkan and HIP-on-SPIR-V; Julia/.NET/JVM runtime integration; ROCm repository migrations; lightweight Vulkan compute frameworks; Rust JIT/autotuning runtimes; and CUDA binary compatibility. Follow-up searches for alternative Java and mobile/Vulkan layers increasingly returned already-covered implementations, forks, wrappers, and application-specific projects. Those searches helped check diversity rather than supplying unverified entries.

Every retained canonical GitHub repository was opened, and repository metadata was checked through the GitHub API. All 25 were non-archived at inspection. This status is not evidence of a support commitment or sustained quality. Each entry also has an independently opened design document, API explanation, or source implementation beyond the root repository page. The linked entry points are the material actually inspected. No candidate was cloned, installed, executed, or benchmarked.

Important boundaries and exclusions:

- ROCm's migrated HIP/CLR/ROCr repositories and the Unified Runtime subtree are not counted twice. Old OpenSYCL/hipSYCL names and Kompute forks are not independent entries. Dawn is explicitly identified as an official substantive mirror.
- Proprietary CUDA runtime internals cannot be studied through a public GitHub implementation; the selection instead includes open implementations, compatibility projects, and language integrations. A standards specification, ICD header/loader, or compiler-only translation tool does not automatically qualify as a substantive runtime.
- General tensor frameworks, vendor BLAS collections, GPU simulators, renderer applications, tutorials, and awesome-lists were outside the core scope. Smaller candidates such as VUDA and alternative JVM bindings were discovered but not promoted merely to increase the count. This is a selection, not an exhaustive census.
- Search results and documentation can lag source changes. In particular, alpaka's inspected default branch contains the newer frame-based model, RAJA's linked walkthrough is versioned, and some OCCA/Kompute documentation is incomplete or describes older API spellings. ZLUDA's documentation also contains historical roadmap material; no projected milestone is reported as accomplished here.
- **Interpretation:** Statements that particular invariants or abstractions make a project useful to study are grounded engineering judgments from the cited material. Backend lists are not performance-equivalence claims. C4 is used sparingly, and neither stars nor recent pushes were treated as evidence for it.
