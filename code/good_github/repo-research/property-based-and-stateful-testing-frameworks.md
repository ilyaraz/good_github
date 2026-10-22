# Property-based and stateful testing frameworks

Research date: **2026-10-09**.

This selection covers 27 GitHub repositories implementing reusable property generators, counterexample shrinking, state-machine testing, concurrent-history checking, or closely related bounded exhaustive testing. It spans general libraries, language-specific frameworks, and substantive API-testing and proof-assistant systems. The emphasis is on code an experienced engineer can study: how generated tests remain meaningful during reduction, how effects and dependencies are modeled, and how search cost and reproducibility are managed. Inclusion is a selection judgment supported by the cited sources, not a claim that every component is exemplary or that every project is suitable for new production adoption.

**Criteria legend**

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or failure handling create substantial implementation challenges.
- **C2 — Reusable abstractions:** the repository supplies substantial generators, testing engines, models, or composition mechanisms usable across applications.
- **C3 — Performance with structure:** concrete search, allocation, execution, or reduction costs are addressed through understandable implementation boundaries.
- **C4 — Sustained evolution:** dated changes demonstrate years of compatibility work, testing improvements, or deliberate complexity management. Repository age and push dates alone do not qualify.

Canonical repository identities and archive/fork metadata were checked through GitHub's API. Source links point to the inspected default branches; these can contain work newer than the latest release. No blanket claim of active maintenance is intended. Significant status qualifications appear in the entries.

## General engines and shrinking architectures

### 1. [HypothesisWorks/hypothesis](https://github.com/HypothesisWorks/hypothesis)

**Language / role:** Python, with Rust internals; general property-based and rule-based stateful testing.

Study the separation between user strategies and Conjecture's representation of test executions as typed random choices. This is a particularly useful codebase for understanding why simplifying the decisions that generated an input can preserve constraints better than independently simplifying the final value.

