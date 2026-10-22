# Software model checkers

Research date: **2026-10-09**.

This selection covers 25 substantial GitHub repositories that check program implementations or executable models of software, concurrent algorithms, and distributed protocols. It includes bounded and unbounded symbolic verification, explicit-state exploration, stateless concurrency checking, and timed/probabilistic models. The latter check specifications rather than automatically proving arbitrary source code. Hardware-only checkers, general-purpose theorem provers and SMT solvers, ordinary fuzzers, and collections of verification examples are outside this scope.

Every repository heading links to a verified GitHub repository. Linked implementation files and technical documents provide additional primary evidence and suggested reading entry points. “Study” recommendations are engineering judgments grounded in those sources, not claims that every component is exemplary. A successful bounded or restricted exploration is only meaningful within its stated bounds, environment assumptions, and supported semantics.

Criteria legend:

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or failure modes.
- **C2 — Reusable abstractions:** substantial interfaces, intermediate representations, or frameworks supporting different applications.
- **C3 — Performance with structure:** explicit treatment of computational or memory constraints through understandable architectural choices.
- **C4 — Sustained evolution:** evidence across years together with compatibility work, testing, or management of complexity; age alone does not qualify.

## Program-code verification and abstraction refinement

### 1. [diffblue/cbmc](https://github.com/diffblue/cbmc)

**C++ — bounded model checking for C/C++; the monorepo also contains JBMC for Java.** Study how a compiler-like pipeline preserves program semantics while turning safety questions into solver queries. Count CBMC and its bundled Java checker once.

