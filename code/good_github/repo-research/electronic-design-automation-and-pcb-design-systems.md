# Electronic design automation and PCB design systems

Research date: 2026-10-09.

This report selects 24 GitHub codebases for studying the engineering of electronic design tools: schematic and PCB editors, routing and fabrication preparation, programmable circuit construction, analog simulation and model compilation, RTL synthesis and simulation, FPGA implementation, and ASIC physical design and verification. It includes large integrated systems and smaller specialist engines. Hardware designs, component collections, PDK data alone, tutorials, and thin tool wrappers are outside the selection.

Each repository heading links to its verified canonical GitHub location. The linked implementation and documentation sources below were opened and read. Criteria assignments are engineering judgments grounded in those sources, rather than endorsements of every component or claims of independently measured performance. Moving branch links describe the inspected material, not immutable snapshots. Maintenance is not inferred from stars or repository age; mirrors and substantive continuations are identified explicitly.

Criteria legend:

- **C1 — Difficult correctness:** invariants, numerical semantics, concurrency, malformed inputs, or consequential failure modes.
- **C2 — Reusable abstractions:** substantial models, APIs, intermediate representations, or extension mechanisms supporting multiple uses.
- **C3 — Performance with structure:** concrete computational or memory constraints addressed through understandable architecture or algorithms.
- **C4 — Sustained evolution:** development across years accompanied by compatibility work, testing, or explicit complexity management.

## PCB editors, routing, and manufacturing preparation

### 1. [KiCad/kicad-source-mirror](https://github.com/KiCad/kicad-source-mirror)

**Language/role:** C++; integrated schematic capture, PCB layout, routing, and manufacturing tools. **Official mirror:** development is hosted on GitLab; the GitHub repository explicitly describes itself as the development mirror and does not accept GitHub pull requests.

Study the relationship between interactive editing, a persistent board model, and undoable transactions. The relevant subsystems are `pcbnew`, `eeschema`, the shared tool framework, and QA infrastructure; the suite counts once.

- **C1:** Editing multiple board objects requires coordinated ownership and rollback. `BOARD_COMMIT` records original states before modification, retains removed objects for undo, and distinguishes pushing a change from abandoning it. Tool reset also releases references that become invalid when the model changes.
- **C2:** Actions, scopes, event transitions, and coroutine-based interactive tools provide a shared extension structure for both schematic and board editors. These are concrete abstractions for implementing many editing operations, not simply a collection of menu handlers.

