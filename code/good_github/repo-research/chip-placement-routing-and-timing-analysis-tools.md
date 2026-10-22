# Chip placement, routing, and timing analysis tools

Research date: **2026-10-09**.

This report selects 22 GitHub repositories implementing ASIC or FPGA placement, physical routing, static timing analysis, or reusable physical-design infrastructure with those engines. It includes digital and analog flows, CPU and GPU algorithms, established systems, and substantial research implementations. PCB routing, logic synthesis alone, layout viewers alone, tutorial designs, and flow scripts without substantive implementation are outside this selection. The criteria describe engineering material worth studying, not a guarantee of production readiness or correctness throughout a repository.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, or failure handling. **C2** — substantial reusable abstractions supporting multiple applications. **C3** — real performance constraints addressed through an understandable architecture. **C4** — sustained evolution with concrete compatibility, testing, or complexity-management evidence. Each entry justifies at least two criteria; C4 is not inferred from repository age or a recent push.

## Integrated ASIC implementation and research infrastructure

### 1. [The-OpenROAD-Project/OpenROAD](https://github.com/The-OpenROAD-Project/OpenROAD)

**Language/role:** C++ with Tcl and Python interfaces; integrated digital physical implementation. Relevant subsystems include global and detailed placement, clock-tree synthesis, global and detailed routing, and the database/timing integration.

Study how algorithms that began as separate tools share design state and cooperate in timing and congestion optimization. The developer guide specifies one process and one database, centralized design I/O, tool-owned state, and explicit construction/initialization interfaces.

