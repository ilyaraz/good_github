# Cluster resource managers and workload schedulers

Research date: **2026-10-09**

This report selects 26 GitHub repositories that implement cluster resource allocation, workload admission, placement, scheduling policy, or the distributed control machinery behind those functions. It spans traditional HPC batch systems, general cluster orchestrators, Kubernetes scheduling extensions, and substantive research implementations. Nested task schedulers are included where they expose meaningful cluster resource models. Workflow definition tools and generic background-job queues are outside the main scope.

The criteria are: **C1 — difficult correctness**, including concurrency, resource invariants, numerical semantics, and failure recovery; **C2 — reusable abstractions** that support multiple workloads or policies; **C3 — performance constraints addressed through understandable architecture**; and **C4 — sustained evolution with concrete evidence of compatibility, testing, or complexity management**. Each selection below has at least two supported criteria. These are reasons to study particular mechanisms, not assertions that every component is equally exemplary. Source links are entry points into the evidence inspected; maintenance observations are dated to this research.

## HPC and batch resource managers

### 1. [SchedMD/slurm](https://github.com/SchedMD/slurm)

**Language/role:** C; full HPC workload manager, including controller, node agents, accounting integration, and scheduling plugins.

Slurm is useful for studying how site policy, resource topology, reservations, and controller responsiveness interact in a production batch scheduler.