Entry points: [tool framework and commit semantics](https://dev-docs.kicad.org/en/components/tool-framework/index.html); [testing and replayable push-and-shove router diagnostics](https://dev-docs.kicad.org/en/components/testing/index.html).

### 2. [LibrePCB/LibrePCB](https://github.com/LibrePCB/LibrePCB)

**Language/role:** Primarily C++, with Rust components; integrated schematic and PCB design system.

Useful for studying how a CAD application makes physical quantities and component identity explicit in its domain model. Its library representation separates electrical meaning from symbols, packages, and purchasable devices.

- **C1:** The common `Length` type stores dimensions in integer nanometers and documents precision loss at floating-point conversion boundaries. Library references additionally depend on immutable UUIDs and stable pin interfaces; incompatible changes require new elements rather than silently changing existing identities.
- **C2:** Symbols, packages, abstract components, and concrete devices are separately reusable, including across library boundaries. The same dimension abstraction is used throughout schematics, footprints, and layouts.

Entry points: [length representation and conversions](https://raw.githubusercontent.com/LibrePCB/LibrePCB/master/libs/librepcb/core/types/length.h); [library specification and dependency invariants](https://developers.librepcb.org/df/d4f/doc_library.html). The separate [file-format versioning specification](https://developers.librepcb.org/d1/d69/doc_versioning.html) is useful context for migration behavior, but a compatibility policy alone is not counted as C4 here.

### 3. [horizon-eda/horizon](https://github.com/horizon-eda/horizon)

**Language/role:** C++/GTKmm/OpenGL; integrated PCB design and parts management.

Study a unified editor whose document model, tools, and rendering are connected through a core layer. Horizon includes a KiCad-derived router, so that router is not treated as an independently invented algorithm here; the wider editor and pool architecture justify the entry.

- **C1:** The core exists partly to keep schematic and netlist modifications synchronized. This is a meaningful model-consistency problem: graphical edits must preserve the electrical representation.
- **C2:** The interactive manipulator serves symbols, schematics, padstacks, packages, and boards. Rendering hooks also serve Gerber export, 3D preview, and DRC, while the pool composes reusable units and entities into parts.
- **C3:** The canvas converts drawing objects into segments and triangles uploaded to the GPU, exposing a clear boundary between editable objects and accelerated rendering.

Entry points: [theory of operation](https://docs.horizon-eda.org/en/latest/theory-of-operation.html); [pool composition rationale](https://docs.horizon-eda.org/en/latest/pool-why.html).

### 4. [freerouting/freerouting](https://github.com/freerouting/freerouting)

**Language/role:** Java; PCB autorouting and route optimization with GUI and headless interfaces.

Study a geometric search engine that must mutate a board while preserving connectivity and design rules. The architecture document distinguishes initial connection finding from subsequent route-quality optimization.

- **C1:** Maze search respects clearances, permitted layers, and via rules. Optimization can rip up and reroute geometry, retaining an improvement or restoring the previous state. Passes also stop when they cannot make useful progress.
- **C2:** Board storage, rule models, planar geometry, DRC, parsers, and routing stages are separate packages. ArchUnit rules explicitly constrain dependencies on GUI and API layers.
- **C3:** Spatial search trees support clearance/overlap queries; optimization can evaluate multiple candidates in parallel. The document explains the boundaries between search costs, route scoring, and board mutation.

Entry point: [architecture, package map, and routing algorithm](https://github.com/freerouting/freerouting/blob/master/docs/architecture.md). These are documented mechanisms, not a claim that an autorouter will find a legal solution for every board.

### 5. [yaqwsx/KiKit](https://github.com/yaqwsx/KiKit)

**Language/role:** Python; KiCad panelization and fabrication automation library, CLI, and plugin.

A useful smaller system for studying the geometry behind manufacturing preparation. Its panel representation must connect irregular board substrates, tabs, rails, and cut paths while retaining the original boards' electrical identities.

- **C1:** Tab generation depends on oriented partition lines and ray/substrate intersections. The documentation explains rejected intersections, half-tab merging, and why future framing must be represented by boundary substrates. The repository also explains net renaming between repeated board instances to avoid false electrical connections.
- **C2:** The `Panel` abstraction supports scripted board placement, substrate construction, tabs, and multiple cut representations. CLI presets expose the same operations for repeatable workflows.

Entry points: [tab-generation algorithm and boundary cases](https://github.com/yaqwsx/KiKit/blob/master/docs/panelization/tabs.md); [panelization examples and selection semantics](https://github.com/yaqwsx/KiKit/blob/master/docs/panelization/examples.md).

### 6. [gerbv/gerbv](https://github.com/gerbv/gerbv)

**Language/role:** C; Gerber, Excellon drill, and assembly-data viewing and manipulation. **Continuation:** the repository identifies itself as a maintained fork of the former gEDA utility, with its own bug-fix evolution and releases; the older implementation is not counted separately.

Study the interpretation of manufacturing files as a stateful plotting language and the separation of reusable parsing from the desktop viewer.

- **C1:** The Gerber parser tracks aperture state, unit conversions, absolute versus incremental coordinates, omitted zeros, and aperture-block transitions. These interacting state changes make apparently simple coordinate input numerically and semantically demanding.
- **C2:** `libgerbv` exposes the core parsing, rendering, editing, and exporting functionality independently of the viewer, allowing other applications to work with manufacturing data.

Entry points: [Gerber parser implementation](https://raw.githubusercontent.com/gerbv/gerbv/develop/src/gerber.c); [libgerbv documentation](https://gerbv.github.io/doc/index.html).

## Circuit construction as code

### 7. [devbisme/skidl](https://github.com/devbisme/skidl)

**Language/role:** Python; reusable circuit descriptions, electrical-rule checking, and netlist generation.

Study how Python operators and object composition become electrical connectivity rather than merely textual netlist templates. The project is especially useful for understanding the semantics of pins, nets, buses, and hierarchical subcircuits.

- **C1:** Connecting normal nets through a pin merges their connectivity, whereas the special no-connect net has deliberately different behavior. ERC also distinguishes pin functions and drive levels, so power-delivery errors and intentional unconnected pins need separate handling.
- **C2:** Parts, nets, buses, and reusable subcircuits support parameterized designs. Custom `erc_assert` checks let applications add requirements beyond the built-in rules.

Entry point: [manual, especially no-connect semantics, drive levels, hierarchy, and custom ERC](https://devbisme.github.io/skidl/). These sections contain executable API examples and behavioral rules beyond the introductory feature list.

### 8. [atopile/atopile](https://github.com/atopile/atopile)

**Language/role:** Python and Zig core components; electronics language, compiler, and KiCad-oriented design toolchain.

Study the `faebryk` graph model underlying reusable electronics descriptions. The repository combines language/toolchain work with the graph implementation; these are counted as one system.

- **C1:** The node implementation distinguishes fields declared in Python, fields bound into a type graph, and children bound to an instance graph. Access at the wrong stage raises an invalid-state error; binding checks attribute types and reports unresolved paths with graph context. These are concrete safeguards against incorrect elaboration and reference resolution.
- **C2:** Nodes, child fields, graph edges, and traits provide a reusable composition system underneath the `.ato` modules and interfaces described by the repository. An engineer can study how domain objects are constructed through a typed graph rather than ad hoc nested dictionaries.

Entry points: [node and binding implementation](https://raw.githubusercontent.com/atopile/atopile/main/src/faebryk/core/node.py); [core source layout](https://github.com/atopile/atopile/tree/main/src/faebryk/core). This entry does not infer solver completeness from the project's validation claims.

### 9. [tscircuit/core](https://github.com/tscircuit/core)

**Language/role:** TypeScript; compilation of React-style electronics descriptions into Circuit JSON.

Study the intermediate-representation and lifecycle layer of programmable PCB design. This entry is specifically the core compiler, not every separate tscircuit package or its external routing solvers.

- **C1:** Rendering phases wait for declared asynchronous dependencies, including footprint fetching and trace routing before dependent geometry. Dirty-state propagation marks later phases and ancestors, making invalidation and asynchronous ordering explicit correctness concerns.
- **C2:** React elements become component class instances; ordered rendering phases produce source, schematic, and PCB-related data in a shared Circuit JSON database. Removal has corresponding phase hooks, giving a reusable lifecycle for different component types.
- **C3:** Initialized phases invoke update hooks only when dirty, avoiding unnecessary component work. A benchmark workflow measures expensive calls, while exported JSON inputs isolate routing, packing, and schematic-trace algorithms for investigation.

Entry points: [rendering, invalidation, and asynchronous phase implementation](https://github.com/tscircuit/core/blob/main/lib/components/base-components/Renderable.ts); [development guide and algorithm reproducers](https://github.com/tscircuit/core/blob/main/docs/DEVELOPMENT.md).

## Analog design, circuit simulation, and device-model compilation

### 10. [StefanSchippers/xschem](https://github.com/StefanSchippers/xschem)

**Language/role:** C and Tcl/Tk; hierarchical schematic capture for analog, ASIC, and VLSI design. **Official mirror arrangement:** its README says the GitHub and Codeberg repositories are exact mirrors.

Study the connection between graphical primitives, reusable symbols, component properties, and several netlisting dialects. It is particularly relevant to tools that must preserve hierarchy while generating simulator-specific output.

- **C1:** The documented file format has version-sensitive records and embedded-symbol rules. Embedded definitions must follow the corresponding instance, and shared instances refer to one embedded definition. Correct parsing and reference handling are essential to preserving a circuit.
- **C2:** Property strings and separate SPICE, Verilog, VHDL, and other netlisting attributes allow reusable symbols to participate in several downstream flows. The developer manual exposes both the serialization model and its implementation-facing semantics.

Entry point: [developer information, file format, symbols, and netlisting properties](https://xschem.sourceforge.io/stefan/xschem_man/developer_info.html).

### 11. [ra3xdh/qucs_s](https://github.com/ra3xdh/qucs_s)

**Language/role:** C++/Qt; schematic capture, simulation control, and results visualization. **Substantive derivative:** based on Qucs, but its multi-SPICE backend implementation makes it more than an unchanged fork; the original Qucs is not also listed.

Study the difficult boundary between a shared schematic/UI model and simulators with different input and output conventions.

- **C1:** The shared kernel explicitly handles real/complex output and adaptive transient sweeps. Its resampling routine is documented to intersect time ranges and interpolate unequal Xyce time series onto a common grid before merging them, addressing a concrete numerical-shape mismatch.
- **C2:** `AbstractSpiceKernel` centralizes netlist generation, simulator execution, output conversion, and schematic checks, while Ngspice and Xyce backends specialize it. This is a substantial adapter architecture rather than a command launcher alone.

Entry points: [shared kernel interface and resampling contract](https://raw.githubusercontent.com/ra3xdh/qucs_s/current/qucs/extsimkernels/abstractspicekernel.h); [backend implementation directory](https://github.com/ra3xdh/qucs_s/tree/current/qucs/extsimkernels).

### 12. [Xyce/Xyce](https://github.com/Xyce/Xyce)

**Language/role:** C++; parallel SPICE-compatible analog circuit simulator.

Study the separation of device physics, nonlinear convergence, time integration, and linear algebra. The repository notes that its master history was re-rooted at the 7.9 release; its current commit count therefore should not be interpreted as the project's age.

- **C1:** A developer explanation describes both vector-wide and device-level convergence criteria, plus voltage limiting that differs materially from a conventional scalar line search. These details matter when numerical convergence must also represent a physically meaningful circuit solution.
- **C2:** Device loads keep the differential-algebraic equation's charge, static, and source contributions separate, allowing much of the same device-loading implementation to support different analysis types.
- **C3:** The developers identify device evaluation and the Newton linear solve as distinct performance bottlenecks, and explain the role of distributed-memory MPI and problem-dependent solver choices without promising universal scaling.

Entry points: [numerical formulation and convergence discussion](https://github.com/Xyce/Xyce/discussions/106); [developer discussion of parallelism and solver costs](https://github.com/Xyce/Xyce/discussions/90).

### 13. [OpenVAF/OpenVAF-Reloaded](https://github.com/OpenVAF/OpenVAF-Reloaded)

**Language/role:** Rust, with LLVM and a C-facing interface; Verilog-A device-model compiler. **Community continuation:** its README documents the fork's 2024 origin, model-correctness fixes, and OSDI 0.4 extensions. The original OpenVAF and its mirror are not counted separately.

Study a compiler whose output is a numerical model library embedded inside circuit simulators, where ABI layout and mathematical contributions are both correctness concerns.

- **C1:** The internal representation distinguishes resistive and reactive Jacobian contributions, collapsed nodes, parameter-given flags, and model/instance storage. Descriptor-size handling is necessary when traversing arrays across OSDI interface versions.
- **C2:** OSDI exposes model metadata, nonlinear inputs, and Jacobian-loading operations through a reusable simulator interface. Offset-based loading supports analyses that evaluate one circuit at multiple time points.

Entry point: [model storage and OSDI internals](https://github.com/OpenVAF/OpenVAF-Reloaded/blob/mob/internals.md). The repository's compatibility explanation requires simulator-side adaptation; it is not an assertion of unconditional binary compatibility.

## RTL synthesis, simulation, and FPGA implementation

### 14. [YosysHQ/yosys](https://github.com/YosysHQ/yosys)

**Language/role:** C++; RTL synthesis framework for FPGA, ASIC, and formal-analysis workflows.

Study how a compiler preserves hardware semantics while lowering behavioral processes and memories into netlists. The relevant subsystem is Yosys itself, including RTLIL, frontends, transformation passes, and backends; bundled dependencies are not separate entries here.

- **C1:** RTLIL must preserve bus direction and indexing, synchronization conditions, and next-state assignments. Its identifier rules also prevent generated names from colliding with user names, and enforce invalid-identifier checks.
- **C2:** Frontends, passes, and backends share the same design/module/cell/wire/process representation. Scripted pass composition and parameter-specialization callbacks support many synthesis targets and analyses.

Entry points: [RTLIL representation and semantic examples](https://github.com/YosysHQ/yosys/blob/main/docs/source/yosys_internals/formats/rtlil_rep.rst); [changelog covering compatibility repairs, semantic checks, and pass evolution](https://github.com/YosysHQ/yosys/blob/main/CHANGELOG). The latter is useful maintenance evidence, but no calendar-age claim is inferred solely from version numbers.

### 15. [verilator/verilator](https://github.com/verilator/verilator)

**Language/role:** C++; SystemVerilog compiler, simulator-model generator, and lint system.

Study how language semantics constrain optimization and parallel execution. Its internals explain the entire route from AST transformations to scheduling and generated C++ models.

- **C1:** Scheduling must reproduce the relevant SystemVerilog event regions and restore the invariant that combinationally driven values are consistent with their logic after evaluation. Dependency cycles and different process classes need distinct handling.
- **C3:** Static ordering reduces repeated evaluation; the multithreaded implementation groups data by the macro-tasks that access it and aligns groups to avoid false sharing without constructing a prohibitively large pairwise graph.
- **C2:** AST visitors, reusable graph types, and a separate combinational data-flow representation provide structured foundations for numerous optimization passes.

Entry point: [internals: compiler passes, scheduling, multithreading, and regression/fuzz testing](https://github.com/verilator/verilator/blob/master/docs/internals.rst).

### 16. [YosysHQ/nextpnr](https://github.com/YosysHQ/nextpnr)

**Language/role:** C++, with Python tooling; timing-driven FPGA placement and routing.

Study an architecture-independent implementation engine with explicit contracts for device-specific backends. It complements VTR below: nextpnr's FAQ emphasizes implementation for available FPGA devices, while VTR emphasizes architecture and algorithm research.

- **C1:** Binding and unbinding a cell, wire, or routing switch must update both resource occupancy and the associated cell/net records. Availability and conflict queries encode exclusivity relationships that go beyond checking whether one resource is occupied.
- **C2:** The architecture API abstracts basic elements, wires, switches, delay estimates, groups, and device-specific metadata. Custom range types and default implementations let backends reuse common algorithms.
- **C3:** The API explicitly favors lightweight identifiers and hierarchical interned names to avoid storing full resource names throughout large device databases.

Entry points: [architecture API and binding invariants](https://github.com/YosysHQ/nextpnr/blob/main/docs/archapi.md); [terminology and project scope](https://github.com/YosysHQ/nextpnr/blob/main/docs/faq.md).

### 17. [verilog-to-routing/vtr-verilog-to-routing](https://github.com/verilog-to-routing/vtr-verilog-to-routing)

**Language/role:** Primarily C/C++ with Python flow tooling; FPGA architecture and CAD research framework.

Focus on VPR and the VTR evaluation infrastructure. The monorepo counts once, including its associated packing, placement, routing, and analysis flow.

- **C1:** Routing must realize netlist connectivity using the architecture's routing-resource graph; packing and placement must remain consistent with legal complex blocks and physical sites.
- **C2:** Architecture descriptions and externally supplied routing-resource graphs let the implementation machinery evaluate different FPGA fabrics. Analysis can also run separately on saved packing, placement, and routing results.
- **C3:** The developer guide distinguishes broad functional regression tests from quality-of-results and performance evaluation, measuring runtime and memory as well as circuit quality. This makes algorithmic tradeoffs inspectable instead of conflating every changed result with a failure.

Entry points: [VPR flow and resource representation](https://github.com/verilog-to-routing/vtr-verilog-to-routing/blob/master/doc/src/vpr/basic_flow.rst); [developer testing and evaluation guide](https://github.com/verilog-to-routing/vtr-verilog-to-routing/blob/master/README.developers.md).

## ASIC physical design, verification, and design-flow infrastructure

### 18. [The-OpenROAD-Project/OpenROAD](https://github.com/The-OpenROAD-Project/OpenROAD)

**Language/role:** Primarily C++, with Tcl/Python interfaces; integrated ASIC physical-design application.

Study integration of placement, clock-tree construction, routing, extraction, and optimization around a common database. OpenDB and the integrated routing/placement subsystems are included in this single entry.

- **C2:** The developer guide defines one application, one process, and one database, with individual tools packaged behind classes, namespaces, and controlled initialization interfaces. Shared readers and database access prevent each tool from inventing its own transfer format.
- **C3:** Avoiding process launches and file-based tool communication reduces orchestration overhead and repeated data movement. The guide explicitly ties these architectural choices to efficient flow execution.
- **C1:** The same guide addresses non-convergent optimization: a pass should detect futile iteration, stop with a diagnostic, and preserve the ability to obtain downstream flow metrics. This is a documented design requirement, not proof that every pass already satisfies it.

Entry point: [developer guide and tool-integration architecture](https://github.com/The-OpenROAD-Project/OpenROAD/blob/master/docs/contrib/DeveloperGuide.md).

### 19. [The-OpenROAD-Project/OpenSTA](https://github.com/The-OpenROAD-Project/OpenSTA)

**Language/role:** C++ and Tcl; reusable static timing-analysis engine.

Study dependency invalidation in an incremental numerical graph system. Although OpenROAD incorporates OpenSTA, it remains an independently reusable repository and API; this entry focuses on timing-engine internals rather than recounting the physical-design flow.

- **C1:** Changing a false-path constraint must invalidate arrival and required times. The API warns that recomputing delays directly through a component can leave dependent arrival times incorrect; the coordinating `Sta` interface exists to preserve these relationships. Readers also normalize physical quantities into common units.
- **C2:** Network, timing graph, constraints, delay calculation, parasitics, and search are separate components. The network adapter can use an embedding application's objects without requiring them to inherit STA classes.
- **C3:** That adapter avoids constructing and maintaining a second copy of the host netlist, an explicit memory and synchronization-cost decision.

Entry point: [STA API, component coordination, units, and network adapters](https://github.com/The-OpenROAD-Project/OpenSTA/blob/master/doc/StaApi.md).

### 20. [KLayout/klayout](https://github.com/KLayout/klayout)

**Language/role:** C++ with Ruby/Python scripting; IC layout viewing, editing, generation, and verification infrastructure.

Study a hierarchical geometry database that is useful both inside an editor and as an independent programmable layout engine.

- **C1:** Coordinates are integer database units, while floating-point geometry uses physical units. Conversion rounds onto the database grid, and changing the database unit rescales geometry. These semantics must remain correct across file import, hierarchy transformations, and generated layouts.
- **C2:** Layouts, cells, instance arrays, shape collections, and geometric primitives form a reusable object model. Standalone layouts need no view; linked library cells use proxy semantics that differ from ordinary editable cells.
- **C3:** Property sets are deduplicated behind integer IDs rather than copied onto every shape or instance. Parameterized-cell layouts are cached by parameter set, avoiding repeated execution of their geometry-generation code.

Entry point: [database API and representation semantics](https://www.klayout.de/doc/programming/database_api.html). This is a guide to the database subsystem, not an independent assessment of every DRC/LVS rule implementation.

### 21. [RTimothyEdwards/magic](https://github.com/RTimothyEdwards/magic)

**Language/role:** C and Tcl; VLSI layout editing and physical-verification infrastructure.

Study the corner-stitched tile representation, an unusually direct example of a geometric data structure shaping the surrounding CAD architecture.

- **C1:** Tiles store one corner plus neighbor stitches, from which other boundaries are derived. Plane sentinels must support coordinate transformations without integer overflow. The header also explains why a temporary split-side flag must not mutate stored tile types during searches, since that would obstruct parallel searches.
- **C2:** The tile/plane interface exposes reusable split, join, point-search, and geometry operations for higher-level layout subsystems, representing both material and empty space.
- **C3:** Search hints and optional memory-mapped tile allocation show concrete locality/allocation concerns alongside the geometry abstraction.

Entry point: [tile structures, plane invariants, and public operations](https://raw.githubusercontent.com/RTimothyEdwards/magic/master/tiles/tile.h).

### 22. [RTimothyEdwards/netgen](https://github.com/RTimothyEdwards/netgen)

**Language/role:** C and Tcl; netlist comparison and layout-versus-schematic checking, distinct from the unrelated mesh generator with the same name.

Study equivalence checking when circuits contain hierarchy, interchangeable pins, device properties, and black-box cells.

- **C1:** The LVS orchestration tracks property errors, unmatched subcircuits, and top-level pin mismatches separately. It selectively flattens unmatched hierarchy while preserving explicit no-flatten and black-box behavior; a structural match alone does not erase these other failure conditions.
- **C2:** Multiple netlist readers and configurable rules for device classes, subcircuit correspondence, and pin permutations support different technologies and extraction flows.
- **C4:** The repository README documents the 2003 Tcl rework, 2007 expansion of device/property/hierarchy handling, and 2014 stable/development-series separation. This is evidence of sustained interface and complexity management, rather than just an old creation timestamp.

Entry points: [LVS implementation](https://raw.githubusercontent.com/RTimothyEdwards/netgen/master/tcltk/netgen.tcl.in); [repository documentation and revision history](https://github.com/RTimothyEdwards/netgen).

### 23. [VLSIDA/OpenRAM](https://github.com/VLSIDA/OpenRAM)

**Language/role:** Python; SRAM compiler producing layout, circuit netlists, characterization, and integration views.

Study a specialized hardware generator that must make multiple representations of a memory agree. Its technology abstraction is a useful comparison with generic place-and-route frameworks.

- **C1:** The base design checks custom-cell pin names against SPICE data, maps physical pin geometry from GDS, and enforces a fixed read/write-port ordering. These are concrete cross-representation invariants, not simply filename conventions.
- **C2:** Technology packages supply reusable hard cells, corresponding SPICE netlists, layer maps, device models, and DRC/LVS rules. Shared design classes provide physical constants and analytical models to generated modules.

Entry points: [base design and pin/port contracts](https://raw.githubusercontent.com/VLSIDA/OpenRAM/stable/compiler/base/design.py); [technology-porting interface](https://github.com/VLSIDA/OpenRAM/blob/stable/PORTING.md).

### 24. [librelane/librelane](https://github.com/librelane/librelane)

**Language/role:** Python, Tcl, and Nix packaging; reusable ASIC implementation-flow infrastructure. **Successor:** based on OpenLane 2; older OpenLane and ChipFoundry-specific repositories are not additional entries.

Study reproducible orchestration around expensive external EDA tools. Its own contribution is the flow/state/configuration model, rather than the algorithms inside the tools it invokes.

- **C1:** A step consumes a configuration and state and returns a new state. The architecture forbids in-place input modification and undeclared filesystem dependencies, and fixes random seeds; configuration immutability is programmatically enforced. It explicitly acknowledges acceptable nondeterminism such as timestamps.
- **C2:** `State`, `Step`, `Flow`, and configuration objects separate design artifacts, atomic tool execution, and orchestration. Custom Python flows and plugins can recombine those pieces beyond the provided reference flows.

Entry points: [architectural contracts](https://librelane.readthedocs.io/en/latest/reference/architecture.html); [successor history and compatibility changes](https://github.com/librelane/librelane/blob/main/Changelog.md).

## Coverage, search process, and limitations

Discovery used substantially more than six distinct live-search formulations. Search angles included integrated PCB editors and their architectures; external PCB autorouters; Python and TypeScript circuit construction; panelization and fabrication geometry; Gerber/CAM parsers; SPICE and parallel circuit simulation; Verilog-A compiler continuations; RTL synthesis and intermediate representations; FPGA architecture research versus device implementation; ASIC placement/routing; timing engines; and layout-versus-schematic verification. Follow-up searches checked source locations, repository ownership, and successor/mirror status. Late broad PCB/CAM searches increasingly returned wrappers, small viewers, tutorial projects, or already represented systems; Gerbv was retained as a distinct manufacturing-data implementation.

The selection includes C, C++, Java, Python, TypeScript, Rust, Zig, and Tcl-centered work, spanning desktop applications, numerical engines, compilers, geometry libraries, and orchestration frameworks. C1/C2 are the most common supported criteria. C3 is credited for specific structures or performance-evaluation mechanisms, without adopting advertised speedup figures. C4 is applied conservatively where the inspected material establishes both years of evolution and concrete complexity management.

Ngspice was investigated but not retained: its README points to SourceForge, and the search found multiple GitHub copies, including the explicitly labeled [imr/ngspice mirror](https://github.com/imr/ngspice). The investigation did not establish sufficiently clear official GitHub-mirror provenance to include it under this report's rule. That is a hosting/provenance limitation, not a judgment of simulator quality. Ringdove/pcb-rnd likewise remains outside this GitHub-focused selection because an official substantive GitHub mirror was not established. Generic electromagnetic solvers and photonic-layout frameworks were not expanded into separate coverage here.

No unchanged forks, component-only libraries, generated wrappers, awesome lists, or individual board designs are counted. KiCad and Xschem are explicitly labeled mirrors; Qucs-S, Gerbv, OpenVAF-Reloaded, and LibreLane are identified continuations or substantive derivatives, with only one implementation lineage representative counted in each case. Repository pages and additional primary documentation/source material were inspected, but the projects were not cloned, built, benchmarked, or tested locally. The report is a source-reading selection guide, not a certification of fabrication readiness or uniform code quality.