- **C2:** The common database, tool interfaces, namespaces, and Tcl integration support many physical-design stages and custom flows while reducing duplicated infrastructure. See the [developer guide](https://github.com/The-OpenROAD-Project/OpenROAD/blob/master/docs/contrib/DeveloperGuide.md).
- **C1 and C3:** The global placer combines nonlinear electrostatic optimization with slack-based net reweighting and congestion-driven cell-area inflation. Its documentation explains divergence recovery, overflow-triggered timing updates, and the runtime tradeoff between RUDY estimation and global routing. These expose numerical and cross-tool consistency problems alongside explicit cost controls. See the [global-placement implementation guide](https://openroad.readthedocs.io/en/latest/main/src/gpl/README.html).

Count this monorepo once: its RePlAce, FastRoute, TritonRoute, and TritonCTS lineage is not repeated as separate historical repositories below.

### 2. [OSCC-Project/iEDA](https://github.com/OSCC-Project/iEDA)

**Language/role:** Primarily C++; ASIC implementation infrastructure containing iPL placement, iRT routing, iCTS clock synthesis, and iSTA timing analysis. This is the project's official GitHub distribution; its README directs source checkout and contributions to Gitee, so GitHub should be treated as a substantive project mirror/distribution rather than assumed to be the sole development venue.

An engineer can compare its database/manager/operator organization with OpenROAD and then follow timing invalidation into an individual engine.

- **C2:** The repository separates shared infrastructure from the physical-design tools, including a timing engine intended to be called by other design stages. The [project overview](https://github.com/OSCC-Project/iEDA/blob/master/README.md) identifies these layers and the upstream contribution location.
- **C1:** iSTA's incremental implementation explicitly resets slew, delay, and arrival/required propagation state, handles disabled loop arcs, guards reset operations with a vertex mutex, and schedules propagation through queues. This makes dependency invalidation and traversal ordering concrete study topics; it does not establish that every incremental path is correct. See [StaIncremental.cc](https://github.com/OSCC-Project/iEDA/blob/master/src/operation/iSTA/source/module/sta/StaIncremental.cc).

### 3. [lip6/coriolis](https://github.com/lip6/coriolis)

**Language/role:** C++ and Python; VLSI database, analytical placement, and routing, centered on Hurricane, Etesian, and Katana.

Coriolis is valuable for studying a physical-design system built around a reusable geometric database and a routing engine with explicit event management. Its current README identifies GitHub as the project host, superseding older references to LIP6 GitLab.

- **C2:** Hurricane and its parsers serve the placer, router, graphical application, and Python API, making the database a reusable substrate rather than private state inside one optimizer. See the [project architecture overview](https://github.com/lip6/coriolis/blob/main/README.rst).
- **C1:** Katana's event queue must maintain ordering when segment state changes. It removes and reinserts events, refreshes keys during commit, handles invalidated segments, and includes duplicate/key-consistency checks. Read [RoutingEventQueue.cpp](https://github.com/lip6/coriolis/blob/main/katana/src/RoutingEventQueue.cpp) for a compact route into those invariants.

The obsolete standalone Coloquinte repository is excluded because it explicitly redirects users to this implementation family.

### 4. [RsynTeam/rsyn-x](https://github.com/RsynTeam/rsyn-x)

**Language/role:** C++; extensible physical-synthesis research framework with timing, routing, and congestion models. Treat its documented compiler/platform requirements as historical reference information, not a current support promise.

Study how a mutable netlist can support multiple analyses without baking each analysis into its core object representation.

- **C2:** Typed attributes attach application data to nets, pins, arcs, and library objects; services provide timing and other models. The [README's traversal and attribute examples](https://github.com/RsynTeam/rsyn-x/blob/master/README.md) show how optimizers can share the framework.
- **C1:** The timer is both a service and a design observer. It reacts to instance/net creation and removal, cell remapping, and pin connection changes. Its API also distinguishes early/late timing and different input-driver delay conventions—important semantic details when comparing against other timers. See [Timer.h](https://github.com/RsynTeam/rsyn-x/blob/master/rsyn/src/rsyn/model/timing/Timer.h).

Rsyn is retained for its own framework and timing implementation; the trimmed parser copies inside CUHK routers are not counted as additional Rsyn projects.

## Standalone timing engines

### 5. [parallaxsw/OpenSTA](https://github.com/parallaxsw/OpenSTA)

**Language/role:** C++ and Tcl; standalone and embeddable gate-level static timing analysis. This is the canonical upstream named by OpenSTA itself, rather than the OpenROAD organization copy.

Study the boundary between a host netlist, timing constraints, delay calculation, graph annotation, and incremental timing search.

- **C1:** The API guide explains why callers must use the coordinating `Sta` interface: recomputing delays without invalidating dependent arrival times leaves inconsistent results. It also specifies internal units, ownership rules, clock/exception-specific events, and incremental propagation tolerance.
- **C2:** Network adapters operate on a host application's netlist without duplicating it; delay calculators are replaceable through a separate API. Both points are developed in the [STA API guide](https://github.com/parallaxsw/OpenSTA/blob/master/doc/StaApi.md).
- **C4:** The [release/change log](https://github.com/parallaxsw/OpenSTA/blob/master/doc/ChangeLog.md) spans releases from 2018 through 2026 and documents semantic changes, deprecated commands, compatibility options, and multi-corner/multi-mode migration. This is concrete compatibility management, not merely an old creation date.

### 6. [OpenTimer/OpenTimer](https://github.com/OpenTimer/OpenTimer)

**Language/role:** C++17; parallel, incremental static timing analysis with a library and interactive shell.

Its distinctive study subject is deferred execution: edits build a task lineage, actions materialize timing work, and accessors inspect state without changing it.

- **C2:** The builder/action/accessor division is a reusable API model for applications that perform many design edits between timing queries. The [design-philosophy section](https://github.com/OpenTimer/OpenTimer#design-philosophy) explains the contract and embedding options.
- **C1 and C3:** Dependency graphs order forward slew/arrival propagation and backward required-time propagation. The implementation queues mutations under a mutex and connects tasks into the lineage, exposing both concurrency ordering and incremental-work reduction. Read [timer.cpp](https://github.com/OpenTimer/OpenTimer/blob/master/ot/timer/timer.cpp).

The README also identifies Doctest unit tests and TAU15 regression benchmarks. This is useful validation infrastructure, but no claim is made that its supported timing semantics match every commercial signoff feature.

### 7. [verilog-to-routing/tatum](https://github.com/verilog-to-routing/tatum)

**Language/role:** C++; embeddable block-based static timing library, used by VPR and other architecture-research tools.

Tatum is particularly instructive for separating timing semantics from netlist formats and arranging graph data for repeated analysis.

- **C2:** The host supplies an abstract timing graph and can provide its own delay calculator. Setup/hold analysis, multiple clocks, skew, and exceptions are supported through the library rather than a required standalone file-processing flow. See the [library overview](https://github.com/verilog-to-routing/tatum#overview).
- **C1 and C3:** `TimingGraph` stores static connectivity separately from dynamic delays and timing values. Its documented structure-of-arrays layout, strongly identified nodes/edges, levelization preconditions, and traversal-order memory reordering make both graph invariants and cache locality explicit. Start at [TimingGraph.hpp](https://github.com/verilog-to-routing/tatum/blob/master/libtatum/tatum/TimingGraph.hpp).

This is counted separately from VTR because it is an independently reusable implementation with a distinct host-integration API.

## ASIC placement and floorplanning

### 8. [limbo018/DREAMPlace](https://github.com/limbo018/DREAMPlace)

**Language/role:** Python, C++, and CUDA; analytical ASIC global placement, legalization, and detailed placement built around PyTorch operators.

Study the translation of a geometric optimization problem into tensor computation without losing discrete placement constraints.

- **C1:** The objective implementation treats gradient preconditioning, fixed-node masks, fence-region assignments, filler regions, and stopping updates for completed regions explicitly. These are numerical and constraint-preservation issues beyond merely calling an optimizer. See [PlaceObj.py](https://github.com/limbo018/DREAMPlace/blob/master/dreamplace/PlaceObj.py).
- **C3:** Expensive wirelength, density, legalization, and detailed-placement work is decomposed into operators with CPU/GPU implementations, while Python controls the optimization flow.
- **C4:** The [versioned feature history](https://github.com/limbo018/DREAMPlace#features) records deterministic execution, parallel-CPU robustness work, fence regions, timing integration, and named benchmark tests across its 2020–2024 extensions. These changes show sustained complexity and reproducibility management.

Do not generalize its published speedups across hardware or benchmarks; none are used as selection evidence here.

### 9. [google-research/circuit_training](https://github.com/google-research/circuit_training)

**Language/role:** Python/TensorFlow; reinforcement-learning macro placement and floorplanning research, with standard-cell placement integration.

Study the interaction between learned placement policies, legal move generation, a placement-cost service, and distributed experience collection.

- **C1 and C3:** The coordinate-descent implementation excludes fixed macros, restricts legal orientation families, checks location masks, and uses incremental cost updates and bounded neighborhood searches. These choices connect placement invariants to the expense of repeatedly scoring candidates. See [coordinate_descent_placer.py](https://github.com/google-research/circuit_training/blob/main/circuit_training/environment/coordinate_descent_placer.py).
- **C2:** The same training machinery supports multiple training netlists, evaluation netlists, and single-block fine-tuning through separate learner, replay-buffer, collector, and evaluator jobs. The [pretraining guide](https://github.com/google-research/circuit_training/blob/main/docs/PRETRAINING.md) specifies netlist-index and episode-length coordination.

This is a placement research system, not a replacement for final routing or signoff. It also depends on external placement-cost/build artifacts; this research did not establish that all downloadable artifacts remain obtainable.

### 10. [rubund/graywolf](https://github.com/rubund/graywolf)

**Language/role:** C; historical standard-cell placement tool in the Qflow ecosystem, continued from TimberWolf 6.3.5. GitHub metadata reports its latest push in 2021; retain it as a legacy algorithm study, not as evidence of current maintenance.

It offers a contrasting implementation style to tensor-based analytical placement: tightly coupled, incremental move evaluation in an annealing-era placer.

- **C1:** A single-cell move stages row/bin penalties, net bounding boxes, and timing changes, then commits the corresponding state only when the move is accepted. A debug path compares incremental timing penalties with a full calculation.
- **C3:** The same routine rejects expensive candidates early and recomputes affected nets/timing rather than the entire design. Read [ucxx1.c](https://github.com/rubund/graywolf/blob/master/src/twsc/ucxx1.c).

The [README](https://github.com/rubund/graywolf/blob/master/README.md) documents the TimberWolf lineage, integration changes, test command, stable/development branch policy, and a 32-bit test limitation. The lineage is represented once; its old coding style and global state are part of the engineering tradeoff to examine.

## ASIC routing engines

### 11. [RTimothyEdwards/qrouter](https://github.com/RTimothyEdwards/qrouter)

**Language/role:** C and Tcl/Tk; multilayer detailed routing for digital ASIC designs using LEF/DEF.

Qrouter is a useful smaller counterpart to modern routing frameworks: its maze search incorporates terminal geometry, obstructions, layer rules, and multi-terminal connectivity.

- **C1:** Routing must distinguish already connected targets, power-bus geometry, extended pin-access areas, disabled locations, and reusable search state. These cases are visible in [maze.c](https://github.com/RTimothyEdwards/qrouter/blob/master/maze.c).
- **C3:** The [algorithm/release notes](https://github.com/RTimothyEdwards/qrouter/blob/master/README) explain retaining search results between connections of a multi-tap net and masking the search to a restricted region—specific approaches to reducing redundant exploration.
- **C4:** Those notes describe the 2014 robustness/DRC work and the 2017 decision to keep version 1.3 stable for Qflow while branching version 1.4. This supplies explicit multi-year compatibility management.

The material is valuable even where the implementation or documented process assumptions differ from advanced-node commercial routers.

### 12. [cuhk-eda/cu-gr](https://github.com/cuhk-eda/cu-gr)

**Language/role:** C++; CUGR global routing. The verified default branch is `dac2020`; this is a research implementation associated with its DAC paper, not a claim of current product maintenance.

Study why a global router should optimize the usefulness of its routing guides to a detailed router, not just coarse-grid overflow.

- **C1:** Initial routing selects pin-access locations according to adjacent-edge accessibility, merges coincident pin locations, and constructs layer-aware routing topology. A mutex protects calls into FLUTE. These details are exposed in [InitRoute.cpp](https://github.com/cuhk-eda/cu-gr/blob/dac2020/src/single_net/InitRoute.cpp).
- **C3:** The [algorithm/module overview](https://github.com/cuhk-eda/cu-gr/blob/dac2020/README.md) describes probabilistic resource costs, combined pattern routing/layer assignment, multilevel maze routing, guide patching, and separate single-net/multi-net work. This gives a clear decomposition of the routing-quality/runtime tradeoff.

Its optional evaluation path uses Dr. CU and commercial Innovus checks. The report does not treat coarse routing success as proof of final design-rule cleanliness.

### 13. [cuhk-eda/dr-cu](https://github.com/cuhk-eda/dr-cu)

**Language/role:** C++; Dr. CU detailed routing research implementation for ISPD contest-style designs.

Its particularly useful subject is enriching shortest-path state so physical design rules influence path construction rather than only post-routing repair.

- **C1:** The maze router carries path length alongside cost, evaluates layer transitions and minimum-area-related penalties, tracks alternate pin-access vertices, and returns an explicit disconnected-grid failure. See [MazeRoute.cpp](https://github.com/cuhk-eda/dr-cu/blob/master/src/single_net/MazeRoute.cpp).
- **C3:** The [architecture overview](https://github.com/cuhk-eda/dr-cu/blob/master/README.md) separates a global database from local single-net graphs and multi-net rip-up/reroute scheduling, with sparse structures and bulk-synchronous parallelism addressing graph size and routing contention.

Treat this as a research release with documented contest coverage. The published result tables themselves include remaining violations; “correct-by-construction” algorithm descriptions should not be expanded into a blanket guarantee for arbitrary technologies.

### 14. [NVlabs/Differentiable-Global-Router](https://github.com/NVlabs/Differentiable-Global-Router)

**Language/role:** Python/PyTorch; differentiable optimization of global-routing choices, integrated with a modified CUGR2 implementation.

Study a different routing architecture: represent candidate paths and trees as probability distributions, optimize a continuous objective, then provide discrete routing choices to a conventional router.

- **C1:** The model uses grouped softmax, optional Gumbel perturbations, coupled tree/path probabilities, capacity-demand overflow, via costs, and separate continuous/discrete objective functions. Maintaining indexing and objective semantics across that relaxation is a substantive correctness problem.
- **C3:** Sparse path/via tensors, tensor products, and optional edge batching make repeated congestion evaluation suitable for accelerated numerical computation. Both criteria can be examined in [model.py](https://github.com/NVlabs/Differentiable-Global-Router/blob/main/model.py).

The [integration instructions](https://github.com/NVlabs/Differentiable-Global-Router/blob/main/README.md) explain which CUGR2 pattern-routing step its output replaces. It is retained for its own optimization implementation, not counted as an independent full copy of CUGR or a standalone detailed router. Maintenance and benchmark reproducibility were not demonstrated by execution.

## FPGA placement, routing, and timing integration

### 15. [YosysHQ/nextpnr](https://github.com/YosysHQ/nextpnr)

**Language/role:** C++ with Python interfaces; architecture-neutral, timing-driven FPGA placement and routing for multiple device families.

Study the interface between generic CAD algorithms and concrete programmable resources, including resources whose availability depends on other bindings.

- **C1:** The architecture contract specifies updates required when binding/unbinding cells to BELs, unique resource identities and locations, and conflict reporting when one allocation blocks another. These are explicit consistency obligations between the generic engine and each backend.
- **C2:** Architecture-defined identifiers, ranges, delays, BELs, wires, PIPs, and clusters allow the core algorithms to operate across different fabrics. The [architecture API](https://github.com/YosysHQ/nextpnr/blob/main/docs/archapi.md) also discusses lightweight identifiers and hierarchical naming to reduce memory overhead.

The [repository overview](https://github.com/YosysHQ/nextpnr/blob/main/README.md) distinguishes supported and experimental targets. Device support should be evaluated per backend; a common interface does not imply identical timing or packing capability for every architecture.

### 16. [verilog-to-routing/vtr-verilog-to-routing](https://github.com/verilog-to-routing/vtr-verilog-to-routing)

**Language/role:** Primarily C++; FPGA architecture/CAD research monorepo. The relevant subsystem is **VPR**, including packing, placement, routing, and implementation analysis.

Study how a configurable FPGA architecture becomes a routing-resource graph and how intermediate design representations connect successive optimization stages.

- **C2:** VPR can generate a routing-resource graph from an architecture description or load an externally constructed graph. The documented flow also offers integrated analytical packing/placement and explicit traditional sequential stages, supporting different research experiments.
- **C1:** Complex-block placement, pin/clock relationships, and SOURCE/SINK/IPIN/OPIN/channel connectivity must agree across packed netlists, placement files, and route files. The [VPR flow guide](https://github.com/verilog-to-routing/vtr-verilog-to-routing/blob/master/doc/src/vpr/basic_flow.rst) describes these representations and their identity information in enough detail to study consistency boundaries.

The [repository overview](https://github.com/verilog-to-routing/vtr-verilog-to-routing/blob/master/README.md) establishes the broader architecture-research role and distinguishes regression-tested releases from the changing development branch. This monorepo is counted once; bundled synthesis programs are not separate selections here.

### 17. [Xilinx/RapidWright](https://github.com/Xilinx/RapidWright)

**Language/role:** Java, with Python access; FPGA implementation framework bridging Vivado design checkpoints, including placement, routing, timing, and reuse of implemented modules.

Study how existing routed implementation state can be preserved, relocated, and selectively rebuilt rather than regenerating every design from scratch.

- **C2:** Its design-checkpoint interface and cached, replicated, relocatable pre-implemented modules enable specialized implementation flows. These are explained in the [project overview](https://github.com/Xilinx/RapidWright/blob/master/README.md).
- **C1 and C3:** RWRoute's resource graph distinguishes created nodes from nodes preserved for existing nets, uses atomic storage and an outstanding-work latch for asynchronous preservation, and documents a per-tile single-thread access assumption for the regular node map. This is a concrete concurrency/performance contract, not just a claim of parallelism. See [RouteNodeGraph.java](https://github.com/Xilinx/RapidWright/blob/master/src/com/xilinx/rapidwright/rwroute/RouteNodeGraph.java).

RapidWright complements the vendor ecosystem; it is not a fully independent replacement for every Vivado stage.

### 18. [PKU-IDEA/OpenPARF](https://github.com/PKU-IDEA/OpenPARF)

**Language/role:** Python, C++, and CUDA; heterogeneous-FPGA placement/routing research framework with multi-die placement support.

Study how continuous placement coordinates interact with several resource types, clock-region restrictions, discrete legalization, and cross-die interconnect objectives.

- **C1:** The placer preserves original instance dimensions for legalization after optimization inflates areas, distinguishes movable/fixed/filler ranges, retains best clock-aware solutions, and resets optimization state when objectives change. See [placer.py](https://github.com/PKU-IDEA/OpenPARF/blob/master/openparf/placement/placer.py).
- **C2 and C3:** Separate placement data, operator collections, models, and optimizers allow the Python flow to compose CPU/GPU numerical kernels. The same source makes device and precision choices explicit; the [project overview](https://github.com/PKU-IDEA/OpenPARF/blob/master/README.md) identifies the supported resource classes and multi-die extension.

The README's “production-ready” wording is a project claim, not an assessment adopted here. Its documented toolchain versions and benchmark assumptions require checking before practical reuse.

### 19. [rachelselinar/DREAMPlaceFPGA](https://github.com/rachelselinar/DREAMPlaceFPGA)

**Language/role:** Python, C++, and CUDA; GPU-accelerated heterogeneous-FPGA placement and LUT/FF packing/legalization.

This is retained separately from DREAMPlace because the FPGA-specific packing, site legality, and timing mechanisms are substantive additions rather than a renamed ASIC-placer fork.

- **C1:** The legalizer models flip-flop control sets, LUT types, site capacities, fence assignments, timing-net weights, and current/next candidate state. These constraints explain why a geometrically plausible placement may still be illegal for an FPGA. Inspect [lut_ff_legalization.py](https://github.com/rachelselinar/DREAMPlaceFPGA/blob/main/dreamplacefpga/ops/lut_ff_legalization/lut_ff_legalization.py).
- **C3:** The [algorithm overview](https://github.com/rachelselinar/DREAMPlaceFPGA/blob/main/README.md) identifies GPU acceleration of wirelength/density operators and an enhanced direct packer-legalizer, with timing criticality fed into cluster scoring. The source exposes CPU/CUDA dispatch and tensor state for these stages.

Architecture-specific slice and clock/control capacities appear in the implementation; supporting another family requires more than supplying different device dimensions.

### 20. [zslwyuan/AMF-Placer](https://github.com/zslwyuan/AMF-Placer)

**Language/role:** C++ with supporting Tcl/Python; mixed-size, timing-driven placement for heterogeneous FPGA resources.

It provides a useful CPU-oriented contrast to GPU tensor placers, particularly for connecting a lightweight timing model to global and detailed placement decisions.

- **C1:** The timing optimizer exposes incremental timing at a proposed placement location, critical-path selection, clock-region clustering, and piecewise delay models with lower bounds and region-crossing adjustments. See [PlacementTimingOptimizer.h](https://github.com/zslwyuan/AMF-Placer/blob/main/src/lib/HiFPlacer/placement/placementTiming/PlacementTimingOptimizer.h).
- **C2 and C3:** The [implementation overview](https://github.com/zslwyuan/AMF-Placer/blob/main/README.MD) separates design/device information, placement state, legalization, packing, timing, and problem solvers; it describes multithreaded placement stages and slack-guided quadratic optimization.

Material limitation: the README explicitly distinguishes the public basic implementation from an advanced version used for the paper's reported results. No paper-level quality or runtime equivalence is assumed for the public repository, and no maintainer was contacted.

## Analog placement and routing

### 21. [ALIGN-analoglayout/ALIGN-public](https://github.com/ALIGN-analoglayout/ALIGN-public)

**Language/role:** Python and C++; hierarchical analog layout generation, including constraint-aware placement and global, detailed, and power routing.

Study how designer intent becomes checked geometric constraints across a hierarchy of analog blocks, rather than treating analog layout as ordinary standard-cell placement.

- **C1:** Constraint validators resolve instance/port names and enforce parameter conditions; hard constraints translate into solver expressions. For example, ordering and abutment become bounding-box inequalities/equalities, and ordering is explicitly distinct from alignment. See [constraint.py](https://github.com/ALIGN-analoglayout/ALIGN-public/blob/master/align/schema/constraint.py).
- **C2:** The schema separates soft, hard, and user-level constraints, while the physical flow separates hierarchical storage, common-centroid capacitor layout, analog placement, and routing. The [hierarchical P&R guide](https://github.com/ALIGN-analoglayout/ALIGN-public/blob/master/PlaceRouteHierFlow/README.md) explains symmetry, shielding, parallel-routing constraints, and coordinate transformations.

That subsystem guide also records limited process/test coverage and unfinished work. Its architecture is useful study material without implying arbitrary-PDK support.

### 22. [magical-eda/MAGICAL](https://github.com/magical-eda/MAGICAL)

**Language/role:** Python and C++ components; hierarchical analog layout synthesis integrating constraint generation, device generation, placement, and routing. Treat it as a research/reference flow; GitHub metadata reports the latest push in 2024, so its README's undated active-development statement is not repeated as a current maintenance claim.

Study the physical and hierarchical state that must cross the boundaries between independently implemented analog tools.

- **C1:** The P&R integration transfers a placement symmetry axis and grid origin to the router, checks routing failure, reloads routed geometry, and expands block boundaries onto the placement grid after wires change their extent. These are essential coordinate and hierarchy invariants, visible in [PnR.py](https://github.com/magical-eda/MAGICAL/blob/master/flow/python/PnR.py).
- **C2:** The flow coordinates a design database and technology database with separately maintained constraint, placement, routing, and device-generation components. The [repository overview](https://github.com/magical-eda/MAGICAL/blob/master/README.md) explains this composition and the device/net symmetry input model.

The example flow contains technology-specific assumptions, and the README explicitly identifies an ADC example with routing problems. Submodule engines are not separately counted in this selection.

## Search coverage and limits

Discovery used more than six distinct live-web formulations: integrated ASIC physical implementation and timing; vendor-neutral FPGA P&R; GPU analytical placement; analog hierarchical/symmetry layout; standalone incremental/parallel STA; global versus detailed routing; historical Qflow placement/routing; Java and Rust implementation alternatives; multi-die FPGA placement; reinforcement-learning floorplanning; and archived clock-tree tools. Follow-up searches targeted AMF-Placer, Rsyn, iEDA, Coloquinte, and newer GPU timing references. Later searches increasingly returned already-covered systems, tutorial applications, forks, and out-of-scope PCB tools.

Every retained canonical repository URL was checked through the GitHub API, including its default branch and archived flag. Each entry also has an opened implementation or architectural source beyond repository metadata; the additional source is not just the same README fetched under a different URL. No retained repository was marked archived at the time of checking. Research releases and legacy implementations are identified explicitly; a push date is used only as a limited maintenance observation, never to establish C4.

Important exclusions and counting decisions:

- OpenROAD's integrated placement, routing, and clock-tree components are represented by its monorepo. The retired, archived [standalone TritonCTS repository](https://github.com/The-OpenROAD-Project/TritonCTS) explicitly directs readers to its successor; it is not an additional selection.
- [Coloquinte's old repository](https://github.com/Coloquinte/Coloquinte_placement) says the placer became Etesian in Coriolis. Its algorithms are represented by Coriolis, avoiding a moved-project duplicate.
- OpenSTA is represented by its declared canonical Parallax upstream. Tatum and DREAMPlaceFPGA remain separate because their independent library interface or substantial FPGA implementation provides distinct study value.
- Searches for Rust alternatives predominantly surfaced PCB routers, including projects named “fastroute” unrelated to OpenROAD's IC global router. These were excluded rather than used to manufacture language diversity. Pure synthesis, reverse-engineered device databases, benchmark-only repositories, and educational RTL-to-GDS exercises were also excluded.

This was read-only source/document research: no candidate code was run, no dependencies were installed, and no large repositories were cloned. Performance mechanisms are grounded in the inspected architecture and implementation, but no numerical speedup, signoff equivalence, clean build, full regression pass, or uniform code quality is independently asserted. Proprietary evaluation tools, incomplete public artifacts, process-specific assumptions, and differences between public code and paper versions remain material limits where noted. The learning value and criterion assignments are reasoned assessments based on the cited evidence.
