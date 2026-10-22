# Distributed consistency and linearizability checkers

Research date: **2026-10-09**.

This selection covers 18 GitHub repositories that implement linearizability checking, transactional isolation analysis, or reusable distributed-consistency verification infrastructure. It includes executable sequential specifications, dependency-graph inference, constraint solving, timestamp-assisted checking, and model/proof-based approaches. JVM and Haskell concurrent-object checkers are included because their linearizability engines directly belong to the category; they are distinguished from network fault-injection tools. Database servers merely using another project's checker, generic chaos tools without a consistency oracle, and general-purpose theorem provers are outside the main selection.

The criteria below describe reasons to study particular subsystems, not a certification of every component. Passing a finite history or a bounded exploration does not establish correctness for every execution. History instrumentation, the specification, treatment of incomplete operations, and the exact isolation definition remain part of the trusted setup.

## Criteria legend

- **C1 — Difficult correctness:** substantial invariants, concurrency semantics, adversarial histories, or failure handling.
- **C2 — Reusable abstractions:** meaningful models, protocols, interfaces, or composition mechanisms supporting multiple systems and workloads.
- **C3 — Performance with structure:** explicit techniques for controlling search, graph, solver, or memory costs while retaining an understandable decomposition.
- **C4 — Sustained evolution:** documented changes over years, coupled with compatibility work, testing, or complexity management. Age, stars, and recent pushes alone do not qualify.

Repository identities, default branches, archive flags, and relevant source paths were checked against repository pages and the GitHub API. Languages below describe the relevant implementation, rather than GitHub's sometimes misleading majority language for repositories containing vendored solvers or generated artifacts. Research artifacts are identified as such; no general promise of active maintenance is inferred from an unarchived repository.

## General linearizability engines and concurrent-object testing

### 1. [anishathalye/porcupine](https://github.com/anishathalye/porcupine)

**Language / role:** Go; embeddable linearizability checker with history visualization.

Porcupine accepts an executable sequential specification and either timestamped operations or ordered invocation/return events. It is a useful starting point for studying how a formal property becomes a relatively small library API, including nondeterministic specifications and partial linearizations for explaining failures. Its implementation combines reversible manipulation of a history with memoized search; partitioning is supplied by the model author rather than guessed by the checker.

