# Machine learning training frameworks

Research date: **2026-10-09**

This report selects **27 GitHub repositories** for studying the engineering of reusable model training systems: automatic differentiation and execution, training loops, distributed optimization, and native-language neural network frameworks. It includes composable training libraries that deliberately avoid calling themselves frameworks. In large repositories, the relevant training subsystem is identified; related packages within one monorepo are counted once. Historical projects are explicitly marked.

The criteria are engineering judgments grounded in the linked primary material, not assertions that every component is exemplary. Performance mechanisms are described without treating project benchmark claims as independently reproduced results.

- **C1 — Correctness:** difficult numerical, state, concurrency, invariant, or failure-handling requirements.
- **C2 — Abstraction:** substantial reusable interfaces and components serving different models or training workflows.
- **C3 — Performance:** concrete memory, execution, or communication constraints addressed through an understandable architecture.
- **C4 — Evolution:** documented development across years together with compatibility, testing, or complexity management. Age or activity alone does not establish this criterion.

## Core execution and neural network systems

### [pytorch/pytorch](https://github.com/pytorch/pytorch)

**Language/role:** Python, C++, and accelerator code; tensor execution, autograd, neural network modules, and training infrastructure.

Study the boundary between a convenient imperative tensor API and a backward engine that must respect aliasing, saved values, and concurrent execution. The most useful initial subsystem is autograd, rather than attempting to read the entire monorepo.

