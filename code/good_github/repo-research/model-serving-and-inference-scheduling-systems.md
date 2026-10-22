# Model serving and inference scheduling systems

Research date: **2026-10-09**.

This selection covers 26 GitHub repositories implementing model-serving runtimes, batching and request schedulers, model lifecycle control planes, distributed inference routing, and serving-specific cache infrastructure. It includes conventional prediction, embedding and reranking services, autoregressive generation, and diffusion inference. Research systems are included where their implementations expose a distinct scheduling idea worth studying. Ray and llama.cpp are counted once each, with the relevant serving subsystem identified.

The criteria below are evidence-based selection judgments, not a correctness audit or a claim that every component is exemplary. Repository pages and the additional primary sources linked in each entry were opened and read. Performance mechanisms are described without adopting unverified benchmark claims. Archive and historical status are called out where established; inclusion otherwise makes no blanket claim about current maintenance.

- **C1 — Difficult correctness:** meaningful invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components supporting multiple models, applications, policies, or deployments.
- **C3 — Structured performance engineering:** concrete latency, throughput, memory, or resource constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** evidence spanning years together with compatibility work, testing, or explicit complexity management. Age alone does not qualify.

## General-purpose model servers

### 1. [tensorflow/serving](https://github.com/tensorflow/serving)

**Language/role:** C++; model lifecycle management and RPC inference serving.

Study how model loading and retirement are separated from inference execution. A servable has a versioned identity, while Sources, Loaders, and Managers divide discovery, resource acquisition, and availability decisions. This makes the code useful beyond a single TensorFlow prediction endpoint.

- **C1:** A newly requested version does not simply overwrite the old one. The manager coordinates loading, availability, and retirement; availability-preserving policies can retain an old version until its replacement is ready. This exposes the interaction between concurrent requests and model lifetime.
- **C2:** Source and Loader interfaces separate artifact discovery from the concrete computation being served. The architecture explicitly treats a servable as a general computation object.
- **C3:** `SharedBatchScheduler` multiplexes separate task queues over a shared thread pool. Queue limits, batching timeouts, and queue addition/removal connect throughput policy to model-version turnover.

