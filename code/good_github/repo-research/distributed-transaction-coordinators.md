# Distributed transaction coordinators

Research date: **2026-10-09**.

Scope: 19 GitHub repositories implementing transaction coordination across resource managers, services, distributed storage, or actor state. The selection covers XA/JTA two-phase commit, TCC, compensating sagas, and storage-oriented commit protocols. These mechanisms offer different guarantees: a saga's application-defined compensation is not an atomic database rollback. Embedded and decentralized coordinators are included when their coordination implementation is substantial and identifiable. General workflow engines, transaction API declarations without implementations, and databases included merely because they support transactions are outside this selection.

This is a guide to code worth studying, not a production-readiness ranking or a claim that every component is exemplary. Repository identities and relevant primary materials were checked live. Links generally follow the inspected development branch; they do not establish that every described feature is in a released version.

## Criteria legend

- **C1 — Difficult correctness:** meaningful invariants, concurrency, uncertainty, crash recovery, or other failure semantics.
- **C2 — Reusable abstractions:** substantial interfaces and components applicable to different resources or applications.
- **C3 — Performance with structure:** concrete mechanisms addressing coordination, persistence, contention, or execution costs within an understandable architecture.
- **C4 — Sustained evolution:** dated evolution accompanied by compatibility work, testing, or explicit complexity management. Creation dates, stars, and recent pushes alone do not qualify.

## XA/JTA managers and transaction-processing middleware

### 1. [jbosstm/narayana](https://github.com/jbosstm/narayana)

**Language/role:** Java; transaction manager spanning ArjunaCore, JTA, JTS, and web-service transaction protocols. The monorepo is counted once.

Study how a reusable coordination core separates transaction execution from recovery. The particularly instructive problem is deciding whether an apparently unfinished transaction needs recovery or is still running in its original process.

- **C1:** Recovery uses persistent object-store records, two scanning passes, and a transaction-status check before taking over work. The documentation explicitly explains why recovering a still-live transaction can break consistency, and why losing the object store can make recovery impossible.
- **C2:** `RecoveryModule` supplies pluggable recovery passes, while the core is exposed through different transaction APIs and protocol layers. This is a useful model for sharing durable coordination machinery without making every resource integration implement the entire manager.

