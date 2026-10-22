# Probabilistic programming systems

Research date: **2026-10-09**.

This report selects 24 GitHub repositories implementing probabilistic modeling languages, their execution systems, or integrated model-and-inference frameworks. It covers continuous and discrete inference, dynamic traces, tensor computation, message passing, compiler construction, symbolic conditioning, and probabilistic logic. The emphasis is what an experienced engineer can learn from the implementation. Inclusion is not a claim that every component is exemplary, that inference is exact, or that a project is currently maintained.

**Criteria legend:** **C1** — difficult correctness involving numerical semantics, invariants, concurrency, or failure modes. **C2** — substantial reusable abstractions supporting different models or inference methods. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — sustained evolution with evidence of compatibility, testing, or complexity management. Each entry explains at least two criteria; architectural assessments are grounded engineering judgments, not independent correctness proofs.

## General-purpose statistical and tensor systems

### 1. [stan-dev/stan](https://github.com/stan-dev/stan)

**C++ — Stan's inference algorithms and services.** Study the boundary between a differentiable model and reusable numerical inference. This entry concerns the core Stan repository; the separate language compiler, math library, and language bindings are not counted again.

- **C1:** The [NUTS implementation](https://github.com/stan-dev/stan/blob/develop/src/stan/mcmc/hmc/nuts/base_nuts.hpp) combines recursive trajectory construction, multiple no-U-turn checks, log-space weight accumulation, NaN handling, and divergence detection. These are correctness-sensitive parts of sampling, rather than ordinary numerical plumbing.
- **C2:** The same implementation parameterizes the model, Hamiltonian, integrator, and random-number generator, exposing useful boundaries for studying algorithm reuse.
- **C4:** The [release history](https://github.com/stan-dev/stan/blob/develop/RELEASE-NOTES.txt) spans many years and records integration-test refactoring, Eigen compatibility, numerical bug fixes, and a PRNG change explicitly warning that old seeds produce different results. This is concrete evolution evidence beyond repository age.

### 2. [pymc-devs/pymc](https://github.com/pymc-devs/pymc)

**Python — probabilistic model graphs and Bayesian inference.** Particularly useful for studying how a friendly modeling API connects to graph transformations and several inference engines.

- **C1:** The [log-probability transform implementation](https://github.com/pymc-devs/pymc/blob/main/pymc/logprob/transforms.py) reconstructs densities through inverse transformations, applies Jacobian corrections, and handles invalid transformed domains. Its separate log-CDF and inverse-CDF paths expose additional discrete-versus-continuous subtleties.
- **C2:** The [architecture guide](https://github.com/pymc-devs/pymc/blob/main/ARCHITECTURE.md) separates model construction, distributions, sampling orchestration, and step methods, while assigning low-level graphs and differentiation to PyTensor. MCMC, variational inference, and SMC share the modeling infrastructure. Treat this guide as a map; individual module names can evolve.

### 3. [pyro-ppl/pyro](https://github.com/pyro-ppl/pyro)

**Python/PyTorch — dynamic probabilistic programs with effect handlers.** Study how ordinary Python model execution becomes inspectable and transformable without embedding inference logic in each model.

- **C1:** The [Poutine implementation guide](https://pyro.ai/examples/effect_handlers.html) explains two-direction handler-stack traversal and why log probabilities must sometimes be calculated after other handlers have modified a sample site. Observation flags, handler order, and cleanup are semantic invariants.
- **C2:** Tracing, conditioning, replay, and other behaviors compose through the `Messenger` protocol. The guide builds a log-joint evaluator from these pieces and explains the shared message representation used throughout inference. This is a substantial example of separating model syntax from its interpretation.

### 4. [pyro-ppl/numpyro](https://github.com/pyro-ppl/numpyro)

**Python/JAX — probabilistic programming with functional randomness and compiled inference.** A separate implementation worth comparing with Pyro because JAX transformations impose different execution constraints.

- **C1:** The [effect-handler guide](https://num.pyro.ai/en/latest/tutorials/effect_handlers.html) demonstrates that nesting `condition` and `substitute` in opposite orders changes values while preserving different observation semantics. It also shows explicit PRNG-key splitting and reparameterization of a difficult posterior geometry.
- **C2:** Named sample sites, distribution objects, and composable handlers support inspection, conditioning, reparameterization, and posterior prediction through a shared interface.
- **C3:** The repository describes a JAX-backed implementation using automatic differentiation and JIT compilation across CPU/GPU/TPU targets. Study the interaction between that execution model and the handler abstraction; no cross-project speed ranking is asserted here.

### 5. [tensorflow/probability](https://github.com/tensorflow/probability)

**Python — distributions, joint-model construction, transforms, and inference kernels.** The relevant subsystem is TensorFlow Probability's model-building and inference stack, including its JAX substrate, rather than TensorFlow generally.

- **C1:** The [PRNG design document](https://github.com/tensorflow/probability/blob/main/PRNGS.md) explains how eager execution, graph execution, and functional seeds differ, and how seed sanitization and splitting mediate these differences. Reproducibility depends on execution semantics, not merely accepting an integer seed.
- **C2:** The repository's documented layers separate distributions and bijectors from joint distributions, probabilistic neural-network layers, and customizable MCMC kernels. These abstractions support both explicit probabilistic models and uncertainty-aware neural models.

The PRNG document is explicitly dated 2020: use it to understand the design transition, not as an unconditional statement about every current TensorFlow backend.

### 6. [TuringLang/Turing.jl](https://github.com/TuringLang/Turing.jl)

**Julia — general-purpose modeling and compositional inference.** Study integration across a scientific-language ecosystem: models, interchangeable differentiation backends, and inference algorithms. DynamicPPL and other dependencies are acknowledged components, not additional entries here.

- **C1:** The [automatic-differentiation guide](https://turinglang.org/docs/usage/automatic-differentiation/) documents a concrete silent-error hazard: a pre-recorded ReverseDiff tape is unsafe when a model's sequence of operations changes between executions. It also distinguishes more extensively tested backends from merely available ones.
- **C2:** A common gradient interface supports HMC, variational inference, and other consumers; Gibbs sampling can combine different AD modes for different variable blocks.
- **C3:** One-time gradient preparation amortizes setup costs, and the guide provides a way to benchmark backend choices for a particular model. The lesson is configurable numerical infrastructure with explicit validity constraints.

## Programmable traces, transformations, and streaming inference

### 7. [probcomp/Gen.jl](https://github.com/probcomp/Gen.jl)

**Julia — programmable inference through generative functions and execution traces.** One of the clearest systems for studying an explicit contract between modeling languages and inference code.

- **C1:** The [generative-function interface](https://www.gen.dev/docs/stable/ref/core/gfi/) specifies address uniqueness, proposal-support requirements, trace weights, and what happens to discarded choices when control flow changes. These details determine whether trace modification yields valid inference.
- **C2:** Generative functions represent models, proposals, and variational approximations through a common interface; custom implementations can participate in larger models.
- **C3:** Argument and return-value change hints enable incremental computation. The documentation explicitly says incorrect hints may cause incorrect behavior because Gen generally does not verify them. This makes the performance/correctness tradeoff unusually visible.

### 8. [ReactiveBayes/RxInfer.jl](https://github.com/ReactiveBayes/RxInfer.jl)

**Julia — factor-graph modeling and reactive message-passing inference.** Study the orchestration layer connecting model specification, approximation constraints, and the ReactiveMP engine.

- **C2:** The [message-passing architecture](https://docs.rxinfer.com/stable/concepts/message-passing/) selects update rules using node type, outgoing edge, incoming distribution families, and factorization assumptions. Custom rules extend this interface rather than requiring a separate inference engine.
- **C3:** Nodes expose reactive message streams, so changed observations trigger dependent updates instead of requiring a precomputed global schedule. This supports streaming model execution through local dependency structure.
- **C1:** The [missing-rule guide](https://docs.rxinfer.com/stable/manuals/sharpbits/rule-not-found/) explains that apparently simple models can lack the necessary closed-form updates. Available rules and chosen approximations constrain inference; a factor-graph frontend does not make every model automatically tractable.

### 9. [pyprob/pyprob](https://github.com/pyprob/pyprob)

**Python/PyTorch — inference around existing simulators.** The repository calls itself a research prototype. Its distinctive scope is connecting simulator execution to inference, including the PPX interface across languages, processes, and machines.

- **C1:** The [execution-state implementation](https://raw.githubusercontent.com/pyprob/pyprob/master/pyprob/state.py) derives sample-site addresses from execution frames or explicit addresses, tracks repeated instances, and records observation log probabilities and importance weights. Stable correspondence between random choices across executions is central to the inference machinery.
- **C2:** A common trace/model interface supports importance sampling, Metropolis–Hastings variants, and learned proposal networks for inference compilation. This offers a reusable architecture for simulator-backed models rather than a single application.

The inspected state module contains process-global state and interpreter-sensitive address extraction; it should not be read as evidence of unrestricted thread safety or modern-Python compatibility.

### 10. [cscherrer/Soss.jl](https://github.com/cscherrer/Soss.jl)

**Julia — probabilistic programming through source rewriting.** Study models as manipulable syntax, especially the distinction between a generative program and transformations of its dependency structure. The inspected stable documentation was generated in 2022; current maintenance is not established by that documentation.

- **C2:** The [internals guide](https://cscherrer.github.io/Soss.jl/stable/internals/) describes translating model statements into `Assign` and `Sample` representations, with distributions collected into the model representation.
- **C1:** The [transformation API](https://cscherrer.github.io/Soss.jl/stable/api/) gives precise ancestor/descendant rules for `before`, `after`, `prior`, `predictive`, and `prune`. `Do` changes which quantities are arguments without making the same dependency cut as prediction. Preserving these distinctions is essential to the resulting probabilistic semantics.

### 11. [probmods/webppl](https://github.com/probmods/webppl)

**JavaScript — a probabilistic language for browsers and Node.js.** A useful, comparatively approachable compiler/runtime study, especially for readers interested in continuations and higher-order languages.

- **C1:** The [language specification](https://webppl.readthedocs.io/en/master/language.html) requires host JavaScript functions to be deterministic and free of cross-call state, and limits higher-order interoperability. These restrictions protect the meaning of repeated or suspended probabilistic executions.
- **C2:** A functional JavaScript subset supports recursive and higher-order models, while continuation-passing-style transformation gives inference algorithms such as enumeration and SMC control over execution.

The linked documentation identifies itself as version 0.9.13. This entry is a language-design study, not a claim of recent release activity or full JavaScript compatibility.

### 12. [probprog/anglican](https://github.com/probprog/anglican)

**Clojure — a probabilistic language with CPS compilation and multiple inference backends.** Retained as a substantive research-system codebase, including source and tests. Its public language documentation also contains links from the project's older Bitbucket era.

- **C1:** The [language guide](https://probprog.github.io/anglican/language/) distinguishes ordinary Clojure functions from CPS-transformed Anglican functions, explains per-execution state, and defines `observe` as a log-weight update. Interoperability mistakes can appear as arity errors; the boundary is part of the language semantics.
- **C2:** The [source map](https://github.com/probprog/anglican/blob/master/doc/codemap.md) separates runtime and particle state from CPS transformations and numerous algorithms, including particle Gibbs, interacting particle MCMC, and asynchronous particle cascades. It is a useful map for comparing inference strategies over a shared execution substrate.

## Compiled, staged, and object-based systems

### 13. [nimble-dev/nimble](https://github.com/nimble-dev/nimble)

**R and C++ — BUGS-style models, programmable algorithms, and compilation.** Study specialization of inference code to model structure, rather than treating the model as an opaque density callback.

- **C2:** The [nimbleFunction programming chapter](https://r-nimble.org/manual/cha-progr-with-models.html) separates R setup code, which inspects model dependencies, from restricted run code that can be compiled. Nested functions and lists of samplers support reusable model-aware algorithms.
- **C1:** The same chapter documents topological node ordering, persistent state, and scalar/vector distinctions required for correct model calculation and compilation.
- **C4:** The [change history](https://github.com/nimble-dev/nimble/blob/devel/packages/nimble/inst/NEWS.md) records releases across 2018–2026, fixes to invalid sampling and non-finite weights, testing-infrastructure corrections, and C++20 compatibility changes. These provide unusually concrete evidence of long-term numerical and compiler maintenance.

### 14. [dotnet/infer](https://github.com/dotnet/infer)

**C# — Infer.NET's probabilistic model compiler and message-passing runtime.** The monorepo contains compiler, runtime, tests, and applications; the compiler/runtime are the relevant study target.

- **C1:** The [compiler-transform map](https://dotnet.github.io/infer/development/Compiler%20transforms.html) makes difficult invariants explicit: stochastic branches become gates, variable references become graph channels, and cyclic dependencies require iteration and scheduling passes.
- **C2:** Model descriptions are lowered into generated inference code through separate transformations. Hybrid-algorithm boundaries translate between message representations, illustrating reusable infrastructure for more than one inference strategy.
- **C3:** Message deduplication, pruning, dead-code elimination, and loop merging are identifiable optimization stages. The pipeline lets an engineer inspect how computational savings relate to dependency analysis.

### 15. [stripe/rainier](https://github.com/stripe/rainier)

**Scala — functional Bayesian modeling and JVM numerical compilation.** A useful contrast with both native-code and tensor-backend PPLs. Its documented workload assumes fixed model structure, continuous parameters, and data fitting in one machine's RAM.

- **C2:** Models compose distributions and transformations over a static differentiable compute graph. Modeling, graph computation, sampling, and benchmarking occupy separate modules in the repository.
- **C3:** The repository documents precomputation using known data and generation of unboxed JVM bytecode. The [compiler implementation](https://raw.githubusercontent.com/stripe/rainier/develop/rainier-compute/src/main/scala/com/stripe/rainier/compute/Compiler.scala) exposes the boundary from real expressions to IR and compiled functions, including method/class size limits and explicit work buffers.

The architectural mechanisms are the evidence here; the README's machine-specific timing comparisons are not repeated as general performance claims.

### 16. [facebookresearch/beanmachine](https://github.com/facebookresearch/beanmachine)

**Python and C++ — declarative models with a specialized graph compiler. Archived on 2023-12-18.** Study the Bean Machine Graph/Beanstalk subsystem as a historical implementation, not a currently supported dependency.

- **C1:** The [BMG compiler guide](https://beanmachine.org/docs/beanstalk/) specifies static dependency graphs, function purity, restrictions on in-place mutation, and restrictions on stochastic control flow. These define which Python models can safely become a compiled graph.
- **C3:** The compiler targets a C++ inference runtime to remove Python execution overhead, particularly for unvectorized models. The graph can be inspected through Graphviz/DOT interfaces, making the specialization boundary reviewable.
- **C2:** The compiled backend fits into the broader model/query/observation interface instead of requiring a separate modeling language from users.

The documentation still uses development-era language about active work; GitHub's archive banner takes precedence for maintenance status.

### 17. [lawmurray/Birch](https://github.com/lawmurray/Birch)

**Birch language and C++ — compiled probabilistic programs with delayed sampling.** The monorepo contains the transpiler, memory and numerical support libraries, standard library, and tests; count it once.

- **C1:** The [delayed-sampling explanation](https://birch-lang.org/concepts/delayed-sampling/) describes an explicit structural invariant: marginalized variables are maintained in chains, and branching trees are reduced by simulating a variable when necessary. The example shows how conditioning changes the retained graph.
- **C2:** Automatic marginalization and conditioning operate on generative programs, allowing linear-Gaussian examples to recover Kalman-filter operations without users encoding that algorithm directly.
- **C3:** C++ transpilation and separate memory/numerical components expose execution costs below the modeling language. Delayed sampling also avoids sampling quantities that the system can integrate analytically.

### 18. [charles-river-analytics/figaro](https://github.com/charles-river-analytics/figaro)

**Scala — object-based probabilistic models and reusable reasoning algorithms.** Valuable as a classic JVM design, particularly for studying long-running inference services and algorithm lifecycle management. Current maintenance is not inferred from its historical code comments.

- **C2:** The [Algorithm interface](https://raw.githubusercontent.com/charles-river-analytics/figaro/master/Figaro/src/main/scala/com/cra/figaro/algorithm/Algorithm.scala) unifies one-time and anytime algorithms through start, stop, resume, and kill operations, including lifecycle-state checks.
- **C1:** The [Anytime implementation](https://raw.githubusercontent.com/charles-river-analytics/figaro/master/Figaro/src/main/scala/com/cra/figaro/algorithm/Anytime.scala) uses an Akka actor with active, inactive, and shutdown behaviors; it handles inference steps, query services, acknowledgments, resource cleanup, and timeouts. This adds concrete concurrency and failure semantics to probabilistic inference.

These sources are useful for assessing the lifecycle design, including its limitations; they do not establish that every transition or race is correct.

### 19. [miking-lang/miking-dppl](https://github.com/miking-lang/miking-dppl)

**Miking/MCore with an OCaml compilation target — a framework for building PPLs.** The relevant subsystem is CorePPL. The repository explicitly distinguishes its current structure from the artifact accompanying its 2022 paper.

- **C2:** The [compiler driver](https://raw.githubusercontent.com/miking-lang/miking-dppl/master/coreppl/src/cppl.mc) composes language fragments, loaders, transformations, and compiler selections for importance sampling, SMC, and several MCMC variants. This is a PPL construction framework with reusable compiler components.
- **C1:** The [inference-method interface](https://raw.githubusercontent.com/miking-lang/miking-dppl/master/coreppl/src/infer-method.mc) defines type-checking and compiler/runtime selection obligations. It documents an important caching invariant: method comparison must distinguish every field that runtime selection inspects.
- **C3:** The same interface exposes CPS choices, model alignment, delayed sampling, and resampling-placement strategies. The driver makes lowering and dead-code elimination explicit rather than hiding compilation behind a single opaque call.

## Exact, symbolic, logic, and functional approaches

### 20. [ML-KULeuven/problog](https://github.com/ML-KULeuven/problog)

**Python and probabilistic Prolog — inference through weighted Boolean formulas.** Study how a probabilistic logic language is grounded and compiled into a representation suitable for exact inference.

- **C1:** Overlapping proofs cannot be treated as independent events. The repository's two-coin example and weighted-formula explanation illustrate why the system must preserve shared logical structure when computing probabilities.
- **C2:** The [Python integration guide](https://problog.readthedocs.io/en/latest/python.html) exposes conversion stages from a logic program to a formula and then CNF/NNF or SDD representations. Decision-theoretic inference, learning from partial interpretations, and sampling reuse the core.
- **C3:** Knowledge compilation separates expensive logical representation construction from evaluation, with interchangeable target representations. The stage-by-stage API is a useful entry point for studying this architecture.

### 21. [SHoltzen/dice](https://github.com/SHoltzen/dice)

**OCaml with a decision-diagram backend — exact discrete probabilistic inference. Research code.** Study a compact compiler with explicit symbolic state and evidence handling. “Exact” refers to the inference approach; numeric evaluation still has selectable representations.

- **C1:** The [compiler](https://raw.githubusercontent.com/SHoltzen/dice/master/lib/Compiler.ml) carries separate BDDs for result state and observation constraints, assigns weights to fresh random choices, and combines evidence conditionally across branches. Losing that distinction changes the conditional distribution.
- **C2:** Typed expressions and compiled functions support compositional models, while the repository documents fixed-width integers, tuples, and bounded lists. Recursion is explicitly unsupported.
- **C3:** The [weighted model counter](https://raw.githubusercontent.com/SHoltzen/dice/master/lib/Wmc.ml) memoizes BDD subproblems and supports ordinary floating-point, big-number, and log-domain evaluation. Function compilation and alternative eager/substitution modes provide further concrete optimization boundaries.

### 22. [fzaiser/genfer](https://github.com/fzaiser/genfer)

**Rust — probabilistic programs compiled to generating functions. Research implementation.** An especially useful alternative to both sampling and Boolean knowledge compilation: it extracts posterior masses and moments through differentiation and can represent certain distributions with infinite support.

- **C1:** The [interval arithmetic implementation](https://raw.githubusercontent.com/fzaiser/genfer/main/src/interval.rs) widens numerical bounds using neighboring representable values. The repository distinguishes arbitrary precision from guaranteed precision and documents unsupported continuous observations, nonlinear operations, and unbounded loops.
- **C2:** The [generating-function representation](https://raw.githubusercontent.com/fzaiser/genfer/main/src/generating_function.rs) abstracts over number types and provides substitution, derivatives, Taylor coefficients, and symbolic operations usable across different models.
- **C3:** Shared expression nodes use reference counting, and analyses/simplification cache results for shared nodes. The repository candidly documents exponential dependence on the number of program variables, making this a useful study of optimization within a restricted inference domain.

### 23. [hakaru-dev/hakaru](https://github.com/hakaru-dev/hakaru)

**Haskell and Maple — typed probabilistic programs transformed into inference programs.** The repository explicitly labels itself alpha and experimental. Study symbolic inference as a compiler problem rather than treating inference as an external black box.

- **C1:** The [disintegration documentation](https://hakaru-dev.github.io/transforms/disintegrate/) shows transformation of a joint model into a program conditioned on supplied data, including ordering requirements and a documented limitation on Boolean conditioning. Correct variable binding, weighting, and transformation domains are substantive semantic obligations.
- **C2:** The [language-extension map](https://hakaru-dev.github.io/internals/newfeature/) connects the AST, symbol resolution, typechecker, probability transformations, sampler, and code generators. A single language representation is reused across interpretation, symbolic manipulation, and compilation.

The documentation has incomplete areas, so this is most suitable for engineers willing to work directly from a research compiler's source.

### 24. [tweag/monad-bayes](https://github.com/tweag/monad-bayes)

**Haskell — probabilistic models and compositional inference transformers.** Study how typeclasses and transformer composition can provide a probabilistic language without a separate surface-language compiler.

- **C1:** The [implementation guide](https://monad-bayes.netlify.app/usage/) uses a distinct log-number type for weights to avoid underflow from multiplying tiny probabilities. It also makes representation limits visible: enumerating continuous or infinite support is not an interchangeable replacement for sampling.
- **C2:** `MonadDistribution` and weighting capabilities separate model descriptions from concrete inference interpretations. Weighted, population, sequential, and traced representations compose into MCMC, SMC, and hybrid algorithms.

The [user guide](https://monad-bayes.netlify.app/probprog/) is a complementary entry point for tracing how the same model is consumed by different methods. The implementation guide is the stronger source for the abstraction boundaries.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search angles: tensor/effect-handler systems; Julia DSLs and programmable traces; R/BUGS compilation; Scala/JVM and C# compilers; Haskell symbolic and monadic systems; JavaScript/Clojure continuations; simulator/HPC integration; reactive message passing; exact logic and decision-diagram inference; and Go/Rust plus extensible compiler frameworks. Follow-up searches targeted implementation guides, source maps, compiler passes, PRNG semantics, and release histories. Later searches added Genfer and Miking DPPL; repeated searches within the established families increasingly returned the same projects, papers, wrappers, and examples.

Every retained canonical GitHub repository was opened. Each also has at least one separately inspected primary document or implementation file beyond its repository README; the linked entry points identify those materials. Some GitHub source pages and older documentation links failed to render, so public raw source files were read where necessary. Unauthenticated GitHub API requests were rate-limited; repository-page verification was used instead. No candidate code was run, dependencies installed, repositories cloned, or external services modified.

The selection avoids counting bindings and component libraries as independent full systems: Stan interfaces, DynamicPPL, ReactiveMP, stand-alone samplers, and generic autodiff libraries are not separately enumerated. Book-example collections, tiny demonstrations, and awesome-lists were excluded. Searches also found Liesel, Funsor, and other relevant projects; their omission is a scope choice, not a negative quality judgment. Infergo results pointed to its official Bitbucket distribution, so it was not included without verification of a substantive official GitHub repository. This report is not an exhaustive history of Church descendants, BUGS implementations, or probabilistic verification tools.

Maintenance claims are deliberately limited. Bean Machine's archive status is verified and called out; several other entries are explicitly research or historical-design studies, and older documentation is identified where material. C4 is awarded only where release history supplies sustained compatibility/testing evidence. No numerical speedup claims were independently benchmarked, and no source inspection here proves statistical correctness across all models or backends.
