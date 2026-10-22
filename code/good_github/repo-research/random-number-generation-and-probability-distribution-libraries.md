# Random number generation and probability distribution libraries

Research date: **2026-10-09**.

This selection covers 26 GitHub repositories implementing reusable random-bit engines, nonuniform sampling, probability-distribution calculations, and composable distribution objects. It includes parallel and vectorized generation, functional state management, numerical tails, and differentiable distributions. Large scientific repositories appear once, with the relevant subsystem identified. Quasi-random generation is included where it forms part of a substantial sampling library. Cryptography-only libraries, entropy services, statistical-test-only suites, tutorials, and thin bindings are outside the selection.

The criteria below are judgments grounded in the linked primary material, not a certification of correctness or an assertion that every component is exemplary. Repository pages and additional documentation or implementation material were opened for every entry. No candidate code was executed, and no performance benchmark was independently reproduced. Inclusion does not imply a particular maintenance cadence.

## Criteria legend

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or important failure modes.
- **C2 — Reusable abstractions:** substantial interfaces or compositional structures serving multiple applications.
- **C3 — Performance with structure:** concrete efficiency constraints addressed through understandable architectural choices.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility, testing, or complexity-management evidence; age alone does not qualify.

## Parallel, counter-based, and vectorized generation

### 1. [DEShawResearch/random123](https://github.com/DEShawResearch/random123)

**Language / role:** C and C++; counter-based engines for CPUs and GPU programming environments.

Study how Philox, Threefry, and related families replace a long mutable recurrence with a deterministic function of a key and counter. The repository explains both the direct functional API and adapters for conventional C++ and GSL consumers. It is particularly useful for understanding how application-level identities can determine random streams independently of execution order.

