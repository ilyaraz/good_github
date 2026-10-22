# Infrastructure provisioning and configuration management engines

Research date: **2026-10-09**.

This selection covers engines that turn infrastructure or machine configuration into ordered changes: cloud resource planners, continuous control planes, host configuration managers, declarative deployment tools, and operating-system or bare-metal provisioners. It includes both large ecosystems and smaller implementations with substantial execution semantics. Provider collections, configuration examples, inventory-only systems, and generic workflow runners are outside the scope. Each repository below was opened on GitHub and checked against additional primary implementation or architectural material.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, dependency semantics, untrusted inputs, or partial failure.
- **C2 — Abstractions:** substantial reusable interfaces or models that support different resources, environments, or deployment strategies.
- **C3 — Performance and structure:** concrete execution or resource constraints addressed through an understandable architecture; this does not imply a measured speed advantage.
- **C4 — Evolution:** evidence of development across years accompanied by compatibility, regression testing, or deliberate complexity management.

The criteria are evidence-based selection judgments, not claims that every subsystem is exemplary. Language labels describe the relevant implementation rather than every language in a repository.

## Cloud resource planning and orchestration

### [hashicorp/terraform](https://github.com/hashicorp/terraform)

**Language / role:** Go; Terraform Core, including configuration evaluation, planning, state, and graph execution. The current core is source-available under the repository's Business Source License; individual providers are separate projects.

Study how a declarative language becomes an executable dependency graph, and how an engine separates planning from applying changes to systems it does not control.

