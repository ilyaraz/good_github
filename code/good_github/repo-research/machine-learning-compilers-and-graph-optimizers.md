# Machine learning compilers and graph optimizers

Research date: **2026-10-09**.

This report selects **27 GitHub repositories** for studying the engineering of machine learning compilation: graph rewriting, tensor IRs, fusion, scheduling, memory planning, numerical semantics, distributed partitioning, and hardware lowering. It includes compiler subsystems in larger frameworks, reusable compiler infrastructure, embedded and FPGA toolchains, and substantial research implementations. Each monorepo appears once, with the relevant subsystem identified. The links within each entry are reading entry points and primary evidence, not merely project homepages.

The criteria below describe reasons to study a codebase, not a guarantee that every component is exemplary or that it is ready for a new deployment. Statements about architectural value are grounded engineering judgments. Canonical URLs, default branches, and archive flags were checked through GitHub's repository API. An unarchived repository is not, by itself, evidence of active maintenance; material status caveats appear below.

- **C1 — Difficult correctness:** meaningful invariants, aliasing, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or representations supporting multiple operators, models, targets, or integrations.
- **C3 — Performance with structure:** real execution or compilation constraints addressed through an understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or complexity management; age alone does not qualify.

## Compiler foundations and reusable lowering systems

### 1. [apache/tvm](https://github.com/apache/tvm)

**Languages/role:** Python and C++; cross-level model and tensor compiler.

Study how a common `IRModule` accommodates graph functions and low-level tensor functions, allowing graph transformations, kernel scheduling, and external-library dispatch to cooperate. The current documentation describes Relax alongside TensorIR and the newer `tirx`/`s_tir` organization; older Relay-only descriptions do not adequately describe this checkout.

