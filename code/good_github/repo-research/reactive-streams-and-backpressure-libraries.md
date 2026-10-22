# Reactive streams and backpressure libraries

Research date: **2026-10-09**

This selection covers 26 GitHub repositories implementing composable event streams, demand protocols, pull-based streaming, or suspension-based backpressure. It includes the JVM Reactive Streams contract and TCK, several substantial streaming subsystems inside larger repositories, and two important push-observable libraries whose limits are explicitly distinguished from backpressure. It excludes distributed streaming platforms, message brokers, application examples, and thin integration wrappers.

The criteria below are engineering assessments grounded in the linked primary material, not certifications of correctness or recommendations to adopt every project. Documentation and branches are identified where version differences matter. Inclusion does not imply a particular current maintenance cadence.

## Criteria legend

- **C1 — Difficult correctness:** concurrency, ordering, cancellation, resource lifetime, numerical invariants, or failure handling.
- **C2 — Reusable abstractions:** substantial protocols, operators, or composition mechanisms useful across applications.
- **C3 — Performance with structure:** explicit treatment of allocation, scheduling, buffering, throughput, or bounded resource use within an understandable design.
- **C4 — Sustained evolution:** multiple years of changes with concrete compatibility, testing, or complexity-management evidence.

## Demand protocols and JVM operator engines

### 1. [reactive-streams/reactive-streams-jvm](https://github.com/reactive-streams/reactive-streams-jvm)

**Java; interoperability specification, executable conformance kit, and examples.** This is supporting infrastructure rather than a full operator library. It is the best starting point for understanding the obligations that demand-aware libraries must preserve across asynchronous boundaries.

