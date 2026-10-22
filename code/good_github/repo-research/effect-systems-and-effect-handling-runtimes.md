# Effect systems and effect handling runtimes

Research date: **2026-10-09**

This report selects **24 GitHub repositories** spanning languages with effect typing, algebraic effect handlers, native continuation machinery, extensible effect libraries, and runtimes for typed effectful programs. These are related but different designs: a library that models errors, environments, and asynchronous execution does not necessarily offer user-defined resumable operations. For compiler and library monorepos, the discussion identifies the relevant subsystem; each repository is counted once.

The selection is intended for experienced engineers studying implementation choices and their consequences. Inclusion means that the inspected material supports at least two criteria below, not that every component has been audited or that every research implementation is suitable for production.

Criteria legend:

- **C1 — Difficult correctness:** substantive invariants involving typing, continuation lifetime, concurrency, resource cleanup, or failure behavior.
- **C2 — Reusable abstractions:** mechanisms that support multiple effects, interpreters, or application domains.
- **C3 — Performance with structure:** concrete treatment of allocation, dispatch, stack use, scheduling, or other performance constraints through an understandable architecture.
- **C4 — Sustained evolution:** evidence of development over years together with compatibility work, testing, or complexity management. Age and recent pushes alone do not establish this criterion.

## Languages and their effect implementations

### [koka-lang/koka](https://github.com/koka-lang/koka)

**Language/role:** Haskell compiler, Koka libraries, and C runtime; a research language with inferred effect types and algebraic handlers. Study how a language-level effect discipline reaches an ordinary native backend, rather than stopping at a source-level interpreter.

