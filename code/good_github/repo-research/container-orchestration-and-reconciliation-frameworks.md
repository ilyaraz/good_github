# Container orchestration and reconciliation frameworks

Research date: **2026-10-09**.

This report selects 25 GitHub repositories whose central work is scheduling containerized workloads, implementing reusable reconciliation machinery, or coordinating desired state across applications, clusters, and edge nodes. It includes complete orchestrators, operator runtimes, resource composition engines, GitOps reconcilers, and specialized workload controllers. Cluster API and Crossplane are included for their reusable reconciliation frameworks; they are not container schedulers. Mesos is an explicitly historical reference. The list is a reading guide, not a ranking or a claim that every subsystem is exemplary.

Criteria used below:

- **C1 — Correctness:** substantial invariants, concurrency, state transitions, adversarial inputs, or recovery from partial failure.
- **C2 — Abstractions:** reusable interfaces and mechanisms that support materially different workloads or controllers.
- **C3 — Performance and structure:** concrete resource, throughput, or latency constraints addressed through understandable architecture. This does not imply independently measured performance.
- **C4 — Evolution:** years of documented changes accompanied by compatibility work, testing, migrations, or complexity management. Age alone does not qualify.

The criteria are selective: each entry supports at least two, and an omitted criterion is not a negative judgment. Linked technical documents serve as the recommended entry points. Repository headings use canonical GitHub locations checked during research.

## General orchestration engines

### 1. [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)

**Language / role:** Go; container orchestration control plane. Within this monorepo, focus on kube-scheduler and its framework rather than attempting to read the entire platform at once.

Study how placement decisions interact with asynchronous binding and partially completed operations. **C1:** scheduling cycles are serialized while binding cycles may overlap; the Reserve/Unreserve protocol prevents reservation races and requires idempotent rollback when a later stage fails. **C2:** plugins implement separate filtering, scoring, reservation, permission, and binding interfaces, allowing different policies to share the scheduler machinery. **C3:** concurrent node evaluation and event-sensitive queueing avoid treating every cluster change as a reason to retry every unschedulable Pod. These mechanisms and their contracts are explained in the [scheduling framework documentation](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/).

### 2. [hashicorp/nomad](https://github.com/hashicorp/nomad)

**Language / role:** Go; scheduler for containers, batch jobs, services, and other executable workloads.

