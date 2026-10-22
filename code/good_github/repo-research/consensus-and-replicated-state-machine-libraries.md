# Consensus and replicated state machine libraries

Research date: **2026-10-09**.

This report selects **26 GitHub repositories** implementing reusable consensus cores, replicated state machine frameworks, or substantial embeddable replication subsystems. It covers crash-fault-tolerant Raft and Paxos, RDMA-oriented replicated objects, and Byzantine consensus. Databases and blockchains that merely consume these libraries are outside the main scope. Research frameworks are included when their protocol implementations and reusable abstractions offer substantial engineering study value; their limitations are identified.

Every repository URL was checked against its GitHub page or GitHub API. Each selection also has an independently inspected implementation file, design document, API guide, or subsystem document beyond the root README. Criteria are evidence-based selection judgments, not certifications of correctness or production suitability. Source links generally follow the inspected default branch and can change after this research date.

## Criteria legend

- **C1 — Difficult correctness:** meaningful invariants, concurrency, adversarial behavior, persistence ordering, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces or frameworks applicable to multiple applications and integration environments.
- **C3 — Performance with structure:** concrete latency, throughput, memory, disk, or network constraints addressed through understandable architectural mechanisms.
- **C4 — Sustained evolution:** dated development history together with compatibility work, testing, or explicit management of implementation complexity. Repository age or a recent push alone does not establish C4.

## Raft cores and integration boundaries

### 1. [etcd-io/raft](https://github.com/etcd-io/raft)

**Go — deterministic Raft protocol core.** An especially useful starting point for understanding how a consensus algorithm can remain separate from networking and storage. The embedding application advances the core with messages and ticks, then handles the resulting entries, state changes, and outbound messages.