- **C1:** The language makes effect information part of function types and supports polymorphic effect rows. Its handler examples expose resumption and handler composition, making the preservation of effect information across higher-order functions a central compiler obligation. The [language tour](https://github.com/koka-lang/koka/blob/dev/doc/spec/tour.kk.md) is the best semantic entry point.
- **C2:** User-defined operations and handlers provide a common abstraction for control and stateful computations rather than separate hard-coded language constructs for each use case.
- **C3:** The implementation research describes a staged translation through generalized evidence passing, yield bubbling, and a monadic translation, implemented in Koka's C backend. This is concrete architecture for reducing handler overhead; no numerical speed comparison is assumed here. See [Generalized Evidence Passing for Effect Handlers](https://www.microsoft.com/en-us/research/publication/generalized-evidence-passing-for-effect-handlers/).

The repository describes Koka as a research language; its inclusion is not a production-readiness claim.

### [effekt-lang/effekt](https://github.com/effekt-lang/effekt)

**Language/role:** Scala compiler and language tooling; effects implemented through lexically scoped capabilities. Particularly useful for comparing effect requirements with the capabilities that a closure actually captures.

- **C1:** The [capture documentation](https://effekt-lang.org/tour/captures) explains how second-class computations and capture annotations on boxed values prevent capabilities from escaping their valid scope. These are lifetime and typing invariants with direct consequences for first-class functions.
- **C2:** Effects describe capabilities that callers must supply, while higher-order functions can remain abstract over the effects of supplied blocks. The [effect-safety explanation](https://effekt-lang.org/docs/concepts/effect-safety) carefully distinguishes this relative purity from unrestricted referential transparency. That distinction makes the design useful for reusable control abstractions and restricted callbacks.

This is a research language implementation. Read the capture rules alongside the effect syntax; treating its effect annotations as interchangeable with conventional effect rows misses an important design choice.

### [matijapretnar/eff](https://github.com/matijapretnar/eff)

**Language/role:** OCaml implementation of Eff, an ML-like language centered on first-class effect handlers. Its compact evaluator is a useful bridge between formal handler semantics and executable code.

- **C1:** In the [runtime evaluator](https://github.com/matijapretnar/eff/blob/master/src/05-backends/runtime/eval.ml), computations return either values or operation calls carrying continuations. Sequencing composes those continuations; handling wraps resumed computations in the handler again, forwards unmatched operations, and sequences the final clause. Nested handling and finalization order are therefore explicit, inspectable correctness obligations.
- **C2:** The same handler machinery supports state, nondeterministic computations, and alternative interpretations of operations. The author's [handler tutorial](https://www.eff-lang.org/handlers-tutorial.pdf) develops these patterns and their operational semantics.

The repository's README explicitly says its types do not express computational effects. Do not confuse the existence of handlers, or related type-and-effect research, with a claim that this implementation statically tracks every effect.

### [links-lang/links](https://github.com/links-lang/links)

**Language/role:** Primarily OCaml; a research language spanning browser, server, and database programming. The relevant parts are effect rows, handler compilation/runtime behavior, and their interaction with session-typed communication.

- **C1:** The [0.9.8 release documentation](https://github.com/links-lang/links/releases) describes optional control-flow linearity checking that addresses a soundness bug involving exceptions, multi-shot handlers, and session-typed channels. This is an unusually concrete example of why duplicating or discarding continuations can conflict with linear resources. The flag is optional; the report does not assume it is always enabled.
- **C2:** Effect signatures and aliases describe reusable families of operations, while handlers are available in a language that also crosses client/server boundaries. The same release history documents effect aliases and shows how an effect row can be abstracted and reused in function types.

The [repository overview](https://github.com/links-lang/links#readme) provides the broader multi-tier architecture. Release notes also document handler-syntax changes and OCaml compatibility work, making them a useful companion when comparing examples from different versions.

### [unisonweb/unison](https://github.com/unisonweb/unison)

**Language/role:** Haskell compiler/runtime monorepo; focus on Unison abilities and `unison-runtime`, not the entire codebase-management system. Study the connection between typed requests and an explicit continuation machine.

- **C1:** The [runtime machine](https://github.com/unisonweb/unison/blob/trunk/unison-runtime/src/Unison/Runtime/Machine.hs) documents how `splitCont` walks continuation frames and captures matching data-stack segments. Pending arguments from over-applied functions must be recorded and restored correctly. Resumption also restores handler environments and rejects impossible captured frame forms.
- **C2:** The [ability-handler reference](https://www.unison-lang.org/docs/language-reference/ability-handlers/) describes `handle` in terms of typed requests and result types. Operations can be interpreted by different handlers while unhandled abilities remain requirements of the surrounding computation.

This entry is about the language's ability subsystem. The repository also contains historical runtime design notes; the concrete implementation claims above are grounded in the machine source rather than treating those older notes as current architecture.

### [flix/flix](https://github.com/flix/flix)

**Language/role:** Scala compiler for the JVM-targeting Flix language. An especially useful codebase for effect inference and constraint solving, alongside user-defined handlers.

- **C1:** The [effect unifier](https://github.com/flix/flix/blob/master/main/src/ca/uwaterloo/flix/language/phase/unification/EffUnification3.scala) translates type constraints into set equations, distinguishes rigid from flexible atoms, and states a critical precondition: saturated occurrences of a polymorphic effect constructor must already have identical type arguments. Incorrect staging between ordinary type unification and effect unification would violate that invariant.
- **C2:** [Polymorphic effects](https://doc.flix.dev/polymorphic-effects.html) parameterize operations such as emission by their value type and let handlers remove that effect from a larger set. The documentation also states restrictions on multiple instantiations, which are useful limits to study rather than hide.
- **C3:** The unifier first attempts simpler solutions and bounds polynomial simplification by a variable-count threshold. Its phase separation exposes how inference cost is managed without making every type constraint follow the most expensive path.

Polymorphic effects are documented as experimental. Development-branch implementation details can advance ahead of published language-guide descriptions.

## Native continuations and direct-style runtimes

### [ocaml/ocaml](https://github.com/ocaml/ocaml)

**Language/role:** OCaml compiler and C runtime; focus on OCaml 5 effect primitives and continuation management. This is the underlying control mechanism, not an application scheduler.

- **C1:** The [effect-handler manual](https://ocaml.org/manual/5.3/effects.html) specifies one-shot continuations: a second resumption raises `Continuation_already_resumed`. It also explains why a captured continuation should be resumed or discontinued to release resources, and distinguishes deep handlers from shallow handlers that must explicitly arrange subsequent handling.
- **C2:** These primitives allow libraries to implement direct-style concurrency and other control abstractions without requiring a separate built-in construct for every scheduling policy. The manual walks through both handler styles and their control behavior.
- **C3:** The manual connects the one-shot restriction to avoiding continuation copying. This is a deliberate performance/expressiveness tradeoff, not a claim of general multi-shot support.

The cited manual is explicitly versioned. OCaml's runtime enforcement of continuation use should not be mistaken for a static effect-safety guarantee.

### [ocaml-multicore/eio](https://github.com/ocaml-multicore/eio)

**Language/role:** OCaml direct-style I/O and structured concurrency built on effect handlers. Relevant subsystems include fibers, switches, cancellation contexts, and backend-independent I/O interfaces.

- **C1:** The [repository's architecture and cancellation documentation](https://github.com/ocaml-multicore/eio#readme) explains how switches own fibers and resources, how failure propagates through cancellation contexts, and where cancellation protection is needed during cleanup. Correctness includes waiting for owned work and releasing resources under failure, rather than merely starting asynchronous operations.
- **C2:** Capability-oriented interfaces let applications use flows, networking, and files through common APIs while platform backends supply the actual I/O operations. The scheduler and resource model can therefore support many application domains.
- **C1, additional concurrency evidence:** The [multicore guide](https://github.com/ocaml-multicore/eio/blob/main/doc/multicore.md) distinguishes cooperatively scheduled fibers from parallel domains and explains shared-memory races and ordering. It is a valuable companion to the effect-based API because direct-style syntax does not remove multicore hazards.

Cancellation is cooperative at appropriate operation boundaries; the documentation does not promise that racing external I/O becomes an exactly-once transaction.

### [koka-lang/libhandler](https://github.com/koka-lang/libhandler)

**Language/role:** C99/C++ library implementing algebraic effect handlers through captured execution contexts. A research implementation associated with the 2017 paper on handlers in C.

- **C1:** The [repository implementation notes](https://github.com/koka-lang/libhandler#readme) discuss stack capture and platform assumptions, as well as interaction with C++ exception unwinding and destructors. Continuation lifetime and cleanup across nonlocal control transfer are the main engineering issues to inspect.
- **C2:** The library exposes operations and handlers as a general control abstraction usable from ordinary C functions, rather than requiring an interpreter for a separate language.
- **C3:** The authors' [implementation paper page](https://www.microsoft.com/en-us/research/publication/implementing-algebraic-effects-c/) describes operational semantics guiding the C implementation and an extension for efficiently implementing tail resumptions. The value here is the explicit relationship between handler semantics and fast paths; this report does not repeat its benchmark ratios.

Treat this as a research-origin implementation with documented portability assumptions, not as evidence that arbitrary C/C++ stacks can safely be copied under every toolchain.

### [koka-lang/libmprompt](https://github.com/koka-lang/libmprompt)

**Language/role:** C/C++ multi-prompt delimited-control runtime, with the higher-level `libmpeff` effect-handler layer in the same repository. These layers count as one project.

- **C1:** The [`mpeff.h` interface](https://github.com/koka-lang/libmprompt/blob/main/include/mpeff.h) makes continuation lifetime distinctions explicit: scoped versus escaping resumptions, one-shot versus multi-shot operation kinds, tail resumptions, and release/finalization operations. It also documents tag identity and operation-index requirements that callers must preserve.
- **C2:** Prompt/continuation primitives form a lower layer, while effect definitions and handler dispatch form a reusable higher layer. The [source layout note](https://github.com/koka-lang/libmprompt/blob/main/src/readme.md) explains that separation.
- **C3:** The repository describes growable stacks backed by reserved virtual address space, committing memory as needed while keeping stack addresses stable. Operation kinds let the handler layer exploit more restrictive resumption behavior instead of paying uniformly for the most general case.

The README explicitly describes the library as not production ready. Its listed releases are historical evidence of the implementation, not a basis for claiming current production support.

### [effect-handlers/libseff](https://github.com/effect-handlers/libseff)

**Language/role:** C and assembly; lightweight shallow effect handlers using mutable coroutines. This research artifact offers a markedly different stack and request representation from copying continuations.

- **C1:** The authors' [libseff paper](https://homepages.inf.ed.ac.uk/slindley/papers/libseff.pdf) explains the linear-use discipline around mutable coroutines and the effect-tag conventions used by dispatch. Those obligations matter: the C interface cannot universally prevent a caller from misusing coroutine state or conflicting tags.
- **C2:** Reified requests let ordinary C code dispatch and handle operations, supporting reusable control abstractions and schedulers without requiring heap-allocated handler closures for every case.
- **C3:** The paper grounds the design in mutable continuation state, avoiding a fresh immutable continuation allocation for each operation, and in segmented stacks. It explicitly contrasts the stack strategy with virtual-address-reservation approaches. The [repository](https://github.com/effect-handlers/libseff#readme) supplies the implementation, tests, and benchmarks accompanying this design.

This is a research implementation; the paper's performance evaluation is evidence of engineering attention, not a benchmark independently reproduced for this report.

## Typed effect programs and fiber interpreters

### [zio/zio](https://github.com/zio/zio)

**Language/role:** Scala effect library and fiber runtime. Its central abstraction represents an effectful program with environment, error, and result types; it is not the same interface as an algebraic handler with arbitrary continuation access.

- **C1:** The [runtime reference](https://zio.dev/reference/core/runtime/) describes the interpreter's responsibilities for asynchronous execution, error handling, fiber execution, and finalization. Scoped runtime configuration must also be inherited and restored correctly, creating correctness obligations beyond evaluating a simple monadic expression.
- **C2:** A `ZIO[R, E, A]` program is a value interpreted by a `Runtime[R]`, separating reusable program construction from its environment and execution machinery. Runtime construction through layers supports different application configurations.
- **C3:** The same reference explains the interpreter loop, thread-pool execution, and cooperative yielding. This makes ZIO valuable for studying how a structured program representation becomes scheduled work with fairness and cleanup concerns.

Start with the runtime reference before exploring the much larger collection of application-facing combinators in the monorepo.

### [typelevel/cats-effect](https://github.com/typelevel/cats-effect)

**Language/role:** Scala effect type classes and the `IO` runtime. The `core` fiber interpreter is the principal subsystem for this category; generic abstractions in the repository support implementations beyond `IO` itself.

- **C1:** [`IOFiber.scala`](https://raw.githubusercontent.com/typelevel/cats-effect/series/3.x/core/shared/src/main/scala/cats/effect/IOFiber.scala) documents the invariant that only one thread owns a fiber run loop at a time. Its atomic suspended state and executor handoffs provide publication barriers for otherwise nonvolatile interpreter state. Cancellation, join callbacks, and finalizer execution interact with that ownership protocol.
- **C2:** The [repository overview](https://github.com/typelevel/cats-effect#readme) distinguishes reusable effect capabilities from the concrete runtime, allowing resource management and concurrent programs to target an abstraction rather than hard-code one interpreter.
- **C3:** The same fiber source uses explicit continuation stacks, cancellation checks, and automatic yielding. Comments explain why additional barriers can be avoided under the ownership invariant, making this an unusually useful performance-and-correctness study.

The source link deliberately targets the `3.x` series. It provides implementation evidence, not a guarantee that every version uses identical internals.

### [getkyo/kyo](https://github.com/getkyo/kyo)

**Language/role:** Scala 3 effects toolkit; focus on `kyo-kernel` and its relationship to the higher-level runtime. The kernel distinguishes operations that suspend a continuation from contextual effects that supply values.

- **C1:** The [kernel guide](https://github.com/getkyo/kyo/blob/main/kyo-kernel/README.md) documents resource-region issues when a continuation is replayed after its bracket has closed. Its handling APIs distinguish ordinary continuation handling from repeated handling that must reacquire resources. Stack safety also requires cooperation with suspension and safepoints.
- **C2:** `ArrowEffect` and `ContextEffect` provide different reusable mechanisms for defining effects, while the effect parameter records what remains to be handled. This is more specific than a fixed catalog of asynchronous operations.
- **C3:** The kernel guide connects trampolining to periodic safepoints and explains how `Loop` can reuse continuation structure across iterations. These mechanisms expose the cost model behind nested effectful computation.

The [repository overview](https://github.com/getkyo/kyo#readme) situates the kernel within the broader toolkit. Handler order and repeated resumptions have semantic consequences; concise effect syntax does not eliminate them.

### [atnos-org/eff](https://github.com/atnos-org/eff)

**Language/role:** Scala extensible effects library using typed collections of effects and interpreters. This supplies an open effect vocabulary, unlike a runtime restricted to one built-in effect representation.

- **C2:** The [interpreter construction guide](https://atnos-org.github.io/eff/org.atnos.site.CreateEffects.html) shows operation injection, continuation-based interpretation, and `Member.Aux` evidence that removing one effect from the input collection produces the remaining collection. Interpreters can stop, resume, or translate operations, supporting application-specific DSLs.
- **C3:** The [applicative execution guide](https://atnos-org.github.io/eff/org.atnos.site.ApplicativeEvaluation.html) distinguishes sequential monadic traversal from applicative traversal that can run independent future effects concurrently. The interpreter interface has a separate `onApplicative` path, so this performance opportunity is represented structurally rather than guessed from arbitrary sequential code.

This is useful for studying the relationship between type-level effect membership, interpreter composition, and available parallelism. Its documentation also records Scala inference limitations; use the examples as version-sensitive API material.

### [Effect-TS/effect](https://github.com/Effect-TS/effect)

**Language/role:** TypeScript monorepo; focus on the core effect interpreter, fibers, scopes, and resource handling. Its typed effect values combine success, error, and environmental requirements for application programs.

- **C1:** The [fiber guide](https://effect.website/docs/v4/concurrency/fibers) explains interruption boundaries, protected regions, and finalization. In particular, interrupting a fiber waits for finalizers and full termination; distinguishing an interruption signal from completed teardown is a significant lifecycle invariant.
- **C2:** The [repository overview](https://github.com/Effect-TS/effect#readme) describes a common effect abstraction supporting error handling, dependency requirements, and concurrency. The fiber guide shows different lifetime relationships through child, scoped, and detached work, letting applications express ownership policies rather than manage every promise manually.

The inspected guide is the explicitly versioned v4 documentation. This entry concerns effectful-program interpretation and structured concurrency, not a claim that TypeScript has acquired native algebraic effect handlers.

### [thefrontside/effection](https://github.com/thefrontside/effection)

**Language/role:** TypeScript structured-concurrency runtime using generator-based operations. A useful contrast with both promise-centric APIs and deeply nested typed effect expression trees.

- **C1:** The [task implementation](https://raw.githubusercontent.com/thefrontside/effection/v4/lib/task.ts) ties child tasks to owners, makes interruption settle through unwinding, and routes unhandled failures through the owning context. Removing a task from its group and halting owned work are explicit lifecycle operations rather than incidental promise callbacks.
- **C2:** The [resource implementation](https://raw.githubusercontent.com/thefrontside/effection/v4/lib/resource.ts) supplies a reusable protocol in which initialization provides a value while the resource operation remains alive until its caller's scope ends. The same protocol accommodates sockets and other resources with asynchronous cleanup.

These entry points are on the `v4` branch. The attraction is the small set of operation, task, and ownership mechanisms; resource cleanup still depends on participating in their scope protocol.

## Extensible effects and capabilities in Haskell

### [haskell-effectful/effectful](https://github.com/haskell-effectful/effectful)

**Language/role:** Haskell effect library using a concrete environment over `IO`, with static and dynamic dispatch. Study the deliberate tradeoff between general continuation manipulation and predictable interaction with existing Haskell I/O.

- **C1:** The [architecture discussion](https://github.com/haskell-effectful/effectful#readme) addresses preservation of state updates when exceptions occur and distinguishes thread-local from shared state. Its concrete representation is motivated partly by avoiding surprising interactions between state, exceptions, and transformer-style unlifting.
- **C2:** Static and dynamic dispatch offer reusable effect interfaces with different implementation choices, while the `IO` foundation supports integration with existing exception and concurrency libraries. This is not a general multi-shot continuation system.
- **C3:** The [benchmark methodology](https://github.com/haskell-effectful/effectful/blob/master/benchmarks/README.md) separates tight dispatch-heavy workloads from file-oriented workloads and tests both shallow and deeper effect environments. It uses non-inlining boundaries to avoid making whole-program specialization look like ordinary library performance. That methodology is stronger evidence than simply quoting a benchmark winner.

No speed ratios are reproduced here; compiler version, inlining, and workload materially affect comparisons.

### [coclique/cleff](https://github.com/coclique/cleff)

**Language/role:** Haskell extensible effects using an `IO`-based environment with higher-order handlers. The canonical repository is `coclique/cleff`; the older `re-xyr/cleff` address redirects here and is not counted separately.

- **C1:** The [internal monad implementation](https://github.com/coclique/cleff/blob/master/src/Cleff/Internal/Monad.hs) separates the effect stack's handler pointers from a vector of stored handlers. Its commentary distinguishes changing a pointer for global reinterpretation from replacing a handler for local behavior. Preserving the correct scope for higher-order operations is a substantive invariant, not merely a type synonym choice.
- **C2:** `Eff` programs share one environment representation while handlers interpret application-specific operations. The [repository guide](https://github.com/coclique/cleff#readme) explains higher-order effect support and interaction with ordinary `IO`, allowing domain DSLs and local interpretation to use a common mechanism.

This entry is particularly useful alongside effectful: both choose a concrete I/O foundation, but the inspected handler-environment design gives a distinct implementation to study. No maintenance-status conclusion is inferred from the ownership change.

### [polysemy-research/polysemy](https://github.com/polysemy-research/polysemy)

**Language/role:** Haskell higher-order extensible effects. Study the separation between a polymorphic program representation and interpreters that must account for embedded computations and finalization semantics.

- **C1:** [`Polysemy.Resource`](https://github.com/polysemy-research/polysemy/blob/master/src/Polysemy/Resource.hs) implements bracket operations and distinguishes ordinary higher-order interpretation from final interpretation into `IO`. The source explicitly warns about local-state semantics for other interpreted effects and uses inspection of results to account for short-circuiting behavior.
- **C2:** The [`Sem` implementation](https://github.com/polysemy-research/polysemy/blob/master/src/Polysemy/Internal.hs) represents programs through a polymorphic interpreter over an open union of effects. Together with higher-order interpretation, that supports reusable operations that themselves contain effectful computations.

The README candidly withdraws earlier broad zero-cost performance expectations for programs where cross-module inlining does not scale. This makes Polysemy a valuable semantic and abstraction study without requiring an unsupported performance endorsement.

### [fused-effects/fused-effects](https://github.com/fused-effects/fused-effects)

**Language/role:** Haskell effect signatures and carrier algebras. Its central design interprets effects through composed carriers instead of building and repeatedly traversing an intermediate free-program tree.

- **C2:** [`Control.Algebra`](https://raw.githubusercontent.com/fused-effects/fused-effects/main/src/Control/Algebra.hs) makes the relationship between an effect signature, a carrier monad, and the handling of embedded computations explicit. Context threading is part of the algebra interface, enabling higher-order operations as well as simple requests.
- **C3:** Carrier composition and fusion are deliberate mechanisms for removing intermediate interpretation structure. The algebra interface is a useful architectural entry point for understanding what must inline or specialize for that approach to pay off.
- **C1:** The [changelog](https://github.com/fused-effects/fused-effects/blob/main/ChangeLog.md) records fixes for duplicated state in strict and Church-encoded state carriers and for accumulator strictness. It also records compiler-compatibility and inspection-testing updates. These are concrete examples of semantic and evaluation-order problems that optimized carriers must manage.

This selection does not turn the project's name into a blanket performance claim: compiler optimization and the selected carrier still matter.

### [lexi-lambda/freer-simple](https://github.com/lexi-lambda/freer-simple)

**Language/role:** Haskell extensible effects with a freer representation. Particularly useful as a comparatively compact implementation of operation requests plus queued continuations.

- **C2:** The [freer internals](https://github.com/lexi-lambda/freer-simple/blob/master/src/Control/Monad/Freer/Internal.hs) distinguish a completed value from an effect in an open union accompanied by its continuation queue. This representation lets effect-specific interpreters operate on reusable programs without requiring every effect to be a functor.
- **C3:** The [type-aligned queue](https://github.com/lexi-lambda/freer-simple/blob/master/src/Data/FTCQueue.hs) stores composable arrows in a tree, supports efficient append, and reorganizes the tree when viewing from the left. It addresses the cost of repeatedly associating binds rather than leaving continuation composition as a naïvely nested function structure.
- **C1:** The queue's GADT connects the output type of each continuation with the input type of the next, while existential intermediate types remain hidden. The data structure is therefore a useful joint study of an execution invariant and its typed representation.

The repository is retained for its substantive implementation, without assuming a current maintenance cadence from its historical influence.

### [tomjaguarpaw/bluefin](https://github.com/tomjaguarpaw/bluefin)

**Language/role:** Haskell effect system organized around explicit value-level handles. A useful counterpoint to libraries that resolve an effect entirely from a type-level list.

- **C1:** The [main library documentation and implementation overview](https://github.com/tomjaguarpaw/bluefin/blob/master/bluefin/src/Bluefin.hs) explains the ST-like use of type parameters to prevent handles from escaping their scope. This is essential to the pure runner's contract because the internal computation representation is based on `IO`.
- **C2:** Explicit handles distinguish multiple resources with otherwise similar types and can be passed directly to reusable operations. The [repository introduction](https://github.com/tomjaguarpaw/bluefin#readme) presents this approach across state, exceptions, streams, and I/O-style capabilities.

Bluefin's design does not provide general multi-shot continuation handling. Its study value lies in capability identity, scoped access, and the boundary between an efficient implementation and the guarantees of the public API.

## Rust coroutine-based typed handlers

### [rosefromthedead/effing-mad](https://github.com/rosefromthedead/effing-mad)

**Language/role:** Rust library and procedural macros using nightly coroutine features; the core is `no_std`. This is an experimental implementation of typed operation suspension and handler composition, not a stable-language effect feature.

- **C1:** The [core implementation](https://github.com/rosefromthedead/effing-mad/blob/main/src/lib.rs) pins underlying coroutines and routes yielded effects and resume values through typed coproducts. `run` accepts a computation with an uninhabited yield type. The grouped-handler API also documents a remaining obligation: returning an injection for the wrong effect can cause a panic. This is an informative boundary between static representation and dynamic protocol correctness.
- **C2:** Handlers can resume or terminate computations, remove individual or grouped effects, or transform one effect into other effects. The same core source supplies asynchronous handlers and describes conversion between futures and effectful computations, extending the mechanism beyond a single toy interpreter.

The [repository](https://github.com/rosefromthedead/effing-mad#readme) and feature gates establish the nightly requirement. No claim of stable compiler compatibility, production maturity, or competitive performance is made.

## Coverage, search method, and limitations

Discovery used live web searches with separate formulations for: (1) effect-oriented languages such as Koka, Effekt, Eff, and Links; (2) Haskell extensible effects, higher-order handlers, and explicit handles; (3) Scala effect libraries and fiber runtimes; (4) C/C++ stack capture, multi-prompt control, and shallow handlers; (5) TypeScript effect runtimes and structured concurrency; (6) OCaml effects, Eio cancellation, and multicore behavior; (7) Unison abilities and Flix effect inference; and (8) Rust coroutine handlers, plus a broader Kotlin/C++/Rust follow-up. Follow-up searches targeted implementation papers, resource semantics, source files, release notes, and compiler compatibility. Later broad searches increasingly returned already examined projects, introductory demonstrations, or adjacent coroutine systems.

Every retained repository's canonical GitHub page was opened, and at least one additional primary source was read. Evidence includes official language references, source implementations, project-maintained architecture notes, authors' implementation papers, and changelogs. GitHub content retrieval was used when browser source views were unavailable. Source links deliberately identify inspected branches or versioned manuals where relevant; documentation and development branches can differ. No repository code or benchmarks were executed.

The selection spans different scales and mechanisms: full language toolchains, native stack machinery, small effect kernels, open effect unions, explicit capability handles, generator operations, and large concurrent runtimes. It includes research artifacts and less prominent substantive implementations, while retaining established libraries for their concrete runtime engineering. The three Koka-organization repositories are separate compiler and native-library implementations; `libmpeff` is a subsystem of libmprompt and is not counted again. Monorepos likewise appear once.

Comparison repositories such as effects-rosetta-stone and effect-handler benchmark collections were useful discovery leads but are not counted as independent reusable runtimes. Tutorial gists, proposal-only repositories, generated wrappers, and general async libraries without a sufficiently central effect-system or handler implementation were excluded. Rust coverage is selective: follow-up searches found additional alternatives, including corophage and reffect, but this report does not claim to have independently evaluated every such project. The report is also not an exhaustive survey of Scheme/Racket control operators or every language with an effect annotation.

Criteria assignments are engineering judgments grounded in the cited mechanisms; they are not formal verification results. C4 is defined for completeness but is not awarded solely from release counts, old origin dates, compiler-version lists, or current activity. The strongest inspected evidence for these entries concerns C1–C3. Research and experimental limitations are identified individually, and no entry should be read as an implied promise of active maintenance. Performance discussion identifies designs and evaluation methods rather than unsupported cross-project rankings.
