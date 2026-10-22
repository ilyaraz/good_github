# Automatic differentiation frameworks

Research date: **2026-10-09**.

This selection covers **27 GitHub repositories** that implement reusable automatic differentiation (AD) machinery: tensor graph engines, compiler transformations, binary instrumentation, operator-overloading libraries, and language-level differentiation systems. Large repositories appear once, with the relevant AD subsystem identified. The emphasis is on implementation study, including numerical semantics, memory ownership, extension interfaces, and computation–storage tradeoffs. Inclusion is not a claim that every component is exemplary or suitable for every workload.

**Criteria legend:** **C1** — difficult correctness involving numerical semantics, invariants, concurrency, or failure modes. **C2** — substantial reusable abstractions supporting multiple use cases. **C3** — real performance constraints addressed through understandable architecture. **C4** — sustained evolution with concrete compatibility, testing, or complexity-management evidence. Criteria below are engineering judgments grounded in the linked primary material; performance rankings are not inferred from project advertising.

## Tensor and array differentiation engines

### 1. [jax-ml/jax](https://github.com/jax-ml/jax)

**Language/role:** Python and C++; composable program transformations for accelerator-oriented numerical computing. Study the AD interpreter and its relationship to tracing, rather than treating JAX as only a neural-network library.

- **C1:** The [AD interpreter](https://github.com/jax-ml/jax/blob/main/jax/_src/interpreters/ad.py) explicitly handles trace tags, symbolic zero tangents, integer-related `float0` tangents, and conversion between primal and tangent representations. These mechanisms make nested differentiation and inactive values a substantial semantic problem.
- **C2 and C3:** The same implementation builds linearized programs through partial evaluation, separates residuals from primal results, prunes residuals already available as inputs or outputs, and caches transformations. Together with the repository's documented composition of differentiation, batching, and JIT compilation, this offers a concrete study of reusable transformations and derivative-memory reduction.

### 2. [pytorch/pytorch](https://github.com/pytorch/pytorch)

**Language/role:** C++ and Python; the relevant subsystem is the dynamic autograd engine under `torch/csrc/autograd`.

- **C1:** The [engine implementation](https://github.com/pytorch/pytorch/blob/main/torch/csrc/autograd/engine.cpp) explains why invoking backward from a backward worker can deadlock. Its reentrant execution scheme, task completion notifications, and thread-local state are unusually instructive concurrency material.
- **C3:** Device-associated ready queues and worker reuse organize backward execution. The same file documents how backward operations recover forward-stream information and synchronize producers, consumers, and the caller's streams. Performance and observable execution semantics are designed together.

This is particularly useful for engineers studying task schedulers whose tasks can recursively invoke the scheduler.

### 3. [tensorflow/tensorflow](https://github.com/tensorflow/tensorflow)

**Language/role:** C++ and Python; scope here is eager-mode gradient recording and backpropagation infrastructure.

- **C1:** The [gradient tape implementation](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/c/eager/tape.h) makes ownership of backward closures and retained activations explicit. Persistent tapes keep those resources for repeated differentiation; ordinary tapes can reclaim them earlier. The class is explicitly documented as not thread-safe.
- **C2:** `GradientTape`, operation entries, tensor identifiers, and the abstract `VSpace` separate graph bookkeeping from gradient aggregation and execution callbacks. This is a reusable architectural boundary across gradient representations.
- **C3:** The [advanced autodiff guide](https://www.tensorflow.org/guide/advanced_autodiff) demonstrates suspending recording to avoid retaining work irrelevant to a derivative. Read it alongside the implementation to connect the public API to memory lifetime.

### 4. [HIPS/autograd](https://github.com/HIPS/autograd)

**Language/role:** Python; a comparatively compact, substantive implementation of differentiation through NumPy-oriented programs.

- **C1:** In the [core implementation](https://github.com/HIPS/autograd/blob/master/autograd/core.py), reverse traversal accumulates contributions from multiple parents, distinguishes mutable and immutable accumulation, handles sparse contributions, and returns appropriately shaped zeros when a result does not depend on an input.
- **C2:** Separate JVP and VJP node classes, primitive-rule registries, and a `VSpace` protocol make the differentiation engine extensible without embedding every numerical type into graph traversal.

Study this repository for a manageable route from mathematical pullbacks to an operational engine. Its size does not eliminate the difficult interaction among sparse gradients, custom primitives, and higher-order differentiation.

### 5. [pymc-devs/pytensor](https://github.com/pymc-devs/pytensor)

**Language/role:** Python with compiled execution backends; static array-expression graphs, differentiation, rewriting, and compilation. The repository identifies itself as a descendant of Aesara and Theano; those ancestors are not counted separately here.

- **C1:** The [gradient driver](https://github.com/pymc-devs/pytensor/blob/main/pytensor/gradient.py) represents disconnected derivatives separately from mathematically undefined and unimplemented derivatives. It also explicitly matches floating-point tangent dtypes to their variables while treating discrete variables differently.
- **C2 and C3:** The repository demonstrates extensible operators and graph transpilation to C, JAX, and Numba, plus rewrites that remove operations or replace them with BLAS calls. The gradient driver builds symbolic pullback/pushforward expressions within that reusable graph system.

The distinguishing study topic is how derivative construction participates in a graph compiler with explicit error semantics.

## Compiler transformations and binary instrumentation

### 6. [EnzymeAD/Enzyme](https://github.com/EnzymeAD/Enzyme)

**Language/role:** C++ and compiler IR; an AD transformation for LLVM and MLIR, usable beneath multiple source languages.

- **C1:** [Activity analysis](https://github.com/EnzymeAD/Enzyme/blob/main/enzyme/Enzyme/ActivityAnalysis.h) distinguishes an instruction that propagates adjoints from a value or pointer that contains derivative information. It combines alias information, type analysis, recursive hypotheses, and re-evaluation dependencies rather than merely marking floating-point operations active.
- **C2 and C3:** Differentiation at shared compiler-IR layers makes the machinery reusable across language frontends. The repository describes differentiating optimized code, while activity analysis supplies a concrete mechanism for avoiding derivative work that cannot affect the result.

Study the boundary between general compiler analyses and AD-specific analyses. Language bindings are not counted as separate implementations in this report.

### 7. [vgvassilev/clad](https://github.com/vgvassilev/clad)

**Language/role:** C++; Clang plugin that generates derivative C++ through AST transformation.

- **C1:** The [reverse-mode visitor](https://github.com/vgvassilev/clad/blob/master/lib/Differentiator/ReverseModeVisitor.cpp) manages nested loop scopes, saved primal values, and AST-node ownership. Its comments explain why reused references must be cloned so generated calls own their AST expressions.
- **C2 and C3:** The repository exposes differentiation, gradient, Jacobian, and Hessian APIs around generated callable functions. The visitor chooses between local array slots and heap-growing tapes based on loop bounds, value types, and storage size, making storage decisions visible in generated-code construction.

**Caveat:** The repository documents a numerical-differentiation fallback when algorithmic differentiation fails, and warns about differentiating integer-like types and lossy casts. These are significant semantics to examine, not interchangeable AD guarantees.

### 8. [mitsuba-renderer/drjit](https://github.com/mitsuba-renderer/drjit)

**Language/role:** C++ and Python; tracing JIT and AD system developed for differentiable rendering and other parallel numerical programs.

- **C1:** The [differentiation documentation](https://github.com/mitsuba-renderer/drjit/blob/master/docs/autodiff.rst) specifies separate correctness conditions for sum loops and general reverse-mode loops. General loops require a valid iteration bound; exceeding it can produce incorrect gradients in release builds.
- **C3:** Sum loops can avoid storing a trajectory, whereas general loops record state and reconstruct a per-iteration subgraph during reverse replay. The surrounding system fuses traced arithmetic into accelerator or CPU kernels, addressing workloads with many small operations.

Dr.Jit explicitly identifies itself as an all-new implementation succeeding Enoki. Enoki is omitted to avoid presenting an older lineage member as another current choice without a separate historical study.

### 9. [SciCompKL/derivgrind](https://github.com/SciCompKL/derivgrind)

**Language/role:** C/C++ with supporting Python; a substantive AD extension built into a Valgrind source tree. The relevant subsystem is `derivgrind/`, not the inherited Valgrind tools.

- **C1:** Machine instructions can encode real arithmetic through bit operations. The repository documents this limitation, and the [expression instrumentation](https://github.com/SciCompKL/derivgrind/blob/derivgrind/derivgrind/dg_expressionhandling.c) handles VEX operations, guarded loads, conditionals, and warnings/default handling for unsupported expressions.
- **C2:** A common expression-handling interface supports forward differentiation and tape-recording modes. Input/output annotations can surround compiled library calls, enabling differentiation across source-language boundaries.

This is valuable for studying AD below source code. The repository limits support to x86/AMD64 Linux and documents substantial runtime overhead and incomplete instruction/bit-manipulation coverage; it is not presented as a general high-throughput replacement for source-level AD.

## C++ numerical libraries and scientific computing

### 10. [coin-or/CppAD](https://github.com/coin-or/CppAD)

**Language/role:** C++; recording and replaying differentiated algorithms through `AD` values and `ADFun` objects.

- **C1:** The [tape optimizer and its embedded documentation](https://github.com/coin-or/CppAD/blob/main/include/cppad/core/optimize.hpp) describe conditional skipping, comparison-change information, atomic-function dependency analysis, and treatment of unused atomic inputs as NaNs. Debug configurations can compare function results before and after optimization.
- **C3:** The optimizer reduces operation count and tape memory while exposing tradeoffs such as hash-collision limits, optimization cost, and repeated tape reuse. It also explains why recording an initial evaluation that optimization will invalidate wastes work.

This is a strong study target for semantics-preserving optimization of an AD-specific intermediate representation, with examples of precisely where user-defined operations complicate the optimizer.

### 11. [coin-or/ADOL-C](https://github.com/coin-or/ADOL-C)

**Language/role:** C/C++; operator-overloading AD with recorded tapes, derivative drivers, sparse support, and parallel integration options.

- **C1:** The repository documents that constructing or destroying active values under the wrong selected tape can cause memory corruption. The [tape interface](https://github.com/coin-or/ADOL-C/blob/master/ADOL-C/src/tape_interface.cpp) explicitly brackets recording state, restores it on exceptions, and rejects stopping a tape that is not recording.
- **C2 and C3:** The same interface separates operation, location, value, and Taylor storage and exposes buffer configuration and tape statistics. Reusable tape identities support multiple differentiated functions; optional sparse and parallel facilities broaden the use cases.

**Status caveat:** The repository explicitly marks `master` unstable during modernization and directs users to a release. The entry concerns architecture and invariants, not a recommendation to deploy the default branch.

### 12. [rjhogan/Adept-2](https://github.com/rjhogan/Adept-2)

**Language/role:** C++; integrated array expressions, automatic differentiation, and optimization utilities. This is the Adept 2 repository, not the older scalar-only Adept repository.

- **C1:** The [stack implementation](https://github.com/rjhogan/Adept-2/blob/master/include/adept/Stack.h) exposes active-stack selection, thread-local versus explicitly unsafe global access, gradient registration, and checks when appending operations to an existing statement.
- **C2 and C3:** A common expression-template framework covers differentiable scalar and array calculations. The stack separates storage implementations and records derivative information for adjoint, tangent-linear, and Jacobian operations; it also tracks whether callers were compiled with OpenMP support.

Engineers can study how a numerical array API and an AD tape share expression machinery while maintaining explicit stack-lifetime requirements.

### 13. [SciCompKL/CoDiPack](https://github.com/SciCompKL/CoDiPack)

**Language/role:** C++; expression-template AD with several tape and identifier-management strategies.

- **C2:** The [tape interface design](https://github.com/SciCompKL/CoDiPack/blob/master/documentation/developer/TapeInterfaces.md) divides the full interface into basic recording/gradient capabilities and optional interfaces for external functions, partial evaluation, custom adjoints, and data management. A new tape can implement a useful subset.
- **C3:** Jacobian versus primal-value tapes and linear versus reused identifiers offer different storage costs. The repository also explains preaccumulation and external-function helpers for reducing recording overhead.
- **C4:** The [changelog](https://github.com/SciCompKL/CoDiPack/blob/master/documentation/Changelog.md) records evolution from 2019 through 2026: higher-order test expansion, a major tape rewrite with migration guidance, memory-corruption fixes, parallel support, and an explicit C++17 transition retaining the older release line for C++11 users.

### 14. [autodiff/autodiff](https://github.com/autodiff/autodiff)

**Language/role:** C++17; forward-mode dual numbers and reverse-mode expression trees behind concise numerical APIs.

- **C1:** The [reverse variable implementation](https://github.com/autodiff/autodiff/blob/main/autodiff/reverse/var/var.hpp) contains both numeric derivative propagation and propagation of derivative expressions for higher-order use. Rules such as absolute value explicitly choose behavior at the nondifferentiable point, while dependent variables must update cached primal values and accumulate derivative contributions correctly.
- **C2:** A hierarchy of constant, independent-variable, dependent-variable, unary, binary, and ternary nodes provides reusable expression machinery. The repository's `wrt`/`at` API and dual/variable types expose different differentiation modes without requiring callers to manage this hierarchy.

Study the distinction between evaluating a derivative and constructing a differentiable expression for that derivative.

### 15. [auto-differentiation/xad](https://github.com/auto-differentiation/xad)

**Language/role:** C++; forward and reverse operator-overloading AD with higher-order nesting and checkpoint facilities.

- **C1:** The [tape reference](https://github.com/auto-differentiation/xad/blob/main/docs/ref/tape.md) specifies a moveable but noncopyable tape, one active tape per thread, exceptions for conflicting activation or uninitialized derivatives, and a strong exception guarantee for adjoint evaluation.
- **C2 and C3:** Scalar type parameterization allows nested active types. Tape positions, partial reverse evaluation, derivative clearing, and checkpoint callbacks expose reusable controls for the storage/recomputation tradeoff.

The useful study material is the unusually explicit tape contract. The repository's optional JIT interface is distinct from its commercially licensed code-generation backend; no headline speed comparison is adopted here.

### 16. [stan-dev/math](https://github.com/stan-dev/math)

**Language/role:** C++; differentiable numerical and probability functions. Scope is the Math library's AD core, not the Stan language compiler.

- **C1:** [Autodiff stack storage](https://github.com/stan-dev/math/blob/develop/stan/math/rev/core/autodiffstackstorage.hpp) documents the static-initialization-order hazard, ownership of the first stack instance, initialization requirements for child threads, and nested differentiation positions.
- **C3:** The source explains why the optional thread-local stack is represented by a constant-initialized pointer: avoiding dynamic TLS wrapper overhead matters on the AD hot path. Arena allocation and separate chainable/non-chainable stacks make resource management concrete.

This is especially useful for understanding how pervasive numerical operators depend on a small global-or-thread-local runtime, and the lifecycle constraints that design imposes.

### 17. [casadi/casadi](https://github.com/casadi/casadi)

**Language/role:** C++ core with multiple language interfaces; sparse expression graphs and AD for numerical optimization and optimal control.

- **C2:** The [official guide](https://web.casadi.org/docs/) explains scalar-expression `SX`, matrix-expression `MX`, sparsity objects, and reusable function objects that can embed solvers and differentiable computations. Existing models generally need to be expressed in CasADi's representation.
- **C3:** Its AD section explains sparse Jacobian construction through sparsity discovery, graph coloring, directional derivative evaluation, and assembly; Hessian construction additionally exploits symmetry. Jacobian-vector products avoid constructing a complete Jacobian when only its action is needed.

For implementation study, [function internals](https://github.com/casadi/casadi/blob/main/casadi/core/function_internal.hpp) show the shared function lifecycle, per-evaluation memory objects, and code-generation interfaces behind those abstractions.

### 18. [trilinos/Trilinos](https://github.com/trilinos/Trilinos)

**Language/role:** C++; this monorepo entry covers **Sacado**, under `packages/sacado`, rather than all Trilinos solvers.

- **C2:** Sacado's [project documentation](https://trilinos.github.io/sacado.html) explains scalar-type templating and expression templates for extracting derivatives from scientific application code, including finite-element assembly.
- **C1 and C3:** The [hierarchical parallelism design](https://github.com/trilinos/Trilinos/blob/develop/packages/sacado/README_HIERARCHICAL_PARALLELISM.md) maps derivative components onto Kokkos vector lanes. Contiguous storage, strided derivative views, and thread-local scalar types must agree; it documents different GPU-backend requirements and rejects configurations that would silently compute incorrect derivatives.

This is a distinctive study of AD data layout and parallel execution, where the derivative dimension itself becomes a hardware-parallel dimension.

## Julia differentiation systems

### 19. [JuliaDiff/ForwardDiff.jl](https://github.com/JuliaDiff/ForwardDiff.jl)

**Language/role:** Julia; forward-mode AD using generic dual-number arithmetic.

- **C1:** The [implementation explanation](https://github.com/JuliaDiff/ForwardDiff.jl/blob/master/docs/src/dev/how_it_works.md) describes tags that prevent perturbation confusion and nested dual values for higher derivatives. The repository also documents a dual-number equality change made to avoid incorrect derivatives when programs inspect structural zeros.
- **C2 and C3:** Public derivative, gradient, Jacobian, and Hessian APIs seed and extract these values. The [advanced guide](https://github.com/JuliaDiff/ForwardDiff.jl/blob/master/docs/src/user/advanced.md) explains chunk-size tradeoffs, preallocated results, type stability, and optional NaN-safe propagation.

This is a clear study of how seemingly small numeric-type choices affect both correctness and compilation/performance behavior.

### 20. [JuliaDiff/ReverseDiff.jl](https://github.com/JuliaDiff/ReverseDiff.jl)

**Language/role:** Julia; trace-based reverse AD with reusable and compilable tapes.

- **C1:** The [API guide](https://github.com/JuliaDiff/ReverseDiff.jl/blob/master/docs/src/api.md) explicitly warns that a replayed tape follows only the path executed during recording. Input-dependent branches are not reevaluated, so matching shape and element type alone does not establish safe reuse.
- **C2 and C3:** Separate configurations, gradient/Jacobian tapes, compilation, and in-place result APIs let callers independently avoid buffer allocation and trace reconstruction. The API documents the upfront compilation cost versus repeated evaluation benefit.

The [limitations guide](https://github.com/JuliaDiff/ReverseDiff.jl/blob/master/docs/src/limits.md) adds restrictions on foreign calls, tracked-array mutation, and nested differentiation of closures. These constraints make the repository useful for studying precisely what a reusable execution trace guarantees.

### 21. [FluxML/Zygote.jl](https://github.com/FluxML/Zygote.jl)

**Language/role:** Julia; source-to-source differentiation integrated with Julia's lowered representation and compiler.

- **C1:** The [internals guide](https://github.com/FluxML/Zygote.jl/blob/master/docs/src/internals.md) derives reverse loops, closure-captured gradients, and pullback state. Reversing statements alone is insufficient: intermediate values and contributions to captured function data must survive.
- **C2:** Generated functions construct pullbacks on demand; lowered code is transformed through SSA and converted back into runnable IR. The repository also supports custom rules through ChainRules and differentiation of nested model parameter structures.

This makes closure conversion and compiler-generated derivative programs unusually accessible. The repository documents limitations around mutation and exception handling; those boundaries matter when evaluating applicability to numerical programs with mutable state.

### 22. [chalk-lab/Mooncake.jl](https://github.com/chalk-lab/Mooncake.jl)

**Language/role:** Julia; differentiation of inferred, optimized Julia IR, including support for mutation.

- **C1:** The [reverse-mode design](https://github.com/chalk-lab/Mooncake.jl/blob/main/docs/src/developer_documentation/reverse_mode_design.md) explains how a pullback reconstructs predecessor edges, routes phi-node contributions, records dynamic control-flow information, and transports communication values between passes.
- **C2 and C3:** A builder-local control-flow graph separates AD assembly from the compiler's concrete IR numbering. Per-statement forward/reverse fragments are assembled, lowered back to compiler IR, optimized, and wrapped in closures. The public API uses reusable caches tied to input types and sizes.

Study this as a more explicit control-flow construction architecture alongside Zygote and ReverseDiff. No multi-year maturity criterion is inferred merely from its compiler integration or tests.

## Other language communities and numerical abstractions

### 23. [DiffSharp/DiffSharp](https://github.com/DiffSharp/DiffSharp)

**Language/role:** F#/.NET; differentiable tensor programming with backend-separated numerical storage.

- **C1:** The [tensor implementation](https://github.com/DiffSharp/DiffSharp/blob/dev/src/DiffSharp.Core/Tensor.fs) represents constant, forward-active, and reverse-active values separately. Nesting tags, reverse fanout counts, and explicit rejection of casts or device/backend moves during differentiation expose important invariants.
- **C2:** Recursive tensor representations allow derivative values themselves to be tensors with derivative state. The `RawTensor` boundary separates these AD semantics from numerical backends, supporting mixed-mode and nested differentiation.

**Status caveat:** The default `dev` branch identifies itself as development for DiffSharp 1.0 and warns of incomplete functionality and changing design. It is retained as a substantive implementation study, not characterized as a stable current release.

### 24. [ekmett/ad](https://github.com/ekmett/ad)

**Language/role:** Haskell; forward, reverse, sparse, and higher-order differentiation combinators.

- **C1:** The repository explains how mode abstraction and universal quantification prevent accidental mixing of infinitesimals. The [public implementation](https://github.com/ekmett/ad/blob/master/src/Numeric/AD.hs) exposes those constraints in rank-polymorphic signatures rather than relying solely on runtime discipline.
- **C2 and C3:** Combinators work over `Traversable` structures and compose modes. Hessian-vector products use forward-on-reverse differentiation, while Hessians use sparse-on-reverse composition, showing how to reuse lower-level operators without always constructing larger derivative objects.

This is a valuable counterpart to mutable tapes: study how type-level scoping, generic containers, and higher-order functions organize the same underlying calculus.

### 25. [tracel-ai/burn](https://github.com/tracel-ai/burn)

**Language/role:** Rust; scope is the `burn-autodiff` crate inside the tensor/deep-learning monorepo.

- **C2:** The [AD backend](https://github.com/tracel-ai/burn/blob/main/crates/burn-autodiff/src/backend.rs) is a decorator over a generic numerical backend. It wraps differentiable floating tensors while forwarding other tensor types and execution services to the underlying backend.
- **C1 and C3:** The [checkpoint strategy implementation](https://github.com/tracel-ai/burn/blob/main/crates/burn-autodiff/src/checkpoint/strategy.rs) distinguishes compute-bound and memory-bound operations and stores recomputation procedures accordingly. It detects untracked parents and resets incomplete checkpoint construction rather than pretending the required history exists.

The backend also explicitly disables graph capture under AD because replay would omit tape recording. This is a concrete example of checking interactions between individually useful execution features.

### 26. [itt-ustutt/num-dual](https://github.com/itt-ustutt/num-dual)

**Language/role:** Rust with Python bindings; generalized scalar/vector dual and hyper-dual numbers, including implicit differentiation.

- **C1:** The [implicit derivative implementation](https://github.com/itt-ustutt/num-dual/blob/master/src/implicit.rs) computes derivative corrections using scalar derivatives or Jacobian linear solves and includes analytic-result checks in examples. Its API requires an already obtained primal solution; these routines do not replace a nonlinear solver, and singular derivative systems remain a relevant failure boundary.
- **C2 and C3:** The [crate-level design and API](https://github.com/itt-ustutt/num-dual/blob/master/src/lib.rs) supports nested dual types, fallible/container-valued outputs, and generic parameter structures. It explicitly discusses heap-allocation costs of dynamic derivative dimensions and provides the `Gradients` abstraction to address static/dynamic dimension tradeoffs.

This adds scientific numerical AD coverage beyond Rust's tensor-training frameworks.

### 27. [gorgonia/gorgonia](https://github.com/gorgonia/gorgonia)

**Language/role:** Go; reusable tensor-expression graphs and differentiation infrastructure.

- **C1:** The [differentiation implementation](https://github.com/gorgonia/gorgonia/blob/master/differentiation.go) checks graph membership, analyzes differentiable reachability in both directions, reports invalid differentiation targets, and accumulates multiple gradient terms in reverse topological traversal.
- **C2:** Operator-specific differentiation is accessed through interfaces such as `SDOp`, while graph analysis and `Backpropagate` orchestrate reusable tensor expressions. Symbolic derivative construction prepares the graph for numerical AD execution rather than being a standalone computer-algebra simplifier.

Study the interaction between graph validation, operator capability discovery, and derivative construction in Go. The repository's distributed-computing aspirations are not treated as implemented capabilities, and no active-maintenance claim is made here.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations, covering LLVM/Clang compilers; C++ tape, sparse, and expression-template libraries; Julia language-level AD; Python tensor-engine internals; Rust/Go/Haskell/F# implementations; differentiable rendering; finite-element/HPC integration; implicit differentiation; and checkpointing/binary instrumentation. Later queries increasingly returned already represented projects, thin bindings, tutorials, application-specific models, or speculative projects. The two late substantive additions—num-dual and Derivgrind—justify extending the list slightly beyond the initial 15–25 guide.

Each retained canonical GitHub repository page was opened successfully. Each entry also has an independently read implementation or substantive design/API source beyond its root README; raw source retrieval was used where browser views were noisy. GitHub's unauthenticated API was rate-limited, so canonical URLs, branches, and archive notices were checked through public repository pages instead. No retained page displayed an archive notice at inspection time; this is not a claim of ongoing maintenance. Links to default branches and hosted documentation are mutable snapshots, not pinned release audits.

The selection excludes tutorial engines such as micrograd-style exercises, benchmark/awesome-list repositories, pure wrappers around an already counted engine, and application packages that merely call another project's AD API. PyTensor represents the Theano/Aesara lineage here; Adept 2 represents Adept; Dr.Jit represents the separately implemented successor to Enoki. Derivgrind is retained despite its inherited Valgrind tree because it adds a substantive, distinct AD implementation. No unofficial mirror is substituted for a project's canonical repository.

Coverage favors publicly accessible English documentation and implementations whose architecture could be examined directly. It is not exhaustive across every Fortran transformation tool, experimental reversible language, Java/OCaml library, or proprietary AD product. Source inspection was read-only: no dependencies were installed, candidate code executed, large repositories cloned, or performance claims benchmarked. C4 is credited only where a release history actually demonstrated sustained changes and compatibility/testing work; longevity, stars, and recent pushes alone were not used as evidence.