- **C1:** Conjecture tracks distinct failures while shrinking, handles floating-point choices separately, and explicitly treats minimization as an approximation rather than a guarantee of a global minimum. **C3:** search objects cache decisions, while deletion passes avoid repeatedly reconsidering prefixes that would introduce quadratic work. The [internals guide](https://github.com/HypothesisWorks/hypothesis/blob/master/guides/internals.rst) explains these mechanisms and the engine's targeted quality tests.
- **C2:** rule-based machines combine strategies with reusable result bundles, preconditions, and initialization. Bundles let later actions consume values returned by earlier actions, as shown in the [stateful testing guide](https://github.com/HypothesisWorks/hypothesis/blob/master/hypothesis/docs/stateful.rst).

### 2. [dubzzz/fast-check](https://github.com/dubzzz/fast-check)

**Language / role:** TypeScript; property testing, model-based testing, and asynchronous race testing for JavaScript.

Study how generated commands retain execution and replay information, alongside a scheduler that controls when wrapped promises resolve. The latter explores asynchronous ordering; it should not be confused with exhaustive scheduling of native threads or uncontrolled external events.

- **C1:** command shrinking filters out operations that never ran, checks replay consistency, and preserves the final failing operation during sequence reduction. **C3:** the implementation deliberately flattens the composition of shrink iterators to avoid deep recursion and stack overflow on large command sequences. See [CommandsArbitrary.ts](https://github.com/dubzzz/fast-check/blob/main/packages/fast-check/src/arbitrary/_internals/CommandsArbitrary.ts).
- **C2:** the [scheduler guide](https://github.com/dubzzz/fast-check/blob/main/website/docs/advanced/race-conditions.md) exposes reusable wrappers for individual promises, asynchronous functions, and dependent sequences, with reporting and explicit scheduling controls.

### 3. [nick8325/quickcheck](https://github.com/nick8325/quickcheck)

**Language / role:** Haskell; the QuickCheck 2 generator/property/shrinker library.

Study the architecture in which value generation and shrinking are separately specified. Its explicit contracts make this an instructive counterpart to integrated-shrinking systems.

- **C1:** the documented shrinker contract addresses invariant preservation, candidate ordering, accidental self-shrinking loops, and the mistake of forcing several fields to shrink in tandem. **C2:** `Arbitrary`, its higher-kinded variants, and generic subterm operations provide reusable mechanisms for user-defined types. See [Arbitrary.hs](https://github.com/nick8325/quickcheck/blob/master/src/Test/QuickCheck/Arbitrary.hs).
- **C4:** the [changelog](https://github.com/nick8325/quickcheck/blob/master/changelog.md) records compatibility work across 2019–2026, floating-point shrinker fixes, strict-map invariant repairs, and changes to coverage and discard handling. It also documents specialized numeric generators and reduced memory use in float generation, rather than merely asserting maturity.

### 4. [hedgehogqa/haskell-hedgehog](https://github.com/hedgehogqa/haskell-hedgehog)

**Language / role:** Haskell; integrated shrinking, effectful generators, and abstract state-machine testing.

Study the generator's actual representation: a size and seed produce a tree of candidate values, with discard and user effects represented through transformers. This connects the public composition API directly to the reduction machinery.

- **C1:** state-machine variables distinguish symbolic results available during generation from concrete results available during execution. Environment lookup and type errors are represented explicitly, addressing dependencies between actions. See [Internal/State.hs](https://github.com/hedgehogqa/haskell-hedgehog/blob/master/hedgehog/src/Hedgehog/Internal/State.hs).
- **C2:** `GenT` combines a generator, shrink tree, discard handling, and effects, with explicit operations for running and transforming that structure. [Internal/Gen.hs](https://github.com/hedgehogqa/haskell-hedgehog/blob/master/hedgehog/src/Hedgehog/Internal/Gen.hs) is the architectural entry point. The monorepo's core `hedgehog` package is the focus; its adapters and examples are not counted separately.

### 5. [well-typed/falsify](https://github.com/well-typed/falsify)

**Language / role:** Haskell; property testing with internal shrinking over a splittable random sample tree.

Study an alternative to both output shrink trees and linear random-choice recordings. A generator interprets a sample tree and returns possible smaller sample trees; monadic composition combines reductions from separate branches.

- **C1:** the explicit `Minimal` constructor represents an infinite all-zero tree finitely. Shrinking must recognize it without forcing infinite subtrees, a nontrivial interaction between laziness, termination, and counterexample reduction. See [SampleTree.hs](https://github.com/well-typed/falsify/blob/main/falsify/src/Test/Falsify/SampleTree.hs).
- **C2:** the [generator implementation](https://github.com/well-typed/falsify/blob/main/falsify/src/Test/Falsify/Internal/Generator.hs) provides `Functor`, `Applicative`, `Monad`, and selective composition, plus mechanisms for generator independence. It explains how generation constraints and dependent choices interact with shrinking. The core and Tasty integration belong to one repository.

### 6. [proptest-rs/proptest](https://github.com/proptest-rs/proptest)

**Language / role:** Rust; composable strategies, shrinking, and the `proptest-state-machine` subsystem.

Study the distinction between a strategy and its stateful `ValueTree`, whose `simplify` and `complicate` operations support a reversible search for failing values.

- **C1:** shrinking respects the strategy's described domain; the [shrinking guide](https://github.com/proptest-rs/proptest/blob/main/book/src/proptest/tutorial/shrinking-basics.md) demonstrates this for numeric intervals and structured Unicode strings.
- **C2:** [state-machine testing](https://github.com/proptest-rs/proptest/blob/main/book/src/proptest/state-machine.md) separates `ReferenceStateMachine` from `StateMachineTest`, allowing the same transition descriptions to drive an abstract model and the real system. Preconditions are rechecked because removing earlier transitions can invalidate later ones; postconditions, invariants, teardown, and saved regression seeds complete the reusable framework. This crate is counted as part of the monorepo, not as another project.

### 7. [flyingmutant/rapid](https://github.com/flyingmutant/rapid)

**Language / role:** Go; property testing with recorded-randomness shrinking and state-machine actions.

Study a relatively direct imperative interface backed by a multi-pass reduction engine. It is useful for tracing the entire path from generated actions to minimized random-bit recordings.

- **C1:** `T.Repeat` checks invariants before and after actions, rejects invalid action attempts, and uses stable ordering of action names. **C2:** actions can be supplied as functions or obtained from a state-machine interface, providing two reusable ways to model imperative APIs. See [statemachine.go](https://github.com/flyingmutant/rapid/blob/master/statemachine.go).
- **C3:** [shrink.go](https://github.com/flyingmutant/rapid/blob/master/shrink.go) separates group removal, block minimization, and more expensive fallback passes, with deadlines and a candidate cache. This is concrete evidence of controlling reduction cost, without assuming comparative throughput against other libraries.

### 8. [clojure/test.check](https://github.com/clojure/test.check)

**Language / role:** Clojure and ClojureScript; composable generators and lazy shrink trees.

Study a compact functional implementation shared across JVM and JavaScript targets. The useful distinction is between the size parameter controlling generated distributions and the tree governing subsequent reduction.

- **C1:** tree filtering removes invalid candidate subtrees; collection shrinking combines removal of elements with shrinking their contents. Those operations must preserve the relationship between a generated value and its descendants. **C2:** lazy rose-tree `fmap`, `bind`, `join`, and `zip` give the engine reusable composition primitives. See [rose_tree.cljc](https://github.com/clojure/test.check/blob/master/src/main/clojure/clojure/test/check/rose_tree.cljc).
- The [growth and shrinking guide](https://github.com/clojure/test.check/blob/master/doc/growth-and-shrinking.md) explains how generator sizing affects practical coverage. This entry concerns the general engine; it does not claim a built-in concurrent state-machine framework.

### 9. [c-cube/qcheck](https://github.com/c-cube/qcheck)

**Language / role:** OCaml; the QCheck/QCheck2 core, generator derivation, and test-runner integrations.

Study QCheck2's public contracts alongside the repository's compatibility surface. It provides a clear account of how integrating generated values with their possible shrinks changes a library API.

- **C1:** QCheck2 packages a value with a lazy tree of reductions so composed generators retain constraints such as positivity. **C2:** `Gen`, `Tree`, `Print`, and `Test` separate data construction, simplification, diagnostics, and execution, including recursive generators. Start with the substantive [QCheck2 interface documentation](https://github.com/c-cube/qcheck/blob/main/src/core/QCheck2.mli).
- The [changelog](https://github.com/c-cube/qcheck/blob/main/CHANGELOG.md) provides concrete migration context: renamed combinators, migration attributes, deprecation removals, and overflow fixes. Its unreleased changes should not be assumed to describe an installed release. The separate multicore testing repository below supplies the state-machine/concurrency extensions.

## State machines, concurrency, and native failure modes

### 10. [proper-testing/proper](https://github.com/proper-testing/proper)

**Language / role:** Erlang; PropEr's general property engine and `proper_statem` framework.

Study symbolic command generation followed by concrete execution. This separation allows tests to refer to resources that have not yet been created and lets shrinking reason about command validity without executing the target system.

- **C1:** preconditions are revalidated during reduction, and parallel tests are checked for a serialization consistent with observed results. The implementation also constrains generated concurrent sequences so their preconditions remain meaningful across interleavings.
- **C2:** the callback protocol—initial state, command generation, precondition, transition, and postcondition—supports arbitrary reactive systems. Symbolic variables carry results between calls, while the same model serves sequential and parallel testing.

The extensive module documentation embedded in [proper_statem.erl](https://github.com/proper-testing/proper/blob/master/src/proper_statem.erl) is both the API guide and an architectural explanation, including cleanup requirements and limits on parallel generation.

### 11. [stevana/quickcheck-state-machine](https://github.com/stevana/quickcheck-state-machine)

**Language / role:** Haskell; model-based testing of monadic programs, including parallel command histories.

Study typed symbolic/concrete references and the separation of generation, execution, shrinking, and history interpretation. This is the successor fork of the archived `advancedtelematic` repository, counted once. The maintainer describes the project as feature-complete enough for minor maintenance, with no major changes planned; see [history and current status](https://github.com/stevana/quickcheck-state-machine#history-and-current-status).

- **C1:** parallel programs require valid shrinking and repeated execution to expose nondeterministic failures. **C2:** the [parallel module](https://github.com/stevana/quickcheck-state-machine/blob/master/src/Test/StateMachine/Parallel.hs) exposes reusable generation, shrinking, execution, and linearization operations over user-defined machines.
- **C4:** the [2023–2026 changelog](https://github.com/stevana/quickcheck-state-machine/blob/master/CHANGELOG.md) documents compiler compatibility, CI restoration, dependency removal, and redesign of where repetitions happen. This establishes substantive evolution beyond simply retaining the original fork.

### 12. [emil-e/rapidcheck](https://github.com/emil-e/rapidcheck)

**Language / role:** C++; QuickCheck-style properties and command-based stateful testing.

Study the division between `Command<Model, Sut>::apply`, which changes the model, and `run`, which executes and checks the real system. The design explicitly accommodates C++ ownership and non-copyable model types.

- **C1:** preconditions must remain valid after earlier commands are shrunk away; the state passed to a command generator is only a hint, not a lasting guarantee. The framework checks command validity during both generation and reduction.
- **C2:** templated commands, command generators, and model factories apply to containers, services, or fixtures. **C3:** validating candidate sequences against a model before executing the real system avoids wasting expensive shrinking attempts on invalid programs.

The [stateful testing guide](https://github.com/emil-e/rapidcheck/blob/master/doc/state.md) explains these choices, including why immutable command objects are held through copyable shared pointers.

### 13. [ocaml-multicore/multicoretests](https://github.com/ocaml-multicore/multicoretests)

**Language / role:** OCaml; focus on reusable `qcheck-stm` and `qcheck-lin` libraries within the multicore regression-test repository.

Study how a real compiler/runtime test suite exposes general testing infrastructure. The STM subsystem provides model-based checking; the repository also supplies Lin for comparing concurrent observations with sequential behavior.

- **C1:** the [STM specification interface](https://github.com/ocaml-multicore/multicoretests/blob/main/lib/STM.mli) makes preconditions, state transitions, result types, postconditions, and cleanup explicit. Preconditions prevent shrinking from constructing invalid histories. **C2:** a module implementing that interface can be passed to reusable execution functors.
- **C3:** [STM_domain.ml](https://github.com/ocaml-multicore/multicoretests/blob/main/lib/STM_domain.ml) uses synchronized starts, repeated executions during shrinking, bounded sequence sizes, and arrays to reduce allocation during concurrent runs. These choices expose the practical tradeoff between race detection and test cost. The libraries and bundled tests count as one repository.

### 14. [silentbicycle/theft](https://github.com/silentbicycle/theft)

**Language / role:** C; callback-based property testing, custom reduction tactics, and random-bitstream autoshrinking.

Study how a C library supports shrinking without requiring a high-level generic type system. This is a historical/dormant selection: GitHub metadata showed the latest push in December 2020, although the repository was not archived.

- **C1:** optional child-process execution allows crashes and timeouts to remain reducible test failures; signal handling and child exit status affect the outcome. See [forking semantics](https://github.com/silentbicycle/theft/blob/master/doc/forking.md).
- **C2:** allocation and shrink callbacks describe application-specific values, while ordered tactics and hooks control reduction. **C3:** tried argument combinations are tracked to avoid duplicate executions, and coarse reductions precede finer ones. The [shrinking design](https://github.com/silentbicycle/theft/blob/master/doc/shrinking.md) also explains autoshrinking's random-bit recording and its generator assumptions. That document labels autoshrinking experimental; this report makes no claim that the qualification was later removed.

## JVM, .NET, BEAM, and other language ecosystems

### 15. [fscheck/FsCheck](https://github.com/fscheck/FsCheck)

**Language / role:** F# implementation serving .NET languages; general properties and an experimental model-based API.

Study how a functional engine offers both functional and fluent consumer APIs, plus the lifecycle needed to compare mutable objects with immutable models.

- **C1:** model states captured during generation and shrinking must not subsequently mutate. **C2:** `Machine`, `Setup`, and `Operation` separate fresh target construction, model transitions, preconditions, checks, and teardown. The [model-based guide](https://github.com/fscheck/FsCheck/blob/master/docs/StatefulTestingNew.fsx) explains this contract and explicitly exempts the experimental API from normal semantic-versioning expectations.
- **C4:** [release notes](https://github.com/fscheck/FsCheck/blob/master/FsCheck%20Release%20Notes.md) document the 2021–2026 transition from global mutable arbitrary lookup to configurable immutable maps, the F#/fluent API split, asynchronous properties, and evolving NUnit/xUnit compatibility.

### 16. [AnthonyLloyd/CsCheck](https://github.com/AnthonyLloyd/CsCheck)

**Language / role:** C#; randomized properties, model and metamorphic tests, and parallel testing.

Study its alternative shrinking architecture: generate a value with a composable size measure, then search for smaller failing values using randomized generation. This differs substantially from walking a fixed output shrink tree.

- **C1:** parallel tests compare observations after concurrent operations against possible sequential linearizations, optionally using a separate non-thread-safe reference model. **C2:** composable `Gen` values and operation descriptions support ordinary properties and model comparisons. The [parallel-testing documentation](https://github.com/AnthonyLloyd/CsCheck#parallel-testing) gives concrete queue examples.
- **C3:** the [design comparison](https://github.com/AnthonyLloyd/CsCheck/blob/master/docs/Comparison.md) ties the cost of repeated candidate generation to PCG and the size representation, and explains seed-based continuation of shrinking. Its claims of superiority over competitors are author claims; this selection relies on the described mechanism, not those rankings or implied global-minimum guarantees.

### 17. [jqwik-team/jqwik](https://github.com/jqwik-team/jqwik)

**Language / role:** Java, with Kotlin support; property-testing engine on the JUnit Platform.

Study a framework that embeds property generation and stateful action chains into test discovery and execution. The repository separates public APIs from engine and integration modules.

- **C1:** dependent actions generate transformations from the current state, with preconditions and postcondition checks governing legal sequences. **C2:** `Action`, `Transformer`, and `ActionChainArbitrary` let both state-dependent and independent operations compose into generated tests. The [stateful design guide](https://github.com/jqwik-team/jqwik/blob/main/documentation/src/docs/include/stateful-testing.md) explains the distinction and marks the newer interface experimental.
- **Status:** the [repository README](https://github.com/jqwik-team/jqwik#maintenance-mode) explicitly declares maintenance mode, emphasizing dependency updates and selected critical fixes. It also flags a usage-license change beginning with 1.10. This is an architectural selection, without an assertion of unrestricted licensing or ongoing feature development.

### 18. [typelevel/scalacheck](https://github.com/typelevel/scalacheck)

**Language / role:** Scala; general property testing with a substantial `Commands` stateful subsystem.

Study a typed command API that keeps mutable targets separate from immutable model states and command results. Resource lifecycle is part of the testing abstraction rather than an implicit responsibility of a surrounding fixture.

- **C1:** shrinking can change the initial state, so its precondition must be rechecked. Commands capture success or exceptions through `Try`, and the API documents that commands are treated atomically when testing in parallel.
- **C2:** `Commands` abstracts state, target construction/destruction, command generation, preconditions, transitions, and result-dependent properties. Its `canCreateNewSut` hook supports systems that cannot safely have unrestricted concurrent instances.

The heavily documented [Commands.scala](https://github.com/typelevel/scalacheck/blob/main/core/shared/src/main/scala/org/scalacheck/commands/Commands.scala) is a useful entry point for both the extension interface and its correctness assumptions.

### 19. [whatyouhide/stream_data](https://github.com/whatyouhide/stream_data)

**Language / role:** Elixir; reusable data generators and ExUnit property integration.

Study how generators can act as ordinary enumerable streams while retaining a richer internal representation for shrinking. This is included as a property-testing engine; no built-in state-machine layer is claimed.

- **C1:** shrinking is tied to each generated value, not merely to decreasing a generation-size parameter. Mapping and filtering through ordinary `Stream`/`Enum` operations loses shrinkability, an important boundary explained in [StreamData's implementation documentation](https://github.com/whatyouhide/stream_data/blob/main/lib/stream_data.ex).
- **C2:** generators compose through dedicated operations such as `bind`, while [LazyTree](https://github.com/whatyouhide/stream_data/blob/main/lib/stream_data/lazy_tree.ex) supports mapping, filtering, and flattening trees of candidate values. **C3:** children are realized lazily, and flattening allows generators to choose whether outer or inner reductions receive priority.

### 20. [hedgehogqa/r-hedgehog](https://github.com/hedgehogqa/r-hedgehog)

**Language / role:** R; integrated property testing and abstract state machines with testthat-style expectations.

Study a substantive R implementation of generator and model-based testing concepts, especially the adaptation of symbolic references to dynamically typed commands and reference classes.

- **C1:** commands that use results of earlier operations must remain valid after shrinking. The framework distinguishes symbolic outputs during generation from real outputs during execution; model updates must accommodate both. A command's requirement check protects against removal of a prerequisite operation.
- **C2:** the `command` abstraction separates argument generation, execution, model updates, requirements, and expectations; `gen.actions` and `expect_sequential` reuse that description for many stateful systems.

The [state-machine vignette](https://github.com/hedgehogqa/r-hedgehog/blob/master/vignettes/state-machines.Rmd) walks through these mechanisms with a mutable reference registry and shows why the real system must reset between generated scenarios. This is a separate R implementation, not an additional listing of the Haskell repository.

### 21. [Qqwy/ruby-prop_check](https://github.com/Qqwy/ruby-prop_check)

**Language / role:** Ruby; compositional property testing with lazy integrated shrinking.

Study the compact interaction among Ruby blocks, generators, lazy candidate trees, hooks, and exception-based failures. Its implementation is small enough to follow end to end while addressing more than random input sampling.

- **C1:** generation has a bounded retry policy for overrestrictive filters, and shrinking must preserve and report the failure while traversing candidate descendants. The [shrinker](https://github.com/Qqwy/ruby-prop_check/blob/main/lib/prop_check/property/shrinker.rb) handles exceptions, traversal state, hooks, and a maximum shrink budget.
- **C2:** a [Generator](https://github.com/Qqwy/ruby-prop_check/blob/main/lib/prop_check/generator.rb) maps size and random state to a lazy tree, with `map` and dependent `bind` transforming the reduction structure as well as the initial value. This entry concerns general properties, not an asserted concurrent or state-machine testing API.

### 22. [giorgiosironi/eris](https://github.com/giorgiosironi/eris)

**Language / role:** PHP; property-testing engine integrated with PHPUnit.

Study an engine that coordinates composite generated values, assertions, reduction conditions, listeners, and time budgets while tracking a changing host testing framework.

- **C1:** the [multiple-value shrinker](https://github.com/giorgiosironi/eris/blob/master/src/Shrinker/Multiple.php) retests candidates, rejects reductions violating configured conditions, and retains the failure when a reduction time limit is reached. **C2:** its tuple-generator, evaluation, listener, and time-limit interfaces separate reusable policies from the core search loop.
- **C4:** the [2016–2026 changelog](https://github.com/giorgiosironi/eris/blob/master/CHANGELOG.md) records generator API migrations, changes to shrinking, PHP/PHPUnit support, and concrete correctness fixes. The 2026 fixes cover integer ranges wider than the random source's native range and proper reporting of PHP `Error` failures, particularly relevant numerical and failure semantics.

### 23. [elm-explorations/test](https://github.com/elm-explorations/test)

**Language / role:** Elm with JavaScript kernel support; focus on the `Fuzz`, random-run, and simplification subsystem of the broader testing library.

Study how a property-testing engine evolved from shrinking generated-value trees to shrinking recorded PRNG decisions, enabling dependent generator composition.

- **C1:** the [simplifier](https://github.com/elm-explorations/test/blob/master/src/Simplify.elm) retains the best failing random run and generated value, repeats passes while progress is made, and removes inapplicable commands when the run becomes shorter.
- **C2:** the [changelog's architectural explanation](https://github.com/elm-explorations/test/blob/master/CHANGELOG.md#1-fuzzing-and-shrinking-reimplementation) describes how the redesign restored `Fuzz.andThen`, reduced the need for custom generators, and changed floating-point generation and shrinking to include special values and readable fractions.
- **C3:** the same changelog documents a TypedArray-based random-run representation and a Fisher–Yates shuffle with a smaller recorded footprint. These particular optimizations are listed as **unreleased**, not assumed to be available in the published package.

## Schema-driven, proof-oriented, and research frameworks

### 24. [schemathesis/schemathesis](https://github.com/schemathesis/schemathesis)

**Language / role:** Python; schema-driven property testing of OpenAPI and GraphQL APIs, built on Hypothesis.

Study the substantive layer that turns schema relationships and response data into executable workflows. It adds its own producer/consumer analysis and lifecycle machinery, so it is more than a generated wrapper around Hypothesis.

- **C1:** operations must use resources returned by earlier requests to reach failures involving updates, deletion, and dependent resources. The [stateful architecture explanation](https://github.com/schemathesis/schemathesis/blob/master/docs/explanations/stateful.md) describes schema inference, GraphQL type relationships, explicit OpenAPI links, and links learned from `Location` headers. It also distinguishes CLI-only learning from Python execution.
- **C2:** schema-derived state-machine classes expose scenario setup/teardown and per-request hooks, permitting authentication, fixtures, and customized requests without rebuilding the workflow engine. See the [stateful customization guide](https://github.com/schemathesis/schemathesis/blob/master/docs/guides/stateful-testing.md).

### 25. [QuickChick/QuickChick](https://github.com/QuickChick/QuickChick)

**Language / role:** Rocq/Coq Gallina and OCaml; property-testing plugin with derived generators, enumerators, checkers, and supporting proofs.

Study the boundary between executable testing and formal reasoning about the generators themselves. This codebase addresses constrained inductive relations, not merely arbitrary instances for ordinary record types.

- **C1:** generated partial decision procedures use explicit fuel and distinguish an undecided result from true or false. The [automation tutorial](https://github.com/QuickChick/QuickChick/blob/master/tutorials/Automation.v) explains monotonicity and soundness requirements using balanced trees.
- **C2:** typeclasses and derivation commands construct generators, shrinkers, printers, and relation checkers. The [proof-derivation tutorial](https://github.com/QuickChick/QuickChick/blob/master/tutorials/DerivingProofs.v) gives a set-of-outcomes semantics for enumerators and derives monotonicity properties. These abstractions support testing new datatypes and specifications while making the testing infrastructure itself amenable to proof.

### 26. [Bodigrim/smallcheck](https://github.com/Bodigrim/smallcheck)

**Language / role:** Haskell; bounded exhaustive property testing.

Study a deliberately different search strategy: enumerate all values within a structural-depth bound instead of sampling random inputs and shrinking failures. **Historical qualification:** the [README](https://github.com/Bodigrim/smallcheck#smallcheck-a-property-based-testing-library-for-haskell) describes the library as largely obsolete as of 2023 and recommends considering newer shrinking-based approaches. It remains useful here for architectural comparison.

- **C1:** depth has precise semantics for constructors and generated functions; newtypes and ordinary constructors must be handled differently, and enumeration order should favor shallower combinations.
- **C2:** `Serial`, `CoSerial`, generic derivation, and constructor combinators support user-defined values and functions rather than a fixed set of primitive domains.

The detailed documentation in [Series.hs](https://github.com/Bodigrim/smallcheck/blob/master/Test/SmallCheck/Series.hs) explains these mechanisms. Exhaustiveness is relative to the declared generators and bound; it is not an unbounded correctness proof.

### 27. [agroce/tstl](https://github.com/agroce/tstl)

**Language / role:** Python; Template Scripting Testing Language, harness generation, randomized action sequences, and test reduction/normalization.

Study a testing DSL that describes pools of reusable values, permitted actions, and invariants, then compiles a target-system interface used by multiple testing tools. This is a research-oriented selection: GitHub metadata showed the last push in April 2024, and the README retains qualifications about its Python 2 origins and Python 3 testing. Current-runtime compatibility was not established by execution.

- **C1:** reduction can preserve a particular exception, coverage, or evidence of nondeterminism. The [reduction driver](https://github.com/agroce/tstl/blob/master/tstl/reduce.py) constructs those predicates separately from sequence reduction, alpha conversion, and normalization.
- **C2:** the [DSL and tool documentation](https://github.com/agroce/tstl/blob/master/README.md) explains initialized value pools, differential reference pools, replay, standalone-test output, and sandbox reduction for interpreter crashes. These mechanisms support multiple target libraries and multiple search/reduction strategies.

## Coverage, search process, and limitations

Discovery used more than twenty query formulations, including general property/state-machine frameworks; C/C++ reduction; Rust and Go integrated shrinking; JVM action models; .NET concurrent testing; Erlang/Elixir generators; OCaml multicore checking; Rocq/Coq generator derivation; Ruby, R, PHP, and Swift ecosystems; bounded exhaustive Haskell testing; JavaScript asynchronous scheduling; schema-driven API sequences; and TSTL/Elm implementation searches. Later searches mostly returned additional ports, integrations, tutorials, or alternative implementations of already-covered designs. TSTL and Elm were retained because their DSL and random-run architectures added meaningful coverage, extending the initial selection to 27.

Search results and ecosystem comparison pages were discovery aids only. Retained entries were checked against GitHub repository metadata and actual source or project documentation, not justified from search snippets or star counts. Source trees were inspected before choosing entry points; an indexed CsCheck document had moved into `docs/`, and the final link uses the verified location. The old quickcheck-state-machine parent is archived; only its substantively evolved successor is listed. None of the 27 selected repository records was marked archived at the check date, but that is not evidence of continuing support: theft, TSTL, SmallCheck, jqwik, and quickcheck-state-machine carry explicit qualifications above.

The scope excludes awesome lists, demonstration-only repositories, ordinary unit-test runners without a substantive property engine, and thin bindings counted separately from their engine. It does not attempt a complete catalog of QuickCheck ports; SwiftCheck, additional Go/Rust ports, and several other language implementations were discovered but not promoted merely to increase language or repository counts. Specialized security fuzzers, distributed-system fault-injection platforms, and general model checkers were kept outside this selection unless their property/stateful framework was the central subject. Schemathesis is retained because its schema analysis and state-machine construction are substantive; broader test repositories such as multicoretests and elm-explorations/test are included only for their identified reusable subsystems.

The criterion assignments are grounded engineering judgments from the inspected mechanisms. No candidate code was executed, dependencies installed, benchmark results independently reproduced, or external services modified. The report therefore establishes source-level study value, not comparative bug-finding effectiveness, maintenance responsiveness, or universal compatibility. In particular, shrinking descriptions do not imply a guaranteed globally smallest counterexample, and randomized concurrency checks do not establish exhaustive schedule coverage.
