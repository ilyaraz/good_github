# Hardware description language simulators

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing HDL simulation engines or substantive simulation compilers: Verilog/SystemVerilog and VHDL kernels, SystemC and Bluespec execution, native simulators for embedded HDLs, hardware-IR simulators, and heterogeneous acceleration. Netlist simulation is included where its relationship to HDL designs is explicit. Verification frameworks, waveform viewers, parser-only projects, and thin wrappers around another simulator are outside scope. Monorepos are counted once, with the relevant subsystem identified.

The entries are engineering study recommendations, not a claim of complete language conformance, current production readiness, or uniformly exemplary code. Criteria judgments are inferences grounded in the cited implementation and documentation. Archived projects and specialized research implementations remain useful studies when their limitations are explicit.

## Criteria legend

- **C1 — Difficult correctness:** scheduling invariants, concurrency, numerical semantics, or consequential failure modes.
- **C2 — Reusable abstractions:** substantial representations, execution interfaces, or composition mechanisms serving multiple designs and use cases.
- **C3 — Performance with structure:** concrete performance constraints addressed through an understandable architecture.
- **C4 — Sustained evolution:** evidence spanning years of compatibility work, testing, or complexity management. Repository age alone does not qualify.

## Standards-oriented language kernels and compiled simulators

### 1. [verilator/verilator](https://github.com/verilator/verilator)

**Language/role:** C++; compiled Verilog/SystemVerilog simulation, emitting C++ or SystemC models.

Study the compiler-to-runtime boundary: Verilator refines an AST through analysis and transformation passes, then emits an execution schedule. Its current architecture includes timing and event scheduling; describing it only as a cycle-based simulator would miss substantial implementation work.

- **C1:** The scheduling design explicitly handles Active and NBA regions and states invariants about combinational values being settled at evaluation boundaries. Clocked, combinational, and hybrid logic require different ordering; cycles cannot simply be topologically sorted away.
- **C3:** Static ordering and trigger domains reduce unnecessary evaluation while preserving those dependencies. The visitor and graph infrastructure makes the optimization machinery inspectable rather than hiding it behind an opaque generated runtime.