- **C1:** Backfill may start lower-priority work only when it does not delay the expected start of higher-priority jobs. Wall-time estimates, reservations, and jobs eligible for overlapping partitions make this more subtle than finding currently idle nodes. The [scheduling configuration guide](https://slurm.schedmd.com/sched_config.html) explains these constraints and reservation behavior.
- **C2:** The controller/node-agent architecture separates allocation from execution and offers plugins for selection, scheduling, priority, preemption, authentication, and topology. The [architecture overview](https://slurm.schedmd.com/overview.html) is the best map of these extension boundaries.
- **C3:** The scheduling guide describes event-triggered short scheduling passes, periodic fuller passes, and backfill lock yielding. Its configuration exposes the tradeoff between search quality and controller responsiveness.

### 2. [openpbs/openpbs](https://github.com/openpbs/openpbs)

**Language/role:** C and C++; batch resource manager with a substantial C++ scheduling subsystem.

The scheduler is particularly instructive when a job's legal start or duration depends on reservations, queue policy, prime time, and dedicated time.

- **C1:** [`src/scheduler/check.cpp`](https://github.com/openpbs/openpbs/blob/master/src/scheduler/check.cpp) checks queue eligibility and time boundaries and implements shrink-to-fit reasoning between minimum and maximum job durations. These are concrete examples of temporal feasibility checks whose boundary behavior affects correctness.
- **C3:** The same implementation bounds candidate-duration exploration rather than exhaustively searching every possible end time, and distinguishes checks that can be reused during a scheduling cycle. Engineers can inspect the actual quality-versus-search-cost decision.
- **C2:** [`data_types.h`](https://github.com/openpbs/openpbs/blob/master/src/scheduler/data_types.h) provides the shared server, queue, job/reservation, resource, and work-item representations used across policy checks. This makes the scheduler's reusable internal model visible rather than hiding it behind configuration syntax.

### 3. [htcondor/htcondor](https://github.com/htcondor/htcondor)

**Language/role:** Primarily C++; high-throughput resource management and distributed job execution.

Study HTCondor for policy-driven matchmaking between independently administered resource providers and job submitters.

- **C2:** The [administrative architecture introduction](https://github.com/htcondor/htcondor/blob/main/docs/admin-manual/introduction-admin-manual.rst) separates collector/negotiator, submit-side schedd/shadow, and execution-side startd/starter responsibilities. Matchmaking and execution have distinct ownership and failure boundaries; existing matches can continue when the central manager is unavailable.
- **C1:** The [ClassAd mechanism](https://github.com/htcondor/htcondor/blob/main/docs/classads/classad-mechanism.rst) defines cross-ad evaluation, `MY`/`TARGET` scoping, and explicit `UNDEFINED` and `ERROR` values. Resource matching therefore involves a real expression-language semantics, including compatibility behavior, rather than simple label equality.

### 4. [flux-framework/flux-core](https://github.com/flux-framework/flux-core)

**Language/role:** Primarily C, with Python interfaces; distributed runtime and resource-management services for hierarchical HPC scheduling.

Flux is a strong study in composing schedulers recursively: an allocation can run its own Flux instance with its own services and policies.

- **C2:** The [broker internals guide](https://github.com/flux-framework/flux-core/blob/master/doc/guide/broker.rst) describes broker event loops, message-based services, modules with separate execution contexts, overlay communication, and nested-instance bootstrapping. These are substantive runtime extension boundaries.
- **C1:** The [KVS guide](https://github.com/flux-framework/flux-core/blob/master/doc/guide/kvs.rst) explains transactional updates to content-addressed trees, serialized root changes, follower caches, and version-based coordination. Its read-your-writes and causal-ordering discussion exposes the consistency machinery needed by distributed management services.
- **C3:** The KVS design also coalesces missing-object requests and distributes cached immutable content, providing an inspectable response to control-plane data-access costs.

### 5. [flux-framework/flux-sched](https://github.com/flux-framework/flux-sched)

**Language/role:** C++; Fluxion resource matching and scheduling components for Flux.

This is a separate scheduling implementation, not a duplicate listing of the Flux runtime. Its graph-oriented resource model is useful for reasoning about heterogeneous, hierarchical allocations.

- **C1:** The [Planner API](https://github.com/flux-framework/flux-sched/blob/master/doc/api/planner.rst) models reservations as time spans with resource quantities and answers whether capacity remains available over an interval. Time-dependent availability is an explicit data-structure contract.
- **C3:** Planner uses scheduled-point and augmented minimum-time trees to support availability queries and resource-graph pruning. This exposes how expensive matching is reduced before policy evaluation.
- **C2:** The [resource API map](https://github.com/flux-framework/flux-sched/blob/master/doc/api/resource.rst) separates resource schemas, evaluators, traversers, and matching callbacks. The planner itself works with generic resource quantities, supporting uses beyond a single CPU allocation policy.

### 6. [oar-team/oar](https://github.com/oar-team/oar)

**Language/role:** Primarily Perl with C components; classic OAR batch scheduler, using the repository's `2.5` branch.

OAR offers a comparatively explicit process-and-event architecture for batch-system lifecycle control. This entry concerns classic OAR, not the separate OAR3 implementation.

- **C1:** The [module architecture](https://github.com/oar-team/oar/blob/2.5/docs/source/admin/modules.rst) separates wall-time/dead-node detection, job termination, and node-state changes. Termination escalates after timeouts, and uncertain nodes can become suspected rather than immediately returning to normal allocation.
- **C2:** The same document shows an automaton-driven coordinator, a launcher pool, reservation checking, and replaceable Gantt-based scheduling policies supporting moldable, timesharing, and best-effort workloads.
- **C3:** The architecture includes bounded parallel power-management operations and keepalive constraints. The [changelog](https://github.com/oar-team/oar/blob/2.5/CHANGELOG) provides useful follow-through on practical complications, including database transaction/locking fixes and node-wakeup races. These are stronger study material than a feature checklist alone.

### 7. [It4innovations/hyperqueue](https://github.com/It4innovations/hyperqueue)

**Language/role:** Rust; task scheduler that can aggregate workers inside allocations supplied by systems such as Slurm or PBS.

HyperQueue belongs at the nested scheduling layer. Its own [FAQ](https://github.com/It4innovations/hyperqueue/blob/main/docs/faq.md) makes clear that multi-user isolation is outside its scope; it should not be mistaken for a site's security and accounting authority.

- **C1:** The [resource model](https://github.com/It4innovations/hyperqueue/blob/main/docs/jobs/resources.md) distinguishes indexed resources, which require exclusive identities, from sum resources, which require bounded aggregate consumption. Resource groups add placement concerns such as NUMA locality and compact versus scattered allocation.
- **C2:** Arbitrary named resources and grouping policies make this model reusable for CPUs, accelerators, licenses, and application-defined constraints, subject to the documented distinction between logical accounting and actual enforcement.
- **C3:** The FAQ explains its Tokio-based execution and Tako work stealing, and output streaming that avoids a proliferation of small output files. These are concrete responses to scheduler overhead and parallel-filesystem pressure.

### 8. [hpc-gridware/clusterscheduler](https://github.com/hpc-gridware/clusterscheduler)

**Language/role:** C++; Open Cluster Scheduler, a substantively evolved Grid Engine descendant.

The value here is the detailed scheduler-thread implementation, including parallel jobs, resource quotas, reservations, and category-based reuse. Its Grid Engine lineage is explicit; this is not an unrelated new design or an arbitrary mirror.

- **C1:** The [scheduler-thread development guide](https://github.com/hpc-gridware/clusterscheduler/blob/master/doc/markdown/manual/development-guide/25_scheduler_thread.md) explains time-based resource diagrams and the select/assign/debit sequence. Failed assignments must revert quota debits, while reservations and calendars affect future availability.
- **C3:** The guide describes category caches that avoid repeating unsuitable-host/queue checks, plus different slot-search strategies for parallel jobs. Event mirroring and copied master lists make the scheduling data path visible.
- **C2:** The same architecture separates mirrored cluster state, policy evaluation, resource accounting, and orders sent back to the master, providing useful boundaries for studying extensions to a mature batch-system design.

### 9. [PKUHPC/CraneSched](https://github.com/PKUHPC/CraneSched)

**Language/role:** C++; HPC controller and node-agent backend. The separate Go client/frontend repository is not counted here.

CraneSched adds a newer HPC implementation to the selection. Its controller code is substantial and sometimes centralized, making it useful for studying both mechanisms and their complexity costs.

- **C1:** [`JobScheduler.cpp`](https://github.com/PKUHPC/CraneSched/blob/master/src/CraneCtld/JobScheduler.cpp) restores previous runtime-state fields when persistence fails and reconstructs scheduling state from database snapshots during initialization. The suspend paths also coordinate parallel node RPC results instead of assuming all nodes transition together.
- **C2:** [`JobScheduler.h`](https://github.com/PKUHPC/CraneSched/blob/master/src/CraneCtld/JobScheduler.h) exposes priority-sorter and node-cost policy interfaces together with pending/running job and resource views. Basic and multifactor priority strategies share those boundaries.
- **C1, temporal accounting:** Its time-indexed resource model orders releases before allocations at equal timestamps, an important detail for adjacent reservations and capacity conservation.

## General cluster orchestration

### 10. [hashicorp/nomad](https://github.com/hashicorp/nomad)

**Language/role:** Go; general cluster scheduler and workload orchestrator.

Nomad offers a clear path from desired workload state through reconciliation and placement to a validated allocation plan.

- **C1:** The [evaluation lifecycle](https://github.com/hashicorp/nomad/blob/main/contributing/architecture-eval-lifecycle.md) describes durable evaluations, concurrent scheduling against snapshots, leader-side plan validation, and retries when plans conflict or become stale. This is a concrete optimistic-concurrency protocol rather than an assumption of globally current scheduler state.
- **C2:** The [scheduler implementation guide](https://github.com/hashicorp/nomad/blob/main/scheduler/README.md) explains scheduler interfaces, reconciliation classifications, feasibility iterators, and ranking stages. Device, volume, network, affinity, quota, and workload-lifecycle concerns fit into identifiable abstractions.
- **C3:** Parallel scheduling work is separated from authoritative plan acceptance, while iterator stacks separate cheap feasibility reduction from ranking. Both architectural choices address throughput without eliminating correctness checks.

### 11. [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)

**Language/role:** Go; monorepo entry specifically for **kube-scheduler** and its framework.

The scheduler demonstrates how a widely reused placement engine exposes policy hooks while retaining control of lifecycle and resource-state transitions.

- **C1:** The [Scheduling Framework documentation](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/) distinguishes serial scheduling cycles from concurrent binding cycles. Reserve/Unreserve prevents resource races; Unreserve must be idempotent and cannot fail, and failed or timed-out Permit operations require cleanup.
- **C2:** Filter, Score, Reserve, Permit, Bind, and related extension points let policies customize different stages without replacing the entire scheduler. The [`pkg/scheduler` source tree](https://github.com/kubernetes/kubernetes/tree/master/pkg/scheduler) connects the lifecycle description to queues, cache, framework, and plugins.
- **C3:** Node filtering can proceed concurrently even though each scheduling decision has an ordered lifecycle. This is useful material for separating safe parallel work from stateful commitment.

### 12. [apache/hadoop](https://github.com/apache/hadoop)

**Language/role:** Java; official Apache repository, with this entry restricted to the **YARN** subsystem.

YARN is useful for studying the separation between cluster-wide allocation and application-specific execution management. Hadoop's other subsystems are not separate entries here.

- **C2:** The [YARN architecture](https://github.com/apache/hadoop/blob/trunk/hadoop-yarn-project/hadoop-yarn/hadoop-yarn-site/src/site/markdown/YARN.md) splits responsibilities among ResourceManager, per-application ApplicationMaster, and per-node NodeManager. Pluggable allocation policies work with resource containers while applications retain their execution logic.
- **C1:** [ResourceManager restart documentation](https://github.com/apache/hadoop/blob/trunk/hadoop-yarn-project/hadoop-yarn/hadoop-yarn-site/src/site/markdown/ResourceManagerRestart.md) explains work-preserving reconstruction from node and application reports. It also distinguishes state persistence from fencing: the documented ZooKeeper store supports fencing for HA, whereas filesystem and LevelDB storage do not provide the same split-brain protection.

### 13. [moby/swarmkit](https://github.com/moby/swarmkit)

**Language/role:** Go; distributed orchestration toolkit underlying Docker Swarm mode.

SwarmKit has unusually approachable design documents for connecting task-state semantics with a practical placement algorithm.

- **C1:** The [task model](https://github.com/moby/swarmkit/blob/master/design/task_model.md) treats task specifications as immutable and distinguishes desired from observed state. Replacing a task is a different operation from mutating or migrating an existing assignment.
- **C3:** The [scheduler design](https://github.com/moby/swarmkit/blob/master/design/scheduler.md) explains filter setup reuse, batching equivalent service tasks, topology-aware node organization, and bounded scheduling latency. It also penalizes repeatedly failing nodes so their apparent emptiness does not continually attract more work.
- **C2:** A filter pipeline and explicit task lifecycle provide reusable seams for eligibility rules, resource checks, and service-level reconciliation.

## Kubernetes admission and specialized placement

### 14. [volcano-sh/volcano](https://github.com/volcano-sh/volcano)

**Language/role:** Go; batch-oriented Kubernetes scheduler and supporting workload controllers.

Volcano is useful for studying collective jobs and policy-rich queue management on top of Kubernetes objects.

- **C1:** The [capacity scheduling design](https://github.com/volcano-sh/volcano/blob/master/docs/design/capacity-scheduling.md) distinguishes guaranteed, deserved, and maximum capacity. Reclamation must identify borrowed resources without violating queue guarantees; admission, allocation, and preemption cannot use interchangeable resource totals.
- **C2:** The [capacity plugin implementation](https://github.com/volcano-sh/volcano/blob/master/pkg/scheduler/plugins/capacity/capacity.go) turns these distinctions into queue state and scheduler callbacks, including separate allocated and queued resource accounting. It also shows the additional bookkeeping introduced by hierarchical queues and newer resource types.

The design document is a proposal-era explanation; the current implementation is the companion source for judging what has actually evolved beyond that proposal.

### 15. [apache/yunikorn-core](https://github.com/apache/yunikorn-core)

**Language/role:** Go; platform-independent core of Apache YuniKorn's application and queue scheduler.

This entry counts the core once; its Kubernetes shim is an integration layer rather than another independent selection.

- **C2:** The [architecture](https://yunikorn.apache.org/docs/next/design/architecture/) separates scheduler core, scheduler-interface protocol, and platform shim. The shim translates platform state and performs binding, while queue and application policy remain in the core. The abstraction supports platform independence; it does not establish that every conceivable platform integration exists.
- **C1:** The [concurrency guide](https://yunikorn.apache.org/docs/next/developer_guide/concurrency/) documents lock ordering, exceptions around partition state, a single scheduling goroutine alongside concurrent event handling, and snapshot/copy rules. It also distinguishes absent resource limits from zero limits and describes temporary overcapacity during recovery or configuration changes.

These documents expose both concurrency invariants and the non-obvious semantics of sparse resource vectors. The linked `next` documentation is development documentation, not a promise about every released version.

### 16. [kubernetes-sigs/kueue](https://github.com/kubernetes-sigs/kueue)

**Language/role:** Go; Kubernetes workload queueing, quota reservation, and admission control.

Kueue is an admission layer, not a replacement for all pod-level placement. It is valuable for understanding the boundary between permission to consume resources and the later act of placing pods.

- **C2:** The [admission model](https://github.com/kubernetes-sigs/kueue/blob/main/site/content/en/docs/concepts/admission.md) connects LocalQueues, ClusterQueues, quota reservation, and extensible AdmissionChecks. Temporary failures can release quota and requeue work; permanent rejection has a different lifecycle.
- **C1:** The [fair-sharing explanation](https://github.com/kubernetes-sigs/kueue/blob/main/site/content/en/docs/concepts/fair_sharing.md) analyzes preemption using dominant resource shares and states conditions under which cycles are excluded. Its qualification matters: the argument assumes particular share/borrowing behavior and does not claim a general proof for all hierarchical configurations.

This is especially useful code to study when deciding which invariants belong in quota admission rather than the underlying node scheduler.

### 17. [armadaproject/armada](https://github.com/armadaproject/armada)

**Language/role:** Go; queueing and scheduling of batch work across multiple Kubernetes clusters.

Armada separates the global backlog from worker clusters and makes event-log consistency part of its scheduling architecture.

- **C2:** The [system overview](https://github.com/armadaproject/armada/blob/master/docs/system_overview.md) describes global scheduling, job leasing, per-cluster executors, and the transition from queued to leased, pending, running, and completed work. Keeping the backlog outside worker clusters is a concrete scaling boundary.
- **C1:** [Consistency across views](https://github.com/armadaproject/armada/blob/master/docs/maintaining_consistency_across_views.md) explains ordered, idempotent event application and transactions coupling each view's updates with its log offset. Recovery can replay events without silently duplicating effects or losing acknowledged progress.
- **C3:** Multiple consumers can maintain purpose-specific views from the event stream. The design explicitly accepts eventual consistency and its user-visible delays rather than pretending every read is globally synchronous.

### 18. [koordinator-sh/koordinator](https://github.com/koordinator-sh/koordinator)

**Language/role:** Go; Kubernetes scheduling and resource-management extensions, including elastic quotas and workload co-location.

The selected subsystem is hierarchical elastic quota scheduling. It connects organizational sharing policy to concrete plugin and informer state.

- **C1:** The [elastic quota design](https://github.com/koordinator-sh/koordinator/blob/main/docs/proposals/scheduling/20220722-multi-hierarchy-elastic-quota-management.md) distinguishes minimum, maximum, runtime entitlement, demand, and sharing weight across a quota tree. Borrowing unused resources and returning capacity must respect both ancestor constraints and demand limits.
- **C2:** The [elasticquota plugin](https://github.com/koordinator-sh/koordinator/blob/main/pkg/scheduler/plugins/elasticquota/plugin.go) integrates through PreFilter, PostFilter, and Reserve interfaces, maintains quota managers per tree, and updates state through informer events. Policy is organized around explicit group managers and snapshots rather than being a single scheduling predicate.

The proposal explains the model; the implementation demonstrates its integration and concurrent state management. Proposal-era non-goals should not be read as a definitive list of current product limitations.

### 19. [kubernetes-sigs/scheduler-plugins](https://github.com/kubernetes-sigs/scheduler-plugins)

**Language/role:** Go; a collection of substantive out-of-tree scheduling policies, not a standalone cluster manager.

This repository is useful for comparing specialized policies within one extension framework. Plugin maturity and operational requirements vary.

- **C1:** The [PodGroup coscheduling design](https://github.com/kubernetes-sigs/scheduler-plugins/blob/master/kep/42-podgroup-coscheduling/README.md) covers minimum membership/resources, Permit waiting, timeout rejection, and backoff. Partial progress for a gang creates lifecycle problems that ordinary independent-pod scheduling does not have; the proposal also candidly identifies preemption limitations.
- **C2:** Coscheduling and topology-aware placement reuse the Kubernetes framework while introducing different state and policy abstractions. The [NodeResourceTopology test guide](https://github.com/kubernetes-sigs/scheduler-plugins/blob/master/pkg/noderesourcetopology/TESTS.md) shows the breadth of the resource model: init versus application containers, NUMA-local versus node-total capacity, resource types, and policy scopes.
- **C3:** Group backoff avoids repeatedly spending scheduling work on groups that cannot yet proceed. The topology test matrix is also useful evidence of how combinatorial policy interactions are made reviewable.

### 20. [kai-scheduler/KAI-Scheduler](https://github.com/kai-scheduler/KAI-Scheduler)

**Language/role:** Go; Kubernetes scheduler focused on AI workloads, collective jobs, and hierarchical resource sharing.

The canonical repository verified for this report is under `kai-scheduler`. Its kube-batch lineage does not make it a duplicate of Volcano: the inspected implementation has its own action/session, group, quota, and binding model.

- **C1:** The [scheduler concepts](https://github.com/kai-scheduler/KAI-Scheduler/blob/main/docs/developer/scheduler-concepts.md) describe transactional scheduling statements that can be committed or discarded, including speculative preemption scenarios. PodGroup and subgroup thresholds must survive both successful and failed scheduling attempts without retaining partial effects.
- **C2:** Actions such as allocate, reclaim, preempt, consolidate, and stale-gang eviction run through a common session model. Queue hierarchies, policy plugins, and group abstractions support multiple sharing and collective-placement policies.
- **C3:** Scheduling operates on cache snapshots and hands binding to an asynchronous binder through BindRequest objects. This separates expensive decision-making from API-side commitment while keeping their interface explicit.

### 21. [kubewharf/godel-scheduler](https://github.com/kubewharf/godel-scheduler)

**Language/role:** Go; Kubernetes scheduler with concurrent scheduling flows and separate binding conflict checks.

Godel is a useful architectural comparison to kube-scheduler. Its repository README lists Kubernetes compatibility only through **1.24.6**, so this selection does not imply suitability as a drop-in scheduler for a current cluster.

- **C3:** The [concurrent scheduling guide](https://github.com/kubewharf/godel-scheduler/blob/main/docs/features/concurrent-scheduling.md) describes independently handled subclusters and scheduling flows. Dispatching, scheduling, and binding are separated to permit more scheduling work to occur concurrently.
- **C1:** The binder's [resource conflict check](https://github.com/kubewharf/godel-scheduler/blob/main/pkg/binder/framework/plugins/noderesources/conflict_check.go) recomputes pod requests and checks them against node information before commitment. Optimistic placement therefore has an explicit later validation boundary.
- **C2:** The repository's Unit/Pod framework distinguishes collective scheduling units from individual pods, offering a reusable way to express group-level and per-pod decisions.

## Historical systems and research implementations

These entries are included for substantive mechanisms, with lifecycle limitations made explicit. Apache Mesos and Aurora are official ASF GitHub source repositories retained for historical study; their official retirement notices take precedence over interpreting commit recency as ongoing project support.

### 22. [apache/mesos](https://github.com/apache/mesos)

**Language/role:** C++; two-level resource manager. **Retired:** the [Apache Attic record](https://attic.apache.org/projects/mesos.html) dates retirement to August 2025 and the move to the Attic to October 2025. The repository was not marked archived when checked, which is not evidence that the project remains active.

- **C2:** The [architecture](https://github.com/apache/mesos/blob/master/docs/architecture.md) separates allocation of resource offers from framework-specific task placement. Allocator policy controls which framework receives capacity, while frameworks can accept or reject offers to implement application-specific requirements.
- **C1:** The [reconciliation protocol](https://github.com/apache/mesos/blob/master/docs/reconciliation.md) addresses dropped messages and diverging task beliefs through explicit and implicit reconciliation, retry/backoff behavior, and rules for stale offers after disconnection. This is valuable material on recovering from ambiguous distributed execution outcomes.

### 23. [twosigma/Cook](https://github.com/twosigma/Cook)

**Language/role:** Primarily Clojure, with client components; fair batch scheduling. **Archived:** the repository announces the end of development after seven years and is read-only.

- **C1:** The [scheduler concepts](https://github.com/twosigma/Cook/blob/master/scheduler/docs/concepts.md) distinguish a job's persistent intent from retried execution instances, explicitly depending on idempotent work. Fair ranking, rebalancing/preemption, and actual placement are separate decisions.
- **C3:** The same guide describes bin-packing and a shrinking candidate window when leading jobs cannot be placed. Engineers can study the tension between throughput, fairness, and repeatedly examining infeasible work.
- **C4:** The [scheduler changelog](https://github.com/twosigma/Cook/blob/master/scheduler/CHANGELOG.md) records concrete evolution of Kubernetes watch processing, launch/kill ordering locks, GPU scheduling tests, and rebalancer integration. Together with the repository's stated development span, this supports sustained complexity management rather than an age-only maturity claim.

### 24. [apache/aurora](https://github.com/apache/aurora)

**Language/role:** Java scheduler with Python Thermos execution components; Mesos-based service and batch orchestration. **Archived and retired:** the [Apache Attic record](https://attic.apache.org/projects/aurora.html) records retirement in February 2020 and the Attic move in April 2021.

- **C1:** The [storage architecture](https://github.com/apache/aurora/blob/master/docs/operations/storage.md) combines a replicated log with an in-memory query store. Writes reach the log before updating cached state, and locking, replay, and snapshots determine what survives leadership changes and restarts.
- **C3:** The same design distinguishes consistent from weakly consistent read paths and uses snapshots to constrain recovery work. The tradeoff between durable writes and efficient scheduler queries is visible.
- **C2:** The [task lifecycle](https://github.com/apache/aurora/blob/master/docs/reference/task-lifecycle.md) makes partition handling configurable: deferring replacement can be appropriate for expensive tasks, while immediate replacement serves other workloads. Flapping, throttling, terminal states, and preemption live in an explicit lifecycle model.

### 25. [camsas/firmament](https://github.com/camsas/firmament)

**Language/role:** C++; research cluster scheduler based on minimum-cost flow. **Historical research implementation:** the repository's latest push observed through GitHub metadata was in 2021; ongoing maintenance is not asserted.

- **C2:** The [official research-project description](https://www.cl.cam.ac.uk/research/srg/netos/camsas/firmament/) explains representing tasks, resources, and placement choices as a flow network. Modular cost models let the same scheduling machinery express different placement objectives and resource-topology preferences.
- **C1:** The actual [cost-model interface](https://github.com/camsas/firmament/blob/master/src/scheduling/flow/cost_model_interface.h) exposes arc capacities, minimum flow, costs, continuation/preemption choices, and equivalence classes. Its contract includes monotonic waiting penalties, making numerical and policy assumptions inspectable. This is evidence of a difficult modeling problem, not proof that every cost model is correct.
- **C3:** Resource and task equivalence classes aggregate repeated structure, providing a concrete architectural approach to keeping optimization-based placement tractable.

### 26. [stanford-futuredata/gavel](https://github.com/stanford-futuredata/gavel)

**Language/role:** Python; heterogeneous GPU cluster scheduling research implementation, with simulator and execution machinery.

Gavel adds a numerical optimization perspective that is underrepresented in the otherwise predominantly discrete scheduling systems. Treat it as a research artifact rather than an implied production support commitment.

- **C1:** [`max_min_fairness.py`](https://github.com/stanford-futuredata/gavel/blob/master/scheduler/policies/max_min_fairness.py) constructs throughput-normalized allocation programs. Worker-type capacity, per-job allocation bounds, scale factors, and pair-allocation symmetry require careful treatment; the code also handles solver status and clips numerical results. Such handling warrants inspection rather than assuming an optimizer automatically ensures end-to-end feasibility.
- **C2:** Policies operate over common throughput/allocation representations and can be evaluated through the supplied simulation and execution framework. The [experiment guide](https://github.com/stanford-futuredata/gavel/blob/master/EXPERIMENTS.md) describes reproducible traces, seeds, measured throughput inputs, and physical-cluster experiments.
- **C3:** The design explicitly incorporates different job throughputs on different accelerator types. The experiment guide also distinguishes simulation-based evidence from physical-cluster runs, avoiding a false equivalence between them.

## Search coverage and limitations

Discovery used more than six meaningfully different live search formulations: traditional HPC batch managers and backfill; heterogeneous and hierarchical Flux scheduling; Kubernetes gang scheduling, queue admission, and quota sharing; general datacenter orchestration and resource offers; Rust/Perl implementations and nested schedulers; Grid Engine descendants; concurrent and topology-aware Kubernetes schedulers; optimization-based research schedulers; GPU fairness; and newer HPC systems such as CraneSched. Targeted follow-up searches checked retirement, architecture, consistency, and implementation entry points. Later language/backfill searches increasingly returned previously identified systems, thin integrations, generic job queues, and unrelated tools.

Canonical repository identities were checked by opening GitHub repository pages or querying the GitHub API. Every retained repository has an additional inspected primary document or source file containing substantive architecture or implementation material; search snippets were not used as the sole verification. Exact branches and file paths were checked against repository trees or successful source reads. Archive flags were checked where available, and official project retirement records were consulted for Mesos and Aurora. API rate limiting affected the final discovery round, which used GitHub pages and direct public source reads instead. No repository code was executed and no dependencies were installed.

The selection deliberately excludes generic workflow/DAG engines, cron services, background-job libraries, and generated bindings whose main contribution is not resource management or placement. Ray and Dask are adjacent distributed execution runtimes but were not added merely to enlarge this resource-manager-focused selection. Pure simulators and integrations are not counted separately; Firmament integrations, YuniKorn's Kubernetes shim, and CraneSched's frontend do not create additional entries. Flux core and Fluxion are separate because each supplies a substantial, independently inspectable runtime or scheduling implementation. Grid Engine lineage is disclosed rather than presented as unrelated invention. Proprietary LSF/Moab implementations and unverified or lightly differentiated TORQUE/OpenLava forks were not padded into the list.

This is a source-based selection guide, not a benchmark, security audit, or deployment recommendation. No numerical performance result was independently reproduced. Links generally follow the verified development branch and may change; design proposals are paired with implementation evidence where necessary, and research or retired systems are labeled. C1–C3 judgments are grounded engineering interpretations of the linked mechanisms. C4 is claimed selectively where both a development span and concrete complexity-management evidence were established.
