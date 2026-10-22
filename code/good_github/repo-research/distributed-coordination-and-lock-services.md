# Distributed coordination and lock services

Research date: **2026-10-09**.

This selection covers coordination servers, distributed lock managers, leader-election and membership frameworks, and substantive libraries that implement leases or locking over an external service. It includes 24 repositories across Go, Java, C++, C, Python, Erlang, C#, Rust, PHP, and TypeScript. For large repositories, only the named coordination subsystem is in scope. Historical implementations and research prototypes are included for their engineering lessons and explicitly identified.

The criteria are judgments about study value, grounded in the linked primary material:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial conditions, or failure semantics.
- **C2 — Abstraction:** substantial reusable mechanisms supporting different applications.
- **C3 — Performance:** concrete resource or latency constraints addressed through understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility, testing, or complexity management.

A criterion is not a certification of correctness. In particular, expiration does not stop a paused process from resuming protected work. Some systems expose fencing tokens; applications must arrange for the protected resource to reject stale tokens. Backend selection and failure assumptions remain part of the design, as the [Hazelcast fencing explanation](https://docs.hazelcast.com/hazelcast/5.5/data-structures/fencedlock) and [Redis locking specification](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/) illustrate.

## Coordination servers and replicated primitives

### 1. [etcd-io/etcd](https://github.com/etcd-io/etcd)

**Go — replicated coordination store and client-side concurrency primitives.** Study how a transactional, revisioned keyspace becomes a session-bound mutex, and how externally observed histories test the resulting service.

- **C1:** The mutex attaches a contender key to a session lease, orders ownership by creation revision, waits for earlier contenders to disappear, and checks that its own key survived before returning ownership. Cancellation also requires cleanup. The [mutex implementation](https://github.com/etcd-io/etcd/blob/main/client/v3/concurrency/mutex.go) makes these races concrete.
- **C2:** Transactions, leases, revisions, and watches form reusable coordination building blocks. Their contracts differ: default KV operations provide strong consistency, while watches are ordered and resumable within retained history but are not themselves linearizable. See the [API guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/).
- **C4:** The [robustness testing guide](https://github.com/etcd-io/etcd/blob/main/tests/robustness/README.md) documents fault injection, model-based history checking, and a multi-year record of reproduced bugs, including work to preserve reproductions as the framework evolves.

**Entry points:** the mutex implementation and robustness testing guide above.

### 2. [apache/zookeeper](https://github.com/apache/zookeeper)

**Java — hierarchical coordination service; official Apache GitHub mirror.** The project's [version-control page](https://zookeeper.apache.org/version-control/) identifies the mirror. A foundational study in separating a small server API from sophisticated client recipes.

- **C1:** The [internals documentation](https://zookeeper.apache.org/doc/current/zookeeperInternals.html) explains atomic broadcast, leader activation, quorum intersection, and recovery ordering. The [recipes](https://zookeeper.apache.org/doc/current/recipes.html) expose an equally important client failure: a successful sequential-node creation can lose its response, requiring recovery of the already-created node rather than blind creation of another contender.
- **C2:** Ephemeral and sequential znodes, conditional updates, and watches support locks, barriers, membership, and election without separate server implementations for every recipe.
- **C3:** The lock recipe watches the immediately preceding contender instead of making every waiter watch the owner. This limits the wake-up herd when ownership advances; the recipes also explain why polling should be avoided.

**Entry points:** the internals and recipes documents. Distinguish write ordering from the semantics of ordinary local reads when studying the service.

### 3. [hashicorp/consul](https://github.com/hashicorp/consul)

**Go — service coordination through sessions and KV acquisition.** Focus on the session/lock subsystem rather than the whole networking product.

- **C1:** [Session internals](https://developer.hashicorp.com/consul/docs/automate/session) explicitly connect lock validity to health checks, TTL renewal, and invalidation. Failure detectors can produce false positives; lock delay reduces some consequences but is not a complete safety mechanism. A TTL is a lower bound on invalidation time, not a precise release deadline.
- **C2:** The same session abstraction connects node health, ownership of KV entries, and release-versus-delete behavior. KV acquisition associates a session with the key and advances a lock index, allowing applications to build elections and ownership protocols on a common mechanism.

**Entry point:** the session internals document, especially invalidation and KV integration. This is particularly useful for studying the boundary between a membership service's suspicion of failure and an application's authority to act.

### 4. [ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse)

**C++ — ClickHouse Keeper subsystem within the ClickHouse monorepo.** Counted once, specifically for its ZooKeeper-compatible coordination server, not for analytical query execution.

- **C1:** [Keeper's design and deployment guide](https://clickhouse.com/docs/guides/oss/deployment-and-scaling/keeper) distinguishes protocol compatibility from internal compatibility. Keeper uses Raft through NuRaft; its snapshots, logs, and interserver protocol differ from ZooKeeper's, so a mixed ensemble is not supported. Default reads and writes also have different consistency properties, with an option for linearizable reads.
- **C2:** The ZooKeeper-facing interface lets existing clients use a separate implementation of the coordination service. Keeper can run independently or embedded in ClickHouse and supports coordination for replication and distributed DDL.

**Entry point:** the Keeper guide, including consistency, configuration, and migration sections. Its strongest study value is the engineering of a replacement coordination service under an established client protocol, rather than a claim of identical internals or universal drop-in compatibility.

### 5. [hazelcast/hazelcast](https://github.com/hazelcast/hazelcast)

**Java — CP subsystem, especially `FencedLock`, within the Hazelcast monorepo.** Study how familiar Java locking operations acquire a distributed failure contract.

- **C1:** The [FencedLock implementation contract](https://github.com/hazelcast/hazelcast/blob/master/hazelcast/src/main/java/com/hazelcast/cp/lock/FencedLock.java) addresses retried operations, reentrancy, and ownership loss after session expiration. Internal retry deduplication is distinct from whether application work still has permission to proceed.
- **C2:** The API adapts `java.util.concurrent.locks.Lock` while adding monotonically increasing fencing tokens. The [guide](https://docs.hazelcast.com/hazelcast/5.5/data-structures/fencedlock) explains how an external service can use those tokens to reject a previously paused owner.

**Entry points:** the interface's detailed Javadoc and the FencedLock guide. The guide explicitly conditions strong guarantees on CP configuration; its default unsafe mode must not be confused with CP operation. Fencing also requires cooperation from the protected resource, and the lock does not promise fairness.

### 6. [atomix/atomix](https://github.com/atomix/atomix)

**Go — Kubernetes-oriented distributed primitives runtime.** This entry covers the Go repository, not the separate archived Java implementation. Its repository metadata showed a latest push in June 2024 when checked; no current-maintenance claim is made. [Repository metadata](https://api.github.com/repos/atomix/atomix).

- **C1:** The [replicated lock state machine](https://github.com/atomix/atomix/blob/master/protocols/rsm/pkg/statemachine/lock/v1/statemachine.go) persists ownership and queued proposals in versioned snapshots. Recovery rebuilds session/proposal watches, while closure, cancellation, and timeouts must remove or advance contenders consistently.
- **C2:** The repository separates a polyglot runtime and primitive APIs from storage drivers and replication protocols. The lock is registered through typed primitive machinery, codecs, and state-machine context rather than implemented as an isolated endpoint.

**Entry point:** the lock state machine, followed through its snapshot/recovery and session-watch paths. This is useful for engineers designing reusable replicated objects whose pending operations must remain meaningful after restoring state.

### 7. [ha/doozerd](https://github.com/ha/doozerd)

**Go — historical Paxos-based coordination daemon.** Retained as a compact design study. The repository is not GitHub-archived, but its recorded latest push is March 2016. The README describes in-memory storage and external backup, so durability should not be assumed from replication alone. [Repository metadata](https://api.github.com/repos/ha/doozerd).

- **C1:** The [Paxos acceptor](https://github.com/ha/doozerd/blob/master/consensus/acceptor.go) exposes promise rounds, previously accepted values, and checks on nominations directly. At the client boundary, revision mismatch and history-retention errors are explicit parts of the protocol.
- **C2:** The [wire protocol](https://github.com/ha/doozerd/blob/master/doc/proto.md) provides revisioned file operations and waits over path patterns, suitable for configuration, naming, and ownership protocols. Tagged requests allow multiple operations to be outstanding on one connection.

**Entry points:** the acceptor and wire protocol. The appeal is the short path from consensus state to observable API behavior; this is a historical implementation, not a recommendation for a newly maintained deployment.

### 8. [spcl/faaskeeper](https://github.com/spcl/faaskeeper)

**Python — research prototype of serverless coordination using functions, storage, and queues.** The associated work was published at HPDC 2024. It offers a substantially different architecture from continuously running consensus servers.

- **C1:** The [authors' paper](https://arxiv.org/html/2203.14859v3) explains conditional commits under expiring locks, recovery when queue publication and storage commit cannot be atomic, and epoch counters that keep reads from overtaking watch notifications.
- **C3:** The design separates control state from user data, serves reads directly from storage, and batches queued function invocations. These choices address invocation overhead, storage costs, and ordering constraints together, with concrete evaluation rather than a generic scalability claim.

**Entry points:** the paper's design/implementation sections and the [AWS watch function](https://github.com/spcl/faaskeeper/blob/master/functions/aws/watch.py). **Limitation:** the inspected watch code implements only a subset of event paths and raises unimplemented-operation errors for others. Treat this repository as a research artifact; the paper's design claims are not evidence that every checked-in integration path is complete.

### 9. [rabbitmq/portunus](https://github.com/rabbitmq/portunus)

**Erlang, with Quint specifications — replicated leases, locks, and process coordination on Ra.** A young project: repository metadata records creation in July 2026, and the inspected README describes no Hex release yet. [Repository metadata](https://api.github.com/repos/rabbitmq/portunus).

- **C1:** The [Quint state-machine model](https://github.com/rabbitmq/portunus/blob/main/quint/portunus_machine.qnt) states mutual exclusion, increasing fencing tokens, stale-release behavior, and priority/FIFO succession. Batch expiry has a particularly instructive invariant: revoking multiple leases must not promote another revoked contender or mint duplicate tokens within the command.
- **C2:** Sessions and leases can own multiple keys; lock succession, handover, and coordination helpers build on the replicated state rather than on unrelated lock records. This makes the repository relevant to application supervision and service ownership as well as mutexes.

**Entry point:** the Quint model and its commentary on bounded checks and implementation property tests. Those are evidence of deliberate verification work, not a proof of all deployed behavior. Its short history does not qualify it for C4.

## Cluster locking and coordination frameworks

### 10. [torvalds/linux](https://github.com/torvalds/linux)

**C — `fs/dlm` distributed lock manager in the official Linux GitHub source mirror.** Only the cluster DLM is in scope; ordinary kernel mutexes and unrelated filesystems are not counted separately.

- **C1:** The [lock engine](https://github.com/torvalds/linux/blob/master/fs/dlm/lock.c) includes compatibility and conversion matrices, granted/converting/waiting queues, lock-value-block transfer, and synchronization with lockspace recovery. Converting an existing lock is a distinct correctness problem from acquiring a new one.
- **C2:** The [public DLM API](https://github.com/torvalds/linux/blob/master/include/linux/dlm.h) exposes named resources within lockspaces, multiple lock modes, asynchronous completion and blocking callbacks, and recovery notifications. A successful submission is not necessarily a granted lock.
- **C3:** The implementation documents successive stages for validation, resource lookup, local-versus-remote routing, and actual queue/grant processing. The API also exposes callback execution choices that avoid a workqueue context switch where callers can accept the restrictions.

**Entry points:** `fs/dlm/lock.c` and `include/linux/dlm.h`.

### 11. [apache/curator](https://github.com/apache/curator)

**Java — ZooKeeper client framework and coordination recipes; official Apache GitHub source.** Study how reusable recipes centralize the error-handling obligations that otherwise spread through application code.

- **C1:** The [error-handling guide](https://curator.apache.org/docs/errors/) distinguishes suspension from definite session loss and explains conservative cleanup policy. It also records a change in the meaning of `LOST` before version 3.0, illustrating why connection-state semantics are part of an API contract.
- **C2:** The [shared reentrant lock recipe](https://curator.apache.org/docs/recipes-shared-reentrant-lock/) supplies timed acquisition, balanced reentrant ownership, cooperative revocation, and connection-state guidance on a common client framework. The surrounding recipe family applies the same infrastructure to other coordination patterns.

**Entry points:** the errors guide and reentrant-lock recipe. Particularly useful questions are when protected work must stop, how a recipe reacts to a suspended connection, and which cleanup operations remain safe after the session is lost.

### 12. [python-zk/kazoo](https://github.com/python-zk/kazoo)

**Python — ZooKeeper client and coordination recipes.** A readable implementation of the subtle bookkeeping behind high-level lock APIs.

- **C1:** The [lock recipe source](https://kazoo.readthedocs.io/en/latest/_modules/kazoo/recipe/lock.html) uses a unique contender prefix to recover an ambiguous successful create. Session listeners, cancellation, predecessor disappearance, and cleanup interact in the acquisition loop; merely sorting sequential nodes is insufficient.
- **C2:** Exclusive locks, reader/writer locks, and semaphores share client and recipe machinery while adapting contender filtering and capacity rules. These are reusable coordination mechanisms rather than a single application-specific lock.
- **C3:** Predecessor watches limit mutex wake-ups. The semaphore implementation separately explains how restricting which contender watches the shared child set avoids a herd of watchers.

**Entry point:** the rendered source for `kazoo.recipe.lock`, which includes implementation rather than only API signatures. Compare the mutex and semaphore paths to see why different admission rules require different observation strategies.

### 13. [apache/helix](https://github.com/apache/helix)

**Java — cluster coordination framework; official Apache GitHub mirror.** Includes both broad resource-state coordination and the `helix-lock` subsystem.

- **C1:** The [architecture](https://helix.apache.org/Architecture.html) separates ideal, current, and externally visible state. Controllers issue transitions subject to replica-state constraints and dependencies, while participants execute them. This exposes safety questions that remain after leader election itself is solved.
- **C2:** Resources, partitions, participants, spectators, and pluggable state machines form a reusable vocabulary for coordinating different kinds of distributed services.
- **C3:** Independent transitions can proceed concurrently while dependent ones wait, making transition planning part of the performance architecture rather than blindly serializing all changes.

**Entry points:** the architecture document and [ZooKeeper nonblocking lock implementation](https://github.com/apache/helix/blob/master/helix-lock/src/main/java/org/apache/helix/lock/helix/ZKDistributedNonblockingLock.java). The latter deliberately uses persistent znodes and implements leases, priority, and cleanup/preemption policy; it should not be mistaken for the standard ephemeral-sequential mutex recipe.

### 14. [openstack/tooz](https://github.com/openstack/tooz)

**Python — coordination abstraction across backends; official GitHub mirror of OpenStack's OpenDev project.** Useful precisely because it makes the limits of interchangeable backends visible.

- **C1:** The [driver documentation](https://docs.openstack.org/tooz/latest/user/drivers.html) describes materially different failure semantics: session-based ownership, expiring Redis locks, connection-bound database locks, and weaker backends with problematic release races. Applications cannot infer identical guarantees from an identical method name.
- **C2:** The [coordination layer](https://github.com/openstack/tooz/blob/master/tooz/coordination.py) defines group membership events, leader-election events, a heartbeat lifecycle, and explicit driver characteristics such as host distribution and timeout dependence. This supports a reusable coordination API while retaining information about backend capabilities.

**Entry points:** the driver guide and `tooz/coordination.py`. Study the division between the generic lifecycle and driver-specific behavior; selecting a backend is part of selecting the algorithm, not just choosing a connection URL.

### 15. [kubernetes/client-go](https://github.com/kubernetes/client-go)

**Go — reusable leader-election subsystem in Kubernetes' official staged publishing mirror.** This entry concerns the hand-written `tools/leaderelection` code, not the generated API clients. The README explains that development originates in the Kubernetes staging tree.

- **C1:** The [leader-election source](https://github.com/kubernetes/client-go/blob/master/tools/leaderelection/leaderelection.go) explicitly does not guarantee fencing. It explains clock-skew-rate assumptions, validates lease/renewal/retry relationships, and warns that releasing on cancellation before protected work stops can permit concurrent actors.
- **C2:** Resource-lock interfaces, lifecycle callbacks, configurable timing, and health reporting separate application work from election mechanics. This is reusable for controllers and other processes that must select an active participant.

**Entry point:** the package comment, configuration validation, and lifecycle in `leaderelection.go`. It is an especially valuable counterexample to treating an election winner as automatically having exclusive, externally enforceable authority.

### 16. [uwiger/locks](https://github.com/uwiger/locks)

**Erlang — hierarchical distributed locking with deadlock detection.** Offers an architecture quite different from independent expiring keys in a remote store.

- **C1:** The repository's algorithm description covers distributed wait-for information, deadlock resolution by surrender, versioned updates, and acknowledgments needed to avoid acting on stale lock information. It distinguishes the earlier verified algorithm from this implementation's extensions; the entire current system should not be called formally verified.
- **C2:** The [API documentation](https://github.com/uwiger/locks/blob/master/doc/locks.md) exposes transaction agents, hierarchical resource identifiers, read/write modes, and acquisition across all, any, or a majority of specified nodes. Applications can choose whether to abort on deadlock or tolerate surrender and retry.

**Entry points:** the repository README's algorithm discussion and `doc/locks.md`. Study how hierarchical intent, multi-node acquisition, and transaction-wide ownership expand the state space beyond a flat named mutex, especially when nodes disappear or become available again.

## Database and cloud-backed lock libraries

### 17. [madelson/DistributedLock](https://github.com/madelson/DistributedLock)

**C# — common distributed synchronization APIs across databases and services.** Includes mutexes, reader/writer locks, and semaphores with synchronous and asynchronous use; backend support differs by primitive.

- **C1:** The [PostgreSQL provider guide](https://github.com/madelson/DistributedLock/blob/master/docs/DistributedLock.Postgres.md) distinguishes connection-scoped and transaction-scoped ownership. Disposing a transaction-scoped handle does not end the transaction's lock lifetime, and externally supplied connections impose concurrency constraints.
- **C2:** Shared handle/provider abstractions let applications use several storage mechanisms without reimplementing acquisition and disposal conventions. Provider documentation keeps backend-specific key namespaces and lifetimes visible rather than claiming identical behavior.
- **C3:** The PostgreSQL provider can multiplex multiple locks over connections to reduce connection consumption. Its documentation explains the incompatibility of that optimization with transaction-scoped locking and the role of keepalive behavior.

**Entry point:** `docs/DistributedLock.Postgres.md`, then the repository's API/provider overview. A strong study in retaining a convenient common API without erasing the underlying database's ownership model.

### 18. [awslabs/amazon-dynamodb-lock-client](https://github.com/awslabs/amazon-dynamodb-lock-client)

**Java — distributed leases over DynamoDB conditional operations.** The repository describes community support; inclusion is based on the protocol and implementation, not an assumption of a managed AWS service or support commitment.

- **C1:** The [AWS protocol walkthrough](https://aws.amazon.com/blogs/database/building-distributed-locks-with-the-dynamodb-lock-client/) explains conditional acquisition, heartbeats with changing record-version numbers, and contenders observing whether a version remains unchanged across a lease interval. This avoids relying on synchronized absolute client clocks for that expiration decision.
- **C2:** Named lock records and configurable leases support both coarse and fine resource locking and leader-election applications. Applications reuse the same heartbeat and conditional-update machinery rather than inventing a table protocol for each resource.

**Entry point:** the official walkthrough's acquisition, renewal, and failure sequence, followed by the repository API examples. The random record-version number is an ownership/version check; it should not be described as a monotonically increasing fencing token for arbitrary external resources.

### 19. [alexheretic/dynamodb-lease](https://github.com/alexheretic/dynamodb-lease)

**Rust — asynchronous DynamoDB leases with automatic renewal and release.** This is the current repository to which the former `TrueLayer/dynamodb-lease` project points; the old location is not counted separately.

- **C1:** The [design document](https://github.com/alexheretic/dynamodb-lease/blob/main/DESIGN.md) describes version-conditional renewal and deletion so a stale holder cannot refresh or remove a successor's lease. Acquisition uses expiry timestamps, so clock skew matters; the document also explains the limits of health information after storage access fails.
- **C2:** A lease object packages acquisition, Tokio background renewal, health inspection, and release initiated on drop. The abstraction is reusable across application-defined resource names and makes Rust lifetime management meet an asynchronous remote protocol.

**Entry point:** `DESIGN.md`, then the README's acquisition and health examples. This implementation is a useful comparison with the Java DynamoDB client because their clock assumptions and client-lifecycle mechanisms differ. Automatic renewal is best effort and does not make stale application work harmless.

### 20. [lukas-krecan/ShedLock](https://github.com/lukas-krecan/ShedLock)

**Java — distributed exclusion for scheduled-task execution.** Its scope is preventing overlapping execution; it is not itself a distributed scheduler, and competing executions are generally skipped.

- **C1:** The [task executor](https://github.com/lukas-krecan/ShedLock/blob/master/shedlock-core/src/main/java/net/javacrumbs/shedlock/core/DefaultLockingTaskExecutor.java) separates successful acquisition from skipped execution and guarantees cleanup around task exceptions. The README explains that exceeding `lockAtMostFor` can allow overlap and that database-time options address application-clock skew for supported SQL providers.
- **C2:** Core task execution, lock-provider interfaces, and framework integrations are separate layers. Many storage providers can therefore support the same scheduling integration while retaining provider-specific transaction behavior.
- **C4:** The [release history](https://github.com/lukas-krecan/ShedLock/blob/master/RELEASES.md) documents development across years, including 2024–2026 provider fixes, transaction changes, and explicitly recorded breaking API changes. It provides concrete evidence of compatibility and backend-complexity management.

**Entry points:** the task executor and release history. Read lease-duration and transaction caveats before interpreting the high-level scheduling annotations.

### 21. [symfony/lock](https://github.com/symfony/lock)

**PHP — Symfony Lock component; official component split from the main Symfony repository.** Its README directs issues and pull requests to `symfony/symfony`; the component is counted once here.

- **C1:** The [combined-store implementation](https://github.com/symfony/lock/blob/8.2/Store/CombinedStore.php) tracks successes and failures, checks expiration, stops when its strategy cannot succeed, and cleans up partial acquisition on failure. Combining stores creates a protocol, not merely an array of independent writes.
- **C2:** The [component guide](https://symfony.com/doc/current/components/lock.html) explains store capabilities, blocking versus expiring behavior, shared locks, refresh, and combined-store strategies. Redis, PostgreSQL, and ZooKeeper providers expose different lifetimes, while local stores do not become multi-host locks merely by sharing the API.

**Entry points:** `Store/CombinedStore.php` and the component guide. Particularly useful for studying capability-based interfaces and failure cleanup. A majority strategy is not, by itself, evidence of safety under every timing, persistence, or partition scenario.

## Redis-based synchronization implementations

The following repositories are retained for distinct architectural lessons. They are not interchangeable guarantees of exclusive access. The [Redis specification](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/) discusses bounded validity, elapsed acquisition time, drift, restart behavior, and the need for fencing; it also warns that wall-clock changes can affect expiration. Random ownership values used for compare-and-delete are not equivalent to ordered fencing tokens.

### 22. [redisson/redisson](https://github.com/redisson/redisson)

**Java — Redis-backed synchronization and distributed objects.** This entry focuses on locks and synchronizers rather than the entire Redis client.

- **C1:** The [locks and synchronizers documentation](https://github.com/redisson/redisson/blob/master/docs/data-and-services/locks-and-synchronizers.md) describes thread ownership, watchdog renewal, explicit lease expiration, and the need to retain the correct thread identifier across asynchronous operations. Its fenced-lock API adds a token that an external resource must validate.
- **C2:** Reentrant, fair, reader/writer, and fenced locking coexist with semaphore-style primitives and synchronous, asynchronous, and reactive APIs. Shared Redis infrastructure supports a substantial family of coordination use cases.
- **C3:** The documentation explains the different operating costs of publication/subscription wake-ups and spin-lock backoff under high lock churn. This connects notification strategy and subscription pressure to concrete implementation choices.

**Entry point:** the locks/synchronizers document, especially watchdogs, spin locks, and fenced locks. Keep ordinary lock ownership, replica behavior, and externally enforced fencing separate when evaluating a particular API.

### 23. [mike-marcacci/node-redlock](https://github.com/mike-marcacci/node-redlock)

**TypeScript — Redis quorum leases with scoped execution and extension.** Useful for studying how a distributed protocol is expressed through promises and cancellation signals.

- **C1:** The repository guide documents automatic extension and the abort signal provided when extension fails. Applications must respond to that signal. The [implementation](https://github.com/mike-marcacci/node-redlock/blob/main/src/index.ts) combines validity calculations, retries, partial-acquisition cleanup, and ownership-checked scripts.
- **C2:** Resource arrays and scoped execution package multi-resource acquisition and lease maintenance into a reusable application-facing abstraction.
- **C3:** Per-client attempts run concurrently; the operation can resolve once a quorum outcome is known while statistics await the remaining responses. Script-hash execution falls back when Redis lacks the cached script, reducing repeated script transfer without assuming caches persist.

**Entry points:** `src/index.ts` and the repository's scoped-execution guide. Quorum acquisition does not remove the validity-window and stale-worker limitations described in the Redis specification.

### 24. [go-redsync/redsync](https://github.com/go-redsync/redsync)

**Go — Redis distributed mutexes with pluggable client pools.** A compact implementation suited to tracing the full acquisition/extension path.

- **C1:** The [mutex source](https://github.com/go-redsync/redsync/blob/master/mutex.go) subtracts elapsed acquisition time and a drift allowance from validity, requires quorum, and releases partial results after failed attempts. Extension repeats quorum and validity checks. The deprecated `Valid` method's warning illustrates why probing nodes can itself take long enough to invalidate an answer.
- **C2:** Pool adapters decouple the mutex protocol from particular Go Redis clients; contexts, retries, and extension are exposed through a reusable mutex API.
- **C3:** Operations are dispatched across pools concurrently rather than paying each server's latency serially. The source keeps timeout policy and lease arithmetic visible alongside that concurrency.

**Entry points:** `mutex.go` and the README's adapter examples and algorithm disclaimer. The repository explicitly cautions about the underlying algorithm; inclusion recognizes the implementation's study value, not an unconditional safety endorsement.

## Search coverage and limitations

Discovery used more than six distinct search formulations and several rounds of refinement. The search angles included:

- Replicated coordination stores, ZooKeeper alternatives, Raft-backed lock services, and Paxos coordination daemons.
- ZooKeeper recipes, session-loss handling, hierarchical locks, and distributed deadlock detection.
- Kernel cluster DLMs, lock conversion, callback interfaces, and lockspace recovery.
- Cloud leases, DynamoDB conditional writes, Rust renewal/drop behavior, and serverless ZooKeeper research.
- Redis Redlock implementations, renewal, fencing, partial acquisition, and client-library architectures.
- SQL/advisory-lock libraries, .NET synchronization providers, PHP store composition, and scheduled-task exclusion.
- Kubernetes leader election, OpenStack backend characteristics, cluster state machines, and newer Erlang services.

Canonical GitHub repository pages or API records were opened for every selection. Each was also checked against an additional primary document or source file; a raw copy of the same README was not treated as independent evidence. Sources included actual lock state machines, protocol specifications, callback APIs, formal models, fault-testing documentation, and release history. Later searches increasingly returned overlapping Redlock ports, thin wrappers, examples, and application schedulers rather than distinct coordination architectures.

Generic consensus libraries were excluded unless the selected repository implemented a substantive coordination service or primitive above consensus. General databases, service meshes, orchestration applications, awesome-lists, and tutorials were not included merely because they use locks. Chubby was not included without a qualifying public implementation. Additional Redis ports were deliberately limited; their language alone would not establish a distinct study contribution. Monorepos and official publishing mirrors are counted once, and moved DynamoDB-lease URLs were consolidated.

This is a source-based selection guide, not a benchmark, deployment recommendation, or claim that every component is uniformly exemplary. No candidate code was executed and no fault guarantees were independently reproduced. Linked branch and current-documentation URLs may evolve. Doozer is historical, Atomix's observed activity is dated explicitly, FaaSKeeper has incomplete inspected paths, and Portunus is young; their inclusion does not imply ongoing support or production readiness. C4 is used selectively where multi-year testing or release evidence was actually inspected, rather than inferred from repository age or popularity.
