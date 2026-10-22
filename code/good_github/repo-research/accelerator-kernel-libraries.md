# Accelerator kernel libraries

Research date: **2026-10-09**.

This report selects **25 GitHub repositories** containing reusable accelerator kernels, kernel-building primitives, or libraries that generate substantial computational kernels. Coverage includes CUDA, HIP/ROCm, SYCL/ESIMD, OpenCL, Vulkan, Metal, Rust/CubeCL, AWS Neuron, and FPGA/AI Engine implementations. In larger repositories, the entry identifies the relevant subsystem. General compiler frameworks, device drivers, thin bindings, and full inference engines are outside the main scope.

Repository identities, default branches, and archive flags were checked through the public GitHub API. The linked implementation and documentation files were read separately from each repository's top-level README. Criteria are engineering judgments grounded in those sources, not claims that every component is equally strong. No kernels were built or benchmarked for this report; performance discussion concerns mechanisms rather than independently measured speedups.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions supporting many use cases. **C3** — real performance constraints addressed through understandable architecture. **C4** — sustained evolution with evidence of compatibility, testing, or complexity management. A recent push or an old creation date alone does not establish C4.

## Vendor foundations and kernel construction

### 1. [NVIDIA/cutlass](https://github.com/NVIDIA/cutlass)

**Language/role:** CUDA C++ and Python DSLs; matrix multiplication, convolution, and tensor-operation building blocks, including CuTe. Study how a library exposes instruction-level features while keeping data layout, mainloop scheduling, and epilogues composable.