- **C1:** The specification defines emission-versus-request accounting, serialized signals, reentrant requests, bounded recursion, eventual cancellation, and terminal-state rules. The TCK turns important obligations into adversarial checks, including unsolicited emissions and overlapping callbacks. Read the [normative contract](https://github.com/reactive-streams/reactive-streams-jvm#specification) alongside [PublisherVerification.java](https://raw.githubusercontent.com/reactive-streams/reactive-streams-jvm/master/tck/src/main/java/org/reactivestreams/tck/PublisherVerification.java).
- **C2:** Four small interfaces separate data transport and demand from application operators and scheduling. The reusable TCK lets independently implemented publishers validate a shared contract. Passing it is useful evidence, not a proof covering every possible interleaving.

### 2. [reactor/reactor-core](https://github.com/reactor/reactor-core)

**Java; Reactor's Flux/Mono operator engine and testing support.** Study how local operators transform a global demand budget, particularly when batching and nested publishers change the units being requested.

- **C1:** `BaseSubscriber` enforces single-use subscription behavior; insufficient demand can stall a pipeline; cancellation need not immediately stop an already running source. These are concrete lifecycle and progress constraints in the [reference guide](https://docs.spring.io/projectreactor/reactor-core/docs/current/reference/html/#_on_backpressure_and_ways_to_reshape_requests).
- **C2:** `Flux`, `Mono`, schedulers, programmable sources, and testing facilities form reusable asynchronous composition machinery.
- **C3:** Buffer operators multiply demand, inner publishers use prefetch and replenishment, and `limitRate` divides requests into batches. These mechanisms make queue size and request overhead visible design choices. The same guide explains why callback bridges using unbounded buffering can still exhaust memory.

### 3. [ReactiveX/RxJava](https://github.com/ReactiveX/RxJava)

**Java; ReactiveX operators, including backpressured Flowable streams.** A particularly valuable implementation study for the mechanics behind seemingly simple operators. The entry point below explicitly documents the **2.x operator architecture**; check the chosen branch before treating internal names as current APIs.

- **C1:** Request accounting uses atomic updates and overflow-aware arithmetic; deferred requests and cancellation must survive subscriptions arriving late; terminal signals require coordination. The [operator-writing guide](https://github.com/ReactiveX/RxJava/wiki/Writing-operators-for-2.0) explains these races with code.
- **C2:** Separate sequence types distinguish many-item, optional, single-result, and completion-only computations. `Flowable` carries demand semantics; `Observable` does not acquire backpressure merely by being reactive.
- **C3:** Queue-drain serialization, work-in-progress counters, and specialized single-producer queues expose the tradeoffs among allocation, synchronization, and signal ordering. These are inspectable mechanisms rather than unsupported benchmark claims.

### 4. [smallrye/smallrye-mutiny](https://github.com/smallrye/smallrye-mutiny)

**Java; Uni/Multi pipelines organized around event-specific operator groups.** Useful for studying how a substantial reactive engine can expose demand control through a discoverable API rather than requiring every caller to implement a subscriber.

- **C1:** Demand capping must preserve outstanding demand; custom capping functions have a positive, upper-bounded result invariant. Pausing leaves already requested items in flight, so pause handling needs an explicit buffering policy. The [demand-control guide](https://smallrye.io/smallrye-mutiny/latest/guides/controlling-demand/) explains these cases and shows assertions.
- **C2:** Pacing, capping, and pausing are reusable operators around `Multi`; `Uni` models single asynchronous outcomes, and converters support other reactive libraries. The repository documents both Java Flow and earlier Reactive Streams baselines and their TCK compliance, making interoperability boundaries visible.

### 5. [apple/servicetalk](https://github.com/apple/servicetalk)

**Java; focus on `servicetalk-concurrent-api` and its networking integration.** This monorepo counts once. Unlike a thin adapter over another operator library, ServiceTalk documents its own operators and the reasons for implementing them.

- **C1:** End-to-end demand propagation must coexist with error propagation, executor boundaries, and ordered network flushes. Its [performance/design document](https://apple.github.io/servicetalk/servicetalk/0.41/performance.html) explains why asynchronous transformations must preserve flush ordering.
- **C2:** Publisher-style operators connect reusable asynchronous computations to HTTP and other protocol APIs, with separate adapters for Reactive Streams.
- **C3:** The same versioned design document discusses minimizing operator allocation and synchronization, executor affinity, batching versus latency, and copying reference-counted buffers at public boundaries. It is unusually candid about safety/performance tradeoffs. Treat its version-specific tuning details as a study of that documented release.

### 6. [apache/pekko](https://github.com/apache/pekko)

**Scala/Java; the Pekko Streams subsystem, GraphStage, and stream testkits.** Pekko is an Apache continuation forked from Akka 2.6.x, as its repository explains. Akka is not counted separately here, avoiding duplication of this implementation lineage.

- **C1:** A stage may push only after downstream demand. Reusable `GraphStage` definitions must remain immutable, while each materialization receives separate mutable `GraphStageLogic`. The [custom-stage guide](https://pekko.apache.org/docs/pekko/current/stream/stream-customize.html) explains port state, cancellation, callbacks, and lifecycle handling.
- **C2:** Sources, sinks, flows, graph junctions, and materialization separate reusable topology from running state. Study this when linear operator chains are insufficient.
- **C3:** Asynchronous boundaries use windowed, batched demand to amortize communication costs; per-operator buffers can also change observable timing behavior. The [buffering and rate guide](https://pekko.apache.org/docs/pekko/current/stream/stream-rate.html) explains both effects. The repository separates stream tests, TCK tests, and the stream testkit from the runtime.

## Functional effects, pull streams, and acknowledgement protocols

### 7. [typelevel/fs2](https://github.com/typelevel/fs2)

**Scala; effect-polymorphic streaming I/O.** Study the relationship among `Stream`, `Pull`, chunks, and scoped effects instead of assuming that all streaming composition must use subscriber callbacks.

- **C1:** `bracket` introduces resource cleanup with documented once-only semantics across stream transformations and failures. `Pull` preserves resource management while exposing lower-level consumption. The [implementation-oriented guide](https://github.com/typelevel/fs2/blob/main/site/guide.md) builds transformations step by step.
- **C2:** Effect-polymorphic streams, reusable pipes, and `Pull` provide a general vocabulary for I/O, transformations, and concurrent composition.
- **C3:** Streams are internally chunked, and many operators preserve chunks to reduce per-element overhead. Pull-based consumption and explicit concurrent operations make evaluation and buffering boundaries worth studying together; this is not a claim that every possible FS2 pipeline has bounded memory.

### 8. [monix/monix](https://github.com/monix/monix)

**Scala/Scala.js; focus on the 3.x `monix-reactive` Observable design.** Its distinguishing feature is acknowledgement-based flow control rather than a request counter as the internal user-facing model.

- **C1:** An observer returns an acknowledgement that permits continuation or stops production, and the producer must wait for it before sending another item. Concurrent, non-pausable sources require separate overflow handling. The [Observable guide](https://monix.io/docs/current/reactive/observable.html) explains this protocol and its cancellation implications.
- **C2:** Observables compose with `Task`, subjects, queues, and a substantial operator family, spanning both JVM and JavaScript use cases.
- **C3:** Bounded backpressure, failure, dropping newer or older items, and unbounded buffering are deliberately different policies. The guide discusses their latency and throughput implications. The study target is the documented 3.x design; no recent release cadence is assumed.

### 9. [zio/zio](https://github.com/zio/zio)

**Scala; the `zio-streams` subsystem inside the ZIO monorepo.** Useful for examining how stream composition incorporates typed errors, environmental requirements, and effect scopes.

- **C1:** Scoped constructors and `acquireReleaseWith` bind resources to stream use; finalizers have explicit ordering. The [resourceful-streams guide](https://zio.dev/reference/stream/zstream/resourceful-streams/) makes these lifecycle obligations concrete.
- **C2:** `ZStream`, sinks, pipelines, and channels supply reusable stages while preserving the stream's error and environment types.
- **C3:** Partitioning explicitly bounds how far one branch can run ahead of another. The [operations guide](https://zio.dev/reference/stream/zstream/operations/) exposes buffering and branch coordination, a useful study of how downstream consumers affect a shared upstream computation.

### 10. [Kotlin/kotlinx.coroutines](https://github.com/Kotlin/kotlinx.coroutines)

**Kotlin; Flow, SharedFlow, StateFlow, and channel-based stream builders.** Counted for the streaming subsystem, not as a blanket endorsement of the entire coroutine runtime.

- **C1:** `Flow` requires context preservation and exception transparency. A builder must not casually emit from unrelated coroutine contexts or continue emitting after a failed emission. These constraints and their enforcement rationale appear in [Flow.kt](https://raw.githubusercontent.com/Kotlin/kotlinx.coroutines/master/kotlinx-coroutines-core/common/src/flow/Flow.kt).
- **C2:** Cold flows, hot shared/state flows, suspending terminal operations, and `channelFlow` cover distinct reusable models without reducing them to one subscription lifecycle.
- **C3:** Ordinary flow operators execute sequentially in the same coroutine; buffering and merge operators explicitly introduce concurrency. This makes suspension-based flow control and the cost of introducing a channel boundary natural study targets.

### 11. [leonoel/missionary](https://github.com/leonoel/missionary)

**Clojure/ClojureScript with Java internals; functional effects and reactive flows.** The repository describes its maturity as experimental but stable. It is a substantive, smaller alternative with a distinct model, not a wrapper over RxJava.

- **C1:** Process supervision propagates cancellation and failure. The flow tutorial distinguishes sequential, preemptive, and concurrent forking, including cancellation of obsolete work. Read [Hello flow](https://github.com/leonoel/missionary/blob/master/doc/tutorials/hello_flow.md).
- **C2:** A common flow abstraction supports discrete backpressured events and lazy sampling of continuous signals; the `ap` DSL composes processes that can produce multiple values.
- **C3:** The tutorial's explicit parallelism argument and completion-order behavior expose the relationship among concurrency, ordering, and upstream consumption. Study these semantics rather than assuming a stream's original ordering survives concurrent evaluation.

### 12. [clj-commons/manifold](https://github.com/clj-commons/manifold)

**Clojure; asynchronous streams, deferred values, and interoperability.** A useful study of backpressure through asynchronous acceptance acknowledgements and inspectable connections.

- **C1:** A sink being closed differs from a source being drained. Timeouts, rejected puts, and propagation of closure through a graph need distinct outcomes; otherwise an unusable downstream can indefinitely pressure its upstream. The [stream design/API guide](https://github.com/clj-commons/manifold/blob/master/doc/stream.md) explains these cases.
- **C2:** Source/sink conversion, transducers, and `connect-via` support composition across Manifold, core.async channels, Java queues, and lazy sequences. A deferred callback result controls acceptance of the next message.
- **C3:** Buffers can be measured by a user-supplied metric, not merely message count. That is a valuable resource-control abstraction when individual messages vary greatly in size.

### 13. [composewell/streamly](https://github.com/composewell/streamly)

**Haskell; streaming, concurrent evaluation, folds, and fused processing.** This is a broader library, selected for its stream concurrency machinery and explicit scheduling controls.

- **C1:** Concurrent evaluation distinguishes original-order output from completion-order output and permits different scheduling policies. Limits must interact correctly with long or infinite streams. The [versioned Stream.Prelude reference](https://streamly.composewell.com/haddocks/streamly-0.11.0/Streamly-Data-Stream-Prelude.html) describes the underlying channel model.
- **C2:** A small family of primitives—`parBuffered`, `parConcatMap`, and `parConcatIterate`—supports a larger concurrent combinator vocabulary.
- **C3:** `maxThreads`, `maxBuffer`, and consumption-sensitive scheduling expose real CPU, in-flight-I/O, and memory constraints. The documentation states that a full result buffer stops additional task spawning. This is stronger evidence than repeating the project's comparative speed claims.

### 14. [snoyberg/conduit](https://github.com/snoyberg/conduit)

**Haskell; demand-driven streaming composition and resource management.** Included as a pull-stream architecture, not as an implementation of the JVM Reactive Streams interfaces.

- **C1:** Upstream/downstream termination, leftover input, component-local exception handling, and resource release make fusion more subtle than ordinary function composition. The [internal Conduit implementation](https://raw.githubusercontent.com/snoyberg/conduit/master/conduit/src/Data/Conduit/Internal/Conduit.hs) explicitly warns that `catchC` does not catch other components' exceptions and should not be used to reconstruct asynchronous-exception-safe cleanup.
- **C2:** `ConduitT`, `await`, `yield`, fusion, and `ResourceT` integration support reusable producers, transformers, and consumers for files, parsing, and network data.
- **C3:** Its demand-driven interpreter and explicit leftover handling let consumers terminate without requiring complete upstream materialization. The repository's guide is a practical companion for studying evaluation order and deterministic resource use.

## JavaScript and TypeScript streaming models

### 15. [Effect-TS/effect](https://github.com/Effect-TS/effect)

**TypeScript; Stream/Sink and scoped effects within the Effect monorepo.** The linked guides describe the v4 API. This selection concerns streaming composition rather than every subsystem in Effect.

- **C1:** Resources must remain acquired throughout consumption, and finalizers must run on success, failure, or interruption. The [resourceful-streams guide](https://effect.website/docs/v4/stream/resourceful-streams) explains scope ownership and finalizer ordering.
- **C2:** Streams combine typed values, errors, and environmental requirements with reusable transformations and sinks.
- **C3:** Streams use pull-based consumption; buffering offers bounded, unbounded, sliding, and dropping policies. Broadcasting also exposes how far upstream can advance relative to slow consumers. The [operations guide](https://effect.website/docs/v4/stream/operations) makes these choices explicit. An unbounded option remains unbounded despite the library's support for backpressure elsewhere.

### 16. [caolan/highland](https://github.com/caolan/highland)

**JavaScript; high-level streams for Node.js and browsers.** Study the tension between lazy consumption, callback sources, Node streams, and multiple observers. The repository distinguishes its 3.0 development branch from the 2.x line; the linked site documents the established API.

- **C1:** A stream has a consumption lifecycle; multiple consumers require an explicit choice between `fork` and `observe`. Non-pausable event sources can accumulate data even when ordinary pipelines backpressure correctly. The [API/design guide](https://caolan.github.io/highland/) describes these boundaries.
- **C2:** Generator callbacks, Node readables, promises, iterators, and arrays share a compositional transformation vocabulary.
- **C3:** `fork` shares downstream pressure, whereas `observe` leaves another consumer responsible for pacing and may buffer. This is an instructive, concrete fan-out tradeoff that is easy to hide in higher-level APIs.

### 17. [pull-stream/pull-stream](https://github.com/pull-stream/pull-stream)

**JavaScript; a compact, callback-based demand-driven stream protocol.** Smaller than the major operator engines, but substantial as an abstraction: sources, through-streams, and sinks compose without a large scheduler or object hierarchy.

- **C1:** End, error, and abort are protocol states, and synchronous callbacks must not turn long streams into unbounded recursion. The [drain implementation](https://raw.githubusercontent.com/pull-stream/pull-stream/master/sinks/drain.js) uses a loop around synchronous callback progress and propagates termination upstream.
- **C2:** The [repository's protocol explanation](https://github.com/pull-stream/pull-stream#how-pull-streams-work) describes reusable functional stages for object and byte streams. This is a meaningful architecture study even though individual modules are small.
- **C3:** Downstream reads drive upstream work, allowing simple transformations to propagate pressure without independent queues at every stage. It is distinct from Node's stream protocol, so interoperability requires adapters rather than assuming identical semantics.

### 18. [MattiasBuelens/web-streams-polyfill](https://github.com/MattiasBuelens/web-streams-polyfill)

**TypeScript; a substantive implementation of WHATWG readable, writable, and transform streams.** Despite the “polyfill” name, this contains the stream algorithms rather than merely forwarding calls to native APIs.

- **C1:** Transform streams must coordinate two sides, unblock writes when errors occur, and correctly resolve changing backpressure promises. Inspect [transform-stream.ts](https://raw.githubusercontent.com/MattiasBuelens/web-streams-polyfill/master/src/lib/transform-stream.ts), especially `TransformStreamSetBackpressure` and the error/unblock path.
- **C2:** Readable, writable, and transform abstractions implement a cross-runtime standard, with both global-replacing and non-replacing distributions.
- **C3:** Separate readable/writable high-water marks and promise-based write gating make queue boundaries explicit. The repository also documents browser Web Platform Test coverage and deliberate compatibility exceptions; that is stronger evidence than assuming every polyfill perfectly matches native behavior.

### 19. [ReactiveX/rxjs](https://github.com/ReactiveX/rxjs)

**TypeScript/JavaScript; push-observable composition. Study target: the verified 7.x implementation.** This belongs to the reactive-stream portion of the category; ordinary RxJS observables do not provide Reactive Streams-style demand negotiation. The repository's default development generation differs from the selected branch.

- **C1:** Merge completion depends on the outer source ending, all inner subscriptions ending, and the pending buffer draining. Cancellation and error finalization must differ from normal completion. These conditions are explicit in [mergeInternals.ts on 7.x](https://raw.githubusercontent.com/ReactiveX/rxjs/7.x/src/internal/operators/mergeInternals.ts).
- **C2:** The implementation shares machinery across merge-style operators, illustrating how a broad operator API can reuse one state-management core.
- **C3:** The source bounds active inner subscriptions but pushes excess outer values into an array. Consequently, bounded concurrency alone does **not** bound queued input. That limitation is an important architectural lesson, not a claim of backpressure support.

## Runtime-native channels and asynchronous sequences

### 20. [rust-lang/futures-rs](https://github.com/rust-lang/futures-rs)

**Rust; focus on Stream/Sink traits, combinators, and asynchronous channels.** A reusable protocol layer rather than a JVM-style publisher/subscriber implementation.

- **C1:** `Sink::start_send` requires preceding readiness; readiness may register a waker; beginning a send is distinct from flushing or closing it. The [Sink contract](https://docs.rs/futures/latest/futures/sink/trait.Sink.html) exposes the progress and completion obligations that wrappers must preserve.
- **C2:** Generic stream and sink combinators compose channels, buffered output, and asynchronous I/O without coupling them to one application protocol.
- **C4:** The [changelog](https://raw.githubusercontent.com/rust-lang/futures-rs/main/CHANGELOG.md) records multiple years of soundness fixes, stream termination fixes, compatibility adapters, cooperative-scheduling compatibility, and explicit handling of problematic releases. This makes historical changes part of the study material, not just evidence of an old repository.

### 21. [apple/swift-async-algorithms](https://github.com/apple/swift-async-algorithms)

**Swift; asynchronous sequence algorithms and backpressured channels.** Particularly useful for comparing language-native async iteration with explicit demand counters.

- **C1:** A pending channel send must resume on consumption, while finish/failure and task cancellation have different effects on blocked senders and receivers. The [Channel design document](https://github.com/apple/swift-async-algorithms/blob/main/Sources/AsyncAlgorithms/AsyncAlgorithms.docc/Guides/Channel.md) specifies these transitions and explains why an actor implementation was not chosen.
- **C2:** `AsyncChannel` and `AsyncThrowingChannel` fit the same `AsyncSequence` world as merge, zip, combineLatest, and time-based algorithms.
- **C3:** Suspending `send` transmits consumer pacing to producers without blocking a thread. The design makes termination behavior explicit rather than relying on a buffered async sequence to provide equivalent flow control.

### 22. [OpenCombine/OpenCombine](https://github.com/OpenCombine/OpenCombine)

**Swift; an independent implementation compatible with Apple's Combine model.** Useful for studying demand semantics and behavioral compatibility against an external framework. It is not an official Apple mirror.

- **C1:** Demand has finite and unlimited cases, rejects negative construction, and handles arithmetic overflow deliberately. Read [Subscribers.Demand.swift](https://raw.githubusercontent.com/OpenCombine/OpenCombine/master/Sources/OpenCombine/Subscribers/Subscribers.Demand.swift) for the numerical contract underpinning subscriptions.
- **C2:** Publishers, subscribers, subjects, schedulers, and separate Foundation/Dispatch integration modules provide reusable sequence composition across platforms.
- **C4:** The [2019–2023 changelog](https://raw.githubusercontent.com/OpenCombine/OpenCombine/master/CHANGELOG.md) records thread-safety audits, reentrancy and lifecycle fixes, a FlatMap rewrite for Combine compatibility, and successive Swift/Xcode compatibility targets. Its last listed release is April 2023; this report does not infer present toolchain support or active maintenance from that history.

### 23. [elixir-lang/gen_stage](https://github.com/elixir-lang/gen_stage)

**Elixir; demand-driven producer and consumer processes.** The important unit here is a supervised stage rather than a callback operator or an iterator.

- **C1:** Each producer relationship has its own demand, and dispatchers distribute events across consumers without exceeding requested quantities. Subscription and cancellation behavior must coexist with process lifecycles. The [GenStage reference](https://gen-stage.hexdocs.pm/GenStage.html) explains these relationships.
- **C2:** Producer, consumer, producer-consumer, dispatcher, and ConsumerSupervisor abstractions support reusable actor pipelines; Flow and Broadway build higher-level processing on this foundation.
- **C3:** `min_demand` and `max_demand` control replenishment and batching. The documentation explicitly discusses the throughput cost of undersized buffers and the memory cost of oversized ones. This is a clear example of flow control integrated with actor scheduling.

### 24. [ReactiveX/RxGo](https://github.com/ReactiveX/RxGo)

**Go; ReactiveX-style pipelines built from channels and goroutines.** Useful for understanding the choices required when adapting observer composition to a language whose ordinary concurrency abstractions already carry blocking semantics.

- **C1:** Hot event-source delivery coordinates observer registration, shutdown, context cancellation, and channel closure. The [event-source implementation](https://raw.githubusercontent.com/ReactiveX/RxGo/master/iterable_eventsource.go) shows the locking and cancellation paths.
- **C2:** Operators, observable sources, context options, and worker-pool configuration form a reusable pipeline vocabulary.
- **C3:** The same source implements distinct blocking and dropping delivery strategies. Blocking delivery can let a slow observer affect later deliveries; dropping explicitly sacrifices items when a receiver is not ready. The repository explains how this differs from buffered channel sources and how operator pools introduce concurrency.

### 25. [dbrattli/aioreactive](https://github.com/dbrattli/aioreactive)

**Python; async/await observables and observers on asyncio.** A smaller, substantive library that differs from ordinary RxPY by making sending, subscribing, and disposing asynchronous.

- **C1:** The push-to-iterator bridge must serialize concurrent producers and coordinate separate push/pull futures, termination, and subscription disposal. Inspect `AsyncIteratorObserver` in [observers.py](https://raw.githubusercontent.com/dbrattli/aioreactive/master/aioreactive/observers.py).
- **C2:** AsyncObservable/AsyncObserver and composable function operators connect push-style reactive code with `async for` consumption.
- **C3:** The producer awaits downstream progress; the iterator bridge implements a rendezvous instead of merely moving the overload into a growing queue. This describes the inspected bridge and cooperative sending contract, not a guarantee that arbitrary external producers cannot enqueue work elsewhere.

## Push-reactive composition as a comparison point

### 26. [dotnet/reactive](https://github.com/dotnet/reactive)

**C#; focus on Rx.NET/System.Reactive within the broader repository.** Included for reactive event streams. Its `IObservable<T>` contract is not a request-counted backpressure protocol, and asynchronous scheduling must not be mistaken for bounded buffering.

- **C1:** A source may invoke an observer from different threads, but callbacks for one subscription must remain sequential and stop after a terminal signal. Merging multiple inputs must preserve that contract. The project's [Scheduling and Threading chapter](https://introtorx.com/chapters/scheduling-and-threading) explains the invariants and their consequences.
- **C2:** Observable operators and scheduler abstractions separate event composition from execution context, clocks, and timing behavior.
- **C3:** Ordinary operator chains often forward notifications through direct calls on the producing thread; explicit scheduler boundaries change that execution structure. This provides a useful comparison with demand-aware libraries: serial notification safety, concurrency control, and upstream flow control are separate properties.

## Coverage, search method, and limitations

Discovery used more than six distinct live-web query families: JVM Reactive Streams engines and TCKs; Scala functional streams and acknowledgement protocols; Java networking demand propagation; JavaScript pull streams and Node integration; Python/Go/Elixir backpressure; Clojure and Haskell streaming; Swift Combine demand and async channels; Rust Stream/Sink readiness; C++ ReactiveX implementations; and WHATWG stream implementations. Follow-up searches targeted implementation details such as request accounting, merge buffering, thread limits, scheduler contracts, and resource finalization. Later queries mostly returned already covered families, documentation variants, thin adapters, or applications. The WHATWG polyfill supplied the final distinct implementation family and justified extending the selection to 26.

Every retained canonical repository page was opened, and each entry has additional primary material that was opened and read. Sources include actual operator code, protocol tests, API/design documentation, and selected changelogs. Raw source links are used where GitHub's rendered file view was less reliable; fetching a README again was not treated as independent evidence. No candidate code was executed, dependencies installed, or repositories cloned.

The list covers Java, Scala, Kotlin, Clojure, Haskell, JavaScript/TypeScript, Rust, Swift, Elixir, Go, Python, and C#. It emphasizes several distinct correctness models rather than maximizing the number of ReactiveX ports. C++ RxCpp/ReactivePlusPlus appeared in discovery but were not expanded into retained entries; coverage is therefore not exhaustive. RxJS and Rx.NET are explicitly marked as push-reactive comparison points. Pull-driven Conduit and suspension-driven Flow/async channels are included because they implement meaningful consumer-paced streaming even without the JVM protocol.

Akka was not separately counted alongside Pekko. Thin bindings, generated API wrappers, example applications, awesome lists, generic distributed stream-processing platforms, and duplicate specification forks were excluded. None of the selected entries is being presented as a migrated project's unofficial mirror. Historical or version-specific study material is labeled, particularly RxJava's 2.x operator guide, RxJS's 7.x source, Monix's 3.x design, ServiceTalk's versioned architecture document, and OpenCombine's release history. Default branches and live documentation can evolve; this is a source-selection guide as of the research date, not a maintenance audit or a finding that every component is uniformly exemplary.
