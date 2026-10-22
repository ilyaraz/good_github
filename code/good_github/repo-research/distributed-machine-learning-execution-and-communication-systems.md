# Distributed machine learning execution and communication systems

Research date: **2026-10-09**.

This report selects **25 GitHub repositories** for studying the execution and communication machinery behind distributed machine learning: collective libraries, tensor transports, gradient aggregation, parameter servers, decentralized learning, parallelization compilers, and training orchestration. Framework monorepos appear once, with the relevant subsystem identified. Both current systems and explicitly labeled historical implementations are included. These are engineering study recommendations, not a production-readiness ranking or a claim that every component is exemplary.

Criteria used below:

- **C1 — Difficult correctness:** concurrency, ordering, numerical semantics, invariants, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces and components supporting multiple algorithms, backends, or execution patterns.
- **C3 — Structured performance engineering:** concrete memory, bandwidth, latency, or scheduling constraints addressed through an understandable design.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or complexity management; repository age alone does not qualify.

The criterion judgments are grounded engineering inferences from the linked primary material. Lifecycle labels reflect explicit project statements; an unlabeled repository should not be interpreted as having a verified maintenance commitment.

## Collective communication and tensor transport

### 1. [NVIDIA/nccl](https://github.com/NVIDIA/nccl)

**Language / role:** C++ and CUDA; GPU collective and point-to-point communication across devices and hosts.

Study how a compact communicator API exposes distributed operations while preserving GPU execution ordering and managing asynchronous failure. The repository supports PCIe, NVLink/NVSwitch, InfiniBand, and socket paths, making it useful for following an operation from an application-facing primitive toward transport-specific execution.