**Entry point:** [Compiler internals and scheduling design](https://github.com/verilator/verilator/blob/master/docs/internals.rst), especially the scheduling, ordering, and graph sections. These describe both the semantic obligations and the mechanisms used to reduce runtime work.

### 2. [steveicarus/iverilog](https://github.com/steveicarus/iverilog)

**Language/role:** C/C++; Verilog compiler and the `vvp` simulation virtual machine.

The repository is useful for following a language implementation from parsing and elaboration into an event runtime. The [repository documentation](https://github.com/steveicarus/iverilog) distinguishes parsed forms, scope/parameter elaboration, netlists, and selectable code-generation targets.

- **C1:** `vvp` keeps separate queues for active, inactive, nonblocking-assignment, read/write synchronization, read-only synchronization, and deletion events within a time step. A separate initialization queue addresses time-zero behavior. Event subclasses also distinguish four-state vectors, real values, and process execution.
- **C2:** The compiler's elaborated netlist and backend boundary separate language processing from executable representation. Within the runtime, typed events share scheduling machinery rather than each implementing an independent simulation loop.

**Entry point:** [vvp/schedule.cc](https://github.com/steveicarus/iverilog/blob/master/vvp/schedule.cc). Its queue structures, scheduling functions, and event classes expose the executable meaning of assignment and synchronization semantics.

### 3. [ghdl/ghdl](https://github.com/ghdl/ghdl)

**Language/role:** Primarily Ada, with C and other supporting code; VHDL analysis, elaboration, native compilation, and simulation runtime.

GHDL offers a particularly direct study of translating language-standard simulation rules into runtime code.

- **C1:** The runtime's simulation-cycle implementation follows driver updates, signal propagation, process wakeups, postponed versus nonpostponed processes, and advancement through delta cycles and physical time. Language-reference annotations make the connection between specification and implementation unusually accessible.
- **C4:** The release history documents VHDL-2008 and verification-library compatibility work in 2019–2020, later elaboration and backend changes, Windows and VUnit-related fixes in 2024–2025, and initial VHDL-2019 work in 2026. This is evidence of sustained compatibility management rather than merely an old repository.

**Entry points:** [grt-processes.adb](https://github.com/ghdl/ghdl/blob/master/src/grt/grt-processes.adb) for the simulation cycle; [NEWS.md](https://github.com/ghdl/ghdl/blob/master/NEWS.md) for dated evolution. Backend availability and newer-language coverage vary by version; the history should be read alongside the runtime.

### 4. [nickg/nvc](https://github.com/nickg/nvc)

**Language/role:** C; VHDL compiler and LLVM-backed native/JIT simulation runtime. The repository also describes experimental newer-language and Verilog work.

Study how native execution coexists with a full event model and useful failure diagnostics. Its analyze/elaborate/run stages provide a different implementation organization from GHDL.

- **C1:** The model distinguishes physical simulation time from delta iteration when recording signal events. Separate process, postponed, driving, and effective-update work queues preserve ordering. Exceeding the delta-iteration limit reports active processes and drivers rather than silently hanging or advancing time.
- **C3:** LLVM-generated execution is coupled to a runtime model that owns scheduling, signals, and event heaps. This separation allows compiled process bodies without erasing the event semantics required by VHDL.

**Entry point:** [src/rt/model.c](https://github.com/nickg/nvc/blob/master/src/rt/model.c), especially `model_cycle`, signal-event tracking, and `reached_iteration_limit`. The [repository overview](https://github.com/nickg/nvc) documents the compiler stages and supported integration interfaces.

### 5. [accellera-official/systemc](https://github.com/accellera-official/systemc)

**Language/role:** C++; official SystemC reference implementation, including the discrete-event kernel used for hardware and system-level descriptions.

This is a simulator kernel study within a C++ hardware-description system. Focus on how modules, processes, channels, and simulation context cooperate.

- **C1:** The kernel's `crunch` loop separates runnable-process evaluation, primitive-channel updates, and event notification. Method processes and coroutine-backed threads have distinct execution paths, and repeated delta cycles must reach quiescence before time advances.
- **C2:** Process scheduling, channel update requests, hierarchy, and the simulation context form reusable interfaces for many hardware models. Their separation is also visible in stop, error, and process-lifetime handling.

**Entry points:** [sc_simcontext.cpp](https://github.com/accellera-official/systemc/blob/main/src/sysc/kernel/sc_simcontext.cpp) for evaluation/update/notification ordering; [release notes](https://github.com/accellera-official/systemc/blob/main/RELEASENOTES.md) for the supported standard, tested platforms, and compatibility caveats. In particular, the notes warn against assuming binary compatibility between library versions.

### 6. [B-Lang-org/bsc](https://github.com/B-Lang-org/bsc)

**Language/role:** Haskell compiler plus C++ runtime; the relevant subsystem is **Bluesim**, the simulator for Bluespec designs.

Study the interaction between rule-based language semantics, generated schedules, and a reusable simulation kernel. This monorepo is counted once, rather than counting its compiler, simulator, and SystemC integration separately.

- **C1:** Generated top-level schedules must obey rule and method constraints. The kernel's simulation thread also coordinates queue execution, pause/resume, and shutdown through explicit synchronization and running-state management.
- **C2:** Compiled module classes contain rule and method implementations; a generated top-level model supplies scheduling; the kernel invokes that model. The same organization supports foreign functions and SystemC wrappers without placing all integration policy inside individual modules.

**Entry points:** [Designing with Bluespec](https://bluespec.dev/user-guide/designing-with-bluespec-link.html), covering Bluesim model structure and SystemC integration; [Bluesim kernel.cxx](https://github.com/B-Lang-org/bsc/blob/main/src/bluesim/kernel.cxx) for the simulation thread and event-queue lifecycle.

## Native simulation inside embedded HDLs

### 7. [amaranth-lang/amaranth](https://github.com/amaranth-lang/amaranth)

**Language/role:** Python; hardware-description framework with its own Python simulation engine in `amaranth/sim`.

The native simulator is substantial independently of Amaranth's HDL emission. Study how an asynchronous testbench API is implemented over circuit processes, trigger state, and simulation time.

- **C1:** Edge, delay, change, and sample triggers carry different wakeup semantics. The engine tracks trigger validity and rejects conflicting clock drivers; these are concrete correctness boundaries in concurrent testbench execution.
- **C2:** The engine separates compiled circuit processes, simulation state/timeline, testbenches, and trigger/context interfaces. A testbench can await clocks and sample values through a reusable API instead of depending on engine internals.

**Entry points:** [Simulator guide](https://amaranth-lang.org/docs/amaranth/latest/simulator.html) for sampling and testbench contracts; [pysim.py](https://github.com/amaranth-lang/amaranth/blob/main/amaranth/sim/pysim.py) for `_PyTriggerState` and `PySimEngine`. Reading the contract and implementation together is especially useful for understanding when observations are stable.

### 8. [myhdl/myhdl](https://github.com/myhdl/myhdl)

**Language/role:** Python; generator-based HDL with a native simulator and external-simulator co-simulation support.

MyHDL exposes a compact but nontrivial example of adapting a host language's generators into hardware processes.

- **C1:** The simulation loop orders pending signal updates, runnable waiters, and future events. Its co-simulation path explicitly keeps input/output exchange operations paired to avoid desynchronizing the other simulator. Finalization must also release signals, traces, and child processes correctly.
- **C2:** Generator and waiter adapters, nested block flattening, and a common simulation driver allow pure Python hardware processes and co-simulation participants to share scheduling machinery. Duplicate-instance and simulation-lifetime checks define important API boundaries.

**Entry point:** [_Simulation.py](https://github.com/myhdl/myhdl/blob/master/myhdl/_Simulation.py). Follow instance flattening, the main event loop, suspend/resume handling, and cleanup. The [repository overview](https://github.com/myhdl/myhdl) establishes the native hardware-modeling role; this entry is not merely about its Verilog conversion feature.

### 9. [UCSBarchlab/PyRTL](https://github.com/UCSBarchlab/PyRTL)

**Language/role:** Python, with generated Python and C execution; RTL construction and simulation framework.

PyRTL is useful for comparing execution strategies behind a closely related user-facing simulation API.

- **C1:** Its documented step sequence distinguishes latching the previous register-next values, evaluating combinational logic, applying memory writes, recording traces, and saving register-next values for the following step. This makes observable state and memory timing explicit.
- **C3:** `Simulation`, `FastSimulation`, and `CompiledSimulation` trade interpreter overhead against Python or C code-generation startup costs. The C backend's restricted tracing and potentially expensive compilation make the architectural tradeoff concrete, rather than treating compilation as a free speed improvement.

**Entry point:** [Simulation and testing documentation](https://pyrtl.readthedocs.io/en/latest/simtest.html), including the step semantics and the separate backend sections. Study how implementation choice changes startup, per-cycle execution, and observability constraints.

### 10. [pymtl/pymtl3](https://github.com/pymtl/pymtl3)

**Language/role:** Python; multi-level hardware modeling, with native simulation implemented through passes. This entry focuses on native execution rather than external Verilator integration.

- **C1:** `SimpleSchedulePass` consumes dependency constraints, constructs a legal topological schedule, and detects cyclic constraints. Sequential update blocks and their buffered state transitions are treated separately from combinational updates.
- **C3:** Generated double-buffer flip code groups state by host component to reduce repeated access work and generated-code size. The source also discusses replacing an expensive code-generation helper with direct Python compilation for designs containing many flip-flops.

**What to study:** How an elaborated component model becomes a dependency graph, then a schedule, then executable Python closures. The performance decisions are visible in the same pass that must preserve register semantics.

**Entry point:** [SimpleSchedulePass.py](https://github.com/pymtl/pymtl3/blob/master/pymtl3/passes/sim/SimpleSchedulePass.py). The [repository](https://github.com/pymtl/pymtl3) supplies the broader modeling and pass-framework context; documentation completeness should not be assumed from the breadth of the framework.

### 11. [janestreet/hardcaml](https://github.com/janestreet/hardcaml)

**Language/role:** OCaml; typed hardware construction and the native **Cyclesim** simulator.

Study a deliberately constrained cycle simulator whose sampling contract is explicit. Cyclesim is two-state, treats clocks as a single clock for this model, and supports rising-edge behavior; it should not be mistaken for a general timed Verilog engine.

- **C1:** Evaluation proceeds through combinational logic using current registers, register/memory updates, and a further combinational phase. The API distinguishes observations before and after the edge, preventing an otherwise common ambiguity in cycle-oriented testbenches.
- **C2:** A `Circuit.t` graph becomes an executable simulator with reusable input/output interfaces. Typed interfaces and the circuit representation support systematic construction and testing across many designs.

**Entry point:** [Cyclesim simulation documentation](https://docs.hardcaml.org/hardcaml-docs/simulating-circuits/simulation/), particularly its execution phases, output sampling, and limitations. The [repository overview](https://github.com/janestreet/hardcaml) explains the surrounding circuit and interface abstractions.

### 12. [yupferris/kaze](https://github.com/yupferris/kaze)

**Language/role:** Rust; embedded HDL that generates Rust simulators. **Archived on GitHub in March 2024**; retained as an implementation study.

- **C1:** The expression compiler implements hardware-width semantics explicitly: masking after operations such as inversion, converting boolean values for arithmetic, and using wrapping arithmetic where host-language overflow behavior would otherwise differ.
- **C3:** Simulator generation walks reachable design state, builds an arena-backed intermediate representation, and uses reference counts when compiling expressions. Tracing changes which signals must remain available, exposing the tension between eliminating work and preserving observability.

**What to study:** The path from a Rust-hosted signal graph to standalone generated simulation code, especially places where ordinary Rust expression semantics are insufficient for hardware values.

**Entry points:** [sim.rs](https://github.com/yupferris/kaze/blob/master/kaze/src/sim.rs) for validation, state discovery, and generation; [sim/compiler.rs](https://github.com/yupferris/kaze/blob/master/kaze/src/sim/compiler.rs) for iterative expression traversal and bit-width handling. Archival status is visible on the [repository page](https://github.com/yupferris/kaze).

### 13. [samitbasu/rhdl](https://github.com/samitbasu/rhdl)

**Language/role:** Rust; hardware-description language and native simulation framework. The project describes itself as a rewrite/successor to RustHDL, which is not counted separately here.

- **C1:** Hierarchical simulation repeatedly evaluates kernels and child circuits until state reaches a fixed point. Equality-comparable cloned state makes convergence observable. The documented iteration cap can also reject a circuit that settles only after more iterations, so hitting it is not proof of oscillation.
- **C2:** The `Circuit` simulation contract separates inputs, mutable simulation state, and outputs. Iterator adapters construct timed input streams and compose simulation pipelines using standard Rust iteration mechanisms.

**What to study:** How derived implementations connect language-level circuit composition with an executable fixed-point model, and where a practical termination policy limits that model.

**Entry points:** [Circuit simulation semantics](https://github.com/samitbasu/rhdl/blob/main/doc/book/src/circuits/circuit_trait/simulation.md); [iterator-based simulation](https://github.com/samitbasu/rhdl/blob/main/doc/book/src/simulations/iterator.md). These describe a native execution model, not simply a wrapper around emitted Verilog.

## Hardware-IR interpreters and software simulation compilers

### 14. [llvm/circt](https://github.com/llvm/circt)

**Language/role:** C++/MLIR; compiler infrastructure monorepo. The relevant subsystem is the **Arc dialect and arcilator**, including lowering event/process behavior into compiled simulation.

- **C1:** The Arc documentation describes lowering suspended processes into state machines: program-counter states, values that must persist across waits, wakeup times, and terminal states. Recursive coroutine relationships require rejection because persistent state cannot be sized by an ordinary finite bottom-up layout.
- **C2:** Hardware, sequential, combinational, and process representations are lowered through reusable dialect boundaries into state-transfer functions and explicit state. This makes simulation one consumer of shared compiler infrastructure.
- **C3:** Explicit state and callable transfer functions expose simulation to compiler optimization and LLVM code generation rather than requiring interpretation of every hardware operation.

**Entry point:** [Arc dialect architecture](https://github.com/llvm/circt/blob/main/docs/Dialects/Arc.md). Focus on the representation and coroutine-lowering sections. CIRCT is counted once; inclusion does not assert that every experimental simulation path has complete language coverage.

### 15. [chipsalliance/treadle](https://github.com/chipsalliance/treadle)

**Language/role:** Scala; FIRRTL interpreter/simulator. **Archived in August 2024**; the repository directs users toward CIRCT-related successors.

- **C1:** The scheduler maintains clock and previous-clock state so repeated evaluation of the same edge does not incorrectly advance a register twice. Ordered assigners and end-of-cycle work encode the execution contract.
- **C3:** The data store specializes storage into integer, long, and big-integer arrays. Assigner implementations distinguish lean execution from paths supporting forced values and plugins, illustrating how instrumentation costs can be isolated from ordinary simulation.

**What to study:** How to execute a typed hardware IR while retaining debugging and override facilities, and how clock bookkeeping differs from simply walking a list of operations.

**Entry points:** [Scheduler.scala](https://github.com/chipsalliance/treadle/blob/master/src/main/scala/treadle/executable/Scheduler.scala); [DataStore.scala](https://github.com/chipsalliance/treadle/blob/master/src/main/scala/treadle/executable/DataStore.scala). Treat this as a historical interpreter architecture, not an actively supported default for new Chisel projects.

### 16. [ucsc-vama/essent](https://github.com/ucsc-vama/essent)

**Language/role:** Scala; FIRRTL-to-C++ simulation compiler originating in architecture research.

The [repository's design explanation](https://github.com/ucsc-vama/essent) describes flattened evaluation, local temporaries versus persistent state, register-update phases, conditional evaluation, and activity-based partitions. Its documented main-branch restrictions include a single clock and no logic on the clock path. RepCut and Dedup branches are not counted as separate repositories.

- **C1:** Conditional partition construction must retain external dependencies and topological order. Side effects matter: print operations are excluded from ordinary skip-able partitions and placed in always-active handling.
- **C3:** Cached partition outputs and conditional evaluation avoid recomputing unchanged logic. The implementation makes partition inputs, outputs, and graph ordering explicit, providing a concrete study of the overhead versus saved-work tradeoff.

**Entry point:** [OptMakeCondPart.scala](https://github.com/ucsc-vama/essent/blob/master/src/main/scala/OptMakeCondPart.scala). Read it alongside the repository's optimization levels and stated restrictions; research benchmarks do not establish universal superiority over other engines.

### 17. [OpenXiangShan/gsim](https://github.com/OpenXiangShan/gsim)

**Language/role:** C++; FIRRTL/CHIRRTL-oriented compiler producing C++ RTL simulation code, developed around large processor designs.

- **C1:** Bit-level dependency analysis splits signals only where downstream computation does not depend on the complementary bits. Reset optimization must restore reset values and reactivate successors after its optimistic fast path. These transformations have observable semantic obligations beyond ordinary expression simplification.
- **C3:** GSIM groups correlated nodes into supernodes to reduce activation checks, then balances that saving against extra evaluations. Cost models also choose between extracting shared expressions and inlining them, exposing the interaction among branches, memory accesses, and arithmetic work.

**What to study:** A graph optimizer designed around the actual overheads of activity-driven software simulation, including cases where an optimization at one level increases work at another.

**Entry point:** [The authors' GSIM design paper, section III](https://arxiv.org/html/2508.02236v1). The [repository](https://github.com/OpenXiangShan/gsim) documents its input workflow and debugging facilities. Performance numbers are intentionally not generalized from the paper's selected designs.

## Heterogeneous and hardware-accelerated simulation

### 18. [vmware-archive/cascade](https://github.com/vmware-archive/cascade)

**Language/role:** C++; Verilog JIT simulation with software execution and FPGA acceleration. **Archived; the repository explicitly says development has ended.**

- **C1:** Replacing a running engine requires transferring both state and inputs, finalizing the replacement, and preserving pending-read information. This is a concrete semantic continuity problem when compilation finishes after simulation has already begun.
- **C2:** A common `Engine` wraps a `Core` and an `Interface`, exposing evaluation, update, state, and input operations across execution implementations.
- **C3:** The architecture allows simulation to begin in software while slower hardware compilation proceeds, then substitutes the compiled implementation through that interface.

**Entry point:** [target/engine.h](https://github.com/vmware-archive/cascade/blob/master/src/cascade/target/engine.h), especially `replace_with`. The [repository documentation](https://github.com/vmware-archive/cascade) explains the execution model and restricted semantics, including its two-state treatment. Study it as a historical adaptive execution system, not as a fully interchangeable standards simulator.

### 19. [ManticoreRTL/manticore-compiler](https://github.com/ManticoreRTL/manticore-compiler)

**Language/role:** Scala; compiler and reference interpreter for a specialized FPGA-hosted manycore RTL simulator. The associated hardware, frontend, and runtime repositories are dependencies, not additional entries here.

- **C1:** The placed-level interpreter distinguishes bounded and unbounded register files and checks invalid allocation or uninitialized values. Its explicit limitation—communication interpretation does not establish absence of network contention—is valuable when studying what a reference model does and does not validate.
- **C3:** The architecture uses static bulk-synchronous scheduling, moving resource and communication scheduling into compilation to address fine-grained synchronization costs. This is described in the [authors' paper](https://arxiv.org/abs/2301.09413).

**Entry point:** [AtomicInterpreter.scala](https://github.com/ManticoreRTL/manticore-compiler/blob/master/src/main/scala/manticore/compiler/assembly/levels/placed/interpreter/AtomicInterpreter.scala), followed by the paper for the execution model. This is a specialized research stack with hardware requirements; its compiler/interpreter can be studied without assuming availability of a general-purpose replacement for desktop simulators.

### 20. [firesim/firesim](https://github.com/firesim/firesim)

**Language/role:** Scala, C++, and Python; FPGA-accelerated RTL/full-system simulation. The relevant engine is **Golden Gate/MIDAS**, not only the deployment manager.

- **C1:** Target time is decoupled from FPGA host time. Tokens represent converged target-cycle values, and a model advances by consuming and producing the required tokens. Correct models preserve output sequences despite variable arrival latency and backpressure.
- **C2:** Models, tokens, channels, and bridges allow simulation components to reside on CPUs or FPGAs. The documentation distinguishes cycle-exact RTL models from intentionally abstract models; choosing an abstract component changes fidelity.
- **C3:** Host decoupling permits resource-saving implementations that take several host cycles per target cycle, while preserving the intended target behavior.

**Entry points:** [Golden Gate overview](https://docs.fires.im/en/latest/golden-gate/overview/); [target abstraction and host decoupling](https://docs.fires.im/en/latest/golden-gate/li-bdn/). These make clear why the system is a deterministic simulation architecture rather than merely synthesis of an FPGA prototype.

### 21. [NVlabs/GEM](https://github.com/NVlabs/GEM)

**Language/role:** Rust with CUDA/C++; GPU execution of synthesized RTL logic through a virtual Boolean processor.

- **C2:** GEM separates AIG synthesis, mapping to a virtual manycore representation, and execution. The resulting mapping can be reused across testbenches, giving a stable compiled artifact between the design-processing and simulation stages.
- **C3:** Its architecture explicitly accepts expensive synthesis/mapping startup to enable GPU execution. The [repository explanation](https://github.com/NVlabs/GEM) states that these steps need not be repeated for every testbench; this tradeoff matters for workload selection.

**What to study:** How a synthesized logic representation becomes a reusable GPU simulation workload, and how memory/clock support constrains that representation. The usage guide includes intermediate CPU-reference checks after transformations.

**Entry point:** [usage.md on the published staged-aig-release branch](https://github.com/NVlabs/GEM/blob/staged-aig-release/usage.md). It documents static, noninteractive waveform testbenches and restrictions including unsupported latches/asynchronous sequential elements. Those restrictions are material; this is not a general behavioral SystemVerilog event kernel.

### 22. [dian-lun-lin/RTLflow](https://github.com/dian-lun-lin/RTLflow)

**Language/role:** C++/CUDA; batch-stimulus RTL simulation. **Verilator-derived research implementation**, retained because it adds a substantive GPU memory, code-generation, and scheduling architecture.

- **C1:** CPU input preparation and GPU design evaluation have dependencies within each stimulus group's simulation cycle. The pipeline overlaps independent groups while retaining those per-group dependencies; concurrency is not equivalent to freely interchanging simulation steps.
- **C3:** AST annotation and indexed device storage support multi-stimulus kernels. GPU task-graph partitioning, CUDA Graph reuse, and CPU/GPU pipelining target distinct costs: memory access, repeated launches, and input-preparation stalls.

**What to study:** How a compiler designed for single-design CPU execution is substantially adapted to batched GPU execution, including the relationship between stimulus grouping and coalesced memory access.

**Entry point:** [Authors' RTLflow design paper, sections 3.1–3.3](https://tsung-wei-huang.github.io/papers/icpp22-rtlflow.pdf). Its architecture substantiates the separate inclusion; inherited Verilator history is not counted as independent C4 evidence.

### 23. [epfl-vlsc/parendi](https://github.com/epfl-vlsc/parendi)

**Language/role:** C++ compiler emitting Poplar/IPU execution code. **Verilator-derived research prototype** with separate partitioning, scheduling, and IPU-specific optimization work.

- **C1:** Registers are split into current and next values. Bulk-synchronous execution separates private computation from communication with barriers, ensuring that newly computed register values do not leak into another process's same-cycle evaluation.
- **C3:** Partitioning balances duplicated combinational work, communication, and finite tile memory. Large-array co-location, cross-chip partitioning, memory-aware merging, and differential exchange address different bottlenecks instead of merely maximizing thread count.

**What to study:** The compiler's translation from shared-memory-oriented RTL execution to explicitly communicating processes. The [repository](https://github.com/epfl-vlsc/parendi) documents its Poplar/IPU requirements and prototype restrictions, including the limited timing/clock model.

**Entry point:** [Authors' Parendi paper, sections 3 and 5](https://arxiv.org/html/2403.04714v1). Separate inclusion rests on the described backend changes, not on being another copy of the upstream Verilator tree.

## Asynchronous and interactive netlist engines

### 24. [asyncvlsi/actsim](https://github.com/asyncvlsi/actsim)

**Language/role:** C++; simulator for the ACT asynchronous hardware-description ecosystem, spanning CHP, HSE, production rules, and mixed-abstraction composition.

- **C1:** Channel rendezvous, guarded choices, arbitration, unstable transitions, and interference introduce correctness problems not captured by a single synchronous clock. The guide distinguishes randomized scheduling choices and handling of unknown/interfering values.
- **C2:** Process graphs represent assignments, send/receive operations, forks, conditions, loops, and joins. These abstractions support multiple description levels, with separate integration to Xyce for analog portions rather than pretending that the digital engine is itself the analog solver.

**What to study:** A simulator whose fundamental concurrency model includes communication and production rules, and the consequences of substituting one abstraction level for another. The documented fallback behavior makes model selection worth inspecting explicitly.

**Entry points:** [ACT simulator guide](https://avlsi.csl.yale.edu/act/doku.php?id=tools:actsim); [chpsim.h](https://github.com/asyncvlsi/actsim/blob/master/chpsim.h) for statement representations, dereferences, channel data, and process-graph bookkeeping.

### 25. [tilk/digitaljs](https://github.com/tilk/digitaljs)

**Language/role:** JavaScript; digital-netlist simulation and visualization, including synthesized HDL designs through the Yosys conversion ecosystem.

This entry sits at the netlist boundary: DigitalJS is not a general behavioral Verilog parser. Its value is the inspectable engine behind interactive circuit visualization.

- **C1:** The synchronous engine stores time-indexed pending gates and input snapshots, respects propagation delays, handles subcircuit ports, and suppresses unchanged propagation. Same-time processing and monitor timing require ordering beyond simply redrawing changed gates.
- **C2:** A device/connector/subcircuit model is separated from simulation engines. The worker engine serializes model and signal changes across a Web Worker boundary, supporting an interactive front end without embedding simulation logic into every display object.

**Entry points:** [engines/synch.mjs](https://github.com/tilk/digitaljs/blob/master/src/engines/synch.mjs) for scheduling and propagation; [engines/worker.mjs](https://github.com/tilk/digitaljs/blob/master/src/engines/worker.mjs) for the worker interface. The [repository](https://github.com/tilk/digitaljs) documents the JSON circuit representation and HDL-netlist relationship.

## Search coverage, exclusions, and limitations

Discovery used more than six distinct live search formulations, covering: open-source Verilog/SystemVerilog event and compiled engines; VHDL runtime kernels and LLVM backends; SystemC and Bluespec simulation internals; Python embedded-HDL native simulators; Rust and OCaml simulation generation; FIRRTL/MLIR interpreters and compilers; asynchronous ACT simulation; browser/Yosys netlist engines; and GPU, IPU, FPGA, and JIT acceleration. Follow-up searches for alternatives largely returned the same architectural families, integration layers, legacy mirrors, and additional specialized research systems. The accelerator entries are a representative selection, not a census of every published prototype.

For every retained entry, the canonical GitHub repository page or GitHub API metadata was opened, and an additional implementation file, technical guide, or author-written architecture paper was read. The links above are the reading entry points, not search-result snippets. No candidate code was executed and no performance or conformance suite was run. Performance criteria therefore describe supported architectural decisions, not independently reproduced speedups. Branch links identify the material inspected but may change after this research date.

Important boundaries and exclusions:

- Cocotb, VUnit, and OSVVM were not counted as simulator implementations; waveform viewers such as GTKWave and frontends such as slang/Surelog were also excluded when they did not supply the simulation engine being studied.
- [Migen's GitHub repository](https://github.com/m-labs/migen) now directs development to a non-GitHub host. It was excluded rather than treating the stale GitHub tree as a verified continuing official mirror. [RustHDL](https://github.com/samitbasu/rust-hdl) was not counted separately from the successor RHDL selection.
- Historical CVC/Cver/FreeHDL-style candidates were investigated, but GitHub copies were not retained where official provenance or a substantive continuing official mirror could not be established. Consequently, historical coverage is selective.
- Treadle, Kaze, and Cascade are explicitly marked archived. Research artifacts and specialized backends are identified without assuming active support. C4 is claimed only where multi-year compatibility evidence was actually inspected; a recent push or an inherited upstream history was not treated as sufficient.
- CIRCT, BSC, and the embedded-HDL frameworks are counted once each. ESSENT variants and Manticore companion repositories are not inflated into separate entries. RTLflow and Parendi are explicitly identified as Verilator-derived and included for their substantial separate execution architectures.

The broad scope makes the report useful for comparing scheduling, state representation, code generation, concurrency, and acceleration. It does not make all entries substitutes for one another: event accuracy, four-state values, timing, clocks, supported HDL subsets, testbench interaction, and required hardware differ materially.