- **C1:** Loop unwinding, memory-safety instrumentation, and assertion checking lead to SAT/SMT encodings and reconstructed counterexample executions. The [architecture document](https://github.com/diffblue/cbmc/blob/develop/doc/architectural/cbmc-architecture.md) exposes the boundaries between instrumentation, symbolic execution, solving, and trace production.
- **C2:** Language frontends share a serializable GOTO intermediate representation with analysis and transformation tools, rather than each frontend owning a separate verification engine. The same [architecture](https://github.com/diffblue/cbmc/blob/develop/doc/architectural/cbmc-architecture.md) explains this reuse; the [source tree](https://github.com/diffblue/cbmc/tree/develop/src) is the implementation entry point.

### 2. [esbmc/esbmc](https://github.com/esbmc/esbmc)

**C++ — SMT-based context-bounded software checker.** Study the combination of compiler frontends, symbolic execution, and solver-independent encodings. ESBMC identifies its origin as a CBMC 2.9 fork, but its separate frontend, SMT, concurrency, and induction development makes it a substantive independent project.

- **C1:** The checker addresses pointer errors, arithmetic errors, assertions, and thread interleavings; the repository distinguishes bounded exploration from induction-based verification. Its [architecture](https://github.com/esbmc/esbmc/blob/master/ARCHITECTURE.md) follows AST → GOTO → bounded symbolic execution/SSA → SMT, explicitly explaining what an unsatisfiable bounded query establishes.
- **C2:** Multiple source languages converge on the same GOTO and SSA representations, with several SMT backends. This is useful material for designing a verification platform whose frontend and decision procedure can evolve independently. Start with the [architecture](https://github.com/esbmc/esbmc/blob/master/ARCHITECTURE.md) and [implementation tree](https://github.com/esbmc/esbmc/tree/master/src).

### 3. [model-checking/kani](https://github.com/model-checking/kani)

**Rust — bit-precise model checking for Rust, using CBMC.** Study the engineering required to connect a changing language compiler to a verification backend. Although it uses CBMC, this repository contains substantial Rust compiler integration and verification-specific infrastructure.

- **C1:** Proof harnesses explore nondeterministic inputs and check panics, arithmetic overflow, assertions, and supported forms of undefined behavior, including in unsafe code. The repository explains the harness model; the [GOTO backend module](https://github.com/model-checking/kani/blob/main/kani-compiler/src/codegen_cprover_gotoc/mod.rs) separates compiler integration, code generation, contexts, and overrides.
- **C2:** The compiler-facing API migration is an instructive abstraction boundary: [StableMIR documentation](https://github.com/model-checking/kani/blob/main/docs/src/stable-mir.md) explains typed definitions, instantiated bodies, bridges to internal compiler APIs, and module conventions. It also records which interfaces remain unstable, so this should not be read as a promise of stable compiler compatibility.

### 4. [sosy-lab/cpachecker](https://github.com/sosy-lab/cpachecker)

**Java — configurable software-verification platform; official read-only GitHub mirror.** Development infrastructure is hosted by SOSY-LAB on GitLab. Study how many program analyses can share a core without erasing their distinct abstract semantics.

- **C1:** A configurable analysis must correctly define state transfer, merging, stopping, and precision adjustment. These obligations are visible directly in [ConfigurableProgramAnalysis.java](https://github.com/sosy-lab/cpachecker/blob/main/src/org/sosy_lab/cpachecker/core/interfaces/ConfigurableProgramAnalysis.java), including initial states and state-space partitions.
- **C2:** Those operations are separate interfaces, making abstract domains and exploration policies composable rather than embedding one analysis throughout the engine. The [developer guide](https://github.com/sosy-lab/cpachecker/blob/main/doc/Developing.md) adds concrete complexity-management evidence: multiple static checks, unit tests, and integration runs over many configurations. This testing evidence is useful, but is not by itself used here to claim C4.

### 5. [ultimate-pa/ultimate](https://github.com/ultimate-pa/ultimate)

**Java — program-analysis monorepo containing Automizer, Taipan, Kojak, and GemCutter.** Study automata-based verification and reusable program representations. These tools count as one repository, not separate entries.

- **C1:** Automizer generalizes infeasible traces into proof automata; GemCutter combines commutativity-based partial-order reduction with trace-abstraction refinement. These algorithms are described in the repository overview. The [CFG representation document](https://github.com/ultimate-pa/ultimate/wiki/Terminology-and-Concepts-of-our-CFG-based-program-representation) explains the semantic foundation: state sets as formulas and transitions as binary relations over before/after variables.
- **C2:** Parsing, translation, and analysis are assembled as plugin toolchains. Shared transition formulas, automata libraries, and model-checker utilities support several verification strategies. Compare the [representation document](https://github.com/ultimate-pa/ultimate/wiki/Terminology-and-Concepts-of-our-CFG-based-program-representation) with the [plugin/library source tree](https://github.com/ultimate-pa/ultimate/tree/dev/trunk/source).

### 6. [seahorn/seahorn](https://github.com/seahorn/seahorn)

**C++ with Python orchestration — LLVM-based bounded and constrained-Horn-clause software verification.** Study how an analysis framework separates operational semantics from verification-condition construction. The project explicitly presents itself as a research framework requiring configuration and composition.

- **C1:** The [operational-semantics interface](https://github.com/seahorn/seahorn/blob/main/include/seahorn/OperationalSemantics.hh) distinguishes symbolic stores, path conditions, rely constraints, guarantees, and function summaries. These are concrete places where an incorrect abstraction can change which program behaviors are admitted.
- **C2:** Register-only, pointer, and memory tracking levels, overridable contexts, and separate execution hooks for blocks, branches, and phi nodes allow different semantic encodings to reuse the framework. Read [OperationalSemantics.hh](https://github.com/seahorn/seahorn/blob/main/include/seahorn/OperationalSemantics.hh), then the neighboring [BMC, Horn, and VC interfaces](https://github.com/seahorn/seahorn/tree/main/include/seahorn).

### 7. [ftsrg/theta](https://github.com/ftsrg/theta)

**Java/Kotlin — configurable model-checking framework, including CFA/XCFA software verification.** Study the practical design space of counterexample-guided abstraction refinement (CEGAR), especially how choices are made independently and then combined.

- **C1:** Abstract counterexamples must be checked for feasibility before declaring an actual error; spurious ones drive precision refinement. The [CEGAR guide](https://github.com/ftsrg/theta/blob/master/doc/CEGAR-algorithms.md) explains this safety argument and the roles of interpolation and unsatisfiable cores.
- **C2:** The framework combines explicit-value, predicate, and product domains with search, initial-precision, refinement, and pruning strategies across multiple formalisms. Its XCFA tooling covers procedures and concurrent C programs, while other frontends cover transition systems and timed automata.
- **C3:** The same [guide](https://github.com/ftsrg/theta/blob/master/doc/CEGAR-algorithms.md) documents concrete tradeoffs between Cartesian/Boolean predicates, enumeration limits, and block encodings. The [development guide](https://github.com/ftsrg/theta/blob/master/doc/Development.md) provides the project-level orientation.

### 8. [kind2-mc/kind2](https://github.com/kind2-mc/kind2)

**OCaml — parallel SMT-based checking of Lustre programs.** Study cooperation between proof engines for synchronous software, rather than treating a portfolio as unrelated solver invocations.

- **C1:** Safety properties require both a valid base case and an inductive step. The [k-induction documentation](https://github.com/kind2-mc/kind2/blob/main/doc/content/techniques/kinduction.md) explains why the step engine alone cannot establish a property, and how invariant strengthening interacts with counterexamples.
- **C3:** Kind 2 runs bounded checking, induction, invariant generation, and IC3-related engines concurrently. Its [k-induction implementation guide](https://github.com/kind2-mc/kind2/blob/main/doc/content/techniques/kinduction.md) exposes path-compression variants and lazy assertion of invariants to block candidate counterexamples. These are explicit controls over proof-search cost, not just claims of speed. The [techniques directory](https://github.com/kind2-mc/kind2/tree/main/doc/content/techniques) is the next reading point.

## Concurrency, weak memory, and controlled execution

### 9. [javapathfinder/jpf-core](https://github.com/javapathfinder/jpf-core)

**Java — extensible model-checking virtual machine for Java bytecode.** Study how execution, scheduling choices, stored state, and backtracking fit together inside a verifier.

- **C1:** Thread and heap snapshots must be restored consistently while exploring deadlocks, exceptions, and assertion failures. The [ChoiceGenerators design](https://github.com/javapathfinder/jpf-core/blob/master/docs/devel/ChoiceGenerators.md) walks through shared-field access, instruction re-execution at transition boundaries, and restoration of unexplored choices.
- **C2:** Typed choice generators cover both scheduling and input nondeterminism, with configuration-selected implementations. This avoids hard-coding domain-specific input heuristics into the VM or test driver. The same [design document](https://github.com/javapathfinder/jpf-core/blob/master/docs/devel/ChoiceGenerators.md) also explains why a finite heuristic selection of floating-point inputs is not exhaustive checking of that domain.

### 10. [MPI-SWS/genmc](https://github.com/MPI-SWS/genmc)

**C++ — stateless checking of concurrent programs through LLVM IR; official periodically updated mirror.** The repository explicitly mirrors an internal development repository. Rust support is marked experimental. Study the boundary between an interpreter and an execution-graph verifier.

- **C1:** The [verification driver](https://github.com/MPI-SWS/genmc/blob/master/genmc/genmc/Verification/GenMCDriver.hpp) models event ordering and memory operations, including separate success information for weak compare-and-swap, which can fail spuriously. It distinguishes completed, blocked, and erroneous scheduling outcomes.
- **C2:** Execution graphs, work queues, choice maps, consistency checking, scheduling, and interpreter event handling are distinct components. The [development guide](https://github.com/MPI-SWS/genmc/blob/master/doc/development.md) gives the actual cross-component steps for adding an event-label type, making it a useful guide to extending a checker without silently omitting semantic handling.

### 11. [nidhugg/nidhugg](https://github.com/nidhugg/nidhugg)

**C++ — LLVM-level stateless checking, especially C/pthreads under relaxed memory.** Study how the equivalence relation used to prune executions changes the engineering of a concurrency checker.

- **C1:** The [manual](https://github.com/nidhugg/nidhugg/blob/master/doc/manual.tex) states finiteness and determinism requirements, differentiates memory models, and explains why ARM coverage is an under-approximation. The repository additionally warns that ARM/POWER support is unavailable with LLVM 15 and newer.
- **C3:** Source-DPOR, optimal DPOR, observer-based reduction, and reads-from-centric exploration have different memory/runtime tradeoffs. The [manual](https://github.com/nidhugg/nidhugg/blob/master/doc/manual.tex) also explains spin-loop-to-assumption rewriting and the distinction between preserving safety properties and preserving robustness violations. These semantic qualifications make the optimization code especially instructive.

### 12. [hernanponcedeleon/Dat3M](https://github.com/hernanponcedeleon/Dat3M)

**Java — Dartagnan, bounded checking parameterized by CAT memory models.** Study a symbolic alternative to enumerating weak-memory executions, including how language-level operations are lowered for target memory models.

- **C1:** Program assertions and memory-model constraints are checked together. The repository distinguishes `PASS` after full loop unrolling from `UNKNOWN` when the chosen bound is insufficient, and makes matching the CAT model to the target instruction set an explicit user responsibility.
- **C2:** Memory models are input data rather than one fixed semantics embedded in the checker. [WmmEncoder.java](https://github.com/hernanponcedeleon/Dat3M/blob/master/dartagnan/src/main/java/com/dat3m/dartagnan/encoding/WmmEncoder.java) separates relations, axioms, analysis knowledge, and the encoding context.
- **C3:** The [encoder](https://github.com/hernanponcedeleon/Dat3M/blob/master/dartagnan/src/main/java/com/dat3m/dartagnan/encoding/WmmEncoder.java) uses active sets and relation analysis to restrict encoded constraints and avoid redundant coherence edges, exposing the connection between static analysis and solver-formula size.

### 13. [tokio-rs/loom](https://github.com/tokio-rs/loom)

**Rust — library-based concurrency permutation checking.** Study how replacement synchronization types make a model checker usable within ordinary library tests.

- **C1:** The repository demonstrates an assertion failure caused by interleaving separate atomic loads/stores. It also explicitly documents incomplete C11 coverage: certain `SeqCst` operations can produce false alarms, and some load-buffering behaviors are missed. A passing Loom test is therefore not a full C11 proof.
- **C3:** [execution.rs](https://github.com/tokio-rs/loom/blob/master/src/rt/execution.rs) implements dynamic partial-order reduction through dependency tracking, vector-clock comparisons, and recorded backtracking points. It also reuses execution storage between permutations and detects deadlock when no thread can run. The [runtime tree](https://github.com/tokio-rs/loom/tree/master/src/rt) separates atomics, locks, paths, scheduling, and causality support.

### 14. [dvyukov/relacy](https://github.com/dvyukov/relacy)

**C++ — header-based synchronization algorithm verifier for relaxed memory.** This is the author's repository, originally exported from Google Code; it is not presented here as a newly created checker. Study a compact library architecture with explicit scheduler policies and modeled synchronization types.

- **C1:** The [full-search scheduler](https://github.com/dvyukov/relacy/blob/master/relacy/full_search_scheduler.hpp) handles runnable/blocked threads, timed waits, spurious wakeups, yield priorities, and replay consistency checks. These are concrete failure modes beyond merely permuting thread starts.
- **C2:** Template-based scheduler composition and replacement `rl::atomic`/`rl::thread` types support many synchronization algorithms. The [library tree](https://github.com/dvyukov/relacy/tree/master/relacy) includes full-search, context-bounded, and random schedulers. The repository documents compiler-matrix testing and warns that its optional standard-header interception may need adaptation as toolchains change; the scheduler modes should not be treated as equivalent coverage guarantees.

### 15. [parapluu/Concuerror](https://github.com/parapluu/Concuerror)

**Erlang — stateless checking of Erlang programs.** Study reduction algorithms that understand message delivery, receive behavior, and shared ETS operations rather than only shared-memory reads and writes.

- **C1:** The [technical FAQ](https://github.com/parapluu/Concuerror/blob/master/docs/faq.md) describes instrumenting and reloading modules, recording interfering events, and replaying prefixes before changing event order. It explicitly explains abstractions for timeouts and limitations around native implemented functions (NIFs).
- **C3:** Optimal dynamic partial-order reduction uses knowledge of Erlang/OTP built-ins to avoid equivalent schedules; exploration bounds and race visualization help diagnose state explosion. These mechanisms are explained in the [FAQ](https://github.com/parapluu/Concuerror/blob/master/docs/faq.md).
- **C4:** The [changelog](https://github.com/parapluu/Concuerror/blob/master/CHANGELOG.md) spans releases from 2015 through 2020 and records OTP compatibility changes, litmus tests, EUnit infrastructure, and DPOR revisions. This supports sustained historical evolution, not a claim about current release cadence.

### 16. [microsoft/coyote](https://github.com/microsoft/coyote)

**C# — controlled concurrency testing with deterministic bug reproduction.** Included as systematic concurrency exploration rather than an unrestricted proof engine. Study how IL rewriting introduces a controlled scheduler into existing asynchronous application tests.

- **C1:** Coyote instruments managed assemblies to control task execution and nondeterminism. Its [binary-rewriting document](https://github.com/microsoft/coyote/blob/main/docs/concepts/binary-rewriting.md) discusses unsupported low-level concurrency, uncontrolled calls, and even exception-handler rewrites needed to preserve test cancellation.
- **C2:** The same testing engine and rewriting layer apply to task-based code, actors, and application unit tests. This is a reusable runtime/instrumentation architecture, not a checker for one protocol.
- **C3:** The [rewriting document](https://github.com/microsoft/coyote/blob/main/docs/concepts/binary-rewriting.md) explains component-level instrumentation and partially controlled exploration as responses to schedule explosion. Its iteration budgets and heuristic handling of uncontrolled dependencies must remain visible when interpreting results.

## Explicit and symbolic checking of software specifications

### 17. [tlaplus/tlaplus](https://github.com/tlaplus/tlaplus)

**Java — TLC model checker within the TLA+ tools monorepo.** The relevant subsystem is TLC under `tlatools`; the repository also contains the Toolbox IDE, which its README explicitly marks unmaintained. Study the operational machinery of checking distributed-system specifications.

- **C1:** [ModelChecker.java](https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/src/tlc2/tool/ModelChecker.java) coordinates initial-state computation, assumption failures, counterexamples, and liveness checking. Error paths must retain the original verification failure even when diagnostic replay behaves differently.
- **C3:** The implementation separates a fingerprint set of visited states, a queue of unexplored states, concurrent trace storage, and worker instances; it also recovers saved checking state. The [same implementation](https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/src/tlc2/tool/ModelChecker.java) is a useful starting point for studying how storage and parallel exploration constrain a checker’s design.

### 18. [apalache-mc/apalache](https://github.com/apalache-mc/apalache)

**Scala — symbolic checking of TLA+ and Quint specifications.** Study how a high-level specification language becomes a bounded SMT problem while retaining a separate frontend and checking pipeline.

- **C1:** The [theory document](https://github.com/apalache-mc/apalache/blob/main/docs/src/apalache/theory.md) derives the conjunction of initial-state and transition constraints, then adds a disjunction describing invariant failure at any checked step. It makes the parameter and execution-length assumptions concrete.
- **C2:** The [repository structure](https://github.com/apalache-mc/apalache) separates parsing, type checking, preprocessing, intermediate representations, passes, and the bounded-checking subsystem (`tla-bmcmt`), supporting reuse across specification inputs and analysis stages.
- **C3:** Values of intermediate states are solved symbolically rather than individually enumerated. The [encoding explanation](https://github.com/apalache-mc/apalache/blob/main/docs/src/apalache/theory.md) shows the precise architectural difference from TLC; it does not establish a universal performance advantage.

### 19. [nimble-code/Spin](https://github.com/nimble-code/Spin)

**C — explicit-state verification of Promela models of concurrent software.** Study generation of a model-specific C verifier and the consequences for state layout, property automata, and compile-time specialization.

- **C1:** The [verifier generator](https://github.com/nimble-code/Spin/blob/master/Src/pangen1.c) constructs process state, claim state, channels, and the global state vector. Correctly preserving that representation is fundamental to detecting safety and temporal-property violations.
- **C3:** Generated structures and compile-time options support specialized state representation and multicore verification. The repository documents distinct depth-first, breadth-first, bitstate, and partial-order-reduced searches; their coverage and storage properties should not be conflated.
- **C4:** The [version-6 history](https://github.com/nimble-code/Spin/blob/master/Doc/V6.Updates) records multi-year changes and concrete compatibility management, including a switch to restore old scoping rules while introducing inline temporal properties and new syntax.

### 20. [Smattr/rumur](https://github.com/Smattr/rumur)

**C++ generator and C verifier runtime — Murphi-compatible state-space checking.** Study a substantial separate implementation in the Murphi family, particularly its concurrent storage design. Rumur also exposes a parsing library for other Murphi tools.

- **C1:** The [CMurphi comparison](https://github.com/Smattr/rumur/blob/main/doc/vs-cmurphi.rst) carefully distinguishes assumptions, invariants, its specific liveness semantics, and “stuttering” versus “stuck” deadlocks. It also documents unsupported constructs; language compatibility is not universal.
- **C3:** The [seen-state-set design](https://github.com/Smattr/rumur/blob/main/doc/internals-seen-state-set.rst) explains an insert-only concurrent hash set, thread-local borrowed pointers, cooperative resizing, tombstones, and a synchronization rendezvous before replacing the table. This is unusually concrete material on the verifier’s own concurrency correctness and memory bottleneck.

### 21. [utwente-fmt/ltsmin](https://github.com/utwente-fmt/ltsmin)

**C/C++ — language-independent model-checking toolset.** Study an interface that lets different modeling languages benefit from shared exploration and reduction algorithms. Its integrations include Promela and other software/protocol modeling formalisms.

- **C2:** [PINS (`pins.h`)](https://github.com/utwente-fmt/ltsmin/blob/master/src/pins-lib/pins.h) defines a partitioned next-state interface, model types, transition groups, labels, and dependency matrices. Frontends supply semantic structure instead of only an opaque successor callback.
- **C3:** Read/may-write/must-write dependencies and matrix strictness rules provide information for reduction and transformation layers while stating which changes preserve semantics. The [PINS source](https://github.com/utwente-fmt/ltsmin/blob/master/src/pins-lib/pins.h) complements the [symbolic reachability command documentation](https://github.com/utwente-fmt/ltsmin/blob/master/doc/pins2lts-sym.txt). The repository describes symbolic, multicore, and distributed exploration; no comparative throughput claim is made here.

### 22. [stateright/stateright](https://github.com/stateright/stateright)

**Rust — embedded model checker and actor library for distributed systems.** Study the relationship between a generic transition-system API and executable actors, including explicit assumptions about message delivery.

- **C1:** The repository supports invariant checks and consistency checking while varying loss, duplication, and ordering of network messages. It explicitly marks eventual-property/liveness checking experimental and incomplete, so those results deserve a narrower interpretation than safety checks.
- **C2:** The [Model trait](https://github.com/stateright/stateright/blob/master/src/lib.rs) separates initial states, actions, transitions, and properties; actor-specific modeling builds on this general interface. Its documentation requires deterministic action ordering so stored paths can be reconstructed correctly. The [checker and actor source layout](https://github.com/stateright/stateright/tree/master/src) is a practical starting point for studying reuse between generic state exploration and distributed-system applications.

## Timed and probabilistic software models

### 23. [ticktac-project/tchecker](https://github.com/ticktac-project/tchecker)

**C++ — timed-automata checking framework and command-line tools.** Relevant to timing models of software and protocols, rather than source-language memory safety. Study how zone semantics, abstraction, and exploration can be varied separately.

- **C1:** The [algorithm documentation](https://github.com/ticktac-project/tchecker/blob/master/doc/usage.md) explains the correctness requirement for state covering: the covering relation must preserve trace inclusion. It also distinguishes elapsed/non-elapsed semantics and explains why omitting extrapolation can leave an infinite zone graph.
- **C3:** Zone inclusion and clock-bound abstractions discard subsumed states; search order, pool allocation sizes, and hash-table sizes expose concrete time/memory tradeoffs. The [same technical guide](https://github.com/ticktac-project/tchecker/blob/master/doc/usage.md) makes those mechanisms inspectable. It contains older command examples, so use it for algorithm design and consult the checked-out version’s help for exact CLI syntax.

### 24. [prismmodelchecker/prism](https://github.com/prismmodelchecker/prism)

**Java with C/C++ numerical backends — probabilistic model checking.** Relevant to probabilistic software/protocol models, including Markov chains and decision processes. Study how model construction and numerical solution can use different representations.

- **C1:** Quantitative properties depend on numerical semantics: the [engine documentation](https://www.prismmodelchecker.org/manual/ConfiguringPRISM/ComputationEngines) distinguishes iterative floating-point computation with a chosen precision from restricted exact-arithmetic checking. This is a substantive correctness issue, not merely an output-format detail.
- **C3:** MTBDD, sparse, hybrid, and explicit engines separate symbolic construction, matrix storage, and numerical work in different ways. The [technical comparison](https://www.prismmodelchecker.org/manual/ConfiguringPRISM/ComputationEngines) explains regularity-sensitive compression and why a large mostly unreachable state space can favor explicit construction. It also identifies the pure-Java explicit engine as an extensible implementation path.

### 25. [stormchecker/storm](https://github.com/stormchecker/storm)

**C++ — probabilistic model-checking framework.** Study an alternative architecture for quantitative verification, particularly when different query types favor different state representations and exploration strategies.

- **C1:** The [engine guide](https://www.stormchecker.org/documentation/background/engines.html) distinguishes numerical model checking, precision-dependent on-the-fly exploration, and abstraction refinement. It explicitly restricts some engines to discrete-time models or reachability objectives, preventing an assumption that all engines answer the same class of queries.
- **C3:** Sparse matrices and bit vectors support numerical operations; decision diagrams compress structured models; the hybrid engine transfers heavy numerical work to explicit structures; exploration can avoid building the entire model. The [architecture discussion](https://www.stormchecker.org/documentation/background/engines.html) also identifies the memory cost of converting to sparse matrices. These tradeoffs make Storm useful to compare with PRISM without asserting one is universally faster.

## Search coverage and limitations

Discovery used more than six distinct live-web query formulations, including: C/C++ bounded checking; Rust and Java concurrency checkers; explicit/symbolic specification checking; weak-memory checking with GenMC/Nidhugg/Dartagnan; Erlang and .NET systematic testing; configurable software verification; Murphi and timed automata; probabilistic and synchronous-language checking; and additional Go/Haskell/OCaml and distributed-state-exploration searches. Queries were followed by opening official repository pages, reading public source-tree listings, and reading implementation files, developer documents, or manuals. Search snippets were used for discovery, not as the sole evidence for retained entries.

The later searches increasingly returned the selected families, application-specific verification artifacts, general theorem-proving material, and experimental alternatives. This is a curated selection, not an exhaustive census: for example, the cross-language searches also surfaced DSCheck and Cubicle, which were not subjected to the same full inclusion review here. The report includes small research-community projects such as Rumur, TChecker, LTSmin, and Theta alongside widely used platforms, without using star counts as quality evidence.

Forks and monorepos were handled explicitly: ESBMC has substantial independent evolution; Rumur has a separate generated verifier and runtime architecture; Kani contributes its own Rust compiler integration; CBMC/JBMC and Ultimate’s multiple tools each count once. CPAchecker and GenMC remain included because their official GitHub mirrors contain substantive implementations. Duplicate artifact forks, tool lists, frontend-only wrappers, solver libraries, and hardware-only checkers were excluded. No claim is made about the absence of other good projects or about a uniform maintenance level across the selection.

Verification was read-only. No candidate was cloned, built, or executed, and no dependencies were installed. Some web-rendered GitHub pages and external manuals were unavailable; public raw source and repository documentation supplied the retained evidence instead. Documentation can lag implementation, especially CLI examples and research prototypes. C4 is claimed only where inspected history and compatibility/testing details support it; other entries are selected on C1–C3 without an inferred maintenance endorsement. The cited branch links describe the versions inspected and can change after the research date.