- **C1:** The model contract requires pure state transitions, correct state equality, and equal hashes for equal states. Partitioning must preserve an equivalence: the whole history is linearizable exactly when every partition is. These are correctness obligations on optimizations, not merely callback conventions. See [model.go](https://github.com/anishathalye/porcupine/blob/master/model.go).
- **C2:** `Model` and `NondeterministicModel` separate application semantics from history formats and the decision procedure. Optional descriptions and metadata connect the same model to diagnostic visualization.
- **C3:** [checker.go](https://github.com/anishathalye/porcupine/blob/master/checker.go) caches pairs of linearized-operation bitsets and model states, removes/reinserts matched calls during backtracking, and supports cancellation during model steps. This exposes the relationship between state-space reduction, allocation, and responsiveness.

**Entry points:** the two source files above. General histories can still cause state-space explosion; the repository also discusses timestamp-recording hazards on weakly ordered machines. The advertised speedup figures are not treated here as independently reproduced measurements.

### 2. [jepsen-io/knossos](https://github.com/jepsen-io/knossos)

**Language / role:** Clojure/JVM; history-based linearizability analysis used by Jepsen.

Knossos is especially valuable for understanding histories obtained from unreliable systems. Its operation vocabulary distinguishes invocation, success, definite failure, and indeterminate completion. Its model interface can represent registers and other state machines, while separate search engines explore legal linearizations. The repository explicitly cautions readers to inspect reported results rather than regard the implementation as an unquestionable oracle.

- **C1:** [linear.clj](https://github.com/jepsen-io/knossos/blob/master/src/knossos/linear.clj) distinguishes pending calls, linearized calls awaiting return, and completed operations. Transitions must update both the sequential model and process state correctly, including the orders in which pending operations can take effect.
- **C2:** A user-defined model is independent of the search algorithm. The public competition analysis accepts a model, history, and execution options, and returns validity plus debugging information.
- **C3:** The graph-search implementation memoizes equivalent configurations to prune duplicate exploration. [competition.clj](https://github.com/jepsen-io/knossos/blob/master/src/knossos/competition.clj) runs the graph and WGL analyses together and terminates when an engine reaches a decision; time limits can produce an unknown result.

**Entry points:** `linear.clj` for the transition/search machinery and `competition.clj` for orchestration. This is a useful contrast with Porcupine: compare representations and pruning strategies without assuming that one benchmark establishes universal superiority.

### 3. [ahorn/linearizability-checker](https://github.com/ahorn/linearizability-checker)

**Language / role:** C++11; historical research implementation and experimental corpus for efficient linearizability checking.

This repository contains the actual checker in a large `lt.cc` translation unit, together with histories and experiment settings. It is a good study of the concrete engineering behind partitioned checking and search caches. The supplied workloads span concurrent sets and etcd histories. Treat it as a historical research artifact, not a currently maintained C++ library: the inspected GitHub metadata reports its last push in 2015.

- **C1:** [lt.cc](https://github.com/ahorn/linearizability-checker/blob/master/lt.cc) states invariants for the stack of tentatively linearized calls and the remaining linked history. `lift`/`unlift` must reversibly remove and restore both halves of an operation; state and operation bitsets must also roll back together.
- **C3:** The same source separates cache policy through templates, offers alternative caching choices including LRU, and slices suitable histories into partitions. Timeouts, iteration counts, and memory instrumentation make the resource consequences of these choices observable. The [Makefile](https://github.com/ahorn/linearizability-checker/blob/master/Makefile) exposes experiments for the supplied workloads.

**Entry points:** `LinearizabilityTester`, `LruCache`, and `Slicer` inside `lt.cc`; then the experiment Makefile. Its concentration in one source file is itself an architectural limitation, although internal classes make the algorithmic boundaries inspectable. The intentionally weak etcd read configuration described by the authors should not be misreported as evidence that default etcd behavior is broken.

### 4. [rystsov/fast-jepsen](https://github.com/rystsov/fast-jepsen)

**Language / role:** Clojure; historical Jepsen checker prototype for a restricted CAS-based register workload.

This is a deliberately specialized alternative to general state-space search. Updates carry unique write IDs and predecessor IDs, allowing the checker to reconstruct a chain of accepted versions and determine whether reads lag behind a version already known when they began. The repository calls itself a proof of concept, and its inspected metadata reports a last push in 2018. Its value is the reduction and explicit implementation, rather than breadth or current packaging.

- **C1:** [fchecker.clj](https://github.com/rystsov/fast-jepsen/blob/master/jepsen/src/src/mongo_http/fchecker.clj) rejects reused write IDs, competing successor chains, reads of unproposed versions, stale observations, and value/version mismatches. It separately tracks pending writes and the accepted head seen by each pending read.
- **C3:** The algorithm trades a richer workload contract for substantially simpler checking: accepted version chains replace general permutation search. Its history merge scans per-thread queues; the claim of linear scaling depends on treating concurrency as fixed. The [design explanation](https://github.com/rystsov/fast-jepsen#checker) states the required CAS and version assumptions.

**Entry points:** the checker implementation and README's checker section. This is not a drop-in checker for arbitrary reads and writes. Its history filtering and older Jepsen protocol signature deserve attention before reuse. The implementation comments and README do not present identical complexity wording, so no unconditional complexity or throughput claim is adopted here.

### 5. [JetBrains/lincheck](https://github.com/JetBrains/lincheck)

**Language / role:** Kotlin and Java; JVM concurrent testing with a substantive linearizability verifier.

The relevant subsystem is the declarative concurrent-data-structure API and its verifiers; the wider project also tests arbitrary concurrent code. Lincheck generates scenarios, exercises them through stress testing or managed exploration, and checks results against sequential behavior. Its lineage is the Devexperts Lin-Check framework, but the JetBrains implementation has substantial independent evolution; the ancestor is not counted separately.

- **C1:** [LinearizabilityVerifier.kt](https://github.com/JetBrains/lincheck/blob/master/lincheck/src/jvm/main/org/jetbrains/lincheck/datastructures/verifier/LinearizabilityVerifier.kt) combines labeled-transition-system legality with happens-before clocks. It also tracks suspended operations, cancellation, and remapped resumption tickets—considerably more subtle than simply enumerating completed method calls.
- **C2:** [AbstractLTSVerifier.kt](https://github.com/JetBrains/lincheck/blob/master/lincheck/src/jvm/main/org/jetbrains/lincheck/datastructures/verifier/AbstractLTSVerifier.kt) supplies shared search infrastructure over a sequential specification. The surrounding framework separates operation declarations, scenario execution, and the selected correctness property.
- **C3:** The verifier hierarchy caches previously processed execution results and explores only transitions consistent with recorded ordering. The [release notes](https://github.com/JetBrains/lincheck/releases) also document ongoing work on instrumentation and loop detection, illustrating the costs surrounding the oracle itself.

**Entry points:** the two verifier files. This primarily checks in-process JVM concurrency; it does not supply Jepsen-style network partitions or independently verify a deployed distributed database. Current package/API names differ from older `org.jetbrains.kotlinx.lincheck` examples.

### 6. [stevana/quickcheck-state-machine](https://github.com/stevana/quickcheck-state-machine)

**Language / role:** Haskell; model-based generation, shrinking, execution, and linearizability checking of stateful programs.

This is the maintained successor fork identified by the package's changelog and Hackage metadata, not an additional copy of the archived `advancedtelematic` repository. Study the connection between typed symbolic commands, concrete resources returned by execution, preconditions, and parallel history checking. The relevant subsystem is `Test.StateMachine.Parallel`.

- **C1:** [Parallel.hs](https://github.com/stevana/quickcheck-state-machine/blob/master/src/Test/StateMachine/Parallel.hs) generates parallel-safe command groups whose preconditions survive alternative orders, shrinks while preserving scope and preconditions, and linearizes observed histories by checking model postconditions along candidate interleavings.
- **C2:** A reusable state-machine description supplies transitions, execution semantics, and pre/postconditions. The parallel machinery works over generic command and response types rather than a fixed register or database protocol.
- **C4:** The [changelog](https://github.com/stevana/quickcheck-state-machine/blob/master/CHANGELOG.md) documents the 2021 successor transition, compiler compatibility and CI changes in 2023–2024, and dependency compatibility updates through 2026. It also explains removals and API changes, including revised repetition semantics and a diffing abstraction.

**Entry points:** `Parallel.hs` and `CHANGELOG.md`. A concrete limitation appears in the inspected linearizer: its `Crash` branch remains unimplemented. That matters for fault-oriented testing and prevents treating the framework's parallel checking as a complete substitute for an uncertain-operation distributed history model.

## Distributed testing and executable protocol models

### 7. [jepsen-io/jepsen](https://github.com/jepsen-io/jepsen)

**Language / role:** Clojure; distributed fault-injection, history collection, checker composition, and reporting framework.

Jepsen is retained for its own reusable test and checker architecture, not as another implementation of Knossos or Elle. Its control node schedules clients and a nemesis, records operation boundaries, and persists the resulting history and analysis. An engineer can study how a trustworthy oracle is embedded in the much messier lifecycle of deployment, failures, client exceptions, and incomplete tests.

- **C1:** [checker.clj](https://github.com/jepsen-io/jepsen/blob/main/jepsen/src/jepsen/checker.clj) distinguishes valid, invalid, and unknown results; checker exceptions become unknown instead of silently passing. Its built-in set, queue, counter, and unique-ID checks have workload-specific semantics beyond the delegated linearizability engine.
- **C2:** The `Checker` protocol and `compose` combine independent checks while preserving named results and an aggregate verdict. The repository's [design overview](https://github.com/jepsen-io/jepsen#design-overview) separates client, generator, nemesis, operating-system, and database responsibilities, allowing the same infrastructure to test unrelated distributed systems.

**Entry points:** the checker source and [Jepsen changelog](https://github.com/jepsen-io/jepsen/blob/main/jepsen/CHANGELOG.md). Recent changelog entries describe both oracle fixes and a fault-injection regression in which some kill/pause faults did nothing. That is unusually instructive evidence that test-harness correctness is itself part of the problem. Do not equate the framework's availability with a ready-made, correct workload for a particular database.

### 8. [stateright/stateright](https://github.com/stateright/stateright)

**Language / role:** Rust; distributed actor modeling/runtime with embedded linearizability and sequential-consistency testers.

Stateright joins executable actors, configurable network semantics, and model exploration. The selected subsystem captures client operations against a sequential reference object while the surrounding model checker explores message delivery choices. This gives a different route to finding consistency failures from collecting one history of an externally deployed system.

- **C1:** [linearizability.rs](https://github.com/stateright/stateright/blob/master/src/semantics/linearizability.rs) records the last operation completed by other threads when a new operation starts. Those indices constrain serialization so that non-overlapping operations respect real-time precedence. The implementation also distinguishes malformed histories from well-formed but inconsistent ones.
- **C2:** [consistency_tester.rs](https://github.com/stateright/stateright/blob/master/src/semantics/consistency_tester.rs) defines a common interface around a `SequentialSpec`; the implementation is generic over operation, return, and thread-ID types. The wider actor model offers selectable loss, duplication, and ordering behavior for the network.

**Entry points:** the linearizability implementation and common tester trait. Included examples cover an ABD-style register and Paxos, making the connection between message-level transitions and client-visible specifications concrete. Conclusions from exploration remain relative to the modeled system, network assumptions, and explored state space. The inspected repository is unarchived, but no current maintenance-rate claim is made.

## Transactional dependency graphs and constraint solvers

### 9. [jepsen-io/elle](https://github.com/jepsen-io/elle)

**Language / role:** Clojure and Java checker, with Isabelle proof material; black-box transactional anomaly detection.

Elle infers dependencies from observable transactional operations and searches for cycles forbidden by the chosen consistency model. Its strongest engineering lesson is the separation between deriving an edge and explaining that edge to a human. Register and list-append workloads provide different amounts of recoverable version-order information; the checker does not require a database-specific internal transaction scheduler.

- **C1:** Dependencies must remain justified despite failed or indeterminate operations and partially observed version orders. The [repository documentation](https://github.com/jepsen-io/elle#completeness) explicitly explains that the checker is incomplete and limits its inference to tractable cases; an absence of reported anomalies is not a general serializability proof.
- **C2:** [core.clj](https://github.com/jepsen-io/elle/blob/main/src/elle/core.clj) separates analyzers, dependency graphs, and explainers. Composed analyses union their graphs and retain the corresponding explanation machinery, allowing process, real-time, and data-derived relations to work together.
- **C3:** The same source explains why expensive history indexes are retained in explainers, and submits component analyses as tasks through the history executor. Strongly connected components and targeted cycle explanations replace exhaustive sequential-state replay for applicable workloads.

**Entry points:** `core.clj` and [consistency_model.clj](https://github.com/jepsen-io/elle/blob/main/src/elle/consistency_model.clj). Treat the repository's proof material as supporting work, not a completed machine-checked proof of the implementation. The Jepsen changelog also records fixes to Elle's inference, reinforcing the importance of auditing witnesses and exact versions.

### 10. [amnore/PolySI](https://github.com/amnore/PolySI)

**Language / role:** Java with MonoSAT integration; research snapshot-isolation checker.

PolySI is a clear example of turning uncertainty about version order into alternative dependency constraints. Its pipeline first checks internal transaction consistency, constructs known edges, produces constraints, prunes consequences, and invokes a solver. It can ingest Cobra, DBCop, or text histories and produces conflicting transactions when rejecting a history. This is a research implementation; current maintenance is not asserted.

- **C1:** [SIVerifier.java](https://github.com/amnore/PolySI/blob/master/src/main/java/verifier/SIVerifier.java) constructs paired ordering alternatives for transactions writing the same key, together with the induced read-write dependencies. It retains the involved edges and transactions for conflict reporting, rather than reducing every rejection to a Boolean.
- **C2:** Generic history loaders and key/value types separate input representation from the checking pipeline. Coalescing and pruning can be controlled independently, supporting experiments with the same histories.
- **C3:** [Pruning.java](https://github.com/amnore/PolySI/blob/master/src/main/java/verifier/Pruning.java) uses graph composition and reachability to resolve alternatives before solving, iterates until a threshold or contradiction, and profiles individual stages. Constraint coalescing avoids generating equivalent choices repeatedly.

**Entry points:** `SIVerifier.java` and `Pruning.java`. This is specifically SI analysis; serializability, strict serializability, and session guarantees should not be inferred from a successful SI verdict. The source is useful even if the original artifact's native-solver build environment needs reconstruction.

### 11. [Khoury-srg/Viper](https://github.com/Khoury-srg/Viper)

**Language / role:** Python checker and graph construction, backed by native SAT/SMT libraries; research snapshot-isolation analysis.

Viper exposes several encodings of SI, making it a strong comparison project for engineers deciding which semantic facts belong in graph construction and which should remain solver choices. Its begin/commit representation distinguishes the endpoints of a transaction instead of treating a transaction as one undifferentiated graph vertex. Vendored C++ dependencies account for much of the repository's language footprint.

- **C1:** [checkers.py](https://github.com/Khoury-srg/Viper/blob/main/src/checker/checkers.py) maps different dependency kinds to different begin/commit endpoints, asserts transaction-internal ordering, encodes alternative edges, and asks for acyclicity. Getting these edge directions wrong changes the consistency property being checked.
- **C3:** The implementation contains Z3 and MonoSAT variants, including optimized graph encodings, with separate encoding and solving timers. [build_graph4adyaSI_chain.py](https://github.com/Khoury-srg/Viper/blob/main/src/buildgraph/build_graph4adyaSI_chain.py) isolates known-edge construction, write/read indexing, and constraint generation from the solver layer.

**Entry points:** those two files. The authors explicitly note stale paths in the artifact instructions. They also distinguish default Adya SI from strong-session SI, which requires enabling session-order edges. This matters when comparing Viper with a checker whose nominal “SI” option includes different order constraints. The selection is based on architecture and implementation, not on reproducing the paper's performance measurements.

### 12. [DBCobra/CobraVerifier](https://github.com/DBCobra/CobraVerifier)

**Language / role:** Java with CUDA/native components and MonoSAT; historical serializability verification research artifact.

CobraVerifier checks transaction histories either in one shot or in rounds. The latter is particularly instructive: retaining every past transaction is not viable for long-running verification, but deleting a transaction can destroy evidence relevant to later observations. The artifact makes the interplay between solver constraints, epochs, and history reclamation explicit. Its documented environment is tied to an older Java/CUDA stack; inspected repository metadata reports a last push in 2020.

- **C1:** [MonoSATVerifierRounds.java](https://github.com/DBCobra/CobraVerifier/blob/master/src/main/java/verifier/MonoSATVerifierRounds.java) tracks frozen components, frontiers, and safe deletion candidates. Reclamation checks reads from deleted transactions and preserves transitive relationships needed by subsequent rounds.
- **C3:** The rounds pipeline constructs the relevant graph, prunes constraints using a reachability matrix, divides suitable work into independent components, solves them, and garbage-collects old transactions. [MonoSATVerifierOneshot.java](https://github.com/DBCobra/CobraVerifier/blob/master/src/main/java/verifier/MonoSATVerifierOneshot.java) provides the corresponding whole-history path for comparison.

**Entry points:** the rounds implementation and one-shot implementation. The README states that round-based verification requires fence transactions generated by the cooperating benchmark client, and the documented build requires an NVIDIA GPU. Those are concrete instrumentation and deployment constraints, not interchangeable implementation details. This repository is counted once; its companion workload/log repositories are not independent checker entries.

### 13. [CzxingcHen/VeriStrong](https://github.com/CzxingcHen/VeriStrong)

**Language / role:** C++; research checker for serializability and snapshot isolation with a specialized MiniSat-based backend.

VeriStrong moves beyond feeding all transactional structure through a generic graph-solver interface. Its source represents known dependencies, alternative write orders, and sets of possible writers for a read, then passes this structure to specialized solver implementations. The repository also contains baselines and experiment material; the relevant original subsystem is `veristrong/`, not the bundled copies of other checkers.

- **C1:** [acyclicMinisatSolver.cpp](https://github.com/CzxingcHen/VeriStrong/blob/main/veristrong/src/solver/acyclicMinisatSolver.cpp) preserves dependency types and keys while remapping transaction IDs. It carries both write-write alternatives and read-from candidate sets, which is significant when an observation cannot identify a unique writer. SER and SI dispatch to distinct backend paths.
- **C3:** [pruner.cpp](https://github.com/CzxingcHen/VeriStrong/blob/main/veristrong/src/solver/pruner.cpp) resolves unit constraints, updates typed dependency graphs, checks for contradictions using graph algorithms, and contains further reachability-oriented pruning machinery. The command-line interface exposes solver/pruning choices, and the artifact records construction, pruning, encoding, and solving costs separately.

**Entry points:** the solver adapter and pruner. This is a research artifact with compile-time experimental variants, not a claim of a stable production SDK. The code includes incomplete optimization work for particular paths; the presence of a specialized solver should not be generalized into uniform optimization of every isolation mode.

### 14. [dracoooooo/Plume](https://github.com/dracoooooo/Plume)

**Language / role:** Java checker, Rocq mechanization, and experimental tooling; weak transactional-isolation analysis.

Plume targets read committed, read atomicity, and transactional causal consistency through transactional anomalous patterns. It provides a useful counterpoint to SI/SER solvers: for these weaker levels, explicit graph traversal and causal summaries can be the central machinery. The relevant implementation lives in `Plume/`; bundled comparison tools are not additional original implementations.

- **C1:** [Plume.java](https://github.com/dracoooooo/Plume/blob/main/Plume/src/main/java/alg/Plume.java) maps isolation levels to prohibited patterns and distinguishes thin-air, aborted, intermediate, non-repeatable, fractured, and causality-related observations. It constructs ordering relationships and associates detected anomalies with the selected level.
- **C3:** The algorithm separates graph construction from traversal and uses clock-bearing nodes to summarize dependencies. [TreeClock.java](https://github.com/dracoooooo/Plume/blob/main/Plume/src/main/java/util/TreeClock.java) implements tree clocks with packed array-based structure, making clock joins and traversal costs inspectable rather than hiding them behind a solver invocation.

**Entry points:** `Plume.java` and `TreeClock.java`. A material recent qualification: the authors' [2026 mechanization paper](https://arxiv.org/abs/2610.07665) reports corrections to the original history model and read-atomicity characterization, including session guarantees, and says these refinements were integrated into Plume. Check the exact revision and definitions before relying on a completeness claim. This report does not independently establish correspondence between every code path and the mechanized theorems.

## Alternative evidence sources and integrated analysis platforms

### 15. [lucidliy/TimeKiller](https://github.com/lucidliy/TimeKiller)

**Language / role:** Java; timestamp-assisted offline and online SI/SER checking, named Chronos and Aion.

TimeKiller deliberately uses stronger observations than black-box read/write histories: transaction start and commit timestamps. Its formats accept hybrid logical timestamps, and its offline and online modes expose different memory-management choices. Study it when a database can export meaningful transaction-order metadata and the cost of inferring all possible orders would be excessive.

- **C1:** [SIFastChecker.java](https://github.com/lucidliy/TimeKiller/blob/main/src/main/java/checker/si/SIFastChecker.java) distinguishes internal consistency, external reads, and overlapping write conflicts. It compares a transaction's start timestamp with prior commit timestamps to determine which written value should be visible and returns structured violations.
- **C3:** [SEROnlineChecker.java](https://github.com/lucidliy/TimeKiller/blob/main/src/main/java/checker/ser/SEROnlineChecker.java) maintains commit frontiers, revisits external-read conclusions when additional transactions arrive, and accesses garbage-collected transaction state through a storage layer. The architecture makes the tension between late information, memory limits, and incremental checking explicit.

**Entry points:** the offline SI and online SER implementations. The [input documentation](https://github.com/lucidliy/TimeKiller#input-file-format) defines timestamp fields; arbitrary wall-clock observations are not automatically substitutes for the intended database timestamps. Online timeouts and reclamation settings also affect operation. This is a research implementation, and its sample runtimes are not independently validated here.

### 16. [jasonqiu98/GRAIL-artifact](https://github.com/jasonqiu98/GRAIL-artifact)

**Language / role:** Go and Java, with AQL/Cypher queries; archived research artifact for graph-query-based isolation checking.

GRAIL materializes transaction/event dependency graphs in graph databases and uses graph queries or graph algorithms to detect forbidden cycle patterns. It includes ArangoDB and Neo4j approaches. That architecture is distinct from an in-memory Clojure graph or an SAT encoding, and exposes ingestion, querying, and diagnostics as separate costs. GitHub marks the repository **archived**.

- **C1:** [list_append.go](https://github.com/jasonqiu98/GRAIL-artifact/blob/main/go-graph-checker/list_append/list_append.go) distinguishes forbidden cycles for SER, SI, PSI, and weaker levels. For example, the positions and number of read-write edges matter; detecting any graph cycle is not a correct universal isolation test.
- **C3:** The artifact compares traversal, shortest-path, and graph-algorithm approaches, with profiling experiments described in its README. The source separates dependency-graph construction from level/mode dispatch and witness formatting, making query-plan and graph-storage choices accessible to study.

**Entry points:** the list-append checker and [rw_register/graph.go](https://github.com/jasonqiu98/GRAIL-artifact/blob/main/go-graph-checker/rw_register/graph.go). The latter uses WAL-derived version information and explicitly checks mismatches between operation histories and those logs; it should not be described as uniformly black-box. Some traversal variants have bounded search depths, so their results must be interpreted according to the chosen mode rather than assuming all variants are complete.

### 17. [hengxin/IsoVista](https://github.com/hengxin/IsoVista)

**Language / role:** Java checking core with web frontend/backend; integrated database-isolation testing, visualization, and profiling platform.

IsoVista is retained for its integration architecture and in-tree checking code, not counted as another independent invention of every incorporated algorithm. Its platform spans workload execution, multiple history formats, several isolation levels, and anomaly visualization. It is useful for studying how to put different checkers behind a consistent experiment and explanation interface.

- **C1:** [C4.java](https://github.com/hengxin/IsoVista/blob/main/src/main/java/checker/C4/C4.java) constructs session and data-derived ordering relationships, detects transactional patterns, and produces bug graphs. This is substantive checking logic in addition to adapters for other tools.
- **C2:** The [checker extension guide](https://github.com/hengxin/IsoVista/blob/main/docs/how-to-implement-a-new-checker.md) defines a contract for verification, DOT witnesses, and per-stage profiling. It explicitly accommodates native/JNI and subprocess implementations, including registering child processes for resource monitoring.
- **C3:** The interface distinguishes construction/traversal timing from construction/encoding/pruning/solving timing. That lets users compare algorithms with different internal architectures without collapsing all costs into one opaque runtime.

**Entry points:** the C4 implementation and checker extension guide. The platform shares research lineage and code with other selected tools; their counts are repository counts, not counts of independent algorithms. Its own documentation notes resource limits on workload parameters. Completeness claims should be checked against the exact underlying checker, formal definition, and revision, especially for weak-isolation characterizations.

## Mechanized causal-consistency verification

### 18. [rocq-community/chapar](https://github.com/rocq-community/chapar)

**Language / role:** Coq/Rocq and extracted OCaml; causal-consistency framework with a verified client-program model checker.

Chapar belongs at the proof-oriented edge of this category. It supplies formal operational semantics and proofs for replicated key-value stores, plus executable schedule checking for client behavior under the abstract semantics. It is not a drop-in analyzer of production log files. Its distinctive lesson is how to connect a checker implementation to the semantics it is intended to explore.

- **C1:** [ReflectiveAbstractSemantics.v](https://github.com/rocq-community/chapar/blob/master/theories/Framework/ReflectiveAbstractSemantics.v) implements schedule enumeration over process steps and inter-node updates. It proves soundness/completeness connections for executable steps and relates successful checking to absence of client faults under stated assumptions.
- **C2:** The framework separates syntax parameters, concrete store algorithms, abstract execution, and reflective checking. An engineer can study how one causal-consistency model supports multiple store implementations and client programs rather than one hard-coded execution trace.
- **C4:** The [changelog](https://github.com/rocq-community/chapar/blob/master/CHANGELOG.md) documents compatibility work from 2019 through 2023: Coq version migrations, tactic and lemma updates, Dune extraction/build restructuring, and CI repairs. This is concrete maintenance of a proof artifact across toolchain changes; no claim of recent feature development is made.

**Entry points:** the reflective semantics/checker and changelog. A finite schedule bound remains a bound; theorem hypotheses and any quantification over bounds must be read carefully. The canonical GitHub organization is now `rocq-community`, while some internal historical links still use `coq-community`.

## Coverage, search method, and limitations

Discovery used live web search with more than six distinct formulations, including: general linearizability libraries; Go/Java/Rust/Python implementations; C++ partitioning research; Haskell parallel state-machine testing; causal-consistency checkers; black-box serializability verification; SI polygraph/SMT tools; weak-isolation anomaly detection; timestamp/white-box checking; and graph-database query approaches. Targeted follow-ups covered Cobra, PolySI, Viper, Plume, VeriStrong, TimeKiller, IsoVista, Emme, DBCop, and successor-repository provenance. Later generic and language-specific searches increasingly returned known engines, applications embedding them, ports, teaching projects, or unrelated uses of “consistency.” Primary source inspection, rather than search rank or stars, determined retention.

For every retained entry, the canonical repository was opened or verified through the GitHub API, and additional implementation or design material was read. Recursive source-tree metadata was used to verify exact paths; selected source files were read without cloning or executing candidate projects. The API also exposed archive status and helped distinguish original checker code from vendored baselines. Root repository documentation was not counted twice merely because it was available through a raw URL.

Important boundaries and exclusions:

- **DBCop:** the primary literature and inspected GitHub copy point to a GitLab upstream. This search did not establish an authoritative substantive GitHub verifier mirror or independently evolved GitHub checker suitable for this list. Its importance to the literature is acknowledged, but it is not represented by an invented or ambiguously attributed canonical repository.
- **Emme:** discovered through papers and related projects, but no verified official substantive GitHub implementation was established. A comparison project's reimplementation is not treated as the original tool.
- **Thin frontends and duplicates:** `elle-cli`, ports that mainly reproduce another engine, bundled baselines, and old/new copies of the same library were not separate entries. IsoVista is included for its substantive checking and integration architecture; algorithmic overlap is disclosed.
- **Adjacent tools:** generic chaos injectors, general model checkers without a category-specific subsystem, database implementations that only call Porcupine/Elle, awesome-lists, and tutorial exercises were excluded. Maelstrom's teaching workbench was not added simply to expand the Jepsen family count. The small `fast-jepsen` artifact is retained specifically for its implemented CAS/version-chain reduction, with its prototype status explicit.
- **Limits of verification:** this was source/document research, not a build, benchmark reproduction, proof audit, or comprehensive test run. Artifact environments may require repair. No comparative throughput claims were independently measured. C4 is awarded only where dated compatibility/evolution evidence was inspected; research artifacts can qualify through C1 and C3 without an invented maturity claim.

The descriptions of code paths and documented contracts are source-grounded facts. Judgments about what is especially useful to study, and the resulting C1–C4 selections, are engineering inferences from that evidence. A deployed checker should be selected by its observation requirements and exact semantics as well as its implementation quality.
