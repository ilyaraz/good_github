# Continuous integration servers and execution runners

Research date: **2026-10-09**.

This selection covers 24 GitHub repositories implementing CI control planes, pipeline execution engines, build-farm schedulers, worker agents, and runner fleet controllers. It includes complete services and substantial execution components of hosted services. General deployment tools, build tools without a CI execution service, workflow examples, and thin runner packaging are outside the scope. The purpose is to identify concrete engineering material to study, not to rank products or certify every component's quality.

Canonical repository URLs, default branches, and archive flags were checked through the GitHub API. Each entry also uses an opened implementation file or substantive primary architectural document. None of the retained repositories was marked archived at inspection; this does not establish a maintenance commitment. Links to default branches describe the inspected snapshot and can change. Explicitly dated design documents are architectural evidence, not promises that every historical detail remains current.

## Criteria legend

- **C1 — Correctness:** demanding invariants, concurrency, adversarial inputs, or failure recovery.
- **C2 — Abstractions:** substantial reusable interfaces or models supporting different workflows and environments.
- **C3 — Performance:** identifiable throughput, latency, capacity, or resource constraints addressed by understandable architecture; no benchmark claims are implied.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, migrations, or deliberate complexity management. Age and stars alone do not qualify.

## CI servers and pipeline control planes

### [jenkinsci/jenkins](https://github.com/jenkinsci/jenkins)

**Java · Extensible CI automation controller.** Study the core scheduler and the cost of evolving a controller with independently deployed agents and plugins. This entry concerns Jenkins core; it does not count the separately maintained Pipeline plugin repositories as part of this repository.