- **C1:** Separate plan and apply graph builders compose transformations for configuration, references, providers, and state. Graph traversal must preserve dependencies while synchronized state wrappers protect concurrent access. The [core architecture document](https://raw.githubusercontent.com/hashicorp/terraform/main/docs/architecture.md) explains these boundaries and their interactions.
- **C2:** Modules, provider protocols, evaluation contexts, and state managers separate resource semantics from the common engine; the same architecture is a useful map through those abstractions.
- **C4:** The [June 2021 v1.0 release](https://github.com/hashicorp/terraform/releases/tag/v1.0.0) explicitly established a compatibility baseline after earlier architectural work. The continuing [v1 compatibility policy](https://developer.hashicorp.com/terraform/language/v1-compatibility-promises) specifies protected interfaces, provider protocol support, and regression tests for previously missed feature combinations. Its guarantees have defined limits, particularly around independently maintained providers.

### [opentofu/opentofu](https://github.com/opentofu/opentofu)

**Language / role:** Go; declarative infrastructure planner and executor, forked from Terraform.

This is retained alongside Terraform because it has substantive independent development, notably configurable state and plan encryption. Much of the graph architecture remains shared ancestry, so the two entries should not be interpreted as independent inventions of that architecture.

- **C1:** Encryption changes state-loading and migration semantics: plaintext input is rejected unless an appropriate fallback is configured, and key changes require a deliberate migration path. The [encryption documentation](https://opentofu.org/docs/language/state/encryption/) also distinguishes confidentiality from replay protection and recovery after key loss.
- **C2:** Composable key providers and encryption methods extend the engine without tying every backend to one key-management service. Separately, graph transformers, evaluation contexts, and backend/state interfaces provide reusable infrastructure execution machinery, documented in the [core architecture](https://raw.githubusercontent.com/opentofu/opentofu/main/docs/architecture.md).

Study how an inherited planner can gain a new cross-cutting state feature while preserving readable boundaries between persistence, cryptography configuration, and execution.

### [pulumi/pulumi](https://github.com/pulumi/pulumi)

**Language / role:** Go engine with language SDKs; infrastructure deployment driven by ordinary programming languages. Counted once as a monorepo.

Study the boundary between a user program that registers resources and an engine that must safely execute the resulting changes.

- **C1:** The [step executor](https://raw.githubusercontent.com/pulumi/pulumi/master/pkg/resource/deploy/step_executor.go) handles cancellation, ordered step chains, pending outputs, and failure-sensitive stack output handling. In particular, missing outputs after failure cannot simply be treated as intentional deletions.
- **C3:** The same executor distinguishes serial chains from independent work and schedules execution through workers and synchronization primitives. This exposes the concrete tradeoff between respecting dependencies and keeping unrelated resource operations concurrent.
- **C2:** Language hosts and resource providers communicate with a common deployment engine; resource registration, diffing, replacement, and deletion remain engine concerns. The [execution overview](https://www.pulumi.com/docs/iac/guides/basics/how-pulumi-works/) explains this reusable boundary across languages and providers.

### [openstack/heat](https://github.com/openstack/heat)

**Language / role:** Python; template-based cloud orchestration. **Official substantive GitHub mirror:** development is hosted by OpenStack on OpenDev.

Study distributed execution of stack dependency graphs, especially what cancellation means when cloud operations have already started.

- **C1:** The convergence worker distinguishes stopping workers at yield points from stopping a traversal: the latter marks failure and prevents further propagation while allowing in-progress resource work to finish. Nested stacks complicate that distinction. These semantics are documented in the [worker API and implementation reference](https://docs.openstack.org/heat/latest/api/heat.engine.worker.html).
- **C2:** API services, RPC communication, and the orchestration engine separate request protocols from stack/resource processing. The [architecture guide](https://docs.openstack.org/heat/latest/developing_guides/architecture.html) explains the division, while the worker reference shows asynchronous actors processing resource updates, cleanup, and related graph operations.

The architecture guide contains historical material; the more specific worker documentation supplies the execution detail used here.

## Continuous control planes and deployment lifecycle

### [crossplane/crossplane](https://github.com/crossplane/crossplane)

**Language / role:** Go; Kubernetes-based infrastructure control plane. The relevant subsystem is composition and its function execution pipeline.

Study how an extensible control plane lets external functions construct desired resources without abandoning a common reconciliation contract.

- **C1:** A function must preserve desired state produced by earlier pipeline stages unless it intentionally changes that state. Response correlation and fatal-result handling are also explicit protocol obligations. These are consequential correctness rules, because an omitted desired resource can change what subsequent reconciliation considers authoritative.
- **C2:** Functions expose a gRPC contract and can be packaged independently, making composition logic reusable across different composite resource APIs. The protocol also specifies response caching through TTLs rather than baking one execution policy into every function.

The [composition function specification](https://raw.githubusercontent.com/crossplane/crossplane/main/contributing/specifications/functions.md) is the primary architectural entry point for both criteria. It is a contract-level study guide; readers should match detailed API fields to the Crossplane version they investigate.

### [kubernetes-sigs/cluster-api](https://github.com/kubernetes-sigs/cluster-api)

**Language / role:** Go; Kubernetes cluster lifecycle controllers. This entry covers the core Machine lifecycle and the repository's related bootstrap/control-plane machinery, not every external provider.

Study deletion as a distributed protocol rather than a single API call.

- **C1:** Machine deletion coordinates hooks, workload draining, volume detachment, infrastructure deletion, bootstrap cleanup, and removal of the Kubernetes Node. The [Machine deletion specification](https://main.cluster-api.sigs.k8s.io/tasks/automated-machine-management/machine_deletions.html) explains waiting conditions, exceptions, and retries that protect storage and workload lifecycle invariants.
- **C2:** Infrastructure and bootstrap objects remain distinct participants in a common Machine lifecycle. The same specification makes the provider boundaries concrete by identifying which objects the controller requests deleted and which disappearances it must observe before continuing.
- **C3:** Draining progresses through reconciliation and requeueing rather than one controller invocation blocking until all eviction work finishes. This is an instructive execution structure for long-running operations under external constraints.

### [cloudfoundry/bosh](https://github.com/cloudfoundry/bosh)

**Language / role:** Primarily Ruby; BOSH Director and deployment lifecycle machinery. The CLI and agent have separate repositories and are not counted here.

Study infrastructure replacement strategies where persistent disks, instance identity, and available capacity constrain the order of operations.

- **C1:** The create-swap-delete strategy provisions a replacement before stopping the old VM, then transfers persistent disks and completes the transition. Static-IP instance groups cannot use the same strategy because two VMs cannot simultaneously claim that address. These constraints are explicit in the [deployment VM strategy documentation](https://bosh.io/docs/changing-deployment-vm-strategy/).
- **C3:** Preparing replacement VMs in parallel reduces time spent in later replacement steps but temporarily consumes additional infrastructure capacity. The same guide documents strategy selection and per-instance-group overrides, making the performance/resource tradeoff visible in the deployment model.

This is especially useful for studying why a generally attractive replacement strategy needs exceptions determined by resource identity and ownership.

### [juju/juju](https://github.com/juju/juju)

**Language / role:** Go; model-driven infrastructure and application lifecycle controller with machine and unit agents.

Study how a distributed desired-state model is decomposed into agent workers and provider-facing operations.

- **C1:** Worker runners distinguish tasks that should restart from completed tasks and fatal agent errors. A runner owning an API connection can stop its dependent workers, reconnect, and reconstruct them, avoiding continued work against a failed connection.
- **C2:** Provider implementations abstract the compute, storage, and network substrate, while API facades isolate worker responsibilities such as provisioning and upgrading. Facades are individually versioned and negotiate supported versions, exposing an explicit compatibility boundary between components.

Both details are described in the [Juju 3.6 architectural overview](https://canonical.com/juju/docs/juju-cli/3.6/contributor/reference/architectural-overview/). This is a version-scoped architectural source, not a claim that its database internals or every worker path describe all subsequent Juju releases.

## General host configuration engines

### [ansible/ansible](https://github.com/ansible/ansible)

**Language / role:** Python; ansible-core execution engine, playbooks, inventories, and plugin infrastructure. External collection repositories are not separate entries here.

Study how agentless automation coordinates host workers, execution strategies, user-visible results, and failure status.

- **C1:** Cross-process result handling includes typed envelopes for results, display requests, prompts, and secret-mask registration. The task queue manager also distinguishes failed hosts from unreachable hosts instead of collapsing these into one outcome.
- **C2:** Strategy plugins, inventory/host state, callbacks, and worker processes meet at a common scheduling boundary. This makes alternative execution strategies possible without rewriting module semantics.
- **C3:** A bounded pool of forked workers and interprocess queues supports concurrent host operations while retaining central result processing.

The [task queue manager source](https://raw.githubusercontent.com/ansible/ansible/devel/lib/ansible/executor/task_queue_manager.py) is a substantive entry point for all three criteria. Follow its worker and strategy interfaces to understand how concurrency affects observable playbook behavior.

### [saltstack/salt](https://github.com/saltstack/salt)

**Language / role:** Python; remote execution and declarative host-state engine.

Study the semantics of a state dependency language, particularly why ordering, change-triggered execution, and failure-triggered execution need different operators.

- **C1:** A required state can prevent a dependent state from executing after failure; `watch`, `onchanges`, `prereq`, and `onfail` have distinct evaluation behavior. Confusing these relationships can produce incorrect service restarts or recovery actions even when every individual state module is correct.
- **C2:** Requisites compose independently implemented state modules, including packages, files, and services. Reverse requisites and different matching forms allow reusable formulas without putting all orchestration logic inside resource implementations.

The detailed [requisites reference](https://docs.saltproject.io/en/latest/ref/states/requisites.html), including its examples and operator distinctions, supplies primary evidence for both criteria. It offers a focused route into Salt's execution model before exploring the broader event and transport subsystems.

### [puppetlabs/puppet](https://github.com/puppetlabs/puppet)

**Language / role:** Ruby; catalog-based declarative host configuration engine.

Study the transaction implementation that turns a resource catalog into ordered provider operations. A Puppet transaction should not be assumed to provide database-style atomic rollback of all external changes.

- **C1:** Dynamically generated resources affect dependency handling; cycles must be detected and represented as failures. Pre-run checks, provider suitability, and failure propagation also affect whether catalog resources can be evaluated safely.
- **C2:** Catalogs, resource harnesses, event management, and providers divide specification, ordering, execution, and reporting. Provider prefetching is coordinated centrally rather than requiring every resource to invent a transaction model.

The [transaction source](https://raw.githubusercontent.com/puppetlabs/puppet/main/lib/puppet/transaction.rb) exposes these mechanisms together, including generated-resource processing, graph traversal, exception handling, and report persistence. It is a useful case study in preserving coherent reporting when only part of a configuration run succeeds.

### [chef/chef](https://github.com/chef/chef)

**Language / role:** Ruby; Chef Infra Client's resource convergence engine.

Study the runner and notification machinery, where resource changes create additional work and failures can arrive during both ordinary convergence and deferred actions.

- **C1:** Immediate and delayed notifications are conditional on whether an action updated a resource. When convergence fails, the runner still processes delayed notifications and preserves multiple failures rather than silently replacing the original error. Forward notifications and unified-mode behavior further complicate execution order.
- **C2:** Resources, providers, run context, and the notification scheduler allow many resource kinds to share a common convergence lifecycle. Lazy resource references are resolved at a defined stage instead of each provider managing the entire run.

The [runner implementation](https://raw.githubusercontent.com/chef/chef/main/lib/chef/runner.rb) is compact enough to read end to end and makes the error and notification semantics explicit. It is a strong entry point before exploring the larger resource/provider framework.

### [cfengine/core](https://github.com/cfengine/core)

**Language / role:** C; promise-based host configuration and convergence engine.

Study a configuration model that incorporates repeated execution, expensive checks, and overrunning processes into policy semantics.

- **C1:** The documented `expireafter` behavior depends on a later agent invocation detecting an overdue earlier execution; it is not simply a timer within the original action. The interaction between lock state, retry frequency, and termination is a substantive failure-handling problem.
- **C2:** Promise types and reusable bodies express files, processes, services, storage, and other resources through shared action controls. Fix-versus-warn behavior can therefore be expressed independently of a particular resource implementation.
- **C3:** `ifelapsed` throttles repeated checks, including costly ones. Its lock-based timing is explicitly described as weak frequency control, a useful limitation to study rather than assuming strict scheduling guarantees.

The [promise types and common attributes reference](https://docs.cfengine.com/docs/lts/reference/promise-types/) is the primary entry point for these semantics.

## Smaller, reactive, and policy-oriented configuration engines

### [pyinfra-dev/pyinfra](https://github.com/pyinfra-dev/pyinfra)

**Language / role:** Python; agentless configuration and deployment through facts, operations, and connectors.

Study how a Python deployment definition can preserve operation order while discovering remote state and executing across many hosts.

- **C1:** Preparation records operations and their order, while execution evaluates operations against the relevant state to produce changes. The separation matters when earlier operations alter facts needed by later ones; treating the initial inspection as a permanently valid plan would be incorrect.
- **C2:** Facts, operation implementations, and connectors separate state discovery, desired changes, and transport.
- **C3:** The default execution model progresses through operations across hosts in lockstep while allowing host concurrency, and reuses SSH connections with separate channels for commands. The [deployment process documentation](https://docs.pyinfra.com/en/3.x/deploy-process.html) explains these stages and constraints.

The [3.x changelog](https://github.com/pyinfra-dev/pyinfra/blob/3.x/CHANGELOG.md) provides a second entry point into concrete correctness work, including shell quoting and execution-context fixes. No benchmark advantage is inferred from the concurrency model.

### [bundlewrap/bundlewrap](https://github.com/bundlewrap/bundlewrap)

**Language / role:** Python; declarative host configuration based on reusable bundles and resource items.

Study a relatively small resource protocol with explicit state comparison and dependency semantics.

- **C1:** `after` imposes ordering, whereas `needs` also changes behavior when a dependency fails or is skipped. That distinction prevents ordering alone from being mistaken for a success prerequisite. The [item dependency reference](https://docs.bundlewrap.org/repo/items.py/) also explains implicit dependencies and triggered execution.
- **C2:** Custom items expose expected state, actual state, and a repair method receiving the difference. Absence has an explicit representation rather than being conflated with an empty property dictionary.
- **C3:** Item types can declare incompatible concurrent execution through `block_concurrent`, allowing the scheduler to parallelize work without assuming all resource handlers can overlap safely. The [custom item development guide](https://docs.bundlewrap.org/guide/dev_item/) documents this interface alongside state comparison.

### [purpleidea/mgmt](https://github.com/purpleidea/mgmt)

**Language / role:** Go; reactive configuration engine and the MCL configuration language.

Study resource convergence as a lifecycle of validation, initialization, watching, and checking/applying, rather than just repeated execution of scripts.

- **C1:** `CheckApply` distinguishes a resource that was already correct from one repaired during the call. Apply-disabled execution must not mutate the resource; an applying call is expected to converge or return an error. The resource contract also accounts for concurrent outside changes through subsequent watch events.
- **C2:** Common resource traits and lifecycle methods support different resource kinds without duplicating engine orchestration.
- **C3:** Watches invalidate the engine's knowledge of resource state, enabling it to avoid repeated checks when nothing has invalidated that knowledge. The relationship between event delivery and correctness is therefore explicit.

The [resource development guide](https://raw.githubusercontent.com/purpleidea/mgmt/master/docs/resource-guide.md) explains these contracts and the restrictions on shared/global state. It is the primary architectural entry point for this selection.

### [Normation/rudder](https://github.com/Normation/rudder)

**Language / role:** Scala server with Rust policy tooling and modules; configuration policy generation and execution support. Relevant monorepo subsystems include `policies/rudderc` and the policy modules.

Study both cross-platform policy compilation and the point where a common abstraction must preserve operating-system-specific behavior.

- **C2:** The [technique compiler guide](https://docs.rudder.io/techniques/8.3/usage.html) describes generating Linux CFEngine policy, Windows PowerShell policy, and metadata from technique definitions, with validation and reusable methods. The compiler is part of a broader configuration engine rather than an isolated syntax converter.
- **C1:** An accepted [service restart architecture decision](https://github.com/Normation/rudder/blob/master/adr/system/28559-service-restart-system-updates.md) documents failures caused by uniform service restarts after package upgrades. It moves restart/reboot responsibilities toward package-manager-specific handling, including native mechanisms and exceptions, while retaining separate upgrade and restart phases.

The second source is an architectural decision, not proof that every described change has shipped. The compiler guide is explicitly versioned at 8.3.

## Declarative Nix deployment and storage

### [nix-community/colmena](https://github.com/nix-community/colmena)

**Language / role:** Rust and Nix; multi-host NixOS deployment engine built on Nix's evaluation and build machinery.

Study orchestration above an existing package/build system: evaluation, building, copying closures, activation, keys, and rebooting still require substantive scheduling and failure policy.

- **C1:** Deployment checks can refuse to replace an unknown remote system profile unless explicitly permitted. The engine also distinguishes errors that terminate an overall evaluation from failures of individual attributes/jobs.
- **C3:** Separate evaluation and apply limits use semaphores; chunked and streaming evaluation paths organize work differently. Building locally versus on the target and copying closures are represented as explicit deployment stages.
- **C2:** Host, profile, goal, target-node, and job abstractions separate transport and machine operations from the deployment strategy.

The [deployment module](https://raw.githubusercontent.com/nix-community/colmena/main/src/nix/deployment/mod.rs) contains the relevant implementation. Its streaming evaluator is marked experimental; that path should be studied with its stated status intact.

### [nix-community/disko](https://github.com/nix-community/disko)

**Language / role:** Nix with generated shell operations; declarative disk partitioning, formatting, encryption, and mounting.

Study how a nested storage description becomes an ordered program whose mistakes can destroy or make data inaccessible.

- **C1:** Device dependencies are topologically sorted, and cycles are rejected. Creation and mount scripts follow dependency order; unmounting uses the reverse relationship. Destroying, formatting, and mounting are separate phases, making their different safety requirements visible.
- **C2:** Recursive module types represent different storage layers and combinations, including partitions, encryption, logical volumes, and filesystems. Shared schema machinery generates operations and integrates with NixOS configuration rather than requiring an unrelated script for every layout.

The [core library](https://raw.githubusercontent.com/nix-community/disko/master/lib/default.nix) exposes the type construction and dependency-ordering machinery. This is a study of explicit destructive provisioning semantics, not a claim that arbitrary layout changes are nondestructive or universally idempotent.

## First boot and bare-metal provisioning

### [canonical/cloud-init](https://github.com/canonical/cloud-init)

**Language / role:** Python; cloud instance initialization through datasource discovery and configuration modules.

Study boot ordering as a correctness constraint, including which configuration can be known before networking and which needs network-delivered data.

- **C1:** The local stage must render appropriate networking and prevent stale image network configuration from taking effect. Later network-dependent stages can process included user data and storage configuration; doing that work too early would use incomplete information or conflict with boot dependencies.
- **C2:** Datasources and staged modules let the same initialization engine adapt to different cloud metadata systems and operating-system configuration tasks. Detect, local, network, config, and final stages provide shared lifecycle boundaries for those extensions.

The repository's [boot stage design documentation](https://raw.githubusercontent.com/canonical/cloud-init/main/doc/rtd/explanation/boot.rst) is the primary entry point. This belongs here as an actual initialization engine, even though it normally runs at a different lifecycle point from continuous configuration managers.

### [coreos/ignition](https://github.com/coreos/ignition)

**Language / role:** Go; early-boot machine provisioning. The repository now also contains Butane-related configuration tooling and is counted once.

Study the separation between validating a provisioning specification and mutating storage and system configuration during early boot.

- **C1:** Validation rejects conflicting configuration before execution, while runtime failures that cannot be predicted from the specification still require explicit failure behavior. Configuration fetching must distinguish a slow source from the absence of configuration; silently continuing can produce a machine with unintended state.
- **C2:** The [development guide](https://github.com/coreos/ignition/blob/main/docs/development.md) separates a frontend parsing/validation library from backend machine changes. It also defines versioning and feature-admission rules for the configuration specification, which are useful examples of evolving an executable data format.

The [release history](https://github.com/coreos/ignition/releases) provides a second entry point: inspected releases include Butane integration, a partition-device race fix, and test/toolchain compatibility changes. These observations are specific evidence, not a blanket maintenance or correctness guarantee.

### [openstack/ironic](https://github.com/openstack/ironic)

**Language / role:** Python; bare-metal provisioning service. **Official substantive GitHub mirror:** OpenStack develops the project on OpenDev.

Study a machine lifecycle whose actions involve both out-of-band hardware control and in-band deployment agents.

- **C1:** The [node state machine](https://docs.openstack.org/ironic/latest/user/states.html) distinguishes enrollment, cleaning, availability, deployment waits, active use, and several failure/recovery states. A failed deployment can be retried or undeployed; cleanup failure is not equivalent to a machine being ready for reuse. Agent callbacks and timeouts make these transitions distributed rather than purely local.
- **C2:** The common lifecycle supports different hardware interfaces and deployment implementations. Drivers supply hardware-specific operations while state transitions give users and orchestration systems a consistent model of progress, failure, and recovery.

The state documentation is the strongest entry point for understanding why bare-metal provisioning requires more than issuing a power-on command and serving an image.

### [cobbler/cobbler](https://github.com/cobbler/cobbler)

**Language / role:** Python; network installation/provisioning server coordinating distribution, profile, system, and boot configuration.

Study the object model beneath a provisioning service, particularly inherited configuration and the cost of repeatedly resolving related objects.

- **C2:** The abstract item hierarchy separates serializable objects, inheritable objects, and bootable objects. Explicit dependency maps connect distributions, profiles, images, systems, and related records; raw values and fully resolved inherited values are distinct representations.
- **C3:** Item caching reduces repeated lookups, while lazy materialization can defer loading full objects. Cache invalidation and dependency-aware loading are visible architectural responsibilities rather than hidden optimizations.

The [abstract item API documentation](https://cobbler.readthedocs.io/en/latest/code-autodoc/cobbler.items.abstract.html) includes implementation links, dependency mappings, cache methods, and class change histories. **Version limitation:** the inspected documentation describes the 4.0 development series, with several features explicitly marked unreleased; these details must not be attributed wholesale to older stable releases.

### [tinkerbell/tinkerbell](https://github.com/tinkerbell/tinkerbell)

**Language / role:** Go; consolidated bare-metal provisioning system with workflow, boot, metadata, and hardware-control components. Historical component repositories are not counted separately.

Study how a hardware-specific provisioning request becomes a reusable sequence of worker actions under a controller-managed lifecycle.

- **C1:** Workflows move through preparation, pending/running execution, and post-processing before terminal states. Enabling and later disabling network boot are part of that lifecycle; timeout and failure are explicit outcomes. The [v0.22 workflow guide](https://tinkerbell.org/docs/v0.22/concepts/workflows/) explains controller rendering, persisted tasks, and these transitions.
- **C2:** A workflow binds hardware to a reusable template. Tasks select workers, while container actions carry execution details such as environment, volumes, and timeouts. The [template model](https://tinkerbell.org/docs/v0.22/concepts/templates/) separates those reusable action sequences from a particular hardware binding.

The linked documentation is versioned, which makes it a more precise starting point than assuming old Tinkerbell component layouts match the consolidated repository.

## Coverage and search notes

Discovery used live web searches with meaningfully different formulations: infrastructure-as-code dependency graphs and state engines; agentless Python configuration systems; Ruby and C host configuration engines; reactive Go configuration; Kubernetes infrastructure reconciliation; OpenStack orchestration and bare-metal state machines; BOSH/Juju deployment lifecycle; NixOS deployment and disk configuration; cloud first-boot engines; and PXE/network provisioning. Additional searches for less prominent projects and language communities led to BundleWrap, mgmt, Rudder, Colmena, and disko alongside the larger ecosystems. Follow-up searches targeted source files, protocol specifications, deletion semantics, resource development guides, and architecture decisions. Later broad searches mostly repeated candidates or returned configuration collections and shallow wrappers, indicating diminishing discovery returns.

The resulting **24 repositories** cover Go, Python, Ruby, C, Rust, Scala, and Nix implementations; one-shot planning, repeated convergence, persistent reconciliation, reactive invalidation, and first-boot execution; and cloud, virtual-machine, host, and physical-machine scopes. Monorepos count once. OpenTofu is the deliberate fork exception because its separately developed state-encryption behavior supplies distinct study material. Heat and Ironic are explicitly identified as official mirrors.

Important exclusions include provider-only collections, cookbook/playbook repositories, generated SDK wrappers, tutorial engines, awesome lists, inventory/DCIM systems without provisioning execution, generic CI orchestration, and standalone infrastructure syntax compilers. Image builders and broader container schedulers were left to adjacent categories. [NixOps](https://github.com/NixOS/nixops) was examined but omitted from the main selection: its repository describes low-maintenance status and warns about suitability for new projects, while Colmena supplies a focused Nix deployment implementation here. That is a scope choice, not a claim that historical NixOps has no engineering value.

All retained repository URLs were opened, and each entry uses at least one additional primary source with substantive architecture, execution semantics, or implementation content. Some attempted source URLs failed to load; the report cites successfully opened alternatives. No candidate code was executed, dependencies installed, or performance benchmarked. Links to moving branches and `latest` documentation are research-date snapshots, not immutable source pins. Juju, Rudder, Tinkerbell, and Cobbler have explicit version or implementation-status qualifications above. Absence of a C4 label is not evidence of immaturity: sustained evolution was only credited where the inspected material established more than repository age or recent activity. The engineering study recommendations and criterion assignments are grounded in the cited material but remain evaluative judgments, not independent audits of the projects.