- **C1, C2:** CuTe's multidimensional `Layout` and `Tensor` vocabulary makes thread-to-data mappings explicit and permits compile-time checks on static coordinate transformations. The 3.x design replaces many bespoke iterator types with shared abstractions and policy-based dispatch. **C3:** the same design explains why algorithm-centered layers accommodate warp-group instructions and asynchronous data movement better than a hierarchy rigidly tied to older hardware. Start with the [3.x design document](https://github.com/NVIDIA/cutlass/blob/main/media/docs/cpp/cutlass_3x_design.md).
- **C4:** the [changelog](https://github.com/NVIDIA/cutlass/blob/main/CHANGELOG.md) spans the 2017 initial release through subsequent architecture generations. Its 3.0 entry documents adapters allowing 2.x and 3.x kernels to coexist, providing concrete compatibility evidence alongside the architectural redesign.

### 2. [NVIDIA/cccl](https://github.com/NVIDIA/cccl)

**Language/role:** CUDA C++; the consolidated home of CUB, Thrust, and libcudacxx. The most direct category fit is CUB's device-, block-, and warp-level algorithms. Count these components once, rather than listing their former repositories separately.

- **C1, C3:** [CUB's block reduction implementation](https://github.com/NVIDIA/cccl/blob/main/cub/cub/block/block_reduce.cuh) distinguishes algorithms that require commutative operators from those preserving noncommutative ordering. It explains register accumulation, shared-memory exchange, warp reductions, and the throughput-versus-latency tradeoff between variants.
- **C2:** those collectives provide reusable building blocks beneath complete device algorithms and higher-level Thrust interfaces. The [CUB testing guide](https://github.com/NVIDIA/cccl/blob/main/docs/cub/developer/test_overview.rst) shows how this broad surface is checked against host references, including floating-point corner cases, iterator variation, large offsets, determinism, and expected compilation failures. This is a useful study of testing a generic parallel library, without assuming that tests alone prove correctness.

### 3. [ROCm/rocm-libraries](https://github.com/ROCm/rocm-libraries)

**Language/role:** Primarily HIP/C++ with Python tooling; AMD's consolidated library repository. Focus here on `projects/composablekernel`, while recognizing that rocPRIM, rocFFT, MIOpen, and hipBLASLt are also consolidated components. The root migration table identifies the super-repository as their source of truth; old component repositories are not additional selections.

- **C2:** Composable Kernel separates templated tile operators, templated kernels/invokers, instantiated kernels/invokers, and a client API. The [structure document](https://github.com/ROCm/rocm-libraries/blob/develop/projects/composablekernel/docs/conceptual/Composable-Kernel-structure.rst) provides a concise map for navigating this substantial subsystem.
- **C1, C3:** [CK Tile's distribution design](https://github.com/ROCm/rocm-libraries/blob/develop/projects/composablekernel/docs/conceptual/ck_tile/tile_distribution.rst) maps physical tensor coordinates, access patterns, processing elements, and optional replication through compile-time transformations. It makes coalescing, thread cooperation, and bank-conflict avoidance part of an explicit layout model. Study the distinction between logical tensor organization and the physical work assigned to GPU threads.

### 4. [intel/xetla](https://github.com/intel/xetla)

**Language/role:** C++ SYCL/ESIMD templates for Intel Xe matrix and fused kernels. **Archived and explicitly unmaintained:** the repository states that Intel has ceased development and no longer accepts patches. Retain it as a historical implementation study, not a current support recommendation.

- **C2:** the [programming guidelines](https://github.com/intel/xetla/blob/main/media/docs/programming_guidelines.md) distinguish kernel, group, and subgroup APIs. GEMM dispatch policies, matrix descriptors, accumulator tiles, and epilogues allow the same building blocks to be reused in different fused operations.
- **C1, C3:** the guidelines explain where responsibility for shared local memory, barriers, registers, prefetch, and workgroup partitioning changes between abstraction levels. Group-level access to accumulators permits post-operations before global stores; subgroup APIs expose the synchronization obligations underlying that flexibility. This makes XeTLA valuable for comparing Intel DPAS/2D-block operations with CUDA-oriented tile libraries.

### 5. [uxlfoundation/oneDNN](https://github.com/uxlfoundation/oneDNN)

**Language/role:** C++ with generated GPU assembly, OpenCL, and SYCL implementations; neural-network primitives. The relevant subsystem is `src/gpu`, especially Intel GPU JIT kernels, rather than the separately substantial CPU implementation.

- **C2, C3:** the [GPU JIT architecture](https://github.com/uxlfoundation/oneDNN/blob/main/src/gpu/intel/jit/README.md) explains nGEN instruction generation, reusable low-level injectors, and an intermediate representation transformed by optimization passes. It explicitly balances common building blocks against necessary hardware specialization.
- **C1:** [scratchpad documentation](https://github.com/uxlfoundation/oneDNN/blob/main/doc/functional_api/programming_model/attributes_scratchpad.md) distinguishes temporary execution storage from training workspace and spells out concurrency restrictions for library-managed and user-managed memory. The instructive problem is not merely computing a primitive: it is keeping temporary-buffer lifetime and concurrent execution compatible with a reusable primitive API.

### 6. [ARM-software/ComputeLibrary](https://github.com/ARM-software/ComputeLibrary)

**Language/role:** C++ and OpenCL, alongside CPU assembly; low-level vision and machine-learning kernels. Focus on the Mali GPU/OpenCL subsystem and its scheduling interfaces.

- **C1, C2:** the [implementation guide](https://github.com/ARM-software/ComputeLibrary/blob/main/docs/contributor_guide/implementation_topics.dox) gives explicit bounds, step, and divisibility invariants for splitting execution windows. Its configure/window/run interface and OpenCL queue example show how a common kernel contract organizes different operations.
- **C3, C4:** the [historical changelog](https://github.com/ARM-software/ComputeLibrary/blob/main/docs/user_guide/release_version_and_change_log.dox) records years of kernel changes, GPU fusion work, OpenCL dispatch changes, deprecations, and reductions in host-side kernel-flushing overhead. It also explains the transition to release-page changelogs after v24.08. Study how performance tuning coexists with evolving API and library boundaries; the historical file is not the complete current release history.

## Portable primitives, sparse kernels, and transforms

### 7. [kokkos/kokkos-kernels](https://github.com/kokkos/kokkos-kernels)

**Language/role:** C++; local dense, sparse, batched, and graph kernels using Kokkos execution and memory abstractions. These are reusable computational kernels, distinct from the Kokkos programming framework itself.

- **C1:** the [sparse matrix multiplication symbolic API](https://github.com/kokkos/kokkos-kernels/blob/develop/docs/source/API/sparse/spgemm_symbolic.rst) documents symbolic versus numeric phases, handle state, output allocation, optional row-map computation, and conditional sortedness requirements. It also explicitly rejects transposed cases despite exposing transpose arguments. These contracts matter for avoiding incorrect assumptions in generic sparse code.
- **C2, C3:** the root documentation separates public interfaces from implementation specializations and correctness/performance tests. This permits precompiled specializations while preserving a common view-based interface. The [developer guide](https://github.com/kokkos/kokkos-kernels/blob/develop/DEVELOPER.md) explains transitive Kokkos configuration and optional vendor BLAS/sparse-library integration. Study the boundary between portable kernels and specialized external implementations.

### 8. [CNugteren/CLBlast](https://github.com/CNugteren/CLBlast)

**Language/role:** C++ and OpenCL C; tunable BLAS kernels for multiple vendors and device classes. Particularly useful for understanding when an ostensibly faster inner kernel loses after preparation costs are included.

- **C1, C3:** the [GEMM implementation guide](https://github.com/CNugteren/CLBlast/blob/master/doc/details_gemm.md) contrasts direct kernels with an indirect pipeline that prepares matrices to satisfy layout and size assumptions. Direct kernels handle incomplete tiles; indirect kernels can simplify computation but pay preprocessing and postprocessing costs.
- **C2:** the same matrix-operation interface is backed by reusable tuning parameters for workgroup sizes, register tiles, vector widths, unrolling, and local memory. The [tuning guide](https://github.com/CNugteren/CLBlast/blob/master/doc/tuning.md) documents device-specific configuration and fallback choices for unfamiliar hardware. It is a concrete example of separating numerical operation semantics from a searchable implementation space.

### 9. [DTolm/VkFFT](https://github.com/DTolm/VkFFT)

**Language/role:** C-style header implementation with backend integration code; runtime-generated multidimensional FFT kernels for Vulkan, CUDA, HIP, OpenCL, Level Zero, and Metal. This provides meaningful coverage of Apple GPUs and graphics-compute APIs.

- **C1, C2:** the [API guide source](https://github.com/DTolm/VkFFT/blob/master/documentation/VkFFT_API_guide.tex) describes transform normalization, strides, precision modes, buffer roles, and Bluestein auxiliary storage. These are substantive numerical and memory-layout contracts beneath one configurable transform interface.
- **C3:** the [axis planner](https://github.com/DTolm/VkFFT/blob/master/vkFFT/vkFFT/vkFFT_PlanManagement/vkFFT_Plans/vkFFT_Plan_FFT.h) specializes generated kernels using transform dimensions, batching, warp size, shared-memory organization, prime-transform choices, and backend details. Study how a shared planning model feeds several execution APIs while avoiding a separate handwritten implementation for every transform shape. Performance and precision depend on configuration; the report does not adopt the README's comparative benchmark claims.

### 10. [clMathLibraries/clFFT](https://github.com/clMathLibraries/clFFT)

**Language/role:** C++ host implementation and generated OpenCL FFT kernels. **Historical selection:** GitHub does not mark it archived, but the API reported its last push as 2022-10-05. No active-maintenance claim is made.

- **C1, C2:** the [library documentation source](https://github.com/clMathLibraries/clFFT/blob/master/src/library/mainpage.h) separates plan-time parameters from execution-time buffers and direction. It documents complex/real layouts, strides, in-place permissions, context reference lifetimes, asynchronous queues, and thread-safety expectations. Study the state and ownership model around runtime-generated FFTs.
- **C3:** batching amortizes submission overhead, and reusable plans separate preparation from repeated transforms. The [historical changelog](https://github.com/clMathLibraries/clFFT/blob/master/CHANGELOG) makes failure modes concrete: temporary-buffer races, lifetime fixes, radix-specific failures, and bank-conflict improvements. It is useful historical evidence, but its old entries should not be mistaken for a current compatibility matrix.

### 11. [moderngpu/moderngpu](https://github.com/moderngpu/moderngpu)

**Language/role:** Header-only CUDA C++; primitives for irregular parallel work. A relatively compact alternative to vendor-scale repositories for studying segmented operations and load distribution.

- **C1:** [segmented reduction](https://github.com/moderngpu/moderngpu/blob/master/src/moderngpu/kernel_segreduce.hxx) explicitly tracks segment boundaries, carry-in/carry-out values, empty segments, and segments crossing thread-block tiles. A follow-up reduction fixes partial results spanning blocks.
- **C2, C3:** templated operators, iterators, contexts, and cooperative primitives make this machinery reusable. The implementation separates intra-block accumulation from cross-block fixup rather than hiding all irregularity in one kernel. The [segmented-reduction test](https://github.com/moderngpu/moderngpu/blob/master/tests/test_segreduce.cu) generates random segment boundaries and checks a host-computed result. Its test style is worth inspecting critically: the shown mismatch path exits with status zero, so it is evidence of verification intent, not a blanket endorsement of CI failure signaling.

### 12. [boostorg/compute](https://github.com/boostorg/compute)

**Language/role:** C++ metaprogramming and generated OpenCL C; containers, iterators, and parallel algorithms. The reusable algorithm implementations make this more than an OpenCL API wrapper.

- **C2:** the [design document](https://github.com/boostorg/compute/blob/master/doc/design.qbk) distinguishes the thin device/context layer from STL-like algorithms and composable transform/permutation iterators. It also explains interoperability with existing OpenCL code.
- **C1, C3:** the [GPU reduction implementation](https://github.com/boostorg/compute/blob/master/include/boost/compute/algorithm/detail/reduce_on_gpu.hpp) generates kernels with private accumulation, bounded tail loads, shared-memory reduction, barriers, and configurable work sizes. Source generation and parameter/program caches expose the mechanics behind a familiar algorithm interface. Some code contains hardware-specific warp assumptions, making it a useful subject for portability review rather than grounds to assume every optimization suits every current device.

### 13. [ddemidov/vexcl](https://github.com/ddemidov/vexcl)

**Language/role:** C++ expression templates generating OpenCL/CUDA kernels; vector arithmetic, reductions, and sparse operations across devices.

- **C1, C2:** the [expression documentation](https://github.com/ddemidov/vexcl/blob/master/docs/expressions.rst) requires participating vectors to have matching sizes and device sets. It exposes generated kernel examples, constant-versus-runtime arguments, command-queue selection, and kernel caching. These details make the abstraction inspectable rather than purely declarative.
- **C3:** [multiexpressions](https://github.com/ddemidov/vexcl/blob/master/docs/multiexpr.rst) combine several output expressions into one generated kernel through multivectors or `vex::tie`. The two-dimensional rotation example shows precisely which independent assignments can be fused to reduce launches. Study the connection between C++ expression structure, device partitioning, and generated memory traffic.

### 14. [tracel-ai/cubek](https://github.com/tracel-ai/cubek)

**Language/role:** Rust/CubeCL; reusable matmul, convolution, attention, reduction, quantization, and random kernels. This is the kernel-library selection; the underlying CubeCL language/compiler is not counted separately.

- **C2, C3:** the [kernel development guide](https://github.com/tracel-ai/cubek/blob/main/GUIDE.md) separates a minimal compile-time `Blueprint`, a hardware-adapting `Routine`, and an autotuner. Keeping shapes and strides at runtime limits unnecessary JIT variants, while structural choices specialize code.
- **C1:** the guide explains validation before launch, boundary strategies, and shared iteration-space descriptions that prevent operands from disagreeing about partitioning. The [test utilities guide](https://github.com/tracel-ai/cubek/blob/main/crates/cubek-test-utils/README.md) documents host-reference comparisons and distinguishes numerical failures from unsupported compilation configurations. Its default `correct` policy accepts compilation errors; use the documented `strict` policy when assessing complete support for a particular configuration.

## Attention, fusion, and low-precision operator libraries

### 15. [Dao-AILab/flash-attention](https://github.com/Dao-AILab/flash-attention)

**Language/role:** CUDA C++, Python, and CuTe DSL, with AMD implementations also present; exact attention kernels. Study how an IO-aware algorithm becomes a family of implementations with masking, variable lengths, dropout, and differentiated execution paths.

- **C1, C3:** the [softmax implementation](https://github.com/Dao-AILab/flash-attention/blob/main/csrc/flash_attn/src/softmax.h) maintains running maxima and sums and rescales accumulated outputs as new tiles arrive. It handles all-masked negative-infinity rows and delays some cross-thread summation until normalization, directly connecting numerical semantics with work reduction.
- **C2:** the operator family supports packed and variable-length inputs and several attention configurations. The [tests](https://github.com/Dao-AILab/flash-attention/blob/main/tests/test_flash_attn.py) exercise causal/local masking, MHA/MQA/GQA, dropout, deterministic modes, and non-power-of-two dimensions. These provide useful examples of the combinatorial correctness surface hidden behind a single attention API.

### 16. [flashinfer-ai/flashinfer](https://github.com/flashinfer-ai/flashinfer)

**Language/role:** CUDA C++ and Python; inference kernels and kernel generation for attention, GEMM, MoE, sampling, and related serving operations. Inspect its own attention abstractions, even where other operations dispatch to external backends.

- **C1, C2:** the [KV-cache layout guide](https://github.com/flashinfer-ai/flashinfer/blob/main/docs/tutorials/kv_layout.rst) specifies ragged offsets, page indices, valid last-page lengths, layout alternatives, and packed-mask representation. It explicitly warns about index-width requirements. These reusable formats support changing sequence lengths without padding every request to a common size.
- **C3:** [recursive attention](https://github.com/flashinfer-ai/flashinfer/blob/main/docs/tutorials/recursive_attention.rst) represents partial results as attention states and merges them using normalized values and log-sum-exp statistics. This enables shared-prefix reuse and splitting a long KV dimension across blocks. The associativity described is mathematical; it should not be read as a promise of bitwise equality under arbitrary floating-point reduction orders.

### 17. [HazyResearch/ThunderKittens](https://github.com/HazyResearch/ThunderKittens)

**Language/role:** CUDA C++; register/shared-memory tiles, collective operations, and complete GPU kernels. The repository's library is substantive beyond its educational examples; those examples make a convenient route into the abstractions.

- **C2:** tile types, memory-space views, shared allocators, semaphores, and warp-group operations compose into matmul and attention kernels. The [Hopper GEMM progression](https://github.com/HazyResearch/ThunderKittens/blob/main/kernels/gemm/educational_h100/README.md) is a manageable study path through increasingly involved scheduling choices.
- **C1, C3:** its [level-seven GEMM](https://github.com/HazyResearch/ThunderKittens/blob/main/kernels/gemm/educational_h100/level_07.cu) shows a double-buffered producer/consumer pipeline: asynchronous TMA loads, full/empty semaphore phases, register-budget changes, and explicit completion before buffer reuse. The synchronization protocol is visible in a short source file. The root README also states that further active Ampere support is no longer planned; do not infer uniform support across NVIDIA generations.

### 18. [deepseek-ai/DeepGEMM](https://github.com/deepseek-ai/DeepGEMM)

**Language/role:** CUDA C++ and Python/JIT integration; tensor-core GEMM and related LLM kernels. Particularly useful for studying specialized low-precision computation without needing to begin with an entire inference engine.

- **C1:** the [SM90 FP8 GEMM implementation](https://github.com/deepseek-ai/DeepGEMM/blob/main/deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d1d.cuh) asserts scaling granularity, thread-group requirements, accumulator type, and shared-memory alignment. Its template parameters distinguish grouped layouts and TMA/mathematical workers.
- **C2, C3:** the code separates scheduling, memory transfer, MMA, and other reusable machinery from concrete kernels. A particularly small entry point is [the ring pipeline helper](https://github.com/deepseek-ai/DeepGEMM/blob/main/deep_gemm/include/deep_gemm/common/ring_pipeline.cuh), which tracks stage and phase and optimizes power-of-two stage counts. Its comment also exposes an essential precondition: callers advance by at most one full ring. Study these contracts before treating a specialized kernel as a general BLAS substitute.

### 19. [ROCm/aiter](https://github.com/ROCm/aiter)

**Language/role:** Python/Triton, HIP/C++, and assembly; AMD AI operators with multiple implementation backends. This remains a separate project from the consolidated ROCm math-library repository.

- **C1:** the [online softmax kernel](https://github.com/ROCm/aiter/blob/main/aiter/ops/triton/_triton_kernels/softmax.py) maintains a running maximum, rescales the previously accumulated exponential sum, masks tail loads, and makes a second pass to produce normalized output. It is a compact numerical kernel to read before exploring larger operators.
- **C2, C3:** the [MoE kernel-generation and tuning guide](https://github.com/ROCm/aiter/blob/main/csrc/ck_gemm_moe_2stages_codegen/README.md) connects reusable operator interfaces to shape-, quantization-, and device-specific configuration. It describes one-stage versus two-stage selection, tuned configuration files, JIT rebuilding, and candidate pruning. Its explicit statement that pruning speedup has not been measured is a useful boundary between an architectural optimization rationale and a benchmark claim.

### 20. [pytorch/FBGEMM](https://github.com/pytorch/FBGEMM)

**Language/role:** C++/CUDA and Python; select the **FBGEMM_GPU** operator subsystem, including recommendation and generative-AI workloads. The CPU FBGEMM package and GPU packages count as one repository.

- **C1, C2:** the [jagged-tensor format](https://github.com/pytorch/FBGEMM/blob/main/fbgemm_gpu/docs/src/fbgemm_gpu/overview/jagged-tensor-ops/JaggedTensorOps.rst) separates values, nested offsets, and maximum lengths. Its offset invariants and empty-subsequence examples expose the representational difficulty behind reusable variable-length operators.
- **C3:** the [jagged softmax kernel](https://github.com/pytorch/FBGEMM/blob/main/fbgemm_gpu/src/jagged_tensor_ops/jagged_softmax_forward.cu) operates directly on that representation using bounded sequence lengths, block reductions, grid-stride traversal, and synchronization between maximum, exponential-sum, and output phases. This offers a concrete route from an irregular data abstraction to GPU work scheduling. The format overview's short operation inventory is historical; the inspected source demonstrates a broader implementation surface.

### 21. [bitsandbytes-foundation/bitsandbytes](https://github.com/bitsandbytes-foundation/bitsandbytes)

**Language/role:** CUDA/HIP C++ and Python; low-bit quantization, quantized linear operations, and memory-efficient optimizers. Focus on the actual kernels beneath the PyTorch interface.

- **C1:** [the kernel implementation](https://github.com/bitsandbytes-foundation/bitsandbytes/blob/main/csrc/kernels.cu) computes block-local absolute maxima, normalizes values, encodes FP4/NF4 or general 8-bit data, and packs two 4-bit values per byte. Tail counts, scale storage, and optional stochastic quantization are part of the correctness problem, not just datatype conversion.
- **C2, C3:** templated kernels reuse block loading, reduction, and storing machinery across formats. The small-block path packs several quantization blocks into one wavefront, while load/store choices account for CUDA/RDNA versus CDNA warp sizes. Study how the numerical block size interacts with the execution width. Accelerator support is operation-specific, as the root README's support matrix makes clear; no blanket backend parity is implied.

### 22. [linkedin/Liger-Kernel](https://github.com/linkedin/Liger-Kernel)

**Language/role:** Python/Triton and additional backend implementations; fused training and post-training operators. This is a useful source for understanding activation-memory reduction together with autograd semantics.

- **C1, C3:** [fused linear cross entropy](https://github.com/linkedin/Liger-Kernel/blob/main/src/liger_kernel/ops/fused_linear_cross_entropy.py) chunks tokens to bound transient vocabulary-sized logits. The code distinguishes accumulation dtypes, ignored targets, class weights, and per-token upstream gradients; memory savings cannot be separated from preserving these gradient semantics.
- **C2:** [FlexChunkLoss](https://github.com/linkedin/Liger-Kernel/blob/main/src/liger_kernel/chunked_loss/README.md) provides reusable preference and distillation base classes. They manage chunking, fusion, and compilation while subclasses supply a loss on each chunk. The document explains computing gradients during the forward work to reduce retained intermediates. The project combines handwritten kernels and PyTorch/compiler composition, so its components should be studied at their actual implementation level.

### 23. [flagos-ai/FlagGems](https://github.com/flagos-ai/FlagGems)

**Language/role:** Python/Triton; generic PyTorch-compatible accelerator operators. The verified canonical owner is **flagos-ai**; older `FlagOpen/FlagGems` links redirect here.

- **C1, C2:** the [pointwise-generation design](https://github.com/flagos-ai/FlagGems/blob/master/docs/content/en/overview/pointwise-dynamic.md) handles arbitrary ranks, noncontiguous strides, broadcasting, mixed scalar/tensor inputs, type promotion, and preallocated outputs. A reusable decorator generates indexing and launch wrappers around the scalar operation.
- **C3:** the design avoids making tensors contiguous merely to simplify kernels, preserving the memory-bound character of pointwise work. The [backend adaptation guide](https://github.com/flagos-ai/FlagGems/blob/master/src/flag_gems/runtime/backend/README.md) separates vendor descriptors, heuristics, autotuning configurations, and operator overrides. Study how a common operator surface accommodates heterogeneous accelerators; the existence of a backend directory alone is not evidence of equal completeness or performance.

## Non-GPU accelerator kernels

### 24. [aws-neuron/nki-library](https://github.com/aws-neuron/nki-library)

**Language/role:** Python using the Neuron Kernel Interface; reference and optimized kernels for AWS Neuron accelerators, including attention, MLP, MoE, projections, and normalization. This is the reusable kernel library rather than the separate tutorial/sample repository.

- **C1, C3:** the [token-generation attention design](https://github.com/aws-neuron/nki-library/blob/main/src/nkilib_src/nkilib/core/attention/attention_tkg_design_spec.md) distinguishes batch sharding from sequence sharding across NeuronCores. It explains online-softmax state and postponing cross-core max/sum/output exchange until finalization so communication does not contend with value prefetch during the tile loop.
- **C2:** these kernels expose distinct context-encoding and token-generation operations with shared infrastructure. The [test-framework guide](https://github.com/aws-neuron/nki-library/blob/main/test/README.md) maps tests to kernel modules and separates numerical simulation, compile-only checks, and hardware execution. That distinction is valuable when studying an accelerator ecosystem where compilation success and simulated accuracy are insufficient evidence of hardware behavior.

### 25. [Xilinx/Vitis_Libraries](https://github.com/Xilinx/Vitis_Libraries)

**Language/role:** C/C++ HLS and AI Engine code, with host integration; reusable FPGA and adaptive-compute kernels. Relevant subsystems include BLAS, DSP, and vision. Count the monorepository once.

- **C1, C3:** the [HLS GEMM implementation](https://github.com/Xilinx/Vitis_Libraries/blob/main/blas/L1/include/hw/xf_blas/gemm.hpp) expresses stream-based systolic computation through templates, pipelining, array partitioning, and unrolled multiply-accumulate cells. Tagged flush boundaries and buffer-dimension assertions expose temporal invariants that differ substantially from GPU thread-block programming.
- **C2:** the [vision library guide](https://github.com/Xilinx/Vitis_Libraries/blob/main/vision/README.md) explains the L1 kernel, L2 packaged-kernel, and L3 application organization, with C simulation, synthesis, co-simulation, and hardware flows. **Status limitation:** the root README deprecates several programmable-logic libraries starting with 2025.2, including sparse, HPC, graph, and data-compression libraries, and drops some platforms. The repository is substantial, but maintenance must be assessed by subsystem and release.

## Search coverage and limitations

Discovery used more than six distinct live-web formulations, covering: CUDA tile and collective primitives; AMD CK/rocPRIM/Tensile/AITER; Intel SYCL/ESIMD; OpenCL BLAS and generated kernels; Vulkan/Metal FFTs; sparse and graph kernels; attention and serving kernels; Triton training/operator libraries; AWS Neuron and Ascend; Rust accelerator kernels; and FPGA/HLS/AI Engine libraries. Later searches were useful chiefly for filling Rust and FPGA gaps; other results increasingly repeated established projects, bindings, educational reimplementations, or compiler frameworks.

Primary verification combined GitHub repository metadata, README scope checks, and separate source/design/test documents. The ROCm recursive tree response was truncated because of repository size; the specific retained CK documents were nevertheless individually fetched and read. Canonical redirects were resolved, including FlagGems and oneDNN. CCCL and ROCm component consolidation were handled explicitly, and no fork or old component repository was counted as an independent duplicate.

Important exclusions include closed-source cuBLAS/cuDNN implementations, wrapper-only packages, tutorial-only attention kernels, full serving frameworks, and compiler-first projects such as Triton, TileLang, and CubeCL. Ginkgo was inspected but omitted to keep the selection centered on kernel libraries rather than sparse solver frameworks. Ascend-focused searches found additional projects, including the newly announced DeepGEMM-Ascend; it was not developed into a separately verified entry here. Coverage is therefore broad, not exhaustive, particularly for Ascend, TPU, and smaller embedded NPUs.

XeTLA's archive status, clFFT's historical status, Vitis subsystem deprecations, and selected testing limitations are recorded rather than hidden. Source links generally follow the verified default branch and may evolve. Numerical speedups, uniform device support, and production suitability were not independently established. The suggested study value and criterion assignments are grounded in the inspected architecture and code, and remain a selection guide rather than a code-quality certification.