- **C2:** Shared module, type, target, and pass abstractions support different function representations and Python customization. The architecture explains their boundaries and calling relationships.
- **C3:** `LegalizeOps`, graph/tensor fusion, explicit scheduling, and MetaSchedule connect model-level decisions to thread bindings and generated kernels. Runtime modules provide a separate deployment boundary. These mechanisms and their source-directory map are detailed in the [architecture guide](https://tvm.apache.org/docs/arch/index.html).

### 2. [openxla/xla](https://github.com/openxla/xla)

**Languages/role:** Primarily C++; HLO optimizer and compiler for CPUs, GPUs, and accelerators.

XLA is useful for studying where target-independent graph reasoning ends and hardware-dependent scheduling, fusion, library selection, and code generation begin. This is the standalone OpenXLA repository, rather than a second count of TensorFlow's historical XLA tree.

- **C2:** StableHLO provides the input interchange boundary, while internal HLO and backend interfaces let multiple framework frontends share compilation infrastructure.
- **C3:** Buffer analysis, removal of intermediate storage, backend-specific fusion, stream partitioning, and library-call matching address memory traffic and launch overhead within an explicit staged pipeline. The [XLA architecture document](https://openxla.org/xla/architecture) explains this decomposition. Its architectural account is useful, but its dated backend examples should not be treated as a complete current hardware-support matrix.

### 3. [iree-org/iree](https://github.com/iree-org/iree)

**Languages/role:** C++ compiler, C runtime, and Python integration; MLIR-based compilation and execution.

Study a compiler that represents execution planning explicitly instead of treating everything after kernel generation as an opaque runtime concern.

- **C2:** The compiler separates input conversion, code generation, translation, and extensible input/target plugins. Flow models tensor workloads, Stream models device placement and asynchronous scheduling, HAL models buffers and execution, and VM models host-side execution. The [compiler source map](https://github.com/iree-org/iree/blob/main/compiler/src/iree/compiler/README.md) identifies these boundaries.
- **C3:** Workload partitioning, scheduling, and device code generation are distinct compilation responsibilities. The [developer overview](https://iree.dev/developers/general/developer-overview/) connects the compiler/runtime layout to tools for executing and checking compiled modules, making the complete deployment path inspectable.

### 4. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Languages/role:** C++, TableGen, and MLIR; specifically the **MLIR tensor, Linalg, bufferization, and rewriting infrastructure** in this monorepo.

This entry concerns the infrastructure underlying many ML compilers, not LLVM's entire collection of language toolchains. One-Shot Bufferize is a particularly concrete starting point.

- **C1:** Converting immutable tensor values into mutable buffers requires reasoning about aliases, read-after-write conflicts, writable destinations, and function boundaries. The documentation shows why a branched use-def chain can force a copy and how conflict diagnostics explain it.
- **C2:** `BufferizableOpInterface` separates a generic analysis from dialect-specific read/write and alias information. External interface models let downstream dialects reuse the machinery without embedding all knowledge into one pass. The [bufferization design and examples](https://mlir.llvm.org/docs/Bufferization/) also explain conservative handling of unknown operations and layouts.

### 5. [onnx/onnx-mlir](https://github.com/onnx/onnx-mlir)

**Languages/role:** C++, MLIR/TableGen, and Python; ONNX-to-native compilation with a small runtime interface.

Study how a standardized operator graph becomes loops and native library artifacts, including the boundary between reusable ONNX dialect definitions and implementation-specific lowering.

- **C2:** The Krnl dialect represents loop construction and transformations above the affine level. Math, memory-reference, and Krnl builders centralize type-dependent operations, allocation, bounds, and iteration-space manipulation. The [lowering guide](https://github.com/onnx/onnx-mlir/blob/main/docs/LoweringCode.md) includes implementation examples.
- **C1:** Operator lowering is checked through ONNX backend execution tests, FileCheck tests, and numerical tests. The [testing guide](https://github.com/onnx/onnx-mlir/blob/main/docs/Testing.md) explains static/dynamic input configurations and retaining intermediate artifacts for diagnosis. These are concrete mechanisms for checking both IR transformations and resulting numerical behavior.

### 6. [llvm/torch-mlir](https://github.com/llvm/torch-mlir)

**Languages/role:** C++, MLIR/TableGen, and Python; a PyTorch-to-MLIR bridge, not a complete deployment compiler by itself.

The central learning opportunity is the **backend contract**: a deliberately restricted tensor program that downstream compilers can consume. The repository identifies itself as an LLVM incubator project, outside official LLVM releases.

- **C1:** The Torch dialect distinguishes tensors carrying mutation and aliasing semantics from immutable value tensors. Lowering must establish value semantics, known rank, and known dtype before satisfying the backend contract.
- **C2:** Normalizing multiple capture paths to one contract allows lowerings to Linalg-on-Tensors, TOSA, StableHLO, or downstream-specific targets. The [architecture document](https://github.com/llvm/torch-mlir/blob/main/docs/architecture.md) explains these types and guarantees. Its older frontend discussion should be read alongside the repository's current FX/ONNX-oriented introduction.

### 7. [openxla/shardy](https://github.com/openxla/shardy)

**Languages/role:** C++, MLIR/TableGen, and bindings; tensor sharding propagation and partitioning infrastructure.

Study distributed layout reasoning as a compiler problem: assigning tensor dimensions to device-mesh axes while preserving user constraints and propagating information through operations.

- **C1:** Propagation traverses use-def relationships in both directions to a fixed point. Conflicting shardings require priorities and compatibility rules; reshapes need compound factors rather than simple dimension correspondence. The [propagation design](https://github.com/openxla/shardy/blob/main/docs/propagation.md) makes these cases explicit.
- **C2:** Operation sharding rules and dataflow interfaces factor out operator-specific knowledge from the shared algorithm. The [dialect-independence document](https://github.com/openxla/shardy/blob/main/docs/dialect_agnostic_sharding.md) distinguishes implemented interfaces from future work: full independence from StableHLO remains a goal in that document. The repository also labels the project a work in progress.

## Graph compilers inside broader frameworks

### 8. [pytorch/pytorch](https://github.com/pytorch/pytorch)

**Languages/role:** Python and C++; specifically **TorchInductor's graph lowering and scheduling**, with Dynamo providing the surrounding capture path.

Study the tension between aggressive fusion and the semantics of mutable, aliased tensor programs. The scheduler is large, but individual legality checks and scoring functions provide useful bounded reading targets.

- **C1:** Scheduler logic rejects unsafe mutation/alias movement and checks dependency relationships before transformations. For example, epilogue hoisting must account for every node sharing storage in the fused kernel, including nodes outside the hoisted subset.
- **C3:** Fusion scoring estimates saved memory accesses and shared-buffer locality; reduction fusion also considers backend support, loop order, and workload size. These checks live in the [Inductor scheduler implementation](https://github.com/pytorch/pytorch/blob/main/torch/_inductor/scheduler.py), which exposes legality and profitability decisions together.

### 9. [tensorflow/tensorflow](https://github.com/tensorflow/tensorflow)

**Languages/role:** C++ and Python; specifically **Grappler and its MetaOptimizer**, rather than recounting standalone XLA.

Grappler is valuable for studying graph optimization inside a runtime with existing graph versions, device assignments, function libraries, and configurable optimization policies.

- **C1:** `MetaOptimizer` supports inter-pass and post-optimization verifiers, preserves the graph producer version, and repairs topological ordering and colocation after optimization. These invariants are explicit in the [MetaOptimizer implementation](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/grappler/optimizers/meta_optimizer.cc).
- **C3:** The same implementation shows a non-obvious performance interaction: the default memory optimizer is disabled under particular XLA JIT configurations because inserted memory copies can lose the concurrency needed to hide their cost. This is a useful example of optimizations interfering through execution scheduling, rather than always composing beneficially.

### 10. [pymc-devs/pytensor](https://github.com/pymc-devs/pytensor)

**Languages/role:** Python with native/transpilation backends; symbolic tensor compiler used by PyMC.

PyTensor represents the Theano/Aesara lineage's continuing, separately developed PyMC-oriented implementation. Those ancestor repositories are not counted again here. It broadens the selection beyond neural-network deployment compilers.

- **C1:** In-place optimization must preserve the ordering of consumers of shared inputs and views. `DestroyHandler` adds ordering constraints and checks for cycles that ordinary dataflow edges alone would miss. The [mutation-analysis implementation](https://github.com/pymc-devs/pytensor/blob/main/pytensor/graph/destroyhandler.py) explains both correctness and compilation-cost considerations.
- **C2:** Graph rewriters, node rewriters, validation features, and queryable rewrite databases support reusable optimization pipelines. Sequential and equilibrium databases offer different composition models. The [graph-rewriting guide](https://github.com/pymc-devs/pytensor/blob/main/doc/extending/graph_rewriting.rst) provides an unusually detailed account of these extension points.

## Inference graph optimization and deployment compilers

### 11. [microsoft/onnxruntime](https://github.com/microsoft/onnxruntime)

**Languages/role:** Primarily C++ with multiple language APIs; specifically **graph transformers, rewrite rules, and execution-provider partitioning**.

Study how a graph optimizer interoperates with heterogeneous provider capabilities and compiled subgraphs while preserving a common host execution model.

- **C2:** Execution providers advertise supported nodes/subgraphs through capability queries; graph transformation and local rewrite interfaces are separate extension points. The [architecture guide](https://onnxruntime.ai/docs/reference/high-level-design.html) describes their interaction.
- **C3:** Basic rewrites occur before partitioning, while more specialized fusions and layout transformations occur after target assignment. Offline optimization trades initialization work for reusable artifacts, with hardware/provider compatibility constraints. The [graph-optimization guide](https://onnxruntime.ai/docs/performance/model-optimizations/graph-optimizations.html) makes those phase boundaries and deployment consequences explicit. Exact transformations and provider coverage should be checked for the chosen release.

### 12. [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino)

**Languages/role:** Primarily C++ with Python interfaces; specifically **the model transformation framework and common optimization pipelines**.

OpenVINO is useful for studying the engineering of many interacting model transformations across device plugins and operator versions.

- **C2:** `GraphRewrite` groups independently registered `MatcherPass` implementations, shares pass configuration, and supports selectively disabled transformations. Its [interface and execution contract](https://github.com/openvinotoolkit/openvino/blob/master/src/core/include/openvino/pass/graph_rewrite.hpp) explain the extension mechanism.
- **C3:** Multiple matchers can share one traversal, with type-based root dispatch avoiding unnecessary matcher work. The [common optimization pipeline](https://github.com/openvinotoolkit/openvino/blob/master/src/common/transformations/src/transformations/common_optimizations/common_optimizations.cpp) then shows explicit ordering among decompositions, constant folding, convolution/multiply fusion, and operator-version conversions. It is a concrete study in managing optimization interactions rather than a list of isolated rewrites.

### 13. [ROCm/AMDMIGraphX](https://github.com/ROCm/AMDMIGraphX)

**Languages/role:** C++ and Python interfaces; model compilation and graph optimization for AMD GPUs.

Study a compiler that combines graph rewrites, generated kernels, vendor libraries, and execution planning. Use the verified `develop` branch when following the source links.

- **C2:** The GPU target constructs pass sequences from separate dynamic-shape, required, optimization/rewrite, fusion, and backend pipelines. Compile modes select different compositions, while backend options configure tuning and caches.
- **C3:** The backend explicitly schedules streams, applies memory coloring, synchronizes devices, preallocates scratch space, and eliminates allocations. The [GPU target implementation](https://github.com/ROCm/AMDMIGraphX/blob/develop/src/targets/gpu/target.cpp) exposes these decisions in order; the [compilation overview](https://github.com/ROCm/AMDMIGraphX/blob/develop/docs/conceptual/deep-learning-compilation.rst) places them in the graph-to-kernel flow. The implementation provides stronger architectural evidence than the autogenerated API-index stubs.

### 14. [sonos/tract](https://github.com/sonos/tract)

**Languages/role:** Rust; inference graph analysis, rewriting, target lowering, and compact deployment.

Tract offers a different perspective from large C++ compiler stacks: typed graph stages and symbolic dimensions expressed directly in Rust abstractions.

- **C1:** `TDim` represents symbolic shape algebra. Symbolic broadcasting carries compatibility requirements that cannot be replaced by taking a maximum; simplification must preserve those distinctions. The [symbolic-shapes document](https://github.com/sonos/tract/blob/main/doc/symbolic-shapes.md) explains these semantics and their implications for rewrites.
- **C2:** Loading, inference, portable decluttering, target-specific optimization, and execution planning are distinct stages. A runtime trait owns preparation for a target, while a portable NNEF representation can be serialized before target-specific lowering. The [pipeline guide](https://github.com/sonos/tract/blob/main/doc/pipeline.md) explains this separation and where kernel selection occurs.

### 15. [kendryte/nncase](https://github.com/kendryte/nncase)

**Languages/role:** C# compiler infrastructure with C++ runtime components and Python tooling; neural-network compilation for Kendryte accelerators.

The compiler's C# e-graph implementation provides a substantial language and hardware-community contrast to the LLVM-centered entries. Study equivalence-class maintenance together with constrained graph extraction.

- **C1:** Union operations update representative classes and type information, then enqueue repairs to canonicalize affected parents. The [e-graph implementation](https://github.com/kendryte/nncase/blob/master/src/Nncase.EGraph/Passes/EGraph.cs) exposes the invariants required after merges; it does not establish general thread safety.
- **C3:** Extraction builds an OR-Tools CP-SAT model with root/child-selection requirements, cycle exclusions, and weighted costs. It bounds solving resources and rejects invalid or unsuccessful solutions. The [extractor](https://github.com/kendryte/nncase/blob/master/src/Nncase.EGraph/Passes/EGraphExtractor.cs) is a useful study of optimization quality versus compilation effort. Hardware deployment also depends on the corresponding target/runtime packages.

## GPU kernel languages, fusion engines, and compact compiler stacks

### 16. [triton-lang/triton](https://github.com/triton-lang/triton)

**Languages/role:** Python, C++, MLIR/TableGen; language and compiler for custom tensor kernels.

Study the interface between a Python-like kernel language, explicit numerical semantics, and a target-extensible compilation pipeline. This is the canonical Triton language repository, not NVIDIA's unrelated Triton Inference Server.

- **C1:** Type promotion, broadcasting, integer division, compile-time constants, and out-of-range casts have documented semantics that can differ from Python or NumPy. The [semantics specification](https://github.com/triton-lang/triton/blob/main/docs/python-api/triton-semantics.rst) identifies concrete sources of wrong-code assumptions.
- **C2:** Backends supply compilation stages, dialects, and code-generation implementations. The [compiler driver](https://github.com/triton-lang/triton/blob/main/python/triton/compiler/compiler.py) coordinates those stages, caches intermediate artifacts, and supports IR-level inputs and overrides useful for debugging and testing.

### 17. [tile-ai/tilelang](https://github.com/tile-ai/tilelang)

**Languages/role:** Python and C++; TVM-based tile programming language and accelerator compiler.

Study how a compiler turns tile-level operations and pipeline annotations into legal overlapping memory/compute schedules. Despite sharing TVM infrastructure, TileLang has substantial independent language and lowering implementations.

- **C1:** The fence-injection pass conservatively merges proxy state through control flow and inserts ordering between generic shared-memory traffic and asynchronous GPU operations. The [fence-pass design](https://github.com/tile-ai/tilelang/blob/main/docs/compiler_internals/inject_fence_proxy.md) explains the potential races and treatment of opaque calls.
- **C3:** Stage/order annotations drive prologue, steady-state, and epilogue generation. Producer/consumer checks and replay of scalar bindings preserve the appropriate logical iteration while enabling software pipelining. The [pipeline guide](https://github.com/tile-ai/tilelang/blob/main/docs/programming_guides/software_pipeline.md) gives detailed examples rather than relying on benchmark claims.

### 18. [NVIDIA/Fuser](https://github.com/NVIDIA/Fuser)

**Languages/role:** C++ with Python integration; nvFuser fusion code generation for NVIDIA GPUs.

This repository is particularly useful for engineers interested in the mathematics behind tensor indexing and schedule transformations.

- **C1:** Splitting an extent by a non-divisor introduces invalid iteration points. Correct predicates must distinguish those points after subsequent transformations; the [split-divisibility document](https://github.com/NVIDIA/Fuser/blob/main/doc/reading/divisibility-of-split.md) explains this with worked examples and states the nonnegative-index assumption behind its division reasoning.
- **C2:** `IterDomain` transformations are modeled through paired extent and index mappings, composition, and equivalence. The [IterDomain design](https://github.com/NVIDIA/Fuser/blob/main/doc/reading/iterdomain.md) makes a shared abstraction available for reasoning about many schedules. These documents are valuable design material, not a claim of a complete formal verification of generated kernels.

### 19. [facebookincubator/AITemplate](https://github.com/facebookincubator/AITemplate)

**Languages/role:** Python compiler with CUDA/HIP C++ output and runtime; ahead-of-time inference compilation.

Study a relatively direct model-to-native pipeline and the contract between generated code, reusable runtime machinery, and requested model outputs.

- **C1:** The compiler validates output membership and names before optimization, verifies that required outputs survive, and restores output ordering after replacements. The runtime's `ModelContainer` manages shared constants and a pool of model instances for concurrent requests; see the [runtime design](https://github.com/facebookincubator/AITemplate/blob/main/docs/source/runtime/cxx_design.rst).
- **C3:** Graph optimization, kernel profiling, constant folding, memory planning, source generation, and final library construction appear as separate stages in [the compiler driver](https://github.com/facebookincubator/AITemplate/blob/main/python/aitemplate/compiler/compiler.py). This makes performance specialization and generated-artifact construction directly traceable.

### 20. [tinygrad/tinygrad](https://github.com/tinygrad/tinygrad)

**Languages/role:** Primarily Python; tensor framework with its own graph compiler, kernel lowering, and execution machinery.

Study an end-to-end stack whose compiler abstractions remain visible from the tensor frontend through accelerator launch. Its compact design makes it a useful complement to larger systems, without implying that its internal APIs are stable.

- **C2:** Tensor operations construct UOp graphs; scheduling produces kernel calls; renderers, compilers, runners, and device runtimes have distinct responsibilities. The [developer architecture guide](https://github.com/tinygrad/tinygrad/blob/master/docs/developer/developer.md) maps these concepts to code.
- **C3:** The scheduler partitions computation into kernels, and lowering includes BEAM search before rendering and binary compilation. This organization provides a concrete path for studying fusion, schedule exploration, and device execution within one repository, rather than treating the tensor API as the entire system.

### 21. [hidet-org/hidet](https://github.com/hidet-org/hidet)

**Languages/role:** Primarily Python; deep-learning graph and tensor-program compiler. **Archived repository**, retained for architectural study; the README's active-development wording is stale relative to the [verified archive flag](https://api.github.com/repos/hidet-org/hidet).

Study task-based kernel implementation alongside graph-level rewrites.

- **C2:** A `Task` describes computation and can supply CPU or CUDA implementations. Graph rewrite rules separately combine a DAG pattern with a replacement constructor that may reject a match. The [rewrite extension guide](https://github.com/hidet-org/hidet/blob/main/gallery/developer-guides/add-subgraph-rewrite-rule.py) explains this boundary and its ordering relative to operator resolution.
- **C3:** Template scheduling instantiates tensor programs for shapes and tunable parameters, with explicit warp/lane mappings, shared memory, registers, and matrix instructions. The [template-scheduling guide](https://github.com/hidet-org/hidet/blob/main/gallery/developer-guides/add-new-operator-template-based.py) shows the implementation. These are documentation examples inside a substantial compiler, not a standalone tutorial repository.

## Alternative MLIR compiler architectures

### 22. [alibaba/BladeDISC](https://github.com/alibaba/BladeDISC)

**Languages/role:** C++, MLIR, and Python integration; dynamic-shape model compiler.

Study compilation when shapes are unknown until execution. **Public-activity caveat:** [GitHub metadata](https://api.github.com/repos/alibaba/BladeDISC) reported the last repository push as 2024-12-30; current maintenance was not established, and documented framework versions should be treated accordingly.

- **C1:** Fusion must determine whether dynamic tensor extents are compatible from topology and operation semantics. Implicit broadcasting and vectorization cannot simply assume the favorable static-shape case.
- **C3:** The compiler creates specialized fusion variants guarded by generated host-side conditions, and its stitch strategy combines differently sized schedules using intermediate storage. The [pass-pipeline walkthrough](https://github.com/alibaba/BladeDISC/blob/main/docs/developers/pass_pipeline.md) explains these mechanisms, including speculation, buffer deallocation, runtime abstraction, and device lowering. Its explicitly unfinished sections are historical design context, not verified current feature promises.

### 23. [bytedance/byteir](https://github.com/bytedance/byteir)

**Languages/role:** C++, MLIR, and Python integration; compiler, frontends, and runtime in one repository.

Study how a compiler extends upstream tensor transformations while retaining recognizable dialect interfaces. **Public-activity caveat:** [GitHub metadata](https://api.github.com/repos/bytedance/byteir) reported the last repository push as 2025-08-20; the README describes an early-stage project.

- **C1:** The Linalg-extension document demonstrates a concrete wrong tiling: zero-filling an accumulator inside every reduction tile destroys previous partial sums. Its corrected transformation moves initialization outside the loop.
- **C2:** `linalg-ext` and extended tiling/fusion operations accommodate scan, top-k, softmax, multiple fusion roots, diamond-shaped graphs, and intermediate outputs while aiming to interoperate with upstream Linalg. The [Linalg extension design and IR examples](https://github.com/bytedance/byteir/blob/main/compiler/doc/linalg.md) make these distinctions inspectable. The repository's frontend/compiler/runtime split is separately described in its introduction.

## FPGA compilation and quantized hardware generation

### 24. [fastmachinelearning/hls4ml](https://github.com/fastmachinelearning/hls4ml)

**Languages/role:** Python compiler and C++/HLS templates; machine-learning inference hardware generation.

Study model conversion where numerical precision and synthesis resources are part of compilation, particularly from the scientific-instrumentation community.

- **C1:** Model-wide precision inference uses symbolic interval reasoning and explicit quantizers; unsupported operators fail conversion rather than silently bypassing the analysis. The [precision guide](https://github.com/fastmachinelearning/hls4ml/blob/main/docs/advanced/precision.rst) states the quantization assumptions and floating-point caveat.
- **C2:** Reusable optimizer passes are assembled into dependency-ordered flows that repeat until no graph changes remain. Backend-specific flows reuse common transformations, as explained in the [pass/flow design](https://github.com/fastmachinelearning/hls4ml/blob/main/docs/ir/flows.rst).
- **C4:** The [2021 v0.5.0 release](https://github.com/fastmachinelearning/hls4ml/releases/tag/v0.5.0) documents streaming-IO migration and latency fixes; [2026 v1.3.0](https://github.com/fastmachinelearning/hls4ml/releases/tag/v1.3.0) adds synthesis tests, Keras 3 test coverage, and pytest compatibility work. This is direct evidence of evolution and complexity management across years.

### 25. [Xilinx/finn](https://github.com/Xilinx/finn)

**Languages/role:** Python with HLS/RTL generation and integration; dataflow compiler for quantized neural networks on FPGAs.

FINN identifies itself as an experimental AMD research framework. Study compilation that produces a network-specific hardware architecture, with intermediate forms that remain executable for verification.

- **C2:** The flow separates model preparation, hardware specialization, generation, and deployment. Users can stop at intermediate representations or incorporate generated IP into larger systems. The [end-to-end flow](https://github.com/Xilinx/finn/blob/main/docs/finn/end_to_end_flow.rst) describes these reusable boundaries.
- **C1:** A mixed graph of standard ONNX nodes, custom nodes, and HLS/RTL nodes can be checked node by node. Verification progresses through Python execution, generated C++ simulation, and RTL/IP emulation, with waveform tracing for diagnosis. The [verification guide](https://github.com/Xilinx/finn/blob/main/docs/finn/verification.rst) explains how correctness is checked across representation changes.

## Graph superoptimization research implementations

### 26. [jiazhihao/TASO](https://github.com/jiazhihao/TASO)

**Languages/role:** C++ optimizer with Python bindings and a Python/Z3 verifier; tensor graph superoptimization. **Historical research implementation:** [repository metadata](https://api.github.com/repos/jiazhihao/TASO) reported its last push in January 2023.

Study the separation of transformation generation/validation from cost-directed search over candidate computation graphs.

- **C1:** The [verifier](https://github.com/jiazhihao/TASO/blob/master/verify/verify.py) encodes tensor operators and axioms, then asks Z3 whether a proposed inequivalence is satisfiable. This is reasoning relative to the encoded algebraic model, not an unconditional guarantee of bitwise IEEE floating-point equivalence.
- **C3:** The [substitution engine](https://github.com/jiazhihao/TASO/blob/master/src/core/substitution.cc) matches graph patterns, rejects cyclic replacements, checks graph consistency, and limits candidates by cost, size, and deduplication. Those mechanisms make search-space control and rewrite legality visible. No headline speedup from the original benchmark is assumed to generalize to modern hardware.

### 27. [uwplse/tensat](https://github.com/uwplse/tensat)

**Languages/role:** Rust with TASO C++ integration; equality-saturation tensor graph optimization. **Historical research artifact:** [repository metadata](https://api.github.com/repos/uwplse/tensat) reported its last push in June 2021, and its README still labels the optimizer in progress.

Tensat is a substantive alternate optimizer built around e-graphs, not an independently counted copy of TASO. It depends on research forks of TASO and egg, which are not listed separately.

- **C1:** Rewrite application checks the validity of constructed patterns and provides cycle filtering for multi-pattern transformations. Inspect the [rewrite machinery](https://github.com/uwplse/tensat/blob/master/src/rewrites.rs); its algebraic assumptions should not be confused with unrestricted floating-point equivalence.
- **C3:** Cost evaluation reuses TASO operator measurements, while greedy and integer-programming extraction offer different search tradeoffs. The [optimization and extraction code](https://github.com/uwplse/tensat/blob/master/src/optimize.rs) includes cost-model plumbing and memoized reconstruction of a selected graph, illustrating the gap between discovering equivalences and choosing executable shared computation.

## Search coverage, exclusions, and limitations

Discovery used more than six distinct live-web formulations, including: MLIR/TVM/IREE/XLA architecture; Python GPU tensor DSLs; Rust inference graph optimization; equality saturation and TASO/Tensat; FPGA FINN/hls4ml compilation; vendor inference optimizers; ByteIR/BladeDISC/NNFusion/Hidet; distributed sharding and TPU compilers; C# and embedded RISC-V compilation; symbolic PyTensor rewrites; and broader embedded, Rust, and Zig compiler searches. Primary GitHub APIs, repository introductions, source files, developer documentation, and release records were then opened and read. Search snippets were discovery aids rather than the sole evidence for retained entries.

The list extends beyond 25 because nncase and PyTensor added materially different implementations and communities after the initial cross-section was assembled. Later broad queries increasingly returned already-covered compiler families, forks, small teaching implementations, and adjacent projects. The selection still does not exhaust the ecosystem: Glow, NNFusion, TPU-MLIR, AKG, and Intel's graph-compiler family are examples of omitted candidates, not projects judged inferior. General-purpose HPC compilers, kernel libraries without a substantial compiler, model-serving systems, converter-only wrappers, awesome-lists, and tutorial repositories were outside the retained scope.

No duplicate upstream mirrors or sibling forks are counted. PyTorch, TensorFlow, LLVM, and other monorepos are each counted once; their relevant subsystems are explicit. Archive and public-push metadata were checked on the research date, but no maintenance promise is inferred from a recent push. Hidet's archival status overrides its older README wording; BladeDISC, ByteIR, TASO, and Tensat carry explicit historical/activity caveats. Documentation can lag implementation, especially in fast-moving dialect and frontend APIs.

This was read-only source research: no candidate repository was cloned, built, installed, benchmarked, or executed. Test mechanisms described here were inspected, not run. Performance criteria refer to concrete optimization mechanisms and architectural constraints, not reproduced speedups. C4 is asserted only where multi-year release evidence was examined; its absence from other entries is not a claim that those projects lack a long history.