**Entry point:** [Project documentation, especially Failure Recovery and JTA/JTS](https://www.narayana.io/docs/project/index.html). The repository README also describes separate unit, integration, and QA suites; those are useful navigation aids, not proof that all failure cases are covered.

### 2. [atomikos/transactions-essentials](https://github.com/atomikos/transactions-essentials)

**Language/role:** Java; embeddable JTA/XA manager. The repository identifies itself as the project's community development **mirror** and contains the substantive implementation under `public/`.

Study the coordinator as a finite-state machine whose state handlers control prepare, commit, rollback, timeout, and heuristic outcomes.

- **C1:** `CoordinatorImp` rejects recursive preparation and preparation with active sibling transactions, serializes operations on the FSM, and distinguishes heuristic commit, abort, mixed, and hazard states. Those distinctions expose the gap between a requested outcome and what participants actually report.
- **C2:** The coordinator implements participant and recovery interfaces itself, allowing subordinate coordination. The surrounding JDBC/JMS integrations adapt different resource types to that reusable core.
- **C3:** Termination selects one-phase commit for at most one participant and avoids a second commit phase for a read-only vote, illustrating protocol-level savings rather than an unsupported throughput claim.

**Entry point:** [CoordinatorImp and its state-handler interactions](https://github.com/atomikos/transactions-essentials/blob/master/public/transactions/src/main/java/com/atomikos/icatch/imp/CoordinatorImp.java).

### 3. [scalar-labs/btm](https://github.com/scalar-labs/btm)

**Language/role:** Java; Bitronix JTA/XA transaction manager. The former `bitronix/btm` URL redirects here; the README documents Scalar's takeover. This is one project, not two independent implementations.

Study a comparatively focused implementation of XA journal reconciliation and resource recovery.

- **C1:** Recovery correlates dangling journal records with XIDs returned by resources, commits branches with a durable committing decision, and rolls back appropriate remaining branches. It filters ownership and considers the oldest in-flight transaction so recovery does not blindly interfere with current work. An atomic running flag prevents overlapping recovery executions.
- **C2:** Resource registration and `XAResourceProducer` objects reconstruct the resources needed for recovery; the journal and resource interfaces keep this logic independent of a particular JDBC database or JMS provider.

**Entry point:** [Recoverer, including its recovery algorithm commentary](https://github.com/scalar-labs/btm/blob/master/btm/src/main/java/bitronix/tm/recovery/Recoverer.java). Its value is the explicit correspondence between journal state, resource state, and recovery actions.

### 4. [apache/geronimo-txmanager](https://github.com/apache/geronimo-txmanager)

**Language/role:** Java; reusable transaction-manager and connector components. **Official Apache GitHub mirror.**

Study imported transactions and resource identity during recovery, rather than treating every recovered XID as locally owned.

- **C1:** Recovery separates locally initiated transactions from externally coordinated ones. It commits only when the recovered resource name belongs to the logged branch; an externally prepared branch waits for its originator's decision. It also handles invalid XIDs and XA heuristic outcomes. [RecoveryImpl](https://github.com/apache/geronimo-txmanager/blob/trunk/geronimo-transaction/src/main/java/org/apache/geronimo/transaction/manager/RecoveryImpl.java).
- **C2:** `TransactionLog` abstracts preparation records, branch lists, commit/rollback markers, and reconstruction through an XID factory. This is a concrete boundary between transaction semantics and logging implementations, useful when embedding a manager in different containers. [TransactionLog](https://github.com/apache/geronimo-txmanager/blob/trunk/geronimo-transaction/src/main/java/org/apache/geronimo/transaction/manager/TransactionLog.java).

### 5. [tiian/lixa](https://github.com/tiian/lixa)

**Language/role:** C core with C++, Java, and C transaction interfaces; XA/TX manager with a separate state server.

LIXA deliberately separates transaction management from a full transaction-processing monitor. Study how many application containers can share a transaction environment through a client/server state service.

- **C1:** The recovery protocol validates message steps, locates recovery records, transfers processing to the owning server thread when necessary, and compares the recovering client's configuration digest with the recorded configuration. Resource and branch state are explicitly reconstructed. [Server recovery implementation](https://github.com/tiian/lixa/blob/master/src/server/server_recovery.c).
- **C2:** Standard XA/TX boundaries and the XTA interfaces allow transaction participation from different application containers and language bindings; the application does not have to adopt a complete middleware server to obtain coordination. The repository's architecture description explains this distinction.

The repository was not archived when checked; its API-reported last push was April 2025. That observation is not used as evidence of either abandonment or C4.

### 6. [endurox-dev/endurox](https://github.com/endurox-dev/endurox)

**Language/role:** Primarily C; Enduro/X distributed transaction-processing middleware. Relevant subsystem: `tmsrv`, its XA state driver, and associated transaction tests.

Study a transaction manager integrated with a multiprocess XATMI service environment, where participants, service calls, and recovery have to agree on branch outcomes.

- **C1:** The state driver aggregates resource votes and maps XA return codes into subsequent transaction stages. It distinguishes retries from preparation outcomes and explicitly votes toward abort when a resource-state log write fails during preparation. [XA state driver](https://github.com/endurox-dev/endurox/blob/master/tmsrv/statedrv.c).
- **C2:** XATMI service APIs and XA resource integration support many service/resource combinations. Transaction coordination is a named subsystem within the larger middleware, making its boundary with application execution inspectable.

**Further entry point:** [Transaction-manager source tree](https://github.com/endurox-dev/endurox/tree/master/tmsrv). The broader repository also contains dedicated XA and transaction-server test suites; the selection concerns this subsystem, not every platform feature.

### 7. [casualcore/casual](https://github.com/casualcore/casual)

**Language/role:** C++; XATMI application middleware with a distributed transaction manager. Relevant subsystem: `middleware/transaction`.

Study the same manager acting as a coordinator for local resources and as a participant under an upstream manager.

- **C1:** Successful prepare handling records the transaction before sending the dependent prepared response upstream. Read-only participants are removed from further coordination, and distinct transaction stages govern subsequent handling.
- **C3:** The implementation batches persistence-dependent replies, flushes the log before releasing those replies, and uses a one-resource one-phase optimization. These mechanisms make the durability/latency tradeoff concrete. Both criteria are visible in [manager message handling](https://github.com/casualcore/casual/blob/feature/1.9/main/middleware/transaction/source/manager/handle.cpp).
- **C2:** Global and branch transaction identities, resource proxies, and a separately implemented persistence layer support coordination across application services. The [SQLite-backed transaction log](https://github.com/casualcore/casual/blob/feature/1.9/main/middleware/transaction/source/manager/log.cpp) shows the persistence boundary.

The inspected default branch was `feature/1.9/main`; its name should not be mistaken for a stable release designation.

## Multi-protocol and TCC service coordinators

### 8. [apache/incubator-seata](https://github.com/apache/incubator-seata)

**Language/role:** Java; Seata transaction coordinator with AT, TCC, Saga, and XA integrations. This was the canonical repository returned by GitHub, including when opening `apache/seata`.

Study the separation between the transaction coordinator, transaction manager, and resource managers, especially AT mode's interaction between local commits and a global decision.

- **C1:** AT writes business changes and undo data in one local transaction, requires a global write lock before that local commit, and validates after-images before undo. Its documented default global read isolation is not equivalent to serializable isolation. [AT protocol and isolation](https://seata.apache.org/docs/dev/mode/at-mode/).
- **C2:** The coordinator tracks global/branch sessions while protocol-specific resource managers implement different participation mechanisms.
- **C3:** AT's second-phase commit can clean undo records asynchronously; coordinator code separately schedules commit retries and asynchronous completion. [DefaultCoordinator](https://github.com/apache/incubator-seata/blob/2.x/server/src/main/java/org/apache/seata/server/coordinator/DefaultCoordinator.java).

### 9. [dtm-labs/dtm](https://github.com/dtm-labs/dtm)

**Language/role:** Go; service coordinator supporting Saga, TCC, XA, workflow, and transactional-message patterns, with multiple language clients.

Study how participant-side idempotency barriers complement server-side orchestration. Retrying a branch safely is a different problem from deciding which branch to execute next.

- **C1:** `BranchBarrier.Call` inserts origin/current operation markers in the same local SQL transaction as business work. Its affected-row checks handle repeated requests, empty compensation, and late requests after cancellation. [Branch barrier](https://github.com/dtm-labs/dtm/blob/main/client/dtmcli/barrier.go).
- **C2:** Shared branch identities and barriers apply across TCC, Saga, and workflow operations, while the server provides separate processors for transaction types.
- **C3:** The Saga processor supports dependency-constrained concurrent forward execution and corresponding compensation ordering, rather than requiring every saga to be a linear chain. [Saga processor](https://github.com/dtm-labs/dtm/blob/main/dtmsvr/trans_type_saga.go).

### 10. [dromara/hmily](https://github.com/dromara/hmily)

**Language/role:** Java; TCC and TAC distributed transaction framework with embedded recovery and RPC integrations.

Study recovery coordination through a shared repository, including how clustered application instances claim participant work.

- **C1:** Recovery skips unfinished `PRE_TRY` participants, acquires a repository participant lock before recovery, chooses confirm/cancel using global or participant state, and moves work beyond its retry limit to a terminal failure status. These are explicit safeguards and limits, not a guarantee that arbitrary business callbacks are correct.
- **C2:** TCC callbacks and TAC undo records share participant/repository infrastructure while retaining different recovery procedures. This makes Hmily useful for comparing business-defined compensation with framework-managed SQL undo. [Recovery scheduler](https://github.com/dromara/hmily/blob/master/hmily-core/src/main/java/org/dromara/hmily/core/schedule/HmilyTransactionSelfRecoveryScheduled.java).

**Maintenance snapshot:** Not archived, but the [GitHub API metadata](https://api.github.com/repos/dromara/hmily) reported the last repository push in July 2024. Treat this as an implementation study, without assuming current framework-version compatibility.

### 11. [liuyangming/ByteTCC](https://github.com/liuyangming/ByteTCC)

**Language/role:** Java; TCC transaction manager with JTA integration and Spring/Dubbo-related adapters.

Study the relationship between a local transactional resource and a compensable distributed transaction, especially when the outcome of the Try phase must be reconstructed after restart.

- **C1:** Startup first recovers underlying transactions and then reconstructs compensable archives, linking corresponding records. Recovery distinguishes an absent XA branch from an unavailable resource or an unknown outcome, instead of collapsing all exceptions into “aborted.”
- **C2:** Archived participant descriptors, remote coordinator abstractions, compensable logs, and bean-factory interfaces separate protocol execution from resource and integration details. The same recovery machinery can reconstruct different participant combinations. [TransactionRecoveryImpl](https://github.com/liuyangming/ByteTCC/blob/master/bytetcc-core/src/main/java/org/bytesoft/bytetcc/TransactionRecoveryImpl.java).

**Maintenance snapshot:** An older implementation: [GitHub metadata](https://api.github.com/repos/liuyangming/ByteTCC) reported the last push in April 2022 and did not mark it archived. No claim of active maintenance is made.

### 12. [changmingxie/tcc-transaction](https://github.com/changmingxie/tcc-transaction)

**Language/role:** Java; annotation/integration-oriented TCC implementation with a transaction repository and recovery components.

Study the ordering between durable transaction-state changes and asynchronous confirm/cancel execution.

- **C1:** The manager persists `CONFIRMING` or `CANCELLING` before dispatching the terminal operation, updates records after failures, and removes records after successful completion. Custom transaction identifiers receive additional creation handling to avoid repeated initialization.
- **C2:** Participant enlistment, a transaction repository, propagated transaction context, and the completion executor are separate responsibilities. This is a useful smaller counterpart to the larger multi-protocol servers.
- **C3:** Persistence is deferred for ordinary transaction creation until participant enlistment, and asynchronous completion uses a bounded executor. The associated recovery dependency is visible rather than hidden. [TransactionManager](https://github.com/changmingxie/tcc-transaction/blob/master-2.x/tcc-transaction-core/src/main/java/org/mengyun/tcctransaction/transaction/TransactionManager.java).

The inspected branch was `master-2.x`; repository metadata showed a January 2025 last push. This entry evaluates transaction structure, not deployment suitability or dependency security.

## Compensating saga coordinators

### 13. [eventuate-tram/eventuate-tram-sagas](https://github.com/eventuate-tram/eventuate-tram-sagas)

**Language/role:** Java; durable, message-driven saga orchestration for microservices, with Spring, Micronaut, and Quarkus integration paths described by the project.

Study a saga represented as persistent application state plus commands and replies. Forward and compensating steps are coordinated through participant messages rather than holding distributed database locks.

- **C1:** The manager saves the saga instance, correlates replies by saga identity/type, advances the state definition, tracks locked resources, and sends unlock commands at completion. Correctness crosses the boundary between persisted saga state and message processing.
- **C2:** `Saga`, `SagaDefinition`, the instance repository, lock manager, and command producer are separate abstractions; the definition DSL supports reusable orchestration over different business participants. [SagaManagerImpl](https://github.com/eventuate-tram/eventuate-tram-sagas/blob/master/eventuate-tram-sagas-orchestration/src/main/java/io/eventuate/tram/sagas/orchestration/SagaManagerImpl.java).

The framework builds on Eventuate Tram's database/message publication infrastructure. Its guarantees should be assessed together with that infrastructure and the application's compensating operations.

### 14. [apache/servicecomb-pack](https://github.com/apache/servicecomb-pack)

**Language/role:** Java; Alpha coordinator and Omega service agents implementing Saga and TCC. **Historical, archived project:** GitHub records archival on 2024-10-13, and the README explicitly says the project lacks maintainers.

Study event-based coordination in which service agents report transaction execution while a separate coordinator diagnoses failure and invokes recovery.

- **C1:** The design covers start/end/abort event relationships, periodic detection of timed-out work, and forward versus compensating recovery. It describes acceptance tests that simulate execution errors and timeouts and compare the resulting coordinator events.
- **C2:** Agent interception, transaction context, callbacks, transport contracts, event storage, and scanning are separate modules. Saga and TCC use this shared infrastructure with different protocol semantics.

**Entry point:** [Pack design](https://github.com/apache/servicecomb-pack/blob/master/docs/design.md). This remains a substantive architectural study; the archive and maintainer notice make it inappropriate to describe as a currently supported solution.

### 15. [oxidecomputer/steno](https://github.com/oxidecomputer/steno)

**Language/role:** Rust; embedded Saga Execution Coordinator for graphs of asynchronous actions and undo actions.

Study the boundary between graph execution, a durable saga log, and application-supplied persistence. The README retains explicit prototype-quality and failover caveats, so this entry does not assume turnkey highly available execution.

- **C1:** Recovery depends on durably recording saga creation and node events; cached completion state is an optimization because the log contains the authoritative history. The provided in-memory store explicitly cannot recover after a process crash. [SecStore contract](https://github.com/oxidecomputer/steno/blob/main/src/store.rs).
- **C2:** Action registration, DAG construction, serialized action data, and a storage trait separate business tasks from execution and persistence.
- **C4:** The dated 2022–2024 release history documents idempotency fault-injection support and a breaking change that reports undo failures instead of panicking. It also explains why failed compensation can require application-specific intervention. [Changelog](https://github.com/oxidecomputer/steno/blob/main/CHANGELOG.adoc).

## Storage and actor-state transaction coordination

### 16. [apache/phoenix-omid](https://github.com/apache/phoenix-omid)

**Language/role:** Java; Omid transaction management over HBase, centered on a Transactional Status Oracle. **Official Apache GitHub mirror**, now under the Phoenix repository name.

Study centralized conflict validation with distributed data storage and a separately persisted commit table.

- **C1:** The architecture explains monotonic timestamp allocation across crashes, conflict-map eviction coupled to a low watermark, and persistence of commit status before acknowledging success. Advancing the watermark is necessary to avoid missing conflicts whose map entries were evicted.
- **C3:** A bounded, hashed conflict map, timestamp-range reservation, and shadow cells reduce memory or lookup/persistence costs. The documentation candidly identifies false-abort tradeoffs in hashed conflict detection.
- **C2:** Transaction demarcation, transactional table operations, timestamp allocation, and commit-table storage are separately described components. [Omid architecture and component description](https://omid.apache.org/omid-components.html).

**Additional entry point:** [TSO server implementation](https://github.com/apache/phoenix-omid/tree/master/tso-server). The architectural documentation is older and describes HA as work in progress; it is used for protocol concepts, not as evidence of the current HA feature set.

### 17. [apache/phoenix-tephra](https://github.com/apache/phoenix-tephra)

**Language/role:** Java; transaction manager layered over distributed stores, notably HBase. **Official Apache GitHub mirror.** The former incubator URL redirects here; the archived pre-Apache `cdapio/tephra` repository is not counted separately.

Study the distinction between writing data and making a transaction's versions visible to other readers.

- **C1:** Transactions carry read/write pointers and excluded versions. The manager checks conflicts before persistence and again at commit because another transaction may have committed between those steps. The commit path coordinates changes to in-progress/committing state with transaction-log access. [TransactionManager](https://github.com/apache/phoenix-tephra/blob/master/tephra-core/src/main/java/org/apache/tephra/TransactionManager.java).
- **C2:** `TransactionAware` defines dataset participation through start/update, change-set extraction, persistence, rollback, and post-commit callbacks. Its documented sequence distinguishes data durability from transaction visibility, allowing different datasets to participate under one manager. [TransactionAware](https://github.com/apache/phoenix-tephra/blob/master/tephra-api/src/main/java/org/apache/tephra/TransactionAware.java).

The official mirror was not archived when checked. Older incubator wording and release documents should not be read as a statement about present release cadence.

### 18. [scalar-labs/scalardb](https://github.com/scalar-labs/scalardb)

**Language/role:** Java; database-independent transaction layer. Relevant subsystem: Consensus Commit and the two-phase coordinator/participant interfaces; the monorepo is counted once.

Study coordination over storage with conditional writes, including lazy repair by subsequent transactions and explicit treatment of unknown commit outcomes.

- **C1:** The protocol description states invariants relating coordinator and resource states and supplies TLA+ models. The implementation leaves records prepared when writing the coordinator's committed state has an unknown outcome; it does not guess whether to commit or undo them. [Protocol and model overview](https://github.com/scalar-labs/scalardb/blob/master/tla%2B/consensus-commit/README.md).
- **C2:** The coordinator drives participant join, prepare, validation, commit, and rollback through interfaces, and keys write sets by stable participant identity. It enlists each participant identity idempotently. [ConsensusCommitCoordinator](https://github.com/scalar-labs/scalardb/blob/master/core/src/main/java/com/scalar/db/transaction/consensuscommit/ConsensusCommitCoordinator.java).

The inspected coordinator explicitly rejects group-commit configuration that it does not yet support. The presence of related group-commit classes elsewhere should not be generalized to this implementation.

### 19. [dotnet/orleans](https://github.com/dotnet/orleans)

**Language/role:** C#; distributed virtual-actor framework. Relevant subsystem: `Orleans.Transactions`, not the entire framework. Coordination is decentralized: a manager is selected from the transaction's participants rather than provided by a single central server.

Study how transaction decisions interact with actor activation, participant queues, and storage recovery.

- **C1:** Participant queues retain unresolved versions and locks; a response timeout does not establish abort because the manager may already have persisted commit. Durable records support replay of pending confirmations and recovery across activation/process restart.
- **C2:** Transaction agents, managers, participant queues, and transactional storage have distinct responsibilities, providing reusable coordination across multiple grains and supported storage providers.
- **C3:** Read-only transactions use a direct participant path, write transactions use one-way preparation notifications, and overload detection bounds admitted work. These optimizations are explained alongside the durability costs. [Transaction implementation](https://dotnet.github.io/orleans/docs/implementation/transactions/).

Atomicity covers registered transactional resources; arbitrary external side effects require separate coordination or compensation. This boundary is explicit in the implementation documentation.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, including: general distributed transaction coordinators with Saga/TCC/XA; Java JTA managers and recovery; C/C++ XA/XATMI middleware; Chinese-community TCC implementations; durable Rust saga execution; message-driven Saga/Alpha–Omega coordination; HBase transaction oracles and conflict detection; heterogeneous-database transactions; and .NET actor transaction protocols. Follow-up searches tested alternatives such as TX-LCN and EasyTransaction and clarified repository transfers. Later queries mostly repeated these families, surfaced wrappers/examples, or broadened into general workflow engines and databases; that was the practical diminishing-return point.

Every retained repository had its canonical GitHub page or API metadata inspected, plus an additional substantive implementation or architecture source read. Source paths were checked through repository trees and/or successful file retrieval. The report follows redirects for Bitronix, Seata, Omid, and Tephra, identifies official mirrors, and counts monorepos once. No candidate code was executed, dependencies installed, or repositories cloned.

Selection favors actual coordination logic over client SDKs, Spring integration wrappers, demonstrations, specification-only projects, and generic outbox relays. General-purpose workflow products were not included merely because users can implement compensation in them. Full distributed databases were also excluded unless the selected project exposes a distinct reusable coordination layer; Orleans is retained specifically for its independently inspectable transaction subsystem. Proprietary coordinators such as MSDTC and commercial-only transaction-manager components do not meet the substantive GitHub-source requirement.

The ecosystem is Java-heavy; language diversity was obtained through substantive C, C++, Go, Rust, and C# implementations rather than thin bindings. Maintenance observations are deliberately limited: archived status, project notices, and repository activity snapshots do not establish correctness or support commitments. Some documentation is older than its source tree, especially Omid's architecture pages and Steno's README caveats. Those discrepancies are noted rather than silently interpreted as evidence of current capabilities. GitHub's unauthenticated API rate limit interrupted one additional metadata lookup; Omid's identity and source-tree entry point were verified through its GitHub pages instead.

The C1–C4 assignments and suggested study value are grounded engineering judgments from the cited material. They are not formal verification of the implementation, benchmark results, or an exhaustive security/maintenance audit.
