# Machine learning inference runtimes

Research date: **2026-10-09**.

This report selects 24 GitHub repositories whose implementations load, execute, schedule, or provide substantial runtime support for trained machine-learning models. It covers general graph execution, compiler-generated runtimes, mobile and microcontroller deployment, Rust and browser implementations, generative-model execution, server scheduling, and decision-tree prediction. Compiler projects are included only where their deployment runtime is a substantive subsystem. These are engineering study candidates, not a ranking or a claim that every component is uniformly exemplary.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions supporting multiple use cases. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — demonstrated evolution over years together with compatibility, testing, or complexity management. The criterion assignments below are assessments grounded in the linked material; they are not certifications of correctness or performance.

## General and compiler-backed runtimes

### 1. [microsoft/onnxruntime](https://github.com/microsoft/onnxruntime)

**Language/role:** C++ core with multiple language bindings; cross-platform ONNX execution. The relevant subsystem is inference, including execution providers, graph partitioning, and session execution; the training portion is outside this selection.

Study how an execution engine negotiates which parts of a graph each accelerator can handle, while retaining a common tensor representation at partition boundaries.

- **C1:** The architecture documents concurrent calls to a session's `Run`, stateless kernel computation, and providers' responsibility for converting private tensor representations at subgraph boundaries. These are explicit concurrency and representation contracts.
- **C2:** Execution providers expose capabilities and allocators; graph transformations and rewrite rules provide separate extension mechanisms. This is a reusable integration architecture for heterogeneous devices.
- **C3:** Provider-independent optimization precedes capability-based partitioning and provider compilation, making the relationship between optimization and dispatch inspectable.

