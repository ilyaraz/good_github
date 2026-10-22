# Software-defined networking controllers

Research date: **2026-10-09**.

This guide selects **20 GitHub repositories** implementing SDN controllers, substantial controller frameworks, or controller runtimes that compile network policy into forwarding behavior. It covers physical OpenFlow fabrics, WAN circuit control, virtual networks, P4Runtime, and research programming models. In larger repositories, the relevant controller subsystem is identified explicitly. Protocol codecs, switches, emulators, deployment wrappers, and ordinary network automation tools are outside the main selection.

The criteria are engineering judgments grounded in the linked primary material, not certifications of correctness or production suitability. Historical implementations remain useful study targets and are labeled accordingly. Repository status and default branches were checked through GitHub pages and the GitHub API; a recent push alone is not treated as proof of maintenance quality.

- **C1 — Difficult correctness:** meaningful invariants, concurrency, protocol semantics, adversarial inputs, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces or models supporting multiple applications and use cases.
- **C3 — Performance with structure:** concrete resource, latency, or throughput constraints addressed through an understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate complexity management.

## General-purpose controller platforms

### 1. [opennetworkinglab/onos](https://github.com/opennetworkinglab/onos)

**Java — clustered controller platform; official GitHub mirror.** The repository explicitly identifies Gerrit as its contribution upstream. The mirror's [last observed push was in June 2024](https://api.github.com/repos/opennetworkinglab/onos), so treat this as an inspectable ONOS snapshot rather than assume it represents current upstream development.

Study the boundary between an application's declarative intent and the asynchronous work required to install, withdraw, and recompile it. The relevant subsystem is `core/api` plus the intent implementation in `core/net`.