The useful reading path follows an evaluation from job registration to allocation and deployment health monitoring. **C1:** workers plan against snapshots, so the leader validates and serializes proposed plans, rejecting conflicts and forcing retries against refreshed state. Evaluations are acknowledged or returned for another attempt, and leader transitions reconstruct pending work. **C2:** evaluation-specific schedulers for service, system, system-batch, and batch jobs reuse the same broker, planning, allocation, and client execution structure. **C3:** scheduling workers run across servers, while feasibility checks and blocking state queries limit unnecessary work. The [evaluation lifecycle architecture](https://github.com/hashicorp/nomad/blob/main/contributing/architecture-eval-lifecycle.md) connects these mechanisms in one unusually useful implementation narrative.

### 3. [moby/swarmkit](https://github.com/moby/swarmkit)

**Language / role:** Go; reusable orchestration toolkit underlying Docker Swarm mode.

Study its explicit task lifecycle and scheduler-local state. **C1:** assignment is a one-way task transition; filters enforce resource, port, platform, and availability constraints, and per-service failure tracking prevents repeatedly favoring a node that cannot successfully run that service. **C2:** the filter pipeline separates task-specific preprocessing, node checks, and explanations, while replicated and global services share scheduling machinery. **C3:** equivalent tasks are batched by service and specification version, sharing a placement tree; scheduler-maintained maps and resource tallies avoid repeated store queries. The [scheduler design](https://github.com/moby/swarmkit/blob/master/design/scheduler.md) explains both the optimization and its latency tradeoff, rather than merely asserting scalability.

### 4. [apache/mesos](https://github.com/apache/mesos)

**Language / role:** C++; historical cluster resource manager and framework substrate. This is the official Apache GitHub source mirror. Mesos retired in August 2025 and completed its move to the Apache Attic in October 2025; it is a historical study selection, not an actively supported deployment recommendation. See the [Apache retirement record](https://attic.apache.org/projects/mesos.html).

**C1:** dropped launch messages, scheduler failover, and master failover can leave participants with different task states. Explicit and implicit reconciliation, bounded outstanding reconciliation work, and exponential retry are documented responses to those failures. **C2:** resource offers separate allocation policy from each framework's task-placement decisions, with pluggable allocation modules supporting different sharing policies. Start with the [architecture](https://mesos.apache.org/documentation/latest/architecture/) and then the [reconciliation protocol](https://mesos.apache.org/documentation/latest/reconciliation/). The architectural lesson is the division of responsibility between a cluster manager and independently recovering schedulers.

## Reusable controller and operator runtimes

### 5. [kubernetes-sigs/controller-runtime](https://github.com/kubernetes-sigs/controller-runtime)

**Language / role:** Go; reusable Kubernetes controller runtime used by Kubebuilder and Operator SDK.

The central abstraction deliberately turns events into object identities rather than instructions to replay a particular change. **C1:** reconciliation reads current state, duplicate requests are coalesced, ordinary errors trigger backoff, and terminal errors explicitly stop retries. This is worth studying when reasoning about missed, repeated, or stale notifications. **C2:** generic reconciler interfaces work with Kubernetes resources and external systems while separating domain logic from event delivery and scheduling. The [reconcile package contract](https://pkg.go.dev/sigs.k8s.io/controller-runtime/pkg/reconcile) is the best first entry point. The [versioning policy](https://github.com/kubernetes-sigs/controller-runtime/blob/main/VERSIONING.md) also makes an important library boundary explicit: patch releases avoid breaking changes, whereas minor releases can change APIs alongside Kubernetes dependencies.

### 6. [kube-rs/kube](https://github.com/kube-rs/kube)

**Language / role:** Rust; Kubernetes client, runtime, and custom-resource tooling. The relevant monorepo subsystem is `kube-runtime`.

**C1:** watchers handle interrupted watches and relisting; controllers combine ownership relationships, custom relationship mappings, and configurable watch backoff. Shared-stream APIs explicitly document a readiness requirement needed to avoid deadlock. **C2:** API clients, watchers, reflectors, stores, and controllers compose independently, supporting both statically typed and discovered resource kinds. See the [Controller API](https://docs.rs/kube/latest/kube/runtime/controller/struct.Controller.html).

**C4:** the [changelog](https://kube.rs/changelog/) documents evolution from 2020 through 2026, including the move to parallel reconciliation, a 2021 runner-wakeup fix backported to the older Tokio branch, and later schema and watch fixes. This is concrete migration and maintenance evidence, not simply an old creation date. Study the runtime alongside its migration history to see how Rust trait and async-runtime constraints shape a public framework.

### 7. [nolar/kopf](https://github.com/nolar/kopf)

**Language / role:** Python; handler-oriented Kubernetes operator framework. This is the continuation of the original Zalando codebase, counted once.

**C1:** the framework distinguishes temporary, permanent, and unexpected handler failures, with retry delays, retry limits, and timeouts. The [error-handling documentation](https://docs.kopf.dev/en/stable/errors/) explains how a retry can be postponed without sleeping inside the handler and blocking other processing for that object. **C2:** decorators, timers, per-resource daemons, and indexes support multiple ways to implement domain controllers.

An important study caveat is explicit in the [reconciliation guide](https://docs.kopf.dev/en/latest/reconciliation/): change callbacks alone do not establish convergence with external actual state. The operator author must arrange observation and reconciliation, for example through timers, daemons, and indexed child resources. This makes Kopf useful for comparing handler-driven APIs with controller-runtime's level-based contract.

### 8. [operator-framework/java-operator-sdk](https://github.com/operator-framework/java-operator-sdk)

**Language / role:** Java; operator runtime built on the Fabric8 Kubernetes client.

Study how the SDK maps changes in secondary resources onto primary-resource reconciliation. **C1:** it guarantees no concurrent reconciler execution for the same primary resource while permitting different primaries to run in parallel. On reference changes, mapping both old and new secondary-resource versions lets dropped dependencies trigger corrective reconciliation too. **C2:** event sources support Kubernetes resources and external notification systems; mapping and caching are reusable framework interfaces. **C3:** informer caching and event-driven scheduling reduce repeated API reads and unnecessary reconciliation. The [event-source documentation](https://javaoperatorsdk.io/docs/documentation/eventing/) explains these contracts; the [architecture overview](https://javaoperatorsdk.io/docs/documentation/architecture/) supplies the surrounding runtime structure. Some newer cache options carry their own maturity caveats in the documentation.

### 9. [dotnet/dotnet-operator-sdk](https://github.com/dotnet/dotnet-operator-sdk)

**Language / role:** C# / .NET; KubeOps operator SDK. The former `buehler/dotnet-operator-sdk` URL redirects here.

**C1:** a shared coordinator prevents reconciliation or finalization of the same entity UID from running concurrently, even when multiple controllers match that entity type. Conflict policies distinguish waiting, discarding redundant work, and delayed requeueing. **C2:** the runtime separates typed entity controllers, watchers, finalizers, and operator lifecycle management; see the [operator engine documentation](https://github.com/dotnet/dotnet-operator-sdk/blob/main/src/KubeOps.Operator/README.md). **C3:** a semaphore shared per entity type limits parallel reconciliations before dequeueing, so adding more controllers does not multiply the concurrency budget. The [parallel reconciliation design](https://github.com/dotnet/dotnet-operator-sdk/blob/main/docs/docs/operator/configuration/parallel-reconciliation.mdx) is a concrete study of per-object exclusion versus global throughput control.

### 10. [metacontroller/metacontroller](https://github.com/metacontroller/metacontroller)

**Language / role:** Go runtime with language-independent JSON webhooks; community continuation of the original GKE Metacontroller.

**C1:** parent selectors and controller ownership govern adoption and orphaning; omitted desired children are deleted, rolling updates pause on failed status checks, and finalization can delay deletion until cleanup completes. These are meaningful ownership and lifecycle invariants, not merely webhook plumbing. **C2:** a CompositeController declares parent and child kinds while its webhook returns desired children and status, making the same engine usable for many higher-level APIs. **C3:** resynchronization reads from watch-maintained local caches rather than repeatedly listing through the API server. The [CompositeController specification](https://metacontroller.github.io/metacontroller/api/compositecontroller.html) is both an API entry point and a detailed explanation of the engine's semantics. Do not count the original GKE repository as an additional implementation.

### 11. [flant/shell-operator](https://github.com/flant/shell-operator)

**Language / role:** Go runtime; event-driven operator hooks written in shell, Python, or other executable languages.

The interesting code is the execution engine around scripts. **C1:** hooks execute sequentially within each named queue; a failing hook is retried and blocks later work in that queue unless failure is explicitly allowed. Startup synchronization and named-queue options expose ordering decisions to the author. **C2:** Kubernetes watches, schedules, startup hooks, and resource snapshots form a reusable automation model. **C3:** adjacent executions can be combined, jq-based projections suppress irrelevant modified events, and retaining only projected data reduces the memory used for snapshots. The [hooks and execution lifecycle documentation](https://flant.github.io/shell-operator/HOOKS.html) makes the tradeoffs observable, including the risk of queue blockage behind a persistently failing hook.

### 12. [knative/pkg](https://github.com/knative/pkg)

**Language / role:** Go; shared controller infrastructure used across Knative. Focus on the controller and reconciler support, rather than the repository's unrelated utility packages.

**C1:** the controller runtime integrates leader election, waits for running work during shutdown, and offers explicit finalizer field-management options to manage conflicts among controllers. **C2:** a shared controller implementation drives a small reconciler interface, with configurable event handling, status behavior, and concurrency. **C3:** global and filtered resynchronization enter a slow queue, distinct from ordinary work; worker counts and rate-limiting queues expose control over bursts and background reprocessing. The [controller package documentation](https://pkg.go.dev/knative.dev/pkg/controller) connects these interfaces to their source files. This is a useful comparison with controller-runtime because it shows another substantial framework's choices about resync traffic, lifecycle, and generated reconciliation support.

### 13. [coryodaniel/bonny](https://github.com/coryodaniel/bonny)

**Language / role:** Elixir; framework for Kubernetes operators, controllers, and custom schedulers.

**C2:** controllers are composable processing steps operating on a `Bonny.Axn` value; they register descendants, status changes, and events, with application of those changes separated into later pipeline stages. **C3:** the observed-generation step compares `metadata.generation` with stored observed generation and halts redundant add/modify processing, reducing work caused by status updates while retaining periodic reconciliation for missed events and drift. The [controller guide](https://hexdocs.pm/bonny/controllers.html) explains both the pipeline and the suppression mechanism.

This is a useful smaller-language-community counterpoint to Go runtimes, but its capabilities should not be generalized beyond their documented maturity: the inspected [leader-election documentation](https://hexdocs.pm/bonny/Bonny.Operator.LeaderElector.html) marks that feature as still under testing and for testing use only. No production availability claim is inferred from the presence of a Kubernetes Lease implementation.

## Resource composition and continuous delivery reconciliation

### 14. [crossplane/crossplane](https://github.com/crossplane/crossplane)

**Language / role:** Go; extensible control-plane and resource composition framework. Focus on composite-resource reconciliation and composition functions.

**C1:** every function in a pipeline receives the same initially observed state, while desired state accumulates between functions. Failing to carry a previously desired resource forward can delete it; field ownership and server-side apply therefore have consequential correctness semantics. **C2:** custom composite APIs and reusable function pipelines let platform authors assemble applications and infrastructure without writing a bespoke controller for every abstraction. The [composition documentation](https://docs.crossplane.io/latest/composition/compositions/) explains both the extension model and the observed/desired-state contract. Study this when designing declarative APIs with programmable composition, especially the boundary between rendering desired resources and applying them. The broader infrastructure-provider ecosystem is outside this entry's scope.

### 15. [kubernetes-sigs/kro](https://github.com/kubernetes-sigs/kro)

**Language / role:** Go; Kube Resource Orchestrator. The former `kro-run/kro` location now resolves to this Kubernetes SIG repository.

**C1:** ResourceGraphDefinition reconciliation validates CEL syntax, field references, types, and cycles before instantiating resources. It builds a dependency graph from expression references and checks nested structural compatibility against Kubernetes OpenAPI schemas. **C2:** schema definitions, templates, expressions, and inferred dependencies provide a reusable way to define higher-level APIs spanning existing Kubernetes kinds. The versioned [static-analysis documentation](https://kro.run/0.8.0/docs/concepts/rgd/static-type-checking/) is an unusually concrete entry point into graph compilation and validation.

The [main-branch readiness documentation](https://kro.run/next/docs/concepts/reconciliation/readiness/) is also instructive, but describes development semantics: it distinguishes ResourceGraphDefinition dependency gating from the newer Graph model's readiness reporting. Treat those APIs as version-specific; this entry does not award C4 or imply long-term API stability.

### 16. [argoproj/argo-cd](https://github.com/argoproj/argo-cd)

**Language / role:** Go, with a TypeScript web interface; Kubernetes application reconciliation from Git. Relevant monorepo subsystem: the application controller and its synchronization engine.

**C1:** synchronization phases gate later actions on hook success and resource health; pruning reverses wave order and stops when deletion fails, protecting dependency ordering. Selective sync has different hook semantics, which is an important boundary to study. **C2:** the application abstraction can reconcile different manifest-generation systems through a repository server separated from the API server and application controller. These responsibilities are laid out in the [architecture overview](https://argo-cd.readthedocs.io/en/stable/operator-manual/architecture/). The [sync phases and waves guide](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/) is the better entry point for understanding actual orchestration invariants. The UI is not the reason for inclusion.

### 17. [fluxcd/kustomize-controller](https://github.com/fluxcd/kustomize-controller)

**Language / role:** Go; the Flux controller that builds and continuously reconciles Kubernetes resource sets. This is the implementation repository, rather than the Flux installation/CLI umbrella.

**C1:** the controller tracks successfully applied objects in an inventory used for garbage collection and drift handling; dependency readiness, failed health checks, retry behavior, and deletion policy affect convergence. Circular dependencies can prevent progress and are explicitly documented. **C2:** Kustomization resources connect independently produced source artifacts to arbitrary Kubernetes resources, with configurable patches, health checks, dependency conditions, and service-account impersonation. The [Kustomization API and behavior guide](https://fluxcd.io/flux/components/kustomize/kustomizations/) provides the main entry point. Study the distinction between a declarative resource set, its last successful inventory, and the live objects; it is much richer than periodically running a manifest build command.

## Multicluster and edge control planes

### 18. [karmada-io/karmada](https://github.com/karmada-io/karmada)

**Language / role:** Go; multicluster workload placement and propagation.

**C1:** application-level failover distinguishes application health from cluster reachability, propagates dependencies, and supports delayed removal of the old application until the replacement is healthy or a grace period expires. This makes the availability-versus-duplicate-execution tradeoff explicit. **C2:** propagation policies are reusable across workloads, while override policies specialize configuration for particular clusters. The controller chain separates policy selection, resource binding, and Work execution, as described in the repository architecture.

Start with [propagation and override concepts](https://karmada.io/docs/core-concepts/concepts/), followed by [application failover](https://karmada.io/docs/userguide/failover/application-failover/). The Resource Interpreter Framework is particularly worth studying: generic multicluster machinery needs resource-specific definitions of health rather than assuming every workload behaves like a Deployment.

### 19. [open-cluster-management-io/ocm](https://github.com/open-cluster-management-io/ocm)

**Language / role:** Go; Open Cluster Management core components, including registration, placement, and work distribution.

**C1:** cluster registration requires consent on both sides, uses separate authorization boundaries, and manages certificate and registration lifecycle. Managed-cluster agents continue their local management role during hub disconnection rather than requiring each operation to originate synchronously from the hub. **C2:** PlacementDecision separates cluster selection from consumers that execute the resulting placement, while ManifestWork describes resources to distribute. **C3:** managed-cluster agents pull and execute work locally, moving execution and event-handling pressure away from the central hub. The [architecture document](https://open-cluster-management.io/docs/concepts/architecture/) explains these divisions. Read the core repository as one implementation; its surrounding addon ecosystem is not counted as extra entries here.

### 20. [liqotech/liqo](https://github.com/liqotech/liqo)

**Language / role:** Go; Kubernetes multicluster offloading through virtual nodes and resource reflection.

**C1:** remote ShadowPod resources let a controller in the provider cluster enforce desired pod presence during temporary loss of connectivity to the originating cluster. Status, endpoint addresses, and other resource details must be remapped between clusters. **C2:** a remote resource allocation appears as a local virtual node, allowing existing scheduling policies to work across clusters; reflection supports workload configuration, service exposure, and storage resources. The [offloading architecture](https://docs.liqo.io/en/latest/features/offloading.html) explains negotiated capacity, virtual kubelets, twin namespaces, and remote enforcement. This is a distinct architectural family from a central placement controller: it adapts Kubernetes' node abstraction to another cluster while preserving enough local autonomy for failures.

### 21. [kubeedge/kubeedge](https://github.com/kubeedge/kubeedge)

**Language / role:** Go; cloud-and-edge container orchestration and device-management framework. Relevant subsystems are CloudHub/EdgeHub, Edged, and MetaManager.

**C1:** the design must retain usable application metadata while cloud connectivity is absent or intermittent. MetaManager persists metadata in SQLite, tracks connection state for remote queries, and synchronizes pod status back toward the cloud. **C2:** cloud controllers, edge execution, message transport, metadata storage, and device interaction are separated into reusable modules. **C3:** updates are checked for a local delta before being stored and forwarded, and status synchronization is configurable; these are concrete mechanisms for limiting work across constrained links and devices. The repository's architecture overview supplies the module map, and the versioned [MetaManager documentation](https://release-1-19.docs.kubeedge.io/docs/architecture/edge/metamanager/) supplies the message and persistence details. Configuration names in that document belong to its documented release.

## Workload scheduling and lifecycle extensions

### 22. [openkruise/kruise](https://github.com/openkruise/kruise)

**Language / role:** Go; Kubernetes workload controllers, including CloneSet, Advanced StatefulSet, Advanced DaemonSet, and SidecarSet.

**C1:** in-place updates must distinguish supported field changes from changes requiring recreation, preserve lifecycle ordering, and observe completion of one container batch before advancing to another. Lifecycle hooks can mark Pods unready before update or deletion and wait for another controller's cleanup. **C2:** multiple advanced workloads reuse the in-place update implementation while exposing different workload-level policies. **C3:** retaining the Pod while updating eligible containers avoids replacing the entire Pod and disturbing unrelated running containers. Read the [in-place update mechanics](https://openkruise.io/docs/core-concepts/inplace-update) and [CloneSet lifecycle semantics](https://openkruise.io/docs/user-manuals/cloneset). The docs explicitly distinguish SidecarSet's behavior, so a guarantee for one workload must not be assumed for all of them.

### 23. [volcano-sh/volcano](https://github.com/volcano-sh/volcano)

**Language / role:** Go; batch-oriented Kubernetes scheduler and workload control system.

**C1:** gang scheduling reasons about the minimum viable group of tasks rather than admitting arbitrary individual Pods; preemption, reclamation, and queue policy must interact without undermining that group requirement. **C2:** scheduling sessions invoke ordered actions whose algorithmic behavior is supplied by plugins, supporting policies such as priority, dominant-resource fairness, predicates, and bin packing. **C3:** caching, session-based scheduling, and backfilling expose the tradeoff between policy, placement work, and unused capacity. The [scheduler architecture](https://volcano.sh/docs/scheduler/overview/) connects those mechanisms. Its warning that action order is configurable but not automatically checked is a useful correctness boundary. This is especially valuable for studying distributed training and other workloads that need coordinated admission.

### 24. [kubernetes-sigs/kueue](https://github.com/kubernetes-sigs/kueue)

**Language / role:** Go; Kubernetes job queueing and admission framework, complementary to pod placement.

**C1:** admission combines nominal quota, borrowing and lending limits, resource flavors, cohort membership, and preemption policy. The semantics constrain both which resources can be borrowed and whether a workload's resource requests fit; they are more subtle than a single counter. **C2:** ClusterQueues, cohorts, ResourceFlavors, and workload integrations separate organizational allocation policy from particular job implementations. **C3:** the distinction between strict FIFO and best-effort FIFO makes head-of-line blocking versus utilization a deliberate policy choice. The [ClusterQueue specification](https://kueue.sigs.k8s.io/docs/concepts/cluster_queue/) provides detailed examples and inequalities, making it a strong entry point for studying resource-accounting invariants. Kueue should not be mistaken for a replacement for every kube-scheduler placement function.

### 25. [kubernetes-sigs/cluster-api](https://github.com/kubernetes-sigs/cluster-api)

**Language / role:** Go; declarative Kubernetes cluster and machine lifecycle framework. Focus on the core Machine controller and provider contracts.

**C1:** a Machine coordinates infrastructure provisioning, bootstrap readiness, and association with an actual Kubernetes Node through provider identity. Deletion includes draining and waiting for storage detachment rather than simply removing the desired-state object. **C2:** separate InfraMachine and BootstrapConfig contracts let infrastructure and bootstrap providers participate in a shared lifecycle without implementing the whole controller. The [Machine controller documentation](https://cluster-api.sigs.k8s.io/developer/core/controllers/machine) explains ownership, status propagation, readiness, and cleanup responsibilities. This is useful for engineers studying reconcilers that span multiple APIs and long-running external operations. It orchestrates the infrastructure on which containers run, so its fit is the reconciliation-framework half of this category.

## Search coverage, exclusions, and limits

Discovery used more than six distinct live search formulations, followed by opening canonical repositories and technical primary material for every retained project. Search angles included:

- Complete container schedulers and reconciliation architecture: Kubernetes, Nomad, SwarmKit, and the Mesos family.
- Operator runtime design across Rust, Python, Java, .NET, Elixir, JavaScript/TypeScript, and Scala communities.
- Language-independent webhook and executable-hook controllers, plus shared controller packages.
- Declarative composition, expression analysis, inferred dependency graphs, and continuous GitOps reconciliation.
- Multicluster placement, pull-based work distribution, virtual-kubelet offloading, and disconnected edge operation.
- Batch gang scheduling, quota admission, fairness, in-place workload updates, and infrastructure lifecycle contracts.
- Retirement, repository moves, compatibility policies, and changelog evidence, followed by alternative-language and historical-framework searches to test whether the selection was overly familiar.

Later searches increasingly returned the same architectural families, narrow integrations, or less well-supported candidates. Bonny was retained from the alternative-language pass because its controller pipeline and generation filtering supplied substantive additional material. Small TypeScript and Scala frameworks were discovered but not researched to the same evidentiary depth and are not implicitly judged low quality. This is a bounded selection, not an exhaustive ecosystem inventory.

Kubebuilder and Operator SDK scaffolding were not counted separately from their shared Go runtime merely to inflate coverage. Kubernetes' published staging libraries were likewise not treated as independent copies of the main monorepo. Generic container runtimes, networking/storage plugins, Helm-style packaging alone, single-application operators, tutorial operators, and general workflow engines were outside the selected scope. Crossplane and Cluster API remain deliberate boundary inclusions because their reusable reconciliation machinery is central to their implementation.

Historical breadth is represented by Mesos without separately expanding the report into all of its schedulers. [Marathon's repository](https://github.com/d2iq-archive/marathon) was checked and is explicitly archived; the [Apache Aurora repository](https://github.com/apache/aurora) was also inspected during this historical search. Neither is an additional retained entry. Repository moves for KubeOps and kro were followed; Kopf and Metacontroller continuations are each counted only once.

All retained entries have an opened GitHub repository page and at least one additional opened primary technical source. Some GitHub pages exposed only partial rendered content, so official API references and project documentation supplied implementation contracts where needed. No candidate was cloned, installed, or executed, and no benchmark or comprehensive correctness audit was performed. Statements about study value and criterion fit are engineering judgments grounded in the cited mechanisms. Documentation under `latest`, `stable`, or a moving branch may change; explicitly versioned and development documentation is identified where material. Except where a status is specifically discussed, inclusion does not certify a current maintenance cadence or deployment support commitment.