- **C1:** The test design distinguishes statistical quality from implementation correctness: language-independent known-answer vectors check compiled implementations, while unit tests check invariants such as increment equivalence. The documentation records compiler/intrinsic miscompilation as a real failure mode. [Tests and benchmarks](https://raw.githubusercontent.com/DEShawResearch/random123/main/tests/README).
- **C2 / C3:** Fixed-size counter/key types support several algorithms, while `MicroURNG` and `Engine` expose different state-management tradeoffs. Header implementation and counter-based evaluation make parallel generation structurally straightforward; the repository supplies CPU, threaded, and GPU timing harnesses. [Architecture and adapter overview](https://github.com/DEShawResearch/random123#overview).

The authors explicitly describe these generators as unsuitable for cryptographic use. Their test harness also deliberately sacrifices readability for portability; the engine interfaces are the better architectural starting point.

### 2. [imneme/pcg-cpp](https://github.com/imneme/pcg-cpp)

**Language / role:** C++; reference implementation of the PCG generator family.

Study a family of engines exposed through both convenient aliases and underlying templates, including normal and extended generators. This is more substantial than a single recurrence copied into an application: it makes stream identity, seeding, serialization, and navigation explicit parts of the API.

- **C1:** Equality includes both state and stream; calculating distance between generators requires a shared stream. The API documents the interaction between seeding and stream selection, and the limitations of extended generators. These contracts are central to reproducible state restoration and stream navigation.
- **C2 / C3:** C++ random-engine compatibility allows reuse with standard distributions. `advance` and `backstep` navigate eligible engines in logarithmic time, and `seed_seq_from` adapts external seed sources. [Detailed C++ API and behavioral contracts](https://www.pcg-random.org/using-pcg-cpp.html).

The linked API is the main reading entry point; the repository's `include` directory contains the corresponding template implementation. No current development-rate claim is made.

### 3. [rabauke/trng4](https://github.com/rabauke/trng4)

**Language / role:** C++; engines and discrete/continuous distributions for sequential and parallel Monte Carlo work.

Study explicit stream partitioning through `jump` and `split`, without coupling the library to one threading runtime. The repository demonstrates assigning portions of a sequence to OpenMP workers while retaining ordinary C++ engine/distribution usage.

- **C1:** The `yarn2` engine exposes modular recurrence arithmetic, separate parameter and state objects, and serialization that installs a parsed state only after successful input. Its CPU and CUDA paths also show the implementation consequences of platform differences. [YARN2 implementation](https://github.com/rabauke/trng4/blob/master/trng/yarn2.hpp).
- **C2:** Engines expose standard random-engine operations plus parallel stream operations; distributions remain interchangeable consumers. This provides a reusable framework for simulations using threads or MPI rather than a single parallel example. [Library and parallel-use overview](https://github.com/rabauke/trng4#example).

### 4. [msu-sparta/OpenRAND](https://github.com/msu-sparta/OpenRAND)

**Language / role:** C++; portable random generation for CPU and GPU scientific kernels.

Study the mapping from a simulation object's identity and iteration counter to a local generator. The project is a separate library with its own common API, generator implementations, and testing/benchmark integration, although its Philox implementation explicitly derives from Random123.

- **C1:** The Philox implementation separates user-supplied identifiers from an internal draw counter. Its source makes the counter layout and ten-round transformation inspectable, exposing the uniqueness and finite-counter assumptions on which reproducibility depends. [Philox implementation](https://raw.githubusercontent.com/msu-sparta/OpenRAND/main/include/openrand/philox.h).
- **C2 / C3:** The API serves scalar integer and floating-point requests, standard C++ distributions, and vector draws. The application pattern constructs short-lived kernel-local generators instead of moving a large persistent RNG state per object. The repository also documents TestU01 and PractRand integration. [Usage and testing design](https://github.com/msu-sparta/OpenRAND#usage).

### 5. [ROCm/rocm-libraries](https://github.com/ROCm/rocm-libraries)

**Language / role:** C++/HIP; **rocRAND subsystem**, with related hipRAND interoperability in the same monorepo.

Study bulk GPU generation as a problem of sequence layout, kernel configuration, and reproducibility. This is the canonical monorepo: its migration table marks rocRAND complete. The former standalone rocRAND repository is retired and is not counted separately.

- **C1:** The programming guide precisely specifies how logical generator positions map to output memory for different engines. It distinguishes backward-compatible ordering from dynamic ordering, whose sequences may vary by GPU and library version.
- **C2 / C3:** The common generator framework covers pseudorandom and Sobol-family quasi-random methods. Explicit ordering modes expose a real architectural tradeoff between hardware-specific tuning and stable output rather than hiding it behind a universal performance claim. [Programming guide and sequence-ordering formulas](https://rocm.docs.amd.com/projects/rocRAND/en/latest/conceptual/programmers-guide.html).

The monorepo's [migration and directory description](https://github.com/ROCm/rocm-libraries#super-repo-project-status) identifies `projects/rocrand` as the relevant component; unrelated ROCm libraries are outside this entry.

### 6. [bab2min/EigenRand](https://github.com/bab2min/EigenRand)

**Language / role:** C++; vectorized engines and distribution generators integrated with Eigen arrays and matrices.

Study how random generation fits an expression-oriented numerical library. Scalar parameters, arrays of parameters, reusable generator objects, and multivariate outputs all share the surrounding Eigen type and shape machinery.

- **C2:** Distribution generator objects can be reused across matrix requests; `generateLike` preserves an existing object's shape/type, and supported distributions can broadcast scalar parameters or consume parameter arrays. [Generator and parameter-vectorization guide](https://bab2min.github.io/eigenrand/v0.5.0/en/getting_started.html).
- **C3:** SIMD engines and distribution routines address the cost of scalar random calls in matrix construction. Reusing generator objects avoids reconstructing distribution setup for each matrix. The guide explains these mechanisms rather than merely reporting speedups.
- **C4:** The repository's dated 2020–2026 history records cross-ISA sequence support, scalar range and infinite-loop fixes, NEON work, and Eigen 5 support while retaining earlier Eigen compatibility. [Release history](https://github.com/bab2min/EigenRand#history).

The detailed guide linked above is explicitly version 0.5.0; use the repository history for later compatibility changes.

### 7. [arm/openrng](https://github.com/arm/openrng)

**Language / role:** C++ implementation with a VSL-compatible interface; random engines and distribution generation for Arm-oriented numerical software.

Study an independent implementation of an established numerical API. The README distinguishes cross-platform reproducibility of bit outputs from integer or floating-point distribution results, which can differ because of arithmetic precision.

- **C1:** The generator base class handles null/bad stream checks, initialization failure, and cached Box–Muller state that must survive intervening generator advancement. These are observable API semantics, not merely recurrence mathematics. [Generator base implementation](https://github.com/arm/openrng/blob/main/src/generic/generator/generator.hpp).
- **C2:** A common abstraction covers bulk bit/real output, state save/load, skip-ahead, and leapfrogging; unsupported capabilities return explicit error codes. The implementation also documents how it manages polymorphic objects while avoiding a C++ runtime dependency.

Coverage is incomplete: the verified [implementation-status matrix](https://github.com/arm/openrng/blob/main/IMPLEMENTATION_STATUS.md) marks some generators and distributions unimplemented. This entry does not claim complete oneMKL equivalence or long-established project evolution.

## General-purpose engines and state-management frameworks

### 8. [rust-random/rand](https://github.com/rust-random/rand)

**Language / role:** Rust; reusable RNG interfaces, common generators, basic distributions, and sequence sampling.

Study the boundary between convenient thread-local randomness, explicitly owned generators, and reusable sampling interfaces. The separate `rand_distr` repository below supplies specialized distribution algorithms and is not counted as part of this entry.

- **C1:** `ThreadRng` documents its non-reentrancy assumptions, exclusion from cross-thread transfer, reseeding failure behavior, and lack of automatic reseeding after `fork`. Its `UnsafeCell` rationale explains the exclusive-access invariant, and its debug-output test protects internal state from accidental formatting disclosure. [Thread-local implementation](https://github.com/rust-random/rand/blob/master/src/rngs/thread.rs).
- **C2 / C3:** The ecosystem separates engine selection from consumers. The implementation uses buffered block generation and a documented reseeding threshold, while the [RNG design guide](https://rust-random.github.io/book/guide-rngs.html) compares state size, initialization, portability, and generation costs.

These are useful engineering contracts; the entry is not a security certification for every generator offered by Rand.

### 9. [numpy/numpy](https://github.com/numpy/numpy)

**Language / role:** Python, Cython, and C; **`numpy.random` subsystem**.

Study the separation of raw-bit engines from array-valued distribution generation, and the migration away from freezing every distribution algorithm indefinitely. This subsystem is particularly instructive for scientific APIs whose users depend on reproducibility.

- **C1 / C2:** `SeedSequence` mixes input entropy and spawn-tree position into engine initialization. Recursive spawning supports distributed work without a global allocation service, while the documentation carefully describes stream independence as probabilistic. [Parallel generation design](https://numpy.org/doc/stable/reference/random/parallel.html).
- **C4:** The 2018–2019 RNG policy proposal documents the compatibility policy established in 2008, its platform and LAPACK limitations, and the design rationale for retaining legacy behavior while enabling a new generator system. This is concrete evidence of years of compatibility management, not merely repository age. [NEP 19](https://numpy.org/neps/nep-0019-rng-policy.html).

Do not infer that a seed alone guarantees identical floating-point distribution results across versions and platforms; this limitation is part of the material worth studying.

### 10. [bashtage/randomgen](https://github.com/bashtage/randomgen)

**Language / role:** Python, Cython, and C; additional NumPy-compatible bit generators and extended variate generation.

Study how a generator collection integrates with another library's distribution layer through a low-level ABI. Its independent implementations and engine-specific state management make it substantially more than a generated NumPy wrapper.

- **C1:** The ChaCha implementation documents shared locking, buffered state, key-versus-seed semantics, state advancement, and jump-based stream partitioning. It validates configuration and exposes the assumptions behind integer-stream compatibility. [ChaCha source and embedded design documentation](https://raw.githubusercontent.com/bashtage/randomgen/main/randomgen/chacha.pyx).
- **C2 / C3:** Function-pointer capsules supply raw integers and doubles to NumPy's `Generator`; generator choice can change independently of distribution consumers. The same source exposes a SIMD capability check and selectable implementation, keeping platform optimization behind the engine boundary.

The repository documents the removal of its older `Generator` and `RandomState` classes in favor of NumPy's consumer API. Study the current bit-generator integration rather than assuming old examples remain supported.

### 11. [apache/commons-rng](https://github.com/apache/commons-rng)

**Language / role:** Java; RNG interfaces, engine implementations, factories, and sampling algorithms. **Official Apache GitHub mirror**, with Apache GitBox identified by the project documentation as the current source repository.

Study a deliberate separation into client API, core engines, simple construction, and sampling modules. This keeps algorithms consuming randomness independent of implementation and construction policy.

- **C1:** Jumpable and splittable interfaces make different promises about stream partitioning. The guide warns that returned values do not necessarily correspond one-for-one to engine state steps, an important limitation when preventing overlap between workers.
- **C2 / C3:** `UniformRandomProvider` is a small consumer-facing boundary; factories and samplers build on it. Samplers can precompute coefficients, while separate JMH and external statistical-stress tools evaluate cost and output quality. [Architecture, stream contracts, and performance methodology](https://commons.apache.org/proper/commons-rng/userguide/rng.html).

The guide is a particularly useful single entry point because it connects module boundaries to their rationale and explicitly discusses release compatibility.

### 12. [haskell/random](https://github.com/haskell/random)

**Language / role:** Haskell; splittable generators and pure/monadic random-generation interfaces.

Study the same probabilistic computation expressed over pure state, ordinary mutable references, atomic references, or software transactional memory. This exposes concurrency and exception behavior directly in the abstraction choices.

- **C1:** The source distinguishes `StateGenM`, `IOGenM`, `AtomicGenM`, and `TGenM` by exception and concurrency guarantees. Atomic updates and transactional updates solve different state-consistency problems. [Stateful interface and adapters](https://raw.githubusercontent.com/haskell/random/master/src/System/Random/Stateful.hs).
- **C2:** `RandomGen`, `StatefulGen`, `Uniform`, and `UniformRange` separate generator mechanics, execution context, and sampled types; adapters let existing pure engines participate in mutable algorithms.

The [changelog](https://github.com/haskell/random/blob/master/CHANGELOG.md) is a valuable second entry point: it records the SplitMix transition, floating-point fixes, compiler compatibility work, and a `setStdGen` thread-safety correction. Those fixes are evidence of substantive failure modes, not grounds to assume every historic version has identical behavior.

### 13. [dubzzz/pure-rand](https://github.com/dubzzz/pure-rand)

**Language / role:** TypeScript; deterministic engines, uniform distributions, jumping, and optional pure state transitions.

Study how a small JavaScript-facing library deals with integer arithmetic wider than the language's bitwise operations. Its API supports both mutation and a `purify` adapter that returns a value plus a new generator, making replay and branching explicit.

- **C1:** The small-range implementation rejects the excess part of the engine's output range before taking a remainder, avoiding modulo bias. The large-range path uses two-word arithmetic when subtracting endpoints cannot safely remain a JavaScript number. [Rejection sampler](https://github.com/dubzzz/pure-rand/blob/main/src/distribution/internals/uniformIntInternal.ts); [large-range handling](https://raw.githubusercontent.com/dubzzz/pure-rand/main/src/distribution/uniformInt.ts).
- **C2:** Interchangeable engines and distribution functions share a generator contract, while the documented pure adapter and jump operations support repeatable simulations and state branching without requiring a distinct distribution implementation for each execution style.

### 14. [boostorg/random](https://github.com/boostorg/random)

**Language / role:** C++; Boost.Random engines, distributions, seed sequences, and adapters.

Study a concept-oriented random-number framework whose contracts make engines and distribution mappings independently replaceable. This is a distinct implementation repository from Boost.Math: its central role is generating samples rather than evaluating distribution functions.

- **C1:** The reference carefully distinguishes closed integer ranges from half-open real ranges, requires stable engine bounds, and explains why mapping an integer engine to a different range is nontrivial. These details are foundational to unbiased and boundary-correct distributions.
- **C2 / C3:** Templates and concrete aliases separate algorithm families from parameter choices; distribution concepts permit different implementations with tradeoffs in storage, random draws, and arithmetic cost. [Concepts and implementation-oriented reference](https://www.boost.org/doc/libs/latest/doc/html/boost_random/reference.html).

The reference is the principal entry point for understanding the abstractions before reading individual engine and distribution headers.

## Probability distributions and numerical evaluation

### 15. [rust-random/rand_distr](https://github.com/rust-random/rand_distr)

**Language / role:** Rust; specialized nonuniform samplers using Rand's distribution and RNG interfaces.

Study distribution-specific algorithms separated from the engine ecosystem. The repository explicitly focuses on sampling; it points users needing PDF/CDF calculations toward alternatives such as Statrs. Its history before the 2025 repository split remains associated with `rand`.

- **C1:** Gamma sampling documents overflow and underflow limits, validates shape/scale, and handles shape below one, exactly one, and above one through different representations. This shows that mathematically valid parameters can still pose floating-point problems.
- **C2 / C3:** The Gamma type implements the common `Distribution` interface while storing precomputed constants in specialized representations. It composes normal, exponential, and open-interval uniform samplers instead of embedding another RNG. [Gamma source, algorithms, and numerical limitations](https://raw.githubusercontent.com/rust-random/rand_distr/master/src/gamma.rs).

The repository also documents how `libm` versus standard-library math affects reproducibility, portability, and performance; identical seeds are not the entire contract.

### 16. [JuliaStats/Distributions.jl](https://github.com/JuliaStats/Distributions.jl)

**Language / role:** Julia; univariate, multivariate, and matrix-valued distributions, sampling, and fitting.

Study an extensible mathematical type hierarchy built around multiple dispatch. A small implementation surface supplies richer public behavior, while separate sampler objects can retain expensive setup.

- **C2:** `Sampleable` encodes variate form and value support. Implementing a few scalar or in-place methods provides allocating and batched APIs; distribution types add log densities, CDFs, quantiles, and support information. [Extension contracts and implementation sketches](https://juliastats.org/Distributions.jl/stable/extends/).
- **C3:** `sampler(d)` can return a precomputed sampling object, and specialized matrix methods can replace repeated scalar draws. Generic public methods perform allocation and shape checks before calling lower-level kernels, keeping performance work behind explicit contracts.

The repository additionally requires edge-case tests and checks for method ambiguities. That is especially relevant when studying how an open multiple-dispatch hierarchy grows without silently introducing ambiguous calls.

### 17. [scipy/scipy](https://github.com/scipy/scipy)

**Language / role:** Python with compiled numerical components; **`scipy.stats` distributions and random-variable infrastructure**.

Study the redesign of a large distribution API while keeping established users functional. The transition guide explains the costs of pre-instantiated distribution families, repeated parameter validation, and duplicated method documentation, then motivates parameterized random-variable objects.

- **C1:** The new interface includes direct interval-probability calculations that can avoid cancellation when subtracting nearly equal CDF values. Logarithmic and complementary operations are exposed as first-class numerical tools.
- **C2 / C3:** Distribution-family classes, fixed-parameter random variables, transformations, and shared methods provide a reusable framework. Moving validation and setup to object construction addresses concrete repeated-call overhead. [Random Variable Transition Guide](https://docs.scipy.org/doc/scipy/tutorial/stats/rv_infrastructure.html).

The guide explicitly permits continued use of the older infrastructure and discusses migration limitations, including fitting workflows. The selection concerns this subsystem, not all of SciPy.

### 18. [boostorg/math](https://github.com/boostorg/math)

**Language / role:** C++; **statistical-distribution and supporting special-function subsystem**.

Study probability evaluation as generic numerical software: distribution objects work with common nonmember operations, and the library supports numeric types beyond ordinary `double`. This complements, rather than duplicates, Boost.Random's sampling role.

- **C1:** Complemented CDF and quantile operations avoid forming `1-p` when cancellation would destroy significant digits. The documentation demonstrates why directly supplying a small tail probability can distinguish a finite answer from an overflow. [Complement design and numerical examples](https://www.boost.org/doc/libs/latest/libs/math/doc/html/math_toolkit/stat_tut/overview/complements.html).
- **C2:** Distribution objects and generic PDF/CDF/quantile operations provide a common interface across discrete and continuous families. The repository describes generic real-number support, including multiprecision, backed by shared special functions. [Distribution API overview](https://www.boost.org/doc/libs/latest/libs/math/doc/html/math_toolkit/stat_tut/overview.html).

The complement adapter is an especially compact example of API design preserving numerical intent.

### 19. [apache/commons-statistics](https://github.com/apache/commons-statistics)

**Language / role:** Java; **`commons-statistics-distribution` subsystem**. Official Apache GitHub repository/mirror in the Commons development infrastructure.

Study the separation between distribution evaluation and RNG-dependent sampling. This entry is distinct from Commons RNG: the normal distribution computes densities and tail probabilities itself, then constructs a sampler using Commons RNG.

- **C1:** `NormalDistribution` uses complementary error functions for opposite tails, an error-function difference for interval probabilities, and extended-precision setup to reduce rounding while avoiding overflow/underflow. Its inverse survival calculation does not first subtract the probability from one. [Normal implementation](https://github.com/apache/commons-statistics/blob/master/commons-statistics-distribution/src/main/java/org/apache/commons/statistics/distribution/NormalDistribution.java).
- **C2 / C3:** `ContinuousDistribution` separates evaluation from a nested `Sampler` created with a supplied `UniformRandomProvider`. The implementation caches normalization quantities and composes a Ziggurat-based sampler through that boundary. [ContinuousDistribution contract](https://commons.apache.org/proper/commons-statistics/commons-statistics-distribution/apidocs/org/apache/commons/statistics/distribution/ContinuousDistribution.html).

### 20. [gonum/gonum](https://github.com/gonum/gonum)

**Language / role:** Go; **`stat/distuv` and related distribution packages** in the numerical monorepo.

Study compact distribution implementations that combine probability evaluation and sampling while accepting an explicit random source. The Gamma implementation is a useful starting point because it selects different algorithms for materially different parameter regimes.

- **C1:** Very small Gamma shape parameters use a specialized rejection algorithm carried out in log space where possible. Quantile arguments are checked, support boundaries receive explicit handling, and the survival function calls a complementary incomplete-gamma routine directly.
- **C2 / C3:** A distribution value exposes `Prob`, `LogProb`, `CDF`, `Quantile`, `Survival`, moments, and `Rand`, with an optional `rand.Source`. The exponential special case and separate small-shape path show targeted algorithm selection within a readable implementation. [Gamma source](https://raw.githubusercontent.com/gonum/gonum/master/stat/distuv/gamma.go).

Gonum's repository documents compiler/platform testing and cautions that floating-point behavior can differ across architectures; this entry does not assume bitwise portability.

### 21. [mathnet/mathnet-numerics](https://github.com/mathnet/mathnet-numerics)

**Language / role:** C# with F# support; **random-source and probability-distribution subsystems**.

Study how an existing platform RNG abstraction is extended with optional thread safety, array filling, and lazy sequences, then consumed by distribution classes. The managed implementation provides meaningful architecture independently of optional native linear-algebra providers.

- **C1 / C3:** `RandomSource` centralizes optional locking and range validation. Bulk fill methods lock around the whole loop, and sequence generation uses buffering: concrete choices that balance synchronization costs with reusable engine methods. [RandomSource implementation](https://raw.githubusercontent.com/mathnet/mathnet-numerics/master/src/Numerics/Random/RandomSource.cs).
- **C2:** Distribution objects implement common interfaces and accept `System.Random` sources. The normal distribution supplies distinct factories for standard deviation, variance, and precision, making parameter semantics explicit. [Normal distribution implementation](https://raw.githubusercontent.com/mathnet/mathnet-numerics/master/src/Numerics/Distributions/Normal.cs).

### 22. [statrs-dev/statrs](https://github.com/statrs-dev/statrs)

**Language / role:** Rust; distribution evaluation, special functions, statistical summaries, and optional sampling.

Study a Rust-native API that began as a port of Math.NET's statistical functionality and developed its own traits, errors, feature boundaries, and precision conventions. It is a substantive implementation, not a generated binding to Math.NET.

- **C1:** The Beta implementation rejects invalid shape parameters through typed errors, treats support endpoints explicitly, and implements CDF and survival operations through special-function calculations. Its survival implementation switches formulas to avoid losing information when subtracting a very small argument from one. [Beta implementation](https://docs.rs/statrs/latest/src/statrs/distribution/beta.rs.html).
- **C2:** Density and cumulative operations are exposed through separate traits, and optional Rand integration implements sampling through the common distribution interface. This lets callers use probability calculations without requiring one particular entropy backend. [Beta traits and sampling implementation](https://docs.rs/statrs/latest/src/statrs/distribution/beta.rs.html).

The repository's precision discussion and NIST-test instructions provide context for evaluating numerical changes. Accuracy claims should still be assessed distribution by distribution.

### 23. [haskell/statistics](https://github.com/haskell/statistics)

**Language / role:** Haskell; **`Statistics.Distribution` hierarchy and implementations** within the statistics library. The README identifies the GitHub repository as its master Git mirror.

Study how mathematical properties become type-class distinctions rather than assumptions attached to every distribution. In particular, having a mean for some parameters is represented differently from having a finite mean for all valid parameters.

- **C1:** Complementary cumulative functions are explicit extension points to avoid precision loss. `MaybeMean`, `MaybeVariance`, and `MaybeEntropy` represent undefined quantities, while quantile methods document invalid-probability behavior.
- **C2:** Separate classes cover discrete probability, continuous density, quantiles, sampling, and fitting. Default methods reduce the required implementation surface, and samplers accept `StatefulGen` instead of fixing one engine or execution context. [Distribution contracts and default implementations](https://raw.githubusercontent.com/haskell/statistics/master/Statistics/Distribution.hs).

This is a useful contrast to class hierarchies that return a numeric sentinel for every undefined statistic.

## Simulation streams and composable differentiable distributions

### 24. [umontreal-simul/ssj](https://github.com/umontreal-simul/ssj)

**Language / role:** Java; stochastic simulation library, specifically **`rng`, `randvar`, `probdist`, and randomized quasi-Monte Carlo facilities**.

Study streams and substreams as explicit simulation resources. The library separates uniform engines from nonuniform variate generation and probability-distribution calculations, supporting simulation replications and controlled replay.

- **C1:** `RandomStream` distinguishes the initial stream state, current substream start, and current state. Reset and advance operations specify which states change; uniform real generation excludes both endpoints. These contracts matter when replaying replications or applying transforms with singularities at zero or one.
- **C2:** Concrete engines implement the stream interface while variate generators live in a separate package. The same stream-management model can therefore support multiple distributions and simulation strategies. [RandomStream design and interface](https://raw.githubusercontent.com/umontreal-simul/ssj/master/src/main/java/umontreal/ssj/rng/RandomStream.java).

The repository documents a package-namespace change at version 3.1.0; historical examples may use the earlier namespace. Broader event-simulation facilities are not independently counted.

### 25. [tensorflow/probability](https://github.com/tensorflow/probability)

**Language / role:** Python; **distribution, bijector, and joint-distribution layers**, with TensorFlow and JAX substrate support.

Study distributions as tensor-valued objects with batch and event semantics, and transformations as reusable objects that know their inverse and Jacobian. This entry concerns those probability-library layers rather than cataloguing all inference algorithms in the repository.

- **C1:** `TransformedDistribution` connects log probability to the inverse transform and inverse log-Jacobian determinant. It also documents a subtle failure mode: determining whether bijectors match for KL calculations can behave differently in eager and traced execution.
- **C2:** A base distribution plus a bijector supplies a transformed distribution, allowing the same implementation to express familiar log-normal variables and more elaborate models. Sampling, density evaluation, and related operations derive from the shared contract. [TransformedDistribution implementation and mathematical contracts](https://raw.githubusercontent.com/tensorflow/probability/main/tensorflow_probability/python/distributions/transformed_distribution.py).

The repository overview explains how these building blocks feed joint distributions and model-building layers; it does not imply every transform has every statistic implemented.

### 26. [google-deepmind/distrax](https://github.com/google-deepmind/distrax)

**Language / role:** Python/JAX; distributions and bijectors, implemented as a JAX-native subset/reworking of TensorFlow Probability concepts.

Study a smaller implementation that emphasizes readable mathematics and compatibility with TFP objects. It merits a separate entry because it implements its own transformation, shape inference, and combined sampling paths rather than merely forwarding calls to TFP.

- **C1:** `Transformed` checks event-rank compatibility and infers shapes/dtypes through JAX tracing. Its source documents the traceability assumptions and rejects KL computations when equivalent transformations cannot be established.
- **C2 / C3:** `_sample_n_and_log_prob` combines sampling with forward transformation and log-determinant evaluation. This avoids an inverse transform and also permits the operation for bijectors without inverse methods. [Transformed distribution implementation](https://github.com/google-deepmind/distrax/blob/main/distrax/_src/distributions/transformed.py).

The [design and extension guide](https://github.com/google-deepmind/distrax#design-principles) explains static event dimensions, subclassing, and TFP interoperability. It also flags incomplete support for mapping over distribution objects with `vmap`/`pmap`; ordinary vectorized sampling should not be confused with that broader capability.

## Search coverage, exclusions, and limitations

Discovery used more than twenty query formulations, followed by repository-page verification and source/documentation inspection. Distinct search angles included:

- Counter-based CPU/GPU engines, stream partitioning, PCG, and reproducible parallel simulation.
- GPU RNG libraries, rocRAND migration, SIMD matrix generation, and Arm numerical-API compatibility.
- Rust and Julia distribution libraries; NumPy-compatible bit generators and their ABI/state contracts.
- Java RNG versus distribution packages, and simulation-oriented stream/substream management.
- Go, C#, Haskell, TypeScript, and smaller language communities, including searches for Common Lisp and Fortran implementations.
- Automatic nonuniform variate generation, complementary CDFs, extreme quantiles, and numerical stability.
- Sobol/Halton and quasi-Monte Carlo sampling; exact/discrete distribution composition; JAX distribution/bijector libraries.

Later searches continued to find candidates, but increasingly repeated already represented implementation patterns—counter/key partitioning, engine/distribution separation, tail-aware special functions, and transformed distributions. Distrax was retained from the later pass because its combined forward sampling/log-probability path added a concrete architectural contrast. The stopping judgment concerns diminishing architectural variety in this selection, not proof that no other qualifying repositories exist.

The retired standalone rocRAND repository and RandomGen's superseded `ng-numpy-randomstate` predecessor were not counted separately. PCG ports and Random123 ports were not multiplied into independent entries; OpenRAND was retained for its separate API, implementation integration, and work-unit model, with its Random123 lineage disclosed. Likewise, Statrs' Math.NET origins and Distrax's TFP relationship are explicit. Boost.Random and Boost.Math are separate substantive repositories with different responsibilities; Apache Commons RNG and Commons Statistics likewise implement different layers.

UNU.RAN and GSL appeared in discovery, but this pass did not establish a suitable canonical official GitHub implementation/mirror for a separate entry; their absence is a hosting-verification limitation, not a quality judgment. Small standalone Sobol implementations and libraries primarily about integration were not expanded into a second quasi-Monte Carlo catalogue. Statistical batteries such as TestU01 and PractRand were used only as project-reported testing context. Cryptographic entropy infrastructure and general probabilistic-programming systems without a separately inspected distribution subsystem were excluded.

All retained repository URLs were opened, and every entry has additional primary documentation or source evidence beyond its repository tagline. Some raw GitHub fetches failed; those were resolved through GitHub file retrieval, rendered source, or official API documentation. Branch and `latest` documentation links can change after the research date, and cached documentation may describe different releases; explicit version differences are noted where material. No claim of uniform active maintenance, universal numerical accuracy, or independently verified benchmark superiority is made.