- **C1:** The integration contract makes durability ordering explicit: the application must correctly persist entries, hard state, and snapshots and respect the restrictions on sending messages. This makes the distinction between protocol correctness and a correct host integration directly inspectable in the [repository integration guide](https://github.com/etcd-io/raft).
- **C2:** Storage and transport remain outside the deterministic core, allowing the same protocol implementation to serve different storage engines and runtimes.
- **C3:** Follower replication has separate Probe, Replicate, and Snapshot states. Optimistic replication, rejection handling, and bounded in-flight messages are explained together rather than hidden behind a throughput claim. Start with the [replication progress design](https://github.com/etcd-io/raft/blob/main/design.md).

### 2. [tikv/raft-rs](https://github.com/tikv/raft-rs)

**Rust — embeddable Raft implementation used by TiKV.** This is a substantive Rust implementation in the etcd Raft lineage, counted separately for its implementation and integration API; TiKV itself is not counted again. It is valuable for studying how Rust types express the boundary between a protocol decision and completed I/O.

- **C1:** `Ready` distinguishes state and entries requiring persistence from messages that may be sent immediately and messages held until persistence. `must_sync` and the later `LightReady` stage expose the consequences of getting disk, commit, and apply sequencing wrong.
- **C2:** `RawNode` works with an application-supplied `Storage` implementation, while the host controls networking and scheduling.
- **C3:** The API permits selected persistence work to proceed asynchronously under documented conditions. This is a concrete performance mechanism whose safety restrictions are visible in the same interface.

The principal implementation entry point is [`src/raw_node.rs`](https://github.com/tikv/raft-rs/blob/master/src/raw_node.rs); use the [repository overview](https://github.com/tikv/raft-rs) for its relationship to the surrounding application.

### 3. [databendlabs/openraft](https://github.com/databendlabs/openraft)

**Rust — asynchronous, generic Raft library.** OpenRaft makes application data, node identifiers, storage, networking, and runtime choices configurable. It has evolved beyond its async-raft ancestry; the ancestor is not listed separately here.

- **C1:** The integration guide spells out safety obligations such as globally unique node identities and avoiding conflicting instances with the same identity. Its separation of log storage from state-machine storage also makes recovery responsibilities explicit.
- **C2:** `RaftTypeConfig`, `RaftLogStorage`, `RaftStateMachine`, and `RaftNetworkV2` provide substantial application and runtime extension points. Study how these interfaces compose before treating the library as a drop-in server.

Start with the inspected [0.10.0-alpha.36 integration guide](https://docs.rs/openraft/0.10.0-alpha.36/openraft/docs/getting_started/index.html) and the [repository's version guidance](https://github.com/databendlabs/openraft). **Version caveat:** the inspected material distinguishes the 0.10 alpha line from 0.9 bug fixes and warns about pre-1.0 API changes. This entry does not imply API stability.

### 4. [cowsql/raft](https://github.com/cowsql/raft)

**C — asynchronous Raft core with external I/O.** This is a separately evolved fork maintained by the original author of Canonical's Raft library. The README's compatibility claim is specifically bounded to Canonical versions through at least 0.18.0; it should not be generalized to all subsequent APIs.

- **C1:** The event interface distinguishes receiving a message from completing entry or snapshot persistence. It also specifies buffer ownership on successful and failed calls, making memory lifetime part of the integration contract.
- **C2:** The documented core performs no I/O or system calls. Drivers supply network, timer, and storage events, supporting different event loops and asynchronous I/O implementations.
- **C3:** `raft_step` processes events and returns work for the host, allowing batching and asynchronous completion without embedding a particular storage scheduler in the protocol.

Read the [architecture/API documentation](https://raft.readthedocs.io/) and [event interface](https://raft.readthedocs.io/events.html). This report counts the cowsql/Canonical lineage once rather than treating closely related versions as independent discoveries.

### 5. [hashicorp/raft](https://github.com/hashicorp/raft)

**Go — integrated Raft library with pluggable state machine, stores, and transport.** Its organization is useful for comparing a library that supplies substantial runtime machinery with smaller protocol-only cores.

- **C1:** The implementation separates the main consensus loop, exclusive FSM execution, snapshot work, and per-follower replication. Snapshot capture and slower persistence have different concurrency requirements; understanding that boundary is central to implementing a correct FSM.
- **C2:** FSM, log storage, stable storage, snapshot storage, and transport interfaces support different application and persistence choices. The [internal architecture guide](https://github.com/hashicorp/raft/blob/main/docs/README.md) maps these responsibilities to workers and control flow.
- **C4:** The inspected changelog documents evolution across 2019–2024, including snapshot restore fixes, fuzzy testing, mixed-version testing, and the MessagePack time-format compatibility switch. These are concrete examples of managing an evolving distributed protocol, not just evidence of age. See the [changelog](https://github.com/hashicorp/raft/blob/main/CHANGELOG.md).

## Raft runtimes and language ecosystems

### 6. [lni/dragonboat](https://github.com/lni/dragonboat)

**Go — multi-group Raft runtime.** Dragonboat is particularly instructive at the boundary between consensus logs and independently durable application state, and when many Raft groups share a process.

- **C1:** `IOnDiskStateMachine` requires the applied index to be persisted atomically with state changes and recovered state to form a durable prefix without holes. Its API also specifies which update, lookup, snapshot, and synchronization operations may overlap.
- **C2:** Separate state-machine forms and replaceable log/network components support applications with different persistence and concurrency models.
- **C3:** Batched updates and explicit `Sync` separate application progress from synchronization cost; backpressure and memory controls address overloaded storage and slow peers.
- **C4:** The 2019–2021 release history documents snapshot-format changes, an upgrade-checking tool, transport/log-format breaks, filesystem testing, and the RocksDB-to-Pebble transition.

Start with [`statemachine/disk.go`](https://github.com/lni/dragonboat/blob/master/statemachine/disk.go) and the [changelog](https://github.com/lni/dragonboat/blob/master/CHANGELOG.md). The inspected changelog marks the v4 release entry as provisional; branch content and released-version guarantees should be distinguished.

### 7. [rabbitmq/ra](https://github.com/rabbitmq/ra)

**Erlang — Raft framework for Erlang/Elixir applications and multiple local groups.** Its state-machine behavior is a strong example of separating deterministic state transitions from effects executed by the surrounding runtime.

- **C1:** The machine's `apply` callback returns state, replies, and effects. Some effects may repeat after leadership changes or restarts, so applications must respect their idempotency requirements. Snapshot/checkpoint and release-cursor operations encode when log history may safely be discarded.
- **C2:** The `ra_machine` behavior supports application-defined commands, queries, versioned machine modules, and effect-driven integration. It provides a reusable model beyond a single replicated queue or database.
- **C3:** The design addresses the resource footprint of many Raft groups, while effect handling exposes nonblocking message delivery choices instead of forcing every application action into the consensus loop.

Read the [`ra_machine` callback and effect contracts](https://github.com/rabbitmq/ra/blob/main/src/ra_machine.erl) alongside the [library overview](https://github.com/rabbitmq/ra).

### 8. [baidu/braft](https://github.com/baidu/braft)

**C++ — Raft library built around brpc.** The server API documentation contains unusually practical discussion of callback ownership, ambiguous completion, and stale leadership assumptions.

- **C1:** `expected_term` protects submissions from leadership changes, including an ABA-style return to leadership. A failed proposal response need not mean the command can never commit, so retry and deduplication semantics belong in the application. Ordered batch iteration and completion callbacks add further ownership constraints.
- **C2:** The state-machine API and distinct log, metadata, and snapshot storage interfaces support reusable integration with application storage.
- **C3:** Batched application through an iterator and `IOBuf`-based data handling make batching and copying costs visible architectural concerns.

The main study entry is the Chinese-language [server integration guide](https://github.com/baidu/braft/blob/master/docs/cn/server.md). The repository remains unarchived, but [GitHub metadata](https://api.github.com/repos/baidu/braft) showed its last push in October 2024; this is a selection for its implementation, not a claim of active maintenance in 2026.

### 9. [eBay/NuRaft](https://github.com/eBay/NuRaft)

**C++ — extended Raft library derived from cornerstone.** NuRaft has substantial separate implementation and evolution, including application log-store interfaces and snapshot facilities; cornerstone is not counted as another selection.

- **C1:** Its parallel-log design explicitly distinguishes the leader's local append progress from durable replication elsewhere. Correct commit calculation must use durability information rather than assuming the leader has already persisted every candidate entry.
- **C2:** Application-supplied log stores and state machines permit integration into different storage systems; logical snapshot support broadens the application-state boundary described in the [repository overview](https://github.com/eBay/NuRaft).
- **C3:** Parallel log appending overlaps the leader's disk work with network replication. The documentation explains `last_durable_index` and completion notification, connecting the latency optimization to its correctness conditions.

Read [parallel log appending](https://github.com/eBay/NuRaft/blob/master/docs/parallel_log_appending.md). **Feature caveat:** that document labels this mode experimental and disabled by default; its presence is not evidence that every deployment should enable it.

### 10. [apache/ratis](https://github.com/apache/ratis)

**Java — customizable Raft framework; official Apache GitHub mirror.** The [Apache project site](https://ratis.apache.org/) explicitly identifies GitHub as a mirror and distinguishes development source from checked release artifacts.

- **C1:** `StateMachine` separates serial transaction preparation from application stages that may complete asynchronously. Determinism, concurrency, and buffer lifetime obligations appear directly in the API, including reference handling for streamed data.
- **C2:** State machines, transports, logs, and metrics are pluggable. This makes Ratis useful for studying a protocol framework assembled from independently replaceable subsystems.
- **C3:** The optional `DataApi` supports handling larger application data separately from the consensus log and exposes streaming/buffer controls. It is a concrete example of reducing data movement without erasing durability responsibilities.

Start with the [`StateMachine` API and nested interfaces](https://github.com/apache/ratis/blob/master/ratis-server-api/src/main/java/org/apache/ratis/statemachine/StateMachine.java), then use the official site for the module map. This entry counts the mirror and upstream project as one repository selection.

### 11. [MicroRaft/MicroRaft](https://github.com/MicroRaft/MicroRaft)

**Java — embeddable Raft library with application-owned integration.** MicroRaft's state-machine contract is useful for understanding how carefully chosen execution and snapshot rules simplify an application while still imposing nontrivial replay requirements.

- **C1:** State-machine operations execute on the Raft node's executor, avoiding internal concurrency for those callbacks. Replay still requires attention to external side effects. Snapshot chunks must be immutable and deterministic so that independently supplied pieces represent the same state.
- **C2:** State machine, executor, transport, and persistence boundaries allow embedding without adopting a complete server stack.
- **C3:** Chunked snapshots can be obtained from multiple nodes, distributing transfer work. The corresponding immutability requirement makes the performance design's correctness cost explicit.

Read the [`StateMachine` contract](https://github.com/MicroRaft/MicroRaft/blob/master/microraft/src/main/java/io/microraft/statemachine/StateMachine.java) and [repository overview](https://github.com/MicroRaft/MicroRaft). The practical study question is which guarantees come from serialized callbacks and which still belong to the application.

### 12. [sofastack/sofa-jraft](https://github.com/sofastack/sofa-jraft)

**Java — Raft runtime, especially the `jraft-core` subsystem.** This is a substantial Java implementation derived from braft's design. Its accompanying RheaKV application is not counted as a separate repository.

- **C1:** The architecture separates log checks and persistence from committed-entry delivery through `FSMCaller`; replication and state-machine execution have distinct responsibilities. This offers a concrete route through the otherwise easy-to-confuse append, commit, and apply stages.
- **C2:** Public node operations, state machines, log storage, metadata storage, snapshot storage, and RPC form identifiable extension boundaries.
- **C3:** `LogManager` caching and batching, batched FSM delivery, and per-follower `Replicator` objects organized by `ReplicatorGroup` make the pipeline and its performance responsibilities understandable.

Start with the official Chinese-language [engine architecture](https://www.sofastack.tech/projects/sofa-jraft/engine-architecture/) and the [repository's subsystem overview](https://github.com/sofastack/sofa-jraft). The entry concerns the Raft engine; it does not evaluate every auxiliary component in the repository.

### 13. [bakwc/PySyncObj](https://github.com/bakwc/PySyncObj)

**Python — replicated application objects using Raft.** PySyncObj exposes consensus through classes and replicated methods, making it useful for studying the semantic consequences of a high-level API rather than only protocol packet handling.

- **C1:** Its rolling-deployment procedure retains old replicated method versions while mixed-version nodes coexist, then explicitly advances the cluster's code version. The order matters because replayed commands must invoke compatible behavior across replicas.
- **C2:** `SyncObj`, replicated-method decorators, and reusable consumers for common data structures support multiple application models rather than one fixed storage service.
- **C3:** The repository describes copy-on-write process forking for state serialization, separating snapshot cost from the main application path. That mechanism has platform and application integration implications worth examining.

Read the [zero-downtime deployment guide](https://github.com/bakwc/PySyncObj/wiki/Zero-downtime-deploy) and [library overview](https://github.com/bakwc/PySyncObj). The deployment guide is useful evidence of compatibility semantics, but its existence alone is not treated as proof of C4 or of compatibility for arbitrary application changes.

### 14. [dotnet/dotNext](https://github.com/dotnet/dotNext)

**C# — monorepo; relevant subsystems are `DotNext.Net.Cluster` and `DotNext.AspNetCore.Cluster`.** The consensus components offer transport-agnostic Raft and integration with .NET hosting. Other utilities in the monorepo are outside this assessment.

- **C1:** The guide distinguishes durable persistence from the default in-memory consensus state, discusses linearizable reads and leadership cancellation, and leaves client-session duplicate detection to the application. These are important boundaries between a working election cluster and a correct replicated service.
- **C2:** `RaftCluster<TMember>` and `IPersistentState` separate protocol membership, transport, and persistent state; ASP.NET Core hosting is an additional integration layer.
- **C3:** Dedicated TCP transport and HTTP hosting expose different protocol-overhead and deployment tradeoffs within the same conceptual framework.

Start with the substantive [Raft integration guide](https://dotnet.github.io/dotNext/features/cluster/raft.html). **Default caveat:** the documented `ConsensusOnlyState` does not supply durable replicated application storage. This is an integration choice to resolve, not a hidden guarantee supplied by the package.

### 15. [aeron-io/aeron](https://github.com/aeron-io/aeron)

**Java consensus subsystem — `aeron-cluster`, within the larger Aeron repository.** Aeron Cluster combines a replicated service API with a sequenced message transport and an archive. This selection concerns that subsystem rather than treating every transport implementation in the monorepo as consensus code.

- **C1:** The Consensus Module controls ordering and progress, while services consume committed log entries. The subsystem document connects majority recording, deterministic execution, snapshots, and replay during recovery.
- **C2:** Replicated services have reusable facilities for client sessions, timers, snapshots, and service messaging, allowing applications beyond a single key/value store.
- **C3:** The separation of transport streams, archival recording, consensus control, and service execution provides a clear architecture for reasoning about message movement and latency-sensitive processing.

The principal entry point is the [`aeron-cluster` subsystem document](https://github.com/aeron-io/aeron/tree/master/aeron-cluster), read in addition to the [repository overview](https://github.com/aeron-io/aeron). Its service/runtime model is materially different from an event-driven Raft core that delegates all I/O to a host.

## Paxos, quorum frameworks, and replicated objects

### 16. [haraldng/omnipaxos](https://github.com/haraldng/omnipaxos)

**Rust — embedded replicated-log library with pluggable storage and networking.** OmniPaxos is particularly interesting for leader election under partial connectivity and for configurable quorum geometry.

- **C1:** Ballot leader election seeks a quorum-connected leader, and the host must call `tick` to drive election and retransmission behavior. Flexible read/write quorum sizes must satisfy the documented intersection constraint; availability cannot be inferred from either size alone.
- **C2:** The protocol is exposed as a struct that can be integrated with different storage implementations, transports, and runtimes.
- **C3:** Distinct election and append quorum sizes allow a tradeoff between less frequent leader-election work and frequent replication work. The documentation explains the mechanism rather than presenting a universal speedup.

Start with [leader election](https://omnipaxos.com/docs/omnipaxos/leader-election/) and [flexible quorums](https://omnipaxos.com/docs/omnipaxos/flexible-quorums/). **Status caveat:** the project identifies itself as in development, and master-oriented documentation may run ahead of a released API.

### 17. [Tencent/phxpaxos](https://github.com/Tencent/phxpaxos)

**C++ — multi-instance Paxos library with application state machines.** PhxPaxos is useful for studying how execution outcomes and checkpoints connect an application to a consensus engine.

- **C1:** The state-machine API distinguishes a deterministic application-level rejection from an execution/system failure that requires retry. Checkpoint interfaces tie a checkpoint to an executed instance and provide locking around a consistent file set.
- **C2:** Multiple state machines can be identified through `SMID`; storage and network extension points, and state-machine-based auxiliary functions, make it a reusable framework.
- **C3:** The repository's group and batch-proposal facilities expose two different ways to organize replication work: independent consensus groups and amortized proposal processing.

Read [`include/phxpaxos/sm.h`](https://github.com/Tencent/phxpaxos/blob/master/include/phxpaxos/sm.h) alongside the [project overview](https://github.com/Tencent/phxpaxos). **Historical implementation:** [repository metadata](https://api.github.com/repos/Tencent/phxpaxos) showed the last push in December 2023. It was unarchived when checked; this report makes no current-maintenance claim.

### 18. [JPaxos/JPaxos](https://github.com/JPaxos/JPaxos)

**Java, with C++ persistent-memory work — JPaxos/mPaxos research framework.** The repository combines a reusable replicated-service abstraction with recovery-oriented implementations. JPaxos and its mPaxos work are counted once.

- **C1:** The `Service` API associates command execution and snapshots with request positions, specifies execution threading, and distinguishes recovery completion from ordinary operation. Snapshot position and replay semantics are central study topics.
- **C2:** Applications implement the service interface rather than reimplementing Paxos, state transfer, and recovery coordination.
- **C3:** Separate advisory and forced snapshot requests expose the relationship between application snapshot cost and replication-log growth; the repository also contains persistent-memory-oriented work.

Start with [`src/lsr/service/Service.java`](https://github.com/JPaxos/JPaxos/blob/master/src/lsr/service/Service.java). **Historical research code:** the [README](https://github.com/JPaxos/JPaxos) explicitly warns that GitHub may not contain the authors' latest code, and [metadata](https://api.github.com/repos/JPaxos/JPaxos) showed a July 2021 last push. It remains useful for implementation study, with that provenance limitation.

### 19. [Derecho-Project/derecho](https://github.com/Derecho-Project/derecho)

**C++ — replicated objects, ordered multicast, and persistence for high-speed networks.** Derecho provides an important architectural counterpoint to conventional TCP-oriented Raft libraries: strongly ordered operations are integrated with typed replicated objects, subgroups, and RDMA-oriented communication.

- **C1:** Ordered replicated calls, membership changes, persistence, and recovery must agree on the same operation history. The documented separation between ordered operations and point-to-point calls also makes the consistency consequences of each access path visible.
- **C2:** Typed object groups, subgroups, shards, factories, and RPC interfaces support multiple services within a group structure.
- **C3:** The [architecture overview](https://github.com/Derecho-Project/derecho) explains separate multicast, shared-state, and persistence components and their use of remote-memory communication. Performance choices come with deployment assumptions, including homogeneous object representation and relatively stable membership.

Study the [replicated-object example](https://github.com/Derecho-Project/derecho/blob/master/src/applications/demos/simple_replicated_objects.cpp) to see `ordered_send`, `p2p_send`, factories, and reply handling in context. Its intended network and membership environment should not be generalized to arbitrary WAN deployments.

### 20. [ailidani/paxi](https://github.com/ailidani/paxi)

**Go — reusable Paxos-family research and experimentation framework.** Paxi brings several protocols into a shared environment, including Paxos, Flexible Paxos, EPaxos, and WPaxos. It is useful for comparing designs without rebuilding all networking, clients, and experiments for each algorithm.

- **C1:** The quorum code tracks unique acknowledgments and per-zone participation, including majority and grid-shaped quorum predicates. Its shared simulation and fault-injection facilities provide a way to investigate assumptions; their presence is not proof that every protocol variant is correct.
- **C2:** Common nodes, handlers, transport, quorum helpers, and benchmarking infrastructure support multiple substantially different protocols. A Go-channel transport enables a different execution environment from networked runs.
- **C3:** WPaxos uses ownership movement and geographically organized quorums to trade wide-area coordination against more local steady-state replication, as described in the [repository overview](https://github.com/ailidani/paxi).

Read [`quorum.go`](https://github.com/ailidani/paxi/blob/master/quorum.go). **Research-framework caveat:** [metadata](https://api.github.com/repos/ailidani/paxi) showed a December 2023 last push; treat this as an experimental codebase, not an assurance of maintained production integrations.

## Byzantine consensus and replicated state machines

### 21. [bft-smart/library](https://github.com/bft-smart/library)

**Java — BFT-SMaRt replicated state machine library.** Its application/recovery interfaces and alternative state-transfer strategies make it valuable beyond the high-level Byzantine consensus algorithm.

- **C1:** `DefaultRecoverable` coordinates execution, checkpoint boundaries, application state, log state, hashes, and saved replies. The code makes visible why recovery must preserve more than just application bytes and why deterministic serialization matters.
- **C2:** Executable and recoverable service abstractions support application-specific state machines with shared ordering and recovery infrastructure.
- **C3:** Batch execution can split around a checkpoint boundary. The [repository guide](https://github.com/bft-smart/library) also distinguishes in-memory recovery logs from a durability-oriented coordinator and documents memory/liveness tradeoffs in optional read optimizations.

Start with [`DefaultRecoverable.java`](https://github.com/bft-smart/library/blob/master/src/main/java/bftsmart/tom/server/defaultservices/DefaultRecoverable.java). This is a good codebase for studying how checkpoint policy, batching, and reply recovery meet; optional optimizations should be assessed with the limitations documented by the project.

### 22. [hyperledger/SmartBFT](https://github.com/hyperledger/SmartBFT)

**Go — embeddable Byzantine replicated state machine library.** The current canonical repository is under `hyperledger`; older owner paths should not be used as separate projects. This is the consensus library itself, rather than the full Hyperledger Fabric application stack.

- **C1:** `Application.Deliver` requires a decision to be persisted before returning and can communicate reconfiguration. Verification interfaces distinguish proposals, requests, signatures, and verification sequences; synchronization must recover an appropriate decision/configuration state.
- **C2:** Communication, proposal assembly, signing, verification, write-ahead logging, application delivery, and synchronization are explicit host-supplied interfaces. This offers a clear map of the responsibilities a BFT library can and cannot take over from its host.

The substantive entry point is [`pkg/api/dependencies.go`](https://github.com/hyperledger/SmartBFT/blob/main/pkg/api/dependencies.go), supplemented by the [repository overview](https://github.com/hyperledger/SmartBFT). Its BFT-SMaRt inspiration does not make it a duplicate: it is a separate Go implementation with a distinct integration contract.

### 23. [cometbft/cometbft](https://github.com/cometbft/cometbft)

**Go — Byzantine state machine replication engine with ABCI application integration.** CometBFT continues the Tendermint lineage, which is counted once here. Although commonly used in blockchain systems, its engine/application split fits this category directly.

- **C1:** The consensus specification describes height, round, and step transitions, proposal/prevote/precommit processing, validator locking, and the later-round proof needed to unlock. These rules expose the interaction between Byzantine safety and progress under changing message arrival and timeouts.
- **C2:** ABCI/ABCI++ separates consensus from application execution and permits independently implemented applications, including ones outside Go. This is a larger process/service boundary than a conventional in-process FSM callback.

Read the [consensus state-machine specification](https://github.com/cometbft/cometbft/blob/main/spec/consensus/consensus.md) and [repository architecture overview](https://github.com/cometbft/cometbft). The selection is for the reusable consensus engine and its explicit application protocol, not for unrelated token or application economics.

### 24. [circlefin/malachite](https://github.com/circlefin/malachite)

**Rust — modular BFT consensus engine; alpha.** Malachite is useful for studying how a Tendermint-style protocol can be exposed at several integration levels without coupling the core state machine to a particular asynchronous runtime.

- **C1:** The architecture separates vote tracking, round-state transitions, and a driver, with explicit effects for signing, publishing, deciding, and finalizing. Equivocation evidence and recovery/WAL responsibilities are identifiable parts of the surrounding implementation.
- **C2:** A core with no I/O, generic context types, host channels, and higher-level actor integration provide multiple embedding boundaries. Applications can choose how much networking and runtime machinery to reuse.

Start with [`ARCHITECTURE.md`](https://github.com/circlefin/malachite/blob/main/ARCHITECTURE.md). **Status caveat:** the [README](https://github.com/circlefin/malachite) labels the project alpha and says it has not undergone an external audit. Its specification/model-checking work is evidence of an engineering approach, not a substitute for that limitation or a correctness certification.

### 25. [hot-stuff/libhotstuff](https://github.com/hot-stuff/libhotstuff)

**C++ — historical HotStuff research prototype and library.** This is a protocol-study selection with material implementation limits, not a general production recommendation.

- **C1:** The consensus implementation exposes quorum certificates, locked/executed blocks, ancestry checks, and the chain conditions leading to commitment. It is valuable for tracing exactly how the voting and locking rules constrain a block graph.
- **C2:** The repository separates the consensus core from networking/service machinery and the pacemaker, allowing the protocol and progress mechanism to be studied or adapted independently.

Read [`src/consensus.cpp`](https://github.com/hot-stuff/libhotstuff/blob/master/src/consensus.cpp) together with the [README's limitations](https://github.com/hot-stuff/libhotstuff). **Material caveats:** persistent-state recovery and chain pruning are unfinished in the inspected README, and the project documents additional prototype limitations. [Metadata](https://api.github.com/repos/hot-stuff/libhotstuff) showed a June 2023 last push; it is unarchived, but no active-maintenance claim is made.

### 26. [poanetwork/hbbft](https://github.com/poanetwork/hbbft)

**Rust — Honey Badger asynchronous Byzantine consensus components.** This repository offers a compositional view of BFT: reliable broadcast, binary agreement, asynchronous common subset, and threshold-cryptographic machinery are exposed as reusable protocols.

- **C1:** Protocol composition must tolerate malicious participants while relying on eventual delivery. The interface produces messages, outputs, and fault information separately, making adversarial behavior and progress assumptions visible. The documentation also distinguishes synchronous key-generation assumptions from the asynchronous consensus protocols.
- **C2:** A common input-to-`Step` model leaves networking and scheduling to the caller and permits component reuse. The host still owns serialization and appropriate message authentication; the core abstraction is not a complete secure network service.

Read the crate-level architecture and protocol contracts in [`src/lib.rs`](https://github.com/poanetwork/hbbft/blob/master/src/lib.rs) and the [project README](https://github.com/poanetwork/hbbft). **Historical/work-in-progress caveat:** the project describes unfinished status, and [metadata](https://api.github.com/repos/poanetwork/hbbft) showed a January 2024 last push. It was not archived when checked.

## Search coverage and limits

Discovery used more than six distinct live-search formulations and continued through increasingly specialized queries. The main angles were deterministic Raft cores; integrated multi-Raft runtimes; C/C++ asynchronous and storage-oriented libraries; Java Raft frameworks; Rust Raft and Paxos; Erlang, Python, and .NET integrations; Paxos/EPaxos/WPaxos and Viewstamped-replication research; RDMA and replicated objects; and Byzantine families including BFT-SMaRt, HotStuff, Honey Badger, and Tendermint-style engines. Additional Scala, Haskell, Swift, and alternative C-library searches broadened language coverage but did not yield further selections with stronger inspected evidence than the retained set. Later queries increasingly returned overlapping projects, application servers, and small experimental implementations.

Primary evidence consisted of canonical GitHub pages/API responses, actual source and callback contracts, official architecture/API documentation, and selected changelogs. Several GitHub web-page fetches failed; the read-only GitHub API/file connector supplied the corresponding canonical metadata and source instead. No candidate repository was cloned, built, tested, or executed. Performance judgments concern documented mechanisms and constraints, not independently measured speed. Statements about what an engineer can learn are grounded inferences from the inspected architecture, not endorsements of every component.

The list deliberately avoids duplicate counting of applications that consume the selected libraries, ancestors with no separately assessed contribution, tutorials, wrappers, awesome-lists, and unrelated projects that happen to contain “Raft” in their name. It counts monorepos once and identifies the relevant subsystem. Substantive independent implementations or evolved forks, such as raft-rs, NuRaft, SOFAJRaft, and SmartBFT, remain separate because their inspected interfaces and implementation structure provide distinct material. Ratis is explicitly identified as an official mirror.

All 26 retained repositories were unarchived in the checked GitHub metadata. That flag does not establish present maintenance: slower-moving and historical projects are labeled where relevant, and alpha/experimental features are distinguished from stable guarantees. C4 is assigned only where the inspected dated history also demonstrates compatibility, testing, or complexity management. This is a broad selection guide rather than an exhaustive catalogue, security audit, or claim that every subsystem is uniformly exemplary.