Entry points: [serving architecture](https://www.tensorflow.org/tfx/serving/architecture) and [batching library design](https://github.com/tensorflow/serving/blob/master/tensorflow_serving/batching/README.md).

### 2. [triton-inference-server/server](https://github.com/triton-inference-server/server)

**Language/role:** C++ with Python tooling; inference server integrating multiple execution backends.

Triton is particularly useful for comparing scheduling contracts for stateless and stateful models. This entry covers the server project and its documented scheduler integration; portions of the underlying implementation live in companion Triton repositories, which are not counted separately here.

- **C1:** Sequence batching preserves model-instance affinity and conveys sequence start, end, and identity information. Dynamic batching separately exposes response ordering and queue timeout policies. These are different correctness obligations, not interchangeable batching options.
- **C2:** Backend integration and configurable batch policies let the same serving infrastructure accommodate different model execution environments and request semantics.
- **C3:** Preferred batch sizes, bounded queue delay, priority queues, and iterative sequence rescheduling expose concrete throughput/latency choices. Iterative sequences can mix work that continues from previous execution steps with newly admitted work; the documentation marks this facility as provisional.

Entry point: [dynamic, sequence, and iterative batching guide](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/batcher.html).

### 3. [openvinotoolkit/model_server](https://github.com/openvinotoolkit/model_server)

**Language/role:** C++ and Python; OpenVINO-based prediction and generative-model serving.

OVMS offers a useful view of artifact-driven model lifecycle management across OpenVINO execution targets. Its repository documents conventional inference alongside generative APIs, allowing an engineer to study how one server accommodates different request surfaces.

- **C1:** Version policies distinguish all versions, the latest versions, and explicitly selected versions. Directory monitoring loads new versions and unloads removed ones, but changing an already loaded artifact does not itself trigger replacement. The documented Windows memory-mapping restriction makes filesystem and model-lifetime interactions concrete.
- **C2:** Model configuration and version selection are reusable serving abstractions across deployed models, with standard inference protocols and OpenAI-compatible generative interfaces described by the repository. The version-policy document also states an important boundary: this mechanism applies to individual models, not DAG or MediaPipe definitions.

Entry point: [model version policy and reload semantics](https://github.com/openvinotoolkit/model_server/blob/main/docs/model_version_policy.md).

### 4. [deepjavalibrary/djl-serving](https://github.com/deepjavalibrary/djl-serving)

**Language/role:** Java with Python model integrations; model server and reusable workload manager.

DJL Serving is a substantive JVM counterpart to the predominantly Python/C++ ecosystem. Its architecture separates the Netty frontend, endpoint and model management, workflow execution, and worker scheduling.

- **C2:** A workflow composes models and glue logic, while the WorkLoadManager is available independently of the HTTP server. Models shared by multiple workflows can use the same underlying workload-management instance rather than requiring one worker infrastructure per composition.
- **C3:** Worker threads, batching, request routing, and worker scaling are organized behind workload management. The explicit separation makes it possible to trace how endpoint/version routing becomes executable batches without conflating networking with model execution.

Entry point: [architecture, workflows, and WorkLoadManager](https://github.com/deepjavalibrary/djl-serving/blob/master/serving/docs/architecture.md).

### 5. [SeldonIO/MLServer](https://github.com/SeldonIO/MLServer)

**Language/role:** Python; extensible inference runtimes, protocol handling, and worker pools.

MLServer is useful for studying the boundary between a model runtime and generic serving machinery. Its adaptive batching combines requests and then reconstructs individual responses, including parameter handling across the combined request.

- **C2:** Custom inference runtimes and codecs provide extension points for models and input/output types while retaining common serving protocols and process management.
- **C3:** Per-model batch size and waiting-time settings expose the latency/throughput tradeoff. Worker-pool changes in the changelog also address starvation between inference workloads.
- **C4:** The inspected changelog spans 2022–2025 and records custom-runtime API simplification, worker-queue fixes, Pydantic v2 migration, Python-version CI changes, streaming support, and a batching timeout fix. This is direct evidence of compatibility and concurrency-related maintenance across years.

Entry points: [adaptive batching semantics](https://github.com/SeldonIO/MLServer/blob/master/docs/user-guide/adaptive-batching.md) and [dated changelog](https://github.com/SeldonIO/MLServer/blob/master/CHANGELOG.md).

## Serving frameworks and deployment control planes

### 6. [ray-project/ray](https://github.com/ray-project/ray)

**Language/role:** Python serving subsystem over Ray's Python/C++ distributed runtime. **Relevant subsystem: Ray Serve.**

Study Serve's controller, proxy, replica, and deployment-handle architecture. The relevant contribution is the distributed serving layer rather than Ray's entire collection of training and data libraries.

- **C1:** The architecture distinguishes durable deployment configuration from transient request queues. Controller recovery uses checkpointed configuration, while proxy or replica failures can lose in-flight work. Existing serving can continue through a controller outage even though control operations and autoscaling are affected.
- **C2:** Deployment handles reuse request-routing machinery for composition between deployments; replicas encapsulate user application execution independently of HTTP/gRPC proxies.
- **C3:** Per-deployment queues, maximum ongoing-request limits, replica selection, and autoscaling from queued/in-flight demand connect admission pressure to distributed capacity.

Entry point: [Ray Serve architecture and fault tolerance](https://docs.ray.io/en/latest/serve/architecture.html).

### 7. [bentoml/BentoML](https://github.com/bentoml/BentoML)

**Language/role:** Python; service definitions, model application composition, and adaptive inference batching.

BentoML is a useful application-facing example: a typed service method becomes a batching boundary, and service dependencies allow different execution stages to be composed.

- **C2:** The batchable API, typed inputs, input/output batch dimensions, and service dependency abstractions let serving behavior be expressed independently of a particular model framework. Composite input objects provide a way to retain a single batching argument while representing richer requests.
- **C3:** The dispatcher estimates execution cost to select batches under configured latency and size targets. The guide also explains how endpoint concurrency and synchronous worker capacity constrain whether batching can actually accumulate useful work, and how overload can produce rejection.

Entry point: [adaptive batching and service examples](https://docs.bentoml.com/en/latest/get-started/adaptive-batching.html). Treat the latency setting as a dispatch target described by the implementation, not an unconditional end-to-end guarantee.

### 8. [kserve/kserve](https://github.com/kserve/kserve)

**Language/role:** Go and Python; Kubernetes inference lifecycle and deployment control plane.

KServe belongs here because it turns serving intent into reconciled deployment, networking, and scaling resources. Its contribution is broader than any single model execution backend.

- **C1:** InferenceService validation, mutation, reconciliation, readiness, rollout, and cleanup form a lifecycle with partially created or changing distributed resources. These boundaries are the main correctness study target.
- **C2:** The InferenceService contract separates user-facing serving configuration from the Kubernetes resources and serving runtimes needed to implement it.
- **C3:** The documented Standard and Knative modes make different scaling and routing mechanisms explicit: Deployments/Services and HPA or KEDA versus Knative Services/Revisions, queue proxies, and scale-to-zero. Their cold-start and routing implications can be studied without attributing every capability to every mode.

Entry point: [control-plane architecture and deployment modes](https://kserve.github.io/website/docs/concepts/architecture/control-plane).

### 9. [SeldonIO/seldon-core](https://github.com/SeldonIO/seldon-core)

**Language/role:** Go control services, Java stream processing, and Python integrations; distributed model and inference-pipeline serving. **Scope: the v2 architecture.**

The current repository identifies a Business Source License; treat this as a source-available study target and check its terms for intended reuse. Architecturally, its scheduler/agent separation and Kafka-based pipeline execution distinguish it from a simple endpoint controller.

- **C1:** Scheduler restart behavior includes persistence and a reconnection interval for servers. Existing data-plane execution can survive scheduler unavailability, while agents handle local model loading and unloading. This exposes recovery coordination without assuming control-plane health is necessary for every inference.
- **C2:** Pipeline gateways, model gateways, and Kafka Streams assemble synchronous API calls into reusable dataflow operations, including joins and triggers. The architecture separates model placement, local execution, traffic routing, and pipeline semantics.

Entry point: [v2 architecture and component responsibilities](https://github.com/SeldonIO/seldon-core/blob/v2/docs-gb/architecture/README.md).

### 10. [kserve/modelmesh](https://github.com/kserve/modelmesh)

**Language/role:** Java; distributed model-residency management and routing. **Archived on April 14, 2026**, as shown on the repository page.

ModelMesh is a historical but substantial design for serving many more models than can remain resident simultaneously. It should be read as its own runtime-management implementation, not as another copy of the KServe controller.

- **C1:** Its runtime contract distinguishes loading, unloading, capacity reporting, and inference against fully loaded models. The documented idempotency requirement and immutable model identities matter when requests and residency operations span multiple instances; mutable virtual-model names add an explicit indirection layer.
- **C2:** The runtime API does not require ModelMesh to understand model formats. Separate runtimes supply model-specific execution and resource information.
- **C3:** Distributed LRU residency and request routing coordinate scarce memory across a pool of runtime instances, making eviction and reload costs central to the architecture.

Entry point: [runtime interface and model-management design](https://raw.githubusercontent.com/kserve/modelmesh/main/docs/README.md).

## Inference engines and local request schedulers

### 11. [vllm-project/vllm](https://github.com/vllm-project/vllm)

**Language/role:** Python, C++, and CUDA; generative inference engine and serving runtime.

The architecture overview makes vLLM valuable beyond its individual attention kernels. It traces requests from API processes through engine scheduling to GPU workers and model runners.

- **C2:** Model runners, workers, configuration objects, and execution interfaces separate model integration from process orchestration. The documented model initialization path also explains how sharding and quantization fit into loading rather than requiring every worker to materialize an entire model first.
- **C3:** CPU-side request preparation, EngineCore scheduling/KV management, and GPU execution occupy distinct processes and responsibilities. Data-parallel coordination and messaging topology expose where scheduling decisions and capacity boundaries live.

Entry point: [architecture overview](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/design/arch_overview.md). This entry concerns the serving engine and its process structure, not a claim that every supported model has identical execution behavior.

### 12. [sgl-project/sglang](https://github.com/sgl-project/sglang)

**Language/role:** Python, C++/CUDA, and Rust components; structured generation and inference serving.

SGLang provides a particularly clear connection between shared prompt structure and runtime scheduling. Its authors' architectural account explains RadixAttention and how cache-aware scheduling exploits shared prefixes.

- **C1:** The radix tree represents shared token prefixes while GPU memory holds the corresponding KV tensors. Splitting tree nodes, retaining shared paths, and evicting eligible leaves create concrete ownership and mapping invariants to inspect.
- **C3:** Prefix reuse avoids repeated computation across related requests, and scheduling considers cache locality alongside continuous batching. This is a different optimization axis from merely increasing batch size.

Entry point: [authors' RadixAttention and scheduler design article](https://www.lmsys.org/blog/2024-01-17-sglang/). This 2024 source establishes the foundational design; it is not evidence that every detail of the expanding current repository remains unchanged. The monorepo is counted only once.

### 13. [InternLM/lmdeploy](https://github.com/InternLM/lmdeploy)

**Language/role:** Python and C++/CUDA; deployment toolkit with TurboMind and PyTorch inference engines.

TurboMind's architecture offers an approachable study of persistent inference batches and the relationship between session state and KV-cache residency.

- **C1:** The documented cache design distinguishes retained KV state from compact token history. When cached state is evicted, the history supports reconstruction rather than treating the session as nonexistent. Studying this path reveals which state is authoritative and which is an optimization.
- **C3:** Requests can join free batch slots and leave independently instead of waiting for all members of a fixed batch to finish. The cache pool and persistent-batch execution connect request turnover to memory reuse and GPU utilization.

Entry point: [TurboMind architecture](https://lmdeploy.readthedocs.io/en/latest/inference/turbomind.html). The guide is evidence for the described design; cache granularity and engine-specific behavior should be checked against the version being studied.

### 14. [NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)

**Language/role:** Python, C++, and CUDA; optimized generative inference and request scheduling.

The PyTorch-backend scheduler documentation exposes a useful separation between determining which requests fit and choosing the next execution microbatch.

- **C1:** Capacity decisions must agree with the resource managers that actually allocate and release KV blocks. The documented no-eviction policy reserves capacity for running requests before admitting more work, exposing a concrete invariant between admission and future generation requirements.
- **C2:** CapacityScheduler and MicroBatchScheduler can be customized separately, or replaced through RequestScheduler. Scheduling policy is therefore an explicit integration interface rather than an inseparable part of model execution.
- **C3:** Microbatch selection accounts for resource fit and pipeline work already in flight, making execution overlap and memory pressure visible in the scheduling design.

Entry point: [PyTorch scheduler architecture and extension examples](https://nvidia.github.io/TensorRT-LLM/latest/torch/scheduler.html).

### 15. [huggingface/text-generation-inference](https://github.com/huggingface/text-generation-inference)

**Language/role:** Rust router with Python and accelerator-side model execution; text-generation serving. **Archived on March 21, 2026**, according to the repository page.

TGI remains a useful historical implementation of a router/launcher/model-server split. The archive status takes precedence over older documentation that describes ongoing support.

- **C2:** The HTTP router manages public requests, the launcher coordinates model-server processes, and gRPC connects the routing and execution components. These contracts separate batching and service concerns from model-specific execution.
- **C3:** Router-side queues and token budgets control prefill admission and waiting work. The architecture explains how requests become batches and how sharded model servers participate in execution, making the effect of request limits more concrete than a collection of command-line flags alone.

Entry point: [TGI component and request architecture](https://huggingface.co/docs/text-generation-inference/en/architecture). Retained for architectural study, not as an assertion of active maintenance.

### 16. [huggingface/text-embeddings-inference](https://github.com/huggingface/text-embeddings-inference)

**Language/role:** Rust with accelerator backends; embedding, reranking, and classification serving.

TEI adds a non-autoregressive scheduling case. Its queue implementation is compact enough to study directly while still handling cancellation, token budgets, and result indexing.

- **C1:** Queue state is owned by a background task receiving commands; closed response channels identify cancelled work. Batch construction maintains sequence offsets and separate output-index sets, so combining requests must preserve their eventual response correspondence.
- **C3:** Admission distinguishes padded batches, whose cost depends on the maximum sequence length times batch size, from packed batches, whose cost is the sum of token lengths. A request that would exceed the budget is returned to the front of the queue instead of silently overcommitting the batch.

Entry point: [queue and batch construction implementation](https://raw.githubusercontent.com/huggingface/text-embeddings-inference/main/core/src/queue.rs).

### 17. [EricLBuehler/mistral.rs](https://github.com/EricLBuehler/mistral.rs)

**Language/role:** Rust with CUDA/Metal support; model runtime and inference server.

The scheduler module provides a useful systems-language study of request lifetime, resource admission, and interchangeable scheduler implementations.

- **C1:** Prefix-cache validation can be staged and committed only after KV admission succeeds. Cancellation and completed-group cleanup interact with sequence and recurrent-state ownership. The same module includes checks around cache reconfiguration, including tests that rejected changes preserve existing limits.
- **C2:** A shared Scheduler trait supports default and paged-attention scheduling, with hooks for different sequence and media requirements. The interface exposes allocation and cleanup responsibilities rather than reducing scheduling to ordering a list of requests.
- **C3:** Sequence limits and separate prefill/decode token budgets make memory and execution constraints explicit at the scheduler boundary.

Entry point: [scheduler interfaces, admission, and tests](https://raw.githubusercontent.com/EricLBuehler/mistral.rs/master/mistralrs-core/src/scheduler/mod.rs).

### 18. [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)

**Language/role:** C/C++ with several CPU/GPU backends. **Relevant subsystem: `tools/server`.**

The server is worth examining independently of the tensor runtime: it turns parallel requests into slots and shared execution batches on resource-constrained local machines as well as larger hosts.

- **C1:** Server slots move through explicit prompt-processing and generation states. The server context tracks which batch positions belong to which slots; speculative-generation replay also coordinates accepted tokens with sampler state. These are concrete per-sequence correctness obligations inside shared execution.
- **C3:** Continuous batching, prompt-cache reuse, parallel slots, and logical versus physical batch limits connect user-visible concurrency to bounded execution work. The server documentation exposes the knobs, while the context implementation reveals the state machinery behind them.

Entry points: [server guide](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) and [server context implementation](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/server-context.cpp).

## Distributed routing and serving-specific cache infrastructure

### 19. [ai-dynamo/dynamo](https://github.com/ai-dynamo/dynamo)

**Language/role:** Rust and Python; distributed inference orchestration, routing, and resource management.

Dynamo is useful for tracing how a serving engine becomes a distributed service with separate prefill/decode workers, cache-location knowledge, and capacity planning.

- **C1:** The developer architecture discusses worker discovery, stale endpoints, health, draining, cancellation, and overload handling. These mechanisms expose the failure cases around routing to workers whose availability is changing.
- **C2:** The architecture separates request processing, control operations, and cache events, with engine integrations and transport interfaces beneath them. This supports multiple execution backends without requiring the router to own model internals.
- **C3:** Routing considers KV overlap and load, while planning can scale prefill and decode capacity independently. Cache events and transfer mechanisms connect placement decisions to the cost of moving or recomputing state.

Entry point: [developer architecture and component responsibilities](https://github.com/ai-dynamo/dynamo/blob/main/docs/fern/pages/developer-guide/knowledge-base/overview.md).

### 20. [llm-d/llm-d-router](https://github.com/llm-d/llm-d-router)

**Language/role:** Go; inference endpoint selection and routing policy.

This is the verified canonical repository reached from the former `llm-d-inference-scheduler` URL. Its architecture is especially useful for studying composable routing policies rather than GPU-kernel execution.

- **C1:** Global screening constrains candidates across scheduling profiles, while admission plugins can reject work before selection. The distinction between mandatory eligibility and weighted preference matters when different profiles select prefill and decode destinations.
- **C2:** The pipeline separates data production, admission, filtering, scoring, and final selection. Plugins can contribute policy without rewriting the endpoint-selection process; the documentation also explains configuration-version translation.
- **C3:** Cache and load information can inform routing, with multiple scheduling profiles supporting phase-specific placement. The documented ordering of filters and scorers provides a concrete structure for understanding policy interactions.

Entry point: [router architecture and scheduling pipeline](https://github.com/llm-d/llm-d-router/blob/main/docs/architecture.md).

### 21. [kvcache-ai/Mooncake](https://github.com/kvcache-ai/Mooncake)

**Language/role:** C++ with Python integration; KV-cache storage and transfer infrastructure for distributed inference.

Scope here is the public Mooncake Store/transfer implementation and serving integrations, not an assumption that an entire production service is present in the repository. It belongs in this category because cache placement and transfer directly constrain disaggregated inference scheduling.

- **C1:** Immutable objects, metadata allocation, and replica handling impose publication and lifetime requirements. The documented optional high-availability path requires a promoted master to catch up and validate leadership before serving; the default single-master mode has a different failure boundary.
- **C2:** Put/Get/Remove operations and client/server role choices separate storage use from model-engine internals.
- **C3:** Clients transfer payloads directly, including through RDMA, while the master handles metadata. This separation makes the cache data path and its potential bottlenecks inspectable.

Entry point: [Mooncake Store architecture and availability design](https://github.com/kvcache-ai/Mooncake/blob/main/docs/source/design/store/mooncake-store.md).

## Research systems with distinctive scheduling designs

### 22. [ucbrise/clipper](https://github.com/ucbrise/clipper)

**Language/role:** C++ and Python; prediction-serving research system. **Historical: the repository explicitly says it is not actively maintained.**

Clipper is useful for understanding serving before the current LLM emphasis: model containers and adaptive batching are combined with a separate model-selection layer.

- **C2:** A model abstraction layer hides framework-specific execution behind containers, while a model-selection layer can choose or combine predictions. This separates “how to execute a model” from “which model should answer.”
- **C3:** The paper explains per-model adaptive batching using additive increase and multiplicative decrease around a latency objective. Delayed dispatch allows requests to accumulate, and different model execution costs lead to different batch choices.

Entry point: [authors' NSDI 2017 system paper, especially architecture and batching](https://www.usenix.org/system/files/conference/nsdi17/nsdi17-crankshaw.pdf). The historical implementation is a design study target; its dependency stack should not be mistaken for a current deployment recommendation.

### 23. [uwsampl/nexus](https://github.com/uwsampl/nexus)

**Language/role:** C++ with Python profiling tools; GPU inference scheduling research system associated with SOSP 2019.

Nexus connects request-level latency requirements to GPU placement and batch sizing. The authors' paper is particularly helpful for understanding the code's scheduling decomposition.

- **C2:** The query abstraction represents pipelines containing multiple DNN computations and permits shared computation across queries. Scheduling therefore operates on a richer workload than unrelated calls to one model.
- **C3:** Batch-aware packing treats GPU cost as dependent on batch size. Global scheduling coordinates model placement and execution allocation, while worker batching and frontend routing handle requests locally. Splitting a query's latency budget across its component models connects placement decisions to end-to-end service objectives.

Entry point: [authors' system paper, including scheduling and implementation sections](https://homes.cs.washington.edu/~arvind/papers/nexus.pdf). Retained as a historical research implementation; no active-maintenance claim is made.

### 24. [microsoft/sarathi-serve](https://github.com/microsoft/sarathi-serve)

**Language/role:** Python with C++/CUDA components; research serving engine focused on prefill/decode interference.

The repository identifies itself as a research prototype derived from vLLM and documents reduced feature parity. It is retained separately because the scheduler represents a substantive algorithmic implementation, not a cosmetic fork.

- **C1:** The scheduler checks cache capacity and sequence/token limits before adding work, and can preempt when a running sequence cannot append a slot. Admission, chunk progress, and running/waiting state must remain consistent.
- **C3:** Decode work and chunks of prefill are assembled under a shared token budget. The implementation makes chunk sizing and the treatment of already running prefills visible, providing a direct study of how to reduce long-prefill interference with ongoing generation.

Entry point: [Sarathi scheduling implementation](https://raw.githubusercontent.com/microsoft/sarathi-serve/main/sarathi/core/scheduler/sarathi_scheduler.py). Prototype scope and its vLLM provenance are material qualifications.

### 25. [LLMServe/DistServe](https://github.com/LLMServe/DistServe)

**Language/role:** Python orchestration with a separate model-execution dependency; disaggregated prefill/decode research implementation.

DistServe gives a concrete view of separating context processing from token generation rather than merely running two deployment replicas with different labels.

- **C1:** The engine coordinates separate processing loops, a bridge queue, per-request outputs, KV-handle registration, and cleanup of migrated context blocks. These mechanisms expose the ownership and handoff requirements before decoding can consume prefill state.
- **C3:** Separate stage configurations and Ray placement groups let prefill and decode use different parallel arrangements. Placement and KV migration are coordinated explicitly, revealing the communication costs and topology constraints behind disaggregation.

Entry point: [engine orchestration and migration implementation](https://raw.githubusercontent.com/LLMServe/DistServe/main/distserve/engine.py). This is a research implementation associated with the DistServe work, not evidence of broad production compatibility or ongoing maintenance.

### 26. [DiT-Serving/TetriServe](https://github.com/DiT-Serving/TetriServe)

**Language/role:** Python/PyTorch; multi-GPU diffusion-transformer serving research system associated with ASPLOS 2026.

TetriServe broadens the category beyond token decoding. It schedules diffusion requests with different resolutions and latency objectives, and can change their GPU allocation between groups of denoising steps.

- **C1:** Intermediate latents must follow the correct step dependency when a request moves to different ranks. The architecture describes per-GPU latent stores, deferred retrieval handles, request tracking, and dedicated transfer process groups that avoid interference with inference collectives.
- **C2:** The engine, scheduler, workers, and latent-transfer layer have separate responsibilities; multiple allocation policies share scheduled-request and dependency representations.
- **C3:** Cost estimates guide per-request sequence-parallel allocation, and scheduling rounds permit reassignment between diffusion steps. This exposes a different scheduling unit and resource tradeoff from autoregressive continuous batching.

Entry point: [architecture, scheduling rounds, and latent transfer](https://github.com/DiT-Serving/TetriServe/blob/release/v1.0/doc/architecture.md). Its integration with xDiT is acknowledged by the repository; the distinct scheduling implementation is the reason for inclusion.

## Coverage, search process, and limitations

Discovery used live web searches with more than six distinct formulations, followed by repository-page verification and additional primary-source reading for every retained entry. Search angles included general dynamic batching and model servers; continuous batching and prefill/decode scheduling; Rust and Go inference services; JVM and OpenVINO servers; Kubernetes inference controllers; distributed KV caches and cache-aware routing; historical prediction-serving research; heterogeneous accelerator scheduling; and diffusion-transformer serving. Follow-up queries targeted architecture documents, scheduler implementations, model lifecycle semantics, release history, and author-hosted papers. Later searches increasingly returned already covered systems; diffusion-specific searching added a distinct final architecture family.

The resulting coverage spans C++, Python, Rust, Go, Java, and accelerator code; local servers and distributed services; general-purpose frameworks and focused research prototypes. Established systems are complemented by narrower implementations such as TEI's token-aware queue, mistral.rs's admission interface, Nexus, Sarathi-Serve, DistServe, and TetriServe. C4 is deliberately used sparingly: dated compatibility and testing evidence was stronger for MLServer than for many newer systems, and recent commits alone were not treated as evidence of maturity.

Tutorial servers, generated API wrappers, awesome-lists, benchmark-only projects, training schedulers, and kernel libraries without a substantive serving scheduler were excluded. Ordinary forks were not counted independently; Sarathi-Serve's distinct scheduler and disclosed provenance justify its inclusion. Clockwork-related searching did not establish an official substantive GitHub repository confidently enough for inclusion. Related Gateway API routing work is discussed through llm-d-router rather than counted again without an independent implementation review. No third-party mirror is presented as an official project.

This is a selection guide, not an exhaustive inventory or comparative benchmark. Source and documentation inspection establishes the described mechanisms; the judgment that those mechanisms make a repository worth studying is an inference. No candidate code was cloned or executed, no dependencies were installed, and performance or fault-tolerance claims were not independently tested. Some architectural sources describe historical designs, and moving default-branch or “latest” documentation may change after the research date. Archived projects and research prototypes remain useful for study but have materially different maintenance and deployment expectations.