- **C1:** Intent processing checks ownership before recompilation, avoids resubmitting work already pending, and releases shared resources only after checking whether other intents still use their resource group. These are concrete lifecycle and ownership invariants in [IntentManager](https://github.com/opennetworkinglab/onos/blob/master/core/net/src/main/java/org/onosproject/net/intent/impl/IntentManager.java).
- **C2:** [IntentService](https://github.com/opennetworkinglab/onos/blob/master/core/api/src/main/java/org/onosproject/net/intent/IntentService.java) exposes asynchronous submission and withdrawal, state inspection, and events. Compiler and installer registries in the implementation separate application policy from its realization on devices.

### 2. [opendaylight/controller](https://github.com/opendaylight/controller)

**Java — distributed controller infrastructure; official Gerrit mirror.** This repository is the controller's clustered data and runtime foundation, not the entire collection of OpenDaylight southbound plugins.

Study how a model-driven controller exposes transactions while its storage is partitioned, replicated, and subject to leader changes. The [distributed datastore design](https://github.com/opendaylight/controller/blob/master/opendaylight/md-sal/sal-distributed-datastore/src/site/asciidoc/distributed-data-store.adoc) is unusually explicit about uncertain outcomes after communication failures. It is an evolving design document and retains older Akka terminology.

- **C1:** The design analyzes lost messages, shard-leader failure, actor failure, transaction identity, and the inability to infer whether a timed-out request executed. A replicated state machine and frontend/backend protocol make these failure modes part of the controller's core design.
- **C2:** Applications use a `DOMDataBroker` and a transactional data-tree model instead of implementing shard communication themselves. The same document explains how this abstraction separates frontend application access from backend replication.
- **C3:** Local-leader access can perform preparatory work in the calling thread, avoiding messages otherwise needed for remote access; the design explains the locality tradeoff rather than merely claiming speed.

### 3. [PANTHEONtech/lighty](https://github.com/PANTHEONtech/lighty)

**Java — embeddable SDN controller SDK built from OpenDaylight components.** This is a separate runtime and integration project, not another copy of the OpenDaylight controller repository. Its inspected README declares compatibility with the OpenDaylight 2026-09 release.

Study how to package controller services into a Java application with explicit lifecycle ownership. The [migration guide](https://github.com/PANTHEONtech/lighty/blob/main/docs/ODL-migration-guide.md) maps OSGi activation and configuration responsibilities to `LightyModule`, while leaving application module ordering explicit.

- **C2:** Modules, service injection, model registration, and independently initialized northbound/southbound components allow the controller to be embedded in different applications and application frameworks.
- **C1:** [LightyControllerImpl](https://github.com/PANTHEONtech/lighty/blob/main/lighty-core/lighty-controller/src/main/java/io/lighty/core/controller/impl/LightyControllerImpl.java) manages actor startup, clustered datastore restoration, schema/codec construction, and ordered shutdown. Shutdown handles ownership-service errors, actor termination timeouts, and waiting for the actor-system port to become available before reuse.

### 4. [floodlight/floodlight](https://github.com/floodlight/floodlight)

**Java — modular OpenFlow controller.** Historical study target: [repository metadata shows the last push in April 2024](https://api.github.com/repos/floodlight/floodlight); ongoing maintenance is not assumed.

Study the interaction between extension loading and a stateful southbound protocol. Floodlight makes both concerns visible in ordinary Java classes rather than hiding them behind an application example.

- **C1:** [OFSwitchHandshakeHandler](https://github.com/floodlight/floodlight/blob/master/src/main/java/net/floodlightcontroller/core/internal/OFSwitchHandshakeHandler.java) tracks pending role requests, transaction IDs, timeouts, unsupported-role behavior, and master/slave state transitions. Its comments also disclose limitations of retaining only the latest pending role request, making it useful for critical review of failure handling.
- **C2:** [FloodlightModuleLoader](https://github.com/floodlight/floodlight/blob/master/src/main/java/net/floodlightcontroller/core/module/FloodlightModuleLoader.java) resolves module dependencies through service interfaces and initializes a configured controller composition. This supports reusable topology, forwarding, and other services without baking each application into the core.

## OpenFlow and programmable-switch frameworks

### 5. [faucetsdn/faucet](https://github.com/faucetsdn/faucet)

**Python — configuration-driven controller for OpenFlow 1.3 switching and routing.** Faucet is a network implementation on top of controller machinery, making it a useful complement to general frameworks such as Ryu.

Study how VLANs, ACLs, host learning, routing, and flooding become a multi-table switch pipeline. The [architecture and pipeline specification](https://docs.faucet.nz/en/latest/architecture.html) describes the ordering and responsibilities of individual tables.

- **C1:** The pipeline encodes concrete isolation and packet-processing rules: ingress VLAN validation, dropping unknown or unwanted traffic at specified stages, source-MAC spoof protection for the controller's virtual MAC, and VLAN-scoped flooding.
- **C3:** Forwarding work is pushed into switch tables, with controller involvement for learning and control traffic. Unneeded tables are omitted, while tables are referred to by name because numeric IDs can change with the configured pipeline. This ties resource use directly to a comprehensible architecture.
- **C2:** The pipeline combines L2, IPv4/IPv6 routing, ACLs, and external packet-processing integration across compatible switches, rather than implementing only a fixed learning-switch application.

### 6. [faucetsdn/ryu](https://github.com/faucetsdn/ryu)

**Python — component-based controller framework.** **Explicitly unmaintained:** the repository's README says Ryu needs maintainers and points readers to OpenStack's OS-Ken alternative. That pointer is not treated here as independent verification of OS-Ken's present maintenance.

Study a compact event-driven application model and the consequences of blocking handlers. The [application API guide](https://ryu.readthedocs.io/en/latest/ryu_app_api.html) explains the execution model and OpenFlow negotiation phases.

- **C1:** Each application has an ordered receive queue and one event-processing thread; a blocking callback stalls later events. Synchronous request replies use a separate transaction queue to avoid deadlock. Handlers can be restricted to handshake, configuration, operational, or disconnected phases.
- **C2:** `RyuApp`, typed events, decorators, and version-specific datapath/parser objects let applications reuse protocol and dispatch infrastructure. The framework supports multiple network-control protocols rather than one forwarding policy.

### 7. [kytos-ng/kytos](https://github.com/kytos-ng/kytos)

**Python — Kytos-ng controller core and network-application platform.** This is a substantive continuation of Kytos; the original archived `kytos/kytos` repository is not counted separately.

Study the separation of controller lifecycle, asynchronous event delivery, and installable Network Applications, or NApps. The [architecture overview](https://github.com/kytos-ng/kytos/blob/master/docs/developer/architecture.rst) explains this separation; some listed companion applications reflect the inherited architecture and should be read alongside current changes.

- **C2:** The controller registers, loads, unloads, and connects applications through event buffers, while protocol parsing and network functions have separate responsibilities.
- **C1:** The [changelog](https://github.com/kytos-ng/kytos/blob/master/CHANGELOG.rst) records concrete concurrency and lifecycle work: per-link locking, waiting for NApps during shutdown, startup-exception handling, and preventing late consistency executions after shutdown. Its unreleased section separately records duplicate-datapath and pidfile-ownership fixes; these are not claimed as released features.
- **C4:** Releases spanning 2022–2026 document Python and database upgrades, API startup ordering, queue resilience, and tested operating-system compatibility. This is evidence of sustained adaptation beyond merely an old creation date.

### 8. [noxrepo/pox](https://github.com/noxrepo/pox)

**Python — component-based network platform with an OpenFlow controller.** The verified default branch is `gar-experimental`; the README distinguishes Python 3 “gar” from the older Python 2 line. The controller subsystem, rather than POX's additional switch capabilities, is the selection target.

- **C1:** [OpenFlow connection handling](https://github.com/noxrepo/pox/blob/gar-experimental/pox/openflow/of_01.py) checks handshake versions and barrier transaction IDs, defers port-status events until connection setup completes, and handles real switch quirks. This is a useful study of ordering across protocol initialization and asynchronous device events.
- **C2:** [The core runtime](https://github.com/noxrepo/pox/blob/gar-experimental/pox/core.py) provides component registration, dependency-ready callbacks, and a cooperative scheduler. It explicitly explains how external threads must schedule work back into the cooperative execution context to preserve the assumptions of code written without locks.

The smaller codebase makes it practical to trace bootstrapping, protocol events, and an application together; its older OpenFlow focus is a scope constraint.

### 9. [trema/trema](https://github.com/trema/trema)

**Ruby, with Gherkin acceptance specifications — OpenFlow controller framework and development environment.** Historical: [last repository push observed in June 2018](https://api.github.com/repos/trema/trema). The inspected default branch is `develop`.

Study an approachable controller API that still exposes meaningful concurrency and protocol-version concerns. [Controller implementation](https://github.com/trema/trema/blob/develop/lib/trema/controller.rb) is the main entry point.

- **C1:** Connections and timers use threads, but application handlers are serialized through a mutex. Switch initialization failures, disconnected sockets, unsupported OpenFlow versions, and different OpenFlow 1.0/1.3 flow-modification fields are handled explicitly.
- **C2:** Applications subclass `Controller` and implement event handlers while reusing message construction, timers, connection management, and the surrounding network-emulation environment.

The [changelog](https://github.com/trema/trema/blob/develop/CHANGELOG.md) provides useful compatibility examples, including OpenFlow 1.3 output-port defaults and startup-time packet handling. Its inconsistent date labels are a reason not to use it to establish a precise multi-year C4 claim.

### 10. [ARCCN/runos](https://github.com/ARCCN/runos)

**C++ — distributed OpenFlow controller with active/standby recovery.** Study the tension between asynchronous switch requests and controller ownership. The code offers a different implementation style from Java service containers and Python event frameworks.

- **C1:** [Recovery.cc](https://github.com/ARCCN/runos/blob/master/src/core/Recovery.cc) handles role requests with generation IDs, timeouts, unexpected `EQUAL` responses, and master-to-slave changes associated with split-brain handling. It can detach a switch whose role cannot be reconciled.
- **C2:** [OFAgent.hpp](https://github.com/ARCCN/runos/blob/master/src/core/api/OFAgent.hpp) presents future-returning operations for barriers, switch configuration, roles, statistics, and flow/group/meter changes. Typed errors preserve datapath and transaction identifiers, making asynchronous failure information available to reusable controller applications.

The repository also separates server connection management from recovery and application APIs. No numerical throughput claim or current support guarantee is inferred from its performance-oriented description.

### 11. [byllyfish/finsy](https://github.com/byllyfish/finsy)

**Python/asyncio — P4Runtime controller library with gNMI support.** This is a controller-building library, not a packaged network operating system. Its README documents multi-switch controllers, ready handlers, and task lifetimes tied to switch connections and role changes.

- **C1:** [P4Runtime arbitration](https://github.com/byllyfish/finsy/blob/main/finsy/p4arbitrator.py) handles election-ID collisions and primary/backup transitions, checks election-ID invariants, and attaches role/election information to write requests. The code also documents a switch-specific arbitration workaround, giving a concrete protocol-compatibility case to examine.
- **C2:** Switch objects, controller orchestration, typed P4 entities, and managed asynchronous handlers provide reusable building blocks for different P4 programs and network applications. Disconnect or role-change behavior is part of the public programming model.

The [changelog](https://github.com/byllyfish/finsy/blob/main/CHANGELOG.md) is a second useful entry point for tracing evolving P4Runtime support, Python compatibility, API changes, and controller-removal completion semantics. No multi-year claim is based solely on its undated version headings.

## WAN and research-network circuit controllers

### 12. [telstra/open-kilda](https://github.com/telstra/open-kilda)

**Java, with Python and other supporting components — distributed OpenFlow WAN controller.** Its stated problem is global networking with substantial control-plane latency and latency-aware path optimization. The repository uses its own application and processing architecture while incorporating Floodlight as a southbound component; it is not merely another Floodlight fork.

Study asynchronous flow operations and recovery when repeated network events arrive before previous operations finish. The [reroute retry design](https://github.com/telstra/open-kilda/blob/develop/docs/design/hub-and-spoke/reroute/retry/README.md) explicitly diagnoses duplicated retry logic and proposes a single coordination point.

- **C1:** The design distinguishes in-progress, pending, and throttled reroutes, classifies retryable failures, and serializes operations for a given flow. These are concrete ordering and failure-state problems.
- **C3:** Coalescing and throttling reroute requests address event bursts without making every topology event a new full operation. The work is organized around queues, processing services, and flow state machines.

The cited document is design evidence, not a benchmark or proof that every described transition is implemented without defects. The [last observed repository push was July 2025](https://api.github.com/repos/telstra/open-kilda).

### 13. [GlobalNOC/OESS](https://github.com/GlobalNOC/OESS)

**Perl control services, JavaScript UI, and bundled NOX components — Open Exchange Software Suite.** Historical study target: [last repository push observed in April 2023](https://api.github.com/repos/GlobalNOC/OESS). Count the suite once, including its embedded controller components.

Study how a research-network controller combines circuit provisioning with workgroup ownership, interface permissions, scheduled actions, and operational failover.

- **C1:** [FWDCTL/Master.pm](https://github.com/GlobalNOC/OESS/blob/master/perl-lib/OESS/lib/OESS/FWDCTL/Master.pm) translates forwarding-verification link events into affected-circuit failovers, suppresses those actions during maintenance, cancels restorations, and collects asynchronous switch responses when changing a circuit path.
- **C2:** The [API and data-model guide](https://globalnoc.github.io/OESS/the-basics/oess-api.html) describes reusable user, workgroup, interface, and circuit concepts. These support a network service shared by independent organizations rather than a single hard-coded forwarding application.

This is particularly useful for engineers interested in the boundary between permissioned network services and device-level control.

## Distributed network virtualization controllers

### 14. [ovn-org/ovn](https://github.com/ovn-org/ovn)

**C — Open Virtual Network control plane.** The relevant subsystems are `ovn-northd`, chassis-local `ovn-controller`, and the shared incremental-processing engine. Open vSwitch's dataplane repository is not a separate entry here.

Study a two-stage translation: desired logical networks become southbound logical flows, then chassis-specific physical OpenFlow rules. The [architecture manual](https://www.ovn.org/support/dist-docs/ovn-architecture.7.html) explains the northbound/southbound database boundary and division of responsibility.

- **C2:** Logical switches, routers, ACLs, port bindings, and chassis representation let different cloud-management integrations reuse the same controller machinery.
- **C3:** The [incremental-processing engine](https://docs.ovn.org/en/latest/topics/incremental-processing/incremental-processing.html) represents dependencies as a DAG of nodes with persistent state. Change handlers process supported deltas; otherwise a node recomputes its result, avoiding unconditional global recomputation.
- **C1:** Correct incremental processing requires complete dependencies and either correct delta handling or fallback recomputation. The guide explicitly documents this obligation and the `EN_UNHANDLED` fallback, making the performance/correctness boundary inspectable.

### 15. [OpenSDN-io/tf-controller](https://github.com/OpenSDN-io/tf-controller)

**C++ and Python — OpenSDN configuration and distributed virtual-network control plane.** This is the community continuation/fork of Tungsten Fabric. Only this lineage representative is counted; `tungstenfabric/tf-controller` is not a second project in the list. Focus on `src/bgp`, `src/control-node`, configuration distribution, and compute-agent control rather than treating the whole monorepo as uniformly exemplary.

- **C1:** The [controller design](https://github.com/OpenSDN-io/tf-controller/blob/master/Controller-Design.md) explains exclusion policies between configuration and routing tasks, route-partition invariants for VPN import/export, validation of BGP inputs, and reconciliation of desired and advertised updates.
- **C3:** Peer processing and route processing are parallelized separately; update queues suppress redundant work and retain per-peer progress when sockets become backpressured. The document connects these choices to named task, partition, and scheduling-group abstractions.
- **C2:** Schema-derived configuration and operational routing state are separated, while the design's factory-based injection allows multiple BGP servers and substituted components in tests.

Compare the design with the actual [control-node task-exclusion policy](https://github.com/OpenSDN-io/tf-controller/blob/master/src/control-node/control_node.cc).

### 16. [midonet/midonet](https://github.com/midonet/midonet)

**Scala and Java — distributed virtual-network control and simulation.** Historical: [last repository push observed in December 2022](https://api.github.com/repos/midonet/midonet). The study target is the Midolman agent's controller, topology, and flow-management code, not its packaging or client tools.

Study the design in which a packet is simulated through a virtual topology and the result becomes a datapath rule. The [design overview](https://github.com/midonet/midonet/blob/master/docs/design-overview.md) is a historical architecture description, with explicit discussion of asynchronous topology availability and replicated learning state.

- **C1:** The design addresses races between MAC learning and replicated state, suspended simulations waiting for missing topology or ARP information, and invalidating flows when the state they depend on changes.
- **C3:** Deduplicating packets while an equivalent simulation is pending reduces repeated work. The inspected [FlowController implementation](https://github.com/midonet/midonet/blob/master/midolman/src/main/scala/org/midonet/midolman/FlowController.scala) additionally exposes per-worker flow limits, preallocated flow structures, object pools, and expiration queues.

The design and implementation should be compared rather than assumed to describe identical revisions of the system.

### 17. [hubo1016/vlcp](https://github.com/hubo1016/vlcp)

**Python — distributed controller and extensible virtual-network framework.** Historical: [last repository push observed in December 2019](https://api.github.com/repos/hubo1016/vlcp). The README's deployment and throughput statements are not used as independently verified performance results.

Study how controller-local state mirrors interact with a shared transactional object database.

- **C1:** [ObjectDB's design](https://github.com/hubo1016/vlcp/blob/master/doc/source/objectdb.rst) works through lost updates, partial multi-key writes, inconsistent object references, and notifications that expose only part of a change. Walker transactions require compatible database versions and may retry; updater functions must be repeatable for identical inputs.
- **C2:** [The SDN design](https://github.com/hubo1016/vlcp/blob/master/doc/source/sdndesign.rst) lets modules request named tables and declare ordering dependencies, rather than share brittle fixed numeric table IDs.
- **C3:** That design also explains incremental flow changes and the tradeoffs among proactive installation, switch-local learning, controller learning, and first-packet upload. Performance choices are tied to controller load, broadcast traffic, and pipeline structure.

## Policy languages and research control planes

### 18. [frenetic-lang/frenetic](https://github.com/frenetic-lang/frenetic)

**OCaml, with application-facing APIs — network policy language, compiler, and controller runtime.** Historical research implementation: [last repository push observed in November 2023](https://api.github.com/repos/frenetic-lang/frenetic).

Study how high-level network policies are compiled into OpenFlow tables through a reusable intermediate representation. The [local compiler interface](https://github.com/frenetic-lang/frenetic/blob/master/src/lib/netkat/Local_compiler.mli) is an especially clear starting point.

- **C1:** Sequential and parallel composition, iteration, switch restriction, and conversion back to policy carry explicit semantic contracts. Structural equality is carefully distinguished from full semantic equivalence, and policies containing links require global rather than local compilation.
- **C2:** Forwarding Decision Diagrams provide an intermediate representation reusable by composition, interpretation, queries, and single- or multi-table output.
- **C3:** [The compiler implementation](https://github.com/frenetic-lang/frenetic/blob/master/src/lib/netkat/Local_compiler.ml) exposes field-order selection, cache preparation, optimization, and flow deduplication. These provide concrete places to examine compilation cost and generated rule size without assuming formal correctness of every optimization.

### 19. [frenetic-lang/pyretic](https://github.com/frenetic-lang/pyretic)

**Python — compositional policy language and controller runtime.** **Archived and explicitly unsupported.** It is a distinct language/runtime implementation in the Frenetic research family, not a duplicate fork of the OCaml controller.

- **C2:** [language.py](https://github.com/frenetic-lang/pyretic/blob/master/pyretic/core/language.py) gives policies both packet-evaluation and classifier-compilation interfaces, with sequential/parallel composition, filters, queries, and dynamic policies. These abstractions let independent forwarding and measurement policies be combined.
- **C1:** [runtime.py](https://github.com/frenetic-lang/pyretic/blob/master/pyretic/core/runtime.py) coordinates network changes and policy changes using distinct locks, invalidates cached classifiers after dynamic updates, and tracks classifier versions and outstanding queries/deletions. The correctness problem is keeping interpreted behavior, compiled rules, and asynchronous device events aligned.

An experienced engineer can compare language-level modularity with the much messier operational bookkeeping needed to maintain that abstraction over a changing network. Legacy dependencies and explicit archival status make this a study target rather than a present-day deployment recommendation.

### 20. [kandoo/beehive-netctrl](https://github.com/kandoo/beehive-netctrl)

**Go — research distributed controller on the Beehive programming framework.** Historical: [last repository push observed in March 2016](https://api.github.com/repos/kandoo/beehive-netctrl). The source includes incomplete operations; notably the deletion handler in `controller/flow.go` is a stub. It is retained for its distinct distributed programming model, not as a complete controller product.

- **C2:** [The network object model's path types](https://github.com/kandoo/beehive-netctrl/blob/master/nom/path.go) express a path as composable pathlets and distinguish invalid paths from paths that are valid but infeasible in the current network. Messages expose installation and deletion outcomes to subscribers independently of a southbound protocol.
- **C1:** [The consolidator and poller](https://github.com/kandoo/beehive-netctrl/blob/master/controller/consolidator.go) reconcile reported flow state with controller state, notify subscribers of disappearing flows, evaluate triggers, and detect unresponsive drivers. Mapping handlers to per-node distributed state creates a concrete ownership and consistency problem worth studying critically.

The useful comparison is between protocol handlers, message-to-state placement, and network-level abstractions; unfinished work and missing operations materially limit completeness.

## Coverage, search method, and limitations

Discovery used live web searches with more than six distinct formulations, including general OpenFlow platforms; Ryu/Faucet architecture and testing; C++ RUNOS/OpenMUL controllers; Go distributed controllers and Beehive; Kytos/OpenKilda WAN control; functional Frenetic/Pyretic controllers; OVN incremental processing; Tungsten Fabric/OpenSDN control nodes; research-network OESS; P4Runtime/Finsy; Rust and Erlang implementations; SQL-oriented Ravel; and optical/TeraFlowSDN controllers. Later searches mostly returned small demonstrations, protocol libraries, repeated known projects, or repositories outside the required hosting scope; VLCP was the final substantive addition.

Every retained canonical GitHub URL was opened or verified through GitHub's repository API. Each entry also uses independently read implementation or design material beyond its top-level README. Source paths and branches were checked against repository trees, and targeted files were read directly without cloning or running candidate code. Some older ONOS wiki pages timed out, so ONOS's actual intent API and implementation supply the architectural evidence instead.

Important selection boundaries:

- Open vSwitch, Stratum, software switches, codecs, Mininet, and benchmark tools were excluded as dataplanes, supporting libraries, or test infrastructure rather than controllers. General CNI projects and Contiv's broader container-networking integration were not needed to establish this category's coverage.
- The original Kytos and Tungsten Fabric repositories were not counted alongside their selected continuations. OpenDaylight satellite repositories and small ONOS SDKs were not multiplied into separate entries. Lighty is included for its distinct embeddable runtime, and Faucet for its substantive network-policy implementation on controller infrastructure.
- OpenMUL's advertised canonical `openmul/openmul` endpoint returned GitHub API 404 during verification. Ravel did not yield a verifiable substantial canonical repository in the searches performed. Neither was replaced with an arbitrary fork.
- TeraFlowSDN is relevant, but its [official deployment guide](https://tfs.etsi.org/documentation/latest/deployment_guide/) directs users to ETSI-hosted GitLab. No official substantive GitHub mirror was established, so it is excluded from this GitHub-only report.
- Historical code is deliberately represented, including an explicitly incomplete research controller. No builds, tests, benchmarks, security audits, or deployment claims were independently reproduced. Design documents can lag source, and quoted project status is limited to the inspected material and research date.

The list is a selection guide for studying architectural and implementation tradeoffs; it does not claim that every component, historical dependency, or operational practice is exemplary.