- **C1:** Saved tensors carry version information; backward checks detect intervening in-place mutation. The documentation also distinguishes concurrent backward execution from safe accumulation into shared gradients, making this a concrete concurrency and numerical-correctness study. [Autograd mechanics](https://docs.pytorch.org/docs/2.14/notes/autograd.html).
- **C2:** The repository separates tensor operations, automatic differentiation, `nn` modules, multiprocessing, and data-loading utilities into reusable layers. Model authors can extend neural components without replacing the differentiation engine. [Repository component overview](https://github.com/pytorch/pytorch).

### [tensorflow/tensorflow](https://github.com/tensorflow/tensorflow)

**Language/role:** C++ and Python; general machine learning runtime and graph-based training system.

Study how eager Python programs become cached executable graphs. The `tf.function` subsystem is especially useful for understanding the semantic costs of making an apparently ordinary function compiled and polymorphic.

- **C1:** Tracing executes Python separately from later graph execution. Mutating a Python object's attributes can leave a cached computation unchanged; dispatch depends on tracing types and function signatures, not simply the apparent Python call. [Function semantics and pitfalls](https://www.tensorflow.org/guide/function).
- **C2/C3:** `PolymorphicFunction`, `ConcreteFunction`, and `Graph` separate dispatch, specialization, and execution. Reusing a compatible graph avoids repeated tracing, while input signatures and tracing rules control the specialization/performance tradeoff. The same [implementation-oriented guide](https://www.tensorflow.org/guide/function) provides worked examples of these boundaries.

### [keras-team/keras](https://github.com/keras-team/keras)

**Language/role:** Python; high-level model construction, optimization, and training across TensorFlow, JAX, and PyTorch backends.

Study how a high-level training API preserves useful customization without making every model backend-specific.

- **C2:** Recursively composed `Layer` objects own state and computation; `Model` adds training and serialization. Using `keras.ops` preserves backend independence, while the documentation explicitly identifies the portability boundary introduced by backend-native operations. [Layer and model architecture](https://keras.io/guides/making_new_layers_and_models_via_subclassing/).
- **C1:** `LossScaleOptimizer` scales and unscales gradients, skips an update on nonfinite gradients, and adjusts its scale dynamically. Its API also distinguishes the iteration counters used by gradient accumulation, exponential moving averages, and learning-rate schedules. These interacting state transitions are more instructive than a basic `fit()` example. [Loss-scale optimizer](https://keras.io/api/optimizers/loss_scale_optimizer/).

### [PaddlePaddle/Paddle](https://github.com/PaddlePaddle/Paddle)

**Language/role:** C++, Python, and accelerator kernels; general deep learning training framework.

Study the connection between tensor mutation semantics and the compiler representation used to optimize training graphs. Relevant areas include autograd and Paddle Intermediate Representation, rather than the surrounding model libraries.

- **C1:** Release documentation describes an in-place-operation redesign that detects backward dependencies on forward inputs and preserves the required values before mutation. This is an explicit response to the risk of silently corrupting gradients.
- **C2/C3:** PIR separates operations, attributes, types, traits, and interfaces, with dialects and an SSA representation. Pattern rewriting and optimization passes give the compiler an extensible structure for improving execution rather than accumulating isolated operator special cases. Both mechanisms are explained in the primary [release notes, including the PIR and in-place sections](https://github.com/PaddlePaddle/Paddle/releases). The substantive notes include Chinese-language material.

### [Oneflow-Inc/oneflow](https://github.com/Oneflow-Inc/oneflow)

**Language/role:** C++ and Python; distributed deep learning execution and training framework.

Study a system designed around distributed data movement from the beginning. Its architecture offers a useful comparison with frameworks that add distribution around a single-device execution model.

- **C1/C3:** The documented actor runtime uses producer/consumer messages, explicit register ownership, and readiness conditions. A storage block becomes reusable only after consumers finish; multiple blocks permit pipelining. Communication and computation are represented together to support overlap. [Versioned system-design document](https://docs.oneflow.org/en/v0.4.0/basics_topics/essentials_of_oneflow.html).
- **C2:** Placement and SBP describe the mapping between logical tensors and physical pieces: split, broadcast, or partial values. This abstraction supports different parallelization strategies without forcing model code to manually express every transfer. The linked design document is historical architectural evidence; [parallel-training documentation](https://docs.oneflow.org/en/master/parallelism/01_introduction.html) supplies the training context.

### [tinygrad/tinygrad](https://github.com/tinygrad/tinygrad)

**Language/role:** Primarily Python; compact tensor, autograd, compiler, and training stack.

Study an end-to-end implementation whose compiler and runtime boundaries are relatively easy to locate. This is substantive training infrastructure, although its API and implementation should not be assumed stable.

- **C2:** The architecture separates a tensor frontend, scheduler, lowering engine, and execution engine. Tensor expressions construct a graph of `UOp` objects, while runtimes encapsulate device allocation and program execution. [Developer architecture](https://docs.tinygrad.org/developer/developer/).
- **C3:** Scheduling partitions the graph into executable kernels; lowering performs optimization and code generation, including a search over kernel implementations. The architecture makes fusion and launch overhead visible study targets. The repository also requires benchmark evidence for speedup contributions and explicitly cautions that code outside the core has weaker testing. [Repository engineering notes](https://github.com/tinygrad/tinygrad).

## Reusable training loops and orchestration

### [Lightning-AI/pytorch-lightning](https://github.com/Lightning-AI/pytorch-lightning)

**Language/role:** Python; PyTorch Lightning's managed training loop and the lower-level Fabric package, counted together.

Study how a framework separates model-specific training logic from optimization and accelerator orchestration while still providing an escape hatch for unusual algorithms.

- **C2:** `LightningModule` describes the training computation and optimizer configuration; the trainer manages execution. Fabric provides a different degree of control within the same repository. [Package and model overview](https://github.com/Lightning-AI/pytorch-lightning).
- **C1:** Automatic optimization builds a closure containing loss computation, gradient clearing, and backward execution. This accommodates optimizers such as LBFGS that reevaluate closures. Manual optimization handles multiple optimizers, while scheduler interval/frequency settings introduce additional ordering requirements. [Repository-hosted optimization design](https://github.com/Lightning-AI/pytorch-lightning/blob/master/docs/source-pytorch/common/optimization.rst).

### [pytorch/ignite](https://github.com/pytorch/ignite)

**Language/role:** Python; event-driven training and evaluation engines for PyTorch.

Study a small central abstraction that can run training, evaluation, or other batch-processing tasks without prescribing a model class.

- **C2:** `Engine(process_function)` exposes shared state and named events; ordinary callables, event filters, custom events, and attached metrics compose behavior around an iteration function. [Engine API and examples](https://docs.pytorch.org/ignite/generated/ignite.engine.engine.Engine.html).
- **C1:** Interruption, termination, resumed data iteration, and restored counters have distinct semantics. The API specifies required checkpoint fields and constrains changes to epoch length during restoration. It also documents an older-behavior compatibility switch for interrupt/resume corner cases. These are concrete state-machine concerns, not merely callback convenience. [Engine run and state semantics](https://docs.pytorch.org/ignite/generated/ignite.engine.engine.Engine.html).

### [fastai/fastai](https://github.com/fastai/fastai)

**Language/role:** Python; layered training library covering vision, text, tabular learning, and recommendation.

Study how the `Learner`, data abstractions, and callbacks let high-level workflows share a customizable core.

- **C2:** Two-way callbacks can inspect and modify learner state at defined points around prediction, loss, backward, and optimizer updates. The documentation even tests and warns about accidentally shadowing learner attributes inside a callback. [Callback architecture and executable examples](https://docs.fast.ai/callback.core.html).
- **C1/C3:** The mixed-precision material explains FP32 master weights, transferring gradients between representations, underflow, overflow, and dynamic loss scaling. It provides utilities for these operations, making numerical preservation under memory and throughput constraints a concrete study path. [Mixed-precision implementation guide](https://docs.fast.ai/callback.fp16.html). Some explanatory hardware examples are historical; no speedup figures are adopted here.

### [mosaicml/composer](https://github.com/mosaicml/composer)

**Language/role:** Python; PyTorch trainer for composable training algorithms and distributed workloads.

Study a trainer organized around explicit model interfaces, shared state, event hooks, and training-time units.

- **C2:** `ComposerModel` separates forward computation from loss; algorithms and callbacks interact with a central `State`. The `Time` abstraction supports durations expressed in epochs, batches, or proportions of a run. [Trainer architecture and usage](https://docs.mosaicml.com/projects/composer/en/stable/trainer/using_the_trainer.html).
- **C1/C3:** The trainer distinguishes a per-device optimization batch from the microbatches used to accumulate its gradients. It coordinates gradient scaling, device movement, and distributed execution; the repository additionally documents FSDP integration and checkpoint restoration with a changed GPU count. [Trainer accumulation semantics](https://docs.mosaicml.com/projects/composer/en/stable/trainer/using_the_trainer.html), [repository scalability overview](https://github.com/mosaicml/composer).

### [huggingface/accelerate](https://github.com/huggingface/accelerate)

**Language/role:** Python; device, precision, and distributed-training coordination for user-owned PyTorch loops.

Study how an adapter can retain an ordinary training loop while jointly preparing models, optimizers, and data loaders.

- **C2:** `Accelerator.prepare`, `backward`, and accumulation contexts provide reusable coordination across execution configurations. The user still supplies the actual training algorithm. [Repository integration example](https://github.com/huggingface/accelerate).
- **C1/C3:** The synchronization guide explains why accumulated microbatches should defer gradient communication, why `no_sync` must include the forward pass, and why avoiding synchronization under FSDP can increase memory consumption. `accumulate` and its plugin settings encode these competing constraints. [Gradient synchronization guide](https://huggingface.co/docs/accelerate/concept_guides/gradient_synchronization).

### [open-mmlab/mmengine](https://github.com/open-mmlab/mmengine)

**Language/role:** Python; common training engine underlying OpenMMLab libraries and usable independently.

Study the infrastructure shared by many algorithm packages: runners, registries, hooks, optimizer wrappers, evaluators, and data elements.

- **C2:** The runner coordinates separate model, dataset, optimizer, scheduler, and evaluation interfaces. Registries can inherit from common roots, while data elements standardize communication across algorithm libraries. [Architecture introduction](https://github.com/open-mmlab/mmengine/blob/main/docs/en/get_started/introduction.md).
- **C1/C3:** `OptimWrapper` and `AmpOptimWrapper` coordinate backward, clipping, gradient clearing, and update frequency. Their optimization context suppresses unnecessary distributed synchronization during accumulation, while retaining lower-level methods for custom update logic. [Optimizer-wrapper design and examples](https://github.com/open-mmlab/mmengine/blob/main/docs/en/tutorials/optim_wrapper.md).

## Distributed training and large-model runtimes

### [deepspeedai/DeepSpeed](https://github.com/deepspeedai/DeepSpeed)

**Language/role:** Python, C++, and accelerator kernels; distributed training engine and memory/communication optimizations.

Study ZeRO's partitioning of optimizer state, gradients, and parameters. The verified current repository is under `deepspeedai`; older Microsoft-owner references are not separate entries.

- **C1:** Configuration validation encodes dependencies between optimization stages and offload modes. Checkpoint restoration distinguishes FP32 master weights from lower-precision copies; gradient-norm settings also have conditions tied to clipping and optimizer behavior. [ZeRO API and configuration contracts](https://deepspeed.readthedocs.io/en/latest/zero3.html).
- **C2/C3:** Staged state partitioning, contiguous gradient buffers, bounded collective buckets, overlap with backward computation, and CPU/NVMe offload expose separable mechanisms for handling GPU-memory limits. The same [ZeRO documentation](https://deepspeed.readthedocs.io/en/latest/zero3.html) explains the architecture and parameter tradeoffs, including the replacement of legacy elastic checkpointing.

### [NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM)

**Language/role:** Primarily Python with compiled acceleration; large-model training and the reusable Megatron Core subsystem.

Study Megatron Core's composition of parallelism dimensions. The repository explicitly distinguishes its reference training scripts from the composable library; these are counted once.

- **C2:** Transformer building blocks and parallelism components are reusable in other training frameworks, rather than being confined to one pretrained model. [Repository subsystem description](https://github.com/NVIDIA/Megatron-LM).
- **C1/C3:** Tensor, pipeline, context, expert, and data parallelism divide different parts of the workload. Virtual pipeline stages address balance; sequence partitioning reduces activation storage, and combining tensor and expert parallelism imposes a documented sequence-parallelism requirement. This offers a clear study of interacting layout constraints and communication costs. [Parallelism architecture guide](https://docs.nvidia.com/megatron-core/developer-guide/latest/user-guide/parallelism-guide.html).

### [hpcaitech/ColossalAI](https://github.com/hpcaitech/ColossalAI)

**Language/role:** Python and accelerator extensions; distributed training transformations and memory management.

Study the Booster/plugin boundary, particularly how it accommodates both external distributed backends and substantive ColossalAI implementations.

- **C2:** Plugins give a common integration surface to DDP, FSDP, low-level ZeRO, Gemini, and hybrid parallel training. The hybrid plugin combines Shardformer, pipeline management, mixed precision, and data-parallel optimizers. [Booster plugin guide](https://colossalai.org/docs/basics/booster_plugins/).
- **C1/C3:** Gemini implements ZeRO-3 with chunk-based heterogeneous memory management. The guide records differences in gradient-accumulation support between plugins, so backend substitution is not semantically unconstrained. This is a useful case study in making performance-specific capabilities and limitations visible through an abstraction. [Plugin capabilities and constraints](https://colossalai.org/docs/basics/booster_plugins/).

### [horovod/horovod](https://github.com/horovod/horovod)

**Language/role:** Python and C++; cross-framework distributed training. **Historical: the repository states that it was archived in September 2026 because of inactivity.**

Study elastic membership and failure recovery around synchronous training; this is an architectural reference, not an assertion of ongoing maintenance.

- **C1:** A worker failure can interrupt a partially applied parameter update. Elastic Horovod restores committed state, performs a new rendezvous, broadcasts from the new worker zero, and resumes. It also forbids premature collectives before the elastic wrapper establishes consistent membership. [Elastic state and recovery protocol](https://horovod.readthedocs.io/en/stable/elastic.html).
- **C2/C3:** The `State` abstraction covers parameters, optimizer state, and progress across supported frameworks. Commit frequency trades copying overhead against replay after failure; graceful membership changes use a different recovery path. [Elastic training guide](https://horovod.readthedocs.io/en/stable/elastic.html).

## JAX model and training abstractions

### [google/flax](https://github.com/google/flax)

**Language/role:** Primarily Python; JAX neural network abstractions, including Linen and NNX in one repository.

Study how mutable object graphs can cross functional compilation and differentiation boundaries without silently losing shared references.

- **C1/C2:** NNX decomposes a module into `GraphDef` and `State`; `split`, `merge`, and `update` move between object and pytree semantics. Variable filters partition differentiable parameters and other state, and must cover all values. [NNX functional architecture](https://flax.readthedocs.io/en/latest/nnx_basics.html).
- **C4:** The repository identifies Linen's 2020 release and NNX's 2024 introduction. The changelog records normalization/attention equivalence tests, JAX compatibility changes, deprecations, and migration work, providing evidence of evolution with complexity management rather than age alone. [Repository chronology](https://github.com/google/flax), [changelog](https://github.com/google/flax/blob/main/CHANGELOG.md).

### [patrick-kidger/equinox](https://github.com/patrick-kidger/equinox)

**Language/role:** Python; composable JAX neural network and scientific-computing library. The project explicitly describes itself as a library rather than a framework.

Study a deliberately small model abstraction: callable objects registered as pytrees, with filtered transformations supplying much of the training machinery.

- **C2:** Models pass through JAX transformations without a separate proprietary model graph. Filtering works at individual pytree leaves, allowing an argument to contain both arrays and static Python values. [Transformation API and design](https://docs.kidger.site/equinox/api/transformations/).
- **C1/C3:** `filter_jit` makes static/dynamic treatment explicit; buffer-donation options allow memory reuse but prohibit later use of donated arrays. Filtered differentiation and compilation therefore have concrete ownership and numerical-selection contracts. The same [transformation reference](https://docs.kidger.site/equinox/api/transformations/) documents those constraints and examples.

### [apple/axlearn](https://github.com/apple/axlearn)

**Language/role:** Python; configurable large-scale training library on JAX/XLA.

Study how object-oriented configuration and hierarchical modules coexist with functional execution and global distributed-array semantics.

- **C2:** `Config`, module hierarchies, and `InvocationContext` separate construction from execution. A functional call supplies parameter state and returns an output collection carrying auxiliary summaries and other values through nested modules. [Core concepts and linked implementation excerpts](https://github.com/apple/axlearn/blob/main/docs/02-concepts.md).
- **C1/C3:** `BaseLayer` parameter specifications include initialization and partitioning; the framework describes computations globally using GSPMD rather than requiring per-accelerator model code. The engineering study is the consistency of state/context propagation together with explicit sharding. [Concepts](https://github.com/apple/axlearn/blob/main/docs/02-concepts.md), [global-computation overview](https://github.com/apple/axlearn). The repository cautions that its API is subject to change.

## Native-language and alternative ecosystem implementations

### [tracel-ai/burn](https://github.com/tracel-ai/burn)

**Language/role:** Rust; tensor execution, autodiff, and model training across multiple backends.

Study device and differentiation context management together with the separation between reusable model code and execution backends.

- **C1:** Device transfer preserves a tensor's differentiation context; device equality alone does not establish autodiff participation. `Module::fork` and `Module::to_device` have different parameter-connection semantics. The documentation also states the first-order-autodiff limitation. [Backend and device contracts](https://burn.dev/books/burn/building-blocks/backend.html).
- **C2/C3:** A shared tensor/model API targets multiple devices; the repository describes operation-stream compilation, kernel fusion, and composable execution capabilities. Explicit `sync`, `flush`, and memory-cleanup operations expose asynchronous execution and allocation concerns. [Backend architecture](https://burn.dev/books/burn/building-blocks/backend.html), [repository overview](https://github.com/tracel-ai/burn).

### [FluxML/Flux.jl](https://github.com/FluxML/Flux.jl)

**Language/role:** Julia; neural network training through native functions, model structures, and differentiation libraries.

Study how little framework-specific machinery is required when parameterized Julia functions can themselves be models.

- **C2:** Training takes an explicit loss, model, data iterator, and optimizer state. `trainstep!` exposes a single update, while automatic-differentiation selection can be supplied separately; custom loops can reuse these pieces. [Training API](https://fluxml.ai/Flux.jl/stable/reference/training/reference/).
- **C1:** Flux checks the mutability assumption required by in-place updates, distinguishes its optimizer setup from the underlying Optimisers package, and stops `train!` on nonfinite loss. These contracts make the ownership of model and optimizer state inspectable. The same [training reference](https://fluxml.ai/Flux.jl/stable/reference/training/reference/) explains conversion of older optimizer types and the boundary between orchestration and optimization.

### [LuxDL/Lux.jl](https://github.com/LuxDL/Lux.jl)

**Language/role:** Julia; explicitly parameterized neural networks and training, including related packages in its monorepo.

Study an alternative to models that hide mutable weights internally: a layer receives input, parameters, and state, then returns output and updated state.

- **C2:** Container layers recursively compose sublayers, and parameter containers are accessed through a defined property interface. This admits both named tuples and other parameter structures while keeping model computation separate. [Lux interface specification](https://lux.csail.mit.edu/stable/manual/interface).
- **C1/C3:** State must remain a named tuple with matching input/output keys; dispatch may use state types for efficient specialized code. The documentation explicitly assigns responsibility for AD compatibility to custom parameter implementations. The repository's training examples also show interchangeable Enzyme/Reactant and Zygote paths. [State and parameter contracts](https://lux.csail.mit.edu/stable/manual/interface), [training examples](https://github.com/LuxDL/Lux.jl).

### [deeplearning4j/deeplearning4j](https://github.com/deeplearning4j/deeplearning4j)

**Language/role:** Java, C++, and related JVM code; DL4J training, ND4J/LibND4J numerical execution, and SameDiff autodiff in one monorepo.

Study the boundary between JVM object lifetimes and native tensor storage. The relevant subsystems are DL4J training and ND4J memory workspaces, rather than every integration package.

- **C2:** Model training, array operations, native kernels, and graph differentiation are separate layers. The repository documents backend-selectable platform testing and custom-layer integration with SameDiff. [Repository subsystem overview](https://github.com/deeplearning4j/deeplearning4j).
- **C1/C3:** Workspaces reuse off-heap memory across cyclic training workloads. Arrays that escape their workspace or survive into a later iteration can reference invalid storage; the guide explains scope checks, detaching, and moving arrays between workspaces. [Versioned ND4J architecture guide, workspace sections](https://deeplearning4j.konduit.ai/en-1.0.0-beta6/nd4j/overview). This older guide supports the architectural analysis, not a claim that every API shown is current.

### [mlpack/mlpack](https://github.com/mlpack/mlpack)

**Language/role:** C++; general machine learning library, retained specifically for its reusable ANN training subsystem.

Study template-based composition of network containers, layers, objectives, initializers, and optimizers. The broader collection of classical estimators is not the reason for inclusion.

- **C2:** `FFN` and `RNN` share `Train`, `Predict`, and layer-composition interfaces. Their objective/gradient interface permits optimization through ensmallen, while template parameters customize loss and initialization. [ANN architecture and training guide](https://www.mlpack.org/doc/tutorials/ann.html).
- **C3:** Armadillo/BLAS and optional OpenMP support provide the execution foundation. The repository discusses BLAS thread oversubscription and the compilation cost of broad template instantiation, including selective headers and opt-in ANN serialization. These are concrete runtime and build-performance constraints around a reusable C++ design. [Performance and compilation notes](https://github.com/mlpack/mlpack).

### [modern-fortran/neural-fortran](https://github.com/modern-fortran/neural-fortran)

**Language/role:** Modern Fortran; native neural network training and inference with data parallelism.

Study a smaller implementation suited to understanding how a scientific-language framework organizes training without a Python runtime.

- **C2:** A network owns an allocatable array of layers. A common layer type manages dataflow and dispatches concrete forward/backward implementations; optimizer objects and activation types are separate extension points. Interfaces live in modules and implementations in submodules. [Code organization and architecture](https://github.com/modern-fortran/neural-fortran/blob/main/CONTRIBUTING.md).
- **C3:** The framework offers parallel execution through coarrays and optional BLAS/MKL acceleration for matrix operations. Its repository distinguishes serial and parallel builds and lists compiler testing, giving a concrete portability/performance study alongside the small object model. [Parallel execution and numerical backend configuration](https://github.com/modern-fortran/neural-fortran).

### [elixir-nx/axon](https://github.com/elixir-nx/axon)

**Language/role:** Elixir; Nx-based neural network construction and event-driven training.

Study a functional training framework in the BEAM ecosystem whose numerical execution is delegated to Nx compilers and backends.

- **C2:** Numerical definitions, model construction, and training loops are separate APIs. A model builds into initialization and prediction functions; loops add metrics, event handlers, monitors, and checkpointable state. [Repository API architecture](https://github.com/elixir-nx/axon), [Axon.Loop reference](https://axon.hexdocs.pm/Axon.Loop.html).
- **C1/C3:** Loop execution can require strict compilation, raising on a compilation-cache miss. Garbage-collection controls expose a memory-versus-throughput tradeoff, and custom step-state containers require an appropriate serialization function to make checkpoints meaningful. [Loop execution and serialization contracts](https://axon.hexdocs.pm/Axon.Loop.html).

## Historical dynamic-graph reference

### [chainer/chainer](https://github.com/chainer/chainer)

**Language/role:** Primarily Python with native components; define-by-run neural network framework. **Maintenance mode:** its README limits further development to bug fixes and maintenance.

Study dynamic differentiation through explicit graph nodes and retained values. It remains useful as a design reference even though it is not presented here as a choice for a new supported deployment.

- **C1:** `FunctionNode.apply` constructs graph edges while computing outputs; backward must accumulate gradients correctly at branches. Inputs/outputs needed by backward must be explicitly retained, and output nodes use weak references. [FunctionNode architecture and contracts](https://docs.chainer.org/en/stable/reference/generated/chainer.FunctionNode.html).
- **C2/C3:** Function implementations separate CPU/GPU forward paths and can compute only requested input gradients. The newer function-node interface supports differentiable backward computation, while old-style functions are represented through wrappers. This is a useful study of extending a reusable AD interface while managing memory and unnecessary computation. [FunctionNode reference](https://docs.chainer.org/en/stable/reference/generated/chainer.FunctionNode.html).

## Search coverage and limitations

Discovery used more than six distinct formulations: general training-framework architecture; JAX functional libraries; Rust/Julia/C++ implementations; event-driven trainers and callbacks; ZeRO, tensor, and pipeline parallelism; Chinese-framework/autograd designs; JVM native-memory management; Fortran/coarray training; Elixir model and loop APIs; and historical or archived framework searches. Follow-up queries tested whether additional distributed/JAX and callback-based projects added a distinct architecture. Later results increasingly repeated covered mechanisms or led to demonstrations, forks, thin integrations, and model-specific training scripts. The extra Fortran and Elixir entries justify extending the usual broad-category range to 27.

Every retained canonical repository page was opened, and every entry includes at least one separately opened substantive primary document beyond the repository landing page. Documentation links also serve as reading entry points. Some sites failed to render: Lightning's optimization material was read in the repository, Paddle's compiler/autograd details in release notes, and DL4J memory architecture in a clearly identified versioned guide. The OneFlow actor design is also explicitly versioned historical material. Branch-based and unversioned documentation links may change after this research date.

The selection emphasizes reusable neural training machinery. It excludes inference-only runtimes, standalone optimizers, cluster provisioning systems, awesome-lists, courses, and single-model demonstrations. General classical-ML estimator libraries were not exhaustively surveyed; mlpack is included for its ANN framework. Additional JAX libraries such as Haiku/Pax and callback ecosystems such as Catalyst/skorch were discovered but not expanded into a second layer of closely overlapping entries. Forks and model-specific adaptations are not counted independently. No selected entry relies on an unofficial GitHub mirror.

Maintenance status is not inferred from stars, repository age, or a recent push. Horovod's archival and Chainer's maintenance notice are stated explicitly; other entries make no blanket promise of current support. This was read-only source/documentation research: no dependencies were installed, repositories cloned, candidate code executed, or benchmarks reproduced. The result is a selection guide and a set of grounded study hypotheses, not a code audit or uniform quality certification.