- **C1:** The queue distinguishes waiting, blocked, buildable, pending, and departed items. Its implementation explains the particularly difficult handoff race: an assigned node can disappear before an executable is instantiated, allowing requeueing, whereas disappearance after instantiation requires a different failure path. Cancellation can occur at any queue stage. Start with [Queue.java](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/hudson/model/Queue.java).
- **C4:** The [2016 Jenkins 2.0 release account](https://www.jenkins.io/blog/2016/04/26/jenkins-20-is-here/) explains evolutionary migration of existing installations. The later [2.479 LTS upgrade guide](https://www.jenkins.io/doc/upgrade-guide/2.479/) documents coordinated Java, Spring/Jakarta, plugin, and Remoting transitions. Together these show sustained compatibility management, including explicit breaking boundaries, rather than merely an old project.

### [buildbot/buildbot](https://github.com/buildbot/buildbot)

**Python, with JavaScript UI components · Programmable CI framework and workers.** The monorepo contains the master, worker, and web components. It is particularly useful for studying distributed scheduling implemented with Twisted services and a relational database.

- **C1:** Masters transactionally claim build requests so only one succeeds. A disappeared worker can cause a claim to be released; periodic database polling recovers requests missed through failures or message/database races. The [build-request claiming design](https://github.com/buildbot/buildbot/blob/master/master/docs/developer/br-claiming.rst) explains both the normal path and its recovery mechanism.
- **C2:** A dynamically reconfigurable service tree separates change sources, schedulers, builders, worker protocols, caches, and database access. The [master organization guide](https://github.com/buildbot/buildbot/blob/master/master/docs/developer/master-overview.rst) maps these abstractions to actual objects, making it a useful entry point for custom CI systems rather than only fixed pipeline execution.

### [gocd/gocd](https://github.com/gocd/gocd)

**Java and TypeScript · CI/CD server with dependent pipelines and agents.** Study how a build system tracks provenance across independently executing component pipelines. GoCD's distinction is its dependency/material model, not simply a sequential list of commands.

- **C1:** Fan-in resolution prevents a downstream packaging or deployment pipeline from combining incompatible ancestor revisions when upstream pipelines finish at different times. The [fan-in documentation](https://docs.gocd.org/current/advanced_usage/fan_in.html) walks through the resolution and explicitly limits it to applicable automatic triggers; material filters can defeat the expected behavior.
- **C2:** The same model represents parallel validation gates, independently built components, and matching an artifact to the exact tests for its source revision. These worked cases in the fan-in guide demonstrate reusable dependency semantics across several CI topologies. Begin with those examples before tracing the server/agent implementation.

### [concourse/concourse](https://github.com/concourse/concourse)

**Go · Container-based pipeline server and workers.** A strong study target for version-driven scheduling: jobs consume resource versions, and the controller must decide which combinations justify a new build.

- **C1:** The scheduler resolves pinned versions, disabled versions, and upstream `passed` constraints. It also avoids duplicate automatic builds for already consumed triggering versions and coordinates scheduler activity across ATC nodes. The [build scheduler internals](https://concourse-ci.org/docs/internals/scheduler/) describe these invariants and unsuccessful resolution.
- **C3:** Scheduling runs periodically but only recomputes jobs affected by relevant events, including resource discovery, upstream completion, configuration changes, and pinning. That is a concrete reduction of unnecessary scheduling work, with a clear separation between version selection and build tracking. The same document is the main reading entry point; [the ATC source tree](https://github.com/concourse/concourse/tree/master/atc) separates scheduler, engine, execution, database, and garbage-collection modules.

### [woodpecker-ci/woodpecker](https://github.com/woodpecker-ci/woodpecker)

**Go and TypeScript · CI server, agents, CLI, and pipeline runtime.** Study a server/agent engine whose pipeline parsing and execution are separated from forge integrations and backend-specific execution. Its substantial current runtime and independently organized server/agent code justify treating it as a separate project from the Drone runner below.

- **C1:** The [workflow runtime](https://github.com/woodpecker-ci/woodpecker/blob/main/pipeline/runtime/workflow.go) requires cleanup to outlive workflow cancellation, uses a once-only destruction function, waits for running steps, and distinguishes a failed user step from an infrastructure/runtime failure. Normal completion also waits for log and trace uploads.
- **C2:** The [versioned architecture guide](https://woodpecker-ci.org/docs/3.18/development/architecture) maps the shared pipeline engine, RPC boundary, server, agent, and CLI into dependency layers. Read that older architecture map alongside current runtime code; it is not a statement that 3.18 is the current supported release.

### [agola-io/agola](https://github.com/agola-io/agola)

**Go · Distributed CI/CD service with Docker and Kubernetes executors.** Particularly instructive for the tension between availability and avoiding duplicate execution. The API snapshot showed a latest push on 2025-09-24, so this is included for its architecture without claiming current active maintenance.

- **C1:** The [run-service design](https://agola.io/doc/architecture/runservice) deliberately treats executors as authoritative for task state. A disconnected executor's task is not simply declared finished and duplicated elsewhere. Change-group update tokens provide optimistic concurrency control so concurrent schedulers cannot both admit work beyond a configured limit. These are documented intended semantics, not a proof of exactly-once execution.
- **C2:** The run service models task dependencies without knowing higher-level projects, users, or commits. Docker and Kubernetes drivers share that execution model while using different executor-lifetime and stale-task cleanup policies. The same design document is a compact entry point into both the reusable boundary and its consequences.

### [go-vela/server](https://github.com/go-vela/server)

**Go · Vela's server/API and pipeline compiler.** This is the control-plane repository, not Vela's separate worker repository. Study how repository events and reusable pipeline definitions become execution plans.

- **C1:** The [native compiler](https://github.com/go-vela/server/blob/main/compiler/native/compile.go) validates SCM token/netrc requests before proceeding and validates YAML after inline template rendering. Rule inputs distinguish branch, event action, path, sender, target, and other build context, making expansion and authorization boundaries visible.
- **C2:** The compiler separates parsing, template expansion, rule evaluation, substitution, and stage/step compilation; `CompileLite` exposes partial compilation as well. This supports multiple configuration and preview/execution uses. The [local architecture documentation](https://github.com/go-vela/server/blob/main/DOCS.md) explains how the server manages resource state and translates webhooks into builds for the worker.

### [ovh/cds](https://github.com/ovh/cds)

**Go and TypeScript · Distributed CI/CD platform, workers, and provisioning services.** Relevant monorepo components include the API, worker binary, log/artifact services, and hatcheries. Study separation of job execution, control-plane traffic, and worker provisioning in a multi-team installation.

- **C2:** Hatcheries implement different worker-provisioning environments, including local processes, containers, and virtual machines, behind the platform's worker model. The [service architecture](https://ovh.github.io/cds/hosting/cds_services/) maps these components and identifies their shared PostgreSQL/Redis dependencies.
- **C3:** The [design principles](https://ovh.github.io/cds/about/) explain stateless API replication and independent API replacement while jobs run. The service guide further separates log/artifact traffic into a CDN service and describes Redis coordination for replicated hooks/VCS services. It also identifies a non-replicable repository service in that documented architecture, a useful reminder that scaling properties differ by subsystem.

### [screwdriver-cd/screwdriver](https://github.com/screwdriver-cd/screwdriver)

**JavaScript/Node.js · CI build-platform API and orchestration server.** This repository is the API/control-plane implementation; other repositories supply parts of the executor and data ecosystem. Study how pipeline, event, job, build, template, and authorization models meet at API boundaries.

- **C1:** The [build-update handler](https://github.com/screwdriver-cd/screwdriver/blob/master/plugins/builds/update.js) restricts transitions according to current build status, limits which terminal states users and administrators may request, binds build credentials to the corresponding build, and rejects a repeated RUNNING update. These are concrete state-machine and authorization concerns; the checks alone should not be mistaken for a proof against every concurrent race.
- **C2:** [Server construction](https://github.com/screwdriver-cd/screwdriver/blob/master/lib/server.js) injects factories for pipelines, jobs, events, builds, stages, templates, tokens, and build clusters into a plugin-based Hapi service. This exposes a reusable domain/service boundary across different execution and SCM integrations.

## Kubernetes-native pipelines, large CI systems, and fleet control

### [tektoncd/pipeline](https://github.com/tektoncd/pipeline)

**Go · Kubernetes-native CI pipeline controller and execution machinery.** This entry concerns Tekton Pipelines, not the whole collection of Tekton projects. Study how declarative CI objects become correctly ordered container execution.

- **C1:** The [container contract](https://github.com/tektoncd/pipeline/blob/main/docs/container-contract.md) explains why step entrypoints are replaced with a coordination binary: containers in one pod must execute in task order. Resolving an omitted command also requires registry entrypoint lookup and credential selection, rather than blindly using the image as supplied.
- **C2:** [Tasks](https://github.com/tektoncd/pipeline/blob/main/docs/tasks.md) expose parameters, ordered steps, workspaces, results, volumes, and sidecars. These are reusable execution interfaces rather than application-specific scripts; the documentation also distinguishes namespaced tasks from cluster-wide task resolution and records deprecated ClusterTasks.

### [taskcluster/taskcluster](https://github.com/taskcluster/taskcluster)

**JavaScript/TypeScript, Go, SQL, and other components · Distributed CI services and workers.** The monorepo is counted once. The most useful initial subsystem is `services/queue`, which coordinates task execution and dependencies.

- **C1:** The [queue internals](https://github.com/taskcluster/taskcluster/blob/main/services/queue/README.md) explain atomic database updates that change a run to pending and place it in the claimable queue. Thus a subsequent messaging failure need not leave an unclaimable pending task. Claims expire, workers reclaim long-running tasks, and deadline/dependency processing handles unresolved work.
- **C2:** Separate pending, claim, deadline, and resolution queues encode reusable task/run lifecycle machinery. The documented APIs separate worker claiming and result reporting from dependency resolution, enabling different workers to participate without embedding their execution mechanism in the queue service. The [queue source tree](https://github.com/taskcluster/taskcluster/tree/main/services/queue/src) is the implementation entry after the lifecycle diagrams.

### [kubernetes-sigs/prow](https://github.com/kubernetes-sigs/prow)

**Go · Kubernetes-based CI/CD and repository-event automation.** This is the current dedicated Prow repository, rather than counting its earlier location in `kubernetes/test-infra` separately. Focus on the CI job path, not merely its comment bots.

- **C1:** The [life of a Prow job](https://github.com/kubernetes-sigs/prow/blob/main/site/content/en/docs/life-of-a-prow-job.md) traces permission-sensitive triggering: the trigger plugin checks whether a contributor is trusted or the pull request is explicitly permitted to run tests. Execution, status reporting, and eventual deletion belong to separate components, exposing failure and reconciliation boundaries.
- **C2:** A `ProwJob` resource separates event-triggering plugins from Kubernetes execution, external reporting through crier, and cleanup through sinker. The walkthrough connects these pieces to source locations and shows how one job abstraction supports presubmit workflows. Some explanatory links retain a historical reference snapshot; the document identifies that limitation explicitly.

### [actions/actions-runner-controller](https://github.com/actions/actions-runner-controller)

**Go · Kubernetes operator for GitHub Actions runner fleets.** This is fleet lifecycle and scaling infrastructure, distinct from the `actions/runner` job-execution agent. Study how eventual consistency at an external service affects Kubernetes reconciliation.

- **C1:** The [runner unregistration implementation](https://github.com/actions/actions-runner-controller/blob/master/controllers/actions.github.com/runner_unregistration.go) distinguishes clean self-deregistration from runners killed or lost before cleanup. Requests are deduplicated using namespace, object name, and runner ID; still-running jobs get delayed retries. Its comments explicitly explain why restart loss of the in-memory queue delays cleanup rather than providing durable delivery.
- **C3:** External deregistration runs in a worker pool outside the ephemeral-runner reconcile loop, so slow service calls do not block local pod cleanup. The ready queue advances a head index to avoid quadratic shifting during deletion bursts. The [controller source tree](https://github.com/actions/actions-runner-controller/tree/master/controllers/actions.github.com) also exposes focused cleanup, stale-state, and reconciliation tests.

## Small servers and specialized build farms

### [ohwgiles/laminar](https://github.com/ohwgiles/laminar)

**C++ · Lightweight, script-driven CI service.** A useful smaller codebase for following an entire job from RPC request through process execution to completion. Its shell-oriented model keeps workflow policy outside a large configuration language.

- **C1:** [Run execution](https://github.com/ohwgiles/laminar/blob/master/src/run.cpp) manages a leader process, output pipes, asynchronous completion, abnormal termination, and process-group cancellation. The implementation converts wait status into a run result and resolves start/finish promises for callers.
- **C2:** The [user manual](https://github.com/ohwgiles/laminar/blob/master/UserManual.md) shows dynamic job chains, parallel downstream jobs, parameterized runs, and before/after hooks using the same `laminarc` interface. Parent job/run identifiers preserve dependency traceability. This makes shell composition a reusable CI abstraction rather than simply invoking one hard-coded script.

### [NixOS/hydra](https://github.com/NixOS/hydra)

**Rust, Perl, SQL, and Nix · Nix-based continuous build service.** The inspected source snapshot places Rust queue-runner, evaluator, and builder components beside the Perl web application. Use the current `subprojects/` layout; relying on older descriptions of Hydra's implementation would be misleading.

- **C2:** The [architecture manual](https://github.com/NixOS/hydra/blob/master/subprojects/hydra-manual/src/architecture.md) separates jobset evaluation, derivation scheduling, remote building, notifications, and UI/API responsibilities. Shared crates expose database access, store transfer, binary-cache operations, and build-log following. One top-level CI build can expand into many derivation steps.
- **C3:** Builder machines use independent Nix stores and connect to the queue runner over gRPC. Outputs can go to a separate destination binary cache, and build steps can reuse Nix-store results. The architecture makes the boundaries between scheduling, transfer, cache storage, and live log streaming explicit. Follow it into the [queue-runner source](https://github.com/NixOS/hydra/tree/master/subprojects/hydra-queue-runner/src).

### [ocurrent/ocluster](https://github.com/ocurrent/ocluster)

**OCaml · CI build scheduler and worker pools over Cap'n Proto.** A relatively compact distributed execution service, supporting Dockerfile and OBuilder jobs. It is particularly useful for studying cache locality and fairness together.

- **C1:** The [pool interface](https://github.com/ocurrent/ocluster/blob/master/scheduler/pool.mli) makes worker capacity, duplicate registration, cancellation, pause reasons, shutdown, and disconnection explicit. Deactivating a worker returns queued work to the main queue; a released worker handle cannot be reused. These documented invariants give a precise reading map for the implementation.
- **C3:** The [scheduler documentation](https://github.com/ocurrent/ocluster/blob/master/README.md) describes cache hints that prefer a previously used worker, while client rates assign fair start times so a large submitted batch need not starve another client. Spare capacity remains usable. This is a concrete locality-versus-fairness scheduling problem, without requiring speculative throughput claims.

### [ocurrent/ocaml-ci](https://github.com/ocurrent/ocaml-ci)

**OCaml · Metadata-driven CI service for OCaml projects.** This is the higher-level CI service, separately implemented from OCluster's general worker-pool scheduler. Study automatic build-matrix construction and incremental recomputation instead of requiring every project to author its own CI script.

- **C2:** The [service pipeline](https://github.com/ocurrent/ocaml-ci/blob/master/service/pipeline.ml) composes repository installations, branches/PRs, variants, and GitHub check reporting through OCurrent values. It models active, skipped, experimental-failure, and completed outcomes, keeping ecosystem-specific policy above generic execution.
- **C3:** The [repository's architectural overview](https://github.com/ocurrent/ocaml-ci/blob/master/README.md) explains dependency-sensitive Docker layering: opam metadata and dependency installation precede the remaining source files, permitting reuse when only application source changes. The service infers builds from opam/dune metadata across compiler and OS variants, giving this caching structure a substantial CI workload.

## Execution agents and local workflow runtimes

### [actions/runner](https://github.com/actions/runner)

**C# · GitHub Actions execution agent.** Study execution semantics at the boundary between workflow steps, reusable actions, and host processes. This repository is the runner, not GitHub's hosted scheduling service.

- **C1:** The accepted [composite-actions design](https://github.com/actions/runner/blob/main/docs/adrs/1144-composite-actions.md) specifies recursion limits, nested pre/post ordering, and per-action state isolation. It explains why post steps must not accidentally share another action's state and why action-download policy checks matter. Its historical rollout limitations should not be treated as a current feature matrix.
- **C2:** The same design gives composite actions an input/output interface and makes JavaScript, container, and nested composite actions behave as one workflow step. This is substantial reusable execution machinery, with explicitly hidden internal structure and carefully controlled context propagation. The [ADR collection](https://github.com/actions/runner/tree/main/docs/adrs) offers further entry points for shell, environment, hook, and result semantics.

### [microsoft/azure-pipelines-agent](https://github.com/microsoft/azure-pipelines-agent)

**C# · Cross-platform Azure Pipelines execution agent.** Study how a task definition becomes a platform-specific handler while preserving shared conditions, stages, execution context, and cleanup behavior.

- **C1:** The [job-cancellation design](https://github.com/microsoft/azure-pipelines-agent/blob/master/docs/design/jobcancellation.md) describes cancellation from the server and signal escalation when a child process does not stop. This is a concrete failure boundary between a control-plane cancellation and actual termination of user work.
- **C2:** [TaskRunner](https://github.com/microsoft/azure-pipelines-agent/blob/master/src/Agent.Worker/TaskRunner.cs) implements a common step/service interface, loads task definitions, selects pre/main/post execution data, verifies tasks, and chooses handlers for the host platform. Conditions, timeouts, continue-on-error, and execution targets belong to shared task semantics rather than each task implementation.

### [buildkite/agent](https://github.com/buildkite/agent)

**Go · Self-hosted execution agent for Buildkite's hosted control plane.** The repository implements polling, job execution, status/log reporting, and artifact operations. A particularly clear subsystem to study is concurrent log streaming under process and network lifecycle constraints.

- **C1:** The [log streamer](https://github.com/buildkite/agent/blob/main/agent/log_streamer.go) serializes chunk creation, assigns sequence numbers and byte offsets, rejects processing after stop, and coordinates channel closure with worker shutdown. Cancellation participates in queue submission, while upload failures are tracked separately.
- **C3:** Chunking and a configurable upload-worker pool decouple job output production from network requests through a bounded channel. The implementation exposes the relevant synchronization and backpressure rather than hiding them behind a large framework. The [agent source tree](https://github.com/buildkite/agent/tree/main/agent) contains the adjacent heartbeat, watchdog, job-runner, and focused log-streaming tests.

### [gitlabhq/gitlab-runner](https://github.com/gitlabhq/gitlab-runner)

**Go · Official GitHub mirror of GitLab Runner.** Development and issue tracking are upstream on GitLab, as the [mirror metadata](https://api.github.com/repos/gitlabhq/gitlab-runner) identifies. The GitHub tree is substantive, but its snapshot can lag upstream; the inspected changelog begins with v19.3.1, not a claim about the latest available release.

- **C1:** The [executor-interface design](https://github.com/gitlabhq/gitlab-runner/blob/main/docs/development/internal/engineering/executor_interface/_index.md) distinguishes reserving provider capacity from creating an executor and from preparing, running, finishing, and cleaning a job environment. Separating these lifetimes exposes resource-leak and partial-failure problems. The [changelog](https://github.com/gitlabhq/gitlab-runner/blob/main/CHANGELOG.md) supplies concrete corroboration, including leaked setup connections and atomic Kubernetes stage-script writes.
- **C2:** `Executor` and `ExecutorProvider` accommodate host shells, remote machines, containers, and custom execution mechanisms, while shared executor behavior centralizes trace/metrics integration. The design is explicitly dated 2022-01-26, so use it as an interface reading guide and check the current code for exact signatures.

### [drone-runners/drone-runner-docker](https://github.com/drone-runners/drone-runner-docker)

**Go · Docker execution runner for Drone.** This is a substantial compiler/runtime implementation, not a container image wrapper. It is **source-available** under the repository's [Polyform license alternatives](https://github.com/drone-runners/drone-runner-docker/blob/master/LICENSE.md); inclusion is about inspectable engineering, not unrestricted licensing. No active-maintenance claim is made from its January 2026 push alone.

- **C1:** The [Docker engine](https://github.com/drone-runners/drone-runner-docker/blob/master/engine/engine.go) creates shared volumes and networks, bounds internal setup work, and tears down containers, volumes, and networking. It deliberately logs and ignores cleanup failures, documenting the need for later administrative pruning. This is a useful failure-policy tradeoff to inspect, not an assertion of leak-free cleanup.
- **C2:** The [compiler](https://github.com/drone-runners/drone-runner-docker/blob/master/engine/compiler/compiler.go) translates YAML into an execution-oriented intermediate representation and accepts environment, secret, registry, workspace, network, privilege, and resource providers/settings. The separation makes configuration expansion and Docker lifecycle independently understandable.

### [nektos/act](https://github.com/nektos/act)

**Go · Local execution engine for GitHub Actions workflows.** Study the machinery needed to turn a remote CI configuration language into a local execution plan. Compatibility should be assessed per feature; this entry does not claim exact equivalence to GitHub's hosted service.

- **C2:** The [runner implementation](https://github.com/nektos/act/blob/master/pkg/runner/runner.go) converts planned stages, jobs, matrix variants, and per-run contexts into composable executors. Its configuration provides distinct boundaries for event data, action caches, container settings, artifacts, and platform mapping.
- **C3:** Job concurrency and matrix concurrency are controlled separately. The implementation composes sequential stage execution with bounded parallel executors and reduces matrix parallelism to the actual matrix size. The [runner directory](https://github.com/nektos/act/tree/master/pkg/runner) also exposes expression, reusable-workflow, composite-action, and job-executor implementations and tests for deeper semantic study.

### [cirruslabs/cirrus-cli](https://github.com/cirruslabs/cirrus-cli)

**Go · Local Cirrus task executor and persistent worker.** Despite its name, this repository contains an execution engine and a worker that receives cloud tasks; it is not merely an API command wrapper. It brings useful macOS/VM and hardware-attached execution cases into the selection.

- **C1:** The [executor](https://github.com/cirruslabs/cirrus-cli/blob/main/internal/executor/executor.go) manages task-status transitions, distinguishes cancellation/deadlines from ordinary failures, and cancels work when optional heartbeat monitoring detects a timeout. It also handles instances that exit before a task runs. Its ordered environment-merging logic makes precedence visible rather than leaving it to incidental map updates.
- **C2:** The [persistent-worker guide](https://github.com/cirruslabs/cirrus-cli/blob/main/PERSISTENT-WORKERS.md) documents arbitrary named resource quantities, pool labels, and configurable isolation through containers or Tart/Vetu VMs. It also makes the trust boundary explicit: unisolated execution is possible, and administrators can restrict isolation kinds, VM images, and mounts. These abstractions support both local reproduction and specialized remote workers.

## Coverage, search method, and limitations

Discovery used more than six distinct live-web query formulations, followed by GitHub API directory inspection and direct reading of primary files. The search angles included:

- Established controller/agent systems: `open source continuous integration server architecture Jenkins Buildbot GoCD GitHub`.
- Container and Kubernetes pipelines: `continuous integration server DAG container Woodpecker Concourse Tekton architecture`.
- Hosted-service execution agents: `self hosted CI runner GitHub agent execution architecture Buildkite GitLab runner`.
- Smaller independent servers: searches combining CI with Laminar, Agola, Vela, and Screwdriver.
- Large distributed installations: OVH CDS hatcheries, Taskcluster queue internals, and Prow's current repository.
- Local runners and autoscaling: searches for act, Cirrus CLI, and Actions Runner Controller.
- Language/ecosystem diversity: Nix Hydra, OCurrent/OCaml-CI, and Rust/Haskell CI-server searches.
- Lifecycle and provenance checks: GitLab's official mirror, Zuul's move to OpenDev, and Jenkins compatibility/upgrade history.

Later queries increasingly returned already covered architectures, project-specific CI configurations, and thin wrappers. The retained set spans Java, Python, Go, C#, JavaScript, C++, Rust/Perl/Nix, and OCaml, from a small Unix service to distributed task queues and Kubernetes runner fleets. Related projects are retained only where the inspected code implements a distinct layer: OCluster versus OCaml-CI, and the Actions runner versus its fleet controller. Monorepos are counted once.

**Important exclusions:** Zuul is highly relevant technically, but the opened [former GitHub repository](https://github.com/openstack-infra/zuul) is a move notice pointing to OpenDev, so it is not presented as a current substantive GitHub implementation. Proprietary CI control planes are not inferred to be public merely because their agents are. General deployment orchestrators, generic workflow tools without a sufficiently specific CI role, application repositories that merely contain CI configuration, tutorial implementations, and wrapper images were excluded. Broader forges and smaller candidates such as Strider were explored but not retained without equally strong evidence for this report; exclusion is not a quality judgment.

This was read-only source/document research. No candidate code was cloned, installed, executed, or benchmarked, and tests were not run. The descriptions distinguish observed implementation behavior from historical design intent; criterion assignments are engineering judgments grounded in the linked evidence. Documentation and live source may differ, particularly across versioned guides and mirrors. These limitations prevent claims of end-to-end correctness, current support guarantees, or uniform quality across every subsystem.
