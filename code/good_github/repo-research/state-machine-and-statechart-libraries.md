# State machine and statechart libraries

Research date: **2026-10-09**.

This selection covers 25 reusable implementations of finite-state machines, hierarchical statecharts, SCXML execution, and compile-time state protocols. It spans application workflows, reactive interfaces, embedded systems, robotics, and library-level protocol enforcement. The emphasis is on execution semantics and reusable architecture, rather than diagram editors, application-specific machines, or distributed workflow services. Every repository URL was checked against GitHub repository metadata, and every entry includes an independently inspected implementation or documentation source beyond its repository landing page.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, adversarial inputs, or failure handling; **C2** — substantial abstractions reusable across applications; **C3** — concrete performance/resource constraints addressed through understandable architecture; **C4** — sustained evolution supported by compatibility work, testing, or complexity management. These are evidence-based reasons to study a repository, not certifications of correctness or uniform code quality.

## Application statecharts and interpreters

### 1. [statelyai/xstate](https://github.com/statelyai/xstate)

**TypeScript / JavaScript — statechart interpreter and actor orchestration.** The relevant subsystem is the `xstate` core within this monorepo; UI bindings and the separate store package are not separate selections. Study how machine definitions, actor instances, hierarchical state configurations, and effects fit together.

- **C1:** Transition selection searches active children before their ancestors. Targetless, targeted, and re-entering transitions have different consequences for child configurations, entry/exit effects, and invoked actors. These distinctions make lifecycle correctness a substantial part of the engine. The [transition semantics guide](https://stately.ai/docs/transitions) explains the selection and re-entry rules.
- **C2:** The repository combines reusable machine logic with independently instantiated actors, hierarchical and parallel states, and history. Its [core overview and examples](https://github.com/statelyai/xstate#packages) show how the same abstractions support UI and non-UI logic. The inspected rolling documentation identifies itself as v6 alpha; do not assume all described behavior belongs to an older installed release.

### 2. [pytransitions/transitions](https://github.com/pytransitions/transitions)

**Python — object-oriented FSM core with hierarchical, asynchronous, locking, and visualization extensions.** A useful study in attaching a state-machine API to existing domain objects while keeping execution strategies extensible.

- **C1:** Immediate nested triggers can run before an outer transition's completion callbacks; queued processing changes that ordering and cannot report eventual transition success at enqueue time. The [core implementation](https://raw.githubusercontent.com/pytransitions/transitions/master/transitions/core.py) exposes the queue, callback phases, exception handling, and cleanup of events associated with removed models.
- **C2:** State, transition, event, and machine objects form a reusable core, with extension families for hierarchy and execution context. The repository explicitly limits locking guarantees to protected function access; arbitrary model mutations are not automatically synchronized.
- **C4:** The [changelog](https://raw.githubusercontent.com/pytransitions/transitions/master/Changelog.md) documents years of work on nested-state scope preservation, asynchronous callback ordering, Python compatibility, and test tooling. This is stronger evolution evidence than repository age alone.

### 3. [fgmacedo/python-statemachine](https://github.com/fgmacedo/python-statemachine)

**Python — declarative FSMs and statecharts with synchronous and asynchronous execution.** Study the boundary between class-level declarations and the engine that turns an external event into a stable state configuration.

- **C1:** The [processing-model documentation](https://python-statemachine.readthedocs.io/en/latest/processing_model.html) distinguishes microsteps from macrosteps, prioritizes eventless transitions and the internal queue, and separates `raise_()` from externally queued `send()`. It also explains how configured error handling can skip remaining actions in a failing block while continuing the microstep.
- **C2:** Declarative states and transitions are reusable across flat machines and richer statecharts, with domain-model integration and async support. The same processing guide demonstrates chained transitions and initialization under a common execution model. The inspected documentation is for the 3.x generation; its richer statechart API should not be projected onto older versions.

### 4. [AlexandreDecan/sismic](https://github.com/AlexandreDecan/sismic)

**Python — observable statechart interpreter, simulation, and testing toolkit.** Particularly useful for engineers who want to inspect execution as data rather than only receive callbacks from an opaque runtime.

- **C1:** Its [execution guide](https://sismic.readthedocs.io/en/latest/execution.html) describes separate internal/external event queues, transition selection, conflict and nondeterminism errors, and stabilization of compound, orthogonal, and history configurations. Bounded execution is available to avoid unbounded automatic stepping.
- **C2:** Microstep and macrostep objects report consumed events, transitions, and entered/exited states. Interpreter methods separate event selection, transition sorting, step creation, and application, allowing alternative semantics. The same guide covers listeners, binding between interpreters, and a subclassable asynchronous runner. This makes it a strong selection for simulation and verification tooling as well as execution.

### 5. [glyph/automat](https://github.com/glyph/automat)

**Python — typed finite-state transducers exposed as ordinary method-call interfaces.** Study how a state-machine library can enforce sequencing without exposing a generic `send(event)` interface to its callers.

- **C1:** The [typed-machine tutorial](https://automat.readthedocs.io/en/latest/tutorial.html) demonstrates rejecting an undefined transition before invoking application behavior. Its state-specific data factories require the data needed by a state to be supplied on entry, reducing reliance on partially initialized shared objects.
- **C2:** `TypeMachineBuilder` combines a caller-facing `Protocol`, a shared core object, state-specific data, and typed transition behavior into reusable factories. Input argument and result types are checked against transition signatures. The tutorial also explicitly distinguishes the newer typed API from the older `MethodicalMachine` API retained for migration; the documentation header alone is not a reliable guide to API generation.

### 6. [kmarkus/rFSM](https://github.com/kmarkus/rFSM)

**Lua — embeddable hierarchical statecharts for coordination, including robotics.** This provides a substantially different implementation community and execution model from web-oriented state libraries.

- **C1:** The [engine](https://raw.githubusercontent.com/kmarkus/rFSM/master/src/rfsm/rfsm.lua) validates model structure, resolves transition paths through a least common ancestor, maintains active-child relationships, and coordinates event processing with coroutine-based state activities. Its step loop explicitly distinguishes transitions, completed activities, and idle execution.
- **C2:** A root machine is itself a composite state, so machines can be embedded as substates. The [model and execution guide](https://github.com/kmarkus/rFSM#specifying-rfsm-models) explains composition, voluntary yielding from `doo` activities, and hooks/plugins for time events and event memory. Study how extensibility remains in ordinary Lua tables and functions rather than requiring a separate modeling language.

## C and C++ execution architecture

### 7. [boost-ext/sml](https://github.com/boost-ext/sml)

**C++ — compile-time transition-table DSL and state-machine engine.** This is the independent Boost.Ext SML project, not the Boost.Statechart or Boost.MSM library. Its value is the relationship between a compact declarative notation and generated dispatch machinery.

- **C2:** The [user guide](https://boost-ext.github.io/sml/user_guide.html) documents typed states/events, guards/actions, dependency injection, and independently composable logging and locking policies. Explicit dependency declarations address cases where generic callables hide the signature the library needs to inspect.
- **C3:** The [repository's implementation examples and benchmark section](https://github.com/boost-ext/sml#benchmark) treat runtime, compilation time, memory footprint, and executable size as separate engineering concerns. The transition-table design and policy boundaries provide concrete architectural material for investigating these tradeoffs. The published benchmark numbers are workload/compiler-specific and were not reproduced here.

### 8. [boostorg/statechart](https://github.com/boostorg/statechart)

**C++ — class-based hierarchical statecharts with synchronous and asynchronous execution.** Study this alongside table-driven libraries: state object lifetime is central to its design.

- **C1:** The [design rationale](https://www.boost.org/doc/libs/latest/libs/statechart/doc/rationale.html) works through failures during nested entry actions, exception-to-event translation, and two-stage exit. It also explains compile-time rejection of invalid transitions between orthogonal regions.
- **C2:** State-local storage follows construction/destruction of state objects, while scheduler and worker abstractions separate event queuing, synchronization, and processor lifetime. Machines can be spread across translation units. The rationale makes the costs and benefits of this design explicit, including why it does not offer arbitrary runtime reconfiguration of machine topology.

### 9. [boostorg/msm](https://github.com/boostorg/msm)

**C++ — Meta State Machine, with interchangeable modeling front ends and execution back ends.** Especially valuable for studying template metaprogramming as a compiler for a reusable behavioral model.

- **C2:** The [internals documentation](https://www.boost.org/doc/libs/latest/doc/antora/msm/internals.html) defines the contract between transition rows and the engine: source/target/event types, action and guard calls, initial regions, flags, and deferred events. Modeling syntax is separated from execution rather than baked into one API.
- **C3:** The [repository overview](https://github.com/boostorg/msm) distinguishes the classic and newer `backmp11` engines and describes runtime-versus-compilation tradeoffs and configurable heapless execution. This offers a concrete study of evolving an implementation strategy while preserving the modeling layer. The inspected manual marks `backmp11` experimental and eUML deprecated; these subsystems should not be treated as equally settled.

### 10. [andrew-gresyk/HFSM2](https://github.com/andrew-gresyk/HFSM2)

**C++ — statically structured hierarchical FSMs for games and embedded software.** Study how composite/orthogonal regions, typed transitions, and reusable state behavior fit into an allocation-conscious implementation.

- **C2:** Typed region structures, state injections, transition payloads, planning, and alternative region-selection strategies support more than simple event-to-state lookup. The [transition API](https://github.com/andrew-gresyk/HFSM2/wiki/Transitions) separates instance controls from controls available inside states.
- **C3:** The repository explicitly uses static topology, variadic templates, inline-friendly compile-time polymorphism, and no dynamic allocation in the framework. Its [legacy hierarchy design explanation](https://github.com/andrew-gresyk/HFSM2/wiki/Legacy-Transitions-within-Hierarchy) gives substantive background on ancestor traversal and restart/resume/utility selection. That page is labeled legacy; its exact scheduling details are historical, while the static architecture is stated in the current repository overview.

### 11. [QuantumLeaps/qpc](https://github.com/QuantumLeaps/qpc)

**C — embedded active-object framework with hierarchical state-machine processors.** The relevant components are the QHsm/QMsm processors and their integration with event-driven active objects, not merely the bundled examples or RTOS ports.

- **C1:** The [state-machine requirements and semantics](https://www.state-machine.com/qpc/srs-qp_sm.html) specify nested initialization, cleanup through exit actions, least-common-ancestor transitions, history, and the distinction between internal and self-transitions. They also document deliberate differences from UML action ordering, making semantic assumptions reviewable.
- **C2:** Active and passive objects share a state-machine abstraction with interchangeable implementation strategies.
- **C3:** The same document explains why a manually maintainable QHsm strategy and a code-generation-oriented QMsm strategy differ: generated transition information can precompute entry/exit paths that would otherwise be discovered at runtime. This is concrete architecture for embedded execution costs, not a numerical speed claim.

### 12. [igor-krechetov/hsmcpp](https://github.com/igor-krechetov/hsmcpp)

**C++ — hierarchical machines with SCXML code generation and configurable platform dispatch.** Useful for studying portability across an existing GUI event loop, a dedicated thread, and an RTOS task.

- **C1:** The [platform/dispatcher documentation](https://hsmcpp.readthedocs.io/en/latest/platforms/platforms.html) details queued transition execution, callback thread context, dispatcher ownership, and construction/destruction restrictions for particular dispatchers. It identifies concrete failure modes when those lifecycle rules are violated.
- **C2:** `IHsmEventDispatcher` separates the state-machine engine from timers, event notification, and OS synchronization. The same guide describes standard C++, GLib, Qt, Arduino, and FreeRTOS implementations. Model-driven SCXML and direct C++ definitions share this runtime. The repository explicitly says ultra-constrained environments without dynamic memory are outside its intended fit; do not confuse it with HFSM2's allocation model.

## SCXML engines and standard-oriented execution

### 13. [apache/commons-scxml](https://github.com/apache/commons-scxml)

**Java — Apache Commons SCXML interpreter.** Study the separation between the standard's execution algorithm and host-environment services. The inspected API documentation is labeled **2.0-SNAPSHOT**, not a declaration of a stable 2.0 release.

- **C1:** [`SCXMLSemanticsImpl`](https://commons.apache.org/proper/commons-scxml/apidocs/org/apache/commons/scxml2/semantics/SCXMLSemanticsImpl.html) exposes construction of entry/exit sets, legal-configuration checking for compound and parallel states, history recording, microsteps, macrosteps, and invocation handling. These are substantive statechart invariants.
- **C2:** The [engine guide](https://commons.apache.org/proper/commons-scxml/guide/core-engine.html) separates expression evaluation and variable contexts from event dispatch, error reporting, and listeners. The semantics implementation is itself stateless and designed for extension/testing. The older guide also makes synchronization responsibilities explicit; verify the precise executor API against the version being studied.

### 14. [qt/qtscxml](https://github.com/qt/qtscxml)

**C++ / Qt — SCXML compiler and runtime; official GitHub mirror.** Qt's [GitHub organization identifies its repositories as official mirrors](https://github.com/qt). The relevant module includes SCXML execution and generated-machine support; it is counted once.

- **C1:** [`QScxmlStateMachine` documentation](https://doc.qt.io/qt-6/qscxmlstatemachine.html) describes initialization, invalid-document diagnostics, parent/child session routing, and active-state configurations. It specifies that the Qt event loop schedules nested-machine events and delayed events, and that replacing an initialized data model has undefined behavior.
- **C2:** The runtime exposes machines loaded from data/files and interfaces used by compiled representations, together with data models and Qt connections for state/event observation. Study how an SCXML execution model is integrated into a general application framework without making every consumer implement its own event transport.

## JVM and .NET application frameworks

### 15. [spring-attic/spring-statemachine](https://github.com/spring-attic/spring-statemachine)

**Java — Spring-integrated state-machine framework; archived July 5, 2026.** The former `spring-projects` repository redirects here. Retained as a historical architecture study, not an actively supported recommendation.

- **C1:** The [persistence chapter](https://docs.spring.io/spring-statemachine/docs/current/reference/#statemachine-persist) explains why persisting from a post-transition listener can leave memory and storage inconsistent. Its interceptor approach can halt a transition if persistence fails, while `StateMachineContext` represents hierarchical/parallel runtime state without serializing the entire Spring object graph.
- **C2:** The [reference manual](https://docs.spring.io/spring-statemachine/docs/current/reference/) integrates builders/factories, guards, reactive actions, regions, interceptors, persisters, and testing support. Study the separation between machine definition, runtime instances, application-context integration, and durable state representation.

### 16. [hekailiang/squirrel](https://github.com/hekailiang/squirrel)

**Java — programmable state machines with fluent and annotation-based definitions.** A worthwhile lower-profile study of reusable machine definitions and extensible action dispatch. GitHub metadata showed no push after June 2024; this is not a claim of current maintenance.

- **C2:** The [repository's detailed builder guide](https://github.com/hekailiang/squirrel#user-guide) describes typed machine/state/event/context parameters, multiple transition kinds, action conventions, extension hooks, and reusable builders.
- **C3:** Definitions are constructed lazily and shared among instances from the same builder, reducing repeated construction and definition storage. This is an explicit memory/construction-time design decision, rather than an inferred performance benefit from Java generics.
- **C1:** [`AbstractStateMachine`](https://raw.githubusercontent.com/hekailiang/squirrel/master/squirrel-foundation/src/main/java/org/squirrelframework/foundation/fsm/impl/AbstractStateMachine.java) separates mutable execution data, event queues, machine status, action execution services, and read/write locking. Those boundaries offer concrete material for examining reentrant firing and failure handling.

### 17. [KStateMachine/kstatemachine](https://github.com/KStateMachine/kstatemachine)

**Kotlin — multiplatform hierarchical machines with a DSL and coroutine integration.** Study the distinction between a suspendable state-machine API and the scheduling discipline that makes its mutation safe.

- **C1:** The [concurrency guide](https://kstatemachine.github.io/kstatemachine/pages/multithreading.html) specifies single-threaded use and explains context preservation when coroutine-enabled entry points are called elsewhere. It also identifies recursive blocking calls as a deadlock risk. This is not a blanket claim that coroutine support makes arbitrary concurrent mutation safe.
- **C2:** The core statechart model can be used with or without the coroutine library. The documented dispatch/context boundary lets hierarchical states, guards, listeners, and application-specific actions be reused across supported Kotlin targets. Study the two integration modes together; the standard-library-only machine does not provide the coroutine variant's context switching.

### 18. [dotnet-state-machine/stateless](https://github.com/dotnet-state-machine/stateless)

**C# — generic hierarchical state machines with fluent configuration.** Particularly instructive when state is owned by a domain object or persistence layer rather than by the library.

- **C1:** The [state-machine core](https://raw.githubusercontent.com/dotnet-state-machine/stateless/dev/src/Stateless/StateMachine.cs) explicitly distinguishes immediate firing from queued run-to-completion processing and manages reentrant triggers through a queue and firing guard.
- **C2:** Generic state/trigger types, external state accessor/mutator delegates, parameterized triggers, hierarchy, and inspection let the same machine logic serve UI and backend domain models.
- **C4:** The [2016–2025 changelog](https://raw.githubusercontent.com/dotnet-state-machine/stateless/dev/CHANGELOG.md) records framework compatibility changes and fixes to hierarchy precedence, asynchronous ordering, guard handling, and parameter-conversion tests. This provides sustained complexity-management evidence, not just a long commit count.

### 19. [appccelerate/statemachine](https://github.com/appccelerate/statemachine)

**C# — active/passive hierarchical machines, including async/await variants.** Study the separation of a reusable definition from the mechanism that executes it. The repository warns that its older external website documentation is stale; prefer its in-repository material.

- **C1:** The [tutorial](https://github.com/appccelerate/statemachine/blob/master/documentation/tutorial.md) specifies ordered exit/transition/entry actions, first-matching guards, shallow versus deep history, suspended processing, and priority events placed ahead of queued work. These interacting rules expose real sequencing and lifecycle complexity.
- **C2:** A built definition can create multiple active or passive instances. The repository explains using a passive implementation behind the common interface in tests of systems that normally use active machines, a useful substitution boundary. The same definition mechanism also supports asynchronous actions and guards.

## Go and Rust execution models

### 20. [looplab/fsm](https://github.com/looplab/fsm)

**Go — compact event/callback FSM with cancellation and asynchronous transition completion.** This is a useful smaller codebase for following an entire transition lifecycle without the additional semantics of a full statechart interpreter.

- **C1:** The [core implementation](https://raw.githubusercontent.com/looplab/fsm/main/fsm.go) separates state and event mutexes, rejects new events during unfinished transitions, and manages cancellation of deferred transition closures. Comments and code explain why event locking is released before entry callbacks that may initiate another event.
- **C2:** Transition descriptors, named callback phases, event arguments, and context propagation form a reusable embedded machine API. The [repository examples](https://github.com/looplab/fsm?tab=readme-ov-file) show both direct use and embedding a machine inside a domain object. Its compactness does not remove the subtle cancellation/reentrancy cases worth studying.

### 21. [qmuntal/stateless](https://github.com/qmuntal/stateless)

**Go — hierarchical machine implementation derived from the .NET Stateless design.** This is an independent Go implementation, not a generated binding or a second listing of the C# source. Its lineage is explicitly acknowledged by the project.

- **C1:** [`modes.go`](https://raw.githubusercontent.com/qmuntal/stateless/master/modes.go) implements immediate and queued firing separately. The queued mode combines a mutex-protected trigger list, an atomic firing flag, and deferred release of that flag while carrying each trigger's `context.Context` and arguments.
- **C2:** The [configuration overview](https://github.com/qmuntal/stateless#features) exposes hierarchical states, guards, parameterized triggers, inspection, and externally stored state. Comparing the Go queue/context implementation with the C# original is especially useful for understanding which abstractions transfer and which need language-specific treatment.

### 22. [mdeloof/statig](https://github.com/mdeloof/statig)

**Rust — hierarchical machines with macro-assisted or handwritten trait implementations.** A strong study of state-local ownership and borrowed superstate views.

- **C1:** The [implementation explanation](https://docs.rs/statig/latest/statig/#implementation) represents leaf-state data as owned enum fields and superstate data as borrows. Transition traversal exits and enters only the appropriate path through the hierarchy, avoiding unnecessary destruction/re-entry of shared ancestors.
- **C2:** State/superstate traits, shared storage, external context, introspection hooks, and optional async handlers expose the machinery independently of the procedural macro.
- **C3:** The [crate documentation](https://docs.rs/statig/latest/statig/) specifies `no_std` compatibility, ROM-defined machines, and no heap allocation in the state-machine representation. The enum/trait architecture explains how those resource goals are pursued without relying on an opaque runtime.

### 23. [rustype/typestate-rs](https://github.com/rustype/typestate-rs)

**Rust — procedural-macro DSL for compile-time state protocols; archived.** GitHub repository metadata reports this project archived. It remains valuable as a historical implementation and language-design study.

- **C1:** The [macro documentation](https://docs.rs/typestate/latest/typestate/) explains consuming one typed state to produce another, rejecting missing initial/final-state definitions, and using generated state-specific interfaces to prevent invalid operations. This is protocol enforcement through Rust's ownership/type system rather than runtime event rejection.
- **C2:** The DSL supports ordinary state transitions, same-state operations, state-specific data construction, and enum-mediated alternatives when an operation can produce different states. Study how user declarations become Rust interfaces and diagnostics, and where this model differs from a runtime statechart with concurrently active regions.

## Ruby domain-object state machines

### 24. [aasm/aasm](https://github.com/aasm/aasm)

**Ruby — state-machine DSL for plain objects and persistence-backed models.** Particularly useful for understanding the interaction between transition callbacks, database writes, and framework compatibility.

- **C1:** The [transaction and locking documentation](https://github.com/aasm/aasm#transaction-support) describes rollback, nested transaction behavior, pessimistic locking, and limitations of AASM's `after_commit` handling. Those documented limitations are part of its study value; the library should not be assumed to make arbitrary callback side effects transactional.
- **C2:** The DSL supports multiple named machines and several persistence adapters while remaining usable on plain Ruby classes. State/event declarations are separated from persistence-specific behavior.
- **Evolution evidence:** The [changelog](https://github.com/aasm/aasm/blob/master/CHANGELOG.md) records Ruby keyword-argument fixes, Rails test-matrix updates, callback bugs, and explicit compatibility removals. C1 and C2 are the qualifying criteria here; no longevity claim depends only on the project's origin story.

### 25. [state-machines/state_machines](https://github.com/state-machines/state_machines)

**Ruby — attribute-oriented state machines, with persistence integrations in separate repositories.** Study this project's own implementation and evolution; do not count its ORM adapters as additional machines in this selection.

- **C1:** [`TransitionCollection`](https://raw.githubusercontent.com/state-machines/state_machines/master/lib/state_machines/transition_collection.rb) rejects multiple simultaneous transitions for the same machine attribute, coordinates callback execution, deduplicates shared actions, and rolls back state changes on failure. It also handles partially completed/deferred callbacks so they do not leak into a later action cycle.
- **C2:** The [core usage guide](https://github.com/state-machines/state_machines#usage) combines namespaced machines, conditional transitions, state-specific behavior, coordinated events, and path analysis for arbitrary Ruby classes. The transition-collection layer is particularly instructive as a reusable coordination abstraction above an individual state machine. Its use of “parallel” transitions should not be read as a promise of simultaneous OS-thread execution.

## Coverage, search process, and limitations

Discovery used more than six distinct live web-search formulations: JavaScript actor/statechart libraries; C++ compile-time and embedded HSMs; Python execution/testing frameworks; Java/Kotlin and SCXML engines; Go/.NET workflow machines; Rust hierarchical machines and typestate macros; Ruby/Swift object-state libraries; W3C-conformance-oriented engines; and Lua/Haskell/robotics-oriented alternatives. Follow-up inspection used official repository pages, GitHub API metadata, raw implementation files, project manuals, API references, and changelogs. Later queries increasingly repeated established candidates or surfaced small examples, wrappers, and adjacent workflow products; the Lua and typestate searches supplied the most useful final additions.

The selection deliberately includes contrasting architectures: dynamic object models, static C++ topology, pluggable dispatchers, standards-oriented interpretation, typed ownership protocols, and persistence-aware transition coordination. Three Boost-related projects are separate implementations; the Go Stateless entry is a substantive language port with its own execution machinery. XState is counted once despite its packages. Qt SCXML is retained as an official substantive mirror. GitHub metadata marked Spring Statemachine and `typestate-rs` archived; other entries are not thereby promised active support. The slower recent activity of Squirrel is called out rather than inferred away.

Robot, SwiftState, `rust-fsm`, qlibs SML, and other surfaced candidates were considered but not added simply to enlarge the list. Diagram-only tools, awesome lists, application-specific machines, generated bindings, and distributed workflow/consensus systems were outside scope. This is a diverse selection, not an exhaustive catalog; mobile-specific and functional-language ecosystems received less deep coverage than C/C++, Python, JVM, and .NET implementations.

No candidate code was executed, dependencies installed, or performance results reproduced. Some pages required GitHub API/raw-source fallbacks, and several documentation sites track rolling or prerelease branches. Version-sensitive qualifications are noted where material: XState's alpha documentation, Apache's snapshot API, and HFSM2's legacy design page. Criterion judgments and suggested study value are grounded engineering inferences from the linked material; they are not proofs that every advertised semantic or performance property holds under every configuration.