- **C1:** Communicator creation requires consistent rank/device assignments. Concurrent communicators require compatible launch ordering; network errors can prevent completion and require coordinated abort/recreation. These are explicit correctness contracts in the [communicator and failure-handling guide](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html).
- **C2:** All-reduce, all-gather, reduce-scatter, broadcast, and send/receive share reusable communicator machinery rather than being tied to one training framework. The [repository overview](https://github.com/NVIDIA/nccl) describes this API and hardware coverage.

**Entry point:** [Communicator lifecycle, ordering, and recovery](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html).

### 2. [ROCm/rocm-systems](https://github.com/ROCm/rocm-systems) — RCCL subsystem

**Language / role:** C++ and HIP; AMD GPU collective communication, specifically `projects/rccl` in the ROCm systems monorepo.

Study the AMD implementation of reusable GPU collectives, especially how communication competes with computation for device resources. The former standalone `ROCm/rccl` repository explicitly [declares its retirement and move](https://github.com/ROCm/rccl); it is not counted separately. RCCL is a substantive hardware-specific implementation, not merely a renamed NCCL wrapper.

- **C2:** The [RCCL subsystem](https://github.com/ROCm/rocm-systems/tree/develop/projects/rccl) provides collective and direct send/receive operations for both single-process and multiprocess execution, over local and network interconnects.
- **C3:** The same source overview describes ring/tree algorithms, aggregation of small operations, and an opt-in copy-engine path for selected collectives that avoids consuming GPU compute units. Its symmetric-buffer registration and hardware restrictions make the optimization boundary concrete.

**Entry point:** [RCCL source, build options, tests, and execution modes](https://github.com/ROCm/rocm-systems/tree/develop/projects/rccl).

### 3. [pytorch/gloo](https://github.com/pytorch/gloo)

**Language / role:** C++ with CUDA support; transport-independent collectives for machine learning. **Maintenance-only**, according to the repository.

Gloo is particularly readable for comparing collective algorithms rather than treating all-reduce as a black box. Its documentation separates rendezvous, contexts, transports, algorithms, and CUDA integration.

- **C1:** The [algorithm descriptions](https://raw.githubusercontent.com/pytorch/gloo/main/docs/algorithms.md) explain why reduce-scatter/all-gather phases need notifications before reusing buffers, and how non-power-of-two process counts alter execution.
- **C2:** A `Context` owns rank and connection state without global or thread-local state, allowing independent communication groups. See the [architecture overview](https://github.com/pytorch/gloo/tree/main/docs).
- **C3:** The algorithm guide distinguishes latency-producing communication steps from bytes transferred and explains double buffering and pipelined local reduction/broadcast.

**Entry points:** [Architecture and rendezvous guide](https://github.com/pytorch/gloo/tree/main/docs); [algorithm semantics and cost analysis](https://raw.githubusercontent.com/pytorch/gloo/main/docs/algorithms.md).

### 4. [pytorch/tensorpipe](https://github.com/pytorch/tensorpipe)

**Language / role:** C++; asynchronous tensor-aware point-to-point transport. **Maintenance mode since the project's December 2025 notice**, with only minimal build fixes planned.

Study communication for parameter servers, model partitioning, and actor/learner arrangements where all-process collectives are a poor fit. TensorPipe separates small control payloads from large CPU/GPU tensors and negotiates transports and tensor channels independently.

- **C1:** The [interface contract](https://github.com/pytorch/tensorpipe) transfers buffer ownership until completion callbacks run; callbacks must return ownership even on error or closure. Descriptor-first receives also separate allocation from data movement.
- **C2:** Contexts, listeners, pipes, messages, transports, and channels form reusable layers. The maintainers' [RPC-agent design RFC](https://github.com/pytorch/pytorch/issues/35251) explains arbitrary topologies, asynchronous/asymmetric communication, and capability negotiation. The RFC is historical design evidence, not a current rollout plan.

**Entry points:** [Interface and transport/channel architecture](https://github.com/pytorch/tensorpipe#interface); [RPC integration rationale](https://github.com/pytorch/pytorch/issues/35251).

### 5. [microsoft/mscclpp](https://github.com/microsoft/mscclpp)

**Language / role:** C++, CUDA/HIP, and Python; GPU-initiated communication primitives and collective construction.

Study how one-sided communication can be embedded inside application kernels. This is a distinct communication stack; the older MSCCL runtime is not counted as another copy of the same selection.

- **C1:** The [primitive design](https://github.com/microsoft/mscclpp#overview) exposes `put`, `get`, `signal`, `wait`, and `flush` while addressing ordering across GPU/CPU accesses and local/remote links. The synchronization contract is a central engineering concern.
- **C2:** The [abstraction overview](https://microsoft.github.io/mscclpp/overview.html) separates low-level C++ primitives, a Python collective DSL, and an NCCL-compatible API.
- **C3:** Direct transfers between application buffers avoid intermediate copies; GPU-side initiation supports fine-grained communication/computation overlap. Those are identifiable mechanisms, independent of the README's benchmark claims.

**Entry points:** [Layered API overview](https://microsoft.github.io/mscclpp/overview.html); [primitive design](https://github.com/microsoft/mscclpp#overview).

### 6. [deepseek-ai/DeepEP](https://github.com/deepseek-ai/DeepEP)

**Language / role:** CUDA/C++ and Python; expert-parallel dispatch/combine communication, with additional experimental parallelism primitives.

Study specialized all-to-all execution for mixture-of-experts models: token routing, quantized payloads, reusable layouts, stream events, and interconnect resource allocation. The inspected repository describes a newer implementation with NCCL Gin and runtime kernel compilation; older descriptions of its removed NVSHMEM implementation should not be assumed current.

- **C1:** [`EPBuffer.dispatch`](https://github.com/deepseek-ai/DeepEP/blob/main/deep_ep/buffers/ep.py) specifies tensor shapes/dtypes and requires routing indices stored by reference to remain unchanged until all handle uses complete. Its stream/event controls expose asynchronous lifetime obligations.
- **C3:** That implementation chooses SM and queue-pair counts and distinguishes direct from hybrid communication. The [repository](https://github.com/deepseek-ai/DeepEP) explains the dispatch/combine focus and labels the broader bucket, pipeline, and remote-memory features experimental.

**Entry point:** [Expert buffer implementation and dispatch contract](https://github.com/deepseek-ai/DeepEP/blob/main/deep_ep/buffers/ep.py).

## Gradient aggregation, parameter servers, and decentralized execution

### 7. [horovod/horovod](https://github.com/horovod/horovod)

**Language / role:** C++ and Python; distributed training integration across TensorFlow, Keras, PyTorch, and MXNet. **Archived September 17, 2026; historical study target.**

Study the boundary between framework-specific optimizer integration and shared collective/elastic execution. Its recovery protocol is especially useful because it connects model state consistency to process membership changes.

- **C1:** [Elastic Horovod](https://horovod.readthedocs.io/en/stable/elastic_include.html) distinguishes unexpected failures requiring rollback from graceful membership changes, then re-rendezvouses and broadcasts state. Model, optimizer, and progress counters must move together.
- **C2:** A framework-independent elastic state contract and framework-specific state implementations support multiple training loops and custom state.
- **C4:** The [2020–2023 changelog](https://github.com/horovod/horovod/blob/master/CHANGELOG.md) records TensorFlow/PyTorch/Keras compatibility fixes, race/deadlock corrections, and collective edge cases. This is longitudinal complexity-management evidence, not a claim of current activity.

**Entry points:** [Elastic execution protocol](https://horovod.readthedocs.io/en/stable/elastic_include.html); [changelog](https://github.com/horovod/horovod/blob/master/CHANGELOG.md).

### 8. [bytedance/byteps](https://github.com/bytedance/byteps)

**Language / role:** C++ and Python with GPU communication integration; hierarchical gradient aggregation. **Archived December 8, 2025; historical study target.**

BytePS is a useful alternative to both pure all-reduce and traditional parameter servers: CPU servers reduce gradients, while workers retain optimizer updates.

- **C2:** Its [architecture](https://github.com/bytedance/byteps/blob/master/docs/architecture.md) separates framework plugins, priority queues, and a communication core. Moving optimizer updates to workers avoids imposing one framework's optimizer semantics on the servers.
- **C3:** The documented execution path combines local NCCL reduce-scatter, intermachine ps-lite push/pull, server reduction, and local all-gather. Priority-aware task selection makes the communication schedule explicit rather than FIFO by default.

**Entry point:** [Architecture and staged communication workflow](https://github.com/bytedance/byteps/blob/master/docs/architecture.md).

### 9. [dmlc/ps-lite](https://github.com/dmlc/ps-lite)

**Language / role:** C++; reusable parameter-server substrate.

Study the smaller systems layer beneath a full distributed learner: workers compute, servers own model partitions, and a scheduler coordinates membership/control. It is valuable for understanding what push/pull communication supplies and what an optimizer must still define.

- **C1:** The [optimization overview](https://ps-lite.readthedocs.io/en/latest/overview.html) explicitly distinguishes asynchronous updates using delayed weights from synchronized gradient aggregation. Scheduling changes the algorithm's numerical semantics, not just execution speed.
- **C2:** Push/pull and partitioned server ownership support different update policies without embedding a particular neural-network framework. The overview demonstrates both synchronous and asynchronous orchestration on the same substrate.

**Entry point:** [Roles, update ordering, and synchronization tradeoffs](https://ps-lite.readthedocs.io/en/latest/overview.html).

### 10. [Angel-ML/angel](https://github.com/Angel-ML/angel)

**Language / role:** Java and Scala; parameter-server-based distributed ML and graph computation, including YARN and Spark integration.

Angel broadens the report beyond GPU-centric Python systems. Study model partition ownership, parameter-server agents, and the deliberate separation of runtime, ML interfaces, and algorithm implementations.

- **C1:** The [synchronization controller](https://github.com/Angel-ML/angel/blob/master/docs/design/sync_controller_en.md) implements BSP, bounded-staleness SSP, and ASP using partition-level vector clocks and worker synchronization threads. The guide explicitly discusses the convergence consequences of relaxing ordering.
- **C2:** The [code-framework guide](https://github.com/Angel-ML/angel/blob/master/docs/overview/code_framework_en.md) separates PS server/agent/worker components, matrix/vector/optimizer interfaces, client integration, and algorithm libraries. The parameter-server service can support Spark without replacing the core.

**Entry points:** [Synchronization design](https://github.com/Angel-ML/angel/blob/master/docs/design/sync_controller_en.md); [code architecture](https://github.com/Angel-ML/angel/blob/master/docs/overview/code_framework_en.md).

### 11. [Bluefog-Lib/bluefog](https://github.com/Bluefog-Lib/bluefog)

**Language / role:** C++ and Python; graph-based decentralized optimization and communication.

Study algorithms that average information over selected neighbors rather than synchronizing the whole worker population. The repository acknowledges its Horovod ancestry; its graph-neighbor and one-sided operation families provide the substantive architectural distinction for retaining it separately.

- **C1:** [One-sided operations](https://bluefog-lib.github.io/bluefog/bluefog_ops.html) separate remote writes from local visibility and averaging through `win_update`; window creation/freeing remain collective. Hierarchical neighbor averaging also has an explicit homogeneous-process-count restriction.
- **C2:** Collective, neighbor, hierarchical, and one-sided APIs support different synchronous and asynchronous optimization algorithms.
- **C3:** The operation guide decomposes hierarchical communication into local averaging, communication between local leaders, broadcast, and final averaging to reduce intermachine traffic.

**Entry point:** [Operation semantics and hierarchical implementation](https://bluefog-lib.github.io/bluefog/bluefog_ops.html).

### 12. [learning-at-home/hivemind](https://github.com/learning-at-home/hivemind)

**Language / role:** Python; decentralized PyTorch learning across heterogeneous, unreliable Internet-connected peers.

Study execution without a fixed master or stable all-worker barrier. The repository combines DHT-based discovery with peer averaging and distributed experts, exposing a different failure model from a tightly managed GPU cluster.

- **C1:** The [averager API](https://learning-at-home.readthedocs.io/en/latest/modules/averaging.html) makes matchmaking, request/chunk/sender/reducer timeouts, state sharing, and group formation explicit. These reveal where peer failure and partial participation enter the execution protocol.
- **C2:** `DecentralizedAverager` operates over supplied tensors with configurable grouping, compression, and averaging strength, making it usable independently of one model architecture.
- **C3:** Chunk sizing and bandwidth-aware work allocation—including peers that rely on others to perform averaging—address heterogeneous network capacity directly.

**Entry point:** [Decentralized averaging contract and configuration](https://learning-at-home.readthedocs.io/en/latest/modules/averaging.html).

### 13. [BaguaSys/bagua](https://github.com/BaguaSys/bagua)

**Language / role:** Python, Rust, and CUDA/C++; distributed PyTorch training with communication and synchronization relaxations. **Explicitly unmaintained**, according to the repository notice.

Study the system consequences of choosing compressed, decentralized, or asynchronous communication through a common training integration. It is a historical implementation with more breadth than a single gradient-compression demonstration.

- **C2:** Algorithms are supplied to the model integration through `with_bagua`, and the [repository](https://github.com/BaguaSys/bagua) exposes centralized, decentralized, low-precision, and asynchronous choices.
- **C3:** The official [ByteGrad design](https://tutorials-8ro.pages.dev/algorithms/bytegrad) gives a concrete hierarchy: local gradient reduction, min/max-based quantization, inter-node exchange, and local broadcast. It explains where compression occurs and which network traffic it targets.

**Entry point:** [ByteGrad algorithm and model integration](https://tutorials-8ro.pages.dev/algorithms/bytegrad). This tutorial host is linked directly by the official repository.

## Framework execution, sharding, and automatic parallelization

### 14. [pytorch/pytorch](https://github.com/pytorch/pytorch) — distributed execution

**Language / role:** Python and C++; `torch.distributed`, c10d process groups, and distributed data-parallel execution within the PyTorch monorepo.

Study how autograd readiness is converted into communication while preserving identical model updates across replicas. The DDP design note provides a particularly useful route into a large codebase.

- **C1:** DDP broadcasts initial state, tracks parameter readiness, and marks unused parameters so missing gradients do not cause an indefinite wait. Bucket reductions must execute consistently across processes. These obligations are detailed in the [DDP internal design](https://docs.pytorch.org/docs/2.14/notes/ddp.html).
- **C2:** The design separates the model wrapper, reducer, autograd hooks, and process-group communication abstraction.
- **C3:** Gradient bucketing and asynchronous all-reduce overlap backward computation with communication; bucket construction and graph compilation interact with that schedule.

**Entry point:** [DDP design note and implementation references](https://docs.pytorch.org/docs/2.14/notes/ddp.html).

### 15. [tensorflow/tensorflow](https://github.com/tensorflow/tensorflow) — `tf.distribute`

**Language / role:** Python and C++; distribution strategies, distributed variables, and worker coordination inside TensorFlow.

Study how a framework makes variables, optimizers, checkpoints, and training loops aware of distribution without requiring every model to implement a transport protocol.

- **C1:** The [distribution guide](https://www.tensorflow.org/guide/distributed_training) distinguishes identical mirrored-variable updates from asynchronous parameter-server updates. Its coordinator owns resource creation, remote step dispatch, checkpoints, and handling failed tasks.
- **C2:** `Strategy` covers custom loops and Keras execution across multiworker GPU and TPU configurations. Replaceable cross-device operations separate reduction implementation from model semantics.
- **C3:** Multiworker execution exposes ring/RPC and NCCL communication choices, while all-reduce combines aggregation and replication rather than treating them as independent transfers.

**Entry point:** [Distribution strategies and execution architecture](https://www.tensorflow.org/guide/distributed_training).

### 16. [jax-ml/jax](https://github.com/jax-ml/jax) — multi-controller execution and sharded arrays

**Language / role:** Python and C++; distributed array programming and execution integration with XLA.

Study the distinction between a global logical array and the shards addressable by one process. This selection concerns JAX's distributed programming/execution interfaces; XLA is a separate implementation dependency and is not counted as part of this repository.

- **C1:** The [multi-controller guide](https://docs.jax.dev/en/latest/multi_process.html) requires all participating processes to issue compatible computations in the same order; divergent control flow can strand collective operations. It also explains why nonlocal shards cannot simply be fetched as local arrays.
- **C2:** Device meshes, global arrays, and sharding descriptions provide reusable abstractions for model and data partitioning.
- **C3:** The guide demonstrates distributed matrix multiplication in which the compiler partitions execution and inserts communication according to array layout, exposing the connection between placement and network work.

**Entry point:** [Multi-process arrays, meshes, and ordering rules](https://docs.jax.dev/en/latest/multi_process.html).

### 17. [deepspeedai/DeepSpeed](https://github.com/deepspeedai/DeepSpeed) — ZeRO runtime

**Language / role:** Python, C++, and CUDA; sharded model-state execution and memory offload for distributed training.

Study parameter materialization as a runtime protocol. ZeRO partitions optimizer state, gradients, and eventually parameters, so executing a module requires coordinating the availability and lifetime of its weights.

- **C1:** The [ZeRO guide](https://deepspeed.readthedocs.io/en/latest/zero3.html) documents assumptions about accessing parameters inside their owning module, mechanisms for external/shared parameters, and precision-sensitive state access. Violating those assumptions changes what data is present when computation runs.
- **C2:** Initialization contexts, gathered-parameter scopes, external-parameter registration, and state inspection APIs support models with different ownership patterns.
- **C3:** CPU/NVMe offload, communication overlap, and memory-centric tiling address capacity and transfer bottlenecks through identifiable runtime mechanisms.

**Entry point:** [ZeRO partitioning, coordination, and offload](https://deepspeed.readthedocs.io/en/latest/zero3.html).

### 18. [NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM) — Megatron Core

**Language / role:** Python with accelerated backend integration; composable large-model parallel training.

Study how different partitioning dimensions affect memory, communication, and scheduling. The relevant reusable subsystem is Megatron Core, rather than only the model-training scripts shipped in the repository.

- **C2:** The [parallelism guide](https://docs.nvidia.com/megatron-core/developer-guide/latest/user-guide/parallelism-guide.html) distinguishes data, tensor, pipeline, context, expert, and fully sharded execution and describes combinations of these strategies.
- **C3:** Separate controls overlap gradient reduction with backward computation, parameter gathering with forward computation, and tensor-parallel communication with compute. Sequence partitioning targets activation memory. The guide discusses memory/communication tradeoffs rather than offering only a launcher abstraction.

**Entry point:** [Parallelism architecture and overlap controls](https://docs.nvidia.com/megatron-core/developer-guide/latest/user-guide/parallelism-guide.html).

### 19. [hpcaitech/ColossalAI](https://github.com/hpcaitech/ColossalAI)

**Language / role:** Python with C++/CUDA components; hybrid parallel execution, sharding, and distributed optimizers.

Study the numerical work required when an optimizer needs statistics for an entire layer but each rank owns only part of it. This provides a useful complement to implementations that focus primarily on Adam/SGD sharding.

- **C1:** The [distributed-optimizer guide](https://colossalai.org/docs/features/distributed_optimizers/) explains why layer-wise statistics make ordinary optimizer implementations invalid for sharded layers, then documents distributed Adafactor, CAME, GaLore, and Lamb integration.
- **C2:** Booster and hybrid-parallel plugins connect optimizer implementations with tensor parallelism, DDP, and ZeRO rather than requiring a separate application loop for each combination.
- **C3:** The design explicitly targets additional communication introduced by distributed optimizer statistics, alongside the memory-saving goals of the optimizer algorithms.

**Entry point:** [Distributed optimizer semantics and plugin integration](https://colossalai.org/docs/features/distributed_optimizers/).

### 20. [Oneflow-Inc/oneflow](https://github.com/Oneflow-Inc/oneflow)

**Language / role:** C++, CUDA, and Python; a framework whose distributed compiler/runtime uses global tensor layouts and actor execution.

Study an alternative to bolting parallelism onto an originally local execution model. OneFlow describes logical-to-physical tensor mappings using placement and SBP: split, broadcast, and partial values.

- **C1:** The [system design](https://docs.oneflow.org/en/v0.4.0/basics_topics/essentials_of_oneflow.html) explains legal operator SBP signatures and insertion of boxing operations when producer and consumer layouts differ. These conversions must preserve the meaning of the logical tensor, including gradient partial sums.
- **C2:** Placement, SBP signatures, and boxing form a reusable representation for data, model, and pipeline parallelism.
- **C3:** Actor scheduling and explicit data movement connect dependency management with pipelining and communication cost.

**Entry point:** [System design](https://docs.oneflow.org/en/v0.4.0/basics_topics/essentials_of_oneflow.html). This is a versioned, older architectural explanation; the current repository uses Global Tensor terminology and should be consulted for current APIs.

### 21. [alpa-projects/alpa](https://github.com/alpa-projects/alpa)

**Language / role:** Primarily Python; automatic parallelization compiler and distributed runtime built on JAX/XLA and Ray. **Archived October 19, 2024; explicitly a research artifact.**

Study the decomposition of a large parallelization search into inter-operator and intra-operator decisions. The repository notes that its core auto-sharding algorithm was incorporated into XLA; the retained GitHub project remains the historical integrated implementation.

- **C2:** The [architecture](https://github.com/alpa-projects/alpa/blob/main/docs/architecture/overview.rst) separates graph stages, device meshes, Ray-backed workers, compiler passes, and runtime orchestration.
- **C3:** An inter-operator pass chooses stage/mesh assignments, an intra-operator pass chooses partitioning within each mesh, and orchestration generates cross-mesh resharding and static pipeline schedules to reduce runtime scheduling overhead.

**Entry point:** [Compiler/runtime architecture](https://github.com/alpa-projects/alpa/blob/main/docs/architecture/overview.rst). The document has an unfinished standalone resharding subsection, but its orchestration section substantively describes the required communication.

### 22. [flexflow/flexflow-train](https://github.com/flexflow/flexflow-train)

**Language / role:** C++ with Python bindings and accelerator kernels; automatic discovery of distributed training parallelization strategies.

Study parallelization as a compiler problem over a parallel computation graph, with distinct graph, compiler, kernel, and execution layers. The original FlexFlow repository now redirects here following a training/serving split; the serving repository is not counted in this selection.

- **C2:** The [current library tree](https://github.com/flexflow/flexflow-train/tree/master/lib) separates `pcg`, compiler, substitutions, task specifications, kernels, and local/Realm execution. This is a useful route into reusable representations rather than only end-to-end model examples.
- **C3:** The [developer guide](https://flexflow.readthedocs.io/en/stable/developers_guide/developers_guide.html) explains parallelization operators, runtime/mapping responsibilities, and separation of high-level operators from CUDA/HIP kernels; the repository identifies automated parallelization search as its training function.

**Entry points:** [Current implementation modules](https://github.com/flexflow/flexflow-train/tree/master/lib); [architectural developer guide](https://flexflow.readthedocs.io/en/stable/developers_guide/developers_guide.html). The latter predates the current `lib/` organization, so its old paths are historical orientation, not current source locations.

## Training orchestration and distributed actor execution

### 23. [ray-project/ray](https://github.com/ray-project/ray) — Ray Train and supporting runtime

**Language / role:** Python and C++; distributed execution runtime, scoped here to training worker groups and recovery.

Study where model-level checkpointing meets a general distributed process runtime. Ray Train makes worker failures, node loss, and driver loss separate cases rather than presenting all restart behavior as one transparent operation.

- **C1:** The [failure-handling guide](https://docs.ray.io/en/latest/train/user-guides/fault-tolerance.html) describes shutting down and restarting the complete training worker group after a worker-node failure, restoring the latest checkpoint, and separately relaunching a failed driver using persistent run state.
- **C2:** Framework trainers share worker orchestration, storage/checkpoint integration, and configurable retry behavior, allowing application training functions to reuse recovery machinery.
- **C3:** Recovery avoids discarding an entire run, but restart work depends on checkpoint cadence and resource replacement. The guide gives explicit execution sequences and documents the Train V2 API boundary.

**Entry point:** [Worker, node, and driver recovery](https://docs.ray.io/en/latest/train/user-guides/fault-tolerance.html).

### 24. [kubeflow/trainer](https://github.com/kubeflow/trainer)

**Language / role:** Primarily Go; Kubernetes control plane for distributed training jobs and reusable training runtimes.

Study execution preparation and lifecycle control outside the numerical training loop: validation, resource construction, framework-specific policy, watches, and terminal-state propagation.

- **C1:** The [v2 design](https://github.com/kubeflow/trainer/tree/master/proposals/2170-kubeflow-trainer-v2) spells out immutable runtime/controller ownership fields, suspension, and child-job status accounting. These are concrete reconciliation invariants rather than ordinary container-launch scripting.
- **C2:** The [extension framework](https://trainer.kubeflow.org/en/latest/operator-guides/extension-framework.html) separates startup, pre-execution, build, and post-execution phases. Plugins supply validation, watches, ML policy, pod-group policy, and resource builders for different training runtimes.

**Entry points:** [Extension architecture](https://trainer.kubeflow.org/en/latest/operator-guides/extension-framework.html); [v2 design and API rationale](https://github.com/kubeflow/trainer/tree/master/proposals/2170-kubeflow-trainer-v2). Proposal text is design evidence; the operational guide is the companion implementation-facing reference.

### 25. [meta-pytorch/monarch](https://github.com/meta-pytorch/monarch)

**Language / role:** Rust and Python; actor-based, single-controller programming for multi-machine PyTorch execution.

Study a different distributed programming model from one Python controller per training rank. Actors are arranged into multidimensional meshes that support collective addressing and slicing while retaining explicit resource ownership.

- **C1:** The [actor guide](https://meta-pytorch.org/monarch/stable/actors.html) specifies that meshes have at most one owner and cannot outlive it. Unhandled failures propagate through a supervision tree, and cleanup ordering is defined. Supervision can interrupt an actor at safe points, making reentrancy a visible design concern.
- **C2:** Host, process, and actor meshes, typed endpoints, asynchronous result gathering, and slicing provide reusable building blocks for multi-machine training arrangements beyond a fixed data-parallel loop.

**Entry point:** [Actor model, mesh operations, and supervision](https://meta-pytorch.org/monarch/stable/actors.html).

## Search coverage and limitations

Discovery used more than six distinct search formulations, including distributed ML communication architecture; pipeline-parallel execution and scheduling; parameter servers and push/pull aggregation; decentralized neighbor averaging and unreliable peers; GPU collectives and device-initiated communication; automatic inter-/intra-operator parallelization; sharded optimizers; Java/Scala parameter-server systems; elastic training and Kubernetes control planes; and Rust-backed communication compression. Follow-up searches covered Bagua, Hetu/Galvatron, AxoNN, and specialized pipeline schedules. Later results increasingly repeated the architectural families already represented; Bagua was retained to add a concrete quantized communication design.

Every selected canonical GitHub repository was opened, and each entry has additional opened primary documentation, design discussion, or implementation evidence. Verification followed redirects and project notices: Gloo's current owner, Angel's current organization, DeepSpeed's organization, RCCL's monorepo move, and FlexFlow's training/serving split are reflected above. No forks are counted merely for preserving upstream code; BlueFog is retained for its distinct decentralized communication model. Repository stars were not used as quality evidence.

The scope excludes launcher-only templates, tutorials implementing toy distributed training, model zoos, awesome-lists, and ordinary application wrappers. Generic MPI/UCX infrastructure and generic cluster schedulers were not expanded into separate entries; the focus is systems with an explicit ML execution or communication layer. Specialized systems such as Hetu/Galvatron and AxoNN remain plausible further study targets, but are not claimed to have failed the criteria. This is a diverse selection, not an exhaustive catalog.

Limitations: no candidate code was executed, dependencies installed, benchmarks reproduced, or large repositories cloned. Some rendered GitHub/documentation routes failed to load; retained claims use successful alternative primary pages. Older architectural guides are labeled where they differ from current source organization. Archived or unmaintained systems are included for study, not recommended as newly supported deployment dependencies. Performance judgments concern inspectable mechanisms, not unverified speedup numbers. C4 is awarded conservatively where a longitudinal changelog was actually inspected.