**Entry point:** [ONNX Runtime architecture](https://onnxruntime.ai/docs/reference/high-level-design.html), which explains all three mechanisms. Its high-level descriptions should be read alongside the release being studied rather than treated as an exhaustive current operator-support guarantee.

### 2. [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino)

**Language/role:** C++ with Python and C bindings; model optimization and inference across device plugins.

Study the distinction between a framework-independent model, a device-specific compiled model, and a mutable inference request.

- **C2:** `Core`, frontends, plugins, `CompiledModel`, and `InferRequest` have separate responsibilities, allowing model import and device execution to evolve independently. The [architecture document](https://github.com/openvinotoolkit/openvino/blob/master/src/docs/architecture.md) traces their dependency structure.
- **C1:** The asynchronous request base class specifies cancellation, completion callbacks, tensor shape/type requirements, and a destructor requirement to stop and wait for tasks that capture derived state.
- **C3:** Asynchronous execution is represented as stages paired with executors, so plugins can construct pipelines instead of treating asynchronous inference as an opaque thread launch. See [IAsyncInferRequest](https://github.com/openvinotoolkit/openvino/blob/master/src/inference/dev_api/openvino/runtime/iasync_infer_request.hpp).

### 3. [iree-org/iree](https://github.com/iree-org/iree)

**Language/role:** C runtime and C++/MLIR compiler; portable execution of compiled machine-learning programs. Focus on `runtime/src/iree`, particularly the VM, hardware abstraction layer, and runtime sessions.

Study how compiler output is embedded into an application with explicit resource ownership and device synchronization.

- **C1:** Sessions isolate module state and timelines; a single session requires external synchronization for concurrent use. Sharing across incompatible instances/devices requires import/export rather than unchecked pointer reuse. These rules are documented in [session.h](https://github.com/iree-org/iree/blob/main/runtime/src/iree/runtime/session.h).
- **C2:** Sessions compose lower-level VM and HAL facilities while exposing module loading, device allocators, and resource trimming.
- **C3:** The HAL distinguishes host/device wait and signal capabilities, interrupt versus spinning behavior, and single-producer optimizations. Its [semaphore contract](https://github.com/iree-org/iree/blob/main/runtime/src/iree/hal/semaphore.h) also explains failure payloads and a cross-device timeline-value limitation: useful evidence of portability affecting runtime design.

### 4. [apache/tvm](https://github.com/apache/tvm)

**Language/role:** C++ and Python; machine-learning compiler with a deployment runtime. Counted once, with emphasis on the runtime rather than the entire compiler.

Study how compiled functions, device modules, callbacks, and remote execution share a small interoperability layer.

- **C2:** The runtime architecture explains type-erased packed calls, tensor exchange, and modules that expose device-specific compiled functions through a common interface. The same mechanism supports language bindings and callbacks.
- **C3:** The deployment core is separated from compiler IR support; modules cache function handles, and RPC enables remote correctness checks and profiling without rebuilding a target-language test harness.
- **C1:** The design explicitly identifies thread-safe driver glue as a responsibility of device modules. This is a useful boundary to inspect, rather than an assertion that arbitrary compiled code is automatically thread-safe.

**Entry point:** [TVM runtime system](https://github.com/apache/tvm/blob/main/docs/arch/runtime.rst), including packed functions, modules, and remote deployment. The document also shows the current dependency on TVM FFI; this report does not count that dependency separately.

## Mobile, embedded, and resource-constrained execution

### 5. [pytorch/executorch](https://github.com/pytorch/executorch)

**Language/role:** C++ runtime and Python export/lowering tooling; execution of PyTorch-derived programs on edge devices.

Study how ahead-of-time planning moves complexity out of the device's execution loop while preserving familiar operator semantics.

- **C1:** Immutable `Program` objects can be shared across threads, while a mutable `Method` must have serialized access. Operator semantics are checked against core PyTorch through a dedicated testing framework.
- **C2:** Injected data loaders, allocators, a platform abstraction layer, kernel registration, and delegates separate application, operating-system, and accelerator concerns.
- **C3:** Constants can refer directly to program-file data; mutable tensor storage is planned into caller-provided buffers, including different memory banks. The core avoids implicit heap allocation and executes an instruction sequence.

**Entry point:** [runtime overview](https://github.com/pytorch/executorch/blob/main/docs/source/runtime-overview.md). It explicitly distinguishes guarantees of the core from potentially different behavior of kernels and delegates.

### 6. [google-ai-edge/LiteRT](https://github.com/google-ai-edge/LiteRT)

**Language/role:** C/C++ runtime with platform bindings; the successor to TensorFlow Lite. Focus on `litert` and its compiled-model/NPU dispatch path rather than counting TensorFlow Lite again inside the TensorFlow monorepo.

Study the boundary between accelerator compilation, executable loading, and hardware-buffer ownership.

- **C2:** The [Dispatch API](https://github.com/google-ai-edge/LiteRT/blob/main/litert/DISPATCH_API.md) separates device and invocation contexts, executable blobs, tensor buffers, and vendor implementations behind C interfaces intended for ABI compatibility.
- **C1:** Buffer requirements communicate type, size, stride, and alignment before buffers are attached to an invocation. Runtime compatibility and capability checks are part of initialization, making otherwise implicit accelerator assumptions explicit.
- **C3:** Hardware-buffer interoperability and asynchronous execution are designed into dispatch. The document explains how the compiled-model layer coordinates the interpreter-facing delegate and NPU implementation.

### 7. [tensorflow/tflite-micro](https://github.com/tensorflow/tflite-micro)

**Language/role:** C++; inference for microcontrollers and other targets with tight memory budgets.

Study memory planning when the runtime's workspace must fit into a caller-supplied arena.

- **C1:** Arena head, temporary, and tail regions have different lifetimes. Temporary allocations must be reset before adjusting the head; offline overlap is valid only for tensors whose live ranges do not overlap.
- **C3:** A greedy planner reuses nonpersistent buffers, while persistent metadata occupies the tail. Offline placements can coexist with online scratch allocation. Recording APIs attribute arena consumption to tensor metadata, operator state, and other categories.

**Entry point:** [memory management design](https://github.com/tensorflow/tflite-micro/blob/main/tensorflow/lite/micro/docs/memory_management.md). It also candidly documents currently ignored offline-plan metadata fields, making this a useful study of the difference between a serialized format and actual validation behavior.

### 8. [Tencent/ncnn](https://github.com/Tencent/ncnn)

**Language/role:** C++; compact inference engine with CPU and Vulkan backends and model-conversion tools.

Study allocation and concurrency choices in an embeddable runtime without mandatory third-party runtime dependencies.

- **C1:** The allocator guide distinguishes locked and unlocked pools and prescribes sharing arrangements for concurrent extractors and multiple networks. Correctness depends on matching pool synchronization to actual ownership and execution concurrency.
- **C2:** A small allocator interface can replace all allocation/free operations, while separate blob and workspace allocators distinguish externally retrievable values from temporary kernel storage.
- **C3:** Pool reuse and sharing reduce allocation churn and memory duplication. The guide gives concrete configurations for single-threaded and concurrent inference rather than just an allocator API signature.

**Entry point:** [custom allocator guide](https://github.com/Tencent/ncnn/blob/master/docs/developer-guide/custom-allocator.md). The repository's inference, conversion, and platform support establish broader category fit; the allocator is an especially compact subsystem to study.

### 9. [alibaba/MNN](https://github.com/alibaba/MNN)

**Language/role:** C++ core with additional tooling; mobile-to-server tensor execution, including on-device language-model inference.

Study how a backend contract connects operator implementations to memory reuse, execution mode, and hardware-specific tuning.

- **C2:** `Backend` creates an `Execution` for an operator and provides lifecycle hooks. Its configuration distinguishes direct execution from recorded execution. See [Backend.hpp](https://github.com/alibaba/MNN/blob/master/source/core/Backend.hpp).
- **C1:** Storage classes explicitly differ in when acquire, release, and clear allocate, recycle, or free memory. Applying the wrong lifetime assumption to reusable and nonreusable storage is a substantive correctness problem.
- **C3:** The same interface exposes allocator policy, quantized attention, KV-cache memory limits, and CPU scheduling hints. The [project introduction](https://github.com/alibaba/MNN/blob/master/docs/intro/about.md) connects these runtime concerns with offline graph fusion/layout transformations and different CPU/GPU implementations.

### 10. [Tencent/TNN](https://github.com/Tencent/TNN)

**Language/role:** C++; inference framework spanning mobile, desktop, and server devices. It draws on ncnn and Rapidnet but has a substantive separate implementation and architecture, rather than being listed as an equivalent fork.

Study factory-based model interpretation, graph construction, and device-specific layer acceleration.

- **C2:** The [architecture guide](https://github.com/Tencent/TNN/blob/master/doc/en/development/architecture_en.md) separates model interpreters, network structures/resources, devices, and accelerated layers through registered creators.
- **C1:** Blob reuse is coordinated through common base storage and offsets. Cross-instance reuse has different rules within one thread and across threads; external memory users must manage lifetime and locking. Operator tests compare device implementations with a CPU reference.
- **C3:** Size-aware blob reuse and consolidated allocation make memory optimization visible above individual kernels.

**Maintenance context:** GitHub metadata reported the last push as 2025-05-09 and did not mark the repository archived. It is retained for study without implying current active maintenance. [Repository metadata](https://api.github.com/repos/Tencent/TNN).

### 11. [PaddlePaddle/Paddle-Lite](https://github.com/PaddlePaddle/Paddle-Lite)

**Language/role:** C++; mobile and edge inference within the Paddle ecosystem.

Study the separation of graph analysis from lightweight execution, and a type system that includes hardware placement as well as tensor representation.

- **C1/C2:** Kernel registration describes target, precision, layout, and input/output types. The [architecture guide](https://github.com/PaddlePaddle/Paddle-Lite/blob/develop/docs/develop_guides/architecture-intro.md) explicitly warns that inaccurate declarations can make the analysis and execution state machines disagree. MIR passes operate on an SSA graph, while operators and kernels have distinct responsibilities.
- **C3:** Shape inference is treated as a per-batch cost, with caching discussed separately from initial checks and graph optimization.
- **C4:** The [2020 v2.7 release](https://github.com/PaddlePaddle/Paddle-Lite/releases/tag/v2.7) documents a model-format migration and required reconversion; [2024 v2.14-rc](https://github.com/PaddlePaddle/Paddle-Lite/releases/tag/v2.14-rc) adds newer Paddle model support and fixes compatibility and numerical issues. The [test-development guide](https://github.com/PaddlePaddle/Paddle-Lite/blob/develop/docs/develop_guides/add_unit_test.md) explains generated cases and absolute/relative-error comparisons against PaddlePaddle.

The architecture and testing guides are the two recommended starting points. Several detailed sources are in Chinese; no performance ratios from their benchmark claims are adopted here.

### 12. [ARM-software/armnn](https://github.com/ARM-software/armnn)

**Language/role:** C++; heterogeneous inference SDK and TensorFlow Lite delegate targeting Arm hardware. **Historical/legacy selection:** its [current README](https://github.com/ARM-software/armnn/blob/main/README.md) explicitly says Arm no longer actively maintains it and that further security and functional updates should not be expected.

Study a substantial accelerator-integration architecture, with that maintenance limitation understood.

- **C2:** Pluggable backends supply workload factories, memory managers, layer-support queries, optimization views, and optional runtime/profiling contexts. The [backend development guide](https://github.com/ARM-software/armnn/blob/main/src/backends/README.md) follows registration through graph partitioning and runtime creation.
- **C1:** A backend factory object is not guaranteed to outlive objects it creates; the guide explicitly recommends stateless factories and distinguishes factory, loaded-network, and runtime-context lifetimes. That is a useful ownership invariant at an extensibility boundary.

The GitHub repository was not marked archived when checked; the explicit legacy notice is more informative than that flag or a recent push.

## Rust runtimes

### 13. [sonos/tract](https://github.com/sonos/tract)

**Language/role:** Rust; self-contained model loading, optimization, and inference, including ONNX and TensorFlow-related deployment paths.

Study a typed progression from partially known models to portable intermediate representations and target-specific execution plans.

- **C1:** Shape/type resolution is a distinct stage. The documented portable, decluttered form must be distinguished from machine-specific lowering; serializing the latter as though it were portable would violate the representation boundary.
- **C2:** The `Runtime` trait prepares a typed model into a runnable object, with a registry for linked runtime implementations. Execution state is separated from the prepared plan.
- **C3:** Generic operations lower into target-specific matrix-multiplication microkernels and optimized scans. The guide separates graph simplification from hardware-specific code generation so performance differences can be investigated stage by stage.

**Entry point:** [load–optimize–run pipeline](https://github.com/sonos/tract/blob/main/doc/pipeline.md). This is especially useful for understanding why an intermediate model and a production runnable are different artifacts.

### 14. [robertknight/rten](https://github.com/robertknight/rten)

**Language/role:** Rust; ONNX inference with native CPU and WebAssembly deployment.

Study a smaller runtime whose graph-value lifetimes and performance diagnostics are directly accessible.

- **C1:** Graph execution maintains remaining-use counts for intermediate values. The compact counter saturates and becomes nondecrementing at its maximum, avoiding wraparound that could incorrectly release a still-needed value. See [graph.rs](https://github.com/robertknight/rten/blob/main/src/graph.rs).
- **C3:** The [performance guide](https://github.com/robertknight/rten/blob/main/docs/performance.md) separates operator time from allocation overhead, discusses thread counts and int8 bandwidth benefits, and describes `partial_run` for computing loop-invariant subgraphs once.
- **C2:** Partial execution, configurable run options, graph planning, and reusable tensor/operator facilities make this a general model runtime rather than a single-model demonstration.

The documented profiling method provides a practical route from a slow model to a focused implementation investigation without requiring a very large framework checkout.

## Browser execution

### 15. [tensorflow/tfjs](https://github.com/tensorflow/tfjs)

**Language/role:** TypeScript/JavaScript with backend implementations; browser and Node.js tensor execution and model deployment. Focus on the core engine and inference-related backend infrastructure, not the whole training API.

Study explicit device-resource management inside a garbage-collected language.

- **C1:** The engine tracks tensors separately from underlying data buffers, handles shared data references, and delegates disposal to the owning backend. Backend initialization may be asynchronous; pending initialization identities guard against an outdated initialization completing after a backend switch.
- **C2:** Backend factories, kernel registration, initialization/disposal hooks, and a common engine expose hardware-specific implementations through reusable tensor operations.
- **C3:** Memory accounting and kernel profiling are integrated with execution, allowing backend time and peak allocation behavior to be inspected together.

**Entry point:** [tfjs-core/src/engine.ts](https://github.com/tensorflow/tfjs/blob/master/tfjs-core/src/engine.ts), especially backend initialization and tensor disposal/profiling. This monorepo is counted once rather than listing each backend package separately.

### 16. [mlc-ai/web-llm](https://github.com/mlc-ai/web-llm)

**Language/role:** TypeScript; browser-local LLM runtime using WebGPU and TVM-generated functions. Related to MLC LLM, but with substantial browser-specific runtime code.

Study how compiled model execution, browser resource limits, streaming, and workers fit together.

- **C1:** The [LLM chat pipeline](https://github.com/mlc-ai/web-llm/blob/main/src/llm_chat.ts) validates required storage-buffer limits and consistency between artifact roles and runtime-reported KV/recurrent state. It resolves prefill/decode function availability and owns compiled function lifetimes.
- **C2:** A shared engine interface is exposed through worker clients/handlers. The [worker implementation](https://github.com/mlc-ai/web-llm/blob/main/src/web_worker.ts) correlates requests and results, transports errors, and associates streams with request identifiers.
- **C3:** WebGPU execution and moving computation into a worker address browser compute and UI responsiveness constraints. The project also documents service-worker termination as a lifecycle concern, so worker persistence should not be assumed.

## Generative-model execution engines

### 17. [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)

**Language/role:** C/C++ with accelerator code; local and server LLM execution. This selection includes its integrated GGML backend layer and counts that code only once.

Study the relationship between model/context APIs and cross-device tensor movement.

- **C2:** The [public API](https://github.com/ggml-org/llama.cpp/blob/master/include/llama.h) separates models from contexts, supports custom thread pools and split model loading, and exposes actual context limits after creation.
- **C1:** [Backend tensor-copy code](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-backend.cpp) requires matching layouts. If an asynchronous device copy is unavailable, it synchronizes both backends before performing the blocking fallback, preserving ordering rather than merely copying bytes.
- **C3:** Device capability queries, host buffers, asynchronous copies, and fallback transfers make the costs of heterogeneous execution visible. This is a useful entry beneath the command-line application into reusable runtime machinery.

### 18. [vllm-project/vllm](https://github.com/vllm-project/vllm)

**Language/role:** Python with C++/CUDA and other accelerator kernels; LLM inference and serving.

Study a cache manager whose invariants directly influence serving throughput and tenant isolation.

- **C1:** Prefix-block identities include predecessor state, token content, and additional distinctions such as adapters, multimodal inputs, and cache salts. Reference counts prevent in-use blocks from being evicted. The design explicitly discusses hash collisions and cross-request isolation.
- **C2:** A block pool, free queue, hash lookup, and request-to-block mapping support a reusable allocation/append/free/evict lifecycle rather than model-specific caching.
- **C3:** Full-block reuse avoids repeated prefill computation; preallocated block objects and intrusive free-list links reduce Python allocation and queue-management overhead.

**Entry point:** [automatic prefix caching design](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md). It contains allocation workflows and worked examples, making it a stronger starting point than throughput claims alone.

### 19. [sgl-project/sglang](https://github.com/sgl-project/sglang)

**Language/role:** Python and accelerator kernels; inference runtime for language and multimodal models. Focus on `python/sglang/srt`, not just its frontend API.

Study a radix-tree alternative to hash-indexed prefix caching.

- **C1:** Splitting a cache node preserves parent/child structure, inherited lock references, and the correspondence between token keys and cached values. Protected versus evictable sizes are adjusted as references change; cache namespaces and salts must remain compatible.
- **C2:** The implementation implements a common prefix-cache interface for matching, insertion, eviction, and lock references, allowing scheduling code to consume cache behavior through defined operations.
- **C3:** Prefix sharing, page-aligned matching, access-time tracking, and eviction policy are integrated with the tree; specialized key views avoid unnecessary token-list materialization.

**Entry point:** [radix_cache.py](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py), especially key handling, node splitting, prefix matching, and reference accounting. These observations concern the inspected cache implementation, not a proof of the entire scheduler's correctness.

### 20. [NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)

**Language/role:** Python, C++, and CUDA; NVIDIA-oriented generative-model inference with runtime scheduling and cache management.

Study heterogeneous attention-state layouts and the interaction between admission estimates and actual cache reuse.

- **C1:** The [KV-cache design](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/features/kvcache.md) groups compatible layers by head count and attention window. Hybrid/recurrent models require additional state handling; manager implementations have different supported combinations. These distinctions constrain safe reuse.
- **C2:** Cache configuration exposes pool sizing, reuse, retention policy, and manager choice across multiple model families.
- **C3:** Radix-indexed block sharing, priority-aware eviction, secondary-memory offload, and sliding-window reclamation address both memory pressure and repeated computation. Scheduler-side prefix estimates are explicitly separate from whether actual block reuse is enabled.

The cited document acknowledges limitations, including static division between some pools and leaf-only eviction in the described scheme. This repository contains substantive open runtime code, while parts of its deployment stack depend on NVIDIA-provided components.

### 21. [OpenNMT/CTranslate2](https://github.com/OpenNMT/CTranslate2)

**Language/role:** C++ with Python bindings; transformer inference, including translation and generation workloads.

Study concurrency controls with clearly distinguished levels of parallelism.

- **C2:** Translator and generator objects share concepts for intra-operation threads, batch workers, multiple devices, and asynchronous results.
- **C1:** Asynchronous submission has bounded queues and can block when they fill. Python computation methods release the GIL; callers must distinguish asynchronous return behavior from unlimited admission.
- **C3:** Workers on one device share model weights; GPU workers can use separate streams. The guide distinguishes data parallelism from tensor parallelism and explains why extra workers or cross-machine execution need not improve throughput.

**Entry point:** [multithreading and parallelism](https://github.com/OpenNMT/CTranslate2/blob/master/docs/parallel.md). It connects concrete runtime behavior to configuration, including memory sharing and backpressure, rather than presenting parallelism as a single switch.

### 22. [mlc-ai/mlc-llm](https://github.com/mlc-ai/mlc-llm)

**Language/role:** Python compilation/model tooling and C++ runtime; compiler-backed LLM deployment. Its model-serving runtime is distinct from TVM's general runtime and WebLLM's browser integration.

Study a serving engine organized into state transitions and executable actions.

- **C1:** [Engine cancellation](https://github.com/mlc-ai/mlc-llm/blob/main/cpp/serve/engine.cc) removes requests from queues, recycles sequence/cache resources, and emits terminal callbacks. The implementation explicitly requires final usage output even on error.
- **C2:** Decode is an engine action operating on common request/model state, alongside separate prefill, draft, and verification actions.
- **C3:** [BatchDecode](https://github.com/mlc-ai/mlc-llm/blob/main/cpp/serve/engine_actions/batch_decode.cc) attempts cache reclamation and request preemption under capacity pressure, selects decode versus prefill kernels from token counts, and overlaps prefix-cache bookkeeping with GPU execution. Assertions tie batch shape and admitted sequence count to engine configuration.

## Reusable server execution core

### 23. [triton-inference-server/core](https://github.com/triton-inference-server/core)

**Language/role:** C++; in-process inference-server core and APIs. This is the execution coordination layer, not a standalone numerical kernel runtime; it must be paired with backends, as the [repository overview](https://github.com/triton-inference-server/core/blob/main/README.md) explains. The separate server packaging repository is not counted again.

Study dynamic batching as concurrent resource scheduling rather than HTTP request handling.

- **C1:** The [dynamic batch scheduler](https://github.com/triton-inference-server/core/blob/main/src/dynamic_batch_scheduler.cc) releases its queue lock while waiting for execution capacity so enqueue operations can progress, and handles timeout rejection and cancellation. Shape and optional-input compatibility constrain which requests may share a batch.
- **C2:** An embeddable core API, backend boundary, rate limiter, and scheduling machinery allow several inference implementations to use the same coordination layer.
- **C3:** Preferred batch sizes, maximum batch capacity, queue-delay policy, and execution-slot availability jointly determine dispatch. The code makes the throughput/latency tradeoff inspectable.

## Non-neural model inference

### 24. [dmlc/tl2cgen](https://github.com/dmlc/tl2cgen)

**Language/role:** C++ compiler/runtime with Python and Java integration, producing C prediction code for decision-tree ensembles.

Study inference specialization when the model is a branching program rather than a tensor graph.

- **C2:** Treelite-importable tree models can be compiled into native libraries and loaded through a predictor runtime, or distributed as generated prediction code. The [deployment guide](https://github.com/dmlc/tl2cgen/blob/main/docs/tutorials/deploy.rst) distinguishes runtime-assisted deployment from deploying prediction code alone.
- **C3:** The [optimization tutorial](https://github.com/dmlc/tl2cgen/blob/main/docs/tutorials/optimize.rst) explains how representative data produces branch annotations and how generated C conveys branch likelihood to the compiler without changing model decisions.
- **C1:** Threshold comparisons and missing-value routes must retain their semantics through code generation; the displayed prediction code makes these branches concrete. This correctness challenge is an inference from the documented transformation, not a claim of a formal proof.

**Project boundary:** Treelite moved compilation out starting with version 4.0; the [migration guide](https://github.com/dmlc/tl2cgen/blob/main/docs/treelite-migration.rst) establishes why TL2cgen, rather than modern Treelite alone, belongs in this runtime selection.

## Coverage, search method, and limitations

Discovery used live web search with more than six distinct formulations: heterogeneous graph runtimes and execution providers; mobile engines and memory planners; microcontroller/TinyML runtimes; compiler/runtime architectures; Rust ONNX engines; browser WebGPU/JavaScript execution; LLM paged attention and scheduling; and native decision-tree inference. Follow-up searches targeted backend contracts, cache designs, and less prominent embedded/Rust projects. Later queries increasingly returned already-covered implementations, thin wrappers, tutorials, or alternatives within represented architectural families; the selection stopped at 24 substantial repositories rather than expanding mechanically.

Every selected canonical repository URL, default branch, and archive flag was checked through the GitHub API, with repository pages also opened for multiple groups. Each entry has an additional opened primary document or source file; repository metadata and search snippets were not used as substitutes for implementation evidence. Source links use verified paths on the inspected default branches, which can change after this date. No candidate repository was cloned, built, or executed, and no benchmark claims were independently reproduced.

The selection deliberately includes both large ecosystems and smaller implementations such as RTen and TL2cgen. Discovery also surfaced Tengine, WONNX, and uTensor; they are not assessed here in enough depth to make a quality judgment, and their omission is not a negative rating. Kernel-only libraries, model collections, thin language bindings, deployment dashboards, generic routing infrastructure, educational mini-engines, and lists of projects were excluded. TensorFlow itself was not added merely to duplicate LiteRT and TFLite Micro. Related MLC projects are retained because their generic runtime, native serving engine, and browser lifecycle code are substantive different layers; those relationships are explicit above.

Maintenance is not inferred from stars, repository age, or an unarchived flag. Arm NN is explicitly legacy, and TNN's limited recent activity is noted. C4 is assigned only where multi-year change and compatibility/testing evidence were actually read. Most other entries qualify through C1–C3 without an unsupported maturity claim. Hardware-specific completeness, model accuracy, security posture, and production suitability still require a release- and workload-specific review.
